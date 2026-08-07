# Class 2 Fork — B-57 / B-112: direct-append surfaces are locked to caller-supplied timestamps under a zero-tolerance monotonicity check, while the deadline'd-lock mechanism makes out-of-order arrival live

**Status: FILED 2026-08-07, awaiting operator ratification.** Doc-only filing per the workspace
codex-context-guard rule (fork FILINGS ship doc-only FIRST; no `design-substrate/**` edit rides this
PR). Chain mirrors `B-88`'s, `B-107`'s and `B-97`(a)'s: **filing (this PR) → operator ratification →
spec leg (IS spec v1.12 → v1.13 + clearance + IS plan v2.8 → v2.9) → impl leg (~8 one-line
conversions + the two-process witness).**

**Register rows.** TWO, cross-linked and both `registered_finding` at
`.harness/forward-register.yaml`:

- **`B-57`** — *Direct-writer caller-supplied timestamp capture-order inversion* — the **REMEDY
  OWNER**. Its close-out already prescribes the route this filing prices: *"a narrow IS spec delta
  extending section 7.6's writer-owned sampling to an opt-in direct-append mode (or per-writer
  serialization guidance) + U-IS-11 widening."* Its materialization condition — *"IF the direct-path
  inversion materializes in practice"* — was moved from VERIFIED-DORMANT to **PARTIALLY MET** on
  2026-08-06 (recorded at PR #1241).
- **`B-112`** — *Deadline'd lock polling drops kernel handoff fairness…* — the **CAUSE-AND-EVIDENCE
  RECORD** (`pr: #1241`), which explicitly **DEFERS the adoption question to `B-57`**.

**Neither row's status flips at this PR.** Both stay `registered_finding`; the `pr:` pointers and any
status change ride the **ratification** leg, per the `B-88` precedent. The two ratified row mints
that ship in this same PR (`B-115`, `B-116`) are **unrelated to this fork** — they carry separately
ratified findings and are filed here only for PR economy.

**Grounding HEAD.** `73b0e87b`. Every `§`/line cite below was re-resolved **by direct read at this
HEAD**, and every count was recomputed programmatically. **The recorded line numbers were NOT
trusted**: three module PATHS in the inbound grounding notes were wrong, one line cite drifted by
three lines, and one inventory site turned out to have **zero production callers**. All five are
recorded at §9 rather than silently normalized, and the corrected values are used throughout.

**What this filing does NOT do.** It does not re-litigate the B-48 ratified narrow scope, the B-93
lock deadline, or the `WRITER_OWNED_TIMESTAMP` carrier choice. Those are LANDED and treated as
settled. It decides one thing: **whether C-IS-07 §7.6's writer-owned sampling becomes available to
DIRECT append surfaces as a per-call-site opt-in.**

---

## §1 The question, and what carries it

A **direct** state-ledger append — the default `append_ledger_entry` contract — samples its
`timestamp` in the CALLER, outside the write serialization point, and the writer then validates it
against PHYSICAL APPEND ORDER with **zero** clock-skew tolerance. Two uncoordinated concurrent direct
writers can therefore sample in one order and physically append in the opposite order, and the later
arrival is **refused**, not reordered.

**The three facts that make this a fork rather than an impl task.** `[HIGH]`

1. **The contract pins it.** `Spec_Information_Substrate_v1.md` §7.6 *"Surfaces that do NOT change"*
   (`:776`) keeps **every** direct append on caller-supplied semantics **verbatim**, and its
   **registered residual** (`:778`) states the extension in the exact words that make it back-flow:

   > *"Extending writer-owned authority to direct surfaces would change caller-supplied semantics for
   > every existing direct producer and **requires its own back-flow**; it is registered here as a
   > surfaced finding, not silently absorbed."*

   The same section's deferred-to-discretion paragraph (`:782`) constrains any carrier to *"preserve
   the direct-path caller-supplied contract **byte-verbatim**."* Absorbing the extension at Phase 7
   is precisely the silent design extension X-AL-3 exists to stop (root `CLAUDE.md` §4.4).
2. **It is a genuine choice between substantive alternatives**, not a defect with one correct repair.
   Detect-then-refuse is the **committed posture**, not an accident: an out-of-order refusal is the
   *honest* outcome wherever the timestamp means "when the event happened." That makes this **Class
   2** (in-execution operator decision) rather than Class 1 (halt-execution defect) per root
   `CLAUDE.md` §4.3 — the same classification `B-88`, `B-98`, `B-104` and `B-107` carry.
3. **The probability changed, so the deferral's own premise is live.** `B-57`'s close-out defers
   *until the inversion materializes in practice*. `B-112` records a reproduced mechanism (12/20
   runs, two-process probe) that raises that probability, plus a code-grounded **in-process
   widening** — the exposed population is any two concurrent direct appenders on one ledger root,
   **threads included** (§3(v)).

**The harm, stated precisely and against interest.** Nothing is silently corrupted — the refusal is
loud, and mutual exclusion is unaffected (the same kernel `flock` it always was). The harm is
**availability of an honest write**: a direct producer whose entry means *"when this was appended"*
can be refused for a reason that has nothing to do with its own correctness — it merely lost a lock
race after sampling. One production site already works around this by hand (§3(iv)).

---

## §2 Current behaviour at HEAD `73b0e87b`

| Surface | State |
|---|---|
| **Tolerance** | `_CLOCK_SKEW_TOLERANCE = timedelta(0)` — `state_ledger_write.py:69`. Its own comment (`:67`–`:68`) reads *"Configuration-supplied; defaults to zero (strict non-decreasing order)"* — **it is a module constant, not configuration-supplied at HEAD** |
| **Refusal** | `state_ledger_write.py:321`–`:324`: `if prior_entry is not None and timestamp < prior_entry.timestamp - _CLOCK_SKEW_TOLERANCE: raise NonMonotonicTimestampError(...)` |
| **The sentinel** | `WRITER_OWNED_TIMESTAMP: Timestamp = datetime.fromtimestamp(0, tz=UTC)` — `state_ledger_write.py:83`, docstring `:71`–`:82` |
| **THE DECISIVE CHEAPENER — the sentinel check is UNCONDITIONAL** | `state_ledger_write.py:316`–`:320`: `timestamp = datetime.now(UTC) if entry_payload.timestamp == WRITER_OWNED_TIMESTAMP else entry_payload.timestamp`. There is **no surface discriminator, no mode flag, no path gate** — the substitution fires for ANY caller that stamps the sentinel. It sits INSIDE `with cross_process_write_lock(...), _WRITE_LOCK:` (`:306`), the same critical section that reads the prior entry and computes `prior_event_hash` |
| **What restricts it today** | **PROSE ONLY.** The sentinel docstring (`:79`–`:80`) says *"Every DIRECT append path keeps caller-supplied timestamp semantics verbatim — this sentinel is opt-in per entry, never a default"*, and §7.6 `:776`/`:778` says the same at contract level. **No code enforces the restriction** |
| **Lock shape (the B-112 mechanism)** | In-process face: `_rlock.acquire(blocking=False)` → `note_contention()` → timeout-bounded `acquire` (`cross_process_ledger_lock.py:173`–`:184`). Cross-process arm: non-blocking `flock` probe then bounded wait (`:524`). `flock` *"contends between separate fds even within one process"* — the module's own text, `:120` |
| **Hash participation** | The persisted `timestamp` IS a `StateLedgerEntry` field and IS hash-covered. **But this fork changes no field, no shape, and no recipe** — only WHICH INSTANT a consenting call site records. Zero canonicalization delta, zero `snapshot_hash` migration |
| **Existing direct-surface opt-in** | **ONE, in tests only**: `harness-is/tests/test_shadow_git_rollback.py`'s concurrent-append worker retries with the sentinel on a DIRECT surface — adjudicated PERMITTED at the B-93 leg (a single explicit opt-in changes no producer's semantics and sets no default) and recorded on `B-112` as the first direct-surface use in the tree |

