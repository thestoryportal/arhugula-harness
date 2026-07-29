# Class 1 Fork — B-92: C-MEM-10 promotion eligibility of records captured during a cross-family fallback leg

**Filed:** 2026-07-29 · autonomous-loop grounding arc (register `B-92`, registered by this filing).
**Classification: Class 1** — the memory spec is *deliberately* silent on whether a record captured during a
cross-family fallback leg is promotion-eligible under C-MEM-10, and the silence is load-bearing: it decides
whether content produced by one provider family can become injectable semantic/procedural memory attributed
to another. Resolution owes amendment text to `Spec_Memory_Substrate_v1.md` (C-MEM-10, and under two of the
three readings C-MEM-08 or C-MEM-03 as well). No `design-substrate/**` file is edited by this filing; the
spec leg is a separate follow-on arc per the B-33 / B-59 / B-70 / B-72 / B-86 precedent. `B-92` is registered
directly at `design_substrate_gated` (the B-70 discriminator: a real gap that needs spec-level CONTRACT text
before code — here reinforced by the fact that the spec *itself* named the question and declined to answer
it).

All code and spec cites below were re-grounded by direct read at HEAD `dd2a8c1a`, re-verified at
`6ab41d7f` on the R3 pass, at `ca0cc5a2` on the R4 pass, at `1c99e208` on the R6 pass, at `d8df7647` on
the R7 pass, at `d9907c24` on the R8 pass, and at `26720e8e` on the R9 pass (no code file under `harness-*/`
differs across those HEADs — every commit on this branch is doc-only; every R9 cite below was read directly,
not carried).

**RATIFIED 2026-07-29 — Reading B (flag + gate); Q2 routed to the spec leg. See §11.** The §8 ask is
answered; the next arc is the spec-writer apply leg, then the impl leg.

**Review status: R9 is the SOUNDNESS EXIT — this filing is CLOSED to further review rounds.** Nine
out-of-family rounds; the A/B/C readings, the Q1 recommendation of **B**, and the ratification ask have been
stable throughout; the ask's justification is precision-qualified at R9; all remaining sub-altitude mechanics
are routed to the spec leg **by rule**. See §10.

**Cite convention (Codex R3 [P2-2]).** `Spec_Memory_Substrate_v1.md` is cited **by contract ID + section name
+ a byte-verified quoted fragment**, never by line number. That is the spec's own instruction at its v1.1
change-note, "Surfaced finding, not patched.": *"Cite this spec by contract ID and section name, not by line,
in any text authored after v1.1."* — the anchor-drift class this workspace repaired at PR #1155. The same
convention is applied to `Implementation_Plan_Memory_Substrate_v1.md` (unit ID + subsection heading). Cites
into **code** files keep `file:line`, which is the fork-doc genre's existing convention and is sound because
each was verified at the HEADs named above; the two historical `:NNN` spec cites reproduced below are marked
as historical records of an earlier filing state, not live references.

## §1 The question, and what carries it

**The question.** A run's `MemoryScope.provider_family` is keyed to the fallback chain's PRIMARY family. On a
cross-family fallback leg the harness captures the *candidate's* output under the *primary's* scope. Under
C-MEM-10, is that record promotion-eligible — may it be promoted to a semantic or procedural record, and
thereafter injected into future runs, under the primary's family — on the same terms as a record whose
content was produced by the primary itself?

**Carrier 1 — the witness.** The behaviour is not hypothetical; it is asserted by a shipped test.
`harness-runtime/tests/test_automatic_memory_runtime.py:515`
(`test_u_mem_26_capture_is_unaffected_by_the_cross_family_withholding`) drives a real dispatch whose chain
primary is `anthropic` and whose dispatched candidate is `openai`, and asserts at `:579`:

```python
assert captured.envelope.scope.provider_family == ProviderFamily.ANTHROPIC.value, (
    "the captured record carries the run's COMPOSED family value, not the "
    "dispatched candidate's provider key (`B-89`)"
)
```

