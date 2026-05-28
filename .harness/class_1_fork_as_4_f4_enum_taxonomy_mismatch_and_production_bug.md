# Class 1 Fork — AS-4 F4 enum taxonomy mismatch + production bug at runtime_tool_dispatcher.py

**Filed:** 2026-05-25 (H_T-AS-4 retirement arc scope-discriminator pass)
**Status:** ✅ APPLIED 2026-05-26 (status-line refreshed 2026-05-27) — Reading B arc 2 landed: AS spec v1.6 → v1.7 §15.8 `MCPInvocationFailClass` 4-value StrEnum + §15.9 dual-attribute `mcp.fail.class` emission + §15.10 projection table; AS plan v1.3 → v1.4 U-AS-03 + U-AS-17 absorption; harness-as carrier impl + harness-runtime dispatcher bug fix at `runtime_tool_dispatcher.py:395-412` + 17+5 new tests; retirement batch-19 H_T-AS-4 PARTIAL → RETIRED. Species 3 stale-carry per workflow v1.9 §7.4.7.2.

_Original filing footer:_ **Status:** OPEN — Class 1 (halt-execution); routes to design-phase back-flow before AS-4 impl proceeds
**Halt target:** H_T-AS-4 retirement arc (PARTIAL since batch-13; sweep claimed "1-attr gap on sandbox.violation"; discriminator audit revealed the gap is structural, not 1-attr)
**Routing target:** AS spec v1.5 → v1.6 amendment (F4 enum extension OR MCP-protocol-layer fail-class taxonomy addition) — operator routing decision required at systems-architect Mode 3 recommendation
**Detection mode:** Discriminator audit per `[[verification-shape-sharpened-grep-vs-e2e]]` + advisor-flagged bug investigation at runtime_tool_dispatcher.py:380-420

---

## §1 — Empirical-verification details

### §1.1 Spec-side claims (AS spec v1.5 §15 + §4.1)

**§4.1 F4 fail-class enum (7 values, verbatim from `harness-as/src/harness_as/sandbox_fail_class.py`):**

```python
class SandboxFailClass(StrEnum):
    ESCAPE_ATTEMPT = "escape_attempt"
    EGRESS_DENIED = "egress_denied"
    TIMEOUT = "timeout"
    OOM = "oom"
    SIGNAL = "signal"
    EXIT_NONZERO = "exit_nonzero"
    POLICY_OVERRIDE = "policy_override"
```

Shape: **process-execution failure taxonomy** — fits a sandboxed-process model (escape attempts, OOM kills, signal interrupts, non-zero exit codes, policy violations).

**§15.1 span hierarchy:**

```
subagent.span[i]
├── sandbox.enter         (attrs: tier/tech/provider/policy.assigned_tier_reason/...)
├── tool.call[]
├── sandbox.violation      (attrs: sandbox.fail.class ∈ §15.5 enum; details per fail class)
├── sandbox.tier_escalation
└── sandbox.exit
```

`sandbox.violation` is a **child span** (sibling to `tool.call`/`sandbox.tier_escalation`/`sandbox.exit` under `sandbox.enter`), not a span event on the parent. Opened via `start_as_current_span("sandbox.violation")`.

**U-AS-17 AC #1 (Implementation_Plan_Action_Surface_v1.md line 893):**

> Span hierarchy matches §15.1 verbatim: `subagent.span[i] → sandbox.enter → tool.call[] / sandbox.violation / sandbox.tier_escalation / sandbox.exit`.

**U-AS-17 AC #3 (line 895):**

> `sandbox.enter` carries 10 attributes (...); `sandbox.violation` carries 1+; `sandbox.tier_escalation` carries 3 (...); `sandbox.exit` carries 5.

**U-AS-18 AC #6 (line 943):**

> `tail-keep-on-classification=true` for `sandbox.violation` per §15.4 row 3.

### §1.2 Empirical reality (HEAD `b245159`)

**Production code at `harness-runtime/src/harness_runtime/lifecycle/runtime_tool_dispatcher.py:395-412`:**

