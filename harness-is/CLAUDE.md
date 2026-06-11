# harness-is/CLAUDE.md — Information Substrate (IS) Axis

*Per-axis subdirectory guidance for the IS axis. Loaded by Claude Code at session startup alongside workspace root `CLAUDE.md`. Canonical pointer to design-phase IS-axis artifacts.*

---

## 1. Axis identity + scope boundary

### 1.1 Axis identity

The Information Substrate (IS) axis owns **persistence**: state ledger, path-class registry, artifact-tier registry, hash-chain integrity discipline, JSONL composition contracts, shadow-Git checkpoint, worktree isolation, and substrate seam exports.

IS is the **consumer-most-upstream axis** per `Cross_Axis_Composition_Document_v2_19.md` §2.2: 0 outbound cross-axis edges; all other axes (AS / CP / OD) consume IS exports via U-IS-17 terminal aggregate exporter manifest. v2.1 → v2.17 refresh per CXA v2.17 §0.3 absorbing the 6-row CP→IS Pattern-P1 bucket growth at PR #92 commit `28259ed` 2026-05-31 (U-CP-74..U-CP-79 §16.5 CP→IS composer atomic-unit LANDED events at PRs #39-#44 2026-05-28..29; each composer consumer `harness_cp.<composer_module>` imports `EntryPayload` from `harness_is.state_ledger_write` per CP spec v1.25 §16.5.3 contract). **IS-axis outbound invariant PRESERVED VERBATIM at v2.17** (0 outbound to other axes; all IS-direction edges are inbound — v2.17 grew the CP→IS inbound bucket only).

### 1.2 Spec + plan authority

