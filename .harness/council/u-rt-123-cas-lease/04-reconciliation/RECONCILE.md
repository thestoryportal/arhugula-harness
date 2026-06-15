# Consolidated reconcile (E2b+E3b collapsed) + E3 reviewer convergence

Per the reorder the workflow allows + advisor's proportionality call: the constraint-collision is the operator's decision **by construction** (a value choice, not a reconcilable technical disagreement); the Class-2 findings (F-03/04/05/06) are **accepted, not disputed**. So NO ceremonial full-council re-convene — the orchestrator folds the accepted refinements into the DELIVERABLE.

## E3 — decorrelated reviewers (the signal: 3-way + council = 4-way convergence)

| Reviewer | Family | Saw | Verdict |
|---|---|---|---|
| **Codex** (gpt-5.5) | out-of-family | COLD descriptive primer ONLY | "cross-host automatic at-most-once crash recovery over a bare shared filesystem is **impossible** under the stated constraints. CAS can serialize a metadata race; it is not a death detector and cannot fence unfenced external side effects." Full eval: `03-codex-advisor/codex-eval.md`. |
| **advisor** | in-family | full transcript | F-02 correct from first principles (failure-detector / FLP). The decomposition: etcd CAS (floor iii, case b) ≠ etcd lease/TTL (death-detector, case a). Floor (iii) CAS IS buildable cross-host; floor (i) auto-recovery on multi-host is impossible under I-6 without a vendored lease or a timeout. HITL-mediated multi-host recovery is the CORRECT FULL-SPEC move, not a defer. |

**No divergence to dig into — 4-way convergence (council + adversarial + advisor + Codex), reached from independent angles, is the "ship with confidence" signal.** Codex's independent agreement on the impossibility claim (cold, from first principles) is the decorrelated confirmation the workflow exists to extract.

**Codex's sharpening (folded):** on single-host, **hold the `flock` across the full suffix execution + write-back** → a GC-paused holder still holds the flock; a competitor can't reclaim until the kernel releases it on death → closes the zombie case (ii) ON SINGLE-HOST. (NOTE: holding the lock across the driver step-loop is a CP-scope change — the driver holds the RT lock across `:1681` — so case-(ii) closure is CP-scope regardless of mechanism, consistent with C1's F-1.)

## Folded Class-2/3 findings (accepted)

- **F-03** (probe gives false confidence): the startup atomicity probe is a SAME-host sanity check — honestly labeled as such; NOT a cross-host CAS verifier. The operator config-time declaration is the load-bearing (un-verifiable) gate. Codex independently confirmed.
- **F-04** (floor-iii false-advertisement): U-RT-123's AC relabeled "floor (iii) — case-(i) claim-race only, single-host-complete; case-(ii) zombie → CP finding; cross-host auto-recovery → O-E3-2".
- **F-05** (incarnation identity unbuilt/degenerate): macOS local-dev has no `boot_id`; containers share `boot_id`+`pid=1`. Specify a portable recipe with per-surface fallbacks OR downgrade to best-effort fencing-stamp (single-host-meaningful). Since case-(ii)/multi-host fencing is routed out, the in-U-RT-123 incarnation stamp is best-effort.
- **F-06** (backend-enum leak-guard): pin "no leak into `harness_cp` / a cleared Protocol" as an explicit AC + import-surface test.

## Byte-confirms (both Reading-A checks PASS → in-arc carve-out, NOT a spec fork)

1. **ADR-D1 §1.1** (`ADR-D1_v1_2.md:42`): reconciler-loop row — Concurrent-resume mitigation = "etcd compare-and-swap" (= case b, floor iii, buildable cross-host); Capability-floor = "CRDs persist agent state across restarts" (= the durable store survives restart, satisfied by the engine-owned convergence log). Neither mandates AUTO cross-host crash-recovery. `ABORT_REVALIDATION_FAILED → §22.1` is contract-blessed (`pause_resume_protocol.py:97-98`). → HITL-mediated multi-host replay is spec-faithful.
2. **Multi-host not reachable now:** O-E3-2 (deployment-admissibility) + O-E3-3 (live-K8s) already deferred; §7.2 excludes reconciler-loop at local-development; current materialization is the non-live filesystem proof. → the cross-host auto-recovery constraint-collision RIDES with the already-deferred O-E3-2 gate.
