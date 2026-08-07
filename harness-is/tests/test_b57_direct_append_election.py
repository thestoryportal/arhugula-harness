"""U-IS-11 ACs #14–#20 — C-IS-07 §7.6.1 per-call-site writer-owned ELECTION on
DIRECT append surfaces (IS spec v1.13, `B-57` ratified Reading A; IS plan v2.9
§2.1 + §2.3 + §2.4).

The load-bearing witnesses of the `B-57` impl leg live here:

- the **two-OS-process contention witness** (§2.4 first bullet) — the direct
  analogue of `B-112`'s own 12/20 repro, made DETERMINISTIC by marker-staging
  the overtake instead of racing for it, plus a genuinely simultaneous
  40-vs-40 contention test so the race is non-vacuous;
- the **non-electing default-preservation NEGATIVE witness** (AC #15) — the one
  that proves the election did NOT become a default;
- the **per-site table conformance check** (AC #17);
- the **`restored_at` decoupling pin** (AC #20, row 1).

Every witness here is PD-8 mutation-probed; each docstring names the reversion
that turns it RED.
"""

from __future__ import annotations

import subprocess
import sys
import time
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest
from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.shadow_git_checkpoint import (
    CheckpointTriggerContext,
    create_shadow_git_checkpoint,
)
from harness_is.shadow_git_rollback import RollbackStatus, rollback_to_checkpoint
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_write import (
    WRITER_OWNED_TIMESTAMP,
    EntryPayload,
    NonMonotonicTimestampError,
    WriteKey,
    append_ledger_entry,
    read_ledger,
)
from harness_is.workload_manifest_opt_in_schema import CheckpointCadence

_ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="agent-b57")
_RUN = Identifier("wf-run-b57")


def _handle(path: Path) -> JsonlLedgerHandle:
    return JsonlLedgerHandle(canonical_path=path, exists=False, entry_count=0)


def _append(handle: JsonlLedgerHandle, tag: str, stamp: datetime) -> None:
    append_ledger_entry(
        handle,
        EntryPayload(
            action_id=Identifier(f"act-{tag}"),
            idempotency_key=Identifier(f"idem-{tag}"),
            actor=_ACTOR,
            timestamp=stamp,
        ),
        WriteKey(
            thread_id=_RUN,
            step_id=Identifier(f"step-{tag}"),
            idempotency_key=Identifier(f"idem-{tag}"),
        ),
    )


# ---------------------------------------------------------------------------
# §2.4 bullet 1 — the two-OS-process contention witness.
# ---------------------------------------------------------------------------

