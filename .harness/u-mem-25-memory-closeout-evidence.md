# U-MEM-25 Memory Closeout Evidence

Status: provider-free memory substrate closeout evidence ready for review, **scoped to `Spec_Memory_Substrate_v1.md` v1.1 and `Implementation_Plan_Memory_Substrate_v1.md` v1.1 (U-MEM-01..26)**. The v1.1 obligations added at the `B-86` spec leg **are certified here** as of the U-MEM-26 impl leg (2026-07-28): all six rows that carried a `PENDING — U-MEM-26` marker are re-opened and extended below. The **v1.2** obligations added at the `B-92` spec leg are **not** certified here; six rows carry an explicit `PENDING — U-MEM-27` marker (C-MEM-03, C-MEM-10, R-MEM-01, R-MEM-05, R-MEM-09, R-MEM-14). See "Version scoping" under Remaining Gates And Blockers for both interim windows - the v1.1 one and its closure, and the v1.2 one still open.

This packet is the human-facing closeout checklist for U-MEM-25. It maps every
R-MEM and C-MEM item to implementation and verification evidence, records the
review path, and names the remaining live credential gates without executing
provider calls.

## R-MEM Closeout Matrix

| Requirement | Closeout evidence | Verification evidence |
| --- | --- | --- |
| R-MEM-01 - Full memory layer, no limited MVP | Canonical store, policy, retrieval, access modes, native adapter, standard tools, migration, redaction, observability, and verification matrix are all implemented across `harness-is`, `harness-cp`, `harness-as`, and `harness-runtime`. **v1.1 obligations CERTIFIED at the U-MEM-26 impl leg (2026-07-28).** The unit the plan v1.1 added to this requirement's unit range landed in full: the C-MEM-13 cross-family withhold guard at `_standard_memory_tools_context`, the `B-89` writer-side repair (capture consumes the run's composed `record_scope`) with the `B-90` `tenant`/`workload_class` fold-in, the C-MEM-03 value domain enforced at every scope-AUTHORING durable write, and request- plus direct-reader-boundary enforcement with per-predicate null denial. No U-MEM-26 obligation is outstanding. **Evidences the v1.1 obligations only.** v1.2 obligations (the U-MEM-27 unit added to this requirement's unit range): **PENDING — U-MEM-27**. | U-MEM-24 matrix plus `just memory-closeout-check`, extended by the 39 U-MEM-26 witnesses at `harness-is/tests/test_memory_scope_value_domain.py` (19) and `harness-runtime/tests/test_u_mem_26_write_boundary.py` (20), plus the slice-3 dispatch witnesses at `harness-runtime/tests/test_lifecycle_llm_dispatch.py` and `harness-runtime/tests/test_automatic_memory_runtime.py`. Arc record at `.harness/u-mem-26-impl-leg-close-2026-07-28.md`. |
| R-MEM-02 - Canonical filesystem/git store | Memory path registry, filesystem-backed operations, operation ledger, and derived retrieval indexes preserve canonical store ownership. | Path registry, operation ledger, retrieval-index, and durability selectors in `harness-runtime/src/harness_runtime/memory_verification_suite.py`. |
| R-MEM-03 - Typed memory records | Typed record envelopes cover episodic, semantic, preference, procedural, compaction, migration, and redaction records. | Schema validation selectors in the C-MEM-20 matrix. |
| R-MEM-04 - Automatic episodic and durable capture | Runtime capture paths create scoped records and durable operation-ledger rows. | Operation ledger and durability selectors in the matrix. |
| R-MEM-05 - Semantic and preference promotion | Promotion candidates and review services prevent model-authored records from becoming injectable without approval. **Evidences the v1.1 obligations only.** v1.2 obligations (the C-MEM-10 review gate on cross-family-captured promotion candidates - such a candidate is review-required and never auto-promotable): **PENDING — U-MEM-27**. | Promotion policy and memory-poisoning selectors in the matrix. |
| R-MEM-06 - Compaction safety | Compaction requires one durable disposition per candidate and records discard, keep, promote, or queue decisions. | Compaction safety selectors in the matrix. |
| R-MEM-07 - Retrieval and ranking | Retrieval is deterministic for fixed store, policy, request, and index inputs. | Retrieval and retrieval-index selectors in the matrix. |
| R-MEM-08 - Memory packet assembly and injection | Runtime context assembly builds prompt packets only from policy-filtered records and redaction-safe content. | Prompt fallback, retrieval denial, and redaction selectors in the matrix. |
| R-MEM-09 - Multi-provider memory routing | Access-mode scenarios cover native provider memory, standard memory tools, prompt fallback, and no-access denial. **v1.1 obligations CERTIFIED at U-MEM-26 (2026-07-28).** Cross-family withholding on a SERVABLE dispatch landed as the sixth conjunct of `_standard_memory_tools_context` (`harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py`), sharing `_packet_scope_matches_dispatch_family` verbatim with `_degraded_serve_disposition` so a cross-family dispatch cannot fall through to the `arm_unservable` repair branch; the recording surface is the C-MEM-19 degraded span carrying the named denial reason `provider_family_scope_mismatch` with `record_count=0` and no `packet_hash`, and the dispatch itself still completes. **Evidences the v1.1 obligations only.** v1.2 obligations (per-stored-record cross-family capture provenance, and the promotion gate that reads it): **PENDING — U-MEM-27**. | Access-mode scenarios in `ACCESS_MODE_VERIFICATION_SCENARIOS`, plus the U-MEM-26 dispatch witnesses `test_u_mem_26_cross_family_ollama_dispatch_withholds_tools_and_packet`, `test_u_mem_26_cross_family_openai_dispatch_withholds_tools_and_packet`, and `test_u_mem_26_same_family_dispatch_exposure_is_unchanged` in `harness-runtime/tests/test_lifecycle_llm_dispatch.py`; `test_u_mem_26_capture_is_unaffected_by_the_cross_family_withholding` in `harness-runtime/tests/test_automatic_memory_runtime.py`; and the inverted production-path assertion in `harness-runtime/tests/integration/test_r300_cross_family_fallback_e2e.py`. |
| R-MEM-10 - CLI-neutral and CLI-specific profiles | CLI profiles cover generic, Claude Code, Codex, Antigravity, legacy Gemini, and custom routes. | CLI profile scenarios and fake-subprocess external route selectors in `CLI_PROFILE_VERIFICATION_SCENARIOS` and `EXTERNAL_CLI_ROUTING_SCENARIOS`. |
| R-MEM-11 - Engine-class durability | Durable engine classes are covered by operation-ledger and runtime durability selectors. | Engine-class durability row in the C-MEM-20 matrix. |
| R-MEM-12 - Redaction, privacy, and scope controls | Redaction, tombstone, retention, and cross-scope denial exclude unavailable records from packets and tools while keeping audit sidecars. **v1.1 obligations CERTIFIED at U-MEM-26 (2026-07-28).** Run-level `provider_family` keying is now the writer's only source (`EpisodicMemoryCapture` takes the run's composed `record_scope`; both construction sites pass it, and the raw provider key survives only on the C-MEM-08 payload and the C-MEM-19 span). Asymmetric `null` semantics are enforced per predicate rather than at the policy leg alone - `_scope_mismatch`, `_scope_matches`, and `_scope_not_broader` each deny a `provider_family=None` request against a family-scoped record independently. `B-90` is closed: the composed scope carries `tenant` and `workload_class`, denied at all three predicates separately. Redaction is deliberately exempt from the write validator (LEGACY-REDACTION preserve-verbatim), so a legacy raw-key record stays redactable and tombstonable with its scope byte-intact. | Redaction, retrieval, memory tool, policy, and access-mode denial selectors, plus the U-MEM-26 read-boundary witnesses in `harness-is/tests/test_memory_scope_value_domain.py` (null-asymmetry pair, per-layer null denial incl. end-to-end `DerivedRetrievalIndexStore.retrieve`, the three separate `B-90` tenant-denial assertions) and the write-boundary witnesses in `harness-runtime/tests/test_u_mem_26_write_boundary.py` (composed-scope capture, round-trip retrievability, `test_legacy_raw_key_record_stays_redactable_with_its_scope_intact` in both its `redact` and `tombstone` parametrizations). |
| R-MEM-13 - Observability | Memory telemetry spans and operation/failure classifications are wired across capture, retrieval, tools, native adapter, migration, redaction, and lifecycle paths. | Observability implementation is covered by the U-MEM-22 selectors and the full provider-free local gate. |
| R-MEM-14 - Review and administration | Promotion review, administrative evidence packets, live-gate records, and this U-MEM-25 closeout packet make memory state reviewable. **Evidences the v1.1 obligations only.** v1.2 obligations (the C-MEM-10 operator review gate on cross-family-captured candidates, and the durable risk-flag carrier that records WHY a proposal was held for review): **PENDING — U-MEM-27**. | `tools/memory_closeout_check.py`, `just memory-closeout-check`, and closeout review evidence below. |
| R-MEM-15 - Migration and compatibility | Callback-backed migration supports dry-run reports and explicit `migrate` events without silent canonical writes. | Migration compatibility tests from U-MEM-23 and provider-free local gate evidence. |

