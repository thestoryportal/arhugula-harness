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
            "spec.md": ["The delta carries 4 carrier amendments."],
            "plan.md": ["The delta carries FIVE carrier amendments."],
        }
    )
    msgs = _hard(report)
    assert any("carrier amendments" in m and "DIFFERENT" in m for m in msgs), msgs


def test_count_check_is_silent_when_every_mirror_agrees():
    report = _report_for_counts(
        {
            "spec.md": ["The delta carries 5 carrier amendments."],
            "plan.md": ["Confirmed: FIVE carrier amendments."],
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
    disagreeing = ["It has 3 sites.", "It has 9 sites."]
    assert _hard(_report_for_counts({"spec.md": disagreeing})) != []
    assert _hard(_report_for_counts({".harness/roadmap_drift_log_archive.md": disagreeing})) == []


# --- check 3: § label collision ----------------------------------------------


def _substrate(tmp_path, files: dict[str, str]):
    d = tmp_path / "design-substrate"
    d.mkdir()
    for name, body in files.items():
        (d / name).write_text(body, encoding="utf-8")
    return d


def test_label_check_fires_when_a_minted_label_already_heads_a_section_elsewhere(tmp_path):
    """The B-71 defect: §25.17/§25.18 were minted fresh and were already CP
    v1.32's. Nothing local to the edited file can see that."""
    d = _substrate(
        tmp_path,
        {
            "Spec_A_v1_32.md": "### §25.17 Existing section\n",
            "Spec_A_v1_119.md": "### §25.17 New\n",
        },
    )
    report = ls.Report()
    ls.check_label_collisions({"design-substrate/Spec_A_v1_119.md": ["### §25.17 New"]}, report, d)
    msgs = _hard(report)
    assert any("§25.17" in m and "delta chain" in m for m in msgs), msgs


def test_label_check_is_silent_when_the_minted_label_is_free(tmp_path):
    d = _substrate(tmp_path, {"Spec_A_v1_119.md": "### §25.99 Brand new\n"})
    report = ls.Report()
    ls.check_label_collisions(
        {"design-substrate/Spec_A_v1_119.md": ["### §25.99 Brand new"]}, report, d
    )
    assert _hard(report) == []
    assert report.stats["labels_minted"] == 1


def test_label_check_ignores_a_bare_cite_which_is_expected_to_already_exist(tmp_path):
    """`see §25.17` in prose is a REFERENCE, not a mint. Flagging references
    would make every arc that cites a spec fail."""
    d = _substrate(tmp_path, {"Spec_A_v1_32.md": "### §25.17 Existing\n"})
    report = ls.Report()
    ls.check_label_collisions({"design-substrate/x.md": ["Per §25.17 the rule holds."]}, report, d)
    assert _hard(report) == []
    assert report.stats["labels_minted"] == 0


def test_label_check_does_not_read_a_python_comment_as_a_minted_heading(tmp_path):
    """REGRESSION (first dogfood run): `# §12.2.1, enforced ...` in a .py file is
    byte-identical to an h1 markdown heading, and was reported as a mint."""
    d = _substrate(tmp_path, {"Spec_A.md": "### §12.2.1 Owned elsewhere\n"})
    report = ls.Report()
    ls.check_label_collisions({"tools/x.py": ["    # §12.2.1, enforced not documented"]}, report, d)
    assert report.stats["labels_minted"] == 0
    assert _hard(report) == []


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
    disagreeing = ["It has 3 sites.", "It has 9 sites."]
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
