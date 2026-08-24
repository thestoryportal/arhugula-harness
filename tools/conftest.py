"""B-208 — keep the SHARED loop ledger unreachable from a `tools/` test process.

`loop_status_path()` (tools/hooks/loop_lib.sh) resolves the ledger from the ambient
environment and falls back to the operator's real
`~/.gstack/projects/<project>/loop_status.md` whenever `HARNESS_LOOP_STATUS_PATH` is
unset -- the default state of every pytest process. Any test reaching a real emit path
therefore appended real `DEFERRED-HIL` rows to the venue the SessionStart hook reads,
where a synthetic `pr-1` gate nags forever and only a hand-written `RESOLVED-HIL`
clears it. It is append-only by contract (C-HE-09 §2), so the debris is not removable
after the fact: by the time this landed, 6288 of the ledger's 6589 rows (1.07 MB) were
`lane=A` fixtures against 82 real-lane rows.

Isolating per test FILE is what the workspace tried and what drifted -- two files
remember (`test_arc_exit_report.py`, `test_review_wrapper.py`), `test_merge_door.py`
does not, and a file written tomorrow will not either. `emit_loop_row` also shells out
to bash and several door tests drive `merge_door.py` as a real SUBPROCESS, so
monkeypatching the Python seam cannot reach them; only the inherited environment can.
Hence one enforcement point for the whole directory: no `tools/` test can reach the
production ledger by omission.

This lives HERE and not in the root conftest deliberately. Every producer of loop rows
is under `tools/` (`reservations.emit_loop_row`, its `merge_door` callers, the hook
suites -- which already isolate themselves); no `harness-*` package writes the ledger.
A root-level redirect additionally leaks a `HARNESS_*` name into every axis suite, and
`harness-runtime/tests/test_config_loader.py::test_env_defaults_to_os_environ_when_none`
asserts that NO `HARNESS_*` variable is set, because RuntimeConfig's env loader consumes
that namespace. Enforcing at the joint where the concern actually lives keeps both
invariants true instead of trading one for the other.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Iterator
from pathlib import Path

import pytest

_VENUE_ENV = "HARNESS_LOOP_STATUS_PATH"


@pytest.fixture(scope="session", autouse=True)
def _isolated_loop_status_venue() -> Iterator[Path]:
    """Redirect the ledger for the whole `tools/` session, then take the venue with it.

    Set unconditionally rather than only-if-unset: no test here legitimately writes the
    real venue, so an ambient value pointing at it is a misconfiguration, not an intent
    worth honouring. A per-test `monkeypatch.setenv` still wins -- it runs later and is
    undone first.

    The directory is removed on teardown rather than left to the OS. `mkdtemp` with no
    owner is how B-207's sibling leak got filed; a fixture already has the teardown, so
    there is no reason to accrue one temp tree per test run.
    """
    root = Path(tempfile.mkdtemp(prefix="harness-loop-status-"))
    previous = os.environ.get(_VENUE_ENV)
    os.environ[_VENUE_ENV] = str(root / "loop_status.md")
    try:
        yield root
    finally:
        if previous is None:
            os.environ.pop(_VENUE_ENV, None)
        else:
            os.environ[_VENUE_ENV] = previous
        # Swallowing here is deliberate and bounded: the tree is ours, lives under
        # TMPDIR, and nothing downstream reads it. Raising would turn a cleanup hiccup
        # into a red session, which is the wrong trade for a directory the OS reaps
        # anyway -- the leak this closes is about accrual, not correctness.
        shutil.rmtree(root, ignore_errors=True)
