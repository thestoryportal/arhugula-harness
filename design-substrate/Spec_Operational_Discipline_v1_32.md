# `Spec_Operational_Discipline` v1.32 — delta over v1.31

**Filed:** 2026-07-13
**Authoring authority:** Phase 7 — R-FS-2 Wave 4 standalone `B-*` arc **B-19-BREAKER-AMBIENT-ATTRS** (`.harness/r-fs-2-final-closure-implementation-plan-v1.md` §5)
**Predecessor:** `Spec_Operational_Discipline_v1_31.md` (v1.31 — C-OD-24 §24.7 `audit.rotation_correlation_id` namespace attribute)
**Revision shape:** Delta-only spec file per workspace `CLAUDE.md` §2.3 OD spec row convention. v1.31 + v1.30 + ... + v1 file bodies PRESERVED VERBATIM. v1.32 carries this change-note + the C-OD-07 §7.1 ADDITIVE amendment only.

---

## Change-note (v1.31 → v1.32)

**Re-introduces `breaker.cause` + `breaker.cooldown_ms` under the canonical `harness.breaker.*` schema, per operator discretion.** CP spec v1.1 (`Spec_Control_Plane_v1_2.md` §"Attribute set reconciliation" line 72) recorded a deliberate drop of these two CP-side ambient attributes when the 4-attribute CP set (`breaker.key` / `breaker.cause` ∈ `{rate_limit, auth_failure, 5xx_streak, capability_shortfall}` / `breaker.cooldown_ms` / `breaker.state`) was replaced by the OD 7-attribute canonical event set — flagged as a "semantic-loss note" and explicitly forward-flagged as operator-discretionary re-introduction, tracked at `.harness/post-phase-8-forward-register.md` Surface B-19 and resolved at Phase 7 R-FS-2 Wave 4.

