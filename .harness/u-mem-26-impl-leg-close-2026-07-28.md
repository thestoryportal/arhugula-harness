# U-MEM-26 impl leg — close record (2026-07-28)

The implementation leg of `B-86`'s ratified `Spec_Memory_Substrate_v1.md` v1.1 contracts.
Branch `u-mem-26-impl`. This is the record the U-MEM-25 closeout evidence packet and future
sessions cite; it carries what the commit messages and the register rows do not.

## Slices

| Slice | Commit | Content |
| --- | --- | --- |
| 1 | `b592c043` + `8ddf7d82` | `harness-is` read boundary — C-MEM-03 scope asymmetry, request-side value domain (`memory_scope_value_domain.py`), 19 witnesses. |
| 2 | `76c0e879` + `ce5d6e3c` | `B-89` writer repair + `B-90` fold-in, write-boundary at every scope-AUTHORING surface, `memory_scope_family.py` composition root, 20 witnesses. |
| 3 | `8624af53` | C-MEM-13 cross-family withhold guard + production-wired witnesses; two defect-pinning tests inverted. |
| 4 | this commit | Closeout-evidence refresh (six rows), `B-86`/`B-89`/`B-90` register close-outs, this note. |

## By-rule inventory additions found during impl

The plan's own implementation note (`Implementation_Plan_Memory_Substrate_v1.md:928`) warns
that the enumerated reader/writer inventory is **review-time, not proven complete**. Re-grounding
at impl HEAD found two surfaces the enumeration missed — worth recording, because the under-count
is the point:

- **(b2), a second candidate-identity origination site.** Surface (b) was enumerated as *the*
  promotion path, `_candidate_from_hint` (`memory_promotion.py`). Grepping every
  `PromotionCandidate(` construction found a second one at `memory_tool_executor.py:417`, which
  never traverses the hint path — so a canonicalization placed only at `_candidate_from_hint`
  is bypassable. Resolved by `_require_canonical_candidate_scope`, a write-side backstop at
  `_persist_decision` that **REFUSES** an un-canonicalized candidate rather than repairing it:
  repairing there would fix the persisted scope while leaving `candidate_id` and `risk_flags`
  derived from the raw identifier — exactly the split the ordering rule exists to prevent.
- **The r300 integration surface, found by suite-run rather than by enumeration.** No reader/writer
  grep would have surfaced `test_r300_deterministic_cross_family_fallback_through_production_path`:
  it is a *test* that pinned the defect, asserting the five C-MEM-14 wire names DO reach the
  cross-family openai leg. It surfaced only when the full suite was run against the slice-3 guard.
  Inverted in place with contract cites; its wire-name / HTTP-400 coverage is preserved on the
  same-family paths that still inject. **Lesson: an inventory grep finds production carriers, not
  tests that encode the defect as expected behaviour — only a suite run does.**

## Load-flake identities verified

The slice-4 full-suite run at slice-3 HEAD: **6966 passed / 31 skipped / 8 failed** in 469s. All 8
failures are live-Ollama e2e integration nodes that pass in isolation and fail under full-suite
load (contention against a local `llama3.2:3b`), verified by a positive control —
`test_r300_live_ollama_provider_fallback_exercise` passed standalone in 31.8s, having failed in the
same run. The identities, across four modules:

- `integration/test_r300_cross_family_fallback_e2e.py` — `test_r300_live_ollama_provider_fallback_exercise`,
  `test_r_pm_1_active_prompt_injection_honored_by_live_ollama`, `test_r_pm_1_workload_selection_drives_live_ollama_injection`
- `integration/test_r_cl_p3_live_multi_tier_e2e.py::test_r_cl_p3_live_multi_tier_api_run` — all three persona-tier params
- `integration/test_u_cp_89_hierarchical_delegation_live_e2e.py::test_u_cp_89_hierarchical_delegation_depth2_live_ollama`
- `integration/test_u_cp_90_decentralized_handoff_live_e2e.py::test_u_cp_90_decentralized_handoff_three_stage_live_ollama`

None touches memory-substrate code; the provider-free suite is green. *(The slice-3 handoff named
three such identities; the slice-4 run surfaced the six functions / eight nodes above. Recorded as
observed rather than reconciled to the handoff count.)*

## Forward residuals

- **C-MEM-10 promotion eligibility is now materially reachable.** The spec v1.1 change-note carries
  "promotion eligibility of records captured during a cross-family fallback leg" as a named open
  question, and the plan puts it out of scope (`:933`). It is no longer hypothetical: capture now
  writes under the run's **composed** scope, so a cross-family fallback leg lands an
  `anthropic`-family record while the dispatch that produced it ran on `openai`. Witness:
  `test_u_mem_26_capture_is_unaffected_by_the_cross_family_withholding`
  (`harness-runtime/tests/test_automatic_memory_runtime.py`), which asserts exactly that
  `captured.envelope.scope.provider_family == ProviderFamily.ANTHROPIC.value` on an openai leg.
  Whether such a record may be **promoted** — and injected back under the primary's family — is
  the open C-MEM-10 question, now with a concrete carrier.
- **The R5-path family conjunct is inert by construction.** With the withhold guard upstream, a
  cross-family dispatch never reaches `_degraded_serve_for_unservable_arm`, so that path's own
  family conjunct can no longer fire. It is retained as defence in depth with its comment corrected
  to say so rather than claiming it is live. Any future change that makes the R5 path reachable
  cross-family must re-verify it.
