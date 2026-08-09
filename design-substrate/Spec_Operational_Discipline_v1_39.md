# Spec: Operational Discipline — v1.39 (delta over v1.38)

*Delta-only file. The v1.38 body + the entire C-OD-01 … C-OD-34 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta carries exactly ONE amendment — **§C-OD-09 §9.2.1 term 3 is AMENDED**, retracting its explicit decline to widen the §10.2 classification-trigger predicate to span events. §9.2.1 terms 1, 2, 4 and 5, §9.1, §9.2's nineteen rows, §9.3 and the whole of C-OD-10 §10.2 are UNTOUCHED and PRESERVED VERBATIM; they are cross-referenced here, never restated.*

**Filed:** 2026-08-09
**Authoring authority:** `Spec_Operational_Discipline_v1_38.md` §9.2.1 term 3 (*"The §10.2 trigger predicate itself is **NOT** widened to events at this delta … That half of the same span-name-vs-span-event mismatch is register row **`B-123`**'s scope and is left to it deliberately — the two rows are one family and `B-123` owns its own disposition."*), read together with forward-register row **`B-123`** close-out step (2), whose repair is settled and whose two candidate remedies are dispositioned there. Applied per workspace `CLAUDE.md` §4.3 back-flow + §4.5 clearance discipline.
**Predecessor:** `Spec_Operational_Discipline_v1_38.md` (v1.38 — the `B-133` realization leg, NEW §9.2.1; cleared 2026-08-08)
**Revision shape:** Delta-only spec file per the OD delta-only convention. v1.38 + all earlier file bodies PRESERVED VERBATIM. v1.39 carries this change-note + exactly ONE amendment: **§C-OD-09 §9.2.1 term 3**. **ZERO new contract numbers**; **ZERO roster change** (§9.2 stays at NINETEEN rows); **ZERO change to C-OD-10 §10.2** (its three rows are already correct — see §0.2); **ZERO new namespace** (C-OD-05 §5.1 roster UNCHANGED at 15); **ZERO new attribute**; **ZERO emission-site change**; **ZERO head-sampler change**; **ZERO CP delta**; **ZERO Runtime delta**; **ZERO CXA rows** (aggregate frozen at 111); **ZERO hash impact**.

---

## Change-note (v1.38 → v1.39)

### §0.1 What v1.38 declined, and on what grounds the decline is retracted

`[HIGH]` v1.38's term 3 did two things in one paragraph. It made the §10.2 keep flag **mirror** the name-matching path for a span forwarded under term 2 — and it then declined to widen the trigger **predicate** itself, naming `B-123` as the owner of that half and leaving it deliberately.

The decline was correct at v1.38 and is not being second-guessed here: `B-123` had not yet run its own close-out, its repair candidates were unchosen, and a leg that closes one half of a two-half mismatch should not silently absorb the other. **What v1.38 could not know is that the mirror it wrote was, at that revision, structurally sound but VACUOUS.** Term 3's first sentence conditions the flag on the span being *"itself a classification trigger"*; the predicate it defers to matches by span **name**; the carrier of an event-shaped trip is named `harness.runtime.retry_breaker_fallback`. The mirror therefore had no live case for the very members §9.2.1 exists to deliver. This delta supplies the case; it does not change the mirror.

`B-123`'s close-out has since run. Its step (1) positive control — the same real exhausted dispatch `B-133` used — observed `is_classification_trigger(span)` returning `False` on the carrying span and the trace's buffered siblings consequently DROPPED at root close. Its steps (2), (3) and (4) are answered on the register. **The retraction below is therefore the discharge of a deferred half, on grounds established after v1.38 was cleared — not a reversal of v1.38's judgement.**

### §0.2 The disposition is a CONFORMANCE REPAIR — C-OD-10 §10.2 already says EVENT

`[HIGH]` This is the load-bearing framing of the whole delta, and it is why no contestable spec direction is being chosen.

The §10.2 contract table is at `design-substrate/Spec_Operational_Discipline_v1_2.md` lines 580–584 and its two event-shaped rows read **VERBATIM**:

| Classification trigger | Span-tree preservation | Source declaration |
|---|---|---|
| `sandbox-violation` propagation | Parent + sibling spans of any `sandbox.violation` **event** preserved | ADR-D6 v1.1 §1.3 |
| `breaker-trip` propagation | Parent + sibling spans of any `breaker.tripped` **event** preserved | ADR-D6 v1.1 §1.3 |

The contract has said **event** since C-OD-10 was written. The realization matches by span **name**. So the divergence is **code non-conformant to cleared contract text**, and widening the predicate to scan span events is the repair that makes the realization say what the contract already says. **`B-123`'s two registered candidates are not symmetric under this reading:** "match the event name as well as the span name" conforms to the existing table, while "emit a span so named" would mint a NEW emission primitive that no cleared contract authorizes — an X-AL-3 design extension routing through workspace `CLAUDE.md` §4.3 back-flow, and the same venue-(b) route `B-133` already refused. **The first is taken.**

**Consequently §10.2 itself is NOT amended, and its non-amendment is the point.** The only text in the corpus that needs to change is v1.38's own explicit decline. A delta that also edited §10.2 would be asserting that the contract was wrong; it was not.

### §0.3 Scope narrows to the breaker arm — the sandbox sibling is already conformant

`[HIGH]` `B-123`'s registration instructed that the probe be widened by one arm rather than assuming the sibling was fine, since §10.2 rows 2 and 3 share the identical span-name-only shape. **That instinct was right and the answer is that the sibling IS fine.**

`sandbox.violation` is emitted as a **real span**, not an event — `tracer.start_as_current_span("sandbox.violation")` at `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:725`. An exhaustive `add_event(` sweep over all seven `harness-*/src` trees returns exactly **six** production call sites — `harness_breaker_schema.py:282` (`breaker.tripped`), `alignment_floor_drift_detection.py:242`, `retry_breaker_fallback.py:749` (`fallback.triggered`) / `:879` (`retry.skipped`) / `:1151` (`fallback.exhausted`), and `retry_breaker_tool.py:314` (`tool_retry.exhausted`) — and **NONE** is named `sandbox.violation`. The name the row-2 predicate matches is genuinely produced.

