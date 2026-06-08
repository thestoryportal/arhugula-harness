---
stepsCompleted: [1, 2, 3, 4]
inputDocuments:
  - "02-prd/prds/prd-arhugula-v2-2026-06-04/prd.md (FR-1..FR-22, NFR-1..NFR-8, SM-1..SM-4, SM-C1..SM-C4)"
  - "02-prd/prds/prd-arhugula-v2-2026-06-04/addendum.md (mechanism + transport + schemas)"
  - "04-architecture/architecture.md (ARD — component contracts, data schemas, §9 ratification register)"
runMode: 'autonomous (background session — [C] continue gates auto-resolved + documented in §Assumptions & Auto-Continued Gates)'
project_name: 'Context & Memory Layer (Harness Self-Governance)'
user_name: 'Robert'
date: '2026-06-08'
---

# Context & Memory Layer (Harness Self-Governance) - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for the **Context & Memory Layer (Harness Self-Governance)**, decomposing the requirements from the PRD (`prd.md` + `addendum.md`) and the Architecture Decision Document (`architecture.md` / ARD) into implementable stories. There is **no UX Design document** for this layer — it is a non-UI process-governance feature (the only "UI" surface is the three-integer SessionEnd health-line, per ARD §3.0); the UX-requirements extraction step is correctly skipped and **no `UX-DR` items are fabricated**.

**The spine, stated once (PRD §1; ARD §0.3 / §6.2 / §10.1):** success is **measured drift-reduction in real coding sessions, graded by a human (the WS-0 probe)** — *never* byte≤cap, *never* generic architecture-quality criteria, *never* "the file got smaller." Every acceptance criterion below ties to that real success gate (SM-1..SM-4 / SM-C1..SM-C4 and the six drift classes D1–D6). **Proportionality is binding** (NFR-1): the large deferred tail (PRD §6.2 / ARD §8) and the principled-refusal register (PRD §5 / ARD §2.8) are out of scope by construction and are listed, never decomposed into stories.

