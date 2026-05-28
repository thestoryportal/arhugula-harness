# Phase 7d Retirement Events — Batch 27

| Field | Value |
|---|---|
| Batch number | 27 |
| Filed at | 2026-05-28 (post H_T-AS-8f STILL-BOUNDED → STILL-BOUNDED-INDEFINITELY at batch-26; same-session U-OD-39 cost-attribution tool-dispatch arc: module + 12 unit tests at `0e84c94` + production binding + 5 integration tests at `7e513c8`) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; U-OD-39 production binding empirically MET via 5 integration tests at `test_lifecycle_runtime_tool_dispatcher_cost_attribution.py` covering success path + 4 exception paths + None-substrate skip + unknown-tool-id swallow |
| Predecessor batch | `phase-7d-retirement-events-batch-26.md` (2026-05-28, H_T-AS-8f STILL-BOUNDED → STILL-BOUNDED-INDEFINITELY DEFER INDEFINITELY mirror AS-8e) |

---

## §0 Batch context

**Status type: 1 within-PARTIAL advance (H_T-OD-5).** Closure-event-class: producer-site landing at the 2nd of 4 billable dispatch surfaces enumerated at OD spec v1.8 §C-OD-26.2. The retirement state itself does NOT transit (OD-5 stays PARTIAL) but the surface-coverage count advances 1/4 → 2/4. Mirror of within-PARTIAL advance precedent at batch-11 (H_T-OD-5 PARTIAL at LLM-only surface landing per U-OD-38).

**Distinction from batch-25/26 transits:** AS-8d at batch-25 was STILL-BOUNDED → RETIRE-READY (carrier-binding-chain MET + e2e empirical-emission MET; full retirement gates on operator deployment-time hook). AS-8f at batch-26 was STILL-BOUNDED → STILL-BOUNDED-INDEFINITELY (X-AL-2 bounded-residual routing transit; mirror AS-8e). H_T-OD-5 at batch-27 is **within-PARTIAL advance** — no state transit; the 5-step chain advances to a 2nd dispatch surface but PARTIAL → RETIRE-READY gates on **all 3 missing surfaces** (tool + validator + webhook). After this batch: 1 of 3 missing surfaces (tool) production-wired; 2 remain (validator + webhook bundled at U-OD-40 next-arc scope).

**Counting math (post-batch-26):**

Pre-batch-27:
- Workspace ledger cumulative: 33/54 RETIRED + 1/54 RETIRE-READY (AS-8d) + 5/54 PARTIAL (CP-8 + CP-9 + CP-11 + CP-14 + CP-17 + OD-5) + 13/54 STILL-BOUNDED + 2/54 STILL-BOUNDED-INDEFINITELY = **39/54 = 72.2% pipeline-advanced** (per batch-26)
- OD-axis: 2/8 RETIRED + 2/8 PARTIAL (OD-5 + OD-6) + 4/8 STILL-BOUNDED (OD-1/3/4/7); OD-5 had 1/4 surfaces wired (LLM only)

Post-batch-27 (H_T-OD-5 within-PARTIAL advance at tool dispatch surface):
- Workspace ledger cumulative: 33/54 RETIRED + 1/54 RETIRE-READY + 5/54 PARTIAL + 13/54 STILL-BOUNDED + 2/54 STILL-BOUNDED-INDEFINITELY = **39/54 = 72.2% pipeline-advanced (unchanged — within-PARTIAL advance does NOT promote count)**
- OD-axis: 2/8 RETIRED + 2/8 PARTIAL (OD-5 + OD-6) + 4/8 STILL-BOUNDED (OD-1/3/4/7); **OD-5 now has 2/4 surfaces wired (LLM + tool)**
- Surface-coverage view at OD-5: 50.0% wired (was 25.0% post-batch-11); pipeline path to RETIRE-READY: U-OD-40 bundled validator + webhook = remaining 2/4 surfaces

**Design-substrate edits at batch-27:**
- `harness-od/CLAUDE.md` H_T-OD-5 row refresh — 2 of 4 surfaces wired + clearance of stale 2026-05-23 cross-axis-blocker framing + U-OD-39 production-binding empirical citations
- `.harness/phase-7d-retirement-events-batch-27.md` NEW (this file)
- ZERO spec amendments (OD spec v1.24 unchanged; runtime spec v1.33 unchanged; AS / CP / CXA / ADR / ADD / PRD all unchanged)
- ZERO workspace `CLAUDE.md` version bump (no spec or plan delta)

