# Round 2 — Adversarial ⟷ Council Reconciliation — **COMPLETE, reconciled-to-zero**

**Date:** 2026-06-03 · **Gate:** this must close BEFORE Codex/advisor handoff (operator-clarified loop step 2). **Status: CLOSED — reconciled-to-zero.**

**Inputs:** `02-adversarial/REVIEW.md` (verdict: CLEAR + 5 Class-2 + 4 Class-1 + 2 missed tensions; cite-verification CLEAN) · Stage-2b council dispositions `round2-council-responses/c{2,3,5,9}.md` · Stage-2c cross-cutting synthesis `round2c-crosscutting/c{1,7,5,9}.md` (the genuine cross-read step — voices reconciling shared seams directly).

**Outcome:** every adversarial finding ACCEPTED or RECONCILED-by-composition; **zero REBUT**; **every cross-cutting seam COHERE**; one sharp NEW finding surfaced by the cross-read (memory store not git-versioned). Ready for Stage 3.

---

## A. Per-finding disposition

| AR-ID | Class | Owner voice(s) | Disposition | PLAN delta (folds into DESIGN.md) |
|---|---|---|---|---|
| **AR-1** plan/execute boundary | 2 | C2 (WS-1/WS-2) | **ACCEPT** | DESIGN.md gets a plan/execute boundary **banner** + a per-WS **`Deliverable-of-THIS-arc`** column. WS-1 deliverable = the cut-list spec + byte-budget value (NOT the eviction); WS-2 deliverable = the nav-infra spec (NOT the authored files). "This arc produces a PLAN; a downstream arc authors files / performs eviction." |
| **AR-2** home-of-record | 2 | C9 + C1 | **ACCEPT (co-signed)** | **HARDENING_PLAN = home-of-record for `tools/hooks/` EXECUTION units** (U-HK-30/40); **council WS-6 = a DEPENDENCY-CITE on D14** (owns only the P1-lands-WITH-D14 sequencing). **C1 third term:** `HOOKS.md` = a NEW read-only **lifecycle-topology descriptor** (C1×C2×C7) that *describes* the 3-in/4-out boundary map — it does **not** build/modify any hook body; it re-derives from `settings.json`, never the reverse. Three artifacts, three owners, no fork. |
| **AR-3** version-chain X-AL-3 posture | 2 | C3 | **ACCEPT** | Scope the folder-architecture remedy to **non-canonical copies only**; route execution through the X-AL-3 escape-hatch (clearance marker / `design-phase-direct` label per CLAUDE.md §4.4); name that EXECUTING it (later arc) requires **design-phase posture**, not mode-agnostic. As a *plan* it is additive-safe. |
| **AR-4** FM-H severity | 2 | C3 + C9 | **ACCEPT (sharpened — see §C)** | Re-rate **two-dimensional: consequence-HIGH / incidence-UNCONFIRMED**. Sequence as 3 gated steps: (1) **detection-first** (C3 probe: does a concurrent-write conflict actually occur?); (2) **rollback-boundary confirm — RESOLVED NEGATIVE this session** (§C); (3) **build serialization only if step 1 observes the race** (C3 flock/lease). Lane: C9 surfaces gap + existence-verdict; C3 owns serialization + durability remedy. |
| **AR-5** proportionality | 2 | C2 + C3 + C5 + C7 | **ACCEPT** | Apply the cluster-2 §1.11 filter the council had only *named*. **Unified MVP slice in §D.** Each WS ranks load-bearing-vs-defer; the deferred tail is explicitly marked optional/trigger-gated. |
| **AR-6** cache multipliers | 1 | C2 | **ACCEPT** | Tag "1.25× write / 0.10× read" **[MODERATE — Anthropic pricing, research §2.3, not re-isolated]**; keep the qualitative cache-detonation claim **[HIGH]** (self-grounded: §2 edited on 60/60 recent commits). |
| **AR-7** WS-6 credit/build split | 1 | C9 + C1 | **ACCEPT** | Split WS-6: **6a CREDIT** (no work — `postcompact-reinject.sh` + `context-recovery.sh` already conform to §7.2, verified) vs **6b BUILD** (owed — D14 U-HK-30/40 + the `context_budget_exceeded` mode). Mark the split in WS-6 *and* in the `HOOKS.md` state-OUT boundary table. |
| **AR-8** secrets / new injectors | 1 | C2 + C7 | **ACCEPT** | Re-state the secrets pre-check: "No P1–P6 commitment, **nor any new WS-2 version-state injector, nor any WS-5 health hook**, places secret material in prefix or suffix." Verified: existing sibling injectors carry only roadmap/version/health strings — zero secret material (structure-not-content). |
| **AR-9** finding-count audit | 1 | orchestrator | **RESOLVED** | Per-voice tally audited: C2=5, C3=6, C1=5, C5=5, C7=5, C9=5 = **exactly 31**. The stated count holds; no count-drift. |
| **Missed: C5↔C9** gate vs degradation-mode | (missed) | C5 + C9 | **RECONCILE — compose (§B)** | The G1 `--check` gate (CI/PR-time) and the `context_budget_exceeded` mode (session-runtime) govern **disjoint surfaces** → compose without contention; never-halt binds only runtime. **Closes the adversarial's own missed-tension #1 structurally.** |
| **Missed: AGENTS.md auto-load** | (missed) | C2 (+ C1 confirm) | **ACCEPT + RESCOPE** | Empirically verified (C2 + C1 independently): no top-level orientation doc exists at root; **Claude Code auto-loads only `CLAUDE.md` + its `@import` chain** (not `AGENTS.md`). RESCOPE WS-2: prefer `ARCHITECTURE.md` as the canonical anchor; if `AGENTS.md` is kept (cross-runtime hedge), constrain to a thin pointer; **forbid `@import`-ing any WS-2 anchor into `CLAUDE.md`** (the one prefix-forcing path — currently satisfied: zero `@import` lines). |

