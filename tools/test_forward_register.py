"""Tests for the forward register (post-Phase-8 forward-work schema).

Mirrors `tools/test_arc_ledger.py`: the live register must pass validation AND the
prose-drift cross-check, the derived counts must match the snapshot pin (no inline
magic numbers), and a battery of NEGATIVE tests proves each gate failure-class is
actually caught.
"""

from __future__ import annotations

import copy
import sys
import tempfile
from contextlib import contextmanager
from pathlib import Path

# `tools/` is not a package and pytest runs under `--import-mode=importlib`, which does
# NOT put this directory on `sys.path`. Without this insert the module imports only when
# some OTHER test file in the same invocation happens to have inserted it first — an
# order-dependent pass that vanishes the moment that sibling is renamed (B-184 close-out 3).
sys.path.insert(0, str(Path(__file__).resolve().parent))

import forward_register
import pytest


def _has_text(v: object) -> bool:
    return isinstance(v, str) and bool(v.strip())


def _data() -> dict:
    return forward_register.load()


@contextmanager
def _temp_prose(mutate_text):
    prose_text = forward_register.DEFAULT_PROSE.read_text(encoding="utf-8")
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write(mutate_text(prose_text))
        tmp_path = Path(fh.name)
    try:
        yield tmp_path
    finally:
        tmp_path.unlink()


def test_live_register_passes_validation() -> None:
    assert forward_register.validate(_data()) == []


def test_live_register_has_no_prose_drift() -> None:
    assert forward_register.check_prose_drift(_data()) == []


def test_derived_counts_match_snapshot_pin() -> None:
    data = _data()
    d = forward_register.derive(data)
    snap = data["snapshot"]
    for key in (
        "total",
        "open",
        "design_substrate_gated",
        "registered_finding",
        "operator_gated",
        "held",
        "closed",
    ):
        assert d[key] == snap[key], f"{key}: derived {d[key]} != snapshot {snap[key]}"
    assert forward_register._identity_digest(data["items"]) == snap["identity_digest"]


def test_contract_closed_items_carry_a_pr_citation() -> None:
    d = forward_register.derive(_data())
    for r in d["items"]:
        if r["status"] == "closed":
            assert r.get("pr"), f"{r['id']}: closed item must cite a deliverable"


def test_contract_open_items_carry_close_out_and_council() -> None:
    d = forward_register.derive(_data())
    for r in d["open_items"]:
        assert r.get("close_out"), f"{r['id']}: open-class item must carry close_out"
        assert r.get("council"), f"{r['id']}: open-class item must carry a council disposition"


def test_contract_every_row_has_a_heading_backpointer() -> None:
    d = forward_register.derive(_data())
    for r in d["items"]:
        assert r.get("heading"), f"{r['id']}: missing heading back-pointer"


def test_detail_lookup_returns_the_prose_block() -> None:
    data = _data()
    row = next(r for r in data["items"] if r["id"] == "B-24")
    assert row["heading"] in forward_register.DEFAULT_PROSE.read_text(encoding="utf-8")


def test_detail_cli_anchors_to_the_real_heading_line_not_a_decoy_substring(capsys) -> None:
    """A heading string quoted earlier in the file (e.g. as an inline cross-reference)
    must not hijack `--detail` -- it has to find the actual heading LINE, not the
    first place the text happens to appear."""
    heading = next(r["heading"] for r in _data()["items"] if r["id"] == "B-24")

    def mutate_prose(text: str) -> str:
        decoy = f"An earlier section references {heading!r} as an example.\n\n"
        return decoy + text

    with _temp_prose(mutate_prose) as tmp_path:
        forward_register.main(
            [
                "--detail",
                "B-24",
                "--ledger",
                str(forward_register.DEFAULT_LEDGER),
                "--prose",
                str(tmp_path),
            ]
        )
        out = capsys.readouterr().out
        # The canonical block prints first, so the anchoring property is asserted on
        # the PROSE SECTION rather than on the whole output -- same proof, new offset.
        prose_section = out.split(forward_register.PROSE_DELIMITER, 1)[1].lstrip("\n")
        assert prose_section.startswith(heading)
        assert "An earlier section references" not in out


