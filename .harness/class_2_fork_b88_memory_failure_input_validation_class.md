# Class 2 Fork — B-88 (spec half): the C-MEM-19 failure vocabulary has no input-validation class, so a malformed memory-tool argument has nowhere truthful to go

**Status: FILED 2026-08-05, awaiting operator ratification.** Doc-only filing per the workspace
codex-context-guard rule (fork FILINGS ship doc-only FIRST; no `design-substrate/**` edit rides this
PR). Chain mirrors `B-107`'s, `B-98`'s and `B-97`(a)'s: **filing (this PR) → operator ratification →
spec leg → impl leg.**

**Register row.** `B-88` at `.harness/forward-register.yaml` (`status: registered_finding`, no `pr:`
field) + prose at `.harness/post-phase-8-forward-register.md` `### B-88` (`:859`–`:906`). The row's
**impl half LANDED 2026-07-28 at PR #1144**; its close-out step (2) — *"Decide the input-validation
class — REMAINS OPEN, spec-side"* — is the fork this filing carries. The row's `pr:` pointer and any
status change ride the **ratification** leg, not this PR; the row stays `registered_finding` here.

**Grounding HEAD.** `4f914159`. Every `§`/line cite below was re-resolved by direct read at this HEAD
and every count was recounted programmatically. **Five count claims and one file:line cite on the
row itself have drifted since the impl leg** — all six are recorded at §10 rather than silently
normalized, and the current numbers (not the row's) are used throughout this filing.

**What this filing does NOT do.** It does not re-litigate the impl half (the type-keyed declaration
mechanism, the deleted `"io" in exc_name` rule, the populations table, the witnesses, the
mutation probes). Those are LANDED and are treated as settled. It decides one thing: **whether
C-MEM-19's failure vocabulary gains a seventh member for input-validation faults.**

---

## §1 The question, and what carries it

A **malformed model-supplied memory-tool argument** — `memory tool argument 'limit' must be >= 1`,
`unsupported promotion target_kind 'nope'`, `allowed_kinds must be a sequence` — is raised as a
typed `MemoryToolExecutionInputError` and emitted on the C-MEM-19 telemetry surface as
`memory.failure_class = provider_adapter_failure`.

That value is a **declared stopgap, on the record, in the shipped code**. `memory_tool_executor.py`
`:150`–`:167` says so in its own docstring:

> *"B-88 (impl half), LEAST-WRONG STOPGAP - the flip site when the spec half lands. The closed
> C-MEM-19 vocabulary has no input-validation class, so a malformed model-supplied argument has
> nowhere truthful to go; adding a member is a Class 1 back-flow to `Spec_Memory_Substrate_v1.md`
> C-MEM-19 and is NOT absorbable at Phase 7 per X-AL-3."*

**Why it is a fork rather than an impl task.** `[HIGH]`

- **The vocabulary is a contract term.** `Spec_Memory_Substrate_v1.md` §C-MEM-19 Invariants `:870`
  names six values by prose; the code enum `MemoryTelemetryFailureClass`
  (`harness-is/src/harness_is/memory_observability.py:33`–`:41`) is its six-member realization. Any
  seventh member changes what the contract requires implementations to distinguish.
- **X-AL-3 forecloses absorbing it.** Adding a contract-named value at Phase 7 is precisely the
  silent design extension the rule exists to stop (root `CLAUDE.md` §4.4).
- **It is a genuine choice between substantive alternatives**, not a defect with one correct repair:
  the stopgap has a four-point rationale of its own (recorded at the row and at
  `memory_tool_executor.py:152`–`:166`), and blessing it is a live option. That makes it **Class 2**
  (in-execution operator decision) rather than Class 1 (halt-execution defect) per root `CLAUDE.md`
  §4.3 — the same classification `B-98`, `B-104` and `B-107` carry.

**The harm, stated precisely and against interest.** Nothing is broken. Every failure on the
CLASSIFY-ROUTED population — the executor's 10 raise sites plus the four classifier call sites'
paths — IS emitted, on the right span, with a value from the six-member vocabulary (the dispatch
population's telemetry fate is unverified; §4 Reading A's A-ii sub-decision states it). The harm is **triage resolution**: an
operator filtering `memory.failure_class = provider_adapter_failure` to find provider/adapter faults
gets, mixed in, every model-authored argument error — and (see §3(iv)) also gets every *unclassified*
failure, because `provider_adapter_failure` is simultaneously the classifier's **residual**.

---

## §2 Current behaviour at HEAD `4f914159`

| Surface | State |
|---|---|
| **Spec statement of the vocabulary** | `Spec_Memory_Substrate_v1.md:870`, ONE prose sentence inside `## C-MEM-19 - Observability` → `### Invariants`: *"Failure telemetry must distinguish policy denial, path violation, IO failure, serialization failure, provider adapter failure, and retrieval empty-result."* **No enum table, no value-domain subsection, and no closure statement** — see §3(ii) |
| **Spec statement of the attribute** | `:864`, the bare name `memory.failure_class` inside the ten-line ```` ```text ```` Required-attributes block at `:854`–`:865` |
| **Plan restatement** | `Implementation_Plan_Memory_Substrate_v1.md:829`, U-MEM-22 acceptance: *"Failure classes distinguish policy denial, path violation, IO failure, serialization failure, provider adapter failure, and retrieval empty result."* (note: `empty result`, unhyphenated — the spec hyphenates) |
| **Code realization** | `MemoryTelemetryFailureClass(StrEnum)`, `memory_observability.py:33`–`:41`; docstring *"Failure classes required by C-MEM-19."* Six members |
| **Classifier** | `classify_memory_failure`, `memory_observability.py:166`–`:200`. Declaration-first (`_declared_failure_class`, `:203`–`:220`, honoured only for real enum members), then four message/type heuristics, then the residual `return MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE` at `:200` |
| **The flip site** | `MemoryToolExecutionInputError.memory_failure_class`, `memory_tool_executor.py:169`–`:171`. Declared **explicitly, not inherited**, expressly so it stays a single-line flip (`:166`) |
| **Population — executor** | **10** `raise MemoryToolExecutionInputError(` sites in `memory_tool_executor.py` (`:271`, `:681`, `:690`, `:699`, `:708`, `:712`, `:724`, `:767`, `:771`, `:798`). These are the classify-routed ones: `execute`'s blanket `except` calls `classify_memory_failure(exc)` at `:255` |
| **Population — dispatch** | **8 further** `raise MemoryToolExecutionInputError(` sites in `lifecycle/llm_dispatch.py` (`:4334`, `:4338`, `:4344`, `:4346`, `:4450`, `:4458`, `:4947`, `:4958`), same class (imported at `:137`). `llm_dispatch.py` contains **no** `classify_memory_failure` call at all — these are tool-schema/context construction faults raised outside the executor's span. **18 raise sites total; only the executor's 10 are demonstrably classified here** |
| **Classifier consumers (non-test)** | **EXACTLY FOUR** `classify_memory_failure(...)` call sites: `harness-is/src/harness_is/memory_redaction.py:273`, `harness-runtime/src/harness_runtime/memory_capture.py:778`, `harness-runtime/src/harness_runtime/memory_tool_executor.py:255`, `harness-runtime/src/harness_runtime/lifecycle/native_memory_adapter.py:556`. All four pass the result straight into `set_memory_telemetry_attributes(..., failure_class=...)` |
| **Hardcoded-member emission sites (non-test)** | **FIVE**: `memory_capture.py:896` + `:1051` (`IO_FAILURE`), `memory_context.py:216` (`POLICY_DENIAL`), `:264` (`RETRIEVAL_EMPTY_RESULT`), `lifecycle/llm_dispatch.py:2938` (`POLICY_DENIAL if degraded.policy_denial else None`) |
| **Declaration sites (non-test)** | **NINE** `memory_failure_class: ClassVar[...]` declarations: `lifecycle/memory_tool_types.py:133` + `:157`; `memory_capture.py:286` + `:307`; `memory_tool_executor.py:100`, `:117`, `:144`, `:169`; `lifecycle/native_memory_adapter.py:79` |
| **Hash participation** | **NONE.** `memory.failure_class` is set only by `span.set_attribute` (`memory_observability.py:137`). It is not an input to any canonicalization, `snapshot_hash`, or `packet_hash` — see §3(iii) |

---

## §3 Five grounding findings that shape the readings

### (i) THE COUNCIL'S PREMISE IS FALSIFIED — there are **ZERO** exhaustive consumers `[HIGH]`

The row's `council` field says convening is *"Likely … an observability-vocabulary blast radius
(**every consumer switching on the value**)."* That is a claim, and it was **measured**, not
inferred. Sweep over `harness-{is,as,cp,od,cxa,core,runtime}` + `tools`, `.py` only, worktree copies
under `.claude/worktrees/` excluded:

| Consumer class | Count | Evidence |
|---|---|---|
| **(a) exhaustively switches / enumerates the members — would BREAK on a 7th** | **0** | Zero hits for `match … failure_class`, `for … in MemoryTelemetryFailureClass`, `list(MemoryTelemetryFailureClass`, `len(MemoryTelemetryFailureClass`, `MemoryTelemetryFailureClass.__members__`. A separate sliding-window sweep for any 6-line span mentioning ≥4 of the six member strings found **exactly one site in the whole tree**: the enum definition itself (`memory_observability.py:34`–`:39`) |
| **(b) produces / compares a SPECIFIC member — tolerant of additions** | **14 src** | 9 `ClassVar` declarations + 5 hardcoded emissions (both enumerated at §2) |
| **(c) passes the value through — telemetry attribute emission only** | **6 src** | 4 `classify_memory_failure` call sites + the two setter/span helpers `set_memory_telemetry_attributes` (`memory_observability.py:136`–`:137`) and `memory_telemetry_span` |
| **(d) test-only** | **8 files** | `harness-is/tests/{test_memory_observability, test_memory_redaction}` + `harness-runtime/tests/{test_lifecycle_llm_dispatch, test_memory_context, test_memory_failure_classification, test_memory_tool_executor, test_native_memory_adapter, test_u_mem_26_write_boundary}`. The only behaviourally load-bearing set is the 39-row table (§3(v)) |

Total non-test symbol references to `MemoryTelemetryFailureClass.<MEMBER>`: **20** (POLICY_DENIAL 8,
IO_FAILURE 5, PROVIDER_ADAPTER_FAILURE 3, PATH_VIOLATION 2, SERIALIZATION_FAILURE 1,
RETRIEVAL_EMPTY_RESULT 1) — of which **6 are inside `memory_observability.py` itself** (the residual
returns at `:193`/`:195`/`:197`/`:199`/`:200` plus the docstring example at `:158`).

**Consequence.** The stated blast radius does not exist. The classifier is **total** by construction
(`:200` returns a value for every input), so a seventh member cannot make any existing call site
non-exhaustive. `MemoryTelemetryFailureClass` is a `StrEnum` consumed as an attribute value, never as
a dispatch key. **This finding is what probe-resolves the council question at §7 — and it materially
cheapens Reading A.**

*One honest caveat.* `lifecycle/llm_dispatch.py` contains **13** occurrences of the lowercase token
`policy_denial`, and **every one of them** is the unrelated `_DegradedMemoryServe.policy_denial`
boolean field (declared `:2283`), not the enum member. The file's single enum use is the *uppercase*
`MemoryTelemetryFailureClass.POLICY_DENIAL` at `:2938` — which sits on the same line as one of the
boolean references. The census above counts symbols (`MemoryTelemetryFailureClass.<MEMBER>`), so it
is not contaminated by this collision; a naive string census would be.

*A second measurement caveat, recorded because it moved a number in this filing's own first pass.*
A bare-token census of the six member strings across test files returns **13** files; **five of
those are false positives from test FUNCTION NAMES** — `test_policy_denial_is_explicit_and_ledgerable`
(`harness-cp/tests/test_memory_access_mode.py:233`), `test_no_retry_on_io_failure_view` / `…_create`
(`test_lifecycle_memory_tool_filesystem.py:293`/`:319`),
`test_memory_path_violation_error_is_exception_subclass`
(`test_lifecycle_memory_tool_types.py:128`), `…typed_serialization_failure`
(`test_lifecycle_protected_result_store.py:310`), `test_path_violation_propagates_verbatim`
(`test_u_rt_81_memory_tool_dispatch.py:654`) — none of which references the vocabulary at all. The
true count is **8**, and it is the symbol-scoped census that is reported in the table above.

### (ii) THE SPEC DOES NOT CLOSE THE VOCABULARY — "closed" is a CODE-side and REGISTER-side word `[HIGH]`

The exact and complete spec statement is one sentence, `Spec_Memory_Substrate_v1.md:870`:

> *"Failure telemetry must distinguish policy denial, path violation, IO failure, serialization
> failure, provider adapter failure, and retrieval empty-result."*

Read against `## C-MEM-19 - Observability` in full (`:835`–`:870`): the section has a `### Contract`
listing ten covered operations, a ten-line Required-attributes text block, and two invariants. There
is **no value-domain subsection, no enum table, no "exactly six", and no closure statement** anywhere
in C-MEM-19. A grep for `closed` / `exactly six` / `value domain` across the whole memory spec
returns C-MEM-03's `provider_family` value domain (`:212`–`:232`) and change-note prose — nothing
bearing on C-MEM-19.

**Where "closed" actually comes from.** Two non-spec places: `_declared_failure_class`'s docstring
(*"the closed C-MEM-19 vocabulary"*, `memory_observability.py:213`–`:214`) and the B-88 register row
itself. Both are Phase-7 artifacts describing the *code enum*, which genuinely is closed. **The
contract sentence is a MUST-DISTINGUISH floor, not a ceiling.**

**Why this matters, in both directions.** `[MODERATE]`
- *For Reading A*: a seventh member **contradicts no spec sentence**. The amendment is additive —
  extend one list — not a reversal.
- *Against complacency*: a floor also means the current code is **already contract-conformant**. The
  six required distinctions are all made. Reading A is a *precision improvement*, not a conformance
  repair, and this filing does not claim otherwise.

**The in-spec precedent for exactly this move**, found at `Spec_Memory_Substrate_v1.md:496` (C-MEM-10,
landed at v1.2 under `B-92`):

> *"This is a **vocabulary addition, not a schema widening**: `risk_flags` is declared above as an
> open `list<string>`, so the new value requires no field, no type change, and no shape change at
> this contract."*

That is the same category as C-MEM-19's failure vocabulary at the same contract family, ratified
on 2026-07-29 (memory spec v1.1 -> v1.2, clearance marker
`.harness/clearance/spec-memory-substrate-v1-2-cleared-2026-07-29.md`). It is the nearest sibling
precedent this workspace has.

### (iii) HASH DISPOSITION — **ZERO**, verified rather than assumed `[HIGH]`

`memory.failure_class` reaches exactly one write: `span.set_attribute("memory.failure_class",
_string_value(failure_class))` (`memory_observability.py:137`). A window sweep for
`snapshot_hash|packet_hash|canonical|hashlib|sha256` within ±8 lines of every non-test
`failure_class` occurrence returns only **co-located parameter names** — `packet_hash` is a *sibling
attribute* passed alongside it (`:57`, `:81`, `:132`–`:133`, `:255`), never a hash *over* it. The
memory packet hash is computed elsewhere and consumed at `memory_context.py:261`. There is no
canonical dict, no snapshot, no chain input.

Contrast `B-98`'s finding (v) (`class_2_fork_b98_gate_description_durable_carrier.md:316`–`:361`),
where the disposition needed the whole drop-when-`None` precedent chain because the field lived on a
hashed `PauseSnapshot`. **Here the question does not arise**: a span attribute value has no hash
identity, so no `snapshot_hash` impact, no drop-when-`None` decision, and no migration surface. This
removes an entire cost column from Reading A.

### (iv) THE DECISIVE ASYMMETRY — the stopgap value **is also the residual** `[HIGH]`

`classify_memory_failure`'s final line is `return MemoryTelemetryFailureClass.PROVIDER_ADAPTER_FAILURE`
(`memory_observability.py:200`). It is the **catch-all** — every undeclared exception that trips none
of the four message heuristics lands there. Concretely, per the row's own populations table and
confirmed at HEAD, that bucket already holds: `MemoryOperationIdempotencyConflictError`, the
projection/redaction-event mismatch family, pydantic `ValidationError`, the
`MemoryToolExecutionError` base's defensive branch — and a bare `RuntimeError` (witness row, §3(v)).

So `provider_adapter_failure` currently means **either** "we determined this is an adapter fault"
**or** "we could not determine anything." Routing a large, well-typed, deliberately-classified
population into that same value makes the two indistinguishable at the telemetry surface.

**This is the strongest ground for Reading A, and it is a different argument from "the label is
imprecise."** A deliberate classification and a failure-to-classify must not share a value, or an
operator cannot tell a triaged failure from an untriaged one. Note that this argument is *symmetric*
with the impl half's own accepted reasoning (a real policy denial must not sit in the IO bucket) —
except that here the collision is with the residual, which is worse, because the residual by design
has no semantics at all.

### (v) THE WITNESS AND PLAN FOOTPRINT — measured, and small `[HIGH]`

- **Witness flips.** `harness-runtime/tests/test_memory_failure_classification.py` carries a single
  `@pytest.mark.parametrize` table with **39 rows** (recounted by AST, decorator at `:57`). By
  exception type: `MemoryToolExecutionDeniedError`→`POLICY_DENIAL` ×10;
  **`MemoryToolExecutionInputError`→`PROVIDER_ADAPTER_FAILURE` ×8** (`:90`, `:92`, `:96`, `:100`,
  `:103`, `:105`, `:110`, `:112`); `MemoryToolExecutionStoreError`→`IO_FAILURE` ×4;
  `MemoryCallbackIOError`→`IO_FAILURE` ×4; `_NativeMemoryPolicyDeniedError`→`POLICY_DENIAL` ×4;
  `MemoryPathViolationError`→`PATH_VIOLATION` ×3; `MemoryToolExecutionError`→`PROVIDER_ADAPTER` ×2;
  `MemoryCaptureScopeValueDomainError`, `MemoryCaptureReservedActorError`, `OSError`, `RuntimeError`
  ×1 each. **Exactly 8 rows flip under Reading A; the other 31 are untouched.**
- **No other assertion flips.** Sweep of every other test asserting `memory.failure_class`:
  `test_memory_tool_executor.py:722` (`io_failure`, store path) and `:751` (`policy_denial`, denial
  path); `test_u_mem_26_write_boundary.py:479`–`:480` (`POLICY_DENIAL`);
  `test_memory_redaction.py` (2 rows: `io_failure` + `provider_adapter_failure`, the latter for
  `MemoryOperationIdempotencyConflictError`, not an input error);
  `test_native_memory_adapter.py` (6, all denial/path). **None asserts
  `provider_adapter_failure` on an input-error path.**
- **Plan rider.** `Implementation_Plan_Memory_Substrate_v1.md` U-MEM-22 (`:812`–`:834`) owns the
  vocabulary: `Implement:` `:823` *"Failure class vocabulary."*, `Acceptance:` `:829` restates the
  six values. **Reading A owes a one-line amendment to `:829`** (and no new unit — see §9). No other
  `U-MEM-*` or `U-IS-*` unit names the failure vocabulary; a sweep of both memory artifacts for the
  six-value list returns exactly the two sites `Spec:870` and `Plan:829`.
- **Cross-spec drift.** Sweep of all `design-substrate/Spec_*.md` + `Implementation_Plan_*.md` for
  restatements of the vocabulary: **exactly two sites, both named above.** No sibling axis spec
  (IS / AS / CP / OD / Runtime) restates it. `ADR-D5.md` mentions `policy_denial` twice and
  `Spec_Control_Plane_v1_2.md:1911` / `Implementation_Plan_Control_Plane_v2_4.md:633` once each —
  read directly, **all four are the CP-axis `validator.fail.cause_attribution` vocabulary**, a
  different namespace that happens to share one value name, and one the CP artifacts declare an
  **"enum string from open set"** in the same breath. Not C-MEM-19 restatements. **A seventh member
  falsifies no other artifact** — and the workspace's nearest sibling failure-cause vocabulary is
  already declared open.
- **CXA impact: ZERO, determined not assumed.** The change adds no cross-package consumption: the
  enum already lives in `harness-is` and is already imported by `harness-runtime`
  (`memory_tool_types.py:38` and four sibling modules). No new package edge, no new typed seam, so
  nothing is owed at `Cross_Axis_Composition_Document_v2_23.md` §2.3 — the same disposition
  `B-97`(a) reached for the same reason.

---

## §4 The readings

### Reading A — add a SEVENTH C-MEM-19 member for input-validation faults *(RECOMMENDED)*

**Name: `input_validation_failure`** (spec prose form: *"input validation failure"*). Justification,
since the row leaves the name open:

1. **Shape match.** Three of the six existing members are `<domain>_failure` noun phrases
   (`io_failure`, `serialization_failure`, `provider_adapter_failure`). `input_error` breaks that
   shape and reads as an exception *type* name (it collides idiomatically with
   `MemoryToolExecutionInputError`); `input_validation` alone is not a failure noun phrase.
2. **It is already the name the workspace reached for.** The literal string
   `"input_validation_failure"` exists at HEAD — as the deliberately-bogus non-member fixture at
   `harness-is/tests/test_memory_observability.py:55`. Independent evidence that this is the natural
   name for exactly this concept.
3. **Witness-hygiene consequence, stated because it is easy to get wrong.** That fixture does **not
   break** if the name is adopted: `_declared_failure_class` gates on
   `isinstance(declared, MemoryTelemetryFailureClass)` (`memory_observability.py:218`), and the
   fixture's attribute is a plain `str`, which is not an instance of the `StrEnum` subclass. The row
   stays green. But its comment (*"A non-member declaration is ignored: the closed C-MEM-19
   vocabulary cannot be widened by an attribute"*, `:82`–`:83`) would then name a **real** member
   while intending a non-member — semantically muddled. **The spec leg's impl rider must re-key that
   fixture to a genuinely non-member string.** If the operator prefers to avoid this entirely,
   `input_error` is the fallback name at the cost of point 1.

**Spec amendment shape — ONE site, one sentence extended.** `Spec_Memory_Substrate_v1.md:870`:

> *"Failure telemetry must distinguish policy denial, path violation, IO failure, serialization
> failure, provider adapter failure, input validation failure, and retrieval empty-result."*

Plus **one boundary sentence**, appended as a second invariant — without it the new member is
under-specified and the next arc re-litigates it:

> *"Input validation failure names a refusal of caller- or model-supplied arguments at the memory
> tool boundary — a malformed, out-of-domain, or missing argument. It is distinct from provider
> adapter failure, which names a fault of the provider adapter or its transport, and from
> serialization failure, which is reserved for record-codec faults."*

**Impl flip — ONE line.** `memory_tool_executor.py:169`–`:171`:
`PROVIDER_ADAPTER_FAILURE` → `INPUT_VALIDATION_FAILURE`, plus the new enum member at
`memory_observability.py:41`-ish and a rewrite of the `:150`–`:167` stopgap docstring (which
explicitly names itself the flip site).

**Populations that move: the `MemoryToolExecutionInputError` family, and ONLY it — with one
population split the spec leg MUST resolve (codex R4, accepted).** The declaration lives on the
TYPE, so all **18** repo-wide raise sites' instances carry it — but the type is raised for TWO
distinct fault kinds. The executor's 10 sites are genuine caller/model argument validation (inside
the boundary sentence above). The `llm_dispatch.py` population includes at least two sites —
`:4458` and `:4958`, raised when the internal `MEMORY_TOOL_CONTRACTS` schema itself lacks
`properties` — plus missing-runtime-context sites, which are INTERNAL configuration/wiring faults,
not caller-supplied-argument refusals; labeling those `input_validation_failure` would contradict
the boundary invariant on its face. **Sub-decision A-ii, owed at the spec leg (impl rider):**
either (a) re-type the internal-fault raise sites to a type outside the family (e.g. the base or a
dispatch-local subtype declaring `provider_adapter_failure`) so the family boundary IS the type
boundary — the recommended shape, keeping declaration-at-the-definition-site honest — or (b)
accept the family-wide declaration and record the internal-fault sites as mis-typed at birth (a
pre-existing typing choice, arguably its own defect row). Either way the spec leg MUST first
establish empirically whether the dispatch population reaches `classify_memory_failure` at all
(`llm_dispatch.py` contains no call to `classify_memory_failure` — this filing verified the
absence by direct search but did NOT trace whether those raises reach any other classifying span,
so their telemetry fate is stated here as UNVERIFIED rather than assumed; only the executor's 10
sites are demonstrably classified), and the impl rider MUST witness the dispatch population's
emitted class (or its unreachability) explicitly, per the production-path verification rule. The
base `MemoryToolExecutionError`'s `provider_adapter_failure` (`:100`–`:101`), the classifier residual
(`memory_observability.py:200`), and every other declared class stay exactly where they are. Reading
A does **not** touch the residual — see §5's dominated variant A′.

**Witness shape.** (a) The 8 table rows at `test_memory_failure_classification.py` flip their
expected value; (b) **two negative rows, one per gate, with distinct literals** — (b1) the point-3
fixture RE-KEYED to a genuinely non-member literal (e.g. `"not_a_c_mem_19_class"`), pinning that the
closed vocabulary cannot be widened by an arbitrary declaration, and (b2) a NEW second fixture
declaring the plain `str` `"input_validation_failure"` — the new member's VALUE but not the enum
member — still IGNORED, pinning the `isinstance(declared, MemoryTelemetryFailureClass)` type gate
(`memory_observability.py:218`) independently of membership. One fixture cannot serve both rows: b1
must not name a real member's value and b2 must; (c) a **mutation probe**: revert the declaration at
`memory_tool_executor.py:169`, confirm exactly the 8 rows fail with
`assert 'provider_adapter_failure' == 'input_validation_failure'`, restore.

**Plan rider.** `Implementation_Plan_Memory_Substrate_v1.md:829` acceptance line extended to seven
values. **No new unit** — U-MEM-22 already owns the vocabulary and is already landed; this is an
acceptance-criterion amendment, the same shape the `B-100` CP plan leg used (AC amended, zero new
units).

**Costs, stated plainly.** ZERO hash impact (§3(iii)); ZERO CXA rows (§3(v)); ZERO contract numbers
minted (extends C-MEM-19, does not create one — per `[[spec-leg-cannot-mint-contract-number]]`);
ZERO other artifacts falsified (§3(v)); 8 witness rows + 1 fixture re-key + 1 enum member + 1
declaration line + 2 doc lines. **Spec version: v1.2 → v1.3.** Plan: v1.2 → v1.3.

### Reading B — bless the stopgap: record `provider_adapter_failure` as the DELIBERATE home

**Spec amendment shape — one appended paragraph at C-MEM-19 Invariants**, vocabulary stays six:

> *"A refusal of caller- or model-supplied arguments at the memory tool boundary is reported as
> provider adapter failure. The fault originates in a provider- or model-emitted tool call arriving
> through the adapter rather than in the memory substrate's own IO or record codecs, and the
> retry-classification surface groups it with the provider-payload-shape family on the same
> reasoning. Serialization failure remains reserved for record-codec faults."*

**The argument is the row's own four points**, re-verified at this HEAD: (i) the fault originates in
a provider/model-emitted tool call arriving through the adapter; (ii)
`retry_breaker_fallback._classify_provider_exception` already groups `MemoryToolExecutionInputError`
with `LLMDispatchPayloadShapeError` in one `isinstance` tuple — **verified at
`retry_breaker_fallback.py:325`–`:333`, both named at `:329`–`:330`**, with the rationale spelled at
`:293`–`:298`; (iii) it restores the pre-B-84 value, so B-84's incidental shift is reverted rather
than entrenched; (iv) `serialization_failure` is reserved for record-codec faults and using it here
would poison that bucket.

**Zero impl delta. Zero witness delta.** The only code change is rewriting the
`memory_tool_executor.py:150`–`:167` docstring, which currently calls itself a stopgap and names a
spec leg that would no longer be coming.

**What Reading B costs, stated because the row does not.** It ratifies the residual collision at
§3(iv): `provider_adapter_failure` remains simultaneously the deliberate class for a large typed
population **and** the classifier's catch-all. Reading B should therefore be understood as ratifying
that collision, not as leaving it open.

### Reading C — DEFER, with a falsifiable demand test

Vocabulary stays six; the row stays `registered_finding` with an explicit reopening condition, per
the `B-98` / `B-104` pattern. The shipped docstring does NOT stay as-is: it currently PROMISES a
spec leg ("the flip site when the spec half lands"), which selecting C falsifies, so the
ratification leg rewrites it to state the deferral + demand test instead (§8/§9's immediate-rewrite
requirement — the value stays `provider_adapter_failure`; only the promise text changes). **The
row reopens on ANY of:**

- **D-0** — a **retention/triage surface** consumes `memory.failure_class` for operator-facing
  filtering (a dashboard, an alert rule, an audit query). Today no such consumer exists in-tree
  (§3(i)); the moment one does, the residual collision becomes an operator-visible defect rather
  than a latent one. *(Dominant disjunct — it is the only one that converts the harm from
  theoretical to observed.)*
- **D-1** — a **second input-error family** appears that is *not* provider-originated (e.g. a
  harness-internal caller passing a malformed memory-tool argument). Rationale (i) of Reading B —
  "the fault originates through the adapter" — is then false for part of the population, and the
  bless becomes untenable.
- **D-2** — an **operator triage incident** conflates input errors with adapter faults, or requires
  the split to answer a question.
- **D-3** — a **later arc changes the classifier residual** to a dedicated unclassified value. That
  removes the §3(iv) collision, at which point Reading A's decisive argument weakens to the merely
  cosmetic and this row should be re-decided from scratch rather than executed as filed.

**Cost.** Zero now. The debt is that the shipped docstring keeps promising a spec leg — under
Reading C it must be rewritten to say "deferred under the B-88 demand test", or it becomes a
stale-carry the next reader trusts.

---

## §5 The decisions, and one variant considered and dominated

**There is exactly ONE decision:** does C-MEM-19's failure vocabulary gain a seventh member (A),
formally not (B), or is the question deferred with a stated reopening test (C)? The naming question
(`input_validation_failure` vs `input_error`) is a **sub-decision of A only**, with a recommendation
and a fallback at §4; it does not need its own gate.

**Variant A′ — considered, dominated, recorded so it is not re-proposed.** Instead of adding an
input class, change the **residual** at `memory_observability.py:200` to a new `unclassified` member.
That addresses §3(iv)'s collision directly and is the same *category* of change (one added member,
one contract sentence). **It is dominated because it does not fix the primary mislabel**: a malformed
model argument would still be reported as `provider_adapter_failure`, only now with fewer
false companions. A′ is a *sibling improvement to the residual*, not an alternative to A — if the
operator finds §3(iv) the compelling argument but rejects A, A′ is the coherent follow-on, and it
should be registered as its own row rather than absorbed here.

---

## §6 Recommendation — **Reading A**, runner-up **Reading C**, and the discriminator that flips it

**RECOMMENDED: Reading A** (`input_validation_failure`, plus the boundary invariant). `[MODERATE]`

Grounds, in order of weight:

1. **§3(iv), the residual collision.** The chosen stopgap value is the classifier's catch-all. A
   deliberate classification and a failure-to-classify sharing one value is not imprecision — it
   destroys the ability to tell triaged from untriaged failures. This argument is independent of
   whether the input-error label itself is "close enough."
2. **§3(i), the measured blast radius is EMPTY.** The one substantive reason to prefer B or C — that
   widening an observability vocabulary is expensive — was *measured and found absent*: zero
   exhaustive consumers, zero hash participation, zero cross-artifact restatements beyond the two
   sites the amendment itself touches, zero CXA rows. The change is 8 witness rows and ~5 lines of
   contract and code.
3. **§3(ii), the spec does not forbid it,** and its nearest sibling precedent — C-MEM-10's
   `cross_family_capture` at `:496`, ratified 2026-07-29 under `B-92` — explicitly blesses
   "vocabulary addition, not schema widening" at this same contract family.
4. **The shipped code already predicts this outcome.** `memory_tool_executor.py:152` calls itself
   *"LEAST-WRONG STOPGAP - the flip site when the spec half lands"* and `:166` explains that the
   declaration is written explicitly rather than inherited *precisely so it stays the flip site*. The
   impl half was built anticipating A. That is not authority — the impl half cannot decide a spec
   question — but it means A costs strictly less than it would have.

**A note against my own recommendation.** `[HIGH]` Reading B's point (ii) is real and verified:
`retry_breaker_fallback.py:325`–`:333` genuinely groups `MemoryToolExecutionInputError` with
`LLMDispatchPayloadShapeError`. But that grouping answers a **retry** question (fail-fast vs
transient), not a **taxonomy** question — two exceptions can share a retry disposition and still be
different kinds of fault. The `_classify_provider_exception` docstring at `:285`–`:298` frames the
grouping entirely in fail-fast terms and never claims a telemetry class. So (ii) is evidence about
*retry policy*, not about what `memory.failure_class` should say. I judge it non-decisive; an
operator who reads it as decisive should pick B, and that is a legitimate reading of the same facts.

**RUNNER-UP: Reading C** (defer with D-0…D-3), *not* Reading B. Reason: C and A are both honest
about the residual collision — C simply says "not yet, and here is what would change my mind." B
**ratifies** the collision in contract text, which is the one outcome that is hard to walk back: a
spec sentence saying input faults *are* adapter faults must later be *retracted*, whereas C's
deferral costs one docstring edit. Under this workspace's own asymmetry reasoning (an addition later
is free; a retraction later is not — `B-98` §3(v)), B carries the only irreversible cost of the
three.

**THE DISCRIMINATOR — what flips the choice.** `[HIGH]`

> **Does `memory.failure_class` name the fault's KIND, or the fault's LOCUS?**

- If **KIND** (*what sort of failure was this*), an argument-validation refusal is categorically
  distinct from an adapter transport/protocol fault, and **A is right**. Three of the six members
  (`io_failure`, `serialization_failure`, `retrieval_empty_result`) are kinds, which is the reading
  the vocabulary mostly supports.
- If **LOCUS** (*which subsystem owns this failure*), then a model-emitted malformed argument
  genuinely entered through the adapter boundary, `provider_adapter_failure` is correct on its own
  terms, and **B is right** — with §3(iv)'s collision then reclassified as a *residual* defect to be
  fixed by A′ (§5), not by an input class.
- If the operator holds that **no in-tree consumer yet needs the split**, **C is right** — this is
  the "correct but not yet load-bearing" position, and D-0 is exactly its falsifier.

I recommend A because the vocabulary is majority-KIND and because the residual collision is a
locus-independent harm. **A single operator sentence choosing KIND, LOCUS, or "not yet" decides
this fork.**

---

## §7 Council position — **PROBE-RESOLVED; NO convening is owed** `[HIGH]`

The row's `council: Likely` was keyed on one named tension: an *"observability-vocabulary blast
radius — every consumer switching on the value."* The workspace's probe-first discipline (root
`CLAUDE.md` §10.9, council posture amendment 5) requires an empirical probe at the most specific
primary source before emitting a TENSION block. The probe was run (§3(i)) and **the premise is
falsified**: **zero** consumers switch exhaustively on the value; zero would break; the only site in
the entire tree that enumerates the vocabulary is the enum definition itself.

The nameable-tension discriminator (posture amendment 1) therefore fails: **C7/C8 (observability)
against the memory-contract owner have nothing to disagree about.** C7/C8's interest — telemetry
consumers must not break, and the namespace must stay coherent — is *served* by A, not opposed to it:
additivity is proven, and the boundary invariant at §4 is exactly the coherence C7/C8 would demand.
Convening a dyad whose two voices agree in advance is the primary-collapse failure the posture
amendments exist to prevent.

**What WOULD owe a convening.** If the operator selects **Reading B**, the contract would state that
input faults *are* adapter faults, which is a substantive observability-taxonomy commitment with a
real C7/C8 ⊥ memory-contract-owner tension (namespace coherence vs. locus-faithfulness). **A
Reading-B selection should be routed to a dyadic convening before the spec leg is authored.** A and C
do not owe one.

---

## §8 The ratification ask — ONE decision, three options

**This filing joins the standing operator ratification batch** alongside `B-96` (PR #1179), `B-98`
(PR #1180) and `B-104` (PR #1181), all `registered_finding` and awaiting the same gate.

| Option | What the operator ratifies | What it costs |
|---|---|---|
| **A** *(recommended)* | C-MEM-19 gains `input_validation_failure` as a seventh failure class, plus the boundary invariant distinguishing it from provider-adapter and serialization failure. Name defaults to `input_validation_failure`; `input_error` is the stated fallback | Memory spec v1.2 → v1.3 (1 sentence extended + 1 invariant added); memory plan v1.2 → v1.3 (U-MEM-22 `:829` extended, **no new unit**); impl: 1 enum member + 1 declaration flip + 1 docstring rewrite + 1 fixture re-key; 8 witness rows flip + 1 added + 1 mutation probe. Zero hash / CXA / contract-number impact |
| **B** | C-MEM-19 records `provider_adapter_failure` as the deliberate home for memory-tool input faults; vocabulary stays six | Memory spec v1.2 → v1.3 (1 paragraph appended); zero plan delta; zero impl delta beyond a docstring rewrite. **Routes to a dyadic council convening first (§7).** Ratifies the §3(iv) residual collision in contract text |
| **C** | Defer under the D-0…D-3 demand test; row stays `registered_finding` | One docstring rewrite AT RATIFICATION (not deferred — see §9) so the shipped stopgap text stops promising a spec leg |

**Carried by any answer** (no separate gate): the five count-drift repairs and the one stale file:line
cite at §10 ride the ratification leg's register touch; and under A or B the shipped
`memory_tool_executor.py:150`–`:167` docstring is rewritten to match the ratified outcome
(under C that rewrite is owed at ratification itself — see §9's C row).

---

## §9 Sequencing, and what each leg owes

| Leg | Owes | Gate |
|---|---|---|
| **This filing** (doc-only) | The filing + a `close_out` sentence + a prose bullet on `B-88`. Row stays `registered_finding`; **no snapshot change** (the digest is over `id:status` pairs, and status is unchanged) | — |
| **Ratification** | Operator selects A / B / C via `AskUserQuestion`; a `§11 RATIFICATION` section is appended to this filing; the register row's `pr:` pointer is set and (under A or B) status flips to `design_substrate_gated` | Operator |
| **Council** *(B only)* | Dyadic C7/C8 ⊥ memory-contract-owner convening per §7, before spec text is authored | Follows ratification |
| **Spec leg** *(A or B)* | `Spec_Memory_Substrate_v1.md` v1.2 → v1.3 by a dedicated spec-writer; under A also `Implementation_Plan_Memory_Substrate_v1.md` v1.2 → v1.3 (`:829`); clearance markers at `.harness/clearance/` per root `CLAUDE.md` §4.5, one per artifact actually changed — **under A both** (spec + plan), **under B the spec marker only** (the plan has zero delta and stays v1.2; the convention ties a marker to a changed, specifically versioned artifact, `.harness/clearance/README.md`). Memory-family precedent: `spec-memory-substrate-v1-2-cleared-2026-07-29.md` + `implementation-plan-memory-substrate-v1-2-cleared-2026-07-29.md` | X-AL-3 guard + adversarial review |
| **Impl leg** *(A)* | Enum member, the one-line declaration flip, the docstring rewrite, the fixture re-key, 8 flipped + the two added negative witness rows, the mutation probe | CI + `merge-gate` 3-lens (code-touching) |
| **Terminal leg** *(B)* | The one-line docstring rewrite at `memory_tool_executor.py` (the shipped text calls the classification a stopgap and promises a flip site; under B the spec BLESSES the value, so the docstring must say so) + the witness-comment refresh; lands WITH or immediately after B's spec leg, and closes the row — status transits `design_substrate_gated → closed` at this leg's merge | CI (docstring + test-comment only; `merge-gate` proportional-skip candidate) |

Under **C**, only the docstring rewrite is owed — and it is owed **at the ratification leg itself**,
not deferred: selecting C immediately falsifies the shipped docstring's "the single flip site when
the vocabulary gains an input class" promise, and no later memory arc is guaranteed to exist, so
deferring it would be exactly the stale-as-described carry the workspace's §10.5 rule forbids. The
ratification PR (or an immediate explicit follow-on leg in the same batch) carries the rewrite.

---

## §10 Cite re-verification at HEAD `4f914159`, and the count/cite drift found

Every cite in this filing was resolved by direct read at this HEAD. Every count was recomputed
programmatically (AST for the parametrize table; filesystem walks excluding `.claude/worktrees/`,
`__pycache__`, `.venv` for all sweeps).

**Verified as cited.**

| Cite | Verified |
|---|---|
| `Spec_Memory_Substrate_v1.md:870` — six-value MUST-distinguish invariant | ✓ exact sentence |
| `Spec_Memory_Substrate_v1.md:835`–`:870` — the whole of C-MEM-19; no closure statement | ✓ read in full |
| `Spec_Memory_Substrate_v1.md:496` — C-MEM-10 "vocabulary addition, not a schema widening" | ✓ |
| `Implementation_Plan_Memory_Substrate_v1.md:812`–`:834` — U-MEM-22; `:829` acceptance | ✓ |
| `memory_observability.py:33`–`:41` — six-member enum | ✓ (class `:33`, members `:36`–`:41`) |
| `memory_observability.py:166`–`:200` — classifier; `:200` residual | ✓ |
| `memory_observability.py:203`–`:220` — `_declared_failure_class`; `:218` isinstance gate | ✓ |
| `memory_tool_executor.py:149`–`:171` — the stopgap class + flip site at `:169`–`:171` | ✓ |
| `retry_breaker_fallback.py:325`–`:333` — the fail-fast isinstance tuple; `:329`–`:330` | ✓ |
| `test_memory_observability.py:52`–`:55`, `:82`–`:87` — the bogus-declaration fixture | ✓ |
| `.harness/post-phase-8-forward-register.md:859`–`:906` — the B-88 prose block | ✓ |

**DRIFT FOUND — six items, all on the B-88 register row itself, none changing any disposition.**
Recorded per the workspace stale-carry discipline rather than silently normalized. The current
numbers are what this filing uses.

| # | Row claim | Verified at HEAD `4f914159` | Class |
|---|---|---|---|
| 1 | *"the scope-value-domain exceptions declare `memory_failure_class` at their definition sites, `memory_capture.py:215` and `:236`"* (`close_out`) | **STALE.** `:215` is a blank line inside `MemoryCaptureStatus`; `:236` is `MemoryCaptureResult`'s docstring. The two declarations are at **`:286`–`:288`** (`MemoryCaptureScopeValueDomainError`, class at `:271`) and **`:307`–`:309`** (`MemoryCaptureReservedActorError`, class at `:291`) | 3 |
| 2 | *"`MemoryToolExecutionInputError`, all 10 sites"* | **10 in `memory_tool_executor.py`** (correct as scoped to the executor) but **18 repo-wide** — 8 more in `lifecycle/llm_dispatch.py`, which contains no classify site. The row's number is right for the classified population and wrong as a total | 3 |
| 3 | *"`MemoryToolExecutionDeniedError`, all **14** raise sites"* | **15** at HEAD (`memory_tool_executor.py:325`, `347`, `406`, `408`, `531`, `539`, `541`, `543`, `555`, `571`, `592`, `598`, `606`, `614`, `884`). Growth from later arcs, not a regression | 3 |
| 4 | *"37 parametrized rows"* (`test_memory_failure_classification.py`) | **39** (AST count, decorator `:57`) | 3 |
| 5 | *"Mutation probes (all **five** fail post-fix …)"* | **SELF-INCONSISTENT on the row.** The bullet's header says five while its own body enumerates **(a) through (g) — seven**; rounds 2 and 3 appended probes without refreshing the header. No probe is missing; only the count is wrong | 3 |
| 6 | *"all four native-adapter denial sites span-pinned"* | **6** `_NativeMemoryPolicyDeniedError` raise sites at HEAD: the row's four (`_require_native_access:294`, `_require_capture_allowed:299`, `_require_retrieval_allowed:313` + `:324`) plus `_require_scope_family_in_domain:305` and a third `_require_retrieval_allowed` branch at `:334` — both added by later arcs. Whether the two newcomers are span-pinned was **NOT** verified by this filing (out of scope for the spec half) and is stated as unverified rather than assumed | 3 |

Item 6's unverified tail is the one claim in this document I did not ground. It does not bear on any
reading; it is recorded so a later arc does not inherit "all four are pinned" as covering six sites.

**Review record (out-of-family `just codex-review`, branch-vs-main).**
- **R1 — 3 [P2], all accepted and fixed** (`6b19ad2c`): the §8 carried-repairs sentence undercounted
  ("four" → five count repairs + the stale cite); Reading B's spec-leg row over-mandated two
  clearance markers where the convention ties a marker to a changed artifact (B → spec marker only,
  A → both); Reading C's docstring repair was deferrable to an unspecified future arc — now owed at
  the ratification leg itself (stale-as-described rule).
- **R2 — 1 [P1] + 1 [P2], both accepted and fixed** (`1d02f554`): the register's B-88 prose/YAML
  still told the pre-filing story ahead of the appended filing bullet (council "likely" + five
  drifted counts) — reconciled IN PLACE per the replace-not-append discipline, history preserved
  parenthetically; the Reading-A witness recipe's single fixture contradicted its own re-key
  requirement — split into two negative rows with distinct literals (b1 non-member re-key, b2
  plain-str-of-the-new-member type-gate pin).
- **R3 — 2 findings, both accepted and fixed** (`e5094220`): Reading B's owed docstring rewrite had
  no terminal leg (§9's impl leg was A-only) — B now carries its own terminal leg and status
  transition; this review record itself still held the R0 placeholder while R1/R2 commits existed —
  replaced with a round-by-round account.
- **R4 — 2 findings, both accepted and fixed** (`75abd93e`): [substantive] Reading A treated all 18
  `MemoryToolExecutionInputError` raise sites as one population while `llm_dispatch.py:4458`/`:4958`
  raise the type for INTERNAL `MEMORY_TOOL_CONTRACTS` schema faults that contradict the boundary
  invariant — NEW sub-decision **A-ii** (re-type the internal-fault sites, recommended, or record
  them mis-typed at birth; dispatch population's classification reachability to be established at
  the spec leg, witnessed at the impl rider); [replace-not-append, third instance] the register's
  early bullets carried stale classifier (`:150-163` → `:166`–`:200`) and spec-invariant (`:641` →
  `:870`) cites plus an unqualified "closed" — corrected in place, date-stamped.
- **R5 — 2 [P2], both accepted and fixed** (`d8fab8a7` + this SHA-repair amendment): this record ended at R3 while HEAD was the
  R4 commit — extended; the A-ii text cited a phantom "§0 ungrounded-claim 2" — replaced with the
  inline statement of what was and was not verified.
- **R6 — 1 [P2] fixed** (`130a2270`): Reading C's paragraph contradicted §8/§9's immediate
  docstring-rewrite requirement — aligned. **R7 — 1 [P2] fixed** (`16e31032`): §1's "every failure
  IS emitted" scoped to the classify-routed population. **R8 — 1 [P2] fixed** (this commit): this
  record extended through R6/R7. **SOUNDNESS EXIT DECLARED at R8** per the workspace's
  deferred-mechanism review-exit discipline: the recommendation, runner-up, and discriminator never
  moved across eight rounds; substantive findings ended at R4 (A-ii); R5–R8 are
  consistency-of-the-record corrections — the self-referential-drift discriminator. Contract-level
  findings still reopen this record at ratification.