---

## §3 Six grounding findings that shape the readings

### (i) THE MECHANISM EXISTS; ONLY THE AUTHORIZATION IS MISSING `[HIGH]`

This is the single most important fact in the filing, and it is what makes Reading A cheap. The
sentinel check at `state_ledger_write.py:316`–`:320` is **unconditional at HEAD**. A direct producer
that stamps `WRITER_OWNED_TIMESTAMP` today *already gets writer-owned sampling* — the writer cannot
tell a drain from a direct append and does not try to.

**Consequence, stated carefully in both directions:**

- *For Reading A*: the impl leg is **not** "build writer-owned sampling for direct surfaces." It is
  "**stop forbidding** what the code already does, at named call sites." The per-site change is one
  line — replace a `datetime.now(UTC)` / `time_source()` expression with the sentinel constant.
- *Against complacency*: because nothing enforces the restriction, the contract is currently held by
  **prose alone**, and the test opt-in at `test_shadow_git_rollback.py` is already exercising it.
  Reading A does not create a bypass; it **names and bounds** one that structurally exists.

### (ii) THE DIRECT-WRITER INVENTORY — TWELVE SITES, re-resolved BY CONTENT `[HIGH]`

Every site below was re-resolved by reading the line at HEAD. **Three module paths in the inbound
grounding notes were wrong** and are corrected here (§9 item 1).

| # | Site (corrected path) | Timestamp expression | Meaning |
|---|---|---|---|
| 1 | `harness-is/src/harness_is/shadow_git_rollback.py:141` | `timestamp=now` (`now = datetime.now(UTC)` at `:93`) | when appended |
| 2 | `harness-cp/src/harness_cp/pause_resume_protocol.py:1103` | `timestamp=datetime.now(UTC)` | when appended |
| 3 | `harness-cp/src/harness_cp/pause_resume_protocol.py:1190` | `timestamp=datetime.now(UTC)` | when appended |
| 4 | `harness-cp/src/harness_cp/pause_resume_protocol.py:1294` | `timestamp=datetime.now(UTC)` | when appended |
| 5 | `harness-cp/src/harness_cp/workflow_driver.py:6074` | `timestamp=datetime.now(UTC)` | when appended |
| 6 | `harness-cp/src/harness_cp/workflow_driver.py:6297` | `timestamp=datetime.now(UTC)` | when appended |
| 7 | `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py:337` | `timestamp=datetime.now(UTC)` | when appended |
| 8 | `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:290` | `timestamp=datetime.now(UTC)` | when appended |
| 9 | `harness-cp/src/harness_cp/per_step_override_evaluator.py:489` | `timestamp=timestamp` (param; caller samples `datetime.now(UTC)` at `:523`) | when appended |
| 10 | `harness-cp/src/harness_cp/sibling_ledger_entry_composition.py:163` | `timestamp=timestamp` (param, threaded through `cp_is_wiring.py:151`) | **UNREACHABLE — see (iii)** |
| 11 | `harness-runtime/src/harness_runtime/lifecycle/hitl_gate_composer.py:1566` | `timestamp=datetime.now(UTC)` | when appended |
| 12 | `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py:701` (+ resample-retry `:751`) | `timestamp=self.time_source()` | when appended — **but injected, see (iv)** |
| 13 | `harness-runtime/src/harness_runtime/lifecycle/cost_attribution_f2_write.py:157` | `timestamp=time_source()` | when appended — **injected** |
| 14 | `harness-runtime/src/harness_runtime/lifecycle/as_is_wiring.py:129` | `timestamp=composed.timestamp` | **EVENT time — must stay caller-supplied** |

