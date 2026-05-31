# Phase 7d retirement events — batch-50

*Filed 2026-05-31 closing **H_T-IS-2 PARTIAL → RETIRED** — the final transit of the R-003 producer-site cascade. The cross-tier traceability invariant is now runtime-enforced at append-time: every active-workflow-context state-ledger write populates `EntryPayload.procedural_tier_snapshot_ref` via the resolver, displacing the H_E convention-substitution (operator-authored `action_id` text / manual cross-tier traceability in ledger entries). All 13 producer sites are handled — 6 §16.5 composers (PR #107) + 4 lifted (R-003 Cluster A PR #136 + Cluster B PR #137) + 3 documented `None`-canonical (outside active-workflow context per IS spec v1.3 §C-IS-05 §5.1). X-AL-2 BOTH conjuncts MET. Unblocks roadmap `R-001-h-t-is-2-retired`.*

---

## §0 Batch context

**Status type: 1 PARTIAL → RETIRED transition (H_T-IS-2).** Closes the substrate-lift arc opened at batch-49 (STILL-BOUNDED → PARTIAL). This is a **substantive substitution-retirement** — NOT a vacuous / authoring-only / categorical-mismatch close. The H_E convention surface (manual cross-tier traceability encoded in `action_id` text per `CLAUDE.md`-declared tier-naming convention) is empirically displaced by a typed, resolver-populated, hash-chained sidecar field at every active-workflow-context producer site.

**Closure shape — substantive-substrate-lift completed.** batch-49 landed the carrier + resolver (first conjunct). This batch records the second conjunct: all producer-site call-sites are lifted (active-workflow context) or documented `None`-canonical (outside-context). The convention surface is no longer invoked at any active-workflow-context substitution site.

**Lineage.** batch-49 (STILL-BOUNDED → PARTIAL, substrate landed) → PR #107 (6 §16.5 CP→IS composers populate the sidecar, Reading C apply `89915af`) → PR #136 (R-003 Cluster A: runtime dispatchers) + PR #137 (R-003 Cluster B: CP sites + 3 `None`-canonical docs) + PR #138 (roadmap R-003 RESOLVED) → this batch (PARTIAL → RETIRED).

**Conclusion (preview):** **1 PARTIAL → RETIRED transit** (H_T-IS-2). IS-axis advances 8/9 RETIRED + 1 PARTIAL → **9/9 RETIRED = 100%** (FIRST fully-RETIRED axis at the RETIRED view, not just pipeline-advanced). Workspace RETIRED 45/54 → **46/54 = 85.2%**; pipeline-advanced UNCHANGED at 49/54 = 90.7% (IS-2 was already counted as PARTIAL); workspace PARTIAL decrements by 1 (IS-2 transits out). Counts anchored to the batch-49 footer baseline.

---

## §1 H_T-IS-2 PARTIAL → RETIRED

### §1.1 Pre-transition state (batch-49 close, 2026-05-30)

H_T-IS-2 carried as PARTIAL per `harness-is/CLAUDE.md` §4.1 (post-batch-49): substrate landed (sidecar field carrier + `StateLedgerEntry` D-derivative field + canonicalize discipline at harness-is; `resolve_procedural_tier_snapshot(ctx)` + `make_procedural_tier_snapshot_resolver(ctx)` resolver primitive at runtime axis per Q-γ=(γ-2)), but the X-AL-2 second conjunct was BOUNDED — producer-site call-sites had not yet been lifted to populate `procedural_tier_snapshot_ref` at firing time. The PARTIAL gate-text enumerated "7 producer-site lifts remaining post-PR #107" (6-of-13 landed at PR #107).

### §1.2 Transition trigger (this batch, 2026-05-31)

**R-003 producer-site cascade complete.** All 13 producer sites are now handled:

| # | Site | Class | Disposition | Landed |
|---|---|---|---|---|
| 1 | `harness-cp/.../per_step_override_evaluator.py` (U-CP-14) | §16.5 composer | LIFT — `procedural_tier_snapshot_resolver()` at EntryPayload | PR #107 `89915af` |
| 2 | `harness-cp/.../workload_binding_engine_class_selection.py` (U-CP-27) | §16.5 composer | LIFT | PR #107 |
| 3 | `harness-cp/.../pause_resume_protocol.py` workflow-layer (U-CP-30) | §16.5 composer | LIFT | PR #107 |
| 4 | `harness-cp/.../hitl_as_tool_call_rewriting.py` (U-CP-37) | §16.5 composer | LIFT | PR #107 |
| 5 | `harness-cp/.../pause_resume_protocol.py` `capture_pause_snapshot` engine-layer (U-CP-49) | §16.5 composer | LIFT | PR #107 |
| 6 | `harness-cp/.../pause_resume_protocol.py` `attempt_resume` engine-layer (U-CP-50) | §16.5 composer | LIFT | PR #107 |
| 7 | `harness-runtime/.../lifecycle/sub_agent_dispatch.py:~488` `_compose_and_persist_audit` F2 `f2_payload` | active-workflow context | **LIFT** — resolver field on `@dataclass(slots=True)`, built at bootstrap stage 5 | **PR #136 (R-003 Cluster A)** |
| 8 | `harness-runtime/.../lifecycle/hitl_gate_composer.py:~787` `_compose_and_persist_audit` F2-HITL `f2_payload` | active-workflow context | **LIFT** — same dataclass-field + stage-5 wiring pattern | **PR #136 (R-003 Cluster A)** |
| 9 | `harness-cp/.../sibling_ledger_entry_composition.py:~158` `construct_sibling_ledger_entry` (U-CP-34) | active-workflow context | **LIFT** — `procedural_tier_snapshot_ref` param threaded from `RuntimeCpIsWiring.emit_sibling_ledger_entry` caller | **PR #137 (R-003 Cluster B)** |
| 10 | `harness-cp/.../workflow_driver.py:~1385` `_append_step_ledger_entry` | active-workflow context | **LIFT** — resolver via `DriverContext` Protocol + `HarnessContext`, wired at stage 6 | **PR #137 (R-003 Cluster B)** |
| 11 | `harness-runtime/.../lifecycle/audit_writer.py:~120` `append` | OUTSIDE (audit-wrap of pre-signed OD entries; separate ledger family) | **DOCUMENT** `None`-canonical per IS §5.1 — code comment | **PR #137 (R-003 Cluster B)** |
| 12 | `harness-runtime/.../lifecycle/as_is_wiring.py:~110` `append` secret-fetch | OUTSIDE (fires at bootstrap / provider-construction) | **DOCUMENT** `None`-canonical | **PR #137 (R-003 Cluster B)** |
| 13 | `harness-is/.../shadow_git_rollback.py:~111` `perform_rollback` | OUTSIDE (administrative / recovery) | **DOCUMENT** `None`-canonical | **PR #137 (R-003 Cluster B)** |

The 4 active-workflow-context LIFTs (sites 7–10) mirror the canonical `RuntimeCpIsWiring.procedural_tier_snapshot_resolver` pattern (the 6 §16.5 composers): the resolver closure is built by `make_procedural_tier_snapshot_resolver(ctx)` and invoked zero-arg at `EntryPayload(...)` construction. The 3 `None`-canonical DOCUMENTs (sites 11–13) are spec-correct per IS spec v1.3 §C-IS-05 §5.1 — entries written outside an active workflow context carry `procedural_tier_snapshot_ref = None` canonically; they are NOT invocations of the convention-substitution surface.

### §1.3 X-AL-2 both-conjuncts disposition — RETIRED

Per `Phase_7_Meta_Architecture_v1.md` §7.7 X-AL-2 (retirement = condition-A ∧ condition-B):

| Conjunct | Verification | Verdict |
|---|---|---|
| **(A) Cited unit IDs landed** | Artifact-tier registry substrate (U-IS-03) + `EntryPayload`/`StateLedgerEntry` sidecar + canonicalize discipline (U-IS-11) + resolver primitive (U-RT-112) all landed at batch-49; the 6 §16.5 CP→IS composers landed at PR #107; the R-003 producer-site lift units landed at PR #136 + #137. | **MET** |
| **(B) H_E surface no longer invoked at substitution site** | The H_E convention-substitution (manual cross-tier traceability via `action_id` text encoding per `CLAUDE.md`-declared tier-naming convention) is no longer invoked at any active-workflow-context producer site: all 10 active-context sites populate the typed `procedural_tier_snapshot_ref` sidecar via the resolver. The 3 outside-context sites carry spec-canonical `None` per IS §5.1 (not convention-surface invocations). Cross-tier traceability is now programmatic + hash-chained, not manual. | **MET** |

Both conjuncts MET → **RETIRED** (not RETIRE-READY). Empirically verified at HEAD `e736f53` (origin/main post-PR #139): all 4 lifted sites populate the sidecar via the resolver; all 3 documented sites carry the IS §5.1 `None`-canonical comment; no active-workflow-context producer site bypasses the resolver.

### §1.4 X-AL-1 substrate-boundary disposition

Per X-AL-1: the substrate boundary is preserved through retirement. Pre-retirement, the procedural-tier reference lived in `CLAUDE.md`-prose + operator-authored `action_id` text (H_E owns the convention). Post-retirement, H_T owns the invariant: the typed `procedural_tier_snapshot_ref` sidecar is resolved in-process (`resolve_procedural_tier_snapshot(ctx)`) and contributes to the hash chain (`entry_hash.canonicalize`) at every active-workflow-context append. The boundary moved from "H_E convention" to "H_T in-process resolver"; the boundary itself is preserved.

### §1.5 X-AL-3 disposition

No H_T design extension at this retirement. The contract surfaces (IS spec v1.3 §C-IS-05 §5.1 sidecar + §5.2 resolver + §C-IS-02 line 170 substantive-runtime-gate) were authored at the Phase 7 substantive-amendment arc (batch-49, spec v1.3) under operator ratification, and the producer-site lifts (R-003) were operator-ratified scope (AskUserQuestion Option A 2026-05-31, recorded at `.harness/R-003-checkpoint.md` §1). This batch records the retirement transit only; it authors no new contract.

---

## §2 Cross-axis cascade discipline

**ZERO new cross-axis cascade at this arc.** The producer-site lifts already landed (PR #107 / #136 / #137); this batch is the retirement-event record. The CP→IS Pattern-P1 seams for the 6 §16.5 composers were absorbed into CXA at v2.17 (rows 38–43, PR #92); the R-003 lifts at sites 7–10 are additional consumers of the already-canonical IS-axis sidecar substrate (no NEW typed edge — they populate a field the IS axis owns).

- **CP spec / AS spec / OD spec / CXA / ADR / ADD / PRD PRESERVED VERBATIM** at this arc (retirement-event filing; no design-substrate amendment).

---

## §3 Adjacent observations

### §3.1 IS-axis fully RETIRED at the RETIRED view

With H_T-IS-2 RETIRED, the IS axis reaches **9/9 RETIRED = 100%** — the first axis to be fully RETIRED at the strict RETIRED view (not merely pipeline-advanced). (CP-axis §4.1 is fully RETIRED in the pipeline-advanced sense with authoring-only + bounded-residual rows; IS axis has no STILL-BOUNDED-INDEFINITELY residual.)

### §3.2 Cascade-completion close-pattern

H_T-IS-2 is a `[[substrate-pre-landed-consumer-deferred-multi-arc-lift]]` close: substrate landed at one arc (batch-49), consumers lifted across later arcs (PR #107 + R-003 #136/#137), retirement filed when the last active-workflow-context consumer was lifted. Mirror precedent: the multi-arc consumer-lift shape catalogued at runtime spec v1.37 + OD-3/OD-4 batch-34/35.

### §3.3 Roadmap cascade

This batch closes roadmap `R-001-h-t-is-2-retired` (the R-003 `next_pointer`). Cascade → consolidated roadmap dashboard refresh (`R-003` already RESOLVED; `R-001-h-t-is-2-retired` → RESOLVED; next action re-derived).

---

## §4 Filing footer

| Field | Value |
|---|---|
| Batch | 50 |
| Filed at | 2026-05-31 |
| Filing authority | Roadmap `R-001-h-t-is-2-retired` (`Project_Roadmap_v1.md` §5.2; dashboard ACTIVE) + X-AL-2 both-conjuncts verification at HEAD `e736f53` |
| Net delta | 1 PARTIAL → RETIRED (H_T-IS-2). IS-axis 8/9 RETIRED + 1 PARTIAL → **9/9 RETIRED = 100%**. Workspace RETIRED 45/54 → **46/54 = 85.2%** (batch-49 footer baseline); pipeline-advanced UNCHANGED 49/54 = 90.7%; workspace PARTIAL −1 (IS-2 out). |
| Production binding | NONE at this arc (retirement-event filing). The binding landed at PR #107 (6 §16.5 composers) + PR #136 (R-003 Cluster A: `sub_agent_dispatch` + `hitl_gate_composer` resolver fields + stage-5 wiring) + PR #137 (R-003 Cluster B: `workflow_driver` + `sibling_ledger` lifts + 3 `None`-canonical docs). |
| Cross-axis cascade | NONE at this arc. |
| Downstream artifacts | `harness-is/CLAUDE.md` §4.1 H_T-IS-2 row PARTIAL → RETIRED + cumulative-counts refresh (this PR); `.harness/phase-7d-retirement-ledger-v2.md` §11.x supersession entry (this PR, forward-only — §3 snapshot preserved verbatim); roadmap `R-001-h-t-is-2-retired` → RESOLVED + dashboard refresh (consolidated cascade). |
