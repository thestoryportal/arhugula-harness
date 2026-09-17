"""The defect-class-preflight skill's `refresh-classes.py`: the corpus report and the
`classify` verb the review-loop gate consumes at sweep template/attest time.

Behavioural contract only ([LAW:behavior-not-structure]): JSON list in, finding_id →
class-name list out; malformed input and unknown verbs exit non-zero on stderr, never
an empty map that would read as 'every finding unmatched'."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = (
    Path(__file__).resolve().parent.parent
    / ".claude/skills/defect-class-preflight/scripts/refresh-classes.py"
)


def _run(*argv: str, stdin: str = "", cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *argv],
        input=stdin,
        capture_output=True,
        text=True,
        cwd=cwd,
    )


def test_classify_names_every_matching_class_and_empty_for_unmatched():
    rows = [
        {
            "finding_id": "a:1",
            "observed_evidence": "a race between two writers; the timeout is never retried",
            "location": "x.py:1",
        },
        {"finding_id": "a:2", "observed_evidence": "the widget frobnicates", "location": ""},
    ]
    proc = _run("classify", stdin=json.dumps(rows))
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    assert set(out) == {"a:1", "a:2"}
    assert "1 race / TOCTOU / atomicity / lock" in out["a:1"]
    assert "5 timeout / retry / budget" in out["a:1"]
    assert out["a:2"] == []


def test_bare_drift_is_not_class_2_vocabulary():
    # handoff-s2 §2 B proposed `\bdrift` for class 2; the corpus said no (30 of 35 "drift"
    # rows are contract / configuration / roadmap drift or the arc-metrics drift cohort —
    # see the LEFT OUT note above CLASSES). These shapes must stay in the intake pile.
    rows = [
        {
            "finding_id": "d:1",
            "observed_evidence": "the added test codifies this contract drift",
            "location": "",
        },
        {
            "finding_id": "d:2",
            "observed_evidence": "allowing configuration drift to go undetected",
            "location": "",
        },
        {
            "finding_id": "d:3",
            "observed_evidence": "reports a confident zero regardless of actual roadmap drift",
            "location": "",
        },
        {"finding_id": "d:4", "observed_evidence": "the lease is left adrift", "location": ""},
    ]
    out = json.loads(_run("classify", stdin=json.dumps(rows)).stdout)
    for fid in ("d:1", "d:2", "d:3", "d:4"):
        assert "2 prose stale / counts / cites" not in out[fid], fid


def test_classify_reads_the_location_too():
    # the location carries file-shaped vocabulary the row text may lack
    rows = [{"finding_id": "b:1", "observed_evidence": "", "location": "tools/conftest.py fixture"}]
    out = json.loads(_run("classify", stdin=json.dumps(rows)).stdout)
    assert "10 fixture scope / lifecycle" in out["b:1"]


def test_classify_malformed_input_is_a_loud_nonzero_exit():
    for bad in ("not json", "[{}]", '[{"finding_id": 1, "observed_evidence": 2}]', "{}"):
        proc = _run("classify", stdin=bad)
        assert proc.returncode == 2, bad
        assert "malformed input" in proc.stderr
        assert proc.stdout == ""


def test_unknown_verb_refuses():
    proc = _run("bogus")
    assert proc.returncode == 2
    assert "usage" in proc.stderr


def test_report_counts_agree_with_classify(tmp_path: Path):
    # one authority: the report's per-class tally and the verb's answer derive from
    # the same function, so a row the verb calls unmatched is one the report lists
    log = tmp_path / ".harness" / "merge-gate-log.jsonl"
    log.parent.mkdir()
    rows = [
        {"record_kind": "finding", "observed_evidence": "swallowed via 2>/dev/null", "ts": "2026"},
        {"record_kind": "finding", "observed_evidence": "the widget frobnicates", "ts": "2026"},
        {"record_kind": "no_finding", "observed_evidence": "", "ts": "2026"},
    ]
    log.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    # the report resolves its log from the script's own location: run a copy
    # planted at the same relative path under the temp repo
    copy = tmp_path / SCRIPT.relative_to(SCRIPT.parents[4])
    copy.parent.mkdir(parents=True)
    copy.write_text(SCRIPT.read_text())
    proc = subprocess.run([sys.executable, str(copy)], capture_output=True, text=True, cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    assert "2 findings in" in proc.stdout
    assert "    1  3 silent failure / fallback" in proc.stdout
    assert "Unmatched findings (new-class candidates): 1" in proc.stdout
    # the same rows through the verb: its per-class tally and its unmatched count must be
    # the numbers the report printed — one function, two consumers (handoff-s2 §2 B, P3)
    finding_rows = [
        {"finding_id": f"r:{i}", "observed_evidence": r["observed_evidence"], "location": ""}
        for i, r in enumerate(rows)
        if r["record_kind"] == "finding"
    ]
    verb = subprocess.run(
        [sys.executable, str(copy), "classify"],
        input=json.dumps(finding_rows),
        capture_output=True,
        text=True,
        cwd=tmp_path,
    )
    assert verb.returncode == 0, verb.stderr
    by_id = json.loads(verb.stdout)
    assert len(by_id) == 2
    unmatched = sum(1 for hits in by_id.values() if not hits)
    silent = sum(1 for hits in by_id.values() if "3 silent failure / fallback" in hits)
    assert f"Unmatched findings (new-class candidates): {unmatched}" in proc.stdout
    assert f"    {silent}  3 silent failure / fallback" in proc.stdout
    assert "the widget frobnicates" in proc.stdout


def test_class_16_needs_both_a_blessing_verb_and_the_artifact_doing_it():
    # Evidence quoted from the rows measured into this class (2026-09-17 corpus of 2,163;
    # 15 rows matched no other class). The PHRASE is the contract: one alternative must
    # carry both halves, so a blessing verb whose subject is no witness is NOT this class
    # — the measured `--match-head-commit merely pins the merge` false match, and a spec
    # that codifies a rule is not a test that blesses a departure. Asserted through the
    # `classify` verb, never against the regex ([LAW:behavior-not-structure]).
    codifying = [
        {
            "finding_id": "c:1",
            "observed_evidence": "The new merged-holder test codifies this contract drift"
            " while the clearance claims no spec contract changed.",
            "location": "tools/arc_metrics.py:564",
        },
        {
            "finding_id": "c:2",
            "observed_evidence": "The rewritten test now expects the sibling R-999 row,"
            " so it blesses rather than detects this regression",
            "location": "tools/arc_exit_report.py:600",
        },
        {
            "finding_id": "c:3",
            "observed_evidence": "the new row-order test enshrines the opposite contract",
            "location": "tools/loop_cost_baseline.py:47",
        },
        {
            "finding_id": "c:4",
            "observed_evidence": "test_codex_workflow_parity.py even requires the omission,"
            " so CI codifies the admitted cohort gap instead of detecting it.",
            "location": ".agents/skills/ship-pr/SKILL.md:208",
        },
        # the subject sits an adverb away from its verb ("witness INSTEAD blesses"), which
        # is what the pronoun arm's <=2-word gap buys; without it this true member drops
        {
            "finding_id": "c:5",
            "observed_evidence": "this witness instead blesses 4,636,541 (4.64M) and labels"
            " the difference a correction. That changes the measurement baseline without"
            " updating the governing plan",
            "location": "tools/test_arc_cost.py:243",
        },
        # the artifact is a test NAME, so `\btest\b` would miss it: the underscore is a
        # word character, which is why the token stays `tests?[\w-]*`
        {
            "finding_id": "c:6",
            "observed_evidence": "test_happy_path_lands_holds_through_ci_and_releases"
            " currently codifies this refresh-free path as the happy path.",
            "location": "tools/merge_door.py:1226",
        },
    ]
    not_codifying = [
        # a blessing verb, no witness anywhere in the text
        {
            "finding_id": "n:1",
            "observed_evidence": "--match-head-commit merely pins the merge to that"
            " unreviewed H2, and the spec codifies the older rule.",
            "location": "",
        },
        # a witness, but nothing blessing anything
        {
            "finding_id": "n:2",
            "observed_evidence": "the added failure test asserts the warning",
            "location": "",
        },
        # THE production failure mode (codex r1 P2): classification reads evidence PLUS
        # location, so a paired verb/artifact conjunct was satisfied by the location
        # alone — every finding located in a test file became this class. An empty
        # location cannot witness that, which is why n:1/n:2 above did not catch it.
        {
            "finding_id": "n:3",
            "observed_evidence": "the governing spec codifies the required behavior,"
            " but implementation violates it",
            "location": "tools/test_widget.py",
        },
        # same hole one directory shape over: `/tests/` survives a word boundary that
        # `test_widget` does not, so the boundary alone was never the fix — ordering is
        {
            "finding_id": "n:4",
            "observed_evidence": "the spec codifies the older rule",
            "location": "harness-cp/tests/test_foo.py",
        },
        # co-occurrence ACROSS a sentence break: the witness and the blessing belong to
        # different claims, which is what the one-sentence window refuses
        {
            "finding_id": "n:5",
            "observed_evidence": "The test passes cleanly. The spec codifies the older rule.",
            "location": "",
        },
        # `test` as a SUBSTRING of this workspace's own vocabulary — at-TEST-ation, la-TEST
        # (merge-gate witness lens, P2). The leading \b is what refuses these, and dropping
        # it is the likeliest regression here precisely because `attest` is everywhere in
        # this repo: a finding about the attestation step is not a finding about a test.
        {
            "finding_id": "n:6",
            "observed_evidence": "the attestation step now codifies the loosened threshold"
            " as permanent policy",
            "location": "",
        },
        {
            "finding_id": "n:7",
            "observed_evidence": "the latest commit codifies a workaround instead of fixing it",
            "location": "",
        },
        # a word that merely BEGINS with `test` (merge-gate witness lens r2). The leading
        # \b admits these — `testament` starts at a word boundary — so the token needs the
        # `(?![a-z])` lookahead too: it is the WORD `test`, not a prefix of a longer word.
        {
            "finding_id": "n:9",
            "observed_evidence": "the last testament codifies the will's provisions",
            "location": "",
        },
        {
            "finding_id": "n:10",
            "observed_evidence": "her testimony codifies the account",
            "location": "",
        },
        # an `assert`-shaped PATH: the old tuple's artifact half matched `assert` anywhere,
        # so a path alone satisfied it. Ordering refuses it now — this case existed only in
        # the arc's transient measurement until the lens noted the comment claimed a probe
        # the suite did not carry
        {
            "finding_id": "n:8",
            "observed_evidence": "the ADR codifies a different bound",
            "location": "tools/test_assertions.py:12",
        },
    ]
    out = json.loads(_run("classify", stdin=json.dumps(codifying + not_codifying)).stdout)
    for r in codifying:
        assert "16 witness codifies the divergence" in out[r["finding_id"]], r["location"]
    for r in not_codifying:
        assert "16 witness codifies the divergence" not in out[r["finding_id"]], r["finding_id"]


def test_every_class_row_has_its_skill_section_and_vice_versa():
    # the table and the author-facing checklist are two carriers of one class list
    # (codex r1 P2 on the intake arc): a row landed in one without the other is the
    # drift the skill's own docstring forbids, so it fails here rather than in review
    import re
    import runpy

    table = runpy.run_path(str(SCRIPT))["CLASSES"]
    table_numbers = {name.split(" ", 1)[0] for name in table}
    skill = (SCRIPT.parents[1] / "SKILL.md").read_text()
    section_numbers = set(re.findall(r"^### (\d+)\. ", skill, re.M))
    assert table_numbers == section_numbers
