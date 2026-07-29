# Specification - Memory Substrate v1

## Status

Proposed.

Date: 2026-07-01

Authority chain: ADR-F2, ADR-D3, PRD v1.2 R-MEM family, and Memory Substrate Design v1.

This specification introduces the `C-MEM-*` contract family for the full provider-neutral memory layer. It is additive to the existing Information Substrate, Action Surface, Control Plane, Operational Discipline, and Runtime specifications.

Revision: v1 -> v1.1 (`B-86` spec-leg apply pass - C-MEM-03 `provider_family` value domain, `null` semantics, and derivation rule; C-MEM-13 cross-family withholding invariant; C-MEM-14 exposure qualification. The Memory threat model is unchanged. Detail at the change-note below.)

Revision date: 2026-07-28

Revision: v1.1 -> v1.2 (`B-92` spec-leg apply pass - C-MEM-10 cross-family-captured promotion candidates carry a risk flag AND a review gate (RATIFIED reading B); C-MEM-03 gains the tri-state `MemoryRecordEnvelope.captured_cross_family` provenance field that makes that gate decidable. The Memory threat model is unchanged. Detail at the change-note below.)

Revision date: 2026-07-29

## Change-note (v1.1 -> v1.2)

**Trigger and back-flow authority.** RATIFIED Class 1 fork `.harness/class_1_fork_c_mem_10_cross_family_promotion_eligibility.md` (filed 2026-07-29, nine out-of-family review rounds, SOUNDNESS EXIT declared at R9; register row `B-92` at `.harness/forward-register.yaml`, status `design_substrate_gated` **at the fork filing** - historical-at-filing, not live: the row transits to `open` within this same PR, since this spec leg is what clears the design gate. Consult the register for live status). The fork discharges the open question v1.1 carried at its own change-note paragraph "Named open question carried forward, not discharged." - whether records captured during a cross-family fallback leg are promotion-eligible under C-MEM-10 - and the operator RATIFIED **reading B (flag + gate)** on 2026-07-29 via `AskUserQuestion` (fork §11). Reading C (outright refusal) is foreclosed; reading A (status quo made explicit) is not adopted as the permanent posture; the **A-as-recorded-interim** variant was **not** selected, so its T1 / T2 / T3 interim-ending triggers are not owed. Amendment 1 below is the mechanical apply of that ratified position against the fork's §6 reading-B drafting-target row.

**Amendment 1 - C-MEM-10: NEW subsection "Cross-family-captured promotion candidates" plus two appended invariants.** (a) The condition: a promotion candidate is *cross-family-captured* when the source record it derives from was captured on a fallback leg whose dispatched provider family differed from the record's own `MemoryScope.provider_family`, or when that relation cannot be determined from the record. (b) The mark: such a candidate carries the risk-flag value `cross_family_capture`. This is a **vocabulary addition, not a schema widening** - the `PromotionCandidate.risk_flags` field declared in this contract is an open `list<string>`, so a new value needs no field, type, or shape change here; only the implementation-side flag enumeration is closed, and admitting the value there is the plan leg's work, not a contract change. (c) The **gate**, which is the load-bearing half: a cross-family-captured candidate is **review-required and is never auto-promotable**, under every policy configuration. The gate is stated in the Contract *and* as an invariant deliberately. A flag alone would land inert: the fork's §2 grounding establishes that at the filing HEAD no promotion predicate reads `risk_flags` at all, so a mark without an obligation attached to it is advisory metadata that is carried, persisted, and never acted on. Eligibility is otherwise **preserved** - a cross-family-captured candidate may still be promoted, by review; what is removed is *silent* auto-promotion.

