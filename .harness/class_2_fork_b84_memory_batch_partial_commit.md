# Class 2 Fork — B-84 (partial-commit half): a memory-tool batch commits its earlier calls before a later call's executor-level argument failure aborts the batch

**Status: FILED 2026-08-05, awaiting operator ratification.** Doc-only filing per the workspace
codex-context-guard rule (fork FILINGS ship doc-only FIRST; no `design-substrate/**`, no
`.harness/forward-register.yaml`, no `.harness/post-phase-8-forward-register.md`, and no
`.harness/roadmap_status.md` edit rides this PR). Chain mirrors `B-88`'s, `B-107`'s and `B-98`'s:
**filing (this PR) → operator ratification → build leg(s)** — with the register row's `pr:` pointer
and any status change riding the **ratification** leg, not this one. The row stays
`registered_finding` here.

**Register row.** `B-84` at `.harness/forward-register.yaml` (`status: registered_finding`, no `pr:`
field) + prose at `.harness/post-phase-8-forward-register.md` `### B-84`.

**Grounding HEAD.** `496f0f4b`. Every `§`/file:line cite below was re-resolved by **direct read** at
this HEAD; every count was **recomputed** (`git grep -c` / AST / direct enumeration), never copied
from the row. **Two premise qualifications and seven stale cites** were found and are recorded at §9
rather than silently normalized — including **three stale cites in shipped code**, not just in the
register.

**What this filing does NOT do.** It does not re-litigate the **retry-duplication half**, which is
LANDED (2026-07-28) and settled: `MemoryToolExecutionInputError` is a member of the fail-fast
`isinstance` tuple at `retry_breaker_fallback.py:325`–`:333` (named at `:330`), documented at
`:293`–`:316`, with `MemoryToolExecutionDeniedError` deliberately excluded (`:312`–`:316`). Verified
at this HEAD. That half is treated as closed. This filing decides **one** thing: **what, if anything,
the harness owes for the partial-commit half.**

---

## §1 The question, and why it is a fork rather than an impl task

A memory-tool batch of `[memory.write_note (valid), <a later call that is dispatch-valid but
executor-invalid>]` passes **every** dispatch-side pre-check, so the executor runs the calls in
order: the first call **commits durable state**, and then the second raises. Nothing rolls back.

**Why this is Class 2 (in-execution operator decision), not Class 1 (halt-execution defect).**
`[HIGH]`

- **Nothing in the contract corpus is violated.** A repo-wide sweep of
  `design-substrate/Spec_Memory_Substrate_v1.md` and
  `design-substrate/Implementation_Plan_Memory_Substrate_v1.md` for
  `batch|all-or-none|transactional|journal|partial commit|pre-?pass|validate .* before` returns
  **ZERO hits in each file** (§3(ii)). C-MEM-14's four invariants (`:730`–`:733`) are stated
  **per call**, not per batch. There is no contract to fail.
- **It is therefore IMPL-DISCRETION, not spec-owed** — the same verdict the row's `close_out`
  records for the landed fail-fast half, now re-established from a repo-wide search rather than
  inherited (§3(ii)).
- **But it is a genuine choice between substantive alternatives with materially different blast
  radii** — a pre-pass, a positional constraint, a transactional batch, or a deferral — which is
  precisely root `CLAUDE.md` §4.3's Class 2 discriminator, and the same classification `B-88`,
  `B-98`, `B-104` and `B-107` carry.

**What ratification would authorize.** Under A, C or D: an **impl-discretion BUILD leg** only —
**no spec leg is owed**, because no `C-MEM-*` or `C-RT-*` contract sentence changes.

**Reading B is different, and its routing is stated explicitly (codex R2 [P1-a]).** `[HIGH]` B
introduces durable-write ORDERING and compensation semantics for a hash-chained append-only ledger,
which is a contract-shaped commitment against `C-MEM-08` / `C-MEM-14`. Per
`.claude/skills/phase-7-back-flow-routing/SKILL.md` §2.2, a Class 2 fork's Recording row reads
*"Sub-phase log only (no design-phase artifact revision)"*. **Selecting B therefore does not proceed
under this filing's Class 2 authority: it OPENS a Class 1 back-flow route** — halt, operator-authorized
routing to the Phase 5 memory-spec channel per root `CLAUDE.md` §4.3 — and the council convening at §7
precedes even that. **A Reading-B selection is a decision to open a Class 1 fork, not a decision to
build.** Nothing in this filing authorizes a contract edit.

