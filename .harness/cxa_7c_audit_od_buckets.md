# 7c Cross-Axis Composition Audit — OD-Consumer Buckets

**Scope.** Classify the 26 OD-consumer cross-axis edges (OD→IS 4 + OD→AS 10 + OD→CP 12) as
`genuine-typed-seam` / `convention-level` / `phase-2-runtime` / `spurious`, ahead of a canonical
CXA v2.3 revision.

**Authority.** Edge enumerations from `design-substrate/Cross_Axis_Composition_Document_v2_2.md`
§2.3.4/§2.3.5/§2.3.6 (post-Prereq-1/Prereq-4 resolved carrier IDs). Consumer code under
`harness-od/src/harness_od/`. Producer surfaces under `harness-{is,as,cp}/src/`.

**Read-only audit.** No code or design artifact was edited.

---

## Method note — what the OD axis-stream actually did at 7b

Every OD consumer unit body carries an explicit, consistent declaration: cross-axis edges are
**declarative placeholders resolved at 7c**, and OD imports **no typed surface** from IS/AS/CP at
7b. The single exception is U-OD-29, which was operator-authorized at 7b (v2.10) to import
`SandboxTier` from `harness_as.sandbox_tier` early. Direct quotes:

- U-OD-17 (`cross_deployment_monotonic_tightening.py:30-37`): *"Those edges are declarative …
  U-OD-17 consumes no typed surface from either — the composition is at the bridging-arc
  transition surface, not a type import."*
- U-OD-19 (`cost_attribution_sandbox_fanout.py` docstring): *"The cross-axis dependencies are
  attribute-name + enum-value surfaces … no cross-axis type is consumed at a signature position."*
- U-OD-23 (`operator_burden_eval_primitives.py` docstring): *"The cross-axis dependencies are
  attribute-name surfaces (`sandbox.violation`, `anthropic.cache_*`, `hitl.invocation.responded`)."*
- U-OD-30 (`multi_tenant_trace_separation_and_audit_ledger.py:26-35`): *"resolve to the
  IS-exported `StateLedgerEntry` shape + hash-chain discipline (NOT to an `AuditLedger` type …)."*

So the classification below is not guesswork against intent — it largely reflects what the OD
plan and unit bodies already say the edges are.

**Important finding on U-OD-33.** U-OD-33 (`§3.8.2` — compose per-dimension preservation
invariants) has **no source file** in `harness-od/src/harness_od/`. It is referenced only as a
`source_unit` *string* in U-OD-34's manifest (`substrate_seam_exports_aggregate_manifest.py:253`).
U-OD-33 was not landed at 7b. All four U-OD-33 cross-axis edges (3 AS + 1 CP) therefore cannot be
audited against consumer code — marked **NEEDS-REVIEW**.

---

## Bucket 1 — OD → IS (4 edges) — CXA §2.3.4

| # | OD consumer | Producer target | Contract anchor | Classification | Evidence |
|---|---|---|---|---|---|
| 1 | U-OD-20 | U-IS-12 (idempotency-key join) | C-IS-10 §10.2 | **convention-level** | `idempotency_join_dedup.py:95,122,162` — `idempotency_key` typed `str`, an axis-local free-text descriptor. Docstring (`:77`): the extended-shape carrier "resolves at sub-phase 7c against C-IS-10". No `harness_is` import; U-IS-12 exposes no join-key type the consumer imports. Forcing one would change the `str` signature. |
| 2 | U-OD-30 | U-IS-11 (JSONL event-ledger write) | C-IS-10 §10.5 | **phase-2-runtime** | `multi_tenant_trace_separation_and_audit_ledger.py:31-35` — the edge composes the OD-side `verify_hash_chain_integrity` walk with the IS ledger-write *at runtime*; "NOT to an `AuditLedger` type — `AuditLedger` is OD-axis-local". A ledger-write IO relationship, not a compile-time type link. **Anchor discrepancy: file docstring (`:47`) cites C-IS-14 §14.2, CXA §2.3.4 cites C-IS-10 §10.5 — see Discrepancies.** |
| 3 | U-OD-30 | U-IS-10 (hash-chain verification) | C-IS-10 §10.3 | **convention-level** | `multi_tenant_trace_separation_and_audit_ledger.py:15,33-35` — OD re-implements its own hash-chain walk (`verify_hash_chain_integrity`) over OD-local `AuditLedger` entries; docstring says it "composes with the IS C-IS-13 §13.5 primitive at 7c". OD re-applies the hash-chain algorithm rather than importing IS's `verify_chain` (`harness_is/chain_verification.py`). **Anchor discrepancy: docstring cites C-IS-13 §13.5; CXA §2.3.4 cites C-IS-10 §10.3.** |
| 4 | U-OD-34 | U-IS-17 (IS terminal aggregate exporter) | IS substrate seam exports | **phase-2-runtime** | `substrate_seam_exports_aggregate_manifest.py` docstring — "U-IS-17 … These are string-typed target identifiers; the edge wiring lands at 7c." U-OD-34 carries `U-IS-17` as a manifest string reference, not a type import. Terminal-exporter manifest reference = aggregate hand-off, not a typed seam. |

