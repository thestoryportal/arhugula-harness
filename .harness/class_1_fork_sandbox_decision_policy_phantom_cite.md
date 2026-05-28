# Class 1 Fork — `SandboxDecisionPolicy` phantom cite at AS spec v1.3 §15

**Filed:** 2026-05-22 at L9-septies cluster impl arc, pre-U-RT-71 landing.
**Status:** ✅ APPLIED 2026-05-22 at L9-septies cluster close `00da5ef` (status-line refreshed 2026-05-27) — operator ratified Q1=C-i (re-home to harness-core empty-marker); applied via runtime spec v1.15 → v1.16 + plan v2.12 → v2.13 + harness-core plan v1.1 → v1.2 + U-CORE-02 empty-marker `SandboxDecisionPolicy` Pydantic v2 BaseModel landing; ZERO cross-axis cascade per §5. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

_Original filing footer:_ **Status:** OPEN — awaiting operator routing decision.
**Scope:** Phase 7b atomic-unit consumption discipline; halt-execution Class 1
per `Project_Workflow_v1_8.md` §2.7.6 + workspace CLAUDE.md §4.3.
**Surfaced by:** `phase-7-implementation` skill at §3.4 dependency-verification
step during U-RT-71 (RuntimeConfig schema extension) consumption.
**Disposition:** L9-septies cluster fully HALTED at this arc (no code landed).
U-RT-71, U-RT-73, U-RT-75, U-RT-68 all gated on this fork. U-RT-72 + U-RT-74
are technically unblocked but landing them alone leaves the cluster in
3/6-landed with no operational chain — recommend HALT-all for cluster coherence.

---

## 1. The gap

`Spec_Harness_Runtime_v1.md` v1.15 §3 C-RT-02 RuntimeConfig field-table
states:

> **`sandbox_decision_policy`** — `SandboxDecisionPolicy | None` (AS spec
> v1.3 §15 carrier) — no (default `None` → uses `SandboxDecisionPolicy.default()`)
> — Operator-supplied sandbox-tier decision policy ingested at stage 5 by
> `materialize_runtime_tool_dispatcher_stage` factory per §14.9.3; consumed
> by `RuntimeToolDispatcher` for tier-floor evaluation per §14.9.1 step 5.
> Added at v1.15 per U-RT-68 fork Q2=B2 ratification.

And `Spec_Harness_Runtime_v1.md` v1.15 §14.9.3 stage-5 factory step 3 states:

> Construct bare `RuntimeToolDispatcher` with references to `ctx.mcp_client_host`
> + `ctx.per_server_trust_evaluator` + `ctx.mcp_namespace_emitter` +
> `config.sandbox_decision_policy` (defaults to `SandboxDecisionPolicy.default()`
> if `None`).

And `Implementation_Plan_Harness_Runtime_v2_12.md` U-RT-71 Signatures + U-RT-75
AC #4 carry the same cite verbatim:

> `SandboxDecisionPolicy` imported from AS package per AS spec v1.3 §15
> carrier home.

**`SandboxDecisionPolicy` does NOT exist at the canonical AS authority.**
Empirical verification (2026-05-22):

| Check | Result |
|---|---|
| `grep -rn "SandboxDecisionPolicy" design-substrate/*.md` | Only 3 hits: 2 in runtime spec v1.15, 1 in runtime plan v2.12. ZERO hits in AS spec v1.3 (`design-substrate/Spec_Action_Surface_v1.md`). |
| `grep -rn "SandboxDecisionPolicy" --include="*.py" harness-as/ harness-cp/ harness-runtime/ harness-core/` | ZERO hits across all axis packages. |
| AS spec v1.3 §15 inspection | §15 is not a numbered section in AS spec v1.3 (the spec is structured around C-AS-NN contracts; C-AS-15 is the §15 reference and treats `secret.fetch` span attribute schema, not sandbox decision policy). |
| AS spec v1.3 sandbox-related carriers | `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier \| REFUSE` is a **FUNCTION** (5-arg per §2.3 row→argument keying), not a `SandboxDecisionPolicy` class. `SandboxTier` enum exists. No "policy" class. |

The cite was authored during the U-RT-68 fork resolution arc at last session
(spec v1.14 → v1.15 commit `6a19755`, plan v2.11 → v2.12 commit `373f32a`).
The original Q2=B2 ratification at `.harness/class_1_fork_u_rt_68_retry_wrap_shape_gap.md`
§5 lists the bootstrap-wiring chain primitives and includes `sandbox_decision_policy`
as a config field — but does not commit on its home package. The cite to "AS spec
v1.3 §15" was synthesized at spec-writer authoring time without verification
against the AS spec body.

## 2. Why this is Class 1 (not Class 3 prose drift)