**Fourteen rows, twelve SITES** (`audit_writer` contributes a primary and its resample retry;
`per_step_override_evaluator` contributes the composer and its sampling caller). This is the surface
Reading A must price — and it is **not** uniformly convertible, which is the finding the inbound
"every `datetime.now(UTC)`-at-construction site can adopt" summary got wrong (§9 item 4).

### (iii) ONE SITE IS PRODUCTION-UNREACHABLE — measured, not assumed `[HIGH]`

`sibling_ledger_entry_composition.py:163` receives its `timestamp` as a parameter, threaded from
`RuntimeCpIsWiring.emit_sibling_ledger_entry` (`harness-runtime/src/harness_runtime/lifecycle/cp_is_wiring.py:124`,
passing it on at `:151`). A sweep of `harness-{is,as,cp,od,cxa,core,runtime}` + `tools`, `.py` only,
`.venv`/`__pycache__`/`.codex-worktrees` excluded, for `emit_sibling_ledger_entry` returns **exactly
three non-test hits: the definition itself and two docstring mentions.** Every call site is a test.

**Consequence.** The sibling seam is **wired but not driven** at HEAD. It cannot contend at runtime
today, so it is **out of scope for the impl leg's conversions** and belongs in the classification
table as *deferred-until-a-producer-exists*. Converting it would be speculative work against an
unreached path.

*Contrast, verified the same way*: the three sites added to the inventory at the 2026-08-07 pass ARE
production-reachable — `workload_binding_engine_class_selection` via
`harness-runtime/src/harness_runtime/bootstrap/stage_3b_cp_routing.py:124`;
`hitl_as_tool_call_rewriting` via `harness-runtime/src/harness_runtime/lifecycle/hitl_tool_loop.py:131`;
`per_step_override_evaluator` via `harness-cp/src/harness_cp/workflow_driver.py:5279` and `:6656`
(each through the `cp_is_wiring` binding at `:205` / `:235` / `:301`).

### (iv) ONE PRODUCTION SITE ALREADY WORKS AROUND THIS BY HAND — *and `B-57` already reads it the OTHER way* `[HIGH]`

**Attribution first: this is NOT a new finding.** `B-57`'s own 2026-07-27 grounding bullet already
records it, at `audit_writer.py:727-752`, under the heading *"Nuance worth recording — asymmetric
caller-side recovery already exists on ONE half of this row's own named interleave."* This filing
neither discovered it nor may present it as fresh evidence. What this filing adds is a **disagreement
about what it means**, stated explicitly so the operator can adjudicate rather than inherit.

`audit_writer.py:727`–`:752` (comment `:727`–`:738`, loop `:739`–`:752`) is a **bounded resample-retry
loop**:

```
attempts_left = 5
while True:
    try:
        return self.ledger_writer.append(payload, write_key)
    except NonMonotonicTimestampError:
        attempts_left -= 1
        if attempts_left <= 0:
            raise
        payload = EntryPayload(..., timestamp=self.time_source())
```

Its own comment names the exact race this fork is about (`:727`–`:734`): *"this lock serializes AUDIT
appends, but ordinary `LedgerWriter.append` F2/state writes to the SAME ledger do not take it — one
can commit a newer timestamp between our sampling and our IS append, which then raises
NonMonotonicTimestampError AFTER the sidecar row is durable (an unanchored signature)."*

**`B-57`'s reading, quoted so it is not strawmanned:** *"That is caller-side recovery layered ATOP
detect-then-refuse, fully consistent with the committed posture rather than a departure from it.
The COST half (`cost_attribution_f2_write.py`) and every other direct writer have no such recovery,
so the row's failure mode stays live-but-unexercised for them. Posture unchanged."*

**Where this filing disagrees, and it is a narrow disagreement.** The register is right that a
caller-side retry is *compatible* with detect-then-refuse — it is not a contract violation. But
"compatible with the posture" and "evidence the posture is costless" are different claims, and the
row's bullet supports only the first. Three grounded observations:

1. The loop exists because a **real** contended interleave was identified at review (its comment is
   tagged *"codex round-8 P1"*) — so on at least one production path the refusal was judged likely
   enough to need code, before `B-93` raised the probability further.
2. The mitigation is **strictly weaker than the sentinel**: it samples outside the lock every time,
   so it can lose five consecutive races and then raise — whereas the sentinel resolves *inside* the
   critical section and makes the refusal unreachable by construction.
3. It leaves the asymmetry the row itself names: `cost_attribution_f2_write.py:157` — the **other**
   half of `B-57`'s own named audit/cost interleave — has no recovery at all.

**Under Reading A this loop becomes dead code at that site**, which is a concrete simplification the
impl leg should take deliberately rather than leave (§4's injection caveat interacts with it — see
there). **Weight, stated honestly:** this is *circumstantial* evidence of materialization, not an
observed production incident, and `B-57`'s own reading of the same code is the reasonable contrary
one. It is a reason to re-price the deferral, not a reason to declare its condition met.

### (v) THE EXPOSED POPULATION IS BROADER THAN TWO PROCESSES `[HIGH]` *(code-grounded; NOT reproduced)*

