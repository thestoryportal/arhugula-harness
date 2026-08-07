# Implementation Plan — Information Substrate (IS axis) — v2.9

*Delta over v2.8. v2.9 is the IS-axis plan leg of the RATIFIED **`B-57` Class 2 fork** (`.harness/class_2_fork_b57_direct_append_writer_owned_opt_in.md` — **operator-ratified 2026-08-07, Reading A**, recorded at that filing's §11), absorbing **IS spec v1.13** (NEW **C-IS-07 §7.6.1** — per-call-site writer-owned timestamp ELECTION on DIRECT append surfaces, extending the EXISTING §7.6; plus the §7.6 residual-status paragraph and the §7.1 row-7 cross-reference clause). The amendment is homed at **ONE EXISTING unit — U-IS-11** (the C3-pole append-only write contract, `Implements: C-IS-07 §7.1, §7.3, §7.6`, the unit owning `append_ledger_entry` at `harness_is.state_ledger_write`) — **ZERO new atomic units, ZERO new nodes, ZERO new edges, ZERO new auxiliary types** (the shape `B-100` and `B-88` both used). This delta additionally carries the **PER-SITE CLASSIFICATION TABLE** that IS spec v1.13 §7.6.1 deliberately routes to the plan rather than the contract (*"this contract states the RULE, the plan states the ROSTER"*) — re-grounded by direct read at HEAD `acfc1afa`, with two of the filing's own count claims CORRECTED rather than carried. IS 0-outbound preserved: the amendment adds NO dependency on any U-CP-\* / U-RT-\* unit. **SPEC-LEG ONLY** — the call-site conversions, the two injection-caveat resolutions and the two-process contention witness are the separate impl leg. v2.8 + earlier PRESERVED VERBATIM per delta-only-plan-chain convention.*

**Status:** Proposed

---

## §0 Change-note (v2.8 → v2.9)

### §0.1 Predecessor

`Implementation_Plan_Information_Substrate_v2_8.md` (v2.8 — the `B-33-A` spec-leg apply; NEW U-IS-20 `rotation_correlation_id` carrier unit). U-IS-20 is **untouched** by this delta.

### §0.2 Revision scope (v2.8 → v2.9)

v2.9 absorbs **IS spec v1.13 C-IS-07 §7.6.1** into the ONE existing unit that owns the write contract. `append_ledger_entry`'s sentinel substitution is already unconditional in landed code, so the impl work this delta scopes is **not "build writer-owned sampling for direct surfaces"** — it is *"stop forbidding, at named call sites, what the writer already does"*, plus the witnesses that prove the default did **not** move for everyone else.

| In scope at v2.9 | Out of scope |
|---|---|
| U-IS-11 amendment — ACs #14–#20 (with #14-bis): the per-call-site ELECTION authorization, the eligibility rule, the demonstrable default-preservation property, per-site table conformance, the two injection-caveat resolutions, the DEFER site, and the `shadow_git_rollback` `restored_at` decoupling pin (IS spec v1.13 §7.6.1) | All v2.8 / v2.7 / v2.6 / earlier unit bodies — preserved verbatim per §0.3 (U-IS-11 ACs #1–#13 included) |
| The **per-site classification table** (§2.1 below) — 14 rows, ELECT / ELECT-with-injection-caveat / RETAIN / DEFER, re-grounded by direct read at HEAD `acfc1afa` | Widening `_CLOCK_SKEW_TOLERANCE` or adding a configuration surface for it — `B-112` step (3); NOT reached (§0.6), and its own back-flow if ever reached |
| The **live council re-determination trigger** (§0.6) — a RETAIN verdict on either injection-caveat site reopens the C3 ⊥ C11 question BEFORE any tolerance change is authored | Any writer-side "mode", per-producer flag, path gate or configuration by which election could become ambient — NOT authorized by §7.6.1 |
| DAG delta: NONE. Coverage-matrix delta: +1 row (C-IS-07 §7.6.1) | The event-time contract at `as_is_wiring.py:129` — RETAINS caller-supplied semantics; an out-of-order refusal there is the honest outcome by design, not a defect to engineer away |

### §0.3 Sections preserved verbatim from v2.8

| Section | Status at v2.9 |
|---|---|
| §0 (v2.8 change-note) | Superseded by this §0 (historical record preserved at v2.8) |
| §1 Spec inventory | Refreshed: IS spec canonical at HEAD is **v1.13**; every contract row is byte-unchanged per the v1.13 PRESERVED-VERBATIM list — only the NEW §7.6.1 is new surface (the §7.6 residual-status paragraph and the §7.1 row-7 clause are, respectively, a status record and a cross-reference, neither introducing coverage-owed surface) |
| §2 — U-IS-01..U-IS-10, U-IS-12..U-IS-17, U-IS-18 (RETIRED), U-IS-19, U-IS-20 | **PRESERVED VERBATIM** from v2.8 §2 and earlier (delta-only-plan-chain convention) |
| §2 — U-IS-11 ACs #1–#13 | **PRESERVED VERBATIM** (the v2.1 baseline body ACs #1–#10; the v2.7 B-48 additions ACs #11–#13). v2.9 appends #14–#20 (with #14-bis) and leaves every prior AC's text untouched |
| §3 Dependency graph | UNCHANGED — U-IS-11's edges `[U-IS-05, U-IS-07, U-IS-08, U-IS-09]` are unchanged; zero new nodes, zero new edges, IS 0-outbound preserved |
| §4 Coverage matrix | Revised: +1 row (C-IS-07 §7.6.1); all other rows preserved verbatim |
| §5 Auxiliary-type carrier audit | UNCHANGED — v2.9 introduces no auxiliary record type (the election reuses the EXISTING `WRITER_OWNED_TIMESTAMP` constant; no new type, no new API surface) |

### §0.4 Authority chain — no further operator gate

v2.9 absorbs a spec amendment authored in the SAME leg as this plan delta (IS spec v1.12 → v1.13). The ONE operator decision the arc surfaced — Reading A (per-call-site opt-in) vs Reading B (HOLD until an observed production refusal) — is **ALREADY TAKEN** (2026-08-07, Reading A, recorded at the fork's §11). No FURTHER gate is owed at the plan layer: §7.6.1 fully specifies the election, its eligibility rule and its does-NOT-authorize list, and this delta performs the mechanical acceptance-criterion decomposition, exactly as v2.7 did for IS spec v1.11 §7.6. **ZERO X-AL-3 risk** — spec + plan land together in this arc with a clearance marker each, per workspace `CLAUDE.md` §4.5.

**One decision this delta deliberately does NOT pin.** The two injection-caveat sites (§2.1 rows 12–13) are resolved **at the impl leg, per site, explicitly** — AC #18 requires the decision and its rationale to be recorded, and forbids absorbing it silently. That is implementation discretion the fork itself scoped (*"the spec leg must decide, per site, between (a) electing and retiring the injection seam's timestamp role, or (b) retaining caller-supplied semantics and keeping determinism"*), routed here rather than to the contract because both options conform to §7.6.1 — the choice is a test-determinism-vs-availability trade at a named call site, not a contract question. **What is NOT discretionary is the consequence:** a RETAIN verdict on either site fires the §0.6 council trigger.

### §0.5 Status posture

`Status: Proposed` (pending P6-CK / decorrelated-review clearance). Clearance marker owed at `.harness/clearance/implementation-plan-information-substrate-v2-9-cleared-2026-08-07.md` per workspace `CLAUDE.md` §4.5, filed in the same PR as the IS spec v1.13 clearance marker. No sibling plan co-publication at this leg — the classified call sites live in `harness-cp` and `harness-runtime`, but **no CP or Runtime plan delta is owed**: the election changes no CP/Runtime contract, adds no unit and declares no edge; each converted site is a one-line change against the C-IS-07 §7.1 write contract those sites already consume (the same "no cross-package consumption, so nothing to classify" determination `B-97`(a) reached for CXA).

### §0.6 Council — probe-resolved at this leg, with a LIVE re-determination trigger

`B-112`'s `council` field conditions convening on reaching **step (3)** — widening `_CLOCK_SKEW_TOLERANCE`, which would trade information-substrate integrity (**C3**) against operator-loop robustness (**C11**) across every ledger writer at once — and step (3) is reached only if step (2) leaves an **exposed caller that cannot adopt** writer-owned sampling.

**Re-determined at this leg from the §2.1 table, not inherited from the filing.** Exactly ONE row RETAINS caller-supplied semantics: `as_is_wiring.py:129` (`timestamp=composed.timestamp`), which carries genuine **event time** passed through from an upstream composed record. That site is not a caller that *cannot* adopt while exposed to contention — it is a caller for which an out-of-order refusal is the honest outcome **by design**, exactly as §7.6.1's eligibility rule frames it. No exposed caller is stranded ⟹ step (3) is never reached ⟹ the C3 ⊥ C11 tension does not arise. Recorded **surfaced + probe-resolved** per root `CLAUDE.md` §10.9 posture amendment 5, with the §2.1 classification sweep as the resolving probe; amendment 1's nameable-tension discriminator fails, and convening a dyad whose triggering condition is unmet is the primary-collapse failure those amendments exist to prevent.

> **LIVE TRIGGER (binds the impl leg, not this one).** If the impl leg's per-site resolution judges **either** injection-caveat site (§2.1 rows 12–13) **RETAIN**, that verdict produces an exposed direct caller that must keep caller-supplied semantics — precisely the shape step (3) tests for — and **this determination MUST be re-run, and the C3 ⊥ C11 dyad convened, BEFORE any `_CLOCK_SKEW_TOLERANCE` change is authored.** The trigger is recorded here so it is checkable, not recalled.

---

## §1 Spec inventory

PRESERVED VERBATIM from v2.8 §1, **plus** the NEW §7.6.1 contract surface:

| Contract | Version | Status at v2.9 |
|---|---|---|
| C-IS-05 §5 (six-field shape) / §5.1–§5.6 (sidecars + resolver + store) | IS spec v1.13 (byte-unchanged from v1.12 per the v1.13 PRESERVED-VERBATIM list) | Covered at prior units; unchanged. §7.6.1 adds no field and changes no shape — only which instant a consenting call site records |
| C-IS-06 §6 hash-chain | IS spec v1.13 | UNCHANGED — construction, canonicalization and the `timestamp` field's hash participation are all untouched; ZERO migration surface, ZERO `snapshot_hash` delta |
| C-IS-07 §7.1 row 7 ("Timestamp authority") | IS spec v1.13 (cross-reference clause added) | Covered at U-IS-11 (already). The v1.13 clause names §7.6.1 and carries ZERO new semantics — no additional coverage is owed for it |
| C-IS-07 §7.6 (writer-owned drain-path timestamp authority) + residual-status paragraph | IS spec v1.13 (paragraphs preserved verbatim; ONE status paragraph added) | Covered at U-IS-11 (AMENDED at v2.7, ACs #11–#13, unchanged here) |
| **C-IS-07 §7.6.1 (per-call-site writer-owned ELECTION on DIRECT append surfaces)** | **IS spec v1.13 (NEW)** | **Covered at U-IS-11 (AMENDED this arc — ACs #14–#20 (with #14-bis))** |
| C-IS-07 §7.7 (rotation-correlation read-side invariants) | IS spec v1.13 | UNCHANGED — covered at U-IS-20 |

---

## §2 U-IS-11 AMENDMENT — per-call-site writer-owned election on DIRECT append surfaces (IS spec v1.13 §7.6.1)

The v2.1-baseline U-IS-11 body (`append_ledger_entry` + `EntryPayload`/`WriteKey`/`WriteResult`, ACs #1–#10) and the v2.7 B-48 additions (ACs #11–#13 + their witnesses) are **PRESERVED VERBATIM**; v2.9 adds:

**Implements (addition):** + C-IS-07 §7.6.1 (NEW at IS spec v1.13 — per-call-site writer-owned timestamp election on DIRECT append surfaces).

**Depends on (unchanged):** `[U-IS-05, U-IS-07, U-IS-08, U-IS-09]` — NO new edges; NO cross-axis outbound edge (IS 0-outbound preserved). The converting call sites live in `harness-cp` and `harness-runtime` and consume the C-IS-07 §7.1 write contract they already import; the conversion declares no new dependency in either direction.

### §2.1 Per-site classification table (the ROSTER §7.6.1 routes here)

**Grounding provenance — read this before trusting a line number.** Every row below was re-resolved **by direct read at HEAD `acfc1afa`** at this plan leg; every cited CODE LINE re-read byte-identical to what the fork filing's §3(ii) table recorded (the MODULE PATHS below are the filing's own §9-item-1 corrected ones, and several rows carry annotation the filing's table does not). **Line numbers drift and this table WILL go stale** — the impl arc MUST re-resolve each row **by content** (the `timestamp=` expression and its meaning), never by the cite alone, and record any drift rather than silently normalizing it. The MODULE PATHS below are the corrected ones (the filing's §9 item 1 records five inbound path errors; the corrected paths are used here).

| # | Site (path re-verified at `acfc1afa`) | Timestamp expression | Meaning | Disposition |
|---|---|---|---|---|
| 1 | `harness-is/src/harness_is/shadow_git_rollback.py:141` | `timestamp=now` (`now = datetime.now(UTC)` at `:93`) | when appended | **ELECT** |
| 2 | `harness-cp/src/harness_cp/pause_resume_protocol.py:1103` | `timestamp=datetime.now(UTC)` | when appended | **ELECT** |
| 3 | `harness-cp/src/harness_cp/pause_resume_protocol.py:1190` | `timestamp=datetime.now(UTC)` | when appended | **ELECT** |
| 4 | `harness-cp/src/harness_cp/pause_resume_protocol.py:1294` | `timestamp=datetime.now(UTC)` | when appended | **ELECT** |
| 5 | `harness-cp/src/harness_cp/workflow_driver.py:6074` | `timestamp=datetime.now(UTC)` (appends to `ctx.ledger_writer` at `:6082` — a genuine DIRECT append, re-verified in context) | when appended | **ELECT** |
| 6 | `harness-cp/src/harness_cp/workflow_driver.py:6297` | `timestamp=datetime.now(UTC)` (post-join synthesis; appends to `ctx.ledger_writer` at `:6305`) | when appended | **ELECT** |
| 7 | `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py:337` | `timestamp=datetime.now(UTC)` | when appended | **ELECT** |
| 8 | `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:290` | `timestamp=datetime.now(UTC)` | when appended | **ELECT** |
| 9 | `harness-cp/src/harness_cp/per_step_override_evaluator.py:489` | `timestamp=timestamp` (parameter; its caller samples `datetime.now(UTC)` at `:523` — the ELECTION is expressed at the SAMPLING caller `:523`, not at the pass-through `:489`) | when appended | **ELECT** |
| 10 | `harness-cp/src/harness_cp/sibling_ledger_entry_composition.py:163` | `timestamp=timestamp` (parameter, threaded from `cp_is_wiring.py:124` → `:151`) | when appended | **DEFER** — production-UNREACHABLE (§2.2) |
| 11 | `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:1566` | `timestamp=datetime.now(UTC)` | when appended | **ELECT** |
| 12 | `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py:701` (+ the resample-retry re-stamp at `:751`) | `timestamp=self.time_source()` — an **INJECTED** source (`:294`, defaulted at `:1639` to `lambda: datetime.now(UTC)`) | when appended | **ELECT — with the injection caveat (AC #18)** |
| 13 | `harness-runtime/src/harness_runtime/lifecycle/cost_attribution_f2_write.py:157` | `timestamp=time_source()` — an **INJECTED** source (`:74`, same default inline) | when appended | **ELECT — with the injection caveat (AC #18)** |
| 14 | `harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py:129` | `timestamp=composed.timestamp` | **EVENT time** — passed through from an upstream composed record | **RETAIN caller-supplied** |

**Counts, recomputed at this leg — and TWO filing count claims CORRECTED rather than carried** (`[[count-claims-drift-every-review-round]]`). The table is **14 rows**: **10 ELECT** (rows 1–9, 11) + **2 ELECT-with-injection-caveat** (rows 12–13) + **1 RETAIN** (row 14) + **1 DEFER** (row 10) = 14. ✓

1. The filing's *"Fourteen rows, twelve SITES"* (§3(ii)) **does not reconcile with its own table**. Its stated justification — that `audit_writer` contributes a primary plus its resample retry, and `per_step_override_evaluator` contributes the composer plus its sampling caller — describes a fold that is **ALREADY PERFORMED** inside rows 12 and 9 as the filing prints them. Deducting the same two companions twice is what produces "twelve"; the number appears to be residue from an earlier draft. **By content at HEAD the classification table is 14 rows**, and that is what this plan carries.
2. The filing's ELECT disposition is priced at *"≈8 conversions"* in prose (and *"~8 one-line conversions"* at its §4/§7 cost lines) while its **own ELECT cell enumerates TEN payload-construction rows**. The corrected figure is **10 ELECT rows**, plus 2 rows pending the AC #18 per-site resolution — i.e. **10 conversions committed, up to 12 depending on the injection-caveat verdicts**.

**Neither correction changes any disposition, any reading, or any cost line that matters** (contract numbers, hash, CXA and new-unit counts are all still ZERO). It changes the **SIZE of the surface the impl leg must convert** — which is precisely what a re-grounding pass owes, and is recorded here rather than silently normalized.

### §2.2 Why row 10 DEFERS — measured, not assumed

`sibling_ledger_entry_composition.py:163` receives its `timestamp` as a parameter, threaded from `RuntimeCpIsWiring.emit_sibling_ledger_entry` (`harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py:124`, passing on at `:151`). An independent sweep re-run at this leg over `harness-{is,as,cp,od,cxa,core,runtime}` + `tools`, `.py` only, excluding `.venv` / `__pycache__` / `.codex-worktrees` / `.claude/worktrees`, returns **19 hits for `emit_sibling_ledger_entry`, of which exactly 3 are non-test**: the definition at `cp_is_wiring.py:124` and two docstring mentions (`cp_is_wiring.py:34`, `sibling_ledger_entry_composition.py:150`). **Every call site is a test.** The seam is wired but not driven at HEAD, so it cannot contend at runtime and converting it would be speculative work against an unreached path. Per §7.6.1, *"a site whose classification is DEFERRED because it has no production caller acquires no election by default; it is re-classified when a real producer appears."*

### §2.3 Acceptance criteria (v2.9 additions; #1–#13 preserved verbatim)

14. **(§7.6.1 "The contract" — the ELECTION.)** A DIRECT-append call site MAY elect writer-owned sampling by supplying the EXISTING `WRITER_OWNED_TIMESTAMP` sentinel as its write payload's `timestamp`; on an electing call the persisted `timestamp` is sampled by the writer INSIDE the write serialization point, so on that call sampling order equals physical-append order and C-IS-05 §5 monotonicity holds by construction. **NO new API surface is introduced at `append_ledger_entry`**: no mode parameter, no writer flag, no path discriminator, no dedicated entry point, no configuration key. The landed sentinel substitution IS the carrier. An implementation that adds a writer-side mode to express election is an acceptance FAILURE — §7.6.1 authorizes a per-call-site election only, and a mode is the ambient form it explicitly forecloses.

14-bis. **(Prose-carrier refresh — the OTHER half of the restriction §7.6.1 replaces.)** The direct-path restriction §7.6.1 supersedes was carried by **TWO** prose surfaces, not one: §7.6's `"Surfaces that do NOT change"` paragraph (refreshed at the spec leg by the v1.13 residual-status paragraph) **and the shipped sentinel docstring at `harness-is/src/harness_is/state_ledger_write.py:78`–`:80`** — *"Every DIRECT append path keeps caller-supplied timestamp semantics verbatim — this sentinel is opt-in per entry, never a default."* Its first clause is already imprecise under §7.6.1 and becomes flagrantly false once the ELECT conversions land. The impl arc MUST refresh that docstring to state the v1.13 contract (the election is per call site and never a default; a NON-electing direct append keeps caller-supplied semantics byte-verbatim), citing §7.6.1. Leaving it is a stale-carry acceptance FAILURE — recorded here rather than left to be rediscovered, because a named-but-unowned prose carrier is exactly how stale-carry survives an arc that was watching for it.

15. **(§7.6.1 default preservation — the NEGATIVE property, demonstrable.)** For every NON-electing direct producer the §7.6 `"Surfaces that do NOT change"` paragraph holds BYTE-VERBATIM: the persisted `timestamp` **IS** the caller-supplied value, and an inversion on a non-electing direct path still raises `NonMonotonicTimestampError` beyond clock-skew tolerance. AC #9 and AC #13 stand unchanged for these producers. This property MUST be demonstrated **negatively by a witness** (below), not asserted: if it cannot be demonstrated, the election has silently become a default and the amendment is violated. A change that makes any non-electing producer's persisted timestamp writer-owned is an acceptance FAILURE.

16. **(§7.6.1 eligibility rule — the contract obligation.)** A call site MAY elect ONLY where its entry's `timestamp` means *when the entry was appended*. Where it means *when the event happened*, caller-supplied semantics are REQUIRED and an out-of-order refusal is the honest outcome. Concretely at this arc: `as_is_wiring.py:129` (row 14) carries event time passed through from an upstream composed record and **MUST NOT** elect; a witness pins that its persisted timestamp remains the composed record's own value. Electing on an event-time path to silence a refusal is a contract violation regardless of whether the code accepts it (the writer's sentinel check is unconditional and cannot make this distinction — the contract must).

17. **(Per-site table conformance — the audit surface.)** The impl arc converts **exactly** the rows §2.1 classifies ELECT, having first re-resolved each row **by content** at the arc's own HEAD. A conversion at a site the table does not classify ELECT, or a missed ELECT row, is an acceptance FAILURE. Any row whose cite or expression has drifted since `acfc1afa` is **re-stamped and the drift recorded** at the impl PR, never silently normalized; any site NEWLY appearing in the tree that constructs a direct-append `timestamp` is classified before the arc closes, or explicitly recorded as unclassified-and-why.

18. **(The injection caveat — rows 12–13, resolved EXPLICITLY per site.)** `audit_writer.py:701`/`:751` and `cost_attribution_f2_write.py:157` sample an **INJECTED** `time_source` (`audit_writer.py:294`, defaulted at `:1639`; `cost_attribution_f2_write.py:74`), a seam that exists so tests can pin a deterministic instant. Stamping the sentinel **OVERRIDES that injection** — the writer substitutes its own sample regardless — so any test asserting a pinned ledger timestamp on those paths breaks and the seam's timestamp role goes partially inert. The impl arc MUST decide **per site, and record the decision with its rationale at the impl PR**: (a) **ELECT**, retiring the injection seam's timestamp role for the ledger append and updating the affected determinism tests; or (b) **RETAIN** caller-supplied semantics, keeping determinism. Absorbing this silently — converting without recording, or skipping without recording — is an acceptance FAILURE. **If EITHER site is resolved RETAIN, the §0.6 council trigger FIRES**: the C3 ⊥ C11 re-determination is owed before any `_CLOCK_SKEW_TOLERANCE` work is authored.

19. **(`audit_writer` resample-retry disposition — pinned either way.)** `audit_writer.py:727`–`:752`'s bounded 5-attempt resample-retry loop exists to recover from exactly the refusal §7.6.1 addresses (its own comment is tagged *"codex round-8 P1"*). Under an ELECT verdict at row 12 the loop becomes **unreachable at that site** — the refusal it catches can no longer fire there — and the arc MUST take that simplification deliberately (remove it, with the removal witnessed) rather than leave dead code. Under a RETAIN verdict the loop is **retained deliberately** and the reason recorded. Either way the disposition is **stated**, not left implicit — an untouched loop with no recorded verdict is an acceptance FAILURE.

20. **(`shadow_git_rollback` `restored_at` decoupling — pinned, not discovered.)** Row 1's `now` (`:93`) is shared with **three** `RollbackResult.restored_at` returns — `:98` (`CHECKPOINT_NOT_FOUND`), `:125` (`ROLLBACK_FAILED`) and `:151` (`RESTORED`). **Only `:151` is affected**: `:98` and `:125` are early returns that fire BEFORE the `append_ledger_entry` call at `:135`–`:141`, so on those paths no ledger entry is written and there is nothing to decouple from. Electing at `:141` **decouples** the returned `restored_at` from the persisted ledger timestamp: `restored_at` keeps the caller-sampled instant, while the ledger entry carries the writer's. This is witness-visible and semantically harmless — the two now honestly mean different things (*when the rollback completed* vs *when the entry was appended*) — but it MUST be pinned by an explicit assertion and a code comment, so a later reader does not read the divergence as a defect. A conversion that leaves the two silently divergent with no pin is an acceptance FAILURE.

**Recorded limit (NOT an acceptance criterion — no witness is owed for it here).** Election is **not refusal immunity**. The direct surface's population is MIXED by design (electing and non-electing producers coexist on one ledger — that mixture is precisely what preserves the default for non-electing producers), so an electing append can still be refused if a preceding NON-electing producer persisted a future-skewed caller-supplied timestamp. Election removes the electing site's exposure to **its own** sample-then-lose-the-race inversion — the whole of `B-57`'s named failure — not its exposure to another producer's clock. Stated at IS spec v1.13 §7.6.1 and recorded here so the impl leg's two-process witness is scoped to the former and a later reader does not price the arc against the latter.

### §2.4 Tests (v2.9 additions — mutation-probed per PD-8)

- **Two-process contention witness (the load-bearing one):** `test_electing_direct_append_survives_lock_race_overtake` — two OS processes contend on one ledger root; the waiter that sampled FIRST but acquires SECOND, having ELECTED, is **not** refused, and both entries persist with non-decreasing timestamps in physical-append order. This is the direct analogue of `B-112`'s 12/20 two-process repro. **Mutation probe: revert the election at the site under test (restore the caller-sampled expression) → the witness must FAIL with `NonMonotonicTimestampError`.** A green test with no demonstrated red under reversion is not a witness (`[[mutation-probe-load-bearing-witness]]`). Run it enough times to make the race non-vacuous, and assert the *lock/ordering identity* rather than a timing threshold (`[[verification-shape-sharpened-grep-vs-e2e]]`).
- **Non-electing default-preservation NEGATIVE witness (AC #15):** `test_non_electing_direct_append_keeps_caller_supplied_semantics` — a direct append that does NOT stamp the sentinel persists the caller's own value **and** still raises `NonMonotonicTimestampError` on an inversion. **Mutation probe: make writer-owned sampling unconditional on the direct path → this witness must FAIL.** This is the witness that proves the election did not become a default; without it, AC #15 is unverified.
- **Event-time preservation control (AC #16):** `test_as_is_wiring_event_time_append_is_not_writer_owned` — the `as_is_wiring` path's persisted timestamp IS the upstream composed record's value, unchanged. **Mutation probe: elect at row 14 → this witness must FAIL** (it is the guard against a blanket sweep converting an event-time site).
- **Per-site conformance check (AC #17):** an arc-time assertion (test or CI check) that the set of call sites stamping `WRITER_OWNED_TIMESTAMP` on a DIRECT surface equals the §2.1 ELECT set, so a later drive-by conversion cannot slip in unclassified. **Mutation probe: elect at an unclassified site → the check must FAIL.**
- **Injection-caveat witness (AC #18), shape follows the verdict:** under ELECT — a witness that the injected `time_source` no longer determines the persisted ledger timestamp at that site, and the affected determinism tests are updated (not deleted) to assert what they still legitimately pin; under RETAIN — a witness that the injected source DOES still determine it. Either way the verdict is asserted, not assumed.
- **`audit_writer` retry-loop disposition witness (AC #19):** under ELECT — a witness that the refusal path is unreachable at that site and the loop is gone; under RETAIN — a witness that the bounded loop still recovers and still exhausts loudly at 5 attempts.
- **`restored_at` decoupling pin (AC #20):** `test_rollback_restored_at_decoupled_from_persisted_ledger_timestamp` — asserts both values explicitly and asserts they are permitted to differ.

**Note (implementation discretion — NOT pinned by the planner).** Whether an electing call site imports `WRITER_OWNED_TIMESTAMP` directly or via an existing re-export; whether a shared helper expresses the election at the several `pause_resume_protocol` rows; the concrete shape of the AC #17 conformance check (a test vs a CI grep-check vs an overlay query). What is NOT discretionary: no writer-side mode (AC #14), no silent injection-caveat absorption (AC #18), no unrecorded retry-loop disposition (AC #19), and no conversion outside the §2.1 ELECT set (AC #17).

**Rollback boundary (addition).** Revert the elections; every converted site regresses to caller-sampled outside-lock capture and the `B-57` refusal reopens at each of them. The contract does not need reverting for the code to be safe — a non-electing tree is exactly the v1.12 behaviour, which is why the rollback is per-site and needs no coordinated migration.

---

## §3 Dependency graph delta

**NONE.** U-IS-11's within-axis edges are unchanged (`[U-IS-05, U-IS-07, U-IS-08, U-IS-09]`); ZERO new nodes; ZERO new edges; ZERO new auxiliary types. IS 0-outbound preserved (Kahn-trivially acyclic — the amendment adds no edge in either direction). The converting call sites in `harness-cp` / `harness-runtime` consume the C-IS-07 §7.1 write contract they already import, so **no cross-axis edge is created or owed on either side** — and, for the same reason, **no CXA row is owed** at `Cross_Axis_Composition_Document_v2_23.md` §2.3 (no new package edge, no new typed seam; the `B-97`(a) / `B-88` disposition, determined here rather than assumed).

---

## §4 Coverage matrix delta

| Spec contract | Atomic unit |
|---|---|
| IS spec v1.13 C-IS-07 §7.6.1 (per-call-site writer-owned ELECTION on DIRECT append surfaces; eligibility rule; demonstrable default preservation; the per-site roster carried at this plan) | **U-IS-11 (AMENDED)** |

All other rows PRESERVED VERBATIM from v2.8 §4. ZERO contract-coverage gap at the IS axis. (The §7.1 row-7 cross-reference clause and the §7.6 residual-status paragraph add no coverage-owed surface — the first carries zero new semantics, the second is a status record over text preserved verbatim.)

---

## §5 Auxiliary-type carrier audit

UNCHANGED from v2.8 §5 — v2.9 introduces no auxiliary record type. The election reuses the EXISTING `WRITER_OWNED_TIMESTAMP` constant already exported from `harness_is.state_ledger_write`; no new type is authored and no carrier-home question arises.

---

## §6 Filing footer

| Field | Value |
|---|---|
| Plan version | v2.9 (delta over v2.8) |
| Authored at | Phase 7 — `B-57` spec leg (2026-08-07) |
| Authoring authority | IS spec v1.13 (C-IS-07 §7.6.1, `Spec_Information_Substrate_v1.md`) + `.harness/class_2_fork_b57_direct_append_writer_owned_opt_in.md` (**RATIFIED 2026-08-07 — Reading A**, §11) |
| Net delta | ONE amended unit (U-IS-11 — ACs #14–#20 (with #14-bis) + the §2.1 per-site classification table + witnesses); ZERO new units; ZERO new nodes; ZERO new edges; ZERO new auxiliary types; +1 coverage row (C-IS-07 §7.6.1); ZERO IS-outbound edge (preserved); ZERO CXA rows |
| Grounding | Every §2.1 row re-resolved by direct read at HEAD `acfc1afa`; the `emit_sibling_ledger_entry` reachability sweep re-run independently; two filing count claims corrected at §2.1 |
| Siblings (same arc) | None — SPEC-LEG ONLY (the impl leg is a separate, not-yet-opened PR, mirroring `B-33-A` / `B-59-A`) |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
