# Implementation Plan: Control Plane — v2.53 (delta over v2.52)

*v2.53 absorbs the `B-71` spec leg (CP spec v1.119, Runtime spec v1.121) into the plan's
execution authority by adding **ONE new unit, U-CP-102**, carrying the five additive
carrier amendments and the persist/read/write wiring the spec's persist-once contract requires.
NO landed unit's body is amended — the B-97(a)/B-118 new-unit precedent, the same shape
v2.52 used for its supersession notes: new obligations ride a new unit, landed criteria
stand as HISTORY. Every existing unit body, signature block, rollback boundary, cluster
assignment and all other plan content are PRESERVED VERBATIM. No contract number is
minted (the spec leg mints none); no existing field changes type.*

**Status:** Proposed

## §0 Change-note (v2.52 → v2.53)

### §0.1 Why a new unit rather than criteria on the landed carriers

The five amendment sites live on carriers whose units are long landed (`HITLEscalationBrief`
at the C-CP-28 §25.2 lineage; `StepExecutionContext` at C-CP-25, twice; the per-branch
pre-dispatch gate-owning resume state at C-CP-26; the pause-location projection at C-CP-21). Amending those units' acceptance
criteria in place would rewrite history that was verified against a different contract —
the precise failure v2.52 §0.2 avoided by riding supersession as a note. It would also
scatter one mechanism across four units whose landings cannot be sequenced relative to
each other.

`B-71` is **one mechanism**: a token that is minted once, folded once, persisted once and
read back before recompute, and projected so an operator can match it. Its five carriers are
jointly meaningless — a basis field with no minter, an echo with no writer or no reader, or
a projection with no token each satisfy nothing. U-CP-102 therefore owns the whole CP-side
surface, and the seam to the Runtime minter is a co-land pin rather than a shared unit.

### §0.2 U-CP-102 (NEW) — `B-71` branch-distinct escalation correlation carriers

| | |
|---|---|
| **Unit** | U-CP-102 |
| **Cluster** | C-CP-28 escalation-carrier cluster (the `HITLEscalationBrief` owner), with declared reach into C-CP-21, C-CP-25 and C-CP-26 carriers per §0.3 |
| **Spec authority** | `Spec_Control_Plane_v1_119.md` §0.3 / §0.4 / §0.4.1 / §0.4.2 / §0.4.3 / §0.4.4 / §0.5 / §0.6 / §0.7 / §0.12 |
| **Depends on** | the landed C-CP-21 / C-CP-25 / C-CP-26 / C-CP-28 carriers. **NO dependency on U-RT-155** — see the co-land pin at §0.4 |
| **Co-land pin** | **U-RT-155** (Runtime plan v2.63). A PIN, not a DAG edge — see §0.4 |
| **Level** | terminal within its cluster; introduces no new DAG node upstream of any landed unit |

**Files — the five carrier declarations AND the CP-side wiring its own criteria require.**
A first draft of this line said "declarations, and nothing else", which out-of-family review
showed contradicts the unit's own acceptance criteria: AC 11 changes **both**
`workflow_driver.py` snapshot builders (the mint-to-snapshot write and the carried-forward
preservation), AC 13 populates the pause-state projection, and AC 14 sanitizes the
validator-supplied brief at the CP acceptance seam. Scoping the unit to declarations alone
would permit an implementation that declares five fields and never persists, projects or
sanitizes the token — every criterion unowned by any file. Those wiring sites are in scope.

What is NOT in scope: the Runtime-owned minter, the `compose_hitl_action_id` fold, and the
`payload_body` **emission** — they are U-RT-155's, per Runtime spec v1.121. The emitter is
`project_brief_to_payload`, which is Runtime-owned, so assigning the keys to both units
would give two units overlapping ownership of one surface and make their completion
evidence ambiguous. **U-CP-102 owns the VALUES the keys carry** (the contract at spec §0.6 —
which vocabulary, what each key may and may not say); **U-RT-155 owns their EMISSION**
(AC 9).

**Acceptance criteria.**

1. `HITLEscalationBrief` carries `escalation_instance_id: str | None = None` exactly as
   canonically read at spec §0.3's `§25.2.Z` body, with v1.19's `fail_detail_hash: str | None`
   widening carried forward — a witness pins BOTH, so the v1.18-composition regression that
   out-of-family review caught on the draft cannot recur silently.
2. `StepExecutionContext` carries `pre_dispatch_escalation_basis: str | None = None`
   (spec §0.4.1 / `§25.20`, **pre-hash**) and `pre_dispatch_escalation_instance_id: str | None = None`
   (spec §0.4.3 / `§25.21`, **post-hash**). A witness asserts both are `model_copy`-inherited
   and that a branch child never re-derives either.

   **`pre_dispatch_escalation_basis` is derived UNCONDITIONALLY at BOTH composition sites**
   (`workflow_driver.py:8410-8418` and `:12746-12754`), NOT inside the existing
   `_recovered_pre_dispatch_gate_owning and resume_context is not None` guard. Witnessed on a
   **first, non-resume** fan-out escalation: the basis is non-`None` and a token is minted.
   Without this the whole mechanism is inert on exactly the path `B-71` exists to fix — the
   guard means the identity is not computed at all on a first escalation — and every other
   criterion could pass while two peers still collided.
