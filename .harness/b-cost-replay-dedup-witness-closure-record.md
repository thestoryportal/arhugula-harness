# B-COST-REPLAY-DEDUP-WITNESS — replay-dedup cost-join verification witness

**Status:** CLOSED — verify-first, GREEN, no fix (ADR-D6 §1.5 / C-OD-14).

## 1. The grounding question

Per `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §4: ADR-D6 §1.5 / C-OD-14 commits "cost attribution joins on `idempotency_key`; replay must not double-count." Flagged `[MODERATE — not independently re-executed]` at the NotebookLM audit. Scope: build a witness that replays a completed step (journal_resume path) and asserts the cost rollup is emitted once; if the join is missing, land the smallest fix at the cost-record accumulator.

## 2. What initial grounding got wrong

An Explore-agent grounding pass hypothesized the CP driver's F2 committed-step-prefix skip (`enumerate(steps[resume_at:], ...)`, `workflow_driver.py:4193`) would prevent a replayed `JOURNAL_RESUME` (`EngineClass.PURE_PATTERN_NO_ENGINE`) step from ever re-invoking its dispatcher, making the cost-attribution call site structurally unreachable on replay.

**This is empirically false.** Direct reading of `workflow_driver.py`'s `resume_at`-determination `if`/`elif` chain (~lines 3816–3969) shows it branches only on `EngineClass.SAVE_POINT_CHECKPOINT`, `EVENT_SOURCED_REPLAY`, `RECONCILER_LOOP`, and `WAL_SEGMENT`. `PURE_PATTERN_NO_ENGINE` has no branch, so `resume_at` stays `0` on every call and the step loop re-dispatches every step from scratch on every re-drive. Instrumented dispatch-call counting during this arc's build confirmed 2 dispatcher invocations across 2 `execute_workflow` calls with the same `run_id` — not 1.

## 3. The real mechanism (verified by mutation probe)

The replay-dedup guarantee lives one layer down, at the **IS state-ledger's content-addressed write** (`harness_is/state_ledger_write.py:append_ledger_entry`, C-IS-07 §7.1): a write whose `idempotency_key` already exists in the ledger returns `WriteResult.IDEMPOTENT_NOOP` and is silently dropped. This check applies to every ledger append, including `RuntimeAuditLedgerWriter.append` (`harness_runtime/lifecycle/audit_writer.py`), the wrap every cost-attribution audit entry goes through.

The audit entry's `idempotency_key` is `f"audit:{tag}:{audit_entry.entry_hash}"`, and `entry_hash` is a pure SHA-256 over the OD `AuditPayload`'s canonical JSON serialization (`audit_ledger_types.py:compute_entry_hash`) — **not** timestamped. The cost-record projection helper (`cost_record_audit_writer.py:_project_cost_record_to_audit_payload`) defaults `timestamp=""` (documented MVP sentinel per §24.4 NOTE 8a-iii), and `attribute_llm_dispatch_cost` never overrides it. So two dispatches of the identical step (same `span_id` / `workflow_id` / `parent_action_id` / token counts ⟹ same computed cost) produce a byte-identical `AuditPayload` ⟹ identical `entry_hash` ⟹ identical `idempotency_key` ⟹ the second write is recognized as a duplicate and dropped at the IS layer.

**Mutation-probed both ways (ad hoc, not committed):**
1. Patching `_determine_resume_at` to always return `0` had **no effect** on the outcome — confirms it's not on the `JOURNAL_RESUME` path at all.
2. Patching `harness_is.state_ledger_write.append_ledger_entry` to always return `APPENDED` (removing the idempotency-key dedup check) turned the positive witness **RED** (`count_after_r2 == 2`) — confirms the test is a genuine detector of the real mechanism, not a tautology.

The committed negative control (`test_journal_resume_fresh_second_run_id_emits_independently`) is the in-repo evidence: two genuinely distinct runs (different `run_id` ⟹ different `parent_idempotency_key` ⟹ different `entry_hash`) independently emit 2 entries, not 1 — the `==1` assertions in the positive test are not vacuous.

## 4. Disposition

**Verified GREEN — no fix landed.** The C-OD-14 "replay must not double-count" invariant holds for the `journal_resume` path, via the IS-layer content-addressed idempotent write — not via the OD `dedupe_on_replay` decision function (confirmed unwired at all four production cost-emission call sites, per the original grounding, which stands unmodified) and not via a CP-level re-dispatch guard for this engine class (confirmed absent). Neither of the latter two is a defect: the ledger's content-addressed dedup is the real, already-working exactly-once boundary for audit-ledger appends generally, cost-attribution included.

**No forward item registered.** The mechanism this arc set out to verify is already correctly load-bearing; there is nothing to fork or fix.

**Scope note.** This arc verifies `JOURNAL_RESUME` only, per its authored scope. The other engine classes (`WAL_SEGMENT`, `EVENT_SOURCED_REPLAY`, `RECONCILER_LOOP`, `SAVE_POINT_CHECKPOINT`) have their own `resume_at`-computation branches and are out of scope here; per the standing discipline, a cost-replay concern surfaced there would be a separate register-don't-build finding, not a broadening of this arc.

## 5. Verification

- `resume_at` `if`/`elif` chain (no `PURE_PATTERN_NO_ENGINE` branch): `harness-cp/src/harness_cp/workflow_driver.py` lines 3816–3969, read directly.
- IS-layer idempotency dedup: `harness-is/src/harness_is/state_ledger_write.py:append_ledger_entry`, lines ~198–230, read directly.
- Audit-write wrap + `idempotency_key` composition: `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py:RuntimeAuditLedgerWriter.append`, read directly.
- `entry_hash` computation (pure content hash, no timestamp): `harness-od/src/harness_od/audit_ledger_types.py:compute_entry_hash`, read directly.
- `timestamp=""` MVP sentinel default: `harness-od/src/harness_od/cost_record_audit_writer.py:_project_cost_record_to_audit_payload`, read directly; confirmed `attribute_llm_dispatch_cost` never overrides it.
- Witness test (both the positive replay-dedup case and the negative distinct-run-id control): `harness-runtime/tests/integration/test_b_cost_replay_dedup_witness.py`.
- Mutation probes (ad hoc scripts, deleted after use — not part of the committed diff): confirmed `_determine_resume_at` is a dead end for this engine class; confirmed the witness goes RED when the real IS-layer dedup check is disabled.
- `advisor()` consulted before the build (flagged the framing risk of over-claiming the idempotency-key JOIN mechanism works, when in fact for journal_resume the join is unreachable and a different, upstream skip was hypothesized to be responsible — that earlier hypothesis is itself what this arc's empirical build corrected).
- Full `harness-runtime` suite: 2445 passed, 40 skipped. `pyright` 0 errors/0 warnings on the new file. `ruff` clean. Out-of-family Codex review: no actionable issues.

## 6. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/b-cost-replay-dedup-witness-closure-record.md` |
| Arc | `B-COST-REPLAY-DEDUP-WITNESS`, R-FS-2 Wave 3, fourth/final arc |
| Disposition | CLOSED — verify-first, GREEN, no fix |
| Authority | ADR-D6 §1.5; OD spec C-OD-14 |
| Forward item registered | None |
| Code change | New test only (`test_b_cost_replay_dedup_witness.py`); no production code change |

*End of B-COST-REPLAY-DEDUP-WITNESS closure record.*