## C-MEM Closeout Matrix

| Contract | Closeout evidence | Verification evidence |
| --- | --- | --- |
| C-MEM-01 - Memory plane boundary | Memory store, access-mode, policy, retrieval, and runtime projection boundaries stay separated. | Matrix rows for schema validation, cross-scope denial, prompt fallback, standard tools, and native adapter. |
| C-MEM-02 - Canonical path registry | Path registry rejects traversal and scopes memory paths. | `path_traversal_rejection` selectors. |
| C-MEM-03 - Common record identity | Record envelopes carry stable identity, scope, provenance, timestamps, and hashes. **v1.1 obligations CERTIFIED at U-MEM-26 (2026-07-28).** The `provider_family` value domain is enforced at every scope-AUTHORING durable write - automatic capture, the promotion record write (canonicalized AHEAD of `_risk_flags` and `_candidate_id`, with `_persist_decision` REFUSING an un-canonicalized candidate rather than repairing it), the tool-executor promotion under a statically-supplied context, the compaction-decision write, and the native-adapter tool-event write - through the `ScopeFamilyCanonicalizer` seam declared in `harness-is/src/harness_is/memory_scope_value_domain.py` and bound once at `harness-runtime/src/harness_runtime/memory_scope_family.py` to the fail-closed `provider_family_for_scope_check` authority (never the `LOCAL_OPEN_WEIGHT`-defaulting cost-attribution one). A registered provider key is canonicalized; an out-of-domain identifier is denied. Surface (f), the redaction/tombstone transition of an already-persisted record, is the deliberate exemption. Asymmetric `null` semantics are documented and enforced: a `null`-family record is reachable by a family-scoped request, a family-scoped record is not reachable by a `null`-family request. Forward-only residual stands - pre-repair raw-key records are not rewritten and stay unreachable under family-scoped requests. **Evidences the v1.1 obligations only.** v1.2 obligations (the NEW tri-state `MemoryRecordEnvelope.captured_cross_family` field: its derivation rule, its `unknown` semantics and read-side fail-closed mapping, its hash-inertness, and its forward-only consequence): **PENDING — U-MEM-27**. | `schema_validation` selectors, plus `harness-is/tests/test_memory_scope_value_domain.py` (value-domain + crafted-bypass negatives at both read layers, incl. the unregistered-key case the out-of-domain denial alone closes) and `harness-runtime/tests/test_u_mem_26_write_boundary.py` (per-surface canonicalize/deny witnesses, the two surface-(b) ordering witnesses - same `candidate_id` for key-vs-value-equivalent hints, no false `CROSS_SCOPE` on a registered same-family alias - and the native-adapter denial leaving both store and operation ledger untouched). |
| C-MEM-04 - Episodic records | Episodic capture records preserve source and scope before promotion. | Record-envelope and operation-ledger selectors. |
| C-MEM-05 - Semantic records | Semantic records are promotion-gated and retrieval-ranked. | Promotion policy, memory-poisoning, retrieval, and retrieval-index selectors. |
| C-MEM-06 - Preference records | Preference promotion is explicit and policy-reviewed. | Promotion policy selectors. |
| C-MEM-07 - Procedural snapshots | Procedural snapshots remain typed records with scoped durability. | Schema validation and engine-class durability selectors. |
| C-MEM-08 - Memory operation ledger | Memory mutations append ledger entries with hash-chain continuity. | `append_only_ledger_hash_chain` and `concurrent_writer_no_fork` selectors. |
| C-MEM-09 - Memory policy | Policy governs capture, promotion, retrieval, access modes, and cross-scope denial. | Policy schema, cross-scope denial, and access-mode selectors. |
| C-MEM-10 - Promotion pipeline | Candidate extraction and review bind promotion before injection. **Evidences the v1.1 obligations only.** v1.2 obligations (the cross-family-captured condition, the `cross_family_capture` risk-flag vocabulary addition, and the gate making it non-inert - review-required, never auto-promotable, under every policy configuration): **PENDING — U-MEM-27**. | `promotion_policy` and `memory_poisoning` selectors. |
| C-MEM-11 - Retrieval and ranking | Retrieval output is deterministic under fixed inputs and excludes disallowed records. | `retrieval_determinism` and `cross_scope_cross_tenant_denial` selectors. |
| C-MEM-12 - Memory packet assembly | Prompt packets are assembled from filtered records and provider-neutral context carriers. | `prompt_packet_fallback`, `memory_poisoning`, and redaction selectors. |
| C-MEM-13 - Provider memory access modes | Native memory, standard tools, prompt packet, and no-access mode are typed scenarios. **v1.1 obligations CERTIFIED at U-MEM-26 (2026-07-28).** When `standard_memory_tools` has been selected and the dispatched candidate's provider family differs from `MemoryScope.provider_family`, neither the tool schemas nor the scope reference are exposed; the withholding is recorded on the C-MEM-19 telemetry surface with the named denial reason `provider_family_scope_mismatch` (span-shaped, no new C-MEM-08 operation kind), the dispatch still completes, and harness-authored capture is unaffected. **Two defect-pinning tests were INVERTED rather than deleted** - each had encoded the pre-fix disclosure as the expected behaviour: the B-83-era `test_b83_cross_family_recomposed_context_is_reported_but_never_rendered` required the tools to be ARMED cross-family so the daemon could refuse them (now `test_u_mem_26_cross_family_ollama_dispatch_withholds_tools_and_packet`), and the r300 production-path integration test asserted the five C-MEM-14 wire names DO reach the cross-family openai leg. The withholding therefore fires on the canonical `api.run` cross-family fallback path, not only at the unit boundary; the inverted r300 assertion's wire-name / HTTP-400 coverage is preserved on the same-family paths that still inject. | `ACCESS_MODE_VERIFICATION_SCENARIOS`, plus `test_u_mem_26_cross_family_ollama_dispatch_withholds_tools_and_packet`, `test_u_mem_26_cross_family_openai_dispatch_withholds_tools_and_packet`, and `test_u_mem_26_same_family_dispatch_exposure_is_unchanged` in `harness-runtime/tests/test_lifecycle_llm_dispatch.py`; `test_u_mem_26_capture_is_unaffected_by_the_cross_family_withholding` in `harness-runtime/tests/test_automatic_memory_runtime.py`; and `test_r300_deterministic_cross_family_fallback_through_production_path` in `harness-runtime/tests/integration/test_r300_cross_family_fallback_e2e.py`. |
| C-MEM-14 - Provider-neutral memory tools | Standard memory tools expose controlled read/list/write behavior on tool-capable paths. **v1.1 obligations CERTIFIED at U-MEM-26 (2026-07-28).** Exposure is now QUALIFIED, not unconditional: the schemas and the bound `scope_ref` are emitted only when the dispatched candidate's family matches the packet scope's family, so a tool call can no longer `memory.search` across - or `memory.write_note` into - a partition belonging to another provider family. The qualification is one conjunct on the SHARED authority (`_packet_scope_matches_dispatch_family`), deliberately not a second cross-family test, because a divergent predicate would route the withheld dispatch into the `arm_unservable` repair branch and serve the same scope as prompt text. The tool executor's own by-reference readers are bound independently (resolved per call site, not once at `execute`), so neither the index-entry nor the record-by-ref lookup is reachable under a crafted raw-key `context.scope`. | `standard_memory_tools` selectors, plus the exposure/withhold pair in `harness-runtime/tests/test_lifecycle_llm_dispatch.py`, and `test_executor_by_reference_readers_deny_a_crafted_raw_key_context` / `test_executor_by_reference_readers_serve_a_canonical_record` / `test_write_note_lands_the_context_record_scope_not_a_provider_derived_one` in `harness-runtime/tests/test_u_mem_26_write_boundary.py`. |
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

