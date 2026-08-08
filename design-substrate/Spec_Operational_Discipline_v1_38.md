# Spec: Operational Discipline — v1.38 (delta over v1.37)

*Delta-only file. The v1.37 body + the entire C-OD-01 … C-OD-34 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta carries exactly ONE amendment — a **NEW §C-OD-09 §9.2.1**, "Realization of the §9.2 floor at the SDK boundary", which discharges the v1.37 honest-scope residual for the **TAIL** consumer and NARROWS it to a declared bound at the **HEAD** consumer. §9.1, §9.2's nineteen rows and §9.3 are UNTOUCHED and PRESERVED VERBATIM; they are cross-referenced here, never restated.*

**Filed:** 2026-08-08
**Authoring authority:** `Spec_Operational_Discipline_v1_37.md` change-note § *"Honest scope — what §9.2 membership does and does not deliver at HEAD"* (*"**The realization debt is REGISTERED, not absorbed and not repaired here.** Register row **`B-133`** carries it, with a named positive control as its first close-out step and two repair candidates whose venues differ in kind — an event-aware arm at tail-keep `on_end` (single-domain, no new primitive) versus an event→span projection at emission (a **new primitive routing through §4.3 back-flow per X-AL-3**, which this delta has no authority to mint)."*), read together with forward-register row **`B-133`** close-out steps (1) and (2). Applied per workspace `CLAUDE.md` §4.3 back-flow + §4.5 clearance discipline.
**Predecessor:** `Spec_Operational_Discipline_v1_37.md` (v1.37 — the `B-116-t3` leg, §9.2 roster 18 → 19; cleared 2026-08-08)
**Revision shape:** Delta-only spec file per the OD delta-only convention. v1.37 + all earlier file bodies PRESERVED VERBATIM. v1.38 carries this change-note + exactly ONE amendment: **NEW §C-OD-09 §9.2.1**. **ZERO new contract numbers** (C-OD-09 already exists — this adds a subsection to its own §9.2 material, at the venue where the floor is defined); **ZERO roster change** (§9.2 stays at NINETEEN rows); **ZERO new namespace** (C-OD-05 §5.1 roster UNCHANGED at 15); **ZERO new attribute**; **ZERO emission-site change**; **ZERO CP delta**; **ZERO Runtime delta**; **ZERO CXA rows** (aggregate frozen at 111); **ZERO hash impact**.

---

## Change-note (v1.37 → v1.38)

### §0.1 What v1.37 left open, and what was actually measured

`[HIGH]` v1.37's honest-scope paragraph states the characteristic without asserting its consequence: *"for all three the head=1.0 guarantee is carried only insofar as the **wrapper** span is kept"*. Whether the wrapper is in fact kept was **not** determined there — the paragraph registers the question at `B-133` and its close-out step (1) demands *"the positive control FIRST, and run it end-to-end rather than at the predicate. Grep proves the code path; only the run proves the floor is or is not delivered."*

**The positive control was run before this delta was drafted, and its result is the ground for every term below.** A real exhausted dispatch (`RetryBreakerFallbackDispatcher.dispatch`, a mock inner raising to fallback-chain exhaustion) was driven through a `TracerProvider` wired with the REAL `HarnessCompositeSampler` and the REAL `TailKeepSpanProcessor`, and the exporter was read directly. All three event-shaped members were covered by REAL dispatch shapes — `fallback.exhausted` by chain exhaustion, `fallback.triggered` by a capability-shortfall exhaustion, `breaker.tripped` by a charging-fault exhaustion at `fail_threshold=1`.

| Arm | Consumer | Configuration | Exported spans | Members delivered |
|---|---|---|---|---|
| A | HEAD only | `base_rate=0.0`, no tail processor | **0** | none |
| A′ | HEAD only | `base_rate=1.0` (control) | 3 | the carrier + its event **do** exist |
| A″ | HEAD only | `base_rate=0.0`, one span **NAMED** `fallback.exhausted` + one span **carrying it as an event** | **1** | only the **name**-shaped one survives |
| B | TAIL | head admits (`base_rate=1.0`), REAL `TailKeepSpanProcessor`, no `force_flush` | **0** | none |
| C | HEAD + TAIL | `base_rate=0.0` + tail processor (production shape) | **0** | none |
| E2 / E3 | HEAD / TAIL | the `fallback.triggered` dispatch shape | **0** / **0** | none |
| F2 / F3 | HEAD / TAIL | the `breaker.tripped` dispatch shape | **0** / **0** | none |

