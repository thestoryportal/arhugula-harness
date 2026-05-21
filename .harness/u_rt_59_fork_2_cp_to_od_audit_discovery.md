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

---

## §10 Second-order halt — ADR-D5 §1.4 deviates from code (added 2026-05-20 after Path B ratification)

**Context.** Operator ratified Path B at §9 ("treat current code as canonical; lift verbatim into OD spec"). Spec-writer arc opened against OD spec v1.4 → v1.5 to author new C-OD-24 lifting `AuditPayload` + `AuditLedgerEntry` shapes. **Halted again before authoring** after reading ADR-D5 §1.4 + §1.4.1.

**Finding.** ADR-D5 §1.4 (canonical authority) commits a **structurally different** audit-ledger entry shape than the code:

| Surface | ADR-D5 §1.4 canonical commitment | Code at `audit_ledger_types.py` |
|---|---|---|
| Audit-ledger entry payload | F2 state-ledger entry shape: `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` — **6 typed fields per C-IS-05** | `AuditPayload` = 3 fields: `entry_core: StateLedgerEntryRef` (opaque str) + `audit_namespace_attrs: dict[str, str]` (untyped bag) + `prior_entry_hash` |
| Storage | Single sqlite `ledger_entries` table extended with 4 signature columns at team-binding+ tiers (`signature_value` / `signature_key_id` / `signature_key_period` / `rotation_correlation_id`) | Pydantic models only; no sqlite schema; OD `RuntimeAuditLedgerWriter.append` wraps into IS JSONL ledger via `EntryPayload` (different shape) |
| `entry_hash` recipe | `audit.signature.sha256` = "per-event SHA-256 hash over the ledger entry payload" — SHA-256 over the 6-field F2 shape (canonical, ADR-committed) | None at HEAD; discovery prototype uses interim `sha256(payload.model_dump_json())` over the 3-field `AuditPayload` |
| Signature attributes | 7 `audit.*` attributes per §1.4.1 (4 `audit.signature.*` + 3 v1.1 attributes) | `AuditSignatureAttributes` carries 4 of the 7 (the `audit.signature.*` subset) |
| Shape relationship | Audit-ledger entry IS the F2 entry (extended at team-binding+ with crypto columns) | Audit-ledger entry REFERENCES a separate F2 entry via opaque `entry_core` marker; carries its own dict of audit metadata |

**Net.** Code's audit-ledger types are not a faithful materialization of ADR-D5 §1.4. The deviation predates Fork 2 (authored at U-OD-00, OD plan v2.6 R5 §0.3, 2026-05-15; R5 Q-R5-3 ratified placement of `AuditSignatureAttributes` at U-OD-00 but did NOT ratify the `AuditPayload` 3-field shape — it's an undeclared authoring choice).

**Path B as ratified is incompatible with ADR-D5 §1.4.** "Lift code verbatim" would either:
(a) Codify a NEW deviation in OD spec v1.5, requiring an ADR-D5 amendment (Phase 3a/3b ADR revision back-flow per §4.3) to permit the deviation; OR
(b) Document the deviation as deliberate Class 3 in OD spec v1.5 — but Class 3 is for non-architectural drift, and divergence from a foundational ADR §1.4 commitment is architectural.

Either way, Path B's scope is materially larger than the §9 routing assumed. Spec-writer cannot pick between (a) and (b) — both are architectural decisions.

**Revised options for operator (supersedes §9 path enumeration):**

| Path | Description | Cost |
|---|---|---|
| **B-revised-a** | Lift code shapes to OD spec v1.5 as authored (3-field `AuditPayload` + dict bag); **amend ADR-D5 §1.4** to permit the deviation (or open council convening for the ADR amendment). Documents the deviation as the new canonical commitment. | Large — ADR revision is foundational (F1–F5 anchors); council convening per Project_Workflow §2.7.6 Class 1 ADR revision back-flow |
| **B-revised-b** | Lift code shapes to OD spec v1.5 with explicit "deliberate deviation from ADR-D5 §1.4" rationale; file Class 1 (not Class 3 — architectural) for ADR-D5 amendment in a follow-on arc. | Medium — defers the ADR revision but commits the spec to the deviation. The Class 1 is the architectural decision deferred |
| **A-revised** | Author OD spec v1.5 to align with ADR-D5 §1.4 (6-field F2-shape audit-ledger entry, sqlite-extended-table model); **REWRITE code** at `audit_ledger_types.py` + `audit_writer.py` + downstream callsites to match. | Large — spec authoring + code rewrite + test rewrite. The "honest" Path A: spec is the authority; code conforms. |
| **C** | Defer Fork 2 entirely until the broader OD audit-ledger drift resolution arc (`B-revised-a` OR `B-revised-b` OR `A-revised`) lands. Fork 2 stays at discovery-only. | Zero today; preserves operator decision authority |
| **D** | Reduced-scope Path A landing: CXA v2.4 + CP spec v1.7 §13.5 converter contract only (these surfaces depend on CP-side §16.2 which IS spec-anchored). Defer ALL OD-side spec work to the drift resolution arc. | Medium-small — closes the spec-anchored 2 of 6 Path A artifacts |

