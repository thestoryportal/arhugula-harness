# Cross-Axis Composition Document (v2.3)

*Delta over v2.2. v2.3 reclassifies every declared cross-axis edge against the landed 7b code. Only the sections enumerated in §0.2 are revised; every other §1–§8 section is preserved verbatim from `Cross_Axis_Composition_Document_v2_2.md`.*

## §0 Change note (v2.2 → v2.3)

### §0.1 Revision context — the 7c reclassification finding

Sub-phase 7c bucket wiring began at bucket 1 (AS→IS). Wiring + two parallel audits (CP-consumer buckets; OD-consumer buckets) against the **landed 7b code** established that the CXA edge enumeration **conflated three structurally different kinds of cross-axis relationship under one "typed edge" label**:

- a **typed seam** — a Pydantic v2 model / enum / function imported across the axis-package boundary;
- a **convention-level relationship** — Pattern-P1 byte-exact namespace alignment, a re-applied scheme/algorithm, or a free-text `str` / axis-local-enum descriptor — a real cross-axis obligation, but not a type import;
- a **phase-2-runtime relationship** — a ledger write / hash / append / emit, or a terminal-exporter manifest string reference — runtime behavior, not a compile-time link.

It also found **spurious** rows — edges declared where the consumer unit references the producer axis nowhere at all.

This is not a counting error; it is a category error in the CXA enumeration (inherited unchanged from v1 through v2.2). The 7b axis-streams built each relationship in the form that fits its kind. v2.3 re-tags every edge to what it actually is, so 7c wiring targets only genuine typed seams and does not attempt Pydantic imports for convention/runtime/spurious rows.

Evidence base (per-edge, durable): `.harness/class_1_tension_cxa_as_is_untyped_edges.md` (AS→IS, bucket-1 wiring + direct verification); `.harness/cxa_7c_audit_cp_buckets.md` (CP→IS, CP→AS); `.harness/cxa_7c_audit_od_buckets.md` (OD→IS, OD→AS, OD→CP).

### §0.2 Sections revised

§0 (this change note); §2.1 (matrix); §2.2 (edge-label); §2.3.1–§2.3.6 (every bucket — classification column added, spurious rows struck, count + producer-attribution corrected); §2.4 (posture summary). §3 unchanged (and see §0.9). All other sections preserved verbatim from v2.2.

### §0.3 Classification taxonomy

| Class | Definition | 7c disposition |
|---|---|---|
| **genuine-typed-seam** | Consumer imports a Pydantic v2 type / enum / function from the producer axis package. | Wire / verify wired at 7c. |
| **convention-level** | Pattern-P1 namespace alignment, re-applied scheme, or free-text/axis-local descriptor. Real obligation, no type import. | NOT wired as an import; satisfied by Pattern-P1 verification (§3). |
| **phase-2-runtime** | Ledger write / hash / append / emit, or terminal-exporter manifest string reference. Runtime behavior. | Deferred to Phase 2 runtime. Not 7c work. |
| **spurious** | Consumer unit references the producer axis nowhere. CXA over-declaration. | Struck from the edge enumeration. |

### §0.4 Aggregate reclassification matrix

| Bucket | Declared (raw cells) | genuine | convention | phase-2-runtime | spurious |
|---|---|---|---|---|---|
| AS → IS (§2.3.1) | 13 | 7 | 3 | 1 | 2 |
| CP → IS (§2.3.2) | 38 *(v2.2 mislabelled 36 — see §0.5)* | 8 | 11 | 17 | 2 |
| CP → AS (§2.3.3) | 24 | 2 | 16 | 0 | 6 |
| OD → IS (§2.3.4) | 4 | 0 | 2 | 2 | 0 |
| OD → AS (§2.3.5) | 10 | 1 | 8 | 1 | 0 |
| OD → CP (§2.3.6) | 12 | 0 | 9 | 3 | 0 |
| **Total** | **101** | **18** | **49** | **24** | **10** |

