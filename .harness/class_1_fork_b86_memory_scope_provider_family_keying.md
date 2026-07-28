# Class 1 Fork — B-86: `MemoryScope.provider_family` keying + cross-family SERVABLE-tools posture

**Filed:** 2026-07-28 · autonomous-loop grounding arc (Round 37; register `B-86`, registered 2026-07-28 at
the B-83 arc close). **Classification: Class 1** — the memory spec is genuinely silent on two surfaces that
change *which records a run can read and write*, and the resolution owes amendments to
`Spec_Memory_Substrate_v1.md` (C-MEM-03 / C-MEM-11-or-03 / C-MEM-13 / C-MEM-14). No `design-substrate/**`
file is edited by this filing; the spec-leg is a separate follow-on arc per the B-33/B-59/B-70/B-72
precedent. `B-86` flips `registered_finding` → `design_substrate_gated` with this filing (the B-70
discriminator: a real gap that needs spec-level CONTRACT text before code).

This filing was produced by a three-leg decorrelated pass on 2026-07-28: (i) an Opus grounding agent
(direct code/spec read, file:line evidence), (ii) a transcript-aware `advisor()` pass (GO + 4 adjustments),
(iii) a genuinely-convened council deliberation — C10 + C3 co-primary, C6 consultant (expansion beyond
dyadic justified by a distinct third concern: fallback-chain semantics), C4/C2/C7/C11 handled-by-reference.
The council record is reproduced in condensed form at §4; recommendations at §5.

## §1 The defect, confirmed at HEAD `f79dbe85`

On the memory-substrate SERVABLE standard-tools path, a cross-family fallback serves the chain PRIMARY's
memory scope to a different-family candidate:

- `record_scope.provider_family` derives from `fallback_chain.primary.family`
  (`harness-runtime/src/harness_runtime/automatic_memory.py:197`) while access-mode/tool selection
  re-picks from the CANDIDATE's capabilities (`automatic_memory.py:206-209`;
  `harness-cp/src/harness_cp/memory_access_mode.py:370-374` — identity tracks the candidate, family tracks
  the primary, disagreeing by construction on a cross-family fallback).
- The injected tool schemas bind `scope_ref` — a hash of the FULL 7-field `MemoryScope`
  (`memory_context.py:576-579`) — as a single-member enum
  (`lifecycle/llm_dispatch.py:3754` / `:4223`, `_bind_schema_fixed_value`), so the candidate can
  `memory.search` across, and `memory.write_note` INTO, a scope belonging to a different provider family —
  read disclosure AND durable write attribution.
- The executor-side `scope_ref` check (`llm_dispatch.py:3636-3641`) is a **transcription check, not a
  policy check**: the harness hands the model the token, then verifies the model returned the token it was
  handed. The candidate is never authorized against the scope.
- `provider_family` is a real enforcement boundary, not descriptive: three read-side sites filter on it
  (`harness-is/src/harness_is/memory_retrieval.py:371-384`, `memory_retrieval_index.py:379-396`,
  `memory_policy.py:336-359`).

Pre-existing since U-MEM-16/B-82; deliberately scoped out of the B-83 arc as a C-MEM-11/13 scope-semantics
decision.

## §2 The spec silence (Class 1 trigger), byte-grounded

`design-substrate/Spec_Memory_Substrate_v1.md`:

- **C-MEM-03 (`:100-108`)** declares `provider_family: string | null` with **no value domain** — the spec
  never states whether the field carries a `ProviderFamily` value or a provider key, and never states which
  binding sources it. (`provider_family` occurs exactly twice in the 669-line spec: `:104` and `:481` —
  council Probe A; the silence is total, not partial.)
- **C-MEM-11 (`:346-395`)** carries `provider` (`:358`) and `scope` (`:361`) as **independent** request
  fields — two slots for two facts (the dispatch fact and the partition fact), never bound to each other.
