# U-MEM-25 Memory Closeout Evidence

Status: provider-free memory substrate closeout evidence ready for review.

This packet is the human-facing closeout checklist for U-MEM-25. It maps every
R-MEM and C-MEM item to implementation and verification evidence, records the
review path, and names the remaining live credential gates without executing
provider calls.

## R-MEM Closeout Matrix

| Requirement | Closeout evidence | Verification evidence |
| --- | --- | --- |
| R-MEM-01 - Full memory layer, no limited MVP | Canonical store, policy, retrieval, access modes, native adapter, standard tools, migration, redaction, observability, and verification matrix are all implemented across `harness-is`, `harness-cp`, `harness-as`, and `harness-runtime`. | U-MEM-24 matrix plus `just memory-closeout-check`. |
| R-MEM-02 - Canonical filesystem/git store | Memory path registry, filesystem-backed operations, operation ledger, and derived retrieval indexes preserve canonical store ownership. | Path registry, operation ledger, retrieval-index, and durability selectors in `harness-runtime/src/harness_runtime/memory_verification_suite.py`. |
| R-MEM-03 - Typed memory records | Typed record envelopes cover episodic, semantic, preference, procedural, compaction, migration, and redaction records. | Schema validation selectors in the C-MEM-20 matrix. |
| R-MEM-04 - Automatic episodic and durable capture | Runtime capture paths create scoped records and durable operation-ledger rows. | Operation ledger and durability selectors in the matrix. |
| R-MEM-05 - Semantic and preference promotion | Promotion candidates and review services prevent model-authored records from becoming injectable without approval. | Promotion policy and memory-poisoning selectors in the matrix. |
| R-MEM-06 - Compaction safety | Compaction requires one durable disposition per candidate and records discard, keep, promote, or queue decisions. | Compaction safety selectors in the matrix. |
| R-MEM-07 - Retrieval and ranking | Retrieval is deterministic for fixed store, policy, request, and index inputs. | Retrieval and retrieval-index selectors in the matrix. |
| R-MEM-08 - Memory packet assembly and injection | Runtime context assembly builds prompt packets only from policy-filtered records and redaction-safe content. | Prompt fallback, retrieval denial, and redaction selectors in the matrix. |
| R-MEM-09 - Multi-provider memory routing | Access-mode scenarios cover native provider memory, standard memory tools, prompt fallback, and no-access denial. | Access-mode scenarios in `ACCESS_MODE_VERIFICATION_SCENARIOS`. |
| R-MEM-10 - CLI-neutral and CLI-specific profiles | CLI profiles cover generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom routes. | CLI profile scenarios and fake-subprocess external route selectors in `CLI_PROFILE_VERIFICATION_SCENARIOS` and `EXTERNAL_CLI_ROUTING_SCENARIOS`. |
| R-MEM-11 - Engine-class durability | Durable engine classes are covered by operation-ledger and runtime durability selectors. | Engine-class durability row in the C-MEM-20 matrix. |
| R-MEM-12 - Redaction, privacy, and scope controls | Redaction, tombstone, retention, and cross-scope denial exclude unavailable records from packets and tools while keeping audit sidecars. | Redaction, retrieval, memory tool, policy, and access-mode denial selectors. |
| R-MEM-13 - Observability | Memory telemetry spans and operation/failure classifications are wired across capture, retrieval, tools, native adapter, migration, redaction, and lifecycle paths. | Observability implementation is covered by the U-MEM-22 selectors and the full provider-free local gate. |
| R-MEM-14 - Review and administration | Promotion review, administrative evidence packets, live-gate records, and this U-MEM-25 closeout packet make memory state reviewable. | `tools/memory_closeout_check.py`, `just memory-closeout-check`, and closeout review evidence below. |
| R-MEM-15 - Migration and compatibility | Callback-backed migration supports dry-run reports and explicit `migrate` events without silent canonical writes. | Migration compatibility tests from U-MEM-23 and provider-free local gate evidence. |

## C-MEM Closeout Matrix

