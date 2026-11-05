# Spec: Harness Runtime — v1.139 (delta over v1.138)

*Delta-only file. One contract amended: C-RT-27 (§14.17, text current at the base file v1.32) gains
skill-content delivery. It amends §4 C-RT-04 `skills` load (via §14.17.5 invariant 7 and §14.17.7),
§14.17.2 hook 2, §14.17.4 failure-mode taxonomy, §14.17.5 invariants 3, 6 and 7 and the §14.6 C-RT-16
per-candidate attempt loop (one propagation arm), and adds NEW §14.17.8. Hooks 1 and 3 are unchanged. Every other v1.138 and earlier term remains in force.
Proposed v1.135/v1.136 deltas are not amended. Cleared predecessor files are not edited.*

**Status: CLEARED 2026-11-05 — ratified by the integration lead at LIT `cmt-e4d23545-c62a-42a3-89cb-89a186846f10`
on the frozen reviewed body `68eb98a343f7d4c7d0b8ff74a45365b4287dfd76` (independent contract GREEN
`cmt-d0bb3182-ae11-4af2-947d-c2242214cc59`); clearance `.harness/clearance/Spec_Harness_Runtime-v1_139-cleared-2026-11-05.md`.
Contract clearance only; source conformance (W1–W8, W4b), CI, landing and installed acceptance remain owed.**

**Filed:** 2026-11-05

**Authority:** LIT `arhugula-harness-trial-193.bt0` (solo-local package 05, "Complete usable skills");
claim `cmt-523be120-2313-4f50-b95c-fba87a6372a3`; grounding `cmt-04dbb7aa-7d62-4343-ab2c-e1db071d49cd`.

**Predecessor:** `Spec_Harness_Runtime_v1_138.md` (proposed, unlanded; Spec 4h4). This delta touches no
v1.138 site. If v1.138 does not land first, the predecessor becomes `Spec_Harness_Runtime_v1_137.md`
with no textual change below.

## §0 Change-note (v1.138 → v1.139)

| Site | Change |
|---|---|
| §14.17.5 inv 7, §14.17.7 `version_sha`/`body_tokens` | A loaded skill carries its SKILL.md content bytes. `version_sha` is the git blob SHA of those bytes; `body_tokens` is estimated from them. A manifest-supplied `version_sha` must equal the computed value. |
| §4 C-RT-04 load (`load_skills_from_dir`) | Unavailable or invalid content is a typed load failure that aborts bootstrap stage 2. |
| §14.17.2 hook 2 | The selected skills' content is rendered into the dispatch's effective system prompt. An unknown or duplicate selected id fails the step instead of being skipped. |
| §14.17.4 | Two new fail classes: `RT-FAIL-SKILL-CONTENT-INVALID`, `RT-FAIL-SKILL-SELECTION-INVALID`. |
| §14.6 C-RT-16 attempt loop | `SkillSelectionInvalidError` propagates through a by-name arm: no retry, candidate advance or breaker charge. The run's step `fail_class` names `RT-FAIL-SKILL-SELECTION-INVALID`. |
| §14.17.5 inv 3, 6 | Inv 3 keeps the opt-out path but removes the skills-unbound skip. Inv 6 makes the hook-2 membership check a step failure. |
| NEW §14.17.8 | Skill-content delivery contract and witnesses. |

## §14.17.8 Skill-content delivery (NEW at v1.139)

### §14.17.8.1 Content source and load

1. **One content file per manifest.** For a manifest at `<dir>/<stem>.skill.json`, the content file is
   `<dir>/<stem>.SKILL.md`. No other location is searched. The content is the file's complete bytes,
   decoded as UTF-8. No frontmatter is stripped; the manifest remains the only frontmatter source.
2. **Content is loaded once, at bootstrap stage 2.** `load_skills_from_dir` reads each content file in
   the same pass that reads its manifest. A loaded `Skill` carries `content: str` beside `manifest` and
   `source_path`. No read happens at dispatch time. A file changed after bootstrap therefore cannot
   alter delivered content or diverge from `version_sha`.
3. **`version_sha` is the digest of the delivered bytes.** `version_sha =
   compute_git_blob_sha(<content file bytes>)`, byte-identical to `git hash-object <content file>`.
   The manifest file's bytes no longer feed `version_sha`. If the manifest JSON supplies `version_sha`,
   it must equal the computed value; otherwise the load fails (§14.17.8.3, reason
   `version-sha-mismatch`). A supplied value acts only as a pin and never replaces the computed one.
4. **`body_tokens` is estimated from the content.** `body_tokens = len(content) // 4`. A manifest-
   supplied `body_tokens` is ignored and overwritten. The description-length proxy is removed.
5. **Content must be usable.** A load fails when the content file is absent, unreadable, not valid
   UTF-8, or empty after whitespace stripping.
