# Phase 7d Retirement Events — Batch 14

| Field | Value |
|---|---|
| Batch number | 14 |
| Filed at | 2026-05-24 (post U-RT-82 e2e exercise against real Anthropic API with `ANTHROPIC_API_KEY` supplied — 3/3 e2e tests pass at `03025cb`) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 invoked per RETIRE-READY → RETIRED operator-opt-in gate satisfaction (operator request following e2e exercise 2026-05-24) |
| Predecessor batch | `phase-7d-retirement-events-batch-13.md` (2026-05-23, 1 within-tier promotion PARTIAL → RETIRE-READY for H_T-CP-16; cumulative 22/49 RETIRED + 4 RETIRE-READY + 9 PARTIAL = 35/49 advanced per §4) |

---

## §0 Batch context

**Status type: 1 RETIRE-READY → RETIRED full retirement (H_T-CP-16). FIRST RETIRE-READY → RETIRED transition in the retirement ledger — establishes the close pattern for the operator-opt-in RETIRE-READY bucket introduced at batch-10 H_T-CP-18. Cumulative RETIRED count advances 22/49 → 23/49 (44.9% → 46.9%); RETIRE-READY count decrements 4 → 3; pipeline-advanced unchanged at 35/49 (71.4%) — within-tier promotion.**

This batch records a single RETIRE-READY → RETIRED transition for **H_T-CP-16** (Memory primitives + `memory.*` namespace consumption) following empirical exercise of the U-RT-82 e2e test against the real Anthropic API. The test was added at L9-octies cluster close `42c9a30` (2026-05-23, batch-13 §1.4) with explicit `@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), ...)` module-level gating; this batch is filed once that gate condition is satisfied.

The batch-13 §1.4 RETIRE-READY → RETIRED gate enumerated three operational sub-conditions:

> 1. Operator-supplied `memory_tool_backend_config` non-default at `RuntimeConfig` (i.e., `MemoryToolStorageBackend.FILESYSTEM` resolved with a concrete root path, not the default `EPHEMERAL_IN_MEMORY` placeholder)
> 2. Step payload contains `memory_20250818` tool definition (i.e., the workflow author opted the step into Memory tool participation)
> 3. `ANTHROPIC_API_KEY` available for live `messages.create` exercise against `claude-haiku-4-5` (or another Memory-tool-capable Anthropic model)

All 3 sub-conditions empirically satisfied at the U-RT-82 e2e exercise (see §1.1 evidence block below).

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + the operator-opt-in RETIRE-READY pattern close at this batch:

> RETIRED = (criterion A MET) ∧ (criterion B structural-MET) ∧ (criterion B operational-MET) — where operational-MET for the operator-opt-in bucket = (the operator-supplied config + step payload + external substrate exercise paths have been empirically traversed end-to-end at least once with the production composer in the loop).

Under that discipline, H_T-CP-16 transitions RETIRE-READY → RETIRED: criterion-A preserved from batch-11 §2.1 (U-AS-28 + U-AS-31 at AS axis); structural-criterion-B preserved from batch-13 §1.3 (runtime composer at `llm_dispatch.py` + 5-callback Protocol + LocalFilesystemMemoryToolBackend + registry + stage-5 factory + composer-step amendment); operational-criterion-B NEW at this batch via U-RT-82 e2e exercise.

**Conclusion (preview):** **1 new RETIRED transition** (H_T-CP-16) — cumulative **23/49 RETIRED** (46.9%, +1 from batch-13). **−1 RETIRE-READY** (H_T-CP-16 promoted out — RETIRE-READY count 4 → 3; remaining: H_T-CP-18 batch-10, H_T-CP-21 batch-11, H_T-AS-2 batch-12). PARTIAL count unchanged at 9. Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL): **35/49 = 71.4%** (unchanged from batch-13; bucket composition shifts +1 RETIRED / −1 RETIRE-READY). **First RETIRE-READY → RETIRED close in ledger history — establishes the empirical-evidence-driven close pattern for the operator-opt-in RETIRE-READY bucket.**

---

## §1 H_T-CP-16 RETIRE-READY → RETIRED

