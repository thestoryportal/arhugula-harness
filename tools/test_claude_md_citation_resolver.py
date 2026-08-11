"""Tests for the U-CTX-14 `CLAUDE.md` §-citation resolver.

Two halves. The SYNTHETIC half builds throwaway git repos and drives the resolver
table-driven over every citation shape the tracked corpus actually uses, plus the
negative cases that make the gate load-bearing. The LIVE half asserts the invariant
against HEAD itself.

NO TOTAL IS EVER ASSERTED (plan errata E3). The corpus grows every time a program doc
lands, so a pinned count would be a maintenance tax that fails for the wrong reason.
`test_census_is_derived_not_pinned` asserts the census is INTERNALLY CONSISTENT with the
citations it was derived from — a property that holds at any corpus size.

Every citation literal here is composed with an f-string over `SIGN` rather than written
out, because this module is itself tracked: a literal broken citation in a test fixture
would be scanned by the live gate and would turn HEAD red.

Mutation-reasoning table — each mutation and the test that MUST go red for it:

   1 drop TABLE_ANCHOR_RE from heading_sections
       -> test_bold_table_row_labels_are_section_anchors
   2 accept any bold span as an anchor, not just a first-cell label
       -> test_emphasis_inside_a_cell_is_not_an_anchor
   3 resolve every prefix to root (ignore the path component)
       -> test_axis_prefixed_cite_resolves_against_the_axis_file
   4 resolve an axis-prefixed cite to root AND the axis file
       -> test_axis_prefixed_cite_does_not_touch_root
   5 satisfy a cite from ANY CLAUDE.md rather than the one it names
       -> test_axis_prefixed_cite_to_a_root_only_section_fails
   6 drop brace expansion  -> test_brace_expanded_prefix_hits_every_named_axis
   7 drop glob expansion   -> test_glob_prefix_hits_every_matching_axis
   8 gate only the first member of an expanded prefix
       -> test_brace_expansion_is_gated_per_member
   9 treat an unresolvable directory as root
       -> test_unknown_directory_prefix_is_reported_not_gated
  10 treat a `~`-rooted path as root -> test_external_home_path_is_reported_not_gated
  11 drop the `.md` gap disqualifier -> test_intervening_filename_breaks_the_anchor
  12 drop gap_is_appositive, or widen it to two words
       -> test_multiword_clause_gap_is_not_a_citation, test_gap_is_appositive_unit_table
  13 narrow gap_is_appositive to zero words
       -> test_single_modifier_word_gap_is_still_a_citation
  14 raise the gap cap so a distant section is captured
       -> test_distant_section_is_not_captured
  15 drop CHAIN_RE -> test_chained_sibling_sections_inherit_the_target
  16 let CHAIN_RE cross arbitrary prose -> test_chain_does_not_cross_prose
  17 skip gating chained siblings -> test_chained_sibling_is_gated_too
  18 match a section by ancestor prefix instead of exactly
       -> test_subsection_under_an_existing_section_still_fails
  19 tolerate an anchor-free CLAUDE.md -> test_anchorless_claude_md_is_fail_closed
  20 tolerate a missing root CLAUDE.md -> test_missing_root_claude_md_is_fail_closed
  21 swallow an undecodable file silently
       -> test_undecodable_file_is_reported_not_silently_dropped
  22 drop the stale-waiver check from scan -> test_stale_waiver_fails_the_gate
  23 make a waiver cover any section/file -> test_waiver_does_not_cover_a_different_section,
       test_waiver_does_not_cover_a_different_file
  24 key waivers on line number rather than (file, target, section)
       -> test_waiver_survives_a_line_shift
  25 make --check return 0 unconditionally
       -> test_check_mode_exits_non_zero_on_a_broken_cite
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import claude_md_citation_resolver as resolver
import pytest

SIGN = resolver.SECTION_SIGN

ROOT_FIXTURE = "\n".join(
    [
        "# Root",
        "",
        "## 1. Alpha",
        "",
        "### 1.1 Beta",
        "",
        "## 12. Gamma",
        "",
        "### 12.5 Delta",
        "",
        "#### 12.5.4 Epsilon",
        "",
        "## 14. Conventions",
        "",
        "| Convention | Rule |",
        "|---|---|",
        "| **14.2 Named convention** | body text with **bold 99.9 emphasis** inside |",
        "",
    ]
)

AXIS_FIXTURE = "\n".join(
    [
        "# Axis",
        "",
        "## 4. Substitution",
        "",
        "### 4.1 Axis substitutions",
        "",
    ]
)

AXIS_DIRS = ("harness-cp", "harness-od")


def _repo(tmp_path: Path, docs: dict[str, str]) -> Path:
    """A throwaway git repo: the CLAUDE.md targets plus whatever citing docs a test needs."""
    files = {"CLAUDE.md": ROOT_FIXTURE}
    for axis in AXIS_DIRS:
        files[f"{axis}/CLAUDE.md"] = AXIS_FIXTURE
    files.update(docs)
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    subprocess.run(
        ["git", "-C", str(tmp_path), "add", "--", *sorted(files)],
        check=True,
    )
    return tmp_path


def _scan(tmp_path: Path, body: str, **kwargs: object) -> resolver.CitationReport:
    repo = _repo(tmp_path, {"doc.md": body})
    known: tuple[resolver.KnownBroken, ...] = kwargs.get("known_broken", ())  # type: ignore[assignment]
    return resolver.scan(repo, known_broken=known)


def _sections(report: resolver.CitationReport, target: str) -> list[str]:
    return [c.section for c in report.citations if target in c.targets]


# --------------------------------------------------------------------------------------
# Shape coverage — every form the tracked corpus actually uses.
# --------------------------------------------------------------------------------------

RESOLVING_SHAPES: tuple[tuple[str, str, str], ...] = (
    ("bare", f"see CLAUDE.md {SIGN}1.1 for detail", "1.1"),
    ("backticked", f"see `CLAUDE.md` {SIGN}12.5 for detail", "12.5"),
    ("relative-root", f"per ./CLAUDE.md {SIGN}1 rules", "1"),
    ("workspace-prefixed", f"per workspace CLAUDE.md {SIGN}12.5.4 rules", "12.5.4"),
    ("compound-word-prefix", f"per root-CLAUDE.md {SIGN}1.1 rules", "1.1"),
    ("table-cell-boundary", f"| `CLAUDE.md` | {SIGN}12.5 | note |", "12.5"),
    ("dash-separated", f"`CLAUDE.md` — {SIGN}1 framing", "1"),
    ("bold-run-on", f"`CLAUDE.md`** {SIGN}12 note", "12"),
    ("parenthetical", f"`CLAUDE.md` (workspace) {SIGN}1.1 note", "1.1"),
    ("word-form", "per root CLAUDE.md section 12.5 rules", "12.5"),
    ("table-row-anchor", f"per `CLAUDE.md` {SIGN}14.2 convention", "14.2"),
)


@pytest.mark.parametrize(
    ("name", "body", "expected"),
    RESOLVING_SHAPES,
    ids=[case[0] for case in RESOLVING_SHAPES],
)
def test_supported_shapes_resolve_against_root(
    tmp_path: Path, name: str, body: str, expected: str
) -> None:
    report = _scan(tmp_path, body)
    assert report.ok, report.findings
    assert _sections(report, "CLAUDE.md") == [expected], name


def test_bold_table_row_labels_are_section_anchors() -> None:
    assert "14.2" in resolver.heading_sections(ROOT_FIXTURE)


def test_emphasis_inside_a_cell_is_not_an_anchor() -> None:
    # The fixture's 14.2 row carries `**bold 99.9 emphasis**` in its SECOND cell. Only a
    # bold label opening the FIRST cell declares a section.
    assert "99.9" not in resolver.heading_sections(ROOT_FIXTURE)


def test_headings_without_a_title_are_not_anchors() -> None:
    assert resolver.heading_sections("## 7.\n\n## 8. Real heading\n") == ("8",)


# --------------------------------------------------------------------------------------
# The gate itself — a cite to a section that does not exist must fail with file:line.
# --------------------------------------------------------------------------------------


def test_nonexistent_section_fails_with_file_and_line(tmp_path: Path) -> None:
    body = f"line one\nsee `CLAUDE.md` {SIGN}99.9 here\n"
    report = _scan(tmp_path, body)
    assert not report.ok
    assert len(report.findings) == 1
    finding = report.findings[0]
    assert (finding.source, finding.line, finding.target, finding.section) == (
        "doc.md",
        2,
        "CLAUDE.md",
        "99.9",
    )
    assert "doc.md:2" in finding.render()
    assert "99.9" in finding.render()


def test_subsection_under_an_existing_section_still_fails(tmp_path: Path) -> None:
    # §12 and §12.5 and §12.5.4 all exist; §12.5.9 does not. Membership is EXACT — a
    # cite is not satisfied by having an existing ancestor section.
    report = _scan(tmp_path, f"`CLAUDE.md` {SIGN}12.5.9")
    assert [f.section for f in report.findings] == ["12.5.9"]


def test_existing_subsection_under_existing_section_passes(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"`CLAUDE.md` {SIGN}12.5.4")
    assert report.ok, report.findings


def test_check_mode_exits_non_zero_on_a_broken_cite(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, {"doc.md": f"`CLAUDE.md` {SIGN}99.9"})
    assert resolver.main(["--root", str(repo), "--check"]) == 1
    assert "BROKEN CITATIONS: 1" in capsys.readouterr().out


def test_check_mode_exits_zero_when_every_cite_resolves(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    repo = _repo(tmp_path, {"doc.md": f"`CLAUDE.md` {SIGN}12.5.4"})
    assert resolver.main(["--root", str(repo), "--check"]) == 0
    assert "BROKEN CITATIONS: 0" in capsys.readouterr().out


# --------------------------------------------------------------------------------------
# Axis attribution — the subtlety the unit exists to get right.
# --------------------------------------------------------------------------------------


def test_axis_prefixed_cite_resolves_against_the_axis_file(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"per `harness-cp/CLAUDE.md` {SIGN}4.1 table")
    assert report.ok, report.findings
    assert _sections(report, "harness-cp/CLAUDE.md") == ["4.1"]


def test_axis_prefixed_cite_does_not_touch_root(tmp_path: Path) -> None:
    # §4.1 exists in the axis file and NOT in the root fixture. If the resolver also
    # attributed the cite to root it would produce a spurious finding.
    report = _scan(tmp_path, f"per `harness-cp/CLAUDE.md` {SIGN}4.1 table")
    assert _sections(report, "CLAUDE.md") == []
    assert report.findings == ()


def test_axis_prefixed_cite_to_a_root_only_section_fails(tmp_path: Path) -> None:
    # §12.5 exists in ROOT but not in the axis file — the axis-prefixed cite must fail,
    # proving attribution is by named file rather than by "does any CLAUDE.md have it".
    report = _scan(tmp_path, f"per `harness-cp/CLAUDE.md` {SIGN}12.5 table")
    assert [(f.target, f.section) for f in report.findings] == [("harness-cp/CLAUDE.md", "12.5")]


def test_brace_expanded_prefix_hits_every_named_axis(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"per `harness-{{cp,od}}/CLAUDE.md` {SIGN}4.1 tables")
    assert report.ok, report.findings
    targets = {t for c in report.citations for t in c.targets}
    assert targets == {"harness-cp/CLAUDE.md", "harness-od/CLAUDE.md"}


def test_glob_prefix_hits_every_matching_axis(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"per `harness-*/CLAUDE.md` {SIGN}4.1 tables")
    assert report.ok, report.findings
    targets = {t for c in report.citations for t in c.targets}
    assert targets == {"harness-cp/CLAUDE.md", "harness-od/CLAUDE.md"}


def test_brace_expansion_is_gated_per_member(tmp_path: Path) -> None:
    repo = _repo(
        tmp_path,
        {
            "doc.md": f"per `harness-{{cp,od}}/CLAUDE.md` {SIGN}4.1",
            "harness-od/CLAUDE.md": "# Axis\n\n## 5. Other\n",
        },
    )
    report = resolver.scan(repo, known_broken=())
    assert [(f.target, f.section) for f in report.findings] == [("harness-od/CLAUDE.md", "4.1")]


def test_unknown_directory_prefix_is_reported_not_gated(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"per `Sibling-spec/CLAUDE.md` {SIGN}25 residual")
    assert report.ok, report.findings
    assert [c.attribution for c in report.citations] == [resolver.Attribution.UNRESOLVABLE]
    assert report.citations[0].targets == ()


def test_external_home_path_is_reported_not_gated(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"per `~/.claude/CLAUDE.md` {SIGN}99 discipline")
    assert report.ok, report.findings
    assert [c.attribution for c in report.citations] == [resolver.Attribution.EXTERNAL]


# --------------------------------------------------------------------------------------
# Gap discipline — what separates a citation from adjacent prose.
# --------------------------------------------------------------------------------------


def test_intervening_filename_breaks_the_anchor(tmp_path: Path) -> None:
    # The section belongs to the artifact named second, not to CLAUDE.md.
    report = _scan(tmp_path, f"`CLAUDE.md` and `Spec_Other_v1.md` {SIGN}99.9")
    assert report.citations == ()
    assert report.ok


def test_multiword_clause_gap_is_not_a_citation(tmp_path: Path) -> None:
    # Live shapes: "`harness-cp/CLAUDE.md` | No direct §7.4.7 cite" and
    # "at harness-od/CLAUDE.md to require §9.1" — both name another artifact's section.
    for body in (
        f"| `harness-cp/CLAUDE.md` | No direct {SIGN}99.9 cite |",
        f"gate at harness-cp/CLAUDE.md to require {SIGN}99.9 only",
    ):
        report = _scan(tmp_path, body)
        assert report.citations == (), body


def test_single_modifier_word_gap_is_still_a_citation(tmp_path: Path) -> None:
    # Live shapes: "`CLAUDE.md` framing (§1 ...", "CLAUDE.md root §1.1", "CLAUDE.md NEW §12.5".
    for body, expected in (
        (f"the workspace `CLAUDE.md` framing ({SIGN}1 project framing)", "1"),
        (f"Workspace CLAUDE.md root {SIGN}1.1 row", "1.1"),
        (f"encoded it in CLAUDE.md NEW {SIGN}12.5", "12.5"),
    ):
        report = _scan(tmp_path, body)
        assert _sections(report, "CLAUDE.md") == [expected], body


def test_gap_is_appositive_unit_table() -> None:
    for gap in ("`", "` | ", "` — ", "` (workspace) ", "`** ", "` (root) | ", " root ", " NEW "):
        assert resolver.gap_is_appositive(gap), gap
    for gap in (" | No direct ", " to require ", " with the ", " row bump + "):
        assert not resolver.gap_is_appositive(gap), gap


def test_distant_section_is_not_captured(tmp_path: Path) -> None:
    # The gap cap keeps a section far down the sentence from being pulled in.
    report = _scan(
        tmp_path,
        f"`CLAUDE.md` is the governance file and elsewhere the spec {SIGN}99.9 applies",
    )
    assert report.citations == ()


# --------------------------------------------------------------------------------------
# Chained sibling sections.
# --------------------------------------------------------------------------------------

CHAIN_CASES: tuple[tuple[str, str, list[str]], ...] = (
    ("plus", f"`CLAUDE.md` {SIGN}1 + {SIGN}12.5", ["1", "12.5"]),
    ("slash", f"`CLAUDE.md` {SIGN}1/{SIGN}12.5", ["1", "12.5"]),
    ("comma", f"`CLAUDE.md` | {SIGN}1, {SIGN}12.5", ["1", "12.5"]),
    ("triple", f"`CLAUDE.md` {SIGN}1 + {SIGN}12 + {SIGN}12.5", ["1", "12", "12.5"]),
)


@pytest.mark.parametrize(
    ("name", "body", "expected"), CHAIN_CASES, ids=[case[0] for case in CHAIN_CASES]
)
def test_chained_sibling_sections_inherit_the_target(
    tmp_path: Path, name: str, body: str, expected: list[str]
) -> None:
    report = _scan(tmp_path, body)
    assert report.ok, report.findings
    assert _sections(report, "CLAUDE.md") == expected, name


def test_chained_sibling_is_gated_too(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"`CLAUDE.md` {SIGN}1 + {SIGN}99.9")
    assert [f.section for f in report.findings] == ["99.9"]


def test_chain_does_not_cross_prose(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"`CLAUDE.md` {SIGN}1, and the other spec {SIGN}99.9")
    assert _sections(report, "CLAUDE.md") == ["1"]
    assert report.ok, report.findings


def test_axis_prefixed_chain_stays_on_the_axis_file(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"`harness-cp/CLAUDE.md` {SIGN}4 + {SIGN}4.1")
    assert report.ok, report.findings
    assert _sections(report, "harness-cp/CLAUDE.md") == ["4", "4.1"]
    assert _sections(report, "CLAUDE.md") == []


# --------------------------------------------------------------------------------------
# Fail-closed behaviour on malformed inputs.
# --------------------------------------------------------------------------------------


def test_anchorless_claude_md_is_fail_closed(tmp_path: Path) -> None:
    repo = _repo(tmp_path, {"harness-cp/CLAUDE.md": "# Axis\n\nNo numbered headings.\n"})
    with pytest.raises(ValueError, match="section anchors"):
        resolver.scan(repo, known_broken=())


def test_missing_root_claude_md_is_fail_closed(tmp_path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "doc.md").write_text("nothing here\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(tmp_path), "add", "--", "doc.md"], check=True)
    with pytest.raises(ValueError, match="no tracked"):
        resolver.scan(tmp_path, known_broken=())


def test_undecodable_file_is_reported_not_silently_dropped(tmp_path: Path) -> None:
    repo = _repo(tmp_path, {"doc.md": f"`CLAUDE.md` {SIGN}1"})
    blob = repo / "payload.bin"
    blob.write_bytes(b"\xff\xfe\x00binary CLAUDE.md")
    subprocess.run(["git", "-C", str(repo), "add", "--", "payload.bin"], check=True)
    report = resolver.scan(repo, known_broken=())
    assert report.skipped_binary == ("payload.bin",)
    assert report.ok, report.findings


# --------------------------------------------------------------------------------------
# The known-broken baseline: enumerated, and self-cleaning.
# --------------------------------------------------------------------------------------

WAIVER = resolver.KnownBroken(
    source="doc.md", target="CLAUDE.md", section="99.9", rationale="fixture"
)


def test_waived_citation_does_not_fail_the_gate(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"`CLAUDE.md` {SIGN}99.9", known_broken=(WAIVER,))
    assert report.ok
    assert report.findings == ()
    assert [f.section for f in report.waived] == ["99.9"]


def test_waiver_survives_a_line_shift(tmp_path: Path) -> None:
    # Waivers are keyed on (file, target, section), so an unrelated edit above the
    # citation must not stale the baseline.
    body = "\n".join(["padding"] * 40 + [f"`CLAUDE.md` {SIGN}99.9"])
    report = _scan(tmp_path, body, known_broken=(WAIVER,))
    assert report.ok
    assert [f.line for f in report.waived] == [41]


def test_stale_waiver_fails_the_gate(tmp_path: Path) -> None:
    # The citation resolves now, so the waiver is dead weight — the gate must say so
    # rather than let the baseline rot into a permanent blind spot.
    report = _scan(tmp_path, f"`CLAUDE.md` {SIGN}12.5", known_broken=(WAIVER,))
    assert report.findings == ()
    assert report.stale_waivers == (WAIVER,)
    assert not report.ok


def test_waiver_does_not_cover_a_different_section(tmp_path: Path) -> None:
    report = _scan(tmp_path, f"`CLAUDE.md` {SIGN}99.9 and {SIGN}88.8", known_broken=(WAIVER,))
    assert [f.section for f in report.findings] == ["88.8"]


def test_waiver_does_not_cover_a_different_file(tmp_path: Path) -> None:
    repo = _repo(tmp_path, {"other.md": f"`CLAUDE.md` {SIGN}99.9"})
    report = resolver.scan(repo, known_broken=(WAIVER,))
    assert [f.source for f in report.findings] == ["other.md"]
    assert report.stale_waivers == (WAIVER,)


def test_shipped_baseline_rows_carry_a_rationale() -> None:
    assert all(entry.rationale.strip() for entry in resolver.KNOWN_BROKEN)


# --------------------------------------------------------------------------------------
# Census derivation (errata E3) and the live HEAD invariant.
# --------------------------------------------------------------------------------------


def test_census_is_derived_not_pinned(tmp_path: Path) -> None:
    body = "\n".join(
        [
            f"`CLAUDE.md` {SIGN}1 + {SIGN}12.5",
            f"`harness-cp/CLAUDE.md` {SIGN}4.1",
            f"`harness-*/CLAUDE.md` {SIGN}4",
        ]
    )
    report = _scan(tmp_path, body)
    assert report.ok, report.findings
    # The census is a projection of the citation list, at any corpus size.
    assert sum(report.census_by_directory().values()) == len(report.citations)
    assert sum(report.census_by_attribution().values()) == len(report.citations)
    # Multi-target cites count once per target, so the by-target census is >= the total.
    assert sum(report.census_by_target().values()) >= len(report.citations)


def test_live_head_citation_corpus_resolves() -> None:
    report = resolver.scan()
    assert report.ok, "\n".join(f.render() for f in report.findings) or report.stale_waivers
    # Non-vacuous: the live corpus is large, and the root file really is cited.
    assert len(report.citations) > 100
    assert report.census_by_target()["CLAUDE.md"] > 100


def test_live_root_heading_set_is_the_superset_arc_5_must_preserve() -> None:
    report = resolver.scan()
    cited = {citation.section for citation in report.citations if "CLAUDE.md" in citation.targets}
    declared = set(report.heading_sets["CLAUDE.md"])
    waived = {entry.section for entry in resolver.KNOWN_BROKEN if entry.target == "CLAUDE.md"}
    assert cited - declared == waived
