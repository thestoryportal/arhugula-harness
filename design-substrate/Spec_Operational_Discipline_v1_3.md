# Specification — Operational Discipline v1.3

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_3.md` |
| Status | **Proposed** — F2-12 cascade Step 5b revision pass; promotion to Accepted at cascade close (post-Step 6 plan v2.2 filings) |
| Revision | v1 → v1.1 (P5-CK iter-1 close mechanical revision) → v1.2 (P5-CK iter-2 close final-revision-pass) → **v1.3 (F2-12 cascade Step 5b revision pass authored 2026-05-14 per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade Step 5b row + PRD v1.1 R-OD-05 absorption)** |
| Revision date | 2026-05-14 (v1.3 revision pass) |
| Phase | 5 — Specification authoring (post-Phase-3 F2-12 cascade Step 5b per `Project_Workflow_v1_7.md` §4.1.2; cascade-driven revision pass under `spec-writer` SKILL.md spec-revision-pass discipline + Workflow v1.7 §7 fidelity-grammar) |
| Skill | `spec-writer` (spec-revision-pass sub-mode) at v1.3 |
| Promotion path | Accepted at F2-12 cascade close |
| Source-set | PRD v1.1 R-OD-05 (cascade Step 4 output) + ADD v1.3 §3.4.1 (D6 v1.2 absorption) + ADR-D6 v1.2 §1.5 (cost-attribution-per-span dashboarding contract with dedup algorithm) + §1.5.1 (replay-aware dedup orthogonality) + §1.5.2 (cause_attribution invariance check) + §1.5.3 (per-attempt cost-attribution discipline) + ADR-D1 v1.2 §1.1.1 (`engine.replay_disposition` as dedup discriminator) + §1.1.2.2 (F2 state-ledger entry shape extension consumed at dedup lookup) + `Spec_Control_Plane_v1_3.md` C-CP-08 + C-CP-09 (cascade Step 5a co-revision output) |
| Entry authorization | `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 cascade Step 5b row + ADD v1.3 §6.3.1 cascade execution path Step 5b row + `Project_Workflow_v1_7.md` §3.1 |
| Exit gate | F2-12 cascade Step 6b (OD plan v2.2 revision pass per `implementation-planner` SKILL.md revision-pass sub-mode) consuming this OD spec v1.3 as substrate |

## Change-note (v1.2 → v1.3)

**Scope of revision.** F2-12 cascade Step 5b revision pass per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 + ADD v1.3 §6.3.1 cascade execution path Step 5b row. The revision pass absorbs the ADR-D6 v1.2 §1.5 + §1.5.1 + §1.5.2 + §1.5.3 substantive amendments + PRD v1.1 R-OD-05 observable-behavior surface into Operational Discipline spec contract surfaces at C-OD-14 (cost-attribution-per-span formula composing pricing + sandbox-tier + per-sibling rollup) and closes the §14.5 F2-12 ACTIVE engagement notation. Five amendment sites all within C-OD-14:

