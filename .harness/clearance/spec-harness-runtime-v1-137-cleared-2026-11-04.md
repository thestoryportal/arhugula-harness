---
artifact: design-substrate/Spec_Harness_Runtime_v1_137.md
version: v1.137
cleared_at: 2026-11-04T16:38:35Z
clearance_status: cleared
clearance_type: Phase-7-absorbed-via-fork-doc
back_reference:
  - ".harness/class_1_fork_runtime_resume_cli_supersession.md"
  - ".harness/runtime-resume-contract-authority.md"
  - "LIT arhugula-harness-trial-193 cmt-7cc5fc50-f3cc-4592-a441-4f1f5198349e (Runtime/OD ratification at H 002f40a658bc75a9447c9a563ad637c81bb6c336, portable snapshot)"
  - "LIT arhugula-harness-trial-193 cmt-9733f3e9-e3e7-4c8a-97b5-d3770f8c0f40 (ratification of exact H eb607692d19e472cf8c3f45734f90f5131e01f9f: IS C-IS-01 and the Runtime B3/B8 amendment; OD unchanged, portable snapshot)"
merge_commit: "pending (docs contract PR; ratified contract head eb607692d19e472cf8c3f45734f90f5131e01f9f; no main landing claimed)"
reviewer_chain:
  - "Independent Codex review GREEN of the Runtime/OD deltas at exact H 002f40a6, reviewer implementer 01a1a70f: LIT cmt-53662ef5-eeea-4317-87fb-1d3e03fd487d"
  - "Independent Codex review GREEN of the C-IS-01 companion and Runtime B3/B8 correction at exact H eb607692, reviewer implementer 01a1a739: LIT cmt-b58fbcee-7f94-4d43-821b-e61798caa3f9; review SHA256 39ec78306c553ab42b6ffffb96051a16bfc8d27bc180fa24b24bb9bce957574e"
  - "Buford integration-lead ratification cmt-7cc5fc50 and cmt-9733f3e9; profile-coder applied this marker as the delegated mechanical apply, which Buford verifies before landing"
supersedes: spec-harness-runtime-v1-134-cleared-2026-10-04.md
---

# Clearance — Runtime v1.137

This marker clears the ratified Runtime resume contract for source consumption: the supersession record and the `superseded` read attribution, the ninth B-313 arm `pause-record-superseded`, the `harness resume` subcommand with exits 6 and 7, the Rule B7 installation pause-journal root as the only journal location with an unresolved root refused as `protocol-not-bound`, and the Rule B8 fail-closed cutover that keeps the operator-only pre-upgrade inventory. Authorities and evidence snapshots are pinned in `.harness/runtime-resume-contract-authority.md`.

This marker does not clear the Proposed A5 (v1.135, plan v2.66) or A4 (v1.136, plan v2.67) deltas. v1.137 amends no site they amend; their fold and the U-RT-160 unit-ID recheck remain owed at their landing. It accepts no implementation and does not expose `harness resume`. Physical pause-journal storage remains Buford-owned and unselected; it gates accepted 160a behavior, resume exposure and installed acceptance. PR CI, main landing, post-main CI and installed acceptance remain owed, and the original B-314 engine-native obligation stays open.