---

## §1 Retirement event — H_T-OD-5 within-PARTIAL advance (tool dispatch surface wired)

**Substitution identity:** H_T-OD-5 (Cost-attribution 5-step chain at billable spans).

**Pre-batch state:** PARTIAL. Surface coverage 1/4 (LLM only via U-OD-38 at `7104fd7` cluster 4-OD-D). Gate text at `harness-od/CLAUDE.md:165` dated 2026-05-23 cited cross-axis blockers (U-RT-67/U-RT-69 tool-invocation composer + U-CP-60 validator framework + U-CP-72 audit-write seam) as the holdup. ALL THREE EMPIRICALLY CLEARED at HEAD `ccad7fb`:
- U-RT-67 RuntimeToolDispatcher LANDED at L9-sexies/septies 2026-05-22 (`harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:204`).
- U-CP-60 validator framework LANDED at cluster 10-CP-A `b70e9a6` (RETIRE-READY per H_T-CP-21 batch-11).
- U-CP-72 audit-write seam ALL-RESIDUALS-CLOSED at batch-18 2026-05-24 per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]`.

**Closure-event lineage:**

1. **Empirical orientation + advisor pre-substantive consultation** — 26th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`. Advisor surfaced the discriminator: OD spec v1.8 §C-OD-26.2 already enumerates 4 producer-site contracts (LLM/tool/validator/webhook) with distinct per-surface cost-meter semantics; §C-OD-28.1 + RATE_TABLE_V1 already has `tool_rates` + `webhook_rate` + `cpu_rate_per_ms` rate rows for all 3 missing surfaces. **OD-5 is CODE arc, NOT spec-fork arc.** Advisor's 3 semantic risks (validator double-count / webhook no-rate-input / tool vs AS-sandbox-cost overlap) all spec-addressed before drafting.

2. **Module + unit tests** — `0e84c94` (merged to main at `ccad7fb`): NEW `harness-runtime/src/harness_runtime/lifecycle/cost_attribution_tool_dispatch.py` (311 LOC) mirroring `cost_attribution_llm_dispatch.py` structural precedent. Module surface: `attribute_tool_dispatch_cost(...)` full 5-substep chain + `_compute_tool_cost(rate, tool_args, response)` 3-branch cost_kind formula + `_canonical_json_byte_length(payload)` UTF-8 byte count + `_resolve_tool_rate(rate_table, tool_id)` §C-OD-28.2 default fail-closed + NEW `ToolRateMissingError`. 12 NEW unit tests at `test_lifecycle_cost_attribution_tool_dispatch.py` covering 3 cost_kind branches + Decimal precision + canonical-JSON byte-length + AC #4 + AC #5 + fail-closed.

3. **Production binding** — `7e513c8`: RuntimeToolDispatcher.__init__ extended with `cost_chain` / `audit_writer` / `rate_table` None-default kwarg-only params. NEW private method `_attribute_tool_cost_best_effort` wraps the helper at 5 invocation sites (1 success + 4 exception paths: ToolInvocationTimeoutError / ToolInvocationProtocolError / MCPHostUnreachableError / ToolInvocationSchemaViolationError). materialize_runtime_tool_dispatcher_stage factory threads ctx.cost_chain + ctx.audit_writer + RATE_TABLE_V1 kwarg. bootstrap stage_5_loop_init.py passes RATE_TABLE_V1 to the factory. 5 NEW integration tests at `test_lifecycle_runtime_tool_dispatcher_cost_attribution.py`.

**Post-batch state:** PARTIAL (within-PARTIAL advance). Surface coverage 2/4 (LLM + tool). U-OD-39 production-binding chain MET; AC #1 (success+failure invocation) + AC #3 (mcp.tool.call piggyback) + AC #4 (cost-record attached + audit-ledger entry) + AC #5 (1-call-1-entry empirical) all empirically verified at integration test suite.

