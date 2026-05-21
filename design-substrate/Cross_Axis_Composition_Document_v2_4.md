# Cross-Axis Composition Document (v2.4)

*Delta over v2.3. v2.4 lands the operator-ratified **U-RT-59 Fork 2 Path D** chunk: one new genuine-typed-seam edge (CP→OD) carrying the `cp_audit_to_od_audit` converter contract. Only the sections enumerated in §0.2 are revised; every other section is preserved verbatim from `Cross_Axis_Composition_Document_v2_3.md`.*

## §0 Change note (v2.3 → v2.4)

### §0.1 Revision context — Fork 2 Path D landing

Per operator ratification 2026-05-20 at `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10 (Path D — reduced-scope landing). Fork 2 surfaced a pre-existing X-AL-3 drift between code (`harness-od/src/harness_od/audit_ledger_types.py`) and ADR-D5 §1.4 in the OD-side audit-ledger payload shape; full broader-scope resolution (Path B-revised-a/b OR Path A-revised) deferred to a dedicated drift-resolution arc. v2.4 lands ONLY the surfaces that are spec-anchored at HEAD:

- The CP-side `cp_audit_to_od_audit` converter contract (CP spec v1.6 → v1.7 §13.5.1 — co-published with this v2.4 amendment).
- The CXA enumeration of the new CP→OD genuine-typed-seam edge (this v2.4 amendment).

OD-side amendments (recognize CP-sourced audit entries; canonicalize `entry_hash`; resolve `AuditPayload` shape vs ADR-D5 §1.4 deviation) remain deferred. The new edge declared at v2.4 is **contract-anchored** at the CP side; its runtime materialization is gated on the OD-side drift resolution arc.

### §0.2 Sections revised

§0 (this change note); §2.1 (matrix — CP→OD 0 → 1; aggregate 92 → 93; genuine 22 → 23); §2.3.7 (NEW — CP→OD bucket, 1 canonical edge); §2.4 (posture summary — CP outbound 55 → 56, genuine 14 → 15; aggregate genuine 22 → 23). All other sections preserved verbatim from v2.3.

### §0.3 Precedent — typed seam whose import lives at `harness-cxa/`

The new edge U-CP-28 → U-OD-00 is the **first CXA-enumerated edge whose typed import physically resides at `harness-cxa/`** rather than at the consumer-axis package. Per the Fork 2 Q5 ratification, the converter is homed at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` (not `harness-cp/` and not `harness-od/`) because:

- `harness-od/` is foreclosed by OD's "0 outbound cross-axis edges" invariant (`harness-od/CLAUDE.md` §2.2).
- `harness-cp/` would require a new CP→OD outbound edge at the package-import level (`harness-cp/CLAUDE.md` §2.3 invariant change).
- `harness-cxa/` is the designed home for cross-axis composition seams per workspace `CLAUDE.md` §2.5.

**Classification.** Per §0.3 taxonomy at v2.3 the edge is **G** (genuine-typed-seam) — the contract at CP spec v1.7 §13.5.1 names OD `AuditLedgerEntry` as the converter's output type. The physical import (`from harness_od.audit_ledger_types import AuditLedgerEntry`) lives at the `harness-cxa/` converter module per the home decision. Sets the precedent: future cross-axis-composition-seam converters homed at `harness-cxa/` are still G when the contract references a typed cross-axis output.

### §0.4 Aggregate reclassification matrix (v2.4 delta)

Snapshot 3 — post-v2.4 (added one G edge in CP→OD bucket):

| Bucket | v2.3 canonical | v2.4 canonical | v2.3 genuine | v2.4 genuine | v2.3 convention | v2.4 convention | v2.3 phase-2-runtime | v2.4 phase-2-runtime |
|---|---|---|---|---|---|---|---|---|
| AS → IS (§2.3.1) | 11 | 11 | 7 | 7 | 3 | 3 | 1 | 1 |
| CP → IS (§2.3.2) | 37 | 37 | 9 | 9 | 11 | 11 | 17 | 17 |
| CP → AS (§2.3.3) | 18 | 18 | 5 | 5 | 13 | 13 | 0 | 0 |
| OD → IS (§2.3.4) | 4 | 4 | 0 | 0 | 2 | 2 | 2 | 2 |
| OD → AS (§2.3.5) | 10 | 10 | 1 | 1 | 8 | 8 | 1 | 1 |
| OD → CP (§2.3.6) | 12 | 12 | 0 | 0 | 9 | 9 | 3 | 3 |
| **CP → OD (§2.3.7) — NEW v2.4** | 0 | **1** | 0 | **1** | 0 | 0 | 0 | 0 |
| **Total** | **92** | **93** | **22** | **23** | **46** | **46** | **24** | **24** |

23 + 46 + 24 = 93. The v2.3 axis-level acyclicity statement (IS < AS < CP < OD) becomes **no longer total**: the new CP→OD edge is the first cross-axis dependency in the direction opposite to the prior partial order. This is acknowledged at §2.2 (the §2.2 axis-level dependency graph is preserved from v2.3 with the v2.4 edge label added as a back-edge); per-unit acyclicity within CP and within OD is unaffected.

### §0.5 Authoring discipline

Scope: ONE new edge added per Fork 2 Path D ratification — no other reclassification; no other edge added or removed; no other section content changed. The Path D scope explicitly excludes OD-side amendments pending the drift resolution arc. Spurious strikes from v2.3 preserved. Producer-attribution corrections from v2.3 preserved. Per-edge evidence at the converter contract (CP spec v1.7 §13.5.1) + the discovery report.

