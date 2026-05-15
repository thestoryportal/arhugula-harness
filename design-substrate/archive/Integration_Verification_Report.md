# Integration Verification Report — Phase 3c

## Status

- **Filed**: 2026-05-10
- **Phase**: 3c (per `Project_Workflow_v1_2.md` §2.3.4)
- **Inputs**: 11 ADRs (F1 v1.2, F2 v1.2, F3 v1.1, F4 v1.1, F5 v1.1, D1 v1, D2 v1, D3 v1, D4 v1, D5 v1, D6 v1) + Persona Document v1 + Cluster 5 V2 §3 substrate + Pattern Reference Catalog v1.0 §11.3.1 + §11.3.2 + permanent-tension ledger
- **Operator decisions**: OD-1.A (pairwise lower-triangular 11×11 = 55 cells) / OD-2.A (full namespace × source verification, 12 namespaces) / OD-3.A (full bridging-arc verification, 8 cells)
- **Voice slate**: Full eleven-voice council per Workflow v1.2 §2.3.4 mandatory full-slate convening; per-question primary anchor selected at deliberation time per `s2-orchestrator-design.md` §3
- **Routing**: P3c-CK (NEW Workflow v1.2) per §0 Visual Summary; harness adversarial reviewer skill executes; clearance gates Phase 3d entry; D-ADR `Status: Proposed → Accepted` promotion per Workflow v1.2 §3.1 conditional on P3c-CK clearance

---

## Executive synthesis

Phase 3c cross-axis integration verification at OD-1.A / OD-2.A / OD-3.A depth produces the following composite disposition:

- **Pairwise consistency matrix (55 cells)**: 45 Consistent + 10 Adjacency (T-perm engagements) + **0 Conflict**. No Integ-1 (same-axis) or Integ-2 (cross-axis) fork triggered. Workflow v1.2 §2.3.4 exit criterion (a) **SATISFIED at coarse grain**.
- **Span schema ingestion contract verification (12 namespaces)**: source declaration ✓ (12/12); namespace collision discipline ✓ (no `gen_ai.*` shadowing); sampling discipline ✓ modulo F-9; redaction discipline ✓. **Per-attribute alignment surfaces 9 Class 2 findings (F-1 through F-9)** at 7+ namespaces — systemic per-attribute name drift between D6 §1.2 and source D-ADRs/F-ADRs (5 source D-ADRs + F4 affected). The drifts are concept-coherent but attribute-name-divergent; forward-routable to P3c-CK adversarial review without halting Phase 3c.
- **T-perm engagement coherence (3 T-perms × per-layer composition)**: T-perm-1 (C4↔C10) coherent across F4 → D5 → D2 → D3/D4 → D6 chain; T-perm-2 (C2↔C3) coherent across F1/F2/F3/F5/D2/D3/D4/D5/D6 multi-seam chain; T-perm-3 (C1↔C9) coherent across F1 → D1 → D4 → D2/D3/D5 → D6 chain. D6 ledger-reference-only carry-forward verified non-regressing for all three T-perms. Workflow v1.2 §2.3.4 exit criterion (c) **SATISFIED**.
- **Bridging-arc trace continuity (8 cells × 4 dimensions, OD-3.A)**: PASS across all valid persona-tier transitions in D6 §1.1 9-cell matrix (multi-tenant × local-development EXCLUDED). Span schema continuity ✓; sampling discipline class-preserved-or-tightened ✓; redaction discipline class-tightened-not-relaxed ✓ (solo operator-self-redact → team collector-boundary-processor → multi-tenant pre-collector eval-grade); trace storage tier monotonic-or-tightened ✓.
- **Integ-3 missing-dependency check**: All cited ADR dependencies satisfied across 11 ADRs. I1/I2/I3 formally deferred per Phase 3b §2.3.3 discretion; no ADR depends on a missing I-ADR. **No Integ-3 fork.**
- **Integ-4 cross-axis emergent property surfacing**: 4 candidates assessed; 3 addressed by ADR conjunction; **1 candidate (replay-determinism semantics across the durable boundary)** surfaced as cross-axis specification gap with disposition options requiring operator decision (D1 §1.1 row 1 / D6 §1.2 amendment vs in-session Integ-4 fork vs defer to P3c-CK).
- **TENSION block**: OMITTED per skill output template discipline (no fresh voice disagreements; known T-perms labeled-permanent; Integ-4 candidate surfaced in §7 of this report).

**Disposition**: **CONDITIONAL CLEARANCE.** Phase 3c verification SATISFIES Workflow v1.2 §2.3.4 exit criteria (a), (b), (c) at coarse grain. Fine-grain findings (9 Class 2 per-attribute alignment + 1 Integ-4 candidate replay-determinism) are forward-routable to P3c-CK adversarial review with explicit finding-list disclosure, OR resolvable in-session via D-layer amendment passes per operator direction. **Recommended path: forward-route findings to P3c-CK** (consistent with OD-2.A original framing — verification at depth at Phase 3c is the cheaper path; remaining findings at fine grain are appropriate for P3c-CK red-team).

---

## §1 Inputs verified

### §1.1 — ADR inventory (11 ADRs)

