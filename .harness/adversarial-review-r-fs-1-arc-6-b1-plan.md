# Adversarial Review — R-FS-1 arc #6 (B1-plan) implementation-plan decomposition

## Summary

- **Review mode:** Phase-7 pre-merge implementation-plan review (P6-CK-class), pre-landing.
- **Severity scale used:** **§2.7.6 Phase-7 execution-fork scale** (per task directive, which overrides the SKILL.md §4.1 template scale). On THIS scale: **Class 1 = blocking** (halt-execution: spec contradiction / phantom cite / spec-extension / coverage gap / dependency cycle / cross-spec drift breaking byte-exact resolution); **Class 2 = substantive non-blocking** (in-execution operator decision); **Class 3 = informational / doc-hygiene**. The template's §4.1 polarity (Class 1 = minor, Class 3 = severe) is deliberately NOT used; section headers below are relabeled to the §2.7.6 polarity to avoid the conflation the SKILL.md warns against.
- **Artifacts reviewed:** `design-substrate/Implementation_Plan_Information_Substrate_v2_6.md` (U-IS-19); `design-substrate/Implementation_Plan_Harness_Runtime_v2_43.md` (U-RT-113, U-RT-114); `design-substrate/Implementation_Plan_Control_Plane_v2_32.md` (U-CP-80..U-CP-90 + the B1-arc aggregate dependency graph at its §3); `CLAUDE.md` line 62 (§2.4 plan-head pointer bump).
- **Owning specs verified byte-exact at HEAD:** CP `Spec_Control_Plane_v1_32.md` §25.10–§25.18; runtime `Spec_Harness_Runtime_v1.md` (v1.48) §2.2 / §9 / §14.5.3; IS `Spec_Information_Substrate_v1.md` (v1.8) §5.4. Plus the landed-contract cites (C-CP-10 §10.1/§10.3, C-CP-12 §12.2, C-CP-13, C-CP-29 §29.4, ADR-F2 v1.2 §Consequences (c)).
- **Date:** 2026-06-13
- **Finding count by class (§2.7.6 scale):** **Class 1 (blocking): 0** · Class 2 (substantive non-blocking): 0 · Class 3 (informational / doc-hygiene): 1
- **Highest-severity finding:** F3-01 (Class 3 informational — pre-existing CLAUDE.md §2.3 CP spec-head staleness; out of this PR's scope).
- **VERDICT: `APPROVE-WITH-CLASS-3`.** No blocking (Class 1) finding surfaced. The decomposition is transcription-faithful to the three cleared specs, the 14-node aggregate dependency graph is acyclic with correct cross-axis direction, coverage is complete with every disposition explicit, and the unit IDs are collision-free. One Class 3 informational note (§2.3 spec-head pointer, not introduced by this PR) is logged for transparency; it does not block.

---

## Class 1 findings (BLOCKING — halt-execution per §2.7.6)

**NONE.** No spec contradiction, phantom cite, silent spec-extension, coverage gap, dependency cycle, wrong-direction cross-axis edge, or byte-exact-breaking cross-spec drift was found across the three plans. The detailed verification supporting this "none" is in the "Findings considered and rejected" section below — it is the load-bearing audit, not a rubber-stamp.

## Class 2 findings (substantive non-blocking — in-execution operator decision per §2.7.6)

**NONE.** No spec-deferred decision was silently planner-decided (the carrier-home, async-structure, fan-out-cap, and `DriverStrategy`-shape deferrals are all correctly recorded as implementer-discretion at U-IS-19 Note (a) / O-CP-1 / O-RT-1, not pinned). No atomicity defect requiring operator re-scoping was found.

## Class 3 findings (informational / doc-hygiene per §2.7.6)

### F3-01 — CLAUDE.md §2.3 CP spec-head pointer is stale (`v1_30` vs cleared `v1.32`) — PRE-EXISTING, out of this PR's scope

- **Location:** `CLAUDE.md` line 58 (§2.3 Per-Axis Specs): "CP `Spec_Control_Plane_v1_30.md`". The cleared canonical CP spec at HEAD is `Spec_Control_Plane_v1_32.md` (cleared PR #529, marker present at `.harness/clearance/Spec_Control_Plane-v1_32-cleared-2026-06-13.md`).
- **Defect:** The §2.3 spec-head pointer lags the canonical CP spec by two versions (v1.30 → v1.32). The pointer still *resolves* (`Spec_Control_Plane_v1_30.md` exists on disk), so it is not a phantom cite — it resolves byte-exact to a real but superseded version.
- **Why Class 3 (informational), NOT Class 1:** (a) **Pre-existing, not introduced by this PR.** `git show HEAD:CLAUDE.md` line 58 already carries `v1_30`; this PR's CLAUDE.md diff touches ONLY §2.4 (plan heads), not §2.3 (spec heads). The staleness is the spec-clearing PRs' debt (#529 CP v1.32 should have bumped §2.3 and did not), not a defect of this plan-decomposition PR. (b) **Scope-correct for a plan PR.** A plan PR bumps plan-head pointers (§2.4); spec-head pointers (§2.3) are a spec PR's concern. This PR's §2.4 bump is exactly right and complete.
- **Precision:** Only **CP** §2.3 is stale. IS (`Spec_Information_Substrate_v1.md`) and Runtime (`Spec_Harness_Runtime_v1.md`) §2.3 pointers are **version-less filenames** that cannot go stale on filename (their canonical version is v1.8 / v1.48 inside the file). OD (`Spec_Operational_Discipline_v1_28.md`) is unrelated to this arc and not assessed.
- **Resolution path (informational):** Since CLAUDE.md is already open in this PR's working tree, the §2.3 CP pointer MAY be opportunistically bumped to `Spec_Control_Plane_v1_32.md` here (cheap, in-scope-adjacent). Alternatively, file it against a follow-on §2.3 cite-hygiene sweep (it is also flagged at CP spec v1.32 §-adjacent observation (a) as a Q1 doc-hygiene residual). Either is acceptable; neither blocks the plan decomposition.

---

## Findings considered and rejected (the load-bearing audit — what was actually checked)

Per the task done-bar, the verdict is auditable: each probe below was run by direct read of the specs + planner template, NOT by trusting the plans' own claims.

### Probe 1 — COVERAGE COMPLETENESS (the #1 plan defect class) — PASS

Every B1 spec subsection maps to ≥1 unit or an explicit disposition. The coverage matrices (IS §4.1, runtime §4.1, CP §4.1) were read directly and confirmed to contain these rows:

| Spec subsection | Disposition in plans | Confirmed |
|---|---|---|
| CP §25.10 (dispatch table) | U-CP-80 | ✓ (CP §4.1 row 1) |
| CP §25.11 (per-pattern + common substrate) | U-CP-81/82 (substrate) + U-CP-86..90 (5 strategies) | ✓ |
| CP §25.12 (buffered drain + determinism + context) | U-CP-81 (context) + U-CP-82 (drain) | ✓ |
| CP §25.13 (branch causality — Route-Y seam) | U-CP-81 (causality fields) + U-CP-84 (write-cadence producer) | ✓ |
| CP §25.14 (role seam) | U-CP-81 (`AgentRole` field, CP-half) + U-RT-114 (read, runtime-half) | ✓ |
| CP §25.15 (`cascade_policy` + 8 cascade-cancel obligations) | U-CP-85 | ✓ |
| CP §25.16 (branch-scoped idempotency-key) | U-CP-83 | ✓ |
| CP §25.17 (failure-mode taxonomy) | U-CP-80 (admissibility / no-longer-raises) + U-CP-85 (cascade-failure / barrier-deadline) | ✓ (no own unit — correctly cited by two units) |
| CP §25.18 (deferred-to-impl + recorded forks) | §6 Open-items O-CP-1 / O-CP-2 (no unit — implementer-discretion / already-resolved forks) | ✓ |
| runtime §2.2(a) (materialization site — existing stage-5 sufficient) | §6 Open-item O-RT-1 (no-change disposition) | ✓ ("no change needed" correctly NOT unit-ified per planner §3.1 atomicity) |
| runtime §2.2(b) drain / §2.2(c) write-cadence / §2.2(d) branch context | CP plan U-CP-82 / U-CP-84 / U-CP-81 (CP-driver-internal code home) | ✓ (runtime §0.2 + CP §4.1 cross-reference; the code lands CP-side, the runtime-spec contract is satisfied — coherent split by code-residence) |
| runtime §9 (`'partial'` projection) | U-RT-113 | ✓ |
| runtime §14.5.3 (role-read) | U-RT-114 | ✓ |
| IS §5.4 (`branch_metadata` carrier) | U-IS-19 (carrier shape) + U-CP-84 (producer/write-cadence, CP-side) | ✓ |

**No silently-uncovered subsection.** The §25.17→two-units, §25.18→O-CP-1/2, §2.2a→O-RT-1, and §2.2(b/c/d)→CP-side dispositions are each stated explicitly in the coverage matrices, not omitted. PASS.

### Probe 2 — NO SPEC EXTENSION (the plan's core risk) — PASS

Each unit's `Signatures introduced or modified` field was checked against the cited spec section, by direct read. The two load-bearing transcriptions named in the task:

- **U-IS-19 `BranchMetadata`.** Plan: three-field frozen record `parent_action_id: Identifier`, `branch_index: int (≥0)`, `terminal_status: Literal['cancelled', 'completed', 'timed_out'] | None`, plus optional 8th field `branch_metadata: BranchMetadata | None = None`. **IS spec §5.4 (lines 481–487) authors EXACTLY this:** the field-spec table commits `parent_action_id: Identifier`, `branch_index: Integer ≥ 0`, `terminal_status: {cancelled, completed, timed_out} OR None` (closed at cardinality 3, value-set CP-producer-owned per §25.15.2 obl. 4), and the "Optional 8th field" `branch_metadata` (line 471). The plan's `Literal[...]` rendering of the spec's closed-set is the correct Pydantic transcription, not a redesign. **No invented field.** PASS.
- **U-RT-113 `Literal['completed', 'drained', 'failed', 'paused', 'partial']`.** **Runtime spec §9 (line 2450) authors EXACTLY this Literal** verbatim. The plan's `_CP_TO_RT_STATUS[RunStatus.PARTIAL] = 'partial'` flip, the `failure_cause stays None` invariant, and the "no `degraded` field" stipulation each match runtime §9's invariants (lines 2462, 2465) verbatim. **No invented mapping or field.** PASS.
- **U-RT-114 role-read.** Plan: a read-substitution — the dispatch composer indexes `RoutingManifest.per_role_bindings[step_context.agent_role]`, fall-through to default on miss/`"default"`/empty-catalog; **NO new signature.** Runtime §14.5.3 (lines 3000, 3007) authors exactly the dispatch-read mechanism, the model-binding-only scope, the non-breaking-default invariant, and the per-role-prompt→B4 deferral. The plan correctly scopes OUT the per-role prompt (matching §14.5.3 "Model binding only"). **No spec extension.** PASS.

Spot-checks on the CP strategy units: U-CP-80's dispatch-map `{TopologyPattern → DriverStrategy}` with 6 entries matches §25.10.1's dispatch table verbatim (concrete `DriverStrategy` shape correctly left to §25.18 impl-discretion). U-CP-83's `idempotency_key = sha256(run_idempotency_key, step_index, branch_path)` matches §25.16 verbatim. U-CP-85's run-level mapping (`cascade-cancel→FAILED`, `proceed→PARTIAL`, `pause→PAUSED`, no new `RunStatus` value) matches §25.15.1 + §25.15.2 obl. 6 verbatim. **No unit invents a signature/field/behavior the spec does not commit.** PASS.

**Code-symbol reality check (the plans cite these as code-real):** verified by direct grep at HEAD — `_CP_TO_RT_STATUS` exists at `api.py:862` with the current `PARTIAL: "failed"` defensive placeholder (so U-RT-113's "flip from `'failed'`" is accurate); the CLI exit-code mirror `_CP_STATUS_TO_EXIT_CODE` at `cli/app.py:225` ALREADY maps `"partial": EXIT_WORKFLOW_FAIL` (so U-RT-113's "no exit-map edit" claim is accurate); `_MVP_DEFAULT_AGENT_ROLE = AgentRole("default")` exists at `llm_dispatch.py:281` used at line 490 (so U-RT-114's code-home + "replacing the hardcoded discard" claim is accurate); `_IN_SCOPE_TOPOLOGY = frozenset({SINGLE_THREADED_LINEAR})` at `workflow_driver.py:83` (so U-CP-80's "replace the gate" claim is accurate). PASS.

### Probe 3 — DEPENDENCY GRAPH ACYCLIC + cross-axis correctness — PASS (walked edge-by-edge, NOT trusting the plan's §3.3 proof)

The §3.1 per-unit dependency lists were walked against the §3.2 topological order independently:

- **(a) DAG / valid topological order.** All 14 nodes appear in the §3.2 order. Every one of the 14 dependency edges points to a strictly-lower unit in that order: `U-CP-82→[81]`, `U-CP-83→[81]`, `U-CP-84→[IS-19, 81, 82]`, `U-CP-85→[82,83,84]`, `U-CP-86→[80,82,84]`, `U-CP-87→[80,82]`, `U-RT-114→[CP-81]`, `U-CP-88→[80,81,82,84,85]`, `U-CP-90→[80,81,82,84,85]`, `U-CP-89→[88,85]`; foundationals (U-IS-19, U-CP-80, U-CP-81, U-RT-113) have no deps. **No back-edge.** Valid linear extension exists ⟹ DAG. PASS.
- **(b) Cross-axis edges.** Exactly two: **U-CP-84→U-IS-19 (CP→IS)** and **U-RT-114→U-CP-81 (RT→CP)**. Both run downstream in the package-dependency direction (`harness-runtime` → `harness-cp` → `harness-is`). Correct direction. PASS.
- **(c) IS-0-outbound cycle guard.** No U-IS-* depends on any U-CP-*/U-RT-* (U-IS-19 is `Depends on: (none)`, 0 outbound). So the inbound edge U-CP-84→U-IS-19 cannot close a cycle. PASS.
- **(d) HIERARCHICAL_DELEGATION (U-CP-89) `Depends on [U-CP-88]`.** Verified the spec basis: CP spec §25.11 (line 67) defines `HIERARCHICAL_DELEGATION` as "**Recursive `ORCHESTRATOR_WORKERS`** with depth." The `U-CP-89 → [U-CP-88]` edge correctly encodes "reuses, not parallels" — matching the spec's recursive definition. PASS.
- **No CP↔RT cycle.** The only CP↔RT edge is U-RT-114→U-CP-81 (RT→CP); no CP unit depends on any U-RT-* (CP strategies SET `agent_role` via U-CP-81; runtime READS it via U-RT-114). PASS.

### Probe 4 — ATOMICITY — PASS

- **U-CP-81 (the task-named probe): defensible as ONE unit.** It composes the branch child `StepExecutionContext` with `parent_action_id` + `branch_index` (causality) AND the `agent_role` field. This is a single coherent `StepExecutionContext`-shape extension at one composition point, not two changes. Both fields are **spec-authored on the same context**: runtime §2.2(4) lists the causality fields (`parent_action_id` + `branch_index`) AND names the `AgentRole` carry as the two runtime-owned deltas to the child context; CP §25.14 + §25.11 author `agent_role` on the same child context. So U-CP-81 is neither under-decomposed (one rollback boundary: the context-shape change) NOR a spec extension (both fields are committed). The plan's own Scope note ("split from the buffered-drain per the dependency discipline — the idempotency-key + role-read consumers need the *context*, not the *buffering*") is the correct atomicity rationale. PASS.
- **No over-decomposition.** The 5 strategy units (U-CP-86..90) are each a distinct driver strategy with a distinct rollback boundary; U-CP-84 (write-cadence) is consolidated as ONE tri-spec cross-cutting unit (correctly, per planner §5 — atomizing it per-spec would fragment one coherent producer-cadence change). PASS.
- **No malformed-example anti-patterns (planner template §5).** Grep confirmed ZERO risk/estimate/effort/story-point/T-shirt annotations across all three plans (§5.7 anti-pattern). No PR-title / commit-count / line-number pre-commitment (§5.8). Code file-path references (`api.py`, `llm_dispatch.py`, `workflow_driver.py`) are logical surface-names matching the established convention in predecessor plan v2.42 (which cites `procedural_tier_snapshot.py` etc.) — not the forbidden git-mechanics granularity. PASS.

### Probe 5 — SPEC-TRACEABILITY (byte-exact) — PASS

Every cite on the task's byte-exact list was resolved against the named spec at HEAD by direct grep/read:

- `C-CP-25 §25.10–§25.18` → `Spec_Control_Plane_v1_32.md` lines 26–171, all subsections present. ✓
- `C-RT-09 §9` → `Spec_Harness_Runtime_v1.md` line 2434. ✓
- `C-RT-15 §14.5.3` → line 2994. ✓ `C-RT-02 §2.2` → line 2080. ✓
- `C-IS-05 §5.4` → `Spec_Information_Substrate_v1.md` line 469. ✓
- `C-CP-10 §10.1` (six-pattern taxonomy) → `Spec_Control_Plane_v1_2.md` line 834; `§10.3` (cross-pattern admissibility, "fan-out cap 3 per parent") → line 865/872. ✓
- `C-CP-12 §12.2` (sub_agent_gate_level_descent) → `Spec_Control_Plane_v1_2.md` line 1004. ✓
- `C-CP-13` (HandoffContext) → present in `Spec_Control_Plane_v1_2.md`/v1_10/v1_17. ✓
- `C-CP-29 §29.4` (runtime consumer-site obligation) → `Spec_Control_Plane_v1_31.md` line 66. ✓
- `ADR-F2 v1.2 §Consequences (c)` ("What is now constrained downstream" → "per-workload-class extensions to the entry shape") → `ADR-F2.md` line 24/26 + line 32; version stamp v1.2 confirmed (line 6). ✓
- **No phantom / mis-resolving cite found.** **Unit-ID collision check:** highest existing units at predecessor plans are U-CP-79 / U-RT-112 / U-IS-18 (grep-confirmed). New units correctly start at U-CP-80 / U-RT-113 / U-IS-19 — **no collision.** ✓

*Scope note (not on the task's byte-exact list; landed-contract cites):* `C-IS-07 §7.5` (keying tuple) and `C-CP-01 §1.3` (`RoutingManifest.per_role_bindings`) are pre-existing landed contracts cited as composed-existing, not B1 surfaces — not chased per task scope. The CP §25.13 cite is correctly handled: §25.13 was a "FORWARD-COORDINATION REFERENCE (not a byte-resolvable cite)" in the CP spec; it is now satisfied by the landed IS v1.8 §5.4, and U-CP-84 correctly cites BOTH §25.13 (producer obligation) and IS §5.4 (the now-resolved carrier).

### Probe 6 — DELTA-FILE INTEGRITY — PASS

- **(a) Sections-preserved-verbatim declared.** Each plan's §0.3 carries an explicit preserved-verbatim table (IS: U-IS-01..17 + U-IS-18-as-RETIRED; RT: U-RT-01..112; CP: U-CP-01..79). ✓
- **(b) No silent re-authoring of preserved units.** Each plan's §2.1 references the predecessor for preserved bodies (delta-only-plan-chain convention); the new units are confined to §2.2. ✓
- **(c) Version bumps correct.** CP v2.31→v2.32, runtime v2.42→v2.43, IS v2.5→v2.6 — all match the predecessor files (which exist on disk) and the §0.1 predecessor declarations. ✓
- **CLAUDE.md §2.4 plan-head bump is exactly correct:** the diff bumps ONLY the three changed plan heads (IS v2_5→v2_6, CP v2_31→v2_32, RT v2_42→v2_43); core/AS/OD/CXA plan heads correctly untouched (those plans are unchanged this arc). ✓
- **Clearance markers present.** All three spec clearance markers (`Spec_Control_Plane-v1_32`, `Spec_Information_Substrate-v1_8`, `Spec_Harness_Runtime-v1_48`, all cleared 2026-06-13) exist at `.harness/clearance/` — the plans absorb cleared specs, ZERO X-AL-3 risk (plan-layer decomposition of cleared contracts; no spec amendment). ✓
- **Shared design authority** (`.harness/r-fs-1-b1-topology-orchestration-design-v1.md`) cited by all three §7 footers — exists. ✓

### Other attack vectors applied that did not surface a finding

- **X-AL-3 anti-extension (always-check):** ZERO spec amendment in any plan; each is a plan-layer decomposition of a cleared contract. No silent H_T design extension. No finding.
- **Halt-route-split-AC pattern:** runtime §2.2(a) (no-change) is correctly dispositioned as O-RT-1 (not bundled into a unit with materializable atoms); CP §25.18 deferred-items correctly split to O-CP-1 (impl-discretion) vs O-CP-2 (already-resolved forks). No mis-bundled AC. No finding.
- **Spec-prose-vs-plan-body drift:** the plan ACs (e.g., U-CP-84's "fresh terminal entry, never by mutating a prior entry → §6.3 chain intact"; U-CP-85's 8-obligation enumeration) match the current CP v1.32 / IS v1.8 spec bodies, not a stale version. No finding.
- **Verification-shape (grep-vs-e2e):** the units' integration ACs correctly demand e2e exercise ("Verified at B1-impl-N live e2e where a provider step is involved") for transit/behavior claims, not grep. No finding.
- **Carrier-home / cross-axis-isolation:** U-IS-19 correctly pins the one hard constraint (`BranchMetadata` NOT in `harness-cp`; IS 0-outbound) while leaving `harness-core` vs `harness-is` to impl-discretion — matching IS §5.4's deferral exactly. No axis-isolation leak. No finding.

---

## Disposition

**VERDICT: `APPROVE-WITH-CLASS-3`** (per the task's §2.7.6 scale: a pass with one informational note).

- **0 Class 1 (blocking).** The three plans faithfully decompose the three cleared B1 specs into 14 collision-free atomic units with: complete, explicitly-dispositioned coverage of every spec subsection; transcription-faithful signatures (the two load-bearing ones — `BranchMetadata` and the `'partial'` Literal — verified verbatim against IS §5.4 and runtime §9); an acyclic 14-node aggregate dependency graph with correct downstream cross-axis edges and an intact IS-0-outbound cycle guard; and clean delta-file integrity (correct version bumps, declared preserved-verbatim sets, present clearance markers, zero X-AL-3 risk).
- **0 Class 2 (substantive non-blocking).** No spec-deferred decision was planner-decided; no atomicity defect needs operator re-scoping.
- **1 Class 3 (informational).** F3-01: CLAUDE.md §2.3 CP spec-head pointer is two versions stale (`v1_30` vs cleared `v1.32`) — but this is PRE-EXISTING (already stale on HEAD) and out of this plan PR's scope (a plan PR owns §2.4 plan heads, not §2.3 spec heads; the §2.4 bump in this PR is correct and complete). Optionally fold the §2.3 CP bump into this PR since CLAUDE.md is already open; otherwise route to the CP-spec Q1 cite-hygiene sweep (already flagged at CP v1.32 §-adjacent (a)). Does not block.

**Recommendation:** merge the B1-plan cascade. The single Class 3 note is a transparency log, not a gate.

---

*Reviewer: harness-adversarial-reviewer (Phase-7 pre-merge mode). Severity per Project_Workflow §2.7.6 fork-class scale (per task directive). Verification by direct read of `Spec_Control_Plane_v1_32.md`, `Spec_Harness_Runtime_v1.md` (v1.48), `Spec_Information_Substrate_v1.md` (v1.8), the cited landed-contract specs, the implementation-planner template, and the at-HEAD code symbols — not by trusting the plans' own claims.*