**The amendment nonetheless covers BOTH names, and the asymmetry between coverage and population is deliberate.** The predicate conforms to the contract table, and the table names both. A repair scoped to the one name that has a live event producer would re-create the same class of defect the moment a producer changed shape — which is precisely how this one arose. *(This is a coverage statement, not a producer claim: at HEAD, row 2's event arm matches nothing.)*

**Row 1 is untouched and is NOT part of this family.** Its carrier is a span **attribute** (`validator.fail.permanence == "permanent"`), so the name-versus-event distinction does not apply to it at all. Its own inertness — no production path sets that attribute — is register row **`B-124`**'s scope and is neither repaired nor prejudged here.

### §0.4 What this delta does NOT do — each stated so its absence reads as a decision

| Surface | Disposition |
|---|---|
| C-OD-10 §10.2's three rows | **UNCHANGED, and deliberately so** — the table already specifies the event carrier (§0.2). This delta conforms the realization to it; it does not re-word it |
| §10.2 row 1 (`validator.fail.permanence`) | **UNCHANGED.** An attribute carrier, outside the name-versus-event family; its inertness is `B-124`'s |
| §9.2's nineteen rows | **UNCHANGED.** No row added, removed or re-qualified. The §10.2 trigger set and the §9.2 roster are DIFFERENT rosters and this delta keeps them distinct (§1 term 3, second paragraph) |
| §9.2.1 terms 1, 2, 4, 5 | **PRESERVED VERBATIM.** Only term 3 is amended |
| §9.1 per-deployment-surface sampling mode | **UNCHANGED** |
| §9.3 sampling-discipline invariants | **UNCHANGED, and all three still bind.** The amendment only ever ADDS keeps, so the inviolable floor is never lowered |
| C-OD-11 §11.1 per-cell cardinality budget | **UNCHANGED.** Enforcement remains at COLLECTOR_BOUNDARY / BACKEND_INGESTION, downstream of and independent of any sampling decision |
| C-OD-05 §5.1 namespace roster (15) | **UNCHANGED** |
| The HEAD consumer | **UNCHANGED.** §9.2.1 term 4's declared bound is inherited unamended and applies to this amendment too (§0.5) |
| Emission sites, span topology, attributes | **UNCHANGED, byte-for-byte.** No emission moves; only the tail consumer's classification widens |

**No new contract number.** The amendment edits one term of an existing subsection of C-OD-09. Per the workspace's spec-leg discipline a spec leg cannot mint a `C-*` number; none is minted.

### §0.5 The honest bound — this repair is admission-bounded, and is not a full floor

`[HIGH]` §9.2.1 term 4 is inherited unamended, and it binds this amendment exactly as it binds terms 1–3: the head sampler resolves at span **creation**, production binds it from the §10.3 per-cell envelope **unconditionally in both §9.1 modes**, and a carrier the head never recorded never reaches `on_end` at all. Register row **`B-137`** measured the consequence — event-carrying carriers reach the tail at **~10%** at base-rate 0.1 (10.4% over 4,000 carriers) and **~20%** at 0.2 (20.9%).

**So this amendment delivers the §10.2 sibling tree only for head-ADMITTED carriers, and that is stated rather than glossed.** Of the trips the tail can see, the repair preserves the tree; of the trips the head dropped, it can preserve nothing. No term below asserts a full §10.2 floor, and none should be read as asserting one. The architecture-level route that would close the head half is `B-137`'s and is not decided here.

### §0.6 A premise the grounding pass FALSIFIED — recorded rather than inherited

`[HIGH]` `B-123`'s close-out carries a Class-3 informational note, homed there on the grounds that it *"sits on the same §10.2 table"*, asserting that §10.2 row 1's cite (*"classification == `permanent-fail` per ADR-D2 §1.8 fail-class taxonomy"*, `Spec_Operational_Discipline_v1_2.md:582`) **does not resolve**, because ADR-D2 §1.8 *"contains NO permanent-fail value"*. That rider was queued to ride this delta at zero marginal cost.

**It was re-grounded before being written into contract text, and it is FALSE.** `design-substrate/ADR-D2.md` §1.8 is at line 301, headed *"Sandbox-violation fail-class taxonomy"*, and its table at lines 303–311 has **three** columns — the second headed *"C5 fail-class (per `c5-validation-contract` SKILL.md)"*, whose values include **`permanent-fail`** at line 305 (`escape_attempt`), line 306 (`egress_denied` — *"permanent-fail (deterministic policy hit)"*) and line 309 (`signal` — *"permanent-fail (operator-induced)"*). The register's claim was derived from the `sandbox.fail.class` value enum at `ADR-D2.md:285` alone and missed the fail-class column of the very table it cites. **§10.2 row 1's cite RESOLVES.**

**The rider is therefore NOT carried by this delta**, and the register row's Class-3 note is corrected at the register rather than propagated. *(Recorded because a wrong cite-does-not-resolve note, once written into a contract as a carried rider, is materially harder to retract than to check — and because "it costs nothing extra to carry" is exactly the reasoning under which an unverified claim enters a canonical artifact.)*

---

## §1 The amendment — §C-OD-09 §9.2.1 term 3, AMENDED

*(Term 3 is REPLACED in full by the text below. Terms 1, 2, 4 and 5 and every other part of §9.2.1 are PRESERVED VERBATIM.)*

**Term 3 — the §10.2 keep flag is mirrored, AND the trigger predicate resolves BOTH shapes.** A span forwarded under term 2 MUST still set its trace's §10.2 keep flag if the span is itself a classification trigger, mirroring the name-matching path so an event-carrying trigger preserves its buffered tree-siblings.

The §10.2 classification-trigger predicate MUST resolve the two event-shaped triggers — `sandbox.violation` and `breaker.tripped` — against the span's **name** and, when the name does not match, against the names of the span's **events**. This conforms the realization to C-OD-10 §10.2, whose rows for both triggers specify the carrier as an *event* and always have; no §10.2 row is amended by this term. A trip carried as an event on a span that is in neither §9.2 nor §10.2 therefore delivers **both** its own §9.2 floor (term 2) **and** its trace's §10.2 sibling preservation.

**The §10.2 event-name set is NOT the §9.2 roster, and the two MUST NOT be collapsed.** Term 1 resolves §9.2 membership through the §9.2 SSOT; this term resolves §10.2 membership through the two §10.2 event-shaped trigger names only. The rosters answer different questions — §9.2 asks *"is this span kept unconditionally?"*, §10.2 asks *"does this span preserve its trace's siblings?"* — and a §9.2 member that is not a §10.2 trigger (`fallback.exhausted` is the live case) MUST forward its own carrier without flagging its trace. Both name sets MUST derive from a single declaration of each trigger name, so a name change reaches the span arm and the event arm together and the two cannot drift apart.

**§10.2 row 1 is outside this term.** Its carrier is a span attribute, so the name-versus-event distinction does not apply; its realization is register row `B-124`'s and is unaffected.

**The predicate MUST remain total and side-effect-free.** A span with no events, or with an absent attribute bag, MUST return a verdict rather than raise, preserving the predicate's existing tolerance. The event scan MUST be reached only after the name and attribute resolutions have failed, so a name-matching span never pays for it; that ordering is a cost property and is recorded as implementation discretion, not as a behavioural term.

**This term is bounded by term 4 exactly as terms 1–3 are.** It realizes §10.2 sibling preservation for carriers the head ADMITTED; it cannot realize it for carriers the head never recorded. No full-floor claim is made (§0.5).

### §1.1 Residual status — v1.38's deferred half

v1.38 term 3's deferred half is **DISCHARGED** for the TAIL consumer by the amendment above, and **NOT** discharged for the HEAD consumer, which is term 4's declared bound and stays exactly as v1.38 left it. Register row `B-123` closes at this leg's implementation. Register rows `B-124` (the §10.2 row-1 attribute carrier), `B-136` (the name-arm root-close buffer leak) and `B-137` (head admission) are untouched, each cross-referenced above and none prejudged.

### §1.2 Cross-axis dispositions

**CP UNCHANGED** — `Spec_Control_Plane_v1_2.md` §3.5's sampling declarations are untouched and no emission site moves. **Runtime UNCHANGED** — the `breaker.tripped` emission at `harness_breaker_schema.py:282` and its call site at `retry_breaker.py:641` are byte-unchanged; this delta changes a consumer's classification, never a producer. **IS / AS specs UNCHANGED.** **CXA UNCHANGED** — the amendment governs a classification inside a consumer OD already owns, introducing no new cross-package consumption, so **no row is owed and the aggregate stays frozen at 111**. **ADR-D6 v1.1 §1.3 UNCHANGED** — it is the source declaration §10.2's two rows already cite, and the amendment moves the realization toward it, not away.

### §1.3 Deferred to implementation discretion

**Nothing new is deferred as contract.** The name of the derived §10.2 event-name constant, its home, the scan's early-exit, and the once-only read of the span's event collection are implementation discretion, resolved at `Implementation_Plan_Operational_Discipline_v2_34.md` U-OD-60.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Spec_Operational_Discipline_v1_39.md` |
| Version | v1.39 (delta over v1.38) |
| Filed | 2026-08-09 |
| Predecessor | `Spec_Operational_Discipline_v1_38.md` (cleared 2026-08-08) |
| Amendment sites | ONE — §C-OD-09 §9.2.1 term 3 (replaced in full) |
| Contract numbers minted | ZERO |
| §9.2 roster | UNCHANGED at nineteen |
| C-OD-10 §10.2 | UNCHANGED — already specifies the event carrier |
| C-OD-05 §5.1 namespace roster | UNCHANGED at 15 |
| CXA rows | ZERO owed; aggregate frozen at 111 |
| Hash impact | ZERO |
| Plan leg | `Implementation_Plan_Operational_Discipline_v2_34.md` U-OD-60 |
| Register consequence | `B-123` CLOSES at this leg's implementation; its Class-3 rider is FALSIFIED and corrected at the register (§0.6), not carried |