| ADR | Version | Status | Filed | References-section five-shape discipline (Step 2) |
|---|---|---|---|---|
| F1 | v1.2 | Proposed (per P3a-CK Final Clearance Audit) | 2026-05-09 (revised 2026-05-10) | n/a (P3a-CK pre-cleared four-shape discipline) |
| F2 | v1.2 | Proposed | post-P3a-CK | n/a (P3a-CK pre-cleared) |
| F3 | v1.1 | Accepted (post Step D) | post-P3a-CK | n/a (P3a-CK pre-cleared) |
| F4 | v1.1 | Accepted | post-P3a-CK | n/a (P3a-CK pre-cleared) |
| F5 | v1.1 | Proposed | post-P3a-CK | n/a (P3a-CK pre-cleared) |
| D1 | v1 | Proposed | 2026-05-10 | ✓ all 5 shapes declared |
| D2 | v1 | Proposed | 2026-05-10 | ✓ all 5 shapes declared |
| D3 | v1 | Proposed | 2026-05-10 | ✓ all 5 shapes declared |
| D4 | v1 | Proposed | 2026-05-10 | ✓ all 5 shapes declared |
| D5 | v1 | Proposed | 2026-05-10 | ✓ all 5 shapes declared |
| D6 | v1 | Proposed | 2026-05-10 | ✓ all 5 shapes declared |

### §1.2 — Five-shape References discipline carry-forward verification (Workflow v1.2 §2.3.3.1)

Per-D-ADR five-shape declaration completeness — substrate dependency / Pattern Reference Catalog source / per-axis recommendation / parent F-ADR/D-ADR / Persona document trace:

| D-ADR | Shape 1 | Shape 2 | Shape 3 | Shape 4 | Shape 5 |
|---|---|---|---|---|---|
| D1 | ✓ Cluster 5 V2 §3 D1 | ✓ §10.1 P-CP-7/-8, §10.4 P-OD-3/-13 | ✓ §11.3.2 D1 lines 3110–3118 | ✓ F3/F1/F2 | ✓ Persona 16 trace points |
| D2 | ✓ | ✓ §10.3 P-AS-1, §11.3.1 F4, §10.4 P-OD-3/-11 | ✓ §11.3.2 D2 lines 3119–3127 | ✓ F4/D1/D5/D4/D3/F1/F2/F3 | ✓ Persona 14 trace points |
| D3 | ✓ Cluster 5 V2 §3 D3 line 205 | ✓ §10.1 P-CP-3, §10.2 P-CR | ✓ §11.3.2 D3 lines 3129–3137 | ✓ F2/D1/D4/D5/F1/F3/F4 | ✓ Persona 12+ trace points |
| D4 | ✓ Cluster 5 V2 §3 D4 line 206 | ✓ §10.1 P-CP series, P-CP-8, §10.4 P-OD-3 | ✓ §11.3.2 D4 lines 3139–3148 | ✓ F3/F1/F2/D1/D5 | ✓ Persona 15+ trace points |
| D5 | ✓ Cluster 5 V2 §3 D5 line 207 | ✓ §10.3 P-AS-4/-1/-6, §10.1 P-CP-8 | ✓ §11.3.2 D5 lines 3150–3160 | ✓ F3/D1/F4/F2/F1 | ✓ Persona 19 trace points |
| D6 | ✓ Cluster 5 V2 §3 D6 | ✓ §10.4 P-OD-6/-3, §10.1 P-CP-8 | ✓ §11.3.2 D6 lines 3161–3168 | ✓ F3/D1/D5/D4/D3/D2/F4/F1/F2 | ✓ Persona 8 trace points |

**Disposition**: **PASS.** All six D-ADRs declare all five shapes; no Class 2 finding default per §4.1 discriminator (a); no systemic-pattern recurrence; no Workflow v1.2 §7 session-prompt-template revision recommendation.

**Note (non-finding)**: All six D-ADR References cite `Project_Workflow_v1_1.md` rather than v1.2 — temporally correct (D-ADRs filed 2026-05-10 under v1.1; the v1.1 → v1.2 elevation per `Project_Workflow_Revision_log.md` carries forward §2.3.3.1 unchanged). No re-filing required.

---

## §2 Pairwise consistency matrix (OD-1.A — 11 × 11 lower-triangular)

### §2.1 — Matrix summary

| Cell category | Consistent | Adjacency | Conflict | Total |
|---|---|---|---|---|
| F×F (10) | 9 | 1 (F1×F3 T-perm-3) | 0 | 10 |
| F×D (30) | 25 | 5 (F1×D1, F1×D3, F1×D4 — T-perm-3/2; F4×D2, F4×D5 — T-perm-1) | 0 | 30 |
| D×D (15) | 11 | 4 (D1×D4 T-perm-3; D2×D4, D2×D5, D4×D5 — T-perm-1) | 0 | 15 |
| **Total** | **45** | **10** | **0** | **55** |

### §2.2 — Adjacency cells by T-perm engagement

