# U-RT-59 Fork 2 — CP→OD audit-write Discovery Report

**Posture:** discovery-grade — scopes the spec-amendment surface + open sub-questions for operator ratification. NOT a spec amendment. NOT runtime wiring. Mirrors U-RT-59 Fork 1's discovery-first pattern (`84edc30` → `d64d8cf`).

**Filed:** 2026-05-20.
**Authored by:** discovery pass per `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]` resolution scoping.
**Companion artifacts:**
- Prototype converter: `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` (DISCOVERY-GRADE; not wired)
- Round-trip test: `harness-runtime/tests/test_cp_audit_conversion.py`

---

## 1. Problem restatement

Per `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]`: CP composer produces `CPAuditLedgerEntry` (CP-shape, 8 fields, unsigned at compose site); OD `RuntimeAuditLedgerWriter.append(tenant_id, audit_entry)` consumes a *pre-signed* `AuditLedgerEntry` (OD-shape: `payload` + `signature_attrs` + `entry_hash`). The two types are structurally distinct; **no converter exists at HEAD; no design-phase artifact specifies one.**

U-RT-59 AC #9 write half was STRUCK at landing per `[[halt-route-split-AC-pattern]]`. This discovery scopes the surface owed to close that strike.

---

## 2. Variant foreclosed

The fork file referenced Variant A vs B at high level. **One variant is foreclosed before we start:**

- ~~Variant: accept already-signed `CPSignedAuditLedgerEntry`, project CP's 5 `audit_signature_*` fields → OD `AuditSignatureAttributes`, no re-sign.~~
  - Foreclosed: CP signature is computed *over the CP-shape payload* (`CPAuditLedgerEntry`). OD `AuditSignatureAttributes` is computed *over `AuditPayload`* (different fields, different bytes). Re-projecting CP's signature into the OD slot ships a signature that won't verify against the OD payload it's attached to. The `SignatureAlgorithm` enum values aligning (`ed25519` / `ecdsa-p256` / `rsa-pss-2048`) is necessary but not sufficient.

So the live variant is: **accept the unsigned `CPAuditLedgerEntry`; converter builds OD `AuditPayload`; converter calls OD `sign_audit_entry(payload, key_id, algo)` to produce `AuditSignatureAttributes`; converter assembles final `AuditLedgerEntry` with computed `entry_hash`.** The remaining design questions are *how* to project, *where* to source the synthesized fields, and *where* to home the converter.

---

## 3. Field-projection table

CP `CPAuditLedgerEntry` (8 fields per `harness-cp/src/harness_cp/per_step_override_evaluator.py:48`) → OD `AuditLedgerEntry` (3 fields: `payload` + `signature_attrs` + `entry_hash`).

| CP field | Type | → OD destination | Notes |
|---|---|---|---|
| `action_id` | `ActionID` | `audit_namespace_attrs["audit.cp.action_id"]` | String-coerced. Anchor for cross-side join (this audit entry corresponds to CP action X). |
| `gate_level` | `GateLevel` (`{auto, ask, deny}`) | `audit_namespace_attrs["audit.cp.gate_level"]` | StrEnum value. |
| `response` | `str` (`{approve, edit, reject, respond}`) | `audit_namespace_attrs["audit.cp.response"]` | Drives which conditional hash field is populated. |
| `edited_proposal_hash` | `str \| None` | `audit_namespace_attrs["audit.cp.edited_proposal_hash"]` iff present | Per C-CP-16 §16.2 row 2. |
| `rejection_reason_hash` | `str \| None` | `audit_namespace_attrs["audit.cp.rejection_reason_hash"]` iff present | Per C-CP-16 §16.2 row 3. |
| `response_text_hash` | `str \| None` | `audit_namespace_attrs["audit.cp.response_text_hash"]` iff present | Per C-CP-16 §16.2 row 4. |
| `timestamp` | `str` (ISO-8601) | `audit_namespace_attrs["audit.cp.timestamp"]` | Pass-through. |
| `prior_event_hash` | `str` (SHA-256 hex-64) | `payload.prior_entry_hash` | **Direct re-use.** The C-IS-06 chain link IS the OD audit-chain link semantically (both are SHA-256 over prior canonical entry). Spec ratification needed (see §5 Q1). |
| — | — | `payload.entry_core: StateLedgerEntryRef` | **NOT derivable from CP entry alone.** See §5 Q2 — unresolved sub-question. |
| — | — | `signature_attrs` | Produced by `sign_audit_entry(payload, key_id, algo)`. Caller injects `key_id` + `algo`. |
| — | — | `entry_hash` | Computed by converter; convention TBD (see §5 Q3). |

