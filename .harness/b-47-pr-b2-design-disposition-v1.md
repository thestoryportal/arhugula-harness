# B-47 PR B2 — design-cluster disposition (v1)

*Authored 2026-07-17 at the autonomous-loop design leg following PR #1036 (B2a). Scope: disposition the
B-47 close-out items (e)–(j) + (m) so the buildable engineering separates from the genuine design-phase
forks. Process-substrate (`.harness/`), mode-agnostic posture — no `design-substrate/**` edit in this leg.*

## 0. Load-bearing grounding correction — Tier-5 is a durability CLASS, not SQLite

The register's item (g) carried the phrase "intersecting C-OD-21 §21.2 and its own hash-chained-SQLite
storage commitment for the Tier-5 audit ledger." That is an **over-reading**, absorbed from an
out-of-family review framing (codex round-24 on PR B1) without spec verification — the exact
`[[insights-recs-workspace-blind]]` / stale-carry class the workspace disciplines exist to catch.

Verified at source:

- **OD §21.2** (`Spec_Operational_Discipline_v1_2.md:1184-1193`, last substantive definition) commits:
  Storage tier **"Tier-5 (per C3 five-tier durability)"**, hash-chain per C-IS-06, the four
  `audit.signature.*` attributes, always-sampled `audit.*`, and tamper-evidence independent of the trace
  backend. **No storage engine is named.** Its own "Deferred to implementation discretion" paragraph
  (line ~1207) defers key custody and tenant-isolation primitives.
- **ADR-D1 v1.2 (line ~39)** identifies Tier-5 by example as the **F2 state-ledger** durability class
  ("cursor journal (Tier-3) + F2 state-ledger (Tier-5) joined on `idempotency_key`").
