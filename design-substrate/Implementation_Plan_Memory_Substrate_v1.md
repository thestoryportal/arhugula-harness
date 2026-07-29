# Implementation Plan - Memory Substrate v1

## Status

Proposed.

Date: 2026-07-01

Scope: atomic implementation plan for the full memory substrate. This plan is not an MVP. Units are sequenced only to control risk and review size.

Revision: v1 -> v1.1 (`B-86` spec-leg apply pass - NEW U-MEM-26 decomposing the impl leg of `Spec_Memory_Substrate_v1.md` v1.1. Detail at the change-note below.)

Revision date: 2026-07-28

Revision: v1.1 -> v1.2 (`B-92` spec-leg apply pass - NEW U-MEM-27 decomposing the impl leg of `Spec_Memory_Substrate_v1.md` v1.2. Detail at the change-note below.)

Revision date: 2026-07-29

## Change-note (v1.1 -> v1.2)

**Trigger and back-flow authority.** RATIFIED Class 1 fork `.harness/class_1_fork_c_mem_10_cross_family_promotion_eligibility.md` (filed 2026-07-29; register row `B-92`), applied at the spec leg as `Spec_Memory_Substrate_v1.md` v1.2 in this same PR. v1.2 of that spec settles the C-MEM-10 promotion-eligibility question v1.1 carried undischarged - operator-ratified **reading B (flag + gate)** - and adds the C-MEM-03 tri-state `MemoryRecordEnvelope.captured_cross_family` field that makes the gate decidable. This plan delta decomposes the resulting impl leg.

