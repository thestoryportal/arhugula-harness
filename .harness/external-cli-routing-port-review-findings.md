# External-CLI (OAuth) routing port — review findings + dispositions

**Arc:** port the external-CLI / OAuth multi-LLM routing capability from the deployed
sibling repo `thestoryportal/arhugula` (commits `ad690ed` + `c2ca63c`) into
`arhugula-v2` main, so the routing lives in both repos (feature work continues here;
the deployed repo was a point-in-time test). Impl commit: `59302905` on branch
`feat/external-cli-oauth-routing-port`.

**Decorrelated review (2026-07-09):** two independent reviewers on the committed diff —
an out-of-family **Fable 5** reviewer (Codex subscription inactive, so Fable 5 stood in
for the `just codex-review` role) + the Claude **harness-adversarial-reviewer**. They
**agreed** on the one blocking finding (strongest possible signal). Full transcripts are
in the job task outputs; this file is the durable disposition record.

Both verified independently: memory-substrate (U-MEM) hooks in `llm_dispatch.py` are
**preserved** (the only deleted line is an `else:` → `elif` conversion; the
`capture_turn_completion` hook fires after the new external-CLI branch and tolerates the
CLI path's `None` token counts); the conservative default otherwise holds; subprocess
execution is argv-only (no shell); lineage is clean (21 routing-scoped files, no
docs/packaging/portable leakage); pyright-strict + ruff clean.

## Fixed in the port PR (WS1)

| ID | Sev | Finding | Fix |
|---|---|---|---|
| **F1** | **Class 1 (blocking)** | The port *silently* flipped `anthropic_optional` / `openai_optional` / `ollama_optional` defaults `False` → `True`, reversing the operator-ratified fail-fast default (`.harness/class_1_fork_provider_construction_allowlist_semantic.md`, E-prod-3; ADR-F1 v1.2) — under a commit that affirmatively claimed conservative defaults. | First restored to `False` (removing the SILENT flip), then — after the operator chose **deployed-parity (prefer-OAuth by default)** at the AskUserQuestion below — flipped to `True` again, now as an **explicit ratified change**: recorded in fork-doc §10 amendment, with `types.py` docstrings + `harness.toml.example` + `test_config_loader.py::test_enabled_provider_names_defaults_to_prefer_oauth` all naming the 2026-07-09 ratification. The `ProviderAuthError` carve-out is unchanged; `SDK_ONLY_ENABLED_PROVIDER_NAMES` is the explicit fail-fast opt-out. |
| **F4** | Class 2 | Spawned CLIs inherited the full harness environment, incl. `*_API_KEY` vars. The `claude`/`codex`/`gemini` CLIs prefer an inherited API key over their OAuth session — silently converting the subscription route into **metered API billing** and exporting harness secrets into an agentic child process. Acute here: this workspace loads keys into the env via `just` dotenv. | `AsyncioSubprocessRunner.run` now passes a scrubbed env (`_scrubbed_child_env`) that strips `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` / `GOOGLE_API_KEY` / `GOOGLE_APPLICATION_CREDENTIALS`. |
| **F5** | Class 3 | `_go_seconds_duration` used `:.3g`, producing invalid Go duration `"1.2e+03s"` for timeouts ≥ 1000s (antigravity `--print-timeout`). | Format as a plain trimmed decimal (`"1200s"`, `"0.5s"`). |
| **F9** | Class 3 | `harness.toml.example` routing manifest used `claude_code` as fallback primary (+ codex/antigravity hops) while the `[[runtime.external_cli_providers]]` blocks are commented out — a copied example burns dead candidates. | Restored the SDK-only (`anthropic` primary) manifest + a comment explaining how to opt into CLI routing. |

## Registered for follow-up (not fixed in WS1)

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| **F2** | Class 2 → **FIXED** | External-CLI dispatches got **no memory retrieval/injection** under the default policy: `select_memory_access_mode` picked `STANDARD_MEMORY_TOOLS` for non-anthropic/non-openai providers (capabilities hardcode `supports_tools=True`), but the standard-tools executor path exists only in the openai dispatch branch → a `claude_code`/`codex` dispatch injected no memory. **Elevated to must-fix** because the operator chose prefer-OAuth (CLI is now the default routing path). | **Fixed in WS1.** `reflect_memory_provider_capabilities` gained an `is_external_cli` flag (CLI adapters have no tool loop → `supports_standard_memory_tools=False`, `supports_native_memory=False`), so selection falls through to `PROMPT_EXTENSION_PACKET`; `LocalAutomaticMemoryRuntime` passes `is_external_cli` from `config.external_cli_providers`. The packet then reaches the CLI via the existing `compose_system_prompt_with_memory_packet` → `_effective_system_prompt` → `_payload_to_external_cli_prompt(system=...)` path (no dispatch-branch change). Witness: `test_memory_access_mode.py::test_external_cli_binding_selects_prompt_packet_not_standard_tools` (with a contrasting no-flag baseline). Better than deployed, which still has the gap. |
| **F3** | Class 2 | Prompt-in-argv for antigravity / gemini / generic-`arg`-transport has no `--` end-of-options separator; a prompt beginning with `-`/`--` (pipeline-influenceable content) could be parsed as flags. Also visible in `ps`. No shell is ever used. Matches deployed. | Hardening follow-up: insert `--` where the CLI supports it / prefer stdin. Not done in WS1 because the affected adapters (antigravity/gemini) are live-gated and untestable here — changing their transport risks breaking an unverifiable path. |
| **F6** | Class 3 | Timeout `process.kill()` reaps only the direct child; these CLIs spawn subprocesses → possible orphans. | Hardening follow-up (`start_new_session=True` + killpg). Matches deployed. |
| **F7** | Class 3 | No validator forbids an `external_cli_providers` entry from taking a builtin provider name (`anthropic`/`openai`/`ollama`); the builtin construction branch wins and the CLI config is silently dropped. Inert under conservative default (empty by default). | Follow-up: fail-loud validator or documented reservation. |
| **F8** | Class 3 | Auth-probe / CLI stderr (which can carry account identity, e.g. "Logged in as …") flows into `ProviderDegradedWarning` + span telemetry (`fallback.last_failure_detail`, bounded 500 chars). Tokens unlikely. | Note only; consider redacting identity from degraded telemetry. |
| **F1-03** | Class 3 | Codex auth-status uses a fragile stdout substring heuristic vs Claude's structured `loggedIn` check. Fails-closed; faithful to deployed. | Note only. |

## Governance follow-up (WS2)

- **ADR-D7 stale claim:** `ADR-D7_memory_substrate.md` §15 ("a separate existing substrate … not the gap") and §86 ("Existing external CLI routing remains the provider-construction authority") are now stale present-tense — the routing is owned in this repo as of this port. Correct them. (§17 is commit-pinned to `cc612ec8` and is NOT stale — do not touch.)
- **Overlay cite hygiene:** `external_cli_provider.py` is an advisory `code_without_cite` orphan (carries `R-CLI-1`, no `C-*`). The overlay drift gate is GREEN (soft orphan, not a HARD `cxa_seam_missing_endpoint`). Add the implied `C-MEM-*` cite (`Spec_Memory_Substrate_v1.md` §"C-MEM-16 CliProfile" / line ~540) or formally register `R-CLI-1`.
- **X-AL-3:** the routing port is the design-*anticipated* "routing port lands" event mandated by ADR-D7 (§17/§87) + named file-for-file in `Implementation_Plan_Memory_Substrate_v1.md`. NOT a silent design extension.
- **Clearance markers** for the 5 "Proposed" memory design artifacts + CLAUDE.md §2 pointer refresh (memory + routing) + stale spec-version bumps (CP v1.38→v1.85, OD v1.28→v1.30, Runtime v1.52→v1.92).

## Operator decision — RESOLVED (2026-07-09)

**Default routing posture.** Surfaced via AskUserQuestion. The operator chose
**deployed-parity (prefer OAuth by default)**: `enabled_provider_names` defaults to
`DEFAULT_ENABLED_PROVIDER_NAMES` (CLI providers first) and `external_cli_providers` to
`DEFAULT_EXTERNAL_CLI_PROVIDERS` (claude_code/codex/antigravity), with `*_optional=True`
soft-degrade as the coherent companion. Landed as an **explicit ratified change** (fork
§10 amendment), not a silent flip. `SDK_ONLY_ENABLED_PROVIDER_NAMES` is the documented
opt-out. This choice is what elevated F2 to must-fix (now fixed above), since CLI routing
is now the default path.
