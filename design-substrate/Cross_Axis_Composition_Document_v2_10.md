# Cross-Axis Composition Document (v2.10)

*Delta over v2.9. v2.10 is a narrow-scope bookkeeping refresh of the §0.3 action_id prefix discriminator table — appending a `validator:` row with production-consumer cite to runtime spec v1.22 §14.15.2 step 7 (Reading B validator-composer arc landing per `.harness/reading_b_validator_composer_arc_scoping.md`). The `validator:` discriminator itself is not new — it was introduced in the v2.6 §2.3.7 CP→OD bucket composer-arc absorption (ValidatorFramework row, one of 5 new typed seams at v2.6). v2.10 documents the now-operational production consumer per the runtime spec v1.22 §14.15.2 step 7 self-flag ("the CXA v2.9 §0.3 action-id prefix enumeration MAY need refresh at follow-on bookkeeping arc"). No new edges. No aggregate matrix change. No per-axis attribution change. No new cross-axis cascade. Reading B operational landing scope discipline preserved: §0.3 refresh is the only substantive amendment; the v2.9 cost-attribution row 8 publication and all v2.8 + v2.7 + v2.6 substantive content preserved verbatim by reference.*

## §0 Change note (v2.9 → v2.10)

### §0.1 Revision context — `validator:` discriminator production-consumer cite refresh

Per runtime spec v1.22 §14.15.2 step 7 self-flag (the v1.22 amendment that landed the Reading B validator-composer arc per `.harness/reading_b_validator_composer_arc_scoping.md` + fork doc `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.2): the `validator:` action_id prefix is now consumed at a canonical production composer at runtime spec v1.22 §14.15.2 step 7 (the ValidatorEscalationGateComposer's audit-write 4-substep sequence — `action_id=Identifier(f"validator:{step_action_id}:escalation")`). The runtime spec v1.22 §14.15.2 step 7 parenthetical surfaces the bookkeeping owe: "The `validator:` action_id prefix is a NEW discriminator at v1.22; the CXA v2.9 §0.3 action-id prefix enumeration MAY need refresh at follow-on bookkeeping arc — surfaced as adjacent finding NOT patched per FM-2." v2.10 patches the refresh.

**Clarification on "NEW at v1.22".** The runtime spec self-flag prose at §14.15.2 step 7 says `validator:` is "a NEW discriminator at v1.22" — this is correct from the **runtime-spec-side production-consumer perspective** (Reading B was the first runtime arc to land a composer firing `validator:` prefix). From the **CXA-side commitment perspective**, however, `validator:` was already canonical at v2.6 §2.3.7 CP→OD bucket composer-arc absorption (the ValidatorFramework row was one of 5 new typed seams at v2.6 — see workspace `CLAUDE.md` §1.1 CXA row: "ValidatorFramework + PauseResumeProtocol + PerServerTrustEvaluator + HITL webhook delivery + HITL operator-burden — all 5 sharing the `cp_audit_to_od_audit` converter with distinct F2 action_id prefixes"). v2.10 reconciles the two perspectives by documenting the production-consumer cite at the §0.3 discriminator table while preserving the v2.6 CXA-side canonicalization timestamp.

### §0.2 Sections revised

§0 (this change note); §0.3 discriminator-extension table (new row appended — `validator:`). All other sections preserved verbatim from v2.9 (which preserved verbatim from v2.8 + v2.7 + v2.6). No §2.x amendment — `validator:` is not a new edge (it canonicalized at v2.6 §2.3.7 CP→OD bucket); no aggregate matrix change; no per-axis outbound attribution change; no acceptance criterion change at any prior row.

### §0.3 `validator:` discriminator production-consumer cite refresh (extension of v2.9 §0.3 table)

The v2.9 §0.3 action_id-prefix discriminator table (introduced at v2.9 with the `cost:` row appended) is extended at v2.10 with one new row documenting the production consumer for the existing `validator:` discriminator. The `validator:` row references its existing canonical CXA home at v2.6 §2.3.7 (ValidatorFramework row, one of 5 v2.6 composer-arc absorption seams) and its production consumer at runtime spec v1.22 §14.15.2 step 7 (Reading B landing).

| Discriminator | Action_id pattern | Bucket row | Added | Production consumer |
|---|---|---|---|---|
| `cost:` | `cost:<workflow_id>:<step_action_id>` | **v2.9 §2.3.7 row 8** | v2.9 | OD spec v1.10 §C-OD-26.6 CostRecordAuditPayload (per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` Sub-arc B sequel landing 2026-05-24) |
| `validator:` | `validator:<step_action_id>:escalation` | **v2.6 §2.3.7 ValidatorFramework row** (one of 5 v2.6 composer-arc absorption seams) | v2.6 (CXA-side canonicalization); **runtime spec v1.22 §14.15.2 step 7 production-consumer landing** (Reading B 2026-05-24) | runtime spec v1.22 §14.15.2 step 7 (ValidatorEscalationGateComposer audit-write 4-substep sequence — `Identifier(f"validator:{step_action_id}:escalation")`) |

