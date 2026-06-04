# Stage 1 — Council Deliberation: Context & Memory Layer Grounding

**Arc:** council-context-memory-grounding · **Stage:** 1 (council convening) · **Date:** 2026-06-03
**Mechanism:** genuine 6-voice invocation (each voice ran as a dedicated agent adopting its own `cN` council skill + reviewing the repo through its lens — NOT core-agent ventriloquism). Primaries C2/C3 generated independently; consultants C1/C5/C7/C9 reacted to the primaries' real output. Orchestrator (this file) composes the envelope + probe-resolves tensions.
**Verbatim contributions:** `contributions/c{2,3,1,5,7,9}.md` (the voice text the envelope wraps; positions below are not paraphrased away).

---

## Convening Block

- **Question type:** cross-cutting (multi-axis foundational grounding of the harness's own context/memory PROCESS machinery against the intended interpretable-context + IS read/write spec).
- **Voices convened:** C2 (primary), C3 (co-primary), C1 (consultant), C5 (consultant), C7 (consultant), C9 (consultant). *(6 voices — explicit operator override above the nominal cap of 5, justified by a genuinely six-axis foundational topic per CHARTER §4.)*
- **Routing rationale:**
  - **C2** — the layer's center: what enters context, CLAUDE.md altitude/budget, folder-architecture-as-interpretable-context, JIT/loading discipline, context-rot.
  - **C3** — durable memory: MEMORY.md/memory/, the five durability tiers mapped onto the repo, checkpoints, ledger-bloat/pruning, the across-turn store.
  - **C1** — the session/loop lifecycle that drives context in/out (the hooks as the runtime execution of the read/write seam; loop termination).
  - **C5** — the conformance-contract surfaces for the durable artifacts + doc single-sources (is there a gate, or only prose?).
  - **C7** — legibility of context/memory state to agent + operator (the hooks as observability; what's surfaced vs silent).
  - **C9** — durability/recovery of context+memory across crash/compaction/handoff (the D14 layer; recovery as the discontinuity-triggered read seam).
- **Voices considered, not convened:** C4 (Skills/tools *content* — loading-discipline is touched but content is out of scope; handled-by-reference inside C2); C6 (model routing — orthogonal to context/memory process machinery); C8 (eval methodology/thresholds — handled-by-reference; C5/C7/C9 each surfaced *measurables*, C8 owns whether the thresholds are well-chosen); C10 (action-safety — the locked paid/secret/destructive deny-list is preserved operating-rule content, enforced at `permission-guard.sh`; handled-by-reference); C11 (HITL primitive + dashboard UX — handled-by-reference; surfaced by C7 as a C7↔C11 co-primary on the dashboard health surface).
- **Pre-check status:** see CCR below.

---

## Cross-Cutting Receipt (CCR) — slim

| # | Concern | Touched | Owner status | Pre-check note |
|---|---|---|---|---|
| 3 | Token economy & cost | Yes | convened (C2) | The §2 provenance dump cache-detonates the ~334KB Tier-1 prefix on ~every spec PR — the dominant cost lever of the whole layer (probe: CLAUDE.md=341,611B; 60/60 recent commits touch it). |
| 4 | Reliability & failure containment | Yes | convened (C9) | Recovery-completeness is unpriced against the slim-down; no `context_budget_exceeded` degradation mode; the cross-worktree shared-MEMORY.md write race (FM-H) is silent by construction. |
| 2 | Observability hooks | Yes | convened (C7) | Session-*progress* state is richly instrumented; context/memory-*health* state (CLAUDE.md budget, ledger growth, checkpoint growth, write-collision, cache-warmth) is largely un-surfaced. |
| 5 | Eval-ability | Yes | handled-by-reference (C8 §"C7/C8 boundary"; not convened) | Each voice surfaced measurables (bytes≤cap, marker-schema-conformance, recovery-pointer-present-rate); whether the thresholds/caps are well-chosen on a holdout is C8's population claim — held out of lane. |
| 6 | HITL & local-first | Yes | handled-by-reference (C11; not convened) | Dashboard UX is a C7↔C11 co-primary; the durable memory store living *outside* the worktree is the local-first surface that breaks worktree isolation (FM-H). Locked never-halt/defer-and-continue/prefer-free-ollama preserved, not relitigated. |
| 1 | Security & blast radius | Yes | handled-by-reference (C10 `permission-guard.sh`) | n/a for secret material — no P/G/R commitment places a secret in prefix or suffix; the structure-not-content discipline the hooks already follow (zero content captured) IS the security-relevant property (C7). Locked deny-list preserved. |

---

## Probe-first log (orchestrator empirical resolution, per council-orchestrator §5)

Before surfacing tensions, three disputed/load-bearing claims were probed at primary source this session:

1. **Is the MEMORY.md byte-cap a gate or advisory? (resolves C5↔C2)** — `session-end-cleanup.sh:53` prints `OVER CAP, compact` inside a `} > "$REPORT" … || true` block (no exit); `loop-gc.sh:56` sets a flag string then `exit 0` (line 59). **Advisory — routes on nothing.** By contrast `tools/substitution_ledger.py` `--check` carries `exit 1 on any violation` (`:193/:206`, `main()->int`). **→ C5 is empirically correct: the byte-budget must mirror the `--check` gate, not the advisory cap.**
2. **Is CLAUDE.md's prefix actually edited every PR? (strengthens C2 cost claim)** — `wc -c CLAUDE.md` = **341,611 bytes** (exact match to C2's measurement). `git log -60 -- CLAUDE.md` on this branch = **60 of 60** commits touch CLAUDE.md (C7 measured 37/60 on main). **→ the edit-cadence cost proxy is saturated; the cache-detonation mechanism is confirmed and then some.**
3. **Does cache-hit-rate have a dev-loop observability home? (resolves C2 signal-b vs signal-d, via C7)** — no hook consumes `cache_*`/usage from Claude Code hook JSON (verified by C7); cache attribution lives in H_T *product* OTel, not the dev loop. **→ C2's eval signal (b) "static-prefix cache-hit-rate" is a constraint, not a measurable; use the git-derivable §2-edit-cadence proxy (signal d) instead.**

---

## Voice contributions (primary first; full text in `contributions/`)

**C2 — Context Engineering (PRIMARY)** · first cite: IS spec §C-IS-07 §7.2 (C2-pole read contract).
The harness ships a Selective/Bounded/Navigation-mediated read contract for its *runtime* and then force-loads its entire delta-version provenance ledger into its own re-attended-every-turn Tier-1 prefix. CLAUDE.md = 341,611B; **§2 = 277,298B = 81%**, concentrated in 3 cells (CP/OD/CXA, lines 80/81/92) of ~52–55KB each. The disease is **altitude + placement**, not line count: operating-rules (keep) vs navigation-anchors (inflated) vs provenance/audit-trail (evict — already redundant in git + the spec files). The bloat and the missing SSOT pointer are the *same* defect. 6 commitments: P1 static/dynamic split (≤~40KB), P2 altitude, P3 JIT provenance, P4 byte-budget, P5 navigation infra, P6 MEMORY.md index discipline. **Explicit lane note: do NOT delete the 29 versioned copies — at-rest retention is intended (C3 + locked convention); fix = navigation + altitude extraction, never retention.**

**C3 — State, Memory & Persistence (CO-PRIMARY)** · first cite: IS spec §C-IS-02 five-tier model + §C-IS-07 read/write pair.
Forecloses the wrong gap up front: the `.harness/` ledger is **not** defective for being un-hash-chained (the hash-chain is the H_T *product* contract for a `state.jsonl` that doesn't exist yet; git commits already are a parent-SHA chain). The intended frame is the **five-tier methodology** (append-only + *mandatory* pruning-axis-per-tier + concurrent-write contract); every gap is **FM-G (pruning silent)** or **FM-H (concurrent-write silent)**. Five-tier as-is map: three of five tiers have **no enforced retention contract**. Two HIGH findings: **MEMORY.md over-cap with no enforced pruning** (27,051B/24,400B), and **the durable memory store lives *outside* the worktree → all worktrees + main share one MEMORY.md with no write serialization → lost-update race (FM-H)**. `substitutions.yaml` is the one place the methodology is correctly applied — the model for the rest. Version-chain proliferation = tier-confusion (git Tier-2 already holds history) → a *folder-architecture* remedy, never content edits.

**C1 — Orchestration & Control (consultant)** · first cite: IS spec §C-IS-07 §7.1+§7.2.
The connective claim no other voice makes: **the hook lifecycle IS the runtime topology that executes the C-IS-07 read/write contract** — 3 context-IN boundaries (SessionStart/UserPromptSubmit/PostCompact) + 4 state-OUT (PreCompact/SessionEnd/Stop/PostToolUse). Reframes hunch #5: the missing artifact is a **lifecycle-TOPOLOGY contract**, not a hook inventory. The loop *amplifies* C2's cost: `HARNESS_LOOP_MAX=25` auto-continued turns each re-attend the ~334KB prefix → C2's warming fix has outsized value under loop mode. The loop **termination contract is SOUND** (cap=25 guarantees termination) but **distributed across 5 surfaces**. Sharp sub-finding: **three distinct control semantics share the word "halt"** — drift→HALT (integrity reconcile) / `.loop-halt` (work-exhaustion) / never-halt (posture) — disambiguate by name (surface-only; don't relitigate the locked posture).

**C5 — Validation Contract (consultant)** · first cite: IS spec §C-IS-07 §7.1+§7.2 + §6.4 `verify_chain`.
The harness wrote itself a conformance gate (`verify_chain`) for its product state and runs its process state on prose. **Three-tier gate-conformance map:** Tier-1 GATED (exactly one real gate — `substitution_ledger.py --check` — excellent, the model); Tier-2 ADVISORY-ONLY (MEMORY.md cap + roadmap-freshness — checked but route on nothing); Tier-3 UNGATED (CLAUDE.md no gate; clearance markers have a `TEMPLATE.md` schema that nothing validates). **The C2/C3 split is only durable if expressed as a `--check` gate — that §2 grew to 277KB is *because* the budget was prose, and prose doesn't fail a build.** 4 gate contracts G1–G4. Refines C2's P4: mirror the `--check` gate, not the advisory cap (probe-confirmed).

**C7 — Observability (consultant)** · first cite: IS spec §C-IS-07 §7.2.
The hooks are the runtime-introspection layer over the repo's own context/memory state, correctly **structure-not-content** (zero content captured). **Legibility coverage map:** session-*progress* state richly instrumented; context/memory-*health* state largely un-surfaced — 5 of the highest-value remediation targets have **zero legibility today**. An observability requirement is *logically prior* to any retention policy or cap value (you can't manage what you can't see). The MEMORY.md cap fires only at session *boundaries*, never mid-session. Probe: cache-hit-rate has no dev-loop home; the git-derivable §2-edit-cadence proxy carries the cost story instead. Dashboard surfaces progress, not health (C7↔C11).

**C9 — Reliability & Recovery (consultant)** · first cite: IS spec §C-IS-07 §7.2 (recovery = the discontinuity-triggered direction of the read seam).
Headline: **recovery-completeness is a CO-REQUISITE for C2's slim-down, not a follow-on** — slimming the always-present prefix converts the recovery/reinject machinery from a redundant backstop into a load-bearing dependency. Three-way recovery maturity: compaction recovery **BUILT + sound** (credit it); output-cap truncation recovery **UNBUILT** (the gap); crash/handoff **SPLIT**. **Cite-don't-duplicate:** the output-cap gap is already scoped in `HARDENING_PLAN.md` as **D14 / U-HK-30 + U-HK-40** — the council PLAN *adopts* that scoping, sequences it as the P1 co-requisite, and declares the home-of-record so the two plans don't fork on `tools/hooks/`. New C9-shaped finding: no `context_budget_exceeded` degradation mode (context-rot is silent). Recovery re-hydration must hold to §7.2 (pointer + revalidation, never re-bloat) — `postcompact-reinject.sh` already conforms; credit it.

---

## TENSION block

### T1 — C2 ↔ C3: where version-provenance lives / how much enters the Tier-1 prefix (T-perm-2)

- **Parties:** C2, C3
- **Issue:** The CLAUDE.md §2 provenance — at-rest durable audit trail (C3) vs within-turn re-attended prefix content (C2).
- **Positions:**
  - **C2:** Provenance is C3's at-rest concern (git + the delta-only-preserve spec files already hold it verbatim); it must NOT occupy the re-attended-every-turn static prefix — JIT-load it (navigation-mediated per §7.2) only on a version question. C2 owns the read-into-context / prefix-placement decision; the §2 cells dumping ~277KB every turn is the read seam over-loading working memory.
  - **C3:** Owns the at-rest write/prune discipline; flags CLAUDE.md-at-rest has no pruning cadence + no single-writer contract; explicitly does NOT specify what to cut (that would be FM-A). The disagreement is purely WHERE it lives and HOW MUCH pre-loads, not WHETHER it is retained.
- **Stakes:** If resolved toward eager-prefix, the cache never warms and per-turn cost stays pathological; if resolved toward eviction without a navigation surface, version-canonicality becomes less discoverable (the `[[wrong-version-read-delta-only-baseline]]` hazard). Both voices already agree it is WHERE-not-WHETHER and route "what to cut" to council co-primary.
- **Status:** **promoted to Layer 3 (permanent tension — T-perm-2).** H_T-resolved at the IS read/write boundaries (C-IS-07 §7.1/§7.2); not relitigated. **Operative resolution for the PLAN:** the cut-list is a co-primary C2(attention-budget) × C3(at-rest storage) decision — sequence it as a joint step, do not let either voice resolve it alone.

### T2 — C5 ↔ C2: which precedent to mirror for the context-doc byte-budget

- **Parties:** C5, C2
- **Issue:** C2's P4 says give CLAUDE.md "an automated byte-budget + surfacing hook, mirroring the MEMORY.md 24,400B cap precedent." C5 says the MEMORY.md cap is itself advisory.
- **Positions:**
  - **C2:** The MEMORY.md cap is the working precedent proving the fix-pattern; mirror it for CLAUDE.md.
  - **C5:** The MEMORY.md cap *routes on nothing* (prints then `exit 0`) — which is exactly why MEMORY.md is over cap and "only partially loaded." Mirroring an advisory check yields a second advisory check. The correct precedent is `substitution_ledger.py --check` (exits 1). Both MEMORY.md and CLAUDE.md need a `--check`-tier gate.
- **Stakes:** An advisory budget decays back to prose (the mechanism that let §2 reach 277KB); a `--check`-tier gate holds the C2/C3 split durably.
- **Status:** **surfaced + probe-resolved (in C5's favor).** Probe: the cap is advisory (`session-end-cleanup.sh:53` / `loop-gc.sh:56` route on nothing); `substitution_ledger --check` exits 1. **PLAN adopts:** the byte-budget is a `--check`-tier gate (G1), not a second advisory hook. C2 correctly identified the artifact + need; C5 corrected the enforcement tier. The cap *value* stays C3's; the cut-list stays C2's; the *gate* is C5's.

### T3 — C7 ↔ C2: legibility vs attention-budget on the provenance eviction

- **Parties:** C7, C2
- **Issue:** C2's eviction of ~277KB provenance from the prefix trades an always-on legibility property (version-canonicality visible every turn) for prompt-cost.
- **Positions:**
  - **C2:** Eviction is the read-seam / attention-budget call (C2's lane); the cost case is decisive.
  - **C7:** The eviction is C2's to make, but it MUST be paired with a legibility-preserving navigation surface (a genuinely-navigable `design-substrate/INDEX.md` mapping artifact→canonical-version + a compact version-state line surfaceable cheaply via a dynamic-suffix injector) — otherwise "canonical = vN" becomes *less* legible after eviction than before.
- **Stakes:** Eviction without a navigation surface worsens the wrong-version-read hazard C3 named; eviction with one captures the cost win and keeps canonicality discoverable.
- **Status:** **surfaced (reconcilable co-requisite).** Not a blocker — C7's legibility-preservation is an additive constraint on C2's P1/P5. **PLAN adopts:** the eviction (P1) is bound to a navigation surface (P5) that is genuinely navigable, with a cheap version-state injector at the §7.2 read locus.

### T4 — C9 ↔ C2: sequencing of the prefix slim-down vs recovery-completeness

- **Parties:** C9, C2
- **Issue:** C2 costed the slim-down for cache/attention only; C9 flags an unpriced reliability consequence.
- **Positions:**
  - **C2:** Slim the prefix (334KB→~40KB) for the cost/attention win.
  - **C9:** Concurs on direction, but slimming the always-present prefix converts recovery/reinject from a redundant backstop into a load-bearing dependency. Recovery-completeness (HARDENING_PLAN D14 / U-HK-30+40) is therefore a **co-requisite sequenced WITH P1**, not a follow-on. *Calibrated:* the evicted content is provenance (recovery rarely needs it), so the eviction's own blast radius is modest — the load-bearing point is the principle (more JIT ⇒ recovery must be complete first).
- **Stakes:** Slim-first-then-recovery leaves a window where a compaction/crash mid-arc loses more than today; slim-with-recovery closes it.
- **Status:** **surfaced (sequencing flag, reconcilable).** **PLAN adopts:** WS-1 (slim-down) lands WITH WS-6 (D14 recovery wiring), not before it.

### T5 — C9 ↔ C3: recovery of the out-of-worktree shared memory store (C3↔C9 co-primary)

- **Parties:** C9, C3
- **Issue:** The FM-H cross-worktree write race (C3) + whether the out-of-worktree memory store has a recovery primitive (C9).
- **Positions:**
  - **C3:** Owns the store, the retention policy, and the write serialization that *prevents* the lost-update.
  - **C9:** Adds the partial-failure-recovery question C3's framing didn't close — the store lives in a *different* git repo than any worktree, so a corrupted/lost-update MEMORY.md is recoverable only if that path is itself versioned. C9 contributes the recovery-primitive existence check only.
- **Stakes:** Without a confirmed rollback boundary, an FM-H lost-update is unrecoverable.
- **Status:** **surfaced (clean C3↔C9 co-primary).** **PLAN adopts:** route the joint piece (store rollback + write serialization) to C3 as owner with C9 as recovery-primitive consultant; the PLAN confirms + names the memory-store rollback boundary.

### T6 — C1 ↔ C9: loop fault-handling-as-topology (T-perm-3)

- **Parties:** C1, C9
- **Issue:** The loop's defer-and-advance / self-heal / breaker-routes-to-fallback recovery posture is fault-handling-as-topology.
- **Positions:**
  - **C1:** Owns the loop SHAPE (where the recovery transition sits; the exit set; that a defer-and-advance branch exists).
  - **C9:** Owns what happens INSIDE a failed iteration (retry mechanics, backoff, breaker thresholds, idempotency).
- **Stakes:** The lifecycle-topology contract must name C9 as owner of in-iteration retry and stop at the boundary.
- **Status:** **known permanent (T-perm-3).** Surfaced, not relitigated; the topology doc names the boundary.

---

## Cross-voice convergence — the one-sentence diagnosis

**The harness authored a Selective/Bounded/Navigation-mediated read contract (C-IS-07 §7.2) and a `verify_chain` gate (§6.4) for its *product* state, and runs its own *process* context/memory state in violation of both** — provenance force-loaded into the re-attended Tier-1 prefix (C2), three of five durability tiers without an enforced retention contract (C3), exactly one real conformance gate (C5), context/memory-*health* state largely un-observable (C7), recovery-completeness unpriced against the slim-down (C9) — with the hook lifecycle (C1) as the under-documented control spine that already executes the read/write seam correctly. **The fix-patterns the repo needs all already exist in the repo** (`substitution_ledger --check`, the hook token-budget discipline, `postcompact-reinject` §7.2-conformance, the MEMORY.md cap precedent) — they are simply not applied to the context/memory governance layer itself.

## Emerging PLAN shape (bridge to DESIGN.md — to be red-teamed at Stage 2)

| WS | Workstream | Owner (co) | Consolidates |
|---|---|---|---|
| **WS-1** | CLAUDE.md altitude extraction + static/dynamic split (≤~40KB; evict §2 provenance to the durable store; JIT-load) | C2 (× C5 gate, C7 legibility, C9 recovery seq) | C2 P1/P2/P3 |
| **WS-2** | Navigation infrastructure / interpretable-context: SSOT pointers + `design-substrate/INDEX.md` + `ARCHITECTURE.md`/`AGENTS.md`/`WORKFLOW.md` + `HOOKS.md`-as-lifecycle-topology-contract | C2 × C1 (topology doc) × C7 (observability-fabric anchor) | C2 P5, C1 (topology), C7 |
| **WS-3** | Durable-memory retention contracts: enforced MEMORY.md compaction; `.harness/` Tier-5 archival policy (model on `substitutions.yaml`); reconcile checkpoint-store asymmetry | C3 (× C5 gates, C7 legibility, C9 mode) | C3 findings |
| **WS-4** | Conformance gates: promote advisory checks → `--check`-tier; clearance-marker schema gate; ledger-shape gate; freshness-gate-teeth decision (drift = HITL-recoverable) | C5 | C5 G1–G4 |
| **WS-5** | Context/memory-health observability: the 5 un-surfaced health states; mid-session surface; cache-efficiency via git-proxy; dashboard health | C7 (× C11 UX) | C7 findings |
| **WS-6** | Recovery completeness: adopt HARDENING_PLAN D14 / U-HK-30+40 (cite, declare home-of-record); `context_budget_exceeded` degradation mode; §7.2-conformant re-hydration; memory-store rollback boundary | C9 (× C3) | C9 R1–R5 |
| **X** | **FM-H cross-worktree memory-write serialization** (HIGH — affects this very arc) | C3 (× C9 recovery primitive) | C3 + C9 T5 |

**Hard lane discipline carried into the PLAN (all voices concur):** additive-only; the remedies are navigation + gates + observability + recovery + retention contracts — **never deletion of versioned copies, never edits to design-substrate *content*, never edits to `harness-*/src` or the R-NNN roadmap.** The version-chain proliferation is fixed by *folder-architecture* (SSOT pointer / archive), not content removal.

## What Stage 2 (adversarial reviewer) should red-team

1. **Is the §2-provenance eviction (WS-1) safe** given the delta-only-preserve-verbatim convention + X-AL-3? The provenance is canonical; does evicting it from CLAUDE.md (while it lives in git + the spec files) violate any convention, or is it purely a navigation move?
2. **Does the FM-H cross-worktree write race actually manifest**, or is it mitigated by single-session reality / gstack serialization? (C3 rates it HIGH; verify the threat model.)
3. **The cache-detonation framing** depends on where Claude Code places `cache_control` — C2 hedged this ("the design-level claim holds regardless"). Is the cost claim robust if the literal breakpoint isn't where C2 assumes?
4. **Scope-coordination with the U-HK `HARDENING_PLAN`** (C9 R2): do this council PLAN and the U-HK plan fork on `tools/hooks/`? Which is home-of-record?
5. **Any recommendation crossing into design-substrate content / R-NNN roadmap / `harness-*/src`** (additive-only + X-AL-3 violation)?
6. **Over-engineering check:** are WS-4 gates / WS-5 observability proportionate to a solo-developer harness, or do they re-introduce the very bloat the arc is trying to remove? (cluster-2 §1.11 — four-tier memory separation "rarely paid back at solo-founder scale.")
