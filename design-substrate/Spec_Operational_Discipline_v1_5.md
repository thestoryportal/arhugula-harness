# Specification — Operational Discipline v1.5

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_5.md` |
| Status | **Proposed** — Phase 7 sub-phase 7b/7c in-CLI revision pass (U-RT-59 Fork 2 drift-resolution Path B-revised-a) |
| Revision | v1 → v1.1 → v1.2 → v1.3 (F2-12 cascade Step 5b) → v1.4 (FF-2 collector-placement enum formalization, 2026-05-16) → **v1.5 (U-RT-59 Fork 2 drift-resolution Path B-revised-a; new C-OD-24 audit-ledger payload + entry composition contract; 2026-05-20)** |
| Revision date | 2026-05-20 (v1.5 revision pass) |
| Phase | 7 — sub-phase 7b/7c; in-CLI per workspace `CLAUDE.md` §4.3 (design-phase back-flow deprecated 2026-05-15 per `[[design-substrate-divergence]]`) |
| Predecessor | `Spec_Operational_Discipline_v1_4.md` (FF-2 collector-placement) |
| Entry authorization | Operator ratification 2026-05-20 of `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10 Path B-revised-a + Q1+Q2(a)+Q3+Q4 ratifications |
| Co-published with | `ADR-D5.md` v1.4 (§1.4 storage-form reconciliation + §1.4.1 entry_hash recipe tightening) |
| Exit gate | OD plan v2.11 → v2.12 revision pass (U-OD-00 absorbs new C-OD-24 contract); downstream `Spec_Control_Plane_v1_7.md` §13.5.1 NOTE 1 + NOTE 2 references resolve at follow-on Form A patch (v1.8) |

## Change-note (v1.4 → v1.5)

