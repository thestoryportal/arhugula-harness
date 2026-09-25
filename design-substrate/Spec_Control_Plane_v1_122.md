# Spec: Control Plane — v1.122 (delta over v1.121)

*Delta-only file. C-CP-25's workflow entry, step context, PAUSED result and paused-child
fan-out carriers are amended below. C-CP-26 §26.1/§26.6's capture and snapshot-hash
terms are amended for typed exact-record capture and optional child refs. Every other v1.121 and earlier C-CP-01 …
C-CP-29 term remains in force. No contract number or `RunStatus` value is added.*

**Filed:** 2026-09-25  
**Authority:** ratified B-104 at-most-once durable HITL terms and adopted operator
defaults, recorded in `evaluation/production-readiness-arch/b104-operator-amendment-proposal-1.md`;
Task 4 source at `f1e7430ddefe98f9cb96d1eb9c1db8843864128d` after the independently
reviewed DENY rebase.  
**Predecessor:** `Spec_Control_Plane_v1_121.md`  
**Paired Runtime successor:** Runtime v1.129 is owed. This Control Plane delta alone
does not admit a durable child resume or install the Task 5 claim gateway.

## §0 Change-note (v1.121 → v1.122)

### §0.1 The gap

A pause capture previously returned a snapshot without the exact record identity
created by the durable journal append. A fan-out parent could therefore retain its
paused child's snapshot while losing the record needed to prove recency. A boolean
descent marker also could not distinguish a root from a child and grandchild at the
journal boundary. Root and descended entry inputs were conflated: a caller could
present a child as a root. These are unsafe inputs to the ratified B-104 claim flow.

### §0.2 C-CP-26 §26.1/§26.6 (AMENDED) — typed capture and exact record

The workflow-layer `PauseResumeProtocol.capture_pause_snapshot` requires a
**keyword-only** `descent_depth: int` with no default. The root supplies `0`; each
recursive child supplies its parent's depth plus one. A driver-composed
`StepExecutionContext` rejects a negative depth; the durable journal append
rejects a negative or otherwise malformed depth. The CP ephemeral capture
accepts the argument but does not persist or independently validate it.
The ephemeral protocol does not journal and returns
`EphemeralCapturedPause(snapshot)` with `record_ref is None`. The durable protocol
returns `DurableCapturedPause(snapshot, record_ref)` only after appending that
snapshot; `record_ref` is the `JournalRecordRef` for the exact append. Together these
are `CapturedPause`. The ref is a sibling of the snapshot, never a field within its
own journaled bytes, which would make the record digest self-referential.

The capture boundary MUST reject a durable pair whose ref's `workflow_id`,
`run_id` or `snapshot_hash` differs from its snapshot. A `RunResult` carrying
`pause_record_ref` MUST also carry `pause_snapshot` and enforce the same binding.
Under C-CP-25 §25.15's PAUSED return, every driver-composed PAUSED result,
including branch and reestablishment paths, carries the
ref it received from the capture, or `None` for an ephemeral capture. A successful
capture may not be represented by a synthetic ref or by a ref copied from a
different append. Runtime's exact lookup verifies the named record's position,
digest and identity; the Task 5 claim store must establish recency before any
durable child body is admitted. This CP pairing alone is not that verification.

### §0.3 C-CP-25 workflow entry and `StepExecutionContext` (AMENDED)

The public `execute_workflow` entry is the **root** entry. It has no caller-supplied
depth, `parent_gate_floor` or inherited placements and invokes
`execute_workflow_at_depth(..., descent_depth=0)`.
`execute_workflow_at_depth` is the explicit descended entry; its keyword-only
`descent_depth` is mandatory. Each recursive child invocation supplies its parent's
depth plus one. Its `parent_gate_floor` defaults to `AUTO`; the effective parent
gate is the stricter of the child's resolved manifest parent gate and this
inherited floor. Omitting the floor therefore contributes no inherited
restriction. A recursive caller supplies the actual parent floor. The
ancestor-first `PRE_ACTION` placements retain the v1.120 matching rule. The
root entry does not accept a parent floor or inherited placements. The v1.120 text that put
`inherited_hitl_placements` directly on `execute_workflow` is superseded at this
entry boundary: that parameter belongs on the descended entry only. The
ancestor-first composition and first-match semantics of v1.120 remain unchanged.

