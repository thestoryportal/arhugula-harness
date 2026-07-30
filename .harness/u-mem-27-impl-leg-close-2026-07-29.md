# U-MEM-27 impl leg — close record (2026-07-29)

The implementation leg of `B-92`'s ratified `Spec_Memory_Substrate_v1.md` v1.2 contracts
(C-MEM-10 reading B — flag plus gate — and the C-MEM-03 tri-state `captured_cross_family`
field). Branch `u-mem-27-cross-family-promotion-gate`. This is the record the U-MEM-25
closeout evidence packet and future sessions cite; it carries what the commit messages and
the register rows do not.

## Slices

| Slice | Commit | Content |
| --- | --- | --- |
| 1 + 2 | `ef201f36` | Envelope tri-state (`CapturedCrossFamily`, `MemoryRecordEnvelope.captured_cross_family`) + the write-side ORIGIN-AWARE derivation across `_capture` / `_record`; hash-inertness and legacy-read witnesses. |
| 3a | `5447b653` | Entry-point cross-family gate at BOTH promotion surfaces, the illegal-pair validator, the reserved-flag re-derivation, the durable content carrier, and the redaction RESET. |
| 3b | `f658668f` | Frozen-snapshot activation boundary, worst-value aggregation, per-branch fail-closed handling, choke-point normalization across all four `_persist_decision` callers, and commit binding via a guarded conditional write. |
| 4 | this commit | Closeout-evidence refresh (six rows), window-2 close, `B-92` register flip, this note. |

## Re-grounding at arc open

Every plan cite consumed by this arc was re-verified at impl HEAD `d95212e2`
(`ops: roadmap status refresh post-#1158`, the commit the arc branched from). The spec leg
had landed one commit earlier at `1eba1ae0`; `git diff 57f840b6..HEAD -- harness-*` was
**empty** at arc open, so no implementation surface moved between the spec leg's own
grounding sweep and this arc — the sweep held **verbatim** and did not need re-derivation.
Beyond the line-level cites, each slice agent re-verified the structures it touched by
**direct read** rather than by trusting the plan's rendering of them (the
`[[cleared-spec-resolves-it-before-first-principles-fix]]` discipline): the `_capture` /
`_record` parameter flow, the `PromotionCandidate` validator, the four `_persist_decision`
call sites, and the store's lock structure were each read at HEAD before being changed.

## The `event_kind` → content-origin table as implemented

The derivation is origin-aware and split by where its inputs live: `_capture` — the one
method holding `event_kind` — determines the CONTENT-ORIGIN disposition and passes that
disposition into `_record`, which holds the call `provider` and the resolved scope and
computes the final tri-state. Origin **gates** the family comparison: a non-dispatch-derived
origin yields `unknown` and the comparison is never consulted.

The disposition has **two dimensions**, not one (the codex R3 correction below): the
`event_kind` table applies only when the capture is not redacting its content.
`MemoryCaptureMode.REDACTED` overrides every row to `UNDETERMINED`, because
`_captured_text` replaces the summary wholesale with a harness-authored constant. Both
dimensions are resolved at `_capture` by `_content_origin_for(event_kind, capture_mode)`;
the final tri-state is still computed only at `_record`.

| Capture mode | Origin disposition | Why |
| --- | --- | --- |
| `REDACTED` (any `event_kind`) | `UNDETERMINED` | Content is the harness-authored `[redacted]` constant; no dispatch produced it. Overrides the table below in **both** directions — a same-family redacted capture must not land `false`, a cross-family one must not land `true`. |
| `FULL` / `SUMMARIZED` / *(none)* | per the `event_kind` table below | The stored content is the caller's own material. |