| T-perm | Adjacency cells | Specialization layers engaged |
|---|---|---|
| T-perm-1 (C4↔C10 capability vs gating) | F4×D2, F4×D5, D2×D4, D2×D5, D4×D5 | F4 four-tier set → D5 multiplicative gate-level rule (4 axes) → D2 5-axis specialization (adds `sandbox_tier`); D2 §1.4 sub-agent monotonic-ascension extension; D4×D5 cascade-policy joint resolution |
| T-perm-2 (C2↔C3 within vs across-turn) | F1×D3 | F1 explicit "deferred to the D-ADR on prompt-cache" → D3 §1.5 prompt-cache breakpoint placement contract |
| T-perm-3 (C1↔C9 control-flow vs reliability) | F1×F3, F1×D1, F1×D4, D1×D4 | F1-layer per-layer time-budget shape → D1 §1.3 `topology_fault_handling` per surface → D4 §1.6 `topology_fault_handling × workload_class × topology_pattern` 3-axis multiplicative; D1×D4 joint 2D matrix workload-class × engine-class composition |

### §2.3 — Disposition

**Zero Conflict cells.** No Integ-1 / Integ-2 fork triggered. Workflow v1.2 §2.3.4 exit criterion (a) *"Consistency matrix shows zero unresolved contradictions"* — **SATISFIED at the pairwise grain**. (Fine-grain per-attribute alignment surfaces 9 Class 2 findings — see §3.)

---

## §3 Span schema ingestion contract verification (OD-2.A — 12 namespaces)

### §3.1 — Per-namespace verification matrix

| # | Namespace | Source | (a) Source declared | (b) Per-attribute alignment | (c) Namespace collision | (d) Sampling discipline | (e) Redaction class |
|---|---|---|---|---|---|---|---|
| 1 | `gen_ai.*` | OTel GenAI semconv 1.41.0 [HIGH] | ✓ | ✓ Stable / Development / Opt-In tiers per OTel | n/a (base) | ✓ | ✓ |
| 2 | `anthropic.*` | D3 §1.8 | ✓ | ⚠️ Class 2 F-1 | ✓ | ✓ | ✓ |
| 3 | `mcp.*` | D3 §1.8 | ✓ | ⚠️ Class 2 F-2 | ✓ | ✓ modulo F-9 | ✓ |
| 4 | `skill.*` | D3 §1.8 | ✓ | ⚠️ Class 2 F-3 | ✓ | ✓ | ✓ |
| 5 | `managed_agents.*` | D3 §1.8 | ✓ | ⚠️ Class 2 F-4 | ✓ | ✓ | ✓ |
| 6 | `sandbox.*` | D2 §1.7 + F4 §Consequences (a) | ✓ | ⚠️ Class 2 F-4 + F-5 | ✓ | ✓ | ✓ |
| 7 | `hitl.*` | D5 §1.8 + D5 §1.1 | ✓ | ⚠️ Class 2 F-5 + F-6 | ✓ | ✓ modulo F-5 | ✓ |
| 8 | `topology.fanout.*` | D4 §1.9 | ✓ | ✓ Aligned | ✓ | ✓ | ✓ |
| 9 | `subagent.*` | D4 §1.9 + D4 §1.5 | ✓ | ✓ Aligned | ✓ | ✓ | ✓ |
| 10 | `engine.*` | D1 §1.1 row 1 | ✓ (concept) | ⚠️ Class 2 F-7 (attribute names introduced at D6) | ✓ | ✓ | ✓ |
| 11 | `audit.*` | D5 §1.4 | ✓ (concept) | ⚠️ Class 2 F-8 (attribute names introduced at D6) | ✓ | ✓ | ✓ |
| 12 | `provider_discriminator` | F1 §Decision | ✓ (concept) | ⚠️ Class 2 F-10 (attribute name not declared at F1) | ✓ | ✓ | ✓ |

### §3.2 — Class 2 findings summary

Nine findings F-1 through F-9 (plus F-10 on provider_discriminator) at fine-grain per-attribute alignment dimension. Source D-ADRs/F-ADR engaged: D1, D2, D3, D4, D5, F4. Pattern: D6 §1.2 introduced namespacing conventions (consistent dot-separator format, OTel-aligned prefixing) without back-propagating to source D-ADRs.