**Revision scope.** ONE new atomic unit, **U-MEM-27**, carrying five coupled parts: the **write side** (the tri-state derivation at the single central capture site), the **read side** (the `cross_family_capture` risk flag as the single gate authority, plus the review-required / never-auto-promotable gate at both promotion entry points), the **two-surface authority model** (a consistency validator rejecting the disagreeing pair at every validating constructor; the **activation boundary** re-deriving the condition from the stored source records and never trusting the candidate's own assertions, failing closed on an unresolvable source; the `PromotionDecisionStore` read widening that re-derivation needs; and the reserved-flag re-derivation that stops caller input asserting the mark), the **durable carrier** (the flag persisted into promotion-written record content, so the artifact review actually reads records why the candidate was gated), and the **witnesses** (hash-inertness, biconditionality, forward-only legacy records including their durable-transition arm, and one per tri-state arm crossed with each derivation input). U-MEM-27 is **not** a conformance-repair unit in U-MEM-26's sense: v1.2 settles a genuinely open contract question and adds a field, so this unit builds a new obligation rather than making an already-mandated one checkable. It is nonetheless narrow - one optional envelope field, one derivation, two gate sites, one content key, and one validator.

**Why the write side is one site and not seven.** The fork's R9 pass corrected an earlier claim that a capture-side provenance field would touch every capture writer; re-grounded at this leg's HEAD `57f840b6` before this unit was authored. All seven `capture_*` methods on `EpisodicMemoryCapture` (`harness-runtime/src/harness_runtime/memory_capture.py:294` / `:337` / `:382` / `:439` / `:487` / `:534` / `:585`; the class at `:241`) already accept `provider: str | None` (`:302` / `:347` / `:396` and siblings) and already pass it to `_capture` (`:329` / `:374` / `:431` / `:479` / `:526` / `:577` / `:623`), which threads it into `_record` (`:649-658`, the argument at `:657`). `_record` (`:1015-1046`) holds the **family-comparison** inputs: the call's raw `provider` (`:1025`) and the record's resolved scope, produced by `_scope_for_record` (`:1048-1086`). It does **not** hold the content-origin input, which lives at `_capture` (`:631`) as the per-method `event_kind` - so the derivation spans those two private methods, origin gating the comparison (see the round-7/round-8 paragraphs below). **No public writer signature changes, and the unit must not propose any** - a seven-signature refactor would repeat exactly the falsehood R9 corrected. One implementation detail is pinned in the unit body because it is real and small: `_scope_for_record` is today called **inline** at the envelope's `scope=` argument (`:1038-1042`), so the resolved scope must be bound to a local before the envelope is constructed for the predicate to read it.

**Why the read side is two sites, and what exactly must reach the four predicates.** Both promotion entry points construct a `PromotionCandidate` and set `review_required` / `auto_promote_allowed` on it, and neither derivation currently receives anything about the source record. On the hint path, `_candidate_from_hint` (`memory_promotion.py:616-655`) holds `record` but passes only `hint` and `resolution` into `_review_required` (`:762-773`) and `_auto_promote_allowed` (`:776-790`). On the tool path, `_propose_promotion` (`memory_tool_executor.py:399-435`) holds `source` and passes it to `_promotion_risk_flags` (`:882-885`) but **not** to `_promotion_review_required` (`:888-894`) or `_promotion_auto_allowed` (`:897-903`), both of which take the policy resolution alone. What must reach those four predicates is **the derived risk-flag set, not the raw provenance value** - the C-MEM-10 single-authority rule (see the Codex round 1 [P2] paragraph below). Each path already has a natural single derivation site: `_risk_flags` on the hint path, `_promotion_risk_flags` on the tool path. This is internal-helper wiring, not a public contract change.

**Dependencies, and one deliberate omission.** `Depends on: U-MEM-01, U-MEM-07, U-MEM-08, U-MEM-09, U-MEM-16, U-MEM-26.` U-MEM-01 declares the envelope the field is added to; U-MEM-07 owns the capture API that derives it; U-MEM-08 owns hint-path candidate extraction and U-MEM-09 the promotion / review-queue decision, which are the two halves of the gate on that path; U-MEM-16 owns the standard-memory-tool executor, the gate's other entry point; U-MEM-26 landed the composed-scope writer repair the derivation compares the dispatch `provider` **against**, so without it the record's `provider_family` is a per-turn raw key and the predicate is meaningless. **U-MEM-25 is deliberately NOT declared**, unlike at U-MEM-26: it is reached transitively through U-MEM-26, which declares it, so the ordering behind the closeout packet this unit must also refresh is already satisfied and a second edge would be redundant. The omission is stated so it reads as a decision rather than an oversight.

**Axis placement.** Information substrate plus runtime plus operational discipline. Information substrate because the field is added to `harness-is`'s `MemoryRecordEnvelope` (`harness-is/src/harness_is/memory_record_envelope.py:126-142`), so IS isolation tests and IS review posture must not be skippable by axis-scoped execution - the same reasoning round 14 applied to U-MEM-26. Runtime because the derivation and both gate sites live under `harness-runtime`. Operational discipline because promotion and review-queue units are placed there (§3 already lists U-MEM-08 and U-MEM-09 under it) and the gate is a review-disposition change. **Control plane is deliberately not claimed**: the gate is unconditional on policy, adds no C-MEM-09 policy decision value, and consults no policy field beyond the resolution already passed in. **Action surface is deliberately not claimed**: the unit defines no telemetry member and no new tool.

**Closeout staleness at v1.2 - annotation half APPLIED HERE, at this spec leg, per the `B-86` precedent.** `.harness/u-mem-25-memory-closeout-evidence.md` scopes itself to spec **v1.1**, and six of its rows grow obligations at v1.2: C-MEM-03 and C-MEM-10 in the C-MEM matrix (the two contracts v1.2 amends) and R-MEM-01, R-MEM-05, R-MEM-09, and R-MEM-14 in the R-MEM matrix (the four requirements §4.1 below maps U-MEM-27 into). `just memory-closeout-check` stays green regardless, because it tests `## C-MEM-NN` and `### R-MEM-NN` heading-derived id coverage and v1.2 adds neither - the identical interim-window shape v1.1's change-note recorded, and the reason the red-gate alternative was DECLINED there applies unchanged (a red `just check` on `main` for the whole interim window blocks every unrelated arc). **The v1.1 precedent split that fix across the two legs, and this delta follows it exactly.** The honest-annotation half is applied **in this same PR**: `PENDING - U-MEM-27` markers on all six rows, in the same `**Evidences the v1.1 obligations only.** v1.2 obligations (...): **PENDING - U-MEM-27**.` shape the `B-86` spec leg used for its own six rows, plus a second "Version scoping" window paragraph stated beside the now-closed v1.1 one. The re-open-and-extend half is owed at **U-MEM-27**, as an acceptance criterion with a green re-run in Verification - mirroring how the U-MEM-26 impl leg lifted every one of the six v1.1 pendings and closed window 1. R-MEM-12 is deliberately **not** annotated, for the same reason §4.1 does not extend it: the new field is provenance rather than partition, and this unit adds no scope-enforcement obligation.

**One cite repair inside the packet, disclosed because this delta caused it.** The packet's window-1 paragraph cited two U-MEM-26 acceptance items by plan line (`:901` and `:924`). This delta inserts its change-note above the v1 -> v1.1 block, which shifts every anchor below it, so those two cites broke as a direct consequence of this arc rather than by inheritance. They are repaired **in place** to unit-id-plus-subsection form - the convention the spec's own v1.1 change-note fixed for exactly this drift class - not left stale and not deleted. The pre-existing U-MEM-26 unit body's `harness-runtime` code cites are a different case and are left verbatim (see "Cite hygiene" below): they were already stale before this arc, and rewriting them would be an unrelated edit.

**Back-reference reconciliation inside this file.** §3 axis placement gains U-MEM-27 under information substrate, operational discipline, and runtime; §4 gains six dependency edges (`U-MEM-01`, `U-MEM-07`, `U-MEM-08`, `U-MEM-09`, `U-MEM-16`, `U-MEM-26` -> `U-MEM-27`); §4.1 coverage map extends the R-MEM-01 range and adds U-MEM-27 to R-MEM-05, R-MEM-09, and R-MEM-14 (the last added at round 10: the unit adds the operator review gate and the durable flag explaining why a proposal was held, which is squarely R-MEM-14's "review of pending promotions" obligation); §7 gains a G7 review-boundary row; §9 extends the completion range to U-MEM-27. No other row is touched. R-MEM-12 is deliberately not extended: the field is provenance, not partition, and the unit adds no scope-enforcement obligation.

**Out-of-family Codex round 1 - four findings, all applied, each re-grounded by direct code read before the fix was written.** [P1] **The gate had no durable carrier.** The unit verified the flag only on the in-memory candidate while `_semantic_record_content` (`memory_promotion.py:919-956`), `_procedural_record_content` (`:959-989`), and the promotion `_operation_payload` (`:515-542`) all omit risk flags - so a `PROPOSED` record reached review with no record of why it was held, defeating the auditability C-MEM-10 claims. Fixed by carrying the flags in promotion-written record **content**, with a durable-carrier witness read back from the store plus a mutation probe (drop the content write, the durable witness fails while every in-memory witness still passes). The ledger row was rejected as the carrier because `MemoryOperationPayload` is closed (`memory_operation_ledger.py:167-170`) and a field there is the C-MEM-08 amendment this arc forswears; reusing the free-text `review_reason` key was rejected as too weak to carry a flag set. [P2] **Two gate authorities.** The first draft sent the raw provenance value to all four decision predicates while deriving the flag separately - parallel derivations of one fact, free to diverge, leaving the flag advisory. Fixed to one authority: derive once at the existing flag site, have the predicates consume the flag set, and assert **biconditionality** in both directions. [P2] **`EPISODIC_RUN` identity exception.** The spec draft said `memory_id` derives from tier, kind, and content hash universally; `_memory_id_for` (`memory_capture.py:1100-1109`) hashes the `run_id` alone for that kind at `:1106-1108` - which is exactly what this unit's own multi-writer witness depends on. Qualified in both the C-MEM-03 hash-inert paragraph and the change-note's `(i-content)` rejection, with the hash-inert conclusion left universal because the envelope is an input to neither derivation. [P2] **Legacy records rewritten by redaction.** The absolute no-rewrite claim was false for the transition path: `_transition` (`memory_redaction.py:184-189` / `:201-210` / `:258`) rebuilds and rewrites the envelope, and `canonicalize_memory_store_record` (`memory_store.py:327-337`, `BaseModel` branch at `:392`) calls `model_dump()` with defaults included, so an explicit `unknown` **is** materialized. Resolved by permitting it - the guarantee is reframed as being about provenance **determination**, never about envelope byte-stability - and the legacy witness gains a redaction/tombstone transition arm. Unset-preserving serialization was declined explicitly: it would complicate the settled U-MEM-26 LEGACY-REDACTION path for zero semantic gain.

**Out-of-family Codex round 2 - three findings, all applied, and all three are consequences of the round-1 single-authority fix rather than pre-existing defects.** [P1] **The biconditional bound the two derivation paths, not the candidate value.** Both `PromotionCandidate` and `PromotionDecisionService` are exported (`harness-runtime/src/harness_runtime/__init__.py:106` / `:112`), and the service's activation gate is one test of the candidate's own assertion (`memory_promotion.py:368-371`, `:431-434`), so a hand-built candidate carrying the flag with `auto_promote_allowed=True` reached `ACTIVE` unreviewed while satisfying every word of the round-1 text. Round 2 answered with a validator plus a service refusal; **round 3 found that answer incoherent and it was reconciled rather than extended** - see the round-3 paragraph below for the final shape. What stands from round 2 is the consistency validator and the empirical bypass fact: `model_copy(update=...)` does not re-run after-validators on this project's Pydantic (2.13.4, probed directly: the illegal pair survived the copy) and `candidate.model_copy(...)` is **already** called on this model at `memory_compaction_safety.py:288-292`. [P2] **The flag was both the authority and a caller-writable input.** `_risk_flags` seeds from `set(hint.risk_flags)` (`:677`) and `PromotionCandidateHint.risk_flags` is typed to the flag enum (`:193`), so admitting the new value would let a stored hint assert cross-family provenance about a `false` record and have the gate honour it. The value is now **reserved to the deriving writer**, discarded from caller input and re-derived unconditionally in both directions, with a spoof arm and a suppression arm witnessed separately. The tool path needed no equivalent (`memory_tool_executor.py:882-885` accepts no caller flags) and that asymmetry is recorded rather than smoothed over. [P2] **The live register entry contradicted the corrected plan** - it still instructed the four predicates to receive the source record and omitted the durable carrier; rewritten to match this unit's final shape.

**Out-of-family Codex round 3 - two P1 findings, resolved by ONE altitude correction rather than a third patch layer.** Both landed on round 2's direct-construction hardening and together showed it could not be repaired additively. **[P1-a] The consistency validator cannot close the surface it was given.** A directly constructed candidate can **omit** `cross_family_capture` entirely while asserting `auto_promote_allowed=True` against a source whose envelope reads `true` or `unknown`. That candidate is internally consistent, so the validator (which only detects a *disagreeing pair*) passes it; the reserved-flag rule does not reach it either, since that governs caller-supplied *flags* and there are none. It would activate unreviewed. **[P1-b] The unrepresentability claim contradicted this unit's own witness.** The acceptance criterion said no constructor including a **copied** one could produce the illegal pair, while the verification deliberately produced one via `model_copy` to prove the service refuses it - mutually unsatisfiable, since `model_copy` bypasses validators by design. **The reconciliation, now stated once in C-MEM-10 and mirrored here:** two surfaces with different authority. At **derivation**, unchanged from R1/R2 - derive the mark once, reserve it from caller input, predicates consume the flag set. At **activation**, for a candidate the service did not derive, the carrier is **not trusted at all**: `approve` / `edit_and_approve` re-derive from the stored source records named by `source_memory_refs` and gate on `true` / `unknown` irrespective of the candidate's assertions, failing closed on any unresolvable source. This required grounding a claim before making it: the `PromotionDecisionStore` Protocol (`memory_promotion.py:269-277`) has **no** read method, so the widening is real work - and it appears **nowhere** under `design-substrate/`, so it is an internal seam, not a public contract change; the widened method is satisfied by the existing `MemoryStore.read_record` (`harness-is/src/harness_is/memory_store.py:190-197`) with no new store code. The validator is **demoted** to what Pydantic actually provides - consistency at validating constructors, explicitly not unreachability - and overriding `model_copy` is forbidden rather than merely unmentioned, since it would fight frozen-copy semantics for a guarantee activation already provides. **Why this is not the parallel derivation R1 [P2] forbade:** that defect was two derivations of one fact *at the same surface*; this is one derivation at each of two *trust boundaries*, which is the earliest-gate / authority-mirror discipline. The distinction is stated in the contract itself so the two rules cannot be read as contradicting.

**Out-of-family Codex round 4 - three findings, and its [P1] is the most consequential of the whole leg because the round-3 fix had drifted into the reading the operator FORECLOSED.** [P1] **The activation-boundary criterion implemented reading C.** As round 3 wrote it, a re-derived `true` / `unknown` refused activation *unconditionally* - which contradicts this unit's own eligibility-preserved criterion and silently converts the ratified flag-plus-gate into outright refusal. Grounding showed why the error mattered more than it looked: `operator_approved` is not a separate path but a **disjunct** of the existing gate (`memory_promotion.py:368` / `:431`, parameter at `:361` / `:424`), and it is the **only** route by which a non-auto-promotable candidate reaches `ACTIVE` at all - no production caller sets it today (the tool path at `memory_tool_executor.py:448-460` branches on `auto_promote_allowed` and never passes it), so an unconditional refusal foreclosed the *entire* review path rather than narrowing it. Corrected to the minimal composing form: re-derivation **overrides `auto_promote_allowed` to False** and the pre-existing disjunction decides, so the automatic path is withheld while an operator-approved activation still succeeds. The single eligibility arm became a **pair** - approved activates, unapproved refuses - because the old single arm was satisfiable by a unit with no re-derivation at all and would have been falsified by one that had it. [P2] **The durable proposal was left untrusted.** `propose_for_review` (`:328-352`) is publicly reachable with a hand-built candidate and persisted its flags verbatim, so an omitted or spoofed mark produced a wrong durable review artifact - defeating the very auditability the round-1 carrier fix was added for. Surface 2 now normalizes the reserved flag from the resolved sources before the durable write, both directions, with unresolvable branches carrying the flag per the `unknown` mapping. No new contract obligation: C-MEM-10 surface 2 is written over "a candidate the promotion surface did not itself derive", which covers the persistence path in its own words, so the plan cites it rather than duplicating it. [P2] **The procedural auto-promotion branch was uncovered.** `_auto_promote_allowed` takes a separate branch for `PROCEDURAL_UPDATE` (`:788-790`), so a gate placed only on the semantic return at `:790` would leave cross-family procedural candidates auto-promoting while every mandated witness passed; the vacuity-defeating matrix is duplicated under `PROMOTE_PROCEDURAL` + `AUTOMATIC`, with a note that the tool path's `_promotion_auto_allowed` (`memory_tool_executor.py:897-903`) has no kind branch at all, so the asymmetry is hint-path-specific.

**Out-of-family Codex round 5 - one [P2], the last consistency hole in the durable-provenance story, and it was fixed by GENERALIZING rather than by adding a third patch.** Round 4 normalized the reserved flag on `propose_for_review` only, while the round-1 durable carrier copies `candidate.risk_flags` into record content on **every** path through `_persist_decision` - so an operator-approved `ACTIVE` record, the longest-lived artifact the pipeline produces, would have persisted whatever provenance a hand-built candidate asserted. The fix is stated **once**, as a uniform rule over every durable write taken from an untrusted candidate, and implemented at the **single choke point** (`_persist_decision`, `memory_promotion.py:451-513`) rather than at each caller. Grounding the enumeration corrected the finding's own scope: `_persist_decision` has **four** call sites, not the "remaining two" the finding names - `propose_for_review` (`:340`), `approve` (`:378`), **`deny` (`:402`)**, and `edit_and_approve` (`:437`). `deny` writes a durable `DENIED` record through the same carrier and is precisely the caller a per-method fix would miss; normalizing at the choke point covers all four by construction and any future caller on the same terms. The compaction-disposition writer was checked and is outside the rule - its content carries no risk flags. New witnesses: both directions on the `ACTIVE` write (through `approve` **and** `edit_and_approve`, which can regress independently), plus one on `DENIED`. The omitted-arm `ACTIVE` witness carries a second meaning worth stating: an operator-approved cross-family record remains **auditable as cross-family** downstream, because approval records a decision to accept the provenance, not to forget it.

**Out-of-family Codex round 6 - two applied, one DECLINED with its rationale on the record (the `B-86` one-recorded-decline precedent).** [P2, applied] **The derivation gave a determination to content no dispatch produced.** `compose_for_dispatch` writes the run-start record at `automatic_memory.py:232` and returns the context at `:238`, so that capture precedes any provider call and its provider is a *selection*; a same-family selection would have landed `false`. Grounding widened the fix and produced a **cleaner cut than the event-aware rule the finding proposed**: classifying all seven writers by content shows both run writers carry only run metadata with **no `summary_*` field**, so `capture_run_close` - post-dispatch in timing - describes no provider-produced content either and would have been mis-derived by an event-timing rule. The condition is therefore **content provenance**, stated over the condition rather than over method names, which also covers `harness_rule` summaries and any writer added later; the `EPISODIC_RUN` overwrite witness is restated to expect `unknown` surviving rather than a determination. [P2, applied] **Multi-source aggregation was undefined** - worst-value across cited sources, `false` only when all resolve `false`, with three mixed-source witnesses. Plurality was grounded to the direct-construction surface only (both derivation paths set one ref: `memory_promotion.py:644`, `memory_tool_executor.py:420`), so the rule sits at surface 2 and is not duplicated at derivation. [P2, **DECLINED**] Binding the operator-approval bypass to a *verified* identity or durable approval artifact. The finding is factually correct - the service accepts any `Actor` and a direct integration can self-attest - and it is declined on a threat-model reading, recorded here rather than absorbed: this contract family's trust boundary is content authorship (Memory threat model §Threats, *"treats model-authored and external CLI-authored memory as untrusted"*), not an in-process caller of the harness's own service, and such a caller already holds the authority to write a canonical record directly, so the binding buys nothing against that caller class. It would also import an identity-verification mechanism from the review surface - C-MEM-10 Pipeline step 3 and the OD-axis HITL contracts - into a promotion-provenance delta, while the strongest identity claim anywhere in this family is that operator-direct preferences be *distinguishable* from inferred ones, a labelling obligation rather than an authentication one. Verified before declining: **no C-MEM contract claims actor-identity verification at promotion** (the only `actor` occurrences are C-MEM-08's ledger field and the redaction event's `harness | operator | policy` label). The forward question - whether an approval attestation must be authentic, and what artifact evidences it - is recorded at the spec change-note as review-surface work a future HITL-binding amendment may take up, so it stays visible without being silently absorbed.

**Out-of-family Codex round 7 - two findings, both applied.** [P1] **Two reads where there must be one.** Rounds 3-6 left the unit describing a re-derivation at the activation gate and a normalization at the durable write; since the field is hash-inert a record can be rewritten under the same `memory_id` between them, so `approve` could observe `false` at `memory_promotion.py:368`, admit an activation without `operator_approved`, and then have `_persist_decision` observe `true`, persist the mark, and write `ACTIVE` - a record both marked cross-family-captured and never reviewed, which the C-MEM-10 gate invariant forbids. Replaced with **one re-derivation per service call carried as a frozen snapshot** (the `B-91` idiom): resolve once, build an immutable effective-provenance result plus normalized flag set, thread it through both the gate test and `_persist_decision`, and make the gate a pure projection that performs no lookup. Explicitly not two lookups plus a comparison, which detects the disagreement rather than preventing it. Witnessed with a **mutating** fake store asserting exactly one resolution per call and that the persisted mark equals the first read - a non-mutating consistency test would pass against the defective shape, and the unit says so. [P2] **Content origin conflated with summarization mechanism** - a correction to an earlier draft of this unit's own bullet, not to an external claim. That draft said a `harness_rule` summary is "the harness's text, not a provider's"; grounding the production path shows the runtime computes the stored `response_summary` **from the actual provider response** (`automatic_memory.py:249` / `:269`) while labelling the summarizer `SummarySource.HARNESS_RULE` (`:270`), so the draft's rule would have marked **every production turn capture** `unknown`, including completed same-family dispatches. Restated over **content origin** with `summary_source` explicitly disqualified as the discriminator, the writer keying instead on holding a completed dispatch result, and two new witness cells pinning the production turn path to `false` (same-family) and `true` (cross-family).

**Review-time inventory and the cap on the derivation-mechanics surface (PD-9).** Round 7 is the **third** consecutive correction to the derivation rule's mechanics (R6 event-timing -> content; R7 summarization-mechanism -> content origin), which is the non-convergent-mechanics signature the `B-92` fork documented on its own Q2 comparison and capped under the same discipline. What is **settled at contract altitude** is enumerated at the spec change-note's matching paragraph: tri-state, fail-closed `unknown`, hash-inert, forward-only with no back-filled determination, content-origin keying, single-frozen-snapshot consumption at surface 2, and worst-value aggregation. Residual precision about **which capture call sites can determine content origin** is bounded **by rule rather than by enumeration**, and this unit is where that rule lands: **U-MEM-27 must re-ground every capture call site against its own HEAD before wiring the derivation** - the `B-86` -> U-MEM-26 precedent and the fork's §10 cap - and any call-site-level refinement found there is **impl work**, not a contract amendment, unless it contradicts one of the settled sentences, in which case it back-flows. The call-site sweep was COMPLETED at this leg, all seven methods dispositioned by direct read. (1) **`capture_turn_completion` - DISPATCH-DERIVED.** Its production caller receives `response: Mapping[str, Any]` (`automatic_memory.py:249`) and computes the stored summary from it (`:269`); determination required. (2) **`capture_run_start` - PRE-DISPATCH, `unknown`.** Called from `compose_for_dispatch` at `:232`, before the context returns at `:238`. (3) **`capture_compaction_event` - CANNOT-TELL, therefore `unknown`.** Its compaction-side counterpart `complete_compaction` takes `summary: str` as a **caller-supplied argument** (`memory_compaction_safety.py:168`) with no dispatch result in hand and no provenance marker on the string, which is precisely the "writer cannot tell" case C-MEM-03's rule routes to `unknown`. (4) **`capture_tool_event` - DISPATCH-DERIVED at its sole production caller.** A full-source sweep (`grep -rn 'capture_run_close(\|capture_tool_event(\|capture_provider_route(\|capture_failure_observation(' harness-runtime/src harness-is/src`, run at this leg) finds exactly one call site beyond the definition: `MemoryToolExecutor._write_note` (`memory_tool_executor.py:361`), the model's `memory.write_note` tool. Its content is model-authored note text produced by the in-flight dispatch - `SummaryProvenance(source=SummarySource.MODEL_GENERATED, model=context.model)` at `:366`, `provider=context.provider` at `:369` - so the writer holds both the produced content and the family that produced it; determination required. (5) **`capture_run_close`, `capture_provider_route`, `capture_failure_observation` - NO production caller**, re-verified by the same sweep (the prior branch grounding's carried claim about `capture_run_close` is now re-verified at this leg rather than inherited). The sweep scope is complete by architecture, not by sampling: `EpisodicMemoryCapture` is a `harness-runtime` class, and the lower-level axis packages (`harness-cp/od/as/core/cxa`) cannot import harness-runtime without the carrier-home/axis-isolation violation this workspace forbids, so `harness-runtime/src` + `harness-is/src` is the whole caller universe. (6) **The capture API boundary is uniform across all content-bearing methods** - each receives an already-summarized string, e.g. `capture_tool_event(..., summary_text: str, ...)` (`memory_capture.py:445`) - which is the fact that moved the derivation site to `_capture`/`event_kind` above. The resulting `event_kind` -> origin-disposition map at this HEAD: turn/tool -> determination; run-start/run-close/compaction -> `unknown`; provider-route/failure-observation -> currently unproduced, dispositioned by the content-origin rule if a producer arrives. U-MEM-27 still re-grounds every call site against its own HEAD before wiring (the `B-86` -> U-MEM-26 precedent), and the cap above still governs any NEW call site or refinement found there: impl work unless it contradicts a settled sentence, in which case it back-flows.

**Out-of-family Codex round 8 - two coherence findings, both applied.** [P2] two of this unit's own bullets gave **mutually exclusive** derivation-site instructions (one requiring `_record` "which already holds both inputs", the other requiring `_capture` because content origin is unavailable in `_record`), and the stale direction had propagated to both clearance markers, the register close_out, and root `CLAUDE.md` §2.4 - following it would classify pre-dispatch and lifecycle captures from `provider` alone, violating C-MEM-03. [P2] the C-MEM-10 contract shape declared only `source_refs`, so surface 2's record-lookup and gate-pair obligations referenced **undeclared** fields; `source_memory_refs`, `review_required`, and `auto_promote_allowed` are now declared as the existing reality the implementation model already carries (`memory_promotion.py:217` / `:226` / `:227`), with every preserved-verbatim claim updated to separate the one added capability from the three declarations.

**Out-of-family Codex round 10 - three applied, one answered at property altitude.** [P1] the commit-binding obligation needed its **force** stated (a re-check separable from the write it authorizes is still a TOCTOU window; the store exposes reads and writes separately with locks over individual writes only) and its **scope** justified (activation only, because non-active outcomes are stale-but-gated and self-correct at the next surface-2 invocation). Both are now in the contract; the demanded CAS/lock/transaction apparatus stays **impl discretion**, and this unit's mechanism item gains the requirement that the chosen mechanism make **verification atomic with persistence** on the activation path, with a witness exercising the **between-recheck-and-write** interleaving specifically. [P2] origin is **per-invocation**: `event_kind` is a sound realization only for methods whose every production invocation shares one origin, and `capture_failure_observation` can describe a dispatch that produced output *or* none - so it takes an explicit per-call origin value or records `unknown` for the invocations it cannot distinguish (honestly scoped: that method has **no production caller at HEAD**, so this is rule-precision, not live misclassification). [P2] a content-replacing transition must **reset** the field: `_replacement_content` (`harness-is/src/harness_is/memory_redaction.py:271-296`) substitutes a wholly harness-authored mapping while `_transition`'s `model_copy` preserves the envelope value, so `true`/`false` would survive onto content deriving from no dispatch; reset-to-`unknown` arms added to the transition witness. [P2] **R-MEM-14** gains U-MEM-27 in §4.1 and a `PENDING - U-MEM-27` annotation in the closeout packet, taking the pending set from five rows to **six** and extending this unit's closeout criterion accordingly.

**Review-time inventory and SOUNDNESS EXIT on the activation-race surface (PD-9).** Four rounds have now narrowed one race on the activation surface - R3 established the durable carrier, R7 the single frozen snapshot, R9 the commit-binding property, R10 its atomicity force and the non-active-write disposition - and **each finding was a consequence of the previous fix rather than a defect in the premise**. Across all four, nothing invalidated what the delta actually commits to: the ratified flag-plus-gate reading, the tri-state with fail-closed `unknown`, the two-surface authority model, or the durable carrier. What moved each time was the precision of one property. That is the non-convergent-mechanics signature the `B-92` fork documented on its own Q2 comparison and closed under the same discipline, and this subsection closes on the same terms. **Settled at contract altitude:** the commit-binding property, its force (a verification separable from the persistence it authorizes does not discharge it - conformance is judged on the outcome), the reason it attaches to activation rather than to every durable write (non-active outcomes are stale-but-gated and self-correct at the next surface-2 invocation; only stale-`false`-to-automatic-activation crosses the gate), and the explicit refusal to prescribe machinery. **Routed to the implementation leg by rule:** the mechanism choice (compare-and-set, generation token, lock, transaction), how atomicity is achieved for it, and any interleaving refinement below the property - all of which U-MEM-27 must resolve and **state**, against its own HEAD, exactly as the derivation-mechanics cap already requires for call sites. **The exception that reopens this delta** is unchanged in kind from the fork's own: a finding that invalidates a ratified reading, the gate obligation itself, or the two-surface authority model. A further finding that the property needs a *different mechanism* is not such a finding, and belongs to the leg that builds it.

**Out-of-family Codex round 9 - three findings, all applied.** [P1] the one-read rule did not bind the decision to a source **version**, and grounding showed the race is **LIVE at HEAD** rather than theoretical: the determination-bearing kinds are the JSONL-backed ones (`harness-is/src/harness_is/memory_store.py:143-147`), `write_record` **appends** for them with no dedup, skip, or error (`_append_jsonl`, `:432-436`), `_read_jsonl_record` takes the **last** matching line (`:445-463`, the reassignment at `:460`), and hash-inertness means a differently-marked rewrite keeps the same `content_hash` and therefore the same `memory_id` - so provenance changes silently under a stable identity. `_capture` also writes the record (`memory_capture.py:730`) **before** its ledger append (`:732`), so even a capture reporting `FAILED` on an idempotency conflict has already appended its line. (`EPISODIC_RUN` overwrites rather than appends, but always lands `unknown`, so its overwrite cannot change a gating outcome.) A **commit-binding obligation** is added - no activation commits against a source whose provenance changed after the snapshot; on change the invocation fails or retakes it - with **mechanism left to implementation discretion** and the unit required to **state which it chose and why**. The round-7 mutating-store witness, which had explicitly blessed first-read-wins, is corrected, and a paired commit-binding witness forbids silent auto-activation on a mid-call provenance change. [P2] two bullets gave incompatible derivation flows; one flow is now stated identically on all seven surfaces, with impl discretion narrowed to the private parameter **shape** rather than to where the final value is computed. [P2] the closeout packet's window-1 closure sentence claimed no matrix row carries a `PENDING` marker while five carry `PENDING - U-MEM-27`; qualified to `PENDING - U-MEM-26`.

**Cite hygiene.** Every `file:line` cite in U-MEM-27 and in this change-note was verified by direct read at HEAD `57f840b6`, per the fork §10 cap requiring the spec leg to re-ground all mechanics against its own HEAD. The pre-existing U-MEM-26 unit body's `harness-runtime` cites drifted when U-MEM-26 landed (for example `memory_capture.py:585-591`, `memory_promotion.py:741-753`, `:568-582`); they are historical records of that unit's authoring HEAD, they are **not** rewritten here, and U-MEM-27 does not inherit them.

**Sections preserved verbatim at v1.2.** The Status section (revision lines appended only); the whole `## Change-note (v1 -> v1.1)` block; §1 goal; §2 non-negotiable constraints; §5 unit bodies U-MEM-01 through U-MEM-26; §6 required review gates; §8 risk controls. The reconciliations enumerated above are the only edits to pre-existing text, and each is a range or membership extension - no pre-existing unit body, acceptance criterion, or verification line is rewritten.

## Change-note (v1 -> v1.1)

**Trigger and back-flow authority.** RATIFIED Class 1 fork `.harness/class_1_fork_b86_memory_scope_provider_family_keying.md` (filed 2026-07-28; register row `B-86`), applied at the spec leg as `Spec_Memory_Substrate_v1.md` v1.1 in this same PR. v1.1 of that spec adds the C-MEM-03 `provider_family` value domain, `null` semantics, and run-level derivation rule with its paired writer-side obligation; the C-MEM-13 cross-family withholding invariant; and the C-MEM-14 exposure qualification. This plan delta decomposes the resulting impl leg.

**Revision scope.** ONE new atomic unit, **U-MEM-26**, carrying the C-MEM-13 cross-family withholding guard at the standard-memory-tools context resolution, the `B-89` writer-side repair (the capture path consumes the run's composed record scope instead of constructing its own, which will incidentally close `B-90`'s `tenant` / `workload_class` omission when the unit lands - not before), and their witnesses. U-MEM-26 is a **conformance-repair unit against the already-cleared threat-model invariant** "Retrieval and injection enforce project, workflow, tenant, provider-family, CLI-profile, and visibility scope before ranking." - not new capability. Per the spec v1.1 recording-surface paragraph, the withholding is **recorded** on the C-MEM-19 telemetry surface with a named denial reason; a durable ledger row is owed only where the withholding is realized as a `no_memory_access` transition, and is then dischargeable through the existing `inject` operation kind. U-MEM-26 introduces no C-MEM-08 operation kind. Codex round 4 widened the unit twice, both grounded by direct read before authoring: [P2-a] the writer repair is not capture-only - the promotion record write persists a caller-supplied `suggested_scope` verbatim, so the value domain is enforced at every durable write surface, each named in the acceptance criteria so the impl leg cannot silently cover one; [P2-b] the closeout-refresh criterion now covers the three `R-MEM` rows the same PR marked `PENDING`, not only the three `C-MEM` rows. Codex round 5 then corrected the round-4 wording twice: [P1] the capture-path `null` fallback round 4 proposed was **itself** a scope-isolation defect - a stored `null` is the unpartitioned wildcard matching every requested family under the same asymmetric semantics the spec now documents, so degrading an unknown provider key to `null` would make that record cross-family retrievable, against R-MEM-12; the fallback is removed, and the criterion instead states that the unknown-key case cannot arise at the capture surface once the writer repair lands, since the composed run scope becomes the sole source; [P2] the round-4 acceptance canonicalized a registered raw key while its verification bullet demanded that same case be denied - canonicalization is kept for registered keys (consistent with the provider-to-family authority and with (b1)'s risk-flagging posture) and denial is scoped to unregistered or out-of-domain identifiers, with the verification bullet aligned. Codex round 6 [P2-a] then found the surface inventory still incomplete and it was extended, again by direct read: the compaction-decision write (d) and the native-adapter tool-event write (e) both persist a caller-supplied scope, and **neither is discharged by construction** - at HEAD both have test-only call sites, so no composition root seeds either from the run's composed scope, and the obligation attaches at the write plus at whatever production wiring later appears. A witness is pinned for each.

**Closeout staleness, disclosed (Codex round 1 [P2-c]).** U-MEM-24 verification and U-MEM-25 closeout evidence were certified against the pre-v1.1 contracts, and the closeout checker keys on the spec's `## C-MEM-NN` headings — v1.1 adds no new contract id, so the check still reports ready while covering obligations that have since grown. The fix is taken in the **minimal form**: no dependency-edge or ordering change (the checker is id-coverage-based, not ordering-sensitive, and U-MEM-25's evidence remains valid for U-MEM-01..25). Instead, U-MEM-26 carries an acceptance criterion requiring the U-MEM-25 closeout evidence rows for C-MEM-03, C-MEM-13, and C-MEM-14 to be re-opened and extended for the v1.1 obligations, plus a verification line requiring the closeout check to be re-run green with those refreshed rows. U-MEM-26 therefore cannot land while the closeout evidence still describes only pre-v1.1 obligations.

**The interim window, and the declined alternative (Codex round 2 [P1]).** Round 2 raised the same surface one step further: between this spec leg and U-MEM-26, `just memory-closeout-check` (which `just check` runs) prints `ready: yes` while the v1.1 obligations are un-evidenced, which reads as certification of coverage the packet does not have. Codex proposed making the gate red or pending until U-MEM-26 lands. **That alternative is DECLINED, deliberately and on the record.** A gate that is red on `main` for the whole interim window violates the workspace's main-always-green CI discipline and would block every unrelated arc that runs `just check` — a disproportionate cost for a documentation-scoping problem, and one that would pressure the next arc to bypass the gate rather than fix the evidence. The binary gate certifies a narrow property — that every contract id derived from the spec's `## C-MEM-NN` headings has an evidence row — and that property is genuinely still true at v1.1, which adds no id. **The applied fix is the honest-annotation half instead:** the C-MEM-03, C-MEM-13, and C-MEM-14 rows of `.harness/u-mem-25-memory-closeout-evidence.md` now state that they evidence the **v1** obligations only and carry a visible `PENDING — U-MEM-26` marker naming the v1.1 obligation each row does not yet cover, with a matching version-scoping paragraph under that packet's "Remaining Gates And Blockers". The version-scoped truth therefore lives in the evidence artifact and in this plan note, where a reader looks, rather than in a binary that cannot express it; and U-MEM-26's acceptance criteria already force the refresh plus a green re-run before the unit closes.

**Back-reference reconciliation inside this file.** §3 axis placement gains U-MEM-26 under control plane, runtime, operational discipline, and information substrate; §4 gains six dependency edges (`U-MEM-07`, `U-MEM-09`, `U-MEM-14`, `U-MEM-16`, `U-MEM-22`, `U-MEM-25` -> `U-MEM-26`); §4.1 coverage map extends the R-MEM-01 range and adds U-MEM-26 to R-MEM-09 and R-MEM-12; §7 gains a G6 review-boundary row; §9 extends the completion range to U-MEM-26. No other row is touched.

**Dependency and axis widening (Codex round 6 [P2-b]).** The unit as first written depended only on U-MEM-07 / U-MEM-14 / U-MEM-16, which under-declared two real couplings the write-boundary and recording-surface criteria introduced: promotion-record persistence is **U-MEM-09**'s (the promotion and review-queue unit that owns the canonical semantic/procedural write), and the C-MEM-19 telemetry surface the withholding is recorded on is **U-MEM-22**'s. Both are added to `Depends on:` and to the §4 DAG, and the unit's axis line gains **operational discipline** (the axis §3 already places both U-MEM-09 and U-MEM-22 under). Round 14 added **information substrate** as a fourth axis for the same reason - the unit changes `harness-is`'s retrieval request and derived-index query models and all three scope predicates, so IS isolation tests and IS review posture must not be skippable by axis-scoped execution. Action surface is deliberately NOT added: U-MEM-26 consumes the existing C-MEM-19 vocabulary as attribute values and defines no new telemetry member, so it is a telemetry *emitter*, not an owner of the namespace.

**Dependency completion (Codex round 8 [P2-a]).** **U-MEM-25** is added as a sixth dependency. It is the transitive-ordering edge the unit was missing: U-MEM-25 depends on U-MEM-24, which depends on U-MEM-20..23, so declaring it orders U-MEM-26 behind the compaction-safety writer that write-boundary surface (d) exercises, and behind the closeout packet the unit is required to rewrite. Note this **supersedes the round-1 [P2-c] paragraph's "no dependency-edge or ordering change" framing** on one point: that statement was true of the closeout-staleness fix considered alone (the checker is id-coverage-based, so nothing about *it* demanded an edge), and it remains the reason the gate was not reddened - but rounds 6 and 8 added edges for independent reasons (real unit couplings, and this transitive ordering), so the plan's final shape does carry them.

**`B-90` layer-independent witnesses (Codex round 8 [P2-b]).** `B-90`'s own close-out step (3) requires the tenant-denial witness to be asserted at each of the three enforcement predicates separately, because a single composite retrieval witness passes *over* the other two layers - which is how the omission survived in the first place. U-MEM-26 incorporates the `B-90` repair, so it inherits that obligation: three verification bullets, one per predicate, each cited. The unit cannot close `B-90` while any one layer still admits a cross-tenant record.

**The redaction exception (Codex round 9 [P2-a]).** Round 8's inventory still read as "every durable write", which would have swept in the redaction / tombstone / retention-expiry transition (`memory_redaction.py` `_transition` `:168-263`, durably rewriting at `:258`). That reading is a **compliance hazard**: a central write validator applied there would make a pre-v1.1 record carrying a raw provider key impossible to redact - an un-redactable legacy sensitive record - while a silent exemption would leave an out-of-domain value undocumented. Both are avoided by scoping the obligation precisely: it binds **scope-authoring** writes, and the transition is named as surface (f) with an explicit LEGACY-REDACTION rule to preserve the record's existing scope verbatim. Grounding shows this pins current behaviour rather than changing it - the `model_copy` update set at `:201-210` carries only `updated_at`, `content_hash`, and `redaction_state`, so scope already survives untouched. Nothing is laundered: a redaction cannot create a record that did not exist, nor introduce a value the record did not already carry. A compliance witness is pinned.

**Register-status labels are historical-at-filing (Codex round 9 [P2-b]).** The spec change-note and the spec clearance marker both record `B-86` as `design_substrate_gated`, which was true at the fork filing and became stale within this same PR when the spec leg cleared the design gate and the row transited to `open`. Both sites are now labelled explicitly as historical-at-filing values with a pointer to `.harness/forward-register.yaml` for live status - the marker especially, since it is the version-binding source later sessions consume.

**Two wording corrections (Codex round 10).** [P2-a] The spec's asymmetry rationale had the direction **inverted**: it read that a request declining to name a partition is "narrower than, never broader than, a partitioned record". The truth is the opposite and is the whole reason the policy predicate rejects it - omitting the family constraint is a request for **broader** reach, since an unconstrained request would span every partition. Corrected at the C-MEM-03 subsection and at change-note (b); the C-MEM-03 invariant bullet ("a `null` requested value does not widen access past a family-scoped record") was already stated in the correct direction and is unchanged. [P2-b] Several sites said `B-90` "is closed incidentally" by the writer repair, which reads as already-resolved. Every such site under this branch's changed files is now future/conditional - the repair **will** close it when U-MEM-26 lands; until then the cross-tenant exposure stands and the register correctly carries `B-90` as `open`. Fork-doc phrasing is left as authored: it is a historical filing record, not a live claim.

**Two impl-ordering constraints (Codex round 11).** Both were found by asking *where* in each call path a validator would actually have to sit, and both were confirmed by direct read. [P2-a] At the promotion surface, a validator placed at the write call is provably too late: `_candidate_from_hint` derives risk flags and the candidate identity from the **raw** suggested scope first, so key-vs-value-equivalent inputs would still receive different `candidate_id`s and a registered alias of the record's own family would still be falsely flagged `CROSS_SCOPE`, even where the persisted record ends up canonical. The criterion now pins canonicalization **ahead of** those two derivations, and the witnesses assert the two derived outputs rather than only the persisted record. [P2-b] At the native tool-event surface the operation-ledger append precedes the record write, so a denial at the write would strand a durable `native_adapter_call` entry referencing a record that never existed. The criterion now requires validation before the append, and the denial witness asserts both stores are unchanged. Neither constraint changes a contract - each pins *where* in an existing call path the already-committed obligation must sit, which is exactly the kind of thing a plan unit is for.

**Contract reopening (Codex round 12).** Round 11 was labelled terminal on the exit-on-soundness reading that the spec text had been quiet since round 10. **That label was premature and is corrected here:** round 12 produced two *contract-level* findings, which is precisely the condition under which the leg correctly reopens. Both landed in the spec (see its own change-note) and ripple here. [P2-a] The value domain was **one-sided**: it bound authored record scopes but not request scopes, and since the scope predicates match raw strings, a crafted raw-key request reached a legacy raw-key record - collapsing both the "not retrievable under a family-scoped request" guarantee and the permanent-residual claim that rests on it. U-MEM-26 gains a request-boundary acceptance criterion with the grounded request models and construction sites named, plus witnesses at **both** read layers (retriever and derived index), since a single-layer negative witness would pass over the other. [P2-b] The derivation rule over-claimed the composed run scope as the authority for *every* record a run writes; promotion, compaction disposition, and native-adapter tool events legitimately author their own scopes - which the write-boundary criterion already assumed, so the spec sentence and the plan were quietly inconsistent until now. The spec is narrowed to automatically-captured records and the two surfaces now agree.

**Two coverage extensions, and the cap (Codex round 13).** Contract text is untouched this round, which is consistent with soundness; both findings are plan-tier. [P2-a] The round-12 request-boundary fix bound the two *request models*, but several **direct readers** reach a scope predicate without constructing either - the native backend's retrieval-allowed path and the standard-tool-executor's by-reference paths - so the crafted-scope bypass survived it. Those paths are now named in the criterion with the same canonicalize/reject split, with a negative witness each. [P2-b] `null`-request denial was only ever enforced at the **policy** predicate: the retriever and index predicates both admit family-scoped entries for a `null` request, and grounding showed the public `DerivedRetrievalIndexStore.retrieve` reaches the index predicate through `_filter_candidates` with **no policy leg at all**, so that path returns family-scoped metadata and refs - and does its filtering before `_order_candidates`, which is exactly the "before ranking" position `:481` binds. Each predicate is now fixed on its own terms with a separate witness, mirroring the round-8 three-layer tenant pattern.

**And the cap.** This is the thirteenth review round, and rounds 4, 6, 12, and 13 each found a surface the previous enumeration had missed - the signature of a non-convergent enumeration, where each round returns a narrower instance of an already-characterized class rather than a new class. Continuing to iterate would trade real returns for the appearance of thoroughness. The leg therefore **caps here**: one further round runs as a witness, and any further *plan-tier enumeration* finding is absorbed into the new "the enumerated inventory is review-time, not proven complete" implementation note rather than iterated into the list - the note already binds every surface by rule and obliges the impl leg to re-ground the whole inventory at its own HEAD. A **contract-level** defect would still reopen the leg, as round 12's did.

**Round 14 - the witness round, and the leg exit.** Two findings, neither of the capped enumeration class. [P2-a] **Axis classification.** U-MEM-26 changes `harness-is`'s retrieval-request and derived-index-query models and all three scope predicates, so **information substrate** is added to the unit's axis line and to §3 - without it, axis-scoped execution could skip the IS isolation tests and the IS review posture for a unit that edits IS surfaces. [P2-b] **Register next-executor instruction.** The `B-86` / `B-89` / `B-90` close-outs still led with the *pre-ratification* questions ("decide the keying", "decide the posture", "do not land ahead of the spec leg"), which v1.1 has answered, and repeated as present tense that the value and `null` semantics are undocumented, which v1.1 has documented. Each row now leads with a `LIVE NEXT STEP` naming the remaining implementation work, with the original text retained verbatim below a `HISTORY (pre-ratification)` label - provenance kept, instruction corrected. Text-only; no status changed, so the register's identity digest is untouched.

**The leg exits here, on soundness.** The exit is argued, not merely declared: the **contract** text has been quiet since round 12, whose reopening was itself resolved within that round (request-boundary binding + the narrowed derivation claim), so the artifact's committed surface has been stable across two subsequent review rounds. Rounds 13 and 14 produced only coverage, classification, and bookkeeping findings - none altered a contract, and none changed what the impl leg must build. Residual **enumeration** risk is governed by rule rather than by listing, at the "review-time inventory" implementation note, which obliges the impl leg to re-ground the whole inventory at its own HEAD and binds any surface found beyond the list. What remains is implementation, not specification. A contract-level defect surfacing later would reopen the leg on the same terms round 12 did.

**Sections preserved verbatim at v1.1.** The Status section (revision lines appended only); §1 goal; §2 non-negotiable constraints; §5 unit bodies U-MEM-01 through U-MEM-25; §6 required review gates; §8 risk controls. The reconciliations enumerated above are the only edits to pre-existing text, and each is a range or membership extension - no pre-existing unit body, acceptance criterion, or verification line is rewritten.

## 1. Goal

Implement the complete provider-neutral memory layer specified by `Spec_Memory_Substrate_v1.md` and required by PRD v1.2 R-MEM.

The implementation is complete only when the harness can:

- Capture episodic and durable memory automatically.
- Promote semantic and procedural memory under explicit policy.
- Retrieve, rank, and assemble bounded memory packets.
- Expose memory through native Anthropic memory, provider-neutral memory tools, and prompt-extension fallback.
- Resolve memory behavior for generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom CLI profiles.
- Preserve engine-class durability behavior.
- Audit capture, retrieval, promotion, injection, denial, redaction, and compaction decisions.

## 2. Non-negotiable constraints

- No limited MVP.
- No provider-owned canonical memory.
- No silent semantic or procedural promotion.
- No injection without policy and ledger decision.
- No unbounded prompt memory dump.
- No derived index as source of truth.
- No external CLI memory mutation without an explicit ledgered import/export policy.
- No runtime behavior change for no-memory deployments; default policy is memory-disabled until explicitly enabled.
- No completion claim until every `C-MEM-*` contract is implemented and verified; blockers are allowed only for registered external dependencies with deterministic absence probes.

Existing deployed external CLI routing in `thestoryportal/arhugula` is an integration boundary, not new scope. The memory layer must reuse and extend:

- `harness_runtime.types`: external CLI provider kind/config/default provider ordering.
- `harness_runtime.lifecycle.external_cli_provider`: Claude Code, Codex, Antigravity, legacy Gemini, and generic-command subprocess adapters.
- `harness_runtime.lifecycle.providers`: enabled-provider ordering, provider construction, optional degradation, and API/SDK fallback.
- `harness_runtime.lifecycle.llm_dispatch`: external CLI dispatch and `external_cli.*` telemetry.
- `harness.toml.example`, `tools/external_cli_provider_config.py`, `just external-cli-config`, examples, docs, and tests that prove provider precedence.

Repository sequencing note: at filing head `cc612ec8`, this repository's `main` branch does not yet contain the deployed external CLI routing surface. G1 foundational memory schemas, store, policy, and ledger work can proceed without it, but CLI-route-specific acceptance in U-MEM-05, U-MEM-12, U-MEM-14, U-MEM-18, and U-MEM-24 is port-gated. Those slices must run after the external CLI routing port is landed, or on an implementation branch that carries that port and proves provider ordering, optional degradation, and dispatch telemetry are preserved. No affected unit may claim full CLI-profile completion against a branch that lacks the routing port.

## 3. Axis placement

| Axis | Units |
|---|---|
| Information substrate | U-MEM-01, U-MEM-02, U-MEM-03, U-MEM-04, U-MEM-05, U-MEM-06, U-MEM-10, U-MEM-11, U-MEM-21, U-MEM-24, U-MEM-26, U-MEM-27 |
| Action surface | U-MEM-12, U-MEM-13, U-MEM-22, U-MEM-24 |
| Control plane | U-MEM-11, U-MEM-12, U-MEM-18, U-MEM-19, U-MEM-24, U-MEM-26 |
| Operational discipline | U-MEM-04, U-MEM-08, U-MEM-09, U-MEM-20, U-MEM-21, U-MEM-22, U-MEM-24, U-MEM-26, U-MEM-27 |
| Runtime | U-MEM-07, U-MEM-08, U-MEM-09, U-MEM-14, U-MEM-15, U-MEM-16, U-MEM-17, U-MEM-18, U-MEM-19, U-MEM-20, U-MEM-22, U-MEM-23, U-MEM-24, U-MEM-26, U-MEM-27 |
| Cross-axis closeout | U-MEM-24, U-MEM-25 |

## 4. Dependency map

```text
U-MEM-01 -> U-MEM-02
U-MEM-01 -> U-MEM-03
U-MEM-02 -> U-MEM-03
U-MEM-01 -> U-MEM-04
U-MEM-01 -> U-MEM-05
U-MEM-01 -> U-MEM-06
U-MEM-02 -> U-MEM-06
U-MEM-03 -> U-MEM-06
U-MEM-04 -> U-MEM-06
U-MEM-05 -> U-MEM-06
U-MEM-03 -> U-MEM-07
U-MEM-06 -> U-MEM-07
U-MEM-04 -> U-MEM-08
U-MEM-07 -> U-MEM-08
U-MEM-06 -> U-MEM-09
U-MEM-08 -> U-MEM-09
U-MEM-06 -> U-MEM-10
U-MEM-04 -> U-MEM-11
U-MEM-10 -> U-MEM-11
U-MEM-04 -> U-MEM-12
U-MEM-11 -> U-MEM-12
U-MEM-04 -> U-MEM-13
U-MEM-11 -> U-MEM-13
U-MEM-12 -> U-MEM-13
U-MEM-11 -> U-MEM-14
U-MEM-12 -> U-MEM-14
U-MEM-14 -> U-MEM-15
U-MEM-13 -> U-MEM-16
U-MEM-14 -> U-MEM-16
U-MEM-14 -> U-MEM-17
U-MEM-05 -> U-MEM-18
U-MEM-14 -> U-MEM-18
U-MEM-03 -> U-MEM-19
U-MEM-07 -> U-MEM-19
U-MEM-11 -> U-MEM-19
U-MEM-14 -> U-MEM-19
U-MEM-07 -> U-MEM-20
U-MEM-08 -> U-MEM-20
U-MEM-09 -> U-MEM-20
U-MEM-04 -> U-MEM-21
U-MEM-06 -> U-MEM-21
U-MEM-09 -> U-MEM-21
U-MEM-03 -> U-MEM-22
U-MEM-12 -> U-MEM-22
U-MEM-16 -> U-MEM-22
U-MEM-17 -> U-MEM-22
U-MEM-21 -> U-MEM-22
U-MEM-17 -> U-MEM-23
U-MEM-23 -> U-MEM-24
U-MEM-15 -> U-MEM-24
U-MEM-16 -> U-MEM-24
U-MEM-17 -> U-MEM-24
U-MEM-18 -> U-MEM-24
U-MEM-19 -> U-MEM-24
U-MEM-20 -> U-MEM-24
U-MEM-21 -> U-MEM-24
U-MEM-22 -> U-MEM-24
U-MEM-24 -> U-MEM-25
U-MEM-07 -> U-MEM-26
U-MEM-09 -> U-MEM-26
U-MEM-14 -> U-MEM-26
U-MEM-16 -> U-MEM-26
U-MEM-22 -> U-MEM-26
U-MEM-25 -> U-MEM-26
U-MEM-01 -> U-MEM-27
U-MEM-07 -> U-MEM-27
U-MEM-08 -> U-MEM-27
U-MEM-09 -> U-MEM-27
U-MEM-16 -> U-MEM-27
U-MEM-26 -> U-MEM-27

External CLI routing port gates CLI-route-specific acceptance in U-MEM-05, U-MEM-12, U-MEM-14, U-MEM-18, and U-MEM-24. It is not represented as a `U-MEM` node because it is an upstream/deployed feature port, not memory-layer scope.
```

## 4.1 Requirement coverage map

| Requirement | Primary units |
|---|---|
| R-MEM-01 full layer/no MVP | U-MEM-01 through U-MEM-27 |
| R-MEM-02 canonical filesystem/git store | U-MEM-02, U-MEM-03, U-MEM-06 |
| R-MEM-03 typed records | U-MEM-01, U-MEM-06, U-MEM-07 |
| R-MEM-04 automatic episodic and durable capture | U-MEM-03, U-MEM-07 |
| R-MEM-05 semantic/preference promotion | U-MEM-06, U-MEM-08, U-MEM-09, U-MEM-27 |
| R-MEM-06 compaction safety | U-MEM-20 |
| R-MEM-07 retrieval and ranking | U-MEM-10, U-MEM-11 |
| R-MEM-08 packet assembly and injection | U-MEM-11, U-MEM-14, U-MEM-15, U-MEM-16, U-MEM-17 |
| R-MEM-09 multi-provider memory routing | U-MEM-12, U-MEM-13, U-MEM-14, U-MEM-15, U-MEM-16, U-MEM-17, U-MEM-26, U-MEM-27 |
| R-MEM-10 CLI-neutral and CLI-specific memory | U-MEM-05, U-MEM-18, U-MEM-24 |
| R-MEM-11 engine-class durability | U-MEM-19 |
| R-MEM-12 redaction, privacy, and scope | U-MEM-04, U-MEM-21, U-MEM-24, U-MEM-26 |
| R-MEM-13 observability | U-MEM-22 |
| R-MEM-14 review and administration | U-MEM-09, U-MEM-21, U-MEM-25, U-MEM-27 |
| R-MEM-15 migration and compatibility | U-MEM-17, U-MEM-23, U-MEM-24 |

## 5. Atomic units

### U-MEM-01 - Declare memory vocabulary and record envelopes

Contracts: C-MEM-01, C-MEM-03.

Axis: Information substrate.

Implement:

- `MemoryTier`, `MemoryRecordKind`, `MemoryScope`, `SourceRef`, `MemoryRecordEnvelope`.
- Stable record identity and content hash helpers.
- Supersession and redaction-state fields.

Acceptance:

- Illegal tier/kind values are rejected.
- Content hash is deterministic for equivalent records.
- Supersession and redaction fields are present on every record envelope.

Verification:

- Schema tests for valid and invalid envelopes.
- Deterministic hash tests.

### U-MEM-02 - Implement memory path registry

Contracts: C-MEM-02.

Axis: Information substrate.

Depends on: U-MEM-01.

Implement:

- Logical path classes for manifest, policy, episodic, semantic, procedural, and durable ledgers.
- Root binding with deployment-surface remapping.
- Traversal rejection.
- Directory creation strategy for canonical roots.

Acceptance:

- Every C-MEM-02 path resolves through the registry.
- Traversal outside root fails loudly.
- Deployment remapping preserves logical path identity.

Verification:

- Path resolution tests for every logical path.
- Traversal rejection tests.

### U-MEM-03 - Implement durable memory operation ledger

Contracts: C-MEM-08.

Axis: Information substrate.

Depends on: U-MEM-01, U-MEM-02.

Implement:

- `MemoryOperationEntry` as an additive C-IS-05/C-IS-06 state-ledger derivative.
- Canonical append-only writer for `durable/memory_ops.jsonl` over the existing C-IS ledger append/verify discipline.
- Rebuildable projection writers for promotion decisions, injection decisions, and retrieval events.
- Idempotency handling.
- Prior-event-hash chaining.
- Global append serialization for concurrent writers.
- Ledger verifier.

Acceptance:

- Duplicate idempotency key for equivalent operation is safe.
- Non-equivalent duplicate idempotency key fails loudly.
- Hash-chain verification detects tampering.
- Parallel appends cannot fork the canonical memory operation ledger.
- Projection entries are keyed by canonical ledger `action_id` and do not define independent causality.

Verification:

- Append, retry, conflict, and tamper tests.
- Concurrent append serialization tests.
- Projection rebuild tests.

### U-MEM-04 - Implement memory policy model

Contracts: C-MEM-09.

Axis: Information substrate plus operational discipline.

Depends on: U-MEM-01.

Implement:

- Capture, promotion, access, review, retention, and redaction decision enums.
- Policy document schema.
- Default disabled/no-memory policy that preserves current runtime behavior until memory is explicitly enabled.
- Policy resolver with fail-closed injection and promotion behavior.

Acceptance:

- Default policy denies retrieval, injection, native memory, and standard memory tools unless memory is enabled.
- Policy resolution can deny capture, summarize capture, allow capture, and redact capture.
- Policy resolution can deny, queue, or allow promotion.
- Policy failure denies promotion and injection.

Verification:

- Policy matrix tests.
- Fail-closed tests.

### U-MEM-05 - Implement CLI profile schema

Contracts: C-MEM-16.

Axis: Information substrate.

Depends on: U-MEM-01.

Implement:

- `CliProfileKind`.
- `CliProfile`, instruction source, external memory source, and import policy schemas.
- Optional binding fields for existing external CLI provider identity: provider name, provider kind, command name, and auth boundary.
- Built-in generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom profile validation.

Acceptance:

- Generic profile has no CLI-specific assumptions.
- Claude Code and Codex profiles require explicit source declarations.
- Built-in profiles declare provider identity bindings without creating a second provider-ordering system.
- Concrete mapping to deployed external CLI provider identities is verified only after the external CLI routing port is present.
- External memory source mutation is impossible unless import policy allows it.

Verification:

- Profile validation tests.
- Port-present provider identity mapping tests for the external CLI profiles.
- Import-policy guard tests.

### U-MEM-06 - Implement canonical memory store

Contracts: C-MEM-02, C-MEM-03, C-MEM-04, C-MEM-05, C-MEM-06, C-MEM-07.

Axis: Information substrate.

Depends on: U-MEM-01, U-MEM-02, U-MEM-03, U-MEM-04, U-MEM-05.

Implement:

- Store read/write interfaces for episodic, semantic, preference, procedural, and durable records.
- Canonical serialization.
- Atomic write discipline appropriate to local filesystem roots.
- Derived index invalidation hook.

Acceptance:

- Each canonical record kind can be written and read back byte-stably.
- Derived indexes are invalidated or marked stale after writes.
- Redacted/tombstoned records remain inspectable through the store API under audit mode.

Verification:

- Round-trip record tests.
- Derived-index invalidation tests.

### U-MEM-07 - Add automatic episodic capture API

Contracts: C-MEM-04, C-MEM-08.

Axis: Runtime.

Depends on: U-MEM-03, U-MEM-06.

Implement:

- Capture API for run start, turn completion, tool event, provider route, failure observation, compaction event, and run close.
- Durable ledger write for capture decisions.
- Minimal capture mode for redacted or summarized policy.
- Summary provenance fields for rule-generated, model-generated, operator, and imported summaries.

Acceptance:

- Every supported event can produce an episodic record and a memory operation entry.
- Stored summaries carry source, model when applicable, and summary hash.
- Capture failure is observable.
- Capture does not promote semantic memory.

Verification:

- Event capture tests.
- Capture failure tests.

### U-MEM-08 - Implement promotion candidate extraction

Contracts: C-MEM-10.

Axis: Runtime plus operational discipline.

Depends on: U-MEM-04, U-MEM-07.

Implement:

- Candidate extractor for facts, decisions, conventions, preferences, failure learnings, research findings, and procedural updates.
- Candidate source refs.
- Risk flags for sensitive, low-confidence, cross-scope, and behavior-changing candidates.

Acceptance:

- Extracted candidates are source-linked.
- Preference candidates distinguish operator-direct from inferred.
- Low-confidence candidates cannot auto-promote when policy requires review.

Verification:

- Candidate extraction tests from representative episodic records.

### U-MEM-09 - Implement promotion and review queue

Contracts: C-MEM-05, C-MEM-06, C-MEM-10.

Axis: Runtime plus operational discipline.

Depends on: U-MEM-06, U-MEM-08.

Implement:

- Promotion decision application.
- Review queue persistence for proposed semantic and procedural records.
- Operator approve, deny, supersede, and edit flow at the API level.
- Promotion decision ledger writes.

Acceptance:

- Approved semantic records become active only after policy/review allows it.
- Denied records are ledgered.
- Preference promotion requires scope, evidence, confidence, and injection policy.

Verification:

- Promotion lifecycle tests.
- Preference review tests.

### U-MEM-10 - Implement derived retrieval indexes

Contracts: C-MEM-02, C-MEM-11.

Axis: Information substrate.

Depends on: U-MEM-06.

Implement:

- Rebuildable metadata index over semantic/procedural records.
- Index version/hash.
- Rebuild command/API.
- Empty-store behavior.
- Optional non-authoritative search accelerator hook; absent accelerators degrade to deterministic metadata-index retrieval.

Acceptance:

- Index can be rebuilt from canonical records.
- Stale index is detected.
- Large-store retrieval uses the rebuildable index path rather than unbounded prompt dumping.
- Empty store returns a valid empty retrieval base.

Verification:

- Index rebuild and stale-detection tests.
- Large-store fixture test proving bounded indexed retrieval.

### U-MEM-11 - Implement retrieval, ranking, and packet assembly

Contracts: C-MEM-11, C-MEM-12.

Axis: Control plane plus information substrate.

Depends on: U-MEM-04, U-MEM-10.

Implement:

- Retrieval request/result models.
- Ranking over scope, recency, confidence, authority, pinning, failure-risk relevance, workflow, and CLI profile.
- Stable memory packet assembly with section ordering and token budget.
- Retrieval event ledger write.

Acceptance:

- Fixed store/policy/request produces stable selected refs and packet hash.
- Excluded considered refs carry reasons.
- Packet sections cite memory refs and obey budget.

Verification:

- Deterministic retrieval tests.
- Token budget tests.
- Exclusion reason tests.

### U-MEM-12 - Extend provider capability and access-mode selection

Contracts: C-MEM-13.

Axis: Action surface plus control plane.

Depends on: U-MEM-04, U-MEM-11.

Implement:

- `MemoryAccessMode` vocabulary.
- Capability reflection for native memory, standard memory tools, and prompt packet fallback.
- Selection function using provider, model, provider route, CLI profile, workflow policy, and token budget.

Acceptance:

- Anthropic can select native memory when policy allows.
- Tool-capable non-native providers can select standard memory tools.
- Providers without usable tools can select prompt-extension packet.
- External CLI route fields participate in access-mode selection when the external CLI routing port is present.
- Denial is explicit and ledgerable.

Verification:

- Access-mode matrix tests.
- Port-present external CLI route selection tests.

### U-MEM-13 - Define provider-neutral memory tools

Contracts: C-MEM-14.

Axis: Action surface.

Depends on: U-MEM-04, U-MEM-11, U-MEM-12.

Implement:

- Tool contracts for `memory.search`, `memory.read`, `memory.write_note`, `memory.propose_promotion`, and `memory.request_redaction`.
- Argument schemas.
- Output schemas carrying stable refs.
- Policy requirements per tool.

Acceptance:

- Tool schemas are provider-neutral.
- Write-like tools require durable ledger entries.
- Tool outputs never return untracked memory prose.

Verification:

- Contract schema tests.
- Policy requirement tests.

### U-MEM-14 - Implement runtime memory context composer

Contracts: C-MEM-11, C-MEM-12, C-MEM-13.

Axis: Runtime.

Depends on: U-MEM-11, U-MEM-12.

Implement:

- Run-start composition of policy, CLI profile, provider route, retrieval request, packet, and access mode.
- Injection decision ledger entry.
- No-memory-access denial entry.

Acceptance:

- Run start can produce a memory context with packet or denial.
- Packet hash and policy ref are stored before dispatch.
- External CLI provider routes compose with memory context when the external CLI routing port is present.
- No-memory-access is explicit.

Verification:

- Runtime composer tests for all access modes.
- Port-present composer tests for external CLI routes.

### U-MEM-15 - Implement prompt-extension packet fallback

Contracts: C-MEM-12, C-MEM-13.

Axis: Runtime.

Depends on: U-MEM-14.

Implement:

- Read-only system-prompt memory packet rendering.
- Provider prompt seam integration for providers that use top-level system content or leading system messages.
- Conflict detection with existing system prompt overrides.

Acceptance:

- Prompt packet is bounded, cited, and stable.
- Prompt injection conflict fails loudly.
- Denied or redacted records do not appear.

Verification:

- Prompt packet rendering tests.
- Provider prompt integration tests.

### U-MEM-16 - Implement standard memory tool executor

Contracts: C-MEM-14.

Axis: Runtime.

Depends on: U-MEM-13, U-MEM-14.

Implement:

- Tool executor for provider-neutral memory tools.
- Policy enforcement for every call.
- Durable ledger entries for reads and writes where required.
- Tool-call span emission.

Acceptance:

- `memory.search` and `memory.read` return only allowed refs.
- `memory.write_note` stays episodic unless policy promotes.
- `memory.propose_promotion` queues or applies policy decision.
- `memory.request_redaction` creates a reviewable durable request.

Verification:

- Tool executor tests.
- Non-native provider dispatch integration check.

### U-MEM-17 - Refactor Anthropic native memory adapter onto canonical store

Contracts: C-MEM-15.

Axis: Runtime.

Depends on: U-MEM-14.

Implement:

- Adapter bridge from Anthropic Memory callbacks to canonical store and policy.
- Compatibility with existing `/memories` path validation.
- Durable ledger entries for native adapter operations.
- Existing backend selection preserved where applicable.

Acceptance:

- Existing Anthropic callback behavior remains compatible.
- Native writes cannot silently promote semantic memory.
- Adapter reads and writes are policy-checked and ledgered.

Verification:

- Compatibility tests for existing memory callbacks.
- Native adapter policy tests.

### U-MEM-18 - Implement CLI profile loading

Contracts: C-MEM-16.

Axis: Runtime plus control plane.

Depends on: U-MEM-05, U-MEM-14.

Implement:

- Profile resolver for generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom profiles.
- Integration with existing external CLI provider config and dispatch metadata for `claude_code`, `codex`, `antigravity`, `gemini_legacy` over legacy `gemini`, and `generic-command`.
- Instruction source loading under policy.
- External memory source read/import guards.
- CLI profile provenance threading into capture, retrieval, and injection.

Acceptance:

- Generic profile works without CLI-specific files.
- Claude Code and Codex profiles require explicit source policy.
- Custom profile can declare instruction and memory sources.
- Profile resolution follows active runtime provider route and does not override enabled provider order or fallback-chain selection.
- CLI profile appears in episodic and durable records.

Verification:

- Profile resolver tests for all built-in profiles and a custom profile.

### U-MEM-19 - Implement engine-class durability bindings

Contracts: C-MEM-17.

Axis: Runtime plus control plane.

Depends on: U-MEM-03, U-MEM-07, U-MEM-11, U-MEM-14.

Implement:

- Binding to the existing five-value `EngineClass` taxonomy.
- Memory store version and packet hash carrier for checkpoint engines.
- Activity/snapshot boundary contract for replay engines.
- State-ledger write contract for pure-pattern engines.
- Reconciler observed-version carrier.
- WAL rebuild/prewarm contract.

Acceptance:

- Each engine class has a represented memory durability strategy.
- The represented classes match the current closed `EngineClass` enum before implementation proceeds.
- Replay cannot perform unstabilized retrieval without recorded version or packet hash.
- Pending writes do not become active semantic memory before commit boundary.

Verification:

- Contract-level tests for all five engine classes.

### U-MEM-20 - Implement compaction safety hook

Contracts: C-MEM-06, C-MEM-10.

Axis: Runtime plus operational discipline.

Depends on: U-MEM-07, U-MEM-08, U-MEM-09.

Implement:

- Compaction candidate extraction before context loss.
- Required disposition for each candidate.
- Durable compaction decision entry.
- Fail-closed behavior when disposition cannot be written.

Acceptance:

- Compaction cannot complete without candidate disposition.
- Candidates can be discarded, kept episodic, promoted, or queued.
- Disposition is auditable.

Verification:

- Compaction safety tests.

### U-MEM-21 - Implement redaction, tombstone, and retention

Contracts: C-MEM-18.

Axis: Operational discipline plus information substrate.

Depends on: U-MEM-04, U-MEM-06, U-MEM-09.

Implement:

- Redaction event schema and writer.
- Tombstone state transition.
- Retention expiry operation.
- Ledgered physical redaction/compaction operation for content-bearing files where policy requires content removal.
- Retrieval/tool exclusion for redacted or tombstoned records.

Acceptance:

- Redacted records are excluded from packets and tools.
- Tombstoned records remain ledger-visible.
- Physical content removal preserves old and new content hashes in the redaction event.
- Retention expiry is ledgered before derived index removal.

Verification:

- Redaction/tombstone/retention tests.
- Physical redaction hash-preservation tests.

### U-MEM-22 - Implement memory observability

Contracts: C-MEM-19.

Axis: Action surface plus operational discipline plus runtime.

Depends on: U-MEM-03, U-MEM-12, U-MEM-16, U-MEM-17, U-MEM-21.

Implement:

- Memory telemetry attributes for capture, retrieval, ranking, packet assembly, injection, promotion, native adapter calls, standard tool calls, redaction, and denial.
- Failure class vocabulary.
- Additive compatibility with existing `memory.*` attributes: `memory.operation.kind`, `memory.path`, `memory.backend`, `memory.bytes_read`, `memory.bytes_written`, and `memory.context_editing_active`.

Acceptance:

- All major memory operations emit telemetry.
- Failure classes distinguish policy denial, path violation, IO failure, serialization failure, provider adapter failure, and retrieval empty result.
- Existing memory telemetry consumers remain compatible and existing attribute names are not renamed.

Verification:

- Span/attribute tests.

### U-MEM-23 - Implement migration and compatibility defaults

Contracts: C-MEM-15.

Requirements: R-MEM-15.

Axis: Runtime.

Depends on: U-MEM-17.

Implement:

- Adapter compatibility for existing storage backend selections.
- Migration path from callback-only memory store to canonical memory root.

Acceptance:

- Existing callback-backed memory can operate through the new adapter.
- Migration is explicit and ledgered.

Verification:

- Adapter backward compatibility tests.
- Migration dry-run tests.

### U-MEM-24 - Cross-provider and CLI verification suite

Contracts: C-MEM-20 and all preceding contracts.

Axis: Runtime plus information substrate plus action surface plus control plane plus operational discipline plus cross-axis evidence.

Depends on: U-MEM-15, U-MEM-16, U-MEM-17, U-MEM-18, U-MEM-19, U-MEM-20, U-MEM-21, U-MEM-22, U-MEM-23.

Implement:

- End-to-end scenario for Anthropic native memory.
- End-to-end scenario for standard memory tools on a non-native provider path.
- End-to-end scenario for prompt-extension fallback.
- CLI profile scenarios for generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom.
- External CLI routing scenarios for Claude Code, Codex, Antigravity, legacy Gemini, and generic-command, with credential-gated live tests separated from deterministic subprocess-fake tests.
- Compaction safety scenario.
- Redaction and denial scenarios.
- Memory poisoning and cross-scope isolation scenarios.

Acceptance:

- All access modes are exercised.
- All CLI profiles are exercised.
- Existing external CLI provider ordering and optional degradation semantics are preserved.
- Compaction safety is exercised.
- Redaction and policy denial are exercised.
- Model-authored memory cannot become injectable without policy approval.
- Cross-project, cross-workflow, cross-tenant, cross-provider-family, and cross-CLI leakage is denied.
- Credential-gated live checks are separated from non-credential checks with explicit gates.

Verification:

- Local deterministic suite.
- Optional live-provider suite behind explicit credential gates.
- Cross-axis review of evidence.

### U-MEM-25 - Closeout, documentation, and review evidence

Contracts: C-MEM-20.

Axis: Cross-axis.

Depends on: U-MEM-24.

Implement:

- Operator-facing memory policy documentation.
- Maintainer-facing architecture notes.
- Migration notes.
- Review evidence packet.
- Closeout checklist mapping every R-MEM and C-MEM item to implementation and verification evidence.

Acceptance:

- Every R-MEM requirement is mapped to code and verification evidence.
- Every C-MEM contract is mapped to implementation and verification evidence.
- Any remaining blocker names an external dependency, includes a deterministic absence probe, and is registered in a fork, roadmap, or credential-gate surface.
- Out-of-family review has been run against the complete diff or explicitly blocked with reason.

Verification:

- Documentation link check.
- Closeout checklist review.

### U-MEM-26 - Enforce run-level memory scope keying and cross-family tool withholding

Contracts: C-MEM-03, C-MEM-13, C-MEM-14.

Requirements: R-MEM-09, R-MEM-12.

Axis: Runtime plus control plane plus operational discipline plus information substrate.

Depends on: U-MEM-07, U-MEM-09, U-MEM-14, U-MEM-16, U-MEM-22, U-MEM-25.

Back-flow authority: `.harness/class_1_fork_b86_memory_scope_provider_family_keying.md` (RATIFIED Class 1 fork; register rows `B-86`, `B-89`, `B-90`), applied at `Spec_Memory_Substrate_v1.md` v1.1.

Implement:

- The C-MEM-13 cross-family withholding guard at the standard-memory-tools context resolution: when `standard_memory_tools` has been selected and the dispatched candidate's provider family differs from `MemoryScope.provider_family`, neither the memory tool schemas nor the scope reference are exposed for that dispatch, and the dispatch proceeds without model-facing memory access.
- A named denial reason recorded for the withheld dispatch on the C-MEM-19 memory telemetry surface, following the span-shaped disposition already used for the withheld read-only rendered packet. No new C-MEM-08 operation kind is introduced; the denial reason rides an attribute value.
- The `B-89` writer-side repair: the capture path consumes the run's composed record scope instead of constructing an independent `MemoryScope`, so written records carry the run's `ProviderFamily` value rather than a raw per-dispatch provider key.
- Validate-or-canonicalize of `provider_family` at every durable `MemoryScope` write surface enumerated in the acceptance criteria below - capture, promotion-record write, and the statically-supplied context that feeds it - not at the capture path alone.
- Forward-only normalization posture for records already written with a non-value identifier: no rewrite, no migration.

Acceptance:

- A cross-family servable dispatch lands with the memory tools and scope reference withheld and the withholding reported on the C-MEM-19 memory telemetry surface with a named denial reason; the dispatch itself still completes.
- Where the withholding is realized as a transition of that dispatch to `no_memory_access`, C-MEM-13's pre-existing must-ledger invariant is satisfied through the existing `inject` memory operation entry and its injection-decision projection; where it is not such a transition, the recording is span-only and no durable row is claimed. Neither branch introduces a C-MEM-08 operation kind.
- Harness-authored automatic capture is unaffected by the withholding guard and continues on the same dispatch.
- A same-family servable dispatch is unchanged: schemas and scope reference are exposed exactly as before.
- Records written by the capture path carry the run's composed record scope, including `provider_family` as a `ProviderFamily` value and the `tenant` and `workload_class` fields the independently-constructed scope omitted, closing `B-90`.
- A record written under the run's composed scope is retrievable by a family-scoped request of that same family, which the pre-repair raw-key write was not.
- Write-boundary coverage: the C-MEM-03 "never a provider key" value domain is enforced at **every scope-AUTHORING durable write** of a `MemoryScope` - every write that originates a scope value - and not only at the automatic capture path. It does **not** bind a state transition of an already-persisted record, whose deliberate exception is surface (f) below. The grounded authoring surfaces are (a) automatic capture, which constructs its own scope today (`memory_capture.py:585-591`) and is the `B-89` half above; (b) the promotion record write, which persists `candidate.suggested_scope` **verbatim** into `MemoryRecordEnvelope.scope` (`memory_promotion.py:741-753`), whose scope arrives either from a caller/model-supplied promotion hint (`_candidate_from_hint`, `memory_promotion.py:568-582` - today only risk-flagged `CROSS_SCOPE` at `:609`, never normalized) or from the tool-execution context (`memory_tool_executor.py:405-412`); (c) a statically-supplied `RuntimeMemoryContext` on the non-recomposing dispatcher path (`llm_dispatch.py:669`, `:1475`), whose `record_scope` reaches (b) through that same context; (d) the compaction-decision write (`memory_compaction_safety.py:140-169`), whose `event_scope = scope or _scope_from_candidates(candidates)` (`:157`) is either an explicit caller-supplied `scope` keyword (`:148`) or `candidates[0].suggested_scope` (`:241-244`), which inherits (b1)'s untrusted origin verbatim; and (e) the native-adapter tool-event write (`native_memory_adapter.py:369`, `_build_tool_event_record` `:388` persisting `scope=self._scope` at `:441`), whose `self._scope` is a REQUIRED constructor argument (`:96-116`) and is therefore whatever the wiring supplies. Surface **(f)** is the redaction / tombstone / retention-expiry transition (`harness-is/src/harness_is/memory_redaction.py`, `_transition` `:168-263`: reads the target with `audit_mode=True` at `:184-189`, rebuilds the envelope via `record.envelope.model_copy(update={...})` at `:201-210`, and durably rewrites it with `self._store.write_record(updated_record)` at `:258`). It is a **deliberate exception, governed by an explicit LEGACY-REDACTION rule**: a redaction, tombstone, or retention-expiry rewrite **preserves the record's existing scope verbatim**, including an out-of-domain legacy `provider_family`. The rewrite is a state transition of an existing record, not the authoring of a new scope - the `:201-210` update set carries only `updated_at`, `content_hash`, and `redaction_state`, so scope preservation is already the behaviour today and the rule pins it rather than changing it. Applying the value-domain obligation here would be a **compliance hazard**: a central write validator would make a pre-v1.1 record carrying a raw provider key impossible to redact or tombstone, i.e. an un-redactable legacy sensitive record. Exempting it launders nothing, because a redaction cannot create a record that did not already exist and cannot introduce a value the record did not already carry. Grounding note for (d) and (e): neither is discharged by construction. At HEAD both have test-only call sites (`CanonicalNativeMemoryToolBackend(` and `complete_compaction(` resolve only under `harness-runtime/tests/`), so no composition root currently seeds either from the run's composed scope - the obligation therefore attaches at the write itself, and at whatever production wiring later appears, not to an assumed-safe caller. Each surface validates or canonicalizes `provider_family` before the write. Where the input is a **registered provider key**, it is canonicalized to that key's `ProviderFamily` value through the existing provider-to-family authority (`lifecycle/cross_family_cost_tag.py:60-69`) - consistent with that authority's own semantics and with (b1)'s existing risk-flagging-rather-than-rejecting posture. Where the input is an **unregistered or otherwise out-of-domain identifier**, the write is denied: C-MEM-09 already requires promotion to deny on failed policy resolution, and no surface silently persists an out-of-domain value. **At the capture surface the unknown-key case cannot arise once the writer repair lands**, because the capture path then derives nothing from the per-turn provider key at all - it consumes the run's composed `record_scope`, whose `provider_family` is by construction a valid `ProviderFamily` value derived once from the chain primary. If any residual code path can still construct a capture scope from a provider key, it must retain the composed run scope: **never the raw key, and never `null`**. `null` is emphatically not a fail-safe here - per C-MEM-03's asymmetric semantics a stored `null` is the unpartitioned wildcard that matches *every* requested family, so degrading an unknown key to `null` would widen the record's reach rather than narrow it, against R-MEM-12.
- Write-boundary **ordering**, at two surfaces where a validate-at-the-write-call placement is provably too late. **(b) promotion:** canonicalization happens **before** risk-flag and candidate-identity derivation, not merely before the record write. `_candidate_from_hint` (`memory_promotion.py:547-582`) derives `risk_flags` first (`:553-556` -> `_risk_flags` `:599-613` -> `_scope_escapes_source` `:625-640`, which compares `provider_family` as a raw string at `:628-639`) and then folds the raw `hint.suggested_scope` into `candidate_id` (`:569` -> `_candidate_id` `:691-710`, hashing `suggested_scope.model_dump(mode="json")` at `:701`), both strictly before the record write at `:741-753`. Canonicalizing only at the write would therefore leave two observable defects intact: key-vs-value-equivalent inputs receiving **different** candidate identities, and a registered alias of the record's own family being **falsely** flagged `CROSS_SCOPE`. **(e) native tool event:** validation happens **before** `_append_native_adapter_call`. `_persist_tool_event` (`native_memory_adapter.py:358-386`) appends the `native_adapter_call` operation-ledger entry at `:378-383` and only then writes the record at `:384`, so a denial at the record write would strand a durable ledger entry referencing a record that was never persisted.
- Request-boundary enforcement, mirroring the authoring side. The `provider_family` value domain is enforced on retrieval-request and derived-index-query scopes as well: a requested `provider_family` that is a registered provider key is canonicalized to its `ProviderFamily` value, and an out-of-domain identifier is rejected - the same split, no third posture. The grounded request models are `MemoryRetrievalRequest` (`harness-is/src/harness_is/memory_retrieval.py:73`) and `DerivedRetrievalIndexQuery` (`harness-is/src/harness_is/memory_retrieval_index.py:104-112`, `scope` at `:111`), both of which accept a `MemoryScope` whose `provider_family` is an arbitrary string; the request-scope construction sites are `memory_context._retrieval_request` (`:557-573`, `scope=request.record_scope` at `:570`) and `memory_tool_executor._search` (`:268-289`, `scope=context.scope` at `:283`), both of which draw from a scope that is caller-supplied on the statically-supplied-context path. Without this the value domain is one-sided: the scope predicates match raw strings, so a crafted raw-key request reaches a legacy raw-key record and the "not retrievable under a family-scoped request" guarantee - and the permanent-residual claim resting on it - are bypassable. **Direct readers are in scope on the same terms**: several paths reach a scope predicate without constructing either request model, so enforcing at the request models alone leaves the bypass open. They are `CanonicalNativeMemoryToolBackend._require_retrieval_allowed` (`native_memory_adapter.py:289-306`, passing the constructor-supplied `self._scope` as `requested_scope` at `:298-302`; the same field is also raw-compared at `_latest_state` `:319-328`, `:327`) and the standard-tool-executor by-reference paths (`memory_tool_executor.py:500-526`, `requested_scope=context.scope` at `:511`, and `_read_retrievable_record_by_ref` `:542-555`, same at `:551`). Each canonicalizes a registered provider key and rejects an out-of-domain identifier before the predicate sees it.
- Per-layer null-request denial. A `provider_family=None` request must be denied against a family-scoped record **at each enforcement layer independently**, not only at the policy predicate. Today `_scope_mismatch` (`memory_retrieval.py:371-384`) and `_scope_matches` (`memory_retrieval_index.py:379-396`) both **admit** family-scoped entries for a `null` request - only `_scope_not_broader` (`memory_policy.py:336-359`) denies - and `DerivedRetrievalIndexStore.retrieve` (`memory_retrieval_index.py:212-231`) reaches `_scope_matches` through `_filter_candidates` at `:221` **with no policy leg at all**, so that public path returns family-scoped metadata and refs to a `null` request. That also breaks the `:481` ordering requirement, which binds the scope boundary *before ranking* (`_order_candidates` runs at `:222`, after the filter). Each predicate is fixed on its own terms.
- Legacy READ compatibility is retained: already-persisted records are not rewritten or re-scoped, the read paths continue to serve them unchanged (`native_memory_adapter.py:300`, `memory_tool_executor.py:510` and `:550` pass `record.envelope.scope` through as-is), and the forward-only residual stands - pre-repair records written with a non-value identifier stay unretrievable under family-scoped requests.
- The forward-only migration residual is stated: pre-repair records written with a non-value identifier remain unretrievable under family-scoped requests and are not rewritten.
- The U-MEM-25 closeout evidence rows for C-MEM-03, C-MEM-13, and C-MEM-14 **and** for R-MEM-01, R-MEM-09, and R-MEM-12 - all six carry a `PENDING - U-MEM-26` marker at the spec-leg PR - are re-opened and extended to cover the v1.1 obligations (value domain, asymmetric `null` semantics, and the write-boundary enforcement above; cross-family withholding and its recording surface; the qualified exposure obligation), the packet's version-scoping status wording is lifted from v1-only, and the closeout check is re-run green with those rows in place. The unit cannot close while the packet still says the v1.1 obligations are uncertified.

Verification:

- Cross-family servable dispatch test asserting withheld schemas, withheld scope reference, the named denial reason on the telemetry surface, and continued dispatch.
- Same-family control test asserting exposure is unchanged.
- Capture-unaffected test asserting harness-authored capture still writes on the withheld dispatch.
- Capture-scope test asserting written records carry the composed scope's `provider_family`, `tenant`, and `workload_class`.
- Round-trip retrieval test proving a newly captured record is visible to a family-scoped request of its own family.
- Asymmetric `null` test pair: a `null`-family record is reachable by a family-scoped request, and a family-scoped record is NOT reachable by a `null`-family request.
- Write-boundary test per grounded surface: a promotion hint carrying a **registered** raw provider key is canonicalized to that key's family value rather than persisted verbatim; a promotion hint carrying an **unregistered or out-of-domain** identifier is denied per C-MEM-09 rather than persisted; a tool-executor promotion under a statically-supplied context lands a canonicalized family value; and a capture taken during a dispatch whose candidate carries an unregistered provider key still lands the composed run scope's family value - never the raw key, never `null`.
- Witness for surface (d): a `complete_compaction` call whose candidate-derived scope carries a raw provider key persists a canonicalized family value (registered key) or is denied (unregistered identifier), asserted on the written compaction-decision record.
- Ordering witnesses for surface (b), asserted on the derived candidate rather than only on the persisted record: two hints whose `provider_family` inputs are key-vs-value equivalent for the same family (for example a registered provider key and its `ProviderFamily` value) produce the **same** `candidate_id`; and a hint carrying a registered alias of the source record's own family is **not** flagged `CROSS_SCOPE`. Both fail if canonicalization is placed at the write call rather than ahead of `_risk_flags` and `_candidate_id`.
- Witness for surface (e): a `CanonicalNativeMemoryToolBackend` constructed with a raw-provider-key scope persists a canonicalized family value (registered key) or is denied (unregistered identifier) on its tool-event write, asserted on the written record. On the denial case the witness asserts that **both** the record store **and** the memory operation ledger are unchanged - no `native_adapter_call` entry is appended for a record that was never persisted.
- Witness for surface (f), the LEGACY-REDACTION rule: a legacy record already persisted with a raw provider key in `provider_family` can be redacted **and** tombstoned, and retains its original scope byte-for-byte through the transition - the write validator must not refuse it, and must not rewrite its scope. This is the compliance witness: without it, a central validator silently makes legacy sensitive records un-redactable.
- Request-boundary witnesses, both halves: a retrieval request whose scope carries a registered raw provider key is canonicalized to that key's family value, and one carrying an out-of-domain identifier is rejected. Negative pair, asserted at **both** read layers: a legacy record persisted with a raw provider key remains unreachable by a crafted raw-key request through the retriever **and** through the derived index - the crafted-request bypass must not resurrect it at either layer.
- Direct-reader negative witness (i): a legacy raw-key record stays unreachable through `CanonicalNativeMemoryToolBackend`'s retrieval-allowed path when the backend is constructed with a crafted raw-key scope - the canonicalize/reject step fires before `_scope_not_broader` sees either side.
- Direct-reader negative witness (ii): the same, through the standard-tool-executor by-reference paths under a crafted raw-key `context.scope`, asserted on both the index-entry lookup and the record-by-ref lookup.
- Per-layer null-request denial witness (i), retriever: a `provider_family=None` request does **not** reach a family-scoped record through `_scope_mismatch`, asserted against that predicate directly.
- Per-layer null-request denial witness (ii), derived index: the same through `_scope_matches`, asserted both against the predicate and end-to-end through the public `DerivedRetrievalIndexStore.retrieve`, whose result must carry neither the entry nor its ref. Kept separate from witness (i) for the same reason as the `B-90` trio below: one aggregate test passes over whichever layer is still leaking.
- `B-90` layer-independent tenant denial, witness (i): a tenant-A request fails to reach a tenant-B tool-captured record at the retriever predicate `MemoryRetriever._scope_mismatch` (`harness-is/src/harness_is/memory_retrieval.py:371-384`), asserted against that predicate directly.
- `B-90` layer-independent tenant denial, witness (ii): the same denial at the derived-index predicate `_scope_matches` (`harness-is/src/harness_is/memory_retrieval_index.py:379-396`), asserted against that predicate directly.
- `B-90` layer-independent tenant denial, witness (iii): the same denial at the policy predicate `_scope_not_broader` (`harness-is/src/harness_is/memory_policy.py:336-359`), asserted against that predicate directly. The three are deliberately separate: a single composite retrieval witness passes **over** the other two layers - precisely how the `B-90` omission survived - so U-MEM-26 cannot close `B-90` while any one enforcement layer still admits the record.
- Re-run of the memory closeout check with all six refreshed evidence rows (C-MEM-03 / C-MEM-13 / C-MEM-14 and R-MEM-01 / R-MEM-09 / R-MEM-12) and the packet's version-scoping wording lifted.

Implementation note - the enumerated inventory is review-time, not proven complete:

- The reader and writer surfaces enumerated across this unit - six authoring writers, two request models, the direct readers, and the three scope predicates - were accumulated by successive out-of-family review rounds against one HEAD. That is a **review-time inventory, not a proven-complete set**, and each round found surfaces the previous round's enumeration had missed. The impl leg MUST therefore **re-ground the full inventory at its own HEAD before building**: grep every caller of `write_record` and every caller of the three scope predicates, and reconcile the result against the list above. Any surface found beyond this enumeration carries the same obligations - value-domain enforcement at scope authoring, canonicalize-or-reject at the request and direct-reader boundaries, validation ahead of any identity, risk, or ledger derivation, and the preserve-verbatim exception for redaction transitions - **by rule, not by listing**. The enumeration is a starting point and an audit aid; it is not the definition of the obligation, and a surface's absence from it is never a licence to skip enforcement.

Out of scope for this unit:

- The C6 stated limit at C-MEM-13: family equality is necessary but not sufficient, and the within-family local-terminal posture is addressed outside this contract.
- Promotion eligibility of records captured during a cross-family fallback leg, which remains a C-MEM-10 policy question carried as a named open question at the spec v1.1 change-note.

### U-MEM-27 - Gate promotion of cross-family-captured records behind review

Contracts: C-MEM-03, C-MEM-10.

Requirements: R-MEM-05, R-MEM-09.

Axis: Information substrate plus runtime plus operational discipline.

Depends on: U-MEM-01, U-MEM-07, U-MEM-08, U-MEM-09, U-MEM-16, U-MEM-26.

Back-flow authority: `.harness/class_1_fork_c_mem_10_cross_family_promotion_eligibility.md` (RATIFIED Class 1 fork, reading B - flag plus gate; register row `B-92`), applied at `Spec_Memory_Substrate_v1.md` v1.2. All `file:line` cites in this unit were verified by direct read at HEAD `57f840b6`.

Implement:

- The C-MEM-03 tri-state `MemoryRecordEnvelope.captured_cross_family` field: optional, `true` / `false` / `unknown`, absent-reads-as-`unknown`, on `harness-is/src/harness_is/memory_record_envelope.py` (the model at `:126-142`, `model_config = ConfigDict(extra="forbid", frozen=True)` at `:129`). The default must be **`unknown`, never `false`** - a `false` default would persist a determination no writer made, which is the defect the tri-state exists to prevent, and it is also what keeps the other three envelope construction sites (`harness-runtime/src/harness_runtime/memory_promotion.py:844`, `harness-runtime/src/harness_runtime/lifecycle/native_memory_adapter.py:463`, `harness-runtime/src/harness_runtime/memory_compaction_safety.py:327`) and every pre-amendment serialized envelope valid under `extra="forbid"`.
- The **single central write-side derivation, ORIGIN-AWARE and split across two private methods by where its inputs live.** The derivation has two inputs of different kinds and they are not co-located, which is the whole reason this bullet is precise about placement. (i) The **content-origin disposition** is determined at `EpisodicMemoryCapture._capture` (`harness-runtime/src/harness_runtime/memory_capture.py:631`), the one method that receives `event_kind` - a value each `capture_*` method supplies for itself (for example `event_kind="tool_event"` at `:472`) and which therefore maps one-to-one onto the calling method and onto that method's origin disposition. (ii) The **family comparison** consumes the call's raw `provider` and the record's resolved scope, which are held at `_record` (`:1015-1046`, `provider` at `:1025`, the resolved scope from `_scope_for_record` at `:1048-1086`): canonicalize `provider` through the existing house authority - `canonical_scope_family` / `resolve_scope_family` (`memory_scope_family.py:50` / `:62`), binding the fail-closed `provider_family_for_scope_check` (`lifecycle/cross_family_cost_tag.py:101-124`) - and compare it against the resolved scope's own `provider_family`. The stored value is the origin disposition **gating** that comparison: where origin is not dispatch-derived the result is `unknown` and the comparison is not consulted at all. **The private parameter shape carrying the disposition is implementation discretion** - an enum, a bool-plus-sentinel, or a small value object all conform. **Where the final value is computed is NOT discretionary:** `_capture` determines the origin disposition and passes that disposition into `_record`, and `_record` computes the final tri-state. Computing a finished tri-state at `_capture` is non-conforming, because the resolved scope the comparison needs does not exist there. What is **not** discretionary: the value must never be derived from `provider` and scope **alone**, because those two are identical in shape on a pre-dispatch call and a post-dispatch one, so a comparison-only derivation would classify pre-dispatch and run-lifecycle captures as `false` in violation of C-MEM-03. **No `capture_*` signature changes and no per-method threading**: all seven methods (`:294` / `:337` / `:382` / `:439` / `:487` / `:534` / `:585`) already pass `provider` to `_capture` (`:329` / `:374` / `:431` / `:479` / `:526` / `:577` / `:623`), which passes it to `_record` (`:649-658`), and `event_kind` is already an argument of `_capture`. No new normalization posture is invented; the comparison reuses the B-86 / B-89 authorities verbatim.
- One mechanical consequence of that placement: `_scope_for_record` is today called **inline** at the envelope's `scope=` argument (`:1038-1042`), so the resolved scope must be bound to a local **before** the `MemoryRecordEnvelope(...)` construction at `:1030-1044`, and both the local and the derived tri-state passed into it.
- **The content-origin signal is NOT available from `provider` alone, and the derivation site is `_capture` rather than `_record` on that account** (the round-7 call-site sweep forced this correction to an earlier draft of this unit, which asserted `_record` already held both inputs it needed). Two grounded facts settle it. First, `provider` cannot discriminate origin: the pre-dispatch run-start caller passes a `provider` exactly as the post-dispatch turn caller does - one a selection, one a producer - so a predicate over `provider` and the resolved scope alone cannot tell them apart. Second, the capture layer never sees a provider response at all: every content-bearing method receives an **already-summarized string** from its caller (`capture_tool_event(..., summary_text: str, ...)` at `memory_capture.py:445`, and the same shape at its siblings), so content origin is not recoverable from the captured content either. What *is* available centrally is the **`event_kind` argument** that every `capture_*` method already passes to `_capture` (for example `event_kind="tool_event"` at `:472`). It identifies the **calling method**, which is a sound realization of the rule **only for methods whose every production invocation shares one origin** - and that qualification is load-bearing, not boilerplate: `capture_failure_observation` can describe a dispatch that produced output *or* one that produced none, so its origin varies **per invocation** and the method name cannot decide it. Such a method either takes an explicit per-call origin value (an impl-leg choice, and the one place a public signature addition would be justified) or records `unknown` for the invocations it cannot distinguish. Honest scoping: `capture_failure_observation` has **no production caller at HEAD** per the completed sweep, so this is rule-precision rather than a live misclassification - but the rule must be right before a caller appears. The data flow is therefore fixed, and is stated identically on every surface: `_capture` determines the ORIGIN DISPOSITION from `event_kind` and passes **that disposition** (not a finished tri-state) into `_record`, which computes the final value: origin gates the family comparison over the raw `provider` and the resolved scope, both of which live there. This respects both constraints - `event_kind` exists only at `_capture`, the resolved scope only at `_record` - while keeping **one** site that computes the final value. **No public writer signature changes** - the fork's R9 conclusion survives; what changes is which private method computes the value. Do not add a public parameter to the seven `capture_*` methods to carry origin: `event_kind` already carries it.
- `unknown` recorded, never `false`, in each of the four undetermined cases: **the stored content was not produced by a completed provider dispatch** (the round-6 [P2] case, below); `provider is None` (the type is `str | None` at every capture signature - `:302` / `:347` / `:396` and siblings); the provider key is unregistered, so `provider_family_for_scope_check` returns `None` and its own documented fail-closed obligation applies (`cross_family_cost_tag.py:101-124`); or the resolved `scope.provider_family` is `null`, the C-MEM-03 unpartitioned wildcard, which `resolve_scope_family` passes through untouched (`memory_scope_family.py:62-68`) and against which cross-family is undefined.
- **The content-ORIGIN condition, which is what makes the derivation honest rather than merely central.** Per C-MEM-03's derivation rule, a determination is recorded **only where the stored content derives from the output of a completed provider dispatch**; the writer records `unknown` otherwise. The discriminator is the **capturing caller's own knowledge of holding a completed dispatch result** - a property of the call, not a stored field. Two grounded poles, both verified by direct read at this leg's HEAD. (a) **Dispatch-derived, determination REQUIRED:** the production turn capture. `LocalAutomaticMemoryRuntime.capture_turn_completion` (`harness-runtime/src/harness_runtime/automatic_memory.py:240-284`) receives `response: Mapping[str, Any]` (`:249`), computes the stored `response_summary=_response_summary(response)` from that actual provider response (`:269`), and passes the dispatched `provider` / `model` (`:276-277`). This content is dispatch-derived and must carry a real determination. (b) **Pre-dispatch, `unknown` REQUIRED:** `compose_for_dispatch` calls `_capture_run_start_once` at `:232` and only then returns the context at `:238`, so the run-start record is written **before any provider call** and the provider it is handed is a *selection*, not a producer; a same-family selection must not land `false`. Run-lifecycle metadata is `unknown` whenever written, since it derives from no dispatch output at all - both run writers' content is `run_id` / `workflow_id` / `thread_id` / `engine_class` / `cli_profile` / `provider_route` / `started_at` / `closed_at` / `close_status`, with **no summary field of any kind**.
- **`summary_source` is NOT the discriminator, and the unit must not use it as one** (round-7 [P2] correction to an earlier draft of this very bullet, which said a `harness_rule` summary is "the harness's text, not a provider's"). That was **false in the most common production case**: the turn path at `:269-270` summarizes a real provider response *using* a harness rule and labels the summarizer `SummarySource.HARNESS_RULE`, so a `summary_source`-keyed rule would mark every production turn capture `unknown`, including completed same-family dispatches - forcing review on content whose provenance is in fact known, and contradicting this unit's own claim that content-bearing captures receive determinations. Content **origin** and summarization **mechanism** are independent axes; only origin governs this field. **Implement the condition, not a method list and not a `summary_source` test** - either would fall behind the implementation, which is the failure mode rounds 5 and 6 each corrected once already in this unit.
- The `EPISODIC_RUN` consequence, stated so the multi-writer witness is not misread: **both** run writers record `unknown` under this rule, so the surviving overwritten run record carries `unknown` - not a determination inherited from run-close. That is the honest value for a record whose content is metadata, and it costs nothing at the promotion pipeline, which sources candidates from the content-bearing kinds.
- The `cross_family_capture` risk-flag value admitted into the implementation-side flag enumeration `PromotionRiskFlag` (`memory_promotion.py:80-86`), which is a closed `StrEnum` even though the C-MEM-10 contract field is an open `list<string>`. This is the only enum edit the unit makes.
- The **read-side gate at both promotion entry points**, with the flag as the **single gate authority** per the C-MEM-10 biconditional. The provenance value is read from the source record's envelope **exactly once per candidate**, at flag-derivation time, and yields the `cross_family_capture` flag; the four decision predicates then consume **the derived flag set** - not a second read of `source.envelope.captured_cross_family`. Entry point 1, the hint path: `_candidate_from_hint` (`memory_promotion.py:616-655`) already computes `risk_flags = _risk_flags(hint, source_scope=record.envelope.scope)` at `:626-629` (`_risk_flags` at `:672-686`), which is where the provenance read belongs; `_review_required` (`:762-773`) and `_auto_promote_allowed` (`:776-790`) currently take only `hint` and `resolution` and must additionally receive **that flag set**. Entry point 2, the tool path: `_propose_promotion` (`harness-runtime/src/harness_runtime/memory_tool_executor.py:399-435`) already computes `risk_flags=_promotion_risk_flags(source)` at `:425` (defined `:882-885`), again the right derivation site; `_promotion_review_required` (`:433`, defined `:888-894`) and `_promotion_auto_allowed` (`:434`, defined `:897-903`) take the policy resolution alone and must additionally receive that flag set. These are internal-helper signature widenings, not public contract changes.
- **Two parallel derivations of the same fact are forbidden, and this is an acceptance-bearing constraint rather than a style preference.** A gate computed from the envelope and a flag computed from the envelope are free to diverge under later edits, which would leave the flag advisory - the exact condition the `B-92` fork found at this pipeline and that C-MEM-10 now forbids. There must be no code path on which a candidate is gated for cross-family capture without carrying the flag, or carries the flag without being gated.
- **A `PromotionCandidate` model validator rejecting the illegal PAIR**, extending the existing `model_validator(mode="after")` (`memory_promotion.py:229-243`): when `cross_family_capture` is in `risk_flags`, `review_required` must be `True` and `auto_promote_allowed` must be `False`, or construction is refused. Its scope is stated exactly, because an earlier draft of this unit overstated it: this is a **consistency** check at every *validating* constructor (init, deserialization). It is **not** a provenance check and **not** an unreachability guarantee - it cannot see a candidate that omits the mark, and it does not run on `model_copy(update=...)`, which bypasses after-validators by design on this project's Pydantic (2.13.4, probed directly; `candidate.model_copy(...)` is already used on this model at `memory_compaction_safety.py:288-292`). The unit must **not** attempt to close the copy route by overriding `model_copy` - that fights the framework's frozen-copy semantics for a guarantee the activation boundary below already provides properly.
- **The activation-boundary re-derivation, which is where the obligation actually rests** (C-MEM-10 surface 2). Before a candidate the service did not itself derive becomes an ACTIVE record, `approve` and `edit_and_approve` (`memory_promotion.py:354-390` / `:416-449`) must **re-derive** the condition from the stored source record(s) named by `candidate.source_memory_refs` - reading each record's `captured_cross_family` - rather than trusting `candidate.auto_promote_allowed`, which is the only gate today (`:368-371`, `:431-434`). This closes both round-3 cases: the omitted-mark candidate (invisible to any consistency check) and the copied illegal pair.
- **The re-derivation withholds the AUTOMATIC path only, and must NOT refuse an operator-approved activation** - the round-4 [P1] correction, and the single most important constraint on this unit, because getting it wrong implements reading C, which the operator explicitly foreclosed. The existing gate is a **disjunction**: `if not candidate.auto_promote_allowed and not operator_approved: raise` (`:368` / `:431`), where `operator_approved` is a caller-supplied attestation that review occurred (`:361` / `:424`) and is the **only** route by which a non-auto-promotable candidate reaches `ACTIVE` at all - no production caller sets it today, so an unconditional refusal would have foreclosed the entire review path rather than narrowing it. The correct implementation is therefore minimal and composes with the existing API instead of replacing it: a re-derived `true` / `unknown` **overrides the candidate's `auto_promote_allowed` claim to False**, and the pre-existing disjunction then does exactly the right thing - automatic activation blocked, explicit operator approval still activating. Do **not** add a second refusal branch ahead of that check; overriding the input to it is the whole change.
- **Worst-value aggregation across multiple cited sources** (round-6 [P2]). `PromotionCandidate.source_memory_refs` is a `tuple[MemoryID, ...]` (`memory_promotion.py:217`) and both derivation paths set exactly one entry (`:644`, `memory_tool_executor.py:420`), so plurality reaches only the direct-construction surface - which is precisely surface 2, where this rule belongs and where the unit implements it. The effective provenance is `true` if **any** resolved source is `true`; else `unknown` if **any** is `unknown` or unresolvable; else `false` only when **every** cited source resolves to `false`. An implementation that gated only when all sources were risky would satisfy every other witness in this unit while auto-promoting a mixed candidate, which is exactly why the mixed-source witness below is mandatory rather than illustrative.
- **The commit must be bound to the source version the snapshot read** (round-9 [P1]; the race is **live at HEAD**, verified rather than assumed). The determination-bearing kinds are exactly the JSONL-backed ones - `EPISODIC_TURN`, `TOOL_EVENT`, `COMPACTION_EVENT` (`_JSONL_BY_KIND`, `harness-is/src/harness_is/memory_store.py:143-147`) - and for those `write_record` **appends** (`_append_jsonl`, `:432-436`, opening `"ab"`) with no dedup, skip, or error, while `_read_jsonl_record` (`:445-463`) reassigns its match on every line so the **last** one wins (`:460`). Because the envelope is hash-inert, a rewrite carrying a different `captured_cross_family` has the **same** `content_hash` and therefore the **same** `memory_id`, so the two lines collide by construction and the record's provenance silently changes. The ordering inside `_capture` widens it: `write_record` runs at `memory_capture.py:730` **before** the ledger append at `:732`, so even a capture that ultimately reports `FAILED` on an idempotency conflict has already appended its provenance line. `EPISODIC_RUN` takes the overwrite branch instead, but always lands `unknown` under the origin table, so its overwrite cannot change a gating outcome. **Obligation:** the activation write must not commit against a source whose recorded provenance changed after the snapshot; on change the invocation fails or retakes the snapshot and re-decides. **Mechanism is impl discretion** - a version/generation token carried with the snapshot, a re-check of the cited sources at commit, or a lock across the decision all discharge it. This unit deliberately prescribes none, and the impl leg must **state which it chose and why** rather than leaving it implicit. **The chosen mechanism must make verification atomic with persistence on the activation path** (round-10 [P1]): a re-check that can be separated from the write it authorizes is still a TOCTOU window, and the store exposes reads and writes separately with locks covering only individual writes, so atomicity does not come for free. The witness must exercise the **between-recheck-and-write** interleaving specifically, not only the between-snapshot-and-recheck one.
- **Fail closed on an unresolvable source**, which is a real branch and not a formality: `source_memory_refs` may be empty on a hand-built candidate; the record kind must be recovered by parsing the `memory_id` (`mem:{tier}:{kind}:{hex}`, `harness-is/src/harness_is/memory_record_envelope.py:222`); and an episodic source additionally needs a `run_id`, since `_required_run_id` **raises** without one (`harness-is/src/harness_is/memory_store.py:353-356`) - the service holds only an optional `self._run_id` (`memory_promotion.py:310` / `:321`), which may be absent or may belong to a different run than the source record. Any of those, plus an unreadable record, is treated exactly as `unknown`: mark carried, automatic activation withheld, operator-approved path open.
- **ONE re-derivation per service call, carried as a frozen snapshot** (round-7 [P1]) - the constraint that makes the gate and the durable write agree by construction. As rounds 3-6 accumulated it, this unit described a re-derivation at the activation gate **and** a normalization at the durable write: two reads of the same source records. Because `captured_cross_family` is hash-inert, a record may be rewritten under the same `memory_id` between them, so the two can disagree - and the failure is concrete, not bookkeeping: `approve` could observe `false` at `memory_promotion.py:368` and admit the activation without `operator_approved`, then `_persist_decision` could observe `true` and persist the mark, writing an `ACTIVE` record that is both marked cross-family-captured and never reviewed. Required shape instead: resolve the cited source records **once** at the start of the service call, build an immutable effective-provenance result (the aggregated tri-state **plus** the normalized flag set), and thread that one value through both the gate test and `_persist_decision`. The gate becomes a **pure projection** of the snapshot - it performs no lookup of its own - and the durable write states that same snapshot's mark. This is the `B-91` frozen-decision-input idiom; do **not** implement it as two lookups plus a comparison, which detects the disagreement instead of preventing it.
- **The uniform normalization rule, stated once over EVERY durable write rather than per method** (round-4 [P2], corrected and generalized at round-5 [P2]). Any durable write taken from a candidate the service did not itself derive persists the **re-derived** mark, never the supplied one. Implement it at the **single choke point**, `_persist_decision` (`memory_promotion.py:451-513`), rather than at each caller: normalize `candidate.risk_flags` from the resolved source record(s) before `_promotion_record` builds the content, injecting the reserved flag when re-derivation yields `true` or `unknown` (including every unresolvable branch, matching the read-side `unknown` mapping - the honest durable statement is "this needs review and here is why") and stripping it when it yields `false`. Grounding the enumeration rather than trusting it: `_persist_decision` has **four** call sites, not the two or three a per-method reading suggests - `propose_for_review` (`:340`, writes `PROPOSED`), `approve` (`:378`, `ACTIVE`), **`deny` (`:402`, `DENIED`)**, and `edit_and_approve` (`:437`, `ACTIVE`). Every one of them reaches the durable carrier the round-1 fix added, so a per-method fix would have left at least one write persisting untrusted provenance - and `deny` is exactly the one an enumeration reached for casually would miss. Normalizing at the choke point covers all four by construction, and covers any future caller by the same construction. **No new spec obligation is created:** C-MEM-10 surface 2 states the rule over "every durable write taken from that candidate … whatever the resulting status" in its own words, which this bullet cites rather than duplicating. (The compaction-disposition writer is outside this rule and was checked rather than assumed: its content carries no risk flags at all.)
- **A read method on the `PromotionDecisionStore` Protocol**, which that re-derivation requires and which does not exist today: the Protocol (`memory_promotion.py:269-277`) declares only `write_record` and `append_memory_operation`, so the service literally cannot resolve a source record. Widening it is an **internal seam addition, not a public contract change** - verified, not asserted: `PromotionDecisionStore` appears **nowhere** under `design-substrate/`, so no spec declares it. The widened method is satisfied by the existing concrete store without new code, `MemoryStore.read_record(memory_id, kind, *, run_id=None, audit_mode=False)` (`harness-is/src/harness_is/memory_store.py:190-197`). Every existing test double implementing the Protocol needs the method added.
- **The reserved-flag derivation on caller-supplied input.** `_risk_flags` seeds from caller material (`flags = set(hint.risk_flags)`, `memory_promotion.py:677`) and `PromotionCandidateHint.risk_flags` is typed to the flag enum (`:193`), so admitting `cross_family_capture` to that enum makes it a **valid hint input** that would otherwise be honoured as authoritative. Any occurrence of the reserved value in hint-supplied flags is therefore **discarded and re-derived** from the source record's `captured_cross_family`, unconditionally and in both directions: a hint cannot introduce the mark on a `false` source, and cannot suppress it on a `true` / `unknown` source. Implement as an overwrite of that one flag rather than a validation refusal - a hint carrying it is not malformed, merely not authoritative. The tool path needs no equivalent today (`_promotion_risk_flags`, `memory_tool_executor.py:882-885`, derives from the source record and accepts no caller flags), and that asymmetry is recorded rather than papered over.
- The **durable carrier** for the flag, per C-MEM-10's durable-review-artifact requirement: the promotion-written record's own **content** carries the candidate's risk flags. `_semantic_record_content` (`memory_promotion.py:919-956`) and `_procedural_record_content` (`:959-989`) both currently omit them, so both gain the key; `_promotion_record` (`:815-857`) then hashes the extended content at `:842` and derives the record identity from it at `:845`. No model edit is needed - `MemoryStoreRecord.content` is an open `Mapping[str, object]` (`harness-is/src/harness_is/memory_store.py:86`). **Deliberately NOT the C-MEM-08 ledger row:** `_operation_payload` (`memory_promotion.py:515-542`) stays unchanged, because `MemoryOperationPayload` is closed (`extra="forbid", frozen=True`, `harness-is/src/harness_is/memory_operation_ledger.py:167-170`) and a field there would be the C-MEM-08 amendment this arc forswears. The consequence to accept knowingly: promotion records written after this unit lands carry one more content key and therefore a different `content_hash` and `memory_id` than they would have - forward-shape only, no existing record rewritten or moved, and no capture-path content shape touched.
- The gate is **unconditional on policy**: it is not expressed as a policy decision value, a review mode, or a confidence threshold, and it must hold even where `promotion_decision` is `PROMOTE_SEMANTIC` / `PROMOTE_PROCEDURAL` and `review_mode` is `AUTOMATIC` (the latter is already the sole production setting - `_policy_from_config` pins `review_mode=ReviewMode.AUTOMATIC` at `harness-runtime/src/harness_runtime/automatic_memory.py:555` while pinning `promotion_decision=PromotionDecision.PROPOSE_SEMANTIC` at `:542`). A gate that only holds under today's `PROPOSE_SEMANTIC` pin would be vacuous, since that pin is what makes every candidate review-required today anyway.
- Forward-only posture for records already written: **no determination is ever back-filled** - no migration turns an absent or `unknown` field into `true` or `false`. A pre-amendment record reads `unknown` and is gated on that basis. Per C-MEM-03's forward-only paragraph this is **not** a byte-stability guarantee for the serialized envelope: a redaction / tombstone / retention-expiry transition of a legacy record rebuilds its envelope (`MemoryRedactionService._transition` reads at `harness-is/src/harness_is/memory_redaction.py:184-189`, `model_copy`s at `:201-210`, and durably rewrites at `:258`) and the store's serializer calls `model_dump()` on it with defaults included (`canonicalize_memory_store_record`, `harness-is/src/harness_is/memory_store.py:327-337`, the `BaseModel` branch at `:392`), so such a transition **will** materialize an explicit `unknown` where the field was absent. That is permitted and must not be prevented: absent and explicit-`unknown` denote the identical undetermined status and gate identically. The unit must **not** introduce unset-preserving serialization to avoid it - doing so would complicate the U-MEM-26 LEGACY-REDACTION path that must stay able to redact a legacy record, for zero semantic gain.

Acceptance:

- The envelope carries `captured_cross_family` as an optional tri-state whose absent value is `unknown`; a pre-amendment serialized envelope with no such key still validates, and reads as `unknown`.
- A capture taken on a dispatch whose canonicalized `provider` family **differs** from the record's composed `scope.provider_family` lands `captured_cross_family=true`.
- A capture taken on a dispatch whose canonicalized `provider` family **equals** it lands `false`.
- A capture whose derivation inputs are undetermined lands `unknown`, in each of the four cases independently: content **not produced by a completed dispatch**; `provider=None`; an **unregistered** provider key; and a composed scope whose `provider_family` is `null`. None of the four may land `false`.
- **Content that does not derive from a completed dispatch lands `unknown` even when a same-family provider is in hand**; content that does derive from one lands a real determination **even when a harness rule did the summarizing**. Specifically: a run-start capture taken during dispatch composition lands `unknown` rather than `false`; a run-close capture lands `unknown` too, its content being run metadata; and the **production turn capture lands `false` on a same-family completed dispatch and `true` on a cross-family one, notwithstanding its `SummarySource.HARNESS_RULE` label**. The criterion is stated over content origin, not over method names and not over `summary_source`, so a writer added later inherits it.
- **The gate and every durable write of one service call consume ONE frozen provenance snapshot.** A single re-derivation per call produces the aggregated tri-state plus the normalized flag set; the gate is a pure projection of it and performs no lookup of its own. It must be impossible for a call to admit an activation on one reading and persist a different one.
- **Multi-source aggregation is worst-value.** A candidate citing sources that resolve `false` and `true` is gated; `false` and unresolvable is gated; `false` and `unknown` is gated; all-`false` is not. No aggregation may require every source to be risky before gating.
- The field is **hash-inert**: adding and populating it changes neither `content_hash` nor `memory_id` for otherwise identical content. `_record` computes `content_hash` from `content` at `memory_capture.py:1027` and `memory_id` at `:1028`, both **before** the envelope is constructed at `:1030-1044`; the store re-derives the same way (`compute_memory_content_hash(self.content)`, `harness-is/src/harness_is/memory_store.py:95`). The acceptance is that this stays true after the edit, not merely that it was true before.
- A candidate derived from a source record carrying `true` or `unknown` carries the `cross_family_capture` risk flag **and** is `review_required=True` with `auto_promote_allowed=False`, at **both** entry points, asserted on the constructed candidate.
- A candidate derived from a source record carrying `false` is unchanged from today at both entry points: no `cross_family_capture` flag, and `review_required` / `auto_promote_allowed` exactly as the pre-existing predicates compute them.
- **Flag-gate biconditionality**, at both entry points: the flag is present on a candidate if and only if that candidate is gated on the cross-family ground. The gate predicates read the derived flag set; there is no second read of `captured_cross_family` inside them, and no configuration under which flag and gate disagree.
- **The illegal pair is refused at every validating constructor.** Constructing a `PromotionCandidate` that carries `cross_family_capture` together with `auto_promote_allowed=True` (or `review_required=False`) is **refused** - by direct construction and by deserialization, including a hand-built candidate that touched neither extraction path. A legal flagged candidate (`review_required=True`, `auto_promote_allowed=False`) constructs normally, and an unflagged candidate is entirely unaffected. This criterion claims consistency at validating constructors and **nothing more**: it deliberately does not claim the pair is unreachable, since `model_copy` does not validate.
- **The activation boundary re-derives and does not trust the candidate.** For a candidate the service did not itself derive, `approve` and `edit_and_approve` resolve `source_memory_refs`, read each source record's `captured_cross_family`, and withhold **automatic** activation when any resolves to `true` or `unknown` - **irrespective of the candidate's own `risk_flags` and `auto_promote_allowed`**. The two cases this must cover, both of which every value-level check provably misses: (i) a candidate that **omits** the mark while asserting `auto_promote_allowed=True` against a `true` / `unknown` source, and (ii) a candidate carrying the illegal pair reached via `model_copy(update=...)`. Nothing is written to either store when activation is withheld.
- **Operator-approved activation still succeeds, and this criterion is non-negotiable** - it is what keeps the unit implementing the ratified reading B rather than reading C. The *same* `true` / `unknown` candidate that is refused without approval **activates to `ACTIVE`** when the call carries the explicit operator approval. The re-derivation therefore overrides `auto_promote_allowed` and lets the pre-existing disjunction decide; it must not introduce a refusal that outranks operator approval.
- **Unresolvable provenance is treated as `unknown` at that boundary**, in each of its distinct branches: empty `source_memory_refs`; a `memory_id` whose kind cannot be parsed; an episodic source with no usable `run_id`; and a reference that cannot be read. Each withholds automatic activation while leaving the operator-approved path open. A candidate whose sources all resolve to `false` auto-activates exactly as it does today - the positive control that keeps the criterion from being satisfied by refusing everything.
- **EVERY durable record written from an untrusted candidate carries a re-derived mark, not the candidate's claim** - uniformly across all four `_persist_decision` call sites, whatever status results. A hand-built candidate that **omitted** the flag against a `true` / `unknown` source produces a record whose content **carries** it; one that **spoofed** the flag against a `false` source produces a record whose content **does not**. This holds for the `PROPOSED` write, for **both** `ACTIVE` writes, and for the `DENIED` write. Every unresolvable branch carries the flag, matching the `unknown` mapping. Without this the durable artifact the R1 carrier fix exists to make auditable would be exactly as untrustworthy as the candidate that supplied it - and an operator-approved `ACTIVE` record, the longest-lived and most consequential artifact of the whole pipeline, would be the one most likely to carry a false provenance.
- **Caller-supplied `cross_family_capture` is not authoritative, in both directions.** A hint carrying the reserved flag against a source record whose `captured_cross_family` is `false` yields a candidate **without** the flag and **without** the gate; a hint omitting it against a `true` or `unknown` source yields a candidate **with** both. The hint is not rejected in either case - the flag is simply re-derived.
- **The durable review artifact carries the flag.** A gated candidate routed through `propose_for_review` (`memory_promotion.py:328-352`) produces a `PROPOSED` record whose **content** carries `cross_family_capture` among its risk flags, so an operator inspecting the durable record can see why it was held. The C-MEM-08 ledger row is unchanged, and `_operation_payload` (`:515-542`) gains no field.
- The promotion path's content extension is confined to promotion-written records. Capture-path content shapes are untouched, and no already-written record of any kind is rewritten, re-hashed, or re-identified by this unit.
- The gate holds under a `PROMOTE_SEMANTIC` policy with `ReviewMode.AUTOMATIC` - the configuration under which every other gate would allow automatic promotion - which is the only configuration that distinguishes a real gate from one made vacuous by today's `PROPOSE_SEMANTIC` pin.
- Eligibility is **preserved**, not removed: a cross-family-captured candidate that goes through review can still be approved and become an `ACTIVE` semantic or procedural record. The unit must not implement reading C, and a test must show the approval path still reaches `ACTIVE` for such a candidate.
- The pre-existing `cross_scope` risk flag is untouched and remains distinct: a candidate whose suggested scope escapes its source record's scope is still flagged `cross_scope` by `_scope_escapes_source` / `_family_escapes_source` (`memory_promotion.py:698-712` / `:715-743`), independently of `cross_family_capture`. Neither flag may be derived from the other, and a candidate may carry both.
- A legacy record written before this amendment - carrying no field - is gated as `unknown`: review-required and never auto-promotable. No determination is back-filled onto it. A durable transition of such a record (redaction / tombstone / expiry) still succeeds and may materialize an explicit `unknown`, which is accepted rather than prevented.
- No C-MEM-08 operation kind, projection, telemetry member, or ledger shape is introduced or changed. The gate reads the record's own field and performs no ledger join.
- The six U-MEM-25 closeout evidence rows that carry a `PENDING - U-MEM-27` marker at the spec-leg PR - **C-MEM-03 and C-MEM-10** in the C-MEM matrix, **R-MEM-01, R-MEM-05, R-MEM-09, and R-MEM-14** in the R-MEM matrix - are re-opened and extended to cover the v1.2 obligations (the tri-state field with its derivation rule, `unknown` semantics, hash-inertness and forward-only consequence; the cross-family-captured condition, the flag vocabulary addition, and the review-required / never-auto-promotable gate), **every one of the six `PENDING - U-MEM-27` markers is lifted**, the packet's status line and its "Version scoping - window 2 (v1.2) OPEN" paragraph are closed the way the U-MEM-26 impl leg closed window 1 (retained as historical record, relabelled CLOSED, scope advanced to spec v1.2 / plan v1.2 / U-MEM-01..27), and the closeout check is re-run green with the refreshed rows in place. The annotations themselves already exist - they landed at the spec-leg PR per the `B-86` precedent - so this criterion is a RESOLVE-and-lift obligation, not an author-them one. The unit cannot close while any row still carries a `PENDING - U-MEM-27` marker or the packet still says the v1.2 obligations are uncertified.

Verification:

- Per-arm write-side witness matrix, one test per cell, asserted on the written record's envelope: (`true`) a cross-family dispatch producing turn content; (`false`) a same-family dispatch producing turn content; (`unknown`) each of `provider=None`, an unregistered provider key, and a `null` composed `provider_family`. Five cells; a single parametrized case that collapses the three `unknown` inputs is insufficient, because each reaches the sentinel through a different authority and a fix to one can silently break another. The `true` / `false` cells must use a **content-bearing** capture, since the run kinds can no longer produce a determination.
- **Pre-dispatch witness** (round-6 [P2]): a run-start capture taken through the production composition path - where `compose_for_dispatch` writes the record before returning the context (`automatic_memory.py:232` / `:238`) - lands `unknown` **even though the selected provider matches the composed scope family**. Asserting the same-family case specifically is the point: an implementation that derived from the selected provider would land `false` here and pass a cross-family-only witness.
- **Harness-authored-content witness** (the class an event-timing rule misses): a `capture_run_close` taken **after** a completed same-family dispatch still lands `unknown`, because run-close content is run metadata deriving from no dispatch output. Paired with the `EPISODIC_RUN` overwrite witness below, which must now assert that `unknown` is what survives the overwrite - not a determination.
- **Harness-summarized-but-dispatch-derived witness pair** (round-7 [P2]) - the cells the round-6 wording would have got backwards. Driven through the production turn path, whose summarizer label is `SummarySource.HARNESS_RULE` (`automatic_memory.py:270`) while its `response_summary` derives from the actual provider response (`:269`): (a) a completed **same-family** dispatch lands `false`; (b) a completed **cross-family** dispatch lands `true`. Neither may land `unknown`. An implementation that keyed on `summary_source` passes every other witness in this matrix and fails exactly these two, which is why they are pinned separately rather than folded into the arm matrix above.
- **Single-snapshot witness** (round-7 [P1]). The honestly testable assertion, stated as such rather than as a race reproduction: a fake `PromotionDecisionStore` that **counts source-record resolutions and mutates the source's `captured_cross_family` after the first read** is used for one `approve` call; the witness asserts (i) exactly **one** resolution occurred for the decision, and (ii) the gate and the persisted mark agree with each other. **It must NOT assert that first-read-wins is the correct outcome** - that was an earlier draft's error, caught at round 9 [P1]: for a source whose provenance genuinely changed before commit, first-read-wins is precisely the defect. Pair it therefore with a **commit-binding witness**: the fake mutates the cited source's `captured_cross_family` from `false` to `true` after the snapshot but before the durable write, and the call must NOT auto-activate on the stale snapshot - it either fails or retakes the snapshot and gates. Asserting either acceptable outcome is fine; asserting a silent auto-activation is not. The mutating fake is what makes the assertion load-bearing: against a two-read implementation the counter reads 2 and the persisted mark diverges from the gate's input, and both halves fail. Repeated for `edit_and_approve`. A test that merely asserts consistent behaviour on a non-mutating store would pass against the defective shape and is explicitly not sufficient.
- Registered-key canonicalization witness: a dispatch whose `provider` is a **registered provider key** whose canonical family **equals** the record's `provider_family` lands `false`, not `true`. Without this, a raw-key-vs-value comparison would false-positive the gate on every same-family dispatch that names its provider by key - the same key-vs-value defect `_family_escapes_source` documents at `memory_promotion.py:715-743`.
- Hash-inertness witness: two records with byte-identical content and differing `captured_cross_family` values share the same `content_hash` **and** the same `memory_id`, and both pass the store's own consistency check (`memory_store.py:95-99`).
- `EPISODIC_RUN` multi-writer witness, **restated after round 6**: a run whose `capture_run_start` ran same-family and whose `capture_run_close` ran cross-family leaves the single stored run record carrying the **run-close** call's value - which under the content-provenance rule is `unknown`, since run-close content is metadata. The witness therefore asserts two things: that the surviving envelope is the one co-written with the surviving content (the mechanism), and that its value is `unknown` rather than a determination (the rule). Writing it against a `true`/`false` expectation would encode the very defect round 6 removed. The mechanism holds because `_memory_id_for` derives the `EPISODIC_RUN` `memory_id` from the `run_id` alone (`memory_capture.py:1100-1109`) and `MemoryStore.write_record` writes envelope and content together through the atomic-write branch (`memory_store.py:178-188`, `:186`, `_run_record_path` at `:290-295`).
- Read-side gate witness per entry point, kept separate: (i) the hint path, asserted on the candidate `_candidate_from_hint` returns; (ii) the tool path, asserted on the candidate `_propose_promotion` constructs. One aggregate test passes over whichever entry point is still ungated - the same layer-independence discipline U-MEM-26 applies to its three scope predicates.
- Per-arm read-side witness, at both entry points: source record `true` -> flagged and gated; `unknown` -> flagged and gated identically; `false` -> unflagged and ungated. The `unknown` arm is the load-bearing one, since a fail-open implementation that only tests `true` passes without it.
- Vacuity-defeating gate witness: under a policy resolution with `promotion_decision=PROMOTE_SEMANTIC` and `review_mode=ReviewMode.AUTOMATIC`, a `false`-provenance candidate is `auto_promote_allowed=True` while a `true`- or `unknown`-provenance candidate is `auto_promote_allowed=False`. Both halves are required: the positive control proves the test configuration really does permit automatic promotion, so the negative is the gate firing rather than the ambient `PROPOSE_SEMANTIC` pin refusing everything.
- **The same matrix under `PROMOTE_PROCEDURAL` + `AUTOMATIC` for a `PROCEDURAL_UPDATE` candidate** (round-4 [P2]): `false` auto-promotable, `true` and `unknown` not. This is not redundant with the row above, because `_auto_promote_allowed` takes a **separate branch** for that kind - `if hint.proposed_kind is PromotionCandidateKind.PROCEDURAL_UPDATE: return resolution.promotion_decision is PromotionDecision.PROMOTE_PROCEDURAL` (`memory_promotion.py:788-790`) - so a gate placed only on the semantic return at `:790` would leave cross-family **procedural** candidates auto-promoting, and the semantic-only matrix would pass throughout. Note the two entry points differ here and the witness must not assume otherwise: the tool path's `_promotion_auto_allowed` (`memory_tool_executor.py:897-903`) tests membership in `{PROMOTE_SEMANTIC, PROMOTE_PROCEDURAL}` with **no** kind branch at all, so the procedural asymmetry is hint-path-specific.
- **Eligibility-preserved witness pair, now composed with the activation-boundary re-derivation** (round-4 [P1]; the single arm this replaces was satisfiable by a unit that had not yet added re-derivation, and would have been FALSIFIED by the version that had). Both arms use the identical candidate against a source record whose `captured_cross_family` is `true`, and are repeated for `unknown`: (a) **approved arm** - the call carries the explicit operator approval and the record reaches `SemanticRecordStatus.ACTIVE`; (b) **unapproved arm** - the identical call without it is refused. This is the anti-reading-C witness: arm (a) fails if the unit refuses cross-family activation outright, and arm (b) fails if the re-derivation does not bite. Neither arm alone proves the gate - (a) alone permits a no-op gate, (b) alone permits reading C.
- Flag-independence witness: a candidate that is cross-family-captured but whose suggested scope does **not** escape its source scope carries `cross_family_capture` and **not** `cross_scope`; and the converse case carries `cross_scope` and not `cross_family_capture`. Both assertions guard against the two flags being collapsed.
- Legacy-record witness, **read arm**: a record deserialized from a pre-amendment payload with no `captured_cross_family` key reads `unknown` and is gated as such through both entry points, and is not rewritten by the read.
- Legacy-record witness, **transition arm** (the arm the read arm cannot cover): the same legacy record is **redacted** and, in a second parametrization, **tombstoned**; each transition SUCCEEDS, the transitioned record still reads `unknown`, and no `true` / `false` determination appears. The witness asserts the materialized-`unknown` outcome as the EXPECTED one rather than treating it as a defect - it is what C-MEM-03's forward-only paragraph permits. **Plus the RESET arms** (round-10 [P2]), which the absent-field arm does not reach: a record carrying `true`, and a second carrying `false`, each transitioned by redaction and by tombstone, must read **`unknown`** afterwards. Grounding for why this is owed: `_replacement_content` (`harness-is/src/harness_is/memory_redaction.py:271-296`) substitutes a wholly harness-authored mapping (`status`, `redaction_kind`, `target_memory_id`, `old_content_hash`, `reason`, `replacement_summary`, a timestamp) for the record's content, while `_transition`'s `model_copy` update set carries only `updated_at` / `content_hash` / `redaction_state` - so a prior determination would survive onto content that derives from no dispatch, asserting the replacement material came from the old dispatch. Pair it with the U-MEM-26 `test_legacy_raw_key_record_stays_redactable_with_its_scope_intact` precedent, which this arm sits directly beside.
- Durable-carrier witness: the `PROPOSED` record written by `propose_for_review` for a gated candidate carries `cross_family_capture` in its persisted **content**, asserted by reading the record back from the store rather than by inspecting the in-memory candidate - the in-memory assertion is what the read-side witnesses above already cover, and it is precisely what passes while the durable carrier is missing.
- Ledger-unchanged control for that carrier: the promotion `MemoryOperationEntry` for the same decision carries no risk-flag field, confirming the obligation was discharged in content and that C-MEM-08's closed shape was not amended.
- Mutation probe on the gate: with the gate reverted, the `unknown`-arm read-side witnesses must FAIL. A green suite alone does not prove the gate is load-bearing, and the `unknown` arm is where a silently fail-open implementation hides.
- Mutation probe on the durable carrier: with the content-side risk-flag write removed, the durable-carrier witness must FAIL while every in-memory read-side witness still passes. That asymmetry is the point - it is the exact shape of the defect out-of-family review caught in this unit's first draft, and only a probe distinguishes a real carrier from a claim of one.
- **Direct-construction witness (i), the validating-constructor level:** a `PromotionCandidate` hand-built with `cross_family_capture` in `risk_flags` and `auto_promote_allowed=True` is REFUSED at construction; the same with `review_required=False` is refused; the legal flagged shape constructs. This witness must not route through `_candidate_from_hint` or `_propose_promotion` - constructing the model directly is the whole point, since that is the surface an integration reaches through the `harness_runtime` export (`__init__.py:106`).
- **Activation-boundary witness (ii), the copied illegal pair:** a candidate carrying the flag but asserting auto-promotability, reached by `model_copy(update=...)` - the route that provably survives the validator (probed at Pydantic 2.13.4) and is already used on this model at `memory_compaction_safety.py:288-292` - is REFUSED by `approve` and by `edit_and_approve`, with neither the record store nor the memory-operation ledger written. This witness **deliberately constructs a value the validator would reject**, which is coherent only because the unrepresentability claim is scoped to validating constructors; an absolute claim would make this witness unsatisfiable, and reconciling that contradiction is what Codex round 3 [P1-b] forced.
- **Activation-boundary witness (iii), the OMITTED mark - the case no value-level check can catch:** a candidate that carries **no** `cross_family_capture` flag, is internally consistent, and asserts `auto_promote_allowed=True`, whose `source_memory_refs` name a stored record with `captured_cross_family=true`, is REFUSED by `approve`. Repeated for an `unknown` source. Witness (i) passes this candidate by construction and so does every consistency check, so this arm is the only proof the activation boundary re-derives rather than inspects - it is the direct witness for Codex round 3 [P1-a].
- **Activation-boundary positive control:** the same candidate shape whose sources all resolve to `false` AUTO-ACTIVATES normally, with no operator approval supplied. Without it, witnesses (ii) and (iii) are satisfiable by a boundary that refuses everything.
- **Mixed-source witnesses** (round-6 [P2]), each a hand-built candidate citing two source records: (a) one `false` + one `true` is gated; (b) one `false` + one **unresolvable** is gated; (c) one `false` + one `unknown` is gated. The all-`false` positive control above is the fourth cell and stays unchanged. Arms (a)-(c) each fail against an implementation that gates only when *every* source is risky - which is a reading of "read each source record" that no other witness in this unit excludes.
- **Durable-proposal normalization witnesses, both directions** (round-4 [P2]): a hand-built candidate that **omits** `cross_family_capture` against a `true` source produces a `PROPOSED` record whose persisted content **carries** the flag; one that **spoofs** the flag against a `false` source produces a record whose content **omits** it. Asserted by reading the record back from the store, not on the in-memory candidate. Repeated for an `unknown` source and for one unresolvable branch, both of which must carry the flag.
- **ACTIVE-record persistence witnesses, both directions** (round-5 [P2]) - the arm the proposal witness above does **not** reach, since it exercises a different `_persist_decision` caller. (a) **Spoof arm:** a hand-built candidate that spoofs `cross_family_capture` against a `false` source, activated via `approve`, produces an `ACTIVE` record whose persisted content **omits** the flag - a false provenance must not become durable on the pipeline's longest-lived artifact. (b) **Omitted arm:** a candidate that omits the flag against a `true` source, activated via `approve` **with the explicit operator approval**, produces an `ACTIVE` record whose persisted content **carries** it. Arm (b) is doing double duty and both halves matter: it proves the normalization reaches the activation write, and it documents that an **operator-approved cross-family record stays auditable as cross-family downstream** - which is the entire purpose of the durable carrier, since approval records a decision to accept the provenance, not a decision to forget it. Both arms repeated through `edit_and_approve`, which is a separate call site (`:437`) and can regress independently.
- **DENIED-record persistence witness** (round-5, the call site codex's own enumeration missed): a hand-built candidate with a spoofed flag against a `false` source, passed to `deny`, produces a `DENIED` record whose content **omits** the flag. One arm suffices here - the point is that the choke-point normalization covers this caller too, which a per-method fix would not have.
- **Fail-closed witnesses at the activation boundary, one per branch:** empty `source_memory_refs`; a `memory_id` whose kind cannot be parsed; an episodic source with no usable `run_id` (the `_required_run_id` raise at `memory_store.py:353-356`); and an unreadable / absent source record. Each yields review-required, not activation. Kept per-branch rather than aggregated, because a single catch-all `except` would satisfy one aggregate test while leaving the others silently unhandled.
- **Reserved-flag witness, spoof arm:** a stored hint whose `risk_flags` already contains `cross_family_capture`, against a source record whose `captured_cross_family` is `false`, yields a candidate carrying **neither** the flag nor the gate - the caller-supplied value is discarded, not honoured. Without this the flag is caller-writable and the whole single-authority claim is void.
- **Reserved-flag witness, suppression arm:** a stored hint whose `risk_flags` omits `cross_family_capture`, against a source record whose `captured_cross_family` is `true`, yields a candidate carrying **both**. Repeated for an `unknown` source. Both arms are required: an implementation that only strips, or only adds, satisfies one and fails the other.
- Re-run of the memory closeout check with all six refreshed evidence rows (C-MEM-03 / C-MEM-10 and R-MEM-01 / R-MEM-05 / R-MEM-09 / R-MEM-14), every `PENDING - U-MEM-27` marker lifted, and the packet's window-2 version-scoping paragraph closed to v1.2.

Out of scope for this unit:

- Any **family-discriminating** promotion policy - one that treats a local-open-weight fallback leg differently from a remote one. The field answers present/absent only, per the C-MEM-03 stated bound; such a policy needs a separate family-valued amendment with its own value domain.
- **Aggregate-run** provenance ("was any leg of this run cross-family"), which no per-record envelope field can represent. It would require the C-MEM-08 ledger join the spec v1.2 explicitly declines to mandate.
- Any back-fill or migration of the pre-amendment corpus. It reads `unknown` by construction and is gated on that basis; back-filling it would be the ledger-join option run offline, which is not this unit.

## 6. Required review gates

Before implementation starts:

- Review this design packet for consistency with ADR-F2, ADR-D3, C-IS-02, C-AS-13, C-AS-14 §14.7, C-RT-22, and the resolved H_T-CP-16 memory lineage.
- Confirm no existing roadmap artifact already supersedes the memory substrate packet.
- Confirm operator acceptance of the provider-neutral architecture and policy-gated promotion/injection behavior.

During implementation:

- Run narrow checks after each unit.
- Run cross-axis compatibility checks after every unit that changes a public contract.
- Run out-of-family review at each major group boundary: foundational store, retrieval/policy, provider access, CLI/engine durability, final full layer.

Before completion:

- Run the full local verification suite.
- Run credential-gated live checks only with explicit operator authorization.
- Run closeout and report all warnings.
- Produce a final R-MEM and C-MEM coverage matrix.

## 7. Grouping for PR execution

The units may land as multiple PRs if each PR is internally complete and does not claim full-layer completion early.

Recommended PR groups:

| Group | Units | Purpose |
|---|---|---|
| G1 | U-MEM-01 through U-MEM-06 | Canonical schemas, path registry, policy, store, ledger. U-MEM-05 schema can land port-free; external CLI identity mapping evidence is port-gated. |
| G2 | U-MEM-07 through U-MEM-11 | Capture, promotion, retrieval, packet assembly. |
| G3 | U-MEM-12 through U-MEM-17 | Provider access modes, standard tools, prompt fallback, Anthropic adapter. External CLI route branches of U-MEM-12 and U-MEM-14 are port-gated. |
| G4 | U-MEM-18 through U-MEM-22 | CLI profiles, engine durability, compaction safety, redaction, observability. Requires landed external CLI routing before CLI-profile completion claims. |
| G5 | U-MEM-23 through U-MEM-25 | Migration, end-to-end verification, documentation, final evidence. |
| G6 | U-MEM-26 | Run-level memory scope keying and cross-family tool withholding. Conformance repair against the cleared threat-model scope invariant; lands after the `B-86` spec leg. |
| G7 | U-MEM-27 | Cross-family-captured promotion gate. Lands after the `B-92` spec leg and after G6, whose composed-scope writer repair is what makes the provenance comparison meaningful. |

No group may be described as an MVP. Groups are review boundaries only.

## 8. Risk controls

| Risk | Control |
|---|---|
| Silent behavior change in no-memory runs | U-MEM-04 default-disabled policy preserves current behavior unless memory is enabled. |
| Provider-native memory bypasses policy | U-MEM-17 maps native operations through canonical policy and ledger. |
| Semantic preference pollution | U-MEM-06 and U-MEM-09 require evidence, confidence, scope, and injection policy. |
| Compaction loses facts | U-MEM-20 blocks compaction until candidate disposition is durable. |
| Retrieval becomes nondeterministic | U-MEM-10 and U-MEM-11 pin index version, request hash, selected refs, and packet hash. |
| CLI silos fragment memory | U-MEM-18 treats CLI profiles as provenance and import policy, not separate canonical stores. |
| Redaction rewrites history | U-MEM-21 uses tombstone and redaction events. |
| Engine replay sees different memory | U-MEM-19 records store version or packet hash at replay/checkpoint boundaries. |

## 9. Completion definition

The memory substrate is complete when:

- U-MEM-01 through U-MEM-27 are implemented.
- Every R-MEM requirement maps to implementation and verification evidence.
- Every C-MEM contract maps to implementation and verification evidence.
- Anthropic native memory, standard memory tools, and prompt packet fallback all operate over the same canonical store.
- Generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom CLI profiles all resolve and are recorded.
- Compaction safety is enforced.
- Redaction and retention are durable.
- Engine-class memory durability is represented.
- Closeout and out-of-family review are complete or explicitly blocked by a registered external dependency with a deterministic absence probe.
