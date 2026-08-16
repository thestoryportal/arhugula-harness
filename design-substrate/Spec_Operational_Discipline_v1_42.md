# Spec: Operational Discipline — v1.42 (delta over v1.41)

*Delta-only file. The v1.41 body + the entire C-OD-01 … C-OD-34 contract body are
PRESERVED VERBATIM (delta-only-spec-file convention). This delta carries exactly ONE
amendment — the **C-OD-09 §9.2 always-sampled exception set gains ONE row, 19 → 20**,
ingesting the `workflow.envelope` head=1.0 disposition that **C-OD-25 §25.3 has declared
since v1.8** and that §9.2 never absorbed. §9.1 and §9.3 are UNTOUCHED; §9.2's other
**nineteen** rows are PRESERVED VERBATIM and are cross-referenced here, never restated.*

**Authoring authority:** operator ratification 2026-08-16 of **`B-137` step (3) =
candidate (C1), "admit the root"**, taken via `AskUserQuestion` over the five-option set
with each option's measured cost stated, and recorded at PR #1383 / the `B-137` register
row. The ratification discharges the architectural gate the row carried since
2026-08-13. Applied per workspace `CLAUDE.md` §4.3 back-flow + §4.5 clearance discipline.
**Predecessor:** `Spec_Operational_Discipline_v1_41.md` (v1.41 — the B-138
`validator.fail.class` domain leg; cleared 2026-08-13)
**Revision shape:** Delta-only spec file. v1.41 + all earlier file bodies PRESERVED
VERBATIM. v1.42 carries this change-note + exactly ONE amendment: **§C-OD-09 §9.2 gains
row 20.** **ZERO new contract numbers** (C-OD-09 already exists — this amends its own
table, at the venue where the set is defined); **ZERO new namespace** (C-OD-05 §5.1
roster UNCHANGED at 15); **ZERO new attribute**; **ZERO emission-site change** (the
envelope span, its open site and its attribute set are all pre-existing and byte-
unchanged — only its sampling disposition moves); **ZERO CP delta**; **ZERO Runtime
delta**; **ZERO CXA rows** (aggregate frozen at 111); **ZERO hash impact**.

---

## Change-note (v1.41 → v1.42)

### §0.1 The defect — a declared floor that §9.2 never ingested

`[HIGH]` **C-OD-25 §25.3 already declares the disposition this delta ingests.**
`Spec_Operational_Discipline_v1_8.md:90`, byte-exact apart from one marked elision:

> *"`workflow.envelope` head=1.0 (always-sampled — every workflow envelope-observable per
> PRD). […] the envelope ALWAYS persists."*

**On the elision.** The omitted middle clause defers tail-keep policy to the composite-sampler
contract, naming it under v1.8's pre-zero-padding numbering — the ancestor of today's
**C-OD-09**. It is elided rather than quoted because reproducing that legacy identifier at the
delta-chain HEAD would mint a head-scoped contract cite with no code behind it (the overlay
drift gate reads §-cites mechanically and cannot tell a quotation from an assertion). Nothing
load-bearing to this delta sits in the elided clause: the amendment turns on the head=1.0
declaration and the *"ALWAYS persists"* guarantee, both quoted verbatim above.

C-OD-25 is **preserved verbatim through the entire v1.9 → v1.41 delta chain** (v1.9 §52 /
§57, v1.10 §246 / §251, v1.11 §234 each re-attest the preservation), so `:90` is the LIVE
declaration at HEAD, not superseded text. `workflow.envelope` is nonetheless **absent from
`ALWAYS_SAMPLED_EVENT_CLASSES`**, which §9.2 defines as exactly that floor.

**This is the same defect class v1.37 repaired, and the same shape.** v1.37 ingested
`fallback.exhausted` after finding its always-sampled disposition declared at
`Spec_Control_Plane_v1_2.md:410` and dropped at OD ingestion. Here the declaring contract
is OD's own C-OD-25 rather than CP's C-CP-03, so the ingestion gap is intra-axis; the
repair venue — the table where the set is defined — is identical.

`[HIGH]` **What the gap costs, measured rather than argued.** The envelope is the trace
ROOT (`workflow_driver.py:3458`, `start_as_current_span("workflow.envelope")`), and the
shipped head composition is `ParentBased(root=HarnessCompositeSampler(base_rate))`
(`tracer_provider.py:236-240`, bound unconditionally at every cell, mode discarded).
`ParentBased` consults the inner sampler **only for roots**; every child inherits the
root's decision and its own name is never examined. So an ordinary, non-member root loses
its base-rate draw and takes **every in-envelope §9.2 member down with it** — the floor
is unreachable for the members that matter, not because they were omitted from the set but
because the head never asks. Measured at the real production cell `team-binding ×
self-hosted-server` (base rate 0.1) over 100 envelope-rooted traces, `hitl.gate.evaluated`
— a §9.2 member with a declared head=1.0 floor — exported **9–13 times**, not 100.

