---
artifact: design-substrate/Spec_Information_Substrate_v1.md
version: v1.10
cleared_at: 2026-07-12T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/r-fs-2-final-closure-implementation-plan-v1.md (§3 B-18-LANEB-PROMPT-SEMVER, Wave 2)
  - .harness/u1-slice3b-epoch-partition-design.md (§5 "Lane-B semantic-major" + §6 forward-arc registration)
  - .harness/u1-3c-prewarm-design-decision-record.md (§8 deferred/registered follow-ons table)
merge_commit: <pending — pinned at PR merge>
reviewer_chain:
  - impl-time grounding pass — verified every production consumer of PromptVersion reads .version_sha or .content only (never the full model), confirming cache-inertness by construction before authoring the spec text
supersedes: Spec_Information_Substrate-v1_9-cleared-2026-06-17.md
---

# Clearance — `Spec Information Substrate v1.10`

v1.10 adds NEW §5.5: `PromptVersion.version: str | None = None` — an operator-declared semantic-version label on the already-frozen `PromptVersion` carrier, mirroring the Skills `frontmatter.version` concept ADR-D3 §1.8.1 committed, but optional (unlike Skills, where `version` is a required, load-seam-enforced constraint per B-SKILL-FRONTMATTER-VALIDATOR). The field is explicitly cache-inert: it is not read by the §5.2 procedural-tier recipe (which reads only `active_prompt_version.version_sha`), not read by the CP `cohort_key` / cacheable-epoch `prefix_content_hash` derivations (both already scalar-typed on `version_sha`), and not a dimension of the §5.3 store's content-addressed-uniqueness invariant (keyed on `version_sha` only — two store entries may share the same `version` label). `version_sha` remains the sole cache-correctness + content-identity key, per `u1-slice3b-epoch-partition-design.md`'s empirical finding that Anthropic's prompt cache is byte-exact.

**Zero change to** the §5 six-field shape / §5.1 sidecar / §5.2 recipe / §5.3 store invariants (a)/(b)/(c) / §5.4 `branch_metadata` / §6 hash-chain / §7 read-write / §10 seam exports. A pure additive optional field, defaulted `None` — byte-compatible with every pre-existing `PromptVersion` construction call site. No ADR revision — ADR-D3 §1.8.1 already commits the analogous Skills concept; this amendment ports the pattern to prompts at IS-spec level only.

**No operator gate.** The one-time strike window at the R-FS-2 Unit-0 PR review (#934) passed unexercised, so this builds under FULL-SPEC discipline. Additive, reversible, no committed invariant sacrificed — no nameable cross-domain tension (`[[feedback-gate-only-on-meaningful-architecture-change]]`).

**Phase 7 consumers.** Companion code lands in the same PR: `PromptVersion.version` field in `harness_is/prompt_manifest.py`; a byte-unchanged control witness at `resolve_procedural_tier_snapshot` (proves cache-inertness by execution, not just by spec assertion); round-trip tests for construction with/without the field.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
