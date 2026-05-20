# Phase 7 sub-phase 7d — substitution retirement events, batch 1 (8 events)

**Filed:** 2026-05-20, Phase 7 sub-phase 7d. **Skill:** `phase-7-substitution-retirement` §8.1 (workspace progress ledger).
**Authority:** v2 second-pass ledger at `.harness/phase-7d-retirement-ledger-v2.md` §9.1 (verification evidence base). Operator-ratified runtime-only substitution-site reading per v2 §1.

---

## §0 Batch context

8 H_T substitutions transition **bounded-residual** (v1, 2026-05-17) → **RETIRED** (this batch, 2026-05-20) under condition A ∧ condition B per X-AL-2:

- Condition A (cited unit IDs landed): universally TRUE per v1 (7b/7c complete; IS 17/17, AS 33/33, CP 58/58, OD 35/35).
- Condition B (H_E surface no longer invoked at substitution site): evaluated per substitution against H_T runtime at `43500bf` under runtime-only substitution-site reading (operator-authoring lane out of scope).

Per-event records follow skill §8.1 field shape:

| Field | Content |
|---|---|
| Substitution ID | H_T-{AXIS}-N |
| Retirement event timestamp | Phase 7 session + segment + unit-landing event reference |
| Condition A verification | Cited unit IDs + acceptance-criteria-passed reference |
| Condition B verification | Substitution-site code-review reference; H_E surface confirmed not invoked |
| Cross-axis dependency cascade | If §6.3.1 or §6.3.2 triggered |

---

## §1 H_T-IS-1 — Path-class registry + workflow-canonical path resolver

| Field | Content |
|---|---|
| Substitution ID | H_T-IS-1 |
| Primitive | Path-class registry (4-class enum: SKILLS / PROMPTS / ROUTING_MANIFEST / STATE_LEDGER) + workflow-canonical path resolver |
| Spec contract | C-IS-01 §1 |
| Retirement event timestamp | Phase 7 sub-phase 7d second pass, 2026-05-20; verified against runtime closure `43500bf` (Phase 2 close, per `[[phase-2-runtime-close]]`) |
| Condition A verification | Cited carrier units U-IS-01, U-IS-02, U-IS-03 all landed at 7b (IS 17/17 complete per `[[phase-7-bootstrap-status]]`); IS terminal exporter U-IS-17 landed (125 IS tests green) |
| Condition B verification | `harness-runtime/src/harness_runtime/bootstrap/stage_1_is.py` step 1 invokes `materialize_path_registry(config.path_bindings, workflow_class, deployment_surface)`; resulting registry exposed at `ctx.path_resolver` for downstream stages. `path_class_registry.py:31-37` defines the 4-member `PathClass` enum. Zero `CLAUDE.md`-convention path-class reads at runtime — no `Bash(Glob)` / `Read` of `CLAUDE.md` for path-class semantics in any runtime module. Substitution mechanism (Convention category per Meta-Architecture §5.2) no longer operative at runtime substitution site |
| Cross-axis dependency cascade | None at retirement event. Downstream IS-AL-1 conformance at runtime now enforced |
| Evidence anchor | v2 ledger §3 (IS table row 1) + `phase_7c_genuine_typed_seam_verification.md` §3 row 7 (U-AS-28 → U-IS-02 PATH_CLASS_REGISTRY import wired) |

---

## §2 H_T-IS-5 — State-ledger entry shape (6-field idempotency-key carrier)

