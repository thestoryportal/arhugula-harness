---
name: phase-7-cross-axis-composition
description: Execute Phase 7 sub-phase 7c cross-axis composition seam instantiation against the 101 typed cross-axis edges declared at CXA v2.1 §2.3 across 6 composition buckets (AS→IS / CP→IS / CP→AS / OD→IS / OD→AS / OD→CP). Activates when the user requests instantiation of a cross-axis seam ("wire the CP→IS ledger-emission edge", "instantiate the CXA composition seam", "implement the AS→IS edge for U-AS-19", "compose the 5 CXA composition seams"), opens sub-phase 7c, authorizes the sa-cxa sub-agent, or references cross-axis edges, the 6 composition buckets, Pattern P1 byte-exact alignment, terminal exporter manifests, or CXA seam instantiation. Always use this skill whenever the user mentions cross-axis wiring, CXA edges, edge cardinality, composition seams, terminal aggregate exporter consumption, cross-axis dependency resolution at integration time, or any reference to the 101-edge aggregate or per-bucket edge enumerations. Triggers on words like "wire", "instantiate", "compose", "integrate", "CXA", "seam", "cross-axis edge", or any reference to cross-axis composition during 7c.
---

# phase-7-cross-axis-composition

Phase 7 sub-phase 7c cross-axis composition seam instantiation discipline. Drives wiring of the 101 typed cross-axis edges declared at `Cross_Axis_Composition_Document_v2_1.md` §2.3 across 6 composition buckets, against Pattern P1 byte-exact alignment.

## 1. Activation surface

### 1.1 Active during

- Sub-phase 7c cross-axis composition execution
- `sa-cxa` sub-agent active per `Sub_Agent_Boundary_Specification_v1.md` §4.5
- Operator request for cross-axis seam instantiation
- Cross-axis edge wiring verification at composition close

### 1.2 NOT active during

| Sub-phase | Alternate skill |
|---|---|
| 7a (bootstrap) | None specific; consult Meta-Architecture §5 |
| 7b (per-axis-stream implementation) | `phase-7-implementation` |
| 7d (substitution retirement) | `phase-7-substitution-retirement` |
| Fork detection (any sub-phase) | `phase-7-back-flow-routing` |

### 1.3 Entry-gate prerequisites

`sa-cxa` activates ONLY after all 4 axis-stream sub-agents complete per `Sub_Agent_Boundary_Specification_v1.md` §3.1 activation window. Terminal exporter manifests must be operational:

| Manifest | Source | Verifies |
|---|---|---|
| U-IS-17 | IS plan v2.2 §2.6 | IS substrate seam exports (6 export seams) |
| U-AS-33 | AS plan v1 §2 | AS substrate seam exports |
| U-CP-54 / U-CP-55 | CP plan v2.3 §2.9 (Cluster 9) | CP substrate seam exports (terminal aggregate exporters; F2-12 cascade Step 6a closure record carrier at U-CP-55) |
| U-OD-34 | OD plan v2.4 §[exports] | OD substrate seam exports |

If any terminal exporter is not operational, HALT and route per `phase-7-back-flow-routing`.

## 2. CXA aggregate adjacency

Per `Cross_Axis_Composition_Document_v2_1.md` §2.1 aggregate 4×4 adjacency matrix:

```
                Target ↓
Source →    IS      AS      CP      OD
   IS    (self)    0       0       0
   AS     13     (self)    0       0
   CP     36      24     (self)    0
   OD      6      10      12     (self)
```

| Property | Value |
|---|---|
| Aggregate cross-axis edges | 101 |
| Non-empty buckets | 6 |
| Zero buckets | 6 (producer-side surfaces via terminal exporter manifests; consumer-side declares `Depends on`) |
| Axis-level topological order | IS → AS → CP → OD (acyclic per §2.2) |

## 3. The 6 composition buckets

### 3.1 AS → IS bucket (13 edges; 8 AS units → 8 IS carriers)

