# Cluster 4-OD-D Partial-Close — U-OD-39/40/41 Cross-Axis Block

**Filed:** 2026-05-21 (end of cluster 4-OD-D impl arc)
**Closure status:** PARTIAL — 1 of 4 units landed (U-OD-38)
**Landed commit:** `7104fd7` (U-OD-38 cost-attribution at LLM dispatch site)
**Deferred units:** U-OD-39 / U-OD-40 / U-OD-41

---

## §1 Landed slice

**U-OD-38 — Cost-attribution at LLM dispatch site.** Production-path
materialization of OD spec v1.8 §C-OD-26.1 + §C-OD-26.2 row "llm_dispatch".
Every LLM dispatch invokes the 5-substep cost-attribution chain
post-provider-call + writes one audit-ledger entry. Flips H_T-OD-5
STILL-BOUNDED → PARTIAL (LLM-dispatch callsite live; tool-dispatch +
validator + webhook + audit-ledger projection extension still bounded).

Side effect: closes `[[fork-price-table-ref-substitution-retirement]]`
(criterion B met by grep — no production callsite invokes the old
`cost_formula.py:69` PRICE_TABLE_REF placeholder).

---

## §2 Deferred units + cross-axis blocks

### U-OD-39 — Cost-attribution at tool-dispatch site

