# Residual closure: Richer `pause_context_reader` body — CLOSED-as-WON'T-FIX (2026-05-24)

**Surface.** Runtime spec v1.21 §14.14.7 deferred-discretion clause — "`pause_context_reader` composition body. v1.21 specifies the callable signature + the factory invocation site composition discipline (§14.14.2 invariant 4). The specific composition shape (closure-over-ctx vs partial-application vs class-bound-method on a stage-5 helper class) is implementation discretion at the C-RT-24 landing arc."

**Current state at HEAD `fc34ec7`.** `_make_default_pause_context_reader(ctx)` at `harness-runtime/src/harness_runtime/bootstrap/factories/pause_resume_protocol_factory.py:64-102` returns a minimal placeholder: empty `StateSummary` (zero `relevant_entries`, empty `summary_text`, `"0"*64` summary_hash, empty idempotency_key, no external_references) + constant anchor sentinel `"0"*64`. Operator-supplied `pause_context_reader` override at factory keyword-arg is honored; default is the MVP placeholder.

**Trigger.** Checkpoint `20260524-094950-session-close-4-items-defer-item-2.md` remaining-work item #3 ("Richer `pause_context_reader` body ~3-5 commits with LedgerReader extension"). Arc opened 2026-05-24 per operator selection on the remaining-work menu at `/checkpoint resume`.

