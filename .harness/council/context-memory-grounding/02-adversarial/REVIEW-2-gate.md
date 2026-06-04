# Adversarial #2 GATE — final review (Stage 4)

*harness-adversarial-reviewer as a dedicated agent (genuine invocation), bounded confirmation gate on the candidate DESIGN.md. Run `wf_aa4d14fb-801`.*

---

The `research §2.2.2` cite resolves: cluster-2 (context/prompts/memory) §2.2.2 "Canonical sources, deeply engaged" (line 198), and line 208 specifically names "Chroma context-rot ... empirical degradation curves" — exactly the lost-in-the-middle / U-shaped attention substrate DESIGN.md §5 cites. The cite is real and on-topic (DESIGN.md is a context/memory arc → cluster-2 is the correct cluster per the research-citations mapping). **Not a phantom cite.** ✅

All checks complete. I have a fully-grounded verdict: every CA/AR closed (genuine, not nominal), all empirical claims verified, WS-0 falsifiable with one optional grader-blinding sharpening, anti-bloat self-applied, hard-lane honored, no new Class-1. Composing the gate verdict now.

## Adversarial #2 GATE verdict

### Verdict: **CLEAR-TO-COMMIT**

DESIGN.md closes the loop. Every CA-1..CA-7 and the AR Class-2 set (AR-1..AR-5) is addressed **structurally, not nominally**; the keystone WS-0 is a genuinely falsifiable gate; the anti-bloat discipline (CA-2) is self-applied — including by the process itself (this single-reviewer gate IS the collapsed Stage-4 that CA-2 mandated, not a 6-agent fan-out). No Class-1 halt, no X-AL-3 violation, no phantom cite. One optional Class-2-or-3 sharpening (grader blinding) is noted for the execution arc; it does not block commit. I checked hard for the opposite failure — manufacturing a finding to look rigorous (skill-FM-A, the CA-2 irony) — and declined.

---

### CA/AR closure (per-finding)

**Codex/advisor findings (CA-1..CA-7):**

| CA | Finding | Closure | Where in DESIGN.md |
|---|---|---|---|
| **CA-1** | Drift-disconnect (the load-bearing one) | **CLOSED — genuine** | §2 reframes the success criterion to **measured drift-reduction**, byte≤cap explicitly demoted to leading-indicator. §3 WS-0 defines the 6-class taxonomy + counterfactual probe. §5 WS-1 carries a first-class **keep/position half** (attention-positioning, not eviction byproduct). The PLAN is now drift-connected, not byte-connected. |
| **CA-2** | Governance-native bloat irony | **CLOSED — genuine, self-applied** | §1 names it ("the de-bloating effort must not itself become governance-bloat"); §4 is a 7-row MVP; §6 deferred tail "large on purpose"; DESIGN.md itself is ~115 lines. *And the process honored CA-2's "collapse Stage-4" — this is a single reviewer, not a fan-out.* |
| **CA-3** | Verify-before-evict | **CLOSED** | §5 WS-1 precondition: (a) extract live invariants, (b) dependency-scan grep for §2-cell refs, (c) archive target must be **verified-already-git-versioned**. |
| **CA-4** | Memory rollback load-bearing | **CLOSED — resolved toward Codex** | §4/§5 X-min = minimal recoverability (snapshot/version + atomic writes + stale-base detection) in MVP; locking deferred + trigger-gated. Detect-only correctly rejected. |
| **CA-5** | G1 guardrail-not-religion | **CLOSED** | §5 WS-4 G1: effective-loaded-context byte-sum, warn-then-hard-fail, explicit override/waiver, CI/PR-time not in-loop (C5↔C9 surface-disjoint). |
| **CA-6** | MEMORY.md compaction → MVP | **CLOSED** | §4 WS-3a promoted to MVP; over-cap claim (27,051B > 24,400B) **verified exact at HEAD**. |
| **CA-7** | Reconciled-to-zero ≠ correctness | **CLOSED** | §2 states it plainly; §10 reaffirms the PLAN is falsifiable by the WS-0 probe, not by council agreement. |

**Adversarial #1 Class-2 set (AR-1..AR-5):**