- **Spec:** §C-OD-26.2 row "tool.dispatch" / "mcp.tool.call"
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py` (EXTEND)
- **Cross-axis dep:** **U-RT-67** (`RuntimeToolDispatcher` per C-RT-19) — **NOT LANDED**
- **Block:** The integration target file does not exist yet. U-RT-67 is in
  cluster L9-sexies (runtime tool-invocation, 8 units) per Closure Arc
  handoff §5 #2. Without RuntimeToolDispatcher composer, there is no tool
  dispatch site to wire cost-attribution INTO.
- **Routing:** Open L9-sexies; land U-RT-67; then re-open U-OD-39.

### U-OD-40 — Cost-attribution at validator + webhook sites

- **Spec:** §C-OD-26.2 rows "validator.evaluate" + "hitl.webhook.deliver"
- **Files:** `harness-cp/src/harness_cp/validator_framework.py` +
  `harness-runtime/src/harness_runtime/lifecycle/webhook_delivery_composer.py`
  (both EXTEND)
- **Cross-axis deps:**
  - **U-CP-60** (ValidatorFramework per C-CP-25 §25) — **NOT LANDED**;
    in cluster 10-CP-A (handoff §5 #5)
  - **U-RT-69** (WebhookDeliveryComposer per C-RT-20 §14.10) — **NOT
    LANDED**; in cluster L9-sexies (handoff §5 #2)
- **Block:** Both integration target files do not exist yet.
- **Routing:** Land L9-sexies + 10-CP-A; then re-open U-OD-40.

### U-OD-41 — Cost-record audit-ledger write composition

- **Spec:** §C-OD-26.3 audit-ledger write per cost-record
- **Files:** `harness-od/src/harness_od/cost_record_audit_writer.py` (NEW)
- **Cross-axis dep:** **U-CP-72** (cp_audit_to_od_audit converter extension
  to 8 prefixes incl `cost:`) — **NOT LANDED**; in cluster 10-CP-D
  (handoff §5 #10)
- **Inline workaround at U-OD-38:** The cost-record → CPAuditLedgerEntry
  projection currently inlined at
  `harness-runtime/src/harness_runtime/lifecycle/cost_attribution_llm_dispatch.py::_project_and_convert_audit_entry`.
  U-OD-41 will extract this to a standalone projector at the OD axis
  package as the U-CP-72 producer-side-rewrite seam canonicalizes the
  CPAuditLedgerEntry shape (today: HITL-semantic `gate_level=AUTO`
  no-op default for non-HITL cost entries).
- **Block:** Converter producer-side semantics for `cost:` prefix not yet
  canonicalized. The inline workaround is functional but bypasses the
  canonical projector seam.
- **Routing:** Land 10-CP-D U-CP-72; then re-open U-OD-41 with a clean
  projector extraction.

---

## §3 Architectural drift discovered + filed (Class 3, non-blocking)

### D1 — Spec §C-OD-26.1 "compute_cost(...)" facade vs chain reality

Spec sample uses `cost_chain.compute_cost(span_ref, parent_idempotency_key,
span_attributes)` as a single facade method. The existing
`RuntimeCostAttributionChain` does not expose `compute_cost`; the chain has
granular 5-method surface (`compute_per_attempt_cost`, `compose_total_cost`,
`attach_idempotency_key`, `rollup_fanout`, `dedupe_on_replay`). U-OD-38
helper bridges this gap by composing the granular methods. Class 3 drift
candidate: either spec amendment to remove the facade or chain extension to
add it. Non-blocking.

### D2 — ProviderRates (Decimal) ↔ PriceRateEntry (float) bridge precision loss

OD spec §C-OD-28.4 invariant 2 mandates Decimal arithmetic throughout. The
existing `cost_formula._formula` uses float arithmetic. U-OD-38 introduces
`rate_table_bridge.provider_rates_to_price_rate_entry` which converts at
the bridge boundary, losing precision past ~15 sig digits. Full-Decimal
chain migration owed.

### D3 — Audit chain integrity placeholder

CPAuditLedgerEntry's `prior_event_hash` field is set to empty string at the
cost-attribution projector — follows the existing
`RuntimeHandoffRegistry.compose_dispatch_audit` pattern (handoff.py:216-218
docstring — placeholder "filled at write-time" discipline). Audit chain
validity is deferred. Same drift as the existing sub-agent dispatch audit
path; no new exposure.

### D4 — SpanRef as TypeAlias for OTel span vs prior code assuming constructible

`harness_od.otel_genai_base.SpanRef` is a `type SpanRef = _OTelSpan` TypeAlias
(Python 3.12 syntax). Some callsites assume `SpanRef(...)` constructor.
U-OD-38 helper sidesteps by passing the span_id string directly to
`attach_idempotency_key` (parameter unused beyond correlation per its
docstring). Class 3 drift candidate: either narrow `SpanRef` to a Newtype OR
update callsites to obtain real spans. Non-blocking at v1.

---

## §4 Retirement projection delta

| Substitution | Pre-U-OD-38 | Post-U-OD-38 |
|---|---|---|
| H_T-OD-5 (Cost-attribution 5-step chain) | STILL-BOUNDED | PARTIAL (LLM-dispatch live; tool/validator/webhook pending) |
| `[[fork-price-table-ref-substitution-retirement]]` | OPEN bounded X-AL-2 residual | **CLOSED** |

Cumulative retirement progress: 22/49 → ~23/49 (OD-5 at PARTIAL doesn't
count as full retirement per X-AL-2 strict reading; the PRICE_TABLE_REF
fork CLOSURE is the concrete delta).

---

## §5 Re-open routing

When operator chooses to fully close cluster 4-OD-D:

1. Open L9-sexies (8 units U-RT-63..70) — lands RuntimeToolDispatcher
   (U-RT-67) + WebhookDeliveryComposer (U-RT-69).
2. Open cluster 10-CP-A (4 units U-CP-58..61) — lands ValidatorFramework
   (U-CP-60).
3. Re-open U-OD-39 + U-OD-40 (now unblocked).
4. Open cluster 10-CP-D (2 units U-CP-71..72) — lands cp_audit_to_od_audit
   converter extension to 8 prefixes incl `cost:`.
5. Re-open U-OD-41 (now unblocked) — extracts the inline projector to a
   standalone module at harness-od.
6. Cluster 4-OD-D fully closes; H_T-OD-5 RETIRED at full landing.

---

## §6 Workspace state at filing

- **Worktree:** `worktree-remaining-work-closure-arc-phase-a` at HEAD `7104fd7`
- **Workspace tests:** 2403 green (+7 over post-4-OD-C baseline)
- **Cluster status:**
  - 4-OD-A: CLOSED (3 commits `1efc5ea`/`1dd098e`/`461ba5e`)
  - 4-OD-C: CLOSED (4 commits `1daeda0` → `404fef7`)
  - 4-OD-D: PARTIAL (1 commit `7104fd7`; 3 units deferred)
- **Cumulative impl commits on worktree:** 8 (3 + 4 + 1)
