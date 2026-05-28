# Bounded Residual — `SpanCostRecord` → audit-ledger writer wiring

**Class:** 3 informational (no AC fails at HEAD; bounded residual carried)
**Status:** ✅ CLOSED (status-line refreshed 2026-05-28 Phase 1 status-cascade sweep per workflow v1.12 §7.4.7.3.B) — wiring path resolved at CXA v2.9 §2.3.7 row 8 cost-attribution audit-write seam + OD spec §C-OD-26.6 `CostRecordAuditPayload` + U-OD-41 production landing. Producer: `harness-od/src/harness_od/cost_record_audit_writer.py` projects `SpanCostRecord` → `CostRecordAuditPayload` (12 fields → 4 audit_cp_* common + 5 cost-specific) → routes through `cp_audit_to_od_audit` converter via `cost:` action_id prefix → audit-ledger ingestion. Species 3 stale-carry per workflow v1.12 §7.4.7.2.

**Status:** 🛑 OPEN — bounded residual; carried forward *(historical, predates 2026-05-24 CXA v2.9 row 8 + U-OD-41 landing)*
**Filed:** 2026-05-20 alongside CP spec v1.5 §25.9 absorption (`.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` resolution arc)
**Trigger:** Pattern P2 candidate caught at v1.5 spec-writer audit; conflation of *carrier production* vs *audit-ledger emission* surface.

## The gap

CP spec v1.5 §25.9 specifies step-body-owned cost-attribution chain invocation that produces a `SpanCostRecord` carrier (12-field, per OD plan v2.8 §3.5.3 D-5). It explicitly does NOT specify the downstream wiring that writes the `SpanCostRecord` to the OD audit ledger.

**What's specified at v1.5 (in scope):**
- Step body invokes `ctx.cost_chain.compute_per_attempt_cost(inputs, rates)` → produces a per-attempt cost float per OD spec v1.3 §14.1.
- Step body invokes `ctx.cost_chain.compose_total_cost(...)` → produces a `SpanTotalCost` per §14.2.
- Step body composes the 12-field `SpanCostRecord` carrier.
- Step body invokes `ctx.cost_chain.attach_idempotency_key(...)` to set the parent's `idempotency_key` per §14.4 (the JOIN contract).
- Output is the `SpanCostRecord` carrier.

**What's NOT specified (out of scope at v1.5):**
- Where the produced `SpanCostRecord` is written.
- Whether the audit-ledger writer at `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py` consumes `SpanCostRecord` directly or via an intermediate composition (e.g., a `CostAttributionEntry` ledger row).
- The §-pin at OD spec C-OD-NN that owns the audit-ledger `SpanCostRecord` ingestion contract (OD has 23 contracts C-OD-01 through C-OD-23; the `harness-od/CLAUDE.md` §1.3 reference to "8-row audit-ledger enumeration ← U-OD-20 ← C-OD-14 §14.5.2" is unverified at this audit and may itself be inaccurate — §14.5 sub-tree at OD spec v1.3 is the F2-12 trace-ingestion dedup algorithm + replay-aware orthogonality + cause_attribution invariance + per-attempt cost-attribution discipline; not the audit-ledger schema as such).
- The wiring path: does the cost-attribution invocation block return the `SpanCostRecord` to its caller (the step body), which then calls a separate writer? Does the chain itself write? Is the carrier accumulated on `ctx` and flushed at workflow close?

## Why this isn't blocking the U-RT-49 AC un-strike

The AC text is "cost attribution chain produced an entry." The smoke test materializes carrier production via the chain — chain invoked, `SpanCostRecord` produced, idempotency-key joined per §14.4. AC literally satisfied. The audit-ledger write site is a separate downstream surface that doesn't exist at HEAD (the `audit_writer` module wraps the IS ledger writer; no `SpanCostRecord`-specific append surface).

## How this differs from the `PRICE_TABLE_REF` residual

| Surface | What's deferred | Why |
|---|---|---|
| `PRICE_TABLE_REF` (`fork_price_table_ref_substitution_retirement.md`) | The per-provider rate table data | X-AL-2 second-criterion-unmet (substituted H_E surface still invoked); requires authoring rate tables for committed providers |
| `SpanCostRecord` → audit-ledger wiring (THIS record) | The composition path between chain output and ledger writer | Spec layer doesn't yet have a clear §-pin owning this composition; resolution may require an OD spec amendment naming the seam |

Both residuals carry forward; neither blocks U-RT-49 AC closure. They differ in resolution shape: `PRICE_TABLE_REF` is bounded substitution authoring; this record is potentially a spec gap (which spec-and-section owns the audit-ledger ingestion contract for `SpanCostRecord`?).

## Recommended verification (before resolution)

1. **Locate the canonical §-pin.** Read OD spec v1.3 C-OD-01 through C-OD-23 systematically for the audit-ledger emission contract. The `harness-od/CLAUDE.md` may have a citation error at §1.3 row "Audit-ledger schema + 8-field SHA-256 composition + field-ordering ← U-OD-20 ← C-OD-14 §14.5.1"; verify against the spec source text.
2. **Locate the audit-ledger writer surface.** `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py` exists; grep for whether it accepts `SpanCostRecord` writes, or only IS-substrate writes.
3. **Determine resolution class.** If OD spec specifies the seam but no implementation: minimal OD plan absorption + runtime wiring. If OD spec is silent on the seam: Class 1 OD spec amendment owed.

## Routing

Bounded residual; carries forward. NOT halt-execution. Surface as:
- Phase 7 sub-phase 7c CXA seam candidate (cross-axis composition between CP-produced `SpanCostRecord` and OD audit-ledger ingestion).
- OR Phase 7 sub-phase 7d substitution-retirement adjacent event (since the audit-ledger emission surface may itself be a deferred substitution).

## Cross-references

- `.harness/fork_u_rt_49_cost_attribution_invocation_underspec.md` — parent fork; §25.9 production contract is downstream of this carrier-production scope
- `Spec_Control_Plane_v1_5.md` §25.9 "Chain output" paragraph + "v1.5 amendment-site verification" line (cites this record)
- `Spec_Operational_Discipline_v1_3.md` C-OD-14 §14.4 (idempotency-key join contract — verified byte-exact at v1.5 spec-writer audit)
- `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py` — runtime-side audit-ledger writer (current shape NOT consuming `SpanCostRecord`)
- `harness-od/CLAUDE.md` §1.3 — contains an unverified citation that may need correction at next OD CLAUDE.md revision pass

## Provenance

- Filing event: 2026-05-20 at CP spec v1.5 §25.9 absorption pass — advisor-flagged Pattern P2 candidate during pre-commit audit; verification against OD spec v1.3 §14.4 confirmed §-pin mismatch in initial draft; §25.9 prose re-worded to drop false "emission target" claim; this record filed for the downstream wiring gap.
- Caught discipline: distinguish *carrier production* from *audit-ledger emission* — they are separate composition surfaces governed by separate spec §-pins.