| `event_kind` | Origin disposition | Why |
| --- | --- | --- |
| `turn_completion` | `DISPATCH_DERIVED` *(unless `REDACTED`)* | The stored `response_summary` is computed from the actual provider response, notwithstanding its `SummarySource.HARNESS_RULE` label. |
| `tool_event` | `DISPATCH_DERIVED` *(unless `REDACTED`)* | Tool-event content is produced by a completed dispatch. |
| `run_start` | `UNDETERMINED` | Written by `compose_for_dispatch` **before** any provider call; its provider is a *selection*, not a result. |
| `run_close` | `UNDETERMINED` | Post-dispatch in timing, but its content is run metadata describing no provider-produced output. |
| `provider_route` | `UNDETERMINED` | Routing metadata, not dispatch output. |
| `failure_observation` | `UNDETERMINED` | Observation metadata; no completed dispatch produced the stored content. |
| `compaction` | `UNDETERMINED` | Harness-authored compaction content; assigned by the per-invocation rule, not by a claim about the underlying records. |
| *(any unmapped kind)* | `UNDETERMINED` | The mapping lookup falls back to `UNDETERMINED`, so a writer added later inherits the fail-closed value rather than a determination. |

The criterion is stated over **content origin**, never over method names and never over
`summary_source` — which is why the production turn path lands a real determination while
`capture_run_close`, taken after a completed same-family dispatch, lands `unknown`.

## Commit-binding mechanism — the chosen mechanism and why

The plan leaves the mechanism to implementation discretion but requires the leg to **state
which it chose and why** rather than leaving it implicit. Recorded verbatim as the slice-3b
implementation decision:

> I chose a generic guarded conditional write executed inside the store's own write locks — a
> new `CanonicalMemoryStore.write_record_guarded(record, *, precondition)` that evaluates the
> caller-supplied predicate and performs the write it authorizes without releasing either
> write lock in between, raising `MemoryStoreGuardedWriteConflictError` when the predicate no
> longer holds (which the service converts to `PromotionProvenanceChangedError`). A
> version/generation token is unavailable: the store exposes none, and `memory_id` cannot
> serve as one precisely because the envelope is hash-inert — a rewrite carrying a different
> `captured_cross_family` collides on the same id, which is the very reason the race is live.
> A lock spanning decision-and-write would only pretend atomicity if it were
> promotion-service-local, since the capture writers that append new provenance lines do not
> hold any service lock; the only locks the mutating writers actually take are the store's own
> `_FILE_WRITE_LOCK` and `_JSONL_WRITE_LOCK`, so the honest span is those. That is what the
> guarded write holds — both, in a documented `_FILE_WRITE_LOCK → _JSONL_WRITE_LOCK` order,
> because a determination-bearing source can reach disk through either branch. Both locks
> became `threading.RLock` for re-entrancy, since the precondition re-reads through the
> store's own read path and the wrapped `write_record` re-takes them; no pre-existing path
> nests them at all, so the single ordering rule keeps the pair acyclic. Round-10's constraint
> is met because the verification is not a step the runtime performs and then follows with a
> separable `write_record` call — it is inside the same lock-held region as the write. The
> store side stays free of promotion semantics (an opaque callable, per carrier-home
> discipline), and the compared value is the snapshot's decision-bearing projection (`gated`),
> not raw equality of every per-source tri-state. **[SUPERSEDED at Codex round 2 — see the
> "Codex round 2" section below. The compared value is now the EXACT per-source provenance
> vector; the projection reading narrowed the plan's literal `:1022` obligation and is
> retracted. The rest of this quoted paragraph stands.]** Scope stated honestly: these are in-process
> locks, so the guarantee is exactly as strong as the store's existing write atomicity and
> makes no cross-process claim. The guard is applied to the activation path only — a
> `PROPOSED` or `DENIED` write authorizes nothing, so a concurrent source append must not be
> able to make a denial fail; those writes still state the snapshot's re-derived mark, they
> are simply not conflict-bound to it.

## Slice-1 discrepancy findings

Three findings surfaced while grounding the write side, recorded because each is a place the
plan's rendering and the code at HEAD do not line up one-to-one:

- **`capture_run_close` has no production caller at HEAD.** The method exists and is
  exercised by tests, but no production path invokes it. Its `UNDETERMINED` disposition is
  therefore correct *and* currently unexercised in production — worth knowing before anyone
  reasons about run-close provenance from the origin table alone.
- **`compaction` is assigned `UNDETERMINED` by the per-invocation rule**, not by a claim that
  compaction output can never be dispatch-derived. The rule classifies the *capture
  invocation's* content origin; compaction content is harness-authored at the invocation, so
  the disposition follows from the same rule as the run kinds rather than from a special case.
