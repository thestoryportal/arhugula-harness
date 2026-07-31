# Spec: Control Plane — v1.112 (delta over v1.111)

*Delta-only file. The v1.111 body + the entire C-CP-01 … C-CP-29 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). v1.112 is the CP-owned leg of the RATIFIED **B-69 durable-pause-state read accessor arc** (council record `.harness/council-b69-pause-state-accessor-2026-07-30.md`; **operator ratified OPTION A′ — CO-REQUISITE, SEQUENCED — 2026-07-30**). It carries THREE sections: **§1** the REQUIRED typed response carrier binding accessor-derived responses to their staleness token (an amendment to `ResumeContext`, whose `hitl_responses` field was last substantively defined at `Spec_Control_Plane_v1_106.md` §1); **§2** the NEW public projection-returning surface over the two private resume-tree walks, publishing the four-variant location classification; **§3** the LIFT of two registered scope-limit notes now discharged by the arc. Runtime-owned contract text (the accessor itself, C-RT-36 §31; the refusal-only staleness precondition on `resume()`, §30) lives at the same-arc `Spec_Harness_Runtime_v1.md` v1.107 — cross-referenced, never restated here.*

**Filed:** 2026-07-30
**Authoring authority:** Council record `.harness/council-b69-pause-state-accessor-2026-07-30.md` (genuine three-voice convening C10 + C11 + C9, converged, `CLEAR-TO-COMMIT` at its E4 gate; 4 seams surfaced, 4 resolved, 0 surfaced-unresolved; 20 positions withdrawn/corrected across two reconcile rounds), plus the **operator `AskUserQuestion` ratification 2026-07-30 answering the record's §8.2 scope gate with OPTION A′** (recorded verbatim at the record's §14 addendum). Applied per workspace `CLAUDE.md` §4.3 back-flow + §4.5 clearance discipline.
**Predecessor:** `Spec_Control_Plane_v1_111.md` (v1.111 — a PROSE-ONLY §1.1(d) miscount correction over v1.110; filed 2026-07-27)
**Revision shape:** Delta-only spec file. v1.111 + all earlier file bodies PRESERVED VERBATIM. v1.112 amends `ResumeContext` additively (§1) and adds one new public CP surface (§2); it removes, retypes, reorders and narrows NOTHING. `hitl_responses` / `hitl_response_for` / `effect_fence_resolutions` / `effect_fence_resolution_for` / `hitl_response` / `effect_fence_resolution` keep their v1.106 / v1.107 / v1.66 shapes byte-unchanged. Properties 1–8 of the §1.2 / §1.1 multi-branch invariant families are PRESERVED VERBATIM and are not re-stated here.

---

## §0 Change-note (v1.111 → v1.112)

### §0.1 Revision context — what the arc found, and why CP owes two surfaces rather than none

The `B-69` register row authorizes an **accessor**: a Runtime-owned read letting a `resume_handle` crash-recovery caller learn paused locations' identities before `resume_context` construction. The council found — unanimously, after two of the three voices withdrew contrary claims — that CP owes two surfaces the row did not anticipate, for reasons that are **safety**, not bookkeeping.

**(i) The response carrier (§1).** `resume()` re-derives the *snapshot* from the durable journal on every call, and it is tempting to conclude that this makes any caller-side read untrusted and therefore harmless. That conclusion proves the **snapshot** is re-derived. It does **not** prove the operator's **response map** was composed against the same snapshot. `[HIGH]` **Two different objects; only one is re-derived — and that distinction is the entire finding.** A response map composed against a superseded read, delivered through §1.2 property 4's sole-member carve-out, can land a HITL response on a branch the operator never saw. The mitigation is Runtime's refusal-only precondition (v1.107 §30), but the token it fences on must ride a **CP-owned carrier**, because the responses it binds — `hitl_responses`, `effect_fence_resolutions` — are CP-owned `ResumeContext` fields. A Runtime-side parallel carrier would leave *"these responses came from **this** read"* untyped, and would create a second authority over that fact.

**(ii) The projection surface (§2).** The classification an operator reasons from — gate-owning vs. transitively-paused container (§1.2 property 5, v1.106), never-keyable pre-dispatch identity (§1.1(b), v1.108), effect-fence-abort suppression (property 8, v1.110) — is a **safety classification**, and it lives in the carrier rows CP's private tree-walks visit. If Runtime re-walked the snapshot to build its projection, that classification would have **two authorities that can drift**. The concrete harms: *a projection listing a container branch as addressable invites the operator to key a response the resolver will refuse — livelock; a projection omitting a gate-owning branch the resolver counts leaves it unaddressed — misattribution, the exact property-4 harm.* These semantics have been corrected **three times in six weeks** (property 5 at v1.106, property 6 at v1.108, property 8 at v1.110); a second authority would already have had three opportunities to diverge. `[HIGH]`

