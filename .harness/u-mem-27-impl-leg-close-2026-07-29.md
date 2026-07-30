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

| `event_kind` | Origin disposition | Why |
| --- | --- | --- |
| `turn_completion` | `DISPATCH_DERIVED` | The stored `response_summary` is computed from the actual provider response, notwithstanding its `SummarySource.HARNESS_RULE` label. |
| `tool_event` | `DISPATCH_DERIVED` | Tool-event content is produced by a completed dispatch. |
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
> not raw equality of every per-source tri-state. Scope stated honestly: these are in-process
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