| Contract | Closeout evidence | Verification evidence |
| --- | --- | --- |
| C-MEM-01 - Memory plane boundary | Memory store, access-mode, policy, retrieval, and runtime projection boundaries stay separated. | Matrix rows for schema validation, cross-scope denial, prompt fallback, standard tools, and native adapter. |
| C-MEM-02 - Canonical path registry | Path registry rejects traversal and scopes memory paths. | `path_traversal_rejection` selectors. |
| C-MEM-03 - Common record identity | Record envelopes carry stable identity, scope, provenance, timestamps, and hashes. | `schema_validation` selectors. |
| C-MEM-04 - Episodic records | Episodic capture records preserve source and scope before promotion. | Record-envelope and operation-ledger selectors. |
| C-MEM-05 - Semantic records | Semantic records are promotion-gated and retrieval-ranked. | Promotion policy, memory-poisoning, retrieval, and retrieval-index selectors. |
| C-MEM-06 - Preference records | Preference promotion is explicit and policy-reviewed. | Promotion policy selectors. |
| C-MEM-07 - Procedural snapshots | Procedural snapshots remain typed records with scoped durability. | Schema validation and engine-class durability selectors. |
| C-MEM-08 - Memory operation ledger | Memory mutations append ledger entries with hash-chain continuity. | `append_only_ledger_hash_chain` and `concurrent_writer_no_fork` selectors. |
| C-MEM-09 - Memory policy | Policy governs capture, promotion, retrieval, access modes, and cross-scope denial. | Policy schema, cross-scope denial, and access-mode selectors. |
| C-MEM-10 - Promotion pipeline | Candidate extraction and review bind promotion before injection. | `promotion_policy` and `memory_poisoning` selectors. |
| C-MEM-11 - Retrieval and ranking | Retrieval output is deterministic under fixed inputs and excludes disallowed records. | `retrieval_determinism` and `cross_scope_cross_tenant_denial` selectors. |
| C-MEM-12 - Memory packet assembly | Prompt packets are assembled from filtered records and provider-neutral context carriers. | `prompt_packet_fallback`, `memory_poisoning`, and redaction selectors. |
| C-MEM-13 - Provider memory access modes | Native memory, standard tools, prompt packet, and no-access mode are typed scenarios. | `ACCESS_MODE_VERIFICATION_SCENARIOS`. |
| C-MEM-14 - Provider-neutral memory tools | Standard memory tools expose controlled read/list/write behavior on tool-capable paths. | `standard_memory_tools` selectors. |
| C-MEM-15 - Native provider memory adapters | Native provider adapters are separated from prompt fallback and standard tools. | `native_anthropic_adapter` selectors plus live Anthropic gate. |
| C-MEM-16 - CLI profiles | CLI profile resolution supports generic and vendor-specific routes without hard-coded auth assumptions. | `cli_profile_resolution` selectors and external CLI route scenarios. |
| C-MEM-17 - Engine-class durability | Durable engine classes preserve memory operation evidence across restart/resume boundaries. | `engine_class_durability` selectors. |
| C-MEM-18 - Redaction, tombstone, and retention | Redacted, tombstoned, and expired records stay auditable but unavailable to retrieval/tools. | `redaction_tombstone_exclusion` selectors. |
| C-MEM-19 - Observability | Memory operations and failures emit structured telemetry without leaking content. | U-MEM-22 observability tests and provider-free local gate. |
| C-MEM-20 - Verification contract | The C-MEM-20 evidence matrix indexes deterministic selectors and live credential gates. | [memory_verification_suite.py](../harness-runtime/src/harness_runtime/memory_verification_suite.py) and `just memory-closeout-check`. |

## Review Evidence

