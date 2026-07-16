# ADR-D5: HITL synchrony — four-response palette with synchrony class parametric on persona-tier × D1-engine-class

## Status

Accepted
Date: 2026-05-10
Phase: 3b Stage 1 (per `Project_Workflow_v1_1.md` §2.3.3)
Promotion path: Accepted at P3-CK clearance per Workflow v1.1 §3.1
Revision: v1 → v1.1 (P3c-CK iter-1 close mechanical revision per Path A — F2-06 hitl.* attribute prefix discipline at §1.8; F2-08 audit.* attribute names back-declared at §1.4 source via new §1.4.1 sub-section) → v1.2 (P3c-CK iter-1 close council-orchestrator substantive revision — F2-13 signing-key resolution at §1.4 multi-tenant-compliance row composing with ADR-F5 secrets bridge; F2-15 permanent-fail-vs-transient discriminator at §1.10 pre-HITL escalation order; new §1.10.1 sub-section declaring `validator.fail.*` attribute substrate) → v1.3 (P3c-CK iter-2 close revision per `Project_Workflow_v1_2.md` §4.1.2 path — F2-iter2-02 cross-namespace canonical-naming resolution under operator-selected Reading 1 canonical pass-through: drop `hitl.gate.tool` and `hitl.gate.mcp_server` at §1.8; gate-event consumer reads canonical attributes `gen_ai.tool.name` per OTel GenAI semconv 1.41.0 and `mcp.server.name` per ADR-D3 v1.1 §1.8.1 via trace correlation; F2-iter2-03 secret_rotation_event dual-signature sqlite schema specification under operator-selected Option (a) two-row pattern: §1.4 sqlite schema extended with `rotation_correlation_id` column joining the two rotation-pair entries that together carry the dual signature) → v1.4 (Phase-7 audit-ledger storage-form reconciliation — U-RT-59 Fork 2 drift-resolution Path B-revised-a; 2026-05-20) → **v1.5 (`B-36`/`ADR-D8` cross-reference — §1.4 row 3's F5-prod-tech deferral resolved for the AWS case; 2026-07-16)**
Revision date: 2026-07-16 (v1.5 — prose-only cross-reference addition, no table structure/row/column change; Phase-7 in-CLI per workspace `CLAUDE.md` §4.3)
Promotion: P3c-CK final clearance — 2026-05-11

## Change-note (v1 → v1.1)

**Scope of revision.** Two-finding mechanical-alignment revision pass clearing `Adversarial_Review_3c.md` F2-06 (Pattern P1 attribute prefix drift — hitl.* span events declared at §1.8 with un-prefixed per-event attributes; D6 §1.2 declares prefixed `hitl.gate.level` / `hitl.response.class`) and F2-08 (Pattern P1 concept-vs-attribute split — `audit.*` attribute names introduced at D6 §1.2 without back-declaration at D5 source). §1.8 span attribute table rewritten with per-event-namespace prefix discipline; new §1.4.1 sub-section declares the three `audit.*` span attribute names (`audit.signature.sha256`, `audit.signature.prior_hash`, `audit.actor.id`) with explicit mapping to the §1.4 per-persona-tier ledger cryptographic shape table. ADR-D6 §1.2 rows `hitl.*` and `audit.*` read from D5 v1.1 declarations after this revision; the per-attribute set at D6 §1.2 is unchanged.

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_2.md` §3.1 — promotion to `Accepted` blocked until P3c-CK clearance. D5 v1.1 enters P3c-CK iteration 2 as input artifact alongside D1 v1.1 and the other revised D-ADRs (D2 v1.1, D3 v1.1, D4 v1.1, D6 v1.1).

**Sections preserved verbatim.** §1.1 four-response palette; §1.2 synchrony-class × HITL-primitive-shape matrix; §1.3 three-placement HITL topology primitive (incl. §1.3.1 + §1.3.2); §1.4 per-persona-tier ledger cryptographic shape table (rows + columns + values); §1.5 T-perm-1 D5-layer composition rule (incl. §1.5.1 + §1.5.2); §1.6 composition with reliability primitives; §1.7 persona-tier-binding-time selection contract; §1.9 composition with eval methodology; §1.10 composition with model routing; §1.11 context revalidation on HITL resume; Rationale (all sub-sections); Consequences (all sub-sections); Alternatives considered; References Substrate dependency declaration + Pattern Reference Catalog citations + Per-axis recommendation citation + Parent F-ADR/D-ADR citations + Persona document trace + Substrate research citations + Convening artifact citations.

**Changes inline.** Status block (Revision / Revision date lines added). This Change-note section. §1.4.1 sub-section inserted immediately after §1.4 table (before §1.5). §1.8 span attribute table rewritten in place (event names unchanged; per-event attributes prefixed). References "Workflow and skill discipline references" extended with new entries (Workflow v1.2 §3.1, Workflow v1.2 §4.1.2, spec-writer skill, Adversarial_Review_3c.md F2-06/F2-08, Phase 3c-CK iteration 1 close handoff §4.1). Closing footer revised to note v1.1 filing.

**F2-06 mechanical-prefix rule applied.** Each attribute under a `hitl.*` event inherits the event-namespace as its prefix. Where D6 §1.2 already declares a canonical attribute name (`hitl.gate.level` cardinality-safe metric dimension; `hitl.response.class` ∈ approve/edit/reject/respond per §1.1 four-response palette), D5 v1.1 uses D6's declared name. Where no D6 declaration exists, the event-namespace prefix is applied directly (`hitl.invocation.placement`, `hitl.timeout.duration_ms`, etc.). Attribute semantics are unchanged; only naming aligns.

**Open scoping question surfaced for next-revision attention (NOT addressed in this revision).** `tool` and `mcp_server` attributes under `hitl.gate.evaluated` are mechanically prefixed to `hitl.gate.tool` and `hitl.gate.mcp_server` per F2-06's prefix-discipline rule. A semantically richer alignment would route these through OTel-canonical `gen_ai.tool.name` and ADR-D3 `mcp.*` namespaces respectively (since the gate-evaluation references the same tool / MCP server identities the tool-call span itself carries). This is a substantive content decision beyond F2-06's mechanical scope and is surfaced here for iteration-2 adversarial review attention; if the reviewer flags it as a finding, a future D5 revision will resolve it via cross-namespace canonical-naming.

**Deferred — F2-13 and F2-15 NOT addressed in this revision.** `Adversarial_Review_3c.md` F2-13 (signing-key resolution at §1.4 multi-tenant-compliance row not specified — F5 secrets bridge composition + signature algorithm specification missing; §References Shape 4 add F5) and F2-15 (D5 §1.10 pre-HITL escalation order does not distinguish permanent-fail from transient — D2 §1.8 explicit handling vs D5 source ADR lacks anchor) are the substantive content additions for D5 paired with F2-06 + F2-08 in the iteration 1 close handoff §4.1. Both route to a separate `council-orchestrator` session per §5.1: F2-13 is C11 (operator/local; signing-key resolution) + C10 (action-safety; signature algorithm) cross-voice; F2-15 is C5 (validation-contract; permanent-fail taxonomy) anchor with C9 (reliability/recovery; transient-vs-permanent classification) consultant. F2-06 + F2-08's mechanical attribute-name discipline is the prerequisite for F2-13's and F2-15's content additions — once `audit.*` attributes are declared at the source D-ADR and `hitl.*` attribute prefix is consistent, F2-13 extends the `audit.*` namespace at D5 §1.4.1 and F2-15 introduces a new `validator.*` namespace at D5 §1.10.1; F2-06 + F2-08 close before F2-13 + F2-15 to avoid namespace-rework collision.

## Change-note (v1.1 → v1.2)

**Scope of revision.** Two-finding substantive content addition revision pass clearing `Adversarial_Review_3c.md` F2-13 (signing-key resolution at §1.4 multi-tenant-compliance row not specified — F5 secrets bridge composition + signature algorithm specification missing) and F2-15 (D5 §1.10 pre-HITL escalation order does not distinguish permanent-fail from transient — D2 §1.8 explicit handling vs D5 source ADR lacks anchor). §1.4 extended with signing-key resolution prose composing against ADR-F5; §1.4.1 extended with four new `audit.signature.*` attribute declarations (`audit.signature.value`, `audit.signature.algorithm`, `audit.signature.key_id`, `audit.signature.key_period`) accreting onto the v1.1-declared three; §1.10 pre-HITL escalation order replaced with discriminated five-class encoding aligning to the locked C5 retry-exit taxonomy (per `c5-validation-contract` SKILL.md s14 §7.5(d) reconciliation); new §1.10.1 sub-section declares the `validator.fail.*` attribute substrate (`validator.fail.class`, `validator.fail.cause_attribution`, `validator.fail.permanence`); §References Shape 4 extended with ADR-F5 citation per F2-13 explicit requirement and ADR-D2 §1.8 citation per F2-15 precedent shape.

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_2.md` §3.1 — promotion to `Accepted` blocked until P3c-CK clearance. D5 v1.2 enters P3c-CK iteration 2 as input artifact alongside the other revised D-ADRs.

**Sections preserved verbatim.** §1.1 four-response palette; §1.2 synchrony-class × HITL-primitive-shape matrix; §1.3 three-placement HITL topology primitive (incl. §1.3.1 + §1.3.2); §1.4 per-persona-tier ledger cryptographic shape table proper (the 3-row table — preserved verbatim; signing-key resolution prose appended below the table, table content unchanged); §1.5 T-perm-1 D5-layer composition rule (incl. §1.5.1 + §1.5.2); §1.6 composition with reliability primitives; §1.7 persona-tier-binding-time selection contract; §1.8 composition with observability (v1.1 prefixed-attribute table preserved verbatim); §1.9 composition with eval methodology; §1.10 §1.10 prose preserved EXCEPT the pre-HITL escalation order code block which is replaced with discriminated five-class encoding (§1.10's persona-tier × summarization-model table preserved verbatim); §1.11 context revalidation on HITL resume; Rationale (all sub-sections); Consequences (all sub-sections); Alternatives considered; References Substrate dependency declaration + Pattern Reference Catalog citations + Per-axis recommendation citation + Persona document trace + Substrate research citations + Convening artifact citations from v1 + v1.1.

**Changes inline.** Status block (revision-history line consolidated to v1 → v1.1 → v1.2). This Change-note section appended after the v1 → v1.1 Change-note. §1.4 prose extended with signing-key resolution paragraph below the table (before §1.4.1). §1.4.1 attribute set extended with four new declarations (existing three preserved verbatim; deferral paragraph at §1.4.1 close updated to reflect F2-13 closure). §1.10 pre-HITL escalation order code block replaced with discriminated five-class encoding. §1.10.1 sub-section inserted after §1.10, before §1.11. References Shape 4 extended with F5 + D2 §1.8 citations. References "Workflow and skill discipline references" extended with v1.2-related entries (council-orchestrator skill applied at v1.2 authoring; Adversarial_Review_3c.md F2-13/F2-15 entries; Phase 3c-CK iter-2 pre-entry handoff). References "Convening artifact citations" extended with v1.2 council-orchestrator session reference (F2-13 + F2-15 deliberation). Closing footer extended with v1.2 filing.

**F2-13 substantive resolution applied.** Signing-key resolution composes against ADR-F5's `fetch_secret(name, scope) -> SecretRef` abstraction — signing key is treated as a secret resolved through F5's tier-aware abstraction (F5 dev-tech OS keychain at team-binding; F5 prod-tech vault deferred to D-ADR at multi-tenant-compliance). Signature algorithm: Ed25519 default with operator-tunable axis `audit_signature_algorithm ∈ {ed25519 / ecdsa-p256 / rsa-pss-2048}` at deployment-binding-time. Rotation: key-period model (each ledger entry carries `audit.signature.key_period`; chain continuous across rotations; `secret_rotation_event` entry counter-signed under outgoing + incoming keys when the rotated secret IS the audit-signing key, single-signed under current key for all other rotations). Cross-deployment transition: mandatory-HITL trigger per s13 §4.11; chain preserved with verifier reading `key_period` to apply correct verification key. Signing-key residence per persona tier — the per-deployment-vs-per-tenant scope choice at multi-tenant-compliance is operator-tunable at multi-tenant-binding-time (`audit_signing_key_scope ∈ {deployment / tenant}`) per Persona §11.10 multi-tenant tenant-isolation deferral; the v1.2 commitment is the tunable axis, not a default-binding pick. Council convening per `council-orchestrator` skill: C11 (primary anchor; signing-key residence + sqlite schema extension), C10 (co-primary; signature-algorithm trust-boundary), C3 (consultant; F2 state-ledger composition), C7 (consultant; attribute schema accretion).

**F2-15 substantive resolution applied.** Pre-HITL escalation order at §1.10 discriminates by C5 fail-class (locked five-class retry-exit taxonomy per s14 §7.5(d) reconciliation: `transient-retry` / `Reflexion-recoverable` / `HITL-recoverable` / `permanent-fail-exit` / `terminal-fail-exit`). Transient-retry and Reflexion-recoverable classes traverse the staircase (1st→retry→2nd→model-tier-escalation→3rd→HITL); HITL-recoverable routes to validator-HITL placement per s14 §4.1.6 (palette {approve / request-changes / reject}); permanent-fail-exit and terminal-fail-exit SKIP the staircase and route directly to validator-escalation HITL placement per §1.3 (palette {approve / edit / reject / respond} per s14 §4.1.8, restricted to {approve / reject / respond} when composing with cross-trust-boundary actions per s14 §7.10(d)). Permanent-fail-exit classification originates with C5 emitting `validator.fail.class=permanent-fail-exit` plus `cause_attribution` annotation per s12 §7.5(a); C9 owns the parallel retry-budget-exit exit condition that also routes to staircase-skip. The 2nd-rung branch in the transient staircase (model-tier escalation OR re-prompt-with-different-system-prompt per Cluster 4 §2.2.3 [HIGH]) is cause-attribution-conditioned — model-tier escalation fires on `model_misfire` / `provider_outage` / `capability_shortfall`; re-prompt-with-different-system-prompt fires on `semantic_disagreement` / `contract_violation` if not yet routed to Reflexion. The discriminated encoding aligns D5 §1.10 with the precedent shape committed at ADR-D2 v1 §1.8 ("Permanent-fail violations skip the staircase and go directly to HITL"); D2 v1 §1.8 cross-D-ADR composition citation added to §References Shape 4 per F2-15. Council convening per `council-orchestrator` skill: C5 (primary anchor; five-class taxonomy), C9 (co-primary; retry-budget vs permanent-fail; trigger vocabulary), C6 (consultant; model-tier-escalation bypass), C11 (consultant; palette under permanent-fail), C10 (consultant; HITL trigger catalog composition).

**Cross-finding integration.** F2-13 + F2-15 are independent in their primary substrates but compose at two interaction surfaces: (a) permanent-fail-exit ledger entries use the same audit-signing key as all other ledger entries — no permanent-fail-specific signing path; (b) each HITL invocation under permanent-fail-exit writes a ledger entry that must be signed per F2-13's resolution. Both interactions are containment-of-existing-shape (no new tension; T-perm-1 / T-perm-2 / T-perm-3 unchanged); the spec-writer ingests both findings as v1.2 amendments without ledger updates.

## Change-note (v1.2 → v1.3)

**Scope of revision.** Two-finding revision pass clearing `Adversarial_Review_3c_iter2.md` F2-iter2-02 (Class 2 — D5 §1.8 cross-namespace canonical-naming: `hitl.gate.tool` and `hitl.gate.mcp_server` event-scoped attributes reference the same identities as `gen_ai.tool.name` per OTel GenAI semconv 1.41.0 and `mcp.server.name` per ADR-D3 v1.1 §1.8.1 on parent tool-call / mcp-tool-call spans; the v1.2 prose at §1.8 closing paragraph deferred resolution to iter-2 adversarial review attention) and F2-iter2-03 (Class 2 — D5 §1.4 secret_rotation_event dual-signature sqlite schema not specified: the §1.4 prose committed counter-signing under outgoing + incoming keys when the rotating secret IS the audit-signing key, but the §1.4 sqlite schema extension table declared only three signature columns without specifying how the dual-signature entry is stored). §1.8 `hitl.gate.evaluated` row revised to drop `hitl.gate.tool` and `hitl.gate.mcp_server` under operator-selected Reading 1 (canonical pass-through); §1.8 closing paragraph rewritten to document canonical-attribute reference via trace correlation. §1.4 sqlite schema extension table extended with `rotation_correlation_id` column under operator-selected Option (a) (two-row pattern); new paragraph after the population paragraph documents external-auditor verification semantics for the dual-signed rotation entry pair. §References Shape 4 extended with OTel GenAI semconv 1.41.0 citation per F2-iter2-02 Reading 1 closure and refined ADR-D3 v1.1 §1.8.1 citation for `mcp.server.name` canonical attribute source.

**F2-iter2-02 resolution applied under operator-selected Reading 1 (canonical pass-through).** Per `ask_user_input_v0` elicitation at P3c-CK iter-3 revision-pass session entry (selection: Reading 1 — canonical pass-through; drop event-scoped names, gate-event references parent span attributes via trace correlation, Pattern P1 unity). §1.8 `hitl.gate.evaluated` row at v1.3: `hitl.gate.tool` and `hitl.gate.mcp_server` attributes retired; the gate-event consumer reads the gated tool's name from `gen_ai.tool.name` on the parent `tool.call` span (canonical per OTel GenAI semconv 1.41.0) and the gated MCP server's identity from `mcp.server.name` on the parent `mcp.tool.call` span (canonical per ADR-D3 v1.1 §1.8.1). Trace correlation requires the gate-event's trace context to include the parent span; the gate-event-emission-time discipline at the harness ensures parent-span attributes are populated before gate evaluation completes. The v1.2-declared event-scoped attribute set on `hitl.gate.evaluated` (`hitl.gate.level`, `hitl.gate.persona_tier`, `hitl.gate.required`) is preserved; only the two parent-span-referenced attributes are dropped. D6 §1.2 row `hitl.*` ingestion contract at D6 v1.1 (filed under the parallel iter-3 D6 v1.1 revision pass) enumerates the four event names from D5 v1.3 §1.8 verbatim; the attribute-name set on `hitl.gate.evaluated` reduces from five at v1.2 to three at v1.3.

**F2-iter2-03 resolution applied under operator-selected Option (a) two-row pattern.** Per `ask_user_input_v0` elicitation at P3c-CK iter-3 revision-pass session entry (selection: Option (a) two-row pattern — secret_rotation_event written as two ledger entries joined by a rotation-event correlation ID). The §1.4 sqlite schema extension table is extended with a fourth column `rotation_correlation_id text NULL`: NULL for all non-rotation ledger entries (the dominant case; preserves existing schema semantics for the existing v1.2 population); UUID populated and shared across the two rotation-pair entries when the secret_rotation_event materializes (one entry signed under the outgoing key at current `signature_key_period=N`, one entry signed under the incoming key at next `signature_key_period=N+1`). The pair-join via shared UUID is the structural carrier of the dual-signature commitment from §1.4 prose. Population per persona tier extends accordingly: `solo-developer` → column always NULL (no signature path); `team-binding` and `multi-tenant-compliance` → NULL for non-rotation entries, UUID for rotation-pair entries (and only when the rotating secret IS the audit-signing key; non-audit-key rotations remain single-entry per §1.4 prose). External-auditor verification semantics added as a paragraph after the population paragraph: walk the chain entry-by-entry; on encountering a non-NULL `rotation_correlation_id`, query the sibling entry with the same correlation ID; verify both entries' signatures (sibling-1 under `signature_key_period=N` using the key valid at period N, sibling-2 under `signature_key_period=N+1` using the key valid at period N+1); confirm chain hash continuity at the rotation boundary (sibling-2's `entry_hash` extends the chain from sibling-1's `entry_hash`).

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_2.md` §3.1 — promotion to `Accepted` blocked until P3c-CK clearance. D5 v1.3 enters P3c-CK iteration 3 as input artifact alongside D1 v1.1, D2 v1.1, D3 v1.1 (with iter-2 Class 1 inline fix applied), D4 v1.1, and D6 v1.1 (filed at iter-2 close per the parallel iter-3 revision-pass scope).

**Sections preserved verbatim.** §1.1 four-response palette; §1.2 synchrony-class × HITL-primitive-shape matrix; §1.3 three-placement HITL topology primitive (incl. §1.3.1 + §1.3.2); §1.4 per-persona-tier ledger cryptographic shape table proper (the 3-row table preserved verbatim); §1.4 signing-key resolution prose (v1.2 commitments preserved verbatim — signing-key residence table, signature algorithm tunable axis, key-period rotation model, cross-deployment transition discipline, HITL trigger on signing-key absence); §1.4.1 span attribute names (all seven `audit.*` attributes preserved verbatim); §1.5 T-perm-1 D5-layer multiplicative gate-level composition rule (incl. §1.5.1 + §1.5.2); §1.6 composition with reliability primitives; §1.7 persona-tier-binding-time selection contract; §1.9 composition with eval methodology; §1.10 composition with model routing (incl. v1.2 discriminated five-class encoding preserved verbatim); §1.10.1 span attribute names declared by §1.10 (`validator.fail.*` substrate preserved verbatim); §1.11 context revalidation on HITL resume; Rationale (all sub-sections); Consequences (all sub-sections); Alternatives considered; References Substrate dependency declaration + Pattern Reference Catalog citations + Per-axis recommendation citation + Persona document trace + Substrate research citations + Convening artifact citations from v1 + v1.1 + v1.2.

**Changes inline.** Status block (Revision line extended with v1.2 → v1.3; Revision date 2026-05-11). This Change-note (v1.2 → v1.3) section appended after the Change-note (v1.1 → v1.2). §1.4 sqlite schema extension table extended with `rotation_correlation_id` column row; new paragraph after the population paragraph documenting external-auditor verification semantics. §1.8 `hitl.gate.evaluated` row revised (two attributes retired); §1.8 closing paragraph at v1.2 location replaced with the Reading 1 cross-namespace canonical-naming resolution prose. §References Shape 4 extended with OTel GenAI semconv 1.41.0 citation and refined ADR-D3 v1.1 §1.8.1 citation for `mcp.server.name` canonical attribute declaration. References "Workflow and skill discipline references" extended with v1.3-related entries (`Adversarial_Review_3c_iter2.md` F2-iter2-02 / F2-iter2-03 citations; Phase 3c-CK iter-2 close → iter-3 entry operator-action guide §5.1 / §5.2 / §7.1 / §7.2 elicitation discipline; ask_user_input_v0 disposition record at iter-3 revision-pass session entry). Closing footer extended with v1.3 filing.

**Cross-finding integration.** F2-iter2-02 (cross-namespace canonical-naming at §1.8 hitl.gate.evaluated) and F2-iter2-03 (secret_rotation_event dual-signature sqlite schema at §1.4) are independent in their primary substrates — F2-iter2-02 touches the HITL-event span schema; F2-iter2-03 touches the audit-ledger sqlite schema — and compose at no shared interaction surface. Both apply under the spec-writer Path A discipline (revision pass per Workflow v1.2 §4.1.2); no council convening required at iter-3 since neither finding requires multi-voice substantive deliberation, only operator decision between pre-deliberated readings / schema shapes (elicitation, not convening). T-perm-1 / T-perm-2 / T-perm-3 unchanged; no ledger updates emitted at v1.3.

**F2-12 deferral carry-forward acknowledgement (unchanged at v1.3).** F2-12 (replay-trace-emission contract at D1) routes to a separate D1 v1.1 → v1.2 revision per the iter-1 close handoff; this work is parallel to P3c-CK iter-3 scope and does not gate iter-3 clearance. D5 v1.3 inherits this acknowledgement unchanged from v1.2.

## Change-note (v1.3 → v1.4)

**Scope of revision.** Phase-7 in-CLI revision absorbing operator-ratified **U-RT-59 Fork 2 drift-resolution Path B-revised-a** per `.harness/u_rt_59_fork_2_cp_to_od_audit_discovery.md` §10 routing (selected 2026-05-20). Fork 2 surfaced a pre-existing storage-form deviation between this ADR-D5 §1.4 (which committed SQLite persistence at all 3 persona tiers, citing `c11-operator-local` SKILL.md schema — a file not present in this workspace) and the landed code (`harness-od/src/harness_od/audit_ledger_types.py` Pydantic shapes + `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py` which wraps audit entries into the IS JSONL state-ledger per IS spec v1.3 §3 + ADR-F2). Operator-ratified Path B-revised-a: **code is canonical; ADR-D5 §1.4 amends to permit the landed storage form.**

**Two amendment sites.**

| Site | Amendment shape | Substrate source |
|---|---|---|
| **§1.4 per-persona-tier ledger cryptographic shape table (storage-form row prose)** | The "Ledger cryptographic shape" column at each of the 3 rows is **re-worded to be storage-form-flexible**: SQLite is reclassified from a v1 architectural commitment to a v1.4 C11-style D-ADR-specific persistence model (deferred to a future operator-self-redact arc); the v1.4 canonical storage form is **JSONL via IS state-ledger composition** (per ADR-F2 §Decision + IS spec v1.3 §3 JSONL commitment + landed code at `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py`). The audit-ledger entry's Pydantic shape (`AuditPayload` + `AuditSignatureAttributes` + `entry_hash`) is committed canonical at OD spec v1.5 C-OD-24 (co-published with this v1.4 amendment). Hash-chain integrity discipline (`prior_event_hash` linkage per C-IS-06) unchanged. Cryptographic signature requirement at multi-tenant-compliance (row 3) unchanged. | Operator-ratified Path B-revised-a; landed code at `audit_ledger_types.py` + `audit_writer.py`; `Spec_Operational_Discipline_v1_5.md` C-OD-24 (co-published); `Spec_Information_Substrate_v1.md` v1.3 §3 (JSONL canonical); ADR-F2 §Decision (filesystem + git + JSONL event ledger) |
| **§1.4.1 `audit.signature.sha256` recipe (canonical entry_hash)** | The "per-event SHA-256 hash over the ledger entry payload" description is **tightened**: at v1.4, "ledger entry payload" canonically means the OD `AuditPayload` Pydantic model (3 fields per OD spec v1.5 C-OD-24.1 — `entry_core`, `audit_namespace_attrs`, `prior_entry_hash`); the hash is computed as SHA-256 over `AuditPayload.model_dump_json()` (Pydantic v2 canonical JSON serialization per the OD-axis ConfigDict `extra="forbid", frozen=True` discipline). The v1.1 + v1.2 attribute declaration shape is preserved verbatim; only the "payload" referent is tightened from ambiguous to spec-anchored. | Operator-ratified Path B-revised-a Q3 ratification; landed code at `audit_ledger_types.py` `AuditPayload` shape; `Spec_Operational_Discipline_v1_5.md` C-OD-24.1 + C-OD-24.5 (co-published) |

**Sections preserved verbatim from v1.3.** §1.1 four-response palette; §1.2 synchrony-class × HITL-primitive-shape matrix; §1.3 three-placement HITL topology primitive; §1.4 signing-key resolution prose (signing-key residence table; signature-algorithm tunable axis; key-period rotation model; cross-deployment transition discipline; HITL trigger on signing-key absence; sqlite schema extension table — see "carry-forward" below); §1.4.1 attribute names (7 audit.* attributes — names preserved; `audit.signature.sha256` description tightened only); §1.5 + §1.6 + §1.7 + §1.8 + §1.9 + §1.10 + §1.10.1 + §1.11 preserved; Rationale; Consequences; Alternatives considered; References.

**§1.4 sqlite schema extension table carry-forward (Class 3 flagged).** The 4-column table at §1.4 (`signature_value` / `signature_key_id` / `signature_key_period` / `rotation_correlation_id`) commits a SQLite persistence model that is **not the v1.4 canonical storage form** (JSONL via IS composition is canonical at v1.4). The table is preserved verbatim at v1.4 as a **C11-style D-ADR deferred persistence model** — applicable if and when a future operator-self-redact / cross-deployment-monotonicity D-ADR commits to a SQLite migration. At v1.4 the equivalent column data lives as Pydantic fields on `AuditSignatureAttributes` (per ADR-D5 §1.4.1 + OD spec v1.5 C-OD-24.2). Class 3 flag: future C11-style D-ADR authoring will need to either reconcile the table with v1.4 JSONL-canonical, OR commit the SQLite migration explicitly and update v1.4 accordingly.

**Status posture.** `Status: Accepted` preserved at v1.4 (promotion happened at P3c-CK clearance between v1.3 filing 2026-05-11 and v1.4 authoring 2026-05-20; v1.4 is a Phase-7 in-CLI revision against an already-Accepted ADR, not a status-promotion event).

**v1.4 canonical scope clarification (advisor-flag close-out).** v1.4 commits JSONL via IS composition as the canonical SHAPE of audit-ledger storage — the `RuntimeAuditLedgerWriter.append(tenant_id, audit_entry)` wrap pattern at `harness-runtime/src/harness_runtime/lifecycle/audit_writer.py` is the canonical referent (per OD spec v1.5 C-OD-24 + Spec_Harness_Runtime_v1.md §6 C-RT-04). Production CALLSITE exercise of this wrap is deferred to the U-RT-59 Fork 2 implementation arc — no production callsite currently invokes `audit_writer.append` at any persona tier (verified 2026-05-20: discovery + ratified at `.harness/class_1_tension_u_rt_59_cp_to_od_audit_write_gap.md` AC #9 write half STRUCK; production-call routing owed to runtime spec amendment). v1.4's amendment is shape-canonical, not callsite-exercised — both are required for full self-hosting but operate on independent gradients per Phase-7 substitution-retirement discipline.

**Citation chain integrity finding (Class 3 flagged).** §1.4 row 1 cites `c11-operator-local` SKILL.md as the source of the `audit_ledger.sqlite` schema. That SKILL.md file is not present in this workspace (verified at v1.4 authoring via `find . -name "c11*"`). The citation chain is broken; the SQLite commitment at v1.4 is therefore unanchored from its cited substrate. Reframed at v1.4 as a deferred-persistence-model carry-forward (see prior paragraph) which preserves operator visibility without forcing immediate citation repair. Future C11-style D-ADR authoring will close this.

**Downstream absorption owed.** (a) `Cross_Axis_Composition_Document_v2_4.md` §2.3.7 (CP→OD bucket) — co-existing artifact; v1.4 ADR amendment closes the OD-side dependency referenced at the v2.4 edge classification; (b) `Spec_Control_Plane_v1_7.md` §13.5.1 NOTE 1 + NOTE 2 — references the OD-side drift resolution arc as pending; v1.4 + OD spec v1.5 ARE that resolution; a follow-on Form A patch to CP spec (v1.8) updates the NOTE references; (c) `Cross_Axis_Composition_Document_v2_4.md` §0.4 — Path D landing now has a coherent OD-side substrate to compose against.

**Cross-finding integration (v1.4).** This v1.4 amendment composes with `Spec_Operational_Discipline_v1_5.md` C-OD-24 (new contract — co-published) which authors the canonical OD-side audit-ledger payload schema lifted from code. Path B-revised-a's two artifacts (ADR-D5 v1.4 + OD spec v1.5) are inseparable — the ADR amends to permit the code-canonical shape; the OD spec authors the shape into the contract layer.

## Change-note (v1.4 → v1.5)

**Scope of revision.** Prose-only cross-reference addition at §1.4's per-persona-tier signing-key residence table, row 3 (`multi-tenant-compliance`). `B-36` (`.harness/forward-register.yaml`) closed the F5-prod-tech backend deferral this row names, for the AWS case, via `ADR-D8_audit_signing_backend.md` — a new sibling D-ADR selecting AWS KMS delegated signing (`ECC_NIST_EDWARDS25519`/Ed25519). Row 3's literal enumeration ("Vault / AWS Secrets Manager / Azure Key Vault / GCP Secret Manager / Doppler / 1Password Connect") names "AWS Secrets Manager," not "AWS KMS" — `ADR-D8` deliberately chose a different, more tightly-scoped AWS service (delegated HSM signing, never resolving key material via `fetch_secret`) over the literally-enumerated one, for reasons documented in `ADR-D8`'s own Rationale. This revision adds a forward-pointer note so a reader of this canonical ADR in isolation can discover that resolution exists, matching the precedent set by the `B-25`/`ADR-D2` v1.2→v1.3 bundled-absorption arc (which amended the sibling artifact it was correcting in the same PR).

**No structural change.** The §1.4 table's row/column shape, the signature-algorithm-tunable-axis paragraph, the key-period rotation model, the cross-deployment transition discipline, and the HITL trigger on signing-key absence are all preserved verbatim — this revision adds two sentences inside row 3's existing cells, nothing else. Other §1.4 row-3-named backends (Vault / Azure Key Vault / GCP Secret Manager / Doppler / 1Password Connect) remain deferred exactly as before.

**Sections preserved verbatim from v1.4.** Everything except the two sentences added inside §1.4 row 3.

## Context

This ADR closes the persona-dependent HITL-synchrony deferral declared at `ADR-F3.md` v1.1 §References (per Pattern Reference Catalog v1.0 §11.3.2 D5 enumeration; per Cluster 5 V2 §3 D5 line 207 persona-dependent classification; per `Persona_Document_v1` §10.2 explicit `HITL synchrony — Must be selective (math of tens-concurrent + 99.9%); UX shape open` constraint). F3 v1.1 (Status: Accepted post Step D) committed the harness to the stateless-reducer / launch-pause-resume durable-execution pattern (Pattern Reference Catalog v1.0 §10.1 P-CP-8) with a non-negotiable capability-requirement floor including (iv) observable lifecycle exposing workflow-start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease-acquired/released, and resumption events; F3 §Rationale (a) explicitly framed HITL primitive composition with durable-execution lifecycle as structurally identical, citing Cluster 4 §2.4 [HIGH]: "interrupt/resume as structurally identical to durable-execution checkpoint... selective HITL becomes mechanically expressible at the F3-lifecycle layer." `ADR-D1.md` v1 (Status: Proposed, 2026-05-10) specialized F3 by committing a five-element engine-class taxonomy with per-deployment-surface candidate mapping; D1 §1.2 enumerated per-engine-class HITL primitive shapes (event-sourced-replay → `wait_condition` + signal-handler per Temporal HITL doc [HIGH]; save-point-checkpoint → `interrupt()` + Command resume per LangGraph HITL doc [HIGH]; pure-pattern-no-engine → application-defined event-and-resume per 12-Factor Factor 7 [HIGH]). D5 specializes both F3 and D1 by traversing the synchrony-class candidate space competitively across the persona-tier axis and committing synchrony-class-and-rationale parametric on persona-tier × D1-engine-class.

The deliberation surface at D5 is the synchrony-class taxonomy across the candidate space, not a single-engine pick. Cluster 4 §2.4 [HIGH] establishes the canonical synchrony-class distinction across HITL implementations: sync-blocking (Cline per-step approval gate, OpenHands per-action approval, LangGraph `interrupt()`) vs durable-async (HumanLayer SDK `@hl.require_approval()` + ContactChannel + webhook, humanlayer/agentcontrolplane `ContactChannel` CR mesh-pattern, Temporal `wait_condition` + signal-handler with `timeout=days`, Inngest `waitForEvent`, langgenius/dify Human Input node) vs both-by-tier (RooCodeInc/Roo-Code configurable autonomy slider, Kilo-Org/kilocode `allowedCommands` + `deniedCommands` + `--auto` for CI/CD, Claude Code permission model `deny → ask → allow`, langchain-ai/deepagents HITL approval gates) vs two-agent-observer (disler/the-verifier-agent two-agent observer pattern). Cluster 4 §2.4.3 [HIGH] establishes the HandoffContext shape (`proposed_action`, `agent_confidence`, `failed_attempts`, `alternatives_considered`, `state_summary`, `audit_trail_link`, `retry_history`) as the within-turn assembly contract surrendered at HITL pause-time; Cluster 4 §2.4.4 [HIGH] establishes sub-agent HITL composition failure modes (sub-agent interrupt stranding; cascade timeout composition with parallel sibling sub-agents); Cluster 4 §2.4.5 [HIGH] documents webhook lost-update mitigation requirements and `interrupt()` re-entry bug pattern; Cluster 4 §2.4.6 / §2.4.7 [HIGH] document approval-fatigue mitigation patterns; Cluster 4 §2.2.3 [HIGH] retry protocol establishes 3rd-validator-fail → human-handoff as the C5↔C11 escalation contract.

`Persona_Document_v1` §2 records the bridging-arc persona — "sole operator at design-time; team or multi-tenant binding state later" — explicitly establishing all three persona tiers (solo-developer, team-binding, multi-tenant-compliance) as bridging-arc-traversal-required rather than a single-tier commitment. Persona §4 sets the 99.9%+ completion SLO at tens-concurrent scale and names this "mathematically incompatible with operator-in-loop-on-every-failure HITL — HITL must be selective, with the deterministic outer harness absorbing most recovery." Persona §8.1 names software engineering as natural-synchronous at design-time (operator review-in-loop) with multi-step session shape dominant; Persona §8.2 explicitly states "[HIGH] HITL naturally synchronous at design-time (operator review-in-loop); at multi-tenant binding, async HITL becomes feasible"; Persona §8.3 names pipeline automation as "[MODERATE] Often scheduled or event-triggered, not interactive"; Persona §8.4 names research as mixed; Persona §10.4 names compliance-readiness foundational primitives — "hash-chained audit ledger, granular access controls, encryption-at-rest, retention controls, tenant isolation, secrets rotation, comprehensive observability — need to be foundational, not bolt-on" — making per-persona-tier audit-ledger cryptographic shape a load-bearing D5 commitment surface.

Three permanent tensions interact with D5. T-perm-1 (C4 ↔ C10 — capability vs gating) is the **direct engagement at D5** — HITL-as-gate-on-irreversible-actions sits exactly on the C4-capability (per-tool tier annotation `tier ∈ {auto, ask, deny}` per Cluster 4 §2.4.3 [HIGH]) vs C10-gating (per-MCP-server trust framework + per-tool blast-radius taxonomy per `c10-action-safety` SKILL.md) axis; the eleven-trigger HITL catalog cited at both `c10-action-safety` and `c11-operator-local` SKILL.md is the cross-voice substrate for resolution. T-perm-3 (C1 ↔ C9 — control-flow vs reliability) D1-layer resolution shape `topology_fault_handling` stands; D5 surfaces the tension at the sub-agent boundary HITL composition (cascade timeout per Cluster 4 §2.4.4 [HIGH]) but does not revise the D1-layer resolution. T-perm-2 (C2 ↔ C3 — within-turn vs across-turn) F2-layer resolution stands per F3 v1.1 §References explicit framing; D5 surfaces the tension at the HandoffContext serialization seam (HITL pause is across-turn by definition; HandoffContext assembly is within-turn) but does not revise the F2-layer resolution.

ADR-F4 (Status: Proposed) is a load-bearing prior at the **sandbox-isolation seam**. F4's graduated-isolation principle (sandbox-strength-by-trust-level) composes with D5 at the gate-level computation per §1.5 below — F4's per-tool sandbox-tier assignment is one of the inputs to the gate-level composition rule. ADR-F1 (Status: Proposed) composes against D5 at the escalate-model-tier-on-validator-failure seam — Cluster 4 §2.2.3 [HIGH] establishes 2nd-validator-fail → re-prompt-with-different-system-prompt OR escalate-model-tier as the pre-HITL composition before 3rd-fail → C11 HITL escalation; F1 chain-advancement subscribes to F3 lifecycle events including HITL-event emission per §1.8 below.

## Decision

Commit at the D5 layer to a **four-component HITL synchrony specification**:

1. **Four-response palette** (`approve` / `edit` / `reject` / `respond`) as the harness-canonical operator-response contract across all cells of the persona-tier × D1-engine-class matrix (§1.1).
2. **Synchrony-class commitment per cell** of the 2D matrix (persona-tier × D1-engine-class → synchrony-class + HITL primitive shape) (§1.2).
3. **Three-placement topology primitive** (pre-action gate / sub-agent boundary / validator-failure escalation) as first-class topology declaration (§1.3).
4. **T-perm-1 D5-layer multiplicative gate-level composition rule** with `persona_tier × blast_radius_tier` axes added to the locked tunable parameter (§1.5).

Synchrony class is committed at D5 per cell; specific candidate-within-class is deferred to persona-tier-binding-time downstream of Phase 3 per §1.7 contract.

### 1.1 Four-response palette (cross-cell invariant)

The harness-canonical operator-response contract is the four-response palette per `c11-operator-local` SKILL.md primitive ownership:

| Response | Semantics | Audit ledger entry |
|---|---|---|
| `approve` | Proceed with proposed action as-is | `(action_id, gate_level, response: approve, timestamp, prior_event_hash)` |
| `edit` | Proceed with operator-modified proposed action | `(action_id, gate_level, response: edit, edited_proposal_hash, timestamp, prior_event_hash)` |
| `reject` | Cancel proposed action; agent receives rejection signal | `(action_id, gate_level, response: reject, rejection_reason_hash?, timestamp, prior_event_hash)` |
| `respond` | Continue dialogue with the agent without action commitment | `(action_id, gate_level, response: respond, response_text_hash, timestamp, prior_event_hash)` |

Palette completeness is invariant across all cells of §1.2. The synchrony class determines *how* the palette is delivered (in-process function return vs durable signal vs webhook callback) — not *what* the operator can express.

### 1.2 Synchrony-class × HITL-primitive-shape matrix (persona-tier × D1-engine-class)

The 2D matrix below commits synchrony class and HITL primitive shape per cell. Cell entries follow the schema `synchrony-class | HITL primitive shape | candidate evidence`.

| persona-tier ↓ \ D1-engine-class → | event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment |
|---|---|---|---|---|---|
| **solo-developer** | sync-blocking PRIMARY \| in-process function with synchronous return; durable-async available via DBOS-as-library MODERATE | sync-blocking PRIMARY \| LangGraph `interrupt()` + Command resume per LangGraph HITL doc [HIGH] \| cline per-step approval gate; OpenHands per-action approval | sync-blocking PRIMARY \| 12-Factor Factor 7 application-defined event-and-resume [HIGH] \| humanlayer/12-factor-agents F7 | durable-async PRIMARY (rare at solo; if K8s local — Kind/k3s) \| `ContactChannel` CR mesh-pattern \| humanlayer/agentcontrolplane | sync-blocking PRIMARY \| segment-resume on restart with approval-pending-segment marker \| shareAI-lab/Kode-Agent (per D1 §References) |
| **team-binding** | durable-async PRIMARY \| Temporal `wait_condition` + signal-handler with `timeout=days` per Temporal HITL doc [HIGH] \| Temporal self-hosted; Inngest self-hosted `waitForEvent` | both-by-tier PRIMARY \| LangGraph + Postgres + Redis-lease + per-tool tier annotation; Claude Code permission model `deny → ask → allow` \| RooCodeInc/Roo-Code autonomy slider; langchain-ai/deepagents HITL approval gates | EXCLUDED (per D1 §1.2 self-hosted-server row excludes pure-pattern for durable pole) | durable-async PRIMARY \| `ContactChannel` CR mesh-pattern with K8s-resident operator \| humanlayer/agentcontrolplane | durable-async PRIMARY \| segment-resume + external trigger via webhook ingress \| Kode-Agent + webhook |
| **multi-tenant-compliance** | durable-async PRIMARY \| Temporal Cloud / AWS Bedrock AgentCore / Google Vertex Agent Engine native HITL primitives \| Temporal Cloud; Bedrock; Vertex | durable-async PRIMARY \| LangGraph + DynamoDBSaver + managed checkpointer with engine-bound HITL signal \| LangGraph + DynamoDBSaver per AWS pattern | EXCLUDED (analogous to team-binding; pure-pattern excluded for durable pole at managed-cloud surface) | durable-async PRIMARY \| ACP K8s-managed with multi-tenant `ContactChannel` namespace isolation \| humanlayer/agentcontrolplane | durable-async PRIMARY \| managed-WAL with cryptographic-signed audit ledger \| Kode-Agent pattern + managed substrate |

Cells reading `EXCLUDED` reflect D1 §1.2 candidate-set exclusions (pure-pattern excluded from durable pole at self-hosted-server and managed-cloud deployment surfaces); D5 inherits the exclusion without revisiting D1.

The both-by-tier class is a **per-tool overlay** that operates at every cell rather than a competing synchrony class — at any cell, per-tool `tier ∈ {auto, ask, deny}` annotation determines which actions invoke HITL gate (synchrony class per the cell) and which fire `auto` without operator engagement. The two-agent-observer class (disler/the-verifier-agent) is a **meta-class composable orthogonally** at any cell where Tier-3+ blast-radius actions per `c10-action-safety` require independent verification before HITL escalation.

### 1.3 Three-placement HITL topology primitive

HITL placement is a first-class topology declaration with three placement points:

| Placement | Trigger | Cell applicability |
|---|---|---|
| `pre-action` | Before any tool call where `_hitl_required(tool, server, persona_tier) == true` per §1.5 composition | All cells |
| `sub-agent-boundary` | At parent-child handoff per Cluster 4 §2.4.4 [HIGH] (HandoffContext serialization point) | All cells; sub-agent interrupt stranding mitigated via cascade-timeout per §1.6 |
| `validator-escalation` | After retry-budget exhaustion (3rd validator fail per Cluster 4 §2.2.3 [HIGH]) | All cells |

#### 1.3.1 Topology primitive interface signature

```
hitl_gate(
    placement       : "pre-action" | "sub-agent-boundary" | "validator-escalation",
    handoff_context : HandoffContext,    // Cluster 4 §2.4.3 [HIGH] shape
    response_palette: { approve, edit, reject, respond },
    timeout         : Duration,          // None for sync-blocking; bounded for durable-async
    cascade_policy  : "pause" | "proceed" | "cascade-cancel"
) → HITLResult {
    response                 : "approve" | "edit" | "reject" | "respond",
    edited_proposal          : Optional<ProposedAction>,
    response_text            : Optional<String>,
    timestamp                : ISO-8601,
    audit_ledger_entry_id    : EntryID,
    response_summary_hash    : SHA-256
}
```

#### 1.3.2 HITL-as-tool-call rewriting contract

Every tool exposed to the agent declares `tier ∈ {auto, ask, deny}` and `blast_radius ∈ {read-only, local-mutation, external-reversible, external-irreversible}` in its SKILL.md frontmatter or MCP server manifest (C4 contract per `c4-tools-integration` SKILL.md). The runtime evaluates `_hitl_required(tool, server, persona_tier)` per §1.5 against per-MCP-server trust and persona-tier floor before dispatching the tool call. If `_hitl_required` evaluates true, the tool call is **rewritten** by the harness into one of the three semantic variants:

| Variant | Tool signature | Engine binding |
|---|---|---|
| `request_human_input(prompt, options)` | Synchronous return | sync-blocking cells |
| `await_human_approval(action, context, channel)` | Durable signal-and-wait | durable-async cells |
| `escalate_to_human(severity, summary, retry_history)` | Triggered post retry-budget exhaustion | All cells; composes with §1.3 `validator-escalation` placement |

### 1.4 Per-persona-tier ledger cryptographic shape

The audit ledger entry per HITL invocation is persona-tier-conditional in cryptographic shape (D1 §1.2 commits engine-class C3-tier residence; D5 commits per-persona-tier ledger cryptographic shape composed atop):

| Persona tier | Ledger cryptographic shape | Compliance posture |
|---|---|---|
| solo-developer | Append-only ledger (storage form per IS spec; v1.4 canonical = JSONL via IS state-ledger composition per ADR-F2 + `Spec_Information_Substrate_v1.md` v1.3 §3; SQLite migration via C11-style D-ADR is permitted but not committed at v1.4 — see §1.4 sqlite schema extension table carry-forward in Change-note v1.3 → v1.4); no hash chain required by default | Best-effort; operator self-audit |
| team-binding | Hash-chained ledger (storage form per IS spec; v1.4 canonical = JSONL via IS state-ledger composition) with `prior_event_hash` linkage per F2 state-ledger entry shape and per OD spec v1.5 C-OD-24.1 `AuditPayload.prior_entry_hash` field | Tamper-evident under team review |
| multi-tenant-compliance | Hash-chained ledger (storage form per IS spec; v1.4 canonical = JSONL via IS state-ledger composition) + cryptographic signature per ledger entry (per `AuditSignatureAttributes` declared at OD spec v1.5 C-OD-24.2); tamper-evident under external audit | Persona §10.4 compliance-readiness foundational primitive |

#### Signing-key resolution at multi-tenant-compliance (v1.2 — closes F2-13)

The hash-chain commitment at row 2 (team-binding) provides tamper-evidence WITHIN a ledger; the cryptographic signature commitment at row 3 (multi-tenant-compliance) adds authorship-binding ON TOP of the hash chain. The two are stacked: the hash chain detects in-place modification (any tamper without recomputing the chain forward breaks integrity); the signature detects authorship spoofing (an attacker who modifies entries cannot produce valid signatures without the signing key). Under external audit at multi-tenant-compliance posture, both are required because the threat model includes both insider tampering (hash-chain catches) and key-extraction-and-replay scenarios (signature key-period model surfaces rotation events for forensic reconstruction).

The signing key is itself a secret and resolves through ADR-F5's `fetch_secret(name, scope) -> SecretRef` abstraction. Per persona-tier signing-key residence:

| Persona tier | Signing-key residence | F5 composition contract |
|---|---|---|
| `solo-developer` | No signing key required (row 1 commits no hash chain; no signature). | n/a |
| `team-binding` | OS keychain via F5 dev-tech (per ADR-F5 §Decision and `c11-operator-local` SKILL.md `keyring` Python library: Apple Keychain on macOS / Secret Service on Linux / Credential Locker on Windows). Per-deployment signing key under namespace `harness.<deployment_id>.audit_signing_key`. | F5 dev-tech `fetch_secret("audit_signing_key", scope=deployment_id)` |
| `multi-tenant-compliance` | F5 prod-tech (deferred to D-ADR per ADR-F5 §Deferred D-ADRs — Vault / AWS Secrets Manager / Azure Key Vault / GCP Secret Manager / Doppler / 1Password Connect). Per-deployment vs per-tenant scope is operator-tunable at multi-tenant-binding-time (`audit_signing_key_scope ∈ {deployment / tenant}`) per Persona §11.10 multi-tenant tenant-isolation deferral. **v1.5 note (`B-36`/`ADR-D8`, 2026-07-16): for a deployment provisioning AWS as its production signing surface, this deferral is resolved by `ADR-D8` — AWS KMS delegated signing (`ECC_NIST_EDWARDS25519`/Ed25519, matching this row's own default algorithm below), NOT AWS Secrets Manager as literally enumerated here. The two are architecturally distinct: KMS never exposes key material outside its HSM boundary (no `fetch_secret` resolution occurs for the signing key itself), whereas Secrets Manager would store raw key bytes for local signing. `ADR-D8`'s own Rationale documents why KMS was chosen over the Secrets-Manager-literal reading. Other backends (Vault / Azure Key Vault / GCP Secret Manager / Doppler / 1Password Connect) remain deferred.** | F5 prod-tech `fetch_secret("audit_signing_key", scope=deployment_id\|tenant_id)` per the operator-tunable scope; **AWS deployments: see `ADR-D8`** — the signing key itself is never `fetch_secret`-resolved (KMS-delegated, not F5-secret-resolved) |

Signature algorithm at team-binding and multi-tenant-compliance: **Ed25519 default**, with operator-tunable axis `audit_signature_algorithm ∈ {ed25519 / ecdsa-p256 / rsa-pss-2048}` at deployment-binding-time. Ed25519 default rationale per `c11-operator-local` SKILL.md substrate: small key/signature size (32-byte key, 64-byte signature), constant-time implementations available across language ecosystems, no parameter-choice footguns, broad HSM / TPM 2.0 / Secure Enclave support. ECDSA-P256 offered as HSM-compatibility fallback for environments where Ed25519 is unavailable. RSA-PSS-2048 offered for compliance regimes that mandate RSA-family algorithms.

**Key-period model for rotation.** Per ADR-F5 §(c)(iii) rotation-aware retry contract and `c11-operator-local` SKILL.md §4.1.14 secret-rotation flow, signing-key rotation emits a `secret_rotation_event` ledger entry. Each multi-tenant-compliance ledger entry carries `audit.signature.key_id` (the signing key's identity in the secrets backend) and `audit.signature.key_period` (a monotonic integer incremented on each rotation). The hash chain (`prior_event_hash` / `entry_hash` per F2 + `c11-operator-local` SKILL.md §4.1.28) is **continuous across rotations**; rotation does NOT break the chain. The signature is per-entry and binds to the entry's `key_period`. External-audit verification: walk the chain, recompute hashes, verify each entry's signature using the appropriate key for that entry's `key_period`. The `secret_rotation_event` entry IS the chain-rotation event itself: when the rotating secret IS the audit-signing key (discriminator `audit.signing_key_rotation: bool` set to true on the event payload), the entry is counter-signed under both the outgoing key (current `key_period`) AND the incoming key (next `key_period`) — anchoring chain continuity at the rotation boundary. For rotations where the rotating secret is NOT the audit-signing key (e.g., harness's API keys to model providers), the rotation event is single-signed under the current audit-signing key.

**Cross-deployment key transition.** When the deployment moves from self-hosted-server (team-binding, F5 dev-tech keychain) to managed-cloud (multi-tenant-compliance, F5 prod-tech vault) per the bridging-arc per Persona §2 / §10.2, the signing-key residence may change. Per s14 §4.1.34 cross-deployment opt-in granularity and s13 §4.11 eleven-trigger HITL catalog, the transition is a mandatory-HITL trigger; the operator approves the transition and supplies (or designates via F5 prod-tech) the new key. The cross-deployment transition itself emits an `audit_event` ledger entry of kind `signing_key_residence_transition` carrying old and new `key_id` plus the operator-approved transition timestamp; the entry is counter-signed under outgoing + incoming keys per the rotation discipline. Chain continuity is preserved across the transition; verification requires the auditor to know which key serves which `key_period` per the standard verification rule.

**HITL trigger on signing-key absence.** Adding a refinement to the s13 §4.11 eleven-trigger HITL catalog: when the harness attempts to write a multi-tenant-compliance ledger entry and F5 returns `secret_unavailable` or `secret_unknown` per F5 cause-attribution refinements, this is a mandatory-HITL escalation — the harness MUST NOT silently proceed without signature at multi-tenant-compliance posture. `secret_unavailable` (transient backend-down) routes through C9 per-`{secret_backend, scope}` breaker per F5 §Consequences; `secret_unknown` (operator-must-provision) routes to permanent-fail per F5 fail-class. Both trigger the catalog refinement "Signing-key fetch failure at multi-tenant-compliance" with `available_responses` restricted to `{approve / reject / respond}` per s14 §7.10(d) (operator cannot edit-around the trust posture).

**Sqlite schema extension** per `c11-operator-local` SKILL.md §4.1.28: the `ledger_entries` table is extended with three signature columns at team-binding and multi-tenant-compliance, plus a fourth `rotation_correlation_id` column at v1.3 under F2-iter2-03 Option (a) two-row pattern:

| Column | Type | Definition |
|---|---|---|
| `signature_value` | blob (variable; 64 bytes for Ed25519, 64 bytes for ECDSA-P256, 256 bytes for RSA-PSS-2048) | Per-entry signature over the entry's `entry_hash` |
| `signature_key_id` | text | Stable identifier for the signing key in the secrets backend (e.g., `harness.<deployment_id>.audit_signing_key.v3`) |
| `signature_key_period` | integer | Monotonic period; increments on each signing-key rotation |
| `rotation_correlation_id` | text (UUID) NULL **(v1.3 — added per F2-iter2-03 Option (a) two-row pattern)** | NULL for all non-rotation ledger entries (the dominant case); UUID populated and shared across the two rotation-pair entries that together materialize a `secret_rotation_event` when the rotating secret IS the audit-signing key (sibling-1 signed under outgoing key at current `signature_key_period=N`, sibling-2 signed under incoming key at next `signature_key_period=N+1`; the shared UUID is the structural carrier of the dual-signature commitment from the §1.4 prose) |

Population per persona tier: `solo-developer` → all four columns NULL; `team-binding` → first three columns populated under `audit_signature_algorithm` choice and `rotation_correlation_id` NULL except on rotation-pair entries (populated with shared UUID); `multi-tenant-compliance` → first three populated and `rotation_correlation_id` populated only on rotation-pair entries (NULL elsewhere). Single schema with conditional population per row; no per-tier table multiplication.

**External-auditor verification semantics for the two-row rotation pattern (v1.3 — F2-iter2-03 Option (a) closure).** Standard chain-verification walks entries in `entry_hash` chain order, recomputing hashes and verifying each entry's `signature_value` against the key valid at the entry's `signature_key_period`. On encountering a non-NULL `rotation_correlation_id`, the auditor queries for the sibling entry sharing the same correlation UUID; the pair is verified jointly per the discipline below. Sibling-1 carries `signature_key_period=N` and is verified under the key valid at period N (the outgoing key at the rotation boundary); sibling-2 carries `signature_key_period=N+1` and is verified under the key valid at period N+1 (the incoming key). Chain hash continuity is preserved across the rotation boundary: sibling-2's `entry_hash` extends the chain from sibling-1's `entry_hash` (no chain break; sibling-2 is treated as the rotation-anchor entry under the new key-period). A verification failure of either sibling under its appropriate key indicates either key compromise OR ledger tampering at the rotation boundary; both fail the audit. Recovery from such a failure routes through the standard `c11-operator-local` SKILL.md §4.1.28 audit-failure escalation path. Non-rotation entries (`rotation_correlation_id IS NULL`) are verified one-at-a-time under their declared `signature_key_period`, unchanged from the v1.2 baseline.

### 1.4.1 Span attribute names declared by §1.4

The §1.4 per-persona-tier ledger cryptographic shape is materialized as the **`audit.*` span attribute namespace** ingested by ADR-D6 §1.2 row `audit.*` under the OTel/OTLP export contract. D5 §1.4.1 is the canonical declaration site for these attribute names; D6 §1.2 inherits without re-declaration. Seven attribute names declared (three v1.1 attributes preserved verbatim — active per §1.4 row activation discipline — plus four v1.2 attributes added under the F2-13 signing-key resolution closure):

**v1.1-declared attributes (preserved verbatim):**

- **`audit.signature.sha256`** — per-event SHA-256 hash over the ledger entry payload. Type: hex-encoded 64-character string. Always-emitted at multi-tenant-compliance tier (per §1.4 row 3); structurally absent at solo-developer (§1.4 row 1 — no signature shape) and team-binding (§1.4 row 2 — hash chain present but signature absent). Per D6 §1.3 sampling discipline, spans carrying `audit.signature.*` attributes are always-sampled (head=1.0) regardless of base sampling rate per cryptographic-anchor tamper-evidence relevance. **v1.2 reframing (semantic clarification, no rename):** under the F2-13 signing-key resolution, this attribute carries the SHA-256 hash that is *signed* by the signing-key-resolved cryptographic signature; the signature value itself is the new `audit.signature.value` attribute below. The pre-existing `audit.signature.sha256` continues to denote the hash; the v1.2 amendment introduces the signature bytes as a sibling attribute rather than renaming the existing declaration to avoid D6 §1.2 ripple effects. **v1.4 tightening (canonical payload referent):** "ledger entry payload" canonically means the OD `AuditPayload` Pydantic model declared at `Spec_Operational_Discipline_v1_5.md` C-OD-24.1 (3 fields: `entry_core` + `audit_namespace_attrs` + `prior_entry_hash`); the hash is computed as `SHA-256(AuditPayload.model_dump_json())` per the Pydantic v2 canonical JSON serialization under the OD-axis `ConfigDict(extra="forbid", frozen=True)` discipline. The v1.1 + v1.2 attribute declaration shape is preserved verbatim; only the "payload" referent is tightened from ambiguous to spec-anchored. See OD spec v1.5 C-OD-24.5 for the canonical `compute_entry_hash` helper at the OD axis.

- **`audit.signature.prior_hash`** — hash-chain link to the prior event in the per-tenant audit ledger. Type: hex-encoded 64-character string. Always-emitted at team-binding (§1.4 row 2 — *hash-chained SQLite with `prior_event_hash` linkage per F2 state-ledger entry shape*) and multi-tenant-compliance (§1.4 row 3); structurally absent at solo-developer (§1.4 row 1 — no hash chain). The `prior_hash` value joins to the F2 state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` via `prior_event_hash` (semantic equivalence; ledger-entry-hash is the cryptographic anchor on the F2 entry's `prior_event_hash` field).

- **`audit.actor.id`** — actor identity for the ledger entry. Type: opaque string under each persona tier's actor-identity discipline (operator UUID at solo-developer; operator-or-agent UUID at team-binding; operator/agent/sub-agent/system identity per `c11-operator-local` SKILL.md actor-identity registry at multi-tenant-compliance). Always-emitted at all three persona tiers; cardinality is bounded by the actor-identity registry (operator + named agents + system; not per-session-unique).

**v1.2-declared attributes (new under F2-13 closure):**

- **`audit.signature.value`** — per-entry cryptographic signature over the entry's `audit.signature.sha256` hash, produced under the signing-key resolved through F5 per the §1.4 signing-key residence table. Type: binary (variable length per `audit.signature.algorithm` — 64 bytes for Ed25519, 64 bytes for ECDSA-P256, 256 bytes for RSA-PSS-2048). Always-emitted at team-binding (when team-binding deployments opt into signature posture beyond default hash-chain — this is operator-tunable per persona-tier shape) and multi-tenant-compliance (per §1.4 row 3 — always-on). Structurally absent at solo-developer.

- **`audit.signature.algorithm`** — signature algorithm enum carried per entry. Type: enum string ∈ `{ed25519 / ecdsa-p256 / rsa-pss-2048}`. Default: `ed25519`. Operator-tunable at deployment-binding-time per `audit_signature_algorithm`. Cardinality is low (deployment-bound; one value per deployment binding).

- **`audit.signature.key_id`** — signing-key identifier in the F5 secrets backend. Type: opaque string (typical shape `harness.<deployment_id>.audit_signing_key.v<N>` at team-binding under F5 dev-tech keychain; tenant-namespaced shape at multi-tenant-compliance per `audit_signing_key_scope`). Cardinality is low-medium (per key-period; one value per active signing key plus historical values for chain-verification under rotation).

- **`audit.signature.key_period`** — monotonic period integer incremented on each signing-key rotation per §1.4 key-period model. Type: integer (non-negative, monotonic per deployment). Cardinality is low (one value per active signing key, plus historical values for chain-verification under rotation).

**Persona-tier emission discipline.** The §1.4 ledger cryptographic shape conditionally activates these attributes per persona tier — solo-developer emits only `audit.actor.id`; team-binding emits `audit.actor.id` + `audit.signature.prior_hash` (and optionally `audit.signature.sha256` + `audit.signature.value` + `audit.signature.algorithm` + `audit.signature.key_id` + `audit.signature.key_period` if team-binding deployment opts into signature posture); multi-tenant-compliance emits all seven. D6 §1.2 row `audit.*` ingestion contract honors this conditional activation through per-cell sampling discipline (multi-tenant-compliance always-sampled; team-binding base-rate; solo-developer base-rate per §1.3).

**Capability-floor (iv) traceability (v1.2 — F2-13 closure).** F3 v1.1 capability-floor (iv) requires observable lifecycle including audit-relevant events; §1.4.1 declares the attribute substrate for the cryptographic-anchor portion of the audit ledger. The signing-key resolution mechanism (which key signs the `audit.signature.sha256` hash; how it is provisioned through F5 secrets bridge; what signature algorithm produces the bytes; how rotation is handled; how cross-deployment transition preserves chain continuity) is **closed in v1.2 per the §1.4 signing-key resolution sub-section above**. The v1.1 deferral to a forthcoming D5 revision per F2-13 routed to `council-orchestrator` C11+C10 session is satisfied; the council convening at v1.2 emitted the resolution committed at §1.4 + §1.4.1 v1.2 additions (C11 primary; C10 co-primary; C3 / C7 consultants per the v1.2 council-orchestrator session referenced in §References Convening artifact citations).

### 1.5 T-perm-1 D5-layer multiplicative gate-level composition rule

T-perm-1 (C4 ↔ C10 — capability vs gating) is promoted to Layer 3 with D5-layer resolution shape encoded as the tunable parameter `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier` per spec-writer s3 §6.3. This specializes the previously locked tunable `per_tool_gate_level × per_mcp_server_trust_tier` (per `references/output-templates.md`) by adding the `persona_tier × blast_radius_tier` dimensions D5 introduces.

#### 1.5.1 Composition rule

```
gate_level(tool, mcp_server, persona_tier) =
    max(
        per_tool_gate_level,                  // C4 contract: {auto, ask, deny}
        blast_radius_floor(tool),             // C10 four-tier taxonomy
        per_mcp_server_trust_floor(server),   // C10 five-tier framework
        persona_tier_floor                    // D5 introduces this axis
    )

where:
    blast_radius_floor:
        read-only                 → auto
        local-mutation            → ask  (configurable to auto at solo-developer)
        external-reversible       → ask
        external-irreversible     → ask  (with dual-control at multi-tenant-compliance)

    persona_tier_floor:
        solo-developer            → ask  (operator may override to auto for non-irreversible)
        team-binding              → ask  (audit ledger required; no auto override on external-*)
        multi-tenant-compliance   → ask  (audit ledger + cryptographic signature; dual-control on
                                          external-irreversible)
```

#### 1.5.2 Cross-deployment monotonicity

When persona tier changes during bridging-arc traversal (solo-developer → team-binding → multi-tenant-compliance), `persona_tier_floor` is monotonic ascending. Tier downgrade is structurally prohibited; tier upgrade is permitted at any time and immediately raises the effective gate level for in-flight workflows.

### 1.6 Composition with reliability primitives

Durable-async cells require timeout-degradation mode commitment. Per Cluster 4 §2.4 [HIGH] Temporal `wait_condition timeout=days` and per Cluster 4 §2.4.5 [HIGH] webhook lost-update mitigation:

| Persona tier | Timeout-degradation mode | Rationale |
|---|---|---|
| solo-developer | `fail-closed` | Operator is the developer; no secondary channel |
| team-binding | `escalate-secondary-channel` (default); `fail-closed` (configurable) | On-call rotation typical; operator-tunable per workload |
| multi-tenant-compliance | `fail-closed` + alerting | Persona §10.4 compliance posture incompatible with `fail-open`; tamper-evident audit requires explicit operator action |

Webhook ingress for durable-async cells MUST use idempotency-keyed signal delivery composed against F2 state-ledger entry shape (`(approval_id, idempotency_key)` checked against the ledger before signal application) per Cluster 4 §2.4.5 [HIGH].

Sub-agent cascade timeout per Cluster 4 §2.4.4 [HIGH]: the topology declaration determines `cascade_policy ∈ {pause, proceed, cascade-cancel}`; C9 owns the timeout mechanism; T-perm-3 D1-layer resolution shape `topology_fault_handling` covers this composition without D5-layer revision.

### 1.7 Persona-tier-binding-time selection contract

Per-cell synchrony class is committed at D5; specific candidate-within-class is deferred to persona-tier-binding-time downstream of Phase 3. The selection contract:

```
At persona-tier-binding-time downstream of Phase 3:

1. Operator declares persona tier (solo-developer | team-binding | multi-tenant-compliance).
2. Operator declares deployment surface (local-development | self-hosted-server | managed-cloud)
   per D1 §1.2.
3. Cell at (persona-tier × D1-engine-class) lookup yields synchrony class + HITL primitive shape.
4. Operator selects specific candidate from §References shape 3 enumeration meeting the cell's
   synchrony class and HITL primitive shape.
5. Composition with §1.4 ledger cryptographic shape, §1.5 gate-level composition, §1.6
   timeout-degradation mode is enforced at runtime regardless of candidate choice.
```

### 1.8 Composition with observability

F3 v1.1 capability-floor (iv) observable lifecycle is extended at D5 with the HITL-event span schema. Per the F2-06 prefix-discipline resolution at v1.1 (each per-event attribute carries the event-namespace as its prefix), the schema is:

| Span name | Span attributes (structure-not-content per `c7-observability` SKILL.md) |
|---|---|
| `hitl.gate.evaluated` | `hitl.gate.level` (cardinality-safe metric dimension per D6 §1.2), `hitl.gate.persona_tier`, `hitl.gate.required: bool` **(v1.3 — `hitl.gate.tool` and `hitl.gate.mcp_server` retired per F2-iter2-02 Reading 1 canonical pass-through; gated tool identity read from `gen_ai.tool.name` on parent `tool.call` span per OTel GenAI semconv 1.41.0; gated MCP server identity read from `mcp.server.name` on parent `mcp.tool.call` span per ADR-D3 v1.1 §1.8.1 via trace correlation)** |
| `hitl.invocation.opened` | `hitl.gate.level` (cross-event reference; same canonical attribute as evaluated event), `hitl.invocation.placement`, `hitl.invocation.handoff_context_size_bytes`, `hitl.invocation.audit_ledger_entry_id` |
| `hitl.invocation.responded` | `hitl.response.class` (cardinality-safe metric dimension per D6 §1.2 ∈ `approve` / `edit` / `reject` / `respond` per §1.1 four-response palette), `hitl.response.latency_ms`, `hitl.response.summary_hash` |
| `hitl.invocation.timed_out` | `hitl.timeout.duration_ms`, `hitl.timeout.degradation_mode_applied` |

HITL spans are always-sampled (head=1.0, tail-keep-on-classification=true) regardless of base sampling rate per `c7-observability` SKILL.md sampling discipline; HITL events are tamper-evidence-relevant under Persona §10.4 compliance posture.

**Cross-namespace canonical-naming (v1.3 — closes F2-iter2-02 under operator-selected Reading 1 canonical pass-through).** Gate-event attributes that reference identities also carried by parent spans use the canonical OTel GenAI / D3 namespace names rather than event-scoped aliases. Specifically: the gated tool's name is read from `gen_ai.tool.name` on the parent `tool.call` span (canonical per OTel GenAI semconv 1.41.0); the gated MCP server's identity is read from `mcp.server.name` on the parent `mcp.tool.call` span (canonical per ADR-D3 v1.1 §1.8.1). The gate-event consumer recovers these via trace correlation (parent-span attribute lookup at the gate-event's trace context) rather than through duplicated event-scoped attributes. The v1.1-declared `hitl.gate.tool` and `hitl.gate.mcp_server` attribute names are retired at v1.3; the v1.2-declared event-scoped attribute set on `hitl.gate.evaluated` (`hitl.gate.level`, `hitl.gate.persona_tier`, `hitl.gate.required`) is preserved. This preserves cross-event attribute-name unity per Pattern P1 mechanical-alignment discipline — gate-event consumers traverse one trace step (parent-span attributes) to recover the tool / MCP server identity rather than parsing event-scoped aliases that would duplicate canonical attribute content under a divergent name.

### 1.9 Composition with eval methodology

Per `c8-eval-engineer` SKILL.md, the `expected_hitl_invocations_per_session` metric is the canonical operator-burden eval primitive. Per-persona-tier calibration targets:

| Persona tier | Target `expected_hitl_invocations_per_session` | Failure modes |
|---|---|---|
| solo-developer | 5–20 | <2 → over-automated; >40 → fatigue |
| team-binding | 1–5 | <1 → over-automated; >10 → fatigue |
| multi-tenant-compliance | 0.5–3 | <0.5 → audit gap risk; >5 → fatigue |

Tool-tier annotation calibration eval (Husain manual-review→categorize→automate→align loop per `c8-eval-engineer` SKILL.md): `ask`-tier tools producing >95% approve responses across a holdout indicate mis-calibration toward `auto`; `auto`-tier tools producing operator overrides via post-action audit-ledger flagging indicate mis-calibration toward `ask`.

### 1.10 Composition with model routing

HandoffContext summarization role is per-persona-tier model-bound:

| Persona tier | Summarization model | Rationale |
|---|---|---|
| solo-developer | Haiku | Low-latency, low-cost; operator review-in-loop tolerates lower fidelity |
| team-binding | Sonnet | Balanced fidelity/cost |
| multi-tenant-compliance | Sonnet with extended-thinking budget OR Opus | Compliance-bound summaries require higher fidelity |

Pre-HITL escalation order — discriminated by C5 fail-class (locked five-class retry-exit taxonomy per `c5-validation-contract` SKILL.md s14 §7.5(d) reconciliation):

```
On validator failure event from C5 gate evaluation:

  Discriminate by validator.fail.class (per §1.10.1 attribute declarations):

  ── transient-retry             → C9 backoff + retry (mechanism per `c9-reliability-recovery`
                                   SKILL.md full-jitter retry; cause-attribution-conditioned
                                   policy per c9 §4.1.1)
  ── Reflexion-recoverable       → C5 reflect-step verbal feedback + C1 retry-loop
                                   (per `c5-validation-contract` SKILL.md Reflexion contract);
                                   C2 stitches feedback into next iteration's prompt
  ── HITL-recoverable            → C11 HITL primitive (validator-HITL placement per
                                   `c11-operator-local` SKILL.md §4.1.6); palette
                                   {approve / request-changes / reject}; request-changes
                                   routes back as Reflexion-recoverable
  ── permanent-fail-exit         → SKIP STAIRCASE; route directly to C11 HITL
                                   (validator-escalation placement per §1.3); palette
                                   {approve / edit / reject / respond} per s14 §4.1.8;
                                   palette restricted to {approve / reject / respond}
                                   when composing with cross-trust-boundary actions
                                   (cross-family active, local-terminal active,
                                    untrusted-MCP) per s14 §7.10(d)
  ── terminal-fail-exit          → SKIP STAIRCASE; workflow halts; HITL escalation
                                   per `c11-operator-local` SKILL.md with no recovery path

When validator.fail.class ∈ {transient-retry, Reflexion-recoverable}:
  Pre-HITL escalation order (the v1 staircase, transient-only) per Cluster 4 §2.2.3 [HIGH]:
    1st validator fail   → retry with backoff (C9 mechanism)
    2nd validator fail   → cause-attribution-conditioned branch:
                            - cause ∈ {model_misfire, provider_outage, capability_shortfall_transient}
                              → escalate model tier per ADR-F1 chain composition
                                (subscribes to C9 trigger on_capability_shortfall or
                                 on_per_model_breaker_trip)
                            - cause ∈ {semantic_disagreement, contract_violation_not_yet_routed_to_Reflexion}
                              → re-prompt with different system prompt
    3rd validator fail   → C5 emits permanent-fail-exit → routes to validator-escalation
                            HITL placement per §1.3 (skip-staircase branch above)
```

Permanent-fail-exit classification originates with C5 emitting `validator.fail.class=permanent-fail-exit` plus `validator.fail.cause_attribution` annotation per `c5-validation-contract` SKILL.md and s12 §7.5(a); C9 owns the parallel retry-budget-exit exit condition (the budget exhausting; per `c9-reliability-recovery` SKILL.md) which also routes to staircase-skip with `validator.fail.cause_attribution=time_budget_exhaust`. Both routes terminate the staircase early and converge at validator-escalation HITL placement per §1.3.

Typical `cause_attribution` values that route to permanent-fail-exit per `c5-validation-contract` SKILL.md (locked at s14 §7.5(d) reconciliation; F5 substrate at ADR-F5 §Decision adds five secret-fetch refinements): `contract_violation` (model demonstrably cannot fix; Reflexion attempts exhausted), `schema_violation` under guaranteed-decoder mode (structural anomaly), `capability_shortfall` (chain-terminal model below capability floor; composes with `c11-operator-local` SKILL.md §4.1.20 capability-shortfall HITL escalation), `policy_denial` (operator policy or trust-boundary policy permanently disallows), `secret_unknown` per F5 (unprovisioned secret; no recovery path). `human_rejection` routes to `terminal-fail-exit` (operator explicitly rejected; no further retry of any class). `time_budget_exhaust` routes to permanent-fail-exit or terminal-fail-exit per topology context.

The discriminated encoding aligns D5 §1.10 with the precedent shape committed at ADR-D2 v1 §1.8: *"Permanent-fail violations skip the staircase and go directly to HITL"* — D2's sandbox-violation case is one instance of the general validator-failure shape D5 §1.10 now formalizes; D2 cross-D-ADR composition citation added to §References Shape 4 per F2-15.

Audit ledger discipline under permanent-fail-exit composes against §1.4 + §1.4.1 unchanged: each permanent-fail HITL invocation writes a ledger entry signed under the multi-tenant-compliance signing-key resolution per F2-13 closure (no permanent-fail-specific signing path); each operator response under validator-escalation HITL emits a `hitl.invocation.responded` span per §1.8 carrying the four-response palette outcome. The `validator.fail.*` attribute substrate per §1.10.1 surfaces in trace data alongside the audit-ledger entry; operator-burden eval primitive `expected_hitl_invocations_per_session` per §1.9 is unchanged in shape (sub-discrimination by `validator.fail.permanence` is a forward concern for D6 ingestion, not a v1.2 commitment).

### 1.10.1 Span attribute names declared by §1.10

The §1.10 discriminated pre-HITL escalation order is materialized as the **`validator.fail.*` span attribute namespace** ingested by ADR-D6 §1.2 (forward-reference; D6 §1.2 row `validator.*` is added at D6 v1.2-or-later under the accretion-pattern rule per `c7-observability` SKILL.md s10 §4.4). D5 §1.10.1 is the canonical declaration site for these attribute names. Three attribute names declared:

- **`validator.fail.class`** — fail-class enum carried per validator-failure event. Type: enum string ∈ `{transient-retry / Reflexion-recoverable / HITL-recoverable / permanent-fail-exit / terminal-fail-exit}` per `c5-validation-contract` SKILL.md s14 §7.5(d) locked five-class taxonomy. Always-emitted on every validator-failure event. Ownership: emitted by C5 at fail-classification time. Cardinality is bounded (five values).

- **`validator.fail.cause_attribution`** — cause-attribution annotation per fail-class signal. Type: enum string from the open set per `c5-validation-contract` SKILL.md (`network_timeout`, `provider_outage`, `model_misfire`, `contract_violation`, `schema_violation`, `semantic_disagreement`, `policy_denial`, `human_rejection`, `time_budget_exhaust`, `capability_shortfall`) plus F5-introduced refinements (`secret_unknown`, `secret_unavailable`, `secret_expired`, `secret_locked`, `secret_revoked` per ADR-F5 §Decision). Always-emitted on every validator-failure event per s12 §7.5(a) standing pre-check (a fail-class without cause_attribution is FM-J per `c5-validation-contract` SKILL.md). Ownership: emitted by C5 at fail-classification time. Cardinality is medium (open set; phase-2 may add).

- **`validator.fail.permanence`** — derived discriminator boolean / enum. Type: enum string ∈ `{transient / permanent}`; derived from `validator.fail.class` (`permanent` if class ∈ {`permanent-fail-exit`, `terminal-fail-exit`}; `transient` otherwise). Always-emitted on every validator-failure event. Cardinality is bounded (two values). Rationale: provides a C7-instrumentable boolean discriminator for cross-attribute filtering and dashboard binding without requiring downstream consumers to enumerate the full five-class set. Redundant-by-construction with `validator.fail.class` but operationally useful at the dashboard / sampling-discipline layer.

**Sampling discipline.** Per `c7-observability` SKILL.md head-based-dev / tail-based-prod default, validator-failure spans carrying `validator.fail.permanence=permanent` are always-sampled (head=1.0, tail-keep-on-classification=true) regardless of base sampling rate per tamper-evidence and operator-burden traceability relevance. Validator-failure spans carrying `validator.fail.permanence=transient` follow base-rate sampling per cell.

**Capability-floor (iv) traceability.** F3 v1.1 capability-floor (iv) requires observable lifecycle including validator-failure events; §1.10.1 declares the attribute substrate for the discriminated pre-HITL escalation order at §1.10. The forward-reference to ADR-D6 §1.2 row `validator.*` is an accretion-pattern addition per `c7-observability` SKILL.md s10 §4.4; D6 v1.2-or-later incorporates the row without re-declaring the attribute names.

### 1.11 Context revalidation on HITL resume

For durable-async cells, long pause durations (e.g., 5-day Temporal `wait_condition timeout`) introduce context-rot risk — the active context at pause-time may be stale at resume-time. Resume protocol:

```
on_hitl_resume(handoff_context, operator_response):
    1. Reconstruct active context from durable state (C3 stake)
    2. Revalidate: for each external reference in state_summary,
       refetch and diff against captured snapshot
    3. If material diff detected → re-emit HITL with updated context
       (per Cluster 4 §2.4.6 / §2.4.7 [HIGH] approval-fatigue mitigation:
        only re-emit on material diff, not on every irrelevant change)
    4. Apply operator response (approve/edit/reject/respond palette)
```

T-perm-2 (C2 ↔ C3 — within-vs-across-turn) F2-layer resolution stands; context revalidation composes against the existing F2 read/write contract pair without D5-layer revision.

## Rationale

**(a) Pattern this decision follows.** D5 composes Pattern Reference Catalog v1.0 §10.3 P-AS-4 (HITL approval gates as first-class action-surface primitives) with §10.1 P-CP-8 (stateless reducer / launch-pause-resume control flow) committed at F3, §10.3 P-AS-1 (sandbox isolation with per-tool trust tiers) committed at F4, and §10.3 P-AS-6 (outer-loop async tool calls). The HITL-as-tool-call structural identity per 12-Factor Factor 7 (Cluster 4 §2.4 [HIGH]) is preserved at the C4 capability-declaration layer; the HITL-as-checkpoint structural identity (Cluster 4 §2.4 [HIGH] establishing "interrupt/resume as structurally identical to durable-execution checkpoint") is preserved at the F3 lifecycle layer; D1's per-engine-class HITL primitive shape (§1.2 mapping table) is the substrate composition surface. The synchrony-class taxonomy (sync-blocking | durable-async | both-by-tier | two-agent-observer) is the deliberation surface across the candidate space; the 2D matrix at §1.2 commits the class per cell.

**(b) Persona-constraint application.** Persona §2 bridging-arc traversal mandates preservation of all three persona tiers as parametric axes — committing a single persona tier at D5 (rejected option OD-3.B) compresses two decisions into one and forces D5 revisit on every bridging-arc traversal, structurally breaking the harness-level HITL contract. Persona §4 "mathematically incompatible with operator-in-loop-on-every-failure HITL — HITL must be selective" is operationalized at §1.5 via the per-tool tier annotation × per-MCP-server trust tier × persona-tier floor multiplicative composition — selectivity is the structural property the gate-level rule guarantees. Persona §8.1 software-engineering and §8.2 content-creation natural-synchronous-at-design-time aligns with sync-blocking PRIMARY at solo-developer × {save-point-checkpoint, pure-pattern-no-engine} cells; Persona §8.3 pipeline-automation "often scheduled or event-triggered, not interactive" aligns with durable-async PRIMARY at team-binding × event-sourced-replay; Persona §10.4 compliance-readiness foundational primitives (hash-chained audit ledger, comprehensive observability) is operationalized at §1.4 per-persona-tier ledger cryptographic shape and §1.8 HITL-event span schema.

**(c) T-perm-1 D5-layer stance.** T-perm-1 (C4 ↔ C10 — capability vs gating) is the direct engagement at D5. The tension cannot be collapsed without sacrificing either C4's predictability contract (developer-declared `tier` annotation honored) or C10's safety contract (persona-tier and trust-tier floors enforced). The D5-layer resolution shape — multiplicative composition at §1.5 with the locked tunable parameter specialized to `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier` — preserves both contracts: the developer's annotation is one input to the union floor, the operator's persona-tier and the server's trust-tier are co-equal inputs, and the blast-radius taxonomy provides per-tool floor enforcement. The cross-deployment monotonicity at §1.5.2 ensures bridging-arc traversal cannot regress the gate level.

**(d) Cross-axis composition.** D5 composes against:

- **D1 substrate** — per-engine-class HITL primitive shape inheritance from D1 §1.2; D5 §1.2 matrix orthogonally adds the persona-tier axis without revising D1.
- **F3 lifecycle** — capability-floor (iv) observable lifecycle extended with §1.8 HITL-event span schema; manifest-declaration default per F3 invocation-discipline applies to HITL placement declarations.
- **F4 sandbox tier** — per-tool sandbox tier per F4 graduated-isolation principle is one input to §1.5 `blast_radius_floor`; high-blast-radius tools requiring strong-tier sandbox compose against `ask`-floor at the gate-level rule.
- **F1 routing** — escalate-model-tier-on-validator-failure per Cluster 4 §2.2.3 [HIGH] composes pre-HITL per §1.10; F1 chain-advancement subscribes to §1.8 `hitl.gate.evaluated` and `hitl.invocation.opened` spans.
- **F2 state-ledger** — §1.4 ledger cryptographic shape composes against F2 state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)`; HITL ledger entries are F2-substrate-resident with persona-tier-conditional cryptographic enrichment.
- **D2 sandbox provider (forward-reference)** — gate-level composition rule at §1.5 takes per-tool blast-radius as input; D2 sandbox-provider selection determines runtime enforcement of blast-radius floors. D5 does not commit D2; D2 forward-references D5 §1.5 as the composition contract.
- **D4 multi-agent topology (forward-reference)** — sub-agent HITL composition per §1.3 `sub-agent-boundary` placement; cascade-policy declaration at the topology primitive interface (§1.3.1) is the D4-layer composition contract; D4 references D5 §1.3 in its §Rationale.
- **D6 observability backend (forward-reference)** — §1.8 HITL-event span schema is the ingestion contract for D6; backend-specific span enrichment composes against this schema without revising it.

## Consequences

**(a) What becomes possible.**

- **Per-persona-tier × D1-engine-class HITL primitive shape lookup** at persona-tier-binding-time without D5 revisit. The 2D matrix at §1.2 is the lookup surface; the persona-tier-binding-time selection contract at §1.7 makes downstream candidate selection mechanical.
- **Selective HITL mechanically expressible at the F3-lifecycle layer** (per F3 v1.1 §Rationale (a) anticipation) — the §1.5 gate-level composition rule is the selectivity mechanism; per-tool tier annotation × per-MCP-server trust tier × persona-tier-floor × blast-radius-floor union determines per-action HITL invocation without operator-in-loop-on-every-failure burden.
- **Hash-chained audit ledger composition with HITL events by construction** — §1.4 per-persona-tier ledger cryptographic shape and §1.8 HITL-event span emission together produce tamper-evident HITL audit records composing with F2 state-ledger and F3 lifecycle event substrate. Persona §10.4 compliance-readiness foundational primitive is operationalized.
- **Bridging-arc persona tier upgrade without HITL contract revision** — §1.5.2 cross-deployment monotonicity ensures persona-tier upgrade raises the effective gate level for in-flight workflows without code change; tier downgrade is structurally prohibited; harness-level HITL contract holds across the bridging arc.
- **Calibrated approval-rate distribution per tool-tier annotation** via §1.9 Husain loop application — operator responses are the calibration input; mis-calibrated annotations surface via post-action audit-ledger flagging.

**(b) What becomes harder.**

- **Per-persona-tier ledger cryptographic shape implementation** — three distinct ledger shapes (append-only SQLite | hash-chained SQLite | hash-chain + signature) must be implemented and tested; cryptographic-signature shape at multi-tenant-compliance requires key management composing with F5 secrets architecture.
- **Multiplicative gate-level composition rule enforcement at every tool invocation** — §1.5 composition is hot-path; per-tool blast-radius lookup, per-MCP-server trust-tier lookup, and persona-tier floor evaluation must be O(1) at runtime; caching strategy composes with C2 context engineering.
- **Sub-agent HITL composition with cascade-policy declaration** — every multi-agent topology must declare `cascade_policy` per topology primitive interface (§1.3.1); D4 deliberation must specify cascade-policy semantics composing with D5 §1.3 `sub-agent-boundary` placement.
- **HITL-event span volume and storage** — §1.8 always-sampled HITL spans produce unbounded telemetry volume at high `expected_hitl_invocations_per_session`; D6 observability backend must accommodate the always-sampled discipline.
- **Tool-tier annotation calibration eval discipline** — §1.9 calibration targets and Husain loop application require holdout construction and judge-human alignment work; C8 eval methodology must include the calibration eval as standing primitive.
- **Context revalidation on HITL resume implementation** — §1.11 protocol requires per-external-reference snapshot capture at pause-time and diff at resume-time; capture surface composes with C2 HandoffContext shape and C3 durable state.

**(c) What is now constrained downstream.**

- **D2 sandbox provider** must accommodate per-tool blast-radius taxonomy as input to §1.5 gate-level composition; sandbox provider candidates (Firecracker / gVisor / Kata / Docker per Persona §10.3 F4-tech) compose against blast-radius floors.
- **D4 multi-agent topology** must declare `cascade_policy` per §1.3.1 and propagate sub-agent HITL invocations to parent topology layer per §1.3 `sub-agent-boundary` placement; sub-agent interrupt stranding mitigation is D4-layer commitment.
- **D6 observability backend** must ingest §1.8 HITL-event span schema with always-sampled discipline; backend selection (OTel-to-vendor vs dedicated LLM-observability platform per Pattern Reference Catalog v1.0 §11.3.2 D6) must accommodate compliance-relevant tamper-evidence capture.
- **F5 secrets architecture (downstream)** must accommodate cryptographic-signing key for multi-tenant-compliance ledger entries per §1.4; key rotation composes with F5 cross-deployment secrets bridge principle.
- **Persona-tier-binding-time selection** per §1.7 contract is the gate downstream of Phase 3 — operator must declare persona tier and deployment surface before specific candidate selection within the cell.

**(d) Permanent-tension ledger updates.**

- **T-perm-1 promoted to Layer 3** with D5-layer resolution shape `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier`. Specializes the previously locked tunable `per_tool_gate_level × per_mcp_server_trust_tier` per `references/output-templates.md`.
- **T-perm-3 D1-layer resolution shape** `topology_fault_handling` stands; D5 surfaces the tension at sub-agent boundary HITL cascade-timeout composition (§1.6) without D5-layer revision.
- **T-perm-2 F2-layer resolution shape** stands per F3 v1.1 §References explicit framing; D5 surfaces the tension at HandoffContext serialization seam and §1.11 context revalidation without D5-layer revision.

**(e) Remaining D-ADR forward-references.**

- D2 references D5 §1.5 gate-level composition rule (`blast_radius_floor` runtime enforcement).
- D4 references D5 §1.3 sub-agent-boundary HITL placement and §1.3.1 `cascade_policy`.
- D6 references D5 §1.8 HITL-event span schema (always-sampled ingestion contract).

## Alternatives considered

**(1) Synchrony-class alternatives per §11.3.2 D5 enumeration evaluated and not adopted as harness-uniform default:**

- **Sync-blocking-only** (cline / OpenHands / LangGraph `interrupt()` uniform commitment) — rejected because Persona §8.3 pipeline-automation "often scheduled or event-triggered, not interactive" and Persona §4 "mathematically incompatible with operator-in-loop-on-every-failure HITL" are structurally incompatible with sync-blocking-only at team-binding and multi-tenant-compliance tiers.
- **Durable-async-only** (HumanLayer / ACP / Temporal `wait_condition` uniform commitment) — rejected because Persona §8.1 / §8.2 design-time HITL-naturally-synchronous and Persona §2 design-time-sole-operator make durable-async overhead unwarranted at solo-developer × {save-point-checkpoint, pure-pattern-no-engine} cells.
- **Two-agent-observer-only** (disler/the-verifier-agent uniform commitment) — rejected because two-agent-observer is a verification pass, not a synchrony class; treating it as the primary synchrony commitment loses the four-response palette operator contract per §1.1.
- **Both-by-tier-only** (Roo Code autonomy slider / Claude Code permission model uniform commitment) — rejected because both-by-tier is a per-tool overlay, not a synchrony class; the underlying engine-class lifecycle ownership (§1.2) determines whether the per-tool annotation routes through sync-blocking or durable-async primitives.

**(2) Scope-shape alternatives evaluated and not adopted:**

- **OD-1.B synchrony-class-only narrowed scope** — rejected because per-class candidate semantics differences (`interrupt()` re-entry bug pattern per Cluster 4 §2.4.5 [HIGH], webhook lost-update mitigation, approval-fatigue patterns per Cluster 4 §2.4.6 / §2.4.7 [HIGH]) are the deliberation surface; class-only scope produces under-closure relative to the full nine-candidate competitive scope.
- **OD-1.C solo-developer-tier-narrowed scope** — rejected because pre-commits a persona-tier dimension Persona §2 records as bridging-arc-traversal-required; collapses the bridging-arc parametric axis prematurely.

**(3) Framing alternatives evaluated and not adopted:**

- **OD-3.B persona-tier-assumed-at-D5** — rejected because forces a persona-tier commitment Persona §2 records as bridging-arc-traversal-required; compresses two decisions (D5 synchrony commitment + persona-tier binding) into one; tier change downstream triggers D5 revisit per Workflow §4.1.2 Class-2 fork.
- **OD-3.C synchrony-class-only-at-D5** — rejected because produces under-closure relative to per-cell commitment; class-only commitment without per-tier candidate evaluation leaves the production-pattern witnesses (cline / kilocode / Roo Code / OpenHands sync-blocking; HumanLayer / ACP ContactChannel durable-async; Claude Code permission model / kilocode `--auto` both-by-tier; disler the-verifier-agent two-agent-observer) unconnected to D5's decision rationale.

**(4) Voice-slate alternatives evaluated and not adopted:**

- **OD-2.B anchor-plus-consultants downgrade** — rejected because loses C2 HandoffContext stake (Cluster 4 §2.4.3 [HIGH]), C6 model-tier-as-HITL-alternative stake, C7 HITL-event-span stake (F3 capability-floor (iv)), and C8 expected-HITL-invocations operator-burden stake — all of which compose with D5 substrate choice per §1.8, §1.9, §1.10.
- **OD-2.C single-voice with handled-by-reference** — rejected because forfeits T-perm-1 surfacing entirely; D5's direct engagement on T-perm-1 requires C4 + C10 co-primaries.

**(5) Harness-uniform synchrony commitment** — rejected because Persona §10.2 explicit constraint "HITL synchrony — Must be selective (math of tens-concurrent + 99.9%); UX shape open" plus Persona §2 bridging-arc traversal plus D1 §1.2 per-engine-class lifecycle-ownership variation make harness-uniform synchrony structurally incompatible with the persona × deployment-surface × workload-class space.

## References

### Substrate dependency declaration (shape 1 per Workflow v1.1 §2.3.3.1)

- Cluster 5 V2 §3 D5 line 207 (within `Agent_Harness_Architecture__Deployment_Surfaces__Anthropic_Primitives__and_Foundational_Tradeoffs.md`): "D5. HITL synchrony — **persona-dependent**: solo developer → synchronous interactive; team or production → async approval queues; enterprise compliance → both, with audit-ledger." Derived from F3 + D1.

### Pattern Reference Catalog source citations (shape 2)

- Pattern Reference Catalog v1.0 §10.3 P-AS-4 (HITL approval gates as first-class action-surface primitives) — load-bearing pattern at D5 layer; HITL-as-tool-call (12-Factor F7); synchrony-divergence variation point.
- Pattern Reference Catalog v1.0 §10.1 P-CP-8 (stateless reducer / launch-pause-resume control flow) — F3-cited; HITL pause/resume substrate.
- Pattern Reference Catalog v1.0 §10.3 P-AS-1 (sandbox isolation with per-tool trust tiers) — composes with HITL gate-tier per tool at §1.5 `blast_radius_floor`.
- Pattern Reference Catalog v1.0 §10.3 P-AS-6 (outer-loop async tool calls) — durable-async HITL substrate.

### Per-axis recommendation citation (shape 3)

Pattern Reference Catalog v1.0 §11.3.2 D5 lines 3150–3160 verbatim:

> **D5. HITL synchrony** — *persona-dependent*: solo developer → synchronous interactive; team or production → async approval queues; enterprise compliance → both, with audit-ledger. Load:
> - **humanlayer/12-factor-agents** — Factor 7 (contact humans with tool calls).
> - **cline/cline** — Per-step approval gate (synchronous interactive).
> - **Kilo-Org/kilocode** — Approval gates + `--auto` for CI/CD (both modes).
> - **RooCodeInc/Roo-Code** — Configurable autonomy slider.
> - **langgenius/dify** — Human Input node (v1.13.0).
> - **humanlayer/agentcontrolplane** — `ContactChannel` CR (mesh-pattern async).
> - **langchain-ai/deepagents** — HITL approval gates.
> - **disler / the-verifier-agent** — Two-agent observer pattern.
> - **OpenHands/OpenHands** — Per-action approval.

### Parent F-ADR / D-ADR citations (shape 4)

- ADR-F3 v1.1 §Decision: capability-requirement floor (i)–(iv); (iv) observable lifecycle composes with §1.8 HITL-event span schema. ADR-F3 §Rationale (a) anticipation: "HITL primitive composes with durable-execution lifecycle by construction... selective HITL becomes mechanically expressible at the F3-lifecycle layer."
- ADR-D1 v1 §1.2: per-deployment-surface engine-class mapping; per-engine-class HITL primitive shape source for §1.2 matrix. ADR-D1 v1 §1.3: D1-layer T-perm-3 resolution shape `topology_fault_handling` inherited as adjacency-only at §1.6.
- ADR-F4 §Decision: sandbox isolation tier per F4 graduated-isolation principle is one input to §1.5 `blast_radius_floor`.
- ADR-F2 §(c) state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)`: F2 substrate composition for §1.4 ledger cryptographic shape.
- ADR-F1 §"Permanent tensions engaged" T-perm-3 acceptance: F1-layer resolution stands; D5 §1.10 composes against F1 chain-advancement at the escalate-model-tier-on-validator-failure seam.
- **ADR-F5 §Decision (v1.2 — added per F2-13 closure):** secrets bridge `fetch_secret(name, scope) -> SecretRef` abstraction with tier-aware resolution (F5 dev-tech OS keychain at process tier; F5 prod-tech vault at microVM/full-VM tiers). F5's `outputs_hash = sha256(secret.name || secret.scope || secret.last_rotated_at)` structure-not-content audit composition is the secret-access-event fingerprinting discipline F5 anchors; D5 §1.4 signing-key resolution composes against F5's `fetch_secret` abstraction with the signing key treated as a secret resolved through F5's tier-aware bridge (signing-key residence per persona tier: F5 dev-tech keychain at team-binding; F5 prod-tech vault at multi-tenant-compliance with `audit_signing_key_scope ∈ {deployment / tenant}` operator-tunable). F5 §Deferred D-ADRs identifies the specific secrets-provider selection as deployment-surface-bound per Pattern Reference Catalog v1.0 §11.3.2 derivative; the multi-tenant-compliance signing-key residence inherits this deferral.
- **ADR-D2 v1 §1.8 (v1.2 — added per F2-15 precedent shape):** sandbox-violation fail-class table with explicit permanent-fail-vs-transient handling (`escape_attempt` / `egress_denied` / `signal` → permanent-fail, NO retry, immediate HITL; `timeout` / `oom` → transient-fail, C9 backoff + retry per Cluster 3 retry protocol [HIGH]); D2 §1.8 prose closing paragraph "Permanent-fail violations skip the staircase and go directly to HITL" is the precedent shape D5 §1.10's discriminated five-class encoding generalizes from sandbox-violation to validator-failure-at-large per the locked C5 retry-exit taxonomy.
- **OTel GenAI Semantic Conventions 1.41.0 (v1.3 — added per F2-iter2-02 Reading 1 closure):** `gen_ai.tool.name` canonical attribute declaration on the `tool.call` span (per `opentelemetry.io/docs/specs/semconv/gen-ai/`). Under operator-selected Reading 1 canonical pass-through, the v1.1 `hitl.gate.tool` event-scoped attribute is retired; the gated tool's name is read from `gen_ai.tool.name` on the parent `tool.call` span via trace correlation. Preserves cross-event attribute-name unity per Pattern P1 mechanical-alignment discipline.
- **ADR-D3 v1.1 §1.8.1 — refined citation (v1.3 — F2-iter2-02 Reading 1 closure):** `mcp.server.name` canonical attribute declaration on the `mcp.tool.call` span. Under operator-selected Reading 1 canonical pass-through, the v1.1 `hitl.gate.mcp_server` event-scoped attribute is retired; the gated MCP server's identity is read from `mcp.server.name` on the parent `mcp.tool.call` span via trace correlation. D3 v1.1 §1.8.1 is the canonical declaration site per Workflow v1.3 §2.3.3.1 clause (ii) concept-attribute joint declaration discipline.

### Persona document trace (shape 5 — required per D5 persona-dependent classification)

- `Persona_Document_v1` §2 (User — bridging-arc persona; sole operator at design-time, team or multi-tenant binding state later) — persona-tier triplet axis source for §1.2 matrix.
- `Persona_Document_v1` §3 (Workloads — heterogeneous primary task classes) — workload-class context for synchrony-class differentiation.
- `Persona_Document_v1` §3.1.1 (Software / web engineering) — natural-synchronous-at-design-time evidence for solo-developer × {save-point-checkpoint, pure-pattern-no-engine} sync-blocking PRIMARY commitment.
- `Persona_Document_v1` §3.1.2 (Content creation) — natural-synchronous-at-design-time per §8.2 evidence.
- `Persona_Document_v1` §3.1.3 (Pipeline & automation) — `often scheduled or event-triggered, not interactive` per §8.3 evidence for team-binding × event-sourced-replay durable-async PRIMARY commitment.
- `Persona_Document_v1` §3.1.4 (Research, analysis, knowledge work) — mixed HITL synchrony per §8.4.
- `Persona_Document_v1` §3.2 (Secondary / future task classes; workload-class extensibility flag) — accommodation surface preserved across persona tiers.
- `Persona_Document_v1` §4 (Scale — 99.9%+ completion SLO at tens-concurrent): "mathematically incompatible with operator-in-loop-on-every-failure HITL — HITL must be selective, with the deterministic outer harness absorbing most recovery" — selectivity mechanism source for §1.5 multiplicative composition rule.
- `Persona_Document_v1` §5 (Integration surface) — broad action surface evidence for §1.5 `blast_radius_floor` taxonomy applicability.
- `Persona_Document_v1` §6 (Hard constraints — per-workload-class cost ceiling; compliance regime open) — composition-cost source for §1.9 calibration targets.
- `Persona_Document_v1` §7 (Soft preferences — Python-first; pragmatic-mixed ecosystem affinity) — implementation-affinity context.
- `Persona_Document_v1` §8.1 (Software / web engineering — F3 mixed; multi-step session shape dominant) — sync-blocking PRIMARY rationale at solo-developer cells.
- `Persona_Document_v1` §8.2 (Content creation — `[HIGH] HITL naturally synchronous at design-time (operator review-in-loop); at multi-tenant binding, async HITL becomes feasible`) — persona-tier transition evidence.
- `Persona_Document_v1` §8.3 (Pipeline & automation — `[MODERATE] Often scheduled or event-triggered, not interactive`; durable-execution-spine territory par excellence) — durable-async PRIMARY rationale at team-binding × event-sourced-replay.
- `Persona_Document_v1` §8.4 (Research — mixed) — both-by-tier overlay applicability.
- `Persona_Document_v1` §10.1 (durable-execution capability requirement persona-answered) — F3 substrate inheritance for D5 lifecycle composition.
- `Persona_Document_v1` §10.2 (HITL synchrony — `Must be selective (math of tens-concurrent + 99.9%); UX shape open`) — direct D5 constraint source.
- `Persona_Document_v1` §10.4 (compliance-readiness foundational primitives — hash-chained audit ledger, granular access controls, encryption-at-rest, retention controls, tenant isolation, secrets rotation, comprehensive observability) — §1.4 ledger cryptographic shape and §1.8 HITL-event span always-sampled discipline source.
- `Persona_Document_v1` §11.6 (compliance regime determination — open item) — multi-tenant-compliance persona-tier-binding-time deferral source.
- `Persona_Document_v1` §11.7 (vendor / IP-handling restrictions at multi-tenant binding — open item) — per-MCP-server trust-tier downstream binding source.
- `Persona_Document_v1` §11.9 (future-state operator interaction surface — open item) — operator-interaction-surface deferral; §1.1 four-response palette is interaction-surface-agnostic.
- `Persona_Document_v1` §11.10 (multi-tenant tenant-isolation specifics — open item) — D2 trust-tier downstream constraint source for §1.5 `per_mcp_server_trust_floor`.

### Substrate research citations (corpus-derived)

- Cluster 4 §2.4 [HIGH] (HITL design — sync-blocking vs durable-async; HITL interrupt/resume structurally identical to durable-execution checkpoint per 12-Factor Factor 6; LangGraph `interrupt()` as special case of checkpoint substrate; Temporal `wait_condition timeout=days` durable-async primitive) — synchrony-class taxonomy source for §1.2 matrix.
- Cluster 4 §2.4.3 [HIGH] (HandoffContext shape: `proposed_action`, `agent_confidence`, `failed_attempts`, `alternatives_considered`, `state_summary`, `audit_trail_link`, `retry_history`; tiered-autonomy approval-fatigue mitigation) — §1.3.1 topology primitive interface signature source.
- Cluster 4 §2.4.4 [HIGH] (sub-agent HITL composition; sub-agent interrupt stranding; cascade timeout composition with parallel sibling sub-agents) — §1.3 `sub-agent-boundary` placement and §1.6 `cascade_policy` composition source.
- Cluster 4 §2.4.5 [HIGH] (`interrupt()` re-entry bug pattern; webhook lost-update mitigation requirements) — §1.6 idempotency-keyed signal delivery requirement source.
- Cluster 4 §2.4.6 / §2.4.7 [HIGH] (approval-fatigue mitigation patterns) — §1.9 calibration targets and §1.11 material-diff-only re-emit source.
- Cluster 4 §2.2.3 [HIGH] retry protocol (3rd-validator-fail → human-handoff; 2nd-validator-fail → re-prompt-with-different-system-prompt OR escalate-model-tier) — §1.10 pre-HITL escalation order source.
- Cluster 4 §2.2.7 [HIGH] (Stripe-style idempotency-key construction `sha256(conversation_id || step_index || tool || canonical_args)`) — §1.6 webhook signal delivery composition source.
- Anthropic, "Building Effective Agents," Schluntz & Zhang, Dec 2024, anthropic.com/engineering/building-effective-agents — pattern catalog source for evaluator-optimizer / reflection composition with HITL escalation.
- Anthropic, "Effective harnesses for long-running agents," Nov 26 2025, anthropic.com/engineering/effective-harnesses-for-long-running-agents — long-running harness composition source.
- LangChain, LangGraph human-in-the-loop documentation, docs.langchain.com/oss/python/langchain/human-in-the-loop — `interrupt()` + Command resume primitive source for save-point-checkpoint × solo-developer cell.
- Temporal, HITL documentation, docs.temporal.io/ai-cookbook/human-in-the-loop-python — `wait_condition` + signal-handler with `timeout=days` primitive source for event-sourced-replay × team-binding cell.
- HumanLayer, "12-Factor Agents," Factor 7 (contact humans with tool calls), github.com/humanlayer/12-factor-agents — HITL-as-tool-call structural identity source.
- HumanLayer, agentcontrolplane (ACP) `ContactChannel` CR mesh-pattern, github.com/humanlayer/agentcontrolplane — durable-async × reconciler-loop primitive source.
- Anthropic, Claude Code permission model documentation — `deny → ask → allow` per-tool tier annotation source for both-by-tier overlay.

### Workflow and skill discipline references

- `Project_Workflow_v1_1.md` §2.3.3 (Phase 3b D-ADR exit criteria — all six D-ADRs filed; each References section satisfies §2.3.3.1 discipline).
- `Project_Workflow_v1_1.md` §2.3.3.1 (References-section discipline for Phase 3b D-ADRs — five declaration shapes required; shape 5 mandatory for persona-dependent D-ADRs).
- `Project_Workflow_v1_1.md` §3.2 (Phase dependencies — D-ADR composition against F-ADR parent + Persona document + Cluster 5 V2 §3 substrate dependency declaration).
- `Project_Workflow_v1_1.md` §5.1 DP-1 (Phase 3a/3b execution-agent decision — DP-1-A full-council default applied at Phase 3b kickoff; DP-1-A confirmed at OD-2.A).
- `council-orchestrator` skill (`/mnt/skills/user/council-orchestrator/SKILL.md`) — convening discipline; Convening Block + CCR + voice contributions + TENSION block emission; T-perm-1 known-permanent labeling.
- `c11-operator-local` SKILL.md — HITL primitive ownership; four-response palette; approval queue sqlite schema; eleven-trigger HITL catalog source.
- `c10-action-safety` SKILL.md — per-MCP-server trust framework; four-tier blast-radius taxonomy; eleven-trigger HITL catalog co-citation; hash-chained audit ledger discipline.
- `c4-tools-integration` SKILL.md — per-tool tier annotation contract `tier ∈ {auto, ask, deny}`; HITL-as-tool-call structural identity; strict-mode contract.
- `c1-orchestration-control` SKILL.md — HITL placement in topology; sub-agent boundary; T-perm-3 adjacency.
- `c3-state-persistence` SKILL.md — durable state across HITL pause; CoALA episodic / semantic / procedural memory tier residence.
- `c5-validation-contract` SKILL.md — validator-failure escalation contract; retry-exit criteria.
- `c9-reliability-recovery` SKILL.md — timeout-degradation modes; circuit breaker; idempotency-keyed signal delivery.
- `c2-context-engineering` SKILL.md — HandoffContext within-turn assembly; context-revalidation-on-resume.
- `c6-model-routing` SKILL.md — escalate-model-tier-on-validator-failure as pre-HITL composition; per-tier model binding for handoff-context summarization.
- `c7-observability` SKILL.md — HITL-event span schema; structure-not-content discipline; always-sampled HITL spans; cost-attribution-per-span.
- `c8-eval-engineer` SKILL.md — `expected_hitl_invocations_per_session` operator-burden eval primitive; Husain manual-review→categorize→automate→align loop; tool-tier annotation calibration eval.
- spec-writer s3 §6.3 (permanent-tension-ledger tunable-parameter encoding architecture) — T-perm-1 D5-layer tunable parameter shape source.
- spec-writer skill (`/mnt/skills/user/spec-writer/SKILL.md`) — synthesis primitive applied at v1.1 revision-pass authoring per Phase 3c-CK iteration 1 close handoff §5.1 Path A skill mapping for Pattern P1 mechanical-alignment passes; applied at v1.2 revision-pass authoring (substantive content additions) ingesting council-orchestrator output per Phase 3c-CK iter-2 pre-entry handoff §3.2.
- council-orchestrator skill (`/mnt/skills/user/council-orchestrator/SKILL.md`) — convening discipline applied at v1.2 authoring; Convening Block + CCR + voice contributions emitted for F2-13 (C11 primary anchor; C10 co-primary; C3 / C7 consultants) and F2-15 (C5 primary anchor; C9 co-primary; C6 / C11 / C10 consultants; C7 handled-by-reference); cross-finding integration note emitted per handoff §2.3; T-perm-1 / T-perm-2 / T-perm-3 carried forward unchanged (no TENSION block emitted; voices reached substantive agreement).
- `Project_Workflow_v1_2.md` §3.1 — `Status: Proposed` preservation discipline on revised D-ADRs until P3c-CK clearance; D5 v1.1 carries Proposed posture into iteration 2 entry; D5 v1.2 inherits the same posture.
- `Project_Workflow_v1_2.md` §4.1.2 — Class-2 finding resolution path: revised ADR with version bump in the artifact + change-note inline. D5 v1.1 instantiates this shape for F2-06 + F2-08; D5 v1.2 instantiates this shape for F2-13 + F2-15.
- `Adversarial_Review_3c.md` F2-06 (Phase 3c F-6 / reviewer-confirmed Class 2 — Pattern P1 attribute prefix drift: `hitl.*` events declared at D5 §1.8 with un-prefixed per-event attributes against D6 §1.2 prefixed declarations) — v1.1 revision driver.
- `Adversarial_Review_3c.md` F2-08 (reviewer-surfaced Class 2 — Pattern P1 concept-vs-attribute split: `audit.*` attribute names introduced at D6 §1.2 not declared at D5 §1.4) — v1.1 revision driver.
- `Adversarial_Review_3c.md` F2-13 (signing-key resolution at §1.4 multi-tenant-compliance row not specified — F5 secrets bridge composition + signature algorithm specification missing; §References Shape 4 add F5) — v1.2 revision driver.
- `Adversarial_Review_3c.md` F2-15 (D5 §1.10 pre-HITL escalation order does not distinguish permanent-fail from transient — D2 §1.8 explicit handling vs D5 source ADR lacks anchor) — v1.2 revision driver.
- Phase 3c-CK iteration 1 close handoff §4.1 D5 row (revision scope: `audit.*` attribute names declared at source via §1.4 amendment; `hitl.*` prefix on all attribute names at §1.8; F2-13 signing-key resolution and F2-15 permanent-fail handling deferred to council-orchestrator session) and §5.1 Path A skill-routing guidance — v1.1 revision-scope authority.
- Phase 3c-CK iter-2 pre-entry handoff D5 substantive bundle (filed 2026-05-10 alongside D5 v1.1; specifies F2-13 + F2-15 council-orchestrator session scope, voice load list, expected exit shape per §4, hand-off to spec-writer per §3.2) — v1.2 revision-scope authority.
- **`Adversarial_Review_3c_iter2.md` F2-iter2-02 (Class 2 — D5 §1.8 cross-namespace canonical-naming: gate-event `hitl.gate.tool` and `hitl.gate.mcp_server` reference canonical identities on parent spans) — v1.3 revision driver.**
- **`Adversarial_Review_3c_iter2.md` F2-iter2-03 (Class 2 — D5 §1.4 secret_rotation_event dual-signature sqlite schema not specified) — v1.3 revision driver.**
- **Phase 3c-CK iter-2 close → iter-3 entry operator-action guide (filed 2026-05-11) §5.1 / §5.2 / §7.1 / §7.2 — v1.3 revision-scope authority; §7.1 / §7.2 specify the two operator decisions (Reading 1 / Reading 2 at F2-iter2-02; Option (a) / (b) / (c) at F2-iter2-03) elicited via `ask_user_input_v0` at iter-3 revision-pass session entry.**
- **Operator-decision dispositions filed at iter-3 revision-pass entry via `ask_user_input_v0`: OD-iter3-1 F2-iter2-02 Reading 1 canonical pass-through selected (drop event-scoped names; gate-event consumer reads canonical attributes via trace correlation); OD-iter3-2 F2-iter2-03 Option (a) two-row pattern selected (sqlite schema extended with `rotation_correlation_id` UUID column joining rotation-pair entries).**

### Convening artifact citations (from this session's substrate review)

- Convening Block + CCR + voice contributions (C11 primary anchor; C10 / C4 / C1 co-primaries; C3 / C5 / C9 / C2 / C6 / C7 / C8 consultants) — preceding response in this session, segment 1 of 2.
- TENSION block (T-perm-1 promoted to Layer 3 with D5-layer resolution shape `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier`; T-perm-3 / T-perm-2 adjacencies carry-forward by reference) — preceding response in this session, segment 1 of 2.
- **Convening Block + CCR + voice contributions (v1.2 council-orchestrator session at F2-13 + F2-15 substantive content additions; F2-13 segment: C11 primary anchor, C10 co-primary, C3 + C7 consultants; F2-15 segment: C5 primary anchor, C9 co-primary, C6 + C11 + C10 consultants, C7 handled-by-reference) — Phase 3c-CK iter-2 pre-entry council session preceding this v1.2 spec-writer authoring.**
- **Cross-Finding Integration Note (F2-13 ↔ F2-15 interactions: permanent-fail-exit ledger entries use uniform signing-key resolution; HITL invocations under permanent-fail-exit write signed ledger entries per §1.4 + §1.4.1 v1.2 commitments) — same v1.2 council session.**
- **Operator-decision dispositions filed at v1.2 council session close: OD-1 signing-key residence at multi-tenant-compliance deferred as `audit_signing_key_scope ∈ {deployment / tenant}` operator-tunable axis at multi-tenant-binding-time (Reading 2 per Persona §11.10 deferral); OD-2 signature algorithm Ed25519 default with operator-tunable `audit_signature_algorithm ∈ {ed25519 / ecdsa-p256 / rsa-pss-2048}` (Reading 2); OD-3 permanent-fail signal origination substrate-dispositive per `c5-validation-contract` SKILL.md s14 §7.5(d) (no operator action — C5 owns classification, C9 owns retry-budget-exit, both route to staircase-skip).**

---

*Filed 2026-05-10 at Phase 3b Stage 1 close per Workflow v1.1 §2.3.3; revised v1 → v1.1 same date at P3c-CK iter-1 close per `Project_Workflow_v1_2.md` §4.1.2 (F2-06 hitl.* attribute prefix discipline at §1.8; F2-08 audit.* attribute names back-declared at §1.4 source via new §1.4.1; F2-13 signing-key resolution and F2-15 permanent-fail handling deferred to council-orchestrator C11+C10 / C5+C9 sessions per Phase 3c-CK iteration 1 close handoff §5.1; session handoff for the council-orchestrator session filed alongside this revision); revised v1.1 → v1.2 same date at P3c-CK iter-2 pre-entry council-orchestrator session per `Project_Workflow_v1_2.md` §4.1.2 (F2-13 signing-key resolution at §1.4 multi-tenant-compliance row composing with ADR-F5 secrets bridge — Ed25519 default with operator-tunable `audit_signature_algorithm`, key-period rotation model, cross-deployment transition discipline, sqlite schema extension, F5 prod-tech residence with `audit_signing_key_scope ∈ {deployment / tenant}` operator-tunable at multi-tenant-binding-time; F2-15 permanent-fail-vs-transient discriminator at §1.10 pre-HITL escalation order — discriminated five-class encoding per locked `c5-validation-contract` SKILL.md s14 §7.5(d) reconciliation, transient staircase preserved with cause-attribution-conditioned 2nd-rung branching, permanent-fail-exit / terminal-fail-exit skip-staircase routing to validator-escalation HITL per §1.3 aligning with ADR-D2 v1 §1.8 precedent shape; new §1.10.1 sub-section declares `validator.fail.*` attribute substrate; §References Shape 4 extended with F5 + D2 §1.8 citations); revised v1.2 → v1.3 2026-05-11 at P3c-CK iter-2 close revision pass per `Project_Workflow_v1_2.md` §4.1.2 (`Adversarial_Review_3c_iter2.md` F2-iter2-02 cross-namespace canonical-naming at §1.8 hitl.gate.evaluated resolved under operator-selected Reading 1 canonical pass-through — `hitl.gate.tool` and `hitl.gate.mcp_server` retired; gated tool identity read from `gen_ai.tool.name` per OTel GenAI semconv 1.41.0 and gated MCP server identity read from `mcp.server.name` per ADR-D3 v1.1 §1.8.1 via trace correlation; §1.8 closing paragraph rewritten as Reading 1 resolution prose; F2-iter2-03 secret_rotation_event dual-signature sqlite schema resolved under operator-selected Option (a) two-row pattern — §1.4 sqlite schema extended with `rotation_correlation_id` UUID column joining the two rotation-pair entries that together carry the dual signature when the rotating secret IS the audit-signing key; external-auditor verification semantics paragraph added; §References Shape 4 extended with OTel GenAI semconv 1.41.0 citation and refined ADR-D3 v1.1 §1.8.1 citation for `mcp.server.name` canonical source). Recommended next session for D5: P3c-CK iteration 3 entry adversarial review (`harness-adversarial-reviewer` skill) once D5 v1.3 + D6 v1.1 + D3 v1.1 inline fix all filed; D5 v1.3 enters as iteration-3 input artifact carrying Status: Proposed posture per `Project_Workflow_v1_2.md` §3.1 (promotion to Accepted blocked until P3c-CK clearance). D4 multi-agent topology composition forward-reference per Cluster 4 §2.4.4 [HIGH] carries forward unchanged.*