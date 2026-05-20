# Adversarial Review — Phase 2 Session 3 Track A atomic-decomposition plan

## Summary
- **Mode:** Phase-7 pre-implementation review (Session 3 plan red-team before Session 4 spec authoring + Track A unit landing opens)
- **Artifact reviewed:** `/Users/robertrhu/.claude/plans/noble-pondering-giraffe.md` (Track A atomic-decomposition plan for `harness-runtime/`, ~49 atomic units U-RT-NN across topological levels L0–L11)
- **Anchoring inputs cross-checked:** `.harness/phase-2-session-1-framing.md`, `.harness/phase-2-session-2-track-a-strawman.md`, `.harness/phase_2_fork_F-P2-1..F-P2-5_*.md`, `design-substrate/Cross_Axis_Composition_Document_v2_3.md` §2.3, landed code across `harness-{core,is,as,cp,od,cxa}/`, `design-substrate/Project_Workflow_v1_8.md` §2.6 exit criteria
- **Date:** 2026-05-19
- **Finding count by class:** Class 3: 0 · Class 2: 8 · Class 1: 3
- **Highest-severity finding:** F2-01 (stage-count drift across plan's own internal model)
- **Disposition recommendation:** **Current-phase plan revision before Session 4 opens** per §4.1.2. No Phase-7 §2.7.6 fork required (no halt-execution; defects are revision-internal to Session 3's deliverable, not upstream-phase revision triggers).

---

## Class 3 findings (severe — phase re-opening)

*None. All discriminator (b) and (c) walks miss. Plan respects framing commitments (multi-LLM preserved; persona uncommitted; stack honored; framework-pull discipline maintained); no upstream artifact revision is required.*

---

## Class 2 findings (moderate — current-phase plan revision)

### F2-01 — Stage-count drift across plan's own internal model
- **Location:** §1 package layout (`bootstrap/` shows files `stage_0_preamble.py` through `stage_7_ingress.py` — 8 files); §2 L0 U-RT-03 enum body (`stages 0–8 (PREAMBLE, IS, AS, CP_CLIENTS, CP_ROUTING, OD, LOOP_INIT, CXA_WIRING, INGRESS_ACCEPT)` — 9 stages); §2 L11 U-RT-49 AC ("touches stage 1–5" — 5 stages); §2 L9 U-RT-43 scope ("`bootstrap/__init__.py` runs stages in fixed order"); §2 L11 U-RT-50 scope ("stages 0–8 each have a focused integration test" — 9 stages).
- **Defect:** The plan asserts three different stage counts for the same bootstrap sequence. The package layout files (8) under-shoot the enum (9); the smoke-test AC (5) cites the strawman §3's original 5-stage count without reconciliation. The "8 conceptual stages" prose in the strawman §2 (preamble + 5 strawman stages + CXA + ingress + shutdown ≠ 8 either, depending on whether stage 0 counts) sits beside the 9-name enum without bridging text.
- **Discriminator:** (a) — affects substantive content of current-phase artifact; rectifying does not require revising the strawman or any fork-resolution record.
- **Evidence:** Three direct quotes above contradict each other on stage count. The enum drives `BootstrapStage.PREAMBLE..INGRESS_ACCEPT` which is `len()==9`; the file layout shows `stage_0..stage_7` which is 8 files; the U-RT-49 AC asserts coverage of "5 bootstrap stages" inherited verbatim from strawman §3 without reconciling.
- **Resolution path:** Pick one canonical stage enumeration (recommend the 9-value enum as authoritative since it's the runtime-visible contract); rename the bootstrap files to match the enum 1:1; rewrite U-RT-49 AC to assert coverage of all 9 stages by name or by enum membership; remove the "8 conceptual stages" prose drift.

### F2-02 — U-RT-33 conflates compile-time CXA seam imports with runtime instantiation
- **Location:** §2 L7 U-RT-33 ("Genuine seam instantiation (22 typed edges)" — "Scope: realize the 22 genuine typed CXA seams per CXA v2.3 §3 Pattern P1 — runtime constructs and exposes the byte-exact reference each consumer imports."); §4 unit-correspondence table footnote ("Plus U-RT-33 for the 22 genuine typed seams (Pattern P1 byte-exact).").
- **Defect:** Pattern P1 typed seams per CXA v2.3 §3 are *compile-time module imports* — the producer exports a name from its axis package and the consumer imports that name. The composition root does not "construct" or "instantiate" the seam; the import graph realizes it the moment the consumer module is loaded. U-RT-33's scope language ("runtime constructs and exposes the byte-exact reference") mischaracterizes Pattern P1. The unit as currently scoped is a *verification* unit (assert each of 22 seams is reachable; Pattern P1 identity test), not a *wiring* unit; it belongs at L11 (verification) alongside U-RT-49/50, not at L7 (CXA wiring) alongside the 24 phase-2-runtime edges. The CXA v2.3 reclassification (per strawman §2 + Explore agent's read of the doc) is explicit that the 22 typed seams "live as distributed cross-axis imports inside the 4 axis packages (not in `harness-cxa/`)" — they require no runtime instantiation.
- **Discriminator:** (a) — affects substantive content; resolving requires rewriting U-RT-33's scope and likely relocating it across topological levels. No upstream artifact revision required.
- **Evidence:** Strawman §2 — "Only composition root imports seam exports … terminal aggregate exporters are 'manifests, not wiring — explicitly composition surfaces live at the source units; this exports references only.'" The unit's own AC ("Pattern P1 alignment test (consumer reference identity-equal to producer export)") is an *assertion*, not a *wiring action*.
- **Resolution path:** Reframe U-RT-33 as a verification unit at L11 ("Pattern P1 import-graph completeness assertion"); make its scope a test that exercises the import of each of 22 producer modules and asserts identity-equality with consumer references; remove the "instantiation" framing. Optionally, an L7 unit may still be needed if the *terminal aggregate exporter manifests* (U-IS-17, U-AS-33, U-CP-54, U-CP-55, U-OD-34) need explicit runtime import for their side-effects — clarify which.

### F2-03 — No L2 unit for IS content-addressed-index reattach
- **Location:** §2 L2 IS bootstrap (U-RT-10 path resolver + U-RT-11 worktree manager + U-RT-12 state-ledger reattach); strawman §2 stage 1 "initialize the state ledger …, path-class registry, **content-addressed index**, semantic cache" (emphasis on what the plan dropped).
- **Defect:** Strawman §2 enumerates four IS bootstrap responsibilities at stage 1: state ledger, path-class registry, content-addressed index, semantic cache. The plan covers ledger (U-RT-12), path-class registry (U-RT-10), and worktree manager (U-RT-11), but is silent on content-addressed index reattach and semantic cache initialization. Landed `harness_is/` includes content-addressed-index modules; runtime needs to reattach them.
- **Discriminator:** (a) — coverage gap in current-phase artifact; does not require revising the strawman.
- **Evidence:** Strawman §2 stage-1 list quoted above; landed `harness-is/src/harness_is/` exports (per Explore agent) include the index surface; the plan's L2 cluster does not name a unit covering it.
- **Resolution path:** Add U-RT-09 (slot is empty — see F1-01) or U-RT-11b for content-addressed-index reattach + semantic cache init, dependency on U-RT-10, AC: index handle returned; cache hits observable; on missing-index path, fresh-create idempotent.

### F2-04 — Shadow-Git checkpoint / rollback runtime activation not enumerated
- **Location:** §2 L2 IS bootstrap; landed code under `harness-is/src/harness_is/shadow_git_checkpoint.py` (U-IS-14) and `shadow_git_rollback.py` (U-IS-15) per Explore agent survey.
- **Defect:** Shadow-Git checkpoint and rollback are landed IS primitives that require runtime activation (subprocess invocation of `git`, worktree-tier sub-role binding). The plan's L2 IS bootstrap does not name a unit that constructs or registers the shadow-Git surface at runtime. If U-IS-14/15 are landed as library-only (like U-OD-27 collector), runtime must instantiate the supervisor; if they're invoked on-demand from within other units, the on-demand invocation site needs naming.
- **Discriminator:** (a) — coverage gap in current-phase artifact; resolution does not require IS spec revision.
- **Evidence:** Explore agent's IS module survey lists `shadow_git_checkpoint.py` and `shadow_git_rollback.py`; plan L2 enumerates only `PathResolver`, `WorktreeIsolationManager`, and the ledger writer.
- **Resolution path:** Add a unit at L2 (or extend U-RT-11 worktree manager scope) covering shadow-Git checkpoint/rollback runtime binding, with AC tied to a round-trip checkpoint → rollback test against tmp `.harness/`.

### F2-05 — Drain semantics at U-RT-44 cite a CP primitive that may not be landed
- **Location:** §2 L10 U-RT-44 ("Scope: cooperative drain via CP lifecycle; bounded wait; typed timeout.").
- **Defect:** The plan asserts drain proceeds "via CP lifecycle" but does not cite a landed CP unit that owns drain semantics. F-P2-2 explicitly deferred operator-facing ingress to Track B, which may also have deferred the inverse (graceful drain). Landed CP modules per Explore agent survey include workflow lifecycle, override evaluator, topology — none of which obviously enumerate a "drain" primitive. If CP doesn't expose drain, U-RT-44 is forced to implement it inside `harness-runtime/`, which is fine but should be stated; if CP does expose it, cite the unit.
- **Discriminator:** (a) — under-specified scope in current-phase artifact; *potential* escalation to (b) if a CP spec gap surfaces at landing, but that converts to a §2.7.6 Class-1 fork at landing time, not now.
- **Evidence:** No CP unit ID cited in U-RT-44 scope; CP plan v2.10 enumeration in CLAUDE.md does not name a drain primitive in the unit count.
- **Resolution path:** Either cite the landed CP unit that owns drain, OR explicitly scope U-RT-44 to define `harness-runtime/`'s own drain semantics (signal-handler → set drained-flag → CP polls flag at lifecycle boundaries). Add to Risk §8 as candidate Class-1 surface at landing if CP turns out silent.

### F2-06 — Async/sync posture for provider SDK clients unpinned
- **Location:** §2 L4 U-RT-17 / U-RT-18 / U-RT-19 ("instantiate `anthropic.Anthropic(...)` / `openai.OpenAI(...)` / `ollama.Client(...)`"); §2 L9 U-RT-42 ("signature is `async def run(...)`; sync convenience wrapper documented").
- **Defect:** `anthropic`, `openai`, and `ollama` SDKs each expose both sync (`anthropic.Anthropic`) and async (`anthropic.AsyncAnthropic`) client classes. The plan names the sync variants for L4 client construction but commits Track A to an `async def run(...)` signature at L9. If sync clients are constructed and invoked from inside async contexts, the runtime blocks the event loop on every LLM call — a serious performance defect that surfaces only at integration. CP v2.10 routing core surface (`infer()` per Explore agent) does not pin async-vs-sync either.
- **Discriminator:** (a) — under-pinned current-phase decision; substantive.
- **Evidence:** Direct sync-client names in U-RT-17/18/19; `async def run` at U-RT-42; no reconciling statement.
- **Resolution path:** Pin async clients (`AsyncAnthropic`, `AsyncOpenAI`, `ollama.AsyncClient`) at L4 to match the L9 async posture; OR commit to `asyncio.to_thread()` wrapping at the routing-core call site and state it explicitly. Per asyncio stack mandate (`Target_Stack_Commitment_v1.md` §5.1), async clients are the cleaner fit.

### F2-07 — `Spec_Harness_Runtime_v1.md` authoring asserted as pre-condition but no gate / unit / verification enforces it
- **Location:** §5 spec recording strategy ("Author `Spec_Harness_Runtime_v1.md` *first* (post-fork-resolution, before U-RT-01 lands)"); §"Execution recommendations" step 1 ("Author `Spec_Harness_Runtime_v1.md` first").
- **Defect:** The plan recommends authoring the new runtime spec before any unit lands, but no atomic unit gates U-RT-01 on spec existence. A future executor reading only the unit list (skipping §5) will land U-RT-01 without the spec. The recommendation also conflicts with the unit-trace discipline: every U-RT-NN cites contracts from landed axis specs but cites no section of the runtime spec — meaning the units could land before the runtime spec is even drafted. This is a soft gate that needs hardening.
- **Discriminator:** (a) — structural defect in current-phase artifact; pre-condition needs explicit enforcement.
- **Evidence:** No U-RT unit lists "`Spec_Harness_Runtime_v1.md` exists" as a dependency; §5 prose recommendation is non-binding from the unit-graph's perspective.
- **Resolution path:** Either (a) add U-RT-00 ("Author `Spec_Harness_Runtime_v1.md`") as the unit-graph root with U-RT-01 dependency on it, OR (b) declare in plan preamble that Session 4 (spec authoring) is a hard gate on Session 5+ (unit landing), AND add a citation field to every U-RT unit pointing to the runtime spec section it implements.

### F2-08 — Acceptance criteria testability loose at U-RT-21, U-RT-24, U-RT-32
- **Location:** §2 L5 U-RT-21 ("manifest validates against R-2 + W-2; residence policy honored; **replay deterministic**"); §2 L5 U-RT-24 ("**transient staircase enforced**; breaker state machine wires; idempotency join wires"); §2 L6 U-RT-32 ("audit entries appended via IS ledger writer; multi-tenant separation enforced; chain integrity preserved").
- **Defect:** "Replay deterministic", "transient staircase enforced", "multi-tenant separation enforced" — each names an invariant without specifying the observable that proves it. §2.6 exit criteria require AC to be observable; these AC require reading the implementation to verify. U-RT-32's writer signature is also unspecified, so "audit entries appended via IS ledger writer" admits multiple implementations.
- **Discriminator:** (a) — AC precision below §2.6 exit criteria bar.
- **Evidence:** Direct quotes above; compare against tight AC like U-RT-10 ("all PathClass members resolve; missing paths created idempotently; resolver stored on `HarnessContext`") which names observable post-conditions.
- **Resolution path:** Rewrite each AC to name the test invocation that proves it. E.g., U-RT-21 replay determinism → "two `build_routing_manifest(config)` invocations against the same config produce byte-identical output"; U-RT-24 transient staircase → "injected transient fault N times surfaces N escalated retry intervals matching `validator_fail_transient_staircase` table"; U-RT-32 → name the writer-protocol entry point and a post-condition test.

---

## Class 1 findings (minor — documentation drift)

### F1-01 — Unit-numbering gap at U-RT-09
- **Location:** §2 L1 ends at U-RT-08; §2 L2 opens at U-RT-10. No U-RT-09 anywhere in the plan.
- **Defect:** Unit ID numbering skips 9. Not load-bearing, but a future reader will wonder.
- **Resolution:** Either backfill U-RT-09 (good slot for the content-addressed-index reattach unit per F2-03) or document the skip in §2 preamble.

### F1-02 — Strawman section-pointer prose unused
- **Location:** §2 preamble (`(strawman §N)` cites the Session 2 strawman.").
- **Defect:** The preamble declares a `(strawman §N)` citation convention but no unit body uses it. Either remove the convention statement or add the citations where the plan inherits strawman content.
- **Resolution:** Inline drop the convention statement OR add `(strawman §2)` / `(strawman §3)` to unit bodies that inherit responsibility decomposition / bootstrap order.

### F1-03 — Bootstrap file layout off-by-one with stage enum
- **Location:** §1 package layout `bootstrap/` lists `stage_0_preamble.py … stage_7_ingress.py` (8 files); §2 U-RT-03 enum lists 9 stages.
- **Defect:** File-count vs enum-count off-by-one; this is the cosmetic surface of F2-01 but emit separately to make the file-rename fix explicit.
- **Resolution:** Rename files to match the canonical stage enumeration chosen for F2-01.

---

## Findings considered and rejected (transparency)

| Check | Outcome |
|---|---|
| **A1 — Silent grounding collapse.** Did the plan cite primary sources for every substantive wiring decision? | Pass. Each unit cites landed module names (`harness_is.path_resolver`, `harness_cp.routing_manifest_residence`, etc.) and references the fork resolution records or strawman where applicable. No "engineering best practices" without source. |
| **A4 — Fabricated citations.** Do `.harness/phase_2_*` files referenced under "Critical files" exist? | Pass. `phase-2-session-1-framing.md`, `phase-2-session-2-track-a-strawman.md`, `phase_2_fork_F-P2-1_runtime_package_placement.md`, `phase_2_fork_F-P2-2_workflow_ingress.md`, `phase_2_forks_F-P2-3_4_5_runtime_lifecycle_ownership.md` all enumerated by directory listing. |
| **A8 — Framing contamination (highest-value vector).** Did the plan pre-commit persona, single-LLM, deployment surface, or pull in disallowed frameworks? | Pass. Multi-LLM preserved at U-RT-17/18/19/20 (3 provider SDKs under capability-aware abstraction). No persona commitment. Deployment surface stays config-driven via `RuntimeConfig`. Framework-pull discipline holds — U-RT-24 explicitly states "hand-rolled, no `tenacity`/`pybreaker`". |
| **Dependency-graph acyclicity (§2.6 exit criterion).** | Pass. Walked the L0→L11 graph; no cycles. L7 CXA wiring depends on L2–L6; no edge points backward. |
| **CXA edge total math.** Plan asserts 24 phase-2-runtime edges distributed as AS→IS=1, CP→IS=17, OD→IS=2, OD→AS=1, OD→CP=3. | Pass. Sum is 24; matches D-P2-2 and CXA v2.3 §2.3 reclassification (verified against Explore agent's enumeration of source-unit lists). |
| **Sub-agent boundary (CP-AL-1).** Does the plan conflate H_E sub-agent topology with H_T TopologyPattern enum? | Pass. U-RT-40 explicitly dispatches H_T's 6-class enum; U-RT-26 covers H_T sub-agent handoff (not H_E). The H_E vs H_T boundary holds. |
| **Substitution retirement preview completeness.** Does §6 cover the substitution categories Track A unlocks? | Pass. 8 categories enumerated against Meta-Architecture §5. Bounded-residual carry-forward to Track B explicitly named (operator-facing surfaces). |
| **Track-A vs Track-B scope boundary.** Does any unit poach Track-B responsibility? | Pass. CLI `run` correctly absent; topology selection algorithm absent (U-RT-40 only dispatches); TUI absent; markdown workflow authoring absent; operator-typed prompt → workflow absent. U-RT-47/48 are admin stubs only. |
| **IS state-ledger entry shape (Fork-001).** Does U-RT-12 honor the resolved 6-field entry shape from the previously filed state-ledger fork? | Pass. U-RT-12 cites `state_ledger_entry_schema`, `entry_hash`, `chain_link_construction`, `chain_verification` — all aligned to Fork-001's `.harness/state.jsonl` append/hash recipe per memory `[[fork-state-ledger-entry-shape]]`. |
| **Spec coverage (§2.6 exit criterion).** Does every spec element have at least one unit? | Partial-pass. Landed-axis spec elements are covered (path resolver, ledger writer, routing manifest, etc.). The plan's *own* runtime spec (`Spec_Harness_Runtime_v1.md`) does not yet exist, so its element coverage is provisional; F2-07 flags the gate. |
| **HITL placement in Track A.** Does U-RT-25 stay within Track A's wiring scope? | Pass. Registry instantiation + binding to landed CP/OD primitives. Operator-facing HITL UX is correctly deferred to Track B; U-RT-25 only registers placement and wires the response palette types. |

---

## Cross-artifact pattern detection

Single-artifact review; no cross-artifact pattern surfacing applies. Within this artifact:

- The stage-count drift (F2-01) repeats across at least three locations in the same plan (file layout, enum, AC). This is a *within-artifact* recurrence, not a §6 cross-artifact systemic pattern — but it indicates a single canonical enumeration was never committed.
- The "AC names invariant without observable" pattern (F2-08) recurs across U-RT-21, U-RT-24, U-RT-32 — three units in the same plan. Recommend a §7 audit pass *during* revision to walk every unit's AC list against the "name the test observable" bar before re-emitting.

---

## Disposition

**Recommendation: current-phase plan revision before Session 4 opens.** Per §4.1.2, 8 Class 2 findings → fork to plan revision (not phase re-opening). No Class 3 findings means no §2.7.6 Phase-7 fork is engaged; no upstream artifact (strawman, fork records, axis specs, ADRs) needs revision; the revision is internal to the Session 3 deliverable.

**Suggested revision order (one pass):**

1. **F2-01 + F1-03** — pick canonical stage enumeration; align package layout, enum, and ACs.
2. **F2-02** — relocate U-RT-33 to L11; reframe as verification not wiring; consider an L7 manifest-import unit for the terminal aggregate exporters if their import side-effects matter.
3. **F2-03 + F2-04 + F1-01** — backfill U-RT-09 (content-addressed-index reattach + semantic cache init); add a unit (or extend U-RT-11) for shadow-Git checkpoint/rollback runtime binding.
4. **F2-05** — pin drain ownership (cite landed CP unit OR scope to `harness-runtime/`-owned drain).
5. **F2-06** — pin async client variants at U-RT-17/18/19.
6. **F2-07** — choose Option (a) [add U-RT-00] or (b) [hard-gate Session 4 + add spec citation field to every unit]; recommend (a) for unit-graph cleanness.
7. **F2-08** — walk every U-RT AC list and rewrite invariants as test observables.
8. **F1-02** — drop the unused `(strawman §N)` convention statement or backfill the citations.

After revision, this skill does not need to re-review unless the operator wants a second pass. The defects are mechanical; a single revision cycle suffices.

---

*Authored 2026-05-19 by `harness-adversarial-reviewer` skill in Phase-7 pre-implementation review mode against the Session 3 atomic-decomposition plan. Report is read-only with respect to the plan; resolution paths describe defect-shape, not replacement text. No Phase-7 §2.7.6 fork engaged. Operator decides revision scope.*
