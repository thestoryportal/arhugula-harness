# Cross-Voice Consistency Check — second-pass procedure

Source: `s14-c11-operator-local-spec.md` §"Residual concerns" (b) and `s15-phase2-prep-reconciliation.md` §"Open questions" (e). The phase-2 prep reconciliation walked the eleven voice specs once and surfaced known retroactive interactions across five voices (C3, C5, C7, C8, C9) plus a slate-wide system-property disposition (operator-burden cost-axis). **That was the first pass. This skill's check is the second pass.**

The check does not duplicate the first pass — those reconciliation entries are already in `s15-phase2-prep-reconciliation.md` and the absorbing voice's phase-2 SKILL.md drafting session applies them. The check looks for *additional* retroactive interactions the first pass missed, plus the standing alignment lints (CCR, TENSION, decision-claim vocabulary) that apply to every ingestion.

---

## When to run the full check vs. the light check

- **Light check** — per-session ingestion of one orchestrator envelope. CCR ↔ commitment alignment lint only. Run on every per-session spec section.
- **Full check** — integrated ingestion. All four parts. Run when:
  - Stage 1 design doc is being assembled.
  - Stage 1→2 PRD synthesis.
  - Stage 2→3 final-spec promotion.
  - Multiple voice specs are being ingested in the same session.
  - Operator explicitly requests *"run the consistency check"* on existing integrated content.

The full check is not optional on integrated ingestion. Skipping it violates the inherited obligation per s14 §"Residual concerns" (b).

---

## Part 1 — Retroactive-interaction scan

**The risk.** Each voice spec was written against the slate state at its session; later voices may produce commitments that retroactively interact with earlier voices' commitments in ways the earlier voice didn't anticipate. The s15 prep reconciliation surfaced several cases (HITL-recoverable retry-exit class addition to C5; five accretion-pattern additions to C7; etc.). The check looks for further cases.

**What to scan for.** When a new voice spec is being ingested, or when integrating across voice specs, scan prior voice specs for:

- **New commitments that constrain prior commitments.** A later voice's commitment narrows the action space of an earlier voice's commitment. Example pattern: a later voice declares an event-attribute set that a prior voice's instrumentation must emit; the prior voice's instrumentation surface gains an obligation it didn't declare.
- **New commitments that contradict prior commitments.** Two voices' commitments cannot both hold. Example pattern: a later voice's gate policy excludes a tool the earlier voice committed to exposing.
- **New commitments that enrich prior commitments.** A later voice extends an earlier voice's contract without contradicting it. Example pattern: a later voice adds attributes to an earlier voice's event schema, expanding without contradicting.
- **New commitments that move ownership.** A capability that an earlier voice anchored becomes a co-primary commitment with a later voice. Example pattern (from s15 prep): the audit-ledger schema becomes a C3↔C11 co-primary at s14 §11.3, having been C3-anchored in s6.

**Known patterns from the first pass (do not re-flag).** The s15 prep reconciliation already handled:

- C3: hash-chain schema absorbed (s14 §11.3); durable semantic cache as Tier-4 use-case (s9 §7.3).
- C5: five-class retry-exit taxonomy with reconciliation flag (s14 §7.5); `cause_attribution` annotation (s12 §7.5).
- C7: five accretion-pattern attributes (s14 §4.1.10); two event-name additions (s14 §4.1.33 / §4.1.34); one C10-source proposed attribute (s13 §7.8).
- C8: operator-burden cost-axis primitive — *proposing*; status pending operator confirmation before session 24.
- C9: two additional breaker-trip attributes (s13 §4.10).

If your scan turns up one of the above, that's not a finding — it's the first pass's known item. Cite the s15 prep reconciliation entry; do not re-flag.

**Patterns to actively look for** (not yet in first pass):

- Cross-voice naming collisions. Two voices use the same identifier for different things (e.g., a parameter name, an event name, a class label). Naming collisions silently break implementation.
- Implicit dependency ordering. Voice A's commitment requires voice B to have produced a specific contract first; the dependency was assumed but not declared.
- Capability-cut inconsistency. Two voices contribute to the same PRD capability but anchor incompatible framings (e.g., one frames retries as an in-loop validator concern; another frames retries as a control-flow concern; PRD capability "Failure recovery" inherits the inconsistency).
- Slate-wide assumption violations. The locked slate-wide assumptions (single-operator, local-first, etc.) are violated by an individual voice's commitment. The s15 prep reconciliation §"Open questions" (c) names the multi-operator absence as a slate-wide assumption per s14 §11.4 — verify each voice's commitments are consistent with single-operator deployment.