**Operator decision (AskUserQuestion 2026-05-24).** Operator selected "Close as WON'T-FIX (mirror fork §11)" from a 4-option menu (Close-as-WON'T-FIX / Defer-until-consumer-surfaces / Open-Class-1-fork / Author-MVP-PLUS-anchor-only). The arc is closed-as-won't-fix at this scope, recoverable if a concrete consumer surfaces.

## Pre-decision orientation (advisor-driven)

Per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` discipline (13th application this project), advisor surfaced three discriminating questions before any authoring:

### (1) Concrete consumer of richer data

**None named.** Empirical grep across production source (excluding tests):

- `capture_pause_snapshot` is invoked at exactly one production callsite: `harness-cp/src/harness_cp/workflow_driver.py:681` (U-RT-89 landing). The callsite is reachable only when `ctx.pause_resume_protocol is not None and ctx.pause_requested_flag.is_set()`.
- Per `[[fork-u-cp-72-cost-and-pause-resume-prefix-gap]]` §11 won't-fix closure, no production code path sets `pause_requested_flag`. The callsite is structurally present but practically dormant in production.
- No production assertion on `snapshot.state_summary` content or `snapshot.state_ledger_anchor` content. The sole production-shape assertion at `harness-runtime/tests/integration/test_u_rt_89_pause_resume_e2e.py:217` is `assert len(snapshot.state_ledger_anchor) == 64` — shape, not content.
- Protocol-class unit tests at `harness-cp/tests/test_pause_resume_protocol_class.py:198,239,240,282,283` and `test_pause_resume_protocol_spans.py:127,356` assert on specific anchor values (`"c"*64`, `"f"*64`, etc.) — but these tests inject their own non-trivial `pause_context_reader` fixtures. They test the `PauseResumeProtocol` class with controlled inputs; they do NOT test the factory's default reader.

Richer data from the factory's default reader has no current downstream consumer that would fail against the MVP placeholder.

### (2) Signature foreclosure — closed at CP spec v1.13 §26.3

**`PauseContextReader = Callable[[], tuple[StateSummary, str]]` is locked at zero args** per `harness-cp/src/harness_cp/pause_resume_protocol.py:195`. The driver's per-step accumulated state (`accumulated: dict[str, Any]` at `workflow_driver.py:551`) has no channel to the reader at capture-time except via:

| Option | Cost | Shape |
|---|---|---|
| (a) Closure over a mutable cell that the driver writes each step | Hidden coupling between `workflow_driver` and the reader; works only if driver writes to the cell at every step | Possible without spec change |
| (b) Widen `PauseContextReader` signature to take state | CP spec v1.13 §26.3 amendment + PauseResumeProtocol constructor-ref discipline change | **Class 1 back-flow** per X-AL-3 |
| (c) Ledger-head read via new IS `read_latest` primitive | IS spec extension (new `LedgerReader.read_latest()` surface beyond current `read_by_idempotency_key` at `state_ledger.py:156`) | Reader reads ledger-state, NOT driver-accumulated state — different data shape |

Critically: **(a) vs (c) is an architectural call, not implementation discretion**. (a) reads driver-tracked accumulated dict-state; (c) reads ledger-head entry_hash. These are not the same data. The spec §14.14.7 narrative — "follow-on arc when the workflow_driver supplies the per-step accumulated state to the reader at capture-time" — assumes (a); but no consumer requires the driver-state semantics over the ledger-state semantics. Settling (a) vs (c) requires a named consumer to discriminate. None exists.

### (3) FM-2 risk pattern recurrence

Authoring richer reader semantics against an architectural principle (snapshot-completeness) rather than a named consumer surface matches the FM-2 violation pattern surfaced at fork §11 (#1 won't-fix). H_T-CP-22 is already RETIRED at batch-18 — no retirement gate. No failing test cites missing reader richness. No compliance shape cites snapshot content semantics. The "richer body" is speculative authoring.

## Rationale for won't-fix

With (1) no concrete consumer + (2) signature foreclosure forcing an architectural commitment that no consumer can discriminate + (3) FM-2 risk pattern recurrence, opening a 3-5 commit arc would be:

- Authoring against an architectural principle (snapshot-completeness) rather than a named consumer → FM-2 violation pattern (no-extension discipline applies to spec extensions authored ahead of consumer demand)
- Committing to (a) vs (c) without evidence to discriminate the two — locking in an architectural choice on speculation
- Adding code-and-test surface area against a feature surface (`PauseContextReader` default composition) that is structurally MET at the binding-chain level (factory landing + U-RT-89 e2e PASS against MVP placeholder)

## Recovery path if a concrete consumer surfaces

If a downstream consumer is named later, this closure can be reopened. Shape options preserved for future reference:

### Option (a) — closure-over-mutable-cell (driver-state semantics)

| Surface | Change |
|---|---|
| Factory body | Compose a mutable cell (e.g., `_DriverStateCell` holding `dict[str, Any]`) at stage-5 LOOP_INIT module |
| Factory reader closure | Read from the cell at invocation; serialize `accumulated` → `StateSummary` |
| Driver | Write to the cell at every per-step pre-entry before pause-trigger detection |
| Spec | NEW §14.14.2 invariant documenting the cell-write contract; no signature change |
| Test | Driver-cell-write coverage at U-RT-89 e2e shape |

Estimated 2-3 commits, single-axis (runtime). Hidden coupling cost: any future driver refactor must preserve the cell-write contract.

### Option (b) — widen `PauseContextReader` signature (Class 1 back-flow)

| Surface | Change |
|---|---|
| CP spec v1.13 §26.3 | Amend `PauseContextReader` signature to `Callable[[StateSummary | None], tuple[StateSummary, str]]` (or similar) |
| `PauseResumeProtocol.capture_pause_snapshot` | Pass current driver state to reader at capture-time |
| Runtime spec §14.14 | Amend constructor-ref discipline + invariants |
| Plan | U-CP-63 / U-CP-64 / U-RT-88 revisions |
| Impl | Factory + driver + protocol-class + tests |

Estimated 5-8 commits, multi-axis (CP + runtime + plan + impl). Class 1 back-flow per X-AL-3.

### Option (c) — IS `read_latest` extension (ledger-state semantics)

| Surface | Change |
|---|---|
| IS spec | NEW `LedgerReader.read_latest()` contract surface |
| IS plan | NEW unit or extension to U-IS-NN landing arc |
| harness-is impl | NEW `read_latest()` method body |
| Runtime factory | Reader closure uses `ctx.ledger_reader.read_latest()` to compose anchor |
| Test | IS unit tests + factory integration tests |

Estimated 3-5 commits, multi-axis (IS + runtime). NO signature change; reader reads ledger-head, not driver-state.

## Adjacent defects surfaced (not patched per FM-2)

(i) Runtime spec v1.21 §14.14.7 deferred-discretion clause prose at line 2935-2936 still describes the composition body as "implementation discretion at the C-RT-24 landing arc". The prose is technically accurate (impl discretion does indeed cover the MVP placeholder choice), but does not record the won't-fix closure of the richer-body arc. NOT patched per FM-2 no-spec-amendment discipline (the spec records a deferred-discretion routing target; the routing-target now resolves to won't-fix at this closure doc; the spec does not need to absorb the resolution).

(ii) The MVP placeholder docstring at `pause_resume_protocol_factory.py:81-83` says "MVP placeholder — richer composition body would read ctx.ledger_reader for the current head entry_hash. v1.21 narrow-scope arc defers this per §14.14.7." This is technically accurate per the spec but represents the implicit (c) reading; the won't-fix closure surfaces (a) vs (c) as undetermined. NOT patched — the docstring describes the deferral, not the resolution, and the deferral framing is consistent with the closure (richer body deferred indefinitely without consumer).

## Cross-axis cascade

**ZERO at this arc.** No spec amendment; no CXA amendment; no plan revision; no impl commit; no new test surface. Pure closure-doc bookkeeping.

## Status post-closure

`pause_context_reader` factory MVP composition body (empty `StateSummary` + sentinel `"0"*64` anchor) — **structurally MET; CLOSED-as-WON'T-FIX (this arc, 2026-05-24)**. Recovery path preserved at three architectural options (a)/(b)/(c) above if a concrete consumer surfaces. The MVP placeholder satisfies the binding chain (U-RT-89 e2e PASS) and preserves the operator-supplied-reader override channel at factory keyword-arg for future opt-in use.

## Memory updates this arc

None. Per system reminder, MEMORY.md is over budget (28.9KB vs 24.4KB limit) — no new index entry; this closure is discoverable via `.harness/` directory listing and git history.
