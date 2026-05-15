# Product Requirements Document v1.1

## Status block

| Field | Value |
|---|---|
| Artifact | `PRD_v1_1.md` |
| Status | **Proposed** — F2-12 cascade Step 4 revision pass; promotion to Accepted at cascade close (post-Step 6 plan v2.2 filings) |
| Version | v1.0 (2026-05-13) → v1.0.1 (2026-05-13 — substrate-citation refinement, no requirement-level change) → **v1.1 (2026-05-14; F2-12 cascade Step 4 revision pass absorbing ADR-D1 v1.2 + ADR-D6 v1.2 + ADD v1.3 per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade Step 4 row)** |
| Date | 2026-05-14 (v1.1 revision pass) |
| Phase | 4 — PRD authoring (post-Phase-3 F2-12 cascade Step 4 per `Project_Workflow_v1_7.md` §4.1.2; cascade-driven revision pass under `prd-author` SKILL.md §7 revision-pass sub-mode + Workflow v1.7 §7 fidelity-grammar discipline) |
| Skill | `prd-author` (revision-pass sub-mode per SKILL.md §7) at v1.1 |
| Promotion path | Accepted at F2-12 cascade close |
| Source-set | ADD v1.3 (cascade Step 3 output absorbing D1 v1.2 + D6 v1.2) + ADR-D1 v1.2 + ADR-D6 v1.2 + `F2-12_Closure_Path_Execution_Kickoff.md` + `F2-12_Council_Deliberation_Output.md` (cascade Step 1 substrate) + `Persona_Document_v1.md` (read-only context) |
| Entry authorization | `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 cascade Step 4 routing + ADD v1.3 §6.3.1 cascade Step 4 row + `Project_Workflow_v1_7.md` §3.1 Status: Proposed preservation discipline |
| Exit gate | F2-12 cascade Step 5 (CP spec v1.3 + OD spec v1.3 revision passes) consuming this PRD v1.1 as substrate |

## Change-note (v1.0 → v1.1)

**Scope of revision.** F2-12 cascade Step 4 revision pass per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade execution path table row 4. The revision pass absorbs the ADR-D1 v1.2 + ADR-D6 v1.2 substantive amendments into the PRD's observable-behavior surface and closes the [CF-1] F2-12 carry-forward declaration. Three requirement-level amendment sites + one carry-forward closure + one traceability matrix update:

| Site | Amendment shape | Substrate source |
|---|---|---|
| R-CP-04 (workflow lifecycle event surface) | Observable behavior + ADR citation + Acceptance criterion paragraphs revised to surface the 4-attribute `engine.*` namespace + 6-attribute `retry.*` namespace as production-time-operator-visible distinguishing dimensions; lifecycle event class enumeration extends from 8 → 8 (terminology correction only: retry-attempt now emits BOTH parent event AND child span per D6 v1.2 §1.2.2) | ADR-D1 v1.2 §1.1.1; ADR-D6 v1.2 §1.2 + §1.2.2 |
| R-CP-07 (replay-resumption semantics) | Observable behavior + ADR citation + Acceptance criterion paragraphs revised to surface `engine.replay_disposition` 5-value enum as production-time-operator-visible discriminator; per-engine-class replay-emission discipline visibility added | ADR-D1 v1.2 §1.1.1 + §1.1.2 |
| R-OD-05 (cost-attribution per span at run cost-attribution surface) | Observable behavior + ADR citation + Acceptance criterion paragraphs revised to surface the per-attempt cost-attribution discipline (cost accrues per retry attempt; not aggregated across attempts; `deterministic_replay` re-reads contribute zero) and dedup-algorithm correctness as production-time-operator-visible cost-correctness property | ADR-D6 v1.2 §1.5 + §1.5.1 + §1.5.3 |
| [CF-1] F2-12 carry-forward | Status revised from 🔄 Deferred-acknowledged → **✅ CLOSED at cascade Step 4 absorption**; PRD impact updated to record the requirement-level absorptions at R-CP-04 + R-CP-07 + R-OD-05; Forward routing collapsed into closure-execution-path record | ADD v1.3 §6.3.1 cascade Step 4 closure declaration |
| §[traceability] matrix | D1 v1.1 → D1 v1.2 row label update; D6 v1.1 → D6 v1.2 row label update; cell marks preserved (no new requirements added; no requirements removed) | Status block source-set update |

Workflow v1.7 §7 fidelity-grammar discipline applied across all amendment sites: no Pattern P1 cross-artifact name drift (D1 v1.2 §1.1.1 4-attribute namespace canonical at source ADR; PRD requirement ADR citations consistent with ADD v1.3 + ADR source files); no Pattern P2 verbatim-claim-contradicted (all "per ADR-X v1.2 §Y" claims verify against source files at `/mnt/user-data/outputs/`); citation anchors substrate-verified per Workflow v1.7 §2.3.3.1 clause (iii). `prd-author` SKILL.md §4 four sub-disciplines verified inline at each amended requirement: trace-back at section level ✅; non-contradiction with ADD v1.3 ✅; observable framing (no implementation-grade leakage; behavior framed at observer surface) ✅; no-architecture-introduction (PRD inherits architecture from ADD v1.3 + ADR-D1 v1.2 + ADR-D6 v1.2; no new architectural commitments introduced) ✅.

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` blocked until F2-12 cascade close (post-Step 6 plan v2.2 filing). PRD v1.1 enters cascade Step 5 (CP spec v1.3 + OD spec v1.3 revision passes) as substrate input.

