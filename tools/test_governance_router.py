"""U-CTX-15 — set-equality pin over the governance-pack router (R-CTX-1 Arc 5).

U-CTX-13 relocated root `CLAUDE.md` reference bodies into `docs/governance/*.md`. Three
venues advertise that roster to a runner — the load matrix at `docs/governance/README.md`,
the Claude-side router `CONTEXT.md`, and the Codex-side projection `AGENTS.md`. A pack
added, renamed, or dropped in one venue only is the drift this module forbids: every
assertion is SET EQUALITY against the filesystem, never a subset or a count.

Mutation-reasoning table — each mutation and the test that MUST go red for it:

   1 add a pack file without a README row       -> test_readme_matrix_matches_the_filesystem
   2 add a README row for a nonexistent pack    -> test_readme_matrix_matches_the_filesystem
   3 rename a pack in README only               -> test_readme_matrix_matches_the_filesystem
   4 drop a pack row from CONTEXT.md            -> test_context_router_matches_the_filesystem
   5 drop a pack row from AGENTS.md             -> test_agents_router_matches_the_filesystem
   6 weaken any assertion to a subset check     -> test_router_venues_agree_pairwise
   7 point a root pointer at a missing pack     -> test_every_root_pointer_resolves_to_a_pack
   8 relocate a safety-kernel section out of root-> test_safety_kernel_sections_stay_in_root
   9 break the AGENTS.md roadmap-recipe cite    -> test_agents_roadmap_cite_is_preserved
  10 leave a root section body in root AND pack -> (covered by U-CTX-13's own verification;
       this module pins the ROUTER, not the relocation)
  11 a pack header claims a § the pack lacks    -> test_pack_sections_match_origin_header
  12 a venue advertises a different § list      -> test_venues_advertise_pack_section_list
  13 a range endpoint names no real section     -> both of rows 11-12 (unresolvable set)
  14 a pack with zero headings passes vacuously -> both of rows 11-12 (per-pack non-empty)
  15 a range spans sections the pack lacks      -> both of rows 11-12 (root-universe basis)

Rows 11-12 were added 2026-09-17. Until then every assertion above compared pack FILENAMES,
so `project-framing.md` could advertise a relocation of root §7 into a pack that has never
carried a §7 and the whole module stayed green (it did, from 0f05512ca until that date; the
same wrong claim had been copied into all three venues). A runner that needs §7 follows the
router to a pack without it, which is the failure these two rows forbid.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[1]
GOVERNANCE = REPO / "docs" / "governance"
README = GOVERNANCE / "README.md"
CONTEXT = REPO / "CONTEXT.md"
AGENTS = REPO / "AGENTS.md"
ROOT_CLAUDE = REPO / "CLAUDE.md"

# The FULL path is required in every venue. A bare basename is ambiguous — the sibling
# `.harness/artifact-pointers/` roster uses the same naming shape, and a loose matcher
# silently pulled `spec-heads.md` / `plan-heads.md` into the pack roster.
PACK_RE = re.compile(r"`docs/governance/([a-z0-9-]+\.md)`")

# Relocating any of these out of root would move a load-bearing rule behind an optional
# read. They are named in `docs/governance/README.md` and pinned here.
SAFETY_KERNEL: tuple[str, ...] = (
    "1.3",
    "3.1",
    "3.2",
    "4.3",
    "4.4",
    "5",
    "5.1",
    "5.2",
    "8",
    "11",
    "11.1",
    "11.2",
    "11.3",
    "11.4",
    "11.5",
    "11.6",
    "12.2.1",
    "12.4.1",
    "13.1",
    "14",
)


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def filesystem_packs() -> set[str]:
    """Every governance pack on disk, README excluded (it is the router, not a pack)."""
    return {p.name for p in GOVERNANCE.glob("*.md")} - {"README.md"}


def _advertised(text: str) -> set[str]:
    return {name for name in PACK_RE.findall(text) if name != "README.md"}


def readme_packs() -> set[str]:
    return _advertised(_read(README))


def context_packs() -> set[str]:
    return _advertised(_read(CONTEXT))


def agents_packs() -> set[str]:
    return _advertised(_read(AGENTS))


def test_filesystem_roster_is_non_empty() -> None:
    # Guards every set-equality assertion below from passing vacuously.
    assert len(filesystem_packs()) >= 5


def test_readme_matrix_matches_the_filesystem() -> None:
    assert readme_packs() == filesystem_packs()


def test_context_router_matches_the_filesystem() -> None:
    assert context_packs() == filesystem_packs()


def test_agents_router_matches_the_filesystem() -> None:
    assert agents_packs() == filesystem_packs()


def test_router_venues_agree_pairwise() -> None:
    # Explicitly pairwise, so a mutation that swaps two venues' rosters cannot hide behind
    # a single shared comparison against the filesystem.
    assert readme_packs() == context_packs()
    assert context_packs() == agents_packs()
    assert agents_packs() == readme_packs()


def test_every_root_pointer_resolves_to_a_pack() -> None:
    cited = {name for name in re.findall(r"`docs/governance/([a-z0-9-]+\.md)`", _read(ROOT_CLAUDE))}
    assert cited, "root CLAUDE.md must point at the packs it relocated bodies into"
    assert cited <= filesystem_packs(), f"dangling root pointers: {cited - filesystem_packs()}"


def test_every_pack_is_pointed_at_from_root() -> None:
    cited = set(re.findall(r"`docs/governance/([a-z0-9-]+\.md)`", _read(ROOT_CLAUDE)))
    assert filesystem_packs() <= cited, f"orphan packs: {filesystem_packs() - cited}"


def root_sections() -> set[str]:
    """Every section root `CLAUDE.md` numbers — headings plus the `| **N.M` table anchors.

    Root keeps every heading with its number and position when a body is relocated, so
    this is the universe a `§` claim is written against.
    """
    text = _read(ROOT_CLAUDE)
    headings = set(re.findall(r"^#{2,4} (\d+(?:\.\d+)*)\.? ", text, flags=re.MULTILINE))
    table_anchors = set(re.findall(r"^\| *\*\*(\d+(?:\.\d+)*) +\S", text, flags=re.MULTILINE))
    return headings | table_anchors


def test_safety_kernel_sections_stay_in_root() -> None:
    text = _read(ROOT_CLAUDE)
    anchors = root_sections()
    assert set(SAFETY_KERNEL) <= anchors, f"missing kernel anchors: {set(SAFETY_KERNEL) - anchors}"
    # A kernel section that got relocated would leave a pointer where its body was.
    sections = dict(
        re.findall(
            r"^#{2,4} (\d+(?:\.\d+)*)\.? [^\n]*\n(.*?)(?=^#{2,4} \d|\Z)",
            text,
            flags=re.MULTILINE | re.DOTALL,
        )
    )
    relocated_kernel = [sec for sec in SAFETY_KERNEL if "docs/governance/" in sections.get(sec, "")]
    assert not relocated_kernel, f"safety-kernel sections relocated: {relocated_kernel}"


def test_agents_roadmap_cite_is_preserved() -> None:
    # The U-CTX-15 AC names this cite explicitly: it must survive the router edit and it
    # must still resolve, so root §12.2 has to remain a real heading.
    assert "per CLAUDE.md §12.2)" in _read(AGENTS)
    assert re.search(r"^### 12\.2 ", _read(ROOT_CLAUDE), flags=re.MULTILINE)


# A venue names a pack's sections as `§N`, an inclusive range `§A–§B` (en dash, as the
# packs write it) or the `§N.x` family shorthand CONTEXT.md and AGENTS.md use.
#
# Expansion is against ROOT `CLAUDE.md`'s section universe, never the pack's own headings,
# and that basis is the whole guarantee. Resolving against the pack makes every range
# self-satisfying, because a range can only ever yield sections the pack already has:
# `§12.5.1–§99` and `§1.1–§9.1` both filter down to exactly the pack's true set, so set
# equality cannot see either one. Two review rounds landed on that basis — the merge-gate
# witness lens caught the bad ENDPOINT (`§99`) and codex r2 caught the over-broad SPAN
# (`§1.1–§9.1`, which also advertises §2..§8, sections that live in other packs). Checking
# endpoints was a patch for the first and left the second; expanding against root fixes
# both at once, because a claim's meaning is what root numbers, not what the pack happens
# to contain. `unresolvable` then reports any token naming no root section at all.
SECTION_TOKEN_RE = re.compile(r"§(\d+(?:\.\d+)*)(?:\s*[–-]\s*§(\d+(?:\.\d+)*)|(\.x))?")
# Located by its text, not by a line number: `test_packs_declare_their_origin` only
# requires this sentence to be PRESENT, so pinning it to a line index would invent a
# stricter contract than the module already enforces.
PACK_ORIGIN_MARKER = "Relocated BYTE-VERBATIM from Root `CLAUDE.md`"


def _section_key(section: str) -> tuple[int, ...]:
    return tuple(int(part) for part in section.split("."))


def _expand_sections(spec: str, universe: set[str]) -> tuple[set[str], set[str]]:
    """`(sections this spec claims, tokens naming nothing in `universe`)`.

    `universe` is root's section set, so the returned set is what the spec MEANS, which
    the caller then compares against what the pack actually carries.
    """
    resolved: set[str] = set()
    unresolvable: set[str] = set()
    for start, end, dot_x in SECTION_TOKEN_RE.findall(spec):
        if end:
            lo, hi = _section_key(start), _section_key(end)
            resolved |= {sec for sec in universe if lo <= _section_key(sec) <= hi}
            unresolvable |= {bound for bound in (start, end) if bound not in universe}
        elif dot_x:
            family = {sec for sec in universe if sec == start or sec.startswith(f"{start}.")}
            resolved |= family
            if not family:
                unresolvable.add(f"{start}.x")
        else:
            resolved.add(start)
            if start not in universe:
                unresolvable.add(start)
    return resolved, unresolvable


def pack_headings(pack: str) -> set[str]:
    body = _read(GOVERNANCE / pack)
    return set(re.findall(r"^#{2,4} (\d+(?:\.\d+)*)\.? ", body, flags=re.MULTILINE))


def pack_claimed_sections(pack: str) -> tuple[set[str], set[str]]:
    """The sections a pack's own origin header says were relocated into it."""
    lines = [ln for ln in _read(GOVERNANCE / pack).splitlines() if PACK_ORIGIN_MARKER in ln]
    assert len(lines) == 1, f"{pack}: expected exactly one origin header, found {len(lines)}"
    return _expand_sections(lines[0], root_sections())


