# Class 1 Fork — B1 branch-causality recording (Route X vs Route Y)

**Filed + RESOLVED:** 2026-06-13 · R-FS-1 arc #3 (B1-spec-1), design-phase posture. Class 1 (cross-axis: CP driver ↔ IS state-ledger schema). Resolved with rationale + decorrelated review (reversible spec-shape decision; no operator gate — composes a precedented D-derivative, no ADR/six-field change).

**Status:** ✅ RESOLVED → Route Y. CP-side recorded at `Spec_Control_Plane_v1_32.md` §25.13 (forward-coordination reference); IS-side sidecar **owed at coordinated B1-spec-1b**.

## §1 The fork

Under fan-out, the persisted `StateLedgerEntry` must record **branch causality** (`parent_action_id`, `branch_index`) + a **persisted cancellation marker** (`terminal_status`, per the cascade-cancel fork). The driver-transient `StepExecutionContext.parent_action_id` / `parent_entry_hash` are NOT persisted (the `EntryPayload` write contract is `extra="forbid"` — `state_ledger_write.py`), so durable recording requires a deliberate route:

| Route | Mechanism | IS cost | Assessment |
|---|---|---|---|
| **X — `action_id` encoding** | Compose `parent_action_id` + `branch_index` + `terminal_status` *into* the child entry's `action_id` (persisted F-layer field), per the HITL `compose_*_action_id` precedent + the §5 footer "action_id MAY encode … sub-class metadata". | Zero IS-schema change — but **not zero-work**: D3's resume contract needs a *defined* terminal-status encoding + a resume-side parser (a fragile string-parse read path). | **Rejected.** IS spec v1.3 Amendment 3 ratified that *structured traceability* MUST flow via a **sidecar**, not action_id-encoding (carriers kept separate to avoid conflation); branch causality + status is structured traceability. A string-parsed `terminal_status` is fragile vs a typed field. |
| **Y — D-derivative sidecar field** | A bounded `branch_metadata` sidecar `{parent_action_id, branch_index, terminal_status}` on `StateLedgerEntry` **+** `EntryPayload` **+** `_serialize_entry`/deserialize — the exact `procedural_tier_snapshot_ref` template (ADR-F2 §Consequences (c)). | A bounded IS amendment (C-IS-05 §5.x new D-derivative sidecar — additive; **zero six-field shape / §6 hash-chain / §7 read-write-contract / ADR-F2 §Decision change**). | **CHOSEN.** Follows the workspace's own ratified MAY/MUST separation; carries both branch causality AND the §25.15 cancellation marker D3 requires as a typed field; precedented. |

## §2 Resolution

**Route Y — bounded IS D-derivative `branch_metadata` sidecar.** The CP driver is the **producer** (composes branch metadata at branch-spawn + at cancel); the IS sidecar is the **persisted carrier**, authored at the coordinated **B1-spec-1b** IS amendment (a new C-IS-05 §5.x subsection, `procedural_tier_snapshot_ref` template). The CP spec v1.32 §25.13 names the seam + field shape as a **forward-coordination reference** (not a byte-resolvable cite — the IS section number is assigned at B1-spec-1b).

D1 confirmed: the hash chain stays single-parent linear, untouched — no second `prior_event_hash`, no DAG entry, no multi-parent chain (the heaviest-route foundational-ADR back-flow is avoided; serialized single-threaded append is ADR-F2's own prescribed boundary). Route Y is a precedented additive extension at the D-derivative layer, NOT an ADR-F2 §Decision revision.

Decorrelated: advisor (pre-substantive — flagged that branch causality is not free-on-existing-fields, the driver-transient-vs-persisted correction, recommended Y) + the `procedural_tier_snapshot_ref` precedent.
