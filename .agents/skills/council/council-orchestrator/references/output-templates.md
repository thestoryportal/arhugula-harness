<!--
VENUE PROVENANCE — imported 2026-05-29 from Drive folder 1Je_dlorQQEIRp...
References to `s2-orchestrator-design.md` / `s3-spec-writer-architecture.md` are
historical provenance pointers. The operative format-contract canonical lives here.
-->

# Output Templates — Convening Block, CCR, TENSION block

The format below is the contract surface — keep it stable across responses so downstream parsing is reliable. Spec-writer + adversarial-reviewer skills both consume these structures as embedded artifacts.

---

## Convening Block — emitted at the head of every response

Use this exact structure. Markdown headings + bulleted fields. Values can be prose; field names must be stable.

```markdown
## Convening Block

- **Question type:** [architectural | contract | failure-mode | tradeoff | cross-cutting]
- **Voices convened:** [Cn (primary), Cn (consultant), Cn (consultant)]
   - Co-primary form when applicable: `[Cn (co-primary), Cn (co-primary), Cn (consultant)]`
- **Routing rationale:** one sentence per convened voice explaining why convened
   - Cn — [why this voice]
   - Cn — [why this voice]
   - Cn — [why this voice]
- **Voices considered, not convened:** [Cn — reason; Cn — reason]
   - Include voices that scored above zero on Layer C but below threshold or above the size cap. Empty list is allowed and stated explicitly: *"None — Layer C only surfaced the convened voices."*
- **Pre-check status:** see CCR below
```

### Field discipline

- **Question type** is exactly one of the five canonical types from Layer B. If genuinely multi-type, pick the more specific anchor (per `routing-rubric.md`) and note the secondary in routing rationale.
- **Voices convened** uses C-number notation (C1, C2, etc.). Tag each voice as `(primary)`, `(co-primary)`, or `(consultant)`.
- **Routing rationale** is one sentence per voice. Not three; not zero. Sentences explain *the routing decision*, not the voice's substantive position (substance comes in the voice's turn).
- **Voices considered, not convened** is the operator's debugging surface. Not optional. State *"None"* if there are none, but always include the field. Reasons can be: *"scored below threshold"*, *"capped at default size of 3"*, *"voluntarily recused"*, *"consulted by reference instead — see citation in primary's response"*.
- **Pre-check status** is a one-line pointer to the CCR that follows immediately. *"See CCR below."* — do not duplicate CCR content in the Convening Block.

---

## CCR (Cross-Cutting Receipt) — emitted immediately after the Convening Block

The CCR addresses each of the six concerns in fixed order. Each concern gets three fields: Touched / Owner status / Pre-check note.

```markdown
## Cross-Cutting Receipt (CCR)

| # | Concern | Touched | Owner status | Pre-check note |
|---|---|---|---|---|
| 1 | Security & blast radius | [Yes / No] | [convened / handled-by-reference / deferred] | [one sentence framing how this concern applies, or "n/a" if Not Touched] |
| 2 | Observability hooks | [Yes / No] | [convened / handled-by-reference / deferred] | [one sentence] |
| 3 | Token economy & cost | [Yes / No] | [convened / handled-by-reference / deferred — note joint ownership C2/C4/C6] | [one sentence] |
| 4 | Reliability & failure containment | [Yes / No] | [convened / handled-by-reference / deferred] | [one sentence] |
| 5 | Eval-ability | [Yes / No] | [convened / handled-by-reference / deferred] | [one sentence] |
| 6 | HITL & local-first deployment | [Yes / No] | [convened / handled-by-reference / deferred] | [one sentence] |
```

### Discipline

- **Touched** is binary. The orchestrator decides *Touched* if the topic genuinely engages the concern; *Not Touched* if the concern is orthogonal. Err toward Touched when borderline — false-positive Touched is cheap (one-sentence pre-check); false-negative Touched is a real failure (concern silently skipped).
- **Owner status** is exactly one of three values:
   - **convened** — the concern's owner voice is in the convening, will address the concern in their turn.
   - **handled-by-reference** — the owner is not convened; the orchestrator (or a convened voice in their turn) will cite the owner's SKILL.md section to apply the concern. The citation must be specific (`c7-observability/SKILL.md §4.4`, not `per C7's spec`).
   - **deferred** — the concern is Touched but neither convened nor handled-by-reference. Deferral must be justified in the pre-check note (e.g., *"deferred to a later session because the question of measurement applies only after the contract under design is finalized"*).
- **Pre-check note** is one sentence framing how the concern applies to the topic at hand. For Not Touched concerns, write *"n/a"* — not "no security concern" or other prose.
- **Voices addressing Touched concerns:** every convened voice must engage Touched concerns within their domain. Silent skipping is rejected — a consultant who has nothing to add on a Touched concern in their domain must say so explicitly with rationale (e.g., *"on observability: no incremental observation hook beyond what C7's pre-check note already flagged"*).

### Spot audit (every fifth session, or operator-tagged)

When a spot audit is invoked, ONE Touched concern in the CCR must be expanded with concrete artifact-level evidence rather than a one-sentence note. The audit replaces the *Pre-check note* cell for the audited concern with a multi-sentence response that names a specific artifact (e.g., a span attribute schema, a gate predicate, a ledger entry shape) the topic at hand creates or modifies. This combats CCR ritualization.

---

## TENSION block — emitted at the end of the response (Layer 1, default surfacing)

Whenever convened voices disagree, surface the disagreement explicitly. Do not smooth tensions into agreement; do not collapse them into "we'll figure it out later." The TENSION block is the structured record of unresolved disagreement.

```markdown
## TENSION block

