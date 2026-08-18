# ADR-HE-1 — Parallel-lane coordination architecture for the autonomous loop

**Filed** 2026-08-17 · **Amended v1.1 same day** · **Repo at** `17011f89c` · **Axes** control plane ·
information substrate · operational discipline · **Class** Foundational (F) for the H_E loop substrate

**Scope.** This record governs the **coordination/concurrency spine only** — how lanes build in
parallel and land serially. The full loop design spans four foundational decisions; the other three
are [ADR-HE-2](ADR-HE-2_review_gate_and_completion_semantics.md) (verdict validity),
[ADR-HE-3](ADR-HE-3_record_and_measurement_substrate.md) (record + measurement), and
[ADR-HE-4](ADR-HE-4_defect_mechanization_and_grounding.md) (mechanization + grounding).
See [README](README.md) for the set.

> **Change-note v1.1 — authored against an incomplete corpus, corrected.** v1.0 was written from
> `HARNESS-LOOP-AND-LANES-DESIGN-v2.md` alone. v2 is the head of a **three-link chain** and is
> deliberately narrowed to the lanes tension its council deliberated; it neither repeats nor
> supersedes the ratified operator decisions carried at **v1 §3.1**. Consequences of the miss, all
> corrected below: **O2's recommendation was withdrawn** (it contradicted ratified decision **D-C**),
> **O1 was superseded** (by **D-A**), and **§5's disposition of the L0.2′ record was inverted**
> (it is ratified-but-unbuilt, not a candidate for striking). §3.1's foundational decision and its
> eleven derivatives are unaffected — the corpus corroborates them.

---

## 0. Corpus and authority chain

The design corpus is three links plus an evidence record. **Earlier links govern where later ones
are silent** — the same rule v1 states of its own predecessors.