| Finding | Namespace | Drift | Severity |
|---|---|---|---|
| F-1 | `anthropic.*` | D3 attributes (`anthropic.thinking_*`, `anthropic.cache_breakpoint_id`, `anthropic.batch_id`, `anthropic.tokenizer_version`, `anthropic.inference_geo`, `anthropic.cache_ttl_seconds`) not in D6; D6 introduces `anthropic.reasoning.output_tokens` not in D3 | Class 2 |
| F-2 | `mcp.*` | D3 underscore-separator (`mcp.server_name`, `mcp.server_trust_tier`) vs D6 dot-separator (`mcp.server.name`, `mcp.server.trust_tier`); D3 has `mcp.protocol_version`/`transport`/`auth_present` not in D6; D6 introduces `mcp.primitive.kind`/`mcp.primitive.signature.sha256` not in D3 | Class 2 |
| F-3 | `skill.*` | D3 (`skill.name`, `skill.version_sha`, `skill.body_tokens`, `skill.activation_mode`) vs D6 (`skill.id`, `skill.frontmatter.name`, `skill.frontmatter.version`); near-total attribute set divergence; `version_sha` (git hash) vs `frontmatter.version` (frontmatter field) is semantic distinction | Class 2 |
| F-4 | `managed_agents.*` | D3 prefixes Managed Agents attributes under `anthropic.managed_agent_*` (within `managed_agents.runtime` span); D6 declares separate `managed_agents.*` namespace | Class 2 |
| F-5 | `sandbox.*` | F4 §Consequences (a) authoritative names `sandbox.tech` / `sandbox.fail.class` vs D2 §1.7 + D6 §1.2 implementation names `sandbox.provider` / `sandbox.violation.class`; F4 `sandbox.policy.assigned_tier_reason` not declared at D2/D6 | Class 2 |
| F-5 (event) | `hitl.*` | D5 declares `hitl.invocation.responded` + `hitl.invocation.timed_out` (different attrs); D6 collapses to single `hitl.invocation.closed` event — information loss | Class 2 |
| F-6 | `hitl.*` | D5 attribute `gate_level_computed` (no prefix) vs D6 `hitl.gate.level` (with prefix); D5 attrs `tool`/`mcp_server`/`persona_tier_active`/`hitl_required` not enumerated at D6 | Class 2 |
| F-7 | `engine.*` | D1 §1.1 row 1 declares engine-class taxonomy + tier residence at concept level; D6 introduces span attribute names (`engine.class`, `engine.event_history.tier`, `engine.event.id`) not declared at D1 | Class 2 |
| F-8 | `audit.*` | D5 §1.4 declares per-persona-tier ledger cryptographic shape at concept level; D6 introduces span attribute names (`audit.signature.sha256`, `audit.signature.prior_hash`, `audit.actor.id`) not declared at D5 (semantically aligned with F2 §(c) ledger entry shape) | Class 2 |
| F-9 | `mcp.*` sampling | D3 §1.8 commits `mcp.tool.call` at head=1.0 with tail-keep-on-trust-tier-floor-violations; D6 §1.3 lists `tool.call` under base-rate sampled — D6 should explicitly distinguish MCP vs non-MCP tool calls | Class 2 |
| F-10 | `provider_discriminator` | D6 §1.2 cites F1 §Decision as source; F1 §Decision discusses cross-family fallback chain composition seam but does not declare `provider_discriminator` as attribute name (anchored at `c7-observability` SKILL.md per D6 framing) | Class 2 |

### §3.3 — Recommended resolution paths

**Resolution path A (preferred — D-layer alignment pass)**: D-ADRs revise attribute names to align with D6 §1.2 canonical naming. Touches 5 D-ADRs (D1 §1.1 row 1, D2 §1.7, D3 §1.8, D4 §1.9, D5 §1.4 + §1.8). Cheaper than F-layer reopen; preserves F4 `Status: Accepted` posture for `sandbox.*` finding via compromise (Resolution path C below for F-5).

**Resolution path B (D6 self-correction)**: D6 §1.2 revises to use source-D-ADR attribute names verbatim. Single ADR touched but loses D6's namespacing-convention coherence; introduces inconsistent separator conventions (`mcp.server_name` vs `topology.fanout.opened`) within D6.

**Resolution path C (F-5 specifically — namespacing reconciliation)**: D6 §1.2 adds explicit *"namespacing-convention reconciliation"* sub-section declaring per-attribute renames + rationale; F4 `sandbox.tech` + `sandbox.fail.class` remain authoritative; D2/D6 emit `sandbox.provider` + `sandbox.violation.class` (canonical at D-layer) AND F4 names as aliases for backwards-compat. Operationally undesirable (cardinality-doubling); avoid unless F-layer revision surface is otherwise unacceptable.

**Recommended composite**: Path A for F-1 through F-4, F-6, F-7, F-8, F-9, F-10 (D-layer alignment pass); Path C for F-5 (`sandbox.*`) only because F4 is `Status: Accepted` post-Step-D ratification and reopening is high-cost. Operator decides at Phase 3c clearance vs P3c-CK clearance.

### §3.4 — Step 4 verification disposition

| Verification dimension | Outcome |
|---|---|
| (a) Source declaration | PASS (12/12) |
| (b) Per-attribute alignment | **FAIL — 9 Class 2 findings** at fine grain |
| (c) Namespace collision discipline | PASS |
| (d) Sampling discipline coherence | PASS modulo F-9 |
| (e) Redaction discipline class | PASS |

**Coarse-grain verification PASSES.** Fine-grain findings forward-routable to P3c-CK or resolvable via in-session D-layer amendment per operator direction.

---

## §4 T-perm engagement and resolution coherence

### §4.1 — T-perm-1 (C4 ↔ C10 — capability vs gating)

**Engagement chain**: F4 §Decision (4-floor `max()` formula) → D5 §1.5.1 (4-axis multiplicative gate-level rule) → D2 §1.5 (5-axis specialization adding `sandbox_tier`) → D3/D4 (inheritance-without-revision) → D6 §1.4 (ledger-reference-only carry-forward as redaction discipline).

**Coherence verification**: ✓ PASS.
- Each layer composes additively without removing or weakening prior axes
- D6 §1.4 per-cell content-capture posture composes in same monotonic-tightening direction as `persona_tier_floor` ascending across bridging-arc
- Sub-agent monotonic-ascension specialization (D2 §1.4 + D4 §1.5 + D5 §1.5.2) preserves monotonicity at all three axes (gate-level, sandbox-tier, persona-tier) at sub-agent boundary; tier downgrade structurally prohibited

**Status**: Promoted to Layer 3 (permanent tension); resolution shape locked at D2 §1.5 (5-axis multiplicative tunable parameter `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier`); D6 ledger-reference-only carry-forward verified non-regressing.

### §4.2 — T-perm-2 (C2 ↔ C3 — within-turn vs across-turn)

