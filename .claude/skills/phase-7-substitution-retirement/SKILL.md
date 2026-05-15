---
name: phase-7-substitution-retirement
description: Execute substitution retirement events against the 49-row substitution mapping table at Phase_7_Meta_Architecture_v1.md §5 (IS=9 / AS=6 / CP=21 / OD=8 / CXA=5) under the X-AL-2 retirement criterion fidelity rule. Activates when the user retires an H_E substitution ("retire H_T-IS-1", "U-IS-01 landed — retire the path-class convention substitution", "substitution retirement for H_T-CP-1"), opens sub-phase 7d, references the self-hosting milestone gradient at Meta-Architecture §6, requests verification of retirement criterion conditions, or surfaces a cross-axis retirement dependency (e.g., H_T-CP-1 retirement enables H_T-AS-8 anthropic.* namespace emission per §6.3.1; F-CP-01 Stage 3b inversion per §6.3.2). Always use this skill whenever the user mentions retirement, retirement criterion, self-hosting milestone, substitution gradient, H_T-{AXIS}-N primitive retirement, the 6 substitution-mechanism categories (H_E-direct / MCP-server / convention / shell-out / manual / authoring-only), bounded-residual substitution carry-forward, or any reference to substitution retirement against the canonical mapping table. Triggers on words like "retire", "retired", "retirement", "self-hosting", "substitution complete", "milestone", "H_E surface no longer invoked", or "bounded residual".
---

# phase-7-substitution-retirement

Event-driven substitution retirement discipline. Drives verification + recording of H_E substitution retirement against the 49-row substitution mapping table at `Phase_7_Meta_Architecture_v1.md` §5 under X-AL-2 retirement criterion fidelity.

## 1. Activation surface

### 1.1 Active during

- Retirement events throughout sub-phases 7b, 7c, 7d (event-driven, not phase-bound)
- Per-primitive retirement criterion verification at unit landing
- Self-hosting milestone gradient traversal per Meta-Architecture §6
- Cross-axis retirement dependency activation per §6.3

### 1.2 NOT active during

| Sub-phase / event | Alternate skill |
|---|---|
| 7b unit consumption (no retirement triggered) | `phase-7-implementation` |
| 7c seam wiring (no substitution retirement at edge) | `phase-7-cross-axis-composition` |
| Fork detection | `phase-7-back-flow-routing` |

### 1.3 Trigger events

| Event | Routing |
|---|---|
| Atomic unit lands (e.g., U-IS-01 acceptance criteria all green) | Verify retirement criterion for substitutions citing that unit ID |
| Operator declares retirement (e.g., "retire H_T-CP-1") | Verify both retirement criterion conditions per §3 |
| Cross-axis dependency activates (e.g., H_T-CP-1 retired → H_T-AS-8 unblocked) | Update cross-axis retirement dependency graph per §4 |
| 7d sub-phase closure | Verify all substitutions retired OR bounded-residual carried per §5 |

## 2. The 49-row substitution mapping table

Per `Phase_7_Meta_Architecture_v1.md` §5 + workspace root `CLAUDE.md` §4.1:

### 2.1 Per-axis substitution count

| Axis | Substitution count | Source |
|---|---|---|
| IS | 9 | Meta-Architecture §5.2 |
| AS | 6 | Meta-Architecture §5.3 |
| CP | 21 | Meta-Architecture §5.4 — **largest axis** |
| OD | 8 | Meta-Architecture §5.5 |
| CXA | 5 | Meta-Architecture §5.6 |
| **Aggregate** | **49** | Meta-Architecture §5 |

### 2.2 Per-mechanism category distribution

| Mechanism | Count | Retirement characteristic |
|---|---|---|
| H_E-direct | 11 | Direct H_E surface used (e.g., Checkpointing, worktree primitives, Skills frontmatter) |
| MCP-server | 12 | Routed through MCP server boundary (canonical H_E ↔ H_T transition site per X-AL-1) |
| Convention | 9 | `CLAUDE.md` prose + sub-agent compliance; **most fragile retirement** (compliance verification at retirement) |
| Shell-out | 8 | `Bash(git *)`, `Bash(python -c ...)`, `Bash(cat <<EOF >>)`; retires when typed contract supersedes shell invocation |
| Manual | 5 | Operator-driven gates (review, approval); retires when automation lands |
| Authoring-only | 4 | Substitutions present only during artifact authoring; retire at authoring close (out of Phase 7 scope for retirement event handling) |

## 3. Retirement criterion fidelity (X-AL-2)

Per `Phase_7_Meta_Architecture_v1.md` §7.7:

> **X-AL-2.** **Retirement criterion fidelity.** Every substitution at §5 carries a retirement criterion. Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked at substitution site). Both conditions required.

### 3.1 Both-conditions discipline