| Source | CXA §2.3.1 |
|---|---|
| AS-side authority | `Implementation_Plan_Action_Surface_v1.md` §3.4 |
| Producer-side manifest | U-AS-33 substrate seam exports |
| Consumer-side surface | U-IS-17 substrate seam exports manifest (read-only) |

Wired AS units: U-AS-19, U-AS-25, U-AS-26, U-AS-27, U-AS-28, U-AS-29, U-AS-30 (and 1 more per §3.4).

### 3.2 CP → IS bucket (36 edges)

| Source | CXA §2.3.2 |
|---|---|
| CP-side authority | `Implementation_Plan_Control_Plane_v1.md` §3.3 cluster-level edge profile (preserved at v2.3) |
| Producer-side manifest | U-CP-54 / U-CP-55 substrate seam exports |
| Consumer-side surface | U-IS-17 substrate seam exports manifest (read-only) |

Largest bucket. Per-cluster CP → IS edge distribution at CP plan §3.3 table (3 + 5 + 4 + 5 + 9 + 2 + 4 + 4 + 1 = 36 across 9 clusters).

### 3.3 OD → CP bucket (12 edges)

| Source | CXA §2.3.3 |
|---|---|
| OD-side authority | `Implementation_Plan_Operational_Discipline_v2_4.md` §4.5 |
| Producer-side manifest | U-CP-54 / U-CP-55 substrate seam exports |
| Consumer-side surface | OD plan §4.5 cross-axis consumer declarations |

Inversion seam: H_T-CXA-5 (F-CP-01 Stage 3b inversion) per Meta-Architecture §6.3.2 requires both endpoints (H_T-OD-2 + H_T-CP-24) retired before the inversion seam activates.

### 3.4 CP → AS bucket (24 edges)

| Source | CXA §2.3.4 |
|---|---|
| CP-side authority | `Implementation_Plan_Control_Plane_v1.md` §3.3 cluster-level edge profile |
| Producer-side manifest | U-AS-33 substrate seam exports |
| Consumer-side surface | CP plan cross-axis dependency declarations |

Per-cluster CP → AS edge distribution: 1 + 0 + 0 + 4 + 5 + 0 + 7 + 4 + 2 = 24 across 9 clusters.

### 3.5 OD → IS bucket (6 baseline / 4 at OD v2.4)

| Source | CXA §2.3.5 |
|---|---|
| OD-side authority (baseline) | OD plan v2.3 §4.5.1 (6-row enumeration) |
| OD-side authority (current) | `Implementation_Plan_Operational_Discipline_v2_4.md` §4.5.1 (4-row enumeration per C3-15 Path (i-refined) deletions) |
| Producer-side manifest | U-IS-17 substrate seam exports manifest |
| Consumer-side surface | OD plan §4.5.1 cross-axis consumer declarations |

**CXA-OD-IS-EDGE-DRIFT (Class 3 informational)** per IS plan v2.2 §0.9 + OD plan v2.4 §0.9: CXA v2.1 §2.3.5 enumerates 6 edges; OD plan v2.4 §4.5.1 enumerates 4. Cardinality drift surfaced; non-blocking; future composition-document revision pass.

**At seam instantiation:** wire against OD plan v2.4 §4.5.1 canonical (4 edges), NOT CXA v2.1 baseline (6 edges). Operator decision required if 6-edge wiring intended.

### 3.6 OD → AS bucket (10 edges)

| Source | CXA §2.3.6 |
|---|---|
| OD-side authority | `Implementation_Plan_Operational_Discipline_v2_4.md` §4.5 |
| Producer-side manifest | U-AS-33 substrate seam exports |
| Consumer-side surface | OD plan cross-axis consumer declarations |

## 4. Per-edge instantiation shape

For each cross-axis edge:

### 4.1 Step 1 — Locate edge declaration

| Step | Action |
|---|---|
| 1.a | Identify the bucket per §3 (one of 6) |
| 1.b | Read CXA v2.1 §2.3.X for the bucket's edge enumeration |
| 1.c | Identify consumer-side unit (e.g., U-AS-19) + producer-side carrier (e.g., U-IS-07) + spec contract (e.g., C-IS-10 §10.1 STATE_LEDGER_ENTRY_SHAPE_EXPORT) |