**Amendment 2 - C-MEM-03: NEW field `MemoryRecordEnvelope.captured_cross_family`, a tri-state, plus its NEW subsection and six appended invariants.** This is the discriminator amendment 1's gate requires, and it is the fork's Q2 - a question the fork deliberately left **leveled** and routed to this leg (fork §8 item 2, §10's cap, §11). The requirement is stated first and the mechanism chosen from it, per the fork's own instruction that the requirement is what decides the option.

**The requirement C-MEM-10 needs, stated before the pick.** The ratified position is a present/absent mark plus a boolean gate, and both consumers are per-record: a candidate is derived from **one** stored source record (`_candidate_from_hint(record, hint, resolution)`, `harness-runtime/src/harness_runtime/memory_promotion.py:616-655`, which sets `source_memory_refs=(record.envelope.memory_id,)` at `:644`; and `MemoryToolExecutor._propose_promotion`, `harness-runtime/src/harness_runtime/memory_tool_executor.py:399-435`, which reads one source record by reference at `:408-411`). The gate's two outputs are booleans on that candidate (`review_required` / `auto_promote_allowed`, `memory_promotion.py:226-227`), and the mark's carrier is a flag vocabulary with no payload (`PromotionRiskFlag`, `:80-86`; `risk_flags: list<string>` in this spec's C-MEM-10 Contract). Nothing in either path consults a run-level aggregate. So the requirement is **stored-version provenance, present/absent**: *was the content of the record I am about to promote produced on a leg whose dispatched provider family differed from that record's own partition family - or is that undeterminable?* It is **not** provenance *by family* (the ratified position draws no distinction between one cross-family leg and another; a family-discriminating policy would be a later, separate amendment) and it is **not** *aggregate-run* provenance ("did any leg of this run run cross-family"), which would be strictly **broader** than what was ratified - it would flag records the run's own primary produced, and no consumer above reads a run.

**The pick that requirement selects: the fork's `(i-envelope-bool)`, re-derived against this leg's own HEAD `57f840b6` per the fork §10 cap.** A tri-state field on `MemoryRecordEnvelope` answers exactly the stored-version present/absent question and nothing more, and on this requirement it is the cheapest of the fork's three columns and the most reliable: the field ships **inside the version it describes**, co-written with the content it qualifies, so it cannot go stale relative to that content - whereas the alternative C-MEM-08 ledger join can match a correctly-qualified single row that describes a *superseded* version of a multi-writer record. The fork's own leveling rested on three axes where the ledger join wins (already-written records, zero write-side reach, aggregate-run provenance); the first two are costs this amendment accepts and states below, and the third is not the requirement. The `(i-content)` placement variant is rejected: content is the hash input, so a content field would move `content_hash` and, through it, the `memory_id` of every **content-addressed** kind - verified at HEAD, `_record` computes `content_hash` from `content` at `harness-runtime/src/harness_runtime/memory_capture.py:1027` and `memory_id` at `:1028`, **before** constructing the envelope around them at `:1030-1044`, and the store re-derives the same way (`compute_memory_content_hash(self.content)`, `harness-is/src/harness_is/memory_store.py:95`). The claim is qualified rather than universal, because the run kind is the standing exception: `_memory_id_for` (`memory_capture.py:1100-1109`) hashes the `run_id` alone for `EPISODIC_RUN` (`:1106-1108`) and ignores the content hash entirely, so a content field would move identity for every kind **except** that one. The qualification does not weaken the rejection - moving most identities is disqualifying on its own - and it leaves the hash-inert conclusion for the **envelope** field untouched and universal, since the envelope is an input to neither derivation on any kind.

**What amendment 2 costs, stated rather than implied. This is a closed-schema amendment, and it reverses v1.1's own zero-new-field posture one delta later.** v1.1's "Sections preserved verbatim at v1.1." paragraph reads *"Zero new record type, zero new field, zero new enum member, zero change to any ledger, packet, or telemetry shape."* v1.2 adds exactly one field, to exactly one record type, and says so plainly: the `MemoryRecordEnvelope` block in the C-MEM-03 Contract - byte-unchanged at v1.1 - gains `captured_cross_family`. At the implementation altitude the carrier is a closed model (`MemoryRecordEnvelope` declares `model_config = ConfigDict(extra="forbid", frozen=True)`, `harness-is/src/harness_is/memory_record_envelope.py:129`), so this is a real field addition and not an open-map extension. Two consequences follow and are stated in the new subsection: the field is **optional with `unknown` as its absent value**, so the other three envelope construction sites (`memory_promotion.py:844`, `lifecycle/native_memory_adapter.py:463`, `memory_compaction_safety.py:327`) and every pre-amendment serialized envelope still validate; and the field is **forward-only** - records written before this amendment carry no field, read as `unknown`, and are not rewritten or back-filled. No ledger, packet, or telemetry shape changes.

**The tri-state is a contract obligation, not a nicety.** The writer cannot always determine the predicate, and recording `false` where no determination was made is the exact permissive-by-silence defect this delta exists to close. Three inputs can be absent at HEAD: `provider` is `str | None` at every capture signature (`memory_capture.py:302` / `:347` / `:396`); the family authority returns `None` for an **unregistered** key and its own contract requires scope-boundary callers to fail closed on it (`provider_family_for_scope_check`, `harness-runtime/src/harness_runtime/lifecycle/cross_family_cost_tag.py:101-124`); and the record's own composed `scope.provider_family` may be `null`, the C-MEM-03 unpartitioned wildcard, against which "cross-family" is undefined (`resolve_scope_family` passes a `null` family through untouched, `harness-runtime/src/harness_runtime/memory_scope_family.py:62-68`). Each case records `unknown`, and `unknown` maps to the same place amendment 1's gate sends `true` - review-required, never auto-promotable. That is the B-91 tri-state idiom, reused verbatim rather than re-invented: report a determination only when one was actually reached.

**The derivation is one central site, and this delta pins it as a rule rather than as a refactor.** The fork's R9 pass corrected an earlier claim that the field would touch every capture writer; re-verified at this leg's HEAD, all seven `capture_*` methods (`memory_capture.py:294` / `:337` / `:382` / `:439` / `:487` / `:534` / `:585`) already take `provider` and already pass it to `_capture` (`:329` / `:374` / `:431` / `:479` / `:526` / `:577` / `:623`), which threads it into `_record` (`:649-658`, the argument at `:657`). `_record` (`:1015-1046`) therefore already holds the **family-comparison** inputs - the call's raw `provider` (`:1025`) and the record's resolved scope, returned by `_scope_for_record` (called at `:1038-1042`, defined `:1048-1086`, whose output family is canonical by construction because it has already refused an out-of-domain value). The **content-origin** input is not among them and is not recoverable there: `provider` is passed identically by a pre-dispatch caller and a post-dispatch one. It is available at `_capture` (`:631`), the one method holding the per-method `event_kind`, so the derivation spans those two private methods with a fixed flow: `_capture` determines the ORIGIN DISPOSITION from `event_kind` and passes **that disposition** (not a finished tri-state) into `_record`, which computes the final value: origin gates the family comparison over the raw `provider` and the resolved scope, both of which live there. The contract states the rule and its inputs; **no public writer signature changes** (`event_kind` is already an argument of `_capture`), and the private threading between the two is the plan leg's concern.

**The `EPISODIC_RUN` multi-writer disposition, stated because it is the one kind with two writers.** One stored record per run is written by run-start and **overwritten** by run-close. The field describes **the stored version** - it is co-written with the content it qualifies, from one call, and `MemoryStore.write_record` writes envelope and content together (`memory_store.py:178-188`, the `EPISODIC_RUN` atomic-write branch at `:186` against `_run_record_path`, `:290-295`). So an overwrite **preserves** provenance for the version that is stored, which is the semantics a promotion reader needs: it is promoting that version, not the run's writer history. The field is deliberately **not** a record of which writer set it.

**The bound, stated as plainly as the capability.** `captured_cross_family` answers **present/absent only**. It cannot say *which* provider family produced the content, so it cannot support a family-discriminating promotion policy - one that treated a local-open-weight fallback leg differently from a remote one would need a second amendment carrying a family-valued field, with its own value domain and its own reconciliation against `MemoryScope.provider_family`. It also cannot answer aggregate-run provenance, which no envelope payload can represent. Neither is the requirement stated above; both are recorded so a later reader does not mistake the field for more than it is.

**The mark's durability, and the carrier chosen for it (out-of-family Codex round 1 [P1]).** A first draft of amendment 1 claimed the flag keeps the gating reason "visible and auditable downstream" while owing no durable carrier at all, and that claim was **false against the code**. Grounded at HEAD: a gated candidate takes `propose_for_review` (`memory_promotion.py:328-352`), which persists through `_persist_decision` (`:451-513`); the record content builders `_semantic_record_content` (`:919-956`) and `_procedural_record_content` (`:959-989`) write no risk flags, and the promotion ledger payload `_operation_payload` (`:515-542`) carries none either. The flag therefore died with the in-memory candidate, and an operator reading the durable `proposed` record could not see why it was held. **Carrier chosen: the promotion-written record's own content.** The two alternatives were weighed and are recorded. (1) *The C-MEM-08 ledger row* - rejected on decisive grounds: `MemoryOperationPayload` is a closed model (`model_config = ConfigDict(extra="forbid", frozen=True)`, `harness-is/src/harness_is/memory_operation_ledger.py:167-170`), so a `risk_flags` field there is exactly the C-MEM-08 closed-schema amendment this delta forswears, and the ledger row is an audit trail keyed by `action_id` rather than the artifact a reviewer reads. (2) *Reusing the existing free-text `review_reason` content key* - available and cheaper still, but rejected as weaker: it is one unstructured string that cannot carry a flag set, and a reviewer auditing a machine-set gate should read the machine's own vocabulary. The chosen carrier needs **no model change at all** - `MemoryStoreRecord.content` is an open `Mapping[str, object]` (`harness-is/src/harness_is/memory_store.py:86`) - and it follows the existing shape of that content, which already carries `candidate_id`, `source_memory_refs`, and `review_reason` beyond the C-MEM-05 `SemanticRecord` block's declared fields. **The honest consequence, stated per the drafting instruction:** content is the hash input, so promotion records written after this amendment carry one additional content key and hash accordingly, changing what their `memory_id` would have been (`_promotion_record` derives it at `memory_promotion.py:843-845`). This is a **forward-shape change for new promotion-written records only** - no existing record is rewritten, re-hashed, or moved, and no capture-path content shape is touched. C-MEM-05's declared `SemanticRecord` block is unchanged.

**One gate authority, not two (out-of-family Codex round 1 [P2]).** A first draft of the plan leg had the four promotion decision predicates each receive the source record's provenance value directly, while the flag was derived separately from the same source - two parallel derivations of one fact, which would have left the flag advisory in practice and free to diverge from the gate under later edits. That is the precise failure amendment 1 exists to end, reintroduced one layer down. The contract now states the flag as the **single authority** and the relation as **biconditional**, and the plan leg derives the mark once and has the gate predicates consume *the flag*. The biconditional framing is the `B-91` idiom applied here: the workspace has been bitten before by a mark and its consequence being separately derived.

**The single-authority rule's own two holes, closed at out-of-family Codex round 2.** Round 1's fix created them, and both were verified against code before the contract text was written. **[P1] The biconditional bound the derivation paths, not the value.** `PromotionCandidate` and `PromotionDecisionService` are both exported (`harness-runtime/src/harness_runtime/__init__.py:106` / `:112`), and the service's activation gate is a single test of the candidate's own assertion - `if not candidate.auto_promote_allowed and not operator_approved: raise` at `memory_promotion.py:368-371`, repeated at `edit_and_approve` `:431-434`. A hand-built candidate carrying `cross_family_capture` with `auto_promote_allowed=True` therefore reached `ACTIVE` with no review, satisfying every word of the round-1 text because it never passed through either extraction path. Round 2 answered this by binding the carrier - the illegal pair rejected at construction, plus a refusal at the receiving surface. **Round 3 found that answer incoherent, and the contract text above is the reconciled version rather than a third patch layer** (see the round-3 paragraph below). What survives from round 2 is the consistency check and the empirical fact that motivated its companion: a construction-time validator is provably bypassable by `model_copy(update=...)`, which does not re-run after-validators on the project's own Pydantic (2.13.4 - probed directly, an illegal pair survived the copy), and the codebase **already** calls `candidate.model_copy(...)` on this exact model at `memory_compaction_safety.py:288-292`. **[P2] The flag was simultaneously the authority and a caller-writable input.** `_risk_flags` seeds from caller material - `flags = set(hint.risk_flags)` (`memory_promotion.py:677`) - and `PromotionCandidateHint.risk_flags` is typed to the flag enum (`:193`), so admitting the new value to that enum would have made a **stored hint** able to assert cross-family provenance about a record whose envelope says `false`, and the gate would have honoured it. The value is now **reserved to the deriving writer** with unconditional both-direction overwrite semantics. (The tool path is unaffected on this point and the asymmetry is deliberate to record: `_promotion_risk_flags` (`memory_tool_executor.py:882-885`) derives from the source record alone and accepts no caller flags, so only the hint path needed the reservation - but the rule is stated over candidate input generally, so a future caller-flag surface inherits it by construction.)

**The authority model reconciled at out-of-family Codex round 3 - an altitude correction, not a third patch.** Round 3 returned two P1 findings against round 2's carrier answer, and together they showed that answer could not be made true by adding to it. **[P1-a] The consistency check cannot close the surface it was assigned.** A directly constructed candidate may simply **omit** `cross_family_capture` while asserting `auto_promote_allowed=True` against a source record whose envelope reads `true` or `unknown`. Such a candidate is internally consistent, so the validator - which only detects a *disagreeing pair* - passes it, and the both-directions reservation does not reach it either, because that rule governs derivation from caller-supplied *flags*, and here there are none to reserve. It would activate without review. **[P1-b] The unrepresentability claim contradicted the arc's own witnesses.** Round 2's text said no constructor "derived, hand-built, deserialized, or **copied**" could produce the illegal pair, while the same arc's verification deliberately *produces* one through `model_copy` in order to prove the service refuses it. Both cannot hold: `model_copy(update=...)` bypasses validators **by design**, and no in-model mechanism closes it without fighting the framework's frozen-copy semantics. **The reconciliation, stated once above rather than layered:** two surfaces with different authority - derivation (derive once, consume the mark) and **activation** (never trust the carrier; re-derive the condition from the stored source records the candidate cites; unresolvable source fails closed to review-required). The consistency check is demoted to exactly what Pydantic provides - a guarantee at every *validating* constructor, explicitly **not** a claim of unreachability - and the copy route's non-validating nature is recorded as one of the two reasons the activation surface, not the value, carries the obligation. The apparent tension with the single-authority rule is addressed in the contract text directly: that rule forbids two derivations *at one surface*, whereas this is one derivation at each of two *trust boundaries*, which is the earliest-gate / authority-mirror discipline rather than a parallel derivation.

**The activation surface corrected at out-of-family Codex round 4 - the round-3 text had drifted into the foreclosed reading.** Round 3's surface-2 paragraph said a re-derived `true` or `unknown` gates activation, without distinguishing the automatic path from the reviewed one. Read plainly, that **refuses** such a candidate outright - reading C, which the operator explicitly foreclosed at ratification, and which the eligibility-preserved paragraph of this very subsection contradicts. The grounding makes the severity concrete: the promotion service's activation gate is a **disjunction** over the candidate's own auto-promotability and an explicit operator approval (`memory_promotion.py:368` and `:431`, the parameter at `:361` and `:424`), and that approval is the **only** mechanism by which a non-auto-promotable candidate can ever become active. An unconditional refusal therefore would not have narrowed the review path - it would have removed it. The contract now says exactly what the re-derivation withholds: **the automatic path only**, with the operator-approved activation preserved *because* routing to review is the whole of what this rule asks for, and an approval is that review having happened. Round 4 also extended surface 2 to the **durable proposal** path - a hand-built candidate could otherwise persist an omitted or spoofed mark into the very artifact the durable-carrier rule exists to make auditable - which needed no new contract text, since surface 2 is written over any candidate "the promotion surface did not itself derive" and the persistence path is one.

**And generalized at round 5, which found that extension still too narrow.** Naming the proposal path specifically left the **activation** writes stating whatever provenance the candidate asserted, so an operator-approved active record - the longest-lived artifact this pipeline produces - could carry a false one. The obligation is now stated as **uniform over every durable write** taken from such a candidate, whatever status results: activation, proposal, and denial alike persist the re-derived mark. That framing is deliberate rather than stylistic. The per-event enumerations this subsection went through twice were each incomplete, and a contract that lists events will keep being one write behind the implementation; a contract that states the rule over *any* durable write cannot be. Note the consequence for the approved case, which is the point of the carrier rather than an edge of it: an operator-approved cross-family-captured record stays **marked** as cross-family-captured, because an approval records a decision to accept that provenance, not a decision to erase it.

**Out-of-family Codex round 6 - two findings applied, one DECLINED on the record.** **[P2, applied] The derivation rule gave a determination to content no dispatch produced.** The pipeline calls the run-start capture from inside the dispatch-composition step, *before* any provider call, passing the *selected* provider; a same-family selection therefore recorded `false` for content that no dispatch had produced - a category error against this field's own definition, since `false` means an equality that was tested and held. Grounding the fix widened it beyond the reported case and produced a cleaner cut than an event-name rule: classifying all seven capture writers by their **content** shows the run-close writer is post-dispatch in *timing* yet its content is also pure run metadata (identifiers, engine class, CLI profile, provider route, timestamps, close status - and no summary field of any kind), so an event-timing rule would have handed it a determination just as wrongly. The contract therefore keys on **content provenance**: a determination only where the stored content was produced by a completed provider dispatch, `unknown` otherwise, which covers pre-dispatch writes, run-lifecycle metadata, and `harness_rule` summaries under one rule that names no method and cannot fall behind the implementation - the same lesson round 5 applied to durable writes. **[P2, applied] Multi-source aggregation was undefined.** A candidate may cite several source records, and nothing said how their values combine, so an implementation gating only when *every* source was risky would have satisfied every stated witness while auto-promoting a mixed candidate. The rule is now the forced fail-closed one: worst value across sources, `false` only when all resolve `false`. Grounding confirms plurality reaches only the direct-construction surface - both derivation paths set exactly one reference - so the rule is stated at surface 2 where it applies and is deliberately not duplicated at derivation.

**[P2, DECLINED - recorded rather than absorbed.]** Round 6 also asked that the operator-approval bypass be bound to a *verified* operator identity or a durable approval artifact, on the ground that a direct integration can self-attest `operator_approved` under a non-operator actor. **The finding is factually correct and the amendment is still declined, for a threat-model reason rather than a convenience one.** This contract's trust boundary is stated at the Memory threat model §Threats opener - *"The memory substrate treats model-authored and external CLI-authored memory as untrusted until policy promotes it."* - which makes the untrusted party the **author of the content**, not an in-process caller of the harness's own service. A caller able to invoke that service with a self-attested approval already holds the authority to write a canonical record directly, so binding this one boolean buys no protection against that caller class while importing an identity-verification mechanism from a surface this delta does not own: review is C-MEM-10's Pipeline step 3 and the operational-discipline HITL contracts, and the strongest identity claim anywhere in this contract family is that operator-direct preferences be *distinguishable* from inferred ones - a labelling obligation, never an authentication one. Amending here would put a verification requirement in the promotion contract while the review contract that should define it says nothing, which is the inverted-layer defect this workspace has repaired before. **Recorded as a forward question rather than closed:** whether an approval attestation must be *authentic*, and what artifact would evidence it, is a review-surface question that a future HITL-binding amendment may take up on its own authority; it is visible here so it is not lost, and it is not silently absorbed into a promotion-provenance delta.

**Out-of-family Codex round 10 - four findings: three applied, and one answered at property altitude with its machinery demand routed to the implementation leg.** **[P1, answered at altitude] The commit-binding property needed its force stated, and its scope justified.** The round-9 text left two things implicit. First, atomicity: a re-check that can be separated from the write it authorizes is still a window, and the store exposes reads and writes separately with locks covering individual writes only - so the contract now says the property **binds the commit itself**, conformance is judged on the outcome rather than on the presence of a verification step, and no interleaving may exist in which a commit lands against a superseded source. The demanded apparatus - a compare-and-set, generation check, lock, or transaction spanning validation and persistence - remains **implementation discretion by design**, which is the same disposition round 9 took and which this leg does not revisit: a doc-only spec leg that prescribed a concurrency mechanism would be specifying an implementation, and the property is what conformance can actually be judged against. Second, scope: the binding attaches to **activation** rather than to every durable write, and that is now stated as a decision with its reasoning - a proposal or denial persists the snapshot's honestly-read provenance, is stale-but-gated rather than stale-and-injectable if the source is superseded, and self-corrects at the next surface-2 invocation, so only a stale `false` reaching automatic activation crosses this contract's gate. **[P2, applied] Origin is a per-INVOCATION property, and `event_kind` is only a coarse method-level proxy for it.** The round-7 rule keyed the writer's signal to the capturing caller's knowledge, but this subsection's own practical-reach sentence then lumped failure captures in with turn and tool captures as determination-bearing - and a failure observation may describe a dispatch that produced **no** output, for which a selected same-family provider would have stored `false` against content nothing produced. The rule now says the signal is the caller's knowledge **on this invocation**; a method-level mapping is sound only where every production invocation of that method shares one origin; and a method whose invocations can differ either carries an explicit per-call origin value or records `unknown` for the invocations it cannot distinguish. **[P2, applied] A transition that replaces the stored content must reset the field.** Redaction, tombstone, and retention expiry substitute a wholly harness-authored mapping for the record's content while preserving the envelope's existing value, so a prior `true` or `false` would assert that the replacement material came from the original dispatch. Such a transition now writes `unknown` for the resulting version whatever the prior value was - the converse of the no-back-fill rule rather than a conflict with it, since that rule forbids manufacturing a determination and this discards one that no longer describes the content. **[P2, applied] R-MEM-14 coverage.** The unit adds the operator review gate and the durable flag recording why a proposal was held, which is squarely R-MEM-14's review-of-pending-promotions obligation; the coverage map and the closeout annotation set both gain it, taking the pending-marker set from five rows to six.

**Review-time inventory and SOUNDNESS EXIT on the activation-race surface (PD-9).** Four rounds have now narrowed one race on the activation surface - R3 established the durable carrier, R7 the single frozen snapshot, R9 the commit-binding property, R10 its atomicity force and the non-active-write disposition - and **each finding was a consequence of the previous fix rather than a defect in the premise**. Across all four, nothing invalidated what the delta actually commits to: the ratified flag-plus-gate reading, the tri-state with fail-closed `unknown`, the two-surface authority model, or the durable carrier. What moved each time was the precision of one property. That is the non-convergent-mechanics signature the `B-92` fork documented on its own Q2 comparison and closed under the same discipline, and this subsection closes on the same terms. **Settled at contract altitude:** the commit-binding property, its force (a verification separable from the persistence it authorizes does not discharge it - conformance is judged on the outcome), the reason it attaches to activation rather than to every durable write (non-active outcomes are stale-but-gated and self-correct at the next surface-2 invocation; only stale-`false`-to-automatic-activation crosses the gate), and the explicit refusal to prescribe machinery. **Routed to the implementation leg by rule:** the mechanism choice (compare-and-set, generation token, lock, transaction), how atomicity is achieved for it, and any interleaving refinement below the property - all of which U-MEM-27 must resolve and **state**, against its own HEAD, exactly as the derivation-mechanics cap already requires for call sites. **The exception that reopens this delta** is unchanged in kind from the fork's own: a finding that invalidates a ratified reading, the gate obligation itself, or the two-surface authority model. A further finding that the property needs a *different mechanism* is not such a finding, and belongs to the leg that builds it.

**Out-of-family Codex round 9 - three findings, all applied; the P1 is a genuine bound rather than another lap of the same chain.** **[P1] The snapshot did not bind the decision to a source VERSION.** Round 7's one-read rule makes the gate and the durable write agree with each other, which does not stop them agreeing on a version the store has since superseded. Reachability was grounded at HEAD before any contract text was written, and the race is **live**: the determination-bearing kinds are exactly the JSONL-backed ones (`EPISODIC_TURN`, `TOOL_EVENT`, `COMPACTION_EVENT` - `_JSONL_BY_KIND`, `harness-is/src/harness_is/memory_store.py:143-147`); for those `write_record` **appends** with no dedup, skip, or error (`_append_jsonl`, `:432-436`); and `_read_jsonl_record` (`:445-463`) reassigns its match on every line, so the **last** wins (`:460`). Because this field is hash-inert, a rewrite carrying different provenance keeps the same `content_hash` and hence the same `memory_id`, so the lines collide by construction and provenance changes silently. The capture ordering widens it further - `write_record` at `harness-runtime/src/harness_runtime/memory_capture.py:730` precedes the ledger append at `:732`, so even a capture reporting `FAILED` on an idempotency conflict has already appended its line. (`EPISODIC_RUN` overwrites rather than appends, but always lands `unknown` under the origin rule, so its overwrite cannot change a gating outcome.) The contract therefore states the obligation **at the commit**: an activation must not commit against a source whose recorded provenance changed since the snapshot, and on change the invocation fails or retakes the snapshot. **Mechanism is left to implementation discretion by design** - version token, re-check at commit, or lock - because the honest requirement is the property, not the machinery, and this doc-only leg prescribes no concurrency apparatus. The round-7 mutating-store witness, which had explicitly blessed first-read-wins, is corrected: it may assert one resolution and gate/write agreement, but a paired commit-binding witness now forbids silent auto-activation when the cited source's provenance changes before the write. **[P2] The derivation flow was stated two incompatible ways.** One bullet allowed the comparison to be combined at `_capture`; another required `_capture` to produce the finished tri-state - impossible together, since `event_kind` exists only at `_capture` and the resolved scope only at `_record`. One flow is now stated identically on all seven surfaces, and the impl-discretion clause is narrowed to the private parameter *shape* rather than to where the final value is computed. **[P2] A stale absolute in the closeout packet.** Its window-1 closure sentence claimed no matrix row carries a `PENDING` marker, which the five `PENDING - U-MEM-27` rows contradict; qualified to `PENDING - U-MEM-26` so the window-1 claim stays true while window 2 is open.

**Out-of-family Codex round 8 - two findings, both applied.** **[P2] The obligations above referenced fields the contract had never declared.** Surface 2 requires a promotion surface to re-read "the stored source records the candidate cites" and to constrain the pair "carries the mark while asserting auto-promotability" - but the `PromotionCandidate` block declared only `source_refs`, with no storage reference to re-read and no representation of the gate booleans being constrained. A conforming external candidate therefore could not identify the records to resolve nor express the state the invariants govern, which makes an obligation stated over undeclared fields incoherent. The block now declares three further fields: `source_memory_refs: list<memory_id>`, `review_required: bool`, and `auto_promote_allowed: bool`. **This DECLARES existing reality rather than widening the contract** - the implementation model has carried all three since before this delta (`harness-runtime/src/harness_runtime/memory_promotion.py:217`, `:226`, `:227`), and every obligation added across rounds 1-7 already depended on them; what was missing was the declaration, not the capability. No existing field is removed, retyped, or reordered. **[P2] One derivation site, stated consistently everywhere.** Two plan bullets had come to give mutually exclusive instructions - one placing the derivation inside `_record` "which already holds both inputs", the other establishing that the content-origin signal is not available there - and the stale direction had also propagated to both clearance markers, the register, and the root `CLAUDE.md` pointer row. Following the stale wording would classify pre-dispatch and run-lifecycle captures from `provider` alone, which C-MEM-03 forbids. Every surface now states the same origin-aware shape: origin determined at `_capture` from the per-method `event_kind`, the family comparison at `_record` from `provider` plus the resolved scope, origin gating the comparison, the private threading between them left to implementation discretion, and no public writer signature change.

**Out-of-family Codex round 7 - two findings, both applied.** **[P1] Two reads where there must be one.** The surface-2 obligation, as rounds 3 through 6 had accumulated it, described a re-derivation at the gate *and* a normalization at the durable write. Because this field is hash-inert, a record may legitimately be rewritten under the same identity between those two reads, so the two could disagree - and the specific failure is not hypothetical bookkeeping: a gate could observe `false` and admit an activation without operator approval, after which the write could observe `true` and persist the mark, yielding an `ACTIVE` record that is simultaneously marked cross-family-captured and never reviewed. That is precisely what this subsection's own gate invariant forbids. The contract now specifies **one re-derivation per surface invocation, producing a frozen snapshot** that the decision and every durable write of that invocation consume, with the decision stated as a *pure projection* of it - the `B-91` frozen-decision-input idiom, which this workspace already uses for exactly this class of disagreement. The race is removed structurally; nothing is left to a caution. **[P2] Content origin conflated with summarization mechanism.** Round 6's rule said a `harness_rule` summary is harness-authored text and therefore undetermined. Grounding the production turn-capture path shows that is wrong in the most common case: the runtime computes the stored `response_summary` **from the actual provider response** and labels the summarizer `harness_rule`, so round 6's rule would have marked every production turn capture `unknown` - including completed same-family dispatches - contradicting the very next paragraph's claim that content-bearing captures receive determinations. The rule is restated over **content origin**: material deriving from a completed dispatch's output carries a determination *regardless of which mechanism summarized it*, `summary_source` is explicitly disqualified as the discriminator, and the writer's signal is the capturing caller's own knowledge of holding a completed dispatch result. Run-lifecycle metadata still records `unknown` because it derives from no dispatch output at any time.

**Review-time inventory and the cap on this surface (PD-9).** Round 7 is the **third** consecutive correction to the *mechanics* of the derivation rule - round 6 moved it from event-timing to content, round 7 from summarization-mechanism to content origin - which is the non-convergent-mechanics signature the `B-92` fork itself documented on its Q2 comparison and capped under the same discipline. The rule's **contract substance is settled** and is enumerated here so its boundary is checkable: the field is a tri-state; `unknown` is fail-closed and is the value for every undetermined case; the field is hash-inert; it is forward-only with no back-filled determination; determinations are keyed to **content origin** rather than to event timing or summarization mechanism; the re-derivation at surface 2 is a **single frozen snapshot** consumed by both the decision and every durable write; and multi-source aggregation is **worst-value**. Residual precision about **which individual capture call sites can determine content origin** is bounded **by rule, not by enumeration**: the implementation leg re-grounds every call site against its own HEAD before wiring, per the `B-86` → U-MEM-26 precedent and the fork's own §10 cap, and any call-site-level refinement discovered there is **implementation work** rather than a contract amendment - *unless* it contradicts one of the settled sentences above, in which case it back-flows on the same terms any contract defect does. This gives further review a principled exit: a finding below contract altitude routes to the impl leg instead of reopening this delta.

**No amendment - Memory threat model.** Zero change, deliberately, exactly as at v1.1. Its §Threats bullet "Cross-run prompt-injection persistence through promoted semantic/procedural memory." and its §Invariants bullet "Model-authored notes are episodic by default and cannot become injectable semantic memory without policy and evidence." are the authority these two amendments conform to, not a surface they revise - the same X-AL-3 posture v1.1 took at its change-note paragraph "Why this is conformance repair, not design extension (X-AL-3)." Unlike v1.1, v1.2 does **not** claim to be pure conformance repair: it settles a question the contract had left genuinely open, on ratified operator authority, and it adds a field. The threat model is what makes reading B the conforming answer among the three; it does not by itself entail the field.

**Plan absorption (same arc).** `Implementation_Plan_Memory_Substrate_v1.md` v1.1 -> v1.2 adds NEW U-MEM-27 decomposing the impl leg, filed in this same PR. This delta changes no code.

**Naming recorded as an apply-pass choice.** The fork specifies a "`CROSS_SCOPE`-equivalent risk flag" without naming it. The value `cross_family_capture` is this apply pass's choice, made deliberately distinct from the pre-existing `cross_scope` value, which denotes a different relation - a *candidate's* suggested scope escaping its *source record's* scope, not the capture leg's provenance. Collapsing the two would make the gate unable to distinguish an escaping scope from a foreign-family capture.

**Closeout scoping, annotated in this same PR per the `B-86` precedent.** The U-MEM-25 closeout evidence packet (`.harness/u-mem-25-memory-closeout-evidence.md`) certifies this family at **v1.1**, and six of its rows grow obligations at v1.2. `just memory-closeout-check` stays green regardless, because it tests `## C-MEM-NN` and `### R-MEM-NN` heading-derived id coverage and v1.2 adds neither - the identical interim-window shape v1.1 recorded. Both halves of that precedent's fix are applied on the same terms: the **honest-annotation half lands HERE, at the spec leg** - `PENDING - U-MEM-27` markers on C-MEM-03 and C-MEM-10 in the C-MEM matrix and on R-MEM-01, R-MEM-05, R-MEM-09, and R-MEM-14 in the R-MEM matrix, plus a second "Version scoping" window paragraph stated beside the closed v1.1 one - exactly as the `B-86` spec leg annotated its own six rows before U-MEM-26 existed. The **re-open-and-extend half is owed at U-MEM-27**, whose acceptance criteria require all six rows lifted, the window paragraph closed the way window 1 was, and the check re-run green before the unit can close. Reddening the gate for the window is declined again on the main-always-green CI grounds v1.1 recorded. R-MEM-12 is deliberately **not** annotated: the new field is provenance rather than partition, and U-MEM-27 adds no scope-enforcement obligation.

**Surfaced findings, not patched.** (i) The U-MEM-26 unit body's own `file:line` cites into `harness-runtime` (for example `memory_capture.py:585-591`, `memory_promotion.py:741-753`) drifted when U-MEM-26 landed; they are historical records of that unit's authoring HEAD and are deliberately not rewritten. U-MEM-27's cites are verified at HEAD `57f840b6`. (ii) The closeout packet's own window-1 paragraph cited two U-MEM-26 acceptance items by plan line (`:901` / `:924`), anchors this delta's plan insertion shifted. Because the drift is **caused by this delta** rather than inherited, those two cites are repaired in place to unit-id-plus-subsection form - the cite convention this spec's own v1.1 change-note fixed - rather than left stale or silently deleted.

**Sections preserved verbatim at v1.2.** The Status section (revision lines appended only); the whole `## Change-note (v1 -> v1.1)` block; C-MEM-01; C-MEM-02; the C-MEM-03 `SourceRef` and `MemoryScope` field shapes, the "`MemoryScope.provider_family` value domain and derivation" subsection in full, and all six existing C-MEM-03 invariants (the `MemoryRecordEnvelope` block gains one field line and nothing else - no removal, no retype, no reorder of the existing twelve; eight invariants appended); C-MEM-04 through C-MEM-09; the C-MEM-10 `PromotionCandidate` block's pre-existing field lines (none removed, retyped, or reordered - the new flag value is a vocabulary addition to an already-open `list<string>`; the block gains **three** field lines at v1.2 declaring `source_memory_refs`, `review_required`, and `auto_promote_allowed`, fields the implementation model has carried all along and which this delta's own obligations depend on), its `### Pipeline` list, and all three existing invariants (one subsection and thirteen invariants appended); C-MEM-11 through C-MEM-13; **the Memory threat model in full**; C-MEM-14 through C-MEM-20. Zero new record type, zero new enum member, zero change to any ledger, packet, or telemetry shape. Exactly one new field is introduced as a capability - `captured_cross_family` on `MemoryRecordEnvelope`, optional and hash-inert. Three further field lines are **declared** at the C-MEM-10 `PromotionCandidate` block - `source_memory_refs`, `review_required`, `auto_promote_allowed` - which the implementation model has carried since before this delta and which this delta's own obligations depend on; declaring them adds no capability and removes, retypes, or reorders nothing.

**One caveat on that preservation claim, stated so it cannot mislead.** C-MEM-05's declared `SemanticRecord` block and C-MEM-07's `ProceduralSnapshotRecord` block are byte-unchanged, but the durable-carrier obligation added at C-MEM-10 above **does** add a content key to the records the promotion path writes. Those two facts are compatible - the declared blocks were never the exhaustive content schema, and the promotion path already writes `candidate_id`, `source_memory_refs`, and `review_reason` outside them - but a reader should not take "C-MEM-05 preserved verbatim" to mean promoted-record content is byte-unchanged at v1.2. It is not, for records written after this amendment.

## Change-note (v1 -> v1.1)

**Trigger and back-flow authority.** RATIFIED Class 1 fork `.harness/class_1_fork_b86_memory_scope_provider_family_keying.md` (filed 2026-07-28; register row `B-86` at `.harness/forward-register.yaml`, status `design_substrate_gated` **at the fork filing** - that value is historical-at-filing, not live: the row transited to `open` within this same PR, since the spec leg below is what clears the design gate. Consult the register for live status). The fork's §5 recommendations were produced by a three-leg decorrelated pass: an Opus grounding agent (direct code and spec read, file:line evidence), a transcript-aware `advisor()` pass, and a genuinely-convened council deliberation - C10 (action-safety / blast-radius) and C3 (state / memory / persistence) co-primary, C6 (model routing) consultant. The Q1 C10↔C3 tension was surfaced and probe-resolved in favour of chain-primary keying, with C10's requirement satisfied at a different mechanism (the dispatch-side predicate of Amendment 2). This delta is the mechanical spec-leg apply of the fork's §6 drafting targets; nothing was decided here.

**Why this is conformance repair, not design extension (X-AL-3).** The Memory threat model's invariant "Retrieval and injection enforce project, workflow, tenant, provider-family, CLI-profile, and visibility scope before ranking." (line `:481` at fork-filing HEAD `f79dbe85`) **stands unchanged at v1.1 and is the authority for all three amendments below**. v1 already mandated that the provider-family boundary be enforced; it never stated what that boundary is keyed to, which left the mandate unfalsifiable at the contract level. v1.1 supplies the missing value domain, derivation rule, and dispatch-boundary condition that make the already-cleared invariant checkable. No new commitment is created.

**Amendment 1 - C-MEM-03: NEW subsection "`MemoryScope.provider_family` value domain and derivation" plus three appended invariants.** (a) Value domain: the field carries a `ProviderFamily` value - `anthropic`, `openai`, `google`, or `local_open_weight` - never a provider key, a model identifier, or a CLI-profile identifier; a record written with a non-value identifier is not retrievable under a family-scoped request, including a request scoped to that identifier's own family; normalization to the value domain is forward-only, leaving pre-normalization records as a permanent residual. (b) `null` semantics, load-bearing in the enforcement predicates but undocumented at v1: a `null` **stored** value denotes an unpartitioned record that matches any requested family - a wildcard, not an unknown-deny sentinel - while a `null` **requested** family does not widen access past a family-scoped record. The asymmetry is stated deliberately: it is what the enforcement predicates in aggregate actually do (the two scope-filter predicates skip a `null` on either side, but the policy leg they compose with denies a `null`-request-vs-non-`null`-record pair), and it is the field-level instance of C-MEM-09's "Injection cannot be broader than the record's scope." invariant - an unnamed requested partition is a request for *broader* reach, not narrower, which is exactly why the policy predicate refuses it against a partitioned record. A first draft of this delta claimed symmetric either-side wildcarding; out-of-family Codex round 1 [P1-a] caught the over-claim against the policy predicate, and it was corrected before merge. (c) Derivation rule (fork §6 item 2, placed at C-MEM-03 rather than C-MEM-11 because it constrains a field C-MEM-03 declares): a run-level partition attribute, derived once at run-scope composition from the fallback chain's primary family binding, not re-derived per dispatch, so a fallback advancement to a different-family candidate does not alter the run's memory scope. (d) The paired writer-side obligation: **automatic capture** writes under the run's composed record scope and constructs no independent scope, while the other authoring writers (promotion, compaction disposition, native-adapter tool events) legitimately author their own scopes and are bound by the value domain instead. (e) The value domain binds **request-side** scopes - retrieval requests and derived-index queries - on the same terms, with the same registered-key-canonicalize / out-of-domain-reject split.

**Amendment 2 - C-MEM-13: NEW subsection "Cross-family withholding of standard memory tools" plus one appended invariant.** When `standard_memory_tools` has been selected and the dispatched candidate's provider family differs from `MemoryScope.provider_family`, the harness MUST NOT expose the memory tool schemas or the scope reference for that dispatch; the dispatch proceeds without model-facing memory access, and the withholding is recorded with a named denial reason on the C-MEM-19 memory telemetry surface (see the recording-surface paragraph below). Harness-authored memory capture is unaffected - C3's condition of concurrence, on the ground that capture is a different authorship class and crosses no boundary the harness does not already hold. C6's limit is recorded as a stated non-claim: family equality is a necessary but not a sufficient trust condition, and within-family routing to a local terminal surface carries a distinct posture addressed outside this contract.

**Recording surface, stated precisely (Codex round 1 [P1-b]).** The fork's §6 wording called a withheld exposure a "ledgered outcome"; v1.1 does **not** adopt that phrasing, because it over-claims. The withholding is a **recorded** outcome on the C-MEM-19 memory telemetry surface, with the denial reason carried as an attribute value - the shape already shipped for the B-83 packet disposition. On the durable-ledger half the position is split, and both halves are stated at the new C-MEM-13 recording-surface paragraph: (i) where the withholding is realized as a transition of that dispatch to `no_memory_access`, C-MEM-13's pre-existing must-ledger invariant applies unchanged and is **dischargeable through the existing `inject` operation kind** and its injection-decision projection - no new operation kind, no C-MEM-08 amendment; (ii) where it is not such a transition, no durable row is owed, because C-MEM-08's operation-kind vocabulary is closed and expresses no requested-but-withheld operation. Half (ii) is a **pre-existing recording-surface limitation of C-MEM-08, not created by v1.1** - the same constraint the `B-85` close-out recorded independently, and the same one the `B-83`-era span-only disposition already lives under. Widening that vocabulary would be a C-MEM-08 amendment on its own authority, and v1.1 neither performs nor implies one.

**Amendment 3 - C-MEM-14: the exposure obligation qualified.** The present-tense "the harness exposes provider-neutral tools" obligation is now explicitly subject to the C-MEM-13 family-scope condition, and a withheld exposure is a recorded outcome (per the paragraph above) rather than a violation of this contract. Recorded as a clarification of C-MEM-14's existing invariant "Tools cannot bypass scope, redaction, retention, or injection policy." - withholding is that invariant enforced at the exposure boundary instead of at the call - not an extension of it.

**No amendment - Memory threat model.** Zero change, deliberately. Per the X-AL-3 paragraph above, the `:481` invariant is the authority the three amendments conform to, not a surface they revise.

**Downstream consequences recorded here, applied elsewhere.** (i) `B-89` (producer key-vs-value asymmetry: written records carry raw provider keys while retrieval requests carry family values, so an `ollama`-written note is invisible even to a `local_open_weight`-scoped request of its own family) now has its direction determined - the writer adopts the run's composed record scope per Amendment 1(d). (ii) `B-90` (the capture path's independently-constructed scope omits `tenant` and `workload_class`, so under the wildcard-on-`null` semantics every tool-captured record is tenant-unpartitioned, against the `:481` tenant mandate) **will be** closed incidentally by that same writer-side repair **when U-MEM-26 lands**. It is not closed by this delta: until the impl leg ships, the cross-tenant exposure stands, and the register correctly carries `B-90` as open. (iii) The impl leg - the C-MEM-13 withholding guard (fork §5 Q2), the `B-89` writer repair, and the `B-90` fold-in - follows as a separate arc per the `B-33` / `B-59` / `B-70` / `B-72` spec-leg-then-impl-leg precedent. This delta changes no code.

