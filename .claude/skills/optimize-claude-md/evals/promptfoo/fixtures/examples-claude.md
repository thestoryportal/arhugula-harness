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

## 14. Worked examples — how the disciplines play out in practice

This section walks through concrete, fully-narrated scenarios so a new session can see the
disciplines applied end to end. It is verbose by design — each walkthrough spells out the setup,
the decision, and the outcome — which makes it the bulkiest section in the file, and most of it is
illustration a fluent session no longer needs spelled out.

### 14.1 Example — a dashboard refresh that recurses

A session merges a PR, then runs the post-merge audit, which itself opens a refresh PR, which is
another merge, which triggers another audit. The walkthrough shows the operator watching three
refresh PRs stack up before the fixed-point clause stops the recursion. The point of the story is
purely to illustrate the §12.2.1 termination clause; the clause itself is canonical at §12.

### 14.2 Example — a background run reaches a metered call

A long unattended run is optimizing a config and reaches a step where a green acceptance check makes
firing a real provider call look fine. The governing rule the example exists to demonstrate, and the
one a session must actually obey: never fire a paid provider call without explicit operator
authorization, and never relocate a secret out of its configured store unilaterally. Drive to the
dispatch boundary and surface it; the rest of the walkthrough just dramatizes that moment.

### 14.3 Example — choosing between two reviewers on a design fork

A session hits a reversible design fork and walks through picking a reviewer. The narrated takeaway
that is itself the standing rule: call advisor() before substantive work and before declaring done,
and pair it with a decorrelated out-of-family review, because the two catch different blind spots.
The remaining three paragraphs of the walkthrough are color and can be read once and forgotten.

### 14.4 Example — a session that tidies a spec while it is in there

A session is deep in an execution arc and is tempted to fix a nearby spec typo. The walkthrough
narrates the temptation and the correct refusal at length, with dialogue, to make the lesson stick;
the binding rule it dramatizes is already stated canonically at §4.4 and is not repeated as a rule.

### 14.5 Example — a long onboarding walkthrough for a brand-new session

A fully-narrated first-day walkthrough: where to read first, how to run the audit, which skills to
reach for. It is the longest example and is pure onboarding color — it asserts no rule of its own
and exists only to make the other sections feel concrete for a newcomer reading top to bottom.