---

## §2 Cross-axis adjacency matrix — REVISED

### §2.1 Aggregate 4×4 adjacency matrix — REVISED (CP→OD bucket grown 0 → 1)

Total cross-axis relationships per bucket (spurious struck):

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | 11 | *(self)* | 0 | 0 |
| **CP** | 37 | 18 | *(self)* | **1 (v2.4)** |
| **OD** | 4 | 10 | 12 | *(self)* |

**93 canonical cross-axis relationships** (92 at v2.3 + 1 new CP→OD genuine-typed-seam edge at v2.4). Genuine typed seams within that: **23** (22 at v2.3 + 1). Convention-level: **46** (unchanged from v2.3). Phase-2-runtime: **24** (unchanged from v2.3). 23 + 46 + 24 = 93.

### §2.2 Axis-level dependency graph — REVISED (v2.4 back-edge added)

The §2.2 ASCII graph is preserved from v2.3 with the v2.4 back-edge added: **CP → OD (1)**. Axis-level partial-order acyclicity (IS < AS < CP < OD per v2.2/v2.3) no longer holds; the new CP→OD edge introduces a back-direction dependency at axis granularity. Per-unit acyclicity within each axis is preserved; per-axis Kahn ordering within CP and within OD unaffected.

### §2.3 Per-bucket edge enumeration — REVISED (new §2.3.7 added; §2.3.1–§2.3.6 preserved verbatim from v2.3)

§2.3.1 (AS→IS) — preserved verbatim from v2.3.
§2.3.2 (CP→IS) — preserved verbatim from v2.3.
§2.3.3 (CP→AS) — preserved verbatim from v2.3.
§2.3.4 (OD→IS) — preserved verbatim from v2.3.
§2.3.5 (OD→AS) — preserved verbatim from v2.3.
§2.3.6 (OD→CP) — preserved verbatim from v2.3.

#### §2.3.7 CP → OD (1 canonical) — NEW v2.4 — evidence: `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md`

| Consumer | Producer | Contract | Class |
|---|---|---|---|
| U-CP-28 | U-OD-00 | C-CP-13 §13.5.1 (v1.7) | **G** — `AuditLedgerEntry` as converter output type at the CP-spec-anchored `cp_audit_to_od_audit` contract. Physical import at `harness-cxa/src/harness_cxa/cp_audit_conversion.py` per Q5 ratification (precedent — §0.3). |

*Edge note.* The CP-side contract (CP spec v1.7 §13.5.1) commits the CP-side semantics + field projection table + `audit.cp.*` namespace prefix + `prior_entry_hash ≡ CP prior_event_hash` equivalence + caller-supplied `entry_core` source semantic. The runtime materialization (un-strike U-RT-59 AC #9 write half + composer step 8 F2-write + audit-write composition at the dispatch composer) is owed to the runtime spec arc and gated on the OD-side audit-ledger drift resolution arc per discovery report §10.

### §2.4 Per-axis outbound posture summary — REVISED (CP outbound 55 → 56; genuine 14 → 15; aggregate genuine 22 → 23)

| Axis | Canonical outbound relationships | Genuine typed seams | Posture |
|---|---|---|---|
| IS | 0 | 0 | Pure foundational substrate |
| AS | 11 | 7 | Consumes IS; the 4 non-genuine are scheme-inheritance / descriptors / 1 runtime |
| CP | **56 (v2.4: +1 CP→OD)** | **15 (v2.4: +1 CP→OD)** | Largest consumer; new v2.4 CP→OD edge is the first CP-outbound edge to OD (back-direction) |
| OD | 26 | 1 | Consumer-most axis; built almost entirely as Pattern-P1 convention surfaces by design |
| **Aggregate** | **93** | **23** | — |

### §0.11 Promotion candidates (operator decision — NOT applied at v2.3, preserved at v2.4)

Two convention-level edges (preserved from v2.3) — non-Fork-2 surface, unchanged at v2.4:
- U-OD-26 → U-CP-47 (§2.3.6): could import `harness_cp...ValidatorFailClass`.
- U-OD-29 → U-AS-15 §12.4 arm (§2.3.5): could import `harness_as.cross_deployment_monotonicity`.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_4.md` |
| Status | Canonical — Phase 7 sub-phase 7b/7c, U-RT-59 Fork 2 Path D landing |
| Predecessor | `Cross_Axis_Composition_Document_v2_3.md` (preserved verbatim except §0, §2.1, §2.3.7-NEW, §2.4) |
| Authored at | Phase 7 sub-phase 7b/7c, 2026-05-20 (in-CLI) |
| Co-published with | `Spec_Control_Plane_v1_7.md` v1.7 §13.5.1 (`cp_audit_to_od_audit` converter contract) |
| Evidence base | `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` (§§1–10); `.harness/class_1_tension_u_rt_59_cp_to_od_audit_write_gap.md` |
| Net effect | 92 → 93 canonical cross-axis relationships (+1 G); 22 → 23 genuine typed seams (+1); 46 convention-level + 24 phase-2-runtime unchanged. New bucket CP→OD = 1 G. |
| Deferred | OD-side audit-ledger drift resolution arc per discovery report §10 (Path B-revised-a / Path B-revised-b / Path A-revised — operator decision pending); runtime spec v1.7 §14.7.6 amendment (un-strike U-RT-59 AC #9 write half); CP plan + OD plan absorption |
| Next gate | (a) operator selects drift resolution path; (b) implementation arc opens to wire the converter at sub-agent dispatch composer step 8 |
