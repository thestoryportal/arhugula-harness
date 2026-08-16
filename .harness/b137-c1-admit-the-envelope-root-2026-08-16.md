# B-137 step (3) = C1 — build record, back-flow filing, and the two findings the build surfaced

**Filed:** 2026-08-16
**Arc:** implementation of `B-137` step (3), candidate **C1 (admit the root)**, operator-ratified
2026-08-16 and recorded at PR #1383.
**Posture:** bundled-absorption (root `CLAUDE.md` §11.4) — `design-substrate/` amendment
co-landing with `harness-od/src` + tests. Clearance marker at
`.harness/clearance/spec-operational-discipline-v1-42-cleared-2026-08-16.md`.
**Class:** Class 3 (informational back-flow) for the two findings below. Neither halts the arc;
both are recorded because they change what a downstream reader should believe.

---

## 1. What landed

`workflow.envelope` joins the C-OD-09 §9.2 always-sampled exception set as **row 20**
(`Spec_Operational_Discipline_v1_42.md` §0.2). The shipped head is
`ParentBased(root=HarnessCompositeSampler)`, which consults the inner sampler **only for
roots**; making the envelope a member therefore delivers the §9.2 floor to every in-envelope
member span **by inheritance**, which is the mechanism membership alone could not supply.

Count-contract reconciliation, five carriers, one commit (per
`[[count-contract-sweep-every-granularity]]`): `sampling_mode.py` (docstring, set comment,
decomposition note, set literal), `alignment_floor_drift_detection.py` (×2),
`substrate_seam_exports_aggregate_manifest.py:203`, `tests/test_sampling_mode.py`,
`tests/test_composite_sampler.py`. Point-in-time carrier landscapes (`v1_27.md:19`, v1.37's own
nineteen-row statements) are **preserved verbatim** per the v1.37 precedent.

---

## 2. FINDING 1 (Class 3) — C1 is an ingestion repair; the ratification was taken on an incomplete premise

`B-137` framed step (3) as *"a genuine architectural fork, not a bug with a fix"*, and candidate
C1 as *"add `workflow.envelope` itself to §9.2"* — i.e. as the workspace choosing to mint a new
floor. **Grounding at build time falsified that framing in the favourable direction.**

`Spec_Operational_Discipline_v1_8.md:90` (C-OD-25 §25.3), byte-exact:

> *"`workflow.envelope` head=1.0 (always-sampled — every workflow envelope-observable per PRD).
> […] the envelope ALWAYS persists."*

*(The elided clause defers tail-keep policy to the composite-sampler contract under v1.8's
pre-zero-padding numbering — today's C-OD-09. Elided, not quoted, so the head-scoped overlay
drift gate does not read a legacy identifier as a live contract cite with no code behind it.)*

C-OD-25 is preserved verbatim through the entire v1.9 → v1.41 chain (v1.9 §52/§57, v1.10
§246/§251, v1.11 §234 each re-attest it), so this is the **live** declaration at HEAD. §9.2 never
ingested it.

**Why this matters and is filed rather than absorbed.** The operator ratified C1 believing it to
be an architectural choice with a carried-forward cost. It is instead the same defect class v1.37
repaired for `fallback.exhausted` — a declared head=1.0 disposition dropped at §9.2 ingestion —
and the ratified option was therefore the one that restores contract consistency rather than the
one that departs from it. **This strengthens rather than undermines the ratification**, so the
arc proceeded; had the grounding cut the other way it would have been a Class 1 halt. Recorded so
no future reader treats §9.2 row 20 as a Phase-7 design extension (X-AL-3) when it is an
ingestion catch-up.

---

## 3. FINDING 2 (Class 3) — the ratified cost is superseded, and the real residual is a different one

The ratification carried forward: *"C1's cost is **data loss, not delay** — under production
buffer bounds a trace containing any ordinary non-member child becomes never-resolving, drained
only by `force_flush`"*, and required the implementing arc to measure the ordinary-child
population's frequency before shipping.