**Namespace prefix convention `audit.cp.*`** is provisional, not spec-fixed. Per C-OD-05 §5.1 the 15-namespace ingestion map enumerates `audit.*` as the OD canonical namespace; `audit.cp.*` as a CP-source sub-namespace is the natural extension but requires spec ratification (see §5 Q4).

---

## 4. Spec-amendment surface

| Artifact | Section | Amendment |
|---|---|---|
| `Spec_Control_Plane_v1_7.md` (bump from v1.6) | §13.5 | Add CP→OD audit-write composition contract: name `cp_audit_to_od_audit` converter signature; cite the field-projection table from §3 here; commit to `audit.cp.*` namespace prefix or alternative. |
| `Spec_Operational_Discipline_v1_5.md` (bump from v1.4) | §14.5 | Recognize CP-sourced audit entries: define what `AuditPayload.entry_core` resolves to for CP-sourced entries (the source-state-ledger entry being audited; OR a synthesized ref with documented opacity); confirm `prior_entry_hash` semantic equivalence with CP `prior_event_hash`. |
| `Cross_Axis_Composition_Document_v2_4.md` (bump from v2.3) | §2.3 | Add new edge: CP §13.5 → OD `audit_writer.append`. Classify as genuine-typed-seam (Pattern P1 — direct typed call across MCP boundary). Pull bucket totals: CP→OD = 1 (was 0). |
| `Implementation_Plan_Harness_Runtime_v1.7.md` (bump from v1.6) | §14.7.6 | Un-strike AC #9 write half; specify composer step 8b — call converter, append to `ctx.audit_writer` post-compose. Add `ctx.audit_writer` as a `RuntimeSubAgentDispatcher` constructor parameter. |
| `Implementation_Plan_Control_Plane_v2_11.md` (bump from v2.10) | §3 Cluster 5 | Add a new unit (or amend U-CP-14) to declare the converter + projection table at CP-side authority; pair-cite to OD plan. |
| `Implementation_Plan_Operational_Discipline_v2_12.md` (bump from v2.11) | §4.5 | Add inbound edge from CP if converter is OD-homed; OR pointer to harness-runtime/ if runtime-homed (see §5 Q5). |

**Six artifacts touched if Path A is ratified in full.** A reduced-scope variant (interim runtime-only landing with deferred-formalization) could land at `Spec_Harness_Runtime_v1.7` only and pointer-defer the CP+OD+CXA amendments — see §6.

---

## 5. Open sub-questions (operator decision points)

These are the unresolved spec-level choices the converter materialization cannot answer on its own authority. Each gates the corresponding amendment in §4.

### Q1 — Is CP `prior_event_hash` semantically equivalent to OD `prior_entry_hash`?

Both are SHA-256 hex-64 hash-chain links. CP cites "C-IS-06" (the IS hash-chain primitive). OD cites "C-IS-13 §13.5 discipline." If both reduce to the same IS chain, direct re-use is correct. If they are intended as *separate* chains (CP audit chain ≠ OD audit chain), re-use is wrong and the converter needs synthesis logic.

**Discovery prototype assumes:** direct re-use (semantically equivalent). Documented inline. **Test `test_converter_produces_well_formed_audit_ledger_entry` (+ the chain-verify tests) encode this assumption as an invariant; re-shape required if operator ratifies the separate-chains reading.**

### Q2 — What is `AuditPayload.entry_core` for a CP-sourced audit entry?

