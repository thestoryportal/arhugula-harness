# Class 1 Fork — B-EFFECT-FENCE: at-most-once EXECUTION of non-idempotent step effects

**Filed:** 2026-06-18 · **Arc:** R-FS-1 standalone `B-*` build arc **B-EFFECT-FENCE** (the 8th standalone `B-*` arc; spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md` line 49) · **Posture:** bundled-absorption (design-substrate `Spec_Harness_Runtime_v1.md` v1.59 → v1.60 NEW §14.22 C-RT-31 + `harness-runtime/src` + `harness-cp` test + by-execution tests + this fork doc + clearance marker) · **Classification:** Class 1 (a genuinely-new H_T sink-fencing surface → design-fork-first per X-AL-3), driven autonomously under FULL-SPEC (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`), **NO operator gate** (`[[feedback-gate-only-on-meaningful-architecture-change]]` — additive + opt-in, no committed-invariant sacrifice). **HEAD at authoring:** origin/main `f2897fb5`.

---

## §1 — The gap (surfaced by U-RT-123 / E-impl-3b finding F-2)

The durable engine classes (E sub-program) advertise floor-(ii) **at-most-once EXECUTION**, but deliver only at-most-once **claim of a revision**. The U-RT-123 reconciler CAS (and every durable resume) guarantees the first resume of a revision wins; it does NOT guarantee at-most-once execution of the workflow steps a resume re-runs. The `idempotency_key` was on the `cp.resume-attempted` AUDIT entry + the per-step ledger dedup, **not** on the external effect at its sink (the effect is opaque to the harness ledger).

**The window (empirically confirmed by code-read at HEAD):**

| Site | What |
|---|---|
| `workflow_driver.py:1985` | compute `step_idempotency_key_pre = _compute_step_idempotency_key(run_idempotency_key, step_index)` |
| `workflow_driver.py:2031` | **dispatch → TOOL_STEP effect fires** (`RuntimeToolDispatcher.dispatch` → `call_tool` → the external MCP tool) |
| `workflow_driver.py:2336` | **`_append_step_ledger_entry` — the per-step ledger COMMIT** |
| `workflow_driver.py:2432` | on resume, `_determine_resume_at` returns the first step ABSENT from the contiguous-materialized prefix (shared by all 4 durable engine classes via `_determine_{event_replay,segment_replay,reconciler_converge}_resume_at` → `_determine_resume_at`) |

A crash anywhere in **`:2031` → `:2336`** leaves the effect fired but the step uncommitted → resume returns this step's index → re-dispatch → the same external effect (`git_push`/`send_email`/payment) fires a SECOND time. The prefix-skip protects only COMMITTED steps; this is precisely the effected-but-uncommitted step, DISTINCT from the reconciler's revision-claim fail-close.

---

## §2 — The build (C-RT-31 §14.22)

A hand-rolled (I-6 — no vendored Temporal/DBOS activity-dedup) durable **effect fence** at the `RuntimeToolDispatcher` `call_tool` sink, mirroring the U-RT-123 `_claim_resume_revision` crash-atomic `O_EXCL`/`os.link`/`fsync` claim, re-keyed from `(workflow, resource_version)` to the per-(run, step, tool) `idempotency_key`:

- **`try_reserve(idempotency_key) -> bool`** — the atomic claim. WON (`True`) → fire; LOST (`False`) → fail-close. First dispatch wins; any re-dispatch of the same effect loses (a cross-process resume re-dispatch OR an in-process `RetryBreakerToolDispatcher` retry — the fence error is not in `_TRANSIENT_TOOL_DISPATCH_ERRORS`, so the breaker fail-fasts it).
- A lost claim raises **`EffectFenceReservedUncommittedError`** → the driver's generic `except BaseException` maps it to a FAILED `RunResult` (honest fail-close to §22.1, no silent double-fire).
- **COMMIT = the existing per-step ledger entry** (`_append_step_ledger_entry`); the fence adds ONLY the RESERVE (pre-fire) marker — one source of truth (advisor: the genuinely-new piece is the reserve; the commit already exists).
- Opt-in `RuntimeConfig.effect_fencing: bool = False`; the stage-5 tool-dispatcher factory constructs `RuntimeEffectFence(fence_dir=repository_root/.harness/effect-fence)` when `True`. Default → `None` → byte-identical.

**At-most-once, NOT exactly-once.** The fire-then-crash-before-commit window is ambiguous (did the effect fire?), so the conservative fail-close (a reserved-but-unfired effect also fail-closes its re-dispatch) is the honest answer — exactly the reconciler's §22.1 posture. Single-host (cross-host folds into the deferred F-CC item).

### The one nameable design fork — fence scope (C10⊥C11), probe-resolved

| Reading | Position | Voice |
|---|---|---|
| **A — uniform (fence every tool call)** | max action-safety; but fence I/O on every call (incl. read-only) + on non-durable runs | C10 action-safety/blast-radius |
| **B — per-tool classified (fence only declared-non-idempotent tools)** | minimal cost; but needs a NEW `ToolContract` idempotency field (absent today) → cross-axis AS fork | C11 operator-loop/local-first |
| **C — opt-in under durable engine** ✅ | pay fence I/O only when a resume can re-fire (exactly when double-fire is possible); runtime-only, no AS field | resolves both |

