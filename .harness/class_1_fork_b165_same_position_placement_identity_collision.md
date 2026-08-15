# Class 1 Fork — `B-165`: two same-position HITL placements collide onto ONE audit identity, contradicting Runtime spec §14.8.7 NOTE 6-i

**Filed:** 2026-08-14 (`B-165` grounding leg — the step-1 the register row made mandatory)
**Status:** OPEN — Class 1 (architectural defect; design-phase artifact requires revision)
**Halt target:** any future arc that builds on NOTE 6-i's per-placement distinctness claim, or that treats the `B-71` token as separating placements. **Nothing in flight is blocked today** — this is filed at the moment of discovery, not at the moment of obstruction, per `CLAUDE.md` §4.3 ("silent absorption of design-phase defects is the worst failure mode").
**Routing target:** `Spec_Harness_Runtime_v1.md` §14.8.7 NOTE 6-i (the false invariant) — and, only if the operator elects the widen-the-basis reading, `Spec_Control_Plane_v1_119.md` §0.4(2) (the ratified identity basis).
**Detection mode:** execution probe + a 13-function / 16-node witness across three modules, all new this arc. Witnesses at `harness-runtime/tests/test_b165_same_position_placement_identity_witness.py` (the composer half) and `harness-cp/tests/test_b165_production_feed_duplicate_placements.py` (the production-feed half); all 13 test functions (16 parametrized nodes) are PD-8 mutation-proven (13/13 probes kill their test).

---

## §1 — What the register row asked, and what execution answered

`B-165` was registered at the `B-71` spec leg with an **explicitly unverified premise**
and a close-out that made grounding the whole row: *"establish, BY EXECUTION, whether two
same-position placements can both mint an escalation token on ANY venue... UNTIL (a)-(c)
ARE ANSWERED THIS IS NOT A DEFECT."* That caution was earned — a first draft of the row
cited `test_two_pre_action_placements_emit_per_placement_canonical_4_spans` as proof the
shape is live, and round-9 review showed that test constructs the composer WITHOUT
`pause_resume_protocol`/`webhook_delivery_composer`, so it exercises the SYNCHRONOUS loop.

The three questions, answered by running the code:

| Row question | Answer | Witness |
|---|---|---|
| **(a)** does the durable-async `NoReturn` escalation make a second same-position mint unreachable within one pass? | **YES — unreachable.** With TWO same-position placements declared, exactly ONE escalation is entered. | test 5 (POSITIVE control: a counter on the real escalation reads exactly `1`) |
| **(b)** does any OTHER venue mint for more than one placement at a position? | **YES — the SYNC-BLOCKING loop does.** Both placements are gated, both reach the §14.8.2 step-4h audit write. | test 3 (2 surface calls, 2 F2 writes) |
| **(c)** if a duplicate audit write occurs, on which venue and with which key? | **Sync venue; a BYTE-IDENTICAL key, `B-71` token included.** | test 3 pins the exact string; test 6 shows the consequence |

**The premise is CONFIRMED.** Two placements at one position, on one branch, compose one
identity.

### §1.1 The reachability chain, each link witnessed

1. **The declaration is admissible.** `WorkflowManifestEntry` has no validator rejecting
   two same-position placements; a full `model_validate` accepts the pair (test 1).
2. **The fold preserves both.** `fold_step_hitl_placements` forecloses the *override*
   introducing a duplicate position and says so in its own docstring — but explicitly does
   **not** de-duplicate a workflow that itself declares two, calling that *"a
   workflow-validation concern, out of scope here"* (`workflow_driver_types.py:753-756`).
   Link 1 shows that workflow-validation does not exist anywhere, so the disclaimed concern
   has no owner (test 2).
3. **The composer loops over both.** `hitl_gate_composer.py:1972` iterates `matching` in
   declaration order; the APPROVE branch `pass`es and the loop continues to placement 2.