> **Two load-bearing disciplines for the reader of these stories.**
> 1. **No silent absorption of unratified ARD §9 decisions (X-AL-3 / PRD's worst failure mode).** Where a story depends on a decision still pending operator ratification at ARD §9, the dependency is flagged `**Ratification dependency: ARD §9.x**` on the story and the ARD's recommended default is cited as *a default, ratification-pending* — never baked in as settled. The full list is collected in the **Ratification Dependencies** section near the end.
> 2. **Byte-count is never a success condition.** The byte-budget guardrail (Epic 5) legitimately *measures* a byte-sum as its mechanism, but no story's *win* is a smaller file; the slim's success is the WS-0 probe, and one explicit false-green guard AC (SM-C1) is carried.

## Requirements Inventory

### Functional Requirements

*Extracted verbatim-faithful from PRD §4 (FR-1..FR-22). Each maps 1:1 to a PRD feature / DESIGN MVP workstream / ARD component (the §7.4 coverage backbone).*

- **FR-1: Binary drift taxonomy.** The grader can label any real session against the six drift classes D1–D6, each scored as a binary incident (1 if observed, 0 if not) from the transcript alone. (WS-0 / C-GATE)
- **FR-2: Counterfactual before/after probe.** The operator can run the probe as two arms — Arm A (HEAD layer) and Arm B (slimmed layer) — over real coding-loop sessions across representative workflow classes, producing per-class incidence for each arm. (WS-0 / C-GATE)
- **FR-3: Pass condition by tallied incidents.** The probe yields a `SOUND` verdict only when Arm B's tallied incidence is ≤ Arm A on every class AND strictly < on at least one class; the verdict is derived from tallied incidents, never inferred from the byte-count. (WS-0 / C-GATE)
- **FR-4: `not-exercised` cell rule and `INCOMPLETE` verdict.** A drift class with zero incidents in *both* arms is recorded `not-exercised` (distinct from `passed`) and does not satisfy the "reduces ≥1 class" clause; when D4 or D6 is `not-exercised` the verdict is `INCOMPLETE-on-{D4,D6}` (literal `INCOMPLETE-on-D4` / `INCOMPLETE-on-D6` / `INCOMPLETE-on-D4-and-D6`), never `SOUND`. (WS-0 / C-GATE)
- **FR-5: Grading codebook-lens.** The grader can map an observed failure to its drift class via a fixed lens — *recall* failure → D1/D4, *artifact* failure → D2/D5, *continuation* failure → D3/D5 — making the human label reproducible without adding any test case. (WS-0 / C-GATE)
- **FR-6: Operator waiver for unexercised rare classes.** The operator can discharge an `INCOMPLETE` verdict by recording an explicit waiver that names the specific untested rare class (D4 and/or D6), allowing a `SOUND` verdict to stand; no "keep running until exercised" minimum-exposure mandate is imposed. (WS-0 / C-GATE)
- **FR-7: Verify-before-evict dependency scan.** The operator can run a dependency scan that searches rules, hooks, scripts, and recovery-paths for references to any content proposed for eviction, producing the set of load-bearing invariants that must survive the slim; eviction does not proceed until the scan completes. (WS-1 / C-SLIM)
- **FR-8: L1 deterministic slim-time assertion.** The system asserts once, at slim-time, that every invariant the dependency scan proved load-bearing still emits or resolves after the provenance is evicted; a failed assertion blocks the slim. Scope = exactly the scan-discovered invariants (not a hard-coded list); judge-free and deterministic. (WS-1 / C-SLIM)
- **FR-9: Provenance eviction to a versioned archive.** The operator can evict the version-provenance out of the every-turn prefix into a git-versioned archive, such that the content remains byte-recoverable verbatim from git and the spec files; eviction is a move, never a deletion. (WS-1 / C-SLIM)
- **FR-10: Altitude-content retention and attention-positioning.** The slimmed `CLAUDE.md` retains the behavior-governing altitude content (operating rules, posture, the loop, conventions, locked rules — preserved verbatim) and positions critical content near the start and end of the window rather than mid-window. (WS-1 / C-SLIM)
- **FR-11: Source-of-truth pointer and artifact→version index.** The agent can resolve the canonical version of any design-substrate artifact via the SSOT pointer and the `design-substrate/INDEX.md` artifact→version mapping, without a version carried inline in the prefix; the MVP index is un-anchored (artifact→version only, no `file#header` anchors). (WS-2a / C-NAV)
- **FR-12: Navigation-set guardrail.** The layer constrains the navigation set to established anchors only and forbids the inversions: no invented `GC.md`/`ROUTING.md`/`CATALOG.md`, no authored `WORKFLOWS.md`, no `@import`-ing any navigation anchor into `CLAUDE.md`, no hand-authored `#section` anchors at the MVP floor. (WS-2a / C-NAV)
- **FR-13: Degree-keyed selection rule.** Compaction can keep or retire each lesson by its wiki-link in-degree: KEEP-HOT (in-degree ≥5, descriptions full), KEEP-LINKED (1–4 inbound, compaction-eligible), ARCHIVE (zero-inbound, body archived + index line dropped, recoverable on demand); all three tiers distinguishable from the in-degree alone; the pin-set re-derived against the current count at slim-time. (WS-3a / C-MEM)
- **FR-14: Bi-temporal supersede-mark (never silent-drop).** When compaction retires a lesson, it marks the lesson superseded (`valid_until` + `superseded_by: [[slug]]` frontmatter) and archives the body, rather than silently dropping it — so compaction is non-lossy and recoverable. (WS-3a / C-MEM)
- **FR-15: Three-integer SessionEnd health-line.** At session boundary the operator is shown exactly three grep-derived integers: `notes-superseded`, `notes-untouched-beyond-N-days`, and `patterns-unwritten-with-≥4-refs` — boundary-only, not a rot-score, not a dashboard. (WS-3a / C-MEM)
- **FR-16: One-time hygiene write of dangling high-reference lessons.** The operator can perform a finite one-time write of the high-reference (≥4 inbound) pattern lessons that are already promised but have no note file, bringing durable memory into a consistent state. This is one-time hygiene, NOT the recurring consolidation pass (deferred). (WS-3a / C-MEM)
- **FR-17: Effective-auto-loaded-context byte-budget check.** The system can compute the effective auto-loaded context as the deterministic byte-sum of `CLAUDE.md` + its `@import`-closure + `MEMORY.md`, and check it against a budget via a `--check` invocation; byte-sum only (not attention-weighted/token-estimated), not a link check. (WS-4 G1 / C-G1)
- **FR-18: Warn-then-fail mode with explicit waiver.** The guardrail runs in warning mode before the slimmed baseline is clean and in hard-fail mode after; a clearly-marked override/waiver path always exists so a justified breach is never blocked into unreadable compression. (WS-4 G1 / C-G1)
- **FR-19: Review-time-only execution (never-halt composition).** The guardrail runs only at code-review/CI time and never as an in-session runtime blocker, so it composes with never-halt. (WS-4 G1 / C-G1)
- **FR-20: Snapshot/versioned store with atomic writes.** The operator can snapshot and version the out-of-worktree memory store with git as the rollback boundary, and every write to the store is atomic (no partial state observable); a superseded lesson's archived body is recoverable from a store snapshot. (X-min / C-STORE)
- **FR-21: Stale-base (optimistic-concurrency) detection.** The store detects when a write is based on a stale read, so two independent worktree sessions writing concurrently cannot silently clobber each other; serialization is at the store (OCC), not at a topology lead. Full write-locking is NOT part of this FR (deferred to X-full). (X-min / C-STORE)
- **FR-22: Reinject-pointer-resolvability floor.** The recovery path names reinject-pointer-resolvability as an explicit requirement; at the MVP floor an absence-guard graceful-degrades when a re-injected pointer's target file is missing. Resolution-validation of a present-but-wrong/drifted target is NOT in the MVP floor (it rides the deferred G-LINK, not the byte-budget guardrail). (X-min / C-STORE)

### NonFunctional Requirements

*Extracted from PRD §8 (NFR-1..NFR-8) — bounds, not adjectives. NFRs are enforced as constraints across stories (traced in the NFR Coverage Map), not as standalone stories.*

- **NFR-1: Proportionality (the governing constraint).** No MVP item may add a session, a tool, a synthetic case, a model-judge, a daemon, or a dashboard beyond what PRD §4 specifies. A change that increases the layer's own governance weight without a drift justification is out of bounds by construction.
- **NFR-2: Attention-aware context budget.** Critical governing content sits near the start or end of the every-turn window, never mid-window, against the lost-in-the-middle attention degradation (a 40–60% recall trough in the middle of a long context).
- **NFR-3: Non-lossiness of durable memory.** No enforced compaction may drop a lesson without a recoverable supersede-mark; a silent lossy drop is a defect (the D4 incident this layer exists to replace).
- **NFR-4: Recoverability and concurrency-safety.** The memory store is snapshot/versioned with git as the rollback boundary, writes are atomic, and stale-base writes are detected (OCC). Full locking is out of scope until an observed race.
- **NFR-5: Observability at boundary, not runtime.** Memory health is surfaced as exactly three plain integers at session boundary; no runtime monitoring surface, no continuous score, no live console.
- **NFR-6: Never-halt composition.** All gates in this layer (the byte-budget guardrail; the deferred G-LINK) run at code-review/CI time only and never halt a live session.
- **NFR-7: Honest verdict integrity.** The success gate must be able to fail and must return `INCOMPLETE` rather than a clean pass when the rare classes were not exercised.
- **NFR-8: Non-lossy lane discipline (authoring vs execution).** Nothing load-bearing is ever destroyed; but the execution arc DOES rewrite the prefix — additively-as-navigation (eviction moves provenance to a git-versioned archive where it stays byte-recoverable), never as deletion. Authoring scope adds no edits to `design-substrate/**` content, `harness-*/src`, `CLAUDE.md` content, or the roadmap.

### Additional Requirements

*Architecture-derived requirements that impact epic/story creation, extracted from ARD §2 (decisions), §3 (component homes), §6 (sequencing), and §9.5 (corpus-vs-HEAD divergences). Per Step 1 §5 of the skill.*

- **AR-A — No greenfield starter template (ARD §2.0).** This layer is an additive governance overlay on the existing committed `arhugula-v2` monorepo — there is NO starter/scaffold to set up. Per ARD §2.0 + §6.1 step 0, **the first implementation step is WS-0 baseline capture (Arm A) on current HEAD**, NOT a project-init command. → Epic 1 Story 1 is "define the D1–D6 taxonomy + verdict function," not a scaffold story.
- **AR-B — Zero new runtime dependencies (AD-0).** The layer is built from Python 3.12 stdlib + the existing repo toolchain (`grep`/`wc`/byte-sum/frontmatter-parse/git). Pulling a graph engine, eval framework, or embedding library would BE the bloat this layer cuts. Affects every story's implementation.
- **AR-C — Committed stack (AD-1..AD-6).** Python 3.12+; Pydantic v2 only where a typed schema is authored (MVP reads frontmatter by `grep`, a Pydantic model is the enhancement path only); `pytest` + `pyright`-strict + `ruff`-clean on all new `tools/` scripts; git-as-state (no external DB, no lockfile-daemon); plain-text/markdown as the interface for every governance artifact.
- **AR-D — Guardrails modeled on the existing `tools/substitution_ledger.py --check` (AD-4).** The `--check`/`--summary`/exit-0-or-1/CI-tier pattern already exists and is proven in-repo; G1 (and the deferred G-LINK) copy this shape. No eval framework, no model-judge.
- **AR-E — Existing in-repo integration sites the layer extends (ARD §3.4 / §4.5 / §4.7 / §3.6).** The SessionEnd report at `session-end-cleanup.sh` (the MEMORY.md-cap block, ~lines 49-56) is the health-line host; the `postcompact-reinject.sh:28-32` `CK`/`CKNOTE` absence-guard is the reinject floor (PRESENT at HEAD); the memory store at `~/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` is the C-STORE / C-MEM home; the archive target is `memory/archive/`.
- **AR-F — Corpus-vs-HEAD divergence: the memory store is NOT its own git repo at HEAD (ARD §9.5.1 / AD-17).** There is no `memory/.git`; `rev-parse --show-toplevel` resolves to an ancestor `~/` repo. So X-min's first concrete step is **"create a git repo AT the store + first snapshot," NOT merely "first commit on an existing repo."** OCC `base_rev` MUST resolve against the store-local repo, never the ancestor. (Surfaced, not absorbed — a ratification item, §9.5.1.)
- **AR-G — Corpus-vs-HEAD divergence: G1 input-scope boundary (ARD §9.5.2 / AD-16).** G1 measures the harness's own **root** auto-loaded set (root `CLAUDE.md` + its `@import`-closure + project `MEMORY.md`); it scopes OUT operator-global `~/.claude/CLAUDE.md` + `@RTK.md` and the per-axis `harness-*/CLAUDE.md` files (which are populated — IS 17,444 + AS 29,032 + CP 38,031 + OD 46,928 = 131,435 B at HEAD — but load additively within their own subtree). The per-axis slim is a separate §7-framework F4 application, NOT a widening of root G1. (Ratification item, §9.5.2.)
- **AR-H — Corpus-vs-HEAD divergence: MEMORY.md / count growth (ARD §9.5.3).** MEMORY.md reads ~15,995 B / 183 note files at the ARD's 2026-06-08 snapshot (grown from the 10,306 B arc-open snapshot; the top hub grew 65→83). **This is "No ratification needed" (ARD §9.5.3) — recorded as confirmation of the "re-derive the pin-set at slim-time, never freeze a list" discipline, NOT a ratification item and NOT new work.** Empirical scale figures re-derive at slim-time (AD-12); do not freeze the snapshot numbers.
- **AR-I — Cross-step sequencing (ARD §6.1 ★NEW-1).** The C-NAV `INDEX.md` (the artifact→version map) MUST complete before / atomically-with the C-SLIM eviction of a §2 version-row — a version-string must be navigable via the INDEX before it leaves the prefix, else the eviction strands the canonical-version pointer. (Carried as a cross-epic dependency on the relevant stories.)

### UX Design Requirements

**N/A — no UX Design document exists for this layer.** This is a non-UI process-governance feature; the only "UI" surface is the three-integer SessionEnd health-line (covered by FR-15, Epic 4). Per the skill's Step 1 §6, the UX-requirements extraction is correctly skipped and **no `UX-DR` items are fabricated** (fabricating UX-DRs for a non-UI feature would be the silent-scope-extension failure mode). Confirmed against ARD §3.0 ("Frontend → N/A → the 3-integer SessionEnd health-line; dashboard permanently in WS-5 deferral").

---

## Epic List

*Six epics, organized by USER VALUE (each delivers a complete, end-to-end governance capability), one per PRD §4 feature / DESIGN MVP workstream / ARD component. File-churn overlap is low: the only shared surface — the memory store, touched by Epic 4 (C-MEM) and Epic 6 (C-STORE) — splits cleanly per the ARD §3.7 C2↔C3 ownership cut (C-MEM owns the at-rest retention rule + supersede schema; C-STORE owns the store's git/atomic/OCC substrate), so **consolidation was considered and rejected**: these are distinct concerns with a fixed ownership seam, not file-churn on one component. The reusable framework (ARD §7) is explicitly a **template that adds nothing beyond §4** — it is NOT a 7th epic and is listed under Out of Scope.*

**Cross-epic sequencing (named honestly, not faked as independence).** The WS-0 success gate (Epic 1) **brackets** the build: its Arm-A baseline is captured FIRST (foundational — before any slim ships, FR-2), and its Arm-B-plus-verdict is the CLOSING action that depends on Epics 2–6 having landed (the §6.2 close decision). Within Epic 1 the bracket is made explicit by ordering the instrument-build stories first and the Arm-B/verdict story last with a documented cross-epic dependency. One further cross-epic ordering holds: **Epic 3's `INDEX.md` must precede Epic 2's version-row eviction** (AR-I / ARD §6.1 ★NEW-1) — carried as an explicit dependency note on the relevant stories.

### Epic 1: Trustworthy Success Gate — measure drift, honestly
The operator can prove the layer reduced drift (or honestly say "not yet"), by grading real coding sessions on six binary drift classes across a blinded before/after probe — the falsifiable acceptance gate for the entire layer, adding zero new tooling, sessions, synthetic cases, or model-judge. This is the definition of done (ARD §6.2 / §10.1).
**FRs covered:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6

### Epic 2: Lean Every-Turn Context — slim CLAUDE.md without losing what governs behavior
The agent re-reads a lean, behavior-first prefix with the governing rules positioned where attention lands, after a safety-interlocked one-time slim (verify-before-evict → L1 assert → evict provenance to a git-versioned archive → keep + position altitude content) that is structurally prevented from causing the drift it aims to cut.
**FRs covered:** FR-7, FR-8, FR-9, FR-10

### Epic 3: Discoverable Canonical Truth — navigate to "canonical = vN" instead of carrying it inline
The agent can resolve the canonical version of any design-substrate artifact by navigating an `artifact→version` index + a source-of-truth pointer, instead of reading a stale inline version where it rots — closing the wrong-version-read (D2) hazard without adding eager prefix weight, and with a standing guardrail that forbids re-bloating the navigation set.
**FRs covered:** FR-11, FR-12

### Epic 4: Trustworthy Durable Memory — non-lossy compaction with a health glance
The agent relies on a durable memory where nothing learned was silently lost: compaction keeps/retires lessons by connectivity, marks every retirement as superseded (never silent-drops), and surfaces exactly three plain integers of memory health at session boundary — plus a finite one-time hygiene write that clears the two already-promised dangling lessons.
**FRs covered:** FR-13, FR-14, FR-15, FR-16

### Epic 5: Leading-Indicator Budget Guardrail — keep the prefix lean at review-time, never in-session
The operator gets a cheap review-time `--check` that the slim took and that provenance is not creeping back into the effective auto-loaded context — warn-then-fail with an explicit waiver, running strictly at CI/review time so it composes with never-halt — a reported leading indicator, never the success gate.
**FRs covered:** FR-17, FR-18, FR-19

### Epic 6: Recoverable, Concurrency-Safe Memory Store — parallel sessions cannot clobber each other
The operator can trust the out-of-worktree memory store under the parallel multi-session workflow: it is snapshot/versioned with git as the rollback boundary, writes are atomic, stale-base writes are detected (OCC, not full locking), and the resumption path degrades gracefully when a re-injected pointer's target is missing.
**FRs covered:** FR-20, FR-21, FR-22

### FR Coverage Map

*Every FR-1..FR-22 maps to exactly one owning epic. Mirrors ARD §7.4 (22/22, zero orphans, zero epic without an FR).*

- **FR-1:** Epic 1 — binary D1–D6 drift taxonomy
- **FR-2:** Epic 1 — counterfactual two-arm (Arm A / Arm B) probe
- **FR-3:** Epic 1 — `SOUND` pass condition by tallied incidents (never byte-count)
- **FR-4:** Epic 1 — `not-exercised` cell rule + `INCOMPLETE-on-{D4,D6}` verdict
- **FR-5:** Epic 1 — grading codebook-lens (recall/artifact/continuation → D-class)
- **FR-6:** Epic 1 — operator waiver for unexercised rare classes
- **FR-7:** Epic 2 — verify-before-evict dependency scan
- **FR-8:** Epic 2 — L1 deterministic slim-time assertion
- **FR-9:** Epic 2 — provenance eviction to a git-versioned archive
- **FR-10:** Epic 2 — altitude-content retention + attention-positioning
- **FR-11:** Epic 3 — SSOT pointer + `artifact→version` INDEX
- **FR-12:** Epic 3 — navigation-set guardrail
- **FR-13:** Epic 4 — degree-keyed (KEEP-HOT/KEEP-LINKED/ARCHIVE) selection rule
- **FR-14:** Epic 4 — bi-temporal supersede-mark (never silent-drop)
- **FR-15:** Epic 4 — three-integer SessionEnd health-line
- **FR-16:** Epic 4 — one-time hygiene write of the two dangling ≥4-ref lessons
- **FR-17:** Epic 5 — effective-auto-loaded-context byte-budget `--check`
- **FR-18:** Epic 5 — warn-then-fail mode with explicit waiver
- **FR-19:** Epic 5 — review-time-only execution (never-halt composition)
- **FR-20:** Epic 6 — snapshot/versioned store with atomic writes
- **FR-21:** Epic 6 — stale-base (OCC) detection
- **FR-22:** Epic 6 — reinject-pointer-resolvability floor (absence-guard)

### NFR Coverage Map

*Every NFR-1..NFR-8 traces to the epic(s)/story-ACs that enforce its bound (mirrors ARD §10.3). NFRs are cross-cutting constraints, not standalone stories.*

- **NFR-1 (Proportionality):** ALL epics — each story's ACs hold to PRD §4 / ARD §4 scope; enforced negatively by the Out-of-Scope section (no daemon/dashboard/score/synthetic-corpus/model-judge). Explicit anti-bloat ACs on Story 4.3 (exactly 3 integers), Story 1.1 (zero new tooling/script/model-judge in the gate) + Story 1.2 (no synthetic corpus), Story 2.1 (one-shot script, not a standing CI gate), Story 4.1 (no recompute engine), Story 5.3 (one CI step, no daemon/runtime surface).
- **NFR-2 (Attention-aware budget):** Epic 2 — Story 2.4 (positioning near start/end vs the mid-window trough; verified by inspection, no numeric boundary invented).
- **NFR-3 (Non-lossiness):** Epic 4 — Story 4.2 (supersede-mark + archive-move, structural); Epic 6 — Story 6.1 (snapshot recoverability of archived bodies).
- **NFR-4 (Recoverability + concurrency):** Epic 6 — Stories 6.1 (git rollback + atomic), 6.2 (OCC).
- **NFR-5 (Observability at boundary):** Epic 4 — Story 4.3 (exactly 3 grep-derived integers at SessionEnd, boundary-only, no runtime console/score).
- **NFR-6 (Never-halt composition):** Epic 5 — Story 5.3 (review-time/CI only, never an in-loop runtime blocker); Epic 6 — Story 6.3 (reinject floor continues-on-absence, never aborts).
- **NFR-7 (Honest-verdict integrity):** Epic 1 — Stories 1.3, 1.4 (the gate can FAIL; `INCOMPLETE` over false-pass; `not-exercised` ≠ `passed`).
- **NFR-8 (Non-lossy lane discipline):** Epic 2 — Story 2.3 (eviction is additive-as-navigation = a move to a git-versioned archive, byte-recoverable, never deletion); reinforced by the cross-cutting lane rule (authoring scope adds no `design-substrate/**`/`harness-*/src`/`CLAUDE.md`-content/roadmap edits).

---

## Epic 1: Trustworthy Success Gate — measure drift, honestly

**Goal.** Give the operator a falsifiable, human-graded before/after probe that proves the layer reduced drift — or honestly returns "not yet" when the rare classes were never exercised. This is the **definition of done for the entire layer** (ARD §6.2 / §10.1): success is measured drift-reduction, never byte-count. The whole gate adds **zero** new tooling, sessions, synthetic cases, or model-judge (PRD §4.1 feature-NFR; SM-C4).

**FRs covered:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6. **Relevant NFRs:** NFR-1 (proportionality — zero new tooling), NFR-7 (honest-verdict integrity). **Drift classes:** the gate *defines and measures* all of D1–D6; D4 + D6 are the designated rare/expensive classes. **Metrics:** SM-1 (the primary gate), SM-C1/SM-C3 (counter-metrics).

**Sequencing note (the WS-0 bracket).** Stories 1.1–1.5 build the *instrument* and capture the Arm-A baseline FIRST, before any slim ships (FR-2; ARD §6.1 step 0). Story 1.6 (the operator waiver) is part of the instrument. The Arm-B capture + verdict computation is the **closing action of the whole layer** and depends on Epics 2–6 having landed — it is carried as Story 1.7 with an explicit cross-epic dependency. Within the epic, each story depends only on previous stories.

### Story 1.1: Define the binary D1–D6 drift taxonomy

As a grader (the operator),
I want a fixed taxonomy of exactly six binary drift classes, each with a one-line transcript-observable criterion,
So that I can label any real session for drift from the transcript alone, with no tool or model.

**Acceptance Criteria:**

**Given** a real coding-loop session transcript
**When** the grader applies the taxonomy
**Then** each of the six classes D1 (stale-rule use), D2 (wrong-canonical-artifact), D3 (forgotten task-constraint), D4 (memory-pollution/context-poisoning), D5 (bad resumption), D6 (instruction-conflict) has a documented one-line observable criterion a human can apply without running any tool or model (FR-1)
**And** each per-session, per-class label is exactly 0 or 1 — no fractional or weighted scores
**And** the taxonomy is exactly six classes, with D4 and D6 explicitly designated the rare/expensive classes (the `INCOMPLETE` rule, used by Story 1.4)
**And** the taxonomy artifact is a spec + a grading worksheet under the planning tree — it introduces NO script, NO model-judge, NO synthetic test case (NFR-1; ARD §3.1 anti-bloat self-attestation)

### Story 1.2: Capture the Arm-A baseline on current HEAD before any slim ships

As the operator,
I want to grade a set of real coding-loop sessions on D1–D6 against the current-HEAD layer (Arm A),
So that the counterfactual baseline is captured before the slim changes anything, not reconstructed after the fact.

**Acceptance Criteria:**

**Given** the D1–D6 taxonomy (Story 1.1) and the layer at current HEAD
**When** the operator runs the probe's Arm-A capture
**Then** the probe reuses real `[[use-the-product-probe-pattern]]` coding-loop sessions — NO synthetic or authored corpus is introduced (FR-2; SM-C4; refusal R7)
**And** Arm A is captured against current HEAD *before* the slim (Epic 2) ships — the baseline is not reconstructed after the fact (FR-2)
**And** the output is a per-class D1–D6 incident count for Arm A over the graded sessions
**And** each cell is normalized to incidence-per-task (task-count tracked per session) and each arm's workflow-class distribution is recorded, per the operator-ratified arm-comparability REPORT form (ARD §4.2 / §9.6.1)
**And** **Ratification dependency: ARD §9.6.1** — the credible session-count floor (default ~15–25) and the named representative workflow-class set are operator-pending; the story proceeds on the ~15–25 default explicitly as a default, and a too-thin sample is allowed to surface honestly as `INCOMPLETE` rather than being force-padded (no minimum-exposure mandate, FR-6)

### Story 1.3: Author the `SOUND` pass-condition function (verdict from tallied incidents only)

As the operator,
I want the verdict function authored to compute the pass condition purely from a D1–D6 incidence matrix (Arm B ≤ Arm A on every class AND < on ≥1 class),
So that the layer is judged by measured drift-reduction and can never be declared a success because the byte-count looks good.

**Acceptance Criteria:**

**Given** the D1–D6 incidence-matrix shape (Story 1.1) and a representative/illustrative two-arm incidence matrix (real Arm A from Story 1.2; the verdict function is authored and unit-exercised against illustrative incidence — it does NOT require the live Arm-B run, which is Story 1.7's application of this function)
**When** the verdict function is authored and exercised against the illustrative matrix
**Then** a `SOUND` verdict is emitted only when Arm B's tallied incidence is ≤ Arm A on every class AND strictly < on at least one exercised class (FR-3)
**And** a run where Arm B exceeds Arm A on any class does NOT yield `SOUND` (it routes to restore-and-re-measure, SM-C2)
**And** a run where Arm B equals Arm A on every class (no class strictly improved) does NOT yield `SOUND` (FR-3)
**And** the verdict computation takes the D1–D6 incidence matrix (+ the recorded per-arm class-distribution sidecar, ARD §4.2) as its only input — NO byte-delta, cache metric, or file-size figure participates (FR-3; the verdict strings are the literal `SOUND` / `INCOMPLETE-on-D4` / `INCOMPLETE-on-D6` / `INCOMPLETE-on-D4-and-D6` / `SOUND-COMPOSITION-CONFOUNDED` / `SOUND-WAIVED`, used verbatim per ARD §5.2)
**And** *(false-green guard, SM-C1 — the primary failure mode to guard against)* a clean byte-count or a green byte-budget guardrail (Epic 5) is NEVER read as a pass-signal for the layer; the only pass-signal is this matrix

### Story 1.4: Author the `not-exercised` cell rule and the honest `INCOMPLETE` verdict

As the operator,
I want the verdict function extended so a drift class with zero incidents in BOTH arms is recorded as `not-exercised` (distinct from `passed`), and an `INCOMPLETE` verdict is returned when a rare class (D4/D6) is unexercised,
So that the gate is honest — it never claims a clean `SOUND` with a buried footnote about a class nobody exercised.

**Acceptance Criteria:**

**Given** the verdict function (Story 1.3) and the D1–D6 incidence-matrix shape (Story 1.1), exercised against an illustrative two-arm incidence (this rule is authored against illustrative incidence — it does NOT require the live Arm-B run, which is Story 1.7's application)
**When** the verdict function evaluates each class
**Then** a class with zero incidents in both arms is labeled `not-exercised` and CANNOT be counted as the strictly-improved class (FR-4; `not-exercised` ≠ `passed`)
**And** if D4 or D6 is `not-exercised`, the returned verdict string literally names the unexercised set — `INCOMPLETE-on-D4`, `INCOMPLETE-on-D6`, or `INCOMPLETE-on-D4-and-D6` — never `SOUND` or `PASS` (FR-4; NFR-7)
**And** a `SOUND` verdict requires every one of D4 and D6 to have been exercised OR explicitly waived (Story 1.6)
**And** `INCOMPLETE-on-D4` is dischargeable by the standing `patterns-unwritten-with-≥4-refs` health-line signal (Epic 4 / FR-15) OR a waiver; `INCOMPLETE-on-D6` has no standing mitigation and is discharged only by exercising D6 or an explicit waiver (FR-4)
**And** *(SM-C3 guard)* a green byte-budget guardrail + untouched health-counts are NEVER read as "memory is healthy" when the rare classes went unexercised — the honest `INCOMPLETE` is the correct signal, not a defect to suppress into a pass

### Story 1.5: Provide the grading codebook-lens for reproducible labels

As the grader,
I want a fixed lens that maps an observed failure-type to its drift class (recall→D1/D4, artifact→D2/D5, continuation→D3/D5),
So that my labels are reproducible across re-gradings without adding any test case.

**Acceptance Criteria:**

**Given** an observed failure in a transcript
**When** the grader applies the codebook-lens before writing a D-class cell
**Then** the lens is a documented mapping from the three failure-observation types (*recall* / *artifact* / *continuation*) to D-classes, and applying it introduces, runs, or authors NO test (FR-5)
**And** the same grader applying the lens to the same observed failure arrives at the same D-class on re-grading (intra-rater consistency; cross-grader agreement is NOT claimed at solo scale)
**And** the lens is applied *before* writing each D-class cell, every time (ARD §5.2 codebook-lens-before-labeling rule)
**And** the two zero-machinery content-blinding disciplines are applied before grading — temporal separation (grade Arm B in a later session) + evicted-marker redaction (mask removed-provenance tokens) — on top of arm-label shuffle, with the residual self-grading bias *disclosed, not eliminated* (ARD §3.1 / AD-19; NO redaction/temporal pipeline machinery is built — an independent grader is deferred-on-trigger, not an MVP add)

### Story 1.6: Record an operator waiver for an unexercised rare class

As the operator,
I want to discharge an `INCOMPLETE` verdict by recording an explicit waiver that names the specific untested rare class,
So that a `SOUND` verdict can stand when I have judged the unexercised class acceptable — without any forced "keep running until exercised" mandate.

**Acceptance Criteria:**

**Given** an `INCOMPLETE-on-D4` / `-D6` / `-D4-and-D6` verdict
**When** the operator records a waiver
**Then** the waiver names the specific class (D4 and/or D6) it covers and is recorded explicitly, not implied by silence (FR-6)
**And** with a recorded waiver for an unexercised class, the verdict may become `SOUND` (or the distinct `SOUND-WAIVED`, per the §9.6.3 sharpening); without it, the verdict stays `INCOMPLETE` on that class (FR-6)
**And** NO "keep running sessions until the class is exercised" mandate is imposed as a precondition — the minimum-exposure floor is refused (PRD §5); exercising the class is one discharge path, the waiver is the other (FR-6)
**And** **Ratification dependency: ARD §9.6.3** — the waiver's author/owner and record-location, and the adoption of the distinct `SOUND-WAIVED` verdict, are operator-pending; default per ARD §9.6.3 is "operator authors + owns; recorded in the WS-0 grading worksheet alongside the verdict; `SOUND-WAIVED` adopted; the waiver names which reason fired (rare-class vs `composition-confound`)" — carried as a default, ratification-pending, not baked in

### Story 1.7: Capture Arm B on the slimmed layer and emit the close verdict

As the operator,
I want to grade the same representative workflow classes on the slimmed layer (Arm B, blinded) and compute the close verdict,
So that I can decide whether the layer is done — by measured drift-reduction, honest about the rare classes and any arm-composition skew.

**Acceptance Criteria:**

**Given** Epics 2–6 have landed (the slimmed layer is live) and the Arm-A baseline (Story 1.2) exists
**When** the operator grades Arm B and runs the verdict function (Stories 1.3, 1.4)
**Then** Arm B reuses real sessions across the same representative workflow classes as Arm A, with arm labels de-identified/shuffled before grading (FR-2)
**And** the verdict ∈ {`SOUND`, `SOUND-WAIVED`, `SOUND-COMPOSITION-CONFOUNDED`, `INCOMPLETE-on-D4`, `INCOMPLETE-on-D6`, `INCOMPLETE-on-D4-and-D6`, `FAIL (regression)`, `FAIL (no class improved)`} per the ARD §4.2 verdict function, computed from the matrix + the per-arm class-distribution sidecar only
**And** the close decision follows ARD §6.2: `SOUND`/`SOUND-WAIVED` → the layer is closed; `SOUND-COMPOSITION-CONFOUNDED` → NOT auto-closed (discharge by re-running Arm B over a representative mix OR a recorded waiver → `SOUND-WAIVED`); `INCOMPLETE-on-{D4,D6}` → NOT closed; any class REGRESSED → NOT closed → presume over-eviction (SM-C2) → restore-and-re-measure (the restore PR uses the Epic 5 `--waiver`, NOT blocked by G1 hard-fail; never-halt, NFR-6); a clean byte-count with drift unchanged → the false-green (SM-C1), NOT closed
**And** **cross-epic dependency:** this story is the closing action of the whole layer and cannot complete until Epics 2–6 land (it is NOT independently completable mid-build — the dependency is named, not hidden)
**And** if the regressed class is D5 (bad resumption) → this is the named trigger for the deferred WS-6 6b (D14 recovery build) — recorded, not built here (Out of Scope)

---

## Epic 2: Lean Every-Turn Context — slim CLAUDE.md without losing what governs behavior

**Goal.** Slim the every-turn `CLAUDE.md` to its behavior-governing altitude content, evicting version-provenance to a git-versioned archive — but only through a hard safety interlock (verify-before-evict → L1 assert → evict → position) that makes the slim structurally unable to cause the drift it aims to cut. This is the **primary drift lever**. Success is the Epic 1 WS-0 probe, **NOT** byte-count (PRD §4.2 feature-NFR; SM-C1).

**FRs covered:** FR-7, FR-8, FR-9, FR-10. **Relevant NFRs:** NFR-2 (attention-aware budget), NFR-8 (non-lossy lane discipline), NFR-1 (one-shot scripts, not standing CI). **Drift classes:** the slim's risk is *causing* drift (over-eviction → any class regresses, especially D1/D2); the interlock + WS-0 backstop hold it. **Metrics:** SM-3 (the byte-delta — a reported indicator only), SM-C2 (over-eviction counter-metric).

**Sequencing note.** The four stories are an ordered pipeline (the order is non-negotiable, ARD §6.1 / pattern P7): 2.1 (scan) → 2.2 (L1 assert) → 2.3 (evict) → 2.4 (keep/position). Each depends only on previous stories. **Cross-epic dependency (AR-I / ARD §6.1 ★NEW-1):** Story 2.3's eviction of a §2 version-row MUST be preceded by / atomic-with Epic 3's `INDEX.md` (Story 3.1) — a version-string must be navigable via the INDEX before it leaves the prefix.

### Story 2.1: Run the verify-before-evict dependency scan

As the operator,
I want a dependency scan that searches rules, hooks, scripts, and recovery-paths for references to any content proposed for eviction,
So that I know exactly which invariants are load-bearing and must survive the slim — before anything is evicted.

**Acceptance Criteria:**

**Given** a set of candidate-for-eviction provenance content in `CLAUDE.md`
**When** the dependency scan runs
**Then** the scan covers, at minimum, rules + hooks + scripts + recovery-paths, and its output is the enumerated set of references found (FR-7)
**And** an active reference is defined as a textual reference to a provenance cell (a version string, an artifact-version row, a provenance anchor) found by the grep across the rules/hooks/scripts/recovery-path corpus; a candidate with ≥1 such reference is flagged load-bearing and is NOT silently evicted (FR-7; ARD §3.2)
**And** the scan surface EXCLUDES the provenance set's own internal version-provenance cross-references (the delta-only change-note chain references its own prior versions; counting those intra-eviction-set refs would flag the whole chain un-evictable and the slim would no-op — ARD C2-NEW-1a)
**And** the eviction step (Story 2.3) CANNOT run before this scan has produced its reference set (the interlock; pattern P7)
**And** the scan is a one-shot Python 3.12 stdlib script (`pyright`-strict, `ruff`-clean, `pytest`-covered) — NOT a standing CI gate, NOT a daemon (NFR-1; AD-0)

### Story 2.2: Assert load-bearing invariants still resolve after eviction (L1 slim-time assertion)

As the operator,
I want a judge-free assertion fired once at slim-time that every scan-discovered load-bearing invariant still resolves after the provenance is evicted,
So that a slim that would strand a load-bearing reference is blocked before it ships.

**Acceptance Criteria:**

**Given** the load-bearing invariant set from the dependency scan (Story 2.1)
**When** the L1 assertion runs at slim-time, with the provenance moved to the archive
**Then** the assertion's scope is exactly the scan-discovered invariants — NOT a hard-coded or corpus-derived list (the `[i]`-citation check is an illustration of the form, not the work-item; FR-8; ARD §3.2)
**And** the assertion is judge-free and deterministic: it passes only when ALL scan-discovered invariants resolve post-eviction, and fails when any dangles — no probabilistic or model-graded admission (FR-8)
**And** a failed assertion BLOCKS the slim from being treated as complete (FR-8; pattern P7)
**And** the assertion fires ONCE at slim-time (one-shot, not a standing validator; pattern P3 / NFR-1)

### Story 2.3: Evict version-provenance to a git-versioned archive (a move, never a deletion)

As the operator,
I want to move the version-provenance out of the every-turn prefix into a git-versioned archive,
So that the prefix is lean while the provenance remains byte-recoverable verbatim — a navigation move, never a loss.

**Acceptance Criteria:**

**Given** the scan (Story 2.1) and L1 assertion (Story 2.2) have passed
**When** the operator evicts the version-provenance
**Then** after eviction the evicted content is byte-recoverable verbatim from the git-versioned archive location (FR-9; NFR-8)
**And** the archive target is an actually git-versioned location — eviction to a non-versioned path is invalid (FR-9; pattern P5)
**And** NO evicted content is deleted; eviction is a move, and the pre-eviction state is reconstructable from git history (FR-9; NFR-8)
**And** **cross-epic dependency (AR-I / ARD §6.1 ★NEW-1):** for any §2 version-row that carries a "canonical = vN" claim, Epic 3's `INDEX.md` (Story 3.1) MUST be in place before / atomically-with this row's eviction, so the canonical-version pointer is navigable and not stranded
**And** the eviction magnitude is **re-derived at slim-time** (the historical "~277KB" figure is downstream of a superseded over-count, and the §2 pointer table has since been relocated; slim-time re-identifies the current largest auto-loaded provenance blocks — ARD §1.3 / AD-12); the success measure is the Epic 1 probe, NOT the byte delta (SM-3 is a reported indicator only)

### Story 2.4: Retain altitude content and position it where attention lands

As the in-session coding agent (beneficiary),
I want the slimmed `CLAUDE.md` to keep the behavior-governing altitude content and position critical content near the window's start and end,
So that the governing rules are in the region I attend to, not buried mid-window under provenance.

**Acceptance Criteria:**

**Given** the evicted prefix (Story 2.3)
**When** the slimmed `CLAUDE.md` is assembled
**Then** the retained set is the altitude content (operating rules + `CLAUDE.md` §11 posture + §12 loop + §13/§14 conventions + the locked operator rules); version-provenance is NOT among it (FR-10)
**And** critical governing content is placed near the prefix start or end, not buried mid-window — verified by inspection of the slimmed file's layout against the lost-in-the-middle trough (NFR-2), NOT by a hard byte/token boundary (DESIGN sets no numeric threshold, so none is invented — FR-10)
**And** the locked operator rules (never-halt, defer-and-continue, prefer-free-ollama, the paid/secret/destructive deny-list) are preserved VERBATIM, not relitigated or weakened by the slim (FR-10; PRD §9.1)
**And** *(SM-C2 backstop)* if the Epic 1 probe later regresses any class, the cause is presumed evicted load-bearing content → restore-and-re-measure, NEVER re-slim more aggressively
**And** **Ratification dependency: ARD §9.1** — the exact retained-altitude-vs-evicted-provenance set is operator-confirmed at slim-time; the set above is the ARD §9.1 / AD-8 recommended default, carried as a default-ratification-pending, NOT baked in as the final cut

---

## Epic 3: Discoverable Canonical Truth — navigate to "canonical = vN" instead of carrying it inline

**Goal.** Make canonical truth discoverable without inlining it where it rots: an `artifact→version` index + a source-of-truth pointer the agent navigates to on demand, plus a standing guardrail that forbids re-bloating the navigation set. This closes the wrong-version-read (D2) hazard without adding eager prefix weight.

**FRs covered:** FR-11, FR-12. **Relevant NFRs:** NFR-1 (one maintained markdown index — the cheapest navigation surface; nothing `@import`-ed). **Drift classes:** cuts D2 (wrong-canonical-artifact). **Metrics:** supports SM-1 by removing a D2 surface.

**Sequencing note.** Story 3.1 (the INDEX + SSOT pointer) is **a precedent of Epic 2's version-row eviction** (AR-I / Story 2.3) — the INDEX is the navigation replacement for the evicted inline versions, so it must exist before those rows leave the prefix. Story 3.2 (the guardrail) depends only on 3.1.

### Story 3.1: Author the un-anchored artifact→version INDEX and the SSOT pointer

As the in-session coding agent (beneficiary),
I want to resolve the canonical version of any design-substrate artifact via an `artifact→version` index and a source-of-truth pointer,
So that I find "canonical = vN" by navigation instead of trusting a stale version inlined in the every-turn prefix.

**Acceptance Criteria:**

**Given** the design-substrate artifact set (no `design-substrate/INDEX.md` exists at HEAD — greenfield)
**When** the operator authors `design-substrate/INDEX.md` + the SSOT pointer
**Then** `INDEX.md` maps each covered artifact to its canonical version (`artifact → vN`), one row per covered artifact (FR-11)
**And** the canonical version of an artifact is resolvable from the index WITHOUT reading an inline version string in `CLAUDE.md` or another prefix document (FR-11)
**And** the MVP index is un-anchored — artifact→version only; it does NOT contain hand-authored `file#header` section anchors (FR-11; a generated section-router is the deferred WS-2b enhancement, Out of Scope)
**And** the SSOT pointer is a single line in the slimmed `CLAUDE.md`'s navigation section pointing to the INDEX — navigated-to, NEVER `@import`-ed (FR-12)
**And** the INDEX is maintained by regenerate-and-commit (the existing `roadmap.html` convention), not hand-edit-and-drift (ARD §5.2)
**And** **cross-epic dependency (AR-I):** this story precedes / is atomic-with Epic 2 Story 2.3's eviction of the §2 version-rows it replaces (the 1:1 navigation hand-off)
**And** **Ratification dependency: ARD §9.6.5** — the exact INDEX coverage set is operator-pending; the default per §9.6.5 is "cover exactly the §2-version-carried artifacts the slim evicts (specs + plans + CXA + ADRs with a 'canonical = vN' claim)" — carried as a default, ratification-pending

### Story 3.2: Enforce the navigation-set guardrail (forbid the four inversions)

As the operator,
I want a standing rule constraining the navigation set to established anchors and forbidding the prefix-rebloating / stale-link inversions,
So that the navigation surface cannot grow back into the bloat this layer exists to cut.

**Acceptance Criteria:**

**Given** the navigation set defined by Story 3.1
**When** the navigation-set guardrail is applied (as an authoring-discipline rule)
**Then** `GC.md`, `ROUTING.md`, and `CATALOG.md` are NOT invented as navigation conventions (FR-12; refusal R8)
**And** a static `WORKFLOWS.md` is NOT authored — loop procedures stay as just-in-time skills, not an eager prefix document (FR-12; permanently refused, R8)
**And** NO WS-2 navigation anchor is `@import`-ed into `CLAUDE.md` (it would become eager prefix weight — the inversion to prevent; FR-12)
**And** hand-authored `#section` anchors are NOT introduced at the MVP floor (a stale-link/D4 surface; FR-12)
**And** the guardrail is a standing authoring rule (and, when the deferred G-LINK goes live, a link-integrity check) — NOT a one-time cleanup (ARD AD-11)
**And** **Ratification dependency: ARD §9.2** — the namable established anchors are operator-pending; the default per §9.2 / AD-10 is "`ARCHITECTURE.md` + `HOOKS.md` routing (content deferred to WS-2b); `WORKFLOWS.md` permanently refused" — carried as a default, ratification-pending, with new anchors added only on an observed orientation gap (the WS-2b trigger)

---

## Epic 4: Trustworthy Durable Memory — non-lossy compaction with a health glance

**Goal.** Make `MEMORY.md` compaction enforced and non-lossy: keep/retire lessons by connectivity (wiki-link in-degree), mark every retirement as superseded (never silent-drop), surface exactly three plain integers of memory health at session boundary, and perform a finite one-time hygiene write of the two already-promised dangling lessons. The motivating incident — an ad-hoc lossy compaction silently dropped ~75 index entries (≈120→45) with no mark and no rollback, itself a live D4 incident — is exactly what this enforced contract replaces.

**FRs covered:** FR-13, FR-14, FR-15, FR-16. **Relevant NFRs:** NFR-3 (non-lossiness), NFR-5 (observability at boundary), NFR-1 (grep-by-eye, three integers — no engine/dashboard/score). **Drift classes:** cuts D1 (stale-rule) + D4 (memory-pollution). **Metrics:** SM-2 (memory non-lossiness), SM-4 (memory-health observability).

**Ownership note (ARD §3.7).** Epic 4 (C-MEM) owns the *at-rest* retention rule + the ARCHIVE move + the `superseded_by` schema; Epic 6 (C-STORE) owns the store's git/atomic/OCC substrate that makes archived bodies recoverable. The seam is fixed — no file-churn overlap. Stories within the epic depend only on previous stories.

### Story 4.1: Compact MEMORY.md by degree-keyed selection (KEEP-HOT / KEEP-LINKED / ARCHIVE)

As the operator,
I want compaction to keep or retire each lesson by its wiki-link in-degree across three distinguishable tiers,
So that a hub lesson's value (its connectivity) decides its fate — not its filename prefix or category — and the pin-set tracks a moving count instead of a frozen list.

**Acceptance Criteria:**

**Given** the `MEMORY.md` index and the durable note set
**When** the operator runs degree-keyed compaction
**Then** selection is keyed on wiki-link in-degree, NOT on prefix, filename, or category (FR-13; pattern P1)
**And** a note with in-degree ≥5 is retained KEEP-HOT with its full description; a 1–4-inbound note is retained KEEP-LINKED (compaction-eligible, not archived); a zero-inbound note is moved to ARCHIVE with its index line dropped (body → `memory/archive/`, recoverable on demand) — all three tiers distinguishable from the in-degree alone (a binary keep/archive split that collapses the KEEP-LINKED middle tier does NOT satisfy this rule) (FR-13)
**And** the pin-set is re-derived against the current count at slim-time — thresholds operator-tunable against a moving number, NOT a frozen list (FR-13; AR-H: the top hub grew 65→83 / MEMORY.md grew since the arc-open snapshot — re-derive, don't freeze)
**And** the KEEP-HOT hubs are the notes Epic 2 Story 2.4 keeps positioned in the re-attended prefix (the ARD §3.7 C2↔C3 cut)
**And** in-degree is read by eye with `grep | wc -l` — NO connectivity-recompute engine is built (FR-13 feature-NFR; refusal R5; NFR-1)

### Story 4.2: Retire a lesson with a bi-temporal supersede-mark (never silent-drop)

As the operator,
I want every retired lesson marked superseded (`valid_until` + `superseded_by`) with its body archived, instead of silently dropped,
So that compaction is non-lossy and recoverable by construction — the 06:27 silent-lossy-drop incident cannot recur.

**Acceptance Criteria:**

**Given** a lesson selected for retirement (ARCHIVE tier, Story 4.1)
**When** compaction retires it
**Then** the lesson is recorded as superseded — `valid_until: <ISO-8601 datetime>` is set and `superseded_by: "[[<replacement-slug>]]"` points to what supersedes it (a frontmatter breadcrumb) — and the body is moved to `memory/archive/`; it is NOT removed without a mark (FR-14; §4.1 schema)
**And** a superseded lesson's body is recoverable — via the archive-move (PRESENT at HEAD, git-independent) at HEAD, and additionally via the store snapshot once Epic 6 establishes `memory/.git` (FR-14 / FR-20; the snapshot is an X-min enhancement, ARD ★NEW-3)
**And** NO compaction path deletes a lesson with no breadcrumb — the silent-lossy-drop that motivated this feature is structurally prevented (FR-14; NFR-3; pattern P2; SM-2)
**And** the supersede-mark is a Tier-1 frontmatter breadcrumb — NOT a Tier-5 hash-chained ledger write (proportionate; AD-13; NFR-1)
**And** retirement is always `set valid_until + set superseded_by + move body to memory/archive/` — the field names are used verbatim, no synonym (ARD §5.2; PRD §3 Glossary)

### Story 4.3: Emit the three-integer SessionEnd health-line

As the operator,
I want exactly three grep-derived integers of memory health at session boundary,
So that creeping rot and the deferred-tail triggers are a glance — not an autopsy, not a dashboard, not a rot-score.

**Acceptance Criteria:**

**Given** the durable note set at session boundary
**When** the SessionEnd report is emitted (extending the existing `session-end-cleanup.sh` MEMORY.md-cap block at ~lines 49-56)
**Then** the health-line emits exactly three integers — `notes-superseded`, `notes-untouched-beyond-N-days`, and `patterns-unwritten-with-≥4-refs` (the canonical FR-15 field names, verbatim) — never a fourth (FR-15; NFR-5; pattern P4)
**And** it is NOT a rot-score, an embedding-drift/MMD/cosine metric, or a dashboard (FR-15; refusal R3; NFR-5)
**And** the line is emitted at session boundary only — it is NOT a mid-session runtime surface (FR-15; NFR-5)
**And** `notes-superseded` is derived by `grep -l 'valid_until:' memory/*.md | wc -l`; `notes-untouched-beyond-N-days` by mtime; `patterns-unwritten-with-≥4-refs` by counting dangling `[[ ]]` slugs with in-degree ≥4 and no note file (ARD §4.5)
**And** the `patterns-unwritten-with-≥4-refs` integer is the signal that discharges `INCOMPLETE-on-D4` (Epic 1 Story 1.4 / FR-4) and the standing observability that keeps the deferred consolidation trigger from being silent
**And** **Ratification dependency: ARD §9.3(a) + §9.6.4** — who sets the "unhealthy" threshold on each integer, the mechanism that ensures the counts are acted on rather than scrolled past, and the value of N (untouched-beyond-N-days) are operator-pending; defaults per §9.3 / §9.6.4 are "the line REPORTS the numbers (sets no thresholds); the operator sets thresholds at the existing SessionEnd/roadmap review cadence (no new enforcement built — proportionality); N = 90 days (operator-tunable)" — carried as defaults, ratification-pending

### Story 4.4: Perform the finite one-time hygiene write of the two dangling ≥4-ref lessons

As the operator,
I want a finite one-time write of the two high-reference pattern lessons that are already promised (≥4 inbound) but have no note file,
So that durable memory is brought into a consistent state and the two standing `patterns-unwritten-with-≥4-refs` health-line counts clear.

**Acceptance Criteria:**

**Given** the two currently-dangling ≥4-ref patterns at HEAD — `plan-revision-against-not-yet-built-substrate` (≈6 inbound refs) and `strike-revision-on-refined-second-tier-reason` (≈5 inbound refs), both promised but with no note file
**When** the operator performs the one-time hygiene write
**Then** the two named pattern notes are written into the durable memory (semantic tier) as a finite one-time action (FR-16)
**And** this is a one-time hygiene write, NOT the recurring consolidation pass — the recurring consolidation mechanism is explicitly deferred (Out of Scope; PRD §6.2; pattern P3) and is NOT stood up here
**And** after the write, the `patterns-unwritten-with-≥4-refs` health-line integer reflects the two cleared danglers (the exact reference counts re-derive at write-time per AR-H, since the count moves)
**And** the story scope is exactly the two named notes — it does NOT scan-and-promote the broader note set (that would be the deferred recurring pass)

---

## Epic 5: Leading-Indicator Budget Guardrail — keep the prefix lean at review-time, never in-session

**Goal.** Ship the only blocking gate in the MVP — a review-time `--check` over the effective auto-loaded context (the deterministic byte-sum of `CLAUDE.md` + its `@import`-closure + `MEMORY.md`), warn-then-fail with an explicit waiver, modeled on the existing `substitution_ledger.py --check`. It runs strictly at CI/review time so it composes with never-halt. **It is a leading indicator, never the success gate** (PRD §4.5; SM-3 / SM-C1).

> **Constraint discipline for this epic.** The guardrail *legitimately measures a byte-sum* as its mechanism — its ACs correctly describe `bytes(CLAUDE.md)+@import-closure+bytes(MEMORY.md)`, warn-then-fail, waiver, review-time-only. What is forbidden is any AC whose *success condition* is "byte ≤ cap" or "file smaller." A green G1 is a reported indicator; the layer's win is the Epic 1 WS-0 probe (SM-C1). Story 5.1 carries the explicit false-green guard AC.

**FRs covered:** FR-17, FR-18, FR-19. **Relevant NFRs:** NFR-6 (never-halt composition), NFR-1 (reuses the existing `--check` pattern; zero new framework). **Drift classes:** indirectly supports SM-1 by keeping the prefix lean (NFR-2). **Metrics:** SM-3 (reported leading indicator), SM-C1 (the false-green counter-metric).

**Sequencing note.** Per ARD §6.1: G1 ships in warn-mode first (Story 5.2 warn half), then flips to hard-fail once the post-slim baseline is clean (Story 5.2 flip). Stories depend only on previous stories; the warn→fail flip depends on Epic 2's slim having landed.

### Story 5.1: Compute and check the effective-auto-loaded-context byte-sum

As the operator,
I want a `--check` that computes the effective auto-loaded context as a deterministic byte-sum and validates it against a budget,
So that I have a cheap, auditable, reproducible measure that the slim took and that provenance is not creeping back.

**Acceptance Criteria:**

**Given** the harness's root auto-loaded set
**When** the `--check` runs
**Then** the measured input is exactly `bytes(CLAUDE.md) + bytes(@import-closure) + bytes(MEMORY.md)` — a byte-sum, NOT an attention-weighted or token-estimated figure (FR-17)
**And** the `@import`-closure follows only `@import`s reachable from the *root* `CLAUDE.md` (deduped, transitive); it does NOT chase `@import`s originating inside the scoped-out operator-global file (so `@RTK.md`, reached only via `~/.claude/CLAUDE.md`, is NOT counted) — two implementers compute the identical byte-sum (FR-17; ARD §4.4 closure determinism)
**And** the check is a `--check` invocation returning pass/fail against the configured budget, modeled on `tools/substitution_ledger.py --check` (zero new framework; AD-4)
**And** the check is byte-budget only — it does NOT validate link integrity (link-integrity is the deferred G-LINK; FR-17; Out of Scope)
**And** *(false-green guard, SM-C1)* a green `--check` is read as a reported leading indicator ONLY — it is NEVER read as "the layer succeeded"; the verdict is the Epic 1 WS-0 matrix (pattern P8; refusal R6)
**And** **Ratification dependency: ARD §9.5.2** — the G1 input-scope boundary is operator-pending; the recorded decision (AD-16) is "measure the root auto-loaded set; scope OUT operator-global `~/.claude/CLAUDE.md` + `@RTK.md` and the per-axis `harness-*/CLAUDE.md` (the latter populated at 131,435 B but loading additively within their own subtree → a separate per-axis F4 application, NOT a widening of root G1)" — carried as the recorded decision, ratification-asked at §9.5.2, NOT silently widened
**And** **Ratification dependency: ARD §9.6.4** — the budget integer and the archive location are operator-pending; defaults per §9.6.4 are "budget = the post-slim clean baseline byte-sum + a small margin (derived, not pre-chosen); archive = a git-versioned `design-substrate/`-adjacent history doc" — carried as derivation-rules, ratification-pending

### Story 5.2: Run in warn-then-fail mode with an explicit waiver path

As the operator,
I want the guardrail to warn before the slimmed baseline is clean and hard-fail after, always with an explicit waiver,
So that a justified breach is never blocked into unreadable compression and the gate gets teeth only once the slim has actually landed.

**Acceptance Criteria:**

**Given** the `--check` (Story 5.1) and the post-slim baseline state
**When** a budget breach occurs
**Then** before the baseline is clean, a breach WARNS but does not fail the check (exit 0); after the baseline is clean, a breach FAILS it (exit 1) (FR-18)
**And** an explicit waiver path (`--waiver <reason>`) lets a justified breach pass without removing the gate (FR-18)
**And** the gate NEVER forces compression that would make the context unreadable — the waiver is the escape for the rare justified case (FR-18)
**And** the restore-and-re-measure recovery path (Epic 1 Story 1.7 / SM-C2) is NOT blocked by a G1 hard-fail — a restore PR uses the `--waiver`, because byte-clean is a proxy the WS-0 `SOUND` verdict licenses, not an independent gate (ARD §6.2 C1-CONCERN-1 / Seam E; never-halt, NFR-6)
**And** **Ratification dependency: ARD §9.4** — the precise "clean baseline" definition the warn→hard-fail flip keys on is operator-pending; the default per §9.4 / AD-16 is "the effective byte-sum is at or below the configured budget after the slim, with the provenance region not creeping back (the git-edit-cadence proxy stable)" — carried as a default, ratification-pending

### Story 5.3: Run only at review/CI time (never-halt composition)

As the operator,
I want the guardrail to run only at code-review/CI time and never as an in-session runtime blocker,
So that it composes with the never-halt discipline and no live coding session is ever halted by a byte-budget breach.

**Acceptance Criteria:**

**Given** the guardrail wired into the toolchain
**When** it executes
**Then** the check runs at code-review/CI time — the same tier as `substitution_ledger --check` + `x-al-3-guard.yml` — and does NOT execute as an in-loop session-runtime step (FR-19; NFR-6; pattern P6)
**And** NO live coding session is halted by the guardrail (never-halt binds runtime; this gate is not a runtime surface) (FR-19)
**And** the guardrail adds one CI step — NO daemon, NO runtime surface, NO mid-session blocker (NFR-1; the mid-session budget surface is the deferred WS-5, Out of Scope)

---

## Epic 6: Recoverable, Concurrency-Safe Memory Store — parallel sessions cannot clobber each other

**Goal.** Make the durable, out-of-worktree memory store recoverable and safe under the parallel multi-session (decentralized-handoff) workflow, *without* full locking: snapshot/version it with git as the rollback boundary, make writes atomic, detect stale-base writes (OCC), and name the reinject-pointer-resolvability floor. Because the topology is N independent worktree sessions with no lead writer, serialization lives at the store (OCC), not at a topology lead.

> **Boundary discipline for this epic (X-min IN / X-full OUT).** This epic builds **X-min** — OCC detect-and-refuse, atomic writes, git-as-state, the absence-guard reinject floor. It does **NOT** build **X-full** (full write-locking — deferred to an observed concurrent-write race) and does **NOT** build resolution-validation of a present-but-drifted reinject target (deferred to G-LINK). Drifting into the deferred half is silent scope-creep and is explicitly forbidden.

**FRs covered:** FR-20, FR-21, FR-22. **Relevant NFRs:** NFR-4 (recoverability + concurrency-safety), NFR-3 (snapshot recoverability of archived bodies, with Epic 4), NFR-6 (the reinject floor continues-on-absence, never aborts). **Drift classes:** cuts D4 (a bad write entering the store) + supports D5 (bad-resumption) recovery floor. **Metrics:** SM-2 (recovery of a superseded body from a snapshot).

**Lane note (ARD §9.5.1 / NFR-8).** The store's *first commit / repo creation* and the `CLAUDE.md §12.5.1` provenance-line correction are **execution-arc work via the X-AL-3 escape-hatch** — they are NOT performed by authoring artifacts (this epics doc, the ARD, the PRD all describe; the execution arc performs). Stories within the epic depend only on previous stories.

### Story 6.1: Snapshot/version the store with git as the rollback boundary + atomic writes

As the operator,
I want the out-of-worktree memory store snapshot/versioned with git and every write made atomic,
So that a prior store state is recoverable and no partially-written store state is ever observable.

**Acceptance Criteria:**

**Given** the memory store at `~/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` — which is **NOT its own git repo at HEAD** (no `memory/.git`; `rev-parse --show-toplevel` resolves to an ancestor `~/` repo; commit count 0)
**When** X-min establishes store versioning
**Then** the store is versioned such that a prior state is recoverable, with git as the rollback boundary (FR-20)
**And** X-min's first concrete step is **"create a git repo AT the store (`memory/.git`) + first snapshot"** — NOT merely "first commit on an already-existing repo" (FR-20; AR-F / ARD §9.5.1 / AD-17)
**And** a write to the store either fully applies or does not apply — no partially-written store state is observable (atomic temp-then-rename) (FR-20; ARD §4.6)
**And** a superseded lesson's archived body (Epic 4 Story 4.2) is recoverable from a store snapshot (FR-20; SM-2; NFR-3)
**And** the store's first repo-creation/commit is performed by the **execution arc** via the X-AL-3 escape-hatch — NOT by any authoring artifact (lane discipline, NFR-8; the store is outside the planning tree)
**And** **Ratification dependency: ARD §9.5.1** — the sharpened framing is operator-pending; confirm "the `CLAUDE.md §12.5.1` provenance-line stays fix-when-versioned (execution-arc, not this doc's to perform); X-min starts from create-the-repo, not first-commit-on-existing" — carried as the ARD §9.5.1 recommended framing, ratification-asked, NOT silently absorbed

### Story 6.2: Detect stale-base writes (optimistic concurrency) at the store

As the operator,
I want the store to detect when a write is based on a stale read,
So that two independent worktree sessions writing concurrently cannot silently clobber each other — without paying for full locking.

**Acceptance Criteria:**

**Given** two independent worktree sessions reading and writing the store
**When** a write whose base read is stale is attempted
**Then** the stale-base write is DETECTED rather than silently overwriting a newer state (FR-21)
**And** serialization is enforced at the store (OCC: capture the store's git rev as a base token at read-time; compare at write-time) — NOT at a topology lead agent (the decentralized-handoff topology has no single writer) (FR-21; ARD §4.6)
**And** the OCC `base_rev` MUST resolve against the store-local `memory/.git` (Story 6.1), NEVER the ancestor `~/` repo — else every unrelated home-dir commit advances `base_rev` and produces cry-wolf STALE-BASE false-positives (ARD §4.6 / ★NEW-3)
**And** full write-locking is NOT part of this story — it is deferred to X-full on an observed concurrent-write race (FR-21; Out of Scope)
**And** on STALE-BASE the floor is a one-shot retry on a fresh base, then surface to the operator (a full 3-way merge is deferred to X-full; better than silent-clobber; not a halt) (ARD §4.6 C9-CONCERN)
**And** **Ratification dependency: ARD §9.6.2** — the X-full locking-graduation watcher is operator-pending; the default per §9.6.2 is "the OCC stale-base refusal event IS the observed-race signal — a refused write is the trigger — reviewed by the operator at SessionEnd; no dedicated race-monitor is built" — carried as a default, ratification-pending

### Story 6.3: Name the reinject-pointer-resolvability floor (absence-guard, graceful degrade)

As the in-session coding agent (beneficiary, on resume),
I want the recovery path to degrade gracefully when a re-injected pointer's target file is missing,
So that resumption never hard-errors or proceeds on a phantom target — and the quiet present-but-drifted case is honestly deferred, not silently claimed solved.

**Acceptance Criteria:**

**Given** the reinject floor at `postcompact-reinject.sh:28-32` (the `CK`/`CKNOTE` `&&`-append absence-guard, PRESENT at HEAD)
**When** a re-injected pointer's target snapshot is missing
**Then** the recovery path degrades gracefully — the appended note is simply left empty and execution CONTINUES; it does NOT hard-error and does NOT proceed on a phantom target (FR-22; the floor is present at HEAD; only the richer resolve-and-reinject body is to-be-authored, modeled on the same continue-on-absence shape)
**And** the resolution-validation of a present-but-wrong or cross-store-drifted target is NOT part of the MVP floor — it rides the deferred G-LINK `--check` when live, and explicitly does NOT ride the byte-budget guardrail (byte-budget ≠ link-integrity) (FR-22; Out of Scope)
**And** the recovery-degrade path leaves a grep-able `hook_emit` breadcrumb so a silent degrade is watchable via the existing health-line — NO fourth integer, NO new schema (the exactly-three rule holds, R3) (ARD §4.7 C9-N-C9-3)
**And** the reinject pointer's firing-site is the already-wired PostCompact / SessionStart(compact) hook — naming it keeps the floor from drifting un-anchored (ARD §4.7 C9-N-C9-2)
**And** **Ratification dependency: ARD §9.3(b)** — how present-but-drifted resume-target validation is triggered into existence, and how the operator learns of a quiet resume failure that never surfaces as an error, are operator-pending; the default per §9.3 is "the MVP floor is the `[ -f ]` absence-guard; resolution-validation defers to G-LINK on its trigger, never to G1 — the held tension is accepted explicitly and watched via the health-line breadcrumb" — carried as a default, ratification-pending

---

## Out of Scope (deferred tail + principled refusals — NOT decomposed into stories)

*Proportionality (NFR-1) is binding: the deferred tail is large on purpose and the refusals are permanent. These are listed, NEVER decomposed into stories. Any story for the items below would be the governance-bloat this layer exists to cut.*

### A. Deferred tail — returns only on a named observed trigger (PRD §6.2 / ARD §8)

| Deferred item | Named trigger to revisit |
|---|---|
| **G-LINK — link-integrity `--check`** (validates `[[wiki]]` / `[md](slug)` / cross-store refs / generated section anchors / the reinject pointer / `superseded_by` targets all resolve) — and OWNS the present-but-drifted resume-target resolution-validation (FR-22 deferred half) | WS-2a generated section-routing ships, OR `superseded_by` becomes machine-emitted, OR an observed D4-via-dangling-reference at the WS-0 probe |
| **Recurring consolidation pass** (synchronous SessionEnd write-event promoting lessons into the semantic tier; no daemon) — distinct from FR-16's finite one-time write | the `patterns-unwritten-with-≥4-refs` health-line count rises above zero (observed D4) |
| **WS-2b — top-level orientation docs** (`ARCHITECTURE.md` / `HOOKS.md` content; generated `file#header` section-routing) | an observed fresh-context orientation gap, OR the hook system next substantially changed, OR a wrong-section-citation D2 incident |
| **WS-3b** — `.harness/` archival policy + checkpoint-store asymmetry | ledger/checkpoint growth causing an observed navigation or cost problem |
| **WS-4 G2 / G3 / G4** — clearance-marker schema / ledger-shape / freshness-teeth | an observed malformed-marker / ledger-drift / stale-roadmap incident |
| **Per-axis G1 scope** (a separate per-axis F4 application to each populated `harness-*/CLAUDE.md`) — NOT a widening of root G1 | axis `CLAUDE.md` files populated (condition ALREADY met at HEAD: 131,435 B) → re-evaluate as a per-axis F4 application, never widen root G1 |
| **WS-5** — mid-session budget surface + dashboard health states | G1 (CI-time) + the 3-integer health-line prove insufficient and mid-session blindness causes observed drift |
| **WS-6 6b** — the D14 recovery build | the WS-0 probe shows D5 (bad-resumption) drift after the slim (the named §6.2 regression trigger) |
| **X-full** — memory-store serialization / full write-locking | an observed concurrent-write race (the X-min OCC detects-and-refuses until then) |
| **Tier-2 ICM structural adoption** (numbered `stages/NN-*/` folders + `CONTEXT.md` Inputs/Process/Outputs contracts) | an explicit operator scope-reopening (operator-ratified NON-GOAL for this layer, 2026-06-05; a design-revision, never a silent add) |

### B. Principled refusals — standing "we are NOT building this" (PRD §5 / ARD §2.8 R1–R9)

- **R1 — No automated eval harness.** The gate is a human reading real sessions.
- **R2 — No model-as-judge.** D1–D6 are binary + human-graded.
- **R3 — No continuous health-score / rot-score** (embedding-drift / MMD / cosine / staleness-decay). The health surface stays exactly three plain integers.
- **R4 — No background consolidation daemon on a fixed cadence.** Consolidation, when it returns, is a synchronous SessionEnd write-event on an observed trigger.
- **R5 — No connectivity-recompute engine.** In-degree is read by eye with a grep.
- **R6 — No byte-count as the success gate.** Byte≤cap is a reported leading indicator only (SM-3), never the verdict.
- **R7 — No synthetic test corpus / forced coverage.** The probe reuses real sessions and reports honestly what was not exercised.
- **R8 — No invented navigation conventions** (`GC.md` / `ROUTING.md` / `CATALOG.md`), no authored `WORKFLOWS.md`, no hand-authored `#section` anchors, no `@import`-ing a nav anchor into `CLAUDE.md`.
- **R9 — Not becoming a platform.** Self-governance for this harness's specific files — not a portable framework, library, product, or live monitoring console.

### C. Mandate-2 reusable framework (ARD §7) — a TEMPLATE, not buildable MVP scope

The ARD §7 reusable per-layer framework (F1 doc-architecture / F2 INDEX-navigation / F3 drift-taxonomy / F4 budget-guardrail / F5 memory-discipline) is **explicitly a template that "adds NOTHING beyond §4"** — a way of re-using Epics 1–6's patterns on the *other* harness layers, each on its own per-layer trigger. It is NOT a 7th epic and NOT buildable MVP work; it is recorded here so it is not mistaken for in-scope decomposition.

---

## Ratification Dependencies — the batched operator-decision agenda (ARD §9)

*Per the X-AL-3 no-silent-absorption discipline: every story above that depends on a decision still pending operator ratification at ARD §9 carries a `Ratification dependency` flag, collected here as the operator's batched decision set. The ARD's recommended default is cited on each story as a default, ratification-pending — NEVER baked in as settled. These are the decisions to ratify before (or as) the dependent stories are built. (ARD §9.5.3 / AR-H — MEMORY.md growth — is explicitly "No ratification needed" and is NOT listed here; it is recorded as confirmation only.)*

| # | ARD §9 item | Decision pending | Recommended default (ratification-pending) | Dependent story |
|---|---|---|---|---|
| 1 | **§9.1** [PRD-assumption / FR-10] | The exact retained-altitude-vs-evicted-provenance set at slim-time | Operating rules + `CLAUDE.md` §11/§12/§13/§14 + locked rules = retained; the §2 version-provenance = evicted (AD-8) | **2.4** |
| 2 | **§9.2** [PRD-assumption / FR-12] | The namable established navigation anchors | `ARCHITECTURE.md` + `HOOKS.md` routing (content deferred to WS-2b); `WORKFLOWS.md` permanently refused (AD-10) | **3.2** |
| 3 | **§9.3(a)** [PRD Q3 / FR-15] | Who sets the "unhealthy" health-count thresholds + the acted-on mechanism | Line REPORTS the numbers; operator sets thresholds at the existing SessionEnd/roadmap review cadence; no new enforcement built | **4.3** |
| 4 | **§9.3(b)** [PRD Q5 / FR-22] | How present-but-drifted resume-target validation is triggered + how the operator learns of a quiet resume failure | MVP floor = `[ -f ]` absence-guard; resolution-validation defers to G-LINK (never G1); held tension accepted + watched via the health-line breadcrumb | **6.3** |
| 5 | **§9.4** [PRD Q7 / FR-18] | The precise "clean baseline" definition for the G1 warn→hard-fail flip | At/below the configured budget after the slim, with the provenance region not creeping back (git-edit-cadence proxy stable) (AD-16) | **5.2** |
| 6 | **§9.5.1** [corpus-vs-HEAD / FR-20] | The sharpened store-not-a-repo framing | `§12.5.1` line stays fix-when-versioned (execution-arc); X-min starts from create-the-repo, not first-commit-on-existing (AD-17) | **6.1** |
| 7 | **§9.5.2** [corpus-vs-HEAD / FR-17] | The G1 input-scope boundary | Root auto-loaded set only; scope OUT operator-global config + per-axis files (per-axis → separate F4 application, never widen root G1) (AD-16) | **5.1** |
| 8 | **§9.6.1** [PRD Q1 / FR-2] | Credible session-count floor + named representative workflow-class set (arm-comparability method is RESOLVED: the operator-ratified REPORT form, ARD §4.2 — not re-opened) | ~15–25 real sessions; workflow-class set from the `[[use-the-product-probe-pattern]]` corpus; do NOT pin a hard floor (report coverage, let `INCOMPLETE` carry the honesty) | **1.2** |
| 9 | **§9.6.2** [PRD Q2 / FR-21] | The X-full locking-graduation watcher | The OCC stale-base refusal event IS the observed-race signal, reviewed at SessionEnd; no dedicated race-monitor built | **6.2** |
| 10 | **§9.6.3** [PRD Q6 / FR-6] | The waiver author/owner + record-location + the `SOUND-WAIVED` distinct-verdict sharpening | Operator authors + owns; recorded in the WS-0 grading worksheet; adopt `SOUND-WAIVED`; the waiver names which reason fired | **1.6** |
| 11 | **§9.6.4** [corpus-silent / FR-17, FR-9, FR-15] | The G1 budget integer + the archive location + the health-line N-days | Budget = post-slim clean baseline + small margin (derived); archive = git-versioned `design-substrate/`-adjacent; N = 90 days (tunable) | **5.1, 4.3** |
| 12 | **§9.6.5** [corpus-silent / FR-11] | The `INDEX.md` coverage set | Cover exactly the §2-version-carried artifacts the slim evicts (specs + plans + CXA + ADRs with a "canonical = vN" claim) | **3.1** |

**12 ratification dependencies span 11 of the 23 stories.** None blocks the *build start* — ARD §10.4: step 0 (Epic 1 Story 1.1/1.2, the WS-0 baseline) can begin immediately; each ratification item must be resolved with the operator before its dependent component is built. The operator decides; this list is the agenda, not a set of pre-made decisions.

---

## Assumptions & Auto-Continued Gates

*This deliverable was produced in an autonomous background session. The skill's `[C]` continue menus (Step 1 §10, Step 2 §8, Step 3 §7, Step 4) and the `bmad-advanced-elicitation` `[A]` / party-mode `[P]` options were not interactively presented to the operator. At each gate the reasonable product-strategist decision was made, recorded here, and execution continued. The `bmad-advanced-elicitation` skill exists but interactive elicitation is skipped in autonomous mode; `bmad-help` and `bmad-party-mode` are not installed (skipped gracefully). `persistent_facts` referenced `**/project-context.md` — none exists in this repo (noted gracefully, continued).*

1. **Step 1 `[C]` gate (requirements confirmation) — auto-continued.** Extracted all 22 FRs (verbatim-faithful from PRD §4), all 8 NFRs (PRD §8), the architecture-derived Additional Requirements (ARD §2/§3/§6/§9.5), and correctly recorded UX as N/A (no UX doc; no UX-DRs fabricated). Judged complete and faithful; proceeded to Step 2 without operator confirmation.
2. **Step 2 `[A]`/`[P]`/`[C]` gate (epic structure approval) — auto-continued to `[C]`.** Adopted 6 epics, one per PRD §4 feature / DESIGN workstream / ARD component, value-titled (not "WS-N"). File-churn was assessed: the only shared surface (the memory store, Epics 4 + 6) splits cleanly on the ARD §3.7 C2↔C3 ownership seam → consolidation considered and rejected with rationale. Skipped `[A]` advanced-elicitation (interactive) and `[P]` party-mode (not installed). Proceeded without operator approval.
3. **No 7th epic for the ARD §7 reusable framework — decided.** The §7 framework is explicitly a template that "adds nothing beyond §4." Decomposing it into stories would be over-decomposition of non-MVP scope (a proportionality violation). Recorded under Out of Scope §C instead.
4. **The WS-0 bracket (Arm A foundational, Arm B closing) — structural decision.** BMad's within-epic "no forward dependency" rule strains legitimately here: the gate measures the layer it brackets. Resolved by keeping WS-0 as one epic delivering the standalone *instrument* (Stories 1.1–1.6), with Arm-B/verdict (Story 1.7) as the closing action carrying an explicit, named cross-epic dependency on Epics 2–6 — named, not faked as independence.
5. **Story granularity ≈ 1 per FR (23 stories / 22 FRs) — decided.** The FRs are already atomic and story-sized; the PRD's per-FR "Consequences (testable)" are essentially pre-written, source-faithful ACs and were mined directly. The one split beyond 1:1 is Epic 1's Story 1.7 (Arm-B capture + close verdict), carved out from the instrument stories because it is the cross-epic closing action with a distinct dependency profile.
6. **Story-count vs the ARD's "first implementation step" — reconciled.** ARD §2.0 says there is NO greenfield starter; the first step is WS-0 baseline capture. So Epic 1 Story 1.1 = define the D1–D6 taxonomy + verdict function (NOT a scaffold/project-init story); recorded as Additional Requirement AR-A and honored in the Epic 1 sequencing.
7. **Verbatim verdict strings + field names — discipline applied.** Used the literal `SOUND` / `SOUND-WAIVED` / `SOUND-COMPOSITION-CONFOUNDED` / `INCOMPLETE-on-D4` / `INCOMPLETE-on-D6` / `INCOMPLETE-on-D4-and-D6` and `valid_until` / `superseded_by` / the three canonical health-integer names throughout, because ARD §5.2 makes synonym-introduction a discipline violation.
8. **§9 default-absorption guard (the task's named worst failure mode) — actively held.** Every story whose AC depends on an unratified ARD §9 decision carries a `Ratification dependency` flag and cites the ARD default *as a default, ratification-pending* — never as settled. ARD §9.5.3 (MEMORY.md growth) was correctly NOT flagged (the ARD itself says "No ratification needed"); it is recorded as confirmation under AR-H.
9. **Step 3 `[C]` gate (all stories complete) — auto-continued.** All 6 epics processed in sequence with full Given/When/Then ACs tied to D1–D6 / SM metrics; no per-epic operator confirmation between epics (autonomous mode). Proceeded to Step 4.
10. **Empirical figures cited as snapshot-anchored, re-derive-at-slim-time.** The byte/count figures (131,435 B axis files; ~15,995 B MEMORY.md; 183 notes; the ≈6/≈5 dangling-ref counts; the historical "~277KB"/"~342KB"/"~85.7K-tok" being superseded over-counts) are cited as the ARD's 2026-06-08 Stage-D-corrected snapshot and flagged to re-derive at slim-time (AD-12), not frozen.
