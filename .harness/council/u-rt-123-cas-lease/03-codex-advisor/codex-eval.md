# Codex cold review: U-RT-123 CAS lease substrate

## Verdict

The candidate is correct only as a single-host crash-recovery mechanism, and even there only if the critical section is defined so that the kernel `flock` is held across the full resume side-effect suffix. It is not a correct cross-host at-most-once auto-crash-recovery mechanism on a bare shared filesystem without a lease expiry, liveness/death detector, consensus service, or externally enforced fencing.

The impossible part is not atomic file creation by itself. The impossible part is simultaneously:

1. allowing automatic recovery after a prior claimant might have crashed, and
2. forbidding a second live claimant from executing the same non-idempotent suffix,
3. without any reliable way to distinguish "dead owner" from "slow, partitioned, stalled, or still executing owner."

That is the classic asynchronous failure-detector problem behind FLP-style impossibility results. A process pause, network delay, NFS stall, scheduler stop, VM suspend, or mount partition is observationally indistinguishable from a crash to another host unless the system adds timing assumptions or an external authority. A filesystem CAS can serialize mutations to a metadata object; it cannot prove process death, cannot revoke an executing process, and cannot fence arbitrary external side effects such as `git push`, email, or paid API writes.

## Q1: Is correct cross-host at-most-once auto-crash-recovery achievable on a bare shared filesystem with no consensus and no TTL/death detector?

No.

At-most-once auto-crash-recovery requires a recovery process to make a unilateral decision that the previous owner is dead and that it is safe to execute the remaining workflow suffix. In an asynchronous distributed system, that decision is impossible without a failure detector or a consensus-backed lease/fencing authority. The recovery process can observe only absence of progress. Absence of progress does not imply death.

The system has two irreconcilable choices:

- If a persistent claim is never stealable, then case (b) is safe, but case (a) deadlocks after the winner crashes before clearing or advancing the claim.
- If a persistent claim is stealable automatically, then case (a) can recover, but case (b) can double-execute whenever the original owner is live but slow, partitioned from the shared store, blocked in I/O, suspended, or still executing side effects after losing store visibility.

`resource_version` CAS does not change that impossibility. It gives a linearizable election only if the underlying store really provides linearizable create/link semantics. It does not provide liveness. It also does not fence side effects unless every side-effect sink participates in the fencing protocol and rejects stale tokens. The primer explicitly includes external effects that do not naturally accept fencing tokens. Therefore "exactly one live reconciler executes the suffix, while a crashed reconciler's work is automatically recovered" is not implementable under the stated constraints.

## Q2: Double-execution windows and crash-recovery deadlocks

### Local development: single host

`flock` is a reasonable same-host liveness witness because the kernel releases the lock on process death. If every process that can execute the suffix honors the same per-workflow lock, and the lock is held from "decide to resume" through the last non-idempotent side effect and durable write-back, then same-host mutual exclusion is achievable.

The double-execution windows are still:

- If the lock is released before all non-idempotent suffix steps finish, a second local reconciler can enter and re-execute the suffix.
- If side effects are launched asynchronously outside the lock's lifetime, the lock no longer fences them.
- If a child process or helper continues side effects after the parent dies and the kernel releases the lock, a restart can execute the suffix again while the child still acts.
- If another code path ignores the advisory lock, `flock` does not stop it.

The deadlock window is small on a true local filesystem if the persistent claim is not treated as an unrecoverable owner token. If the implementation creates a persistent claim before execution and then refuses to proceed when it sees that claim after a crash, it converts a recoverable same-host crash into a permanent deadlock. On single host, the kernel lock should be the liveness mechanism; stale durable claims must be interpreted through the recovered log state, not as proof of a live owner.

### Self-hosted server: single host

This is essentially the same as local development, assuming a real local POSIX filesystem and one kernel lock domain. It remains unsafe if "self-hosted" means multiple containers, supervisors, or hosts sharing a volume where `flock` semantics are not a single coherent kernel authority.

### Self-hosted server: multi-host shared volume

This is where the candidate silently assumes infrastructure.

`flock` is not a portable cross-host correctness primitive. Depending on mount type and options, it may be local-only, advisory but inconsistently propagated, emulated, lost on server restart, or subject to lease recovery behavior outside the application's model. Even if cross-host `flock` works, it is now relying on the shared filesystem's lock manager as the distributed coordination service that the constraints say not to vendor.

The CAS claim creates these windows:

- Claim-before-execute deadlock: A wins claim for R, crashes before advancing the convergence log. B sees claim R and cannot know whether A is dead or live. If B refuses, recovery is deadlocked. If B proceeds, double execution is possible.
- Execute-before-claim double execution: If any suffix step occurs before the durable CAS claim is committed and directory-fsynced, two reconcilers can both execute side effects and then race on metadata.
- Claim-then-side-effect-then-crash ambiguity: A claims R, performs one or more external effects, then crashes before appending the new resource_version. B cannot know which effects happened. Retrying the suffix can duplicate them; not retrying can leave the workflow stuck.
- Append-before-side-effect inconsistency: If A advances the log before all side effects are durably complete, a crash can make recovery skip effects that never happened.
- Partitioned-owner double execution: A claims R and is executing side effects. A loses access to the shared store or stalls on write-back. B observes no progress and, if the design permits stealing, executes the same suffix. Both are live.
- Zombie-after-fence double execution: An incarnation token fences only participants that check it. A zombie can still perform unfenced external effects after B has claimed a later token.
- Directory-cache/read-after-write lag: B may not immediately observe A's claim or log append on some shared stores, so two hosts can make decisions from divergent views unless the store supplies close-to-open or stronger consistency adequate for the protocol.