3-bis. **Production DELIVERS that shape.** Driving the REAL `execute_workflow` on a
   `PARALLELIZATION` topology, every branch's `StepExecutionContext` arrives at the step
   dispatcher carrying BOTH declared placements AND a non-`None`
   `pre_dispatch_escalation_basis` — the co-arrival that makes the collision reachable
   rather than hypothetical (`harness-cp/tests/test_b165_production_feed_duplicate_placements.py`).
   This link exists because out-of-family review objected, twice and correctly, that a
   composer-only witness shows the collision *given* the shape without showing that
   production *produces* it.

   *A finding worth keeping from probing that link:* the declared tuple reaches each
   branch by TWO REDUNDANT routes — the fan-out parent seeds it (`workflow_driver.py:8411`)
   and the branch child re-folds it from `manifest_entry` (`:8593`). Deleting either alone
   leaves the other delivering it, so a single-line mutation SURVIVES; only the conjunction
   reds the test. Two annotations naming one line each were written and both proved vacuous
   before this was found.

4. **Both compose the same key.** `compose_hitl_action_id(parent, position, token)` —
   both placements share `parent`, share `position`, and share `token`, because
   `resolve_escalation_instance_id` derives it from the run-scoped branch identity plus
   `placement.position.value` (CP v1.119 §0.4(2)). Nothing in the composition varies per
   declaration.

### §1.2 The observed key

```
hitl:workflow:test:step:0:pre-action:1b6651c6bde3c4c5a7ce1f2130d1107926348fac2146787d32c2a9c033053eaa
```

Emitted **twice**, byte-identical, from one `dispatch` over two declared placements on a
gate-owning fan-out branch (the venue where the token genuinely exists — so this is not the
token-free path the falsified first draft accidentally described).

---

## §2 — The defect proper: NOTE 6-i asserts an invariant the system does not satisfy

`Spec_Harness_Runtime_v1.md:4864`, verbatim:

> **NOTE 6-i — Multi-placement same step at v1.9 MVP (load-bearing future-arc commitment).**
> When `step.hitl_placements` declares multiple placements with overlapping
> `applicable_placements` (e.g., one step declares both `PRE_ACTION` for the action AND
> `SUB_AGENT_BOUNDARY` for a child sub-agent), each placement evaluates independently per
> the §14.8.2 step 4 loop. **Each placement's audit entry uses a distinct `action_id`**
> (action_id includes `placement.position.value` per substep 8b-HITL). **Sibling-
> distinguishability via the IS-anchored `entry_core` is preserved** (each placement's F2
> entry has its own action_id pattern). […]

Two claims, both emphasised above, are **FALSE for the same-position case**:

- *"Each placement's audit entry uses a distinct `action_id`"* — test 3 shows two identical.
- *"Sibling-distinguishability … is preserved"* — test 6 shows the opposite (below).

**The note's own parenthetical is the tell.** It justifies distinctness by *"action_id
includes `placement.position.value`"* — a justification that holds only when the positions
DIFFER, which is exactly the case its example enumerates (`PRE_ACTION` + `SUB_AGENT_BOUNDARY`).
The note generalises from an example whose distinctness is incidental to it, and never
states the precondition it silently relies on.

### §2.1 Why this is not a `B-71` regression

The two-argument key `hitl:{parent}:{position}` already collided for same-position
placements before the `B-71` arc; the token neither introduced nor closed this. Test 4 is
the discriminator that keeps the two facts apart, and it asserts BOTH halves: two peer
BRANCHES at one position receive **different** keys (the aliasing `B-71` genuinely closed),
while two placements within ONE branch receive the **same** key. Reporting only the second
half would read as a `B-71` regression, which the evidence does not support.

**Nor is the shape merely theoretical-but-unbuilt.** It is admissible at every layer that
could have refused it, and one in-tree test has exercised it since v1.11.

### §2.2 What it costs — the consequence, at the real writer

