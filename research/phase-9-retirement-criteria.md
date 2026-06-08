# Phase-9 Retirement Criteria Research Brief

Filed: 2026-06-08
Roadmap item: `R-901-phase-9-retirement-criteria`
Disposition: research-only + roadmap selector guidance; no design-substrate back-flow in this arc.

## Research question

After Phase 8 has closed historical substitution accounting, what should a Phase-9 retirement model control, and when should a later finding become research-only, roadmap-only, implementation/back-flow work, or a design-substrate amendment?

This question is narrow by design. Phase 9 should not reopen Phase 8's historical declaration by default. It should govern post-Phase-8 changes that alter the live ledger, retire bounded residuals with new evidence, or identify a producer/composer gap that cannot honestly be closed by wiring a placeholder.

## Sources queried

Project corpus:

- `.harness/phase-8-graduation.md`
- `.harness/R-700-phase-8-closure-accounting-draft.md`
- `.harness/phase-7d-retirement-events-batch-51.md`
- `.harness/phase-7d-retirement-events-batch-52.md`
- `.harness/phase-7d-retirement-events-batch-53.md`
- `.harness/phase-7d-retirement-events-batch-54.md`
- `.harness/retirement-event-pattern-catalogue.md`
- `Project_Roadmap_v1.md`

NotebookLM:

- Notebook: Agent Harness Engineering (`57b8d946-830c-42dd-b201-ac117a8af951`)
- Query result: the notebook does not contain the project-specific terms "arhugula", "Phase-8 substitution accounting", "Phase-9 retirement criteria", "bounded residuals", "live-ledger back-flow", or "producer-gated CXA seams".
- Useful adjacent sources surfaced by NotebookLM: `Pattern_Reference_Catalog_v1.0.md` for research-artifact vs production-harness strata, `agent-harness-eng-deep-research-baseline.md` for state-ledger/WAL and context-management themes, and the context-management sources for harness state-safety concerns.

Perplexity:

- Query result: the first pass returned generic governance advice but search drifted toward financial/human-retirement sources because of the word "retirement".
- Use in this brief: weak external corroboration only. The authoritative criteria below are derived from the local harness corpus and NotebookLM corpus-boundary result.

## Findings

### 1. Phase 8 is a historical accounting close, not a universal production proof

`.harness/phase-8-graduation.md` explicitly states that Phase 8 graduates substitution accounting, not every capability exercised in production. The canonical historical declaration remains `46/54` retired and `49/54` pipeline-advanced. That declaration is not rewritten by later work.

The same document now carries a forward supersession note: later batches moved Files, Managed Agents, OD-4, CXA-4, and CXA-3 through live-ledger back-flow, advancing the live ledger without rewriting the Phase-8 event. That is the model Phase 9 should preserve.

### 2. Bounded residual is an honest terminal accounting shape, but not a permanent immunity label

Batch 51 is the clearest precedent. OD-6 became `RETIRED-AS-BOUNDED-RESIDUAL` because the substrate existed but the collector-to-sqlite loop was dormant at MVP. The close was legitimate for Phase-8 accounting because the rationale and future milestone were explicit.

Batch 52 shows the follow-on rule. Rows previously accepted as indefinite defers can move to substantive retirement once live evidence exists. Files and Managed Agents did exactly that. Therefore Phase 9 should not treat bounded residuals as failures, but it should define the conditions under which they can be promoted.

### 3. Live-ledger back-flow is forward-only and evidence-triggered

Batches 52, 53, and 54 establish a disciplined back-flow pattern:

- Batch 52: R-810/R-820 live provider evidence moved AS-8e, AS-8f, and CP-17 to substantive retirement.
- Batch 53: OD-4 runtime residual and CXA-4 bookkeeping residual moved to substantive retirement.
- Batch 54: the CP->AS runtime composer moved CXA-3 to substantive retirement.

In each case, the new record names the prior state, evidence, transit, non-transits, and co-published artifacts. That is enough for Phase 9; it does not require a new substrate layer unless future findings change contracts or invariants.

### 4. Producer-gated seams should stay gated until a real producer exists

The remaining live non-retired rows are CXA-1 and CXA-2. Their current status is not "forgotten work"; it is a safety property.

- CXA-1 still lacks a production AS secret-fetch producer.
- CXA-2 still lacks production HITL rewrite and engine recovery-loop producers for the remaining CP->IS methods.

The dashboard/status discipline is correct to prevent hollow wiring. Phase 9 should encode this as a decision rule: a seam is not closable merely because a consumer API exists; it needs a real upstream producer, a design narrowing, or a documented back-flow decision.

### 5. NotebookLM does not currently contain this project's Phase-8/Phase-9 terms

The NotebookLM query is useful mostly as negative evidence. The research notebook supports the broader harness-engineering ideas of lifecycle phases, ledgers, context/state safety, and research-vs-production strata, but the project-specific Phase-8/Phase-9 closure model lives in the repo corpus. If Phase 9 becomes a durable methodology concept, the notebook corpus should be updated with the Phase-8 graduation and post-Phase-8 batch records.

## Phase-9 criteria

Phase 9 should be a decision layer for post-Phase-8 findings. It should ask these questions in order.

1. Does the finding change the historical Phase-8 declaration?

   Default answer: no. Historical Phase 8 remains fixed unless the prior record is internally inconsistent and needs a forward-only supersession.

2. Is there new runtime/live evidence for a previously bounded, partial, or deferred row?

   If yes, file a back-flow batch that names the prior state, evidence, transit, non-transits, and co-published artifacts.

3. Is there a real producer for a producer-gated seam?

   If no, keep the seam gated. Do not wire placeholders just to move a count. If yes, implement or test the smallest producer-to-consumer path and then reassess the row.

4. Does the finding alter a contract, invariant, lifecycle phase, or required operator behavior?

   If yes, route to design-substrate back-flow or fork/amendment before implementation.

5. Is the finding only a conceptual model or evidence gap?

   If yes, keep it research-only or roadmap-only.

## Routing outcomes

Research-only:

- Use when the result clarifies the model but changes no roadmap state, code, spec, or live ledger.
- R-901 itself lands here. It defines the decision model and records the research basis.

Roadmap-only:

- Use when a new named work item is needed, but no implementation should start yet.
- Example: a future `R-902` would be appropriate if the team decides to formalize Phase-9 workflow mechanics or update the NotebookLM corpus with Phase-8 records.

Implementation/back-flow:

- Use when live evidence or a real producer exists and the current substrate can be advanced without changing the contract.
- Examples already shipped: batches 52, 53, and 54.

Design-substrate amendment:

- Use when the correct answer would change a contract, required lifecycle phase, execution semantics, or cross-axis invariant.
- This arc does not surface such a tension. No design-substrate amendment is owed now.

## Recommendation

Close R-901 as research-only. Keep Phase 9 as a lightweight post-closure decision model rather than a new mandatory lifecycle phase. The current next-action selector should return to the genuine remaining gates:

1. R-CXA-2 if a real HITL rewrite or engine recovery-loop producer appears, or if a design/back-flow amendment changes the producer requirement.
2. R-CXA-1 if a real scoped AS secret-fetch producer appears, or if a design/back-flow amendment changes the seam scope.

Do not create a design-substrate amendment from R-901 alone. The project already has the necessary forward-only machinery: roadmap entries, retirement batches, substitution ledger, dashboard generator, and producer-gated watch discipline.
