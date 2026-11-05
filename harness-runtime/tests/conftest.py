"""Shared test fixtures for `harness-runtime/tests/` — U-RT-146.

The process-lifetime capacity ledger (`harness_runtime.lifecycle.
sub_agent_dispatch_executor._process_capacity_ledger`) survives across
`api.run()` bootstrap invocations by design (Runtime spec v1.104 §14.8.10.6).
That is exactly the behavior a test session must NOT inherit across test
cases — an autouse, session-wide reset mirrors the existing
`reset_process_drained_for_tests()` precedent at `harness_runtime.drain`
(see `test_drain.py`'s local fixture), lifted to a repo-wide conftest since
any test touching bootstrap/stage_5 or the dispatch executor's adoption path
could otherwise leak occupied/budget state into an unrelated later test.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from harness_runtime.lifecycle.pause_journal_root_resolver import (
    INSTALLATION_STATE,
    STORAGE_UNSELECTED,
)
from harness_runtime.lifecycle.sub_agent_dispatch_executor import (
    reset_capacity_authority_for_tests,
)

from .pause_journal_roots import placed_root  # noqa: F401  (fixture, suite-wide)
from .test_state_placement import world  # noqa: F401  (fixture: placed_root's scratch dir)


@pytest.fixture(autouse=True)
def _isolate_capacity_authority_for_tests() -> Iterator[None]:
    reset_capacity_authority_for_tests()
    yield
    reset_capacity_authority_for_tests()


@pytest.fixture(autouse=True)
def _storage_unselected() -> Iterator[None]:
    """Every test starts from production's unbound pause-journal root (U-RT-160b).

    [LAW:no-shared-mutable-globals] This fixture owns restoration: `reset` returns the variable
    to its pre-test value however many roots the test declared in this context.
    """
    token = INSTALLATION_STATE.set(STORAGE_UNSELECTED)
    yield
    INSTALLATION_STATE.reset(token)
