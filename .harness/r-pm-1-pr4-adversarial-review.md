# Adversarial Review — R-PM-1 cascade PR #4 (OD per-tier prompt governance)

## Summary
- Mode: Phase-7 bundled-absorption arc pre-merge review (§4.1 severity framework)
- Commit reviewed: `6cd9dd2` on `feat/r-pm-1-pr4-od-per-tier-prompt-governance` (vs `main`)
- Artifacts reviewed: `design-substrate/Spec_Operational_Discipline_v1_29.md` (NEW C-OD-34); `harness-od/src/harness_od/prompt_governance_gradient.py` (NEW); `harness-od/tests/test_prompt_governance_gradient.py` (NEW); `harness-runtime/src/harness_runtime/lifecycle/prompt_selection.py` (MOD); `harness-runtime/src/harness_runtime/bootstrap/stage_0_preamble.py` (MOD); `harness-runtime/src/harness_runtime/types.py` (MOD); `harness-runtime/tests/test_prompt_governance_enforcement.py` (NEW); `harness-runtime/tests/test_bootstrap.py` (MOD); `.harness/clearance/Spec_Operational_Discipline-v1_29-cleared-2026-06-12.md` (NEW); `harness-od/CLAUDE.md` (MOD)
- Date: 2026-06-12
- Finding count by class (§4.1): Class 3 (severe): 0 · Class 2 (moderate): 0 · Class 1 (minor/drift): 2
- Highest-severity finding: F1-01 (clearance back_reference cites a non-resolvable runtime-spec path-form)
- Disposition recommendation: **clearance with inline fixes** (both Class-1 findings are optional, non-blocking; neither requires a code change)

---

## Class 3 findings (severe — phase re-opening)

None.

## Class 2 findings (moderate — current-phase revision)

None.

## Class 1 findings (minor — documentation drift)

### F1-01 — Clearance back_reference cites a non-resolvable runtime-spec path-form
- **Location:** `.harness/clearance/Spec_Operational_Discipline-v1_29-cleared-2026-06-12.md:9` — `design-substrate/Spec_Harness_Runtime_v1_44... §14.5.2 (the injection layer)`
- **Defect:** The literal path `design-substrate/Spec_Harness_Runtime_v1_44.md` does NOT exist. The runtime spec is a **single delta-only file** `design-substrate/Spec_Harness_Runtime_v1.md` whose *internal* title/head is "Harness Runtime v1.44" (verified: `Spec_Harness_Runtime_v1.md:1` = "# Specification — Harness Runtime v1.44"). The clearance writes the path with an ellipsis (`v1_44...`) as if the runtime spec were a per-version file like the OD/CP/IS specs, but it is not. The cite is decision (the `§14.5.2` target is real — `Spec_Harness_Runtime_v1.md:13` authors §14.5.2), only the path-form is imprecise/non-resolvable as written.
- **Discriminator:** (a/b/c) all miss — this is a cross-reference imprecision in a non-canonical process-substrate doc (a clearance marker, not a design-substrate spec), with no semantic change. → Class 1 (drift).
- **Evidence:** `ls design-substrate/ | grep Spec_Harness_Runtime` → only `Spec_Harness_Runtime_v1.md`. The **spec body** of v1.29 cites the same seam correctly as prose ("runtime spec v1.44 §14.5.2", `Spec_Operational_Discipline_v1_29.md:12` + `:44`), which resolves to the runtime spec at its internal v1.44 §14.5.2 — so the canonical artifact is clean; only the clearance back_reference path-form drifts.
- **Resolution path:** Inline fix in the clearance marker — write the runtime-spec back_reference in the file-path-plus-internal-version form the spec body already uses (file is `Spec_Harness_Runtime_v1.md`, internal version v1.44), rather than as a non-existent `Spec_Harness_Runtime_v1_44.md` path. Non-blocking.