**Why the FILING stays Class 2 (codex R2 [P1-a], partially declined — grounds recorded).** `[HIGH]`
The §2.2 **trigger** row — *"In-session decision-point requiring operator selection between
substantive alternatives (NOT an architectural defect)"* — is satisfied exactly: §3(ii) establishes
there is no contract to violate, so there is no architectural defect to halt on, and what is owed is
a selection among four substantive options. Reclassifying the whole filing as Class 1 would also
contradict settled practice: **10 of the 19 `class_2_fork_b*` filings in `.harness/` carry a spec
leg**, including every recent one (`B-88`, `B-93`/`B-45`, `B-96`, `B-97a`, `B-98`, `B-104`,
`B-107`) — four of which sit in the same standing ratification batch. The correct repair is the
paragraph above (name B's Class 1 route explicitly), not a reclassification that would silently
relitigate nine siblings. *(The taxonomy-row-vs-practice divergence this surfaced is real but is not
B-84's to settle; it is noted here and belongs to whoever next revises the routing skill.)*

---

## §2 The mechanism at HEAD `496f0f4b`, re-grounded end to end

| Stage | Site (verified by direct read) | What it does |
|---|---|---|
| **Dispatch pre-pass** | `_openai_prepared_memory_tool_calls` (`lifecycle/llm_dispatch.py:4187`–`:4226`) / `_ollama_prepared_memory_tool_calls` (`:4823`–`:4857`) | Resolves + validates the **complete** batch before any of it executes. Exactly four checks: OpenAI `tool_call.id` present/non-empty (`:4204`, OpenAI arm only — ollama has no such field, `:4833`–`:4834`); name resolution to a `MemoryToolName` (`:4265`–`:4272`); `arguments` normalizing to a mapping (`:4273`–`:4288`); and `_standard_memory_tool_context` (`:4323`–`:4364`) — `record_scope` present (`:4333`), `scope_ref` present (`:4337`), and the `scope_ref` **argument** matching the context for the two tools whose contracts declare it (`:4341`–`:4348`, membership computed from `MEMORY_TOOL_CONTRACTS` at `:4291`–`:4320`) |
| **What the pre-pass deliberately does NOT check** | same | Per-tool **required-argument keys** and per-tool **policy gates**. These are the EXECUTOR's semantics. Mirroring them into dispatch is the one-source-of-truth violation the B-82 arc declined by design; `_PreparedMemoryToolCall`'s own docstring (`:3933`–`:3951`) states the boundary |
| **Batch execution** | `_openai_memory_tool_result_messages` (`:4229`–`:4249`) / `_ollama_memory_tool_result_messages` (`:4860`–`:4882`) | `for call in prepared: standard_memory_tool_executor.execute(call.request)` — `:4236`–`:4237` and `:4874`–`:4875`. **Sequential, unguarded, no rollback.** Both docstrings say "Execute an ALREADY-VALIDATED batch in order" |
| **Per-call durable commit — record** | `StandardMemoryToolExecutor._write_note` → `capture_api.capture_tool_event(...)` (`memory_tool_executor.py:362`) → `EpisodicMemoryCapture._capture` → `store.write_record(record)` (`memory_capture.py:818`) then `store.append_memory_operation(payload)` (`:820`) | The record is written **before** its ledger entry, deliberately (`:809`–`:817`) |
| **Per-call durable commit — ledger, EVERY tool** | `StandardMemoryToolExecutor.execute` `:247` → `_append_standard_tool_call` (`:616`–`:652`) | **On the success path of EVERY call**, including read-only `memory.search` / `memory.read`, a `MemoryOperationKind.STANDARD_TOOL_CALL` row is appended to the durable ledger (`:634`). See §3(i) — this widens the row's framing |
| **The later raise** | `_string_arg` (`:678`–`:682`), `_optional_string_arg` (`:685`), `_positive_int_arg` (`:694`), `_allowed_kinds` (`:703`), `_kind_from_memory_ref` (`:764`), `_promotion_kind` (`:783`) | **10** syntactic `raise MemoryToolExecutionInputError(` sites in the executor (recounted: `git grep -c`), plus **8** in `lifecycle/llm_dispatch.py`. The executor's are the ones reachable *mid-batch* — see the count note below |
| **Retry disposition (LANDED half)** | `_classify_provider_exception` (`retry_breaker_fallback.py:269`, fail-fast tuple `:325`–`:333`) | Returns `None` → `_PerCandidateTerminal(result=None, …)` (`:998`) → the outer loop does **not** retry the same candidate but **does** advance to the next (`:692`–`:706`) |
| **Cross-candidate residual** | `_advance_or_exhaust` at `:699`; next candidate re-enters `self.inner.dispatch(rebound, step, …)` (`:948`) with the ORIGINAL `step` | The failed candidate's `prepared` batch is **local** to the inner dispatch and is never forwarded. The next candidate re-samples its own tool calls. **Duplication is CONTINGENT, not guaranteed** — confirmed |

**Count note — 10 syntactic, 9 model-reachable (codex R1 [P3], accepted).** `[HIGH]` The tenth is
`_execute_authorized`'s trailing `raise MemoryToolExecutionInputError(f"unsupported memory tool
{tool_name!s}")` (`memory_tool_executor.py:271`). `request.tool_name` is typed `MemoryToolName`, all
**five** members are dispatched at `:261`–`:270`, and the pre-pass only ever constructs a request
from a resolved enum member (`llm_dispatch.py:4206`/`:4838`), so that branch is a defensive residual
unreachable from model-supplied arguments. **9** is the number Reading A's coverage and W-4's scope
are stated against.

**Direction (1) and direction (2) are both confirmed UNBUILT at HEAD.** `git grep -n 'def validate'
harness-runtime/src/harness_runtime/memory_tool_executor.py` returns **nothing** — the executor's
sole public surface is `execute()` (`:231`), which alone carries the access check (`:239`), the
telemetry span (`:236`–`:255`) and the ledger append (`:247`); calling the private
`_execute_authorized` (`:259`) directly bypasses all three. And there is no transactional or
journaled batch surface anywhere on the standard-memory path (`:4236`/`:4874` are plain `for` loops).

---

## §3 Grounding findings that shape the readings

### (i) THE DURABLE FOOTPRINT IS WIDER THAN THE ROW STATES — every successful call commits `[HIGH]`

The row frames the committed prefix as *"the earlier write"*. Measured at HEAD, that undercounts:
`execute()` appends a `STANDARD_TOOL_CALL` memory-operation row for **every successful call**
(`memory_tool_executor.py:247` → `:634`), read-only tools included. So a batch of
`[memory.search (valid), <executor-invalid call>]` — with **no write at all** — still leaves a
durable ledger row behind.

**Stated against interest:** that row is arguably **truthful**. It attests that a search *did*
happen, and it did. The semantically damaging residue is `_write_note`'s **episodic record**, which
asserts a note the model was never told landed. So the honest statement is: **the durable footprint
is per-call and universal; the harm is concentrated in the write-like tools.** This matters because
it is what makes Reading C a *harm-reduction* rather than an elimination (§4).

### (ii) THE CONTRACT CORPUS IS SILENT ON BATCHES — measured, not assumed `[HIGH]`

Sweep for `batch|all-or-none|all or none|transactional|journal(ed)? batch|partial commit|pre-?pass|
validate .* before`, case-insensitive:

| Artifact | Hits |
|---|---|
| `design-substrate/Spec_Memory_Substrate_v1.md` | **0** |
| `design-substrate/Implementation_Plan_Memory_Substrate_v1.md` | **0** |

C-MEM-14 (`Spec_Memory_Substrate_v1.md:712`–`:733`) states four invariants, all **per call**:
*"Tools are policy-enforced at every call."*, *"Tools cannot bypass scope, redaction, retention, or
injection policy."*, *"Write-like tools append durable memory operation entries."*, *"Tool output
must include stable refs, not untracked memory prose."* (`:730`–`:733`). Nothing about ordering,
batching, or atomicity. The owning plan unit is **U-MEM-16** (`Implementation_Plan_Memory_
Substrate_v1.md:650`–`:675`, `Contracts: C-MEM-14`), whose four acceptance lines are likewise
per-tool.

**The only atomicity-adjacent sentence in the whole memory spec** is at `:516`, inside
`## C-MEM-10 - Promotion pipeline` (heading at `:471`) — and it explicitly declines to prescribe
machinery:

> *"Whether that is achieved by a compare-and-set, a generation token, a lock, or a transaction
> spanning validation and persistence remains implementation discretion; what is not discretionary
> is that the chosen mechanism must leave no interleaving in which the property fails."*

That is a **precedent, not an obligation**: it governs promotion **activation**, not memory-tool
batches, and it is the workspace's own statement that *the property is contractual and the mechanism
is not*. `[MODERATE]` — it supports treating the batch question as impl-discretion; it does not
decide which mechanism.

**And the Runtime spec does not cover this path at all.** All 40 `memory tool|memory_tool|C-MEM-14`
occurrences in `design-substrate/Spec_Harness_Runtime_v1.md` concern the **Anthropic
`memory_20250818` native** primitive (C-RT-22 §14.12 at `:5386`+; the C-RT-15 §14.5.1
callback-binding at `:3971`–`:3985`, whose step 1 detects `type == "memory_20250818"` at `:3977`).
The OpenAI/ollama **standard**-memory dispatch loops this row is about are not the subject of any
`C-RT-*` contract. `[HIGH]`

### (iii) THE U-MEM-27 RE-PRICE CUTS BOTH WAYS — the seam is real, and it is on the wrong path `[HIGH]`

The row's 2026-07-30 note says direction (2)'s cost predates U-MEM-27 and must be re-priced. It was.
Both named pieces exist at HEAD, with the semantics claimed:

- **`CanonicalMemoryStore.write_record_guarded`** (`harness-is/src/harness_is/memory_store.py:298`–
  `:352`). Signature: `(self, record: MemoryStoreRecord, *, precondition: Callable[[], bool]) ->
  MemoryStoreWriteResult`. It holds `self._write_scope(), _FILE_WRITE_LOCK, _JSONL_WRITE_LOCK`
  (`:341`), evaluates `precondition()` inside that hold (`:342`), raises
  `MemoryStoreGuardedWriteConflictError` on refusal (`:343`), and otherwise performs
  `_write_record_locked` without releasing (`:346`). Its own docstring calls it *"A GENERIC
  compare-and-commit seam"* carrying *"no promotion, provenance, or policy semantics"* (`:306`–
  `:308`).
- **`cross_process_scope_lock`** (`harness-is/src/harness_is/cross_process_ledger_lock.py:186`–
  `:218`). *"REENTRANT per thread, so a guarded section may call through the tree's own write path
  (which re-takes this lock) without self-deadlock; other threads and other OS processes still
  block."* (`:197`–`:200`). *"Same-host only, and a no-op on Windows"* (`:202`–`:203`).

**Three things the re-price must say honestly, all of which cut against the row's expected lean:**

1. **It is not transactionality.** `write_record_guarded` is a **single-record** compare-and-commit.
   A batch of N durable writes is N separate guarded writes. Nothing in it makes N writes
   all-or-none.
2. **The memory-tool write path does not use it.** `git grep -rn write_record_guarded` over all
   `harness-*/src` returns **exactly one production consumer**: `memory_promotion.py:911`. The
   `_write_note` path goes `capture_tool_event` → `_capture` → the **unguarded**
   `store.write_record` (`memory_capture.py:818`). Direction (2) would have to route the capture
   path through a new batch surface *or* reach below it — materially more than "the seam now
   exists."
3. **What the lock DOES give is exclusion, not atomicity.** A batch could hold the per-root scope
   across all its writes without self-deadlock (the reentrancy is real and load-bearing). That
   removes *interleaving* writers. It does **not** remove the earlier-commit-then-later-raise shape,
   which is intra-batch and needs compensation, not exclusion.

**Net re-price verdict.** `[MODERATE]` The substrate does move direction (2) from "starts from
nothing" to "has a locking primitive it can build on," but the **compensation question the direction
actually turns on is untouched**, and one obstacle the row did not know about was added: the write
path in question bypasses the guarded seam entirely.

### (iv) "ROLLBACK" HERE IS NOT DELETION, AND THE CROSS-CANDIDATE REPLAY SPLITS INTO FOUR CASES — NOT ONE `[MODERATE]`

*(This subsection was materially rewritten at codex R1 [P2-a]; the first pass asserted a single
"identical replay raises a conflict" outcome, which is **false as stated**. The corrected matrix is
below, and it makes the aggravator narrower than the first pass claimed.)*

**The mechanics, verified.** `MemoryRecordKind.TOOL_EVENT` is in `_JSONL_BY_KIND`
(`memory_store.py:195`–`:199`), so a `write_note` record is **appended** to the episodic tool-events
JSONL by `_append_jsonl` (`:266`–`:267` → `:623`–`:627`) — an unconditional `open("ab")` append with
**no dedupe**, and it runs **before** the ledger append (`memory_capture.py:818` then `:820`). The
`memory_id` is content-addressed (`:1117` → `_memory_id_for` `:1269`–`:1278` →
`derive_memory_id(EPISODIC, kind, content_hash)`) and the ledger `idempotency_key` is derived from it
(`:1084`–`:1087`).

**Two identity inputs the first pass missed.** (a) The hashed content includes
`"summary_model": summary.model` (`memory_capture.py:542`), and `_write_note` supplies
`SummaryProvenance(..., model=context.model)` (`memory_tool_executor.py:367`) where `context.model`
is the **per-candidate rebound model** (`llm_dispatch.py:4213`–`:4220`). (b)
`append_memory_operation` does **not** raise on every key collision: it compares an **18-field
equivalence payload** — including `provider` and `model`, excluding `timestamp` —
(`memory_operation_ledger.py:476`–`:519`) and returns `MemoryOperationWriteResult.IDEMPOTENT_NOOP`
on a match (`:536`), raising `MemoryOperationIdempotencyConflictError` **only** when the same key
carries a *different* payload (`:537`–`:539`).

**The corrected matrix for a cross-candidate re-emission of "the same" `write_note`:**

| Case | Record identity | Ledger outcome | Net effect |
|---|---|---|---|
| **(1) Re-sampled with different text** (likeliest — sampling is stochastic, and §3(v)'s aggravator raises malformed/varied re-emission) | different `content_hash` → **different `memory_id`** | new key → `APPENDED` | **An extra, distinct note.** Not a duplicate — a second memory the operator never asked for |
| **(2) Same text, different MODEL** (the ordinary fallback shape — a chain advances to another model) | `summary_model` differs → **different `memory_id`** | new key → `APPENDED` | Same as (1): **an extra distinct note** |
| **(3) Same text, same model NAME, different provider** (narrow: one model name served by two providers in the chain) | identical content → **same `memory_id`** → duplicate JSONL line appended at `:818` | same key, `provider` differs → **RAISES**; `_capture` re-raises for `event_kind != RUN_START_EVENT_KIND` (`:884`–`:885`) → broad handler `:892`–`:903` → `FAILED` → `MemoryToolExecutionStoreError` (`memory_tool_executor.py:385`–`:387`), which is **NOT** in the fail-fast tuple and classifies `TRANSIENT_RETRY` | **Duplicate physical line PLUS a re-opened retry staircase** on a different exception class than the one B-84's landed half closed |
| **(4) Fully identical** (same provider, same model — degenerate across candidates) | same `memory_id` → duplicate JSONL line still appended | equivalence matches → `IDEMPOTENT_NOOP` (`:536`), no raise | Duplicate physical line, reported CAPTURED |

**Stated with its confidence, and against interest.** `[MODERATE]` The whole matrix is a **code-read
inference, not an executed witness** — none of the four cases was run. Cases (1)/(2) are the
*ordinary* ones and produce an **extra note**, which is the honest statement of the harm; the first
pass's "duplicate line + re-opened staircase" claim survives only as case **(3)**, which is narrow.
Case (3), if real, is a **new aggravator on this row, not a defect elsewhere** — it would mean the
landed fail-fast half can be re-entered through `MemoryToolExecutionStoreError`. **The build leg must
witness the full four-cell matrix** (§8 W-5) and record the answers, rather than either reading being
relied on as settled.

### (v) THE AGGRAVATOR IS UNCHANGED AND UNVERIFIED HERE `[SPECULATIVE]`

The row's ollama-SDK finding (the client revalidates tool mappings as its own closed-field-subset
`ollama.Tool` model, silently dropping `additionalProperties` / `minimum` / `minLength`, so the
model never sees the constraints the contracts declare) was verified **at registration time against
the locked `ollama==0.6.2`**. This filing **did not re-verify it** — it is an aggravator on
likelihood, not on mechanism, and no reading below turns on it. Recorded as inherited-and-unre-checked
rather than restated as fresh.

---

## §4 The readings

### Reading A — an executor-exposed pure `validate()` pre-pass *(RECOMMENDED)*

**Shape.** `StandardMemoryToolExecutor` grows a **side-effect-free** `validate(request:
MemoryToolExecutionRequest) -> None` that runs exactly the argument checks `_execute_authorized`
would run for that tool, raising the same `MemoryToolExecutionInputError`. Both
`_openai_prepared_memory_tool_calls` and `_ollama_prepared_memory_tool_calls` call it for every
prepared call — inside the existing pre-pass, where nothing has run yet — before either result-message
builder is reached.

**Why it does not violate the one-source-of-truth boundary.** The executor still owns the semantics;
dispatch only *asks*. This is the row's own direction (1), and it is the shape the B-82 arc's
declined alternative (mirror-copying required-key rules into dispatch) was declined *in favour of*.

**Blast radius.** One new public method on the executor + two call sites. **Zero** contract text,
zero spec/plan version bump, zero CXA rows (no new cross-package consumption — `harness-runtime`
already imports the executor), zero durable-write ordering change.

**What it closes, and what it does NOT — stated precisely.** `[HIGH]`
- **Closes** the demonstrated door: the argument-shape class, i.e. the **9 model-reachable** of the
  executor's 10 `MemoryToolExecutionInputError` raise sites (see §2's count note).