**Sections preserved verbatim from v1.0 (and v1.0.1 if applicable).** Front-matter §Shape declaration; Front-matter §Persona summary; Front-matter §Scope and out-of-scope; §1 Control plane requirements R-CP-01, R-CP-02, R-CP-03, R-CP-05, R-CP-06, R-CP-08, R-CP-09, R-CP-10, R-CP-11, R-CP-12 (only R-CP-04 + R-CP-07 amended at v1.1); §2 Information substrate requirements R-IS-01, R-IS-02, R-IS-03, R-IS-04 (no v1.1 amendments); §3 Action surface requirements R-AS-01 through R-AS-07 (no v1.1 amendments); §4 Operational discipline requirements R-OD-01, R-OD-02, R-OD-03, R-OD-04, R-OD-06, R-OD-07, R-OD-08 (only R-OD-05 amended at v1.1); §[carry-forwards] [CF-2] Workflow §7 substrate-skill propagation (no v1.1 change); §[coherence pass] Audits 6.1–6.5 + aggregate (preserved at v1.0 form; v1.1 amendment sites verify inline per Workflow v1.7 §7 fidelity-grammar discipline, not via re-running v1.0 audit harness).

**Changes inline.** Status block (Version line extended with v1.1 entry; Date line extended; Source-set updated ADD v1.2 → v1.3 + D1 v1.1 → v1.2 + D6 v1.1 → v1.2 + F2-12 cascade citations; Entry authorization updated; Exit gate revised to cascade Step 5). This Change-note (v1.0 → v1.1) section. R-CP-04 (all four paragraphs) revised per v1.1 amendment table above. R-CP-07 (all four paragraphs) revised per v1.1 amendment table above. R-OD-05 (all four paragraphs) revised per v1.1 amendment table above. [CF-1] F2-12 carry-forward (all three paragraphs) revised per v1.1 amendment table above. §[traceability] matrix rows D1 + D6 row-label versions updated. Closing footer updated to v1.1.

**Cross-cascade-step coordination.** PRD v1.1 produces two downstream effects at cascade Step 5:

| Downstream cascade step | Substrate consumed from PRD v1.1 |
|---|---|
| Step 5a — CP spec v1.3 revision pass | R-CP-04 (lifecycle event surface — engine.* + retry.* namespaces visible) + R-CP-07 (replay-resumption semantics — engine.replay_disposition visible) → C-CP-08 §8.4 affected-contract notation closes + C-CP-09 §9.1 4-attribute engine.* declaration |
| Step 5b — OD spec v1.3 revision pass | R-OD-05 (cost-attribution per span with per-attempt discipline + dedup correctness) → C-OD-14 cost-attribution-per-span contract amends with dedup algorithm + per-attempt cost discipline per D6 v1.2 §1.5 + §1.5.3 |