- U-MEM-24 added [memory_verification_suite.py](../harness-runtime/src/harness_runtime/memory_verification_suite.py), including `LIVE_CREDENTIAL_GATES`, access-mode scenarios, CLI profile scenarios, external CLI route scenarios, and deterministic selector coverage for every C-MEM-20 verification requirement.
- U-MEM-24 focused verification passed: missing-module RED before implementation, 5 focused tests, 160 provider-free matrix-selector tests, ruff/format/pyright, overlay check, provider-free `codex-check`, PR CI, and no-upload concrete-diff review.
- U-MEM-25 adds [memory_closeout_check.py](../tools/memory_closeout_check.py) and wires `just memory-closeout-check` so the R-MEM/C-MEM closeout mapping stays provider-free and repeatable.
- `just codex-review` remains the required decorrelated review command. Tenant policy blocks sending uncommitted private diffs to the external review surface in this environment; the approved substitute is a no-upload concrete-diff review plus `git diff --check`.

## Remaining Gates And Blockers

No provider-free U-MEM-25 blocker remains once `just memory-closeout-check`,
docs link checks, overlay checks, `just codex-check`, review, and closeout pass.

Live checks are explicitly gated, not silently skipped:

| Gate | External dependency | Deterministic absence probe | Resume surface |
| --- | --- | --- | --- |
| `live-anthropic-native-memory` | `ANTHROPIC_API_KEY` and paid provider execution | Provider-free native adapter callback tests pass locally. | `codex-credential-gate:U-MEM-24:anthropic-native-memory` |
| `live-claude-code-cli-auth` | Authenticated local Claude Code CLI session | Fake-subprocess route resolves `claude-code:claude`. | `codex-credential-gate:U-MEM-24:claude-code-cli-auth` |
| `live-codex-cli-auth` | Authenticated local Codex CLI session | Fake-subprocess route resolves `codex:codex`. | `codex-credential-gate:U-MEM-24:codex-cli-auth` |
| `live-antigravity-cli-auth` | Authenticated local Antigravity CLI session | Fake-subprocess route resolves `antigravity:antigravity`. | `codex-credential-gate:U-MEM-24:antigravity-cli-auth` |
| `live-gemini-legacy-cli-auth` | Authenticated local legacy Gemini CLI session | Fake-subprocess route resolves `gemini:gemini`. | `codex-credential-gate:U-MEM-24:gemini-legacy-cli-auth` |
| `live-generic-command-cli-auth` | Operator-declared generic external CLI auth | Fake-subprocess route resolves `generic-command:custom`. | `codex-credential-gate:U-MEM-24:generic-command-cli-auth` |

### Live Confirmation Resume Tests

U-MEM-live-confirmations adds the declared U-MEM-24 e2e resume surfaces:

- `harness-runtime/tests/integration/test_u_mem_24_live_memory.py`
  runs `-m e2e -k anthropic_native_memory` against the hosted Anthropic
  Memory tool and asserts the canonical `CanonicalNativeMemoryToolBackend`
  writes `TOOL_EVENT` records plus `NATIVE_ADAPTER_CALL` operation-ledger rows.
- `harness-runtime/tests/integration/test_u_mem_24_live_cli_routes.py`
  runs `-m e2e -k {claude_code,codex,antigravity,gemini_legacy,generic_command}`
  and binds real local CLI status probes to `ExternalCliRoute` carriers without
  printing or moving credential values.

Pass/skip semantics are explicit. Anthropic skips only when `ANTHROPIC_API_KEY`
is absent from the live execution environment. Claude Code and Codex pass only
when the local CLI is installed and reports authenticated status; the Codex
probe strips `OPENAI_API_KEY` and requires ChatGPT subscription auth. Antigravity
passes when its CLI binary `agy` is installed and the declared `agy models` auth
probe exits 0 with non-empty stdout, and skips when either condition fails.
Legacy Gemini skips when its CLI is absent, and otherwise runs the auth probe
declared on `PROVIDER_PRESETS["gemini"].auth_args` through the production
`construct_gemini_cli_adapter`, skipping with the probe's own failure text when
that probe does not confirm a session. The generic-command gate skips when
`U_MEM_24_GENERIC_COMMAND_AUTH_PROBE` is unset; its standing operator-ratified
value is `ollama list`, embedded in the gate's `resume_command`.

