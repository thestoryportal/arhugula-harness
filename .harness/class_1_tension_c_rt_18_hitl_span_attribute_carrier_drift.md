# Class 1 Tension — C-RT-18 §14.8.2/§14.8.5 HITL span attribute carrier drift

**Filed:** 2026-05-21 — Phase 7 sub-phase 7b U-RT-60 implementation arc OPEN (executed under `phase-7-implementation` skill from HEAD `e3b193f`). Surfaced at Step 2 of the unit consumption shape (read spec contract) when cross-checking AC #7 + AC #13 against the canonical CP carrier at `harness-cp/src/harness_cp/audit_hitl_span_namespace.py`.
**Surfaced by:** `phase-7-implementation` skill §6 halt condition (cited spec contract section under-specifies / self-contradicts the surface). Routed here via `phase-7-back-flow-routing` skill §4.1 Step 1 classification.
**Status:** **AUTHORING → PROPOSING → RATIFIED → APPLIED** 2026-05-21 (Q5 single-arc co-publication landed: spec v1.10 → v1.11 at HEAD `904a4ec` + plan v2.8 → v2.9 at HEAD `8e08e9e`). U-RT-60 implementation arc unblocked against re-clearance state — canonical 4-span shape per ADR-D5 v1.3 §1.8 + CP carrier `HITL_SPAN_NAMESPACE_SCHEMA` 4-entry shape is now spec-authoritative + plan-authoritative. Q6 systemic-pattern follow-on arc remains operator-scheduled independently. Downstream owed (non-blocking U-RT-60 impl): workspace `CLAUDE.md` §2.3 + §2.4 runtime spec version row bump v1.10 → v1.11; per-axis CLAUDE.md no change owed (CP carrier untouched; ADR-D5 untouched).
**Substitutions at stake:** **H_T-CP-20** (HITL primitive + 4-response palette + `hitl.*` / `audit.*` namespaces; X-AL-2 retirement criterion B reading at spec §14.8.3 — "namespace emission at production execution path" cannot be verified if the composer emits attribute names that the canonical CP carrier does not declare).
**Defect class:** Class 1 — spec contract self-contradicts at the attribute-name layer; design-phase artifact requires revision per workspace `CLAUDE.md` §4.3 + X-AL-3 (no silent H_T design extension) + X-AL-1 (carrier-canonical discipline).

---

## Defect

The runtime spec C-RT-18 §14.8 contract self-contradicts at the canonical-attribute-source layer for the `hitl.*` span namespace. Two clauses of the same contract cannot both be satisfied by any implementation:

### Clause A (§14.8.5 + AC #13 — carrier-canonical)

`Spec_Harness_Runtime_v1.md` v1.10 §14.8.5 paragraph "Producer-side attribute carrier reference":

> v1.9 composer imports the canonical `hitl.*` + `audit.*` attribute name set from `harness_cp.audit_hitl_span_namespace.AUDIT_NAMESPACE_SCHEMA` + `harness_cp.audit_hitl_span_namespace.HITL_SPAN_NAMESPACE_SCHEMA` (landed per U-CP-46). **Hand-coded attribute strings are NOT permitted;** the carrier import ties retirement criterion B verification ("references the canonical attribute carrier") directly to the canonical producer surface (analog of §14.6 / §14.7 producer-carrier discipline).

Plan v2.8 AC #13 mirrors verbatim:

> producer-side carrier import discipline per spec §14.8.5 also verified (composer imports `hitl.*` + `audit.*` attribute name set from `harness_cp.audit_hitl_span_namespace.AUDIT_NAMESPACE_SCHEMA` + `HITL_SPAN_NAMESPACE_SCHEMA` per U-CP-46; **hand-coded attribute strings NOT permitted** — pyright/ruff lint-clean assertion).

### Clause B (§14.8.2 step 4e/4g + AC #7 + AC #8 — hand-coded attribute names)

`Spec_Harness_Runtime_v1.md` v1.10 §14.8.2 step 4e:

> Set attributes per C-CP-20 §20.5 row 1 (`hitl.gate.evaluated.placement` = string-value of `placement.position`) + row 2 (`hitl.gate.evaluated.response_palette` = sorted-tuple-of-string-values of `palette`).

`Spec_Harness_Runtime_v1.md` v1.10 §14.8.2 step 4g:

> Set `hitl.invocation.responded.response_class` = string-value of `gate_result.response` per C-CP-20 §20.5 row 3 + `hitl.invocation.responded.response_latency_ms` = `gate_result.latency_ms` per row 4.

Plan v2.8 AC #7 + AC #8 mirror these attribute names verbatim. Spec §14.8.5 fail-class extensions also name `hitl.gate.evaluated.outcome = "timeout"` / `"audit-compose-failed"` — both attribute names absent from the carrier.

### Carrier ground truth

`harness-cp/src/harness_cp/audit_hitl_span_namespace.py:107-141` declares `HITL_SPAN_NAMESPACE_SCHEMA` with 4 spans + their attribute lists. Per `Spec_Control_Plane_v1_2.md` §20.6 (lines 1818–1820 — canonical at CP spec v1.2; preserved verbatim through CP spec v1.3 → v1.9):

| Span name | Canonical attributes (CP §20.6 + carrier) |
|---|---|
| `hitl.gate.evaluated` | `hitl.gate.level`, `hitl.gate.persona_tier`, `hitl.gate.required` |
| `hitl.invocation.opened` | `hitl.gate.level`, `hitl.invocation.placement`, `hitl.invocation.handoff_context_size_bytes`, `hitl.invocation.audit_ledger_entry_id` |
| `hitl.invocation.responded` | `hitl.response.class`, `hitl.response.latency_ms`, `hitl.response.summary_hash` |
| `hitl.invocation.timed_out` | `hitl.timeout.duration_ms`, `hitl.timeout.degradation_mode_applied` |

