---
artifact: design-substrate/Spec_Operational_Discipline_v1_34.md
version: v1.34
cleared_at: 2026-07-18T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-1-fork-ratification (B-51/B-52/B-54 OD audit-signing amendment arc; spec-writer apply pass per CLAUDE.md §4.3 back-flow + §4.5)
back_reference:
  - .harness/class_1_fork_b51_b52_b54_od_signing_amendment_arc.md (the ratified filing — ALL TEN gate items RATIFIED 2026-07-18 AS RECOMMENDED, operator decision recorded at PR #1054)
  - design-substrate/Spec_Operational_Discipline_v1_33.md (predecessor — the §21.2.1 SigningBackend seam this delta amends)
  - design-substrate/Spec_Control_Plane_v1_101.md (same-arc CP rider — §13.5.1 tenant amendment, §28.10.4 carve-out, §20.3.1 reconciliation, §20.1.1 historical exception)
  - design-substrate/Spec_Harness_Runtime_v1.md (same-arc Runtime v1.101 rider — flag carrier, MTC validation invariants, prewarm/keepalive disable, §13.5 verifier inputs, §13.4 B-53 row)
merge_commit: pending (pre-merge at filing time; Arc A apply PR)
reviewer_chain:
  - operator ratification (2026-07-18) — all ten gate items AS RECOMMENDED, one decision (fork filing converged over 26 codex rounds pre-gate)
  - council dyad 1 (B-51, C7 primary ⊥ C2 consultant, 2026-07-18) — all nine leg-1 requirements CONFIRM, zero deviations; fifth-segment representation pinned to the writer-normalized tenant tag (one source of truth with the sidecar join key)
  - council dyad 2 (B-52, C7 ⊥ C9 with C1 noted inline, 2026-07-18) — all eight leg-2 requirements CONFIRM, zero deviations; one tension (span-end fail-closed vs hot-path stall) surfaced + probe-resolved on-main by the signing-side breaker; catch-ordering + keepalive-loop precision notes carried into the delta
  - council dyad 3 (B-54, C7 ⊥ C9 with C1 noted inline, 2026-07-18) — all twelve leg-3 requirements CONFIRM, zero deviations; blocking/non-blocking reconciliation probe-resolved (disjoint invocation surfaces); breaker sign/verify asymmetry pinned intentional
  - out-of-family codex review to convergence on the landing PR (recorded at the PR thread)
---

# Clearance — Spec_Operational_Discipline v1.34 (B-51/B-52/B-54 apply pass)

The v1.34 delta transcribes the ratified filing's three legs into OD contract surface: AMENDED §21.2.1 (fifth canonical-message segment carrying the writer-normalized tenant tag, drop-when-`None` byte-compat; the tenant-bearing `sign_audit_entry` API; the MTC tenant-scope bootstrap invariant; `sign_rotation_pair` PROHIBITED at MTC until B-33), NEW §21.2.2 (backend-aware signature verification API — resolver keyed on stored `(algorithm, key_id)`, message-format cutover, authenticated tenant-bound legacy exemption triples, typed failure taxonomy, non-blocking default, UNVERIFIED-at-MTC), and NEW §21.2.3 (`audit_signing_fail_closed` policy — per-persona defaults, explicit-`false`-INVALID-at-MTC, single typed boundary, zeroth-site backend-required invariant, redaction path unconditionally fail-closed, post-effect result-preserving bypass policy). CP-owned and Runtime-owned text is cross-referenced to the same-arc riders, never restated. Verification obligations (witness classes (a)-(f), each PD-8 mutation-probed) bind the impl arc.
