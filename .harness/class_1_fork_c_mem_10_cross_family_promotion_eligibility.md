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

All code and spec cites below were re-grounded by direct read at HEAD `dd2a8c1a`.

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
`:153`/`:155`. What it means downstream at C-MEM-10 is the open question.

**Carrier 2 — the lineage.** The question was surfaced at the B-86 council convening (2026-07-28) as C3's
fourth forward item and carried, unresolved, through every artifact of that arc:

- `.harness/class_1_fork_b86_memory_scope_provider_family_keying.md` §7, fourth bullet: *"**C3
  promotion-eligibility question** (records captured during a cross-family leg under C-MEM-10) — flagged, out
  of B-86 scope, C-MEM-10 policy territory; carried here as a named open question for the spec-leg author to
  restate or discharge."*
- `design-substrate/Spec_Memory_Substrate_v1.md:37` (the v1.1 change-note), byte-exact:

  > **Named open question carried forward, not discharged.** Fork §7: whether records captured during a
  > cross-family fallback leg are promotion-eligible under C-MEM-10. That is C-MEM-10 policy territory,
  > outside B-86's scope; v1.1 neither resolves nor forecloses it, and it is restated here so it does not
  > disappear with the fork doc.

- `design-substrate/Implementation_Plan_Memory_Substrate_v1.md:933` (U-MEM-26, "Out of scope for this unit"):
  *"Promotion eligibility of records captured during a cross-family fallback leg, which remains a C-MEM-10
  policy question carried as a named open question at the spec v1.1 change-note."*

The spec-leg author restated it rather than discharging it. This filing is the discharge arc.

**Why it is Class 1 and not a Class 3 note.** The spec named the question, so nothing here is a newly
surfaced primitive (X-AL-3 is not engaged by the *question*). But every one of the three readings requires
CONTRACT text — C-MEM-10 today has no provenance term at all, and two of the three readings additionally
require a discriminator that does not exist at any contract (§3). An implementation choosing any reading on
its own authority would be silent absorption.

## §2 Current behaviour at HEAD `dd2a8c1a` — permissive, and silent

There are **two** promotion entry points. Neither has a family term.

**Entry point 1 — the hint-extraction path.** `PromotionCandidateExtractor.extract_from_records`
(`harness-runtime/src/harness_runtime/memory_promotion.py:286-297`) reads hints from a stored record and
calls `_candidate_from_hint` (`:296`). That builds risk flags with `source_scope=record.envelope.scope`
(`:626-628`) — i.e. the **composed run scope**, `anthropic` on the witness above. `_scope_escapes_source`
(`:698-712`) delegates the family comparison to `_family_escapes_source` (`:715-743`), which canonicalizes
both sides and compares candidate family against **source-record** family. Both are `anthropic`. No
`CROSS_SCOPE` flag. `_auto_promote_allowed` (`:776-790`) consults `review_required`, `resolution.review_mode`,
`hint.confidence`, and `hint.proposed_kind` — **no family term, and no risk-flag term** (see the next
paragraph).

**Entry point 2 — the live model-facing tool path, which is the sharper one.**
`MemoryToolExecutor._propose_promotion` (`harness-runtime/src/harness_runtime/memory_tool_executor.py:399-435`)
serves the C-MEM-14 `memory.propose_promotion` tool (`Spec_Memory_Substrate_v1.md:556`). It reads a source
record **by reference** (`:408-411`), hardcodes `confidence=PromotionCandidateConfidence.HIGH` (`:423`),
takes `auto_promote_allowed` from policy alone (`_promotion_auto_allowed`, `:897-903`), and computes
`risk_flags=_promotion_risk_flags(source)` (`:425`) — which inspects **only** `redaction_state` (`:882-885`).
No scope comparison of any kind. So the cross-family-captured record is reachable by the *primary-family*
model on any later same-family turn — a path the C-MEM-13 withhold does not and should not touch, because on
that turn the acting model is legitimately in-partition.