**Probe-resolved** (`[[probe-resolves-fork-prescribed-council]]`): scoping to "tool steps under a durable/resumable engine" collapses the C10⊥C11 cost objection (fence I/O is paid exactly when double-fire is possible) AND a *correctness* property cannot default-off or trust operator metadata (foreclosing B's classified-default + the trust-the-tool path). No nameable tension survives → advisor, not council (§10.9). Per-tool classification = registered follow-on `B-EFFECT-FENCE-PER-TOOL`.

---

## §3 — Registered follow-ons (NOT silent-deferred; `[[spine-ledger-forward-arc-registration]]`)

| Follow-on | What |
|---|---|
| **`B-EFFECT-FENCE-DURABLE-AUTO`** | Auto-activate the fence whenever `manifest_entry.engine_class` is durable (thread the engine class to the factory / a per-run reserve gate), removing the opt-in flag for the common case while keeping non-durable runs fence-free. |
| **`B-EFFECT-FENCE-PER-TOOL`** | A `ToolContract` idempotency classification (`{READ_ONLY, IDEMPOTENT, NON_IDEMPOTENT}`) so only declared-non-idempotent tools are fenced — a cross-axis AS contract surface → design-fork-first per X-AL-3 at that arc. |
| **`B-EFFECT-FENCE-HITL-ROUTE`** | Turn the interim fail-closed raise into a genuine §22.1 operator-resolvable PAUSE (skip / re-run / abort) + register an `RT-FAIL-EFFECT-FENCE-*` taxonomy code; *suppress-and-continue* (return the prior output so the run proceeds past the suppressed effect) composes with `B-ENGINE-OUTPUT-REPLAY`'s output-carrying substrate. |

Cross-host effect fencing folds into the existing deferred **F-CC** item (distributed-impossible under {I-6 ∧ no-unsafe-TTL}; the same bound U-RT-123 carries).

---

## §4 — Non-vacuity (the live trap — advisor's #1 steer; cf. B-TOOL-GATE #653 wired-but-production-dead)

Proven by-execution with **NO proxy** (`harness-runtime/tests/test_effect_fence.py` + `harness-cp/tests/test_workflow_driver.py`):

1. **Fence mechanics** — first claim wins; re-claim loses; distinct keys independent (run-scoping); a fresh `RuntimeEffectFence` instance over the same dir sees the prior claim (durable across a restart).
2. **Real-dispatcher at-most-once** — a real `RuntimeToolDispatcher.for_single_host(effect_fence=…)` over a counting MCP tool: two dispatches with the same key fire the tool body EXACTLY ONCE (the second raises `EffectFenceReservedUncommittedError`).
3. **NEGATIVE CONTROL** — the same two dispatches WITHOUT the fence DOUBLE-FIRE (the window is real + the fence is load-bearing).
4. **Genuine crash-then-resume** — a SECOND dispatcher instance over the SAME on-disk fence dir (a restarted process) fail-closes against the durable claim → 1 fire across the restart.
5. **Driver re-dispatch key-stability** — through the real `execute_workflow` resume path (ledger-reader-controlled `resume_at`), the re-dispatched uncommitted step carries a byte-identical `step_context.parent_idempotency_key` to the genesis run → the fence resolves it to the SAME claim. (Observes the key only — does NOT fake the suppression; the suppression is proven at the real sink in #2.)

---

## §5 — Classification: Class 1 (design-fork-first), driven autonomously, NO operator gate

| Class-1 indicator | Present? |
|---|---|
| New H_T primitive surfaced (X-AL-3) | **YES** — a sink-fencing surface is new → design-fork-first: C-RT-31 §14.22 authored + clearance marker filed BEFORE/with the impl. |
| Committed invariant sacrificed | NO — additive + opt-in (default byte-identical); I-6 hand-roll + ADR-F2 single-write honored (separate store, COMMIT = existing ledger entry); no §5.2-hash / IS / CP / OD contract change. |
| Nameable cross-domain tension needing a council | NO — the one C10⊥C11 fence-scope tension is probe-resolved by durable-resume scoping (§2) → advisor, not council. |
| Operator gate | NO — additive + opt-in, no committed-invariant sacrifice; FULL-SPEC pre-authorizes the build + back-flow (`[[feedback-gate-only-on-meaningful-architecture-change]]`). |

**Gates:** pyright 0/0/0 (changed files); ruff clean; harness-runtime 1726 passed (non-e2e); harness-cp 1063 passed + 1 xfailed; `test_effect_fence.py` 6/6. Decorrelated review: advisor (full-transcript) + out-of-family Codex (pre-merge, on the diff).

---

## §6 — Files

- `harness-runtime/src/harness_runtime/lifecycle/effect_fence.py` — NEW: `RuntimeEffectFence` (crash-atomic `try_reserve`) + `EffectFenceReservedUncommittedError` + `EffectFenceProtocol`.
- `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py` — `effect_fence` ctor param + `self._effect_fence` + the sink reserve-before-`call_tool` (Step 6b).
- `harness-runtime/src/harness_runtime/bootstrap/factories/runtime_tool_dispatcher_factory.py` — construct the fence when `config.effect_fencing`, thread to the dispatcher.
- `harness-runtime/src/harness_runtime/types.py` — `RuntimeConfig.effect_fencing: bool = False`.
- `harness-runtime/tests/test_effect_fence.py` — NEW: fence mechanics + real-dispatcher at-most-once + negative control + fresh-instance restart.
- `harness-cp/tests/test_workflow_driver.py` — NEW `test_resume_redispatch_hands_byte_identical_idempotency_key_to_tool_sink` (the driver re-dispatch key-stability link).
- `design-substrate/Spec_Harness_Runtime_v1.md` — v1.59 → v1.60 NEW §14.22 C-RT-31 + change-note.
- `.harness/clearance/Spec_Harness_Runtime-v1_60-cleared-2026-06-18.md` — clearance marker.
- `.harness/beyond-mvp-capability-boundary-ledger.md` — B-EFFECT-FENCE marked BUILT + the 3 follow-ons registered.
- This fork doc.
