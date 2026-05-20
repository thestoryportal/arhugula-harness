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

## Known sub-issue — `MCPTrustTier` value-set divergence (surfaced 2026-05-16)

The landed U-CP-00c `MCPTrustTier` enum carries the AS C-AS-10 §10.3 4-level
trust-tier values (`LEVEL_0_REFUSE_REMOTE` / `LEVEL_1_SIGNED_PINNED` /
`LEVEL_2_SANDBOX_ALL` / `LEVEL_3_ALLOW_WITH_AUDIT`), whereas the already-landed
U-CP-43 `MCP_TRUST_GATE_LEVEL_FLOOR` keys on a different 4-value set
(`TIER_1_FIRST_PARTY` / `TIER_2_VENDOR_VERIFIED` / `TIER_3_COMMUNITY_AUDITED` /
`TIER_4_UNTRUSTED`) — both claiming byte-exact C-AS-10 §10.3. When U-CP-43's
`[U-CP-00c]` consumer edge is wired (sub-phase 7c CXA pass), the two value sets
must be reconciled — either a 7c seam mapping or a U-CP-43 micro-revision
conforming its floor-table keys to the U-CP-00c `MCPTrustTier`.

## Routing

Class 1 — informational/coverage. No design-substrate revision required: the 9
types are correct; only the cross-unit composition test is non-materializable
ahead of its consumers. Re-run the acc #10 composition check when the
Pattern-D consumer units land.

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** U-CP-00c landed (9 structured types declared per CP plan v2.8 §2.0c). ACC #10 full-enumeration assertion is bookkeeping carry-forward, not architectural defect.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