| Field | Value |
|---|---|
| Substitution ID | H_T-CP-16 |
| Primitive | Memory primitives + `memory.*` namespace consumption (CP-side runtime consumer of Anthropic Memory tool client-side primitive per ADR-D3 v1.2 §1.1 #11) |
| Substituted H_E surface | "`CLAUDE.md` hierarchy as memory; no `memory.*` namespace emission" (Meta-Arch v1.5 §5.4 row H_T-CP-16) |
| Prior status | RETIRE-READY per batch-13 §1 (2026-05-23 — PARTIAL → RETIRE-READY at L9-octies cluster close `42c9a30`; criterion-A MET + structural-criterion-B MET; operational-criterion-B GATED on `ANTHROPIC_API_KEY`-bound U-RT-82 e2e exercise) |
| Transition this batch | RETIRE-READY → **RETIRED** |
| Triggering arc | U-RT-82 e2e empirical exercise 2026-05-24 at HEAD `03025cb` (test fixture system-prompt tightening per FM-2 escape hatch + `ANTHROPIC_API_KEY` supplied + 3/3 e2e tests pass against `claude-haiku-4-5`) |

### §1.1 Operational-criterion-B exercise evidence

The 3 sub-conditions from batch-13 §1.4 RETIRE-READY → RETIRED gate enumeration, each verified empirically at the 2026-05-24 e2e exercise:

| Sub-condition | Evidence at U-RT-82 e2e exercise |
|---|---|
| (1) Operator-supplied `memory_tool_backend_config` non-default | `MemoryToolRegistry(backend=_RecordingBackend(...), configured_backend=MemoryToolStorageBackend.FILESYSTEM)` at test body — `_RecordingBackend` wraps a real `LocalFilesystemMemoryToolBackend(root=memory_backend_root)` (per-test `tmp_path` fixture). Not the default `EPHEMERAL_IN_MEMORY` placeholder. ✓ |
| (2) Step payload contains `memory_20250818` tool | Step payload constructed at `_step()` helper includes the Anthropic Memory tool definition with `type == "memory_20250818"` — verified by C-RT-15 inner-loop `execute_with_memory_callbacks(...)` invocation triggering on tool-name match. ✓ |
| (3) `ANTHROPIC_API_KEY` available for live `messages.create` | `os.environ["ANTHROPIC_API_KEY"]` resolved (sourced from `~/Projects/arhugula/.env` via dotenv-load at session startup); `AsyncAnthropic(api_key=api_key)` instantiated; `await client.models.list()` reachability check passed; full `messages.create(model="claude-haiku-4-5", tools=[memory_tool], ...)` exercise completed within ~4s. ✓ |

### §1.2 Empirical evidence block (test output)

Test run captured at 2026-05-24 against `claude-haiku-4-5`:

```
harness-runtime/tests/integration/test_u_rt_82_memory_tool_filesystem_e2e.py::test_memory_tool_filesystem_e2e_write_path PASSED [ 33%]
harness-runtime/tests/integration/test_u_rt_82_memory_tool_filesystem_e2e.py::test_module_skip_gate_present              PASSED [ 66%]
harness-runtime/tests/integration/test_u_rt_82_memory_tool_filesystem_e2e.py::test_module_importable                    PASSED [100%]
============================== 3 passed in 4.25s ===============================
```

**Per-AC observable outcomes verified at `test_memory_tool_filesystem_e2e_write_path`:**

| AC | Observable outcome at e2e exercise |
|---|---|
| AC #1 | Test completes within ~30s (actual: ~4s including build); `create` callback invoked on `_RecordingBackend` at least once with fixture path `/memories/notes.txt`; file present at `memory_backend_root / "notes.txt"` containing fixture content verbatim |
| AC #2 | Module-level `@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), ...)` gate present per `test_module_skip_gate_present` assertion (skip-without-key path verified previously at batch-13 §1.4 dry-run) |
| AC #3 | `_RecordingBackend.create` recorded in `calls` list — fixture-path + verbatim-content assertion both green |
| AC #4 | OTel span emitted with `memory.backend == "filesystem"` + `memory.path == "/memories/notes.txt"` + `memory.operation.kind == "write"` (assertions at test body lines 309-313) |

### §1.3 FM-2 test-fixture tightening — Class 3 record

The initial U-RT-82 e2e run at HEAD `42c9a30` against `claude-haiku-4-5` failed at the verbatim-content assertion (line 293):

```
AssertionError: file content mismatch: expected fixture content
  'User prefers concise responses with bullet points.'
in file body
  'User Preferences\n================\n\n- Prefers concise responses with bullet points\n'
```

The model paraphrased the fixture content into a markdown-styled note structure instead of writing the literal fixture string. The original system prompt asked the model to "save the following content" without explicitly forbidding reformatting.

Per the test docstring's FM-2 escape hatch ("Adjust the system prompt per FM-2 if recent model variant changes Memory tool invocation behavior"), the system prompt and user message were tightened at commit `03025cb` to require byte-for-byte content preservation. After the change, all 3 e2e tests pass.

**FM-2 discipline observation.** The test fixture change does NOT modify the production composer, contract, or Protocol surface — only the test prompt fixture. The fix lives entirely inside the test module per FM-2 no-extension discipline. The C-RT-15 §14.5.1 callback-injection inner loop and the C-RT-22 §14.12 5-callback Protocol are untouched. The runtime composer behavior under test is invariant against the prompt change — the prompt change adjusts only what bytes the LLM passes to the `content` parameter of the `create` callback. The composer correctly invokes the callback in both pre-fix (paraphrased content) and post-fix (verbatim content) runs.

**Class 3 record (not a fork).** Model-prompt sensitivity to verbatim-content discipline is a fixture-tuning concern, not a contract-shape defect. No design-phase artifact requires revision. Operator-discretion follow-on: future Memory tool e2e fixtures may need analogous prompt tightening if `claude-haiku-4-5` (or a successor variant) further drifts toward auto-formatting. This is logged as a Class 3 informational item per workspace `CLAUDE.md` §4.3.

### §1.4 No new gating dependencies

H_T-CP-16 RETIRED is now unconditional. No further operator-opt-in gates remain. The retirement is permanent under the prevailing runtime spec v1.17 + AS spec v1.5 + Meta-Arch v1.5 §5.4 cite shape.

Should a future spec revision extend the Memory tool surface (e.g., adding the `rename` callback per batch-13 §6(e) SDK-vs-harness 5-vs-6 callback asymmetry observation), the new surface would require its own retirement-event analysis at the time of landing — but the existing 5-callback retirement is not disturbed.

---

## §2 H_T-CP-17 status preservation

H_T-CP-17 (Files API consumer) status unchanged at this batch — remains PARTIAL per runtime spec v1.17 §14.C ratified Files-arc-deferred scope. No transition this batch. The Files arc opens only when operator authorizes a Phase-6-back-flow design extension per workspace `CLAUDE.md` §4.3.

---

## §3 Cross-axis cascade analysis

| Cascade endpoint | Disposition at this batch |
|---|---|
| §6.3.1 — H_T-CP-1 → H_T-AS-8 anthropic.* namespace emission | Unchanged — H_T-CP-1 RETIRED (batch 2); cascade discharged 2026-05-20. H_T-CP-16 RETIRED does NOT activate a new cascade (the `memory.*` namespace is already emitted via the L9-octies callback-injection inner loop landed at U-RT-81 commit `00d3132`; operational exercise via U-RT-82 confirms emission but does not change the cascade structure) |
| §6.3.2 — F-CP-01 Stage 3b inversion ordering | Unchanged — both endpoints RETIRED (batch 2 + authoring close v1 §1); cascade FULLY DISCHARGED at U-RT-58 landing arc per batch-3 |
| L9-octies cross-axis cascade per fork doc §5 + architect §13.6.D | ZERO new cascade — confirmed unchanged across batch-12 + batch-13 + this batch. CXA v2.8 unchanged. AS spec v1.5 §14.7 footer note already in place. OD-axis observability scope NOT affected by this RETIRED transition (the `memory.*` namespace emission is AS-side per C-AS-14, not OD-side) |

**Conclusion.** ZERO new cross-axis cascade triggered by the RETIRE-READY → RETIRED transition. The transition consumes the existing wire-up state without modifying any cross-axis edge.

---

## §4 Cumulative retirement state

**Workspace-wide post-batch-14:**

| Tier | Post-batch-13 | Delta this batch | Post-batch-14 |
|---|---|---|---|
| RETIRED | 22/49 (44.9%) | +1 (CP-16) | **23/49 (46.9%)** |
| RETIRE-READY | 4 (CP-18, CP-21, AS-2, CP-16) | −1 (CP-16 → RETIRED) | **3 (CP-18, CP-21, AS-2)** |
| PARTIAL | 9 | +0 | **9** |
| STILL-BOUNDED | 13 | +0 | **13** |

Sum: 23 + 3 + 9 + 13 = 48 ≠ 49 ✗ — the missing row is the 1 row carried out of the 49-row mapping table per batch-N footers (Meta-Arch v1.5 §5.4 carries a documented authoring-only retirement-target row that was authored-only-RETIRED at workflow close — preserved per prior batch accounting). Aggregate accounting matches batch-13 §4 totals shape exactly + this batch's +1/−1 shift.

**Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL):**

