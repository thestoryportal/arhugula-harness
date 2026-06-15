# DELIVERABLE — U-RT-123 CAS-lease realization (council v1, 2026-06-15)

*Conscious versioned deliverable of the genuine multi-agent council (5 voices + adversarial + Codex out-of-family + advisor; 4-way convergence). Ledger: `00-CHARTER.md` · `01-council/` · `02-adversarial/` · `03-codex-advisor/` · `04-reconciliation/`. This decides the HOW for U-RT-123; the spec v1.33 §7.4 already cleared the substrate to impl-discretion (no spec amendment).*

## The core correction (the design win)

The defeated `[P1]` owner-token model treated the CAS as an **owner-identity mutex**. etcd's actual primitive — and what C-CP-07 §7.1 row 4 / §7.4 floor (iii) names — is **compare-and-swap on the resource revision** (`mod_revision`), NOT an owner mutex. The fix is to realize the genuine optimistic-concurrency primitive: a **write-back-conditional CAS on `resource_version`** over the engine-owned convergence store. Confirmed a genuine strength by the adversarial reviewer; 4-way converged.

**The decomposition that dissolves the FULL-SPEC tension** (advisor + Codex, from first principles): etcd's *compare-and-swap* (floor iii — the **concurrent-resume mitigation**, case b: two LIVE reconcilers) and etcd's *lease/TTL* (the **death-detector** that enables floor-i AUTO crash-recovery, case a: a DEAD prior holder) are **different primitives**.
- **Floor (iii) CAS (case b) is BUILDABLE cross-host** (given atomic-`link` storage) — FULL-SPEC satisfied.
- **Floor (i) AUTO crash-recovery on multi-host (case a) is IMPOSSIBLE** without either a vendored consensus/lease service (I-6 forbids) OR a TTL/liveness death-detector (a false-positive double-execution window — C10 refused; the "trap" advisor + Codex both flagged). This is distributed-systems physics (the failure-detector problem / FLP), not a council oversight.

## A. BUILDABLE in U-RT-123 now (pure-RT substrate, impl-against-cleared-spec)

1. **Delete the owner-token same-owner-re-entry model** (defeated/inverted).
2. **Same-host `flock`** around the read→claim critical section (keep; correct kernel-mediated serializer + liveness witness — auto-released on death).
3. **Write-back-conditional CAS on `resource_version`** (the etcd `mod_revision` analogue): the claim is the atomic `O_EXCL`/`os.link` create on `(workflow, revision)`. **Closes the two-reconciler CLAIM race (case b / floor iii) on single AND cross-host (given atomic-link storage):** two resumes that observed the SAME committed `resource_version` race the claim; the first wins, any LATER resume of that SAME revision hits `FileExistsError` → ABORT. (Precise mechanism — NOT "observes the revision advanced"; nothing advanced, it is a same-revision claim collision.) **Caveat (cross-host, folds into F-CC):** the claim is "first-to-claim revision N," NOT "claim conditional on N still being head." Same-host the `flock` serializes read→claim so a converge cannot interleave; cross-host, a concurrent capture can bump head N→N+1 while a resume runs its post-claim diff/revalidate on stale N (two resumes on DIFFERENT revisions both proceed). That cross-host stale-revision window is the multi-host-AUTO-recovery hard case → **F-CC** (HITL-mediated, spec-faithful).
4. **Parameterized lease backend** `{local-single-host (DEFAULT, zero-config), shared-store-cas}` — `harness_runtime`-PRIVATE (must not leak into `harness_cp.pause_resume_protocol` / a cleared Protocol signature — explicit AC + import-surface test).
5. **Startup atomicity assertion** for `shared-store-cas`: a one-shot probe, **HONESTLY labeled a same-host sanity check (NOT a cross-host CAS verifier)**; fail-closed via a substrate `RuntimeError` (NOT a `ResumeOutcome` — store-unverifiability stays OUT of the closed enum). The operator config-time declaration is the load-bearing (un-verifiable) gate.
6. **Lost concurrent race → `ABORT_REVALIDATION_FAILED`** (contract-faithful; → §22.1).
7. **`PathClass.STATE_LEDGER`** (no IS delta).
8. **Incarnation stamp** — best-effort fencing stamp on the engine-owned write-back; document per-surface portability limits (no `boot_id` on macOS; container `pid=1`/shared `boot_id`). NOT load-bearing in U-RT-123 (the load-bearing fence-consult is CP-scope, routed below).
9. **Verification (AC):** exercise genuinely-concurrent OS **processes** (not threads) + a crash-mid-converge (`kill -9` a claim-holder, then retry), single-host. Honestly state: cross-host cannot be verified in single-host CI → `shared-store-cas` cannot ship labeled "verified".