- **Does NOT close** anything the pre-pass cannot predict. `_write_note` calls
  `self._policy_resolver.resolve_capture()` (`memory_tool_executor.py:345`) and `_propose_promotion`
  calls `resolve_promotion()` (`:404`); a resolver that flips between validate and execute reopens
  the window (a genuine TOCTOU, not a hypothetical — the same class C-MEM-10 `:514`–`:516` reasons
  about). Nor does it cover store errors (`MemoryToolExecutionStoreError`) or §3(iv)'s idempotency
  conflict.
- **Standing discipline cost:** every future executor check must land in the shared path or the
  pre-pass silently stops being exhaustive. That is a real maintenance obligation, and the build leg
  owes a witness that pins it (§8, W-4).

### Reading B — transactional / journaled batch execution at the executor

**Shape.** The executor accepts a batch and either commits all durable operations or none, using the
memory-operation ledger as the journal, with the per-root `cross_process_scope_lock` held across the
whole batch.

**Strictly stronger.** It covers every mid-batch failure — argument, policy flip, store I/O,
idempotency conflict — because it constrains the *outcome*, not the *prediction*.

**Priced honestly at HEAD (§3(iii)–(iv)):** `[MODERATE]`
- The reentrant scope lock genuinely enables a hold across N writes. That part of the re-price is
  real.