| Scope | Post-batch-13 | Post-batch-14 | Delta |
|---|---|---|---|
| Workspace-wide | 35/49 (71.4%) | 35/49 (71.4%) | unchanged (within-tier promotion) |
| CP-axis | 20/22 (90.9%) | 20/22 (90.9%) | unchanged (within-tier promotion) |

**CP-axis bucket breakdown post-batch-14:**

| Tier | Pre | Post | Delta |
|---|---|---|---|
| RETIRED | 10/22 (45.5%) | **11/22 (50.0%)** | +1 (CP-16) |
| RETIRE-READY | 3/22 (13.6%) | **2/22 (9.1%)** | −1 (CP-16) |
| PARTIAL | 7/22 (31.8%) | 7/22 (31.8%) | unchanged |
| STILL-BOUNDED | 2/22 (9.1%) | 2/22 (9.1%) | unchanged |

**Milestone.** CP-axis crosses the **50% RETIRED threshold** at this batch (11/22). First-ever workspace transition through this milestone for the largest axis (CP = 22 rows, 44.9% of the 49-row mapping table).

The within-tier promotion preserves the pipeline-advanced count; the composition shifts the H_T-CP-16 row from RETIRE-READY into RETIRED, reflecting the operational readiness gain from the U-RT-82 e2e empirical exercise.

