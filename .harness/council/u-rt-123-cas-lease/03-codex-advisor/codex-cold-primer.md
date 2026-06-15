# Cold primer for out-of-family review (Codex) — descriptive ONLY

*Decorrelation discipline: this primer describes the PROBLEM + the CANDIDATE mechanism only. It deliberately contains NO prior reviewer's conclusions.*

## System

A hand-rolled durable workflow-execution engine ("reconciler-loop" class) in Python. Hard constraint: NO vendored orchestration/consensus infrastructure (no Kubernetes, no etcd, no Temporal, no ZooKeeper, no distributed-lock service). All coordination must be hand-rolled over a filesystem.

A workflow can PAUSE (its converged state is captured durably) and later RESUME. **The resume effect is re-executing the workflow's remaining steps**, some of which perform non-idempotent external side effects (e.g. `git push`, send email, a paid API write).

## The durable substrate (filesystem)

- An append-only, per-workflow convergence log. Each record is checksummed and stamped with a monotonically increasing integer `resource_version` (= its position). Torn-tail / corrupt records are detected and the contiguous valid prefix defines the latest committed state.
- Per-`(workflow, resource_version)` claim files created atomically via `O_CREAT | O_EXCL` + `os.link` (temp-then-link), with a directory fsync.
- A per-workflow advisory `flock`.

## The correctness requirement

The substrate must distinguish two cases:
- **(a) crash-then-retry** by the same logical reconciler — sequential; the prior process is DEAD — and MUST be allowed to re-resume its own paused workflow ("durable replay across restart").
- **(b) two concurrent DISTINCT reconcilers** resuming the same paused workflow — both LIVE — exactly ONE may proceed; the other MUST abort.

A double-resume = the workflow's step suffix executes twice = a potentially unbounded, irreversible double side-effect.

## Candidate mechanism (to red-team)

Replace an owner-identity-token claim (which is defeated when all reconciler processes share one identity) with:
1. **Same-host:** the per-workflow `flock` serializes + witnesses liveness (kernel releases it on process death).
2. **Cross-host:** a **write-back-conditional CAS on `resource_version`** — analogous to etcd's `mod_revision` compare-and-swap: a reconciler reads the latest committed `resource_version` R, and its convergence write-back succeeds only if it can atomically claim R via the `os.link` claim; a loser observes the revision already advanced and aborts. Plus an "incarnation-unique" identity to fence a zombie.
3. A **parameterized lease backend** `{local-single-host, shared-store-cas}`; `shared-store-cas` runs a one-shot startup atomicity probe and **fails closed** (refuses to start) if the store can't back atomic claims.

## Deployment surfaces

- `local-development` — single host.
- `self-hosted-server` — single OR multi-host (HA) over a shared volume.
- `managed-cloud` — likely multi-host over a network/shared/object-store-backed mount.

## The questions to answer independently

1. **Is a correct cross-host *at-most-once auto-crash-recovery* (case a, with no double-execution in case b) achievable on a bare shared filesystem WITHOUT (i) a vendored consensus service and WITHOUT (ii) a TTL / lease-expiry / liveness-probe death-detector?** If not, name precisely what is impossible and why.
2. Red-team the candidate for **double-execution windows** and **crash-recovery deadlocks** across the 3 surfaces. Where does it silently assume infrastructure?
3. Is the `os.link` write-back-conditional CAS sound *cross-host*? What exactly does it assume about the shared store (NFSv3 vs NFSv4 vs object-store FUSE)? Can a single-process startup probe verify that assumption?
4. If a tradeoff is forced, which is the least-bad: scope to single-host, accept HITL-mediated multi-host recovery, hand-roll a liveness mechanism, or relax the no-vendored-infra constraint? Reason from distributed-systems first principles.