#: The child half of the two-process witness. A REAL second OS process — spawned
#: via `sys.executable`, not a thread and not a fork of this interpreter's state.
#:
#: Two modes:
#:
#: - ``overtake`` — samples its timestamp FIRST, announces the sample, then
#:   WAITS on a `go` marker the parent writes only after its own, later-sampled
#:   entry is durable. That is `B-57`'s named failure staged DETERMINISTICALLY
#:   (sampled-first / appended-second) rather than raced for OR timed. Both
#:   processes still go through the real `flock`; what is removed is the
#:   coin-flip, not the lock.
#: - ``hammer`` — appends a burst of electing entries as fast as it can while
#:   the parent does the same, which is the genuinely CONTENDED half: it makes
#:   the race non-vacuous instead of assuming it.
#:
#: Why markers and not a parent-held lock: within one process a nested
#: `cross_process_write_lock` opens a SECOND fd on the same canonical file, and
#: `flock` contends between separate fds even within one process
#: (`cross_process_ledger_lock.py:120`) — so a parent holding the lock across
#: the overtake would deadlock against its own append. Only the per-directory
#: face is refcount-reentrant. Grounded by direct read + an observed hang, not
#: assumed.
_CHILD_SOURCE = """\
import json, sys, time
from datetime import UTC, datetime
from pathlib import Path

from harness_is.jsonl_event_ledger_lifecycle import JsonlLedgerHandle
from harness_is.state_ledger_entry_schema import Actor, ActorClass, Identifier
from harness_is.state_ledger_write import (
    WRITER_OWNED_TIMESTAMP,
    EntryPayload,
    NonMonotonicTimestampError,
    WriteKey,
    append_ledger_entry,
)

mode = sys.argv[1]
ledger_path = Path(sys.argv[2])
marker = Path(sys.argv[3])
elects = sys.argv[4] == "elect"
ACTOR = Actor(actor_class=ActorClass.AGENT, actor_id="agent-b57")
handle = JsonlLedgerHandle(canonical_path=ledger_path, exists=False, entry_count=0)


def append(tag, stamp):
    append_ledger_entry(
        handle,
        EntryPayload(
            action_id=Identifier("act-" + tag),
            idempotency_key=Identifier("idem-" + tag),
            actor=ACTOR,
            timestamp=stamp,
        ),
        WriteKey(
            thread_id=Identifier("wf-run-b57"),
            step_id=Identifier("step-" + tag),
            idempotency_key=Identifier("idem-" + tag),
        ),
    )


if mode == "overtake":
    # 1. Sample FIRST — before queuing for the lock. This is the whole of
    #    B-57's named failure: an instant captured OUTSIDE the writer's
    #    serialization point, which a later-arriving writer can overtake.
    sampled = datetime.now(UTC)
    # 2. Announce the sample so the parent can overtake deterministically.
    marker.write_text(sampled.isoformat())
    # 3. Wait for the parent's OWN, later-sampled entry to be durable. A
    #    marker, never a sleep: a fixed delay would make the ordering identity
    #    a timing bet a loaded CI runner could lose, and the identity is the
    #    whole point of this witness.
    while not (marker.parent / "go.marker").exists():
        time.sleep(0.005)
    try:
        append("child", WRITER_OWNED_TIMESTAMP if elects else sampled)
    except NonMonotonicTimestampError:
        print(json.dumps({"outcome": "refused", "error": "NonMonotonicTimestampError",
                          "sampled": sampled.isoformat()}))
        raise SystemExit(3)
    print(json.dumps({"outcome": "appended", "sampled": sampled.isoformat()}))
else:  # "hammer" — genuine simultaneous contention on one ledger root.
    marker.write_text("ready")
    while not (marker.parent / "go.marker").exists():
        time.sleep(0.005)
    for i in range(40):
        append("child-%02d" % i, WRITER_OWNED_TIMESTAMP if elects else datetime.now(UTC))
    print(json.dumps({"outcome": "appended", "count": 40}))
"""