Per workspace CLAUDE.md memory `spec-prose-plan-body-drift-pattern`: when spec
prose drifts from plan body BUT the contract is unambiguous, land against plan
body + file Class 3.

**This is not that pattern** — both spec AND plan agree on the cite; the AS
spec (cited authority) is what disagrees, and the cited carrier doesn't exist
anywhere. There is no "land against plan body" path because the plan body's
import target is missing.

Per workspace CLAUDE.md §4.3 routing table: "Cited spec contract section
unreachable or under-specifies the surface — Class 1, routes to Phase 5 spec
revision." This matches exactly.

Per X-AL-3 (Meta-Architecture §7.7): "no silent H_T design extension at
Phase 7 execution-time. New H_T primitives surfaced at execution-time route to
design-phase back-flow before implementation proceeds." Authoring a new
`SandboxDecisionPolicy` class in-arc at AS or runtime without operator
ratification would be a silent design extension.

## 3. The three possible readings

### Reading A — extend AS spec (cascade)

**Action.** Author `SandboxDecisionPolicy` carrier into AS spec v1.3 → v1.4
at a new §15 (or attached to existing C-AS-15 `secret.fetch` neighbor — TBD).
Author new AS plan unit U-AS-NN for the package implementation. Re-issue AS
spec + AS plan + runtime spec §3 cite stays unchanged.

**Cascade scope.** AS spec v1.3 → v1.4 revision; new AS plan unit; cross-axis
edge enumeration check (CXA v2.8 §2.3.2 CP→IS / §2.3.4 CP→AS — none currently
typed against SandboxDecisionPolicy). AS package implementation (~50-200 LOC
depending on policy surface).

**Cost.** 1 spec-writer arc + 1 implementation-planner arc + 1 AS implementation
unit. Pushes L9-septies opening by 1 cluster.

**Pro.** Preserves cite intent. AS-axis owns sandbox decisions canonically per
ADR-D2 (sandbox tier composition); a policy carrier is the natural home.

**Con.** AS spec was P3-CK / P5-CK cleared at v1.3; reopening requires care.
No prior surface signaled the need for a runtime-injectable policy (sandbox
decisions are currently keyed by `sandbox_tier_floor()` function output at the
call site, not by a policy object). The semantic surface of `SandboxDecisionPolicy`
is unspecified at the canonical chain.

### Reading B — runtime spec downscope (strike the field)

**Action.** Runtime spec v1.15 → v1.16: strike `sandbox_decision_policy` from
C-RT-02 field-table (§3 row at line 641); strike the cite at §14.9.3 stage-5
step 3 (line 1931). Runtime plan v2.12 → v2.13: strike `sandbox_decision_policy`
from U-RT-71 Signatures + ACs; strike from U-RT-75 step 3 ACs. The bare
`RuntimeToolDispatcher` at U-RT-67 is constructed without policy ref; tier-floor
evaluation falls back to whatever default it currently encodes.

**Cascade scope.** Runtime spec v1.16 revision; runtime plan v2.13 revision.
ZERO AS cascade. ZERO CXA cascade.

**Cost.** 1 spec-writer arc + 1 implementation-planner arc. Same-session
unblock possible.

**Pro.** Minimum cascade. Recognizes that no operator has actually asked for
sandbox policy at runtime injection time; the field was added speculatively
during U-RT-68 absorption.

**Con.** Locks in a future Class 1 re-open if operator surfaces the need for
runtime-injectable sandbox policy later. The current `RuntimeToolDispatcher`
must encode SOME default sandbox decision; if it currently lacks one, this
reading exposes that as a separate gap.

### Reading C — runtime spec re-home (where it actually lives)

**Action.** Runtime spec v1.15 → v1.16: change the cite from "AS spec v1.3 §15
carrier" to one of three concrete homes:
  (i) `harness-core` package — minimal `SandboxDecisionPolicy` dataclass with
      `default() -> SandboxDecisionPolicy` factory and operator-defined fields
      (e.g. `tier_floor_overrides: Mapping[str, SandboxTier]`)
  (ii) `harness-as` package without AS spec amendment — runtime-spec-only home
      declaration (X-AL-3 violation candidate — needs operator ratification)
  (iii) `harness-runtime` package — fully runtime-internal carrier; AS spec
      stays untouched

**Cascade scope.** Runtime spec v1.16 revision; runtime plan v2.13 revision.
If (i) or (iii): new ~20-50 LOC carrier in the chosen package. If (ii):
silent AS extension → X-AL-3 violation, requires explicit operator
authorization and is not recommended.

**Cost.** 1 spec-writer arc + 1 implementation-planner arc + ~30 LOC. Same-
session unblock possible after operator picks (i) / (iii).

