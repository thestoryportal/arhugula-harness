---
artifact: .harness/class_1_fork_provider_construction_allowlist_semantic.md
version: §10-amendment (prefer-OAuth default; supersedes E-prod-3's False default forward)
cleared_at: 2026-07-09T22:40:00+00:00
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - .harness/class_1_fork_provider_construction_allowlist_semantic.md §10
  - .harness/external-cli-routing-port-review-findings.md
  - PR #914
merge_commit: (pending — feat/external-cli-oauth-routing-port)
reviewer_chain:
  - operator AskUserQuestion ratification 2026-07-09 (deployed-parity / prefer-OAuth default posture)
  - out-of-family Fable 5 review (substituted for the inactive Codex subscription) — verdict MERGE
  - harness-adversarial-reviewer Phase-7 pre-merge review — verdict MERGE
---

# Clearance — provider-construction-allowlist fork §10 amendment (prefer-OAuth default)

Records the operational acceptance, for Phase-7 consumption, of the §10 amendment to
`.harness/class_1_fork_provider_construction_allowlist_semantic.md`. The amendment flips
the DEFAULT of `RuntimeConfig.anthropic_optional` / `openai_optional` / `ollama_optional`
from `False` (E-prod-3, 2026-05-28) to `True` (soft-degrade), as the coherent companion
to the operator-ratified prefer-OAuth default routing posture that landed with the
external-CLI (OAuth) routing port. The field semantics, the `ProviderAuthError`
always-surface carve-out for the hosted SDK providers, and the ADR-F1 multi-LLM
commitment are all unchanged; only the DEFAULT value of an existing operator knob is
flipped, under explicit operator ratification.

This clearance marker also records this PR as a **legitimate bundled-absorption arc**
(CLAUDE.md §11.4): the fork §10 design-phase amendment co-lands with its Phase-7
implementation (`harness-runtime/.../types.py` field defaults + docstrings, `harness.toml.example`,
and the `test_config_loader.py` default assertion) in one reviewed PR. E-prod-3 stands as
the field's origin; this amendment supersedes only its default value, forward. An operator
who wants fail-fast sets `*_optional = false` explicitly (or selects the
`SDK_ONLY_ENABLED_PROVIDER_NAMES` opt-out).

## Notes

- Phase 7 consumers may rely on this prefer-OAuth default until a successor decision is filed.
- See `.harness/clearance/README.md` for marker discipline.
- The broader governance reconciliation for this arc (ADR-D7 stale-claim correction, routing
  `C-*` cite, memory-substrate clearance markers, CLAUDE.md §2 pointer refresh) is tracked as
  `R-300-external-cli-routing-governance` and lands in a separate design-phase PR.