`B-112`'s 12/20 figure is a **two-OS-process** measurement. But `flock` *"contends between separate
fds even within one process"* — stated in the lock module's own text at
`cross_process_ledger_lock.py:120`, which is precisely why the module carries a refcounted in-process
`_rlock` face at all. A sibling **thread** that loses the in-process probe enters the same polling
wait (`:173`–`:184`), and the cross-process arm beneath it polls the same way (`:524`).

So the exposed population is **any two concurrent direct appenders on one ledger root, threads
included** — not merely the `harness run` alongside `harness daemon` two-process topology that
`B-112`'s close-out step (1) names. **Stated as a code-grounded scope widening only: no in-process
probe was run at this pass**, and the 12/20 figure is not claimed for the threaded case.

### (vi) COSTS THAT ARE ZERO, DETERMINED RATHER THAN ASSUMED `[HIGH]`

- **Contract numbers: ZERO.** Reading A extends the EXISTING `C-IS-07 §7.6`. No `C-*` number is
  minted — per `[[spec-leg-cannot-mint-contract-number]]`, a spec leg cannot mint one anyway.
- **Hash / canonicalization: ZERO.** No field added, no shape changed, no recipe touched. The
  `timestamp` field was already hash-covered; only which instant a consenting site records changes.
  No migration surface, no `snapshot_hash` delta.
- **CXA rows: ZERO, determined not assumed.** The sentinel is already exported from `harness-is`
  (`state_ledger_write.WRITER_OWNED_TIMESTAMP`) and the converting call sites already import from
  `harness_is.state_ledger_write` (the C-IS-07 §7.1 write contract they already use). **No new
  package edge, no new typed seam**, so nothing is owed at
  `Cross_Axis_Composition_Document_v2_23.md` §2.3 — the same disposition `B-97`(a) and `B-88`
  reached for the same reason.
- **New plan units: ZERO.** U-IS-11 already owns the C-IS-07 §7.1/§7.6 write surface and is already
  landed; this is an acceptance-criterion widening, the shape `B-100` and `B-88` both used.

---

## §4 The readings

### Reading A — a narrow IS delta authorizing PER-CALL-SITE opt-in on direct surfaces *(RECOMMENDED)*

**The contract change, stated minimally.** `C-IS-07 §7.6` gains one subsection. The default is
**unchanged**: caller-supplied semantics remain the contract for every direct producer that does not
opt in. What changes is that a direct producer MAY elect writer-owned sampling **per call site**, by
stamping the existing `WRITER_OWNED_TIMESTAMP` sentinel.

**Amendment shape — ONE site, one added subsection.** The `:776` *"Surfaces that do NOT change"*
paragraph and the `:778` residual are **preserved verbatim as historical record** (they were accurate
when authored); a new subsection states the opt-in and its boundary:

> *A direct-append call site MAY elect writer-owned sampling by supplying `WRITER_OWNED_TIMESTAMP` as
> the write payload's timestamp. The election is **per call site**, never a default and never a mode
> on the writer: a direct producer that supplies any other value retains caller-supplied semantics
> byte-verbatim, so §7.6's direct-path contract is unchanged for every non-electing producer. A call
> site MAY elect only where its entry's timestamp means **when the entry was appended**; where it
> means **when the event happened**, caller-supplied semantics are required and an out-of-order
> refusal is the honest outcome.*

Plus a **per-site classification table** carried at the plan (not the spec), pinning each of the
twelve sites as ELECTING / RETAINING / DEFERRED, so the boundary is auditable rather than folkloric.

**The classification, from §3(ii)'s grounded inventory** *(recommended dispositions; the spec leg
re-grounds each)*:

| Disposition | Sites | Why |
|---|---|---|
| **ELECT** (≈8 conversions) | shadow_git_rollback `:141`; pause_resume_protocol `:1103`/`:1190`/`:1294`; workflow_driver `:6074`/`:6297`; workload_binding_engine_class_selection `:337`; hitl_as_tool_call_rewriting `:290`; per_step_override_evaluator `:489`/`:523`; hitl_gate_composer `:1566` | Each samples at construction and means *when appended* |
| **ELECT, with an injection caveat** | audit_writer `:701`/`:751`; cost_attribution_f2_write `:157` | Same meaning — **but see the caveat below** |
| **RETAIN caller-supplied** | as_is_wiring `:129` (`timestamp=composed.timestamp`) | Genuine **event time**, carried from an upstream composed record; single-producer |
| **DEFER** | sibling_ledger_entry_composition `:163` | **No production caller at HEAD** (§3(iii)) |

**THE INJECTION CAVEAT — stated because it is easy to get wrong and it is a real per-site cost.**
`audit_writer` and `cost_attribution_f2_write` do not call `datetime.now(UTC)` at the construction
site; they call an **injected** `time_source` (`audit_writer.py:294`, defaulted at `:1639` to
`lambda: datetime.now(UTC)`; `cost_attribution_f2_write.py:74`, same default inline). That injection
point exists so tests can pin a deterministic instant. Stamping the sentinel **overrides the injected
source** — the writer substitutes its own `datetime.now(UTC)` regardless — so any test that asserts a
pinned timestamp on those paths would break, and the injection seam would become partially inert.
The spec leg must decide, per site, between (a) electing and retiring the injection seam's timestamp
role, or (b) retaining caller-supplied semantics and keeping determinism. **This is the one place
Reading A is not a one-line change**, and it is stated here rather than discovered at the impl leg.

Two facts bound the cost: `shadow_git_rollback:141` shares its `now` with `restored_at` at `:125`, so
electing there decouples the returned `RollbackResult.restored_at` from the persisted ledger
timestamp — a witness-visible but semantically harmless divergence the impl leg should pin
deliberately; and `audit_writer`'s resample-retry loop (§3(iv)) becomes dead at that site under
election, which is a net simplification the leg should take rather than leave.

