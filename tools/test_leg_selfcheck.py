"""Tests for tools/leg_selfcheck.py.

Every check here is tested in BOTH directions — it fires on the defect it was
built for, AND it stays silent on the look-alike that is not a defect. The
one-directional half is the one that matters least: a check that fires on
everything gets muted by its operator within two rounds, which is exactly how a
gate degrades into a rubber stamp. Three of the negative tests below are
REGRESSIONS captured from this tool's own first dogfood run, where it reported
five false count claims and one false label mint against its own arc.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import leg_selfcheck as ls

ROOT = ls.ROOT


def _report_for_counts(by_file: dict[str, list[str]]) -> ls.Report:
    report = ls.Report()
    ls.check_counts(by_file, report)
    return report


def _hard(report: ls.Report) -> list[str]:
    return [f.message for f in report.hard]


# --- diff parsing ------------------------------------------------------------


def test_added_by_file_groups_lines_under_their_own_file():
    diff = (
        "diff --git a/x.md b/x.md\n"
        "--- a/x.md\n"
        "+++ b/x.md\n"
        "@@\n"
        "+alpha\n"
        "-removed\n"
        "diff --git a/y.py b/y.py\n"
        "--- a/y.py\n"
        "+++ b/y.py\n"
        "@@\n"
        "+beta\n"
    )
    assert ls.added_by_file(diff) == {"x.md": ["alpha"], "y.py": ["beta"]}


def test_is_history_path_recognizes_the_archive_carriers():
    assert ls.is_history_path(".harness/roadmap-next-action-archive.md")
    assert ls.is_history_path(".harness/roadmap_drift_log_archive.md")
    assert not ls.is_history_path("design-substrate/Spec_Control_Plane_v1_119.md")


# --- check 1: cite resolution ------------------------------------------------


def test_cite_check_fires_on_a_line_number_past_the_end_of_the_file():
    report = ls.Report()
    ls.check_cites({"spec.md": ["see tools/leg_selfcheck.py:999999 for the guard"]}, report)
    assert any("stale cite" in m for m in _hard(report)), _hard(report)


def test_cite_check_is_silent_on_a_line_number_that_resolves():
    report = ls.Report()
    ls.check_cites({"spec.md": ["see tools/leg_selfcheck.py:1 for the shebang"]}, report)
    assert _hard(report) == []
    assert report.stats["cites_resolved"] == 1


def test_cite_check_resolves_a_range_by_its_end_not_its_start():
    """`file.py:10-999999` is stale even though its START resolves — the range
    end is the claim being made."""
    report = ls.Report()
    ls.check_cites({"spec.md": ["tools/leg_selfcheck.py:10-999999 covers the guard"]}, report)
    assert any("stale cite" in m for m in _hard(report)), _hard(report)


def test_cite_check_treats_an_unresolvable_path_as_advisory_not_hard():
    """Prose and URLs contain `word.md:12` shapes that are not repo cites. Only a
    path that RESOLVES is a claim this tool can judge; guessing would make the
    gate noisy enough to be muted."""
    report = ls.Report()
    ls.check_cites({"spec.md": ["some/other/repo/thing.md:12 is elsewhere"]}, report)
    assert _hard(report) == []
    assert any(f.severity == ls.ADVISORY for f in report.findings)


# --- check 2: count consistency ----------------------------------------------


def test_count_check_fires_when_mirrors_disagree():
    """The B-71 defect: the same noun claimed with different numbers across
    carriers (amendments 3->4->5, ACs 10->14->15->16)."""
    report = _report_for_counts(
        {
            "spec.md": ["U-CP-102 carries 4 carrier amendments."],
            "plan.md": ["U-CP-102 carries FIVE carrier amendments."],
        }
    )
    msgs = _hard(report)
    assert any("carrier amendments" in m and "DIFFERENT" in m for m in msgs), msgs


def test_count_check_does_not_compare_two_different_units_in_a_co_land():
    """[P2] (codex round 2): merging every claim for a noun into ONE repo-wide
    bucket made a legitimate co-land -- "U-CP-102 has 16 acceptance criteria",
    "U-RT-155 has 11" -- a HARD disagreement. That is the exact shape of the B-71
    leg this gate was built for, so it would have false-positived on its own
    motivating arc."""
    report = _report_for_counts(
        {
            "plan_cp.md": ["U-CP-102 = 16 acceptance criteria + 9 mutation probes."],
            "plan_rt.md": ["U-RT-155 = 11 acceptance criteria + 6 mutation probes."],
        }
    )
    assert _hard(report) == [], _hard(report)


def test_count_check_still_compares_unattributed_claims_within_one_file():
    """Unattributed claims are keyed per-FILE, so the preamble-vs-body drift the
    context widening exists for is still caught, without comparing two unrelated
    artifacts' unattributed numbers."""
    same = _report_for_counts({"spec.md": ["It has 3 sites.", "It has 9 sites."]})
    assert _hard(same) != []
    across = _report_for_counts({"a.md": ["It has 3 sites."], "b.md": ["It has 9 sites."]})
    assert _hard(across) == []


def test_count_check_is_silent_when_every_mirror_agrees():
    report = _report_for_counts(
        {
            "spec.md": ["U-CP-102 carries 5 carrier amendments."],
            "plan.md": ["U-CP-102 confirmed: FIVE carrier amendments."],
        }
    )
    assert _hard(report) == []


def test_count_check_does_not_read_a_pr_reference_as_a_count():
    """REGRESSION (first dogfood run): `Post-#935 follow-on refresh` was reported
    as a claim of 935 follow-ons."""
    report = _report_for_counts(
        {
            "notes.md": [
                "Post-#935 follow-on refresh landed.",
                "Post-#1060 follow-on refresh landed.",
            ]
        }
    )
    assert _hard(report) == [], _hard(report)


def test_count_check_does_not_read_a_section_number_as_a_count():
    """REGRESSION (first dogfood run): `§12.2 owed follow-on` was reported as a
    claim of 2 follow-ons, because the `2` after the dot parsed as the number."""
    report = _report_for_counts({"notes.md": ["§12.2 owed follow-on.", "§12.3 owed follow-on."]})
    assert _hard(report) == [], _hard(report)


