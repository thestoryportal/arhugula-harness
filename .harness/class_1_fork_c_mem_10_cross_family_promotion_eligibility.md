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
`6ab41d7f` on the R3 pass, and re-verified again at `ca0cc5a2` on the R4 pass (no code file differs across
the three HEADs; every R4 cite below was read directly, not carried).

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
- **Future policy configs.** A deployment setting `PROMOTE_SEMANTIC` / `PROMOTE_PROCEDURAL` with
  `ReviewMode.AUTOMATIC` — a configuration C-MEM-09 explicitly permits — makes the path auto-promoting, with
  no family term anywhere for it to consult.
- **A first hint producer.** The moment one populates `promotion_candidates`, entry point 1 becomes live with
  its candidate-family convention still unpinned.

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
policy decision), the hint path is unfed and its candidate convention undefined. What is real *now* is the
contract gap, which a single policy field or a first producer converts into a live exposure with no further
review. That is precisely why this is a Class 1 spec question and not a Phase 7 bug — and it is also why the
urgency is **low and the necessity is not**: nothing is leaking today, and nothing prevents it from leaking
the day a config changes.

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

- **Blast radius: high.** C-MEM-03's field shapes were preserved *byte-unchanged* at v1.1, and the change-note
  says so explicitly at **"Sections preserved verbatim at v1.1."**: *"Zero new record type, zero new field,
  zero new enum member, zero change to any ledger, packet, or telemetry shape."* Adding one reverses that
  posture one delta later.
- Touches every capture writer, and the field must be reconciled against the C-MEM-03 value domain
  (§"`MemoryScope.provider_family` value domain and derivation") — a *second* family-valued field on the same
  record, with its own null semantics, sitting beside `MemoryScope.provider_family` and meaning something
  different. That is a one-source-of-truth hazard in its own right.
- `MemoryScope` is hash-inert for `memory_id` (`memory_capture.py:574-575` per the B-86 §3 P5 finding), but a
  new **content** field is not — content is hashed (C-MEM-03 §Invariants: *"`content_hash` is computed over
  canonical serialized content excluding derived indexes."*), so this option moves identities for newly
  written records and needs an explicit forward-only statement.
- Upside: self-contained; no cross-contract read dependency; works for a record read in isolation — **with one
  exception the R3 finding exposes, recorded at the assessment below**: on `EPISODIC_RUN`, which is one stored
  record per run written by run-start and overwritten by run-close, a stored field is set by *whichever writer
  ran last* and records nothing about which that was.

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
  case to three, R4 takes it to five.** All of:
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

  Plus the ambiguity arm: **any** resolution returning more than one row is `UNVERIFIABLE` (vacuous under the
  (ii-a) key-shaped join, mandatory in the contract regardless — (ii-b) above).

  Each yields *unknown*, not *same-family*. The house idiom for exactly this is already established and should
  be reused verbatim rather than re-invented: the B-91 tri-state convergence (`MATCH` / `CONFIRMED_MISMATCH` /
  `UNVERIFIABLE`, where a determination is only reported when it was actually reached). Under reading B the
  honest mapping is `UNVERIFIABLE` → review_required, never auto-promote.

**Assessment, re-run after the R3 and R4 findings — (ii) stands, by a narrower margin each round, and the
accounting is stated rather than asserted.**

- **What the findings cost (ii).** The "join key already exists" claim was too clean, twice over. R3: the key
  is not `memory_refs`, and the one-row-per-record premise was false for the one record kind that has multiple
  writers. R4: the key is not `action_id` either — the ledger's uniqueness is on `idempotency_key`, and the
  capture path's deterministic `idempotent:{action_id}` derivation is what makes that key reconstructible from
  a stored record. The contract now owes **four** things where it originally owed two: the join key stated
  exactly (the capture `idempotency_key`, composed from the record's own `event_type`; explicitly **not**
  `memory_refs` and **not** the bare `action_id`), the `operation_kind == CAPTURE` qualification, the
  five-case `UNVERIFIABLE` set plus its multi-match arm, and the existing cross-contract-dependency sentence.
- **What they did not cost.** No new field, schema member, enum value, hash input, or identity movement. The
  event-qualification machinery is *two already-exported helpers whose docstrings name this exact
  discrimination as their reason for being exported*, and R4's key derivation is a one-line composition over
  them that the capture writer already performs. This remains a **specification** cost, not a **mechanism**
  cost — more precise sentences, not more moving parts.
- **What (i) still costs, unchanged.** A closed-schema extension at C-MEM-03 reversing v1.1's own zero-new-field
  posture one delta later; a second family-valued field beside `MemoryScope.provider_family`; content-hash
  identity movement for newly written records.
- **And (i) does not escape the finding either — this is what keeps the preference from flipping.** A content
  field on an `EPISODIC_RUN` record is written by run-start and **overwritten** by run-close, so (i) resolves
  the same ambiguity by the same last-writer-wins accident that (ii-a) resolves *deliberately* — and resolves
  it silently, since nothing in a stored field records which writer set it. (i)'s "works for a record read in
  isolation" upside is real for single-writer kinds like `EPISODIC_TURN`; for the multi-writer kind that
  produced this finding it is **weaker** than (ii-a), not stronger.

**Preference: unchanged, (ii) with (ii-a) as the join.** Stated plainly because the temptation here is to
defend the prior pick: had event-qualification required new machinery — a new key, a new index, a scan
discipline — the balance would genuinely have moved toward (i)'s single self-contained field, and this filing
would say so. It does not. Confidence on the Q2 recommendation stays **[MODERATE]** and does not recover,
because the join's *shape* has now been mis-stated **twice** (R3: the wrong field family; R4: the wrong
uniqueness guarantee). The corrected mechanics are, if anything, slightly *stronger* than the R3 draft's —
the ledger really does enforce at-most-one on the key, which the `action_id` claim only asserted — but the
recurrence is the signal: **the spec leg must state the key exactly, and state what enforces its uniqueness,
rather than gesture at "the record's capture row."**

