---
artifact: design-substrate/Spec_Action_Surface_v1.md
version: v1.9
cleared_at: 2026-06-10T21:58:40-06:00
clearance_type: doc-hygiene-refresh
back_reference:
  - roadmap R-CL-P6 (Project_Roadmap_v1.md §5.15; post-MVP full-closure track) — spec-prose ↔ impl hygiene
  - .harness/post-mvp-full-closure-plan-v1.md §2 "Phase P6 — Spec-prose ↔ impl hygiene"
  - .harness/substitutions.yaml rows H_T-AS-8e / H_T-AS-8f / H_T-CP-17 (all SUBSTANTIVE_RETIRED, batch-52) — the authoritative landed-reality source
  - R-810-files-api-integration (Project_Roadmap_v1.md §5.9) — live Files proof, Cloud Trace bfd28fa8fc8ecc3ba973d1e405cdb865
  - R-820-managed-agents-integration (PR #380) — live Managed Agents proof, Cloud Trace 009d7716b19c75e4ad7edb93e78f8d2b
  - .harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md §14.C (the v1.5 Files-deferred ratification this discharges)
  - .harness/class_1_fork_as_8f_managed_agents_namespace_production_only_exclusion.md Q1=(C) (the v1.8 managed_agents-deferred ratification this supersedes)
merge_commit: (pending)
reviewer_chain:
  - pre-substantive empirical grounding 2026-06-10 — premise verified TRUE against the authoritative substitutions.yaml (AS-8e/8f/CP-17 = SUBSTANTIVE_RETIRED batch-52) + live Cloud Trace IDs; producer-sites grounded as code adapters at harness-runtime/.../lifecycle/{files_api,managed_agents}.py
  - advisor pass 2026-06-10 — confirmed approach; 5 execution refinements baked in (supersession-leads-not-buries; §14.6 bridges the v1.5 deferral + cites landed code not phantom C-RT-NN; change-note carries the why-rg-clean spine + negative confirmed; durable follow-on for harness-as/CLAUDE.md; no fresh version-identity hazard)
  - overlay-check clean (305 nodes, 31/31 seams wired); cross-spec rg negative confirmed (all sibling hits are frozen change-note/revision/audit blocks)
  - Codex out-of-family review (pending — pre-merge)
  - spec-writer apply discipline (in-context; edits fully decided + surgical)
  - design-phase posture session 2026-06-10 (auto-detected per workspace CLAUDE.md §11.2 — edits scoped to design-substrate/** only)
supersedes:
superseded_by:
---

# Clearance — `Spec — Action Surface v1.9`

v1.9 is a spec-prose ↔ impl hygiene refresh per roadmap R-CL-P6 (the `[[spec-prose-plan-body-drift-pattern]]` class). It reconciles two now-stale "deferred indefinitely" dispositions in C-AS-14 to the reality landed by R-810 (Files API) and R-820 (Managed Agents). Both arcs shipped real Anthropic adapters with live managed-cloud producer-sites and Cloud Trace proof, and the substitution ledger has recorded `H_T-AS-8e` / `H_T-AS-8f` / `H_T-CP-17` as `SUBSTANTIVE_RETIRED` (batch-52) since those landings — the AS spec prose lagged. Three edits: (i) the §14.5 `managed_agents.*` production-only-exclusion footer gains a **leading** Supersession (v1.9) banner — the v1.8-footer body is preserved verbatim below it (the local-development exclusion + three canonical anchors remain TRUE), but its forward-looking "deferred indefinitely / Re-opens at future managed-cloud arc" conclusion is superseded by the R-820 producer-site at `harness-runtime/.../lifecycle/managed_agents.py`; (ii) a NEW §14.6 `files.*` producer-site footer is authored, discharging the v1.5 "footer NOT authored / Files arc deferred indefinitely per §14.C" deferral now that R-810 materialized the Files arc at `harness-runtime/.../lifecycle/files_api.py` (the §14.6 eight-attribute schema is preserved verbatim); (iii) the stale title header `v1.7` is reconciled to `v1.9` (canonical was already `v1.8` since the 2026-05-28 footer-only pass, recorded in the revision table but never bumped at the header — a version-identity drift).

**Class-3 informational — producer-site asymmetry (not a defect, not fixed in P6).** Unlike `mcp.*` (§14.3 → CP spec C-CP-27 / runtime C-RT-19) and `memory.*` (§14.7 → runtime C-RT-22), the `files.*` and `managed_agents.*` producer-sites are **code adapters** under `harness-runtime/.../lifecycle/` with no separate runtime-spec producer *contract* authored at R-810/R-820. The refreshed footers therefore cite the landed code, not a phantom `C-RT-NN`. The AS spec §14.5/§14.6 attribute schemas remain the canonical declaration; the code emits them. This asymmetry is recorded as an honest hygiene observation; authoring a retroactive runtime-spec producer contract for files/managed_agents is out of P6 scope (and would be a separate design-phase arc if ever wanted).

**Frozen historical preserved; cross-spec "clean" is auditable, not asserted.** The prior-deferral-state prose in sibling artifacts — the v1.5 front-matter notes ("Files §14.6 not authored"), runtime spec v1.17 §14.C + v1.33 change-note (AS-8f indefinite-defer), ADR-D3 §1.1 #10/#11 filing note, and `Project_Workflow_v1_12.md` §7.4.7.3 audit row — are accurate point-in-time records and are NOT edited (stale-carry-text disposition: supersession is recorded forward, not by rewriting history). A cross-spec `rg` for the stale shape still returns those hits; all 6 runtime-spec hits were confirmed to live inside `## Change-note` / revision sections, none in a live contract body asserting deferral as current fact. So the hits are clean by construction.

**Follow-on owed (Phase-7 posture — NOT bundled here, per §11.4 + R-CL-P6 scope).** `harness-as/CLAUDE.md` carries stale prose at the axis-governance layer: line 19 (spec-version pointer still `v1.8`, now v1.9), lines 175/176 (H_T-AS-8e/8f rows still narrated `STILL-BOUNDED-INDEFINITELY`), line 179 (cumulative tally `2/11 STILL-BOUNDED-INDEFINITELY`). The authoritative dispositions already live in `.harness/substitutions.yaml` (both `SUBSTANTIVE_RETIRED`), so this is narrative drift only. It is Phase-7 posture (axis subdirectory CLAUDE.md) and the R-CL-P6 `scope.files` is design-substrate-only, so it is filed as a tracked forward-register follow-on rather than bundled into this design-phase PR. Preferred fix (per R-600 spirit): repoint the tally at the derived `substitution_ledger.py` source rather than hand-refresh a count that will drift again.

## Notes

- Phase 7 consumers may rely on AS spec v1.9 as canonical until a successor marker is filed.
- ZERO field-set change; ZERO attribute-list change; ZERO AS-AL rule added; ZERO change to §13 / §14.1–§14.4 / §15 / §16 / traceability / coherence-pass sections.
- See `.harness/clearance/README.md` for marker discipline.
