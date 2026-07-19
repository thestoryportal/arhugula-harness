# Spec — Information Substrate v1

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Information_Substrate_v1.md` |
| Status | **Proposed** (v1.2 pending Phase 6 entry per `Project_Workflow_v1_2.md` §3.1); final-revision-pass post-P5-CK iter-2 close per `Project_Workflow_v1_2.md` §4.1.2 modified path; coherence pass preserved verbatim as v1 + v1.1 historical record per Change-note §"§[coherence pass] preservation discipline" |
| Date | 2026-05-13 |
| Phase | 5 — specification authoring (session 1 of 4–6) per `Project_Workflow_v1_2.md` §2.5 |
| Skill | `spec-writer` SKILL.md in Stage-3 final-specification mode per skill description |
| Axis | Information Substrate (per `Phase_5_Entry_Handoff.md` §3.1 axis sequencing) |
| Source-set | `PRD_v1.0.md` §2 (R-IS-01 through R-IS-04); `Architectural_Design_Document_v1.md` v1.2 §2.2 + §5.2.2 + §5.3.3 + §6.3.1; `ADR-F2.md` v1.2 (§Decision + §Rationale (a) + §Rationale (a.1) + §Consequences (a)(b)(c) + §"Permanent tensions engaged"); `Persona_Document_v1.md` §3.1.1 + §3.1.3 + §5.1 + §7 + §8.1 + §10.1 + §10.2 + §10.4 |
| Entry authorization | `Phase_5_Session_1_Session_Prompt.md` §4 entry-gate verified (6/6); `Phase_5_Entry_Handoff.md` §5 preconditions verified |
| ODs applied | OD-5-1.A (per-axis multi-document) + OD-5-2.A (spec-writer judgment; Information Substrate per handoff §3.1) + OD-5-3.A (as-needed council consultant; no escalation invoked at session 1) + OD-5-4.A (aggregate P5-CK at full close) |
| Exit gate | This spec filed at `/mnt/user-data/outputs/`; §[coherence pass] returns ✅ PASS at all five audit dimensions; `Phase_5_Session_2_Session_Prompt.md` authored at session close |
| Revision | v1 → v1.1 (P5-CK iter-1 close mechanical + substantive revision per modified `Project_Workflow_v1_2.md` §4.1.2 path — F-IS-01 substrate-residence statement aligned with five-tier table episodic-row reading; F-IS-02 keying-tuple ↔ entry-shape reconciliation deferred to D-ADR on ledger schema via C-IS-07 §7.4 "Deferred to implementation discretion" subsection per ADR-F2 §Consequences (c); F-IS-03 reclamation operational semantic defined inline at C-IS-09 §9.2 per operator sub-decision; C-IS-01, C-IS-02 table, C-IS-03 through C-IS-10 substantive content preserved verbatim except as enumerated) |
| Revision date | 2026-05-13 |
| Revision | v1.1 → v1.2 (P5-CK iter-2 close final-revision-pass per modified `Project_Workflow_v1_2.md` §4.1.2 path — F-iter2-03 C-IS-10 §10.4 line 551 Action Surface row body-citation bump `ADR-D3 v1.1` → `ADR-D3 v1.2` at two sites (cell-name parenthetical + cell prose citation) per Pattern P2-PHASE-5 use-latest-version discipline; cited content materially unchanged at ADR-D3 v1.2 §1.8.1 Skills loading discipline per `P5-CK_Iteration_2_Close_Handoff.md` §3.5; all other contracts preserved verbatim) |
| Revision date | 2026-05-13 |
| Revision | v1.2 → v1.3 (Phase 7 H_T-IS-2 substitution-retirement apply-pass per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` operator-ratified 2026-05-30 (Q1=γ-family + Q1.1=γ + Q2=narrow + Q3=bundled + Q4=inline) + Q-α=(α-1) content-hash + Q-β=(β-3) direct-compute ratified at apply-pass session 2026-05-30 D1. NEW §5.1 D-derivative sidecar field `procedural_tier_snapshot_ref: Identifier \| None` authored per ADR-F2 §Consequences (c) extension authorization (the F-layer six-field shape at §5 PRESERVED VERBATIM; sidecar is additive at the D-derivative extension layer). NEW §5.2 `resolve_procedural_tier_snapshot(harness_context) -> Identifier` resolver contract — content-hash form `sha256(canonical_join(active_skills_versions ‖ routing_manifest_sha))` per Q-α=(α-1); prompts component deferred at v1.3 per apply-time empirical orientation surfacing absent runtime binding (no `active_prompt_version` field on `HarnessContext`; no `PromptManifest` carrier at HEAD); direct-compute storage (no separate registry; procedural artifacts persist at filesystem+git per §C-IS-02 line 163; resolver re-computes from current HarnessContext at every call) per Q-β=(β-3). §C-IS-02 line 170 inline canonical-reading patch reconciling MAY/MUST composition (action_id MAY encode action class per §5 field-spec footer; procedural-tier traceability MUST flow via the §5.1 sidecar field, NOT via action_id encoding) per Q4=inline. Engine-layer composers without HarnessContext access at firing time receive `resolve_procedural_tier_snapshot: Callable[[], Identifier]` as a kw-only parameter per CP spec v1.25 §16.5.7 + §16.5.8 `ledger_writer` kw-only-callable-bound-at-runtime-wiring precedent. ZERO change to F-layer six-field shape at §5; ZERO change to hash-chain construction at §6; ZERO change to read/write contracts at §7; ZERO change to seam exports at §10; ZERO cross-axis cascade at this arc per Q2=narrow (producer-site lifts at ~13 sites across CP / runtime / AS deferred to follow-on per-axis arcs per workspace `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent; H_T-IS-2 PARTIAL → RETIRED transit gated on full producer-site lift completion per X-AL-2 second conjunct). 54th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture at Q-α + Q-β collapse to single 4-option AUQ pre-AUQ-authoring (5 illegal/contradictory/redundant pairs foreclosed per advisor coupling analysis; AUQ authored over 4 legal pairs rather than sequential D1+D2 over 6 sub-options with operator-trap). NEW species candidate `[[procedural-tier-mutability-as-decisive-discriminator]]` catalogued at architect rec §7 (e) preserved at v1.3. v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention. 2026-05-30) |
| Revision date | 2026-05-30 |
| Revision | v1.3 → v1.4 (Post-MVP closure R-CL-P4 keying-tuple ↔ entry-shape reconciliation — operator-ratified **reading (iii)** 2026-06-10, re-confirmed 2026-06-11; fork `.harness/class_1_fork_keying_tuple_entry_shape_d_adr.md`. NEW §7.5 ratifies reading (iii): `thread_id`/`step_id` are write-time `WriteKey` write-arguments, NOT persisted `StateLedgerEntry` fields (code-confirmed at HEAD); `idempotency_key` is the sole persisted entry-level dedup discriminator. The C-IS-05 §5 six-field shape PRESERVED VERBATIM (inviolate per IS-AL-3); ZERO new contract / ZERO new entry field. §7.4 "Deferred to implementation discretion" keying-tuple clause flipped deferred → resolved-at-§7.5; the stale F2-12 forward-cite ("open downstream resolution path") refreshed (F2-12 CLOSED 2026-05-14 on an adjacent D1/D6 replay/cost-dedup scope, NOT this reconciliation per `[[stale-carry-text-disposition]]`). NO code change owed (the landed implementation already implements reading (iii)). ZERO change to §5 six-field shape / §6 hash-chain / §7.1–§7.3 read-write contracts / §10 seam exports. v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention. 2026-06-11) |
| Revision date | 2026-06-11 |
| Revision | v1.4 → v1.5 (Post-MVP closure R-CL-P4 **prompts-management binding** — operator-ratified 2026-06-11; fork `.harness/class_1_fork_prompts_management_surface_active_prompt_version.md` (DP-1..DP-4: mirror `RoutingManifest` / minimal binding). The §5.2 "Prompts component deferred at v1.3" footer is FLIPPED deferred → **bound**: the third procedural-tier hash component `active_prompt_version` is now authored — recipe widens to 3-component `sha256(canonical_json(active_prompt_version ‖ active_skills_versions ‖ routing_manifest_sha))`. The three §5.2 preconditions are satisfied: (1) `PromptVersion`/`PromptManifest` carrier types authored at `harness_is.prompt_manifest` (mirror `RoutingManifest`, frozen + `extra="forbid"`); (2) runtime `HarnessContext.prompt_manifest` carrier field authored at runtime spec v1.42 §4 C-RT-04; (3) resolver reads `ctx.prompt_manifest.active_prompt_version.version_sha` at write-time. Forward-only hash rebase (no migration of historical entries) per §5.2. **ZERO change to §5 six-field shape / §5.1 `procedural_tier_snapshot_ref` sidecar contract / §6 hash-chain / §7 read-write / §10 seam exports** — the recipe-internal component count is a §5.2 resolver detail, not an entry-shape change. The fuller prompts-management surface (multi-prompt versioning + selection) is a separate forward arc per fork DP-4. v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention. 2026-06-11) |
| Revision date | 2026-06-11 |
| Revision | v1.5 → v1.6 (R-PM-1 cascade PR #1 **prompts-management injection — §5.2 provenance-tightening** — operator-directed R-PM-1 capability arc #2 (`.harness/r-pm-1-prompts-management-design-v1.md`); fork `.harness/class_1_fork_prompts_management_surface_active_prompt_version.md` DP-5. The runtime-injection cascade (runtime spec v1.44 §14.5) carries the active prompt's *content* to the provider; for that content to participate in the §5.2 procedural-tier hash without silent drift, `active_prompt_version.version_sha` MUST be **content-derived** (`version_sha == prompt_version_sha(content)`). v1.6 adds the **minimal inline `content` carrier** to `PromptVersion` (`content: str = ""`, the self-contained PR #1 content source; PR #2 generalizes to the multi-version `PROMPTS`-path-class store) + the derive-invariant (detect-then-refuse at construction; `prompt_version_sha("") == ""` preserves the empty-carrier sentinel). **The §5.2 recipe SHAPE is unchanged** (still 3-component, still reads `active_prompt_version.version_sha`); only `version_sha`'s *provenance* tightens — this is a provenance-tightening, NOT a recipe change, so no hash-consumer cascade. The #496 minimal binding (v1.5) is the foundation, not a redo; PR #1 amends the just-cleared frozen `PromptVersion` carrier shape (clearance owed). Forward-compatible: empty-carrier configs (`content=""` → `version_sha=""`) are unchanged; configs that newly supply content rebase forward (as v1.5's recipe-widening already established). **ZERO change to §5 six-field shape / §5.1 sidecar / §6 hash-chain / §7 read-write / §10 seam exports.** v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention. 2026-06-11) |
| Revision date | 2026-06-11 |
| Revision | v1.6 → v1.7 (R-PM-1 cascade PR #2 **prompts versioned authoring store** — operator-directed R-PM-1 capability arc #2 (`.harness/r-pm-1-prompts-management-design-v1.md` §4.3 / §6 row #2); fork `.harness/class_1_fork_prompts_management_surface_active_prompt_version.md` DP-4 (multi-version surface). NEW §5.3 authors the `PromptManifest.versions` authoring store — a tuple of content-addressed `PromptVersion`s on the `PROMPTS` path-class (C-IS-01) — **added alongside the still-inline `active_prompt_version`, NOT generalized into it**. This is an additive, forward-only carrier widening: the §5.2 hash reader (`active_prompt_version.version_sha`) and the runtime stage-5 injection reader (`active_prompt_version.content`) are byte-unchanged. The store has **no runtime consumer at PR #2** — per-role/workload *selection* (which authored version is active) is the CP cascade arc (PR #3 §4.2), and that arc is what would later collapse `active_prompt_version` from an inline record to a pure sha-reference into the store. PR #2 lands the IS authoring substrate + the content-addressing discipline (`version_sha = prompt_version_sha(content)`, the v1.6 per-version invariant applied across a store) + internal-coherence invariants (store entries authored + content-addressed-unique; a non-empty active selection is a store member) + the `from_contents` authoring builder. Verified by carrier-coherence unit tests (the appropriate shape for an additive carrier with no behavioral path yet — there is no e2e to run until PR #3 wires selection). Empty `versions` (the default) preserves the #496/PR-#1 behavior verbatim. **The §5.2 recipe SHAPE is unchanged** (still 3-component, still reads `active_prompt_version.version_sha`). **ZERO change to §5 six-field shape / §5.1 sidecar / §5.2 recipe / §6 hash-chain / §7 read-write / §10 seam exports.** v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention. 2026-06-11) |
| Revision date | 2026-06-11 |
| Revision | v1.7 → v1.8 (R-FS-1 arc #4 — **B1-spec-1b non-linear-topology branch-causality carrier** — full-spec build program (`.harness/beyond-mvp-capability-boundary-ledger.md`; design `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` D1.a); the coordinated IS amendment CP spec v1.32 §25.13 forward-references (Route Y; fork `.harness/class_1_fork_b1_branch_causality_route_x_vs_y.md`). NEW §5.4 D-derivative `branch_metadata` sidecar on `StateLedgerEntry` / `EntryPayload` — optional 8th field (alongside the §5.1 7th) carrying fan-out branch causality (`parent_action_id`, `branch_index`) + the per-branch dispatch-boundary `terminal_status` (`{cancelled, completed, timed_out} | None`; value-set CP-producer-owned per CP spec v1.32 §25.15.2 obl. 4). **Producer-supplied** by the CP `WorkflowDriver` (not resolver-derived — no §5.2 analogue). Authors two carrier invariants: **append-only** (`terminal_status` set at a fresh terminal entry, never by mutating a prior entry — else the §6.3 chain breaks) + **dispatch-boundary-disposition-not-step-outcome** (a ran-and-errored branch is `completed`; no `failed` — step-outcome lives at the step entry per CP §25.15.2 obl. 3). Hash-level **forward-only, ZERO breaking change** via the established §5.1 omit-when-`None` canonicalization (`entry_hash.py`) — every pre-v1.8 entry carries `branch_metadata=None` → byte-identical canonicalization. Cross-spec reconciliation vs the sibling CP enums (`SubAgentResultStatus` C-CP-14 §14.2 / `CascadeDecisionAtFanoutClose` C-CP-15 §15.2 / `RunStatus` C-CP-25 §25.2) is **descriptive** (distinct tokens on distinct carriers; only `completed` shared, consistent meaning; no collision); the reciprocal CP cross-ref is flagged **Class 3 informational**. Carrier-home (`harness-core` vs `harness-is`) deferred to B1-impl-N; **hard constraint: NOT `harness-cp`** (IS 0-outbound invariant). **ZERO change to §5 six-field shape / §5.1 / §5.2 recipe / §5.3 / §6 hash-chain / §7 read-write / §10 seam exports.** v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention. 2026-06-13) |
| Revision date | 2026-06-13 |
| Revision | v1.9 → v1.10 (R-FS-2 Wave 2 — **B-18-LANEB-PROMPT-SEMVER, operator-declared semantic-version field on `PromptVersion`** — full-spec build program (`.harness/beyond-mvp-capability-boundary-ledger.md`; named at `.harness/u1-slice3b-epoch-partition-design.md` §5 row "Lane-B semantic-major" + §6 forward-arc registration; `.harness/u1-3c-prewarm-design-decision-record.md` §8). NEW §5.5 adds `PromptVersion.version: str \| None = None` — an operator-declared semantic-version label (the skill `frontmatter.version` analogue per ADR-D3 §1.8.1) distinct from the content-derived `version_sha`. **Explicitly optional and cache-inert**: NOT read by the §5.2 recipe (which reads only `active_prompt_version.version_sha`) and NOT subject to the §5.3 store's content-addressed-uniqueness invariant (uniqueness is keyed on `version_sha`; two store entries may carry the same operator-declared `version` label without violating (b)). Migration-tracking / lifecycle metadata only — `version_sha` remains the sole cache-correctness + content-identity key (per `u1-slice3b-epoch-partition-design.md` §2.2: "Adding a semantic-major field is … not required for the epoch primitive"). **ZERO change to** the §5 six-field shape / §5.1 sidecar / §5.2 recipe / §5.3 store invariants (a)/(b)/(c) / §5.4 `branch_metadata` / §6 hash-chain / §7 read-write / §10 seam exports — a pure additive field on the already-frozen `PromptVersion` carrier, defaulted `None` (byte-compatible with every existing manifest / construction call site). v1.9 + v1.8 + v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention. 2026-07-12) |
| Revision date | 2026-07-12 |
| Revision | v1.8 → v1.9 (R-FS-1 arc B4 — **per-role prompt threading ⊥ procedural-tier hash coherence** — full-spec build program (`.harness/beyond-mvp-capability-boundary-ledger.md`; arc-open grounding `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` Arc B4); bundled-absorption arc — the runtime per-role prompt injection co-lands in the same PR; fork `.harness/class_1_fork_b4_per_role_prompt_procedural_tier_hash_coherence.md`. The §5.2 content-hash recipe widens 3-component → **4-component**: NEW `prompt_selection_manifest_sha` (SHA-256 over the whole `PromptSelectionManifest` canonical-JSON bytes at `HarnessContext.config.prompt_selection_manifest` — the operator-supplied `RuntimeConfig` field, NOT a new carrier since it is not stage-enriched, so NO runtime-spec §4 C-RT-04 row is owed; `""` when `None`), **exactly mirroring `routing_manifest_sha`**. B4 makes a fan-out branch's per-role prompt take effect (its `content` injected at the §14.5.2 translate seam keyed on `step_context.agent_role`); the v1.8 recipe hashed only the resolved default-role `active_prompt_version.version_sha` + skills + the whole routing manifest — so per-role prompt-*selection* bindings were NOT hash-visible (flipping a `per_role_bindings` entry changed a branch's injected content while the procedural-tier hash reported "unchanged" — the §14.5.2 invariant violated for the per-role dimension; the tell: the routing manifest's own per-role bindings WERE already hash-visible via `routing_manifest_sha`). Route C (whole-selection-manifest hash, vs rejected Route A fold-into-`active_prompt_version` / Route B resolved-only) restores the invariant + the routing symmetry. Forward-only hash rebase (no migration of historical entries) per §5.2; `None`/empty selection → `""` (byte-identical to no-selection). **ZERO change to §5 six-field shape / §5.1 sidecar / §5.3 store / §5.4 `branch_metadata` / §6 hash-chain / §7 read-write / §10 seam exports** — the recipe-internal component count is a §5.2 resolver detail (the v1.5 recipe-widening framing). v1.8 + v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention. 2026-06-17) |
| Revision date | 2026-06-17 |
| Revision | v1.10 → v1.11 (B-48 apply arc — IS rider (d) — **C-IS-07 §7.1 buffered/branch-drain timestamp authority → WRITER-OWNED** — operator-RATIFIED 2026-07-18 (OPTION B with all filing-settled riders); fork `.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md` §4 item 7 + §5 rider (d); 16/16-CONFIRM C1⊥C9 apply-leg dyad `.harness/council-dyad-b48-apply-2026-07-18.md`. ONE ADDITIVE §7.1 table row + NEW §7.6: on the buffered/branch-drain append surface (the CP fan-out barrier drain per CP spec v1.32 §25.12 D1/D1.b feeding the single real writer), the persisted `timestamp` is sampled BY THE WRITER at each entry's append, INSIDE the write serialization point (the `_WRITE_LOCK` read-prior-then-append critical section at `harness_is.state_ledger_write.append_ledger_entry`) — replacing caller/drain-supplied timestamps captured outside the lock; the C-IS-05 §5 monotonic-non-decreasing constraint becomes enforceable BY CONSTRUCTION on that surface (two concurrent sibling drains can no longer append in capture-opposite order → `NonMonotonicTimestampError`; the superseded-for-routing defect record's §8.3 identifies this as a C-IS-07 write-contract change). ALL DIRECT append surfaces keep caller-supplied timestamp semantics VERBATIM under the existing detect-then-refuse enforcement; the §8.3 broader direct-path extension is a REGISTERED residual at §7.6, NOT absorbed. SPEC-APPLIED posture: the impl fix + strict-xfail removal (`test_concurrent_sibling_drains_invert_timestamp` flips to a passing witness; marker REMOVED) land at the B-48 impl arc — B-48 cannot close over an accepted-failing concurrency witness. Same-arc Runtime v1.102 + CP v1.102 deltas; IS plan absorption owed to implementation-planner; clearance marker owed. ZERO change to §5 six-field shape / §5.1–§5.5 / §6 hash-chain / §7.2–§7.5 / §8 / §9 / §10 seam exports. v1.10 + v1.9 + v1.8 + v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention. 2026-07-19) | (with the ONE rounds-28/29 exception: offloaded sub-agent audit appends adopt writer-owned sampling per §7.1/§7.6 — the B-48-owned carve-out).
| Revision date | 2026-07-19 |

---

## Change-note (v1.10 → v1.11)

**Scope of revision.** B-48 apply arc — IS rider (d) of the RATIFIED Class 2 fork `.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md` (operator selected OPTION B AS RECOMMENDED, 2026-07-18, with all filing-settled riders; §4 item 7 carries the defect, §5 rider (d) carries the IS back-flow), confirmed 16/16 by the C1⊥C9 apply-leg dyad `.harness/council-dyad-b48-apply-2026-07-18.md` (§5-d row). **The C-IS-07 drain-timestamp write-contract amendment**: ONE ADDITIVE row at the §7.1 C3-pole write-contract table + NEW §7.6. Landing the fix under Runtime deltas alone would silently change caller-supplied ledger-timestamp semantics without the authoritative IS contract moving — the superseded-for-routing defect record `.harness/runtime_defect_sub_agent_inference_child_loop_bridge_deadlock.md` §8.3 itself identifies the fix as a C-IS-07 §7.1 write-contract change ("today the timestamp is caller-supplied and merely *validated* non-decreasing; the fix makes the writer the timestamp *authority*"); hence this IS-owned delta.

**The amendment.** For the BUFFERED/branch-drain append surface (the CP fan-out barrier drain, CP spec v1.32 §25.12 D1/D1.b, feeding the single real writer), entry-timestamp authority moves INSIDE the IS writer's serialization point: the writer samples the persisted `timestamp` at each entry's append under the write lock (writer-owned), replacing the caller/drain-supplied `drain_timestamp` captured outside the lock (grounded at HEAD: `drain_branch_buffers` at `harness_cp.workflow_driver` captures `drain_timestamp` before any append and re-stamps every buffered payload; `_WRITE_LOCK` + the read-prior-then-append critical section live at `harness_is.state_ledger_write.append_ledger_entry`). The C-IS-05 §5 monotonic-non-decreasing constraint becomes enforceable BY CONSTRUCTION on that surface — two concurrent sibling drains can no longer serialize their physical appends in capture-opposite order (the pinned `NonMonotonicTimestampError` inversion). ALL DIRECT append surfaces keep caller-supplied timestamp semantics verbatim with the existing detect-then-refuse enforcement. Precise surface split + the registered direct-path residual (the defect record's §8.3 broader fix-direction is NOT ratified here) at §7.6. SCOPE WIDENING (B-48 apply-PR codex round-28 — a consequence of the arc's OWN new concurrency, distinct from the `B-57` general direct-writer residual): the offloaded sub-agent dispatch AUDIT append path (`sub_agent_dispatch.py:713-725` samples `time_source()` BEFORE the write lock; two concurrent sync siblings' success paths can invert and fail an otherwise-successful branch as `SubAgentDispatchAuditComposeError`) is ALSO covered — its appends sample writer-owned under the lock (or are equivalently serialized) at the B-48 impl arc; `B-57` continues to cover the OTHER direct writers.

**SPEC-APPLIED posture + witness obligation.** This delta is spec-only; the implementation fix + the removal of the strict xfail marker on `test_concurrent_sibling_drains_invert_timestamp` (`harness-cp/tests/test_workflow_driver_buffered_append.py` — the test asserts the CORRECT behavior this contract commits and flips to a PASSING witness when the fix lands) belong to the B-48 impl arc. B-48 cannot close over an accepted-failing concurrency witness.

**Cross-references (same arc).** Runtime spec v1.101 → v1.102 delta (co-resident on this apply branch — the B-48 executor-offload Runtime rider) + CP spec v1.102 delta (the C-CP-25 §25.11 fan-out cap-gating rider, co-landing in this apply arc). IS plan absorption of this contract change is owed to `implementation-planner` revision-pass (fork §5 rider (d) names "IS spec **+ plan** back-flow") — flagged here, not done here. Clearance marker owed at `.harness/clearance/` in the landing PR.

**Sections preserved verbatim at v1.11.** §Status block (rows appended only); §1–§4; **§5 C-IS-05 six-field shape + §5.1–§5.5** (the §5 `timestamp` field row is byte-unchanged — writer-owned sampling on the drain surface *realizes*, and does not alter, its "wall-clock instant the entry was written" semantic and monotonic constraint); §6 C-IS-06 hash-chain; **§7.1 table rows 1–6 byte-unchanged (ONE additive row appended)**; §7.2–§7.5; §8; §9; §10 C-IS-10 seam exports; §[carry-forwards]; §[traceability]; §[coherence pass]. ZERO change to the F-layer six-field shape, hash-chain construction, read contract, idempotent-write keying, or seam exports. v1.10 + v1.9 + v1.8 + v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention.

---

## Change-note (v1.9 → v1.10)

**Scope of revision.** R-FS-2 Wave 2 standalone `B-*` arc **B-18-LANEB-PROMPT-SEMVER** (owner IS; bundled-absorption). Named at `.harness/u1-slice3b-epoch-partition-design.md` §5 ("Lane-B semantic-major — add an operator-declared semantic-version field to `PromptVersion` (skill `frontmatter.version` analogue)") + §6 forward-arc registration, and carried forward at `.harness/u1-3c-prewarm-design-decision-record.md` §8 ("`B-18-LANEB-PROMPT-SEMVER` | operator-declared semantic-version field on `PromptVersion` | IS-spec amendment; NOT required (version_sha is the cache key)"). The one-time strike window at the R-FS-2 Unit-0 PR review (#934) passed unexercised, so this BUILDS per FULL-SPEC discipline (a documented, ratified-but-unbuilt mechanism is a build target, not a resting deferral).

**The amendment — NEW §5.5 `PromptVersion.version` operator-declared semantic-version field.** A single additive optional field `version: str | None = None` on the already-frozen `PromptVersion` carrier (`harness_is.prompt_manifest`), mirroring the skill `frontmatter.version` concept ADR-D3 §1.8.1 committed for Skills ("operator may bump `frontmatter.version` … without changing every byte," both-required alongside `skill.version_sha`) — except for prompts the field is **optional**, since (unlike Skills, where `version` is a required frontmatter constraint enforced at the load seam per B-SKILL-FRONTMATTER-VALIDATOR, R-FS-2 Wave 1) no committed contract requires prompt versioning to carry an operator-facing semantic label.

**Why optional, and why NOT the cache/identity key.** `u1-slice3b-epoch-partition-design.md` §2.1-§2.3 established (empirically, ahead of this amendment) that Anthropic's prompt cache is byte-exact, so the only cache-correct identity for "which dispatches can share a warm cache" is the byte-exact content hash — `version_sha`. A coarser semantic-version key would be a cache-correctness bug (two different-byte prompts sharing an operator-declared "major version" do not share a cache entry). `version` is therefore purely a migration-tracking / operator-lifecycle label — orthogonal to, and never substitutable for, `version_sha`.

**Cache-inertness (verified, not merely asserted).** Every production consumer of `PromptVersion` reads either `.version_sha` (the §5.2 recipe's `active_prompt_version` component; the CP `cohort_key` / cacheable-epoch `prefix_content_hash` derivations at `harness-runtime`) or `.content` (the runtime stage-5 injection reader) — never the full serialized model. Adding `version` therefore cannot participate in any hash, cohort key, or cache-epoch identity by construction; no code beyond the carrier field is required to preserve cache-inertness. The field is grounded here explicitly per the workspace's new-surface-audit discipline (`[[new-surface-audit-hash-and-config-not-carrier]]`) precisely because it is easy to *assume* inertness without checking every consumer — this amendment checks.

**§5.3 store interaction — free-text, not a uniqueness dimension.** `PromptManifest.versions`' content-addressed-uniqueness invariant (§5.3 (b): no two store entries share a `version_sha`) is keyed on `version_sha` only. `version` carries **no** uniqueness constraint — two store entries may declare the same operator label (e.g. two entries both labeled `"1.0"` during a rename/rebase) without violating (b); the label is descriptive metadata, not a second identity axis. This is a deliberate design choice (mirroring how skill `version` labels are not required to be globally unique across skills either) — enforcing uniqueness on an operator-facing convenience label would be a scope-creeping invention beyond what any cited authority commits.

**Sections preserved verbatim at v1.10.** §Status block (rows appended only); §2 C-IS-01 + C-IS-02; §3; §4; **§5 C-IS-05 six-field shape + §5.1 sidecar + §5.2 recipe + §5.3 store invariants (a)/(b)/(c) + §5.4 `branch_metadata`** (all byte-unchanged — §5.2 does not read `version`; §5.3's (a)/(b)/(c) invariants are keyed on `version_sha`, untouched by an orthogonal free-text field); §6 C-IS-06 hash-chain; §7; §8; §9; §10 C-IS-10 seam exports (the entry-shape / prompt-manifest export surfaces travel the new optional field with zero seam-shape change). **ONLY a NEW §5.5 sub-section is appended at the end of §5.** ZERO change to the F-layer six-field shape, hash-chain construction, read/write contracts, the §5.2 recipe, or seam exports. No ADR revision — ADR-D3 §1.8.1 already commits the analogous Skills concept; this amendment ports the pattern to prompts at IS-spec level only. v1.9 + v1.8 + v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention.

---

## Change-note (v1.8 → v1.9)

**Scope of revision.** R-FS-1 arc **B4** (per-role / per-step dispatch indexing; full-spec build program — spine `.harness/beyond-mvp-capability-boundary-ledger.md`; arc-open grounding `.harness/r-fs-1-remaining-arcs-grounding-sweep-v1.md` Arc B4). **Bundled-absorption arc:** this IS §5.2 recipe widening is the coherence half of an arc whose runtime per-role prompt injection co-lands in the same PR (per-role prompt threading at `harness-runtime` stage-0/stage-5/dispatch). Back-flow doc: `.harness/class_1_fork_b4_per_role_prompt_procedural_tier_hash_coherence.md` (Class 1, RESOLVED — design back-flow FULL-SPEC-pre-authorized; reversible additive recipe component mirroring `routing_manifest_sha`; no operator gate, no ADR/six-field/§6/§7 change).

**The amendment — §5.2 recipe 3-component → 4-component.** A single additive component `prompt_selection_manifest_sha` (SHA-256 over the whole `PromptSelectionManifest` canonical-JSON bytes at `HarnessContext.config.prompt_selection_manifest` — the operator-supplied `RuntimeConfig` field, NOT a new top-level carrier, since it is not stage-enriched; `""` when `None`), inserted in alphabetical position between `active_skills_versions` and `routing_manifest_sha`. **Exactly mirrors `routing_manifest_sha`** (no runtime-spec §4 C-RT-04 row owed — reads existing config).

**Why (the coherence gap B4 surfaced).** B4 injects a fan-out branch's per-role prompt `content` (keyed on `step_context.agent_role`) at the §14.5.2 translate seam. The v1.8 recipe hashed only the resolved default-role `active_prompt_version.version_sha` (+ skills + the whole routing manifest), so per-role prompt-*selection* bindings were not hash-visible — flipping a `per_role_bindings` entry changed a branch's injected content while the procedural-tier hash reported "unchanged" (the §14.5.2 invariant violated for the per-role dimension). The tell: the recipe already made the routing manifest's per-role bindings hash-visible via `routing_manifest_sha`; the prompt-selection manifest's were not. Route C (whole-selection-manifest hash) restores both the invariant and the routing symmetry. Rejected: Route A (fold per-role shas into `active_prompt_version` — breaks the single-active-version semantics the §14.5.2 injection reader depends on); Route B (resolved-per-role-only — incomplete + asymmetric).

**Forward-only, additive.** Hash rebases forward (no migration of historical entries; snapshot-ref equality scoped within a recipe-version generation — exactly as the v1.3/v1.5 prose anticipated). `None`/empty selection → `""` (byte-identical to a no-selection run). **ZERO change to** the §5 six-field shape / §5.1 `procedural_tier_snapshot_ref` sidecar / §5.3 versioned store / §5.4 `branch_metadata` / §6 hash-chain / §7 read-write contracts / §10 seam exports. The recipe-internal component count is a §5.2 resolver detail (the same framing as the v1.5 prompt-component binding). v1.8 + v1.7 + v1.6 + v1.5 + v1.4 + v1.3 + v1.2 + v1.1 + v1 PRESERVED VERBATIM per delta-only convention.

---

## Change-note (v1.7 → v1.8)

**Scope of revision.** R-FS-1 arc #4 — **B1-spec-1b** (full-spec build program; spine `.harness/beyond-mvp-capability-boundary-ledger.md`; design `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` D1.a; the coordinated IS amendment that CP spec v1.32 §25.13 forward-references). **The Route-Y branch-causality + terminal-disposition carrier** — `StateLedgerEntry` gains an optional `branch_metadata` D-derivative sidecar carrying fan-out branch causality (`parent_action_id`, `branch_index`) + the per-branch dispatch-boundary `terminal_status` the CP non-linear-topology `WorkflowDriver` composes. A **single additive amendment** at a NEW §5.4 sub-section under C-IS-05. NOT a recipe change, NOT a new top-level contract, NOT a six-field-shape change — an additive D-derivative extension at the layer §5.1 established (ADR-F2 §Consequences (c)).

**Amendment 1 — NEW §5.4 `branch_metadata` D-derivative sidecar.** `StateLedgerEntry` (and the `EntryPayload` write-carrier) gain an optional 8th field `branch_metadata: BranchMetadata | None = None` (alongside the §5.1 7th field). `BranchMetadata` is a three-field record: `parent_action_id: Identifier` (the spawning step's `action_id`), `branch_index: int ≥ 0` (0-based fan-out ordinal), and `terminal_status: {cancelled, completed, timed_out} | None` (the branch's dispatch-boundary terminal disposition; value-set + per-value semantics CP-producer-owned per CP spec v1.32 §25.15.2 obligation 4). `None` for every entry outside a fan-out branch (the `SINGLE_THREADED_LINEAR` path, bootstrap, non-branch steps — **every pre-v1.8 entry**). **Producer-supplied, not resolver-derived** (the CP `WorkflowDriver` is the producer per CP spec v1.32 §25.11 / §25.13 / §25.15) — so unlike §5.1 there is **no §5.2-analogue resolver contract**. `(parent_action_id, branch_index)` uniquely identifies a branch even under nested fan-out (`action_id` is globally unique per §5), so no `branch_path` is needed at this persisted causality carrier (`branch_path` is the CP-side §25.16 idempotency-key composition detail).

**Amendment 1 (cont.) — two carrier invariants.** (a) **Append-only** — `terminal_status` is set at the branch's *terminal entry* written fresh at branch-termination, NEVER by mutating an already-written entry (mutation would re-hash a persisted entry and break the §6.3 chain); a branch's earlier step entries carry `terminal_status = None`. (b) **Dispatch-boundary disposition, not step-outcome** — a branch whose in-flight step ran-and-errored is `completed` (its dispatch attempt completed; the step's own failure is recorded at that step's ordinary ledger entry per CP §25.15.2 obligation 3), which is why the value set carries **no `failed`**. *Which* entry carries the terminal disposition + *which* entries carry `branch_metadata` are producer/runtime write-cadence, deferred to B1-spec-2 (CP spec v1.32 §25.18).

**Hash level — forward-only, zero breaking change (the §5.1 pattern).** `branch_metadata` is payload content: when non-`None` it participates in the §6.1 canonicalization + §6.2 `response_hash` (tamper-evident per §6.5, like `procedural_tier_snapshot_ref`); when `None` it is **omitted** from the canonical payload (the established `entry_hash.py` `if … is not None` discipline). Every pre-v1.8 entry (all carry `branch_metadata = None`) therefore canonicalizes byte-identically to a v1.8 `None`-sidecar entry — ZERO breaking change for the existing chain; forward-only, no historical-entry migration. The §6 construction **discipline is unchanged**.

**Cross-spec reconciliation (descriptive) + a Class 3 CP-side item.** §5.4 documents the relationship between `terminal_status` and the three sibling CP disposition vocabularies (`SubAgentResultStatus` C-CP-14 §14.2 span-attribute; `CascadeDecisionAtFanoutClose` C-CP-15 §15.2 fanout-close aggregate; `RunStatus` C-CP-25 §25.2 run-level) — observably distinct token sets on distinct carriers, sharing only `completed` (consistent meaning), no token collision. CP spec v1.32 §25.13 / §25.15 commits the per-branch value set without a reciprocal cross-reference to these enums; that reciprocal CP-side note is flagged a **Class 3 informational** doc-coordination item (non-blocking; foldable into a future CP touch — e.g. B1-spec-2 / B1-plan), not a contract defect — the committed value set is coherent + buildable.

**Carrier-home + the IS 0-outbound constraint.** The `BranchMetadata` record + `terminal_status` type is a shared cross-axis type (CP produces, IS persists); its package home (`harness-core` vs `harness-is`) is a B1-impl-N decision (as §5.1 deferred resolver residence), with the **one hard constraint** that it is **NOT** homed in `harness-cp` — the IS axis has 0 outbound cross-axis edges (harness-is §1.1 / CXA §2.2), so IS cannot import from CP; CP consumes the entry shape from IS via the established CP→IS direction.

**Sections preserved verbatim at v1.8.** §Status block (rows appended only); §2 C-IS-01 + C-IS-02; §3; §4; **§5 C-IS-05 six-field shape + §5.1 `procedural_tier_snapshot_ref` sidecar + §5.2 resolver contract + §5.3 prompts versioned authoring store** (all byte-unchanged — the §5.2 recipe does NOT read `branch_metadata`); §6 C-IS-06 hash-chain (construction discipline unchanged; the canonical payload naturally covers the new optional sidecar per the §5.1 omit-when-`None` pattern); §7 (incl. §7.5 keying-tuple); §8; §9; §10 C-IS-10 seam exports (the §10.1 entry-shape export naturally travels the new optional field; no new export seam); §[traceability]; §[carry-forwards]; §[coherence pass]. **ONLY a NEW §5.4 sub-section is appended at the end of §5.** ZERO change to the F-layer six-field shape, hash-chain construction, read/write contracts, the §5.2 recipe, or seam exports. The carrier amendment is forward-only (no historical-entry migration; `None`-sidecar entries unchanged) and follows the CP spec v1.32 §25.13 Route-Y forward-coordination reference.

## Change-note (v1.6 → v1.7)

**Scope of revision.** R-PM-1 cascade PR #2 (`Project_Roadmap_v1.md` §5.16 / §5.17 R-CC-1 arc #2; design at `.harness/r-pm-1-prompts-management-design-v1.md` §4.3 / §6 row #2). **The prompts versioning/authoring layer** — `PromptManifest` gains a multi-version content store on the `PROMPTS` path-class (C-IS-01). A **single additive amendment** authored at a NEW §5.3 sub-section under C-IS-05. NOT a recipe change, NOT a new top-level contract (the prompt carrier already lives under §5.2's prompts-component prose; §5.3 extends that carrier's documentation).

**Honest framing — additive store, NOT a generalization-into.** The R-PM-1 design (§4.3) phrases PR #2 as "generalize PR #1's inline `content` into the store." What is actually *forward-only* is narrower and is what v1.7 commits: the store is **added alongside** the still-inline `active_prompt_version`. A true generalization — moving content *into* the store and making `active_prompt_version` a pure sha-reference — would force the runtime stage-5 injection reader (`active_prompt_version.content`) and the §5.2 hash reader (`active_prompt_version.version_sha`) to change; that is PR #3 blast radius (it composes with the CP selection layer that *populates* the active selection). v1.7 keeps both readers byte-unchanged. The transitional consequence is named explicitly: when a non-empty active selection is also present in a non-empty store, the active version's content is duplicated against its store entry — but the duplication is **byte-identical by construction** (content-addressing: same `version_sha` ⟹ same content, each independently satisfying the v1.6 derive-invariant), not an independent second authority that can drift. PR #3 collapses `active_prompt_version` to a reference and removes the duplication.

**Amendment 1 — NEW §5.3 `PromptManifest.versions` authoring store.** `PromptManifest` gains `versions: tuple[PromptVersion, ...] = ()` — the content-addressed authoring store for prompt versions residing operationally on the `PROMPTS` path-class (C-IS-01 §1, plain-text-file-in-git). Each entry is a `PromptVersion` carrying `content` + a content-addressed `version_sha = prompt_version_sha(content)` (the v1.6 per-version derive-invariant, now applied across a collection). The store mirrors the operator-supplied-carrier pattern (`RoutingManifest`/Skills — declarative config, not runtime filesystem-scanning; a filesystem-materialization stage remains the deferred forward arc the v1.5 §5.2 prose named). `from_contents(manifest_version, contents, active)` is the authoring builder.

**Amendment 1 (cont.) — internal-coherence invariants (illegal-states-unrepresentable, enforced at construction).** With a non-empty store: (a) every entry is an authored version (`version_sha != ""`; the empty-carrier sentinel is the no-active-prompt marker on `active_prompt_version`, never a stored version); (b) entries are content-addressed-unique (no two share a `version_sha` — duplicate content is one version); (c) a non-empty `active_prompt_version` is a member of the store (you cannot activate an unauthored version). An empty store (the default) short-circuits to the #496/PR-#1 behavior — `active_prompt_version` stands alone with no membership obligation (forward-compatible with #506 inline-only configs). These are internal-coherence invariants, not a consumer interface; the sha→content resolution the selection layer needs is deliberately NOT pre-built here (PR #3 defines the lookup it actually requires).

**§5.2 recipe SHAPE unchanged (additive store, not a recipe change).** The §5.2 content-hash recipe is byte-identical at v1.7: still 3-component, still reads `active_prompt_version.version_sha`. The `versions` store does not enter the recipe (it has no §5.2 consumer); it is the authoring substrate the PR #3 CP selection layer will index into. There is therefore NO hash-consumer cascade.

**Sections preserved verbatim at v1.7.** §Status block (rows appended only); §2 C-IS-01 (the PROMPTS path-class is *referenced* by §5.3, not modified) + C-IS-02; §3; §4; **§5 C-IS-05 six-field shape + §5.1 `procedural_tier_snapshot_ref` sidecar + §5.2 resolver contract** (the §5.2 recipe + its `active_prompt_version.version_sha` read are byte-unchanged); §6 C-IS-06 hash-chain; §7; §8; §9; §10 C-IS-10 seam exports; §[traceability]; §[carry-forwards]; §[coherence pass]. **ONLY a NEW §5.3 sub-section is appended at the end of §5** (the versioned authoring store). ZERO change to the F-layer six-field shape, hash-chain construction, read/write contracts, seam exports, or the §5.2 recipe. The carrier amendment is forward-only (no historical-entry migration; empty-store configs unchanged) and cross-axis-neutral.

## Change-note (v1.5 → v1.6)

**Scope of revision.** R-PM-1 cascade PR #1 (`Project_Roadmap_v1.md` §5.16 / §5.17 R-CC-1 arc #2; design at `.harness/r-pm-1-prompts-management-design-v1.md` §4.1/§4.3). **§5.2 provenance-tightening** — the IS-carrier side of a bundled-absorption arc whose runtime-injection side is co-published at runtime spec v1.44 §14.5. The runtime cascade injects the active prompt's *content* as a per-provider system prompt; this amendment makes `active_prompt_version.version_sha` content-derived so injected content cannot drift from the procedural-tier hash. A **runtime-binding-extension / provenance-tightening arc** per the §5.2 framing — NOT a recipe change and NOT a new contract.

**Amendment 1 — `PromptVersion.content` inline carrier (minimal).** `PromptVersion` gains `content: str = ""` (optional, empty-defaultable). This is the self-contained PR #1 content source so a single operator-supplied active prompt injects + proves e2e within PR #1; PR #2 (versioning/authoring) generalizes the inline field to the multi-version `PROMPTS`-path-class store (C-IS-01) + content-addressing. The field is a forward amendment to the just-cleared (v1.5) frozen `PromptVersion` shape — empty-default keeps existing empty-carrier configs (`PromptVersion(version_sha="")`) valid; configs that newly supply content rebase the procedural-tier hash forward (exactly as v1.5's recipe-widening established).

**Amendment 2 — the `content ↔ version_sha` derive-invariant.** `version_sha == prompt_version_sha(content)` is enforced at construction (detect-then-refuse — a mismatched sha raises). `prompt_version_sha(content)` is the single source of the sha: `""` (the empty-carrier sentinel) for empty content, else the lowercase hex SHA-256 digest of the UTF-8 content bytes. This closes the silent provenance/replay-integrity gap the injection cascade would otherwise open: without it, injected content could change while the §5.2 procedural-tier hash reports "unchanged" (because the hash reads `version_sha`, not content). The sha is no longer an independent operator-set field: supplying only `content` — including declaratively via TOML/JSON `RuntimeConfig.prompt_manifest`, where the operator constructs `PromptVersion(content="...")` without a precomputed digest — derives `version_sha`; an explicitly-supplied non-empty `version_sha` that disagrees with the content is refused. `PromptVersion.from_content(content)` is the explicit authoring helper.

**§5.2 recipe SHAPE unchanged (provenance-tightening, not recipe change).** The §5.2 content-hash recipe is byte-identical at v1.6: still 3-component, still reads `active_prompt_version.version_sha`. ONLY `version_sha`'s provenance tightens (now content-derived). There is therefore NO hash-consumer cascade — every §5.2 consumer reads the same `version_sha` field with the same type/semantic; the tightening is internal to how that value is produced at the carrier.

**Sections preserved verbatim at v1.6.** §Status block (rows appended only); §2 C-IS-01 + C-IS-02; §3; §4; **§5 C-IS-05 six-field shape + §5.1 `procedural_tier_snapshot_ref` sidecar contract** (unchanged — `version_sha` is read by §5.2, and §5.2's recipe shape is unchanged); §6 C-IS-06 hash-chain; §7; §8; §9; §10 C-IS-10 seam exports; §[traceability]; §[carry-forwards]; §[coherence pass]. **ONLY §5.2's prompts-component paragraph gains a provenance-tightening sub-paragraph** (the inline `content` carrier + the derive-invariant). ZERO change to the F-layer six-field shape, hash-chain construction, read/write contracts, or seam exports. The carrier amendment is forward-only (no historical-entry migration) and cross-axis-neutral (the procedural-tier snapshot ref was already a §5.1 sidecar, not a persisted cross-axis join key).

## Change-note (v1.4 → v1.5)

**Scope of revision.** Post-MVP closure R-CL-P4 (`Project_Roadmap_v1.md` §5.15) **prompts-management binding** — the last open R-CL-P4 blocker. Closes the §5.2 v1.3 "Prompts component deferred" footer by authoring the third procedural-tier hash component (`active_prompt_version`), per operator ratification of fork `.harness/class_1_fork_prompts_management_surface_active_prompt_version.md` (DP-1..DP-4, 2026-06-11). This is the **recipe side** of a bundled-absorption arc; the runtime-context binding side is co-published at runtime spec v1.42 §4 C-RT-04. A **runtime-binding-extension arc** per the §5.2 framing — NOT a spec-extension-from-scratch and NOT a new contract.

**Amendment 1 — §5.2 deferral→bound flip (3-component recipe).** The §5.2 "Prompts component deferred at v1.3" paragraph is rewritten to bind the third component. The content-hash recipe widens from 2-component `{active_skills_versions, routing_manifest_sha}` to 3-component `{active_prompt_version, active_skills_versions, routing_manifest_sha}` (alphabetically ordered; `sort_keys=True`). `active_prompt_version` is read as `HarnessContext.prompt_manifest.active_prompt_version.version_sha`. The three v1.3-named preconditions are recorded as satisfied (carrier types at `harness_is.prompt_manifest`; runtime field at runtime spec v1.42 §4 C-RT-04; resolver read-access at write-time). Hash rebasing is expected + forward-only per the v1.3 §5.2 prose (already anticipated: "Hash rebasing at v1.x absorption is expected … operators MUST treat snapshot-ref equality as scoped within a single recipe-version generation").

**Amendment 2 — `PromptManifest`/`PromptVersion` carrier types (IS-axis home).** The carriers are authored at `harness_is.prompt_manifest` (`PromptManifest` = `manifest_version: int` + `active_prompt_version: PromptVersion`; `PromptVersion` = `version_sha: str`; both frozen + `extra="forbid"`), mirroring the `RoutingManifest` precedent (fork DP-1). Empty-defaultable at the runtime carrier (`version_sha=""` → no active prompt) so operators carry zero config burden — the `routing_manifest` `default_factory` precedent.

**Sections preserved verbatim at v1.5.** §Status block (rows appended only); §2 C-IS-01 + C-IS-02; §3; §4; **§5 C-IS-05 six-field shape + §5.1 `procedural_tier_snapshot_ref` sidecar contract** (the recipe-internal component count is a §5.2 resolver detail — the §5.1 sidecar field type/semantic/constraint are unchanged); §6 C-IS-06 hash-chain; §7 (incl. the v1.4 §7.5 reading-(iii) ratification); §8; §9; §10 C-IS-10 seam exports; §[traceability]; §[carry-forwards]; §[coherence pass]. **ONLY §5.2's "Prompts component deferred" paragraph is amended** (deferral → bound). ZERO change to the F-layer six-field shape, hash-chain construction, read/write contracts, or seam exports. The recipe widening is forward-only (no historical-entry migration) and cross-axis-neutral (the procedural-tier snapshot ref was already a §5.1 sidecar, not a persisted cross-axis join key — `idempotency_key` is, and it is unchanged).

## Change-note (v1.3 → v1.4)

**Scope of revision.** Post-MVP closure R-CL-P4 (`Project_Roadmap_v1.md` §5.15) keying-tuple ↔ entry-shape reconciliation. Resolves the §7.4 "Deferred to implementation discretion" deferral of the relationship between the §7.1 idempotent-write keying tuple `(thread_id, step_id, idempotency_key)` and the C-IS-05 six-field entry shape, per operator ratification of fork `.harness/class_1_fork_keying_tuple_entry_shape_d_adr.md` (**reading (iii)**; operator decision 2026-06-10, re-confirmed 2026-06-11). One new subsection + one inline deferral→resolution flip + one stale-cite refresh; **no contract/behavior change** (the landed implementation already implements reading (iii); a companion `harness-is/src/harness_is/state_ledger_write.py` module docstring is reconciled from its "§7.4 deferral / left to implementer" framing to the ratified reading (iii) in the same PR — doc-only, no behavior change).

**Amendment 1 — NEW §7.5 reading-(iii) ratification.** Authoring §7.5 stating reading (iii): `thread_id`/`step_id` are write-arguments carried on the write-time `WriteKey` structure, not persisted as distinct `StateLedgerEntry` fields; `idempotency_key` is the sole persisted entry-level dedup discriminator. Code-confirmed at HEAD (`harness-is/src/harness_is/state_ledger_write.py` `WriteKey` carries `thread_id`/`step_id`; `harness-is/src/harness_is/state_ledger_entry_schema.py` `StateLedgerEntry` persists the six fields + the v1.3 `procedural_tier_snapshot_ref` sidecar — none of which is `thread_id`/`step_id`). The C-IS-05 §5 six-field shape is inviolate (IS-AL-3); reading (iii) is the base contract, the §5 field-shape-extensibility (iv) per-workload-class extension remains admissible and composes with (iii).

**Amendment 2 — §7.4 deferral→resolution flip + F2-12 cite refresh.** The §7.4 "Deferred to implementation discretion" paragraph's keying-tuple clause is flipped from deferred (to a downstream D-ADR) to resolved-at-§7.5. The stale F2-12 forward-cite ("F2-12 active engagement … the open downstream resolution path") is refreshed: F2-12 is CLOSED (`F2-12_Closure_Declaration.md`, 2026-05-14) on an **adjacent** scope (D1/D6 replay-trace-emission + cost-dedup, where `idempotency_key` is a trace-ingestion cost-dedup join key), NOT this write-keying-tuple ↔ entry-shape reconciliation, per `[[stale-carry-text-disposition]]`. The §7.4 multi-seam T-perm-2 engagement table + the §[carry-forwards] [CF-1] F2-12 line are preserved verbatim as historical record.

**Sections preserved verbatim at v1.4.** §Status block (rows appended only); §2 C-IS-01; §2 C-IS-02 (five-tier table + substrate-residence + survival + cross-tier traceability + the v1.3 line-170 patch); §3 C-IS-03; §4 C-IS-04; §5 C-IS-05 six-field shape + the v1.3 §5.1 sidecar + §5.2 resolver; §6 C-IS-06 hash-chain; §7 C-IS-07 §7.1 write contract + §7.2 read contract + §7.3 composition format + §7.4 multi-seam T-perm-2 engagement table (only the keying-tuple deferral clause within §7.4's "Deferred to implementation discretion" paragraph is flipped to a §7.5 pointer); §8 C-IS-08; §9 C-IS-09; §10 C-IS-10 seam exports; §[traceability] matrix; §[carry-forwards] (the [CF-1] F2-12 line preserved as historical record); §[coherence pass]. ZERO change to the F-layer six-field shape, hash-chain construction, read/write contracts, or seam exports. No cross-axis cascade (the reconciliation is IS-internal; the keying tuple was never a persisted cross-axis join key — `idempotency_key` is, and it is unchanged).

## Change-note (v1.2 → v1.3)

**Scope of revision.** Phase 7 H_T-IS-2 substitution-retirement apply-pass per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` operator-ratified 2026-05-30 Q-set (Q1=γ-family + Q1.1=γ + Q2=narrow + Q3=bundled + Q4=inline) + apply-pass session Q-α=(α-1) content-hash + Q-β=(β-3) direct-compute D1-ratified 2026-05-30. Three substantive amendments + one canonical-reading patch authored at delta-only-spec-file convention.

**Amendment 1 — NEW §5.1 D-derivative sidecar field.** Authoring `procedural_tier_snapshot_ref: Identifier | None` as the documented D-derivative extension of the §5 F-layer six-field shape, per ADR-F2 §Consequences (c) extension authorization. Sidecar carries the content-hash digest identifying which procedural-tier snapshot (active Skills version set + active prompt version + routing manifest SHA) was in scope at the entry's write-time. `None` permitted at entries written outside an active workflow context (bootstrap-stage entries; operator-explicit administrative entries). The F-layer six-field shape PRESERVED VERBATIM at §5 lines 262-269; sidecar is additive at the D-derivative extension layer authorized by §5 "Field-shape extensibility commitment."

**Amendment 2 — NEW §5.2 resolver contract.** Authoring `resolve_procedural_tier_snapshot(harness_context: HarnessContext) -> Identifier` resolver signature + content-hash recipe + direct-compute storage discipline. **Recipe at v1.3 (2-component scope):** `sha256(canonical_join(active_skills_versions ‖ routing_manifest_sha))` over canonical-JSON byte representation of the two presently-bound procedural-tier components ordered alphabetically by component name; lowercase hex serialization. **Prompts component deferred at v1.3 per apply-time empirical orientation** — `active_prompt_version` has no runtime binding at HEAD (`HarnessContext` schema has no `active_prompt_version` field; no `PromptManifest` carrier exists at any harness-* package); per X-AL-3 the spec MUST NOT commit a content-hash recipe to a phantom referent. Prompts will join the recipe at a future v1.x amendment when the runtime spec authors `active_prompt_version` AND the prompts-management surface lands at production (the `prompts/` path-class taxonomy already exists at `atomic_deploy_event.py:159` per the PROMPTS classification; the operational referent exists at filesystem layer, but the runtime-side binding to query active version is not yet authored). Direct-compute storage: no separate snapshot-keyed registry persists at H_T; resolver re-computes from current `HarnessContext` state at every call (procedural artifacts themselves persist at filesystem+git per §C-IS-02 line 163; the snapshot identity is derived, not stored). Engine-layer composers without `HarnessContext` access at firing time receive the resolver as a `Callable[[], Identifier]` kw-only parameter at the composer function signature, bound at runtime composition time per CP spec v1.25 §16.5.7 + §16.5.8 `ledger_writer` kw-only-callable-bound-at-runtime-wiring precedent.

**Amendment 3 — §C-IS-02 line 170 canonical-reading patch.** Inline rewrite reconciling the MAY/MUST composition shape per Q4=inline ratification. Line 170 previously declared cross-tier traceability flows via `action_id` field encoding; v1.3 declares traceability MUST flow via the §5.1 sidecar field and `action_id` MAY continue to encode action class / sub-class metadata per the §5 field-spec footer (lines 264 + 282). Closes the architect rec §7 (b) MAY/MUST composition observation at first pass per `[[stale-carry-text-disposition]]` discipline.

**Workspace pattern + cardinality.** 54th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture — pre-substantive advisor pass at apply-pass session caught replay-semantics ambiguity at §C-IS-05 + ADR-F2; empirical grep across `replay` mentions discriminated "engine-replay" (CP/OD layer using `idempotency_key` for dedup) from "procedural-tier state reconstruction"; procedural artifacts persist at filesystem+git per §C-IS-02 line 163, so all three Q-α sub-shapes remained live but Q-α × Q-β coupling collapsed to 4 legal pairs (5 illegal/contradictory/redundant pairs foreclosed: (α-1)+(β-1) moot, (α-2)+(β-1) illegal per cross-run survival contract, (α-2)+(β-3) contradictory, (α-3)+(β-1) and (α-3)+(β-2) redundant); AUQ authored over 4 legal pairs at single D1 rather than sequential D1+D2 over 6 sub-options with operator-trap risk. NEW species candidate `[[procedural-tier-mutability-as-decisive-discriminator]]` catalogued at architect rec §7 (e) preserved at v1.3 (awaits second instance for workflow doc §7.4.7.2 sub-species addition).

**Per-axis cascade discipline.** ZERO cross-axis cascade at this arc per Q2=narrow ratification. ~13 producer-site lifts across `harness-as` / `harness-cp` / `harness-runtime` defer to follow-on per-axis arcs per `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` precedent. H_T-IS-2 substitution-retirement transit STILL-BOUNDED → PARTIAL on v1.3 apply-pass merge (substrate landed at IS-axis); PARTIAL → RETIRED gated on full producer-site lift completion per X-AL-2 second conjunct. Cluster-boundary call sites at HEAD continue to work without modification (sidecar field is `Optional`, default `None`).

**Sections preserved verbatim at v1.3.** §Front-matter; §1 C-IS-01; §2 C-IS-02 lines 156-168 (five-tier table + substrate-residence + survival-semantics paragraphs); §2 C-IS-02 "Deferred to implementation discretion" footer; §3 C-IS-03; §4 C-IS-04; §5 C-IS-05 lines 250-282 (the F-layer six-field shape + extensibility commitment + cross-axis seam compositions + deferred-to-implementation-discretion footer all PRESERVED VERBATIM; §5.1 + §5.2 are additive sub-sections introduced at v1.3); §6 C-IS-06; §7 C-IS-07; §8 C-IS-08; §9 C-IS-09; §10 C-IS-10; §[carry-forwards]; §[traceability]; §[coherence pass] (preserved verbatim as v1 + v1.1 + v1.2 historical record per `P5-CK_Iteration_2_Final_Revision_Pass_Session_Prompt.md` §5.2 §[coherence pass] preservation discipline; v1.3 is a Phase 7 substantive amendment arc, not a P5-CK clearance arc; coherence-audit re-run is not required for Phase 7 in-flight substrate amendments per workspace `CLAUDE.md` §11.4 mixed-posture default).

**Status posture.** `Status: Proposed (v1.3 in-flight Phase 7 substantive amendment per `.harness/architect_recommendation_h_t_is_2_artifact_tier_registry_wiring.md` apply-pass arc 2026-05-30)`. Clearance marker filed at `.harness/clearance/Spec_Information_Substrate-v1_3-cleared-2026-05-30.md` per workspace `CLAUDE.md` §4.5.

**Changes inline.** Status block (Status row revised; third pair of Revision row + Revision date row appended for v1.2 → v1.3). This Change-note section (new; appended between Status block and previous Change-note v1.1 → v1.2). §2 C-IS-02 "Tier composition contract" line 170 (rewrite for MAY/MUST composition reconciliation). §5 C-IS-05 NEW §5.1 + §5.2 sub-sections (appended at end of §5 before the `---` separator). No other content modified.

---

## Change-note (v1.1 → v1.2)

**Scope of revision.** Single-finding final revision pass clearing `Adversarial_Review_5_iter2.md` F-iter2-03 / Pattern P2-PHASE-5 (Class 1 mechanical — body-citation drift `ADR-D3 v1.1` → `v1.2` at C-IS-10 §10.4 Action Surface row, line 551, two sites in one table row: cell-name parenthetical + citation in cell prose). Cited content materially unchanged at ADR-D3 v1.2 per `P5-CK_Iteration_2_Close_Handoff.md` §3.5; token-level alignment only under use-latest-version discipline. Single mechanical bump applied at this revision pass per `P5-CK_Iteration_2_Final_Revision_Pass_Session_Prompt.md` §5.1 Stage 2.

**Sections preserved verbatim at v1.2.** §Front-matter (Axis declaration; Axis-grounding note; Persona summary; PRD requirement scope; ADR commitment scope; cross-axis citation table; Deferred to implementation discretion); §2 C-IS-01 (workflow root layer schema); §2 C-IS-02 (five-tier table; substrate residence; survival semantics; cross-tier traceability); §3 C-IS-03 (combined git tier role decomposition); §4 C-IS-04 (workflow-class-tunable shadow-Git checkpointing); §5 C-IS-05 (state-ledger entry-shape signature); §6 C-IS-06 (hash-chain integrity); §7 C-IS-07 (idempotent-write keying tuple, read contract, composition format, multi-seam T-perm-2 engagement, Deferred-to-implementation-discretion subsection); §8 C-IS-08 (shadow-Git checkpoint contract); §9 C-IS-09 (per-sub-agent worktree opt-in declaration, worktree-termination contract, concurrent-read isolation invariant, multi-writer scaling boundary, all Deferred-to-implementation-discretion subsections); §10 C-IS-10 §10.1, §10.2, §10.3, §10.5, §10.6, §10.7, §10.8 (all substrate seam exports except §10.4 Action Surface row at line 551); §[traceability] matrix; §[carry-forwards]; §[coherence pass] (preserved verbatim as v1 + v1.1 historical record).

**Changes inline.** Status block (Status row revised; second pair of Revision row + Revision date row appended for v1.1 → v1.2). This Change-note section (new; appended between Status block and previous Change-note v1 → v1.1). §10 C-IS-10 §10.4 Action Surface row at line 551 (two body-citation sites in one table row: `(D3 v1.1 Skills loading discipline)` → `(D3 v1.2 Skills loading discipline)` cell-name parenthetical + `per ADR-D3 v1.1` → `per ADR-D3 v1.2` citation in cell prose). Two amendment sites total; no other content modified.

**§[coherence pass] preservation discipline.** §[coherence pass] section at v1.2 is preserved verbatim as the v1 + v1.1 point-in-time audit historical record. Audit rows referencing v1 substrate state and v1.1 D-ADR-citation state are accurate historical record of those audit passes; v1.2 final-revision-pass mechanical body-citation bump does not re-run the audit. Per `P5-CK_Iteration_2_Final_Revision_Pass_Session_Prompt.md` §5.2 §[coherence pass] preservation discipline.

---

## Change-note (v1 → v1.1)

**Scope of revision.** Three-finding revision pass clearing `Adversarial_Review_5.md` F-IS-01 (Class 2 — C-IS-02 tier-residence internal contradiction at episodic tier), F-IS-02 (Class 2 — C-IS-07 keying tuple not reconciled with C-IS-05 entry-shape signature), and F-IS-03 (Class 1 — C-IS-09 §9.2 "reclamation" operational-semantic ambiguity). All three findings resolvable at this single axis-spec revision pass per `P5-CK_Iteration_1_Close_Handoff.md` §3.2 + §3.3.

**F-IS-01 Path A resolution per operator sub-decision.** C-IS-02 §"Tier composition contract" / "Substrate residence" statement at line 132 rewritten to align with the five-tier table at lines 122–128. The table commits `episodic` tier as "Filesystem (run-bounded paths)" with no git surface; the revised substrate-residence statement reads "all durable-survival tiers (semantic / procedural / durable) reside on filesystem AND git per ADR-F2 §Decision combined-tier role; working and episodic tiers reside on filesystem only (no git)". The table is the canonical reading; the statement aligns to the table.

**F-IS-02 Path B resolution per operator sub-decision.** C-IS-07 §7.1 idempotent-write keying tuple `(thread_id, step_id, idempotency_key)` retained verbatim (canonical per ADR-F2 §Consequences (c) Stripe-style convention citation). The relationship between the keying tuple and the C-IS-05 six-field entry shape is explicitly deferred to a downstream D-ADR on ledger schema via a new entry at C-IS-07 §7.4 "Deferred to implementation discretion" subsection. The deferral cites ADR-F2 §Consequences (c) "defers the relationship reconciliation to the D-ADR on ledger schema fields" as the upstream-substrate authority. F2-12 active engagement on ledger-schema D-ADR per ADD §6.3.1 + PRD §[carry-forwards] [CF-1] (parallel `council-orchestrator` C7+C9 session at operator discretion) is the open downstream resolution path; this revision does not pre-empt that work.

**F-IS-03 Path C resolution per operator sub-decision.** C-IS-09 §9.2 worktree-termination contract row at line 456 receives inline definition of "reclamation" operational semantic: reclamation = `git worktree remove` invocation + directory contents removal, triggered at operator-policy-controlled lifecycle-marker boundary. The mechanical operation and the policy trigger are both specified; specific lifecycle-marker policy is operator territory at workflow-binding time and remains at the existing C-IS-09 §9.4 "Deferred to implementation discretion" subsection ("specific worktree reclamation cleanup policy").

**Sections preserved verbatim.** §1 Axis declaration / Axis-grounding note / Persona summary; §2 C-IS-01 (workflow root layer schema); §2 C-IS-02 five-tier table at lines 122–128 (the canonical reading; substrate-residence statement aligns to the table, not vice-versa); §2 C-IS-02 Survival semantics + Cross-tier traceability paragraphs; §3 C-IS-03 (combined git tier role decomposition); §4 C-IS-04 (workflow-class-tunable shadow-Git checkpointing); §5 C-IS-05 (state-ledger entry-shape signature — the six-field tuple); §6 C-IS-06 (hash-chain integrity); §7 C-IS-07 §7.1 keying tuple statement (canonical per ADR-F2 §Consequences (c)); §7 C-IS-07 §7.2 read contract; §7 C-IS-07 §7.3 composition format; §7 C-IS-07 §7.4 multi-seam T-perm-2 engagement; §8 C-IS-08 (shadow-Git checkpoint contract); §9 C-IS-09 §9.1 + §9.3 + §9.4 (per-sub-agent worktree opt-in declaration, concurrent-read isolation invariant, multi-writer scaling boundary, all Deferred-to-implementation-discretion subsections); §10 C-IS-10 (substrate seam exports surface); §[traceability] matrix; §[carry-forwards]; §[coherence pass] (preserved verbatim as v1 point-in-time historical audit per PRD v1.0 → v1.0.1 precedent).

**Status posture.** `Status: Proposed (v1.1 pending P5-CK iteration 2 clearance per Project_Workflow_v1_2.md §3.1)`. v1.1 enters P5-CK iteration 2 as input artifact alongside ADR-D3 v1.2, PRD v1.0.1, and the three other Phase 5 spec revisions per handoff §6.1 entry-gate checklist.

**Changes inline.** Status block (Status row revised; Revision row + Revision date row appended). This Change-note section (new). §2 C-IS-02 substrate-residence statement at line 132 (rewrite). §7 C-IS-07 §7.4 "Deferred to implementation discretion" subsection at line 373 (append new entry covering keying-tuple ↔ entry-shape deferral). §9 C-IS-09 §9.2 worktree-termination contract row at line 456 (inline reclamation definition). No other content modified.

**§[coherence pass] preservation discipline.** §[coherence pass] section is v1 point-in-time audit; v1.1 mechanical revision does not re-run the audit. Audit rows referencing v1 substrate state are accurate historical record. v1.1 → v1.2 (if needed at iteration 2 entry or post-iter-2) is the proper moment for fresh coherence pass.

---

## Front-matter

### Axis declaration

Per OD-5-2.A spec-writer judgment with handoff §3.1 recommendation followed: **Information Substrate** is the session-1 axis. Rationale:

- **Smallest axis surface.** One foundational ADR (F2 v1.2); four PRD requirements (R-IS-01 through R-IS-04). No D-ADRs in axis per ADD §3.2 OD applied.
- **Substrate seam priority.** The F2 state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` is the harness-canonical join key against which every downstream axis composes — engine event history (Control Plane via D1), audit-ledger cryptographic shape (Operational Discipline via D5), sandbox-violation events (Action Surface via D2), span emission (Operational Discipline via D6) all join on `idempotency_key` per ADD §2.2 Synthesis. Authoring the substrate seam first locks the composition surface for sessions 2–4.
- **Session 1 warmup.** Exercising the inversion-discipline analog (`Phase_5_Session_1_Session_Prompt.md` §1.2 + `Phase_5_Entry_Handoff.md` §6.3) at the smallest axis surface before scaling to denser axes (Control Plane at 5 ADRs / 12 PRD requirements).

### Axis-grounding note

The Information Substrate axis hosts **one foundational ADR** (F2 v1.2 — filesystem + git canonical state substrate with files-as-artifacts and combined git tier) per ADD §2.2. §3 (Information Substrate D-ADRs) is empty per ADD §3.2 OD applied. Cross-axis composition with the control plane (F3 ↔ F2 substrate seam per ADD §2.3), action surface (F5 ↔ F2 audit composition per ADD §2.5), and operational discipline (D6 ↔ F2 span schema composition per ADD §3.4.1) is captured at C-IS-10 (substrate seam exports surface) for downstream-axis specs to consume by citation.

### PRD requirement scope

| PRD requirement | Observer role | Primary ADR section citation |
|---|---|---|
| R-IS-01 — Files-as-artifacts at canonical filesystem paths | Production-time operator + Downstream maintainer | ADR-F2 v1.2 §Decision; ADD §2.2 Synthesis |
| R-IS-02 — Git as combined-tier state record | Downstream maintainer | ADR-F2 v1.2 §Decision; ADD §2.2 Synthesis |
| R-IS-03 — State-ledger entry shape with hash-chain integrity | Downstream maintainer | ADR-F2 v1.2 §Decision + §Rationale (a.1); ADD §2.2 Synthesis |
| R-IS-04 — Workload-class-opt-in shadow-Git checkpoint and worktree isolation | Production-time operator + Downstream maintainer | ADR-F2 v1.2 §Decision; ADD §2.2 Synthesis |

### ADR scope

| ADR | Version | Role in axis |
|---|---|---|
| F2 | v1.2 | Sole foundational ADR; commits filesystem + git canonical state substrate; commits artifact-tier layering, combined git tier role, state-ledger entry shape, hash-chain integrity construction discipline, workload-class-opt-in shadow-Git + worktree-isolation |

### Persona-linkage substrate

| Persona anchor | Inheriting requirement(s) |
|---|---|
| §3.1.1 (software engineering — F2 leverage maximal) | R-IS-04 |
| §3.1.3 (pipeline automation — durability tier mandatory) | R-IS-04 |
| §5.1 (state lives on local filesystem + remote git) | R-IS-01, R-IS-02 |
| §7 (workflow-definition surface — both markdown-spec-driven and code-driven authoring) | R-IS-01 |
| §8.1 (software-engineering action surface — code execution + filesystem + git as primary) | R-IS-04 |
| §10.1 (filesystem + git as canonical state shape — operator-confirmed locked principle) | R-IS-01 |
| §10.2 (cost-attribution-per-span composes against the JSONL event ledger as per-event audit surface) | R-IS-02, R-IS-03 |
| §10.4 (compliance-readiness — hash-chained audit ledger foundational primitive) | R-IS-02, R-IS-03 |

### Scope and out-of-scope

| In scope | Out of scope |
|---|---|
| Specification-grade contract precision for R-IS-01 through R-IS-04 (signatures, schemas, formulas, enums, surface contracts) | New architectural commitments (Phase 3 territory; back-flow to ADR revision if surfaced) |
| Citation-by-section to PRD requirements + ADR commitments + ADD synthesis paragraphs | ADR revision; ADD revision; PRD revision |
| Persona-linkage trace preservation from PRD requirements | Cross-axis spec coherence beyond substrate seam exports (deferred to session 5 composition document per handoff §3.1) |
| Substrate seam exports surface (C-IS-10) for downstream-axis specs to consume by citation | Action-surface, control-plane, operational-discipline contracts (sessions 2–4) |
| §[carry-forwards] inheritance from PRD §[carry-forwards] | F2-12 closure (parallel `council-orchestrator` C7+C9 session territory; carry-forward only here) |
| Deferred-to-implementation discretion notation per Workflow §2.5.1 exit criteria language | Implementation-grade choices beyond specification surface (specific library bindings beyond ADR-declared, specific file paths beyond canonical-path declaration, specific provider candidates) |

---

## §1 C-IS-01 — Canonical filesystem path contract

**Contract surface.** Path-class enumeration with stability invariants and visibility surface.

**PRD requirement(s) satisfied.** R-IS-01 (files-as-artifacts at canonical filesystem paths).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (filesystem + git canonical state substrate; Skills, prompts, routing manifest, state-ledger all authored as files); ADD §2.2 Synthesis.

**Persona linkage.** Persona §5.1 (state lives on local filesystem + remote git); §7 (workflow-definition surface — both markdown-spec-driven and code-driven authoring); §10.1 (filesystem + git as canonical state shape — operator-confirmed locked principle).

**Specification content.**

Four canonical artifact classes reside on the filesystem; each class declares its path-residence contract:

| Class | Path-residence contract | Path-stability invariant | Visibility surface |
|---|---|---|---|
| Skills | SKILL.md-as-directory (folder-with-SKILL.md), one folder per skill; folder name is the skill identifier; SKILL.md frontmatter carries `name` + `description` (required) and `allowed-tools` + `disable-model-invocation` + `license` + `dependencies` (optional) per agentskills.io open standard ratified 18 Dec 2025 [HIGH — ADR-F2 v1.2 §Rationale (a)] | Folder identifier stable across runs of the same workflow; SKILL.md frontmatter schema stable across runs | Filesystem-readable to production-time operator during a run; filesystem-readable to downstream maintainer after termination |
| Prompts | Plain-text-file-in-git; one file per prompt artifact; prompts loaded as stable static-prefix content per Cluster 2 V2 §1.2 prompt-cache hierarchy [HIGH — ADR-F2 v1.2 §Rationale (b)(ii)] | File path stable across runs; file content cache-prefix-integrity-preserving | Filesystem-readable to production-time operator during a run; filesystem-readable to downstream maintainer after termination |
| Routing manifest | Single file in git per ADR-F1 v1.2 Consequences §(a) "manifest-layer model assignment as auditable default at every call site"; manifest declares per-agent-role + per-workflow-class + per-step model assignments. **Path resolution: `PathClass.ROUTING_MANIFEST` resolves to the containing directory; the manifest file lives inside as `routing.manifest.json`** (v1.3 amendment 2026-05-20 per `[[fork-state-ledger-path-dir-vs-file]]` Path A — disambiguates from prior file-vs-dir reading ambiguity) | Directory path stable across runs (workflow-class-bound); manifest filename stable; manifest content immutable within a run | Filesystem-readable to production-time operator during a run; filesystem-readable to downstream maintainer after termination |
| State-ledger | Two-mode composite per C-IS-03 §3 (git commit stream as one mode; JSONL event ledger as second mode); commit stream at workflow-bound git repository. **Path resolution: `PathClass.STATE_LEDGER` resolves to the containing directory; the JSONL event-ledger file lives inside as `state.jsonl`** (v1.3 amendment 2026-05-20 per `[[fork-state-ledger-path-dir-vs-file]]` Path A) | Directory path stable across runs of the same workflow; JSONL filename stable; git repository identity stable across runs of the same workflow | Filesystem-readable to production-time operator during a run; filesystem-readable to downstream maintainer after termination |

**Stability invariants.**

- A path identifier is **workflow-canonical** if it is stable across all runs of the same workflow class.
- A path identifier MAY vary across workflow classes; the contract does not commit to project-global canonical paths.
- A path identifier MAY vary across deployment surfaces per ADD §3 OD-2.A deployment-surface flex; canonical-path declaration commits only that *some* stable path exists per (workflow class, deployment surface) cell.

**Visibility surface contract.** All four artifact classes are filesystem-readable to (a) the production-time operator during a run via direct filesystem access on the host, and (b) the downstream maintainer after run termination via the durable filesystem persisting beyond run lifetime. No artifact class is held in-memory-only.

**Deferred to implementation discretion.** Specific canonical path strings per workflow class per deployment-surface cell (e.g., `.harness/skills/`, `harness/prompts/`, `routing.manifest.json` literal paths) are implementation-grade choices not committed by ADR substrate; binding occurs at implementation (Phase 6).

---

## §2 C-IS-02 — Artifact-tier layering schema

**Contract surface.** Five-tier model with tier-to-artifact-class mapping and tier composition contract.

**PRD requirement(s) satisfied.** R-IS-01 (files-as-artifacts at canonical filesystem paths; artifact-tier layering as the layering contract).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (artifact-tier layering composing working / episodic / semantic / procedural / durable); ADR-F2 v1.2 §Rationale (a) (P-IS-1 D-on-schema variation: ICM five-layer prescriptive, 12-Factor minimum-viable, Anthropic progress-file pattern as the loosest viable shape); ADD §2.2 Synthesis.

**Persona linkage.** Persona §5.1 (state lives on local filesystem + remote git); §10.1 (filesystem + git as canonical state shape — operator-confirmed locked principle).

**Specification content.**

The five-tier artifact layering schema commits the following layer enumeration:

| Tier | Semantic role | Substrate residence | Survives across |
|---|---|---|---|
| `working` | Per-run scratch state | Filesystem (run-bounded temporary paths) | A single inference call within a run |
| `episodic` | Per-run history; in-flight conversational state | Filesystem (run-bounded paths) | Multiple inference calls within a run; restart only via durable-execution engine replay |
| `semantic` | Cross-run knowledge artifacts; learned content | Filesystem + git (semantic-tier paths) | Run termination; carries forward into future runs |
| `procedural` | Workflow-class procedural artifacts (Skills, prompts, routing manifest) | Filesystem + git (procedural-tier paths) | Run termination + workflow versioning; carries forward across workflow versions |
| `durable` | Append-only state-ledger + JSONL event ledger + audit ledger | Filesystem + git (state-ledger paths per C-IS-05) | Run termination + restart + crash recovery; chain-integrity-verified per C-IS-06 |

**Tier composition contract.**

- **Substrate residence.** All durable-survival tiers (`semantic`, `procedural`, `durable`) reside on filesystem AND git per ADR-F2 §Decision combined-tier role; `working` and `episodic` tiers reside on filesystem only (no git) — consistent with the substrate-residence column of the five-tier table (see §2 lines 122–128).
- **Survival semantics.** Each tier's "survives across" property is a contract: artifacts at tier T are guaranteed to be readable at all future times within T's survival scope. `working` and `episodic` survival is run-bounded; `semantic`, `procedural`, and `durable` survival is durable across runs.
- **Cross-tier traceability.** Every `durable`-tier ledger entry references the `procedural`-tier artifacts in scope at the entry's write-time via the `procedural_tier_snapshot_ref` sidecar field at C-IS-05 §5.1 (D-derivative extension of the F-layer six-field shape per ADR-F2 §Consequences (c)). The `action_id` field MAY independently encode action class / sub-class metadata per the §5 field-spec footer; the MAY (action class) and MUST (procedural-tier ref via sidecar) composition is non-conflicting — both can hold at the same entry without conflation. This composition enables replay of the procedural-tier state at any prior durable-tier entry timestamp by re-resolving the snapshot content-hash against the current `HarnessContext` (verification) or by looking up the historical procedural artifacts at filesystem+git (recovery; the artifacts themselves persist at filesystem+git per the row 4 substrate-residence column).

**Deferred to implementation discretion.** Specific filesystem path conventions per tier (e.g., `.harness/working/`, `.harness/episodic/`, `.harness/semantic/`); tier-internal subdivisions (e.g., per-workload-class subdirectories); cross-deployment-surface tier-residence overrides per ADD §3 OD-2.A flex.

---

## §3 C-IS-03 — Combined git tier role decomposition

**Contract surface.** Five-sub-role git tier composition with foundational-vs-opt-in posture per sub-role.

**PRD requirement(s) satisfied.** R-IS-02 (git as combined-tier state record).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (combined git tier serving five-sub-role composition); ADD §2.2 Synthesis ("Git serves a combined role: code/spec/prompt/manifest/Skill versioning (foundational) + append-only state-ledger via commit stream + JSONL event ledger (foundational) + on-demand shadow-Git checkpointing (workload-class-opt-in) + worktree-isolation for concurrent sub-agent reads (workload-class-opt-in)").

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit ledger as foundational primitive); §5.1 (remote git of GitHub/GitLab class); §10.2 (cost-attribution-per-span composes against the JSONL event ledger).

**Specification content.**

The combined git tier serves five sub-roles within a single git repository; each sub-role carries a posture commitment:

| Sub-role | Function | Posture | Composition contract |
|---|---|---|---|
| **Versioning** | Code/spec/prompt/manifest/Skill atomic versioning via git commit history | **Foundational** (always-on; no opt-out) | Composes with C-IS-04 atomic deploy contract |
| **State-ledger via commit stream** | Append-only state-ledger expressed as the git commit stream itself (commit hashes form a chain natively); workflow-canonical commit cadence per workflow class | **Foundational** (always-on; no opt-out) | Composes with JSONL event ledger sub-role; commit-stream-as-coarse-grain-ledger pairs with JSONL-as-fine-grain-ledger |
| **JSONL event ledger** | Per-event append-only JSONL file at workflow-canonical path (per C-IS-01); per-event records carry the canonical six-field entry shape (per C-IS-05); hash-chain integrity constructed per C-IS-06 | **Foundational** (always-on; no opt-out) | Composes with commit-stream sub-role and with C-IS-05 + C-IS-06 entry-shape + hash-chain commitments |
| **Shadow-Git checkpointing** | On-demand checkpoint snapshots via shadow-repository pattern (Cline / kilocode / Roo Code precedent per ADR-F2 §Rationale (a)) | **Workload-class-opt-in** (per workflow manifest declaration per C-IS-08) | Composes with C-IS-08 contract; opt-out workloads do not produce shadow-Git artifacts |
| **Worktree-isolation for concurrent sub-agent reads** | Per-sub-agent worktree directories via `git worktree` primitives; isolates concurrent reads from sibling sub-agents | **Workload-class-opt-in** (per workflow manifest declaration per C-IS-09) | Composes with C-IS-09 contract; opt-out workloads do not allocate worktree directories |

**Sub-role co-residence contract.** All five sub-roles share the same git repository identity without interference:

- Versioning operates on the main repository's branch heads.
- State-ledger via commit stream operates on the main branch's commit history; commit messages MAY encode state-ledger-relevant metadata.
- JSONL event ledger is a file artifact tracked in git (versioned via the versioning sub-role); appends to the file produce diff-traceable commits.
- Shadow-Git checkpointing operates via separate shadow refs/branches; does not pollute the main branch commit history.
- Worktree-isolation creates per-sub-agent working directories pointing at the same `.git` storage backend; reads do not contest with one another.

**Cross-sub-role consistency invariant.** A given git repository hosts at most one harness state-ledger; the five sub-roles share that ledger. Cross-repository state-ledger composition is out of scope at F2 substrate layer; per-tenant repository isolation at multi-tenant binding is the F2-compatible scaling shape per ADR-F2 §Consequences (a).

**Deferred to implementation discretion.** Specific commit cadence policy per workflow class; specific commit message conventions for state-ledger-relevant metadata; specific shadow-ref / shadow-branch naming conventions; specific worktree directory naming conventions; specific git hosting backend (GitHub / GitLab / Gitea / self-hosted) per deployment-surface cell.

---

## §4 C-IS-04 — Atomic prompt + code + eval + manifest deploy contract

**Contract surface.** Atomicity contract over the prompt + code + eval + manifest deploy unit.

**PRD requirement(s) satisfied.** R-IS-02 (git log inspection reveals atomic prompt+code+eval+manifest deploys).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Consequences (a) ("Prompts-as-files in git, atomically deployed alongside code and evals (Cluster 2 V2 §3.4.1 [HIGH])"; "Eval-set residence in git enables atomic prompt+code+eval deploys"); ADD §2.2 Synthesis.

**Persona linkage.** Persona §5.1 (state lives on local filesystem + remote git); §7 (pragmatic-mixed ecosystem affinity — git-as-deploy-substrate compatible with all language ecosystems).

**Specification content.**

The deploy unit consists of four co-located artifact classes:

- **Prompts** — plain-text prompt files per C-IS-01.
- **Code** — workflow implementation code (Python-first per Persona §7).
- **Eval-sets** — eval-set artifacts (eval inputs, expected outputs, eval scripts) co-located with the code they evaluate.
- **Routing manifest** — per ADR-F1 v1.2 Consequences §(a) manifest-layer model assignment.

**Atomicity contract.**

A "deploy" event is the application of a single git commit (or atomic commit-group via merge commit / tagged release) that updates one or more of the four artifact classes. The atomicity property commits:

| Property | Contract |
|---|---|
| **All-or-nothing per commit** | A commit either applies all its prompt + code + eval + manifest changes or applies none of them; partial application is precluded by git's commit atomicity at the storage layer |
| **Single-version observability** | The downstream maintainer inspecting any single git commit observes a coherent snapshot of all four artifact classes at that commit's revision |
| **Composition with C-IS-03 commit-stream sub-role** | Every deploy commit is itself a state-ledger entry at the commit-stream sub-role (per C-IS-03); the commit's message metadata MAY tag the deploy as a release |
| **Composition with C-IS-08 shadow-Git checkpointing** | Shadow-Git checkpoints (per C-IS-08) are orthogonal to deploys; checkpoint cadence and deploy cadence are independent commitments |

**Verification surface.** Git log inspection at any commit reveals the prompt + code + eval + manifest revision active at that commit; bisection across the commit history isolates regression boundaries per atomic deploy unit.

**Deferred to implementation discretion.** Specific deploy tagging conventions; specific eval-set file format (JSON / YAML / JSONL); specific commit-message-driven deploy-event annotation conventions.

---

## §5 C-IS-05 — State-ledger entry shape signature

**Contract surface.** Six-field record type with per-field type/format/semantic precision.

**PRD requirement(s) satisfied.** R-IS-03 (state-ledger entry shape with hash-chain integrity — entry shape half).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (state-ledger entry shape); ADD §2.2 Synthesis ("the state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` becomes the harness-canonical substrate").

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit foundational primitive); §10.2 (cost-attribution-per-span composes against the JSONL event ledger as the per-event audit surface).

