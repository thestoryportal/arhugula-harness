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
| **F1** | **Class 1 (blocking)** | The port silently flipped `anthropic_optional` / `openai_optional` / `ollama_optional` defaults `False` → `True`, reversing the operator-ratified fail-fast default (`.harness/class_1_fork_provider_construction_allowlist_semantic.md`, E-prod-3; ADR-F1 v1.2) — under a commit that affirmatively claimed conservative defaults. | Restored all three field defaults to `False` in `types.py` (+ docstrings) and `anthropic_optional = false` in `harness.toml.example`; updated `test_config_loader.py` to assert the fail-fast default. Preferring soft-degradation remains a deliberate opt-in. |
| **F4** | Class 2 | Spawned CLIs inherited the full harness environment, incl. `*_API_KEY` vars. The `claude`/`codex`/`gemini` CLIs prefer an inherited API key over their OAuth session — silently converting the subscription route into **metered API billing** and exporting harness secrets into an agentic child process. Acute here: this workspace loads keys into the env via `just` dotenv. | `AsyncioSubprocessRunner.run` now passes a scrubbed env (`_scrubbed_child_env`) that strips `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` / `GEMINI_API_KEY` / `GOOGLE_API_KEY` / `GOOGLE_APPLICATION_CREDENTIALS`. |
| **F5** | Class 3 | `_go_seconds_duration` used `:.3g`, producing invalid Go duration `"1.2e+03s"` for timeouts ≥ 1000s (antigravity `--print-timeout`). | Format as a plain trimmed decimal (`"1200s"`, `"0.5s"`). |
| **F9** | Class 3 | `harness.toml.example` routing manifest used `claude_code` as fallback primary (+ codex/antigravity hops) while the `[[runtime.external_cli_providers]]` blocks are commented out — a copied example burns dead candidates. | Restored the SDK-only (`anthropic` primary) manifest + a comment explaining how to opt into CLI routing. |

## Registered for follow-up (not fixed in WS1)

| ID | Sev | Finding | Disposition |
|---|---|---|---|
| **F2** | Class 2 | External-CLI dispatches get **no memory retrieval/injection** under the default policy: `select_memory_access_mode` picks `STANDARD_MEMORY_TOOLS` for non-anthropic/non-openai providers (provider capabilities hardcode `supports_tools=True`), but the standard-tools executor path exists only in the openai dispatch branch, and no prompt packet is rendered → a `claude_code`/`codex` dispatch injects no memory. Main's `MemoryAccessModeRequest.external_cli_route` seam is left unpopulated by `automatic_memory.compose_for_dispatch`. **Pre-exists for ollama** (not a regression) and **matches deployed**, but the port extends it to the headline routing path. | **Top follow-up.** Inert under the conservative default (CLI routing off by default). Proper fix (provider-capability-aware reflection, or wiring `external_cli_route` so CLI kinds fall through to `PROMPT_EXTENSION_PACKET`) belongs in a focused memory-substrate arc with a witness test. Register as R-IF / forward item. |
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

## Open operator decision

**Default routing posture.** WS1 lands the conservative default (external-CLI routing OFF /
opt-in; hosted-SDK routing + fail-fast preserved) to avoid silently changing behavior. The
deployed repo runs the *opposite* posture (prefer OAuth CLI + soft-degrade by default). If
the operator wants deployed-parity-by-default, that is a separate, explicit, ratified change
(fork-doc / ADR note flipping `enabled_provider_names` to `CLI_PREFERRED_ENABLED_PROVIDER_NAMES`
and `external_cli_providers` to `DEFAULT_EXTERNAL_CLI_PROVIDERS`), not a silent default flip.