The deadlocks are:

- Permanent stale claim after crash with no expiry/death detector.
- Lock-manager orphan/recovery states where a server or client loses lock state but the application cannot safely decide whether to retry.
- Split-brain mounts where each host can make local progress but metadata reconciliation is delayed or non-linearizable.
- Human operator lockout if the design fails closed on any ambiguous claim but provides no mediated recovery path.

### Managed cloud shared/object-store-backed mount

This is the least safe surface for the candidate.

Many managed mounts are not linearizable POSIX filesystems. Object stores often lack atomic rename/link semantics entirely; FUSE layers may emulate them with copy-plus-delete or side metadata; listings may lag; error and retry behavior can duplicate writes; durability of directory fsync may be meaningless or unsupported. A mechanism that depends on `os.link` as a linearizable compare-and-swap is silently depending on a filesystem with a real single metadata serialization point and durable directory operations.

For this surface, startup must fail closed unless the backend is explicitly known to provide the required semantics. A one-shot probe is not enough evidence.

## Q3: Is `os.link` write-back-conditional CAS sound cross-host?

It is sound only under strong assumptions:

- `link(old_tmp, claim_path)` must be atomic across all clients.
- Exactly one concurrent linker can succeed for a missing `claim_path`.
- All clients must observe the winning link consistently before making dependent decisions.
- Directory fsync, or an equivalent durability barrier, must make the claim survive crash/restart.
- The filesystem must not emulate hard links with non-atomic object-store operations.
- The protocol must handle server restart, client retry, timeout, and ambiguous error responses without treating "unknown" as success or failure incorrectly.

On a local POSIX filesystem, hard-link creation to a non-existing destination can be used as an atomic create-like primitive, subject to correct fsync discipline.

On NFS, the answer is version/configuration dependent. NFSv3 has server-mediated operations but weaker cache and failure semantics than a local filesystem; clients can see stale attributes, ambiguous RPC outcomes, and server reboot recovery cases. NFSv4 improves stateful locking and consistency machinery, but correctness still depends on server implementation, mount options, delegations/caching, and recovery behavior. "NFS" is not a single proof obligation.

On object-store FUSE, assume it is not sound unless the vendor explicitly documents linearizable create-if-absent/link/rename semantics and durable directory barriers matching the protocol. S3-like object stores can provide conditional put on object keys, but that is not POSIX `os.link`; a FUSE layer may not expose the object-store conditional primitive faithfully.

A single-process startup probe cannot verify the needed property. It can detect obvious local unsupported operations, but the property is about concurrent cross-client linearizability under crash, retry, cache invalidation, server failover, and network partition. At minimum, a meaningful probe would need multiple independent clients/hosts racing on the same mount and fault injection. Even that would be an empirical compatibility test, not a proof. It cannot establish future behavior under all failure modes.

## Q4: Least-bad tradeoff

The least-bad tradeoff is:

1. scope automatic recovery to single-host backends using kernel `flock` plus durable log recovery; and
2. for multi-host shared-store deployments, require HITL-mediated recovery unless a real coordination/fencing service is allowed.

That preserves the non-negotiable safety property: no automatic double execution of non-idempotent side effects. It also tells operators the truth. Multi-host automatic failover is not free; it requires a failure detector, a lease authority, or consensus-backed fencing. If the project needs unattended HA recovery, the right engineering move is to relax the no-vendored-infra constraint and use a coordination system with documented linearizable CAS, leases, sessions, and fencing semantics. etcd, ZooKeeper, Consul, a database with transactional advisory locks plus fencing tokens, or a cloud-native conditional-write service are all more honest foundations than a hand-rolled filesystem lease pretending to be one.

I would not hand-roll a liveness mechanism here. A TTL lease is a failure detector with timing assumptions. Implementing it over a filesystem recreates the hard parts badly: clock bounds, renewal latency, pause-the-world stalls, server failover, split brain, monotonic token issuance, and fencing of old owners. If TTLs are used anyway, they must be named as a bounded-synchrony assumption and paired with fencing tokens enforced by every side-effect sink. The primer's side effects do not satisfy that condition.

I would also not "solve" this by accepting automatic multi-host recovery with best-effort CAS and a startup probe. That chooses availability while hiding a double-execution risk in the exact scenario where the substrate is supposed to prevent irreversible duplicate effects.

Concrete product posture:

- `local-development`: allow `local-single-host`; hold `flock` across full suffix execution and write-back; test crash/restart on the same host.
- `self-hosted-server`: allow automatic recovery only when explicitly configured as single-host. For HA over shared volume, fail closed into HITL recovery unless a vetted coordination backend is configured.
- `managed-cloud`: do not enable filesystem-CAS automatic recovery by default. Require either HITL-mediated recovery or a managed coordination primitive with documented conditional write/lease semantics.

The decisive line is: cross-host filesystem CAS can be an election primitive on some stores, but it is not a death detector and not a side-effect fence. Therefore it cannot deliver at-most-once automatic crash recovery for non-idempotent workflow suffixes under the stated constraints.
