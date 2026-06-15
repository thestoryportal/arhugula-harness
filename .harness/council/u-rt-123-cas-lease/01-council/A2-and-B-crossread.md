# E1-A2 (consultants react) + E1-B (cross-read DEBATE / reconciled disposition)

Genuine dedicated-agent invocations; each adopted its cN SKILL.md, read the verbatim A1 primaries, grounded in source, reacted. C3's full verbatim also at `A2-c3-consultant.md`.

---

## A2 — C1 (orchestration/lifecycle) reaction

**COHERE C10 / CONFLICT C9-placement.** Traced control-flow end-to-end:
- Lease acquired in `attempt_resume` BEFORE diff/revalidate (`reconciler_pause_resume_substrate.py:277`); lost race → `ABORT_REVALIDATION_FAILED` (`:286-297`) — loser never holds the lease.
- Driver fails the run closed on any abort at `workflow_driver.py:1646-1658` **before** the step loop at `:1681`. The step loop has **zero** lease reference / no per-step re-check / no fencing token (read `:1681-1709+`).
- **EFFECT gated at the CLAIM:** correct claim-time CAS → the loser never enters the step loop. `attempt_resume` is the SINGLE gate, upstream of all side effects. **Case (i) two-reconciler claim race → fully closed in U-RT-123.**
- **Zombie (ii):** a holder that passed the claim, GC-paused, got fenced+reclaimed, then WAKES is ALREADY inside the `for` loop — does NOT re-call `attempt_resume`. Only a commit-boundary fence stops it — which is exactly what's absent. C9's hazard is REAL, but it's a guard that doesn't exist anywhere in the CP step-loop, requiring a token threaded `attempt_resume → driver → commit`.
- **T2 verdict (3-way split):** claim-time atomic-CAS + fail-closed = **in U-RT-123**; commit-boundary fence = **NOT U-RT-123-buildable** (reaches CP step-loop U-CP-96/97 + commit) → **halt-route-split-AC**: partial-land the substrate CAS, route the fence as a separate finding.

## A2 — C5 (validation-contract) reaction

X-AL-3 / IS-AL-1 verdicts (grounded in the 4-member closed `ResumeOutcomeKind` `pause_resume_protocol.py:88-101`):
1. **Lost race → `ABORT_REVALIDATION_FAILED`** = contract-faithful (build; already present).
2. **Store-unverifiable → outcome enum** = SEMANTICS STRETCHED. Keep OUT of the enum — it's a startup `RuntimeError` (substrate-precondition), NOT a resume-time revalidation failure. Don't overload `ABORT_REVALIDATION_FAILED` with two meanings (FM-H discrimination failure at enum scale).
3. **C11 backend enum `{local-single-host, shared-store-cas}`** = X-AL-3-CLEAN, buildable — a substrate CHOICE within §7.4 impl-discretion, not a new contract. GUARD: must stay `harness_runtime`-private (never leak into `harness_cp.pause_resume_protocol` / a cleared Protocol signature).
4. **Startup atomicity-assert + fail-closed** = clean deterministic gate; typed RT-config field; fail via a substrate `RuntimeError`, NOT a `ResumeOutcome`. Buildable.
5. **T2 fencing-at-F2-commit** = FORK-FIRST if it requires a CAS-on-append/reject-stale-generation at the F2 ledger (a NEW IS write-time contract; `EntryPayload` append is a closed surface, `response_hash`/`prior_event_hash` IS-internal). PathClass stays clean (`STATE_LEDGER`, no delta).

## A2 — C3 (state-persistence) reaction — C9's punt RESOLVED