**The floor was not delivered, at either consumer, for any of the three members.** Arm A″ is the discriminator that makes *event-shaped, not name-shaped* the operative cause rather than an inference: the same sampler, at the same base rate, keeps the member when it is a span name and drops it when it is a span event.

The mechanism at the tail was read off the same run rather than assumed: the carrier span is `harness.runtime.retry_breaker_fallback`, which is in **neither** §9.2 (so `is_always_sampled(span.name, span.attributes)` is `False`) **nor** §10.2 (so `is_classification_trigger(span)` is `False`) — it therefore buffers and is dropped at root close, taking the always-sampled event with it.

**A side observation, recorded because it belongs to a sibling row and not to this one.** The same run confirms `B-123`'s step-(1) question in the affirmative for the §10.2 arm: `is_classification_trigger` matches `breaker.tripped` by span **name**, so an event-carried trip does **not** flag its trace for §10.2 sibling preservation. `B-123` owns its own disposition and is **not** closed here; §9.2.1 term 3 below deliberately declines to widen the trigger predicate.

### §0.2 Why the repair is the TAIL arm, and why the HEAD half is declared rather than discharged

`B-133` close-out step (2) names two candidate venues and rules them **not equivalent in kind**. Candidate (b) — an event→span projection at emission — mints a NEW emission primitive that no cleared spec authorizes and changes the span topology every existing witness asserts against; it is an **X-AL-3 design extension routing through §4.3 back-flow**, and this delta has no authority for it. Candidate (a) — an event-aware arm at the tail-keep `on_end` — introduces no primitive, no contract number and no new type; it reads the **existing** `is_always_sampled` SSOT against data the span already carries. **(a) is taken.**

The step also instructs *"confirm rather than assume"* on the head half, on the hypothesis that *"the HEAD surface at a head-based-dev cell samples at 1.0 anyway, so the head arm may need nothing."* **That hypothesis was checked and is FALSE, and the correction is recorded rather than inherited.** Enumerating C-OD-10 §10.3's per-cell envelope against §9.1's per-surface modes at this filing:

| Cell | §9.1 mode | §10.3 default base-rate |
|---|---|---|
| solo-developer × local-development | `HEAD_BASED_DEV` | **1.0** |
| **team-binding × local-development** | **`HEAD_BASED_DEV`** | **0.5** (min 0.1) |
| every other ACTIVE cell | `TAIL_BASED_PROD` | 1.0 / 0.1 / 0.2 |

`team-binding × local-development` is head-based at a default base-rate of **0.5**, and the tail-keep processor is not engaged at that surface at all (the production materializer wraps the BSP only when `deployment_surface != LOCAL_DEVELOPMENT`). **The head half is therefore a real, non-vacuous exposure at exactly one live cell**, and it cannot be repaired at candidate (a)'s venue for a structural reason: a span's events do not exist at span creation, so the head sampler has nothing to inspect. It is stated below as a **declared bound**, not as a discharged one.

### §0.3 What this delta does NOT do — each stated so its absence reads as a decision