- `write_record_guarded` **does not** supply transactionality, and the write path in question does
  not go through it — so the seam is not the shortcut the row's note hoped for.
- **"Rollback" for an append-only, hash-chained, content-addressed JSONL store is not deletion.** It
  is compensating ledger entries — which means new operation-kind or projection semantics, i.e. a
  **C-MEM-08 / C-MEM-14 contract question**, not an impl choice.
- Consequently **B is the only reading that owes a spec leg** — and, per §7, a **council convening
  before that leg is authored**.

**Blast radius.** Largest: durable-write ordering, a new executor batch surface, compensation
semantics on a hash-chained ledger, a spec leg, a plan amendment at U-MEM-16, and a migration story
for in-flight ledgers. Not recommended now; **not foreclosed by A or C** (both are strictly weaker
and compose beneath it).

### Reading C — a dispatch-side positional constraint: at most one durable-effecting call, and it must be last

**Shape.** In the existing pre-pass — where `tool_name` is already resolved and nothing has executed
— refuse any batch in which a **durable-effecting** tool (`write_note`, `propose_promotion`,
`request_redaction`; the C-MEM-14 *"Write-like tools append durable memory operation entries."*
partition, `Spec_Memory_Substrate_v1.md:732`) appears anywhere but last, or appears more than once.
Raise `MemoryToolExecutionInputError` — already fail-fast — before executing anything.

**Why it is genuinely cheaper than A, and structurally different.** It mirrors **zero** executor
semantics: it keys only on the tool identity the pre-pass already computed. And it is **positional,
not predictive** — it removes the *inter-call* commit-then-raise sequence regardless of *why* the
later call fails, including the policy-flip class A cannot predict.

**What it costs, stated plainly.** `[HIGH]`
- **It is model-visible.** A batch the model legitimately emits — `write_note` then `search` — is
  refused outright, converting a partial success into a total failure. Under §3(v)'s aggravator,
  refusals may not be rare.
- **It is harm-*reduction*, not elimination**, because of §3(i): earlier successful **read-like**
  calls still append `STANDARD_TOOL_CALL` ledger rows before a later raise. That residual is
  defensible (those rows truthfully attest calls that happened) but it must not be described as
  closed.