def _spawn_child(
    mode: str, ledger_path: Path, marker: Path, *, elects: bool
) -> subprocess.Popen[str]:
    script = ledger_path.parent / "b57_child_appender.py"
    script.write_text(_CHILD_SOURCE, encoding="utf-8")
    return subprocess.Popen(
        [
            sys.executable,
            str(script),
            mode,
            str(ledger_path),
            str(marker),
            "elect" if elects else "caller",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _await_marker(marker: Path, child: subprocess.Popen[str], what: str) -> None:
    deadline = datetime.now(UTC) + timedelta(seconds=60)
    while not marker.exists():
        if child.poll() is not None:
            stdout, stderr = child.communicate()
            pytest.fail(f"child exited before {what}: {stdout}{stderr}")
        if datetime.now(UTC) > deadline:
            child.kill()
            pytest.fail(f"child never reached {what}")
        time.sleep(0.005)


def _run_two_process_overtake(tmp_path: Path, *, elects: bool) -> subprocess.CompletedProcess[str]:
    """Stage the `B-57` overtake across two real OS processes, deterministically.

    The child samples first and appends second; the parent samples second and
    appends first. Both go through the real cross-process `flock`; the ordering
    is STAGED via markers in BOTH directions rather than raced for, because
    `flock` specifies no acquisition ordering and a raced (or sleep-timed)
    formulation is flaky in both directions — the lesson already recorded on
    `test_rollback_cross_process_lock_prevents_lost_concurrent_append`.
    `B-112` reproduced this same ordering 12/20 by racing; this makes it 20/20,
    with no timing assumption a loaded CI runner could invalidate. The genuinely
    SIMULTANEOUS half is a separate test below.
    """
    ledger_path = tmp_path / "state.jsonl"
    marker = tmp_path / "child-sampled.marker"
    handle = _handle(ledger_path)
    _append(handle, "seed", datetime.now(UTC))

    child = _spawn_child("overtake", ledger_path, marker, elects=elects)
    _await_marker(marker, child, "its timestamp sample")
    # The child has sampled and is waiting. Overtake it with a LATER instant,
    # then release it — so it provably sampled first and appends second.
    _append(handle, "parent", datetime.now(UTC))
    (tmp_path / "go.marker").write_text("go")

    stdout, stderr = child.communicate(timeout=120)
    return subprocess.CompletedProcess(child.args, child.returncode, stdout, stderr)


def test_electing_direct_append_survives_lock_race_overtake(tmp_path: Path) -> None:
    """§2.4 bullet 1 — the ELECTING half, the load-bearing witness of this arc.

    Two real OS processes write one ledger root. The waiter that sampled FIRST
    but appends SECOND, HAVING ELECTED, is not refused: its persisted instant is
    the writer's own, taken inside the serialization point at the real append
    moment, so sampling order IS physical-append order for it, and both entries
    persist with non-decreasing timestamps in physical-append order.

    The assertions are on the LOCK/ORDERING IDENTITY, never on a timing
    threshold: the child's pre-queue sample is strictly earlier than the
    overtaking parent's entry (without which the staging would be vacuous), the
    child's entry is physically LAST, and its persisted instant is NOT its own
    sample.

    PD-8: the RED half is not hypothetical — it is
    `test_non_electing_direct_append_is_refused_after_lock_race_overtake`
    below: the identical staging with the election reverted at the site under
    test, which FAILS with `NonMonotonicTimestampError`. The two tests differ by
    exactly one payload value.
    """
    result = _run_two_process_overtake(tmp_path, elects=True)
    assert result.returncode == 0, f"electing child was refused: {result.stdout}{result.stderr}"

    entries = read_ledger(_handle(tmp_path / "state.jsonl"))
    assert [e.action_id for e in entries] == ["act-seed", "act-parent", "act-child"], (
        "the child must have appended SECOND (after the overtaking parent entry)"
    )

    child_pre_queue_sample = datetime.fromisoformat(
        (tmp_path / "child-sampled.marker").read_text(encoding="utf-8")
    )
    parent_entry, child_entry = entries[1], entries[2]
    assert child_pre_queue_sample < parent_entry.timestamp, (
        "the staging is vacuous unless the child genuinely sampled BEFORE the overtaker"
    )
    assert child_entry.timestamp >= parent_entry.timestamp, (
        "the electing child's persisted instant must be writer-owned, in append order"
    )
    assert child_entry.timestamp > child_pre_queue_sample, (
        "the electing child's persisted instant must NOT be its own pre-queue sample"
    )
    assert [e.timestamp for e in entries] == sorted(e.timestamp for e in entries)


def test_non_electing_direct_append_is_refused_after_lock_race_overtake(
    tmp_path: Path,
) -> None:
    """§2.4 bullet 1 — the RED half / PD-8 mutation probe, run as a real test.

    Identical staging with the election reverted at the site under test (the
    child supplies its own pre-queue sample). It is REFUSED with
    `NonMonotonicTimestampError` — `B-57`'s named failure, reproduced
    deterministically. This is what makes the green witness above load-bearing,
    and it doubles as a second demonstration that non-electing direct producers
    keep caller-supplied detect-then-refuse semantics (AC #15).
    """
    result = _run_two_process_overtake(tmp_path, elects=False)
    assert result.returncode == 3, (
        f"the non-electing child should have been REFUSED, got rc={result.returncode}: "
        f"{result.stdout}{result.stderr}"
    )
    assert '"outcome": "refused"' in result.stdout
    assert "NonMonotonicTimestampError" in result.stdout

    entries = read_ledger(_handle(tmp_path / "state.jsonl"))
    assert [e.action_id for e in entries] == ["act-seed", "act-parent"], (
        "the refused append must not have persisted"
    )


@pytest.mark.skipif(sys.platform == "win32", reason="POSIX flock serializes these writers")
def test_electing_appends_never_invert_under_real_two_process_contention(
    tmp_path: Path,
) -> None:
    """§2.4 bullet 1's *"run it enough times to make the race non-vacuous"* half.

    Where the staged witness above pins the ORDERING IDENTITY deterministically,
    this one supplies the genuine simultaneity: two real OS processes hammer 40
    electing appends each into one ledger root, released together off a shared
    `go` marker, with no coordination beyond the writer's own lock. Zero
    refusals, all 80 entries durable, and the persisted timestamps
    non-decreasing in physical-append order — by construction, not by luck.

    PD-8: switch either side to caller-supplied sampling (`elects=False`) and
    refusals appear as soon as the two interleave — which is exactly what
    `test_non_electing_direct_append_is_refused_after_lock_race_overtake`
    demonstrates deterministically.
    """
    ledger_path = tmp_path / "state.jsonl"
    marker = tmp_path / "child-ready.marker"
    handle = _handle(ledger_path)
    _append(handle, "seed", datetime.now(UTC))

    child = _spawn_child("hammer", ledger_path, marker, elects=True)
    _await_marker(marker, child, "its ready signal")
    (tmp_path / "go.marker").write_text("go")
    for i in range(40):
        _append(handle, f"parent-{i:02d}", WRITER_OWNED_TIMESTAMP)

    stdout, stderr = child.communicate(timeout=120)
    assert child.returncode == 0, f"contending child failed: {stdout}{stderr}"

    entries = read_ledger(handle)
    assert len(entries) == 81, "every append from both processes must be durable"
    timestamps = [e.timestamp for e in entries]
    assert timestamps == sorted(timestamps), (
        "electing appends must never invert under real two-process contention"
    )


# ---------------------------------------------------------------------------
# AC #15 — default preservation, demonstrated NEGATIVELY.
# ---------------------------------------------------------------------------


def test_non_electing_direct_append_keeps_caller_supplied_semantics(tmp_path: Path) -> None:
    """AC #15 — the witness that proves the election did NOT become a default.

    For a NON-electing direct producer the §7.6 `"Surfaces that do NOT change"`
    paragraph still holds BYTE-VERBATIM: (a) the persisted `timestamp` IS the
    caller-supplied value, and (b) an inversion on a non-electing direct path
    is still refused with `NonMonotonicTimestampError`.

    PD-8: make writer-owned sampling unconditional on the direct path (drop the
    `entry_payload.timestamp == WRITER_OWNED_TIMESTAMP` guard in
    `append_ledger_entry`) and BOTH halves fail — (a) because the persisted
    value stops being the caller's, (b) because the inversion stops being
    detectable at all.
    """
    handle = _handle(tmp_path / "state.jsonl")
    caller_instant = datetime(2026, 5, 19, 12, 0, 0, tzinfo=UTC)

    # (a) the caller's own value is what persists — byte-verbatim.
    _append(handle, "first", caller_instant)
    [entry] = read_ledger(handle)
    assert entry.timestamp == caller_instant

    # (b) an inversion on a non-electing direct path is still refused.
    with pytest.raises(NonMonotonicTimestampError):
        _append(handle, "inverted", caller_instant - timedelta(seconds=1))
    assert len(read_ledger(handle)) == 1

    # ... and a non-electing append that does NOT invert still lands verbatim,
    # so the refusal above is a real discriminator and not a blanket rejection.
    later = caller_instant + timedelta(seconds=1)
    _append(handle, "second", later)
    assert [e.timestamp for e in read_ledger(handle)] == [caller_instant, later]


def test_electing_and_non_electing_producers_coexist_on_one_ledger(tmp_path: Path) -> None:
    """The §7.6.1 MIXED-POPULATION property, positively witnessed.

    Election is per call site, so both kinds of producer write to one chain:
    the non-electing entry keeps its caller-supplied instant verbatim while the
    electing entry beside it carries the writer's. This is the shape that makes
    the AC #15 default preservation true in the presence of the conversions —
    not merely true in a ledger where nobody elects.
    """
    handle = _handle(tmp_path / "state.jsonl")
    caller_instant = datetime(2026, 5, 19, 12, 0, 0, tzinfo=UTC)
    _append(handle, "non-electing", caller_instant)

    before = datetime.now(UTC)
    _append(handle, "electing", WRITER_OWNED_TIMESTAMP)
    after = datetime.now(UTC)

    non_electing, electing = read_ledger(handle)
    assert non_electing.timestamp == caller_instant
    assert electing.timestamp != WRITER_OWNED_TIMESTAMP
    assert before <= electing.timestamp <= after


# ---------------------------------------------------------------------------
# AC #20 — row 1's `restored_at` decoupling pin.
# ---------------------------------------------------------------------------


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=True
    ).stdout.strip()


def test_rollback_restored_at_decoupled_from_persisted_ledger_timestamp(
    tmp_path: Path,
) -> None:
    """AC #20 — the decoupling row 1's election introduces, pinned explicitly.

    `RollbackResult.restored_at` keeps the caller-sampled instant (`now` at
    `shadow_git_rollback.py:93`, taken before the git checkout); the persisted
    ledger entry now carries the WRITER's later sample. The two are PERMITTED
    to differ and now honestly mean different things — *when the rollback
    completed* vs *when the entry was appended*. Asserted, so a later reader
    cannot mistake the divergence for a defect.

    PD-8: revert the row-1 election and the strict inequality below fails —
    the two values become identical.
    """
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@harness.local")
    _git(repo, "config", "user.name", "harness-test")
    (repo / "app.py").write_text("v1\n")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "base")

    handle = _handle(repo / "state.jsonl")
    _append(handle, "pre", datetime(2026, 5, 16, 1, tzinfo=UTC))

    checkpoint = create_shadow_git_checkpoint(
        repository_root=repo,
        workflow_run_id=_RUN,
        trigger_context=CheckpointTriggerContext(cadence=CheckpointCadence.PER_STEP),
    )

    (repo / "app.py").write_text("v2-dirty\n")
    result = rollback_to_checkpoint(
        repository_root=repo,
        ledger_handle=handle,
        checkpoint_id=checkpoint.checkpoint_id,
        workflow_run_id=_RUN,
    )
    assert result.status is RollbackStatus.RESTORED
    assert result.restored_at is not None

    rollback_entry = next(e for e in read_ledger(handle) if e.action_id.startswith("rollback:"))
    # Both values asserted explicitly, and asserted to be PERMITTED to differ:
    # `restored_at` is the pre-checkout caller sample, the ledger timestamp is
    # the writer's post-checkout sample taken inside `_WRITE_LOCK`.
    assert rollback_entry.timestamp > result.restored_at, (
        "the persisted ledger instant must be the writer's LATER sample, not `restored_at`"
    )
    assert rollback_entry.timestamp != WRITER_OWNED_TIMESTAMP, (
        "the sentinel must have resolved to a real instant"
    )