| Field | Content |
|---|---|
| Substitution ID | H_T-IS-5 |
| Primitive | State-ledger entry shape — 6-field idempotency-key carrier per C-IS-05 §5 |
| Spec contract | C-IS-05 §5 |
| Retirement event timestamp | Phase 7 sub-phase 7d second pass, 2026-05-20; verified against runtime closure `43500bf` |
| Condition A verification | Cited carrier units U-IS-07, U-IS-08, U-IS-09, U-IS-10 all landed at 7b; F3-02 idempotency-key join carrier closure at U-IS-12 (canonical join carrier per F3-02). State-ledger entry shape fork closed per `[[fork-state-ledger-entry-shape]]` (resolved; includes append/hash recipe). State-ledger path dir-vs-file fork resolved per `[[fork-state-ledger-path-dir-vs-file]]` Path A (IS spec v1.3 §1 amendment) 2026-05-20 |
| Condition B verification | `harness-runtime/src/harness_runtime/lifecycle/state_ledger.py` (`LedgerWriter.append(payload, write_key)`) is the runtime-side typed surface; wraps `harness_is.state_ledger_write.append_ledger_entry`. Driver invocation at `harness-cp/src/harness_cp/workflow_driver.py:397-417` (`_append_step_ledger_entry` with computed `step_idempotency_key`) — F2 six-field shape exercised end-to-end. Admin read path at `harness-runtime/src/harness_runtime/admin/inspect.py` opens `.harness/state.jsonl` programmatically through typed surface. Substitution mechanism (Shell-out category — `Bash(python -c 'import json...')` / `Bash(cat <<EOF >>)`) no longer required at runtime substitution site; runtime callers obtain idempotency-key discipline via `append_ledger_entry` not via operator-shell |
| Cross-axis dependency cascade | Composes with H_T-IS-6 + H_T-IS-7 to form the typed state-ledger surface that H_T-CXA-2 (CP→IS) substrate-side depends on. Consumer side (CP driver invocation) still bounded by absent CP driver surfaces — does NOT yet trigger CXA-2 retirement |
| Evidence anchor | v2 ledger §3 (IS table row 2) + 7c log §3 rows 13/14 (U-CP-34 → U-IS-07/11 typed imports wired); `bootstrap/stage_1_is.py` step 2 (`ctx.ledger_writer` post-condition non-None) |

---

## §3 H_T-IS-6 — Hash-chain integrity discipline

| Field | Content |
|---|---|
| Substitution ID | H_T-IS-6 |
| Primitive | Hash-chain integrity discipline (canonicalize → SHA-256 → chain-construct → verify pipeline) per C-IS-06 §6 |
| Spec contract | C-IS-06 §6 |
| Retirement event timestamp | Phase 7 sub-phase 7d second pass, 2026-05-20; verified against runtime closure `43500bf` |
| Condition A verification | Cited carrier units U-IS-08, U-IS-09, U-IS-10 all landed at 7b |
| Condition B verification | `harness-is/src/harness_is/entry_hash.py` owns the in-process `hashlib.sha256` invocation (line 76) + JCS canonicalization (line 37) — this is the H_T implementation, NOT the H_E substitution. The H_E substitution was operator shelling out to `Bash(python -c 'import hashlib')` to produce entry hashes. At runtime: `harness-is.chain_link_construction.construct_prior_event_hash` + `chain_verification.verify_chain` invoked via `append_ledger_entry` chain-construct + reattach-and-verify at `bootstrap/stage_1_is.py` post-condition ("ledger chain reattached and verified"). Substitution mechanism (Shell-out + Authoring) no longer invoked at runtime substitution site |
| Cross-axis dependency cascade | Composes with H_T-IS-5 + H_T-IS-7 for state-ledger surface; satisfies H_T-CXA-2 substrate-side hash-chain dependency |
| Evidence anchor | v2 ledger §3 (IS table row 3) + 7c log §3 rows 4/5 (U-AS-26 → U-IS-09 `construct_prior_event_hash` + U-AS-26 → U-IS-10 `verify_chain` imports wired) |

---

## §4 H_T-IS-7 — T-perm-2 F2-layer read/write contract pair (JSONL composition)