**Specification content.**

The state-ledger entry record is a six-field tuple with the following per-field specification:

| Field | Type / format | Semantic | Constraint |
|---|---|---|---|
| `action_id` | Identifier — unique per action occurrence | Identifies the action this entry records | Unique within the ledger; harness-generated; MAY encode action class / sub-class metadata |
| `idempotency_key` | Identifier — stable per logical operation | Harness-canonical join key per ADD §2.2 Synthesis | Stable across retry attempts of the same logical operation; the join key for cross-axis composition (engine event history at D1, audit-ledger signing at D5, sandbox-violation events at D2, span emission at D6) per ADD §2.2 closing sentence |
| `actor` | Identifier — agent / sub-agent / operator | Identifies the entity that originated the action | Drawn from the active workflow's actor namespace |
| `response_hash` | Bytes — SHA-256 digest | Hash of the canonical-JSON byte representation of the entry's payload content | Per-entry hash discipline per C-IS-06 |
| `timestamp` | Timestamp — monotonic ordering | The wall-clock instant the entry was written | Monotonically non-decreasing within a ledger (subject to clock-skew tolerance documented at implementation) |
| `prior_event_hash` | Bytes — SHA-256 digest OR all-zeros sentinel | The SHA-256 of the canonical-JSON byte representation of the prior entry; all-zeros sentinel for chain-inception entries | Chain-construction discipline per C-IS-06 |

