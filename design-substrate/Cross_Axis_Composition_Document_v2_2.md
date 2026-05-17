# Cross-Axis Composition Document (v2.2)

*Delta over v2.1. Only the sections enumerated in §0.2 are revised; every other §1–§8 section is preserved verbatim from `Cross_Axis_Composition_Document_v2_1.md`.*

## §0 Change note (v2.1 → v2.2)

### §0.1 Revision context

CXA doc v2.2 is the Phase 7 sub-phase 7c **prerequisite pass** absorption. Sub-phase 7c (cross-axis composition seam instantiation) entry-gate orientation surfaced four prerequisites before the 101-edge bucket wiring opens, filed at `.harness/cxa_7c_prerequisites_report.md`. v2.2 absorbs all four. Authored in-CLI per the design-substrate-canonical revision discipline (Phase 7; design-phase back-flow deprecated 2026-05-15).

### §0.2 Per-prerequisite amendment trace

| Prerequisite | Class | Site(s) amended | Resolution shape |
|---|---|---|---|
| Prereq 1 — placeholder carrier IDs | 1 | §2.3.5 (8 rows), §2.3.6 (7 rows) | Citation-precision resolution: every `U-AS-NN` / `U-CP-NN` placeholder resolved to its canonical carrier unit by the cited contract anchor against the producer-axis plan coverage table. Resolution table at `.harness/cxa_7c_placeholder_resolution.md`. No carrier ID invented (X-AL-3). |
| Prereq 4 — CXA-OD-IS-EDGE-DRIFT | 2 | §2.1, §2.2, §2.3.4, §2.4 | Operator decision 2026-05-16: **wire 4** (OD plan v2.4 §4.5.1 canonical), not 6 (CXA v2.1 baseline). §2.3.4 conformed to the OD plan v2.4 4-row enumeration; the 2 mis-routed rows (OD v2.4 C3-15 deletions) dropped. Aggregate edge count 101 → 99. |
| Prereq 3 — §3 staleness vs OD plan v2.7–v2.10 | — | §3.3, §3.4, §3.5, §3.6.1, §3.7 | §3.3 `harness.breaker.*` Tier column struck (OD plan v2.8 D-3 — OD spec C-OD-07 §7.1 declares no tier classification). §3.4 `audit.signature.*` 4th attribute corrected `sha256` → `key_period` (OD plan v2.7 D-3). Cascade: §3.5 audit.signature row, §3.6.1 P1-CXA-1 disposition, §3.7 aggregate. |
| Prereq 2 — CP plan `RoleRoutingBinding` Class 1 | — | (no CXA site) | Reconciled at CP plan v2.10 (catch-up note — the Class 1 was operator-resolved 2026-05-16). No CXA amendment; the CP→IS U-CP-04 edges are unblocked. Recorded here for completeness. |

### §0.3 Cross-axis edge enumeration

**Aggregate edge count: 101 → 99.** The −2 delta is the Prereq 4 OD→IS conformance (CXA v2.1 baseline 6 → OD plan v2.4 canonical 4). The 2 dropped edges (U-OD-27 → sqlite substrate; U-OD-27 → ring-buffer eviction) were mis-routed declarations in the CXA v2.1 baseline — OD plan v2.4 §0.4.2 establishes they are OD-axis-internal, not cross-axis edges. No edge added; no edge silently extended (X-AL-3 holds). Prereq 1 is carrier-ID precision only — no edge added or dropped.

Revised aggregate:

| Bucket | v2.1 | v2.2 |
|---|---|---|
| AS → IS | 13 | 13 |
| CP → IS | 36 | 36 |
| CP → AS | 24 | 24 |
| OD → IS | 6 | **4** |
| OD → AS | 10 | 10 |
| OD → CP | 12 | 12 |
| **Aggregate** | **101** | **99** |

### §0.4 Source-plan version-citation update