def test_detail_renders_the_canonical_close_out_even_when_the_prose_disagrees(capsys) -> None:
    """B-235. `--detail` renders the PROSE carrier, but `close_out` in the YAML is the
    authority, and `check_prose_drift` compares headings only -- so a prose body edited
    out of step with `close_out` used to leave operator-facing routing showing only the
    hand-copy. The witness is behavioural, not a presence check: the prose copy is
    mutated to CONTRADICT the canonical field, and the canonical text must still reach
    the reader."""
    row = next(r for r in _data()["items"] if r["id"] == "B-234")
    canonical = row["close_out"]
    # Without this, a future edit blanking B-234's close_out would make the canonical-text
    # assertion vacuously true rather than failing (merge-gate witness lens, P3).
    assert row["status"] != "closed" and canonical and canonical.strip(), (
        "fixture: B-234 must be open-class with a non-blank close_out"
    )

    def gut_the_prose(text: str) -> str:
        # Replace the prose body's own disposition with a contradicting one.
        return text.replace(
            "REGISTERED, and **BLOCKING the Scope-level completeness of U-HE-37**",
            "CLOSED — nothing blocks U-HE-37",
        )

    with _temp_prose(gut_the_prose) as tmp_path:
        forward_register.main(
            [
                "--detail",
                "B-234",
                "--ledger",
                str(forward_register.DEFAULT_LEDGER),
                "--prose",
                str(tmp_path),
            ]
        )
        out = capsys.readouterr().out

    # The canonical disposition reaches the reader despite the prose saying otherwise.
    assert canonical.split("\n")[0].strip()[:60] in " ".join(out.split())[:4000] or (
        canonical[:60] in out
    )
    assert "CANONICAL" in out
    # ...and it is read BEFORE the hand-copy, so the authority is never met second.
    assert out.index("CANONICAL") < out.index(forward_register.PROSE_DELIMITER)
    # The contradicting prose is still shown -- the divergence is made visible, not hidden.
    assert "CLOSED — nothing blocks U-HE-37" in out


def test_detail_states_an_absent_close_out_rather_than_omitting_it(capsys) -> None:
    """A `held` row carries no `close_out` by design, and `held` is the ONE non-closed,
    non-open-class status -- so it is the only fixture that reaches the "not required"
    arm. (Closed rows render their closure instead; open-class rows must carry one.)
    Printing nothing would be indistinguishable from a close_out that failed to load, so
    absence is STATED -- gate-cannot-tell-empty-from-unlooked, applied to a renderer."""
    row = next(r for r in _data()["items"] if r["id"] == "B-149")
    assert row["status"] == "held" and not row.get("close_out"), (
        "fixture: B-149 is held, no close_out"
    )

    forward_register.main(["--detail", "B-149"])
    header = capsys.readouterr().out.split(forward_register.PROSE_DELIMITER, 1)[0]
    assert "close_out (CANONICAL" in header, header
    assert "(none — not required at status 'held')" in header, header


def test_detail_emits_the_delimiter_as_one_bare_unindented_line(capsys) -> None:
    """Pins the PRODUCER half of the contract `tools/leg_selfcheck.py` relies on.

    That consumer tolerates a missing delimiter (`cut = 0`) because injected `detail_fn`
    fakes predate the header. The tolerance is for the TEST SEAM only -- on the real path
    the delimiter is always emitted, and if it ever stopped being, the consumer would
    silently revert to counting the canonical header as prose body: the exact silent
    retirement of the YAML-only-row gate that B-235's consumer fix exists to prevent.
    Nothing else asserts the real CLI's shape, so this test is what closes that loop.
    """
    row = next(r for r in _data()["items"] if r["id"] == "B-235")
    # Fixture shape asserted, not assumed: this test pins the OPEN-CLASS header, so if a
    # future PR closes B-235 the label changes and the assertions below would silently
    # stop witnessing what they name (merge-gate witness lens, P3).
    assert row["status"] != "closed", "fixture: B-235 must be open-class for this test"

    forward_register.main(["--detail", "B-235"])
    lines = capsys.readouterr().out.splitlines()
    # Exactly one, and BARE -- an indented occurrence is row content, not the frame.
    assert lines.count(forward_register.PROSE_DELIMITER) == 1, lines[:20]
    idx = lines.index(forward_register.PROSE_DELIMITER)
    # The canonical header precedes it; the prose heading follows it.
    assert any(ln.startswith("close_out (CANONICAL") for ln in lines[:idx])
    assert any(ln.startswith("### B-235") for ln in lines[idx + 1 :])