| Artifact | Version | Role |
|---|---|---|
| `Spec_Information_Substrate_v1.md` | **v1.7 — canonical HEAD** (delta-only chain; filename stays `_v1.md`, version tracked via in-file Revision rows. Latest delta v1.7 = R-PM-1 cascade PR #2 **prompts versioned authoring store**: NEW §5.3 `PromptManifest.versions: tuple[PromptVersion, ...]` content-addressed authoring store on the PROMPTS path-class (C-IS-01), added **alongside** the still-inline `active_prompt_version` (NOT generalized into it — §5.2 hash reader + runtime stage-5 injection reader byte-unchanged); content-addressing discipline (`version_sha = prompt_version_sha(content)`) + internal-coherence invariants (entries authored + content-addressed-unique; non-empty active is a store member) + `from_contents` builder; no runtime consumer (selection is PR #3 CP arc); empty store = #496/PR-#1 behavior verbatim. **§5.2 recipe SHAPE unchanged**; ZERO change to §5 six-field shape / §5.1 sidecar / §5.2 recipe / §6 / §7 / §10. Clearance `Spec_Information_Substrate-v1_7-cleared-2026-06-11.md`. v1.6 prior delta = R-PM-1 cascade PR #1 **prompts-management injection — §5.2 provenance-tightening**: NEW inline `PromptVersion.content` carrier (minimal PR #1 content source) + the `version_sha == prompt_version_sha(content)` derive-invariant (so injected content can't drift from the §5.2 hash); **§5.2 recipe SHAPE unchanged** (still 3-component, still reads `active_prompt_version.version_sha`) — provenance-tightening, not a recipe change; co-published with runtime spec v1.44 §14.5.2 injection. Clearance `Spec_Information_Substrate-v1_6-cleared-2026-06-11.md`. v1.5 prior delta = R-CL-P4 **prompts-management binding** (last open P4 blocker) — §5.2 "Prompts component deferred at v1.3" footer FLIPPED deferred → **bound**: third procedural-tier hash component `active_prompt_version` authored; recipe widens 2→3-component. `PromptManifest`/`PromptVersion` carriers at `harness_is.prompt_manifest` (mirror `RoutingManifest`, empty-defaultable); runtime `HarnessContext.prompt_manifest` field at runtime spec v1.42 §4 C-RT-04; forward-only hash rebase. ZERO change to §5 six-field shape / §5.1 sidecar / §6 / §7 / §10. Prior delta v1.4 = R-CL-P4 keying-tuple ↔ entry-shape reconciliation — NEW §7.5 ratifies **reading (iii)** (`thread_id`/`step_id` are `WriteKey` write-args, NOT persisted `StateLedgerEntry` fields; code-confirmed); §7.4 deferral flipped → resolved + stale F2-12 forward-cite refreshed; ZERO new contract, six-field shape PRESERVED VERBATIM, no code change. v1.3 = Phase 7 H_T-IS-2 apply-pass 2026-05-30 — additive NEW §5.1 `procedural_tier_snapshot_ref` sidecar + §5.2 resolver under C-IS-05; C-IS-02 §line-170 traceability canonical-reading patch; F-layer six-field shape §5 + §6 hash-chain + §7 read/write + §10 seam exports PRESERVED VERBATIM) | Contract authority — 10 contracts C-IS-01 through C-IS-10 |
| `Implementation_Plan_Information_Substrate_v2_5.md` | **v2.5 — canonical HEAD** (delta-only chain; this row's prior `v2.3` was the authoring-era pin — v2.4 absorbed IS spec v1.3 §5.1/§5.2 sidecar+resolver, v2.5 closed H_T-IS-2 by relocating U-IS-18 → U-RT-112 at runtime plan v2.42) | Execution authority — 17 atomic units across 6 clusters and 6 topological levels (L0–L5) (count cycled 17→18→17: v2.4 added U-IS-18, v2.5 retired it to U-RT-112) |

### 1.3 Scope inclusion (per IS plan v2.1 §4 coverage matrix; preserved verbatim at v2.3)

| Surface | Carrier units | Spec contract |
|---|---|---|
| Path-class registry (4-class enum + metadata schema + workflow-canonical resolver) | U-IS-01, U-IS-02 | C-IS-01 §1 |
| Artifact-tier registry (cross-tier traceability invariant) | U-IS-03 | C-IS-02 §2 |
| Git-tier substrate (worktree-aware) | U-IS-04, U-IS-05 | C-IS-03 §3 |
| Atomic deploy primitive (commit-grain reversibility) | U-IS-06 | C-IS-04 §4 |
| State-ledger entry shape (6-field idempotency-key carrier) | U-IS-07 | C-IS-05 §5 |
| Hash-chain integrity discipline (canonicalize → SHA-256 → chain construct → verify) | U-IS-08, U-IS-09, U-IS-10 | C-IS-06 §6 |
| F2-layer JSONL composition + idempotency-key join | U-IS-11, U-IS-12 | C-IS-07 §7 |
| Workload-class-opt-in shadow-Git checkpoint | U-IS-13, U-IS-14, U-IS-15 | C-IS-08 §8 |
| Workload-class-opt-in worktree isolation | U-IS-13, U-IS-16 | C-IS-09 §9 |
| IS substrate seam exports manifest | U-IS-17 | C-IS-10 §10 |

### 1.4 Scope exclusion

| NOT IS | Owning axis |
|---|---|
| Tool contracts, MCP integration, sandbox, Skills filesystem residence + reachability | AS — `harness-as/CLAUDE.md` |
| Routing, retry, breaker, workflow lifecycle, topology, HITL placement | CP — `harness-cp/CLAUDE.md` |
| HITL primitives, audit ledger schema, cost attribution chain, observability namespace emission | OD — `harness-od/CLAUDE.md` |
| Within-axis cycles | IS DAG is acyclic per IS plan v2.1 §3.4; cycle re-introduction is a Class 1 fork |

---

## 2. Per-axis canonical artifacts

### 2.1 Anchoring ADRs

Per `Phase_7_Meta_Architecture_v1.md` §2.1 IS-axis primitives:

| ADR | Version | Role |
|---|---|---|
| ADR-F2 | v1.2 | State ledger substrate |
| ADR-F3 | v1.1 | Engine event history |
| ADR-D1 | v1.2 | Engine + replay |
| ADR-D3 | v1.2 | Artifact filesystem residence |

ADD attestation: `Architectural_Design_Document_v1_3.md` v1.3.

### 2.2 IS export seams (consumed by AS / CP / OD)

Per U-IS-17 substrate seam exports manifest (C-IS-10):

| Export seam | Spec § | Consumed by |
|---|---|---|
| STATE_LEDGER_ENTRY_SHAPE_EXPORT | C-IS-10 §10.1 | AS, CP, OD |
| IDEMPOTENCY_KEY_JOIN_EXPORT | C-IS-10 §10.2 | AS, CP, OD |
| HASH_CHAIN_CONSTRUCTION_DISCIPLINE_EXPORT | C-IS-10 §10.3 | AS, CP, OD |
| FILESYSTEM_PATH_CONTRACT_EXPORT | C-IS-10 §10.4 | AS, CP, OD |
| JSONL_EVENT_LEDGER_FORMAT_EXPORT | C-IS-10 §10.5 | AS, CP, OD |
| WORKLOAD_CLASS_OPT_IN_MANIFEST_EXPORT | C-IS-10 §10.6 | CP only |

### 2.3 Cross-axis edge inventory (CXA v2.19 canonical reading)

*The `§2.3.x` cites below name the **v2.19 canonical reading**; the per-bucket row tables are preserved verbatim from the last full re-table at **v2.3** (§2.3.2 CP→IS last amended at v2.17), not byte-tabled in the v2.19 delta — per the delta-only chain (root `CLAUDE.md` §2 delta-baseline §-cite convention). v2.19 itself only restated §2.1 (aggregate matrix) + §2.4 (per-axis attribution).*

IS is consumer-most-upstream; all IS-direction edges are **inbound**:

| Source axis → IS | Edges | Source artifact |
|---|---|---|
| AS → IS | **11** (CXA v2.19 §2.1 canonical — set at v2.3 by the 2-spurious-edge strike; the v2.1 baseline value 13 was superseded) | `Cross_Axis_Composition_Document_v2_19.md` §2.3.1 (v2.3-canonical, preserved verbatim v2.3→v2.19); `Implementation_Plan_Action_Surface_v1_2.md` §3.4 still enumerates 13 — the documented, unresolved 13-vs-11 plan-vs-CXA divergence per FM-2 |
| CP → IS | 43 (was 36 at v2.1 baseline; 37 at v2.6/v2.9..v2.16; **43 at v2.17** per §0.3 absorbing 6 NEW Pattern-P1 typed seams at rows 38-43 for U-CP-74..U-CP-79 §16.5 composer atomic-unit LANDED events at PRs #39-#44 2026-05-28..29 per CP spec v1.25 §16.5.3 contract) | `Cross_Axis_Composition_Document_v2_19.md` §2.3.2 |
| OD → IS | **4** (CXA v2.19 §2.1 canonical = OD plan v2.6 §4.5.1 per C3-15 Path (i-refined) deletions; was 6 at the superseded v2.1 baseline) | `Cross_Axis_Composition_Document_v2_19.md` §2.3.4 (OD→IS bucket — §2.3.5 is OD→AS per canonical numbering; preserved verbatim through v2.19); drift recorded at `Implementation_Plan_Information_Substrate_v2_3.md` §0.9 (the CXA-OD-IS-EDGE-DRIFT was a phantom per CXA v2.19 §0.6 — OD→IS has been canonical 4 since v2.3) |
| **IS outbound** | **0** | IS exports surface via U-IS-17 manifest; consumers declare `Depends on` at consumer-side plans (invariant PRESERVED VERBATIM through v2.17) |

---

## 3. Topological entry-points (Level 0)

Per `Implementation_Plan_Information_Substrate_v2_1.md` §3.4 ASCII dependency graph (preserved verbatim at v2.3 §0.3):

| L0 unit | Implements | Cluster |
|---|---|---|
| U-IS-01 | Path-class registry schema (C-IS-01 §1) | Cluster 1 — foundational schemas |
| U-IS-03 | Artifact-tier registry schema (C-IS-02 §2) | Cluster 1 — foundational schemas |
| U-IS-04 | Git-tier substrate primitive (C-IS-03 §3) | Cluster 2 — git tier |
| U-IS-07 | State-ledger entry shape (C-IS-05 §5) | Cluster 3 — state ledger |
| U-IS-13 | Shadow-Git checkpoint schema (C-IS-08 §8) | Cluster 4 — checkpoint + worktree |

**5 L0 units; in-degree 0.** Phase 7 sub-phase 7b IS-axis-stream execution begins from these entry-points.

### 3.1 Full DAG topology (canonical at v2.1; preserved at v2.3)

```
LEVEL 0:   U-IS-01, U-IS-03, U-IS-04, U-IS-07, U-IS-13
LEVEL 1:   U-IS-02, U-IS-06, U-IS-08, U-IS-14, U-IS-16
LEVEL 2:   U-IS-05, U-IS-09, U-IS-10
LEVEL 3:   U-IS-11, U-IS-12
LEVEL 4:   U-IS-15
LEVEL 5:   U-IS-17 (terminal aggregate exporter)
```

DAG verified acyclic per IS plan v2.1 §3.4 Kahn execution: 17 units consumed; remaining edge set ∅.

### 3.2 Coverage matrix verification

Per IS plan v2.1 §4 (preserved at v2.3): 10 of 10 contracts covered by ≥1 unit; no coverage gaps. Coverage matrix per-axis-only per OD-S1-2.A; aggregate cross-axis matrix not composed.

---

## 4. Substitution + anti-leakage surface

### 4.1 IS-axis substitutions

Per `Phase_7_Meta_Architecture_v1.md` §5.2: **9 IS-axis substitution entries** across 6 substitution-mechanism categories. Substitution mechanism profile:

| Mechanism category | IS-axis carriers (selected) | H_E surface used |
|---|---|---|
| Convention | H_T-IS-1, H_T-IS-2 | `CLAUDE.md` path-class + tier-naming declarations + sub-agent compliance |
| Shell-out (`Bash`) | H_T-IS-4, H_T-IS-5, H_T-IS-6 | `Bash(git *)`; `Bash(python -c 'import hashlib...')`; `Bash(cat <<EOF >> .harness/state.jsonl)` |
| Composite | H_T-IS-7 | C3-pole: `Bash(cat <<EOF >>)` append; C2-pole: `Bash(jq ...)` or `Read` + Python `json.loads` filtering |
| H_E-direct | H_T-IS-8, H_T-IS-9 | H_E Checkpointing + `EnterWorktree`/`--worktree` worktree primitives |

Full per-substitution bounded-scope + retirement criterion at Meta-Architecture §5.2. Retirement bindings: U-IS-NN landings per the criterion column.

**Retirement status (post 7d batch 39 H_T-IS-4 STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY via sub-species 10 audit, 2026-05-28).** Per cumulative batch records `.harness/phase-7d-retirement-events-batch-{1..39}.md` + v2 ledger `.harness/phase-7d-retirement-ledger-v2.md` §3 under operator-ratified runtime-only substitution-site reading + line-33 strict-reading discipline. **Batch-39 advances H_T-IS-4 PARTIAL → RETIRED via sub-species 10 `gate-text-stale-vs-production-landings` audit** per workflow v1.12 §7.4.7.2 — categorical-mismatch retirement criterion (operator `Bash(git *)` IS the canonical deploy substrate per ADR-F2 §Decision, not a transitional substitution); X-AL-2 second conjunct vacuously satisfied via shape (3) H_E-surface-IS-canonical-substrate (distinct from OD-1 batch-37 shape (1) categorical-mismatch + OD-7 batch-38 shape (2) no-automated-H_E-surface). THIRD sub-species 10 closure in retirement ledger + FIRST cross-axis application (OD-axis origin → IS-axis). H_T-IS-2 subsequently advanced STILL-BOUNDED → PARTIAL (batch-49, substrate landed) → **RETIRED (batch-50, 2026-05-31)** — the substantive runtime gate at append-time cross-tier traceability (C-IS-02 §"Tier composition contract" line 170) is now enforced via the resolver-populated `procedural_tier_snapshot_ref` sidecar at every active-workflow-context producer site (R-003 producer-site cascade complete; X-AL-2 both conjuncts MET). **IS axis now 9/9 RETIRED = 100%** (FIRST axis fully RETIRED at the strict RETIRED view; see the IS-2 row + cumulative line below + `.harness/phase-7d-retirement-events-batch-50.md`).

| Substitution | Status | Source |
|---|---|---|
| H_T-IS-1 (path-class registry) | **RETIRED** 2026-05-20 | `stage_1_is.py` step 1 `materialize_path_registry`; convention surface displaced |
| H_T-IS-2 (artifact-tier registry) | **RETIRED** 2026-05-31 (batch-50; PARTIAL → RETIRED — substantive substitution-retirement) | Cross-tier traceability invariant now runtime-enforced at append-time: `EntryPayload.procedural_tier_snapshot_ref` populated via `resolve_procedural_tier_snapshot(ctx)` / `make_procedural_tier_snapshot_resolver(ctx)` (resolver residence pinned at runtime axis per Q-γ=(γ-2) per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` §11.4; sidecar field carrier + `StateLedgerEntry` D-derivative field + canonicalize contribution at harness-is per IS spec v1.3 §C-IS-05 §5.1 + §C-IS-06 §6.1). **All 13 producer sites handled** — 6 §16.5 CP→IS composers (PR #107 Reading C apply `89915af`) + 4 lifted (R-003 Cluster A PR #136: `sub_agent_dispatch` + `hitl_gate_composer`; Cluster B PR #137: `workflow_driver._append_step_ledger_entry` + `sibling_ledger_entry_composition`) + 3 documented `None`-canonical per IS §5.1 (`audit_writer`, `as_is_wiring`, `shadow_git_rollback` — entries written outside active-workflow context). X-AL-2 **BOTH conjuncts MET** (substrate landed batch-49 + convention surface no longer invoked at any active-workflow-context site; cross-tier traceability is programmatic + hash-chained, not manual). See `.harness/phase-7d-retirement-events-batch-50.md` |
| H_T-IS-4 (atomic deploy primitive) | **RETIRED** 2026-05-28 (batch 39 STILL-BOUNDED → RETIRED-AS-AUTHORING-ONLY via sub-species 10 `gate-text-stale-vs-production-landings` audit; categorical-mismatch shape (3) H_E-surface-IS-canonical-substrate) | Contract IS git-commit-atomicity per ADR-F2 §Decision + C-IS-04 §4 ("A 'deploy' event is the application of a single git commit ... All-or-nothing per commit precluded by git's commit atomicity at the storage layer"); operator `Bash(git *)` IS the canonical substrate not a transitional substitution; `verify_deploy_atomicity` verification primitive landed at harness-is; commit-message annotation deferred to operator per C-IS-04 §"Deferred to implementation discretion". X-AL-2 second conjunct vacuously satisfied — abandoning operator `Bash(git *)` would mean abandoning git as deploy substrate, foreclosed by ADR-F2 §Decision. See `phase-7d-retirement-events-batch-39.md` |
| H_T-IS-5 (state-ledger entry shape) | **RETIRED** 2026-05-20 | `lifecycle/state_ledger.py` driver-invoked at `workflow_driver.py:397-417` |
| H_T-IS-6 (hash-chain integrity) | **RETIRED** 2026-05-20 | `entry_hash.py` in-process `hashlib`; chain-verify at stage_1_is reattach |
| H_T-IS-7 (F2 read/write contract pair) | **RETIRED** 2026-05-20 | `state_ledger_write` + `state_ledger_read` both materialized at bootstrap |
| H_T-IS-8 (shadow-Git checkpoint) | **RETIRED** 2026-05-20 | `shadow_git_checkpoint.py:91` manifest-driven cadence gate |
| H_T-IS-9 (worktree isolation) | **RETIRED** 2026-05-20 | `worktree_isolation.py` manifest-driven opt-in + concurrency-cap |
| H_T-IS-10 (substrate seam exports manifest) | RETIRED (authoring close, v1 §1) | Authoring-only |

IS-axis post-batch-50 (2026-05-31): **9 / 9 RETIRED (100%) + 0 RETIRE-READY + 0 PARTIAL + 0 STILL-BOUNDED + 0 STILL-BOUNDED-INDEFINITELY = 9 ✓**. H_T-IS-2 PARTIAL → RETIRED at batch-50 closes the R-003 producer-site cascade (6 §16.5 composers PR #107 `89915af` + 4 lifted R-003 PR #136/#137 + 3 documented `None`-canonical); X-AL-2 both conjuncts MET. **FIRST axis fully RETIRED at the strict RETIRED view** (was 8/9 RETIRED + 1 PARTIAL post-batch-49). Pipeline-advanced 9/9 = 100% UNCHANGED (IS-2 was already pipeline-advanced as PARTIAL). Cumulative-counts line maintenance per workflow v1.12 §7.4.7.3.C retirement-tier-transit audit-template — refreshed at batch-50 publication in lockstep with the row-table gate-text + the post-batch-39 status paragraph tail (both stale-as-of-batch-49 carries closed at this transit).

### 4.2 IS-axis anti-leakage rules

Per `Phase_7_Meta_Architecture_v1.md` §7.2:

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| IS-AL-1 | `.claude/` hierarchy ≠ path-class registry. The 4 H_T path classes (`SKILLS` / `PROMPTS` / `ROUTING_MANIFEST` / `STATE_LEDGER`) are a typed registry with workflow-canonical resolution, not a filesystem-organization convention | Modeling H_T path classes after `.claude/` sub-directories |
| IS-AL-2 | H_E Checkpointing ≠ shadow-Git workload-class-opt-in checkpoint. H_E operates on session state at H_E-decided cadence; H_T operates on harness state at manifest-declared cadence | Authoring U-IS-13 to delegate checkpoint construction to H_E Checkpointing |
| IS-AL-3 | H_E conversation history ≠ state ledger entry shape. H_E retains `(role, content, tool_calls, tool_results)` tuples; H_T retains 6-field `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` entries per C-IS-05 §5 (relationship to the C-IS-07 §7.1 keying tuple deferred per C-IS-07 §7.4) | Re-deriving the H_T state ledger entry shape from H_E session history records |
| IS-AL-4 | `Bash` shell-outs are substitutions, not contracts. Hash-chain integrity via Python stdlib invoked through `Bash` is execution-time scaffolding; H_T contract at C-IS-06 is typed at U-IS-08/09/10 | Treating "we already have a Python script that does SHA-256 chain construction" as evidence that U-IS-08 is functionally complete |

Cross-cutting rules X-AL-1 (substrate boundary at MCP server process) / X-AL-2 (retirement criterion fidelity) / X-AL-3 (no silent H_T design extension) per Meta-Architecture §7.7 also bind IS-axis implementation.

---

## 5. Back-flow channels

Axis-specific design defects route per `Project_Workflow_v1_8.md` §2.7.6 + workspace root `CLAUDE.md` §4.3.

### 5.1 Class 1 routing by defect locus

| Defect locus | Class 1 routing |
|---|---|
| IS plan v2.3 atomic unit signature defect (acceptance criteria unimplementable; cross-unit dependency wrong) | Phase 6 plan revision-pass at design-phase workspace |
| IS spec v1.2 contract defect (C-IS-NN under-specifies the surface; spec inconsistent with ADR) | Phase 5 spec revision-pass at design-phase workspace |
| ADR-F2 v1.2 / F3 v1.1 / D1 v1.2 / D3 v1.2 anchor decision defect | Phase 3a/3b ADR revision via council convening |
| ADD v1.3 attestation mismatch with IS spec v1.2 | Phase 3d ADD revision |
| CXA v2.1 §2.3.1 (AS→IS) / §2.3.2 (CP→IS) / §2.3.5 (OD→IS) edge defect | Phase 6 CXA revision-pass at design-phase workspace |
| Cross-axis substrate seam (U-IS-17 manifest) defect | Phase 6 IS plan revision-pass; cascade to consumer-side plans if seam-export shape changes |

### 5.2 Open carry-forwards at IS axis entry

| Carry-forward | Status | Routing |
|---|---|---|
| CF-1 (F2-12) — D1 v1.1 → v1.2 replay-trace-emission contract | CLOSED at Phase 6 close cascade per `F2-12_Closure_Declaration.md` | No action |
| CXA-OD-IS-EDGE-DRIFT (Class 3) | CXA v2.1 §2.3.5 enumerates 6 OD→IS edges; OD plan v2.6 §4.5.1 enumerates 4 per C3-15 Path (i-refined) deletions. Cardinality drift surfaced at IS plan v2.3 §0.9 + OD plan v2.6 §0.9 | Non-blocking; future composition-document revision pass |

### 5.3 Filing footer

| Field | Value |
|---|---|
| Artifact | `harness-is/CLAUDE.md` |
| Authored at | Phase 6.5 Session 6 (ε), 2026-05-15 |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.2 |
| Predecessor | Design-phase workspace IS spec v1.2 + IS plan v2.3 |
| Revision policy | This file is canonical for the `harness-is/` subdirectory; revisions route to design-phase back-flow per §5.1 |

---

*End of `harness-is/CLAUDE.md`. Parent guidance at workspace root `CLAUDE.md`. IS spec + plan + CXA v2.1 §2.3.1 / §2.3.2 / §2.3.5 at design-phase workspace.*