**Plan rider.** `Implementation_Plan_Information_Substrate_v2_8.md` U-IS-11 acceptance widened to
cover the opt-in on direct surfaces + the classification table. **No new unit** (§3(vi)).

**Witness shape.** (a) A **two-OS-process contention probe**: a waiter whose timestamp is sampled
first must not be refused after a later writer overtakes it — the direct analogue of `B-112`'s
12/20 repro, asserted GREEN under election and RED under a reverted election (PD-8 mutation probe).
(b) A **negative witness** pinning that a non-electing direct producer still gets caller-supplied
semantics and still refuses on inversion — the default must be demonstrably unchanged, or the
amendment has silently become a default. (c) A witness that `as_is_wiring`'s event-time path is
untouched. (d) The `audit_writer` retry-loop disposition pinned either way.

**Costs, stated plainly.** ZERO contract numbers; ZERO hash/canonicalization impact; ZERO CXA rows;
ZERO new plan units; ONE spec subsection + ONE plan AC widening + a classification table; ~8 one-line
conversions + 2 injection-caveat decisions + 1 retain + 1 defer. **IS spec v1.12 → v1.13; IS plan
v2.8 → v2.9.**

### Reading B — HOLD: keep detect-then-refuse until an observed production refusal

Vocabulary of the contract stays exactly as §7.6 wrote it. `B-57` stays `registered_finding` with its
materialization condition **restated as the explicit demand test** it already implies: the row
reopens on an observed `NonMonotonicTimestampError` from concurrent production direct writers.

**The argument, at its strongest.** `B-57`'s own close-out conditions the remedy on the inversion
*"materializ[ing] in practice."* What `B-112` supplies is a **mechanism and a probability**, not an
observation — stated on `B-112` itself, against interest: *"NOT NEWLY POSSIBLE, NEWLY LIKELY … the
same refusal was always reachable whenever the later writer genuinely acquired first, and POSIX
`flock` specifies NO acquisition ordering at all, so the pre-B-93 code was relying on an UNSPECIFIED
kernel behaviour."* On that reading the pre-B-93 world was never actually safe, and B-93 merely made
a pre-existing latency visible. Holding costs nothing and preserves §7.6's direct-path contract
byte-verbatim, which is exactly what its deferred-to-discretion paragraph (`:782`) asks of any
carrier.

**Zero spec delta. Zero plan delta. Zero impl delta.**

**What Reading B costs, stated because the rows do not.** It leaves `audit_writer`'s hand-rolled
resample-retry (§3(iv)) as the *de facto* mitigation — a bounded loop that can still exhaust and
raise, on the one production path noisy enough to have needed a workaround. It also leaves the
restriction held by **prose alone** (§3(i)) while a test already opts in on a direct surface, so the
boundary continues to drift without a contract to check against.

---

## §5 Recommendation — **Reading A**, and the discriminator that flips it

**RECOMMENDED: Reading A.** `[MODERATE]`

Grounds, in order of weight:

1. **§3(i), the mechanism is already unconditional.** The one substantive reason to prefer B — that
   extending writer-owned authority to direct surfaces is expensive — was *measured and found
   absent*. There is nothing to build. The authorization is the whole cost, and the code cannot
   currently distinguish an authorized opt-in from an unauthorized one, which means the contract is
   enforced by prose while a test already exercises the bypass.
2. **§3(iv), a production site already worked around it by hand** — with the weight discounted as
   §3(iv) states. A bounded resample-retry exists at `audit_writer.py:727`–`:752` for exactly this
   refusal, added at review as a P1. `B-57` reads it as *consistent with* the committed posture and
   that reading is defensible; this filing reads it as circumstantial materialization evidence,
   because the mitigation is strictly weaker than the sentinel and the interleave's other half has
   none. **This ground is contested and is weighted accordingly** — it does not carry the
   recommendation on its own.
3. **§3(v), the exposed population is broader than the rows record.** Threads, not just processes.
   The deferral was priced against a two-process topology.
4. **§3(vi), the costs are zero where it matters** — no contract number, no hash, no CXA, no new
   unit. The delta is one spec subsection.

**A note against my own recommendation.** `[HIGH]` Reading B's core point is verified and it is
`B-112`'s own words: this is *newly likely, not newly possible*, and POSIX `flock` never specified
acquisition ordering — so no production refusal has actually been observed, and `B-57`'s close-out
conditions the remedy on exactly that. An operator who reads "materializes in practice" strictly
should pick B, and that is a legitimate reading of the same facts. My judgement is that §3(iv)'s
hand-rolled retry loop is the materialization evidence the condition was asking for, but it is
**circumstantial** — the loop's comment does not name a production incident.

**THE DISCRIMINATOR — what flips the choice.** `[HIGH]`

> **Does §7.6's direct-path residual guard the CONTRACT (what producers may rely on), or the
> DEFAULT (what producers get absent an election)?**

- If it guards the **DEFAULT**, then a per-call-site opt-in that leaves every non-electing producer
  byte-identical does not touch what the residual protects, and **A is right** — the residual's own
  words are *"would change caller-supplied semantics **for every existing direct producer**"*, which
  a per-site election precisely does not do.
- If it guards the **CONTRACT ITSELF** — the guarantee that *a direct append's timestamp is the
  caller's*, as a property a reader may rely on across the whole surface — then any election
  weakens it for readers who cannot tell which sites elected, and **B is right** until an observed
  failure justifies the trade.