**Engagement chain**: F1 §"Permanent tensions engaged" (touched-but-deferred) → F2 §Decision (state-ledger entry shape as across-turn substrate) → F3 §Decision capability-floor (ii) (idempotency-keyed exactly-once via F2 ledger) → F5 §Decision (closure at secrets-in-sandbox seam) → D2/D3/D4/D5 (multiple D-layer seam engagements) → D6 §1.7 (OTLP collector boundary as within-vs-across-turn seam at all 9 cells; ledger-reference-only carry-forward).

**Coherence verification**: ✓ PASS.
- F2-layer resolution composes consistently with D6 §1.7 OTLP collector boundary at all 9 cells (within-turn BatchSpanProcessor → boundary → across-turn durable storage tier)
- F5 closure at secrets-in-sandbox seam is independent of broader T-perm-2 engagement (closure at one F-layer seam does not foreclose D-layer surfaces at prompt-cache pin / OTLP collector / HITL pause-resume)
- Within-turn streaming emission composes with across-turn durable trace storage tier residence per D6 §1.1 trace storage tier per cell

**Status**: Active permanent tension; multi-seam engagement with F5 closure at one F-layer seam; D-layer engagements at D3 §1.5 (prompt-cache pin), D5 §1.11 (HITL pause-resume), D6 §1.7 (OTLP collector boundary); all coherent.

### §4.3 — T-perm-3 (C1 ↔ C9 — control-flow vs reliability)

**Engagement chain**: F1 §"Permanent tensions engaged" (per-layer time-budget shape) → F3 §Decision (closure at durable-execution-engine seam via capability-floor + manifest-declaration default) → D1 §1.3 (`topology_fault_handling ∈ {ABOVE_ENGINE, BELOW_ENGINE, RECONCILER}` per-deployment-surface mapping) → D4 §1.6 (`topology_fault_handling × workload_class × topology_pattern` 3-axis multiplicative specialization) → D2/D3/D5 (adjacency / inheritance) → D6 §1.3 (always-sampled `fallback.triggered`/`breaker.tripped`/`retry.attempt`; ledger-reference-only carry-forward).

**Coherence verification**: ✓ PASS modulo F-5.
- F1-layer per-layer time-budget shape composes with D1-layer `topology_fault_handling` per-deployment-surface mapping coherently
- D1-layer + D4-layer multiplicative tunable composition preserves dimensionality without contradiction
- Reliability event spans surface as span events on the original parent PLUS as new spans under sibling fallback attempt without trace-context regression (D6 §1.2 lifecycle event set + D4 §1.9 multi-agent span hierarchy)
- D6 §1.3 always-sampled discipline matches upstream commitments at all sites (modulo F-5 `hitl.invocation.responded`/`timed_out` collapse)

**Status**: Promoted to Layer 3 (permanent tension); resolution shape locked at F1 + D1 + D4 layer composition (per-layer time-budget × per-surface `topology_fault_handling` × per-workload-class-pattern multiplicative); D6 ledger-reference-only carry-forward verified non-regressing.

### §4.4 — Step 5 disposition

All three permanent tensions engaged coherently across F-layer + D-layer specialization sites; D6 ledger-reference-only carry-forward verified non-regressing for all three. **Workflow v1.2 §2.3.4 exit criterion (c) — SATISFIED.**

---

## §5 Bridging-arc trace continuity verification (OD-3.A — 8 cells)

### §5.1 — Verification cells

Within-column transitions (5):
1. solo × local-development → team × local-development
2. solo × self-hosted-server → team × self-hosted-server
3. solo × managed-cloud → team × managed-cloud
4. team × self-hosted-server → multi-tenant × self-hosted-server
5. team × managed-cloud → multi-tenant × managed-cloud

Diagonal transitions (3):
6. solo × local-development → team × self-hosted-server
7. solo × local-development → team × managed-cloud
8. team × local-development → multi-tenant × self-hosted-server

(multi-tenant × local-development EXCLUDED per D6 §1.1; bridging-arc cannot land at the excluded cell.)

### §5.2 — Per-cell × per-dimension verification

| Dimension | Outcome across all 8 cells |
|---|---|
| (a) Span schema ingestion contract continuity (no namespace dropped) | ✓ PASS — all 12 namespaces preserved across all 8 transitions; collector placement changes (in-process / sidecar / vendor-pipeline / per-tenant routing) preserve namespace ingestion contract at both sides of each transition |
| (b) Sampling discipline class-preserved-or-tightened | ✓ PASS — always-sampled set preserved at every transition; base-rate set tightens monotonically (default 1.0 at solo → 0.05–0.5 at team → tail-based-prod with always-sampled exceptions at multi-tenant); tail-keep-on-classification preserved |
| (c) Redaction discipline class-tightened-not-relaxed | ✓ PASS — solo operator-self-redact → team redaction-processor at OTLP collector boundary → multi-tenant pre-collector eval-grade pipeline (at SDK/wrapper attribute-set time, BEFORE BatchSpanProcessor buffer); strict monotonic tightening across all 8 transitions; no transition relaxes |
| (d) Trace storage tier transitions | ✓ PASS — Tier-3 sqlite ring-buffer → Tier-4 backend-managed OR vendor-bound → Tier-4 partitioned + Tier-5 (per-tenant audit ledger hash-chained + cryptographic signature); monotonic-or-tightened across all 8 transitions |