`entry_core: StateLedgerEntryRef` is an opaque `str`-newtype IS marker. For an OD-emission-site audit (today's only path), `entry_core` references a real F2 state-ledger entry. For a CP-sourced audit at the sub-agent dispatch composer:

- **Option (a):** the composer writes an F2 state-ledger entry recording the dispatch action *before* composing the audit, then the audit `entry_core` references that entry. (Adds a state-ledger write to the composer; cleanest semantic.)
- **Option (b):** `entry_core` references the parent action's F2 entry (the one CP `action_id` resolves to in some lookup table). (No new F2 write; requires a CP→IS lookup that may not exist at v1.6.)
- **Option (c):** synthesize `entry_core = StateLedgerEntryRef(f"cp-audit:{cp_entry.action_id}")` — opaque marker, no IS entry exists. (Cheapest; breaks the IS-anchor semantic of `entry_core`.)

**Discovery prototype uses Option (c) with explicit comment.** Operator picks the real answer.

### Q3 — How is OD `AuditLedgerEntry.entry_hash` computed canonically?

C-OD-14 §14.5.1 specifies "8-field SHA-256 composition + field-ordering" but no helper exists at HEAD (`grep -rn compute_entry_hash harness-od/src` returns no hits). Existing tests use arbitrary hex strings. The discovery converter uses the interim convention `sha256(payload.model_dump_json(sort_keys=True).encode())` and documents the gap.

**This gap pre-exists this fork.** It surfaces here because the converter is the first non-test caller that needs a real value. Operator decides whether this fork carries the `compute_entry_hash` helper (expanded scope) or whether it lands separately as a small OD-axis follow-up.

### Q4 — Namespace key discipline: `audit.cp.*` or alternative?

CP fields land in `audit_namespace_attrs: dict[str, str]`. The provisional prefix `audit.cp.*` extends C-OD-05's `audit.*` ingestion namespace. Alternatives: `audit.source.cp.*`, `cp.*` (unsuffixed), `audit.gate.*` (semantic grouping rather than source-axis grouping). Spec ratification at C-OD-05 §5.1 amendment.

### Q5 — Converter home axis

The fork file proposed `harness-od/src/harness_od/cp_audit_conversion.py`. **This breaks the OD posture** per `harness-od/CLAUDE.md` §2.2: "OD outbound (downstream): 0 — OD terminates the axis-level dependency graph." A converter at harness-od/ importing `CPAuditLedgerEntry` from harness-cp creates a new OD→CP edge and violates that invariant.

Candidate homes:

| Home | Pros | Cons |
|---|---|---|
| **`harness-runtime/lifecycle/cp_audit_conversion.py`** (prototype default) | Existing precedent: runtime is the cross-axis composition substrate; `audit_writer.py` already imports both `harness_cp` (composer side) and `harness_od.audit_ledger_types`. No axis-posture violation. | Runtime owns the cross-axis seam — discovery may land before CXA edge is formalized. |
| `harness-cxa/cp_to_od_audit.py` | CXA axis owns cross-axis composition by design. Clean home. | CXA module not yet populated; precedent unclear. |
| `harness-cp/cp_to_od_audit_conversion.py` | CP-owned authority over CP-shape projection. Aligns with "CP emits, OD ingests" D6 pattern. | Creates new CP→OD outbound edge (currently 0 per CXA v2.3 §2.3); CP CLAUDE.md §2.3 invariant change. |
| `harness-od/cp_audit_conversion.py` (fork file's proposal) | Pairs with OD's `sign_audit_entry`. | **Foreclosed by OD outbound-edge invariant.** Requires OD plan v2.12 §4.5 amendment to permit OD→CP outbound. |

**Discovery prototype goes to `harness-runtime/`** as the lowest-friction home for prototype validation. Final home is operator decision.

---

## 6. Reduced-scope landing variant (operator option)

The full Path A surface in §4 is six artifacts. A reduced-scope interim landing is possible:

- **Phase 1 (interim):** Land the converter at `harness-runtime/`; un-strike AC #9 at U-RT-59 via spec-level amendment to `Spec_Harness_Runtime_v1.7` §14.7.6 only. Defer CP / OD / CXA / plan amendments. Document in `harness-runtime/CLAUDE.md` as a runtime-internal cross-axis seam pending CXA formalization.
- **Phase 2 (formalization):** When the next CXA revision pass opens, formalize as a typed cross-axis seam at CXA v2.4 and back-port the spec edits to CP + OD plans.

Trade-off: gets H_T-CP-14 closer to RETIRED (audit-write end-to-end criterion) without spec-revision overhead; carries a Class 3 "convention-level seam pending formalization" item.

---

## 7. Recommended next steps (operator-gated)

1. **Operator ratifies** Q1 + Q2 + Q3 + Q4 + Q5 at next session.
2. **Pick landing variant** — full Path A (§4, six artifacts) OR reduced-scope (§6, two artifacts).
3. **Spec-writer arc** authors the chosen amendments (spec edits in-CLI per `[[design-substrate-divergence]]`).
4. **Implementation-planner arc** absorbs into runtime plan.
5. **Phase 7 implementation arc** un-strikes AC #9 + lands the wiring at `RuntimeSubAgentDispatcher.dispatch` step 8.
6. **Retirement audit** re-evaluates H_T-CP-14 (audit-write criterion) for full RETIRED transition.

---

## 8. Filing footer

| Field | Value |
|---|---|
| Discovery posture | Scoping only; no spec amendment; no runtime wiring |
| Prototype location | `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` |
| Prototype test | `harness-runtime/tests/test_cp_audit_conversion.py` |
| Companion fork | `[[class_1_tension_u_rt_59_cp_to_od_audit_write_gap]]` |
| Related family | `[[fork-cp-is-wiring-gaps]]` (DEFERRED Path D); `[[fork-cost-record-audit-ledger-wiring-residual]]` (Class 3 bounded) |
| Re-entry trigger | Operator ratification of Q1–Q5 + landing-variant selection |

---

*End of Fork 2 discovery report. See companion prototype + test for materializability evidence.*

---

## §9 Halt-on-application finding (added 2026-05-20 — pre-existing audit-ledger spec-vs-code drift)

**Context.** Operator ratified Full Path A + Q1–Q5 + chunk = CXA v2.4 + OD spec v1.5. Spec-writer arc opened against `Cross_Axis_Composition_Document_v2_3.md` (→ v2.4) + `Spec_Operational_Discipline_v1_4.md` (→ v1.5). **Halt** invoked per spec-writer FM-1 (`Phase-7 Spec-Writer SKILL.md` §"Failure modes") before any edit applied.

**Finding.** The OD-side audit-ledger Pydantic types declared at `harness-od/src/harness_od/audit_ledger_types.py` (`AuditPayload`, `AuditLedgerEntry`, `AuditSignatureAttributes`) are **specified in code only** — no design-substrate OD spec contract defines their shape. Specifically:

| Surface | Code authority | Spec authority | Status |
|---|---|---|---|
| `AuditSignatureAttributes` (4 `audit.signature.*` fields) | `audit_ledger_types.py:87-107` | C-OD-21 §21.2 (OD spec v1.2 preserved verbatim through v1.4) | **SPEC'd** — algorithm enum + 4 attributes match |
| `AuditPayload` (3 fields: `entry_core` / `audit_namespace_attrs` / `prior_entry_hash`) | `audit_ledger_types.py:67-85` | None canonical | **DRIFT** — payload shape not in spec |
| `AuditLedgerEntry` (3 fields: `payload` / `signature_attrs` / `entry_hash`) | `audit_ledger_types.py:110-118` | None canonical | **DRIFT** — wrapper not in spec |
| 8-field SHA-256 composition for `entry_hash` | `audit_ledger_types.py:117` docstring claims "C-OD-14 §14.5.1" | OD spec §14.5.1 is cost-attribution F2-state-ledger-extension, NOT audit-ledger | **DRIFT** — code docstring cites wrong section; canonical recipe missing |
| `StateLedgerEntryRef` opaque marker | `audit_ledger_types.py:44` | None | **DRIFT** — implicit resolution at U-OD-30 IS edge per code docstring; no spec contract pins the meaning |

**CP-side verified clean.** C-CP-16 §16.2 (CP spec v1.2 preserved through v1.6) IS the canonical per-response audit-ledger entry shape (4-row response-conditional table). `CPAuditLedgerEntry` (8 fields: `action_id` / `gate_level` / `response` / 3 conditional hash fields / `timestamp` / `prior_event_hash`) is a faithful factor-out — not drifted.

**The "8-field ordering" in Q3's ratification description was inherited from the audit_ledger_types.py docstring, which itself cites a wrong section.** The 8 fields in question are CP-side (C-CP-16 §16.2), not OD-side. OD `AuditPayload` has 3 fields; there is no canonical 8-field ordering at any OD spec section.

**What this blocks.**

- **OD spec v1.5 §14.5 amendment** (Q1 chain equivalence + Q4 namespace + Q2 entry_core resolution) cannot land cleanly: §14.5 doesn't contain audit-ledger schema; amendment site is undecided.
- **OD spec v1.5 §14.5.1 amendment** (Q3 canonical compute_entry_hash helper "per 8-field ordering") cannot land: no canonical 8-field ordering exists at OD spec; helper would land against an undefined surface.
- **CXA v2.4 new edge declaration** (CP §13.5 → OD `audit_writer.append`) — the producer-side contract cite IS valid (CP §13.5 = audit-trail-link composition contract; appropriate site for the converter contract amendment). The consumer-side cite "OD audit_writer.append" needs a contract reference — `RuntimeAuditLedgerWriter.append` is defined in `harness-runtime/.../audit_writer.py` per `Spec_Harness_Runtime_v1.md` v1.6 §6 (C-RT-04 `audit_writer` field), so the consumer contract is C-RT-04, NOT an OD spec contract.
- **CP spec v1.7 §13.5 converter contract** can land — §13.5 (audit-trail-link composition) is the right site per C-CP-13 §13.5. But the OD-side reciprocal (recognize CP-sourced audit entries) cannot land cleanly without resolving the OD-side payload schema drift first.

**Routing.** Pre-existing X-AL-3 drift surfaced at Fork 2 application; **not caused by Fork 2**. Resolution is a separate architectural arc against the entire OD audit-ledger payload schema (not Fork 2's scope). Operator decides:

| Path | Description | Cost |
|---|---|---|
| **A** | Author the missing OD audit-ledger schema contract first (new C-OD-NN at OD spec v1.5 OR §14.5 amendment lifting `audit_ledger_types.py` shapes verbatim into spec). Resume Fork 2 amendments against the new contract. | Large — full schema authoring + ADR back-reference reconciliation |
| **B** | Treat current code as canonical: lift `AuditPayload` + `AuditLedgerEntry` shapes into OD spec verbatim at an appropriate section (e.g., new §14.5.1 sub-section under C-OD-14, OR new C-OD-24 contract). Document as "code-first authoring lifted to spec" Class 3 drift retirement. Smaller scope than full re-authoring; codifies existing X-AL-3 drift. | Medium — spec authoring without re-deciding shapes |
| **C** | Defer Fork 2 entirely until the broader OD audit-ledger spec authoring lands as its own arc. | Zero today; Fork 2 stays at discovery-only |
| **D** | Land CXA v2.4 + CP spec v1.7 §13.5 converter contract only (the surfaces that ARE spec-anchored), defer OD spec v1.5 to a follow-on arc resolving the schema drift. **Reduced-scope landing** that closes 2 of 6 Path A artifacts. | Medium-small — partial Path A landing |

Spec-writer does not recommend; this is a design-substrate decision. The discovery prototype + tests at `70e58f2` are durable and unaffected (they encode the CODE-canonical shapes, which the drift resolution arc may then ratify into spec).

**Action this turn.** Halt. No spec edits. Append this §9 to discovery report + commit + surface to operator.

---

*§9 closes the application loop. Resume Fork 2 spec-writer arc after operator selects A/B/C/D and ratifies the OD audit-ledger schema target.*
