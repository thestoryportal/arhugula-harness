# Architect recommendation — U-RT-35 Gap B (within-Path-A)

**Filed:** 2026-05-28 (Phase 6 back-flow open arc)
**Parent fork:** `.harness/class_1_tension_u_rt_35_cp_is_wiring_gaps.md` (RE-OPENED 2026-05-28; Option A authorized)
**Scope:** Within-Path-A decision; A/B/C routing already settled to A.
**Status:** RECOMMENDATION-AWAITING-OPERATOR-RATIFICATION

---

## What this resolves

Path A (full Phase 6 back-flow) is authorized. Within Path A, Gap B at the parent fork doc presents two structural patterns for the U-CP-14 `per_step_override_evaluator.emit_override_audit_entry` shape divergence and — load-bearing — for the 7 unmaterialized Gap A composers (U-CP-12 / U-CP-27 / U-CP-30 / U-CP-37 / U-CP-49 / U-CP-50 / U-CP-52), which are greenfield and will inherit whichever shape Gap B canonicalizes.

**Within-Path-A choice:**

- **(W) Widen `CPAuditLedgerEntry`.** Extend C-CP-16 §16.2 8-field shape with the 5 missing fields (`idempotency_key`, real `timestamp`, real `prior_event_hash`, output-carried `actor`, `response_hash`). U-CP-14 and the 7 greenfield composers all return the widened `CPAuditLedgerEntry`. Runtime callable signature at §12.3 treats `CPAuditLedgerEntry` as IS-compatible.
- **(S) Sibling typed variant.** Preserve `CPAuditLedgerEntry` verbatim at C-CP-16 §16.2 (8-field shape, signing contract, CP→OD converter at v1.7 §13.5.1 — all unchanged). Author NEW canonical CP-side state-ledger composer `emit_override_state_ledger_entry` returning the F2 state-ledger entry per C-IS-10 §10.1. U-CP-14 emits BOTH (existing `CPAuditLedgerEntry` for CP-audit role + new state-ledger entry for IS hash-chain role); the 7 greenfield composers emit ONLY the state-ledger entry (they have no CP-audit role today). Runtime callable signature at §12.3 receives the state-ledger entry directly.

---

## Recommendation: **(S) Sibling typed variant**

### Decisive structural argument

CPAuditLedgerEntry already carries a signing contract at C-CP-20 §20.4 → `CPSignedAuditLedgerEntry` signs over the 8-field shape. CP spec v1.7 §13.5.1 NOTE 3 ("Cryptographic-payload-mismatch foreclosure") canonicalizes the hash-bytes-immutability discipline: *"CP signature is computed over the CP-shape payload ... algorithm enum values aligning is necessary but not sufficient."* The workspace has already paid this hash-bytes-immutability price once at the CP→OD seam (rejected re-projection of `CPSignedAuditLedgerEntry` into OD `AuditSignatureAttributes` for exactly this reason).

Widening `CPAuditLedgerEntry` changes the signed bytes of the 8-field shape. Every existing CP-signing call site against §16.2 either (a) keeps signing the old 8-field projection — which means the widened fields are NOT actually part of the canonical CP audit record, defeating the widening — or (b) signs the new 13-field shape — which is a breaking change to C-CP-20 §20.4's signing contract and cascades to every CP-signature verifier (including OD's existing `cp_audit_to_od_audit` converter and downstream auditors). Neither outcome is bounded.

(S) preserves C-CP-16 §16.2 verbatim → C-CP-20 §20.4 signing contract unchanged → CP→OD converter at v1.7 §13.5.1 unchanged → CP-AL-2 typed taxonomy boundary respected.

### Workspace-pattern argument

The CP→OD edge is already typed-converter-shape: `cp_audit_to_od_audit` at harness-cxa per v1.7 Q5 ratification. The CP→IS edge is structurally analogous (a CP-source seam to a non-CP-axis sink). The architecturally consistent move is the same pattern: typed CP-side composer producing the sink-axis type at the seam. (S) IS that pattern. (W) is the *anti-pattern* — it conflates two typed ledger roles (CP per-response audit at C-CP-16 §16.2 vs IS-anchored hash chain at C-IS-10 §10.1) into a single widened shape whose semantics depend on which consumer reads it.