| AR | Finding | Closure | Where |
|---|---|---|---|
| **AR-1** | Plan/execute boundary | **CLOSED** | §0 banner + per-WS `Deliverable-of-THIS-arc` column (§4) + §9 hard-lane + §10 handoff. |
| **AR-2** | Home-of-record (no fork) | **CLOSED — the decision is MADE** | §7: HARDENING_PLAN owns hook execution units (D14 U-HK-30/40); council PLAN owns governance layer + cites D14 as WS-6 dependency; HOOKS.md re-derives from settings.json. Three artifacts, three owners. |
| **AR-3** | Version-chain X-AL-3 posture | **CLOSED** | §5 X-min note + §9: non-canonical copies only, X-AL-3 escape-hatch (clearance marker / `design-phase-direct`), design-phase posture named for execution. |
| **AR-4** | FM-H severity re-rate | **CLOSED** | §5 X-min: consequence-HIGH / incidence-unconfirmed; detection-gated; locking deferred. §6 X-full trigger = observed concurrent-write race. |
| **AR-5** | Proportionality filter (apply, don't just name) | **CLOSED — genuine** | §4 MVP / §6 deferred-tail split applies the cluster-2 §1.11 filter; G1 named as the only load-bearing gate, G2–G4 + 5-state dashboard deferred. |

AR-6..AR-9 (Class-1 inline) all folded per round2 §A (cache multipliers, WS-6 6a/6b credit/build split at §6, secrets pre-check, count-audit). No miss.

---

### WS-0 falsifiability verdict

**FALSIFIABLE — sound. This is a real gate that can fail, not ceremony.** Pressure-tested against all four named axes:

- **Counterfactual baseline:** ✅ mandatory — Arm A = current `CLAUDE.md` @ HEAD (= v(N-1), frozen); Arm B = slimmed. Single-arm "feels better" explicitly rejected as FM-H.
- **Binary taxonomy:** ✅ D1–D6 are objective, transcript-checkable yes/no incidents (not a continuous "rot feeling"; no model-judge; no eval harness).
- **Human grader:** ✅ Robert tallies per-class incidence (the human floor; avoids meta-eval recursion).
- **Real pass condition that can fail two ways:** ✅ Arm B ≤ Arm A on **every** class AND < on ≥1 class — fails on any regression OR on zero net reduction. A regression maps to the CA-3 over-eviction failure, caught empirically. §8 step 4 specifies the restore-and-re-measure loop.

**One optional sharpening (does not block):** round3-c8 carried a conditional — "the labeler doesn't know which arm should win **if arms are de-identified**" — that **dropped out of DESIGN.md §3**, which now has a *single, unblinded* grader who is also the slim-author (confirmation-bias vector on the exact comparison that is the gate). What dampens it to non-blocking: D1/D2 (wrong-canonical-artifact, stale-rule) are objective regardless of which arm the grader thinks they're scoring — c8's deeper defense largely immunizes the verdict. Classifiable as **Class-3 informational** (cheap exec-arc hardening: de-identify/shuffle arm labels before grading) or arguably **Class-2 fold-one-line** (a reconciled refinement was dropped between round3 and DESIGN.md). Either way it does **not** halt and must **not** grow the probe into a stats apparatus (that would be the CA-2 irony). Recorded as residual below; the execution arc should restore the de-identification line.

---

### Anti-bloat self-application verdict

**PASS — held on itself, and the strongest evidence is structural.** DESIGN.md is ~115 lines; §4 MVP is a 7-row slice each carrying a `cost/drift/governance` tag + a `Deliverable-of-THIS-arc` note; §6 deferred tail is deliberately dominant ("large *on purpose* — the anti-bloat discipline the out-of-family reviewer demanded"), every entry trigger-gated. The MVP is genuinely drift-connected (each row ties to a D-class or the gate that holds the split), not an instrument-everything surface. Critically, **CA-2's meta-instruction to "collapse Stage-4" was honored by the process itself** — this gate is a single decorrelated reviewer, not another 6-voice fan-out. DESIGN.md is a proportionate plan about de-bloating, not a bloated one.

---

### New Class-1? **None.**

Walked every v3-introduced surface:
- **Empirical claims** — all three load-bearing facts verified at HEAD: MEMORY.md 27,051B (exact), zero `@import` lines in CLAUDE.md (exact), memory store not-a-git-repo (confirmed).
- **§12.5.1 stale-claim** — DESIGN.md's quote resolves to CLAUDE.md:651 verbatim (modulo lowercase "p"); the claim it flags IS false-at-HEAD; correctly **noted-for-execution-arc, not edited here**. Not a phantom cite.
- **`research §2.2.2`** (the one v3 cite not cleared at adversarial #1) — resolves to cluster-2 §2.2.2 (line 198/208, Chroma context-rot / empirical degradation curves); correct cluster for a context/memory arc. Not a phantom cite.
- **Hard-lane** — `git status` shows only `?? .harness/council/` untracked: zero `design-substrate/**`, zero `harness-*/src`, zero `R-NNN`, zero deletion, zero CLAUDE.md content edit. WS-1 eviction correctly framed as **navigation, not deletion** (§5/§9), X-AL-3-safe because CLAUDE.md is mode-agnostic per §11.2:484 (verified). Version-chain remedy correctly scoped to non-canonical copies via the X-AL-3 escape-hatch at design-phase posture.

No contradiction, no additive-only/X-AL-3 violation, no out-of-scope edit-mandate, no phantom cite introduced by the v3 revisions.

---

### Residual

- **[Class-3 informational — exec-arc hardening, non-blocking]** WS-0 grader is single + unblinded (Robert is both slim-author and ≤-grader); round3-c8's "de-identify arms before grading" conditional dropped out of DESIGN.md §3. Dampened by the objective D1–D6 taxonomy. The execution arc should restore arm de-identification/label-shuffling before grading. **Does not block commit; must not be grown into a stats apparatus.**

Nothing else from any round is genuinely open. Adversarial #1 was CLEAR + Class-2-revisions (all 5 folded); round2 reconciled-to-zero; round3 CA-1..CA-7 reconciled-to-zero (per-voice residuals all "none"); the settled cites (U-HK-30/40 etc.) are not re-litigated. **CLEAR-TO-COMMIT — DESIGN.md may commit as the arc's PLAN; the one residual is an optional execution-arc note, not a fold-before-commit requirement.**