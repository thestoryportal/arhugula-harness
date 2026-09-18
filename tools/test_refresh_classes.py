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
    # see the LEFT OUT note above CLASSES). This test pins only that class 2 does not
    # claim them. It no longer means "these stay in the intake pile": d:1 is a test
    # codifying a drift, so class 16 claims it now — which is the whole point of that
    # class, and is why the LEFT OUT note routes this shape there rather than to class 2
    # (merge-gate witness lens r6 P3: this diff invalidated the older wording).
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
    no term for it survived. `caller's shell` was tried and WITHDRAWN: it claimed a finding
    this class does not own, and under the prefer-to-miss policy a term that steals from the
    unmatched pile does not earn its place. That claim is EXISTENTIAL and so survives a growing
    corpus; what is not restated is any COUNT or PRECISION figure, which a growing gate log
    makes true at one anchor and false at the next. These shapes stay in the pile where a human
    reads them.

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


def test_class_4_claims_the_leaves_this_test_green_idiom():
    """The canonical vacuous-witness phrasing, adopted on MEASURED evidence.

    Run against the committed corpus this alternative newly matched rows that were each
    audited individually: every one is "removing/reverting/deleting X leaves this test
    green", which is class 4 exactly. Three sibling candidates were measured in the same
    pass and rejected for mixing in races, spec findings and lock ordering -- `cannot
    detect`, `never (exercis|reach)`, `claim ... is false`. Measuring first is the whole
    difference between this term and the ones this arc withdrew.
    """
    positives = [
        {
            "finding_id": "g:1",
            "observed_evidence": (
                "the test exercises only the readability preflight and never the new "
                "per-source status check; removing the guard would leave this test green"
            ),
            "location": "tools/hooks/test_lane_init.sh:1053",
        },
        {
            "finding_id": "g:2",
            "observed_evidence": (
                "deleting the production _kill_after call would leave the suite green"
            ),
            "location": "",
        },
    ]
    negatives = [
        {
            "finding_id": "g:n1",
            "observed_evidence": "a peer can claim the file between glob and read",
            "location": "",
        },
        {
            "finding_id": "g:n2",
            "observed_evidence": (
                "the holder gate admits a terminal merged reservation, contradicting C-HE-03 §6"
            ),
            "location": "",
        },
    ]
    out = json.loads(_run("classify", stdin=json.dumps(positives + negatives)).stdout)
    for fid in ("g:1", "g:2"):
        assert "4 vacuous witness" in out[fid], (fid, out[fid])
    for fid in ("g:n1", "g:n2"):
        assert "4 vacuous witness" not in out[fid], (fid, out[fid])