**Bucket 1 tally:** genuine 0 / convention 2 / phase-2-runtime 2 / spurious 0.

---

## Bucket 2 — OD → AS (10 edges) — CXA §2.3.5

| # | OD consumer | Producer target | Contract anchor | Classification | Evidence |
|---|---|---|---|---|---|
| 5 | U-OD-06 | U-AS-33 (AS terminal aggregate exporter — namespace map) | C-AS-16 §16.1 + §16.4 | **convention-level** | `as_source_namespace_verification.py` — declares `AS_SOURCE_NAMESPACE_PREFIXES` as a tuple of `str` prefixes; verifies them "byte-exact against the AS plan U-AS-33 substrate seam exports manifest per Pattern P1". Pattern-P1 mechanical alignment of a re-declared prefix set — no AS type imported. |
| 6 | U-OD-17 | U-AS-14 (5-axis gate-level multiplicative tunable) | C-AS-12 §12.1 | **convention-level** | `cross_deployment_monotonic_tightening.py:30-37` — explicitly "declarative; … U-OD-17 consumes no typed surface … composition is at the bridging-arc transition surface, not a type import." Edge carried as a module constant (`D2_CROSS_DEPLOYMENT_MONOTONICITY_COMPOSITION`). |
| 7 | U-OD-19 | U-AS-19 (cross-axis idempotency-key composition + cost-attribution joining) | C-AS-15 §15.6 | **convention-level** | `cost_attribution_sandbox_fanout.py` docstring — "The cross-axis dependencies are attribute-name + enum-value surfaces … no cross-axis type is consumed at a signature position." `SandboxOverhead` is OD-axis-local; `harness_as.sandbox_event_idempotency` (`CostAttribution`, `join_cost_attribution_by_idempotency_key`) is *not* imported. |
| 8 | U-OD-23 | U-AS-18 (sampling discipline for sandbox events + audit-floor) | C-AS-15 §15.4 | **convention-level** | `operator_burden_eval_primitives.py:118` — uses free-text `source_span_class="sandbox.violation"` descriptors; docstring: "attribute-name surfaces … resolved at U-OD-34". `harness_as.sandbox_event_sampling.SamplingPosture` not imported. |
| 9 | U-OD-23 | U-AS-31 (`anthropic.*` span attribute namespace) | C-AS-14 §14.2 | **convention-level** | `operator_burden_eval_primitives.py:144,146` — free-text `source_span_class="anthropic.cache"` + a formula string referencing `anthropic.cache_*` attribute names. No import of `harness_as.anthropic_attribute_namespaces`. |
| 10 | U-OD-29 | U-AS-15 (cross-deployment sandbox-tier monotonicity contract) | C-AS-12 §12.4 | **genuine-typed-seam** (partially wired) | `per_sandbox_tier_otlp_reachability.py:66` — `from harness_as.sandbox_tier import SandboxTier`. NOTE: the *import done* is `SandboxTier` (the C-AS-01 §1.1 tier enum), which is the U-OD-29 ↔ AS-tier-enum link. The CXA-declared C-AS-12 §12.4 monotonicity edge to U-AS-15 itself: docstring (`:59-65`) says that edge "resolves at sub-phase 7c — declared here, not chased". `harness_as.cross_deployment_monotonicity` (the §12.4 carrier) is not imported. The tier-enum seam is genuine and live; the §12.4 monotonicity seam proper is still convention/declarative. Classified **genuine** because a real producer type *is* imported and the §12.4 carrier (`PersonaTierFloor`/`bridging_arc_effective_tier_raise`) is cleanly importable. |
| 11 | U-OD-33 | U-AS-14 (5-axis gate-level multiplicative tunable) | C-AS-12 §12.1 | **NEEDS-REVIEW** | U-OD-33 has no source file; not landed at 7b. Cannot inspect consumer code. (U-OD-33 ≡ `§3.8.2`; referenced only as a string in `substrate_seam_exports_aggregate_manifest.py:253`.) |
| 12 | U-OD-33 | U-AS-19 (cross-axis idempotency-key composition) | C-AS-15 §15.6 | **NEEDS-REVIEW** | U-OD-33 not landed — see #11. |
| 13 | U-OD-33 | U-AS-15 (cross-deployment sandbox-tier monotonicity) | C-AS-12 §12.4 | **NEEDS-REVIEW** | U-OD-33 not landed — see #11. |
| 14 | U-OD-34 | U-AS-33 (AS terminal aggregate exporter) | AS substrate seam exports | **phase-2-runtime** | `substrate_seam_exports_aggregate_manifest.py` docstring — `U-AS-33` carried as a string-typed manifest target identifier; "edge wiring lands at 7c". Manifest-reference, not a typed seam. |