I recommend A because the residual's own sentence is scoped to *every existing direct producer*, and
because the B-93 leg **already adjudicated this exact question** in A's direction for the test
opt-in: *"a single explicit opt-in changes no producer's semantics and sets no default, so the
constraint does NOT forbid it"* (recorded on `B-112`). Reading A generalizes an adjudication the
workspace has already made once, under review, on this same contract.

---

## §6 Council position — **PROBE-RESOLVED; NO convening is owed** `[HIGH]`

`B-112`'s `council` field names the condition precisely: *"Step (3) WOULD be council-eligible if it
is reached — widening the skew tolerance trades information-substrate integrity (C3) against
operator-loop robustness (C11) across every ledger writer at once — but it is reached only if step
(2) leaves an exposed caller that cannot adopt writer-owned sampling."*

**The probe was run (§3(ii)), and step (3) is NOT reached.** The classification leaves exactly one
site retaining caller-supplied semantics — `as_is_wiring.py:129`, which carries **event time**
(`timestamp=composed.timestamp`, a pass-through of an upstream composed record). That site is
**single-producer**: it is not a caller that *cannot* adopt while being exposed to contention; it is a
caller for which an out-of-order refusal is the honest outcome by design, exactly as `B-112`'s step
(2) frames it. Since no exposed caller is left stranded, **`_CLOCK_SKEW_TOLERANCE` configurability is
never reached**, and the C3 ⊥ C11 tension that would have been council-eligible **does not arise**.

Per root `CLAUDE.md` §10.9 council posture amendment 5 (probe-first discipline), this is recorded as
**surfaced + probe-resolved**, with the classification sweep as the resolving probe. The
nameable-tension discriminator (amendment 1) therefore fails: convening a dyad whose triggering
condition is unmet is the primary-collapse failure the amendments exist to prevent.

**What WOULD owe a convening.** If the spec leg's own re-grounding finds an exposed direct caller
that must retain caller-supplied semantics **and** is genuinely contended, step (3) is reached and
the C3 ⊥ C11 dyad is owed **before** any tolerance change is authored. The injection-caveat sites
(§4) are the candidates to watch: if either is judged RETAIN, re-run this determination.

---

## §7 The ratification ask — ONE decision, two options

**THE SINGLE GATE, stated as the question it actually is:**

> **Is authorizing a per-call-site opt-in to an ALREADY-UNCONDITIONAL writer-side mechanism, on a
> cleared contract whose residual routes the extension to back-flow, a SPEC ACT this leg may perform
> — or does it require operator ratification first?**

That question *is* the ratification ask: §7.6's residual says the extension *"requires its own
back-flow,"* and this filing is that back-flow. The operator's answer selects the reading.

| Option | What the operator ratifies | What it costs |
|---|---|---|
| **A** *(recommended)* | `C-IS-07 §7.6` gains a per-call-site opt-in for direct appends via the existing `WRITER_OWNED_TIMESTAMP` sentinel; the default stays caller-supplied for every non-electing producer; a per-site classification table lands at the plan | IS spec v1.12 → v1.13 (1 added subsection; `:776`/`:778` preserved verbatim); IS plan v2.8 → v2.9 (U-IS-11 AC widened + classification table, **no new unit**); impl: ~8 one-line conversions + 2 injection-caveat decisions + 1 retain + 1 defer; witnesses per §4. Zero hash / CXA / contract-number impact |
| **B** | HOLD — detect-then-refuse stays the committed posture; `B-57` stays `registered_finding` with its materialization condition restated as an explicit demand test | Zero now. Leaves `audit_writer`'s hand-rolled resample-retry as the de-facto mitigation and the restriction held by prose alone |

**Carried by either answer** (no separate gate): the five drift repairs at §9 ride the ratification
leg's register touch; and `B-112`'s close-out step (1) sweep is **discharged by §3(ii)/(iii)** — the
classification exists now, and the register should record that rather than re-commissioning it.

---

## §8 Sequencing, and what each leg owes

| Leg | Owes | Gate |
|---|---|---|
| **This filing** (doc-only) | The filing + prose/YAML bullets on `B-57` and `B-112`. Both rows stay `registered_finding`; **no snapshot change** from this fork (the digest is over `id:status` pairs and neither status moves — the snapshot does move at this PR, but only because of the two unrelated `B-115`/`B-116` mints) | — |
| **Ratification** | Operator selects A / B via `AskUserQuestion`; a `§11 RATIFICATION` section is appended here; `B-57`'s `pr:` pointer set and (under A) status → `design_substrate_gated`; `B-112` cross-linked to the outcome | Operator |
| **Council** *(conditional only)* | NOT owed (§6). Re-evaluate only if the spec leg's re-grounding leaves an exposed caller that must retain caller-supplied semantics | — |
| **Spec leg** *(A)* | `Spec_Information_Substrate_v1.md` v1.12 → v1.13 by a dedicated spec-writer + `Implementation_Plan_Information_Substrate_v2_8.md` v2.8 → v2.9; clearance markers at `.harness/clearance/` per root `CLAUDE.md` §4.5, **one per changed artifact — both here**. The leg MUST re-ground the twelve-site classification at its own HEAD and MUST resolve the two injection-caveat sites explicitly | X-AL-3 guard + adversarial review |
| **Impl leg** *(A)* | The ~8 conversions, the 2 injection decisions, the `audit_writer` retry-loop disposition, the `shadow_git_rollback` `restored_at` decoupling pin, the two-process contention witness, the non-electing negative witness, and the PD-8 mutation probe | CI + `merge-gate` 3-lens (code-touching) |
| **Terminal leg** *(B)* | Restate `B-57`'s materialization condition as an explicit demand test on the row, and record §3(iv)'s hand-rolled retry as the known de-facto mitigation so a later reader does not rediscover it as novel | Register touch only |

