# CLAUDE.md

*Workspace governance. Loaded at every session start.*

## 1. Project framing

### 1.3 Canonical authority chain

ADR → ADD → PRD → per-axis spec → per-axis plan → implementation. Earlier artifacts outrank
later ones; when artifacts disagree, the earlier wins. Conflicts route to back-flow per §4.3.

## 4. Substitution + back-flow discipline

### 4.4 NO silent H_T design extension at Phase 7

New H_T primitives surfaced at execution-time route to back-flow before implementation. Never edit
`design-substrate/**` from an execution session — that would be a silent design extension (the X-AL-3 line).

## 11. Posture declaration

Every session is design-phase, Phase 7, or mode-agnostic. Enforce, don't infer.

## 12. Roadmap + drift-detection protocol

§12.1 session-start audit is mandatory: compute the workspace state hash, compare to the dashboard,
HALT on mismatch. §12.3 halt-and-reconcile surfaces drift to the operator before substantive edits.

## 13. Orchestration + effort discipline

§13.1 always-on: call advisor() before substantive work and before declaring done; pair it with
decorrelated out-of-family review. Never fire a paid provider call or relocate a secret unilaterally.

## Appendix B — historical operating notes and accumulated reminders

This appendix collects the long tail of operating notes accumulated across the project's history.
Most of it is provenance — how conventions reached their current form — and reads as reference
material that the always-loaded file no longer needs to carry inline. It grows steadily and is
the single heaviest part of this file. Treat it as the archive of how we got here.

- 2026-05-15: the workspace was bootstrapped at Phase 6.5 Session 6; the original CLAUDE.md was
  authored at the design-phase Drive project and pushed here at session close by the operator.
- 2026-05-17: the OD→IS edge-drift halt-doc item 11 was reconciled; the CXA canonical reading had
  already conformed to the OD plan at v2.3, so the claimed drift was a phantom re-read.
- 2026-05-21: the CP→AS Pattern-P1 seam for U-CP-68 → U-AS-03 was filed at cluster 10-CP-C close;
  runtime enforcement landed at U-CP-70 and the CXA enumeration absorbed it at v2.15.
- 2026-05-28: six CP→IS composer units (U-CP-74..U-CP-79) landed across PRs #39-#44, each importing
  EntryPayload from the IS state-ledger-write module per the CP spec §16.5.3 contract.
- A standing reminder kept here for historical reasons: H_E sub-agent topology (orchestrator-workers
  via the Agent tool) is NOT H_T's TopologyPattern 6-class enum — CP-AL-1 forbids collapsing that
  boundary, which lives at the MCP server process and is enforced by process isolation, not convention.
- 2026-05-29: the venue migration moved authoring from the Drive project to the Claude Code CLI;
  PRs #46-#50 carried the workspace-operational arc and are mode-agnostic by posture.
- 2026-05-31: the §0.4 forward-tracking marker was closed when the six pending CP→IS seams
  transited from PENDING to ABSORBED at CXA v2.17 §2.3.2 rows 38-43.
- 2026-06-01: a four-agent investigation found the AC#2 blocker set was five gaps, not three, and
  authored the sandbox-decision-resolver; two phantom §14.9.7 cite sites were corrected.
- 2026-06-02: the roadmap drift-detection protocol was operationalized so future sessions derive
  their next action from the dashboard without an operator ask-user-question round-trip.