def test_count_check_skips_archive_files_whose_added_lines_are_relocated_history():
    """REGRESSION (first dogfood run): trimming the drift log re-added seven rows
    of historical prose to the archive, and every count word in that history was
    scanned as though this arc had claimed it."""
    disagreeing = ["U-CP-1 has 3 sites.", "U-CP-1 has 9 sites."]
    assert _hard(_report_for_counts({"spec.md": disagreeing})) != []
    assert _hard(_report_for_counts({".harness/roadmap_drift_log_archive.md": disagreeing})) == []


# --- check 3: § label collision ----------------------------------------------


def _substrate(tmp_path, files: dict[str, str]):
    d = tmp_path / "design-substrate"
    d.mkdir()
    for name, body in files.items():
        (d / name).write_text(body, encoding="utf-8")
    return d


def test_label_check_reports_sibling_versions_as_advisory_not_hard(tmp_path):
    """MEASURED DOWN from hard (codex round 2 [P1]): re-minting every artifact's
    own headings hard-failed 241 of 265 artifacts, because the per-axis specs are
    DELTA chains where a section number legitimately recurs. The check surfaces
    the other users of the label and lets the author judge."""
    d = _substrate(
        tmp_path,
        {
            "Spec_A_v1_32.md": "### §25.17 Existing section\n",
            "Spec_A_v1_119.md": "### §25.17 New meaning\n",
        },
    )
    report = ls.Report()
    ls.check_label_collisions(
        {"design-substrate/Spec_A_v1_119.md": ["### §25.17 New meaning"]}, report, d
    )
    assert _hard(report) == [], "a delta chain recurrence must never BLOCK"
    assert any("sibling" in f.message and "25.17" in f.message for f in report.findings)


def test_label_check_treats_suffixed_labels_as_distinct(tmp_path):
    """MEASURED (31 of 265 firings were this one shape): the CXA chain uses
    `§0.5.refresh` / `§0.5.preserved` / `§0.5.new` as THREE labels; capturing only
    `0.5` reported them as one number reused three times."""
    lines = ["### §0.5.refresh A", "### §0.5.preserved B", "### §0.5.new C"]
    minted = sorted({m.group(1) for line in lines if (m := ls._MINT_RE.match(line))})
    assert minted == ["0.5.new", "0.5.preserved", "0.5.refresh"]


def test_label_check_ignores_a_bolded_prose_reference(tmp_path):
    """MEASURED (the residual 6 of 247): `**§2.2 substantive content preserved
    verbatim...**` is a prose REFERENCE to a section, not a declaration of one."""
    assert ls._MINT_RE.match("### §2.2 Action Surface axis") is not None
    assert ls._MINT_RE.match("**§2.2 substantive content preserved verbatim.**") is None


def test_label_check_ignores_a_bare_cite_which_is_expected_to_already_exist(tmp_path):
    d = _substrate(tmp_path, {"Spec_A_v1_32.md": "### §25.17 Existing\n"})
    report = ls.Report()
    ls.check_label_collisions({"design-substrate/x.md": ["Per §25.17 the rule holds."]}, report, d)
    assert _hard(report) == []
    assert report.stats["labels_minted"] == 0


def test_label_check_does_not_read_a_python_comment_as_a_minted_heading(tmp_path):
    d = _substrate(tmp_path, {"Spec_A.md": "### §12.2.1 Owned elsewhere\n"})
    report = ls.Report()
    ls.check_label_collisions({"tools/x.py": ["    # §12.2.1, enforced not documented"]}, report, d)
    assert report.stats["labels_minted"] == 0
    assert _hard(report) == []


def test_label_check_hard_fails_zero_artifacts_across_the_real_corpus():
    """The precision claim, asserted rather than described: re-minting every real
    design-substrate artifact's own headings must produce NO hard failures."""
    sub = ls.ROOT / "design-substrate"
    if not sub.is_dir():
        import pytest

        pytest.skip("design-substrate not present")
    ls._SIBLING_INDEX_CACHE.clear()
    fired = []
    for f in sorted(sub.glob("*.md")):
        heads = [ln for ln in f.read_text(errors="replace").splitlines() if ls._MINT_RE.match(ln)]
        if not heads:
            continue
        rep = ls.Report()
        ls.check_label_collisions({f"design-substrate/{f.name}": heads}, rep, sub)
        if rep.hard:
            fired.append(f.name)
    assert fired == [], fired


# --- check 4: register row renders its current state -------------------------

_REGISTER_PATHS = [".harness/forward-register.yaml"]


def test_register_check_fires_on_a_row_that_renders_a_heading_only():
    """A row written only into the YAML prints just its heading under `--detail`,
    so the next session reads a title and nothing else and concludes it is
    empty — the exact defect the B-71 leg shipped and review caught."""
    report = ls.Report()
    ls.check_register_rows(
        ["- id: B-999"],
        _REGISTER_PATHS,
        report,
        detail_fn=lambda rid: (0, "### B-999 · a title and nothing else\n"),
    )
    msgs = _hard(report)
    assert any("HEADING ONLY" in m for m in msgs), msgs


def _real_shaped_detail(prose: str, *, rid: str = "B-999", status: str = "registered_finding"):
    """Reproduce the SHAPE `forward_register --detail` actually emits: a canonical
    close_out header, the delimiter, then the prose block. Every other fake in this
    file predates that header and omits the delimiter, so they exercise the
    compatibility fallback rather than the runtime path -- these two tests are the
    ones that witness the real shape (B-235)."""
    header = (
        f"{rid} — {status}\n"
        f"close_out (CANONICAL — /x/forward-register.yaml):\n"
        f"  OPEN — the canonical disposition.\n\n"
        f"{ls.PROSE_DELIMITER}\n\n"
    )
    return lambda _rid: (0, header + prose)


def test_yaml_only_row_still_fires_through_the_real_detail_shape():
    """B-235 regression. The canonical header made `--detail` output non-empty for a
    row with NO prose body, so a naive `body` computation would make `not body`
    unreachable and RETIRE this gate silently -- a gate that stops firing without
    saying so. Feed the real shape and prove it still fires."""
    report = ls.Report()
    ls.check_register_rows(
        ["- id: B-999"],
        _REGISTER_PATHS,
        report,
        detail_fn=_real_shaped_detail("### B-999 · a title and nothing else\n"),
    )
    msgs = _hard(report)
    assert any("HEADING ONLY" in m for m in msgs), msgs


