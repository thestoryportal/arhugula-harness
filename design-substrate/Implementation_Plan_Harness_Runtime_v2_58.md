# Implementation Plan: Harness Runtime — v2.58 (delta over v2.57)

*v2.58 is the Runtime plan leg of register row **`B-96`**'s spec leg, absorbing **Runtime spec v1.110 → v1.111** (THREE amendment sites inside §14.8.11: the NEW **§14.8.11.1** carrying the ratified `B-96` **Reading C / form C-2** reclaim grace as TWELVE contract terms, plus two strict appends — the bounded-retention bullet's cross-reference and the deferred-to-discretion list's two new entries). **ONE NEW unit — U-RT-150** — carries the whole grace: the durable observation record, the conjunctive reclaim rule, the two falsifiability surfaces, and the witness pass over every grace-dependent test the change inverts. **ZERO existing units amended; ZERO new cluster; ZERO cross-axis edge.** This is the SPEC LEG's plan absorption only — impl (code + tests) is a separate follow-on arc per the `B-33` / `B-39` / `B-59` / `B-69` / `B-70` / `B-72` / `B-97` / `B-107` precedent.*

**Status:** Proposed

---

## §0 Change-note (v2.57 → v2.58)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_57.md` (v2.57 — the `B-100` spec leg's Runtime plan absorption; ONE amended unit (U-RT-148), zero new units).

### §0.2 Revision context

Runtime spec **v1.111 §14.8.11.1** replaces the protected result store's **sweep-COUNT** reclaim grace with a **DURABLE, publication-bounded, elapsed-TIME first-observation grace**. Reclaim becomes **CONJUNCTIVE**: past-TTL filesystem age **AND** past-TTL elapsed time since a **durably recorded** first observation, **with no third reclaim path**. The observation state must survive process exit, so a one-shot `harness run` shape accumulates real elapsed time across invocations rather than resetting the grace at every bootstrap.

The ratified form is fixed and this plan may not drift from it: `first_observed_at` is **WALL-CLOCK**, sampled at the **locked, post-re-verification observation point**; the carrier is **(C-i)**, a dedicated **candidate-filename + timestamp** record keyed over **BOTH** sweep classes; publication is **temp-write + `fsync` + atomic replace + directory `fsync`**, explicitly **NOT** the write-once no-replace primitive; record absence reads as **no observation**; and there is **NO absolute `k × ttl_seconds` ceiling** (form **C-2**).