v2.2 cites IS plan v2.3, AS plan v1.2, CP plan v2.10, OD plan v2.11 at all amended sites. The OD-plan side of the Prereq 1 citation resolution lands in parallel at OD plan v2.11 (§4.5.2 / §4.5.3 + the U-OD-17/19/23/26/29/33/30 unit-body cross-axis `Depends on` declarations). CXA v2.2 and OD plan v2.11 carry the identical resolved carrier IDs.

### §0.5 Forward-flagged concerns (status at v2.2)

| Concern | Status at v2.2 |
|---|---|
| Rows 10 + 12 anchor citations (F1-CXA-03) | Closed at v2.1 — unchanged |
| F2-12 closure-path execution | Closed — see `F2-12_Closure_Declaration.md` |
| Workflow §7 fidelity-grammar revision (Path δ) | Carry-forward — out-of-band |
| 3 Class 3 citation-imprecision items (C3-CXA-7c-1/2/3) | Logged at `.harness/cxa_7c_placeholder_resolution.md`; non-blocking; C3-CXA-7c-1/2 corrected in this document; C3-CXA-7c-3 folded into CP plan v2.10 |

### §0.6 Authoring discipline

Scope minimality: v2.2 changes restricted to the four 7c-prerequisite resolutions. Per-prerequisite traceability at §0.2. Cross-axis edge re-verification: 99-edge count intact (§0.3). Pattern P1 byte-exact discipline applied at §3 re-verification against OD plan v2.10 + OD spec v1.4.

---

## §2 Cross-axis adjacency matrix (Stage 1 deliverable) — REVISED

### §2.1 Aggregate 4×4 adjacency matrix — REVISED (Prereq 4)

The matrix captures **`Depends on` cross-axis edges** declared at consumer-side plans per `implementation-planner` SKILL.md §7 cross-axis annotation discipline. Producer-side substrate exports are captured via each plan's terminal aggregate exporter manifest (U-IS-17, U-AS-33, U-CP-54, U-CP-55, U-OD-34) and are inverse to the directed-edge declarations in this matrix.

| Source ↓ / Target → | IS         | AS         | CP         | OD         |
|---|---|---|---|---|
| **IS**              | *(self)*   | 0          | 0          | 0          |
| **AS**              | **13**     | *(self)*   | 0          | 0          |
| **CP**              | **36**     | **24**     | *(self)*   | 0          |
| **OD**              | **4**      | **10**     | **12**     | *(self)*   |

**Aggregate cross-axis edge count: 99 edges across 6 non-empty buckets.** (OD → IS conformed 6 → 4 per Prereq 4; see §0.3.)

The 6 zero buckets correspond to producer-side substrate exports surfaced via terminal aggregate exporter manifests and consumed by downstream `Depends on` declarations rather than duplicated as outbound edges. This preserves foundational-first ordering at axis granularity: IS anchors; OD terminates.

### §2.2 Axis-level dependency graph — REVISED (edge label only)

The §2.2 ASCII dependency graph is preserved verbatim from v2.1 with one edge-label correction: the **OD → IS edge label reads `IS (4)`**, not `IS (6)`, per Prereq 4. Acyclicity unchanged — topological order IS < AS < CP < OD holds; the conformance is an edge-count reduction, not a re-direction.

### §2.3 Per-bucket edge enumeration

§2.3.1 (AS → IS, 13 edges), §2.3.2 (CP → IS, 36 edges), §2.3.3 (CP → AS, 24 edges) are **preserved verbatim from v2.1** — no placeholder carrier IDs, no Prereq-1/4 impact.

#### §2.3.4 OD → IS (4 edges) — REVISED (Prereq 4)

Source: OD plan v2.11 §4.5.1 (4-row enumeration; OD plan v2.4 C3-15 Path (i-refined) canonical, version-cite-updated). The CXA v2.1 §2.3.4 6-row table carried 5 `U-IS-NN` placeholders; OD plan v2.4 §0.4.2 had already resolved this bucket — CXA v2.1 was stale. Operator decision 2026-05-16: wire the 4-edge OD-plan-canonical enumeration.