### 4.2 Step 2 — Verify Pattern P1 byte-exact alignment

Per CXA v2.1 §2.3 Pattern P1: cross-axis citation grammar at consumer-side `Depends on:` declaration must match producer-side terminal exporter manifest verbatim. Specifically:

| Field | Verification |
|---|---|
| Carrier unit ID | Consumer-side `(cross-axis: AXIS)` annotation cites the canonical carrier (e.g., `U-IS-12 (cross-axis: IS)`); not a placeholder (e.g., `U-IS-NN`) |
| Export seam name | Consumer-side spec citation matches producer-side manifest's export-seam name verbatim (e.g., `IDEMPOTENCY_KEY_JOIN_EXPORT` not `Idempotency-Key Join Export`) |
| Spec § citation | Consumer-side citation cites the spec section that anchors the export seam (e.g., `C-IS-10 §10.2`) |

F3-02 absorption at IS plan v2.2 + OD plan v2.4 closed one Pattern P1 mis-alignment: OD plan v2.3 U-OD-20 acceptance #11 `Depends on:` `U-IS-NN (C-IS-10 §10.2)` → canonical carrier `U-IS-12`.

### 4.3 Step 3 — Wire the typed seam

Wire the consumer-side import / dependency declaration against the producer-side manifest export. Per `CXA-AL-1` (Meta-Architecture §7.6): **convention-based composition ≠ typed seam contracts**. Wiring is at the type-system level (Pydantic v2 model imports + interface declarations), not convention-level (CLAUDE.md prose).

### 4.4 Step 4 — Verify cardinality match against CXA v2.1

Aggregate cardinality at completion of each bucket:

| Bucket | Expected | Actual at composition close |
|---|---|---|
| AS → IS | 13 | [verify at composition close] |
| CP → IS | 36 | [verify at composition close] |
| OD → CP | 12 | [verify at composition close] |
| CP → AS | 24 | [verify at composition close] |
| OD → IS | 4 (per OD v2.4) / 6 (per CXA v2.1 baseline) | [verify; surface drift if applicable] |
| OD → AS | 10 | [verify at composition close] |

### 4.5 Step 5 — Acyclicity verification at composition close

Per CXA v2.1 §2.2: axis-level topological order is IS → AS → CP → OD (acyclic). Verify at composition close that no cross-axis edge violates this ordering. Within-axis cycles independently disproven at per-axis-plan §3 / §4 acyclicity verification.

### 4.6 Step 6 — Operator confirmation at bucket close

Per `Phase_7_Meta_Architecture_v1.md` §10.2.4 step 5 (adapted for 7c): operator confirms bucket close before next bucket opens.

## 5. Anti-leakage discipline

### 5.1 CXA-axis anti-leakage (Meta-Architecture §7.6)

> **CXA-AL-1.** Convention-based composition (H_E filesystem-primitives + sub-agents + operator-authored prompts) ≠ typed seam contracts (101 cross-axis edges across 6 buckets per CXA v2.1 §2.3 with Pattern P1 byte-exact alignment)
>
> *Anti-pattern foreclosed:* Treating "the sub-agent reads the JSONL ledger via convention" as functional satisfaction of the 36-edge CP→IS typed seam

### 5.2 Consumer-axis anti-leakage applies at seam wiring

When wiring a cross-axis seam, the consumer-axis anti-leakage rules bind:

| Bucket | Consumer axis | Anti-leakage rule(s) binding |
|---|---|---|
| AS → IS | IS | IS-AL-3 (state ledger entry shape); IS-AL-4 (Bash shell-outs as substitutions, not contracts) |
| CP → IS | IS | IS-AL-1 (path-class registry); IS-AL-3; IS-AL-4 |
| OD → IS | IS | IS-AL-3; IS-AL-4 |
| CP → AS | AS | AS-AL-1 (Permission modes ≠ SandboxTier); AS-AL-2 (built-in tools ≠ user-extensible H_T tools); AS-AL-3 (Skills isomorphism does NOT exempt cross-axis IS-dependencies) |
| OD → AS | AS | AS-AL-2; AS-AL-3 |
| OD → CP | CP | CP-AL-1 (sub-agent topology ≠ TopologyPattern); CP-AL-3 (`--fallback-model` ≠ multi-step chain); CP-AL-5 (CLAUDE.md ≠ typed WorkflowManifestEntry) |

