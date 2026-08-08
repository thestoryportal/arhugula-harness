# Implementation Plan: Harness Runtime — v2.61 (delta over v2.60)

*v2.61 is the plan leg of register row **`B-115`**, disposition **(b′)** — the deterministic ledger-conflict split recommended at the #1265 grounding (commit `05abb419`) after that grounding FALSIFIED reading (b)-as-registered. It carries **ONE new unit and ZERO amended units**: **U-RT-153**, the split itself — a new memory-family sibling exception type, the capture-boundary VALUE discriminator that makes the deterministic refusal distinguishable at all, the three executor re-type surfaces, the classifier admission and the waiver-tuple extension **4 → 5**, plus the determinism witness set the spec's own row-6 condition demands. **U-RT-152 is LANDED and CLOSED (PR #1271) and is NOT amended** — a NEW unit per the `B-97`(a) → U-RT-149 and `B-111` → U-RT-151 precedent, because amending a closed unit's acceptance criteria would falsify its closure criterion retroactively. **ZERO contract numbers minted, ZERO `snapshot_hash` impact, ZERO cluster, ZERO cross-axis edge, ZERO CXA rows (aggregate frozen at 111), ZERO Memory-spec or Memory-plan delta.** Every unit other than the NEW U-RT-153 is **PRESERVED VERBATIM**; U-RT-150, U-RT-151 and U-RT-152 remain **CLOSED**.*

**Status:** Proposed

---

## §0 Change-note (v2.60 → v2.61)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_60.md` (v2.60 — the `B-116` Reading (II) plan leg; ONE new unit U-RT-152, ZERO amended). U-RT-152's **impl leg landed at PR #1271** (merge commit `3ba68285`); with the `B-116-t3` OD leg at PR #1272, `B-116` flipped to `closed`.

### §0.2 Revision context