Provenance: `.harness/class_2_fork_b96_gc_grace_elapsed_time_bound.md` (FILED PR #1179; operator-ratified **Reading C** 2026-08-05, recorded at its `§11 RATIFICATION`) + `.harness/council-b96-grace-ceiling-2026-08-01.md` (PR #1183; ceiling sub-decision resolved **C-2**, unanimous C3 + C10 + C7).

### §0.3 Why a NEW unit rather than an amendment of U-RT-145

`[HIGH]` **U-RT-145** (`Implementation_Plan_Harness_Runtime_v2_51.md` §1.1) is the unit that materialized §14.8.11's protected result store, and it is **landed**. Its **AC #7** states the bounded-retention contract at the altitude v1.103 stated it — *idempotent retrieval; ack-gated deletion; a deployment-configurable TTL; GC sweeps at bootstrap / shutdown and a periodic-or-opportunistic runtime sweep; a typed expiry report line* — and **every clause of AC #7 remains TRUE and UNCHANGED under v1.111**. §14.8.11.1 does not contradict AC #7; it adds a **reclaim rule** AC #7 never stated, together with a **new durable artifact**, a **new operator-facing read surface**, and a **witness inversion** on tests that are green today.

Amending a landed unit to carry that would make its closure criterion retroactively false and would obscure which obligations are new. The **`B-97`(a) → U-RT-149** precedent applies directly: a keying + migration change to the *already-shipped* pause journal took its own new unit rather than reopening the unit that built the journal. **U-RT-150 follows it.** U-RT-145's acceptance criteria and closure criterion are **PRESERVED VERBATIM**.

### §0.4 Cross-axis cascade — NONE, determined rather than assumed

**CXA: no delta owed.** The cross-spec probe run at the council record's adversarial pass found `Spec_Control_Plane_v1_103.md` §1 row 6 and §14 / §18, `Spec_Control_Plane_v1_112.md` §55, and Runtime plans v2.51 / v2.56 all **cross-reference** §14.8.11 as the **Runtime-owned definition site** and never restate it — so no sibling text is stranded by this amendment. `Cross_Axis_Composition_Document_v2_23.md` is **UNCHANGED**, aggregate **FROZEN at 111**.

**OD: UNCHANGED.** Every emission §14.8.11.1 owes rides the **typed report-log line §14.8.11 already names** — not spans, not metrics. **No new observability namespace is minted and the `C-OD-05` §5.1 fifteen-row roster is untouched** (spec v1.111 §14.8.11.1 term 12). **IS and AS: UNCHANGED** — the store is Runtime-owned end to end.

**No new package boundary is crossed.** The observation record lives in the store root the Runtime already owns; the inspection extension lands on the Runtime-owned `harness-inspect` admin CLI.

### §0.5 What this delta does NOT do

- It does **NOT** amend U-RT-145, U-RT-148 or U-RT-149, or any other existing unit. All are **PRESERVED VERBATIM**.
- It does **NOT** add a cluster, and it adds **no cross-axis edge**.
- It does **NOT** authorize an absolute reclaim ceiling, a numeric `k`, a `ttl_seconds` floor, a narrowing of `ttl_seconds`, a hard periodic-sweep requirement, a fourth reordering of the publication path's two-stamp pipeline, or carriers **(C-ii)** / **(C-iii)**. Each is **explicitly not owed by any leg** per the ratification.
- It does **NOT** land code or tests. Impl is the follow-on arc.
- It does **NOT** re-litigate the ratified reading. **Reading A** (retain the sweep-COUNT bound) and **Reading B** (per-process elapsed time) are settled — B is retired explicitly at spec term 10, and this plan's AC #10 witnesses that retirement rather than re-arguing it.
- It does **NOT** close `B-96`, the `B-77` residual or `B-74`. All three flip to `closed` **only when U-RT-150 merges**.

### §0.6 A flag this plan carries forward rather than absorbs

`[HIGH]` **FIVE of the spec's twelve terms (#5, #6, #8, #11, #12) are EXPANSIONS beyond the fork's §8 ratification ask** — flagged at the council record's §7.2 and restated in the spec leg's clearance marker. Their claim to ride the Reading-C ratification is that they are **conditions of the selected form**: form C-2's retention statement rests on the observation record being present and readable, so a contract stating C-2 without stating what happens when that premise fails is incomplete. **This plan builds them as spec'd.** If the operator judges they owe a fresh decision, that is a **Class 2** routing against the spec leg, and U-RT-150's ACs #5, #6, #8, #11 and #12 are the ones it would reach.

---

## §1 U-RT-150 — durable, publication-bounded, elapsed-time GC reclaim grace (v1.111 §14.8.11.1)

**Unit ID:** U-RT-150 (**NEW**)
**Spec anchors:** `Spec_Harness_Runtime_v1.md` v1.111 **§14.8.11.1** (terms 1–12, the observation record's carrier, and the does-NOT-acquire list); §14.8.11's bounded-retention bullet as amended.
**Depends on:** [U-RT-145 (prior-landed — the protected post-effect result store this unit's sweep belongs to; Runtime plan v2.51 §1.1)].
**Cluster:** none new — U-RT-150 joins the existing Runtime store cluster U-RT-145 belongs to.

**Files affected (logical):** the protected-result-store module in `harness-runtime` (the sweep body, the observation point, the reclaim predicate, the new record read/write path); the Runtime-owned `harness-inspect` admin CLI (an **extension of the existing store row**, not a new subcommand — the §13.7 pause-journal enumeration row is the shape precedent, not a dependency); the store's existing witness module (the grace-dependent tests this change inverts).

**Acceptance criteria:**

1. **(Conjunctive reclaim rule; no third path.)** An unacknowledged entry is reclaimed **iff BOTH** its filesystem-timestamp-derived age is past the TTL **AND** the elapsed time since its **durably recorded** `first_observed_at` is past the TTL. **Assert the absence of a third path**, not merely that the conjunction works: no code path reclaims on age alone, on a ceiling, or on any `k × ttl_seconds` term. *Mutation probe: relaxing the predicate to either conjunct alone must fail a witness.*

2. **(Publication bound, witnessed.)** For an entry published at `t_pub`, **no reclaim occurs before `t_pub + TTL`**, across an arbitrary number of sweeps and independent of the entry's recorded filesystem timestamp — including the case where that timestamp **under-reports** publication (the crash-window shape `B-77` / `B-74` name). *Mutation probe: sampling the first observation before the existence re-verification, or reintroducing a mtime-only reclaim path, must fail this witness.*

3. **(Sampling point — wall-clock, under the lock, post-re-verification.)** `first_observed_at` is a **wall-clock** value sampled at the **locked observation point after the candidate's existence has been re-verified**, **never** at the sweep's pre-enumeration clock read. Assert **by construction** — the recorded value must not be obtainable from the pre-enumeration read. The sweep's injectable clock seam is extended so a witness can drive both points independently and prove they are distinct. *Mutation probe: moving the sample to the pre-enumeration read must fail AC #2's witness.*

4. **(Derived index, fail-safe direction.)** With the observation record **deleted** between two sweeps, a past-TTL entry is **NOT** reclaimed at the next sweep — a fresh grace begins. Assert the direction as a property: **no record state can shorten retention**; record loss can only lengthen it. *Mutation probe: treating an absent record as "observed long ago" must fail.*

5. **(CLOSED content set, keyed on the candidate filename over BOTH sweep classes.)** The record's content is exactly `{candidate filename, first_observed_at}` per name — **closed at two members** — keyed on the candidate filename, over **BOTH** the published-entry class **AND** the publication path's temporary-file crash-orphan class. **Assert the refusals:** the persisted bytes contain **no composite key / `result_ref` in whole or in part, no tenant tag, no plaintext, no ciphertext** — a known sentinel written through the store is absent from the raw record bytes and from their base64 / utf-8 decodings. **Assert the crash-orphan half explicitly:** an orphan is **NOT** reclaimed on the sweep that first observes it, **AND** is reclaimed on a later sweep once its own grace elapses — the two halves together are what term 5 exists to guarantee, and a witness asserting only the first would pass a never-reclaim implementation. *Mutation probe: restricting the record's key to the published-entry class must fail the crash-orphan half.*

6. **(Reset emitted as an OBSERVED FACT, never a diagnosis.)** When a sweep finds one or more past-TTL candidates **and reads no observation record**, it emits a typed report-log line carrying: *no observation record was read*; the **count** of past-TTL candidates **over both classes**; the **oldest resident candidate's age** from the same timestamp pass; and that a **fresh grace begins**. **Assert the MUST-NOTs:** the line does **not** assert, name or classify the record as **LOST**, and emits **no** verdict. Emission is **unconditional and per-occurrence** — assert it fires on the **first** occurrence with no in-process suppression and no wait for a second. *Mutation probe: adding a "record lost" classification, or suppressing the first occurrence, must fail.*

7. **(Retention is CONDITIONAL — assert the absence of an unconditional claim.)** Witness the typical worst case — `2 × TTL` plus up to two sweep-trigger intervals — **and** witness that no surface, emission, docstring or CLI output asserts an unconditional `N × TTL` bound. **The negative half is load-bearing:** an implementation that ships a correct reclaim rule and an overclaiming docstring violates term 7. *Mutation probe: reintroducing an unconditional bound statement anywhere on the surface must fail.*

8. **(Falsifiable at TWO surfaces.)** **(a)** The **oldest resident candidate's age** is a **field of** every sweep's report-log emission — the reclaim line and the AC #6 / AC #11 lines — never a separate line, and **computed at read time, never cached between sweeps**. **(b)** A **read-only, sweep-free extension of the existing `harness-inspect` store row** reports that same age **and** the observation record's own state **THREE-WAY: present-and-readable / absent / present-but-unreadable**. **(b) engages only when the store root exists**, leaving output **byte-unchanged** otherwise, adds **zero persistence**, and **states in its own output what it cannot tell** — that the value is a read-time snapshot and that the presence of candidates does not imply a sweep will run. **Assert that (b) emits NO bound, NO threshold and NO pass/fail verdict**, and that the **record-absent** reading is presented as *either a first-cutover store or a repeating record-loss loop, indistinguishable at this surface* — an attribution here would reproduce AC #6's defect one surface over. **The `harness-inspect` read-only invariant is preserved: (b) writes nothing and creates nothing.** **Plus** the **which-reclaim-term-fired-last** discriminator — the later of AC #1's two conjunct deadlines, **derived at the reclaim site, never stored** — as an **attribute of the reclaim emission**. *Mutation probes: caching the age across sweeps must fail; making (b) emit a verdict must fail; making (b) create the store root must fail the read-only invariant.*

9. **(Record lifecycle — replace-not-accumulate, over the union.)** The record is **replaced wholesale** at each sweep over the **union of both candidate classes**; names no longer resident are **dropped**. Witness that a long-lived store's record does **not** grow without bound as entries come and go — including across a completed publication whose temporary name drops out. *Mutation probe: accumulating rather than replacing must fail.*

10. **(Per-process elapsed time is RETIRED — the one-shot shape is the witness.)** Across **N successive one-shot process invocations** against the same store root, a genuinely expired entry **IS** eventually reclaimed, because the grace clock **accumulates across process exits**. **This is the criterion that discriminates the ratified form from the retired Reading B**, and it is unbuildable without durability. *Mutation probe: holding the observation state in process-local memory only must fail this witness — the entry is never reclaimed.*

11. **(Unreadable / invalid record reads as NO OBSERVATION, TOTALLY — and emits a FAULT.)** A record that exists but is **truncated, corrupted, or written in an incompatible form** reads as **no observation for EVERY name** — **never partial trust** of rows that happen to parse. Witness a record whose rows are individually well-formed but whose whole is invalid, and assert **no name** is treated as observed. The emission is discriminated as **record present but unreadable** and **MAY be classified as a fault**, unlike AC #6. *Mutation probe: trusting the parseable subset must fail — a row carrying an earlier-than-truth `first_observed_at` shortens retention, the direction AC #4 forbids.*

12. **(Emission surface — carrier, content, cardinality, redaction.)** Every emission this unit adds rides the **typed report-log line** the store already uses — **assert NO span is emitted and NO metric instrument is created**, and that **no new observability namespace appears**. **Content:** the candidate filename of either class MAY appear; the composite key MUST NOT appear in **any** emission; the AC #6 / AC #11 emissions **decrypt nothing** and therefore carry **no tenant identity**. **Cardinality:** a candidate filename may appear in an emission **body** but is **never a dimension or label of an aggregate**. **Redaction:** assert the implementation does **not** rely on the `PersonaTier` span-processor gradient reaching this carrier — it does not. *Mutation probe: emitting the composite key on any of these lines must fail; decrypting an entry to tag the reset line must fail.*

13. **(The witness pass over the inverted grace-dependent tests — a first-class obligation, not cleanup.)** `[HIGH]` The store's existing witness module reaches reclaim by **two sweeps at a pinned or near-identical clock**, which the elapsed-time rule no longer admits. **Every** grace-dependent witness and **every** reclaim assertion in that module is re-grounded against the new rule — the shared past-the-grace sweep helper and each reclaim assertion that pins a reclaimed-name list — and each is **re-pinned deliberately**, with its comment updated to say what it now witnesses. **The `B-74` pin flips from "the live entry is reclaimed" to "the live entry SURVIVES both sweeps" exactly as its own in-file comment instructs**, and is **re-pinned as a POSITIVE witness** rather than deleted. **A green suite reached by weakening or deleting a witness is an acceptance FAILURE**; each flipped assertion carries its own mutation probe.

14. **(New witnesses for the three properties in-process state cannot have.)** **(i)** **Cross-process survival** — the grace persists across process exit (AC #10's shape, asserted directly on the record). **(ii)** **Bounded reclaim** — an expired entry IS reclaimed once both conjuncts elapse, so the grace does not become a never-reclaim rule. **(iii)** **Crash-atomicity of the record's own publication** — interrupting the record write after the temp write and before the atomic replace leaves the **previous** record intact and readable, never an absent or half-written one; and the record is published by **temp-write + `fsync` + atomic replace + directory `fsync`**, **never** the write-once no-replace primitive and **never** unlink-then-recreate. *Mutation probes: using the no-replace primitive freezes the record at its first snapshot and must fail (ii); unlink-then-recreate opens an absent window and must fail (iii).*

15. **(The record's carrier is disjoint and non-dot-leading.)** The record is a **dedicated file in the store root** whose name is **disjoint from BOTH sweep globs** — asserted, not assumed, so the sweep can never enumerate its own record as a candidate — and, per the council record's impl-leg routing, **SHOULD NOT be dot-leading**, closing the dotfile-skipping copy channel that is one of the two ways the record is lost while the entries survive. *Mutation probe: naming the record so a sweep glob matches it must fail.*

**Tests (every witness mutation-probed per Workflow v1.18 PD-8):** the AC #1–#15 witnesses above, homed in the store's existing witness module alongside the re-grounded pass at AC #13. **Verification shape:** AC #10 and AC #14(i) MUST be exercised as **real successive process invocations against one store root**, never as an in-process simulation — the durability property is exactly what an in-process test cannot see, and the wired-but-unreachable failure mode is the one this arc exists to close.

**Closure criterion (CONJUNCTIVE).** U-RT-150 closes when **all** of: AC #1–#15 are green with their mutation probes; the AC #13 re-grounding pass is complete with **no** witness weakened or deleted; and the `B-74` pin is **re-pinned as a positive live-entry-survives witness**. Only at that merge do `B-96`, the `B-77` residual and `B-74` flip to `closed`.

**Rollback boundary:** revert the observation record, the conjunctive predicate and the inspection extension; the store reverts to the sweep-COUNT grace and the `B-96` / `B-77`-residual / `B-74` defect class reopens as filed. **The AC #13 witness flips revert with it** — they are not independently landable, because they assert the new rule.

---

## §2 DAG topology delta (v2.57 → v2.58)

One new unit; acyclic; **no cross-axis edge**:

```
U-RT-145 (landed) ──▶ U-RT-150
```

No existing edge is added, removed or retargeted. U-RT-150 has no dependents at this revision.

---

## §3 Spec-traceability

| Spec surface (v1.111) | Unit |
|---|---|
| §14.8.11.1 terms 1–4 (conjunctive rule; publication bound; sampling point; derived index) | U-RT-150 AC #1–#4 |
| §14.8.11.1 term 5 (closed content set; both candidate classes) | U-RT-150 AC #5 |
| §14.8.11.1 terms 6–7 (reset-as-fact emission; conditional retention) | U-RT-150 AC #6–#7 |
| §14.8.11.1 term 8 (two falsifiability surfaces; the three-way record state) | U-RT-150 AC #8 |
| §14.8.11.1 terms 9–12 (record lifecycle; Reading B retired; unreadable-as-fault; emission surface) | U-RT-150 AC #9–#12 |
| §14.8.11.1 *"The observation record's carrier"* | U-RT-150 AC #14(iii), #15 |
| §14.8.11's amended bounded-retention bullet (unchanged terms) | U-RT-145 AC #7 — **PRESERVED VERBATIM, still true** |

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Implementation_Plan_Harness_Runtime_v2_58.md` |
| Version | v2.58 (delta over v2.57) |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_57.md` |
| Absorbs | `Spec_Harness_Runtime_v1.md` v1.111 §14.8.11.1 (terms 1–12 + carrier + does-NOT-acquire list) |
| Trigger | Register row `B-96`, RATIFIED 2026-08-05 as **Reading C, ceiling form C-2**; fork `.harness/class_2_fork_b96_gc_grace_elapsed_time_bound.md` (PR #1179) + council record `.harness/council-b96-grace-ceiling-2026-08-01.md` (PR #1183) |
| Unit-count change | **+1** — ONE new unit (U-RT-150); **zero existing units amended** |
| Cluster-count change | None |
| DAG topology change | **One new edge:** U-RT-145 → U-RT-150. No existing edge touched |
| Cross-axis cascade | **None** — CXA v2.23 **UNCHANGED**, aggregate frozen at 111; OD / IS / AS **UNCHANGED** (`C-OD-05` §5.1 roster 15 → 15) |
| Acceptance-criteria change | **U-RT-150: FIFTEEN, all new.** U-RT-145 / U-RT-148 / U-RT-149 **PRESERVED VERBATIM** |
| Carrier / hash impact | **NONE** on any existing carrier. The observation record is a **NEW durable artifact** in the store root; no existing schema, envelope or hash input changes |
| Co-published (this arc) | `Spec_Harness_Runtime_v1.md` v1.111; two clearance markers; the `B-96` register row + its prose home (**status UNCHANGED at `design_substrate_gated`** — the impl leg is still owed); the fork filing's chain cross-stamp; workspace `CLAUDE.md` §2.3 / §2.4 pointer bumps |
| Impl leg | **NOT bundled** — code + tests land as a separate follow-on arc. `B-96`, the `B-77` residual and `B-74` close **only** at that merge |
| Expansion flag carried | **FIVE of the twelve spec terms (#5, #6, #8, #11, #12) are EXPANSIONS beyond the fork's §8 ask** (council record §7.2). Surfaced in this leg's clearance marker; a fresh operator decision on them would be a **Class 2** routing reaching AC #5 / #6 / #8 / #11 / #12 |
| Skill discipline | `implementation-planner` Phase-7 revision-pass absorbing upstream Runtime spec v1.111 into ONE new unit; fidelity-pure; NO contract addition beyond the spec; NO existing-unit re-decomposition; NO blanket zero-cascade claim |
| Date | 2026-08-05 |