### The contradiction at attribute-name granularity

| Runtime-spec narrative name | Carrier-canonical name | Status |
|---|---|---|
| `hitl.gate.evaluated.placement` | (no carrier slot) | **MISSING** — would be a new attribute on `hitl.gate.evaluated` span |
| `hitl.gate.evaluated.response_palette` | (no carrier slot) | **MISSING** — would be a new attribute on `hitl.gate.evaluated` span |
| `hitl.gate.evaluated.outcome` (per §14.8.5 fail-class rows) | (no carrier slot) | **MISSING** — would be a new attribute on `hitl.gate.evaluated` span |
| `hitl.invocation.responded.response_class` | `hitl.response.class` | RENAME — same semantic, different prefix |
| `hitl.invocation.responded.response_latency_ms` | `hitl.response.latency_ms` | RENAME — same semantic, different prefix |
| (no spec-narrative name) | `hitl.gate.level` | spec narrative drops a carrier-declared attribute |
| (no spec-narrative name) | `hitl.gate.persona_tier` | spec narrative drops a carrier-declared attribute |
| (no spec-narrative name) | `hitl.gate.required` | spec narrative drops a carrier-declared attribute |
| (no spec-narrative name) | `hitl.response.summary_hash` | spec narrative drops a carrier-declared attribute |

**Two sub-issues, separated for cleaner architectural recommendation:**

1. **Rename drift (low risk):** `hitl.invocation.responded.response_class` / `.response_latency_ms` are equivalent semantically to `hitl.response.class` / `hitl.response.latency_ms`. Same content, different attribute-prefix convention. Resolution scope: spec narrative correction.
2. **Missing carrier slots (load-bearing; potential X-AL-3 surface):** `hitl.gate.evaluated.placement`, `.response_palette`, and `.outcome` have **no canonical attribute at all** in the CP carrier or in CP spec v1.2 §20.6. These would be new H_T design surface (new span attributes) at the canonical owner (CP axis). Per X-AL-3 ("no silent H_T design extension at Phase 7 execution"), absorbing these by carrier extension WITHOUT first surfacing the new-primitive question to the operator IS the worst Phase 7 failure mode.

The composer cannot satisfy Clause A (carrier-canonical; hand-coded forbidden) and Clause B (hand-code these specific names) simultaneously. The contradiction is at the contract layer, not the implementation layer.

## Evidence — current state at HEAD `e3b193f`

```
# Runtime spec §14.8.5 — carrier-canonical clause
$ sed -n '1582,1586p' design-substrate/Spec_Harness_Runtime_v1.md
v1.9 composer imports the canonical `hitl.*` + `audit.*` attribute name set from
`harness_cp.audit_hitl_span_namespace.AUDIT_NAMESPACE_SCHEMA` +
`harness_cp.audit_hitl_span_namespace.HITL_SPAN_NAMESPACE_SCHEMA` (landed per U-CP-46).
Hand-coded attribute strings are NOT permitted; ...

# Runtime spec §14.8.2 step 4e — hand-coded names contradicting §14.8.5
$ sed -n '1529p' design-substrate/Spec_Harness_Runtime_v1.md
4e. Open `hitl.gate.evaluated` span. ... Set attributes per C-CP-20 §20.5 row 1
(`hitl.gate.evaluated.placement` = string-value of `placement.position`) +
row 2 (`hitl.gate.evaluated.response_palette` = sorted-tuple-of-string-values of `palette`).

# Carrier ground truth — gate.evaluated declares 3 attrs; none are `.placement` or `.response_palette`
$ sed -n '108,115p' harness-cp/src/harness_cp/audit_hitl_span_namespace.py
HITLSpanSchema(
    span_name="hitl.gate.evaluated",
    span_attributes=(
        "hitl.gate.level",
        "hitl.gate.persona_tier",
        "hitl.gate.required",
    ),
),

# CP spec v1.2 §20.6 — canonical authority for the carrier
$ sed -n '1818,1820p' design-substrate/Spec_Control_Plane_v1_2.md
| `hitl.gate.evaluated` | `hitl.gate.level` (cardinality-safe metric dimension), `hitl.gate.persona_tier`, `hitl.gate.required: bool` ... |
| `hitl.invocation.opened` | `hitl.gate.level` (cross-event reference), `hitl.invocation.placement` ∈ ..., `hitl.invocation.handoff_context_size_bytes`, `hitl.invocation.audit_ledger_entry_id` |
| `hitl.invocation.responded` | `hitl.response.class` per C-CP-16 §16.4 ∈ ..., `hitl.response.latency_ms`, `hitl.response.summary_hash` |
```

**Drift origin.** `git log -p` confirms the runtime-spec §14.8.2 narrative attribute names were introduced at commit `2685774` (the v1.8 → v1.9 C-RT-18 spec authoring landing 2026-05-20). The pre-implementation adversarial review at HEAD `c783b06` (`.harness/adversarial_review_u_rt_60_pre_impl.md`) ran against `2685774` and surfaced F3-01 (H_E binding mechanism underspec) but **missed this attribute-name drift**. The v1.9 → v1.10 amendment at commit `510c502` touched only §14.8.3 H_E binding mechanism — did not introduce or correct this drift.

## Routing target

Per `phase-7-back-flow-routing` skill §3.1 routing table: **Phase 5 spec revision-pass** (runtime spec) — with possible cascade to **Phase 6 CXA revision-pass** (if missing carrier slots are absorbed via CP carrier extension, U-CP-46 spec growth) OR **Phase 6 plan revision-pass** (if sub-issue 2 is reduced from carrier extension to spec narrative correction). In-CLI per workspace `CLAUDE.md` §4.3 + memory `[[design-substrate-divergence]]`.

