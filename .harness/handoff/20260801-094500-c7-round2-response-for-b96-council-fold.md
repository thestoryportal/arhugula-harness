---
status: in-progress
branch: b96-council-ceiling
timestamp: 2026-08-01T09:45:00-07:00
files_modified: []
---

## COMPANION to 20260801-093000 checkpoint — C7's round-2 response, arrived AFTER the council orchestrator paused

At resume, this text must be folded into `.harness/council-b96-grace-ceiling-2026-08-01.md` (branch `b96-council-ceiling` @ 035395b9, draft PR #1183). It answers the record's `§11.2b` WIP finding **#2** (the [P1] log-durability falsification routed to C7). Finding #1 (`.tmp-*` omission, routed to C10) is still unanswered — the resume agent must obtain or author C10's response. Finding #3 (TENSION-1 reclassification) is orchestrator-owned.

The verdict (C-2) is UNDISTURBED by everything below.

### C7 round-2 — verbatim (relayed from the voice agent, could not reach its parent)

# C7 — Round-2 response. **CONCEDED.** The replacement is option (c), and it is strictly stronger than what it replaces.

## 1. Concession

**The claim is falsified. I concede without reservation.** [HIGH] I re-verified independently before answering: whole-tree grep of production source across all six packages for `basicConfig` / `dictConfig` / `addHandler` / `logging.config` / `StreamHandler` / `FileHandler` / `configure_logging` / `setup_logging` / `handlers[` / `lastResort` returns **zero matches**. The only `logging` touch in the CLI is `logging.getLogger("harness.runtime.keepalive")` at `harness-runtime/src/harness_runtime/cli/app.py:428`–`:432` — a getter, no handler. With nothing configured on the `harness.*` hierarchy, `logger.warning` falls through to `logging.lastResort` → **stderr, WARNING+, nowhere else**. Nothing accumulates across process exit.

My §4A.1 sentence — *"the report log persists across process boundaries, so successive resets remain comparable"* — is **false of the stock deployment**. I tagged it [MODERATE] and it was wrong; that is the tagging system working.

**Scope, so it is not over-read:** what fails is the *cross-run comparability* premise. It does not touch carrier selection, #11, or #12's content terms. It demotes the log from **durable measurement** to **timely notification** — demotion, not deletion.

**One error that is mine, not the reviewer's find:** I had already established in round 1 that this carrier has no OTel log bridge. The inference *"…therefore it likely has no configured sink either"* was available at that moment and I did not draw it.

## 2. What #6 says instead — **option (c)**, and it dominates

**(c) is correct, and better than log-repetition ever could be.** [HIGH]

Round 1's argument was a **TREND** argument — compare successive emissions, watch the age grow. A trend check needs memory, therefore a durable sink. **The pull surface makes it a LEVEL argument.** Condition #7 states the healthy bound (≈2×TTL plus the sweep interval). An operator reading the oldest-resident-entry age on demand and finding it ≫ that bound has **falsified "the store is bounded" from a single read** — no comparison, no history, no sink. **A level check against a spec'd bound needs no memory; a trend check does.**

**It delivers attribution too, at the same read, with zero new state** — the surface can report the record's three-way state (present-and-readable / absent / present-but-unreadable), one `stat()` plus one read of a single file, exactly what #6 and #11 already perform:

| record state | age ≫ #7 bound | reading |
|---|---|---|
| present + readable | yes | **sweeps are not running** — the write-driven-cadence gap (§3.5(a) / §9 item 1) |
| absent | yes | **the repeating sidecar-loss loop** — C3 §3.5(b)(3)'s assumption, now measured |
| present + unreadable | yes | **condition #11's fault, persisting** |
| any | no | bound holds |

**The structural reason (c) works and (b) cannot — a general principle neither voice nor the reviewer stated:** [HIGH] the loss channel is *defined* as "preserves `*.entry`, drops the sidecar." Any diagnostic keyed on the sidecar, or co-resident with it, is destroyed by the event it exists to detect. The pull surface's signal is carried by **the entries' own mtimes — the substrate the fault PRESERVES**. *Measure the fault on the substrate the fault preserves.*

**Consequence:** #6 = timely notification; **#8(b) = authoritative diagnostic**. The separation I should have drawn in round 1.

## 3. Ruling out the other options

**(a) — REJECT as written; adopt one residue.** [HIGH] Making #7's bound conditional on a durable emission sink is a **category error**: the bound depends on record presence/readability and sweep cadence. Whether anyone is *watching* is not a term in it — conditioning it on observability would make the store's retention property change when a log config changes. **Residue adopted:** the spec must not ASSERT log durability; that assertion is struck and replaced with an explicit deployment-configured statement.

**(b) — DIES, more cleanly than option (i) did.** [HIGH] A durable reset counter in the store root is taken by the same backup/copy/cleanup that takes the record — and is **worse** than the init marker I killed at Q1, because its sole purpose is to count the events that destroy it. **Self-defeating by construction.** Inside the record: destroyed with it. Outside the root: a second carrier, outside ratified `(C-i)`. **Had (b) survived, my Q1 kill of (i) would have been special pleading. It does not; consistency holds.**

**Unchanged limitation:** [SPECULATIVE] none of this reaches the **loss-everything** loop — a cleanup one directory left destroys the entries too, the age resets, nothing is measurable. As flagged in round 1.

## 4. Verbatim replacements — three sites move; **#11 untouched**

### #6 — replacement (supersedes round-1 text in full)

> **6. (C-b) A grace RESET is emitted as an OBSERVED FACT, never as a diagnosis — and the AUTHORITATIVE diagnostic is condition #8(b), not this emission.** Whenever a sweep finds that the root holds one or more past-TTL entries and no observation record was read, the sweep MUST emit a report-log line (condition #12's carrier) stating the observed state and nothing beyond it: that **no observation record was read**, the **count** of past-TTL entries found, and the **age of the oldest resident entry** (condition #8's sweep-time value, from the same `stat()` pass) — and therefore that a **fresh grace begins** for every name in that set. **The line MUST NOT assert, name, or classify the record as LOST.** At the first sweep of a store that predates the record, the observable state — entries present, record absent — is IDENTICAL to genuine loss, and no state the store may hold distinguishes them: a durable initialization marker, or a durable reset counter, would live in the same root and be removed by the same selective backup, dotfile-skipping copy, or operator cleanup that removes the record, so each **fate-shares with the artifact it would discriminate** — and a reset counter is additionally destroyed by the very events it counts.
>
> **This emission is a TIMELY NOTIFICATION, not a durable measurement, and the spec MUST NOT claim otherwise.** The report-log carrier's persistence is **deployment-configured**: the harness configures no logging sink of its own, so absent operator configuration the line reaches process stderr and does not survive process exit. **No condition in this section may depend on emission durability for its correctness.** Accordingly, **detection of a repeating loss loop — C3's §3.5(b)(3) assumption, which (C-b) exists to convert into a measurement — is carried by condition #8(b)'s on-demand pull surface**, which reads a **LEVEL against condition #7's stated bound** and therefore requires no history, no comparison across emissions, and no configured sink. This emission remains owed because it is the only signal contemporaneous with the reset, and it is durable in any deployment that configures a sink.
>
> **Emission is unconditional and per-occurrence** — it MUST NOT wait for a second occurrence or attempt in-process suppression, since in the one-shot shape there is no second occurrence within one process to wait for. **The record is written at every sweep that runs, including when the observed set is empty**, per condition #9's replace-not-accumulate semantics; the spec MUST NOT state or imply that this makes a later absence unambiguously loss. Requires no state the store does not already have.

### #7 — clause (c) only; (a) and (b) unchanged

> **(c)** the bound is **conditional on the observation record being present and readable**, and that condition is **contemporaneously emitted per condition #6 AND readable on demand per condition #8(b)** — the pull surface being the **authoritative** means, since the emission's durability is deployment-configured. **Observability is NOT a term in the bound itself:** the bound depends on record presence/readability and sweep cadence, never on whether an emission was captured.

### #8 — replacement of sub-paragraph **(b)** only (preamble, (a), the `I` paragraph, the discriminator sentence unchanged)

> **(b)** an **operator-facing READ-ONLY enumeration of the store on the existing `harness-inspect` admin CLI, requiring no sweep**, on the §13.7 precedent (`:1288`–`:1302`): an **extension of the existing `harness-inspect` row, not a new subcommand**; **engaging only when the store root exists**, with output byte-unchanged otherwise; computing the **same `stat()`-derived oldest-entry age at read time**; and **stating in its own output what it cannot tell** — that the value is a snapshot at read time and that the presence of entries does not imply a sweep will run.
> **It MUST additionally report the observation record's own state, THREE-WAY: present-and-readable / absent / present-but-unreadable** — one `stat()` and one read of a single file, exactly what conditions #6 and #11 already perform, and **zero new persistence**. Crossed with the age against condition #7's bound, this discriminates the three causes of unbounded retention on demand: record readable + age over bound ⇒ **sweeps are not running**; record absent + age over bound ⇒ **the repeating sidecar-loss loop**; record unreadable + age over bound ⇒ **condition #11's fault, persisting**.
> **(b) is owed by THIS leg and carries TWO loads.** First: all three sweep triggers are event-driven, so under (a) alone the oldest-entry age is emitted least often exactly as it grows largest, and a quantity produced only by the mechanism whose absence IS the fault cannot falsify that fault. Second: **(b) is the authoritative diagnostic for conditions #6 and #11**, whose emissions are not durable by default. The signal (b) reads is carried by **the entries' own mtimes — the substrate the loss channel PRESERVES** — which is why it survives a fault that destroys every sidecar-resident artifact.

### #12 — one clause appended (content / cardinality / redaction terms unchanged)

> **Carrier durability is DEPLOYMENT-CONFIGURED and MUST NOT be assumed.** The harness configures no logging sink; absent operator configuration these lines reach process stderr and do not survive process exit. **No condition in this section may depend on emission durability for its correctness** — the durable, queryable surface is condition #8(b).

## 5. The missing logging configuration — **Class-3, routed, NOT owed here**

**Out of scope for this leg; owed as a NEW register row.** [HIGH]

It is **workspace-wide, not B-96-specific**: every `logger.*` in the harness has this property, including the four report-log emissions this store already ships (`:830`, `:839`, `:849`, `:855`) under §14.8.11 `:4909`'s existing typed-report-log mandate. It is **pre-existing at HEAD, orthogonal to C-1/C-2, and tightens both forms and HEAD identically** — precisely the discriminator the council used at §3.5(a) and §9 item 1 to route the write-driven-cadence gap out of this filing.

But **surface it, do not swallow it**: **§14.8.11's typed-report-log term is this store's sole forensic surface, and at HEAD that surface has no configured sink in any deployment shape.** A real finding against a spec'd contract term that generalizes to every axis. Recommend a new register row, cross-referenced from this record, in the same shape as the cadence-gap row.

**And it reinforces §2:** #8(b) is a **product** surface with **no configuration dependency** — exactly why the authoritative diagnostic must live there and not in a log, a conclusion that holds whether or not the logging row is ever closed.

### END C7 round-2 verbatim

## Resume-fold instructions (delta on the 093000 checkpoint's step 2)

1. Relaunch a council-fold agent on `b96-council-ceiling`: fold this C7 response — WIP finding #2 RESOLVED via C7's option (c) with the four verbatim replacement sites (#6 full, #7(c), #8(b), #12 appended clause).
2. Still open in the record: finding #1 (`.tmp-*` closed-set omission — routed to C10; obtain/author C10's answer) and finding #3 (TENSION-1 reclassification — orchestrator-owned).
3. NEW REGISTER ROW owed (Class-3, from C7 §5): workspace-wide missing logging-sink configuration — §14.8.11's typed-report-log term has no configured sink in any deployment shape (zero handler config in any production src tree; `logging.lastResort` → stderr only). Same shape as the write-driven-cadence-gap row; cross-reference from the council record. Register it at the next register touch (likely the B-96 spec leg PR or the council-record finalization PR).
4. Then finish adversarial/codex reconcile-to-zero, un-draft PR #1183.