**Plan absorption (same arc).** `Implementation_Plan_Memory_Substrate_v1.md` v1 -> v1.1 adds NEW U-MEM-26 decomposing that impl leg, filed in this same PR.

**Named open question carried forward, not discharged.** Fork §7: whether records captured during a cross-family fallback leg are promotion-eligible under C-MEM-10. That is C-MEM-10 policy territory, outside B-86's scope; v1.1 neither resolves nor forecloses it, and it is restated here so it does not disappear with the fork doc.

**Surfaced finding, not patched.** Three of the fork's `:NNN` cites are off-by-N against this file at HEAD `f79dbe85`: the C-MEM-14 "Tools cannot bypass scope…" invariant is at `:502` (fork §6 item 4 cites `:500`), the cross-run prompt-injection-persistence threat is at `:471` (fork §4 cites `:472`), and C-MEM-11's stable-result invariant is at `:392` (fork §4 cites `:384`). Every load-bearing cite the amendments rest on - C-MEM-03 `:100-108` and `:104`, C-MEM-11 `:346-395`, C-MEM-13 `:431-463` with `:449` and `:454`, the threat model `:465-483` and `:481`, C-MEM-14 `:485-504` - resolves byte-exact. No spec text is changed on account of the drifted cites. Separately, every pre-v1.1 `:NNN` cite into this file across `.harness/**` (for example the `B-84` row's `:463` and the `B-83` row's `:481`) is pinned to the HEAD at which it was written and shifts by construction with this delta; those are historical records of a filing state, not live contract references, and they are deliberately not rewritten here. Cite this spec by contract ID and section name, not by line, in any text authored after v1.1.

