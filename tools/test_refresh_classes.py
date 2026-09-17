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


def test_class_7_does_not_claim_sourced_shell_caller_state():
    """The shell half of class 7 was tried and withdrawn; nothing here claims it.

    A sourced file mutating its caller's shell IS class 7's concern in another substrate, but
    no term for it survived. `caller's shell` was measured against the committed gate log and
    matched two findings -- one of them about a caller's `set -e` propagating INTO a sourced
    file, the opposite direction -- a precision of 1/2. Under this file's prefer-to-miss
    policy, a term that steals a real finding from the unmatched pile does not earn its place,
    so these shapes stay in the pile where a human reads them.

    Pinned in both directions: re-adding any such term reds the first assertion, and losing
    the Python vocabulary reds the second.
    """
    unclaimed = [
        {
            "finding_id": "u:1",
            "observed_evidence": (
                "because lane-init.sh is sourced, this assignment writes _LI_SRC into the "
                "caller's shell, and every successful path leaves it defined"
            ),
            "location": "tools/hooks/lane-init.sh:31",
        },
        {
            "finding_id": "u:2",
            "observed_evidence": (
                "lib.sh inherits the caller's shell options, so a caller running with set -e "
                "exits on the first lock collision before rc=$? is captured"
            ),
            "location": "tools/hooks/lib.sh:144",
        },
    ]
    still_claimed = [
        {
            "finding_id": "k:1",
            "observed_evidence": "the fixture writes os.environ directly and never restores it",
            "location": "",
        },
    ]
    out = json.loads(_run("classify", stdin=json.dumps(unclaimed + still_claimed)).stdout)
    for fid in ("u:1", "u:2"):
        assert "7 env-var mutation / restore" not in out[fid], (fid, out[fid])
    assert "7 env-var mutation / restore" in out["k:1"], out["k:1"]


def test_class_3_does_not_describe_the_class_table_itself():
    """No class term names this table's own machinery, deliberately.

    Every phrasing tried ("intake path", "intake pile", "classifies unrelated") also reads
    naturally in findings about ingestion endpoints and queue growth, and narrowing never
    converged: four consecutive review rounds, each correct, each attacking the phrase the
    last added. A classifier cannot be widened to catch the complaint that it is too wide.
    Findings about the table stay unmatched, which is where a human reads them.
    """
    rows = [
        {
            "finding_id": "m:1",
            "observed_evidence": (
                "classifies unrelated ownership findings, which removes it from the "
                "unmatched intake pile"
            ),
            "location": "",
        },
        {
            "finding_id": "m:2",
            "observed_evidence": (
                "the webhook intake pile grows without bound and exhausts memory under burst"
            ),
            "location": "",
        },
        {
            "finding_id": "m:3",
            "observed_evidence": "the unsigned webhook intake path accepts forged payloads",
            "location": "",
        },
        # ...while genuine class-3 vocabulary is untouched by the removal.
        {
            "finding_id": "m:4",
            "observed_evidence": "the except arm swallows the error and returns an empty list",
            "location": "",
        },
    ]
    out = json.loads(_run("classify", stdin=json.dumps(rows)).stdout)
    for fid in ("m:1", "m:2", "m:3"):
        assert "3 silent failure / fallback" not in out[fid], (fid, out[fid])
    assert "3 silent failure / fallback" in out["m:4"], out["m:4"]


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
