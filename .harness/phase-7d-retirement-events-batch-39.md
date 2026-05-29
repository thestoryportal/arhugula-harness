# Phase 7d Retirement Events — Batch 39

| Field | Value |
|---|---|
| Batch number | 39 |
| Filed at | 2026-05-28 (same-session-sequel to batch-37 OD-1 + batch-38 OD-7 closures; sub-species 10 `gate-text-stale-vs-production-landings` audit of IS-4 row — first cross-axis application of the audit pattern) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 + workflow v1.12 §7.4.7.3.C retirement-tier-transit audit-template + 33rd application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` |
| Predecessor batch | `phase-7d-retirement-events-batch-38.md` (2026-05-28 — H_T-OD-7 STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY) |

---

## §0 Batch context

**Status type: 1 STILL-BOUNDED → RETIRED transit (H_T-IS-4) via categorical-mismatch reclassification. Cumulative RETIRED count increments 39/54 → 40/54 (74.1%); STILL-BOUNDED count decrements 8/54 → 7/54 (13.0%); RETIRE-READY + PARTIAL + STILL-BOUNDED-INDEFINITELY counts unchanged. Pipeline-advanced 44/54 → 45/54 = 83.3% (+1.9 percentage points). Cardinality check: 40 + 2 + 3 + 7 + 2 = 54 ✓.**

**Workspace crosses 74% RETIRED + 83% pipeline-advanced thresholds. FIRST cross-axis application of sub-species 10 `gate-text-stale-vs-production-landings` audit pattern (OD-axis → IS-axis); pattern generalizes beyond originating axis.**

This batch records the **STILL-BOUNDED → RETIRED transit** for H_T-IS-4 (atomic deploy primitive) via **categorical-mismatch retirement criterion** under sub-species 10 audit. THIRD sub-species 10 closure in retirement ledger (after OD-1 batch-37 + OD-7 batch-38, both 2026-05-28 same calendar day); FIRST closure outside OD-axis. The pre-batch-39 gate text at `harness-is/CLAUDE.md` §4.1 row 143 + ledger v2 §3 row IS-4 framed retirement as gated on H_T owning the deploy act ("deploy act still operator `Bash(git *)`"). Empirical audit performed this session against IS spec C-IS-04 §4 + ADR-F2 §Decision + production grep discriminates:

| Check | Finding | Authority |
|---|---|---|
| 1. IS spec C-IS-04 §4 contract surface | **Atomicity contract over git commit** — NOT a runtime deploy composer. §4 "Specification content": "A 'deploy' event is the application of a single git commit (or atomic commit-group via merge commit / tagged release) that updates one or more of the four artifact classes. The atomicity property commits: All-or-nothing per commit (precluded by git's commit atomicity at the storage layer); Single-version observability; Composition with C-IS-03 commit-stream sub-role; Composition with C-IS-08 shadow-Git checkpointing." Verification surface = "Git log inspection at any commit." **The contract IS the git-commit-atomicity property; the deploy act IS git commit.** §4 "Deferred to implementation discretion": "Specific deploy tagging conventions; specific eval-set file format (JSON / YAML / JSONL); specific commit-message-driven deploy-event annotation conventions." | IS spec v1.2 §4 C-IS-04 lines 212–244 |
| 2. ADR-F2 §Decision (foundational ADR — canonical substrate commitment) | Git is committed as the canonical state substrate at the F-layer (ADR-F2 §Decision: "filesystem + git canonical state substrate; combined git tier role"). C-IS-04 §"ADR commitment(s) honored" cites: "ADR-F2 v1.2 §Consequences (a) ('Prompts-as-files in git, atomically deployed alongside code and evals'; 'Eval-set residence in git enables atomic prompt+code+eval deploys')." **There is no H_T-owned deploy substrate that substitutes for git** — git IS the substrate. Per ADR-F2 the deploy commitment IS git commit atomicity at the storage layer. | ADR-F2 v1.2 §Decision + §Consequences (a) |
| 3. Ledger v2 §3 row IS-4 gate text (empirical citation) | Row text byte-exact: "`verify_deploy_atomicity` is offline/on-demand verification only; **H_T does NOT own the deploy act** — `git add`/`git commit` remain operator `Bash(git *)`. C-IS-04 §4 defers commit-message annotation to operator." The ledger explicitly states H_T does not own the deploy act + defers annotation to operator — confirming the contract is operator-driven by design. | `.harness/phase-7d-retirement-ledger-v2.md` line 76 |
| 4. Production substrate grep — `verify_deploy_atomicity` | Verification primitive LANDED at `harness-is/.../verify_deploy_atomicity.py`. Per the gate text "H_T owns verification primitive only" — the verification side IS landed. The complementary "deploy act" side is structurally precluded from H_T ownership per ADR-F2 (git IS the substrate). | empirical grep `harness-is/src/` |
| 5. H_E substitution surface | H_E surface = operator `Bash(git *)` = `git add` + `git commit`. Per ADR-F2 this IS the canonical substrate, NOT a transitional substitution. X-AL-2 second conjunct ("substituted H_E surface no longer invoked at substitution site") is **vacuously satisfied via categorical-mismatch** — abandoning operator `Bash(git *)` would mean abandoning git as the deploy substrate, which is foreclosed by ADR-F2 §Decision. | ADR-F2 v1.2 §Decision + C-IS-04 §4 deferred-to-implementation-discretion |
| 6. Sibling candidate audits (deferred) | IS-2 (artifact-tier registry) deferred per advisor pre-substantive consultation: ledger v2 line 75 gate explicitly names "cross-tier traceability invariant unenforced at append-time" = substantive runtime work owed; reclassification would be X-AL-3 silent absorption. CP-23 (bridging-arc traversal) deferred: substrate `t_perm_3_composition.py` U-CP-53 landed but no explicit runtime spec carve-out cite (unlike CP-11/CP-14 batches 29/30 which cited runtime spec v1.6 §14.7.2 step 5 line 2546 cascade_policy carve-out). | advisor pre-substantive consultation + grep this session |

**Discriminator outcome:** Contract surface IS git-commit-atomicity per ADR-F2 §Decision; verification primitive landed at H_T; deploy act IS git commit by ADR-F2 canonical-substrate commitment. The IS-4 gate text was structurally stale-vs-spec — framing retirement as "H_T owning the deploy act" which is structurally foreclosed by ADR-F2 (git IS the substrate; not a thing to be wrapped or owned by H_T). Authoring a runtime composer wrapping `git CLI` to "own the deploy act" would be **X-AL-3 silent extension** under cover of stale gate-text framing — and would contradict ADR-F2 §Decision (git is the canonical substrate, not a substitution target).

**Disposition: STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY** (mirror OD-1 batch-37 + OD-7 batch-38 + OD-8 v1 §1 authoring-close pattern). The substrate IS the C-IS-04 contract realization at git-commit-atomicity + verification primitive landing; deploy act IS git commit by ADR-F2; commit-message annotation deferred to operator by C-IS-04 §4. Per X-AL-2 retirement criterion: (cited unit IDs landed: `verify_deploy_atomicity` verification primitive landed at harness-is) ∧ (substituted H_E surface no longer invoked at substitution site: vacuously true — H_E surface IS the canonical substrate per ADR-F2; categorical-mismatch).

Operator-ratified routing (α) at AskUserQuestion 2026-05-28 over (β) STILL-BOUNDED-INDEFINITELY + (γ) Class 1 fork + (δ) X-AL-3 build runtime deploy composer.

---

## §1 Criterion verification

- **Criterion A** (cited unit IDs landed). MET. `verify_deploy_atomicity` verification primitive landed at `harness-is/src/harness_is/verify_deploy_atomicity.py` (the only mandated runtime artifact per C-IS-04 verification surface).

- **Criterion B** (substituted H_E surface no longer invoked at substitution site). MET vacuously via categorical-mismatch. The H_E surface = operator `Bash(git *)` IS the canonical deploy substrate per ADR-F2 §Decision; it is not a transitional substitution to retire. Per the OD-1 batch-37 + OD-7 batch-38 sub-species 10 precedent, X-AL-2 second conjunct is vacuously satisfied when the H_E surface IS the substrate itself.

**No further in-CLI close pathway** — retirement is structural at authoring close; substrate-IS-the-contract pattern. Future operator may author commit-message annotation conventions per C-IS-04 §"Deferred to implementation discretion" — that is operator-discretion convention layer, NOT an H_T design extension.

---

## §2 Sub-row substitution-status table

Pre-batch-39 IS-axis bucket (post 2026-05-20 second-pass closure):

| Substitution | Status | Source |
|---|---|---|
| H_T-IS-1 (path-class registry) | RETIRED 2026-05-20 | `stage_1_is.py` step 1 `materialize_path_registry` |
| H_T-IS-2 (artifact-tier registry) | STILL-BOUNDED (deferred at batch-39 audit per substantive runtime gate "cross-tier traceability invariant unenforced at append-time") | Typed library exists; no bootstrap composer invokes |
| H_T-IS-4 (atomic deploy primitive) | **STILL-BOUNDED → RETIRED at this batch (batch-39)** | Contract IS git-commit-atomicity per ADR-F2; H_E surface IS canonical substrate; categorical-mismatch sub-species 10 |
| H_T-IS-5 (state-ledger entry shape) | RETIRED 2026-05-20 | `lifecycle/state_ledger.py` driver-invoked |
| H_T-IS-6 (hash-chain integrity) | RETIRED 2026-05-20 | `entry_hash.py` in-process hashlib |
| H_T-IS-7 (F2 read/write contract pair) | RETIRED 2026-05-20 | both materialized at bootstrap |
| H_T-IS-8 (shadow-Git checkpoint) | RETIRED 2026-05-20 | `shadow_git_checkpoint.py` |
| H_T-IS-9 (worktree isolation) | RETIRED 2026-05-20 | `worktree_isolation.py` |
| H_T-IS-10 (substrate seam exports manifest) | RETIRED (authoring close, v1 §1) | Authoring-only |

Post-batch-39 IS-axis bucket: **8 RETIRED + 0 RETIRE-READY + 0 PARTIAL + 1 STILL-BOUNDED + 0 STILL-BOUNDED-INDEFINITELY = 9**.

**IS-axis pipeline-advanced: 8/9 = 88.9% (+11.1 pp from 7/9 = 77.8% pre-batch-39).** IS-2 remains the sole STILL-BOUNDED — substantive runtime gate at append-time cross-tier traceability per ledger v2 §3.

Workspace-layer cumulative post-batch-39: **40/54 RETIRED (74.1%) + 2/54 RETIRE-READY (3.7%) + 3/54 PARTIAL (5.6%) + 7/54 STILL-BOUNDED (13.0%) + 2/54 STILL-BOUNDED-INDEFINITELY (3.7%)**. Pipeline-advanced (R+RR+P): **45/54 = 83.3%** (+1.9 percentage points from batch-38).

---

## §3 Adjacent observations

(a) **FIRST cross-axis application of sub-species 10 `gate-text-stale-vs-production-landings` audit pattern.** Sub-species 10 catalogued at workflow v1.12 §7.4.7.2 publication 2026-05-28 (this session, OD-axis origin); first 2 closures at OD-axis (OD-1 batch-37 + OD-7 batch-38); THIRD closure at IS-axis (this batch). Pattern generalizes beyond originating axis — the audit shape (read canonical spec contract surface + grep production for substrate landing + check H_E surface for categorical mismatch) applies to any STILL-BOUNDED row whose gate-text framing diverged from canonical spec contract over the carry window. Audit candidate next-arc: sweep CP-axis + AS-axis remaining STILL-BOUNDED rows for sibling patterns.

(b) **Categorical-mismatch retirement criterion shape catalogued at IS-axis.** OD-1 H_E surface = `ToolSearch` (categorical mismatch with H_T deferral envelope contract); OD-7 H_E surface = "None — manual operator verification at scope boundaries" (no automated H_E surface to retire); IS-4 H_E surface = operator `Bash(git *)` = `git add` + `git commit` (IS the canonical substrate per ADR-F2). Three distinct shapes within sub-species 10 — all satisfy X-AL-2 second conjunct vacuously: (1) categorical-mismatch where H_E surface is wrong abstraction layer; (2) no-automated-H_E-surface where the substitution mechanism is "manual operator verification"; (3) H_E-surface-IS-canonical-substrate where retiring would contradict ADR commitment. IS-4 instantiates shape (3) for the first time.

(c) **IS-axis crosses 88.9% pipeline-advanced — third axis above 80%.** AS-axis at 81.8% (post-batch-31); OD-axis at 100.0% (post-batch-38); IS-axis at 88.9% (post-batch-39). CP-axis remains below 80% (17/22 = 77.3% RETIRED + 3/22 PARTIAL + 2/22 STILL-BOUNDED = 22/22 = 100.0% pipeline-advanced raw, but 5/22 still pre-RETIRED). Workspace pipeline-advanced 83.3% reflects multi-axis convergence on terminal closure pre-deployment.

(d) **IS-2 sibling-candidate explicitly DEFERRED at this batch per advisor pre-substantive consultation.** Advisor flagged IS-2 ledger v2 §3 gate text "cross-tier traceability invariant unenforced at append-time" as substantive runtime work owed (C-IS-02 §"Tier composition contract" line 170: "Every `durable`-tier ledger entry references the `procedural`-tier artifacts in scope at the entry's write-time via the `action_id` field per C-IS-05"). Reclassifying IS-2 as substrate-IS-contract would be X-AL-3 silent absorption — the typed-library-IS-the-contract reading is plausible but the gate text explicitly names a runtime enforcement requirement at the state-ledger writer. IS-2 remains STILL-BOUNDED pending either: (α) runtime enforcement at state-ledger writer's `procedural`-tier reference via `action_id`; OR (β) operator-ratified canonical-reading amendment narrowing the gate. NOT patched per FM-2 single-focus arc.

(e) **CP-23 sibling-candidate explicitly DEFERRED at this batch per advisor pre-substantive consultation.** Substrate `t_perm_3_composition.py` U-CP-53 LANDED (compose_t_perm_3 + read_per_cell_t_perm_3 + handle_runtime_fault); ZERO production callers outside its own module. Pattern is `substrate-pre-landed-consumer-deferred` (NOT sub-species 10). Per advisor: closing CP-23 as operator-discretion ratification (mirror CP-11 batch-30 + CP-14 batch-29 close pattern) requires explicit runtime spec §14.7 MVP carve-out cite naming bridging-arc / cross-deployment scope (parallel to CP-11/CP-14's runtime spec v1.6 §14.7.2 step 5 line 2546 cascade_policy carve-out). Grep at runtime spec found NO such carve-out for U-CP-53. CP-23 remains STILL-BOUNDED pending either: (α) operator AskUserQuestion ratifying explicit v1.6 MVP single-sub-agent-no-bridging-arc carve-out; OR (β) substantive runtime composer landing invoking U-CP-53. NOT patched per FM-2.

(f) **ZERO cross-axis cascade.** Intra-IS-axis doc-hygiene only. NO IS spec / IS plan / CP spec / AS spec / OD spec / runtime spec / CXA / ADR / ADD / PRD amendment. NO production code change. NO test addition. NO carrier change. NO Meta-Arch refresh (IS-4 ledger gate at v2 §3 row 76 + Meta-Arch §5.4 row already accurate; ZERO Meta-Arch row 4 vocab drift surfaced this audit).

(g) **33rd application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`.** Advisor at arc opening: (1) confirmed IS-4 is strongest candidate via categorical-mismatch reading against ADR-F2 + C-IS-04 contract surface; (2) DEFERRED IS-2 per substantive gate text "cross-tier traceability invariant unenforced at append-time" — X-AL-3 risk; (3) DEFERRED CP-23 per absence of explicit MVP carve-out cite — substrate-pre-landed-consumer-deferred is distinct sub-species. Discipline pattern: pre-substantive advisor consultation reduces classification noise; 1 of 3 candidates clean, 2 of 3 require either substantive arc or AskUserQuestion ratification. Advisor recommended "land IS-4 alone this arc" — sequenced as one cleanly-classified candidate to preserve precedent rigor on sub-species 10 application.

