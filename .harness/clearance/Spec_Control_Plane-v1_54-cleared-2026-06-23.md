---
artifact: design-substrate/Spec_Control_Plane_v1_54.md
version: v1.54
cleared_at: 2026-06-23T00:30:00-06:00
clearance_type: Phase-7-absorbed-via-operator-ratified-amendment
back_reference:
  - .harness/r-fs-1-final-closure-plan.md (arc-a)
  - .harness/r-fs-1-arc-a-postjoin-14.23-hollow-finding.md (the two-layer hollow-trap finding + the A AUQ resolution)
  - .harness/r-fs-1-b-fanout-output-replay-impl-design.md (the §25.12-D1 materializability finding; B-full refuted → A)
  - .harness/council/b-postjoin-llm-synthesis/30-synthesis.md (C1⊥C9 dyadic council, PR #711)
  - PR for the arc-a bundle (this branch arc-a-postjoin-llm-synthesis)
merge_commit: <filled at merge>
reviewer_chain:
  - C1⊥C9 dyadic council (genuine dedicated-agent voices, independent → cross-read) + §10.9 probe-resolution + advisor red-team (PR #711)
  - advisor — surfaced the OPTION-B-capture-only #705 hollow trap (reachability ≠ consistency) AND the coherent-B-full §25.12-D1 binary-ledger blocker (no partial fan-out state); both verified empirically against harness_cp.workflow_driver
  - Operator AskUserQuestion 2026-06-23 — chose A (synthesis + loud disclosure now; reproducibility = the registered B-FANOUT-OUTPUT-REPLAY follow-on) over the hollow capture-only B and the larger B-full
  - spec-writer apply pass (this arc, applied by the core agent holding the grounded materializable design)
supersedes: <none>
superseded_by: <none>
---

# Clearance — `Spec_Control_Plane v1.54`

v1.54 amends CP spec v1.53 with the R-FS-1 arc `B-POSTJOIN-LLM-SYNTHESIS` (operator-ratified A, 2026-06-23):

- **§5.2 `step.kind` enum 6 → 7** (ADDS `post-join-synthesis`) + its **§25.2 `StepKind` materialization** — the operator-ratified Workflow §4.1.2 Class-2 revision (the second additive step-kind after v1.39 `managed-agents`). An OPT-IN terminal post-barrier step that LLM-composes a concurrent fan-out's branch-index-ordered sibling outputs.
- **§25.12 determinism-boundary Point 2 (aggregator purity)** amended — when a workflow opts into a `POST_JOIN_SYNTHESIS` terminal step, that run's aggregation is a non-deterministic LLM compose. **Point 1 + the branch-index ordering of the input set are PRESERVED VERBATIM**; the default deterministic fold is byte-identical for every non-opted run.
- **§3 post-barrier dispatch semantics** — the 3 concurrent strategies carve the terminal synthesis step out of the branch set + dispatch it at the barrier reading `collected` (branch-index-ordered) via `StepExecutionContext.sibling_outputs`; the synthesis output replaces the fold on SUCCESS; a disclosing post-barrier step ledger entry (`workflow:{wf}:post-join-synthesis:{N}`) + a trace event make the §25.12 Point-2 sacrifice LOUD. Default fold byte-identical (negative control).

The committed-invariant sacrifice (§25.12 Point-2) is operator-ratified; the bounded residual (the synthesized aggregate is non-deterministic) is forward-looking with an empty divergence window in the currently-wired harness (the 5 non-linear strategies are crash-resume-blind). Reproducible cached-replay is the **registered follow-on `B-FANOUT-OUTPUT-REPLAY`** (a separate §25.12-Point-1/D1 reckoning — its own C1⊥C9 council + gate), explicitly NOT this arc.

NO §5.2-hash / IS change (the `sibling_outputs` carrier is hash-inert; disclosure rides the driver's step entry). NO new CXA edge (reuses the StepKindDispatcherRegistry + the C-RT-16 LLM-dispatch seam). Paired runtime delta: `Spec_Harness_Runtime_v1.md` v1.75 §14.24 C-RT-33 (`PostJoinSynthesisStepDispatcher`). IS / OD / AS / ADR specs UNCHANGED; CXA v2.20 UNCHANGED.

Phase 7 consumers may treat CP spec v1.54 as canonical for the §5.2/§25.2 7-member `StepKind` + the §25.12 Point-2 opt-in-synthesis amendment + the §3 post-barrier dispatch semantics. Other contracts PRESERVED VERBATIM per the delta-only-spec-file convention.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- Reproducible cached-replay (capture + replay the synthesized aggregate across a fan-out crash-resume) is OUT of scope — the registered `B-FANOUT-OUTPUT-REPLAY` follow-on; it needs a durable per-branch-completion substrate + a §25.12-D1 sacrifice, gated separately.
- See `.harness/clearance/README.md` for marker discipline.