**Two contract-text corrections (Codex round 12).** Rounds 3 through 11 landed entirely at the plan and the evidence packet, and the leg was on the point of exiting on soundness; round 12 reopened it because both findings are contract-level, which is the correct exit condition. [P2-a] **Request-side bypass.** The amendment's "not retrievable under a family-scoped request" claim, and the permanent-unretrievable residual that rests on it, were circumventable: `MemoryRetrievalRequest` (`harness-is/src/harness_is/memory_retrieval.py:73`) and `DerivedRetrievalIndexQuery` (`memory_retrieval_index.py:104-112`) both carry a `MemoryScope` whose `provider_family` is an arbitrary string, and all three scope predicates match raw strings - so a legacy record and a request both carrying `provider_family="ollama"` match each other, and the unretrievability the value domain promises evaporates. A new request-boundary paragraph binds the request side on the same terms, deliberately mirroring the authoring side's registered-canonicalize / unregistered-reject split rather than inventing a third posture. [P2-b] **Over-claimed single authority.** The derivation rule's writer-side sentence said the composed run scope is "the single authority for every record the run writes", which is false: promotion, compaction-disposition, and native-adapter tool-event records legitimately author their own scopes. Narrowed to automatically-captured records, with the other authoring writers bound by the value domain instead; the matching change-note clause and the C-MEM-03 invariant bullet are aligned, and a second invariant bullet records the request-side binding.