The OD→AS / OD→CP rows fold in U-OD-33's 4 edges (3 OD→AS + 1 OD→CP) as **convention-level**: U-OD-33's plan §3.8.2 body carries cross-axis dependencies as a `cross_axis_composition_target: str | None` field with verification explicitly deferred (acc #5) — confirmed at U-OD-33 landing (the unit was un-landed at 7b — §0.7).

**Corrected aggregate.** Of 101 raw declared edges: **10 spurious are struck** (+1 genuine seam added per §0.5) → **92 canonical cross-axis relationships**. Of those 92 — **~18 genuine typed seams** (→ **22** after the §0.5 addition + §0.6 retarget corrections), **49 convention-level**, **24 phase-2-runtime**. The v2.1/v2.2 headline "101 / 99 typed cross-axis edges" overstated the typed-seam count by ~4-5×.

### §0.5 Count corrections

- **§2.3.2 (CP→IS) cardinality.** v2.1/v2.2 assert "36 edges". The verbatim multi-target-cell table sums to **38** `(CP-unit × IS-target)` pairs (cell enumeration: 04×3 + 12×1 + 14×4 + 18×3 + 27×3 + 30×2 + 33×2 + 34×4 + 35×2 + 37×2 + 42×4 + 49×2 + 50×3 + 52×2 + 55×1 = 38). v2.3 §2.3.2 is **38**. The v2.2 §0.3 aggregate "99" carried this −2 undercount; the true raw count is **101**.
- **U-CP-52 → U-IS-12 (unlisted genuine seam).** `hitl_timeout_degradation.py:31` genuinely imports `Identifier` from `harness_is.state_ledger_entry_schema` — a genuine typed seam — but the §2.3.2 U-CP-52 row lists only U-IS-07 + U-IS-11. v2.3 §2.3.2 adds the **U-CP-52 → U-IS-12** edge (genuine), and tags the declared U-IS-07/U-IS-11 targets phase-2-runtime.

### §0.6 Producer-attribution corrections (retarget)

Three CP→AS edges carry a real `SandboxTier` / `BlastRadiusTier` import, but the CXA rows mis-attribute the producer unit. Per the U-CP-26 row's own attribution, those tier types are produced by **U-AS-01** (C-AS-01 §1.1 four-tier taxonomy), not by U-AS-09/13/12. v2.3 retargets:

| Edge | v2.2 declared | v2.3 retarget | Effect |
|---|---|---|---|
| U-CP-27 → U-AS-09 (#3, CP→AS) | U-AS-09 (sub-agent tier ascension) | **U-CP-27 → U-AS-01** | convention → genuine-typed-seam |
| U-CP-43 → U-AS-13 (#12, CP→AS) | U-AS-13 | **U-CP-43 → U-AS-01** | convention → genuine-typed-seam |
| U-CP-45 → U-AS-12 (#16, CP→AS) | U-AS-12 | **U-CP-45 → U-AS-01** | convention → genuine-typed-seam |

After §0.5 + §0.6: genuine typed seams **18 → 22** (CP→IS +1 via U-CP-52→U-IS-12; CP→AS +3 via retarget). The §0.4 matrix shows the pre-correction figures; §2.3.2/§2.3.3 below show post-correction.

### §0.7 U-OD-33 — un-landed unit (cross-reference)

The OD audit found **U-OD-33 was never landed at 7b** — OD-7b is 34/35, not 35/35 (a worklist counting error; U-OD-33 is a within-axis leaf so no test caught it). U-OD-33 is the consumer of 4 CXA edges (§2.3.5 ×3, §2.3.6 ×1). Filed: `.harness/class_1_tension_u_od_33_not_landed.md`. Resolution: land U-OD-33 against OD plan §3.8.2 (in progress, this corrective pass). U-OD-33's 4 edges are classified convention-level per §0.4 (its plan body carries cross-axis targets as `str` references).

### §0.8 Spurious edges struck (10)

| Bucket | Struck edge | Reason |
|---|---|---|
| AS→IS | U-AS-30 → U-IS-01 | `anthropic_graceful_degradation.py` consumes no IS path type — uses the AS-local `MemoryToolStorageBackend` enum |
| AS→IS | U-AS-30 → U-IS-02 | same |
| CP→IS | U-CP-50 → U-IS-01 | `material_diff_detection.py` imports no `harness_is` — no filesystem-path reference |
| CP→IS | U-CP-55 → U-IS-12 | `cp_cross_axis_composition_manifest.py` is a reference-list manifest; no idempotency-key consumption |
| CP→AS | U-CP-32 → U-AS-17 | `multi_agent_span_hierarchy.py` imports no `harness_as` |
| CP→AS | U-CP-32 → U-AS-31 | same |
| CP→AS | U-CP-39 → (via U-CP-43) | CP plan §3.6 declares it a non-edge ("none; consumes via U-CP-43") — drop the row |
| CP→AS | U-CP-50 → U-AS-10 | `material_diff_detection.py` — no secret-fail-class reference |
| CP→AS | U-CP-50 → U-AS-29 | same — no model-catalog reference |
| CP→AS | U-CP-53 → U-AS-14 | `t_perm_3_composition.py` imports no `harness_as` |

### §0.9 §3 Pattern P1 — relationship to the convention-level set

§3 (Pattern P1 byte-exact verification) is preserved verbatim from v2.2. v2.3 records its new significance: the **49 convention-level edges** are precisely the relationships §3 governs — their cross-axis "composition" *is* the Pattern-P1 byte-exact namespace/scheme alignment §3 verifies, not a Python import. §3's existing verification (re-confirmed clean at the v2.2 prerequisite pass) discharges the convention-level set. No convention-level edge is wired at 7c; none needs to be.

### §0.10 Authoring discipline

Scope: reclassification only — no edge's underlying 7b implementation is changed; v2.3 corrects the CXA document to match the landed code. Per-edge evidence traces to the three audit artifacts (§0.1). Spurious strikes and retargets are operator-authorized (2026-05-17). No design extension (X-AL-3 holds — v2.3 removes over-declaration, adds nothing).

---

## §2 Cross-axis adjacency matrix — REVISED

### §2.1 Aggregate 4×4 adjacency matrix — REVISED

The matrix now distinguishes **total canonical cross-axis relationships** (post-spurious-strike) from **genuine typed seams** (the 7c-wireable subset).

Total cross-axis relationships per bucket (spurious struck):

| Source ↓ / Target → | IS | AS | CP | OD |
|---|---|---|---|---|
| **IS** | *(self)* | 0 | 0 | 0 |
| **AS** | 11 | *(self)* | 0 | 0 |
| **CP** | 37 | 18 | *(self)* | 0 |
| **OD** | 4 | 10 | 12 | *(self)* |

**92 canonical cross-axis relationships** (101 raw − 10 spurious + 1 added genuine seam). Genuine typed seams within that: **22** (§0.5 + §0.6). Convention-level: **49**. Phase-2-runtime: **24**. (22 + 49 + 24 = 95; the 3 retargeted edges are counted once each — net 92.)

(AS→IS 13−2=11; CP→IS 38−2 spurious +1 U-CP-52→U-IS-12 = 37; CP→AS 24−6 spurious = 18; OD→IS 4; OD→AS 10; OD→CP 12. Total 92.)

### §2.2 Axis-level dependency graph — REVISED

The §2.2 ASCII graph is preserved from v2.2 with edge labels updated to the §2.1 totals (AS→IS 11, CP→IS 37, CP→AS 17, OD→IS 4, OD→AS 10, OD→CP 12). Axis-level acyclicity (IS < AS < CP < OD) holds.

### §2.3 Per-bucket edge enumeration — REVISED (classification column added)

Each bucket below carries the 7c classification. Per-edge evidence (consumer file:line) is at the cited audit artifact. **G** = genuine-typed-seam, **C** = convention-level, **R** = phase-2-runtime, **S** = spurious (struck).

#### §2.3.1 AS → IS (13 declared; 11 canonical) — evidence: `class_1_tension_cxa_as_is_untyped_edges.md`

| Consumer | Producer | Contract | Class |
|---|---|---|---|
| U-AS-19 | U-IS-07 | C-AS-15 §15.6 | **G** — `Identifier` (wired) |
| U-AS-19 | U-IS-12 | C-AS-15 §15.6 | **G** — idempotency-key join (wired) |
| U-AS-25 | U-IS-08 | C-AS-08 §8.1 | **C** — re-applies C-IS-06 §6.1 canonicalization scheme |
| U-AS-26 | U-IS-07 | C-AS-08 §8.2 | **G** — `StateLedgerEntry`/`Actor`/`Identifier` (wired 7b) |
| U-AS-26 | U-IS-09 | C-AS-08 §8.3 | **G** — `construct_prior_event_hash` (wired 7b) |
| U-AS-26 | U-IS-10 | C-AS-08 §8.3 | **G** — `verify_chain` (wired 7b) |
| U-AS-27 | U-IS-11 | C-AS-08 §8.4 | **R** — ledger append is runtime |
| U-AS-28 | U-IS-01 | C-AS-13 §13.2 | **G** — `PathClass` (wired 7b) |
| U-AS-28 | U-IS-02 | C-AS-13 §13.2 | **G** — `PathResolver`/`PATH_CLASS_REGISTRY` (wired 7b) |
| U-AS-29 | U-IS-01 | C-AS-13 §13.3 | **C** — free-text `skills_filesystem_residence: str` descriptor |
| U-AS-29 | U-IS-02 | C-AS-13 §13.3 | **C** — same |
| ~~U-AS-30 → U-IS-01~~ | — | C-AS-13 §13.6 | **S** — struck (AS-local `MemoryToolStorageBackend`) |
| ~~U-AS-30 → U-IS-02~~ | — | C-AS-13 §13.6 | **S** — struck |

#### §2.3.2 CP → IS (38 declared + 1 added; 37 canonical) — evidence: `cxa_7c_audit_cp_buckets.md` Bucket 2

genuine (9): U-CP-04→U-IS-01, U-CP-04→U-IS-02, U-CP-30→U-IS-12, U-CP-33→U-IS-01, U-CP-33→U-IS-02, U-CP-34→U-IS-07, U-CP-34→U-IS-11, U-CP-35→U-IS-12, **U-CP-52→U-IS-12 (added §0.5)**.
convention (11): U-CP-04→U-IS-06, U-CP-18→U-IS-07/09/12, U-CP-35→U-IS-07, U-CP-42→U-IS-07/08/09/11, U-CP-49→U-IS-12, U-CP-50→U-IS-12.
phase-2-runtime (17): U-CP-12→U-IS-07, U-CP-14→U-IS-07/08/09/11, U-CP-27→U-IS-07/09/11, U-CP-30→U-IS-07, U-CP-34→U-IS-08/09, U-CP-37→U-IS-07/09, U-CP-49→U-IS-11, U-CP-50→U-IS-11, U-CP-52→U-IS-07/11.
spurious struck (2): ~~U-CP-50→U-IS-01~~, ~~U-CP-55→U-IS-12~~.

#### §2.3.3 CP → AS (24 declared; 18 canonical) — evidence: `cxa_7c_audit_cp_buckets.md` Bucket 3

genuine (5): U-CP-26→U-AS-01, U-CP-44→U-AS-20, **U-CP-27→U-AS-01 (retarget §0.6)**, **U-CP-43→U-AS-01 (retarget §0.6)**, **U-CP-45→U-AS-01 (retarget §0.6)**.
convention (13): U-CP-09→U-AS-30, U-CP-27→U-AS-14, U-CP-27→U-AS-15, U-CP-29→U-AS-29, U-CP-33→U-AS-31, U-CP-43→U-AS-05, U-CP-43→U-AS-14, U-CP-43→U-AS-15, U-CP-45→U-AS-14, U-CP-47→U-AS-03, U-CP-48→U-AS-10, U-CP-48→U-AS-29, U-CP-55→U-AS-14.
spurious struck (6): ~~U-CP-32→U-AS-17~~, ~~U-CP-32→U-AS-31~~, ~~U-CP-39→(non-edge)~~, ~~U-CP-50→U-AS-10~~, ~~U-CP-50→U-AS-29~~, ~~U-CP-53→U-AS-14~~.

#### §2.3.4 OD → IS (4 canonical) — evidence: `cxa_7c_audit_od_buckets.md` Bucket 1

| Consumer | Producer | Contract | Class |
|---|---|---|---|
| U-OD-20 | U-IS-12 | C-IS-10 §10.2 | **C** — `idempotency_key: str` axis-local descriptor |
| U-OD-30 | U-IS-11 | C-IS-10 §10.5 | **R** — ledger-write composition is runtime |
| U-OD-30 | U-IS-10 | C-IS-10 §10.3 | **C** — OD re-implements its own hash-chain walk |
| U-OD-34 | U-IS-17 | IS seam exports | **R** — terminal-exporter manifest string reference |

*Anchor note:* the landed U-OD-30 file docstring cites C-IS-14 §14.2 / C-IS-13 §13.5 (pre-remap); OD plan v2.4 §0.4.2 remapped these to C-IS-10 §10.5 / §10.3, and OD plan v2.11 §0.5 propagates the remap into the unit-body declaration. The landed U-OD-30 docstring citation is updated when U-OD-30 is next touched (a 7c/Phase-2 code-touch); non-blocking.

#### §2.3.5 OD → AS (10 canonical) — evidence: `cxa_7c_audit_od_buckets.md` Bucket 2

| Consumer | Producer | Contract | Class |
|---|---|---|---|
| U-OD-06 | U-AS-33 | C-AS-16 §16.1+§16.4 | **C** — Pattern-P1 prefix-set alignment |
| U-OD-17 | U-AS-14 | C-AS-12 §12.1 | **C** — declarative, module constant |
| U-OD-19 | U-AS-19 | C-AS-15 §15.6 | **C** — attribute-name surface |
| U-OD-23 | U-AS-18 | C-AS-15 §15.4 | **C** — free-text `source_span_class` descriptor |
| U-OD-23 | U-AS-31 | C-AS-14 §14.2 | **C** — `anthropic.cache_*` attribute-name surface |
| U-OD-29 | U-AS-15 | C-AS-12 §12.4 | **G** — `SandboxTier` imported (wired 7b, U-OD-29 v2.10) |
| U-OD-33 | U-AS-14 | C-AS-12 §12.1 | **C** — `cross_axis_composition_target: str` (U-OD-33 §3.8.2) |
| U-OD-33 | U-AS-19 | C-AS-15 §15.6 | **C** — same |
| U-OD-33 | U-AS-15 | C-AS-12 §12.4 | **C** — same |
| U-OD-34 | U-AS-33 | AS seam exports | **R** — terminal-exporter manifest string reference |

#### §2.3.6 OD → CP (12 canonical) — evidence: `cxa_7c_audit_od_buckets.md` Bucket 3

| Consumer | Producer | Contract | Class |
|---|---|---|---|
| U-OD-07 | U-CP-54 | C-CP-24 §24.1.A+B | **C** — Pattern-P1 prefix-set alignment |
| U-OD-08 | U-CP-54 | C-CP-24 §24.1.B | **C** — attribute-namespace `str` fields |
| U-OD-09 | U-CP-54 | C-CP-24 §24.1.C | **R** — F-CP-01 Stage 3b inversion: OD *exports* `harness.breaker.*`; CP ingests at composition |
| U-OD-17 | U-CP-43 | C-CP-19 §19.2 | **C** — declarative, bridging-arc transition surface |
| U-OD-19 | U-CP-32 | C-CP-14 §14.1 | **C** — OD-local `FanOutPattern` re-declaration |
| U-OD-21 | U-CP-09 | C-CP-04 | **C** — OD-local `FallbackChainCostComposition` |
| U-OD-23 | U-CP-46 | C-CP-20 §20.6 | **C** — `hitl.invocation.responded` attribute-name surface |
| U-OD-26 | U-CP-47 | C-CP-21 §21.5 | **C** — `validator.fail.*` attribute-name prefix *(promotion candidate — §0.11)* |
| U-OD-30 | U-CP-46 | C-CP-20 §20.4 | **C** — CP-emitted audit namespace, attribute-name surface |
| U-OD-33 | U-CP-43 | C-CP-19 §19.2 | **C** — `cross_axis_composition_target: str` (U-OD-33 §3.8.2) |
| U-OD-34 | U-CP-54 | CP seam exports | **R** — terminal-exporter manifest string reference |
| U-OD-34 | U-CP-55 | C-CP-24 §24.4 | **R** — F2-12 inheritance carry-forward declaration |

### §2.4 Per-axis outbound posture summary — REVISED

| Axis | Canonical outbound relationships | Genuine typed seams | Posture |
|---|---|---|---|
| IS | 0 | 0 | Pure foundational substrate |
| AS | 11 | 6 | Consumes IS; the 5 non-genuine are scheme-inheritance / descriptors / 1 runtime |
| CP | 55 | 13 | Largest consumer; convention + runtime dominate (F2 audit-ledger composition is runtime) |
| OD | 26 | 1 | Consumer-most axis; built almost entirely as Pattern-P1 convention surfaces by design |
| **Aggregate** | **92** | **22** | — |

### §0.11 Promotion candidates (operator decision — NOT applied at v2.3)

Two convention-level edges could be promoted to genuine typed seams, but doing so changes a consumer signature and is an AS/CP/OD-plan decision, not a mechanical 7c step. Logged, not applied:
- U-OD-26 → U-CP-47 (§2.3.6): could import `harness_cp...ValidatorFailClass`.
- U-OD-29 → U-AS-15 §12.4 arm (§2.3.5): could import `harness_as.cross_deployment_monotonicity`.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_3.md` |
| Status | Canonical — Phase 7 sub-phase 7c edge reclassification |
| Predecessor | `Cross_Axis_Composition_Document_v2_2.md` (preserved verbatim except §0, §2.1–§2.4) |
| Authored at | Phase 7 sub-phase 7c, 2026-05-17 (in-CLI) |
| Evidence base | `.harness/class_1_tension_cxa_as_is_untyped_edges.md`; `.harness/cxa_7c_audit_cp_buckets.md`; `.harness/cxa_7c_audit_od_buckets.md`; `.harness/class_1_tension_u_od_33_not_landed.md` |
| Net effect | 101 raw declared → 10 spurious struck, +1 added genuine seam → **92 canonical cross-axis relationships**: 22 genuine typed seams (7c-wired/-verified), 49 convention-level (discharged by §3 Pattern P1), 24 phase-2-runtime (deferred to Phase 2) |
| Next gate | Verify the ~22 genuine typed seams are wired (most already are at 7b); 7c convention + runtime sets need no import wiring |