6. **Skills without content are not a mode.** No manifest-only skill kind exists after v1.139.
   Existing manifest-only fixtures need a content file. The repository ships no `*.skill.json`
   outside tests at origin/main `f4973678`.

### §14.17.8.2 Delivery at hook 2

1. **Pre-condition (amends §14.17.2 hook 2 step 1).** Hook 2 runs when
   `skill_activation_emitter is not None` and its `hook is not None`. That is the existing operator
   opt-in, and the opt-out path is unchanged: zero spans and zero delivered content. A dispatcher
   bound with a hook must also be bound with a `skills` mapping, which may be empty. Construction
   with a hook and without a mapping raises `LLMDispatchBindError`. The `self.skills is not None`
   skip is removed.
2. **Selection is parsed before any effect.** The ids returned by
   `select_for_llm_dispatch(...)` are checked in returned order. The first id not in `skills`
   fails the step with `RT-FAIL-SKILL-SELECTION-INVALID` (reason `unknown-id`). An id returned twice
   fails with reason `duplicate-id`. On failure no `skill.activation` span is emitted and no
   provider call is made.
3. **Spans then content.** For a valid selection, one `skill.activation` span is emitted per id in
   order (mode `TOOL_SEARCH`, unchanged). The span's `version_sha` is the delivered content's
   digest by §14.17.8.1 item 3.
4. **Rendering.** Each selected skill renders as one block:

   ```text
   <skill id="{skill_id}" version="{manifest.version}" version_sha="{version_sha}">
   {content}
   </skill>
   ```

   Blocks join in selection order with one blank line (`"\n\n"`). An empty selection renders
   nothing, and the dispatch is byte-identical to pre-v1.139.
5. **Composition order.** The rendered skills append to the step's resolved base system prompt
   (per-step > per-role > run-level default, §14.5.3), separated by `"\n\n"`. They become the prompt
   when the base is `None` or empty. The memory packet composes after the skills
   (`compose_system_prompt_with_memory_packet` unchanged). Order: base, skills, memory.
6. **One system source.** Rendered skills travel only in the harness-owned effective system prompt.
   If that prompt is non-empty and the payload carries its own system source, the existing
   `RT-FAIL-PROMPT-INJECTION-CONFLICT` rule applies unchanged. No new merge path into
   `params["system"]` or a payload system message is added.
7. **No tool or discovery change.** Selecting a skill registers no tool, MCP server or path.
   Tool contracts remain what bootstrap stage 2 `materialize_tool_registry` produced.
8. **Hooks 1 and 3 unchanged.** A hook-1 or hook-3 activation emits its span and delivers no
   content. Content reaches a dispatch only through that dispatch's hook-2 selection.

### §14.17.8.3 Failure-mode taxonomy (amends §14.17.4)

| Fail class | Trigger | Permanent? |
|---|---|---|
| `RT-FAIL-SKILL-CONTENT-INVALID` | `load_skills_from_dir` rejects a skill. The reason is one of `content-missing`, `content-unreadable`, `content-not-utf8`, `content-empty` or `version-sha-mismatch`. The typed error `SkillContentInvalidError(skill_id, content_path, reason)` carries the reason. | YES. Bootstrap stage 2 aborts, fail-closed per ADR-F4 v1.1. |
| `RT-FAIL-SKILL-SELECTION-INVALID` | Hook 2 receives an unknown or duplicate id (reasons `unknown-id`, `duplicate-id`). The typed error `SkillSelectionInvalidError(skill_id, reason)` is raised at the dispatch site and carries the class attribute `rt_fail_class = "RT-FAIL-SKILL-SELECTION-INVALID"`. | YES for the step and run. See the propagation rule below. |

Reasons are closed enums. Messages name the skill id and, for content failures, the content path.

**Propagation through C-RT-16 (amends the §14.6 per-candidate attempt loop).** Hook 2 runs inside
`self.inner.dispatch` of every C-RT-16 attempt (`retry_breaker_fallback.py`). The selection reads
only the loaded skill ids, the workflow id and the step index, never the candidate, so every attempt
on every candidate would fail identically. `SkillSelectionInvalidError` therefore propagates untouched
through a dedicated by-name `except` arm. The arm precedes the generic `except Exception` arm,
beside the existing audit-signing and post-tool-effect arms. It sets `retry.delay_ms = 0` and
`retry.terminal = "skill-selection-invalid"` on the attempt span, then re-raises. As a result:

- No same-candidate retry and no candidate advance occur. No `fallback.exhausted` event is emitted
  and no `RetryBreakerFallbackExhaustedError` is raised.
- The breaker is not charged: `breaker.record_failure` is never called, because a selection fault
  says nothing about `{provider, model}` health (the §14.6.3 test). A half-open trial is inconclusive:
  the existing outer `BaseException` arm (`_release_half_open_trial`, §14.6.4 cells 6-8 class)
  returns it to `open` with a fresh cooldown and an unchanged `fail_count`
  (`re_arm_half_open_trial`).
