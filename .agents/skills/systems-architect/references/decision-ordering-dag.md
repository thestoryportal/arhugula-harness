# Decision Ordering — F / D / I Taxonomy

Architectural decisions sort into three classes by their dependency relationship to other decisions. This taxonomy governs:

- **Phase ordering** — F-decisions are made in Phase 3a; D-decisions in Phase 3b; I-decisions inline with whichever phase they surface in.
- **ADD section ordering** — Phase 3d ADDs order sections F → D → I.
- **Persona-document classification** — Phase 2 pre-classifies which decisions the persona answers, constrains, or leaves open.

---

## 1. Class definitions

### 1.1 Foundational (F)

**Definition:** A decision is foundational if its outcome constrains the option space of two or more other decisions, and is itself constrained only by project framing or persona — not by other architectural decisions.

**Properties:**

- Made first.
- Constrains downstream.
- Cannot be deferred without blocking downstream design.
- Number is small (typically 3–7 F-decisions per project).

**Examples (project-illustrative; not commitments):**

- Provider abstraction shape (constrains every LLM-touching component).
- Durable-execution coordination spine (constrains control plane, recovery, audit).
- Filesystem-as-shared-substrate adoption depth (constrains state, Skills, artifact handling).
- Sandbox isolation policy (constrains action surface, trust boundary).
- Secrets abstraction (constrains every credential-touching component).

### 1.2 Derivative (D)

**Definition:** A decision is derivative if its option space is constrained by one or more F-decisions, and its outcome constrains only I-decisions or no other decisions.

**Properties:**

- Made after the F-decisions it depends on.
- Option space is smaller because F-decisions have eliminated alternatives.
- Cannot be made before the F-decisions that constrain it (or it must be made and then revisited).

**Examples:**

- Specific durable-execution substrate (Temporal vs. Restate vs. DBOS — depends on F-deployment-surface and F-provider-abstraction).
- Specific sandbox provider (depends on F-sandbox-isolation-policy and F-deployment-surface).
- Specific observability backend (depends on F-deployment-surface).
- Specific HITL trigger catalog and approval-queue shape (depends on F-control-plane and F-trust-boundary).
- Specific eval set (depends on F-workload-class).

### 1.3 Independent / deferrable (I)

**Definition:** A decision is independent if it constrains nothing else and is constrained only by D-decisions or directly by persona; or if it can be added later without rework even if its option space changes.

**Properties:**

- Can be deferred to implementation phase or post-launch.
- Option choice is reversible at low cost.
- Often surfaces during implementation, not design.

**Examples:**

- Specific log-shipping target.
- Specific cost-tracking dashboard.
- Specific dev-tooling integrations.
- Specific style guide for prompt authoring.

---

## 2. The classification reasoning pattern

A decision's class is determined by its dependency structure, not by its perceived importance.

### 2.1 Procedure

For a candidate decision D:

1. **What constrains D?** List the constraints. Sources:
   - Project framing / workspace CLAUDE.md
   - Persona document
   - Other ADRs (cite by ID)
   - Substrate research (cite by deliverable + section)

2. **What does D constrain?** List the decisions that cannot be made until D is made.

3. **Apply the classification rule:**

| Constrained by | Constrains | Class |
|---|---|---|
| Project framing or persona only | ≥2 other decisions | **F** |
| ≥1 F-decision | only I-decisions or nothing | **D** |
| any | nothing | **I** |

### 2.2 Common misclassifications

| Misclassification | Symptom | Correction |
|---|---|---|
| **F-inflation** | Tagging a decision F because "it feels foundational" | Apply the rule: does it constrain ≥2 other decisions? If not, it is D or I. |
| **D-as-F** | Tagging a substrate-specific choice F (e.g., "Temporal is foundational") | Substrate-specific choices are D; the F-decision is the *commitment to durable execution as coordination spine*. The substrate is derivative. |
| **F-as-D** | Tagging a constraint-of-everything decision D ("provider abstraction is just a derivative of the provider list") | Provider abstraction *shape* (thin-client vs. portable-API vs. router) constrains every LLM-touching component; it is F. |
| **I-as-D** | Tagging a deferrable decision D and forcing it into Phase 3b | If the decision can be made later without rework, it is I; deferring it is correct. |
| **Hidden F** | A D-decision turns out to constrain ≥2 other decisions | The decision is F, not D; reclassify and revisit phase ordering. This is a workflow event (back-flow per workflow §4.2). |

---

## 3. Decision-ordering DAG (illustrative)

```
                    [Project framing / V3]
                            │
                            ▼
                       [Persona]
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
            [F1]          [F2]          [F3]   ← Foundational
              │             │             │
              └──────┬──────┴──────┬──────┘
                     ▼             ▼
                   [D1]          [D2]          ← Derivative
                     │             │
                     └──────┬──────┘
                            ▼
                          [I1]                  ← Independent
```

**Properties of the DAG:**

- Acyclic. If a cycle appears (D1 constrains F1), one of the two is misclassified.
- Persona has a path to every F-decision (every F is at least persona-constrained, even if persona only contributes hard constraints).
- I-decisions are leaves.

---

## 4. F/D/I and the persona document

Phase 2's pre-classification list categorizes decisions by what the persona resolves:

- **Persona-answered:** the persona directly determines the decision's outcome (e.g., persona is solo-developer-on-laptop → deployment surface is local-dev-design-time).
- **Persona-constrained-not-answered:** the persona narrows the option space but does not pick (e.g., persona requires multi-LLM but does not pick which providers).
- **Persona-leaves-open:** the persona has no bearing; the decision is shaped purely by other forces (substrate research, prior ADRs, integration verification).

This classification is **orthogonal** to F/D/I. A persona-answered decision can be F, D, or I; what matters is the dependency relationship to other decisions, not who answers it.

| Persona relation × F/D/I | Implication |
|---|---|
| Persona-answered F | Most constrained; document persona-derivation explicitly in the F-ADR's Context. |
| Persona-constrained F | Council deliberation operates within persona's narrowed option space. |
| Persona-open F | Council deliberation operates over the full option space; persona is not a load-bearing input. |
| Persona-answered D | The persona has resolved a substrate-level concern; rare but worth flagging. |
| Persona-constrained D | Common; persona narrows downstream alongside the F-constraints. |
| Persona-open D | Common; substrate and F-decisions are the load-bearing inputs. |

---

## 5. Use of the taxonomy in each phase

| Phase | Taxonomy use |
|---|---|
| **Phase 2 — persona surfacing** | Pre-classify decisions on three dimensions: F/D/I; persona-relation; axis. Persona document captures the F-decisions and their persona-relation. |
| **Phase 3a** | F-decisions are authored, one per session, with full council convening per workflow §2.3.1. |
| **Phase 3b** | D-decisions are authored, with full council or per-axis voice per workflow §5.1 DP-1. |
| **Phase 3c** | F-ADRs and D-ADRs are checked for cross-axis consistency. Misclassifications surface here as back-flow events. |
| **Phase 3d** | ADD section ordering follows F → D → I. Within each tier, sections are ordered by axis (control plane → information substrate → action surface → operational discipline → deployment surface). |
| **Phase 4 — PRD** | F-decisions establish the PRD's architectural givens; D-decisions establish the PRD's substrate choices; I-decisions are typically out of PRD scope. |