(h) **Sub-species 10 catalogue cardinality grows: 2 OD-axis closures → 3 closures spanning 2 axes.** Empirical evidence the audit pattern reaches cross-axis applicability. Workflow v1.12 §7.4.7.2 species-3 sub-species column may warrant cross-axis applicability note at next revision pass (currently catalogued at OD-axis origin); routine doc-hygiene candidate for future workflow-doc revision.

(i) **Audit footprint: ~5 file reads + 4 grep operations + 1 advisor call + 1 AskUserQuestion = ~6 minutes wall-clock to discriminate 3 candidates and route cleanly to 1 classification.** Compared with substantive runtime composer arc estimates (~hours to days), sub-species 10 audit pattern delivers ~10-100x leverage when applicable. Pattern viability for next-arc CP-axis + AS-axis sweep candidate.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-39.md` |
| Filed at | 2026-05-28 |
| Phase | Phase 7 sub-phase 7d — substitution retirement |
| Predecessor batch | batch-38 (H_T-OD-7 STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY) |
| Co-published artifacts | `harness-is/CLAUDE.md` §4.1 IS-4 row transit + cumulative-counts line refresh + memory entries |
| Cross-axis cascade | ZERO (intra-IS-axis doc-hygiene only) |
| Production code change | ZERO |
| Test addition | ZERO |
| Spec / plan amendment | ZERO (IS spec preserved verbatim; ADR-F2 preserved verbatim; Meta-Arch §5.4 row preserved verbatim — no vocab drift surfaced at IS-4 audit) |
| Advisor application count this arc | 33rd — pre-substantive trichotomy IS-2/IS-4/CP-23 candidate triage; 1 of 3 cleanly classified at sub-species 10 categorical-mismatch shape (3); 2 of 3 deferred per substantive gate / absence of explicit carve-out |
