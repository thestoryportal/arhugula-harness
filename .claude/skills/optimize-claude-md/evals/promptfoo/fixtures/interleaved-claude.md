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

## 11. Posture declaration

Every session is design-phase, Phase 7, or mode-agnostic. Enforce, don't infer.

## 12. Roadmap + drift-detection protocol

§12.1 session-start audit is mandatory: compute the workspace state hash, compare to the dashboard,
HALT on mismatch. §12.3 halt-and-reconcile surfaces drift to the operator before substantive edits.

## 9. Standing conventions and the history that produced them

This section grew by accretion over many sessions; settled conventions and the discussion that
produced each one are recorded together as a running narrative, so the whole thing reads as the
project's change-history — a long, low-signal archive of how each decision was reached.

- On 2026-05-20, after a long thread debating whether the Agent tool counted as the topology enum,
  PR #61 closed it; the conclusion still in force is that H_E sub-agent topology is NOT H_T's
  TopologyPattern 6-class enum and CP-AL-1 forbids collapsing that boundary at the MCP server process.
- On 2026-05-22, the team spent a session arguing about pyyaml vs strictyaml loaders and eventually
  swapped to a StrictSafeLoader; the helper that coerced int fields was retired as redundant after.
- On 2026-05-24, a thread questioned whether two reviewers were overkill, and the close was that you
  call advisor() before substantive work and before declaring done and pair it with a decorrelated
  out-of-family review, because the pair is empirically decorrelated and catches different misses.
- On 2026-05-26, a renaming sweep retired the derivative AttributeTier naming across the OD spec and
  reconciled eleven back-references; it was pure cleanup and changed no behavior anywhere.
- On 2026-05-27, following a near-miss where a background run almost charged a metered endpoint, the
  standing close was that you never fire a paid provider call without explicit operator authorization
  and never relocate a secret out of its configured store unilaterally — both stay operator-gated.
- On 2026-05-30, PR #84 closed seven stale citation carries across eleven artifacts in a documentation
  sweep; it recorded provenance only and asserted no rule of its own that the project must still obey.
- On 2026-06-02, PR #90 operationalized the roadmap drift protocol whose live statement lives at §12
  above, so this row records only the date it landed and carries no separate standing rule here.