| Source OD unit | IS carrier | Contract anchor | U-OD-34 manifest entry |
|---|---|---|---|
| U-OD-20 | U-IS-12 (idempotency-key join carrier)        | C-IS-10 §10.2  | export #6 |
| U-OD-30 | U-IS-11 (JSONL event-ledger write carrier)    | C-IS-10 §10.5  | export #8 |
| U-OD-30 | U-IS-10 (hash-chain verification carrier)     | C-IS-10 §10.3  | export #8 |
| U-OD-34 | U-IS-17 (terminal aggregate exporter)         | IS substrate seam exports | (terminal aggregate reference) |

**Dropped from the v2.1 baseline (OD plan v2.4 C3-15 deletion record):** `U-OD-27 → sqlite substrate` (was `U-IS-NN`, C-IS-13 §13.2) and `U-OD-27 → ring-buffer eviction` (was `U-IS-NN`, C-IS-08 §8.4) — both mis-routed: sqlite substrate residence and ring-buffer eviction are OD-axis-internal, not IS-axis primitives. The v2.1 §2.3.4 rows falsely declared OD→IS cross-axis edges where none exist. U-OD-27's sqlite-related acceptance criteria remain unchanged within OD-internal scope.

#### §2.3.5 OD → AS (10 edges) — REVISED (Prereq 1)

Source: OD plan v2.11 §4.5.2. All 8 `U-AS-NN` placeholders resolved to canonical carrier units by contract anchor against the AS plan v1 coverage table (`.harness/cxa_7c_placeholder_resolution.md`).

| Source OD unit | AS carrier | Contract anchor | U-OD-34 manifest entry |
|---|---|---|---|
| U-OD-06 | U-AS-33 (terminal aggregate exporter — namespace map) | C-AS-16 §16.1 + §16.4 | export #2 |
| U-OD-17 | U-AS-14 (5-axis gate-level multiplicative tunable composition) | C-AS-12 §12.1 | export #8 |
| U-OD-19 | U-AS-19 (cross-axis idempotency-key composition + cost-attribution joining) | C-AS-15 §15.6 | export #6 |
| U-OD-23 | U-AS-18 (sampling discipline for sandbox events + audit-floor) | C-AS-15 §15.4 | export #1 |
| U-OD-23 | U-AS-31 (`anthropic.*` span attribute namespace) | C-AS-14 §14.2 | export #1 |
| U-OD-29 | U-AS-15 (cross-deployment sandbox-tier monotonicity contract) | C-AS-12 §12.4 | export #7 |
| U-OD-33 | U-AS-14 (5-axis gate-level multiplicative tunable composition) | C-AS-12 §12.1 | export #8 |
| U-OD-33 | U-AS-19 (cross-axis idempotency-key composition + cost-attribution joining) | C-AS-15 §15.6 | export #8 |
| U-OD-33 | U-AS-15 (cross-deployment sandbox-tier monotonicity contract) | C-AS-12 §12.4 | export #8 |
| U-OD-34 | U-AS-33 (terminal aggregate exporter) | AS substrate seam exports | (terminal aggregate reference) |

*Hint-imprecision note (C3-CXA-7c-1).* The v2.1 §2.3.5 descriptive hints labelled C-AS-12 §12.1 a "D2 sandbox-tier monotonicity unit"; AS spec C-AS-12 §12.1 is the **5-axis multiplicative tunable parameter**, §12.4 is the **cross-deployment monotonicity contract**. The contract anchors in the v2.1 table are correct (OD unit bodies — e.g. U-OD-33 §22.4 — confirm intent to compose against §12.1); the carrier-unit descriptions above are corrected to the AS plan v1 unit titles.

#### §2.3.6 OD → CP (12 edges) — REVISED (Prereq 1)