```python
# Lines 395-401: Transport/protocol/health errors
except (
    ToolInvocationTimeoutError,
    ToolInvocationProtocolError,
    MCPHostUnreachableError,
):
    sandbox_fail_class = "transport"    # ← NOT IN F4 ENUM
    raise

# Lines 406-412: Schema validation error
except jsonschema.ValidationError as exc:
    sandbox_fail_class = "schema-violation"    # ← NOT IN F4 ENUM
    raise ToolInvocationSchemaViolationError(...)
```

**Defect (i) — invented strings.** Both `"transport"` and `"schema-violation"` are NOT in the canonical `SandboxFailClass` StrEnum. The production code assigns invented values that fail the §4.1 contract. Silent absorption of a F4-enum-not-fit-for-purpose into production strings is precisely the X-AL-3 "silent H_T design extension at Phase 7" anti-pattern.

**Defect (ii) — sandbox.violation child span never opened.** Line 414 comment: `# --- Step 9-10: sandbox.exit span (sandbox.violation deferred) --`. The child span emission per §15.1 hierarchy + U-AS-17 AC #1 has no production callsite. The 6/7 sandbox.* attrs that DO emit do so at `sandbox.enter` + `sandbox.exit` only; `sandbox.violation` span itself is absent.

**Defect (iii) — production exception types are MCP-protocol-shaped.** The exception types caught in production are MCP-protocol-layer concerns:

| Production exception | Semantic | F4 enum candidate(s) |
|---|---|---|
| `ToolInvocationTimeoutError` | MCP call exceeded timeout | `timeout` — natural fit |
| `ToolInvocationProtocolError` | MCP protocol-layer error (malformed response, etc.) | ?? — no protocol value; closest: `exit_nonzero` (but semantic stretch) |
| `MCPHostUnreachableError` | MCP server process unreachable | ?? — no transport/network value; closest: `exit_nonzero` (but semantic stretch) |
| `jsonschema.ValidationError` | Tool I/O schema mismatch | ?? — no schema-violation value; closest: `policy_override` (but semantic stretch) or `exit_nonzero` |
| `SandboxTierFloorViolationError` | Sandbox tier < contract minimum | ?? — no tier-floor value; closest: `policy_override` (best semantic fit per spec §11.5 row 3 cite at U-AS-09 AC #7) |

Only `ToolInvocationTimeoutError → timeout` has a clean 1:1 mapping. The other four production exceptions force operator-judgment coercion into F4 enum values that don't fit semantically.

---

## §2 — The structural question

The F4 enum at spec §4.1 was authored against a **sandboxed-process model** (escape/egress/oom/signal/exit_nonzero — process execution failure modes). The production runtime catches **MCP-protocol-layer** exceptions (timeout/protocol/unreachable/schema). The two taxonomy shapes don't compose cleanly:

- Process-shape: what FAILED during sandboxed execution (the process did X)
- MCP-shape: what FAILED at the MCP boundary (the protocol exchange did Y)

These are at different abstraction layers. A sandbox.violation event should carry BOTH:
- The MCP-layer cause (which protocol-shape exception fired)
- The process-layer manifestation (which F4-shape behavior the violation represents)

But §15 + §4.1 currently mandate only the latter, and the former has no enum carrier.

Per X-AL-3 (Meta-Architecture §7.7): no silent H_T design extension at Phase 7. The production code at line 400 + 407 silently absorbed this gap by inventing `"transport"` and `"schema-violation"` strings. That silent absorption is the X-AL-3 violation surfaced by this fork.

---

## §3 — Routing options

### §3.1 Reading A — Extend F4 enum to MCP-protocol-shape (additive at §4.1)

Amend AS spec v1.5 → v1.6:
- Add NEW §4.1 F4 enum values: `transport`, `schema_violation`, `protocol_error`, `tier_floor_violation` (or a subset)
- Update §15.5 routing posture table to enumerate the new values
- U-AS-03 carrier update: `SandboxFailClass` StrEnum gains new members
- U-AS-17 AC #3 / U-AS-18 AC #6 carrier-cite-cascade updates

**Scope:** ~5-8 commits (spec amendment + plan revision + carrier extension + impl mapping fix + violation span emission + tests + retirement batch). Multi-axis (AS-spec + AS-plan + harness-as + harness-runtime).

**Pros:** Preserves the production exception types and their semantic mapping (1:1 add); minimal cascade.
**Cons:** F4 enum doubles in cardinality + mixes process-shape with MCP-shape values; semantic coherence degrades. ADR-D5 / D2 may have downstream cite implications.

### §3.2 Reading B — Author a NEW MCP-protocol-layer fail-class taxonomy at §15 (sibling to F4)

Amend AS spec v1.5 → v1.6:
- NEW §15.X sub-section authoring `MCPInvocationFailClass` StrEnum at AS-axis (4-5 values: `transport`, `schema_violation`, `protocol_error`, `tier_floor_violation`, `host_unreachable`)
- `sandbox.violation` child span carries BOTH `sandbox.fail.class` (F4) AND new `mcp.fail.class` attribute
- Optional: §15.6 mapping table from MCP-shape to F4-shape (best-effort projection where applicable)
- U-AS-17 AC #3 update: violation span carries 2+ attrs (was 1+)

**Scope:** ~6-10 commits (richer spec amendment + dual-taxonomy carriers + dual-attribute emission + mapping logic + tests + retirement batch).

**Pros:** Preserves F4 enum semantic coherence (process-shape only); adds MCP-shape at proper abstraction layer; matches production exception types 1:1 in the new taxonomy.
**Cons:** Larger arc; introduces second taxonomy that some readers may conflate with F4; mapping table at §15.6 owes future revisions.

### §3.3 Reading C — Force-coerce production exceptions into F4 enum (no spec amendment)

Treat the production bug as a value-mapping error only:
- `ToolInvocationTimeoutError → timeout` (clean)
- `ToolInvocationProtocolError → exit_nonzero` (semantic stretch; "the protocol exchange exited with non-zero status")
- `MCPHostUnreachableError → exit_nonzero` (same stretch)
- `jsonschema.ValidationError → policy_override` (semantic stretch; "the I/O schema enforcement is a policy")
- `SandboxTierFloorViolationError → policy_override` (already implied at U-AS-09 AC #7)

**Scope:** ~2-4 commits (mapping fix in dispatcher + violation span emission + tests + retirement batch). Single-axis (harness-runtime only).

**Pros:** Cheapest; no spec amendment; preserves F4 enum verbatim.
**Cons:** Silent design choice on what stretched semantics mean; future readers face the same X-AL-3 trap. Class 3 informational drift owed at minimum documenting the coercion convention. **Operator-discretion absorption of the X-AL-3 violation** — explicitly choosing the silent extension route, no longer silent because it's documented in a Class 3 drift.

### §3.4 Reading D — Defer AS-4 retirement entirely (carry-forward)

Acknowledge that AS-4 is structurally blocked at F4 enum + MCP-protocol-layer asymmetry; pin AS-4 PARTIAL indefinitely; route to future Phase 8 or design-phase v2 revision.

**Scope:** 1 commit (fork-doc close-as-deferred + AS-4 status row update at harness-as/CLAUDE.md).

**Pros:** No code change; no spec change; preserves the gap as documented future work.
**Cons:** AS-4 retirement never closes; CXA cascade implications (AS-4 doesn't gate CXA-5 per earlier orientation but may have other downstream effects); workspace retirement count plateau.

---

## §4 — Recommendation (sized for systems-architect Mode 3 input)

Reading B (NEW MCP-protocol-layer taxonomy at §15) is the **architecturally cleanest** — preserves F4 enum semantic coherence + adds the MCP-shape concern at its proper abstraction layer + matches production exception types 1:1.

Reading A (F4 enum extension) is the **path-of-least-resistance** but degrades semantic coherence by mixing two abstraction layers in one enum.

Reading C (force-coerce) is the **highest-X-AL-3-risk** route — it absorbs the silent extension formally but doesn't fix the structural taxonomy gap. Future production sites will face the same coercion temptation.

Reading D (defer) is the **lowest-progress** option but the safest given operator time constraints.

**Per X-AL-3 + operator-ratified preferences in prior arcs:** Reading B should be preferred when:
- Spec coherence is operator-priority (per `[[fork-meta-arch-cp-spec-renumbering-drift]]` + `[[fork-cp-spec-section-25-contract-id-collision]]` resolution patterns favoring spec-side fidelity)
- Multi-axis cascade impact is acceptable (AS spec + AS plan + harness-as carrier + harness-runtime impl)

Reading C should be preferred when:
- Operator time horizon is short (single-session close)
- AS-4 retirement count is operator-priority over taxonomy-cleanliness
- Future spec-revision pass can absorb the mapping convention later

This fork doc does NOT pick. Operator decides at AskUserQuestion; systems-architect can Mode 3 recommend.

---

## §5 — Cross-axis cascade analysis

Per Meta-Arch §2.3: H_T-AS-4 is "AS-internal" posture — does NOT gate any CXA-* row. H_T-CP-12 (Sandbox-tier dispatch, AS consumer) is already RETIRED per prior batches; AS-4 retirement does not unblock additional cascade.

OD-axis: `sandbox.*` namespace consumption is at H_T-OD-2 (already RETIRED at batch-2) + H_T-CXA-1 (AS→IS substrate; PARTIAL). Reading A/B amendments would add new sandbox.* attribute names; this triggers OD spec §C-OD-05 namespace-ingestion-map review per U-OD-05 AC. Whether this is cite-only or carrier-extension depends on Reading choice.

**ZERO new cross-axis edge.** **ZERO new CXA-row dependency.**

---

## §6 — Adjacent findings (NOT this fork's primary scope)

(a) **Sweep "1-attr gap" framing was incorrect.** The batch-18-sweep claim of "AS-4 = 1-attr gap on sandbox.violation, tool-dispatch path live since L9-sexies" missed (i) the child-span emission absence (not just attribute), (ii) the production bug at line 400 + 407, (iii) the F4 enum/MCP exception taxonomy mismatch. Future PARTIAL-row sweeps should include this 4th-check pattern per `[[stale-grep-partial-re-audit-pattern]]` (memory entry owed): verify production binding chain at the EXCEPTION HANDLER level, not just span emission level.

(b) **`SandboxTierFloorViolationError` raise site (line 330) is a SEPARATE concern.** This exception fires before any sandbox.* span opens; the violation must be captured BEFORE the dispatcher's exception handler at line 395-412 can run. The current code re-raises after setting `sandbox_fail_class` — but the raise re-propagates upward without the violation span ever opening. This is a Reading-independent structural concern: regardless of which F4 mapping is chosen, the violation child span must open in the exception path, not at sandbox.exit. Worth confirming the U-AS-17 AC #1 hierarchy reading allows violation-span-during-exception-unwinding (it should — child spans can open and close even on exception paths per OTel semantics).

(c) **harness-as/CLAUDE.md AS-4 row** (line 167 per earlier explorer cite) refers to "6 of 7 attrs declared + 7th `sandbox.violation` deferred per `runtime_tool_dispatcher.py:414` comment". This row also frames AS-4 as a 1-attr gap. Row update owed at fork resolution.

---

## §7 — Filing footer

| Field | Value |
|---|---|
| Class | 1 (halt-execution) |
| Filed at | 2026-05-25 |
| HEAD at filing | `b245159` (worktree clean post OD-2 cleanup commit) |
| Halt target | H_T-AS-4 retirement arc (PARTIAL → RETIRED transition blocked until back-flow resolves) |
| Routing target | AS spec v1.5 → v1.6 amendment per operator-ratified Reading (A / B / C / D) |
| Authority chain | ADR-D2 v1.2 (sandbox tier) → ADR-D5 v1.4 (5-axis gate-level composition) → AS spec v1.5 §4.1 F4 enum + §15 sandbox.* namespace → U-AS-03 + U-AS-16 + U-AS-17 + U-AS-18 carrier units → harness-runtime dispatcher production binding |
| Blocks | H_T-AS-4 retirement; no other rows |
| Cross-axis cascade | ZERO at semantics layer; potential cite cascade at OD §C-OD-05 namespace-ingestion-map depending on Reading choice |
| Memory anchors | `[[verification-shape-sharpened-grep-vs-e2e]]` (4th-check discriminator extension caught this fork at scope-commit gate); `[[fork-meta-arch-section-2-2-as-axis-carrier-phantom-cites]]` (parallel AS-axis carrier-cite drift pattern at spec layer); `[[fork-meta-arch-cp-spec-renumbering-drift]]` (sibling spec-coherence-fidelity pattern); `[[stale-grep-partial-re-audit-pattern]]` (owed memory entry — sweep framing missed this fork) |
| Related forks | None — fresh fork at fresh defect surface |
| Status at filing | OPEN — awaiting operator AskUserQuestion routing OR systems-architect Mode 3 recommendation arc |

---

## §8 — Closure block (Reading B arc 1 LANDED — spec amendment 2026-05-25)

### §8.1 Operator routing decision

AskUserQuestion 2026-05-25 ratified **Reading B** ("NEW MCP-protocol-layer fail-class taxonomy at §15 (sibling to F4)") per fork §3.2 — operator deferred to recommendation per fork §4 (architecturally cleanest; preserves F4 enum semantic coherence; matches production exception types 1:1 at MCP-protocol abstraction layer).

### §8.2 Arc 1 deliverable — AS spec v1.5 → v1.6 amendment (LANDED)

AS spec amendment authored at commit pending this session. Site-by-site delta:

| Site | Amendment | Status |
|---|---|---|
| Title | "Spec — Action Surface v1.5" → "Spec — Action Surface v1.6" | ✓ LANDED |
| Change-note (v1.5 → v1.6) | NEW change-note section authored at top (Trigger / Scope / Site table / Sections preserved / Status posture / Downstream absorption owed / Adjacent defects surfaced) | ✓ LANDED |
| Status block | NEW Revision row v1.5 → v1.6 (2026-05-25) | ✓ LANDED |
| C-AS-15 §15.8 | NEW `MCPInvocationFailClass` 4-value StrEnum (`transport` / `protocol_error` / `schema_violation` / `timeout`) + per-class semantic + C5/C9 routing posture + authority anchors + composition with F4 | ✓ LANDED |
| C-AS-15 §15.9 | NEW `mcp.fail.class` attribute on `sandbox.violation` child span + dual-attribute emission discipline matrix + cross-axis composition + sensitive-data discipline + authority anchors | ✓ LANDED |
| C-AS-15 §15.10 | NEW best-effort projection table MCP-shape → F4-shape + per-row semantic-stretch acknowledgement + implementation discretion + authority anchors | ✓ LANDED |
| §4.1 F4 enum | PRESERVED VERBATIM | ✓ |
| §15.1..§15.7 | PRESERVED VERBATIM | ✓ |
| Workspace CLAUDE.md §2.3 AS row | v1.5 → v1.6 (preserved tail history v1.5..v1.3) | ✓ LANDED |

### §8.3 Arc 2 deliverables (PENDING, fresh worktree recommended)

Per fork §7 change-note item (b): two-arc resolution pattern from `[[fork-cp-spec-section-25-contract-id-collision]]` — arc 2 = plan + impl + retirement bundle at fresh worktree per FM-4 risk-aware scoping.

| Deliverable | Routing | Estimated scope |
|---|---|---|
| (1) AS plan v1.2 → v1.3 | implementation-planner revision-pass per §C-AS-15 §15.8/§15.9/§15.10 absorption | U-AS-17 + U-AS-18 AC bodies absorb dual-attribute emission; potential NEW carrier-unit for MCPInvocationFailClass OR extend U-AS-03 fail-class enum carrier; cite-cascade refresh at U-AS-15..18 unit anchors |
| (2) harness-as impl | NEW `mcp_invocation_fail_class.py` (or extend `sandbox_fail_class.py`) StrEnum carrier per §15.8 | 1 module + 1 test file |
| (3) harness-runtime impl | Fix dispatcher line 400 + 407 invented strings + open `sandbox.violation` child span per §15.1 hierarchy + emit dual fail-class attrs per §15.9 + projection-table application per §15.10 (option a recommended default) | runtime_tool_dispatcher.py changes + 4-5 new tests + existing test updates |
| (4) Retirement batch-20 | `phase-7-substitution-retirement` skill — H_T-AS-4 PARTIAL → RETIRED close per Reading B resolution path | 1 batch event file; AS-axis 3/5 → 4/5 (60% → 80%) |
| (5) Fork doc §8.X closure | Update this §8 with arc 2 close evidence + final status: OPEN → READING-B-APPLIED | This file edit |

Estimated arc 2 cycle cost: ~5-8 commits multi-axis, 1-2 sessions.

### §8.4 Status

| Field | Value |
|---|---|
| Fork status | OPEN → READING-B-ARC-1-LANDED → **READING-B-APPLIED** (arc 2 close at 2026-05-26) |
| HEAD at arc 1 close | `bb2474d` — AS spec v1.5 → v1.6 + workspace CLAUDE.md row bump + §8 closure block (2026-05-25) |
| HEAD at arc 2 close | Commit pending this session — AS plan v1.3 → v1.4 (`54b992d`) + harness-runtime dispatcher fix + 5 e2e tests (`c3545b6`) + retirement batch-19 + workspace + harness-as/CLAUDE.md row bumps + this §8 closure update |
| Cross-axis cascade | ZERO at semantics layer; 3 deferred cascades (OD §C-OD-04/05/06 dual-attr ingestion + CXA v2.10 §2.3.6 edge enumeration + ADR-D2 §1.7.X future-arc projection ratification) surfaced at AS plan v1.4 §3 NOT patched per FM-2 no-extension discipline |

### §8.5 Arc 2 close evidence (2026-05-26)

| Deliverable | Commit | Evidence |
|---|---|---|
| (1) AS plan v1.3 → v1.4 | `54b992d` | Delta-only plan file at `design-substrate/Implementation_Plan_Action_Surface_v1_4.md`; two single-unit-body amendments (U-AS-03 carrier-extension + U-AS-17 AC #3 text-replace + ACs #9/#10); ZERO new units; ZERO DAG change |
| (2) harness-as impl | `54b992d` | `MCPInvocationFailClass` 4-value StrEnum + `project_mcp_to_sandbox_fail_class` projection function + `__all__` exports at `sandbox_fail_class.py`; `SANDBOX_VIOLATION_ATTRIBUTES` extended at `sandbox_span_schema.py`; `MCP_INVOCATION_ATTRIBUTE_SCHEMA` sibling tuple at `sandbox_attribute_schema.py`; 17 new unit tests; pyright strict 0 errors at carrier modules; 317/317 harness-as tests PASS |
| (3) harness-runtime impl | `c3545b6` | Bug fix at `runtime_tool_dispatcher.py:395-412` (invented-string dead-code REPLACED with isinstance dispatch mapping each MCP-protocol exception to MCPInvocationFailClass); NEW `_emit_sandbox_violation` helper opens `sandbox.violation` child span on exception path with dual fail-class attrs per §15.9 + §15.10; 5 new e2e tests against real fastmcp echo fixture (4 exception paths + happy-path no-violation regression guard); 1069/1069 runtime tests PASS; pyright src-side neutral |
| (4) Retirement batch-19 | pending this session | `phase-7d-retirement-events-batch-19.md` filed; H_T-AS-4 PARTIAL → RETIRED close per Reading B resolution path; cumulative 27/49 → 28/49 RETIRED (57.1%); AS-axis 3/6 → 4/6 (66.7%) |
| (5) Fork doc §8 closure | this edit | OPEN → READING-B-ARC-1-LANDED → READING-B-APPLIED |

**Fork CLOSED-APPLIED 2026-05-26.**