| Site | Amendment shape | Substrate source |
|---|---|---|
| §14 Contract surface | Contract surface description extended with dedup algorithm + per-attempt cost-attribution discipline; PRD requirement satisfied row remains R-OD-05 but observable-behavior scope absorbs v1.1 amendment; ADR commitments honored row updated D6 v1.1 → v1.2 | ADR-D6 v1.2 §1.5 |
| §14.4 Idempotency-key join — Replay-safe composition row | Row content updated from "composes with F2 state-ledger via `idempotency_key` to avoid double-counting on replay" (v1.2 — promissory) to specific dedup-algorithm citation per D6 v1.2 §1.5 + §1.5.1; cross-references new §14.5 sub-sections | ADR-D6 v1.2 §1.5 |
| §14.5 ACTIVE engagement → CLOSED | Section header revised from "[F2-12 ACTIVE engagement] — Deferred-to-implementation discretion" to "[F2-12 ✅ CLOSED] — Trace-ingestion dedup algorithm + replay-aware orthogonality + cause_attribution invariance + per-attempt cost-attribution"; 3-row Open-at-F2-12-closure table replaced with closure execution path table; Forward-routing paragraph collapsed into closure summary; substantive content of dedup algorithm + orthogonality + invariance + per-attempt cost-attribution added as new sub-sections §14.5.1 + §14.5.2 + §14.5.3 + §14.5.4 | ADD v1.3 §6.3.1 + ADR-D6 v1.2 §1.5–§1.5.3 |
| §14.5.1 (NEW) | Trace-ingestion dedup algorithm specification (pseudocode + F2 state-ledger composition + hash-chain integrity composition) | ADR-D6 v1.2 §1.5 |
| §14.5.2 (NEW) | Replay-aware dedup with retry orthogonality (orthogonality discriminators + dedup outcome matrix) | ADR-D6 v1.2 §1.5.1 |
| §14.5.3 (NEW) | cause_attribution invariance check at deterministic_replay (escalation on mismatch + cause_attribution catalog extension) | ADR-D6 v1.2 §1.5.2 |
| §14.5.4 (NEW) | Per-attempt cost-attribution discipline (per-disposition cost accrual semantics + parent operation total cost roll-up + cross-axis composition with §C-OD-23 operator-burden eval primitive) | ADR-D6 v1.2 §1.5.3 |

Workflow v1.7 §7 fidelity-grammar discipline applied across all amendment sites: no Pattern P1 cross-artifact name drift (dedup-algorithm pseudocode preserves canonical attribute names from D1 v1.2 §1.1.1 + D6 v1.2 §1.5; `engine.replay_disposition` enum values, `retry.attempt_number`, `retry.cause_attribution` all consistent across the v1.3 cascade artifacts); no Pattern P2 verbatim-claim-contradicted (all "per ADR-D6 v1.2 §1.5.x" claims verify against source files at `/mnt/user-data/outputs/`); citation anchors substrate-verified per Workflow v1.7 §2.3.3.1 clause (iii).

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_7.md` §3.1 — promotion to `Accepted` blocked until F2-12 cascade close. OD spec v1.3 enters cascade Step 6b (OD plan v2.2 revision pass) as substrate input.

**Sections preserved verbatim from v1.2.** §Front-matter (Axis declaration; Axis-grounding note; Persona summary; PRD requirement scope; ADR scope; Cross-axis citation substrate; Persona-linkage substrate; Scope and out-of-scope — only the F2-12 "active engagement" entry revised at v1.3 to closure); §1 C-OD-01 through §13 C-OD-13 (all contracts at v1.2 form); §14 C-OD-14 §14.1 + §14.2 + §14.3 (per-span cost formula; sandbox-tier overhead; per-sibling rollup at fan-out close); §14.4 Idempotency-key join — Join key + Per-sub-agent inheritance rows (only the Replay-safe composition row revised at v1.3); §15 C-OD-15 through §22 C-OD-22 (all contracts); §23 C-OD-23 (operator-burden eval primitive dashboard binding); §[traceability] matrix (D6 row-label version updated v1.1 → v1.2; cell marks preserved — v1.3 amendments at existing C-OD-14 site only); §[carry-forwards] — F2-12 line revised at v1.3 to closure; §[coherence pass] (preserved verbatim as v1 + v1.1 + v1.2 historical record per discipline; v1.3 amendment-site verification inline per Workflow v1.7 §7 fidelity-grammar).

**Changes inline.** Status block (Revision row extended with v1.3 entry; Revision date row appended; Source-set updated D6 v1.1 → v1.2 + PRD v1.1 + ADD v1.3 + CP spec v1.3 cross-axis citation; Entry authorization extended with F2-12 cascade Step 5b row). This Change-note (v1.2 → v1.3) section. §14 Contract surface description extended (3 paragraphs revised). §14 ADR commitments honored row (D6 v1.1 → v1.2). §14.4 Idempotency-key join — Replay-safe composition row (content revised from promissory to dedup-algorithm-specific). §14.5 section header (ACTIVE engagement → CLOSED transition; 3-row open-surface table replaced with closure-execution-path table). §14.5.1 + §14.5.2 + §14.5.3 + §14.5.4 (four new sub-sections inserted between v1.2 §14.5 transitioned header and §15). §[traceability] D6 row label (v1.1 → v1.2). §[carry-forwards] F2-12 entry (transitioned to closure). Filing footer updated to v1.3.

**Cross-cascade-step coordination.** OD spec v1.3 produces one downstream effect at cascade Step 6b:

| Downstream cascade step | Substrate consumed from OD spec v1.3 |
|---|---|
| Step 6b — OD plan v2.2 revision pass | §14.5.1 trace-ingestion dedup algorithm pseudocode → U-OD-14 unit acceptance criterion absorbs dedup-algorithm-correctness as acceptance test; §14.5.2 orthogonality outcome matrix → U-OD-14 per-attempt cost roll-up acceptance criterion; §14.5.3 cause_attribution invariance check → U-OD-14 invariance-check-emits-ESCALATE acceptance criterion; §14.5.4 per-attempt cost-attribution → U-OD-14 cost roll-up acceptance criterion; §14.5 CLOSED status → U-OD-20 closure_path closure status revised |

**F2-12 status at OD spec v1.3.** ✅ CLOSED at this revision-pass filing per ADD v1.3 §6.3.1 cascade Step 5b row. The contract-level absorption at §14.4 + §14.5 + §14.5.1–§14.5.4 closes the D6-side closure half of the F2-12 carry-forward. Formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` at cascade close.