- **The redaction RESET obligation was routed out of slice 1 and landed at slice 3a.** The
  plan lists it under the C-MEM-03 forward-only material, which reads as write-side work, but
  the reset lives in `MemoryRedactionService._replacement_content` / `_transition`
  (`harness-is/src/harness_is/memory_redaction.py`) alongside the rest of the transition
  surface slice 3a owned. It landed there, with both its witnesses.

## Slice-3b deliberate deviation

The **single-snapshot witness** mutates the source's `captured_cross_family` from `true` to
`unknown` — a mutation that cannot cross the gating boundary. That is deliberate: for this
witness the **resolution counter** is the load-bearing half (exactly one resolution per
decision, with the gate and the persisted mark agreeing), and a boundary-crossing mutation
would confound it with the commit-binding outcome. Boundary-crossing mutations are owned by
the **commit-binding witness** (`false` → `true` after the snapshot but before the durable
write, which must not auto-activate), and its `test_a_mutation_that_cannot_change_the_decision_still_commits`
sibling pins the other side — a mutation that leaves the decision-bearing projection intact
must still commit, so the guard is not a blanket refusal.

## Pre-existing tests updated at slice 3b

Two tests predating this unit were updated rather than left failing, both for the same
reason and both with the behavioural note recorded in the test source:

- `harness-runtime/tests/test_memory_promotion_review.py` — its `_store` fixture now seeds a
  `false`-provenance source record for the fabricated `_SOURCE_MEMORY_ID` the U-MEM-09
  candidates cite.
- `harness-runtime/tests/test_memory_plane_boundary.py` —
  `test_promotion_and_injection_are_independently_settable_policy_decisions` now names a
  genuinely resolvable `false`-provenance source instead of an empty `source_memory_refs`.

**The behavioural note both carry:** a production caller approving a candidate whose sources
are unresolvable is now **withheld from automatic activation**. That is the new contract
working, not a defect — those tests always *meant* an auto-promotable candidate to be a
same-family one, and the seed states that intent explicitly. The operator-approved path
remains open for exactly such a candidate.

## Closeout

- All six `PENDING — U-MEM-27` markers in `.harness/u-mem-25-memory-closeout-evidence.md`
  lifted (C-MEM-03, C-MEM-10, R-MEM-01, R-MEM-05, R-MEM-09, R-MEM-14); the packet's window-2
  version-scoping paragraph closed the way the U-MEM-26 leg closed window 1 (retained as
  historical record, relabelled CLOSED, scope advanced to spec v1.2 / plan v1.2 /
  U-MEM-01..27); `just memory-closeout-check` re-run green with the refreshed rows in place.
- `B-92` flipped to `closed` at `.harness/forward-register.yaml` with all five LIVE NEXT STEP
  parts discharged; snapshot counts and `identity_digest` bumped in the same edit;
  `just forward-register-check` green.
- Bounds carried forward unchanged, each needing its own later amendment: the field answers
  **present/absent only** (not by-family), and **aggregate-run** provenance is not
  representable per-record.

## Codex round 1 — two findings against the slice-3b surface

An out-of-family `just codex-review` pass over the slice-3b surface returned two findings.
Both are resolved in code; neither required a spec or plan amendment.

### [P2] Source-read I/O failures escaped the fail-closed snapshot — FIXED

`_resolve_source_provenance` (`harness-runtime/src/harness_runtime/memory_promotion.py`)
enumerated four unresolvable branches and caught only `LookupError` and `ValueError`. A
source that is on disk but *unreadable* — an unreadable file or parent directory, a vanished
mount, EMFILE — raises `OSError` (`PermissionError` is one), which propagated straight out of
`_provenance_snapshot`. Because **every** decision operation takes the snapshot first, that
aborted `propose_for_review` and `deny` — neither of which authorizes anything — and aborted
an operator-approved `approve` too, which the plan (`:1020`) requires to stay OPEN. The
finding is asymmetric in exactly the wrong direction: it converts a fail-closed reading into
a fail-*shut* one.

