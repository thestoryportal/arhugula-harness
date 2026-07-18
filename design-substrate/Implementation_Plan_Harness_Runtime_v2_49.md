# Implementation Plan — Harness Runtime — v2.49

*Delta over v2.48. v2.49 is the Runtime plan leg of the RATIFIED **B-51 / B-52 / B-54 OD audit-signing amendment arc** (`.harness/class_1_fork_b51_b52_b54_od_signing_amendment_arc.md`, **RATIFIED 2026-07-18 — all ten gate items ratified AS RECOMMENDED**; three dyadic council convenings at the apply leg, **all-CONFIRM, zero deviations**), absorbing **Runtime spec v1.101** (the six Runtime-owned rider surfaces (A)–(F): the `audit_signing_fail_closed` C-RT-03 field + MTC config-validation invariant; the MTC tenant-scope bootstrap invariant; the MTC prewarm/keepalive disable; tenant threading + handler wiring; the NEW §13.5 C-RT-13 verifier inputs; the B-53 §13.4 `harness migrate-audit-sidecar` row). The v2.48 head has NO acceptance criteria for any of these (the v1.99 B-18-KEEPALIVE and v1.33-era signing surfaces landed spec+impl-together with no plan units) — v2.49 authors **FIVE NEW atomic units U-RT-134..U-RT-138** (next free IDs after U-RT-133, verified by grep across the chain) and **amends ONE existing unit (U-RT-102)** for the B-53 subcommand. Unit count 133 → **138**. All sections except the §0 change note, the §1 new-unit bodies + U-RT-102 amendment, and the §2/§3 DAG + coverage deltas below are PRESERVED VERBATIM from v2.48 (delta-only-plan-chain convention).*

**Status:** Proposed

---

## §0 Change-note (v2.48 → v2.49)

### §0.1 Predecessor

`Implementation_Plan_Harness_Runtime_v2_48.md` (v2.48 — the R-FS-1 R-plan-1 runtime leg; U-RT-132/133).

### §0.2 Revision scope

Per the fork's ratification-gate plan-delta clause (filing codex round-11 P2 / round-12 P2): "the Runtime plan (v2.48 head) has no acceptance criteria for the new RuntimeConfig flag, bootstrap validation, handler policy, prewarm/keepalive posture, or tenant threading." v2.49 decomposes the Runtime v1.101 rider surfaces (A)–(F) into five new units + one amendment. OD/CP-owned contract text is CROSS-REFERENCED to the same-arc OD plan v2.29 (U-OD-30 amended; U-OD-55 NEW) and CP plan v2.38 (U-CP-42/44/45/72/73 amended) — never restated. Naming discretion per the spec is respected throughout: exact CLI flag / `harness.toml` key names, the C-RT-14 fail-class identifier for the UNVERIFIED-nonzero exit, and the `PrewarmOutcome` policy-skip member name are implementation discretion — the units below pin BEHAVIOR criteria and mark any proposed name as a non-binding suggestion.

### §0.3 Sections revised

§0 (this change note); §1 (NEW U-RT-134..U-RT-138 + the U-RT-102 amendment); §2 (DAG delta); §3 (coverage delta). All v2.48-and-earlier unit bodies (U-RT-01..U-RT-133) PRESERVED VERBATIM except U-RT-102 as amended below.

### §0.4 Scope + witness discipline

The Runtime-owned PD-8 witness obligations of the v1.101 change-note ((a)–(e), each mutation-probed per Workflow v1.18 PD-8) home as `Tests:` criteria: (a) + (c) → U-RT-134; (b) → U-RT-135; (d) → U-RT-138; (e) → U-RT-102 (amended). Cross-axis co-land pins (recorded, not DAG edges): U-RT-136 ⊕ CP plan v2.38 U-CP-73; U-RT-137 ⊕ CP plan v2.38 U-CP-72 ⊕ OD plan v2.29 U-OD-30 — all land in the one B-51/B-52/B-54 impl arc per fork gate item 10.

---

## §1 New units + amendment