**Sections preserved verbatim at v1.1.** The Status section (revision lines appended only); C-MEM-01; C-MEM-02; the C-MEM-03 `MemoryRecordEnvelope`, `SourceRef`, and `MemoryScope` field shapes plus its three existing invariants (byte-unchanged - the amendment constrains a declared field's value domain, derivation, and request-side use; it adds, removes, and retypes nothing); C-MEM-04 through C-MEM-12; the C-MEM-13 `MemoryAccessMode` vocabulary, selection-input list, and all six existing invariants (byte-unchanged; one subsection and one invariant appended); the Memory threat model in full; the C-MEM-14 tool table and all four existing invariants (byte-unchanged; one qualifying paragraph appended to its Contract); C-MEM-15 through C-MEM-20. Zero new record type, zero new field, zero new enum member, zero change to any ledger, packet, or telemetry shape.

## C-MEM-01 - Memory plane boundary

### Contract

The memory substrate is a provider-neutral harness plane with five axis responsibilities:

| Axis | Responsibility |
|---|---|
| Information substrate | Typed records, path registry, canonical artifact IO, deterministic serialization, derived index metadata, memory ledger entry shape. |
| Action surface | Memory access mode vocabulary, provider-neutral memory tool contracts, memory telemetry namespace extension. |
| Control plane | Memory policy resolution, provider/CLI access-mode selection, retrieval budget selection. |
| Operational discipline | Audit, redaction, retention, ledger verification, review queue policy. |
| Runtime | Capture, retrieval invocation, provider adapters, CLI profile loading, packet injection, tool execution. |

### Invariants

- Provider-owned memory is never canonical.
- Derived indexes are never canonical.
- Native provider memory, standard tools, and prompt packet fallback operate against the same canonical store.
- Memory promotion and memory injection are distinct policy decisions.
- Atomic implementation sequencing is allowed; product completion requires the full contract family.

## C-MEM-02 - Canonical path registry

### Contract

The canonical memory root is `.harness/memory/` unless a deployment-surface binding explicitly maps it elsewhere. Under that root, the following paths are stable:

| Path | Role |
|---|---|
| `manifest.json` | Memory store manifest, schema version, project/workflow identity, store id. |
| `policy.json` | Default memory policy for capture, promotion, retrieval, injection, redaction, retention. |
| `episodic/runs/<run_id>/run.json` | One run record. |
| `episodic/runs/<run_id>/turns.jsonl` | Append-only turn records. |
| `episodic/runs/<run_id>/tool_events.jsonl` | Append-only tool summaries. |
| `episodic/runs/<run_id>/compactions.jsonl` | Append-only compaction events. |
| `episodic/runs/<run_id>/summaries/` | Human-readable or machine summaries, source-linked. |
| `semantic/facts/` | Semantic fact records. |
| `semantic/preferences/` | Preference records. |
| `semantic/decisions/` | Decision records. |
| `semantic/conventions/` | Project convention records. |
| `semantic/failures/` | Failure learning records. |
| `semantic/research/` | Research state records. |
| `semantic/index.jsonl` | Derived semantic index metadata. Rebuildable. |
| `procedural/snapshots/` | Procedural snapshot records. |
| `procedural/promoted/` | Policy-approved procedural memory projections. |
| `durable/memory_ops.jsonl` | Canonical append-only global memory operation ledger. |
| `durable/promotion_decisions.jsonl` | Rebuildable review projection keyed by canonical memory operation `action_id`. |
| `durable/injection_decisions.jsonl` | Rebuildable review projection keyed by canonical memory operation `action_id`. |
| `durable/retrieval_events.jsonl` | Rebuildable review projection keyed by canonical memory operation `action_id`. |

### Invariants

- Canonical writes go to canonical paths before derived indexes update.
- Deployment-surface remapping must preserve the same logical path classes.
- A path registry implementation must reject traversal outside the memory root.
- Files under `semantic/index.jsonl` or equivalent derived caches must be rebuildable from canonical records.
- `durable/memory_ops.jsonl` is the only authoritative memory operation ledger and provides the global hash-chain order. Projection files are non-authoritative filtered views that may be rebuilt from `memory_ops.jsonl`.

## C-MEM-03 - Common record identity

### Contract

Every memory record has a common identity envelope:

```text
MemoryRecordEnvelope {
  memory_id: string
  schema_version: string
  tier: working | episodic | semantic | procedural | durable
  kind: string
  created_at: timestamp
  updated_at: timestamp | null
  source_refs: list<SourceRef>
  scope: MemoryScope
  content_hash: sha256
  supersedes: list<memory_id>
  superseded_by: list<memory_id>
  redaction_state: active | redacted | tombstoned
  captured_cross_family: true | false | unknown
}

SourceRef {
  ref_type: run | turn | tool_event | compaction | file | git_commit | operator | provider_response | external
  ref: string
  content_hash: sha256 | null
}

MemoryScope {
  project: string | null
  workflow: string | null
  workload_class: string | null
  provider_family: string | null
  cli_profile: string | null
  tenant: string | null
  visibility: private | project | workflow | tenant | public
}
```

### `MemoryScope.provider_family` value domain and derivation

`provider_family` carries a `ProviderFamily` value - one of `anthropic`, `openai`, `google`, or `local_open_weight` - and never a provider key, a model identifier, or a CLI-profile identifier. The `string | null` declaration above is a serialization shape, not a licence to store an arbitrary identifier.

A record written with a non-value identifier in this field is not retrievable under a family-scoped request. The retrieval, index, and policy scope predicates compare the stored identifier against the requested family directly, so such a record is invisible even to a request scoped to that identifier's own family. Normalization to the value domain is forward-only: records already written with a non-value identifier are not rewritten and remain unretrievable under family-scoped requests as a permanent residual.

`null` on a stored record denotes an unpartitioned record: it matches any requested provider family. `null` is not an unknown-deny sentinel; a record that must be confined to one provider family carries that family's value, never `null`.

The wildcard is scoped to the stored-record side only, and the two sides are deliberately not symmetric. A `null` requested family does not widen access past a family-scoped record: a record carrying a family value is not reachable by a request that carries none. That asymmetry is this field's instance of C-MEM-09's "Injection cannot be broader than the record's scope." invariant: a request that declines to name a partition is asking for **broader** reach than a partitioned record permits - omitting the constraint would let that request reach every family - so the policy predicate denies it against a family-scoped record.

`provider_family` is a run-level partition attribute. It is derived once, at run-scope composition, from the fallback chain's primary family binding, and it is not re-derived per dispatch: a fallback advancement to a candidate of a different provider family does not alter the run's memory scope. A fallback chain is a continuity mechanism, and the run's memory partition is one of the run-level identities it preserves across that boundary.

The paired writer-side obligation is that **automatically captured** records are written under the run's composed record scope. The capture path does not construct an independent `MemoryScope`; for the records a run captures, the composed scope is the single authority, so what a run captures and what a run can retrieve share one partition by construction. Other authoring writers - promotion, compaction disposition, and native-adapter tool events - legitimately author their own record scopes, and are bound by this field's value domain rather than by the run's composed scope.

The value domain binds the **request side** on the same terms as an authored record scope. A retrieval request's scope and a derived-index query's scope carry a `ProviderFamily` value or `null` under the semantics above; a requested `provider_family` that is out of the value domain is canonicalized through the provider-to-family authority when it is a registered provider key, and rejected otherwise - the same registered / unregistered split the authoring side applies, and no third posture. Without this, the unretrievability of a non-value legacy record would be circumventable simply by issuing a request that carries the same non-value identifier, since the scope predicates match raw strings.

### `MemoryRecordEnvelope.captured_cross_family` - stored-version cross-family capture provenance

`captured_cross_family` is a **tri-state** provenance field on the record identity envelope, carrying `true`, `false`, or `unknown`. It records one fact about **the stored version of this record**: whether the content in that version was produced on a dispatch whose provider family differed from the family the record is partitioned under. It exists to make the C-MEM-10 cross-family-captured gate decidable; it is not a second authority on provider family, and no other contract in this family consumes it.

**Derivation rule.** At capture, the writer compares the dispatch's own `provider` - canonicalized through the same provider-to-family authority that governs this field's sibling `provider_family`, with the same fail-closed treatment of an unregistered key - against the record's own composed `scope.provider_family`, and stores the answer. `false` when both resolve and are equal; `true` when both resolve and differ; `unknown` otherwise. The comparison is a **derived predicate over `provider_family`**, dependent on that field rather than rival to it: this field declares no value domain of its own, adds no family-valued surface, and introduces no normalization posture beyond the one the value-domain subsection above already fixes.

**The rule is keyed to the content's ORIGIN - whether it derives from a completed provider dispatch - and not to the mechanism that summarized it.** A determination - `true` or `false` - is recorded **only where the stored content derives from the output of a completed provider dispatch**. Everything else is `unknown`, and this is a consequence of what the field means rather than an extra condition on it: the field states whether *the content in this version* came from a leg whose family differed, so where no dispatch produced the material there is no such leg, and `false` would assert an equality that was never tested against anything.

**Content origin and summarization mechanism are independent, and conflating them is a defect this contract explicitly forecloses.** A capture may summarize a real provider response using a deterministic harness rule rather than a model; the resulting summary is *harness-summarized* but its content is *dispatch-derived*, and it therefore carries a determination normally. The `summary_source` field of the episodic record shapes identifies **which mechanism produced the summary text** - it does not say whether the summarized material came from a provider dispatch - so it is not the discriminator for this field and must not be used as one. A rule keyed to `summary_source` would classify every harness-summarized turn as undetermined, including completed same-family dispatches, forcing review on content whose provenance is in fact known.

**What the writer keys on instead.** The signal is the **capturing caller's own knowledge on THIS invocation**: a capture invoked with a completed dispatch's result in hand records a determination against that dispatch's provider, and a capture invoked with no such result records `unknown`. This is a property of the individual call, not of a stored field and not of the capture method's name. Where every production invocation of a given capture method shares one origin, a method-level mapping is a sound way to realize the rule; where a method's invocations can differ - a failure observation may describe a dispatch that produced output, or one that produced none - the method name is **not** a sufficient signal, and such a method either carries an explicit per-call origin value or conservatively records `unknown` for the invocations it cannot distinguish. Two consequences follow. A capture that runs **before** its dispatch has, by construction, no produced content to describe and the provider it names is a *selection* rather than a producer, so it records `unknown`. And a record whose content is **run-lifecycle metadata** - identifiers, engine class, CLI profile, provider route, timestamps, close status - derives from no dispatch output at all, whenever it is written, and likewise records `unknown`. Where a genuine case arises in which the writer cannot tell whether its content is dispatch-derived, that case records `unknown` under the general undetermined rule above; the contract needs no further enumeration for it.

The practical reach of this qualification is narrower than it first appears, and stating that is part of stating the rule honestly: the records that actually feed the promotion pipeline are the content-bearing turn and tool captures, which summarize real dispatch output and therefore receive real determinations - whether a model or a harness rule did the summarizing. A **failure** capture is the case that shows why the signal is per-invocation rather than per-method: a failure summary that describes output a dispatch actually produced is dispatch-derived and carries a determination, while one describing a dispatch that produced **no** output derives from nothing and records `unknown`. What becomes `unknown` is largely run-lifecycle metadata, which is not promotion source material. The qualification removes false confidence without materially widening what gets gated.

**When the writer must record `unknown`, and why it is not `false`.** `unknown` is recorded whenever the predicate was not actually determined: the stored content does not derive from the output of a completed provider dispatch, per the paragraphs above; the dispatch supplied no `provider`; the supplied provider key is unregistered, so its family is unknown and the fail-closed disposition applies; or the record's own `scope.provider_family` is `null` - the unpartitioned wildcard of the subsection above - against which "cross-family" is undefined. Recording `false` in any of those cases would persist a determination the writer never made, which is the permissive-by-silence failure this field exists to remove. A writer that cannot determine the value records `unknown`; it never defaults to `false`.

**Read-side mapping of `unknown`.** `unknown` is not "presumed same-family". It is treated exactly as `true` is at the C-MEM-10 gate: the candidate is review-required and never auto-promotable. A determination is reported only when it was reached, and an unreached determination fails closed.

**Hash-inert.** The field enters neither `content_hash` nor `memory_id`. `content_hash` is computed over canonical serialized **content**, which the envelope is not part of (the invariant below states this independently). Record identity is then derived from that content hash for the content-addressed kinds, while the run record is the standing exception - its `memory_id` derives from the `run_id` alone and is content-independent, which is what lets one run record be overwritten in place by its second writer. The hash-inert conclusion holds for **both** derivations and for every kind: an envelope field is an input to neither, so adding, populating, or later correcting this field moves no record identity and invalidates no existing hash.

**Forward-only.** The field is optional, and its absent value is `unknown`. A record written before this amendment carries no field and reads as `unknown`: the pre-amendment corpus is uniformly undetermined under this field by construction, and is gated accordingly rather than presumed safe. Writers that legitimately author records other than automatic capture - promotion, compaction disposition, native-adapter tool events - are not required to populate the field and leave it `unknown` unless they can determine the predicate for the content they write.

The forward-only guarantee is about provenance **determination**, and is stated at that precision deliberately. What is forbidden is back-filling a *determination* onto a record whose writer never made one: no migration may turn an absent field into `true` or `false`. It is **not** a guarantee of byte-stability for the serialized envelope across legitimate durable transitions. A redaction, tombstone, or retention-expiry transition rebuilds and rewrites the envelope of an already-persisted record, and such a rewrite may **materialize an explicit `unknown`** where the field was previously absent. That is permitted, and it is not a back-fill: absent and explicit-`unknown` denote the identical thing under this field's semantics, both read as undetermined, and both gate the same way, so the transition records the record's provenance status exactly as it stood. Requiring unset-preserving serialization instead would complicate the transition path that must stay able to redact a legacy record, for no semantic gain.

**A transition that REPLACES the stored content must reset the field to `unknown`, and that is the converse case rather than a back-fill.** A redaction, tombstone, or retention-expiry transition does not merely re-serialize the envelope: it substitutes harness-authored replacement material for the content the record held. Because this field describes **the stored version**, a preserved `true` or `false` would then assert that the replacement material came from the original dispatch, which is false on its face and contradicts both the stored-version rule and the content-origin rule. Such a transition therefore writes `unknown` for the resulting version, whatever the prior value was. This does not collide with the no-back-fill rule above: that rule forbids manufacturing a *determination* where none was made, and this discards a determination that no longer describes the content - the two run in opposite directions and both fail closed.

**Multi-writer records: the field describes the stored version, not the writer history.** Where one stored record is written by one event and later overwritten by another - the run record is the only such kind - the field is co-written with the content it qualifies, from the same call, so the stored value always describes the stored content. An overwrite therefore preserves provenance for the version that survives; it does not record which writer set it, and must not be read as doing so.

**Stated bound.** This field answers **present/absent only**. It cannot name *which* provider family produced the content, so it cannot support a promotion policy that discriminates *between* cross-family legs; such a policy would require a separate family-valued amendment with its own value domain. It also cannot answer whether *any* leg of the producing run was cross-family, which is not representable in a per-record envelope. Neither capability is claimed here.

### Invariants

- `content_hash` is computed over canonical serialized content excluding derived indexes.
- Supersession does not delete the prior record.
- Redaction and tombstone states are durable memory operations.
- `provider_family` carries a `ProviderFamily` value or `null`, where a `null` stored value is the unpartitioned wildcard and not an unknown-deny sentinel, and a `null` requested value does not widen access past a family-scoped record.
- The run's composed record scope is the authority for a run's retrieval and for its automatically captured records; the capture path does not construct an independent scope. Other authoring writers own their record scopes, subject to the same `provider_family` value domain.
- The `provider_family` value domain binds retrieval-request and derived-index-query scopes on the same terms as authored record scopes.
- `captured_cross_family` is a tri-state describing the stored version of the record: `true` or `false` only where the capture writer actually determined the comparison between the dispatch's provider family and the record's own `provider_family`, and `unknown` in every other case, including an absent field on a pre-amendment record. A writer never records `false` for an undetermined comparison.
- A determination is recorded only where the stored content derives from the output of a completed provider dispatch. Content written before its dispatch, and content that derives from no dispatch output such as run-lifecycle metadata, records `unknown` - `false` would assert an equality never tested against a producer.
- Content origin is independent of summarization mechanism: a harness-summarized summary of a real provider response is dispatch-derived and carries a determination. `summary_source` names the summarizing mechanism and is not the discriminator for this field.
- The origin signal is per-invocation, not per-capture-method: a method-level mapping is sound only where every production invocation of that method shares one origin, and a method whose invocations can differ carries an explicit per-call origin value or records `unknown` for the invocations it cannot distinguish.
- No migration may back-fill a determination: an absent or `unknown` field is never rewritten to `true` or `false`. This constrains manufacturing a determination and does not constrain discarding one that no longer describes the stored content.
- A durable transition that replaces the stored content with harness-authored material - redaction, tombstone, retention expiry - writes `unknown` for the resulting version, whatever the prior value was, because the field describes the stored version and the replacement material derives from no dispatch. A durable transition of an already-persisted record - redaction, tombstone, or retention expiry - may materialize an explicit `unknown` where the field was absent, which is not a back-fill, since absent and explicit `unknown` denote the same undetermined status and gate identically.
- `captured_cross_family` is hash-inert: it is an envelope field, so it enters neither `content_hash` nor `memory_id`, and populating or correcting it moves no record identity.
- `captured_cross_family` answers whether the stored content was cross-family-captured, never which provider family produced it and never whether any other leg of the producing run was cross-family.

## C-MEM-04 - Episodic records

### Contract

Episodic memory includes `EpisodicRunRecord`, `EpisodicTurnRecord`, `ToolEventRecord`, and `CompactionEventRecord`.

```text
EpisodicRunRecord {
  envelope: MemoryRecordEnvelope
  run_id: string
  workflow_id: string | null
  thread_id: string | null
  engine_class: event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment
  cli_profile: string
  provider_route: list<ProviderBinding>
  started_at: timestamp
  closed_at: timestamp | null
  close_status: completed | failed | cancelled | paused | unknown
}

EpisodicTurnRecord {
  envelope: MemoryRecordEnvelope
  run_id: string
  turn_id: string
  step_id: string | null
  prompt_summary: string
  response_summary: string
  summary_source: harness_rule | model_generated | operator | imported
  summary_model: string | null
  summary_hash: sha256
  tool_event_refs: list<memory_id>
  failure_observations: list<string>
  promotion_candidates: list<PromotionCandidate>
  token_usage: TokenUsage | null
}
```

### Invariants

- Episodic capture is automatic when memory is enabled.
- Episodic records may summarize sensitive content by policy, but the capture decision remains durable.
- Model-generated summaries are captured as stored artifacts with model and hash provenance; retrieval/ranking must not regenerate summaries as part of selection.
- Episodic records are run-scoped unless explicitly promoted.

## C-MEM-05 - Semantic records

### Contract

Semantic memory includes fact, decision, convention, failure learning, research, and preference records.

```text
SemanticRecord {
  envelope: MemoryRecordEnvelope
  semantic_kind: fact | decision | convention | failure_learning | research | preference
  statement: string
  rationale: string | null
  evidence: list<SourceRef>
  confidence: low | medium | high | verified
  status: proposed | active | denied | superseded | expired
  ttl: duration | null
  expires_at: timestamp | null
  injection_policy: never | retrieval_only | prompt_packet_allowed | tool_allowed | native_allowed
  tags: list<string>
}
```

### Invariants

- Semantic records are cross-run only after promotion policy approves or queues them.
- Evidence is mandatory for active semantic records.
- Expired, denied, superseded, redacted, or tombstoned records are excluded from injection.

## C-MEM-06 - Preference records

### Contract

Preferences are first-class semantic records with additional fields:

```text
PreferenceRecord extends SemanticRecord {
  preference_subject: operator | project | workflow | code_style | tool_use | provider | review | other
  preference_strength: weak | normal | strong | mandatory
  source_authority: operator_direct | inferred_from_repetition | imported | policy
  confirmation_required: bool
}
```

### Invariants

- `source_authority=operator_direct` may be promoted without inference if policy allows.
- `source_authority=inferred_from_repetition` must carry at least two source refs or remain proposed.
- Mandatory preferences must be scoped and source-linked.
- A preference can be stored without being injectable; injection is governed by `injection_policy`.

## C-MEM-07 - Procedural snapshots

### Contract

Procedural memory snapshots capture the workflow instructions active for a run or promotion:

```text
ProceduralSnapshotRecord {
  envelope: MemoryRecordEnvelope
  snapshot_id: string
  workflow_id: string | null
  cli_profile: string
  prompt_refs: list<ContentRef>
  skill_refs: list<ContentRef>
  routing_manifest_ref: ContentRef | null
  instruction_file_refs: list<ContentRef>
  memory_policy_ref: ContentRef
}

ContentRef {
  path_or_uri: string
  content_hash: sha256
  kind: prompt | skill | routing_manifest | instruction_file | memory_policy | other
}
```

### Invariants

- Every memory-affecting run references a procedural snapshot.
- Snapshot refs are content-addressed.
- CLI-specific instruction files may participate only through the active CLI profile policy.

## C-MEM-08 - Memory operation ledger

### Contract

Every memory operation writes a durable ledger entry. The memory ledger shape is an additive D-derivative over the existing C-IS-05/C-IS-06 state-ledger discipline: it preserves `action_id`, `idempotency_key`, `actor`, `response_hash`, `timestamp`, and `prior_event_hash`, then adds memory-specific fields as sidecar payload.

```text
MemoryOperationEntry extends StateLedgerEntry {
  operation_kind: capture | retrieve | inject | promote | propose_promotion | deny_promotion | redact | tombstone | delete_request | native_adapter_call | standard_tool_call | compaction_decision
  operation_projection: none | promotion_decisions | injection_decisions | retrieval_events
  run_id: string | null
  step_id: string | null
  provider: string | null
  model: string | null
  cli_profile: string | null
  engine_class: event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment | null
  memory_refs: list<memory_id>
  policy_ref: string | null
  procedural_snapshot_ref: string | null
}
```

Projection mapping:

| Operation kind | Authoritative ledger | Projection |
|---|---|---|
| `capture` | `durable/memory_ops.jsonl` | none |
| `retrieve` | `durable/memory_ops.jsonl` | `durable/retrieval_events.jsonl` |
| `inject` | `durable/memory_ops.jsonl` | `durable/injection_decisions.jsonl` |
| `promote`, `propose_promotion`, `deny_promotion` | `durable/memory_ops.jsonl` | `durable/promotion_decisions.jsonl` |
| `redact`, `tombstone`, `delete_request` | `durable/memory_ops.jsonl` | none |
| `native_adapter_call`, `standard_tool_call`, `compaction_decision` | `durable/memory_ops.jsonl` | none |

### Invariants

- Ledger entries are append-only.
- `idempotency_key` is stable for retry of the same operation.
- `prior_event_hash` chains entries within `durable/memory_ops.jsonl` using the C-IS hash-chain construction.
- `durable/memory_ops.jsonl` has a serialization point for appends; concurrent writers must not observe the same prior hash and fork the global stream.
- Projection files do not define independent causality; audit reconstruction follows the canonical memory operation ledger order.
- Deletion and redaction are represented as ledgered operations; prior records are not silently rewritten.

## C-MEM-09 - Memory policy

### Contract

Memory policy resolves six decisions:

1. Capture: whether to capture an event and at what fidelity.
2. Promotion: whether to discard, keep episodic, propose, or promote.
3. Retrieval: which scopes and record kinds are eligible.
4. Injection: which packet/tool/native surfaces may expose records.
5. Retention: expiry, pruning, and tombstone behavior.
6. Redaction: sensitive content handling and review.

Policy decision values:

```text
CaptureDecision = deny | summarize_only | capture_full | capture_redacted
PromotionDecision = discard | keep_episodic | propose_semantic | promote_semantic | propose_procedural | promote_procedural
AccessDecision = deny | retrieval_only | prompt_packet | standard_tools | native_provider
ReviewMode = automatic | operator_required | forbidden
```

### Invariants

- If policy resolution fails, capture may fall back to durable minimal evidence, but promotion and injection must deny.
- Injection cannot be broader than the record's scope.
- Native provider access cannot bypass policy.

## C-MEM-10 - Promotion pipeline

### Contract

Promotion transforms episodic candidates into semantic or procedural records.

```text
PromotionCandidate {
  candidate_id: string
  source_refs: list<SourceRef>
  source_memory_refs: list<memory_id>
  proposed_kind: fact | decision | convention | failure_learning | research | preference | procedural_update
  statement: string
  confidence: low | medium | high
  suggested_scope: MemoryScope
  risk_flags: list<string>
  review_required: bool
  auto_promote_allowed: bool
}
```

### Cross-family-captured promotion candidates

A promotion candidate is **cross-family-captured** when the source record it derives from carries `captured_cross_family` as `true` - the content of that stored version was produced on a dispatch whose provider family differed from the record's own `MemoryScope.provider_family` - or as `unknown`, meaning the comparison was never determined for that version. Both dispositions are treated identically here; `unknown` fails closed, per C-MEM-03's read-side mapping of that value. A candidate whose source record carries `false` is not cross-family-captured.

Such a candidate is **marked** with the risk-flag value `cross_family_capture` in `risk_flags`. This is a **vocabulary addition, not a schema widening**: `risk_flags` is declared above as an open `list<string>`, so the new value requires no field, no type change, and no shape change at this contract. Where an implementation carries risk flags as a closed enumeration, admitting this value there is implementation work bound by this contract, not a further contract amendment.

Such a candidate is **review-required and is never auto-promotable**. This holds under every policy configuration: no promotion decision value, no review mode, and no confidence level makes a cross-family-captured candidate eligible for automatic promotion. The mark and the gate are stated together deliberately, because the mark alone would be inert - a risk flag that no promotion decision consults is metadata that is carried and persisted and never acted on, which is precisely the condition the `B-92` fork found at the pipeline. The gate is what the ratified position obliges; the flag is how the reason for it stays visible and auditable downstream.

The mark is the **single authority** for the gate. It is derived once, from the source record's `captured_cross_family` field, at the point the candidate's risk flags are computed; the promotion decision then reads **the flag**, not a second independent look at the source record. The two must not be derived in parallel: a gate computed from one input and a flag computed from another can diverge silently under later edits, which reproduces the advisory-flag condition this rule exists to end. The relation is therefore **biconditional** - a candidate carries `cross_family_capture` if and only if it is review-required-and-not-auto-promotable on that ground - and there is no policy configuration in which one holds without the other.

The rule is enforced at **two surfaces with different authority**, and the distinction is stated explicitly because the two are easy to conflate.

**Surface 1 - derivation.** Where the harness itself builds a candidate from a source record, the mark is derived once from that record and the gate consumes the mark, per the single-authority rule above. Nothing here is re-derived, and nothing is read twice.

**Surface 2 - activation and durable proposal.** Where a promotion surface receives a candidate it did not itself derive - a value any integration may construct, since a promotion candidate is an ordinary data value - the candidate's **own assertions are not authoritative**. Neither its flags nor its booleans may be trusted, and the reason is structural rather than defensive: a candidate that simply **omits** the mark while asserting auto-promotability is internally consistent, so no amount of consistency checking on the value can detect it. Before such a candidate is acted on, the surface therefore **re-derives** the condition from the stored source record or records the candidate cites, reads their `captured_cross_family`, and treats the re-derived answer as authoritative over anything the candidate claims about itself - both for the gate and for the mark the durable artifact carries. The obligation is **uniform over every durable write taken from that candidate**, whatever the resulting status: an activation, a proposal held for review, and a denial all persist a record whose content states the candidate's risk flags, so all three must state the **re-derived** mark rather than the supplied one. Stating it per-event would leave whichever write was not enumerated persisting untrusted provenance into the exact artifact the durable-carrier rule exists to make auditable.

**What the re-derivation withholds, stated precisely, because it is the difference between this contract and a refusal.** A re-derived `true` or `unknown` withholds **automatic** activation only. It does not make the candidate unpromotable: it forces the review-required disposition, and an activation that carries an **explicit operator approval** proceeds normally. That is not a loophole in the gate - it *is* the gate working, because routing such a candidate to review is the whole of what this contract asks for, and an approval is the review having happened. A surface that refused a reviewed-and-approved cross-family-captured candidate would be enforcing the outright-refusal reading this contract deliberately does not adopt, and would contradict the eligibility-preserved paragraph below.

Where the source cannot be resolved at all - no source reference, a reference that cannot be read, or a lookup the surface is unable to perform - the outcome is the same as `unknown`: the mark is carried and automatic activation is withheld, while the operator-approved path remains open. An unresolvable provenance is an undetermined one, and this contract's `unknown` disposition already fixes what undetermined means.

**The re-derivation happens ONCE per surface invocation, and its result governs both the decision and every durable write of that invocation.** The re-derived answer is a **frozen snapshot**, taken once and then consumed; it is not a lookup each consumer repeats. Two reads of the same source records can disagree - this field is hash-inert, so a record may legitimately be rewritten under the same identity between them - and a surface that read once for its gate and again for its write could pass the gate on one answer while persisting the other, producing an active record that is both marked cross-family-captured and never reviewed. That combination is exactly what this subsection's gate invariant forbids, so the contract removes the possibility structurally rather than warning against it: the decision is a **pure projection of the snapshot**, and the durable write states that same snapshot's mark. Where a surface performs its gate check and its write in separate steps, the snapshot is carried between them as data.

**The snapshot binds the decision to the source version it read, and a commit may not outlive that binding.** One read makes the gate and the durable write mutually consistent, which is necessary but not sufficient: it does not by itself tie the decision to the *version of the source* it was taken from. A source record may be legitimately rewritten under the same identity after the snapshot is taken - this field is hash-inert, so a rewrite carrying a different provenance leaves the identity unchanged - and a surface that snapshotted `false`, then committed after such a rewrite, would auto-activate content the canonical source now says requires review, persisting no mark. The obligation is therefore stated at the commit rather than at the read: **an activation must not commit against a source whose recorded provenance has changed since the snapshot was taken.** Where it has changed, the invocation does not proceed on the stale snapshot; it fails, or retakes the snapshot and re-decides. The **mechanism is implementation discretion** - a version or generation token carried with the snapshot, a re-check of the cited sources at commit, or a lock held across the decision all discharge it - and this contract deliberately prescribes none, because the honest requirement is the property, not the machinery. Note this is a genuine bound and not a restatement of the single-read rule: single-read forbids the gate and the write *disagreeing with each other*, and this forbids them *agreeing on a version the store has since superseded*.

**The property binds the commit itself, which settles what would otherwise be an atomicity question.** A verification step that can be separated from the persistence it authorizes does not discharge this obligation: if a supersession can land between the check and the write, then the write did commit against a changed source, and the fact that a check preceded it is immaterial. Conformance is therefore judged on the outcome - no commit against a superseded source - not on the presence of a verification step. Whether that is achieved by a compare-and-set, a generation token, a lock, or a transaction spanning validation and persistence remains implementation discretion; what is not discretionary is that the chosen mechanism must leave no interleaving in which the property fails.

**Why the binding attaches to activation and not to every durable write - a decision, not an omission.** A proposal held for review and a denial are **non-active** outcomes: each persists the provenance the snapshot honestly read, and if the source is superseded between snapshot and write, the artifact is stale-but-gated rather than stale-and-injectable. Such an artifact is corrected at the next surface-2 invocation, which re-derives from the then-current source before anything activates. Only one direction crosses this contract's gate: a stale `false` becoming an **automatic activation**, which makes content injectable that the canonical source now says needs review. That asymmetry is why the commit-binding property is stated over activation; extending it to non-active writes would add cost without closing a gate.

**A candidate may cite more than one source record, and the re-derived answer is the worst of them.** The singular wording above generalizes by taking the least-confident value across every cited source: the candidate's effective provenance is `true` if **any** resolved source is `true`; otherwise `unknown` if **any** source is `unknown` or unresolvable; and `false` **only when every cited source resolves to `false`**. A candidate citing no source at all is `unknown` by the preceding paragraph. The direction is forced rather than chosen - a promoted record's content is derived from all of its sources together, so one cross-family-captured source is enough to make the promoted statement carry cross-family-produced material, and an aggregation that gated only when *every* source was risky would let a single `false` source launder the rest.

**Why this is not the parallel derivation forbidden above.** The single-authority rule forbids computing the mark and the gate from two different inputs *at the same surface*, which lets them disagree. Surface 2 is a **different trust boundary**: the candidate has crossed out of the harness's own derivation and back in, so re-deriving from the authoritative record is not a second opinion about one derivation - it is the only derivation this surface has any warrant to believe. The two rules compose: within a surface, derive once; across a trust boundary, never inherit a claim you can re-establish from the source.

A candidate carrying `cross_family_capture` while asserting auto-promotability remains an **illegal pair**, and every **validating** construction path - direct construction, deserialization - must reject it, so the contradiction cannot be introduced deliberately. That check is a **consistency** guarantee, not a provenance one: it is deliberately not claimed to make the illegal pair unreachable by every mechanism, because a value copied from a valid one need not re-validate, and because it says nothing about the omitted-mark case. Surface 2 is what closes both, and it is where the obligation actually rests.

The `cross_family_capture` value is **reserved to the writer that derives it**. It names a fact about a stored record's provenance, which only the deriving writer is in a position to establish, so a caller-supplied instance of it carries no authority: where candidate material arrives with risk flags already attached - a stored promotion hint, an operator submission, an imported candidate - any occurrence of this reserved value in that input is discarded and the value is re-derived from the source record's own `captured_cross_family` field. The overwrite is unconditional and runs in **both** directions: supplied input can neither introduce the mark on a source record that carries `false`, nor suppress it on a source record that carries `true` or `unknown`. Without that rule the flag would be simultaneously the gate authority and a caller-writable input, which is not an authority at all.

The mark **must survive to the durable review artifact**. A gated candidate is by construction routed to review, so the record that review reads is a durable `proposed`-status semantic or procedural record; if the flag reaches only the in-memory candidate, an operator inspecting that record cannot see why it was held, and the auditability this rule claims is not delivered. The promotion-written record therefore carries its candidate's risk flags in the record's own content, alongside the `evidence`, `confidence`, and `status` a reviewer already reads there. Two consequences are stated rather than left implicit. (a) This obligation is discharged **in record content, not in the C-MEM-08 ledger**: the memory-operation entry shape declared at C-MEM-08 is closed and gains no field, and no operation kind, projection, or telemetry member is added. (b) Record content is the `content_hash` input, so promotion records written **after** this amendment carry one additional content key and hash accordingly. No already-written record is rewritten, re-hashed, or moved; the change is forward-shape only, and it applies to promotion-written records alone - the capture path's content shapes are untouched.

Eligibility is otherwise **preserved**. A cross-family-captured candidate remains promotable through review, and a promotion so approved is an ordinary semantic or procedural record thereafter. This contract does not make the fallback leg's learning permanently unpromotable; what it removes is silent automatic promotion of content whose producing family differed from the family the promoted record will be attributed to.

The provenance term this rule reads is the source record's own stored `captured_cross_family` field. This contract states no other discriminator, and in particular does not require a promotion decision to join against the C-MEM-08 memory operation ledger.

One consequence follows from the fail-closed mapping and is stated rather than left to be discovered. A source record whose writer was not automatic capture - a record already promoted, a compaction disposition, a native-adapter tool event - carries `unknown` per C-MEM-03's forward-only paragraph, and is therefore gated. That is the intended reading, not an accident of it: such a record carries no determination about the provenance of the content it holds, and a *second* promotion taken from it would otherwise inherit that silence. Gating it costs a review; presuming it same-family would reintroduce, one promotion downstream, exactly the silence this rule removes.

### Pipeline

1. Candidate extraction from turn, tool, failure, compaction, or operator events.
2. Policy resolution.
3. Optional operator review.
4. Canonical semantic/procedural write.
5. Durable promotion decision ledger entry.
6. Derived index update.

### Invariants

- Compaction candidates must receive a durable disposition before compaction completes.
- Promotion cannot create an active semantic record without evidence.
- Promotion denial is also ledgered.
- A cross-family-captured candidate - one whose source record carries `captured_cross_family` as `true` or `unknown` - is review-required and is never auto-promotable, under every policy configuration. Cross-family capture does not make a candidate ineligible; it makes automatic promotion of that candidate unavailable.
- A cross-family-captured candidate carries the `cross_family_capture` risk flag, and that flag is gate-bearing rather than advisory: the promotion decision consults it, so a candidate marked with it cannot reach automatic promotion.
- The flag is the single gate authority and the relation is biconditional: a candidate carries `cross_family_capture` if and only if it is gated on that ground. The gate is never derived from a second, parallel read of the source record.
- A candidate that carries `cross_family_capture` while asserting auto-promotability is an illegal pair, and every validating construction path rejects it. That is a consistency guarantee only: it does not make the pair unreachable by a non-validating copy, and it cannot detect a candidate that omits the mark while asserting auto-promotability.
- Before a candidate the promotion surface did not itself derive is acted on, the condition is re-derived from the stored source record or records it cites, and both the gate and the mark the artifact carries follow that re-derivation rather than the candidate's own assertions. An unresolvable source is treated as `unknown`.
- The re-derivation is performed once per surface invocation and its result is a frozen snapshot; the gate decision and every durable write of that invocation consume that one snapshot, never a repeated lookup. A gate passed on one reading while a different reading is persisted is forbidden by construction, not by caution.
- An activation must not commit against a source whose recorded provenance changed after the snapshot was taken. On such a change the invocation fails or retakes the snapshot and re-decides; it never commits on the stale one. The binding mechanism is implementation discretion, but a verification step separable from the persistence it authorizes does not discharge the obligation: conformance is judged on the outcome, leaving no interleaving in which a commit lands against a superseded source.
- The commit-binding obligation attaches to activation. A proposal or denial persists the snapshot's honestly-read provenance and is stale-but-gated if the source is superseded before the write, corrected at the next surface-2 invocation; only a stale `false` reaching automatic activation crosses this contract's gate.
- The re-derived mark, not the supplied one, is what every durable write taken from such a candidate persists - activation, proposal, and denial alike. No durable record states a provenance the surface did not itself establish.
- Where a candidate cites several source records, the re-derived answer is the least-confident across them: `true` if any resolved source is `true`, else `unknown` if any is `unknown` or unresolvable, and `false` only when every cited source resolves to `false`.
- The re-derivation withholds automatic activation only. A re-derived `true` or `unknown` forces review-required; an activation carrying explicit operator approval still proceeds, since that approval is the review this gate routes to. Refusing a reviewed-and-approved cross-family-captured candidate would be the outright-refusal reading this contract does not adopt.
- `cross_family_capture` is reserved to the deriving writer. Caller-supplied occurrences of it in candidate input carry no authority and are discarded, the value being re-derived from the source record in both directions - supplied input can neither introduce nor suppress the mark.
- A promotion-written record carries its candidate's risk flags in its own content, so the durable review artifact records why the candidate was gated. The obligation is discharged in record content; the C-MEM-08 entry shape is unchanged.

## C-MEM-11 - Retrieval and ranking

### Contract

Retrieval accepts:

```text
MemoryRetrievalRequest {
  run_id: string
  workflow_id: string | null
  workload_class: string | null
  cli_profile: string
  provider: string
  model: string
  query_summary: string
  scope: MemoryScope
  token_budget: int
  allowed_kinds: list<string>
}
```

Retrieval returns:

```text
MemoryRetrievalResult {
  request_hash: sha256
  selected_refs: list<memory_id>
  excluded_refs: list<ExcludedMemoryRef>
  packet_hash: sha256
  ranking_trace: list<RankingTraceEntry>
}
```

Ranking factors:

- Scope match.
- Recency.
- Confidence.
- Source authority.
- Explicit pinning.
- Failure-risk relevance.
- Workflow and CLI profile match.
- Supersession, expiry, redaction, and denial filters.

### Invariants

- Fixed store, fixed policy, fixed request, and fixed index version must produce a stable result.
- Retrieval operates over persisted records, persisted summaries, and derived indexes; any LLM summarization occurs before retrieval as ledgered capture or promotion work.
- Excluded refs must carry a reason when they were considered but denied.
- Retrieval writes a durable retrieval event.

## C-MEM-12 - Memory packet assembly

### Contract

A memory packet is a bounded, source-linked representation of selected records:

```text
MemoryPacket {
  packet_id: string
  packet_hash: sha256
  token_budget: int
  access_mode: native_provider_memory | standard_memory_tools | prompt_extension_packet | no_memory_access
  sections: list<MemoryPacketSection>
  selected_refs: list<memory_id>
  policy_ref: string
}
```

Stable section order:

1. Active operator/project preferences.
2. Current project conventions.
3. Relevant prior decisions.
4. Failure learnings and hazards.
5. Research or domain facts.
6. Procedural notes.

### Invariants

- Packet content must cite memory refs.
- Prompt-extension packets are read-only.
- Packet assembly writes or references an injection decision before provider dispatch when injection is used.
- Packet text must not include redacted or denied records.

## C-MEM-13 - Provider memory access modes

### Contract

Provider memory access mode is selected from:

```text
MemoryAccessMode =
  native_provider_memory |
  standard_memory_tools |
  prompt_extension_packet |
  no_memory_access
```

Selection inputs:

- Provider capability reflection.
- Model binding.
- Runtime provider route: enabled provider order, model family, fallback-chain primary, and, when the selected provider is an external CLI route, external CLI provider kind, command boundary, auth-check result, and optional/degradation state.
- CLI profile.
- Workflow policy.
- Step policy.
- Token budget.
- Record scope.

### Cross-family withholding of standard memory tools

When `standard_memory_tools` has been selected and the dispatched candidate's provider family differs from `MemoryScope.provider_family`, the harness MUST NOT expose the memory tool schemas or the scope reference for that dispatch. The dispatch proceeds without model-facing memory access, and the withholding is recorded with a named denial reason. Harness-authored memory capture is unaffected: capture is a different authorship class and crosses no boundary the harness does not already hold.

Recording surface. The withholding is recorded on the C-MEM-19 memory telemetry surface, whose declared coverage already includes standard memory tool calls and policy denial, with the denial reason carried as an attribute value. Where the withholding is realized as a transition of that dispatch to `no_memory_access`, this contract's `no_memory_access` must-ledger invariant applies unchanged and is satisfied by the existing `inject` memory operation entry and its injection-decision projection; no new operation kind is required. Where the withholding is not such a transition, no durable ledger row is owed: C-MEM-08's operation-kind vocabulary is closed and expresses no requested-but-withheld operation, and adding one would be a C-MEM-08 amendment that this contract does not imply.

Stated limit. Family equality is a necessary but not a sufficient trust condition for exposing model-facing memory. Within-family routing to a local terminal surface carries a distinct trust posture that this contract does not address and does not claim to cover.

### Invariants

- Anthropic native Memory is an adapter, not canonical storage.
- Tool-capable non-Anthropic providers may use standard memory tools.
- Providers without usable tool support may receive prompt-extension packets.
- External CLI provider routing remains the provider-construction authority; memory access mode is selected after the route is known.
- Local CLI OAuth/session tokens are never memory records and are never read by the memory layer.
- `no_memory_access` is a valid policy outcome and must be ledgered when memory was requested.
- Standard memory tools and the scope reference are withheld on a cross-family dispatch per the cross-family withholding rule above; the withholding is a recorded outcome, carried on the C-MEM-19 memory telemetry surface with a named denial reason.

## Memory threat model

### Threats

The memory substrate treats model-authored and external CLI-authored memory as untrusted until policy promotes it. The threat model covers:

- Cross-run prompt-injection persistence through promoted semantic/procedural memory.
- Cross-scope or cross-tenant retrieval leakage.
- Model-proposed preferences masquerading as operator instruction.
- External CLI memory import poisoning.
- Provider-side prompt cache retention after harness-side redaction.

### Invariants

- Model-authored notes are episodic by default and cannot become injectable semantic memory without policy and evidence.
- Operator-direct preferences are distinguishable from inferred or model-proposed preferences.
- Retrieval and injection enforce project, workflow, tenant, provider-family, CLI-profile, and visibility scope before ranking.
- Redaction can prevent future harness retrieval/injection, but cannot revoke content already sent to an external provider or provider prompt cache; that limitation must be ledger-visible when relevant.
- Redaction can prevent future harness retrieval/injection, but cannot erase committed git history. If redacted content entered git history, the redaction event records that residual persistence and any operator-managed history rewrite remains outside the memory layer.

## C-MEM-14 - Provider-neutral memory tools

### Contract

When `standard_memory_tools` is selected, the harness exposes provider-neutral tools:

| Tool | Purpose |
|---|---|
| `memory.search` | Search eligible records and return source-linked summaries. |
| `memory.read` | Read one allowed memory record or packet section by ref. |
| `memory.write_note` | Write an episodic note under policy. |
| `memory.propose_promotion` | Submit a promotion candidate for policy/review. |
| `memory.request_redaction` | Submit a redaction request. |

Exposure is subject to the C-MEM-13 cross-family condition: when the dispatched candidate's provider family differs from `MemoryScope.provider_family`, the tool schemas and the scope reference are withheld for that dispatch. A withheld exposure is a recorded outcome - carried on the C-MEM-19 memory telemetry surface with a named denial reason, per the recording-surface paragraph of C-MEM-13 - and not a violation of this contract. This qualification is a clarification of the "Tools cannot bypass scope, redaction, retention, or injection policy." invariant below - withholding enforces that invariant at the exposure boundary rather than at the call - and not an extension of it.

### Invariants

- Tools are policy-enforced at every call.
- Tools cannot bypass scope, redaction, retention, or injection policy.
- Write-like tools append durable memory operation entries.
- Tool output must include stable refs, not untracked memory prose.

## C-MEM-15 - Native provider memory adapters

### Contract

Native provider memory adapters translate provider-native operations into canonical memory operations.

For Anthropic Memory:

- `/memories` path discipline remains enforced.
- Native reads map to canonical store reads or derived packet views.
- Native writes map to policy-checked episodic or semantic operations.
- Native mutations append durable memory operation entries.

### Invariants

- Native adapter operations cannot write outside the canonical memory root.
- Native adapter path or content errors are observable.
- Native adapter writes cannot silently promote semantic memory unless policy allows.

## C-MEM-16 - CLI profiles

### Contract

CLI profile values:

```text
CliProfileKind = generic | claude_code | codex | antigravity | gemini_legacy | custom
```

```text
CliProfile {
  profile_id: string
  kind: CliProfileKind
  provider_name: string | null
  external_cli_kind: string | null
  command_name: string | null
  instruction_sources: list<CliInstructionSource>
  external_memory_sources: list<CliMemorySource>
  capability_flags: list<string>
  import_policy: deny | read_only | ledgered_import | bidirectional_sync
}
```

### Invariants

- `generic` must work without CLI-specific assumptions.
- `claude_code` may read Claude-specific instruction/progress conventions only by policy.
- `codex` may read AGENTS-style and Codex-local memory only by policy.
- `claude_code`, `codex`, `antigravity`, `gemini_legacy`, and `custom` profiles bind to existing external CLI provider identities where those providers are active.
- CLI profile loading must not define an independent provider order; it consumes the runtime route already selected by provider materialization and fallback-chain policy.
- External CLI memory stores are not silently modified.
- CLI profile identity is recorded in episodic and durable records.

## C-MEM-17 - Engine-class durability

### Contract

Memory operations bind to engine class:

| Engine class | Contract |
|---|---|
| `event-sourced-replay` | Memory operations occur inside activities; replay uses deterministic snapshots or monotonic versions. |
| `save-point-checkpoint` | Checkpoint state includes memory store version and packet hash. |
| `pure-pattern-no-engine` | Memory operations append state-ledger entries with idempotency keys. |
| `reconciler-loop` | Memory state binds to CR status, Memory CRD, or mounted canonical store with observed version. |
| `WAL-segment` | Restart rebuilds or prewarms memory from WAL plus canonical ledgers. |

### Invariants

- Replay must not re-run non-deterministic retrieval without a recorded store version or packet hash.
- Pending writes must not become visible as active semantic memory until their commit boundary.
- Engine binding is recorded in `MemoryOperationEntry`.

## C-MEM-18 - Redaction, tombstone, and retention

### Contract

Redaction and deletion are durable state transitions:

```text
MemoryRedactionEvent {
  event_id: string
  target_memory_id: string
  redaction_kind: content_redaction | scope_restriction | tombstone | retention_expiry
  reason: string
  actor: harness | operator | policy
  timestamp: timestamp
  replacement_summary: string | null
}
```

### Invariants

- Redacted records are excluded from packets and tools unless policy explicitly allows a replacement summary.
- Tombstoned records remain ledger-visible.
- Retention expiry writes an event before derived indexes drop the record.
- Content-bearing files may be physically redacted or compacted only through a ledgered redaction/retention operation that preserves the target memory id, old content hash, new content hash or tombstone hash, actor, reason, and timestamp.
- Append-only ledger history is not rewritten by redaction; retrieval eligibility is determined by the latest redaction/tombstone state.
- Git history persistence is ledgered when applicable; the memory layer does not silently rewrite git history.

## C-MEM-19 - Observability

### Contract

Memory telemetry covers:

- Capture.
- Retrieval.
- Ranking.
- Packet assembly.
- Injection.
- Promotion.
- Native adapter call.
- Standard memory tool call.
- Redaction and tombstone.
- Policy denial.

Required attributes:

```text
memory.tier
memory.operation.name
memory.access_mode
memory.provider
memory.model
memory.cli_profile
memory.policy.decision
memory.packet_hash
memory.record_count
memory.failure_class
```

### Invariants

- Existing `memory.*` telemetry remains compatible with the current six-attribute memory namespace; new attributes are additive and must not rename `memory.operation.kind`, `memory.path`, `memory.backend`, `memory.bytes_read`, `memory.bytes_written`, or `memory.context_editing_active`.
- Failure telemetry must distinguish policy denial, path violation, IO failure, serialization failure, provider adapter failure, and retrieval empty-result.

## C-MEM-20 - Verification contract

### Contract

The full layer must be verified by unit, integration, and cross-provider behavior checks.

Required verification:

- Schema validation for every record type.
- Path registry traversal rejection.
- Append-only ledger and hash-chain validation.
- Concurrent writer tests proving ledger streams do not fork under parallel append.
- Promotion policy tests, including preference promotion.
- Memory poisoning tests proving model-authored proposals cannot become injectable memory without policy approval.
- Compaction safety test proving durable candidate disposition.
- Retrieval determinism for fixed store/policy/request.
- Cross-scope and cross-tenant retrieval denial tests.
- Prompt packet fallback for a provider without native memory.
- Standard memory tools for a tool-capable non-native provider path.
- Native Anthropic adapter compatibility with existing `/memories` behavior.
- CLI profile resolution for generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom.
- Engine-class durability behavior for all five engine classes at the contract level.
- Redaction/tombstone exclusion from packets and tools.

### Completion rule

No implementation arc may claim the memory layer complete unless all `C-MEM-*` contracts are implemented and verified. A blocker may substitute for implementation only when it names an external dependency whose absence is verified by a deterministic probe and is recorded in a fork, roadmap, or credential-gate surface. A partial provider adapter is not sufficient.