**Field-shape extensibility commitment.** Per ADR-F2 §Rationale (a.1) "The *specific* canonicalization library binding ... and any per-workload-class extensions to the entry shape are D-derivative downstream per Consequences §(c)." The six-field shape above is the **F-layer minimum**; per-workload-class extensions are D-derivative.

**Composition with cross-axis seams.**

- D1 v1.1 engine event history joins on `idempotency_key` per ADD §3.1.1 + ADR-D1 v1.1.
- D5 v1.3 audit-ledger entries inherit the entry shape and add `audit.*` attribute namespace per ADR-D5 v1.3 §1.4 + §1.4.1.
- D2 v1.1 sandbox-violation events join on `idempotency_key` per ADR-D2 v1.1 §1.8.
- D6 v1.1 cost-attribution-per-span joins on `idempotency_key` per ADR-D6 v1.1 §1.5.

These cross-axis joins are documented at C-IS-10 (substrate seam exports surface).

**Deferred to implementation discretion.** Specific identifier format for `action_id` (UUID v4 / ULID / monotonic-counter); specific format for `idempotency_key` (Stripe-style hex string / UUID / structured); specific timestamp format (ISO 8601 / RFC 3339 / Unix-epoch nanoseconds); per-workload-class extensions to the six-field shape additional to §5.1 (D-derivative per ADR-F2 §Consequences (c)).

