# 7c Cross-Axis Composition Audit — CP-consumer buckets (CP→IS, CP→AS)

**Scope:** Bucket 2 (CP→IS, 36 edges) + Bucket 3 (CP→AS, 24 edges) = 60 declared typed cross-axis edges.
**Task:** Read-only classification — genuine-typed-seam vs convention-level vs phase-2-runtime vs spurious.
**Filed:** 2026-05-17, Phase 7 sub-phase 7c, pre-wiring audit. Feeds canonical CXA v2.3 revision.

---

## Method notes

- **Edge enumeration authority:** CXA v2.2 §2.3.2/§2.3.3 (preserved verbatim from CXA v2.1; identical to CP plan v2 §3.6). 36+24 edges = the multi-target cells expanded one edge per (CP unit × IS/AS target) pair.
- **Unit-ID drift check:** none. CXA cites CP plan v1 framing; the v2.10 code docstrings carry the *same* `U-CP-NN` IDs (e.g. `routing_manifest_residence.py` = U-CP-04, `per_step_override_evaluator.py` = U-CP-14). Map confirmed via docstring headers.
- **Genuine-seam ceiling:** `grep -rn "from harness_is\|from harness_as" harness-cp/src/` returns exactly **11 CP files** with a real cross-axis import. Everything else is at best "could import" — and per the AS→IS precedent, "could import" usually means the consumer re-applies a scheme, returns a composed payload, or uses an axis-local type.
- **Taxonomy applied (AS→IS precedent, `class_1_tension_cxa_as_is_untyped_edges.md`):**
  - genuine-typed-seam — consumer imports a Pydantic v2 type / enum / function from `harness_is`/`harness_as`.
  - convention-level — re-applied scheme/algorithm, free-text `str` descriptor, or axis-local type stand-in.
  - phase-2-runtime — relationship is a runtime ledger write/append/emit, not a compile-time type link.
  - spurious — CXA declares the edge but the consumer unit does not reference the producer axis at all.

### CP files that genuinely import a producer axis (the seam ceiling)

| CP file | Unit | Imports |
|---|---|---|
| `routing_manifest_residence.py` | U-CP-04 | `harness_is.path_class_registry.PathClass`, `harness_is.path_resolver.PathResolver`, `harness_as.SandboxTier` |
| `concurrent_prompt_cache_warmup.py` | U-CP-33 | `harness_is.path_class_registry.PathClass`, `harness_is.path_resolver.PathResolver` |
| `handoff_context.py` | U-CP-30 | `harness_is.state_ledger_entry_schema.Identifier` |
| `hitl_timeout_degradation.py` | U-CP-52 | `harness_is.state_ledger_entry_schema.Identifier` |
| `sibling_ledger_entry_composition.py` | U-CP-34 | `harness_is` `JsonlLedgerHandle`, `StateLedgerEntry`, `Identifier`, `append_ledger_entry` |
| `parent_fanout_close_entry.py` | U-CP-35 | `harness_is.state_ledger_read.LedgerNavigationPrimitive` |
| `per_step_override_evaluator.py` | U-CP-14 | `harness_as.GateLevel` |
| `f5_signing_key_resolution.py` | U-CP-44 | `harness_as` `SandboxTier`, `SecretRef`, `SecretScope`, `fetch_secret` |
| `both_by_tier_overlay.py` | U-CP-41 | `harness_as.sandbox_tier.BlastRadiusTier` |
| `five_axis_composition.py` | U-CP-45 | `harness_as` `BlastRadiusTier`, `SandboxTier` |
| `gate_level_rule.py` | U-CP-43 | `harness_as.BlastRadiusTier` |
| `default_downgrade_rule.py` | U-CP-26 | `harness_as.BlastRadiusTier` |
| `sub_agent_gate_level_descent.py` | U-CP-27 | `harness_as` `GateLevel`, `BlastRadiusTier`, `SandboxTier` |

(13 files; `per_step_override_evaluator` U-CP-14 is CP→AS not CP→IS. `both_by_tier_overlay` U-CP-41 is not a CXA-declared edge source.)

---

## Bucket 2 — CP → IS (36 edges)