---

## §5 Forward-only ledger discipline preservation

Per workspace `CLAUDE.md` §4.3 forward-only ledger discipline. This batch adheres:

- Prior batch records (1..13) NOT modified
- Only new batch-14 added + per-axis CLAUDE.md §4.1 forward-state refresh
- H_T-CP-16 row at `harness-cp/CLAUDE.md` §4.1 retirement-status table updated RETIRE-READY → RETIRED (status-column edit only; rationale + operational-exercise notes appended in-place per pattern at prior RETIRED rows; RETIRE-READY-bucket row count decrements 3 → 2; RETIRED-bucket row count increments 10 → 11)

---

## §6 Adjacent observations (NOT this batch's retirement event)

(a) **First RETIRE-READY → RETIRED close in ledger history — pattern catalogue.** The operator-opt-in RETIRE-READY pattern introduced at batch-10 (H_T-CP-18) accumulates rows pending external-substrate exercise; this batch closes the first such row. The close pattern is:

> 1. RETIRE-READY ledger entry enumerates the operator-opt-in operational sub-conditions at §1.4
> 2. Operator supplies the gating substrate (config / step payload / external service / API key)
> 3. The test infrastructure landed alongside the RETIRE-READY transition (here: U-RT-82) is exercised
> 4. Empirical evidence captured at a new batch §1.1 evidence block
> 5. RETIRE-READY → RETIRED transition recorded; bucket counts updated

This close pattern is the symmetric counterpart to the RETIRE-READY open pattern from batch-10/11/12/13. Future RETIRE-READY → RETIRED closes for H_T-CP-18 + H_T-CP-21 + H_T-AS-2 follow the same shape (gated respectively on `mcp_servers` config + external MCP server; `validator_framework` non-None; `mcp_servers` shared MCP substrate). Operator-discretion timing per existing 7d retirement-event cadence.

(b) **CP-axis 50% RETIRED milestone.** Per §4 cumulative table — CP-axis crosses 11/22 RETIRED at this batch. The 22-row CP axis is the largest axis in the 49-row mapping table; reaching half-RETIRED is a meaningful pipeline milestone. The remaining 11/22 CP-axis rows decompose as: 2 RETIRE-READY (CP-18, CP-21) gating on external-substrate exercise; 7 PARTIAL gating on workflow_driver invocation of already-landed library primitives; 2 STILL-BOUNDED (CP-23, CP-24 — both authoring-only / bridging-concept rows preserved per batch-1).