### §0.2 The amendment — §9.2 gains row 20

**Amendment shape.** The §9.2 table at `Spec_Operational_Discipline_v1_2.md:513-532`
(as extended to nineteen rows at v1.37) gains **ONE row, appended as row 20**. **All
nineteen existing rows are PRESERVED VERBATIM** — no row is reworded, reordered, removed,
or re-qualified. §9.1, §9.3 and the §9 "Deferred to implementation discretion" footer are
**UNTOUCHED**. The §9 header block (Contract surface / PRD requirement / ADR commitment /
Cross-axis citation / Persona linkage) is **UNCHANGED**.

#### §0.2.1 The new row

| Event class | Source declaration | Rationale |
|---|---|---|
| `workflow.envelope` **at the trace root** | C-OD-25 §25.3 (`Spec_Operational_Discipline_v1_8.md:90`) | Trace-root envelope — the declared *"the envelope ALWAYS persists"* floor, ingested. Root membership is additionally the **only** mechanism that delivers the §9.2 floor to in-envelope member spans, because `ParentBased` never consults a non-root child's name. **Root-conditional**, like `subagent.span (root)`: the guarantee binds where the envelope opens the trace, and an envelope opened beneath a foreign unsampled parent is outside it — see §0.2.3 |

**The Source-declaration cell cites an OD contract rather than a CP one**, and
deliberately so: unlike rows 1–19 this row ingests from *within* the axis. Citing a CP
contract here would misdescribe the provenance.

#### §0.2.2 Post-amendment cardinality — stated as contract

**The §9.2 always-sampled exception set is EXACTLY TWENTY members.** The
conditional-by-attribute rows are UNCHANGED at four (`files.operation`,
`memory.operation`, `validator.fail.*`, plus the root-conditional `subagent.span`); row 20
is a **second root-conditional** row, joining `subagent.span` in that shape and taking the
set's structurally-qualified rows from one to two. Neither is attribute-conditional, so the
`_conditional_always_sampled` attribute resolver is **unchanged at three rows**. The two
wildcard entries are UNCHANGED at two (`audit.*`, `validator.fail.*`), so the
literal-vs-prefix decomposition the SDK-boundary lookup derives moves to **18 literals + 2
prefixes** (from 17 + 2).

#### §0.2.3 Row 20 is ROOT-CONDITIONAL, and the contract says so rather than only the change-note

`[HIGH]` **The guarantee is scoped in the row itself, deliberately.** Row 20 delivers the
floor by *inheritance*: the envelope is admitted at the head, and `ParentBased` hands every
child an inherited `RECORD_AND_SAMPLE`. `ParentBased` consults the inner sampler **only for
roots**, so where the envelope is NOT the trace root — a run begun beneath a foreign
unsampled ambient OTel span — it short-circuits to the parent's DROP and the membership is
never consulted at all. Writing row 20 as an unqualified *head=1.0 across all cells* would
therefore state a guarantee the mechanism does not deliver, and the spec would contradict
its own §0.3.1 three sections later. Out-of-family review flagged exactly that incoherence,
and it is fixed in the contract text rather than left to prose.

**This is a precise statement of reach, NOT candidate C.** `B-137`'s candidate C was to
ratify that the §9.2 floor is a floor over the *admitted stream* — accepting base-rate
starvation for in-envelope members. The operator did not select it and this delta does not
take it: within a harness-rooted trace the floor is absolute, which is the whole substance
of C1. **§9.3 is UNTOUCHED and all three of its invariants bind row 20** — the floor stays
inviolable at the deployment-binding layer and per-cell uniform. **Rows 1–19 are UNTOUCHED**;
no other row acquires a qualifier. The precedent for a structurally-qualified row is §9.2's
own `subagent.span (root)`, which has carried exactly this shape since original ingestion.

**The out-of-scope venue is registered, not absorbed.** `B-186` carries it with a measured
witness and a three-way option set (force the envelope to a trace root; attach the ambient
parent as an OTel *link* rather than a parent; or ratify this scope permanently). Choosing
among those changes trace topology for embedded hosts and is an architectural decision, so
it routes to the register rather than being settled inside a delta that declares ZERO
emission-site change.

### §0.3 The ratified cost, RE-MEASURED at this filing — and the carried-forward pricing it supersedes