**Scope of revision.** Phase-7 in-CLI revision absorbing operator-ratified **U-RT-59 Fork 2 drift-resolution Path B-revised-a** per `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10 routing (selected 2026-05-20). Fork 2 surfaced that the OD-side audit-ledger Pydantic types (`AuditPayload` + `AuditLedgerEntry` + `AuditSignatureAttributes` + `AuditLedger` + `StateLedgerEntryRef`) were specified in code only at `harness-od/src/harness_od/audit_ledger_types.py` (authored at U-OD-00 per OD plan v2.6 R5 Q-R5-3 — placement ratification but NOT shape ratification; an undeclared X-AL-3 authoring drift). The discovery report §10 surfaced a second-order finding: the code's `AuditPayload` shape deviates from `ADR-D5.md` §1.4 (which committed SQLite-based audit-ledger storage + a row composing the audit entry against the F2 state-ledger entry shape).

Operator-ratified Path B-revised-a: **code is canonical; lift code shapes into spec verbatim; amend ADR-D5 §1.4 to permit the storage form.** v1.5 lands the OD-spec half: new C-OD-24 contract authoring the audit-ledger payload + entry composition shapes lifted from code. Co-published with `ADR-D5.md` v1.4 which amends §1.4 storage-form prose + §1.4.1 entry_hash recipe.

**One amendment site.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§24 (NEW) — C-OD-24 Audit-ledger payload + entry composition** | A new contract under the OD-axis contract enumeration, declaring 5 typed surfaces: §24.1 `AuditPayload`; §24.2 `AuditLedgerEntry`; §24.3 `AuditLedger`; §24.4 `StateLedgerEntryRef`; §24.5 `compute_entry_hash` canonical helper. Plus §24.6: CP-sourced audit-entry recognition (incorporates the Fork 2 Q1 + Q2(a) + Q4 ratifications already committed at CP spec v1.7 §13.5.1). Shapes lifted verbatim from `audit_ledger_types.py` HEAD. | Operator-ratified Path B-revised-a; landed code at `harness-od/src/harness_od/audit_ledger_types.py`; ADR-D5 v1.4 §1.4 + §1.4.1 (storage-form reconciliation co-published); CP spec v1.7 §13.5.1 (CP-side converter contract); ADR-D6 v1.2 (`audit.*` namespace at the 15-namespace ingestion map at C-OD-05); ADR-F2 §Decision (JSONL via IS state-ledger composition) |

**Sections preserved verbatim from v1.4.** All of v1.4's change-note + status block + §1.2 + §20.1 + filing footer preserved unchanged. §1 through §23 inherited from v1.4 (which inherits from v1.3 + v1.2). Contract count grows from 23 to **24** at v1.5 (C-OD-24 added).

**X-AL-3 drift retirement (closed by v1.5).** The pre-existing X-AL-3 drift surfaced at discovery report §9 + §10 — OD audit-ledger Pydantic types specified in code only without canonical spec contract — is RETIRED at v1.5 §24. The 5 typed surfaces are now spec-anchored at C-OD-24; `audit_ledger_types.py` HEAD shapes are the canonical referent. Future code changes to the audit-ledger types MUST conform to C-OD-24 OR route to a v1.6 revision pass.

**Status posture.** `Status: Proposed` preserved per workspace discipline. v1.5 enters the OD plan v2.12 revision pass (U-OD-00 absorbs new C-OD-24 contract).

**Downstream absorption owed.** (a) OD plan v2.11 → v2.12 revision pass — U-OD-00's `Implements` line gains C-OD-24 citation; (b) workspace `CLAUDE.md` §2.3 contract count update for OD (23 → 24); (c) `Spec_Control_Plane_v1_7.md` §13.5.1 NOTE 1 + NOTE 2 — references the OD-side drift resolution arc as pending; v1.5 + ADR-D5 v1.4 ARE that resolution; follow-on Form A patch (CP spec v1.8) updates the NOTE references.

---

## §24 C-OD-24 — Audit-ledger payload + entry composition (v1.5 NEW)

**Contract surface.** Typed Pydantic v2 surface for the OD-axis audit-ledger composition: payload shape + entry wrapper + ledger sequence + opaque IS reference + canonical entry-hash helper. Lifts the landed code at `harness-od/src/harness_od/audit_ledger_types.py` to canonical spec authority per the U-RT-59 Fork 2 Path B-revised-a drift resolution.

**PRD requirement(s) satisfied.** R-OD-04 (audit-ledger schema — payload composition surface) + R-OD-08 (bridging-arc traversal preservation across observability dimensions — audit-ledger entry composition dimension).

**ADR commitment(s) honored.** ADR-D5 v1.4 §1.4 (per-persona-tier ledger cryptographic shape — storage-form reconciled at v1.4); ADR-D5 v1.4 §1.4.1 (`audit.*` namespace + canonical `audit.signature.sha256` recipe — entry_hash tightened at v1.4); ADR-F2 §Decision (filesystem + git + JSONL event ledger — v1.5 canonical audit-ledger storage form); ADR-D6 v1.2 §1.2 (15-namespace ingestion map — `audit.*` enumeration); ADD §3.5 audit-ledger composition substrate.

**Cross-axis citation.** `Spec_Information_Substrate_v1.md` C-IS-10 §10.1 (state-ledger entry shape export — the `StateLedgerEntryRef` opaque marker resolves at U-OD-30's IS edge); `Spec_Control_Plane_v1_7.md` §13.5.1 (CP-side `cp_audit_to_od_audit` converter contract — consumes C-OD-24.1 + C-OD-24.2); `Spec_Action_Surface_v1.md` C-AS-15 §15.6 (sandbox observability namespace composition — no direct audit-ledger consumption, cited for cross-axis composition awareness).

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit ledger as foundational primitive); §11.10 (tenant-isolation at multi-tenant binding — audit-ledger entries carry per-tenant signature attributes per C-OD-21 §21.2 + ADR-D5 §1.4.1 multi-tenant-compliance row).

**Specification content.**

### §24.1 `AuditPayload` schema

The audit-ledger entry payload — the **signable core** over which `audit.signature.sha256` is computed (per ADR-D5 v1.4 §1.4.1 entry_hash recipe).

```
class AuditPayload:
    model_config = ConfigDict(extra="forbid", frozen=True)

    entry_core           : StateLedgerEntryRef         # §24.4 — opaque IS marker
    audit_namespace_attrs: dict[str, str]              # `audit.*` namespace attributes per C-OD-05 §5.1
    prior_entry_hash     : str                         # SHA-256 hex-64 hash-chain link per C-IS-13 §13.5