- **It does NOT close the store-error residual, and the first pass wrongly claimed it did** (codex
  R2 [P1-b], accepted — the correction is load-bearing enough to state as its own finding):

  > **§3(vi) — the commit-then-raise window is also INTRA-CALL, so no positional rule can close it.**
  > `[HIGH]` `_capture` writes the record (`memory_capture.py:818`) **before** appending its
  > operation-ledger entry (`:820`), both inside one `try`; a failing append lands in the broad
  > handler (`:892`–`:903`) → `FAILED` → `MemoryToolExecutionStoreError`
  > (`memory_tool_executor.py:385`–`:387`) **with the record already durable**. Independently,
  > `execute()` runs `_execute_authorized` (`:240`) and only then `_append_standard_tool_call`
  > (`:247`), so a failing ledger append there raises *after* the tool's durable effect. **Both
  > windows exist inside a SINGLE call**, and therefore inside a single-call batch — which is the
  > common shape the row calls unreachable.

  **Consequences, stated because they cut across the whole filing.** (a) Reading C is bounded to the
  *inter-call* sequence and must retain + witness the intra-call residual (§8, W-6). (b) Reading A
  never claimed to close store errors, so A is unaffected. (c) **Reading B's relative value rises**:
  it is the only reading whose guarantee is outcome-shaped and therefore the only one that reaches
  the intra-call window. (d) Reading D's severity paragraph strengthens: the partial commit is
  deterministic *and* reachable without any batch at all.

**Blast radius.** One predicate + one refusal branch in each of the two pre-passes. Zero contract
text, zero new public surface, zero ordering change.

**A and C compose.** A prevents the predictable case; C bounds the unpredictable one. Nothing
requires choosing exactly one, and B subsumes both.

### Reading D — DEFER, with a falsifiable demand test

Row stays `registered_finding` with an explicit reopening condition, per the `B-98` / `B-104`
pattern. **Reopens on ANY of:**

**Deferral is defensible only on a SEVERITY judgment, not on a reachability one — stated because
codex R1 [P2-b] caught the first pass conflating the two.** `[HIGH]` The **partial commit itself is
DETERMINISTIC on today's default single-candidate chain**: `[write_note (valid), read (invalid)]`
commits the note and then aborts, every time, with no fallback chain involved (§1, §2, W-1). What is
cross-candidate and contingent is only the **duplication** (§3(iv)). Choosing D therefore means
judging that *a committed-but-unreported note is tolerable*, not that the harm is rare.

- **D-0 — an OBSERVED partial commit.** A run leaves a `write_note` record (or a
  `STANDARD_TOOL_CALL` row) for a batch that reported failure, seen in a real ledger. *(Dominant
  disjunct: it is the only one that converts the harm from inferred to observed. The class is
  deterministic in code but has not been seen in a real ledger.)*
- **D-1 — the multi-candidate chain becomes the default.** This raises only the **duplication**
  residual from contingent to routine; it does not bear on the partial commit, which is already
  deterministic. Any config change making multi-candidate chains ordinary trips it.
- **D-2 — §3(iv) case (3) is confirmed by execution.** If the same-text/same-model-name/
  different-provider replay really does append a duplicate physical line **and** re-open a
  `TRANSIENT_RETRY` staircase via `MemoryToolExecutionStoreError`, the landed half is narrower than
  believed and the deferral is no longer honest.
- **D-3 — a write-like tool gains a non-idempotent side effect outside the memory store** (an
  outbound notification, a promotion activation with an external effect). Compensation stops being
  a ledger-local question and A/C stop being adequate.

**Cost.** Zero code now. The debt is that `_PreparedMemoryToolCall`'s docstring
(`lifecycle/llm_dispatch.py:3936`–`:3946`) currently narrates the batch pre-pass as *"what makes the
memory tool loops safe against a partially-committed batch"* — true of the dispatch-side half,
misleading as a standalone claim about the executor-side half. **Under D that sentence must be
qualified at the ratification leg itself, not deferred**, or it becomes exactly the
stale-as-described carry root `CLAUDE.md` §10.5 forbids. (Under A or C it must be updated anyway, to
describe what actually landed.)

---

## §5 Recommendation, runner-up, and the discriminator

**RECOMMENDED: Reading A** (executor-exposed pure `validate()` pre-pass). `[MODERATE]`

Grounds, in order of weight:

1. **It is the reading the workspace's own boundary reasoning already points at.** The B-82 arc
   declined dispatch-side contract prevalidation *because it would mirror-copy executor semantics*.
   A is the shape that gets the same coverage without the copy: the executor stays the single
   authority and dispatch asks it. Choosing anything else means either re-opening that settled
   boundary or accepting a weaker guarantee for reasons independent of it.
2. **It closes the demonstrated door at the lowest cost of any reading that closes it.** One method,
   two call sites, zero contract text, zero ordering change, zero CXA rows.
3. **It forecloses nothing.** C composes with it; B subsumes it. Picking A now does not make the
   stronger reading more expensive later.
4. **It is honest about its residual.** A does not claim to close policy-flip or store-error
   windows, and §4 says so; a reading whose stated scope matches its actual scope is worth more than
   one that overclaims.

**RUNNER-UP: Reading C**, not B and not D. C is the *stronger* harm-closer on the record axis
(positional beats predictive) and is cheaper still — it loses only on **model-visible refusals**,
which is a product judgment rather than a correctness one. An operator who weighs "never commit a
prefix" above "never refuse a batch the model legitimately emitted" should pick C, and that is a
legitimate reading of the same facts.

**A note against my own recommendation, sharpened at codex R2.** `[HIGH]` A's coverage is bounded by
what a pure function can predict, and §4 names two classes it cannot (policy flip, store error). If
the operator's real objection to the status quo is *"a durable commit must never be followed by an
abort"* — an outcome-shaped requirement — then A does not deliver it, **and neither does C**: §3(vi)
establishes that the window is also **intra-call**, so no positional rule over a batch can reach it.
**Only Reading B satisfies an outcome-shaped requirement**, and B is the reading that opens a Class 1
route. That is the real cost of recommending A: it is the best *cheap* answer, not the *complete*
one, and this filing does not pretend otherwise.

**THE DISCRIMINATOR.** `[HIGH]`

> **Is the partial-commit harm an INPUT problem (the later call was already invalid when the batch
> arrived) or an ORDERING problem (any later failure, foreseeable or not, must not follow a
> commit)?**

- **INPUT** → the fault is that a knowably-bad call was executed after a good one. A pure pre-pass
  is exactly the right shape, and **A is right**.
- **ORDERING** → prediction is the wrong tool; the sequence itself must be forbidden. **C is right**
  for a cheap *inter-call* bound — but §3(vi) means C leaves the intra-call window open, so if the
  requirement is the ORDERING property **without exception**, only **B** delivers it, at the cost of
  a Class 1 route (§1).
- **Neither yet load-bearing** — the residual is cross-candidate and contingent, the default chain is
  single-candidate, and no incident has been observed → **D is right**, and D-0 is precisely its
  falsifier.

**A single operator sentence choosing INPUT, ORDERING, or "not yet" decides this fork.**

---

## §6 Pricing summary