Fixed by adding a fifth branch, `except OSError`, returning `UNKNOWN` like its four siblings —
written out per-branch rather than folded into a catch-all, matching the module's own stated
discipline. Witness: `test_fail_closed_on_a_source_read_that_raises_an_io_error`
(`harness-runtime/tests/test_u_mem_27_activation_boundary.py`), parametrized over
`PermissionError` and a non-permission `OSError`, asserting all four outcomes separately —
automatic activation withheld, `propose_for_review` completes carrying the mark, `deny`
completes, operator-approved `approve` reaches `ACTIVE` carrying the mark. Modelled at the
`PromotionDecisionStore` seam rather than by `chmod`, so the branch is deterministic
regardless of the privileges the suite runs under. Mutation-probed: with the `except OSError`
branch removed both arms fail with the raw errno.

### [P1] The guarded write was in-process only — FIXED (cross-process lock built)

Codex reproduced the interleaving directly: `precondition_saw=false`, `source_at_commit=true`,
`activation_committed=True`. Slice 3b's docstring scoped the guarantee honestly to one
process, but the grounding pass found that honest scoping is not discharge here, because the
topology is real:

1. **A house cross-process primitive exists.** `harness-is/src/harness_is/cross_process_ledger_lock.py`
   (B-40, redesigned at B-46) — POSIX `fcntl.flock`, same-host, per-*canonical-file* with a
   parent-directory lock for the absent-file state, plus a reentrant in-process `_DirLock`
   face; Windows degrades to a no-op (registered B-45 gap).
2. **The store's own writers were NOT cross-process coordinated.** `_append_jsonl`
   (`memory_store.py:492`) and `_write_file_atomically` (`:481`) took only module-level
   `threading.RLock`s. Only the durable *memory-ops ledger* was hardened (B-40, flock);
   the canonical record store was not. So the finding was **not** asking the guarded write to
   be stronger than every other write in the store — it was asking the store's write plane to
   match the sibling ledger's already-shipped posture.
3. **Shared-root multi-process is real at HEAD, not hypothetical.** The root is repo-derived
   and stable — `automatic_memory.py:127` resolves `config.memory.root_path or
   (config.repository_root / ".harness" / "memory")`; the unbound default is the relative
   `.harness/memory` (`memory_path_registry.py:18`, `:214`); nothing in `src` derives a
   per-run temp root. Three console scripts ship (`harness-runtime/pyproject.toml:91-99`), and
   both `harness daemon` (which bootstraps the in-process MCP server on a deliberately
   de-PID-ed host-global socket) and the default one-shot `harness run` execute the same
   `run_bootstrap` → stage-5 → `CanonicalMemoryStore` against the same `repository_root`.
   `Spec_Memory_Substrate_v1.md` states **no** process model (one "in-process" hit, at `:57`,
   in a trust-boundary sentence), and the workspace already adjudicated that silence at B-40
   rounds 2-4 — a round-4 Codex pass corrected "dormant" to **LIVE** on exactly this
   two-concurrent-`harness run` ground.

**Branch taken: build it.** Per the decision rule's first branch — house primitive exists and
the topology is real. What is reusable is the primitive's `_DirLock` building block (per-path
`flock` EX + reentrant in-process face), not its file-lock context managers: those key on ONE
canonical file, and this critical section's read set is discovered dynamically inside a
caller-supplied predicate, so there is no single file to key on and locking the discovered set
member-by-member reintroduces a lock-ordering problem. Added `cross_process_scope_lock(root)`
to the same module — a generic, promotion-free exclusive lock over a directory TREE, keyed on
a provisioned `.cross-process-scope.lock` file (a dedicated inode, so scope holders are not
coupled to unrelated ledger writers in the same directory), reentrant per thread, same-host,
Windows no-op — identical posture to its siblings.

Wired in `CanonicalMemoryStore` via `_write_scope()` (`memory_store.py`), taken by **both**
`write_record` (covering `_append_jsonl` for the JSONL determination-bearing kinds AND
`_write_file_atomically`, the atomic-replace branch that redaction rewrites reach through
`memory_redaction.py:271`) and `write_record_guarded` (covering precondition + write). The
in-process `RLock` pair is retained beneath it — cheap same-process exclusion plus the
re-entrancy the guarded section needs. Documented lock order, taken identically at both entry
points: **scope lock → `_FILE_WRITE_LOCK` → `_JSONL_WRITE_LOCK`**; no store path nests a
canonical-file ledger lock inside a scope hold (`append_memory_operation` is a sibling call,
never nested in a write), so the set stays acyclic. `MemoryPathRegistry.canonical_root` was
added as the one new accessor this needs.

