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
  4. of what remains — called by tests and only by tests — skip any symbol *referenced*
     rather than called from a production file, via an AST pass (see below);
  5. report the rest, split into `exported` and `private`.

## Why step 4 exists, and why it is narrow

graft's `calls` relation models call sites. It does **not** model reference-passing, so a
callback registered rather than invoked looks unreachable when it is not. The real case
this was built against, in `harness-runtime/src/harness_runtime/drain.py`:

    loop.add_signal_handler(sig, _on_drain_signal, ctx)

`_on_drain_signal` has four inbound `calls` edges, all from `tests/test_drain.py`, and is
nonetheless live in production. Shipping that as a finding would be a false positive.

The pass is AST-based, not substring-based — `[[source-ordering-is-not-runtime-parentage]]`
is a mistake this workspace has already paid for. But AST alone is not enough: a rescue
that matches on bare names **hides real findings**, which for a detector is the worse
error. Two rounds of review found eight concrete victims, so the match is keyed by
namespace, not name:

  * a `Name` can only reach a **module-level function**, and is attributed to the module it
    was imported from (relative imports resolved) or else the referencing file's own;
  * a `self.` / `cls.` attribute can only reach a **method** — the one receiver resolvable
    without type inference.

Checking both against one flat set is what hid `EngineOutputStore.record` behind a local
dict named `record`, and three test-only `append` methods (one with 28 test callers) behind
unrelated `list.append` calls. `__all__` membership is keyed the same way, since exported
rows are hidden by default and a mis-attributed export silently drops a finding.

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

If the wiring graph is missing, unreadable, **or stale** the tool exits **non-zero with an
explicit message** and reports nothing. "Could not look" must never render as "looked,
found nothing" — see `[[gate-cannot-tell-empty-from-unlooked]]`.

Staleness counts as "cannot look" deliberately. A graph that exists but predates an edit,
branch switch, or rebase still parses, still yields edges, and still exits 0 — while
describing code that is no longer here. That is worse than no answer, because nothing
about the output marks it as wrong. graft's own CLI re-derives before answering, so this
failure is only reachable by reading the artifact directly, which is what this module
does; detecting it is therefore this module's job.

It is otherwise advisory: a clean run and a run with findings both exit 0, so this can
never abort a caller that merely wanted the report.

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
from typing import Any, NamedTuple

WIRING = Path("graft/.graph/wiring.json")

_SRC = re.compile(r"harness-[a-z]+/src/")
_TEST = re.compile(r"(^|/)tests?/|(^|/)test_[^/]*\.py$|conftest\.py$")

# Only these node kinds carry a meaningful "who calls me" question. Classes and modules
# are reached by construction and import, which `calls` edges model differently.
_CALLABLE_KINDS = frozenset({"function", "method"})

# The only attribute receivers resolvable without type inference: they name a sibling
# member of the enclosing class. Everything else (`items.append`) is a guess.
_SELF_RECEIVERS = frozenset({"self", "cls"})


class GraphUnavailableError(RuntimeError):
    """The wiring graph could not be read. Never degrade this to an empty result."""


class ProductionRefs(NamedTuple):
    """Production references, split by how the referenced symbol could be reached.

    `names` — `(module, bare_name)` from `ast.Name`. Only a module-level FUNCTION can be
    reached this way.

    `self_attrs` — `(module, attr)` from a `self.` / `cls.` receiver. Only a METHOD can be
    reached this way.

    Keeping them apart is what stops a local variable named `record` from rescuing
    `EngineOutputStore.record`: a bare name and a method live in different namespaces, so
    matching them against one flat set silently hides findings.
    """

    names: set[tuple[str, str]]
    self_attrs: set[tuple[str, str]]


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


def module_of(path: str) -> str:
    """Dotted module name for a `harness-*/src/<pkg>/...` path, or "" if not importable."""
    marker = "/src/"
    i = path.find(marker)
    if i == -1:
        return ""
    rel = path[i + len(marker) :]
    if rel.endswith(".py"):
        rel = rel[: -len(".py")]
    if rel.endswith("/__init__"):
        rel = rel[: -len("/__init__")]
    return rel.replace("/", ".")


