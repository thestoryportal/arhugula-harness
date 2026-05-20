# Class 1 Tension — U-CP-11 `LEASE_NAMESPACE_SCHEMA` spec-vs-plan divergence

| Field | Value |
|---|---|
| Unit | U-CP-11 — Declare `lease.*` namespace + 5-attribute schema |
| Sub-phase | 7b — CP axis-stream |
| Fork class | Class 1 (halt-execution — spec/plan contradiction) |
| Filed | 2026-05-16 |
| Actor | phase-7-implementation |
| Disposition | **RESOLVED 2026-05-16 (conform-to-spec, reading 1)** — see Resolution update below |

## Defect

U-CP-11 `Implements: [C-CP-05 §5.3]`. The plan's acceptance criterion #1
(CP plan v2.1 §2.2 U-CP-11, the canonical-current body — preserved verbatim
through v2.6) asserts:

> `LEASE_NAMESPACE_SCHEMA` declares exactly five attributes per C-CP-05 §5.3
> **verbatim**: `lease.id`, `lease.holder`, `lease.acquired_at`,
> `lease.duration_ms`, `lease.event_kind`.

The cited spec section, **Spec_Control_Plane_v1_2.md §5.3** (`lease.*` span
attribute namespace; preserved verbatim into v1.3), declares a *different*
5-tuple:

| Spec §5.3 attribute | Type |
|---|---|
| `lease.key` | string |
| `lease.holder` | string |
| `lease.ttl_ms` | int |
| `lease.mechanism` | enum string ∈ `{engine_native, redis_lease, db_unique_constraint, worktree_isolation, etcd_cas, per_segment}` |
| `lease.release_cause` | enum string ∈ `{normal, ttl_expiry, holder_loss, lease_revoked}` |

Only **one** of the five attributes — `lease.holder` — agrees between the
plan acceptance criterion and the cited spec section. The other four are
mutually contradictory:

| Plan acc #1 | Spec §5.3 |
|---|---|
| `lease.id` | `lease.key` |
| `lease.acquired_at` | `lease.ttl_ms` |
| `lease.duration_ms` | `lease.mechanism` |
| `lease.event_kind` | `lease.release_cause` |

The plan additionally declares a `LeaseEventKind` enum `{LEASE_ACQUIRED,
LEASE_RENEWED, LEASE_RELEASED, LEASE_LOST}` as the discriminator for a
`lease.event_kind` attribute that does **not exist** in spec §5.3. The plan's
acc #1 also claims this 5-tuple is "per C-CP-05 §5.3 **verbatim**" — a
verbatim-claim that is contradicted by the cited section (the Pattern-P2
verbatim-claim-contradicted defect class).

This divergence was forward-flagged at **CP plan v2.4 §0.8** as a carried
spec-silence / divergence item — `U-CP-11 (`LEASE_NAMESPACE_SCHEMA`)` — and
carried unresolved through v2.5/v2.6 (v2.5 §0.7: "All v2.4 §0.8
forward-flagged concerns carry unchanged … U-CP-11 … input-set divergence").
It was never resolved before Phase 7 execution.

## Why this is a halt, not a discretion call

Per the phase-7-implementation discipline and the task hard-rules: a unit is
halted when "a cited spec section genuinely under-specifies a signature you
cannot materialize, or an acceptance criterion is contradictory." Here the
acceptance criterion #1 *names a 5-tuple that the cited contract contradicts*.
This is not implementer's discretion (the U-CP-01 `cardinality` Q-R4-2
pattern) — that pattern covers a *plan-added field absent from the spec*,
not a *plan field-set that conflicts with the spec field-set*. There is no
authority-chain-determinate reading: the plan says one thing, the contract it
cites says another, and the spec is canonical for signatures/invariants
(authority chain — spec v1.x is contract authority over plan v2.x).

Materializing either 5-tuple would silently absorb a design-phase defect —
the worst failure mode per workspace `CLAUDE.md` §4.3.

## Routing

Class 1 → design-phase revision. Two candidate loci (operator decides):

1. **CP plan revision (Phase 6 plan revision-pass)** — if spec §5.3 is
   canonical, U-CP-11 acc #1 + Signatures + the `LeaseEventKind` enum + tests
   must be conformed to the spec §5.3 5-tuple (`lease.key` / `lease.holder` /
   `lease.ttl_ms` / `lease.mechanism` / `lease.release_cause`). This is the
   §4A verbatim-divergence-cluster conformance pattern already applied to
   U-CP-01/10/19/22/43/46/47 at v2.4 — U-CP-11 was the "borderline" item
   noted at `.harness/verbatim_audit_cp_plan.md` line 108 and should have
   been in that cluster.
2. **CP spec revision (Phase 5 spec revision-pass)** — only if the plan's
   `lease.id`/`acquired_at`/`duration_ms`/`event_kind` 5-tuple is the
   intended contract and spec §5.3 is the defect.

Reading (1) is strongly indicated: spec §5.3 is internally coherent (the
`lease.mechanism` 6-value enum and `lease.release_cause` 4-value enum are
cross-referenced at C-CP-09 §9.1 and the §5.2 `lease.released` minimum
attribute set), the plan acc #1 carries a contradicted "verbatim" claim, and
U-CP-11 sits in the same verbatim-divergence cluster that v2.4 conformed for
its siblings.

## Impact

U-CP-11 is L0 (`Depends on: (none)` + the v2.6 `[U-CP-00b]` carrier edge).
Downstream consumers of `LEASE_NAMESPACE_SCHEMA`:

- **U-CP-12** — per-class attribute composition for `lease.acquired` /
  `lease.released` events (acceptance #1). U-CP-12 is L3, not in the current
  9-unit L0 batch — no in-batch block.

No unit in the current L0 batch depends on U-CP-11. SKIPPED; the remaining
batch units proceed unaffected.

## Resolution update — 2026-05-16 (CP plan v2.8 — conform-to-spec, reading 1)

Reading (1) applied per the §4A conform-to-spec precedent (operator-ratified,
produced CP plan v2.4/v2.5). Spec §5.3 is canonical; the plan's contradicted
"verbatim" claim and invented 5-tuple are the defect.
`Implementation_Plan_Control_Plane_v2_8.md` §2.2 conforms U-CP-11:

- `LEASE_NAMESPACE_SCHEMA` 5-tuple conformed to C-CP-05 §5.3 verbatim:
  `lease.key`, `lease.holder`, `lease.ttl_ms`, `lease.mechanism`,
  `lease.release_cause`. The invented `lease.id` / `lease.acquired_at` /
  `lease.duration_ms` / `lease.event_kind` are struck.
- The invented `LeaseEventKind` enum is **struck** — it discriminated a
  `lease.event_kind` attribute that does not exist in §5.3.
- `LeaseMechanism` (6 values) + `LeaseReleaseCause` (4 values) enums added,
  byte-exact factor-outs of the §5.3 `lease.mechanism` / `lease.release_cause`
  enum-string domains; declared at U-CP-11 (lease-specific, not shared).

No design extension; no spec edit (the plan conforms to the spec, the spec is
unchanged). U-CP-11 is now landable against v2.8. Fork-queue item 5 → Resolved.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled RESOLVED 2026-05-16 (CP plan v2.8 §2.2 — LEASE_NAMESPACE_SCHEMA conformed to spec §5.3). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
