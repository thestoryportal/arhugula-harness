# Class 1 Tension — C-RT-18 §14.8.2/§14.8.5 HITL span attribute carrier drift

**Filed:** 2026-05-21 — Phase 7 sub-phase 7b U-RT-60 implementation arc OPEN (executed under `phase-7-implementation` skill from HEAD `e3b193f`). Surfaced at Step 2 of the unit consumption shape (read spec contract) when cross-checking AC #7 + AC #13 against the canonical CP carrier at `harness-cp/src/harness_cp/audit_hitl_span_namespace.py`.
**Surfaced by:** `phase-7-implementation` skill §6 halt condition (cited spec contract section under-specifies / self-contradicts the surface). Routed here via `phase-7-back-flow-routing` skill §4.1 Step 1 classification.
**Status:** **AUTHORING → PROPOSING** (pending systems-architect mode 3 recommendation + operator ratification).
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

*To be appended at the next skill invocation per `systems-architect` skill mode 3 against the 6-question chain above. Per skill §4A.2: chain-grounded against canonical authority chain at workspace `CLAUDE.md` §1.3.*

(awaiting systems-architect mode 3 pass)

---

## Operator ratification

*To be appended at operator AskUserQuestion turn after systems-architect recommendation lands.*

(awaiting operator decision)