---

## B. Cross-cutting coherence (Stage 2c — the standing cross-read step)

All four checked seams returned **COHERE** (genuine cross-voice confirmation, not orchestrator-stitched):

1. **C1 × C2 — WS-2 / `HOOKS.md`:** COHERE. `HOOKS.md` is a NEW additive JIT-navigable file with **three orthogonal lanes**: C2 owns loading/prefix-placement (never `@import`-ed, never auto-loaded), C1 owns topology content (the 3-in/4-out boundary map + the single-sited termination contract + the three-halt-semantics disambiguation), C7 owns the observability-anchor overlay.
2. **C5 ↔ C9 — gate vs degradation-mode:** COHERE, **byte-aligned**. C5's G1 `--check` gate (CI/PR-time, `exit 1`, modeled on `substitution_ledger --check`) and C9's `context_budget_exceeded` mode (session-runtime, observe→degrade→continue) are **surface-disjoint** → compose without contention. The never-halt lock (CHARTER §2) binds only the runtime surface; the CI gate is explicitly forbidden from acting as an in-loop blocker. **This is the cross-cutting pass's headline win** — it structurally closes the tension the adversarial reviewer only suspected.
3. **C3 ↔ C9 — FM-H:** COHERE. Unified resolution: consequence-HIGH/incidence-unconfirmed; 3 gated steps (detect → confirm-rollback-boundary → serialize-only-if-observed); lane split (C9 surfaces gap + existence-verdict; C3 owns serialization + durability remedy). No FM-J leak (neither voice authors the other's mechanism).
4. **C7 × C2 × C5 — unified MVP slice:** COHERE. C7's WS-5 MVP (single mid-session byte-budget surface; full 5-state dashboard deferred) consolidates with C2's (WS-1 + G1 + WS-6/D14 + X) and C5's (`{G1}`, defer G2–G4) into one consistent slice (§D).

---

## C. NEW finding surfaced by the cross-cutting pass (genuine cross-read value)

**The out-of-worktree durable memory store is NOT git-versioned.** C9 verified empirically this session: `git -C ~/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory rev-parse` → **not a git repository** (no `.git` up the tree). Consequence:

- **CLAUDE.md §12.5.1's claim "Provenance lives in git history at the global memory store" is FALSE at HEAD** for that store. A deleted/lost-update MEMORY.md entry is **currently unrecoverable** — there is no rollback boundary (the worktree's Tier-2 git boundary does not cover this out-of-tree path).
- This **elevates FM-H's consequence to HIGH** (even though incidence stays UNCONFIRMED — no concurrent-write event observed; single-worktree this session). It is the load-bearing fact under the "X" workstream.
- **Plan implication (DESIGN.md):** the FM-H remedy is two-part — (a) C3 durability remedy = **version/snapshot the memory store** (establishes the missing rollback boundary), gated behind (b) the detection step. Also: **CLAUDE.md §12.5.1 carries a stale/false claim** — noted as a finding for the downstream execution arc (this plan-only arc does not edit CLAUDE.md content).