```

**Field semantics.**

- `entry_core: StateLedgerEntryRef` — an opaque marker referencing an IS-exported F2 state-ledger entry (the action being audited). Per §24.4, `StateLedgerEntryRef` is an opaque `str`-newtype; the concrete IS type resolves at U-OD-30's cross-axis IS edge (C-IS-10 §10.1).
- `audit_namespace_attrs: dict[str, str]` — namespace-prefixed audit metadata. The OD-canonical `audit.*` namespace per C-OD-05 §5.1 + ADR-D5 §1.4.1 declares 7 attribute names (`audit.signature.sha256`, `audit.signature.prior_hash`, `audit.actor.id`, `audit.signature.value`, `audit.signature.algorithm`, `audit.signature.key_id`, `audit.signature.key_period`); the `audit.cp.*` sub-namespace per §24.6 carries CP-sourced fields when the entry was converted via the CP→OD seam.
- `prior_entry_hash: str` — SHA-256 hex-64 hash-chain link to the predecessor entry's `entry_hash`. Composes with the F2 hash-chain construction discipline per C-IS-06 (canonicalize → SHA-256 → prior-event-hash chaining) and with the OD-side hash-chain integrity verification per C-OD-21 §21.2.

**ConfigDict commitments.** `extra="forbid"` (no untyped extensions; future fields land via v1.6+ amendment) + `frozen=True` (immutable post-construction; required for deterministic entry-hash computation per §24.5).

### §24.2 `AuditLedgerEntry` schema

The signed, hash-chained audit-ledger entry — the wire-format entity persisted to the audit ledger.

```
class AuditLedgerEntry:
    model_config = ConfigDict(extra="forbid", frozen=True)

    payload         : AuditPayload                     # §24.1 — signable core
    signature_attrs : AuditSignatureAttributes         # C-OD-21 §21.2 — 4-attribute audit.signature.* set
    entry_hash      : str                              # SHA-256 hex-64 per §24.5 canonical helper
```

**Field semantics.**

- `payload: AuditPayload` — the §24.1 shape, composed before signing.
- `signature_attrs: AuditSignatureAttributes` — the 4-attribute `audit.signature.*` record declared at C-OD-21 §21.2 (preserved verbatim through v1.4): `audit_signature_value`, `audit_signature_algorithm` (SignatureAlgorithm StrEnum ∈ `{ed25519, ecdsa-p256, rsa-pss-2048}` per ADR-D5 §1.4.1 + C-OD-21 §21.2), `audit_signature_key_id`, `audit_signature_key_period`. Produced by the U-OD-30 `sign_audit_entry(payload, key_id, algo) → AuditSignatureAttributes` function (per C-OD-21 §21.2 — preserved verbatim).
- `entry_hash: str` — SHA-256 hex-64 over `payload` per the §24.5 canonical helper; the value that `audit.signature.sha256` carries per ADR-D5 v1.4 §1.4.1.

**ConfigDict commitments.** `extra="forbid"` + `frozen=True` (immutable; pre-signed entry is wire-format-stable for the audit-ledger append discipline).

### §24.3 `AuditLedger` schema

An ordered, hash-chained sequence of `AuditLedgerEntry` instances — the bounded multi-tenant-cell ledger surface.

```
class AuditLedger:
    model_config = ConfigDict(extra="forbid", frozen=True)

    entries : tuple[AuditLedgerEntry, ...]             # §24.2 entries in chain order
    cell_id : CellID                                   # U-OD-01 multi-tenant cell key (cell-7, cell-8)
