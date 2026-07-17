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
- Every `sqlite` reference in the OD spec is the **Tier-3 trace ring-buffer** (solo-developer cells:
  lines 130/139/192/539/590/621/922) — a different tier for a different data class.

**Consequence.** The hash-chained IS state ledger (C-IS-05/06/07, JSONL) + the B2a full-entry sidecar
already inhabit the committed Tier-5 class. "JSONL vs SQLite" is NOT a spec-forced fork; it is an
implementation-substrate choice inside §21.2's committed properties. The register text is corrected in
the same PR as this doc.

## 1. Dispositions

| Item | Disposition | Rationale |
|---|---|---|
| **(e) signed-entry persistence** | **LANDED** (PR B1/B2a) | Sidecar-first durable full-entry store; 49+18 codex rounds + 2 merge-gates of hardening. |
| **(g) disk-backed membership index** | **Impl-discretion engineering** — registered as a BUILD item, no spec surface | Membership must prove absence ⇒ needs complete knowledge; the in-memory index rebuilds by full fold today (correct, O(history) at restart). A disk-backed index (e.g. the stdlib `sqlite3` module — available on the Python 3.12 baseline, unlike `dbm.sqlite3` which is 3.13+ — or an offset-checkpointed index snapshot beside the sidecar) is a pure performance optimization within Tier-5's committed properties. No fork needed. |
| **(h) per-family chain verifier** | **Impl-discretion BUILD item** (the natural next impl arc) | CXA §0.3 (v2.10, last substantive definition) action-id prefixes discriminate families; the B2a reader already documents the non-single-chain contract. A `verify_per_family_chains(entries)` unit partitioning by `payload.entry_core` prefix + running `verify_hash_chain_integrity` per family is buildable against cleared contracts. Global re-sequencing at sign time WOULD touch converter prior-hash semantics — correctly out of scope; the verifier does not need it. |
| **(i) cross-process chain-position atomicity** | **Impl-discretion engineering, deferred with (g)** | Two processes signing against one durable tail need an atomic read-compose-append. Achievable within the existing substrate via the B-40 cross-process lock held across tail-read+compose+append in the token map (a lock-scope widening, no new primitive) — OR falls out of any future single-writer substrate. Bounded residual documented in-code since PR B1 round 13; not operator-gated. |
| **(f) tenant-scope binding under deployment-scoped keys** | **GENUINE design fork — spec delta required** (design_substrate_gated) | The §21.2.1 canonical message binds entry-hash/key_id/algo/period but not tenant. Candidates: (1) bind tenant into `AuditPayload` attrs (no message-format change; weakest), (2) fifth canonical-message segment (OD spec delta; strongest, byte-compat-scoped like the B-22→B-31 precedents), (3) REQUIRE tenant-scoped key_ids at MTC (config-validation-only; no crypto change). **Recommendation: (3) now + (2) at the next OD delta** — (3) is enforceable today at `validate_audit_signing_for_span_stage` with zero message-format risk; (2) closes the hole for deployments that legitimately want one key. Council-eligible (C7 compliance vs C2 schema-minimalism) — convene at the spec-delta leg, not here. |
| **(j) migration-CLI promotion** | **Spec-inventory fork** (design_substrate_gated, LOW urgency) | `python -m harness_runtime.admin.migrate_audit_sidecar` works today; promoting it into `[project.scripts]` extends the runtime spec §13.4 committed CLI inventory. Fold into the next runtime-spec delta as a one-row addition; nothing blocks on it. |
| **(m) fail-open vs fail-closed for signing failures** | **GENUINE design fork — spec delta with a spec-internal precedent** | OD v1.8 §C-OD-28.2 already commits the pattern for the sibling failure class: "operator-configurable; **default fail-closed = raise**" (rate-table resolution). **Recommendation: mirror it** — an `audit_signing_fail_closed` RuntimeConfig flag, default ON at MULTI_TENANT_COMPLIANCE (per-persona default per the §10.2 persona-tier discipline), OFF elsewhere; the six loud-surface sites consult it. Requires an OD delta (a §21.2.1 addendum or §21.2.2) because §28.10.4 invariant 2's "MUST be swallowed" needs a carve-out for the validator hook path. Council-eligible (C7 compliance vs C1/C9 reliability). |

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