def test_class_3_does_not_describe_the_class_table_itself():
    """No class term names this table's own machinery, deliberately.

    Every phrasing tried ("intake path", "intake pile", "classifies unrelated") also reads
    naturally in findings about ingestion endpoints and queue growth, and narrowing never
    converged -- round after round, each correct, each attacking the phrase the last one
    added. A classifier cannot be widened to catch the complaint that it is too wide.
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


def test_class_16_needs_both_a_blessing_verb_and_the_artifact_doing_it():
    # Evidence quoted from the rows measured into this class — 14 of them, in the gate log
    # as of base 63e19e3ee (2,162 findings), the same anchor the class row cites, because
    # this class is measured against the log its own arc's findings append to and a live
    # total is stale before it can be committed. The PHRASE is the contract, and after
    # five review rounds it is a single one: the word `test` must appear BEFORE a blessing
    # verb, within one sentence. So a blessing verb with no `test` in its sentence is not
    # this class (the measured `--match-head-commit merely pins the merge` false match, a
    # spec that codifies a rule, a bare pronoun, a witness noun in the object position),
    # and neither is a `test` that blesses nothing. Asserted through the `classify` verb,
    # never against the regex ([LAW:behavior-not-structure]).
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
        # the artifact is a test NAME, so a trailing `\b` would miss it: the underscore is
        # a word character, which is why the token ends in the `(?![a-z])` lookahead —
        # `test` may be followed by `_`, but not by another letter. (This comment cited the
        # long-deleted `tests?[\w-]*` until lens r8; the token it credits must be the one
        # the row actually ships.)
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
        # (merge-gate witness lens r1). The two are pinned by DIFFERENT guards, measured:
        # `attestation` is refused by the `(?![a-z])` lookahead (the char after the
        # embedded "test" is a letter), so n:6 stays green if the leading \b is deleted;
        # only `latest` — where a space follows — actually depends on that \b, so n:7 is
        # its witness. An earlier comment here credited \b for both (lens r5 P2).
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
        # a BARE PRONOUN before a blessing verb, with no test artifact anywhere in the
        # sentence (merge-gate witness lens r3). `it`/`which` were in the pronoun arm's
        # first draft and carried zero recall, so they were cut rather than bounded: these
        # are ordinary config-drift findings and must stay in the intake pile.
        {
            "finding_id": "n:11",
            "observed_evidence": "The retry budget grew from 3 to 5, and it blesses looser"
            " SLAs without updating the plan.",
            "location": "",
        },
        {
            "finding_id": "n:12",
            "observed_evidence": "The team raised the timeout, which enshrines the"
            " assumption of network latency.",
            "location": "",
        },
        # a sentence break on `?` or `!` rather than `.` — the window's terminator set was
        # `.` alone for six rounds, so "Did the test pass? The spec codifies the older
        # rule." false-matched (merge-gate witness lens r7 P2). 13 base-corpus rows pair
        # this class's `test` token with `!` or `?`, so the surface was live.
        {
            "finding_id": "n:17",
            "observed_evidence": "Did the test pass? The spec codifies the older rule.",
            "location": "",
        },
        {
            "finding_id": "n:18",
            "observed_evidence": "The test failed! The spec codifies the older rule.",
            "location": "",
        },
        # an artifact->verb gap WIDER than the window: the cap is 80 and this gap is 117,
        # so the sentence is refused. The widest gap among the real members is 60
        # ("test at <path>:1301 enshrines"), which is where 80 comes from -- 60 plus
        # headroom, not a round number chosen by eye. Without this case the cap is
        # unwitnessed and a regression to an unbounded window would pass every other
        # test (merge-gate witness lens r6 P2).
        {
            "finding_id": "n:16",
            "observed_evidence": "The test suite ran green and the deployment completed"
            " cleanly and the release notes were filed by the operator, and the spec"
            " codifies the older rule",
            "location": "",
        },
        # a witness noun that is the sentence's OBJECT, not the subject of the blessing
        # verb (merge-gate witness lens r5). No regex can tell those apart, so the whole
        # `CI|witness|fixture` arm was cut once measured to add zero to the new-class
        # pile; these cases pin that it stays cut.
        {
            "finding_id": "n:13",
            "observed_evidence": "The team ignoring the fixture blesses the shortcut anyway.",
            "location": "",
        },
        {
            "finding_id": "n:14",
            "observed_evidence": "A witness account later enshrines a different version of"
            " events in the transcript.",
            "location": "",
        },
        {
            "finding_id": "n:15",
            "observed_evidence": "The CI dashboard owner blesses this manually every week.",
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


def test_owed_pointer_refresh_is_not_class_vocabulary():
    # U-HE-45 shipped this shape as class 17 and SUBTRACTED it three rounds later; see the
    # ALSO-evaluated-and-LEFT-OUT note above CLASSES for the measurements. This test pins the
    # subtraction, so the row cannot creep back without a decision: no class may claim these
    # rows on pointer vocabulary alone.
    #
    # p:1/p:2 are genuine members of the SHAPE — a surface consumers read still naming what was
    # just finished — and they stay in the intake pile, which is the correct place for a shape
    # whose vocabulary was measured unable to carry it.
    #
    # p:3 is codex r5's counterexample and the reason the last regex died: `still points` with
    # POSITIVE polarity. A pattern keyed on "still says/names/points" reads a FRESH pointer as a
    # stale one, and polarity is not regex-expressible — so if anyone re-adds the row, this case
    # is what goes red. It must never be claimed by any class.
    rows = [
        {
            "finding_id": "p:1",
            "observed_evidence": "its live pointer still says U-HE-45 is the next implementable"
            " unit",
            "location": "",
        },
        {
            "finding_id": "p:2",
            "observed_evidence": "The live pointer was never refreshed after the unit completed.",
            "location": "",
        },
        {
            "finding_id": "p:3",
            "observed_evidence": "The live pointer is fresh and still points to the intended next"
            " unit after the refresh",
            "location": "",
        },
    ]
    out = json.loads(_run("classify", stdin=json.dumps(rows)).stdout)
    for row in rows:
        assert out[row["finding_id"]] == [], (row["finding_id"], out[row["finding_id"]])


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