| Field | Content |
|---|---|
| Substitution ID | H_T-IS-7 |
| Primitive | T-perm-2 F2-layer read/write contract pair — typed `append_ledger_entry` writer + typed `LedgerNavigationPrimitive` reader for JSONL composition per C-IS-07 §7 |
| Spec contract | C-IS-07 §7 |
| Retirement event timestamp | Phase 7 sub-phase 7d second pass, 2026-05-20; verified against runtime closure `43500bf` |
| Condition A verification | Cited carrier units U-IS-11, U-IS-12 (canonical idempotency-key join carrier per F3-02 closure) both landed at 7b |
| Condition B verification | `harness-is/src/harness_is/state_ledger_write.py` exposes typed `append_ledger_entry(payload, write_key=(thread_id, step_id, idempotency_key))` write surface; `state_ledger_read.py` exposes typed `LedgerNavigationPrimitive` + `ReadResult` read surface. Both materialized at runtime via `harness-runtime/.../lifecycle/state_ledger.py` (`materialize_state_ledger` writer + `materialize_state_ledger_reader` reader, lines 55-56, 168-178). Substitution mechanism (Shell-out — `Bash(cat <<EOF >>)` C3-pole append + `Bash(jq ...)` or `Read` + Python `json.loads` C2-pole filter) no longer required for runtime callers |
| Cross-axis dependency cascade | Enables typed CP→IS F2-substrate-join at runtime (composes with H_T-CP-8 retirement criterion — CP-8 currently PARTIAL pending `cp_is_wiring.py` 17-edge full-land per `class_1_tension_u_rt_35_cp_is_wiring_gaps.md`). Substrate-side IS surface ready; consumer side awaits CP wiring full-land |
| Evidence anchor | v2 ledger §3 (IS table row 4) + 7c log §3 row 15 (U-CP-35 → U-IS-12 `LedgerNavigationPrimitive` import wired); v2 ledger §5 CP-8 PARTIAL row |

---

## §5 H_T-IS-8 — Workload-class-opt-in shadow-Git checkpoint

| Field | Content |
|---|---|
| Substitution ID | H_T-IS-8 |
| Primitive | Workload-class-opt-in shadow-Git checkpoint — manifest-declared cadence per C-IS-08 §8 |
| Spec contract | C-IS-08 §8 |
| Retirement event timestamp | Phase 7 sub-phase 7d second pass, 2026-05-20; verified against runtime closure `43500bf` |
| Condition A verification | Cited carrier units U-IS-13, U-IS-14, U-IS-15 all landed at 7b |
| Condition B verification | `harness-is/src/harness_is/shadow_git_checkpoint.py` carries manifest-declared cadence enum + workload-class opt-in selection (lines 39, 81, 91); composed in runtime via `harness-runtime/.../lifecycle/shadow_git.py` (`materialize_isolation_stage`) at `bootstrap/stage_1_is.py` step 3. Cadence gate at `shadow_git_checkpoint.py:91` (`opt_ins.shadow_git_enabled and opt_ins.shadow_git_cadence == trigger_context.cadence`). `ctx.shadow_git` post-condition non-None. Substitution mechanism (H_E-direct: H_E Checkpointing on session-state grain + `Bash(git commit)` at H_E-decided cadence + `CLAUDE.md` cadence convention) no longer routes harness-state cadence at runtime substitution site — harness-state cadence is now workload-class-manifest-driven via H_T-owned typed surface |
| Cross-axis dependency cascade | None |
| Evidence anchor | v2 ledger §3 (IS table row 5); `bootstrap/stage_1_is.py` step 3 + post-condition |

---

## §6 H_T-IS-9 — Workload-class-opt-in worktree isolation

| Field | Content |
|---|---|
| Substitution ID | H_T-IS-9 |
| Primitive | Workload-class-opt-in worktree-isolation — manifest-driven opt-in + concurrency-cap per C-IS-09 §9 |
| Spec contract | C-IS-09 §9 |
| Retirement event timestamp | Phase 7 sub-phase 7d second pass, 2026-05-20; verified against runtime closure `43500bf` |
| Condition A verification | Cited carrier units U-IS-15, U-IS-16 both landed at 7b |
| Condition B verification | `harness-is/src/harness_is/worktree_isolation.py` carries manifest-driven workload-class opt-in (`worktree_isolation_enabled` gate at line 117) + `worktree_concurrency_cap` enforcement (lines 117-121). Composed in runtime via `harness-runtime/.../lifecycle/shadow_git.py` (`materialize_isolation_stage`) at `bootstrap/stage_1_is.py` step 3. `ctx.worktree_manager` post-condition non-None. The runtime worktree manager invokes `subprocess.run(["git", "worktree", ...])` *inside* the typed manager (H_T-owned dispatch, not H_E `EnterWorktree`). Substitution mechanism (H_E-direct: H_E native `EnterWorktree` for per-sub-agent isolation + `--worktree <name>` flag) no longer required at runtime substitution site for harness-controlled isolation |
| Cross-axis dependency cascade | None |
| Evidence anchor | v2 ledger §3 (IS table row 6); `bootstrap/stage_1_is.py` step 3 |