def test_a_close_out_containing_the_delimiter_cannot_spoof_the_prose_frame():
    """codex r1 [P2]. A SUBSTRING split lets row CONTENT choose the framing: a close_out
    carrying the delimiter text would split inside the canonical header, drag its own
    remaining lines into the prose half, and a genuinely heading-only row would stop
    reporting HEADING ONLY. The CLI indents every close_out line by two spaces, so the
    frame is an exact UNINDENTED line and content cannot forge it."""
    spoof_header = (
        "B-999 — registered_finding\n"
        "close_out (CANONICAL — /x/forward-register.yaml):\n"
        f"  {ls.PROSE_DELIMITER}\n"
        "  - **Current state.** Text that would masquerade as a prose body.\n\n"
        f"{ls.PROSE_DELIMITER}\n\n"
    )
    report = ls.Report()
    ls.check_register_rows(
        ["- id: B-999"],
        _REGISTER_PATHS,
        report,
        # The real prose block is heading-only -- the defect the gate must still catch.
        detail_fn=lambda _rid: (0, spoof_header + "### B-999 · a title and nothing else\n"),
    )
    msgs = _hard(report)
    assert any("HEADING ONLY" in m for m in msgs), msgs


def test_new_row_lead_check_reads_the_prose_lead_not_the_canonical_header():
    """The same header would otherwise become `body[0]`, so every NEW row would
    hard-fail with the header text as its 'lead'. The lead judged must be the
    PROSE's first bullet."""
    report = ls.Report()
    ls.check_register_rows(
        ["- id: B-999"],
        _REGISTER_PATHS,
        report,
        detail_fn=_real_shaped_detail("### B-999 · t\n\n- **Close-out steps** run the thing.\n"),
        register_added={
            ".harness/post-phase-8-forward-register.md": ["### B-999 · t"],
            ".harness/forward-register.yaml": ["- id: B-999"],
        },
        base_ids=set(),
    )
    msgs = _hard(report)
    # Discriminating assertion: the REPORTED lead must quote the prose bullet. Asserting
    # only that "LEADS with" appears was vacuous -- the canonical header also fails the
    # accepted-lead pattern, so the check fired either way and the mutation did not kill
    # it (mutation-probe non-kill is a finding, not a pass).
    assert any("Close-out steps" in m for m in msgs), msgs
    assert not any("registered_finding" in m for m in msgs), msgs


def test_register_check_is_silent_and_prints_the_lead_when_a_prose_body_exists():
    """The current-state-first half is genuinely non-mechanical, so the leading
    bullet is surfaced for a human instead of pattern-matched into a fake pass."""
    report = ls.Report()
    ls.check_register_rows(
        ["- id: B-999"],
        _REGISTER_PATHS,
        report,
        detail_fn=lambda rid: (0, "### B-999 · title\n\n- **What it is.** The current state.\n"),
    )
    assert _hard(report) == []
    assert any("The current state." in f.message for f in report.findings)


def test_register_check_fires_when_detail_exits_nonzero():
    report = ls.Report()
    ls.check_register_rows(["- id: B-999"], _REGISTER_PATHS, report, detail_fn=lambda rid: (1, ""))
    assert any("exited 1" in m for m in _hard(report)), _hard(report)


def test_register_check_does_not_run_when_no_register_file_was_touched():
    report = ls.Report()
    ls.check_register_rows(["- id: B-999"], ["harness-cp/src/x.py"], report, detail_fn=None)
    assert report.findings == []


# --- the real repo -----------------------------------------------------------


def test_the_live_forward_register_rows_this_arc_touched_render_a_prose_body():
    """Runs check 4 against the REAL register via the real CLI — the concrete
    guard that B-166 (this arc's own row) is not a YAML-only row."""
    report = ls.Report()
    # uncommitted=True: this test deliberately renders the WORKING TREE prose, so
    # it opts out of the committed-mode dirty-carrier fail-close (round 11 [P2]).
    ls.check_register_rows(["- id: B-166"], _REGISTER_PATHS, report, uncommitted=True)
    assert _hard(report) == [], _hard(report)


def test_count_check_skips_source_files_so_it_cannot_read_its_own_fixtures():
    """REGRESSION (first COMMITTED-branch dogfood run): this file's own
    deliberate disagreement fixtures ("It has 3 sites." / "It has 9 sites.")
    were scanned as real claims. Every carrier that drifted on the B-71 leg was
    a prose artifact or the register YAML — a count mirror never lives in
    source, so source is out of scope."""
    disagreeing = ["U-CP-1 has 3 sites.", "U-CP-1 has 9 sites."]
    assert _hard(_report_for_counts({"design-substrate/Spec_A.md": disagreeing})) != []
    assert _hard(_report_for_counts({"tools/test_leg_selfcheck.py": disagreeing})) == []
    assert _hard(_report_for_counts({"harness-cp/src/x.py": disagreeing})) == []


def test_every_content_check_skips_fixture_files():
    """REGRESSION (second committed-branch dogfood run): the cite check read
    THIS file's deliberately-stale `tools/leg_selfcheck.py:999999` fixture as a
    real stale cite. A checker that scans the repo for invalid shapes will
    always find them in the tests that exercise it."""
    assert ls.is_fixture_path("tools/test_leg_selfcheck.py")
    assert ls.is_fixture_path("harness-cp/tests/test_workflow_driver.py")
    assert not ls.is_fixture_path("design-substrate/Spec_Control_Plane_v1_119.md")
    assert not ls.is_fixture_path("tools/leg_selfcheck.py")

    stale = ["tools/leg_selfcheck.py:999999 is stale"]
    fired = ls.Report()
    ls.check_cites({"design-substrate/Spec_A.md": stale}, fired)
    assert _hard(fired) != []
    silent = ls.Report()
    ls.check_cites({"tools/test_leg_selfcheck.py": stale}, silent)
    assert _hard(silent) == []