---

## §9 Cite re-verification at HEAD `73b0e87b`, and the drift found

Every cite was resolved by direct read at this HEAD; every count recomputed programmatically
(filesystem walks excluding `.codex-worktrees/`, `.claude/worktrees/`, `__pycache__`, `.venv`).

**Verified as cited.**

| Cite | Verified |
|---|---|
| `state_ledger_write.py:69` — `_CLOCK_SKEW_TOLERANCE = timedelta(0)` | ✓ exact |
| `state_ledger_write.py:83` — `WRITER_OWNED_TIMESTAMP` sentinel | ✓ exact; docstring `:71`–`:82` |
| `state_ledger_write.py:316`–`:320` — the UNCONDITIONAL sentinel substitution | ✓ read in full; inside `:306`'s lock composition |
| `state_ledger_write.py:321`–`:324` — the `NonMonotonicTimestampError` refusal | ✓ |
| `Spec_Information_Substrate_v1.md:776` — *"Surfaces that do NOT change"* | ✓ exact |
| `Spec_Information_Substrate_v1.md:778` — the registered residual, *"requires its own back-flow"* | ✓ exact |
| `Spec_Information_Substrate_v1.md:782` — *"preserve the direct-path caller-supplied contract byte-verbatim"* | ✓ exact |
| `cross_process_ledger_lock.py:120` — *"`flock` contends between separate fds even within one process"* | ✓ exact |
| `cross_process_ledger_lock.py:173`–`:184` — in-process probe → `note_contention()` → bounded acquire | ✓ |
| `cross_process_ledger_lock.py:524` — cross-process non-blocking probe | ✓ |
| `audit_writer.py:727`–`:752` — the bounded resample-retry loop (comment `:727`–`:738`, loop `:739`–`:752`) | ✓ read in full; matches `B-57`'s own 2026-07-27 bullet cite exactly |
| All twelve direct-writer sites | ✓ each line read at HEAD (§3(ii) table) |

**DRIFT FOUND — five items, none changing any disposition.** Recorded per the workspace stale-carry
discipline rather than silently normalized. The corrected values are what this filing uses.

