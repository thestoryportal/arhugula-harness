# E1-A1 — Primaries (independent, blind)

Genuine dedicated-agent invocations; each adopted its cN SKILL.md + grounded in primary sources. Verbatim.

---

## C9 — Reliability & Recovery

**Position.** The owner-token CAS is not merely defeated — it is *inverted*: same-owner re-acquire IS the crash-recovery admit path (`reconciler_pause_resume_substrate.py:234-235`), but `owner` defaults to the single static `self.actor` (`engine_recovery_loop.py:167,:96`). Two distinct live reconcilers from the same factory carry the same token → both take the "re-entrant → True" branch → both proceed. The mechanism advertised as floor-(i) crash-recovery is what collapses case (b).

**The "crash-stable-BUT-instance-unique" contradiction dissolves by splitting it into THREE:**
1. **Instance-unique incarnation identity** — `{host_id + boot_id + pid + process_start_time}` (boot_id/start_time defeat pid-reuse across a crash).
2. **Liveness witness** — same-host: the existing per-workflow `flock` (kernel-authoritative, released on death). Cross-host: a monotonic **heartbeat SEQUENCE counter** in the lease record (NOT wall-clock TTL).
3. **Fencing generation** — a monotonic counter bumped on every reclaim, carried into and **checked at the EFFECT's durable-write boundary**.

A restarted reconciler does NOT re-present the old lease — it detects the dead prior holder via liveness and FENCES it (generation++), then claims fresh. **Same-owner re-entry is deleted as a concept.**

**Recommended:** (B) liveness-probe + fencing generation, synthesizing (C)'s same-host flock as the liveness *witness* (not the safety guard). Cross-host: reuse the `os.link`+dir-fsync claim verbatim for atomicity; reclaim gated on heartbeat-sequence staleness; every reclaim writes generation+1.

**Atomicity/liveness assumption required:** `O_EXCL`/`os.link` atomicity on the actual backing FS (local + NFSv4 ok; NFSv3 needs the `nlink==2` idiom). `flock` is same-host ONLY (NFS flock unreliable — must never leak into a cross-host safety claim). Reclaim gates on monotonic heartbeat sequence, NEVER wall-clock TTL → kills clock-skew by construction.

**Property split (honest):** CAN guarantee **at-most-once COMMIT** (fencing checked at F2 commit). CANNOT guarantee **at-most-once EXECUTION** of non-idempotent external side effects (slow-vs-dead is undecidable in bounded time). This ties floor (iii) to floor (ii): a lease without idempotency on the effect is not exactly-once.

**THE REFUSAL:** the lease guards the CLAIM, not the EFFECT — and the EFFECT carries no fence today (`workflow_driver.py:1624-1681`: non-abort → straight into the step loop, zero generation token to any F2 step-commit). A stale-but-not-dead holder (GC-paused) already fenced+reclaimed will still **double-commit**. Won't ship as the floor-(iii) mitigation unless a **fencing generation is carried into `attempt_resume`'s outcome and checked at the step-loop's F2 ledger commit boundary** (stale gen → reject write → `ABORT_REVALIDATION_FAILED`). Fencing-token persistence + commit-time enforcement are **C3's surface** (invoked).

---

## C10 — Action Safety & Blast Radius

**Position.** The resume effect is NOT idempotent → maximal safety bar. Verified at `workflow_driver.py:1624-1681`: a non-abort outcome falls into `for step_index, step in enumerate(steps[resume_at:], ...)` and re-executes the step suffix. A step may be `write-unbounded` (git_push / send_email / paid API write). Double-execution is a **write-unbounded blast radius until proven otherwise** — not a benign retry. The discriminator is liveness/time, not static identity (premise 1 confirmed against the code).

**Per-candidate double-execution windows:**
- **(A) TTL** — *TTL expiry while the holder is alive-but-PAUSED.* A RECONCILER_LOOP holder legitimately pauses (HITL_PENDING) longer than the TTL → lease expires → a second reconciler claims and re-executes *while the first is still alive and will itself resume.* TTL **manufactures** the concurrency it's meant to prevent. Plus clock-skew.
- **(B) liveness-probe** — false-negatives a live-but-slow holder (GC pause / HITL pause / partition) → "dead" → re-execute → double. Cross-host liveness probing is a distributed failure-detector with no safe synchronous answer.
- **(C) leader-election** — same-host `flock` is CORRECT (kernel-mediated, auto-released on death; correctly distinguishes crash-retry from concurrent). Cross-host: hand-rolled FS lock over NFS where `O_EXCL`/`link` atomicity is NOT guaranteed (NFSv3 `O_EXCL` non-atomic; `link`-based is the classic workaround but depends on close-to-open consistency).

**Recommended:** **(C), explicitly two-layer, cross-host claim CONDITIONAL not asserted.** Keep same-host flock (correct). Cross-host: require the durable store to provide a **linearizable atomic CAS** (the etcd analogue). The `O_EXCL`/`link`-into-place mechanism is correct **iff** the FS provides atomic `link` + close-to-open consistency — that assumption must be **DECLARED + VERIFIED at deployment, not assumed.**

**Fail-closed posture (required):** when CAS atomicity CANNOT be established, **REFUSE to admit the resume** (`ABORT_REVALIDATION_FAILED`). **In doubt, ABORT.**

**Harm ranking:** false-PROCEED (double-execution: unbounded / irreversible / silent) is STRICTLY worse than false-ABORT (stuck: bounded / reversible / observable → §22.1 → HITL). Prefer ABORT. Accept the operator-burden of false-ABORTs as the correct trade.