def test_resolve_base_refuses_a_ref_that_does_not_resolve():
    """A gate that cannot find its base must NOT report success. `git diff
    <bad-ref>...HEAD` prints nothing to stdout, so an unvalidated base produced
    an empty diff, zero findings and a cheerful `leg-selfcheck OK` — a rubber
    stamp produced by a typo. Found by out-of-family review probing the tool."""
    import pytest

    with pytest.raises(ls.BaseRefError, match="does not resolve"):
        ls.resolve_base("refs/heads/definitely-not-a-ref")


def test_resolve_base_accepts_a_ref_that_does_resolve():
    assert ls.resolve_base("HEAD") == "HEAD"


def test_cli_exits_2_on_an_unresolvable_base(capsys):
    rc = ls.main(["--base", "refs/heads/definitely-not-a-ref"])
    assert rc == 2
    assert "does not resolve" in capsys.readouterr().err


# --- out-of-family review round 1: the two [P1] scope gaps -------------------


def test_count_check_sees_an_unchanged_mirror_in_the_diff_context():
    """[P1] (codex round 1): scanning ADDED lines only meant a single edited
    mirror never disagreed with itself, so a plan newly claiming 15 ACs passed
    while an UNCHANGED mirror two lines up still said 16. Diff context is the
    unchanged text around each edit — the cheapest sound widening."""
    added = {"design-substrate/Plan_A.md": ["U-CP-102 now has 15 acceptance criteria."]}
    ctx = {"design-substrate/Plan_A.md": ["Preamble: U-CP-102 has 16 acceptance criteria."]}

    without = ls.Report()
    ls.check_counts(added, without)
    assert _hard(without) == [], "precondition: added-lines-only cannot see it"

    with_ctx = ls.Report()
    ls.check_counts(added, with_ctx, ctx)
    assert any("acceptance criteria" in m for m in _hard(with_ctx)), _hard(with_ctx)


def test_context_by_file_collects_only_unchanged_lines():
    diff = "--- a/x.md\n+++ b/x.md\n@@\n unchanged context\n+added\n-removed\n"
    assert ls.context_by_file(diff) == {"x.md": ["unchanged context"]}
    assert ls.added_by_file(diff) == {"x.md": ["added"]}


def test_register_check_hard_fails_a_new_row_with_no_current_state_bullet():
    """[P1] (codex round 1): a body-but-superseded lead exited successfully.
    Made structural for NEW rows, which is the half that IS mechanizable."""
    report = ls.Report()
    ls.check_register_rows(
        ["### B-999 · a brand new row"],
        _REGISTER_PATHS,
        report,
        detail_fn=lambda rid: (0, "### B-999 · t\n\n- **What it is.** Only background.\n"),
        register_added={
            ".harness/post-phase-8-forward-register.md": ["### B-999 · a brand new row"]
        },
    )
    assert any("no `- **Current state.**` bullet" in m for m in _hard(report)), _hard(report)


def test_register_check_accepts_a_new_row_that_states_current_state():
    report = ls.Report()
    ls.check_register_rows(
        ["### B-999 · a brand new row"],
        _REGISTER_PATHS,
        report,
        detail_fn=lambda rid: (
            0,
            "### B-999 · t\n\n- **What it is.** Background.\n\n- **Current state.** Registered.\n",
        ),
        register_added={
            ".harness/post-phase-8-forward-register.md": ["### B-999 · a brand new row"]
        },
    )
    assert _hard(report) == [], _hard(report)


def test_register_check_does_not_impose_the_bullet_on_a_legacy_row():
    """Only 35 of 165 existing rows carry the bullet. A corpus-wide hard
    requirement would red 130 legitimate legacy rows and get the gate muted, so
    an AMENDED (not newly-added) row stays advisory."""
    report = ls.Report()
    ls.check_register_rows(
        ["- id: B-100"],  # a YAML-only touch: amending, not adding the prose block
        _REGISTER_PATHS,
        report,
        detail_fn=lambda rid: (0, "### B-100 · t\n\n- **What it is.** Legacy shape.\n"),
    )
    assert _hard(report) == []
    assert any(f.severity == ls.ADVISORY for f in report.findings)


# --- out-of-family review round 3 -------------------------------------------


def test_count_check_binds_each_match_to_its_nearest_unit_on_a_multi_unit_line():
    """[P1] (codex round 3): taking the line's FIRST unit id attributed every
    count on a multi-unit line to one subject, so a single summary sentence —
    exactly the shape the upcoming U-CP-102 + U-RT-155 co-land uses — became two
    conflicting claims for U-CP-102 and hard-failed the pre-push gate."""
    line = "U-CP-102 = 16 acceptance criteria + 9 probes; U-RT-155 = 11 acceptance criteria."
    report = _report_for_counts({"plan.md": [line]})
    assert _hard(report) == [], _hard(report)
    assert ls._claim_subject(line, "plan.md", line.index("16")) == "U-CP-102"
    assert ls._claim_subject(line, "plan.md", line.index("11")) == "U-RT-155"


def test_count_check_still_fires_for_one_unit_claimed_twice_on_one_line():
    line = "U-CP-102 has 16 acceptance criteria, but U-CP-102 has 15 acceptance criteria."
    assert _hard(_report_for_counts({"plan.md": [line]})) != []


def test_changed_line_numbers_tracks_new_file_positions():
    diff = "--- a/x.md\n+++ b/x.md\n@@ -10,3 +10,4 @@\n ctx\n+added-at-11\n ctx\n"
    assert ls.changed_line_numbers(diff) == {"x.md": {11}}


def test_run_checked_fails_closed_on_a_failing_git_invocation():
    """[P2] (codex round 3): _run discarded the return code, so a base that
    RESOLVES but whose diff still fails (two commits with no merge base) yielded
    an empty diff and a cheerful OK. Same family as the round-1 base fail-open."""
    import pytest

    with pytest.raises(ls.BaseRefError, match="failed"):
        ls._run_checked(["git", "diff", "definitely-not-a-ref...also-not-a-ref"])


