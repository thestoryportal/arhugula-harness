---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.39
cleared_at: 2026-05-29T16:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_yaml_loader_step_payload_scalar_coercion_gap.md
  - PR #79 (filing)
  - PR #82 (apply arc — TBD at PR creation)
  - PR #81 (sibling apply for PR #80; spec v1.37 → v1.38)
merge_commit: TBD-at-PR-merge
reviewer_chain:
  - use-the-product probe (post-PR-#78 session, 2026-05-29) — finding #16/#17
  - advisor 56th + 57th applications (pre-substantive scope-discipline + apply-order + empirical-shim-verify-before-spec-text)
  - operator AskUserQuestion ratification 2026-05-29 Q-set (Q1=A + Q2=α + Q3→routes-to-#80 + Q4=b)
  - empirical pyyaml StrictSafeLoader shim feasibility check (78 LOC; 10/10 strictness tests pass at scratch BEFORE spec authoring)
  - spec-writer apply pass (this arc — Reading A absorption into spec body + plan body)
  - impl-time grounding pass (1305/1305 harness-runtime + 794/794 harness-cp tests pass post-amendment)
---

# Clearance — `Spec_Harness_Runtime_v1.md v1.39`

v1.39 absorbs the Class 1 fork resolution Reading (A) re-litigating Q-H=b (Phase 2a G2 strictyaml ratification 2026-05-28) and replacing `strictyaml.dirty_load` with `pyyaml.safe_load` via a thin `StrictSafeLoader` subclass (78 lines at `harness-runtime/.../lifecycle/strict_safe_loader.py`). Strictness motivation preserved exhaustively (duplicate-key detection + non-empty flow-style ban + anchor/alias ban); YAML 1.1 native scalar typing gained. Spec §14.19 canonical-reading amendment; spec body PRESERVED VERBATIM.

What was reviewed: use-the-product probe finding #16/#17 catalogued the structural inconsistency empirically (YAML manifest fails LLM dispatch; TOML transcription of same shape succeeds); advisor 56th + 57th applications caught the apply-order + empirical-verify-before-spec-text disciplines; operator ratified Reading A en-bloc Q1-Q4 + Q-H=b re-litigation; empirical shim verification at $CLAUDE_JOB_DIR pre-positioned the spec amendment; impl-time grounding pass verified ZERO regression at runtime + cp test suites (2099 tests pass total).

Caveats for Phase 7 consumers: `_coerce_int_fields` helper at U-RT-104 RETIRED (native typing makes it redundant). `_check_version` simplified to reject non-int `version` directly. YAML 1.1 boolean ambiguity at `yes` / `no` / `on` / `off` preserved at YAML level — operators wanting string-typed values whose content parses as bool must quote (YAML 1.2's native rule; documented at fork doc §4(b)). Sibling clearance at `.harness/clearance/Spec_Harness_Runtime-v1_38-cleared-2026-05-29.md` (PR #80 apply; topology admissibility deferral to runtime) is the prerequisite for the typed-fixture-pair equivalence test at v1.39.

## Notes

- Phase 7 consumers may rely on v1.39 as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
- Sibling clearance: `Spec_Harness_Runtime-v1_38-cleared-2026-05-29.md` (PR #81; PR #80 apply).
- Q-H=b at Phase 2a G2 (2026-05-28) is RE-LITIGATED AND SUPERSEDED at v1.39 per fork §4(d).