# ---------------------------------------------------------------------------
# AC #17 — per-site table conformance.
# ---------------------------------------------------------------------------

#: The AUDITABLE ROSTER — production DIRECT-append sites that stamp the
#: sentinel, keyed by repo-relative module path with the number of stamps.
#:
#: Rows 1-9 + 11 are IS plan v2.9 §2.1's TEN `ELECT` rows; rows 12-13 are its
#: two injection-caveat rows, resolved ELECT at this impl leg per AC #18. The
#: `sub_agent_dispatch` entry is NOT a §7.6.1 election at all — it is the
#: PRE-EXISTING B-48 rounds-28/29 §7.6 scope-widening carve-out, listed so the
#: check is exhaustive over the tree rather than over this arc's diff.
_SENTINEL_ROSTER: dict[str, int] = {
    # row 1
    "harness-is/src/harness_is/shadow_git_rollback.py": 1,
    # rows 2, 3, 4
    "harness-cp/src/harness_cp/pause_resume_protocol.py": 3,
    # rows 5, 6
    "harness-cp/src/harness_cp/workflow_driver.py": 2,
    # row 7
    "harness-cp/src/harness_cp/workload_binding_engine_class_selection.py": 1,
    # row 8
    "harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py": 1,
    # row 9 (the election is at the SAMPLING caller, not the shared composer)
    "harness-cp/src/harness_cp/per_step_override_evaluator.py": 1,
    # row 11
    "harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py": 1,
    # row 12 — injection-caveat, resolved ELECT
    "harness-runtime/src/harness_runtime/lifecycle/audit_writer.py": 1,
    # row 13 — injection-caveat, resolved ELECT
    "harness-runtime/src/harness_runtime/lifecycle/cost_attribution_f2_write.py": 1,
    # NOT §7.6.1 — the B-48 §7.6 scope-widening carve-out (pre-dates this arc)
    "harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py": 1,
}