- **`_request_hash` is computed pre-canonicalization.** `MemoryRetriever.retrieve`
  (`harness-is/src/harness_is/memory_retrieval.py:222`) hashes the **raw** request, then
  canonicalizes at `:227`. Two key-vs-value-equivalent requests that resolve to the same family
  therefore carry **different** `request_hash` values while returning identical results. Not a
  correctness defect — the hash is a determinism/provenance token, not an identity key, and no
  contract requires equivalence — but it is the retrieval-side mirror of the surface-(b) ordering
  rule the write path *does* enforce. Registered here as an observation, not a fork.

## Codex R1 dispositions (2026-07-28)

- **ACCEPTED [P2] — compaction canonicalized only the envelope, not the persisted content.** `complete_compaction` canonicalized the selected `event_scope` while `_disposition_content` persisted every `candidate.suggested_scope` verbatim, so an `ollama` candidate produced an envelope scoped `local_open_weight` over content carrying `provider_family: ollama` (with the content hash, hence the derived `memory_id`, taken over the raw value) and any candidate past the first faced no value-domain check at all. Fixed by canonicalizing-or-denying EVERY candidate scope at the top of `complete_compaction` (`_canonical_candidates`, rebuilding via `model_copy`) ahead of `_scope_from_candidates` / `_disposition_content` / hashing — the same pre-derivation posture slice 2 gave promotion, same registered→canonicalize / out-of-domain→deny split, same `CompactionScopeValueDomainError`. Witnesses: `test_compaction_canonicalizes_the_persisted_candidate_content` (asserts on the parsed CONTENT plus envelope/content-hash agreement) and `test_compaction_denies_an_out_of_domain_candidate_past_the_first` (deny + nothing written, against a positive control); both fail under a revert-the-content-side mutation probe.
- **DECLINED [P1] — "composition-time inject row vs dispatch-time withholding" audit nuance.** This is not an impl defect: the reading was RATIFIED at the spec leg. `Spec_Memory_Substrate_v1.md` C-MEM-13's recording-surface paragraph holds that the existing inject entry satisfies the must-ledger obligation and that the honest per-dispatch report is the C-MEM-19 span; the plan acceptance at `:890` encodes exactly that, and the slice-3 witness carries the comment recording it. Re-opening it is a spec question routed through back-flow, not something to absorb at the impl leg.

## Codex R2 dispositions (2026-07-28)

- **ACCEPTED [P2-a] — the supplied `record_scope` bypassed the write-boundary value domain.** `memory_capture._scope_for_record` returned `self._record_scope` VERBATIM whenever one was supplied, so only the residual construction was bound by the C-MEM-03 value domain; a caller handing in a registered provider KEY (`provider_family="ollama"`) persisted that key into the record, and an out-of-domain identifier persisted too — the exact raw-key partition the residual path was hardened against, reachable through the other branch. Fixed by collapsing both branches onto ONE canonicalize-or-deny: the supplied scope (or, absent one, the residual construction) is run through `resolve_scope_family`, a registered key becomes its `ProviderFamily` value via `model_copy` (so `tenant` / `workload_class` survive), and an out-of-domain value raises `MemoryCaptureScopeValueDomainError` before any write. No-op on the composed production path, which already supplies a canonical scope. Witnesses: `test_supplied_record_scope_with_a_raw_key_is_canonicalized_before_it_persists` (reads the PERSISTED record back and asserts the family value plus surviving `tenant`) and `test_supplied_record_scope_out_of_domain_is_refused_and_writes_nothing` (raises, zero C-MEM-08 rows, no episodic directory); both fail under a revert-to-verbatim-return mutation probe.
- **ACCEPTED [P2-b] — the withhold predicate compared the SCOPE side raw.** `_packet_scope_matches_dispatch_family` canonicalized only the provider side (`provider_family_for_scope_check(provider_name).value`) and compared `scope.provider_family` as the literal string it arrived as. `MemoryScope.provider_family` is a plain `str` and a statically-injected `RuntimeMemoryContext` never runs `compose_for_dispatch`, so an operator-authored context declaring `provider_family="ollama"` on an ollama dispatch compared `"ollama"` against `"local_open_weight"`, reported a CROSS-family mismatch, and withheld BOTH the tool schemas and the packet on a plainly same-family dispatch — via the shared predicate, so the guard, `_degraded_serve_disposition` and the B-83 packet path all inherited the false negative. Fixed INSIDE the shared predicate by canonicalizing the scope side through `memory_scope_family.canonical_scope_family` (the same fail-closed authority), with the B-86(3) sentinel semantics MIRRORED: a `None` canonicalization is "family UNKNOWN" and never compares equal to anything, so an out-of-domain scope value stays report-only. Docstring updated. Witnesses: `test_r2_p2b_raw_provider_key_scope_serves_on_a_same_family_dispatch` (tools armed, no degraded span), `test_r2_p2b_raw_provider_key_scope_still_withholds_across_families` (`codex` → OPENAI family on an ollama dispatch still withheld with `provider_family_scope_mismatch`), `test_r2_p2b_out_of_domain_scope_value_stays_report_only`; the existing `test_b86_unregistered_provider_key_fails_closed_against_local_scope` (the provider-side half) still passes unchanged. Mutation probe: reverting the scope-side canonicalization fails witness 1 while 2/3 and the B-86 witness stay green — exactly the isolation claimed.
