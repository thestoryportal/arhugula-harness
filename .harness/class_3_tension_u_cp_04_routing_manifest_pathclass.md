# Class 3 Tension — U-CP-04 routing-manifest PathClass drift (informational, RESOLVED)

**Filed:** 2026-05-19 — surfaced during U-RT-21 (L5 stage 3b CP_ROUTING) pre-flight risk-gate check.
**Defect class:** Class 3 — code-vs-spec drift; spec clean, code fixed in-CLI. No design-substrate revision.
**Status:** RESOLVED at filing.

## Observation

`harness-cp/src/harness_cp/routing_manifest_residence.py` `resolve_manifest_residence_path`
(U-CP-04) wired residence through `PathClass.PROMPTS` with a docstring rationale
("operator-authored configuration"). This contradicts three converging authorities:

1. **Spec C-CP-01 §1.3** (`Spec_Control_Plane_v1_2.md` line 248) routes residence
   through `Spec_Information_Substrate_v1.md` **C-IS-10 §10.4** filesystem-path-contract
   export — the dedicated typed PathClass for routing manifests, not the generic prompts class.
2. **IS path registry** (`harness-is/src/harness_is/path_class_registry.py:128`) — the
   `PathClass.ROUTING_MANIFEST` entry's residence contract cites the exact ADR-F1 v1.2
   Consequences §(a) hook ("manifest-layer model assignment as auditable default at every
   call site"); `PathClass.PROMPTS` is a distinct class (prompt-cache static-prefix content
   per Cluster 2 V2 §1.2).
3. **IS-AL-1 anti-leakage** (`harness-is/CLAUDE.md` §4.2) — names the four typed classes
   `SKILLS / PROMPTS / ROUTING_MANIFEST / STATE_LEDGER` as distinct, not aliases.

The U-CP-04 test at `harness-cp/tests/test_routing_manifest_residence.py:65` pinned the
same wrong class (propagated author error).

## Impact

Pre-empted at U-RT-21 pre-flight before any L5 runtime code consumed
`resolve_manifest_residence_path`. U-RT-21 AC binds residence to `PathClass.ROUTING_MANIFEST`;
landing U-RT-21 against the previous CP code would have created a runtime/CP disagreement on
which path the manifest persists at.

## Fix applied in-CLI (2026-05-19)

1. `harness-cp/src/harness_cp/routing_manifest_residence.py:177` — `PathClass.PROMPTS`
   → `PathClass.ROUTING_MANIFEST`.
2. Docstring at the same function — replaced the "operator-authored configuration" rationale
   with the C-CP-01 §1.3 → C-IS-10 §10.4 → registry-entry citation chain.
3. `harness-cp/tests/test_routing_manifest_residence.py:65` — flipped `PathClass.PROMPTS`
   → `PathClass.ROUTING_MANIFEST` plus the corresponding asserted path string.

Ruff + pyright + ruff-format clean. `harness-cp` 465/465 tests pass. Full workspace
1697/1697 tests pass.

## Routing target

None — spec is canonical and unchanged. CP code now conforms.

## Provenance notes

- `concurrent_prompt_cache_warmup.py:115` legitimately uses `PathClass.PROMPTS` (prompt-cache
  surface, not routing-manifest residence) — left untouched.
- U-CP-04 status in CP plan v2.10 remains FULL-LAND; the residence-path call site was always
  inside U-CP-04 scope, no plan signature change required.
- No CXA edge re-tag needed; the CP→IS edge for U-CP-04 → U-IS-02 (`PathResolver` consumption)
  is unchanged in cardinality and direction.