3. The per-branch pre-dispatch gate-owning resume state carries
   `escalation_instance_id: str | None = None` (spec §0.4.2 / `§26.9`), keyed per branch
   entry by the existing `branch_index` within its containing snapshot. A witness asserts
   no tree-wide index is introduced.
4. **Read order (spec §0.4.3), witnessed as three arms, not asserted as prose.** Echo
   non-`None` → used verbatim, recompute NOT invoked; echo `None` and basis non-`None` →
   computed per §0.4(2); both `None` → brief field stays `None`. The recompute-not-invoked
   arm is the one a passing test can most easily fake, so it is witnessed by observing that
   the compute path is not entered, not merely that the output matches.
5. **A persisted echo is never compared against a recompute** (spec §0.4.3 arm 1). A
   witness drives a resume whose recompute would differ and asserts the run does not fail.
6. **Digest conformance is pinned to the spec's exact formula** (§0.4(2)): domain separator
   `"hitl-escalation-instance:"`, the pre-dispatch identity
   `f"{snapshot_run_id}:pre-dispatch-gate:{branch_index}"`, `":"`, the enum's string VALUE,
   sha256, lowercase hex, 64 chars, never truncated, UTF-8 throughout. A witness asserts a
   known-input → known-digest vector, so an encoding or separator drift reddens.
7. **The leak bar is witnessed structurally, not by inspection** (spec §0.5): no
   `snapshot_run_id`, no un-hashed pre-dispatch identity, no `run_id`-shaped string and no
   raw basis material appears in any operator-facing or exported field of the brief —
   including `branch_context`, whose scoped carve-out covers the branch **ordinal in prose**
   and nothing else. A negative witness asserts the ordinal is absent as any typed/parseable
   field and absent from every exported span attribute.
8. **The CP-side CONTRACT for the four additive `payload_body` keys** (`escalation_instance_id`
   — the BARE token, which is what makes the webhook equality-matchable against criterion 13's
   projection — plus `branch_context`, `resolvability`, `resolvability_note`) holds per spec
   §0.6. **Emission is U-RT-155 AC 9's, not this unit's** — this criterion witnesses that the
   source values exist and obey their vocabularies, with `resolvability` drawn from the closed
   `PauseLocationVariant` vocabulary (`Spec_Control_Plane_v1_112.md` §2.1) and no new
   vocabulary minted. `proposed_response_palette` is **preserved and still projected**
   (spec §0.6.1 — the earlier suppression binding is WITHDRAWN and MUST NOT be implemented).
9. **Ingress is one-way** (spec §0.7): no resume surface is keyed by the token; a submitted
   value that matches is counted-as-unaddressed. That half is witnessed as normative. The
   **diagnosis** is advisory until the typed carrier lands and is NOT witnessed as a typed
   disposition — `ResumeResult` / `RunResult` are closed schemas and requiring one here
   would make the unit unimplementable.
10. **Byte-identity on the untouched population** (spec §0.12): on the linear/validator
    path the field is `None`, the four keys are absent, and the wire body, ledger key and
    audit `action_id` are byte-identical to pre-arc. Witnessed by comparison against a
    pre-arc fixture, not by asserting the absence of a key.
11. **The minted token is WRITTEN to the echo** (spec §0.4.2 WRITER row): the
    pause-signal / snapshot producer copies the token from the brief into the per-branch
    entry. Witnessed end-to-end — escalate, then read the snapshot and assert the echo
    equals the delivered token. **Without this criterion the field is declared and never
    populated**, every resume takes the recompute arm, and criterion 4's echo arm is
    unreachable in production even though its unit test passes. **The witness also covers
    the CARRIED-FORWARD path at BOTH snapshot builders** (`workflow_driver.py:10442-10461`
    and `:14810-14829`): a warm-up-withheld gate-owning branch is reconstructed with no new
    brief, and its row MUST carry the prior token forward rather than default to `None` —
    otherwise a resume recomputes and can rotate the key of an escalation the operator is
    still holding. Witnessing only mint-to-first-snapshot would miss this entirely.
12. **Legacy durable snapshots still resume after upgrade** (spec §0.4.2 compatibility
    clause): the field is DROPPED from the serialized form when `None`, mirroring
    `_strip_default_fanout_resume_fields`'s existing treatment of `hitl_gate_config_hash`.
    Witnessed against a snapshot captured **before** the field existed: it must resume, and
    its recomputed hash must be unchanged. Asserting only that new snapshots round-trip
    would miss this entirely — the failure is that a legitimate pre-upgrade snapshot is
    rejected as corrupt.