---

## Front-matter

[§Axis declaration + §Axis-grounding note + §PRD requirement scope + §ADR scope + §Cross-axis citation substrate + §Persona-linkage substrate + §Scope and out-of-scope preserved verbatim from v1.2 except F2-12 line revised at v1.3 to closure (see §[carry-forwards] section below).]

---

## §1 C-OD-01 through §13 C-OD-13

[Preserved verbatim from v1.2.]

---

## §14 C-OD-14 — Cost-attribution-per-span formula composing pricing + sandbox-tier + per-sibling rollup (v1.3 amendment absorbing D6 v1.2)

**Contract surface (v1.3 amendment).** Per-span cost formula + per-sibling rollup at fan-out close + idempotency-key join + **trace-ingestion dedup algorithm with replay-aware orthogonality + cause_attribution invariance check at deterministic_replay + per-attempt cost-attribution discipline per ADR-D6 v1.2 §1.5–§1.5.3 (F2-12 sub-scope (iii) closure)**.

**PRD requirement(s) satisfied (v1.3 amendment).** R-OD-05 (cost-attribution per span at run cost-attribution surface — at v1.1 PRD revision, observable-behavior scope absorbs per-attempt cost-attribution discipline + dedup-algorithm correctness as production-time-operator-visible cost-correctness property).

**ADR commitment(s) honored (v1.3 amendment).** **ADR-D6 v1.2 §1.5 cost-attribution-per-span dashboarding contract (per-Anthropic-pricing formula + sandbox-tier overhead + per-sibling rollup; preserved verbatim from v1.1 except trace-ingestion dedup-algorithm specification added at the §1.5 preamble — see §14.5.1 below); §1.5.1 replay-aware dedup with retry orthogonality; §1.5.2 cause_attribution invariance check at deterministic_replay; §1.5.3 per-attempt cost-attribution discipline**; composition with **ADR-D1 v1.2 §1.1.1 (`engine.replay_disposition` as per-class dedup discriminator) + §1.1.2.2 (F2 state-ledger entry shape extension with `original_trace_id` + `original_span_id` consumed at dedup lookup)**.