This finding did not exist in Stage 1 or Stage 2b — it was produced **only** because C9 and C3 cross-engaged on the FM-H seam in Stage 2c. It is the concrete evidence that the cross-cutting synthesis step the operator requested adds real value.

---

## D. The reconciled PLAN-shape (v2) — the input Stage 3 (Codex + advisor) evaluates

**Plan/execute boundary (AR-1):** every WS below is a **plan for a downstream execution arc**. This arc authors no `/`-level file and performs no CLAUDE.md eviction.

**MVP slice — load-bearing core (build first):**
- **WS-1** — CLAUDE.md altitude extraction + static/dynamic split (evict §2 provenance; target ≤~40KB). *The cost win.*
- **WS-2 (load-bearing half)** — SSOT pointer + `design-substrate/INDEX.md` (artifact→canonical-version). *Causally upstream of the §2 bloat.*
- **WS-4 G1** — context-doc byte-budget `--check` gate (CLAUDE.md + MEMORY.md; `exit 1` over cap; modeled on `substitution_ledger --check`, CI/PR-tier). *The gate that holds the WS-1 split.*
- **WS-5 (load-bearing half)** — the single **mid-session byte-budget surface** (UserPromptSubmit/StatusLine), tied to G1.
- **WS-6/D14** — recovery-completeness co-requisite (cite HARDENING_PLAN U-HK-30/40; **P1 lands WITH D14**, per T4). Split 6a-credit / 6b-build.
- **"X" (detect-gated)** — FM-H: detection step first; version/snapshot the memory store (consequence-HIGH per §C); serialization only if the race is observed.

**Deferred tail (proportionality filter, cluster-2 §1.11 — optional / trigger-gated):**
- WS-2 top-level orientation docs beyond the SSOT pointer (`ARCHITECTURE.md`/`HOOKS.md` content) — proportionate-but-deferrable (HOOKS.md itself is C1×C2×C7, JIT-navigable, never `@import`-ed).
- WS-3 retention: enforced MEMORY.md compaction = MVP-adjacent; `.harness/` Tier-5 archival + checkpoint-store-asymmetry reconcile = defer-candidates.
- WS-4 G2 (clearance-marker schema gate), G3 (ledger-shape gate), G4 (freshness-gate-teeth) — defer-with-triggers (G1 is the only load-bearing gate).
- WS-5 full 5-state dashboard health surface — defer (the mid-session byte-budget surface is the MVP).

**Standing disciplines folded in:** secrets pre-check covers new WS-2/WS-5 injectors (AR-8); cache multipliers tagged [MODERATE], qualitative claim [HIGH] (AR-6); WS-6 credit/build split (AR-7); version-chain remedy scoped to non-canonical copies via X-AL-3 escape-hatch at design-phase posture (AR-3).

---

## E. Reconciliation status

**Adversarial ⟷ Council: reconciled-to-zero.** No REBUT; all findings ACCEPT/RECONCILE-compose; all cross-cutting seams COHERE; AR-9 count audited (31); one NEW finding (§C) integrated. The §2-gate ("close before handoff") is **MET**.

**Next (loop step 3): Codex + advisor handoff** — the two decorrelated evaluators assess this reconciled PLAN-shape (§D) → `03-codex-advisor/`. Then **codex/advisor ⟷ council reconcile-to-zero** (loop step 4), then the **adversarial #2 gate** (loop step 5) → DESIGN.md.