### [one-sentence issue]

- **Parties:** [Cn, Cn, …]
- **Issue:** one sentence stating the disagreement
- **Positions:**
   - **Cn:** one paragraph stating this voice's position
   - **Cn:** one paragraph stating this voice's position
- **Stakes:** one paragraph stating what changes if resolved one way vs. the other
- **Status:** [open | escalated to Layer 2 | promoted to Layer 3 (permanent tension — see ledger)]
```

### Discipline

- **One TENSION entry per disagreement.** If three voices disagree on two distinct points, that's two TENSION entries.
- **No T-ID at emission.** The orchestrator emits tension blocks without a T-ID; the spec-writer assigns the T-ID at ingestion. If a TENSION engages a known Layer-3 permanent tension (T-perm-1, T-perm-2, T-perm-3 below), reference that ID — but new tensions surface without an ID.
- **Parties:** must include exactly the voices in dispute. A voice that didn't speak on the issue is not a party.
- **Positions:** one paragraph per party voice. Positions are preserved verbatim from the voice's turn; the orchestrator does not paraphrase.
- **Stakes:** the orchestrator's framing of what the disagreement means downstream. This is the only orchestrator-authored prose in a TENSION entry. Keep it neutral — do not advocate for one side.
- **Status:** default *open* on first surfacing. Promote to *Layer 3 (permanent tension)* only if the tension is structural to the slate (canonical examples: T-perm-1 C4 ↔ C10, T-perm-2 C2 ↔ C3, T-perm-3 C1 ↔ C9 — see Layer-3 list below).
- **Empty TENSION block:** if convened voices reached genuine agreement, omit the TENSION block entirely. Do not write *"No tensions surfaced"* — silence is the signal. (The Convening Block is always present; the TENSION block is conditional.)

### Layer 2 escalation (operator-requested)

When the operator asks for resolution of a surfaced tension:

1. Run a meta-pass convening: the disputing voices return as **co-primaries** and must engage each other directly.
2. Convene one **arbiter voice** — operator-selected, or orchestrator-suggested. Default suggestion: **C8** when an empirical/measurable framing would help; **C11** when the resolution must defer to operational reality.
3. Output: same Convening Block + CCR + TENSION-block-update structure. The TENSION entry's *Status* updates to one of:
   - **Resolved** (with rationale paragraph) — the disagreement is settled within the council's scope.
   - **Tighter framing** — the meta-pass surfaced previously-hidden assumptions; the tension persists but is now articulated more precisely.
   - **Layer 3** — the tension is structural; promote to permanent-tension ledger.

### Layer 3 promotion

When a tension is structural to the slate (cannot be resolved without changing scope), promote to permanent tension. The orchestrator marks the TENSION entry's status as *promoted to Layer 3 (permanent tension — see ledger)* and the spec-writer maintains the ledger. The orchestrator does not own the ledger; it owns the promotion event.

Currently locked Layer-3 tensions (do not relitigate; surface as known permanent when convened voices touch them):

- **T-perm-1: C4 ↔ C10** — capability vs gating. Tunable parameter `per_tool_gate_level × per_mcp_server_trust_tier`. H_T resolution: C-AS-10 §10.3 4-tier blast radius + CP §19.1.1 4-axis floor composition.
- **T-perm-2: C2 ↔ C3** — within-turn vs across-turn (read/write seam between active context and durable state). H_T resolution: IS spec read/write boundaries.
- **T-perm-3: C1 ↔ C9** — control-flow vs reliability. Tunable parameter `topology_fault_handling`. H_T resolution: CP §22 ResumptionKind taxonomy + `engine.replay_disposition`.

When a topic engages one of these, surface the tension as **known permanent** in the TENSION block — operator does not need to be re-asked whether to escalate. Revisiting H_T-side resolutions requires Class 1 fork → ADR back-flow per CLAUDE.md §4.3, not in-session re-litigation.

---

## Output ordering (single response)

For one orchestrator response, the ordering is fixed:

1. Convening Block
2. CCR
3. Voice contributions in order (primary first, then consultants)
4. TENSION block (if any)

Do not interleave voices into the CCR. Do not put TENSION before voices spoke. The order is the contract.

If the operator asks a follow-up question that doesn't trigger re-convening (e.g., a clarification on a point the primary made), the orchestrator can respond without a fresh Convening Block — but if any new voice is brought in or the question shifts to a new topic, emit a new Convening Block + CCR for the new turn.