**Cross-axis citation (v1.3 amendment).** `Spec_Information_Substrate_v1.md` C-IS-05 (state-ledger entry shape — `idempotency_key` field; **at v1.3, ledger entry shape extends with `original_trace_id` + `original_span_id` per D1 v1.2 §1.1.2.2; D6 dedup at §14.5.1 consumes**); C-IS-10 §10.2 (`idempotency_key` join export — D6 cost-attribution-per-span consuming axis row); `Spec_Action_Surface_v1.md` C-AS-15 §15.6 (sandbox-violation events join on `idempotency_key`; `sandbox.cost.tier_overhead_*` attributes); **`Spec_Control_Plane_v1_3.md` C-CP-08 (cascade Step 5a co-revision; replay-resumption semantics per engine class); C-CP-09 §9.1 (4-attribute `engine.*` namespace including `engine.replay_disposition`); C-CP-03 §3.5 (retry.* 6-attribute namespace + parent-event 3-field schema declaration; dual-emission discipline)**; `Spec_Control_Plane_v1.md` C-CP-14 §14.1 (fan-out boundary cost-attribution anchors); C-CP-24 §24.2 (cross-axis composition exports — fan-out cost-attribution row).

**Persona linkage.** Persona §6 (per-workload-class cost ceiling); §10.2 (cost-attribution-per-span as foundational primitive); §8.5 (cross-class cost × reliability × capability coupling).

**Specification content.**

### §14.1 Per-span cost formula (Anthropic-pricing canonical)

[Preserved verbatim from v1.2.]

### §14.2 Sandbox-tier overhead addition

[Preserved verbatim from v1.2.]

### §14.3 Per-sibling rollup at fan-out close

[Preserved verbatim from v1.2.]

### §14.4 Idempotency-key join (v1.3 amendment to Replay-safe composition row)

Per `Spec_Information_Substrate_v1.md` C-IS-10 §10.2 (idempotency-key join export; D6 cost-attribution-per-span consuming axis row):

| Property | Contract |
|---|---|
| **Join key** | Every per-span cost record carries the parent's `idempotency_key` per C-IS-05 |
| **Replay-safe composition (v1.3 amendment)** | **Cost-attribution-per-span composes with F2 state-ledger via `idempotency_key` AND the trace-ingestion dedup algorithm specified at §14.5.1 below. Dedup discriminates per `engine.replay_disposition` (5 values per C-CP-09 §9.1 / D1 v1.2 §1.1.1): `deterministic_replay` DROPs idempotent re-reads (zero additional cost accrual); `checkpoint_resume` / `reconciler_iteration` / `wal_consume` RECORD new replay-derived spans (cost accrues per attempt); `no_replay` ERRORs on unexpected re-ingestion. Per §14.5.4 per-attempt cost-attribution discipline, cost accrues per retry attempt without aggregation across attempts; parent operation total cost = SUM of per-attempt costs.** |
| **Per-sub-agent inheritance** | Sub-agent dispatch propagates a derived `idempotency_key` per C-AS-15 §15.6 sub-agent boundary inheritance; per-sibling rollup at §14.3 composes against the derived keys |

### §14.5 [F2-12 ✅ CLOSED] — Trace-ingestion dedup algorithm + replay-aware orthogonality + cause_attribution invariance + per-attempt cost-attribution (v1.3 amendment absorbing D6 v1.2 §1.5–§1.5.3)

**Status (v1.3 amendment).** ✅ **CLOSED** at OD spec v1.3 filing per ADD v1.3 §6.3.1 cascade Step 5b row. The v1.2 status was "F2-12 ACTIVE engagement — Deferred-to-implementation discretion" with three open composition surfaces; v1.3 transitions to ✅ CLOSED with F2-12 closure execution path:

| Cascade step | Artifact | Sub-scope closed |
|---|---|---|
| 1 — Council deliberation | `F2-12_Council_Deliberation_Output.md` (filed 2026-05-14) | Substantive resolution substrate for all three sub-scopes |
| 2a — ADR-D1 revision | `ADR-D1_v1_2.md` (filed 2026-05-14) | (i) span re-emission semantics |
| 2b — ADR-D6 revision | `ADR-D6_v1_2.md` (filed 2026-05-14) | (ii) retry.attempt child-per-attempt + (iii) trace-ingestion dedup |
| 3 — ADD consolidation | `Architectural_Design_Document_v1_3.md` (filed 2026-05-14) | Cross-axis consolidation |
| 4 — PRD revision | `PRD_v1_1.md` (filed 2026-05-14) | R-CP-04 + R-CP-07 + R-OD-05 observable-behavior absorption |
| 5a — CP spec revision | `Spec_Control_Plane_v1_3.md` (filed 2026-05-14) | C-CP-08 + C-CP-09 + §3.5 + §5.4 contract-surface absorption |
| **5b — OD spec revision** | **`Spec_Operational_Discipline_v1_3.md` (this artifact)** | **C-OD-14 §14.5.1 dedup algorithm + §14.5.2 orthogonality + §14.5.3 invariance + §14.5.4 per-attempt cost-attribution** |
| 6a — CP plan revision (pending) | `Implementation_Plan_Control_Plane_v2_2.md` | U-CP-20 + U-CP-21 + U-CP-55 plan-level absorption |
| 6b — OD plan revision (pending) | `Implementation_Plan_Operational_Discipline_v2_2.md` | U-OD-20 + U-OD-14 plan-level absorption |
| Close | `F2-12_Closure_Declaration.md` (pending) | Formal `closure_pending false` declaration |

**Contract-level absorption at this spec revision.** F2-12 sub-scope (iii) trace-ingestion dedup composition with F2 `idempotency_key` (the D6-side closure half) closes at the four new §14.5.1–§14.5.4 sub-sections below. The v1.2 §14.5 "Open at F2-12 closure" 3-row table — Span re-emission semantics under engine replay / `retry.attempt` sibling-span discipline at D6 ingestion / Trace-ingestion dedup composition with F2 `idempotency_key` at D6 cost-attribution-per-span — has all three rows now closed (sub-scope (i) at D1 v1.2 + CP spec v1.3 §9.1; sub-scope (ii) at D6 v1.2 + CP spec v1.3 §3.5; sub-scope (iii) at this OD spec v1.3 §14.5.1–§14.5.4).

#### §14.5.1 Trace-ingestion dedup algorithm (v1.3; new sub-section per D6 v1.2 §1.5)

The cost-attribution-per-span contract at §14.1–§14.4 requires per-span cost accrual to be replay-aware. Cost-per-span accrues exactly once per attempt for re-emitting `engine.replay_disposition` values and zero additional accrual for `deterministic_replay`. The dedup algorithm at trace-ingestion time enforces this invariant.

```
function ingest_span(span):
  # span carries: trace_id, span_id, idempotency_key (from F2 state-ledger join),
  #               engine.replay_disposition, optional retry.attempt_number,
  #               optional retry.cause_attribution

  key = span.idempotency_key  # per ADR-IS C-IS-05 + C-IS-10 §10.2 canonical join key
  ledger_entry = F2_state_ledger.lookup_by_key(key)

  if ledger_entry exists:
    match span.engine.replay_disposition:
      case "deterministic_replay":
        # Idempotent replay; verify trace_id + span_id match ledger
        assert span.trace_id == ledger_entry.original_trace_id
        assert span.span_id == ledger_entry.original_span_id
        assert span.retry.cause_attribution == ledger_entry.cause_attribution  # §14.5.3
        DROP  # No new cost attribution; replay is invisible at D6

      case "checkpoint_resume" | "reconciler_iteration" | "wal_consume":
        # Re-emission expected; record as new attempt or new execution
        RECORD span as new ingestion
        mark span.is_replay_derived = true
        # Cost attribution counts ONCE per attempt; not aggregated across replays (§14.5.4)
        # Parent span_id from ledger_entry preserves topology link

      case "no_replay":
        ERROR  # Unexpected re-ingestion for non-replay engine class
        cause_attribution = "replay_semantic_divergence"

  else:
    RECORD span as new (first ingestion)
    F2_state_ledger.append(
      idempotency_key=key,
      original_trace_id=span.trace_id,
      original_span_id=span.span_id,
      engine_attrs={...},
      fail_class=span.retry.fail_class,
      cause_attribution=span.retry.cause_attribution,
      ts_iso8601=now()
    )
```