| Reading | New public surface | Contract delta | Routing | Council | Witnesses owed | Residual left open |
|---|---|---|---|---|---|---|
| **A** *(rec.)* | 1 method (`validate`) on the executor | none | build leg under this Class 2 ratification | no (§7) | W-1, W-2, W-4, W-5 | policy-flip TOCTOU; store errors incl. the **intra-call** window (§3(vi)); §3(iv) |
| **C** *(runner-up)* | none (2 pre-pass predicates) | none | build leg under this Class 2 ratification | no (§7) | W-1, W-3, W-5, **W-6** | read-like `STANDARD_TOOL_CALL` rows (§3(i)); the **intra-call** window (§3(vi)); model-visible refusals |
| **B** | executor batch surface | **yes** — compensation semantics on C-MEM-08 / C-MEM-14 | **opens a CLASS 1 back-flow** (§1) — not buildable under this filing | **YES, before the Class 1 route** | **W-1, W-5, W-6** + ledger-compensation + migration witnesses. **NOT W-2/W-3/W-4** — those pin A's `validate()` wiring and C's positional refusal, behaviours a correct transactional B may deliberately not have (codex R2 [P2-b]) | none in principle; largest execution risk |
| **D** | none | none | docstring qualification at ratification (§4) | no | none (but D-2 wants the §3(iv) case-(3) probe) | the whole class, under a stated reopening test |

---

## §7 Council position — **PROBE-RESOLVED for A / C / D; OWED for B** `[HIGH]`

The row's `council` field says convening is *"Likely"*, keyed on one named tension: direction (2) is
*"a durable-write-semantics decision … with a blast-radius dimension — C10 paired with whichever
voice owns the IS-side memory operation ledger."* Root `CLAUDE.md` §10.9 (posture amendment 5)
requires an empirical probe at the most specific primary source **before** emitting a TENSION block.

**The probe was run** — the actual durable write path, end to end: `_write_note` → `capture_tool_event`
→ `_capture` → `write_record` / `append_memory_operation`; `_JSONL_BY_KIND`; `_append_jsonl`;
`_memory_id_for`; `write_record_guarded`; `cross_process_scope_lock`. Findings at §3(iii)–(iv).

**Probe outcome, split by reading.**

- **Under A, C or D: the tension does not exist.** None of them touches durable-write semantics at
  all — A adds a pure function, C adds a positional refusal in the dispatch pre-pass, D adds a
  docstring qualification. There is nothing for C10 (action-safety / blast radius) and the memory
  ledger owner to disagree about, because no write ordering, no record shape, and no ledger
  projection changes. Convening a dyad whose two voices agree in advance is the primary-collapse
  failure the posture amendments exist to prevent. **No convening owed.**
- **Under B: the tension is real and the probe did NOT dissolve it — it sharpened it.** §3(iv)
  establishes that the record shape is an append-only content-addressed JSONL with a
  content-derived ledger idempotency key, so "rollback" must be **compensating entries on a
  hash-chained append-only ledger**. That is exactly the C10 ⊥ ledger-owner axis the row named:
  blast-radius containment wants an undo; ledger integrity forbids rewriting or deleting a chained
  row. **A dyadic convening is OWED under Reading B, before its Class 1 back-flow route (§1) is
  opened.** §3(vi) sharpens this further: because the window is intra-call, B's compensation design
  must cover a *single* call's record-then-ledger ordering, not merely batch boundaries.

This is the `B-88` §7 shape — probe-resolved for the readings that need no contract change, owed for
the one that does.

---

## §8 Witness matrix for the build leg (including the PD-8 mutation probes)

Owed per reading (see §6). All are new tests unless noted; none exists at HEAD.

| # | Witness | Shape | Owed under |
|---|---|---|---|
| **W-1** | **The harm, made visible.** Drive a real `StandardMemoryToolExecutor` through the real pre-pass + batch loop with `[memory.write_note (valid), memory.read (no `memory_ref`)]`; assert the batch raises **and** that the tool-events ledger gained a record — i.e. the partial commit is asserted as **present**, not merely inferred | End-to-end through `_openai_memory_tool_result_messages`, not a unit call to `execute()`. This is the *baseline* the fix flips | A, B, C, D-2 |
| **W-2** | **A's closure.** Same batch, with `validate()` wired: assert the batch raises **before** any durable write — the ledger and the tool-events file are **unchanged** (assert on the durable surface, not on a call count) | Assert absence on the durable artifact; a mock-call-count assertion would pass on a path the store never sees | A |
| **W-3** | **C's closure + its stated cost.** (a) `[write_note, search]` is REFUSED before execution with the durable surface unchanged; (b) `[search, write_note]` still SUCCEEDS (the constraint is positional, not a ban); (c) `[write_note, write_note]` is refused | Both arms required — (b) is what stops the constraint from silently becoming "no writes in batches" | C |
| **W-4** | **A's parity pin — structural, and scoped to the per-tool ARGUMENT/BRANCH matrix, not to raise statements** (rewritten across codex R1 [P2-c] and R2 [P2-a], both accepted). The **preferred** discharge makes parity *unfalsifiable by construction*: `validate()` and `_execute_authorized` consume **one shared parsed/validated request representation**, so there is no second path to drift from — and under that discharge **no site cap applies**. Where it is not taken, the witness must cover the **per-tool argument matrix**: the same helper serves many fields (`_string_arg` alone is called for `query`, `note`, `memory_ref`, …), so a `validate()` can cover all **9** model-reachable *raise statements* while omitting an entire field's path. Enumerate **(tool × argument × branch)**, not raise sites and not helper names | Corrected twice, and the second correction matters: R1 fixed "helper names → call sites", R2 caught that the **9-site scope I then wrote is the wrong denominator** — 9 counts syntactic raises, which is not the coverage unit. Reading A's whole value rests on permanent parity, so this witness is load-bearing, not hygiene | A |
| **W-6** | **The intra-call residual (§3(vi)), asserted rather than hand-waved.** With a **single-call** `[write_note]` batch, force the operation-ledger append to fail after `write_record` has landed; assert the record IS durable while `execute()` raises `MemoryToolExecutionStoreError`. Repeat for `_append_standard_tool_call` failing after a successful `_execute_authorized` | New at codex R2 [P1-b]. This is the witness that stops Reading C from being *described* as closing a residual it cannot reach, and it is the acceptance evidence Reading B's guarantee is actually judged against | B, C *(as C's retained-residual pin)* |
| **W-5** | **§3(iv)'s FOUR-CELL matrix, executed rather than inferred.** For each of cases (1) different text, (2) same text/different model, (3) same text/same model name/different provider, (4) fully identical: assert (a) whether a new `memory_id` is derived, (b) the physical JSONL line count under that `memory_id`, (c) the `append_memory_operation` outcome (`APPENDED` / `IDEMPOTENT_NOOP` / raise), and (d) for any raise, the surfacing exception class and its `_classify_provider_exception` disposition | The whole matrix is marked `[MODERATE]` for want of execution. Case (3) is the only cell carrying the duplicate-line-plus-re-opened-staircase claim; **it must be run, not assumed**, and cases (1)/(2) are the ordinary ones whose "extra distinct note" outcome is what the harm statement rests on | A, B, C, and D-2's falsifier |