The composed key is used as **both** the CP audit `action_id` **and** the F2 state-ledger
`idempotency_key` (`hitl_gate_composer.py:1740-1758`). `append_ledger_entry`'s dedup is
**key-only** (`state_ledger_write.py:330`), so the second placement's entry returns
`IDEMPOTENT_NOOP` and is **dropped**. Test 6 drives the production function and asserts the
ledger ends with **one** entry after two writes.

The failure is therefore not a noisy duplicate — it is a **silent omission of oversight
evidence**: a second human gate fires, an operator answers it, and no state-ledger record of
that answer exists. For an audit surface whose purpose is to prove a human was consulted,
losing the second consultation is the worse of the two possible failures.

### §2.3 A misreading this arc also corrects

`test_lifecycle_hitl_gate_composer.py` (the v1.11 record) carried:

> `# Note: the v1.11 MVP action_id shape hitl:<parent>:<position> collides across`
> `# same-position placements; per spec §14.8.2 step 4 NOTE 6-i, in-loop sub-shape is`
> `# impl-discretion.`

**NOTE 6-i grants no such discretion.** It *asserts distinctness*. The comment inverted the
spec into a licence, which is plausibly how the collision stayed unexamined from v1.11 until
`B-165`. Corrected in this arc's diff (the test's assertions are unchanged; only the claim
about what the spec says).

---

## §3 — Why this routes to back-flow rather than a Phase-7 fix

Per X-AL-3 / `CLAUDE.md` §4.4, no silent H_T design extension at Phase 7. Every available
repair either contradicts a ratified record or extends one:

| Candidate repair | Why it is not a Phase-7 edit |
|---|---|
| **(A) Narrow NOTE 6-i** — restate the distinctness claim as holding only for placements at DISTINCT positions, and state the same-position collision as a known bound. | Amends a design-substrate spec. Cheapest and most honest; changes no code. |
| **(B) Widen the §0.4(2) basis** — fold a per-declaration ordinal into the hashed material so two same-position placements separate. | Revisits the **ratified** `B-71` identity basis. Also breaks §0.12 byte-identity for the whole linear/validator population unless the ordinal is suppressed at 0 — a real design question, not an implementation detail. |
| **(C) Refuse the shape** — add a workflow-validation rule rejecting two same-position placements. | Foreclosed at C-CP-17 §17.3 (placements are declared per workflow) and would be a new committed invariant. Note the fold's docstring already *names* this owner as existing ("a workflow-validation concern") when it does not — so (C) is really "create the missing validation layer". |

Choosing among (A)/(B)/(C) is an operator/architect decision on a committed surface. **The
recommendation is (A)** — the collision is a genuine bound, not a bug the code got wrong;
(A) makes the spec true at zero blast radius and leaves (B) available if a workflow ever
needs same-position placements distinguished. **(B) should not be taken speculatively**: it
buys separation for a shape no in-tree workflow declares, at the cost of re-opening a
byte-identity criterion that eight review rounds were spent establishing.

---

## §4 — What this arc landed, and what it deliberately did not

**Landed (Phase 7 posture, no design-substrate edit) — at PR #1343, merged 2026-08-14:**
- A 13-function / 16-node witness across THREE modules, pinning the as-built identity so the
  cost is visible and a later fix can re-price it: the composer behaviour
  (`harness-runtime/tests/test_b165_same_position_placement_identity_witness.py`), the
  production feed through the real driver
  (`harness-cp/tests/test_b165_production_feed_duplicate_placements.py`), and the joined
  driver→facade→composer round trip plus the stage-5 wiring assertion
  (`harness-runtime/tests/integration/test_b165_driver_through_composer_round_trip.py`).
- The §2.3 comment correction.

**Landed here (doc-only):** this filing; `B-165`'s register transit
`registered_finding` → `design_substrate_gated`; the owed `--archive-superseded` write; and
`B-176` (the ring-buffer wall-clock flake, third member of the `B-166`/`B-169` class).