| Condition | Verification |
|---|---|
| (A) Cited unit IDs landed | All unit IDs in the substitution entry's retirement criterion column are complete: acceptance criteria green; coverage matrix updated; cluster coherence pass passed |
| (B) H_E surface no longer invoked at substitution site | Code review at the substitution site confirms the H_E surface (e.g., `Bash(git *)`, `CLAUDE.md` convention, H_E Checkpointing) is no longer called for the substituted primitive |

**Partial retirement is non-retirement.** Both conditions are required. Recording retirement with only condition (A) satisfied violates X-AL-2 and surfaces as Class 1 fork via `phase-7-back-flow-routing`.

### 3.2 Verification shape

Per substitution retirement event:

| Step | Action |
|---|---|
| 1 | Locate substitution entry at Meta-Architecture §5.{2,3,4,5,6} |
| 2 | Identify retirement criterion column: cited unit IDs |
| 3 | Verify each cited unit landed (acceptance criteria green; coverage matrix verified) |
| 4 | Code-review substitution site: confirm H_E surface no longer invoked for substituted primitive |
| 5 | If (A) ∧ (B): record retirement at workspace progress ledger |
| 6 | If (A) ∧ ¬(B) OR ¬(A) ∧ (B): HALT; surface to operator (Class 1 via `phase-7-back-flow-routing`) |
| 7 | If retirement triggers cross-axis dependency (per §4), update dependent substitutions' eligibility |

## 4. Cross-axis retirement dependencies

Per `Phase_7_Meta_Architecture_v1.md` §6.3: **2 documented cross-axis retirement dependencies**.

### 4.1 H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission dependency (§6.3.1)

```
H_T-AS-8 substitution (5 of 7 namespaces emitted)
        │
        │ depends on
        ▼
H_T-CP-1 retired (U-CP-01 lands; multi-LLM routing core operational)
        │
        │ enables
        ▼
H_T-AS-8 substitution → full 7-namespace coverage (anthropic.* becomes harness-emittable)
```

Until H_T-CP-1 retires, `anthropic.*` namespace remains absent — H_E owns the Anthropic provider surface and does not expose its telemetry. After H_T-CP-1 retires, H_T provider-portability layer carries the Anthropic provider with harness-authored instrumentation.

### 4.2 F-CP-01 Stage 3b inversion ordering (§6.3.2)

```
H_T-OD-2 retired (U-OD-09 lands; harness.breaker.* canonical declaration)
        │
        │ + parallel
        ▼
H_T-CP-24 retired (U-CP-54 lands; CP-side ingestion of breaker namespace)
        │
        │ jointly enables
        ▼
H_T-CXA-5 inversion seam operational
```

Both endpoints land before the inversion seam activates. Neither blocks the other.

### 4.3 Cross-axis dependency tracking

At each retirement event, check whether the retired substitution unblocks a dependent substitution per §4.1 / §4.2. If so, update the dependent substitution's eligibility (criterion (A) progress) and surface the cascade to operator.

## 5. Self-hosting milestone gradient

Per `Phase_7_Meta_Architecture_v1.md` §6: per-primitive 49-row retirement gradient (live-criterion + substitution-retirement-criterion) + cluster aggregation as secondary view + 2 documented cross-axis retirement dependencies.

### 5.1 Phase 7 progress metric

Phase 7 progress is measured by **substitution-retirement count + cluster-completion ordering** per `Project_Workflow_v1_8.md` §2.7.5 — NOT by sub-phase elapsed time. The retirement gradient is the canonical progress dashboard.

### 5.2 Sub-phase 7d closure criterion

Per Workflow v1.8 §2.7.5:

> Sub-phase 7d closure requires all H_E substitutions retired OR each non-retired substitution explicitly carried as bounded-residual with documented rationale (no silent carry-forward).

### 5.3 Bounded-residual substitution carry-forward

When a substitution cannot retire at 7d closure (e.g., its cited unit IDs are out-of-scope for the current Phase 7 build):

| Required | Action |
|---|---|
| Documented rationale | Why retirement is not achievable; what milestone unblocks it; whether subsequent project iteration will address |
| Operator decision | Class 2 fork via `phase-7-back-flow-routing`; operator authorizes the bounded carry-forward |
| Bounded-residual log entry | Recorded at 7d close handoff with substitution ID + rationale + future milestone |

**Silent carry-forward is forbidden.** Every non-retired substitution at 7d closure requires explicit operator-authorized bounded-residual classification.

## 6. Anti-leakage discipline

### 6.1 Cross-cutting rule (Meta-Architecture §7.7)