**Composition with F2 state-ledger.** The `idempotency_key` is the harness-canonical join key per C-IS-10 §10.2; D6 ingestion-time lookup precedes the dedup decision. ADR-D1 v1.2 §1.1.2.2 declares the ledger entry shape extension with `original_trace_id` + `original_span_id` fields; D6 §14.5.1 dedup is the consumer of those fields.

**Hash-chain integrity composition.** The F2 state-ledger entry hash-chain construction (per `Spec_Information_Substrate_v1.md` C-IS-05 hash-chain construction discipline) extends at v1.3 to include `original_trace_id` + `original_span_id` fields:

```
ledger_entry_hash = SHA-256(
  prev_entry_hash ||
  idempotency_key ||
  original_trace_id ||
  original_span_id ||
  engine_attrs ||
  fail_class ||
  cause_attribution ||
  ts_iso8601
)
```

The three-way seam (C-IS-05 storage primitive / hash-chain integrity discipline / sqlite ledger_entries schema implementation) is preserved without Layer-3 promotion per `F2-12_Council_Deliberation_Output.md` §5.3 reconciliation.

#### §14.5.2 Replay-aware dedup with retry orthogonality (v1.3; new sub-section per D6 v1.2 §1.5.1)

Dedup at trace-ingestion does NOT collapse retry attempts. Each retry attempt is a DISTINCT cost-attribution unit; the dedup algorithm at §14.5.1 collapses only `deterministic_replay` re-reads of the SAME attempt, not different attempts of the same operation.

**Orthogonality discriminators.** Two discriminators compose orthogonally:

| Discriminator | Domain | Discriminates |
|---|---|---|
| `retry.attempt_number` | integer (1..N) | Attempts within a parent operation (attempt 1 vs attempt 2 vs ... vs attempt N) |
| `engine.replay_disposition` | enum (5 values per CP spec v1.3 §9.1 / D1 v1.2 §1.1.1) | Replay-vs-fresh-execution within an attempt |

**Dedup outcome matrix.**

| `retry.attempt_number` | `engine.replay_disposition` | Dedup outcome |
|---|---|---|
| 1 | `deterministic_replay` | DROP if F2 ledger entry matches (idempotency_key + trace_id + span_id + cause_attribution); ERROR if mismatch (per §14.5.3) |
| 1 | `checkpoint_resume` | RECORD as new replay-derived span; cost accrues for attempt 1 |
| 2 | `deterministic_replay` | DROP if F2 ledger entry for attempt 2 matches; ERROR if mismatch |
| 2 | `checkpoint_resume` | RECORD as new retry attempt 2's replay-derived span; cost accrues for attempt 2 |
| 1 | `no_replay` | RECORD if first ingestion; ERROR if re-ingestion (unexpected for no_replay) |
| 2 | `no_replay` | RECORD as new attempt 2; cost accrues for attempt 2 |
| 1 | `reconciler_iteration` | RECORD with iteration_number discriminator from `reconciler.iteration_number` |
| 1 | `wal_consume` | RECORD with consumer_group discriminator from `wal.consumer_group` |

**Per-attempt F2 state-ledger entry shape.** Each retry attempt produces a distinct F2 state-ledger entry. The parent operation has ONE `idempotency_key`; each retry attempt joins via that key but is a DISTINCT entry with `retry.attempt_number` as discriminator within the key's join set. The ledger filter at attempt N reads the join set ordered by `retry.attempt_number`; ledger entries are per-attempt, not per-operation.

#### §14.5.3 cause_attribution invariance check at deterministic_replay (v1.3; new sub-section per D6 v1.2 §1.5.2)

Under `engine.replay_disposition=deterministic_replay`, the dedup algorithm at §14.5.1 includes a cause_attribution invariance check. If the replayed span carries a different `retry.cause_attribution` than the F2 state-ledger entry's stored cause_attribution, this signals replay-introduced semantic divergence — a violation of the deterministic-replay contract.

**Invariance check.**