**Measured at this arc**, `team-binding × self-hosted-server` (base rate 0.1), 100 traces, through
the real `TailKeepSpanProcessor`:

| Composition | Status quo | Under C1 |
|---|---|---|
| Sequential, unbounded buffer | 0 buffered / 0 evicted | **0 buffered / 0 evicted** |
| Sequential, `max_buffered_traces=3` | 0 buffered / 0 evicted | **0 buffered / 0 evicted** |
| Concurrent (100 in flight), default cap 4096 | peak 9 buffered / 0 evicted | peak 100 buffered / **0 evicted** |
| Concurrent (100 in flight), cap 8 | peak 3 / 6 evicted / 8 ordinary exported | peak 8 / 92 evicted / **8 ordinary exported** |

**Three conclusions, each stated at the strength the measurement supports.**

1. **The stranding is discharged, and `B-136` is why.** The never-resolving population was a
   consequence of `B-136`'s name-arm early return, repaired at PR #1331
   (`tail_keep_span_processor.py:599-629`): an always-sampled root now runs the root-close
   flush-or-drop decision *before* forwarding itself, so its trace materializes and frees its
   buffer slot in the same `on_end`. The register row already carried this re-pricing in a
   ⚠️ bullet dated 2026-08-13; **the ratification bullet, written three days later, restated the
   superseded cost anyway.** The row's own two bullets contradict each other, and the later one
   is the wrong one. Corrected in the register at this arc.

2. **THIS ARC'S OWN OVERCLAIM, WITHDRAWN — and the correction is the more useful finding.** The
   first draft concluded *"no configuration loses a span the status quo would have kept"* from
   the cap-8 row, where both worlds export **8** ordinary children. Out-of-family Codex round 2
   rejected the inference, correctly: equal counts are not equal sets. Re-measured by trace
   IDENTITY, the base-rate sampler preserves a hash-drawn spread across the population while C1
   admits every envelope and `_evict_oldest_trace` (drop-oldest FIFO) keeps exactly the newest
   `max_buffered_traces` — so at cap 8 over 100 concurrent traces the baseline's survivors are
   almost entirely displaced. **C1 DOES lose spans the status quo would have kept, above the
   cap.** This is the `[[assert-the-shape-not-the-measurement]]` failure in its own right: an
   impeccable measurement read through the wrong comparison.

   What governs shipping is the threshold, and it is asserted in the same witness: at the
   shipped 4096 default the displacement set at concurrency 100 is **empty**, and C1 preserves
   100 ordinary children against the baseline's 13. Pinned at
   `test_c1_displaces_previously_preserved_traces_under_buffer_pressure`, which asserts the
   deterministic half as an exact set (C1's survivors are precisely the newest `cap`, because
   the policy is FIFO) and the displacement as a shape rather than a particular hash draw.

3. **The real residual is a concurrency THRESHOLD — a different residual from the one the
   ratification carried.** C1 multiplies *concurrent in-flight buffer occupancy* by
   `1/base_rate` (peak 9 → 100 at concurrency 100), because every envelope-rooted trace now
   reaches the buffer where previously only the head-admitted fraction did. Against the shipped
   `max_buffered_traces` default of 4096 (`types.py:741,752`) that moves the threshold at a
   0.1-rate cell from ~40,960 to ~4,096 concurrent envelope-rooted workflows. **Below it the
   cost is zero; above it the cost is the displacement in item 2.** Registered at `B-185`.

**This does not reopen the ratified choice.** The ratification's own instruction was that a
measurement showing buffer exhaustion as C1's steady state would be *"a new finding to route back
— not a licence to silently reopen a ratified choice."* The measurement shows the opposite of
exhaustion, so the choice stands unqualified and this filing is informational.

---

## 4. Consequential surfaces