### §5.3 — Cross-axis emergent property (bridging-arc)

The bridging-arc verification engages **C2 within-turn streaming + C3 across-turn durable storage + C7 span schema + C10 redaction discipline + C11 OTLP collector placement simultaneously** — cross-axis emergent property by definition. **Addressed by ADR conjunction**: D6 §1.1 9-cell matrix + D6 §1.2 unified span schema + D6 §1.4 redaction discipline + D6 §1.7 OTLP collector commitment + D5 §1.5.2 cross-deployment monotonicity + D2 §1.6 cross-deployment sandbox-tier monotonicity + Persona §2 bridging-arc traversal commitment compose without contradiction.

**NOT an Integ-4 fork-class trigger from bridging-arc** — property is cross-axis but addressed; no new ADR required.

---

## §6 Missing ADR dependency check (Integ-3 surfacing)

### §6.1 — Cited ADR dependency completeness

All ADRs cited at Shape 4 across D1–D6 verified present at `/mnt/project/`. **No D-ADR depends on a missing F-ADR or D-ADR.**

### §6.2 — I1 / I2 / I3 status

| ID | Decision | Status |
|---|---|---|
| I1 | Specific LLM-provider routing logic | Formally deferred. F1 §Decision commits layered routing strategy at F-layer; per-class implementation tuning is "D-derivative downstream, not F-layer commitment" per F1 §Rationale (a). No `ADR-I1.md` filed; deferral consistent with Phase 3b §2.3.3 discretion. |
| I2 | Tool granularity (coarse vs fine-grained) | Formally deferred. D3 §1.1 closes Anthropic-primitive enumeration at primitive-set level; per-primitive tool granularity downstream of workload-binding-time. No `ADR-I2.md` filed. |
| I3 | Database-backed vs filesystem+git for durable state | Formally deferred. F2 §Decision commits filesystem+git as canonical state substrate (foundational half); db-augmented composition is deferrable downstream of F-layer. No `ADR-I3.md` filed. |

### §6.3 — Disposition

**No Integ-3 fork triggered.** All ADR dependencies satisfied; I1/I2/I3 formally deferred per Phase 3b discretion; Phase 3c proceeds without backflow to Phase 3a or 3b per Workflow v1.2 §4.2.3.

---

## §7 Cross-axis emergent property surfacing (Integ-4 candidates)

### §7.1 — Candidate assessment summary

| # | Candidate | Engaged voices | Disposition | Trigger? |
|---|---|---|---|---|
| 1 | Replay-determinism semantics across the durable boundary | C1+C3+C7+C11 | Cross-axis specification gap; D1/D6 amendment path preferred (Option A) | **Integ-4 candidate (operator decision required)** |
| 2 | Cross-deployment trace continuity at bridging-arc transitions | C2+C3+C7+C10+C11 | Addressed by ADR conjunction (verified at §5) | NOT trigger |
| 3 | Multiplicative tunable parameter coherence under sub-agent dispatch + sandbox-tier ascension | C1+C4+C10 | Addressed by ADR conjunction (D2 §1.4 + D4 §1.5 + D5 §1.5.2 verified at §4.1) | NOT trigger |
| 4 | Operator-burden eval primitive composition under fallback chain advancement | C6+C7+C8+C9 | Addressed by ADR conjunction (modulo F-10 `provider_discriminator` source citation gap) | NOT trigger |

### §7.2 — Candidate 1: Replay-determinism specification gap

**Property**: When an event-sourced-replay engine (Temporal / DBOS / Restate) replays activities from event history after restart, do spans re-emit, or is replay a deterministic re-read without new span emission? When the engine retries an activity, does the retry emit `retry.attempt` event AND a new sibling span (per D6 §1.2)? How does cost-attribution-per-span (D6 §1.5) avoid double-counting on replay?

**Engaged voices**: C1 (engine boundary topology) + C3 (durable state across replay) + C7 (span schema ingestion) + C11 (OTLP collector boundary placement).

**Addressed by single ADR**: No. F3 §Decision capability-floor (i) "durable replay across restart" anchors concept; D1 §1.1 row 1 declares engine event history at Tier-3 + F2 state-ledger at Tier-5 join via `idempotency_key`; D6 §1.2 `engine.*` namespace ingests D1's per-engine-class trace propagation differential. None of these explicitly commit replay-trace-emission semantics.

**Addressed by ADR conjunction**: Partial. D1 + D6 + F2 ledger entry shape compose to imply replay-deterministic span-emission via idempotency-key dedup at F2 layer — but the explicit replay-emission contract is not stated.

**Disposition options**:
- **Option A (recommended)**: Amendment to D1 §1.1 row 1 OR D6 §1.2 `engine.*` namespace specification declaring explicit replay-emission contract. D-layer amendment, not new ADR.
- **Option B (Integ-4 fork)**: Author new `ADR-I4.md` "Replay-determinism trace-emission contract" within Phase 3c per Workflow v1.2 §4.2.4.
- **Option C (defer)**: Forward-route to P3c-CK adversarial review for severity assessment.

Operator decision required at Phase 3c clearance.

---

## §8 Disposition

### §8.1 — Coarse-grain disposition