Source: OD plan v2.11 §4.5.3. All 7 `U-CP-NN` placeholders resolved to canonical carrier units by contract anchor against the CP plan v2 coverage table. **U-OD-09 is the single F-CP-01 Stage 3b inversion site** — OD-anchored substrate ingested at CP (U-CP-54 §24.1.C).

| Source OD unit | CP carrier | Contract anchor | U-OD-34 manifest entry |
|---|---|---|---|
| U-OD-07 | U-CP-54 (CP namespace exports)                       | C-CP-24 §24.1.A + §24.1.B | export #2 |
| U-OD-08 | U-CP-54 (F3 lifecycle event attributes)              | C-CP-24 §24.1.B           | export #3 |
| **U-OD-09 (OD → CP exporter)** | U-CP-54 (substrate-anchored breaker ingestion) | C-CP-24 §24.1.C | export #4 |
| U-OD-17 | U-CP-43 (4-axis multiplicative gate-level rule + cross-deployment monotonicity) | C-CP-19 §19.2 | export #8 |
| U-OD-19 | U-CP-32 (multi-agent span hierarchy + per-span sampling) | C-CP-14 §14.1 | export #6 |
| U-OD-21 | U-CP-09 (cross-family fallback chain composition)    | C-CP-04                   | export #6 |
| U-OD-23 | U-CP-46 (7 `audit.*` attributes + 4 `hitl.*` span attribute schemas) | C-CP-20 §20.6 | export #1 |
| U-OD-26 | U-CP-47 (5-class fail taxonomy + `validator.fail.*` namespace) | C-CP-21 §21.5 | export #1 |
| U-OD-30 | U-CP-46 (7 `audit.*` attributes + 4 `hitl.*` span attribute schemas) | C-CP-20 §20.4 | export #8 |
| U-OD-33 | U-CP-43 (4-axis multiplicative gate-level rule + cross-deployment monotonicity) | C-CP-19 §19.2 | export #8 |
| U-OD-34 | U-CP-54 (terminal aggregate exporter — namespace map) | CP substrate seam exports | (terminal aggregate reference) |
| U-OD-34 | U-CP-55 (CP F2-12 ACTIVE inheritance)                 | C-CP-24 §24.4             | (F2-12 inheritance reference) |

*Anchor-precision note (C3-CXA-7c-2).* The v2.1 §2.3.6 cited bare `C-CP-19` for the U-OD-17 / U-OD-33 edges; refined to `C-CP-19 §19.2` (cross-deployment monotonicity sub-section per CP plan coverage). *Carrier note (C3-CXA-7c-3).* C-CP-20 §20.6 (HITL-event span schema) is materially carried by U-CP-46; U-CP-46's Implements line cites §20.4/§20.5 — the §20.5/§20.6 Implements-line imprecision is a CP-plan citation-precision item, folded into CP plan v2.10. The carrier is unambiguous.

### §2.4 Per-axis outbound posture summary — REVISED (Prereq 4)

| Axis | Outbound cross-axis edges | Outbound buckets | Posture |
|---|---|---|---|
| IS | 0   | 0 / 3 | Pure foundational substrate; exports via U-IS-17 manifest; no outbound `Depends on` declarations |
| AS | 13  | 1 / 3 | Consumes IS substrate only; exports to CP / OD via U-AS-33 manifest |
| CP | 60  | 2 / 3 | Consumes IS + AS substrate; exports to OD via U-CP-54 (namespace) + U-CP-55 (F2-12 ACTIVE inheritance) |
| OD | 26  | 3 / 3 | Consumer-most axis; consumes IS + AS + CP substrate; one inverted exporter (U-OD-09 → CP) |
| **Aggregate** | **99** | — | — |

(OD outbound 28 → 26 per Prereq 4 OD→IS conformance.)

---

## §3 Pattern P1 cross-axis byte-exact verification — REVISED (Prereq 3)

§3.1, §3.2, §3.6.2 are **preserved verbatim from v2.1**. §3.3, §3.4, §3.5, §3.6.1, §3.7 are re-verified against OD plan v2.10 + OD spec v1.4 and revised below.