### §1.1 U-RT-134 — `audit_signing_fail_closed` RuntimeConfig field + dual env-loader registration + MTC config-validation invariant (rider surfaces A + B)

**Implements:** Runtime spec v1.101 §3 C-RT-03 (`audit_signing_fail_closed` field row; `tenant_id` row MTC amendment; the NEW MTC audit-signing config-validation invariant). Policy semantics OD-owned (OD v1.34 §21.2.3 rows 1–4 — cross-referenced).

**Depends on:** [U-RT-103] (RuntimeConfigSource layered loading — the field must ride all three source layers).

**Files affected (logical):** the RuntimeConfig schema module; `config/loader.py` (`_ENV_SCALAR_FIELDS`); `config_source.py` (`_RuntimeEnvSettings`); the bootstrap config-validation site.

**Acceptance criteria:**

1. `RuntimeConfig` gains `audit_signing_fail_closed: bool | None = None` — bool-like TRI-STATE: unset (`None`) → per-persona default (ON at `multi-tenant-compliance`, OFF at `solo-developer` / `team-binding`); explicit `true` → fail-closed; explicit `false` → valid only at non-MTC tiers.
2. **(EXPLICIT criterion per dyad-2 precision note 3 — the known dropped-env-override defect class, `[[runtimeconfig-scalar-needs-both-env-loaders]]`.)** DUAL env-loader registration: the field is env-keyed via BOTH `config/loader.py::_ENV_SCALAR_FIELDS` AND `config_source.py::_RuntimeEnvSettings`, key `HARNESS_AUDIT_SIGNING_FAIL_CLOSED`. Registration in only one loader is an acceptance FAILURE.
3. Config validation at bootstrap REJECTS, at EVERY persona tier, the RESOLVED `audit_signing_fail_closed` flag ON without a configured `SigningBackend` (§21.2.3 row 4 is TIER-AGNOSTIC — a solo/team `fail_closed=true` opt-in without a backend would be silently ineffective, `unsigned:*` placeholders emitted without raising); ADDITIONALLY at `persona_tier == MULTI_TENANT_COMPLIANCE` it REJECTS (i) explicit `audit_signing_fail_closed=false` (§21.2.3 row 3) and (ii) a `tenant_id` that is `None` OR refused by the OD-exported normalizer (empty string; reserved `"_single"` — validation DELEGATES to the same U-OD-30 normalizer signing uses, codex round-4 P1). All rejections surface via the existing `RT-FAIL-CONFIG` (permanent) taxonomy row.
4. The rejections are bootstrap/config-validation events, not runtime catch-site events; every OTHER configuration at non-MTC tiers is byte-preserved (flag unset/OFF behavior unchanged; flag ON WITH a backend accepted at every tier).

**Tests (mutation-probed per PD-8):** **Witness (a) — flag config-validation:** `test_mtc_explicit_false_rejected_at_config_validation`, `test_fail_closed_on_without_backend_rejected_at_bootstrap_every_tier` (parametrized over solo-developer/team-binding explicit `true` AND MTC per-persona default), `test_env_only_override_honored_through_both_loaders` (mutation probe: removing EITHER loader registration fails the test). **Witness (c) — tenant bootstrap invariant:** `test_mtc_invalid_tenant_rejected_at_config_validation` (parametrized: `None`, `""`, `"_single"` — mutation probe: bypassing the normalizer delegation and checking only `None` fails the empty-string/reserved cases).

**Rollback boundary:** revert the field + invariant; the B-52 fail-open-at-MTC exposure reopens; U-RT-135/U-RT-136 lose their flag substrate.

---

### §1.2 U-RT-135 — MTC prewarm/keepalive DISABLE under fail-closed (rider surface C; fork gate item 8)

**Implements:** Runtime spec v1.101 (C) — the amendment to the v1.99 B-18-KEEPALIVE contract (ADR-D3 §1.5:189-190 lineage). OD policy ground: OD v1.34 §21.2.3 row 8 (cross-referenced).

**Depends on:** [U-RT-134].

**Files affected (logical):** the bootstrap stage-5 LOOP_INIT boot-prewarm site; the `cli/app.py` daemon keepalive-spawn site; the `PrewarmOutcome` enum.