#: IS plan v2.9 §2.1 row 14 — RETAINS caller-supplied semantics (EVENT time).
_RETAIN_SITE = "harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py"
#: IS plan v2.9 §2.1 row 10 / §2.2 — DEFERRED, production-UNREACHABLE.
_DEFER_SITE = "harness-cp/src/harness_cp/sibling_ledger_entry_composition.py"

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _sentinel_stamps_by_module() -> dict[str, int]:
    """Every production `timestamp=WRITER_OWNED_TIMESTAMP` payload stamp.

    Scans `harness-*/src/**/*.py` only — tests are out of scope (§7.6.1's
    roster governs PRODUCERS; a test explicitly opting in changes no
    producer's semantics, the adjudication already recorded on register row
    `B-112`). The drain path's `model_copy(update={"timestamp": ...})` form at
    `workflow_driver` is deliberately NOT matched: it is the §7.6 buffered
    surface, not a §7.6.1 direct-surface election.
    """
    found: dict[str, int] = {}
    for src_dir in sorted(_REPO_ROOT.glob("harness-*/src")):
        for module in sorted(src_dir.rglob("*.py")):
            count = sum(
                1
                for line in module.read_text(encoding="utf-8").splitlines()
                if line.strip() == "timestamp=WRITER_OWNED_TIMESTAMP,"
            )
            if count:
                found[module.relative_to(_REPO_ROOT).as_posix()] = count
    return found