### §0.2 The exposure tradeoff needed NO operator gate — stated plainly, so the absence reads as a decision

`B-69`'s register row anticipated the exposure tradeoff (*"exposing partial durable state pre-resume vs. keeping `resume()` a single atomic call"*) as the likely operator question. **It is not one.** The accessor grants a **strict subset** of the authority `resume()` already grants the identical caller with the identical inputs, and the raw `PauseSnapshot` is *already* caller-reachable whenever a resumed run re-pauses. All three council voices converged on this — including, decisively, the voice whose domain would have owned the objection, which declined to manufacture one and named doing so as its own failure mode (over-gating). **The single operator gate this arc did carry was a SCOPE question** (whether B-69's row authorizes amending a *different* already-cleared contract), answered A′ — see §0.3.

### §0.3 The ratified scope + the arc's closure criterion

**Operator ratification, 2026-07-30, verbatim option:** ***(A′) — CO-REQUISITE, SEQUENCED.*** Both surfaces are authorized under **ONE arc gate**, with the closure criterion stated in X-AL-2 conjunctive form:

> **B-69 closes iff *(accessor landed)* ∧ *(staleness precondition landed ∧ exercised by the W3 mutation-probe)*. Partial is non-closure.**

Spec surfaces and impl units MAY land in separate merges within the arc, subject to ONE ordering constraint: **the staleness precondition lands FIRST OR SIMULTANEOUSLY — never after.** No interval may exist in which an unfenced accessor is reachable on `main`. The criterion is recorded **verbatim at the `.harness/forward-register.yaml` `B-69` row's `close_out`**, so it travels with the row rather than living only in a spec paragraph a closing session may not read — *prose sequencing constraints kept anywhere else are precisely the ones dropped at a session handoff.* **Honest limit:** `tools/forward_register.py --check` validates `close_out` presence and a closed row's PR cite; **it does not parse the conjunction and cannot refuse a premature `closed` flip today**, so enforcement is a **pre-merge review obligation on the closing PR** (both conjuncts confirmed, W3 green). Structured per-conjunct fields plus validator support are a `tools/` change outside a doc-only spec leg's scope, registered at the row rather than assumed.

### §0.4 What changed, in one table

| Surface | v1.111 state | v1.112 state |
|---|---|---|
| `ResumeContext` response fields (`hitl_responses`, `effect_fence_resolutions`, `hitl_response`, `effect_fence_resolution`) | Six fields, shapes per v1.106 / v1.107 / v1.66 | **PRESERVED VERBATIM.** §1 adds a REQUIRED provenance carrier ALONGSIDE them; no existing field is removed, retyped, reordered or made optional-to-required |
| `hitl_response_for` / `effect_fence_resolution_for` resolver methods | Per v1.106 §1 / v1.107 §1.1 | **PRESERVED VERBATIM.** §1's carrier does not change what either resolves, only what a resume composed from a read must carry |
| §1.2 properties 1–5; §1.1 properties 6–8 | Per v1.106 / v1.108 / v1.110 / v1.111 | **PRESERVED VERBATIM.** §2 publishes the classification these properties define; it does not amend one of them |
| The two private resume-tree walks | Private; no public sibling returning structure | **§2 NEW** — one public projection-returning surface |
| v1.106 §3's follow-on (a) | Registered, unresolved | **§3 LIFTED** |
| v1.107 §1.1's round-4 `resume_handle` scope-limit note | Registered, NOT-silently-dropped limitation | **§3 LIFTED**, conditionally and precisely |

### §0.5 Cross-axis dispositions

