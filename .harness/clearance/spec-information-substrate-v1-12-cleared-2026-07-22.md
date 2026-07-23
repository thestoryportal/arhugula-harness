---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.12
cleared_at: 2026-07-22T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-1-fork-ratification (B-33-A spec leg; spec-writer apply pass per CLAUDE.md §4.3 + §4.5)
back_reference:
  - .harness/class_1_fork_b33_rotation_correlation_carrier.md (RATIFIED 2026-07-21 — option A AS RECOMMENDED)
merge_commit: pending (pre-merge at filing time; B-33-A spec-leg apply PR)
reviewer_chain:
  - operator ratification (2026-07-21) — option A as recommended
  - advisor() review of the carrier-shape reconciliation (open-dict framing vs the IS typed-sidecar idiom) prior to authoring
  - just codex-review round 1 (2026-07-22, PR #1082) — 2 P1 + 4 P2 findings, all fixed same round: strengthened the Option-A/B hash-coverage reconciliation to directly rebut the fork's "hash-covered by the chain itself" Option-B parenthetical; added §7.7 invariant (c) non-emptiness guard (presence/uniqueness both pass vacuously on an empty window) + matching plan AC + witness; added construction-time canonical-UUID rejection to §5.6 + plan AC + witness; corrected "Closes B-33" → "Closes the IS-side half of B-33" (B-33 itself stays open) at 2 sites; refreshed harness-is/CLAUDE.md + .harness/claude-artifact-pointers.md pointers; refreshed the B-33 prose block at .harness/post-phase-8-forward-register.md to match the YAML transition
---

# Clearance — Spec_Information_Substrate_v1 v1.12 (B-33-A spec leg)

v1.11→v1.12: NEW §5.6 D-derivative sidecar field `rotation_correlation_id: str | None` on `StateLedgerEntry`/`EntryPayload` (C-IS-05), following the established typed-sidecar idiom at §5.1 (`procedural_tier_snapshot_ref`) and §5.4 (`branch_metadata`) — omit-when-`None` canonicalization, ZERO breaking change to the existing chain. NEW §7.7 (C-IS-07) authors the two read-side invariants checkable against the IS chain alone: presence (every entry in a claimed rotation window carries the id) and uniqueness (a window carries at most one distinct id). This closes the IS-side half of `B-33` (registered at `.harness/post-phase-8-forward-register.md`; `verify_rotation_6_steps` at `harness_cp.five_axis_composition` proved chain continuity, not rotation, because the IS entries it walked carried no rotation-event identity).

The fork's own text described the ratified shape as "an open-dict additive IS carrier." Grounding against the actual `StateLedgerEntry`/`EntryPayload` schema showed IS has no open-dict/namespace-attrs mechanism; the change-note reconciles this explicitly — IS's own additive-carrier idiom is the typed D-derivative sidecar, which is (and must be) hash-covered exactly as OD §24.7 (the cited precedent) already is. The `verify_rotation_6_steps` 3-step extension, the composition-root-injected OD-join evidence DTO, and the B-36 `AwsKmsSigningBackend` key-identity boundary attestation are explicitly OUT of scope here (CP-owned; IS has zero outbound cross-axis edges) — cross-referenced at §7.7, decomposed at the separate CP-axis impl leg (mirrors the `B-59-A` spec-leg → impl-leg precedent, PRs #1080 → #1081). ZERO change to the §5 six-field shape / §5.1–§5.5 / §6 hash-chain construction / §7.1–§7.6 / §10 seam exports.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- The CP-axis impl leg (carrier code + `verify_rotation_6_steps` extension + OD-join) is a separate, not-yet-opened arc.
- See `.harness/clearance/README.md` for marker discipline.