def test_a_whitespace_only_close_out_is_rejected_not_accepted_as_present() -> None:
    """codex r2 [P2]. Plain truthiness accepted `"   "`, so `--check` stayed GREEN while
    `--detail` rendered a required canonical disposition as SILENCE -- the explicit-absence
    contract broken by the very predicate meant to uphold it. Blank is absent."""
    data = copy.deepcopy(_data())
    row = _first_open_class(data)
    row["close_out"] = "   \n\t  "
    violations = forward_register.validate(data)
    assert any("needs a 'close_out' field" in v for v in violations), violations


def test_a_whitespace_only_close_out_never_renders_as_silence(capsys) -> None:
    """The RENDER branch must use the same predicate the validator does. A first version of
    this test pointed at B-1, whose close_out is ABSENT rather than blank, so it exercised
    the `else` arm and passed even with truthiness restored -- a vacuous witness caught by
    the mutation probe. The input has to actually be whitespace."""
    import yaml as _yaml

    ledger = {
        "snapshot": {},
        "items": [
            {
                "id": "B-9999",
                "title": "t",
                "summary": "s",
                "status": "registered_finding",
                "close_out": "   \n\t  ",
                "council": "NO",
                "heading": "### B-9999 · blank close_out",
            }
        ],
    }
    with tempfile.TemporaryDirectory() as d:
        lp = Path(d) / "ledger.yaml"
        lp.write_text(_yaml.safe_dump(ledger), encoding="utf-8")
        pp = Path(d) / "prose.md"
        pp.write_text("### B-9999 · blank close_out\n\n- **What it is.** Body.\n", encoding="utf-8")
        forward_register.main(["--detail", "B-9999", "--ledger", str(lp), "--prose", str(pp)])
        out = capsys.readouterr().out

    header = out.split(forward_register.PROSE_DELIMITER, 1)[0]
    stated = [ln for ln in header.splitlines() if ln.startswith("  ")]
    # An explicit statement, never an empty gap between the label and the delimiter.
    assert stated, header
    # Since codex r9 the message is sharper than "(MISSING": a blank string is PRESENT and
    # malformed, which is a different fact from absent, and the renderer now says so.
    assert any("PRESENT but not text" in ln for ln in stated), header


@pytest.mark.parametrize("bad", [False, True, 0, 1, 1519, [], {}, 1.5, "", "   ", None])
def test_falsy_and_non_scalar_close_out_values_are_all_rejected(bad: object) -> None:
    """codex r3 [P2]. The r2 repair stringified before testing, so `str(False)` was
    `"False"` and `close_out: false` / `pr: 0` / `[]` began PASSING a check that plain
    truthiness had correctly rejected -- the gate widened by the fix meant to narrow it,
    and `--detail` could then present `False` as the canonical disposition. Every value
    the original truthiness test rejected must still be rejected."""
    data = copy.deepcopy(_data())
    row = _first_open_class(data)
    row["close_out"] = bad
    violations = forward_register.validate(data)
    assert any("needs a 'close_out' field" in v for v in violations), (bad, violations)


def test_an_integer_pr_citation_is_still_accepted() -> None:
    """The narrowing must not red the 4 live rows whose `pr` is a bare number -- the
    reason the predicate tests type rather than demanding `str`."""
    data = copy.deepcopy(_data())
    row = _first_closed(data)
    row["pr"] = 1519
    assert not [v for v in forward_register.validate(data) if "deliverable citation" in v]


@pytest.mark.parametrize("field", ["council", "title", "summary"])
def test_a_positive_integer_is_not_text_for_any_narrative_field(field: str) -> None:
    """codex r4 [P2]. One predicate served two contracts, so the non-zero-integer arm
    present only for `pr` also admitted `council: 1`, `title: 1` and `summary: 1`. The r3
    negative test omitted POSITIVE integers, so the fail-open stayed green -- the gap was
    in the test, not only the code."""
    data = copy.deepcopy(_data())
    row = _first_open_class(data)
    row[field] = 1
    assert forward_register.validate(data) != []