**Runtime AMENDED at the same-arc `Spec_Harness_Runtime_v1.md` v1.107** — NEW §31 C-RT-36 (the accessor + its closed four-variant projection DTO + the five-member cause attribution + the declared postures), the §30 refusal-only staleness precondition, the §30 cause-attribution refinement on the EXISTING `RT-FAIL-RESUME-HANDLE-UNKNOWN` (**no new peer fail class for the attribution**), the discharge of §30's `B-69` scope-limit sentence, and the NEW §14.14.8 append-only/never-truncated substrate invariant on which the token property rests. Runtime-owned text is CROSS-REFERENCED here, never restated. **OD AMENDED at the same-arc `Spec_Operational_Discipline_v1_36.md`** (the trace-emission home for the read + the refusing resume). **IS / AS specs UNCHANGED.** **CXA CLASSIFIED at the same-arc `Cross_Axis_Composition_Document_v2_23.md`** — explicitly determined, not carried forward unexamined (the discipline v1.106 §3 applied to itself): **NO new §2.3 row, aggregate FROZEN at 111**, because `harness-runtime` consuming a CP-published public computation is not a member of the IS/AS/CP/OD 4×4 matrix CXA §2.1 enumerates, and Runtime appears in every forward-capability row (§2.3.8/§2.3.9/§2.3.10) only as a MEDIATOR, never as an endpoint — **but the touch is real, and the PAYLOAD widens materially, from three scalars to a structured sequence, which the CXA statement says rather than assumes away.**

**Plan delta.** `Implementation_Plan_Control_Plane_v2_47.md` amends **U-CP-64** (the `ResumeContext` carrier-owning unit, per its own v2.21 landing precedent and its v2.42 `hitl_responses` amendment) for both §1 and §2. A deferred coverage-matrix row — the instrument v2.43 / v2.44 / v2.46 correctly used for properties whose resolvers do not yet exist — is the **wrong** instrument here: this surface **does** have an owner.

### §0.6 Findings surfaced, NOT patched

- **The `hitl_queue`-vs-pause-journal posture divergence.** The HITL approval queue is durable + TTL-bounded + per-item status + surfaced on next operator-touch; the pause journal is per-workflow latest-record with no TTL, no status, and (before this arc) no enumeration. Unifying tier semantics is a persistence-layer question and is scope creep here. **Constraint carried forward:** §2's projection MUST NOT be shaped to imply the journal *is* the queue.
- **Gate description / question text is absent from every durable pause carrier.** Verified across the full `PauseSnapshot` field set, and symmetrically for a closed-vocabulary HITL-placement-enum substitute: `HITLPlacementKind` exists as a `StrEnum`, but **no durable pause carrier declares a field of that type.** Supplying it is capture-side, hash-affecting, X-AL-3-relevant scope — registered out of this arc, declined for it by the ergonomics voice itself.
- **The pause journal carries no tenant binding.** Runtime §14.8.11 commits a full-strength tenant-composite key + typed cross-tenant refusal for comparable durable state; the pause store is `workflow_id`-keyed. **PRE-EXISTING and not CP-owned** — registered out of this arc (`resume()` reads the same key today; the accessor adds zero tenant exposure), with the boundary stated: fixing it changes the store's KEYING, dragging a capture-side change into a read-only arc.

---

## §1 (NEW at v1.112) — `ResumeContext` response provenance: a REQUIRED typed carrier, non-downgradable