| Link | Artifact | Authority |
|---|---|---|
| 1 | `loop-eng-2026-08-16/BUILD-PLAN-operator-ratified-2026-08-17.md` | **Operator-ratified.** Carries decisions D-A…D-D and the Arc 1–7 build order. Highest authority in the chain |
| 2 | `HARNESS-LOOP-AND-LANES-DESIGN-v1.md` | **Consolidated full-loop design** — *"authoritative consolidated source… This file is what to act from."* Merges the loop arc and the lanes arc; carries the ratified decisions forward at §3.1, the lanes decisions L-1…L-5 at §3.2, the not-being-built list at §10, and the evidence standards at §11 |
| 3 | `HARNESS-LOOP-AND-LANES-DESIGN-v2.md` | **Head, but narrow.** Supersedes v1 on the six points its council revised (flock killed, AC#2 rebuilt on subprocess, reservation grown to three states, `concurrent_lanes` as cohort key, coalescing enacted, X9 found). **Silent on the loop half**, so v1 and the BUILD-PLAN govern there |
| — | `loop-eng-2026-08-16/` R1–R9 + STAGE3–7; `parallel-lanes-2026-08-17/` PR1–PR6 + STAGE0b–7 + `ERROR-LEDGER.md` | Evidence record. Inputs, not decisions |

**Known gap in this sweep, recorded so it is not mistaken for coverage.** These four records were
authored from links 1–3 plus `loop-eng`'s STAGE7 and SYNTHESIS, and R1 §7's contradiction checklist.
**Not swept:** `parallel-lanes-2026-08-17/STAGE5` and `STAGE7`, and `ERROR-LEDGER.md`'s 49 lanes
corrections. Because v1 states its own predecessors *"govern where it is silent,"* reading v1
establishes what it **consolidated** but cannot reveal what it **dropped** — any lanes-arc decision
v1 omitted would still govern and would not appear in these records. A sweep of those three files
against §3.1's derivatives is the cheapest remaining completeness check.

**Three build sequencings coexist across the corpus and are not interchangeable**: the BUILD-PLAN's
**Arc 1–7** (ratified), STAGE7's **Layer 0–4** (which the BUILD-PLAN supersedes *where they differ*),
and v1/v2's **Phase 0/1/2** (lanes-arc framing). A fourth — the "Phase 0a/0b" split proposed by this
session's architectural review — was authored without sight of the first two and **is withdrawn as a
numbering proposal**; its substantive claim (that measurement-instrument items are being counted as
lane-safety gates) is re-expressed against the ratified Arc order in ADR-HE-3 §5.

**Ratified operator decisions (2026-08-17), binding on all four records:**

| # | Decision | Governs |
|---|---|---|
| **D-A** | Build through **Layer 2** — safety + measurement + speed. Full scope authorized | HE-1 §6 O1; HE-4 |
| **D-B** | **Extend existing records; do NOT build a new ledger** | HE-3 |
| **D-C** | Wire the second cross-vendor reviewer as **automatic failover** | HE-2; HE-1 §6 O2 |
| **D-D** | Wire the shadow trial into the loop; **measure value live in runtime** | HE-3 |

**Axes** control plane · information substrate · operational discipline · **Class** Foundational (F)
for the H_E loop substrate

---

## Namespace note — why `HE`, not `D9`

This ADR governs **H_E dev tooling**: `tools/arc_metrics.py`, `tools/hooks/`, and the
`.claude/skills/` loop recipes — the scaffolding that *builds* H_T, not H_T itself. The
`design-substrate/` ADR series (`ADR-F1..F5` foundational, `ADR-D1..D8` derivative) is the **H_T**
canon and is consumed by Phase 7 as authoritative product architecture.

Filing this as `ADR-D9` would misfile tooling as product architecture and collapse the substrate
boundary that `CLAUDE.md` invariant **X-AL-1** places at the MCP server process, enforced by process
isolation rather than convention. **CP-AL-1** independently forecloses the adjacent error — reading
H_E orchestration topology as H_T's `TopologyPattern` enum. The `HE` prefix makes the collision
structurally unrepresentable and leaves the `D` series free for genuine H_T derivative decisions.

This ADR therefore does **not** extend the H_T design and does not implicate invariant I-2 / X-AL-3.
Its posture is **mode-agnostic** workspace-operational work per `CLAUDE.md` §11.2.

---

## 1. Status

**ACCEPTED** for the foundational decision and its committed derivatives (§3.1).
**PROPOSED** for the extensions at §3.2 (surfaced by architectural review 2026-08-17, not yet routed
to any council voice).
**OPEN** — four operator-owned questions at §6, none of which gate the foundational decision.

The foundational decision is Accepted rather than Proposed because it **records and extends an
existing workspace commitment**, it does not mint one. `two-lane/SKILL.md:8` already binds the
workspace to build-parallel/land-serial at N=2 — verified at HEAD this session:

> *"Two arcs can be \*built\* concurrently. They cannot be \*landed\* concurrently: CLAUDE.md §12.2.1
> gives the merge lane a single fixed point, and every landing has to pass through it in order."*

The operator has separately mandated N=4. This ADR carries that committed shape from N=2 to N≥2
generally and names the coordination primitives that make it safe.

---

## 2. Context

The autonomous loop currently runs one lane. A ratified operator mandate raises it to four. Two
independent bodies of work — the loop-engineering arc and the parallel-lanes arc — converged on a
single design (`HARNESS-LOOP-AND-LANES-DESIGN-v2.md`), which then passed an eight-voice council
reconciled to zero across three waves plus two cross-voice rounds, a cold out-of-family Codex review,
and a two-round E4 gate (round 1 LOOP-BACK, round 2 CLEAR-WITH-FOLD).

**What forced the decision.** Concurrency hazards in the shared drain/queue substrate are live
**today at N=1 and N=2**, not hypothetical consequences of going to four:

- `main` is unprotected server-side — `protected: false`, rulesets `[]` **[V]** — while
  `permission-guard.sh:427` auto-allows bare `git push` in loop mode inside an alternation carrying
  **no destination-branch predicate**, and `_bash_args_safe` (`:122-144`) gates only on secrets,
  `~`/`..`, `.git/`, uppercase env expansion, and absolute-path containment **[V]**. One
  auto-approved call can place unreviewed content on `main` with no PR, no CI, no merge gate.
- Three check-then-act `os.replace` sites (`arc_metrics.py:666`, `:746`, `:754` **[V]**) are
  unguarded; the losing racer raises an uncaught `FileNotFoundError` that propagates out of
  `drain()`'s loop and abandons every other still-pending entry.
- No reservation exists to prevent duplicate ledger appends across PR-merge latency;
  `lane_id` has **zero occurrences repo-wide [V]**, so no lane-attribution is possible at all.

**Constraints that bound the solution space.** `arc_metrics.py` is deliberately lock-free —
`flock` has **zero occurrences [V]**, and the file states *"no lock is needed to say so"*. `L-2`
forecloses a daemon or coordinator process. `L-5` and `D-B` (extend-don't-build) argue against new
durable stores. `CLAUDE.md` §12.2.1 fixes the merge lane at depth 1 by construction.

---

## 3. Decision

### 3.1 Foundational decision — ACCEPTED

> **Lanes build concurrently in isolated worktrees and land through a single-writer merge door. All
> coordination uses lock-free filesystem CAS — atomic exclusive create plus atomic rename — with no
> daemon, no coordinator process, and no exclusive gate held across an unbounded network call.**

This is parallelization-by-sectioning into a single-writer gather: a standard fan-out/fan-in, not a
compromise. Throughput is explicitly **not** N× — merges serialize by construction.

**Committed derivatives** (council-converged; each carries its ruling ID):

| # | Commitment | Source |
|---|---|---|
| D1 | Reservation is three-state `pending → open → terminal{merged\|abandoned}`; `superseded_by` mandatory on abandon; chain resolution is a bounded walk-to-terminal, **cap 5, exceeding the cap RAISES** | R-7 |
| D2 | `pid`/`host` are **structurally unreachable** for the reservation but **load-bearing** for the merge lease — "correctly different, not must-inherit." The reservation spans an hours-long handoff decoupling liveness from validity; the lease is one continuous seconds-long operation where "pid alive" and "task in progress" are the same fact | R-27(a) |
| D3 | Lease contention is **fail-fast, one attempt, caller decides retry** — L-2-compliant by construction rather than by discipline, since a backoff default would build daemon-shaped arbitration without ever naming it a daemon | R-9 |
| D4 | Merge-door lease payload is `{lane_id, pr, acquired_at, pid, host, merge_attempted_at}`. `pr` is **required for reclaim to function at all** — reclaim runs in a different process against a single global lease, so the PR number cannot come from memory | R-22 + F-R2-03 |
| D5 | `MERGE_ATTEMPTED` (`merge_attempted_at`) is durably written **before** `gh pr merge` fires, via the same atomic rename used by every other transition. Without it, a crash after a successful-but-unconfirmed merge is indistinguishable on restart from "never tried" | R-28 |
| D6 | Reclaim is **two-step**: pid-dead establishes reclaimable-in-principle; `gh pr view <N> --json state,mergedAt` is mandatory ground truth. MERGED → release as completed, **never retry**; OPEN → restart from the merge-tree compare | R-27(b) |
| D7 | `concurrent_lanes` is **`derived`** (count of `open` reservations at the `pending→open` flip), never `declared` | design v2 §5 |
| D8 | `open` + stuck → **warn via the HITL queue, never auto-reclaim**. `gh` transient failure fails safe to "still open," never reclaimable | design v2 §5 |
| D9 | The merge door is fenced by a lease acquired **before** the merge command is constructed; its second step is a read-only `local-base-cas-check` (recompute `git merge-tree`, byte-compare) which survives the blocking of the raw-ref mechanism because it never touches it | R-22, R-23 |
| D10 | `gc.auto 0` is set **repo-wide, once, idempotently** — not per-lane. Without `extensions.worktreeConfig` (UNSET at HEAD) there is no such thing as a per-lane `git config` write | R-17 |
| D11 | Per-lane Docker isolation uses `-p` plus the **full** collision set: ports {3000, 3200, 4317, 4318} **and** the fixed project name, which governs the container/network/**volume** namespace | R-18 |

### 3.2 Proposed extensions — NOT YET COUNCIL-ROUTED

Surfaced by architectural review (`HARNESS-LOOP-AND-LANES-DESIGN-v2-ARCHITECTURE-REVIEW.md`,
2026-08-17). Recorded here because each is structural, but **none has been routed to a voice**.

| # | Proposal | Review ref |
|---|---|---|
| P1 | Lease-before-merge ordering is enforced by an **allowlisted wrapper**, not by prose instruction. Add `tools/hooks/safe-merge.sh`; deny raw `gh pr merge` in the loop-mode deny block (`:314-340`, which precedes the `:427` allow **[V]**); allow only the wrapper alongside `:288-290`. This copies the existing in-repo idiom — raw `git worktree remove` is denied at `:57-65` and only the mutex-backed `safe-worktree-remove.sh` is allowed via `_safe_worktree_remove_wrapper` (`:184-191`) **[V]** | A1 |
| P2 | An explicit invariant links the two state machines: **the lease may be held only by an arc whose reservation is `open`; reclaim transfers merge-driving authority but never reservation ownership.** Add `reservation_id` to the lease payload for the same reason `pr` was restored | A2 |
| P3 | Keep `loop_status.md` a **single file**; fix only the ACTIVATE-reset scoping bug. The AWK reducer keys on `$3`/`$4` and never reads the `$2` timestamp, and `loop_log` writes one line via `>>` **[V]** — so concurrent writers are already correctly serialized by `O_APPEND`. A fragment split would forfeit that property and is what creates the ordering hazard a monotonic `seq` would then repair | A4 |
| P4 | Bounded **120s** timeout on the `gh pr merge` call specifically — not a global `run()` timeout, which would convert slow-but-healthy CI polls into `AbortError`s (`run()` at `:134-146` passes no `timeout=` **[V]**). On timeout, reconcile via `gh pr view`, never blind-retry: the timeout case and the crash case are the same failure shape and take the same fix (D6) | A6 |

**P1 is proposed to supersede R-19's disposition — not yet routed to C10.** R-19 correctly rejected *removing `gh pr merge` from the
allowlist* — bare removal breaks autonomous merging for zero defect closure — and relocated the
obligation into ship-pr's calling code. But its stated premise, that permission-guard *"is not a
workflow-ordering engine,"* is false at HEAD: the guard already performs deny-raw-verb /
allow-only-wrapper ordering for `git worktree remove`. P1 preserves autonomous merging **and** makes
the ordering structurally unrepresentable. This should be re-routed to C10.

---

## 4. Rationale

**Why lock-free CAS over an OS lock.** C9 proposed a full-lifetime `flock` and then **rejected its
own proposal** on verification: `extract()` (`:280`) makes two remote calls inside the window it had
proposed locking — `gh_pr()` at `:284` and `ci_metrics()` at `:376` **[V]**. Its own assessment:
*"an OS lock held across an unbounded external call is the topology-availability twin of a retry
policy with a per-attempt timeout but no total-budget timeout."* Beyond that, `flock` auto-releases
on process death, which is structurally insufficient across the process boundary D6's reclaim must
cross. Introducing it would also have been a mechanism-family change into a deliberately lock-free
file (R-6).

**Why the primitives are already in the file.** This decision adds no new mechanism family.
`publish_exclusive` (`:516`) is documented as creating a path *"atomically AND exclusively"* **[V]**;
`_claim_arc` states *"The claim and its ownership stamp have to be the same operation"* (`:602-610`)
**[V]**; the `except FileNotFoundError` guard with the comment *"A peer finished this arc between
listing and claiming it"* already exists at `:633-638` **[V]**. The fix for the three unguarded
`os.replace` sites is therefore **copying an in-file idiom**, which strengthens rather than
undermines the lock-free commitment.

**Why the merge door is correctness machinery, not speed machinery.** A local pre-check alone retains
a TOCTOU window: post-hoc first-parent assertions detect a bad landing only *after* `main` has
changed. This is the same detect-after-landing insufficiency that disqualifies `ROADMAP_STATUS_DRIFT`
as a merge-door control — it fires against already-landed history, rolls nothing back, and blocks no
merge. Hence R-10 relocated the lease from Phase 2 into the correctness floor.

**Why reliability sits on the deterministic side.** Every commitment above is a filesystem CAS, a
schema-shaped payload, a gate, or a ground-truth query. None rests on an agent behaving correctly.
P1 exists precisely because R-19's relocation left one property — merge-door ordering — resting on
prose executed by an LLM, which is the one placement this architecture otherwise avoids everywhere.

**Why client-side fencing is necessary but not sufficient.** The lease is purely client-side and
gives **zero** defense against any path that never consults it, including the unfenced `push` verb.
R-20 adds the sharper point: once the lease visibly disciplines the cooperative path, the raw-push
route becomes comparatively *easier* because it looks unguarded next to a visibly-managed door.
Branch protection is the only fence independent of a bug in the lease logic — and it remains
operator-owned (§6), not folded in silently.

---

## 5. Consequences

**Becomes possible.** Lanes run at any N≥2 once the safety floor lands. Nothing in the floor is
N=4-specific — items are either N≥2 (reservation, `os.replace` guards, Docker isolation, merge lease)
or live at N=1 today (completion-validity, the review wrapper, the unfenced-push fix). After the
floor, **N is a dial with no further gates**.

**Becomes harder.** Merges serialize, so throughput is well under N× and trailing lanes re-gate on
head change. Any future coordination need must be met by filesystem CAS or escalate to an ADR
superseding this one — a daemon is foreclosed. `gc.auto 0` repo-wide shifts maintenance cadence onto
an explicit schedule.

**Now constrained.** Two contested items are deliberately left outside this decision and flagged:

- **Build sequencing is contested.** The design presents Phase 0 as a single 13-item floor gating
  4 lanes; the review argues four of those items (record extension, gate-coalescing, detection
  emission, the `ARC_METRICS_{REPO,LEDGER}` overrides) are *instrument* correctness gating Phase-1
  measurement rather than lane safety, and that Phase 0 should re-table as 0a/0b. **Not decided
  here** — it changes the answer to the first §6 question. See review §A3.
- **The durable store set is seven** (queue entries, ledger, reservation, lease, `loop_status.md`,
  the L0.2′ record, `Finding` emission) and has never been audited as a set. R-28 invokes
  anti-proliferation once, locally, to fold `MERGE_ATTEMPTED` into the lease; no pass checks the
  result for one-source-of-truth. A store/authority audit is owed before D1 or D4 is built.
  **Corrected in v1.1:** v1.0 noted the L0.2′ record "is prose, not code" and floated striking it as
  a store. That inverts its status — the record is **operator-ratified and explicitly load-bearing**
  under D-A × D-B (*"This common shape is load-bearing: without it N6 is uncomputable"*), and it
  carries **eight** fields, not seven. It is ratified-but-unbuilt, which is the opposite disposition
  from strikeable. The genuine tension — council ruling R-25 retargets emission onto the proven
  3-field `Finding` (`:113-117` **[V]**) while the ratified shape has eight — is adjudicated in
  ADR-HE-3, not here.

**Known residual.** The design's §5 composite carries a `[P]` tag deliberately: its amendments
(R-7/R-8/R-9/R-13/R-14/R-27) were each tested individually, but the assembled composite has had no
holistic pass. P2 is the first finding returned by running one.

---

## 6. Open items — operator-owned, none gating §3.1

| # | Question | Recommendation | Tiebreaker |
|---|---|---|---|
| O1 | ~~Does the N=4 mandate pre-authorize Phase 2 *automation*…~~ **SUPERSEDED by D-A.** | **Partially closed, and split.** D-A authorizes *"build through Layer 2 (safety + measurement + speed work) — full scope."* Layer 2 (STAGE7) is P1 mechanization + decorrelated equivalence proof + the ~58s local/CI gap — **all authorized**, and now governed by ADR-HE-4. But v2's "Phase 2" is a **different set**: it adds *lease-widening* and the *shadow trial*, and D-A does not name lane orchestration. `two-lane/SKILL.md:140-142`'s organic-pain bar governs **follow-on lane orchestration specifically**, which D-A does not reach. **Residual: lease-widening only** — recommend it stays behind the pilot bar | Confirm D-A's "Layer 2" is read as STAGE7's Layer 2 (mechanization / dedup / local-CI gap), not v2's Phase 2 — the two sets differ by lease-widening and the shadow trial |
| O2 | ~~Is `gemini-review` a failover, or is the chain deliberately single-vendor?~~ **RECOMMENDATION WITHDRAWN — it contradicted ratified D-C.** | **Withdrawn.** v1.0 recommended "single-vendor, never a failover," reasoning that failover converts `REVIEWER_UNAVAILABLE` into a silent quality downgrade. **D-C had already ratified automatic failover on 2026-08-17**, and the BUILD-PLAN pre-answers the objection: *"on primary failure, invoke the second cross-vendor reviewer under the **identical** validity check — no relaxed bar. Then block if it also fails."* Identical-bar-plus-block-if-both-fail is not a downgrade. **The residual question is narrower and real** — R1 invariant **#3** scopes out-of-family review to *Codex-authored* work, so which channel serves **Claude-authored** diffs is genuinely open. Now owned by ADR-HE-2 | Confirm whether `just gemini-review` (`justfile:607`, `_require-antigravity` **[V]**) is authorship-gated in implementation or only in the R1 checklist |
| O3 | Escalation TTL (24h proposed, never separately ratified) | **Adopt 24h**, noting it is a *notification* threshold, not a reclaim threshold — D8 already forbids auto-reclaim, so the value cannot cause data loss either way | Confirm no path reclaims on TTL expiry; if one does, the value becomes safety-critical |
| O4 | Branch-protection posture on `main` | **Adopt.** Protection blocks nothing legitimate — every real path already goes through `gh pr merge`, and `ship-pr/SKILL.md:190-191` **[V]** hard-aborts unless `state=MERGED`. R-20 is decisive: it is the only fence independent of a lease-logic bug | Run one `gh pr merge --squash` against a scratch PR with protection requiring an up-to-date base; confirm the loop's merge path still succeeds |

---

## 7. Alternatives considered

| Alternative | Why rejected |
|---|---|
| **Full-lifetime `flock` across the drain lifecycle** | Self-rejected by its proposing voice on verification — two remote calls (`gh_pr` `:284`, `ci_metrics` `:376` **[V]**) sit inside the proposed lock window; `flock` also auto-releases on death, structurally insufficient across the process boundary D6 must cross. Would have been a mechanism-family change into a deliberately lock-free file (R-6) |
| **Daemon-backed merge queue / coordinator process** | Foreclosed by L-2. D3's fail-fast rule exists specifically so an implementer defaulting to retry-with-backoff does not build daemon-shaped arbitration without naming it a daemon (R-8, R-9) |
| **Local base CAS via raw `PATCH /git/refs`** | Blocked for two independent reasons: a locally-built squash commit does not contain the PR head as ancestor, so GitHub's auto-close never fires and `ship-pr` hard-aborts on non-`MERGED`; and the trust-boundary ruling — a raw ref PATCH is content-blind, proving only that the ref had not moved, never that the content passed CI. **Stays blocked even if the ancestry bug is fixed.** The read-only `local-base-cas-check` survives as D9's second step (R-23) |
| **Removing `gh pr merge` from the permission allowlist** | Rejected as posed (R-19): bare removal breaks the autonomous-merge arc that loop mode exists to enable, for zero defect closure. **Superseded by P1**, which achieves the ordering guarantee via an allowlisted wrapper while preserving autonomous merging |
| **`loop_status.d/<lane-id>-<seq>.md` fragment split** | Buys write isolation the design already has: `O_APPEND` single-line writes are correctly serialized, and the reducer never reads the timestamp **[V]**. The split forfeits that property and manufactures the ordering hazard a monotonic `seq` would then be needed to repair (P3) |
| **A third durable store for landing state** | Rejected per L-5 / D-B extend-don't-build; `MERGE_ATTEMPTED` folds into the existing lease payload as one nullable field (R-28). Note this argument is applied once and locally — see §5's outstanding store audit |
| **Post-hoc first-parent assertion instead of a pre-merge lease** | Detect-after-landing. `main` has already changed by the time it fires; it rolls nothing back and blocks no merge (R-8) |

---

## 8. References

**Verified at HEAD (`17011f89c`) this session.** Every **code and skill** cite the decision rests on
was re-grounded; `[V]` throughout this document means exactly that. It does **not** extend to the
blocked-mechanism reasoning at §7 (the squash/ancestry defect and the content-blind trust-boundary
ruling on `PATCH /git/refs`), which is council-recorded.

- `tools/arc_metrics.py` — `REPO`/`LEDGER` `:44-45` (no env override) · `QUEUE_DIR` `:59-63` ·
  `MERGED_REF` `:79` · `run()` `:134-146` (no `timeout=`) · `extract()` `:280`, `gh_pr` `:284`,
  `ci_metrics` `:376` · `publish_exclusive` `:516` · unknown-ownership rule `:586-588` ·
  `_claim_arc` atomicity `:602-610` · `FileNotFoundError` idiom `:633-638` · `os.replace` `:666`,
  `:746`, `:754` · `flock` → 0 occurrences · `lane_id` → 0 occurrences repo-wide
- `tools/hooks/permission-guard.sh` — loop-mode gate `:76` · `_bash_args_safe` `:122-144` ·
  raw worktree-remove deny `:57-65` · `_safe_worktree_remove_wrapper` `:184-191` · wrapper allow
  `:288-290` · deny block `:314-340` (incl. force-push `:322`, branch-deletion `:328`) · allow
  alternation `:427`
- `tools/hooks/test_permission_guard.sh` — `gh pr merge → allow` `:167-169` **and** `:328-329`
- `tools/hooks/loop_lib.sh` — `loop_now()` `:44` (second precision) · `loop_log` `:84` (single `>>`) ·
  AWK reducer `:149-156` (keys `$3`/`$4`; `$2` never read)
- `tools/codex_context_guard.py` — `Finding` `:113-117` (`severity, code, message` only)
- `.claude/skills/two-lane/SKILL.md` — build/land split `:8` · organic-pain bar `:140-142`
- `.claude/skills/ship-pr/SKILL.md` — `state=MERGED` abort `:190-191`
- `deploy/self-hosted-local/compose.yaml` — project name `:1`, ports 3200/4317/4318/3000 ·
  `justfile:471,475,479` pass no `-p`
- GitHub API — `main` `protected: false`, rulesets `[]`
- Absent at HEAD: `tools/codex_review.py` · `tools/arc_disjoint_check.py` · `U-WT-09` (0 matches)

**Council-recorded, not independently re-verified.** The R-numbered rulings (R-1…R-29) and the
E4 gate rounds are cited from `HARNESS-LOOP-AND-LANES-DESIGN-v2.md` §10a as deliberation history.
Also council-recorded rather than re-verified here: the CI cancellation semantics (`ci.yml:42-45`),
green-timing exclusion (`arc_metrics.py:270-277`), and the `ROADMAP_STATUS_DRIFT` emission sites.

**Design constraints L-2 / L-5 / D-B** — carried at
`.harness/council/loop-lanes-design-v1/03-codex-advisor/codex-primer.md`, verbatim at HEAD **[V]**:

- **L-2** (`:124`) — *"Lease-file protocol, not a coordinator process. No daemon, no spawner, no
  merge-queue lock"*
- **L-5** (`:127`) — *"JSONL stays the durable record. sqlite rejected — new shared DB+WAL surface,
  no correctness gain, loses git-diffability"*
- **D-B** (`:108`) — *"Extend existing records; do NOT build a new ledger"*

**Governing artifacts.** `CLAUDE.md` §11.2 (posture), §12.2.1 (merge-lane fixed point), X-AL-1
(substrate boundary), CP-AL-1 (topology anti-leakage) · council charter
`.harness/council/loop-lanes-design-v1/00-CHARTER.md`

**Design + review lineage.**
`~/.gstack/projects/arhugula-v2/research/HARNESS-LOOP-AND-LANES-DESIGN-v2.md` (authoritative design,
supersedes v1) · `…/HARNESS-LOOP-AND-LANES-DESIGN-v2-ARCHITECTURE-REVIEW.md` (architectural review,
source of §3.2 P1–P4 and §5's two flagged residuals)

---

## 9. Filing footer

Recommendations at §3.2 and §6 are **not** operator-ratified; §3.1 is. Superseding this ADR requires
a new `ADR-HE-N` citing this one. Revisions to the H_T authority chain are out of scope by
construction — this record governs H_E tooling only.