---

## §7 H_T-AS-1 — SandboxTier 4-tier enum + tier-monotonicity ordering

| Field | Content |
|---|---|
| Substitution ID | H_T-AS-1 |
| Primitive | SandboxTier 4-tier enum (1-indexed: READ_ONLY / WORKSPACE_WRITE / NETWORK / FULL) + tier-monotonicity ordering + `sandbox_tier_floor` + `SandboxDispatchTable` per C-AS-01 §1 |
| Spec contract | C-AS-01 §1 |
| Retirement event timestamp | Phase 7 sub-phase 7d second pass, 2026-05-20; verified against runtime closure `43500bf` |
| Condition A verification | Cited carrier units U-AS-01, U-AS-02 both landed at 7b (AS 33/33 complete per `[[phase-7-bootstrap-status]]`; harness-as 302 tests green); AS terminal exporter U-AS-33 landed |
| Condition B verification | `harness-as/src/harness_as/sandbox_tier.py` defines `SandboxTier` 4-member enum. `harness-runtime/src/harness_runtime/lifecycle/sandbox_dispatch.py` materializes the 6-provider × tier `SandboxDispatchTable` via `materialize_sandbox_dispatch` (lines 60-95) with empty-tier invariant. `harness-runtime/.../bootstrap/stage_2_as.py:59` wires it at boot. `harness-runtime/.../lifecycle/handoff.py:174` enforces C-AS-11 monotonic-ascent via `assert_monotonic_ascent` in-runtime. The 1-indexed enum is consumed cross-axis (per FF-3 resolution 2026-05-16 per `[[phase-7-bootstrap-status]]` OD plan v2.10) — `harness-od` adds `harness-as` as uv-workspace dep for `SandboxTier` import. Substitution mechanism (H_E-direct: `--permission-mode plan` / `default+deny` / `acceptEdits` / `bypassPermissions` 4-level approval gradient) no longer routes sandbox-tier decisions at runtime — no `--permission-mode` / `bypassPermissions` / `acceptEdits` strings reachable from runtime composers (grep clean) |
| Cross-axis dependency cascade | Substrate-side underpins H_T-CXA-3 (CP → AS) substitution wiring; CXA-3 currently STILL-BOUNDED (no `cp_as_wiring.py` runtime stage per CXA v2.3 spec §12 enumeration). Substrate also underpins H_T-OD-29 → AS-15 cross-axis import per 7c verification log §3 row 22 (OD-29 v2.10) |
| Evidence anchor | v2 ledger §4 (AS table row 1); 7c log §3 row 22 (U-OD-29 → U-AS-15 `SandboxTier` import wired) |

---

## §8 H_T-CP-6 — Workflow manifest schema + per-step override + audit

| Field | Content |
|---|---|
| Substitution ID | H_T-CP-6 |
| Primitive | Workflow manifest schema + per-step override + audit per C-CP-06 §6 |
| Spec contract | C-CP-06 §6 |
| Retirement event timestamp | Phase 7 sub-phase 7d second pass, 2026-05-20; verified against runtime closure `43500bf` |
| Condition A verification | Cited carrier units U-CP-13, U-CP-14 both landed at 7b (CP 58/58 complete per `[[phase-7-bootstrap-status]]`; harness-cp 463 tests green at 7b close, 498 tests at Phase 2 close per `[[phase-2-runtime-close]]`); U-CP-04 `RoutingManifest` FULL-LAND per CP plan v2.10 7c-prereq reconcile (R-2/W-2 schemas ratified) |
| Condition B verification | Operator-supplied typed `RoutingManifest` validated + persisted to `PathClass.ROUTING_MANIFEST` via `harness-runtime/src/harness_runtime/lifecycle/routing_manifest.py:143-145`. Per-step override evaluation via `harness-runtime/.../lifecycle/override_evaluator.py:78-88`. Production execution path at `harness-cp/src/harness_cp/workflow_driver.py:360-364` invokes `resolve_step_binding(manifest_entry, step_id, default_model_binding=...)` **per-step at runtime** — manifest is the execution surface, not prose. Substitution mechanism (Convention: `CLAUDE.md` carries workflow conventions as prose) no longer routes per-step binding at runtime — `CLAUDE.md` prose is not consulted by the driver for per-step model binding |
| Cross-axis dependency cascade | CP-6 retirement does NOT trigger §6.3.1 (which is CP-1 → AS-8) or §6.3.2 (which is OD-2 + CP-24 → CXA-5). Local CP-axis retirement |
| Evidence anchor | v2 ledger §5 (CP table CP-6 row, marked RETIRE-READY); `routing_manifest.py:143-145`, `override_evaluator.py:78-88`, `workflow_driver.py:360-364` |