**F2-12 status at PRD v1.1.** ✅ CLOSED at this revision-pass filing per ADD v1.3 §6.3.1 cascade Step 4 row. The requirement-level absorption at R-CP-04 + R-CP-07 + R-OD-05 surfaces the architectural amendments at the observable-behavior surface; the [CF-1] meta-section is revised to record closure rather than carry forward as deferred-acknowledged. Formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` at cascade close.

## Front-matter

[Front-matter §Shape declaration + §Persona summary + §Scope and out-of-scope preserved verbatim from v1.0.]

### ADR substrate set (v1.1 amendment)

The PRD v1.1 derives observable behavior from the following ADR substrate (v1.0 entries preserved verbatim except D1 + D6):

| ADR | Version at PRD v1.1 | Status | Source |
|---|---|---|---|
| ADR-F1 | v1.2 | Accepted | `/mnt/project/ADR-F1.md` |
| ADR-F2 | v1.2 | Accepted | `/mnt/project/ADR-F2.md` |
| ADR-F3 | v1.1 | Accepted | `/mnt/project/ADR-F3.md` |
| ADR-F4 | v1.1 | Accepted | `/mnt/project/ADR-F4.md` |
| ADR-F5 | v1.1 | Accepted | `/mnt/project/ADR-F5.md` |
| **ADR-D1** | **v1.2** | **Proposed (F2-12 cascade Step 2a)** | **`/mnt/user-data/outputs/ADR-D1_v1_2.md`** |
| ADR-D2 | v1.1 | Accepted | `/mnt/project/ADR-D2.md` |
| ADR-D3 | v1.2 | Accepted | `/mnt/project/ADR-D3.md` (v1.2 per v1.0 baseline; preserved at v1.1) |
| ADR-D4 | v1.1 | Accepted | `/mnt/project/ADR-D4.md` |
| ADR-D5 | v1.3 | Accepted | `/mnt/project/ADR-D5.md` |
| **ADR-D6** | **v1.2** | **Proposed (F2-12 cascade Step 2b)** | **`/mnt/user-data/outputs/ADR-D6_v1_2.md`** |

Consolidating artifact: **ADD v1.3** (`/mnt/user-data/outputs/Architectural_Design_Document_v1_3.md`).

---

## §1 Control plane requirements

[R-CP-01 through R-CP-03 preserved verbatim from v1.0.]

### R-CP-04 — Workflow lifecycle event surface (v1.1 amendment absorbing D1 v1.2 + D6 v1.2)

**Observable behavior (v1.1).** Workflow lifecycle events — workflow-start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease-acquired, lease-released, resumption — are visible to the production-time operator at the run-event surface as distinct event classes. **At v1.1, the retry-attempt class is emitted as BOTH a parent-span event AND a child span per attempt: the parent event carries `parent.attempt_count` + `parent.attempts_remaining` + `parent.next_delay_ms` event fields; the child span carries the six retry.* attributes (`retry.attempt_number`, `retry.original_span_id`, `retry.delay_ms`, `retry.cause_attribution`, `retry.fail_class`, `engine.replay_disposition`). The production-time operator can scan the parent event timeline to see retry occurred AND expand the retry-attempt child span tree to inspect per-attempt sub-agent execution.** Every span emitted under the lifecycle envelope carries the four `engine.*` attributes (`engine.class`, `engine.event_history.tier`, `engine.event.id`, `engine.replay_disposition`) as stable observability dimensions.

**Observer role.** Production-time operator.

**ADR citation (v1.1).** ADR-F3 v1.1 §Decision capability-requirement floor (iv) (observable lifecycle); **ADR-D1 v1.2 §1.1.1 (4-attribute `engine.*` namespace canonical declaration) + §1.1.2 (per-engine-class replay-emission discipline)**; **ADR-D6 v1.2 §1.2 (engine.* row update) + §1.2.2 (retry.* namespace 6-attribute span schema + 3-field parent event schema) + §1.2.3 (sub-agent boundary composition under retry)**; ADD v1.3 §3.1.1 D1 Synthesis + §3.4.1 D6 Synthesis; composition with ADR-F1 v1.2 fallback-chain visibility at fallback-trigger event class.

**Persona linkage.** Persona §4 (99.9% SLO; deterministic outer harness absorbs most recovery); §10.4 (compliance-readiness foundational primitives); §8.3 (pipeline automation — F3 durable-execution-spine territory; retry/breaker discipline most rigorous of all four workload classes).

**Acceptance criterion (v1.1).** Each of the eight lifecycle event classes emits a distinguishable observable record at the run-event surface; the production-time operator can filter and inspect by class. The retry-attempt class emits BOTH the parent-span event and the per-attempt child span; emission of one without the other is a quality failure (FM-Q per D6 v1.2 §1.2.2.3 emission discipline). The four `engine.*` attributes are present on every lifecycle-event-carrying span.

### R-CP-05 — Manifest-default invocation with per-step opt-in override

[Preserved verbatim from v1.0.]

### R-CP-06 — Engine class committed per deployment surface at design time

[Preserved verbatim from v1.0.]

### R-CP-07 — Replay-resumption semantics visible at run resumption (v1.1 amendment absorbing D1 v1.2)

**Observable behavior (v1.1).** When a run resumes after restart, the production-time operator perceives the replay-resumption disposition through the **`engine.replay_disposition` attribute on the run-event surface, taking one of five values closed-mapped to the engine class bound for that workload**:

| `engine.replay_disposition` | `engine.class` (closed mapping) | Operator-visible semantics |
|---|---|---|
| `deterministic_replay` | event-sourced-replay | Prior steps replay as deterministic re-read; original trace context recovered from F2 state-ledger; replay is invisible at the run-event surface (no new span emission per attempt) |
| `checkpoint_resume` | save-point-checkpoint | Resume from save-point; activity-level spans re-emit on resume with NEW span_id and parent_span_id preserved from pre-resume checkpoint |
| `no_replay` | pure-pattern-no-engine | No replay concept applies; every invocation is fresh |
| `reconciler_iteration` | reconciler-loop | Each reconciliation iteration is a fresh execution; spans fresh per iteration |
| `wal_consume` | WAL-segment | Each consumer replay is fresh processing of WAL segments; spans fresh per consumption |

**Observer role.** Production-time operator.

**ADR citation (v1.1).** **ADR-D1 v1.2 §1.1.1 (4-attribute `engine.*` namespace + `engine.replay_disposition` 5-value enum closed-mapped to `engine.class`); §1.1.2 (per-engine-class replay-emission discipline); §1.1.2.2 (F2 state-ledger entry shape extension with `original_trace_id` + `original_span_id` for trace-context durability under deterministic_replay)**; ADD v1.3 §3.1.1 D1 Synthesis + §6.3.1 F2-12 closure record.

**Persona linkage.** Persona §4 (99.9% SLO; durable replay across restart); §10.4 (compliance-readiness — tamper-evidence at replay); §11.3 (long-tail duration of durable pole).

**Acceptance criterion (v1.1).** At resumption, the run-event surface reflects the `engine.replay_disposition` value bound for the workload; the production-time operator can distinguish a deterministic_replay re-read (no new span) from a checkpoint_resume re-emission (new span with preserved parent_span_id) without backend-side enrichment. **F2-12 closure status: ✅ CLOSED — per-event-class replay-emission contract specification is filed at D1 v1.2 §1.1.2 + D6 v1.2 §1.5 dedup algorithm; the v1.0 acceptance criterion's "carries forward as deferred-acknowledged" clause is closed at v1.1 per ADD v1.3 §6.3.1 cascade Step 4 row.**

### R-CP-08 through R-CP-12

[Preserved verbatim from v1.0.]

---

## §2 Information substrate requirements

[R-IS-01 through R-IS-04 preserved verbatim from v1.0.]

---

## §3 Action surface requirements

[R-AS-01 through R-AS-07 preserved verbatim from v1.0.]

---

## §4 Operational discipline requirements

[R-OD-01 through R-OD-04 preserved verbatim from v1.0.]

### R-OD-05 — Cost-attribution per span at run cost-attribution surface (v1.1 amendment absorbing D6 v1.2)

**Observable behavior (v1.1).** The production-time operator perceives per-span cost attribution at the run cost-attribution surface — per-Anthropic-pricing formula composing with sandbox-tier overhead and per-sibling rollup at fan-out, anchored to tokenization version. **At v1.1, the cost-attribution surface enforces per-attempt cost discipline under retry sequences: each retry attempt's cost is a distinct per-attempt accrual unit (NOT aggregated across attempts); the parent operation's total cost is the SUM of per-attempt costs across all retry attempts; `deterministic_replay` re-reads contribute zero additional cost (cost was accrued at first execution; replay re-reads are idempotent at cost level). The production-time operator can inspect per-attempt cost at the retry-attempt child span surface and aggregate cost at the parent operation surface.**

**Observer role.** Production-time operator.

**ADR citation (v1.1).** **ADR-D6 v1.2 §1.5 cost-attribution-per-span dashboarding contract (preamble + dedup algorithm specification) + §1.5.1 replay-aware dedup with retry orthogonality + §1.5.3 per-attempt cost-attribution discipline**; ADR-D1 v1.2 §1.1.1 (`engine.replay_disposition` as dedup discriminator); ADD v1.3 §3.4.1 D6 Synthesis + §5.3 (cost attribution as cross-cutting architectural property).

**Persona linkage.** Persona §6 (per-workload-class cost ceiling); §10.2 (cost-attribution-per-span as foundational primitive); §8.5 (cross-class cost × reliability × capability coupling).

**Acceptance criterion (v1.1).** The per-run cost-attribution surface presents per-span cost; per-sibling rollup composes at fan-out spans; sandbox-tier overhead is additive to per-Anthropic-pricing for sandbox-bounded spans; tokenization version is recorded per span. **At v1.1, per-attempt cost is exposed at the retry-attempt child span surface; parent operation total cost equals the sum of per-attempt costs (no double-counting on replay); `deterministic_replay` re-ingestions contribute zero additional cost. The production-time operator can verify cost-correctness across retry sequences without backend-side enrichment.**

### R-OD-06 through R-OD-08

[Preserved verbatim from v1.0.]

---

## §[carry-forwards]

This meta-section documents Phase-3-boundary items inherited at Phase 4 entry per OD-4-3.A. Entries are **documentation, not requirement-bearing** — they do not engage the four sub-disciplines at `prd-author` SKILL.md §4 (trace-back / non-contradiction / observable framing / no-architecture-introduction); they engage the PRD's operator-visibility surface.

### [CF-1] F2-12 — D1 v1.1 → v1.2 + D6 v1.1 → v1.2 replay-trace-emission contract (✅ CLOSED at v1.1)

**Status (v1.1 amendment).** ✅ **CLOSED** at PRD v1.1 filing per ADD v1.3 §6.3.1 cascade Step 4 row. The v1.0 status was 🔄 Deferred-acknowledged carry-forward; v1.1 transitions to ✅ CLOSED following the cascade execution path: Step 1 (council deliberation, filed 2026-05-14) → Step 2a (ADR-D1 v1.2, filed 2026-05-14) → Step 2b (ADR-D6 v1.2, filed 2026-05-14) → Step 3 (ADD v1.3, filed 2026-05-14) → Step 4 (this PRD v1.1 filing). Formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` filed at cascade close (post-Step 6 plan v2.2 filings).

