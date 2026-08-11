#!/usr/bin/env python3
"""Derive the canonical per-family artifact heads table from `.harness/clearance/`.

R-CTX-1 / U-CTX-11.

Root `CLAUDE.md` §2.3/§2.4 carry the per-axis spec + plan head versions as hand-maintained
prose. That is the workspace's #1 defect class (stale-carry text): the AS spec head sat at
`v1.13` in §2.3 while `.harness/clearance/spec-action-surface-v1-14-cleared-2026-07-15.md`
had cleared `v1.14`. The clearance corpus is the version-binding record (root `CLAUDE.md`
§4.5), so it — not prose — is the authority this tool derives from.

Three properties the naive version of this tool would get wrong:

**Fail-closed.** There is NO regex fallback. A marker that cannot be parsed as a clearance
marker is an ERROR that aborts the derivation, never a silently-skipped row. (The parse
itself is `tools/clearance_frontmatter.py`'s, whose own gate has the matching fail-closed
contract; a marker exempted there is exempted here, by the same single manifest.)

**Family normalization.** The corpus carries TWO marker-filename conventions —
`Spec_Control_Plane-v1_32-cleared-2026-06-13.md` (CamelCase artifact stem, `_`-joined
version) and `spec-control-plane-v1-116-cleared-2026-08-09.md` (all-kebab). Deriving the
family from the FILENAME is measurably wrong: 11 markers disagree with their own `artifact:`
field (`PRD_v1_2-cleared-...` -> `prd-v1-2`; `cross-axis-composition-v2-23-cleared-...` ->
`cross-axis-composition` vs the artifact's `Cross_Axis_Composition_Document`;
`provider-construction-allowlist-prefer-oauth-cleared-...` names nothing in its path). So
the family is derived from the `artifact:` PATH, which both conventions agree on, and the
filename is not consulted at all.

**Version-aware sort.** Versions are compared as integer tuples, so `v1.9 < v1.10 < v1.116`.
A lexicographic sort puts `v1.9` above every `v1.1x` and would report the wrong CP head.

Two gates, both wired into `just check` / `just codex-check` / CI:

* ``--check``             — the generated table equals the committed
  `.harness/artifact-heads.md`, byte for byte.
* ``--check-completeness`` — every family carrying any marker resolves to exactly one head,
  and every `design-substrate/` head names a file that exists at HEAD.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path, PurePosixPath

import clearance_frontmatter as cf

REPO_ROOT = cf.REPO_ROOT
TABLE_PATH = REPO_ROOT / ".harness" / "artifact-heads.md"
DESIGN_SUBSTRATE_PREFIX = "design-substrate/"

# `Spec_Control_Plane_v1_116` -> `Spec_Control_Plane`; `Spec_Action_Surface_v1` ->
# `Spec_Action_Surface`. ADR / PRD stems that carry no version suffix pass through.
_VERSION_SUFFIX = re.compile(r"_v\d+(_\d+)*$")
# A `version:` field is either a LEADING dotted version token — optionally followed by a
# parenthetical annotation the corpus really does carry (`v1.32 (in-place correction;
# version label unchanged)`) — or an opaque LABEL carrying no version at all
# (`§10-amendment (prefer-OAuth default; ...)`). Both are modelled; neither is skipped.
_VERSION_HEAD = re.compile(r"^v?(\d+(?:\.\d+)*)(?![\d.])")
_NON_ALNUM = re.compile(r"[^a-z0-9]+")


class ArtifactHeadsError(Exception):
    """The heads table could not be derived — never downgraded to a skipped row."""


@dataclass(frozen=True)
class Head:
    """The resolved head of one artifact family."""

    family: str
    artifact: str
    version: str
    cleared_at: str
    marker: str
    marker_count: int

    @property
    def is_design_substrate(self) -> bool:
        return self.artifact.startswith(DESIGN_SUBSTRATE_PREFIX)


def family_of(artifact: str) -> str:
    """Normalize an `artifact:` path to its family slug.

    Both marker-filename conventions resolve here identically because neither the filename
    nor its version spelling is consulted — only the artifact path is.
    """
    stem = PurePosixPath(artifact).stem
    stem = _VERSION_SUFFIX.sub("", stem)
    slug = _NON_ALNUM.sub("-", stem.lower()).strip("-")
    if not slug:
        raise ArtifactHeadsError(f"artifact path yields an empty family: {artifact!r}")
    return slug


def version_key(version: str) -> tuple[int, tuple[int, ...], str]:
    """Total order over `version:` values.

    `v1.116` -> `(1, (1, 116), 'v1.116')`. The version component is an INTEGER TUPLE, so
    `v1.9 < v1.10 < v1.116` — a lexicographic sort would put `v1.9` above every `v1.1x` and
    report the wrong CP head. A trailing parenthetical annotation is tolerated (the corpus
    carries several) but never a substitute for the token. A value with no leading version
    token is an opaque LABEL: it keeps its own place in the order, strictly below every
    numbered version, rather than being dropped.
    """
    text = version.strip()
    if not text:
        raise ArtifactHeadsError("empty version field")
    match = _VERSION_HEAD.match(text)
    if not match:
        return (0, (), text)
    return (1, tuple(int(part) for part in match.group(1).split(".")), text)


def is_numbered(version: str) -> bool:
    """True when the `version:` field carries a real version token, not just a label."""
    return version_key(version)[0] == 1


def _cleared_at(value: object) -> str:
    """Normalize the `cleared_at` field to an ISO date, or `-` when absent."""
    if value is None:
        return "-"
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value).strip()
    return text.split("T")[0] if text else "-"


_FILENAME_DATE = re.compile(r"cleared-(\d{4}-\d{2}-\d{2})")


def _marker_date(marker: cf.Marker) -> str:
    """The marker's effective date: `cleared_at` when present, else the date
    encoded in the marker filename (codex round-2 on PR-4: several in-place
    correction markers omit `cleared_at`, and `-` would rank them BELOW an
    older dated marker of the same numeric version)."""
    cleared = _cleared_at(marker.data.get("cleared_at"))
    if cleared != "-":
        return cleared
    match = _FILENAME_DATE.search(marker.path.name)
    return match.group(1) if match else "-"


def _marker_sort_key(marker: cf.Marker) -> tuple[int, tuple[int, ...], str, str, str]:
    """Highest version wins; ties break on effective date, then marker filename.

    The version's raw TEXT participates only as the FINAL tie-break (codex
    round-1 on PR-4): two markers sharing one numeric version but differing in
    annotation — a shape present in this corpus — must be ordered by their
    effective dates, not by which annotation string sorts higher.
    """
    kind, nums, text = version_key(marker.version)
    return (
        kind,
        nums,
        _marker_date(marker),
        marker.path.name,
        text,
    )


def derive(
    directory: Path = cf.CLEARANCE_DIR, manifest_path: Path = cf.MANIFEST_PATH
) -> list[Head]:
    """Resolve every family's head. Raises on the first unreadable marker — no fallback."""
    try:
        markers = list(cf.load_all_markers(directory, manifest_path))
    except cf.ClearanceFrontmatterError as exc:
        raise ArtifactHeadsError(
            f"clearance corpus is not fully parseable, so the heads table cannot be "
            f"derived: {exc}. Run `uv run python tools/clearance_frontmatter.py --check`."
        ) from exc

    grouped: dict[str, list[cf.Marker]] = {}
    for marker in markers:
        grouped.setdefault(family_of(marker.artifact), []).append(marker)

    heads: list[Head] = []
    for family, family_markers in sorted(grouped.items()):
        winner = max(family_markers, key=_marker_sort_key)
        heads.append(
            Head(
                family=family,
                artifact=winner.artifact,
                version=winner.version.strip(),
                cleared_at=_marker_date(winner),
                marker=winner.path.name,
                marker_count=len(family_markers),
            )
        )
    return heads