The two ledgers are conceptually distinct per the spec:
- **C-CP-16 §16.2 CPAuditLedgerEntry** — CP per-response audit record, CP-internal chain (`prior_event_hash` chains the CP-audit sequence), CP-signed, response-conditional optional hash fields.
- **C-IS-10 §10.1 StateLedgerEntry / EntryPayload** — IS-anchored hash-chain state record (`prior_event_hash` chains the IS-anchored canonical sequence per C-IS-13 §13.5), IS-computed hash-chain fields, fixed 6-field shape.

They share field *names* but not field *semantics*. (W) collapses this distinction silently. (S) preserves it.

### Greenfield-composer argument (load-bearing for the 20-25-unit cascade)

The 7 Gap A composers are greenfield — none has a CP-audit role today. Under (W) they would be authored as `CPAuditLedgerEntry` producers, inheriting the CP-audit role, the C-CP-20 §20.4 signing contract surface, the CP→OD converter cascade — a cross-axis cascade footprint they have no reason to carry. Under (S) they emit only the IS state-ledger entry, which is the only role spec §12.3 actually requires. (S) keeps the cascade footprint minimal.

### Cost of (S)

U-CP-14 emits two records per override-application (one CP-audit, one IS-state-ledger). This is acceptable: the records have distinct roles and distinct consumers. The duplication is at the *write* surface, not at the *semantic* surface. (W)'s "single widened record" is illusory — every consumer reads only the fields it cares about, so the semantic separation exists either way; (S) makes it typed.

### What changes vs what doesn't

| Surface | (S) impact |
|---|---|
| `CPAuditLedgerEntry` (C-CP-16 §16.2) | Verbatim, unchanged. |
| `CPSignedAuditLedgerEntry` (C-CP-20 §20.4) | Verbatim, unchanged. |
| `cp_audit_to_od_audit` (v1.7 §13.5.1) | Verbatim, unchanged. |
| C-CP-14 `emit_override_audit_entry` | Verbatim CP-audit emission, unchanged. NEW sibling site adds state-ledger emission. |
| NEW C-CP-14 `emit_override_state_ledger_entry` (or C-CP-NEW) | Returns `StateLedgerEntry`/`EntryPayload` per C-IS-10 §10.1. |
| C-CP-12 / C-CP-27 / C-CP-30 / C-CP-37 / C-CP-49 / C-CP-50 / C-CP-52 | 7 NEW state-ledger composers; ZERO CP-audit emission added. |
| Runtime spec §12.3 callable signature | NO change to (StateLedgerEntry, EntryHash) intent; Gap C drift (EntryPayload vs StateLedgerEntry, WriteResult vs EntryHash) remains Class 3 informational, deferred. |

---

## Sub-questions on field formulas (under (S))

These are decisions the spec amendment must resolve regardless of (S) vs (W). Surface them now so operator can ratify in one pass.

### Q1 — `idempotency_key` formula for override-application surface

C-CP-16 §16.2 does NOT declare an idempotency-key formula for `emit_override_audit_entry`. The IS state-ledger requires one. Two readings:

- **(a)** Reuse C-IS-10 §10.1 formula (whatever workflow-step composer dispatches use): `sha256(workflow_id || step_id || action_kind || canonical_args)`-shape.
- **(b)** Author override-application-specific formula: `sha256(workflow_id || step_id || override_id || policy_id)` — distinguishes override application from step dispatch.

Recommendation: **(b)**. Overrides are distinct semantic actions from step dispatches; same-workflow-same-step can have multiple overrides applied; collision risk under (a) is real.

### Q2 — `actor` carry-through

`emit_override_audit_entry` already accepts `actor: ActorIdentity` as input. The new state-ledger composer outputs it as the C-IS-10 §10.1 `actor: Actor` field. Mapping: identity preservation (the input ActorIdentity IS the output Actor). No transform needed beyond type-narrowing if ActorIdentity ⊆ Actor.

Recommendation: **direct re-use** (mirror v1.7 §13.5.1 Q1 `prior_event_hash ≡ prior_entry_hash` precedent — "semantically equivalent, pass-through").

### Q3 — `timestamp` source

C-IS-10 §10.1 requires real timestamp. Two readings:

- **(a)** Composer-site clock read (`datetime.utcnow().isoformat()` at emission).
- **(b)** Caller-supplied (workflow-driver-stamped at orchestration boundary).

Recommendation: **(a)**. Composer-site is closer to the actual event; caller-supplied risks drift between observation and emission.

### Q4 — `prior_event_hash` source