## §6 Recommended drafting targets, per reading

| Reading | Owed spec text |
|---|---|
| **A** | **C-MEM-10 Contract** — one paragraph: promotion eligibility is determined by record scope, policy, and evidence, and is not conditioned on the provider family that produced the content during a fallback leg; the run's composed partition (C-MEM-03 §"`MemoryScope.provider_family` value domain and derivation", the continuity sentence) is the whole of the provenance question at this contract. **C-MEM-10 Invariants** — one bullet mirroring it. Nothing else; no C-MEM-08, no C-MEM-03, no plan unit beyond a coverage-matrix row. |
| **B** | **C-MEM-10 Contract** — the cross-family-captured condition; the risk-flag obligation; and, explicitly, the **gate**: such a candidate is review-required and not auto-promotable (§2's inert-flag finding makes the gate sentence mandatory, not decorative). **C-MEM-10 `PromotionCandidate.risk_flags`** — no schema change needed: the `PromotionCandidate` block's `risk_flags: list<string>` is already an open list, so the new value is a vocabulary addition at the contract, and only the impl-side `PromotionRiskFlag` enum (`memory_promotion.py:80-86`) is closed. **C-MEM-10 Invariants** — the gate as an invariant. **C-MEM-08** — if discriminator (ii), and per the R3 [P2-1] + R4 [P2] findings this is now **four** sentences, not one: (a) the capture row is the authoritative provenance source for promotion, (b) the join is keyed on the capture **`idempotency_key`, composed from the capture `action_id`, which is composed from the record's own declared `event_type`** — explicitly **not** on `memory_refs` (which cannot discriminate a shared-`memory_id` kind) and explicitly **not** on the bare `action_id` (which the ledger does not constrain for uniqueness at all — `append_memory_operation` dedups on `idempotency_key` alone), (c) the matched row must be **qualified** on `operation_kind == CAPTURE` rather than assumed to be a capture row, and (d) the five-case `UNVERIFIABLE` disposition (no reachable row / record cannot name its writer / composed key matches no row / matched row is not a CAPTURE row / matched row carries `provider = None`, the repair-row shape), plus the multi-match ambiguity arm. **or C-MEM-03** — if discriminator (i): the new field, its value domain, its null semantics, its content-hash consequence, **and** its own multi-writer disposition for `EPISODIC_RUN` (§5(i)'s last bullet). Plus a memory-plan unit (U-MEM-27) decomposing the impl leg. |
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
as the target**, not a discharge; and (b) the two triggers that end the interim are named — a policy
admitting an episodic kind into `eligible_record_kinds` (or setting `PROMOTE_*` with `ReviewMode.AUTOMATIC`),
and the first caller to populate `promotion_candidates`. Absent (b) the interim silently becomes permanent
exactly when it stops being safe. B remains the recommendation on the merits; A-as-recorded-interim is now a
close second rather than a concession. What must not happen is still the third outcome: leaving it silent a
second time.

If B is selected, take **discriminator (ii)** with the **(ii-a) event-qualified join** (§5) — cheaper, no
schema extension, no identity movement, and it reuses the B-91 tri-state, the B-89 canonicalization
authorities, and the two already-exported capture-side helpers verbatim. Neither the R3 [P2-1] nor the R4 [P2]
finding **moved this preference** (§5's re-run assessment states why in full, including the respect in which
(i) is *worse* than (ii-a) on the R3 finding). Between them they raised (ii)'s owed contract text from one
sentence to four and its `UNVERIFIABLE` set from one case to five, and they hold the Q2 confidence at
[MODERATE] because the join's shape has now been mis-stated twice — once in field family, once in what
enforces its uniqueness.

## §8 Ratification ask — operator decision

The A / B / C choice is the operator's. It is an irreversible contract commitment: once C-MEM-10 states a
position, records written under it accumulate against that position, and reversing later leaves a
mixed-provenance corpus with no way to re-adjudicate the already-promoted records (promotion supersession
does not delete — C-MEM-03 §Invariants: *"Supersession does not delete the prior record."*).