An `openai`-produced turn lands as an `anthropic`-family record. That is correct and intended per C-MEM-03
§"`MemoryScope.provider_family` value domain and derivation" — the run-level derivation rule (*"A fallback
chain is a continuity mechanism, and the run's memory partition is one of the run-level identities it
preserves across that boundary."*) and its paired writer-side obligation (*"records are written under the
run's composed record scope"*). What it means downstream at C-MEM-10 is the open question.

**Carrier 2 — the lineage.** The question was surfaced at the B-86 council convening (2026-07-28) as C3's
fourth forward item and carried, unresolved, through every artifact of that arc:

- `.harness/class_1_fork_b86_memory_scope_provider_family_keying.md` §7, fourth bullet: *"**C3
  promotion-eligibility question** (records captured during a cross-family leg under C-MEM-10) — flagged, out
  of B-86 scope, C-MEM-10 policy territory; carried here as a named open question for the spec-leg author to
  restate or discharge."*
- `design-substrate/Spec_Memory_Substrate_v1.md`, change-note (v1 -> v1.1), paragraph **"Named open question
  carried forward, not discharged."** — byte-exact:

  > **Named open question carried forward, not discharged.** Fork §7: whether records captured during a
  > cross-family fallback leg are promotion-eligible under C-MEM-10. That is C-MEM-10 policy territory,
  > outside B-86's scope; v1.1 neither resolves nor forecloses it, and it is restated here so it does not
  > disappear with the fork doc.

- `design-substrate/Implementation_Plan_Memory_Substrate_v1.md`, **U-MEM-26**, subsection **"Out of scope for
  this unit:"** (the sole occurrence of that heading in the file): *"Promotion eligibility of records captured
  during a cross-family fallback leg, which remains a C-MEM-10 policy question carried as a named open
  question at the spec v1.1 change-note."*

The spec-leg author restated it rather than discharging it. This filing is the discharge arc.

**Why it is Class 1 and not a Class 3 note.** The spec named the question, so nothing here is a newly
surfaced primitive (X-AL-3 is not engaged by the *question*). But every one of the three readings requires
CONTRACT text — C-MEM-10 today has no provenance term at all, and two of the three readings additionally
require a discriminator that does not exist at any contract (§3). An implementation choosing any reading on
its own authority would be silent absorption.

## §2 Current behaviour at HEAD `dd2a8c1a` — silent everywhere; permissive only where a future producer or policy makes it so

There are **two** promotion entry points. Neither has a family term — that is the contract gap, and it is
unconditioned. But **neither is a live auto-promotion exposure at HEAD**, and this filing is more useful for
saying so exactly. *(Both sharpenings below came from an out-of-family `just codex-review` R1 pass on the
first draft of this filing; each was re-verified by direct read before being absorbed. The first draft
asserted a live model-facing exposure and inferred the hint path's candidate family from the source record;
both claims were wrong, and both are corrected here rather than quietly dropped. A subsequent R2 pass found
two further accuracy defects — the review branch's durability, corrected inline below, and the §3 data-flow
claim's scope — both likewise re-verified by direct read.)*

**Entry point 1 — the hint-extraction path. The candidate-side family is PRODUCER-DEFINED, hence UNDEFINED
today.** `PromotionCandidateExtractor.extract_from_records`
(`harness-runtime/src/harness_runtime/memory_promotion.py:286-297`) reads hints from a stored record and
calls `_candidate_from_hint` (`:296`). Risk flags are built from the **hint**, with
`source_scope=record.envelope.scope` (`:626-629`) — the composed run scope, `anthropic` on the witness above.
`_scope_escapes_source` (`:698-712`) delegates the family comparison to `_family_escapes_source`
(`:715-743`), which canonicalizes both sides. But the **candidate** side it compares is
`hint.suggested_scope` (`:682`), and `suggested_scope: MemoryScope` (`:191`) is a **required, caller-supplied
field with no default and no derivation from the record**. Nothing in the pipeline makes it the record's
family. So the relation between the two families is a property of a producer that does not exist yet:

- a producer that mirrors the composed run scope supplies `anthropic` — equal to the source, no `CROSS_SCOPE`;
- a producer that supplies the *dispatched* family (`openai`) **already trips `CROSS_SCOPE`** at `:683`.

Neither outcome is a promotion *gate* (see the inert-flag finding below), but the distinction is load-bearing
for the ask: **which of the two a producer must supply is itself part of what C-MEM-10 owes**, and it cannot
be read off the code, because there is no producer to read. What *is* settled is `_auto_promote_allowed`
(`:776-790`): it consults `review_required`, `resolution.review_mode`, `hint.confidence` and
`hint.proposed_kind` — **no family term, and no risk-flag term**. The path is also **unfed**: the sole
production caller of `capture_turn_completion` passes `promotion_candidates=()`
(`harness-runtime/src/harness_runtime/automatic_memory.py:273`), and the extractor is otherwise reached only
from compaction safety (`memory_compaction_safety.py:159`).

**Entry point 2 — the model-facing tool path. NOT a live auto-promotion exposure at HEAD, for two independent
reasons.** `MemoryToolExecutor._propose_promotion`
(`harness-runtime/src/harness_runtime/memory_tool_executor.py:399-435`) serves the C-MEM-14
`memory.propose_promotion` tool (C-MEM-14 Contract, tool table: *"| `memory.propose_promotion` | Submit a
promotion candidate for policy/review. |"*). It reads a source record **by reference**
(`:408-411`), hardcodes `confidence=PromotionCandidateConfidence.HIGH` (`:423`), takes `auto_promote_allowed`
from policy alone (`_promotion_auto_allowed`, `:897-903`), and computes `risk_flags=_promotion_risk_flags(source)`
(`:425`) — which inspects **only** `redaction_state` (`:882-885`). *That* — no scope comparison of any kind —
stands. What does **not** stand is treating the path as reachable for a captured record:

1. **The record kind is denied before a candidate is ever constructed.** `_read_retrievable_record_by_ref`
   (`:554-567`) routes the source record through `resolve_retrieval`, and `_record_kind_allowed`
   (`harness-is/src/harness_is/memory_policy.py:327-333`) denies any kind outside the policy's
   `eligible_record_kinds` (`:300-304`). The **sole** production policy — `_policy_from_config`
   (`automatic_memory.py:532-557`), the only *enabled* `MemoryPolicyDocument` constructed anywhere under
   `src/` (the other is `DEFAULT_DISABLED_MEMORY_POLICY`, `memory_policy.py:105`, `enabled=False`, which
   denies everything) — sets that set to `_retrievable_kinds()` (`:560-569`): the seven **promoted/derived**
   kinds. Every kind the capture path writes is excluded — `EPISODIC_RUN` / `EPISODIC_TURN` / `TOOL_EVENT` /
   `COMPACTION_EVENT` (`memory_tool_executor.py:769-775`) — which covers the witness's `EPISODIC_TURN` and
   also `memory.write_note`'s own output (`capture_tool_event`, `record_kind=MemoryRecordKind.TOOL_EVENT`,
   `memory_capture.py:471-473`). The call raises `MemoryToolExecutionDeniedError` (`:565-566`) before
   candidate construction at `:417`.
2. **And an eligible record could not auto-promote either.** `_policy_from_config:542` pins
   `promotion_decision=PromotionDecision.PROPOSE_SEMANTIC`, and `_promotion_auto_allowed` (`:897-903`)
   returns True only for `PROMOTE_SEMANTIC` / `PROMOTE_PROCEDURAL`. So `auto_promote_allowed` is False for
   **every** candidate on this path today and `_propose_promotion` takes the `propose_for_review` branch
   (`:456`) with `review_required=True`. **That branch is durable but inactive — not ephemeral.** *(The R2
   correction; the first draft's "eligible records reach review, not durability" was wrong.)*
   `PromotionDecisionService.propose_for_review` (`memory_promotion.py:328-352`) calls `_persist_decision`
   with `status=SemanticRecordStatus.PROPOSED`, and `_persist_decision` (`:451-506`) writes **both** the
   semantic/procedural record (`self._store.write_record`, `:498`) **and** a durable C-MEM-08 memory-operation
   entry (`append_memory_operation`, `:499-506`). What review withholds is **activation**, not persistence: a
   `PROPOSED` record is excluded from retrieval by construction (`_INACTIVE_STATUS_REASONS["proposed"]` →
   `RetrievalExclusionReason.PROPOSED`, `harness-is/src/harness_is/memory_retrieval.py:65` / `:71-77`), so it
   is never injected. But it exists, it accumulates, and only `approve` / `edit_and_approve` (`:354-390` /
   `:416-449`) flip it to `ACTIVE` — neither consulting any family term. This does **not** re-open a live
   exposure: reason 1 above still denies every captured kind before a candidate is built, so nothing reaches
   this branch for a capture-path record today. What it does change is the shape of what the interim buys: for
   any record that *is* eligible (the second-order case — a record already promoted out of a cross-family leg),
   review produces a **durable** proposed record carrying the same unrecorded provenance, and the
   operator-review flip that activates it has no family term either.

**What the question therefore is, stated exactly.** Not "a live tool auto-promotes cross-family-captured
content today." It is:

- **Future retrievable-kind records.** `eligible_record_kinds` is a C-MEM-09 **policy** field, not a constant;
  a policy admitting an episodic kind makes the captured record readable through this tool immediately. And a
  **second-order** case needs no policy change at all: a semantic/procedural record *already promoted* out of
  a cross-family leg is an eligible kind by construction, and carries the same unrecorded provenance forward
  into every later promotion and injection.
- **Future policy configs.** A `PROMOTE_SEMANTIC` / `PROMOTE_PROCEDURAL` promotion decision under
  `ReviewMode.AUTOMATIC` — a configuration C-MEM-09 explicitly permits, and whose review-mode half is
  *already* the production setting — makes the tool path auto-promoting for every kind it admits, with no
  family term anywhere for it to consult.
- **A first hint producer.** The moment one populates `promotion_candidates`, entry point 1 becomes live with
  its candidate-family convention still unpinned.

**None of these is individually sufficient, and the filing states the combinations rather than leaving "a
single policy field" to imply otherwise** *(out-of-family `just codex-review` R6 [P2-2]; upheld and verified by
direct read at `1c99e208`. An earlier draft's "a single policy field or a first producer converts this into a
live exposure" was true of **candidate-reachability**, not of **active promotion**, and the two are worth
separating exactly because the interim-ending triggers at §7 are read off them.)* The gate functions are
conjunctions, and one of their conjuncts is **already satisfied in production**:

| Change | What it enables **on its own** |
|---|---|
| **(a)** admit a capture-written kind into `eligible_record_kinds` | **Candidate-reachability only.** The record survives `_read_retrievable_record_by_ref` and a candidate is constructed — but `_policy_from_config` still pins `PROPOSE_SEMANTIC` (`automatic_memory.py:542`), so `_promotion_auto_allowed` (`memory_tool_executor.py:897-903`) is False and `_propose_promotion` takes `propose_for_review`: a **durable `PROPOSED`** record, retrieval-excluded, never injected. |
| **(b)** switch the promotion decision to `PROMOTE_SEMANTIC` / `PROMOTE_PROCEDURAL` | **Active auto-promotion — but only of already-eligible kinds**, i.e. exactly the **second-order** case above (a semantic/procedural record already promoted out of a cross-family leg). Every capture-written kind is still denied at (a)'s gate before a candidate exists. |
| **(c)** set `ReviewMode.AUTOMATIC` | **Nothing — it is already set.** `_policy_from_config` pins `review_mode=ReviewMode.AUTOMATIC` (`automatic_memory.py:555`). This conjunct of `_promotion_auto_allowed` is satisfied at HEAD; only the decision conjunct is not. Correspondingly, the *other* two review modes are live foreclosures a deployment could re-assert: `ReviewMode.OPERATOR_REQUIRED` forces `review_required` (`:889-890`), and `ReviewMode.FORBIDDEN` denies the tool outright at `:406-407`. |
| **(d)** a first caller populating `promotion_candidates` | **Nothing promotable, on two counts.** Under the production policy `_review_required` (`memory_promotion.py:762-773`) returns True for `PROPOSE_SEMANTIC`, so `_auto_promote_allowed` (`:776-790`) is False; and even set True it actuates nothing — see below. |

- **Tool path (entry point 2) — live auto-promotion of a *captured* record requires (a) ∧ (b)**, with (c)
  already true. Both are constructor arguments of the sole production policy, hard-coded side by side at
  `_policy_from_config` (`automatic_memory.py:542` and `:556`) and drawn from **no** `config.memory` field, so
  today this is a code change rather than a deployment setting — but they are C-MEM-09 **policy** fields by
  contract, which is precisely why the contract gap is real regardless of how they are currently sourced.
- **Hint path (entry point 1) — requires (d) ∧ (b) ∧ non-`LOW` hint confidence ∧ an actuator that does not
  exist.** `_auto_promote_allowed` additionally demands `hint.confidence` not `LOW` (`:786-787`) and, for a
  `PROCEDURAL_UPDATE` kind, `PROMOTE_PROCEDURAL` specifically (`:788-790`). And satisfying all of it still
  promotes nothing: the **only** `PromotionDecisionService.approve` call site anywhere under `src/` is the
  tool path's (`memory_tool_executor.py:449`). `extract_from_records` is reached solely from
  `CompactionSafetyHook.extract_candidates` (`memory_compaction_safety.py:153-159`), whose sibling
  `complete_compaction` (`:161-209`) persists the auditable **disposition** set and never promotes — and
  `CompactionSafetyHook` itself has no production caller at all, appearing under `src/` only at its definition
  and its `harness_runtime/__init__.py` export. So on this path `auto_promote_allowed=True` is a value that is
  **computed and persisted and actuated by nothing**.

**The inert-flag finding — unchanged, and still load-bearing.** `risk_flags` **gates nothing today**. A
repo-wide grep finds it only at its definition, its two construction sites, and its persistence
(`memory_promotion.py:175/193/222/576/626/649/672/677`, `memory_tool_executor.py:425/882`); no gating
predicate reads it. `_review_required` (`memory_promotion.py:762-773`) never consults it, and
`_auto_promote_allowed` reads `review_required`, not flags. So `CROSS_SCOPE` — including the one a
dispatch-family hint producer would already trip — is **advisory metadata that is carried and persisted and
never acted on**. Any reading that relies on flagging must therefore state the **gate** as well as the flag,
or it lands inert — the enforced-vs-advisory distinction the workspace has been bitten by before.

**The §1 witness stands regardless.** Nothing above touches it: it pins the **capture-side** fact — an
`openai`-produced turn lands as an `anthropic`-family record — which is what makes the C-MEM-10 question
well-posed at all. The corrections concern what the *promotion* side does with such a record, not whether
such a record exists.

**Net, corrected.** The permissiveness is **structural, not yet exercised**. No family term exists at either
entry point or in any policy field, and on the **composed-scope capture path — the U-MEM-26 production
path** — no record of the producing family survives to promotion time (§3).
Live auto-promotion exposure at HEAD is **nil** — the tool path is closed twice over (by record kind and by
policy decision), the hint path is unfed, its candidate convention undefined, and its result actuated by
nothing. What is real *now* is the contract gap — which **no single named change converts into a live
exposure**, and which the combination table above states exactly: **(a) ∧ (b)** on the tool path (with (c)
already satisfied in production), or **(d) ∧ (b) ∧ an actuator** on the hint path. What a single change *does*
buy is the **transition below it** — (a) makes captured records candidate-reachable and durably `PROPOSED`;
(b) makes the second-order case actively auto-promoting — and each such transition happens **with no further
review**, because there is no family term at any of these gates to consult. That is precisely why this is a
Class 1 spec question and not a Phase 7 bug — and it is also why the urgency is **low and the necessity is
not**: nothing is leaking today, the last step to leaking is a two-field policy change nothing forbids, and
the contract has no position to fall back on when it happens.

## §3 The prerequisite finding — on the composed-scope path (the U-MEM-26 production path), the pipeline cannot discriminate even if policy said to

**This is the load-bearing part of the filing.** Two of the three readings below are not merely unbuilt; they
are currently *unrepresentable* — on the path where the question arises at all.

**Scoping first, because the data flow is not uniform.** *(The R2 correction; the first draft asserted an
exhaustive two-destination flow for `provider` that in fact holds only on the composed-scope path.)*
`EpisodicMemoryCapture` takes `record_scope: MemoryScope | None = None`
(`harness-runtime/src/harness_runtime/memory_capture.py:253`), and `_scope_for_record` (`:1048-1086`) branches
on it:

- **Composed-scope path (`record_scope` supplied).** The envelope scope is the run's composed scope (`:1074`),
  passed through the write boundary's canonicalize-or-deny (`:1083-1086`) — deliberately, per B-89. The
  per-dispatch `provider` argument does **not** reach the envelope. This is the **production** path: the
  automatic-memory runtime always supplies a composed scope whose `provider_family` is
  `fallback_chain.primary.family.value` (`automatic_memory.py:211-221`, the family at `:217`), threaded to the
  capture API at `:504-512` (`record_scope=scope`, `:511`). It is also the path the §1 witness exercises.
- **Residual path (`record_scope` absent).** `_scope_for_record` builds the scope itself with
  `provider_family=provider` (`:1075-1082`, the field at `:1079`) — the per-dispatch key, canonicalized by the
  same `:1083-1086` boundary. Such a record therefore **does** retain its producing family, so the exhaustive
  claim below does not hold for it. But it retains that family by **partitioning the record under it** — the
  per-turn re-derivation B-89 named as a defect and B-90 / U-MEM-26 repaired — which means the cross-family
  question **does not arise on this path at all**: a record written under the producing family is not a
  foreign-family record sitting inside a primary's partition, and there is nothing for C-MEM-10 to
  discriminate. The residual construction is retained only for callers with no composed scope.

**The prerequisite finding's force is therefore undiminished, and this is the precise claim:** the path where
the C-MEM-10 question is well-posed is exactly the path that cannot answer it — and it is the production path.
Everything below is scoped to it.

**On the composed-scope path.** `EpisodicMemoryCapture.capture_turn_completion` writes a `content` mapping
(`:407-422`) carrying `event_type`, `run_id`, `turn_id`,
`step_id`, the two summaries, `summary_source`, `summary_model`, `summary_hash`, `capture_mode`,
`tool_event_refs`, `failure_observations`, `promotion_candidates`, and `token_usage`. **No `provider` field
and no dispatched-`model` field.** The `provider` and `model` arguments are passed through to `_capture`
(`:431-432`) and from there to two places only — the envelope scope being the *third* destination the residual
path adds and this path does not:

1. the C-MEM-08 memory-operation ledger row — `_operation_payload(..., provider=provider, model=model, ...)`
   (`:694-707`), which constructs a `MemoryOperationPayload` carrying `provider` (`:1006`), `model` (`:1007`)
   and `memory_refs=(memory_id,)` (`:1010`); and
2. the C-MEM-19 telemetry span attributes (`:686-688`, `:714-716`).

Promotion never reads either. `_hints_from_record` (`memory_promotion.py:545-560`) reads
`record.content` alone; `_propose_promotion` reads `source.envelope` and `source` content. **There is no path
from a composed-scope stored record to the provider family that actually produced its content.**

Consequence: readings **B** and **C** below cannot be implemented for composed-scope records — i.e. for every
record the production path writes — until a discriminator is surfaced, and surfacing one is itself
contract-altitude work (§5) — X-AL-3-blocked at Phase 7. Only reading **A** is
implementable against the substrate as it stands (and reading A's "implementation" is a spec sentence, not
code).

## §4 The three readings

### Reading A — promotion-eligible, unchanged; the permissiveness made EXPLICIT

C-MEM-10 gains a sentence stating that a record's promotion eligibility is determined by its record scope and
its policy/evidence, and is **not** conditioned on which provider family produced its content during a
fallback leg. Status quo behaviour is unchanged; what changes is that it becomes a *stated* position rather
than an accident of a pipeline that cannot see the fact.

Rationale:

- **The composed scope IS the run's declared identity.** C-MEM-03 §"`MemoryScope.provider_family` value domain
  and derivation" states the run-level derivation as contract: *"A fallback chain is a continuity mechanism,
  and the run's memory partition is one of the run-level identities it preserves across that boundary."* A
  record inside that partition is, by the contract's own construction, a record of that run. Conditioning
  promotion on sub-run provenance re-introduces at C-MEM-10 exactly the per-dispatch partitioning that same
  derivation rule forbids at C-MEM-03.
- **Capture-time scoping was ratified at B-86/B-89 on exactly this ground.** C-MEM-13 §"Cross-family
  withholding of standard memory tools": *"Harness-authored memory capture is unaffected: capture is a
  different authorship class and crosses no boundary the harness
  does not already hold."* That carve-out is about **capture**, and it does not extend itself to promotion.
  **Promotion is a reach transition, not a durability one** *(the R4 correction; a first draft of this bullet
  said "promotion confers durability on content the harness holds, and grants the foreign candidate no new
  reach", and both halves were wrong — stated here rather than quietly repaired)*:
  - The captured record is **already durable**. `_capture` writes it to the canonical store —
    `self._store.write_record(record)` (`memory_capture.py:730`) — *before* its C-MEM-08 row, deliberately, so
    that a ledger failure downgrades to "an orphaned-but-safe record … the record itself is durable"
    (`:721-729`). Promotion adds nothing on this axis.
  - What promotion adds is **injectability**. Every kind the capture path writes sits outside the sole
    production policy's `eligible_record_kinds` — `_policy_from_config` pins it to `_retrievable_kinds()`
    (`automatic_memory.py:556`, defined `:560-569`: the seven promoted/derived kinds, no episodic / tool-event
    / compaction-event kind among them) — and a `PROPOSED` promotion output is excluded from retrieval by
    construction (`memory_retrieval.py:71-77`). Only an **ACTIVE** semantic/procedural record is retrievable,
    and therefore injectable into a future run's context.
  - So foreign-produced content **does** gain new reach at promotion: content that could not enter a future
    run's context becomes content that can, under the primary's family attribution. That is precisely the
    channel the Memory threat model §Threats names — *"Cross-run prompt-injection persistence through promoted
    semantic/procedural memory."* — and precisely the transition §Invariants governs: *"Model-authored notes
    are episodic by default and cannot become injectable semantic memory without policy and evidence."*
  - What gains nothing is the foreign **provider**: it acquires no capability, no tool, and no boundary
    crossing it did not already have. *That* is the true residue of the C-MEM-13 carve-out, and it is a much
    narrower claim than the one it replaces.

  Reading A's honest form is therefore **"the reach transition is acceptable because the composed scope is the
  run's declared identity"** — the first bullet, which is unweakened — **not** "there is no reach transition."
- **The content passed the same capture pipeline as any other record** — same redaction state, same
  `summary_source`, same policy resolution.

Cost: cheapest by a wide margin (one contract paragraph, zero code, zero discriminator). Risk: it ratifies —
at the exact contract that governs the reach transition just described — a permissiveness that policy has
never actually evaluated. See §7.

### Reading B — eligibility preserved, silence removed

Cross-family-produced candidates remain eligible, but a candidate whose source record was captured during a
cross-family leg is marked with a `CROSS_SCOPE`-equivalent risk flag **and** that mark is made
gate-bearing: such a candidate is `review_required` and never `auto_promote_allowed`. Continuity is
preserved; what is removed is *silent* auto-promotion.

Rationale:

- The memory threat model already treats provenance as a first-class axis: §Threats opens *"The memory
  substrate treats model-authored and external CLI-authored memory as untrusted until policy promotes it."*,
  and §Invariants carries *"Model-authored notes are episodic by default and cannot become injectable semantic
  memory without policy and evidence."* Promotion is the trust-conferring step, and §Threats bullets
  *"Cross-run prompt-injection persistence through promoted semantic/procedural memory."* as a covered
  threat — the exact channel this question sits on.
- It satisfies C10's B-86 position (a durable, primary-attributed, promotion-eligible write needs a real
  gate) at the *right* mechanism, without paying C3's continuity cost — structurally the same move B-86
  itself made (keep the run-level partition; satisfy the safety voice at a different mechanism).

Cost: requires the §3 discriminator. **And it must state the gate, not only the flag** (§2's grounded
correction): a flag alone is inert at HEAD.

### Reading C — refuse promotion of cross-family-captured records

Strongest isolation: such records are ineligible for promotion outright; they remain episodic and
retrievable, but can never become injectable semantic/procedural memory.

Rationale for: closes the cross-run prompt-injection-persistence channel (Memory threat model §Threats)
completely for foreign-family content; needs no judgement about
*how much* review is enough.

Rationale against, and it is the B-86 council record's own argument:

- **C3 (state / memory / persistence), condition of concurrence at the B-86 convening** — reproduced at
  `.harness/class_1_fork_b86_memory_scope_provider_family_keying.md` §4: candidate-side partitioning *"makes
  the moment accumulated context matters most (the fallback leg) the moment it disappears — silent,
  permanent, inverted-in-timing data loss."* Reading C resurrects precisely that harm in a narrower register:
  the fallback leg's records become permanently second-class. The fallback leg is, by construction, the leg
  where the run was in trouble — and therefore often the leg carrying the most promotion-worthy learning.
- **C6 (model routing), refinement adopted at that convening** — *"a fallback chain is a **continuity**
  abstraction, not a substitution abstraction — every other run-level identity is preserved across the
  boundary; `provider_family` has no principled reason to be the exception."* Reading C makes
  `provider_family` the exception at C-MEM-10 after B-86 declined to make it the exception at C-MEM-03.
- Reading C also still requires the §3 discriminator (it must know *which* records to refuse), so it is not
  cheaper than B — it is B plus a foreclosure the council explicitly wanted avoided.

## §5 Prerequisite mechanics — the two discriminator options

Both B and C require the harness to know, at promotion time, that a record's content was produced on a
cross-family leg. Two options; they are not equal in cost.

### (i) A new content or envelope field at C-MEM-03 altitude

Capture stamps the dispatched provider family (or a boolean `captured_cross_family`) onto the record itself.
**These are two variants with materially different blast radii, and the R6 finding is that the cost analysis
was written as if they were one** *(out-of-family `just codex-review` R6 [P2-1]; upheld and verified by direct
read at `1c99e208`)*. The consequence the R4 draft charged to the whole of (i) — moved record identities —
belongs to the **content** variant only. Both are stated separately below, and the (i)-vs-(ii) comparison is
re-run against the cheaper one.

**[R8] Option (i) varies along TWO independent axes, not one, and the second was named in the sentence above
and then costed nowhere.** *(out-of-family `just codex-review` R8 [P2-2]; upheld and verified by direct read at
`d9907c24`.)* The axes are **placement** (content vs envelope — the R6 split) and **payload** (a *family value*
vs the *boolean* `captured_cross_family` this section's own opening sentence offers). Every cost bullet below
the opening was written for the family-value payload: "a *second* family-valued field … with its own null
semantics, sitting beside `MemoryScope.provider_family`" is **not** true of a boolean, and neither is the
C-MEM-03 value-domain reconciliation. Since the leveling assessment further down was computed from those
bullets, the boolean was priced as if it carried costs it does not. The universal costs are restated below as
universal, the family-payload costs are moved onto the family payload, and the boolean is analysed on its own
at **(i-envelope-bool)** — including what it structurally **cannot** answer, which is the other half of an
honest comparison.

**What every variant pays — placement and payload alike.**

- **A closed-schema amendment either way.** `MemoryRecordEnvelope` carries
  `model_config = ConfigDict(extra="forbid", frozen=True)`
  (`harness-is/src/harness_is/memory_record_envelope.py:129`), as do `MemoryScope` (`:115`) and `SourceRef`
  (`:97`) — an envelope addition is a real field addition at a closed model, not an open-map extension. And at
  contract altitude the distinction does not exist at all: C-MEM-03's field shapes were preserved
  *byte-unchanged* at v1.1, and the change-note says so explicitly at **"Sections preserved verbatim at
  v1.1."**: *"Zero new record type, zero new field, zero new enum member, zero change to any ledger, packet, or
  telemetry shape."* Either variant reverses that posture one delta later.
- **[R9] ONE central derivation site — NOT "every capture writer". The prior bullet was false about the code,
  and is corrected here rather than quietly repaired.** *(out-of-family `just codex-review` R9 [P2-1]; upheld
  and verified by direct read at `26720e8e`.)* It read: *"Touches every capture writer. Six `capture_*` methods
  plus `_capture` / `_record` thread the new value, whatever its payload shape."* There are **seven**
  `capture_*` methods, not six (`memory_capture.py:294` / `:337` / `:382` / `:439` / `:487` / `:534` / `:585`,
  all on `EpisodicMemoryCapture`, `:241`), and **none of them needs to thread anything**: every one already
  takes `provider: str | None` and already passes it to `_capture` (`:321` / `:366` / `:423` / `:471` / `:518` /
  `:569` / `:615`), which threads it into `_record` (`:649-658`). `_record` (`:1015-1046`) therefore already
  holds **both** inputs the predicate needs — the call's raw `provider` (`:1025`) and the record's resolved
  scope, returned by `_scope_for_record` (`:1038-1042`, defined `:1048-1086`, whose `resolve_scope_family`
  output is canonical by construction and has already refused an out-of-domain family). The derivation is a
  **single hoist inside `_record`**: compare the canonicalized call `provider` against `scope.provider_family`
  and store the answer. **Zero per-method threading; zero signature change at any public writer.** An optional
  field defaulted to the tri-state's *unknown* value likewise leaves the other three `MemoryRecordEnvelope`
  construction sites untouched (`memory_promotion.py:844`, `native_memory_adapter.py:463`,
  `memory_compaction_safety.py:327`) and lets a pre-amendment serialized envelope still validate under
  `extra="forbid"`. *(The default must be **unknown**, never `false` — which is the tri-state obligation stated
  at (i-envelope-bool) below, reached here by a second route.)*
- **Its own null / unknown semantics, whatever the payload.** A writer that cannot determine the value must
  record *unknown* rather than a default, or reading B inherits the permissive-by-silence defect §2 documents
  in a new place.
- **Forward-only, absent a back-fill migration.** A record written before the amendment carries no field at
  all, so the pre-amendment corpus is `UNVERIFIABLE` under (i) by construction. A back-fill is not impossible —
  it would be option (ii)'s join run offline over the existing corpus — but it is then (ii)'s cost, and it
  inherits (ii)'s whole unresolvable set.
- **The R3 multi-writer exception, which no variant escapes** — recorded at the assessment below, where
  the `EPISODIC_RUN` overwrite path was re-verified for the **envelope** variant specifically rather than
  assumed from the content one: on `EPISODIC_RUN`, which is one stored record per run written by run-start and
  overwritten by run-close, a stored field is set by *whichever writer ran last* and records nothing about
  which that was.

**(i-content) — a field inside the record's `content` mapping. Moves identities.** Content is hashed, and the
hash *is* the identity. `compute_memory_content_hash(content)` digests the canonicalized **content mapping
alone** (`harness-is/src/harness_is/memory_record_envelope.py:207-210`, over `canonicalize_memory_content`,
`:189-204`, which omits only top-level `derived_indexes`), and `derive_memory_id(tier, kind, content_hash)`
(`:213-222`) composes `mem:{tier}:{kind}:{hex}` from it. The spec states the same at C-MEM-03 §Invariants:
*"`content_hash` is computed over canonical serialized content excluding derived indexes."* So a new content
field changes `content_hash` and, through it, the `memory_id` of every newly written record of every kind
**except** `EPISODIC_RUN`, whose id derives from the `run_id` alone and is content-independent
(`_memory_id_for`, `harness-runtime/src/harness_runtime/memory_capture.py:1100-1109`). That needs an explicit
forward-only statement in the contract.

**(i-envelope) — a field on `MemoryRecordEnvelope`. Moves NO identities.** The envelope is not an input to
either hash. `_record` (`memory_capture.py:1015-1046`) computes `content_hash` from `content` at `:1027` and
`memory_id` at `:1028` **before** constructing the envelope around them (`:1030-1044`), and the store's own
consistency check re-derives it the same way — `expected_hash = compute_memory_content_hash(self.content)`
(`harness-is/src/harness_is/memory_store.py:95`). *(This also corrects a drifted cite carried since the R4
draft, which anchored `MemoryScope`'s hash-inertness at `memory_capture.py:574-575` — a `source_ref=` /
`run_id=` argument pair inside `capture_failure_observation`. The hash-inertness property is real; it is
carried by the three anchors named above, not by those lines. Corrected here rather than quietly repaired,
and stated as a cite defect because it is the exact claim this split rests on.)* So (i-envelope) leaves every
existing `memory_id` and every existing `content_hash` intact; on the identity axis it costs nothing.

**(i-envelope) is therefore the real contender, and (i-content) is strictly dominated by it** — (i-content)
pays identity movement for a discriminator the envelope carries for free, and buys nothing (i-envelope) does
not, since promotion reads the stored record and can read either field from it. The assessment below compares
(ii)/(ii-a) against **(i-envelope)**, in the cheaper of its two payload shapes.

**(i-envelope-family) — the payload is a provider-family value.** This is the shape every pre-R8 cost bullet
described. On top of the universal costs it pays **a second family-valued field on one record**: the new field
must be reconciled against the C-MEM-03 value domain (§"`MemoryScope.provider_family` value domain and
derivation"), it sits beside `MemoryScope.provider_family` meaning something different (the *dispatched* family
vs the record's *partition*), and its `null` must be distinguished from that field's `null`, which C-MEM-03
v1.1 defines as the unpartitioned wildcard. That is a one-source-of-truth hazard in its own right, and it is
the single largest item in (i)'s column. **What it buys for the price:** the *family pair* — a reader can ask
not only *whether* the leg was cross-family but *which* family produced the content, which is what any future
family-discriminating policy (e.g. "a local-open-weight fallback leg is acceptable, a remote one is not")
would need.

**(i-envelope-bool) — the payload is `captured_cross_family`, a tri-state, and it is the cheapest shape of (i).
[R8]** The field is a *derived predicate*, not a second authority on family: at capture the writer compares the
call's own `provider` — canonicalized by the existing house authorities, `provider_family_for_scope_check`
(`harness-runtime/src/harness_runtime/lifecycle/cross_family_cost_tag.py:101`) and `canonical_scope_family` /
`resolve_scope_family` (`harness-runtime/src/harness_runtime/memory_scope_family.py:50` / `:62`) — against the
record's own composed `scope.provider_family`, and stores the answer.

- **What it does NOT pay, against (i-envelope-family):** no new **value domain** (the contract states a
  *derivation rule*, not an enumeration to be reconciled against C-MEM-03's); no **second family-valued field**
  and therefore no one-source-of-truth hazard — a predicate over `MemoryScope.provider_family` is a
  *dependent* of that field, not a rival authority; and no new normalization posture, since the derivation
  reuses the B-86 / B-89 authorities verbatim.
- **What it still pays:** everything in "What every variant pays" — the closed-schema addition at
  `MemoryRecordEnvelope` (`extra="forbid", frozen=True`) reversing v1.1's zero-new-field posture one delta
  later; the one central derivation in `_record` **[R9]**; forward-only absent a back-fill. **A boolean is not
  a cheaper *schema* change than a family field — it is the same schema change with a narrower contract surface
  behind it.**
- **It must be a TRI-STATE, not a `bool`, and that is a contract obligation rather than a nicety.** The writer
  cannot always determine the predicate: `provider` is `str | None` at every `capture_*` signature (e.g.
  `memory_capture.py:302` / `:347` / `:396`), `provider_family_for_scope_check` returns `None` for an
  **unregistered** key and its own docstring requires scope-boundary callers to *fail closed* on that
  (`cross_family_cost_tag.py:101`), and the composed scope's `provider_family` may itself be `null` — the
  C-MEM-03 unpartitioned wildcard — against which "cross-family" is undefined. Storing `false` in any of those
  cases would record a determination the writer never made, which is exactly the permissive-by-silence defect
  this fork exists to close. The house idiom is already fixed: the **B-91 tri-state** (`MATCH` /
  `CONFIRMED_MISMATCH` / `UNVERIFIABLE`, report only a determination actually reached), and its third value
  maps to the same place (ii)'s does — `UNVERIFIABLE` → review_required, never auto-promote.
- **What it structurally CANNOT answer, stated as plainly as the upside.** (a) **Which** family produced the
  content — so reading B's flag semantics are bounded to *present / absent* ("captured on a cross-family leg"),
  never to a family pair, and any later family-discriminating policy needs a *second* amendment, this time
  paying (i-envelope-family)'s full price. (b) **Aggregate-run** provenance — unchanged from
  (i-envelope-family): the envelope carries its own writer's value only, so "did *any* leg of this run run
  cross-family" remains (ii)-only. (c) It bakes the comparison basis in **at write time**: the stored answer is
  relative to the composed scope as it stood at capture, and it cannot be re-derived under a different basis
  later, where a family value could be.
- **So: is the boolean the cheapest ADEQUATE discriminator for reading B specifically? On reading B as this
  filing has argued it — yes, plausibly, and the honest answer is to say so rather than leave it implied.**
  Reading B asks for a `CROSS_SCOPE`-equivalent **risk flag** plus a gate (§4, reading B; §6's drafting-target
  row), and a risk flag is a present/absent signal — `PromotionRiskFlag` is a flag vocabulary, not a family
  carrier. The boolean answers exactly that question and nothing more, at strictly less contract surface than
  the family value. It does not change (i)'s standing against **(ii)** on the three axes where (ii) wins
  (already-written records, write-side reach, aggregate-run provenance) — it only makes (i)'s own column
  cheaper. **The pick remains the spec leg's**, and it is the same requirement question §5 closes on: if
  C-MEM-10 will only ever need present/absent stored-version provenance, (i-envelope-bool); if it will need to
  discriminate *by* family, (i-envelope-family); if it needs aggregate-run provenance, neither — (ii).

- Upside, all variants: self-contained; no cross-contract read dependency; works for a record read in
  isolation — subject to the `EPISODIC_RUN` exception above.

### (ii) A C-MEM-08 ledger join at promotion time

Promotion resolves the record's capture row and reads its `provider`.

- **The join key exists with no schema change — but it is the capture `idempotency_key`, not `memory_refs`
  (and not `action_id` either — see (ii-a)).**
  `MemoryOperationEntry` (C-MEM-08 Contract) carries `provider: string | null`, `model: string | null` and
  `memory_refs: list<memory_id>`; the authoritative ledger for `capture` is `durable/memory_ops.jsonl`
  (C-MEM-08 Contract, "Projection mapping" table, row *"| `capture` | `durable/memory_ops.jsonl` | none |"*).
  **A first draft of this bullet said capture "writes exactly one `capture` row per record with
  `memory_refs=(memory_id,)`". That premise is FALSE for `EPISODIC_RUN`, and the correction is stated here
  rather than quietly repaired** *(out-of-family `just codex-review` R3 [P2-1]; verified by direct read at
  `6ab41d7f`)*. `_memory_id_for` (`harness-runtime/src/harness_runtime/memory_capture.py:1100-1109`) derives an
  `EPISODIC_RUN` `memory_id` from the **`run_id` alone** — content-independent — so `capture_run_start`
  (`:294-335`) and `capture_run_close` (`:337-380`) write **two** capture rows against **one** `memory_id`.
  The module states the consequence at the point it exports the remedy: `capture_operation_action_id`
  (`:68-77`) — *"run-start and run-close share a single EPISODIC_RUN `memory_id`, so `memory_refs` cannot tell
  them apart"* — and again at the repair-row probe (`:857-861`). Each `capture_*` method takes its **own**
  per-call `provider` (`capture_run_start(..., provider=...)` at `:302`, `capture_run_close(..., provider=...)`
  at `:347`; the runtime supplies the run-start selection at `automatic_memory.py:336`), so on a run whose
  fallback advanced between the two events the two rows carry **different provider keys**. A
  `memory_refs`-keyed join is therefore **not a function**: it classifies provenance by whichever row the scan
  happened to select. **Honest scoping, on the same footing as the rest of this filing:** `capture_run_close`
  has **no production caller at HEAD** (its only call site is `harness-runtime/tests/test_memory_capture.py:151`),
  so today every stored `EPISODIC_RUN` record does in fact carry exactly one row. Like every other exposure in
  §2, the ambiguity is **structural, not yet exercised** — and contract text must not rest on the accident,
  because the API is public and the module's own docstrings treat the two-row case as the operative invariant.
- **(ii-a) — the event-qualified join, which is the one the code already provides. [recommended]** The
  contract names the join key as the capture **`idempotency_key`**, itself composed from the capture
  `action_id`, which is composed from **the record's own declared writer**:

  ```
  Identifier(f"idempotent:{capture_operation_action_id(stored_capture_event_type(record.content), memory_id)}")
  ```

  Both inner halves are already exported, and their docstrings say they are exported for exactly this
  discrimination — `stored_capture_event_type` (`memory_capture.py:1149-1163`) is *"the record's own statement
  of WHICH event wrote it - the discriminator a reader needs when one `memory_id` is shared by several events
  (EPISODIC_RUN is one `run.json` per run, written by run-start and OVERWRITTEN by run-close)"*. Because the
  stored record is overwritten by its later writer, its `content["event_type"]` names the event that wrote
  **the version being promoted**, which is precisely the row whose `provider` is that content's provenance.

  **The uniqueness this join relies on is the `idempotency_key`'s, NOT the `action_id`'s** *(the R4
  correction; a first draft of this bullet said "the ledger's `action_id` idempotency makes a '>1 row' outcome
  unreachable rather than merely unlikely", and **there is no such thing as `action_id` idempotency in the
  ledger** — stated here rather than quietly repaired; out-of-family `just codex-review` R4 [P2], verified by
  direct read at `ca0cc5a2`)*. `append_memory_operation`
  (`harness-is/src/harness_is/memory_operation_ledger.py:522-545`) scans for a prior entry **by
  `idempotency_key` alone** (`:532-539`): an equal key with an equal 18-field equivalence payload returns
  `IDEMPOTENT_NOOP`, an equal key with a divergent payload raises `MemoryOperationIdempotencyConflictError`.
  `action_id` is a caller-supplied payload field carrying **no** ledger-enforced uniqueness whatsoever —
  nothing prevents two entries from sharing one `action_id` under different idempotency keys, so a join keyed
  on it is not guaranteed single-row. What makes the join well-defined is that the capture writer derives the
  key **deterministically** from the id — `idempotency_key=Identifier(f"idempotent:{action_id}")`
  (`memory_capture.py:999`, the sole construction site for every `capture_*` method) — so the key **is
  reconstructible at promotion time from the stored record alone**, and once reconstructed the ledger
  guarantees **at most one** occupying entry.

  Two consequences the contract must carry:

  1. **State the join on the key, not on the id.** "The capture row is found by the record's capture
     `action_id`" is under-specified in exactly the way that produced this finding; "found by the capture
     `idempotency_key` composed as above" is the property the ledger actually enforces.
  2. **Qualify on `operation_kind == CAPTURE`.** Writer namespacing (`capture:…` here, `promotion:…` at
     `memory_promotion.py:523-528` — which shares the *identical* `idempotent:{action_id}` spelling) is a
     convention across producers, not a ledger invariant. The matched row must be **confirmed** to be a
     capture row, never assumed to be one; a matched row of any other `operation_kind` is `UNVERIFIABLE`.
  3. **[R7] A matched row is not, by itself, a row about *this version of* the record — so the join owes a
     MANDATORY record/ledger coherence check, and the contract must state what that check can and cannot
     reach.** *(out-of-family `just codex-review` R7 [P1]; upheld and verified by direct read at `d8df7647`.)*
     The failure is exhibited by a **shipped test**, not hypothesized: in
     `test_a_divergent_second_run_start_capture_is_not_read_as_completion`
     (`harness-runtime/tests/test_u_mem_26_write_boundary.py:1602-1662`) a divergent second
     `capture_run_start` for one `run_id` — reachable because `EpisodicMemoryCapture` is a public API and
     `LocalAutomaticMemoryRuntime`'s presence guard is not in it — **overwrites `run.json` at
     `memory_capture.py:730` and only then meets the first call's row at `:732`**. The capture correctly
     returns `FAILED`, but the durable residue is a record holding **call two's** content beside a single
     ledger row holding **call one's** `provider`. Reconstructing the (ii-a) key against that record still
     resolves to exactly **one** `CAPTURE` row carrying a non-`None` provider — so every qualification stated
     above passes, and the join returns **stale provenance as if it were determined**. None of cases 1-5
     below catches it.

     **What is checkable, stated exactly, because the precision is the whole of this consequence.** No field
     on the capture row binds it to a stored-content *version*: `MemoryOperationEntry`
     (`harness-is/src/harness_is/memory_operation_ledger.py:136-154`) carries no content hash, and the
     `response_hash` it inherits from `StateLedgerEntry` (`state_ledger_entry_schema.py:164-169`) is computed
     over **the ledger entry's own** canonical payload (`compute_memory_operation_response_hash`, `:335-338`,
     over `canonicalize_memory_operation`, `:324-332`), never over the record's content; `memory_refs` carries
     the `memory_id`, which for `EPISODIC_RUN` is `run_id`-derived and content-independent. **So "bind the row
     to the stored content hash" is not available at HEAD** — the field does not exist. What *is* available is
     the set of values `_capture` threads from **one call** into **both** surfaces, which a coherent pair must
     therefore agree on:
     `entry.timestamp` ↔ `record.envelope.created_at` (the single `timestamp` argument, to `_record` at
     `:649-658` and to `_operation_payload` at `:694-707`); `entry.cli_profile` ↔ `content["cli_profile"]`;
     `entry.engine_class` ↔ `content["engine_class"]` (`_engine_class_value`, `:1122-1125`); `entry.step_id` ↔
     `content["step_id"]` on the kinds that carry one; and `entry.run_id` ↔ `content["run_id"]`, which is
     vacuous on this join because the key already derives from it. The `created_at` comparison must be scoped
     to **dispatch** rows: `repair_capture_operation` takes the repairer's own `datetime.now(UTC)`
     (`automatic_memory.py:442`), so a repair row never matches it — which costs nothing, because a repair row
     is already case 5.

     **[R8] That comparable-field set is PER-KIND, and the check is owed on `EPISODIC_RUN` ALONE — the list
     immediately above was read off the run kinds and misfires on every other one.** *(out-of-family
     `just codex-review` R8 [P2-1]; upheld and verified by direct read at `d9907c24`.)* Two independent facts,
     both verified at the capture methods:

     1. **The shared-value set differs by kind, and `cli_profile` / `engine_class` are NOT in it outside the run
        kinds.** Only `capture_run_start` (`memory_capture.py:309-320`) and `capture_run_close` (`:354-365`)
        write `cli_profile` and `engine_class` into **content**. `capture_turn_completion` (`:407-422`),
        `capture_tool_event` (`:459-470`), `capture_provider_route` (`:504-517`),
        `capture_failure_observation` (`:553-568`) and `capture_compaction_event` (`:604-614`) write neither —
        for those kinds both values reach the **ledger row only** (`_operation_payload`, `:1008-1009`).
        Conversely `step_id` is content-side on the turn / tool kinds and is `None` on **both** surfaces for the
        run kinds (`:328` / `:377`) and for compaction (`:622`). Run the R7 list unscoped and every turn / tool
        / compaction record fails the `cli_profile` comparison against an **absent** content field — the whole
        non-run corpus reads `UNVERIFIABLE` for a reason that is an artifact of the check, not a divergence.

        | Record kind (writers) | Content ∩ row values, beyond `created_at` ↔ `timestamp` | `memory_id` derivation |
        |---|---|---|
        | `EPISODIC_RUN` (`run_start`, `run_close`) | `cli_profile`, `engine_class` (`run_id` vacuous — the key derives from it; `step_id` is `None` on both sides) | `run_id` alone — **content-independent** |
        | `EPISODIC_TURN` (`turn_completion`, `failure_observation`) | `step_id`, `run_id` | `content_hash` |
        | `TOOL_EVENT` (`tool_event`, `provider_route`) | `step_id` (may be `None`), `run_id` | `content_hash` |
        | `COMPACTION_EVENT` (`compaction`) | `run_id` | `content_hash` |

     2. **And the window the check exists to close is `EPISODIC_RUN`-only, so on the other kinds a correctly
        scoped check would have nothing left to compare anyway.** `_memory_id_for` (`:1100-1109`) derives every
        non-run kind's id from `content_hash`, and `capture_operation_action_id(event_kind, memory_id)`
        (`:68-77`) composes the join key from that id — so for those kinds **the key IS a content binding**,
        which is precisely the binding R7 found missing for `EPISODIC_RUN`. A divergent re-capture there is a
        *different* `memory_id`, hence a different stored record with its own row; row and stored version
        cannot come apart. That also makes every **content-side** comparator in the table vacuous *by
        construction* on those kinds (any content field that differed would have moved the key), leaving
        `created_at` as the only live comparator — and it is the one that produces **false** `UNVERIFIABLE`s:
        `timestamp` is **not** in the ledger's equivalence payload
        (`_equivalence_payload_from_payload`, `harness-is/src/harness_is/memory_operation_ledger.py:499-519` —
        eighteen keys, `provider` at `:511`, no `timestamp`), so a benign identical-content re-capture at a
        later instant returns `IDEMPOTENT_NOOP` while re-writing the record with a new `created_at`, and for
        the three JSONL-backed episodic kinds the reader takes the **last** matching line (`_read_jsonl_record`,
        `harness-is/src/harness_is/memory_store.py:445-463`; `_JSONL_BY_KIND` at `:143-147`). The genuinely
        divergent case does not reach that state at all: the equivalence payload **does** carry `provider`, so a
        same-content re-capture on a different provider raises `MemoryOperationIdempotencyConflictError` and —
        not being `RUN_START_EVENT_KIND` — re-raises into `FAILED` (`memory_capture.py:796-802`). What remains
        for content-addressed kinds is **duplicate-dispatch ambiguity** (two dispatches produced byte-identical
        content, and the row names one of them), which is a different and much weaker thing than version
        staleness — the row always describes content byte-identical to the stored version — and it is a
        residual **(i-envelope) shares**, since a re-append rewrites the envelope too.

     **So the contract text is: the coherence check is MANDATORY on `EPISODIC_RUN` and comprises
     `envelope.created_at` ↔ `entry.timestamp` (dispatch rows only), `content["cli_profile"]` ↔
     `entry.cli_profile`, and `content["engine_class"]` ↔ `entry.engine_class` — the last compared on the
     enum's `.value`, which is what content stores (`_engine_class_value`, `:1122-1125`). On every other kind it
     is NOT owed, because the join key is itself the content binding.** The residual disposition below
     (α / β / γ) is likewise an `EPISODIC_RUN`-scoped question, which sharpens rather than softens it: (β) — the
     kind-scoped `UNVERIFIABLE`-by-rule — is now visibly the *whole* of the affected corpus, not a subset of it.
     A spec leg stating the check kind-blind would buy a corpus-wide false-`UNVERIFIABLE` rate for a failure
     mode those kinds cannot have.

     **And the honest bound: this check does not close the case that produced it.** The witness's two calls
     differ in `workflow_id` / `provider` / `model` / `policy_ref` and agree on `cli_profile`, `engine_class`
     and `timestamp` — and `provider` / `model` / `policy_ref` / `procedural_snapshot_ref` are **ledger-only**
     (absent from run-start/run-close content) while `workflow_id` / `thread_id` / `provider_route` /
     `started_at` / `close_status` are **content-only**, so a divergence confined to either set is invisible
     to any comparison the two surfaces support. The check catches the divergences that touch a shared value
     — a real second dispatch at a different wall-clock instant fails the `created_at` comparison — and that
     is worth mandating; it is **not** a closure. **The spec leg therefore owes an explicit disposition of the
     residual**, and it has exactly three forms, none of them free: (α) add the record's `content_hash` (or an
     envelope-version stamp) to the capture row — a **C-MEM-08 closed-schema field addition**, i.e. precisely
     the schema cost (ii) was preferred for avoiding, and it repairs no already-written row; (β) classify
     every `EPISODIC_RUN` record as `UNVERIFIABLE` by rule, which is (ii-b) applied to that kind and carries
     (ii-b)'s stated foreclosure; or (γ) state the residual as accepted — a matched row may describe a
     superseded version of a multi-writer record, and the determination is reported anyway. **(i-envelope) has
     no counterpart residual** (see the assessment below): its field ships *inside* the version it describes.
- **(ii-b) — fail closed on ambiguity.** The alternative: the contract defines no event-qualified key and
  instead states that a record whose join resolves to more than one capture row yields `UNVERIFIABLE` — no
  auto-promotion under reading B. It invents no join semantics, but it is **not** the conservative default it
  looks like: it makes **every** `EPISODIC_RUN` record permanently unverifiable the moment `capture_run_close`
  acquires a production caller, i.e. it silently becomes reading **C** for run records while presenting itself
  as reading B. That is a real cost, and a spec leg choosing (ii-b) must state it as a chosen foreclosure.
- **They are not exclusive, and the honest resolution uses both:** (ii-a) is the join, (ii-b) is its residue.
  **And the multi-match arm is mandatory in either case, not optional** — it is vacuous only for the exact
  key-shaped join of (ii-a). Any join keyed on `action_id` or on `memory_refs` carries **no** single-row
  guarantee at all (per the R4 correction above), so the contract must state the ambiguity arm rather than
  rely on a reader choosing the one lookup shape that makes it unreachable.
- The ledger's `provider` is a raw provider **key**, not a family value, so the join needs canonicalization —
  and the machinery already exists and is already the house authority (`provider_family_for_scope_check` /
  `canonical_scope_family`, landed at B-86/B-89). No new normalization posture is invented.
- **Cost: read-side only, but it is a new cross-contract dependency** — C-MEM-10 would depend on C-MEM-08
  availability and readability, which C-MEM-10 does not today. It also couples a promotion decision to a
  ledger scan on `durable/memory_ops.jsonl` (append-only, hash-chained, no index over `memory_refs` **or**
  `action_id`).
- **The unresolvable set must be specified, and each review round has made it larger — R3 took it from one
  case to three, R4 to five, R7 to six. R8 did not add a seventh; it SCOPED the sixth to `EPISODIC_RUN`, which
  is a narrowing of the set on every other kind.** All of:
  1. no reachable capture row at all (promotion-authored, compaction-authored, native-adapter-authored, or an
     unreadable ledger);
  2. `stored_capture_event_type` returning `None` — the helper is deliberately strict, *"an absent or non-text
     field reads as `None` - an unrecognizable record, never a guess at one"* — so the record cannot name its
     own writer;
  3. the composed key matching no row (a torn capture whose repair never ran — `_capture` writes the record
     before its ledger row, `memory_capture.py:721-732`);
  4. **[R4]** the matched row is **not** a `CAPTURE` row (`operation_kind != MemoryOperationKind.CAPTURE`) —
     the cross-producer `action_id` namespacing convention did not hold, and the ledger never guaranteed it
     would;
  5. **[R4]** the matched row **is** a capture row but carries `provider = None`. This is not hypothetical: it
     is the torn-capture **repair** row's shape *by construction* — `repair_capture_operation` passes
     `provider=None` / `model=None` (`memory_capture.py:938-939`), deliberately, because *"they describe the
     dispatch that tore, which the repairer is not … a repair row attests that this capture is durable, not
     which dispatch performed it"* (`:916-921`). A **repaired** capture therefore yields *unknown provenance*,
     and must not be read as *same-family* merely because a row was found.
  6. **[R7, scoped at R8]** the matched row **fails the record/ledger coherence check** of consequence 3 above
     — row and stored record disagree on a value only one call could have written. **The case applies to
     `EPISODIC_RUN` only** (per the R8 scoping at consequence 3: `envelope.created_at` ↔ `entry.timestamp` on
     dispatch rows, `content["cli_profile"]` ↔ `entry.cli_profile`, `content["engine_class"]` ↔
     `entry.engine_class`; `step_id` is **not** a comparator on this kind — it is `None` on both surfaces —
     and the other kinds derive their `memory_id`, hence the join key, from `content_hash`, so the key is
     itself the content binding and this failure mode cannot arise). The row is then about a *different
     version* of this record, and its `provider` is not this content's provenance. Even within `EPISODIC_RUN`
     the case is **detection-bounded, not exhaustive**: a disagreement confined to the ledger-only or the
     content-only field set passes it, which is the residual consequence 3 requires the spec leg to dispose of
     explicitly (α / β / γ there).

  Plus the ambiguity arm: **any** resolution returning more than one row is `UNVERIFIABLE` (vacuous under the
  (ii-a) key-shaped join, mandatory in the contract regardless — (ii-b) above).

  Each yields *unknown*, not *same-family*. The house idiom for exactly this is already established and should
  be reused verbatim rather than re-invented: the B-91 tri-state convergence (`MATCH` / `CONFIRMED_MISMATCH` /
  `UNVERIFIABLE`, where a determination is only reported when it was actually reached). Under reading B the
  honest mapping is `UNVERIFIABLE` → review_required, never auto-promote.

**Assessment, re-run after R3, R4, R6, R7 and R8 — and the honest outcome is that the two options have LEVELED.
This filing no longer recommends one; it presents both, with the requirement that would decide between them.
R8 does not un-level them: it makes (ii)'s coherence check narrower and better-specified (an `EPISODIC_RUN`-only
obligation, not a corpus-wide one) and (i)'s cheapest shape cheaper than the pre-R8 accounting said (the
boolean payload carries no family value domain and no second family field). Both columns moved in the same
direction, which is why the level holds.**

*The change of shape is deliberate and is stated as a correction, not a softening. R6 struck out (i)'s largest
stated cost (identity movement, which belongs to the content variant alone) and the preference was re-affirmed
on one remaining point: that (i-envelope) resolves the multi-writer kind "by silent last-writer-wins accident"
where (ii-a) resolves it deliberately. **R7 found that point FALSE**, and with it goes the last thing keeping
the preference in place. Having said at R6 that a struck-out cost would move the balance "and this filing would
say so," it says so.*

- **What the findings cost (ii) — now five owed things, up from R4's four.** The "join key already exists"
  claim was too clean, three times over. R3: the key is not `memory_refs`, and the one-row-per-record premise
  was false for the one record kind that has multiple writers. R4: the key is not `action_id` either — the
  ledger's uniqueness is on `idempotency_key`, and the capture path's deterministic `idempotent:{action_id}`
  derivation is what makes that key reconstructible from a stored record. **R7: a matched row is not a row
  about *this version of* the record** — for `EPISODIC_RUN` nothing on the row binds it to stored content
  (no content hash; `response_hash` hashes the ledger entry itself; `memory_refs` carries a `run_id`-derived,
  content-independent id), so a divergent second writer leaves a single, correctly-qualified, non-`None`-provider
  row that the join reads as determined provenance while the record it describes has been overwritten. The
  contract now owes: the join key stated exactly; the `operation_kind == CAPTURE` qualification; the
  **six**-case `UNVERIFIABLE` set plus its multi-match arm; the **mandatory record/ledger coherence check with
  its RECORD-KIND SCOPE and its detection bound stated** (R8: `EPISODIC_RUN` only, comparing `created_at` ↔
  `timestamp` on dispatch rows plus `cli_profile` and `engine_class`; the other kinds' join key is itself the
  content binding, and a kind-blind check would false-`UNVERIFIABLE` the entire non-run corpus against content
  fields those writers never store); and an explicit disposition of the residual that check cannot reach
  (α / β / γ at consequence 3, itself an `EPISODIC_RUN`-scoped question) — plus the cross-contract-dependency
  sentence.
- **What they did not cost — with one conditional.** No new field, schema member, enum value, hash input, or
  identity movement, *provided the spec leg disposes of the R7 residual by (β) or (γ)*. Disposition **(α)**
  — binding the row to the record's `content_hash` — is a **C-MEM-08 closed-schema field addition**, and it
  would hand (ii) a schema cost of exactly the kind (i) was charged for. That conditional is new at R7 and
  must not be elided: "read-side only" is true of (ii-a) *as specified*, not of every honest closure of it.
- **What (i) costs — per variant, after the R6 [P2-1] placement split, the R8 [P2-2] payload split and the R9
  [P2-1] write-cost correction.** Every variant pays the closed-schema extension at C-MEM-03, reversing v1.1's
  own zero-new-field posture one delta later; every one is derived at **one** site (`_record`, which already
  receives both inputs — **[R9]**, correcting "every capture writer touched"); every one is **forward-only**
  absent a back-fill (a record written before the amendment carries no field, so the pre-amendment corpus is
  `UNVERIFIABLE` under (i) by construction, and back-filling it *is* option (ii) offline). On top
  of that: **(i-content)** alone pays content-hash identity movement — **(i-envelope)** pays none of it, the
  envelope being an input to neither `content_hash` nor `memory_id` (§5(i)); and **(i-*-family)** alone pays
  the second family-valued field beside `MemoryScope.provider_family` (a one-source-of-truth hazard) plus the
  C-MEM-03 value-domain reconciliation — **(i-envelope-bool)** pays neither, its tri-state being a *derived
  predicate* over that field rather than a rival authority on it. The pre-R8 accounting charged the family
  costs to all of (i), which priced the boolean wrong.
- **[R7] The multi-writer penalty charged to (i-envelope) at R3/R6 is FALSE, and on that axis (i-envelope) is
  in fact STRICTLY BETTER than (ii-a).** *(out-of-family `just codex-review` R7 [P2]; upheld and verified by
  direct read at `d8df7647`.)* The R6 text is mechanically correct that `capture_run_close`
  (`memory_capture.py:337-380`) goes through `_record` (`:1015-1046`), builds a **complete, fresh**
  `MemoryRecordEnvelope`, and that `MemoryStore.write_record` writes the **whole** canonicalized record —
  envelope **and** content together — to the single `run.json`
  (`harness-is/src/harness_is/memory_store.py:178-188`; `EPISODIC_RUN` takes the `_write_file_atomically`
  branch at `:186` against `_run_record_path`, `:273-274` / `:290-295`). **What it drew from that is the
  error.** Envelope and content being written *together, from one call*, is precisely why the field does **not**
  go stale: the stored `content["event_type"]` says `run_close`, and an envelope provenance field would carry
  **that same call's** `provider` — the argument `_capture` threads into `_record` at `:649-658`, alongside the
  content it is describing. The overwrite therefore **preserves** provenance for the version that is stored,
  which is the identical semantics (ii-a) obtains *indirectly*, by selecting the row that `event_type` names.
  "Records nothing about which writer set it" is not a defect when the field describes the version it ships
  inside; the reader is promoting **that** version, not the run's history. And the two diverge in exactly one
  place — the R7 finding-1 case: with the record overwritten and the row not, **(i-envelope) reads call two's
  provider (correct for the stored content) while (ii-a) reads call one's (stale)**. The multi-writer kind
  that R6 said "is what the choice turns on" turns it the other way.

**The comparison, leveled — stated as a ledger rather than a verdict.**

*Three columns, not two, after R8: option (i)'s payload axis is a real fork of its own, and collapsing it hid
the cheaper shape.*

| | **(i-envelope-bool)** *(tri-state predicate)* | **(i-envelope-family)** *(family value)* | **(ii)/(ii-a)** |
|---|---|---|---|
| Provenance semantics | Same-call: ships inside the version it describes; **cannot** go stale relative to it | Same-call, identically | Event-selected: same answer whenever the row and the stored version agree; **stale** when they do not (R7, `EPISODIC_RUN` only per R8) |
| What it can answer | *Whether* the leg was cross-family — present/absent only | *Whether*, **and which family** produced the content | *Whether* + *which* (the row's raw `provider`, canonicalized) |
| Identity movement | None (envelope is hash-inert) | None | None |
| Schema cost | A closed-schema field addition at C-MEM-03, reversing v1.1's zero-new-field posture — **but no new family value domain and no second family-valued field** | The same field addition **plus** a second family-valued field beside `MemoryScope.provider_family` and its C-MEM-03 value-domain reconciliation | None **as specified** — but disposition (α) of the R7 residual reintroduces one at C-MEM-08 |
| Write side **[R9]** | **One** derivation site — `_record` (`memory_capture.py:1015-1046`) already receives both the call's `provider` and the resolved scope; the predicate is derived there from the existing B-86/B-89 family authorities. No public writer signature changes | **One** site, identically | Untouched |
| Read side | Read one field | Read one field | Compose the key, scan an unindexed append-only `durable/memory_ops.jsonl`, qualify the row, run the `EPISODIC_RUN`-scoped coherence check, handle six `UNVERIFIABLE` cases + the multi-match arm |
| Cross-contract dependency | None; works for a record read in isolation | None | New: C-MEM-10 on C-MEM-08 availability + readability |
| Existing records | **No help** — forward-only; the pre-amendment corpus is `UNVERIFIABLE` by construction | **No help** — same | Works on any already-written record that has a row |
| Aggregate-run provenance ("did *any* leg of this run run cross-family") | **Cannot answer** — the envelope carries its own writer's value only | **Cannot answer** — same | **Can** answer — every capture row for the run is retained, each with its own `provider` (a `run_id`-scoped scan, not the keyed join) |
| Future family-discriminating policy | **Cannot support** — needs a second amendment at the family column's price | Supported | Supported |
| Contract text owed | The field, its **derivation rule**, its tri-state `null`/UNVERIFIABLE semantics, its hash-inertness, its forward-only consequence, and its multi-writer disposition | All of that **plus** the value domain and the reconciliation against `MemoryScope.provider_family` | The five items above |

**The requirement that would decide it, which this filing has NOT established and does not invent.** The
columns answer *different questions*, and the fork has never stated which one C-MEM-10 needs:

- If the requirement is **stored-version provenance, present/absent** — "was the content I am about to promote
  produced on a cross-family leg" — all three columns answer it, they are semantically equivalent on the
  coherent path, **(i-envelope) is strictly more reliable on the incoherent one**, and **(i-envelope-bool) is
  the cheapest of the three**: it is the only one that adds no family surface to the contract at all. On
  reading B *as this filing argues it* — a risk flag plus a gate — that is the requirement, and the boolean is
  the proportionate answer. [MODERATE]
- If the requirement is **stored-version provenance, by family** — a policy that treats some cross-family legs
  differently from others — the boolean is inadequate and **(i-envelope-family)** is the floor.
- If the requirement is **aggregate-run provenance** — "was any leg of the run that produced this record
  cross-family" — **(ii) is required**, because no envelope payload can represent it. Note this is a
  *stronger* reading of reading B than the fork has argued for anywhere, and adopting it is itself a decision.

**Confidence on Q2: [MODERATE], and it is now a confidence in the *framing*, not in a pick.** The
recommendation is withdrawn rather than re-stated, because the one asymmetry it rested on did not survive
verification. Three rounds had corrected this comparison — R3 (wrong field family), R4 (wrong uniqueness
guarantee), R6 (variant-blind cost) — R7 corrected it twice more, once on each side, and **R8 corrects it a
sixth time, again on both sides at once** ((ii)'s coherence check over-scoped; (i)'s boolean payload
over-priced). That recurrence is the signal, and the honest conclusion from it is that **Q2 is a decision for
the spec leg to make against its own re-grounding and against a stated requirement, not a preference this
filing should carry forward.** What the filing does carry forward is the mechanics all options must respect:
state the key exactly and what enforces its uniqueness; state the coherence check, **its record-kind scope**
and its detection bound; state the residual's disposition; and, under (i), state hash-inertness, the
forward-only consequence, and — for the boolean — the tri-state's derivation rule and its unknown value.
**What R8 does NOT do is re-introduce a recommendation:** naming the boolean the cheapest *adequate* answer
*for reading B's own present/absent requirement* is a statement about (i)'s internal shape, not a verdict
between (i) and (ii) — the three axes on which (ii) still wins (already-written records, zero write-side
reach, aggregate-run provenance) are untouched by it.

**[R9] The write-cost correction moves weight, and the honest accounting of how much is: within (i)'s own
column only, and the level holds.** *(out-of-family `just codex-review` R9 [P2-1].)* (i)'s "Write side" cell
went from *every capture writer touched* to *one derivation in `_record`* — a real reduction, and the third
time a cost charged to (i) has been struck (R6: identity movement; R8: the family value domain; R9: the
write-side reach). But it changes **nothing** on the three axes that carry (ii)'s side of the level: **existing
records** (still `UNVERIFIABLE` under (i) by construction — a back-fill is (ii) run offline, not a cheaper
(i)), **aggregate-run provenance** (still structurally unrepresentable in an envelope), and **comparison-basis
flexibility** (the stored answer is still baked at write time and cannot be re-derived under a different basis;
(ii)'s row-side `provider` can). Nor does it touch (ii)'s own write-side cell, which was already **zero** and
cannot go lower — so the axis on which the correction operates is one (ii) already won, and winning it by a
smaller margin does not move the balance. **What it does correct is a mis-framing of the cost's *kind*:** (i)'s
write-side price is a **contract** obligation (a closed-schema field at C-MEM-03, its derivation rule, its
tri-state unknown, forward-only) — never a refactor across seven public signatures, which is what the struck
sentence implied. Per §10's rule this is a Q2-mechanics finding and would ordinarily be registered against the
spec leg; it was applied here only because it was a **false statement about the code in the filing's own
text**, on the same standard R3-R8 were held to. No recommendation is restored.

## §6 Recommended drafting targets, per reading

| Reading | Owed spec text |
|---|---|
| **A** | **C-MEM-10 Contract** — one paragraph: promotion eligibility is determined by record scope, policy, and evidence, and is not conditioned on the provider family that produced the content during a fallback leg; the run's composed partition (C-MEM-03 §"`MemoryScope.provider_family` value domain and derivation", the continuity sentence) is the whole of the provenance question at this contract. **C-MEM-10 Invariants** — one bullet mirroring it. Nothing else; no C-MEM-08, no C-MEM-03, no plan unit beyond a coverage-matrix row. |
| **B** | **C-MEM-10 Contract** — the cross-family-captured condition; the risk-flag obligation; and, explicitly, the **gate**: such a candidate is review-required and not auto-promotable (§2's inert-flag finding makes the gate sentence mandatory, not decorative). **C-MEM-10 `PromotionCandidate.risk_flags`** — no schema change needed: the `PromotionCandidate` block's `risk_flags: list<string>` is already an open list, so the new value is a vocabulary addition at the contract, and only the impl-side `PromotionRiskFlag` enum (`memory_promotion.py:80-86`) is closed. **C-MEM-10 Invariants** — the gate as an invariant. **C-MEM-08** — if discriminator (ii), and per the R3 [P2-1] + R4 [P2] + R7 [P1] findings this is now **five** sentences, not one: (a) the capture row is the authoritative provenance source for promotion, (b) the join is keyed on the capture **`idempotency_key`, composed from the capture `action_id`, which is composed from the record's own declared `event_type`** — explicitly **not** on `memory_refs` (which cannot discriminate a shared-`memory_id` kind) and explicitly **not** on the bare `action_id` (which the ledger does not constrain for uniqueness at all — `append_memory_operation` dedups on `idempotency_key` alone), (c) the matched row must be **qualified** on `operation_kind == CAPTURE` rather than assumed to be a capture row, (d) the **six**-case `UNVERIFIABLE` disposition (no reachable row / record cannot name its writer / composed key matches no row / matched row is not a CAPTURE row / matched row carries `provider = None`, the repair-row shape / matched row fails the record-ledger coherence check), plus the multi-match ambiguity arm, and (e) the **mandatory record/ledger coherence check**, **scoped per R8 to `EPISODIC_RUN`** — the comparable same-call values on that kind (`envelope.created_at` ↔ `entry.timestamp` on dispatch rows, `content["cli_profile"]` ↔ `entry.cli_profile`, `content["engine_class"]` ↔ `entry.engine_class` compared on `.value`; **not** `step_id`, which is `None` on both surfaces there), an explicit statement that the check is **not owed on the content-derived-id kinds** (their join key *is* the content binding, and a kind-blind check would false-`UNVERIFIABLE` the whole non-run corpus against content fields those writers never store), its **detection bound** (ledger-only and content-only fields are outside it), and an explicit disposition of the residual it cannot reach (α a C-MEM-08 content-hash binding field / β `EPISODIC_RUN` `UNVERIFIABLE` by rule / γ accepted residual). **or C-MEM-03** — if discriminator (i), and the owed text differs along **both** axes: by **placement** per the R6 [P2-1] split and by **payload** per the R8 [P2-2] split. Under **(i-envelope-bool)** — the cheapest shape — the new tri-state envelope field, its **derivation rule** (the call's `provider` canonicalized through the existing `provider_family_for_scope_check` / `canonical_scope_family` authorities, compared against the record's own composed `scope.provider_family`), its **third value** and when the writer must record it rather than `false` (`provider is None`, an unregistered key, or a `null` — unpartitioned — scope family), the read-side mapping of that third value (`UNVERIFIABLE` → review-required, never auto-promote, the B-91 idiom), an explicit statement that the field is **hash-inert** (it enters neither `content_hash` nor `memory_id`), the **forward-only** consequence (pre-amendment records carry no field and are `UNVERIFIABLE`), its multi-writer disposition for `EPISODIC_RUN` — which per R7 is that the field describes **the stored version**, co-written with the content it qualifies, not the run's writer history — and, stated as a bound rather than left implicit, that the field answers **present/absent only** and cannot support a family-discriminating policy. Under **(i-envelope-family)** all of that **plus** the field's **value domain** and its reconciliation against `MemoryScope.provider_family` as a second family-valued field with its own `null` semantics. Under **(i-content)** whichever payload is chosen **plus** the content-hash identity-movement consequence and its own forward-only statement. Plus a memory-plan unit (U-MEM-27) decomposing the impl leg. |
| **C** | Everything reading B owes, minus the flag/gate wording, plus a **refusal** invariant at C-MEM-10 and a statement of the permanent consequence (fallback-leg learning is unpromotable). Additionally owes a reconciliation sentence against the C-MEM-03 continuity statement (§"`MemoryScope.provider_family` value domain and derivation") and against the C-MEM-13 capture carve-out (§"Cross-family withholding of standard memory tools"), both of which read against it. |

Under all three readings the Memory threat model needs **no** amendment: its §Threats opener, its
cross-run-prompt-injection-persistence bullet, and its model-authored-notes invariant are the authority the
resolution conforms to, not a surface it revises — the same X-AL-3 posture v1.1 took at its change-note
paragraph **"Why this is conformance repair, not design extension (X-AL-3)"**.

## §7 Recommendation — **Reading B** [MODERATE]

The B-86 council record decides this, and it decides it in two directions at once.

**It forecloses C.** C3's continuity argument and C6's continuity-abstraction refinement (§4, reading C) were
not incidental remarks — they are the reasoning that carried Q1, and both apply *a fortiori* to a promotion
refusal, which imposes the same "the fallback leg's memory is second-class" harm that Q1 rejected. Choosing C
would overturn a ratified council resolution one arc later without new evidence.

**It does not license A's silence.** The withhold half of that same record (Q2) rests on C10's classification
of `memory.write_note` as `write-bounded-irreversible` — *"durable, primary-attributed, supersession
non-deleting, promotion-eligible → the `:472` cross-run prompt-injection-persistence threat runs directly
through it"* (B-86 fork §4; its `:472` is quoted verbatim as a **historical** record of that filing's state,
and is one of the drifted cites the v1.1 change-note paragraph **"Surfaced finding, not patched."** already
corrected — the live reference is the Memory threat model §Threats bullet *"Cross-run prompt-injection
persistence through promoted semantic/procedural memory."*). C10 named **promotion-eligibility itself**
as part of what makes that write
dangerous. C10 declined to re-key the scope because the *mechanism* was wrong, not because the concern was
absent — the council's own words: *"the defect is in the absent gate at the dispatch boundary, not in the
scope's key."* Reading B is that same resolution shape applied one contract downstream: keep the partition
(C3/C6 satisfied), put the gate where it belongs (C10 satisfied).

**The R4 correction strengthens this half of the argument, and it should be said plainly rather than left
implicit.** C10's "promotion-eligible" clause was, at the B-86 convening, a characterization. §4's corrected
Reading-A bullet now grounds it mechanically: capture is durable but **not injectable** (every capture-written
kind is outside the sole production policy's `eligible_record_kinds`; a `PROPOSED` record is retrieval-excluded
by construction), and promotion to an `ACTIVE` semantic/procedural record is exactly and only the step that
makes content injectable into a future run. So the threat model's *"Cross-run prompt-injection persistence
through promoted semantic/procedural memory."* is not adjacent to this question — **promotion is the whole of
that channel**, and C-MEM-10 is the contract that governs it. Correspondingly, Reading A lost its second
rationale bullet: the "grants no new reach" argument was the only one that claimed the question was *benign*
rather than merely *acceptable*. A's remaining case is the composed-scope-identity argument alone, which
argues the reach transition is **acceptable** — a genuinely weaker position than the one the first three
rounds recorded, and one the operator should weigh as such.

**And the decisive asymmetry against A is that A would ratify a decision nobody made.** Today the pipeline is
not permissive-by-policy; on the production composed-scope path it is permissive-by-blindness (§3 — it cannot
represent the fact, and the residual path where it can does not pose the question). Writing "eligible,
unchanged" into C-MEM-10 would convert a structural gap into a contract commitment while the policy layer has
still never had the input. That is the *precise* defect the v1.1 change-note identified as B-86's own trigger,
at **"Why this is conformance repair, not design extension (X-AL-3)"**: *"v1 already mandated that the
provider-family boundary be enforced; it never stated what that
boundary is keyed to, which left the mandate unfalsifiable at the contract level."* Reading A repeats that
error one contract over.

**Confidence on Q1 stays [MODERATE], not [HIGH] — and the R4 correction is the first round that pushed
*upward* on it without moving it.** Honestly stated: the R4 finding strengthens B's *contract* argument (the
paragraph above) and weakens A's, which on the merits alone would argue for [HIGH]. It does not get there,
because the reason the tag is [MODERATE] was never doubt about the contract argument — it is the cost/exposure
asymmetry the R1 corrections established, which R4 leaves entirely intact: B still costs a discriminator A
does not, and the live exposure it buys down is still **nil at HEAD**. What R4 *does* change is the balance
*within* that asymmetry, and it changes it in one direction only: A-as-permanent is now a weaker position, and
the reach transition that A would ratify is now a stated mechanism rather than an implicit one. A-as-**interim**
is untouched (see below), because it rests on the exposure fact, not on the rationale that was corrected.

**The R1 corrections at §2 lowered this tag rather than raising it, and that remains why it is not [HIGH].**
Reading B costs a discriminator (§5) that reading A does not, and the live exposure it buys down is — on the
corrected reading — **nil at HEAD**, not merely bounded: the tool path is denied twice over (the capture
kinds are outside the sole production policy's `eligible_record_kinds`, and that policy pins
`PROPOSE_SEMANTIC`, so no candidate on that path is auto-promotable at all), and the hint path is unfed with
its candidate-family convention still undefined. B's case therefore rests entirely on the *contract*
argument above — which is unweakened by R1 and *strengthened* by R4, because the argument was never that
content is leaking today; it is that C-MEM-10 would be committing to a permissiveness the policy layer has
never evaluated, over a transition R4 established is the reach-conferring one.

**What that changes: A-as-interim is now a materially more defensible operator choice, and this filing says
so rather than steering.** With zero live exposure, taking A costs nothing *observable* in the interim, while
B's discriminator (§5) is real work against a path nothing currently exercises — the ordering "state the
position now, build the mechanism when a producer or a policy makes it live" is coherent, not a dodge. Two
conditions keep it honest, and both should be recorded with the decision: (a) it is an **interim with B named
as the target**, not a discharge; and (b) the triggers that end the interim are named.

**The triggers, stated as the combinations they actually are** *(the R6 [P2-2] sharpening; §2's table is the
grounding, and it replaces the earlier "a single policy field converts this into a live exposure" framing,
which was true of candidate-**reachability** and not of active **promotion**)*. They remain **review-triggers**
— any one of them re-opens the question and ends the interim — but each is now recorded with the transition it
actually enables, so no later reader infers that one of them alone turns on live auto-promotion:

| Trigger | Transition it enables **alone** | Why it nonetheless ends the interim |
|---|---|---|
| **T1** — a policy admits a capture-written kind into `eligible_record_kinds` | **Candidate-reachability.** Captured records reach the tool path and accumulate as durable `PROPOSED` records carrying unrecorded provenance; still not injectable | The `PROPOSED` corpus it builds is exactly what a later operator-review flip — which has no family term either — activates. The interim's "nothing accumulates" premise dies here |
| **T2** — the promotion decision moves to `PROMOTE_SEMANTIC` / `PROMOTE_PROCEDURAL` | **Active auto-promotion of already-eligible kinds** — the second-order case (a record already promoted out of a cross-family leg), live *immediately*, because `ReviewMode.AUTOMATIC` is already the production setting (`automatic_memory.py:555`) | It is the *last* missing conjunct for the second-order case — the only trigger that is one change away from real promotions today |
| **T1 ∧ T2** | **Live auto-promotion of a cross-family-captured record.** The full first-order exposure | The interim's premise — nil live exposure — is false from that moment |
| **T3** — a first caller populates `promotion_candidates` | **Candidate-reachability on the hint path only**, and it forces the candidate-family convention §2 records as undefined. Promotes nothing by itself: under `PROPOSE_SEMANTIC` `_auto_promote_allowed` is False, and no actuator reads it | The convention must be pinned *before* a producer ships one, not after; and an actuator for `auto_promote_allowed` (none exists under `src/` today) is the natural companion change that would arrive with it |

Absent this, the interim silently becomes permanent exactly when it stops being safe — and the single-change
framing would have let T1 or T2 pass as "not the live one yet." B remains the recommendation on the merits;
A-as-recorded-interim is now a close second rather than a concession. What must not happen is still the third
outcome: leaving it silent a second time.

**If B is selected, Q2 is a second decision, not a follow-on — and this filing no longer picks it.** Through
R6 the recommendation was **(ii)** with the **(ii-a) event-qualified join**, held in place by one asymmetry:
that (i-envelope) resolved the multi-writer kind by silent last-writer-wins accident where (ii-a) resolved it
deliberately. **R7 [P2] found that asymmetry false** — envelope and content are written *together, from one
call*, so an envelope provenance field describes exactly the version it ships inside, which is the same
semantics (ii-a) reaches indirectly through `event_type` — and **R7 [P1] found the reverse asymmetry real**:
nothing on a capture row binds it to a stored-content *version*, so a divergent second writer leaves (ii-a)
reading stale provenance from a correctly-qualified single row, a case (i-envelope) cannot have. With the one
load-bearing point struck out and a counter-point established, the comparison **levels** (§5's re-run
assessment states the full ledger). The remaining difference is not cost but *question*: (i-envelope) answers
stored-version provenance more reliably and cannot answer aggregate-run provenance at all; (ii) answers both,
covers already-written records, and pays a read-side join plus a residual disposition. Which one C-MEM-10 needs
is a **requirement** this filing has not established and declines to invent. **R8 refines each side without
disturbing that level:** (ii)'s coherence check is `EPISODIC_RUN`-scoped rather than corpus-wide, and (i)'s
payload axis splits into a *family value* and a **tri-state boolean** — the latter carrying no family value
domain and no second family field, hence the cheapest shape of (i), and adequate for reading B's own
present/absent flag requirement while foreclosing any later family-discriminating policy. Q2 confidence stays
**[MODERATE]** and is now confidence in the framing rather than in a pick.

## §8 Ratification ask — operator decision

The A / B / C choice is the operator's. It is a **durable contract commitment**: once C-MEM-10 states a
position, records written under it accumulate against that position, and reversing later leaves a
mixed-provenance corpus that must be re-adjudicated record by record — promotion supersession does not delete
(C-MEM-03 §Invariants: *"Supersession does not delete the prior record."*), so the prior record survives every
correction.

**[R9] "Irreversible" was too strong, and the ask is stated exactly rather than rhetorically.** *(out-of-family
`just codex-review` R9 [P2-2]; upheld and verified by direct read at `26720e8e`.)* The pre-R9 text said
reversal leaves the corpus *"with no way to re-adjudicate the already-promoted records"*. **There is a way, and
this filing already describes its machinery.** A promoted **semantic / preference** record persists its
lineage: `_semantic_record_content` writes `"source_memory_refs": [str(memory_id) for memory_id in
candidate.source_memory_refs]` into the record's own content (`memory_promotion.py:919-943`, the field at
`:932`), and the capture rows those ids resolve to retain their `provider` — which is precisely what option
(ii) reads, and option (ii) *"works on any already-written record that has a row"* (§5's table). So a later
migration can traverse surviving lineage → capture row → provider, re-run the family comparison, and supersede
or deny promotions made under the reversed position. **Reversal is therefore COSTLY AND INCOMPLETE, not
impossible — and the incompleteness is bounded by this filing's own analysis, not asserted:**

- **Missing rows** — §5's unresolvable cases (1) and (3): no reachable capture row at all
  (promotion-authored, compaction-authored, native-adapter-authored, or an unreadable ledger), or a torn
  capture whose repair never ran, so the composed key matches nothing.
- **Repaired rows** — case (5): the repair row carries `provider = None` *by construction*
  (`repair_capture_operation`, `memory_capture.py:938-939`), because *"a repair row attests that this capture is
  durable, not which dispatch performed it"* (`:916-921`). A repaired capture is unknown provenance forever.
- **Stale rows** — case (6), `EPISODIC_RUN`-scoped per R8: a matched, correctly-qualified, non-`None`-provider
  row may describe a *superseded version* of a multi-writer record, and the coherence check that detects it is
  itself detection-bounded (a divergence confined to the ledger-only or content-only field set passes it).

Plus a **fourth bound on the traversal itself**, which is a corollary rather than one of the six: lineage
survives on the **semantic / preference** path only. `_procedural_record_content` (`memory_promotion.py:959-989`)
writes `evidence` (`SourceRef`s) but **no** `source_memory_refs`, so a promoted **procedural** record carries no
memory-id lineage to traverse and sits outside the migration by construction.

**This remains a genuine operator gate — the qualification sharpens it rather than dissolving it.** The gate is
real because the cheapest moment to decide is *before* durable records accumulate: every promotion written
under a position that is later reversed becomes a row in a migration that is unindexed, partially blind on the
four bounds above, and non-deleting (a re-adjudication supersedes; it does not erase the record, and it cannot
recall content already injected into a completed run). What the operator is being asked to authorize is a
position whose practical unwind is a **costly, partially-complete migration**, not one with no unwind at all.

Decisions owed:

1. **Q1 — A, B, or C** (or "A as a recorded interim, B as the target" — which, per §7, the corrected
   zero-live-exposure picture makes a materially defensible choice, provided the interim-ending triggers are
   recorded with it **as §7's table states them**: **T1** an `eligible_record_kinds` admission
   (candidate-reachability), **T2** a `PROMOTE_*` decision (second-order auto-promotion, live immediately
   since `ReviewMode.AUTOMATIC` is already the production setting), **T1 ∧ T2** the full first-order exposure,
   and **T3** the first caller to populate `promotion_candidates`. Recording them as *three review-triggers
   with distinct transitions* — rather than as "the policy change" and "the producer" — is what keeps T1 or T2
   from passing later as "not the live one yet.")
2. **Q2, only if B or C — a LEVELED two-option decision, presented without a recommendation; and under (i) a
   PAYLOAD sub-choice that is a second, smaller decision of its own.** *(Changed at R7. Through R6 this item
   carried a **(ii)/(ii-a)** recommendation; R7 struck out the single asymmetry that held it and established
   one running the other way, so the honest presentation is the ledger, not a pick. R8 added the payload
   sub-choice — family value vs tri-state boolean — which had been offered in §5's opening sentence and costed
   nowhere. The A/B/C reading recommendation at item 1 is **untouched** by either — it never rested on Q2.)*
   Either
   option is defensible, and the choice may reasonably be deferred to the spec leg, which re-grounds all
   mechanics against its own HEAD in any case (§10's cap):

   - **(i-envelope)** — a new hash-inert provenance field on `MemoryRecordEnvelope`. Same-call semantics: the
     field ships inside the version it describes and cannot go stale relative to it, including in the
     divergent-second-writer case that defeats the join. No identity movement, no cross-contract dependency,
     a one-field read side. **Costs:** a closed-schema amendment at C-MEM-03 reversing v1.1's own
     zero-new-field posture one delta later; and it is **forward-only** — no help for already-written records
     absent a back-fill, which is option (ii) run offline. *(**[R9]** the third cost previously listed here —
     "every capture writer touched" — was **false**: all seven `capture_*` methods already thread `provider`
     into `_record`, which also holds the resolved scope, so the derivation is one central hoist and no public
     signature changes. (i)'s write-side price is a **contract** obligation, not a refactor.)*
     **[R8] Two payload shapes, and they are NOT the same commitment.**
     **(i-envelope-bool)** stores a *tri-state* `captured_cross_family` (true / false / unknown, the B-91
     idiom) derived at capture from the existing family authorities: it adds **no** family value domain and
     **no** second family-valued field, making it the cheapest shape of (i) and — on reading B as argued here,
     a present/absent risk flag plus a gate — a proportionate one; the price is that it can never say *which*
     family produced the content, so a later family-discriminating policy would need a second amendment.
     **(i-envelope-family)** stores the family value: it supports that policy, and pays the value-domain
     reconciliation plus a second family-valued field beside `MemoryScope.provider_family` (a
     one-source-of-truth hazard). *(Placement variant **(i-content)** is strictly dominated under either
     payload — same benefits, plus content-hash identity movement.)*
   - **(ii)/(ii-a)** — the event-qualified C-MEM-08 ledger join. The row is selected by the capture
     **`idempotency_key`** (`idempotent:capture:{event_kind}:{memory_id}`, composed from the record's own
     declared `event_type`), **not** by `memory_refs` (which cannot discriminate the run-start / run-close rows
     sharing one `EPISODIC_RUN` `memory_id`) and **not** by the bare `action_id` (which the ledger does not
     dedup on); the matched row is qualified on `operation_kind == CAPTURE`; the **six**-case `UNVERIFIABLE`
     residue plus the multi-match arm fail closed (review_required, never auto-promote). Works on
     already-written records, and is the **only** option that can answer aggregate-run provenance. **Costs:**
     a new cross-contract read dependency plus an unindexed scan; five owed contract sentences; a mandatory
     record/ledger coherence check whose **record-kind scope and detection bound must both be stated** ([R8]:
     owed on `EPISODIC_RUN` only — `created_at` ↔ `timestamp` on dispatch rows plus `cli_profile` and
     `engine_class`; the content-derived-id kinds bind row to content through the join key itself, and a
     kind-blind check would false-`UNVERIFIABLE` the whole non-run corpus); and an explicit disposition of the
     residual that check cannot reach — of which (α), binding the row to the record's `content_hash`, is
     itself a C-MEM-08 closed-schema addition, i.e. (ii) is "read-side only" *as specified*, not under every
     honest closure.
   - **Sub-choice (ii-b)** — fail closed on *any* multi-row ambiguity, defining no event-qualified key — is
     available and needs no new join semantics, but §5 records that it is a de-facto reading **C** for
     `EPISODIC_RUN` records and must be taken as a stated foreclosure, not as a conservative default.

   **What would decide it, if the operator or the spec leg wants a discriminator rather than a coin-flip:**
   state the requirement. **Stored-version provenance, present/absent** ("was the content I am promoting
   produced on a cross-family leg") is answered by all three columns, favours (i-envelope) on reliability, and
   is answered most cheaply by **(i-envelope-bool)** — which is reading B's own requirement as this filing
   argues it; **stored-version provenance by family** (a policy that treats some cross-family legs differently)
   rules the boolean out and makes **(i-envelope-family)** the floor; **aggregate-run provenance** ("did any leg
   of this run run cross-family") *requires* **(ii)**. §5's three-column table is the full ledger.

Per root `CLAUDE.md` §12.4.1, this filing drove the question to its genuine gate: the grounding, the witness,
the prerequisite mechanics, the drafting targets, and — on Q1 — a recommendation are all done. What remains is
the choice itself, which is a real architectural commitment and not a default. On Q2 what remains is a
genuinely leveled pair, and saying so is the honest discharge rather than restating a preference that did not
survive R7.

## §9 Routing

Per root `CLAUDE.md` §4.3: Class 1 → design-phase back-flow. Routing target is the **Phase 5 spec
revision-pass** (`Spec_Memory_Substrate_v1.md` C-MEM-10, plus C-MEM-08 or C-MEM-03 per Q2), with a
`Implementation_Plan_Memory_Substrate_v1.md` delta (a new U-MEM-27) owed under readings B and C, and clearance
markers at `.harness/clearance/` in the same PR per §4.5. The impl leg follows the spec leg per the
B-33 / B-59 / B-70 / B-72 / B-86 precedent. An out-of-family `just codex-review` decorator on the eventual
C-MEM diff is recommended — the amendment is threat-model-adjacent (the Memory threat model's §Threats opener
and cross-run-persistence bullet, and its model-authored-notes invariant) inside an already-cleared contract,
which is exactly the shape that earned it on the B-86 spec leg. It has already earned it here: R1 corrected
two exposure over-claims, R2 corrected the review branch's durability and the §3 data-flow scope, R3
corrected the §5 join premise, R4 corrected the Reading-A reach rationale and the §5 join key, R5 synced the
register carriers to the R4 join semantics, R6 split §5's option (i) into its content and envelope
variants — striking identity movement from the contending one — and replaced the single-change exposure
framing with §2's combination table, and R7 corrected the Q2 discriminator comparison on both sides at once:
[P1] the (ii-a) join can accept **stale** provenance from a correctly-qualified single row (nothing on a
capture row binds it to a stored-content version), which adds a mandatory coherence check, a sixth
`UNVERIFIABLE` case and an owed residual disposition; and [P2] the multi-writer penalty charged to
(i-envelope) is **false** (envelope and content are co-written, so the field describes the version it ships
inside), which removed the last asymmetry holding the (ii) preference and **levelled** Q2 into a two-option
decision. R8 refined both sides of that leveled pair without disturbing it: [P2-1] the R7 coherence check was
written from the run kinds and is owed on `EPISODIC_RUN` **alone** (the other kinds derive `memory_id`, hence
the join key, from `content_hash`, so the key is itself the content binding; and they carry no `cli_profile` /
`engine_class` in content, so a kind-blind check would false-`UNVERIFIABLE` the entire non-run corpus), and
[P2-2] option (i)'s **payload** axis — a family value vs the tri-state `captured_cross_family` boolean the
section's own opening sentence offered — had never been costed, so the boolean was priced with costs it does
not carry. **R9 (this pass) is the SOUNDNESS EXIT**, and both of its findings landed on statements the filing
made about the code rather than on its substance: [P2-1] (i)'s write-side cost was overstated — all seven
`capture_*` methods already thread `provider` into `_record`, which also holds the resolved scope, so the
provenance field is derived at **one** central site with no public signature change, and an unknown-defaulted
optional field leaves the other three envelope constructors and every pre-amendment envelope intact; the
leveling is unmoved, because the three axes carrying (ii)'s side (existing records, aggregate-run provenance,
comparison-basis flexibility) are untouched and (ii)'s own write side was already zero; and [P2-2] the
ratification ask's *"irreversible … no way to re-adjudicate"* was too strong — `source_memory_refs` persists on
the semantic path and capture rows retain `provider`, so a later migration **can** re-adjudicate many existing
promotions; the ask now states the unwind exactly, as costly and partially complete (bounded by missing,
repaired and stale rows, plus the procedural path carrying no lineage at all), and the gate stands on *when* the
decision is cheapest rather than on impossibility.

**No Phase 7 execution is halted by this filing.** U-MEM-26 has landed; the question was already scoped out
of it at `Implementation_Plan_Memory_Substrate_v1.md` U-MEM-26, subsection "Out of scope for this unit:".
What is halted is any *implementation* of a promotion-side family term, which must wait for the ratification
above.

## §10 Review-time inventory — the soundness cap on this filing

*Filed at R4 and maintained each round since, per the PD-9 review-time-inventory discipline
(`Project_Workflow_v1_19.md` §7.5.2 PD-9, adversarial-review-loop non-convergence discriminators), and on the
`deferred-mechanism spec leg exits on soundness, not review-quiet` precedent. This section bounds the review
surface so a further round has a principled exit rather than an open-ended one.*

**What nine rounds converged on, and what they did not touch — restated at R7, because R7 breaks the
previous version of this claim and the honest move is to say so rather than re-assert it.** Rounds R1-R6
corrected *exposure* and *mechanics* (R6 adding a third class, *cost accounting* — mechanics applied to the
comparison rather than to the code) and left the filing's substance untouched. **R7 did not.** It reached the
Q2 discriminator comparison itself — which §10's own exit condition names as in-scope, altitude-qualifying
substance — and changed its outcome from a recommendation to a leveled decision. **R8 reached the same
comparison and did NOT change its outcome:** both of its findings refine one column each and cancel on the
balance, which is why R8 is recorded as the round that *tested* the leveling and left it standing. **R9 is the
terminating round** — one finding on (i)'s write-side cost (the leveling again unmoved) and one on the
ratification ask's irreversibility framing, the latter being the first R7-or-later finding to land on a surface
§10 names as *live* rather than as spec-leg-routable:

| Round | What it corrected | Class |
|---|---|---|
| R1 | Two exposure over-claims at §2 (episodic-kind denial; the hint path's producer-defined candidate family) | exposure |
| R2 | The review branch's durability (durable-but-inactive, not ephemeral); the §3 data-flow claim's scope (composed-scope path only) | exposure + mechanics |
| R3 | The §5 join premise (`EPISODIC_RUN` has two writers against one `memory_id`; `memory_refs` is not the key) | mechanics |
| R4 | Reading A's reach rationale (promotion is the reach transition, not a durability one); the §5 join key (`idempotency_key`, not `action_id`) | rationale + mechanics |
| R5 | No fork-body correction — the register carriers (YAML + mirror) synced to the R4 join semantics | carrier sync |
| R6 | The §5 option-(i) cost accounting (content vs envelope variants: identity movement belongs to the content variant alone, and the envelope variant is the real contender — its `EPISODIC_RUN` overwrite behaviour re-verified rather than inherited); the §2 exposure framing (no single named change creates live auto-promotion — the combination table, and the §7/§8 interim triggers restated with the transition each enables) | cost accounting + exposure |
| R7 | **[P1]** the (ii-a) join's version-binding: a matched, correctly-qualified, non-`None`-provider row need not be a row about the *stored version* — exhibited by a shipped test — so the join owes a mandatory record/ledger coherence check, a sixth `UNVERIFIABLE` case, and an explicit disposition of the residual that check provably cannot reach. **[P2]** the R3/R6 multi-writer penalty on (i-envelope) is **false** — envelope and content are written together from one call, so the field describes the version it ships inside, which is (ii-a)'s semantics reached directly; and on the divergent case the asymmetry **inverts** in (i-envelope)'s favour. Net: **the Q2 comparison levels and the recommendation is withdrawn** | mechanics + **discriminator outcome** |
| R8 | **[P2-1]** the R7 coherence check is **per-kind**, and is owed on `EPISODIC_RUN` alone: `cli_profile` / `engine_class` are content-side only on the run kinds, `step_id` only on the turn / tool kinds, and every non-run kind derives `memory_id` — hence the join key — from `content_hash`, so the key *is* the content binding and the stale-version window cannot open there; stated kind-blind, the check would false-`UNVERIFIABLE` the entire non-run corpus. **[P2-2]** option (i) varies along **two** axes, not one — placement (R6) **and payload** — and the boolean `captured_cross_family` the section's own opening offered was priced with the family value's costs (a value domain, a second family-valued field) that it does not carry; analysed on its own it is the cheapest shape of (i), must be a tri-state to avoid recording an undetermined `false`, and cannot answer *which* family — bounding reading B's flag to present/absent. Net: **both columns refined, the level holds, no recommendation restored** | cost accounting + mechanics scope |
| R9 | **[P2-1]** (i)'s write-side cost was **overstated**: the filing said "touches every capture writer — six `capture_*` methods plus `_capture` / `_record` thread the new value". There are **seven** such methods, and none needs to thread anything — all already take `provider` and pass it to `_capture` → `_record` (`memory_capture.py:649-658`), which also holds the resolved scope (`_scope_for_record`, `:1038-1042`), so the predicate is derived at **one** central site with no public signature change; an unknown-defaulted optional field also leaves the other three `MemoryRecordEnvelope` constructors and every pre-amendment envelope intact. The level is **unmoved**: (ii)'s write side was already zero, and the three axes carrying its side (existing records, aggregate-run provenance, comparison-basis flexibility) are untouched — what changes is the cost's *kind*, a contract obligation rather than a seven-signature refactor. **[P2-2]** the **ratification ask** called the A/B/C choice *"irreversible … no way to re-adjudicate the already-promoted records"* — too strong. `_semantic_record_content` persists `source_memory_refs` (`memory_promotion.py:932`) and capture rows retain `provider`, so a later migration can traverse lineage → row → provider and supersede or deny promotions made under a reversed position. The ask now states the unwind **exactly**: costly and **incomplete**, bounded by missing (cases 1/3), repaired (case 5, `provider = None` by construction) and stale (case 6, `EPISODIC_RUN`) rows, plus the procedural path carrying no `source_memory_refs` at all — and the gate stands on *when* the decision is cheapest, not on impossibility | cost accounting + **the operator-facing ask** |

**Stable across all nine rounds, uncorrected by any of them:** the three READINGS (A / B / C) and their
respective owed spec text; the recommendation of **B** on Q1; the [MODERATE] confidence on both Q1 and Q2;
the A-as-recorded-interim option, *with* named interim-ending triggers; the §1 witness; the §8 ratification
ask *as an ask* — that the A/B/C choice is the operator's and is a real commitment, not a default (its Q1 item
is verbatim across all nine; its Q2 item now presents two options instead of one, plus R8's payload sub-choice
under (i)); and the §9 routing. Eight independent out-of-family passes have found nothing against any of those.

**One qualification to that list, added at R9 rather than absorbed into it.** R9 [P2-2] *did* reach the
ratification ask — the first finding since R4 to touch a surface §10 names as live. What it corrected is the
ask's **justification**, not the ask: "irreversible, with no way to re-adjudicate" became "a durable commitment
whose practical unwind is a costly and partially-complete migration, bounded by missing / repaired / stale rows
and by the procedural path's absent lineage." The gate survives on a *different and narrower* ground — that the
cheapest moment to decide is before durable records accumulate — which is a strengthening of the ask's honesty
and a weakening of its rhetoric. The operator is not being asked a different question; they are being told the
true cost of answering it wrongly.

**What is NOT stable, stated plainly rather than folded into the list above:** the **Q2 mechanics comparison**.
It has now been corrected **three times** — R3 (wrong field family), R4 (wrong uniqueness guarantee), R6
(variant-blind cost accounting) — R7 corrected it a fourth and fifth time, once on each option, with the
result that it no longer carries a preference at all, **R8 a sixth and seventh time, again one per side**
(the coherence check over-scoped; the boolean payload over-priced), and **R9 an eighth** — (i)'s write-side
reach, overstated a third time in a row on the same column. The R6 text claimed the preference "still
did not move" under the sharpest test yet; R7 is a sharper one, and it moved; R8 is sharper still and it did
**not** move — the two refinements point in opposite directions and cancel; R9 is sharper again on (i)'s side
alone and it did not move either, because the axes (ii) wins on are not the axis R9 touches. Q2 is therefore
presented **leveled** — a two-option decision for the spec leg, with a payload sub-choice under (i) — rather
than picked. The three A/B/C readings and the operator-facing ask remain the filing's substance and remain
stable; that is still the artifact this filing owes, and it is undamaged by Q2's mechanics having proved to be
the unstable part. **That EIGHT corrections have landed on one comparison — three of them successively
striking a cost from the same option — is itself the finding the spec leg should carry: this is a mechanics
surface that does not converge by review, and §10's cap is the right response to it.**

**The cap, stated as a rule rather than an enumeration.** Residual mechanics claims not corrected above are
**bounded by rule, not by exhaustive review**: every mechanics claim in this filing is a claim about code at
`26720e8e` (the R9 verification HEAD; no file under `harness-*/` differs from the `dd2a8c1a` grounding HEAD or
from R3's `6ab41d7f`, R4's `ca0cc5a2`, R6's `1c99e208`, R7's `d8df7647` or R8's `d9907c24` — every commit on
this branch is doc-only, verified by `git diff --name-only dd2a8c1a 26720e8e`, which lists only the fork doc
and its two register carriers), and the
spec leg that discharges `B-92` re-grounds all mechanics against its **own** HEAD before
authoring contract text — the `B-86` → `U-MEM-26` precedent, where the spec leg re-verified the capture-path
mechanics rather than inheriting the fork doc's. A mechanics error surviving here therefore cannot reach the
spec: it is caught at the leg that consumes it, by a pass that must read the code anyway. What a further
review round can still change is only what re-grounding would *not* catch — a defect in a READING, in the Q1
recommendation, or in the ratification ask.

**The exit condition, restated at R7 rather than re-asserted — because R7 satisfied the previous one.** The
R4-R6 exit condition was: *a finding that would change the A/B/C choice, the Q2 discriminator choice, or the
operator-facing ask.* R7's [P2] **did** change the Q2 discriminator choice — it dissolved it into a leveled
pair — so R7 was a legitimate seventh round under the rule as written, not a violation of it. What that
demonstrates is the rule working, not the rule failing.

**Consequently, and with Q2 no longer carrying a preference to overturn, the exit condition tightened to:** a
finding that would change the **A/B/C reading**, the **Q1 recommendation of B**, or the **operator-facing
ask**; or, on Q2, a finding that establishes the missing *requirement* (stored-version vs aggregate-run
provenance) — the one thing that would restore a principled preference. Findings below that altitude — a
mis-cited line, a mechanism detail stated at the wrong precision, or a further refinement of a comparison the
filing now declines to decide — should be **registered against the spec leg** rather than spun into a further
correction round here, per the non-convergent-adversarial-hardening discriminator (*"does this finding
invalidate the carrier's premise?"* — if no, stop). Q2's mechanics in particular are now **explicitly** the
spec leg's: it re-derives them against its own HEAD, and it is the leg that must state the requirement anyway.
The filing remains sound as a decision artifact on its A/B/C substance, which nine rounds have left intact.

**R8 measured against that rule, honestly — it sat ON the boundary.** Neither R8 finding changed a reading,
the Q1 recommendation, the ask, or the missing requirement; both were *refinements of a comparison the filing
declines to decide*, which the paragraph above routes to the spec leg. They were applied there rather than
registered for one reason: each was a **false statement in the filing's own text** (a check specified over
kinds whose writers do not carry the fields it compares; a costing that charged a variant with costs it does
not have), and a fork doc that states a falsehood about the code is not a sound decision artifact even when
the falsehood does not move the decision — the same "stated rather than quietly repaired" standard R3-R7 were
held to. R8 recorded that *"that reasoning does not generalize to another round."*

---

### **SOUNDNESS EXIT — declared at R9. This filing is CLOSED to further review rounds.**

*Per the PD-9 cap this section has carried since R4, and on the `deferred-mechanism spec leg exits on
soundness, not review-quiet` precedent: the exit is declared on the filing's **soundness as a decision
artifact**, not on a review going quiet.*

**Why R9 was admitted at all, when R8 declared itself the last round the rule admits.** Because R9 [P2-2]
landed on the **ratification ask** — one of the three surfaces the exit condition names as *live*, and the
first finding since R4 to reach one. Under the rule as written that is an admissible round, not a violation of
the cap; the cap forecloses further **Q2-mechanics** rounds, which is a different thing. R9 [P2-1] *is* such a
mechanics finding and would have been registered against the spec leg on its own — it was applied alongside
[P2-2] only under R8's own false-statement standard, because the sentence it corrects ("touches every capture
writer — six `capture_*` methods … thread the new value") was false about the code in two independent ways at
once. Applying it in the round that was already open costs nothing; it does not reopen the cap.

**The exit, stated as a conclusion.** Nine rounds. Across all nine, the load-bearing substance never moved:
**the three A/B/C readings and their owed spec text, the Q1 recommendation of B at [MODERATE], the
A-as-recorded-interim option with its named interim-ending triggers, the §1 witness, the §9 routing, and the
ratification ask *as an ask*.** Eight out-of-family passes found nothing against any of them. What *did* move,
repeatedly, was the **Q2 mechanics comparison** (eight corrections, one verdict change) — which the filing now
explicitly declines to decide and hands to the spec leg — and, at R9, the **precision of the ask's
justification**, which is now stated exactly rather than rhetorically. A filing whose substance is stable, whose
unstable surface has been identified, bounded and routed, and whose operator-facing ask is precision-qualified
is **sound**, and soundness is the exit criterion.

**What this closes, by rule.** All remaining sub-altitude mechanics are the **spec leg's**, without exception
and without a further round here: the Q2 option choice and its payload sub-choice; the join key, its
qualification, the six-case `UNVERIFIABLE` set and the multi-match arm; the record/ledger coherence check, its
`EPISODIC_RUN` scope and its detection bound; the α/β/γ residual disposition; under (i) the field's placement,
payload, derivation rule, tri-state unknown and hash-inertness; and the missing *requirement* statement
(stored-version present/absent vs by-family vs aggregate-run) that would decide between them. The spec leg
re-grounds every one of these against its **own** HEAD before authoring contract text (the `B-86` → `U-MEM-26`
precedent), so no mechanics error surviving here can reach the spec.

**Any further finding against this filing — including a factually correct one — is to be registered against the
spec leg (`B-92`), not applied here.** The single exception the cap still admits is a finding that would change
an **A/B/C reading**, the **Q1 recommendation of B**, or the **ask itself** (that the choice is the operator's
and is a real commitment) — none of which nine rounds has touched. What remains owed is not review. It is the
operator's answer to §8.

---

## §11 RATIFICATION — Reading B (flag + gate); operator, 2026-07-29

**The §8 ask is ANSWERED. This filing's decision surface is closed; what remains is the spec leg.**

**Q1 — RATIFIED: Reading B.** The operator selected **B — "flag + gate"** on **2026-07-29**, via
`AskUserQuestion` in the autonomous-loop session (root `CLAUDE.md` §14.2 — the interactive menu is this
workspace's ratification primitive; §12.4.1 — the loop drives an item to its *genuine* gate and surfaces
exactly that, which is what this ask was). The A/B/C menu was presented as §8 item 1 states it, with **B
recommended per §7**, and the selected option read:

> *"Cross-family-produced candidates carry a risk flag AND a review gate (no silent auto-promotion;
> eligibility preserved) … Requires the discriminator first (spec leg picks the mechanism from the filing's
> leveled Q2 analysis)."*

Against §4's Reading B text, that ratifies both halves and neither neighbour: **eligibility is PRESERVED** —
reading C's outright refusal is foreclosed, and with it the harm the B-86 council named (C3's *"silent,
permanent, inverted-in-timing data loss"*, C6's continuity abstraction) — **and the silence is REMOVED** —
reading A's status quo is not adopted as the permanent posture. Per §4's own cost line, the ratified position
**states the gate, not only the flag**: such a candidate is `review_required` and never
`auto_promote_allowed`. The **A-as-recorded-interim** variant was **not** selected, so its T1 / T2 / T3
interim-ending triggers are not owed — B is ratified directly, as the target posture.

**Q2 — deliberately NOT decided here.** §8 item 2 presents Q2 **leveled** — (i-envelope), with the
(i-envelope-bool) / (i-envelope-family) payload sub-choice, against (ii)/(ii-a) — without a recommendation,
R7 having struck the last asymmetry that held one. The operator-selected option's own text routes it: *"spec
leg picks the mechanism from the filing's leveled Q2 analysis."* That is the disposition §10's cap already
made binding, and it is unchanged by this ratification. **The spec leg owns, without exception:** the Q2
option and its payload sub-choice; the join key, its `operation_kind == CAPTURE` qualification, the six-case
`UNVERIFIABLE` set and the multi-match arm; the record/ledger coherence check with its `EPISODIC_RUN` scope
and its detection bound; the α/β/γ residual disposition; under (i) the field's placement, payload, derivation
rule, tri-state unknown and hash-inertness; and — the one thing that decides between the options — the
**requirement statement** (stored-version present/absent vs by-family vs aggregate-run). §8's discriminator
guidance stands as *input, not as a decision*: reading B's requirement as this filing argues it is
stored-version provenance **present/absent**, which §5's three-column table answers most cheaply with
**(i-envelope-bool)** — a recommendation the spec leg re-derives against its own HEAD, not a ratified choice.

**Next step — the spec-writer apply leg, then the impl leg.** §9's routing is unchanged, and the sequencing
is the `B-86` → PR #1147 (spec leg) → PR #1148 (impl leg) precedent chain: spec first, impl second, never
bundled.

1. **Spec leg** (`spec-writer`, its own arc/PR): the **C-MEM-10** amendment carrying reading B — the risk-flag
   vocabulary sentence (`PromotionCandidate.risk_flags` is an **open** `list<string>` in the C-MEM-10 Contract
   `PromotionCandidate` block, so this is a vocabulary addition, **not** a schema widening) **plus** the
   gate-bearing obligation that makes the flag non-inert; **plus the discriminator's owed contract text** at
   whichever of C-MEM-03 (option (i)) or C-MEM-08 (option (ii)) the leg selects, per §6's per-reading drafting
   targets and §5's owed-sentence accounting; **plus** the `Implementation_Plan_Memory_Substrate_v1.md` delta
   (a new **U-MEM-27**, owed under B per §9); **plus** clearance markers at `.harness/clearance/` in the same
   PR per root `CLAUDE.md` §4.5. An out-of-family `just codex-review` decorator on the C-MEM diff is
   recommended per §9 — threat-model-adjacent text inside an already-cleared contract is exactly the shape
   that earned it on the B-86 spec leg.
2. **Impl leg**: follows the spec leg as its own arc, per §9.

**Run the spec leg as a FRESH, FOCUSED session.** §10's cap is a *requirement* on that leg, not a courtesy:
every mechanics claim in this filing is a claim about code at `26720e8e`, and the spec leg **re-grounds all of
them against its own HEAD** before authoring contract text (the `B-86` → `U-MEM-26` precedent, where the spec
leg re-verified the capture-path mechanics rather than inheriting the fork doc's). A session carrying this
filing's nine review rounds forward is the wrong instrument for that — it inherits precisely the claims the cap
requires be re-derived.

**Register disposition.** `B-92` **stays** `design_substrate_gated`. The ratification answers §8; it does not
run the spec leg, and the register's own status enum is explicit that *"a filed doc does NOT flip the status —
only ratified + applied spec deltas"*. The row flips to `open` when the C-MEM + plan deltas are APPLIED.