**Mutation probes (PD-8, Workflow v1.18 — green-alone is not proof).**

- **For A:** revert the `validate()` call in **each** pre-pass independently (OpenAI arm, then ollama
  arm) and confirm **W-2 fails in each case**. Reverting only one and seeing red proves the other
  arm nothing — the two loops are separate code paths (`:4187` and `:4823`), and a
  fix-one-arm-only regression is exactly the failure this workspace has hit before.
- **For C:** revert the positional predicate and confirm **W-3(a)** fails while **W-3(b)** still
  passes — the probe must show the predicate is what refuses, not something upstream.
- **For W-6:** the failure must be injected at the **ledger append**, with the record write left to
  succeed. A probe that fails the whole capture proves nothing about ordering — the point is that the
  record survives the ledger's failure, which only a targeted injection can show.
- **For W-1:** it is the *pre-fix* baseline, so it must be shown to FAIL after the fix lands (or be
  re-keyed to the post-fix expectation with the pre-fix behaviour recorded), not left asserting a
  harm that no longer occurs. Note W-1 and W-6 are **different** harms — inter-call and intra-call —
  and W-6 stays green under A and C by design, because neither closes it.

---

## §9 Cite re-verification at HEAD `496f0f4b`, and the drift found

Every cite in this filing was resolved by direct read at this HEAD. Counts recomputed with
`git grep -c` / direct enumeration. **Verified as cited, and matching the row's own 2026-08-05
refresh:** the six argument helpers (`_string_arg` `:678`, `_optional_string_arg` `:685`,
`_positive_int_arg` `:694`, `_allowed_kinds` `:703`, `_kind_from_memory_ref` `:764`,
`_promotion_kind` `:783`), the two denied-class sites (`_allowed_index_entry` `:516`,
`_read_record_by_ref` `:545`), `execute()` `:231` / `_execute_authorized` `:259`,
`write_record_guarded` `memory_store.py:298`, and the fail-fast branch
`retry_breaker_fallback.py:293` / `:312` / `:330`. **Counts:** 10 executor + 8 dispatch
`MemoryToolExecutionInputError` raise sites; **15** `MemoryToolExecutionDeniedError` sites (the row's
older "14" was already corrected to 15 by the `B-88` filing — confirmed 15 here); **1** production
consumer of `write_record_guarded`.

**DRIFT FOUND — 7 stale cites and 2 premise qualifications. None changes any disposition.**

| # | Claim | Verified at HEAD `496f0f4b` | Where it lives | Class |
|---|---|---|---|---|
| 1 | Row prose: Runtime spec §14.6 D2 at `Spec_Harness_Runtime_v1.md:3796` | **STALE, +284.** §14.6 heading is `:4069`; **D2 is `:4080`**. Text itself byte-verified unchanged | register prose | 3 |
| 2 | Row: the batch loops at `lifecycle/llm_dispatch.py` `~:4234` / `~:4865` | **Refined.** Function defs `:4229` / `:4860`; the `execute(` calls are `:4237` / `:4875`. The row's `~` is within tolerance but the exact lines are recorded here | register | 3 |
| 3 | **Shipped code:** `retry_breaker_fallback.py:301` cites the executor's argument validation at `memory_tool_executor.py:549-553` | **STALE.** That is `_string_arg`'s pre-B-84 home; at HEAD it is `:678`–`:682` | **code docstring** | 3 |
| 4 | **Shipped code:** `retry_breaker_fallback.py:302` cites the dispatch-side memory context/schema invariants at `llm_dispatch.py:3626-3641` | **STALE.** At HEAD `_standard_memory_tool_context`'s invariants are `:4333`–`:4348` (and the module moved to `lifecycle/`) | **code docstring** | 3 |
| 5 | **Shipped code:** `retry_breaker_fallback.py:313`/`:315` cite `memory_tool_executor.py:424-435` and `:446-449` for the denied-class sites | **STALE.** At HEAD `_allowed_index_entry` `:516`, `_read_record_by_ref` `:545` | **code docstring** | 3 |
| 6 | **Shipped code:** `memory_tool_executor.py:716` cites the fail-fast tuple at `retry_breaker_fallback.py:326-334` | **Off by one.** The `isinstance` block is `:325`–`:333` | code comment | 3 |
| 7 | **Shipped code:** `memory_tool_executor.py:383`/`:390` cite `memory_capture.py:541-552` / `:553-560` as `_capture`'s `except` around `write_record` + `append_memory_operation` | **STALE.** Those lines are now `capture_tool_event`'s content dict + its `_capture` call. The real sites: `write_record` `:818`, `append_memory_operation` `:820`, the `FAILED` construction `:899` | **code docstring** | 3 |
| 8 | Row: the committed prefix is *"the earlier write"* | **QUALIFIED — understated.** Every successful call appends a `STANDARD_TOOL_CALL` ledger row (`memory_tool_executor.py:247` → `:634`), read-only tools included (§3(i)) | register framing | 3 |
| 9 | Row 2026-07-30 re-price: U-MEM-27's seam means *"make the whole batch atomic no longer starts from nothing"* | **QUALIFIED — cuts both ways.** True for the lock; **false as stated for the seam**: `write_record_guarded` is single-record CAS and the memory-tool write path does not use it at all (§3(iii)) | register framing | 3 |