**Scope (preserved verbatim from v1.0).** D1 v1.1 → v1.2 replay-trace-emission contract covering (i) span re-emission semantics under engine replay; (ii) `retry.attempt` sibling-span discipline; (iii) trace-ingestion dedup composition with F2 `idempotency_key`.

**PRD impact (v1.1 amendment).** Three requirement-level absorptions at v1.1: **R-CP-04 (workflow lifecycle event surface)** absorbs the 4-attribute `engine.*` namespace + 6-attribute `retry.*` namespace + dual-surface retry.attempt discipline per D6 v1.2 §1.2 + §1.2.2; **R-CP-07 (replay-resumption semantics)** absorbs the `engine.replay_disposition` 5-value enum + per-engine-class replay-emission discipline per D1 v1.2 §1.1.1 + §1.1.2; **R-OD-05 (cost-attribution per span)** absorbs the per-attempt cost-attribution discipline + dedup-algorithm correctness per D6 v1.2 §1.5 + §1.5.1 + §1.5.3. The v1.0 statement "binding R-CP-07 to a contract not yet filed at ADR layer would violate `prd-author` SKILL.md §2 inversion discipline" is closed at v1.1 because the contract is now filed at ADR-D1 v1.2 + ADR-D6 v1.2; R-CP-07 binding is valid under the inversion discipline at v1.1.