**Verification-shape applied (per `[[verification-shape-sharpened-grep-vs-e2e]]`):** Empirical e2e at integration tests against real FastMCP echo fixture (NOT _Fake mocks). All 3 binding-chain stages verified:
1. **Module-layer:** `cost_attribution_tool_dispatch.py` 12 unit tests covering schema repurposing + cost_kind formulas + canonical-JSON convention + fail-closed.
2. **Constructor-layer:** RuntimeToolDispatcher.__init__ accepts cost_chain/audit_writer/rate_table; None-defaults preserve unit-test ergonomics.
3. **Dispatch-end-to-end-layer:** Production dispatch at success path emits `cost.attributed_decimal` OTel attribute on outer `tool.dispatch` span carrying serialize_decimal_for_otel(Decimal(...)) value; audit-ledger receives 1 entry per dispatch with `action_id=cost:<workflow_id>:<step_action_id>` + `response=cost_attributed`; failure paths (schema_violation tested empirically) preserve same invocation discipline. Test fixture uses constructor-passed tracer_provider (NOT global) to avoid OTel SDK override discipline pollution.

**ZERO cross-axis cascade:** OD ingestion / AS spec / CXA seam / ADR / ADD / PRD unchanged. CXA v2.9 row 8 cost-attribution audit-write seam is shared with LLM dispatch — no new edge introduced; the tool-dispatch path reuses the same `cp_audit_to_od_audit` converter with same `cost:` action_id prefix branch.

---

## §2 Counting math + axis status

**OD-axis (post-batch-27):**
- RETIRED: 2/8 = 25.0% (OD-2 + OD-8 authoring-only)
- RETIRE-READY: 0/8
- PARTIAL: 2/8 = 25.0% (OD-5 surface-coverage 2/4 + OD-6 collector daemon)
- STILL-BOUNDED: 4/8 = 50.0% (OD-1 + OD-3 + OD-4 + OD-7)
- Pipeline-advanced (R + RR + P): 4/8 = 50.0% (unchanged from batch-11)
- **OD-5 surface-coverage view: 2/4 = 50.0% wired (LLM + tool); 2/4 remain pending U-OD-40 (validator + webhook bundle)**

**Workspace ledger cumulative (post-batch-27):**
- 33/54 RETIRED + 1/54 RETIRE-READY + 5/54 PARTIAL + 13/54 STILL-BOUNDED + 2/54 STILL-BOUNDED-INDEFINITELY = **39/54 = 72.2% pipeline-advanced (unchanged)** — within-PARTIAL surface-coverage advance does NOT promote pipeline-advanced count under X-AL-2; gate transit happens at PARTIAL → RETIRE-READY when all 3 missing surfaces wire.

**OD-5 PARTIAL → RETIRE-READY remaining gate:** U-OD-40 (validator + webhook bundled atomic unit per OD plan v2.14): NEW modules `attribute_validator_dispatch_cost.py` (CPU-meter `execution_time_ms × cpu_rate_per_ms`) + `attribute_webhook_dispatch_cost.py` (`WebhookRate.flat_per_attempt + egress`); production binding at `harness-cp/src/harness_cp/validator_framework.py` + `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py`. Scope: ~5-7 commits per per-surface module + per-surface binding + integration tests + batch-28 retirement event filing. After U-OD-40 lands, OD-5 PARTIAL → RETIRE-READY transit available (mirror H_T-AS-8d operator-opt-in RETIRE-READY pattern with structural-criterion-B MET via 4-of-4 surface-coverage).

---

## §3 Class 3 informational findings

(None at batch-27.)

---

## §4 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-28 |
| Filer | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 |
| Classification | Within-PARTIAL surface-coverage advance (NOT a retirement-state transit); producer-site landing at the 2nd of 4 billable dispatch surfaces |
| Apply-arc shape | 3-commit single-session lifecycle: module + unit tests (`0e84c94`) + production binding + integration tests (`7e513c8`) + docs + ledger event (this commit). Cross-session continuity: module landed previous session at `ccad7fb`; production binding + ledger this session. |
| Source of detection | Empirical re-verification + advisor pre-substantive consultation (26th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`). Pre-substantive read of OD spec §C-OD-26 + §C-OD-28 confirmed CODE arc (not spec-fork arc). |
| Cross-axis cascade | ZERO. CXA v2.9 row 8 audit-write seam shared with LLM dispatch — tool-dispatch reuses same converter |
| Companion batches | `phase-7d-retirement-events-batch-25.md` (immediate predecessor at AS-axis), `phase-7d-retirement-events-batch-26.md` (immediate predecessor at AS-axis), `phase-7d-retirement-events-batch-11.md` (prior OD-5 PARTIAL transit at U-OD-38 LLM landing) |
| Status | ✅ FILED 2026-05-28 |
