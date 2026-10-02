# Class 1 fork — A4 typed resume refusal (bundled design back-flow + implementation)

**Status: PROPOSED.** Authorized bundled arc (LIT `arhugula-harness-trial-193` `cmt-7d8db0b5-6fe0-4f33-8529-9f1c9dd5e821`) under
the user's autonomous full-readiness instruction. Independent design GO:
`.harness/review-evidence/a4-contract-authority/a4-opus-design-review.md` (exact copy, sha256 `4d2716df5f9847ee9a2d62c9b0e584042be8bbe97dfbf2a3ed06f7a20d288a81`) (reviewer `40cd9c0e`, end_turn 2026-10-01T08:01:23Z).
Every cited authority and evidence item is mapped to its filed copy, or marked GAP, in
`.harness/a4_contract_authority.md`.

## Defect

The installed N1 witness requires a lowered inherited PRE_ACTION set to end the root FAILED with
`orchestrator-workers-child-resume-refused (hitl-gate-config-changed)`, no new pause capture or
effects, then a claim-refused second resume. At seed `619cab32` the leaf refuses with a human fail
class only; Runtime maps any FAILED child to `SubAgentChildFailedError`; the middle fan-out records
the branch done and pauses; the root pauses. Reproduced provider-free against the exported seed
bytes: the root ends `PAUSED` (`.harness/review-evidence/a4-contract-authority/red-seed-excerpt.txt.md`, an exact 28-line excerpt; full-source sha256 `10c1a9340aca3bf6a7f19d8e259a06b85b18cf01dfd2ddb8f09f8f8da8b37b3c`; the full source is not filed, and the excerpt's own payload sha256 is `6d4ff591578c98c35155b6a2ff0be145c1dbc4871284028a2549647425f96458`).

## Disposition

One typed carrier, per the design GO: `ChildResumeRefusal.HITL_GATE_CONFIG_CHANGED`; `ResumeRefusal`
(non-empty reasons + signing fact); `RunResult.resume_refusal` (FAILED only); Runtime re-raises the
carried refusal typed. Fan-out gate-owning mismatches are typed at origin. Contract deltas:
CP spec v1.128 / plan v2.56 (U-CP-106), Runtime spec v1.136 / plan v2.67 (U-RT-159), all PROPOSED.

Revision note: the Runtime unit was drafted as U-RT-158. A5 keeps that label, so A4's unit is
U-RT-159, following the fold order A3 (U-RT-157) → A5 (U-RT-158) → A4 (root decision, LIT
`cmt-fcde66ad-1705-4ba8-bc49-7a4e03d4b0e0`). This is a proposed reconciliation only.

## Named limits and follow-ups

- Other pre-step child FAILED results (material diff, step index out of range) can still be laundered
  into a generic child failure; follow-up.
- The public `api.resume` + durable claim-store integration (second resume claim-refused, zero
  tool/HITL/webhook effects) is a source test committed at a preparation head, `harness-runtime/tests/test_public_nested_resume_refusal.py`; it is unlanded source preparation and not on main. It is committed at `bba659dc5c22d381e931fa71922c6d7e5da26483` and byte-identical in the final preparation head `cf1c916f252a4f49450d81898de5055984b6b94c` (parent `c71bf24c7a76c292c4e7099b80a3744d60ff46bd`). Observed source-only evidence at the preparation heads (each observed once in a clean environment with same-process head, origin and Git-blob provenance; LIT `arhugula-harness-trial-193`; root verification digests in parentheses):
  - Unit 1 `c71bf24c` owning modules: 28 collected, 28 passed (completion `cmt-a846f038-903d-4786-bfcf-216792c7e833`; witness.json `4553889da2e06b867603842639806b465781721a2d00d5c55e3323fc205cad98`).
  - Unit 2 `cf1c916f` owning modules including the public test: 37 collected, 37 passed in a basetemp outside every checkout (completion `cmt-8ac926b9-2eff-4ebe-9669-9ddd3d8acac5`; witness.json `dd41799b…85ff87`; root `cf2c93cd6a9811a5a9878d020c264dd8f073e30edec91c60fb6ba2ec22ce3c59`). An earlier U2 run inside a checkout failed placement; that failure is the venue's, not A4 behaviour.
  - Unit 2 four regression modules: 118 collected, 118 passed (completion `cmt-68d31297-37ad-4bb4-be22-b8d1e7ab6143`; root `3cad2c657a9b2e09fcdea4fa821e6a21bfeb77013ef3ccceffa39a0e728a8506`). The 2593-line dispatcher module was effect-scanned, not read line by line.
  - Runtime criterion 8: baseline passed; the reason-collapse and drop-signing-family mutants of the raised arm each failed the named assertion (completion `cmt-e37570f3-bc53-4080-bdd9-ad5563f6bab1`; root `0006509d1731540770f84daf3db169f074755cef0a64a8f45826959748c4bd6a`).
  - Criterion 7 positive control (accepted `cmt-0a04e5db-74a1-4d14-9ddd-5790077c0244`): an approved public resume ran `witness.a` and persisted one approved `hitl:workflow:n1-leaf:step:1:pre-action` row (5 sidecar rows); omitting the composer's whole 8d append for that key gave 0 target rows (4 total) at the named assertion (completion `cmt-30c143f1-23a4-4848-ac69-a190a2d93699`; root `1b59eb024025fc52f6b1be12d889d1b9f85697cace982eac6d21d65c376d15c7`). Association is fresh-fixture-exclusive; persisted per-run ownership, other-row identity, full-workflow completion and signing side effects are unproven.
  These are source observations at pre-landing preparation heads, not new-main, formal, full-gate, CI or installed evidence. The cited LIT comments are filed as exact extracts; of the digests in parentheses, only criterion 7's root digest `1b59eb02…` appears in full in filed evidence. The others, including the truncated `dd41799b…85ff87`, are GAPs (see the authority record). The instrument author and observer of the criterion 7/8 runs is `ecdbd849`; the independent reviewer is `bc16c7af`. Default tmpfs placement and installed N1 acceptance remain owed. The depth-2 Runtime propagation test still uses a synthesized leaf result.
- Runtime v1.134 / plan v2.65 (A3; on main through PR #1633, `763e726585fced31f7c768ee7f503da1955773fd`) and v1.135 / plan v2.66 (A5; Proposed normative fold accepted in LIT `arhugula-harness-trial-193` `cmt-1953a86d-1182-4359-a2ad-1121ac6f9bda`; on main through PR #1635, `01cb8d17b18d7d3b531a75d29d778781f3ac03d1`) are on main and still PROPOSED; the cleared heads remain v1.133 / v2.64. Lineage must be folded
  in the settled order A3 → A5 → A4 before clearance. No head, pointer, marker, register or roadmap edit is made here.
- Source preparation record (not landing heads, not main evidence): Unit 1 `c71bf24c7a76c292c4e7099b80a3744d60ff46bd` (parent `591bc8256a5fbf95729f69efab5f13f6ad3ad1bc`; typed refusal with all consumers and terminal propagation; 216 ALL non-test changed lines) and Unit 2 `cf1c916f252a4f49450d81898de5055984b6b94c` (parent Unit 1; gate-refusal producers and the public test; 143). **These SHAs, counts and byte-identity claims are historical and must be refreshed when the source lands:** this Proposed document filing carries none of the A4 source or tests, and none is on main. Each unit must be rebased onto the A3/A5 landing (now on main as Proposed), then recounted and re-verified. No formal pass, full gate, CI or main acceptance is inferred from these preparation commits.
- Installed N1 and a separate negative-provenance (wrong receipt digest) attempt remain consent-gated.