| Surface | Disposition |
|---|---|
| §9.2's nineteen rows | **UNCHANGED.** No row is added, removed, or re-qualified. This delta governs how the roster is *resolved*, never what is in it |
| §9.1 per-deployment-surface sampling mode | **UNCHANGED.** §9.2.1 adds no per-surface branch; it describes what each existing consumer resolves |
| §9.3 sampling-discipline invariants | **UNCHANGED, and all three still bind.** The arm only ever ADDS keeps, so the inviolable floor is never lowered |
| C-OD-10 §10.1 base-rate set / §10.2 tail-keep triggers | **UNCHANGED.** §10.2's three triggers are not widened to events — that is `B-123` |
| C-OD-11 §11.1 per-cell cardinality budget | **UNCHANGED.** Enforcement remains at COLLECTOR_BOUNDARY / BACKEND_INGESTION, downstream of and independent of any sampling decision |
| C-OD-05 §5.1 namespace roster (15) | **UNCHANGED** |
| The three events' attributes, spans, and emission sites | **UNCHANGED, byte-for-byte.** No emission moves; only the tail consumer's classification widens |
| The HEAD consumer | **UNCHANGED.** Declared bound per §9.2.1 term 4, not repaired |

**No new contract number.** §9.2.1 is a subsection of the existing C-OD-09 §9.2 material, at the venue where the floor is defined. Per the workspace's spec-leg discipline, a spec leg cannot mint a `C-*` number; none is minted.

### §0.4 The F-08 volume bound — now MEASURABLE, still explicitly OPEN

`B-133` close-out step (3) is the C7 `F-08` per-tenant keep-volume measurement against the C-OD-11 §11.1 1,000 spans/sec budget, and it is sequenced **after** realization *"because measuring keep-volume before the floor is actually realized would measure the wrong thing."* This delta realizes the floor at the tail, so the measurement becomes meaningful for the first time — **and it is NOT performed here.** No volume claim is made and no term below depends on one, exactly as v1.37's rider (a) paragraph required. The bound is carried forward as a **named residual on the closed `B-133` row** (the `B-104` precedent for a residual that outlives its row's disposition), not as a silently dropped step.

What CAN be stated without measurement, because it is structural rather than populational: the arm forwards the **carrier span**, which is the smallest unit the OTel export boundary can deliver an event in — there is no sub-span export — so the keep granularity is one carrier span per event-carrying dispatch, and the arm adds **zero** emission sites and **zero** per-attempt multiplier. That is a shape statement, not a volume statement, and it is offered as neither.

**The matching population is enumerated rather than estimated.** Every `add_event` production site in `harness-{runtime,cp,od}/src` was swept at this filing — **six** sites emitting **six** distinct event names — and each was resolved against `is_always_sampled` by execution:

| Event name | §9.2 member? |
|---|---|
| `fallback.triggered` | **yes** |
| `fallback.exhausted` | **yes** |
| `breaker.tripped` | **yes** |
| `retry.skipped` | no |
| `tool_retry.exhausted` | no |
| `gen_ai.eval.alignment_floor.drift_detected` | no (its head=1.0 posture comes from §18.2, not §9.2) |

Plus the SDK's own auto-generated `exception` event, which is also not a member. **Exactly the three named members match, and nothing else does at HEAD** — so the arm's reach is the three rows it exists for, not a widened keep across unrelated telemetry. This is a *current-carrier* enumeration, not a bound: a future producer emitting a §9.2-named event would be matched by term 1 by design, which is the point of resolving through the SSOT rather than a hand-listed three.

---

## §1 The amendment — NEW §C-OD-09 §9.2.1

*(Inserted immediately after the §9.2 table and its preamble; the table, the preamble and §9.3 are PRESERVED VERBATIM.)*

### §9.2.1 Realization of the §9.2 floor at the SDK boundary

The §9.2 set is a roster of **event classes**. Some of its members are realized at the OTel SDK as **spans**, whose class is carried by the span **name**; others are realized as **span events** on a carrier span, whose class is carried by the **event** name. The floor binds identically in both cases — §9.2 membership is a property of the event class, not of the shape the SDK happens to give it. The following five terms are normative.

**Term 1 — the TAIL consumer resolves BOTH shapes.** The tail-keep consumer MUST resolve §9.2 membership against the span's **name** and, when the name does not match, against the names of the span's **events**. Both resolutions MUST go through the SAME §9.2 lookup, so the roster has exactly one authority and any future roster amendment reaches both shapes at once. Event attributes MUST be passed to that lookup, so the four conditional-by-attribute rows keep their **conservative-absent** posture (a missing discriminator always-samples) at the event shape exactly as at the span shape.

