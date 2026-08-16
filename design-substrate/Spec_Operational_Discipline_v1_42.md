# Spec: Operational Discipline — v1.42 (delta over v1.41)

*Delta-only file. The v1.41 body + the entire C-OD-01 … C-OD-34 contract body are
PRESERVED VERBATIM (delta-only-spec-file convention). This delta carries exactly ONE
amendment — the **C-OD-09 §9.2 always-sampled exception set gains ONE row, 19 → 20**,
ingesting the `workflow.envelope` head=1.0 disposition that **C-OD-25 §25.1 has declared
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

`[HIGH]` **C-OD-25 §25.1 already declares the disposition this delta ingests.**
`Spec_Operational_Discipline_v1_8.md:90`, byte-exact:

> *"`workflow.envelope` head=1.0 (always-sampled — every workflow envelope-observable per
> PRD). Tail-keep policies per existing C-OD-3 composite sampler defer to per-child-span
> sampling; the envelope ALWAYS persists."*

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
| `workflow.envelope` | C-OD-25 §25.1 (`Spec_Operational_Discipline_v1_8.md:90`) | Trace-root envelope — the declared *"the envelope ALWAYS persists"* floor, ingested. Root membership is additionally the **only** mechanism that delivers the §9.2 floor to in-envelope member spans, because `ParentBased` never consults a non-root child's name |

**The Source-declaration cell cites an OD contract rather than a CP one**, and
deliberately so: unlike rows 1–19 this row ingests from *within* the axis. Citing a CP
contract here would misdescribe the provenance.

#### §0.2.2 Post-amendment cardinality — stated as contract

**The §9.2 always-sampled exception set is EXACTLY TWENTY members.** The four
conditional-by-attribute rows are UNCHANGED at four (`files.operation`,
`memory.operation`, `validator.fail.*`, and the root-conditional `subagent.span`); row 20
is **unconditional**. The two wildcard entries are UNCHANGED at two (`audit.*`,
`validator.fail.*`), so the literal-vs-prefix decomposition the SDK-boundary lookup
derives moves to **18 literals + 2 prefixes** (from 17 + 2).

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

`[HIGH]` **No configuration loses a span the status quo would have kept.** At the cap-8
concurrent composition — deliberately chosen as the worst measured case — C1 evicts 92
traces yet still exports **8 ordinary children, identical to the status quo's 8**, while
raising trigger-span and envelope exports from 14 and 8 to 100 and 100. What C1 evicts is
buffered context belonging to traces the status quo would have **head-dropped in their
entirety**. C1 is a strict improvement at every measured point.

`[MEDIUM]` **The real residual is concurrency headroom, and it is stated rather than
buried.** C1 multiplies **concurrent in-flight buffer occupancy by `1/base_rate`** (peak
9 → 100 at concurrency 100), because every envelope-rooted trace now reaches the buffer
where previously only the head-admitted fraction did. Against the shipped
`max_buffered_traces` default of 4096 (`types.py:741,752`) that moves the eviction
threshold from roughly 40,960 to roughly 4,096 **concurrent** envelope-rooted workflows at
a 0.1-rate cell. At the default cap the measured eviction count is **zero**; the headroom
reduction is real, bounded, and does not bite at any concurrency this cell is sized for.

`[MEDIUM]` **What is NOT priced here.** The `1/base_rate` **exported-volume** multiplier
against the C-OD-11 §11.1 per-cell budgets — C11's half of the `B-137` C7 ⊥ C11 tension —
is untouched by this delta and stays open at `B-182` / `B-183`. Rider (a) of v1.37 applies
unchanged: §11.1 enforces at the COLLECTOR_BOUNDARY / BACKEND_INGESTION layer
**independently of any sampling decision**, so §9.2 membership cannot admit throughput
past the enforced caps; what membership changes is which spans are KEPT within the
admitted stream. The structural-compatibility check that rider requires therefore
**PASSES** for row 20 on the same reasoning, and the open question remains the volume
*evidence*, not a missing cap.

### §0.4 Rider — this row extends the `B-160` head=1.0 divergence class from four to five

`B-160`'s grounding witness
(`harness-od/tests/test_b160_head_one_declarations_vs_always_sampled_set.py`) established
that head=1.0-declared-but-absent-from-§9.2 is a **class**, enumerating four unconditional
names across C-OD-32.3 and C-OD-30.3 plus two conditional ones. **`workflow.envelope` is a
fifth unconditional member of that same class and the enumeration missed it**, because
`B-160`'s close-out scoped the sweep to *"any OTHER **C-OD-3x** namespace"* and the
declaration lives at **C-OD-25**. The scoping, not the method, is what hid it. This delta
closes the C-OD-25 instance only; the four C-OD-3x instances stay open at `B-160`, whose
conformance sweep must now re-derive its class from a scope wider than C-OD-3x.

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
than ratifying a narrower one. Not a `B-160` conformance sweep — four C-OD-3x instances
stay open there per §0.4. Not a C11 pricing arc — the exported-volume multiplier against
§11.1 stays open at `B-182` / `B-183` per §0.3.

---

*End of v1.42 delta. The v1.41 body and all prior deltas stand unchanged beneath this
file per the delta-only-spec-file convention.*
