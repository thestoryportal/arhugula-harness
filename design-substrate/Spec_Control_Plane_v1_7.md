# Specification — Control Plane v1.7

## Change-note (v1.6 → v1.7)

**Scope of revision.** Phase-7 in-CLI spec growth absorbing operator-ratified **U-RT-59 Fork 2 Path D** chunk per `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10 routing (selected 2026-05-20). Path D lands the CP-side surfaces that ARE spec-anchored at HEAD (per C-CP-16 §16.2 — the canonical CP per-response audit-ledger entry shape, which `CPAuditLedgerEntry` faithfully factors out). OD-side amendments (recognize CP-sourced audit entries; canonicalize `entry_hash`; resolve the `AuditPayload` shape vs ADR-D5 §1.4 deviation surfaced at discovery report §10) **remain deferred** to a dedicated drift-resolution arc.

**Amendment site.** ONE new sub-section.

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§13.5.1 (NEW) — `cp_audit_to_od_audit` converter contract** | Names the converter function; declares signature; specifies field-projection table from `CPAuditLedgerEntry` (C-CP-16 §16.2 — preserved verbatim) to OD `AuditLedgerEntry` (HEAD shape per `harness-od/src/harness_od/audit_ledger_types.py`); commits `audit.cp.*` namespace prefix for CP-sourced fields under OD `audit_namespace_attrs`; commits `prior_event_hash ≡ prior_entry_hash` semantic equivalence (Q1 ratification); commits caller-supplied `entry_core` source semantic (Q2(a) ratification — composer writes F2 entry FIRST, passes resulting state-ledger-entry hash to converter); commits `harness-cxa/` converter home (Q5 ratification); explicit OD-side drift dependency note. | Operator-ratified `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` Q1 + Q2(a) + Q4 + Q5; Path D landing-variant selection (§10 routing); C-CP-13 §13.5 audit-trail-link composition contract (preserved verbatim from v1.2); C-CP-16 §16.2 CP per-response audit-ledger entry shape (preserved verbatim); ADR-D5 §1.4 / §1.4.1 (`audit.*` namespace); `Cross_Axis_Composition_Document_v2_4.md` §2.3.7 (the U-CP-28 → U-OD-00 typed-seam edge — co-published with this revision); discovery prototype at `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` + tests (HEAD `99982de`). |

**Sections preserved verbatim from v1.6.** All v1.6 content outside the NEW §13.5.1 sub-section preserved unchanged. §25.2 (StepExecutionContext schema), §25.3.3.4 (dispatch step body amendment), §25.7 (failure-mode taxonomy), §25.9 (cost-attribution emission composition) all stand. §13.5 (LedgerEntryRef — preserved from v1.2) stands; §13.5.1 is added immediately below it. C-CP-13 contract surface declaration (preserved from v1.2) stands; §13.5.1 expands the contract's scope to include the cross-axis converter declaration per the Path D ratification.

**Status posture.** Proposed (v1.6) → **Proposed (v1.7)**. Adversarial-review pass scheduled at the implementation arc opening per Phase 7 sub-phase 7b discipline.

**OD-side drift dependency (load-bearing).** The converter contract at §13.5.1 references OD `AuditLedgerEntry` as the converter's output type — at HEAD that type is the code-canonical 3-field shape per `harness-od/src/harness_od/audit_ledger_types.py` which **deviates from ADR-D5 §1.4** (6-field F2-shape entry + 4 sqlite signature columns). The discovery report §10 surfaces this drift; resolution is deferred to a dedicated arc (Path B-revised-a / Path B-revised-b / Path A-revised — operator selection pending). v1.7 commits the CP-side semantics + field projection + namespace + entry_core source + converter home; the OD-side output shape semantics are inherited from HEAD code and are subject to revision when the drift-resolution arc lands. The §13.5.1 contract carries an explicit "subject to OD-side drift resolution per `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10" note to preserve operator visibility.