The `validator:` action_id pattern body `<step_action_id>:escalation` follows the 2-segment convention (step-anchored + outcome-tagged) — distinct from the `<workflow_id>:<step_action_id>` 2-segment pattern at `pause:`/`resume:`/`cost:` rows. The pattern-body divergence is canonical at runtime spec v1.22 §14.15.2 step 7 (the production-consumer arc); CXA v2.10 documents the divergence without normalizing it (per FM-2 — pattern-body normalization is a runtime-spec concern, not CXA scope).

### §0.4 Aggregate matrix delta

**No matrix change at v2.10.** v2.9 §2.1 4×4 adjacency matrix (CP→OD bucket cell = 8; aggregate 100; genuine 30; convention-level 46; phase-2-runtime 24) preserved verbatim. `validator:` is not a new CP→OD edge — it canonicalized at v2.6 §2.3.7 ValidatorFramework row, which was already counted in the v2.6 → v2.9 bucket cardinality (2 → 7 → 8). v2.10 §0.3 refresh updates the discriminator-table presentation only; it does not change edge cardinality, edge genuineness classification, or per-axis attribution.

**§2.4 per-axis outbound posture summary.** Unchanged from v2.9 (CP outbound 62; OD outbound 27; aggregate genuine 30). `validator:` row's CP-axis attribution at v2.6 §2.3.7 preserved verbatim.

### §0.5 Status posture

Proposed (v2.9) → **Proposed (v2.10)**. v2.10 is a narrow-scope additive bookkeeping refresh — one new row appended at §0.3 discriminator-table + §0.7 cross-cite to runtime spec self-flag patch. No prior edge classification change; no prior aggregate matrix change; no prior edge spec-version cite change; no acceptance criterion change at any prior row. The v2.9 cost-attribution row 8 publication preserved verbatim; all v2.8 path-γ cite bumps preserved verbatim; all v2.6 + v2.7 + v2.8 substantive content preserved verbatim by reference.

### §0.6 Forward-cite acknowledgement (per v2.6 §0.5 forward-cite hygiene)

The `validator:` row production-consumer cite (runtime spec v1.22 §14.15.2 step 7) is a backward-cite to a now-published canonical (runtime spec v1.22 landed at commit `918f94a` per Reading B arc). The cite is byte-exact at v2.10 publication; no forward-cite at v2.10.