*Amends the `ResumeContext` carrier whose `hitl_responses` field was last substantively defined at `Spec_Control_Plane_v1_106.md` §1, and whose `effect_fence_resolutions` field was last substantively defined at `Spec_Control_Plane_v1_66.md` §1 (unamended by `Spec_Control_Plane_v1_107.md`, which changed only the LINEAR site's consumption of the existing mechanism). Cites to those notes resolve byte-exact at those versions, not at the v1.111 head — the delta chain preserves prior bodies verbatim.*

### §1.1 The contract term

**A `ResumeContext` carrying ANY response value composed from a Runtime C-RT-36 §31 accessor read MUST carry that read's staleness token, non-optionally — the MAP fields and the SCALAR fields alike.**

**The scalar fields are explicitly in scope, and stating "response maps" alone would have left the arc's PRIMARY witness path unfenced.** `[HIGH]` *(Corrected at out-of-family review round 8 [P1].)* A `uniform-fallback-only` location is answered by the **scalar** `hitl_response` / `effect_fence_resolution` field, never by a map entry — and the arc's load-bearing witness **W2 fences exactly that scalar on the 1→1 single-location path**, which is the most common HITL shape at the `solo-developer` tier and the precise case the whole precondition exists for. A map-only reading would have permitted a literal implementation that satisfies §1 while leaving the misattribution W2 reproduces **entirely unfenced** — the mitigation absent from the one path it was built for. **The binding therefore attaches to the ACT of composing from a read, not to which field the response lands in:** `hitl_responses`, `effect_fence_resolutions`, `hitl_response`, and `effect_fence_resolution` are all in scope. The carrier is a **closed two-variant discrimination on the `ResumeContext` itself**:

| Variant | Carries the token | Semantics |
|---|---|---|
| **accessor-derived** | **YES — required, non-optional** | the responses were composed against a specific durable pause-state read; `resume()` fences on the token per Runtime v1.107 §30 |
| **legacy (no-read)** | **NO — the token field does not exist on this variant** | the caller never took an accessor read; **semantically BYTE-IDENTICAL to today's `ResumeContext`** in every observable respect |

### §1.2 The three binding constraints

1. **REQUIRED, not optional — this is the whole point.** An OPTIONAL token would make **omission itself the escape**: `resume()` cannot distinguish *"read the accessor, then omitted the token"* from *"never read"*, so **every accessor user's default path would be unfenced**, and the mitigation would be opt-in for precisely the callers it exists to protect. `[HIGH]` A control that requires an affirmative extra act from every well-intentioned caller is **safe-by-diligence, which is a species of luck** — and the standard this arc holds itself to is *refusable by construction, not safe by luck.* Under the two-variant discrimination, read-then-omitted is **unrepresentable**.
2. **The legacy variant preserves byte-compatibility — and pays that cost better than optionality did**, because the type now RECORDS which path the caller is on instead of inferring it from an absence. Every existing `resume()` caller that has never heard of the accessor constructs the legacy variant and observes today's behavior exactly.
3. **The legacy variant MUST NOT be constructible from an accessor-derived one, and the accessor-derived variant MUST be constructible ONLY from a projection.** No downgrade, no `.without_token()`, no field mutation — **frozen carriers, consistent with `PauseSnapshot`'s own posture** — *and*, symmetrically, the token MUST NOT be constructible, forgeable, or replayable into an accessor-derived context from anything but a C-RT-36 §31 projection object (the projection is the sole capability; a bare string the caller can retype is not). Together these keep Runtime v1.107 §30's no-escape-value rule intact for the path that rule actually governs: **its harm requires the escape to be reachable as a RESPONSE TO A REFUSAL**, and non-downgradability plus projection-only construction make that specific move unrepresentable.

   **The residual, stated precisely rather than left for a reader to discover.** `[HIGH]` A caller who takes an accessor read and then, independently, constructs a **legacy** `ResumeContext` from scratch is **unfenced** — no conversion occurs, so no type discipline can observe the prior read. **The type system cannot track a side effect that happened before construction, and this spec does not pretend otherwise.** This is the precise, stated form of the mitigation's own limit (term 5 of Runtime v1.107 §30: *the precondition NARROWS the supersession window; it does not CLOSE it, and MUST be booked as a mitigation*). What constraints 1–3 do buy, exactly: **read-then-omitted is unrepresentable, so the DEFAULT path of every caller who uses the accessor as designed is fenced**, and no refusal can be answered by downgrading. What they do not buy: protection against a caller who reads and then deliberately builds the no-read carrier. **Closing that would require making the legacy variant unreachable, which would break every existing `resume()` caller — a cost this arc explicitly declines to pay** (constraint 2). A future arc that wishes to close it must deprecate the legacy path, not add a fourth constraint here.

### §1.3 What §1 does NOT do

- It does **NOT** change what `hitl_response_for` or `effect_fence_resolution_for` resolves, nor any membership rule of §1.2 property 4 / §1.1(a)'s unaddressed sets. Those are **PRESERVED VERBATIM**.
- It does **NOT** make fencing mandatory for callers who never read. The legacy variant is a first-class, fully supported path — this contract narrows a supersession window for composed claims; it does not deprecate unfenced resume.
- It does **NOT** name the token's composition. The token is an **opaque value the CP carrier transports**; its required PROPERTY and its impl-discretion composition are Runtime-owned at v1.107 §30 term 1.
- It does **NOT** add a member to any enum, alter `attempt_resume`'s signature (unchanged since v1.16 §26.8.5), or change `PauseSnapshot`, `PausedChildBranchResumeState`, `PreDispatchGateOwningBranchResumeState`, `EffectFencePausedBranchResumeState`, `OrchestratorEffectFencePausedResumeState`, `FanOutResumeState`, or `PeerFanOutResumeState`.

**Carrier shape is implementation discretion; the three constraints are the contract.** Whether the discrimination is expressed as two frozen sibling types, a discriminated-union field, or an equivalent construction is impl discretion — provided (a) the token is non-optional where present, (b) read-then-omitted is unrepresentable, and (c) no construction path produces a legacy variant from an accessor-derived one. **Constraint (c) MUST be witnessed by a detect-then-refuse test, not asserted.**

**One convergence carried forward from the council for the impl leg.** §1's carrier and §2's projection are **discriminated-variant problems on the same two objects**. The discrimination should be authored ONCE, in one idiom, or three ad-hoc shapes will ship.

---

## §2 (NEW at v1.112) — public projection-returning surface over the resume-tree walks

### §2.1 The contract term

**CP publishes ONE public function returning an ORDERED SEQUENCE of TYPED LOCATION PROJECTIONS** over the resume tree of a supplied pause snapshot — the same computation the uniform-fallback resolvers consume, exposed as structure rather than re-derived by the caller. It is a **public sibling to the two private tree-walks** that today collect gate-owning `run_id`s and effect-fence `idempotency_key`s.

**Each projection carries the AUTHORITATIVE CLASSIFICATION plus tree position:**

| Variant | Source carrier | Key field | Semantics |
|---|---|---|---|
| **HITL-addressable** | `PausedChildBranchResumeState` | the paused child's own `run_id` | keys `hitl_responses` (v1.106 §1) |
| **effect-fence-addressable** | **THREE source shapes** — (i) `EffectFencePausedBranchResumeState`; (ii) `OrchestratorEffectFencePausedResumeState`; (iii) **the LINEAR `EffectFenceResumeState`** | `idempotency_key` | keys `effect_fence_resolutions` (v1.107 §1.1) |
| **uniform-fallback-only** | **TWO source shapes** — (i) `PreDispatchGateOwningBranchResumeState`; (ii) **the depth-0 ROOT snapshot's own gate-owning pause** | **NONE — the field is ABSENT** | gate-owning, always unaddressed, resolvable ONLY by the uniform fallback when sole (§1.1(a)+(b), v1.108) |
| **transitively-paused** | container node | **NONE — the field is ABSENT** | not gate-owning, not counted; position only (§1.2 property 5, v1.106) |
**THE EMPTY-`idempotency_key` CRASH-RECONSTRUCTION CARRIER — a FOURTH `effect-fence-addressable` SOURCE SHAPE whose key field is ABSENT, NOT a fifth variant.** `[HIGH]` Fan-out crash reconstruction constructs `EffectFencePausedBranchResumeState(..., idempotency_key="")` — an **intentionally empty** key, with the construction site's own comment stating that resume *"re-pauses with the REAL key (captured off the runtime error) if still ambiguous → a subsequent resume key-binds the operator resolution."* **Both real resume sites consult a fence resolution only when the key is truthy.** Surfacing `""` as a key field would therefore advertise a key the resolver **silently ignores**: an operator response keyed by it is **DROPPED, not refused** — the exact drop-not-refuse livelock §2.2 constraint 2 forecloses for the pre-dispatch identity, arriving through a different door. **The projection MUST carry NO key field on this source shape** — absent, not empty-string, not opaque — and §2.1's source-shape sub-discriminator MUST make that absence unrepresentable-otherwise.

**Why a SOURCE SHAPE and not a fifth variant — a reversal made on the record, not quietly.** `[HIGH]` A draft of this delta declared a fifth variant (`awaiting-fence-reprobe`) for this state, flagged as a deliberate extension beyond the council record's four. **Out-of-family review round 11 [P1] showed that extension BREAKS the one-authority invariant §2.3 exists to protect — the load-bearing safety argument of this entire section.** The empty-key distinction is **not derivable from §1.2 properties 1–5 or §1.1 properties 6–8**: the authoritative effect-fence walk **includes** the empty key, the uniform-fallback computation **counts** it, and only the abort walk filters it. A fifth variant would therefore have required **either a new CP classification rule** (contradicting §2.4's "§2 publishes; it does not decide") **or projection-only logic derived outside the shared computation** — precisely the second authority that can drift. **The source-shape treatment forecloses the same harm at none of that cost:** the classification comes wholly from the existing walk, the variant set stays at the council record's **FOUR**, and the key field is absent by type rather than by convention. *The draft's flag invited exactly this review and got it; the reversal is recorded so the reasoning survives.*