C-IS-10 §10.1 hash-chain semantics: prior_event_hash chains the IS-anchored canonical sequence (per C-IS-13 §13.5). IS computes this internally if the composer supplies `EntryPayload` (per Gap C drift). Two readings:

- **(a)** Composer supplies `StateLedgerEntry` with pre-computed `prior_event_hash` (matches spec §12.3 literal `Callable[[StateLedgerEntry], EntryHash]`).
- **(b)** Composer supplies `EntryPayload`; IS computes `prior_event_hash` internally (matches IS HEAD `append_ledger_entry` contract).

Recommendation: **(b)**. Matches IS HEAD contract; avoids composer-side chain-state tracking; aligns with the (Gap C) realistic callable shape. Flag Gap C resolution as future runtime-spec revision pass — out-of-scope for this revision.

### Q5 — `response_hash` source

C-IS-10 §10.1 6-field shape requires it. For override-application: the override has no "response" in the LLM-completion sense; it has a state-mutation outcome. Two readings:

- **(a)** Hash over override application outcome (post-override step-config canonical bytes).
- **(b)** Hash over override input (policy-evaluation result canonical bytes).

Recommendation: **(a)**. The state-ledger records what *happened*; the outcome bytes are the canonical record. (b) records intent, not effect.

### Q6 — Sibling composer naming

Two readings:

- **(a)** `emit_override_state_ledger_entry` (matches the fork-doc naming hint).
- **(b)** `emit_override_state_entry` (omits "ledger" — shorter; matches `EntryPayload` naming).

Recommendation: **(a)**. The "ledger" suffix names the destination ledger (IS state ledger), disambiguating from the CP-audit composer at the same site. Verbosity acceptable.

---

## Out-of-scope (flagged for future revisions)

- **Gap C — runtime spec §12.3 callable-signature drift.** `Callable[[StateLedgerEntry], EntryHash]` vs IS HEAD `Callable[[EntryPayload], WriteResult]`. Class 3 informational per fork doc; defer to next runtime-spec revision pass. Does NOT block this Phase 6 arc.
- **CXA-4 PARTIAL → RETIRE-READY post-design.** Per checkpoint `[[close-phase-complete-pre-design-batches-42-44]]` batch-42 §1.2. Separate routing.
- **IS-2 canonical-reading amendment.** Per advisor batch-39 path (β). Separate routing.

---

## Cascade footprint summary (under (S))

| Substrate | Change |
|---|---|
| CP spec v1.24 → v1.25 | NEW §16.X sub-section authoring `emit_override_state_ledger_entry` composer contract + 7 greenfield composer contracts (U-CP-12/27/30/37/49/50/52). Idempotency-key formula declared at §16.X.Q1. C-CP-16 §16.2 + C-CP-20 §20.4 preserved verbatim. |
| CP plan v2.27 → v2.28 | ~20-25 atomic units: U-CP-14 shape-revision unit (add sibling emission site) + 7 greenfield composer units + ~5 runtime-wiring units per spec §12.3. |
| CXA v2.15 → v2.16 §2.3.2 | CP→IS bucket: 17-edge canonical enumeration refresh; mark 1 materialized + 16 pending CP plan v2.28 landings. |
| Runtime spec | NO amendment in this revision (Gap C deferred). |
| C-CP-16 §16.2 | Verbatim, unchanged. |
| C-CP-20 §20.4 | Verbatim, unchanged. |
| v1.7 §13.5.1 `cp_audit_to_od_audit` | Verbatim, unchanged. |
| ZERO cross-axis cascade beyond CXA bucket refresh | OD spec unchanged; AS spec unchanged; IS spec unchanged. |

---

## Authority chain

- **Workspace `CLAUDE.md` §4.3 + I-5** — Phase 6 back-flow at design-phase workspace.
- **Workspace `CLAUDE.md` §4.4 X-AL-3** — no silent H_T design extension; Class 1 fork → operator ratification → spec/plan absorption.
- **`harness-cp/CLAUDE.md` §4.2 CP-AL-2** — typed taxonomy boundary.
- **CP spec v1.7 §13.5.1 NOTE 3** — hash-bytes-immutability discipline at signed-payload surfaces. *Decisive structural constraint for this recommendation.*
- **Project_Workflow_v1_12.md §2.7.6 + Phase_7_Kickoff §6** — back-flow routing protocol.

This recommendation does NOT hold decision authority. Operator decides Q1–Q6 + W/S at AskUserQuestion.