| Affected artifact | Revision required (scope-minimum reading) | Revision required (carrier-extension reading) |
|---|---|---|
| `design-substrate/Spec_Harness_Runtime_v1.md` v1.10 → v1.11 | §14.8.2 step 4e/4g + §14.8.5 fail-class rows + AC narrative (in plan-cite) rewritten to use canonical carrier-declared attribute names; semantic content of "what to record" preserved | Same as scope-minimum + cite the new CP carrier surface (e.g., `hitl.gate.evaluated.placement` if CP-side carrier-extension lands) |
| `design-substrate/Spec_Control_Plane_v1_2.md` §20.6 (canonical CP attribute schema) | No revision required (drift is at runtime spec, not CP spec) | Extend `hitl.gate.evaluated` attribute list + cascade through CP spec v1.x version chain; X-AL-3 evaluation required (new H_T design surface) |
| `harness-cp/src/harness_cp/audit_hitl_span_namespace.py` `HITL_SPAN_NAMESPACE_SCHEMA` | No code change | Extend `hitl.gate.evaluated` `span_attributes` tuple (+3 entries: `placement`, `response_palette`, `outcome`); update U-CP-46 |
| `.harness/phase-2-session-3-track-a-atomic-decomposition.md` plan v2.8 → v2.9 | AC #7 + AC #8 narrative absorption to use canonical names; AC #13 unchanged (already correct: cite carrier) | AC #7 + AC #8 update + AC #13 carrier-citation refresh |
| Workspace `CLAUDE.md` §2.3 contract count | Runtime spec version bump v1.10 → v1.11 | Same + CP spec version bump if §20.6 amended |

## Halt state

- **Halt point:** U-RT-60 implementation arc open per `phase-7-implementation` skill Step 2 (cited-spec read); no composer code laid down; no Protocol module created; no tests written.
- **Halt timestamp:** 2026-05-21 (this session).
- **Halt rationale:** Spec C-RT-18 §14.8.2 + §14.8.5 self-contradict at attribute-name granularity per Defect §1 above; AC #7 + AC #13 cannot both be satisfied by any implementation.
- **Resumption requires:** spec amendment landed in-CLI; downstream plan absorption; then `phase-7-implementation` re-opens U-RT-60 against the re-clearance state.

## Operator-surface decision points

The systems-architect mode 3 resolution recommendation (to be appended below at the next skill invocation) will produce a chain-grounded recommendation. Operator decision required across at minimum the following question chain:

**Q1 — Sub-issue (1) rename drift resolution (low-risk).** `hitl.invocation.responded.response_class` / `.response_latency_ms` are clearly equivalent in semantic content to canonical `hitl.response.class` / `hitl.response.latency_ms`. The runtime spec narrative drifted at v1.9 authoring; CP carrier + CP spec v1.2 §20.6 are canonical owner per workspace `CLAUDE.md` §1.3 authority chain (CP spec is the named axis-owner for the `hitl.*` namespace). Resolution shape:

- **(a) Runtime spec narrative correction.** Rewrite §14.8.2 step 4g + AC #7/#8 prose to use canonical CP carrier names (`hitl.response.class` / `hitl.response.latency_ms`). Composer code at the impl arc reads these names from the carrier import. NO new H_T design surface; pure narrative drift resolution.
- **(b) Reverse rename at CP side.** Operator may judge `hitl.invocation.responded.response_class` more readable (longer prefix names the parent span); rename at the CP carrier + CP spec v1.2 §20.6. Cascade: U-CP-46 + CP plan + CP spec version chain. Heavier scope.

**Q2 — Sub-issue (2) missing carrier slots resolution (load-bearing; X-AL-3 evaluation required).** `hitl.gate.evaluated.placement`, `.response_palette`, and `.outcome` (per §14.8.5 fail-class rows) have **no carrier slot at all** in the CP-canonical attribute schema. Per X-AL-3 ("no silent H_T design extension at Phase 7 execution"), these are new H_T primitives requiring explicit architectural decision before absorption:

- **(a) Carrier extension at CP side (CP-owner reading).** Extend `HITL_SPAN_NAMESPACE_SCHEMA` at `audit_hitl_span_namespace.py` to add 3 attributes on `hitl.gate.evaluated` span; cascade CP spec v1.2 §20.6 amendment + U-CP-46 plan AC growth + Phase 7d retirement-event impact (H_T-CP-20 retirement-criterion B reading: carrier slots present, so namespace emission per production execution path verifies cleanly). Acknowledges these as legitimate new H_T design surface per ADR-D5 v1.3 §1.4.1 + §1.8 (HITL placement + invocation matrix). Scope: largest.
- **(b) Spec narrative correction — fold semantics into `audit.*` namespace at step 4h.** The "placement" + "response_palette" semantic content lives semantically in the audit-entry composition at step 4h (`compose_hitl_response_audit` carries `placement.position` + palette membership via `response`); the gate span itself emits only the carrier-canonical `hitl.gate.{level,persona_tier,required}` attributes. Rewrite §14.8.2 step 4e to set carrier-canonical attrs from cell + binding; drop `.placement` and `.response_palette` from the span entirely; lean on audit-entry projection at OD consumer side for the now-orphaned data. Scope: smaller (runtime spec only); requires the operator to confirm the gate-span observability cost reduction is acceptable.
- **(c) Spec narrative correction — fold `.outcome` into existing fail-class span attributes.** The `.outcome="timeout"` / `"audit-compose-failed"` attribute is semantically tied to OTel span status / events, not a custom carrier slot; rewrite §14.8.5 fail-class rows to use OTel span `set_status(StatusCode.ERROR)` + `record_exception(...)` patterns; carrier-canonical attrs unchanged. Scope: narrowest for the outcome attribute.