| # | CP consumer unit | IS producer target | Contract anchor | Classification | Evidence |
|---|---|---|---|---|---|
| 1 | U-CP-04 | U-IS-01 (filesystem path contract) | path-class registry | genuine-typed-seam | `routing_manifest_residence.py:45` `from harness_is.path_class_registry import PathClass`; `:177` `PathClass.PROMPTS` consumed. |
| 2 | U-CP-04 | U-IS-02 (path resolver) | path resolver | genuine-typed-seam | `routing_manifest_residence.py:46` `from harness_is.path_resolver import PathResolver`; `:172` "Delegates to the U-IS-02 `PathResolver`". |
| 3 | U-CP-04 | U-IS-06 (per-deployment storage residence) | storage residence | convention-level | No `harness_is` import for residence; deployment residence resolved via `harness_core.DeploymentSurface`/`WorkloadClass` (`:44`) — no U-IS-06 type consumed. |
| 4 | U-CP-12 | U-IS-07 (F2 state-ledger entry shape) | C-IS-10 §10.1 | phase-2-runtime | `per_class_attribute_composition.py` imports only `harness_core`/`harness_cp`; `workflow.checkpoint` is a span-name string (`:117`). No `StateLedgerEntry` import — checkpoint composition is a runtime emission concern. |
| 5 | U-CP-14 | U-IS-07 (F2 entry shape) | C-IS-10 §10.1 | phase-2-runtime | `per_step_override_evaluator.py:58` docstring: "composes against the IS-exported `StateLedgerEntry` shape via the CP→IS edges" — but no `harness_is` import; only `harness_as.GateLevel` (`:37`). Compose-then-return; F2 delegation is runtime. |
| 6 | U-CP-14 | U-IS-08 (canonicalize/hash) | C-IS-10 §10.3 | phase-2-runtime | `per_step_override_evaluator.py:194` "F2 canonicalize+hash is delegated to U-IS-08" — delegation described in prose; no import. Runtime hash call. |
| 7 | U-CP-14 | U-IS-09 (chain construction) | C-IS-10 §10.3 | phase-2-runtime | `per_step_override_evaluator.py:195` "chain construction to U-IS-09"; prose-only delegation, no import. |
| 8 | U-CP-14 | U-IS-11 (append) | C-IS-10 §10.5 | phase-2-runtime | `per_step_override_evaluator.py:196` "append to U-IS-11"; runtime ledger append, no import. |
| 9 | U-CP-18 | U-IS-07 (F2 read/write substrate) | C-IS-10 §10.1 | convention-level | `f2_substrate_join_discipline.py:65` `read_contract: str` — F2 read/write surfaces are free-text `str` descriptors; `:14-19` docstring: "do NOT re-implement them … cross-axis edges U-IS-07/09/12". No import. Descriptor stand-in. |
| 10 | U-CP-18 | U-IS-09 (chain construction) | C-IS-10 §10.3 | convention-level | Same file; `chain_construction` is a `str` descriptor field, not a U-IS-09 type. |
| 11 | U-CP-18 | U-IS-12 (idempotency-key join / bounded-read) | C-IS-10 §10.2 | convention-level | Same file; `write_contract`/bounded-read expressed as `str` descriptors. No `harness_is` import. |
| 12 | U-CP-27 | U-IS-07 (F2 audit composition) | C-IS-10 §10.1 | phase-2-runtime | `sub_agent_gate_level_descent.py` imports `harness_as` only (`:37-38`); `:191` docstring "canonicalize+hash delegates to U-IS-08, chain construction to U-IS-09, append to U-IS-11" — prose delegation. Audit entry composed then appended at runtime. |
| 13 | U-CP-27 | U-IS-09 (chain construction) | C-IS-10 §10.3 | phase-2-runtime | Same file `:191`; prose delegation, no import. |
| 14 | U-CP-27 | U-IS-11 (append) | C-IS-10 §10.5 | phase-2-runtime | Same file `:120` "once `emit_sub_agent_dispatch_audit` has appended the §12.5 audit"; runtime append. |
| 15 | U-CP-30 | U-IS-07 (F2 entry shape) | C-IS-10 §10.1 | phase-2-runtime | `handoff_context.py` imports `Identifier` only (see #16); HandoffContext does not subclass/import `StateLedgerEntry`. Entry-shape composition is runtime. |
| 16 | U-CP-30 | U-IS-12 (idempotency-key join) | C-IS-10 §10.2 | genuine-typed-seam | `handoff_context.py:36` `from harness_is.state_ledger_entry_schema import Identifier`; `:186` `idempotency_key: Identifier`. Real type import on the idempotency-key join. |
| 17 | U-CP-33 | U-IS-01 (filesystem path contract) | path-class registry | genuine-typed-seam | `concurrent_prompt_cache_warmup.py:39` `from harness_is.path_class_registry import PathClass`; `:115` `PathClass.PROMPTS`. |
| 18 | U-CP-33 | U-IS-02 (path resolver) | path resolver | genuine-typed-seam | `concurrent_prompt_cache_warmup.py:40` `from harness_is.path_resolver import PathResolver`; `:109` "`PathResolver` against the U-IS-01 `PathClass`". |
| 19 | U-CP-34 | U-IS-07 (F2 entry shape) | C-IS-10 §10.1 | genuine-typed-seam | `sibling_ledger_entry_composition.py:34-39` `from harness_is.state_ledger_entry_schema import … StateLedgerEntry`; `:51` `class SiblingLedgerEntry(StateLedgerEntry)` — subclasses the IS-exported F2 entry. |
| 20 | U-CP-34 | U-IS-08 (canonicalize/hash) | C-IS-10 §10.3 | phase-2-runtime | Same file; `:159-162` "canonicalize/hash (U-IS-08) happen inside that" `append_ledger_entry` call — runtime, inside the appended function; no U-IS-08 symbol imported. |
| 21 | U-CP-34 | U-IS-09 (chain construction) | C-IS-10 §10.3 | phase-2-runtime | Same file `:159-162` "chain construction (U-IS-09) … inside that" — runtime; no U-IS-09 import. |
| 22 | U-CP-34 | U-IS-11 (append) | C-IS-10 §10.5 | genuine-typed-seam | `sibling_ledger_entry_composition.py:40-44` `from harness_is.state_ledger_write import … append_ledger_entry`; `:162` `return append_ledger_entry(...)`. Real function import. |
| 23 | U-CP-35 | U-IS-07 (F2 entry shape) | C-IS-10 §10.1 | convention-level | `parent_fanout_close_entry.py:1-4` docstring: "separate primitive — NOT an F2 entry". Merkle-root is over the sibling chains but the unit declares `MerkleRoot` as its own record; no `StateLedgerEntry` import. |
| 24 | U-CP-35 | U-IS-12 (bounded-read) | C-IS-10 §10.2 | genuine-typed-seam | `parent_fanout_close_entry.py:35` `from harness_is.state_ledger_read import LedgerNavigationPrimitive`; `:20` "read-side merkle construction uses U-IS-12's bounded-read primitive". Real type import. |
| 25 | U-CP-37 | U-IS-07 (F2 entry shape) | C-IS-10 §10.1 | phase-2-runtime | `hitl_response_palette.py:12-15` "declares only the audit-entry *shape*, not the chaining mechanism"; imports `harness_core` only — no `harness_is`. Per-response audit entry composed at runtime. |
| 26 | U-CP-37 | U-IS-09 (chain construction) | C-IS-10 §10.3 | phase-2-runtime | Same file `:13-14` "chain-link construction itself delegates to U-IS-09 (cross-axis IS)" — prose delegation, no import. |
| 27 | U-CP-42 | U-IS-07 (F2 cryptographic shape) | C-IS-10 §10.1 | convention-level | `per_persona_tier_audit_cryptographic_shape.py` imports `harness_core` only; `:14` "append-only (no chain) -> hash-chained -> hash-chained + signature" — re-applies the C-IS-06 crypto-shape *scheme* per tier; `:38` `APPEND_ONLY_SQLITE` is an axis-local `StrEnum`. Scheme-inheritance, no IS type. |
| 28 | U-CP-42 | U-IS-08 (canonicalize/hash) | C-IS-10 §10.3 | convention-level | Same file; crypto shape re-described per tier as a scheme, not a U-IS-08 import. |
| 29 | U-CP-42 | U-IS-09 (chain construction) | C-IS-10 §10.3 | convention-level | Same file; "hash-chained" is a tier-attribute value, not a U-IS-09 type consumption. |
| 30 | U-CP-42 | U-IS-11 (append) | C-IS-10 §10.5 | convention-level | Same file; append-discipline named in the scheme; no `append_ledger_entry` import. |
| 31 | U-CP-49 | U-IS-11 (append) | C-IS-10 §10.5 | phase-2-runtime | `pause_resume_protocol.py:114-122` "the concrete F2 append … capture_pause_snapshot composes the U-IS-11 F2 append"; imports `harness_core`/`harness_cp` only — runtime append, no import. |
| 32 | U-CP-49 | U-IS-12 (bounded-read) | C-IS-10 §10.2 | convention-level | Same file; resume-side bounded-read named in prose; no `harness_is` type imported. |
| 33 | U-CP-50 | U-IS-01 (filesystem path) | path-class registry | spurious | `material_diff_detection.py` imports `harness_core.PersonaTier` + `harness_cp` only. No filesystem-path reference at all in the consumer unit. |
| 34 | U-CP-50 | U-IS-11 (append) | C-IS-10 §10.5 | phase-2-runtime | `material_diff_detection.py` — material-diff records composed; any ledger append is a runtime concern. No `harness_is` import. |
| 35 | U-CP-50 | U-IS-12 (bounded-read) | C-IS-10 §10.2 | convention-level | Same file; consumes `harness_cp.handoff_context.ExternalReference` (`:37`) — diff detection operates on CP-local types, not a U-IS-12 bounded-read primitive. |
| 36 | U-CP-52 | U-IS-07 (F2 entry shape) | C-IS-10 §10.1 | phase-2-runtime | `hitl_timeout_degradation.py:31` imports `Identifier` (see edge below); `:148/:183` "`sha256(canonicalize(payload))`" re-applied — timeout-degradation audit entry composed at runtime, no `StateLedgerEntry` import. |
| 36b | U-CP-52 | U-IS-11 (append) | C-IS-10 §10.5 | phase-2-runtime | Same file; append is a runtime concern. **Note:** the CXA §2.3.2 row for U-CP-52 lists 2 targets (U-IS-07, U-IS-11) — edge #36 covers U-IS-07; this row (#36b) covers U-IS-11. See count reconciliation below. |

**NEEDS-REVIEW note on U-CP-52 `Identifier` import:** `hitl_timeout_degradation.py:31` does `from harness_is.state_ledger_entry_schema import Identifier` and uses it at `:121` `idempotency_key: Identifier`. This is a genuine type import — but CXA §2.3.2 declares U-CP-52's targets as **U-IS-07 + U-IS-11**, *not* U-IS-12 (the idempotency-key join unit). The genuine `Identifier` seam at U-CP-52 maps to U-IS-12 by contract, which the CXA row does not list. Either the CXA row mis-targets (should include U-IS-12) or the `Identifier` import is incidental. Marked NEEDS-REVIEW — see "Count reconciliation" below; I classified the two declared targets (U-IS-07, U-IS-11) as phase-2-runtime and flag the unlisted genuine U-IS-12 seam separately.

### Count reconciliation (Bucket 2)

CXA §2.3.2 multi-target cells expand to: 04(3) + 12(1) + 14(4) + 18(3) + 27(3) + 30(2) + 33(2) + 34(4) + 35(2) + 37(2) + 42(4) + 49(2) + 50(3) + 52(2) + 55(1) = **38**, not 36. The document asserts 36. **The arithmetic of the verbatim v2.1 table does not sum to 36** — this is a pre-existing CXA defect independent of this audit. I enumerated all 38 target cells; U-CP-55→U-IS-12 is edge #37 and the 38th is the U-CP-52 second target. Rows above are numbered 1–36 + 36b; #37 below. **Flag for CXA v2.3: the "36 edges" header is wrong; the table holds 38 (CP-unit × IS-target) pairs.**

| # | CP consumer unit | IS producer target | Contract anchor | Classification | Evidence |
|---|---|---|---|---|---|
| 37 | U-CP-55 | U-IS-12 (idempotency-key join) | C-IS-10 §10.2 | spurious | `cp_cross_axis_composition_manifest.py` imports `harness_core.UnitId` only; `:20` "this exports references only". The manifest unit holds no idempotency-key consumption — it lists references. No `harness_is` import. |

### Bucket 2 tally (38 enumerated target cells)

| Classification | Count |
|---|---|
| genuine-typed-seam | 8 (#1, #2, #16, #17, #18, #19, #22, #24) |
| convention-level | 11 (#3, #9, #10, #11, #23, #27, #28, #29, #30, #32, #35) |
| phase-2-runtime | 17 (#4, #5, #6, #7, #8, #12, #13, #14, #15, #20, #21, #25, #26, #31, #34, #36, #36b) |
| spurious | 2 (#33, #37) |

Total: 8 + 11 + 17 + 2 = **38** enumerated (CP-unit × IS-target) cells.

---

## Bucket 3 — CP → AS (24 edges)

| # | CP consumer unit | AS producer target | Contract anchor | Classification | Evidence |
|---|---|---|---|---|---|
| 1 | U-CP-09 | U-AS-30 (adoption-depth matrix / model-tier escalation) | C-AS-13 §13.4 | convention-level | `cross_family_fallback_chain.py` imports `harness_core` + `harness_cp` only — no `harness_as`. `:16` docstring "model-tier escalation chain (U-AS-30 — `MODEL_TIER_ESCALATION_CHAIN`)"; `:91` "delegates to U-AS-30" — named in prose; `MODEL_TIER_ESCALATION_CHAIN` is an importable AS constant but is not imported. Could-import, not wired. |
| 2 | U-CP-26 | U-AS-01 (SandboxTier + BlastRadiusTier) | C-AS-12 §12.1 | genuine-typed-seam | `default_downgrade_rule.py:31` `from harness_as import BlastRadiusTier`; `:20` "U-AS-01 (`harness_as`); its 4 members are the §12.1 four-tier taxonomy". |
| 3 | U-CP-27 | U-AS-09 (sub-agent sandbox-tier ascension) | sub-agent tier | convention-level | `sub_agent_gate_level_descent.py:38` `from harness_as.sandbox_tier import BlastRadiusTier, SandboxTier` — but per the CXA U-CP-26 row attribution, `SandboxTier`/`BlastRadiusTier` are produced by **U-AS-01**, not U-AS-09 (a behavioral "tier-ascension" surface). No U-AS-09-specific type imported. The genuine seam lands on the *undeclared* U-CP-27→U-AS-01 edge — see NEEDS-REVIEW #3. |
| 4 | U-CP-27 | U-AS-14 (5-axis multiplicative tunable) | C-AS-12 §12.1 | convention-level | `sub_agent_gate_level_descent.py` imports `GateLevel`/`SandboxTier`/`BlastRadiusTier` from AS — but no 5-axis-tunable type. The 5-axis composition is performed via CP-local `gate_level_rule`/`per_step_override_evaluator` deps. No U-AS-14 type consumed. |
| 5 | U-CP-27 | U-AS-15 (5-axis composition) | C-AS-12 §12.1 | convention-level | Same file; gate-level descent composes CP-side; no U-AS-15 type imported. |
| 6 | U-CP-29 | U-AS-29 (per-sub-agent-role × model-binding catalog) | C-AS-... model catalog | convention-level | `brief_authoring_inheritance.py:14-18` "Partial-land — `resolve_brief_authoring_model_binding` struck … cross-axis seam: U-AS-29's catalog returns an AS-axis `ModelBinding` … the U-CP-00c `ModelBinding`. Reconciling the two is a [Class 1]". Consumer uses CP-local `ModelBinding`; AS seam explicitly struck. No `harness_as` import. |
| 7 | U-CP-32 | U-AS-17 (sandbox-bounded span schema) | C-AS-15 | spurious | `multi_agent_span_hierarchy.py:31-32` imports `harness_cp` only; no `harness_as`. Docstring `:1-4` covers §14.1/§14.3/§14.5 — no sandbox-bounded span reference. Consumer unit does not reference AS at all. |
| 8 | U-CP-32 | U-AS-31 (anthropic.* cache attributes) | C-AS-14 §14.2 | spurious | Same file; no `anthropic.*`/cache-attribute reference in U-CP-32. CXA edge has no consumer-side referent. |
| 9 | U-CP-33 | U-AS-31 (anthropic.* cache attributes) | C-AS-14 §14.2 | convention-level | `concurrent_prompt_cache_warmup.py` imports `harness_is` (path) only — no `harness_as`. `:8-12` describes prompt-cache warm-up behavior; `:56-63` `CACHE_ACKNOWLEDGEMENT` is an axis-local enum. No `anthropic.*` attribute type consumed. |
| 10 | U-CP-39 | (transitive via U-CP-43) | — | spurious | CXA §2.3.3 + CP plan §3.6 explicitly: "U-CP-39 — (none; consumes via U-CP-43)". Not an edge — a non-edge placeholder row. Counts as 0 typed edges; flagged so CXA v2.3 drops the row. |
| 11 | U-CP-43 | U-AS-05 (per-MCP trust-tier) | C-AS-... trust tier | convention-level | `gate_level_rule.py:43` consumes `harness_cp.cp_shared_types.MCPTrustTier` — a CP-owned (U-CP-00c) enum, not an AS U-AS-05 type. `:9` "CP spec §19.1 names a 'C10 five-tier'" — re-declared CP-side. |
| 12 | U-CP-43 | U-AS-13 (SandboxTier) | C-AS-12 | convention-level | `gate_level_rule.py:39` `from harness_as import BlastRadiusTier` — but per the CXA U-CP-26 row attribution `BlastRadiusTier` is produced by **U-AS-01**, not U-AS-13. No U-AS-13-specific type imported. Genuine seam lands on the undeclared U-CP-43→U-AS-01 edge — see NEEDS-REVIEW #3. |
| 13 | U-CP-43 | U-AS-14 (5-axis multiplicative tunable) | C-AS-12 §12.1 | convention-level | `gate_level_rule.py` — gate-level rule computed from CP-local `GateLevelInput`; only `BlastRadiusTier` imported from AS. No 5-axis-tunable type. |
| 14 | U-CP-43 | U-AS-15 (5-axis composition) | C-AS-12 §12.1 | convention-level | Same file; no U-AS-15 type imported. |
| 15 | U-CP-44 | U-AS-20 (F5 fetch_secret signature) | C-AS-05 §5.1 | genuine-typed-seam | `f5_signing_key_resolution.py:36` `from harness_as import SandboxTier, SecretRef, SecretScope, fetch_secret`. The F5 `fetch_secret` function + `SecretRef`/`SecretScope` types imported directly. |
| 16 | U-CP-45 | U-AS-12 (sandbox-tier composition) | C-AS-12 | convention-level | `five_axis_composition.py:27-28` `from harness_as import BlastRadiusTier` + `from harness_as.sandbox_tier import SandboxTier` — but `SandboxTier`/`BlastRadiusTier` are produced by **U-AS-01** per the CXA U-CP-26 row attribution, not U-AS-12 (a composition surface). `:46-57` cites "U-AS-12 cross-axis" in prose. No U-AS-12-specific type imported. Genuine seam lands on the undeclared U-CP-45→U-AS-01 edge — see NEEDS-REVIEW #3. |
| 17 | U-CP-45 | U-AS-14 (5-axis multiplicative tunable) | C-AS-12 §12.1 | convention-level | Same file; 5-axis composition runs CP-side via U-CP-43 gate-level + U-AS-12 tier input; no U-AS-14 type imported. The "5-axis tunable" is realized as the composition logic, not an imported AS type. |
| 18 | U-CP-47 | U-AS-03 (SandboxFailClass taxonomy) | validator-fail ref | convention-level | `validator_fail_taxonomy.py` imports `harness_core` only — no `harness_as`. CP declares its own `ValidatorFailClass` enum; the U-AS-03 `SandboxFailClass` is a *taxonomy reference* for parallelism, not an import. |
| 19 | U-CP-48 | U-AS-10 (secret.fail.class taxonomy) | secret-fail ref | convention-level | `validator_fail_transient_staircase.py` imports `harness_cp` only — no `harness_as`. Re-uses the staircase scheme; no `SecretFailClass` import. |
| 20 | U-CP-48 | U-AS-29 (model catalog) | model catalog | convention-level | Same file; no `harness_as` import. Fallback model selection referenced in prose, not via the AS catalog type. |
| 21 | U-CP-50 | U-AS-10 (secret.fail.class taxonomy) | secret-fail ref | spurious | `material_diff_detection.py` imports `harness_core`/`harness_cp` only. Material-diff detection has no secret-fail-class reference — the CXA edge has no consumer referent. |
| 22 | U-CP-50 | U-AS-29 (summarization model catalog) | model catalog | spurious | Same file; no model-catalog reference in U-CP-50. |
| 23 | U-CP-53 | U-AS-14 (5-axis multiplicative tunable) | C-AS-12 §12.1 | spurious | `t_perm_3_composition.py` imports `harness_core` + `harness_cp` only. Docstring `:1-25` (C-CP-23 §23.1-§23.4 three-layer F1/D1/D4 composition) makes no AS reference. CXA edge has no consumer referent. |
| 24 | U-CP-55 | U-AS-14 (5-axis multiplicative tunable) | C-AS-12 §12.1 | convention-level | `cp_cross_axis_composition_manifest.py` imports `harness_core` only; `:134` "5-axis gate-level composition; composes with U-AS-14 cross-axis" — a manifest *reference string*, not a type import. |

### Bucket 3 tally (24 enumerated edges; #10 is a declared non-edge)

| Classification | Count |
|---|---|
| genuine-typed-seam | 2 (#2, #15) |
| convention-level | 16 (#1, #3, #4, #5, #6, #9, #11, #12, #13, #14, #16, #17, #18, #19, #20, #24) |
| phase-2-runtime | 0 |
| spurious | 6 (#7, #8, #10, #21, #22, #23) |

24 edges = 2 + 16 + 0 + 6. (Edge #10 U-CP-39 is a CXA-declared non-edge — counted spurious; CXA v2.3 should drop the row, dropping the bucket to 23 real declared edges.)

**Producer-attribution note.** Edges #3 (U-CP-27→U-AS-09), #12 (U-CP-43→U-AS-13), #16 (U-CP-45→U-AS-12) each import `SandboxTier`/`BlastRadiusTier` — a real type import — but the CXA U-CP-26 row attributes those types to **U-AS-01**, not to U-AS-09/13/12. Applying the producer-attribution rule consistently (the same rule that made U-CP-30→U-IS-07 phase-2-runtime while crediting the `Identifier` seam to U-IS-12), the genuine seam at these three units lands on an *undeclared* `→U-AS-01` edge; the declared `→U-AS-09/13/12` rows are convention-level. CXA v2.3 should add the three U-AS-01 edges (or re-target the rows). See NEEDS-REVIEW #3.

---

## Aggregate summary

| Bucket | Declared | genuine | convention | phase-2-runtime | spurious |
|---|---|---|---|---|---|
| CP→IS (§2.3.2) | 36 (actually 38 — see reconciliation) | 8 | 11 | 17 | 2 |
| CP→AS (§2.3.3) | 24 | 2 | 16 | 0 | 6 |
| **Total** | **60 (actually 62)** | **10** | **27** | **17** | **8** |

**Of the 60 (actually 62) CP-consumer cross-axis edges, only 10 are genuine typed seams correctly attributed to the CXA-declared producer unit** — a real `harness_is`/`harness_as` Pydantic type / enum / function import in the CP consumer that maps to the producer the CXA row names. The other 52 are over-declared: 27 convention-level (re-applied scheme, CP-owned/axis-local type stand-in, prose "delegates to", or a real import attributed to the wrong producer unit), 17 phase-2-runtime (F2 ledger compose-then-return / canonicalize / chain / append — runtime concerns, not compile-time links), 8 spurious (consumer unit makes no reference to the producer axis at all). Note: 3 of the 27 convention-level CP→AS edges (#3/#12/#16) DO carry a real type import — but to U-AS-01, not the declared U-AS-09/13/12; the genuine seam exists, the CXA row mis-targets it (NEEDS-REVIEW #3).

This **confirms the systemic over-declaration** the AS→IS bucket-1 audit predicted. The CP→IS bucket is the worst: the F2 state-ledger "audit composition" edges (U-CP-12/14/27/34/37/49/50/52) are almost uniformly phase-2-runtime — the CP units *compose* an audit/checkpoint entry and the canonicalize/hash/chain/append is delegated to the IS axis at runtime (described in prose, never imported). This is the exact U-AS-27 pattern from bucket 1. The CP→AS bucket's spurious count is high (8): U-CP-32, U-CP-50, U-CP-53 carry CXA-declared AS edges their consumer units never reference, and U-CP-39 is an explicit declared non-edge.

### Genuine typed seams (the 10 correctly-declared seams to wire at 7c)

CP→IS (8): U-CP-04→U-IS-01, U-CP-04→U-IS-02, U-CP-30→U-IS-12, U-CP-33→U-IS-01, U-CP-33→U-IS-02, U-CP-34→U-IS-07, U-CP-34→U-IS-11, U-CP-35→U-IS-12.
CP→AS (2): U-CP-26→U-AS-01, U-CP-44→U-AS-20.

(All 10 are already wired in landed 7b code — verified via the import grep. "Already-wired counts as genuine" per the bucket-1 rule.)

**Plus 3 genuine-but-mis-targeted seams (NEEDS-REVIEW #3):** U-CP-27, U-CP-43, U-CP-45 each genuinely import `SandboxTier`/`BlastRadiusTier` — but the seam is to U-AS-01, while the CXA rows declare U-AS-09/U-AS-13/U-AS-12. If CXA v2.3 re-targets these rows to U-AS-01, the genuine CP→AS count rises 2 → 5 and the genuine total rises 10 → 13. The wiring already exists; only the CXA declaration is wrong.

## NEEDS-REVIEW items

1. **CP→IS edge count arithmetic.** CXA §2.3.2 / CP plan §3.6 header says "36 edges" but the verbatim table's multi-target cells sum to **38** (CP-unit × IS-target) pairs. Cell-by-cell: U-CP-04(3) + U-CP-12(1) + U-CP-14(4) + U-CP-18(3) + U-CP-27(3) + U-CP-30(2) + U-CP-33(2) + U-CP-34(4) + U-CP-35(2) + U-CP-37(2) + U-CP-42(4) + U-CP-49(2) + U-CP-50(3) + U-CP-52(2) + U-CP-55(1) = 38. Pre-existing CXA defect — flag for CXA v2.3. Tally above uses the true 38.

2. **U-CP-52 `Identifier` import vs declared targets.** `hitl_timeout_degradation.py:31` genuinely imports `harness_is...Identifier` (a real seam) — but CXA §2.3.2 declares U-CP-52's targets as U-IS-07 + U-IS-11, neither of which is the idempotency-key/`Identifier` unit (U-IS-12). The genuine seam at U-CP-52 maps to U-IS-12, which the CXA row omits. Either the row mis-targets or the import is incidental. I classified the two *declared* targets (U-IS-07, U-IS-11) as phase-2-runtime and did not credit a genuine seam to either; the real U-IS-12 seam is unlisted. CXA v2.3 author should decide whether to add U-CP-52→U-IS-12.

3. **Tier-type producer attribution — U-CP-27/43/45 import real types but the CXA targets are wrong (3 edges).** `sub_agent_gate_level_descent.py`, `gate_level_rule.py`, `five_axis_composition.py` each import `SandboxTier`/`BlastRadiusTier` from `harness_as` — genuine type imports. But the CXA U-CP-26 row explicitly attributes `SandboxTier + BlastRadiusTier` to **U-AS-01** ("SandboxTier + BlastRadiusTier foundational substrate"). The CXA rows for U-CP-27/43/45 declare the targets as U-AS-09 (sub-agent tier ascension), U-AS-13 (SandboxTier), U-AS-12 (sandbox-tier composition) respectively — behavioral/composition surfaces, not the type-producing unit. Applying the producer-attribution rule consistently (same rule that kept U-CP-30→U-IS-07 phase-2-runtime while crediting the `Identifier` seam to U-IS-12, and that flagged U-CP-52's `Identifier` import), the three declared rows are convention-level and the genuine seam belongs to an *undeclared* `→U-AS-01` edge. The CXA author should decide: re-target the three rows to U-AS-01, or add three new U-AS-01 edges. Resolving in favor of U-AS-01 raises the genuine CP→AS count 2 → 5 and the genuine total 10 → 13. The runtime code is correct either way — this is purely a CXA declaration defect. **NOTE on U-CP-43's U-AS-05 row:** CXA declares U-CP-43 against both U-AS-05 (per-MCP trust-tier) and U-AS-13; `gate_level_rule.py:43` consumes the *CP-owned* `MCPTrustTier` (U-CP-00c), not an AS U-AS-05 type — U-AS-05 stays convention-level regardless.