**`B-160`'s divergence class grows from four to five.** `B-160` established that
head=1.0-declared-but-absent-from-§9.2 is a *class*, enumerating four unconditional names across
C-OD-32.3 and C-OD-30.3. `workflow.envelope` is a fifth, and the enumeration was structurally
unable to see it: `B-160`'s close-out scoped the sweep to *"any OTHER **C-OD-3x** namespace"*, and
this declaration lives at **C-OD-25**. The scoping, not the method, is what hid it. Row 20 closes
the C-OD-25 instance; the four C-OD-3x instances stay open at `B-160`, whose conformance sweep must
now re-derive its class from a scope wider than C-OD-3x. `B-160` also recorded that *"membership
alone cannot deliver the floor for a child span (the `B-137` dependency B-160 already carries)"* —
row 20 is the resolution of that dependency.

**A test-fixture hazard, fixed and pinned.** `harness-od/tests/test_tail_keep_span_processor.py`
used `workflow.envelope` as its *ordinary root* fixture in 34 places — a root carrying no floor,
so that reaching `downstream` proves the tail's flush-or-drop decision. Row 20 broke that premise:
seven tests went red, and **several others would have kept passing for the opposite reason**
(forwarded by the name arm, never buffered at all). The fixture is renamed to `ordinary.root` and
the module docstring now states the invariant, so a §9.2 member cannot be reintroduced into that
role and silently convert a buffering test into a passthrough test.

**The C1 discriminator module is inverted, not deleted.**
`harness-runtime/tests/integration/test_b137_c1_discriminator.py` was a counterfactual harness with
a self-guard that fired the moment C1 landed — working exactly as designed. It is converted to an
as-built witness: `_c1_member_set` (patch C1 *in*) becomes `_without_c1` (patch it *out*), the
positive control now asserts as-built membership *and* that the counterfactual arm still reaches
the derived literal structures, and the load-bearing discriminator gains a pre-v1.42 arm asserting
the starvation reproduces. Without that negative arm an as-built assertion cannot distinguish
"C1 works" from "this test asserts nothing"
(`[[only-the-classifier-can-witness-the-classifier]]`).

**A SECOND coverage bound, surfaced by out-of-family Codex against this arc's PR and confirmed
before acceptance (Class 3).** C1's floor works by inheritance through `ParentBased`, which consults
the inner sampler only for roots — so under an **unsampled ambient OTel parent** the envelope is a
child, `ParentBased` short-circuits to the parent's DROP without reaching the §9.2 lookup, and the
entire trace disappears exactly as it did pre-C1. Measured at `base_rate=0.0` through the real
`TailKeepSpanProcessor`: root-envelope exports the trace, ambient-unsampled exports nothing. The
reviewer's claim was **not taken at face value** — it was reproduced directly, and the production
reachability was verified by reading the MCP path (`lifecycle/mcp_server.py` dispatches through
`asyncio.to_thread`, inheriting the caller's `copy_context()`; the OTel current span is a
`ContextVar`). Pinned at `test_c1_does_not_survive_an_unsampled_ambient_parent` with a root-envelope
positive control, stated as a bound at v1.42 §0.3.1, and registered at **`B-186`** — not repaired,
because forcing the envelope to be a trace root trades the observability floor against
distributed-trace continuity, which is an architectural fork, and absorbing it would be a silent
X-AL-3 extension against a delta declaring ZERO emission-site change. It does **not** reopen
`B-137`, whose entire analysis reasons from the envelope being the trace root.

**What stays open.** C11's half of the C7 ⊥ C11 tension — the *exported-volume* multiplier against
the C-OD-11 §11.1 per-cell budgets — is untouched here and stays at `B-182` / `B-183`. v1.37 rider
(a) applies unchanged: §11.1 enforces at the collector/ingestion boundary independently of any
sampling decision, so §9.2 membership cannot admit throughput past the enforced caps; the open
question is the volume *evidence*, not a missing cap. Candidate **A** remains unmeasurable (its
tail half is unbuilt) and is neither taken nor foreclosed.
