# Council dyad records — B-51/B-52/B-54 apply leg (Arc A) · 2026-07-18

Three dyadic convenings per CLAUDE.md §10.9 + the ratified filing's final section (dyads 1+2 REQUIRED; dyad 3's blocking condition MET by gate item 5). Each dyad ran as a dedicated agent adopting the two voice SKILL.md files, grounded in the ratified filing + current spec heads + on-main code probes. ALL verdicts CONFIRM, ZERO deviations; five precision notes carried into the OD v1.34 / CP v1.101 / Runtime v1.101 deltas. Condensed records below; full deliberations at the session transcript.

# Dyad 1 — B-51 leg 1 · C7 (primary) ⊥ C2 (consultant) · 2026-07-18

VERDICT SUMMARY: all nine leg-1 finalized requirements CONFIRM; no DEVIATION; no unresolved TENSION (pre-named bind-everything vs message-minimal tension dissolved on probing).

Key probes (verified on main by the dyad agent):
- `harness-od/src/harness_od/multi_tenant_trace_separation_and_audit_ledger.py:234` — `sign_audit_entry(payload, key_id, algo, *, backend=None)` tenant-less; `_canonical_od_signing_message` ~:217-231 joins exactly four length-prefixed segments.
- `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py:311` — unsigned plaintext sidecar `tenant_tag`; :563-581 writer normalizes `None -> "_single"`.
- Length-prefix encoding keeps four/five-tuple cutover INJECTIVE (probe-resolved; B-22/B-31 byte-compat precedent transfers).
- `cost_attribution_f2_write.py:65` — cost family already transitively tenant-bound via entry_core (per-family exception real).
- `redaction_token_audit_map.py:44/:115/:131` — redaction path holds `_tenant_id`, calls compose directly.
- `llm_dispatch.py:849` prewarm signs `tenant_id=None` (gate item 8 disable removes the path); `llm_dispatch.py:1770` `step_context.tenant_id` in scope at converter production sites.
- `sign_rotation_pair` at `multi_tenant_trace_separation_and_audit_ledger.py:366` — no tenant, `backend=None`; MTC prohibition until B-33 confirmed as only coherent choice.
- Zero `MULTI_TENANT_COMPLIANCE` conditional validation under `harness-runtime/src/harness_runtime/config/`; `tenant_id` plain optional at `config/loader.py:72` — bootstrap invariant gap REAL.
- CP §13.5.1 at `Spec_Control_Plane_v1_7.md:55-62` — converter signs INSIDE, tenant-less; rider placement (CP-owned amendment) correct.

PRECISION NOTE for the spec-writer apply pass (jointly held, within ratified shape):
The OD v1.34 delta MUST pin the fifth segment's representation to a single source of truth shared with the sidecar join key — bind the writer-normalized tenant TAG (`_tenant_tag` normalization at audit_writer.py:563-581) or specify the normalization the leg-3 verifier applies. Do NOT leave "tenant scope token" representation-ambiguous between raw `RuntimeConfig.tenant_id` and the normalized tag; two representations reconciled at verify-time would be a synchronized-copy seam (one-source-of-truth violation).

---

# Dyad 2 — B-52 leg 2 · C7 (primary) ⊥ C9 (consultant, C1 noted inline) · 2026-07-18

VERDICT SUMMARY: all eight leg-2 finalized requirements CONFIRM; no DEVIATION; one TENSION surfaced + probe-resolved.

Key probes (verified on main by the dyad agent):
- §28.10.4 invariant 2 byte-exact at `Spec_Control_Plane_v1_24.md:135` ("Hook exceptions MUST be swallowed") — TWO-SPEC shape structurally necessary.
- OD v1.8 precedent byte-exact at `Spec_Operational_Discipline_v1_8.md:257` ("operator-configurable; default fail-closed = raise").
- EXACTLY ten `except AUDIT_SIGNING_HARD_FAILURES` handlers on main: hitl_gate_composer.py:1050,1269 · sub_agent_dispatch.py:757 · webhook_delivery_composer.py:334,406 · runtime_tool_dispatcher.py:567,649 · llm_dispatch.py:2953,3046 · cost_attribution_validator_dispatch.py:413.
- `audit_signing_errors.py:48` — typed set only 2 types; untyped backend ValueError/TypeError escapes every enumerated catch (single-typed-boundary requirement REAL).
- Redaction 11th path: `redaction_span_processor.py:~310` swallows (KeyError, TypeError) and leaves the RAW value exportable on tokenize failure — unconditional fail-closed confirmed necessary.
- Zeroth site: `multi_tenant_trace_separation_and_audit_ledger.py:283` returns `unsigned:*` placeholder WITHOUT raising — bootstrap invariant load-bearing.
- Prewarm 12th path: `llm_dispatch.py:728` never-raises docstring + keepalive SECOND swallow at `cli/app.py:417-419`.
- `retry_breaker_fallback.py:265` — all other Exceptions -> TRANSIENT_RETRY; signing failure would re-fire a PAID provider call; reclassification alone still advances candidates + corrupts breaker stats -> BYPASS is the only breaker-fidelity-preserving mechanics.
- TENSION (C7 fail-closed span-end vs C9 hot-path stall): probe-resolved at `audit_signing_errors.py:40-51` — the signing-side breaker makes sustained-KMS-outage failure fast+typed (AuditSigningBreakerOpenError in the typed set). No design change.