def test_new_row_rules_apply_only_to_register_prose_additions():
    """[P2] (codex round 4): a `### B-*` heading added in ANY markdown artifact
    (a fork doc, say) landed in new_ids from the flattened added list, imposing
    new-row requirements on it and calling --detail for an id that may not be in
    the register at all."""
    report = ls.Report()
    ls.check_register_rows(
        ["### B-500 · a heading in a FORK DOC, not the register"],
        _REGISTER_PATHS,
        report,
        detail_fn=lambda rid: (0, "### B-500 · t\n\n- **What it is.** Background only.\n"),
        register_added={
            ".harness/class_2_fork_something.md": [
                "### B-500 · a heading in a FORK DOC, not the register"
            ]
        },
    )
    assert _hard(report) == [], _hard(report)


def test_untracked_files_are_scanned_in_uncommitted_mode():
    """[P2] (codex round 4): `git diff HEAD` omits untracked files, so a leg that
    CREATES an artifact and runs the pre-commit mode saw zero changed files and
    skipped every check — and a brand-new artifact is exactly where a fresh stale
    cite or minted label lives."""
    tracked_only = ls.untracked_added(False)
    assert tracked_only == {}
    listing = ls.untracked_added(True)
    assert isinstance(listing, dict)
    for rel, lines in listing.items():
        assert isinstance(rel, str) and isinstance(lines, list)


def test_changed_line_numbers_records_deletion_only_edits():
    """[P2] (codex round 5): a deletion advances no new-file position, so a
    deletion-only edit recorded nothing, `amended` stayed empty, and --detail was
    never called — allowing the exact heading-only regression this gate blocks
    (delete a row's final prose body and nothing notices)."""
    diff = "--- a/x.md\n+++ b/x.md\n@@ -10,3 +10,2 @@\n ctx\n-removed-body-line\n ctx\n"
    # Widened at round 7 to include the position BEFORE the deletion, so a row's
    # LAST body line still attributes to that row rather than the next heading.
    assert ls.changed_line_numbers(diff) == {"x.md": {10, 11}}
    # ...and the added-lines view is still empty, which is why it could not see it
    assert ls.added_by_file(diff) == {"x.md": []}


# --- out-of-family review round 6 -------------------------------------------


def test_cite_check_validates_every_line_in_a_list_form_cite():
    """[P2] (codex round 6): the repo writes `file.py:6,10,47,51` and
    `file.py:119/121/122`. Capturing only the FIRST number let a stale later
    location pass unseen."""
    report = ls.Report()
    ls.check_cites({"spec.md": ["tools/leg_selfcheck.py:1,2,999999 covers it"]}, report)
    hard = _hard(report)
    assert any("999999" in m and "past end-of-file" in m for m in hard), hard

    clean = ls.Report()
    ls.check_cites({"spec.md": ["tools/leg_selfcheck.py:1/2/3 covers it"]}, clean)
    assert _hard(clean) == []


def test_cite_check_resolves_a_sibling_relative_path():
    """[P2] (codex round 6): a design-substrate file citing a SIBLING by bare
    name resolved at the repo root only, so an existing file was downgraded to
    'unresolvable' (advisory) and its stale line number passed."""
    report = ls.Report()
    ls.check_cites({"tools/spec.md": ["see leg_selfcheck.py:999999"]}, report)
    assert any("past end-of-file" in m for m in _hard(report)), report.findings


def test_count_check_refuses_to_guess_on_a_multi_unit_line():
    """[P2] (codex round 6): 'U-CP-102 = 16 ... U-RT-155 = 11' wants
    nearest-PRECEDING; '16 ... for U-CP-102; 11 ... for U-RT-155' wants
    nearest-FOLLOWING. Two successive heuristics each produced a FALSE hard
    disagreement on the other shape, so an ambiguous line is now SKIPPED and
    said to be skipped. For a gate that blocks pushes, silence beats a
    confident wrong answer."""
    for line in (
        "U-CP-102 = 16 acceptance criteria; U-RT-155 = 11 acceptance criteria.",
        "16 acceptance criteria for U-CP-102; 11 acceptance criteria for U-RT-155.",
    ):
        report = _report_for_counts({"plan.md": [line]})
        assert _hard(report) == [], (line, _hard(report))
        assert any("unattributable" in f.message for f in report.findings), line


def test_count_check_still_fires_on_a_single_unit_line():
    line = "U-CP-102 has 16 acceptance criteria, but U-CP-102 has 15 acceptance criteria."
    assert _hard(_report_for_counts({"plan.md": [line]})) != []


def test_register_newness_is_judged_against_the_base_not_the_added_lines():
    """[P2] (codex round 6): correcting an EXISTING row's title re-adds its
    `### B-*` line, which classified a legacy row as new and hard-failed it for
    lacking the newly required Current-state bullet."""
    report = ls.Report()
    ls.check_register_rows(
        ["### B-100 · a CORRECTED title for a legacy row"],
        _REGISTER_PATHS,
        report,
        detail_fn=lambda rid: (0, "### B-100 · t\n\n- **What it is.** Legacy shape.\n"),
        register_added={
            ".harness/post-phase-8-forward-register.md": [
                "### B-100 · a CORRECTED title for a legacy row"
            ]
        },
        base_ids={"B-100"},  # already existed at the base => NOT new
    )
    assert _hard(report) == [], _hard(report)


def test_register_newness_still_flags_a_genuinely_new_row():
    report = ls.Report()
    ls.check_register_rows(
        ["### B-999 · genuinely new"],
        _REGISTER_PATHS,
        report,
        detail_fn=lambda rid: (0, "### B-999 · t\n\n- **What it is.** Only background.\n"),
        register_added={".harness/post-phase-8-forward-register.md": ["### B-999 · genuinely new"]},
        base_ids={"B-100"},
    )
    assert any("Current state" in m for m in _hard(report)), _hard(report)


def test_boundary_deletion_attributes_to_the_row_being_emptied():
    """[P2] (codex round 7) — a fail-open in the ROUND-5 fix: when the removed
    line was a row's LAST body line, the new-file position is already the NEXT
    row's heading, so attributing only that position made rows_enclosing pick the
    FOLLOWING row and the emptied row was never checked — green on precisely the
    heading-only regression this gate exists to block."""
    diff = (
        "--- a/.harness/post-phase-8-forward-register.md\n"
        "+++ b/.harness/post-phase-8-forward-register.md\n"
        "@@ -10,3 +10,2 @@\n"
        " last body line of row A\n"
        "-the ONLY remaining body line\n"
        " ### B-999 · next row heading\n"
    )
    nums = ls.changed_line_numbers(diff)[".harness/post-phase-8-forward-register.md"]
    # both the boundary position AND the one before it, so the emptied row resolves
    assert 11 in nums and 10 in nums, nums