(c) **FM-2 test-fixture tightening as Class 3 record (per §1.3).** The system-prompt change at commit `03025cb` lives entirely inside the test module. No production code modified. Class 3 informational only.

(d) **Meta-Arch v1.5 §5.4 row H_T-CP-16 cite-shape augmentation candidate (carried from batch-13 §6(a)).** Still owed at next Meta-Arch amendment arc; this batch does NOT trigger Meta-Arch amendment. The runtime composer carriers U-RT-76..U-RT-82 (per batch-13 §1.1 augmented cite) materialize the production CP-side surface that satisfies criterion-B. Operator-discretion follow-on.

(e) **Cost-attribution under-reports memory-tool inner-loop iterations (carried from batch-13 §6(d)).** Still owed; OD-axis observability scope, not CP-axis substitution-retirement scope. Does NOT block this batch's RETIRED transition. Operator-discretion timing.

(f) **SDK `rename` command absent from harness Protocol (carried from batch-13 §6(e)).** Still owed at any future runtime spec amendment arc. The 5-callback retirement is not disturbed by the 6th-callback omission per the structural-decline pattern documented at U-RT-81 inner-loop body. Operator-discretion follow-on.

(g) **Test fixture lives at e2e module; not part of production composer surface.** Per §1.3 + §6(c) — the U-RT-82 test module's `_SYSTEM_PROMPT` + `_USER_MESSAGE` fixtures are workflow-author-supplied prompts in production (no harness-owned default prompt for Memory tool exercise). The test fixture serves only to drive the e2e exercise; it is not a contract surface. Workflow authors who want similar Memory tool exercise in production workflows author their own step-payload prompts at workflow manifest time.

---

## §7 Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/phase-7d-retirement-events-batch-14.md` |
| Batch number | 14 |
| Filed at | 2026-05-24 (post U-RT-82 e2e empirical exercise at `03025cb`) |
| Filing authority | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5; criterion-A MET (preserved from batch-11) ∧ structural-criterion-B MET (preserved from batch-13 §1.3) ∧ operational-criterion-B MET (NEW at this batch via U-RT-82 e2e empirical exercise per §1.1) for H_T-CP-16 → RETIRE-READY → RETIRED |
| HEAD at filing | `03025cb` (worktree `worktree-u-rt-82-e2e-prompt-tighten`); 3/3 e2e tests pass against `claude-haiku-4-5` per §1.2 evidence block |
| Predecessor | `.harness/phase-7d-retirement-events-batch-13.md` (2026-05-23, 1 within-tier promotion PARTIAL → RETIRE-READY for H_T-CP-16) |
| Successor | `.harness/phase-7d-retirement-events-batch-15.md` (TBD — likely additional RETIRE-READY → RETIRED transitions for H_T-CP-18 / H_T-CP-21 / H_T-AS-2 at operator-supplied-config + external-substrate-exercise events following same close pattern; OR additional PARTIAL → RETIRE-READY transitions for the 9 remaining PARTIALs at future runtime composer landings) |
| Related forks | `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` (RATIFIED-AMENDED 2026-05-23 — full arc closed; this batch records the operational-criterion-B close for the H_T-CP-16 half); `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` memory entry (status transition: RETIRE-READY → RETIRED post-this-batch) |
| MEMORY.md update owed | Update `[[h-t-cp-16-17-retire-ready-gate-runtime-composer-arcs]]` reflecting H_T-CP-16 RETIRED at batch-14 (operational gate met via U-RT-82 e2e empirical exercise); ADD new memory entry for the FIRST RETIRE-READY → RETIRED close pattern (§6(a) catalogue) — close pattern is the symmetric counterpart to the open pattern documented at batch-10 |

---

*End of Phase 7d retirement events batch 14. 1 RETIRE-READY → RETIRED (H_T-CP-16) — FIRST RETIRE-READY → RETIRED close in ledger history. Cumulative 23/49 RETIRED + 3 RETIRE-READY + 9 PARTIAL = 35/49 advanced (71.4%, unchanged from batch-13 — within-tier promotion). CP-axis crosses 50% RETIRED threshold (11/22). H_T-CP-17 preserved PARTIAL per spec §14.C Files-arc-deferred scope. ZERO new cross-axis cascade.*