The event resolution is **independent of the carrier span's own §9.2 status**, including the carrier's own conditional or root-conditional membership. An event's class is the event's, not the span's; a member carried as an event on a span the roster would have excluded is still a member. *(Stated because the tail's `subagent.span` root-conditional gate sits immediately above this resolution. At HEAD no `subagent.span` carries a §9.2-named event — see §0.4's enumeration — so this is a rule, not a live case.)*

**Term 2 — a match forwards the CARRIER span immediately.** When any of a span's events is a §9.2 member, the span MUST be forwarded to the downstream processor immediately, bypassing the tail-keep buffer, on the same terms as a name-matching span. **The whole carrier span is kept, and this is stated rather than glossed:** the OTel export boundary has no sub-span unit, so the carrier is the minimum that delivers the event. The keep is therefore coarser than the roster entry, and the resulting keep-volume is the OPEN measurement at `B-133`'s residual (§0.4).

**Term 3 — the §10.2 keep flag is mirrored, NOT widened.** A span forwarded under term 2 MUST still set its trace's §10.2 keep flag if the span is itself a classification trigger, mirroring the name-matching path so an event-carrying trigger still preserves its buffered tree-siblings. The §10.2 trigger predicate itself is **NOT** widened to events at this delta: `breaker.tripped` carried as an event delivers its own §9.2 floor (term 2) but does **not** flag its trace for sibling preservation. That half of the same span-name-vs-span-event mismatch is register row **`B-123`**'s scope and is left to it deliberately — the two rows are one family and `B-123` owns its own disposition.

**Term 4 — the HEAD consumer is a DECLARED BOUND, not a discharged one.** The head sampler resolves at span **creation**, before any event exists; it therefore cannot resolve an event-shaped member and is UNCHANGED by this delta. **The bound is not vacuous.** `team-binding × local-development` is `HEAD_BASED_DEV` per §9.1 at a §10.3 default base-rate of **0.5**, and engages no tail-keep consumer, so at that one cell the three event-shaped members remain subject to base-rate sampling notwithstanding their §9.2 membership. Closing this bound requires giving the members a span shape at emission — a NEW emission primitive that no cleared contract authorizes, routing through workspace `CLAUDE.md` §4.3 back-flow per X-AL-3 — and is **NOT** authorized by this delta. Every `TAIL_BASED_PROD` cell, which is every production cell, resolves at the tail and is covered by terms 1–3.

**Term 5 — bookkeeping is bounded.** A span forwarded under term 2 that is also its trace's **root close** MUST still materialize its trace's keep decision, so the trace's buffered siblings resolve and the trace frees its bounded-buffer slot. This is required because the dispatch carrier span is routinely the root close, so an unconditional early return would leave every such trace pending until `force_flush` and would consume `max_buffered_traces` capacity. *(The name-matching path returns unconditionally and does leave an always-sampled root's trace pending; that is PRE-EXISTING, was observed at this leg's positive control, is NOT repaired here, and is registered as forward row `B-136`.)*

**Cost posture.** The event resolution is reached ONLY when the span-name resolution has already failed, so a name-matching span never pays for it, and it early-exits on the first matching event. This is an implementation-discretion property, not a contract term; it is recorded so the discretion is exercised deliberately.

### §1.1 Residual status — v1.37's honest-scope residual

v1.37's registered realization residual is **DISCHARGED for the TAIL consumer** by terms 1–3 and **NARROWED, not discharged, for the HEAD consumer** by term 4. `B-133`'s close-out steps (1) and (2) are executed; step (3) — the F-08 per-tenant keep-volume measurement — stays **explicitly OPEN** and is carried as a named residual on the closed row per §0.4. The v1.37 honest-scope paragraph itself is **PRESERVED VERBATIM**; this subsection records its disposition without editing it.

### §1.2 Cross-axis dispositions