Decisions owed:

1. **Q1 — A, B, or C** (or "A as a recorded interim, B as the target" — which, per §7, the corrected
   zero-live-exposure picture makes a materially defensible choice, provided the two interim-ending triggers
   are recorded with it: an `eligible_record_kinds` / `PROMOTE_*` policy change, and the first caller to
   populate `promotion_candidates`).
2. **Q2, only if B or C** — discriminator (i) new field or (ii) C-MEM-08 ledger join. Recommendation: **(ii),
   with the (ii-a) event-qualified join** — the ledger row is selected by the capture **`idempotency_key`**
   (`idempotent:capture:{event_kind}:{memory_id}`, composed from the record's own declared `event_type`),
   **not** by `memory_refs`, which cannot discriminate the run-start / run-close rows that share one
   `EPISODIC_RUN` `memory_id`, and **not** by the bare `action_id`, which the ledger does not dedup on; the
   matched row is qualified on `operation_kind == CAPTURE`, and the five-case `UNVERIFIABLE` residue plus the
   multi-match arm fail closed (review_required, never auto-promote). Sub-choice (ii-b) — fail closed on *any*
   multi-row ambiguity, defining no event-qualified key — is available and needs no new join semantics, but
   §5 records that it is a de-facto reading **C** for `EPISODIC_RUN` records and must be taken as a stated
   foreclosure, not as a conservative default.

Per root `CLAUDE.md` §12.4.1, this filing drove the question to its genuine gate: the grounding, the witness,
the prerequisite mechanics, the drafting targets, and a recommendation are all done. What remains is the
choice itself, which is a real architectural commitment and not a default.

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
corrected the §5 join premise, and R4 corrected the Reading-A reach rationale and the §5 join key (this pass).

**No Phase 7 execution is halted by this filing.** U-MEM-26 has landed; the question was already scoped out
of it at `Implementation_Plan_Memory_Substrate_v1.md` U-MEM-26, subsection "Out of scope for this unit:".
What is halted is any *implementation* of a promotion-side family term, which must wait for the ratification
above.

## §10 Review-time inventory — the soundness cap on this filing

*Filed at R4 per the PD-9 review-time-inventory discipline (`Project_Workflow_v1_19.md` §7.5.2 PD-9,
adversarial-review-loop non-convergence discriminators), and on the `deferred-mechanism spec leg exits on
soundness, not review-quiet` precedent. This section bounds the review surface so a further round has a
principled exit rather than an open-ended one.*

**What four rounds converged on, and what they did not touch.** Every round corrected the same class of
claim — *exposure* and *mechanics* — and no round has touched the filing's substance:

| Round | What it corrected | Class |
|---|---|---|
| R1 | Two exposure over-claims at §2 (episodic-kind denial; the hint path's producer-defined candidate family) | exposure |
| R2 | The review branch's durability (durable-but-inactive, not ephemeral); the §3 data-flow claim's scope (composed-scope path only) | exposure + mechanics |
| R3 | The §5 join premise (`EPISODIC_RUN` has two writers against one `memory_id`; `memory_refs` is not the key) | mechanics |
| R4 | Reading A's reach rationale (promotion is the reach transition, not a durability one); the §5 join key (`idempotency_key`, not `action_id`) | rationale + mechanics |

**Stable across all four rounds, uncorrected by any of them:** the three READINGS (A / B / C) and their
respective owed spec text; the recommendation of **B** with discriminator **(ii)/(ii-a)**; the [MODERATE]
confidence on both Q1 and Q2; the A-as-recorded-interim option with its two named interim-ending triggers;
the §1 witness; the §8 ratification ask; and the §9 routing. Four independent out-of-family passes have found
nothing against any of them. That is the filing's convergence claim, and it is the one that matters, because
the artifact this filing owes the operator is a **decision**, not a mechanics reference.

**The cap, stated as a rule rather than an enumeration.** Residual mechanics claims not corrected above are
**bounded by rule, not by exhaustive review**: every mechanics claim in this filing is a claim about code at
`ca0cc5a2`, and the spec leg that discharges `B-92` re-grounds all mechanics against its **own** HEAD before
authoring contract text — the `B-86` → `U-MEM-26` precedent, where the spec leg re-verified the capture-path
mechanics rather than inheriting the fork doc's. A mechanics error surviving here therefore cannot reach the
spec: it is caught at the leg that consumes it, by a pass that must read the code anyway. What a further
review round can still change is only what re-grounding would *not* catch — a defect in a READING, in the
recommendation, or in the ratification ask.

**Consequently, the exit condition for further review of *this filing* is:** a finding that would change the
A/B/C choice, the Q2 discriminator choice, or the operator-facing ask. Findings below that altitude — a
mis-cited line, a mechanism detail stated at the wrong precision — should be **registered against the spec
leg** rather than spun into a fifth correction round here, per the non-convergent-adversarial-hardening
discriminator (*"does this finding invalidate the carrier's premise?"* — if no, stop). The filing is sound as
a decision artifact; the mechanics are the spec leg's to re-derive.