def _resolved_import_sources(tree: ast.AST, mod: str) -> dict[str, str]:
    """`{imported_name: defining_module}` for every `from X import Y` in one file.

    Relative imports are resolved against `mod`'s package so `from .drain import _on_x`
    inside `harness_runtime.lifecycle.a` attributes `_on_x` to `harness_runtime.lifecycle.drain`
    rather than to a bare `drain` that would match nothing.
    """
    sources: dict[str, str] = {}
    pkg = mod.rsplit(".", 1)[0] if "." in mod else ""
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level:
            base = pkg
            for _ in range(node.level - 1):
                base = base.rsplit(".", 1)[0] if "." in base else ""
            origin = f"{base}.{node.module}" if node.module else base
        else:
            origin = node.module or ""
        for alias in node.names:
            sources[alias.asname or alias.name] = origin
    return sources


def production_references(paths: Iterable[Path], root: Path | None = None) -> ProductionRefs:
    """`{(defining_module, name)}` referenced — not called — from production source.

    **Scoped by module on purpose.** A flat set of bare names over-suppresses badly: a
    test-only method named `append` vanishes because unrelated `.append` calls exist
    somewhere in the tree. Since this module is a triage list, a false negative (a real
    finding silently hidden) is strictly worse than a false positive (a live symbol worth
    30 seconds to dismiss), so the rescue must be precise rather than generous.

    A `Name` reference is attributed to the module that can actually see it: the module it
    was imported from, or — absent an import — the referencing file's own module. So
    `loop.add_signal_handler(sig, _on_drain_signal, ctx)` inside `drain.py` rescues
    `drain._on_drain_signal` and nothing else.

    `Attribute.attr` is collected **only for a `self.` / `cls.` receiver**, and attributed
    to the referencing file's own module. That receiver is the one resolvable without type
    inference — it names a sibling member of the enclosing class — and it is exactly the
    `self._compose_and_persist_audit(...)` pattern graft does not always turn into a call
    edge. Any other receiver is a guess, and a wrong guess hides a finding: collecting
    every `.attr` was suppressing three real test-only `append` methods (one with 28 test
    callers) because unrelated `list.append` calls exist.

    Measured on this repo, the rules compose to 2 residual rows, both documented classes
    below. Accepted rather than tuned further.

    Residue, accepted and NOT fixed:
      * a method reached through a non-`self` receiver of its own type
        (`parent._link_child(self)`) surfaces as a row to dismiss;
      * `__init__` reached only by construction surfaces likewise.
    Both are cheap to dismiss. Narrowing them further needs type inference, which buys
    two rows at the cost of a resolver this module has no business owning.

    A file that fails to parse is skipped rather than fatal: a syntax error in one module
    must not silently empty the whole reference set, but it also must not stop the run.
    """
    base = root or Path(".")
    names: set[tuple[str, str]] = set()
    self_attrs: set[tuple[str, str]] = set()
    for path in paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            continue
        try:
            mod = module_of(str(path.relative_to(base)))
        except ValueError:
            mod = module_of(str(path))
        imported = _resolved_import_sources(tree, mod)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add((imported.get(node.id, mod), node.id))
            elif (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in _SELF_RECEIVERS
            ):
                self_attrs.add((mod, node.attr))
    return ProductionRefs(names=names, self_attrs=self_attrs)