# --- out-of-family review round 8 -------------------------------------------


def test_cite_check_rejects_line_zero():
    """[P2] (codex round 8): `n > total` alone accepted `file.py:0` as resolved.
    Line 0 never exists, so a placeholder or zero-based cite failed open."""
    report = ls.Report()
    ls.check_cites({"spec.md": ["tools/leg_selfcheck.py:0 is a placeholder"]}, report)
    assert any("not valid" in m for m in _hard(report)), report.findings


def test_cite_dedup_key_includes_the_citing_source(tmp_path, monkeypatch):
    """[P2] (codex round 8): resolution is source-relative, so two documents in
    DIFFERENT directories citing the same sibling shorthand are different claims.
    A (rel, spec) key collapsed them and skipped the second — stale, and green."""
    monkeypatch.setattr(ls, "ROOT", tmp_path)
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "SIB.md").write_text("\n".join(f"line {i}" for i in range(1, 51)))
    (tmp_path / "b" / "SIB.md").write_text("only one line")
    report = ls.Report()
    ls.check_cites({"a/doc.md": ["see SIB.md:50"], "b/doc.md": ["see SIB.md:50"]}, report)
    assert any("b/SIB.md" in m or "SIB.md" in m for m in _hard(report)), report.findings


def test_sibling_label_index_is_built_once_per_family_set(tmp_path):
    """[P2] (codex round 8): the old code re-globbed the directory AND re-read
    every artifact once per MINTED LABEL — quadratic in production, not only in
    the corpus test that measured it at 45s."""
    d = _substrate(tmp_path, {"Spec_A_v1.md": "### §1.1 A\n### §1.2 B\n### §1.3 C\n"})
    ls._SIBLING_INDEX_CACHE.clear()
    first = ls._sibling_label_index(d, frozenset({"spec_a"}))
    second = ls._sibling_label_index(d, frozenset({"spec_a"}))
    assert first is second, "the index must be memoised, not rebuilt"
    assert set(first) == {"1.1", "1.2", "1.3"}


def test_a_specific_noun_is_not_also_counted_in_its_generic_bucket():
    """[P2] (codex round 9): the intervening-word matcher let `amendments?`
    swallow "3 carrier amendments" (it consumes "carrier"), so 3 landed in the
    GENERIC bucket and collided with a perfectly consistent "5 amendments"
    total — a HARD block on valid prose."""
    report = _report_for_counts(
        {"spec.md": ["U-CP-1 has 3 carrier amendments out of 5 amendments total."]}
    )
    assert _hard(report) == [], _hard(report)


def test_a_genuine_generic_disagreement_still_fires():
    report = _report_for_counts(
        {"spec.md": ["U-CP-1 has 5 amendments.", "U-CP-1 has 7 amendments."]}
    )
    assert _hard(report) != []


# --- out-of-family review round 10 ------------------------------------------


def test_count_subjects_separate_by_enclosing_row_in_an_aggregate_file():
    """[P2] (codex round 10): the whole-FILE fallback collapsed unrelated rows in
    an aggregate carrier — two register rows added in one round, each
    legitimately claiming a different count, shared one subject and HARD-blocked
    the push."""
    report = _report_for_counts(
        {
            ".harness/post-phase-8-forward-register.md": [
                "### B-900 · first row",
                "- **What it is.** It touches 3 sites.",
                "### B-901 · second row",
                "- **What it is.** It touches 4 sites.",
            ]
        }
    )
    assert _hard(report) == [], _hard(report)


def test_count_subjects_still_disagree_within_one_enclosing_row():
    report = _report_for_counts(
        {
            ".harness/post-phase-8-forward-register.md": [
                "### B-900 · one row",
                "- **What it is.** It touches 3 sites.",
                "- **Current state.** It touches 4 sites.",
            ]
        }
    )
    assert _hard(report) != []


def test_minted_labels_are_queried_only_within_their_own_family(tmp_path):
    """[P2] (codex round 10): unioning every changed family let a label minted
    only in a CP artifact be queried against Runtime siblings merely because a
    Runtime file was also touched — cross-family noise contradicting the family
    isolation this check is built on."""
    d = _substrate(
        tmp_path,
        {
            "Spec_Runtime_v1_1.md": "### §9.9 Runtime meaning\n",
            "Spec_Runtime_v1_2.md": "### §9.9 Runtime meaning again\n",
            "Spec_CP_v1_1.md": "### §9.9 CP meaning\n",
        },
    )
    ls._SIBLING_INDEX_CACHE.clear()
    report = ls.Report()
    # A CP label minted while a Runtime file is ALSO in the diff.
    ls.check_label_collisions(
        {
            "design-substrate/Spec_CP_v1_1.md": ["### §9.9 CP meaning"],
            "design-substrate/Spec_Runtime_v1_2.md": ["some unrelated edit"],
        },
        report,
        d,
    )
    sibling_msgs = [f.message for f in report.findings if "sibling" in f.message]
    assert not any("Runtime" in m for m in sibling_msgs), sibling_msgs


# --- out-of-family review round 11 ------------------------------------------


def test_body_only_edits_to_two_rows_resolve_to_their_own_rows(tmp_path, monkeypatch):
    """[P2] (codex round 11): two EXISTING register rows given body-only edits
    contribute no heading to the added set, so both rows' claims collapsed onto
    one `(unattributed in file)` subject and HARD-blocked perfectly valid
    per-row counts."""
    monkeypatch.setattr(ls, "ROOT", tmp_path)
    reg = tmp_path / ".harness"
    reg.mkdir()
    f = reg / "post-phase-8-forward-register.md"
    f.write_text(
        "### B-900 · first\n"
        "- **What it is.** It touches 3 sites.\n"
        "### B-901 · second\n"
        "- **What it is.** It touches 9 sites.\n"
    )
    added = {
        ".harness/post-phase-8-forward-register.md": [
            "- **What it is.** It touches 3 sites.",
            "- **What it is.** It touches 9 sites.",
        ]
    }
    positions = {
        ".harness/post-phase-8-forward-register.md": [
            (2, added[".harness/post-phase-8-forward-register.md"][0]),
            (4, added[".harness/post-phase-8-forward-register.md"][1]),
        ]
    }
    report = ls.Report()
    ls.check_counts(added, report, None, positions)
    assert _hard(report) == [], _hard(report)


