# Codex Handoff — Arhugula v2 / H_T harness (2026-06-27)

*Authored by Claude at session close, handing forward driving to Codex (gpt-5.5) due to Claude weekly-usage exhaustion. This is the lay of the land + forward guidance. Read this, then read root `CLAUDE.md` (the always-loaded governance), then derive your next action per §12 of that file.*

---

## 0. TL;DR — where things stand right now

- **HEAD:** `0436929f` on `main` (a §12.2.1 terminating-refresh commit). Working tree clean, 0 open PRs.
- **Active program:** **R-FS-1** (the operator's FULL-SPEC build directive, 2026-06-12 — *build the whole spec beyond MVP, nothing deferred*). Its frozen 11-arc order is COMPLETE; what remains is a register of standalone `B-*` build arcs.
- **Live tally (authoritative):** `python3 tools/arc_ledger.py --check` → **67 closed / 0 gated / 4 resolved / 2 forward**. R-FS-1 stays ACTIVE until the 2 forward arcs land/resolve, then the `R-CL-Q1` whole-harness quality track admits.
- **The 2 forward arcs** (the only remaining build work):
  1. `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-FANOUT-CHILD-RECONCILER` — **NOT operator-gated, this is your next pickup** (§5 below).
  2. `B-FANOUT-CRASH-RESUME-ORCHESTRATOR-PROCEED-RESIDUAL` — **operator-gated** (C10⊥C11 council + an operator `AskUserQuestion` at open); goes last.
- **Dashboard fixed point:** `.harness/roadmap_status.md` stores `workspace_state_hash = 57e300cc36d8`, which is `compute(state at HEAD~1)`. This one-commit lag is EXPECTED (the §12.2.1 terminating-refresh fixed point) — do **not** treat it as drift, and do **not** spawn another refresh PR for it. The session-start audit recognizes it automatically.

---

## 1. The lay of the land

This repo builds **H_T** (the target multi-LLM agent harness, "Arhugula v2") under **H_E** (the Claude Code / now Codex CLI dev surface). It is BOTH a design-substrate corpus AND a Python implementation, co-resident.

```
design-substrate/        # CANONICAL design artifacts (ADRs, ADD, PRD, per-axis specs + plans, CXA).
                         #   Delta-only spec chains: Spec_Control_Plane_v1_85.md is the CP HEAD;
                         #   Spec_Harness_Runtime_v1.md is a single file with prepended change-notes (HEAD v1.91).
harness-core/            # shared cross-axis types
harness-is/  harness-as/ harness-cp/  harness-od/  harness-cxa/   # the 4 axes + cross-axis seams
                         #   Most R-FS-1 crash-resume work lives in harness-cp + harness-runtime.
harness-runtime/         # the runtime composer/dispatch layer (lifecycle/, bootstrap/)
.harness/                # PROCESS substrate (NOT design-substrate): the roadmap dashboard, arc-ledger,
                         #   clearance markers, fork docs, retirement events, this handoff.
tools/                   # arc_ledger.py, substitution_ledger.py, dashboard/generate.py, semantic_overlay/
CLAUDE.md                # ALWAYS-LOADED root governance. Read it. §12 is the roadmap loop; §13 orchestration;
                         #   §14 execution conventions. harness-cp/CLAUDE.md is the CP-axis scoped guidance.
```

**Authority chain (earlier is canonical for later):** ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.20 → Phase-7 implementation (the code). Conflicts route to design-phase back-flow, never silent absorption.

**Two postures, one repo (the X-AL-3 boundary — `CLAUDE.md` §4.4 + §11):**
- *Phase-7 (impl):* edits `harness-*/src|tests/**`, consumes `design-substrate/*` as cleared canonical.
- *Design-phase:* edits `design-substrate/**`.
- A PR that touches BOTH (a "bundled-absorption arc" — which every crash-resume arc is) MUST carry back-flow documentation (a clearance marker under `.harness/clearance/`). The CI guard `.github/workflows/x-al-3-guard.yml` fails a design-substrate edit with no back-flow doc. **Always co-land clearance markers with spec edits** (template: `.harness/clearance/TEMPLATE.md`).

---

## 2. The roadmap loop (§12 of CLAUDE.md — this is how you derive what to do)

1. **Session-start audit** (`CLAUDE.md` §12.1): read `.harness/roadmap_status.md`; compute `workspace_state_hash` (recipe in `Project_Roadmap_v1.md` §7.1 — `git HEAD[:8]` + open-PR list + open-fork count + latest retirement-batch path → sha256[:12]). If it mismatches AND the most-recent merge is a terminating refresh (title begins `ops: roadmap status refresh `) AND the stored hash == `compute(HEAD~1)`, that's the **expected fixed-point lag** → proceed, silently update the stored hash, do NOT spawn a refresh PR. Otherwise a genuine mismatch → HALT + reconcile.
2. **Derive next action:** the live `arc_ledger.py` register + the `roadmap_status.md` "Next action" cell. Right now that's the RECONCILER arc (§5).
3. **Build with verification → PR → merge.**
4. **Post-merge §12.2 audit:** a *content* PR that advances `main` owes a **terminating refresh PR** afterward — title prefix `ops: roadmap status refresh `, changing **only** `.harness/roadmap_status.md` + `tools/dashboard/roadmap.html` (regenerated via `python3 tools/dashboard/generate.py --root .`). That refresh PR is the recursion-stopping fixed point (§12.2.1) — it does NOT owe its own refresh.
   - Update in the refresh: `workspace_state_hash`, `git_head`, `last_refreshed`, prepend `recently_completed` (drop oldest, keep 5), re-derive `next_action`. Also bump the `snapshot:` block in `.harness/arc-ledger.yaml` **in the content PR** (forward-only; the `arc-ledger` CI gate fails an impossible tally).
   - **A post-merge hook prints the exact hash + steps** — honor it.

**Practical note for Codex:** the giant `git_head` cell in `roadmap_status.md` exceeds editor/Read token limits. Edit it with a Python `str.replace` script (see how PR #791/#793 did it) — match the cell's leading segment, prepend the new entry, demote the prior to `**PRIOR LINEAGE (#NNN, preserved):**`.

---

## 3. Disciplines you must carry forward (non-negotiable)

| Discipline | What it means | Source |
|---|---|---|
| **FULL-SPEC, nothing deferred** | Every capability gets BUILT beyond MVP. A "defer / bounded-residual / confirm-defer" close is NOT acceptable — register it as a `B-*` arc and build it. Back-flow is PRE-AUTHORIZED. | `[[feedback-full-spec-beyond-mvp-nothing-deferred]]` |
| **Decorrelated review before merge** | Two independent reviewers on every high-blast-radius diff. Claude used **advisor** (full-transcript) + **out-of-family Codex** (`just codex-review`). **For Codex-as-driver this changes:** Codex-reviewing-Codex is NOT decorrelated. Your decorrelation = (a) the deterministic gates (full suite + pyright + ruff + overlay + arc-ledger + closure-gate), (b) the `harness-adversarial-reviewer` skill as a dedicated red-team pass, (c) **by-execution witnesses** (see below), and (d) the operator is non-coding, so adjudicate code findings via witnesses, NOT operator surfacing (`[[feedback-noncoding-operator-decorrelated-adjudication]]`). |
| **CAN vs DOES / by-execution witness** | A relaxed predicate over a dead producer is green-and-wrong. Every recovery/behavior claim needs a **RED-without-fix** witness through the REAL path (`compose_child_workflow_runner` → `execute_workflow`), empirically confirmed by reverting the fix — not a unit test on the predicate. This is the single most load-bearing discipline in this family. | `[[built-but-vacuous-reground-ledger-asis]]`, `[[full-chain-witness-not-half-proofs]]` |
| **Ground before building** | At arc-open, re-ground the registered "anticipated_scope" — it is an *anticipation*, often overturned. #779, #788, #790 all overturned their registration's "needs a new substrate" framing by grounding (the existing machinery extended). | `[[grounding-reveals-claude-closeable-slice-close-honestly]]`, `[[disposition-label-is-a-claim-verify-against-spec]]` |
| **Byte-exact citations** | Every `§N.M` / `C-*` / `U-*` cite resolves byte-exact at session-time. Use `just overlay-query` to resolve cite→code; grep siblings for cross-spec drift. | `CLAUDE.md` §13.1 |
| **Never `git add -A`** | The workspace has ~2500 deliberately-untracked files. Stage explicit paths only. | `[[never-git-add-all-untracked-pollution]]` |
| **Secrets via `just`** | `.env` (gitignored, in the MAIN checkout) + justfile dotenv-load supply provider keys. `just <recipe>`, never source. | `[[secrets-via-just-recipe-not-direct-sourcing]]` |
| **No unilateral paid calls / secret relocation** | Drive to the dispatch/credential boundary, surface it; don't auto-fire a paid LLM call or move secrets. Prefer free Ollama for live-e2e. | `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]` |

---

## 4. How to build + verify + ship an arc (the mechanical loop)

```bash
# Verify (the deterministic gates — these are your decorrelation as Codex):
uv run --package harness-cp pytest harness-cp/tests -q                       # CP suite (~1434 pass / 1 xfail)
uv run --package harness-runtime pytest harness-runtime/tests -q -m "not e2e" # runtime (~2166 pass / 10 skip)
uv run pyright <touched files>          # must stay 0/0/0
uv run ruff format <files> && uv run ruff check <files>
just overlay-check                      # code↔cite / cross-axis-seam drift (330 nodes / 31 seams)
python3 tools/arc_ledger.py --check     # tally consistency (fails on impossible tally)
just closure-gate                       # G1.1 = standalone_registered + standalone_gated == 0

# Ship (bundled-absorption arc = spec + impl + clearance + ledger + dashboard, one PR):
#  1. spec delta (new design-substrate/Spec_*_vN.md for CP; prepend a change-note for runtime)
#  2. 2 clearance markers under .harness/clearance/  (X-AL-3 back-flow — REQUIRED)
#  3. arc-ledger.yaml: flip the arc to status:closed (+ pr/spec_delta/gives/closed_scope/as_built/why),
#     register any decomposed follow-on, bump the snapshot: block + its FRONTIER NOTE
#  4. python3 tools/dashboard/generate.py --root .   (regenerate roadmap.html; never hand-edit it)
#  5. branch, commit explicit paths, push, gh pr create, wait CI (~75s), gh pr merge --squash
#  6. terminating refresh PR (§2 step 4)
```

CI is ~75s (15 blocking checks; `main` is UNPROTECTED — red advisory checks like `coverage` don't block merge). Don't over-poll (~80s once).

---

## 5. YOUR NEXT PICKUP — `B-FANOUT-CRASH-RESUME-MAYBE-RAN-SUBAGENT-FANOUT-CHILD-RECONCILER`

**Read its full `anticipated_scope` in `.harness/arc-ledger.yaml`** (it has the grounding leads). Summary:

**What it is:** a maybe-ran fan-out / orchestrator `SUB_AGENT_DISPATCH` whose CHILD is itself FAN-OUT (`PARALLELIZATION`/`ORCHESTRATOR_WORKERS`/`HIERARCHICAL_DELEGATION`) ∧ engine `RECONCILER_LOOP`. Today it fails closed; this arc makes it recoverable (or resolves it invalid if grounding shows it's unrepresentable — but representability is already confirmed: see below).

**Why it was decomposed out of #790 (don't skip this):** #790 closed the SAVE_POINT slice as a light constant-widen (`_FANOUT_REPLAY_ENGINE_CLASSES` {ESR,WAL} → {ESR,WAL,SAVE_POINT}). SAVE_POINT is the C-CP-11 §11.2 **ABOVE_ENGINE** reading — the *harness* branch store (`EngineOutputStore`, class-agnostic) is the SOLE aggregate authority. RECONCILER is the §11.2 **RECONCILER** reading — the *engine* owns reconvergence (CRD-resource-version). That asymmetry is exactly what split the LINEAR final_state family into #779 (SAVE_POINT) and #781 (RECONCILER). **The recurring discriminator: ABOVE_ENGINE engine classes close as light relaxes; RECONCILER always carries its own two-authorities grounding.**

**The two open grounding questions for RECONCILER (resolve at open):**
1. **Two-authorities-for-aggregate:** does the engine-owned reconciler substrate COMPETE with the B-FANOUT-OUTPUT-REPLAY branch store for the fan-out *aggregate* authority? For the LINEAR RECONCILER slice (#781) store-reuse won because the reconciler substrate carries a convergence *digest* (`StateSummary`: summary_text + summary_hash + ledger refs), NOT the per-step output map → no competing authority. **Verify this holds for a fan-out AGGREGATE.** Key fact in your favor: `_determine_fanout_resume` (harness-cp/src/harness_cp/workflow_driver.py) reconstructs from `store.read_branch_records` ONLY — "the STORE is the SOLE which-branches-completed authority" — so the reconstruction path is already class-agnostic.
2. **CAS/F-1 under fan-out:** the RECONCILER F-1 won-CAS-claim window — when re-dispatching a *fan-out of branches*, each branch's own crash-resume fires the engine-layer reconverge gated at the CAS claim. The LINEAR RECONCILER child (#784) resolved this via `ABORT_REVALIDATION_FAILED` → child FAILED before any step re-executes → parent fold raises `SubAgentChildFailedError` (fail-closed, never a SUCCESS aggregate). **Confirm a fan-out of CAS-claiming branches is fail-closed-safe.**

**Likely shape of the close:** if both resolve fail-closed-safe, it's a constant widen ({ESR,WAL,SAVE_POINT} → +RECONCILER) mirroring #790. The mechanism + witnesses to mirror:
- CP: `_FANOUT_REPLAY_ENGINE_CLASSES` (harness-cp/src/harness_cp/workflow_driver.py:~716).
- runtime mirror: `_SUBAGENT_RECOVERABLE_FANOUT_CHILD_ENGINE_CLASSES` (harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:~339).
- by-execution witness: `harness-runtime/tests/integration/test_fanout_child_crash_resume_witness.py` (add a RECONCILER variant; it must be RED-without-fix).
- classifier + parity + swap-guard verdicts: `harness-runtime/tests/test_lifecycle_sub_agent_dispatch.py` (the `fanout-child-reconciler` False control flips to True; the `_payload_engine_signature` `topology:engine` fold already covers the engine, no new swap hole).
- swap guard already folds `f"{topology}:{engine}"` — no new code needed there, just a witness.

**If it closes:** that's `standalone_closed` 67 → 68, `standalone_registered` 2 → 1. Only `…-ORCHESTRATOR-PROCEED-RESIDUAL` (operator-gated) would remain → then R-FS-1 resolves → R-CL-Q1 quality track admits.

---

## 6. The crash-resume family context (so the above makes sense)

R-FS-1's biggest sub-program is the **fan-out / sub-agent crash-resume family** — 34 closed arcs. The throughline: a maybe-ran step on a strict-tier crash-resume should RECOVER (re-dispatch under a deterministic `child_run_id` so the child's own crash-resume auto-resumes), not fail the run closed — while preserving **at-most-once** (committed effects never re-fire). Recent lineage you'll see cited:
- **#774/#777** — worker / orchestrator maybe-ran SUB_AGENT, LINEAR-{ESR,WAL}-leaf child.
- **#779/#781/#782/#784** — final_state reconstruction + child-recoverability across all 4 durable engine classes {ESR,WAL,SAVE_POINT,RECONCILER}. **#779→#781 is the SAVE_POINT-then-RECONCILER decompose precedent you're mirroring.**
- **#786** — NONLEAF-CHILD (nested grandchild recursion; the recursive `payload_child_recoverable` predicate is ONE SOURCE OF TRUTH, CP + runtime delegate to it).
- **#788** — FANOUT-CHILD {ESR,WAL} (the child is itself fan-out; reconstructs its AGGREGATE via `_crash_fan_out_resume`). Added the `_payload_engine_signature` cross-topology swap fold.
- **#790** — FANOUT-CHILD SAVE_POINT (this session). Your RECONCILER arc is the last sibling.

**At-most-once is the invariant.** The cross-topology swap guard (`_payload_engine_signature` folds `{engine_class, topology_pattern}` — the complete recovery-selecting pair) and the per-run seed disambiguator (`_linear_step_disambiguator`) are the protections; any new engine/topology admission must not reopen a swap. The `_DURABLE_AUTO_FENCE_ENGINE_CLASSES` (runtime) auto-activates the §14.22 effect fence for all 4 durable classes, so in-flight branch re-dispatch is fenced.

---

## 7. Gotchas / cautions (things that bit this session)

- **Dashboard `git_head` cell** exceeds Read/editor token limits → edit via Python `str.replace`.
- **Force-push is HARD-BLOCKED** by `tools/hooks/permission-guard.sh`. To update a pushed branch, add a follow-up commit (squash-merge collapses it); don't try to amend+force.
- **`git add -A` is HARD-BLOCKED** (and would sweep ~2500 untracked files). Stage explicit paths.
- **`rtk` wraps shell commands** — `rg -g`/parens/`find -not` get mangled; `git diff -- <pathspec>` strips `--`. Use dir-args, `-F`, omit pathspecs. `pyright`/`ruff` are not on bare PATH — use `uv run pyright` / `uv run ruff`.
- **The operator is non-coding.** Don't surface code findings for adjudication — verify them yourself via witnesses + the adversarial-reviewer. Surface only genuine architectural/scoping forks, credentials, paid-call authorization, or irreversible actions — and only when guessing is costlier than the round-trip.
- **A registered arc's `anticipated_scope` must not name a concrete `U-*` unit** (the arc-ledger `--check` enforces this) — describe scope, don't cite units.
- **Operator-owned files this session:** `CLAUDE.md` + `.claude/settings.json` were edited by the operator and landed in PR #792 (settings.json now runs `uv run pyright` on git-commit; CLAUDE.md §4.2 frozen snapshot is byte-exact `46/54 RETIRED (85.2%) + 49/54 pipeline-advanced (90.7%)` — note the *live derived* substitution count is `54/54`, a separate tally).

---

## 8. Quick-start checklist for your first Codex session

1. `git -C <repo> fetch && git merge --ff-only origin/main` (clean-behind).
2. Read root `CLAUDE.md` (§12 loop, §13 orchestration, §14 conventions) + `harness-cp/CLAUDE.md`.
3. Run the §12.1 session-start audit (the hash will lag by one — that's the expected fixed point, proceed).
4. `python3 tools/arc_ledger.py --check` → confirm 67/0/4/2.
5. Open the RECONCILER arc: read its `anticipated_scope` in `arc-ledger.yaml` + §5 above; ground the two-authorities + CAS/F-1 questions at the real code sites; build with a RED-without-fix by-execution witness; ship per §4.
6. Verify everything green, then do the §12.2 terminating refresh.

Good luck. The mechanism is well-trodden; the discipline (ground first, witness by-execution, preserve at-most-once, decompose honestly) is what keeps it correct.
