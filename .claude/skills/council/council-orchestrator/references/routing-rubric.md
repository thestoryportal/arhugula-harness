<!--
VENUE PROVENANCE — imported 2026-05-29 from Drive folder 1Je_dlorQQEIRp...
References to `s2-orchestrator-design.md` are historical provenance pointers.
The operative routing-architecture canonical lives at this skill's SKILL.md
and these references/ files in this workspace.
-->

# Routing Rubric — the four-layer signal

This document is the operational expansion of the four-layer signal procedure referenced by the council orchestrator's SKILL.md. When the SKILL.md says "score voices per Layer C," this is the procedure.

---

## Layer A — Operator override (terminal)

**When the operator names voices or types explicitly, honor it. No further routing analysis.**

### Recognition signals

- **Voice naming:** `C1`, `C2`, `C5`, `C11` (and so on through C11) appearing as a directive in the prompt — *"C1 + C5 on this," "convene C7 and C8," "what does C9 think."*
- **Question-type tagging:** the operator tags the question type explicitly — *"this is a tradeoff question, please convene accordingly."*
- **Full-council tag:** the operator says *"full council"*, *"convene the whole slate"*, or *"all voices."* This invokes the full-council pass per §"Convening size" below — warn the operator about context cost before proceeding.

### Behavior under override

If voices are named: use exactly that set. The orchestrator does NOT add unnamed voices via Layer C scoring even if they would have scored above threshold. The operator's set is treated as the convening.

If a question type is tagged: use that type's default cluster as the starting point for Layer C selection (do not re-classify against Layer B).

If the override is partial (operator names a primary but not consultants): use the named voice as primary; select consultants via Layer C.

If the override is invalid (named voice is out of slate; tag is not one of the five canonical types): surface the issue to the operator and ask, rather than silently substituting.

---

## Layer B — Question-type templating (primary signal when no override)

**Classify the prompt into one of five canonical types. Each type has a default voice cluster.**

### The five types and their default clusters

| Type | Trigger phrasing | Default cluster |
|---|---|---|
| **Architectural** | "how should X be structured," "what's the topology for Y," "how do these fit together," "what's the layout for Z" | C1 anchor + 1–2 adjacent voices via Layer C. Within-turn architectural → C2 anchors. Across-turn lifecycle → C3 anchors. Action-surface aggregate → C4 anchors. Trace-topology → C7 anchors. Routing-as-topology → C1 + C6 co-primary. |
| **Contract** | "what does the interface between X and Y look like," "what guarantees does Z provide," "what's the schema for…," "what's the pass condition / payload / trust tier of…" | Contract-owner anchors. Tool / MCP / Skill content → **C4**. Validation gate → **C5**. Action-safety / permission / trust → **C10**. Span schema / observability → **C7**. Eval / holdout / regression → **C8**. Durability / rollback / state → **C3**. Model-strategy / fallback-chain → **C6**. Adjacent voices via Layer C. |
| **Failure-mode** | "what happens when X fails," "what's the blast radius of Y," "how does the harness recover from Z," "what does the operator see when…" | Default: C9 anchor + C10 + C11; add C7 if observability of the failure is core. **C5** anchors if the failure mode is gate-classification. **C10** anchors (promotes from default-consultant) if the failure mode is a blast-radius outlier or trust-boundary breach. **C11** anchors if the failing surface is the operator's interface. **C6** anchors if the question is fallback-chain composition under failure. |
| **Tradeoff** | "should we choose X or Y," "what's the cost of doing Z," "is it worth using A," "X vs Y at this scale" | Multi-anchor / often co-primary. Cost-vs-quality of model strategy → **C6**. Cost-vs-quality of context construction → **C2**. Cost-vs-capability of action surface → **C4**. Reliability vs cost / latency → **C9**. Eval-cost vs eval-coverage → **C8**. Operator-burden vs autonomy → **C11**. Most likely to invoke whole-council escalation when the axis is cross-cutting — surface this to the operator, don't escalate silently. |
| **Cross-cutting** | "how do we handle observability for the whole harness," "what's our slate-wide reliability posture," "how does cost flow across all the voices" | Concern-owner anchors. Security #1 → **C10**. Observability #2 → **C7**. Cost #3 → joint C2/C4/C6 (pick co-primaries by which cost driver is dominant). Reliability #4 → **C9**. Eval-ability #5 → **C8**. HITL/local-first #6 → **C11**. Adjacent voices via Layer C. |

### Classification guidance — when the type is ambiguous

A prompt can read as multiple types. When this happens:

- **If the prompt asks for a decision** (build / don't-build, choose / not-choose), it's a **tradeoff**.
- **If the prompt asks for a structure or topology**, it's **architectural**.
- **If the prompt asks for a definition of an interface or guarantee**, it's a **contract**.
- **If the prompt names a failing condition explicitly**, it's a **failure-mode**.
- **If the prompt invokes a cross-cutting concern by name** (security, observability, cost, reliability, eval, HITL/local-first), it's **cross-cutting**.
- **If the prompt is genuinely two types at once** (common — e.g., "what's the contract for the validator gate, and what does it return on failure" is contract + failure-mode), classify as the type with the more specific anchor and let Layer C pull the second-type voice as a consultant.

If still ambiguous after this guidance, surface the ambiguity to the operator before convening — *"I can read this as architectural or tradeoff; the convening is different. Which framing is closer?"* This is preferable to silently picking and routing wrong.

---

## Layer C — Scope-keyword scoring (refinement)

**For each voice, score the prompt against the voice's scope-keyword profile (in `voice-roster.md` or the source voice SKILL.md). Convene voices that score above threshold up to the size cap.**

### Scoring procedure

1. **For each voice C1–C11**, examine the prompt for terms in the voice's strong-keyword cues (full list in `voice-roster.md` / source SKILL.md §3.3).
2. **Count distinct strong-keyword hits** — multiple hits of the same term don't add weight; distinct terms in the voice's profile do.
3. **Apply question-type prior** — if the voice is the natural anchor for the Layer B type, multiply by the prior weight (default 2× — voices anchoring the classified type are favored).
4. **Apply negative-keyword penalty** — if the prompt contains terms in the voice's negative-keyword list (signals "this voice should NOT anchor"), subtract from the score.
5. **Apply co-primary boost** — if the prompt phrasing engages a known co-primary seam (e.g., "validator + topology" is C5 ↔ C1; "capability + gating" is C4 ↔ C10), boost both voices in the seam.

### Threshold and convening

- **Threshold:** at least one strong-keyword hit OR question-type prior alignment. Voices with zero on both are not candidates.
- **Convene:** the top scorers up to default size (3 voices) or hard cap (5 voices). See "Convening size" below for size policy.

### Tie-breaking

When two voices tie for a consultant slot:

- Prefer the voice that owns a Touched cross-cutting concern (per CCR §3) over a voice that does not.
- Prefer the voice that is named in a known permanent tension on the topic over a voice that is not.
- If still tied, prefer the voice the operator has not seen in the last three sessions (rotation freshness, where session history is observable).
- If no further signal, surface the tie to the operator and let them break it.

---

## Layer D — Voluntary self-volunteer (during convening)

**Once convened, any voice can flag during its turn that another non-convened voice should join.**

### Approval logic

- If total voices (current + new) ≤ hard cap (5): auto-approve. Note the addition in the Convening Block as a Layer-D add with rationale.
- If at the cap: surface the request to the operator with the volunteering voice's rationale. Pause. Resume after operator decision.
- The volunteering voice must give a one-sentence rationale — not a vague "C7 might want to weigh in" but a specific "C7 should weigh in because the breaker-trip event schema is at stake and C7 owns the catalog."

### Recusal

A convened voice may flag "this isn't really my territory" and decline substantive contribution — note the recusal in the Convening Block. This reduces effective convening size; consider whether to backfill (Layer C re-scoring on the residual prompt) or proceed with reduced size.

---

## Convening size policy

- **Default:** 3 voices (1 primary + 2 consultants).
- **Hard cap:** 5 voices.
- **Full-council pass (11 voices):** only on explicit operator tag (`"full council"`, `"convene the whole slate"`, etc.). Warn the operator about context cost first.

### Voice asymmetry within a convening

- **Exactly one primary** anchors the substantive answer. The primary speaks first (after the Convening Block + CCR), produces the load-bearing position, and frames what consultants react to.
- **Co-primary** is allowed when the topic genuinely has two equal anchors — common cases: C4 ↔ C5 contract questions, C2 ↔ C3 boundary questions, C1 ↔ C9 reliability-control questions, C5 ↔ C8 judge-as-validator-vs-judge-as-eval-tool, C4 ↔ C10 capability-vs-gating, C6 ↔ C9 fallback-composition-vs-mechanics. **Maximum two co-primaries.** Three co-primaries indicates the topic is genuinely whole-council; either escalate to full-council or accept that the topic is too broad and ask the operator to narrow.
- **Consultants** speak after primary. Each consultant must produce one of:
   - **Concur with rationale** — agreement is acceptable but rationale must tie the primary's position to the consultant's domain. *"Looks good"* alone is not valid; re-prompt for rationale.
   - **Surface a tension** — explicit disagreement / gap / conflict-of-priorities, framed from the consultant's domain.
   - **Propose a refinement** — additive contribution that doesn't disagree but extends or constrains the primary's position.

"No comment" is not a valid consultant response. If a convened voice has nothing to contribute, it should have recused (Layer D) rather than been convened in the first place.

### Consulted-by-reference (not convening)

When the orchestrator wants a voice's perspective without spending a turn on it (apply a known C2 principle without convening C2 live), cite the voice's SKILL.md rather than convene. This is **not** convening; the voice is **not** in the Convening Block. It is documented as a citation in the response (cite the specific §-pointer of the voice's SKILL.md).