### [CF-2] Workflow §7 substrate-skill propagation

[Preserved verbatim from v1.0.]

---

## §[traceability]

ADR × PRD-section traceability matrix per `prd-author` SKILL.md §5.5. Rows = 11 ADRs; columns = 4 PRD sections (OD-4-1.A axis-led). `✓` indicates the ADR is cited by ID + section in ≥1 requirement within that PRD section. **At v1.1, the D1 + D6 row-label versions are updated from v1.1 → v1.2; cell marks preserved (no new requirements added; no requirements removed; the v1.1 amendments are at existing requirement sites R-CP-04 + R-CP-07 + R-OD-05).**

| ADR | §1 Control Plane | §2 Information Substrate | §3 Action Surface | §4 Operational Discipline |
|---|---|---|---|---|
| F1 v1.2 | ✓ (R-CP-01, R-CP-02, R-CP-03) | | | ✓ (R-OD-06) |
| F2 v1.2 | | ✓ (R-IS-01, R-IS-02, R-IS-03, R-IS-04) | | |
| F3 v1.1 | ✓ (R-CP-04, R-CP-05, R-CP-06) | | | |
| F4 v1.1 | | | ✓ (R-AS-01, R-AS-02, R-AS-03) | |
| F5 v1.1 | | | ✓ (R-AS-04, R-AS-05) | |
| **D1 v1.2** | ✓ (R-CP-06, R-CP-07; **R-CP-04 composition** at v1.1 absorbing §1.1.1 4-attribute namespace) | | | |
| D2 v1.1 | ✓ (R-CP-09) | | ✓ (R-AS-01, R-AS-02, R-AS-06) | ✓ (R-OD-08) |
| D3 v1.2 | | | ✓ (R-AS-07) | |
| D4 v1.1 | ✓ (R-CP-08, R-CP-09) | | | |
| D5 v1.3 | ✓ (R-CP-10, R-CP-11, R-CP-12) | | | ✓ (R-OD-06, R-OD-08) |
| **D6 v1.2** | ✓ (R-CP-04 composition reference at v1.1 absorbing §1.2 + §1.2.2 retry.*) | | | ✓ (R-OD-01, R-OD-02, R-OD-03, R-OD-04, **R-OD-05 at v1.1 absorbing §1.5 dedup + §1.5.3 per-attempt**, R-OD-06, R-OD-07, R-OD-08) |

