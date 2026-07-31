# harness-od/CLAUDE.md — Operational Discipline (OD) Axis

*Per-axis subdirectory guidance for the OD axis. Loaded by Claude Code at session startup alongside workspace root `CLAUDE.md`. Canonical pointer to design-phase OD-axis artifacts.*

---

## 1. Axis identity + scope boundary

### 1.1 Axis identity

The Operational Discipline (OD) axis owns **observability + cost + audit + HITL primitive**: HITL invocation primitive (4-response palette canonical schema), audit ledger schema (hash-chain integrity composition), cost attribution 5-step chain (per-attempt + idempotency-key join + hash-chain composition + replay-aware dedup + cause_attribution invariance), validator fail catalog (medium-cardinality cause_attribution + 5-class fail-class taxonomy), 15-namespace OTel observability ingestion map (`anthropic.*` / `mcp.*` / `skill.*` / `managed_agents.*` / `sandbox.*` / `hitl.*` / `topology.*` / `subagent.*` / `engine.*` / `audit.*` / `validator.fail.*` / `files.*` / `memory.*` / `harness.breaker.*` / `provider_discriminator.*`), F3 capability-floor lifecycle event mapping, in-process OTLP collector + sampling discipline.

OD posture per `Cross_Axis_Composition_Document_v2_1.md` §2.1 (baseline) + `Cross_Axis_Composition_Document_v2_18.md` §2.3.7 + §2.4 (v2.4 → v2.18 delta chain; OD→IS bucket 6→4 + OD outbound 28→26 §2.1-conformed at v2.18 per CXA-OD-IS-EDGE-DRIFT closure PR #110): **consumer-most-downstream axis** — 0 outbound cross-axis edges to other axes (preserved invariant); **26 outbound edges per §2.4 axis-attribution at the §2.1-conformed OD-row sum** (4 → IS at CXA v2.18 §2.3.4 per C3-15 — CXA-side/plan-side divergence CLOSED at CXA v2.18; 10 → AS; 12 → CP = 26; the v2.9 attribution-divergence-convention overlay reads 27 with +1 OD-axis-attributed seam at the §2.3.7 CP→OD bucket = row 8 cost-attribution audit-write seam, U-OD-41 producer + U-OD-00 consumer, NEW v2.9 per namespace-ownership convention because `cost.*` is OD-axis-owned); **8 inbound edges from CP at U-OD-00** per CXA v2.17 §2.3.7 (bucket-membership growth: row 1 U-CP-28 audit-ledger entry composition v2.4 + rows 2-7 v2.6 composer-arc absorption [ValidatorFramework + PauseResumeProtocol + PerServerTrustEvaluator + HITL webhook delivery + HITL operator-burden + one prior] + row 8 cost-attribution audit-write seam v2.9; first cross-axis back-edge family — `[[class_3_tension_cxa_v2_4_axis_back_edge]]`). OD terminates the axis-level *downstream* dependency graph (no edges to other axes); the v2.4 → v2.17 bucket growth is acknowledged at U-OD-00 carrier consumption (rows 1-7) + U-OD-41 producer (row 8) and does not alter the 0-outbound-to-other-axes invariant. §2.1-vs-§2.4 attribution divergence at row 8 (counted under CP→OD bucket-membership at §2.1 + §2.3.7 = 8 but attributed to OD outbound at §2.4 = 27) is the natural consequence of the established v2.6 §2.4 namespace-ownership convention preserved through v2.17 per CXA v2.9 §0.3 + §0.7(ii). v2.9 → v2.17 refresh per CXA v2.17 §0.3 absorbing the 6-row CP→IS Pattern-P1 bucket growth at PR #92 commit `28259ed` 2026-05-31; **OD-axis data PRESERVED VERBATIM at v2.17** (outbound 27 / CP→OD 8 rows / 0-outbound-to-other-axes invariant unchanged — v2.17 grew CP→IS bucket only).

### 1.2 Spec + plan authority

| Artifact | Version | Role |
|---|---|---|
| `Spec_Operational_Discipline_v1_36.md` | **v1.36 — canonical HEAD** — 2026-07-30, the OD-owned leg of the RATIFIED **`B-69` durable-pause-state read accessor arc** (council record `.harness/council-b69-pause-state-accessor-2026-07-30.md`; **operator ratified OPTION A′ 2026-07-30**): NEW **§C-OD-30.5** — the observability home for the two events the council ruled REQUIRED, (i) the Runtime C-RT-36 §31 accessor read and (ii) a `resume()` refused on the §30 staleness precondition. **Determination (the council delegated the namespace call to OD, and grounding returned it SPLIT):** both events emit within the **EXISTING** C-OD-30 `pause.*` / `resume.*` family — **NO new top-level namespace, C-OD-05 §5.1 roster UNCHANGED** — but **neither is representable by the existing payload composition unchanged.** The read is a **third event class** (neither a `PauseEvent` nor a `(ResumeAttempt, ResumeOutcome)` pair). The refusal is raised **PRE-BOOTSTRAP**, before any `(ResumeAttempt, ResumeOutcome)` exists, so it composes through neither existing §C-OD-30.4 helper nor the CP→OD converter's `resume:` branch — and `PauseResumeAuditPayload` is `frozen` + `extra="forbid"` with no staleness-token field. **§30.5.2 therefore AUTHORIZES an additive carrier** (an additive field, or a sibling payload type — impl discretion), with the existing field set and BOTH existing helpers **otherwise PRESERVED VERBATIM**. *(An earlier draft claimed "no new payload type and no new converter branch are owed"; out-of-family review round 2 [P1] found both halves false, corrected in place.)* **Load-bearing requirement:** the SAME staleness token is emitted at **BOTH** the successful read and the refusing resume, so a stale-read refusal is reconstructable as **ONE causal pair from telemetry alone**. Content is **split by outcome** — successful read carries the token + **PER-VARIANT location counts** (four counts, one per §31.2 classification; a single total cannot express classification, round 3 [P2]); failed read carries `workflow_id` + the cause attribution and **no token, no count**, but MUST still emit. **NEVER on either:** the locations' payload, or the never-keyable pre-dispatch / depth-0-root identity. **PLAN: no OD plan delta at this leg, and an OD plan delta is OWED AT THE IMPL LEG under EITHER carrier option** (both mutate or extend an OD-owned schema; a Runtime unit cannot own that — round 3 [P1]). Clearance at `.harness/clearance/spec-operational-discipline-v1-36-cleared-2026-07-30.md`. Prior `Spec_Operational_Discipline_v1_35.md` — v1.35 — 2026-07-23, the RATIFIED `B-33` rotation-correlation carrier arc's spec leg (Option A, ratified 2026-07-21): NEW §24.8 (C-OD-24) — a per-correlation-id rotation-pair evidence accessor (`find_rotation_pair_evidence`), sibling to the UNCHANGED §24.7 whole-ledger `verify_rotation_pairs` walk, reusing its crypto/structural checks via an extracted shared helper. Absence of a matching pair (EXACTLY 0 entries — a lone matching entry is NOT absence, it raises `RotationPairIntegrityBreach` as a torn-write/deleted-sibling signal) is explicitly distinguished from `RotationPairIntegrityBreach` (3+ entries, exactly 1 entry, or 2 entries failing the checks) — absence is reported as evidence, never raised as tamper; the evidence DTO also carries `signatures_verified: bool`, always `False` in this delta (no rotation-period-aware cryptographic verifier exists yet) — structural evidence is necessary but not sufficient. CP-owned (NEW §20.3.2 Protocol) + Runtime-owned (NEW §13.6 composition-root inputs) contract text at the same-arc `Spec_Control_Plane_v1_105.md` / Runtime spec v1.105 — cross-referenced, not restated. Clearance at `.harness/clearance/spec-operational-discipline-v1-35-cleared-2026-07-23.md`. Prior `Spec_Operational_Discipline_v1_34.md` — v1.34 — 2026-07-18, the RATIFIED `B-51`/`B-52`/`B-54` OD audit-signing amendment arc (all ten fork gate items ratified AS RECOMMENDED; three all-CONFIRM council dyads at the apply leg): AMENDED §21.2.1 — FIFTH canonical-message segment carrying the writer-normalized tenant tag (OD-homed normalizer, drop-when-`None` byte-compat), tenant-bearing `sign_audit_entry`, MTC tenant bootstrap invariant with the `migrate-audit-sidecar` retag upgrade story, `sign_rotation_pair` PROHIBITED at MTC until `B-33`; NEW §21.2.2 — backend-aware signature verification API (per-row resolver, message-format cutover, authenticated content-bound exemption triples, typed taxonomy `AuditSignatureInvalid` ≠ `HashChainBreach`, non-blocking default, UNVERIFIED-nonzero at MTC); NEW §21.2.3 — `audit_signing_fail_closed` policy (per-persona defaults, explicit-`false`-INVALID-at-MTC, single typed boundary, zeroth-site backend-required invariant, redaction path unconditionally fail-closed with mandatory typed propagation, post-effect result-preserving bypass). Clearance at `.harness/clearance/spec-operational-discipline-v1-34-cleared-2026-07-18.md`. Prior delta v1.33 — 2026-07-16, post-Phase-8 forward-register arc `B-47` (PR A): NEW C-OD-21 §21.2.1 `SigningBackend` composition-root injection seam — OPTIONAL `backend` keyword on the U-OD-30 `sign_audit_entry` (mirror of the cleared C-CP-20 §20.2.1/`B-22` seam; absent → placeholder attrs PRESERVED VERBATIM, zero caller regression; present → real signature over a metadata-bound canonical message, base64 value, per-algorithm length enforcement per C-CP-20 §20.4 widths); clearance at `.harness/clearance/spec-operational-discipline-v1-33-cleared-2026-07-16.md`. Prior delta v1.32 — 2026-07-13, R-FS-2 Wave 4 `B-19-BREAKER-AMBIENT-ATTRS`: C-OD-07 §7.1 ADDITIVE amendment, re-introduces `harness.breaker.cause` + `harness.breaker.cooldown_ms` (CP v1.1's dropped ambient 4-attribute set, re-landed as event attributes; 7→9 attributes). `cause` was a vacuous-by-honest-design slot at v1.32's authoring; the follow-on classifier landed at `B-38` (PR #1020) and it now populates `rate_limit`/`auth_failure`/`5xx_streak` at all three real `record_failure()` sites (`capability_shortfall` remains a forward slot) — v1.32 §7.1 corrected in-place 2026-07-18 per `B-43`; `cooldown_ms` is real and always populated at a trip. Prior delta v1.31 (2026-07-12 pointer catch-up, R-600 cadence-5 adjacent finding): ports `audit.rotation_correlation_id` into the existing `audit_namespace_attrs` open-dict convention (new §24.7, mirroring the §24.6 `audit.cp.*` precedent) for the two-row dual-signature audit-key rotation runtime path (B-AUDIT-KEY-ROTATION-RUNTIME, PR #938); zero Pydantic schema change. v1.30 chain below preserved verbatim as historical (delta-only chain; this row's prior `v1.4` was the Phase-6.5 authoring-era pin, pre-dating the Phase-7 v1.5→v1.30 deltas — latest delta = R-FS-1 `B-COST-DISCRIMINATOR-TAXONOMY` C-OD-15 §15.1 ADDITIVE `PER_DISPATCH_KIND` rollup axis + `DispatchKind` vocabulary + `provider_discriminator` per-dispatch-optional correction; prior delta v1.29 = R-PM-1 cascade PR #4 NEW C-OD-34 per-persona-tier prompt-governance posture. Per delta-only convention each version is canonical-at-authoring for its scope; the chain head is the current contract authority) | Contract authority — 34 contracts C-OD-01 through C-OD-34 *(C-OD-25..33 added at v1.8; C-OD-34 added at v1.29; C-OD-15 §15.1 4th rollup axis added at v1.30; C-OD-07 §7.1 amended at v1.32 — see the canonical spec for the full enumeration)* |
| `Implementation_Plan_Operational_Discipline_v2_30.md` | **v2.30 — canonical HEAD** (2026-07-23 B-33 spec+plan leg — NEW U-OD-56, absorbing OD spec v1.35 §24.8 AND retroactively backfilling the already-landed §24.7 `sign_rotation_pair`/`verify_rotation_pairs` (PR #938), which had zero prior `U-OD-NN` coverage; clearance `implementation-plan-operational-discipline-v2-30-cleared-2026-07-23.md`). Prior `Implementation_Plan_Operational_Discipline_v2_29.md` — v2.29 — (delta-only chain; 2026-07-18 B-51/B-52/B-54 arc plan delta — U-OD-30 amended for OD v1.34 §21.2.1/§21.2.3 + NEW U-OD-55 for the §21.2.2 verification API; clearance at `.harness/clearance/implementation-plan-operational-discipline-v2-29-cleared-2026-07-18.md`; prior delta v2.28 = the U-OD-21 §15.1 reconciliation) | Execution authority — 35 atomic units across 8 clusters (+ U-OD-00 pre-cluster) and 10 topological levels (L0–L9) *(authoring-era figures; see the canonical plan)* |

### 1.3 Scope inclusion

| Surface | Carrier units | Spec contract |
|---|---|---|
| Foundational cost-attribution + telemetry primitives | U-OD-01, U-OD-04 (L0 anchors) | C-OD-01 + C-OD-04 |
| HITL primitive — 4-response palette (4 canonical event names: `hitl.gate.evaluated` / `hitl.invocation.opened` / `hitl.invocation.responded` / `hitl.invocation.timed_out`) | U-OD-NN (Cluster 1) | C-OD-05 row 6 |
| 15-namespace ingestion map | U-OD-NN (Cluster 2–3) | C-OD-05 §5.1 |
| F3 capability-floor lifecycle event mapping (`workflow.start` / `step.boundary` / `fallback.triggered` / `retry.attempt` / `breaker.tripped` / `lease.acquired` / `lease.released` / `workflow.resumed` — the eight event classes per spec C-OD-06 §6.1, canonical; pinned at OD plan v2.8 §0.5) | U-OD-08 (Cluster 2) | C-OD-06 §6.1 |
| 7-attribute `harness.breaker.*` canonical schema | U-OD-NN (Cluster 3) | C-OD-07 §7.1 |
| Cost attribution 5-step chain | U-OD-14 through U-OD-17 | C-OD-12 + C-OD-13 |
| Audit-ledger schema + 8-field SHA-256 composition + field-ordering | U-OD-20 | C-OD-14 §14.5.1 |
| 8-row audit-ledger enumeration | U-OD-20 | C-OD-14 §14.5.2 |
| Validator fail catalog (cause_attribution) | U-OD-NN (Cluster 6) | C-OD-NN |
| In-process OTLP collector + sampling discipline | U-OD-NN (Cluster 7) | C-OD-NN |
| OD substrate seam exports manifest (terminal aggregate exporter) | U-OD-34 | C-OD-23 |

### 1.4 Scope exclusion

| NOT OD | Owning axis / source |
|---|---|
| Path-class registry, state ledger, hash-chain *implementation* (canonical at IS), JSONL composition | IS — `harness-is/CLAUDE.md`. OD consumes IS hash-chain primitives via U-IS-08/09/10 cross-axis edges |
| SandboxTier enum, tool contract schemas, sandbox observability emission (canonical at AS) | AS — `harness-as/CLAUDE.md`. OD ingests `sandbox.*` namespace per D6 §1.2 |
| Multi-LLM routing, retry mechanism implementation, fallback chain composition, workflow lifecycle, topology pattern, HITL placement decision logic, sub-agent handoff schemas | CP — `harness-cp/CLAUDE.md`. OD ingests CP-emitted namespaces (`routing.*` / `fallback.*` / `retry.*` / `engine.*` / `topology.*` / `subagent.*` / `hitl.*` / `harness.breaker.*`) |

**D6 ingestion pattern.** OD canonical authority for: (a) namespace map (C-OD-05 15-row enumeration); (b) lifecycle event mapping (C-OD-06); (c) `harness.breaker.*` 7-attribute schema (C-OD-07 §7.1); (d) cost attribution chain (C-OD-12 + C-OD-13). CP/AS emit per OD's canonical attribute set. Composition site at OD spec; emission site at CP/AS plans.

---

## 2. Per-axis canonical artifacts

### 2.1 Anchoring ADRs

| ADR | Version | Role |
|---|---|---|
| ADR-D1 | v1.2 | Engine + replay (replay-trace-emission contract; F2-12 closure) |
| ADR-D4 | v1.1 | Workload classes (per-workload sampling discipline) |
| ADR-D5 | v1.3 | HITL palette canonical (4-event-name set per §1.8) + cross-deployment monotonicity |
| ADR-D6 | v1.2 | Observability + cost-attribution (12-namespace span schema; canonical) |
| ADR-F2 | v1.2 | State ledger substrate (hash-chain integrity composition consumed at audit) |
| ADR-F3 | v1.1 | Engine event history (lifecycle event categorization) |

ADD attestation: `Architectural_Design_Document_v1_3.md` v1.3.

### 2.2 Cross-axis edge inventory (CXA v2.1 baseline + v2.4 → v2.17 CP→OD bucket growth)

OD is consumer-most-downstream. Pre-v2.4: all OD-direction cross-axis edges were **outbound consumer edges**. At v2.4 (per U-RT-59 Fork 2 Path D landing), the §2.3.7 CP→OD bucket opened with its first row (U-CP-28 → U-OD-00). At v2.6 (composer-arc absorption), rows 2-7 added (6 new typed seams sharing the `cp_audit_to_od_audit` converter via distinct F2 action_id prefixes). At v2.9 (cost-attribution audit-write seam landing per `.harness/Remaining_Work_Closure_Arc_Handoff_v1.md` §6), row 8 added (U-OD-41 producer + `cost:` action_id prefix discriminator). At v2.17 (CP→IS Pattern-P1 6-row absorption per `.harness/overnight_run_2026-05-31_scope_and_discipline.md`), the CP→OD bucket is **PRESERVED VERBATIM** at 8 rows (v2.17 grew CP→IS bucket only — OD-axis data unchanged). The 0-outbound-to-other-axes invariant is preserved across the v2.4 → v2.17 growth; row 8 is OD-axis-attributed at §2.4 per namespace-ownership convention but its endpoints are still both OD-internal (U-OD-41 → U-OD-00 routed through the shared CXA converter):

| Edge direction | Edges | Source artifact |
|---|---|---|
| OD → IS (outbound consumer) | 4 (CXA v2.18 §2.3.4 per C3-15 Path (i-refined); was 6 at CXA v2.1 baseline — CXA-side/plan-side divergence CLOSED at CXA v2.18 per CXA-OD-IS-EDGE-DRIFT, PR #110) | `Cross_Axis_Composition_Document_v2_18.md` §2.3.4 (was cited §2.3.5 at v2.1 numbering — §2.3.5 is OD→AS; corrected per CXA v2.18 §0); `Implementation_Plan_Operational_Discipline_v2_6.md` §0.7 + §4.5.1 |
| OD → AS (outbound consumer) | 10 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.6 |
| OD → CP (outbound consumer) | 12 | `Cross_Axis_Composition_Document_v2_1.md` §2.3.3 |
| **CP → OD (bucket-membership)** | **8** | `Cross_Axis_Composition_Document_v2_9.md` §2.3.7 — 8 genuine-typed-seams at the shared `cp_audit_to_od_audit` converter (homed at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`). Row 1 (U-CP-28 → U-OD-00 audit-ledger entry composition, NEW v2.4) + rows 2-7 (composer-arc absorption: ValidatorFramework + PauseResumeProtocol + PerServerTrustEvaluator + HITL webhook delivery + HITL operator-burden + one prior, NEW v2.6) + row 8 (U-OD-41 → U-OD-00 cost-attribution audit-write seam via `cost:` action_id prefix, NEW v2.9; cite forward to OD spec v1.10 §C-OD-26.6 CostRecordAuditPayload). §2.4 axis-attribution: rows 1-7 CP-axis-attributed (CP outbound 62); row 8 OD-axis-attributed (OD outbound 27 per namespace-ownership convention because `cost.*` is OD-owned). Per-row F2 action_id prefix discriminator at OD audit-trace consumers per CXA v2.9 §0.3 (`dispatch:` / `hitl:` / `hitl_webhook:` / `operator_burden:` / `validator:` / `pause:` / `resume:` / `mcp_trust:` / `cost:`). `[[class_3_tension_cxa_v2_4_axis_back_edge]]` |
| **OD-axis-attributed share of CP→OD bucket** | **1 (row 8)** | Per §2.4 namespace-ownership convention preserved at v2.9 §0.3 + §0.7(ii); row 8 counts toward OD outbound = 27 (was 26 at v2.6); rows 1-7 count toward CP outbound = 62. §2.1-vs-§2.4 attribution divergence at row 8 is the natural consequence of the established convention, not a new exception. |
| **OD outbound to other axes (downstream)** | **0** | OD terminates the axis-level *downstream* dependency graph (invariant preserved at v2.4 → v2.9; all 8 CP→OD bucket rows are within OD endpoints — U-OD-00 or U-OD-41 — so no actual edge to another axis). |

CXA-OD-IS-EDGE-DRIFT Class 3 informational item: CXA v2.1 §2.3.5 enumerates 6 edges (baseline at OD plan v2.3); OD plan v2.6 §4.5.1 enumerates 4 (rows 2 + 3 deleted as OD-internal mis-routed; rows 4 + 5 remapped to canonical IS contracts). Routing: future composition-document revision pass; non-blocking.

### 2.3 OD-internal cross-cluster dependencies (NOT cross-axis)

Per `Implementation_Plan_Operational_Discipline_v2_6.md` §0.7 + §0.9: sqlite substrate residence + ring-buffer eviction are OD-internal concerns (NOT cross-axis edges). C3-15 closure formalized this distinction via Path (i-refined) deletions at v2.6 §4.5.1. OD-internal cross-cluster compositions are within-axis dependencies; cross-axis enumeration at §4.5 covers cross-axis only.

---

## 3. Topological entry-points (Level 0)

Per the canonical OD plan plan-level invariants (head `Implementation_Plan_Operational_Discipline_v2_27.md`; the `_v1.md` §0.2 origin was superseded by the delta-only v2.x chain — invariants summarized inline below):

| L0 unit | Scope | Cluster |
|---|---|---|
| U-OD-00 | OD-local audit-ledger composition-type carrier (added at OD plan v2.6 per revision pass R5) | pre-cluster |
| U-OD-01 | Foundational cost-attribution primitive | 1 |
| U-OD-04 | Foundational telemetry primitive | 1 |

**3 L0 units; in-degree 0.** Phase 7 sub-phase 7b OD-axis-stream execution begins from these entry-points.

### 3.1 OD plan-level invariants (preserved at v2.6)

| Invariant | Value |
|---|---|
| Atomic units | 35 (U-OD-00, U-OD-01 through U-OD-34) — U-OD-00 added at v2.6 per R5 |
| Clusters | 8 (+ U-OD-00 pre-cluster) |
| Spec contracts covered | 23 of 23 (C-OD-01 through C-OD-23) |
| PRD requirements satisfied | 8 of 8 (R-OD-01 through R-OD-08) plus cross-axis surface |
| Within-axis directed edges | 102 (v2.6: +2 M-2 hidden-coupling edges) |
| Cross-axis directed edges | 26 (IS=4; AS=10; CP=12) per OD plan v2.6 §4.5.1 |
| Cross-axis-touching units | 16 of 35 |
| Foundational anchors (L0) | 3 (U-OD-00, U-OD-01, U-OD-04) |
| Terminal units (L9) | 2 (U-OD-31, U-OD-34) |
| Level depth | 10 (L0–L9) |
| F2-12 ACTIVE contract-bearing sites | 1 (U-OD-20) — CLOSED at v2.2 cascade |
| F2-12 carry-forward inheritance sites | 1 (U-OD-34) — CLOSED at v2.2 cascade |

### 3.2 Coverage matrix verification

Per OD plan §4 (preserved at v2.6): 23 of 23 contracts covered by ≥1 unit; no coverage gaps. Coverage matrix per-axis-only per OD-S4-2.A.

---

## 4. Substitution + anti-leakage surface

### 4.1 OD-axis substitutions (8 entries)

Per `Phase_7_Meta_Architecture_v1.md` §5.5. H_E classification per §4.4.4 — **OD is the most-absent axis**:

| H_T primitive class | Count | Representative primitives |
|---|---|---|
| ✗ absent | 7 | H_T-OD-1 (deferral envelope — `ToolSearch` ≠ deferral envelope, categorical mismatch); H_T-OD-2 (OTel SDK injection — H_E telemetry closed); H_T-OD-3 (sampling-discipline surface); H_T-OD-4 (SpanProcessor injection); H_T-OD-6 (in-process OTLP collector); H_T-OD-7 (preservation discipline); H_T-OD-8 (authoring artifact) |
| ~ partial | 1 | H_T-OD-5 (`/cost` + `--max-budget-usd` coarse; not 5-step chain) |
| ✓ native | 0 | None |

**OD is the most distinct H_E ↔ H_T boundary.** All OD substitutions retire at OD-axis unit landings; no native H_E carrier covers any OD primitive in full. The substrate-boundary discipline (X-AL-1: H_E ↔ H_T boundary at MCP server process) is canonical at OD axis per OD-AL-3.

Full per-substitution bounded-scope + retirement criterion at Meta-Architecture §5.5.

> **🎓 PHASE-8 GRADUATION + post-Phase-8 back-flow (2026-06-02 → 2026-06-07).** Substitution accounting is CLOSED at `.harness/phase-8-graduation.md` (the Phase-8-close snapshot was 46/54 RETIRED + 49/54 pipeline-advanced); the **live** RETIRED + pipeline-advanced counts and every per-substitution disposition are **DERIVED from `.harness/substitutions.yaml` via `tools/substitution_ledger.py`** (the blocking CI tally gate) per **R-600 — cite the derivation, never hand-maintain inline** (the post-Phase-8 back-flow after R-810/R-820 + OD-4/CXA-4 + CXA-3 moved the tally past the 46 snapshot). **OD-axis current state (derived 2026-06-08): all 8 H_T-OD primitives retired** — OD-1/7/8 `AUTHORING_ONLY`; OD-2/3/4/5 `SUBSTANTIVE_RETIRED` (OD-4 back-flowed to counted retirement at **batch-53 / R-008** once the opaque-token + audit-backed-tokenization runtime residual closed 2026-06-07 — no longer the `RETIRED-AS-CROSS-AXIS-DEFERRED` / PARTIAL state the prior inline ledger showed); OD-6 `BOUNDED_RESIDUAL` (R-009; `flush_to_sqlite` dormant at MVP, gated on R-420/R-421); pipeline-advanced 8/8. Per-batch forward-only narrative (span-emission landings, gate transits, sub-species-10 doc-hygiene audits) is preserved verbatim at `.harness/phase-7d-retirement-events-batch-{1..53}.md`.

*(Per-substitution disposition table + span-emission activity + per-batch gate transits relocated 2026-06-08 (optimize-claude-md G-5) to their canonical homes — `.harness/substitutions.yaml` (derived dispositions/counts via `tools/substitution_ledger.py`) + `.harness/phase-7d-retirement-events-batch-{1..53}.md` (forward-only per-batch narrative) — per R-600 derive-don't-hand-maintain. Current OD-axis state is summarized in the graduation note above.)*

### 4.2 OD-axis anti-leakage rules (3 entries)

Per `Phase_7_Meta_Architecture_v1.md` §7.5:

| Rule | Statement | Anti-pattern foreclosed |
|---|---|---|
| OD-AL-1 | H_E telemetry (internal Claude Code analytics, closed surface) ≠ harness observability substrate (instruments the harness for harness operators) | Assuming H_E telemetry covers H_T's `sandbox.*` / `mcp.*` / `skill.*` / `topology.*` / `subagent.*` / `engine.*` / `audit.*` / `validator.fail.*` / `harness.breaker.*` namespace emission |
| OD-AL-2 | H_E `/cost` (session-grain coarse cost) ≠ H_T cost-attribution 5-step chain (per-attempt + idempotency-key join + hash-chain integrity composition + replay-aware dedup + cause_attribution invariance) | Authoring U-OD-17 → U-OD-22 to delegate cost computation to `/cost`-derived data |
| OD-AL-3 | All OTel emission during 7a happens at MCP server boundary (H_T-authored code). H_E does not participate in OTel emission. Boundary is load-bearing — prevents H_E internal telemetry from contaminating H_T trace schemas | Attempting to inject OTel SpanProcessors into H_E's emission path; constructing H_T spans by parsing H_E session logs |

Cross-cutting rules X-AL-1 / X-AL-2 / X-AL-3 (Meta-Architecture §7.7) also bind OD-axis implementation. **OD-AL-3 is the canonical concretization of X-AL-1** — substrate-boundary at MCP server process is enforced at OD via "no H_E participation in OTel emission" rather than convention.

---

## 5. Back-flow channels

Axis-specific design defects route per `Project_Workflow_v1_8.md` §2.7.6 + workspace root `CLAUDE.md` §4.3.

### 5.1 Class 1 routing by defect locus

| Defect locus | Class 1 routing |
|---|---|
| OD plan v2.6 atomic unit signature defect | Phase 6 plan revision-pass at design-phase workspace |
| OD spec v1.3 contract defect (C-OD-NN under-specifies the surface; spec inconsistent with ADR) | Phase 5 spec revision-pass at design-phase workspace |
| ADR-D1 v1.2 / D4 v1.1 / D5 v1.3 / D6 v1.2 / F2 v1.2 / F3 v1.1 anchor decision defect | Phase 3a/3b ADR revision via council convening |
| ADD v1.3 attestation mismatch with OD spec v1.3 | Phase 3d ADD revision |
| CXA v2.1 §2.3.3 (OD→CP) / §2.3.5 (OD→IS) / §2.3.6 (OD→AS) edge defect | Phase 6 CXA revision-pass at design-phase workspace |
| OD substrate seam (U-OD-34 manifest) defect; cascade to consumer-side plans (none — OD is consumer-most-downstream) | Phase 6 OD plan revision-pass |

### 5.2 Open carry-forwards at OD axis entry

| Carry-forward | Status | Routing |
|---|---|---|
| F2-12 cascade Step 6b (OD plan layer) | CLOSED at v2.2; preserved through v2.6 per `F2-12_Closure_Declaration.md` | No action |
| F3-02 IS-axis revision (U-OD-20 acceptance #11 `Depends on` placeholder `U-IS-NN` → canonical `U-IS-12`) | CLOSED at v2.4 §0.7 (Form A — citation precision); preserved at v2.6 | No action |
| C3-15 Path (i-refined) deletions at §4.5.1 (OD-internal mis-routed cross-axis edges) | CLOSED at v2.4 §0.7; preserved at v2.6 | No action |
| CXA-OD-IS-EDGE-DRIFT (Class 3 informational) | CXA v2.1 §2.3.5 enumerates 6 edges; OD plan v2.6 §4.5.1 enumerates 4 | Non-blocking; future composition-document revision pass |
| OD-INTERNAL-FORMALIZATION (Class 3 informational) | OD plan lacks explicit "OD-internal cross-cluster dependency" section that canonicalizes sqlite substrate + ring-buffer eviction as within-axis (non-cross-axis) compositions | Non-blocking; future OD plan revision pass (formalization deferred) |

### 5.3 Filing footer

| Field | Value |
|---|---|
| Artifact | `harness-od/CLAUDE.md` |
| Authored at | Phase 6.5 Session 6 (ε), 2026-05-15 |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.2 |
| Predecessor | Design-phase workspace OD spec v1.3 + OD plan v2.6 |
| Revision policy | This file is canonical for the `harness-od/` subdirectory; revisions route to design-phase back-flow per §5.1 |

---

*End of `harness-od/CLAUDE.md`. Parent guidance at workspace root `CLAUDE.md`. OD spec + plan + CXA v2.1 §2.3.3 / §2.3.5 / §2.3.6 at design-phase workspace.*
