# Phase 7 — Class 1 Fork Record 001 — State-Ledger Entry Shape

*Back-flow routing record. Authored at fork detection per `phase-7-back-flow-routing`
SKILL §4.3 (capture halted state). Operator authorized routing option (A) on
2026-05-15. Phase 7 sub-phase 7a HALTED until resumption conditions met (§5).*

---

## §1 Halt state

| Field | Value |
|---|---|
| Fork class | **Class 1** (halt-execution; design-phase artifact requires revision) |
| Detected at | Phase 7 Session 1, sub-phase 7a, substitution-scaffolding surface 2 (state ledger) |
| Halt point | Surface 2 proposal stage — not instantiated |
| Detected | 2026-05-15 |
| Operator routing decision | (A) — authorize design-phase back-flow |
| Status | **RESOLVED** — drift corrected in-workspace 2026-05-15 per operator authorization; see §7 |

## §2 Defect

The state-ledger entry shape is specified two incompatible ways.

**Canonical authority chain — internally consistent at 6-field:**
- `Architectural_Design_Document_v1_3.md §2.2` Synthesis
- `Spec_Information_Substrate_v1.md §5` (contract C-IS-05) — "The state-ledger
  entry record is a **six-field tuple**"

  Shape: `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)`

**Governance + workspace bootstrap substrate — drifted to 8-field:**
- `Phase_7_Meta_Architecture_v1.md §5.2` (H_T-IS-5 row) — "canonical 8-field entries"
- `Phase_7_Meta_Architecture_v1.md §10.1.6` — smoke-test gate verifies
  "idempotency_key + prev_hash + current_hash present"
- root `CLAUDE.md §1.1` — "State ledger (8-field hash-chained entries)"
- `harness-is/CLAUDE.md §1.3` — "State-ledger entry shape (8-field …) … C-IS-05 §5"
- `harness-is/CLAUDE.md §4.2 IS-AL-3` — enumerates 8 fields
  `(thread_id, step_id, idempotency_key, event_type, payload, prev_hash, current_hash, timestamp)`

Count AND field names diverge. `harness-is/CLAUDE.md §1.3` cites `C-IS-05 §5` as
the contract authority while labelling it "8-field"; C-IS-05 §5 says "six-field."

## §3 Why Class 1

`Meta-Architecture §10.1.6` is the canonical-workload smoke test = **7a
exit-criterion #2**. Its verification gate names `prev_hash` and `current_hash` —
fields that **do not exist** in the canonical 6-field shape (which uses
`response_hash` / `prior_event_hash`). The 7a exit gate is **unrunnable as
written** against the canonical contract. Not citation imprecision.

## §4 Routing target

The canonical chain (ADR-F2 → ADD §2.2 → C-IS-05) is consistent at 6-field; the
drift is in **governance** and **workspace bootstrap substrate**. Closest
`phase-7-back-flow-routing` §3.1 row: "Workflow governance defect."

Revisions required at the design-phase workspace:

| # | Artifact | Site | Required correction |
|---|---|---|---|
| 1 | `Phase_7_Meta_Architecture_v1.md` | §5.2 H_T-IS-5 row (summary + detail line ~344) | "8-field" → field shape per C-IS-05 §5 |
| 2 | `Phase_7_Meta_Architecture_v1.md` | §10.1.6 smoke test (EXPECTED step 8 + VERIFICATION GATES) | field names → canonical (`idempotency_key`, `response_hash`, `prior_event_hash`) |
| 3 | `CLAUDE.md` (root) | §1.1 | "8-field" → per C-IS-05 §5 |
| 4 | `harness-is/CLAUDE.md` | §1.3 | "8-field" label → per C-IS-05 §5 |
| 5 | `harness-is/CLAUDE.md` | §4.2 IS-AL-3 | 8-field enumeration → canonical 6-field tuple |

**Reviewer note (non-binding hypothesis):** the OD audit ledger (`C-OD-14 §14.5.1`;
`harness-od/CLAUDE.md §1.3` "8-field SHA-256 composition") *inherits* the
state-ledger shape and adds `audit.*` per C-IS-05. The design-phase reviewer
should check whether the "8-field" figure originated as the audit-ledger shape
(state base + audit additions) and drifted into state-ledger citations — and
confirm the audit-ledger field count is correct relative to the resolved
state-ledger base.

**Authority direction:** ADR/ADD/spec are canonical over governance and workspace
substrate. If the design-phase council determines the 8-field shape is in fact
intended, the correction routes *up* the chain (ADD §2.2 + C-IS-05 revision via
Phase 3d/Phase 5) — a larger back-flow. The default expectation, absent that
finding, is that governance + CLAUDE.md drifted and 6-field stands.