### §5.1 D-derivative sidecar field — `procedural_tier_snapshot_ref`

**Contract surface.** Optional 7th field extending the §5 F-layer six-field shape, authoring the canonical cross-tier traceability carrier per §C-IS-02 line 170.

**Field specification.**

| Field | Type / format | Semantic | Constraint |
|---|---|---|---|
| `procedural_tier_snapshot_ref` | Identifier — content-hash digest OR `None` | References the procedural-tier snapshot (active Skills version set + active prompt version + routing manifest SHA) in scope at the entry's write-time | Lowercase hex SHA-256 (64 chars) per §5.2 resolver contract; `None` permitted at entries written outside an active workflow context (bootstrap-stage entries; operator-explicit administrative entries) |

**Authorization basis.** ADR-F2 §Consequences (c) "per-workload-class extensions to the entry shape are D-derivative downstream" + §5 "Field-shape extensibility commitment" declaring the six-field shape as F-layer minimum + D-derivative authorization. The sidecar field is the documented D-derivative extension shape; no §5 main contract amendment owed.

**Composition with cross-axis seams.** The sidecar field composes orthogonally with the existing `idempotency_key` join surface declared at §C-IS-10 §10.2. Cross-axis consumers MAY query `procedural_tier_snapshot_ref` as a procedural-tier-snapshot join key (for replay-correlation across runs at the same snapshot); this composition is non-conflicting with existing `idempotency_key` join surfaces per §C-IS-10 §10.2 invariants.