# ── rendering ───────────────────────────────────────────────────────────────────────────

_PREAMBLE = """<!--
GENERATED FILE — do not hand-edit.

Regenerate with:  uv run python tools/artifact_heads.py --write
CI gate:          uv run python tools/artifact_heads.py --check

R-CTX-1 / U-CTX-11. Derived from the `.harness/clearance/` marker corpus, which is the
version-binding record per root CLAUDE.md §4.5 — NOT from prose. Family is derived from each
marker's `artifact:` path (the corpus carries two marker-filename conventions and 11 of the
filenames disagree with their own artifact field, so filenames are not consulted). Versions
sort as integer tuples, so v1.9 < v1.10 < v1.116. Derivation is fail-closed: an unparseable
marker aborts the build rather than being skipped.
-->

# Canonical artifact heads

The head version of every artifact family with a clearance marker, derived from
`.harness/clearance/`. `Markers` is the number of markers filed for the family; `Head marker`
is the one that resolved the head.

"""

_DESIGN_HEADER = (
    "## `design-substrate/` families\n\n"
    "| Family | Head | Cleared | Artifact | Markers | Head marker |\n"
    "|---|---|---|---|---|---|\n"
)

_OTHER_HEADER = (
    "\n## Non-`design-substrate/` families\n\n"
    "Markers filed against an artifact outside `design-substrate/`. Enumerated rather than\n"
    "dropped, so a marker can never leave the corpus unaccounted for.\n\n"
    "| Family | Head | Cleared | Artifact | Markers | Head marker |\n"
    "|---|---|---|---|---|---|\n"
)


