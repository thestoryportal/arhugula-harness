# Phase 7d Retirement Events — Batch 19

| Field | Value |
|---|---|
| Batch number | 19 |
| Filed at | 2026-05-26 (post AS-4 Reading B arc 2 close at worktree HEAD `c3545b6` — 5/5 new e2e tests pass against in-process fastmcp echo fixture verifying the `sandbox.violation` child span emits BOTH `mcp.fail.class` (§15.8 direct) AND `sandbox.fail.class` (§15.10 projected) attributes across the 4 MCPInvocationFailClass paths plus a happy-path no-violation regression guard; production bug at `runtime_tool_dispatcher.py:400+:407` empirically replaced with isinstance dispatch via real-fastmcp exercise) |
| Filed by | `phase-7-substitution-retirement` skill §3.2 verification-shape steps 1–5 per the Reading B resolution path operator-ratified at 2026-05-25 + arc 2 impl close 2026-05-26 |
| Predecessor batch | `phase-7d-retirement-events-batch-18.md` (2026-05-24, 1 PARTIAL → RETIRED two-step within-batch for H_T-CP-22 via CP composer authoring arc at `671f195`; cumulative 27/49 RETIRED + 0 RETIRE-READY + 8 PARTIAL = 35/49 advanced per §6 footer; operator-opt-in RETIRE-READY bucket EMPTY post-batch-18; CP-axis 14/22 at 63.6%) |

---

## §0 Batch context

**Status type: 1 PARTIAL → RETIRED transition (H_T-AS-4). Cumulative RETIRED count advances 27/49 → 28/49 (55.1% → 57.1%); PARTIAL count decrements 8 → 7; pipeline-advanced unchanged at 35/49 (71.4%) — within-tier promotion of one row PARTIAL → RETIRED. FIFTH RETIRED close since the operator-opt-in pattern catalogue (joins CP-16 batch-14, CP-18+AS-2 batch-16, CP-21 batch-17 corrective, CP-22 batch-18). AS-axis crosses 4/6 RETIRED (66.7%, +1 from batch-16) — AS-axis exits "at-most-3-RETIRED" plateau held since batch-2 (AS-1 + AS-9 + AS-2 jointly).**

This batch records the sandbox-violation child-span composer transition for **H_T-AS-4** (sandbox.* 7-attribute OTel namespace at MCP server) from PARTIAL → RETIRED via the Class 1 fork Reading B arc landed in this worktree across 3 commits this session-cluster:

| Commit | Artifact | Authority |
|---|---|---|
| `bb2474d` | AS spec v1.5 → v1.6 amendment — NEW §15.8 `MCPInvocationFailClass` 4-value StrEnum + §15.9 `mcp.fail.class` dual-attribute emission discipline + §15.10 best-effort projection table MCP-shape → F4-shape | Operator-ratified Reading B at `.harness/class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` §7, 2026-05-25 |
| `54b992d` | AS plan v1.3 → v1.4 + harness-as impl + 17 new unit tests — U-AS-03 carrier-extension (`MCPInvocationFailClass` + `project_mcp_to_sandbox_fail_class`) + U-AS-17 AC #3 text-replace + ACs #9/#10 + `SANDBOX_VIOLATION_ATTRIBUTES` extended to `frozenset({"sandbox.fail.class", "mcp.fail.class"})` + `MCP_INVOCATION_ATTRIBUTE_SCHEMA` NEW sibling tuple | Spec-revision-driven plan revision via `implementation-planner`; carrier impl via `phase-7-implementation` |
| `c3545b6` | harness-runtime impl — production bug fix at `runtime_tool_dispatcher.py:395-412` (replaced invented-string dead-code assignments with isinstance dispatch); NEW `_emit_sandbox_violation` helper opening `sandbox.violation` child span on exception path with dual fail-class attrs; 5 new e2e tests against real fastmcp echo fixture (4 exception-class paths + happy-path no-violation regression guard) | Plan v1.4 §1 + §2 ACs; producer-side mutation discipline per runtime spec §14.9 |

Per the operator-ratified runtime-only substitution-site reading at `.harness/phase-7d-retirement-ledger-v2.md` §2.1 + line-33 strict-reading discipline + the batch-16 §6 verification-shape sharpening discipline (first prospectively applied at batch-17 §4):

