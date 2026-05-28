# Class 1 Tension — U-CP-08 (`FallThroughCause` spec-silence / X-AL-3)

**Status:** ✅ CLOSED-via-CP-plan-v2.8-§2.1 (resolved 2026-05-16; verified workspace-wide audit 2026-05-20; status-line refreshed 2026-05-27) — `FallThroughCause` enum conformed to C-CP-03 §3.5 4-value set. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

| Field | Value |
|---|---|
| Unit | U-CP-08 — Implement deterministic fall-through procedure |
| Sub-phase | 7b — CP axis-stream |
| Fork class | Class 1 (halt-execution — silent H_T design extension) |
| Filed | 2026-05-16 |
| Actor | phase-7-implementation |
| Disposition | **RESOLVED 2026-05-16 (conform-to-spec)** — see Resolution update below |

## Defect

U-CP-08 (CP plan v2.1 §2.1, canonical-current body — preserved verbatim through
v2.5/v2.6, no body rewrite) is built around an **invented enum the cited spec
does not commit**.

The plan U-CP-08 Signatures block declares:

```
enum FallThroughCause {
  LAYER_NO_DECISION,
  LAYER_BUDGET_EXHAUSTED,
  PROVIDER_UNAVAILABLE,
  CAPABILITY_SHORTFALL
}
```

and U-CP-08 acceptance #1 asserts: *"`FallThroughCause` declares exactly four
values per C-CP-03 §3.2 verbatim."*

**The cited spec section commits no such enum.** `Spec_Control_Plane_v1_2.md`
C-CP-03 §3.2 (preserved verbatim into v1.3) declares a **procedure**, not an
enum:

```
on_layer_exceed_budget(layer, call_site_context, elapsed_ms):
  1. Emit fallback.triggered span event:
       attrs: fallback.from_layer = layer
              fallback.cause = "time_budget_exceeded"
              ...
  2. Advance to the next layer per C-CP-02 §2.1 layer ordering.
  3. If all layers exhausted -> emit fallback.exhausted span event; ...
```

§3.2 names a single string-literal cause `"time_budget_exceeded"`. §3.3
(`on_capability_shortfall`) names a second string-literal cause
`"capability_shortfall"`. Nowhere does C-CP-03 §3.2/§3.3 commit a discriminated
**4-value `FallThroughCause` taxonomy** — there is no `LAYER_NO_DECISION`, no
`PROVIDER_UNAVAILABLE`. The acceptance criterion's claim of a "verbatim"
4-value §3.2 enum is false; the chain is genuinely silent on a fall-through
cause taxonomy.

The remainder of U-CP-08's surface — `FallThroughResult` and the `fall_through`
procedure — is **typed entirely on `FallThroughCause`** (`FallThroughResult.cause
: FallThroughCause`; `fall_through(current_layer, cause: FallThroughCause, ...)`).
The invented enum is not a peripheral field; it is the unit's central
discriminator. The unit cannot be landed without materializing the
unspecified taxonomy.

## Authority basis for HALT

This is the exact shape carried — not resolved — at CP plan v2.4 §0.8 and
recorded in `.harness/pipeline-fork-queue.md` item 3:

> | 3 | **U-CP-08** — `FallThroughCause` design gap (silent H_T design
> extension if invented at the unit) | **Class 1** | back-flow: CP spec/ADR —
> needs the cause taxonomy committed upstream |

CP plan v2.4 §0.8 (the carried-finding ledger):

> **U-CP-08 `FallThroughCause` enum** — spec §3.2 (`on_layer_exceed_budget`)
> declares **no enum**; it is a procedure. The plan invents a 4-value
> `FallThroughCause` enum. There is nothing to "conform to" — the chain is
> genuinely silent. ... a plan unit declaring an H_T structure the spec does
> not commit is a design extension (`CLAUDE.md` I-2 / X-AL-3) that Phase 7 may
> not silently absorb.

Workspace `CLAUDE.md` I-2 / X-AL-3 (Meta-Architecture §7.7): **no silent H_T
design extension at Phase 7 execution.** New H_T primitives surfaced at
execution-time route to design-phase back-flow (Class 1) before implementation
proceeds. Landing U-CP-08 as written would silently absorb a design extension
into the codebase against a spec that does not commit it — the worst failure
mode per `CLAUDE.md` §4.3.