**Downstream absorption owed.** (a) Runtime spec amendment (§14.7.6 or equivalent — un-strike U-RT-59 AC #9 write half; specify composer step 8 F2-write of dispatch action BEFORE audit composition + audit-write composition via converter); (b) CP plan v2.14 absorption (cite §13.5.1 at U-CP-28 implements line); (c) `Cross_Axis_Composition_Document_v2_4.md` co-publication (this revision's companion); (d) converter code move from prototype home `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` → final home `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q5; (e) OD-side drift resolution arc.

---

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_7.md` |
| Status | **Proposed** — Phase-7 sub-phase 7b/7c in-CLI revision; U-RT-59 Fork 2 Path D landing |
| Revision | v1 → v1.1 → v1.2 → v1.3 → v1.4 → v1.5 → v1.6 (C-RT-17 StepExecutionContext) → **v1.7 (U-RT-59 Fork 2 Path D — §13.5.1 converter contract, 2026-05-20)** |
| Revision date | 2026-05-20 (v1.7 revision pass, same day as v1.6) |
| Phase | 7 — sub-phase 7b/7c; in-CLI per workspace convention; `spec-writer` skill (spec-revision-pass sub-mode) applies the operator-ratified Fork 2 Path D fix. |
| Skill | `spec-writer` (spec-revision-pass sub-mode) at v1.7 |
| Promotion path | Accepted at U-CP-28 plan absorption (CP plan v2.13 → v2.14) + implementation arc (composer step 8 + runtime spec amendment + converter code move to `harness-cxa/`) + un-strike U-RT-59 AC #9 write half |
| Source-set | All v1.6 inputs (preserved) + `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` (Q1–Q5 + §10 Path D selection operator-ratified 2026-05-20) + `Cross_Axis_Composition_Document_v2_4.md` (co-published) + `.harness/class_1_tension_u_rt_59_cp_to_od_audit_write_gap.md` (closure substrate) |
| Entry authorization | `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10 Path D ratification + `CLAUDE.md` §4.3 back-flow routing (Class 1 spec revision authorized in-CLI per workspace governance) |
| Exit gate | (a) CP plan v2.14 revision-pass consuming this §13.5.1 contract; (b) runtime spec amendment un-striking U-RT-59 AC #9 write half + specifying composer step 8 F2-write + audit-write composition; (c) converter code move to `harness-cxa/`; (d) OD-side drift resolution arc (independent — does NOT block this v1.7 landing) |

---

## §13 C-CP-13 — Sub-agent handoff context + audit-trail-link composition

[§13.1 HandoffContext payload schema, §13.2 Brief object structure, §13.3 Brief-authoring model-binding inheritance, §13.4 State summary composition, §13.5 Audit-trail-link composition all preserved verbatim from v1.2. §13.5.1 NEW at v1.7 — `cp_audit_to_od_audit` converter contract.]

### §13.5 Audit-trail-link composition with C-IS-10 §10.1

[Preserved verbatim from v1.2: declares `LedgerEntryRef` (action_id + entry_hash + actor) per IS C-IS-10 §10.1 state-ledger entry shape export; the audit-trail-link enables tracing sub-agent execution back to the parent ledger entry; merkle-root composition at fan-out close per C-CP-15 §15.2.]

### §13.5.1 CP→OD audit-write composition — `cp_audit_to_od_audit` converter contract (v1.7 NEW)

The CP-side per-response audit-ledger entry shape declared at C-CP-16 §16.2 (factor-out at `CPAuditLedgerEntry`, 8 fields with response-conditional optional hash fields per the 4-row table) is converted to an OD-shape audit-ledger entry at the cross-axis CP→OD seam. The converter is the typed seam for the U-CP-28 → U-OD-00 edge declared at `Cross_Axis_Composition_Document_v2_4.md` §2.3.7.

**Converter signature.**

```
cp_audit_to_od_audit(
    cp_entry            : CPAuditLedgerEntry,      // C-CP-16 §16.2 shape
    *,
    key_id              : str,                     // ADR-D5 §1.4.1 audit.signature.key_id
    algo                : SignatureAlgorithm = ED25519,  // ADR-D5 §1.4.1 audit.signature.algorithm
    entry_core          : StateLedgerEntryRef,     // F2 state-ledger entry reference (Q2(a))
) -> AuditLedgerEntry                              // OD-shape per harness_od.audit_ledger_types HEAD
```

**Field-projection table.** CP fields → OD `AuditPayload` slots + `audit_namespace_attrs` keys:

| CP field | CP type | → OD destination | Discipline |
|---|---|---|---|
| `action_id` | `ActionID` | `audit_namespace_attrs["audit.cp.action_id"]` | Anchor for CP↔OD cross-side join — names the CP action this audit entry corresponds to. |
| `gate_level` | `GateLevel ∈ {auto, ask, deny}` | `audit_namespace_attrs["audit.cp.gate_level"]` | StrEnum value pass-through. |
| `response` | `str ∈ {approve, edit, reject, respond}` | `audit_namespace_attrs["audit.cp.response"]` | Drives which conditional hash field is populated per C-CP-16 §16.2 row discipline. |
| `edited_proposal_hash` | `str` SHA-256 hex-64 \| `None` | `audit_namespace_attrs["audit.cp.edited_proposal_hash"]` (iff populated) | C-CP-16 §16.2 row 2 (`edit` response). Absent iff response ≠ `edit`. |
| `rejection_reason_hash` | `str` SHA-256 hex-64 \| `None` | `audit_namespace_attrs["audit.cp.rejection_reason_hash"]` (iff populated) | C-CP-16 §16.2 row 3 (`reject` response). Absent iff response ≠ `reject`. |
| `response_text_hash` | `str` SHA-256 hex-64 \| `None` | `audit_namespace_attrs["audit.cp.response_text_hash"]` (iff populated) | C-CP-16 §16.2 row 4 (`respond` response). Absent iff response ≠ `respond`. |
| `timestamp` | `str` ISO-8601 | `audit_namespace_attrs["audit.cp.timestamp"]` | Pass-through. |
| `prior_event_hash` | `str` SHA-256 hex-64 | `payload.prior_entry_hash` | **Direct re-use (Q1).** The C-IS-06 hash-chain link IS the OD audit-chain link semantically — both are SHA-256 over the prior canonical entry on the same IS-anchored hash chain (per C-IS-13 §13.5). No transformation. |
| — | — | `payload.entry_core: StateLedgerEntryRef` | **Caller-supplied (Q2(a)).** The dispatch composer MUST write an F2 state-ledger entry recording the dispatch action BEFORE composing the audit entry; the resulting `StateLedgerEntryRef` is passed to the converter. The audit `entry_core` therefore references the F2 entry of the audited action — preserving the IS-anchor invariant. Composer step specification owed to runtime spec (see §13.5.1 NOTE 2). |
| — | — | `signature_attrs: AuditSignatureAttributes` | Produced inside the converter via OD's `sign_audit_entry(payload, key_id, algo)` per ADR-D5 §1.4.1. Caller supplies `key_id` + `algo`. |
| — | — | `entry_hash: str` | Computed inside the converter per OD-side canonicalization recipe (see §13.5.1 NOTE 1). |

**Namespace commitment (Q4 ratification).** All CP-sourced fields land under the **`audit.cp.*` sub-namespace** within OD's `audit_namespace_attrs` per C-OD-05 §5.1 (the 15-namespace ingestion map; `audit.*` is OD-canonical, `audit.cp.*` is the CP-source extension). The C-OD-05 amendment recognizing `audit.cp.*` as a registered sub-namespace is owed to OD spec at the drift-resolution arc.

**`prior_event_hash` ↔ `prior_entry_hash` semantic equivalence (Q1 ratification).** CP `CPAuditLedgerEntry.prior_event_hash` (per C-CP-16 §16.2 + C-IS-06 hash-chain construction) and OD `AuditPayload.prior_entry_hash` (per C-OD-21 §21.2 + C-IS-13 §13.5) are semantically equivalent — both are SHA-256 hex-64 hash-chain links over the prior canonical entry on the same IS-anchored hash chain. The converter passes the value through unchanged.

**`entry_core` source semantic (Q2(a) ratification).** For CP-sourced audit entries, `AuditPayload.entry_core` references the F2 state-ledger entry recording the audited action (the sub-agent dispatch action). The dispatch composer MUST:

1. Compose the dispatch action's F2 state-ledger entry shape per C-IS-10 §10.1 (`action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash`).
2. Write the F2 entry via the runtime state-ledger writer; capture the resulting `StateLedgerEntryRef` (the IS-canonical reference to the persisted entry).
3. Compose the CP audit entry via `compose_dispatch_audit(...)` per existing C-CP-13 §13.5.
4. Pass `(cp_entry, key_id=..., algo=..., entry_core=<F2 ref from step 2>)` to `cp_audit_to_od_audit(...)`.
5. Append the resulting OD `AuditLedgerEntry` to `ctx.audit_writer` per C-RT-04 (runtime spec `Spec_Harness_Runtime_v1.md` §6).

The composer step specification (un-strike U-RT-59 AC #9 write half; expand step 8 to include the F2-write + converter call + audit-writer append) is **owed to the runtime spec amendment** at the implementation arc opening — NOT in v1.7 scope. v1.7 commits the CP-side converter contract; runtime owns the composer-step specification per `Spec_Harness_Runtime_v1.md` §14.7 authority.

**Converter home (Q5 ratification).** The converter implementation lives at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per the workspace `CLAUDE.md` §2.5 "harness-cxa/ hosts CXA seam instantiation" assignment. `harness-od/` is foreclosed by OD's "0 outbound cross-axis edges" invariant (`harness-od/CLAUDE.md` §2.2); `harness-cp/` would require a new CP→OD outbound package-import edge. The discovery prototype currently resides at `harness-runtime/src/harness_runtime/lifecycle/cp_audit_conversion.py` (HEAD `99982de`); the move to `harness-cxa/` is owed to the implementation arc.

**NOTE 1 — `entry_hash` canonicalization deferred.** The OD-side canonical recipe for `AuditLedgerEntry.entry_hash` is **not specified** at HEAD — `audit_ledger_types.py` declares the field but no canonical helper; ADR-D5 §1.4.1 commits `audit.signature.sha256` as "per-event SHA-256 hash over the ledger entry payload" but the payload shape itself is in drift between code (3-field `AuditPayload`) and ADR-D5 §1.4 (6-field F2 shape). The converter at HEAD uses the interim convention `sha256(payload.model_dump_json())`; canonicalization to a spec-anchored recipe is owed to the **OD-side audit-ledger drift resolution arc** per discovery report §10 (Path B-revised-a / Path B-revised-b / Path A-revised — operator selection pending). The runtime materialization of §13.5.1 inherits whatever recipe the drift-resolution arc commits.

**NOTE 2 — Composer step F2-write specification deferred.** The dispatch composer step amendment (steps 1–5 in the "`entry_core` source semantic" enumeration above) is **owed to runtime spec** (`Spec_Harness_Runtime_v1.md` §14.7 — the C-RT-17 sub-agent dispatch composer contract); not in CP spec v1.7 scope. CP spec v1.7 commits the CONTRACT for the converter; runtime spec commits the composer-step PROCEDURE.

**NOTE 3 — Cryptographic-payload-mismatch foreclosure.** A variant in which CP's signed `CPSignedAuditLedgerEntry` (with its own 5 `audit_signature_*` fields per C-CP-20 §20.4) is re-projected into OD `AuditSignatureAttributes` without re-signing is structurally foreclosed: CP signature is computed over the CP-shape payload; OD signature is over OD `AuditPayload` (different bytes). The algorithm enum values aligning (`ed25519` / `ecdsa-p256` / `rsa-pss-2048` per ADR-D5 §1.4.1) is necessary but not sufficient. The converter's signing posture is therefore fixed: accept the unsigned `CPAuditLedgerEntry`; build OD `AuditPayload`; call OD's `sign_audit_entry(payload, key_id, algo)` per ADR-D5 §1.4.1; assemble final `AuditLedgerEntry`.

**Cross-axis citation.**
- `Cross_Axis_Composition_Document_v2_4.md` §2.3.7 — the U-CP-28 → U-OD-00 typed-seam edge (co-published with this revision).
- `Spec_Operational_Discipline_v1_4.md` C-OD-21 §21.2 — OD `audit.signature.*` 4-attribute set + `sign_audit_entry` (canonical signing surface, IS the source of `AuditSignatureAttributes` the converter consumes).
- `Spec_Operational_Discipline_v1_4.md` C-OD-05 §5.1 — OD 15-namespace ingestion map (`audit.*` is OD-canonical; `audit.cp.*` sub-namespace recognition owed at the OD-side drift-resolution arc).
- ADR-D5 v1.3 §1.4 + §1.4.1 — per-persona-tier ledger cryptographic shape + 7 `audit.*` attribute names.
- `Spec_Harness_Runtime_v1.md` §6 C-RT-04 — runtime `audit_writer` field; consumer of the converter's output.
- `Spec_Harness_Runtime_v1.md` §14.7 — sub-agent dispatch composer contract (will absorb the composer-step amendment at the implementation arc).

**Deferred to implementation discretion.** (a) Signing-backend custody at `key_id` resolution (HSM / KMS / keystore per ADR-D5 v1.3 §1.4.1 deferral pattern); (b) tenant-scoping of `key_id` at multi-tenant-compliance per ADR-D5 §1.4 row 3 (operator-tunable `audit_signing_key_scope ∈ {deployment / tenant}`); (c) operator-side configuration of converter-callsite parameters (key_id, algo) at the runtime composition root.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_7.md` |
| Status | Proposed — Phase 7 7b/7c in-CLI U-RT-59 Fork 2 Path D landing |
| Predecessor | `Spec_Control_Plane_v1_6.md` (C-RT-17 StepExecutionContext) — preserved verbatim except for the new §13.5.1 sub-section |
| Substrate consumed | `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` (Q1 + Q2(a) + Q4 + Q5 + §10 Path D); `.harness/class_1_tension_u_rt_59_cp_to_od_audit_write_gap.md`; `Cross_Axis_Composition_Document_v2_4.md` (co-published) |
| Co-published with | `Cross_Axis_Composition_Document_v2_4.md` (new §2.3.7 CP→OD bucket with U-CP-28 → U-OD-00 edge) |
| Successor | `Implementation_Plan_Control_Plane_v2_14.md` (U-CP-28 absorbs §13.5.1 at next plan revision pass); `Spec_Harness_Runtime_v1.md` v1.7 §14.7 (composer-step amendment owed); OD-side drift resolution arc (Path B-revised-a / Path B-revised-b / Path A-revised — operator selection pending; INDEPENDENT of this v1.7 landing) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-20 |

*Filed at Phase 7 sub-phase 7b/7c as the U-RT-59 Fork 2 Path D landing. New §13.5.1 sub-section declares the `cp_audit_to_od_audit` converter contract; CP-side semantics + field projection + namespace + entry_core source + converter home all committed. OD-side drift dependency surfaced via §13.5.1 NOTE 1 + NOTE 2; runtime materialization owed to runtime spec amendment + OD-side drift resolution arc.*
