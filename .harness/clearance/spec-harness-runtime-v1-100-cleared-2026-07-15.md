---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.100
cleared_at: 2026-07-15T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-roadmap-continue
back_reference:
  - .harness/class_1_fork_cli_exit_code_paused_status_undefined.md (Q1=A / Q2=ii / Q3=b readings, all filer-recommended)
  - .harness/forward-register.yaml (B-27 entry)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - advisor() pre-implementation grounding (this session) — reviewed the B-24/B-25/B-27 ratification batch before build; confirmed B-24/B-27 as Claude-ratifiable (clear, reversible, filer-recommended, convention-following) and B-25 as requiring a genuine operator gate (split off, not built this arc)
  - direct read of `harness-runtime/src/harness_runtime/cli/app.py` confirming both exit-code call sites (`_CP_STATUS_TO_EXIT_CODE` dict for daemon-client mode; the one-shot `if/elif` chain) previously collapsed `paused` onto the same exit code as `failed`
  - "full test run: `harness-runtime/tests/test_cli_one_shot.py` + `test_cli_daemon_client.py` — 28/28 passed, including the 2 new tests added by this fix (`test_b27_workflow_paused_status_exits_five`; the daemon-mode parametrize case `('paused', EXIT_PAUSED)`)"
  - ruff format + ruff check clean on all touched files
supersedes: null
superseded_by: null
---

# Clearance — `Spec Harness Runtime v1.100`

v1.100 closes the `B-27` fork: §14.18.2's exit-code mapping table never assigned `RunResult.status == PAUSED` a disposition. When `'partial'` was added to the status `Literal` at an earlier spec revision, the author explicitly extended §14.18.2's row-1 trigger set to include it; when `'paused'` was added (earlier in the same lineage, per that revision's own "mirroring v1.45's `paused`" framing), no equivalent §14.18.2 amendment happened. Production code (`harness-runtime/src/harness_runtime/cli/app.py`) inherited the gap: both the one-shot `if/else` chain and the daemon-mode `_CP_STATUS_TO_EXIT_CODE` dict fell through to `EXIT_WORKFLOW_FAIL` (exit `1`) for a `paused` run — indistinguishable by exit code from a genuine `failed` run, even though `paused` is a non-terminal outcome distinct in kind from a hard failure.

This delta adds a NEW §14.18.2 row: exit code `5` / `PAUSED` / triggered by `RunResult.status == PAUSED`. `cli/app.py` gains `EXIT_PAUSED = 5`; both call sites now dispatch `paused` to it explicitly rather than falling through to the generic-failure branch. `RunResult.status`'s `Literal` enum itself is unchanged — only the exit-code mapping gained a row, matching the fork's Q2=ii (spec + CLI kept in sync) recommendation. Per Q3, a documentation-only note is recorded: a future CLI `resume` subcommand should honor this same exit-code convention once one is authored — no `resume` subcommand exists yet, and none is added by this delta.

**Naming correction (out-of-family `just codex-review` round 1).** The first pass named the constant `EXIT_PAUSED_RESUMABLE` / row `PAUSED_RESUMABLE`, implying every `paused` run carries a `PauseSnapshot` resumable via `resume()`. Codex correctly flagged that `workflow_driver.py:4224-4248` and `:4259-4282` (`WAL_SEGMENT`/`RECONCILER_LOOP` engine-native recovery-loop pauses) intentionally return `RunStatus.PAUSED` with `pause_snapshot=None` — their durable state lives in the engine's own segment log / reconciler store, not the workflow-layer snapshot, so `api.resume(snapshot)` cannot resume them; a CLI/automation author relying on the `RESUMABLE` name could attempt an impossible resume call. Renamed to the non-overclaiming `EXIT_PAUSED`/`PAUSED`.

**Follow-on correction (out-of-family `just codex-review` round 3).** The round-1 fix's own replacement text asserted engine-native pauses ARE currently resumable via "a plain re-invocation of `harness run`" — also false, and P1-flagged (potentially unsafe: repeating committed side effects). Codex traced `harness-runtime/src/harness_runtime/lifecycle/mcp_server.py:357`: `run_id = _resume_snapshot.run_id if _resume_snapshot is not None else uuid.uuid4().hex` — a plain re-invocation with no snapshot generates a FRESH run_id every time, and the engine recovery loop's `capture_pause` records key on `(workflow_id, run_id)` (confirmed at `workflow_driver.py:4234`, `:4270` — both pass `run_id=run_id`, not `workflow_id` alone). A fresh run_id cannot locate the prior pause record; re-invocation starts an unrelated new run, risking re-execution of already-committed steps rather than resuming anything. §14.18.2's row 5 is corrected to state plainly that engine-native pauses have NO safe resume path at v1.100, and that a future `resume` subcommand must solve run_id recovery for the snapshotless case before re-invocation can be documented or implemented as a resume mechanism.

**Ratification note.** This fork was ratified without an operator `AskUserQuestion` round-trip, per explicit operator direction this session ("continue autonomously, no HIL ... pick up B-24/B-25/B-27's fork docs for ratification") — the filer's recommended readings (Q1=A, Q2=ii, Q3=b) were adopted as-is after confirming via `advisor()` that this fork (unlike the sibling `B-25`, which was NOT built this arc) is mechanical, reversible, and does not carry an irreversible production-security-posture tradeoff a non-coding operator could not audit after the fact.

## Notes

- Phase 7 consumers may rely on this version (v1.100) as canonical for the §14.18.2 exit-code mapping table.
- `B-27`'s forward-register row (`.harness/forward-register.yaml` + `.harness/post-phase-8-forward-register.md`) is marked closed in the same PR, citing this clearance marker.
- Root `CLAUDE.md` §2.3's Runtime spec pointer is intentionally NOT bumped inline here — per observed workspace convention (the CP spec pointer has similarly lagged behind the live `Spec_Control_Plane_v1_100.md` head), that pointer is refreshed in a separate periodic batch pass, not on every individual spec delta.
- See `.harness/clearance/README.md` for marker discipline.