**Bidirectional verification (v1.1 preserved from v1.0).** Every ADR row has at least one column mark; every PRD section column has at least one row mark; no orphan ADRs; no orphan PRD sections.

---

## §[coherence pass]

[Audits 6.1–6.5 + aggregate preserved verbatim from v1.0; the v1.1 revision pass verifies the four sub-disciplines inline at each amended requirement per Workflow v1.7 §7 fidelity-grammar discipline, rather than re-running the v1.0 audit harness.]

### Audit 6.x — v1.1 amendment-site verification (NEW at v1.1)

For each v1.1-amended requirement, the four `prd-author` SKILL.md §4 sub-disciplines verify inline:

| Requirement | Trace-back at section level | Non-contradiction with ADD v1.3 | Observable framing | No-architecture-introduction |
|---|---|---|---|---|
| R-CP-04 (v1.1) | ✅ Cites ADR-D1 v1.2 §1.1.1 + §1.1.2; ADR-D6 v1.2 §1.2 + §1.2.2 + §1.2.3; ADD v1.3 §3.1.1 + §3.4.1 | ✅ ADD v1.3 §3.1.1 D1 Synthesis + §3.4.1 D6 Synthesis commit the 4-attribute engine.* + 6-attribute retry.* namespaces; PRD v1.1 surfaces as observable | ✅ Behavior framed at production-time-operator surface ("can scan timeline" / "can expand child span tree"); no implementation-grade language | ✅ No new architectural commitment; inherits D1 v1.2 + D6 v1.2 amendments |
| R-CP-07 (v1.1) | ✅ Cites ADR-D1 v1.2 §1.1.1 + §1.1.2 + §1.1.2.2; ADD v1.3 §3.1.1 + §6.3.1 | ✅ ADD v1.3 §3.1.1 D1 Synthesis commits engine.replay_disposition + replay-emission discipline; PRD v1.1 surfaces as observable | ✅ Behavior framed at production-time-operator surface ("can distinguish a deterministic_replay re-read from a checkpoint_resume re-emission"); no implementation-grade language | ✅ No new architectural commitment; inherits D1 v1.2 amendment |
| R-OD-05 (v1.1) | ✅ Cites ADR-D6 v1.2 §1.5 + §1.5.1 + §1.5.3; ADR-D1 v1.2 §1.1.1; ADD v1.3 §3.4.1 + §5.3 | ✅ ADD v1.3 §3.4.1 D6 Synthesis commits dedup algorithm + per-attempt cost-attribution; PRD v1.1 surfaces as cost-correctness property | ✅ Behavior framed at production-time-operator surface ("can inspect per-attempt cost" / "can verify cost-correctness across retry sequences"); no implementation-grade language | ✅ No new architectural commitment; inherits D6 v1.2 amendment |