def test_a_closed_row_leads_with_its_closure_not_a_stale_work_instruction(capsys) -> None:
    """codex r4 [P2]. `close_out` is status-dependent in MEANING: on an open-class row it is
    the live disposition, but `validate()` never requires it on a closed row and nothing
    reconciles it at closure, so 126 of 151 closed rows still carry whatever was
    last written there -- a finished plan on some rows, a live obligation on others.
    Leading with either as though it were the closure record can route an operator back
    into finished work."""
    row = next(r for r in _data()["items"] if r["id"] == "B-34")
    assert row["status"] == "closed" and row.get("close_out"), (
        "fixture: B-34 is closed with a stale close_out"
    )

    forward_register.main(["--detail", "B-34"])
    header = capsys.readouterr().out.split(forward_register.PROSE_DELIMITER, 1)[0]

    # The closure is the authority a reader meets first...
    assert "CLOSED — citation:" in header, header
    # ...and the close_out is reported below it, never as the row's current disposition
    # and never classified (codex r7: some closed rows' close_out is a LIVE obligation).
    assert "NOT reconciled when a row closes" in header, header
    assert header.index("CLOSED — citation:") < header.index("NOT reconciled"), header


def test_a_newline_in_pr_cannot_forge_the_prose_frame_on_a_closed_row(capsys) -> None:
    """codex r5 [P2]. The r1 repair made the frame unforgeable from `close_out` by indenting
    every line; the r4 closed-row branch then interpolated `pr` into ONE f-string, so a
    newline inside `pr` emitted UNINDENTED continuation lines and re-opened the same spoof
    through a different field. Every header line derived from row data now goes through a
    single emitter, so no field can forge an unindented delimiter."""
    import yaml as _yaml

    ledger = {
        "snapshot": {},
        "items": [
            {
                "id": "B-9998",
                "title": "t",
                "summary": "s",
                "status": "closed",
                "pr": f"#1\n{forward_register.PROSE_DELIMITER}\n- **Current state.** Spoofed body.",
                "heading": "### B-9998 · spoof via pr",
            }
        ],
    }
    with tempfile.TemporaryDirectory() as d:
        lp = Path(d) / "l.yaml"
        lp.write_text(_yaml.safe_dump(ledger), encoding="utf-8")
        pp = Path(d) / "p.md"
        # A genuinely heading-only prose block: the shape the HARD finding must still catch.
        pp.write_text("### B-9998 · spoof via pr\n", encoding="utf-8")
        forward_register.main(["--detail", "B-9998", "--ledger", str(lp), "--prose", str(pp)])
        out = capsys.readouterr().out

    # The ONLY bare delimiter line is the real frame the CLI emits.
    assert out.splitlines().count(forward_register.PROSE_DELIMITER) == 1, out