def _row(head: Head) -> str:
    return (
        f"| `{head.family}` | `{head.version}` | {head.cleared_at} | "
        f"`{head.artifact}` | {head.marker_count} | `{head.marker}` |\n"
    )


def render(heads: list[Head]) -> str:
    design = [h for h in heads if h.is_design_substrate]
    other = [h for h in heads if not h.is_design_substrate]
    parts = [_PREAMBLE, _DESIGN_HEADER]
    parts.extend(_row(h) for h in design)
    if other:
        parts.append(_OTHER_HEADER)
        parts.extend(_row(h) for h in other)
    return "".join(parts)


# ── gates ───────────────────────────────────────────────────────────────────────────────


def check_generated_matches_committed(
    table_path: Path = TABLE_PATH,
    directory: Path = cf.CLEARANCE_DIR,
    manifest_path: Path = cf.MANIFEST_PATH,
) -> list[str]:
    generated = render(derive(directory, manifest_path))
    if not table_path.exists():
        return [f"{table_path} is missing — run `uv run python tools/artifact_heads.py --write`"]
    committed = table_path.read_text(encoding="utf-8")
    if committed == generated:
        return []
    return [
        f"{table_path.name} is stale against the clearance corpus — run "
        f"`uv run python tools/artifact_heads.py --write` "
        f"({len(committed)} committed bytes vs {len(generated)} generated)"
    ]


def check_completeness(
    directory: Path = cf.CLEARANCE_DIR, manifest_path: Path = cf.MANIFEST_PATH
) -> list[str]:
    """Every family with a marker resolves to one head; every design-substrate head exists."""
    violations: list[str] = []
    heads = derive(directory, manifest_path)

    families = {h.family for h in heads}
    if len(families) != len(heads):
        violations.append("a family resolved to more than one head row")

    covered: set[str] = set()
    for marker in cf.load_all_markers(directory, manifest_path):
        covered.add(family_of(marker.artifact))
    missing = covered - families
    if missing:
        violations.append(f"families with markers but no resolvable head: {sorted(missing)}")

    for head in heads:
        if not head.is_design_substrate:
            continue
        if not (REPO_ROOT / head.artifact).exists():
            violations.append(
                f"`{head.family}` head `{head.version}` names a missing artifact: {head.artifact}"
            )
        if not is_numbered(head.version):
            violations.append(
                f"`{head.family}` head resolves to an unnumbered label `{head.version}` — a "
                f"design-substrate family must have a version-numbered head"
            )
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--check", action="store_true", help="generated table == committed table")
    parser.add_argument(
        "--check-completeness",
        action="store_true",
        help="every family with a marker resolves to a head that names a real artifact",
    )
    parser.add_argument("--write", action="store_true", help="regenerate the committed table")
    parser.add_argument("--print", action="store_true", help="print the generated table")
    parser.add_argument("--table", type=Path, default=TABLE_PATH)
    parser.add_argument("--dir", type=Path, default=cf.CLEARANCE_DIR)
    parser.add_argument("--manifest", type=Path, default=cf.MANIFEST_PATH)
    args = parser.parse_args(argv)

    try:
        heads = derive(args.dir, args.manifest)
    except ArtifactHeadsError as exc:
        print(f"artifact heads FAILED — {exc}", file=sys.stderr)
        return 1

    if args.write:
        args.table.write_text(render(heads), encoding="utf-8")
        print(f"wrote {args.table} — {len(heads)} families")
        return 0

    if args.print:
        sys.stdout.write(render(heads))
        return 0

    violations: list[str] = []
    run_default = not (args.check or args.check_completeness)
    try:
        if args.check or run_default:
            violations += check_generated_matches_committed(args.table, args.dir, args.manifest)
        if args.check_completeness or run_default:
            violations += check_completeness(args.dir, args.manifest)
    except ArtifactHeadsError as exc:
        print(f"artifact heads FAILED — {exc}", file=sys.stderr)
        return 1

    if violations:
        print(f"artifact heads FAILED — {len(violations)} violation(s):", file=sys.stderr)
        for violation in violations:
            print(f"  {violation}", file=sys.stderr)
        return 1
    design = sum(1 for h in heads if h.is_design_substrate)
    print(f"artifact heads OK — {len(heads)} families ({design} design-substrate), table current")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