### 5.3 Cross-cutting rules

| Rule | Application at composition |
|---|---|
| X-AL-1 | Cross-axis seams operate at MCP server process boundary (or pre-MCP-server in-process for non-MCP-bound contracts); never via convention |
| X-AL-2 | Seam instantiation is part of retirement criterion for the bucket's substitution entries (e.g., H_T-CXA-1 through H_T-CXA-5 substitutions per Meta-Architecture §5.6); retirement = wiring complete ∧ pre-wiring substitution no longer invoked |
| X-AL-3 | NEW cross-axis edges surfaced at composition time route to design-phase CXA revision (Class 1 fork); do NOT silently extend CXA v2.1 edge enumeration |

## 6. CXA-axis substitutions

Per `Phase_7_Meta_Architecture_v1.md` §5.6: **5 CXA-axis substitutions**. H_E classification per §4.4.5:

| Seam ID | Status | Brief rationale |
|---|---|---|
| H_T-CXA-1 (filesystem composition mechanism) | ~ partial | Filesystem composition mechanism present; not typed 13-edge contract |
| H_T-CXA-2 (CP → IS composition) | ~ partial | Mechanism present; typed 36-edge contract absent |
| H_T-CXA-3 (CP → AS composition) | ~ partial | Sub-agent + Skills + MCP composition; typed 24-edge contract absent |
| H_T-CXA-4 (OD-axis composition seams) | ✗ absent | OD-axis substrate absent at endpoints |
| H_T-CXA-5 (F-CP-01 Stage 3b inversion seam) | ✗ absent | Breaker primitive absent both endpoints |

CXA seam retirement triggers at the bucket's wiring completion event; delegate to `phase-7-substitution-retirement`.

## 7. Halt conditions

HALT seam instantiation and surface to operator (via `phase-7-back-flow-routing`) when:

| Halt trigger | Class | Routing target |
|---|---|---|
| CXA v2.1 §2.3.X bucket cardinality contradicts consumer-side plan declaration | 1 | CXA revision OR consumer-side plan revision (Class 1; operator decision on locus) |
| Producer-side terminal exporter manifest does not declare the export seam cited by consumer | 1 | IS / AS / CP plan revision (Class 1) |
| Pattern P1 byte-exact alignment fails (e.g., placeholder carrier ID, mis-named export seam) | 1 | Consumer-side plan revision (Form A — citation precision; F3-02 precedent) |
| New cross-axis edge surfaced at composition time | 1 | CXA revision (Class 1; X-AL-3 binds) |
| OD→IS edge wiring against CXA v2.1 baseline (6) vs OD plan v2.4 §4.5.1 canonical (4) | 2 | Operator decision (CXA-OD-IS-EDGE-DRIFT disposition) |

DO NOT silently absorb edge cardinality drift. DO NOT silently extend the 101-edge aggregate.

## 8. Reference artifacts

| Reference | Location | Authority |
|---|---|---|
| `Cross_Axis_Composition_Document_v2_1.md` | Design-phase workspace | CXA aggregate matrix + per-bucket enumeration + Pattern P1 |
| Per-axis `CLAUDE.md` §2.3 + §2.4 | This workspace | Per-axis edge inventory + edge profile |
| `Sub_Agent_Boundary_Specification_v1.md` §4.5 | Workspace root | sa-cxa sub-agent scope |
| `Phase_7_Meta_Architecture_v1.md` §5.6 + §6.3 + §7.6 | Design-phase workspace | CXA substitutions + cross-axis retirement dependencies + CXA-AL-1 |

---

*End of `phase-7-cross-axis-composition` skill. Loaded at sub-phase 7c activation. Delegates to `phase-7-substitution-retirement` (event-driven retirement); `phase-7-back-flow-routing` (fork detection).*
