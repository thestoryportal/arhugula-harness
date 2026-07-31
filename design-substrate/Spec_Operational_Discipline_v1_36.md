# Spec: Operational Discipline — v1.36 (delta over v1.35)

*Delta-only file. The v1.35 body + the entire C-OD-01 … C-OD-30 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta carries exactly ONE section — a NEW subsection under C-OD-30 declaring the observability home for the two events the RATIFIED **B-69 durable-pause-state read accessor arc** rules REQUIRED: (i) the C-RT-36 §31 accessor read, and (ii) a `resume()` refused on the §30 staleness precondition. CP-owned contract text (the `ResumeContext` provenance carrier + the projection-returning surface) lives at the same-arc `Spec_Control_Plane_v1_112.md`; Runtime-owned contract text (the accessor, the precondition, the cause-attribution vocabulary) lives at the same-arc `Spec_Harness_Runtime_v1.md` v1.107 — both cross-referenced here, never restated.*

**Filed:** 2026-07-30
**Authoring authority:** Council record `.harness/council-b69-pause-state-accessor-2026-07-30.md` (§6.5 rules the trace emission **REQUIRED**, declared by three voices; §9 row 5b assigns OD the namespace determination), plus the **operator `AskUserQuestion` ratification 2026-07-30 — OPTION A′**. Applied per workspace `CLAUDE.md` §4.3 back-flow + §4.5 clearance discipline.
**Predecessor:** `Spec_Operational_Discipline_v1_35.md` (v1.35 — the B-33 arc's OD leg, NEW §24.8; cleared 2026-07-23)
**Revision shape:** Delta-only spec file per the OD delta-only convention. v1.35 + all earlier file bodies PRESERVED VERBATIM. v1.36 carries this change-note + exactly ONE section: NEW §30.5 (C-OD-30). **§C-OD-30.1–§C-OD-30.4 are PRESERVED VERBATIM** — this delta ADDS a sibling declaration within the same namespace family; it does not amend, narrow, or re-shape `PauseResumeAuditPayload` or either of its two existing projection helpers.

---

## Change-note (v1.35 → v1.36)

### Why OD owes a section at all — and why the answer is *partly* "it already rides"

`[HIGH]` The council ruled the emission REQUIRED and **explicitly left the namespace determination to OD** — new namespace vs. existing coverage — mirroring the same row-vs-coverage discipline it applied to the CXA classification. Grounding that determination at filing time produced a **split** answer, which is why this delta exists rather than a bare "it rides existing" sentence in a sibling spec's change-note:

- **The refusing `resume()` rides the existing NAMESPACE, but NOT the existing payload or producer path.** It belongs in C-OD-30's `resume.*` half — that much is right, and it is why no new namespace is minted. But it is raised **PRE-BOOTSTRAP**, before any `(ResumeAttempt, ResumeOutcome)` pair exists, so it does **not** compose through the existing §C-OD-30.4 projection helper and does **not** route through the CP→OD converter's `resume:` branch; and `PauseResumeAuditPayload` is `frozen` + `extra="forbid"` with **no staleness-token field**, so the token cannot ride it unchanged. **§30.5.2 therefore authorizes an additive carrier** (an additive field, or a sibling payload type — impl discretion). *An earlier draft of this delta asserted "no new payload type and no new converter branch are owed"; out-of-family review round 2 [P1] found both halves false, and the claim is corrected in place rather than quietly repaired.*
- **The accessor READ does NOT ride existing structure.** It is neither a `PauseEvent` nor a `(ResumeAttempt, ResumeOutcome)` pair — it is a **third event class** in the pause/resume lifecycle: a caller-facing read that neither pauses nor resumes anything. The existing `PauseResumeAuditPayload` composition has no shape for it, and silently forcing it into one of the two existing shapes would misdescribe it in the audit record. **A declaration is owed.**

Declaring only the half that fits, and leaving the other half to be improvised at the impl leg, is the omission this section closes. **"Named as owed" inside a Runtime or CP change-note does not discharge an OD obligation** — the per-axis spec is the artifact an impl leg works from.

### The determination, stated

> **The B-69 read and the B-69 staleness refusal BOTH emit within the EXISTING C-OD-30 `pause.*` / `resume.*` namespace family. NO new top-level namespace is minted, and the C-OD-05 §5.1 namespace roster is UNCHANGED.** **Both are NEW event kinds within that existing family, and NEITHER is representable by the existing payload composition unchanged.** The read is neither a `PauseEvent` nor a `(ResumeAttempt, ResumeOutcome)` pair. The refusal is raised **PRE-BOOTSTRAP, before any `ResumeOutcome` exists**, so it composes through neither existing §C-OD-30.4 helper nor the CP→OD converter's `resume:` branch — and `PauseResumeAuditPayload` is `frozen` + `extra="forbid"` with no staleness-token field. **§30.5.2 therefore AUTHORIZES an additive carrier** (additive field, or sibling payload type — impl discretion), with the existing field set and both existing helpers otherwise PRESERVED VERBATIM. *(An earlier draft of this ruling called the refusal "an existing-shape resume outcome carrying new content" — corrected at out-of-family review rounds 2 [P1] and 7 [P2]; following that summary would have sent an implementation down the converter/helper path, where the required token cannot be represented at all.)*

**Rationale for reusing the family rather than minting a namespace.** `[HIGH]` The three events — pause, read, resume — are one operator lifecycle over one durable object, and an operator reconstructing an incident needs them in one place. Minting a separate namespace for the middle event would split a causal chain across namespaces for no gain, and would force a fourth converter branch on a prefix discriminator table that already carries the pause/resume pair. `[MODERATE]` on the counter-consideration: a read is a *query*, and one could argue queries belong in a read/query namespace of their own — declined here because no such namespace exists to join, and inventing one for a single event would be the heavier extension.

### What §30.5 declares, and what it deliberately does not

**Declares:** the two event obligations; the required attribute CONTENT for each (the council's §6.5 content, applied verbatim); the **pairing requirement** that makes a stale-read refusal reconstructable; and the disclosure limits.

**Does NOT declare:** the concrete OTel attribute keys, the payload class's field names, or the carrier's shape between §30.5.2's two options. Those follow C-OD-30's existing conventions and are **implementation discretion at the impl leg**, consistent with how §C-OD-30.4 itself deferred production-callsite construction. This delta states the obligation and its content; it does not pre-author a schema for a surface whose producer does not yet exist.

**Sampling is DECLARED, not deferred — the exception to the paragraph above, and it is deliberate.** *(Corrected at out-of-family review rounds 6 [P2] and 7 [P2]; an earlier draft listed sampling among the deferred items while §30.5.4 declared it, which would have permitted the two events to be sampled independently.)* C-OD-30's existing sampling discipline names only the event kinds it already carries, so "inherit the existing convention" would have left these REQUIRED emissions with **no rule at all**. §30.5.4 therefore assigns both events the SAME `head` rate C-OD-30 already assigns its existing pause/resume event kinds — **because §30.5.3's pairing requirement is only sound if BOTH members of a pair are retained**, and independent sampling would break causal-pair reconstruction at exactly the rate it drops either one.

### Cross-axis dispositions

**Runtime AMENDED at the same-arc `Spec_Harness_Runtime_v1.md` v1.107** (C-RT-36 §31 accessor; §30 refusal-only staleness precondition; §30 cause-attribution refinement on the EXISTING `RT-FAIL-RESUME-HANDLE-UNKNOWN`; §14.14.8 append-only/never-truncated substrate invariant) — cross-referenced, never restated. **CP AMENDED at the same-arc `Spec_Control_Plane_v1_112.md`** (the `ResumeContext` provenance carrier; the public projection-returning surface) — cross-referenced, never restated. **IS / AS specs UNCHANGED.** **CXA CLASSIFIED at the same-arc `Cross_Axis_Composition_Document_v2_23.md`** — no new row, aggregate frozen at 111. **This OD delta adds NO cross-axis edge of its own:** it declares an emission obligation on surfaces that live in other axes, exactly as C-OD-30 already does for the pause/resume pair, and introduces no new CP→OD or Runtime→OD crossing.

**Plan disposition.** `Implementation_Plan_Operational_Discipline_v2_30.md` is **NOT bumped at this leg** — but **an OD plan delta IS OWED AT THE IMPL LEG, UNCONDITIONALLY.** `[HIGH]` The **emission** is Runtime-owned and pre-bootstrap, so its witnesses ride the same-arc `Implementation_Plan_Harness_Runtime_v2_55.md` U-RT-148 acceptance criteria where the producing code lands. The **carrier §30.5.2 authorizes is an OD-owned schema surface under BOTH options** — option (a) mutates the `frozen` / `extra="forbid"` `PauseResumeAuditPayload` this axis declares; option (b) adds a sibling type alongside it — and **a Runtime plan unit can own neither.** *(Corrected at out-of-family review rounds 3 [P1] and 6 [P2]: earlier drafts of this paragraph made the OD delta conditional on needing an OD-side helper, which left option (a) — an OD schema mutation — with no owning unit and no acceptance criteria.)* **What is deferred is only the SHAPE, not the obligation:** pre-authoring a unit for an unchosen carrier shape would fix by plan what §30.5.2 deliberately leaves to impl discretion, so the delta is registered as owed-at-that-leg rather than filed blind. Runtime plan v2.55 records the resulting ordering constraint as a **pending, not-yet-numbered OD dependency** of U-RT-148, so the Runtime unit cannot be scheduled ahead of it.

---

## §C-OD-30.5 (NEW at v1.36) — durable-pause-state read + staleness-refusal emission

**Contract surface.** Emission obligation. Two event kinds within the EXISTING C-OD-30 `pause.*` / `resume.*` namespace family.

**PRD enablement.** Makes the B-69 read auditable and makes a staleness-refused resume **reconstructable as one causal pair with the read that preceded it** — without which a refusal is an unexplained failure and the accessor is an un-audited read of durable state.

**ADR commitment(s) honored.** ADR-D6 v1.2 §1.2 (observability substrate — OD owns the authoritative namespace schema). **No new ADR**; no new namespace.

### §30.5.1 Event kind 1 — the accessor read (NEW event kind)

**Obligation.** Every invocation of the Runtime C-RT-36 §31 durable-pause-state read accessor emits, whether it succeeds or fails.

**Required content.**

| Carried | Note |
|---|---|
| the read attempt itself | including the failing case — an unsuccessful read MUST NOT be silent |
| `workflow_id` | the read's only key |
| the **cause attribution** — on an unsuccessful read ONLY | one of the five stable identifiers Runtime v1.107 §30 declares — `absent` / `empty-journal` / `read-error` / `corrupt-latest` / `workflow-mismatch` |
| **PER-VARIANT COUNTS** of returned locations — on a **successful** read | one count **per §31.2 classification** — **FOUR counts** (HITL-addressable / effect-fence-addressable / uniform-fallback-only / transitively-paused), **never the locations themselves**. *Per-variant rather than a single total: §30.5.1's disclosure limit 2 requires the emission to carry each location's CLASSIFICATION while carrying no identity, and a single scalar total cannot express classification. Per-variant counts do — they carry exactly the operator-safety-relevant fact (**how many gate-owning locations exist, and of which kind**, which is what property 4's sole-member rule turns on) while disclosing nothing about any individual location. (Corrected at out-of-family review round 3 [P2], which found the single-total shape and the classification requirement mutually unsatisfiable.)* |
| the **staleness token** minted by this read — on a **successful** read ONLY | the pairing key — see §30.5.3 |

**The token is required on SUCCESSFUL reads only, and the asymmetry is a contract term rather than an oversight.** `[HIGH]` *(Corrected at this delta's out-of-family review round 1 [P2], which found the first draft's "every invocation, including failures, emits the token" unimplementable against Runtime §31.4.)* Runtime v1.107 §31.4 rules **no-token-returned MUST mean no-projection-returned** and fails closed when a token cannot be minted — so on an `absent` / `empty-journal` / `read-error` / `corrupt-latest` / `workflow-mismatch` outcome there **is no token to emit**, by construction. Requiring one anyway would force an implementation either to fabricate a token (defeating the fence) or to suppress the failure emission entirely (defeating §30.5.1's own no-silent-failure rule). **The resolution keeps both:** a failed read emits, carrying its **cause attribution** and `workflow_id` and **no token**; a successful read emits carrying its **token** and **location count** and no cause attribution. The pairing requirement at §30.5.3 is correspondingly scoped — it binds a successful read to a subsequent refusal, which is the only pair that can exist, since **a refusal is only reachable from a read that produced a token**.

**Disclosure limits — binding, and each closes a specific hazard.**

1. **NEVER the locations' associated payload.** Not `summary_text`, not orchestrator or branch outputs, not external references. The projection excludes these from the caller-facing return (Runtime v1.107 §31.2); an emission that carried them would reopen through the telemetry channel exactly what the contract closed at the API — and a telemetry sink is a *different* trust boundary from the calling operator.
2. **NEVER the never-keyable pre-dispatch or depth-0-root internal identity.** CP v1.112 §2.2 constraint 2 makes its absence a type invariant at the API boundary; an emission carrying it would restore the pasteable string the invariant exists to eliminate. Emit the location's *presence and classification* — which the per-variant counts above carry exactly — **never its identity**.
3. **The cause attribution names the CAUSE CLASS ONLY** — never the underlying exception text, never a resolved filesystem path. Rendering an I/O error verbatim would disclose resolved filesystem paths on a surface whose entire justification is that it discloses nothing new.

### §30.5.2 Event kind 2 — the staleness-refused resume (a PRE-BOOTSTRAP refusal, and it needs a representable carrier)

**Obligation.** A `resume()` refused on the Runtime v1.107 §30 staleness precondition emits in the existing `resume.*` half of this namespace, carrying the **staleness token the caller supplied**.

**A PRE-BOOTSTRAP EMISSION NEEDS A PRE-BOOTSTRAP SINK — without one this REQUIRED event is silently lost.** `[HIGH]` *(Gap closed at out-of-family review round 15 [P1].)* Both §30.5 events fire on the **first crash-recovery call in a fresh process**, while the SDK `TracerProvider` and the audit writers are created **during bootstrap**. A default no-op / proxy provider **records nothing** — so an implementation that emits and moves on would satisfy the letter of §30.5.1 and §30.5.2 while producing **no telemetry at all**, defeating both the no-silent-failure rule and §30.5.3's causal-pair reconstruction, on the exact path this arc exists to serve.

**Contract term:** the §30.5.1 read event and the §30.5.2 refusal event MUST reach a **real sink**. Satisfying that requires **either** a minimal pre-bootstrap telemetry/audit initialization these two events can use, **or** a deferred buffer drained by the next bootstrap, **or** an equivalent lifecycle — **the mechanism is implementation discretion; reaching a real sink is not.** **Witness obligation:** the **fresh-process path** MUST be exercised end-to-end — assert the events are **retrievable from the sink** after a first-call-in-a-new-process read and a first-call refusal, **never merely that an emit call was made.** *An "the emit fired" assertion against a proxy provider is precisely the false green this term forecloses.*

**CORRECTION — this event kind is NOT representable by the unchanged existing payload, and an earlier draft of this delta wrongly said it was.** `[HIGH]` *(Caught at this delta's out-of-family review round 2 [P1]. The first draft claimed "no new payload type and no new converter branch are owed"; both halves of that claim are false, and they are corrected here rather than quietly repaired.)* Two independent facts defeat it:

1. **Timing.** Runtime v1.107 §30 raises the staleness refusal **PRE-BOOTSTRAP**, alongside the rest of the `RT-FAIL-RESUME-*` detect-then-refuse battery. At that point **no `ResumeAttempt` / `ResumeOutcome` pair exists** — the CP `PauseResumeProtocol` has not been invoked and `attempt_resume` has not run. So the existing §C-OD-30.4 `_project_resume_outcome_to_audit_payload` helper, which composes from exactly that pair, **has no inputs to compose from**, and the emission does **not** route through the CP→OD converter's `resume:` action-id branch at all: **its producer is the Runtime pre-bootstrap guard, not a CP lifecycle event.**
2. **Schema.** `PauseResumeAuditPayload` is declared `frozen=True` with `extra="forbid"` and carries **no staleness-token field**. A frozen closed-schema model cannot carry a value its schema does not declare — so "carry the token on the existing payload unchanged" is not a thing an implementation can do.

**Therefore §30.5.2 AUTHORIZES an additive carrier for this event kind.** Either (a) an additive field on `PauseResumeAuditPayload` for the supplied staleness token, or (b) a sibling payload type for pre-bootstrap resume refusals — **the choice is implementation discretion; the REQUIREMENT is that the token and the refusal disposition be representable without violating the closed schema.** Whichever is chosen: the existing `PauseResumeAuditPayload` field set is **otherwise PRESERVED VERBATIM**, both existing §C-OD-30.4 helpers are **unchanged**, and the existing pause/resume converter branch is **unchanged for every event it already handles**.

**Plan consequence, stated rather than left implicit — and it binds under EITHER option.** `[HIGH]` The **emission** is Runtime-side and pre-bootstrap, so it rides `Implementation_Plan_Harness_Runtime_v2_55.md` U-RT-148 (AC #13). The **carrier** is an **OD-owned schema surface under both option (a) and option (b)** — option (a) mutates the frozen, `extra="forbid"` `PauseResumeAuditPayload` declared by this axis, and option (b) adds a sibling type alongside it. **A Runtime plan unit cannot own an OD schema change or supply its acceptance criteria.** Therefore: **whichever option the impl leg selects, an OD plan delta is OWED AT THAT LEG**, assigning the carrier to an OD unit with its own acceptance criteria (schema shape, frozen/`extra="forbid"` posture preserved, and — for option (a) — a byte-compat witness that every existing `PauseResumeAuditPayload` construction site is unaffected). *(Corrected at out-of-family review round 3 [P1]: an earlier draft made the OD plan delta conditional on option (b) or a helper, which left option (a) — an OD schema mutation — with no owner at all.)*

**Why no OD plan delta is filed at THIS leg.** The carrier's shape is impl discretion between two live options, and pre-authoring a unit for a shape not yet chosen would fix by plan what this section deliberately leaves open. The obligation is **registered as owed-at-the-impl-leg, not deferred silently** — which is the same discipline the change-note's plan disposition applies to the emission-helper question.

### §30.5.3 The pairing requirement — the reason the token is emitted twice

**The token MUST be emitted at BOTH the SUCCESSFUL read (§30.5.1) and the refusing resume (§30.5.2), and it MUST be the same value**, so that a stale-read refusal is reconstructable **as ONE causal pair** from telemetry alone. *(Scoped to successful reads per §30.5.1's correction: a failed read mints no token, and a refusal is only reachable from a read that produced one — so no pair is lost by the scoping.)* `[HIGH]` This is the section's load-bearing requirement: without it, an operator investigating a refusal sees a resume that failed and a read that succeeded, with no evidence linking them — and the refusal's own operator-facing text (*the workflow's paused state changed since your read; re-read and recompose*) becomes unverifiable after the fact. **A refusal the operator cannot reconstruct is a livelock with good manners.**

### §30.5.4 Postures declared, so each absence is a decision

| Posture | Ruling |
|---|---|
| HITL gate on either emission | **NONE.** Runtime v1.107 §31.5 rules the accessor carries no gate; this section adds **zero new entries to the HITL escalation catalog** |
| New top-level namespace | **NONE minted.** Both events ride the existing C-OD-30 family; the C-OD-05 §5.1 roster is UNCHANGED |
| Redaction contract | **NOT ENGAGED, because nothing redactable is emitted.** The disclosure limits at §30.5.1 exclude free-text and model-generated payload at the source. **This is deliberately NOT a redaction gate**: the fields are excluded, so there is nothing to redact, and gating an absent channel is over-gating. **Reopening condition:** if a future arc admits `summary_text` into the projection (Runtime v1.107 §31.2's registered reopening condition, triggered when §14.14.7's `pause_context_reader` deferral is discharged), **this posture MUST be re-adjudicated in the same arc, with a redaction contract as a precondition of any inclusion** |
| Sampling | **DECLARED, not inherited by default.** C-OD-30's existing sampling discipline assigns its `head` rate to the two event kinds it already names (the pause-captured and resume-attempted events); it says nothing about a **third** event kind, so "unchanged" would have left this REQUIRED emission with **no rule at all** and exposed it to being dropped by the default policy — silently defeating §30.5.1's own no-silent-failure requirement. *(Caught at out-of-family review round 6 [P2].)* **Ruling: the §30.5.1 accessor-read event and the §30.5.2 staleness-refusal event take the SAME `head` sampling rate C-OD-30 already assigns its existing pause/resume event kinds** — they are low-volume operator-initiated recovery events, and the pairing requirement at §30.5.3 is only sound if **both** members of a pair are retained; independent sampling of the two would break causal-pair reconstruction at exactly the rate it drops either one |
| Cost attribution | **NOT ENGAGED** — the accessor performs no provider dispatch and incurs no metered cost |

### §30.5.5 Deferred to implementation discretion

The concrete OTel attribute keys and payload field names (following C-OD-30's existing conventions); whether the read event reuses an extended `PauseResumeAuditPayload` or a sibling payload type; the emission call sites; and whether an OD-side projection helper is warranted (see the change-note's plan disposition — **registered, not pre-authored**).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Spec_Operational_Discipline_v1_36.md` |
| Version | v1.36 (delta over v1.35) |
| Predecessor | `Spec_Operational_Discipline_v1_35.md` |
| Authoring authority | `.harness/council-b69-pause-state-accessor-2026-07-30.md` §6.5 + §9 row 5b; operator ratification 2026-07-30 (OPTION A′) |
| Contract-body change | ADDITIVE only — one new subsection under C-OD-30. §C-OD-30.1–§C-OD-30.4 PRESERVED VERBATIM; `PauseResumeAuditPayload` unchanged; C-OD-05 §5.1 namespace roster unchanged |
| Cross-axis cascade | NONE introduced by this delta — it declares an emission obligation on Runtime- and CP-owned surfaces, as C-OD-30 already does for the pause/resume pair |
| Plan delta | NONE at this leg (rationale + the registered condition under which one becomes owed are stated in the change-note) |
| Impl leg | NOT bundled — the emission witnesses ride `Implementation_Plan_Harness_Runtime_v2_55.md` U-RT-148, where the producing code lands |
| Skill discipline | `spec-writer` apply pass — applies the council's REQUIRED ruling + makes the namespace determination the council delegated to OD, with the grounding stated. Decides nothing the record left open |
| Date | 2026-07-30 |