SPEC-WRITER NOTES (within ratified shape):
1. The Runtime rider's MTC disable language MUST cover the keepalive LOOP (`app.py:391-427`) as a contract term, not only the `prewarm()` entry point — otherwise the 13th swallow boundary is unreachable only by coincidence of call order.
2. C1 catch-ORDERING requirement: `AUDIT_SIGNING_HARD_FAILURES` must be caught AHEAD of the generic per-attempt classifier catch in `_run_per_candidate_attempts` (`retry_breaker_fallback.py:837`), result-preserving; same fence at every post-effect site (tools/webhooks execute before attribution).

PLAN-DELTA NOTE:
3. Runtime plan delta carries as acceptance criterion: dual env-loader registration for `audit_signing_fail_closed` (`_ENV_SCALAR_FIELDS` + `_RuntimeEnvSettings`) — the known dropped-env-override defect class.

---

# Dyad 3 — B-54 leg 3 · C7 (primary) ⊥ C9 (consultant, C1 noted inline) · 2026-07-18

VERDICT SUMMARY: all twelve leg-3 finalized requirements CONFIRM; no DEVIATION; one TENSION surfaced + probe-resolved (blocking §20.3.1 walk vs non-blocking OD default occupy DISJOINT invocation surfaces — read-path audit protocol with §4.1.28 operator-escalation recovery vs dispatch hot path with zero verification callers).

Key probes (verified on main by the dyad agent):
- `verify_audit_entry_signature` (`harness-cp/src/harness_cp/f5_signing_key_resolution.py:381`, backend.verify at :451) has ZERO production callers repo-wide — the sidecar's recoverability has no consuming contract.
- `verify_hash_chain_integrity` (`multi_tenant_trace_separation_and_audit_ledger.py:320`) + B-49 `per_family_audit_verification.py`: content+linkage only, zero signature references.
- v1.33 signs the FOUR-tuple today (:295-304, key_period=0) — without the message-format cutover, honest pre-v1.34 history reads as tampering.
- `read_full_entries_for_tenant` (`audit_writer.py:1159`) returns bare entries; tenant_tag stripped (sidecar wrapper :311); `AuditSignatureAttributes` has no tenant field — tenant scope as verifier INPUT structurally required.
- `legacy_baseline` rows = identity pairs, entries unrecoverable (`audit_writer.py:1088-1092`, 862-871); signature_attrs sit OUTSIDE entry_hash — exemption must be content-bound signed triples, never signature-value-shape-keyed.
- `HashChainBreach` (:342/:352) is content/linkage-specific — taxonomy split preserves the trust-property discriminator.
- `admin/inspect.py` checks zero signatures; Runtime §13/§13.4 carries none of the verifier inputs — C-RT-13 rider inputs required or the impl arc invents an unratified CLI surface (X-AL-3).
- §20.1 row 3 (CP v1.2, preserved verbatim to v1.100 per v1.98 line 39) admits no unsigned MTC entry — narrow cutover-scoped historical exception needed for contract/behavior byte-consistency.
- Breaker wrapper instruments sign but passes verify straight through (`harness-runtime/src/harness_runtime/config/audit_signing.py:204-207`) — INTENTIONAL asymmetry, correct under taxonomy branch (b).

SPEC-WRITER NOTE (within ratified shape):
One line of rider prose pinning the sign-instrumented / verify-passthrough breaker asymmetry as intentional (verify-side availability errors are caller-retryable infrastructure failures that must not pollute the signing breaker's dispatch-relevant state) — so a future arc does not "fix" it into breaker-coupling the read path.