def test_sentinel_electing_sites_match_the_plan_v2_9_roster() -> None:
    """AC #17 — the arc converted EXACTLY the rows §2.1 classifies ELECT.

    A conversion at a site the table does not classify ELECT, or a missed ELECT
    row, fails here. So does a later drive-by conversion by an unrelated arc,
    which is the standing value of this check.

    PD-8: stamp the sentinel at any unclassified production site and this test
    FAILS with that path in the diff.
    """
    assert _sentinel_stamps_by_module() == _SENTINEL_ROSTER


def test_no_production_module_touches_the_sentinel_outside_the_roster() -> None:
    """AC #17, the exhaustive half — the stamp check above matches one exact
    line shape, so on its own a differently-formatted drive-by conversion could
    slip past it. This pins the far coarser property instead: which production
    modules MENTION `WRITER_OWNED_TIMESTAMP` at all, in any form.

    A new module reaching for the sentinel trips this even if it never writes
    the canonical line — at which point it must be classified against IS plan
    v2.9 §2.1 before it can land.
    """
    mentioning = {
        module.relative_to(_REPO_ROOT).as_posix()
        for src_dir in _REPO_ROOT.glob("harness-*/src")
        for module in src_dir.rglob("*.py")
        if "WRITER_OWNED_TIMESTAMP" in module.read_text(encoding="utf-8")
    }
    expected = set(_SENTINEL_ROSTER) | {
        # The sentinel's own definition + the §7.6 drain path that predates
        # §7.6.1, plus one cross-reference in prose.
        "harness-is/src/harness_is/state_ledger_write.py",
        "harness-core/src/harness_core/cross_process_lock_deadline.py",
    }
    assert mentioning == expected


def test_retain_and_defer_sites_do_not_elect() -> None:
    """AC #16 + AC #17 — the two rows that MUST NOT have been converted.

    Row 14 (`as_is_wiring`) carries genuine EVENT time and is barred from
    electing by §7.6.1's eligibility rule. Row 10
    (`sibling_ledger_entry_composition`) is production-UNREACHABLE and per
    §7.6.1 *"acquires no election by default"*.

    Named explicitly rather than left implicit in the roster equality above,
    because these are the two the acceptance criteria call out by name.
    """
    for site in (_RETAIN_SITE, _DEFER_SITE):
        assert "WRITER_OWNED_TIMESTAMP" not in (_REPO_ROOT / site).read_text(encoding="utf-8"), (
            f"{site} must not elect"
        )


def test_defer_site_has_no_production_caller() -> None:
    """§2.2 — row 10's DEFER rests on a MEASURED reachability claim, re-measured
    here rather than trusted.

    `emit_sibling_ledger_entry`'s only non-test occurrences are its definition
    and two docstring mentions; every call site is a test. If a real producer
    ever appears, this test fails and the row is re-classified — which is
    exactly what §7.6.1 prescribes.
    """
    non_test_hits: list[str] = []
    for package in sorted(_REPO_ROOT.glob("harness-*")):
        for module in sorted(package.rglob("*.py")):
            parts = module.relative_to(_REPO_ROOT).parts
            if "tests" in parts or ".venv" in parts:
                continue
            for lineno, line in enumerate(module.read_text(encoding="utf-8").splitlines(), 1):
                if "emit_sibling_ledger_entry" in line:
                    non_test_hits.append(f"{module.relative_to(_REPO_ROOT)}:{lineno}")
    assert non_test_hits == [
        "harness-cp/src/harness_cp/sibling_ledger_entry_composition.py:150",
        "harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py:34",
        "harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py:124",
    ], "row 10's DEFER rests on this seam having no production caller"