### F1-02 — `harness-od/CLAUDE.md` §3.1 plan-invariants table does not flag the spec/plan contract-count split
- **Location:** `harness-od/CLAUDE.md:104` — `| Spec contracts covered | 23 of 23 (C-OD-01 through C-OD-23) |`
- **Defect:** The diff updated the §1.2 spec-authority row (`harness-od/CLAUDE.md:19`) to "34 contracts C-OD-01 through C-OD-34" but the §3.1 OD-*plan*-invariants table at line 104 still reads "23 of 23 (C-OD-01 through C-OD-23)". This is **correct-as-scoped** — line 104 reports OD *plan* (v2.27) coverage, and C-OD-34 is a bundled-absorption carrier with NO plan atomic unit (spec footer "ADR impact: None"; design doc §6 row #4 lands it as a spec delta + direct impl, not a plan unit), so the plan still covers exactly the 23 contracts C-OD-01..23. The drift is only that a reader scanning §3.1 in isolation sees "23 of 23" with no note that the spec contract count has since grown to 34 (the distinction is real but unsignposted within the file).
- **Discriminator:** (a/b/c) all miss — within-file presentational imprecision; no semantic error (the number is right for what it counts). → Class 1 (drift).
- **Evidence:** `harness-od/CLAUDE.md:19` ("34 contracts ... C-OD-34 added at v1.29") vs `:104` ("23 of 23"). The spec footer `Spec_Operational_Discipline_v1_29.md:130` confirms "Chain contract count 33 → 34" with no plan-unit landing; OD plan head is `Implementation_Plan_Operational_Discipline_v2_27.md` (unchanged in this PR).
- **Resolution path:** Optional inline clarification at the §3.1 row (note that plan-coverage 23 is distinct from spec contract count 34; C-OD-34 is plan-unit-less by the bundled-absorption arc shape). Non-blocking; the number is not wrong.

---

## Findings considered and rejected (transparency)

These vectors were applied empirically and did NOT surface a defect; recorded for operator trust.

1. **Contract-number collision / off-by-one (C-OD-34 correctness).** Verified: `grep -rhoE 'C-OD-[0-9]+' design-substrate/` → max prior = C-OD-33; no file other than `v1_29` contains `C-OD-34`. C-OD-34 is the correct next number, no collision. **Clean.**

2. **Redaction-derivation: is there a genuine second source of truth?** The crux claim. `prompt_content_redaction_enforced(tier) ≡ not PER_PERSONA_TIER_REDACTION[tier].toggleable` (`prompt_governance_gradient.py:129`). The `PromptGovernancePosture` model carries ONLY `{persona_tier, approval_required}` — verified by `model_fields` assertion in `test_posture_declares_no_redaction_flag`. There is NO re-declared redaction field. The accessor reads the SAME `toggleable` field that `RedactionSpanProcessor.on_end` consults (`redaction_span_processor.py:276` checks `self._persona_tier == SOLO_DEVELOPER and _SESSION_CONTENT_CAPTURE.get()` — i.e. the toggle is honored ONLY at the toggleable tier). **No second source of truth; the derivation is the single-source read.** Clean.

3. **Could `prompt_content_redaction_enforced` ever DISAGREE with what `RedactionSpanProcessor` actually does?** Walked the processor behavior per tier: SOLO (`toggleable=True`) — strips by default but `session_content_capture()` can skip the strip → redaction NOT enforced → accessor returns `not True = False`. AGREES. TEAM/MULTI (`toggleable=False`) — the override at line 276 is gated on `SOLO_DEVELOPER` only, so binding tiers ALWAYS strip → redaction enforced → accessor returns `not False = True`. AGREES. The derivation tracks the processor's real behavior at all 3 tiers. **Clean.**

4. **`gen_ai.system_instructions ∈ DEFAULT_OFF_CONTENT_ATTRIBUTES`?** Verified at `content_structure_discipline.py:63` — it is a member of the frozenset. `test_prompt_artifact_class_is_redaction_covered` asserts it. The prompt-content attribute is genuinely a default-off class. **Clean.**

5. **Spec §C-OD-34.3 4 fire-conditions vs `enforce_prompt_version_approval` byte-for-byte.** Spec conditions (`Spec_Operational_Discipline_v1_29.md:109-112`): (1) `resolve_prompt_governance(tier).approval_required is True`; (2) a selection manifest is configured; (3) selection DRIVES a version (`resolve_active_prompt_version_sha → non-None`); (4) the driven sha ∉ `approved_prompt_version_shas`. Code (`prompt_selection.py:231-241`): `if not resolve_prompt_governance(persona_tier).approval_required: return` (¬1); `if selection_manifest is None: return` (¬2); `selected_sha = resolve_active_prompt_version_sha(...); if selected_sha is None: return` (¬3); `if selected_sha not in approved_prompt_version_shas: raise` (4). **Exact 1:1 correspondence, no off-by-one, no missing condition.** Clean.

6. **Non-breaking claim: does any existing TEAM/MULTI deployment with a selection manifest now fail?** `RuntimeConfig.persona_tier` defaults to `SOLO_DEVELOPER` (`types.py:1288`), so the gate is inert by default (condition 1 fails). An EXHAUSTIVE grep across the whole runtime test tree found the intersection of (a binding `persona_tier`) AND (a `prompt_selection_manifest`) in exactly 3 files: the two NEW test files (expected), plus `test_r300_cross_family_fallback_e2e.py`. In r300, the selection-driving live e2e (lines 902-910) builds config via `_build_config` (lines 130-149, which does NOT set `persona_tier` → defaults to SOLO), and the `TEAM_BINDING` at line 182 is on the `WorkflowManifestEntry` (a different object the gate never reads — the gate keys on `config.persona_tier`). **POSITIVE CONTROL (verified by EXECUTION, not just reading):** ran `pytest test_r300_cross_family_fallback_e2e.py -k 'selection or prompt'` → `test_r_pm_1_workload_selection_drives_live_ollama_injection` (the test with both a driving selection manifest AND a TEAM_BINDING manifest-entry) **PASSED, did not raise `PromptVersionUnapprovedError`** — exactly as the non-breaking claim predicts. Full bootstrap suite 29/29 green. **The non-breaking claim holds, verified empirically.**

7. **Double-resolution divergence: could the gate's re-resolution pick a DIFFERENT sha than the reconciler activated?** The gate independently calls `resolve_active_prompt_version_sha(selection_manifest, role=_MVP_DEFAULT_AGENT_ROLE, workload=workload_class)` — the SAME pure resolver the reconciler used (`reconcile_active_prompt_via_selection` line 150), with identical `(role, workload)` inputs. The resolver is pure (no I/O, no store consultation, deterministic — `prompt_selection_manifest.py:138-157` docstring "Pure (no I/O...)"). So the gate's re-resolved sha is byte-identical to the reconciler's. **No divergence; the gate governs exactly the version the reconciler activated.** Clean.

8. **X-AL-3 silent design-extension check (the most load-bearing rule).** C-OD-34 is an ADDITIVE OD posture composing pre-existing surfaces (ADR-D5 v1.3 §1.5 persona ladder + C-OD-13 redaction gradient + C-OD-12 default-off set + R-CL-P3 #481 tier-distinctness). It edits ZERO of §C-OD-01..C-OD-33 (verified: no prior contract diff). It introduces no new namespace, no new ADR, no new CXA edge (the seam is deferred to cascade PR #5 per §C-OD-34.4). The new runtime enforcement consumes the OD posture + the existing CP resolver within the runtime (the top consumer); OD's 0-outbound-to-other-axes invariant is preserved (the posture is consumed BY runtime; OD emits no new outbound edge). This is a legitimate bundled-absorption arc per workspace `CLAUDE.md` §11.4 (spec delta + impl landed together, with a clearance marker as back-flow doc). **No silent design extension.** Clean.

9. **Forward-cite phantom (does C-OD-34 cite anything that doesn't exist?).** The cross-axis cites in the spec body — runtime spec v1.44 §14.5.2 (injection), IS spec v1.7 §5.3 (store), CP spec v1.31 §29 (selection) — all resolve: §14.5.2 exists in `Spec_Harness_Runtime_v1.md:13`; CP §29 / C-CP-29 is the canonical CP HEAD per `harness-cp/CLAUDE.md:19`. The ONLY phantom is the clearance back_reference path-form (F1-01), not a spec-body cite. **Spec body clean.**

10. **Tests vacuity check (are the ACs proven by EXECUTION, not grep?).** Ran `uv run --package harness-od pytest test_prompt_governance_gradient.py -q` → 7 passed; `uv run --package harness-runtime pytest test_prompt_governance_enforcement.py test_bootstrap.py::test_bootstrap_binding_tier_unapproved_selection_fails_loud test_bootstrap.py::test_bootstrap_binding_tier_approved_selection_passes -q` → 11 passed. The enforcement tests cover all 4 fire-conditions + non-vacuous tier-distinctness ("the SAME unapproved selection inert at solo FAILS at binding tiers") + the per-role path. The 2 bootstrap e2e tests exercise the gate THROUGH `run_bootstrap` (real bootstrap): unapproved → `BootstrapFailure` cause `PromptVersionUnapprovedError` at `PREAMBLE`; approved → `bare.active_system_prompt == "governed prompt"` (gate did not block + the selected version actually activated). **Genuinely e2e-proven, non-vacuous.** Clean.

11. **Sibling-spec / cross-spec drift on the OD contract count.** Grepped `C-OD-01 through C-OD-NN` across all specs/plans/axis-CLAUDE.md. The "23" cites in `Spec_Operational_Discipline_v1 (1).md` / `_v1_1` / `_v1_2` / the OD plans / the archive are all **historical-version files / plan-scoped coverage** (correct for their version/scope under the delta-only convention — each version is canonical-at-authoring for its scope). No sibling spec falsely claims OD is at 23 contracts as current HEAD. The only live within-file count-split is F1-02 (plan-coverage 23 vs spec-count 34 in `harness-od/CLAUDE.md`), which is scoped-correct. **No genuine cross-spec drift.**

12. **pyright strict on changed src files.** `uv run pyright` on the 4 changed src files → `0 errors, 0 warnings, 0 informations`. **Clean.**

13. **Frozen/hashable posture model + totality.** `PromptGovernancePosture` is `frozen=True, extra="forbid"` with an explicit `__hash__`; `PER_PERSONA_TIER_PROMPT_GOVERNANCE` maps all 3 `PersonaTier` values (`test_posture_maps_every_tier` asserts `set(...) == set(PersonaTier)`); `resolve_prompt_governance` is total over the closed enum. **Clean** — mirrors the established `PerPersonaTierRedactionPosture` shape exactly.

---

## Disposition

**APPROVE-WITH-CLASS-3** (i.e. clearance with optional inline documentation fixes; using the report's class taxonomy: only Class-1 findings present → clearance with inline fixes per §4.1.1).

The arc is sound. All three load-bearing design claims verify against reality:
- **Redaction derivation has no second source of truth** and provably tracks `RedactionSpanProcessor`'s actual per-tier behavior (rejected-findings 2 + 3).
- **The approval gate is a real runtime gate** whose 4 fire-conditions match the spec §C-OD-34.3 byte-for-byte (rejected-finding 5), is genuinely e2e-proven through `run_bootstrap` (rejected-finding 10), and is **non-breaking** — inert at the SOLO default, and the one existing TEAM/MULTI-adjacent e2e runs at SOLO so it does not fail (rejected-finding 6). The double-resolution is divergence-free because the resolver is pure with identical inputs (rejected-finding 7).
- **No X-AL-3 violation / no silent design extension** — additive OD posture, zero edit to C-OD-01..33, no new ADR/CXA edge, OD 0-outbound invariant preserved (rejected-finding 8).

The 2 Class-1 findings are both non-canonical-doc drift (a clearance back_reference path-form; an unsignposted plan-vs-spec count split in the axis CLAUDE.md), neither requires a code change, and neither blocks merge. Recommend the operator fix F1-01 inline (cheap, in the clearance marker) and optionally F1-02; both can also be deferred to a doc-hygiene pass without risk.

**No §2.7.6 Phase-7 fork triggered.** (No Class-1-execution-halt; no Class-2-operator-decision. The §4.1 Class-1 findings are doc drift, distinct from §2.7.6 Class-1 halt-execution.)

---

### VERDICT: APPROVE-WITH-CLASS-3
