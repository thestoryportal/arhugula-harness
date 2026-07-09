# Class 1 Fork — Provider construction allowlist/optional semantic

**Status:** ✅ APPLIED-AS-(E-prod-3) 2026-05-28 — operator ratification via AskUserQuestion.
**Class:** 1 (architectural defect; spec internal tension)
**Filing arc:** post-PR-#4 daemon-startup binding-chain depth-3 halt.
**Resolution arc:** runtime spec v1.36 → v1.37 + runtime plan v2.32 → v2.33 + harness-runtime impl, same session.

---

## §1 Defect

Two design-substrate texts at `Spec_Harness_Runtime_v1.md` give contradictory readings of stage 3a CP_CLIENTS provider-construction semantics:

- **Line 1779** — `provider_secrets` field is "Keyring allowlist *keys* only; no secret values in config" — implies the allowlist gates which secrets resolve at stage 3a.
- **Line 1747** — stage 3a post-condition: "`ctx.providers: dict[str, ProviderClient]` has entries for `anthropic`, `openai`, `ollama`; each client passes an async ping" — implies unconditional construction of all three.

Production at `harness-runtime/src/harness_runtime/lifecycle/providers.py:677-686` reads NEITHER allowlist NOR optional flags for anthropic + openai; both constructed unconditionally; only `ollama_optional` accommodates degraded construction (lines 689-706).

Operators without an `anthropic_key` keyring entry surface `ProviderSecretMissingError: provider='anthropic': keyring entry 'anthropic_key' not found` at bootstrap stage 3a — blocking daemon-mode startup. AC #1 / AC #5 / AC #6 subprocess e2e tests all halt at this same site.

## §2 Empirical clarification

Grep at production source resolves the apparent "allowlist gates construction" reading: `operator_allowlist` is the **secret-key allowlist per C-AS-06 §6.2** (operator-policy override set for `check_secret_allowlist`), NOT a provider-construction gate. The line 1779 spec text accurately describes its purpose — but it's orthogonal to whether providers are constructed at stage 3a.

The genuine defect is line 1747 vs the absent anthropic_optional + openai_optional analogues to the existing `ollama_optional` field. Spec assumes always-3-providers; production already accommodates 2-provider degradation; spec should canonicalize the actual capability.

## §3 Readings considered

| Reading | Scope | Properties |
|---|---|---|
| **(E-test)** Mock keyring backend in subprocess tests | 1 conftest fixture + env var | Tactical; defers spec question; preserves silent eager-construct |
| **(E-prod-1)** Lazy provider binding | Larger scope; daemon-startup semantic change | Defers construction until first workflow invokes provider |
| **(E-prod-2)** Empty-allowlist tolerance | ~3 files; spec-conformant per line 1779 (mis-read) | Skip stage 3a when allowlist empty — but allowlist is secret-key policy, not provider-construct gate |
| **(E-prod-3)** ✅ Per-provider opt-in (mirror ollama_optional) | ~5 files + 2 new RuntimeConfig fields | Sibling parallel pattern; explicit degradation semantics per provider |
| **(Halt)** File fork, route to operator | 0 production change | Preserves X-AL-3; safest |

## §4 Operator ratification

**AskUserQuestion 2026-05-28 (session resumption from depth-3 halt checkpoint):**

> "Daemon-startup binding-chain — how should we close the verification-shape depth-3 halt? Spec audit found internal tension: line 1779 implies the allowlist gates provider resolution; line 1747 implies all three providers always constructed; production silently chose unconditional."

**Selected: (E-prod-3) Per-provider opt-in (mirror ollama_optional).**

Preview surfaced at ratification: "Scope: ~5 files + 2 new RuntimeConfig fields ... Unblocks: subprocess e2e via optional=True in fixture. Production effect: graceful degradation across all 3."

## §5 Applied resolution

### §5.1 Spec amendment (runtime spec v1.36 → v1.37)

**§3 C-RT-02 RuntimeConfig field table** — add two NEW optional `bool = False` fields:

- `anthropic_optional` — sibling to `ollama_optional`. When `True`, transient construction failure surfaces `ProviderDegradedWarning` + omits `"anthropic"` from `ctx.providers`. When `False` (default), preserves existing fail-fast posture.
- `openai_optional` — symmetric.

**§14.5 stage 3a post-condition (line 1747)** — REFRAMED:

- v1.36: "`ctx.providers: dict[str, ProviderClient]` has entries for `anthropic`, `openai`, `ollama`; each client passes an async ping"
- v1.37 canonical-reading amendment: "`ctx.providers: dict[str, ProviderClient]` contains a **non-empty subset of {`anthropic`, `openai`, `ollama`}**; each present client passes an async ping. The set may be reduced from the maximal {anthropic, openai, ollama} by per-provider `*_optional` degradation per §C-RT-02 + provider-construction lifecycle at C-RT-05."

**§14.5 stage 3a invariant** — `len(ctx.providers) >= 1` made explicit. Empty providers dict surfaces typed `RT-FAIL-PROVIDER-NONE-CONFIGURED` at stage 3a (NOT stage 5; fail-fast at construction site). The existing `LLMDispatchBindError` at stage 5 (`llm_dispatch.py:1025`) preserved as a defense-in-depth check.

**§14 failure-mode taxonomy** — NEW row:

- `RT-FAIL-PROVIDER-NONE-CONFIGURED` (permanent) | Stage 3a CP_CLIENTS — all providers degraded via `*_optional=True` + transient construction failure; no provider successfully constructed. Operator-fix: configure at least one provider keyring entry, OR mark fewer providers optional.

### §5.2 Plan amendment (runtime plan v2.32 → v2.33)

Single-unit-body amendment at U-RT-02 RuntimeConfig schema:

- Field-set N → N+2 (add `anthropic_optional` + `openai_optional`)
- AC text refresh — field-count assertion
- NEW tests covering each optional field default + non-default round-trip

ZERO new units; ZERO new cluster; ZERO DAG topology change; ZERO cross-axis cascade.

### §5.3 Production binding

**`harness-runtime/src/harness_runtime/lifecycle/providers.py`** — refactor steps 1 + 2 (anthropic + openai) at lines 677-686 to mirror the ollama step 3 try/except pattern at lines 688-706, with one architectural extension. Substantively: each becomes:

```python
try:
    providers["{name}"] = await _attempt_with_bounded_retry(...)
except (ProviderTransientError, ProviderSecretMissingError) as exc:
    if config.{name}_optional:
        warnings.warn(ProviderDegradedWarning("{name}", _cause_for(exc)), stacklevel=2)
    else:
        raise
```

