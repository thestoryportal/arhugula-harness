# Governance pack — project framing + bootstrap state

*Relocated BYTE-VERBATIM from Root `CLAUDE.md` §1.1, §7, §9, §9.1 by U-CTX-13 (R-CTX-1 Arc 5, 2026-08-11).*
*The root file keeps every heading with its number and position, plus a resolving
pointer to this file. Query this pack for the detail; do not preload it.*

---

### 1.1 What this workspace builds

This workspace implements **H_T** (the target harness aka Arhugula v2) — a multi-LLM agent harness — under the **H_E** execution surface (Claude Code CLI). H_T is specified by the design-phase artifact corpus enumerated at §2. H_T implementation traverses the per-axis atomic-unit plans at §2.4 in topological-sort order per per-axis-plan dependency graphs. H_E provides the development environment, IDE substrate, and bounded substitutions for not-yet-built H_T primitives (see §4).

The harness has four design axes plus a cross-axis composition surface:

| Axis | Scope |
|---|---|
| **IS** — Information Substrate | State ledger (6-field hash-chained entries per C-IS-05 §5), content-addressed index, semantic cache, filesystem-path classification |
| **AS** — Action Surface | Tool contracts (typed I/O schemas), MCP integration (FastMCP host + client), sandbox (4-tier blast radius), skills filesystem |
| **CP** — Control Plane | Routing (capability-aware multi-LLM), retry / breaker / idempotency, workflow lifecycle, topology (6-class enum), HITL placement |
| **OD** — Operational Discipline | HITL primitives (4-response palette), audit ledger schema, cost attribution (5-step chain), observability (15-namespace OTel schema per C-OD-05 §5.1) |
| **CXA** — Cross-Axis Composition | **107 plan-canonical cross-axis relationships** across 7 composition buckets per `Cross_Axis_Composition_Document_v2_23.md` §2.3 — **37 genuine typed seams + 48 convention-level + 22 phase-2-runtime** (this plan-derived 7c baseline is FROZEN), **+2 R-PM-1 prompts-management forward-capability seams at §2.3.8 (CP→IS + OD→CP, runtime-mediated `R-live`) +1 B-54 audit-verification seam at §2.3.9 (CP→OD, runtime-mediated `R-live` since 2026-07-20/PR #1067; registered `R-planned` at v2.21, 2026-07-18) +1 B-33 rotation-pair-evidence seam at §2.3.10 (CP→OD, runtime-mediated; registered `R-planned` at v2.22, 2026-07-23 — flips `R-live` at the impl arc) = 111 total**.|

## 9. Workspace bootstrap state

This workspace was bootstrapped at Phase 6.5 Session 6 (ε) per `Phase_6_5_Session_6_Kickoff.md`. Bootstrap substrate authored at design-phase workspace; pushed to this workspace at Session 6 close (operator action).

### 9.1 Filing footer

| Field | Value |
|---|---|
| Artifact | `CLAUDE.md` (workspace root) |
| Authored at | Phase 6.5 Session 6 (ε), 2026-05-15 |
| Authoring authority | `Phase_6_5_Session_6_Kickoff.md` §2.1.1 |
| Predecessor authoring | Design-phase context (historical: separate Claude.ai project through 2026-05-28; forward: Claude Code CLI per operator decision 2026-05-29) |
| Successor consumption | Phase 7 Session 1 onward (this workspace) |
| Revision policy | This file is canonical for this workspace; revisions route to design-phase back-flow (§4.3) prior to in-workspace edit |

---

