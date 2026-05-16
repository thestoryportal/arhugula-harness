# ADR-D2: Specific sandbox provider — per-deployment-surface × per-blast-radius-tier sandbox commitment with sub-agent monotonic-ascension and persona-tier compliance composition

## Status

Accepted
Date: 2026-05-10
Phase: 3b Stage 1 (per `Project_Workflow_v1_1.md` §2.3.3)
Promotion path: Accepted at P3-CK clearance per Workflow v1.1 §3.1
Revision: v1 → v1.1 (P3c-CK iter-1 close mechanical revision per Path A — F2-05 sandbox sub-finding resolution at §1.7 + §1.7.1 + §1.8 honoring F4 §Consequences (a) authoritative `sandbox.tech` / `sandbox.fail.class` / `sandbox.policy.assigned_tier_reason` names with declare-both-with-join semantic for `sandbox.tech` (technology class) ↔ `sandbox.provider` (vendor+tech instance); F1-01 §1.4 function signature parameter naming consistency; F1-02 §1.6 cross-deployment monotonicity prose disambiguation)
Revision date: 2026-05-10
Promotion: P3c-CK final clearance — 2026-05-11
Revision: v1.1 → v1.2 (Phase 7 C-AS-02 `sandbox_tier_floor` signature reconciliation — operator-authorized 2026-05-15 — reconciling the §1.4 3-arg form and the §1.5.1 4-arg form to the canonical 5-arg signature `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier | REFUSE`)
Revision date: 2026-05-15

## Change-note (v1.1 → v1.2)

**Trigger.** Phase 7 C-AS-02 `sandbox_tier_floor` contract self-contradiction surfaced by the AS-plan verbatim audit (`verbatim_audit_as_plan.md` F3-01 / Pattern A2) and re-stated by the R3 implementation-planner pass. The `systems-architect` S1 reconciliation recommendation (`.harness/s1_c_as_02_reconciliation.md`, authored 2026-05-15) was operator-ratified 2026-05-15; this revision applies it. The S1 pass found the contradiction **originates at ADR-D2 itself** — §1.4 renders `sandbox_tier_floor` as a 3-arg form, §1.5.1 as a 4-arg form, and §1.5.1's `where:` block keys rows on `(remote MCP, level N)` while the §1.5.1 signature carries only `mcp_transport` (no trust-level input). The ADR-D2 edit is therefore part of the same reconciliation, not a downstream spec-only fix; it is operator-authorized because it touches a D-ADR.

**Scope of revision.** Reconcile the ADR-D2 §1.4 and §1.5.1 `sandbox_tier_floor` renderings to one canonical 5-argument signature: `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier | REFUSE`. The `tool` argument is retained (rows 1–2 of the §1.5.1 `where:` block — computer-use-bound / LLM-generated-code-execution — are tool-keyed; a 3-arg form cannot evaluate its own lookup table). The trust-level input rows 4–6 require is threaded as the explicit `mcp_server` argument (G-1, explicit-argument resolution — not carrier-borne; parity with the four sibling `max()` floors, all explicit-arg, and with the `assigned_tier_reason` audit surface). No `where:`-block rows are changed; the row→argument keying is made explicit.