**Q3 — Authority-chain reading.** When CP spec + CP carrier + runtime spec narrative diverge on a CP-owned namespace (`hitl.*`), which is canonical?

- **(a) CP-owner reading.** CP spec C-CP-20 §20.6 + CP carrier are canonical for `hitl.*` (CP owns the namespace per `harness-cp/CLAUDE.md` §1.4 "CP and OD share authority over several namespaces (`hitl.*`, …) via the D6 ingestion pattern: CP emits, OD ingests. Authoritative schema lives at OD spec; CP emits per OD's canonical attribute set."). Wait — that line actually says **authoritative schema lives at OD spec** for shared namespaces — confirming the chain runs OD spec → CP carrier → runtime spec narrative. Runtime narrative is leaf; on conflict, leaf yields.
- **(b) Runtime-narrative-prevails reading.** Reject the v1.9 narrative as authoritatively-canonical; rewrite to use carrier names. Picks (1a) for sub-issue 1 + (2b)/(2c) for sub-issue 2.

**Q4 — X-AL-3 evaluation for sub-issue 2.** If Q2 picks (a) carrier extension, was the spec v1.9 authoring at HEAD `2685774` a silent design extension (X-AL-3 violation that landed without fork)? Or does the v1.9 narrative count as a legitimate proposal that the carrier needs to catch up to? Per workspace `CLAUDE.md` invariant I-2 ("NO H_T design extension at Phase 7 execution-time"), the v1.9 authoring SHOULD have surfaced a fork before extending the gate-span attribute set. The fork was missed; the carrier-extension reading is a *retroactive* X-AL-3 surfacing.

**Q5 — Cascade scope at amendment landing.** Single-arc co-publication (spec v1.10 → v1.11 + plan v2.8 → v2.9 + optional CP-side amendments in one operator-ratification turn) or sequential (runtime narrative correction first, CP-side carrier-extension question deferred to its own arc)? Q5 depends on Q2 choice — if (b) or (c), single-arc is feasible; if (a), the CP-side amendment is a separate spec-writer + plan-revision arc.

**Q6 — Systemic-pattern observation.** This is the **4th** adversarial-review-missed defect in the U-RT-58/59/60 sequence:

| Arc | Adversarial review HEAD | Missed defect |
|---|---|---|
| U-RT-58 | (pre-impl review) | `retry.*` attribute drift (caught at impl) |
| U-RT-59 | (pre-impl review) | CP→OD audit-write gap (caught at impl as Fork 2) |
| U-RT-60 | `c783b06` | F3-01 AskUserQuestion H_E binding mechanism (caught at adversarial review; surfaced this skill's prior fork record) |
| U-RT-60 | `c783b06` | **This fork** — CP span-attribute carrier drift (missed by adversarial review; caught at `phase-7-implementation` Step 2 cited-spec cross-check) |

Per `harness-adversarial-reviewer` skill §6 systemic-pattern threshold: 3+ arcs surfacing similar architectural defect category crosses the threshold. All four U-RT-58/59/60 defects are at **CP↔runtime cross-axis attribute/binding surfaces**. Worth considering: (a) `harness-adversarial-reviewer` skill body extension — explicit "carrier-vs-narrative attribute-name cross-check" check at pre-impl review; (b) `phase-7-implementation` skill Step 2 extension — same cross-check as a hard halt before any code lands; (c) `spec-writer` skill body extension — at any spec revision touching attribute names, mandate carrier diff verification.

---

## Systems-architect mode 3 resolution recommendation

*Filed 2026-05-21 by `systems-architect` skill mode 3 against the 6-question chain above. Per skill §4A.4: this is a recommendation, NOT a decision; operator holds decision authority and may counter-propose. Per skill §4A.2 procedure: chain-grounded against canonical authority chain at workspace `CLAUDE.md` §1.3.*

### Tension statement (precise)

Four artifacts engage the divergence; quoting each verbatim:

1. **ADR-D5 v1.3 §1.8 row 1 (`design-substrate/ADR-D5.md:316`)** — canonical schema for `hitl.gate.evaluated` attributes:
   > `hitl.gate.evaluated` | `hitl.gate.level` (cardinality-safe metric dimension per D6 §1.2), `hitl.gate.persona_tier`, `hitl.gate.required: bool` **(v1.3 — `hitl.gate.tool` and `hitl.gate.mcp_server` retired per F2-iter2-02 Reading 1 canonical pass-through; …)**

2. **ADR-D5 v1.3 §1.8 row 2 (`design-substrate/ADR-D5.md:317`)** — canonical schema for `hitl.invocation.opened` (the span that ALREADY carries placement-as-attribute):
   > `hitl.invocation.opened` | `hitl.gate.level` (cross-event reference; same canonical attribute as evaluated event), `hitl.invocation.placement`, `hitl.invocation.handoff_context_size_bytes`, `hitl.invocation.audit_ledger_entry_id`

3. **CP carrier `HITL_SPAN_NAMESPACE_SCHEMA` (`harness-cp/src/harness_cp/audit_hitl_span_namespace.py:107-141`)** — landed 4-span schema mirroring ADR-D5 v1.3 §1.8 verbatim (gate.evaluated 3 attrs; invocation.opened 4 attrs; invocation.responded 3 attrs; invocation.timed_out 2 attrs).

4. **Runtime spec C-RT-18 §14.8.2 step 4e–4g + §14.8.5 fail-class rows + AC #7/#8 (`design-substrate/Spec_Harness_Runtime_v1.md:1529-1531, 1582-1586` + plan v2.8 §L9-quater)** — runtime composer narrative declares a 2-span schema (`hitl.gate.evaluated` → `hitl.invocation.responded`) with attribute names `hitl.gate.evaluated.placement` / `.response_palette` / `.outcome` and `hitl.invocation.responded.response_class` / `.response_latency_ms` — none of which exist in (1)/(2)/(3); and drops the 2 canonical spans (`hitl.invocation.opened` and `hitl.invocation.timed_out`) where the missing semantic content canonically lives.

The divergence is between artifact (4) — the runtime spec narrative — and (1)+(2)+(3) — the entire upstream chain. (4) self-contradicts further because the same runtime spec §14.8.5 declares carrier (3) canonical and forbids hand-coded attribute strings, so the §14.8.2 + AC #7 hand-coding clause cannot be satisfied alongside the §14.8.5 + AC #13 carrier clause.

### Per-artifact authority-chain placement

Per workspace `CLAUDE.md` §1.3 authority chain (ADR → ADD → PRD → per-axis spec → per-axis plan + CXA) + per `harness-cp/CLAUDE.md` §1.4 D6 ingestion pattern ("CP and OD share authority over several namespaces (`hitl.*`, …) via the D6 ingestion pattern: CP emits, OD ingests. **Authoritative schema lives at OD spec; CP emits per OD's canonical attribute set.**"):

| Artifact | Chain position | Authority for `hitl.*` schema |
|---|---|---|
| ADR-D5 v1.3 §1.8 + ADR-D6 §1.2 | Foundational + Derivative ADR (F-axis HITL primitive + OD-side observability ingestion) | **CANONICAL.** Anchor for the 4-span `hitl.*` schema + per-span attribute set. ADR-D5 v1.3 explicitly retired 2 attribute names at iter-3 F2-iter2-02 resolution under Reading 1 canonical pass-through; the retire-discipline confirms attribute-set commitment is load-bearing. |
| OD spec (referenced by `harness-cp/CLAUDE.md` §1.4) | Per-axis spec — authoritative schema owner per D6 ingestion pattern | Canonical (proxy for ADR-D5/D6 at OD-axis surface) |
| CP spec v1.2 §20.6 (lines 1818–1820) | Per-axis spec — CP emits per OD canonical set | Verbatim re-statement of ADR-D5 §1.8 attribute set |
| CP carrier `audit_hitl_span_namespace.py` | Per-axis plan implementation (U-CP-46 landed) | Carrier mirrors CP spec v1.2 §20.6 verbatim; per `Spec_Harness_Runtime_v1.md` §14.8.5 explicitly named the producer-side canonical attribute source |
| Runtime spec C-RT-18 §14.8 v1.9/v1.10 | Per-axis spec — LEAF position re `hitl.*` (runtime consumes the CP-emitted attribute set; does not own it) | LEAF — on conflict with chain-upstream, yields to chain. Per §4A's mode discipline + workspace `CLAUDE.md` §1.3, the chain runs ADR-D5 → OD spec → CP spec/carrier → runtime spec narrative; **the runtime narrative cannot redefine attributes canonical at the upstream chain.** |
| Runtime plan v2.8 (U-RT-60 ACs) | Per-axis plan — leaf | Inherits runtime spec's reading; on resolution, absorbs the corrected reading |

The authority chain is unambiguous: **(1) ADR-D5 v1.3 §1.8 + (2) ADR-D6 §1.2 + (3) CP carrier are canonical; (4) runtime spec narrative is leaf and diverged.** Resolution direction is determined: conform the runtime spec narrative to the upstream canonical schema. The remaining question is *how* to conform — sub-issue 1 (rename drift) admits a clean narrative correction; sub-issue 2 (missing slots) requires accepting that the canonical schema already places that semantic content at canonical spans + attributes the runtime narrative dropped.

### §2-discipline analysis

**§2.1 five-axis decomposition.** The tension touches Control Plane (HITL gate is CP-axis primitive; placement is CP-owned config) + Operational Discipline (`hitl.*` spans are OD-axis ingestion target via D6) + Information Substrate (audit-entry composition at step 4h is the IS-anchored fact carrier for HITL response data). The runtime spec narrative attempted to telescope OD-axis attribute-schema design into runtime spec authoring; the canonical chain has the OD schema authority at ADR-D5 / D6, NOT at runtime spec narrative. **Cross-axis authority inversion is the root cause** of the divergence.

**§2.2 probabilistic-deterministic boundary.** All affected surfaces (span attribute schemas + audit-entry composition + carrier imports) live on the deterministic side. The "what does the gate know about itself" is observability ground truth — must be carrier-declared and chain-canonical. Reliability of `hitl.*` ingestion at OD consumers depends on the canonical 4-span shape with stable attribute names; the runtime narrative's invented 2-span shape would break OD-side dashboards built against ADR-D6 §1.2.

**§2.3 decision ordering.** The `hitl.*` 4-span schema is **F-level** (anchored at ADR-D5 v1.3 §1.8 — foundational HITL primitive observability surface; iter-3 P3c-CK adversarial review F2-iter2-02 resolution committed the v1.3 attribute set under operator-selected Reading 1). Attribute-name commitments at F-level cannot be re-derived at D/I downstream artifacts. The runtime narrative at v1.9 effectively attempted an F-level redefinition without going through ADR revision — this is the X-AL-3 surface implicated at Q4 below.

**§2.5 cross-axis integration verification.** Verify: do the canonical-name + canonical-4-span readings satisfy what the runtime composer body ACTUALLY needs to express? Cross-walk:

| Runtime composer semantic need | Canonical chain placement |
|---|---|
| Which placement triggered the gate (PRE_ACTION / SUB_AGENT_BOUNDARY) | `hitl.invocation.placement` attribute on `hitl.invocation.opened` span (ADR-D5 §1.8 row 2) — composer should OPEN this span when gate evaluates true (not drop it) |
| Which response palette was offered (full vs restricted) | NOT in canonical 4-span schema. Semantic content lives at `compose_hitl_response_audit` audit-entry composition at step 4h (the palette membership is implicit in the `response` field value ∈ {approve, edit, reject, respond}; for restricted-palette case per NOTE 6-iv future arc, the audit entry's `audit.policy.*` namespace via ADR-D6 §1.2 + C-CP-20 §20.4 carries the policy state). **Span-attribute duplication is not required and breaks Pattern P1 mechanical-alignment.** |
| Gate evaluation outcome (response received / timed out / audit-compose failed) | Canonical: response → `hitl.invocation.responded` span (with `.response.class` carrying `gate_result.response` value); timeout → `hitl.invocation.timed_out` span (DEDICATED span per ADR-D5 §1.8 row 4 with `.duration_ms` + `.degradation_mode_applied`); audit-compose failure → OTel `Span.set_status(StatusCode.ERROR)` + `Span.record_exception(...)` on `hitl.gate.evaluated` (semconv-canonical for error outcomes; no custom `.outcome` attribute needed). |
| Operator's response (approve/edit/reject/respond) | `hitl.response.class` on `hitl.invocation.responded` (ADR-D5 §1.8 row 3); same semantic as runtime narrative's `.response_class` but at the canonical attribute name |
| Response latency | `hitl.response.latency_ms` on `hitl.invocation.responded` (ADR-D5 §1.8 row 3) |
| Response summary content hash | `hitl.response.summary_hash` on `hitl.invocation.responded` (ADR-D5 §1.8 row 3) — NEW useful attribute the runtime narrative drops; conforming pulls it in |

Every semantic the runtime composer needs is already canonically placed at the upstream chain. The runtime narrative's invented attribute set was unnecessary AND broke the canonical observability schema.

### Per-question chain-grounded recommendations

**Q1 — Sub-issue (1) rename drift resolution.**

**Recommendation: (a) Runtime spec narrative correction. [HIGH]**

Chain reading is unambiguous: ADR-D5 v1.3 §1.8 row 3 + CP carrier + CP spec v1.2 §20.6 all declare `hitl.response.class` / `.latency_ms` / `.summary_hash` on the `hitl.invocation.responded` span. The runtime narrative's `hitl.invocation.responded.response_class` / `.response_latency_ms` is leaf-level divergence from the canonical CP/OD-axis attribute schema. Conform the runtime narrative; do NOT reverse-rename at the CP carrier (which would require ADR-D5 revision + cascade through OD spec + CP spec + carrier — heavy scope to fix a leaf-side authoring error).

Sub-action: also add `hitl.response.summary_hash` emission to AC #8 (the canonical schema row carries it; the runtime narrative dropped it; conforming pulls it in cleanly).

**Q2 — Sub-issue (2) missing carrier slots resolution.**

**Recommendation: (b) Spec narrative correction — restore canonical 4-span shape + audit-entry-anchored fact carriers. [HIGH]**

The semantic content the runtime narrative tried to attach to invented attribute names is already canonically placed at the chain-upstream schema:

- **`.placement` content** → use canonical `hitl.invocation.placement` attribute on `hitl.invocation.opened` span (ADR-D5 §1.8 row 2). Composer body amendment: at step 4f when AskUserQuestion invoked, open `hitl.invocation.opened` span (currently dropped from runtime narrative's 2-span shape); attach `hitl.invocation.placement = placement.position.value` per canonical row. This restores the canonical 4-span hierarchy: `gate.evaluated → invocation.opened → invocation.responded` (or `→ invocation.timed_out` on timeout).
- **`.response_palette` content** → audit-entry-anchored at step 4h via `CPAuditLedgerEntry.response` field (the actual response value is bounded by the palette set offered; for future cross-trust-boundary palette restriction per NOTE 6-iv, the policy-derived restriction state lives at `audit.policy.*` namespace via ADR-D6 §1.2 + C-CP-20 §20.4 — already canonical). NO span-attribute duplication needed; NO new H_T design surface.
- **`.outcome="timeout"` / `="audit-compose-failed"` content** → for timeout, canonical `hitl.invocation.timed_out` span (DEDICATED span at ADR-D5 §1.8 row 4) with `.duration_ms` + `.degradation_mode_applied`; for audit-compose failure, OTel-canonical `Span.set_status(StatusCode.ERROR)` + `Span.record_exception(typed_error)` on the `hitl.gate.evaluated` span. Semconv-canonical; no custom carrier slot.

This recommendation achieves: (i) carrier-canonical compliance (Clause A of the contradiction); (ii) no new H_T design surface (X-AL-3 honored); (iii) no carrier extension (no cascade to CP spec / ADR-D5); (iv) richer observability than the runtime narrative (4 spans vs 2; canonical `hitl.response.summary_hash` pulled in).

Rejecting (a) carrier extension: would require ADR-D5 v1.3 → v1.4 revision + ADR-D6 §1.2 + OD spec + CP spec v1.2 §20.6 + CP carrier + U-CP-46 plan + retirement-event impact — a 6-artifact cascade for what is, on examination, a runtime narrative authoring error that the canonical chain already handles cleanly. Heavy scope without functional benefit.

Rejecting (c) outcome-only solution: (c) is a subset of (b); (b) is strictly more complete. Treat (c) as the §14.8.5 fail-class-row sub-correction within (b).

**Q3 — Authority-chain reading.**

**Recommendation: (a) CP-owner reading via D6 ingestion (OD-spec-authoritative for `hitl.*` schema; CP emits per). [HIGH]**

`harness-cp/CLAUDE.md` §1.4 is dispositive: "CP and OD share authority over several namespaces (`hitl.*`, …) via the D6 ingestion pattern: CP emits, OD ingests. Authoritative schema lives at OD spec; CP emits per OD's canonical attribute set." The OD-spec-as-authoritative-schema reading combined with ADR-D5 v1.3 §1.8 (the foundational F-level commitment) gives the canonical chain: ADR-D5 → ADR-D6 → OD spec → CP carrier → runtime composer. Runtime spec narrative is leaf in this chain for `hitl.*` schema commitments and cannot redefine attribute names canonical upstream.

This reading is reinforced by ADR-D5 v1.3 iter-3 F2-iter2-02 resolution (Reading 1 canonical pass-through retired `hitl.gate.tool` + `hitl.gate.mcp_server` attribute names — the F-level discipline that says "attribute-name commitments at the canonical span are load-bearing, not interchangeable").

**Q4 — X-AL-3 evaluation for sub-issue 2.**

**Recommendation: confirm retroactive X-AL-3 surfacing; resolve via narrative-correction NOT carrier-extension; do NOT escalate to silent-absorption-violation finding. [HIGH]**

Per workspace `CLAUDE.md` invariant I-2 + Meta-Architecture §7 X-AL-3 ("No silent H_T design extension at Phase 7 execution"), the v1.9 C-RT-18 spec authoring at HEAD `2685774` introduced attribute names that would have been new canonical surface IF interpreted as design extension. **However** — and this is the chain-grounded mitigation — the same v1.9 authoring at §14.8.5 declared the CP carrier canonical + forbade hand-coded names. Read coherently, the §14.8.5 commitment makes the §14.8.2 hand-coded names *non-canonical authoring drift* rather than *design extension* — the author intended carrier-canonical emission and authored placeholder names in narrative thinking the carrier would carry them. Adversarial review missed the cross-check; that's an adversarial-review-effectiveness finding (Q6), not a v1.9-spec-authoring-violation finding.

**The retroactive surfacing this session** is the proper X-AL-3 honor: surface the divergence before any code lands; halt; conform the leaf artifact to the chain. **Sub-issue 2 resolution via (b) narrative-correction does NOT extend H_T design** — every canonical attribute and span is already chain-anchored at ADR-D5 v1.3 §1.8.

Sub-action: at v1.10 → v1.11 spec amendment, add a brief change-note paragraph documenting this fork-resolution path so future adversarial review has a reference for "missed-attribute-carrier-cross-check" as a known finding category.

**Q5 — Cascade scope at amendment landing.**

**Recommendation: single-arc co-publication (runtime spec v1.10 → v1.11 + plan v2.8 → v2.9 in one operator-ratification turn). [HIGH]**

Per Q2's (b) recommendation (no CP carrier or ADR-D5 amendment required), the cascade scope is contained to runtime spec narrative + plan AC absorption:

| Affected artifact | Amendment shape |
|---|---|
| `design-substrate/Spec_Harness_Runtime_v1.md` v1.10 → v1.11 | §14.8.2 step 4e (drop `.placement` / `.response_palette` hand-coding; set carrier-canonical `hitl.gate.{level,persona_tier,required}` from cell + binding); §14.8.2 step 4f-bis (NEW: open `hitl.invocation.opened` span; set `hitl.invocation.placement` per canonical); §14.8.2 step 4g (rename to canonical `hitl.response.class` / `.latency_ms` / `.summary_hash` on `hitl.invocation.responded`); §14.8.2 step 4f timeout-path (open `hitl.invocation.timed_out` span per canonical; drop `.outcome="timeout"`); §14.8.5 hierarchy diagram (restore 4-span shape per ADR-D5 §1.8); §14.8.5 fail-class rows (use OTel Span.set_status + record_exception, drop custom `.outcome` attribute); change-note adds X-AL-3 retroactive-surfacing fork-resolution narrative |
| `.harness/phase-2-session-3-track-a-atomic-decomposition.md` plan v2.8 → v2.9 | AC #7 + AC #8 narrative absorption per spec v1.11 §14.8.2 + §14.8.5; AC #11 multi-placement test design absorption if multi-span-coverage assertion shape changes; AC #13 unchanged (cite carrier — now satisfied without contradiction) |
| Workspace `CLAUDE.md` §2.3 contract count row for runtime spec | version bump v1.10 → v1.11 |

Single-arc co-publication keeps the surface coherent at landing.

**Q6 — Systemic-pattern observation.**

**Recommendation: confirm threshold crossed; surface to operator as systemic-pattern finding for skill-body extension consideration (NOT a same-arc absorption). [MODERATE-HIGH]**

4 adversarial-review-missed defects at U-RT-58/59/60 all share the structural pattern: CP↔runtime cross-axis attribute / binding surface where a runtime-spec narrative diverged from a CP-side canonical (carrier / spec / ADR). This crosses the 3-arc systemic-pattern threshold per `harness-adversarial-reviewer` skill §6.

Recommendation surface (operator decides scope):

- **(a) `harness-adversarial-reviewer` skill body extension** — at pre-impl review of any runtime-spec C-RT-NN contract that cites a CP-side `*_NAMESPACE_SCHEMA` carrier or a CP-side ADR (D5/D6/D1), MANDATE a "carrier-vs-narrative attribute-name cross-check" diff: enumerate every `<namespace>.<attr_name>` reference in the spec narrative; verify each is declared at the carrier; verify each canonical-carrier attribute the narrative claims to set is named correctly per the carrier; flag any extra (narrative names not in carrier — potential X-AL-3) or missing (carrier names the narrative drops — potential observability cost). This is the diff that would have caught this fork at HEAD `c783b06`.
- **(b) `phase-7-implementation` skill body extension** — at Step 2 (read cited spec contract), add an explicit "verify cited attribute names exist at the cited carrier" check; halt before composer code if narrative ↔ carrier divergence detected. This is a hard halt at the latest possible point before code lands.
- **(c) `spec-writer` skill body extension** — at any spec revision touching attribute names, MANDATE the carrier diff. This is the earliest catch (prevents the v1.9-style narrative drift at authoring time).

(a)+(c) together would have prevented this fork from being filed. (b) is the defense-in-depth halt that did catch it (this session). All three are defensible; operator may pick scope.

**This skill-body-extension recommendation is NOT a same-arc absorption** — it is a follow-on arc surface that operator schedules independently of the U-RT-60 implementation arc resumption. Sub-action: file a Class 3 informational record at fork-resolution landing time documenting the recommendation for future skill-revision work.

### Tiebreaker check

The single verifiable fact that, if confirmed, makes this recommendation determinate:

> **Confirm:** No ADR revision between ADR-D5 v1.3 (2026-05-11) and the present (2026-05-21) has redefined the `hitl.gate.evaluated` attribute set OR added `.placement` / `.response_palette` / `.outcome` attributes to any `hitl.*` span.

Verification command:

```
$ grep -nE "hitl\.gate\.evaluated\.placement|hitl\.gate\.evaluated\.response_palette|hitl\.gate\.evaluated\.outcome" design-substrate/ADR-D5.md design-substrate/ADR-D6_v1_2.md
# expected: no matches — confirming the runtime narrative attribute names are not introduced at any ADR revision postdating ADR-D5 v1.3 §1.8
```

If verification finds a postdated ADR introduction, the recommendation flips to Q2 (a) carrier extension (because the design extension already cleared at ADR level). If verification confirms no postdate, Q2 (b) narrative correction is determinate.

The recommendation touches LEAF artifacts only (runtime spec + plan); no F-ADR / D-ADR / CLAUDE.md anti-leakage rule is amended. Per skill §4A.2 step 5, this does NOT require explicit operator load-bearing-artifact sign-off beyond the standard PROPOSING → RATIFIED transition.

### Fork class (per `Project_Workflow_v1_8.md` §2.7.6)

**Class 1 (halt-execution) — confirmed.**

| Property | Value |
|---|---|
| Trigger | Architectural defect: runtime spec contract self-contradicts at attribute-name granularity; canonical chain commitment violated at leaf artifact |
| Behavior | HALT Phase 7 sub-phase 7b U-RT-60 implementation execution; cannot proceed until runtime spec amendment lands |
| Routing | Phase 5 spec revision-pass at design-phase workspace (in-CLI per `[[design-substrate-divergence]]`) |
| Recording | This record + Phase 7 sub-phase log + workspace `CLAUDE.md` §2.3 contract row version bump |
| Operator surface | Required — operator ratifies the 6-Q recommendation chain (PROPOSING → RATIFIED) before spec-writer arc opens |

**Status transition.** AUTHORING → **PROPOSING** at this recommendation filing. Awaiting operator ratification turn before status → RATIFIED + spec-writer arc opens.

---

*End of `systems-architect` mode 3 recommendation. Per skill §4A.4: this is a recommendation, NOT a decision. Operator holds decision authority.*

---

## Operator ratification

**Ratified 2026-05-21 by operator at AskUserQuestion turn (this session).** Selection: "Ratify all 6 Qs as recommended." No counter-proposal raised. Chain reading accepted as authoritative.

**Ratified disposition (per `systems-architect` mode 3 recommendation above):**

| Q | Ratified resolution |
|---|---|
| Q1 | (a) Runtime spec narrative correction — conform to canonical `hitl.response.{class,latency_ms,summary_hash}` per ADR-D5 v1.3 §1.8 row 3 |
| Q2 | (b) Restore canonical 4-span shape + audit-entry-anchored fact carriers — open `hitl.invocation.opened` (placement attr lives there per row 2); open `hitl.invocation.timed_out` for timeout (dedicated span per row 4); use OTel `Span.set_status(StatusCode.ERROR)` + `Span.record_exception(...)` for audit-compose failure (semconv-canonical, drops custom `.outcome` attribute) |
| Q3 | (a) CP-owner reading via D6 ingestion — OD spec authoritative for `hitl.*` schema per `harness-cp/CLAUDE.md` §1.4; CP carrier emits per |
| Q4 | Confirmed retroactive X-AL-3 surfacing — v1.9 authoring at HEAD `2685774` was authoring drift (not design extension) since §14.8.5 declared carrier canonical; honor X-AL-3 by conforming leaf to chain, not extending carrier. No silent-absorption-violation finding filed against v1.9 authoring. |
| Q5 | Single-arc co-publication — runtime spec v1.10 → v1.11 + plan v2.8 → v2.9 in one operator-ratification turn (cascade scope contained to leaves; CP carrier + ADR-D5/D6 untouched) |
| Q6 | Systemic-pattern threshold confirmed crossed — 4 adversarial-review-missed defects at U-RT-58/59/60 all at CP↔runtime cross-axis attribute/binding surface. Surfaced as follow-on arc for `harness-adversarial-reviewer` / `phase-7-implementation` / `spec-writer` skill body extension; operator schedules independently of U-RT-60 resumption. File Class 3 informational record at fork-resolution landing time. |

**Status transition.** PROPOSING → **RATIFIED**. Next: `spec-writer` skill opens runtime spec v1.10 → v1.11 Form A NOTE-form absorption arc; `implementation-planner` co-publishes plan v2.8 → v2.9 absorbing AC #7 + AC #8 (+ AC #11 if multi-span coverage assertion shape changes). U-RT-60 implementation arc HALTED state preserved at HEAD `1e4c59d` (fork-filed) → `3d5a370` (recommendation) → this commit (RATIFIED) → spec-writer arc → plan-writer arc → `phase-7-implementation` resumes against the re-clearance state. The implementation-arc resumption is APPLIED status; full retirement at U-RT-60 landing event per Phase 7d batch 8.
