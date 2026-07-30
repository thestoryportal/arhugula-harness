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