**MAY/MUST composition reconciliation with §5 field-spec footer.** The §5 field-spec footer authorizes `action_id` MAY encode action class / sub-class metadata. The §C-IS-02 line 170 cross-tier traceability contract MUST flow via the §5.1 sidecar field. Both can hold at the same entry without conflation: `action_id="pause:01HQXY..."` (action class label preserved per existing convention) AND `procedural_tier_snapshot_ref="a3f4b2..."` (procedural-tier content-hash per §5.2). The two fields carry distinct semantics; the v1.3 amendment closes the previously-ambiguous composition by separating the carriers.

**Deferred to implementation discretion.** Specific cache shape for the resolver (per-call recompute vs same-input memoization); specific HarnessContext field-access pattern for the three procedural-tier components (direct attribute read vs accessor method); per-deployment-surface override for the `None` permission scope (whether managed-cloud or self-hosted-server tighten the permission to forbid `None` at non-bootstrap entries — a deployment-surface policy, not an F-layer contract).

### §5.2 Resolver contract — `resolve_procedural_tier_snapshot`

**Contract surface.** Pure function from `HarnessContext` to a content-hash `Identifier` identifying the procedural-tier snapshot in scope.

**Signature.**

```
resolve_procedural_tier_snapshot(harness_context: HarnessContext) -> Identifier
```

**Content-hash recipe (v1.9 — 4-component scope; supersedes the v1.5 3-component form via forward-only rebase).** The returned `Identifier` is the lowercase hex SHA-256 digest computed over the canonical-JSON byte representation of the four procedural-tier components, ordered alphabetically by component name:

```
canonical_payload = {
    "active_prompt_version": <str — HarnessContext.prompt_manifest.active_prompt_version.version_sha; "" when no active prompt>,
    "active_skills_versions": <list[str] — sorted ascending, dedup'd, SkillManifest.version_sha values from HarnessContext.skills>,
    "prompt_selection_manifest_sha": <str — SHA-256 over PromptSelectionManifest canonical-JSON bytes at HarnessContext.config.prompt_selection_manifest; "" when no selection manifest (None)>,
    "routing_manifest_sha": <str — SHA-256 over RoutingManifest canonical-JSON bytes at HarnessContext.routing_manifest>,
}
canonical_bytes = json.dumps(canonical_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
ref = sha256(canonical_bytes).hexdigest()
```

The recipe is deterministic + byte-stable across runs at the same procedural-tier state. The `sort_keys=True` + alphabetical component ordering + sorted-dedup'd skills-versions list together establish the canonical-JSON discipline per C-IS-06 §6.1 per-entry canonicalization pattern. The v1.3 2-component form (`{active_skills_versions, routing_manifest_sha}`) is superseded at v1.5; the recipe widening is forward-only — historical entries are NOT migrated, and snapshot-ref equality is scoped within a single recipe-version generation (the v1.3 §5.2 prose already anticipated this rebase).

**Prompts component bound at v1.5 (was deferred at v1.3).** The architect rec named three procedural-tier components per §C-IS-02 line 163 (Skills, prompts, routing manifest). At v1.3 the prompts component had no runtime binding (apply-time empirical orientation at HEAD `8816ce9` surfaced no `active_prompt_version` field on `HarnessContext`; no `PromptManifest` carrier), so per X-AL-3 the spec did not commit the recipe to a phantom referent — it was deferred to a future runtime-binding-extension arc with three named preconditions. **At v1.5 (post-MVP closure R-CL-P4; fork `.harness/class_1_fork_prompts_management_surface_active_prompt_version.md`, operator-ratified 2026-06-11) all three preconditions are satisfied and the component is bound:** (1) the runtime spec authors `HarnessContext.prompt_manifest: PromptManifest` at runtime spec v1.42 §4 C-RT-04 (the `active_prompt_version: PromptVersion` runtime binding lives carrier-homed within the manifest, mirroring how `routing_manifest` carries `routing_manifest_sha`); (2) the `PromptManifest`/`PromptVersion` carrier lands at `harness_is.prompt_manifest` homing prompt-version metadata (mirror `RoutingManifest`, frozen + `extra="forbid"`); (3) `resolve_procedural_tier_snapshot` reads `ctx.prompt_manifest.active_prompt_version.version_sha` at write-time. The recipe component is named `active_prompt_version` (the per-prompt version digest), mirroring how `active_skills_versions` are per-Skill version digests. The carrier is empty-defaultable (`version_sha=""` → no active prompt) so operators that do not version prompts carry zero config burden — the `routing_manifest` `default_factory` precedent (fork DP-1/DP-4). The `prompts/` path-class taxonomy at `harness-is/atomic_deploy_event.py:159` PROMPTS classification remains the filesystem-layer operational referent. The fuller prompts-management surface (multi-prompt versioning + selection, with a materialization stage) is a separate forward arc per fork DP-4. Hash rebasing at this binding is forward-only (historical entries are NOT migrated; snapshot-ref equality is scoped within a single recipe-version generation) — exactly as the v1.3 prose anticipated.

**`active_prompt_version.version_sha` is content-derived at v1.6 (R-PM-1 cascade PR #1 — provenance-tightening).** v1.5 bound `active_prompt_version.version_sha` as a free-standing version *identity* (an opaque operator-set digest). At v1.6 (R-PM-1 cascade PR #1; runtime-injection co-published at runtime spec v1.44 §14.5) the `PromptVersion` carrier gains a minimal inline `content: str = ""` field, and `version_sha` becomes **content-derived**: `version_sha == prompt_version_sha(content)`, where `prompt_version_sha(content)` returns `""` (the empty-carrier sentinel — no active prompt, no injection) for empty content and the lowercase hex SHA-256 of the UTF-8 content bytes otherwise. The invariant is enforced at carrier construction (detect-then-refuse). **This is a provenance-tightening, NOT a recipe change**: the recipe above is byte-identical (still reads `active_prompt_version.version_sha`); only how that `version_sha` is *produced* tightens. The reason is replay-integrity: the runtime cascade injects `content` as a per-provider system prompt, so if `version_sha` were not content-derived, injected content could change while this §5.2 hash reports "unchanged" (a silent provenance gap). With the invariant, content and its hash component move together. Empty-carrier configs (`content=""` → `version_sha=""`) are unchanged; configs that supply content rebase the procedural-tier snapshot forward (forward-only, as the v1.3/v1.5 prose anticipated). The inline `content` carrier is the minimal PR #1 source; the multi-version `PROMPTS`-path-class content store + per-role/workload selection are the PR #2/#3 cascade arcs per the R-PM-1 design.

**`prompt_selection_manifest_sha` bound at v1.9 (R-FS-1 arc B4 — per-role prompt coherence).** R-FS-1 arc B4 (`.harness/class_1_fork_b4_per_role_prompt_procedural_tier_hash_coherence.md`) makes a fan-out branch's **per-role** prompt take effect: a branch's `step_context.agent_role` selects a per-role prompt (`PromptSelectionManifest.per_role_bindings[role]` → `version_sha` → store content) whose `content` is injected at the runtime §14.5.2 translate seam. Through v1.8 the recipe read only the resolved **default-role** `active_prompt_version.version_sha` (coherent because `reconcile_active_prompt_via_selection` *mutates* that single slot so both the §14.5.2 injection reader `.content` and this §5.2 reader `.version_sha` read the same member). A per-role injection cannot share that one slot — N roles need N versions — so per-role bindings were **not** hash-visible: flipping a `per_role_bindings` entry changed a branch's injected content while this hash reported "unchanged", reintroducing the §14.5.2-forbidden drift for the per-role dimension. The asymmetry that decides the fix: the recipe **already** hashes the *whole* `routing_manifest` (so the routing manifest's `per_role_bindings` *are* hash-visible) — the prompt-selection manifest's were not. v1.9 closes this **symmetrically**: a 4th component `prompt_selection_manifest_sha` = SHA-256 over the whole `PromptSelectionManifest` canonical-JSON bytes (`model_dump(mode="json")` + `sort_keys=True` + compact separators, exactly as `routing_manifest_sha`), read from `HarnessContext.config.prompt_selection_manifest` — the operator-supplied `RuntimeConfig` field that is the selection manifest's spec'd home. Unlike `prompt_manifest`/`routing_manifest` (stage-reconciled/-enriched top-level carriers the recipe reads directly), the selection manifest is NOT stage-enriched (the resolver reads the same value config carries), so it needs **no** dedicated top-level `HarnessContext` carrier and owes **no** runtime-spec §4 C-RT-04 field row. `None` (no selection manifest) → `""`, the empty-selection sentinel — byte-identical to a no-selection run. Because the selection manifest binds `version_sha`s and `version_sha` is content-derived (the v1.6 derive-invariant) over a content-addressed store, hashing the manifest captures any per-role injected-content change — the §14.5.2 invariant is restored for the per-role dimension. **This widens the recipe** (3 → 4 component), so it is a forward-only hash rebase exactly as the v1.3/v1.5 prose anticipated (no migration of historical entries; snapshot-ref equality scoped within a single recipe-version generation). It is **not** a §5 six-field-shape / §5.1 sidecar / §5.3 store / §5.4 `branch_metadata` / §6 hash-chain / §7 read-write / §10 seam-export change — the recipe-internal component count is a §5.2 resolver detail (the v1.5 framing).

**Direct-compute storage discipline.** No separate snapshot-keyed registry persists at H_T. The resolver re-computes from current `HarnessContext` state at every call. The procedural artifacts themselves persist at filesystem+git per §C-IS-02 line 163 (substrate residence for the procedural tier); the snapshot identity is a derived content-hash, not a stored registry key. Replay correctness is preserved: re-computing the resolver against historical `HarnessContext` state at filesystem+git yields the same hash, enabling cross-run replay-correlation without registry persistence.

**Cluster-boundary call site discipline.** Composers with `HarnessContext` access at firing time read the resolver result at entry-construction time (synchronous in-process call). Engine-layer composers without `HarnessContext` access at firing time (e.g., `pause_resume_protocol.py` free functions per CP spec v1.25 §16.5.7 + §16.5.8) receive `resolve_procedural_tier_snapshot: Callable[[], Identifier]` as a kw-only parameter at the composer function signature, bound at runtime composition time per the `ledger_writer` kw-only-callable-bound-at-runtime-wiring precedent. The composer never threads `HarnessContext`; the callable closure captures whatever resolution-time state is needed.

**Replay semantics.** Two distinct replay modes both supported:

- **Verification** — at replay time, re-compute `resolve_procedural_tier_snapshot(current_harness_context)` and compare against the stored `procedural_tier_snapshot_ref` at the historical entry; equality confirms the procedural-tier state at replay time matches the state at write time.
- **Recovery** — at replay time, query filesystem+git for the procedural-tier artifacts at the historical entry's timestamp; the recovery surface is at filesystem+git per §C-IS-02 line 163, not at the ledger entry. The `procedural_tier_snapshot_ref` content-hash enables operator-side cross-checking that recovery returned the correct artifact set.

The recipe + direct-compute storage discipline establish that "replay" semantics here are at the engine-replay layer (CP/OD axes) per `[CF-1]` F2-12, NOT at the procedural-tier-state-reconstruction layer (which would require either α-2 opaque-key + persistent registry OR α-3 self-describing struct shape; both foreclosed at v1.3 apply-pass per Q-α=(α-1) ratification).

**Deferred to implementation discretion.** Whether resolver implements same-input memoization (cache HarnessContext-hash → resolver-result; invalidate on procedural-tier-mutation hook trigger); whether the resolver lives at `harness-is` or at a sibling package (resolver primitive is intra-IS-axis per Q2=narrow but consumer sites are cross-axis); specific monotonic-write-discipline around the 3 skill-activation hook firing sites + operator-explicit `HarnessContext.activate_skill(...)` method per runtime spec v1.32 §14.17 (whether the resolver result is captured at composer-entry vs at write-time — a single-call composer captures consistent state regardless, but multi-call composers spanning a skill-activation hook would observe a mid-composer transition; the production discipline is "capture once at composer-entry, thread through" per the `ledger_writer` precedent).

### §5.3 Prompts versioned authoring store — `PromptManifest.versions` (v1.7 — R-PM-1 cascade PR #2)

**Contract surface.** The multi-version authoring store for prompt content on the `PROMPTS` path-class (C-IS-01 §1) — added to the `PromptManifest` carrier *alongside* the §5.2 `active_prompt_version`.

**Authoring layer, not a recipe change.** §5.2 binds *which one* version is active (the `active_prompt_version.version_sha` that enters the procedural-tier hash). §5.3 authors *the set of versions an operator has authored*. These are orthogonal: §5.3 adds the authoring substrate; it does NOT enter the §5.2 recipe and does NOT change any §5/§5.1/§5.2 contract. The PROMPTS path-class (C-IS-01 §1: "Plain-text-file-in-git; one file per prompt artifact; prompts loaded as stable static-prefix content") is the operational residence the store represents; the carrier follows the operator-supplied-carrier pattern (`RoutingManifest`/Skills — declarative config), not runtime filesystem-scanning. A filesystem-materialization stage (scan the PROMPTS directory → build the store) remains the deferred forward arc the v1.5 §5.2 prose named.

**Store specification.**

| Field | Type | Semantic | Default |
|---|---|---|---|
| `PromptManifest.versions` | `tuple[PromptVersion, ...]` | The content-addressed authoring store: the set of prompt versions an operator has authored on the PROMPTS path-class. Each entry carries `content` + `version_sha = prompt_version_sha(content)` per the §5.2 v1.6 derive-invariant. | `()` (empty store) |

**Content-addressing authoring discipline.** Each stored version's `version_sha` is the SHA-256 digest of its `content` (per the v1.6 `prompt_version_sha` invariant, now applied across a collection). Authoring = the operator supplies content; the sha derives. The `from_contents(manifest_version, contents, active)` builder content-addresses a set of content strings into the store and selects an active member (or `active=None` → no active selection). The discipline mirrors the routing-manifest plain-text-in-git pattern (content is the source; identity derives).

**Internal-coherence invariants (enforced at carrier construction — detect-then-refuse).** With a **non-empty** store:

- **(a) Authored entries only.** Every entry has `version_sha != ""`. The empty-carrier sentinel (`version_sha=""`) is the no-active-prompt marker on `active_prompt_version` (§5.2), never a stored authored version.
- **(b) Content-addressed uniqueness.** No two entries share a `version_sha` — duplicate content is one version (content-addressing makes uniqueness structural; a duplicate is refused).
- **(c) Active-selection membership.** A non-empty `active_prompt_version` MUST be a member of the store (its `version_sha` present): an operator cannot activate a version they have not authored. A `version_sha=""` active selection (authored-but-none-selected) is permitted with a non-empty store — selection is the PR #3 CP arc.

An **empty** store (the default `()`) short-circuits these invariants: `active_prompt_version` stands alone with no membership obligation — the #496/PR-#1 behavior preserved verbatim, forward-compatible with v1.6 inline-only configs.