13. **The public projection carries the token** (spec §0.4.4 / `§2.2.A`):
    `PreDispatchUniformFallbackOnlyLocation` exposes `escalation_instance_id` read-only,
    equal to the value delivered on the webhook and persisted at §26.9 — one value, three
    surfaces. Witnessed by asserting all three agree for one escalation, which is the
    property that makes the correlation loop closeable at all. `v1.112` §2.2 constraint 2
    still holds: the internal identity never appears here.
14. **The validator trust seam overwrites, not merely ignores** (spec §0.4(3)): a
    validator-supplied `ValidatorResult.escalation_brief` carrying a non-`None`
    `escalation_instance_id` has that value replaced with the harness-minted value (or
    `None`) at the acceptance point, before the brief reaches any composer, key or exported
    carrier. Witnessed with a hostile value: it must appear in **no** payload, key or span.
    Ignoring without overwriting still ships the operator's value on the wire.

15. **The public projection OMITS the field when `None`** (spec §0.4.4 absence row): a
    pause view derived from an already-durable snapshot serializes NO
    `escalation_instance_id` key at all, not `null`. Witnessed against a pre-field
    snapshot's projected bytes. Criterion 13 checks value agreement and leakage, and
    criterion 12 covers the RESUME-STATE hash — neither covers the projection's wire
    shape, so without this an implementation satisfies every other criterion while
    breaking the legacy projection bytes the spec promises.

**Mutation-probe obligations (Workflow v1.19 PD-9).** Criteria 4, 6, 7, 10, 11, 12, 14 and 15
each carry a `# mutation-probe:` annotation: invert the read order; perturb the digest
formula by one byte of the domain separator; project the un-hashed identity onto
`branch_context`; emit the field on the linear path; drop the minter→snapshot write; emit
the field when `None` instead of dropping it; honour the validator-supplied value; and
emit the projection field as `null` instead of omitting it — each must redden its own
witness and no other.

### §0.3 Cross-carrier reach, declared rather than implied

U-CP-102 declares fields on carriers owned by C-CP-21 (the pause-location projection at
AC 13), C-CP-25 (twice) and C-CP-26 while sitting in the C-CP-28 cluster. This is **declared reach**, and it is stated here because an undeclared
one is how a plan acquires a hidden coupling edge. It introduces **no new dependency edge
into any landed unit** — the amendments are additive and `None`-defaulted, so no landed
unit's acceptance is invalidated and no landed unit must re-run to remain true.

### §0.4 The Runtime relationship — a CO-LAND PIN, not a mutual dependency

U-CP-102 declares the carriers; **U-RT-155** mints into them, folds the token into
`compose_hitl_action_id`, and projects the webhook keys. Neither is independently
observable: carriers with no minter are `None` forever, and a minter with no carriers has
nothing to write.

**That mutual need is expressed as a co-land PIN, and deliberately not as a pair of DAG
dependencies.** A first draft of this delta declared U-CP-102 → U-RT-155 *and*
U-RT-155 → U-CP-102, which is a two-node **cycle** with no valid topological level and
contradicts the acyclic scheduling invariant the axis plans hold (`harness-cp/CLAUDE.md`
§1.1). Out-of-family review caught it. The correct shape is the one the workspace already
uses for same-arc requirements — a **one-way carrier dependency plus a co-land pin**, the
precedent CP plan v2.40 set with its "witness (d) co-land pin at Runtime plan v2.51
U-RT-145":

- **DAG edge:** U-RT-155 depends on U-CP-102 (the writer depends on the carriers). One
  direction only, so the graph stays acyclic and U-CP-102 keeps a valid level.
- **Co-land pin:** U-CP-102 MUST NOT be closed in an arc that does not also land
  U-RT-155. This is a *scheduling* constraint, not a dependency — it does not participate
  in the topological sort.

Recorded as a plan-level fact so a future session cannot land one alone and read a green
carrier suite as evidence the mechanism works.

### §0.5 What this delta is NOT

NOT the impl leg — this delta assigns the work; the code lands at U-CP-102 / U-RT-155.
NOT a contract-number mint (the spec leg mints none). NOT an amendment to any landed unit
body. NOT an OD / IS / AS / CXA / ADR / ADD / PRD change. NOT the registered follow-ons at
spec §0.9 — the uniform-response target selector; redelivery on posture change;
uniform-treatment extension to depth-0 root and already-dispatched children; the pause-view
**addressing** half (the correlation half IS in scope, at AC 13); the unguarded
`entry_version` carrier across the pause boundary; the typed resume-outcome diagnostics
carrier; and **register row `B-165`**, the duplicate same-position placement collision, which
needs a design-record revisit of the ratified identity basis rather than a spec leg. **Seven**
items; each owes its own leg and none is in scope here.