def venue_advertised_sections(pack: str) -> dict[str, tuple[set[str], set[str]]]:
    """Per venue, the sections that venue tells a runner to expect inside `pack`.

    README.md and CONTEXT.md carry a table row whose second cell is the section list;
    AGENTS.md is a single prose line with a parenthetical after each pack path.
    """
    universe = root_sections()
    quoted = re.escape(pack)
    row = re.compile(rf"^\|\s*`docs/governance/{quoted}`\s*\|([^|]*)\|", re.MULTILINE)
    paren = re.compile(rf"`docs/governance/{quoted}`\s*\(([^)]*)\)")
    found: dict[str, tuple[set[str], set[str]]] = {}
    for venue, text, pattern in (
        ("README.md", _read(README), row),
        ("CONTEXT.md", _read(CONTEXT), row),
        ("AGENTS.md", _read(AGENTS), paren),
    ):
        match = pattern.search(text)
        assert match, f"{venue} advertises no section list for {pack}"
        found[venue] = _expand_sections(match.group(1), universe)
    return found


def test_pack_sections_match_origin_header() -> None:
    # Set equality both ways: a claimed-but-absent § is the 2026-09-17 defect, and an
    # unclaimed heading means a section was relocated in without the header saying so.
    for pack in sorted(filesystem_packs()):
        headings = pack_headings(pack)
        # Non-vacuity, per pack: the aggregate roster guard above says nothing about
        # whether THIS pack has any headings, and `set() == set()` would pass.
        assert headings, f"{pack}: no numbered section headings"
        claimed, unresolvable = pack_claimed_sections(pack)
        assert not unresolvable, f"{pack}: origin header names no-such-section {unresolvable}"
        assert claimed == headings, pack


def test_venues_advertise_pack_section_list() -> None:
    for pack in sorted(filesystem_packs()):
        claimed, _ = pack_claimed_sections(pack)
        assert claimed, f"{pack}: origin header claims nothing"
        for venue, (advertised, unresolvable) in venue_advertised_sections(pack).items():
            assert not unresolvable, f"{venue} vs {pack}: no-such-section {unresolvable}"
            assert advertised == claimed, f"{venue} vs {pack}: {advertised} != {claimed}"


def test_packs_declare_their_origin() -> None:
    for pack in sorted(filesystem_packs()):
        body = _read(GOVERNANCE / pack)
        assert "Relocated BYTE-VERBATIM from Root `CLAUDE.md`" in body, pack