> RETIRED = (criterion A MET) ∧ (criterion B structural-MET) ∧ (criterion B operational-MET) — where operational-MET requires all 3 binding-chain stages empirically verified: (1) carrier landed; (2) production span site exists at the producer dispatcher; (3) e2e exercise PASS against a real substrate.

Under that discipline, H_T-AS-4 transitions PARTIAL → RETIRED via Reading B resolution:

- **Criterion A** (cited unit IDs landed). U-AS-10 / U-AS-11 / U-AS-12 / U-AS-13 / U-AS-14 / U-AS-15 all landed at v1.2 baseline (per harness-as/CLAUDE.md §1.3 cluster L0-L3 enumeration). U-AS-03 carrier-extension landed at v1.4 amendment per arc 2 commit `54b992d`. U-AS-17 acceptance criteria absorbed (AC #3 text-replace + ACs #9/#10).
- **Criterion B structural-MET.** NEW MCPInvocationFailClass 4-value StrEnum + projection function carried at `harness-as/src/harness_as/sandbox_fail_class.py` per AS spec v1.6 §15.8/§15.10. `SANDBOX_VIOLATION_ATTRIBUTES` extended to dual-attribute set per §15.9. Producer-site `_emit_sandbox_violation` helper at `runtime_tool_dispatcher.py:268-289` opens `sandbox.violation` child span on the dispatcher exception path emitting both attributes before re-raise.
- **Criterion B operational-MET.** 5 new e2e tests at `harness-runtime/tests/test_lifecycle_runtime_tool_dispatcher.py:484-666` empirically traverse the 3-stage binding chain end-to-end:
  - `test_dispatch_transport_failure_emits_sandbox_violation_dual_attrs` — `MCPHostUnreachableError` path → `mcp.fail.class=transport` + `sandbox.fail.class=exit_nonzero`
  - `test_dispatch_protocol_error_emits_sandbox_violation_dual_attrs` — `ToolInvocationProtocolError` path → `mcp.fail.class=protocol_error` + `sandbox.fail.class=exit_nonzero`
  - `test_dispatch_timeout_emits_sandbox_violation_dual_attrs` — `ToolInvocationTimeoutError` path → `mcp.fail.class=timeout` + `sandbox.fail.class=timeout` (value-name parity per §15.10 row 4)
  - `test_dispatch_schema_violation_emits_sandbox_violation_dual_attrs` — `jsonschema.ValidationError` path → `mcp.fail.class=schema_violation` + `sandbox.fail.class=policy_override` (HIGH semantic stretch per §15.10 row 3)
  - `test_dispatch_happy_path_emits_no_sandbox_violation` — success path emits sandbox.exit without sandbox.violation (regression guard)

All 5 tests open real OTel TracerProvider with InMemorySpanExporter; 4 of 5 use real fastmcp echo server with monkeypatched `call_tool` to raise the target exception post-MCP-span-open; the 5th uses a strict output-schema fixture forcing `jsonschema.ValidationError` through the dispatcher's own `_validate_response_schema` step (no patching). Spans are inspected post-dispatch to verify the `sandbox.violation` span name and dual-attribute presence.

**Conclusion (preview):** **1 new RETIRED transition** (H_T-AS-4) — cumulative **28/49 RETIRED** (57.1%, +1 from batch-18). PARTIAL count **8 → 7** (AS-4 promoted out). Pipeline advanced (RETIRED + RETIRE-READY + PARTIAL): **35/49 = 71.4%** (unchanged from batch-18; composition shifts +1 RETIRED / −1 PARTIAL). **AS-axis crosses 4/6 RETIRED (66.7%).** **Fifth RETIRED close since operator-opt-in pattern catalogue.** ZERO cross-axis cascade at retirement-event semantics (3 adjacent OD/CXA/ADR-D2 cascades surfaced at AS plan v1.4 §3 NOT patched per FM-2).

---

## §1 H_T-AS-4 PARTIAL → RETIRED

### §1.1 Pre-transition state (batch 18 close, 2026-05-24)

Per `harness-as/CLAUDE.md` §4.1 + `phase-7d-retirement-events-batch-16.md` §"AS-axis sibling rows" preserved verbatim through batch-17 + batch-18:

> H_T-AS-4 (sandbox.* 7-attribute namespace) | **PARTIAL** (batch 11 doc-hygiene transition) | 6 of 7 `sandbox.*` attrs declared at `runtime_tool_dispatcher.py:179-184` (`sandbox.tier`, `sandbox.tech`, `sandbox.provider`, `sandbox.policy.assigned_tier_reason`, `sandbox.cost.tier_overhead_ms`, `sandbox.fail.class`) emit at production `sandbox.enter` + `sandbox.exit` spans (commit `83d3b54` U-RT-67); 7th `sandbox.violation` deferred per `runtime_tool_dispatcher.py:414` comment ("sandbox.violation deferred").

The PARTIAL gate text identified the `sandbox.violation` span absence as the residual gap. Class 1 fork audit at `.harness/class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` discriminator pass (filed 2026-05-25 at commit `654f7ee`) surfaced 3 distinct defects on the path to closing this gap:

- **(i) Production bug.** `runtime_tool_dispatcher.py:400` assigned `sandbox_fail_class = "transport"` and `:407` assigned `"schema-violation"` — both strings NOT in canonical F4 `SandboxFailClass` enum at C-AS-04 §4.1 (`escape_attempt` / `egress_denied` / `timeout` / `oom` / `signal` / `exit_nonzero` / `policy_override`). The strings were dead code: `raise` at line 401 exited the `try` block before reaching the `sandbox.exit` emission at line 420, so the local variable was never read.
- **(ii) Span absence.** `sandbox.violation` child span was deferred per `:414` comment. The PARTIAL row pointed at this gap as the operational close gate.
- **(iii) Structural taxonomy mismatch.** F4 enum is process-execution-shaped (containment breach / OS-level failure modes); production exceptions at the MCP-protocol boundary are MCP-protocol-shaped (`ToolInvocationTimeoutError`, `ToolInvocationProtocolError`, `MCPHostUnreachableError`, `jsonschema.ValidationError`). A direct rename of the invented strings to F4 enum values would preserve the bug at semantic layer.

### §1.2 Reading B resolution path (2026-05-25 → 2026-05-26)

Operator-ratified Reading B per fork doc §7 selected the architecturally cleanest path: NEW MCP-protocol-layer fail-class taxonomy authored at AS spec §15 sibling to F4 at C-AS-04 §4.1, preserving F4 enum semantic coherence while providing the proper abstraction layer for production MCP-protocol exceptions.

Spec amendment at `bb2474d` (AS spec v1.5 → v1.6) landed the contract surface:
- **§15.8** — `MCPInvocationFailClass` 4-value StrEnum (`transport` / `protocol_error` / `schema_violation` / `timeout`) at AS-axis as canonical declaration site. Cardinality bounded (4). Sibling to F4 at C-AS-04 §4.1.
- **§15.9** — `mcp.fail.class` attribute on `sandbox.violation` child span sibling to `sandbox.fail.class`. Dual-attribute emission discipline: both names always-emitted on the event; either MAY carry null per the 5-row scenario matrix.
- **§15.10** — best-effort projection table MCP-shape → F4-shape for cross-layer audit-ledger continuity. Row 3 (`schema_violation → policy_override`) flagged HIGH semantic stretch; row 4 (`timeout → timeout`) clean at value-name parity; rows 1+2 (`transport`/`protocol_error → exit_nonzero`) MODERATE stretch.

Plan + impl absorption at `54b992d` (AS plan v1.3 → v1.4 + harness-as impl + 17 unit tests) + `c3545b6` (harness-runtime impl + 5 e2e tests). See §0 batch context for commit table.

### §1.3 Binding-chain stage verification (per batch-16 §6 sharpening)

| Stage | Required evidence | Verified at | Verification shape |
|---|---|---|---|
| 1. Carrier landed | `MCPInvocationFailClass` enum + projection function importable from `harness_as` | `54b992d` | 10 carrier unit tests + 7 import-shape tests at `test_mcp_invocation_fail_class.py` (PASS at HEAD) |
| 2. Producer span site | `runtime_tool_dispatcher.py` opens `sandbox.violation` child span on exception path with both attrs | `c3545b6` | `_emit_sandbox_violation(tracer, mcp_fail_class)` helper at dispatcher class body; invoked at 4 except-branches replacing v1.13 dead-code string-assignment pattern |
| 3. E2E exercise PASS | 4 MCP-protocol exception paths + 1 happy-path regression guard traverse the full dispatch chain through real fastmcp + OTel exporter | `c3545b6` | 5 e2e tests at `test_lifecycle_runtime_tool_dispatcher.py:484-666` open real `TracerProvider` + `InMemorySpanExporter`; assert span-name `"sandbox.violation"` present and dual-attribute values byte-exact per §15.8 / §15.10 |

All 3 stages empirically MET per [[verification-shape-sharpened-grep-vs-e2e]] discipline at batch-16 §6 sharpening. Verification went beyond grep-for-presence — the e2e tests invoke the production `RuntimeToolDispatcher.dispatch()` method against a real fastmcp echo server with controllable failure injection, then read back the emitted spans from `InMemorySpanExporter.get_finished_spans()` and assert the `sandbox.violation` span name + the attributes on the span object.

### §1.4 Cross-axis cascade verification

Per AS plan v1.4 §3 + AS spec v1.6 change-note §"Adjacent defects surfaced": ZERO cross-axis cascade at retirement-event semantics. 3 deferred cascades surfaced + NOT patched per FM-2:

- (a) AS spec §15.10 row 3 HIGH semantic stretch flagged in spec itself; future ADR-D2 / F4 enum revision MAY add a `contract_violation` value to absorb cleanly.
- (b) OD §C-OD-04/05/06 `sandbox.*` ingestion path for the dual-attribute `sandbox.violation` event undocumented at OD spec v1.11 (the `mcp.fail.class` cross-namespace co-emission discipline is a new event surface).
- (c) CXA v2.10 §2.3 AS↔OD edge enumeration unchanged — whether the cross-namespace co-emission warrants a NEW edge declaration at §2.3.6 is open at follow-on CXA revision arc.

None of these adjacent cascades gate the retirement transition. The retirement is for the production-binding-chain criterion B, not for downstream OD ingestion completeness.

### §1.5 Sibling row impact

| Row | Status (post batch-18) | Status (post batch-19) | Reason |
|---|---|---|---|
| H_T-AS-1 | RETIRED | RETIRED | Unchanged |
| H_T-AS-2 | RETIRED | RETIRED | Unchanged |
| H_T-AS-4 | **PARTIAL** | **RETIRED** | **This batch — Reading B arc close** |
| H_T-AS-5 | STILL-BOUNDED | STILL-BOUNDED | Unchanged — gates on production tool-dispatch invoking `sandbox_event_idempotency` composition (independent gate from AS-4 sandbox.violation span emission) |
| H_T-AS-8 | PARTIAL | PARTIAL | Unchanged — gates on remaining `anthropic.*` attrs + cross-namespace consumer-side wiring (independent gate) |
| H_T-AS-9 | RETIRED (authoring) | RETIRED | Unchanged |

**AS-axis cumulative post-batch-19: 4 / 6 RETIRED (66.7%, +1 from batch-18) + 1 / 6 PARTIAL (16.7%, AS-8) + 1 / 6 STILL-BOUNDED (16.7%, AS-5). Pipeline advanced (R+RR+P): 5/6 = 83.3% (unchanged from post-batch-18; within-tier promotion AS-4 PARTIAL → RETIRED).** AS-axis exits the at-most-3-RETIRED plateau held since batch-2 (AS-1 baseline) + batch-16 (joint AS-2 with CP-18) + batch-2 (AS-9 authoring close).

---

## §2 Operator-opt-in RETIRE-READY pattern (post-batch-19)

Pattern members across batches 10–19: 6 historical members (CP-16, CP-18, AS-2, CP-21, CP-22, AS-4); **all RETIRED**. **Operator-opt-in RETIRE-READY bucket EMPTY post-batch-19** (same as post-batch-18 + post-batch-17; transient 0 → 1 → 0 within-batch promotions at batches 17/18/19 confirm the close pattern).

Future PARTIAL → RETIRE-READY promotions under this pattern (for the 7 remaining PARTIALs at this batch: AS-8 + CP-8 + CP-9 + CP-11 + CP-14 + CP-17 + CP-19, plus the 2 OD-axis PARTIALs at OD-X if applicable) must apply the batch-16 §6 verification-shape sharpening: all 3 binding-chain stages must be empirically verified before promotion. This batch is the **second consecutive within-batch PARTIAL → RETIRED transit** (batch-18 H_T-CP-22 was the first); the pattern is now well-established for spec-amendment + impl-arc + e2e-verification closure shape.

---

## §3 Adjacent observations

(a) **`sandbox.cost.tier_overhead_usd` 7th attribute not emitted at production.** Per AS spec C-AS-15 §15.2 the 7-attribute schema enumerates `sandbox.tier` / `sandbox.tech` / `sandbox.provider` / `sandbox.policy.assigned_tier_reason` / `sandbox.cost.tier_overhead_ms` / `sandbox.cost.tier_overhead_usd` / `sandbox.fail.class` — 7 rows. Production dispatcher emits 5 of these on `sandbox.enter` + 1 on `sandbox.violation` post-batch-19. `sandbox.cost.tier_overhead_usd` is still NOT emitted at production. The PARTIAL row text "6 of 7 sandbox.* attrs declared" at batch-11 framing conflated "attribute declared at constant" with "attribute emitted at production span site"; `sandbox.cost.tier_overhead_usd` is in neither. The AS-4 retirement gate framing at the PARTIAL row was specifically about the `sandbox.violation` span emission absence (the operational gap per [[verification-shape-sharpened-grep-vs-e2e]] discipline) which is now MET. The `sandbox.cost.tier_overhead_usd` gap is a separate concern (cost-attribution-aware sandbox decision resolver) tracked at AS plan §0.7 carry-forwards + operator-discretion follow-on arc per FM-2 no-extension discipline at this batch.

(b) **Class 3 drift owed at harness-as/CLAUDE.md §4.1 AS-4 row.** The PARTIAL row text references `runtime_tool_dispatcher.py:179-184` line numbers + the `:414` "sandbox.violation deferred" comment. Both line ranges drift at HEAD `c3545b6` (the file is now 530 lines; `ATTR_MCP_FAIL_CLASS` was added at line 185; `_emit_sandbox_violation` helper at lines 270-291; old `:414` deferral comment removed). Filed as Class 3 documentation-drift at the bookkeeping commit per FM-2 — NOT patched in retirement-event scope; the PARTIAL row itself is being replaced with the RETIRED row in this batch's co-published bookkeeping commit at workspace `CLAUDE.md` + `harness-as/CLAUDE.md`.

(c) **ZERO ledger v2 §6 row update.** Ledger v2 §6 row 79 still lists H_T-AS-4 as STILL-BOUNDED (the pre-batch-11 baseline). The batch-11 doc-hygiene transition PARTIAL framing lives at `harness-as/CLAUDE.md` §4.1 + batch-11/12/13/16 ledger tables, NOT at the v2 ledger row 79. This batch follows the same posture as batches 11/12/13/16 — does NOT modify ledger v2 §6 (frozen at canonical-baseline framing); promotes the row via the cumulative-batch-table state machine. NOT patched per FM-2 — the v2 ledger §6 row drift is a separate scope tracked at ledger v2 maintenance arcs.

(d) **Adversarial review not run.** This batch lands the retirement event in single-session arc 2 close per `[[halt-route-split-AC-pattern]]` precedent (arc-1-spec at last session, arc-2-impl+retirement at this session). Adversarial review pass against AS plan v1.4 + impl arc deferred to operator-discretion follow-on arc; the 5 e2e tests + 17 carrier unit tests + 1069/1069 runtime test suite green + 317/317 harness-as test suite green provide the empirical-verification surface.

---

## §4 Filing footer

| Field | Value |
|---|---|
| Batch | 19 |
| Cumulative RETIRED | 28/49 (57.1%) |
| Cumulative pipeline-advanced | 35/49 (71.4%) |
| New RETIRED transitions | 1 (H_T-AS-4) |
| Filed as | `phase-7d-retirement-events-batch-19.md` |
| Co-published bookkeeping | Workspace `CLAUDE.md` §2.3 AS spec row (v1.5 → v1.6 already absorbed at last session) + §2.4 AS plan row (v1.2 → v1.4 — two-version bump absorbing prior v1.3 documentary annotation pass + this arc's v1.4 substantive amendment) + `harness-as/CLAUDE.md` §1.2 spec/plan version cite update + §4.1 H_T-AS-4 row PARTIAL → RETIRED transition + fork doc `class_1_fork_as_4_f4_enum_taxonomy_mismatch_and_production_bug.md` §8 OPEN → READING-B-APPLIED close block |
| Predecessor | `phase-7d-retirement-events-batch-18.md` |
| Date | 2026-05-26 |