**A grounded correction to the obvious "just flag it" framing.** `risk_flags` **gates nothing today**. A
repo-wide grep finds it only at its definition, its two construction sites, and its persistence
(`memory_promotion.py:175/193/222/576/626/649/672/677`, `memory_tool_executor.py:425/882`); no gating
predicate reads it. `_review_required` (`memory_promotion.py:762-773`) never consults it, and
`_auto_promote_allowed` reads `review_required`, not flags. So `CROSS_SCOPE` is **advisory metadata that is
carried and persisted and never acted on**. Any reading that relies on flagging must therefore state the
**gate** as well as the flag, or it lands inert — the enforced-vs-advisory distinction the workspace has been
bitten by before.

**Net.** An `openai`-produced record is auto-promotable under the `anthropic` family on exactly the same
terms as a genuinely same-family record, with no flag, no review, and no record of the provenance anywhere in
the promotion decision.

**Live-ness, stated honestly.** Entry point 2 is live (a model-callable tool). Entry point 1 is structurally
reachable but currently unfed on the automatic path: the sole production caller of `capture_turn_completion`
passes `promotion_candidates=()` (`harness-runtime/src/harness_runtime/automatic_memory.py:273`), and the
extractor is reached from compaction safety (`memory_compaction_safety.py:159`). So the hint path is latent
today and becomes live the moment a caller populates the field. The exposure is real via entry point 2 and
latent-but-one-line-away via entry point 1.

## §3 The prerequisite finding — the pipeline cannot discriminate even if policy said to

**This is the load-bearing part of the filing.** Two of the three readings below are not merely unbuilt; they
are currently *unrepresentable*.

`EpisodicMemoryCapture.capture_turn_completion` writes a `content` mapping
(`harness-runtime/src/harness_runtime/memory_capture.py:407-422`) carrying `event_type`, `run_id`, `turn_id`,
`step_id`, the two summaries, `summary_source`, `summary_model`, `summary_hash`, `capture_mode`,
`tool_event_refs`, `failure_observations`, `promotion_candidates`, and `token_usage`. **No `provider` field
and no dispatched-`model` field.** The `provider` and `model` arguments are passed through to `_capture`
(`:431-432`) and from there to two places only:

1. the C-MEM-08 memory-operation ledger row — `_operation_payload(..., provider=provider, model=model, ...)`
   (`:694-707`), which constructs a `MemoryOperationPayload` carrying `provider` (`:1006`), `model` (`:1007`)
   and `memory_refs=(memory_id,)` (`:1010`); and
2. the C-MEM-19 telemetry span attributes (`:686-688`, `:714-716`).

The record's *envelope* scope, meanwhile, is the run's composed scope verbatim (`_scope_for_record`,
`:1048-1086`) — deliberately, per B-89.

Promotion never reads either. `_hints_from_record` (`memory_promotion.py:545-560`) reads
`record.content` alone; `_propose_promotion` reads `source.envelope` and `source` content. **There is no path
from a stored record to the provider family that actually produced its content.**

Consequence: readings **B** and **C** below cannot be implemented at all until a discriminator is surfaced,
and surfacing one is itself contract-altitude work (§5) — X-AL-3-blocked at Phase 7. Only reading **A** is
implementable against the substrate as it stands (and reading A's "implementation" is a spec sentence, not
code).

## §4 The three readings

### Reading A — promotion-eligible, unchanged; the permissiveness made EXPLICIT

C-MEM-10 gains a sentence stating that a record's promotion eligibility is determined by its record scope and
its policy/evidence, and is **not** conditioned on which provider family produced its content during a
fallback leg. Status quo behaviour is unchanged; what changes is that it becomes a *stated* position rather
than an accident of a pipeline that cannot see the fact.

Rationale:

- **The composed scope IS the run's declared identity.** C-MEM-03 `:153` states the run-level derivation as
  contract: *"A fallback chain is a continuity mechanism, and the run's memory partition is one of the
  run-level identities it preserves across that boundary."* A record inside that partition is, by the
  contract's own construction, a record of that run. Conditioning promotion on sub-run provenance
  re-introduces at C-MEM-10 exactly the per-dispatch partitioning C-MEM-03 `:153` forbids at C-MEM-03.
- **Capture-time scoping was ratified at B-86/B-89 on exactly this ground.** C-MEM-13 `:509`: *"Harness-authored
  memory capture is unaffected: capture is a different authorship class and crosses no boundary the harness
  does not already hold."* The harness already holds the content; promotion confers durability on content the
  harness holds, and grants the foreign candidate no new reach.
- **The content passed the same capture pipeline as any other record** — same redaction state, same
  `summary_source`, same policy resolution.

Cost: cheapest by a wide margin (one contract paragraph, zero code, zero discriminator). Risk: it ratifies a
permissiveness that policy has never actually evaluated — see §7.

### Reading B — eligibility preserved, silence removed

Cross-family-produced candidates remain eligible, but a candidate whose source record was captured during a
cross-family leg is marked with a `CROSS_SCOPE`-equivalent risk flag **and** that mark is made
gate-bearing: such a candidate is `review_required` and never `auto_promote_allowed`. Continuity is
preserved; what is removed is *silent* auto-promotion.

Rationale:

- The memory threat model already treats provenance as a first-class axis: *"The memory substrate treats
  model-authored and external CLI-authored memory as untrusted until policy promotes it."* (`:529`), and
  *"Model-authored notes are episodic by default and cannot become injectable semantic memory without policy
  and evidence."* (`:539`). Promotion is the trust-conferring step, and `:531` names *"Cross-run
  prompt-injection persistence through promoted semantic/procedural memory"* as a covered threat — the exact
  channel this question sits on.
- It satisfies C10's B-86 position (a durable, primary-attributed, promotion-eligible write needs a real
  gate) at the *right* mechanism, without paying C3's continuity cost — structurally the same move B-86
  itself made (keep the run-level partition; satisfy the safety voice at a different mechanism).

Cost: requires the §3 discriminator. **And it must state the gate, not only the flag** (§2's grounded
correction): a flag alone is inert at HEAD.

### Reading C — refuse promotion of cross-family-captured records

Strongest isolation: such records are ineligible for promotion outright; they remain episodic and
retrievable, but can never become injectable semantic/procedural memory.

Rationale for: closes the `:531` channel completely for foreign-family content; needs no judgement about
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
  says so explicitly (`:43`): *"Zero new record type, zero new field, zero new enum member, zero change to any
  ledger, packet, or telemetry shape."* Adding one reverses that posture one delta later.
- Touches every capture writer, and the field must be reconciled against the C-MEM-03 value domain
  (`:145-157`) — a *second* family-valued field on the same record, with its own null semantics, sitting
  beside `MemoryScope.provider_family` and meaning something different. That is a one-source-of-truth hazard
  in its own right.
- `MemoryScope` is hash-inert for `memory_id` (`memory_capture.py:574-575` per the B-86 §3 P5 finding), but a
  new **content** field is not — content is hashed (`content_hash`, C-MEM-03 `:161`), so this option moves
  identities for newly written records and needs an explicit forward-only statement.
- Upside: self-contained; no cross-contract read dependency; works for a record read in isolation.

### (ii) A C-MEM-08 ledger join at promotion time

Promotion resolves the record's capture row and reads its `provider`.

- **The join key already exists, with no schema change.** `MemoryOperationEntry` carries `provider` (`:306`),
  `model` (`:307`) and `memory_refs: list<memory_id>` (`:310`); capture writes exactly one `capture` row per
  record with `memory_refs=(memory_id,)` (`memory_capture.py:1010`). Authoritative ledger for `capture` is
  `durable/memory_ops.jsonl` (`:320`).
- The ledger's `provider` is a raw provider **key**, not a family value, so the join needs canonicalization —
  and the machinery already exists and is already the house authority (`provider_family_for_scope_check` /
  `canonical_scope_family`, landed at B-86/B-89). No new normalization posture is invented.