| Workflow v1.2 §2.3.4 exit criterion | Status |
|---|---|
| (a) Consistency matrix shows zero unresolved contradictions | **SATISFIED** at coarse grain (55-cell pairwise; 0 Conflict cells; 10 Adjacency = T-perm engagements coherent) |
| (b) Any newly-surfaced ADRs (Integ-4) filed | **CONDITIONAL** — 1 Integ-4 candidate (replay-determinism) surfaced; no in-session ADR authored pending operator disposition |
| (c) Report acknowledges all three permanent tensions and how the chosen ADRs resolve or accept them | **SATISFIED** (T-perm-1, T-perm-2, T-perm-3 engagement chains verified coherent at §4) |

### §8.2 — Fine-grain findings

- **9 Class 2 findings (F-1 through F-9)** at per-attribute alignment dimension across `anthropic.*`, `mcp.*`, `skill.*`, `managed_agents.*`, `sandbox.*`, `hitl.*`, `engine.*`, `audit.*`, `provider_discriminator` namespaces. Pattern: D6 §1.2 introduced namespacing conventions without back-propagating to source D-ADRs.
- **1 Integ-4 candidate** (replay-determinism specification gap) requiring operator disposition.
- **0 Conflict** cells; **0 Integ-1/2/3 forks**; **0 fresh voice disagreements** (TENSION block omitted per skill discipline).

### §8.3 — Composite disposition: CONDITIONAL CLEARANCE

Phase 3c verification SATISFIES Workflow v1.2 §2.3.4 exit criteria (a), (b), (c) at coarse grain. Fine-grain findings are forward-routable to P3c-CK adversarial review or resolvable in-session via D-layer amendment passes per operator direction.

**Recommended path**: Forward-route findings to P3c-CK with explicit finding-list disclosure (consistent with OD-2.A original framing). Operator may alternatively direct in-session D-layer amendment passes for Class 2 findings F-1 through F-9 + Option A amendment for Integ-4 candidate 1, OR escalate Integ-4 candidate 1 to Option B (in-session new ADR).

### §8.4 — Meta-finding (systemic pattern)

The systemic per-attribute name drift across 7+ namespaces and 5+ source D-ADRs constitutes a **session-prompt-template gap at Phase 3b** — D-ADR session prompts should have included a forward-reference clause requiring span attribute names declared in the D-ADR to match the namespacing convention D6 will adopt; OR D6 §1.2 should have explicitly logged the namespacing-convention rename per attribute. This meta-finding is appropriate for **Workflow §7 session-prompt-template revision recommendation** for future projects following this pattern; not action-blocking for current Phase 3c clearance.

---

## §9 Routing forward

Under recommended **CONDITIONAL CLEARANCE** disposition:

- **Phase 3c CLOSE** with finding-list (9 Class 2 findings F-1 through F-9 + 1 Integ-4 candidate replay-determinism) on the open ledger.
- **Route to P3c-CK (NEW Workflow v1.2)** per §0 Visual Summary; harness adversarial reviewer skill executes adversarial review of D-ADRs (D1–D6) with finding-list as input; clearance gates Phase 3d entry; D-ADR `Status: Proposed → Accepted` promotion per Workflow v1.2 §3.1 conditional on P3c-CK clearance.
- P3c-CK clearance options for finding-list:
  - Pre-clearance fix path: D-ADR revision pass aligning attribute names per Resolution path A (preferred — see §3.3) before P3c-CK clearance.
  - Conditional clearance path: P3c-CK clears with finding-list deferral to Phase 3d ADD consolidation; rename rationale consolidated at consolidation-time rather than D-ADR-level.

Under operator override to in-session D-layer amendment pass:

- Phase 3c HOLDS open pending D-layer amendment passes for findings F-1 through F-9.
- Integ-4 candidate 1: Option A (D-layer amendment) OR Option B (in-session new `ADR-I4.md`) per operator direction.
- Phase 3c re-runs consistency verification post-amendment per Workflow v1.2 §4.2 fork-class resolution path.

Under operator override to Integ-4 escalation:

- Phase 3c authors `ADR-I4.md` "Replay-determinism trace-emission contract" within session per Workflow v1.2 §4.2.4.
- Consistency matrix re-runs after `ADR-I4.md` filing; Phase 3c clearance contingent on re-run clearance.

---

## §10 References

### §10.1 — ADRs (11)

- `ADR-F1.md` v1.2 (Status: Proposed) — multi-LLM provider abstraction; layered cheapest-deterministic-first routing
- `ADR-F2.md` v1.2 (Status: Proposed) — filesystem + git as canonical state substrate
- `ADR-F3.md` v1.1 (Status: Accepted) — stateless-reducer / launch-pause-resume durable-execution pattern; capability-requirement floor (i)–(iv)
- `ADR-F4.md` v1.1 (Status: Accepted) — four-tier sandbox-isolation; per-tool tier `max(...)` formula
- `ADR-F5.md` v1.1 (Status: Proposed) — capability-aware secret-fetch abstraction; tier-aware resolution
- `ADR-D1.md` v1 (Status: Proposed; filed 2026-05-10) — engine-class taxonomy; per-deployment-surface candidate mapping; D1-layer T-perm-3 resolution
- `ADR-D2.md` v1 (Status: Proposed; filed 2026-05-10) — deployment-surface × blast-radius-tier sandbox matrix; T-perm-1 D2-layer 5-axis multiplicative tunable
- `ADR-D3.md` v1 (Status: Proposed; filed 2026-05-10) — closed Anthropic-primitive enumeration; per-primitive × workload-class adoption-depth matrix
- `ADR-D4.md` v1 (Status: Proposed; filed 2026-05-10) — six-pattern topology taxonomy; T-perm-3 D4-layer 3-axis multiplicative specialization
- `ADR-D5.md` v1 (Status: Proposed; filed 2026-05-10) — four-response palette; synchrony-class × HITL-primitive matrix; T-perm-1 D5-layer 4-axis multiplicative gate-level rule
- `ADR-D6.md` v1 (Status: Proposed; filed 2026-05-10) — deployment-surface × persona-tier 9-cell matrix; unified span schema ingestion contract; bridging-arc trace continuity discipline anchor