Witness: `harness-is/tests/test_memory_store_cross_process_guard.py::test_a_second_process_cannot_append_between_precondition_and_commit`
— a genuine second OS process (`multiprocessing` fork context, forked BEFORE any lock is
acquired per the workspace fork+lock hazard, gated by `ctx.Event`) holds a guarded section
open across its precondition while this process attempts the superseding append. Thread-based
witnesses cannot pin this: every thread here contends on the same `_DirLock` in-process face
and would pass on the `RLock`s alone. The append BLOCKS for the section's duration, and the
store's own semantic-index ledger — appended inside the same section as each record — gives
the committed order `[source_v1, target, source_v2]`, i.e. the activation committed strictly
before the superseding line. The superseding record is the real colliding shape: same content,
different `captured_cross_family`, therefore the same hash-inert `memory_id`, appended
last-wins. Mutation-probed: with `_write_scope()` removed from both write entry points the
append lands inside the guarded section and the witness fails on its blocking assertion.

The slice-3b `write_record_guarded` docstring's SCOPE paragraph and the `_commit_record`
mechanism narration were both corrected in place — the earlier "makes no cross-process claim"
and "the capture writers do not hold it" statements are now false of the shipped code, and
carrying them forward would have been a stale-carry.

## Codex round 2 — two P2 findings

A second out-of-family pass returned two findings, both on surfaces this leg owns. Both are
resolved in code; neither required a spec or plan amendment.

### [P2] The commit binding compared a projection, not the exact provenance — FIXED

The guarded-write precondition compared only the snapshot's `.gated` projection. The plan's
obligation at `Implementation_Plan_Memory_Substrate_v1.md:1022` is literal and unqualified —
"the activation write must not commit against a source whose recorded provenance changed after
the snapshot; on change the invocation fails or retakes the snapshot and re-decides." It says
*changed*, not *changed the decision*. The projection reading therefore narrowed the contract,
and two classes of real change committed against a stale snapshot: a single source moving
`true` -> `unknown` (both gate, same mark), and multi-source changes that preserve the
worst-value aggregate. **The round-1 "decision-bearing projection" rationale is retracted, not
defended** — the literal text governs, and the mechanism paragraph quoted earlier in this
document now carries a bracketed superseded-note pointing here.

Fix: `_EffectiveProvenance` gained a `per_source` field — the tri-state of every cited source,
positionally aligned with `candidate.source_memory_refs` — and the precondition compares that
vector. ANY difference is a conflict, surfaced as the existing
`PromotionProvenanceChangedError` (fail rather than retake-and-re-decide: the simpler of the
two shapes the plan permits, and the one already wired through the service and its witnesses).

One level down, the same defect was closed with it. `_resolve_source_provenance` now returns
`CapturedCrossFamily | None`, with `None` marking UNRESOLVABLE, kept DISTINCT from a source
whose stored value literally is `unknown`. Collapsing the two would have re-introduced a
compare-a-projection hole: a source that was readable at the snapshot and is unreadable at
commit HAS changed its recorded provenance, and both readings resolve to `unknown`. `None`
aggregates exactly as `unknown` does, so no gate, mark, or fail-closed behaviour moves —
`_aggregate_provenance`'s middle test became "any value that is not `false`", which is the
same predicate stated over the wider domain.

Test consequences, all three handled explicitly rather than by loosening assertions:

- `test_a_mutation_that_cannot_change_the_decision_still_commits` **encoded the narrowed
  reading** and is inverted + renamed to
  `test_a_mutation_that_cannot_change_the_decision_is_still_a_conflict`, asserting the refusal
  (and that neither store was written), with `:1022` quoted in its docstring and its
  predecessor named as superseded rather than silently replaced. It refuses even an
  operator-approved activation — the operator attested to the provenance the snapshot showed
  them, which is no longer what the store records.
- `test_one_service_call_resolves_the_cited_source_exactly_once` used a `true` -> `unknown`
  `after_first_read` mutation that now conflicts before reaching its assertions. Its mutating
  arm is retired (`mutate_to=None`) and the docstring states why: under the exact binding no
  mutating arm can reach those assertions, and the resolution COUNTER carries the
  single-snapshot property unaided — a two-lookup implementation shows 2 whether or not the
  value moved.