**Audit 6.x disposition.** ✅ PASS — all three v1.1-amended requirements satisfy the four sub-disciplines at amendment-site granularity; v1.0 audit harness (Audits 6.1–6.5) preserved unchanged at v1.0 form.

### Coherence pass aggregate (v1.1)

✅ PASS at v1.1 amendment-site granularity. v1.0 aggregate preserved from v1.0. No contradictions surfaced between revised and preserved sections. `prd-author` SKILL.md §4 four sub-disciplines verified at every v1.1 amendment site. F2-12 carry-forward [CF-1] transitioned to ✅ CLOSED status with PRD impact paragraph revised to record the three requirement-level absorptions.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `PRD_v1_1.md` |
| Filing destination | `/mnt/user-data/outputs/PRD_v1_1.md` |
| Status | Proposed (pending F2-12 cascade close per cascade Step 6 plan v2.2 filings) |
| Predecessor | `PRD_v1_0.md` (v1.0 baseline; v1.0.1 substrate-citation refinement) |
| Substrate consumed | ADR-D1 v1.2 + ADR-D6 v1.2 + ADD v1.3 (cascade Steps 2a + 2b + 3 outputs) |
| Successor | `Spec_Control_Plane_v1_3.md` + `Spec_Operational_Discipline_v1_3.md` (F2-12 cascade Step 5; `spec-writer` SKILL.md §12 spec-revision-pass sub-mode) |
| F2-12 closure status | ✅ CLOSED at cascade Step 4 (this artifact); formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` at cascade close |
| Workflow discipline | `Project_Workflow_v1_7.md` §7 fidelity-grammar |
| Date | 2026-05-14 |

*Filed at F2-12 cascade Step 4 close. R-CP-04 + R-CP-07 + R-OD-05 requirement-level absorptions of D1 v1.2 + D6 v1.2 substantive amendments applied; [CF-1] F2-12 carry-forward transitioned to ✅ CLOSED status; traceability matrix D1 + D6 rows updated to v1.2. Cascade segment boundary per OD-F212-4.A. Recommended next cascade step: Step 5a (CP spec v1.3 revision pass) + Step 5b (OD spec v1.3 revision pass) per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 — C-CP-08 §8.4 + C-CP-09 §9.1 + C-OD-14 contract amendments against this PRD v1.1.*