### §10.2 — Permanent-tension ledger entries

- T-perm-1 (C4 ↔ C10 — capability vs gating): F4-layer + D5-layer + D2-layer multiplicative tunable parameter `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier`; D6 §1.4 ledger-reference-only carry-forward verified non-regressing
- T-perm-2 (C2 ↔ C3 — within-turn vs across-turn): F2-layer state-ledger substrate + F5 closure at secrets-in-sandbox seam + D3 §1.5 prompt-cache pin + D5 §1.11 HITL pause-resume revalidation + D6 §1.7 OTLP collector boundary at all 9 cells; ledger-reference-only carry-forward at D6 verified non-regressing
- T-perm-3 (C1 ↔ C9 — control-flow vs reliability): F1-layer per-layer time-budget shape + F3 closure at durable-execution-engine seam + D1 §1.3 `topology_fault_handling` per-surface mapping + D4 §1.6 multiplicative 3-axis tunable specialization; D6 §1.3 always-sampled discipline ledger-reference-only carry-forward verified non-regressing modulo F-5

### §10.3 — Persona document trace points

- Persona §2 (bridging-arc traversal commitment) — anchored at §5 bridging-arc verification + D6 §Consequences (f)
- Persona §3.2 (workload-class extensibility flag) — anchored at D3 §1.2 + D4 §1.2
- Persona §4 (99.9%+ completion SLO at tens-concurrent scale) — anchored at D5 §1.9 operator-burden eval primitive calibration
- Persona §6 (per-class cost ceiling) — anchored at D6 §1.5 cost-attribution-per-span + alerting threshold
- Persona §9 (local-development design-time deployment target) — anchored at D6 §1.1 solo × local-development cell identification
- Persona §10.2 (production-time deployment surface persona-constrained-but-not-picked) — anchored at D6 §1.1 9-cell matrix
- Persona §10.4 (compliance-readiness foundational primitives) — anchored at D5 §1.4 per-persona-tier ledger cryptographic shape + D6 §1.4 redaction discipline + D6 §1.8 multi-tenant tenant-isolation + D6 §1.1 multi-tenant × local-development EXCLUDED

### §10.4 — Workflow citations

- `Project_Workflow_v1_2.md` §2.3.4 (Phase 3c discipline; exit criteria)
- `Project_Workflow_v1_2.md` §4.2 (fork classes Integ-1 / Integ-2 / Integ-3 / Integ-4; resolution paths)
- `Project_Workflow_v1_2.md` §3.1 (D-ADR promotion path; conditional on P3c-CK clearance)
- `Project_Workflow_v1_2.md` §4.1 (finding severity classification — Class 0 / 1 / 2 / 3)
- `Project_Workflow_v1_2.md` §6.2 (phase × execution-agent matrix; council-orchestrator at Phase 3c; harness adversarial reviewer at P3c-CK)
- `Project_Workflow_Revision_log.md` (v1.1 → v1.2 elevation; P3c-CK / P3d-CK / P4-CK additions)

### §10.5 — Cluster substrate citations

- Cluster 5 V2 §3 D1 / D2 / D3 / D4 / D5 / D6 (deployment-surface + persona-tier classification per D-decision)
- Pattern Reference Catalog v1.0 §11.3.1 (per-foundational-decision candidate enumeration)
- Pattern Reference Catalog v1.0 §11.3.2 (per-derivative-decision candidate enumeration; D1 lines 3110–3118; D2 lines 3119–3127; D3 lines 3129–3137; D4 lines 3139–3148; D5 lines 3150–3160; D6 lines 3161–3168; I1–I3 lines 3172–3196)

### §10.6 — Convening artifacts (Phase 3c)

- Global Convening Block + CCR (Segment 1; full eleven-voice slate convening per Workflow v1.2 §2.3.4 mandatory)
- Per-question convening annotations across 55-cell consistency matrix (Segment 2) + 12-namespace span schema verification (Segment 3) + 3-T-perm engagement (Segment 4) + 8-cell bridging-arc verification (Segment 4)
- TENSION block: OMITTED per skill output template discipline (no fresh voice disagreements; known T-perms labeled-permanent in §4)

---

*Filed 2026-05-10 at Phase 3c close. Routing: P3c-CK (NEW Workflow v1.2) per §0 Visual Summary on operator confirmation of clearance disposition. Recommended next session: P3c-CK adversarial review of D-ADRs (D1–D6) with this finding-list as input, executed by the harness adversarial reviewer skill per Workflow v1.2 §6.2 phase × execution-agent matrix.*