- Two NEW witnesses pin the cases a re-narrowed implementation could otherwise pass:
  `test_a_multi_source_change_preserving_the_aggregate_is_a_conflict` (two sources SWAP
  `true`/`false`; every scalar projection — aggregate, gate, persisted mark — is preserved, so
  only a vector comparison sees it) and `test_a_source_that_becomes_unresolvable_is_a_conflict`
  (stored `unknown` becomes unreadable; only the `None`/`unknown` distinction sees it). A new
  `_RewritingSourceStore` double drives the first through the REAL store, so the precondition
  re-reads genuinely re-recorded provenance rather than a double's bookkeeping.

Mutation probes, three, each isolating a different half: reverting the precondition to
`.gated` fails all three binding witnesses; collapsing `None` into `UNKNOWN` in the snapshot
fails **exactly** `test_a_source_that_becomes_unresolvable_is_a_conflict` and nothing else.

### [P2] Malformed stored sources raising `TypeError` escaped the handler — FIXED

Same class as round 1's [P2], one exception type over: a stored payload that fails
deserialization on a TYPE rather than a value — a serialized `content_hash` of `null` reaching
`_bytes32_from_json`, an envelope field of the wrong JSON type — raises `TypeError`, which is
neither `LookupError`, `ValueError`, nor `OSError`. It escaped `_resolve_source_provenance`
and, because every decision operation snapshots first, aborted `propose_for_review`, `deny`,
and operator-approved `approve` alike.

Fixed with a sixth per-branch arm, `except TypeError` -> unresolvable, keeping the written-out
style. Witness `test_fail_closed_on_a_source_read_that_raises_a_type_error`, parametrized over
two `TypeError` shapes, asserting the same four outcomes separately as the branch-5 witness.
Mutation-probed: with the branch removed both arms fail with the raw `TypeError`. The
`_IOFailingSourceStore` double was moved up to the doubles section (it now has three users)
and gained a `fail_after` counter, which is what lets one double model "readable at the
snapshot, unreadable at commit".

## Codex round 3 — one P1 against the write-side derivation

### [P1] `REDACTED` captures recorded a determination against harness-authored content — FIXED

**Finding.** The origin disposition was resolved from `event_kind` alone. Under
`MemoryCaptureMode.REDACTED` a turn or tool capture stores no dispatch output, yet the
mapping still classified the invocation `DISPATCH_DERIVED` — so a same-family redacted
capture recorded `captured_cross_family=false` against content the provider never produced,
and a cross-family one recorded `true`.

**Grounding, by direct read at HEAD — wholesale replacement, not partial masking.**
`_captured_text` (`harness-runtime/src/harness_runtime/memory_capture.py:1216-1219`) is the
whole redaction mechanism:

```python
def _captured_text(value: str, mode: MemoryCaptureMode) -> str:
    if mode is MemoryCaptureMode.REDACTED:
        return _REDACTED_SUMMARY
    return value
```

It **discards `value` entirely** and returns the module constant `_REDACTED_SUMMARY =
"[redacted]"` (`:57`). No substring is preserved, so nothing about the provider's output
survives into the record. It is applied to `prompt_summary` **and** `response_summary` at
`capture_turn_completion` (`:471-472`) and to `summary_text` at `capture_tool_event`
(`:524`), and each method then computes `summary_hash` over the **already-redacted** text
(`:482`, `:534`) — so even the digest carries no dispatch material. The residual
dispatch-adjacent keys are `token_usage` (metering counts) and the refs/ids, none of which
is provider-produced *content*.

Both are live production paths, not hypotheticals: `CaptureDecision.CAPTURE_REDACTED` maps
to `MemoryCaptureMode.REDACTED` at `memory_tool_executor.py:882-883` (reached by
`_write_note`, the tool-event path) and at `automatic_memory.py:663-664` (the turn path).

**Spec text that governs — verbatim, `design-substrate/Spec_Memory_Substrate_v1.md`.**