---

## §9 Cumulative retirement state after batch 1

| Class | Pre-batch (v1 §1) | This batch | Post-batch |
|---|---|---|---|
| Authoring-only retired (v1 §1) | 4 | 0 | 4 |
| Runtime-active retired (this batch) | 0 | **8** | **8** |
| Runtime-active PARTIAL (v2 §9.1) | 0 | 0 | 7 |
| Runtime-active STILL-BOUNDED (v2 §9.1) | 45 | −8 | 30 |
| **Total substitutions** | **49** | — | **49** ✓ |

Post-batch: **12 / 49 retired (24.5%)**. Of the remaining 37, the v2 ledger §9.2.5 reframing applies — closure gated on 3+ separate runtime composers (tool-invocation, LLM-dispatch, HITL/validator/sub-agent), not just Phase 2 runtime.

---

## §10 Cross-axis cascade status after batch 1

| Cascade | Endpoints | Status post-batch | Reason |
|---|---|---|---|
| §6.3.1 H_T-CP-1 → H_T-AS-8 (anthropic.* namespace emission) | CP-1 + AS-8 | DORMANT (unchanged) | CP-1 STILL-BOUNDED (no LLM call site in runtime); CP-1 not in batch 1 |
| §6.3.2 H_T-OD-2 + H_T-CP-24 → H_T-CXA-5 (F-CP-01 Stage 3b inversion) | OD-2 + CP-24 + CXA-5 | DORMANT (unchanged) | OD-2 PARTIAL; OD-2 not in batch 1 |

No cross-axis cascade fires from this batch. The 8 retirements are substrate-layer (IS×6 + AS×1 + CP×1) and do not unblock either documented cross-axis dependency.

---

## §11 Operator ratification

Per skill `phase-7-substitution-retirement` §3.1: retirement = (A) ∧ (B). Both conditions verified for all 8 entries above against v2 ledger evidence base. No halts surfaced (no condition-A-met-with-B-still-invoked patterns; no condition-B-met-with-A-not-landed patterns; all retirement-criterion columns at Meta-Architecture §5 are sufficient).

Per skill §5.2: 7d closure requires all H_E substitutions retired OR explicit bounded-residual carry-forward. Post-batch state: 12 retired + 7 PARTIAL + 30 STILL-BOUNDED. The 37 non-retired are explicitly classified at v2 ledger §3–§7 with file:line evidence + per-substitution rationale + the updated v2 §9.2.5 3-composer scope framing. No silent carry-forward.

**Ratification request:** Operator confirms the 8 retirement events recorded above. v2 ledger §9.4 ratification (37 non-retired as bounded-residual under updated 3-composer scope framing) is a separate ratification — not requested at this batch-1 filing.

---

## §12 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-1.md` |
| Authored at | Phase 7 sub-phase 7d, 2026-05-20 |
| Authoring authority | Skill `phase-7-substitution-retirement` §8.1 (workspace progress ledger) |
| Verification authority | v2 ledger `.harness/phase-7d-retirement-ledger-v2.md` §9.1 (verification evidence base) |
| Scope | Event-record filing for 8 RETIRE-READY events surfaced at v2 second pass |
| Predecessor | `.harness/phase-7d-retirement-ledger.md` v1 §1 (4 authoring-only retirements, 2026-05-17) |
| Successor consumption | Per-axis `harness-{is,as,cp}/CLAUDE.md` §4 substitution-table doc-hygiene pass; future batches when additional substitutions transition PARTIAL/STILL-BOUNDED → RETIRE-READY |
| Status | 8 retirement events recorded; cumulative 12/49 retired; cross-axis cascades unchanged (both DORMANT); §9 Class 2 multi-LLM commitment surface OPEN (unchanged — CP-1 not in batch) |

---

*End of phase-7d retirement events batch 1.*