Note on the materializability axis: `.harness/materializability_audit_cp_plan.md`
verdicts U-CP-08 CLEARED — but that audit is explicit (§"Findings considered and
rejected" item 6) that this is a *different axis*: "`FallThroughCause` IS
declared by U-CP-08 itself; a coding agent can build it ... The two axes give
different verdicts on the same unit; this audit reports only the
materializability axis." The X-AL-3 / design-extension axis governs the
land/halt decision, and on that axis U-CP-08 is a Class 1 fork.

## Resolution

**HALT U-CP-08. Not landed. Skipped — continue the axis stream.**

No partial-land split is available: unlike U-CP-07 (where the schema half was
cleanly separable from the runtime-emission AC), U-CP-08 has no materializable
residue once the invented enum is removed — `FallThroughResult` and
`fall_through` are both typed on `FallThroughCause`, and the spec commits no
substitute taxonomy. The whole unit is blocked on the upstream design gap.

## Recommended back-flow

Design-phase channel — CP spec / ADR-F1:

1. **Option A (spec extension).** `spec-writer` extends `Spec_Control_Plane`
   C-CP-03 §3.2 to commit an explicit fall-through-cause taxonomy. The §3.2 +
   §3.3 procedures already imply at least two causes (`time_budget_exceeded`,
   `capability_shortfall`); the operator/architect must decide whether
   `LAYER_NO_DECISION` and `PROVIDER_UNAVAILABLE` are genuine additional causes
   or whether the §3.2 string-literal `fallback.cause` domain is the canonical
   shape (in which case U-CP-08's enum should be conformed to it, not invented
   anew).
2. **Option B (sanctioned plan extension).** The operator sanctions the plan's
   4-value `FallThroughCause` as an intentional plan-level structure with
   recorded rationale, per the v2.4 §4A.4 item-1 disposition path (b).

Until the operator decides, U-CP-08 stays unlanded. Downstream consumers:
U-CP-09 (`Depends on: [U-CP-08]`) is itself fork-blocked on Pattern D
(`AgentRole`) independently; U-CP-05 (`Depends on` includes U-CP-08) is not in
the Level-1 landing set. No landed unit regresses from this skip.

## Resolution update — 2026-05-16 (CP plan v2.8 — conform-to-spec)

**The original HALT under-read the cited contract.** This record (and the v2.4
§0.8 carried-finding) read C-CP-03 §3.2/§3.3 only — those sections are procedures
naming string-literal causes. But the **same contract's §3.5** (the `fallback.*`
namespace declaration) enumerates the cause taxonomy verbatim, line 401:

> `fallback.cause` ∈ `{time_budget_exceeded, capability_shortfall, breaker_open,
> rate_limit_storm}`

This is a closed 4-value enumeration. There **is** a spec enumeration to conform
to — the chain is not silent. `Implementation_Plan_Control_Plane_v2_8.md` §2.1
conforms U-CP-08: `Implements` corrected `§3.2` → `§3.5, §3.2, §3.3`; the invented
`{LAYER_NO_DECISION, LAYER_BUDGET_EXHAUSTED, PROVIDER_UNAVAILABLE,
CAPABILITY_SHORTFALL}` enum is struck and replaced with the §3.5 4-value set
`{TIME_BUDGET_EXCEEDED, CAPABILITY_SHORTFALL, BREAKER_OPEN, RATE_LIMIT_STORM}`.
The "layer produced no decision" case is no longer an enum member — it is
`cause = None` at the `fall_through` signature (a silent advance per §3.2 step 2,
no `fallback.triggered` event). This is the §4A conform-to-spec resolution
(operator-ratified, produced CP plan v2.4/v2.5) applied — no design extension, no
Class 1. U-CP-08 is now landable against v2.8. Fork-queue item 3 → Resolved.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled RESOLVED 2026-05-16 (CP plan v2.8 §2.1 — FallThroughCause enum conformed to C-CP-03 §3.5 4-value set). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
