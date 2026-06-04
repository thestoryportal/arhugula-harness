# DESIGN — Context & Memory Layer Grounding + Alignment Plan

**Arc:** council-context-memory-grounding · **Version:** **v2 (evidence-enriched)** · **Status:** Round-5 COMPLETE — full loop reconciled-to-zero (council deliberation#2 → Phase-B cross-read → adversarial#1 → Codex + advisor → consolidated reconcile → adversarial#2 gate **CLEAR-WITH-FOLD**, both folds F-G1/F-G2 applied + verified at HEAD); **CLEARED-TO-COMMIT** · **Date:** 2026-06-04
**Produced by:** v1 — 6-voice council → adversarial#1 → adversarial⟷council (+cross-cutting) → Codex + advisor → codex/advisor⟷council. **v2 (Round 5)** — fresh `03-evidence/` research → 7-voice council (C2/C3 + C1/C5/C7/C9 + **C8**) deliberation #2 → Phase-B cross-read → adversarial#1 (E2) → Codex (out-of-family) + advisor (in-family) → consolidated council reconcile. Full ledger at `00-CHARTER.md` + `01-council/` + `02-adversarial/` + `03-codex-advisor/` + `04-reconciliation/`.

> **This is a PLAN, not its execution.** No `/`-level file written, no CLAUDE.md eviction performed, no `design-substrate/**` content / `harness-*/src` / `R-NNN` roadmap edited, no versioned copy deleted. A **downstream execution arc** performs the work; this PLAN tells it what to do and **how its success will be measured.** Additive-only.

---

## 0. Round-5 change-note (v1 → v2: what the fresh research changed)

v1 (committed) was reviewed against fresh research (`03-evidence/`: the empirical 169-note memory-graph + NotebookLM external canon — ICM/arXiv:2603.16021v2, Claude-Code cache mechanics, Letta-on-files, Zep temporal validity, eval-gates, an agent-file taxonomy). The governing tension was **proportionality-vs-canon**: the research recommends much machinery; this is a solo-dev harness. **All 7 voices resolved toward proportionality** — the enrichments are sharpens/riders of existing workstreams + one deferred gate; **zero new MVP workstreams**; a long canon-refusal list. Three decorrelated reviewers (adversarial, Codex out-of-family, advisor) confirmed CLEAR/SOUND-WITH-FIXES; Codex earned its keep (3 findings the Claude-family reviewers missed). **Net v2 deltas:**

- **§3 WS-0 gains an `INCOMPLETE-on-{D4,D6}` verdict** (the rare-class false-green fix — adopted over a minimum-exposure floor, which was rebutted as bloat) + a recall/artifact/continuation **grading codebook-lens**.
- **§5 WS-3a gains** the empirical **degree-keyed selection rule** (pin ≥5 / keep 1–4 / archive the 39 zero-inbound), a **bi-temporal supersede-mark** write-discipline, a **3-integer SessionEnd health-line rider**, and a **one-time hygiene** write of 2 already-dangling ≥4-ref pattern notes.
- **§5 WS-1 gains** the L1 deterministic pre-eviction assertion (scoped to dependency-scan-discovered invariants) + the cache-detonation cost framing demoted to a *reported leading-indicator* (git-§2-edit-cadence + G1 byte-delta; not `cache_read`, which has no dev-loop home).
- **§5 X-min gains** the FM-H *decentralized-handoff* sharpen (serialize at the store via OCC + git-as-state, not at a topology lead) + a named reinject-pointer-resolvability recovery requirement.
- **§6 deferred tail gains G-LINK** (link-integrity `--check`, DEFER→MVP-on-trigger) and the **recurring consolidation mechanism** (synchronous SessionEnd write-event).
- **Citation anchors folded** (no new work): ICM=arXiv:2603.16021v2; CoALA/Letta tier names; OCC/git-as-state; Dive-6 size/format norms.

v1's body is preserved in git; v2 is the operative plan.

---

## 1. Diagnosis (unchanged from v1 — the reframe that matters)

**Convergent council finding:** the harness authored a Selective/Bounded/Navigation-mediated **read contract** (`Spec_Information_Substrate_v1.md` §C-IS-07 §7.2) and a `verify_chain` **conformance gate** (§6.4) for its *product* state — and runs its own *process* context/memory state in violation of both: ~277KB of version-provenance force-loaded into the re-attended-every-turn `CLAUDE.md` prefix; durability tiers without enforced retention; one real conformance gate; context/memory-*health* state largely un-observable; the durable memory store not git-versioned. **The fix-patterns already exist in-repo** — they were never applied to the governance layer itself.

**The reframe (two decorrelated reviewers, independently):** the operator's pain is **drift during coding sessions**, not byte-count. **This PLAN's success criterion is measured drift-reduction (WS-0), not byte≤cap.** And the de-bloating effort must not itself become governance-bloat — every item earns its place against the drift metric; the deferred tail is large on purpose. *(Round 5 confirmed this discipline held: the fresh canon was overwhelmingly triaged citation-enriching/confirmatory; the structural temptations — ICM numbered-folders, CoALA dir-split, a consolidation daemon, an eval cascade, embedding-drift rot-scores — were all refused on solo + drift grounds.)*

---

## 2. Success criterion (falsifiable — this is the gate)

**WS-0 is the acceptance gate.** The PLAN succeeds iff the WS-0 before/after probe shows the slimmed governance layer **does not increase any drift-incident class** vs the current-HEAD baseline **and reduces ≥1 class** — **and the result is not `INCOMPLETE`** (§3). Reconciliation-to-zero across reviewers is a *coherence* property, **not** a correctness property — it removes contradictions; it does not validate the outcome. byte≤cap is an acceptable cheap *reported* leading-indicator (kept as the WS-4 G1 guardrail + a git-§2-edit-cadence proxy), **never** the acceptance gate.

---

## 3. WS-0 — Drift definition + use-the-product probe *(owner: C8; the success gate)*

**Drift = a countable per-session incident set** (binary, human-labelable from a transcript — no model-judge, no eval harness, no continuous "rot score"):

| # | Drift class | Binary check (1 if observed in the session) |
|---|---|---|
| D1 | Stale-rule use | applied a CLAUDE.md/MEMORY.md rule no longer current |
| D2 | Wrong-canonical-artifact | cited/used a non-canonical or wrong-version design-substrate artifact |
| D3 | Forgotten task-constraint | dropped a constraint the operator stated *this session* |
| D4 | Memory-pollution / context-poisoning | acted on a stale/false memory entry, or a bad write entered the store |
| D5 | Bad resumption | on resume, mis-derived next-action vs roadmap/checkpoint truth |
| D6 | Instruction-conflict | surfaced or silently resolved a contradiction between two loaded instructions |

**Probe (Husain error-analysis-first, solo-scale):** ~15–25 *real* coding-loop sessions across representative workflow classes — re-use existing `[[use-the-product-probe-pattern]]` sessions, do **not** author a synthetic corpus. **Two arms, counterfactual baseline mandatory:** Arm A = current `CLAUDE.md` @ HEAD; Arm B = slimmed (WS-1 output). **Grader = Robert (the human floor)** tallies D1–D6 per session → per-class incidence per arm. **De-identify / shuffle the arm labels before grading** (the grader is also the slim-author).

**Grading codebook-lens (Round-5, C8-E4 — a categorization aid, NOT synthetic tests):** when grading a real session, map the observed failure onto the binary D-class via the recall/artifact/continuation probe-types from eval canon (Dive-5): *recall* failure (a fact/rule didn't survive the slim) → D1/D4; *artifact* failure (agent unsure which files/version it touched) → D2/D5; *continuation* failure (multi-step task mis-resumed) → D3/D5. This makes the human label reproducible without adding a single test case.

**Pass condition (Round-5, C8 — the rare-class fix):** Arm B ≤ Arm A on every class AND < on ≥1 class. **A drift class with zero incidents in *both* arms is recorded `not-exercised` ≠ `passed`** — it does not satisfy the "reduces ≥1 class" clause. **When D4 or D6 is `not-exercised`, WS-0 returns `INCOMPLETE-on-{D4,D6}`, never a clean `SOUND`/`PASS`** (a binary PASS doesn't carry a footnote; the honesty lives at the verdict level). A `SOUND` verdict requires those classes were exercised OR an explicit operator waiver acknowledging the untested rare class. **Asymmetry:** D4 carries a *second standing signal* (the §5 WS-3a `≥4-ref-unwritten` health-line inventory) so `INCOMPLETE-on-D4` may be discharged by that signal; **D6 has no standing mitigation** — `INCOMPLETE-on-D6` is the only honest verdict when D6 is unexercised. **A minimum-exposure floor is rebutted** (it re-imports session-curation/synthetic-coverage bloat): *report* coverage, don't *force* it — this is the minimum-viable-gate that a solo dev will actually run.

**Proportionality re-affirmed (C8, F2-02):** the codebook-lens, the `not-exercised` cell-rule, and the `INCOMPLETE` verdict are **all reads off the one matrix Robert already fills** — none adds a session, tool, synthetic case, or model-judge. **WS-0 remains one matrix, Robert's eyes, zero new tooling.**

---

## 4. The MVP slice (load-bearing, drift-connected) — build first

| WS | What (load-bearing core) | Owner | Drift | Deliverable-of-THIS-arc |
|---|---|---|---|---|
| **WS-0** | Drift taxonomy + before/after probe + the `INCOMPLETE` verdict + codebook-lens = the success gate (§3) | C8 | gate | the taxonomy + probe protocol + verdict-rule spec |
| **WS-1** | `CLAUDE.md` altitude-extraction + static/dynamic split — **verify-before-evict precondition** (dependency-scan) + **L1 deterministic assertion** (scan-discovered invariants) + keep/position half | C2 | drift+cost | cut-list spec + retained-content/positioning spec + dependency-scan + L1 assertion spec |
| **WS-2a** | SSOT pointer + `design-substrate/INDEX.md` (**un-anchored `artifact→version` floor**) + do-NOT-invent (GC/ROUTING/CATALOG) + do-NOT-author (WORKFLOWS.md) + `@import`-forbid | C2 ×C1 | drift | the index/pointer spec + the navigation-set guardrail |
| **WS-3a** | **Enforced `MEMORY.md` compaction** — **degree-keyed selection rule** (pin ≥5 / keep 1–4 / archive the 39) + **supersede-mark** (never silent-drop) + **3-integer SessionEnd health-line rider** + **one-time hygiene** (write the 2 dangling ≥4-ref notes) | C3 ×C7 ×C1 | drift | enforced-compaction contract + frontmatter schema + health-line + the 2-note write |
| **WS-4 G1** | Context-doc **byte-budget guardrail** (`--check`, warn-then-fail, waiver) over the auto-loaded set | C5 | governance | the G1 gate contract (guardrail, not religion) |
| **X-min** | **Minimal memory-store recoverability** — snapshot/version (git-as-state) + atomic writes + **stale-base detection (OCC)** + named **reinject-pointer-resolvability** requirement | C3 ×C9 | drift | the recoverability contract; locking NOT in MVP |

---

## 5. MVP workstream detail

**WS-1 — CLAUDE.md altitude extraction (the primary drift lever).**
- **Verify-before-evict precondition (do FIRST):** (a) extract the live invariants/rules embedded in §2 into a compact live contract; (b) **dependency-scan** — grep §2-cell references across rules/hooks/scripts/recovery-paths to *prove* nothing active depends on the provenance; (c) the archive/index target must be an **actually git-versioned** location.
- **L1 deterministic assertion (Round-5, the ex-ante half):** a code assertion fired once at slim-time that **the invariants the dependency-scan (step a/b) proved load-bearing still emit/resolve post-§2-eviction**. Scope to *scan-discovered invariants* — the `[i]`-citation check is an *illustration of the form*, not a hard-coded work-item (a corpus example has no live D-class tie). Judge-free (catch-rate 1.0 for what it encodes), MVP-admissible where κ/TPR/TNR/L2-judge are not. C5 authors it; it rides WS-1; C2 hosts the precondition. (C8's WS-0 recall-lens = the ex-post human half of the same "did the fact survive the slim" discipline.)
- **Evict** the ~277KB §2 version-provenance to that versioned archive (lives verbatim in git + the spec files; a *navigation move*, not deletion).
- **Keep/position half:** of the retained ~40KB, specify *what altitude content stays* (operating rules + §11 posture + §12 loop + §13/§14 conventions + locked rules) and *where it sits* — critical content near start/end, not mid-window (lost-in-the-middle, research §2.2.2). Positioning is a first-class deliverable.
- **Cost framing (Round-5, demoted to a *reported* leading-indicator):** §2 eviction also cures the cache-detonation (Dive-2: editing the auto-loaded prefix invalidates the cache every turn; ×25 under loop mode) — measured by the **git-§2-edit-cadence proxy (ongoing "is provenance creeping back") + the WS-4 G1 byte-delta (one-shot "did the eviction take")**, NOT `cache_read` (no dev-loop home). Kept a *reported* win; **WS-0 drift is the gate.**
- **Success = the WS-0 probe**, not byte-count.

**WS-2a — Navigation infrastructure.** SSOT pointer + a generated/maintained `design-substrate/INDEX.md` mapping `artifact→canonical-version` so "canonical = vN" is discoverable without inline-version carry (closes the `[[wrong-version-read-delta-only-baseline]]` hazard — and **discharges C7's T3 legibility-lien**: the lien requires version-discoverability, not `#section`-precision). **MVP floor = the un-anchored `artifact→version` INDEX**; generated `file#header` section-routing is an *enhancement* that **DEFERS to WS-2b** (hand-authored section-anchors are forbidden — a stale-link/D4 surface). **Navigation-set guardrail (Round-5):** name only the established anchors (`ARCHITECTURE.md`; `WORKFLOWS.md`/`HOOKS.md` → WS-2b); **do NOT invent `GC.md`/`ROUTING.md`/`CATALOG.md`** (non-conventions — context-GC is runtime compaction, routing is CP code-config, a catalog is a generated index); **do NOT author `WORKFLOWS.md`** (the loop procedures already live as JIT skills; a static one would be eager `@import`-able prefix — the inversion to prevent); **forbid `@import`-ing any WS-2 anchor into `CLAUDE.md`**. *(Anchor: ICM = arXiv:2603.16021v2 — the CHARTER's named methodology; Claude Code auto-loads `CLAUDE.md` not `AGENTS.md`.)*

**WS-3a — MEMORY.md compaction (enforced, not advisory).** MEMORY.md is loaded into context every session and **oscillates across the 24,400B cap under churn**: it was 27,051B (over-cap) when this arc opened, and reads **10,306B at HEAD** — because an **ad-hoc, apparently-lossy compaction silently dropped ~75 index entries at 06:27** (≈120 → 45 entries). That interceding compaction is *itself* a live **D4 (memory-pollution)** incident — an unenforced, silent, lossy drop — i.e. exactly the failure this **enforced / supersede-mark / non-lossy** contract exists to replace; **the staleness reaffirms WS-3a, it does not retire it.** WS-3a's MVP inclusion rests on byte-count-**independent** triggers verified live at HEAD — the 2 dangling ≥4-ref patterns (5/5, no note file; §"One-time hygiene") + the store-not-git-versioned recoverability gap (§X-min) — **not** the instantaneous byte count (a fast-moving number re-derived at slim-time, like the 65→83 hub).
- **Degree-keyed selection rule (Round-5, C3 — the missing selection key):** compact by **wiki-link in-degree, not by prefix/category** — **KEEP-HOT** the ≈20 hub notes (in-degree ≥5; descriptions stay full; C2's WS-1 keeps these in the re-attended prefix, positioned start/end); **KEEP-LINKED** the 1–4-inbound (compaction-eligible); **ARCHIVE/JIT** the 39 zero-inbound (body → `memory/archive/`, drop the index line; recoverable per X-min; pulled back by C2's JIT read on demand). **Thresholds operator-tunable against a moving count** (the top hub grew 65→83 since the EVID snapshot — re-derive the pin-set at slim-time, don't freeze a list). **Report the degree by eye (`grep | wc -l`); do NOT build a degree-recompute engine.** *(Anchors: CoALA working/episodic/semantic/procedural; Letta Main/Recall/Archival — the tier vocabulary; the episodic/semantic *directory* split is **refused** — the repo-empirical degree-tiering refutes a flat category split.)*
- **Bi-temporal supersede-mark (Round-5, C3):** the compaction step's `drop superseded` → **`supersede-mark` (set `valid_until` + `superseded_by: [[slug]]` frontmatter, archive the body) — never silent-drop**. A Tier-1 frontmatter breadcrumb (not a Tier-5 ledger write — no hash-chain); recoverable via the X-min snapshot, so compaction is non-lossy. Cuts D1+D4. *(Anchor: Zep/Graphiti Mark-and-New.)*
- **3-integer SessionEnd health-line rider (Round-5, C7):** the existing SessionEnd report (`session-end-cleanup.sh:49-56`) gains **exactly three grep-derived integers** — `notes-superseded` (`valid_until` set) + `notes-untouched->Ndays` (mtime) + `patterns-unwritten->=4-refs` (dangling-`[[ ]]` in-degree) — so the §6 deferred staleness-scan + consolidation triggers are observable rather than silent-never-fires. Boundary-only (the counts are slow-moving); **NOT a WS-5 promotion.** These three **supersede** EVID Finding-4's illustrative `orphan%/density/true-break` triple (they are the *trigger-observability* set). The D1-fire-trigger + D5-resumption signal read off the WS-0 gate's Arm-B columns, not this line.
- **One-time hygiene (Round-5, C3 — the trigger is already met):** write the 2 currently-dangling ≥4-ref pattern bodies — `plan-revision-against-not-yet-built-substrate.md` + `strike-revision-on-refined-second-tier-reason.md` (both ~5 inbound refs, no note file at HEAD) — into the semantic tier. A finite one-time MVP write; the *recurring* consolidation mechanism stays deferred (§6).

**WS-4 G1 — the byte-budget guardrail (not religion).** Input = **effective auto-loaded context** = `bytes(CLAUDE.md) + bytes(@import-closure) + bytes(MEMORY.md)` (deterministic byte-sum; not attention-weighted). Modeled on `substitution_ledger --check` (CI/PR-tier). **Warning-mode before a clean baseline, hard-fail after.** Explicit override/waiver; never forces unreadable compression. **Composes with never-halt:** CI/PR-time guardrail, **never** an in-loop session-runtime blocker. G1 is the *only* load-bearing gate in MVP; it is **byte-budget, NOT link-integrity** (link-integrity is the deferred G-LINK, §6). G2–G4 deferred.

**X-min — minimal memory-store recoverability.** MVP = snapshot/version the out-of-worktree store (**git-as-state** is the rollback boundary) + atomic writes + **stale-base detection (= OCC)**. **FM-H is a *decentralized-handoff* topology (Round-5, C1):** N independent worktree sessions have **no lead agent to BE the single writer**, so the canon's "lead-agent-alone-writes" serialization cannot map to a topology-level writer — **serialization must live at the store (OCC), not the topology.** Full serialization/locking is **deferred** (trigger: an *observed* concurrent-write race). **Reinject-pointer-resolvability (Round-5, C9):** name it as an explicit MVP recovery requirement — at bare MVP the `postcompact-reinject.sh:30` `[ -f ]` absence-guard is the floor (it graceful-degrades on a *missing* file); the *resolution-validation* dimension (a present-but-wrong / cross-store-drifted target) rides the deferred G-LINK `--check` *when live*, NOT G1. **Note for the execution arc:** `CLAUDE.md §12.5.1:651` claims "provenance lives in git history at the global memory store" — **false at HEAD** (the store is not a git repo); correct that line when you version the store. (This PLAN does not edit CLAUDE.md content.)

---

## 6. Deferred tail (proportionality filter applied — large on purpose)

| Deferred | Trigger to revisit |
|---|---|
| **G-LINK** — link-integrity `--check` (code-fence-aware; validates `[[wiki]]` + `[md](slug)` + cross-store kebab/underscore + generated `file#header` + the reinject-pointer + `superseded_by` targets resolve; mirrors `substitution_ledger --check`, exits 1; CI/PR-time, never-halt) | **MVP-on-trigger:** {WS-2a generated section-routing ships} OR {`superseded_by` becomes machine-emitted} OR {an observed D4-via-dangling-ref at WS-0}. Absent a trigger, the 3 bucket-C breaks are one-time hand-hygiene. When live, the reinject pointer + `superseded_by` share **one input set**. |
| **Recurring consolidation pass** — a **synchronous SessionEnd write-event** (C1 fires / C3 fills the semantic-tier write; no daemon, no C9) | observed-D4: the `≥4-ref-unwritten` count > 0 (NOT the canon's 50–200-episode cadence — a solo-scale category error). *(The 2 currently-triggered patterns are handled as MVP one-time hygiene, §5; this is the recurring mechanism only.)* |
| WS-2b — top-level orientation docs (`ARCHITECTURE.md` / `HOOKS.md` content; generated section-routing) | a fresh-context orientation gap is *observed*, or the hook system is next substantially changed, or a wrong-§-citation D2 incident |
| WS-3b — `.harness/` Tier-5 archival policy + checkpoint-store asymmetry | ledger/checkpoint growth causes an *observed* navigation or cost problem |
| WS-4 G2 (clearance-marker schema) / G3 (ledger-shape) / G4 (freshness-teeth) | an *observed* malformed-marker / ledger-drift / stale-roadmap incident (G4 highest-likelihood; D5; HITL-recoverable) |
| WS-5 — mid-session budget surface + dashboard health states | G1 (CI-time) + the SessionEnd 3-integer line prove insufficient and mid-session blindness causes *observed* drift |
| WS-6 6b — D14 recovery build (U-HK-30/40 + `context_budget_exceeded` mode) | **gated on the WS-0 probe showing D5 (bad-resumption) drift after WS-1** (WS-6 **6a done** — `postcompact-reinject.sh` + `context-recovery.sh` conform to §7.2; credited). Deeper §2 externalization does NOT un-defer this — reinject is §7.2-pointer-mediated, orthogonal to prefix depth. |
| X-full — memory-store serialization/locking | an *observed* concurrent-write race |

---

## 7. Cross-cutting ownership (no forks)

- **`tools/hooks/` home-of-record:** the U-HK `HARDENING_PLAN.md` owns hook *execution* units (incl. D14); this PLAN owns the context/memory *governance* layer and **cites** D14 as a WS-6 dependency. `HOOKS.md` (deferred WS-2b) is a 3-lane artifact: C1 owns topology content, C2 owns loading/placement (JIT, never `@import`-ed), C7 owns the observability overlay.
- **T-perm-2 cut-list (C2↔C3):** C3 owns the at-rest degree-keyed retention rule + the ARCHIVE move + the `superseded_by` schema; C2 owns the prefix-read of KEEP-HOT (positioned) + the JIT read-back of ARCHIVE. C3 names the key; C2 decides per-turn reads.
- **Consolidation (C1↔C3):** C1 owns the firing-site (SessionEnd) + the observed-D4 trigger; C3 owns what-to-promote + the semantic-tier write. Synchronous, no daemon, no C9.
- **L1 assertion (C5↔C2↔C8):** C5 authors the assertion (judge-free admissibility); C2 hosts it in the WS-1 precondition; C8's WS-0 recall-lens is its ex-post human half.
- **Recovery-pointer (C9↔C5↔C3):** C9 owns the recovery requirement; the bare-MVP self-check is the `[ -f ]` guard (C9's lane); the resolution-`--check` is C5's G-LINK when live; the store-versioning is C3's X-min. **The requirement rides the `[ -f ]` guard / G-LINK, NOT G1** (byte-budget ≠ link-integrity).
- **Health-line (C7):** C7 surfaces the 3 integers at SessionEnd; C3+C8 own thresholds; C9+C1 own cadence. The line stays exactly 3 integers (no rot-scores — embedding-drift/MMD/cosine are refused as contrary to the binary/human-graded gate).
- **C5↔C9 (gate vs mode):** surface-disjoint — G1/G-LINK = CI/PR-time guardrails; `context_budget_exceeded` (deferred) = session-runtime degradation-mode. Never-halt binds only runtime.

---

## 8. Sequencing

1. **WS-0 first** — define the drift taxonomy + verdict-rule; capture the **baseline (Arm A)** on current HEAD.
2. **WS-1** (verify-before-evict precondition + L1) + **WS-2a** (un-anchored INDEX + guardrail) + **WS-3a** (degree-keyed compaction + supersede-mark + health-line + the 2-note one-time hygiene) + **X-min** (OCC + git-as-state + named reinject-pointer requirement).
3. **WS-4 G1** — warning-mode, then hard-fail once the post-slim baseline is clean.
4. **Measure** — run the WS-0 probe (Arm B). `SOUND` → done. `INCOMPLETE-on-{D4,D6}` → rare classes untested; exercise or waive. Regress any class → WS-1 evicted load-bearing content; restore + re-measure. D5 regression → trigger WS-6 6b.

---

## 9. Hard lane discipline (carried from every round)

Additive-only; PLAN-not-execution; **no** `design-substrate/**` content edits, **no** `harness-*/src`, **no** `R-NNN` roadmap, **no** deletion of versioned copies. The §2 provenance is handled by *navigation + archive*, never retention-removal. The `§12.5.1` correction (§5 X-min) is **execution-arc work**, routed through the X-AL-3 escape-hatch (clearance marker / `design-phase-direct`) at design-phase posture when executed. Locked operator rules (never-halt, defer-and-continue, prefer-free-ollama, paid/secret/destructive deny-list) preserved, not relitigated. **Anti-bloat self-application:** every Round-5 fold is a rule/one-shot/rider on an existing workstream — the degree-key stays grep-by-eye (not a daemon), the one-time hygiene stays a finite write (not the recurring pass), L1 stays a one-shot precondition (not a standing CI gate), the INCOMPLETE verdict stays a matrix read (not new tooling), the health-line stays 3 integers (not a dashboard).

---

## 10. Handoff

This PLAN is handed to a downstream **execution arc**. That arc: runs WS-0 to baseline → executes the MVP (§4–§5) → validates via the WS-0 probe (§3). The PLAN is **falsifiable** by that probe — if drift doesn't measurably fall (or returns `INCOMPLETE` on the rare classes), the PLAN failed regardless of how clean the byte-count looks. The deferred tail (§6) is revisited only on its named triggers. The whole effort is bounded by the same proportionality it prescribes: a solo-developer harness gets the minimal drift-connected core, not a governance apparatus.
