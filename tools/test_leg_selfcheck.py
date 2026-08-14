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
    ls.check_register_rows(["- id: B-166"], _REGISTER_PATHS, report)
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
    assert ls.changed_line_numbers(diff) == {"x.md": {11}}
    # ...and the added-lines view is still empty, which is why it could not see it
    assert ls.added_by_file(diff) == {"x.md": []}