**Single-host is COMPLETE for both cases** (case b via the CAS; case a via flock-release-on-death + durable-log recovery). With the CP-side flock-held-across-suffix (routed below), case (ii) zombie also closes on single-host.

## B. ROUTED FINDINGS (NOT buildable in U-RT-123; X-AL-3 — no silent absorption)

- **F-1 — case-(ii) zombie closure (CP-scope).** A holder that passed the claim, GC-paused, was fenced, then wakes is ALREADY inside the driver step-loop (`workflow_driver.py:1681`) and never re-calls `attempt_resume`. Closing it needs the CP driver to either **hold the engine-owned lock across the full suffix** (Codex's sharpening) OR **consult the engine-owned generation before each step-commit** (C9/C3). Either reaches CP (U-CP-96/97 + the `:1681` loop). → Route as a **CP finding** (a U-CP-96/97 amendment or new unit), not U-RT-123.
- **F-2 — floor-(ii) at-most-once EXECUTION (effect-idempotency).** Non-idempotent external step side-effects (git_push/send_email) can't be made exactly-once by the lease (effect fires, THEN CAS fails). The `idempotency_key` is on the `cp.resume-attempted` AUDIT entry, not the effect. → Separate **floor-(ii) gap finding** (effect-boundary idempotency).
- **F-CC — multi-host AUTO crash-recovery (the constraint-collision).** Cross-host AUTO crash-recovery (case a) is impossible under {I-6 ∧ no-TTL-safety}. **HITL-mediated multi-host recovery (fail-closed to §22.1) is the spec-faithful posture** (Reading A: §7.4/ADR-D1 §1.1 name the durable-store mechanism, not auto-vs-HITL; §22.1 escalation is contract-blessed). → Carry to the **already-deferred O-E3-2** deployment-admissibility gate (multi-host isn't reachable now anyway).

## C. O-E3-2 recommendation INTO E-impl-3 (do NOT silently edit `engine_class_candidate.py`)

local-development is now the **SAFEST** surface (single-host flock complete + local-FS atomic + no clock skew). Recommend WIDENING local-dev admissibility + REPLACING the stale "requires K8s control plane" reason; the real multi-host gate becomes the config-time atomicity declaration + the HITL-recovery posture (F-CC). X-AL-3-clean (a recommendation, not a pre-decision).

## D. CONTRACT/X-AL-3 ledger (C5, confirmed)

| Surface | Disposition |
|---|---|
| backend enum + startup `RuntimeError` | X-AL-3-clean substrate discretion → **build** |
| lost-race → `ABORT_REVALIDATION_FAILED` | faithful → **build** (present) |
| store-unverifiable | startup `RuntimeError`, **OUT of the enum** |
| `PathClass.STATE_LEDGER` | no IS delta → clean |
| case-(ii) fence / floor-(ii) effect-idempotency / multi-host-auto | **fork/route** (F-1 / F-2 / F-CC) |

## The one operator decision (the meaningful gate)

Build **A (single-host-complete + the cross-host CAS *mechanism* / floor iii)** now; route **F-1 / F-2** as findings; carry **F-CC** (multi-host AUTO crash-recovery → HITL-mediated, spec-faithful) to the already-deferred O-E3-2. This honors FULL-SPEC (floor iii builds full cross-host; floor-i multi-host-auto is physics-impossible under I-6, not a defer). Alternatives considered + rejected by 4-way convergence: hand-roll a liveness/TTL lease (the trap — subtly-broken safety advertised as exactly-once); Class-1 ADR fork to relax I-6 (heavy; only if unattended multi-host HA is a near-term requirement).
