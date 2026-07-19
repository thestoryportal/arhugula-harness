---
artifact: design-substrate/Spec_Harness_Runtime_v1.md
version: v1.102
cleared_at: 2026-07-19T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-Class-2-fork-ratification (B-48 apply arc; spec-writer apply pass per CLAUDE.md §4.3 + §4.5)
back_reference:
  - .harness/class_2_fork_b48_sync_subagent_dispatch_offload.md (RATIFIED 2026-07-18 — option B AS RECOMMENDED with all filing-settled riders)
  - .harness/council-dyad-b48-apply-2026-07-18.md (C1⊥C9 dyad — 16/16 CONFIRM, zero deviations; T-perm-3 probe-resolved)
merge_commit: pending (pre-merge at filing time; Arc B apply PR)
reviewer_chain:
  - operator ratification (2026-07-18) — option B as recommended
  - council dyad C1⊥C9 (2026-07-18) — 16/16 CONFIRM; two apply-notes incorporated
  - out-of-family codex review to convergence on the landing PR (recorded at the PR thread)
---

# Clearance — Spec_Harness_Runtime_v1 v1.102 (B-48 apply arc)

v1.101→v1.102: the C-RT-03 sub_agent_dispatch_max_workers field (minor, on the contract-v2 head) + NEW §14.8.10 executor contract (grow-on-demand, occupied+N+S shared-budget admission, atomic reservation, fail-fast never queue, the sharpened admission rule — initial branch-dispatching admission gated at ALL FOUR fan-out sites incl. cancel-policy execution, only frame-releasing teardown of already-admitted branches exempt — plus the three-part cancellation policy with token cascade and job-wide fence, the two-outcome fence-ack contract with the in-flight-at-trip flag, `worker_draining_under_fence` = AMBIGUOUS-EFFECTS/PERMANENTLY TERMINAL, and the §14.8.10.4 pause/resume + selective-contextvar riders with the B-39 boundary and the CP v1.102 §3 full sequencing rule). The C-RT-03 cap field (256, minor on the contract-v2 head) and the reservation-LEASE lifecycle (held to job termination or fence-drain ack, exactly-once release) complete the cleared executor surface. Witness obligations ride the Runtime plan v2.50 delta, each PD-8 mutation-probed.