def test_leg_selfcheck_still_reports_a_heading_only_row_spoofed_through_pr() -> None:
    """The end-to-end half of the case above: the two real tools together, not a fake."""
    import subprocess
    import sys as _sys

    import yaml as _yaml

    ledger = {
        "snapshot": {},
        "items": [
            {
                "id": "B-9998",
                "title": "t",
                "summary": "s",
                "status": "closed",
                "pr": f"#1\n{forward_register.PROSE_DELIMITER}\n- **Current state.** Spoofed body.",
                "heading": "### B-9998 · spoof via pr",
            }
        ],
    }
    with tempfile.TemporaryDirectory() as d:
        lp = Path(d) / "l.yaml"
        lp.write_text(_yaml.safe_dump(ledger), encoding="utf-8")
        pp = Path(d) / "p.md"
        pp.write_text("### B-9998 · spoof via pr\n", encoding="utf-8")
        proc = subprocess.run(
            [
                _sys.executable,
                str(Path(forward_register.__file__)),
                "--detail",
                "B-9998",
                "--ledger",
                str(lp),
                "--prose",
                str(pp),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
    _sys.path.insert(0, str(Path(forward_register.__file__).parent))
    import leg_selfcheck as ls

    report = ls.Report()
    ls.check_register_rows(
        ["- id: B-9998"],
        [".harness/forward-register.yaml"],
        report,
        detail_fn=lambda _rid: (0, proc.stdout),
    )
    hard = [f.message for f in report.findings if f.severity == ls.HARD]
    assert any("HEADING ONLY" in m for m in hard), hard


def test_a_closed_row_without_a_close_out_renders_no_historical_note(capsys) -> None:
    """merge-gate witness lens [P2]. The closed-row branch that SKIPS the historical note
    when close_out is blank/absent had no test, and it is the MODAL shape on the live
    register -- 25 of 151 closed rows take it on every `--detail`. Inverting that guard
    would print the historical preamble with nothing under it, and nothing would fail."""
    row = next(r for r in _data()["items"] if r["id"] == "B-1")
    assert row["status"] == "closed" and not row.get("close_out"), (
        "fixture: B-1 is closed and carries no close_out"
    )

    forward_register.main(["--detail", "B-1"])
    header = capsys.readouterr().out.split(forward_register.PROSE_DELIMITER, 1)[0]
    assert "CLOSED — citation:" in header, header
    # The close_out preamble belongs only to rows that HAVE one...
    assert "NOT reconciled when a row closes" not in header, header
    # ...but absence is still STATED, never a silent gap. The never-silence invariant is
    # universal; this branch used to emit nothing, which read the same as a field that
    # failed to load (codex r8 [P3]).
    assert "close_out: (none — not required once a row is closed)" in header, header


def test_a_closed_row_missing_its_pr_says_so_in_the_render_not_only_in_check(capsys) -> None:
    """merge-gate witness lens [P2]. `test_negative_closed_without_pr_fails` covers
    `validate()`, a DIFFERENT function; the render path's own message was unexercised, so
    a closed row with no citation could have rendered a blank or misleading authority line
    while the validator test stayed green."""
    import yaml as _yaml

    ledger = {
        "snapshot": {},
        "items": [
            {
                "id": "B-9997",
                "title": "t",
                "summary": "s",
                "status": "closed",
                "heading": "### B-9997 · closed with no pr",
            }
        ],
    }
    with tempfile.TemporaryDirectory() as d:
        lp = Path(d) / "l.yaml"
        lp.write_text(_yaml.safe_dump(ledger), encoding="utf-8")
        pp = Path(d) / "p.md"
        pp.write_text(
            "### B-9997 · closed with no pr\n\n- **What it is.** Body.\n", encoding="utf-8"
        )
        forward_register.main(["--detail", "B-9997", "--ledger", str(lp), "--prose", str(pp)])
        header = capsys.readouterr().out.split(forward_register.PROSE_DELIMITER, 1)[0]

    assert "(MISSING — a closed row needs a 'pr' citation" in header, header
    assert "CLOSED — delivered at" not in header, header


def test_a_closed_rows_pr_is_reported_as_a_citation_not_asserted_as_delivery(capsys) -> None:
    """codex r7 [P2]. `pr` is a deliverable citation of arbitrary shape, not proof of
    delivery: 19 closed rows cite something that is not a PR (`R-410`, `batch-53..57`,
    `CP spec v1.97`), and B-25 is closed carrying the placeholder `#PENDING` -- for which
    the old wording rendered the false assertion "CLOSED — delivered at #PENDING"."""
    row = next(r for r in _data()["items"] if r["id"] == "B-25")
    assert row["status"] == "closed" and row.get("pr") == "#PENDING", (
        "fixture: B-25 is closed with the placeholder citation #PENDING"
    )

    forward_register.main(["--detail", "B-25"])
    header = capsys.readouterr().out.split(forward_register.PROSE_DELIMITER, 1)[0]
    assert "CLOSED — citation: #PENDING" in header, header
    assert "delivered at" not in header, header


def test_a_closed_rows_close_out_is_not_declared_historical(capsys) -> None:
    """codex r7 [P2]. The r4 repair called EVERY closed row's close_out historical, which
    over-corrected. Nothing reconciles the field at closure, so its content varies: B-34's
    is a finished plan, but B-125's states a live disposition, a promotion trigger that
    REOPENS the row, and a gloss correction owed as a named rider on the next OD/CP spec
    delta. Telling a reader that is "not a current instruction" suppresses an active
    obligation. The tool cannot discriminate, so it must not classify."""
    row = next(r for r in _data()["items"] if r["id"] == "B-125")
    assert row["status"] == "closed" and _has_text(row.get("close_out")), (
        "fixture: B-125 is closed and carries a non-blank close_out"
    )
    assert "OWED" in row["close_out"], (
        "fixture: B-125's close_out states an owed obligation — the whole point of this test"
    )

    forward_register.main(["--detail", "B-125"])
    header = capsys.readouterr().out.split(forward_register.PROSE_DELIMITER, 1)[0]
    assert "NOT reconciled when a row closes" in header, header
    assert "not a current instruction" not in header, header
    assert "HISTORICAL" not in header, header

    # The PREAMBLE is not the payload. Asserting only the wrapper left this test green
    # when `_emit_indented(close_out, ...)` was deleted -- `--detail B-125` silently
    # dropped the live OWED obligation while all 160 tests passed (codex r11 [P2],
    # confirmed by mutation before fixing). The BODY must be witnessed too, both by a
    # fragment derived from the row (so it cannot drift) and by the semantic phrase that
    # is the whole reason this row is the fixture.
    assert "RIDER OWNER" in header, "B-125's live obligation must reach the header"
    first_line = row["close_out"].splitlines()[0]
    assert first_line[:80] in header, header[:400]


@pytest.mark.parametrize("status", ["closed", "held"])
@pytest.mark.parametrize("bad", [False, 0, [], {}, 1, "   "])
def test_a_present_but_malformed_close_out_is_rejected_at_any_status(
    status: str, bad: object
) -> None:
    """codex r9 [P2]. `close_out` is only REQUIRED on open-class rows, so nothing
    type-checked it on a closed or held row — `close_out: false` passed `--check`.
    Absent is legal where the field is not required; PRESENT-but-malformed never is."""
    data = copy.deepcopy(_data())
    row = next(r for r in data["items"] if r["status"] == status)
    row["close_out"] = bad
    violations = forward_register.validate(data)
    assert any("is present but is not non-blank text" in v for v in violations), (
        status,
        bad,
        violations,
    )


def test_a_malformed_close_out_renders_as_malformed_not_as_absent(capsys) -> None:
    """The renderer half of the same defect: `--detail` can be pointed at a file `--check`
    would reject, and reporting a malformed value as "(none)" is a lie in either
    direction. Malformed, absent, and absent-but-required are three different facts."""
    import yaml as _yaml

    ledger = {
        "snapshot": {},
        "items": [
            {
                "id": "B-9996",
                "title": "t",
                "summary": "s",
                "status": "closed",
                "pr": "#1",
                "close_out": False,
                "heading": "### B-9996 · malformed close_out",
            }
        ],
    }
    with tempfile.TemporaryDirectory() as d:
        lp = Path(d) / "l.yaml"
        lp.write_text(_yaml.safe_dump(ledger), encoding="utf-8")
        pp = Path(d) / "p.md"
        pp.write_text(
            "### B-9996 · malformed close_out\n\n- **What it is.** Body.\n", encoding="utf-8"
        )
        forward_register.main(["--detail", "B-9996", "--ledger", str(lp), "--prose", str(pp)])
        header = capsys.readouterr().out.split(forward_register.PROSE_DELIMITER, 1)[0]

    assert "PRESENT but not text" in header, header
    assert "(none —" not in header, header


@pytest.mark.parametrize("status", ["closed", "held"])
def test_a_null_close_out_is_absence_not_malformation(status: str) -> None:
    """codex r10 [P2], PARTIALLY accepted — the rule's WORDING was fixed, not the rule.

    The finding is right that "a field that is PRESENT must be well-formed" and a
    `value is not None` test disagree, since `close_out: null` is a present KEY. It is
    wrong that null should therefore be rejected: in YAML `null` IS a spelling of absence
    (a bare `close_out:` parses to None, and round-tripping an omitted key through
    safe_dump/safe_load can produce either form), and this register spells absence by
    OMITTING the key on all 27 rows that lack a close_out, writing an explicit null
    nowhere. Rejecting it would red a legitimate authoring style to draw a distinction the
    data model does not make. This test pins that as a DECISION, not an accident.
    """
    data = copy.deepcopy(_data())
    row = next(r for r in data["items"] if r["status"] == status)
    row["close_out"] = None
    assert not [v for v in forward_register.validate(data) if "close_out" in v], (
        "null is absence: it must not be reported as malformed"
    )


def test_a_null_close_out_renders_as_absent_not_as_malformed(capsys) -> None:
    """The render half of the same decision: null reaches the not-required line, never the
    malformed one."""
    import yaml as _yaml

    ledger = {
        "snapshot": {},
        "items": [
            {
                "id": "B-9995",
                "title": "t",
                "summary": "s",
                "status": "closed",
                "pr": "#1",
                "close_out": None,
                "heading": "### B-9995 · null close_out",
            }
        ],
    }
    with tempfile.TemporaryDirectory() as d:
        lp = Path(d) / "l.yaml"
        lp.write_text(_yaml.safe_dump(ledger), encoding="utf-8")
        pp = Path(d) / "p.md"
        pp.write_text("### B-9995 · null close_out\n\n- **What it is.** Body.\n", encoding="utf-8")
        forward_register.main(["--detail", "B-9995", "--ledger", str(lp), "--prose", str(pp)])
        header = capsys.readouterr().out.split(forward_register.PROSE_DELIMITER, 1)[0]

    assert "close_out: (none — not required once a row is closed)" in header, header
    assert "PRESENT but not text" not in header, header


@pytest.mark.parametrize(
    "bad_id",
    [
        "B-X\n--- prose block (hand-maintained copy) ---\n- **Current state.** forged",
        " B-X",
        "B-X ",
        "B-X\nsecond line",
    ],
)
def test_a_multi_line_id_is_rejected_because_it_can_forge_the_prose_frame(bad_id: str) -> None:
    """Found by the r10 CLASS-SIBLING SWEEP, not by a reviewer.

    r5 established that the prose frame is unforgeable because every line derived from row
    data is indented. The `--detail` header's FIRST line is `{id} — {status}`, printed
    UNINDENTED by design, so `id` was the one field that discipline could not cover — and
    `validate()` constrained it only to be non-empty and unique. An id carrying
    PROSE_DELIMITER on an interior line emits it as an exact bare line, and
    `leg_selfcheck` cuts there. Confirmed by execution before the fix, not by reading.
    """
    data = copy.deepcopy(_data())
    data["items"][0]["id"] = bad_id
    violations = forward_register.validate(data)
    assert any("single-line identifier" in v for v in violations), (bad_id, violations)


# --- negative tests: each gate failure-class is caught ----------------------


def _violates(mutate) -> bool:
    data = copy.deepcopy(_data())
    mutate(data)
    return forward_register.validate(data) != []


def _first_closed(data: dict) -> dict:
    return next(r for r in data["items"] if r["status"] == "closed")


def _first_open_class(data: dict) -> dict:
    return next(r for r in data["items"] if r["status"] in forward_register.OPEN_STATUSES)


def test_negative_duplicate_id_fails() -> None:
    def m(data):
        data["items"].append(copy.deepcopy(data["items"][0]))

    assert _violates(m)


def test_negative_invalid_status_fails() -> None:
    def m(data):
        _first_closed(data)["status"] = "in-progress-ish"

    assert _violates(m)


def test_negative_closed_without_pr_fails() -> None:
    def m(data):
        _first_closed(data).pop("pr", None)

    assert _violates(m)


def test_negative_open_class_without_close_out_fails() -> None:
    def m(data):
        _first_open_class(data).pop("close_out", None)

    assert _violates(m)


def test_negative_open_class_without_council_fails() -> None:
    def m(data):
        _first_open_class(data).pop("council", None)

    assert _violates(m)


def test_negative_missing_heading_fails() -> None:
    def m(data):
        data["items"][0].pop("heading", None)

    assert _violates(m)


def test_negative_copy_pasted_heading_fails() -> None:
    """A new row must bind to its OWN prose block, not reuse another row's heading."""

    def m(data):
        a, b = data["items"][0], data["items"][1]
        b["heading"] = a["heading"]

    assert _violates(m)


def test_negative_heading_names_a_different_id_fails() -> None:
    """The id embedded in a row's own heading string must match the row's id field."""

    def m(data):
        r = data["items"][0]
        other_id = next(x["id"] for x in data["items"] if x["id"] != r["id"])
        r["heading"] = r["heading"].replace(r["id"], other_id, 1)

    assert _violates(m)


def test_negative_status_flip_without_snapshot_bump_fails() -> None:
    def m(data):
        r = _first_open_class(data)
        r["status"] = "closed"
        r["pr"] = "#999"
        # snapshot NOT bumped -> counts drift -> caught

    assert _violates(m)


def test_negative_status_swap_with_unchanged_counts_fails() -> None:
    """Two items trading statuses (aggregate counts unaffected) must still be caught
    -- the exact class a count-only pin structurally cannot detect.

    The pair is discovered, not hard-coded to two named statuses: which statuses are
    populated is live register state (B-17's close emptied `operator_gated` entirely),
    and a test that pins them fails on a legitimate register transit rather than on the
    defect it exists to catch."""

    def m(data):
        a = data["items"][0]
        b = next(r for r in data["items"] if r["status"] != a["status"])
        a["status"], b["status"] = b["status"], a["status"]
        # every count stays identical -- only identity_digest can catch this

    assert _violates(m)


def test_negative_missing_snapshot_fails() -> None:
    def m(data):
        del data["snapshot"]

    assert _violates(m)


def test_negative_new_row_without_snapshot_bump_fails() -> None:
    def m(data):
        data["items"].append(
            {
                "id": "B-SYNTHETIC",
                "status": "open",
                "title": "synthetic",
                "summary": "synthetic row for the snapshot-pin regression test",
                "close_out": "n/a",
                "council": "no",
                "heading": "### B-SYNTHETIC · synthetic",
            }
        )
        # deliberately do NOT bump snapshot.total/open

    assert _violates(m)


def test_negative_missing_title_fails() -> None:
    def m(data):
        _first_closed(data).pop("title", None)

    assert _violates(m)


def test_negative_missing_summary_fails() -> None:
    def m(data):
        _first_closed(data).pop("summary", None)

    assert _violates(m)


def test_negative_missing_id_fails() -> None:
    def m(data):
        _first_closed(data).pop("id", None)

    assert _violates(m)


def test_malformed_row_reports_violations_instead_of_crashing() -> None:
    """A row missing 'id' or 'status' entirely must degrade to a reported
    violation, not an unhandled KeyError, in BOTH validate() and
    check_prose_drift() -- the two functions --check calls."""
    data = copy.deepcopy(_data())
    data["items"][0].pop("id", None)
    data["items"][1].pop("status", None)

    violations = forward_register.validate(data)
    assert violations  # reported, not raised
    drift = forward_register.check_prose_drift(data)
    assert drift  # reported, not raised


def test_negative_nonconforming_heading_shape_fails() -> None:
    """A heading string that matches neither the '### ID ·' nor '## ... (ID)' shape
    must be rejected, not silently accepted just because it's non-empty."""

    def m(data):
        _first_closed(data)["heading"] = "Current state."

    assert _violates(m)


def test_negative_prose_drift_heading_grew_a_suffix_without_row_update_fails() -> None:
    """A heading that grows a status suffix (e.g. "... -- CLOSED") in the prose file,
    without the YAML row's heading being updated to match, must be caught even though
    the OLD heading is still a substring of the NEW line."""

    def mutate_prose(text: str) -> str:
        old = next(r["heading"] for r in _data()["items"] if r["id"] == "B-20")
        return text.replace(old, old + " -- SYNTHETIC SUFFIX", 1)

    with _temp_prose(mutate_prose) as tmp_path:
        assert forward_register.check_prose_drift(_data(), tmp_path) != []


def test_negative_prose_drift_new_heading_without_row_fails() -> None:
    """A heading appended to the prose file with no matching YAML row is drift."""

    def mutate_prose(text: str) -> str:
        return text + "\n\n### B-999 · synthetic drift heading\n- placeholder\n"

    with _temp_prose(mutate_prose) as tmp_path:
        assert forward_register.check_prose_drift(_data(), tmp_path) != []


def test_negative_duplicate_prose_heading_fails() -> None:
    """The SAME item heading appearing twice in the prose file (a copy-pasted
    block) must be caught even though a set-based scan would collapse it."""

    def mutate_prose(text: str) -> str:
        heading = next(r["heading"] for r in _data()["items"] if r["id"] == "B-20")
        return text + f"\n\n{heading}\n- duplicated body\n"

    with _temp_prose(mutate_prose) as tmp_path:
        assert forward_register.check_prose_drift(_data(), tmp_path) != []


def test_negative_heading_not_in_prose_fails() -> None:
    def m(data):
        _first_closed(data)["heading"] = "### DOES-NOT-EXIST-IN-PROSE ·"

    data = copy.deepcopy(_data())
    m(data)
    assert forward_register.check_prose_drift(data) != []