**CP UNCHANGED** — `Spec_Control_Plane_v1_2.md` §3.5 declares the three members' sampling disposition and is untouched; the emission sites at `retry_breaker_fallback.py` and the OD breaker emitter are byte-unchanged. **Runtime UNCHANGED** — §14.6.3's waived-charge terms and the `retry.*` residual are cross-referenced, never restated; no Runtime text moves. **IS / AS specs UNCHANGED.** **CXA UNCHANGED** — the amendment governs a classification inside a consumer OD already owns, introducing no new cross-package consumption, so **no row is owed and the aggregate stays frozen at 111**. **C-OD-05 §5.1 namespace roster UNCHANGED at 15.** **C-OD-11 §11.1 UNCHANGED** — the budget enforces downstream of sampling and is not a function of §9.2 realization.

### §1.3 Deferred to implementation discretion

**Nothing new is deferred as contract.** The cost posture recorded at §9.2.1 (name-check-first ordering, early exit) and the concrete lookup helper's name and home are implementation discretion, resolved at `Implementation_Plan_Operational_Discipline_v2_33.md` U-OD-59.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Spec_Operational_Discipline_v1_38.md` |
| Version | v1.38 (delta over v1.37) |
| Predecessor | `Spec_Operational_Discipline_v1_37.md` |
| Authoring authority | v1.37's honest-scope paragraph + forward-register row `B-133` close-out steps (1) + (2); repair venue (a) selected per the row's own not-equivalent-in-kind ruling |
| Contract-body change | **ADDITIVE only** — ONE new subsection §C-OD-09 §9.2.1 (five normative terms). §9.1, §9.2's nineteen rows + preamble, and §9.3 PRESERVED VERBATIM. ZERO new contract numbers; ZERO roster change; ZERO new namespace; ZERO new attribute; ZERO emission-site change; ZERO hash impact |
| Empirical grounding | The `B-133` positive control, run END-TO-END before drafting: a REAL exhausted dispatch through the REAL `HarnessCompositeSampler` + the REAL `TailKeepSpanProcessor`, covering all three event-shaped members across seven configurations. **Result: ZERO spans exported at both consumers for all three members.** Arm A″ isolates *event-shaped, not name-shaped* as the cause |
| Corrections recorded | `B-133` close-out step (2)'s hypothesis that a head-based-dev cell *"samples at 1.0 anyway"* is **FALSE** — `team-binding × local-development` is `HEAD_BASED_DEV` at §10.3 default **0.5** with no tail consumer. Corrected rather than inherited; the head bound is declared as non-vacuous at term 4 |
| Cross-axis cascade | **NONE.** CP / Runtime / IS / AS unchanged; CXA aggregate frozen at 111 |
| Sibling rows NOT closed | **`B-123`** — the §10.2 trigger half. This leg's positive control ANSWERS its step-(1) probe (an event-carried `breaker.tripped` does not flag its trace) and the finding is recorded at §0.1 as a cross-reference; term 3 deliberately declines to widen the predicate. **`B-124`** (the inert attribute-qualified row) UNTOUCHED |
| Residual | v1.37's realization residual **DISCHARGED at the TAIL**, **NARROWED to a declared bound at the HEAD** (term 4). `B-133` step (3) — the F-08 per-tenant keep-volume measurement — stays **explicitly OPEN**, carried as a named residual on the closed row per the `B-104` precedent |
| New forward row | **`B-136`** — the pre-existing name-matching arm leaves an always-sampled ROOT's trace buffered until `force_flush`. Observed at this leg's probe, NOT repaired here (repairing it would change shipped behaviour for name-shaped always-sampled roots, outside this delta's authority) |
| Plan delta | `Implementation_Plan_Operational_Discipline_v2_33.md` — NEW **U-OD-59**, filed in the SAME arc |
| Impl leg | **BUNDLED** — the arm and its twelve witnesses land in this same PR under U-OD-59 |
| Register consequence | **`B-133` CLOSES at this leg** (steps 1 + 2 executed; step 3 carried as a named residual). `B-123` / `B-124` unchanged; `B-136` newly registered |
| Skill discipline | `spec-writer` apply pass — applies the repair venue the `B-133` row itself ranked, executes the positive control the row demanded first, and decides nothing the row left open |
| Date | 2026-08-08 |
