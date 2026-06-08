---
stepsCompleted: [1, 2, 3, 4, 5, 6]
verdict: 'READY-WITH-CONDITIONS (build may start at step 0 / Arm-A baseline immediately; the 12 ARD §9 ratifications are the named conditions, each resolved before its dependent component builds)'
assessor: 'bmad-check-implementation-readiness (genuine skill invocation — expert PM, requirements-traceability) | autonomous background session'
runMode: 'autonomous (background — [C] continue gates auto-resolved + documented in §Assumptions & Auto-Continued Gates)'
artifactUnderReview: '.harness/01-planning/01-harness-planning/01-context-memory-layer-planning/05-epics-and-stories/epics.md (6 epics / 23 stories)'
inputsRead:
  - '02-prd/.../prd.md (FR-1..FR-22, NFR-1..NFR-8, SM-1..SM-4, SM-C1..SM-C4, §5 refusals, §6.2 deferred tail, §11 open Qs, §3 Glossary)'
  - '02-prd/.../addendum.md (mechanism + transport + schemas)'
  - '04-architecture/architecture.md (ARD — AD-0..AD-19, §9 ratification register)'
postureNote: 'Independent / adversarial re-derivation — FR/NFR coverage re-built from the PRD text, NOT taken from the epics own self-claim (correlated-blindness guard).'
date: '2026-06-08'
project_name: 'Context & Memory Layer (Harness Self-Governance)'
user_name: 'Robert'
---

# Implementation Readiness Assessment Report

**Date:** 2026-06-08
**Project:** Context & Memory Layer (Harness Self-Governance) — arhugula-v2
**Assessor:** `bmad-check-implementation-readiness` (expert PM, requirements-traceability)
**Artifact under review:** `05-epics-and-stories/epics.md` — 6 epics, 23 stories
**Run mode:** Autonomous background session (continue-gates auto-resolved; see final section)

> **Independence posture (correlated-blindness guard).** The `epics.md` under review was authored by the same lineage that runs this check. This report therefore **re-derives** the full FR-1..FR-22 / NFR-1..NFR-8 requirement set **from the PRD itself** and re-runs the ARD §9 ratification register against the story bodies **independently** — it does NOT accept the epics' own "FR Coverage Map" / "all FR/NFR mapped" / "12 ratification dependencies" self-claims at face value. Where the self-claim is verified true, that is stated as a confirmed finding, not assumed.

---

## Document Discovery (Step 1)