```
if span.engine.replay_disposition == "deterministic_replay":
  assert span.retry.cause_attribution == ledger_entry.cause_attribution
```

**Escalation on mismatch.** Mismatch ESCALATES to ERROR class:

| Field | Value on mismatch |
|---|---|
| `validator.fail.class` | `terminal-fail-exit` (C5 5-class taxonomy per C-CP-21 §21.5) |
| `validator.fail.cause_attribution` | `replay_semantic_divergence` (new value added to C5 cause_attribution catalog at this revision) |
| `validator.fail.permanence` | `permanent` |
| Always-sampled per C-OD-09 | Yes (validator.fail.permanence=permanent always-sampled per C-OD-09 §9.2) |

The escalation signals an engine-replay-contract violation: the engine claims `deterministic_replay` disposition but the replay produced a different cause_attribution than the original execution. This is a substrate-level integrity violation requiring operator investigation (HITL escalation per `c11-operator-local` SKILL.md mandatory-HITL triggers + `c10-action-safety` SKILL.md eleven-trigger catalog).

**Cause_attribution catalog extension.** The C5 cause_attribution catalog (per `c5-validation-contract` SKILL.md reconciliation; ~15 values bounded) extends with one new value at v1.3: `replay_semantic_divergence`. Cross-ADR coordination: ADR-D5 v1.2 §1.10.1 `validator.fail.cause_attribution` open-set enum absorbs the new value at the next D5 revision (forward-flagged; not blocking this revision).

#### §14.5.4 Per-attempt cost-attribution discipline (v1.3; new sub-section per D6 v1.2 §1.5.3)

Cost-attribution-per-span at §14.1–§14.4 accrues per attempt for re-emitting `engine.replay_disposition` values; cost does NOT aggregate across attempts under any disposition.

**Per-attempt cost accrual.**

| Disposition | Cost accrual semantics |
|---|---|
| `deterministic_replay` | ZERO additional cost accrual at replay; cost was accrued at first execution; ledger entry preserves cost figure |
| `checkpoint_resume` | NEW cost accrual at resume; per-attempt cost is independent of pre-checkpoint accrual; resumed attempt's cost adds to the parent operation's total cost |
| `no_replay` | First execution cost only; re-ingestion is ERROR |
| `reconciler_iteration` | NEW cost accrual per iteration; each iteration is an independent operation cost-wise |
| `wal_consume` | NEW cost accrual per consumption; each consumer's processing is independent cost-wise |

**Parent operation total cost.** The parent operation's total cost is the SUM of per-attempt costs across all retry attempts (per `F2-12_Council_Deliberation_Output.md` §6.8 resolution point 6). The roll-up:

```
total_cost(parent_operation) =
  Σ cost(retry-attempt child span_i) for i in 1..N
```

`deterministic_replay` re-reads of any attempt contribute zero to the sum (cost was accrued at first execution; replay re-reads are idempotent at cost level).

**Cross-axis composition with §C-OD-23 operator-burden eval primitive.** The per-attempt cost-attribution composes with C-OD-23 operator-burden eval primitive dashboard binding: expected-HITL-invocations-per-session × per-HITL-cost rolls up against per-attempt cost-attribution at the per-operation aggregation level. C8's eval primitives (per `c8-eval-engineer` SKILL.md) consume per-attempt cost as substrate without re-aggregation.

**Deferred to implementation discretion.** Specific cost-attribution-per-span emission mechanism per OTel SDK; specific per-cell cost-rollup query implementation at backend; specific BASE_INPUT / BASE_OUTPUT rate-table refresh cadence (deployment-binding-time per C-OD-15 §15.2); specific cross-family `provider_discriminator` cost rollup query at backend per C-OD-15 §15.1.

---

## §15 C-OD-15 through §22 C-OD-22

[All sub-sections preserved verbatim from v1.2.]

---

## §23 C-OD-23 — Operator-burden eval primitive dashboard binding

[Preserved verbatim from v1.2.]

---

## §[carry-forwards]

