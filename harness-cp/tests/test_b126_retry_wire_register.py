"""Drift catchers for the `retry.*` wire surface — register row `B-126`.

`B-126` named three different cardinalities for one namespace (export manifest
4, code schema 6, wire 8) and observed that only the first was verified. The
grounding pass corrected the wire figure to TEN and found the divergence is not
a discretion free-for-all: `retry.*` is declared at TWO contract venues, and six
of the seven keys beyond C-CP-03 §3.5 are MANDATED by name at Runtime §14.6 /
§14.9. `RETRY_WIRE_REGISTER` records them; these tests keep the record true.

Three sweeps, deliberately different in shape, because each alone has a hole:

  * `test_every_retry_literal_in_src_is_declared_somewhere` — the BROAD sweep.
    Every `retry.`-prefixed string literal anywhere in `harness-*/src` must
    belong to one of the three declared buckets. Catches a new key of ANY shape
    (attribute, span name, sampling key) added without declaring it.
  * `test_emitted_attribute_keys_match_the_declared_emitted_set` — the PRECISE
    sweep. The keys actually SET as span attributes must equal the CP-declared
    subset plus the register's `emitted=True` rows. Catches an `emitted` flag
    that lies in either direction, which the broad sweep cannot see.
  * `test_every_declared_name_has_a_site_outside_its_own_declaration` — LIVENESS.
    A declared name whose last real producer or consumer disappears fails here;
    scanning the declaration home would make it vacuous, so the home is excluded.

Together they also foreclose the cheap way to silence any one: relabelling an
emitted attribute as a span NAME keeps the broad union intact but drops it out
of the precise sweep's expectation, so the precise test fails.

The precise sweep's resolver is the part that has been wrong twice — once too
narrow (a regex crediting declarations) and once too wide (an alias arm crediting
any call argument). Its contract, and both retracted arguments, are recorded at
`_emitted_attribute_keys`; precision and recall are each witnessed against
synthetic fixtures rather than asserted in prose.

**WHAT THIS SUITE DOES AND DOES NOT GUARANTEE.** Earlier revisions of this header
claimed *"an undeclared key cannot hide"*. That claim is RETRACTED: it was
falsified by execution twice — a composed key and an imported key constant each
passed the whole suite while wiring an unregistered or `emitted=False` attribute.
Static analysis of arbitrary Python cannot deliver that guarantee, and each round
of chasing one more indirection shape surfaced another. The honest statement is
narrower and is what the tests actually enforce:

  * a key written as a whole literal, or as a resolvable module constant, in an
    attribute-key position, is checked against the register — in BOTH directions;
  * a key ASSEMBLED from fragments is REFUSED outright for the enumerated
    composition shapes, rather than silently resolved;
  * everything else is a NAMED RESIDUAL, enumerated at register row `B-146` rather
    than left for a reader to discover.

Line numbers in `declaring_authority` strings are NOT asserted — the Runtime
spec is a delta chain whose line offsets move on every unrelated amendment, so
pinning them here would manufacture failures in arcs that touched nothing. The
named FILE is asserted to exist; the offsets are a reader's aid.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from harness_cp.retry_fallback_namespace import (
    RETRY_NAMESPACE_SCHEMA,
    RETRY_SPAN_AND_EVENT_NAMES,
    RETRY_WIRE_REGISTER,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]

#: Any `retry.`-prefixed literal. `"retry.*"` (the namespace NAME, as it appears
#: in the export manifest) deliberately does NOT match — `*` is outside the
#: class, and the namespace name is not a wire key. The class admits uppercase
#: and digits even though every current key is lower-snake: a drift catcher whose
#: pattern is narrower than the space it guards has a hole, and an off-convention
#: key is exactly the kind a reviewer would miss (self-caught while probing the
#: liveness check, where a renamed `retry.attempt.FIRSTX` slipped the sweep).
_RETRY_LITERAL = re.compile(r'"(retry\.[A-Za-z0-9_.]+)"')

_RETRY_PREFIX = "retry."

#: The `retry.`-prefixed subset of C-CP-03 §3.5. The sixth schema member is
#: `engine.replay_disposition`, which rides the `engine.*` namespace and is
#: correctly NOT a `retry.*` wire key.
_CP_DECLARED = frozenset(
    a.attribute_name for a in RETRY_NAMESPACE_SCHEMA if a.attribute_name.startswith("retry.")
)

_REGISTERED = frozenset(e.attribute_name for e in RETRY_WIRE_REGISTER)
_REGISTERED_EMITTED = frozenset(e.attribute_name for e in RETRY_WIRE_REGISTER if e.emitted)


#: The module that DECLARES the registers. Every registered name occurs here by
#: definition, so a liveness check that scans it is vacuous — see
#: `test_every_declared_name_has_a_site_outside_its_own_declaration`.
_DECLARATION_HOME = "harness-cp/src/harness_cp/retry_fallback_namespace.py"


def _src_modules(*, exclude_declaration_home: bool = False) -> list[Path]:
    modules = [
        m for src in sorted(_REPO_ROOT.glob("harness-*/src")) for m in sorted(src.rglob("*.py"))
    ]
    if exclude_declaration_home:
        modules = [m for m in modules if m.relative_to(_REPO_ROOT).as_posix() != _DECLARATION_HOME]
    return modules


def _sweep(
    pattern: re.Pattern[str], *, exclude_declaration_home: bool = False
) -> dict[str, set[str]]:
    """Every match of `pattern`, mapped to the modules it was found in."""
    found: dict[str, set[str]] = {}
    for module in _src_modules(exclude_declaration_home=exclude_declaration_home):
        for key in pattern.findall(module.read_text(encoding="utf-8")):
            found.setdefault(key, set()).add(module.relative_to(_REPO_ROOT).as_posix())
    return found


#: Parsed live-tree modules, cached. Lowercase deliberately: this is MUTABLE
#: module state, and pyright strict refuses to let an UPPERCASE name be rebound
#: (reportConstantRedefinition). Parsing 398 modules is the whole cost here
#: (~5s), and FOUR checks need it, so an uncached scan multiplied it on EVERY
#: suite run — out-of-family round 6 [P2], measured at 11.2s + 9.8s of a 23s run.
#: Caching the PARSE rather than each consumer's result is what actually fixes it:
#: a first attempt memoized only one consumer's answer, and adding the next
#: full-tree check immediately re-introduced the cost it was meant to remove.
#: Fixture calls pass `modules` explicitly and are deliberately NEVER cached — each
#: fixture is a different tree, and sharing them would make the witnesses lie.
_live_trees_cache: list[tuple[Path, ast.Module]] | None = None


def _parsed(modules: list[Path] | None) -> list[tuple[Path, ast.Module]]:
    global _live_trees_cache
    if modules is not None:
        return [(m, ast.parse(m.read_text(encoding="utf-8"))) for m in modules]
    if _live_trees_cache is None:
        _live_trees_cache = [(m, ast.parse(m.read_text(encoding="utf-8"))) for m in _src_modules()]
    return _live_trees_cache


def _is_fragment(value: str) -> bool:
    """A string that could become part of a `retry.*` key.

    Includes the bare namespace `"retry"`, because a producer can split the key at
    the separator (`NAMESPACE + "." + suffix`) and then NO fragment contains
    `retry.` — the shape out-of-family round 7 raised, which the first net missed
    entirely. Measured at HEAD: this form flags ZERO sites, while a looser net
    matching any string merely CONTAINING "retry" flags TWELVE (log and error
    messages) — so the boundary is drawn where it is by measurement, not taste.
    """
    return value == "retry" or _RETRY_PREFIX in value


def _composition_parts(node: ast.AST) -> list[ast.expr]:
    """Operands of any string-composition shape, flattened one level.

    `+`, f-strings (unwrapping interpolations, so `f"{PREFIX}x"` counts — the
    sibling of the shape the first net DID catch), `str.join`, `str.format` and
    `%`. Not exhaustive over everything Python can do, which is the point of the
    residual note at `_composed_key_sites`.
    """
    parts: list[ast.expr] = []
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        parts = [node.left, node.right]
    elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mod):
        parts = [node.left]
    elif isinstance(node, ast.JoinedStr):
        parts = [p.value if isinstance(p, ast.FormattedValue) else p for p in node.values]
    elif (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in {"join", "format"}
    ):
        parts = [node.func.value, *node.args]
    flat: list[ast.expr] = []
    for part in parts:
        if isinstance(part, ast.List | ast.Tuple):
            flat.extend(part.elts)
        else:
            flat.append(part)
    return flat


def _composed_key_sites(modules: list[Path] | None = None) -> list[str]:
    """Sites where a `retry.`-prefixed key is ASSEMBLED rather than written whole.

    A key built by concatenation or f-string (`PREFIX + "new_metric"`) is invisible
    to both the literal regex and the constant resolver, so an unregistered emitted
    key could hide behind it — which would void this suite's core guarantee rather
    than merely bound it (out-of-family round 6 [P2]).

    Statically evaluating arbitrary expressions is the wrong ambition here. This
    FAILS CLOSED instead, over the shapes enumerated at `_composition_parts`: `+`,
    f-strings (including interpolated fragment names), `str.join`, `str.format` and
    `%`, with the bare namespace `"retry"` treated as a fragment so a key split at
    the separator is still caught. Zero sites exist at HEAD, so the refusal costs
    nothing today and converts a silent hole into a loud one.

    **NOT EXHAUSTIVE, and the earlier claim that it was is RETRACTED.** A fragment
    held as a class attribute, imported from another module, accumulated by
    `+=`, or routed through `functools.partial` is not detected. Widening further
    was measured and rejected: a net matching any string merely CONTAINING "retry"
    flags TWELVE sites at HEAD, all of them log and error messages. The residual is
    recorded at `B-146`, not chased — closing shapes one at a time is what turned
    the preceding review rounds into an arms race.
    """
    sites: list[str] = []
    for module, tree in _parsed(modules):
        label = module.name if modules is not None else module.relative_to(_REPO_ROOT).as_posix()

        # A fragment is often held in its own constant — `PREFIX = "retry."` — so the
        # operand at the concatenation is a Name, not a literal. Resolving those is
        # required, not optional: the canonical example in the finding that prompted
        # this check has exactly that shape, and the first draft missed it (caught by
        # this function's own vacuity witness before it shipped).
        fragment_names = {
            target.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Assign)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
            and _is_fragment(node.value.value)
            for target in node.targets
            if isinstance(target, ast.Name)
        }

        def is_retry_fragment(part: ast.expr, names: set[str] = fragment_names) -> bool:
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                return _is_fragment(part.value)
            return isinstance(part, ast.Name) and part.id in names

        for node in ast.walk(tree):
            if any(is_retry_fragment(part) for part in _composition_parts(node)):
                sites.append(f"{label}:{node.lineno}")
    return sites


def _emitted_attribute_keys(modules: list[Path] | None = None) -> dict[str, set[str]]:
    """`retry.*` keys in genuine EMISSION position, resolved by AST not regex.

    `modules` overrides the swept set so the resolver's PRECISION can be witnessed
    against synthetic fixtures. It had no such parameter at first, which is exactly
    why a false positive shipped untested — the live pin could only ever witness
    RECALL (out-of-family round 5 + merge-gate lens 3, converging).

    **What counts — an ATTRIBUTE-KEY POSITION, never a mere mention.** Six shapes,
    each one a position whose value definitionally becomes the key:

      1. a literal first argument of `.set_attribute(...)`
      2. a literal key of an inline `attributes={...}` keyword mapping
      3. a NAME resolving to a module `retry.*` constant, at either position above
      4. that same NAME at the forwarded parameter INDEX of a module-local helper
         that hands a parameter straight to `.set_attribute(...)` as the key — the
         in-tree instance is `webhook_delivery_composer._set`
      5. `attributes=<Name>` where the Name was assigned an inline dict
      6. `mapping["retry.xxx"] = value`, the in-place mutation shape

    **What does NOT count, and why the restriction is load-bearing.** A regex could
    not tell a declaration from an emission: a `"retry.*":`-shaped pattern matched
    the `AttributeSpec` schema mapping at `hitl_webhook_namespace.py:119`, leaving
    this check GREEN after every real `retry.attempt_number` producer was deleted
    (out-of-family round 2 [P2]). The AST rewrite fixed that — and then its own
    first alias arm credited ANY call argument, which **re-opened the same hole
    from the other side**: a lint-clean DRY hoist of a declaration literal into a
    module constant made a schema declaration read as a producer, and merge-gate
    lens 3 proved it by deleting all seven real `retry.fail_class` producers and
    watching the suite stay green. Restricting to key positions closes both.

    **A retracted argument, recorded because it was wrong.** That loose arm was
    defended as "biased toward counting, and over-counting fails loudly". It does
    not: over-counting is loud only for the two `emitted=False` rows and for
    unregistered keys. For the ten keys already in the expected set — exactly the
    population this sweep protects — over-counting is SILENT and masks total
    producer loss. The bias inverted the risk where it mattered most.

    Precision and recall are both witnessed against fixtures, not just asserted:
    see `test_the_resolver_does_not_credit_declarations_as_emissions` and
    `test_the_resolver_credits_the_real_emission_shapes`.

    **REMAINING BOUNDS, stated rather than glossed, and no longer claimed to be
    harmless.** `set_attributes` (plural) has zero occurrences tree-wide and every
    in-tree `add_event` passes `attributes=` by keyword. Not resolved: a helper
    reached as a METHOD (`self._set(...)`), a forwarding chain, a key passed to a
    helper BY KEYWORD, and — the one that genuinely escapes every arm — a key
    constant DECLARED IN THE DECLARATION HOME and imported by a producer, since the
    literal then lives only in the module the liveness check excludes. A dict built
    across several statements resolves only the keys present at its literal
    assignment.

    The earlier claim that each residual is "covered from the other side" is
    NARROWED: it holds for locally-declared literals, and NOT for the imported-
    constant case, which merge-gate lens 3 demonstrated end-to-end. Enumerated at
    `B-146`.
    """
    found: dict[str, set[str]] = {}

    def record(key: str, module: Path, shape: str) -> None:
        if key.startswith(_RETRY_PREFIX):
            name = module.name if modules is not None else module.relative_to(_REPO_ROOT).as_posix()
            found.setdefault(key, set()).add(f"{name}:{shape}")

    def retry_str(node: ast.expr | None) -> str | None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value if node.value.startswith(_RETRY_PREFIX) else None
        return None

    for module, tree in _parsed(modules):
        # Mappings that actually REACH a telemetry sink as `attributes=<Name>`. A
        # `mapping["retry.x"] = v` write is credited only for these: an ordinary
        # dict (`cache["retry.terminal"] = v`) is not an emission, and crediting it
        # was a live false-positive path (out-of-family round 7 [P2]).
        sink_mappings = {
            keyword.value.id
            for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            for keyword in node.keywords
            if keyword.arg == "attributes" and isinstance(keyword.value, ast.Name)
        }

        # `NAME = "retry.xxx"` — a constant standing in for one key.
        aliases: dict[str, str] = {}
        # A name rebound to anything else is no longer trustworthy: crediting the
        # stale literal would report an emission the code does not make, and could
        # mask real producer loss (out-of-family round 7 [P2]).
        rebound: set[str] = set()
        # `ATTRS = {"retry.xxx": ...}` — a variable-backed attribute mapping,
        # so `attributes=ATTRS` can be resolved instead of silently skipped.
        map_aliases: dict[str, set[str]] = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Assign):
                continue
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            literal = retry_str(node.value)
            if literal is not None:
                for name in names:
                    aliases[name] = literal
            elif isinstance(node.value, ast.Dict):
                rebound.update(names)
                # REPLACE, never accumulate: a mapping rebound to a fresh dict no
                # longer carries the earlier keys, and `setdefault().update()` kept
                # crediting them — reporting emissions the runtime never sends
                # (out-of-family round 8 [P2], the map-shaped sibling of the scalar
                # alias rebinding handled just below).
                keys = {k for k in (retry_str(k) for k in node.value.keys) if k}
                for name in names:
                    map_aliases[name] = keys
            if literal is None:
                rebound.update(names)

            # `attributes["retry.xxx"] = value` — mutation of a mapping in place.
            for target in node.targets:
                if (
                    isinstance(target, ast.Subscript)
                    and isinstance(target.value, ast.Name)
                    and target.value.id in sink_mappings
                ):
                    key = retry_str(target.slice)
                    if key is not None:
                        record(key, module, "dict-item")

        for name in rebound:
            aliases.pop(name, None)

        # A module-local forwarding helper: some parameter is handed straight to
        # `.set_attribute(...)` as the KEY. `webhook_delivery_composer._set` is the
        # in-tree instance. Recorded WITH ITS PARAMETER INDEX, so a call is credited
        # only at the position that actually becomes the attribute key — never for
        # merely mentioning a constant somewhere in an argument list.
        helper_key_index: dict[str, int] = {}
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                continue
            params = [a.arg for a in node.args.args]
            for inner in ast.walk(node):
                if (
                    isinstance(inner, ast.Call)
                    and isinstance(inner.func, ast.Attribute)
                    and inner.func.attr == "set_attribute"
                    and inner.args
                    and isinstance(inner.args[0], ast.Name)
                    and inner.args[0].id in params
                ):
                    helper_key_index[node.name] = params.index(inner.args[0].id)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func

            if isinstance(func, ast.Attribute) and func.attr == "set_attribute" and node.args:
                first = node.args[0]
                literal = retry_str(first)
                if literal is not None:
                    record(literal, module, "set_attribute")
                elif isinstance(first, ast.Name) and first.id in aliases:
                    record(aliases[first.id], module, "set_attribute-via-constant")

            for keyword in node.keywords:
                if keyword.arg != "attributes":
                    continue
                if isinstance(keyword.value, ast.Dict):
                    for key_node in keyword.value.keys:
                        literal = retry_str(key_node)
                        if literal is not None:
                            record(literal, module, "attributes=")
                        elif isinstance(key_node, ast.Name) and key_node.id in aliases:
                            record(aliases[key_node.id], module, "attributes=-via-constant")
                elif isinstance(keyword.value, ast.Name):
                    for key in map_aliases.get(keyword.value.id, ()):
                        record(key, module, "attributes=-via-map")

            if isinstance(func, ast.Name) and func.id in helper_key_index:
                index = helper_key_index[func.id]
                if index < len(node.args):
                    argument = node.args[index]
                    if isinstance(argument, ast.Name) and argument.id in aliases:
                        record(aliases[argument.id], module, "via-constant")
    return found


def test_the_sweep_reads_a_populated_source_tree() -> None:
    """A sweep over an empty file list passes every set comparison vacuously."""
    modules = _src_modules()
    assert len(modules) > 100, f"source sweep found only {len(modules)} modules"
    # The exclusion must remove exactly one module — a rename that silently
    # disabled it would otherwise weaken the liveness check below.
    assert len(modules) - len(_src_modules(exclude_declaration_home=True)) == 1


def test_every_retry_literal_in_src_is_declared_somewhere() -> None:
    """The BROAD sweep — no undeclared `retry.`-prefixed literal in `src`.

    Expected set is the three buckets unioned. The register's `emitted=False`
    rows ARE expected here: they appear as literals in their own declaration,
    which is exactly where a mandated-but-unwired key should be visible.
    """
    expected = _CP_DECLARED | _REGISTERED | frozenset(RETRY_SPAN_AND_EVENT_NAMES)
    found = _sweep(_RETRY_LITERAL)

    undeclared = {k: sorted(v) for k, v in found.items() if k not in expected}
    assert not undeclared, (
        "undeclared `retry.*` literal(s) — add each to RETRY_WIRE_REGISTER with "
        f"its authorizing clause, or to RETRY_SPAN_AND_EVENT_NAMES: {undeclared}"
    )


def test_every_declared_name_has_a_site_outside_its_own_declaration() -> None:
    """Liveness — a declared name whose last real site disappears fails HERE.

    Scanning the declaration home would make this vacuous: every registered name
    occurs there by construction, so the check would pass even after the only
    producer or consumer was deleted (out-of-family review round 1 [P2], which
    demonstrated it by restricting the sweep to that one module and getting an
    empty diff). The home is therefore excluded.

    The two `emitted=False` rows are excluded from the expectation, not from the
    sweep: they are mandated-but-unwired BY RECORD (`B-145`), so having no site
    outside their declaration is their CURRENT truth, and asserting otherwise
    would demand the very wiring that row exists to track.
    """
    expected_live = _CP_DECLARED | _REGISTERED_EMITTED | frozenset(RETRY_SPAN_AND_EVENT_NAMES)
    found = _sweep(_RETRY_LITERAL, exclude_declaration_home=True)

    dead = expected_live - set(found)
    assert not dead, (
        "declared `retry.*` name(s) with no site outside their own declaration — "
        f"the last producer/consumer went away, or the row should be dropped: {sorted(dead)}"
    )
    assert len(expected_live) == 13


def test_emitted_attribute_keys_match_the_declared_emitted_set() -> None:
    """The PRECISE sweep — the wire's attribute keys, exactly.

    This is `B-126`'s corrected count of TEN, re-derived by a sweep shape
    independent of the one that produced it: 5 CP-declared + 5 registered.

    Emission position is resolved by AST — see `_emitted_attribute_keys` for why
    a regex could not, and for the one declared bound.
    """
    found = set(_emitted_attribute_keys())
    expected = _CP_DECLARED | _REGISTERED_EMITTED

    assert found == expected, (
        "emitted `retry.*` attribute keys diverge from the declared set "
        f"(unregistered: {sorted(found - expected)}; "
        f"declared-emitted but never set: {sorted(expected - found)})"
    )
    assert len(found) == 10


def test_a_helper_based_emission_is_resolved_not_missed() -> None:
    """The named-constant shape is CREDITED — `B-145`'s closure path depends on it.

    `webhook_delivery_composer.py:59` declares `ATTR_RETRY_ATTEMPT_NUMBER` and
    `:293` emits it through `_set(...)`, never naming the literal at the call. If
    the sweep ignored that shape, wiring `retry.backoff_ms` the same way would
    leave its `emitted=False` row falsely green (out-of-family round 3 [P2]).

    Asserted on the LIVE site rather than a fixture, so the check dies with the
    pattern it guards instead of outliving it.
    """
    shapes = _emitted_attribute_keys()["retry.attempt_number"]
    assert any(s.endswith(":via-constant") and "webhook_delivery_composer" in s for s in shapes), (
        f"helper-based emission no longer resolved: {sorted(shapes)}"
    )


def _fixture(tmp_path: Path, body: str) -> list[Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    module = tmp_path / "fixture_module.py"
    module.write_text(body, encoding="utf-8")
    return [module]


def test_the_resolver_does_not_credit_declarations_as_emissions(tmp_path: Path) -> None:
    """PRECISION — a constant MENTIONED in a declaration is not an emission.

    This is the defect that shipped and had to be corrected: the first version of
    the alias arm credited ANY call argument, so a lint-clean DRY hoist of a
    declaration literal into a module constant made a pure schema declaration read
    as a producer — silently voiding the precise sweep for a key already in the
    expected set. Merge-gate lens 3 proved it by deleting all seven real
    `retry.fail_class` producers and watching the suite stay green.

    Two shapes are asserted NOT credited, one from each reviewer:
      * a keyword-argument declaration (`AttributeSpec(attribute_name=CONST)`)
      * a span/event NAME constant handed to `add_event` (out-of-family round 5 —
        crediting it would make a legitimate refactor of a
        `RETRY_SPAN_AND_EVENT_NAMES` member fail the exact-set test)
    """
    modules = _fixture(
        tmp_path,
        'ATTR = "retry.fail_class"\n'
        'EVENT = "retry.skipped"\n'
        "SPEC = AttributeSpec(attribute_name=ATTR)\n"
        "MAPPING = {ATTR: 1}\n"
        "record(tail_keep_on_attribute=ATTR)\n"
        "span.add_event(EVENT)\n"
        "log.info(ATTR)\n",
    )
    assert _emitted_attribute_keys(modules) == {}


def test_no_retry_key_is_assembled_rather_than_written_whole() -> None:
    """FAIL CLOSED on a composed key, rather than silently missing it.

    A key built by concatenation or f-string is invisible to both the literal
    regex and the constant resolver, so an unregistered emitted key could hide —
    voiding this suite's core guarantee rather than merely bounding it
    (out-of-family round 6 [P2]). Statically evaluating arbitrary expressions is
    the wrong ambition; refusing composition outright is exact and cheap.

    ZERO sites at HEAD, so this costs nothing today. If a future producer needs a
    composed key, the fix is to write it whole and register it — not to relax this.
    """
    sites = _composed_key_sites()
    assert not sites, (
        "`retry.`-prefixed key(s) assembled by concatenation or f-string, which the "
        f"drift resolver cannot see — write the key whole and register it: {sites}"
    )


def test_the_composition_refusal_is_not_vacuous(tmp_path: Path) -> None:
    """The fail-closed check must actually fire on the shape it forbids."""
    concatenated = _fixture(tmp_path, 'PREFIX = "retry."\nKEY = PREFIX + "new_metric"\n')
    interpolated = _fixture(tmp_path / "b", 'KEY = f"retry.{suffix}"\n')
    assert _composed_key_sites(concatenated), "concatenation not detected"
    assert _composed_key_sites(interpolated), "f-string not detected"
    # And a whole literal must NOT trip it.
    assert not _composed_key_sites(_fixture(tmp_path / "c", 'K = "retry.delay_ms"\n'))


def test_a_rebound_alias_is_not_credited(tmp_path: Path) -> None:
    """A name rebound before use must not credit its old literal.

    `KEY = "retry.terminal"` then `KEY = compute()` then `set_attribute(KEY, ...)`
    emits something unknown — reporting the stale literal would claim an emission
    the code does not make, and could mask real producer loss (out-of-family round
    7 [P2]). Distrusting any rebound name is the conservative direction.
    """
    modules = _fixture(
        tmp_path,
        'KEY = "retry.terminal"\nKEY = compute()\nspan.set_attribute(KEY, 1)\n',
    )
    assert _emitted_attribute_keys(modules) == {}


def test_the_composition_refusal_covers_the_split_namespace(tmp_path: Path) -> None:
    """A key split AT THE SEPARATOR must still be refused.

    `NAMESPACE = "retry"` then `NAMESPACE + "." + suffix` leaves NO fragment
    containing `retry.`, so the first version of the refusal — and the broad literal
    sweep, and the resolver — all missed it entirely (out-of-family round 7 [P2]).
    The f-string interpolation form is the sibling merge-gate lens 3 raised.
    """
    for body in (
        'NAMESPACE = "retry"\nKEY = NAMESPACE + "." + suffix\n',
        'PREFIX = "retry."\nKEY = f"{PREFIX}new_metric"\n',
        'PREFIX = "retry."\nKEY = "".join([PREFIX, "new_metric"])\n',
        'KEY = "retry.{}".format(suffix)\n',
        'KEY = "retry.%s" % suffix\n',
    ):
        target = tmp_path / str(abs(hash(body)))
        assert _composed_key_sites(_fixture(target, body)), f"not refused: {body!r}"


def test_the_resolver_credits_the_real_emission_shapes(tmp_path: Path) -> None:
    """RECALL — the shapes a producer actually uses are all resolved.

    The two mapping shapes were BOTH declared bounds until out-of-family round 5
    pointed out that `attributes=<Name>` is already live in-tree, so a `B-145` key
    wired that way would leave `emitted=False` falsely green. Closing them is
    cheaper than documenting them.
    """
    modules = _fixture(
        tmp_path,
        "def _set(span, key, value):\n"
        "    span.set_attribute(key, value)\n"
        'KEY = "retry.terminal"\n'
        'span.set_attribute("retry.delay_ms", 1)\n'
        'span.set_attribute(KEY, "x")\n'
        '_set(span, KEY, "y")\n'
        'span.add_event("e", attributes={"retry.attempt_number": 1})\n'
        'ATTRS = {"retry.backoff_ms": 250}\n'
        'span.add_event("e", attributes=ATTRS)\n'
        "sink = {}\n"
        'sink["retry.cause_class"] = "z"\n'
        'span.add_event("e", attributes=sink)\n'
        'cache["retry.original_span_id"] = "not-an-emission"\n',
    )
    assert set(_emitted_attribute_keys(modules)) == {
        "retry.delay_ms",
        "retry.terminal",
        "retry.attempt_number",
        "retry.backoff_ms",
        "retry.cause_class",
    }


def test_the_unemitted_rows_are_not_emitted_anywhere() -> None:
    """The converse of the precise sweep, for the `emitted=False` rows.

    Liveness excludes them by design, so asserting the converse keeps `B-145`'s
    record honest until the wiring lands, at which point this fails and forces the
    flag to move. RENAMED at the arc close: it keys on EMISSION and does not exclude
    the declaration home, so the former "…have_no_site_outside_their_declaration"
    described neither — the U-OD-60 precedent moves the name with the assertion.

    Keyed on EMISSION, not on literal presence. A literal-presence check rejected a
    legitimate consumer-only change: a sampler or schema merely MENTIONING the key,
    with no producer anywhere, would fail here while the precise sweep correctly saw
    no emission — so CI could not go green on a valid diff (out-of-family round 8
    [P2]). That makes this partly redundant with the precise sweep, accepted
    deliberately: the diagnostic here names `B-145` and the flag to flip, which a
    bare set-equality failure does not.
    """
    found = _emitted_attribute_keys()
    for entry in RETRY_WIRE_REGISTER:
        if not entry.emitted:
            assert entry.attribute_name not in found, (
                f"{entry.attribute_name} is marked emitted=False but is now EMITTED at "
                f"{sorted(found[entry.attribute_name])} — flip the flag (B-145)"
            )


def test_the_register_is_disjoint_from_the_cp_declared_schema() -> None:
    """The register is what §3.5 does NOT declare — overlap means one is wrong."""
    assert not (_REGISTERED & _CP_DECLARED)
    assert len(_CP_DECLARED) == 5
    assert len(RETRY_NAMESPACE_SCHEMA) == 6  # the sixth is `engine.replay_disposition`
    assert len(RETRY_WIRE_REGISTER) == 7


def test_names_are_not_attribute_keys() -> None:
    """A span/event name must never be counted as a wire attribute."""
    names = frozenset(RETRY_SPAN_AND_EVENT_NAMES)
    assert len(RETRY_SPAN_AND_EVENT_NAMES) == len(names) == 3
    assert not (names & _CP_DECLARED)
    assert not (names & _REGISTERED)


def test_unemitted_keys_are_exactly_the_two_b145_registers() -> None:
    """The mandated-but-unwired set is DATA, so closing it must edit this line.

    `retry.backoff_ms` and `retry.cause_class` are named at four Runtime step
    bullets and set by zero producers (`B-145`). Wiring either one flips its
    `emitted` flag, and this assertion forces that edit rather than letting the
    gap quietly disappear — or quietly grow.
    """
    unemitted = {e.attribute_name for e in RETRY_WIRE_REGISTER if not e.emitted}
    assert unemitted == {"retry.backoff_ms", "retry.cause_class"}


def test_every_registered_key_cites_an_authority_that_resolves() -> None:
    """Each row names a clause, and the spec file it names exists at HEAD."""
    for entry in RETRY_WIRE_REGISTER:
        assert "§" in entry.declaring_authority, entry.attribute_name
        cited = re.findall(r"([A-Za-z_0-9]+\.md)", entry.declaring_authority)
        assert cited, f"{entry.attribute_name} names no artifact"
        for name in cited:
            assert (_REPO_ROOT / "design-substrate" / name).is_file(), name


def test_most_of_the_wire_surface_beyond_cp_is_mandated_not_discretionary() -> None:
    """`B-126`'s load-bearing correction, pinned.

    The row was filed on the premise that these keys ride an unbounded
    telemetry-volume discretion lane. Grounding found the opposite: only
    `retry.skipped.candidate` is pure discretion; the other six are mandated by
    name. A future arc that re-reads this surface as "all discretionary" fails
    here.
    """
    discretionary = {e.attribute_name for e in RETRY_WIRE_REGISTER if not e.binding}
    assert discretionary == {"retry.skipped.candidate"}