- C-MEM-03 derivation rule, §"…keyed to the content's ORIGIN" (`:234`): *"A determination -
  `true` or `false` - is recorded **only where the stored content derives from the output of
  a completed provider dispatch**. Everything else is `unknown` … the field states whether
  *the content in this version* came from a leg whose family differed, so where no dispatch
  produced the material there is no such leg, and `false` would assert an equality that was
  never tested against anything."*
- The per-invocation qualification the fix turns on (`:238`): *"The signal is the **capturing
  caller's own knowledge on THIS invocation** … This is a property of the individual call,
  not of a stored field and not of the capture method's name. Where every production
  invocation of a given capture method shares one origin, a method-level mapping is a sound
  way to realize the rule; where a method's invocations can differ … the method name is
  **not** a sufficient signal."* `REDACTED` mode is exactly such a per-invocation variation,
  so the `event_kind`-only mapping was an unsound realization of the rule.
- The direct analogue, the transition-reset paragraph (`:252`): *"it substitutes
  harness-authored replacement material for the content the record held. Because this field
  describes **the stored version**, a preserved `true` or `false` would then assert that the
  replacement material came from the original dispatch, which is false on its face and
  contradicts both the stored-version rule and the content-origin rule."* Invariant `:271`
  states the same over durable transitions. The redacted **capture** is the capture-time twin
  of that case: the same harness-authored replacement material, arriving one step earlier.

Every source supports the same reading, so the fix was applied rather than reported back.

**Fix.** A second origin dimension, resolved where the first already is. NEW
`_content_origin_for(event_kind, capture_mode)` returns `UNDETERMINED` for
`MemoryCaptureMode.REDACTED` and otherwise defers to `_CONTENT_ORIGIN_BY_EVENT_KIND`; it is
now the only reader of that mapping. `_capture` gained a private
`capture_mode: MemoryCaptureMode | None = None` parameter — a **private** method, so the
plan's "no `capture_*` signature changes" constraint is untouched — threaded from the four
public methods that can replace their content through `_captured_text`
(`capture_turn_completion`, `capture_tool_event`, `capture_failure_observation`,
`capture_compaction_event`). The value threaded is the **effective** `mode`
(`mode = capture_mode or self._capture_mode`), not the argument, so a recorder bound with
`capture_mode=REDACTED` is covered too. The run kinds pass nothing; they cannot redact and
are `UNDETERMINED` regardless. The final tri-state is still computed only at `_record` — the
plan's non-discretionary placement is unchanged.

All four `_captured_text` callers declare the mode, including the two currently
`UNDETERMINED` by `event_kind`, so a future origin reclassification of `compaction` or
`failure_observation` inherits the override automatically instead of silently regressing.

**Witnesses** (`harness-runtime/tests/test_u_mem_27_capture_provenance.py`), four new:

- `test_redacted_same_family_turn_capture_lands_unknown` — the load-bearing arm, the exact
  cell that landed `false`. Asserts the stored content really is `[redacted]`, then pairs the
  redacted call with a `SUMMARIZED` control differing **only** in mode, which lands `false`.
- `test_redacted_cross_family_turn_capture_lands_unknown` — the override in the other
  direction; its `SUMMARIZED` control lands `true`.
- `test_redacted_tool_event_capture_lands_unknown_both_directions` — the same override on the
  other `DISPATCH_DERIVED` kind, both family arms.
- `test_instance_default_redacted_mode_also_lands_unknown` — a recorder bound with
  `capture_mode=REDACTED` and no per-call argument; consulting only the argument would leave
  this path landing `false`.

**Mutation probe.** Reverting `_content_origin_for` to the bare mapping lookup fails exactly
those four and nothing else: `test_redacted_same_family_turn_capture_lands_unknown`
(`FALSE is not UNKNOWN`), `test_redacted_cross_family_turn_capture_lands_unknown`
(`TRUE is not UNKNOWN`), `test_redacted_tool_event_capture_lands_unknown_both_directions`
(`FALSE is not UNKNOWN`), `test_instance_default_redacted_mode_also_lands_unknown`
(`FALSE is not UNKNOWN`) — 4 failed, 11 passed. The eleven pre-existing witnesses stay green
under both the mutated and the fixed source, so they are the positive controls: the fix
narrows nothing that was already correct.