```

**Well-formedness invariant.** `entries[i].payload.prior_entry_hash == entries[i-1].entry_hash` for all `i > 0`. C-OD-24 declares the shape and documents the invariant; verification is U-OD-30's `verify_hash_chain_integrity(ledger) -> None | raises HashChainBreach` (preserved verbatim from C-OD-21 §21.2).

**Cell scope.** `cell_id: CellID` is restricted to multi-tenant cells (cell-7 / cell-8 per `Spec_Operational_Discipline_v1_2.md` C-OD-01 §1.1); the audit-ledger surface is the multi-tenant-compliance + team-binding tier per ADR-D5 §1.4. solo-developer (cell-1, cell-2, cell-3) emits audit entries in append-only form per ADR-D5 row 1 but does not maintain a hash-chained ledger by default.

### §24.4 `StateLedgerEntryRef` opaque IS marker

```
StateLedgerEntryRef = NewType("StateLedgerEntryRef", str)
```

An opaque `str`-newtype marker referencing an IS-exported F2 state-ledger entry. C-OD-24 declares the type name; the concrete IS-side resolution (the actual entry the marker points to) is at U-OD-30's cross-axis IS edge per C-IS-10 §10.1 (IS state-ledger entry shape export). At v1.5 the marker holds a string reference (typically the F2 entry hash or a constructed action_id like `cp-audit:<cp_action_id>` per the CP-sourced sub-namespace recognition at §24.6).

### §24.5 `compute_entry_hash` canonical helper

The canonical recipe for computing `AuditLedgerEntry.entry_hash` per ADR-D5 v1.4 §1.4.1 tightening.

```
def compute_entry_hash(payload: AuditPayload) -> str:
    """Compute the SHA-256 entry_hash over an AuditPayload.

    Canonical recipe per ADR-D5 v1.4 §1.4.1:
        SHA-256 over the Pydantic v2 canonical JSON serialization of payload.
    Returns hex-encoded 64-character string.
    """
    canonical = payload.model_dump_json()
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
```

**Recipe commitment.** SHA-256 over `payload.model_dump_json()` — the Pydantic v2 canonical JSON serialization. Under the §24.1 `ConfigDict(extra="forbid", frozen=True)` discipline, `model_dump_json()` produces a deterministic byte sequence for a given `AuditPayload` instance (field ordering is the model declaration order; no extra fields; no mutation). Deterministic across implementations conforming to Pydantic v2 + Python `hashlib.sha256`.

**Authority.** ADR-D5 v1.4 §1.4.1 tightening: `audit.signature.sha256` = "SHA-256 over the OD `AuditPayload` Pydantic JSON serialization". §24.5 is the canonical helper that materializes the recipe; the v1.4 ADR amendment + this §24.5 helper IS the spec-anchored entry_hash recipe at HEAD.

### §24.6 CP-sourced audit-entry recognition (Q1 + Q2(a) + Q4 ratifications)

When the audit entry was composed at the CP→OD seam via the converter declared at `Spec_Control_Plane_v1_7.md` §13.5.1 (`cp_audit_to_od_audit`), the OD-side audit-ledger contract recognizes the following discipline:

**Namespace prefix (Q4 ratification).** The `audit.cp.*` sub-namespace within `AuditPayload.audit_namespace_attrs` carries the projected CP-side fields (per CP spec v1.7 §13.5.1 field-projection table). `audit.cp.*` extends the OD-canonical `audit.*` namespace per C-OD-05 §5.1 + ADR-D5 v1.4 §1.4.1 — the sub-namespace pattern is the source-axis tagging convention for cross-axis-composed audit entries.

| CP-source attribute | Projection origin | Discipline |
|---|---|---|
| `audit.cp.action_id` | `CPAuditLedgerEntry.action_id` | Anchor for CP↔OD cross-side join |
| `audit.cp.gate_level` | `CPAuditLedgerEntry.gate_level` (StrEnum ∈ `{auto, ask, deny}`) | Pass-through |
| `audit.cp.response` | `CPAuditLedgerEntry.response` (∈ `{approve, edit, reject, respond}`) | Drives response-conditional discipline per C-CP-16 §16.2 |
| `audit.cp.edited_proposal_hash` | `CPAuditLedgerEntry.edited_proposal_hash` (iff response = edit) | Conditional per C-CP-16 §16.2 row 2 |
| `audit.cp.rejection_reason_hash` | `CPAuditLedgerEntry.rejection_reason_hash` (iff response = reject) | Conditional per C-CP-16 §16.2 row 3 |
| `audit.cp.response_text_hash` | `CPAuditLedgerEntry.response_text_hash` (iff response = respond) | Conditional per C-CP-16 §16.2 row 4 |
| `audit.cp.timestamp` | `CPAuditLedgerEntry.timestamp` (ISO-8601) | Pass-through |

**`prior_entry_hash` semantic equivalence (Q1 ratification).** OD `AuditPayload.prior_entry_hash` and CP `CPAuditLedgerEntry.prior_event_hash` are semantically equivalent — both are SHA-256 hex-64 hash-chain links over the prior canonical entry on the same IS-anchored hash chain per C-IS-06 + C-IS-13 §13.5. The converter (CP spec v1.7 §13.5.1) passes the value through unchanged; OD's hash-chain verification (C-OD-21 §21.2 — preserved verbatim) treats the CP-sourced value identically to OD-native values.

**`entry_core` source semantic (Q2(a) ratification).** For CP-sourced audit entries, `AuditPayload.entry_core` references the F2 state-ledger entry recording the audited action (the sub-agent dispatch action). The CP-side composer is responsible for writing the F2 entry BEFORE composing the audit entry; the resulting `StateLedgerEntryRef` is passed to the converter per CP spec v1.7 §13.5.1 step sequence. The audit `entry_core` therefore preserves the IS-anchor invariant of `StateLedgerEntryRef` even for CP-sourced entries.

**Recognition discipline.** C-OD-24's audit-ledger writer (`RuntimeAuditLedgerWriter.append` at `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py` per `Spec_Harness_Runtime_v1.md` §6 C-RT-04) accepts CP-sourced entries indistinguishable from OD-native entries — the `audit.cp.*` sub-namespace presence is the source-axis discriminator at the namespace level; structural shape and verification discipline are identical.

**Deferred to implementation discretion.** (a) Operator-side configuration of `audit.cp.*` namespace registration at the 15-namespace ingestion map at C-OD-05 §5.1 (the namespace IS recognized at v1.5; explicit row enumeration at C-OD-05 is owed at the next OD spec revision); (b) per-tenant scoping of `audit.cp.*` attribute persistence at multi-tenant-compliance cells per ADR-D5 §1.4 row 3; (c) future namespace extensions for other source-axis-tagged audit entries (e.g., `audit.as.*` if a future AS-axis seam emits audit entries).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_5.md` |
| Status | Proposed — Phase 7 7b/7c in-CLI U-RT-59 Fork 2 Path B-revised-a drift resolution |
| Predecessor | `Spec_Operational_Discipline_v1_4.md` (FF-2 collector-placement enum formalization) — preserved verbatim except for new C-OD-24 contract |
| Substrate consumed | `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` (Q1 + Q2(a) + Q3 + Q4 + §10 Path B-revised-a); `ADR-D5.md` v1.4 (co-published — §1.4 storage-form + §1.4.1 entry_hash); `harness-od/src/harness_od/audit_ledger_types.py` HEAD (code-canonical shapes lifted to spec); `Spec_Control_Plane_v1_7.md` §13.5.1 (CP-side converter contract — co-existing) |
| Co-published with | `ADR-D5.md` v1.4 (§1.4 + §1.4.1 reconciliation) |
| Successor | `Implementation_Plan_Operational_Discipline_v2_12.md` (U-OD-00 absorbs new C-OD-24 contract); workspace `CLAUDE.md` §2.3 contract count update (OD 23 → 24); `Spec_Control_Plane_v1_8.md` (follow-on Form A patch — updates v1.7 §13.5.1 NOTE 1 + NOTE 2 references) |
| Revision policy | In-CLI per workspace discipline (`CLAUDE.md` §4.3) |
| Date | 2026-05-20 |

*Filed at Phase 7 sub-phase 7b/7c as the U-RT-59 Fork 2 Path B-revised-a OD-side drift-resolution landing. New C-OD-24 contract lifts code-canonical audit-ledger shapes to spec authority; co-published with ADR-D5 v1.4 storage-form reconciliation. The Fork 2 OD-side drift surfaced at discovery report §9 + §10 RETIRED at v1.5 §24. Downstream owed: OD plan v2.12 absorption + workspace CLAUDE.md count update + CP spec v1.8 NOTE-reference follow-on patch.*
