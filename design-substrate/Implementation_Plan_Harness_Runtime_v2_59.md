# Implementation Plan: Harness Runtime — v2.59 (delta over v2.58)

*v2.59 is the plan leg of register row **`B-111`**, operator-ratified **disposition (a)** on **2026-08-07**. It carries **ONE amendment site and ONE new unit**. The amendment site: **U-RT-150's AC #15** gains a **narrow qualifier** scoping its no-removal clause to the **SWEEP's payload-orphan accounting path**, so the record's **own publication path** may reclaim **its own** stale publication temporaries — the removal AC #15 as written forbids by **any** path, leaving the artifact reclaimable by **none**. The new unit: **U-RT-151**, the ~5-line prefix-scoped cleanup the qualifier makes legal, its witness, and the one deliberate re-pin of an existing witness's persistence assertion. **The Runtime SPEC is UNTOUCHED — v1.111 stands, and no spec delta is owed** (§0.4). **ZERO contract numbers minted, ZERO carriers retyped, ZERO fields added, ZERO `snapshot_hash` impact, ZERO cluster, ZERO cross-axis edge, ZERO CXA rows.** U-RT-145, U-RT-148, U-RT-149 and **every U-RT-150 acceptance criterion other than #15** are **PRESERVED VERBATIM**, and **U-RT-150 remains CLOSED** (§0.5).*

**Status:** Proposed

---

## §0 Change-note (v2.58 → v2.59)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_58.md` (v2.58 — the `B-96` spec leg's Runtime plan absorption; ONE new unit (U-RT-150), zero existing units amended). U-RT-150's **impl leg landed at PR #1237**, at which merge `B-96`, the `B-77` residual and `B-74` flipped to `closed`.

### §0.2 Revision context — the defect this delta corrects

`[HIGH]` `B-111` was surfaced **at U-RT-150's own impl leg** by out-of-family review round 2 [P2], against that leg's own code, and was **DECLINED with a grounded pin and registered rather than absorbed** — because the natural fix is **foreclosed by this plan's own AC #15**.

The record's publication path (`_publish_observation_record`, `harness-runtime/src/harness_runtime/lifecycle/protected_result_store.py:1282`–`:1340`) publishes by `tempfile.mkstemp(prefix=_GC_OBSERVATION_RECORD_TEMP_PREFIX)` (`:1327`) → write → `flush` → `fsync` (`:1329`–`:1332`) → `os.replace` (`:1333`), with an `except BaseException:` cleanup that unlinks its own temporary (`:1334`–`:1339`). A process **KILLED** strictly between the `mkstemp` and the `os.replace` runs **no** Python cleanup, so a `gc-observations.publishing-*` file survives. That prefix (`:142`) is **deliberately disjoint from BOTH sweep globs** (`_ENTRY_GLOB` / `_ORPHAN_GLOB`, `:150`–`:151`) — **AC #15's second half REQUIRES that disjointness**, for an independent and stronger reason — and nothing else in the store enumerates it. **So no path removes it.**

Two corrections to the registered framing, carried here because they change the argument rather than decorate it, both established at the row's **2026-08-07 grounding pass by direct read**:

- **The window is WIDER than registered.** The row's original *"sub-millisecond gap"* understates it: the gap at `:1329`–`:1332` is **`fsync`-INCLUSIVE**, so on a slow or contended volume it is a **durability-bounded interval**. Worse, it is **correlated** with the condition that provokes an external kill — a supervisor `SIGKILL`ing a process that appears hung on a slow mount lands **preferentially inside** it.
- **The harm is NARROWER than registered, and is stated against interest.** The *"accumulate with no bound"* framing overstates the cost: each leftover is **one record-sized file per killed sweep**, so exhausting a volume needs an implausible number of kills. **The real cost is ACCOUNTING INVISIBILITY** — the leftovers are invisible to term 8's gauge and to the `harness-inspect` counts, so an operator's orphan accounting silently **UNDER-REPORTS**.

**Net: reachability is HIGHER than registered and the harm is NARROWER than registered.** This delta therefore rests on **PLAN-TEXT CORRECTNESS**, not on severity — and that is the ground the operator ratified.

