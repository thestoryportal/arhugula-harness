# Class 1 Fork — U-CP-63/64 `PauseReason` + `capture_pause_snapshot` name collision

**Filed:** 2026-05-21 (cluster 10-CP-B open, pre-LOC carrier inspection)
**Status:** OPEN — operator decision required before any U-CP-62..65 implementation
**Sibling pattern:** `[[class_1_fork_u_cp_58_validator_fail_class_collision]]` (path β rename, ratified 2026-05-21)
**Detection mode:** pre-LOC `grep` of cited Python identifiers across landed code (workspace CLAUDE.md §4.3 silent-absorption discipline)

---

## §1 — Defect surface

### §1.1 Landed code

`harness-cp/src/harness_cp/pause_resume_protocol.py` (landed at U-CP-49, cites C-CP-22 §22.1) declares:

| Identifier | Shape | Lines |
|---|---|---|
| `PauseReason` | StrEnum, **4 members** (HITL_INVOCATION_PENDING / CROSS_DEPLOYMENT_BRIDGING_ARC_PAUSE / OPERATOR_INITIATED_PAUSE / ENGINE_NATIVE_PAUSE) | 36–43 |
| `PauseEvent` | Pydantic BaseModel, 5 fields (paused_at / pause_reason / state_summary_snapshot / external_refs_captured / pause_audit_entry_id) | 46–60 |
| `ResumeAttempt` | Pydantic BaseModel, 3 fields | 63–72 |
| `ResumeOutcomeKind` | StrEnum, 4 members | 75–88 |
| `ResumeOutcome` | Pydantic BaseModel, 4 fields | 91–103 |
| `capture_pause_snapshot` | **free function**, signature `(workflow_id: WorkflowID, pause_reason: PauseReason) -> PauseEvent` | 106 (line 121 raises NotImplementedError) |
| `attempt_resume` | **free function**, signature `(attempt: ResumeAttempt) -> ResumeOutcome` | 128 (line 143 raises NotImplementedError) |
| `classify_resume` | free function (live, not stubbed) | 150 |

External landed consumers:
- `harness-cp/src/harness_cp/material_diff_detection.py:41,161` — imports `PauseEvent` (TYPE_CHECKING)
- `harness-runtime/src/harness_runtime/types.py:66` — imports `ResumeOutcomeKind`
- `harness-runtime/src/harness_runtime/lifecycle/hitl_placement.py:93,17,225` — imports symbols + cites `classify_resume`
- `harness-runtime/tests/test_lifecycle_hitl_placement.py:69` — imports `ResumeOutcomeKind`

### §1.2 New spec contract

CP spec v1.10 §26 (NEW) declares **C-CP-26 PauseResumeProtocol** with:

| Identifier | Shape | Source |
|---|---|---|
| `PauseReason` | Enum, **5 members** (EXPLICIT_OPERATOR / HITL_PENDING / VALIDATOR_ESCALATION / TIMEOUT_BOUNDARY / EXTERNAL_DEPENDENCY) | §26.2 |
| `PauseSnapshot` | frozen dataclass, **8 fields** (workflow_id / run_id / step_index / pause_reason / state_summary / snapshot_hash / created_at / state_ledger_anchor) | §26.2 |
| `MaterialDiffPolicy` | Enum, 3 members | §26.2 |
| `ResumeResult` | frozen dataclass, 5 fields | §26.2 |
| `PauseResumeProtocol.capture_pause_snapshot` | **async method on class**, signature `(workflow_id, run_id, step_index, pause_reason) -> PauseSnapshot` | §26.1 |
| `PauseResumeProtocol.attempt_resume` | **async method on class**, signature `(snapshot, *, material_diff_policy) -> ResumeResult` | §26.1 |

Spec v1.10 §44 declares: "All v1.9 content outside the four amendment sites preserved unchanged. C-CP-01 through C-CP-24 (v1.9 §1 through §24) preserved verbatim." → §22 / C-CP-22 still canonical.

### §1.3 Plan instruction

CP plan v2.16 (substantively v2.15 preserved):
- **U-CP-62** → NEW file `harness-cp/src/harness_cp/pause_resume_protocol_types.py` (clean — no collision)
- **U-CP-63** AC #4 → "Existing `harness-cp/src/harness_cp/pause_resume_protocol.py:121` NotImplementedError closed"
- **U-CP-64** → "EXTEND — closes line 143 NotImplementedError"

Plan instructs EXTEND of the OLD module. The OLD line-121 surface is a **free function** with 2-param signature; the new spec §26.1 surface is a **class method** with 4-param signature. Functionally non-substitutive — closing line 121 cannot mean "implement the new spec signature" because the signatures are structurally different.

### §1.4 The collision proper

Three irreducible collisions:

1. **`PauseReason` enum** — same module-level name, **different members** (4 vs 5; none of the new members overlaps the old set). Python cannot resolve both within `pause_resume_protocol.py`.
2. **`capture_pause_snapshot` / `attempt_resume` symbol** — old surface is free function at module scope; new surface is method on `PauseResumeProtocol` class. Coexistable IF and only if module re-exports both, but the old free functions are still cited by AC #4 as line-121/143 NotImplementedError sites.
3. **Plan AC #4 unsatisfiable as literal** — closing line 121 NotImplementedError requires either (a) replacing the old free function body or (b) declaring the new class method body, but the line number 121 cannot simultaneously be the "old free function body" AND a "new class method body" in the same file.

---

## §2 — Routing-target candidates

Per `phase-7-back-flow-routing` SKILL.md §3.1.

### §2.1 Path α — Plan-level absorption (new module home)

| Action | Locus |
|---|---|
| New `PauseResumeProtocol` class homed in NEW file (e.g., `pause_resume_protocol_v2.py` or `explicit_pause_resume_protocol.py`) | CP plan v2.16 → v2.17 |
| Plan U-CP-63/64 file column updated from `pause_resume_protocol.py` → new module name | CP plan v2.16 → v2.17 |
| Plan U-CP-63/64 AC #4 (line-121/143 closure) — STRIKE; old NotImplementedErrors stay raised; old surface remains the U-CP-49 §22.1 carrier | CP plan v2.16 → v2.17 |
| No spec / ADR / CXA change | — |

**Routing:** Phase 6 CP plan revision-pass.
**Cascade:** Per-axis `CLAUDE.md` cluster-table file column pointers.
**Risk:** Old line-121/143 NotImplementedError remains forever; `[[carried-fork-audit-before-cluster]]` accumulates a STILL-OPEN entry for C-CP-22.

### §2.2 Path β — Identifier rename (same pattern as U-CP-58 ValidatorFailClass)

| Action | Locus |
|---|---|
| Old `PauseReason` (4-class) → renamed to `EngineReplayPauseReason` or `LegacyPauseReason` (existing landed code) | 4 landed files renamed + tests |
| Old `PauseEvent` → renamed to `EngineReplayPauseEvent` | Same |
| Old `ResumeOutcomeKind` → renamed to `EngineReplayResumeOutcomeKind` | Same |
| Old `capture_pause_snapshot` / `attempt_resume` free functions → renamed (e.g., `capture_replay_pause_snapshot`) | Same |
| New `PauseResumeProtocol` (§26 surface) reuses canonical names in same module OR new module — operator pick | New + tests |
| Spec citation update — but C-CP-22 §22.1 cites `PauseEvent` / `PauseReason` by name; spec text would need rename absorption | CP spec v1.10 → v1.11 |
| Plan U-CP-63/64 AC #4 (line-121/143 closure) — STRIKE; lines hold the renamed legacy surface | CP plan v2.16 → v2.17 |

**Routing:** Phase 5 spec revision-pass + Phase 6 plan revision-pass.
**Cascade:** ALL landed-code rename + 4 external consumer files + per-axis CLAUDE.md + retirement ledger updates.
**Risk:** Heaviest absorption; renames a v1 surface that already had retirement criterion declarations. Highest blast radius.

### §2.3 Path γ — Spec-level rename of NEW C-CP-26 identifiers

| Action | Locus |
|---|---|
| Spec §26.2 `PauseReason` → renamed to `ExplicitPauseReason` (or `OperatorPauseReason`) | CP spec v1.10 → v1.11 §26 |
| Spec §26.2 `PauseSnapshot` — already distinct from old `PauseEvent`; preserve | — |
| Plan U-CP-62 carriers — type names follow spec rename | CP plan v2.16 → v2.17 |
| OD spec v1.8 §C-OD-30 — cites `PauseReason` enum from CP spec v1.10 §26.2; absorbs rename | OD spec v1.8 → v1.9 |
| OD plan v2.14 U-OD-51 — schema attribute `pause.reason` cites enum; absorbs rename | OD plan v2.14 → v2.15 |
| CXA v2.7 §2.3.7 — already cites C-CP-26 §26 producer; absorbs rename | CXA v2.7 → v2.8 |
| New class method names — left alone; collision with old free functions handled by class-method scope | — |
| Plan U-CP-63/64 AC #4 line-121/143 — STRIKE (old free functions are distinct surface) | CP plan v2.17 |
| Old §22 / U-CP-49 surface — untouched | — |

**Routing:** Phase 5 spec revision-pass (CP + OD) + Phase 6 plan revision-pass (CP + OD) + Phase 6 CXA revision-pass.
**Cascade:** Spec + OD spec + plan + OD plan + CXA — all delta-version files. ZERO landed-code rename. Test-side fresh implementation against renamed surface.
**Risk:** Touches more design-phase artifacts than path β but ZERO already-landed-code-rename. Cleanest at the boundary going forward.