**Version scoping — window 1 (v1.1) CLOSED (opened 2026-07-28 at the `B-86` spec
leg; closed 2026-07-28 at the U-MEM-26 impl leg).** This packet certifies the
memory substrate at spec **v1.1** and plan **v1.1** (U-MEM-01..26). The paragraph
is retained as the historical record of the window, not as a live scoping caveat.
A **second** window (v1.2 / U-MEM-27) opened 2026-07-29 and is still OPEN — stated
separately below, because this packet now carries one closed and one live scoping.

For the window between the two legs, this packet certified spec **v1** / plan
**v1** (U-MEM-01..25) only, and six rows carried an explicit `PENDING — U-MEM-26`
marker across two matrices:

- **C-MEM matrix** — `Spec_Memory_Substrate_v1.md` v1.1 grew the obligations of
  C-MEM-03, C-MEM-13, and C-MEM-14.
- **R-MEM matrix** — `Implementation_Plan_Memory_Substrate_v1.md` v1.1 maps the
  new U-MEM-26 unit into R-MEM-01, R-MEM-09, and R-MEM-12, so those three
  requirement rows were likewise certified only to their v1 obligations.

The binary checker could not see either scoping: it derives both id sets from
headings (`### R-MEM-NN` in the PRD, `## C-MEM-NN` in the spec) and tests only
that every derived id has an evidence row. Neither id set changed at v1.1, so
the gate correctly reported `ready: yes` throughout for the property it actually
tests — the `PENDING` markers, not the checker, were what carried the scoping.
Making the gate red for the interim window was considered and declined on
main-always-green CI grounds; the rationale is recorded at the plan v1.1
change-note. **That residual is now moot:** U-MEM-26 landed, all six rows are
re-opened and extended above, no matrix row carries a `PENDING — U-MEM-26` marker, and the check was
re-run green with the refreshed rows in place — the plan's own closure condition
for the unit (the closeout-refresh acceptance item and the closeout re-run
verification line of `Implementation_Plan_Memory_Substrate_v1.md` U-MEM-26 — cited by
unit id and subsection rather than by line, since the plan v1.2 delta shifted the
`:901` / `:924` anchors this paragraph originally carried). The impl-leg record is
at `.harness/u-mem-26-impl-leg-close-2026-07-28.md`.