**Architectural extension vs ollama precedent.** Ollama's `*_optional` swallows only `ProviderTransientError` because Ollama is keyring-less (local-tier, no API key). Anthropic + OpenAI both perform keyring lookups at construction, so `*_optional=True` must additionally swallow `ProviderSecretMissingError` to actually unblock the "no keyring entry configured" daemon-startup case (the original finding's blocker). `ProviderAuthError` (operator HAS a keyring entry but it's invalid → 401/403) remains a hard failure because it indicates operator intent + misconfig — exactly the case that should surface.

**Operator UX.** `*_optional=True` means "I'm OK running without this provider if it can't be set up (no keyring entry OR network unreachable). Surface auth errors loudly because those indicate I'm trying to set it up wrong."

NEW post-loop check: `if len(providers) == 0: raise ProviderNoneConfiguredError(...)`.

NEW exception class `ProviderNoneConfiguredError` (typed; carries fail-class `RT-FAIL-PROVIDER-NONE-CONFIGURED`).

**`harness-runtime/src/harness_runtime/types.py`** — add 2 fields to `RuntimeConfig` Pydantic model.

### §5.4 Test coverage

- `harness-runtime/tests/test_types.py` — RuntimeConfig field count + default assertions
- `harness-runtime/tests/lifecycle/test_providers.py` — anthropic_optional + openai_optional degraded paths + empty-providers fail-class

### §5.5 Subprocess e2e implication

Subprocess e2e at AC #1 / AC #5 / AC #6 unblocks by setting `anthropic_optional=true` + `openai_optional=true` (Ollama already optional) in the test-fixture `RuntimeConfig`. Test path: bootstrap stages 0..3a complete; at least one provider must succeed-construct (could be `ollama` via local install OR a mocked construct via the existing `*_construct` test-injection points at `materialize_provider_clients_stage`).

**Recommended test-fixture pattern (Reading B):** mock one provider via existing `*_construct` injection point; all three optional=True. Belt-and-suspenders against keyring requirement in CI.

## §6 Invariants preserved

| Invariant | Statement | Status |
|---|---|---|
| **X-AL-3** | No silent H_T design extension at Phase 7 | PRESERVED — fork-doc + spec amendment ceremony executed before production change |
| **ADR-F1 v1.2** | Multi-LLM commitment (3 providers under capability-aware abstraction) | PRESERVED — degradation is operator-opt-in per provider; default behavior unchanged at `*_optional=False` |
| **C-RT-05** | Provider client lifecycle | PRESERVED — degraded path uses existing `ProviderDegradedWarning` machinery |
| **Stage 5 LLM-dispatch binding** | Requires non-empty providers dict | PRESERVED + reinforced at stage 3a via new `RT-FAIL-PROVIDER-NONE-CONFIGURED` |

## §7 Cross-axis cascade verification

| Axis | Cite cascade owed | Reason |
|---|---|---|
| CP | NO | Provider construction is intra-runtime-axis; CP routing consumes `ctx.providers` post-binding; no CP contract references the field set |
| AS | NO | AS spec C-AS-06 §6.2 allowlist semantics unchanged; orthogonal axis |
| OD | NO | OD spec OTel attribute schemas unchanged; cost-attribution unchanged |
| IS | NO | IS spec state-ledger unchanged |
| CXA | NO | No cross-axis edge addition |
| ADR-F1 | NO | Multi-LLM commitment preserved; degradation is operator-opt-in not architectural retreat |

ZERO cross-axis cascade verified via grep at `design-substrate/` 2026-05-28.

## §8 Audit lineage

- Filed + applied 2026-05-28 single-session per workspace convention (mirror `class_1_fork_h_t_cp_19_default_gate_level_spec_extension.md` 3-arc single-day precedent).
- 28th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture (advisor consulted pre-authoring; 3 concerns surfaced; concerns #1 and #3 incorporated; concern #2 dissolved at empirical clarification — operator_allowlist is secret-key policy, orthogonal to provider construction).
- Closes `[[finding-bootstrap-stage-cp-clients-3-keyring-prebind]]` OPEN → CLOSED-via-(E-prod-3)-2026-05-28.

## §9 Related memory

- `[[finding-bootstrap-stage-cp-clients-3-keyring-prebind]]` — layer 3 finding (CLOSED)
- `[[finding-bootstrap-stage-is-1-requires-skills-path-binding]]` — layer 2 (D-test) fixture pattern (still OPEN; orthogonal arc)
- `[[finding-runtime-config-loader-unreachable-sub-configs]]` — layer 1 (CLOSED by PR #4)
- `[[verification-shape-sharpened-grep-vs-e2e]]` — depth-budget discipline
- `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — 28th application

## §10 Amendment — prefer-OAuth default flips `*_optional` to `True` (2026-07-09)

**Trigger.** The external-CLI (OAuth/subscription) multi-LLM routing capability was
ported into `main` (branch `feat/external-cli-oauth-routing-port`; see
`.harness/external-cli-routing-port-review-findings.md`). The operator ratified the
**prefer-OAuth default routing posture** via AskUserQuestion (2026-07-09): a fresh
checkout routes through local subscription CLIs first (`enabled_provider_names`
defaults to `DEFAULT_ENABLED_PROVIDER_NAMES` = CLI providers + SDK fallbacks;
`external_cli_providers` defaults to the claude_code/codex/antigravity set).

**Decision.** The §5.1 default for `anthropic_optional` / `openai_optional` /
`ollama_optional` flips **`False` → `True`** (soft-degrade) as the coherent companion
to the prefer-OAuth posture: when CLIs are the preferred path, a missing/unreachable
hosted-provider credential must degrade (drop that provider) rather than hard-fail
stage 3a — otherwise a fresh checkout without API keys could not route at all despite
authenticated CLIs being available. This does **not** change the auth-error carve-out
(`ProviderAuthError` 401/403 ALWAYS surfaces) and does **not** weaken ADR-F1: multi-LLM
routing is preserved; degradation is the ratified default, and an operator who wants
fail-fast sets `*_optional = false` explicitly (or picks the
`SDK_ONLY_ENABLED_PROVIDER_NAMES` opt-out).

**Class.** Class 2 (operator decision reversing a prior ratified default). Not a Class 1
architectural fork — the field semantics, the auth-error carve-out, and the multi-LLM
commitment are all unchanged; only the DEFAULT value of an already-existing operator
knob is flipped, under explicit operator ratification. E-prod-3 (2026-05-28, which
ratified `False`) stands as the field's origin; this amendment supersedes only its
default value, forward.

**Carrier.** `harness-runtime/src/harness_runtime/types.py` field defaults + docstrings;
`harness.toml.example`; `test_config_loader.py::test_enabled_provider_names_defaults_to_prefer_oauth`.