- The type is not added to `_classify_provider_exception`'s fail-fast set or to
  `_BREAKER_CHARGE_WAIVED_TYPES`. Those govern the candidate-advancing arm, which this error never
  reaches.

**Step fail class.** The CP driver's step-dispatch boundary already surfaces an `rt_fail_class`
marker through `_step_fail_class`. The run ends with `status = FAILED` and `fail_class =
"step-failure: RT-FAIL-SKILL-SELECTION-INVALID: <message>"`. The marker lacks the
`RT-FAIL-HITL-GATE-` prefix, so the driver's HITL carve-out does not apply. No CP driver change is
required.

### §14.17.8.4 Invariants (amend §14.17.5)

- **Inv 3 (amended).** Every hook site fires only when the emitter and hook are bound. Default
  config emits zero spans and delivers zero content. No bound hook skips work silently.
- **Inv 6 (amended).** Hook 2 enforces membership and uniqueness as a step failure
  (§14.17.8.2 item 2). Spans are never emitted for an invalid selection. The failure propagates
  through C-RT-16 without retry, candidate advance or breaker charge (§14.17.8.3).
- **Inv 7 (amended).** `version_sha` and `body_tokens` derive from the loaded content bytes
  (§14.17.8.1). For every delivered block, `version_sha` in the block, in the span and on
  `ctx.skills[id].manifest` is the same value and equals `git hash-object` of the loaded file.
- **New inv 8.** Delivered content equals the bytes loaded at bootstrap. No dispatch-time read,
  cache or fallback source exists.

### §14.17.8.5 Witnesses (behavioral; required for source conformance)

- **W1 load.** A manifest plus a content file loads. `content` equals the file text. `version_sha`
  equals `git hash-object` of the content file, not of the manifest. `body_tokens` is
  `len(content) // 4`.
- **W2 load failures.** One case per reason: missing, unreadable (permission denied), invalid UTF-8,
  whitespace-only and pinned-mismatch content each raise `SkillContentInvalidError` with that
  reason. Bootstrap stage 2 aborts on each.
- **W3 delivery.** A workflow step dispatched with a hook selecting `[a, b]` reaches the
  provider adapter. The system prompt there is the base, then block `a`, then block `b`, then the
  memory packet when one is bound. Exactly two spans are emitted, with matching `version_sha`.
- **W4 selection failures.** A workflow step whose hook returns an unknown id, or a duplicate id,
  runs under C-RT-16 with at least two fallback candidates and `max_attempts >= 2`. The run ends
  with `RunResult.status = FAILED` and a `fail_class` beginning
  `step-failure: RT-FAIL-SKILL-SELECTION-INVALID:`, with the reason in the message. The test
  observes zero `skill.activation` spans, zero provider calls on every candidate, one attempt span
  with `retry.terminal = "skill-selection-invalid"` and no `fallback.exhausted` event. The primary
  candidate's breaker records no failure: its state and failure count are unchanged.
- **W4b half-open trial.** With the primary breaker in a half-open trial, the same selection
  failure returns the breaker to `open` with `opened_at` renewed to the failure time and
  `fail_count` unchanged. The emitted `half_open → open` transition has `trigger_count = 0`, the
  non-charging re-arm, not a charging re-trip.
- **W5 opt-out and empty.** With no hook, and with a hook returning `[]`, the provider sees the
  pre-v1.139 payload byte-for-byte and zero spans are emitted.
- **W6 conflict.** Skills selected while the payload carries its own system source raise the
  existing `RT-FAIL-PROMPT-INJECTION-CONFLICT`.
- **W7 bind.** Constructing a dispatcher with a hook and without a `skills` mapping raises
  `LLMDispatchBindError`.
- **W8 immutability.** Changing the content file after bootstrap does not change the next
  dispatch's delivered block or `version_sha`.

### §14.17.8.6 Source sites (informative)

`harness-runtime/src/harness_runtime/lifecycle/skills.py` (load, `Skill.content`, errors),
`lifecycle/llm_dispatch.py` (hook 2 at the current 1256–1286 block, and composition at the
effective-system-prompt site before `compose_system_prompt_with_memory_packet`),
`lifecycle/skill_activation.py` (unchanged emitter; the selection check precedes `emit`),
`lifecycle/retry_breaker_fallback.py` (by-name propagation arm),
`harness_runtime/types.py` (no field change expected), `harness-cp` `workflow_driver.py` (unchanged;
`_step_fail_class` reads the marker), and `tests/test_lifecycle_skills.py`,
`tests/test_lifecycle_skill_activation.py` and the two skill integration tests (fixtures gain
content files).

### §14.17.8.7 Out of scope

Operator-explicit content delivery (hook 3), workflow-init delivery (hook 1), skill-declared tool
bindings, discovery beyond `PathClass.SKILLS`, token budgeting of delivered content, and installed
acceptance (B7 and installed-root gates remain held).
