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


def test_safety_kernel_sections_stay_in_root() -> None:
    text = _read(ROOT_CLAUDE)
    headings = set(re.findall(r"^#{2,4} (\d+(?:\.\d+)*)\.? ", text, flags=re.MULTILINE))
    table_anchors = set(re.findall(r"^\| *\*\*(\d+(?:\.\d+)*) +\S", text, flags=re.MULTILINE))
    anchors = headings | table_anchors
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


def test_packs_declare_their_origin() -> None:
    for pack in sorted(filesystem_packs()):
        body = _read(GOVERNANCE / pack)
        assert "Relocated BYTE-VERBATIM from Root `CLAUDE.md`" in body, pack