**THE REFUSAL:** a TTL-expiry or liveness-probe path that admits a resume on an *unverified* shared store — any mechanism that infers "dead" from TIME or a PROBE rather than a linearizable atomic CAS. The honest multi-host build is **(C) + declared-and-verified atomic-CAS + fail-closed-to-ABORT** — NOT (A), NOT (B). ("Scope to single-host" is a FULL-SPEC violation; "assert cross-host safety on a store whose CAS atomicity is unproven" is a blast-radius violation.)

---

## C11 — Operator Loop & Local Deployment

**Position.** (C)'s cross-host extension SILENTLY assumes `os.link`/`O_EXCL` atomicity on whatever the operator mounted as `reconcile_log_dir` — the unsafe-to-ship-bare assumption. (A)/(B) substitute a trustworthy cross-host CLOCK assumption (fails under NTP drift / suspended-VM clock-freeze). Both fail operator-invisibly until two reconcilers race.

**Credit:** the current substrate correctly chose `os.link` over bare `O_EXCL` (atomic on NFS-with-lockd). BUT link-atomicity evaporates on object-store FUSE mounts (gcsfuse/s3fs — no atomic `link`) and NFSv3-without-locking → link-atomicity is necessary-not-sufficient; still needs a config-time assertion.

**Per-surface honesty:**
- **local-development** — single host: flock genuine, local FS atomic, no clock. **Lease is honest + needs ZERO config. The SAFEST surface — not the one to exclude.**
- **self-hosted-server** — single-host fine; multi-host HA honest only on NFSv4/lockd or a real shared block volume; **dishonest on object-store FUSE / NFSv3-no-lock.**
- **managed-cloud** — most likely object-store-backed; atomic `link` LEAST likely to hold; highest risk, least operator-inspectable.

**Recommended — parameterize-and-assert, minimally.** Pluggable lease backend, two members: `local-single-host` (flock + local-FS atomic claim; the DEFAULT — zero burden) and `shared-store-cas` (cross-host `os.link` claim). At startup, `shared-store-cas` runs a one-shot **atomicity PROBE** (create-temp + double-`link` race; assert the second raises `FileExistsError`) and **FAILS CLOSED** if the store can't back it. Maps onto the persona bridging-arc: solo-dev × local-development is safe + unconfigured; the config line + assertion land ONLY on the operator who scaled into multi-host HA.

**Confirm (one AskUserQuestion, only on cross-host backend):** "Is `reconcile_log_dir` on a filesystem providing atomic `link`/`O_EXCL` across all reconciler hosts (NFSv4/lockd or shared block volume) — NOT object-store FUSE or NFSv3-without-locking?" The startup probe is the enforcement.

**O-E3-2 admissibility FLIPS:** the stale reason "requires K8s control plane" was wrong AND pointed the wrong direction. Under the harness-hosted reading, local-development is now the SAFEST surface. Recommend WIDENING local-dev admissibility + REPLACING the reason; move the real gate onto multi-host surfaces via the config-time atomicity assertion. Framed as a recommendation INTO the E-impl-3 deferred decision (resolved against ADR-D1 §1.2), not a pre-decision — X-AL-3-clean.

**THE REFUSAL:** a cross-host CAS lease on shared storage with NO startup assertion that the store provides atomic `link`/`O_EXCL`. Build the cross-host capability (FULL-SPEC) but as *assumes-a-CAS-capable-store, asserted-and-fail-closed at startup*, never silently-assumed.

---

## Orchestrator synthesis (for the cross-read)

**Strong convergence (3/3):**
1. Same-host `flock` is CORRECT and kept.
2. Cross-host needs an ATOMIC LINEARIZABLE CAS on the shared store (`os.link`-based), NOT wall-clock TTL and NOT a pure liveness-probe-of-death.
3. The atomicity assumption must be DECLARED + VERIFIED AT STARTUP + FAIL-CLOSED if unverifiable (parameterize-and-assert; default `local-single-host`).
4. Fail-closed: in doubt, ABORT (false-ABORT ≪ false-PROCEED).
5. O-E3-2: local-development is the SAFEST surface → recommend widening admissibility + moving the gate to multi-host via the atomicity assertion.

**Residual tensions for the cross-read DEBATE:**
- **T1 (C9 ⊥ C10 on death-inference):** C9 recommends (B) liveness-probe **+ fencing-at-commit**; C10 REFUSES any probe/time death-inference, recommends (C) atomic-CAS + fail-closed. Reconcilable? (C9's fencing protects the COMMIT; C10's claim-CAS protects the CLAIM — are both needed, or does atomic-CAS+fail-closed subsume the probe entirely?)
- **T2 (scope/depth of the fence):** C9's refusal requires a **fencing generation carried into `attempt_resume`'s outcome and checked at the step-loop's F2 ledger commit boundary** (`workflow_driver.py:1681` + the IS ledger write). Does that REACH beyond U-RT-123 (the substrate) into CP (driver step-loop) and IS (ledger commit)? If so → a halt-route-split-AC / new-finding question, not buildable purely in U-RT-123.
- **T3 (at-most-once COMMIT vs EXECUTION):** both C9 + C10 surface that non-idempotent external step side-effects can't be made exactly-once by the lease alone — needs floor (ii) idempotency on the EFFECT (currently only on the audit entry). In-scope for U-RT-123, or a separate floor-(ii) gap finding?