### [CF-1] F2-12 — D1 v1.1 → v1.2 + D6 v1.1 → v1.2 replay-trace-emission contract (✅ CLOSED at v1.3)

**Status (v1.3 amendment).** ✅ **CLOSED** at OD spec v1.3 filing per ADD v1.3 §6.3.1 cascade Step 5b row. Contract-level absorption at §14.4 Replay-safe composition row + §14.5 ACTIVE → CLOSED transition + §14.5.1 dedup algorithm + §14.5.2 orthogonality + §14.5.3 invariance + §14.5.4 per-attempt cost-attribution. Closure execution path table recorded at §14.5. Formal `closure_pending false` declaration deferred to `F2-12_Closure_Declaration.md` at cascade close.

### [CF-2] Workflow §7 substrate-skill propagation

[Preserved verbatim from v1.2.]

---

## §[traceability]

[Preserved verbatim from v1.2 except D6 row-label version updated v1.1 → v1.2; cell marks preserved (v1.3 amendments at existing C-OD-14 contract site; no new contracts added).]

---

## §[coherence pass]

[Audits preserved verbatim from v1.2 as v1.2 point-in-time historical audit; v1.3 amendment-site verification inline per Workflow v1.7 §7 fidelity-grammar discipline. The four `spec-writer` SKILL.md §"Workflow at runtime" disciplines verify at each v1.3 amendment site: inputs read (PRD v1.1 + ADD v1.3 + ADR-D6 v1.2 + ADR-D1 v1.2 + CP spec v1.3); ingestion contract per layer (council deliberation substrate + ADR substrate); tensions surfaced (T-perm-2 ENGAGED at sub-scope (iii) reconciled via idempotency_key composition; T-perm-3 ENGAGED at sub-scope (ii) honored at default — both preserved at v1.3); self-audit (no Pattern P1 cross-artifact name drift across cascade artifacts; no Pattern P2 verbatim-claim-contradicted).]

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Operational_Discipline_v1_3.md` |
| Filing destination | `/mnt/user-data/outputs/Spec_Operational_Discipline_v1_3.md` |
| Status | Proposed (pending F2-12 cascade close per cascade Step 6 plan v2.2 filings) |
| Predecessor | `Spec_Operational_Discipline_v1.md` (v1.0 → v1.1 → v1.2 baseline) |
| Substrate consumed | PRD v1.1 R-OD-05 + ADD v1.3 §3.4.1 + ADR-D6 v1.2 §1.5–§1.5.3 + ADR-D1 v1.2 §1.1.1 + §1.1.2.2 + CP spec v1.3 C-CP-08 + C-CP-09 (cascade Step 5a co-revision) |
| Successor | `Implementation_Plan_Operational_Discipline_v2_2.md` (F2-12 cascade Step 6b) |
| F2-12 closure status | ✅ CLOSED at cascade Step 5b (this artifact) |
| Workflow discipline | `Project_Workflow_v1_7.md` §7 fidelity-grammar |
| Date | 2026-05-14 |

*Filed at F2-12 cascade Step 5b close. C-OD-14 contract surface extended with dedup algorithm + per-attempt cost-attribution; §14.4 Replay-safe composition row revised from promissory to dedup-algorithm-specific; §14.5 transitioned from F2-12 ACTIVE → ✅ CLOSED with four new sub-sections §14.5.1 (dedup algorithm pseudocode) + §14.5.2 (orthogonality discriminators + outcome matrix) + §14.5.3 (cause_attribution invariance check + ESCALATION to terminal-fail-exit) + §14.5.4 (per-attempt cost-attribution discipline + parent operation total cost roll-up). Step 5 complete: 5a + 5b both filed. Cascade segment boundary per OD-F212-4.A. Recommended next cascade step: Step 6a (CP plan v2.2 revision pass) + Step 6b (OD plan v2.2 revision pass) per `F2-12_Closure_Path_Execution_Kickoff.md` §3.2 — U-CP-20 + U-CP-21 + U-CP-55 + U-OD-14 + U-OD-20 plan-level absorption against this CP spec v1.3 + OD spec v1.3.*