- **Empirical (body-read):** F2 `append_ledger_entry` (`state_ledger_write.py:216-227`) does idempotency-key dedupe (→ `IDEMPOTENT_NOOP`) + timestamp-monotonicity rejection, under a module lock — but **NO monotonic-generation field, NO stale-generation write-rejection**; the six-field C-IS-05 §5 entry is inviolate (IS-AL-3). Two divergent reconcilers compose DIFFERENT `idempotency_key`s → both pass dedupe → both `APPENDED`. **Stripe-style exact-key dedupe ≠ a fence.** A fence enforced at the F2 commit = a NEW write-side primitive + a six-field violation → **Class-1 fork / X-AL-3**.
- **Where the fence lives:** the ENGINE-OWNED convergence store (`CRD_RECONCILER_LEDGER`; the `resource_version`-stamped log + claim files), NOT F2. The E3 engine-owns-substrate framing is correct.
- **THE ACTUAL BUILD (C3-Q3):** claim-time CAS present but insufficient (only stops different-owner; never re-checked after the gate). **Write-back-conditional CAS — ABSENT = the fix:** `_append` (`:403-439`) takes no expected-version arg, computes `resource_version = len(prefix)`, ALWAYS appends — monotonic append, NOT compare-and-swap-on-write-back. **Build: make the convergence write-back CONDITIONAL on the claim-time `resource_version` (etcd `mod_revision` write-condition) + an incarnation-unique reclaim-generation bumped per reclaim** (defeats the static-token collapse). → at-most-once COMMIT of the converged-state record, entirely engine-owned, NO F2 touch.
- **T2 honest reach (refines C5):** gating the STEP EFFECT means the CP driver step-loop must CONSULT the engine-owned fence before each step-commit (read engine generation; abort if stale). That READS engine state into CP — **NOT an IS write-primitive change** — but it DOES reach CP. So the commit-fence = U-RT-123 (persist + write-back-conditional CAS + incarnation-generation) **+ a CP consult-before-commit seam**, not pure-U-RT-123, not an IS-primitive fork.
- **T3:** at-most-once EXECUTION stays unreachable (effect fires, THEN CAS fails) — separate floor-(ii) effect-idempotency finding.

---

## E1-B — Reconciled disposition (orchestrator synthesis, reconciled-to-internal-zero)

**Realization = a SYNTHESIS (not a clean A/B/C): "write-back-conditional CAS over the engine-owned convergence store (the etcd `mod_revision` analogue, hand-rolled) + same-host flock + a parameterized-and-asserted shared-store backend, fail-closed."** This is the genuine etcd-CAS the spec names — the council's key correction is that etcd's primitive is *compare-and-swap-on-revision at the write-back*, NOT an owner-identity mutex (which is the defeated [P1] model). All 5 convergence points hold; T1 reconciles (C9's "liveness+fencing" and C10's "atomic-CAS+fail-closed" unify as: the CAS-on-write-back IS the mechanism; same-host flock is the liveness witness; the incarnation-generation defeats the static-actor collapse; NO wall-clock TTL, NO probe-based death-inference).

### BUILDABLE in U-RT-123 (the claim + write-back-conditional layer)
1. **Delete the owner-token same-owner-re-entry model** (defeated/inverted — C9, C3).
2. **Same-host:** keep the per-workflow `flock` (correct liveness witness + serializer — all voices).
3. **Cross-host CAS:** convergence write-back CONDITIONAL on the claim-time observed `resource_version` (etcd `mod_revision` analogue) via the atomic `os.link` claim; **incarnation-unique reclaim-generation** `{host_id+boot_id+pid+start_time}` bumped per reclaim. → at-most-once COMMIT of the engine-owned converged-state record. Engine-owned, NO F2 touch.
4. **Parameterized lease backend** `{local-single-host (default, zero-config), shared-store-cas}` — `harness_runtime`-private (C5's leak guard).
5. **Startup atomicity-assertion:** `shared-store-cas` runs a one-shot probe (create-temp + double-`link` race) + fails closed via a substrate `RuntimeError` (C5: NOT a `ResumeOutcome`; store-unverifiability stays OUT of the closed enum).
6. **Lost concurrent race → `ABORT_REVALIDATION_FAILED`** (contract-faithful — C5; already present).
7. **PathClass.STATE_LEDGER** (no IS delta — C5).

### ROUTE AS FINDINGS (split-AC, NOT buildable in U-RT-123 — X-AL-3, no silent absorption)
- **F-1 (zombie commit-fence / deep floor-iii):** the CP driver step-loop must CONSULT the engine-owned incarnation-generation before each step-commit (abort-stale). A **CP-scope seam** (CP reads engine state — C3's refinement of C5), reaching U-CP-96/97 + the `:1681` step-loop — NOT an IS write-primitive fork. Out of U-RT-123 → split-AC; route as a CP finding.
- **F-2 (floor-ii at-most-once EXECUTION / T3):** effect-idempotency for non-idempotent external step side-effects (the `idempotency_key` is on the audit, not the effect). Separate floor-(ii) gap finding.

### O-E3-2 (recommend INTO E-impl-3; do NOT silently edit `engine_class_candidate.py`)
local-development is now the SAFEST surface (single-host flock + local-FS atomic, no clock skew). Recommend WIDENING local-dev admissibility + REPLACING the stale "requires K8s control plane" reason; move the real gate to multi-host via the config-time atomicity assertion. X-AL-3-clean (a recommendation, not a pre-decision).

**Internal-zero reached** (primaries↔consultants closed): the only open question — whether the deep fence is in-scope — is RESOLVED as split-AC (F-1) by C1+C3+C5 concurrence. Ready for E2 adversarial.