**Why `uniform-fallback-only` carries TWO source shapes, and why enumerating only the first would have been a TOTALITY defect.** `[HIGH]` *(Caught at this delta's out-of-family review round 1 [P1], confirmed against the shipped resolver before applying.)* A **top-level** HITL pause — a LINEAR / `EVALUATOR_OPTIMIZER` / `DECENTRALIZED_HANDOFF` workflow that dispatched directly into its own gate, with no fan-out carrier — is **gate-owning and IS counted**: the gate-owning walk returns the root snapshot's own `run_id` for exactly that shape. But the uniform-fallback resolver treats that same root identity as **unconditionally unaddressed**, for precisely the reason §2.2 constraint 2 gives about pre-dispatch identities: *a depth-0 pause has no child `run_id` to key by; it IS the run.* **Counted, never keyable, and required to be served by the uniform fallback when sole — the definition of this variant.** Enumerating only the pre-dispatch shape would have left the single most common HITL pause in the system with **no truthful variant at all**: omitting it violates §2.2 constraint 3's totality requirement, and rendering it `HITL-addressable` would hand the operator a map key the resolver **silently ignores** rather than refuses. This delta therefore widens the SOURCE column, **not the variant set** — the union remains four, because the semantics were already exactly right.

**Why `effect-fence-addressable` carries THREE source shapes, and why omitting the third would have broken the very lift §3.2 grants.** `[HIGH]` *(Caught at this delta's out-of-family review round 2 [P1], confirmed against the carrier before applying.)* The **LINEAR** effect-fence pause — a single tool step whose fence went ambiguous, with no fan-out carrier anywhere — is carried by `EffectFenceResumeState`, which **already exposes its own `idempotency_key`** and is **already included by the authoritative effect-fence walk**. `Spec_Control_Plane_v1_107.md` §1.1's own round-3 correction made this site **genuinely map-addressable** (*"the map is inert TODAY only because the CONSUME SITE chooses to read the raw field instead of calling the resolver method with that key, not because the carrier lacks the key"*). Enumerating only the branch and orchestrator carriers would therefore have **omitted the most common effect-fence shape**, leaving a `resume_handle` caller unable to construct the `effect_fence_resolutions` map **§3.2's lift explicitly promises them** — a self-defeating gap. **The variant set stays at FOUR; only the source column widens.**

**`EffectFenceResumeState`'s field shape is the narrowest of any source carrier, and the per-variant field rule absorbs that without a special case.** It declares **exactly one field — `idempotency_key`** (`extra="forbid"`, frozen): **no `step_id`, no `branch_index`, no `step_kind`.** Its projection therefore carries the key plus `pause_reason` plus the **root snapshot's own `step_index`** (which is the paused step, since a LINEAR fence pause *is* the run) and nothing else. This is not an exception to the per-variant rule below — it is that rule working: **each source shape declares the fields its carrier actually has.**

**Field declaration is PER SOURCE SHAPE, not per variant — and the variants now span SEVEN-PLUS source shapes, so this distinction is load-bearing rather than pedantic.** `[HIGH]` *(Sharpened at out-of-family review round 4 [P1], which found the earlier "per variant" phrasing no longer sufficient once two variants gained additional source shapes with different field sets.)* Every projection carries `pause_reason` (the **SIX**-member domain including `EFFECT_FENCE_AMBIGUOUS`) and `step_index`. Beyond that, `step_id` / `branch_index` / `step_kind` are carried **only where the specific SOURCE SHAPE declares them**:

| Variant | Source shape | `step_kind` | Key field |
|---|---|---|---|
| HITL-addressable | `PausedChildBranchResumeState` | **absent** | child `run_id` |
| effect-fence-addressable | `EffectFencePausedBranchResumeState` | present | `idempotency_key` |
| effect-fence-addressable | `OrchestratorEffectFencePausedResumeState` | present | `idempotency_key` |
| effect-fence-addressable | **LINEAR `EffectFenceResumeState`** | **absent** (the carrier declares exactly ONE field) | `idempotency_key` |
| uniform-fallback-only | `PreDispatchGateOwningBranchResumeState` | present | **absent** |
| uniform-fallback-only | **depth-0 ROOT gate-owning pause** | **absent** | **absent** |
| transitively-paused | container node | **absent** | **absent** |

**Consequence for the type contract: a variant spanning more than one source shape MUST carry a SOURCE-SHAPE SUB-DISCRIMINATOR**, so that a field absent on one shape is *unrepresentable* on that shape rather than merely optional. `[HIGH]` Modelling `step_kind` as an optional field on a single flat `effect-fence-addressable` type would readmit exactly the defect §2.1's union exists to close — **an illegal state becomes representable** (a `EffectFenceResumeState`-sourced projection carrying a `step_kind` it cannot have, or a branch-sourced one silently missing the `step_kind` it always has). The sub-discriminator is required for `effect-fence-addressable` (3 shapes) and `uniform-fallback-only` (2 shapes); `HITL-addressable` and `transitively-paused` have one shape each and need none. **Its exact spelling is impl discretion; the unrepresentability is the contract term**, and it MUST be witnessed by a detect-then-refuse test, not asserted.

Where a closed-vocabulary field is carried, the projection **DECLARES the domain rather than inheriting `str`** — the source field is closed-vocabulary *by provenance*, not by type, and the difference between a promise and an invariant is the whole point of a closed schema.

### §2.2 Three binding constraints

1. **BARE IDENTIFIER SETS ARE FORBIDDEN as the return shape.** `[HIGH]` A set of identifier strings cannot populate position, step, reason and addressability per location without the caller re-walking the snapshot — the very thing this surface exists to prevent — **and it is worse than merely insufficient: it would carry the ONE value that must not cross the boundary** (constraint 2). The distinction the shape must respect: **one-authority is about the CLASSIFICATION**, and a bare identifier set is exactly what destroys it, because the classification lives in the carrier rows the walk visits.
2. **The never-keyable pre-dispatch internal identity MUST NOT cross this boundary as a VALUE — not opaque, not redacted, ABSENT.** §1.1(b) (v1.108) prohibits keying it; publishing it as a field would make that prohibition a convention rather than a **type invariant**. The foreclosed harm is the worst of the three available: the internal identity is a `run_id`-shaped string, so an operator who keys it hits the resolver's collision defence, which counts that response as *unaddressed* — **the response is silently DROPPED, not refused. Livelock with no diagnostic.**
3. **Enumeration MUST be TOTAL over gate-owning locations.** §1.2 property 4's sole-member rule fires at exactly 1, and the projection's contents are what a downstream operator reasons from when judging whether a uniform response is safe. **Omit pre-dispatch locations and that judgment INVERTS** — the reader concludes "one location, uniform is safe" when the true set has two.

### §2.3 One-authority acceptance criterion — checkable, not prose

> ***The Runtime accessor consuming this surface contains NO recursion over `PauseSnapshot` and reads NO nested resume-carrier field.***

That is the operational form of one-authority. *"Must not re-walk"* as prose is not verifiable; this is. It is carried verbatim as an acceptance criterion at `Implementation_Plan_Control_Plane_v2_47.md` and at `Implementation_Plan_Harness_Runtime_v2_55.md`.

### §2.4 Scope limits on §2

- **§2 publishes; it does not decide.** Every classification rule it exposes is defined by §1.2 properties 1–5 and §1.1 properties 6–8, all **PRESERVED VERBATIM**. §2 adds no rule, changes no membership test, and MUST NOT become a second place where classification semantics are stated.
- **§2 adds NO new cross-axis crossing point.** The surface is consumed by `harness-runtime` at the SAME boundary three sibling public CP computations are already consumed across (the uniform-fallback-eligible run-id computation, the effect-fence uniform-fallback-eligible-key computation, and the effect-fence tree-wide-abort-presence computation). **The touch is real and is named, not assumed away, and the PAYLOAD widens materially — from three scalars to a structured sequence.** *Do not let "no new crossing point" carry weight it cannot.* Classification determination at `Cross_Axis_Composition_Document_v2_23.md`.
- **§2 does not consume `harness_od`, `harness_is` or `harness_as`.** The OD→CP canonical import direction (CXA §2.3.3) is preserved unchanged.

---

## §3 (NEW at v1.112) — two registered scope limits, LIFTED

*Both lifted notes live at PRIOR delta versions, not at the v1.111 head. The delta chain preserves prior bodies verbatim, so a `§`-cite names the version of last substantive definition — stated here explicitly so each lift resolves byte-exact.*

### §3.1 LIFT — `Spec_Control_Plane_v1_106.md` §3's follow-on (a)

**Where it lives:** `Spec_Control_Plane_v1_106.md`, the "Cross-axis dispositions" paragraph, which reads in relevant part *"**Two round-3-registered follow-ons, NEITHER resolved by this spec leg:** (a) a durable-pause-state read accessor design enabling `resume_handle` callers to learn paused children's `run_id`s before `resume_context` construction (§0 scope-limit note) — needed to lift the `resume_handle`-path limitation."*

**Disposition: follow-on (a) is DISCHARGED at v1.112 + Runtime v1.107.** The accessor is designed and scoped at Runtime C-RT-36 §31; CP's own two owed surfaces are §1 and §2 above. **Follow-on (b) is UNTOUCHED and remains open** — it was separately filed as `B-70` and separately resolved at `Spec_Control_Plane_v1_107.md`; nothing in this delta re-opens or re-litigates it.

### §3.2 LIFT — `Spec_Control_Plane_v1_107.md` §1.1's round-4 `resume_handle` scope limit

**Where it lives:** `Spec_Control_Plane_v1_107.md`, the paragraph headed *"Round-4 correction … `resume_handle` scope limit, mirroring `B-69`'s already-registered HITL analogue"*, which states that such a caller *"cannot construct a correctly-keyed `effect_fence_resolutions` map addressing them individually and is limited to the single-pause case."* **Its sibling round-5 note is a DIFFERENT correction** — it fixed the *citation* by widening `B-69`'s own register row to cover both identity kinds — and is **NOT lifted**; it is the reason this delta's §2 publishes effect-fence locations at all.

**Disposition: the round-4 scope limit is LIFTED — conditionally and precisely.** A `resume_handle` caller who takes the C-RT-36 §31 read obtains effect-fence-addressable locations carrying their `idempotency_key`s, and can construct a correctly-keyed `effect_fence_resolutions` map addressing 2+ simultaneously-outstanding locations individually. **Three limits on the lift, each load-bearing:**

1. **It lifts only for a caller who TAKES THE READ.** A `resume_handle` caller who does not remains limited to the single-pause uniform-fallback case exactly as v1.107 states — **that text is PRESERVED VERBATIM as the description of the no-read path.**
2. **It lifts only in conjunction with the staleness precondition** (Runtime v1.107 §30) and §1's required carrier. The read alone is **net-negative** on the path it was built for: it converts a known guess into a believed fact. This is the arc's own X-AL-2 conjunctive closure criterion (§0.3), not a caution.
3. **It lifts the ADDRESSING limitation, not §1.1(a)'s safety rule.** When the unaddressed effect-fence-pause set has 2+ members, every member still MUST re-pause INERT rather than receive the uniform default. §1.1(a) is **PRESERVED VERBATIM**; the lift means a caller can now *avoid* that state by addressing each location, never that the state's handling changed.

**Symmetrically for the HITL analogue.** Runtime v1.107 §30's own `hitl_responses` scope-limit sentence is discharged there under the identical three limits; the two notes are lifted as a pair or not at all, since a heterogeneous pause set returns both kinds from one read.

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Spec_Control_Plane_v1_112.md` |
| Version | v1.112 (delta over v1.111) |
| Predecessor | `Spec_Control_Plane_v1_111.md` |
| Authoring authority | `.harness/council-b69-pause-state-accessor-2026-07-30.md` + operator `AskUserQuestion` ratification 2026-07-30 (OPTION A′) |
| Fork/arc | `B-69` — durable-pause-state read accessor (register row at `.harness/forward-register.yaml`) |
| Co-published artifacts (this arc) | `Spec_Harness_Runtime_v1.md` v1.107; `Spec_Operational_Discipline_v1_36.md`; `Cross_Axis_Composition_Document_v2_23.md`; `Implementation_Plan_Control_Plane_v2_47.md`; `Implementation_Plan_Harness_Runtime_v2_55.md`; six clearance markers; workspace `CLAUDE.md` §2.3/§2.4 pointer bumps; the `B-69` register rows |
| Contract-body change | ADDITIVE only — one `ResumeContext` provenance carrier (§1) + one new public projection surface (§2). ZERO field removed, retyped, reordered or narrowed; ZERO enum member added; `attempt_resume` signature unchanged since v1.16 §26.8.5 |
| Properties 1–8 | **PRESERVED VERBATIM.** §2 publishes their classification; it amends none of them |
| Cross-axis cascade | The §2 surface is consumed by `harness-runtime` at the SAME established boundary three sibling public CP computations already use — **no NEW crossing point, but the touch is real and the payload widens materially (three scalars → a structured sequence)**. Classification determined explicitly at CXA v2.23: no new §2.3 row, aggregate frozen at 111 |
| Impl leg | NOT bundled — code + tests land as a separate follow-on arc per the `B-33`/`B-39`/`B-59`/`B-70`/`B-72` precedent, subject to §0.3's ordering constraint (**precondition first or simultaneous, never after**) |
| Skill discipline | `spec-writer` apply pass — applies the council's converged recommendation + the operator's ratified scope. It decides nothing the record left open; the two `[MODERATE]` residuals the record carried (CP-vs-Runtime carrier home; CXA row-vs-coverage) are resolved here **with the grounding stated** (§0.1(i), §0.5), not silently |
| Date | 2026-07-30 |