Items **3–7 are stale cites in shipped source**, not in the register — a drift surface the row's own
2026-08-05 refresh (which corrected the *register's* cites) did not reach. They are recorded here,
not repaired: this PR is doc-only, and repairing a code comment is a build-leg edit. **The build leg
under any reading that touches these files should repair them in the same pass.**

**One thing this filing did NOT ground, stated rather than assumed:** the §3(v) ollama-SDK
aggravator was inherited from the row's registration-time measurement and was **not re-verified**
against the currently-locked SDK. No reading turns on it.

---

## §10 Sequencing, and what each leg owes

| Leg | Owes | Gate |
|---|---|---|
| **This filing** (doc-only) | This document. Row stays `registered_finding`; **no register edit, no `pr:` stamp, no snapshot change** | — |
| **Ratification** | Operator selects A / B / C / D via `AskUserQuestion`; a `§11 RATIFICATION` section is appended here; the register row's `pr:` pointer is set and its `close_out` gains the outcome. **Under D, the `_PreparedMemoryToolCall` docstring qualification (§4, Reading D) is owed AT THIS LEG**, not deferred | Operator |
| **Council** *(B only)* | Dyadic C10 ⊥ memory-ledger-owner convening per §7, **before** the Class 1 route is opened | Follows ratification |
| **Class 1 route** *(B only)* | Selecting B opens a **Class 1 back-flow** (§1), not a build: halt + operator-authorized routing to the Phase 5 memory-spec channel per root `CLAUDE.md` §4.3, then `Spec_Memory_Substrate_v1.md` compensation semantics + `Implementation_Plan_Memory_Substrate_v1.md` U-MEM-16 amendment + clearance markers per §4.5, one per artifact actually changed | Operator (back-flow authorization) → X-AL-3 guard + adversarial review |
| **Build leg** *(A or C directly; B only after its Class 1 route clears)* | The code change + the §8 witnesses **for that reading** (§6's per-reading column, not all of W-1…W-6) + the §8 mutation probes + **W-5's four-cell matrix executed and its answers recorded on the row** + the §9 items 3–7 cite repairs in the touched files | CI + `merge-gate` 3-lens (code-touching) |

---

## §11 Out-of-family review record (`just codex-review`, branch-vs-main)

*(Rounds are recorded here only after they have actually run.)*

- **R1 — 4 findings (3 [P2] + 1 [P3]), ALL accepted and fixed.** Two were **premise-level**, not
  presentation-level, and both corrected claims that would have biased ratification:
  - **[P2-a] Replay identity was wrong.** The first pass asserted that an identical cross-candidate
    `write_note` collides on the ledger idempotency key and raises. Verified false at
    `memory_operation_ledger.py:476`–`:539`: the append compares an 18-field equivalence payload
    (including `provider` and `model`, excluding `timestamp`) and returns `IDEMPOTENT_NOOP` on a
    match, raising only on same-key/different-payload. Codex also identified an identity input the
    first pass missed — `summary_model` participates in the hashed content
    (`memory_capture.py:542`), and the model is rebound per candidate. §3(iv) rewritten as a
    **four-cell matrix**; the ordinary cases produce an *extra distinct note*, and the original
    duplicate-line-plus-re-opened-staircase claim survives only as the narrow same-model-name/
    different-provider cell. W-5 and D-2 re-scoped to match.
  - **[P2-b] "Cross-candidate only" understated the default-path harm.** Reading D's D-1 implied the
    residual was contingent on a multi-candidate chain. The **partial commit is deterministic on the
    default single-candidate chain**; only the *duplication* is cross-candidate. D-1 corrected and a
    severity-vs-reachability paragraph added, because the conflation biased toward deferral.
  - **[P2-c] W-4 could not enforce the invariant Reading A depends on.** A helper-name enumeration
    cannot detect a new call to an existing helper for a new argument, nor a new inline raise —
    either would let `execute()` reject what `validate()` accepts while the test stayed green. W-4
    rewritten to prefer a **single shared parsed/validated request representation** (parity
    unfalsifiable by construction), with a call-site-and-branch comparison as the fallback discharge.
  - **[P3] Raise-site count.** `_execute_authorized:271`'s unsupported-tool branch is unreachable
    from model input (`tool_name` is a `MemoryToolName`; all five members dispatch at `:261`–`:270`).
    Filing now distinguishes **10 syntactic / 9 model-reachable**, and Reading A's coverage and W-4's
    scope are stated against 9.
  - **Zero findings declined at R1.** The recommendation (A), runner-up (C) and the INPUT-vs-ORDERING
    discriminator were untouched by all four.
  - *(Self-caught during the R1 pass, not a codex finding: §3(iv)'s heading said "THREE CASES" over a
    four-row matrix. Recounted and fixed — the count-drift-per-round discipline applied to my own
    edit.)*

- **R2 — 4 findings (2 [P1] + 2 [P2]): 3 accepted, 1 PARTIALLY accepted with the decline half
  grounded and pinned.** One was a genuine defect in a reading's central claim.
  - **[P1-b] ACCEPTED — Reading C's safety claim was false, and the correction created a new
    finding.** C claimed the positional rule made record-level commit-then-raise unreachable and
    closed A's store-error residual. Codex showed the window is **intra-call**: `_capture` writes the
    record (`memory_capture.py:818`) before appending its ledger entry (`:820`), and `execute()` runs
    `_execute_authorized` (`:240`) before `_append_standard_tool_call` (`:247`) — so a **single-call**
    batch can commit then raise, and no positional rule over a batch can reach it. Verified by direct
    read. Promoted to its own finding **§3(vi)**, C's claim retracted and bounded to the *inter-call*
    sequence, **new witness W-6** added as C's retained-residual pin, and the four downstream
    consequences propagated (§5's note-against-recommendation, the ORDERING branch of the
    discriminator, §6, §7, §10). **This raised Reading B's relative value** — B is now the only
    reading that reaches the intra-call window.
  - **[P2-a] ACCEPTED — W-4's scope was still the wrong denominator after R1's fix.** R1 moved W-4
    from helper *names* to call sites, and I then scoped it to the **9** model-reachable *raise
    statements*. Codex correctly caught that 9 raises is not the coverage unit: `_string_arg` alone
    serves `query` / `note` / `memory_ref` / …, so a `validate()` can hit all 9 raises and still omit
    a field's path. W-4 re-scoped to the **(tool × argument × branch)** matrix, with the shared-parser
    discharge carrying **no** site cap.
  - **[P2-b] ACCEPTED — §6 gave Reading B impossible acceptance criteria.** The summary said B owes
    "all of W-1…W-5", but W-2 pins A's `validate()` wiring, W-3 pins C's positional refusal, and W-4
    pins A's parser parity — none of which a correct transactional B need have. B's row now reads
    **W-1, W-5, W-6 + compensation + migration**, consistent with the per-witness `Owed under` column.
  - **[P1-a] PARTIALLY ACCEPTED; the reclassification half DECLINED with grounds.** Codex is right on
    the citation: `.claude/skills/phase-7-back-flow-routing/SKILL.md` §2.2 says a Class 2 fork records
    *"no design-phase artifact revision"*, so Reading B's contract edit cannot ride this filing's
    authority. **Accepted:** §1 now states explicitly that selecting B **opens a Class 1 back-flow
    route** rather than a build leg, and §7/§10 were aligned. **Declined:** reclassifying the *filing*
    as Class 1 — because (i) §2.2's **trigger** row is satisfied exactly (there is no architectural
    defect: §3(ii) shows there is no contract to violate, and what is owed is a selection among four
    options), and (ii) **10 of 19 `class_2_fork_b*` filings carry a spec leg**, including
    `B-88`/`B-93`/`B-96`/`B-97a`/`B-98`/`B-104`/`B-107`, four of them in this same standing
    ratification batch — so reclassifying here would silently relitigate nine landed precedents on
    one review comment. The taxonomy-row-vs-practice divergence is recorded at §1 as a real issue
    belonging to the routing skill's next revision, not to B-84.
