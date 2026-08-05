# Class 2 Fork — B-96: the protected result store's `gc_sweep` grace bound — sweep-COUNT vs elapsed-TIME

**Status: RATIFIED 2026-08-05 as READING C, ceiling sub-decision C-2** (filed 2026-08-01 at PR #1179; the held C-1/C-2 sub-decision resolved by the convening at `.harness/council-b96-grace-ceiling-2026-08-01.md`, merged at PR #1183). See `## §11 RATIFICATION` at the foot of this file. Doc-only filing per the workspace
codex-context-guard rule (fork FILINGS ship doc-only FIRST; no `design-substrate/**` edit rides this
PR). Chain mirrors `B-107`'s, `B-97`(a)'s and `B-65`'s: **filing (this PR) → operator ratification →
spec leg (if owed) → impl leg.**

**Register row.** `B-96` at `.harness/forward-register.yaml:2860`–`:2911` (`status:
registered_finding`, no `pr:`) + prose at `.harness/post-phase-8-forward-register.md:1002`. The row's
`pr:` pointer and any status change ride the **ratification** leg, not this PR.

**Grounding HEAD.** `6d557c26`. Every `§`/line cite below was re-resolved by direct read at this
HEAD. **One anchor moved from the row's grounding and is recorded rather than silently normalized:**
the row cites the Runtime spec's bounded-retention bullet as *"Runtime v1.108 §14.8.11 … `:4883`"*;
at this HEAD the spec head is **`v1.109`** (`Spec_Harness_Runtime_v1.md:1`) and the bullet is at
**`:4909`** (heading `### §14.8.11` at `:4898`). **The bullet text is byte-identical** — the row's
"unchanged across v1.106→v1.108" carry extends to v1.109, verified by direct read (§10).

**What this filing does NOT do.** It does not re-litigate `B-77`'s landed grace (ratified, shipped at
PR #1163), does not re-open the two-stamp `_publish_atomic` pipeline (three prior wrong mechanism
claims are on that file's record — a fourth is the exact non-convergent-hardening pattern this
workspace stops on), and does not narrow `ttl_seconds` (`B-74`'s explicitly declined option). It
**corrects the row's own close_out** where grounding falsifies it, and composes the result into the
operator's decision.

---

## §1 The question, and what carries it

`gc_sweep`'s `B-77` first-observation grace refuses to reclaim an entry the store has not already
seen past TTL at a **prior sweep of the same root** (`protected_result_store.py:863` `_observe_expired`
+ the module-level registry at `:111`). The grace's duration is therefore **a count of sweeps, not an
interval of time** — and on a short or immediately-failing run the two sweeps that bracket it
(bootstrap `stage_4_od.py:123`, shutdown `shutdown.py:800`) land milliseconds apart.

The row's registered `close_out` replaces that with an **elapsed-TIME** bound: record
`first_observed_at` alongside the filename in `_root_observed_expired`, and reclaim only when **both**
the mtime-derived age **and** `now - first_observed_at` exceed `ttl_seconds`. Its declared,
ratification-owned tradeoff is that the conservative rule *"lengthens worst-case retention of a
genuine crash orphan by up to one full TTL (a day at the factory default)"* against Runtime
§14.8.11's bounded-retention term — *"a signing outage must not grow an unbounded store of sensitive
payloads"* (`Spec_Harness_Runtime_v1.md:4909`, byte-verified).

**This filing's grounding pass finds the close_out's MECHANISM sound and its PRICING wrong, in
opposite directions.** `[HIGH]`

- The elapsed-time bound is **stronger** than the row claims: it does not merely lengthen the grace,
  it makes wrongful reclaim **structurally impossible** for *every* mtime-under-report source —
  closing `B-74`'s still-open residual and `B-77`'s residual in the same move (§3(ii)).
- The elapsed-time bound **as the close_out writes it** is **worse** than the row claims: with
  `first_observed_at` stored in the existing in-process registry, worst-case retention in the
  **dominant one-shot process shape is UNBOUNDED**, not "one full TTL" — a direct failure of the very
  §14.8.11 term the close_out prices it against (§3(i)).

So the row's decision surface is not "count vs time." It is **"count, or time-with-durable-state"** —
with the close_out's own written variant (time-without-durable-state) **dominated by both**.

---

## §2 Current behaviour at HEAD `6d557c26`

| Surface | State |
|---|---|
| **The grace mechanism** | `gc_sweep` (`protected_result_store.py:650`) verifies past-TTL candidates under `self._publish_lock` + `_cross_process_lock()`, calls `_observe_expired` (`:863`) with this sweep's past-TTL filename set, and reclaims **only** names the PREVIOUS sweep recorded |
| **The observation registry** | `_root_observed_expired: dict[str, frozenset[str]]` — a **module-level, in-PROCESS** dict (`:111`), guarded by `_root_observed_expired_guard` (`:112`), keyed by the root's **filesystem identity** (`_root_identity_key`, `:115`). Stores **filenames only**, no timestamp. `_observe_expired` **REPLACES** rather than accumulates (`:879`) — that is what keeps it bounded |
| **Age authority** | The entry FILE's `st_mtime`, compared against wall-clock `now` (`:753`, `:774`, `:784`, `:791`) — the only four `st_mtime` reads of this store anywhere in production code. The encrypted envelope's embedded `written_at` is deliberately NOT the authority (`B-68`) |
| **The two mtime stamps** | `_publish_atomic` (`:479`) stamps **pre-commit** on the temp file (`os.utime(tmp_name, None)`, `:557`) then commits (`os.link`, `:570`; `_fsync_dir`, `:571`) then stamps **post-commit** on the entry (`os.utime(entry_path, None)`, `:581`) |
| **Sweep triggers — THREE** | bootstrap `stage_4_od.py:123`; shutdown step 5b `shutdown.py:800`; opportunistic `_maybe_opportunistic_gc_sweep` (`:882`) fired from inside `write_once` at most once per `_OPPORTUNISTIC_GC_INTERVAL_SECONDS` = **300.0** (`:72`), gated on the **per-INSTANCE** `self._last_gc_at` (init `0.0` at `:323`, set at `:860`) |
| **TTL config** | `protected_result_store_ttl_seconds: float = Field(default=86400.0, gt=0.0, allow_inf_nan=False)` (`harness-runtime/src/harness_runtime/types.py:1827`). **`gt=0.0` only — NO resolution floor.** A sub-millisecond TTL is a SUPPORTED configuration (the ground on which `B-74` round 1's "no realistic operator would" dismissal was rejected) |
| **Process shapes — TWO** | one-shot `harness run` (`cli/app.py:342`, `asyncio.run(_api_run(...))`, every exit path a `typer.Exit`) — **one run per process**; and the daemon (`cli/app.py:615` → `_daemon_main`) — **one long-lived process, one shared store instance, many runs** |
| **Store construction** | exactly one non-test site: `bootstrap/factories/protected_result_store_factory.py:78`, invoked from `bootstrap/stage_4_od.py:89`. A FRESH instance per `run()`/`resume()` bootstrap |
| **Repair-flow consumer** | **NONE.** `read()` (`:592`) has **zero** production call sites; `ack_delete()` (`:643`) has **zero** production call sites and exactly ONE caller in the entire repo, a test (`test_lifecycle_protected_result_store.py:487`). The only production consumers are write-side (`resolve_result_ref`, `:953`; `resolve_result_ref_off_loop`, `lifecycle/audit_offload.py:353`) and GC-side. No `harness repair`/`recover` CLI command exists |
| **Grace witnesses** | 4 dedicated (`test_lifecycle_protected_result_store.py:1795`, `:1862`, `:1899`, `:1924`) + 2 registry-shape (`:1985`, `:2033`); **11** call sites of the `_sweep_past_grace` double-sweep helper (`:37`), out of **47** total `gc_sweep(` calls across **62** tests in that file (recounted programmatically) |

---

## §3 Five grounding findings that reshape the row

### (i) THE REGISTRY IS IN-PROCESS — and its direction is FAVOURABLE for the crash case, ADVERSE for retention `[HIGH]`

`_root_observed_expired` (`:111`) is a module-level dict. A `first_observed_at` stored there is
destroyed by process exit — including the crash the grace exists to survive.

**This is not an oversight.** `B-77`'s ratified `close_out` states the judgment in terms:
*"A fresh PROCESS legitimately starts with an empty registry — it cannot distinguish a genuine age
from a crash-window artifact, so granting the grace is the safe direction, and that IS exactly the
crash-recovery case."* The same reasoning is carried in the code comment at `:105`–`:110` and pinned
by a dedicated witness (`test_observation_record_is_shared_across_instances_of_one_root`, `:1985`,
whose docstring records it as a merge-gate BLOCKING finding on PR #1163).

**So for the LIVENESS side, a fresh registry is correct** — the recovering process's bootstrap sweep
is exactly where the observation must start, and starting empty grants the grace rather than denying
it.

**For the RETENTION side under an elapsed-time bound, it is fatal.** Reclaim under the close_out's
rule requires `now - first_observed_at > ttl_seconds` **measured inside one process**:

| Process shape | Effect |
|---|---|
| **one-shot `harness run`** (`cli/app.py:342`) — process ≈ one run, typically seconds-to-minutes, TTL default 86400s | the grace clock **never** reaches TTL before the process exits; the next process starts it over. A **genuinely expired** entry — not just a crash-window one — is **NEVER reclaimed**. Retention **UNBOUNDED** |
| **daemon** (`cli/app.py:615`) — one process, lifetime ≫ TTL | the clock accumulates as intended; reclaim at `first_observed_at + TTL`. Retention ≈ **2×TTL**, exactly the close_out's stated price |

The close_out's *"up to one full TTL"* pricing is therefore **true of the daemon shape only** and
**false of the one-shot shape**, which is the harness's documented minimal-config entry point. This
is the finding that removes the close_out **as written** from the viable set: it does not trade
against §14.8.11's bounded-retention term, it **violates** it.

### (ii) THE PUBLICATION-BOUND LEMMA — an elapsed-time grace closes the wrongful-reclaim class for every Δ, subject to three named qualifications `[HIGH]`

Let `t_pub` be the moment the entry became durably committed (`os.link` at `:570` + `_fsync_dir` at
`:571`), `m` its stored mtime, and **Δ = t_pub − m ≥ 0** the mtime under-report. Three sources of Δ
are on the record:

| Source | Δ |
|---|---|
| normal path | ≈ 0 — the post-commit stamp (`:581`) sets `m ≈ t_pub` |
| **`B-77` crash window** | crash strictly between `:570` and `:581` leaves `m` = the pre-commit stamp (`:557`) ⇒ Δ = metadata-fsync + `os.link` + dir-fsync duration |
| **`B-74` coarse filesystem** | the volume rounds the stored value DOWN by up to its own granularity ⇒ Δ ≤ G (up to ~1s at 1-second resolution) |

A sweep reclaims when `t − m > TTL`. The reclaim is **wrongful** (a live entry destroyed) when also
`t − t_pub ≤ TTL`. Substituting: the wrongful window is `t ∈ (t_pub + TTL − Δ, t_pub + TTL]`, of
width Δ — and when **Δ > TTL** it opens **before publication**, i.e. the entry is **born looking
expired** and any sweep in its whole life reclaims it. That second regime is exactly what
`test_coarse_filesystem_mtime_granularity_does_not_lose_a_live_entry_on_sight` (`:1924`) constructs
(TTL 0.1s, floored-to-whole-second stamps ⇒ Δ ≈ 1.0s).

**Under the sweep-COUNT grace**, reclaim moves to the SECOND sweep after the entry starts looking
expired. That cures the wrongful window only when the **inter-sweep gap exceeds Δ** — which is not
guaranteed, and is exactly the `B-74` **REGISTERED RESIDUAL** pinned as an executable assertion at
`:1982` (`assert store.gc_sweep(now=time.time()) == [entry_path.stem]`, comment at `:1978`).

**Under an elapsed-TIME grace**, reclaim is at `t_first_obs + TTL`. And `t_first_obs ≥ t_pub` **by
construction** — a sweep enumerates `*.entry` files, and the entry does not exist until `os.link`
commits it. Therefore:

> **reclaim ≥ t_pub + TTL — never before the entry's true expiry, for ANY Δ, on ANY filesystem.**

That is precisely *"an age authority that cannot predate publication by construction"* — the phrase
`B-77`'s own close_out names and that `B-74`'s close_out asks for a second way (*"a higher-resolution
age signal (e.g. a companion sidecar file …)"*). **One mechanism closes `B-96`, the `B-77` residual,
and `B-74`'s remaining scope together.** The row's framing of the elapsed-time variant as merely "a
longer grace" **understates** it.

**Two qualifications, added at out-of-family rounds 2–4 and load-bearing for §4/§6/§7.** `[HIGH]`

**(a) The lemma is a property of the GRACE TERM ALONE — so it transfers to C-2 unconditionally and
to C-1 only partially** (round 4 [P2]). Reading C-1 adds an **absolute mtime-keyed reclaim ceiling**
(§4) as a second, *non*-publication-bounded reclaim term; whenever `Δ > (k−1)·TTL` that term fires
first and the lemma does not govern the outcome. **C-2 carries no such term, so under C-2 the lemma
IS the reclaim rule.** This is exactly the C-1 ⊥ C-2 split §4 holds and §7 convenes on — the lemma
does not, by itself, settle it.

**(c) The lemma constrains WHERE `first_observed_at` is sampled — a REQUIRED implementation term,
not impl discretion** (round 5 [P1], verified by direct read). `gc_sweep` samples
`current_time` at `:714`, **before** its deliberately-unlocked enumeration pass and before the lock
is taken; `_observe_expired` runs much later, at `:797`, **after** locked re-verification. Recording
`current_time` as `first_observed_at` would therefore break `t_first_obs ≥ t_pub` outright: a
concurrent cross-process publisher can stamp its temp file, the sweep can sample `now`, and the
publisher can then `os.link` and crash before the post-commit stamp — leaving a record whose
timestamp **predates** publication, from which C-2 can reclaim before one true TTL. **The timestamp
MUST be sampled at the `:797` observation point, under the lock, not at `:714`** — with the
`gc_sweep(now=…)` injection seam extended accordingly so the witness recipe can still drive it.
Carried into §9's impl row as a named acceptance condition rather than left to discretion.

**(b) The lemma assumes a wall clock that does not step BACKWARD between publication and first
observation** (round 4 [P1]). `t_first_obs ≥ t_pub` is a statement about clock *readings*; a
backward NTP step in that interval can make the later reading the smaller one, and reclaim can then
fall short of one true TTL after publication. This is a property of the store's wall-clock age
authority as a whole — the shipped `now − mtime` comparison is perturbed by the same step in the
same direction — not a defect this grace introduces (§5.2), but the lemma is stated with the
assumption rather than without it.

**Cost, stated exactly:** worst-case retention becomes `t_first_obs + TTL ≈ t_pub + 2·TTL` (+ sweep
phase). Bounded — and "bounded" is the whole of what §14.8.11 requires (`:4909`: *"must not grow an
**unbounded** store"*). It does **not** require reclaim at exactly TTL.

### (iii) THERE IS NO REPAIR FLOW AT HEAD — the liveness side is entirely PROSPECTIVE `[HIGH]`

`read()` (`:592`) and `ack_delete()` (`:643`) have **zero** production call sites anywhere in
`harness-*/src/`, `tools/`, or the CLI (verified by a whole-tree sweep; `ack_delete` occurs on
exactly 4 lines repo-wide, three of them its own definition/comment and one a test at
`test_lifecycle_protected_result_store.py:487`). The CLI command set is `run`, `daemon`, `inspect`,
`shutdown`, `migrate-audit-sidecar`, `adopt-pause-journals`, `dispose-pause-journals` — no repair or
recovery command.

**Both directions of this fact are load-bearing and are stated together, against interest:**

- **For A/D:** the wall-clock repair window the elapsed-time bound buys is a window for a consumer
  that does not exist. Nothing at HEAD reads a crash-recovered entry before the shutdown sweep.
- **For B/C:** the store's entire declared purpose is to hold a completed paid effect's payload
  until a repair flow can recover it (§14.8.11: *"Deletion happens ONLY after an explicit DURABLE
  repair ACKNOWLEDGEMENT … read-then-crash must never destroy the only recoverable copy"*). Sizing
  the grace to "what today's consumers need" sizes it to zero and makes the store's contract
  unimplementable when that consumer lands. §14.8.11 states the retention contract, not the
  consumer's presence, as the requirement.

### (iv) THE 300s OPPORTUNISTIC TRIGGER GIVES SWEEP-COUNT A DE-FACTO FLOOR — in ONE of the two shapes `[HIGH]`

`_maybe_opportunistic_gc_sweep` (`:882`) fires from `write_once` only when
`now - self._last_gc_at >= 300.0` (`:72`), and `_last_gc_at` is set by the bootstrap sweep on that
same instance (`:860`). So the second observation lands at:

- **daemon:** `min(` first write ≥300s after bootstrap, shutdown `)` — a **~300s floor** under steady
  traffic, and the whole process lifetime without writes. The row's "milliseconds" does **not**
  describe this shape.
- **one-shot run:** shutdown, i.e. **the run's own duration** — milliseconds for a short or
  immediately-failing run. The row's characterization is exact here.

One nuance the `B-77` arc already recorded (`:1985` docstring): a FRESH instance's `_last_gc_at = 0.0`
makes its first `write_once` always fire an opportunistic sweep — so in any path where a store is
constructed and written to **without** the bootstrap sweep, that first write is itself sweep 1. On
the real bootstrap path (`stage_4_od.py:123` sweeps the same instance the factory built) it is not.

### (v) THE B-74 INTERACTION — an elapsed-time bound FLIPS a deliberately-pinned assertion, and the pin was placed for exactly that `[HIGH]`

`B-74`'s row narrows its remaining scope to *"a rounding error EXCEEDING the gap between two
consecutive sweeps"*, and pins it at `:1982`. Under an elapsed-time bound that assertion becomes
`== []` (the witness's two sweeps are microseconds apart, far under the 0.1s TTL), with reclaim
moving to a third sweep ≥0.1s later — **and the entry survives its full true lifetime**, which is the
`B-74` fix.

The pin's own comment anticipates this: *"Pinned here so a future B-74 fix has to come back and
update this witness rather than silently diverge."* **An elapsed-time leg is therefore not merely
compatible with `B-74` — it is the fix `B-74` is waiting for**, and its impl leg owes the witness
update the pin demands, plus a pass over the **11** `_sweep_past_grace` call sites and the
`== [entry_path.stem]` asserts at `:1858`, `:1920`, `:1982`, `:2026`, all of which reach reclaim via
two sweeps at a pinned or near-identical `now`.

---

## §4 The readings

### Reading A — keep the sweep-COUNT bound; record this analysis; CLOSE `B-96`

No code change. The docstring already states the bound plainly (`:703`–`:712`: *"The grace is bounded
by SWEEP COUNT, not elapsed time — stated plainly so it is not read as more than it is"*). `B-96`
closes as a **documented-and-accepted bound**, with §3(ii)'s lemma recorded on the row so the
mechanism is not re-derived, and the wrongful-reclaim residual left where it already lives — open, at
`B-74`.

- **Liveness:** residual persists — an entry dies up to Δ early in the Δ ≤ TTL regime; is lost
  outright in the Δ > TTL regime whenever two sweeps fall inside Δ (the pinned `:1982` residual).
- **Retention:** strongest of the four — reclaim guaranteed within the recovering run.
- **Cost:** zero. **Spec leg:** none owed (status quo, no design extension).
- **Honest weakness:** it accepts a **live-entry loss** as a permanent bound. §14.8.11's typed-expiry
  term licenses reporting the loss of an **expired** entry; it does not license losing a live one.

### Reading B — elapsed-TIME, per-process (the close_out AS WRITTEN)

`first_observed_at` stored beside the filename in the existing in-process registry.

- **Liveness:** fully closed (§3(ii)).
- **Retention:** **UNBOUNDED in the one-shot process shape** (§3(i)) — a §14.8.11 failure, not a
  trade.
- **Verdict: DOMINATED.** It is strictly worse than C on retention and identical to C on liveness.
  **Not recommended under any weighting.** It is listed because it is what the row's `close_out`
  currently prescribes, and the ratification must retire it explicitly rather than let an impl leg
  build it as written.

### Reading C — elapsed-TIME with DURABLE observation state (the coherent form)

`first_observed_at` persisted per (root, filename) so the grace clock survives process exit.

**C carries ONE internal sub-decision, and this filing HOLDS it rather than deciding it a fourth
time.** `[HIGH]` Out-of-family review moved the absolute-ceiling element three times across rounds
1–3 (introduced → qualified → falsified as a closure claim). Per
`[[reviewer-oscillation-register-and-hold]]`, a third movement on one element is the stop signal:
**both forms are stated below as C-1 / C-2, the recommendation names one, and the adjudication is
routed to the council convening the row itself prescribes (§7) rather than re-decided in another
review round.**

**Common to both forms:**

- **Crash-atomic persistence — by ATOMIC REPLACE, explicitly NOT the write-once primitive**
  (out-of-family round 2 [P2], upheld on direct read). The record is **mutable** — its observation
  set changes at every sweep. The store's entry primitive and `RuntimeEffectFence.capture_output`
  are deliberately **no-replace**: `os.link` raises `FileExistsError` and the first publication wins
  (`lifecycle/effect_fence.py:317`–`:319` — *"Capturing twice … is a no-op: the first published
  output wins (`os.link` raises `FileExistsError`)"*), so borrowing it would freeze the record at
  its first snapshot, and unlink-then-relink would open a window in which the record reads
  **absent** and the grace restarts. **The correct primitive is temp-write + `fsync` +
  `os.replace` + directory `fsync`** — atomic on POSIX, no absent window. This makes **corrupt**
  unreachable (a torn write leaves only an orphan temp), leaving **absent** as the sole loss state.
- **Fail-safe direction:** an absent record reads as **no observation**, granting a fresh grace —
  so record loss can only ever **lengthen** retention, never cause a premature reclaim.
- **Carrier:** see the sub-options below.

**C-1 — with an ABSOLUTE mtime-keyed reclaim ceiling.** Reclaim unconditionally when
`now − mtime > k × ttl_seconds` (k = 2 natural default), **regardless of the grace term**.

- **Retention:** **k×TTL + the next-sweep delay** — bounded independently of the observation
  record (the ceiling never consults it), but **not** independent of sweep cadence, which is
  trigger-driven at HEAD and under both forms alike (round 5 [P2]; the earlier "unconditionally"
  overstated it). Under total record loss the ceiling still fires; under no further sweep, nothing
  fires — for C-1 and C-2 equally.
- **Liveness:** **NOT a uniform narrowing — in the `Δ > (k−1)·TTL` regime it is a REGRESSION
  against HEAD** (out-of-family round 4 [P1], upheld; round 3 [P1] had established the residual but
  mis-signed it). The ceiling fires **unconditionally**, so at `B-74`'s own witness values
  (`ttl_seconds=0.1`, Δ≈1.0s, k=2) `now − mtime > 0.2` is already true at the **bootstrap** sweep
  and the entry **can be** reclaimed **on first observation** — which is precisely what HEAD's
  sweep-count grace *always* prevents. **Stated exactly** (round 5 [P2]): with observation delay
  `s` after publication, first-sweep reclaim needs `s + Δ > k·TTL`; `Δ > (k−1)·TTL` makes the
  ceiling *eligible* before true expiry, and a small `s` makes it *fire*. At `k=2`, `TTL=1`,
  `Δ=1.1`, `s≈0` the ceiling is still false and HEAD's grace applies — so this is a **"can", not a
  "must"**, and is not claimed as more. And because `ttl_seconds` has no floor (`types.py:1827`, `gt=0.0`), the
  same regime is reachable for the `B-77` crash-window Δ (needs `ttl_seconds ≲ Δ_crash`). So C-1 is
  a large improvement for `Δ ≤ (k−1)·TTL` (residual moves from *"Δ exceeds the inter-sweep gap"*,
  milliseconds, to *"Δ exceeds (k−1)·TTL"*, a full TTL) and **strictly worse than doing nothing**
  above it. **This materially reprices the held sub-decision and is the strongest single argument
  for C-2.**

**C-2 — no absolute ceiling (the grace term alone).** Reclaim when `now − mtime > TTL` **and**
`now − first_observed_at > TTL`.

- **Liveness:** **fully closed for all three rows** — §3(ii)'s lemma holds unconditionally, because
  the only term that can predate publication is removed from the reclaim decision.
- **Retention:** ≈**2×TTL + one inter-sweep interval**, under **two** premises, both stated
  (round 4 [P1] — the cadence premise had been dropped in the C-1/C-2 rewrite and is restored
  here):
  - **Sweep cadence.** `gc_sweep` is **trigger-driven, not periodic** (§2: bootstrap / shutdown /
    the 300s opportunistic write trigger). Reclaim needs a sweep to occur *after*
    `first_observed_at + TTL`; in the one-shot shape that is the **next run**, which may be
    arbitrarily later or never. **This premise is not new to C-2 — HEAD has it too (no sweep, no
    reclaim) — but it is stated because it is presented for ratification**, and under C-2 it
    compounds with the grace rather than being absorbed by a same-run shutdown sweep the way it is
    at HEAD.
  - **Sidecar durability — the fate-sharing claim WITHDRAWN at round 6 [P1], against interest.**
    The round-2 `os.replace` correction removes `corrupt` from the reachable state set and closes
    the **crash** loss channel: a torn write leaves only an orphan temp. It does **not** make the
    sidecar fate-share with the entries. A selective backup/restore, a dotfile-skipping copy, or an
    operator cleanup that preserves `*.entry` while dropping the sidecar leaves **every payload and
    no observation timestamp**, and repeated independent loss resets the grace indefinitely. **So
    C-2's retention bound rests on an operationally INDEPENDENT premise, and the earlier "not an
    independent failure mode" claim is withdrawn.** This is a real input to the §7 convening and it
    strengthens the C7/C8 side: an artifact that must be backed up *together with* the entries is a
    new operational invariant the store does not have today. It does not overturn the §6 point-4
    harm asymmetry (C-1's failure destroys a paid effect's only copy; this one retains too much),
    which is why the recommendation stands — but the convening decides it, not this filing.

**The C-1 ⊥ C-2 choice IS the row's named tension, made concrete** — C-1 buys C7/C8's unconditional
retention bound by conceding C3's publication-bound safety at short TTLs; C-2 buys C3's structural
close by resting C7/C8's bound on the store's existing durability assumption. **Neither is
strictly better** (§7).

**Carrier — RATIFIED BY THE §8 ask, NOT impl discretion** (round 5 [P2]: §8 prices `(C-i)`
specifically, so leaving the set open would let an impl leg build `C-ii`/`C-iii` on an operator
answer that never priced them). **`(C-i)` is the carrier under any C answer; `(C-ii)` and
`(C-iii)` are recorded as REJECTED ALTERNATIVES, with their grounds, so the rejection is not
re-derived:**

- **(C-i) dedicated sidecar** — one file in the store root, name disjoint from BOTH sweep globs
  (`*.entry` and `.tmp-*`), exactly as `_CROSS_PROCESS_LOCK_FILENAME = ".cross_process.lock"`
  (`:96`) already is. Holds **only sha256 digests + timestamps** — no plaintext, no ciphertext, no
  tenant payloads — so it does not widen the sensitive-payload surface §14.8.11 governs. Published
  by `os.replace` under the same `_publish_lock` + `_cross_process_lock` the sweep already holds.
  **Cleanest; recommended carrier.**
- **(C-ii) REJECTED — ride `.cross_process.lock`** — no new file, but it conflates a `fcntl.flock` primitive
  with mutable state, and a crash mid-write corrupts a file the B-73 locking path depends on.
  **Not recommended.**
- **(C-iii) REJECTED — ride the entry's own `atime`** — zero new artifacts (`os.utime(path, (first_obs, m))`
  keeps mtime and repurposes atime). `noatime`/`relatime` mounts do not suppress an EXPLICIT
  `os.utime` set, and an implicit atime bump on read only lengthens retention. `[MODERATE]` — but
  it makes correctness depend on a filesystem attribute the store's contract does not own, which is
  the precise assumption class `B-74` exists because of. **Not recommended.**

**Cost common to C-1 and C-2:** reverses `B-77`'s ratified close_out judgment, verbatim *"No new
config surface, no new public API, **no persisted sidecar**."* That reversal is what makes this
operator-owned rather than an impl choice.

**Spec leg:** **owed.** The grace changes the operational meaning of the spec'd `ttl_seconds`
surface (effective worst-case retention k×TTL / ≈2×TTL). §14.8.11's "Deferred to implementation
discretion" list names the TTL field, the envelope format, the refusal class names and the
repair-ack marker shape — **it does not name a retention-extending grace**. Landing one silently
would be an X-AL-3 design extension.

### Reading D — DEFER `B-96` until a repair-flow consumer exists

Hold the row open; re-decide when `read()`/`ack_delete()` acquire a production consumer, at which
point the required window is a stated requirement rather than an inferred one.

- Honest, and §3(iii) supports it. But it leaves a **live-entry loss** standing indefinitely on a
  contract term that does not license it, and it defers a decision whose inputs are already fully
  grounded — the workspace's ground-every-arc discipline treats "no consumer yet" as a reason to size
  the fix, not to skip it.

---

## §5 The three decisions — how they COLLAPSE to one, and the ONE that does not

### §5.1 Decision (1) — the bound

Sweep-COUNT (A/D) vs elapsed-TIME (B/C). §3(ii) settles the liveness side in favour of elapsed-time
unconditionally; §3(i) settles that elapsed-time is only viable in its durable form. So decision (1)
reduces to **A vs C**.

### §5.2 Decision (2) — wall-clock vs monotonic for `first_observed_at`

**Determined by decision (3), not independent.** `[HIGH]`

| If the state is… | Clock | Why |
|---|---|---|
| **in-process (B)** | `time.monotonic()` would be technically correct — NTP-step immune, and only intra-process differences are ever taken | but it **cannot be driven by the existing `gc_sweep(now=…)` seam** (`:650`), so the close_out's own witness recipe would need a second injection point. Moot: B is dominated |
| **durable (C)** | **WALL-CLOCK, necessarily** | `time.monotonic()`'s reference point is undefined across processes, so a persisted monotonic value is meaningless to the next process |

The NTP objection has a clean answer under C — **sharpened at out-of-family review round 1 [P1],
whose premise is upheld and whose conclusion is not.** `[HIGH]`

**Upheld:** a forward clock step of `X` makes a stored-timestamp comparison fire `X` early in
**true elapsed** terms. Under C that means an entry can be reclaimed after `TTL − X` of real time.

**Not upheld — the lemma is not invalidated, and the exposure is not new:**

1. **Both terms are perturbed identically, and the claim was about the TERMS, not the stored
   values.** `now − m` and `now − first_observed_at` are each `now` minus a stored wall-clock value;
   a forward step of `X` increases **both by exactly `X`**. Nothing about C's grace term is more
   clock-fragile than the mtime term the store has compared since `B-68`.
2. **The same step already fires today.** Under the shipped sweep-COUNT grace, a forward step makes
   `now − m > TTL` fire `X` early and the entry is reclaimed at the next sweep. C adds no new clock
   channel — it adds a second term on the **same** clock.
3. **The publication-bound lemma survives FORWARD steps, and requires an explicit assumption
   against BACKWARD ones** (sharpened at round 4 [P1] — the round-2 text asserted "a step can only
   push `t_first_obs` later", which is true of forward steps and **false of backward ones**).
   Reclaim is at clock-reading `t_first_obs + TTL`, and `t_first_obs ≥ t_pub` **as clock readings**
   (the sweep read `now` after `os.link` made the file visible) **provided the clock does not step
   backward in that interval**. A *forward* step only makes `t_first_obs` larger, pushing reclaim
   later; a *backward* step can make the later reading the smaller one, and reclaim can then fall
   short of one true TTL after publication. The same backward step perturbs the shipped
   `now − mtime` term identically and in the same direction, so this is a property of the store's
   wall-clock age authority, not a defect the grace introduces — but the lemma is stated **with**
   the assumption (§3(ii) qualification (b)), not without it. So `reclaim ≥ t_pub + TTL` holds
   unconditionally on the clock the store's TTL is *defined* in. `ttl_seconds` has always been a
   wall-clock quantity here (it is compared against `st_mtime`); a forward step shortens **every**
   TTL term in the store identically, which is a property of the store's clock choice, not of this
   grace.
4. **It is not a choice C could have made differently.** §5.2's table shows a durable record forces
   wall-clock — a persisted `time.monotonic()` is meaningless to the next process. The only
   clock-immune alternative is in-process monotonic, i.e. Reading B, which §3(i) disqualifies on
   retention. **There is no reading that is both cross-process and clock-step-immune.**

Wall-clock also rides the existing `now=` injection seam (`:650`), which is what makes the
close_out's witness recipe (bootstrap-then-shutdown pair, under and over the interval) writable at
all. **Position: WALL-CLOCK, with the true-elapsed compression recorded as an accepted, pre-existing
property of the store's clock choice — not as a defect this reading introduces.**

**Position: WALL-CLOCK.**

### §5.3 Decision (3) — durable observation state, or per-process?

**Durable, if elapsed-time is taken at all.** §3(i) is dispositive: per-process elapsed-time is not a
weaker version of the fix, it is a §14.8.11 regression in the harness's dominant process shape. There
is no middle option — no arrangement of in-process state can measure an interval that outlives the
process holding it.

### §5.4 The collapse — and the one sub-decision that does NOT collapse

Decision (2) is determined by (3); decision (3) reduces the elapsed-time family to a single coherent
family; decision (1) therefore reduces to **A vs C**. **The operator faces ONE primary decision.**

**One sub-decision survives inside C and is HELD, not collapsed:** the **C-1 (absolute mtime
ceiling) ⊥ C-2 (grace term alone)** choice of §4. It is not resolvable by grounding — both forms are
internally consistent and each concedes exactly what the other buys — so it is routed to the
council convening the row's `council` field prescribes (§7) and carried as the ratification ask's
second part (§8).

---

## §6 Recommendation — **Reading C, form C-2**, carrier (C-i). Runner-up: **Reading A**.

`[HIGH]` **Recommend C.**

1. **It closes a genuine contract violation rather than documenting it.** §14.8.11's typed-expiry
   term licenses reporting the collection of an **expired** entry (`:4909`: *"TTL expiry surfaces as
   a TYPED report-log line, never silent loss of the last reference to a paid effect"*). Losing a
   **live** entry is outside what that licenses, and A accepts it permanently.
2. **The publication-bound lemma (§3(ii)) is a structural property of the GRACE term.** Reclaim ≥
   `t_pub + TTL` holds for every Δ on every filesystem as far as the grace is concerned, because a
   sweep cannot observe a file that does not yet exist. Nothing weaker has that property — including
   a TTL floor, which requires knowing the volume's real resolution (the reason `B-74` has stayed
   open). **Under C-2 the lemma is the whole reclaim rule and therefore holds unconditionally; under
   C-1 the ceiling is a second, non-publication-bounded term that can override it** (out-of-family
   round 3 [P1]).
3. **Row disposition, stated per form rather than over-claimed** (corrected across rounds 2–3; the
   first draft claimed a clean triple close, and round 3 showed the ceiling narrows even `B-96`/
   `B-77` at a short enough TTL):
   - **Under C-2:** `B-96`, `B-77`'s residual and `B-74`'s remaining scope **all close** — all three
     reduce to "mtime under-reports publication," and removing mtime from the reclaim decision
     removes the class. `B-74`'s `:1982` pin flips to `== []` and is re-pinned, exactly as its own
     comment instructs.
   - **Under C-1:** all three are **NARROWED for `Δ ≤ (k−1)·TTL`, and can be REGRESSED above it**
     (round 4 [P1], bounded precisely at round 5 [P2]) — where `s + Δ > k·TTL` the ceiling reclaims
     on **first** observation, which HEAD's grace always prevents. All three rows stay open; `B-74`'s pin is re-pinned against the
     new arithmetic rather than deleted; and the regression itself needs its own witness.
   - Either way, advisor()'s cross-reference on the `B-76` arc — recorded verbatim in `B-74`'s row:
     *"ground as a single does-the-age-authority-stay-mtime question before building either in
     isolation"* — is satisfied by C and by nothing else.
4. **Why C-2 over C-1** `[MODERATE]` — **the asymmetry of harm.** C-1's failure mode is *"a
   completed paid effect's only recoverable copy is destroyed"*; C-2's is *"expired entries linger
   until the sidecar is restored or the entries are cleaned up."* The second is recoverable and
   observable; the first is not. **The round-6 [P1] correction is priced in and stated against
   interest:** C-2's bound does rest on an **operationally independent** premise — a selective
   backup/restore or dotfile cleanup can drop the sidecar while keeping every entry — so C-2 adds a
   new operational invariant (back the sidecar up with the entries) that the store does not have
   today. The harm asymmetry is what carries the recommendation past that cost, not an absence of
   cost. **This is the recommendation the council convening (§7) adjudicates; it is not asserted as
   settled.**
5. **The reversal it asks for is narrow and honest.** `B-77`'s "no persisted sidecar" was a scoping
   judgment made when the grace was a filename set with no time dimension; adding a time dimension is
   precisely what changes the calculus. Surfacing it as the ratification ask (§8) is the correct
   handling — not silently overriding it in an impl leg.

**Recommend AGAINST B explicitly.** The row's `close_out` as written must be **amended, not
executed**. An impl leg that builds it verbatim ships an unbounded-retention regression in the
one-shot shape.

**Runner-up: A.** `[MODERATE]` If the operator weights §3(iii) decisively — no repair consumer
exists, so the liveness benefit is prospective while the new durable surface is immediate — then A is
defensible: close `B-96` with §3(ii)'s lemma recorded, leave `B-74` open as today, and revisit when a
repair flow lands. **A is preferred over D**: both defer the fix, but A records the analysis and
retires a row, whereas D leaves a row open whose inputs are already fully ground and whose only
missing input (a repair consumer) does not change §3(ii).

**§6.1 Stated against interest.** `[HIGH]` The reachability floor for the wrongful reclaim is narrow
and unchanged from `B-74`/`B-77`: it needs a deployment `ttl_seconds` short enough that Δ tips a live
entry past it — Δ ≈ milliseconds for the crash window against an 86400s factory default (~7 orders of
magnitude), or Δ ≤ ~1s on a coarse volume. `types.py:1827` permits such a TTL (`gt=0.0`, no floor), so
it is a supported configuration and not unreachable — but it is not a default-path exposure, and this
filing does not claim otherwise. C is recommended on **contract-conformance and row-consolidation**
grounds, not on incident likelihood.

---

## §7 Council position — **CONVENE, dyadic, scoped to the ONE held sub-decision. Position REVERSED from this filing's earlier draft, and the reversal is recorded.**

The row's `council` field is **conditional**: *"convene if the elapsed-time variant is taken"*, on a
named tension — **C3** (state-and-persistence integrity, wanting the conservative
publication-bounded age authority) **⊥ C7/C8** (wanting §14.8.11's bounded-retention floor on
sensitive payloads). The recommendation **is** an elapsed-time variant, so the condition fires.

**What the probe DID resolve.** Per the §10.9 probe-first discipline, a direct read of
`Spec_Harness_Runtime_v1.md:4909` establishes that the spec's word is **"unbounded"** — *"a signing
outage must not grow an **unbounded** store of sensitive payloads"* — **not** "must be collected at
exactly TTL." That forecloses the strongest form of the C7/C8 objection: a retention bound of k×TTL
or ≈2×TTL satisfies the term, so "any lengthening violates §14.8.11" is not available.

**What the probe did NOT resolve — and why the earlier draft's "no convening owed" was wrong.**
`[HIGH]` This filing's rounds 1–2 concluded probe-resolved on the strength of an unconditional
retention bound. Out-of-family round 3 [P1] showed that bound is purchased by the C-1 ceiling, and
that the ceiling **concedes C3's publication-bound safety at short TTLs** — reintroducing the very
live-entry loss the arc exists to close. So the tension does not dissolve; it **relocates** into the
C-1 ⊥ C-2 choice, where it is sharp, concrete, and genuinely two-sided:

- **C3 argues C-2** — an age authority that cannot predate publication is the whole point; a ceiling
  that can fire early re-opens the class.
- **C7/C8 argue C-1** — **sweep cadence is a premise of BOTH forms** (round 5 [P2]; the earlier
  "premise-free bound" framing was inaccurate), so the *only* additional premise C-2 carries is
  **sidecar survival**. C7/C8's argument is therefore narrower than first stated but still real: a
  retention bound with one fewer premise is worth paying for where the payload is sensitive.

**Asymmetry the convening inherits, recorded so it is not re-discovered there** (round 4 [P1]):
C-1 **as specified** is not merely a weaker close — above `Δ > (k−1)·TTL` it **regresses against
HEAD**, reclaiming on first observation where today's grace never does. That does not dissolve the
tension (C7/C8's premise-free-bound argument survives, and C-1 admits variants — a record-keyed
ceiling, or a larger `k` — that trade differently), but the convening should treat **C-1 as
specified** as carrying a known regression rather than as the safe default.

**With that recorded, neither position is refuted by any source this filing can reach**, which is the definition of a
convening-eligible tension under the §10.9 nameable-tension discriminator. **Disposition: a dyadic
C3 + C7 convening is OWED at the ratification leg, scoped to the single question "C-1 or C-2" — not
to re-open A vs C, which the grounding above settles.** The probe's partial yield above is carried
into that convening as a pre-bound fact, so it does not re-litigate the "exactly TTL" reading.

Recorded per `[[probe-resolves-fork-prescribed-council]]` **in the negative**: that pattern licenses
skipping a prescribed convening when a primary-source probe resolves the dispute. Here the probe
narrowed the dispute without resolving it, so the licence does not apply — and saying so is the
honest application of the pattern, not an exception to it.

---

## §8 The ratification ask — ONE primary decision, plus ONE held sub-decision if C

**PRIMARY.**

> **Does `B-96` resolve as Reading A (keep the sweep-COUNT bound, record the publication-bound lemma
> on the row, accept the live-entry-loss residual permanently, leave `B-74` open as today) — or as
> Reading C (replace it with a DURABLE, publication-bounded elapsed-time first-observation grace, on
> a dedicated digest+timestamp sidecar published by `os.replace`), accepting the reversal of
> `B-77`'s ratified "no persisted sidecar" judgment?**

**Recommended: C.** **Runner-up: A.**

**SUB-DECISION, only if C — HELD, and routed to the §7 dyadic council convening rather than decided
here** (the element moved three times under out-of-family review; `[[reviewer-oscillation-register-and-hold]]`):

> **C-1 (absolute mtime-keyed reclaim ceiling at `k × ttl_seconds`) — retention `k×TTL + I` (`I` a
> sweep-period bound; the ceiling is evaluated only when a sweep runs), independent of the
> observation record, but `B-96`/`B-77`/`B-74` are NARROWED only for `Δ ≤ (k−1)·TTL` and **can be
> REGRESSED against HEAD above it** — where `s + Δ > k·TTL` (with `s` the observation delay) the
> ceiling reclaims on FIRST observation, which today's grace never does. Or C-2 (grace term alone)
> — `B-96`/`B-77`/`B-74` all CLOSE, with retention up to **2×TTL + 2I** (one interval to the first
> post-TTL observation, one more to the post-grace reclaim), resting on two premises: sweep
> cadence, and **sidecar durability that is OPERATIONALLY INDEPENDENT of the entries** — a
> selective backup/restore or dotfile cleanup that keeps `*.entry` and drops the sidecar resets the
> grace.**

**Recommended within C: C-2**, on the asymmetry-of-harm ground at §6 point 4, reinforced by round 4
[P1] (C-1 **as specified** regresses against HEAD above `Δ > (k−1)·TTL`) — **explicitly subject to
the council's adjudication, not asserted as settled.**

**Carried by any answer, requiring no separate decision:**

- The row's `close_out` is **amended** to retire Reading B (per-process elapsed-time) explicitly, so
  no future impl leg builds it as currently written. Owed under **every** answer.
- If C: `first_observed_at` is **wall-clock** (§5.2); carrier **(C-i)** dedicated sidecar (§4);
  publication by **temp-write + `fsync` + `os.replace` + directory `fsync`**, explicitly NOT the
  write-once `O_EXCL`/`os.link` primitive (§4); record-absence reads as **no observation**.

---

## §9 Sequencing, and what each leg owes

**Chain: this filing → ratification (incl. the §7 convening if C) → (C only) spec leg → impl leg.**

| Leg | Owed under **A** | Owed under **C** |
|---|---|---|
| **Ratification** | operator answer + row `status: closed`, `pr:` pointer, close_out amended to retire B, §3(ii) lemma recorded | operator answer + the §7 dyadic C3+C7 convening resolving C-1/C-2 + close_out amended (retire B; record the selected form) + the "no persisted sidecar" reversal recorded on `B-77`'s row so it is not later read as unratified drift. **Row status → `design_substrate_gated`, NOT `closed`** (out-of-family round 3 [P1]): under C the spec and impl legs are still outstanding, and `closed` would drop live work out of the open-work inventory |
| **Spec leg** | **none owed** — status quo, no design extension | **owed.** A Runtime §14.8.11 amendment stating the first-observation grace and its effective-retention bound (k×TTL under C-1, ≈2×TTL under C-2). `§14.8.11`'s deferred-to-impl list does not name a retention-extending grace, so landing one silently would be X-AL-3. Co-publication with a clearance marker per `CLAUDE.md` §4.5. **Spec + impl do NOT land together**, per the `B-33`/`B-39`/`B-59`/`B-69`/`B-70`/`B-72`/`B-97`/`B-107` precedent |
| **Impl leg** | docstring sharpening at `:703`–`:712` if the ratification wants the lemma in-code; `B-74` row cross-ref refresh | the sidecar published by **temp-write + `fsync` + `os.replace` + directory `fsync`** (NOT `O_EXCL`/`os.link` — corrected at round 2 [P2]; that primitive is no-replace and would freeze the record at its first snapshot) + the selected C-1/C-2 reclaim rule + `_observe_expired` signature change (`:863`); **`first_observed_at` sampled at the `:797` observation point under the lock, NOT at `:714`** (§3(ii) qualification (c) — a named acceptance condition, not discretion), with the `gc_sweep(now=…)` seam extended so the witness can drive it; **witness pass over all grace-dependent tests** — the 11 `_sweep_past_grace` call sites (`:37`) and the four `== [entry_path.stem]` reclaim asserts at `:1858`, `:1920`, `:1982`, `:2026`, each of which currently reaches reclaim via two sweeps at a pinned or near-identical `now`; the `B-74` pin at `:1982` updated as its own comment demands (`:1978`); new witnesses for **cross-process** survival (the property in-process state cannot have), for **bounded** reclaim, and — under C-1 — for the ceiling firing independently of the record; mutation probes on each. **Row status → `closed` only when this leg merges** |
| **`B-96` / `B-77`-residual disposition** | `B-96` closes as documented-and-accepted; `B-77` residual unchanged | **C-2:** both **close at the impl leg**. **C-1:** both **NARROWED, stay open** — the ceiling reaches them at `ttl_seconds ≲ Δ_crash` (out-of-family round 3 [P1]) |
| **`B-74` disposition** | unchanged — stays open | **C-2:** closes at the impl leg, its close_out recorded as satisfied structurally rather than by a TTL floor. **C-1:** **stays open, NARROWED** — scope tightens from "Δ > the inter-sweep gap" to "Δ > (k−1)·TTL"; `:1982` re-pinned, not deleted; its own close_out remains the fix |

**Not owed by any leg, explicitly:** narrowing `ttl_seconds` or adding a TTL floor (`B-74`'s declined
option, rejected twice on that arc — once by Codex, once by advisor()); any fourth reordering of
`_publish_atomic`'s two-stamp pipeline (`B-77`'s record carries three prior wrong mechanism claims on
that exact surface).

---

## §10 Cite re-verification at HEAD `6d557c26`, and review record

**Code cites — all re-resolved by direct read at this HEAD.** `harness-runtime/src/harness_runtime/lifecycle/protected_result_store.py`:
`:72` `_OPPORTUNISTIC_GC_INTERVAL_SECONDS = 300.0` ✓ · `:96` `_CROSS_PROCESS_LOCK_FILENAME` ✓ ·
`:111` `_root_observed_expired: dict[str, frozenset[str]] = {}` ✓ · `:112` guard lock ✓ · `:115`
`_root_identity_key` ✓ · `:323` `self._last_gc_at = 0.0` ✓ · `:479` `_publish_atomic` ✓ · `:557`
`os.utime(tmp_name, None)` ✓ · `:570` `os.link(tmp_name, entry_path)` ✓ · `:571` `_fsync_dir` ✓ ·
`:581` `os.utime(entry_path, None)` ✓ · `:592` `read` ✓ · `:643` `ack_delete` ✓ · `:650` `gc_sweep` ✓ ·
`:753`/`:774`/`:784`/`:791` the four `st_mtime` reads ✓ · `:860` `self._last_gc_at = current_time` ✓ ·
`:863` `_observe_expired` ✓ · `:879` the replace-not-accumulate write ✓ · `:882`
`_maybe_opportunistic_gc_sweep` ✓ · `:953` `resolve_result_ref` ✓.
Elsewhere: `bootstrap/stage_4_od.py:89`/`:123` ✓ · `bootstrap/factories/protected_result_store_factory.py:78` ✓ ·
`shutdown.py:800` ✓ · `cli/app.py:342`/`:615` ✓ · `lifecycle/audit_offload.py:353` ✓ ·
`harness-runtime/src/harness_runtime/types.py:1827` TTL field ✓.
Tests (`harness-runtime/tests/test_lifecycle_protected_result_store.py`): `:37` `_sweep_past_grace` ✓ ·
`:487` the sole `ack_delete` caller ✓ · `:1795`/`:1862`/`:1899`/`:1924`/`:1985`/`:2033` the six grace
witnesses ✓ · `:1858`/`:1920`/`:1982`/`:2026` the four reclaim asserts ✓ · `:1978` the REGISTERED
RESIDUAL comment ✓.

**Spec cite — ONE anchor moved, recorded not normalized.** `Spec_Harness_Runtime_v1.md` head is
**v1.109** at this HEAD (`:1`), not the row's v1.108; `### §14.8.11` heading at `:4898`; the
bounded-retention bullet at `:4909`, not the row's `~:4883`. **The bullet text is byte-identical to
the fragment the row quotes** — *"a signing outage must not grow an unbounded store of sensitive
payloads"* — so the row's "unchanged across v1.106→v1.108" carry extends to **v1.109**, verified by
direct read rather than assumed. Per that spec's own anchor convention, prior-version change-note
anchors are historical and are not refreshed here; this filing's anchors are current.

**A pointer-drift candidate, PROBED AND FALSIFIED — recorded so it is not re-raised.** `[HIGH]` This
filing initially recorded a governance-pointer lag (root `CLAUDE.md` §2.3 naming an older Runtime
spec head than the file carries). **Direct read at this HEAD falsifies it:** `CLAUDE.md` §2.3 records
**v1.109**, which matches `Spec_Harness_Runtime_v1.md:1` exactly. There is **no pointer drift**. The
only stale label is the one inside the `B-96` **row** (v1.108 / `:4883`), which this filing records
above and which the ratification leg refreshes with the row's other edits. The candidate is kept here
rather than deleted because the falsification is itself the useful record — per
`[[wrong-version-read-delta-only-baseline]]`, an axis/governance pointer is a *likely* drift site,
which is precisely why it was probed rather than asserted.

**Counts, recounted programmatically at this filing.** Sweep triggers **3** · `_root_observed_expired`
production call sites **2** (`:878`, `:879`, both inside `_observe_expired`) · `st_mtime` reads of
this store in production **4**, all inside `gc_sweep` · production callers of `read()`/`ack_delete()`
**0 / 0** · non-test `ProtectedResultStore(` construction sites **1** · `_sweep_past_grace` call sites
**11** · total `gc_sweep(` calls in the witness file **47** across **62** tests · readings **4**,
viable **2** · open decisions **3**, collapsing to **1**.

### §10.1 Out-of-family review — `just codex-review-uncommitted`

**Round 1 — two [P1], both substantive, both dispositioned in the body rather than summarized away.**

- **[P1] "Bound retention after observation-record loss" — UPHELD IN FULL, and it changed the
  reading.** The draft's "≈2×TTL" was true only absent record loss; one loss permits ≈3×TTL and
  repeated losses are unbounded — the same failure shape §3(i) uses to disqualify Reading B, which
  would have made C self-inconsistent. Absorbed at §4 Reading C as **two required mechanisms**
  (crash-atomic persistence removing `corrupt` from the reachable state set; an **absolute reclaim
  ceiling** at `k × ttl_seconds` that does not consult the record and therefore bounds retention
  under total record loss), propagated to §6, §8, §9, and to §7 — where the council disposition is
  now explicitly **contingent** on the ceiling. **This is the round's real yield: without it, C's
  retention pricing was wrong and the probe-resolution unsound.**
- **[P1] "Account for wall-clock steps" — PREMISE UPHELD, CONCLUSION NOT.** The premise (a forward
  step fires a stored-timestamp comparison early in true-elapsed terms) is correct and is now
  recorded at §5.2. The conclusion (that this "invalidates the publication-bound lemma") does not
  hold: both terms are `now` minus a stored wall-clock value and are perturbed by exactly the same
  `X`; the same step already fires against the shipped mtime term, so C adds no new clock channel;
  and `t_first_obs ≥ t_pub` **as clock readings** is what the lemma asserts, which a step can only
  push later. §5.2 states the four-point disposition rather than conceding or dismissing it, and
  adds the structural fact that **no reading is both cross-process and clock-step-immune** — the
  clock-immune alternative *is* Reading B, which §3(i) disqualifies.

**Round 2 — one [P1] + one [P2], both UPHELD on direct read, both absorbed.**

- **[P1] "Keep the absolute ceiling from bypassing the grace" — UPHELD.** Round 1's ceiling is keyed
  on `mtime`, so it fires before true expiry whenever `Δ > (k−1)·TTL` — which `B-74`'s own witness
  scenario (`ttl_seconds=0.1`, Δ≈1.0s, k=2) satisfies. The draft's "liveness fully closed" and
  "retires three rows" claims were therefore over-stated. Absorbed as a **named, irreducible
  tension** (no single ceiling both bounds under record loss *and* cannot predate publication) with
  the mtime-keyed form recommended on the ground that its residual is **exactly `B-74`'s existing
  residual, strictly narrowed** — propagated to §3(ii)'s qualification, §4's liveness bullet, §6
  points 2 and 3, and §9's `B-74` row, which now reads **NARROWED, stays open** rather than
  *closes*. **The recommendation does not flip; its supporting claim is corrected.**
- **[P2] "Use replacement-safe publication for the sidecar" — UPHELD.** The record is mutable, and
  the `O_EXCL`/`os.link` precedent cited in round 1 is deliberately **no-replace**
  (`lifecycle/effect_fence.py:317`–`:319`, read directly) — it would freeze the record at its first
  snapshot, while unlink-then-relink would open an absent window that restarts the grace. The
  precedent cite is **retracted** and replaced with temp-write + `fsync` + **`os.replace`** +
  directory `fsync`.

**Round 3 — five [P1], all UPHELD, all absorbed. This round TRIPPED the register-and-hold cap and
the filing's response was to HOLD, not to decide again.** `[HIGH]`

- **[P1] "Keep the crash-window row open under the ceiling."** The mtime-keyed ceiling fires early
  for the `B-77` crash-window Δ too, whenever `ttl_seconds` is small enough — a supported
  configuration (`types.py:1827`, `gt=0.0`). So C-1 narrows **all three** rows uniformly and closes
  none. Absorbed at §4 (C-1's liveness bullet), §6 point 3 (per-form disposition), §9 (new
  `B-96`/`B-77`-residual row).
- **[P1] "Use atomic replacement for the mutable sidecar."** §9's impl row still carried the
  round-2-retracted `O_EXCL`/`os.link` primitive, contradicting §4. Fixed in §9 and §8.
- **[P1] "Do not close `B-96` before implementation lands."** Under C, ratification leaves a spec
  leg and an impl leg outstanding; `closed` would drop live work from the open-work inventory.
  §9's ratification row now reads **`design_substrate_gated` at ratification, `closed` only when
  the impl leg merges**.
- **[P1] "Remove `B-74` closure from the ratification choice."** §8 asserted a joint close the rest
  of the document no longer supported. §8 rewritten; closure is now stated **per form and at the
  impl leg**, never at ratification.
- **[P1] "Convene the unresolved C3–C7/C8 tension." — REVERSES this filing's §7 position, and the
  reversal is the round's most important yield.** Rounds 1–2 concluded probe-resolved on the
  strength of an unconditional retention bound; round 3 showed that bound is *bought* with C3's
  publication-bound safety, so the tension relocates rather than dissolves. §7 now reads
  **CONVENE — dyadic C3 + C7, scoped to C-1 vs C-2**, with the probe's genuine partial yield (the
  spec's word is *unbounded*, not *exactly TTL*) carried in as a pre-bound fact.

**Round 4 — three [P1] + one [P2], all UPHELD, all absorbed. All four are mispricings of the C-1 /
C-2 characterisations introduced at round 3, not re-flips of the choice itself.** `[HIGH]`

- **[P1] "Do not classify C-1 as a uniform narrowing." — the round's most consequential finding.**
  At `B-74`'s own witness values (`ttl_seconds=0.1`, Δ≈1.0s, k=2) the unconditional ceiling is
  already true at the **bootstrap** sweep, so C-1 reclaims on **first observation** — the one thing
  HEAD's sweep-count grace always prevents. C-1 is therefore a **regression against HEAD** above
  `Δ > (k−1)·TTL`, not a uniform narrowing. Absorbed at §4 (C-1 liveness), §6 point 3, §7 (the
  convening inherits the asymmetry), §8 (sub-ask reworded). **It strengthens the C-2
  recommendation rather than changing it.**
- **[P1] "Include backward clock steps in the publication lemma."** Round 2's *"a step can only
  make `t_first_obs` larger"* is true of forward steps and false of backward ones; a backward step
  between publication and first observation can make reclaim fall short of one true TTL. Absorbed
  at §5.2 point 3 and as §3(ii) qualification (b) — the lemma is now stated **with** its
  no-backward-step assumption, and the assumption is shown to bind the shipped `now − mtime` term
  identically.
- **[P1] "Condition the C-2 retention bound on sweep cadence."** `gc_sweep` is trigger-driven, not
  periodic, so C-2's ≈2×TTL needs a sweep after `first_observed_at + TTL` — the next run in the
  one-shot shape. The cadence premise had been stated in the pre-split draft and dropped in the
  C-1/C-2 rewrite; restored at §4 as an explicit **two-premise** bound, with the honest note that
  the premise is HEAD's too.
- **[P2] "Keep the lemma qualification consistent with C-2."** §3(ii)'s round-2 qualification still
  spoke of "Reading C" as necessarily carrying the ceiling. Rewritten to distinguish the forms:
  under C-2 the lemma **is** the reclaim rule; under C-1 a second, non-publication-bounded term can
  override it.

**Round 5 — one [P1] + three [P2], all UPHELD, all absorbed. All four sharpen statements rather
than move the decision; none re-flips C-1/C-2.** `[HIGH]`

- **[P1] "Timestamp the actual observation after publication."** Verified by direct read: `gc_sweep`
  samples `current_time` at `:714`, before its unlocked enumeration and before the lock; the
  observation happens at `:797`, after locked re-verification. Recording the former as
  `first_observed_at` would let a concurrent cross-process publish leave a record that **predates**
  publication, breaking `t_first_obs ≥ t_pub` at its root. Absorbed as **§3(ii) qualification (c)**
  and as a named acceptance condition in §9's impl row — sampling point is a **contract term of the
  lemma**, not impl discretion.
- **[P2] "Include sweep cadence in the C-1 retention bound."** Cadence is trigger-driven for **both**
  forms; C-1's bound is `k×TTL + next-sweep delay`, not unconditional. §4's C-1 retention bullet
  corrected, and §7's "premise-free bound" framing narrowed to its accurate form — the **only**
  additional premise C-2 carries is sidecar survival.
- **[P2] "Make the durable carrier selection authoritative."** §8 prices `(C-i)` while §4 called
  carriers impl discretion, which would let an impl leg build `(C-ii)`/`(C-iii)` on an answer that
  never priced them. §4 recast: `(C-i)` is the carrier under any C answer; the other two are
  **recorded rejections**.
- **[P2] "Condition first-sweep reclaim on observation delay."** `Δ > (k−1)·TTL` makes the ceiling
  *eligible* before true expiry; firing on the first sweep additionally needs `s + Δ > k·TTL` for
  observation delay `s`. Round 4's regression claim is therefore a **"can", not a "must"** — the
  wording is corrected at §4, §6 and §8 so the C-1/C-2 choice is not biased by an overstatement.

**Round 6 — one [P1] + one [P2], both UPHELD, both absorbed. EXIT declared after this round.**
`[HIGH]`

- **[P1] "Treat sidecar loss as independent from entry loss."** `os.replace` + `fsync` makes the
  sidecar's *update* crash-atomic; it does **not** fate-share the file with its sibling entries. A
  selective backup/restore or dotfile-skipping cleanup preserves every payload and drops every
  timestamp, resetting C-2's grace — repeatably. The round-3 claim that C-2 "adds no independent
  failure mode" is **withdrawn** at §4 and the §8 ask; C-2's bound now reads as resting on an
  operationally independent premise, which **strengthens the C7/C8 side of the held sub-decision**.
  The recommendation stands on the §6 point-4 harm asymmetry, explicitly subject to the convening.
- **[P2] "Correct the retention bounds in the ratification ask."** Both bounds omitted trigger
  delay in the operator-facing block: C-1 is `k×TTL + I`, and C-2 is up to `2×TTL + 2I` (one
  interval to the first post-TTL observation, one more to the post-grace reclaim), for a
  sweep-period bound `I`. §8 corrected to match the body.

**Cap disposition.** The absolute-ceiling element moved three times (round 1 introduced it, round 2
qualified it, round 3 falsified its closure claim). Per `[[reviewer-oscillation-register-and-hold]]`
a third movement is the stop signal, so the filing **stops deciding it**: both forms are stated as
**C-1 / C-2** at §4, the recommendation names C-2 with its ground, and the adjudication is routed to
the §7 convening and the §8 sub-ask. **This is the cap working as intended — not an unresolved
defect.** Driven under the PD-9 non-convergence discriminators throughout: rounds 1 and 2 were
convergent refinements, round 3 was the divergence signal, and the response was to hold rather than
to open round 4 on the same element.

### **SOUNDNESS EXIT — declared after round 6.** This filing is CLOSED to further mechanism rounds.

Per `[[deferred-mechanism-spec-leg-exit-on-soundness]]`: this is a **deferred-mechanism** filing — it
selects a bound, not an implementation. It exits on **soundness of the decision surface**, not on
reviewer quiet. The decision surface is: four readings enumerated, two shown dominated with the
reason stated, three decisions shown to collapse to one primary question, and one sub-decision
explicitly HELD under the oscillation cap and routed to a convening. A finding
that a *carrier sub-option* (C-i/C-ii/C-iii) has a defect is an **impl-leg** finding and does not
reopen this filing. **A finding that re-argues C-1 vs C-2 does not reopen it either** — that element
is under the register-and-hold cap (§10.1) and is routed to the §7 convening by design; re-deciding
it in a review round is the oscillation the cap exists to stop. A finding that a **reading is missing**, that the **publication-bound lemma
(§3(ii)) is false**, or that **§3(i)'s process-shape analysis is wrong**, does reopen it — those are
contract findings against the decision surface itself.

**Why round 6 is the exit.** `[HIGH]` Rounds 1–3 moved the decision surface (a reading was
disqualified, a mechanism was added, the council position reversed). Rounds 4–6 moved only the
**pricing statements** of two options that were already correctly enumerated — each finding upheld,
each absorbed, none introducing a reading, none reopening A-vs-C, and each successive round's
findings strictly narrower than the last's. That is the convergence shape a deferred-mechanism
filing exits on: the operator now has four readings, an accurate price on each, an explicit held
sub-decision with both sides' strongest arguments recorded (including the two that argue *against*
the recommendation), and a scoped convening to adjudicate it. Further pricing refinements are
**inputs to the §7 convening and the impl leg**, and are to be raised there rather than by reopening
this filing.

---

## §11 RATIFICATION

**Status: RATIFIED 2026-08-05 as READING C, with the held ceiling sub-decision resolved as C-2 — the
GRACE TERM ALONE, no absolute mtime-keyed reclaim ceiling. The spec leg and the impl leg are both
still OWED; this filing's chain is at leg 3 of 4.**

The `B-92` / `B-97`(a) / `B-107` precedent is followed: the outcome is recorded here
verbatim-in-substance rather than only at the register row, so the decision travels with the filing a
later session actually reads.

### §11.1 The gate — the primary decision (operator `AskUserQuestion`, 2026-08-05)

> **Operator selected: READING C — replace the sweep-COUNT bound with a DURABLE, publication-bounded
> elapsed-time first-observation grace, on a dedicated digest+timestamp sidecar published by
> `os.replace`, accepting the reversal of `B-77`'s ratified "no persisted sidecar" judgment.**
>
> **Reading A was NOT selected and is NOT partially adopted.** A deferral that quietly kept the
> sweep-count bound while adopting C's vocabulary would be the silent-absorption failure mode this
> filing exists to avoid.

### §11.2 The held sub-decision — resolved as C-2, by convening, not by assertion

§8 routed the C-1/C-2 ceiling question to the §7 dyadic rather than deciding it, under
`[[reviewer-oscillation-register-and-hold]]`, because the element had moved three times under
out-of-family review. **That convening ran on 2026-08-01** and its record is
`.harness/council-b96-grace-ceiling-2026-08-01.md` (merged at PR #1183).

> **VERDICT: C-2 — the grace term alone. UNANIMOUS across three voices, reached from
> NON-OVERLAPPING grounds** (record §7): C3 on age-authority integrity, the implicit-floor identity
> and the witness-inversion discriminator; C10 on under-gating / fail-open in a fail-closed section,
> false audit emission, and the non-existence of the bound C-1 sells; C7 concurring, and adding that
> the report log is this store's **sole** forensic artifact.

**No third form was manufactured.** A third ceiling was actively hunted: C10 constructed and killed
the **record-keyed** and **hybrid absent-record** variants, and the adversarial pass constructed a
**fourth, `ctime`-keyed** variant C10 had missed — the strongest C-1 form found on this arc — which
dies for the same reason (record §4.2b). They are recorded as **tested-and-dead rather than
suppressed**, so a later session does not re-propose one as novel.

**Each voice conceded against interest** (record §7): C3 withdrew *"the record may be discarded
freely"* and accepted the §3.4 incompleteness; C10 declined three arguments its own brief invited and
could not break C3's impossibility claim when it tried on its own side's behalf; C7 stated two limits
against its own recommended option.

### §11.3 The ratified form, stated so the spec and impl legs cannot drift from it

| Element | Ratified value |
|---|---|
| Bound | **Elapsed-time first-observation grace, C-2 form** — the grace term alone. **No** absolute `k × ttl_seconds` reclaim ceiling. |
| `first_observed_at` | **Wall-clock**, sampled at the observation point **under the lock** (§3(ii) qualification (c) — a named acceptance condition, not implementation discretion). |
| Carrier | **(C-i)** — a dedicated digest+timestamp sidecar. Carriers **(C-ii)** and **(C-iii)** are **not** owed by any leg. |
| Publication | temp-write + `fsync` + `os.replace` + **directory `fsync`**. Explicitly **NOT** the write-once `O_EXCL` / `os.link` primitive, which is no-replace and would freeze the record at its first snapshot. |
| Record absence | Reads as **no observation**. |
| Retention | Up to **2×TTL + 2I** (one interval to the first post-TTL observation, one more to the post-grace reclaim). |
| Reading B | **RETIRED EXPLICITLY.** No impl leg may build per-process elapsed time as written. Owed under every answer per §8, and discharged here. |

### §11.4 What the ratification carries, per §8's "carried by any answer" list

| §8 obligation | Disposition at this leg |
|---|---|
| `close_out` **amended** to retire Reading B explicitly | **APPLIED** on both register surfaces. |
| Under C: wall-clock `first_observed_at`, carrier **(C-i)**, `os.replace` publication, record-absence-as-no-observation | **APPLIED** — recorded on the row and tabled at §11.3. |
| The *"no persisted sidecar"* **reversal** recorded on `B-77`'s row so it is not later read as unratified drift (council record §9) | **APPLIED** — `B-77`'s `close_out` and prose now carry the reversal, dated and attributed to this ratification. |
| The `B-74` row cross-referenced to the council record and to the `B-96` impl leg | **APPLIED** — and its stale §14.8.11 anchor refreshed (§11.6). |
| The `council` field flipped from *"convene if the elapsed-time variant is taken"* | **APPLIED** — it now records the convening as **run and resolved**, with the verdict and its three grounds; no further convening is owed at the spec or impl leg. |

### §11.5 Status — `design_substrate_gated`, deliberately NOT `closed`

Per §9 (out-of-family round 3 [P1]) the row moves to **`design_substrate_gated`**, not `closed`:
under C both the spec leg and the impl leg are outstanding, and `closed` would drop live work out of
the open-work inventory.

- **Spec leg (owed):** a Runtime **§14.8.11** amendment carrying the council record's **twelve
  conditions** at its §7.1, with §7.2's **expansion flag** surfaced in the clearance marker per root
  `CLAUDE.md` §4.5. Landing the grace silently would be **X-AL-3** — §14.8.11's deferred-to-impl list
  does not name a retention-extending grace.
- **Spec and impl do NOT land together** (the `B-33`/`B-39`/`B-59`/`B-69`/`B-70`/`B-72`/`B-97`/`B-107`
  precedent).
- **CXA: no delta owed** — *determined, not assumed*: the council record's adversarial pass ran the
  cross-spec probe and found CP v1.103 §1 row 6, CP v1.103 §14/§18, CP v1.112 §55 and Runtime plans
  v2.51/v2.56 all cross-reference §14.8.11 as the **Runtime-owned definition site**, never restating
  it, so no sibling text is stranded.
- **`B-96`, the `B-77` residual and `B-74` all flip to `closed` ONLY when the impl leg merges.**

### §11.6 One correction this leg makes rather than carries

The council record's §9 prescribed refreshing the bounded-retention anchor to **`:4909` at v1.109**.
**That prescription was itself already stale at the ratification HEAD** and is not applied as
written. Re-resolved by direct read at HEAD `4815ebef`: the Runtime spec head is **v1.110**, the
§14.8.11 heading is at **`:4915`**, and the bounded-retention bullet is at **`:4926`** — `v1.110`'s
`B-104` Component 1 insertions having shifted the file. **The bullet TEXT is unchanged across
v1.106 → v1.110**, verified by direct read. Both owed refreshes are applied to their correct homes:
the stale `:4883`-at-v1.108 anchor lives in the **`B-74`** row, and the `B-96` row carried only a
bare version label.

### §11.7 What this leg does NOT do — stated so each absence is a decision

**No `design-substrate/**` edit rides this ratification.** The Runtime §14.8.11 amendment is the
**spec leg's** work and is owed separately, with its own clearance marker. **No `harness-*/src` or
`harness-*/tests` edit rides it either** — the sidecar, the `_observe_expired` signature change, the
`gc_sweep(now=…)` seam extension and the witness pass over the eleven `_sweep_past_grace` call sites
and the four reclaim asserts all belong to the **impl leg**. **Explicitly not owed by any leg:**
narrowing `ttl_seconds` or adding a TTL floor (`B-74`'s twice-declined option), and any fourth
reordering of `_publish_atomic`'s two-stamp pipeline.
