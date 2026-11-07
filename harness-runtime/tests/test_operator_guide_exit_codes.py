"""Pin the operator guide's exit-code table to the CLI's exit-code constants.

The ``EXIT_*`` constants in ``harness_runtime.cli.app`` are the exit-code contract;
the ``## Exit Codes`` table in ``docs/how-to-operate-runtime.md`` is the operator's map
of it. A code added to either side without the other fails here.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OPERATOR_GUIDE = ROOT / "docs" / "how-to-operate-runtime.md"
# `harness_runtime.cli.app` as an attribute is the Typer instance the package re-exports.
cli_app_mod = importlib.import_module("harness_runtime.cli.app")
TABLE_ROW_RE = re.compile(r"^\| `(\d+)` \| .+ \|$")


def _documented_rows() -> list[tuple[int, str]]:
    section = OPERATOR_GUIDE.read_text(encoding="utf-8").split("\n## Exit Codes\n", 1)[1]
    table = section.split("\n## ", 1)[0]
    return [
        (int(m.group(1)), line) for line in table.splitlines() if (m := TABLE_ROW_RE.match(line))
    ]


def test_operator_guide_lists_exactly_the_cli_exit_codes() -> None:
    # [LAW:one-source-of-truth] the constants are canonical; the table is derived from them.
    cli_codes = {value for name, value in vars(cli_app_mod).items() if name.startswith("EXIT_")}
    documented = [code for code, _ in _documented_rows()]

    assert len(documented) == len(set(documented)), f"duplicate table rows: {documented}"
    assert set(documented) == cli_codes
    assert {cli_app_mod.EXIT_RESUME_REFUSED, cli_app_mod.EXIT_RESUME_CLAIM_REFUSED} == {6, 7}


def test_paused_row_states_which_pauses_have_no_resume() -> None:
    # Spec v1.137 §F row 5(b) and Rule B8 (witness I.12): the operator learns from the paused
    # row that engine-native pauses and pre-root pauses cannot be resumed.
    paused_row = dict(_documented_rows())[cli_app_mod.EXIT_PAUSED]

    assert "Engine-native pauses have no safe resume" in paused_row
    assert "captured before the runtime bound its pause-journal root cannot be resumed" in (
        paused_row
    )
