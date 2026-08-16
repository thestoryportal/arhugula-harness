#!/usr/bin/env python3
"""Test-only-caller detector over the graft wiring graph.

The reachability-side sibling to `tools/semantic_overlay/overlay.py`. The overlay joins
spec-cites / CXA-seams / substitutions and answers *"is this file documented against the
canonical design substrate"*. It holds **no call edges**, so it cannot answer the other
orphan question: *"does any production path actually reach this code, or do only the tests
touch it?"*

That question is the `[[wired-handler-unreachable-two-halves-of-one-mechanism]]` failure
shape — a unit lands green, its tests exercise the seam directly, and nothing in the real
product ever calls it. Unit-green is not closeable until the REAL path reaches it. Two
halves of one mechanism; this module detects when only one half exists.

Both instruments can flag the same file for different, independently-correct reasons. A
file with no spec cite may be perfectly reachable; a fully-cited file may be dead. Neither
subsumes the other — run both.

## What it does

For every function/method defined under `harness-*/src/**`:

  1. read inbound `calls` edges from graft's wiring graph;
  2. skip symbols with **no** inbound edges at all — that set is dominated by CLI entry
     points, public API, and framework hooks, and is too noisy to be a signal;
  3. skip symbols with **any** inbound edge from a production (non-test) file;
  4. of what remains — called by tests and only by tests — skip any symbol whose bare name
     is *referenced* (not called) from a production file, via an AST pass (see below);
  5. report the rest, split into `exported` and `private`.

## Why step 4 exists

graft's `calls` relation models call sites. It does **not** model reference-passing, so a
callback registered rather than invoked looks unreachable when it is not. The real case
this was built against, in `harness-runtime/src/harness_runtime/drain.py`:

    loop.add_signal_handler(sig, _on_drain_signal, ctx)

`_on_drain_signal` has four inbound `calls` edges, all from `tests/test_drain.py`, and is
nonetheless live in production. Shipping that as a finding would have been a false
positive. Step 4 catches it by walking the AST of every production source file and
collecting `Name.id` and `Attribute.attr`, which covers callback arguments, decorators,
dict/registry values, and re-exports.

The pass is AST-based, not substring-based, on purpose — see
`[[source-ordering-is-not-runtime-parentage]]`: resolving call sites by substring is a
mistake this workspace has already paid for.

## Known limits — read before treating output as a defect list

**This is a triage list, not a defect list.** Every row needs its own verification.

* **Direct, not transitive.** A private helper called only by another test-only private
  helper in the same file counts as production-referenced, because its caller lives in a
  production file. The question answered is "is this referenced from production code",
  not "is this transitively reachable from an entry point". Computing the latter needs a
  trustworthy entry-point set, which this repo does not have; guessing one trades a small
  known false-positive rate for a large unknown one.
* **Dynamic dispatch is invisible.** `getattr(obj, name)()`, string-keyed registries, and
  plugin loaders defeat both passes. A row may still be live.
* **`exported` rows are usually legitimate.** A public symbol with no in-repo production
  caller is often intended API surface. They are counted, and only listed under `--all`.
* **The graph is per-checkout.** `graft/.graph/wiring.json` is gitignored, so this tool
  runs locally only and is deliberately NOT a CI gate.

## Failure posture

If the wiring graph is missing or unreadable the tool exits **non-zero with an explicit
message** and reports nothing. "Could not look" must never render as "looked, found
nothing" — see `[[gate-cannot-tell-empty-from-unlooked]]`. It is otherwise advisory: a
clean run and a run with findings both exit 0, so this can never abort a caller that
merely wanted the report.

Usage:
    python tools/graft_reachability.py                 # report private findings
    python tools/graft_reachability.py --all           # include exported symbols
    python tools/graft_reachability.py --json          # machine-readable
    just reachability
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

WIRING = Path("graft/.graph/wiring.json")

_SRC = re.compile(r"harness-[a-z]+/src/")
_TEST = re.compile(r"(^|/)tests?/|(^|/)test_[^/]*\.py$|conftest\.py$")

# Only these node kinds carry a meaningful "who calls me" question. Classes and modules
# are reached by construction and import, which `calls` edges model differently.
_CALLABLE_KINDS = frozenset({"function", "method"})


class GraphUnavailableError(RuntimeError):
    """The wiring graph could not be read. Never degrade this to an empty result."""


@dataclass(frozen=True)
class Finding:
    name: str
    path: str
    span: str
    test_callers: int
    exported: bool


def is_src(path: str) -> bool:
    return bool(_SRC.search(path))


def is_test(path: str) -> bool:
    return bool(_TEST.search(path))


def load_graph(root: Path | None = None) -> dict[str, Any]:
    """Read the graft wiring graph, or raise `GraphUnavailableError` with a fix hint."""
    path = (root or Path(".")) / WIRING
    if not path.exists():
        raise GraphUnavailableError(
            f"{path} not found. The graft wiring graph is a gitignored, per-checkout "
            f"build artifact — run `graft build` in this checkout first. "
            f"(Reporting nothing here would be indistinguishable from a clean result.)"
        )
    try:
        graph = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GraphUnavailableError(f"{path} could not be parsed: {exc}") from exc
    if not isinstance(graph, dict) or "nodes" not in graph or "edges" not in graph:
        raise GraphUnavailableError(f"{path} is not a graft wiring graph (missing nodes/edges).")
    return graph


def production_references(paths: Iterable[Path]) -> set[str]:
    """Every bare name referenced in production source, via AST — not substring.

    Collects `Name.id` and `Attribute.attr`, which is what a callback argument, a
    decorator, a registry value, or a re-export looks like once parsed. A `def foo` is an
    `ast.FunctionDef`, not a `Name`, so a definition never counts as a reference to
    itself.

    A file that fails to parse is skipped rather than fatal: a syntax error in one module
    must not silently empty the whole reference set, but it also must not stop the run.
    """
    refs: set[str] = set()
    for path in paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                refs.add(node.id)
            elif isinstance(node, ast.Attribute):
                refs.add(node.attr)
    return refs


def dunder_all_names(paths: Iterable[Path]) -> set[str]:
    """Names listed in any `__all__`, which is what "exported" actually means in Python.

    graft's own `exported` flag is name-convention-based (no leading underscore), so it
    misses the deliberate `__all__ = ["_project_pause_event_to_audit_payload", ...]`
    pattern — an underscore-named helper published on purpose. Classifying those as
    "private, actionable" would manufacture urgency for a conscious design choice.

    `__all__` entries are string constants, not `Name` nodes, so `production_references`
    cannot see them; this is a separate walk on purpose.
    """
    names: set[str] = set()
    for path in paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
                continue
            if isinstance(node.value, ast.List | ast.Tuple):
                names.update(
                    e.value
                    for e in node.value.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                )
    return names


def derive(
    graph: dict[str, Any],
    prod_refs: set[str] | None = None,
    all_names: set[str] | None = None,
) -> list[Finding]:
    """Symbols under `harness-*/src/**` whose only inbound callers are tests.

    `prod_refs` is the AST reference set from `production_references`; pass an empty set
    to disable step 4 (used by tests that exercise the call-edge logic in isolation).
    `all_names` is the `__all__` membership set, OR-ed into each finding's `exported`.
    """
    prod_refs = set() if prod_refs is None else prod_refs
    all_names = set() if all_names is None else all_names
    by_id = {n["id"]: n for n in graph["nodes"]}

    inbound: dict[str, list[str]] = {}
    for edge in graph["edges"]:
        if edge.get("relation") != "calls":
            continue
        inbound.setdefault(edge["target"], []).append(edge["source"])

    findings: list[Finding] = []
    for target, sources in inbound.items():
        node = by_id.get(target)
        if node is None or not is_src(node["path"]):
            continue
        if node.get("kind") not in _CALLABLE_KINDS:
            continue

        caller_paths = [by_id[s]["path"] if s in by_id else s.split("#")[0] for s in sources]
        if any(not is_test(p) for p in caller_paths):
            continue  # a production caller exists — reachable

        if node["name"] in prod_refs:
            continue  # referenced (not called) from production — e.g. a registered callback

        findings.append(
            Finding(
                name=node["name"],
                path=node["path"],
                span=node.get("span", ""),
                test_callers=len(sources),
                exported=bool(node.get("exported")) or node["name"] in all_names,
            )
        )

    findings.sort(key=lambda f: (-f.test_callers, f.path, f.name))
    return findings


def collect(root: Path | None = None) -> list[Finding]:
    """Full pipeline against a real checkout."""
    base = root or Path(".")
    graph = load_graph(base)
    src_files = [
        p for p in base.glob("harness-*/src/**/*.py") if not is_test(str(p.relative_to(base)))
    ]
    return derive(graph, production_references(src_files), dunder_all_names(src_files))


def render(findings: list[Finding], *, show_all: bool) -> str:
    private = [f for f in findings if not f.exported]
    exported = [f for f in findings if f.exported]
    shown = findings if show_all else private

    lines = [
        "graft reachability — src symbols whose only inbound callers are tests",
        "",
        f"  private (actionable) : {len(private)}",
        f"  exported (usually intended API surface) : {len(exported)}"
        + ("" if show_all else "   [--all to list]"),
        "",
    ]
    if not shown:
        lines.append("  no findings.")
    for f in shown:
        tag = " [exported]" if f.exported else ""
        lines.append(f"  {f.test_callers:>3} test callers  {f.name}{tag}")
        lines.append(f"       {f.path}:{f.span}")
    lines += [
        "",
        "TRIAGE LIST, NOT A DEFECT LIST — verify each row before acting. Dynamic dispatch",
        "and string-keyed registries are invisible to both passes; a row may still be live.",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--all", action="store_true", help="include exported symbols in the listing"
    )
    parser.add_argument("--json", action="store_true", help="emit findings as JSON")
    args = parser.parse_args(argv)

    try:
        findings = collect()
    except GraphUnavailableError as exc:
        print(f"graft reachability: CANNOT LOOK — {exc}", file=sys.stderr)
        return 2

    if args.json:
        rows = findings if args.all else [f for f in findings if not f.exported]
        print(json.dumps([asdict(f) for f in rows], indent=2))
    else:
        print(render(findings, show_all=args.all))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