## §5 Resumption conditions

Phase 7 sub-phase 7a resumes when ALL hold:

1. Design-phase session revises the §4 artifacts (or, if 8-field is intended,
   the ADD + C-IS-05 chain) and re-clears at the applicable checkpoint.
2. Re-issued artifacts pushed to / placed in this workspace.
3. Byte-exact integrity verified (`phase-7-back-flow-routing` SKILL §4.6).
4. Resume at surface 2 (state ledger) proposal; verify the entry shape is now
   consistent across canonical chain + governance + workspace substrate.

## §6 Progress preserved at halt

Not invalidated by this fork (independent of the state-ledger shape):
- §4.4 build infrastructure (root + 6 per-axis `pyproject.toml`, 12 skeletons,
  `.gitignore`, `.gitattributes`, `.python-version`, `README.md`, `.mcp.json`)
- `uv` workspace operational; git repo; commits `332a380`, `89aa81f`
- Entry-gate 7/7 cleared; Phase 7 Session 1 open
- Substitution-scaffolding **surface 1 (path conventions)** instantiated
  (`Phase_7a_Substitution_Scaffolding.md §1`)

Halt affects surface 2 (state ledger) onward. Surfaces 3–9 that do not depend on
the state-ledger entry shape are not individually blocked, but 7a closure is
blocked because 7a exit-criterion #2 (the §10.1.6 smoke test) cannot run until
the gate text is corrected.

## §7 Resolution

Operator authorized in-session resolution 2026-05-15 (direction: align to
canonical 6-field; accepting that `design-substrate/` edits diverge from the
design-phase Claude.ai canonical source until reconciled). Resolution applied
as **drift-correction** — the canonical authority chain (ADR-F2 → ADD §2.2 →
C-IS-05 §5) was already consistent at the 6-field shape; the governance +
workspace bootstrap artifacts had drifted to a non-canonical 8-field shape.

**10 lines corrected across 4 files** to the canonical 6-field shape
`(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)`
per C-IS-05 §5, with a deferral note at the IS-AL-3 enumeration sites recording
that the relationship to the C-IS-07 §7.1 keying tuple `(thread_id, step_id,
idempotency_key)` is deferred per C-IS-07 §7.4 (NOT closed — the downstream
D-ADR on ledger schema remains the resolution path; the correction does not
pre-empt it):

| File | Sites |
|---|---|
| `CLAUDE.md` (root) | §1.1 |
| `harness-is/CLAUDE.md` | §1.3, §4.2 IS-AL-3 |
| `design-substrate/Phase_7_Meta_Architecture_v1.md` | §5.2 (×2), §4.4, §7 IS-AL-3, §10.1.6 |
| `Phase_7_Session_1_Entry_Directive_v1.md` | §5.5 smoke gate, §8.5 IS-AL-3 row |

**NOT changed (different contract):** the OD audit-ledger "8-field" at
`harness-od/CLAUDE.md §1.3` and `Phase_7_Kickoff_Prompt.md` — `C-OD-14 §14.5.1`,
which inherits the state-ledger shape + `audit.*` additions. Whether its
field count is correct relative to the resolved 6-field state-ledger base is a
separate determination for the design-phase reviewer.

**Reconciliation owed:** `design-substrate/` is a local copy. The corrected
`Phase_7_Meta_Architecture_v1.md` must be pushed back to the design-phase
Claude.ai project (or this workspace's copy formally designated canonical) so
the canonical source and the workspace copy do not diverge.

## §8 Adjacent observations (separate determinations — NOT acted on)

| # | Observation | Disposition |
|---|---|---|
| 8.1 | `harness-is/CLAUDE.md §5.2` records CF-1/F2-12 as CLOSED (D1 replay-trace contract), but `Spec_Information_Substrate_v1.md §42` calls the ledger-schema D-ADR "F2-12 active engagement … open downstream resolution path." "F2-12" may be overloaded across two distinct items, or there is a further inconsistency. | Design-phase reviewer; out of scope for Fork 001 |
| 8.2 | `Phase_7_Meta_Architecture_v1.md §7.2` IS-AL-3 — wait, IS-AL-1 — names the 4 H_T path classes "(artifact / cache / state / secret)"; `C-IS-01 §1` (canonical contract) and `harness-is/CLAUDE.md §4.2 IS-AL-1` name them "(Skills / Prompts / Routing manifest / State-ledger)". Different taxonomy. | Raised as **Class 1 Fork 002 candidate** — surfaced to operator separately |
