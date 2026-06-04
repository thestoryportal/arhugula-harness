---
description: Run the genuine multi-agent council workflow (council → adversarial → Codex/advisor, reconcile-to-zero) over a HARNESS design/planning question, auto-selecting the relevant cN voices for the harness layer the question touches. Use for a design/spec/plan decision with a nameable cross-domain tension.
argument-hint: <the harness design/planning question> [e.g. "ground the AS-axis sandbox tiering" / "should CP retry policy be cost- or reliability-first"]
allowed-tools: Workflow, Agent, Bash, Read, Write, Edit, advisor
---
Run the **harness-layer-aware council workflow** for this question:

> $ARGUMENTS

**Spec (follow it exactly):** `.harness/council/council-workflow.harness-aware.yaml`
**Prose companion:** `.harness/council/COUNCIL-WORKFLOW.md`
**Lived precedent (read for shape):** `.harness/council/context-memory-grounding/`

Procedure:
1. **Pre-convene** — apply the nameable-tension gate (if no cross-domain tension can be named in advance, STOP and route to a single voice + `advisor()` instead). Identify which harness layer/axis the question touches, and convene the voices from the spec's `layer_voice_map` (primaries = the layer's domain center; consultants = cross-cutting). Name the convening spine-tension. Open a charter + ledger tree.
2. **Run the stages** E1 (A1 primaries-independent → A2 consultants-react-to-primaries → B cross-read DEBATE) → E2 adversarial #1 → E2b reconcile → E3 Codex(out-of-family, descriptive primer ONLY)+advisor(transcript-aware) → E3b reconcile → E4 gate → close. Every voice/reviewer is a **genuine agent invocation** that adopts its skill (never core-agent reference-reads); fan out gently in small waves.
3. **Honor the `hil_gates`** — HALT for operator go-ahead before each full-council convening (E1, E2b, E3b/consolidated); primaries→consultants→cross-read ordering; decorrelated-reviewer wiring; reconcile-to-zero per pairwise gate. (If the operator has said "without HIL", run autonomously but still stop at destructive/irreversible/outward-facing boundaries.)
4. **Close** — fold any residuals; the deliverable is a conscious versioned move (vN + change-note); register the arc in `Project_Roadmap_v1.md` (R-NNN; NOT the dashboard — it self-heals); commit additive-only; PR per operator direction.