**Grounding before this amendment (`.harness/b19-breaker-ambient-attrs-redundancy-analysis.md`, this session).** A full source sweep (CP/OD/runtime/AS/IS/CXA, the CLI, dashboard tooling) found zero production consumers that read breaker state ambiently (outside the event stream) for either attribute today; the one real breaker-state reader (`retry_breaker_fallback.py`'s `should_attempt()` gate) needs only a boolean open/closed check. The operator elected to build ahead of a known consumer (`AskUserQuestion`, 2026-07-12) — a deliberate FULL-SPEC-completeness choice, not a consumer-driven one.

**Event attributes, not true ambient state.** The original CP-side 4-attribute set described *ambient* breaker state (continuously queryable: "what is the current cause while open", "how much cooldown remains"). Building genuine ambient state would require new untracked internal machinery (a clock, an open-timestamp) the breaker state machine deliberately does not carry (`retry_breaker.py`'s `BreakerStateMachine` docstring: "the state machine does not hold a clock"). Per the redundancy analysis's own finding that no consumer needs continuous polling, this amendment instead extends the existing `breaker.tripped` **event** schema with two attributes fully determined at the trip instant: `harness.breaker.cause` (the classified reason, when known) and `harness.breaker.cooldown_ms` (the cooldown *duration* set for this trip — CP v1.1's semantic-loss note itself glosses `breaker.cooldown_ms` as "cooldown duration", not "remaining cooldown"; no clock is required to compute a static duration at emission time).

**`harness.breaker.cause` is a typed, currently-vacuous slot — documented honestly, not silently.** Build-time grounding (this session) traced all three failure-classification layers reachable at a real breaker-trip call site in `retry_breaker_fallback.py`:

1. The capability-shortfall pre-check (`_required_capabilities` / `missing_caps`) fires *before* the breaker is ever consulted — a capability-shortfall candidate never reaches `breaker.record_failure()`, so `capability_shortfall` is structurally unreachable at a trip site in the current architecture.
2. The fail-fast branch (`_classify_provider_exception` returning `None`) only discriminates `LLMDispatchProviderUnreachableError` / `LLMDispatchPayloadShapeError` — both configuration/shape conditions, neither cleanly `auth_failure`.
3. The transient branch (`TRANSIENT_RETRY`) is genuinely undifferentiated — `ProviderTransientError`'s own docstring lumps network / rate-limit / 5xx together with no further split, and the runtime's only real auth-vs-transient discriminator (`ProviderAuthError` / `_classify_anthropic_ping_failure`, `_classify_openai_ping_failure` in `providers.py`) is a **bootstrap ping-time** classifier only — it never reaches the per-step dispatch loop.

None of the four spec-committed values (`rate_limit` / `auth_failure` / `5xx_streak` / `capability_shortfall`) is therefore honestly derivable at a real trip site today. Building a fine-grained provider-exception classifier to make `cause` non-vacuous is out of scope for this arc — the redundancy analysis already forecloses building speculative infrastructure ahead of a consumer, and a classifier is exactly that. Per operator decision (second `AskUserQuestion`, 2026-07-12, surfaced once this build-time fact was established): amend the schema **once**, for both attributes together — `cooldown_ms` populated, `cause` present as the typed 4-value enum slot and always `None` today. A follow-on classifier arc is registered (not built) at `.harness/post-phase-8-forward-register.md` if `cause` is ever needed non-vacuously.

**No new ADR.** This is an OD-side schema-expansion the CP v1.1 semantic-loss note itself named as the correct future path ("re-introducing `breaker.cause` and `breaker.cooldown_ms` ... would require OD C-OD-07 §7.1 schema expansion"). No ADR-D6 commitment is revised — the `harness.breaker.*` namespace remains substrate-anchored at `c9-reliability-recovery` SKILL.md per F2-16 closure; this amendment only widens its attribute count.

**CP-side composition surface — code only, no CP spec delta owed.** The current CP spec head (`Spec_Control_Plane_v1_96.md`) no longer re-tables C-CP-03 §3.5's `harness.breaker.*` namespace mirror in prose (delta-only convention; last substantively defined at `Spec_Control_Plane_v1_3.md`, preserved verbatim since). The load-bearing enforcement surface is the **code**-level composition mirror — `harness_cp.retry_fallback_namespace.HARNESS_BREAKER_NAMESPACE_SCHEMA` + `harness_cp.cp_namespace_export_manifest`'s `attribute_count` entry for `"harness.breaker.*"` + the runtime's `verify_harness_breaker_namespace_inversion()` cardinality check (`harness_runtime.lifecycle.od_cp_wiring`) — all updated in the same bundled-absorption PR as this spec delta, per root `CLAUDE.md` §11.4. No CP spec file edit is owed.

---

## §7.1 Nine-attribute schema (AMENDS v1's seven-attribute table, ADDITIVE)

Extends `spec_operational_discipline_v1_1.md` §7 C-OD-07 §7.1 (preserved verbatim through v1.31) with two new optional attributes. The seven v1-canonical attributes are UNCHANGED:

| Attribute | Type | Source | Meaning |
|---|---|---|---|
| `harness.breaker.scope` | enum string ∈ `{per_model, per_provider}` | `c9-reliability-recovery` SKILL.md (s12 §7.7) | The breaker scope |
| `harness.breaker.from_state` | enum string ∈ `{closed, open, half_open}` | `c9-reliability-recovery` SKILL.md (s12 §7.7) | Source state |
| `harness.breaker.to_state` | enum string ∈ `{closed, open, half_open}` | `c9-reliability-recovery` SKILL.md (s12 §7.7) | Destination state |
| `harness.breaker.trigger_count` | int | `c9-reliability-recovery` SKILL.md (s12 §7.7) | Consecutive failures that tripped the breaker (when `from=closed`, `to=open`) |
| `harness.breaker.permanent_fail_repeats` | bool | `c9-reliability-recovery` SKILL.md (s12 §7.7) | Whether this trip is from repeated C5 permanent-fail-exits — the C10 gating signal |
| `harness.breaker.tool_id` | string | `c9-reliability-recovery` SKILL.md (s13 §4.10 (e)) | Specific tool ID the failures correlate with (when scope is per-model and failures correlate with a specific tool) |
| `harness.breaker.model_version` | string | `c9-reliability-recovery` SKILL.md (s13 §4.10 (e)) | Specific model version (composes with judge-drift discipline per s11 §4.1) |

**NEW at v1.32 (both optional, populated only on a trip transition — `to_state = open`; absent on recovery transitions `half_open → closed` and on the caller-driven `open → half_open` cooldown-elapsed transition, neither of which is a trip):**

| Attribute | Type | Source | Meaning |
|---|---|---|---|
| `harness.breaker.cause` | enum string ∈ `{rate_limit, auth_failure, 5xx_streak, capability_shortfall}`, or attribute absent | This spec (v1.32); CP v1.1 §"Attribute set reconciliation" line 72 names the domain verbatim | The classified trip-cause, when known. **Vacuous-today, honestly documented**: no call site in the current runtime can non-speculatively populate any of the four values (see change-note); the attribute is present in the schema (forward-compatible typed slot) and absent from every emitted event until a follow-on classifier arc supplies real signal. |
| `harness.breaker.cooldown_ms` | int, or attribute absent | This spec (v1.32); derived from `BreakerStateMachine.cooldown_seconds * 1000` at trip time | The cooldown **duration** (not "remaining cooldown" — CP v1.1's own gloss) set for this trip. Fully determined at the trip instant; no clock or ambient-state tracking required. Present on every real trip event (`to_state = open`). |

**Optional-attribute set is now five** (`permanent_fail_repeats` / `tool_id` / `model_version` / `cause` / `cooldown_ms`); the four non-optional attributes (`scope` / `from_state` / `to_state` / `trigger_count`) are UNCHANGED.

**Cardinality.** Attribute count 7 → 9. Downstream code-level cardinality checks (CP's `attribute_count` declaration for `"harness.breaker.*"`, the `CP_EXPORTED_ATTRIBUTE_COUNT` sum, and the runtime's `verify_harness_breaker_namespace_inversion()` bootstrap check) are updated in the same PR — see the change-note's "CP-side composition surface" paragraph.

**Scope discipline.** v1.32 amends ONLY the C-OD-07 §7.1 attribute table (adds `cause` + `cooldown_ms`). §7.2 through §7.7 (event name, sampling discipline, C10 subscription discipline) are PRESERVED VERBATIM — the two new attributes ride the existing `breaker.tripped` event; no new event name, no new sampling rule. All other C-OD-01..C-OD-34 contract surfaces are PRESERVED VERBATIM. v1.31 + earlier lineage PRESERVED VERBATIM per the delta-only-spec-file convention except this §7.1 additive amendment.

**PRD requirement(s) satisfied.** R-OD-02 (unified span schema — additive attribute declaration); R-OD-03 (sampling discipline — unchanged, still always-sampled at `breaker.tripped`).

**ADR commitment(s) honored.** ADR-D6 v1.2 §1.2.1 (`harness.breaker.*` substrate anchor at `c9-reliability-recovery`) — unchanged, only the attribute count widens.

**Cross-reference.** CP spec v1.1 (`Spec_Control_Plane_v1_2.md`) §"Attribute set reconciliation" (the semantic-loss note this amendment resolves) + §"F-CP-01 attribute semantic-loss re-evaluation" (the operator-discretion flag this amendment exercises).

---

## Filing footer

| Field | Value |
|---|---|
| Version | v1.32 (ADDITIVE §7.1 amendment — `harness.breaker.cause` + `harness.breaker.cooldown_ms`; v1.31 + earlier PRESERVED VERBATIM) |
| Trigger | R-FS-2 Wave 4 `B-19-BREAKER-AMBIENT-ATTRS` — operator-ratified BUILD via `AskUserQuestion` (2026-07-12), against the arc's own grounded skip-and-close recommendation; scope narrowed to a single amendment covering both attributes via a second `AskUserQuestion` (2026-07-12) once build-time grounding showed `cause` is vacuous-today |
| Supersedes | None — additive schema-expansion amendment |
| Scope of revision | NARROW: NEW `cause` + `cooldown_ms` attributes at C-OD-07 §7.1. No file edit to v1.31 or earlier; downstream readers apply this table as the current canonical §7.1 body. |
| Contract change | ADDITIVE — 2 new optional attributes; no field removed, no existing attribute's type/cardinality changed |
| Cross-axis cascade | CP composition-mirror code (`retry_fallback_namespace.py`, `cp_namespace_export_manifest.py`) + runtime cardinality check (`od_cp_wiring.py`) updated in the same bundled-absorption PR; no CP spec file edit owed (current CP spec head does not re-table this namespace in prose) |
| Authority anchor | Workspace `CLAUDE.md` §8 I-1 byte-exact discipline + §11.4 bundled-absorption-arc convention + `.harness/r-fs-2-final-closure-implementation-plan-v1.md` §5 Wave 4 |
| Predecessor | v1.31 (C-OD-24 §24.7 `audit.rotation_correlation_id` namespace attribute) |
| Successor | Unassigned — next operator-discretion arc |