def test_enclosing_row_at_resolves_by_position(tmp_path, monkeypatch):
    monkeypatch.setattr(ls, "ROOT", tmp_path)
    d = tmp_path / ".harness"
    d.mkdir()
    (d / "x.md").write_text("### B-900 · first\nbody\n### B-901 · second\nbody\n")
    assert ls.enclosing_row_at(".harness/x.md", 2) == "B-900"
    assert ls.enclosing_row_at(".harness/x.md", 4) == "B-901"


# --- out-of-family review round 13 ------------------------------------------


def test_committed_mode_does_not_resolve_a_cite_from_an_untracked_file(tmp_path, monkeypatch):
    """[P2] (codex round 13): a committed line citing a file that exists only as
    untracked WIP reported 'resolved' while the push omits its target entirely.
    Working-tree fallback belongs to --uncommitted alone."""
    monkeypatch.setattr(ls, "ROOT", tmp_path)
    (tmp_path / "ghost.md").write_text("one\ntwo\n")
    report = ls.Report()
    ls.check_cites({"spec.md": ["see ghost.md:2"]}, report, committed_ref="HEAD")
    # absent at HEAD => unresolved (advisory), never a silent pass
    assert _hard(report) == []
    assert any(
        "unreadable" in f.message or "does not resolve" in f.message for f in report.findings
    ), report.findings


def test_duplicate_context_positions_are_consumed_in_order(tmp_path, monkeypatch):
    """[P2] (codex round 13): a {text: line} map kept only the LAST occurrence,
    so identical text repeated in a later row attributed an earlier row's claim
    to that later row and HID a real disagreement."""
    monkeypatch.setattr(ls, "ROOT", tmp_path)
    d = tmp_path / ".harness"
    d.mkdir()
    f = d / "post-phase-8-forward-register.md"
    f.write_text(
        "### B-900 · first\n"
        "It touches 3 sites.\n"
        "It touches 4 sites.\n"
        "### B-901 · second\n"
        "It touches 3 sites.\n"
    )
    added = {
        ".harness/post-phase-8-forward-register.md": [
            "It touches 3 sites.",
            "It touches 4 sites.",
        ]
    }
    positions = {
        ".harness/post-phase-8-forward-register.md": [
            (2, "It touches 3 sites."),
            (3, "It touches 4 sites."),
            (5, "It touches 3 sites."),
        ]
    }
    report = ls.Report()
    ls.check_counts(added, report, None, positions)
    # both claims belong to B-900 and genuinely disagree — it must NOT be hidden
    assert _hard(report) != [], report.findings


def test_cite_to_a_path_this_diff_deletes_is_a_hard_finding():
    """[P2] (codex round 14): a branch that deletes a file while adding a cite to
    its old path emitted only an advisory, so the gate exited green on an
    unambiguously stale repository citation."""
    report = ls.Report()
    ls.check_cites({"spec.md": ["see tools/gone.py:12"]}, report, removed={"tools/gone.py"})
    assert any("DELETES" in m for m in _hard(report)), report.findings


def test_deleted_paths_parses_dev_null_targets():
    diff = "--- a/tools/gone.py\n+++ /dev/null\n@@ -1 +0,0 @@\n-x\n"
    assert ls.deleted_paths(diff) == {"tools/gone.py"}


def test_a_fully_deleted_register_row_is_still_checked():
    """[P2] (codex round 14): when an entire prose row is deleted, its id appears
    in no added line and rows_enclosing (reading the post-deletion file) resolves
    to an ADJACENT row — so the now heading-only row was never re-checked."""
    diff = (
        "--- a/.harness/post-phase-8-forward-register.md\n"
        "+++ b/.harness/post-phase-8-forward-register.md\n"
        "@@ -10,3 +10,1 @@\n"
        " keep\n"
        "-### B-777 · a row being removed\n"
        "-- **What it is.** body\n"
    )
    ls._DELETED_ROW_IDS.clear()
    ls.changed_line_numbers(diff)
    assert "B-777" in ls._DELETED_ROW_IDS


# --- B-167 step 1: the format-scoped acceptance-criteria recount ---------------
#
# Both directions, per this module's own discipline: the recount returns a number
# where it is exact, and returns None -- never a wrong number, and never 0 -- on
# every shape observed in the real plan corpus where it is not.


def test_recount_returns_the_count_for_a_fresh_contiguous_enumeration() -> None:
    block = (
        "### U-XX-01 — a unit\n\n"
        "**Acceptance criteria:**\n\n"
        "1. first\n2. second\n3. third\n\n"
        "**Tests:** whatever\n"
    )
    assert ls.derive_acceptance_criteria_count(block) == 3


def test_recount_stops_at_the_next_bold_section_rather_than_running_on() -> None:
    """A numbered list in a LATER section must not inflate the count."""
    block = (
        "**Acceptance criteria:**\n\n"
        "1. first\n2. second\n\n"
        "**Mutation-probe obligations:**\n\n"
        "1. a probe\n2. another\n3. a third\n"
    )
    assert ls.derive_acceptance_criteria_count(block) == 2


def test_recount_refuses_an_amendment_block_that_renumbers_into_a_parent_unit() -> None:
    """The real shape that made claims-vs-claims the sound ceiling.

    `Implementation_Plan_Control_Plane_v2_41.md`'s U-CP-45 amendment carries
    `**Acceptance criteria (v2.41 additions):**` and a list starting at `0` — its
    numbers index the PARENT unit's criteria, in another file. Recounting it would
    produce a confident wrong answer.
    """
    block = "**Acceptance criteria (v2.41 additions):**\n\n0. an addition keyed to the parent\n"
    assert ls.derive_acceptance_criteria_count(block) is None


