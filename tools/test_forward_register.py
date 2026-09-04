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
    """A closed row carries no `close_out` by design. Printing nothing would be
    indistinguishable from a row whose close_out failed to load, so absence is
    STATED (the gate-cannot-tell-empty-from-unlooked rule applied to a renderer)."""
    row = next(r for r in _data()["items"] if r["id"] == "B-1")
    assert not row.get("close_out"), "fixture assumption: B-1 is closed with no close_out"

    forward_register.main(["--detail", "B-1"])
    out = capsys.readouterr().out
    assert "CANONICAL" in out
    assert "(none" in out


def test_detail_emits_the_delimiter_as_one_bare_unindented_line(capsys) -> None:
    """Pins the PRODUCER half of the contract `tools/leg_selfcheck.py` relies on.

    That consumer tolerates a missing delimiter (`cut = 0`) because injected `detail_fn`
    fakes predate the header. The tolerance is for the TEST SEAM only -- on the real path
    the delimiter is always emitted, and if it ever stopped being, the consumer would
    silently revert to counting the canonical header as prose body: the exact silent
    retirement of the YAML-only-row gate that B-235's consumer fix exists to prevent.
    Nothing else asserts the real CLI's shape, so this test is what closes that loop.
    """
    forward_register.main(["--detail", "B-1"])
    lines = capsys.readouterr().out.splitlines()
    # Exactly one, and BARE -- an indented occurrence is row content, not the frame.
    assert lines.count(forward_register.PROSE_DELIMITER) == 1, lines[:20]
    idx = lines.index(forward_register.PROSE_DELIMITER)
    # The canonical header precedes it; the prose heading follows it.
    assert any(ln.startswith("close_out (CANONICAL") for ln in lines[:idx])
    assert any(ln.startswith("### B-1") for ln in lines[idx + 1 :])


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
    assert any("(none" in ln or "(MISSING" in ln for ln in stated), header


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