Observed local live-confirmation status on 2026-07-03; the three
previously NOT CONFIRMED rows were re-grounded on 2026-07-27:

| Gate | Local status | Evidence |
| --- | --- | --- |
| `live-anthropic-native-memory` | PASS | `test_u_mem_24_live_memory.py -m e2e -k anthropic_native_memory` passed against the hosted provider and asserted canonical native-adapter ledger rows. |
| `live-claude-code-cli-auth` | PASS | `test_u_mem_24_live_cli_routes.py -m e2e -k claude_code` passed in the broader local Claude Code auth boundary. |
| `live-codex-cli-auth` | PASS | `test_u_mem_24_live_cli_routes.py -m e2e -k codex` passed with `OPENAI_API_KEY` stripped and ChatGPT subscription auth required. |
| `live-antigravity-cli-auth` | PASS (2026-07-27) | `test_u_mem_24_live_cli_routes.py -m e2e -k antigravity` passed. The 2026-07-03 NOT CONFIRMED was a wrong-binary-name probe: the Antigravity CLI binary is `agy` per the repo's own `PROVIDER_PRESETS["antigravity"]` preset (`tools/external_cli_provider_config.py`), not `antigravity`. Live evidence: `agy` v1.1.7 at `/Users/robertrhu/.local/bin/agy`; the production `construct_antigravity_cli_adapter` auth probe (`_antigravity_auth_argv` -> `agy models`) exits 0 with a non-empty model list. Negative control: the same constructor against command `antigravity` fails ENOENT/127, reproducing the original false reading. The test now sources the executable name from the preset so the defect cannot recur. |
| `live-gemini-legacy-cli-auth` | NOT CONFIRMED - upstream tier ineligibility (2026-07-27) | The 2026-07-03 "not installed" reason is false at HEAD: `gemini` v0.49.0 is installed at `~/.local/share/mise/installs/node/24/bin/gemini`, with a logged-in OAuth session at `~/.gemini/oauth_creds.json`. v0.49.0 ships no auth/status subcommand, so the only available probe is an outward model call; that probe is now DECLARED at `PROVIDER_PRESETS["gemini"].auth_args` as `--skip-trust -p "Reply with the single word OK."` (the preset keeps `auth_check=False`, so constructing a Gemini adapter never fires it implicitly). Fired live under operator standing approval: exit 1 with `IneligibleTierError: This client is no longer supported for Gemini Code Assist for individuals.` (upstream `UNSUPPORTED_CLIENT` on `free-tier`), so the gate stays NOT CONFIRMED - the legacy client is deprecated upstream for individual accounts and superseded by the Antigravity (`agy`) route, whose own gate is CONFIRMED above. `test_u_mem_24_live_cli_routes.py -m e2e -k gemini_legacy` is no longer an unconditional skip stub: it now sources both the executable and the probe argv from the preset, drives the production `construct_gemini_cli_adapter` auth path, and skips carrying the probe's verbatim failure text. Negative control: the same constructor with `auth_args` cleared raises `ExternalCLINotAuthenticatedError("Gemini CLI auth_check=true requires auth_args")`, a distinct reason from the tier rejection. |
| `live-generic-command-cli-auth` | PASS (2026-07-27) | `U_MEM_24_GENERIC_COMMAND_AUTH_PROBE="ollama list" pytest harness-runtime/tests/integration/test_u_mem_24_live_cli_routes.py -m e2e -k generic_command` passed and bound `generic-command:custom`. Live evidence: `ollama` 0.18.3 at `/usr/local/bin/ollama`; the daemon was already up via Ollama.app and was left running, so no environment state was changed or needed restoring; the probe `ollama list` exits 0. `ollama list` is now the STANDING operator-ratified declaration (operator standing approval 2026-07-27), embedded in the gate's `resume_command` at `memory_verification_suite.py`; no default is baked into the environment variable itself, so the deterministic-absence negative control still holds - with `U_MEM_24_GENERIC_COMMAND_AUTH_PROBE` unset the test skips rather than passing vacuously. |
