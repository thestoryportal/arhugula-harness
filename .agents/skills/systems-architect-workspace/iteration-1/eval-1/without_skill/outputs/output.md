# U-CP-22 TopologyPattern Enum — Vocabulary Call

**Question.** Should U-CP-22's `TopologyPattern` enum use the spec C-CP-10 §10.1 vocabulary or the plan's (`Implementation_Plan_Control_Plane_v2_1.md` U-CP-22)?

**Decision.** Use the **spec C-CP-10 §10.1 vocabulary**. The six members are the spec's named patterns, transcribed to Python `Enum` member identifiers in UPPER_SNAKE_CASE with the kebab-case spec strings preserved verbatim as the member values.

---

## 1. Why this is not a free choice

You asked me to "just pick one," but the honest finding is that this is not a stylistic toss-up between two equally valid vocabularies. It is a **substantive semantic divergence**, and one side is authoritative.

There are in fact **three** divergent vocabularies in the workspace for the same 6-pattern enum:

| Source | Members |
|---|---|
| **Spec C-CP-10 §10.1** (`Spec_Control_Plane_v1_2.md` §10.1) | `single-threaded-linear`, `orchestrator-workers`, `decentralized-handoff`, `hierarchical-delegation`, `evaluator-optimizer`, `parallelization` |
| **Plan U-CP-22** (`Implementation_Plan_Control_Plane_v2_1.md` line 1185) | `SINGLE_AGENT`, `SEQUENTIAL_HANDOFF`, `PARENT_FANOUT_AGGREGATE`, `RECONCILER_MESH`, `ROUTER_DELEGATE`, `PIPELINE_STAGES` |
| **Root + CP `CLAUDE.md`** (CP-AL-1, root §5.1) | `ORCHESTRATOR_WORKERS`, `DECENTRALIZED_HANDOFF`, `EVALUATOR_OPTIMIZER`, `PARALLELIZATION`, `ROUTING`, `SEQUENTIAL_PIPELINE` |

These are not casing variants of one list. The **member identities themselves** disagree. The plan's `RECONCILER_MESH` and `ROUTER_DELEGATE` have no clean 1:1 mapping to any spec pattern name; the plan drops `hierarchical-delegation` and `evaluator-optimizer` as named concepts entirely. Picking "the plan's vocabulary" would therefore not just rename the spec — it would import a different taxonomy.

## 2. Authority chain settles it

Per `CLAUDE.md` §1.3 (canonical authority chain):

> ADR → ADD → PRD → per-axis spec v1.x → per-axis plan v2.x → Phase 7 implementation. **Earlier artifacts in the chain are canonical for later artifacts.**

The spec (C-CP-10) is canonical *for* the plan (U-CP-22). Where they disagree, the spec wins. Confirming this:

- The plan's own U-CP-22 acceptance criterion #1 reads: *"`TopologyPattern` declares exactly six values per C-CP-10 §10.1 **verbatim**."* The plan does not claim authority to redefine the vocabulary — it claims to transcribe the spec. It then fails its own criterion: `SINGLE_AGENT` etc. are not C-CP-10 §10.1 verbatim. The plan's signature block is a transcription **defect**, not a competing decision.
- C-CP-10 §10.1 states the taxonomy is **closed** at ADR-D4 v1.1 §1.1; the spec is itself transcribing the ADR. The ADR-anchored names are the kebab-case ones.
- Execution invariant **I-1** (`CLAUDE.md` §8): "Canonical artifact citations resolve byte-exact." A plan that cites "§10.1 verbatim" while emitting different tokens violates I-1.

## 3. The call, concretely

`TopologyPattern` for U-CP-22 (Python 3.12 / `enum.Enum`, `str` mixin so the value is the canonical wire token used by `topology.pattern` per Spec §13 `topology.*` namespace):

```python
class TopologyPattern(str, Enum):
    SINGLE_THREADED_LINEAR  = "single-threaded-linear"
    ORCHESTRATOR_WORKERS    = "orchestrator-workers"
    DECENTRALIZED_HANDOFF   = "decentralized-handoff"
    HIERARCHICAL_DELEGATION = "hierarchical-delegation"
    EVALUATOR_OPTIMIZER     = "evaluator-optimizer"
    PARALLELIZATION         = "parallelization"
```