This also supersedes v1.86 C-CP-25 §25.2's stored
`sub_agent_descent: bool = False`, `execute_workflow(sub_agent_descent=...)`
keyword and child re-entry through that root function. Children re-enter
`execute_workflow_at_depth(descent_depth=parent + 1)`.

`StepExecutionContext.descent_depth` defaults to `0` for standalone context
construction. Every context the **CP driver composes** for one workflow invocation, across LINEAR
and the five non-linear strategies, carries the same non-negative
`descent_depth`. Branch context copies preserve it. The context's
`sub_agent_descent` is a read-only derived predicate, exactly
`descent_depth > 0`; it is not a separately stored, caller-settable boolean.
The depth is transient step metadata and does not enter `StepEffectiveBinding`,
the §5.2 override outcome hash, or the pause `snapshot_hash`. A durable journal
records ancestry separately at capture. The runtime's descended tool-superset
read of `sub_agent_descent` remains valid through the derived predicate.
Runtime-created contexts outside the CP driver must be assessed in Runtime
v1.129; this CP driver guarantee does not assign them a child depth.

### §0.4 C-CP-25 §25.11 fan-out carriers and C-CP-26 §26.6 hash input (AMENDED)

A `SUB_AGENT_DISPATCH` child that returns PAUSED hands the parent one
`PausedChildCapture(child_workflow_id, child_snapshot, child_record_ref)`.
`child_record_ref` is the child's exact durable `pause_record_ref`, or `None`
for an ephemeral capture or a legacy carrier that never recorded one. The
child dispatch boundary and both ORCHESTRATOR_WORKERS / HIERARCHICAL_DELEGATION
worker fan-out and PARALLELIZATION peer fan-out MUST carry all three values
together into the parent's `PausedChildBranchResumeState` and recover them
together on resume. A child ref MUST bind to the child snapshot's workflow id,
run id and snapshot hash and to the dispatched child's workflow id when that
identity is present. Two paused children in one fan-out MUST NOT present the
same non-null record ref. A mismatch or duplicate is a resume-body mismatch,
not permission to redispatch the child as fresh work.

The child's ref stays beside the child's snapshot; it is never inserted into
that child's snapshot. When non-null, `child_record_ref` in the parent fan-out
carrier is covered by the **parent's** `snapshot_hash` under §26.1 capture
and §26.6 invariant 2. When null, the field
is dropped from the serialized carrier, including nested paused-child paths,
so ephemeral and pre-v1.122 snapshots recompute their prior hash bytes.
`child_workflow_id`'s existing legacy default and compatibility handling remain
in force. A legacy ref-less child is not silently promoted to a durable exact
record; Runtime determines whether it can be resumed under the Task 4 refusal
rule.

### §0.5 Boundary and preservation

This delta supplies ancestry and an exact captured record reference to the
Runtime boundary. It neither claims a record is still latest nor grants a
paused child permission to execute. Runtime v1.129 must specify verification and
refusal; Task 5 must install a claim/started gateway before durable child body
entry is admitted. The B-104 user-approved at-most-once claim and audited
manual recovery remain authoritative.

| Element | Disposition |
|---|---|
| C-CP-25 topology and terminal status meanings | Preserved |
| C-CP-17 ancestor-first `PRE_ACTION` inheritance and first-match rule | Preserved; moved to explicit descended entry |
| Pause snapshot fields and own hash bytes | Unchanged by the sibling record ref |
| Parent fan-out snapshot hash | Covers a present child ref; omits null for legacy bytes |
| Ephemeral and legacy ref-less child capture | Representable, but cannot prove a durable exact record |
| Task 5 claim, started frame, worker handoff and installed acceptance | Outside this delta |

## §1 Acceptance for the paired implementation

Provider-free tests must demonstrate root depth zero, child depth one and
grandchild depth two at capture; the same depth in every CP-driver-composed step context;
immutable derived descent; exact ref binding on captured pauses and paused
`RunResult`; the ref traversing both fan-out kinds and nested pause recovery;
duplicate/mismatched refs refused; and null-field legacy/ephemeral hash
compatibility. Independent source review and Runtime v1.129 contract clearance
are required before local RC integration. No result here is an installed or
live-model witness.