`[HIGH]` `B-115` records a **MEASURED** residual, not an inferred one: at the `B-84` build leg (PR #1243) cell (3) of that leg's W-5 four-cell matrix was EXECUTED, and it found that a memory capture whose text and model NAME are unchanged but whose PROVIDER differs re-derives the SAME `memory_id` (`summary_model` is hashed into the content; the provider is not), so the record JSONL line is appended a second time and the operation ledger then REFUSES on its 18-field equivalence payload. That refusal surfaced as `MemoryToolExecutionStoreError`, which `_classify_provider_exception` maps to `TRANSIENT_RETRY` — so the landed `B-84` fail-fast half was **re-enterable** through the store-error class, and the duplicate line was re-appended once per retry attempt.

The row registered three candidate dispositions. The **#1265 grounding FALSIFIED (b)-as-registered**: making the whole store-error class non-re-enterable is wrong, because that class also wraps genuinely transient store I/O (disk-full, permission) which a retry CAN clear — the classifier's own docstring already refuses wholesale fail-fasting for exactly this reason. It recommended **(b′)**: split the DETERMINISTIC ledger-conflict case into a NEW exception type, leaving the transient half untouched. Reading (a) — provider joins the capture identity — stays the registered residual and is **NOT built here**.

Spec leg at `Spec_Harness_Runtime_v1.md` **v1.113 §14.6.3** (row 6 flipped from prospective-conditional to WAIVED-confirmed; guard tuple four → five; the `B-132` residual narrowed).

### §0.3 Why spec, plan and impl land TOGETHER at this leg

`[HIGH]` Stated because it departs from the `B-116` / `B-96` / `B-107` split-leg precedent, and the departure is **forced rather than chosen**. §14.6.3 row 6 admits the type *"only after `B-115`'s build confirms determinism"*, and C9's binding form at the council record is *"never speculatively"*. A spec-first leg would have to assert the confirmed disposition before the confirming evidence existed — the circularity `.harness/council/b116-breaker-semantics/02-adversarial/REVIEW-e2.md` F-05 flagged. The determinism witness is therefore a **precondition of the contract text**, and the operative precedent is the bundled **`B-116-t3` leg (PR #1272)**, not the split ones.

### §0.3-bis Round-2 realization — the chaining half of AC #2

`[HIGH]` Out-of-family review round 1 found the value-discriminator realization
had left AC #2's **chaining** requirement unmet on the capture surface: the two
direct-append surfaces chained (they catch the ledger exception), while the
capture surface reduced it to `failure_reason` and raised UNCHAINED. That is a
real AC/impl divergence, not a wording nit — the same substrate event lost its
traceback origin depending on which surface caught it.

**Fixed rather than relaxed.** The AC text was NOT weakened to match the
implementation; the implementation was completed to match the AC. The capture
result now retains the exception itself as `failure_cause`, and the wrapper
raises `from` it. AC #2 is REWORDED at this delta — a plan-file edit in this
PR, which is legitimate because the plan is this PR's own new file — but the
rewording STRENGTHENS it (every surface must chain, plus a joint symmetry
witness), it does not narrow it to fit what was built. Two PD-8 probes were
added for the new surface (f: drop the `from`; g: drop the retention).

### §0.4 What this delta carries — counts

ONE new unit (**U-RT-153**); ZERO existing units amended; ZERO clusters; **ONE new DAG edge** (U-RT-152 → U-RT-153); **ZERO cross-axis edges** (the memory-tool exception types are an EXISTING import dependency of `retry_breaker_fallback.py`, and `harness_runtime` → `harness_is` is a pre-existing package edge — `memory_capture.py` already imports `MemoryOperationIdempotencyConflictError`); ZERO CXA rows (aggregate frozen at 111); ZERO contract numbers; ZERO Memory-spec / Memory-plan delta. Witness modules 2 (5 + 11 tests); PD-8 probes 7.

---

## §1 U-RT-153 — the `B-115` (b′) deterministic ledger-conflict split

**Unit ID:** U-RT-153 (**NEW**)
**Spec anchors:** `Spec_Harness_Runtime_v1.md` v1.113 **§14.6.3** row 6 (the confirmed waiver + the four-part determinism definition), the guard paragraph (five-type tuple, BY-NAME rule, classifier-consistency requirement, sibling-not-subclass constraint) and the narrowed declared-residual paragraph. `Spec_Memory_Substrate_v1.md` v1.3 **C-MEM-19** is consumed UNCHANGED — the new type declares no class and inherits the base residual, which that contract states is conforming. Authority is register row `B-115`, disposition (b′) as recommended at the #1265 grounding and adopted at this leg.
**Depends on:** [U-RT-152 (prior-landed — the guard, the waiver tuple and the predicate this unit extends)].
**Cluster:** none new — U-RT-153 joins the existing Runtime dispatch-composition cluster U-RT-152 belongs to.

### Implement

1. **(The new type — a SIBLING, and the three constraints that fix its shape.)** `[HIGH]` A new `MemoryToolExecutionLedgerConflictError` in `memory_tool_executor.py`, subclassing the memory family BASE. All three constraints are load-bearing and each is separately killable: **(a) NOT a subclass of `MemoryToolExecutionStoreError`** — MRO lookup would carry `io_failure` straight back onto this population and void the C-MEM-19 half of the split; **(b) NOT the family base** — the next item admits it to `isinstance` tuples, which are subclass-inclusive, so the base would sweep in the denied and store subtypes the classifier deliberately leaves transient; **(c) declares NO `memory_failure_class`**, inheriting the base's RESIDUAL `provider_adapter_failure`. (c) is a DECISION, not a default: `io_failure` is a positively wrong claim about a ledger refusal, and minting a dedicated `ledger_conflict` value would widen C-MEM-19's ratified vocabulary — an operator-gated Class 2 decision this leg may not take, registered instead as forward row **`B-134`**.

2. **(The capture boundary — discriminate as a VALUE, not by propagating.)** `[HIGH]` `EpisodicMemoryCapture._capture` folds the ledger refusal into a `MemoryCaptureResult(status=FAILED)` whose only carrier is a `failure_reason` STRING; the exception is deliberately not retained, so **no honest discriminator survived that boundary**. Add a closed `MemoryCaptureFailureKind` enum (`LEDGER_CONFLICT` / `STORE_IO`) and an optional `failure_kind` field on `MemoryCaptureResult`, set on every `FAILED` result and `None` on the CAPTURED path by construction. The span's `failure_class` follows the same split — the **RESIDUAL** for a ledger refusal (not an I/O fault; per C-MEM-19 v1.3 a residual report is the ABSENCE of a claim rather than a wrong one), `io_failure` for everything else — which keeps the inner capture span and the outer standard-tool span AGREEING about the same event, the property `B-88` round 2 introduced the store subtype to protect.

   **The result ALSO retains the ledger exception itself**, as `failure_cause`, typed as the CONCRETE `MemoryOperationIdempotencyConflictError` and set exactly when `failure_kind is LEDGER_CONFLICT` — enforced BOTH WAYS by a model validator, because the missing-cause direction is the dangerous one: the executor's `raise ... from result.failure_cause` would degrade to `raise ... from None`, which **suppresses** the context rather than merely omitting it, actively hiding the origin. This is what lets AC #2's chaining requirement hold on the capture surface, and it is required for SYMMETRY: the two direct-append surfaces chain naturally (they catch), so without it the same substrate event would lose its traceback origin depending on which surface caught it. `model_config` gains `arbitrary_types_allowed=True` — a FIELD-TYPE permission that weakens neither `extra="forbid"` nor `frozen=True`; the model is never serialized (no `model_dump` / `model_dump_json` consumer exists, verified by direct search), and every consumer of a `FAILED` result raises immediately, so the retained traceback does not outlive the dispatch that produced it.

   **PROPAGATING WAS TRIED AND FALSIFIED AT THE BUILD, and the correction is recorded rather than absorbed.** The obvious shape — a narrow `except MemoryOperationIdempotencyConflictError` that re-raises past the broad handler, on the `_repair_capture_operation` precedent — **breaks a contracted outcome**. `_capture` has SIX public entry points, and `FAILED`-on-conflict is contracted for at least two of them by U-MEM-26 / Codex R6+R8: a divergent second run-start must be REPORTED rather than read as completion, and a non-run-start conflict *"must still surface as FAILED"* — both pinned by landed witnesses whose docstrings state that widening the catch would silently mask the divergence. The `_repair_capture_operation` precedent does **not** transfer: that method has ONE caller and no contracted FAILED semantics. A value-carried discriminator leaves every existing caller's control flow **byte-unchanged** while giving the executor the honest discriminator it lacked. **The closed two-value `MemoryCaptureStatus` enum is NOT widened.** The kind is a closed enum rather than a bool so a third failure kind is a type error at every consumer rather than a silent third meaning for `False`.

3. **(THREE executor surfaces, not one — and the scope widening is recorded, not smuggled.)** `[HIGH]` The register row named ONE (`_write_note`). Grounding found THREE, and the two it missed escaped **RAW** — the ledger's own type reaching `_classify_provider_exception` with no memory-family wrapper, where the catch-all routed it to the staircase. **Both were proven reachable BY EXECUTION before scope was fixed**, per the row's own close_out (*"a code-read inference is not sufficient for this row"*): `_append_standard_tool_call` (runs after EVERY successful standard tool call, so a read-only `memory.search` replay from another candidate reaches it with no `write_note` involved) and `_request_redaction`. Both key derivations are provider-BLIND while both payloads set `provider`. The two surfaces are realized DIFFERENTLY, and the asymmetry is structural rather than incidental: the **capture** surface reads `failure_kind` off the result (the refusal never reaches the executor as an exception — see item 2), while the two **direct appends** catch the ledger type at the call the executor itself makes. Route the direct pair through **ONE shared helper** rather than two inline `try` blocks — a second inline handler is a second place for the re-type to be forgotten when a third direct append is added, and AC #3 pins exactly that.

4. **(Classifier admission + waiver tuple, together.)** `[HIGH]` Admit the new type to `_classify_provider_exception`'s fail-fast `isinstance` tuple **BY NAME** (admission arms 6 → 7) AND to `_BREAKER_CHARGE_WAIVED_TYPES` (**4 → 5**). The two MUST move together: §14.6.3's classifier-consistency rule requires the guard's membership to equal the classifier's fail-fast admission, and adding to only one is silently wrong in a way no other witness in the module catches. **The store subtype is UNMOVED in both** — it keeps `io_failure` and keeps classifying `TRANSIENT_RETRY`, which is what makes this a split rather than a reclassification of the memory family. Update the tuple docstring's "four-type" wording, its store-subtype sentence (narrowed to the transient half), and the guard-site comment's "four" → "five".

### Acceptance

**#1 — The four-part determinism definition, witnessed at the LEDGER.** `[HIGH]` §14.6.3 row 6's condition is discharged by a conjunction of four properties, asserted against `append_memory_operation` DIRECTLY rather than through the executor: **(i) repeat-invariance** — the same conflicting append repeated N≥8 times yields exactly ONE distinct `(type, message)` outcome, with the ledger's own line count asserted unchanged so the single-outcome result cannot hold for the wrong reason; **(ii) candidate-independence** — third and fourth unrelated candidates meet the same refusal; **(iii) state-driven-not-stochastic** — re-presenting the ORIGIN candidate's payload returns `IDEMPOTENT_NOOP`, which is simultaneously the honest boundary and the positive control that stops (i) passing vacuously; **(iv) structural clock-exclusion** — the 18-field equivalence set is pinned BY NAME on both projection functions, plus a source-level assertion that neither reads `timestamp` or a clock and that both still read `provider`. The LEDGER placement is required, not incidental: determinism is a property of the ledger's comparison and must stay witnessed there whatever type the executor later wraps it in.

**#2 — All three executor surfaces, each EXECUTED, and all three CHAIN.** `[HIGH]` One witness per surface (capture / standard-tool-call / redaction), each driving a REAL executor over a real filesystem store and asserting the new type. **Every** surface must assert `__cause__` is the ledger exception — plus a JOINT witness over all three together, because the failure mode that actually occurred at this leg's first round was two surfaces chaining and one not: a per-surface witness passes happily in that world, and only the symmetry assertion catches it. The `failure_cause` invariant is separately witnessed in both directions.

**#3 — Partition completeness, asserted STRUCTURALLY.** `[HIGH]` A source-level assertion that the executor makes exactly ONE direct `self._store.append_memory_operation(` call — the one inside the shared helper. A fourth direct append added later would leak the raw ledger type back onto the staircase **silently**, because no behavioural test can cover a surface that does not exist yet. This is the shape a behavioural sweep structurally cannot deliver.

**#4 — The type-level partition witness, in FOUR directions.** `[HIGH]` The U-RT-152 3/25 raise-site partition precedent, adapted to a partition that is TYPE-level rather than site-level (the ledger has ONE raise site; the split is by disposition, not by count): **(1)** the conflict type fail-fasts AND is waived; **(2)** the store subtype is UNMOVED — still transient, still charging; **(3)** neither disposition arrived via the family base, asserted both behaviourally and as a type relation in BOTH directions (`not issubclass` each way); **(4)** guard and classifier agree — every waiver-tuple member classifies `None`, tuple length is 5, and the store subtype is absent. A one-sided assertion here would pass against a wholesale reclassification of the family, which is the error this witness exists to exclude.

**#5 — The C-MEM-19 residual, asserted as a DECLARATION-ABSENCE.** `[HIGH]` The new type must carry no `memory_failure_class` of its own (asserted over `vars()`, so an inherited value cannot satisfy it) and `classify_memory_failure` must report `provider_adapter_failure`; the store subtype's `io_failure` must be untouched. The C-MEM-19 classification-table row for this population MOVES to the new type with the new expected class, plus a WORDING-CONFLICTING sibling row so the absent declaration is not deletable-green.

**#6 — What the split actually buys, measured in durable bytes.** `[HIGH]` N conflicting attempts append N record JSONL lines, because `write_record` precedes the ledger append. The witness asserts the count directly. **The `B-84` W-5 cell-(3) `== 2` duplicate-line assertion is PRESERVED VERBATIM** — this leg closes the RETRY amplification (one duplicate instead of `max_attempts` duplicates), NOT the duplicate-record half, and weakening that assertion would claim a closure the leg did not deliver.

**#7 — Every landed witness the change touches is amended, not deleted.** `[HIGH]` The tuple-equality witness gains the fifth member and a stated second load (it now also kills a re-parenting under the store subtype); the family-refusal fixture set moves the new type to *waived* while base / denied / store stay refused; the store-error end-to-end staircase-charge control **STAYS with its assertions UNCHANGED** and its docstring narrowed to the transient-I/O half with the `B-132`-narrowed note; W-5 cell (3) INVERTS to fail-fast (and gains a store-subtype counterfactual); the U-MEM-28 store-error negative STAYS and gains a mirror asserting the fifth admission was by name and not by base-widening.

**#8 — PD-8 mutation probes, all confirmed RED then restored.** `[HIGH]` (a) narrow the tuple by the new member; (b) broaden the tuple to the memory family base; (c) de-list from the classifier while keeping the waiver (the consistency-rule probe); (d) collapse the capture-boundary discriminator so every `FAILED` reports `STORE_IO`; (e) re-parent the new type under `MemoryToolExecutionStoreError`; **(f) drop the `from` chain at the capture wrapper** — must fail BOTH the capture-surface witness and the symmetry witness; **(g) drop the `failure_cause` retention** — must fail loudly at the result model's own validator rather than silently producing an unchained raise. Each must fail a NAMED witness, and (c) / (e) / (f) must fail the consistency, residual and symmetry witnesses specifically.

**#9 — The contracted `FAILED`-on-conflict outcome is NOT disturbed.** `[HIGH]` The two U-MEM-26 witnesses that pin it — a divergent second run-start REPORTED rather than read as completion, and a non-run-start conflict still surfacing as `FAILED` with the conflict named in `failure_reason` — must pass **unmodified**. They are the reason the discriminator is a value rather than a propagated exception, and re-running them unchanged is the only thing that demonstrates the leg left the other five `_capture` entry points alone.

**Closure criterion (CONJUNCTIVE).** U-RT-153 closes when ALL of: ACs #1–#9 green with their mutation probes; the determinism witnesses green **before** the src change as well as after (they are ledger-level and must not depend on the split); the full Runtime and IS suites green with a programmatic collected-count reconciliation (the `B-117` silent-collection hazard: recount collected vs written, do not trust exit-green alone); `ruff` and `pyright` clean; and the register's `--check` green. **`B-115` flips to `closed` at this unit's merge; `B-132` is NARROWED, not closed.**

### Out of scope

- **Reading (a)** — provider joining the capture identity. It remains the registered residual on `B-115`'s successor framing: it is an identity-dimension change to a content-addressed `memory_id` and carries the full new-surface hash audit (does the id capture the new dimension; what happens to already-persisted records). NOT built, NOT re-priced here.
- **The duplicate-RECORD half.** `write_record` still precedes the ledger append, so one conflicting attempt still lands one extra physical line. Explicitly retained; see AC #6.
- **`B-132`'s remainder** — the denied class and the transient store I/O still charge at the staircase sites. Narrowed by this leg, not closed; any staircase-side waiver re-opens the `B-116` C1/C9-vs-C11 dyad on a new path and owes its own convening.
- **The dedicated C-MEM-19 `ledger_conflict` class** — forward row `B-134`.
- **`memory_promotion`'s decision append**, which the leg's caller survey found carries the SAME provider-blind-key / provider-in-payload shape and is reachable from the executor's promotion tool. Outside the three surfaces this leg's scope names; recorded in the partition witness's docstring as a remaining raw-escape path rather than silently omitted.
- **The dead half-open latch** (`B-118`). Inherited unchanged; the normative test this unit is adjudicated under still references a recovery path with zero production call sites.

---

## §2 DAG topology delta (v2.60 → v2.61)

One new unit; acyclic; **no cross-axis edge**:

```
U-RT-152 (landed — the B-116 guard + waiver tuple) ──▶ U-RT-153
```

U-RT-145 → U-RT-150 → U-RT-151 and U-RT-58 → U-RT-152 (all landed) are unchanged. The edge is real rather than nominal: U-RT-153 extends the tuple and the predicate U-RT-152 introduced, and its classifier-consistency witness asserts over both. No IS-axis edge is added despite the determinism witnesses living in `harness-is/tests` — `harness_runtime` → `harness_is` is a pre-existing package dependency (`memory_capture.py` already imports the ledger's exception type), and a test-side placement creates no plan-graph edge.

---

## §3 Sections preserved verbatim at v2.61

Every U-RT-* unit body other than the NEW U-RT-153; the v2.60 §1 U-RT-152 body and its closure criterion; the v2.60 §2 probe-text rider; all prior change-note blocks; every prior DAG statement. **No pre-existing unit body, dependency edge, acceptance criterion or verification line is removed or rewritten at this delta.**