**Bucket 2 tally:** genuine 1 / convention 5 / phase-2-runtime 1 / spurious 0 / NEEDS-REVIEW 3.

---

## Bucket 3 — OD → CP (12 edges) — CXA §2.3.6

| # | OD consumer | Producer target | Contract anchor | Classification | Evidence |
|---|---|---|---|---|---|
| 15 | U-OD-07 | U-CP-54 (CP namespace exports) | C-CP-24 §24.1.A + §24.1.B | **convention-level** | `cp_source_namespace_verification.py` — declares CP-source prefix tuple of `str`; "verifies the OD-side ingested prefix set against the CP-side declaration; any drift is a Pattern P1 violation". No `harness_cp` import; Pattern-P1 re-declared prefix set. |
| 16 | U-OD-08 | U-CP-54 (F3 lifecycle event attributes) | C-CP-24 §24.1.B | **convention-level** | `f3_lifecycle_event_mapping.py` docstring — "the U-CP-54 edge is a cross-axis dependency resolved at … 7c — NOT a 7b blocker; no typed surface is imported from U-CP-54 here." `attribute_namespaces` carried as OD-local `str` fields. |
| 17 | U-OD-09 → U-CP-54 (OD→CP exporter; F-CP-01 Stage 3b inversion) | U-CP-54 (substrate-anchored breaker ingestion) | C-CP-24 §24.1.C | **phase-2-runtime** | `harness_breaker_schema.py:11-15` — this is the *export* direction: OD declares `harness.breaker.*` and "exports `harness.breaker.*` to the CP plan as a CP-consuming seam … resolved at 7c". The OD unit imports nothing from CP; CP will ingest OD's substrate at runtime/composition. An anchored-substrate ingestion relationship, not an OD-side type import. (Worth a CXA note: this is the one inverted-direction edge in the bucket.) |
| 18 | U-OD-17 | U-CP-43 (4-axis multiplicative gate-level rule + cross-deployment monotonicity) | C-CP-19 §19.2 | **convention-level** | `cross_deployment_monotonic_tightening.py:30-37` — same declarative posture as #6; "composition is at the bridging-arc transition surface, not a type import." `harness_cp.gate_level_rule` (`GateLevel`, `assert_cross_persona_monotonicity`) not imported. |
| 19 | U-OD-19 | U-CP-32 (multi-agent span hierarchy + per-span sampling) | C-CP-14 §14.1 | **convention-level** | `cost_attribution_sandbox_fanout.py` docstring — "the fan-out pattern is CP C-CP-14 §14.1 … consumed cross-axis (Pattern P1 byte-exact alignment)". `FanOutPattern` is an OD-axis-local `StrEnum` re-declaring the pattern; no CP type imported. |
| 20 | U-OD-21 | U-CP-09 (cross-family fallback chain composition) | C-CP-04 | **convention-level** | `cross_family_rollup.py` docstring — "the U-CP-NN edge is a cross-axis dependency resolved at … 7c … no typed surface is imported from any CP package here." `FallbackChainCostComposition` is OD-axis-local; `harness_cp.cross_family_fallback_chain.FallbackChain` not imported. |
| 21 | U-OD-23 | U-CP-46 (7 `audit.*` + 4 `hitl.*` span attribute schemas) | C-CP-20 §20.6 | **convention-level** | `operator_burden_eval_primitives.py:108` — free-text `source_span_class="hitl.invocation.responded"`; docstring lists it as an "attribute-name surface". `harness_cp.audit_hitl_span_namespace.HITLSpanSchema` not imported. |
| 22 | U-OD-26 | U-CP-47 (5-class fail taxonomy + `validator.fail.*` namespace) | C-CP-21 §21.5 | **convention-level** | `eval_vs_runtime_gate.py` docstring — "Depends on: [… U-CP-NN (cross-axis: CP — C-CP-21 §21.5)]" resolved at 7c. The `inline_gate` shape "MUST carry `validator.fail.*` attributes" — checked as a free-text attribute-name prefix; `harness_cp.validator_fail_taxonomy.ValidatorFailClass` not imported. (This is a *clean* candidate to promote to genuine: U-CP-47 exposes the importable `ValidatorFailClass` enum.) |
| 23 | U-OD-30 | U-CP-46 (7 `audit.*` + 4 `hitl.*` span attribute schemas) | C-CP-20 §20.4 | **convention-level** | `multi_tenant_trace_separation_and_audit_ledger.py:28-33` — "CP C-CP-20 §20.4 (audit namespace 7-attribute schema) … resolve to … the CP-emitted audit namespace". `AuditSignatureAttributes` is OD-axis-local (U-OD-00 carrier); no CP type imported. |
| 24 | U-OD-33 | U-CP-43 (4-axis gate-level rule + cross-deployment monotonicity) | C-CP-19 §19.2 | **NEEDS-REVIEW** | U-OD-33 not landed at 7b — no source file. See Bucket 2 #11. |
| 25 | U-OD-34 | U-CP-54 (CP terminal aggregate exporter — namespace map) | CP substrate seam exports | **phase-2-runtime** | `substrate_seam_exports_aggregate_manifest.py` docstring — `U-CP-54` carried as a string-typed manifest target identifier; "edge wiring lands at 7c". Manifest reference. |
| 26 | U-OD-34 | U-CP-55 (CP F2-12 ACTIVE inheritance) | C-CP-24 §24.4 | **phase-2-runtime** | `substrate_seam_exports_aggregate_manifest.py` docstring + `F2_12_CarryForwardInheritance` model (`:114`) — U-CP-55 carried as a string-typed inheritance-target reference; the F2-12 inheritance is a carry-forward declaration, not a type import. |