**Additive + forward-only — NOT a generalization-into the active version.** The store is added *alongside* `active_prompt_version`, which stays an **inline** record (`version_sha` + `content`). The §5.2 hash reader (`active_prompt_version.version_sha`) and the runtime stage-5 injection reader (`active_prompt_version.content`, runtime spec v1.44 §14.5.2) are byte-unchanged. A true generalization — content moving *into* the store with `active_prompt_version` becoming a pure sha-reference resolved against it — would change both readers and compose with the per-role/workload selection layer; that is the PR #3 CP cascade arc, deliberately out of scope here. **Transitional duplication, named:** when a non-empty active selection is also a store member, its content is duplicated against the store entry — but byte-identically *by construction* (content-addressing: equal `version_sha` ⟹ equal content), not as an independent authority that can drift. PR #3 removes the duplication by collapsing the active selection to a reference.

**No pre-built consumer interface.** The store has no runtime consumer at PR #2. The sha→content resolution the selection layer will need is deliberately NOT pre-built — PR #3 (its consumer) defines the lookup it actually requires (by-role binding → version_sha → content). §5.3 commits only the authoring substrate + the content-addressing discipline + the internal-coherence invariants.

**Verification shape.** Carrier-coherence unit tests (construction + the (a)/(b)/(c) invariants + the `from_contents` builder + empty-store forward-compat) — the appropriate shape for an additive carrier with no behavioral path until PR #3 wires selection. There is no end-to-end behavior to exercise at PR #2 (`[[verification-shape-sharpened-grep-vs-e2e]]`: e2e proves transit; here there is no transit yet, so unit-level carrier coherence is the matched claim).

**Deferred to implementation discretion.** Whether the store is later keyed (a sha→version index) for O(1) resolution vs scanned (the version count is small); the per-role/workload selection surface that drives `active_prompt_version` from the store (PR #3, CP-axis); the filesystem-materialization stage that builds the store from PROMPTS-path-class files (a forward arc per the v1.5 §5.2 deferral); any `merge`/`replace` policy if a version is superseded.

### §5.4 D-derivative sidecar field — `branch_metadata` (v1.8 — R-FS-1 B1 non-linear topology)

**Contract surface.** Optional 8th field extending the §5 F-layer six-field shape (alongside the §5.1 7th field `procedural_tier_snapshot_ref`), persisting the fan-out **branch causality** + per-branch **terminal disposition** the CP non-linear-topology driver composes per CP spec v1.32 §25.13 (Route Y). This is the coordinated IS amendment that CP spec v1.32 §25.13 forward-references ("the `branch_metadata` sidecar … authored at the coordinated IS amendment B1-spec-1b").

**Producer-supplied, not resolver-derived.** Unlike §5.1's `procedural_tier_snapshot_ref` (derived from `HarnessContext` by the §5.2 resolver), `branch_metadata` is **composed by the CP `WorkflowDriver`** at branch-spawn and at branch-termination per CP spec v1.32 §25.11 / §25.13 / §25.15 — the CP driver is the producer; the IS sidecar is the persisted carrier. There is therefore **no resolver contract** for this field (no §5.2 analogue).

**Field specification.**

| Field | Type / format | Semantic | Constraint |
|---|---|---|---|
| `branch_metadata` | Structured record (`BranchMetadata`) OR `None` | Records the fan-out branch this entry belongs to + the branch's terminal disposition | `None` at every entry written outside a fan-out branch — the `SINGLE_THREADED_LINEAR` strategy, bootstrap-stage entries, and any non-branch step (the overwhelming majority of entries; **every pre-v1.8 entry**). Non-`None` only on entries the CP driver writes under a child branch `StepExecutionContext` (CP spec v1.32 §25.11). |

`BranchMetadata` is a three-field record:

| Sub-field | Type / format | Semantic | Constraint |
|---|---|---|---|
| `parent_action_id` | Identifier | The `action_id` of the spawning step (the child `StepExecutionContext.parent_action_id` per CP spec v1.32 §25.11) | Resolves to a prior persisted entry's `action_id`; `action_id` is globally unique per §5, so `(parent_action_id, branch_index)` uniquely identifies a branch even under nested fan-out — no `branch_path` is needed at this persisted causality carrier (`branch_path` is a CP-side §25.16 *idempotency-key* composition detail, not the causality key) |
| `branch_index` | Integer ≥ 0 | The branch's 0-based ordinal within its fan-out (deterministic declaration order per CP spec v1.32 §25.12) | Non-negative; unique per `parent_action_id` |
| `terminal_status` | Closed-set disposition (`{cancelled, completed, timed_out}`) OR `None` | The branch's **dispatch-boundary terminal disposition** | `None` on a branch's non-terminal step entries; exactly one of the three values at the branch's terminal entry. Value-set + per-value semantics are owned by the CP producer at CP spec v1.32 §25.15.2 obligation 4: `cancelled` ⟹ the branch terminated at a not-yet-dispatched boundary (no effectful dispatch at the termination point); `completed` / `timed_out` ⟹ the branch's in-flight step ran. Closed at cardinality 3; widening is a coordinated CP+IS revision (the value set is CP-producer-owned). Typed (closed-set), not a free-form string — see the §7.5 contrast + Route-X-rejection note below. |

**`terminal_status` is dispatch-boundary disposition, not step-outcome.** A branch whose in-flight step *ran and errored* is `completed` (its dispatch attempt completed); the step's own success/failure is recorded at that step's ordinary ledger entry per CP spec v1.32 §25.15.2 obligation 3 ("every dispatched effectful step has its own recorded step ledger entry"). This is why the value set has **no `failed` member** — step-outcome lives at the step entry, while `terminal_status` records only whether the branch dispatched / was cancelled-before-dispatch / timed-out-at-its-barrier. The discrimination keeps audit-as-primary-defense non-hollow (CP §25.15.2 obligation 4).

**Relationship to the sibling CP disposition vocabularies (cross-spec reconciliation — descriptive).** Three other CP-axis disposition value-sets exist, at distinct carriers; `branch_metadata.terminal_status` is a fourth, observably distinct from each:

- `SubAgentResultStatus` `{completed, failed, cascade-cancelled}` — the `subagent.result_status` **span attribute** (C-CP-14 §14.2; the observability/telemetry carrier).
- `CascadeDecisionAtFanoutClose` `{completed, cascade-cancelled, paused-on-failure}` — the **aggregate fanout-close decision** recorded in the separate (non-F2) `parent_fanout_close_entry` primitive (C-CP-15 §15.2; the topology-boundary carrier).
- `RunStatus` `{SUCCESS, DRAINED, FAILED, PARTIAL, PAUSED}` — the **run-level** terminal status (C-CP-25 §25.2).

These are distinct token sets recorded on **distinct carriers** — a `subagent.*` span attribute / the separate non-F2 fanout-close primitive / the run-level `RunResult` / this per-branch F2-entry sidecar — **no two of which are ever the same field on the same object**, so there is no comparison column where a collision could arise. The distinctness rests on **carrier-segregation, not token-disjointness**, and `completed` illustrates precisely why segregation (not "consistent meaning") is the right rationale: `terminal_status` shares the token `completed` with `SubAgentResultStatus`, but on different objects and with a *different* meaning — `terminal_status.completed` is **dispatch-boundary** (a ran-and-errored branch is `completed`, per above) whereas `SubAgentResultStatus.completed` is step-**success**; and `RunStatus` does not use `completed` at all (its terminal-success token is `SUCCESS`). `timed_out` (per-branch bounded-barrier exhaustion, CP §25.11) appears on no other carrier; the branch's own `cancelled` is a distinct token from the parent-aggregate's `cascade-cancelled` decision; and `terminal_status` carries neither `failed` nor `paused-on-failure` because step-outcome and run/aggregate-level decisions are recorded at their own carriers. Because the carriers never share a comparison column, these value-set differences cannot produce a harmful collision. CP spec v1.32 §25.13 / §25.15 commits this per-branch value set but does not carry a reciprocal cross-reference to the sibling enums; that reciprocal CP-side note is flagged a **Class 3 informational** doc-coordination item (non-blocking; foldable into a future CP touch — e.g. B1-spec-2 / B1-plan), not a contract defect — the committed value set is coherent and buildable.

**Authorization basis.** ADR-F2 §Consequences (c) "per-workload-class extensions to the entry shape are D-derivative downstream" + §5 "Field-shape extensibility commitment" declaring the six-field shape as F-layer minimum + D-derivative authorization — the same authorization §5.1 invokes. `branch_metadata` is the documented D-derivative extension shape for fan-out branch causality; no §5 main-contract amendment owed, ZERO change to the six-field shape.

**Hash-chain composition (canonicalization-contribution discipline; §6 construction unchanged).** `branch_metadata` is entry **payload content**: when non-`None` it participates in the §6.1 canonicalization and therefore the §6.2 `response_hash` — so branch causality + `terminal_status` are tamper-evident per §6.5, exactly as `procedural_tier_snapshot_ref` is. The §6 construction **discipline is unchanged**: the canonical payload includes the sidecar when non-`None` and **omits it when `None`** (the established §5.1 pattern — `entry_hash.py` `canonicalize` includes a sidecar field only `if … is not None`). Consequence: every pre-v1.8 entry (all of which predate non-linear topology, so carry `branch_metadata = None`) canonicalizes **byte-identically** to a v1.8 entry with `branch_metadata = None` — ZERO breaking change at the hash level for the existing chain; forward-only, no historical-entry migration (the §5.1 / §5.3 forward-only discipline).

**Append-only invariant — `terminal_status` is set at a fresh terminal entry, never by mutating a prior entry.** The hash chain is append-only (§6.3 construct-at-write-time; §6.5 tamper-evidence). `terminal_status` is therefore **not** a mutable field updated onto an already-written branch entry — that would re-hash a persisted entry and break the chain. It is recorded as part of the branch's **terminal entry**, written fresh at branch-termination time (CP spec v1.32 §25.13: the CP driver "composes branch metadata at branch-spawn + at cancel"); a branch's earlier step entries carry `branch_metadata.terminal_status = None`. *Which* entry carries the non-`None` terminal disposition (a dedicated branch-terminal marker entry vs. the branch's last step entry), and *which* entries carry `branch_metadata` at all (every branch step vs. spawn + terminal), are producer/runtime write-cadence concerns deferred to the runtime materialization at B1-spec-2 (CP spec v1.32 §25.18) — this §5.4 authors the carrier shape + the append-only invariant, not the write cadence.

**Composition with cross-axis seams.** `branch_metadata` composes orthogonally with the existing `idempotency_key` join surface (§C-IS-10 §10.2) and travels on the already-exported state-ledger entry shape (§C-IS-10 §10.1, consumed by AS / CP / OD) — it is not itself a new export seam. The CP driver is the sole producer (CP spec v1.32 §25.13); `api.resume` (C-RT-35) is a consumer, reading each branch's persisted `terminal_status` to enforce resume-terminality (CP spec v1.32 §25.15.2 obligation 7 — MUST NOT re-dispatch a `cancelled` / `completed` / `timed_out` branch).

**Persisted causality — contrast with §7.5 write-args.** Unlike `thread_id` / `step_id`, which §7.5 ratifies as write-time `WriteKey` write-arguments **not** persisted on `StateLedgerEntry`, `branch_metadata` **is** a persisted entry-level field — the durable branch-causality carrier the audit / replay / resume paths read. Route X — encoding branch causality + `terminal_status` into the `action_id` string — was rejected at the B1-spec-1 branch-causality fork (`.harness/class_1_fork_b1_branch_causality_route_x_vs_y.md`): IS spec v1.3 Amendment 3 (the §5.1 MAY/MUST reconciliation) ratifies that structured traceability flows via a sidecar, not action_id-encoding, and a string-parsed `terminal_status` is a fragile read path versus a typed field.

**Deferred to implementation discretion.** The carrier-home of the `BranchMetadata` record + the `terminal_status` closed-set type — a **shared type consumable across axes** (the CP driver is the producer; the IS entry carrier persists it), homed where the §C-IS-10 §10.1 entry-shape export is reachable by the CP consumer. The **one hard constraint**: it is **NOT** homed in `harness-cp` — the IS axis is consumer-most-upstream with **0 outbound cross-axis edges** (harness-is §1.1 / CXA §2.2), so IS cannot import from CP; CP consumes the entry shape from IS via the established CP→IS direction. Whether the type lives at `harness-core` (shared) or `harness-is` (with the entry shape) is a B1-impl-N decision, exactly as §5.1 deferred resolver residence. The write-cadence (which entry carries `terminal_status`; which entries carry `branch_metadata`) is deferred to the runtime materialization at B1-spec-2 (CP spec v1.32 §25.18). The serialization of the nested record within the §6.1 canonical payload (sub-field ordering, enum-value rendering) follows the existing `actor` nested-record canonicalization precedent (`entry_hash.py`), a B1-impl-N detail.

### §5.5 Operator-declared semantic-version field — `PromptVersion.version` (v1.10 — R-FS-2 B-18-LANEB-PROMPT-SEMVER)

**Contract surface.** A single additive optional field on the `PromptVersion` carrier (`harness_is.prompt_manifest`) — an operator-declared semantic-version *label*, distinct from and orthogonal to the content-derived `version_sha`.

**Field specification.**

| Field | Type / format | Semantic | Constraint |
|---|---|---|---|
| `PromptVersion.version` | `str \| None` | An operator-supplied semantic-version label for migration-tracking / lifecycle purposes only (e.g. `"1.0"`, `"2.1-rc"`) — the prompt-side analogue of the Skills `frontmatter.version` field ADR-D3 §1.8.1 commits ("operator may bump `frontmatter.version` … without changing every byte") | `None` (the default) = no operator-declared label — byte-compatible with every `PromptVersion` construction call site that predates this amendment (`PromptVersion(version_sha="")`, `PromptVersion.from_content(...)`, both unchanged). When supplied, free-text — no format validation, no cross-entry uniqueness constraint (contrast with Skills, where `version` is a *required* frontmatter constraint enforced fail-closed at the load seam per B-SKILL-FRONTMATTER-VALIDATOR, R-FS-2 Wave 1; the prompt-side field is deliberately optional, since no cited authority commits a required-and-validated posture for prompts) |

**Not the cache-hit key — `version_sha` remains sole cache-correctness identity.** `u1-slice3b-epoch-partition-design.md` §2.1 establishes that Anthropic's prompt cache is byte-exact, so the cache-correct epoch key is necessarily the byte-exact content hash (`version_sha`), never a coarser operator-declared label. `version` MUST NOT be read by any cache-epoch / cohort-key derivation; the CP `cohort_key` (`harness_runtime.lifecycle.llm_dispatch`) and the cacheable-epoch `prefix_content_hash` (`harness_runtime.lifecycle.cacheable_epoch`) both already read the scalar `prompt_version_sha` / `version_sha`, never the full `PromptVersion` model, so this constraint holds by construction with zero code change to either derivation.

**Not a §5.2 recipe component.** The `resolve_procedural_tier_snapshot` recipe's `active_prompt_version` component (§5.2) reads `active_prompt_version.version_sha` only. `version` does not enter the canonical payload — setting or changing `version` on the active prompt produces a byte-identical procedural-tier snapshot hash (a required control-witness property, verified by test).

**Not a §5.3 store uniqueness dimension.** The `PromptManifest.versions` store's internal-coherence invariant (b) — content-addressed uniqueness — is keyed on `version_sha` exclusively. Two store entries MAY declare the same `version` label (e.g. during a content rebase where an operator re-labels an existing semantic version onto new content pending a `version_sha` bump) without violating (b); invariants (a) and (c) are likewise `version_sha`-keyed and unaffected by this field.

**Derivation relationship to `content` / `version_sha` — none.** Unlike `version_sha` (`content`-derived, enforced at construction per the v1.6 derive-invariant), `version` has no derivation relationship to `content` and no construction-time invariant beyond its type. It is pure operator-supplied metadata, analogous to a git tag rather than a git commit hash.

**Verification shape.** Carrier round-trip (construct with/without `version`; frozen + `extra="forbid"` preserved); a byte-unchanged control witness at the §5.2 resolver (`resolve_procedural_tier_snapshot` returns an identical hash whether or not `active_prompt_version.version` is set, and regardless of its value) — the load-bearing cache-inertness proof, not merely a documentation claim.

**Deferred to implementation discretion.** Whether a future prompts-management UX surfaces `version` in any operator-facing listing/selection tool (the fuller prompts-management surface remains a separate forward arc per fork DP-4, unaffected by this narrow carrier addition); any future format convention (e.g. semver-string validation) if an operator workflow later wants one — not committed here, as no cited authority requires it.

---

## §6 C-IS-06 — Hash-chain integrity construction discipline

**Contract surface.** Construction-time discipline + verification-time procedure + tamper-evidence contract.

**PRD requirement(s) satisfied.** R-IS-03 (state-ledger entry shape with hash-chain integrity — hash-chain integrity half).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Rationale (a.1) "Hash-chain integrity construction as F-layer commitment" (full sub-section); ADD §2.2 Synthesis.

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit foundational primitive); §10.2 (cost-attribution-per-span composes against the JSONL event ledger as per-event audit surface).

**Specification content.**

Hash-chain integrity is constructed **at write-time** via the following four-step discipline (per ADR-F2 §Rationale (a.1)):

### §6.1 Per-entry canonicalization

**Signature.** `canonicalize(entry: StateLedgerEntry) -> bytes`

**Discipline.** Each state-ledger entry is canonicalized to a deterministic byte representation prior to hashing. RFC 8785 JSON Canonicalization Scheme (JCS) is the corpus-converged baseline candidate **[MODERATE — per ADR-F2 §Rationale (a.1), library binding to be confirmed at the D-ADR on canonicalization library per language ecosystem]**.

**Contract.** Canonicalization is deterministic — given the same logical entry, two canonicalizations on different runs / machines / library versions of the same canonicalization scheme produce identical byte sequences. Non-determinism in canonicalization is a contract violation.

### §6.2 Per-entry hash computation

**Signature.** `response_hash = SHA-256(canonicalize(entry))`

**Discipline.** The SHA-256 digest of the canonical-JSON byte representation produces the entry's `response_hash` field (per C-IS-05).

**Contract.** SHA-256 is the committed hash function at the F-layer; alternative hash functions are precluded at F2 substrate. The 256-bit digest output is the contract surface.

### §6.3 Chain construction at write-time

**Signature.** For entry N (1-indexed):
- If N = 1 (chain inception): `entry[N].prior_event_hash = ALL_ZEROS_SENTINEL` (32 bytes of zero)
- If N > 1: `entry[N].prior_event_hash = SHA-256(canonicalize(entry[N-1]))`

**Discipline.** The `prior_event_hash` field of entry N references the SHA-256 of entry N−1's canonical-JSON byte representation. Chain-inception entries reference the all-zeros sentinel hash.

**Contract.** The chain is constructed **at write-time** — entries cannot be written without `prior_event_hash` being computed against the prior entry. Concurrent-writer contention on the chain head is precluded by the C3-pole write contract (per C-IS-07).

### §6.4 Chain verification on demand

**Signature.** `verify_chain(ledger: List[StateLedgerEntry]) -> ChainVerificationResult`

**Discipline.** Chain integrity is verified by:
1. For each entry N in the ledger, re-canonicalize entry N to produce `canonical_bytes[N] = canonicalize(entry[N])`.
2. Re-compute `computed_hash[N] = SHA-256(canonical_bytes[N])`.
3. Verify that `entry[N+1].prior_event_hash == computed_hash[N]` for every N from 1 to len(ledger) − 1.
4. Verify that `entry[1].prior_event_hash == ALL_ZEROS_SENTINEL`.

**Contract.** Tamper-evidence is the verification's failure mode at any chain position — if any entry has been modified, the chain verification at the modified position (or any position downstream of it) fails. The verification surface is end-to-end inspectable by the downstream maintainer per R-IS-03 acceptance criterion.

### §6.5 Tamper-evidence contract

| Tamper scenario | Verification outcome |
|---|---|
| Entry-content modification (any field except `prior_event_hash`) | `computed_hash[N]` recomputes differently from `entry[N+1].prior_event_hash` → verification fails at position N+1 |
| `prior_event_hash` modification | Verification fails at the modified entry (its `prior_event_hash` no longer matches `computed_hash` of the prior entry) |
| Entry deletion (mid-chain) | Verification fails at the deletion position; the "new" entry at that position's `prior_event_hash` references a now-absent prior |
| Entry insertion (mid-chain) | Verification fails at the next downstream entry; the inserted entry's `prior_event_hash` either matches the wrong entry or fails the chain construction check |
| Chain-inception modification | Verification fails at entry 1 (`prior_event_hash` no longer equals the all-zeros sentinel) |

**Deferred to implementation discretion.** Specific canonicalization library binding per language ecosystem (RFC 8785 JCS reference implementation per Python / Go / Rust / TypeScript — D-derivative per ADR-F2 §Consequences (c)); specific SHA-256 implementation binding (language-stdlib / cryptography-library); specific verification-procedure performance optimizations (batch-verification / lazy-verification / streaming-verification).

---

## §7 C-IS-07 — State-ledger read/write contract pair (T-perm-2 F2-layer resolution)

**Contract surface.** Read/write contract pair at the state-ledger seam expressing T-perm-2 (C2 ↔ C3 — within-turn vs across-turn) F2-layer resolution shape.

**PRD requirement(s) satisfied.** R-IS-02 (JSONL event ledger) + R-IS-03 (state-ledger entry shape with hash-chain integrity — composition discipline).

**ADR commitment(s) honored.** ADR-F2 v1.2 §"Permanent tensions engaged" (T-perm-2 F2-layer resolution shape: read/write contract pair); ADR-F2 v1.2 §Consequences (c) "D-ADR on ledger entry schema fields and canonicalization library binding" (full sub-section on C3 write contract + C2 read contract composition); ADD §5.2.2 T-perm-2 F2-layer resolution.

**Persona linkage.** Persona §10.4 (compliance-readiness foundational primitive — hash-chained audit ledger); §10.2 (cost-attribution-per-span composes against the JSONL event ledger as per-event audit surface).

**Specification content.**

T-perm-2 (C2 ↔ C3 — within-turn vs across-turn) is **structurally permanent** per ADD §5.2.2; F2-layer resolution shape is a **read/write contract pair** at the state-ledger seam.

### §7.1 C3-pole write contract

| Property | Contract |
|---|---|
| **Append-only** | Writes to the state-ledger append new entries; existing entries are immutable post-write |
| **Structured** | Every entry conforms to the six-field shape per C-IS-05 |
| **JSON-not-Markdown** | Structured entry fields are JSON-encoded; Markdown-only representation is precluded per ADR-F2 §Rationale (b)(iii) Anthropic Nov 26 2025 guidance [HIGH] |
| **Idempotent** | Writes are keyed on `(thread_id, step_id, idempotency_key)` per Stripe-style convention per ADR-F2 §Consequences (c); a second write with the same key is a no-op against the existing entry |
| **Per-event JSONL with stable indexable shape** | The on-disk representation is JSONL (one entry per line); the line-per-entry structure enables indexable access without parsing the entire ledger |
| **Hash-chain-integrity-preserving** | Every write computes `response_hash` and `prior_event_hash` per C-IS-06 before persisting the entry |
| **Timestamp authority (v1.11)** | Caller-supplied `timestamp` on DIRECT appends, validated monotonic-non-decreasing per C-IS-05 §5 (detect-then-refuse); **writer-owned** on the buffered/branch-drain append surface — the writer samples the persisted `timestamp` at each entry's append inside the write serialization point, per §7.6; PLUS (B-48 apply-PR round-28/29 carve-out) the OFFLOADED SUB-AGENT dispatch audit appends — the one direct surface B-48's own concurrency newly exercises — which adopt writer-owned sampling per §7.6's scope-widening |

### §7.2 C2-pole read contract

| Property | Contract |
|---|---|
| **Selective** | Reads target specific entries or entry-ranges; full-ledger reads are precluded as the default read mode |
| **Bounded** | Reads at session start consume a bounded window of recent entries; bounding policy is workload-class-tunable |
| **Navigation-primitive-mediated** | Reads occur via navigation primitives exposed as Skills or in-process tools (per ADR-F2 §Consequences (c)); direct full-file `cat`-style reads are precluded for the read contract |
| **Read-into-dynamic-suffix** | Read content enters the model's dynamic suffix (not the static prefix); prompt-cache integrity is preserved by construction (per ADR-F2 §Rationale (b)(ii) cache-prefix detonation prevention) |

### §7.3 Composition format

**Composition format.** JSONL with stable indexable per-event shape per ADR-F2 §"Permanent tensions engaged".

The composition contract commits:

- **Storage representation** — JSONL file (one JSON-serialized entry per line) at workflow-canonical path per C-IS-01.
- **Per-entry shape** — six-field record per C-IS-05.
- **Indexable access** — line-per-entry structure permits offset-based indexing; navigation primitives exposed as Skills or in-process tools per the C2-pole read contract.
- **Concurrent access** — the C3-pole append-only write contract serializes writers; the C2-pole selective read contract permits concurrent readers.

### §7.4 Multi-seam T-perm-2 engagement (cross-axis context)

T-perm-2 is engaged at **three seams** per ADD §5.2.2:

| Seam | F-layer resolution | Cross-axis specification reference |
|---|---|---|
| State-ledger seam | F2-layer (this contract C-IS-07) | This specification |
| Secrets-in-sandbox-environment seam | F5-layer closure (tier-aware composition with F4 tier-set) | Action Surface specification (session 2) |
| OTLP collector boundary seam | D6-layer commitment (within-turn streaming + across-turn durable trace storage) | Operational Discipline specification (session 4) |

D-layer adjacency engagements at D1 (engine event history Tier-3 vs F2 state-ledger Tier-5 join on `idempotency_key`), D3 (Skills loading discipline vs filesystem residence), D4 (HandoffContext serialization), D5 (HITL pause-resume context revalidation), D6 (OTLP collector boundary) compose against this F2-layer contract without altering it (per ADD §5.2.2 D-layer adjacency rules).

**Deferred to implementation discretion.** Specific navigation primitive APIs (`read_entry(id)`, `read_range(start, end)`, `read_recent(n)`, `read_by_idempotency_key(key)` etc.); specific bounding-window-size defaults per workload class; specific concurrent-writer serialization mechanism (advisory lock / per-line flock / lease coordination); **the relationship between the C-IS-07 §7.1 idempotent-write keying tuple `(thread_id, step_id, idempotency_key)` and the C-IS-05 six-field entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)`** — specifically, whether `thread_id` and `step_id` are (i) embedded within `action_id`'s encoded metadata, (ii) implicit in run-context that scopes `idempotency_key` uniqueness, (iii) supplied as separate write-arguments not persisted as entry fields, or (iv) per-workload-class extension fields — was deferred at v1.1–v1.3 to a downstream D-ADR on ledger schema per ADR-F2 §Consequences (c), and is **resolved at §7.5 (reading (iii), ratified v1.4 — post-MVP closure R-CL-P4)**. The v1.1–v1.3 forward-cite naming F2-12 as "the open downstream resolution path" is refreshed at §7.5 (F2-12 CLOSED an adjacent D1/D6 replay/cost-dedup scope 2026-05-14, not this write-keying-tuple ↔ entry-shape reconciliation).

### §7.5 Keying-tuple ↔ entry-shape relationship — reading (iii) ratified (v1.4)

**Resolution.** The §7.4 deferral of the relationship between the §7.1 idempotent-write keying tuple `(thread_id, step_id, idempotency_key)` and the C-IS-05 six-field entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` is **resolved as reading (iii)**, ratified at post-MVP closure R-CL-P4 (operator decision 2026-06-10, re-confirmed 2026-06-11; fork `.harness/class_1_fork_keying_tuple_entry_shape_d_adr.md`):