def test_recount_refuses_any_parenthetically_qualified_header() -> None:
    for qualifier in (
        "(v2.4 amendment):",
        "(v2.39 additions):",
        "(v2.12 delta — growth only):",
    ):
        block = f"**Acceptance criteria {qualifier}**\n\n1. one\n2. two\n"
        assert ls.derive_acceptance_criteria_count(block) is None, qualifier


def test_recount_refuses_a_list_that_does_not_start_at_one() -> None:
    assert (
        ls.derive_acceptance_criteria_count("**Acceptance criteria:**\n\n0. zero\n1. one\n") is None
    )


def test_recount_refuses_a_list_with_a_gap() -> None:
    assert (
        ls.derive_acceptance_criteria_count("**Acceptance criteria:**\n\n1. one\n3. three\n")
        is None
    )


def test_recount_returns_none_not_zero_when_there_is_no_list() -> None:
    """`None` and `0` must stay distinguishable — a caller reporting a
    disagreement against a missing list is the false-positive class that gets a
    gate muted."""
    assert (
        ls.derive_acceptance_criteria_count("**Acceptance criteria:**\n\nprose only, no list\n")
        is None
    )


def test_recount_returns_none_when_the_block_has_no_acceptance_criteria_section() -> None:
    assert ls.derive_acceptance_criteria_count("### U-XX-02 — a unit\n\n**Files:** none\n") is None


def test_recount_is_exact_on_the_real_u_cp_102_block() -> None:
    """The unit `B-167` was registered against, recounted from the shipped artifact.

    16 criteria, independently corroborated inside the same block by the
    mutation-probe line's highest referenced index (16).
    """
    plan = ROOT / "design-substrate" / "Implementation_Plan_Control_Plane_v2_53.md"
    if not plan.exists():  # pragma: no cover - corpus moved
        return
    text = plan.read_text(encoding="utf-8")
    start = text.find("### §0.2 U-CP-102")
    assert start >= 0, "U-CP-102 block moved — re-ground B-167 step 1"
    end = text.find("### ", start + 10)
    block = text[start:end] if end > start else text[start:]
    assert ls.derive_acceptance_criteria_count(block) == 16


def test_recount_refuses_a_mixed_numbered_and_bulleted_section() -> None:
    """A numbered list PLUS top-level bullets is not exactly countable.

    Counting the numbered items alone yields a confidently INCOMPLETE ground
    truth, which is worse than declining. Regression from out-of-family review:
    an earlier draft returned 4 for `U-RT-138` (4 numbered + 1 bullet) and 6 for
    `U-RT-141` (6 + 2).
    """
    block = "**Acceptance criteria:**\n\n1. one\n2. two\n\n- a bullet criterion\n"
    assert ls.derive_acceptance_criteria_count(block) is None


def test_recount_refuses_the_real_mixed_blocks_from_the_corpus() -> None:
    """The two shapes review named, read from the shipped artifacts."""
    import re as _re

    for name, unit in (
        ("Implementation_Plan_Harness_Runtime_v2_49.md", "U-RT-138"),
        ("Implementation_Plan_Harness_Runtime_v2_50.md", "U-RT-141"),
    ):
        plan = ROOT / "design-substrate" / name
        if not plan.exists():  # pragma: no cover - corpus moved
            continue
        text = plan.read_text(encoding="utf-8")
        heads = list(_re.finditer(r"^#+.*\bU-[A-Z]+-\d+\b.*$", text, _re.M))
        for k, h in enumerate(heads):
            if unit in h.group(0):
                end = heads[k + 1].start() if k + 1 < len(heads) else len(text)
                assert ls.derive_acceptance_criteria_count(text[h.start() : end]) is None, unit
                break


def test_mutation_probe_recount_reads_the_obligations_line() -> None:
    block = "**Mutation-probe obligations (PD-9).** Criteria 4, 6, 7 and 9 each carry a probe.\n"
    assert ls.derive_mutation_probe_count(block) == 4


def test_mutation_probe_recount_deduplicates_repeated_references() -> None:
    block = "**Mutation-probe obligations.** Criteria 3 and 5; criterion 3 again.\n"
    assert ls.derive_mutation_probe_count(block) == 2


def test_mutation_probe_recount_ignores_criteria_named_outside_the_section() -> None:
    """The cross-reference trap. Prose elsewhere in the block naming other
    criteria must not inflate the probe count -- the same trap that made a naive
    corroboration check mis-score `U-RT-147`."""
    block = (
        "Some prose citing Criteria 11, 12 and 13 from an unrelated unit.\n\n"
        "**Mutation-probe obligations.** Criteria 1 and 2 each carry a probe.\n\n"
        "**Tests:** more prose about Criteria 40, 41.\n"
    )
    assert ls.derive_mutation_probe_count(block) == 2


def test_mutation_probe_recount_returns_none_when_no_obligations_section() -> None:
    assert ls.derive_mutation_probe_count("**Acceptance criteria:**\n\n1. one\n") is None


def test_mutation_probe_recount_returns_none_not_zero_when_none_are_named() -> None:
    assert ls.derive_mutation_probe_count("**Mutation-probe obligations.** None owed.\n") is None


def test_mutation_probe_recount_is_exact_on_the_real_u_cp_102_block() -> None:
    """U-CP-102 names nine probe-carrying criteria: 4, 6, 7, 10, 11, 12, 14, 15, 16."""
    plan = ROOT / "design-substrate" / "Implementation_Plan_Control_Plane_v2_53.md"
    if not plan.exists():  # pragma: no cover - corpus moved
        return
    text = plan.read_text(encoding="utf-8")
    start = text.find("### §0.2 U-CP-102")
    end = text.find("### ", start + 10)
    assert ls.derive_mutation_probe_count(text[start:end]) == 9


def test_cite_check_skips_history_carriers_like_the_gate_log():
    """A gate-log row records a reviewer finding's location at the head it REVIEWED; that
    line drifts by design as the arc absorbs it -- evidence of a past head, not a claim."""
    report = ls.Report()
    ls.check_cites(
        {".harness/merge-gate-log.jsonl": ['{"location": "tools/leg_selfcheck.py:999999"}']},
        report,
    )
    assert _hard(report) == []
    report = ls.Report()
    ls.check_cites({"spec.md": ["see tools/leg_selfcheck.py:999999"]}, report)
    assert any("stale cite" in m for m in _hard(report))
