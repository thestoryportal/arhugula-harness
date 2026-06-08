# CLAUDE.md

*Workspace governance. Loaded at every session start.*

## 1. Project framing

### 1.3 Canonical authority chain

ADR → ADD → PRD → per-axis spec → per-axis plan → implementation. Earlier artifacts outrank later
ones; when artifacts disagree, the earlier wins. Conflicts route to back-flow per §4.3.

## 4.4 NO silent H_T design extension at Phase 7

New H_T primitives surfaced at execution-time route to back-flow before implementation. Never edit
`design-substrate/**` from an execution session — that would be a silent design extension (X-AL-3).

## 5. Sub-agent boundary

CP-AL-1: H_E sub-agent topology is NOT H_T's TopologyPattern 6-class enum. Do not collapse the
boundary; it lives at the MCP server process.

## 11. Posture declaration

Every session is design-phase, Phase 7, or mode-agnostic. Enforce, don't infer.

## 12. Roadmap

§12.1 session-start audit is mandatory: compute the workspace state hash, compare to the dashboard,
HALT on mismatch.

## 13. Orchestration

§13.1: call advisor() before substantive work and before declaring done.

## 16. Secrets, credentials, and the long history of how they are handled

This section is by far the heaviest in the file. It interleaves the standing rule on credential
handling with the full historical narrative of how that rule was arrived at, recorded for posterity
across many retrospectives. The bulk of it is provenance — the story, not the rule — and the always
loaded file does not need to carry the whole saga inline every session. It grows with every incident.

- 2026-05-22: the keyring backend choice was settled on python-keyring after evaluating three
  alternatives; the rejected options and the benchmark notes from that evaluation are recorded here
  for anyone who wants to reopen the decision, along with the rationale for each rejection.
- 2026-05-24: an early background-agent prototype attempted to relocate a provider key from the
  operator's environment into a worktree-local file to make an autonomous run self-contained; this
  was flagged in review as exactly the failure the boundary exists to prevent and was reverted.
- 2026-05-26: the secrets-via-just recipe was documented after several sessions tried to source the
  dotenv file directly; the just dotenv-load path became the single supported injection mechanism
  and the direct-sourcing attempts were catalogued as an anti-pattern with their failure signatures.

STANDING RULE — never relocate a secret or fire a paid provider call from a background or autonomous session without explicit operator authorization at the dispatch/credential edge.

- 2026-05-29: the keyring-vs-env precedence was clarified after a session loaded a stale key from
  the environment that shadowed the keyring entry; the precedence order and the debugging trail that
  surfaced it are recorded here in full for future reference.
- 2026-06-02: the provider-secret env-artifact gotcha was documented when local check runs showed
  three red provider tests that were green in CI because just's dotenv-load injects the keys; the
  full reproduction and the env-unset workaround are written up here at length.
- 2026-06-05: the credential-rotation runbook was drafted and then deferred; the draft steps and the
  reasons it was held are preserved here so the next attempt does not start from scratch.
