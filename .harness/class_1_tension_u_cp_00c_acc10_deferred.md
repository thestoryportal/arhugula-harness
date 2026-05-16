# Class 1 Tension — U-CP-00c acceptance #10 partial coverage (halt-route-split-AC)

**Status:** 🟡 PARTIAL — U-CP-00c LANDED; acc #10 full-enumeration assertion deferred.
**Filed:** 2026-05-16 (Phase 7 7b, CP axis-stream).
**Unit:** U-CP-00c — declare the 9 CP-owned structured shared types.
**Plan:** `Implementation_Plan_Control_Plane_v2_8.md` §2.0c.

## What landed

All 9 structured types (`ActorIdentity`, `AgentRole`, `ModelBinding`,
`ProviderAgnosticPayload`, `RoutingDecisionTrace`, `TraceContext`,
`TailKeepPredicate`, `MCPTrustTier`, `Axis`) declared at
`harness-cp/src/harness_cp/cp_shared_types.py`. Accs #1–#9 + #11 fully covered
by per-type isolated tests.

## What is deferred (halt-route-split-AC)

Acc #10 asserts "each of the 15 direct Pattern-D consumer units (§0.5)
resolves a single nominal type via `[U-CP-00c]`; `pyright` strict resolves one
nominal type per type across all consumers" and prescribes
`test_pattern_d_consumers_resolve_single_nominal_type` as a cross-unit
composition check across all 15 consumer units.

The 15 consumers are U-CP-03, 04, 05, 09, 13, 14, 27, 29, 30, 32, 43, 45, 49,
50, 51. At U-CP-00c landing time only **U-CP-27 and U-CP-43 are landed**, and
U-CP-29 / U-CP-34 land later in this same batch. The remaining 11 are HALTED
(undeclared Pattern-D structured types: `ProposedAction` / `FailedAttempt` /
`Alternative` / `RetryHistory` / `RetryPolicy` / `InferenceRequest` — see the
shared carrier-map "Open — Class 1 halt" row and `.harness/pipeline-fork-queue.md`).

The full 15-consumer composition assertion cannot be materialized — most
consumers do not exist as landed code. Per the halt-route-split-AC pattern the
materializable part (the 9 type declarations + their isolated conformance
tests) is landed; the full-enumeration assertion of acc #10 is struck and
deferred until the Pattern-D structured-type consumer halts clear.

## Routing

Class 1 — informational/coverage. No design-substrate revision required: the 9
types are correct; only the cross-unit composition test is non-materializable
ahead of its consumers. Re-run the acc #10 composition check when the
Pattern-D consumer units land.