### §3.3 7 `harness.breaker.*` attributes (substrate-anchored inversion) — REVISED

The F-CP-01 Stage 3b single inversion: OD declares canonically (U-OD-09); CP ingests (U-CP-54 §24.1.C); export direction is OD → CP.

| Attribute name | Byte-exact match |
|---|---|
| `harness.breaker.scope`                  | ✅ |
| `harness.breaker.from_state`             | ✅ |
| `harness.breaker.to_state`               | ✅ |
| `harness.breaker.trigger_count`          | ✅ |
| `harness.breaker.permanent_fail_repeats` | ✅ |
| `harness.breaker.tool_id`                | ✅ |
| `harness.breaker.model_version`          | ✅ |

**7/7 attribute-name PASS.** The v2.1 **Tier column (`REQUIRED` / `CONDITIONAL`) is struck.** OD plan v2.8 D-3 established that OD spec C-OD-07 §7.1 declares **no tier classification** (the §7.1 table columns are `Attribute | Type | Source | Definition`), and the `tier:` annotations were un-materializable against the landed `AttributeTier` enum. `HARNESS_BREAKER_ATTRIBUTES` is a `List<string>` of the seven §7.1 attribute names (landed: `harness-od/src/harness_od/harness_breaker_schema.py`). U-CP-54 §24.1.C `source_authority_posture = SUBSTRATE_ANCHORED_OUTSIDE_CP`.

### §3.4 `audit.signature.*` cross-axis attributes — REVISED

OD plan v2.7 D-3 corrected the OD-side `AuditSignatureAttributes` record: the un-spec'd 4th attribute `sha256` was struck and the record conformed to the v2.5-canonical 4-attribute `audit.signature.*` set per ADR-D5 v1.3 §1.4.1 / OD spec §21.2. The record also moved U-OD-30 → U-OD-00 (OD plan v2.7 D-1; U-OD-30 consumes it via the `[U-OD-00]` edge). Per-plan declaration:

| Plan / unit                        | Declared attributes                                       | Count | Anchor cited |
|---|---|---|---|
| OD plan `AuditSignatureAttributes` @ U-OD-00 (carrier; consumed by U-OD-30) | `value`, `algorithm`, `key_id`, `key_period` | 4 | OD §21.2 + ADR-D5 v1.3 §1.4.1 |
| CP plan U-CP-46 (contract-bearing)                            | `key_id`, `verification_result`           | 2 | C-CP-20 §20.4 + §20.5 |
| IS plan §10.3 composition reference (non-contract-bearing)    | `value`, `algorithm`, `key_id`, `key_period` | 4 | ADR-D5 v1.3 §1.4 |

**Convergence achieved.** With the v2.7 D-3 correction, the OD-side and IS-side `audit.signature.*` sets are **byte-exact identical** (`{value, algorithm, key_id, key_period}`). The v2.1 divergence (OD `sha256` vs IS `key_period` under the same ADR-D5 anchor) is dissolved.

Per-attribute presence matrix (5 distinct cross-axis attributes; was 6 at v2.1):

| Attribute                              | OD @ U-OD-00 | CP U-CP-46 | IS §10.3 ref |
|---|---|---|---|
| `audit.signature.key_id`               | ✓ | ✓ | ✓ |
| `audit.signature.value`                | ✓ |   | ✓ |
| `audit.signature.algorithm`            | ✓ |   | ✓ |
| `audit.signature.key_period`           | ✓ |   | ✓ |
| `audit.signature.verification_result`  |   | ✓ |   |

