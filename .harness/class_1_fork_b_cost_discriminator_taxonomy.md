# Class 1 Fork — B-COST-DISCRIMINATOR-TAXONOMY (dispatch-type cost rollup taxonomy reconciliation)

**Filed:** 2026-06-18 · R-FS-1 standalone `B-*` arc **B-COST-DISCRIMINATOR-TAXONOMY** (surfaced at arc CA, advisor-flagged; spine ledger `.harness/beyond-mvp-capability-boundary-ledger.md` line 118). Bundled-absorption posture: OD spec **v1.29 → v1.30** (C-OD-15 §15.1 amendment) + runtime spec **v1.56 → v1.57** (C-RT-09 §9 amendment) + `harness-od/src` + `harness-runtime/src`. Class 1 (X-AL-3 spec **contract extension** on a cleared spec — a new rollup axis + the corrected `provider_discriminator` carrier semantics). Design back-flow FULL-SPEC-pre-authorized (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Status:** ✅ RESOLVED + design decided — drives the impl. **NO operator gate.** The amendment is **additive** (a new `PER_DISPATCH_KIND` rollup axis + a new optional `RunResult` field) and the one existing-surface change (`provider_discriminator` required-`str` → optional `str | None`, the `PER_PROVIDER_DISCRIMINATOR` axis error-on-non-member → skip-on-`None`) is a **bug-fix toward the cleared spec**, NOT a committed-invariant sacrifice. No nameable cross-domain tension (OD-internal cost-taxonomy type design + a runtime surfacing) → single-voice C7 + advisor, **not council** (§10.9 discriminator applied explicitly). Adopt-and-note per workspace `CLAUDE.md` §12.4.1 + `[[feedback-gate-only-on-meaningful-architecture-change]]`; advisor-confirmed (advisor-not-council, no AUQ).

---

## §1 The fork — a latent Class-1 contract-vs-production coherence defect

The OD aggregate primitive `rollup_costs_by_axis(records, axis)` (`harness_od.cross_family_rollup:171`) offers three axes. The `PER_PROVIDER_DISCRIMINATOR` axis **validates** each record's `SpanCostRecord.provider_discriminator` against the bounded `CrossFamilyTag` vocabulary `{frontier_managed, frontier_managed_alt, local_ollama}` and **raises `CrossFamilyRollupError`** on a non-member (`cross_family_rollup.py:156-168, 192-193`).

But every production cost helper writes a **dispatch-type** tag into `provider_discriminator`:

| Helper | `provider_discriminator` written | A `CrossFamilyTag` member? |
|---|---|---|
| `cost_attribution_llm_dispatch.py:216` | `"llm"` | ✗ |
| `cost_attribution_tool_dispatch.py:274` | `"tool"` | ✗ |
| `cost_attribution_validator_dispatch.py:212` | `"validator"` | ✗ |
| `cost_attribution_webhook_dispatch.py:174` | `"webhook"` | ✗ |

⟹ `rollup_costs_by_axis(production_records, PER_PROVIDER_DISCRIMINATOR)` would raise `CrossFamilyRollupError` on **every** production record. It is **dormant** only because the sole current callers are OD unit tests with synthetic `frontier_managed`/`local_ollama` records (`test_cross_family_rollup.py`) + one synthetic runtime test (`test_api.py:144`); the **production** rollup at `api.py:925` routes around it via `PER_PROVIDER_AND_MODEL` (the arc-CA decision, runtime spec v1.53 §9). The dispatch-type cost breakdown (llm-vs-tool-vs-validator-vs-webhook) is **the most operator-meaningful rollup** and is exactly the one this latent defect blocks (registered as this arc by the CA fork doc §2.1 + runtime spec v1.53 §9 line 51).

### §1.1 The root type defect (the load-bearing finding)

The **spec authority resolves what `provider_discriminator` means** — and the production code is the bug, not the validation:

> **C-OD-15 §15.1** (`Spec_Operational_Discipline_v1_2.md:870-878`, preserved verbatim through v1.29): *"The `provider_discriminator` attribute per C-OD-05 §5.1 row 15 **carries the cross-family fallback chain family tag** (`frontier_managed`, `frontier_managed_alt`, `local_ollama`, etc.)."*

Two **orthogonal** cost dimensions were conflated onto one field:

1. **Cross-family family tag** — *which provider family* (for the §15.3 cross-family fallback-chain cost composition). Per §15.3 this is a **fallback-chain-composition concept**: *"Parent span retains `provider_discriminator` family tag; child retry spans carry per-attempt provider."* It is assigned at **chain level**, not derivable by a per-dispatch cost helper.
2. **Dispatch type** — *which kind of dispatch* (`llm`/`tool`/`validator`/`webhook`) incurred the cost. This is what each per-dispatch helper actually knows.

The per-dispatch helpers wrote the dispatch type into `provider_discriminator` precisely **because they lack the fallback-chain family context** the field is spec-reserved for. The `CrossFamilyTag` validation is **correct per spec**; the production write is spec-wrong.

---

## §2 Resolution — separate the two dimensions (Options B+C converge)

### §2.1 The three options at arc-open + the decision

| Option | Shape | Verdict |
|---|---|---|
| **A — extend `CrossFamilyTag`** with `llm`/`tool`/`validator`/`webhook` | Makes `PER_PROVIDER_DISCRIMINATOR` "work" on production records | **REJECTED.** Conflates two orthogonal dimensions in one enum — `frontier_managed` (a provider family) and `llm` (a dispatch type) would be siblings. Violates §4 one-source-of-truth + the spec's explicit family-tag semantics. Pollutes the vocabulary the §15.3 cross-family composition reads. |
| **B — dedicated dispatch-type `RollupAxis` + field** | New `dispatch_kind` carrier field + `PER_DISPATCH_KIND` axis; keep `provider_discriminator`/`CrossFamilyTag`/`PER_PROVIDER_DISCRIMINATOR` for the family dimension | **CHOSEN** (with C). |
| **C — producers set real `CrossFamilyTag`s + carry dispatch-type separately** | Fix producers; carry dispatch type on a separate dimension | **CHOSEN** (converges with B). |

**B and C converge into one fix, and the producer correction is forced (not optional).** Once `dispatch_kind` + `PER_DISPATCH_KIND` exist (B), production **cannot** keep writing dispatch-types into `provider_discriminator` — that keeps the field spec-wrong and `PER_PROVIDER_DISCRIMINATOR` still raises on production records. So "fix the producers" (C) is forced by the amendment. The decided shape:

1. **NEW `DispatchKind(StrEnum)`** = `{LLM, TOOL, VALIDATOR, WEBHOOK}`, homed in the U-OD-20 carrier module (`idempotency_join_dedup.py`) so `SpanCostRecord` can type it **directly** (no `str`+validate dance). This is cycle-free *unlike* `CrossFamilyTag`: `CrossFamilyTag` is homed in the U-OD-21 **consumer** (so the U-OD-20 carrier `str`-types to avoid a U-OD-20→U-OD-21 cycle), whereas `DispatchKind` is the **producer's own attribute** of the record, naturally homed in the carrier. Illegal states unrepresentable (§4 type-driven design).
2. **NEW `RollupAxis.PER_DISPATCH_KIND`** keying on `record.dispatch_kind` — the dispatch-type cost breakdown.
3. **`SpanCostRecord.provider_discriminator`: `str` → `str | None` (default `None`)**. The per-dispatch helpers write `None` (they lack the chain-level family context). The field stays reserved for the §15.3 fallback-chain composition to populate. Still `str`-typed (not `CrossFamilyTag`) to preserve the no-cycle property.
4. **`PER_PROVIDER_DISCRIMINATOR` skips `None` records** (the error→skip refinement) — a `None` record carries no family tag, so it is not part of a cross-family rollup. Records that *do* carry a tag are still validated against `CrossFamilyTag` (unchanged for the synthetic-record tests + the future §15.3 seam).
5. **Production helpers** write `dispatch_kind=DispatchKind.<KIND>` + `provider_discriminator=None`.
6. **`RunResult` gains `cost_attribution_by_dispatch_kind: tuple[CrossFamilyCostRollup, ...]`** (optional, default `()` — minor bump, the v1.45 `pause_snapshot` precedent), computed at `_build_run_result` via `rollup_costs_by_axis(records, PER_DISPATCH_KIND)`. This gives the new axis a real production **consumer** (non-vacuous) and delivers the operator-meaningful breakdown.

### §2.2 Sum-invariant preserved (both axes partition the same total)

`RunResult.cost_attribution` (PER_PROVIDER_AND_MODEL, v1.53) and the new `cost_attribution_by_dispatch_kind` (PER_DISPATCH_KIND) are **two independent single-axis rollups**. Each record has **exactly one** `dispatch_kind` and exactly one `(provider, model)`, so **each field independently satisfies** `sum(e.total_cost) == total run cost`. The two are orthogonal partitions of the same dollar total — no double-count (the multi-axis-concatenation hazard v1.53 §9 warned against is avoided by keeping them in **separate fields**, not one flat tuple).

### §2.3 Gate verdict — autonomous (the discriminator)

Per `[[feedback-gate-only-on-meaningful-architecture-change]]` + the advisor (full-transcript) review:

- The new axis + new `RunResult` field are **purely additive** — the existing `PER_PROVIDER_DISCRIMINATOR` / `CrossFamilyTag` / `PER_PROVIDER_AND_MODEL` / `cost_attribution` surfaces are **untouched** in semantics.
- The one existing-surface change — `provider_discriminator` required-`str` → optional `str | None`, axis error→skip on `None` — is a **bug-fix toward the cleared spec** (the field was spec-wrong as a required carrier of dispatch-types). It sacrifices **no committed invariant**.
- **The discriminator that would have flipped this to operator-gated:** if the reconciliation changed the *existing* committed `PER_PROVIDER_DISCRIMINATOR` / `CrossFamilyTag` semantics **non-additively** (e.g., redefining the vocabulary, Option A). It does not — kept additive, producer correction = bug-fix. → clean-autonomous.
- **No nameable cross-domain tension** (it is OD-internal cost-taxonomy type design + a runtime surfacing) → single-voice C7 + advisor, **not council** (§10.9).

---

## §3 Scope (this arc)

| Surface | Change |
|---|---|
| OD spec **v1.30** (delta over v1.29) | C-OD-15 §15.1: ADD the `PER_DISPATCH_KIND` rollup axis + the `DispatchKind` dispatch-type vocabulary; note `provider_discriminator` is per-dispatch-optional (`None` until §15.3 chain composition). ADDITIVE; §15.1/§15.2/§15.3 prose otherwise preserved. |
| Runtime spec **v1.57** (in-place, v1.56 → v1.57) | C-RT-09 §9: ADD `cost_attribution_by_dispatch_kind: tuple[CrossFamilyCostRollup, ...]` (optional, default `()`, minor bump per the §9 version-evolution invariant — the v1.45 `pause_snapshot` precedent) computed via `rollup_costs_by_axis(PER_DISPATCH_KIND)`. |
| OD plan **v2.28** (delta over v2.27) | U-OD-21 acc #2 (3→4 axes) + acc #3 (+`PER_DISPATCH_KIND` + skip-`None` refinement) + `Tests:` (rename `test_rollup_axis_cardinality_three`→`_four`; add `test_rollup_per_dispatch_kind` + `test_per_provider_discriminator_skips_none_records`) reconciled to the amended §15.1. Surfaced by the cross-spec drift grep (`[[spec-prose-plan-body-drift-pattern]]` — the plan's `Tests:` field named a renamed test). |
| `harness-od/src/harness_od/idempotency_join_dedup.py` | NEW `DispatchKind(StrEnum)`; `SpanCostRecord` gains `dispatch_kind: DispatchKind`; `provider_discriminator: str` → `str | None = None`. |
| `harness-od/src/harness_od/cross_family_rollup.py` | NEW `RollupAxis.PER_DISPATCH_KIND` + its rollup branch; `PER_PROVIDER_DISCRIMINATOR` skips `None`-tag records. |
| `harness-runtime/src/.../cost_attribution_{llm,tool,validator,webhook}_dispatch.py` | `provider_discriminator=None` + `dispatch_kind=DispatchKind.<KIND>`; the `_*_FAMILY_TAG` str constants → `_*_DISPATCH_KIND` `DispatchKind` members. |
| `harness-runtime/src/harness_runtime/api.py` | `RunResult.cost_attribution_by_dispatch_kind` field + `_build_run_result` computes it. |
| Tests | OD field-count 12→13 + annotation refinement + new `PER_DISPATCH_KIND` axis + skip-`None` + `DispatchKind` presence; runtime helper construction + `RunResult` field + integration smoke. |

## §4 Out of scope — registered forward arc

**`B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION` (registered this arc, forward).** Populating `provider_discriminator` with a real `CrossFamilyTag` at the §15.3 fallback-chain composition (the `FallbackChainCostComposition` seam + the CP→OD cross-axis edge `cross_family_rollup.py:36` — C-CP-04 cross-family fallback chain) — which makes `PER_PROVIDER_DISCRIMINATOR` **non-vacuous in production** (today every production record is correctly `None` because per-dispatch has no chain context). The cross-family rollup axis remains **defined + admissible** (exercised by the synthetic-record tests); only its production population awaits the §15.3 producer. Per the advisor's "don't silently half-fix" + `[[r-cxa-seam-wiring-is-producer-discovery]]` (grep the seam's real producer first — the §15.3 producer is the CP fallback path, a genuinely separate cross-axis arc), this is **registered, not folded in**. Spec §15.3 already marks the dashboard query / population "deferred to implementation discretion."

## §5 Carrier ripple (verified before authoring)

- **Field-count assertion** `test_idempotency_join_dedup.py:94` (`== 12` → `== 13`) + the `is str` annotation assertion at line 123 (`provider_discriminator` now `str | None`; `gen_ai_*` stay `str`). Construction sites updated: 4 production helpers + `_cost_record()` test helpers (OD ×2) + `test_api.py:144` + `test_run_smoke.py` 12-field construction.
- **No C-IS-05 §5.2 hash change.** Per runtime spec v1.53 §9 (scope discipline, line 62): *"No IS-spec / §5.2-hash change (the run-scoped accumulator is ephemeral run-OUTPUT, not a dispatch-determinism config dimension)."* The cost-record carrier feeds the run-scoped ephemeral accumulator + the explicit 5-field `CostRecordAuditPayload` projection (`cost_namespace.py` / `cost_record_audit_writer.py`) — neither `provider_discriminator` nor the new `dispatch_kind` is in that audit projection, so the C-OD-14 §14.5 audit hash is **deliberately unchanged** (consistent with the existing family-tag field's exclusion).
- **Broad-suite run** (`[[shared-is-shape-change-ripples-cross-axis-field-asserts]]`): harness-od + harness-runtime + the CXA-P1 cross-axis import allowlist (no new cross-axis import is added — `DispatchKind` is OD-internal, imported by runtime from the existing `harness_od.idempotency_join_dedup` carrier already imported for `SpanCostRecord`).

---

**Decorrelated review:** advisor (full-transcript — affirmed the spec reading as the load-bearing finding; sharpened the forced `provider_discriminator`-for-non-LLM sub-decision; confirmed autonomous/no-council/additive) + out-of-family Codex (pre-merge, on the diff). **Verification:** reads grounded against the worktree @`655ff6b` (origin/main), NOT the diverged local main checkout @`cc55a43` (the #637 precedent — confirmed live this session).