- **Cost: read-side only, but it is a new cross-contract dependency** — C-MEM-10 would depend on C-MEM-08
  availability and readability, which C-MEM-10 does not today. It also couples a promotion decision to a
  ledger scan on `durable/memory_ops.jsonl` (append-only, hash-chained, no index over `memory_refs`).
- **The unresolvable case must be specified.** A record with no reachable capture row (promotion-authored,
  compaction-authored, native-adapter-authored, or an unreadable ledger) yields *unknown*, not *same-family*.
  The house idiom for exactly this is already established and should be reused verbatim rather than
  re-invented: the B-91 tri-state convergence (`MATCH` / `CONFIRMED_MISMATCH` / `UNVERIFIABLE`, where a
  determination is only reported when it was actually reached). Under reading B the honest mapping is
  `UNVERIFIABLE` → review_required, never auto-promote.

**Assessment:** (ii) is materially cheaper and better precedented. It requires no closed-schema extension, no
new field, no identity movement, and it reuses two existing authorities. Its two real costs — the
cross-contract dependency and the unresolvable case — are both statable in contract text.

## §6 Recommended drafting targets, per reading

| Reading | Owed spec text |
|---|---|
| **A** | **C-MEM-10 Contract** — one paragraph: promotion eligibility is determined by record scope, policy, and evidence, and is not conditioned on the provider family that produced the content during a fallback leg; the run's composed partition (C-MEM-03 `:153`) is the whole of the provenance question at this contract. **C-MEM-10 Invariants** — one bullet mirroring it. Nothing else; no C-MEM-08, no C-MEM-03, no plan unit beyond a coverage-matrix row. |
| **B** | **C-MEM-10 Contract** — the cross-family-captured condition; the risk-flag obligation; and, explicitly, the **gate**: such a candidate is review-required and not auto-promotable (§2's inert-flag finding makes the gate sentence mandatory, not decorative). **C-MEM-10 `PromotionCandidate.risk_flags`** — no schema change needed: `risk_flags: list<string>` (`:378`) is already an open list, so the new value is a vocabulary addition at the contract, and only the impl-side `PromotionRiskFlag` enum (`memory_promotion.py:80-86`) is closed. **C-MEM-10 Invariants** — the gate as an invariant. **C-MEM-08** — if discriminator (ii): a sentence naming the capture row as the authoritative provenance source for promotion, and the `UNVERIFIABLE` disposition; **or C-MEM-03** — if discriminator (i): the new field, its value domain, its null semantics, and its content-hash consequence. Plus a memory-plan unit (U-MEM-27) decomposing the impl leg. |
| **C** | Everything reading B owes, minus the flag/gate wording, plus a **refusal** invariant at C-MEM-10 and a statement of the permanent consequence (fallback-leg learning is unpromotable). Additionally owes a reconciliation sentence against C-MEM-03 `:153`'s continuity statement and against C-MEM-13 `:509`'s capture carve-out, both of which read against it. |

Under all three readings the Memory threat model needs **no** amendment: `:529` / `:531` / `:539` are the
authority the resolution conforms to, not a surface it revises — the same X-AL-3 posture v1.1 took at `:21`.

## §7 Recommendation — **Reading B** [MODERATE]

The B-86 council record decides this, and it decides it in two directions at once.

**It forecloses C.** C3's continuity argument and C6's continuity-abstraction refinement (§4, reading C) were
not incidental remarks — they are the reasoning that carried Q1, and both apply *a fortiori* to a promotion
refusal, which imposes the same "the fallback leg's memory is second-class" harm that Q1 rejected. Choosing C
would overturn a ratified council resolution one arc later without new evidence.

**It does not license A's silence.** The withhold half of that same record (Q2) rests on C10's classification
of `memory.write_note` as `write-bounded-irreversible` — *"durable, primary-attributed, supersession
non-deleting, promotion-eligible → the `:472` cross-run prompt-injection-persistence threat runs directly
through it"* (B-86 fork §4; its `:472` is quoted verbatim and is the drifted cite the v1.1 change-note `:39`
already corrected — the threat is at `:531` at this filing's HEAD). C10 named **promotion-eligibility itself**
as part of what makes that write
dangerous. C10 declined to re-key the scope because the *mechanism* was wrong, not because the concern was
absent — the council's own words: *"the defect is in the absent gate at the dispatch boundary, not in the
scope's key."* Reading B is that same resolution shape applied one contract downstream: keep the partition
(C3/C6 satisfied), put the gate where it belongs (C10 satisfied).

**And the decisive asymmetry against A is that A would ratify a decision nobody made.** Today the pipeline is
not permissive-by-policy; it is permissive-by-blindness (§3 — it cannot represent the fact). Writing "eligible,
unchanged" into C-MEM-10 would convert a structural gap into a contract commitment while the policy layer has
still never had the input. That is the *precise* defect the v1.1 change-note identified as B-86's own trigger
(`:21`): *"v1 already mandated that the provider-family boundary be enforced; it never stated what that
boundary is keyed to, which left the mandate unfalsifiable at the contract level."* Reading A repeats that
error one contract over.

**Confidence is [MODERATE], not [HIGH], and the reason is stated rather than hidden.** Reading B costs a
discriminator (§5) that reading A does not, and the live exposure is bounded: the tool path (entry point 2)
requires `ReviewMode.AUTOMATIC` plus `PROMOTE_SEMANTIC`/`PROMOTE_PROCEDURAL` policy to auto-promote at all,
and the hint path is currently unfed. An operator who wants minimum commitment now could legitimately take
**A as an interim** — but if so it should be recorded as an *interim with B named as the target*, not as a
discharge. What must not happen is the third outcome: leaving it silent a second time.

If B is selected, take **discriminator (ii)** (§5) — cheaper, no schema extension, no identity movement, and
it reuses the B-91 tri-state and the B-89 canonicalization authorities verbatim.

## §8 Ratification ask — operator decision

The A / B / C choice is the operator's. It is an irreversible contract commitment: once C-MEM-10 states a
position, records written under it accumulate against that position, and reversing later leaves a
mixed-provenance corpus with no way to re-adjudicate the already-promoted records (promotion supersession
does not delete — C-MEM-03 `:162`).

Decisions owed:

1. **Q1 — A, B, or C** (or "A as a recorded interim, B as the target").
2. **Q2, only if B or C** — discriminator (i) new field or (ii) C-MEM-08 ledger join. Recommendation: (ii).

Per root `CLAUDE.md` §12.4.1, this filing drove the question to its genuine gate: the grounding, the witness,
the prerequisite mechanics, the drafting targets, and a recommendation are all done. What remains is the
choice itself, which is a real architectural commitment and not a default.

## §9 Routing

Per root `CLAUDE.md` §4.3: Class 1 → design-phase back-flow. Routing target is the **Phase 5 spec
revision-pass** (`Spec_Memory_Substrate_v1.md` C-MEM-10, plus C-MEM-08 or C-MEM-03 per Q2), with a
`Implementation_Plan_Memory_Substrate_v1.md` delta (a new U-MEM-27) owed under readings B and C, and clearance
markers at `.harness/clearance/` in the same PR per §4.5. The impl leg follows the spec leg per the
B-33 / B-59 / B-70 / B-72 / B-86 precedent. An out-of-family `just codex-review` decorator on the eventual
C-MEM diff is recommended — the amendment is threat-model-adjacent (`:529` / `:531` / `:539`) inside an
already-cleared contract, which is exactly the shape that earned it on the B-86 spec leg.

**No Phase 7 execution is halted by this filing.** U-MEM-26 has landed; the question was already scoped out
of it at `Implementation_Plan_Memory_Substrate_v1.md:933`. What is halted is any *implementation* of a
promotion-side family term, which must wait for the ratification above.