| Rule | Statement |
|---|---|
| X-AL-1 | Substrate boundary discipline preserved through retirement. The H_E surface no longer invoked at substitution site means the boundary moves from "H_E owns this primitive" to "H_T owns this primitive at MCP server process boundary" (or pre-MCP-server in-process for non-MCP-bound contracts). The boundary itself is preserved |
| **X-AL-2** | **Retirement criterion fidelity (load-bearing at this skill — see §3)** |
| X-AL-3 | NO H_T design extension via retirement. If retirement reveals an under-specified H_T primitive, surface as Class 1 fork via `phase-7-back-flow-routing`; do NOT silently extend H_T design at retirement event |

### 6.2 Retirement is not architectural commitment

Per Meta-Architecture §7.1:

> Substitutions during 7a are *scaffolding*, NOT architectural commitments.

Retirement closes a scaffolding event. It does NOT modify H_T architectural commitments (those live at ADRs + ADD + specs + plans, all canonical at design-phase workspace). If retirement reveals a contradiction between scaffolding behavior and H_T contract, the H_T contract is canonical; the substitution was wrong; route via `phase-7-back-flow-routing` to surface the misalignment to operator.

### 6.3 Authoring-artifact substitutions

4 substitutions are classified "authoring-only" per Meta-Architecture §5 (e.g., H_T-IS-{authoring}, H_T-AS-9, H_T-CP-24, H_T-OD-8 categorized at §4.4 H_E classification with "Authoring artifact" rationale). These substitutions:

- DO NOT trigger retirement events at Phase 7 execution-time
- ARE retired at design-phase artifact close (already retired at Phase 6.5 entry)
- DO NOT carry forward to 7d closure verification

Skip authoring-artifact substitutions when checking 7d closure criterion (per §5.2).

## 7. Halt conditions

HALT retirement and surface to operator (via `phase-7-back-flow-routing`) when:

| Halt trigger | Class | Routing target |
|---|---|---|
| Condition (A) met but condition (B) not met (cited units landed; H_E surface still invoked) | 1 | Code review at substitution site; locate residual invocation; halt until removed |
| Condition (B) met but condition (A) not met (H_E surface removed; cited units not landed) | 1 | Halt; suspicious — substitution was previously providing value; investigate before recording retirement |
| Retirement criterion column at Meta-Architecture §5 is empty or under-specified for the substitution | 1 | Meta-architecture revision (design-phase back-flow) |
| Retirement reveals H_T primitive under-specification (substitution behavior NOT covered by H_T contract) | 1 | Spec or ADR revision via design-phase back-flow (X-AL-3 binds) |
| 7d closure check finds non-retired substitution without bounded-residual classification | 2 | Operator decision: complete retirement OR bounded-residual classification |
| Cross-axis retirement dependency cycle surfaced (none currently per §4) | 1 | Meta-architecture revision (Class 1) |

DO NOT silently record retirement against partial criterion satisfaction. DO NOT silently carry forward non-retired substitutions past 7d closure.

## 8. Retirement event recording

### 8.1 Workspace progress ledger

Per `phase-7-implementation` skill §3.7: workspace-internal artifact (not specified at design-phase). Per-event recording:

| Field | Content |
|---|---|
| Substitution ID | H_T-{AXIS}-N (e.g., H_T-IS-1) |
| Retirement event timestamp | Phase 7 session + segment + unit-landing event reference |
| Condition (A) verification | Cited unit IDs + acceptance-criteria-passed timestamps |
| Condition (B) verification | Substitution-site code-review reference; H_E surface confirmed not invoked |
| Cross-axis dependency cascade | If §4.1 or §4.2 triggered: dependent substitution ID + cascade state |

### 8.2 Canonical Substrate Inventory update

If retirement closes a substitution that was previously documented at `Canonical_Substrate_Inventory.md` (design-phase workspace), the inventory's substitution-status column updates at the next Phase 7 session-close handoff routing back to design-phase workspace.

## 9. Reference artifacts

| Reference | Location | Authority |
|---|---|---|
| `Phase_7_Meta_Architecture_v1.md` §5 | Design-phase workspace | 49-row substitution mapping table |
| `Phase_7_Meta_Architecture_v1.md` §6 | Design-phase workspace | Self-hosting milestone gradient + cross-axis retirement dependencies |
| `Phase_7_Meta_Architecture_v1.md` §7.7 | Design-phase workspace | X-AL-1 / X-AL-2 / X-AL-3 cross-cutting anti-leakage |
| `Project_Workflow_v1_8.md` §2.7.5 | Design-phase workspace | Self-hosting milestone gradient as Phase 7 progress metric |
| Workspace root `CLAUDE.md` §4 | This workspace | Substitution + back-flow discipline summary |
| Per-axis `CLAUDE.md` §4.1 | This workspace | Per-axis substitution surface summary |

---

*End of `phase-7-substitution-retirement` skill. Event-driven activation across sub-phases 7b–7d. Delegates to `phase-7-back-flow-routing` on halt conditions per §7.*