**Pro.** Preserves the runtime-injectable policy intent. Avoids AS-spec
reopen.

**Con.** Stretches the AS-axis canonical authority — sandbox decisions
"should" live at AS per ADR-D2 ownership, so re-homing them at core /
runtime is mild authority leakage. Operator should ratify.

## 4. Decision questions

**Q1.** Which reading?
  - **(A)** Extend AS spec v1.3 → v1.4 with `SandboxDecisionPolicy` at AS-axis canonical home (cascade route)
  - **(B)** Strike the field from runtime spec v1.15 → v1.16 (downscope route)
  - **(C)** Re-home to harness-core / harness-runtime via runtime spec v1.15 → v1.16 cite correction (minimum-cascade re-home route)

**Q2 (only if Q1=C).** Which home?
  - **(C-i)** `harness-core` package
  - **(C-iii)** `harness-runtime` package

**Q3.** Routing target acceptance — do you want the routing arc to open
immediately at this session?
  - **(yes)** Open routing arc now (spec-writer revision + plan revision).
  - **(no)** Park fork; do other work this session.

**Q4 (only if Q1=B).** Does striking `sandbox_decision_policy` leave a known
sandbox-tier-evaluation gap at `RuntimeToolDispatcher`?
  - **(no-gap)** `RuntimeToolDispatcher` already encodes sandbox decisions via
    `sandbox_tier_floor()` call at construction time; no field needed.
  - **(gap)** A separate Class 1 will be needed to specify how the dispatcher
    obtains its tier-floor inputs.

## 5. Other landings affected

| Unit | Status under each reading |
|---|---|
| U-RT-71 (RuntimeConfig +2 fields) | A: cite-only edit if AS spec v1.4 lands first. B: -1 field (only `trust_policy` lands). C: cite home changes. |
| U-RT-72 (HarnessContext +4 fields) | UNAFFECTED — depends on U-RT-74 + U-RT-63 + cross-axis, not on SandboxDecisionPolicy. |
| U-RT-73 (stage-3a factory) | UNAFFECTED — body does not consume SandboxDecisionPolicy. |
| U-RT-74 (RetryBreakerToolDispatcher) | UNAFFECTED — class body has no SandboxDecisionPolicy ref. |
| U-RT-75 (stage-5 factory) | A/C: cite-only edit. B: step 3 simplifies (no policy arg threaded to bare dispatcher). |
| U-RT-68 (stage-5 wire-up) | UNAFFECTED at AC level — depends on U-RT-75 factory output, not on the policy field directly. |

## 6. Recommendation — operator decides

Operator-only decision. The architect/spec-writer/implementation-planner skill
discipline does not authorize this skill (phase-7-implementation) to pick. My
read of the cost/scope:

- **Reading B (downscope)** is lowest cascade, but freezes out a possibly-real
  surface that operators may want later.
- **Reading C-i (harness-core re-home)** is the smallest spec edit that
  preserves the field — about the same cost as B but keeps the surface open
  for future operator-driven extension.
- **Reading A (extend AS spec)** is the highest-fidelity route but reopens an
  already-P5-CK-cleared spec for a surface no operator has explicitly asked
  for yet.

Default leaning if pressed: **Reading C-i (`harness-core` home)** — minimum
spec churn, preserves the field, no axis-spec reopen, no semantic commitment
to AS-internal sandbox policy at the runtime layer. Pairs with Q3=yes for
same-session unblock.

But: please pick. The L9-septies cluster cannot open without this.

## 7. Cluster state at filing

| Marker | Value |
|---|---|
| HEAD | `128ab4f` (cluster 4-OD-E partial close, U-OD-53 + U-OD-54 landed) |
| Branch | `worktree-remaining-work-closure-arc-phase-a` (41 commits since open) |
| Tree | clean |
| Tests | 2687/2687 green |
| L9-septies status | HALTED — 0/6 units landed (5 new + U-RT-68 rewrite) |
| L9-sexies status | preserved 7/8 landed (U-RT-68 awaiting L9-septies dep) |

## 8. Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-22 (same-day as U-RT-68 fork resolution arc; same-session at L9-septies dependency-verification step) |
| Filed by | `phase-7-implementation` skill §3.4 dep audit |
| Routing target | Operator → spec-writer (runtime spec v1.16 revision OR AS spec v1.4 revision per Q1) + implementation-planner (runtime plan v2.13 revision) |
| Halt scope | L9-septies cluster entirely (recommend HALT-all for cluster coherence even though U-RT-72 + U-RT-74 + U-RT-73 are technically unblocked) |
| Cross-axis cascade | ZERO (per §5 unit-impact table); CXA v2.8 unchanged regardless of reading |
| Next action | Await operator Q1+Q2+Q3 ratification |