### §2.4 Path δ — Supersession (old §22 deprecated)

| Action | Locus |
|---|---|
| CP spec v1.10 → v1.11 declares §22 deprecated; C-CP-22 retired; U-CP-49 surface removed from canonical | CP spec |
| Old `pause_resume_protocol.py` deleted; new `PauseResumeProtocol` class homed there with new schemas | Landed code + tests |
| ALL external consumers (`material_diff_detection.py` PauseEvent ref; `harness-runtime/types.py` ResumeOutcomeKind; `lifecycle/hitl_placement.py` symbols + `classify_resume`) — rewired to new surface OR deprecated | 4 landed files |
| `lifecycle/hitl_placement.py` cites `classify_resume` (pure decision core); if §22 retired, decision core moves to new module OR retired | Same |
| OD spec / OD plan / CXA — already cite §26 surface; no change | — |

**Routing:** Phase 5 spec revision-pass + workspace landed-code refactor + retirement ledger update.
**Cascade:** Highest blast — but resolves the long-term canonical-authority question. Old C-CP-22 surface goes away entirely.
**Risk:** Largest scope. Touches `material_diff_detection` + runtime layers (`hitl_placement.classify_resume` is a load-bearing pure decision core).

---

## §3 — Halt state

| Field | Value |
|---|---|
| Halt point | U-CP-62 entry (pre-LOC; types file not yet created) |
| Halt timestamp | 2026-05-21 |
| Halt rationale | `PauseReason` enum name collision (4-class vs 5-class) + symbol-scope ambiguity (free-function vs class-method) cannot be resolved without operator decision on routing locus |
| Routing target | Operator decision required between Path α / β / γ / δ |
| Resumption requires | Operator-ratified path + delta-version files at design-phase substrate per chosen path |
| Skill discipline | `phase-7-back-flow-routing` Class 1 + workspace CLAUDE.md §4.3 silent-absorption discipline + carrier-surface-inspection lesson `[[carrier-surface-inspection-catches-namespace-collision]]` from U-CP-58 path β |

---

## §4 — Operator decision surface

```
CLASS 1 FORK DETECTED — HALT PHASE 7b CLUSTER 10-CP-B EXECUTION

Defect locus: CP spec v1.10 §22 (preserved verbatim) + §26 (NEW) name collision
              + CP plan v2.16 U-CP-63/64 AC #4 unsatisfiable as literal
Halt point: U-CP-62 entry (pre-LOC)

Operator decision required:
  (α) Plan-level absorption — new file home for §26 surface; strike line-121/143 AC #4
      → CP plan v2.17 only.
  (β) Rename old C-CP-22 surface to legacy names (path β pattern from U-CP-58)
      → CP spec v1.11 + plan v2.17 + 4 landed-code-file renames + 4 external consumer updates.
  (γ) Rename new C-CP-26 identifiers (spec-level rename of NEW surface)
      → CP spec v1.11 §26 + OD spec v1.9 + plan v2.17 + OD plan v2.15 + CXA v2.8.
        ZERO landed-code rename. RECOMMENDED for low blast radius + forward-clean canonical.
  (δ) Declare old §22 deprecated / superseded; rewire 4 external consumers
      → CP spec v1.11 §22 retirement + delete pause_resume_protocol.py legacy surface
        + 4 landed file rewires + retirement ledger update.
        Largest scope; resolves canonical authority question definitively.
```

**Filing recommendation note (advisory; operator decides):** Path γ is the cleanest mirror of U-CP-58's path β resolution at the inverse direction — there we renamed the OLD landed code to free the canonical name for the NEW spec surface; here we have the inverse opportunity to rename the NEW spec surface to preserve the OLD landed code unchanged. Path γ touches only delta-version design-substrate files + carrier authoring (the U-CP-62 file does not exist yet) — zero landed-code blast radius. Path β would re-rename surfaces that already underwent retirement-criterion declarations at the U-CP-49 landing.

---

## §5 — Cross-references

- `[[class_1_fork_u_cp_58_validator_fail_class_collision]]` — sibling pattern (path β resolution at U-CP-58)
- `[[carrier-surface-inspection-catches-namespace-collision]]` — owed memory entry from last session; this fork validates the lesson per-unit
- `[[spec-prose-plan-body-drift-pattern]]` — related: spec §22 + §26 prose vs plan-body instruction divergence
- Workspace CLAUDE.md §4.3 — silent-absorption discipline
- `phase-7-back-flow-routing` SKILL.md §2.4 — Class 1 disambiguation (uncertain → default Class 1)