**Version scoping — window 2 (v1.2) OPEN (opened 2026-07-29 at the `B-92` spec
leg).** `Spec_Memory_Substrate_v1.md` v1.2 and
`Implementation_Plan_Memory_Substrate_v1.md` v1.2 landed the RATIFIED `B-92`
resolution (C-MEM-10 reading B — flag plus gate — and the C-MEM-03 tri-state
`captured_cross_family` field). Those obligations are **not** certified here, and
six rows carry an explicit `PENDING — U-MEM-27` marker across both matrices:

- **C-MEM matrix** — v1.2 grew the obligations of C-MEM-03 (the new tri-state
  provenance field) and C-MEM-10 (the cross-family-captured condition, the flag
  vocabulary addition, and the gate).
- **R-MEM matrix** — plan v1.2 maps the new U-MEM-27 unit into R-MEM-01, R-MEM-05,
  R-MEM-09, and R-MEM-14, so those four requirement rows are likewise certified
  only to their v1.1 obligations. (R-MEM-12 is deliberately NOT annotated: the plan v1.2
  change-note records that it is not extended, because the new field is provenance
  rather than partition and U-MEM-27 adds no scope-enforcement obligation.)

The binary checker cannot see this scoping either, for the identical reason: v1.2
adds no `## C-MEM-NN` heading and no `### R-MEM-NN` heading, so neither derived id
set changes and the gate correctly still reports `ready: yes` for the property it
actually tests. The `PENDING — U-MEM-27` markers, not the checker, carry this
scoping. Reddening the gate for the window is declined again on the same
main-always-green CI grounds recorded at the plan v1.1 change-note and re-affirmed
at the plan v1.2 change-note. U-MEM-27 cannot close until all five rows are
re-opened and extended, this paragraph is closed the way window 1 was, and the
check is re-run green — the unit's own acceptance and verification items say so.

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
`construct_gemini_cli_adapter`, skipping with a redacted reason (the probe's
own output is kept out of test logs) when that probe does not confirm a
session — and failing rather than skipping when the declared `auth_args` is
emptied or the CLI rejects the probe argv itself. The generic-command gate skips when
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
| `live-gemini-legacy-cli-auth` | NOT CONFIRMED - upstream tier ineligibility (2026-07-27) | The 2026-07-03 "not installed" reason is false at HEAD: `gemini` v0.49.0 is installed at `~/.local/share/mise/installs/node/24/bin/gemini`, with a logged-in OAuth session at `~/.gemini/oauth_creds.json`. v0.49.0 ships no auth/status subcommand, so the only available probe is an outward model call; that probe is now DECLARED at `PROVIDER_PRESETS["gemini"].auth_args` as `--skip-trust -p "Reply with the single word OK."` (the preset keeps `auth_check=False`, so constructing a Gemini adapter never fires it implicitly). Fired live under operator standing approval: exit 1 with `IneligibleTierError: This client is no longer supported for Gemini Code Assist for individuals.` (upstream `UNSUPPORTED_CLIENT` on `free-tier`), so the gate stays NOT CONFIRMED - the legacy client is deprecated upstream for individual accounts and superseded by the Antigravity (`agy`) route, whose own gate is CONFIRMED above. `test_u_mem_24_live_cli_routes.py -m e2e -k gemini_legacy` is no longer an unconditional skip stub: it now sources both the executable and the probe argv from the preset, drives the production `construct_gemini_cli_adapter` auth path, and skips with a redacted reason (the probe's stdout/stderr is kept out of test logs per the module's no-secret-output guarantee; the verbatim refusal recorded here came from firing the declared probe manually). Negative control: the same constructor with `auth_args` cleared raises `ExternalCLINotAuthenticatedError("Gemini CLI auth_check=true requires auth_args")`, a distinct reason from the tier rejection; the live test additionally FAILS (not skips) if the preset's `auth_args` declaration is ever emptied, or if the CLI rejects the declared probe argv itself (recognized argv-rot markers, checked internally so output stays redacted), so a gutted or rotted standing probe cannot go silently green. |
| `live-generic-command-cli-auth` | PASS (2026-07-27) | `U_MEM_24_GENERIC_COMMAND_AUTH_PROBE="ollama list" pytest harness-runtime/tests/integration/test_u_mem_24_live_cli_routes.py -m e2e -k generic_command` passed and bound `generic-command:custom`. The test drives the production `construct_generic_command_cli_adapter` auth path (config built from the parsed probe: `command=argv[0]`, `auth_args=tuple(argv[1:])`, `auth_check=True`) rather than a bare subprocess, so a regression in the shipped constructor or auth-arg handling cannot yield a false PASS. Live evidence: `ollama` 0.18.3 at `/usr/local/bin/ollama`; the daemon was already up via Ollama.app and was left running, so no environment state was changed or needed restoring; the probe `ollama list` exits 0. Second negative control: with the probe set to `ollama --definitely-not-a-flag` the same production path raises `ExternalCLINotAuthenticatedError(... unknown flag: --definitely-not-a-flag)` and the test FAILS rather than skipping - a declared-but-failing probe is a failure by design. `ollama list` is now the STANDING operator-ratified declaration (operator standing approval 2026-07-27), embedded in the gate's `resume_command` at `memory_verification_suite.py`; no default is baked into the environment variable itself, so the deterministic-absence negative control still holds - with `U_MEM_24_GENERIC_COMMAND_AUTH_PROBE` unset the test skips rather than passing vacuously. |