| # | Inbound claim | Verified at HEAD `73b0e87b` | Class |
|---|---|---|---|
| 1 | Module paths `harness-runtime/src/harness_runtime/lifecycle/pause_resume_protocol.py`, `harness-cp/src/harness_cp/hitl_gate_composer.py`, `harness-od/src/harness_od/{audit_writer,cost_attribution_f2_write}.py`, `harness-cxa/src/harness_cxa/as_is_wiring.py` | **ALL WRONG — files do not exist at those paths.** Correct: `harness-cp/src/harness_cp/pause_resume_protocol.py`; `harness-runtime/src/harness_runtime/lifecycle/{hitl_gate_composer,audit_writer,cost_attribution_f2_write,as_is_wiring}.py`. The **line numbers were right**; only the packages were wrong (the register itself cites bare filenames, so this drift is in the summary, not the row) | 3 |
| 2 | *"`sibling_ledger_entry_composition.py:163` … a `timestamp` parameter on the sibling-composition path"* — carried as a live direct-writer site | **PRODUCTION-UNREACHABLE.** `emit_sibling_ledger_entry` (`cp_is_wiring.py:124`) has **ZERO non-test callers** — three non-test hits total, all definition/docstring. The site is real; the exposure is not. Re-classified DEFER (§3(iii)) | 3 |
| 3 | *"`retry_breaker_fallback.py` ~:1025 `record_failure` on the cause-None branch"* (`B-116`'s grounding) | **`:1028`.** `:1025` is the `"retry.fail_class"` attribute-set line; `record_failure(cause=breaker_cause)` is at `:1028`, with `breaker_cause` computed at `:1006`. **Substance intact** — one breaker failure IS recorded against the candidate's provider before the fail-fast exit | 3 |
| 4 | *"every `datetime.now(UTC)`-at-construction site means 'when appended' and can adopt"* | **TOO STRONG for two sites.** `audit_writer.py:701`/`:751` and `cost_attribution_f2_write.py:157` call an **injected** `time_source` (`audit_writer.py:294`, defaulted `:1639`; `cost_attribution_f2_write.py:74`), not `datetime.now(UTC)` at the site. Electing there **overrides the injection seam**, which exists for test determinism — a real per-site cost, surfaced at §4 rather than absorbed | 3 |
| 5 | *"`_CLOCK_SKEW_TOLERANCE` … configuration-supplied"* (the constant's own comment, `:67`–`:68`) | **STALE-AS-DESCRIBED IN THE CODE ITSELF.** It is a module-level constant with no configuration path at HEAD. Not this fork's to repair (Reading A does not reach step (3)), but recorded so a later arc does not trust the comment | 3 |

Item 5 is a pre-existing comment defect in shipped code, not a claim this filing relies on. It is
recorded because a reader pricing step (3) would otherwise believe a configuration surface exists.

**Review record (out-of-family review, branch-vs-main).**
- *(To be filled per round; no outcome is pre-written.)*

---

---

## §11 RATIFICATION — **Reading A**, operator, 2026-08-07

**Decision.** The operator ratified **Reading A**: `C-IS-07 §7.6` is extended to authorize **per-call-site** election of writer-owned sampling on DIRECT append surfaces via the EXISTING `WRITER_OWNED_TIMESTAMP` sentinel. The default is **unchanged** — every non-electing direct producer retains caller-supplied semantics byte-verbatim. **No new contract number is minted** (the existing C-IS-07 §7.6 is extended; per `[[spec-leg-cannot-mint-contract-number]]` a spec leg cannot mint one).

| Field | Value |
|---|---|
| Ratified reading | **A** (per-call-site opt-in; `B` — HOLD — declined) |
| Ratified by | Operator |
| Ratified on | 2026-08-07 |
| Gate answered | §7's single gate — *"is authorizing a per-call-site opt-in to an already-unconditional writer-side mechanism, on a cleared contract whose residual routes the extension to back-flow, a spec act this leg may perform, or does it require operator ratification first?"* — answered by **performing** the ratification: this filing IS the §7.6 residual's demanded back-flow, and the operator's selection discharges it |
| Discriminator (§5) resolved | The §7.6 residual guards the **DEFAULT**, not a whole-surface guarantee — its own sentence is scoped to *"every existing direct producer"*, and a per-call-site election leaves every non-electing producer byte-identical. This generalizes the adjudication the `B-93` leg already made once, under review, on this same contract |
| Council | **NOT owed — probe-resolved** per §6, re-determined (not inherited) at the spec leg. `B-112` step (3) is not reached: the classification leaves exactly one RETAIN site (`as_is_wiring.py:129`, genuine event time), which is not an *exposed caller that cannot adopt*. **A LIVE trigger survives:** a RETAIN verdict on either injection-caveat site at the impl leg re-opens the C3 ⊥ C11 determination before any tolerance change — recorded at the plan's §0.6 |

### §11.1 What the spec leg landed (this ratification's apply pass — PR #1255)

| Artifact | Version | Amendment sites |
|---|---|---|
| `design-substrate/Spec_Information_Substrate_v1.md` | v1.12 → **v1.13** | **ONE authorizing site** — NEW `§7.6.1` (the election, the eligibility rule, the demonstrable default-preservation property, the does-NOT-authorize list, and the roster-lives-at-the-plan routing). PLUS ONE **residual-status paragraph** inside §7.6 recording that the residual's demanded back-flow has been performed and DISCHARGED in this narrow form (the `"Surfaces that do NOT change"` and `Registered residual` paragraphs themselves **PRESERVED VERBATIM**, per §4's shape and the §7.5 precedent). PLUS ONE **cross-reference-only** clause at the §7.1 row-7 cell (zero new semantics; authored so the summary row does not become stale-as-described) |
| `design-substrate/Implementation_Plan_Information_Substrate_v2_9.md` | v2.8 → **v2.9** | U-IS-11 AMENDED — ACs **#14–#20** (election authorization; the negative default-preservation witness; the eligibility rule; per-site table conformance; the two injection-caveat resolutions; the `audit_writer` retry-loop disposition; the `shadow_git_rollback` `restored_at` decoupling pin) + the **per-site classification table** §7.6.1 routes to the plan + PD-8-probed witnesses. **ZERO new units / nodes / edges / auxiliary types**; ACs #1–#13 PRESERVED VERBATIM |
| `.harness/clearance/` | — | One marker per changed artifact (spec + plan), per root `CLAUDE.md` §4.5 |
| `.harness/forward-register.yaml` | — | `B-57` `registered_finding` → **`open`** (ratified, spec AND plan deltas applied, impl leg owed — the `B-96`/`B-88` enum reasoning); `B-112` stays `registered_finding` with a note that ratification A landed and its deferred adoption question is answered, its own remaining disposition resolving at the impl leg |

### §11.2 Costs, as ratified — all re-determined at the spec leg, none assumed

**ZERO** contract numbers · **ZERO** hash / canonicalization / migration / `snapshot_hash` impact (no field added, no shape changed, no recipe touched — only *which instant* a consenting call site records) · **ZERO** CXA rows (the sentinel is already exported from `harness-is` and every candidate site already imports the C-IS-07 §7.1 write contract: no new package edge, no new typed seam) · **ZERO** new plan units, nodes, edges or auxiliary types · **ZERO** code at this leg (SPEC-ONLY).

### §11.3 Two count claims in this filing CORRECTED at the spec leg — recorded, not silently normalized

Re-grounded by direct read at HEAD `acfc1afa`; all fourteen §3(ii) rows are byte-identical to this filing, and the `emit_sibling_ledger_entry` zero-non-test-caller sweep re-ran independently (19 hits, exactly 3 non-test: the definition plus two docstring mentions). Two of this filing's own COUNTS do not reconcile with its own table:

1. **§3(ii)'s *"Fourteen rows, twelve SITES"*.** The stated fold (audit_writer's primary + resample retry; per_step_override_evaluator's composer + sampling caller) is **already performed** inside rows 12 and 9 as printed — deducting it again is what produces "twelve". By content the classification table is **14 rows**, and that is what IS plan v2.9 §2.1 carries.
2. **§4/§7's *"≈8 conversions"* / *"~8 one-line conversions"*.** §4's own ELECT cell enumerates **TEN** payload-construction rows. The corrected figure is **10 ELECT** + **2** pending the per-site injection-caveat verdicts.

Neither correction changes a disposition, a reading, or any zero-cost line; both change the **SIZE of the surface** the impl leg must convert. Recorded here per the workspace's stale-carry discipline, alongside this filing's own §9 drift record.

### §11.4 What remains owed after this leg

The **impl leg**: the 10 ELECT conversions; the 2 injection-caveat resolutions recorded with rationale (a RETAIN verdict on either FIRES the §0.6 council trigger); the `audit_writer` resample-retry disposition; the `shadow_git_rollback` `restored_at` decoupling pin; the two-process contention witness under PD-8 mutation probe; the non-electing negative witness; the `as_is_wiring` event-time control; and the per-site table conformance check. `B-57` closes at that leg, not this one.