**Bucket 3 tally:** genuine 0 / convention 8 / phase-2-runtime 3 / spurious 0 / NEEDS-REVIEW 1.

---

## Aggregate tally (26 edges)

| Classification | OD→IS | OD→AS | OD→CP | Total |
|---|---|---|---|---|
| genuine-typed-seam | 0 | 1 | 0 | **1** |
| convention-level | 2 | 5 | 8 | **15** |
| phase-2-runtime | 2 | 1 | 3 | **6** |
| spurious | 0 | 0 | 0 | **0** |
| NEEDS-REVIEW | 0 | 3 | 1 | **4** |

**Genuine typed seams: 1 of 26** — only edge #10 (U-OD-29 → AS sandbox-tier enum), and even
that is the `SandboxTier` *enum* import already done at 7b; the CXA-declared C-AS-12 §12.4
monotonicity edge proper is still declarative.

---

## Summary

The OD-consumer buckets are **far more over-declared than Bucket 1 (AS→IS)**. Where AS→IS landed
7 genuine of 13, OD lands **at most 1 genuine of 26** (and arguably 0 against the *exact*
contract anchors declared, since edge #10's live import is the C-AS-01 tier enum, not the
C-AS-12 §12.4 monotonicity carrier).

Root cause is structural and intentional, not a defect: OD is the consumer-most-downstream axis
(CXA v2.2 §2.4 — 0 outbound edges). The OD axis-stream built every cross-axis edge as a
**declarative placeholder** under explicit 7b discipline ("resolved at 7c, no typed surface
imported"). The edges materialized as one of three things:

1. **convention-level (15)** — OD re-declares an attribute-name prefix set or a free-text
   `str`/local-enum descriptor and Pattern-P1-aligns it against the producer manifest. Forcing a
   producer-type import would change OD signatures. Examples: namespace-prefix verification
   (#5, #15), free-text `source_span_class` descriptors (#8, #9, #21), OD-local re-declared
   enums (#19 `FanOutPattern`).
2. **phase-2-runtime (6)** — terminal-exporter manifest references carried as target-identifier
   *strings* (#4, #14, #25, #26), ledger-write IO (#2), and the F-CP-01 Stage 3b inverted
   export edge (#17). These are runtime/composition relationships, not compile-time type links.
3. **genuine (1)** — only #10's `SandboxTier` import.

**No spurious edges** — every edge's consumer unit does reference the producer axis (via
contract anchor, attribute name, or manifest string), so none is purely fabricated.

### Recommendation for the CXA v2.3 revision

- **6 phase-2-runtime edges** are real composition relationships but not "typed cross-axis
  edges" in the 7c-wiring sense — they should be re-tagged so 7c does not attempt a Pydantic
  import for them.
- **15 convention-level edges** are Pattern-P1 alignment obligations, not type imports — same
  re-tag.
- **2 promotion candidates** worth flagging to the operator: edge #22 (U-OD-26 → U-CP-47) could
  cleanly import `harness_cp.validator_fail_taxonomy.ValidatorFailClass`, and edge #10's §12.4
  arm could import `harness_as.cross_deployment_monotonicity`. Both would change OD consumer
  signatures, so promotion is an operator decision, not a mechanical 7c step.

### Edges flagged NEEDS-REVIEW (4)

Edges #11, #12, #13 (U-OD-33 → AS) and #24 (U-OD-33 → CP): **U-OD-33 was not landed at 7b** —
it has no source file under `harness-od/src/harness_od/`. It exists only as a `source_unit`
string in U-OD-34's manifest (`substrate_seam_exports_aggregate_manifest.py:253`) and as a plan
unit (`Implementation_Plan_Operational_Discipline_v2_1.md` §3.8.2). These 4 edges cannot be
classified against consumer code. **This is itself a potential Class 1 / Class 2 finding**: the
CXA v2.2 §2.3.5/§2.3.6 tables declare 4 edges from a unit that does not exist in the landed 7b
codebase. The 7c wiring of these edges is blocked on U-OD-33 landing first — recommend surfacing
to the operator before the OD→AS / OD→CP buckets are wired.

### Anchor discrepancies observed (informational — for CXA v2.3 reconciliation)

- Edge #2 (U-OD-30 → IS): CXA §2.3.4 cites **C-IS-10 §10.5**; the U-OD-30 file docstring cites
  **C-IS-14 §14.2** (Tier-5 audit-ledger durability).
- Edge #3 (U-OD-30 → IS): CXA §2.3.4 cites **C-IS-10 §10.3**; the U-OD-30 file docstring cites
  **C-IS-13 §13.5** (hash-chain integrity primitive).

The CXA v2.2 §2.3.4 4-row table (sourced from OD plan v2.11 §4.5.1) and the landed U-OD-30 unit
body (sourced from OD plan v2.1 §3.7.4) disagree on which IS contract sections the OD→IS edges
anchor to. Not an audit blocker for classification (both readings land convention/runtime), but
the canonical CXA v2.3 should reconcile the anchor before the OD→IS bucket is finalized.