The operator ratification carried forward a cost statement — *"C1's cost is data loss,
not delay … a trace containing any ordinary non-member child becomes never-resolving,
drained only by `force_flush`"* — and required the implementing arc to **measure the
frequency of that ordinary-child population before shipping C1 to a production-bounded
cell**. That measurement was made at this filing, at the `team-binding ×
self-hosted-server` cell through the real `TailKeepSpanProcessor`, and it **falsifies the
carried-forward cost**. Recorded here rather than deferred:

| Composition (100 traces, base rate 0.1) | Status quo | Under C1 |
|---|---|---|
| Sequential, unbounded buffer | 0 buffered / 0 evicted | **0 buffered / 0 evicted** |
| Sequential, `max_buffered_traces=3` | 0 buffered / 0 evicted | **0 buffered / 0 evicted** |
| Concurrent (100 in flight), default cap 4096 | peak 9 buffered / 0 evicted | **peak 100 buffered / 0 evicted** |
| Concurrent (100 in flight), cap 8 | peak 3 / 6 evicted | peak 8 / 92 evicted |

`[HIGH]` **The stranding is discharged, and `B-136` is why.** The never-resolving
population the ratification carried was a consequence of `B-136`'s name-arm early return,
repaired at PR #1331 (`tail_keep_span_processor.py:599-629`): an always-sampled ROOT now
runs the root-close flush-or-drop decision before forwarding itself, so its trace
materializes and frees its buffer slot in the same `on_end`. Sequentially, C1 costs
**zero** buffered traces and **zero** evictions even at a cap of 3 — the exact
counterfactual that read 3 buffered / 97 evicted before the repair.

`[HIGH]` **A CLAIM THIS DELTA FIRST MADE AND NOW WITHDRAWS.** A first draft stated *"no
configuration loses a span the status quo would have kept"*, resting on the cap-8 row
above: both worlds export **8** ordinary children. **That comparison was cardinality-only,
and out-of-family review was right to reject it.** Re-measured by trace IDENTITY, the two
sets are materially different: the base-rate sampler preserves whichever traces its
trace-id hash admits, spread across the whole population, while C1 admits every envelope
and the buffer's **drop-oldest FIFO** keeps exactly the newest `max_buffered_traces`. So
under buffer pressure C1-admitted traffic **does displace traces the previous sampler
would have preserved** — at cap 8 over 100 concurrent traces the baseline's survivors were
almost entirely evicted. Equal counts concealed it. The claim is withdrawn and the real
behaviour is pinned at
`test_c1_displaces_previously_preserved_traces_under_buffer_pressure`.

`[HIGH]` **What survives the correction, and it is the part that governs shipping.** The
displacement requires **concurrent in-flight traces to exceed `max_buffered_traces`**. At
the shipped default of 4096 (`types.py:741,752`) the measured displacement set at
concurrency 100 is **EMPTY**, and C1 strictly dominates: 100 ordinary children preserved
against the baseline's 13. Both halves are asserted in the same witness, so neither can
drift without reddening.

`[MEDIUM]` **The residual, restated at its true strength.** C1 multiplies **concurrent
in-flight buffer occupancy by `1/base_rate`** (peak 9 → 100 at concurrency 100), moving the
eviction threshold at a 0.1-rate cell from roughly 40,960 to roughly 4,096 **concurrent**
envelope-rooted workflows. Beyond that threshold the cost is **not** merely reduced
headroom — it is the displacement above, a real per-trace loss the status quo would not
have incurred. Below it the cost is zero. Registered at `B-185`, which now carries the
displacement measurement rather than a headroom figure alone.

`[MEDIUM]` **What is NOT priced here.** The `1/base_rate` **exported-volume** multiplier
against the C-OD-11 §11.1 per-cell budgets — C11's half of the `B-137` C7 ⊥ C11 tension —
is untouched by this delta and stays open at `B-182` / `B-183`. Rider (a) of v1.37 applies
unchanged: §11.1 enforces at the COLLECTOR_BOUNDARY / BACKEND_INGESTION layer
**independently of any sampling decision**, so §9.2 membership cannot admit throughput
past the enforced caps; what membership changes is which spans are KEPT within the
admitted stream. The structural-compatibility check that rider requires therefore
**PASSES** for row 20 on the same reasoning, and the open question remains the volume
*evidence*, not a missing cap.

### §0.3.1 Honest scope — what row 20 delivers, and the one venue where it does not