(`audit.signature.sha256` removed — was an un-spec'd OD-side field, struck at OD plan v2.7 D-3.)

### §3.5 Per-namespace attribute-byte-exact verification — REVISED

| Namespace | Attribute count | Verification result | Finding |
|---|---|---|---|
| `sandbox.*`         | 7 | 7/7 PASS                                       | — |
| `anthropic.cache_*` | 4 | 4/4 attribute-name PASS; 1 formula-expression drift | P1-CXA-3 (closed as F2-OD-02 at OD plan v2) |
| `mcp.*`             | 7 | 7/7 PASS                                       | — |
| `hitl.*`            | 4 | 4/4 PASS                                       | — |
| `topology.*`        | 10 | byte-exact PASS                                | P1-CXA-4 (discharged at P6-CK Iter 1) |
| `subagent.*`        | 7 | byte-exact PASS                                | P1-CXA-5 (discharged at P6-CK Iter 1) |
| `engine.*`          | 3 | byte-exact PASS                                | P1-CXA-6 (discharged at P6-CK Iter 1) |
| `audit.*`           | 7 | 7/7 PASS                                       | P1-CXA-1 resolved by convergence — see §3.6.1 |

**v2.2 note.** The `audit.*` row finding column is updated. Two prior items are now disposed: P1-CXA-1 (the `sha256`-vs-`key_period` divergence at the `audit.signature.*` sub-namespace, §3.4) is **resolved by convergence** — the OD plan v2.7 D-3 correction makes the OD and IS sets byte-exact identical; and P1-CXA-2 (`verification_result`, a CP-only attribute serving distinct phase semantics — signature verification result, not raw hash) was **discharged at P6-CK Iteration 1** as a non-finding. With both disposed, no open drift remains on the `audit.*` / `audit.signature.*` surface.

### §3.6.1 Findings (Workflow v1.5 §4.1.2 canonical classification) — REVISED

| Pre-surfaced ID | Surface | Class | Disposition |
|---|---|---|---|
| P1-CXA-1 | IS §10.3 cites `audit.signature.key_period`; OD U-OD-30 cited `audit.signature.sha256` under the same ADR-D5 v1.3 §1.4 anchor | Class 2 | **Resolved by convergence at CXA v2.2.** Absorbed as F2-OD-03 at OD plan v2; the absorption was executed at **OD plan v2.7 D-3** — the OD-side `AuditSignatureAttributes` 4th attribute corrected `sha256` → `key_period`. OD and IS `audit.signature.*` sets now byte-exact identical (§3.4). Finding closed. |
| P1-CXA-3 | U-OD-23 `cache_hit_rate` formula token vs U-AS-31 `anthropic.cache_read_input_tokens` | Class 2 | Absorbed as F2-OD-02 at OD plan v2 (formula token realignment at U-OD-23 acceptance #3). Unchanged at v2.2. |

### §3.7 Pattern P1 aggregate disposition — REVISED

**Post-7c-prerequisite re-verification (v2.2 update).** §3 was re-verified byte-exact against OD plan v2.10 + OD spec v1.4. Two staleness points corrected: §3.3 `harness.breaker.*` Tier column struck (OD plan v2.8 D-3); §3.4 `audit.signature.*` 4th attribute `sha256` → `key_period` (OD plan v2.7 D-3). The §3.4 correction **resolves P1-CXA-1 by convergence** — OD and IS `audit.signature.*` sets are now byte-exact identical. No P1-CXA finding remains open. All OD-touching buckets (OD→IS, OD→AS, OD→CP) are Pattern-P1-clear for 7c bucket wiring.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_2.md` |
| Status | Canonical — Phase 7 sub-phase 7c prerequisite pass absorbed |
| Predecessor | `Cross_Axis_Composition_Document_v2_1.md` (preserved verbatim except §0, §2.1–§2.4, §3.3–§3.7) |
| Authored at | Phase 7 sub-phase 7c, 2026-05-16 (in-CLI) |
| Companion artifacts | OD plan v2.11 (§4.5.2/§4.5.3 + unit-body citation resolution); CP plan v2.10 (Prereq 2 reconcile); `.harness/cxa_7c_placeholder_resolution.md` |
| Next gate | 7c bucket wiring — 6 buckets in axis-topological order (AS→IS, CP→IS, CP→AS, OD→IS, OD→AS, OD→CP) = 99 typed seams |