def dunder_all_names(paths: Iterable[Path], root: Path | None = None) -> set[tuple[str, str]]:
    """Names listed in any `__all__`, which is what "exported" actually means in Python.

    graft's own `exported` flag is name-convention-based (no leading underscore), so it
    misses the deliberate `__all__ = ["_project_pause_event_to_audit_payload", ...]`
    pattern — an underscore-named helper published on purpose. Classifying those as
    "private, actionable" would manufacture urgency for a conscious design choice.

    `__all__` entries are string constants, not `Name` nodes, so `production_references`
    cannot see them; this is a separate walk on purpose.
    """
    base = root or Path(".")
    names: set[tuple[str, str]] = set()
    for path in paths:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError):
            continue
        try:
            mod = module_of(str(path.relative_to(base)))
        except ValueError:
            mod = module_of(str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            if not any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
                continue
            if isinstance(node.value, ast.List | ast.Tuple):
                names.update(
                    (mod, e.value)
                    for e in node.value.elts
                    if isinstance(e, ast.Constant) and isinstance(e.value, str)
                )
    return names


def derive(
    graph: dict[str, Any],
    prod_refs: ProductionRefs | None = None,
    all_names: set[tuple[str, str]] | None = None,
) -> list[Finding]:
    """Symbols under `harness-*/src/**` whose only inbound callers are tests.

    `prod_refs` is the module-scoped `(module, name)` set from `production_references`;
    pass an empty set to disable step 4 (used by tests that exercise the call-edge logic
    in isolation). `all_names` is the `__all__` membership set, OR-ed into `exported`.
    """
    prod_refs = ProductionRefs(set(), set()) if prod_refs is None else prod_refs
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

        key = (module_of(node["path"]), node["name"])
        # A bare name can only reach a module-level function; `self.x` can only reach a
        # method. Checking both against one set is what hid `EngineOutputStore.record`
        # behind a local dict of the same name.
        reachable_by_reference = (
            key in prod_refs.self_attrs if node.get("kind") == "method" else key in prod_refs.names
        )
        if reachable_by_reference:
            continue  # referenced (not called) from a module that can see it — e.g. a callback

        findings.append(
            Finding(
                name=node["name"],
                path=node["path"],
                span=node.get("span", ""),
                test_callers=len(sources),
                exported=bool(node.get("exported")) or key in all_names,
            )
        )

    findings.sort(key=lambda f: (-f.test_callers, f.path, f.name))
    return findings


def stale_sources(
    root: Path | None = None, *, graph: dict[str, Any] | None = None, limit: int = 5
) -> list[str]:
    """Reasons the wiring graph does not describe this checkout.

    A graph that merely EXISTS is not a graph that describes this checkout. An edit, a
    branch switch, or a rebase leaves `wiring.json` intact but describing other code, and
    call edges derived from it are then confidently wrong — a worse outcome than no
    answer, because it still exits 0 and still looks like a clean result.

    Two independent ways to be stale, and mtime alone catches only the first:

    * a tracked file is **newer** than the graph — it was edited after the build;
    * a file the graph **indexes no longer exists** — deleted by a branch switch or
      rebase. Walking the checkout can never see these, because the checkout is precisely
      where they are absent; the graph's own node paths have to be checked against disk.
      Without this, a deleted target still yields a finding naming a nonexistent path.

    graft's own CLI re-derives before answering, so a stale graph is only reachable by
    reading the artifact directly, which is exactly what this module does. Detecting it
    is therefore this module's job, not graft's.

    Returns at most `limit` reasons — enough to name in an error, not a full listing.
    """
    base = root or Path(".")
    graph_path = base / WIRING
    if not graph_path.exists():
        return []
    graph_mtime = graph_path.stat().st_mtime
    reasons: list[str] = []

    for path in base.glob("harness-*/**/*.py"):
        try:
            if path.stat().st_mtime > graph_mtime:
                reasons.append(f"{path} is newer than the graph")
        except OSError:
            continue
        if len(reasons) >= limit:
            return reasons

    if graph is not None:
        seen: set[str] = set()
        for node in graph.get("nodes", []):
            path_str = node.get("path", "")
            if not path_str or path_str in seen or not is_src(path_str):
                continue
            seen.add(path_str)
            if not (base / path_str).exists():
                reasons.append(f"{path_str} is indexed but no longer on disk")
                if len(reasons) >= limit:
                    return reasons
    return reasons


def collect(root: Path | None = None) -> list[Finding]:
    """Full pipeline against a real checkout.

    Refuses to derive from a stale graph for the same reason it refuses to derive from a
    missing one: both are "cannot look reliably", and neither may render as "looked,
    found nothing".
    """
    base = root or Path(".")
    graph = load_graph(base)
    if stale := stale_sources(base, graph=graph):
        detail = "; ".join(stale[:3])
        raise GraphUnavailableError(
            f"{base / WIRING} does not describe this checkout ({detail}). "
            f"Derived call edges would describe code that is no longer here. "
            f"Run `graft build` (seconds, $0, no key) and re-run."
        )
    src_files = [
        p for p in base.glob("harness-*/src/**/*.py") if not is_test(str(p.relative_to(base)))
    ]
    return derive(graph, production_references(src_files, base), dunder_all_names(src_files, base))


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