### §0.3 Why AC #15's clause is over-strong — the ratification's deciding argument

`[HIGH]` AC #15's mutation probe states that a sweep after a simulated mid-publication crash *"must not enumerate, report or remove it"*, and its witness (`test_record_publication_temporary_is_never_enumerated_as_a_payload_orphan`, `harness-runtime/tests/test_lifecycle_protected_result_store.py`) asserts exactly that the leftover **still exists** after a later sweep.

**The clause encodes a constraint STRONGER than its own stated reason.** AC #15 gives its reason in the same sentence, and the reason is entirely about **PAYLOAD classification**: an artifact carrying the payload-temp prefix would enter *"count and age accounting, being reported as a candidate, and being unlinked as though it were ciphertext, all while the final record name satisfies the disjointness check."* Every clause of that reason is about the artifact being **handled AS A PAYLOAD**. **None** of it is about the artifact surviving.

Read literally, though, the clause also forbids the **store's own publication path** from reclaiming its **own** prefix. Combined with the disjointness AC #15's first half **requires**, that literal reading is what makes the leftover reclaimable by **no path at all** — so AC #15, as written, does not merely fail to close `B-111`; **it is the sole reason `B-111` is open.** Because `_publish_observation_record` is reached only **from** `gc_sweep`, an impl leg building the cleanup under the current text would be absorbing a plan-level contradiction — precisely the silent-absorption failure mode X-AL-3 forbids, which is why the impl leg correctly declined and registered instead.

**Ratified disposition (a), operator, 2026-08-07:** narrow the clause to what it exists to protect. Disposition **(b)** (accept and document) is **NOT** selected. The two dispositions the row records as **not owed by any leg** remain not owed and are **not** taken here: **changing the temporary's prefix toward `.tmp-`** (AC #15 requires the disjointness for an independent and stronger reason) and **widening the sweep globs** (which would reintroduce exactly the unlink-as-ciphertext defect AC #15 exists to close).

### §0.4 Why NO spec delta is owed — determined by direct read, not assumed

`[HIGH]` Runtime spec **v1.111 §14.8.11.1** *"The observation record's carrier"* was re-read at session time. It commits the publication mechanism (*"temp-write + `fsync` + ATOMIC REPLACE + directory `fsync`"*), commits the lock scope (*"Published under the same locks the sweep already holds"*), and **explicitly acknowledges the orphan** — *"a failed write leaves only an orphan temporary file"* — as the reason **ABSENT** and **UNREADABLE** are the reachable loss states. It states **no** disposition for that orphan, and the record's *"file name and serialization format are implementation discretion per §14.8.11's deferred list."*

**The spec is therefore SILENT on the leftover's removal, not permissive-by-omission and not prohibitive.** The prohibition `B-111` runs into exists **only** in this plan's AC #15. The correction is consequently a **Phase-6 plan act** end to end: **`Spec_Harness_Runtime_v1.md` v1.111 is UNCHANGED**, no `C-RT-*` number is minted, no term is added to the twelve, and the does-NOT-acquire list is untouched. The cleanup rides the **ratified** lock scope verbatim — it needs no new lock and no new lock scope.

### §0.5 Why the qualifier is a PERMISSION and the obligation takes a NEW unit

`[HIGH]` **U-RT-150 is LANDED and CLOSED.** v2.58 §0.3 states the governing rule for exactly this situation — *"Amending a landed unit to carry that would make its closure criterion retroactively false and would obscure which obligations are new"* — and cites the **`B-97`(a) → U-RT-149** precedent: a change to an *already-shipped* artifact takes its own new unit rather than reopening the unit that built it.

This delta obeys that rule by **splitting the act in two**, which is why AC #15's qualifier is worded as a **MAY**:

- **The qualifier (§1) is a PERMISSION.** It **removes** a prohibition and **adds** no obligation. Code that does not exercise it satisfies the amended AC #15 exactly as it satisfies the current one, so **U-RT-150's conjunctive closure criterion remains TRUE as landed** and nothing shipped at PR #1237 becomes retroactively non-conforming. **This is the whole reason the permission and the obligation are not written into one criterion.**
- **The obligation (§2) is U-RT-151**, a new unit carrying the **MUST**, its witness, and the one deliberate re-pin the permission makes possible.

**Stated plainly so it is not discovered later:** the re-pin at U-RT-151 AC #2 **does** flip one assertion of an existing green witness. **The qualifier does not cause that flip — exercising it does**, which is exactly why the flip is owed by U-RT-151's acceptance surface and not smuggled in under U-RT-150's.

### §0.6 Cross-axis cascade — NONE, determined rather than assumed

**CXA: no delta owed.** This delta introduces **no cross-package consumption at all** — the publication path, the prefix constant, the locks and the witness module are all Runtime-owned and none crosses a package boundary. There is nothing to classify. `Cross_Axis_Composition_Document_v2_23.md` is **UNCHANGED**, aggregate **FROZEN at 111**.

**OD: UNCHANGED.** The cleanup adds **no emission of any kind** — no report-log line, no span, no metric instrument, no new observability namespace. The `C-OD-05` §5.1 fifteen-row roster is untouched (15 → 15). *(Determined by reading U-RT-150 AC #12's emission surface and confirming this delta adds nothing to it, not assumed from "small change".)*

**IS and AS: UNCHANGED** — the protected result store is Runtime-owned end to end. **CP: UNCHANGED** — `Spec_Control_Plane_v1_103.md` §1 row 6 / §14 / §18 and `Spec_Control_Plane_v1_112.md` §55 cross-reference §14.8.11 as the Runtime-owned definition site and never restate it, so no sibling text is stranded.

**No new package boundary is crossed. No DAG edge crosses an axis.**

### §0.7 What this delta does NOT do

- It does **NOT** amend the Runtime **spec**. v1.111 stands; **no** clearance marker for a spec version is filed by this arc.
- It does **NOT** amend U-RT-145, U-RT-148 or U-RT-149, or **any** U-RT-150 acceptance criterion other than **#15**. All are **PRESERVED VERBATIM**. U-RT-150's **closure criterion, rollback boundary and Tests paragraph are PRESERVED VERBATIM.**
- It does **NOT** touch AC #15's **first** half. The record's name stays **disjoint from both sweep globs** and **non-dot-leading**, both still asserted **directly and separately**.
- It does **NOT** weaken the payload-orphan semantics. **No glob widens**; a real `.tmp-*` orphan is enumerated, aged, gauged, reported and reclaimed exactly as before. **Nothing here authorizes any change to the `.tmp-*` class**, and U-RT-151 AC #3 asserts that non-change as a first-class criterion rather than assuming it.
- It does **NOT** change the temporary's prefix, and does **NOT** widen either sweep glob. Both are recorded at `B-111` as **not owed by any leg**, and both remain not owed.
- It does **NOT** authorize the publication path to remove **any** file outside `_GC_OBSERVATION_RECORD_TEMP_PREFIX`. The permission is **prefix-scoped by construction**, and U-RT-151 AC #1 asserts the scope refusal.
- It does **NOT** close `B-110` (the reused-temporary-name generation residual) or `B-108`. Neither is reached by this delta.
- It does **NOT** close `B-111`. `B-111` flips to `closed` **only** when **U-RT-151** merges; this leg flips it from `registered_finding` to **`open`** per the register's own status enum — ratified plus applied plan delta opens the row for code.
- It does **NOT** land code or tests. Impl is the follow-on arc, per the `B-33` / `B-39` / `B-59` / `B-69` / `B-70` / `B-72` / `B-96` / `B-97` / `B-107` precedent.

---

## §1 U-RT-150 AC #15 amendment — the narrow qualifier

**Unit ID:** U-RT-150 (**EXISTING — LANDED and CLOSED; ONE acceptance criterion qualified, not re-decomposed**)
**Spec anchors:** `Spec_Harness_Runtime_v1.md` v1.111 §14.8.11.1 *"The observation record's carrier"* — **UNCHANGED at this delta**.
**Prior scope preserved:** **AC #1 – #14 are PRESERVED VERBATIM.** AC #15's existing body is **PRESERVED VERBATIM** and the qualifier below is **APPENDED** to it; no word of AC #15 is retracted, reworded or reordered. The unit's **Files affected**, **Tests**, **Closure criterion** and **Rollback boundary** paragraphs are **PRESERVED VERBATIM**.

### §1.1 The appended qualifier

> **QUALIFIER (v2.59 — register row `B-111`, operator-ratified disposition (a), 2026-08-07). The no-removal clause above binds the SWEEP's payload-orphan accounting path; it does NOT bind the record's OWN publication path.** `[HIGH]` This AC's mutation probe — *"a sweep after a simulated mid-publication crash must not enumerate, report or remove it"* — states a constraint **stronger than the reason this AC gives for it**. The reason is entirely about **PAYLOAD classification**: an artifact carrying the payload-temp prefix would enter *"count and age accounting, being reported as a candidate, and being unlinked as though it were ciphertext."* Read literally, the clause **also** forbids the record's own publication path from reclaiming its **own** leftovers — which is not a property this AC exists to protect, and which, combined with the disjointness this AC's first half **requires**, leaves a leftover of a **killed** publication reclaimable by **no path at all** (register row `B-111`). The clause is therefore scoped, and **only** scoped, as follows.
>
> - **PRESERVED, UNQUALIFIED — the SWEEP half.** The **sweep** — the `_ENTRY_GLOB` / `_ORPHAN_GLOB` candidate enumeration and **everything downstream of it**: count and age accounting, AC #8's oldest-resident-candidate gauge at **both** surfaces, candidate reporting on **any** emission, and reclaim-as-ciphertext — **MUST NOT** enumerate, report, classify or remove the record or **any intermediate file of the record's own publication**, exactly as stated above. **No glob widens.** **The `.tmp-*` PAYLOAD-orphan semantics are BYTE-UNCHANGED** — a real payload orphan is enumerated, aged, gauged, reported and reclaimed exactly as before — and **nothing in this qualifier authorizes any change to that class.**
> - **PERMITTED, NEWLY — the record's OWN publication path.** The record's publication path **MAY** remove **stale leftovers of its OWN publication-temp prefix** (`_GC_OBSERVATION_RECORD_TEMP_PREFIX`), **scoped to that constant by construction** and performed **under the locks the publication already holds** — per §14.8.11.1's *"Published under the same locks the sweep already holds"*, so **no new lock and no new lock scope**. Such a removal is **not a sweep act**: it enumerates nothing into candidate accounting, emits nothing, and can reach **no** file outside its own prefix. **It is the ONLY removal channel this qualifier opens.**
>
> **This qualifier is a PERMISSION, not an obligation.** An implementation that never exercises it satisfies AC #15 exactly as before, so **U-RT-150's conjunctive closure criterion remains TRUE as landed at PR #1237** and nothing shipped there becomes retroactively non-conforming. The **obligation** to exercise it — and the one witness re-pin that exercising it makes necessary — is **U-RT-151** (§2). *(Ratified 2026-08-07 on PLAN-TEXT-CORRECTNESS grounds, not on severity: the AC's text encodes a constraint stronger than its own stated reason.)*

### §1.2 What the qualifier does NOT reach — stated so it is not over-read

`[HIGH]` **It does not license a second removal channel by analogy.** The permission names **one** constant and **one** path. It does **not** extend to the record file itself, to `_ENTRY_GLOB` or `_ORPHAN_GLOB` members, to any future intermediate artifact of a **different** publication, or to any "clean up what looks stale" generalization.

**It does not touch AC #15's first half.** Glob-disjointness and non-dot-leading remain **asserted directly and separately**; a single glob probe still cannot discharge this AC.

**It does not disturb AC #4 or AC #5.** Removing a leftover **publication temporary** is not the removal-then-name-reuse case AC #5 permits and `B-110` tracks: that case concerns a **candidate** name carried **in** the record, whereas the publication temporary is never a candidate of either class and never appears in the record's closed two-member content set. **`B-110` is neither closed nor widened by this qualifier.**

---

## §2 U-RT-151 — the record's own publication-temp cleanup (`B-111` disposition (a))

**Unit ID:** U-RT-151 (**NEW**)
**Spec anchors:** `Spec_Harness_Runtime_v1.md` v1.111 §14.8.11.1 *"The observation record's carrier"* (**UNCHANGED** — the section commits the publication mechanism and lock scope and explicitly acknowledges *"a failed write leaves only an orphan temporary file"*, while stating **no** disposition for that orphan; the disposition is a plan act per §0.4). Authority for the unit is **register row `B-111`**, operator-ratified **disposition (a)** 2026-08-07, and **U-RT-150 AC #15's qualifier** (§1.1), which makes the cleanup legal.
**Depends on:** [U-RT-150 (prior-landed — the unit that built the observation record and its publication path; this plan §1 / v2.58 §1)].
**Cluster:** none new — U-RT-151 joins the existing Runtime store cluster U-RT-145 and U-RT-150 belong to.

**Files affected (logical):** the protected-result-store module in `harness-runtime` (the record's publication path **only**); the store's existing witness module (one new witness plus **one** deliberate re-pin).

**Scale, stated so the unit is not over-built:** approximately **five lines** of production code — a prefix-scoped `iterdir`/`glob` + suppressed `unlink`, mirroring the shape `_publish_atomic` already uses for payload temporaries at `protected_result_store.py:857`–`:858` — plus its witnesses. **No new type, no new field, no new constant, no new emission, no new configuration, no migration.**

**Acceptance criteria:**

1. **(The cleanup — prefix-scoped BY CONSTRUCTION, under the locks already held.)** `[HIGH]` The record's publication path **MUST** remove **stale leftovers of `_GC_OBSERVATION_RECORD_TEMP_PREFIX`** — leftovers of a **prior, killed** publication — as part of a **later, successful** publication of the record, performed **under the locks the publication already holds** (no new lock, no new lock scope, no widening of the existing one). **Assert the scope refusals, do not assume them:** with the store root additionally holding a real `.tmp-*` payload orphan, an `*.entry` member, the record file itself, the cross-process lock file, and an unrelated arbitrarily-named file, a publication removes **exactly** the stale own-prefix leftovers and **nothing else** — asserted as an exact set, **not** as "the leftover is gone". **The path's own in-flight temporary MUST survive its own cleanup** — a cleanup that unlinks the temporary it is about to `os.replace` would reintroduce the unlink-then-recreate window §14.8.11.1 and AC #14(iii) forbid. *Mutation probes: broadening the scope from the prefix constant to the whole root must fail the exact-set assertion; removing the in-flight temporary must fail AC #14(iii)'s existing crash-atomicity witness.*

2. **(The leftover IS reclaimed by a LATER publication — and the SWEEP half is PRESERVED VERBATIM.)** `[HIGH]` `test_record_publication_temporary_is_never_enumerated_as_a_payload_orphan` is **re-pinned deliberately** — **not** weakened, **not** deleted, and **not** split — with its docstring updated to say what it now witnesses. **Exactly ONE of its assertion groups flips**, and the flip is stated here so the impl leg cannot reach a green suite by discovering it silently:
   - **FLIPS, to a POSITIVE witness:** the `(root / name).exists()` assertion — *"the sweep REMOVED the record's own publication temporary"* — becomes **the leftover IS removed, by a LATER PUBLICATION of the record**. The re-pin **MUST** attribute the removal to the publication path rather than merely observing the file's absence: a witness that only asserts absence would pass an implementation that widened a sweep glob, which is the defect AC #15 exists to close.
   - **PRESERVED VERBATIM:** the `not name.startswith(".tmp-")` prefix-disjointness assertion, **and** the *"the sweep REPORTED … as a candidate"* log assertion. Both are the SWEEP half AC #15's qualifier leaves unqualified, and **both must still hold at every sweep in the witness**, including the sweep that first observes the leftover.
   
   **A green suite reached by weakening or deleting either preserved assertion is an acceptance FAILURE.** *Mutation probes: reverting AC #1's cleanup must fail the flipped assertion; widening `_ORPHAN_GLOB` to match the record's temp prefix must fail the two preserved assertions **while** satisfying the flipped one — this probe is the one that discriminates the ratified fix from the disposition `B-111` records as **not owed by any leg**.*

3. **(The `.tmp-*` PAYLOAD-orphan semantics are BYTE-UNCHANGED — asserted, not assumed.)** `[HIGH]` In the **same** witness state as AC #1, a real `.tmp-*` payload orphan is **still** classified exactly as before: enumerated by the sweep, counted, carried by AC #8's oldest-resident-candidate gauge at **both** surfaces, reported as a candidate, and reclaimed once **both** AC #1-of-U-RT-150 conjuncts elapse — **and NOT reclaimed on the sweep that first observes it** (U-RT-150 AC #5's crash-orphan half). **This criterion is load-bearing and is not bookkeeping:** the cheapest wrong way to close `B-111` is to let the record's temp fall into the payload class, and an acceptance surface that asserted only "the leftover is gone" would accept it. *Mutation probe: routing the record's publication temporary through the payload-orphan class must fail this criterion **and** AC #2's preserved assertions together.*

4. **(No new surface — assert the absences.)** The cleanup emits **no** report-log line, **no** span and **no** metric instrument, mints **no** observability namespace, adds **no** configuration key, and creates **no** new file or directory. **A cleanup failure MUST NOT fail the publication**: an `OSError` on the removal is suppressed and the publication proceeds, matching the store's existing best-effort removal posture (`protected_result_store.py:821`–`:837`) — **but MUST NOT be swallowed in a way that suppresses a failure of the `os.replace` itself.** *Mutation probes: emitting on this path must fail; letting a removal `OSError` propagate out of the publication must fail; broadening the suppression to cover the `os.replace` must fail AC #14(iii)'s existing crash-atomicity witness.*

**Tests (every witness mutation-probed per Workflow v1.18 PD-8):** the AC #1–#4 witnesses, homed in the store's existing witness module alongside the re-pinned AC #2 witness. **Verification shape:** AC #2's *"removed by a LATER publication"* half MUST be exercised as a **real second publication against the same store root** with the leftover present beforehand — not as a direct call to the cleanup helper, which would leave the wired-but-unreachable failure mode open (the leftover is only reclaimed if the **publication** actually reaches the cleanup).

**Closure criterion (CONJUNCTIVE).** U-RT-151 closes when **all** of: AC #1–#4 are green with their mutation probes; the AC #2 re-pin is complete with **neither** preserved assertion weakened or deleted **and** the flipped assertion attributing removal to the publication path; and no sweep glob, no prefix constant and no `.tmp-*` classification has changed. Only at that merge does **`B-111`** flip to `closed`.

**Rollback boundary:** revert the cleanup and restore the AC #2 witness's original `exists()` assertion; the store reverts to leaving killed-publication leftovers unreclaimable and `B-111` reopens as filed. **U-RT-150 AC #15's qualifier does NOT revert with it** — it is a permission, and the store is conforming with or without the cleanup.

---

## §3 DAG topology delta (v2.58 → v2.59)

One new unit; acyclic; **no cross-axis edge**:

```
U-RT-145 (landed) ──▶ U-RT-150 (landed) ──▶ U-RT-151
```

**One new edge:** U-RT-150 → U-RT-151. No existing edge is added, removed or retargeted. U-RT-151 has no dependents at this revision.

---

## §4 Spec-traceability

| Spec surface (v1.111 — **UNCHANGED at this delta**) | Unit |
|---|---|
| §14.8.11.1 *"The observation record's carrier"* — publication mechanism + lock scope + the acknowledged *"orphan temporary file"* whose disposition the spec leaves unstated | U-RT-150 AC #15 **as qualified** (§1.1); U-RT-151 AC #1 |
| §14.8.11.1 term 5 (both candidate classes) + terms 1/8 (conjunctive reclaim; the gauge over both classes) — **the `.tmp-*` class's semantics, asserted UNCHANGED** | U-RT-151 AC #3 |
| §14.8.11.1 term 12 (emission surface — no new namespace, no span, no metric) | U-RT-151 AC #4 |
| §14.8.11.1 *"NOT unlink-then-recreate"* | U-RT-150 AC #14(iii) — **PRESERVED VERBATIM**; U-RT-151 AC #1 + AC #4 assert the cleanup does not reopen that window |
| §14.8.11's amended bounded-retention bullet | U-RT-145 AC #7 — **PRESERVED VERBATIM, still true** |

**Register-traceability:** `B-111` (this delta's authority) ← the qualifier at §1.1 + U-RT-151. `B-110` — **neither closed nor widened** (§1.2). `B-96` / `B-77` residual / `B-74` — **closed at PR #1237, UNCHANGED**.

---

## §5 Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Implementation_Plan_Harness_Runtime_v2_59.md` |
| Version | v2.59 (delta over v2.58) |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_58.md` |
| Absorbs | **NOTHING** — no spec delta exists to absorb. `Spec_Harness_Runtime_v1.md` **v1.111 is UNCHANGED** (§0.4) |
| Trigger | Register row **`B-111`**, operator-ratified **disposition (a)** 2026-08-07 (narrow AC #15's no-removal clause, then build the prefix-scoped cleanup); grounded at the row's 2026-08-07 window-correction pass |
| Unit-count change | **+1** — ONE new unit (U-RT-151); **ONE existing unit qualified at ONE acceptance criterion** (U-RT-150 AC #15) |
| Cluster-count change | None |
| DAG topology change | **One new edge:** U-RT-150 → U-RT-151. No existing edge touched |
| Cross-axis cascade | **None** — CXA v2.23 **UNCHANGED**, aggregate frozen at 111; OD / IS / AS / CP **UNCHANGED** (`C-OD-05` §5.1 roster 15 → 15) |
| Acceptance-criteria change | **U-RT-150: FIFTEEN stay FIFTEEN** — none added, none removed, one **qualified by appended text with nothing retracted**; AC #1–#14, the Tests paragraph, the closure criterion and the rollback boundary **PRESERVED VERBATIM**. **U-RT-151: FOUR, all new.** U-RT-145 / U-RT-148 / U-RT-149 **PRESERVED VERBATIM** |
| Carrier / hash impact | **NONE.** No schema, envelope, record content set, prefix constant, glob or hash input changes. The record's closed two-member content set is untouched |
| Landed-unit discipline | **U-RT-150 remains CLOSED.** The qualifier is a **PERMISSION** and cannot retroactively falsify a conjunctive closure criterion; the **MUST** lives at the new unit, per the `B-97`(a) → U-RT-149 precedent v2.58 §0.3 cites (§0.5) |
| Known witness flip | **ONE, declared rather than discovered:** `test_record_publication_temporary_is_never_enumerated_as_a_payload_orphan`'s `exists()` assertion flips to a positive *removed-by-a-later-publication* witness at **U-RT-151 AC #2**. Its two other assertion groups (prefix-disjointness; not-reported) are **PRESERVED VERBATIM**. **The qualifier does not cause the flip — exercising it does** |
| Co-published (this arc) | The `B-111` register row + its prose home (**status `registered_finding` → `open`** per the register's own status enum — ratified plus applied plan delta opens the row for code; `closed` waits on U-RT-151); this plan's clearance marker; workspace `CLAUDE.md` §2.4 pointer bump + `.harness/claude-artifact-pointers.md` lineage row |
| Impl leg | **NOT bundled** — code + tests land as a separate follow-on arc (U-RT-151). `B-111` closes **only** at that merge |
| Skill discipline | `implementation-planner` Phase-7 revision pass applying an **operator-ratified register disposition** to plan text. Fidelity-pure; **NO spec amendment**; NO contract addition; NO existing-unit re-decomposition; NO blanket zero-cascade claim (§0.6 determines each axis by reading it) |
| Date | 2026-08-07 |
