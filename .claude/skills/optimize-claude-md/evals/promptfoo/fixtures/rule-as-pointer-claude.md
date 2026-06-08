# CLAUDE.md

*Workspace governance. Loaded at every session start.*

## 1. Project framing

### 1.3 Canonical authority chain

ADR → ADD → PRD → per-axis spec → per-axis plan → implementation. Earlier artifacts outrank later
ones; when artifacts disagree, the earlier wins. Conflicts route to back-flow per §4.3.

## 4. Substitution + back-flow discipline

### 4.4 NO silent H_T design extension at Phase 7

New H_T primitives surfaced at execution-time route to back-flow before implementation. Never edit
`design-substrate/**` from an execution session — that would be a silent design extension (the X-AL-3 line).

## 5. Sub-agent boundary

CP-AL-1: H_E sub-agent topology (orchestrator-workers via the Agent tool) is NOT H_T's
TopologyPattern 6-class enum. Do not collapse the boundary; it lives at the MCP server process.

## 11. Posture declaration

Every session is design-phase, Phase 7, or mode-agnostic. Enforce, don't infer.

## 12. Roadmap + drift-detection protocol

§12.1 session-start audit is mandatory: compute the workspace state hash, compare to the dashboard,
HALT on mismatch. §12.3 halt-and-reconcile surfaces drift to the operator before substantive edits.

## 13. Orchestration + effort discipline

§13.1 always-on: call advisor() before substantive work and before declaring done; pair it with
decorrelated out-of-family review.

For the boundary on firing a metered provider request or moving a credential, see the operator-feedback
record: a background or autonomous session may drive a task up to the dispatch / credential edge but must
never fire the paid call or relocate the secret itself without explicit operator authorization at that edge.

## 14. Operating-history notes

This section is the running archive of how the orchestration conventions above reached their current
form. It is the heaviest part of the always-loaded file, almost entirely provenance, and it grows
with every retrospective. None of it changes what the agent does today — it explains how we got here.

- 2026-05-31: the council pilot established the nameable-tension discriminator; councils that converge
  to a single voice plus cosmetic consultants were ruled a primary-collapse failure mode.
- 2026-06-01: the ultracode retrospective concluded that the cheap verification disciplines, not raw
  reasoning depth or multi-agent fan-out, are what catch the bugs; ultracode is not a standing default.
- 2026-06-02: the Claude Code insights report surfaced recurring friction across 197 sessions and
  motivated the always-on execution + interaction conventions now recorded at §14 of the live file.
- 2026-06-03: the Codex out-of-family reviewer was ratified as the default pre-merge diff reviewer,
  with a documented division of labor against the transcript-aware advisor() reviewer.
- 2026-06-04: the deterministic no-API skill-eval loop was landed so a SKILL can be self-improved in
  session against a promptfoo fitness function with hard anti-Goodhart gates, zero metered calls.