**Why the split.** `tools/codex_context_guard.DESIGN_RE` matches `.harness/class_1_fork_*`
and `IMPL_RE` matches the test modules, so a single patch carrying both reports
`HARD DESIGN_IMPL_MIX` — verified by running `stop_gate.py` against a bundled tree, not
assumed. The witness therefore landed first and this filing cites it, so the register never
points at an unlanded artifact at any commit.

**Deliberately NOT done:** any edit to `Spec_Harness_Runtime_v1.md` or
`Spec_Control_Plane_v1_119.md`. The register row anticipated exactly this outcome —
*"the honest outcome may be a fork filing rather than code"* — and it is the outcome.

### §4.1 What the witness does and does not reach — stated rather than hidden

Most tests use mock ledger/audit writers, which record every call. Three do not, and the
distinction matters when quoting them: the dedup-drop test drives the REAL
`append_ledger_entry` (so it, and only it, shows the second entry does not PERSIST); the
production-feed tests drive the REAL `execute_workflow`; and the round trip drives the real
driver through a real `RuntimeHITLGateComposer` behind the real `SyncDispatcherFacade`. A
mock-writer test's "two writes" is a statement about what the COMPOSER EMITS, never about
what persists — the two must not be quoted as one result.

**One step is genuinely unreachable, with its mechanism:** driving a gate through the
UNMODIFIED stage-5 registry. Stage 5 binds the MCP-backed elicitation surface
(`stage_5_loop_init.py:243`), which no automated test can answer, and doubling it would
replace the very component whose installation is under test. The regression that matters —
stage 5 ceasing to install a PRE_ACTION-accepting composer — is therefore closed at its own
layer by an assertion on the real `run_bootstrap`-produced `ctx.step_dispatchers`.

### §4.2 A process finding worth more than the defect

Seven annotation failures surfaced while building this witness, and the seventh was the
grader. SIX `# mutation-probe:` annotations named a plausible production site the test could
not actually detect: the placement fold (the real carrier was inheritance); a single carrier
line (TWO redundant carriers exist — `workflow_driver.py:8411` seeds and `:8593` re-folds, so
only the conjunction reds); the §14.8.2 step-4h audit write (on READ_ONLY the gate SKIPS 4h
entirely and writes via the auto-approve branch at `:2091`); a production site for a test that
hand-builds its own context; a composer TYPE without its `applicable_placements`; and one
masked by the test's own `model_copy`. Every one looked rigorous.

The seventh: the probe driver counted a **SyntaxError-induced pytest COLLECTION failure as a
KILL** — indistinguishable from genuine detection at the exit-code level, and it had been
manufacturing a passing grade. After teaching the driver to `compile()` each mutated file and
REFUSE, 12 of 13 probes were genuine all along and exactly one was the artifact.

**The generalisable rule: a probe reporting KILLED is a claim requiring the same scrutiny as
the test it grades.** Reading the code forms the hypothesis; running the probe tests it;
checking that it failed for the RIGHT REASON is what makes the result trustworthy.

---

## §5 — Filing footer

| Field | Value |
|---|---|
| Fork class | Class 1 (architectural defect; design-phase artifact requires revision) |
| Register row | `B-165` (`.harness/forward-register.yaml`; prose at `.harness/post-phase-8-forward-register.md`) |
| Witnesses | `harness-runtime/.../test_b165_same_position_placement_identity_witness.py` + `harness-cp/.../test_b165_production_feed_duplicate_placements.py` + `harness-runtime/tests/integration/test_b165_driver_through_composer_round_trip.py` (13 functions / 16 nodes, 13/13 mutation-proven) |
| Primary routing target | `Spec_Harness_Runtime_v1.md` §14.8.7 NOTE 6-i |
| Conditional routing target | `Spec_Control_Plane_v1_119.md` §0.4(2) — only under reading (B) |
| Recommendation | (A) narrow NOTE 6-i; do not widen the ratified basis speculatively |
| Decision owner | operator (committed-surface amendment) |