Rationale for the form:
- **Values** are the spec §10.1 kebab-case strings *byte-exact* — these are what `TopologyDeclaration.pattern` (Spec §10.2) and the `topology.pattern` OTel attribute (Spec §13, "enum string per C-CP-10 §10.1 (six values)") serialize. Anything else breaks the audit-ledger / OTel surface and CXA edge alignment.
- **Member identifiers** are UPPER_SNAKE because kebab-case is not a legal Python identifier; UPPER_SNAKE is the stack-idiomatic enum-member convention. This is a mechanical encoding of the spec names, not a redefinition — each identifier is the obvious uppercasing of its spec string.

`CascadePolicy` (also declared in U-CP-22) has the **same defect**: plan emits `COMPLETE_ALL / CANCEL_ON_FIRST_FAIL / PAUSE_ON_FIRST_FAIL`; spec C-CP-10 §10.2 / §10.3 and §10.2 `TopologyDeclaration` give `"pause" | "proceed" | "cascade-cancel"`. Apply the identical rule — spec values verbatim:

```python
class CascadePolicy(str, Enum):
    PAUSE          = "pause"
    PROCEED        = "proceed"
    CASCADE_CANCEL = "cascade-cancel"
```

## 4. Required follow-up — this is a Class 1 back-flow fork

Making the implementation call does **not** close the issue. Per `CLAUDE.md` §4.3 and §4.4 (X-AL-3: no silent H_T design extension at Phase 7) and invariant **I-5**:

- The plan `Implementation_Plan_Control_Plane_v2_*.md` U-CP-22 signature block is **wrong** — it diverges from the spec it claims to transcribe. Silently coding to the spec while leaving the plan uncorrected is exactly the "silent absorption" failure mode `CLAUDE.md` §4.3 names as the worst case. Downstream units that read `TopologyPattern` (U-CP-23, U-CP-25, U-CP-43, U-CP-50, plus the audit/OTel and CXA seams) would inherit ambiguity.
- The `CLAUDE.md` files (root §5.1 / CP §168 CP-AL-1) carry a **third** vocabulary (`ROUTING`, `SEQUENTIAL_PIPELINE`, etc.) — also non-conformant to C-CP-10 §10.1. CP-AL-1's anti-leakage point stands regardless of token spelling, but the enumerated list should be reconciled to the spec to avoid a fourth round of confusion.

**Recommended routing:** File a **Class 1 (or Class 3, operator's call) back-flow record** correcting the U-CP-22 signature block (and the `CLAUDE.md` enum citations) to the C-CP-10 §10.1 vocabulary. The plan is plan v2.1/v2.2/v2.3 — v2.2 and v2.3 explicitly preserve U-CP-22 "verbatim from v2.1," so the defect is live in the current canonical plan and needs an actual edit, not just a note. Per the workspace's `spec-tension-record-pattern` memory, fix in-CLI and track in a tension record with the clearing decision logged.

**Bottom line for moving forward now:** implement U-CP-22 with the spec vocabulary above. You are unblocked. But flag the plan defect to the operator — do not let U-CP-23+ build against the plan's `RECONCILER_MESH`/`ROUTER_DELEGATE` tokens.

---

*Artifacts consulted (all absolute):*
- `/Users/robertrhu/Projects/arhugula-v2/design-substrate/Spec_Control_Plane_v1_2.md` §10 / §10.1 / §10.2 / §10.3 (lines 822–883), §13 `topology.*` (line 1220)
- `/Users/robertrhu/Projects/arhugula-v2/design-substrate/Implementation_Plan_Control_Plane_v2_1.md` U-CP-22 (lines 1172–1212), §4.1.10 traceability (lines 3443–3449)
- `/Users/robertrhu/Projects/arhugula-v2/design-substrate/Implementation_Plan_Control_Plane_v2_2.md` / `_v2_3.md` — confirm U-CP-22 preserved verbatim, defect still live
- `/Users/robertrhu/Projects/arhugula-v2/CLAUDE.md` §1.3, §4.3, §4.4, §8 (I-1, I-5)
- `/Users/robertrhu/Projects/arhugula-v2/harness-cp/CLAUDE.md` CP-AL-1 (line 168)

*No repository files were modified.*