- **C-MEM-13 (`:431-463`)** lists *"fallback-chain primary"* (`:449`, grouped under "Runtime provider
  route") and *"Record scope."* (`:454`) as **separate** selection inputs.
- **Threat model (`:481`)**: *"Retrieval and injection enforce project, workflow, tenant, provider-family,
  CLI-profile, and visibility scope before ranking."* — mandates that the boundary be enforced **without
  saying what it is keyed to**. B-86 is therefore a **failure to honor a cleared invariant**, not a request
  for a new one (this keeps the spec-leg an in-scope conformance repair, X-AL-3-clean).

## §3 Decisive probe findings

- **Probe E (council; the dissolving finding).** The codebase already contains BOTH candidate answers on
  the two halves of one partition: the **writer is already candidate-derived** — the capture path
  constructs its own `MemoryScope` with `provider_family=provider`, the raw per-turn dispatched provider
  KEY (`harness-runtime/src/harness_runtime/memory_capture.py:585-591`) — while the **reader is
  primary-derived** (`automatic_memory.py:197`). The disclosure occurs anyway: its actual carrier is the
  **unconditional `scope_ref` binding** at the injection site, which fires on every servable dispatch with
  no family predicate. Re-keying the scope would suppress the leak only as a side effect of shattering the
  partition.
- **Key-vs-value producer asymmetry (grounding agent; registered as `B-89`).** Written records carry raw
  provider KEYS (`claude_code`/`codex`/`gemini`/`antigravity`/`ollama` do not coincide with any
  `ProviderFamily` value; `anthropic`/`openai`/`google` coincide by accident) while retrieval requests
  carry family VALUES; all three enforcement sites compare raw strings with no normalization. Empirically
  confirmed: an `ollama`-written note is invisible even to a `local_open_weight`-scoped request **of its
  own family**. So today, "memory continuity" under primary-derived keying is largely notional —
  tool-written notes are write-only for 5 of 8 registered provider keys. The continuity side of the tension
  only becomes real after `B-89` lands.
- **Probe C (council).** `None` is already a first-class wildcard in the enforcement predicate
  (`_scope_mismatch` skips a `None` on either side) — undocumented, load-bearing, and the mechanism behind
  the adjacent `B-90` tenant finding (§6).
- **Probe D (council).** `ADR-D5.md:377` already names *cross-family active* as a cross-trust-boundary
  condition that tightens posture — the withhold recommendation is corpus-consistency, not a new
  commitment.
- **B-83 precedent (P3).** The shipped packet-path disposition withholds a *read-only rendered packet*
  cross-family and reports with a named denial reason (`llm_dispatch.py:2358-2370`). The tools path is
  strictly more dangerous (live search + durable attributed write + echoed authorization token); serving it
  while withholding static text is an inconsistency B-83's own rationale forecloses.
- **Hash-inertness (P5).** `MemoryScope` is hash-inert for `memory_id` (content-hash + run_id only,
  `memory_capture.py:574-575`) — a writer normalization moves no identities; migration is forward-only
  (pre-normalization raw-key records stay invisible under family-value requests: no regression, permanent
  residual).

## §4 Council record (condensed; convened 2026-07-28)

**Voices:** C10 (action-safety/blast-radius) + C3 (state/memory/persistence) co-primary; C6 (model
routing) consultant. Deliberated on the **post-B-89 counterfactual** (continuity real, not today's broken
state) per the advisor's framing adjustment.

- **C10:** `memory.write_note` classifies `write-bounded-irreversible` (durable, primary-attributed,
  supersession non-deleting, promotion-eligible → the `:472` cross-run prompt-injection-persistence threat
  runs directly through it). The `scope_ref` echo-check is transcription, not authorization. **But the
  defect is in the absent gate at the dispatch boundary, not in the scope's key** — C10 does not insist on
  candidate keying; re-keying would be the right outcome by the wrong mechanism.
- **C3:** `MemoryScope` is composed once at run start from run-level facts; per-dispatch re-derivation
  makes the run's memory identity non-deterministic within a run and strains C-MEM-11's stable-result
  invariant (`:384`). Candidate keying makes the moment accumulated context matters most (the fallback leg)
  the moment it disappears — silent, permanent, inverted-in-timing data loss. Condition of concurrence on
  Q2: withhold the **model-facing tools only**; harness-authored automatic capture continues (different
  authorship class, crosses no boundary the harness didn't already hold).
- **C6 (refinement adopted):** a fallback chain is a **continuity** abstraction, not a substitution
  abstraction — every other run-level identity is preserved across the boundary; `provider_family` has no
  principled reason to be the exception (the field's name mentioning the provider is a naming coincidence,
  not an architecture). The `scope_ref` currently performs two jobs — naming the run's partition AND
  functioning as the candidate's authorization — and separating them satisfies C10 and C3 simultaneously.
  Stated limit: family equality is necessary but not sufficient (`local_terminal` is *within*-family under
  `local_open_weight` while carrying the slate's most restrictive trust posture).

**TENSION (Q1, C10↔C3): surfaced + probe-resolved** in favor of chain-primary keying, with C10's
requirement satisfied at a different mechanism (the dispatch-side predicate). Neither voice conceded its
axis; the mechanism was the conflation. Not promoted to any T-perm.

## §5 Recommendation (operator holds decision authority)

- **Q1 — key `record_scope.provider_family` to the CHAIN PRIMARY (run-level partition) [HIGH].** Confirm
  `automatic_memory.py:197` as correct-and-canonical; state it in the spec so it stops being an accident.
  Consequence for `B-89`: **the writer adopts the reader's key** — the capture path stops constructing its
  own `MemoryScope` and consumes the run's composed `record_scope` (the larger of the two repairs, correct
  on one-source-of-truth grounds, and it incidentally closes `B-90`).
- **Q2 — WITHHOLD the standard memory tools on a cross-family SERVABLE dispatch [HIGH]**, with C3's
  tools/capture cut as a stated condition: do not inject the memory tool schemas, do not bind `scope_ref`,
  report with a named denial reason (the B-83 disposition shape); **automatic capture unaffected**.
  Withholding is not a gate — nothing routes to an operator, nothing blocks; C10's over-gating failure mode
  is not engaged.

**Interim floor already landed (same PR as this filing):** the scope-boundary family lookup now fails
closed on unregistered provider keys (`provider_family_for_scope_check`, `None` → report-only) — B-86
close-out item (3), pre-cleared by grounding as orthogonal to Q1/Q2.

## §6 What the spec-leg owes (drafting targets, per council)

1. **C-MEM-03** — value domain: `provider_family` carries a `ProviderFamily` **value**
   (`anthropic | openai | google | local_open_weight`), never a provider key; records written with a
   non-value identifier are not retrievable under a family-scoped request; normalization forward-only.
   Plus explicit `null` semantics (unpartitioned-matches-any, not unknown-deny — Probe C is currently
   undocumented load-bearing behavior).
2. **C-MEM-03 or C-MEM-11** — derivation rule: run-level attribute, derived once at run-scope composition
   from the chain primary's family; not re-derived per dispatch; capture writes under the run's composed
   record scope (no independent scope construction).
3. **C-MEM-13** — new invariant: on a `standard_memory_tools` dispatch whose candidate family differs from
   `MemoryScope.provider_family`, the harness MUST NOT expose the memory tool schemas or the scope
   reference; dispatch proceeds without model-facing memory access; withholding recorded with a named
   denial reason; harness-authored capture unaffected. Plus the C6 limit as a stated non-claim (family
   equality necessary, not sufficient; local-terminal posture addressed outside this contract).
4. **C-MEM-14** — qualify the present-tense exposure obligation against the new C-MEM-13 invariant
   (withheld exposure = ledgered outcome, not contract violation; arguably a clarification of the existing
   `:500` "tools cannot bypass scope…" invariant — saying so strengthens the X-AL-3 posture).
5. **Threat model `:481`** — no amendment owed; record that B-86 is conformance repair to a cleared
   invariant.

## §7 Forward items carried by this filing

- **`B-89`** (new row, this PR): producer key-vs-value asymmetry. Existence independent of Q1 (both
  readings leave an `ollama` note invisible to its own family); **direction now determined by §5-Q1**
  (writer adopts the run's `record_scope`); do NOT land ahead of the spec-leg ratification. Hash-inert;
  forward-only migration residual.
- **`B-90`** (new row, this PR): capture-path `MemoryScope` omits `tenant` + `workload_class`
  (`memory_capture.py:585-591`); under wildcard-on-`None` every tool-captured record is
  tenant-unpartitioned at all three enforcement sites (retrieval skips `None`-either-side; policy's
  `_scope_not_broader` guards only non-`None` RECORD values, so a `None` record tenant passes) — against
  `:481`'s tenant mandate. §5-Q1's writer-side repair incidentally closes it; registered on its own merits.
- **C6 within-family `local_terminal` limit** — needs its own pass post-spec-leg (recorded at §6 item 3 as
  a stated non-claim; not a register row yet: no current deployment routes local-terminal on this path —
  re-ground before registering).
- **C3 promotion-eligibility question** (records captured during a cross-family leg under C-MEM-10) —
  flagged, out of B-86 scope, C-MEM-10 policy territory; carried here as a named open question for the
  spec-leg author to restate or discharge.

## §8 Routing

Per root `CLAUDE.md` §4.3: Class 1 → design-phase back-flow. The spec-leg (C-MEM amendments per §6 +
memory-plan delta if unit amendment is owed + clearance markers) opens as a follow-on arc; the impl leg
(Q2 withhold guard + B-89 writer repair + B-90) follows the spec-leg per the B-33/B-59/B-70 precedent. An
out-of-family `just codex-review` decorator on the eventual C-MEM diff is explicitly recommended by the
council (§5b) — the amendment touches a threat-model-adjacent cleared contract.