**Recommendation discipline.** Spec-writer does not recommend among B-revised-a / B-revised-b / A-revised / C / D. The choice between "ADR is authority; code must conform" vs "code is canonical; ADR must accommodate" is a load-bearing architectural call the operator owns. The discovery prototype + tests at `70e58f2` remain durable; they encode the code-canonical shapes and are unaffected by whichever resolution path lands.

**Action this turn.** Halt (second time). No spec edits. Append §10 + commit + re-surface.

---

*§10 closes the second-order application loop. The Fork 2 amendment cannot proceed against ANY spec target until the operator resolves the ADR-D5 deviation question. This is the foundational architectural choice; downstream Fork 2 work flows from it.*

---

## §11 Full Fork 2 spec arc CLOSED (added 2026-05-20)

All Fork 2 design-substrate work landed on main across 5 substantive commits + 2 closure-discipline commits this session. Implementation arc (composer wiring + tests + AC #9 un-strike + converter code move per Q5) is the only remaining work — distinct from spec authoring; handled at next session per phase-7-implementation skill discipline.

### §11.1 Resolution arcs landed

| Arc | Commit | Artifacts |
|---|---|---|
| Discovery + prototype | `70e58f2` | This report (§§1–8) + `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` + 12 round-trip tests |
| §9 first-order halt finding | `2a9f305` | §9 appended — OD audit-ledger schema in code only |
| §10 second-order halt finding | `99982de` | §10 appended — ADR-D5 §1.4 deviates from code (5 routing paths surfaced) |
| **Path D landing** | `ee5ae21` | `Cross_Axis_Composition_Document_v2_4.md` + `Spec_Control_Plane_v1_7.md` §13.5.1 converter contract |
| Path D closure | `7a2b39a` | Fork status OPEN-PARTIAL + Class 3 axis back-edge record |
| **Path B-revised-a landing** | `b3d9368` | `ADR-D5.md` v1.4 (§1.4 storage-form + §1.4.1 entry_hash recipe) + `Spec_Operational_Discipline_v1_5.md` C-OD-24 |
| ADR-D5 v1.4 close-out clarifications | `fd73ba1` | Status + canonical-scope clarifications |
| **Runtime spec v1.7 + CP spec v1.8 Form A** | (this turn) | `Spec_Harness_Runtime_v1.md` v1.7 §14.7.2 step 8 4-substep sequence + `Spec_Control_Plane_v1_8.md` (NOTE references resolved) |

### §11.2 Operator-ratified decision chain (Q1–Q5 + 3 routing decisions)

| Decision | Choice | Routing |
|---|---|---|
| Discovery deliverable | (B) Proposal + prototype converter | Initial scoping |
| Variant | Full Path A | 6-artifact spec amendments target |
| Q1 (chain equivalence) | Direct re-use (prototype default) | CP spec v1.7 §13.5.1 |
| Q2 (entry_core source) | (a) Composer writes F2 entry first | Runtime spec v1.7 §14.7.2 step 8b |
| Q3 (entry_hash canonicalization) | Author canonical helper (scope expansion) | OD spec v1.5 C-OD-24.5 |
| Q4 (namespace prefix) | `audit.cp.*` (prototype default) | OD spec v1.5 C-OD-24.6 |
| Q5 (converter home) | `harness-cxa/` | Code-move owed at implementation arc |
| §9 routing | Path B (lift code into spec) | Triggered §10 halt |
| §10 routing | Path D (land what's spec-anchored) | CXA v2.4 + CP spec v1.7 §13.5.1 |
| Post-§10 drift resolution | Path B-revised-a (lift code + amend ADR-D5) | ADR-D5 v1.4 + OD spec v1.5 |
| Implementation chunk | Spec amendments first (runtime v1.7 + CP spec v1.8) | This turn |

### §11.3 Pre-existing drift findings surfaced this arc

| Finding | Routing | Status |
|---|---|---|
| `c11-operator-local` SKILL.md missing (broken citation chain at ADR-D5 §1.4 row 1) | Class 3 — flagged in ADR-D5 v1.4 change-note | OPEN-FLAGGED (Class 3) |
| First CXA axis-level back-edge in project history (CP→OD per Fork 2) | Class 3 — `.harness/class_3_tension_cxa_v2_4_axis_back_edge.md` | OPEN-FLAGGED (Class 3 — owed Form A deltas at next CP/OD plan + workspace CLAUDE.md revisions) |
| `ctx.audit_ledger_writer` vs C-RT-04 `ctx.audit_writer` field name drift (item 1 of `.harness/class_3_tension_u_rt_59_spec_prose_drift.md`) | Resolved at runtime spec v1.7 §14.7.2 step 8d rewrite | RESOLVED |

### §11.4 Implementation arc — owed at next session

| Work item | Substrate authority |
|---|---|
| Composer wiring at `RuntimeSubAgentDispatcher` (constructor extension + step 8 4-substep sequence) | Runtime spec v1.7 §14.7.2 step 8a–8d |
| F2-write at step 8b (new code) | IS C-IS-10 + C-IS-11 + runtime spec v1.7 §14.7.2 step 8b |
| Converter call at step 8c (existing prototype invoked) | CP spec v1.7 §13.5.1 + v1.8 NOTE 2 resolution |
| `ctx.audit_writer.append` at step 8d (existing audit_writer.py append surface) | C-RT-04 + OD spec v1.5 C-OD-24 |
| AC #9 un-strike at U-RT-59 plan L9-ter | `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.5 → v2.6 |
| New fail class `RT-FAIL-SUB-AGENT-AUDIT-COMPOSE` at runtime spec §14 | Runtime spec v1.7 §14.7.2 step 8 failure-semantics paragraph (followup) |
| Integration test (parent + 3-step child + audit-chain verification via `verify_hash_chain_integrity`) | Runtime spec v1.7 §14.7.2 step 8 + OD spec v1.5 C-OD-24.3 invariant |
| Converter code move `harness-runtime/lifecycle/cp_audit_conversion.py` → `harness-cxa/src/harness_cxa/cp_audit_conversion.py` | CP spec v1.7 §13.5.1 Q5 ratification |
| CP plan v2.13 → v2.14 absorption at U-CP-28 (cite C-CP-13 §13.5.1 v1.7 + v1.8) | Implementation-planner discipline |
| OD plan v2.11 → v2.12 absorption at U-OD-00 (cite C-OD-24) | Implementation-planner discipline |
| Workspace `CLAUDE.md` §2.3 contract count update (OD 23 → 24) | Workspace housekeeping |

---

*§11 closes the Fork 2 spec arc. Discovery → halt → re-routing → Path D + B-revised-a + runtime spec v1.7 + CP spec v1.8 all landed across 7 commits in one session. Implementation arc remains as the only outstanding work; spec substrate is now coherent end-to-end. Re-enter at next session per phase-7-implementation skill discipline against the v1.7 §14.7.2 step 8 4-substep contract.*

---

## §12 Implementation arc CLOSED (added 2026-05-20, next session per §11 routing)

All §11.4 owed items landed in a single phase-7-implementation arc commit. Fork 2 is fully closed — spec + implementation + plan absorptions all coherent.

### §12.1 Implementation deltas landed

| Work item | Materialization site |
|---|---|
| Composer wiring (step 8 4-substep sequence) | `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py` — new `_compose_and_persist_audit(...)` helper threading 8a → 8b → 8c → 8d; 3 call sites (success/drained, child-failed, exception-bubble) consume via `raise_on_failure` flag per spec §14.7.2 step 8 failure-semantics paragraph |
| F2-write of dispatch action (8b) | `dispatch:<parent_action_id>:<child_index>` action_id pattern; action_id IS the `StateLedgerEntryRef` for 8c (per OD spec v1.5 C-OD-24.4 opaque-str discipline) |
| Converter move + import rewrite (Q5) | `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` → `harness-cxa/src/harness_cxa/cp_audit_conversion.py` + test file moved + harness-cxa `py.typed` marker added; converter docstring rewritten from DISCOVERY-GRADE framing to production-seam framing |
| AC #9 un-strike | `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.5 → v2.6 (new revision-history entry + rewritten AC #9 body citing the 4-substep contract) |
| New fail class | `Spec_Harness_Runtime_v1.md` v1.7 §14 failure-mode taxonomy — new row `RT-FAIL-SUB-AGENT-AUDIT-COMPOSE` with full trigger + behavior + suppression-on-failed-path discipline |
| New typed error | `harness_runtime.lifecycle.sub_agent_dispatch.SubAgentDispatchAuditComposeError` |
| Integration test | `test_three_sequential_dispatches_chain_through_audit_writer` (3 dispatches; 3 F2 dispatch entries + 3 OD audit entries persisted; IS hash-chain verification VALID per C-IS-06 §6.4 across all 6 entries) |
| CP plan absorption | `Implementation_Plan_Control_Plane_v2_14.md` — U-CP-28 `Implements:` extended with §13.5.1; CP→OD CXA edge acknowledged |
| OD plan absorption | `Implementation_Plan_Operational_Discipline_v2_12.md` — U-OD-00 `Implements:` extended with C-OD-24; X-AL-3 drift retirement documented |
| Workspace CLAUDE.md | §2.2 ADR-D5 v1.3 → v1.4; §2.3 CP spec v1.3 → v1.8 + OD spec v1.4 → v1.5 (OD contract count 23 → 24); §2.4 CP plan v2.10 → v2.14 + OD plan v2.11 → v2.12 + CXA v2.3 → v2.4 |
| Fork file status flip | `.harness/class_1_tension_u_rt_59_cp_to_od_audit_write_gap.md` Status header: OPEN-PARTIAL → **RESOLVED at implementation-arc landing 2026-05-20** |

### §12.2 Test posture at close

2283 workspace tests green at the implementation arc landing (up from 2278 at the spec-arc close session). Delta breakdown:

- +6 new step-8-specific unit tests (per-substep verification + failure semantics + dispatcher signature surface)
- +1 multi-dispatch IS-chain-integrity integration test
- −2 stale AC #9-partial-landing tests (`test_audit_entry_composed_via_handoff_registry` + `test_audit_entry_not_written_via_ctx_audit_writer_v1_6_mvp`) — the latter explicitly inverted at v1.7 since the dispatcher now DOES take an `audit_writer` kwarg

Net: +5 tests in `test_lifecycle_sub_agent_dispatch.py` (33 total in that file). Total workspace delta: +5 (2278 → 2283). The remaining gap is accounted for by the 12 converter tests at `test_cp_audit_conversion.py` (unchanged by the move) being counted under the new package home — git treats both files as renames, test count is preserved.

### §12.3 Items explicitly deferred

| Item | Routing |
|---|---|
| AC #12 — H_T-CP-10 / H_T-CP-13 / H_T-CP-14 retirement events | Phase 7d batch 4 per operator-ratified retirement audit cadence per Meta-Architecture §10.2.4 step 5 |
| Adversarial-review pass on runtime spec v1.7 | Scheduled per spec v1.7 status posture per Phase 7 sub-phase 7b discipline |
| `harness-cp/CLAUDE.md` + `harness-od/CLAUDE.md` Form A deltas for CXA v2.4 axis back-edge | Class 3 non-blocking per `.harness/class_3_tension_cxa_v2_4_axis_back_edge.md` |
| Class 3 prose drift for action_id-as-StateLedgerEntryRef deviation (spec narrative cites "entry_hash") | Carry-forward at runtime spec drift items; documented inline at the dispatcher module + the AC #9 v2.6 body |
| Class 3 §14.7.6 residual `audit_ledger_writer` field-name occurrences (4 of original 5) | Carry-forward — step 8 site was resolved at v1.7 step 8d rewrite; §14.7.6 prose absorption owed at next runtime spec revision pass |
| Operator-tunable `audit_signing_key_id` / `audit_signing_algorithm` surface | Deferred per spec §14.7 "Deferred to implementation discretion" + ADR-D5 v1.4 §1.4.1 (HSM / KMS / keystore deferral) — v1.7 MVP binds deployment-default `harness-runtime-dev` / `ED25519` |

### §12.4 Substitution retirement re-evaluation

The §11 X-AL-2 retirement implications at runtime spec v1.7 §14.7 are now testable end-to-end at production callsite:

- **H_T-CP-10 RETIRE-READY** — topology dispatcher + `is_topology_permitted` predicate operational at composer step 4. Condition B verified end-to-end via the 3-dispatch integration test (each dispatch traverses the predicate gate).
- **H_T-CP-13 RETIRE-READY** — `RuntimeHandoffRegistry.dispatch(...)` + `HandoffContext` composition operational at composer steps 2–3. Verified at `test_dispatch_invokes_handoff_registry_with_step_context_seeds` + `test_handoff_context_composed_per_v1_6_mvp_table`.
- **H_T-CP-14 PARTIAL → RETIRE-READY (single-sub-agent slice)** — `subagent.*` + narrow `topology.*` namespace emission at production span hierarchy verified at `test_subagent_span_carries_7_subagent_attributes` + `test_subagent_span_carries_2_narrow_topology_attributes`.

Operator ratifies the retirement transitions at Phase 7d batch 4 retirement audit per X-AL-2 strict-reading discipline.

---

*§12 closes the U-RT-59 Fork 2 implementation arc. Spec authority (CXA v2.4 + CP spec v1.7/v1.8 + ADR-D5 v1.4 + OD spec v1.5 + runtime spec v1.7) + code substrate (dispatcher + converter + bootstrap) + plan substrate (CP v2.14 + OD v2.12 + atomic-decomp v2.6) + workspace CLAUDE.md all coherent end-to-end. Fork file flipped to RESOLVED. The Fork 2 arc — surfaced 2026-05-20 at U-RT-59 landing — closes the same session day across 9 commits (8 spec + 1 implementation).*
