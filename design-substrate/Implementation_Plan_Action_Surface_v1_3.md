# Implementation Plan — Action Surface v1.3

## Change-note (v1.2 → v1.3)

**Scope of revision.** Phase C atomic-unit decomposition pass per Remaining-Work Closure Arc plan file. Thin revision-pass absorbing AS spec v1.4 (annotation-only producer-site reference notes at C-AS-14 §14.3 + C-AS-15 §15). **Zero new atomic units.** v1.2 substantive content preserved verbatim.

**Source of fix.** AS spec v1.4 producer-site reference notes documenting that `mcp.*` namespace emission is now contracted via CP spec v1.10 §27 C-CP-27 MCPClientNamespaceEmitter; `sandbox.*` namespace emission is now contracted via runtime spec v1.13 §14.9 C-RT-19 RuntimeToolDispatcher. The AS spec change is documentary; no contract signature change; no new implementation surface.

**Spec authority chain.** AS spec v1.4 §14.3 + §15 producer-site reference notes — no new AS-AL rules; no new AS-axis contracts.

**Plan shape preserved.** v1.2's 9-cluster axis-led structure preserved verbatim. No new clusters; no new units.

**Sections preserved verbatim from v1.2.** ALL v1.2 content preserved. The v1.2 + v1.1 + v1 chain preserved.

**Status posture.** Proposed (v1.2) → Proposed (v1.3). v1.3 is a documentary-only patch — version bump for traceability per `Project_Workflow_v1_8.md` §7.4 use-latest-version body-citation-alignment.

**Downstream absorption owed (post-v1.3).** Workspace `CLAUDE.md` §2.4 AS row version bump (v1.2 → v1.3); `harness-as/CLAUDE.md` §1.2 + §4.1 spec version cite update.

---

## §1 — No new atomic units

No new AS-axis atomic units owed at Phase C. The AS spec v1.4 changes are documentary references to:
- Runtime spec v1.13 §14.9 (C-RT-19 — sandbox.* producer-site at tool-invocation runtime); materialized at Implementation_Plan_Harness_Runtime_v2_11.md U-RT-67.
- CP spec v1.10 §27 (C-CP-27 — mcp.* producer-site at MCPClientNamespaceEmitter); materialized at Implementation_Plan_Control_Plane_v2_15.md U-CP-69.

The AS-axis carriers (`sandbox_*` namespace schemas at `harness-as/src/harness_as/sandbox_*.py`; `mcp_*` namespace schemas) remain at v1.2 unit landings (U-AS-22 through U-AS-29 et al.); no re-decomposition.

---

## §2 — Coverage matrix delta (v1.2 → v1.3)

No coverage delta. AS contracts C-AS-01 through C-AS-16 retain their v1.2 unit coverage verbatim. The new annotation NOTEs at C-AS-14 §14.3 + C-AS-15 §15 are documentary; no coverage row added.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Action_Surface_v1_3.md` |
| Version | v1.3 |
| Filing event | Phase C atomic-unit decomposition pass (thin revision-pass for traceability), 2026-05-21 |
| Predecessor | `Implementation_Plan_Action_Surface_v1_2.md` |
| New units | 0 |
| DAG verification | Unchanged (no new units; no graph delta) |
| Coverage verification | Unchanged (no contract delta) |
| Date | 2026-05-21 |
