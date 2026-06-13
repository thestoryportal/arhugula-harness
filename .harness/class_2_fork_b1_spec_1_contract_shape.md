# Class 2 Fork — B1-spec-1 C-CP-25 extension contract shape

**Filed + RESOLVED:** 2026-06-13 · R-FS-1 arc #3 (B1-spec-1), design-phase posture. Resolved at filing (reversible in-repo spec-shape decision; `[[grounding-reveals-claude-closeable-slice-close-honestly]]` — decide-with-rationale, no operator gate).

**Status:** ✅ RESOLVED → Reading (i). Applied at `Spec_Control_Plane_v1_32.md` §25.10–§25.18.

## §1 The fork

The §25.1 deferral table (`Spec_Control_Plane_v1_6.md` §25.1) names the extension contract for the 5 deferred topology patterns as **"C-CP-25.b or C-CP-26"**. That forward-guess is stale: it pre-dates v1.10, which **occupied C-CP-26 with `PauseResumeProtocol`**. So the contract-shape choice for materializing the 5 patterns is:

| Reading | Shape | Assessment |
|---|---|---|
| **(i) in-place §25.10+ extension of C-CP-25** | Additive subsections on the existing WorkflowDriver contract. | **CHOSEN.** §25.1 deferred C-CP-25's **own** `execute_workflow` behavior for non-linear topologies; lifting it is an extension of the same contract surface (one source of truth). Mirrors the v1.5 §25.9 precedent exactly (cost-attribution was added as an additive C-CP-25 subsection, not a new contract). |
| (ii) new top-level contract C-CP-30 | A separate contract ID (next free; C-CP-29 is the head). | Rejected: implies a separate contract surface, but the driver-strategy dispatch IS `execute_workflow`'s behavior for non-linear topologies — splitting it fragments the WorkflowDriver's single source of truth. |
| (iii) C-CP-25.b sub-ID | The deferral table's literal guess. | Rejected: `.b` sub-IDs are **not an established convention** in this spec (grep: the only `C-CP-25.b` occurrences are the v1.4/v1.5/v1.6 deferral-table guess itself). And the table's paired "C-CP-26" is occupied. Minting a one-off sub-ID convention into a contract ID space that already suffered the v1.13 collision is the wrong move. |

## §2 ID-space grounding (code-grounded, not change-note tables)

Confirmed from contract **bodies** + code (the change-note tables carry a known §25/§28 mislabel — see `.harness/class_1_fork_cp_spec_section_25_contract_id_collision.md` + v1.32 §-adjacent (a)): §25/C-CP-25 = WorkflowDriver; C-CP-26 = PauseResumeProtocol; C-CP-27 = PerServerTrustEvaluator; §28/C-CP-28 = ValidatorFramework; C-CP-29 = PromptSelectionManifest. Highest top-level ID = C-CP-29; next free = C-CP-30 (unused by Reading (i)).

## §3 Resolution

**Reading (i): in-place §25.10–§25.18 additive extension of C-CP-25.** No new contract ID, no `.b` sub-ID. Decorrelated: advisor (steered toward the in-place subsection shape; "you're lifting the WorkflowDriver's own deferred behavior") + the §25.9 precedent. The §25.1 deferral text is preserved verbatim (honored-then-lifted, not contradicted).