The v2.9 `cost:` row forward-cite was `OD spec v1.10 §C-OD-NN` at v2.9 publication; it resolved at OD spec v1.10 §C-OD-26.6 CostRecordAuditPayload landing per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` Sub-arc B sequel (2026-05-24). v2.10 updates the §0.3 table `cost:` row "Production consumer" cell with the resolved cite per byte-exact discipline.

### §0.7 Adjacent defects surfaced (not patched per FM-2 no-extension discipline)

(i) **§2.3.7 bucket-note prose enumeration drift.** The v2.6 bucket-note prose at §2.3.7 (preserved verbatim through v2.7 + v2.8 + v2.9) reads "7 action_id prefix discriminators" but then enumerates 8 names (`dispatch:` / `hitl:` / `hitl_webhook:` / `operator_burden:` / `validator:` / `pause:` / `resume:` / `mcp_trust:`). The count-vs-enumeration internal inconsistency predates v2.10 scope and is not patched here per FM-2 no-extension discipline (Reading B scope discipline applied at 14 sites preserved as analogous example). The discrepancy is informational — the §0.3 discriminator-extension table at v2.9 + v2.10 supersedes the v2.6 prose enumeration as the canonical reference, and the table is internally consistent.

(ii) **`mcp_trust:` discriminator production-consumer cite.** The §0.3 discriminator-extension table at v2.10 enumerates only `cost:` (v2.9) and `validator:` (v2.10) production consumers — it does not yet enumerate the 5 other discriminators (`dispatch:` / `hitl:` / `hitl_webhook:` / `operator_burden:` / `pause:` / `resume:` / `mcp_trust:`). Full enumeration would normalize the table presentation but is out of scope per the v2.10 narrow-scope refresh framing. Surfaced; NOT patched at v2.10 per FM-2 (full enumeration is operator-discretion timing at follow-on bookkeeping arc).

(iii) **Runtime spec v1.22 §14.15.2 step 7 self-flag flip owed.** The runtime spec v1.22 §14.15.2 step 7 parenthetical reads "the CXA v2.9 §0.3 action-id prefix enumeration MAY need refresh at follow-on bookkeeping arc — surfaced as adjacent finding NOT patched per FM-2." With v2.10 publication, the self-flag is now stale — the refresh has been patched at CXA v2.10 §0.3. The runtime-spec-side self-flag flip is a paired co-publication at runtime spec v1.22 → v1.23 (paired narrow-scope amendment); it is co-published with v2.10 per the established v2.9 ↔ OD spec v1.10 / U-CP-72 / U-OD-41 co-publication pattern. Surfaced; co-published this arc.

### §0.8 Downstream absorption owed (post-v2.10)

(a) Workspace `CLAUDE.md` §2.4 CXA row version bump (v2.9 → v2.10).
(b) Workspace `CLAUDE.md` §2.4 CXA row description amendment: append v2.10 narrow-scope refresh note (§0.3 `validator:` discriminator production-consumer cite refresh; no cardinality change; preserves v2.9 cost-attribution row 8 publication verbatim).
(c) Runtime spec v1.22 → v1.23 paired narrow-scope amendment at §14.15.2 step 7 self-flag flip (parenthetical updated from "MAY need refresh ... NOT patched per FM-2" → "patched at CXA v2.10 §0.3"). Co-published this arc per §0.7(iii).
(d) `harness-cxa/CLAUDE.md` discriminator-table refresh per §0.3 — operator-discretion timing.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Cross_Axis_Composition_Document_v2_10.md` |
| Version | v2.10 |
| Filing event | `validator:` discriminator production-consumer cite refresh per runtime spec v1.22 §14.15.2 step 7 self-flag + Reading B validator-composer arc landing per `.harness/reading_b_validator_composer_arc_scoping.md`. Narrow-scope bookkeeping refresh; no §2.x amendment; no cross-axis cascade. 2026-05-24 |
| Predecessor | `Cross_Axis_Composition_Document_v2_9.md` (preserved verbatim outside the §0 amendment site enumerated at §0.2) |
| Successor | (none — current canonical) |
| Aggregate count | **100 canonical cross-axis relationships** (unchanged at v2.10). **30 genuine typed seams** (unchanged). Convention-level **46** preserved. Phase-2-runtime **24** preserved. 30 + 46 + 24 = 100. |
| CP→OD bucket | **8 canonical edges** (unchanged at v2.10). All 8 share the `cp_audit_to_od_audit` converter at `harness-cxa/src/harness_cxa/cp_audit_conversion.py`; F2-action_id-prefix discriminator at OD audit-trace consumers. The `validator:` row (one of the 5 v2.6 composer-arc absorption seams at the ValidatorFramework row) now has production-consumer cite to runtime spec v1.22 §14.15.2 step 7 per v2.10 §0.3 refresh. |
| Per-axis attribution | Unchanged from v2.9 (CP outbound 62; OD outbound 27; §2.1-vs-§2.4 attribution divergence at row 8 preserved). |
| `validator:` discriminator status | Production-consumer-cited at v2.10 (was canonical-only at v2.6 through v2.9). CXA-side canonical at v2.6 §2.3.7 ValidatorFramework row preserved verbatim; v2.10 adds production-consumer cite cell to §0.3 discriminator-extension table. |
| Operator authority | Runtime spec v1.22 §14.15.2 step 7 self-flag (Reading B operator-ratified 2026-05-24 per `.harness/reading_b_validator_composer_arc_scoping.md` + fork doc `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.2 + workspace AskUserQuestion 2026-05-24) + workspace `CLAUDE.md` §2.4 v2.x published-pairing constraint |
| Related forks | `.harness/class_1_fork_validator_composer_arc_stage_4_absence.md` §3.2 Reading B (LANDED at v1.22; `validator:` production-consumer cite refresh is bookkeeping completion) |
| Related memory | `[[verification-shape-sharpened-grep-vs-e2e]]` (verification-shape applied at U-RT-92 e2e for production-consumer existence; bookkeeping refresh is byte-exact byproduct) |
| Date | 2026-05-24 |
