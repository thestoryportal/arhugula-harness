# Test prompts — Spec-Writer (session 16)

These eight prompts exercise the spec-writer's runtime obligations: per-session ingestion, the three pipeline stages (design doc → PRD → final spec), the cross-voice consistency check (phase-2 inherited obligation), a living-document update, an anti-trigger negative case, and an edge case (malformed envelope handling). Each is paired with the s3-derived quality criteria the spec-writer's response must satisfy.

The eval intent: verify the spec-writer (a) triggers on spec-formalization requests and not on convening or voice-substance requests, (b) ingests the orchestrator envelope verbatim and synthesizes Layer C with attribution and asymmetry preserved, (c) assigns traceability anchors (D-IDs, T-IDs, CCR-IDs) per s3 §3, (d) applies per-stage tension treatment per s3 §6, (e) runs the cross-voice consistency check on integrated content per s14 §"Residual concerns" (b), (f) produces transition delta reports at stage boundaries, (g) does not invent voice content during selective convening per s3 §5.

---

## Eval 1 — per-session-ingestion-c5-c9-validator-fail

**Prompt:**
> I just ran the orchestrator on the validator-fail-classification question. Here's the output. Write it up as a spec section for s8.
>
> ## Convening Block
> - **Question type:** contract
> - **Voices convened:** C5 (primary), C9 (consultant)
> - **Routing rationale:**
>   - C5 — owns the validator gate contract and the fail classification taxonomy
>   - C9 — owns retry posture; consultant on transient-vs-permanent split
> - **Voices considered, not convened:** C7 — handled-by-reference; observability of fail events lives in s10's catalog. C1 — Layer C scored below threshold (Reflexion topology not in scope here).
> - **Pre-check status:** see CCR below
>
> ## Cross-Cutting Receipt (CCR)
> | # | Concern | Touched | Owner status | Pre-check note |
> |---|---|---|---|---|
> | 1 | Security & blast radius | No | n/a | n/a |
> | 2 | Observability hooks | Yes | handled-by-reference | C7 owns fail-event span attributes; cite s10 §4.1 catalog. |
> | 3 | Token economy & cost | No | n/a | n/a |
> | 4 | Reliability & failure containment | Yes | convened | C9 anchors retry posture for transient class; permanent class exits the loop. |
> | 5 | Eval-ability | No | n/a | n/a |
> | 6 | HITL & local-first deployment | No | n/a | n/a |
>
> ## C5 (primary)
> The fail classification has four classes: transient, permanent, Reflexion-recoverable, unknown-defer. Transient and permanent are the load-bearing axes; Reflexion-recoverable exists to give the in-loop retry path a visible signal that the validator is requesting a re-attempt with verbal feedback rather than a hard exit; unknown-defer routes through tight-budget transient retry to permanent-fail-exit if the deferral does not resolve. Every fail event carries a `validator_fail_class` attribute with one of these four values plus a `cause_attribution` annotation per s12 §7.5.
>
> ## C9 (consultant — concur with refinement)
> Concur on the four-class taxonomy. Refinement: the transient class composes with the breaker subscription policy — when a per-tool breaker is in `tool-tripped` state, transient-class fails on that tool route to fallback per the breaker's subscription kind rather than being retried at the validator gate.

**What it exercises:** Per-session ingestion. Verbatim Layer B (Convening Block + CCR), synthesized Layer C (C5 anchor + C9 consultant refinement), no TENSION block. Tests CCR-ID assignment, D-ID assignment for the four-class commitment and the breaker-composition refinement, section metadata header, voice asymmetry preservation (C5 anchors load-bearing; C9 annotates as consultant), voice-output shape preference (C5 hybrid leaning structured — fail-class taxonomy as a table is appropriate).

**Expected output:** Spec section with metadata header (anchor C5, consulted C9, Convening Block ID, CCR-ID assigned). Convening Block + CCR ingested verbatim. Synthesis: C5's four-class taxonomy as a table or numbered list (structured for the taxonomy commitment, prose for rationale); D-IDs at the taxonomy commitment and the breaker-composition refinement. C9's contribution clearly annotated as consultant refinement, not promoted to primary anchoring. Light consistency report appended (CCR ↔ commitment alignment lint only). No TENSION block in output (none in input — silence is the signal, not "no tensions surfaced" placeholder).

---

## Eval 2 — stage-1-design-doc-assembly

**Prompt:**
> Phase 1 is closed. I need you to assemble the Stage 1 design doc — `council-design-doc-v1.md` — voice-by-voice from s2 through s14, plus the utility specs and the three living documents. Use the standard format. Surface any cross-voice cross-references that need to be made explicit.