**Output for found interactions.** Each finding becomes a **proposed reconciliation entry** in the consistency report's *Found and flagged* section. The entry has the same shape as a phase-2 prep reconciliation entry: source citation, addition or contradiction summary, recommended absorption point (which voice's phase-2 work absorbs the change), confidence tag, status (`proposing` until operator decides).

---

## Part 2 — CCR ↔ commitment alignment lint (FM-4 mitigation)

**The risk.** The orchestrator emits a CCR per convening declaring which cross-cutting concerns are Touched / Not Touched. The synthesized spec section may include implicit commitments that contradict the CCR's declaration. Example: CCR says "blast radius — Not Touched", but the spec section's synthesis includes a commitment that creates a new tool-execution surface, which is implicitly a blast-radius concern.

**The check.** For each ingested envelope:

1. Read the CCR's six concerns and their Touched/Not Touched status.
2. Walk every commitment in the synthesized Layer C content.
3. For each commitment, ask: does this commitment touch any of the six cross-cutting concerns?
4. Compare the answer to the CCR.

If a commitment touches a concern the CCR declared Not Touched, that's a divergence.

**Concern indicators** (use as scanning heuristics, not exhaustive):

| Concern | Indicators in synthesized prose |
|---|---|
| #1 Security & blast radius | tool execution, file write, network call, secrets handling, credential, gate, sandbox, capability |
| #2 Observability hooks | event, span, attribute, trace, log, metric, instrumentation |
| #3 Token economy & cost | latency budget, token count, cache, model tier, cost-per-call, batch |
| #4 Reliability & failure containment | retry, backoff, breaker, fallback, recovery, idempotency, timeout |
| #5 Eval-ability | measure, eval, regression, holdout, benchmark, accuracy, threshold |
| #6 HITL & local-first deployment | operator, approval, intervention, local, on-device, sqlite, file path |

**Output for divergences.** Each divergence becomes a flagged finding in the consistency report's *Found and flagged* section. The flag has three required fields:

- **Commitment:** the specific commitment in the spec section (with D-ID if assigned).
- **Concern touched:** which of the six concerns.
- **CCR status:** what the CCR declared.
- **Reconciliation candidates:** *(a)* CCR was incomplete (re-emit); *(b)* commitment was inadvertent (tighten); *(c)* scope needs to be tightened (revisit). Operator decides which.

The lint is checkable; pass-or-flag. Do not silently merge a divergent commitment into a Not-Touched concern's silence.

---

## Part 3 — TENSION ↔ ledger alignment

**The risk.** A TENSION block in an ingested envelope may duplicate a known permanent tension (T-perm-1, T-perm-2, T-perm-3) that should have been carried forward by reference instead of re-surfaced as a new Layer-1 tension. Or a TENSION may engage a tension already in the ledger as Active, and the orchestrator emitted it as new — meaning the spec-writer should merge into the existing T-ID rather than assigning a new one.

**The check.** For each TENSION block ingested:

1. Read parties + issue.
2. Compare to permanent tension ledger:
   - Match against T-perm-1 (C4 ↔ C10, capability vs. gating).
   - Match against T-perm-2 (C2 ↔ C3, within-turn vs. across-turn).
   - Match against T-perm-3 (C1 ↔ C9, control-flow vs. reliability).
3. Compare to active T-IDs in the ledger.
4. If the tension is structurally identical to an existing entry, flag for merge.
5. If the tension is structurally similar but not identical (different specific framing), note the relationship and let the operator decide whether to merge or treat as distinct.

**Output for matches.** Each match becomes a flagged finding in the consistency report's *Found and flagged* section. The flag identifies:

- **Ingested TENSION block** (parties + issue).
- **Ledger entry it matches** (T-ID).
- **Relationship:** *identical* (recommend merge), *related* (recommend operator decision), *new framing of permanent* (recommend reference-by-T-ID without merging the old framing's prose).
- **Recommended action:** merge / cross-reference / treat as distinct.

---

## Part 4 — Decision-claim vocabulary scope check

**The risk.** Per s3 §8.1, each voice declares a decision-claim vocabulary in its component 4 — what kinds of commitments this voice makes. A voice making a commitment outside its declared vocabulary is making a scope-creep move. Spec-writer should detect and surface.

**The check.** For each commitment ingested in Layer C:

1. Identify the anchor voice for the commitment (typically the section's primary voice).
2. Read the anchor voice's component-4 decision-claim vocabulary.
3. Verify the commitment is the kind of claim the voice declared as making.
4. If not, flag.

**Examples of in-scope vocabulary** (illustrative, not exhaustive):

- C9 anchors "retry posture" and "fault containment" claims. A C9 commitment about a model-version selection is out-of-scope.
- C7 anchors "instrumentation" and "trace surface" claims. A C7 commitment about tool-call gate policies is out-of-scope.
- C10 anchors "gate" and "blast-radius" claims. A C10 commitment about state-persistence schema is out-of-scope.

**Common false positives.** Co-primary commitments often appear to escape one voice's vocabulary because they live at a seam owned by two voices. Verify that an apparent vocabulary breach is not actually a co-primary commitment with the appropriate joint anchoring before flagging.

**Output for breaches.** Each breach becomes a flagged finding in the consistency report's *Found and flagged* section. The flag identifies:

- **Commitment:** the specific commitment (with D-ID if assigned).
- **Anchor voice:** the voice claiming it.
- **Vocabulary breach:** which kind of claim this is, and why it's outside the voice's declared vocabulary.
- **Reconciliation candidates:** *(a)* re-anchor to the voice whose vocabulary covers it; *(b)* expand the voice's declared vocabulary explicitly (component-4 amendment); *(c)* this is actually a co-primary commitment that should anchor at a seam (revisit).

---

## Consistency report template

The check produces a consistency report appended to whatever spec artifact was being assembled. The report has three sections: *Found and applied* (clean cases the spec-writer reconciled at ingestion), *Found and flagged* (cases requiring operator decision), *No findings* (clean ingestion).

```markdown
## Consistency report

**Scope:** [light | full] — [what content was checked]

**Run against:** s15-phase2-prep-reconciliation.md plus all voice specs s4–s14 plus living documents.

### Found and applied

[Cases the spec-writer reconciled silently at ingestion. Typically empty; this section exists for low-stakes mechanical reconciliations the spec-writer is permitted to make autonomously — e.g., assigning a CCR-ID. If non-empty, every entry is auditable post-hoc.]

### Found and flagged

#### Finding F-NNN-1 — [short title]

- **Type:** [retroactive interaction | CCR/commitment divergence | TENSION/ledger duplicate | decision-claim vocabulary breach]
- **Source:** [where in the ingestion this was detected]
- **Issue:** [one sentence stating the inconsistency]
- **Reconciliation candidates:** [enumerated options per the check's Part]
- **Recommendation:** [spec-writer's recommendation, with confidence tag — typically [MODERATE] proposing]
- **Status:** *proposing* — operator decides at session close.

[... more findings ...]

### No findings

[For each of the four check parts where nothing was found, state explicitly. Silence is not the same as "checked and found nothing"; the operator needs to know which parts ran cleanly.]

- Part 1 (retroactive-interaction scan): no new findings beyond s15-prep first pass.
- Part 2 (CCR ↔ commitment lint): no divergences.
- Part 3 (TENSION ↔ ledger alignment): no duplicates.
- Part 4 (decision-claim vocabulary): no breaches.
```

The flagged-findings section is the operator's actionable surface. The other two sections give the operator confidence the check actually ran.

---

## What this check is not

- **Not a content review.** The check verifies *structural* consistency (CCR ↔ commitment, TENSION ↔ ledger, vocabulary scope, retroactive interaction). It does not verify whether voice claims are *substantively* correct. Substantive correctness is the voice's responsibility, audited by other voices during convening.
- **Not a re-litigation surface.** Findings are flagged, not resolved by the spec-writer. The operator decides reconciliation. The spec-writer presents options with rationale.
- **Not a substitute for the first pass.** s15 prep reconciliation is canonical for the first-pass findings. The spec-writer's check builds on it; it does not replace it.
- **Not infallible.** The check is heuristic. It will miss cases. Surfaced findings may turn out to be false positives. The operator's judgment is the final arbiter; the check exists to make the spec-writer's reading visible, not to replace operator review.