> `thread_id` and `step_id` are supplied as **separate write-arguments** — carried on the write-time `WriteKey` structure (`harness-is/src/harness_is/state_ledger_write.py`), validated only for `write_key.idempotency_key == entry.idempotency_key` consistency — and are **not persisted as distinct `StateLedgerEntry` fields** and **not part of the dedup decision**. Idempotent-write dedup is global on the persisted `idempotency_key` alone: `append_ledger_entry` returns `IDEMPOTENT_NOOP` for any existing entry whose `idempotency_key` matches, regardless of `thread_id`/`step_id`. Per C-IS-05 §5 the caller supplies an `idempotency_key` that is **stable per logical operation** — that field *is* the dedup identity — so `thread_id`/`step_id` are caller-side scoping/context metadata, not dedup participants and not persisted.

This reading keeps the C-IS-05 §5 six-field shape **inviolate** (IS-AL-3) — it adds no entry field — and matches the landed implementation at HEAD: `WriteKey` carries `thread_id`/`step_id` as write-args, while `StateLedgerEntry` (`harness-is/src/harness_is/state_ledger_entry_schema.py`) persists the six fields plus the v1.3 D-derivative `procedural_tier_snapshot_ref` sidecar, none of which is `thread_id`/`step_id`. A future per-workload-class subclass MAY add `thread_id`/`step_id` as extension fields (reading (iv)) per the §5 "Field-shape extensibility commitment"; reading (iii) is the base contract and (iv) an admissible per-class D-derivative extension — the two compose, and (iii) does not preclude (iv).

**F2-12 forward-cite refresh.** The v1.1–v1.3 §7.4 deferral named *"F2-12 active engagement … the open downstream resolution path."* That forward-cite is **stale-as-described** (`[[stale-carry-text-disposition]]`): F2-12 is CLOSED (`F2-12_Closure_Declaration.md`, 2026-05-14) and resolved an **adjacent** scope — D1/D6 replay-trace-emission + cost-dedup, where `idempotency_key` serves as a trace-ingestion cost-dedup join key — **not** this write-keying-tuple ↔ entry-shape reconciliation, which F2-12 never owned. The reconciliation is resolved here at v1.4 by operator ratification, superseding the prior forward-cite. The §7.4 multi-seam T-perm-2 engagement table and the §[carry-forwards] [CF-1] F2-12 line are preserved verbatim as historical record (point-in-time accurate when authored); only this relationship-reconciliation is lifted out of deferral.

### §7.6 Timestamp authority at the buffered/branch-drain append surface — writer-owned (v1.11)

**Amendment authority.** B-48 apply arc §5 rider (d) — fork `.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md` (§4 item 7; RATIFIED 2026-07-18, OPTION B with all filing-settled riders) + apply-leg dyad `.harness/council-dyad-b48-apply-2026-07-18.md` (16/16 CONFIRM). The superseded-for-routing defect record `.harness/runtime_defect_sub_agent_inference_child_loop_bridge_deadlock.md` §8.3 identifies this as a C-IS-07 §7.1 write-contract change: previously the `timestamp` was caller-supplied on every append and merely *validated* non-decreasing; on the surface below, the writer is now the timestamp *authority*.

**The surface that changes.** The **buffered/branch-drain append path**: fan-out branch entries buffered during concurrent branch execution and drained at the barrier through the single real writer, per CP spec v1.32 §25.12 D1/D1.b (`drain_branch_buffers` at `harness_cp.workflow_driver` feeding `append_ledger_entry` at `harness_is.state_ledger_write`). Before v1.11 the drain captured one `drain_timestamp` OUTSIDE the IS writer's serialization point (`_WRITE_LOCK`) and re-stamped every drained payload with it; two sibling drains on separate threads could capture in one order while the lock serialized their physical appends in the opposite order → `NonMonotonicTimestampError` against the C-IS-05 §5 monotonic-non-decreasing constraint (the landed writer defaults to zero clock-skew tolerance).

**The contract.** On this surface the persisted `timestamp` is **writer-owned**: sampled at each entry's append, INSIDE the write serialization point (the same critical section that reads the prior entry, computes `prior_event_hash`, and appends). Any caller/drain-supplied timestamp on the write payload is a placeholder on this path and is NOT the persisted value. Consequences: (a) sampling order equals physical-append order, so the C-IS-05 §5 monotonic-non-decreasing constraint holds **by construction** on this surface — concurrent sibling drains cannot invert; (b) the pre-v1.11 one-drain-one-timestamp re-stamp semantic is superseded — entries of one drain MAY carry distinct (non-decreasing) instants, each sampled at its own append; (c) wall-clock regression between two lock-held samples remains a clock-source property governed by the C-IS-05 §5 clock-skew-tolerance framing, not a concurrency defect.

**Surfaces that do NOT change.** Every DIRECT append — the default `append_ledger_entry` contract: linear-workflow step appends, runtime cost writes and non-offloaded audit writes (the OFFLOADED sub-agent audit appends are the one carved-out exception per §7.1/§7.6 — B-48's own concurrency; rounds 28/29), administrative appends — keeps **caller-supplied** timestamp semantics verbatim, enforced detect-then-refuse by the existing monotonicity rejection (a timestamp earlier than the prior entry's beyond clock-skew tolerance raises `NonMonotonicTimestampError`).

**Registered residual (surfaced, NOT absorbed).** The defect record's §8.3 fix-direction prose reads broader than the ratified scope ("physical-append-order == timestamp-order *by construction* regardless of how many uncoordinated concurrent drains/direct-writers feed it") — extending writer-owned authority to DIRECT appends would also dissolve its facet (b) (a runtime audit / cost write's caller-side capture interleaving a drain's appends). The RATIFIED B-48 scope pins **only the drain/buffered surface** (the filing's §4 item 7 witness is the sibling-drain xfail). Concurrent DIRECT writers each sampling caller-side timestamps outside the serialization point can therefore still interleave in capture-opposite order and are still **refused at write, not reordered**. Extending writer-owned authority to direct surfaces would change caller-supplied semantics for every existing direct producer and requires its own back-flow; it is registered here as a surfaced finding, not silently absorbed — EXCEPT the OFFLOADED sub-agent audit append path, which rounds 28/29 carved OUT of this residual into B-48 itself (§7.1 row + §7.6 scope-widening: writer-owned there; `B-57` covers the remaining direct writers; `B-58`-adjacent clearance text updated in the same arc).

**Witness obligation (B-48 close gate).** The strict xfail `test_concurrent_sibling_drains_invert_timestamp` (`harness-cp/tests/test_workflow_driver_buffered_append.py`) asserts the correct behavior this contract commits (no monotonicity error; both sibling drains' entries persisted). At the B-48 impl arc the fix lands, the test flips to a passing witness, and the strict-xfail marker is REMOVED — B-48 cannot close over an accepted-failing concurrency witness.

**Deferred to implementation discretion.** The API carrier by which the drain path requests writer-owned sampling (a mode parameter / sentinel payload timestamp / dedicated writer entry-point), constrained to preserve the direct-path caller-supplied contract byte-verbatim; whether the pre-existing buffer-time placeholder field is retained on the write payload for diagnostic purposes.

---

## §8 C-IS-08 — Workload-class-opt-in shadow-Git checkpoint contract

**Contract surface.** Manifest declaration shape + checkpoint cadence parameter + reversal granularity contract.

**PRD requirement(s) satisfied.** R-IS-04 (workload-class-opt-in shadow-Git checkpoint and worktree isolation — shadow-Git half).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (on-demand shadow-Git checkpointing workload-class-opt-in); ADR-F2 v1.2 §Consequences (a) "Shadow-Git checkpointing as a workload-class-opt-in primitive (P-OD-4)"; ADD §2.2 Synthesis.

**Persona linkage.** Persona §3.1.1 (software engineering — F2 leverage maximal); §8.1 (software-engineering action surface — code execution + filesystem + git as primary).

**Specification content.**

### §8.1 Opt-in declaration shape

A workflow opts into shadow-Git checkpointing via its workflow manifest. The opt-in declaration shape commits:

| Field | Type | Semantic |
|---|---|---|
| `shadow_git_enabled` | Boolean | `true` ⇒ workflow produces shadow-Git checkpoint snapshots; `false` (default) ⇒ no shadow-Git artifacts |
| `shadow_git_cadence` | Enum / structured | Checkpoint cadence policy per §8.2 below; required when `shadow_git_enabled = true` |

### §8.2 Checkpoint cadence parameter

Checkpoint cadence is **workload-class-tunable** per ADR-F2 §Rationale (a) (workload-class-shaped fine-grained reversal). Cadence enumeration:

| Cadence value | Trigger semantic |
|---|---|
| `per_step` | Snapshot after every step boundary (highest granularity; corpus precedent: Cline's per-step pattern per ADR-F2 §Rationale (a)) |
| `per_tool_call` | Snapshot after every tool invocation that mutates filesystem state |
| `per_significant_change` | Snapshot triggered by workflow-defined "significant change" predicate (workload-class-shaped) |
| `per_explicit_marker` | Snapshot only when workflow explicitly invokes a `checkpoint()` marker |

**Cadence selection rule.** Persona §3.1.1 (software engineering — F2 leverage maximal) implies `per_step` or `per_tool_call` cadence as the default for software-engineering workloads where reversal granularity is high-value. Persona §3.1.3 (pipeline automation — durability tier mandatory) implies `per_explicit_marker` cadence as the default for hours-long-step pipeline workloads where per-step cadence inflates repo size without proportional reliability gain (per ADR-F2 §Rationale (a) Alternative 3 rejection).

### §8.3 Reversal granularity contract

A shadow-Git checkpoint is **rollback-targetable** — the harness can restore the workflow's filesystem state to the snapshot's contents. Rollback semantics:

- **Atomic** — rollback applies the checkpoint's state in full or not at all (per shadow-Git's git-native atomicity).
- **Filesystem-bounded** — rollback restores filesystem state under the workflow's tracked paths; rollback does NOT restore the state-ledger (the ledger is append-only per C-IS-07; rollback writes a new entry recording the rollback event).
- **Workflow-state-coherent** — after rollback, the workflow's filesystem state matches the checkpoint's recorded state; in-flight inference state is not restored (per C2-pole within-turn boundary).

### §8.4 Composition with C-IS-03 sub-roles

Shadow-Git checkpointing is implemented via **shadow refs / shadow branches** within the same git repository as the versioning + commit-stream-state-ledger sub-roles (per C-IS-03 sub-role co-residence contract). Shadow-Git artifacts do **not** pollute the main branch commit history; downstream maintainers inspecting the main branch see deploys + state-ledger commits, not per-step checkpoints.

**Deferred to implementation discretion.** Specific shadow-ref naming convention (`refs/shadow/<workflow-id>/<checkpoint-id>` or alternative); specific snapshot retention policy (keep-all / keep-last-N / age-bounded); specific rollback API surface; specific cadence-policy authoring schema in workflow manifest (YAML / JSON / TOML).

---

## §9 C-IS-09 — Workload-class-opt-in worktree-isolation contract

**Contract surface.** Manifest declaration shape + per-sub-agent worktree directory contract + concurrent-read isolation invariant.

**PRD requirement(s) satisfied.** R-IS-04 (workload-class-opt-in shadow-Git checkpoint and worktree isolation — worktree-isolation half).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (worktree-isolation for concurrent sub-agent reads workload-class-opt-in); ADR-F2 v1.2 §Consequences (a) "Worktree-isolation for the concurrent-sub-agent-read subset that fans out reads while preserving Cognition's single-threaded-write convergence"; ADD §2.2 Synthesis.

**Persona linkage.** Persona §3.1.1 (software engineering — F2 leverage maximal); §3.1.3 (pipeline automation — durability tier mandatory); §8.1 (software-engineering action surface).

**Specification content.**

### §9.1 Opt-in declaration shape

A workflow opts into worktree-isolation via its workflow manifest:

| Field | Type | Semantic |
|---|---|---|
| `worktree_isolation_enabled` | Boolean | `true` ⇒ sub-agent fan-out allocates per-sub-agent worktree directories; `false` (default) ⇒ no worktree allocation |
| `worktree_concurrency_cap` | Integer (optional) | Maximum concurrent sub-agent worktrees per workflow run; default unbounded (subject to filesystem capacity); per ADR-D4 v1.1 fan-out cap composition (cross-axis reference) |

### §9.2 Per-sub-agent worktree directory contract

When `worktree_isolation_enabled = true`, sub-agent fan-out (per ADR-D4 v1.1 orchestrator-workers / decentralized-handoff / hierarchical-delegation patterns) triggers per-sub-agent worktree allocation:

| Property | Contract |
|---|---|
| **Per-sub-agent worktree** | Each fanned-out sub-agent receives an isolated worktree directory pointing at the same `.git` storage backend as the parent workflow |
| **Worktree identity** | Worktree identifier is harness-generated; stable for the lifetime of the sub-agent |
| **Worktree termination** | Worktree directory is reclaimed at sub-agent termination (success or failure); **reclamation** = `git worktree remove` invocation + directory contents removal, triggered at an operator-policy-controlled lifecycle-marker boundary; reclamation MUST NOT delete the underlying `.git` storage backend |

### §9.3 Concurrent-read isolation invariant

| Invariant | Contract |
|---|---|
| **Read-read non-interference** | Concurrent sub-agents reading the same artifact via their respective worktrees do not block one another |
| **Read-write non-interference within worktree** | Sub-agent reads within its worktree are isolated from concurrent writes occurring in sibling worktrees (per `git worktree` semantics) |
| **Cross-worktree writer serialization** | Concurrent writes across sibling worktrees against the same `.git` storage backend are serialized per Cognition single-threaded-write convergence (per ADR-F2 §Consequences (a) reference to Brainstorm synthesis §1) |
| **Composition with sub-agent boundary** | Worktree-isolation composes with ADR-D4 v1.1 §1.5 sub-agent privilege inheritance + ADR-D2 v1.1 §1.4 sub-agent sandbox-tier monotonicity + ADR-D5 v1.3 §1.5.2 cross-deployment monotonicity per ADD §5.3.2 sub-agent boundary as monotonic-only descent (cross-axis composition — Action Surface + Control Plane specs detail downstream) |

### §9.4 Multi-writer scaling boundary

Multi-writer scaling beyond worktree-isolation requires a downstream D-ADR on coordination shape per ADR-F2 §Consequences (b) "Concurrent writes to substrate." Worktree-isolation is the F2-compatible scaling shape for the design-time persona; multi-tenant scaling at the bridging-arc binding adopts per-tenant repo isolation as the F2-compatible scaling shape per ADR-F2 §Consequences (a) "Per-tenant repo isolation as a clean F2-compatible scaling pattern at the bridging-arc multi-tenant binding (kilocode-style)".

**Deferred to implementation discretion.** Specific worktree directory location convention (`.worktrees/<sub-agent-id>/` or alternative); specific worktree-allocation API surface; specific cross-worktree writer-serialization mechanism (advisory lock / leader-election / single-threaded-write enforcer); specific worktree reclamation cleanup policy.

---

## §10 C-IS-10 — Substrate seam exports surface (cross-axis composition)

**Contract surface.** Substrate seams that F2 exports for downstream-axis specifications to consume by citation.

**PRD requirement(s) satisfied.** R-IS-01 (canonical filesystem paths) + R-IS-02 (combined git tier) + R-IS-03 (state-ledger entry shape with hash-chain integrity) — cross-axis composition surface.

**ADR commitment(s) honored.** ADR-F2 v1.2 §Consequences (c) (full enumeration of eleven downstream surfaces); ADD §2.2 Synthesis (state-ledger entry shape as "the harness-canonical substrate against which every downstream action composes"); ADD §5.2.2 T-perm-2 F2-layer resolution.

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit ledger as foundational primitive); §10.2 (cost-attribution-per-span composes against the JSONL event ledger).