Inputs supplied explicitly (the skill's auto-discovery globs do not reach this nested feature-planning tree; explicit paths used).

| Document type | Status | Path (under `01-context-memory-layer-planning/`) | Notes |
|---|---|---|---|
| **Epics & Stories** (under review) | FOUND (single, whole) | `05-epics-and-stories/epics.md` | 666 lines; 6 epics / 23 stories; no sharded duplicate |
| **PRD** | FOUND (single, whole) | `02-prd/prds/prd-arhugula-v2-2026-06-04/prd.md` | FR-1..FR-22, NFR-1..NFR-8, SM/SM-C, §5 refusals, §6.2 deferred tail, §11 open Qs, §3 Glossary |
| **PRD addendum** | FOUND | `.../prd-arhugula-v2-2026-06-04/addendum.md` | mechanism + transport + schemas |
| **Architecture (ARD)** | FOUND (single, whole) | `04-architecture/architecture.md` | 900 lines; AD-0..AD-19; **§9 ratification register** (the load-bearing cross-check) |
| **UX Design** | **N/A — deliberately not applicable** | — | Non-UI process-governance feature; only "UI" is the 3-integer SessionEnd health-line (FR-15). ARD §3.0 confirms `Frontend → N/A`. No UX gap is flagged and **no UX-DR is fabricated** (fabricating one would be the silent-scope-extension failure mode). |

**Duplicates:** none (no whole-vs-sharded conflict for any document type).
**Missing required documents:** none. UX absence is by-construction, not a gap.
**`persistent_facts` (`**/project-context.md`):** no such file exists in this repo — noted gracefully per the skill's instruction, continued.

**Step-1 verdict:** Clean inventory; proceed to PRD analysis.

---

## PRD Analysis (Step 2) — requirements re-derived from the PRD, independently

*Extracted directly from `prd.md` §4 (FR), §8 (NFR), §7 (SM/SM-C), §5 (refusals), §6.2 (deferred tail). Counts re-derived, not copied from the epics.*

### Functional Requirements (PRD §4) — 22 found

| FR | PRD feature / WS | One-line capability (PRD text) |
|---|---|---|
| FR-1 | §4.1 / WS-0 | Binary D1–D6 drift taxonomy; each class scored 0/1 from a transcript, no tool/model |
| FR-2 | §4.1 / WS-0 | Counterfactual two-arm probe (Arm A=HEAD / Arm B=slimmed) over real sessions; per-class incidence |
| FR-3 | §4.1 / WS-0 | `SOUND` iff Arm B ≤ Arm A on every class AND < on ≥1; verdict from tallied incidents, never byte-count |
| FR-4 | §4.1 / WS-0 | `not-exercised` cell rule (≠ `passed`); `INCOMPLETE-on-{D4,D6}` literal verdict |
| FR-5 | §4.1 / WS-0 | Codebook-lens (recall→D1/D4, artifact→D2/D5, continuation→D3/D5); adds no test |
| FR-6 | §4.1 / WS-0 | Operator waiver discharges `INCOMPLETE` for an unexercised rare class; no minimum-exposure mandate |
| FR-7 | §4.2 / WS-1 | Verify-before-evict dependency scan (rules/hooks/scripts/recovery-paths); precondition to eviction |
| FR-8 | §4.2 / WS-1 | L1 deterministic slim-time assertion (scan-discovered invariants resolve post-eviction); fail blocks slim |
| FR-9 | §4.2 / WS-1 | Provenance eviction to a git-versioned archive; byte-recoverable; a move, never a deletion |
| FR-10 | §4.2 / WS-1 | Altitude-content retention + attention-positioning (start/end, not mid-window); locked rules verbatim |
| FR-11 | §4.3 / WS-2a | SSOT pointer + un-anchored `artifact→version` `INDEX.md`; canonical resolvable without inline version |
| FR-12 | §4.3 / WS-2a | Navigation-set guardrail; forbids invented `GC/ROUTING/CATALOG.md`, authored `WORKFLOWS.md`, `@import`-ing anchors, `#section` anchors |
| FR-13 | §4.4 / WS-3a | Degree-keyed selection: KEEP-HOT (≥5) / KEEP-LINKED (1–4) / ARCHIVE (0); pin-set re-derived at slim-time |
| FR-14 | §4.4 / WS-3a | Bi-temporal supersede-mark (`valid_until` + `superseded_by` + archive body); never silent-drop |
| FR-15 | §4.4 / WS-3a | Three-integer SessionEnd health-line (`notes-superseded`, `notes-untouched-beyond-N-days`, `patterns-unwritten-with-≥4-refs`) |
| FR-16 | §4.4 / WS-3a | One-time hygiene write of the dangling ≥4-ref lessons (NOT the recurring consolidation pass) |
| FR-17 | §4.5 / WS-4 G1 | Effective-auto-loaded-context byte-sum `--check` (`CLAUDE.md` + `@import`-closure + `MEMORY.md`) |
| FR-18 | §4.5 / WS-4 G1 | Warn-then-fail mode with explicit waiver path |
| FR-19 | §4.5 / WS-4 G1 | Review-time/CI-only execution (never-halt composition) |
| FR-20 | §4.6 / X-min | Snapshot/versioned store (git rollback boundary) + atomic writes |
| FR-21 | §4.6 / X-min | Stale-base (OCC) detection; serialization at the store, not a topology lead; full locking deferred |
| FR-22 | §4.6 / X-min | Reinject-pointer-resolvability floor (absence-guard graceful-degrade on a missing target) |

**Total FRs (independent count): 22.** Matches the epics' claim of FR-1..FR-22.

### Non-Functional Requirements (PRD §8) — 8 found

NFR-1 Proportionality (governing constraint) · NFR-2 Attention-aware context budget · NFR-3 Non-lossiness of durable memory · NFR-4 Recoverability + concurrency-safety (OCC) · NFR-5 Observability at boundary, not runtime · NFR-6 Never-halt composition · NFR-7 Honest-verdict integrity (`INCOMPLETE` over false-pass) · NFR-8 Non-lossy lane discipline (authoring vs execution).

**Total NFRs (independent count): 8.** Matches the epics' claim.

### Success metrics (PRD §7)

- **Primary:** SM-1 — drift reduction by tallied incidents (THE acceptance gate).
- **Secondary:** SM-2 memory non-lossiness · SM-3 byte-budget (reported leading indicator) · SM-4 memory-health observability.
- **Counter-metrics:** SM-C1 the false-green (primary failure mode) · SM-C2 over-eviction · SM-C3 clean guardrail masking unobserved rot · SM-C4 gate-machinery creep.

### Principled refusals (PRD §5 / ARD §2.8 R1–R9) and deferred tail (PRD §6.2 / ARD §8)

Refusals R1–R9 (eval harness / model-judge / rot-score / consolidation daemon / recompute engine / byte-count-as-gate / synthetic corpus / invented nav conventions / becoming-a-platform). Deferred tail: G-LINK, recurring consolidation, WS-2b, WS-3b, WS-4 G2/G3/G4, per-axis G1 scope, WS-5, WS-6 6b, X-full, Tier-2 ICM. **These set the proportionality boundary for Constraint-3 (no story may build refused/deferred machinery).**

### PRD completeness assessment

The PRD is unusually complete for story-creation input: every FR carries explicit **"Consequences (testable)"** that read as pre-written, source-faithful acceptance criteria; the Glossary (§3) fixes vocabulary verbatim; assumptions are indexed (§12) and routed to the ARD §9 register. **No FR is under-specified to the point of blocking story authoring.** Three FRs carry genuine operator-decision residuals (FR-2 session-count, FR-6 waiver-owner, FR-18 clean-baseline) — surfaced in §11 and tracked at ARD §9, not silently closed.

---

## Epic Coverage Validation (Step 3) — independent FR → story-AC traceability

*Method: for each PRD FR I located the owning story and read its Given/When/Then ACs to confirm the AC actually **tests** the FR (not coverage-in-name-only). "Genuinely tested" = at least one AC asserts the FR's observable consequence. This is built from the PRD + story bodies, NOT from the epics' own FR Coverage Map.*

### FR coverage matrix (re-derived)

| FR | Owning story | AC that tests it (verified in story body) | Status |
|---|---|---|---|
| FR-1 | 1.1 | "each of the six classes … has a documented one-line observable criterion … without running any tool or model"; "exactly 0 or 1" | ✓ Genuinely tested |
| FR-2 | 1.2 (Arm A) + 1.7 (Arm B) | "reuses real … sessions — NO synthetic corpus"; "Arm A captured … *before* the slim ships"; 1.7 "Arm B reuses real sessions … arm labels de-identified/shuffled" | ✓ Genuinely tested |
| FR-3 | 1.3 | "`SOUND` … only when Arm B ≤ Arm A on every class AND strictly < on ≥1"; "takes the incidence matrix … as its only input — NO byte-delta … participates" | ✓ Genuinely tested |
| FR-4 | 1.4 | "zero incidents in both arms … `not-exercised` … CANNOT be counted as the strictly-improved class"; "literally names … `INCOMPLETE-on-D4`/…/`-D4-and-D6` … never `SOUND`" | ✓ Genuinely tested |
| FR-5 | 1.5 | "documented mapping from the three failure-observation types … introduces, runs, or authors NO test"; intra-rater consistency | ✓ Genuinely tested |
| FR-6 | 1.6 | "names the specific class … recorded explicitly, not implied by silence"; "NO 'keep running until exercised' mandate" | ✓ Genuinely tested |
| FR-7 | 2.1 | "scan covers … rules + hooks + scripts + recovery-paths"; "candidate with ≥1 reference … NOT silently evicted"; "eviction CANNOT run before this scan" | ✓ Genuinely tested |
| FR-8 | 2.2 | "scope is exactly the scan-discovered invariants — NOT a hard-coded list"; "judge-free and deterministic"; "a failed assertion BLOCKS the slim" | ✓ Genuinely tested |
| FR-9 | 2.3 | "byte-recoverable verbatim from the git-versioned archive"; "eviction to a non-versioned path is invalid"; "NO evicted content is deleted" | ✓ Genuinely tested |
| FR-10 | 2.4 | "retained set is the altitude content … version-provenance is NOT among it"; "near the prefix start or end … verified by inspection"; "locked operator rules … preserved VERBATIM" | ✓ Genuinely tested |
| FR-11 | 3.1 | "`INDEX.md` maps each artifact to its canonical version"; "resolvable … WITHOUT reading an inline version string"; "un-anchored — artifact→version only" | ✓ Genuinely tested |
| FR-12 | 3.2 | "`GC.md`/`ROUTING.md`/`CATALOG.md` … NOT invented"; "`WORKFLOWS.md` … NOT authored"; "NO WS-2 anchor `@import`-ed"; "hand-authored `#section` anchors … NOT introduced" | ✓ Genuinely tested (all 4 inversions each carry an AC) |
| FR-13 | 4.1 | "keyed on wiki-link in-degree, NOT on prefix/filename/category"; the 3-tier KEEP-HOT/KEEP-LINKED/ARCHIVE split with the explicit "binary split that collapses KEEP-LINKED does NOT satisfy this"; "re-derived against the current count"; "grep \| wc -l — NO recompute engine" | ✓ Genuinely tested |
| FR-14 | 4.2 | "`valid_until` … + `superseded_by` … body moved to `memory/archive/`; NOT removed without a mark"; "NO compaction path deletes a lesson with no breadcrumb"; "Tier-1 breadcrumb — NOT a Tier-5 ledger write" | ✓ Genuinely tested |
| FR-15 | 4.3 | "exactly three integers — `notes-superseded`, `notes-untouched-beyond-N-days`, `patterns-unwritten-with-≥4-refs` … never a fourth"; "NOT a rot-score/dashboard"; "session boundary only" | ✓ Genuinely tested |
| FR-16 | 4.4 | "the two named pattern notes … finite one-time action"; "NOT the recurring consolidation pass"; "scope is exactly the two named notes" | ✓ Genuinely tested |
| FR-17 | 5.1 | "exactly `bytes(CLAUDE.md) + bytes(@import-closure) + bytes(MEMORY.md)` — a byte-sum, NOT attention-weighted/token-estimated"; "does NOT validate link integrity" | ✓ Genuinely tested |
| FR-18 | 5.2 | "before clean: WARNS (exit 0); after: FAILS (exit 1)"; "`--waiver <reason>` … passes without removing the gate"; "NEVER forces … unreadable compression" | ✓ Genuinely tested |
| FR-19 | 5.3 | "runs at code-review/CI time … does NOT execute as an in-loop runtime step"; "NO live session is halted"; "adds one CI step — NO daemon/runtime surface" | ✓ Genuinely tested |
| FR-20 | 6.1 | "versioned such that a prior state is recoverable, git as rollback boundary"; "fully applies or does not apply (atomic temp-then-rename)"; superseded body recoverable from a snapshot | ✓ Genuinely tested |
| FR-21 | 6.2 | "stale-base write is DETECTED rather than silently overwriting"; "serialization at the store (OCC) … NOT at a topology lead"; "full write-locking NOT part of this story" | ✓ Genuinely tested |
| FR-22 | 6.3 | "degrades gracefully — appended note left empty, execution CONTINUES; does NOT hard-error / proceed on a phantom"; resolution-validation of present-but-drifted explicitly OUT of MVP floor | ✓ Genuinely tested |

### Coverage statistics (independent)

- **Total PRD FRs: 22.**
- **FRs with an owning story AND ≥1 genuinely-testing AC: 22.**
- **Coverage: 22/22 = 100%. Zero coverage-in-name-only. Zero orphan FR. Zero FR claimed-covered whose ACs do not actually test it.**
- FRs in the epics but NOT in the PRD: **none** (no invented requirement).
- Story granularity: 23 stories / 22 FRs ≈ 1:1; the one split beyond 1:1 is FR-2 → {Story 1.2 Arm A, Story 1.7 Arm B}, which is correct (the two arms have distinct dependency profiles — Arm A is foundational, Arm B is the closing action). FR-2 is fully covered across the pair.

### NFR coverage (independent spot-check against story ACs)

| NFR | Enforced by (verified in story ACs) | Status |
|---|---|---|
| NFR-1 Proportionality | Explicit anti-bloat ACs on 1.1 (zero new tooling/model-judge), 1.2 (no synthetic corpus), 2.1 (one-shot not standing CI), 4.1 (no recompute engine), 4.3 (exactly 3 integers), 5.3 (one CI step, no daemon); Out-of-Scope section bounds the rest | ✓ Covered (cross-cutting) |
| NFR-2 Attention-aware budget | Story 2.4 ("near start/end vs the mid-window trough … verified by inspection, no numeric boundary invented") | ✓ Covered |
| NFR-3 Non-lossiness | Story 4.2 (supersede-mark + archive-move, structural) + Story 6.1 (snapshot recoverability of archived bodies) | ✓ Covered |
| NFR-4 Recoverability + concurrency | Stories 6.1 (git rollback + atomic) + 6.2 (OCC) | ✓ Covered |
| NFR-5 Observability at boundary | Story 4.3 (exactly 3 grep-derived integers at SessionEnd; boundary-only; no runtime console) | ✓ Covered |
| NFR-6 Never-halt composition | Story 5.3 (review-time/CI only) + Story 6.3 (reinject floor continues-on-absence) | ✓ Covered |
| NFR-7 Honest-verdict integrity | Stories 1.3, 1.4 (the gate can FAIL; `INCOMPLETE` over false-pass; `not-exercised` ≠ `passed`) | ✓ Covered |
| NFR-8 Non-lossy lane discipline | Story 2.3 (eviction = move to versioned archive, byte-recoverable, never deletion); Story 6.1 (store first-commit is execution-arc via X-AL-3 escape-hatch) | ✓ Covered |

**NFR coverage: 8/8.** Every NFR is enforced by at least one concrete story AC (as a cross-cutting constraint, correctly — NFRs are not stood up as standalone stories, which matches BMad practice).

**Step-3 verdict:** Coverage is genuinely complete. No missing FR/NFR; no name-only coverage; no invented requirement.

---

## UX Alignment (Step 4) — deliberately N/A

**UX document status:** None exists, **by construction**, and that is correct — not a gap.

- This is a **non-UI process-governance feature**. The only operator-facing "UI" surface is the **three-integer SessionEnd health-line** (FR-15 / Story 4.3), which is a plain-text boundary report, not a screen, journey, or interaction surface.
- ARD §3.0 explicitly records `Frontend → N/A → the 3-integer SessionEnd health-line; dashboard permanently in WS-5 deferral`. PRD §2.4 has a single operator journey (UJ-1) captured as JTBD, with the agent as beneficiary, not a UI protagonist.
- The epics author correctly **skipped UX-requirements extraction and fabricated no `UX-DR` items**. Fabricating UX requirements for a non-UI feature would be the silent-scope-extension failure mode (and would itself violate NFR-1 proportionality / refusal R3 "no dashboard").

**Alignment check that DOES apply:** the one UI surface (the health-line) must stay within its bound. Story 4.3 holds it to **exactly three integers, boundary-only, no rot-score/dashboard** — consistent with PRD §4.4 / NFR-5 / ARD §4.5. A live dashboard is permanently deferred to WS-5. No UX↔PRD or UX↔Architecture misalignment exists because there is no UX surface beyond this bounded line, and the line is correctly bounded.

**Step-4 verdict:** N/A recorded as deliberate. No warning, no fabricated UX requirement, no gap.

---

## Epic Quality Review (Step 5)

*The deepest pass: the three load-bearing constraint audits (the highest-value checks), then story-quality + dependency analysis. Findings are graded Critical / Major / Minor per the skill's severity scheme.*

### 5.A — Constraint-1 audit: X-AL-3 / no silent absorption of unratified ARD §9 decisions  ★ highest-value check

**Method.** I independently enumerated the open/contested items in the ARD §9 register, then cross-checked each against (a) the story body that depends on it and (b) the epics' own "Ratification Dependencies" table — testing for *both* failure directions: a §9-open value **silently baked into an AC as settled and unflagged** (the real defect), and an item the ARD says needs **no** ratification but a story **over-flags** anyway.

**Independent enumeration of ARD §9 (the ground truth):**

| ARD §9 item | Status in ARD | Dependent FR/story | Correct disposition |
|---|---|---|---|
| §9.1 retained-altitude set | open (PRD-assumption) | FR-10 / 2.4 | must be flagged |
| §9.2 navigation anchors | open (PRD-assumption) | FR-12 / 3.2 | must be flagged |
| §9.3(a) health-count thresholds + N | open (PRD Q3) | FR-15 / 4.3 | must be flagged |
| §9.3(b) present-but-drifted resume-target | open (PRD Q5) | FR-22 / 6.3 | must be flagged |
| §9.4 "clean baseline" definition | open (PRD Q7) | FR-18 / 5.2 | must be flagged |
| §9.5.1 store-not-a-repo framing | open (corpus-vs-HEAD) | FR-20 / 6.1 | must be flagged |
| §9.5.2 G1 input-scope boundary | open (corpus-vs-HEAD) | FR-17 / 5.1 | must be flagged |
| **§9.5.3 MEMORY.md growth** | **"No ratification needed"** (ARD verbatim) | confirmation only | **must NOT be flagged** |
| §9.6.1 session-count floor + workflow-class set | open (PRD Q1) — *arm-comparability sub-item RESOLVED 2026-06-08* | FR-2 / 1.2 | flag the open half only |
| §9.6.2 X-full locking watcher | open (PRD Q2) | FR-21 / 6.2 | must be flagged |
| §9.6.3 waiver owner + `SOUND-WAIVED` adoption | open (PRD Q6) | FR-6 / 1.6 | must be flagged |
| §9.6.4 G1 budget integer + archive + N-days | open (corpus-silent) | FR-17/FR-9/FR-15 / 5.1, 4.3 | must be flagged |
| §9.6.5 INDEX coverage set | open (corpus-silent) | FR-11 / 3.1 | must be flagged |

**Result — direction 1 (silent absorption of an open item):** **NONE FOUND.** Every genuinely-open §9 item carries an explicit `**Ratification dependency: ARD §9.x**` flag on its dependent story body, AND the ARD's recommended default is cited *as a default, ratification-pending* — never baked in as settled:
- 2.4 → §9.1 ✓ · 3.2 → §9.2 ✓ · 4.3 → §9.3(a) + §9.6.4 ✓ · 6.3 → §9.3(b) ✓ · 5.2 → §9.4 ✓ · 6.1 → §9.5.1 ✓ · 5.1 → §9.5.2 + §9.6.4 ✓ · 1.2 → §9.6.1 ✓ · 6.2 → §9.6.2 ✓ · 1.6 → §9.6.3 ✓ · 3.1 → §9.6.5 ✓. **12 ratification flags across 11 stories** (4.3 and 5.1 each carry two), matching the ARD register exactly.

**Result — direction 2 (over-flagging):** **NONE FOUND.** The one ARD item marked **"No ratification needed"** — §9.5.3 (MEMORY.md growth) — is correctly **NOT** flagged as a ratification dependency. The epics record it as architecture-derived requirement **AR-H** ("re-derive the pin-set at slim-time, never freeze a list"), explicitly labeled "No ratification needed … recorded as confirmation only," and the Ratification-Dependencies preamble names it as deliberately excluded. This is exactly right — flagging it would be over-flagging.

**Sub-item integrity (advisor cross-check).** The arm-comparability method under §9.6.1 was **resolved** in the ARD (operator-ratified REPORT form / `SOUND-COMPOSITION-CONFOUNDED`, 2026-06-08) while the session-count floor + workflow-class set stay open. The stories treat this split correctly: Stories 1.3 / 1.4 / 1.7 use the REPORT-form verdict set (`SOUND-COMPOSITION-CONFOUNDED`, the normalization discipline) as **settled** — not silent absorption, because the ARD ratified it — while Story 1.2 flags only the genuinely-open half (the ~15–25 floor + named workflow-class set). No under-flag, no over-flag on the sub-item.

**Table-vs-body integrity.** The epics' Ratification-Dependencies *table* (12 rows) matches each story *body* flag one-for-one; no table row claims a flag its story body omits, and no story body flags an item the table omits.

**Constraint-1 verdict: PASS (clean).** Zero silent absorption; zero over-flagging; table and bodies reconcile. This is the task's named "worst failure mode," and it is genuinely held.

### 5.B — Constraint-2 audit: spine = drift-reduction, NOT byte-count (no story's *win* is a smaller file)

**Method.** I checked every story's success condition: a story is a defect if its *win* is "byte ≤ cap" / "file smaller." The Epic-5 guardrail legitimately *measures* a byte-sum as mechanism — that is allowed; what is forbidden is a story whose acceptance hinges on the file being smaller.

| Story | Success condition | Byte-cap-as-win? |
|---|---|---|
| Epic 1 (1.1–1.7) | The WS-0 matrix / verdict (SM-1) | No — explicitly "never byte-count"; 1.3 carries the SM-C1 false-green guard AC ("a green byte-budget guardrail is NEVER read as a pass-signal") |
| 2.3 (evict) | "byte-recoverable verbatim from the git-versioned archive"; "the success measure is the Epic 1 probe, NOT the byte delta (SM-3 is a reported indicator only)" | No — the win is recoverability + the probe, not a smaller file |
| 2.4 (position) | Altitude retained + positioned by inspection | No |
| Epic 5 (5.1–5.3) | A working `--check` that warns/fails/waives at review-time | **Measures** a byte-sum (allowed mechanism); **win is not "smaller."** 5.1 carries the explicit SM-C1 false-green guard AC: "a green `--check` is read as a reported leading indicator ONLY — NEVER as 'the layer succeeded'" |
| 1.4 | honest `INCOMPLETE` | No — carries the SM-C3 guard ("a green byte-budget guardrail … NEVER read as 'memory is healthy'") |

**Constraint-2 verdict: PASS (clean).** No story's win is a smaller file. Epic 5 measures bytes as mechanism and explicitly demotes the green check to a reported indicator (SM-3), with the false-green counter-metric (SM-C1) carried as an explicit guard AC on Stories 1.3, 1.4, and 5.1. The epic even opens with a dedicated "Constraint discipline for this epic" note making this distinction.

### 5.C — Constraint-3 audit: proportionality / MVP-only (no story builds refused or deferred-tail machinery)

**Method.** I checked each story against PRD §5 refusals (R1–R9) and the PRD §6.2 / ARD §8 deferred tail, testing whether any story decomposes refused or deferred scope into build work.

| Deferred/refused scope | Guarded by a story AC? |
|---|---|
| Recurring consolidation pass (deferred) | Story 4.4 AC: "one-time hygiene write, NOT the recurring consolidation pass … is NOT stood up here"; "scope is exactly the two named notes — does NOT scan-and-promote the broader set" ✓ |
| G-LINK / resolution-validation of present-but-drifted target (deferred) | Story 6.3 AC: "resolution-validation … NOT part of the MVP floor — it rides the deferred G-LINK"; Story 3.1: section-router "is the deferred WS-2b enhancement, Out of Scope" ✓ |
| X-full full write-locking (deferred) | Story 6.2 AC: "full write-locking is NOT part of this story — deferred to X-full" ✓ |
| Model-judge / eval harness / synthetic corpus (R1/R2/R7) | Story 1.1 AC: "NO script, NO model-judge, NO synthetic test case"; Story 1.2: "NO synthetic or authored corpus" ✓ |
| Rot-score / 4th integer / dashboard (R3) | Story 4.3 AC: "exactly three integers … never a fourth … NOT a rot-score … NOT a dashboard" ✓ |
| Connectivity-recompute engine (R5) | Story 4.1 AC: "grep \| wc -l — NO connectivity-recompute engine is built" ✓ |
| Invented nav conventions / `WORKFLOWS.md` (R8) | Story 3.2 ACs forbid each inversion ✓ |
| Standing CI gate from a one-shot script (NFR-1) | Story 2.1 AC: "one-shot Python script … NOT a standing CI gate, NOT a daemon" ✓ |
| Tier-2 ICM structural adoption | Out-of-Scope §A; not decomposed ✓ |

The deferred tail and the R1–R9 refusals are **listed under "Out of Scope," never decomposed into stories**, exactly as proportionality (NFR-1) requires. The ARD §7 reusable framework is correctly recorded as a template (Out-of-Scope §C), not a 7th epic.

**Constraint-3 verdict: PASS (clean).** No story builds refused or deferred machinery. Multiple stories carry explicit "this does NOT build the deferred half" guard ACs — proportionality is actively enforced at the AC level, not merely asserted.

### 5.D — Story-quality review (BMad create-epics-and-stories standards)

**User-value / "technical-milestone" check.** This is a non-UI process-governance layer where the **operator** and the **in-session agent** ARE the users — so the skill's "Setup Database / API Development = no user value" red-flag is calibrated for user-facing apps and does NOT mechanically apply. I checked each apparently-technical story for a real user outcome:
- Stories 2.1 / 2.2 (scan, L1 assert) read technical but each has a genuine operator "So that" — "I know exactly which invariants are load-bearing … before anything is evicted" / "a slim that would strand a load-bearing reference is blocked before it ships." These are safety-interlock outcomes the operator directly values; correct framing, **not** technical milestones.
- Stories 6.1 / 6.2 (snapshot, OCC) similarly have real operator outcomes ("a prior store state is recoverable" / "two sessions cannot silently clobber each other"). Correct.
- Every epic title is value-titled (not "WS-N"), and each delivers an end-to-end governance capability. **No technical-milestone epic.** PASS.

**As-a / I-want / So-that structure.** All 23 stories carry a correct three-part role statement. Roles are honest: most are "As the operator," with the in-session agent used as "(beneficiary)" where it is the true beneficiary (2.4, 3.1, 6.3) and the grader for the WS-0 stories (1.1, 1.5). No mis-attributed roles. PASS.

**Given/When/Then testability.** Every story uses Given/When/Then ACs with observable, specific outcomes (verified per-FR in Step 3). ACs name literal verdict strings / field names verbatim (per ARD §5.2 discipline), making them machine-checkable where applicable. No vague "user can X" ACs. PASS.

**Story sizing.** Right-sized at ≈1 story per FR (23/22). No epic-in-disguise story (each is a single coherent capability), no trivial story. The one beyond-1:1 split (FR-2 → 1.2 + 1.7) is justified by distinct dependency profiles. PASS.

**Greenfield/starter check.** ARD §2.0 establishes there is **no greenfield starter** — this is an additive overlay on a committed monorepo. The epics correctly make **Epic 1 Story 1.1 = "define the D1–D6 taxonomy"** (the WS-0 baseline-first sequencing), NOT a project-init/scaffold story (recorded as AR-A). This is the correct handling of the "first implementation step" for a measurement-gated governance layer. PASS.

### 5.E — Dependency analysis

**Within-epic forward dependencies (the BMad "forbidden" check).** I traced each story's dependencies within its epic:
- **Epic 1:** 1.1 (taxonomy) → 1.2 (Arm A, needs taxonomy) → 1.3 (verdict fn) → 1.4 (extends 1.3) → 1.5 (lens) → 1.6 (waiver) → 1.7 (Arm B, closing). Each depends only on **earlier** stories. **No forward dependency.**
- **Epic 2:** ordered pipeline 2.1 → 2.2 → 2.3 → 2.4, each on the previous. No forward dependency.
- **Epics 3, 4, 5, 6:** each story depends only on previous stories within its epic (verified). No forward dependency.

**The 1.3 ↔ 1.7 circular-dependency claim — VERIFIED RESOLVED.** The epics author claims to have fixed a 1.3↔1.7 circularity. I verified this is genuine, not cosmetic:
- The naïve circularity would be: 1.3 (the verdict function) needs Arm-B data to be authored, but Arm B (1.7) needs the verdict function to compute its result → a cycle.
- The resolution in the story bodies: **Story 1.3's AC explicitly states** the verdict function "is authored and unit-exercised against *illustrative* incidence — it does NOT require the live Arm-B run, which is Story 1.7's application of this function." Story 1.4 carries the identical carve-out. Story 1.7's AC then "runs the verdict function (Stories 1.3, 1.4)" against live Arm-B data.
- **Result:** the dependency is strictly one-directional (1.3 → 1.7); 1.3/1.4 are authored against illustrative data with no dependency on 1.7, and 1.7 applies the already-authored function to live data. **No cycle. Genuinely resolved**, with the resolution written into the ACs (not merely asserted in prose).

**Cross-epic dependencies (named, not hidden — evaluated, not rubber-stamped).** Two exist; both legitimately strain BMad's epic-independence ideal but are **honestly named as cross-epic, not buried as within-epic forward refs**:
1. **Story 1.7 → Epics 2–6 (the WS-0 bracket).** Story 1.7 (Arm-B capture + close verdict) cannot complete until the slimmed layer (Epics 2–6) lands. This is **inherent to a before/after acceptance gate** — the gate measures the layer it brackets. The epics handle it correctly: Epic 1 delivers the standalone *instrument* (1.1–1.6) as independently-completable, and carries 1.7 with an **explicit, named cross-epic dependency** ("this story is the closing action … cannot complete until Epics 2–6 land … the dependency is named, not hidden"). This is the right structural treatment; it is not a defect.
2. **Story 2.3 → Story 3.1 (INDEX before eviction, AR-I / ARD §6.1 ★NEW-1).** The §2 version-row eviction must be preceded by / atomic-with the `INDEX.md` so a canonical-version pointer is navigable before it leaves the prefix. Both Story 2.3 and Story 3.1 carry the matching cross-epic dependency note. **Note (minor, in the epics' favor):** the epics state this ordering *more clearly* than the ARD's own §6.1 table, which lists step 1b (evict) before step 1c (INDEX) in row order while the ★NEW-1 prose mandates INDEX-first — the epics resolve to the correct INDEX-first reading on both stories. No defect.

**Database/entity-timing check.** N/A — there is no relational DB; "state" is git + plain-text/frontmatter. The analogous check (create artifacts only when first needed) is satisfied: `INDEX.md`, the archive, `memory/.git`, and the supersede-schema are each created by the story that first needs them, not front-loaded. PASS.

### 5.F — Quality findings by severity

**🔴 Critical violations:** **NONE.** No technical-milestone epic; no forward dependency; no epic-sized unstartable story; no silent §9 absorption; no byte-cap-as-win; no deferred-scope build.

**🟠 Major issues:** **NONE.**

**🟡 Minor concerns (3):**
- **M-1 — `SOUND-WAIVED` verdict-string used without a re-flag in Stories 1.3 and 1.7.** The *adoption* of the distinct `SOUND-WAIVED` verdict is ratification-pending at ARD §9.6.3, and Story 1.6 flags it correctly ("the distinct `SOUND-WAIVED`, per the §9.6.3 sharpening … operator-pending"). Stories 1.3 and 1.7 list `SOUND-WAIVED` in their verdict-string set as a verbatim ARD §5.2 string **without** repeating the "if §9.6.3 ratified" caveat that the ARD's own verdict-function carries ("`SOUND` (or `SOUND-WAIVED` if §9.6 ratified)"). This is **not silent absorption** — the dependency is flagged at its owning story (1.6) and the string is genuinely in the ARD — but for byte-exact caveat-consistency, 1.3 and 1.7 could note "`SOUND-WAIVED` pending §9.6.3 adoption (flagged at 1.6)." Cosmetic; does not block build.
- **M-2 — `INDEX.md` coverage rows are illustrative, not yet the ratified set.** Story 3.1's content + ARD §4.3 show example INDEX rows (specs/plans/CXA versions). The actual coverage set is §9.6.5-pending (correctly flagged on 3.1). No action needed beyond resolving §9.6.5 before 3.1 builds — already captured as a ratification dependency.
- **M-3 — Empirical figures are snapshot-anchored and must re-derive at build-time.** The dangling-ref counts (≈6/≈5), the "~277KB" historical eviction magnitude, MEMORY.md/axis-file byte figures are cited as the ARD's 2026-06-08 snapshot and explicitly flagged to re-derive at slim-time (AD-12). I confirmed at HEAD: `design-substrate/INDEX.md` is absent (Story 3.1 greenfield ✓), and **both** named dangling-pattern note files (`plan-revision-against-not-yet-built-substrate.md`, `strike-revision-on-refined-second-tier-reason.md`) are **absent** from the memory store (Story 4.4's "no note file at HEAD" ✓ — trigger genuinely live). The figures are correctly framed as re-derive-at-build, not frozen. No defect; flagged so the execution arc re-derives rather than trusting the snapshot.

**Step-5 verdict:** Zero Critical, zero Major, three Minor (all cosmetic / already-tracked). Story quality is high; dependencies are clean (no forward deps; the 1.3↔1.7 circularity is genuinely resolved; the two cross-epic deps are inherent and honestly named).

---

## Final Assessment (Step 6)

### Overall readiness status

# VERDICT: READY-WITH-CONDITIONS

The epics-and-stories set is **build-ready**. Requirements traceability is complete and genuine (22/22 FR + 8/8 NFR, zero coverage-in-name-only, zero invented requirement); story quality is high (correct structure, right-sized, testable Given/When/Then); dependencies are clean (no within-epic forward dependency, the 1.3↔1.7 circularity is genuinely resolved, the two cross-epic dependencies are inherent and honestly named); and all three load-bearing constraints hold (zero silent §9 absorption, no byte-cap-as-win, no deferred-scope build). **No Critical or Major defect was found.**

The verdict is **READY-WITH-CONDITIONS** rather than unqualified READY for one honest reason: **12 ARD §9 ratification decisions are still operator-pending.** These are *named conditions*, not gaps in the epics — every one is explicitly flagged on its dependent story as "a default, ratification-pending," never baked in as settled. **None blocks the build start:** per ARD §10.4, step 0 (Epic 1 Story 1.1 + the Arm-A baseline capture, Story 1.2) can begin immediately; each §9 item must be resolved with the operator only **before its specific dependent component is built**.

This is not a rubber-stamp: I ran both directions of the silent-absorption check, re-derived FR/NFR coverage from the PRD independently, and verified the empirical triggers at HEAD. The epics genuinely held the disciplines the task flagged as highest-risk.

> **Build-ready ≠ done.** "Ready to hand to implementation (modulo §9)" is a different question from "the layer is validated." Per ARD §6.2 / §10.1, the layer is *done* only when the WS-0 probe (Story 1.7) returns `SOUND`/`SOUND-WAIVED` — measured drift-reduction, not this readiness status and never a clean byte-count. This report certifies the former.

### Prioritized gap list

**🔴 Critical (must fix before build):** **NONE.**

**🟠 Important (should resolve at the right point in the build):**
- **The 12 ARD §9 ratifications are real conditions, not gaps — but they ARE the conditions.** Each must be operator-decided before its dependent component builds (not before build *start*). Ownership map (item → dependent story):
  - §9.1 retained-altitude set → **2.4** · §9.2 nav anchors → **3.2** · §9.3(a) health thresholds + N-days → **4.3** · §9.3(b) present-but-drifted resume-target → **6.3** · §9.4 "clean baseline" → **5.2** · §9.5.1 store-not-a-repo framing → **6.1** · §9.5.2 G1 input-scope → **5.1** · §9.6.1 session-count floor + workflow-class set → **1.2** · §9.6.2 X-full watcher → **6.2** · §9.6.3 waiver owner + `SOUND-WAIVED` adoption → **1.6** · §9.6.4 G1 budget integer + archive + N → **5.1, 4.3** · §9.6.5 INDEX coverage set → **3.1**.
  - These are an **operator decision batch**, surfaced as the explicit agenda the epics built. Recommended: ratify the ARD's recommended defaults (they are well-reasoned and low-commitment) at the SessionEnd/roadmap cadence; pin concrete values (budget integer, N-days) at execution.

**🟡 Minor (cosmetic / already-tracked — no build block):**
- **M-1** — Stories 1.3 and 1.7 list the `SOUND-WAIVED` verdict-string without repeating the "pending §9.6.3 adoption" caveat that Story 1.6 carries. Not silent absorption (flagged at its owning story 1.6; the string is verbatim per ARD §5.2). Optional one-line caveat for byte-exact consistency.
- **M-2** — `INDEX.md` coverage rows in Story 3.1 / ARD §4.3 are illustrative; the real set is §9.6.5-pending (already flagged on 3.1).
- **M-3** — Empirical figures (dangling-ref counts, ~277KB eviction magnitude, byte snapshots) are snapshot-anchored and flagged to re-derive at slim-time (AD-12). Verified at HEAD: `design-substrate/INDEX.md` absent (3.1 greenfield ✓); both named dangling-pattern notes absent (4.4 trigger live ✓). Correctly framed; no defect.

### Independent audit results (the task's named checks)

| Check | Result |
|---|---|
| **Independent FR coverage** (re-derived from PRD) | 22/22 genuinely covered; zero name-only; zero orphan; zero invented |
| **Independent NFR coverage** | 8/8 enforced by concrete story ACs |
| **§9 silent-absorption (direction 1)** | PASS — zero open §9 item baked in as settled; all 12 flagged on their dependent story |
| **§9 over-flagging (direction 2)** | PASS — §9.5.3 ("No ratification needed") correctly NOT flagged (recorded as AR-H confirmation) |
| **Constraint-2 (no byte-cap-as-win)** | PASS — no story's win is a smaller file; Epic 5 measures bytes as mechanism only; SM-C1 false-green guards on 1.3/1.4/5.1 |
| **Constraint-3 (no deferred/refused build)** | PASS — deferred tail + R1–R9 listed under Out-of-Scope, never decomposed; explicit "does-not-build-the-deferred-half" guard ACs |
| **1.3↔1.7 circular dependency** | VERIFIED RESOLVED — one-directional (1.3→1.7); 1.3/1.4 authored against illustrative incidence, 1.7 applies to live data; no cycle |
| **Within-epic forward dependencies** | NONE — every story depends only on earlier stories in its epic |
| **Cross-epic dependencies** | 2 (1.7→Epics 2–6; 2.3→3.1) — both inherent and honestly named, not hidden |
| **UX (Step 4)** | Correctly N/A (non-UI); no UX-DR fabricated; no gap flagged |

### Recommended next steps

1. **Begin the build at step 0 immediately** — Epic 1 Stories 1.1 (define D1–D6 taxonomy) + 1.2 (capture Arm-A baseline on HEAD). Nothing blocks this.
2. **Batch the 12 §9 ratifications to the operator** as a single decision agenda (the epics' "Ratification Dependencies" table is that agenda). Resolve each before its dependent component (per the ownership map above), not before build start.
3. **Re-derive snapshot figures at slim-time** (AD-12) — the dangling-ref counts, the eviction magnitude, and all byte figures — rather than trusting the 2026-06-08 snapshot.
4. **(Optional, cosmetic)** add the "pending §9.6.3" caveat to the `SOUND-WAIVED` mentions in Stories 1.3 / 1.7 (M-1).
5. **At close, run the WS-0 probe (Story 1.7)** — the layer is done only on a `SOUND`/`SOUND-WAIVED` verdict, never on a clean byte-count.

### Final note

This assessment found **0 Critical, 0 Major, 1 Important (the 12-item §9 ratification batch — by design, not a defect), and 3 Minor** issues across the FR/NFR coverage, story-quality, dependency, and three-constraint dimensions. The epics-and-stories set is **build-ready as-is**, modulo the operator resolving the 12 known ARD §9 ratifications before their dependent components build. The disciplines the task flagged as highest-risk — silent §9 absorption, byte-cap-as-success, and deferred-scope creep — are **genuinely held**, verified independently and adversarially rather than taken from the epics' self-claim. The set may proceed to implementation.

---

## Assumptions & Auto-Continued Gates

*This readiness assessment was produced in an autonomous background session. The skill's `[C]` continue menus (Step 1 §7, and the implicit auto-proceed gates of Steps 2–6) were not interactively presented. At each gate the expert-PM decision was made, recorded here, and execution continued to a complete one-pass report.*

1. **Step 1 `[C]` gate (document-inventory confirmation) — auto-continued.** Inventory was unambiguous (one whole copy of each of epics/PRD/addendum/ARD; no duplicates; UX deliberately N/A). No resolution was required, so the gate was auto-cleared and Step 2 entered without operator confirmation.
2. **Input-path override — applied as instructed.** The skill's `{planning_artifacts}=_bmad/artifacts` auto-discovery globs do NOT reach the nested `01-context-memory-layer-planning/` tree; the explicit input + output paths supplied in the invocation were used instead. Recorded so the path divergence from the skill default is transparent.
3. **`persistent_facts` (`**/project-context.md`) — absent, handled gracefully.** No such file exists in the repo; noted and continued per the skill's standing instruction (no fabrication of project-context).
4. **Independent/adversarial posture — chosen over confirmatory.** Per the invocation's explicit warning about correlated blindness (the epics were authored by the same lineage running this check), FR/NFR coverage was **re-derived from the PRD text** and the §9 register **re-run from the ARD against story bodies**, rather than accepting the epics' own FR Coverage Map / 12-dependency self-claim. Where the self-claim verified true, it is reported as confirmed, not assumed.
5. **UX Step 4 — recorded as deliberately-N/A, not a warning.** Per the invocation instruction: missing-UX is NOT flagged as a gap and NO UX-DR is fabricated (a non-UI process-governance feature; the only UI is the bounded 3-integer health-line). Confirmed against ARD §3.0.
6. **advisor() consulted once before writing.** A single stronger-reviewer pass on the full transcript was taken before committing to the verdict framing, to sharpen the silent-absorption cross-checks and avoid both manufactured-gap inflation and rubber-stamping. Four cross-verification checks it surfaced (the `SOUND-WAIVED` re-flag, the arm-comparability resolved/open split, the two cross-epic back-dependencies, the 1.3↔1.7 claim) were each run against the story bodies and are reported above.
7. **Empirical HEAD verification — performed, not assumed.** The greenfield `design-substrate/INDEX.md` absence and the two dangling-pattern note-file absences were verified by filesystem check at HEAD (not taken from the ARD snapshot), grounding the Story 3.1 / 4.4 trigger claims.
8. **Verdict calibration — honest middle.** READY-WITH-CONDITIONS was chosen deliberately: not unqualified READY (12 real operator ratifications pend), not NOT-READY (nothing blocks build-start and no Critical/Major defect exists). No gap was manufactured to look thorough; no defect was suppressed to rubber-stamp.

---

*End of Implementation Readiness Assessment Report. Assessor: `bmad-check-implementation-readiness` (expert PM, requirements-traceability), autonomous background session, 2026-06-08. Verdict: READY-WITH-CONDITIONS — build-ready modulo the 12 ARD §9 operator ratifications, none of which blocks the build start.*
