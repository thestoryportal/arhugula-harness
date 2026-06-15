# E2 — Adversarial Review #1 (genuine harness-adversarial-reviewer)

Severity scale = §2.7.6 Phase-7 execution-fork (Class 1 = halt / Class 2 = in-execution operator decision / Class 3 = informational). Cites verified at HEAD.

**Verdict: HALT — do NOT clear "build items 1-7 as specified."** Single-host (`local-single-host` default) backend is sound + buildable. Blocking defects concentrate in the `shared-store-cas` (cross-host) backend.

## Class 1 (halt — surface to operator before BUILD)

**F-01 — Cross-host crash-recovery (floor i) silently narrowed; the council dropped its own cross-host liveness witness.** A1-C9 explicitly proposed a cross-host monotonic **heartbeat-SEQUENCE** witness (`A1-primaries.md:13,18`); the B reconciliation contains "heartbeat"/"SEQUENCE" **nowhere** — the only surviving liveness witness is `flock`, which the substrate docstring states is **same-host only** (`reconciler_pause_resume_substrate.py:153-160`). Item-3's incarnation-generation is a *fencing* token, not a *reclaim authorizer*. So deleting same-owner re-entry (item 1) removes the only multi-host auto-admit path AND drops its replacement → multi-host crash-recovery cannot AUTO-resume; it fail-closes to `ABORT_REVALIDATION_FAILED` → §22.1 HITL. Presented as a clean win with zero multi-host consequence stated = silent absorption / narrowing of floor (i) on 2/3 surfaces.
- **Reading A (Class 2, in-arc carve-out):** §7.4 floor (i) names the *mechanism* not auto-vs-HITL (`Spec_Control_Plane_v1_33.md:31`); `ABORT_REVALIDATION_FAILED → §22.1` is contract-blessed (`pause_resume_protocol.py:97-98`) → HITL-mediated multi-host replay may be spec-faithful → add an explicit AC.
- **Reading B (Class 1 fork):** if *every* multi-host restart degenerates to HITL, floor (i) auto-recovery purpose is unmet on 2/3 surfaces → route to CP spec §7.4 / ADR-D1.

**F-02 — Joint-unsatisfiability: linearizable cross-host CAS on a bare filesystem is impossible under {I-6 no-vendor ∧ C10 no-TTL/no-probe}; relabeled as "parameterize + assert + fail-closed."** Atomic `os.link`/`O_EXCL` gives a *create* race, NOT linearizable compare-and-swap-on-write-back across hosts without (a) vendored consensus (I-6 forbids) or (b) a liveness/TTL death-detector (C10 refused). The honest statement — {FULL-SPEC cross-host} ∧ {I-6} ∧ {C10-no-TTL/no-probe} may be **mutually unsatisfiable** for true cross-host at-most-once auto-recovery — is never made. Which constraint yields is an **operator/architect constraint-collision decision**, not absorbable by relabeling.

## Class 2 (in-arc revision before BUILD)

**F-03 — Startup atomicity probe gives FALSE CONFIDENCE.** A single-process, one-host "create-temp + double-`link`" probe tests SAME-host link semantics; it **cannot** verify two distinct hosts racing `os.link` serialize. Passes on unsafe stores (gcsfuse/s3fs/NFSv3-no-lock). The real (un-verifiable) gate is the operator attestation, not the probe. Don't label the probe "fail-closed enforcement of cross-host atomicity."

**F-04 — Floor-(iii) false-advertisement at the AC label.** The split-AC routing of F-1/F-2 is structurally honest, BUT the E3 plan labels "Floor (iii) CAS is U-RT-123's load-bearing AC" wholesale (`r-fs-1-e3-plan-decomposition.md:63`) with no case-(i)-vs-(ii) carve-out. Relabel: "floor (iii) — case-(i) claim-race only, single-host-complete; zombie case-(ii) → F-1; cross-host auto-recovery → F-01."

**F-05 — Incarnation identity `{host_id+boot_id+pid+start_time}` is unbuilt + degenerates.** Grep-confirmed it exists nowhere in src (purely proposed). macOS local-dev has no `boot_id` (non-portable on the "safest" surface); containers share node `boot_id` and `pid` is often `1` → `{boot_id+pid}` uniqueness degenerates exactly on multi-host. Specify a portable recipe with per-surface fallbacks or downgrade to "best-effort fencing token, single-host-meaningful."

## Class 3 (informational)

**F-06 — Backend-enum leak-guard must be a real AC + test.** C5's verdict (substrate backend choice = X-AL-3-clean, not a smuggled primitive; startup `RuntimeError` correctly kept OUT of the closed 4-member `ResumeOutcomeKind`) is CONFIRMED-sound. Note: pin "never leak into `harness_cp` / a cleared Protocol signature" as an explicit AC + import-surface test, not an aspiration.

## CONFIRMED SOUND (attacked + held — the strengths)
- Single-host flock crash-recovery (kernel-mediated, auto-released on death) — item 2 correct.
- **The etcd reinterpretation (owner-token mutex → write-back-conditional CAS on `mod_revision`) — a genuine STRENGTH, MORE faithful to the spec's "etcd compare-and-swap" than the defeated owner-identity model.**
- Lost-race → `ABORT_REVALIDATION_FAILED` — contract-faithful.
- [P1] static-actor premise — CONFIRMED real (`engine_recovery_loop.py:96,167`; `workflow_driver.py:1632`).
- Floor (ii) doesn't cover the concurrent case — CONFIRMED (`state_ledger_write.py:198-247`: idempotency-dedupe + timestamp-monotonicity, NO generation/stale-write-rejection; divergent reconcilers compose different keys → both APPENDED).
- F-1 (zombie commit-fence reaching CP) + F-2 (effect-idempotency) correctly OUT of U-RT-123 (driver step-loop `:1681+` has zero lease reference; lease emission deferred at `:1821-1830`).
- X-AL-3 backend enum + IS-AL-1 STATE_LEDGER mapping — clean.

## Verification-shape requirement carried to BUILD
The concurrent-resume AC must exercise genuinely-concurrent OS **processes** (not threads) + a crash-mid-converge (`kill -9` a claim-holder, then retry) on a shared dir. The 14 green WIP tests are single-process. STRUCTURAL CEILING: cross-host cannot be verified in single-host CI → the `shared-store-cas` backend cannot ship labeled "verified"; state that, don't paper over it.