**Specification content.**

The Information Substrate axis exports the following seams for cross-axis specifications (sessions 2–4 + session 5 composition document) to compose against by citation. Each seam declares (i) the export surface, (ii) the consuming axis/axes, (iii) the cross-axis composition reference.

### §10.1 State-ledger entry shape export

**Export surface.** Six-field record per C-IS-05.

**Consuming axes.**

| Consuming axis | Composition reference | Cross-spec citation target |
|---|---|---|
| Control Plane (D1 v1.1 engine event history) | Engine event history joins on `idempotency_key`; engine ledger is Tier-3 durability; F2 state-ledger is Tier-5 durability; the two ledgers compose at the join (per ADR-F3 v1.1 §Consequences (a) + ADR-D1 v1.1) | `Spec_Control_Plane_v1.md` C-CP-* on `idempotency_key` join |
| Operational Discipline (D5 v1.3 audit-ledger cryptographic shape) | Audit-ledger entries inherit the entry shape and add `audit.*` attribute namespace per persona-tier cryptographic shape (solo / team / multi-tenant) per ADR-D5 v1.3 §1.4 + §1.4.1 | `Spec_Operational_Discipline_v1.md` C-OD-* on audit-ledger composition |
| Action Surface (D2 v1.1 sandbox-violation events) | Sandbox-violation events join on `idempotency_key` per ADR-D2 v1.1 §1.8 fail-class taxonomy | `Spec_Action_Surface_v1.md` C-AS-* on sandbox-violation event shape |
| Operational Discipline (D6 v1.1 cost-attribution-per-span) | `cost.*` per-span attribution joins on `idempotency_key` to avoid double-counting on replay per ADR-D6 v1.1 §1.5 | `Spec_Operational_Discipline_v1.md` C-OD-* on cost-attribution |

### §10.2 Idempotency-key join export

**Export surface.** `idempotency_key` field per C-IS-05; harness-canonical join key per ADD §2.2 Synthesis closing sentence.

**Consuming axes.** All three downstream axes consume `idempotency_key` as the cross-axis join key for replay-safe composition (per ADD §2.2 closing sentence "engine event history (when adopted at D1), audit-ledger signing (D5), and sandbox-violation events (D2) all join on `idempotency_key`").

**F2-12 carry-forward note.** The replay-trace-emission contract (D1 v1.1 → v1.2) is deferred per ADD §6.3.1 + PRD §[carry-forwards] [CF-1]; specifically, the span re-emission semantics under engine replay, `retry.attempt` sibling-span discipline, and trace-ingestion dedup composition with F2 `idempotency_key` remain open until D1 v1.2 + D6 v1.2 land. This carries forward to this spec's §[carry-forwards].

### §10.3 Hash-chain construction discipline export

**Export surface.** Canonicalize → SHA-256 → prior-event-hash chaining per C-IS-06.

**Consuming axes.**

| Consuming axis | Composition reference |
|---|---|
| Operational Discipline (D5 v1.3 audit-ledger) | Audit-ledger uses the F2 hash-chain construction at team-binding+ persona tiers per ADR-D5 v1.3 §1.4 + §1.4.1 |
| Operational Discipline (D5 v1.3 audit signing extension) | Multi-tenant-compliance persona tier extends hash-chain with cryptographic signature (`audit.signature.value` + `audit.signature.algorithm` + `audit.signature.key_id` + `audit.signature.key_period`) per ADR-D5 v1.3 §1.4 |

### §10.4 Filesystem path contract export

**Export surface.** Canonical filesystem path classes per C-IS-01.

**Consuming axes.**

| Consuming axis | Composition reference |
|---|---|
| Action Surface (D3 v1.2 Skills loading discipline) | Skills-as-files load from filesystem per cache-prefix integrity discipline per ADR-D3 v1.2 |
| Control Plane (F1 v1.2 routing manifest residence) | Routing manifest resides at canonical filesystem path per ADR-F1 v1.2 Consequences §(a) |

### §10.5 JSONL event ledger format export

**Export surface.** JSONL with stable indexable per-event shape per C-IS-07 §7.3 composition format.

**Consuming axes.**

| Consuming axis | Composition reference |
|---|---|
| Operational Discipline (D6 v1.1 OTLP collector boundary) | OTLP collector boundary composes against the F2 JSONL event ledger at within-turn streaming + across-turn durable trace storage per ADR-D6 v1.1 §1.7 (T-perm-2 D6-layer commitment per ADD §5.2.2) |

### §10.6 Workload-class-opt-in shadow-Git + worktree-isolation export

**Export surface.** Manifest declaration shapes per C-IS-08 + C-IS-09.

**Consuming axes.**

| Consuming axis | Composition reference |
|---|---|
| Control Plane (D4 v1.1 sub-agent fan-out) | Worktree-isolation composes with D4 sub-agent privilege inheritance + sandbox-tier monotonicity + cross-deployment monotonicity per ADD §5.3.2 sub-agent boundary as monotonic-only descent |
| Control Plane (D5 v1.3 cross-deployment monotonicity) | Shadow-Git checkpoint cadence engages T-perm-3 at the shadow-Git checkpoint cadence vs retry-mechanics seam per ADR-F2 §"Permanent tensions engaged" T-perm-3 touch + ADD §5.2.3 residual surface |

**Deferred to implementation discretion.** Specific cross-spec citation strings (resolved at sessions 2–4 + session 5 composition document); specific seam-versioning convention if F2 ever revises (out of scope at v1).

---

## §[carry-forwards]

This meta-section documents PRD-inherited carry-forward items per `Phase_5_Session_1_Session_Prompt.md` §5.4. Entries are **documentation, not contract-bearing** — they do not engage the §[coherence pass] §6.1 per-contract audit; they engage the spec's operator-visibility surface.

### [CF-1] F2-12 — D1 v1.1 → v1.2 replay-trace-emission contract

**Status.** 🔄 Deferred-acknowledged at ADD v1.2 §6.3.1 (inherited at PRD v1.0 §[carry-forwards] [CF-1]; inherited at this spec); not blocking session 1 entry; not blocking session 1 filing.

**Scope.** D1 v1.1 → v1.2 replay-trace-emission contract covering: (i) span re-emission semantics under engine replay (event-sourced-replay engines: do spans re-emit, or is replay a deterministic re-read without new span emission?); (ii) `retry.attempt` sibling-span discipline (does the retry emit `retry.attempt` event AND a new sibling span per D6 §1.2?); (iii) trace-ingestion dedup composition with F2 `idempotency_key` (cost-attribution-per-span at D6 §1.5 must avoid double-counting on replay).

**Information Substrate spec impact.** The F2 `idempotency_key` export per C-IS-10 §10.2 is the harness-canonical join key; replay-trace-emission semantics that consume this join key are downstream-axis contracts (Control Plane and Operational Discipline). C-IS-10 §10.2 includes the F2-12 carry-forward note in line. **No Information Substrate contract is open** as a function of F2-12 — the F2 substrate surface (entry shape, hash-chain construction, idempotency-key export) is fully closed at v1.0 of this spec.

**Forward routing.** Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path. Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Phase 5 revision-pass at affected spec sections (Control Plane spec + Operational Discipline spec); Information Substrate spec is NOT a revision target for F2-12 closure.

### [CF-2] Workflow §7 substrate-skill propagation

**Status.** Open operator decision; outside P3-CK closure scope; outside PRD scope; outside Phase 5 scope.

**Origin.** `Project_Workflow_Revision_log.md` v1.4 entry line 297 footnote — `add-consolidation-protocol.md` §3.5 Step 5 substrate-skill update to reference Workflow v1.4 §2.3.5 clause (iv) is a separate skill-substrate revision not in v1.4 scope.

**Information Substrate spec impact.** Not in spec scope (skill-substrate revision is neither architectural commitment nor observable behavior nor specification-grade contract). Documented here for operator-visibility per inheritance from PRD §[carry-forwards] [CF-2].

**Forward routing.** Operator decision at discretion. No specification revision is triggered by skill-substrate propagation.

---

## §[traceability]

PRD-requirement-to-spec-contract sub-matrix for the Information Substrate axis. Rows = 4 PRD requirements; columns = 10 spec contracts. `✓` indicates the contract satisfies the requirement (≥1 contract surface implements the requirement's observable behavior).

| PRD requirement | C-IS-01 | C-IS-02 | C-IS-03 | C-IS-04 | C-IS-05 | C-IS-06 | C-IS-07 | C-IS-08 | C-IS-09 | C-IS-10 |
|---|---|---|---|---|---|---|---|---|---|---|
| R-IS-01 — Files-as-artifacts at canonical filesystem paths | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |
| R-IS-02 — Git as combined-tier state record |  |  | ✓ | ✓ |  |  | ✓ |  |  | ✓ |
| R-IS-03 — State-ledger entry shape with hash-chain integrity |  |  |  |  | ✓ | ✓ | ✓ |  |  | ✓ |
| R-IS-04 — Workload-class-opt-in shadow-Git checkpoint and worktree isolation |  |  |  |  |  |  |  | ✓ | ✓ |  |

**Bidirectional verification.**

| Verification rule | Result |
|---|---|
| Every PRD requirement has ≥1 spec contract satisfying it | ✅ — R-IS-01 (3 contracts); R-IS-02 (4 contracts); R-IS-03 (4 contracts); R-IS-04 (2 contracts) |
| Every spec contract has ≥1 PRD requirement it satisfies | ✅ — C-IS-01 (R-IS-01); C-IS-02 (R-IS-01); C-IS-03 (R-IS-02); C-IS-04 (R-IS-02); C-IS-05 (R-IS-03); C-IS-06 (R-IS-03); C-IS-07 (R-IS-02 + R-IS-03); C-IS-08 (R-IS-04); C-IS-09 (R-IS-04); C-IS-10 (R-IS-01 + R-IS-02 + R-IS-03) |
| 4 PRD requirements present (axis-in-scope) | ✅ — R-IS-01, R-IS-02, R-IS-03, R-IS-04 |
| 10 spec contracts present | ✅ — C-IS-01 through C-IS-10 |
| ADR substrate cited at substrate version | ✅ — ADR-F2 v1.2 cited per `Phase_5_Entry_Handoff.md` §5 substrate version |

**Sub-matrix verification: PASS (5/5 rules).**

---

## §[coherence pass]

Pre-emission self-audit per `Phase_5_Session_1_Session_Prompt.md` §6. Five audit dimensions; spec does not file unless all five return ✅ PASS.

### Audit 6.1 — Per-contract audit (10 contracts × 7 sub-dimensions)

| Sub-dimension | Verification posture | Result |
|---|---|---|
| PRD requirement trace | Every spec contract cites ≥1 PRD R-ID; cited requirement is in session-1 axis scope (R-IS-01 through R-IS-04) | ✅ PASS — spot-check: C-IS-01 cites R-IS-01; C-IS-05 cites R-IS-03; C-IS-07 cites R-IS-02 + R-IS-03; C-IS-10 cites R-IS-01 + R-IS-02 + R-IS-03. 10 of 10 contracts carry PRD requirement citations |
| ADR commitment trace | Every spec contract cites ≥1 ADR by ID **and** section (per inversion-discipline analog) | ✅ PASS — spot-check: C-IS-04 cites `ADR-F2 v1.2 §Consequences (a)`; C-IS-05 cites `ADR-F2 v1.2 §Decision + ADD §2.2 Synthesis`; C-IS-06 cites `ADR-F2 v1.2 §Rationale (a.1)`; C-IS-07 cites `ADR-F2 v1.2 §"Permanent tensions engaged" + §Consequences (c) + ADD §5.2.2`. 10 of 10 contracts carry section-level ADR citations |
| No-architecture-introduction | No spec contract adds architectural commitment beyond ADR-F2 v1.2 + ADD v1.2 content; contracts compose committed material into specification-grade precision | ✅ PASS — all 10 contracts derive directly from ADR-F2 §Decision + §Rationale + §Consequences + ADD §2.2 + §5.2.2 + §5.3.3. No contract asserts a substrate property F2 does not commit. Section §[carry-forwards] [CF-1] explicitly notes that the F2 substrate surface is fully closed at v1.0; F2-12 is downstream-axis territory |
| Translate-not-restate | No spec contract restates PRD observable-behavior text or ADR Decision text verbatim; contracts translate via composition | ✅ PASS — every contract section provides specification-grade structure (signatures, schemas, formulas, enums, surface contracts) absent from PRD prose; ADR Decision text is cited by section, not restated. Spot-check: C-IS-06 §6.1 through §6.5 decomposes ADR-F2 §Rationale (a.1) four-step discipline into per-step signatures + per-step contracts (the four-step discipline is asserted at ADR but not signatured) |
| Persona linkage preserved | Every spec contract preserves the persona §X.y anchor from its parent PRD requirement | ✅ PASS — spot-check: C-IS-01 carries Persona §5.1 + §7 + §10.1 inherited from R-IS-01; C-IS-05 carries Persona §10.4 + §10.2 inherited from R-IS-03; C-IS-08 carries Persona §3.1.1 + §8.1 inherited from R-IS-04. 10 of 10 contracts carry persona anchors |
| Contract grade | Every spec contract sits at specification grade (signature / schema / formula / enum / surface contract); no implementation-grade choices beyond what ADRs commit | ✅ PASS — contract surfaces are: C-IS-01 path-class enumeration + stability invariants (schema); C-IS-02 5-tier schema (enum); C-IS-03 4-sub-role schema (enum); C-IS-04 atomicity contract (surface contract); C-IS-05 six-field record signature (schema); C-IS-06 4-step discipline (signatures); C-IS-07 read/write contract pair (surface contract); C-IS-08 manifest declaration shape + cadence enum (schema + enum); C-IS-09 manifest declaration shape + invariants (schema + surface contract); C-IS-10 export surfaces (surface contract). No implementation-grade commitments beyond ADR-declared (specific path strings, library bindings, API surfaces explicitly deferred) |
| Deferred-to-implementation discretion documented | Contracts that defer detail to Phase 6 implementation discretion per Workflow §2.5.1 exit criteria language carry explicit "deferred to implementation discretion" notation | ✅ PASS — 9 of 10 contracts carry explicit "Deferred to implementation discretion" notation (C-IS-10 is a meta-contract referencing other contracts' implementation deferrals); deferrals include: specific canonical path strings (C-IS-01); tier subdivisions (C-IS-02); commit cadence / message conventions (C-IS-03); deploy tagging (C-IS-04); identifier formats (C-IS-05); library bindings (C-IS-06); navigation primitive APIs (C-IS-07); shadow-ref naming + retention (C-IS-08); worktree directory location + reclamation (C-IS-09) |

**Audit 6.1 aggregate: ✅ PASS (7/7 sub-dimensions across all 10 contracts).**

### Audit 6.2 — PRD-requirement-to-spec sub-matrix audit (Information Substrate axis only)

| Sub-dimension | Result |
|---|---|
| Every session-1 PRD requirement has ≥1 spec contract satisfying it | ✅ PASS — R-IS-01 (3 contracts: C-IS-01, C-IS-02, C-IS-10); R-IS-02 (4 contracts: C-IS-03, C-IS-04, C-IS-07, C-IS-10); R-IS-03 (4 contracts: C-IS-05, C-IS-06, C-IS-07, C-IS-10); R-IS-04 (2 contracts: C-IS-08, C-IS-09) |
| Every session-1 spec contract has ≥1 PRD requirement it satisfies | ✅ PASS — no orphan contracts; every C-IS-01 through C-IS-10 cites ≥1 PRD R-ID |
| ADR commitments cited at session-1 spec are at versions matching PRD substrate set | ✅ PASS — ADR-F2 cited at v1.2; matches `Phase_5_Entry_Handoff.md` §5 substrate version table; matches PRD §"ADR substrate set" table |

**Audit 6.2 aggregate: ✅ PASS (3/3 rules).**

### Audit 6.3 — Front-matter audit (session-1 spec)

| Sub-dimension | Result |
|---|---|
| Session-1 axis declared at front-matter | ✅ PASS — Status block records "Axis: Information Substrate"; Front-matter §"Axis declaration" + §"Axis-grounding note" carry rationale per OD-5-2.A handoff recommendation |
| PRD substrate reference | ✅ PASS — `PRD_v1.0.md` §2 cited at Status block Source-set + Front-matter §"PRD requirement scope" |
| ADR substrate reference | ✅ PASS — ADR-F2 v1.2 enumerated at Status block Source-set + Front-matter §"ADR scope" table |
| ADD substrate reference | ✅ PASS — ADD v1.2 §2.2 + §5.2.2 + §5.3.3 + §6.3.1 cited at Status block Source-set; ADD §2.2 Synthesis cited at every contract that derives from F2 substrate |
| Persona substrate reference | ✅ PASS — Persona Document §3.1.1 + §3.1.3 + §5.1 + §7 + §8.1 + §10.1 + §10.2 + §10.4 enumerated at Status block Source-set + Front-matter §"Persona-linkage substrate" table; per-contract persona linkage inherited |
| Status posture | ✅ PASS — `Status: Proposed` per `Project_Workflow_v1_2.md` §3.1 (no clearance until P5-CK per Workflow §2.5.1 OD-5-4.A) |

**Audit 6.3 aggregate: ✅ PASS (6/6 sub-dimensions).**

### Audit 6.4 — §[carry-forwards] inheritance audit

| Sub-dimension | Result |
|---|---|
| F2-12 carry-forward documented at session-1 spec | ✅ PASS — [CF-1] entry inherits PRD v1.0 §[carry-forwards] [CF-1] verbatim; explicit Information Substrate spec impact statement documents that no Information Substrate contract is open as a function of F2-12 (F2 substrate surface fully closed at v1.0); forward routing documented |
| Workflow §7 substrate-skill propagation carry-forward documented | ✅ PASS — [CF-2] entry inherits PRD v1.0 §[carry-forwards] [CF-2] verbatim; explicit Information Substrate spec impact statement documents non-engagement |
| Carry-forward entries labeled as non-contract-bearing | ✅ PASS — meta-section preamble explicitly states "Entries are documentation, not contract-bearing — they do not engage the §[coherence pass] §6.1 per-contract audit" |

**Audit 6.4 aggregate: ✅ PASS (3/3 sub-dimensions).**

### Audit 6.5 — V3 deference audit

| Sub-dimension | Result |
|---|---|
| Confidence-tag schema | ✅ PASS — V3 `[HIGH]` / `[MODERATE]` / `[SPECULATIVE]` schema preserved; tags applied at the two specification surfaces where uncertainty surfaces: C-IS-01 SKILL.md spec cited as [HIGH] (agentskills.io ratified open standard per ADR-F2 §Rationale (a)); C-IS-06 §6.1 canonicalization library binding flagged [MODERATE] per ADR-F2 §Rationale (a.1) (library binding deferred to D-ADR per ADR-F2 §Consequences (c)) |
| Citations resolve at section level | ✅ PASS — every ADR citation verified by reading the ADR section at the indicated location during substrate read (`view` calls on ADR-F2.md, PRD_v1.0.md, Architectural_Design_Document_v1.md, Phase_5_Entry_Handoff.md at session entry); every persona §X.y anchor verifiable at the indicated section (anchors inherited from PRD §[coherence pass] which audited persona anchors at PRD filing) |
| Anti-fabrication discipline applied | ✅ PASS — no fabricated PRD requirements; no fabricated ADR sections; no invented benchmarks / vendor capabilities; substrate retrieved via `view` against ADR-F2.md + PRD_v1.0.md + Architectural_Design_Document_v1.md + Phase_5_Entry_Handoff.md at session execution before emission |
| Workflow v1.4 §2.3.5 clause (iv) analog | ✅ PASS — section-level citation discipline applied at contract granularity (analog to PRD requirement-granularity citation); every contract carries ADR-ID + section pair in its "ADR commitment(s) honored" sub-section |

**Audit 6.5 aggregate: ✅ PASS (4/4 sub-dimensions).**

### Coherence pass aggregate

| Audit dimension | Result |
|---|---|
| 6.1 Per-contract audit | ✅ PASS (7/7) |
| 6.2 PRD-requirement-to-spec sub-matrix audit | ✅ PASS (3/3) |
| 6.3 Front-matter audit | ✅ PASS (6/6) |
| 6.4 §[carry-forwards] inheritance audit | ✅ PASS (3/3) |
| 6.5 V3 deference audit | ✅ PASS (4/4) |

**Coherence pass: ✅ PASS at all five dimensions. Spec authorized for filing.**

---

*Filed 2026-05-13 at Phase 5 session 1 close → Phase 5 session 2 entry boundary. Session 1 scope: Information Substrate axis specification per OD-5-2.A spec-writer judgment (handoff §3.1 recommendation followed); output `Spec_Information_Substrate_v1.md` per OD-5-1.A axis-led decomposition. Phase 5 arc continues to session 2 (Action Surface) per `Phase_5_Entry_Handoff.md` §3.1 axis sequencing; session 2 session prompt filed at `Phase_5_Session_2_Session_Prompt.md`. Aggregate P5-CK at full specification close per Workflow §2.5.1 + OD-5-4.A. Phase 5 session 2 entry-gate AUTHORIZED against this spec + `Spec_Action_Surface_v1.md` axis substrate.*