**Changes inline.** Status block (second Revision / Revision date line pair added for v1.1 → v1.2). This Change-note section. §1.3 closing prose line — `sandbox_tier_floor` input enumeration aligned to the 5-arg shape. §1.4 `sub_agent_sandbox_tier` body — the inner `sandbox_tier_floor(blast_radius, deployment_surface, mcp_transport)` call reconciled to the canonical 5-arg form `sandbox_tier_floor(tool, deployment_surface, blast_radius, mcp_transport, mcp_server)`; the `sub_agent_sandbox_tier` outer signature gains `tool` and `mcp_server` parameters so it has them to thread through (the sub-agent's own tool + call-site MCP server must reach rows 1–2 and 4–6 of the floor table). §1.5.1 `gate_level` body — the `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport)` call gains the `mcp_server` argument; `gate_level`'s outer signature already carries `mcp_server`. §1.5.1 `where:` block — rows preserved verbatim; a row→argument keying note added beneath the block (rows 1–2 tool-keyed; row 3 `mcp_transport`-keyed; rows 4–6 `mcp_server`-trust-level-keyed; remaining rows `blast_radius_tier`-keyed). §Consequences (b) — the "five inputs (tool, deployment_surface, blast_radius_tier, mcp_transport, plus implicit computer-use / LLM-generated-code binding ...)" enumeration corrected: the inputs are the five explicit arguments; computer-use / code-execution binding is a property of the explicit `tool` argument, not an implicit input. Permanent tension ledger entry (T-perm-1) — the verbatim `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport)` restatement aligned to the 5-arg form.

**Sections preserved verbatim.** §1.1 deployment-surface × blast-radius-tier matrix; §1.2 sandbox provider-class enumeration; §1.3 per-MCP-transport floor table (only the closing input-enumeration prose line amended); §1.4 unconditional-rule + rationale prose (only the function signature/body amended); §1.5 tunable specialization prose; §1.5.1 `where:` block rows (all 10 rows verbatim; a keying note appended); §1.5.2; §1.6; §1.7 + §1.7.1 + §1.8 + §1.9 + §1.10; Rationale (all sub-sections except §Consequences (b) is a Consequences edit; Rationale untouched); Consequences (all sub-sections except (b)'s input enumeration); Alternatives considered; References (all shapes except the T-perm-1 permanent tension ledger entry's signature restatement).

**Surfaced findings (not patched).** None — the §1.3 / §Consequences (b) / T-perm-1 ledger sites are mechanical restatements of the same signature and are reconciled here as intra-file back-references (spec-writer SKILL §5), not left stale.

**Downstream absorption owed.** Workspace root `CLAUDE.md` §2.2 ADR-version table lists `ADR-D2 v1.1` — a follow-up token bump to `v1.2` is owed (not applied here; `CLAUDE.md` is out of spec-writer remit). AS plan units U-AS-06 (`sandbox_tier_floor` carrier) and U-AS-09 (`sub_agent_sandbox_tier` carrier) require an `implementation-planner` R3.1 micro-pass to finalize against the reconciled 5-arg signature.

---

## Change-note (v1 → v1.1)

**Scope of revision.** Three-finding mechanical-alignment revision pass clearing `Adversarial_Review_3c.md` F2-05 sandbox sub-finding (Pattern P1 attribute name drift — D2 §1.7 declares `sandbox.provider` discriminator without surfacing F4 §Consequences (a) authoritative names `sandbox.tech` / `sandbox.fail.class`; F4 commitment `sandbox.policy.assigned_tier_reason` not declared at D2/D6), F1-01 (Class 1 — D2 §1.4 function signature `sub_agent_sandbox_tier(parent_tier, ...)` vs body `max(parent_sandbox_tier, ...)` parameter naming inconsistency), F1-02 (Class 1 — D2 §1.6 cross-deployment monotonicity prose semantic inversion: "cannot downgrade to Tier 2 ... if Tier 3 is the floor" reads as same-tier downgrade rather than failure-to-ascend). The F2-05 hitl.* event-collapse sub-finding is D6's revision territory, not D2's.

**F2-05 sandbox sub-finding resolution: declare-both-with-join semantic per operator selection at session open.** D2 §1.7 span schema rewritten to declare BOTH `sandbox.tech` (F4 canonical; technology class — five values: `microvm`, `container`, `vm`, `language-level`, `fs-overlay`) AND `sandbox.provider` (D2 introduced; vendor+tech instance — 17 values preserved verbatim) as distinct attributes with documented `provider belongs-to tech` join. New §1.7.1 sub-section declares the seven `sandbox.*` span attribute names (`sandbox.tier`, `sandbox.tech`, `sandbox.provider`, `sandbox.fail.class`, `sandbox.policy.assigned_tier_reason`, `sandbox.cost.tier_overhead_ms`, `sandbox.cost.tier_overhead_usd`) with explicit mapping to F4 §Consequences (a) authoritative naming. §1.8 sandbox-violation fail-class taxonomy column header renamed `violation_class` → `sandbox.fail.class` honoring F4 canonical. ADR-D6 §1.2 row `sandbox.*` reads from D2 v1.1 declarations after this revision; the per-attribute set at D6 §1.2 is updated to match (D6 v1.1 absorbs the join semantic).

**Status posture.** `Status: Proposed` preserved per `Project_Workflow_v1_2.md` §3.1 — promotion to `Accepted` blocked until P3c-CK clearance. D2 v1.1 enters P3c-CK iteration 2 as input artifact alongside D1 v1.1, D5 v1.2, and the other revised D-ADRs (D3 v1.1, D4 v1.1, D6 v1.1).

**Sections preserved verbatim.** §1.1 deployment-surface × blast-radius-tier matrix; §1.2 sandbox provider-class enumeration; §1.3 per-MCP-transport sandbox-tier floor; §1.4 sub-agent sandbox-tier monotonic-ascension table prose (only the function signature/body parameter naming amended per F1-01); §1.5 T-perm-1 D2-layer multiplicative tunable parameter specialization (incl. §1.5.1 + §1.5.2); §1.6 cross-deployment sandbox-tier monotonicity (only the bullet-1 prose reworded per F1-02); §1.7 sandbox-boundary span schema code block (F4-canonical attribute names applied per F2-05; the schema *shape* preserved — same parent-child structure, same event names, same sampling discipline); §1.8 sandbox-violation fail-class taxonomy table (column header renamed `violation_class` → `sandbox.fail.class` per F2-05; all rows preserved verbatim); §1.9 sandbox-pool warm-up protocol; §1.10 workload-binding-time × deployment-surface-time selection contract; Rationale (all sub-sections); Consequences (all sub-sections); Alternatives considered; References Substrate dependency declaration + Pattern Reference Catalog citations + Per-axis recommendation citation + Parent F-ADR/D-ADR citations + Persona document trace + Substrate research citations + Primary-source citations + Permanent tension ledger updates + Convening artifact citations.

**Changes inline.** Status block (Revision / Revision date lines added). This Change-note section. §1.4 function signature parameter renamed `parent_tier` → `parent_sandbox_tier` per F1-01 reviewer recommendation (semantic unambiguous; rename body's parameter to match signature would also work, but `parent_sandbox_tier` is more specific and aligns with the body's existing `max()` first argument). §1.6 bullet-1 prose reworded to disambiguate semantic without changing rule (replace "cannot downgrade to Tier 2" with explicit "must ascend to Tier 3" framing). §1.7 span schema attribute names reconciled with F4 canonical: `sandbox_tier` → `sandbox.tier`, `sandbox_provider` → split into both `sandbox.tech` (new, F4 canonical) AND `sandbox.provider` (existing, retained per declare-both-with-join), `violation_class` → `sandbox.fail.class`, plus added `sandbox.policy.assigned_tier_reason` per F4 §Consequences (a) line 57 commitment. §1.7 prose paragraph extended to document the tech/provider join contract. New §1.7.1 sub-section declares the `sandbox.*` attribute namespace at D2 source. §1.8 column header rename `violation_class` → `sandbox.fail.class`. References "Workflow and skill discipline references" extended with new entries (Workflow v1.2 §3.1, Workflow v1.2 §4.1.2, spec-writer skill, Adversarial_Review_3c.md F2-05/F1-01/F1-02, Phase 3c-CK iteration 1 close handoff §4.1). Closing footer revised to note v1.1 filing.

**F2-05 Option B (declare-both-with-join) rationale.** D2 §1.7's 17-value `sandbox.provider` enumeration reads as **provider+technology tuples** (e.g., `e2b_firecracker` = e2b *provider* + firecracker *tech*; `modal_gvisor` = modal *provider* + gvisor *tech*; `bedrock_agentcore` = AWS Bedrock + AgentCore Runtime), not pure technology classes. F4 §Consequences (a) calls `sandbox.tech` a "discriminator attribute (swap-friendly without schema migration)" with role-phrasing matching D2's `sandbox.provider`, but F4's tier-mechanism framing reads as the abstraction class above the provider+tech tuple level. Option A (RENAME) would flatten the 17-value enumeration onto F4's `sandbox.tech` name and lose the abstraction split. Option B (DECLARE-BOTH-WITH-JOIN) preserves the dashboard query surface — "all microVM-tier failures across vendors" → `sandbox.tech=microvm` regardless of `sandbox.provider`, while "Bedrock AgentCore-specific failures" → `sandbox.provider=bedrock_agentcore`. The cardinality-doubling concern Phase 3c §3.3 flagged for Path C (alias scheme) does NOT apply to Option B because Option B adds a low-cardinality (~5) parent attribute alongside the existing 17-value child, not aliasing the cross-product. Reviewer at F2-05 Resolution Path acknowledges Option B as the alternative when "tech as tier-mechanism class; provider as specific-instance" semantic holds — the substrate analysis above confirms it does.

**Deferred — F2-05 hitl.* sub-finding NOT addressed in this revision.** `Adversarial_Review_3c.md` F2-05 has two sub-findings; the sandbox sub-finding is D2's territory (resolved here), the hitl.* event-collapse sub-finding is D6's territory (D6 v1.1 absorbs the resolution per Phase 3c-CK iteration 1 close handoff §4.1 D6 row). D2 v1.1 leaves D6's hitl.* event collapse untouched.

## Context

This ADR closes the deployment-surface-dependent specific-sandbox-provider deferral declared at `Pattern Reference Catalog v1.0 §11.3.2 D2` (lines 3119–3127 — "specific sandbox provider — *deployment-surface-dependent*; derived from F4") and at `Cluster 5 V2 §3 D2` (deployment-surface-dependent classification). `ADR-F4.md` v1.1 (Status: Accepted, 2026-05-09; Adv-2 revision pass per Path 4 session) committed the harness to the **graduated-isolation principle** (sandbox-strength-by-trust-level) with a **four-tier sandbox-isolation tier-set** (process / container / microVM / full-VM) and **per-tool tier assignment computed as `max(contract.minimum_tier, blast_radius_floor, mcp_server_trust_tier_floor, operator_policy_floor)` per call site**; F4 v1.1 §Decision committed process-tier tech (Seatbelt on macOS; bubblewrap+socat on Linux/WSL; language-level + filesystem-ACL on Windows-native; kilocode-style git-worktree-isolation per ADR-F2 as a cross-platform filesystem-bound process-tier composable) and the container-tier abstraction (Docker-on-OCI as the design-time default, with specific container-runtime + image-policy deferred); F4 v1.1 §Decision **deferred microVM-tier and full-VM-tier tech selection to per-deployment-surface D2 D-ADRs constrained to candidates meeting the per-tier capability requirements stated in F4**. D2 specializes F4 by traversing the substrate candidate space competitively per Pattern Reference Catalog v1.0 §11.3.2 D2 enumeration and committing per-deployment-surface × per-blast-radius-tier sandbox provider + sandbox tier + persona-tier compliance composition + sub-agent monotonic-ascension enforcement, with workload-binding-time × deployment-surface-time selection contract for specific candidate selection.

`ADR-D1.md` v1 (Status: Proposed, 2026-05-10) committed a five-element engine-class taxonomy (event-sourced-replay / save-point-checkpoint / pure-pattern-no-engine / reconciler-loop / WAL-segment) with per-deployment-surface candidate mapping; D1 §1.2 enumerated per-surface candidate sets (local-development / self-hosted-server / managed-cloud) D2 inherits as the surface-row enumeration. `ADR-D5.md` v1 (Status: Proposed, 2026-05-10) committed the four-component HITL synchrony specification including §1.5 T-perm-1 D5-layer multiplicative gate-level composition rule with `persona_tier × blast_radius_tier` axes added to the locked tunable; D2 specializes the D5-layer T-perm-1 resolution by adding the `sandbox_tier` axis without modifying the existing four-axis tunable. `ADR-D4.md` v1 (Status: Proposed, 2026-05-10) committed the six-pattern multi-agent topology specification including §1.5 sub-agent privilege inheritance contract (default-downgrade rule per blast-radius tier; sub-agent monotonic gate-level ascension); D2 inherits sub-agent privilege inheritance and **extends sub-agent monotonic-ascension to sandbox tier as an unconditional containment rule** (override-clause at D4 §1.5 does NOT extend to sandbox tier). `ADR-D3.md` v1 (Status: Proposed, 2026-05-10) committed per-cell Skills-as-code-execution-surface adoption depth; D2 composes against D3 §1.2 per-cell adoption-depth at the Skills-as-code-execution containment site.

The deliberation surface at D2 is the per-cell sandbox provider + sandbox tier mapping across the deployment-surface × blast-radius-tier matrix, not a single-provider pick. Cluster 3 §2.2 [HIGH] documents the per-mechanism tradeoff table — language-level (escape risk high if no language sandbox); container + seccomp (shared kernel; escape risk medium — kernel CVE class); gVisor (user-space kernel; escape risk low; ~10–30% I/O overhead); Firecracker microVM (hardware-virt; escape risk very low; ~150ms cold start); full VM (escape risk very low; seconds cold start). Cluster 3 §3.4(d) [MODERATE — promoted from SPECULATIVE per F4 §Rationale (a) triangulation] documents the isolation-by-tool-surface ordering: pure data-read (no sandbox); data-write-bounded (typed + RBAC); code-execution (microVM mandatory); computer-use (full VM, ephemeral, network-egress-restricted). Cluster 4 §2.3.2 [HIGH] documents Willison's lethal-trifecta architectural constraint — any execution path reaching `private-data + untrusted-content + exfil-capability` is structurally vulnerable; filter-based mitigations top out near 97% (Anthropic transparency hub: Sonnet 4.5 + detection prevented 94% MCP / 82.6% computer-use / 99.4% bash); architectural cut-of-leg via tier composition is the only reliable mitigation. Cluster 4 §2.3.3 [HIGH] documents the four-level MCP server trust posture (Level 0 refuse-remote / Level 1 signed-pinned / Level 2 sandbox-all / Level 3 allow-with-audit) and the MCP authorization spec 2025-06-18 [HIGH] OAuth 2.1 Resource Servers + RFC 8707 + RFC 9728 + PKCE mandatory but **explicitly excluding STDIO transports** ("retrieve credentials from environment") — STDIO MCP servers carry zero protocol-level auth and sandbox is the only boundary. Cluster 4 §2.3.5 [HIGH] catalogs in-the-field failures sharing the under-tiering pattern (CVE-2025-53773 GitHub Copilot RCE; CVE-2025-54132 Cursor IDE Mermaid exfil; Anthropic Cowork file-API exfil; Oasis Security Claude.ai URL-param injection).

`Persona_Document_v1` §3 records workload-class enumeration as first-class (§3.1.1 software-engineering; §3.1.2 content-creation; §3.1.3 pipeline-automation; §3.1.4 research); §4 sets the 99.9%+ completion SLO at tens-concurrent scale; §5 names code execution + computer-use at design-time AND production-time as in-scope action surface with stronger sandbox tier at production-time per operator phrasing; §5.1 explicitly records "[HIGH] computer-use-at-production-with-stronger-sandbox-tier"; §6 records per-class cost ceiling; §9 [HIGH] records local-development as design-time deployment target and microVM-class isolation availability required at production-time; §10.2 explicitly records production-time deployment surface as **persona-constrained-but-not-picked** ("Cloud-managed, hybrid, and on-prem-with-sufficient-infrastructure remain live options pending Phase 3 deliberation"); §10.4 records compliance-readiness foundational primitives ("hash-chained audit ledger, granular access controls, encryption-at-rest, retention controls, tenant isolation, secrets rotation, comprehensive observability — need to be foundational, not bolt-on") as architectural posture; §10.5 records routing-strategy as persona-open D-derivative; §11.10 records tenant-isolation specifics at multi-tenant binding (data, cost, model access, per-tenant sandbox) as open item bound when multi-tenant deployment design begins.

Three permanent tensions interact with D2. **T-perm-1 (C4 ↔ C10 — capability vs gating)** is the **direct engagement at D2** — sandbox tier IS the canonical containment side of the action-surface T-perm-1 axis at the per-tool-trust-tier seam. D5 was T-perm-1's first direct D-layer engagement; D2 is the second. **T-perm-3 (C1 ↔ C9 — control-flow vs reliability)** D1-layer `topology_fault_handling` per-deployment-surface mapping + D4-layer `topology_fault_handling × workload_class × topology_pattern` resolutions stand; D2 surfaces adjacency at sandbox cold-start latency engaging cascade-policy timeout composition (Firecracker ~150ms cold start vs full-VM seconds per Cluster 3 §2.2 [HIGH]) without revising D1 or D4. **T-perm-2 (C2 ↔ C3 — within-vs-across-turn)** F2-layer resolution stands per F3 v1.1 §References explicit framing; D2 surfaces adjacency at computer-use within sandbox crossing within-turn screenshot context (C2 stake) and across-turn sandbox state durability (C3 stake) without revising F2.

ADR-F1 (Status: Proposed) composes against D2 at the cross-family fallback chain composition seam — F1's per-layer time-budget shape preserves model-call continuity but does NOT preserve the Anthropic-primitive surface; D2's sandbox-tier commitment is harness-owned and survives cross-family fallback. ADR-F2 (Status: Proposed) composes against D2 at the worktree-isolation seam — F2's combined git tier including kilocode-style worktree-isolation is one process-tier composable D2 inherits as a sandbox provider candidate. ADR-F3 v1.1 (Status: Accepted post Step D) composes against D2 at the capability-floor (iv) observable lifecycle seam — D2's sandbox-boundary span schema extends the F3 lifecycle event set with `sandbox.enter` / `sandbox.exit` / `sandbox.violation` / `sandbox.tier_escalation` events forward-referenced to D6 ingestion.

## Decision

Commit at the D2 layer to a **six-component specific-sandbox-provider specification**:

1. **12-cell deployment-surface × blast-radius-tier matrix** committing per-cell sandbox provider-class + sandbox tier + persona-tier compliance composition (§1.1).
2. **Sandbox provider-class enumeration** at deployment-surface granularity per Pattern Reference Catalog v1.0 §11.3.2 D2 candidate set (§1.2).
3. **Per-MCP-transport sandbox-tier floor** committing Tier 3 minimum for STDIO MCP transports regardless of declared blast-radius (§1.3).
4. **Sub-agent sandbox-tier monotonic-ascension** as unconditional containment rule extending D4 §1.5 sub-agent privilege inheritance contract (§1.4).
5. **T-perm-1 D2-layer multiplicative tunable parameter specialization** adding `sandbox_tier` axis to the locked tunable; locked tunable becomes `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier` (§1.5).
6. **Cross-deployment sandbox-tier monotonicity** extending D5 §1.5.2 — `sandbox_tier_floor` monotonic ascending under bridging-arc traversal (§1.6).

Sandbox provider-class is committed at D2 per cell; specific candidate-within-class is deferred to deployment-surface-time × workload-binding-time downstream of Phase 3 per §1.10 contract.

### 1.1 Deployment-surface × blast-radius-tier matrix

The 2D matrix below commits per-cell sandbox provider-class + sandbox tier + persona-tier compliance composition. Cell entries follow the schema `sandbox tier (F4 graduated-isolation) | provider-class (Cluster 3 §2.2 + §11.3.2 D2) | candidate witnesses`.

| deployment-surface ↓ \ blast-radius-tier → | read-only | local-mutation | external-reversible | external-irreversible |
|---|---|---|---|---|
| **local-development** (design-time target per Persona §9 [HIGH]) | **Tier 1 minimal isolation** \| language-level + filesystem-ACL \| in-process direct execution; F4 v1.1 process-tier substrate; bytedance/deer-flow LocalSandboxProvider for read-only ops | **Tier 2 process isolation** \| Seatbelt (macOS) / bubblewrap+socat (Linux/WSL) / kilocode-style worktree (cross-platform filesystem-bound) per F4 v1.1 + ADR-F2 \| Kilo-Org/kilocode git-worktree; can1357/oh-my-pi worktree / fuse-overlay / fuse-projfs platform-tagged | **Tier 3 container isolation** \| Docker-on-OCI per F4 v1.1 design-time default; gVisor (user-space kernel; escape risk low; ~10–30% I/O overhead) acceptable for trusted workloads per Cluster 3 §2.2 [HIGH] \| OpenHands/OpenHands Docker reference; langgenius/dify dify-sandbox; shareAI-lab/Kode-Agent OpenSandbox | **Tier 4 VM isolation** \| Firecracker microVM (E2B class; ~150ms cold start; <5MiB overhead per Cluster 3 §3.4 [HIGH]); E2B self-host on KVM hosts as design-time default per Cluster 3 §2.2 [HIGH]; gVisor-class fallback per C9 refinement at solo-developer × short-session under operator_policy_floor with audit ledger entry; full VM for computer-use cells (ephemeral; network-egress-restricted) per Persona §5 \| disler/agent-sandboxes E2B; bytedance/deer-flow AioSandboxProvider; langchain-ai/deepagents Modal (gVisor) / Daytona / Deno backends |
| **self-hosted-server** | **Tier 1 minimal isolation** \| language-level + filesystem-ACL \| same as local-development | **Tier 2 process isolation** \| bubblewrap+socat (Linux); container-tier upgrade acceptable at this surface per F4 v1.1 §Decision; kilocode-style worktree where filesystem-bound \| same candidates as local-development; Docker-on-OCI available as Tier 3 substitute under operator_policy_floor | **Tier 3 container isolation** \| Docker-on-OCI default; Kata Containers (microVM-backed; ~150ms cold start); gVisor; humanlayer/agentcontrolplane K8s-resident container per ADR-D1 §1.2 \| OpenHands Docker reference; humanlayer/agentcontrolplane K8s-native; shareAI-lab/Kode-Agent OpenSandbox | **Tier 4 VM isolation** \| Firecracker microVM (E2B self-host); Modal gVisor (managed-sandbox-as-a-service if operator permits cross-deployment trust per F5); langchain-ai/deepagents CompositeBackend (Modal / Daytona / Deno); Kata Containers as microVM-backed container; full VM for computer-use \| disler/agent-sandboxes E2B self-host; langchain-ai/deepagents Modal/Daytona/Deno; Kode-Agent + WAL-segment substrate per ADR-D1 §1.1 row 5 |
| **managed-cloud** | **Tier 1 minimal isolation** \| language-level (vendor-managed runtime; vendor-side filesystem-ACL) \| AWS Lambda / Cloud Run / Cloud Functions class equivalent at vendor runtime | **Tier 2 process isolation** \| vendor-managed process-tier (gVisor at Cloud Run; Firecracker-as-Lambda-substrate; vendor-managed equivalents at Bedrock AgentCore Runtime) per ADR-D1 §1.2 managed-cloud row \| AWS Bedrock AgentCore Runtime sandbox primitive; Google Vertex Agent Engine; Cloudflare Workers Durable Objects | **Tier 3 container isolation** \| AWS Bedrock AgentCore Runtime (vendor-managed sandbox); Google Vertex Agent Engine; vendor-managed container substrate per ADR-D1 §1.2 \| Bedrock AgentCore; Vertex Agent Engine | **Tier 4 VM isolation** \| AWS Bedrock AgentCore Runtime computer-use sandbox primitive (vendor-managed full VM); Anthropic Computer Use VMs (vendor-managed full VM ephemeral network-egress-restricted per Cluster 3 §2.2 [HIGH]); Google Vertex Agent Engine equivalent; managed Firecracker-equivalent at vendor surface \| Anthropic Computer Use VMs; AWS Bedrock AgentCore Runtime computer-use; Vertex Agent Engine |

**Cell selection contract.** Per-cell sandbox provider-class is committed at D2; specific candidate-within-class is deferred to deployment-surface-time × workload-binding-time per §1.10. Operator-policy override of cell-default sandbox tier is permitted at solo-developer × non-compliance cells with audit ledger entry per persona-tier cryptographic shape (D5 §1.4); override is structurally prohibited at multi-tenant-compliance cells per D5 §1.5.2 cross-deployment monotonicity composed with §1.6 below.

**Computer-use cells.** Per Cluster 3 §3.4(d) [MODERATE] and Persona §5 [HIGH], any cell where a computer-use model is bound MUST resolve to **Tier 4 full VM (ephemeral; network-egress-restricted)** regardless of nominal blast-radius-tier — computer-use IS `external-irreversible` because the model can take arbitrary screen-driven action. The 12-cell matrix above commits Tier 4 VM at the `external-irreversible` column of all three deployment surfaces; computer-use binding at workload-binding-time forces resolution to that column.

**LLM-generated-code-execution cells.** Per Cluster 3 §3.4(d) [MODERATE] and Persona §8.1 [HIGH] ("LLM-generated code execution requires F4 sandbox per synthesis §9 Q13"), any cell where the `code-execution-2025-08-25` beta is invoked MUST resolve to **Tier 4 microVM minimum**. The Anthropic-primitive contract per ADR-D3 §1.1 carries an implicit `minimum_sandbox_tier = microvm` annotation; the cell's `sandbox_tier_floor` enforces this regardless of blast-radius declaration.

### 1.2 Sandbox provider-class enumeration

The provider-class taxonomy at D2 layer is closed at six classes; provider-class extensibility (new mechanism class added — e.g., a future eBPF-userspace-kernel class) is a Workflow §4.1.2 Class-2 D2 revision.

| # | Provider class | Mechanism | Cold start | Escape risk | Cluster 3 §2.2 [HIGH] tier mapping | Candidate witnesses (§11.3.2 D2) |
|---|---|---|---|---|---|---|
| 1 | **language-level** | In-process language sandbox (Pyodide; Starlark; ulimit) | ms | high if no lang sandbox | Tier 1 (read-only); Tier 2 only with strict language-level + filesystem-ACL | bytedance/deer-flow LocalSandboxProvider; F4 v1.1 process-tier substrate at Windows-native |
| 2 | **filesystem-overlay / worktree** | Git-worktree isolation (kilocode pattern); fuse-overlay / fuse-projfs (oh-my-pi pattern) | ~10–50ms | medium (filesystem-bound; no process-tier kernel boundary) | Tier 2 (cross-platform filesystem-bound process-tier composable per F4 v1.1 §Decision + ADR-F2) | Kilo-Org/kilocode git-worktree; can1357/oh-my-pi worktree / fuse-overlay / fuse-projfs |
| 3 | **process + ulimit / bubblewrap / Seatbelt** | OS-level process isolation with seccomp / namespacing / sandbox-exec | 10–50ms | medium (kernel CVE class) | Tier 2 (F4 v1.1 process-tier tech commitment: Seatbelt macOS; bubblewrap+socat Linux/WSL) | F4 v1.1 §Decision; reuses Anthropic Claude Code sandboxing pattern verbatim |
| 4 | **container (Docker / Podman; gVisor; Kata)** | Shared-kernel container (Docker; Podman) OR user-space kernel (gVisor) OR microVM-backed container (Kata) | Docker ~100ms; gVisor ~100ms; Kata ~150ms | Docker medium (kernel CVE); gVisor low (~10–30% I/O overhead persistent); Kata very low | Tier 3 (F4 v1.1 §Decision container-tier abstraction Docker-on-OCI as design-time default; gVisor and Kata as escape-risk-low alternatives) | OpenHands Docker; humanlayer/agentcontrolplane K8s container; langgenius/dify dify-sandbox; shareAI-lab/Kode-Agent OpenSandbox |
| 5 | **microVM (Firecracker)** | Hardware-virt microVM with KVM | ~150ms; ≤125ms boot per E2B [HIGH] | very low (hardware boundary) | Tier 4 (F4 v1.1 §Decision deferred microVM-tier tech to D2 — committed here for code-execution cells) | disler/agent-sandboxes E2B (Firecracker); bytedance/deer-flow AioSandboxProvider; langchain-ai/deepagents Modal (gVisor — escape-risk-low alt) / Daytona / Deno backends |
| 6 | **full VM (vendor-managed for computer-use; self-hosted KVM otherwise)** | Hardware-virt full VM; ephemeral; network-egress-restricted | seconds | very low | Tier 4 (F4 v1.1 §Decision deferred full-VM-tier tech to D2 — committed here for computer-use cells) | Anthropic Computer Use VMs (vendor-managed); AWS Bedrock AgentCore Runtime computer-use sandbox primitive; Google Vertex Agent Engine equivalent; self-hosted KVM at self-hosted-server surface |

The eight Pattern Reference Catalog v1.0 §11.3.2 D2 candidates map to this taxonomy as follows: OpenHands (Docker) → class 4; deepagents (Modal / Daytona / Deno) → class 5 (Modal gVisor; Daytona; Deno); deer-flow (Aio) → class 5 (AioSandboxProvider); dify (dify-sandbox) → class 4 (Docker-class container); oh-my-pi (fuse-overlay / fuse-projfs) → class 2; kilocode (git-worktree) → class 2; Kode-Agent (OpenSandbox) → class 4; disler (E2B) → class 5 (Firecracker).

### 1.3 Per-MCP-transport sandbox-tier floor

Per Cluster 4 §2.3.3 [HIGH] MCP authorization spec 2025-06-18 [HIGH] explicitly excludes STDIO transports from OAuth 2.1 + RFC 8707 + RFC 9728 + PKCE ("retrieve credentials from environment"); STDIO MCP servers carry zero protocol-level auth and sandbox is the only boundary. D2 commits the per-MCP-transport sandbox-tier floor table:

| MCP transport | Trust posture (Cluster 4 §2.3.3 [HIGH]) | sandbox_tier_floor | Rationale |
|---|---|---|---|
| **STDIO** | zero protocol-level auth | **Tier 3 container minimum** regardless of declared blast-radius | sandbox is the only boundary; container-tier minimum prevents kernel-CVE-class escape into host filesystem; gVisor or Kata acceptable at trusted-workload subset under operator_policy_floor |
| **Streamable HTTP+SSE, Level 0 (refuse-remote)** | not trusted | REFUSE | Tier-irrelevant; harness rejects connection at MCP server registration |
| **Streamable HTTP+SSE, Level 1 (signed-pinned)** | signed; pinned at registration | per blast_radius_floor | OAuth 2.1 + signature verification provides protocol-level boundary; sandbox-tier follows blast-radius |
| **Streamable HTTP+SSE, Level 2 (sandbox-all)** | sandbox-mediated | **Tier 4 microVM minimum** with allow-listed upstream domains | F4-layer enabler of lethal-trifecta architectural cut per Cluster 4 §2.3.2 [HIGH]; egress allow-listing prevents exfil to attacker-controlled destinations |
| **Streamable HTTP+SSE, Level 3 (allow-with-audit)** | trusted; auditable | per blast_radius_floor with audit ledger | Trust boundary established at OAuth + audit; sandbox-tier follows blast-radius; audit ledger entry per persona-tier cryptographic shape per D5 §1.4 |

The per-MCP-transport floor composes with §1.5 multiplicative `max()` rule — `sandbox_tier_floor` evaluates against tool, deployment-surface, blast-radius-tier, mcp_transport, AND mcp_server (the remote-MCP trust-level input per §1.5.1 rows 4–6) at call time.

### 1.4 Sub-agent sandbox-tier monotonic-ascension

Extending ADR-D4 §1.5 sub-agent privilege inheritance contract:

```
sub_agent_sandbox_tier(parent_sandbox_tier, tool, blast_radius, mcp_transport,
                       deployment_surface, mcp_server) =
    max(
        parent_sandbox_tier,                                            // monotonic ascending
        sandbox_tier_floor(tool, deployment_surface, blast_radius,
                           mcp_transport, mcp_server)
    )
```

**Unconditional rule.** Sub-agent sandbox tier ≥ parent sandbox tier; tier downgrade structurally prohibited; the override clause at D4 §1.5 final paragraph (hierarchical-delegation with explicit operator declaration that child agents own external-reversible authority) does **NOT** extend to sandbox tier — sandbox monotonicity is unconditional even when registry inheritance is overridden.

**Rationale.** Sub-agent registry-downgrade per D4 §1.5 *removes capability* (sub-agent cannot invoke a tool); sub-agent sandbox-monotonicity *constrains containment* (sub-agent runs at no-weaker isolation than parent). Attacker-controlled sub-agent dispatch (e.g., prompt-injection-induced sub-agent spawn per Cluster 4 §2.3.5 [HIGH] CVE-2025-53773 class — attacker flips `chat.tools.autoApprove: true` via injected `~/.vscode/settings.json` then triggers child-agent execution) would otherwise produce a containment regression. Principle-of-least-containment is the wrong principle at the sub-agent boundary; child-agent containment must always meet or exceed parent's.

### 1.5 T-perm-1 D2-layer multiplicative tunable parameter specialization

T-perm-1 (C4 ↔ C10 — capability vs gating) is **promoted to Layer 3** with D2-layer resolution shape encoded as the tunable parameter

```
per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier
```

per spec-writer s3 §6.3. This specializes the D5-layer locked tunable `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier` (per ADR-D5 §1.5) by adding the `sandbox_tier` axis D2 introduces.

#### 1.5.1 Composition rule

Extending ADR-D5 §1.5.1:

```
gate_level(tool, mcp_server, persona_tier, deployment_surface,
           blast_radius_tier, mcp_transport) =
    max(
        per_tool_gate_level,                                    // C4 contract: {auto, ask, deny}
        blast_radius_floor(tool),                               // C10 four-tier taxonomy
        per_mcp_server_trust_floor(mcp_server),                 // C10 five-tier framework
        persona_tier_floor,                                     // D5 §1.5
        sandbox_tier_floor(tool, deployment_surface,            // D2 NEW
                           blast_radius_tier, mcp_transport,
                           mcp_server)
    )

where:
    sandbox_tier_floor:
        (computer-use model bound, *)             → Tier 4 (full VM; ephemeral;
                                                            network-egress-restricted)
        (LLM-generated code execution, *)         → Tier 4 (microVM minimum;
                                                            E2B Firecracker class)
        (STDIO MCP transport, *)                  → max(Tier 3,
                                                        blast_radius_floor)
        (remote MCP, level 0)                     → REFUSE (deny)
        (remote MCP, level 2 sandbox-all)         → max(Tier 4,
                                                        blast_radius_floor)
        (remote MCP, level 1 / level 3, *)        → blast_radius_floor
        (read-only, *, deterministic in-house)    → Tier 1 (operator-tunable
                                                            at solo-developer)
        (local-mutation, *)                       → Tier 2 (process)
        (external-reversible, *)                  → Tier 3 (container)
        (external-irreversible, *)                → Tier 4 (microVM / full VM)
```

**Row→argument keying.** `sandbox_tier_floor` is a 5-argument function — `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier | REFUSE`. Each `where:`-block row band is keyed on a specific argument: rows 1–2 (`computer-use model bound` / `LLM-generated code execution`) are keyed on the **`tool`** argument — these are tool / call-site classifications; row 3 (`STDIO MCP transport`) is keyed on the **`mcp_transport`** argument; rows 4–6 (`remote MCP, level 0` / `level 2 sandbox-all` / `level 1` / `level 3`) are keyed on the remote-MCP trust level read from the **`mcp_server`** argument (the trust level is not derivable from `mcp_transport` — a Streamable-HTTP server may be any of Level 1/2/3); rows 7–10 (`read-only` / `local-mutation` / `external-reversible` / `external-irreversible`) are keyed on the **`blast_radius_tier`** argument. The 3-arg rendering carried at §1.4 prior to the v1.1 → v1.2 reconciliation could not evaluate rows 1–2 (no `tool`) or rows 4–6 (no `mcp_server`); the 5-arg form is the canonical signature at every call site.

The composition is **multiplicative `max()`** — both axes (C4 capability via `per_tool_gate_level` and contract-attached `minimum_tier`; C10 gating via `blast_radius_floor`, `per_mcp_server_trust_floor`, `persona_tier_floor`, `sandbox_tier_floor`) express their concern; the higher tier always wins; neither voice is suppressed; capability and gating reconcile by composition rather than choice.

#### 1.5.2 Composition with operator_policy_floor

Per ADR-F4 v1.1 §Decision `operator_policy_floor` axis, operator-tunable downgrade is permitted with audit ledger entry per D5 §1.4 cryptographic shape:

| persona-tier | operator-policy override of sandbox_tier_floor |
|---|---|
| solo-developer | Permitted at non-compliance cells (Tier 4 → gVisor / Tier 3 → process at short-session × cache-friendly cells); audit ledger entry append-only SQLite |
| team-binding | Permitted only at non-`external-irreversible` cells; audit ledger entry hash-chained SQLite with `prior_event_hash` |
| multi-tenant-compliance | **Structurally prohibited** per D5 §1.5.2 + §1.6; operator-policy override at multi-tenant-compliance produces audit-ledger violation event, not a tier change |

### 1.6 Cross-deployment sandbox-tier monotonicity

Extending ADR-D5 §1.5.2 cross-deployment monotonicity:

When persona tier changes during bridging-arc traversal (solo-developer → team-binding → multi-tenant-compliance), `sandbox_tier_floor` is **monotonic ascending**. Concretely:

- A tool that ran at Tier 2 (process) at solo-developer × local-mutation cells **must ascend** to the team-binding × local-mutation cell's `sandbox_tier_floor` if that floor is higher (e.g., Tier 3 container). The tool cannot remain at Tier 2 process when the bridging-arc traversal raises the floor; tier-equivalence at lower-than-floor is structurally prohibited.
- Tier upgrade is permitted at any time and immediately raises the effective sandbox tier for in-flight workflows.
- Tier downgrade requires explicit Workflow §4.1.2 Class-2 D2 revision.

This is structurally analogous to D5 §1.5.2 `persona_tier_floor` monotonic ascension and composes with it — both floors evaluated jointly produce monotonic-ascending effective gate level under bridging-arc traversal.

### 1.7 Sandbox-boundary span schema (D6 forward-reference)

D2 extends ADR-D4 §1.9 multi-agent span hierarchy schema with sandbox-bounded events. Per the F2-05 sandbox sub-finding resolution at v1.1 (declare-both-with-join semantic honoring F4 §Consequences (a) authoritative names), attribute names follow F4 canonical naming with `sandbox.tech` (technology class) and `sandbox.provider` (vendor+tech instance) declared as distinct attributes joined by belongs-to relation:

```
subagent.span[i] (or root tool.call span)
├── sandbox.enter                    (attrs: sandbox.tier, sandbox.tech,
│                                            sandbox.provider, sandbox.policy.assigned_tier_reason,
│                                            deployment_surface, blast_radius_tier,
│                                            mcp_transport, cold_start_ms,
│                                            pool_acquired: bool, persona_tier)
├── tool.call[]                      (per-tool spans inside sandbox)
├── sandbox.violation                (attrs: sandbox.fail.class ∈
│                                            {escape_attempt, egress_denied,
│                                             timeout, oom, signal, exit_nonzero,
│                                             policy_override},
│                                            severity: ERROR | CRITICAL,
│                                            audit_ledger_entry_id)
│                                    (always-sampled head=1.0;
│                                     tail-keep on classification)
├── sandbox.tier_escalation          (attrs: from_tier, to_tier,
│                                            escalation_trigger, audit_ledger_entry_id)
│                                    (always-sampled head=1.0)
└── sandbox.exit                     (attrs: result_status, sandbox.cost.tier_overhead_ms,
                                             sandbox.cost.tier_overhead_usd,
                                             tokens_in, tokens_out,
                                             pool_returned: bool)
```

Sampling discipline per `c7-observability` SKILL.md head-based-dev / tail-based-prod default — `sandbox.enter` / `sandbox.exit` base-rate sampled (matches `tool.call` parent span); `sandbox.violation` and `sandbox.tier_escalation` always-sampled (head=1.0); cost-attribution-per-sandbox-instance via `sandbox.cost.tier_overhead_*` attrs from F4 v1.1 §Consequences (a) base-rate sampled with per-cell rollup at fan-out close per ADR-D4 §1.9. Sensitive-data discipline per `c7-observability` SKILL.md default-off + structure-not-content discipline: span attributes record sandbox boundary semantics (tier, tech, provider, surface, fail class, policy reason) but never raw tool I/O content; sandbox-resident filesystem state and screenshot context (T-perm-2 surface) are explicitly excluded from span attributes.

**The `sandbox.tech` ↔ `sandbox.provider` join contract.** Per the F2-05 sandbox sub-finding declare-both-with-join resolution, the two attributes operate at different abstraction levels and are jointly populated on every `sandbox.enter` event:

- **`sandbox.tech`** (F4 canonical, technology class) carries values in `{microvm, container, vm, language-level, fs-overlay}` — the sandbox-isolation technology family. Cardinality is low (~5); enables cross-vendor query surfaces ("all microVM-tier failures across vendors" → `sandbox.tech=microvm`).
- **`sandbox.provider`** (D2 introduced, vendor+tech instance) carries values in `{e2b_firecracker, modal_gvisor, kata, docker_oci, bubblewrap, seatbelt, fuse_overlay, fuse_projfs, opensandbox, dify_sandbox, daytona, deno, anthropic_computer_use_vm, bedrock_agentcore, vertex_agent_engine, language_level, kilocode_worktree}` — specific provider+technology bundles. Cardinality is medium (17 values at v1.1 enumeration; phase-2 may add); enables vendor-specific query surfaces ("Bedrock AgentCore-specific failures" → `sandbox.provider=bedrock_agentcore`).

Each `sandbox.provider` value belongs to exactly one `sandbox.tech` class (provider belongs-to tech is functional). The join mapping (referenced as part of the §1.7.1 attribute namespace declaration):

| `sandbox.tech` | `sandbox.provider` values |
|---|---|
| `microvm` | `e2b_firecracker`, `modal_gvisor`, `kata`, `bedrock_agentcore`, `vertex_agent_engine`, `anthropic_computer_use_vm` |
| `container` | `docker_oci`, `opensandbox`, `dify_sandbox`, `daytona` |
| `vm` | (reserved; full-VM tier candidates per F4 deferred microVM/full-VM tier; D2 §1.2 carries this as future) |
| `language-level` | `deno`, `language_level` |
| `fs-overlay` | `bubblewrap`, `seatbelt`, `fuse_overlay`, `fuse_projfs`, `kilocode_worktree` |

The join mapping is operator-tunable at workload-binding-time (operators with custom microVM providers register them under `sandbox.tech=microvm`); the v1.1 mapping is the design-time default per `Pattern Reference Catalog v1.0 §11.3.2 D2` substrate enumeration.

### 1.7.1 Span attribute names declared by §1.7

The §1.7 sandbox-boundary span schema is materialized as the **`sandbox.*` span attribute namespace** ingested by ADR-D6 §1.2 row `sandbox.*` under the OTel/OTLP export contract. D2 §1.7.1 is the canonical declaration site for these attribute names; D6 §1.2 inherits without re-declaration. Seven attribute names declared (six F4-canonical per F4 §Consequences (a) line 40 + line 57; one D2-introduced per the declare-both-with-join resolution):

**F4-canonical attributes (per F4 v1.1 §Consequences (a)):**

- **`sandbox.tier`** — structural, tech-agnostic sandbox-isolation tier. Type: enum string ∈ `{tier-1-process / tier-2-container / tier-3-microvm / tier-4-full-vm}` per F4 four-tier sandbox-isolation tier-set (graduated-isolation principle). Always-emitted on `sandbox.enter` event. Cardinality is bounded (four values).

- **`sandbox.tech`** — discriminator for technology class, swap-friendly without schema migration (per F4 §Consequences (a) line 40). Type: enum string ∈ `{microvm / container / vm / language-level / fs-overlay}`. Always-emitted on `sandbox.enter` event. Cardinality is low (five values at v1.1; phase-2 may add). Composes with `sandbox.provider` per the §1.7 join contract above.

- **`sandbox.fail.class`** — failure-class taxonomy per F4 §Consequences (a) line 40. Type: enum string ∈ `{escape_attempt / egress_denied / timeout / oom / signal / exit_nonzero / policy_override}` per §1.8 fail-class table. Always-emitted on `sandbox.violation` event; always-sampled (head=1.0) per §1.7 sampling discipline. Cardinality is bounded (seven values).

- **`sandbox.policy.assigned_tier_reason`** — audit surface for which `max()` floor won at the per-tool tier-assignment computation (per F4 §Consequences (a) line 57). Type: enum string ∈ `{contract_minimum / blast_radius_floor / mcp_server_trust_floor / operator_policy_floor / sandbox_tier_floor / persona_tier_floor / sub_agent_monotonic_ascension}`. Always-emitted on `sandbox.enter` event. Cardinality is bounded (seven values matching the floor sources composed via §1.5.1 `max()` rule).

- **`sandbox.cost.tier_overhead_ms`** — per-call cost-attribution latency overhead (F4 §Consequences (a) line 41). Type: integer (milliseconds). Always-emitted on `sandbox.exit` event. Cardinality is unbounded (continuous metric); aggregated at metric-export time per `c7-observability` SKILL.md cardinality-safe-attribute discipline.

- **`sandbox.cost.tier_overhead_usd`** — per-call cost-attribution dollar overhead (F4 §Consequences (a) line 41). Type: float (USD). Always-emitted on `sandbox.exit` event. Cardinality is unbounded (continuous metric); aggregated at metric-export time per same discipline.

**D2-introduced attribute (declare-both-with-join with `sandbox.tech`):**

- **`sandbox.provider`** — vendor+technology instance (D2-specific specialization of F4's discriminator concept; declared at v1.1 per F2-05 Option B resolution). Type: enum string carrying the 17-value enumeration declared at §1.7 join table above. Always-emitted on `sandbox.enter` event alongside `sandbox.tech`. Cardinality is medium (17 values at v1.1; phase-2 may add). Operator-tunable at workload-binding-time per `Pattern Reference Catalog v1.0 §11.3.2 D2` enumeration; new providers register under their corresponding `sandbox.tech` class.

**Sampling and composition discipline.** Per `c7-observability` SKILL.md head-based-dev / tail-based-prod default and `c10-action-safety` SKILL.md trust-boundary discipline over the trace store, `sandbox.violation` and `sandbox.tier_escalation` events are always-sampled (head=1.0; tail-keep-on-classification=true) regardless of base sampling rate; `sandbox.enter` and `sandbox.exit` follow base-rate sampling per cell. The `sandbox.tech` and `sandbox.provider` attributes are cardinality-safe at metric-dimensions; the `sandbox.policy.assigned_tier_reason` enum is cardinality-safe at metric dimensions per D6 §1.3 commitment.

**Capability-floor (iv) traceability.** F3 v1.1 capability-floor (iv) requires observable lifecycle including sandbox-related events; §1.7.1 declares the attribute substrate at D2 source per F2-05 sandbox sub-finding closure. ADR-D6 §1.2 row `sandbox.*` reads from D2 v1.1 declarations after this revision; the F4 § Consequences (a) authoritative naming is honored at the source D-ADR (D2) rather than at the synthesis D-ADR (D6) per Pattern P1 mechanical-alignment discipline.

### 1.8 Sandbox-violation fail-class taxonomy (composes with C5 in-loop deterministic gates)

| `sandbox.fail.class` | C5 fail-class (per `c5-validation-contract` SKILL.md) | Retry posture (per `c9-reliability-recovery` SKILL.md) |
|---|---|---|
| `escape_attempt` | permanent-fail | NO retry; immediate HITL escalation per D5 §1.3 validator-escalation |
| `egress_denied` | permanent-fail (deterministic policy hit) | NO retry; tool registry update or HITL escalation |
| `timeout` | transient-fail | C9 backoff + retry; max 3 attempts per Cluster 3 retry protocol [HIGH] |
| `oom` | transient-fail | C9 backoff + retry with sandbox-resource adjustment via operator_policy_floor |
| `signal` (e.g., SIGKILL from operator) | permanent-fail (operator-induced) | NO retry; record audit ledger |
| `exit_nonzero` | depends on tool contract; C5 fail-classification at gate time | Per-tool C9 retry-exit per Cluster 4 §2.2.3 [HIGH] |
| `policy_override` (operator-tunable downgrade per §1.5.2) | informational; not a fail | Audit ledger entry only; no retry |

Pre-HITL escalation order per ADR-D5 §1.10 composes: 1st sandbox-violation (transient class) → C9 backoff + retry; 2nd violation → C6 model-tier escalation per ADR-D3 §1.4; 3rd violation → C11 HITL escalation per D5 §1.3 validator-escalation placement. Permanent-fail violations skip the staircase and go directly to HITL per the discriminated five-class encoding at ADR-D5 §1.10 v1.2 (where D2's sandbox-violation case is one instance of the general validator-failure shape D5 §1.10 generalizes from per the `c5-validation-contract` SKILL.md s14 §7.5(d) locked taxonomy).

### 1.9 Sandbox-pool warm-up protocol (composes with D4 §1.8 concurrent-prompt-cache warm-up)

Per Cluster 3 §2.2 [HIGH] sandbox-stack tradeoff table, parallel sub-agent dispatch with cold sandboxes at Tier 4 produces a cold-start storm. The harness composes sandbox-pool warm-up with D4 §1.8 cache warm-up:

```
on_fanout_dispatch(siblings, cache_breakpoint_id, sandbox_tier):
    1. lead_agent.persist_plan_to_filesystem(plan)              # C2 / D4 §1.8
    2. acquire sandbox_pool[0..N] (eager; pool_size = fan_out_cap)  # D2 §1.9 NEW
    3. dispatch siblings[0] synchronously                        # D4 §1.8
    4. await siblings[0].cache_acknowledgement OR
       await siblings[0].first_token_emission                    # D4 §1.8
    5. dispatch siblings[1..N-1] concurrently into sandbox_pool   # D4 §1.8 + D2 §1.9
```

**Per-surface pool-size policy:** at local-development surface, sandbox-pool size ≤ operator-tunable bounded by hardware capacity (operator-policy override per §1.5.2 with audit ledger entry); at self-hosted-server surface, pool size = fan-out cap per cell with eager warm-up at workflow-start; at managed-cloud surface, sandbox-pool is vendor-managed primitive (Bedrock AgentCore Runtime / Vertex Agent Engine handle pool management).

### 1.10 Workload-binding-time × deployment-surface-time selection contract

Per-cell sandbox provider-class is committed at D2; specific candidate-within-class is deferred to deployment-surface-time × workload-binding-time per the contract below:

| Selection event | Bound at this event | Deferred to next event |
|---|---|---|
| **D2 close (this ADR)** | Per-cell sandbox provider-class; per-cell sandbox tier; per-MCP-transport floor; sub-agent monotonic-ascension; cross-deployment monotonicity; T-perm-1 D2-layer tunable specialization | Specific candidate-within-class per cell (e.g., E2B vs Modal at Tier 4 microVM) |
| **Deployment-surface-time** | Operator declares deployment surface; cells at non-declared surfaces become inactive; operator selects candidate-within-class per active cell | Per-workload-class candidate-tunable refinement |
| **Workload-binding-time** | Per-workload-class candidate tunable refinement (e.g., software-engineering at Tier 4 might prefer E2B for short-session cache-friendly; research-with-computer-use forces full VM) | Per-call-site `sandbox_tier_floor` evaluation (runtime; harness-owned) |
| **Per-call-site (runtime)** | `gate_level()` formula evaluation per §1.5.1; sandbox provider instantiation; sandbox-pool acquisition per §1.9; observability span emission per §1.7 | (terminal — no further deferral) |

## Rationale

**(a) Pattern this decision follows.** The 12-cell deployment-surface × blast-radius-tier matrix follows Pattern Reference Catalog v1.0 §10.3 P-AS-1 (sandbox isolation with per-tool trust tiers — load-bearing pattern at D2 layer) at its converged variation point: corpus convergence on per-tool tiering (OpenHands, DeerFlow, deepagents, Dify, kilocode, oh-my-pi, disler, Kode-Agent) at deployment-surface granularity. The per-cell sandbox provider-class enumeration follows Pattern Reference Catalog v1.0 §11.3.1 F4 candidate set + §11.3.2 D2 candidate set + Cluster 3 §2.2 [HIGH] sandbox-stack tradeoff table. The per-MCP-transport floor follows Cluster 4 §2.3.3 [HIGH] four-level MCP server trust posture composed with the MCP authorization spec 2025-06-18 [HIGH] STDIO-transport zero-protocol-auth implication. The sub-agent monotonic-ascension rule follows ADR-D4 §1.5 sub-agent privilege inheritance contract extended to containment with the principle-of-least-containment-rejected stance. The T-perm-1 D2-layer multiplicative tunable parameter specialization follows the F4-layer + D5-layer resolution shape — multiplicative `max()` composition preserving both C4 capability authority and C10 gating authority. The cross-deployment sandbox-tier monotonicity follows D5 §1.5.2 cross-deployment persona-tier monotonicity extended to containment.

**(b) Persona-constraint application.** Persona §3.1 four-class workload enumeration drives per-cell candidate-within-class refinement at workload-binding-time per §1.10. Persona §5 [HIGH] computer-use at design-time AND production-time with stronger sandbox tier at production-time forces Tier 4 full VM at all `external-irreversible` cells where computer-use is bound. Persona §9 [HIGH] local-development as design-time deployment target makes E2B self-host on KVM hosts the canonical Tier 4 candidate at local-development × external-irreversible per Cluster 3 §2.2 [HIGH]. Persona §10.2 production-time-deployment-surface persona-constrained-but-not-picked drives the OD-3.A 12-cell parametric framing — D2 commits per-surface sandbox decisions without forcing the surface decision. Persona §10.4 compliance-readiness foundational primitives drive the per-persona-tier audit-ledger cryptographic shape composition with D5 §1.4 (solo-developer append-only SQLite; team-binding hash-chained SQLite; multi-tenant-compliance hash-chained + cryptographic signature). Persona §11.10 multi-tenant tenant-isolation drives the multi-tenant-compliance × `external-irreversible` cell vendor-managed-or-managed-cloud commitment.

**(c) T-perm-1 D2-layer stance.** Multiplicative tunable parameter specialization adding `sandbox_tier` as a fifth axis to the locked tunable; per-cell `sandbox_tier_floor` is a D5-layer gate-level extension per §1.5.1. This is structurally identical to the F4-layer + D5-layer resolution shape — both axes (C4 capability via `per_tool_gate_level` and contract-attached `minimum_tier`; C10 gating via `blast_radius_floor`, `per_mcp_server_trust_floor`, `persona_tier_floor`, `sandbox_tier_floor`) express their concern; higher tier wins; neither voice suppressed. The D2-introduced axis maps to call-site dimensions where it dominates (computer-use binding; LLM-generated-code-execution; STDIO MCP transport; operator-policy override; persona-tier binding under bridging-arc traversal).

**(d) Cross-axis composition.** With F4 v1.1 substrate (graduated-isolation principle; tier-set commitment; `max()` composition with four floors): D2 specializes by adding `sandbox_tier_floor` as a fifth floor and committing per-cell binding for the deferred microVM-tier and full-VM-tier tech. With D1 §1.2 per-deployment-surface candidate mapping: D2 inherits surface-row enumeration as the deployment-surface row of the 12-cell matrix; per-cell sandbox candidate enumeration aligns with D1's per-surface engine candidate enumeration where applicable (managed-cloud × Tier 4 sandbox candidates align with Bedrock AgentCore Runtime / Vertex Agent Engine engine candidates per ADR-D1 §1.2). With D5 §1.5 multiplicative gate-level rule: D2 specializes the four-axis tunable to five axes adding `sandbox_tier`; with D5 §1.5.2 cross-deployment monotonicity: D2 extends the rule to `sandbox_tier_floor` per §1.6; with D5 §1.4 per-persona-tier ledger cryptographic shape: D2 composes audit ledger entries for sandbox-violation and sandbox-tier-escalation per persona-tier shape. With D4 §1.5 sub-agent privilege inheritance: D2 extends sub-agent monotonicity to containment per §1.4; with D4 §1.7 HandoffContext serialization: D2 surfaces T-perm-2 adjacency at computer-use sandbox boundary; with D4 §1.8 concurrent-prompt-cache warm-up: D2 composes sandbox-pool warm-up at fan-out per §1.9; with D4 §1.9 multi-agent span hierarchy: D2 extends the schema with sandbox-bounded events per §1.7. With D3 §Decision Skills-as-code-execution composition: D2 commits Tier 4 microVM minimum at all cells where `code-execution-2025-08-25` beta is invoked. With F1 cross-family fallback: harness-owned sandbox tier survives provider fallback; sandbox tier independent of model provider. With F3 v1.1 capability-floor (iv) observable lifecycle: D2 extends the lifecycle event set with sandbox-bounded events. With D6 (forward-reference): sandbox-tier-aware sampling and cost-attribution-per-sandbox-instance forward-referenced for D6 ingestion per §1.7.

## Consequences

**(a) What becomes possible.**

- Per-cell sandbox provider-class commitment at D2 close enables deployment-surface-time × workload-binding-time selection contract per §1.10 — operator declares deployment surface and workload class, harness materializes per-cell sandbox providers per the active matrix row.
- Lethal-trifecta architectural cut per Cluster 4 §2.3.2 [HIGH] becomes structurally available across all three deployment surfaces — the 12-cell matrix's Tier 4 commitment at `external-irreversible` cells with per-MCP-transport floor at Tier 3+ for STDIO transports IS the F4-layer enabler made concrete per cell.
- Sub-agent containment regression (attacker-controlled sub-agent dispatch via prompt-injection; CVE-2025-53773 class) becomes structurally prevented per §1.4 unconditional monotonic-ascension rule.
- Cross-deployment sandbox-tier downgrade under bridging-arc traversal becomes structurally prohibited per §1.6 — workflow continuity across persona-tier upgrade preserved with strict-no-tier-downgrade discipline.
- Per-cell cost-attribution via sandbox-tier-overhead spans per §1.7 enables Persona §6 per-class cost ceiling enforcement accurate to per-call attribution rather than amortized tier rate (continues F4 v1.1 §Consequences (a) primitive).
- Sandbox-pool warm-up at fan-out per §1.9 mitigates the cold-start storm at parallel sub-agent dispatch (Anthropic research system witness fan-out 3–5 [HIGH] at Tier 4 cells); composes with D4 §1.8 cache warm-up at the same fan-out boundary.
- Sandbox-violation as deterministic gate per §1.8 composes with C5 in-loop validator contract — sandbox-violation produces structured fail-class signals consumable by evaluator-optimizer / Reflexion topology cells per ADR-D4 §1.1 row 5.
- Workflow-binding-time selection contract per §1.10 preserves per-workload-class candidate tunability (e.g., E2B for short-session software-engineering; full VM for research-with-computer-use) without re-touching D2 §Decision.

**(b) What becomes harder.**

- Every tool-contract authored from this point forward must declare `minimum_sandbox_tier` per F4 v1.1 §Consequences (b) AND understand the per-cell `sandbox_tier_floor` evaluation at call time (the floor may exceed the contract-declared minimum at cells where deployment-surface, blast-radius, MCP-transport, or computer-use binding raises the floor).
- Operator-policy override at solo-developer × non-compliance cells produces audit ledger entries per persona-tier cryptographic shape per D5 §1.4; the audit ledger surface area expands at every override.
- Bridging-arc traversal (solo-developer → team-binding → multi-tenant-compliance) immediately raises the effective sandbox tier for in-flight workflows per §1.6; operator awareness required during persona-tier transitions; harness must enforce monotonic ascension at the runtime layer (not just at workflow-binding-time).
- Sub-agent monotonic-ascension per §1.4 is unconditional even when D4 §1.5 registry-downgrade is overridden; topology declarations at workload-binding-time must specify per-sub-agent-class sandbox-tier-floor as a topology-declaration field per ADR-D4 §1.11 contract.
- Sandbox-pool warm-up per §1.9 at local-development surface is operator-hardware-bound; pool size > available host capacity produces resource exhaustion at workflow-start; operator-tunable bound required.
- OTLP collector reachability per F4 v1.1 §Consequences (b)(iv) is non-trivial across the four sandbox tiers; D2 inherits the constraint without resolving it — D6 (observability backend) downstream must commit OTLP collector placement per cell.
- The `sandbox_tier_floor` function is the most complex floor in the `max()` composition per §1.5.1 — it carries five explicit arguments (`tool`, `deployment_surface`, `blast_radius_tier`, `mcp_transport`, `mcp_server`); computer-use / LLM-generated-code binding is a property of the explicit `tool` argument (the `where:`-block rows 1–2 are tool-keyed), and the remote-MCP trust level is read from the explicit `mcp_server` argument (rows 4–6); meta-eval per C8 commitment requires per-input-permutation holdout coverage.

**(c) T-perm-1 D2-layer encoding.** Locked tunable becomes `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier`. Tunable parameter specialization is multiplicative (added axis composes via `max()` with the existing four axes). Permanent-tension ledger updates: T-perm-1 D2-layer resolution shape filed; carry-forward to D6 (observability backend) for sandbox-tier-aware sampling commitment.

**(d) Cross-axis tension status.** T-perm-1 promoted to Layer 3 with D2-layer multiplicative tunable parameter specialization. T-perm-3 D1-layer + D4-layer resolutions stand; D2 surfaces adjacency at sandbox cold-start engaging cascade-policy timeout composition; ledger-reference-only carry-forward. T-perm-2 F2-layer resolution stands; D2 surfaces adjacency at computer-use within sandbox crossing within-turn vs across-turn seam; ledger-reference-only carry-forward.

**(e) D6 forward-reference.** Sandbox-tier-aware sampling discipline per §1.7 (always-sampled `sandbox.violation` and `sandbox.tier_escalation`; base-rate `sandbox.enter` / `sandbox.exit`); cost-attribution-per-sandbox-instance via `sandbox.cost.tier_overhead_*` attrs; `sandbox.provider` discriminator attribute for cross-family sandbox-fallback traceability; meta-eval primitive `expected_sandbox_violations_per_session` per workload class per C8 commitment. D6 commits the dashboard binding and the observability backend storage tier downstream.

**(f) Eval primitive commitment.** Sandbox coverage holdout per C8 commitment — per-tool sandbox-tier calibration with TPR ≥ 0.95 on Tier-4-required cases (no false-negatives) and FPR ≤ 0.10 on Tier-2-sufficient cases (cost ceiling per Persona §6); sandbox-escape rate as operator-burden eval primitive `expected_sandbox_violations_per_session` per workload class; meta-eval on each `*_floor` function with per-floor TPR/FPR floor enforced at out-of-loop population-level evaluation.

**(g) Workload-binding-time selection contract.** Per-cell sandbox provider-class committed at D2; specific candidate-within-class deferred to deployment-surface-time × workload-binding-time per §1.10. Workflow §4.1.2 Class-2 D2 revision required for: (i) provider-class extensibility (new mechanism class); (ii) cross-deployment sandbox-tier downgrade (forbidden by §1.6); (iii) per-MCP-transport floor revision (e.g., if MCP authorization spec adds STDIO-OAuth in a future version, the Tier 3 floor for STDIO may revisit).

## Alternatives considered

**Alternative 1: Single-tier-uniform commitment.** Candidate as the simplest cell-uniform shape — one sandbox tier per (deployment-surface, blast-radius-tier) cell with no per-MCP-transport or computer-use overrides. Rejected because cell-uniform tier suppresses two non-negotiable substrate constraints: (i) computer-use → Tier 4 full VM mandatory across all cells where computer-use is bound regardless of nominal blast-radius (Persona §5 [HIGH] + Cluster 3 §3.4(d) [MODERATE]); (ii) STDIO MCP transport → Tier 3 container minimum regardless of declared blast-radius (Cluster 4 §2.3.3 [HIGH] zero-protocol-auth). The per-call-site `sandbox_tier_floor` function is the F4-layer + D5-layer resolution shape extended to D2 — uniform-tier commitment forfeits the structural cut-of-leg per Cluster 4 §2.3.2 [HIGH] lethal-trifecta mitigation that requires call-site-aware tier elevation.

**Alternative 2: Zero-sandbox commitment (language-level only across all cells).** Candidate as the cheapest baseline. Rejected because Cluster 4 §2.3.2 [HIGH] documents filter-based mitigations top out near 97% (Anthropic transparency hub: Sonnet 4.5 + detection prevented 94% MCP / 82.6% computer-use / 99.4% bash); for unsupervised lethal-trifecta-positive deployment per Persona §6 architectural posture, 97% is structurally insufficient — the only reliable mitigation is architectural cut-of-leg via tier composition. Cluster 4 §2.3.5 [HIGH] documents the under-tiering pattern in the field (CVE-2025-53773 GitHub Copilot RCE; CVE-2025-54132 Cursor IDE Mermaid exfil) sharing the same failure mode: a tool surface exists at a tier where blast-radius is not contained.

**Alternative 3: Filter-based-only commitment (no sandbox; rely on prompt-injection detection + output filtering).** Candidate per the Anthropic transparency hub witness suggesting high single-detector accuracy. Rejected per Cluster 4 §2.3.2 [HIGH] structural argument — filter-based mitigations top out near 97%; the 3% residual is structurally insufficient at scale; the lethal-trifecta architectural cut requires structural-not-statistical mitigation. Filter-based detection composes with sandbox tiering (defense-in-depth per Cluster 4 §2.3.4 defense-tradeoff table) but cannot substitute for it.

**Alternative 4: Sub-agent sandbox-tier downgrade permitted under hierarchical-delegation override.** Candidate as the symmetric extension of D4 §1.5 registry-downgrade override to containment. Rejected per §1.4 unconditional monotonic-ascension rule rationale: registry-downgrade *removes capability*; sandbox-monotonicity *constrains containment*; principle-of-least-containment is the wrong principle at the sub-agent boundary because attacker-controlled sub-agent dispatch (CVE-2025-53773 class) is a documented attack class. The override would re-introduce the containment regression D4 §1.5 elsewhere prevents.

**Alternative 5: OD-1.B sandbox-mechanism-class-narrowed scope (defer concrete provider to deployment-time / workload-binding-time; D2 commits class only).** Candidate as the lowest-deliberation-cost option preserving deferral. Rejected at OD-1 selection per session prompt §3 default-application rationale — per-class candidate semantics (Docker per OpenHands; Modal cloud-deployment per deepagents; Firecracker microVM hardware-virt isolation per E2B; gVisor user-space kernel per Modal; git-worktree per kilocode for code-execution-without-process-isolation; E2B-as-managed-service per disler; AioSandboxProvider per deer-flow; OpenSandbox per Kode-Agent; fuse-overlay/fuse-projfs per oh-my-pi; dify-sandbox-under-separate-license per dify) ARE the deliberation surface, not the deferred specification. Deferring to provider-class level produces under-closure relative to OD-1.A — the per-cell candidate witnesses ARE what makes the matrix actionable.

**Alternative 6: OD-1.C deployment-surface-bound-narrowed scope (operator declares one deployment surface at OD-1; candidates outside excluded).** Candidate as the moderate-deliberation-cost option pre-binding the deployment surface. Rejected at OD-1 selection — Persona §10.2 explicitly records production-time deployment surface as persona-constrained-but-not-picked; pre-binding deployment surface at D2 conflates the D2 decision with the deployment-surface decision and forfeits the parametric optionality the persona document records.

**Alternative 7: OD-3.B deployment-surface-declared-at-D2 framing (operator declares one surface at OD-3; per-blast-radius-tier commitment under that surface only).** Candidate as the moderate-complexity output artifact (4-cell row instead of 12-cell matrix). Rejected at OD-3 selection — forces deployment-surface commitment Persona §10.2 records as persona-constrained-but-not-picked at design-time. The 12-cell matrix at OD-3.A is upfront authoring complexity; the operator-burden tradeoff is offset by downstream deployment-surface-time × workload-binding-time clarity per §1.10.

**Alternative 8: OD-3.C blast-radius-tier-only-no-surface-axis framing (4-row commitment; per-surface candidate specifics deferred).** Candidate as the simplest output artifact (4 rows; no per-surface columns). Rejected at OD-3 selection — produces under-closure because per-surface candidate witnesses (OpenHands Docker for local-development; AWS Bedrock AgentCore Runtime for managed-cloud; humanlayer/agentcontrolplane K8s-native for self-hosted-server) ARE part of the deliberation surface. Per-surface differentiation at the cell level is non-trivial (Tier 4 at managed-cloud is vendor-managed Bedrock / Vertex while Tier 4 at local-development is E2B self-host on KVM); deferral to deployment-surface-time without per-surface commitment forfeits the substrate research's deployment-surface-aware enumeration.

## References

### Substrate dependency declaration (shape 1 per Workflow v1.1 §2.3.3.1)

- Cluster 5 V2 §3 D2 (within `Agent_Harness_Architecture__Deployment_Surfaces__Anthropic_Primitives__and_Foundational_Tradeoffs.md`) — deployment-surface-dependent classification; specific sandbox provider derivation from F4.

### Pattern Reference Catalog source citations (shape 2)

- Pattern Reference Catalog v1.0 §10.3 P-AS-1 (sandbox isolation with per-tool trust tiers — corpus convergence on per-tool tiering, divergence on mechanism: Docker / microVM / worktree / agent-server-process; load-bearing pattern at D2 layer).
- Pattern Reference Catalog v1.0 §11.3.1 F4 (tier-mechanism reference enumeration: OpenHands three-layer SDK; deer-flow LocalSandboxProvider/AioSandboxProvider; deepagents CompositeBackend Modal/Daytona/Deno; dify-sandbox; kilocode git-worktree; oh-my-pi worktree/fuse-overlay/fuse-projfs; disler agent-sandboxes E2B; Kode-Agent OpenSandbox).
- Pattern Reference Catalog v1.0 §10.4 P-OD-3 (audit ledger / decision log / hash-chained provenance — composition site for sandbox-violation and sandbox-tier-escalation audit ledger entries).
- Pattern Reference Catalog v1.0 §10.4 P-OD-11 (encrypted-secrets-at-rest with OS-keychain abstraction — composes with sandbox-resident secrets contract via F5 dependency surface).

### Per-axis recommendation citation (shape 3)

- Pattern Reference Catalog v1.0 §11.3.2 D2 lines 3119–3127 (specific sandbox provider — *deployment-surface-dependent*; derived from F4):
  - **OpenHands/OpenHands** — Docker reference.
  - **langchain-ai/deepagents** — Modal / Daytona / Deno backends.
  - **bytedance/deer-flow** — Aio provider.
  - **langgenius/dify** — dify-sandbox.
  - **can1357/oh-my-pi** — fuse-overlay / fuse-projfs.
  - **Kilo-Org/kilocode** — git-worktree.
  - **shareAI-lab/Kode-Agent** — OpenSandbox.
  - **disler / agent-sandboxes** — E2B.

### Parent F-ADR / D-ADR citations (shape 4)

- ADR-F4 v1.1 §Decision (graduated-isolation principle; four-tier sandbox-isolation tier-set — process / container / microVM / full-VM; per-tool tier assignment computed as `max(contract.minimum_tier, blast_radius_floor, mcp_server_trust_tier_floor, operator_policy_floor)` per call site; process-tier tech committed (Seatbelt / bubblewrap+socat / language-level + filesystem-ACL / kilocode-style worktree); container-tier abstraction Docker-on-OCI design-time default; microVM-tier and full-VM-tier tech deferred to D2 per catalog "D2 derived from F4").
- ADR-F4 v1.1 §Consequences (a) (`sandbox.tier` structural attribute + `sandbox.tech` discriminator attribute; `sandbox.fail.class` taxonomy; cost-attribution-per-span via `sandbox.cost.tier_overhead_*`).
- ADR-F4 v1.1 §References (lethal-trifecta architectural cut via Level 2 MCP composition; OTLP collector reachability per tier non-trivial).
- ADR-D1 v1 §1.2 (per-deployment-surface candidate mapping — surface row enumeration source: local-development / self-hosted-server / managed-cloud).
- ADR-D5 v1 §1.4 (per-persona-tier ledger cryptographic shape — solo-developer append-only SQLite; team-binding hash-chained SQLite; multi-tenant-compliance hash-chained + cryptographic signature).
- ADR-D5 v1 §1.5 (multiplicative gate-level rule; T-perm-1 D5-layer resolution shape source — locked tunable `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier`).
- ADR-D5 v1 §1.5.1 (gate_level composition formula; persona_tier_floor enumeration).
- ADR-D5 v1 §1.5.2 (cross-deployment monotonicity; persona_tier_floor monotonic-ascending under bridging-arc traversal).
- ADR-D5 v1 §1.10 (pre-HITL escalation order; model-tier escalation contract).
- ADR-D4 v1 §1.5 (sub-agent privilege inheritance contract; sub-agent registry default-downgrade rule; sub-agent monotonic gate-level ascension — extended at D2 §1.4 to sandbox-tier).
- ADR-D4 v1 §1.7 (HandoffContext serialization contract — T-perm-2 adjacency surface).
- ADR-D4 v1 §1.8 (concurrent-prompt-cache warm-up protocol — composes with D2 §1.9 sandbox-pool warm-up at fan-out).
- ADR-D4 v1 §1.9 (multi-agent span hierarchy schema — extended at D2 §1.7 with sandbox-bounded events).
- ADR-D4 v1 §1.10 (cross-sibling audit-ledger discipline — merkle-root composition for sandbox-boundary events).
- ADR-D3 v1 §Decision (per-cell Skills-as-code-execution-surface adoption depth — composition site for D2 sandbox-tier inheritance at code-execution cells).
- ADR-D3 v1 §1.1 (closed Anthropic-primitive enumeration — Skills system; MCP-as-code; Managed Agents).
- ADR-F1 (cross-family fallback chain composition seam — sandbox tier independent of model provider; harness-owned).
- ADR-F2 (filesystem + git canonical state substrate; combined git tier including kilocode-style worktree-isolation as one process-tier composable; state-ledger entry shape for sandbox-boundary events).
- ADR-F3 v1.1 (capability-floor (iv) observable lifecycle — extended at D2 §1.7 with sandbox-bounded events).

### Persona document trace (shape 5)

- `Persona_Document_v1` §3 (workload-class enumeration as first-class).
- `Persona_Document_v1` §3.1 (primary task classes — software-engineering / content-creation / pipeline-automation / research).
- `Persona_Document_v1` §3.1.1 (software-engineering — F3-mixed; LLM-generated code execution → microVM mandatory per §8.1 [HIGH]).
- `Persona_Document_v1` §3.1.2 (content-creation).
- `Persona_Document_v1` §3.1.3 (pipeline-automation — F3 durable-execution-spine territory).
- `Persona_Document_v1` §3.1.4 (research — browser-driving / computer-use canonical at Anthropic-pattern).
- `Persona_Document_v1` §4 (99.9% completion SLO at tens-concurrent scale).
- `Persona_Document_v1` §5 (integration surface — code execution + computer-use at design-time AND production-time + MCP first-class).
- `Persona_Document_v1` §5.1 (computer-use at production-time with stronger sandbox tier — operator-asserted [HIGH]).
- `Persona_Document_v1` §6 (per-class cost ceiling — composes with sandbox-tier-overhead cost-attribution per §1.7).
- `Persona_Document_v1` §8.1 (software-engineering — F4 sandbox required for LLM-generated code execution per synthesis §9 Q13 [HIGH]).
- `Persona_Document_v1` §8.5 (cross-class pattern — cost × reliability × capability routing).
- `Persona_Document_v1` §9 (deployment-surface implications — local-development as design-time target [HIGH]; microVM-class isolation availability required at production-time [MODERATE]).
- `Persona_Document_v1` §10.2 (production-time deployment surface persona-constrained-but-not-picked; cost-attribution-per-span constraint).
- `Persona_Document_v1` §10.4 (compliance-readiness foundational primitives — hash-chained audit ledger; tenant isolation; secrets rotation; comprehensive observability).
- `Persona_Document_v1` §10.5 (routing-strategy persona-open D-derivative — composes with C6 per-model sandbox-tier).
- `Persona_Document_v1` §11.10 (multi-tenant tenant-isolation specifics open item — D2 §1.1 multi-tenant-compliance row × external-irreversible cell vendor-managed commitment binds at multi-tenant deployment design).

### Substrate research citations (corpus-derived)

- Cluster 3 §1 ¶10 [HIGH] (sandbox-isolation-tier-as-function-of-tool-surface).
- Cluster 3 §2.1.4 (tool-use tradeoff axes including security column across vendor-native / MCP / Code-Execution-with-MCP / Skills / Tool Search Tool).
- Cluster 3 §2.1.5 (failure modes in the field — MCP tool poisoning; rug-pull; indirect prompt injection; Skills malicious script).
- Cluster 3 §2.2 sandbox stack tradeoff table [HIGH] (language-level / container+seccomp / gVisor / Firecracker / full-VM with cold-start, cost overhead, escape risk axes; E2B Firecracker ~150ms boot ≤125ms cold start <5MiB overhead; Modal gVisor ~10–30% I/O overhead).
- Cluster 3 §2.2.5 (failure modes; Reflexion false-positive rate dominance).
- Cluster 3 §3.4(d) [MODERATE — promoted from SPECULATIVE via triangulation per ADR-F4 v1.1 §Rationale (a)] (sandbox-isolation-requirements-by-tool-surface ordering — pure data-read no sandbox; data-write-bounded typed + RBAC; code-execution microVM mandatory; computer-use full VM ephemeral network-egress-restricted).
- Cluster 4 §2.2.7 [HIGH] (per-`{provider, model}` circuit breakers; Stripe-style idempotency keys; full-jitter retry default — composes with sandbox-violation breaker placement per `{deployment_surface, sandbox_tier, sandbox_provider}`).
- Cluster 4 §2.3.2 [HIGH] (Willison lethal-trifecta — three properties; filter-based mitigations top out near 97%; architectural cut-of-leg as only reliable mitigation).
- Cluster 4 §2.3.3 [HIGH] (taint-tracking gate; four-level MCP server trust posture: Level 0 refuse-remote / Level 1 signed-pinned / Level 2 sandbox-all / Level 3 allow-with-audit; MCP authorization spec 2025-06-18 OAuth 2.1 + RFC 8707 + RFC 9728 + PKCE mandatory excluding STDIO transports).
- Cluster 4 §2.3.4 (defense-tradeoff table — capability-removal / sandbox / output-filtering / signed-pinned MCP / audit ledger / HITL).
- Cluster 4 §2.3.5 [HIGH] (in-the-field failures — CVE-2025-53773 GitHub Copilot RCE; CVE-2025-54132 Cursor IDE Mermaid exfil; Anthropic Cowork file-API exfil PromptArmor; Oasis Security Claude.ai URL-param injection; ChatGPT memory exfil; Devin no protection; Google Jules Markdown image exfil).
- Cluster 4 §2.4 [HIGH] (HITL design — sandbox-related HITL triggers compose with eleven-trigger catalog).
- Cluster 4 §2.4.4 [HIGH] (sub-agent HITL composition failure modes — sub-agent interrupt stranding; cascade-timeout composition with parallel sibling sub-agents).
- Cluster 1 §1 [HIGH] (Cognition-Anthropic adjudication — parallelize read/research; serialize writes).
- Cluster 1 §[HIGH] (Anthropic research system witness — 3–5 sub-agents per fan-out for breadth-search; ~15× chat-token budget; concurrent-prompt-cache warm-up requirement).

### Primary-source citations (substrate-anchoring)

- Anthropic, "Claude Code Sandboxing," anthropic.com/engineering/claude-code-sandboxing.
- Anthropic, "Code execution with MCP," Jones/Kelly, Nov 4 2025, anthropic.com/engineering/code-execution-with-mcp.
- Anthropic, "Mitigating the risk of prompt injections in browser use," anthropic.com/news/prompt-injection-defenses.
- Anthropic, "Transparency Hub" (Sonnet 4.5 prompt-injection metrics: 94% MCP, 82.6% computer-use, 99.4% bash), anthropic.com/transparency.
- Model Context Protocol, "Authorization" specification 2025-06-18, modelcontextprotocol.io/specification/draft/basic/authorization.
- Simon Willison, "The lethal trifecta for AI agents: private data, untrusted content, and external communication," simonwillison.net/2025/Jun/16/the-lethal-trifecta/, 16 Jun 2025.
- Johann Rehberger, "GitHub Copilot: Remote Code Execution via Prompt Injection (CVE-2025-53773)," embracethered.com/blog/posts/2025/github-copilot-remote-code-execution-via-prompt-injection/.
- Oasis Security, "Claude.ai Prompt Injection Vulnerability," oasis.security/blog/claude-ai-prompt-injection-data-exfiltration-vulnerability.
- Invariant Labs, "MCP Security Notification: Tool Poisoning Attacks," invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks.
- E2B, Firecracker microVM documentation, e2b.dev/docs.
- Modal, gVisor sandbox documentation, modal.com/docs.
- OpenHands documentation (Docker-based agent-server, separate process), github.com/All-Hands-AI/OpenHands.

### Permanent tension ledger updates

- T-perm-1 (C4 ↔ C10 — capability vs gating): D2-layer multiplicative tunable parameter specialization adding `sandbox_tier` axis. Locked tunable becomes `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier`. Composition rule extends D5 §1.5.1 with `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server)` term (5-arg canonical signature per the v1.1 → v1.2 C-AS-02 reconciliation). Sub-agent monotonic-ascension extends D4 §1.5 to sandbox tier (unconditional). Cross-deployment monotonicity extends D5 §1.5.2 to `sandbox_tier_floor`. Status: promoted to Layer 3 (permanent tension) at D2-layer.
- T-perm-3 (C1 ↔ C9 — control-flow vs reliability): D1-layer `topology_fault_handling` per-deployment-surface mapping + D4-layer `topology_fault_handling × workload_class × topology_pattern` resolutions stand. D2 surfaces adjacency at sandbox cold-start latency engaging cascade-policy timeout composition; ledger-reference-only carry-forward.
- T-perm-2 (C2 ↔ C3 — within-vs-across-turn): F2-layer resolution stands per F3 v1.1 §References explicit framing. D2 surfaces adjacency at computer-use within sandbox crossing within-turn screenshot context (C2 stake) and across-turn sandbox state durability (C3 stake) seam; ledger-reference-only carry-forward.

### Workflow and skill discipline references

- `Project_Workflow_v1_1.md` §2.3.3 (Phase 3b D-ADR exit criteria).
- `Project_Workflow_v1_1.md` §2.3.3.1 (References-section discipline for Phase 3b D-ADRs — five declaration shapes required).
- `Project_Workflow_v1_1.md` §3.2 (Phase dependencies — D-ADR composition against F-ADR parent + Persona document + Cluster 5 V2 §3 substrate dependency declaration).
- `Project_Workflow_v1_1.md` §5.1 DP-1 (Phase 3a/3b execution-agent decision — DP-1-A full-council default applied at Phase 3b kickoff).
- council-orchestrator skill (`/mnt/skills/user/council-orchestrator/SKILL.md`) — convening discipline; Convening Block + CCR + voice contributions + TENSION block emission.
- spec-writer s3 §6.3 (permanent-tension-ledger tunable-parameter encoding architecture) — `sandbox_tier` axis added to T-perm-1 tunable.
- `c10-action-safety` SKILL.md — sandbox within trust-boundary discipline; four-tier blast-radius taxonomy; five-tier MCP-server trust framework; lethal-trifecta architectural cut.
- `c4-tools-integration` SKILL.md — per-tool tier annotation including sandbox-tier-per-tool; sandbox boundary as tool contract surface.
- `c9-reliability-recovery` SKILL.md — sandbox-violation breaker placement per `{deployment_surface, sandbox_tier, sandbox_provider}`; sandbox-pool warm-up at fan-out.
- `c7-observability` SKILL.md — sandbox-bounded span schema; always-sampled `sandbox.violation` and `sandbox.tier_escalation`; cost-attribution-per-sandbox-instance; provider-discriminator attribute.
- `c5-validation-contract` SKILL.md — sandbox-violation as in-loop deterministic gate; fail-class taxonomy.
- `c6-model-routing` SKILL.md — per-model sandbox-tier composition; computer-use → Tier 4 mandatory; cross-family fallback preserves harness-owned sandbox tier.
- `c11-operator-local` SKILL.md — sandbox-violation HITL escalation; operator-policy override audit ledger; in-process OTLP collector reachability per tier.
- `c1-orchestration-control` SKILL.md — sub-agent sandbox-tier inheritance per D4 §1.5; topology-pattern × sandbox-tier composition.
- `c8-eval-engineer` SKILL.md — sandbox coverage holdout; sandbox-escape rate operator-burden eval; meta-eval on `*_floor` functions.
- `c2-context-engineering` SKILL.md — Skills loading discipline composes with sandbox-tier per cell; T-perm-2 adjacency at computer-use screenshot context boundary.
- `c3-state-persistence` SKILL.md — sandbox state isolation; per-sandbox-instance F2 state-ledger entries; T-perm-2 adjacency at across-turn sandbox state durability.
- spec-writer skill (`/mnt/skills/user/spec-writer/SKILL.md`) — synthesis primitive applied at v1.1 revision-pass authoring per Phase 3c-CK iteration 1 close handoff §5.1 Path A skill mapping for Pattern P1 mechanical-alignment passes (F2-05 sandbox sub-finding) and Class 1 documentation drift fixes (F1-01 + F1-02).
- `Project_Workflow_v1_2.md` §3.1 — `Status: Proposed` preservation discipline on revised D-ADRs until P3c-CK clearance; D2 v1.1 carries Proposed posture into iteration 2 entry alongside D1 v1.1 + D5 v1.2 + the remaining D-ADR revisions.
- `Project_Workflow_v1_2.md` §4.1.2 — Class-2 finding resolution path: revised ADR with version bump in the artifact + change-note inline. D2 v1.1 instantiates this shape for F2-05 (Class 2) plus F1-01 + F1-02 (Class 1, folded into the same v1.1 revision pass per the precedent set by D5 v1.1 + D1 v1.1).
- `Adversarial_Review_3c.md` F2-05 sandbox sub-finding (reviewer-confirmed Class 2 — Pattern P1 attribute name drift: D2 §1.7 declares `sandbox.provider` discriminator without surfacing F4 §Consequences (a) authoritative names `sandbox.tech` / `sandbox.fail.class`; F4 commitment `sandbox.policy.assigned_tier_reason` not declared at D2/D6) — v1.1 revision driver.
- `Adversarial_Review_3c.md` F1-01 (Class 1 — D2 §1.4 sub_agent_sandbox_tier function signature/body parameter naming inconsistency `parent_tier` vs `parent_sandbox_tier`) — v1.1 revision driver.
- `Adversarial_Review_3c.md` F1-02 (Class 1 — D2 §1.6 cross-deployment monotonicity prose semantic inversion: "cannot downgrade to Tier 2 ... if Tier 3 is the floor") — v1.1 revision driver.
- Phase 3c-CK iteration 1 close handoff §4.1 D2 row (revision scope: F2-05 sandbox sub-finding resolution at §1.7 + §1.7.1 + §1.8 honoring F4 canonical names with declare-both-with-join semantic for tech/provider; F1-01 + F1-02 mechanical fixes; F2-05 hitl.* sub-finding deferred to D6 v1.1) and §5.1 Path A skill-routing guidance — v1.1 revision-scope authority.

### Convening artifact citations (from this session's substrate review)

- Convening Block + CCR + voice contributions (C10 + C4 co-primaries; C9 / C7 / C2 / C3 / C5 / C6 / C11 / C1 / C8 consultants) — preceding response in this session, segment 1 of 2.
- TENSION block (T-perm-1 promoted to Layer 3 with D2-layer multiplicative tunable parameter specialization adding `sandbox_tier` axis; T-perm-3 / T-perm-2 adjacencies surfaced with ledger-reference-only carry-forward) — preceding response in this session, segment 1 of 2.

---

*Filed 2026-05-10 at Phase 3b Stage 1; revised v1 → v1.1 same date at P3c-CK iter-1 close per `Project_Workflow_v1_2.md` §4.1.2 (F2-05 sandbox sub-finding resolution at §1.7 + new §1.7.1 + §1.8 — declare-both-with-join semantic for `sandbox.tech` (F4 canonical, technology class) ↔ `sandbox.provider` (D2 introduced, vendor+tech instance), join mapping declared, `sandbox.fail.class` rename at §1.7 span schema and §1.8 column header honoring F4 canonical, `sandbox.policy.assigned_tier_reason` declared per F4 §Consequences (a) line 57 commitment; F1-01 §1.4 function signature `parent_tier` → `parent_sandbox_tier` rename for signature/body consistency; F1-02 §1.6 cross-deployment monotonicity prose reworded to disambiguate must-ascend semantic; F2-05 hitl.* sub-finding deferred to D6 v1.1 per Phase 3c-CK iteration 1 close handoff §4.1 D6 row). Recommended next session: continue D-ADR revision-pass authoring track (D3 v1.1, D4 v1.1, D6 v1.1) per Phase 3c-CK iter-2 pre-entry handoff §1.2 D-ADR revision queue, then P3c-CK iter-2 entry adversarial review (`harness-adversarial-reviewer` skill) once all six D-ADR revisions filed; D2 v1.1 enters as iteration-2 input artifact carrying Status: Proposed posture per `Project_Workflow_v1_2.md` §3.1 (promotion to Accepted blocked until P3c-CK clearance). D6 observability backend composition forward-reference per Phase 3b kickoff §4 sequencing carries forward unchanged (D6 is the final Phase 3b D-ADR; D2 v1.1 §1.7 + §1.7.1 sandbox-tier-aware sampling + provider-discriminator + tech-class + cost-attribution-per-sandbox-instance forward-referenced for D6 ingestion).*