`[HIGH]` **Row 20 delivers the floor exactly while `workflow.envelope` is the trace ROOT.**
The mechanism is inheritance through `ParentBased`, and `ParentBased` consults the inner
sampler only for roots. So when a run begins under an **unsampled ambient OTel span** the
envelope is a *child*: `ParentBased` short-circuits to the parent's DROP without ever
reaching the §9.2 lookup, and the whole trace — envelope and every member under it —
disappears exactly as it did before this delta. Measured at `base_rate=0.0` through the
real `TailKeepSpanProcessor`: the root-envelope composition exports the trace, the identical
composition under an unsampled ambient parent exports **nothing**.

**This is stated as a bound rather than repaired here, deliberately.** The repair — opening
the envelope as a *forced* trace root — is an emission-site change that would detach every
embedded run from its caller's distributed trace, trading the observability floor against
trace continuity. That is an architectural decision, and absorbing it into this delta would
be a silent X-AL-3 design extension against a delta that declares **ZERO emission-site
change**. Registered at `B-186` with its measured witness and its option set.

**It is not a defect in row 20 and does not narrow the ratified scope.** `B-137` measured,
and its step-(3) ratification priced, the venue in which the envelope is the trace root —
the row reasons throughout from that premise and scopes its own finding to *"the members
emitted inside the envelope."* Row 20 closes that venue completely. The ambient-parent case
is an adjacent venue the row never scoped.

### §0.4 Rider — this row extends the `B-160` head=1.0 divergence class from four to five

`B-160`'s grounding witness
(`harness-od/tests/test_b160_head_one_declarations_vs_always_sampled_set.py`) established
that head=1.0-declared-but-absent-from-§9.2 is a **class**, enumerating four unconditional
names across C-OD-32.3 and C-OD-30.3 plus two conditional ones. **`workflow.envelope` is a
fifth unconditional member of that same class and the enumeration missed it**, because
`B-160`'s close-out scoped the sweep to *"any OTHER **C-OD-30…33** namespace"* (its own
wording used a `3x` wildcard, expanded here to the explicit range so the overlay drift gate
does not read the wildcard stem as a bare contract cite) and the
declaration lives at **C-OD-25**. The scoping, not the method, is what hid it. This delta
closes the C-OD-25 instance only; the four C-OD-30…33 instances stay open at `B-160`, whose
conformance sweep must now re-derive its class from a scope wider than C-OD-30…33.

`B-160` additionally records that *"repairing the implementation side is not sufficient on
its own — `ParentBased(root=…)` never consults a non-root child's name, so membership
alone cannot deliver the floor for a child span (the `B-137` dependency B-160 already
carries)."* Row 20 is the resolution of that dependency: admitting the ROOT delivers the
floor to in-envelope children **by inheritance**, which is the mechanism membership alone
could not supply.

### §0.5 Same-PR cascade — every live count claim reconciled at one commit

Forward from this delta the live §9.2 count is **20**, and every count claim in the
shipped substrate is reconciled in the same commit: `sampling_mode.py` (module docstring,
set comment, decomposition note, and the set literal), `alignment_floor_drift_detection.py`
(plan-vs-spec note ×2), `substrate_seam_exports_aggregate_manifest.py:203` (seam
`export_name`), and the fixture/cardinality witnesses at
`harness-od/tests/test_sampling_mode.py` + `harness-od/tests/test_composite_sampler.py`.
Per the v1.37 precedent, **point-in-time carrier landscapes are NOT amended**:
`Spec_Operational_Discipline_v1_27.md:19` ("18 entries", under a heading explicitly reading
*"Status at HEAD pre-v1.27"*) and v1.37's own nineteen-row statements are timestamped
records, correct as of their own filing and preserved verbatim.

### §0.6 What this delta is NOT

Not candidate **A**: the §10.3 ratio is **not** moved into the tail consumer, no
mode-conditional sampler is wired, and `tracer_provider.py`'s *"the current default
sampler ignores the mode … Future units may wire mode-conditional samplers"* note stands
unchanged — A's defining tail half remains unbuilt and therefore unmeasurable, exactly as
the `B-137` row records. Not candidate **A′**: `ParentBased` is **not** removed; A′ was
measured as a partial, name-only remedy that leaves the event-carried `B-133` family
starved, and it is not selected. Not candidate **C**: §9.2/§9.3's *head=1.0 across all
cells* language is **not** amended, because this delta ingests a declared floor rather
than ratifying a narrower one. Not a `B-160` conformance sweep — four C-OD-30…33 instances
stay open there per §0.4. Not a C11 pricing arc — the exported-volume multiplier against
§11.1 stays open at `B-182` / `B-183` per §0.3.

---

*End of v1.42 delta. The v1.41 body and all prior deltas stand unchanged beneath this
file per the delta-only-spec-file convention.*