**Acceptance criteria:**

1. Under `audit_signing_fail_closed=ON` at MULTI_TENANT_COMPLIANCE, BOTH B-18-KEEPALIVE surfaces are disabled AS CONTRACT TERMS: (i) the `prompt_cache_boot_prewarm` stage-5 LOOP_INIT boot ping is NOT fired; (ii) the `_keepalive_loop` daemon coroutine is NOT SPAWNED — the LOOP itself, not merely a `prewarm()` early-return (dyad-2 precision note 1: the loop's own swallow-all outer catch must be unreachable BY CONTRACT, not by coincidence of call order).
2. The disable is a POLICY SKIP composing with the existing `PrewarmOutcome` `SKIPPED_*` outcome family — a policy skip is NOT a `FAILED` outcome and MUST NOT count toward the keepalive `consec_fail` self-disable accounting. *(Member name is implementation discretion; non-binding suggestion: `SKIPPED_POLICY_FAIL_CLOSED`.)*
3. The disable keys on the RESOLVED flag, NOT the tier (codex round-2 P1 on the apply PR): an EXPLICIT `audit_signing_fail_closed=true` at solo-developer/team-binding disables prewarm + keepalive identically (otherwise `prewarm()`'s swallow-all at `llm_dispatch.py:851-857` + the keepalive outer catch at `app.py:416-420` convert a post-paid-call signing failure into `FAILED` under an operator's explicit fail-closed opt-in). Flag-OFF behavior (the non-MTC default) BYTE-PRESERVED — the v1.99 contract stands verbatim for it (opt-in-default-off; 5m-TTL-only keep-alive; swallow-all best-effort posture).

**Tests (mutation-probed per PD-8):** **Witness (b) — resolved-flag disable:** `test_flag_on_boot_prewarm_not_fired` (parametrized: MTC default-ON AND solo-developer explicit `true`), `test_flag_on_keepalive_loop_never_spawned` (LOOP-level witness — asserts the coroutine/task is never created, not merely that `prewarm()` early-returns; same parametrization), `test_policy_skip_is_skipped_family_and_never_increments_consec_fail`, `test_flag_off_byte_preservation_control` (flag unset at solo/team — v1.99 behavior verbatim).

**Rollback boundary:** revert the disable; the gate-item-8 fail-open bypass (post-provider-call signing failure swallowed while the process continues) reopens at MTC.

---

### §1.3 U-RT-136 — ten-handler flag-consult wiring + post-effect catch-ordering fence sites (rider surface D, wiring half)

**Implements:** Runtime spec v1.101 (D) — runtime-owned WIRING of OD v1.34 §21.2.3 rows 1/5/7 + CP v1.101 §2 (both cross-referenced; policy and CP-contract halves defined there).

**Depends on:** [U-RT-134, U-CP-73 (cross-axis: CP — the amended carve-out + fence contract at CP plan v2.38 §2; co-land)].

**Files affected (logical):** the ten `except AUDIT_SIGNING_HARD_FAILURES` handler sites on `main` (`hitl_gate_composer.py` ×2, `sub_agent_dispatch.py` ×1, `webhook_delivery_composer.py` ×2, `runtime_tool_dispatcher.py` ×2, `llm_dispatch.py` ×2, `cost_attribution_validator_dispatch.py` ×1); the `_run_per_candidate_attempts` per-attempt catch in `retry_breaker_fallback.py`; the typed-error surface (`audit_signing_errors.py`).

**Acceptance criteria:**

1. ALL TEN enumerated `except AUDIT_SIGNING_HARD_FAILURES` handler sites consult `audit_signing_fail_closed` — or the consult is centralized immediately ahead of every catch: under ON the typed family RAISES; under OFF the existing loudly-surfaced (ERROR-logged) proceed behavior is preserved verbatim at every site.
2. The typed-boundary widening (OD v1.34 §21.2.3 row 5 — untyped backend `ValueError`/`TypeError` routed through `AUDIT_SIGNING_HARD_FAILURES` before any policy catch) is wired at the runtime typed-error surface, per OD plan v2.29 U-OD-30 acc #22 (cross-referenced).
3. The post-effect catch-ordering FENCE is wired at every post-effect site class: `AUDIT_SIGNING_HARD_FAILURES` caught AHEAD of the generic per-attempt classifier catch in `_run_per_candidate_attempts` (whose all-other-`Exception` branch returns `TRANSIENT_RETRY`), and the SAME fence at the tool-execution, webhook-POST, and sub-agent-completion post-effect site classes — result-preserving: never `TRANSIENT_RETRY` (or any staircase class), never candidate-advance, never breaker-failure; the already-obtained result is preserved for the audit-failure report.
4. The validator post-evaluate hook site implements the CP v1.101 §2 carve-out narrowly (typed family raises under ON; all other hook exceptions still swallowed; flag OFF preserved) — the contract criteria live at CP plan v2.38 U-CP-73; this unit is their runtime enforcement site.

**Tests (mutation-probed per PD-8):** runtime-side halves of CP witnesses (b) + (e): `test_each_of_ten_handler_sites_raises_under_flag_on_and_logs_under_off` (parametrized over the ten sites), `test_post_effect_fence_ahead_of_classifier_at_every_site_class_result_preserved`.

**Rollback boundary:** revert the wiring; MTC stays fail-open at the enumerated sites and a post-effect signing failure re-enters retry/breaker (re-firing a completed PAID effect) — the exact defects legs 2's ratification forecloses.

---

### §1.4 U-RT-137 — tenant threading at converter-based production call sites (rider surface D, tenant half)

**Implements:** Runtime spec v1.101 (D) — tenant threading from `StepExecutionContext.tenant_id` (OD v1.34 §21.2.1 row 3; CP v1.101 §1 row 4 — both cross-referenced).

**Depends on:** [U-CP-72 (cross-axis: CP — the tenant-bearing converter signature; co-land), U-OD-30 (cross-axis: OD — the tenant-bearing signing API; co-land)].

**Files affected (logical):** every converter-based production call site of `cp_audit_to_od_audit` in the runtime lifecycle composers.

**Acceptance criteria:**

1. Every converter-based production call site sources the signing tenant from `StepExecutionContext.tenant_id` and passes it RAW to the converter (normalization is OD-owned at signing, never at the call site or converter).
2. The workflow-less prewarm path (which today signs `tenant_id=None` outside any workflow) signs NOTHING at MTC because U-RT-135 removes it there — NO synthetic-scope policy is introduced.
3. The redaction-map carrier path is OD-owned (it already holds its own `_tenant_id`; OD v1.34 §21.2.1 row 4 / OD plan v2.29 U-OD-30 acc #19) — cross-referenced, not re-wired here.
4. Tenant absent (single-tenant deployments) → every call site's produced `AuditLedgerEntry` byte-identical to the pre-amendment path (the drop-when-`None` chain end-to-end).

**Tests (mutation-probed per PD-8):** `test_converter_call_sites_thread_step_context_tenant_id_producing_five_segment_message` (pairs with CP witness (a) / OD witness (a)), `test_tenant_absent_call_sites_byte_identical_end_to_end` (pairs with OD witness (b)). **Normalizer delegation (codex round-2 P2):** `test_writer_tenant_tag_delegates_to_od_normalizer` — `RuntimeAuditLedgerWriter._tenant_tag` DELEGATES to the `harness_od`-exported normalizer authored at U-OD-30 (the OD v1.34 §21.2.1 row-2 ONE authority; `harness-runtime` imports `harness-od`, never the reverse); mutation probe: introducing a divergent rule in the writer (e.g. accepting the empty string) fails the test — the signed segment and the sidecar join key cannot drift.

**Rollback boundary:** revert the threading; converter-site signatures fall back to tenant-unbound four-tuples — the B-51 exposure reopens at every production call site.

---

### §1.5 U-RT-138 — `harness-inspect` audit-signature verification inputs + MTC UNVERIFIED-nonzero disposition (rider surface E; NEW §13.5)

**Implements:** Runtime spec v1.101 NEW §13.5 (C-RT-13 verification inputs rows 1–7) + the §13 `harness-inspect` exit-contract amendment. Verification SEMANTICS OD-owned (OD v1.34 §21.2.2 — cross-referenced; API at OD plan v2.29 U-OD-55).

**Depends on:** [U-RT-47 (the landed `harness-inspect` admin surface), U-OD-55 (cross-axis: OD — the verification API this surface invokes)].

**Files affected (logical):** the `harness_runtime.admin.inspect` surface + its CLI/config input parsing. Plus (codex round-8 P1): the composition-root adapter module injecting the real U-OD-55 verifier into the §20.3.1 CP walk (the CP v2.38 co-land pin's runtime-owned half).

**Acceptance criteria:**

1. The inspect surface accepts the FIVE operator-supplied §13.5 inputs: (i) audit sidecar path (resolved like the existing §13 ledger/collector paths — PATH_CLASS_REGISTRY default, operator-overridable); (ii) expected tenant scope (normalization happens INSIDE the OD API, never in the CLI); (iii) verification backend / key mapping (the operator-supplied form of the §21.2.2 row-1 per-row resolver — NOT a single backend); (iv) the authenticated cutover record; (v) the authoritative persona-tier / `RuntimeConfig` input (the inspector runs against a STOPPED harness and cannot otherwise distinguish MTC's mandatory posture from lower tiers').
2. At MULTI_TENANT_COMPLIANCE, backend inputs ((iii)+(iv)) are REQUIRED, OR the inspection result is an EXPLICIT `UNVERIFIED` disposition with a NONZERO exit — silent hash-only success PROHIBITED. ABSENT an authoritative persona-tier/RuntimeConfig input, the inspection reports explicit `UNVERIFIED` with a NONZERO exit (fail-safe — the RuntimeConfig default tier is SOLO_DEVELOPER, so an unconfigured MTC inspection must not silently pass; codex round-6 P1). ONLY with a supplied authoritative config showing a sub-MTC tier and no verification inputs is the pre-v1.101 hash-only inspection behavior PRESERVED VERBATIM.
3. The §13 read-only invariant holds over the new inputs: verification is a READ; `harness-inspect` MUST NOT write to any file (the chmod-readonly fixture discipline extends over the new inputs).
4. *(Implementation discretion per §13.5's deferred list — the plan pins behavior only; NON-BINDING name suggestions: flags `--audit-sidecar` / `--expected-tenant` / `--signing-key-map` / `--cutover-record` / `--runtime-config`; fail-class `RT-FAIL-AUDIT-UNVERIFIED`; report composed with the existing `--json` output mode.)*

- CP-WALK ADAPTER (codex round-8 P1 — the runtime-owned half of CP v2.38's §3 row-1 mediation): this unit BUILDS the composition-root adapter that wraps the real U-OD-55 verifier in the CP-owned Protocol (maps `AuditSignatureInvalid` → the CP invalid signal; the OD typed availability error → the CP availability type; anything else propagates unwrapped) and INJECTS it wherever the §20.3.1 walk is invoked (the inspect wiring is the first production injection site) — without this criterion the walk would report INCOMPLETE/UNVERIFIED forever. Depends on U-CP-44/U-CP-45 (the Protocol + result boundary) and U-OD-55 (the verifier).

**Tests (mutation-probed per PD-8):** **Witness (d) — inspect UNVERIFIED-nonzero:** `test_mtc_inspection_without_backend_inputs_exits_nonzero_with_explicit_unverified_disposition` (never silent hash-only success), `test_lower_tier_with_authoritative_config_no_inputs_preserves_hash_only_verbatim`, `test_absent_authoritative_config_reports_unverified_nonzero` (mutation probe: defaulting the tier to SOLO_DEVELOPER when the config input is omitted fails the test), `test_inspect_verification_writes_nothing_readonly_fixture`, `test_rt138_adapter_real_od_verifier_through_walk` (integration: the real U-OD-55 verifier through the adapter through the §20.3.1 walk — invalid signature FAILS the walk; the OD typed availability error surfaces as CP availability, not a verdict; a defect raise propagates unwrapped; pairs with the CP v2.38 witness of the same name). **Forged-record rejection (codex round-3 P1, §13.5 row 4):** `test_forged_cutover_record_rejected_typed_never_treated_as_absent` — a cutover record failing authentication against the operator-designated record-signing key (or out-of-band anchor) is REJECTED with a typed error by BOTH the inspect verification path AND the `harness migrate-audit-sidecar` retag mode (mutation probe: downgrading the rejection to absent-record fallback fails the test — a forged record must never drive exemption, era selection, or retagging).

**Rollback boundary:** revert the inputs + disposition; MTC inspection silently presents tampered signature metadata as a passing hash-only audit — the row-8 prohibition reopens.

---

### §1.6 U-RT-102 AMENDMENT — B-53 `harness migrate-audit-sidecar` subcommand (rider surface F; fork gate item 7)

The v2.31 U-RT-102 body (Typer parent app + subcommand stubs) is PRESERVED VERBATIM; v2.49 adds:

**Implements (addition):** + Runtime spec v1.101 §13.4 (the NEW `harness migrate-audit-sidecar` inventory row; subcommand-count invariant 5 → 6).

**Acceptance criteria (v2.49 additions):**

- `harness migrate-audit-sidecar` is registered under the existing flat `harness <subcommand>` namespace (the committed Q-J=(a) command model; NO nesting) and DISPATCHES to the EXISTING B-47 migration module `main` (`harness_runtime.admin.migrate_audit_sidecar`) — the `python -m` module path stays as the implementation; no logic is duplicated into the CLI layer.
- The §13.4 subcommand-structure invariant holds at 6 flat subcommands; the Track A hyphenated standalone binaries are untouched.

- NEW (codex round-1 P1 on the apply PR): the subcommand additionally carries the OD v1.34 §21.2.1 row-6 RETAG mode — it retags each NAMED row's sidecar `tenant_tag` from `"_single"` to the record's attested `tenant_scope` (entry content and `entry_hash` byte-unchanged — the tag lives in the sidecar wrapper outside the hash), making the rows reachable by `read_full_entries_for_tenant(tenant)` for §21.2.2 verification; rows NOT named by the record are NOT retagged.
- IS-IDENTITY COHERENCE (codex round-7 P1): the sidecar tag participates in the audit identity invariant — `audit_writer._action_id_for` embeds the tag in the immutable IS action id, and `_assert_is_refs_covered_locked` joins IS references to sidecar identities on `(tag, entry_hash)` — so retagging the sidecar row ALONE would make every `("_single", hash)` IS reference report truncated history at the next refold/append. The migration MUST keep the join coherent via the ALIAS mechanism — record a per-row alias `("_single", entry_hash) → (tenant_scope, entry_hash)` that the coverage assert (and any identity join) consults; REWRITING the paired IS-reference identity is PROHIBITED (codex round-8 P1: the `audit:<tag>:<hash>` action id participates in the entry response hash and every later state-ledger entry chains to it — an in-place identity rewrite would rewrite the immutable ledger and all descendant hashes, destroying the tamper-evidence chain; the alias is the only append-only-compatible mechanism); witness `test_post_retag_refold_and_append_report_full_history` (post-retag, `_assert_is_refs_covered_locked` passes and a refold/append sees the complete history — mutation probe: retagging only the sidecar row fails the test).
- AUTHENTICATION IS U-RT-102's OWN OBLIGATION (codex round-5 P1): BEFORE any retag, the subcommand VALIDATES the cutover record's trust anchor per Runtime §13.5 row 4 (the operator-designated record-signing key — a reserved row-3-mapping entry distinct from row-derived keys — or the out-of-band anchor supplied with the record); a record failing authentication is REJECTED with a typed error and ZERO tags are changed (never treated as absent, never partial). The forged-record witness `test_forged_cutover_record_rejected_typed_never_treated_as_absent` binds HERE (the retag half) as well as at U-RT-138 (the inspect half) — mutation probe: removing the U-RT-102-side validation while U-RT-138's passes fails the retag-mode case.

**Tests (v2.49 additions — mutation-probed per PD-8):** **Witness (e) — migrate-audit-sidecar subcommand:** `test_harness_migrate_audit_sidecar_dispatches_existing_module_main_under_flat_namespace`. **Witness (f) — `_single`-history retag:** `test_retag_named_rows_reachable_by_tenant_read_content_and_hash_unchanged` (post-retag, the named rows are returned by `read_full_entries_for_tenant(attested_tenant)` with byte-identical entry content + `entry_hash`; an UNNAMED `"_single"` row is NOT retagged and is absent from that read — mutation probe: dropping the named-rows filter or mutating entry content fails the test).

---

## §2 DAG topology delta (v2.48 → v2.49)

Five new units; acyclic (Kahn-verifiable):

```
L0-within-delta: U-RT-134 (← U-RT-103 prior-landed; + U-OD-30 cross-axis, see Also line)
L1-within-delta: U-RT-135 (← U-RT-134), U-RT-136 (← U-RT-134 + U-CP-73 cross-axis)
Independent:     U-RT-137 (← U-CP-72, U-OD-30 cross-axis), U-RT-138 (← U-RT-47 prior-landed + U-OD-55 cross-axis + U-CP-44/U-CP-45 cross-axis — the injected-verifier Protocol + CP-owned result boundary it adapts and integration-tests)
Also:            U-RT-134 (← U-OD-30 cross-axis — bootstrap tenant validation DELEGATES to the OD-exported normalizer)
Amended:         U-RT-102 (← U-RT-138 partial — the §13.5 row-4 record-authentication component; otherwise dispatch to a landed module)
```

Cross-axis edges: U-RT-134 → U-OD-30 (OD — normalizer delegation, codex round-7); U-RT-136 → U-CP-73 (CP); U-RT-137 → U-CP-72 (CP), U-OD-30 (OD); U-RT-138 → U-OD-55 (OD), U-CP-44/U-CP-45 (CP — injected-verifier Protocol + result boundary, codex round-7). Co-land pins per §0.4 (one impl arc per fork gate item 10). All prior edges + acyclicity PRESERVED VERBATIM.

---

## §3 Coverage matrix delta (v2.48 → v2.49)

| Spec surface (Runtime v1.101) | Units covering |
|---|---|
| §3 C-RT-03 `audit_signing_fail_closed` field row + MTC config-validation invariant (i)–(iii) + `tenant_id` row amendment (surfaces A + B) | U-RT-134 |
| MTC prewarm/keepalive disable — v1.99 B-18-KEEPALIVE contract amendment (surface C) | U-RT-135 |
| Ten-handler flag consult + post-effect catch-ordering fence wiring (surface D, wiring half) | U-RT-136 |
| Tenant threading at converter-based call sites (surface D, tenant half) | U-RT-137 |
| NEW §13.5 C-RT-13 verifier inputs + §13 inspect exit-contract amendment (surface E) | U-RT-138 |
| §13.4 `harness migrate-audit-sidecar` row + count invariant 5 → 6 (surface F / B-53) | U-RT-102 (amended) |

All six v1.101 Runtime-owned surfaces covered ≥ 1 unit; every new unit traces ≥ 1 spec surface. ✓

---

## §4 Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_49.md` (delta over v2.48) |
| Authored at | Phase 7 — B-51/B-52/B-54 OD audit-signing amendment arc apply leg (2026-07-18) |
| Authoring authority | Runtime spec v1.101 (change-note + NEW §13.5 + §3 C-RT-03 rows, `Spec_Harness_Runtime_v1.md`) + `.harness/class_1_fork_b51_b52_b54_od_signing_amendment_arc.md` (RATIFIED 2026-07-18, all ten gate items AS RECOMMENDED; dyads 1–3 all-CONFIRM) |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_48.md` (v2.48 — R-plan-1 U-RT-132/133) |
| Siblings (same arc) | `Implementation_Plan_Operational_Discipline_v2_29.md` + `Implementation_Plan_Control_Plane_v2_38.md` |
| Revision policy | Delta-only per workspace `CLAUDE.md` §2.4; revisions route to design-phase back-flow |