**What it exercises:** Stage 1 integration pass. Voice-by-voice organization across the eleven voice specs. Cross-references using D-IDs. TENSION blocks inline as sidebars. Permanent tensions get "see ledger T-perm-N" footers. No new content (transformation only, not new commitments). Living-document summary sections at the end.

**Expected output:** A Stage 1 design doc following the template in `references/stage-templates.md` §"Stage 1 — Design doc". Eleven voice sections (C1–C11). Each section aggregates that voice's commitments by D-ID, names cross-references to other voices' sections, includes section metadata headers from original sessions. TENSION blocks inline as sidebars. Permanent tension ledger summary, decision index summary, voice identity manifest summary at the end. **Critical:** no new commitments invented; if a transformation surfaces a needed decision the council didn't anchor, it goes in a transition delta report, not silently into the design doc. Spec-writer verifies this self-discipline: the doc is a *transformation* of existing artifacts, not new content.

(Note: this eval cannot fully run end-to-end without all eleven voice specs in context. The eval verifies the spec-writer (a) classifies the request as Stage 1 integration, (b) reads the right inputs from project KB, (c) follows the template structure, (d) preserves D-IDs and cross-references, (e) does not invent commitments. A full reconstruction of `council-design-doc-v1.md` is out of scope for one session-16 eval; we verify the spec-writer's *approach* against the template, not the full assembled artifact.)

---

## Eval 3 — stage-2-prd-synthesis

**Prompt:**
> Take the design doc and synthesize the PRD — `council-prd-v1.md`. Reorganize voice-anchored content into capability-anchored content. The capability cuts I'm thinking are: failure recovery, validation pipeline, observability, action safety, model strategy, tool surface, operator experience, eval methodology, state and persistence, context engineering. If you find a capability cut that's missing or that the design doc doesn't cleanly support, flag it in a transition delta report.

**What it exercises:** Stage 1→2 PRD synthesis. Capability-anchored reorganization of voice-anchored content. Transition delta report production for items that don't transform cleanly. "Open Decisions" sections per capability for Layer-1 tensions; "Permanent tensions" appendix for Layer-3. D-ID survival across the transition. Section metadata headers carrying "Contributing voices" sidebars.

**Expected output:** A Stage 2 PRD following the template in `references/stage-templates.md` §"Stage 2 — PRD". Each capability section names contributing voices. Each requirement under a capability carries a D-ID. "Open Decisions" section per capability listing Layer-1 TENSIONs that affect that capability. "Permanent tensions" appendix listing T-perm-1, T-perm-2, T-perm-3. **Plus a transition delta report** flagging: decisions reorganized (most), decisions transformed (with rationale), decisions dropped (if any), capability gaps (if any), recommended targeted convenings. The delta report is the operator's gating surface — it must surface real findings, not be a placeholder.

---

## Eval 4 — stage-3-final-spec-with-permanent-tension-promotion

**Prompt:**
> Promote the PRD to final specification. Specifically I want you to encode the three permanent tensions (T-perm-1, T-perm-2, T-perm-3) as tunable parameters with documented tradeoff space per s3 §6.3. For T-perm-1 the parameter is `per_tool_gate_level × per_mcp_server_trust_tier`; for T-perm-3 it's `topology_fault_handling`; T-perm-2 doesn't have a locked parameter name yet — propose one and document the tradeoff space. If any of the permanent tensions resists clean parameterization, put it in the "Acknowledged structural tensions" section and explain why.

**What it exercises:** Stage 2→3 final-spec promotion. Permanent tension encoding as tunable parameters per s3 §6.3. The novel mechanism that distinguishes Stage 3 from Stage 2. Acknowledged structural tensions for unparameterizable cases. Spec-writer's reasoning visibility when proposing a parameter name (T-perm-2's parameter is not pre-locked — operator hasn't fixed it; the spec-writer must propose with rationale, not invent silently).

**Expected output:** A Stage 3 final spec following the template in `references/stage-templates.md` §"Stage 3 — Final specification". Each permanent tension encoded:
- T-perm-1 → `per_tool_gate_level × per_mcp_server_trust_tier` with tradeoff-space documented (permissive endpoint = full C4 capability, strict endpoint = full C10 gating, balanced default).
- T-perm-3 → `topology_fault_handling` with tradeoff-space documented (where the C1↔C9 control-flow vs. reliability balance lands).
- T-perm-2 → proposed parameter name with rationale (e.g., `state_sync_seam` or `context_durability_boundary`) and tradeoff-space documented (C2 within-turn vs. C3 across-turn).
- Any tension that resists parameterization (the spec-writer's judgment) goes in the "Acknowledged structural tensions" section with explanation.

**Critical:** the spec-writer does not unilaterally lock T-perm-2's parameter name. The proposal is *proposing*, not *decided* — the parameter name and tradeoff-space proposal go into the spec with [MODERATE] *proposing* status; operator confirmation locks it.

---

## Eval 5 — cross-voice-consistency-check-on-integrated-content

**Prompt:**
> I want you to run the cross-voice consistency check across all eleven voice specs s4–s14 plus the utility specs. The s15 prep reconciliation already ran the first pass — your check is the second pass. Look for: retroactive interactions the first pass missed, CCR ↔ commitment divergences, TENSION ↔ ledger duplicates or alignment issues, and decision-claim vocabulary breaches. Surface findings as a consistency report.

**What it exercises:** The phase-2 inherited obligation. All four parts of the check. Awareness of the first pass (s15 prep reconciliation) so as not to duplicate findings. The consistency report template. The discipline of *flagging*, not *resolving* — findings go to the operator with reconciliation candidates, not silent merges.

**Expected output:** A consistency report per the template in `references/consistency-check.md` §"Consistency report template". Three sections:
- *Found and applied* — likely empty or minimal (mechanical reconciliations only).
- *Found and flagged* — at least one finding per the four check parts where applicable, OR a clear statement that the first pass covered everything in that part. Each finding has the required fields: type, source, issue, reconciliation candidates, recommendation with confidence tag, status *proposing*.
- *No findings* — explicit per-part statement when a part ran cleanly. Silence is not the same as "checked and found nothing."

**Critical:** the report must cite s15-phase2-prep-reconciliation.md for first-pass items rather than re-flagging them. The check is *additive* to the first pass.

---

## Eval 6 — living-document-update-tension-ledger

**Prompt:**
> The orchestrator just surfaced a new tension between C7 and C8 on whether eval traces should re-use the same span attributes as runtime traces or have a separate eval-trace namespace. The orchestrator emitted this as a Layer-1 tension; status `open`. Add it to the tension ledger.

**What it exercises:** Living-document update. T-ID assignment for a new Layer-1 tension. Ledger entry shape. Awareness of the ledger as canonical-source (not derivable from anywhere else, unlike the decision index and voice manifest).

**Expected output:** A new ledger entry in `council-tension-ledger.md` under Active tensions. Entry has: T-ID (newly assigned, sequential), parties (C7, C8), issue (one-sentence framing), originating session, last touched, status (Active). The entry is added to the ledger; it is not invented. The spec-writer asks the operator to confirm the orchestrator output was attached or pasted — if the orchestrator output is not visible in the prompt, the spec-writer asks for it before assigning a T-ID. (In this prompt the operator stated the parties and issue; the spec-writer can proceed if the issue summary is sufficient, but should ask if positions and stakes are needed for the ledger entry.)

**Optional:** the spec-writer notes that this new T-014 (or whatever the next sequential T-ID is) does **not** match the locked Layer-3 permanent tensions (T-perm-1/2/3), so it stays Active rather than being immediately promoted. If the spec-writer can detect that the C7↔C8 boundary issue was previously flagged in the s10 §4.4 / s11 §7.1 boundary discussion (per the routing-rubric / voice-roster), it surfaces the prior history as context for the operator's judgment about whether to merge with an existing entry.

---

## Eval 7 — anti-trigger-convene-voices

**Prompt:**
> I'm trying to figure out how the harness should handle parallel sub-agents that all hit a rate limit at once. Convene the council on this.

**What it exercises:** Anti-trigger case. The operator is asking for a *new convening* — that's the orchestrator's job, not the spec-writer's. The spec-writer should NOT activate; routing should go to `council-orchestrator`.

**Expected output:** Spec-writer does NOT trigger. Either (a) the orchestrator skill triggers and produces the convening, or (b) Claude routes the request to the orchestrator with a brief note. The spec-writer's description's anti-trigger discipline ("Do NOT use when the operator is asking voices to convene") should make this routing clean.

If the spec-writer triggers anyway, that's a description-tuning failure — the description must be sharper on the orchestrator vs. spec-writer boundary.

---

## Eval 8 — malformed-envelope-handling

**Prompt:**
> Here's some council output. Write it up as a spec section for s9.
>
> ## Convening Block
> - **Voices convened:** C9, C6
> - **Routing rationale:** Both seem relevant.
>
> ## C9
> Backoff curves should be exponential with jitter for tool calls and fixed for model calls.
>
> ## C6
> Concur.

**What it exercises:** Malformed envelope handling per `ingestion-contract.md` §"Layer B" lint. The envelope is missing question type, voices considered not convened, pre-check status, and the entire CCR. Routing rationale is one sentence for both voices, not one per voice. C6's contribution is bare "concur" with no rationale (the orchestrator should have re-prompted internally; this output is malformed). Tests the spec-writer's behavior when given an under-formed envelope.

**Expected output:** Spec-writer detects the malformation and surfaces it explicitly. Default behavior: ask the operator to re-run the orchestrator on the topic to get a well-formed envelope. The spec-writer **does not** silently fill in the missing CCR or paraphrase a substantive rationale into C6's bare "concur" — that would be inventing content the council did not produce. If the operator opts to ingest the malformed envelope anyway (operator override), the spec-writer ingests with a flag in the section header noting the malformation: which fields were missing, which voices' contributions lacked substance, what the spec-writer assumed (typically: nothing assumed; gaps preserved as gaps).

---

## Quality criteria — pass conditions

| # | Criterion |
|---|---|
| 1 | **Trigger discipline.** Spec-writer activates on prompts 1, 2, 3, 4, 5, 6, 8; does NOT activate on prompt 7. The boundary against orchestrator (prompt 7) and against single-voice consultations (would be a separate eval if voice skills existed yet) is clean. |
| 2 | **Verbatim-layer integrity.** Convening Block, CCR, and TENSION block (when present) are ingested verbatim. The output's verbatim sections must round-trip the input — same field names, same values, same structure. Paraphrasing the envelope is FM-1 in progress; reject. |
| 3 | **Layer C synthesis discipline.** Voice asymmetry preserved (primary anchors load-bearing prose; consultants annotate; co-primaries jointly anchor). No homogenization into a "council voice". No commitments without an anchor voice. Imperative for commitments; paraphrased-voice for rationale. Each paragraph drawing from voice content carries an attribution signal. |
| 4 | **Traceability anchors assigned.** D-IDs at every commitment in synthesized prose, sequential and global. T-IDs at every TENSION block ingested. CCR-ID at the section's metadata header. Section metadata headers complete (anchor voice, consulted voices, Convening Block ID, CCR-ID, originating session). |
| 5 | **Per-stage tension treatment.** Stage 1: TENSION blocks inline as sidebars; permanent tensions get ledger footers. Stage 2: "Open Decisions" sections per capability + "Permanent tensions" appendix. Stage 3: tunable parameters with documented tradeoff space; "Acknowledged structural tensions" section for unparameterizable. |
| 6 | **Selective-convening discipline (s3 §5).** Spec-writer does not invent absent voices' positions. Two structural exceptions only: CCR handled-by-reference (citation, not paraphrase) and permanent-tension carry-forward (T-ID reference, not re-stated positions). |
| 7 | **Cross-voice consistency check (phase-2 inherited).** Light check on per-session ingestion (CCR ↔ commitment alignment). Full four-part check on integrated ingestion (Stage 1/2/3, multi-voice integration, operator-requested). Consistency report appended. Findings flagged with reconciliation candidates, not silently merged. First-pass items (per s15 prep) cited rather than re-flagged. |
| 8 | **Transition delta report at stage boundaries.** Stage 1→2 and Stage 2→3 produce delta reports flagging reorganized / transformed / dropped decisions, capability gaps, recommended targeted convenings. Operator review of the delta gates the transition. |
| 9 | **Spec-writer is not a voice.** No substantive opinions on harness design appear in the spec-writer's output as the spec-writer's positions. When the spec-writer proposes (T-perm-2 parameter name in eval 4; consistency-check findings in eval 5), the proposal carries [MODERATE] *proposing* status; operator confirmation is what locks it. |
| 10 | **Malformed envelope handling.** Lint detects missing fields (eval 8). Default behavior is to ask the operator to re-run the orchestrator. Override path explicitly flags the malformation in the spec section header. |

---

## Iteration plan

Per `/mnt/skills/examples/skill-creator/SKILL.md` §"Claude.ai-specific instructions": run each test case one at a time (no subagents). For each prompt, read the SKILL.md and follow its instructions to accomplish the task. Skip baseline runs. Save outputs into `/home/claude/s16-spec-writer-workspace/iteration-N/eval-K/`. Review qualitatively against the quality criteria. Iterate until all criteria pass.