- **Accurate SQLite lineage (corrected at codex round-7 of this leg — the earlier "every sqlite
  reference is Tier-3" claim was false):** ADR-D5 §1.4 *originally* committed SQLite-based
  audit-ledger storage (OD v1.5's change-note records discovering the code's deviation from it);
  **ADR-D5 v1.4 then reclassified that SQLite schema as a non-canonical, deferred C11-style
  persistence model and committed JSONL-via-IS-composition as CANONICAL storage at all three persona
  tiers** (§1.4 row table); OD v1.31 completed the reconciliation JSONL-canonical (porting
  `rotation_correlation_id`, explicitly "no SQLite migration, no new ADR"). The codex round-24
  framing echoed the SUPERSEDED v1.3-era commitment. The Tier-3 trace ring-buffer sqlite references
  are a separate data class.

**Consequence (stronger than first stated).** JSONL-via-IS-composition is not merely permitted — it
is the ADR-D5 v1.4 CANONICAL storage commitment, reconciled through OD v1.31. The hash-chained IS
state ledger + the B2a full-entry sidecar inhabit exactly that committed shape. A SQLite migration
would itself be the design-fork (reopening a settled ADR commitment), not the JSONL status quo. The
register text is corrected in the same PR as this doc.

## 1. Dispositions

| Item | Disposition | Rationale |
|---|---|---|
| **(e) signed-entry persistence** | **LANDED** (PR B1/B2a) | Sidecar-first durable full-entry store; 49+18 codex rounds + 2 merge-gates of hardening. |
| **(g) disk-backed membership index** | **Impl-discretion engineering** — registered as a BUILD item, no spec surface | Membership must prove absence ⇒ needs complete knowledge; the in-memory index rebuilds by full fold today (correct, O(history) at restart). A disk-backed index (e.g. the stdlib `sqlite3` module — available on the Python 3.12 baseline, unlike `dbm.sqlite3` which is 3.13+ — or an offset-checkpointed index snapshot beside the sidecar) is a pure performance optimization within Tier-5's committed properties. No fork needed. |
| **(h) per-family chain verifier** | **Impl-discretion BUILD item** (the natural next impl arc) | CXA §0.3 (v2.10, last substantive definition) action-id prefixes discriminate families; the B2a reader already documents the non-single-chain contract. The verifier must be PRODUCER-AWARE, not merely prefix-partitioned (codex round-3 on this leg): cost projection defaults `prior_event_hash` to genesis on EVERY entry (`cost_record_audit_writer.py:50`) and HITL uses `_empty_summary_hash()` (`hitl_gate_composer.py:1235`) — chain-verifying those families would fail on the second entry with no tampering. Policy: chain-verified = ONLY families with real chain-position wiring today — the redaction-token family, discriminated by the `audit.redaction_token.*` NAMESPACE KEYS the composer stamps (NOT by entry_core/action-id prefix, which misses caller-supplied `entry_core` rows — the map's own `_seed_chain_from_durable_tail` documents this, PR B1 codex round-39); genesis-per-entry families — cost, HITL, AND sub-agent dispatch (`sub_agent_gate_level_descent.py:215`, codex round-5) — get per-entry CONTENT-HASH verification only. Signature verification through a backend is OUT of B-49's scope (codex round-7): §21.2.1 explicitly leaves verification out of scope and `verify_hash_chain_integrity` never touches `signature_attrs`; a backend-aware verification API (key/period handling + legacy-placeholder semantics) is spec surface — routed to the B-51/B-52 fork legs or its own future fork. Buildable against cleared contracts; global re-sequencing at sign time stays out of scope. |
| **(i) cross-process chain-position atomicity** | **Impl-discretion engineering, deferred with (g)** | Two processes signing against one durable tail need an atomic read-compose-append. Achievable on POSIX — but NOT as a plain outer-lock widening (codex round-6): POSIX `flock` is non-reentrant across separately-opened descriptors, so an outer hold self-deadlocks when the inner `read_full_entries_for_tenant`/`append` reacquire the sidecar lock. The shape is unlocked inner variants callable under an outer transaction, or a lock-ownership API on the writer (`_flock` is a win32 no-op per B-45, so Windows closure rides B-45) — OR falls out of any future single-writer substrate. Bounded residual documented in-code since PR B1 round 13; not operator-gated. |
| **(f) tenant-scope binding under deployment-scoped keys** | **GENUINE design fork — spec delta required** (design_substrate_gated) | The §21.2.1 canonical message binds entry-hash/key_id/algo/period but not tenant. Candidates: (1) bind tenant into `AuditPayload` attrs (no message-format change; weakest), (2) fifth canonical-message segment (OD spec delta; strongest, byte-compat-scoped like the B-22→B-31 precedents), (3) REQUIRE tenant-scoped key_ids at MTC (config-validation-only; no crypto change). **Recommendation (revised at codex round-3): (2) — the fifth canonical-message segment — is the PRIMARY fix at the next OD delta.** Option (3) is NOT enforceable as config validation today: `key_arns` maps logical key_ids to ARNs with no tenant association, and the composers use fixed global logical ids (`stage_4_od.py` supplies them) — a presence check would accept one shared key for every tenant, a false guarantee. Tenant-aware key SELECTION would need per-tenant key_id derivation threaded through every composer (a mechanism change comparable to the message-segment change, with worse key-management ergonomics). Interim MTC posture: operator guidance (distinct per-tenant key_ids in `key_arns`), not a validation claim. Council-eligible (C7 compliance vs C2 schema-minimalism) — convene at the spec-delta leg, not here. |
| **(j) migration-CLI promotion** | **Spec-inventory fork** (design_substrate_gated, LOW urgency) | `python -m harness_runtime.admin.migrate_audit_sidecar` works today; promoting it into `[project.scripts]` extends the runtime spec §13.4 committed CLI inventory. Fold into the next runtime-spec delta as a one-row addition; nothing blocks on it. |
| **(m) fail-open vs fail-closed for signing failures** | **GENUINE design fork — spec delta with a spec-internal precedent** | OD v1.8 §C-OD-28.2 already commits the pattern for the sibling failure class: "operator-configurable; **default fail-closed = raise**" (rate-table resolution). **Recommendation: mirror it** — an `audit_signing_fail_closed` RuntimeConfig flag, default ON at MULTI_TENANT_COMPLIANCE (per-persona default per the §10.2 persona-tier discipline), OFF elsewhere; consulted at ALL TEN surfacing sites — the six fn-internal handlers and the four offload-boundary saturation handlers (codex round-6) — or centralized ahead of every catch. The delta is TWO-SPEC (codex round-4): §28.10.4 invariant 2 is CP-OWNED (`Spec_Control_Plane_v1_24.md` ~line 135), so fail-closing the validator hook needs a CP amendment carving out the audit-signing failure class, alongside the OD addendum; the weaker single-spec alternative preserves fail-open at that one hook while fail-closing the other five sites. Council-eligible (C7 compliance vs C1/C9 reliability). |

## 2. What this leg changes now vs. routes forward

**Now (this PR):** this doc + register corrections (item (g) premise fixed; items re-labeled per the
table; (h) opened as the next buildable impl item).

**Next impl iterations (Claude-buildable, no gate):** (h) per-family verifier unit; (g) disk-backed
index; (i) lock-scope widening in the token map. Plus B-48 (its own registered fork-revision arc) and
B-33 (Class 1 fork leg).

**Design-phase legs (fork docs → operator ratification per §4.3):** (f) and (m) — each gets a Class 2
fork doc with the recommendation above when its leg opens; (j) rides the next runtime-spec delta.

*No design-substrate file is edited by this leg; the two spec-delta forks are registered, not absorbed
(X-AL-3).*
