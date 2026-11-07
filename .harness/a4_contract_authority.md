# A4 contract authority record

**Status:** Provenance for CP spec v1.131 / plan v2.56 (U-CP-106) and Runtime spec v1.142 /
plan v2.70 (U-RT-159), the A4 typed resume refusal, cleared 2026-11-07 by the ratifications in rows 15 and 17. It maps each authority and evidence
citation in `.harness/class_1_fork_a4_typed_resume_refusal.md` to its filed copy in
`.harness/review-evidence/a4-contract-authority/`, or marks it **GAP**. It is provenance, not
normative content; the contracts live in the spec text. This record clears nothing.

**What is not filed.** None of the A4 source changes or A4 tests are on main. The cited test modules
(`test_child_resume_refusal_propagation.py`, `test_public_nested_resume_refusal.py`,
`test_resume_refusal_propagation.py`) and the preparation commits are unlanded source preparation:
Unit 1 `c71bf24c7a76c292c4e7099b80a3744d60ff46bd`, Unit 2 `cf1c916f252a4f49450d81898de5055984b6b94c` and
public-test commit `bba659dc5c22d381e931fa71922c6d7e5da26483`. Their test counts and results are
historical observations at those heads. They are not new-head, formal, full-gate, CI or installed
evidence. They do not show that A4 works on main.

## Hashes

For a Markdown wrapper that quotes one payload, the SHA256 is of the quoted payload as its header
states, not of the wrapper. For the twelve extracted LIT entries, it is of the one-line compact JSON
entry, with no trailing newline. For the three older wrappers (rows 1, 3 and 4) it is of the payload
followed by one newline; all three reproduce. Row 2 is an exact copy and its hash is of the whole file.

## Authorities and evidence

| # | Fork-record citation | Filed copy (`a4-contract-authority/`) | SHA256 | Attribution and limits |
|---|---|---|---|---|
| 1 | Authorizing bundled arc, LIT `cmt-7d8db0b5-6fe0-4f33-8529-9f1c9dd5e821` | `lit-cmt-7d8db0b5.json.md` | payload `a95c72f30118107f2953d88f3030b2e6c8ec9b44fc11bdc4ec47a0707a9c5f49` | Buford routing record; agent-authored, not human consent. It names seed `619cab32785927142deb01876c260cbb696ec4b1`, the full SHA behind the fork record's `619cab32` |
| 2 | Independent design GO | `a4-opus-design-review.md` | file `4d2716df5f9847ee9a2d62c9b0e584042be8bbe97dfbf2a3ed06f7a20d288a81` | reviewer `40cd9c0e-ad5c-41bb-8899-70c02173cae4` (full UUID in the file's header; the fork record gives the prefix) |
| 3 | RED seed reproduction (root ends `PAUSED`) | `red-seed-excerpt.txt.md`: 28 of 421 lines | excerpt payload `6d4ff591578c98c35155b6a2ff0be145c1dbc4871284028a2549647425f96458` | **GAP:** the full seed log is not filed. The fork record's `10c1a9340aca3bf6a7f19d8e259a06b85b18cf01dfd2ddb8f09f8f8da8b37b3c` is that log's hash, quoted in the excerpt header. It cannot be checked from the repository and differs from the excerpt's own payload hash |
| 4 | Root unit-ID decision (A5 keeps U-RT-158; A4 takes U-RT-159), LIT `cmt-fcde66ad-1705-4ba8-bc49-7a4e03d4b0e0` | `lit-cmt-fcde66ad.json.md` (also filed for A5 as `a5-contract-authority/a4-unit-id-assignment-lit.json.md`) | payload `6762363065e78a1745787228c841e81e6ec4b254881bce716d8ec72c93cdf081` | Agent-authored routing decision, not human consent |
| 5 | Unit 1 completion: 28 of 28 passed, LIT `cmt-a846f038-903d-4786-bfcf-216792c7e833` | `lit-cmt-a846f038.json.md` | payload `40d786ac1ba5c9a47b127343db3a125f531b2f8b83da6ef11acc5c78586544de` | Witness `ecdbd849-5db0-410e-ad1f-c2903fcfbf23`. The same comment records the first Unit 2 run as **FAIL**: 36 of 37, a state-root placement refusal inside a checkout. That failure belongs to the venue, not to A4 behaviour, and the run was not repeated in the same venue. **Partial:** the comment gives witness.json as the prefix `4553889d`; the fork record's full `4553889da2e06b867603842639806b465781721a2d00d5c55e3323fc205cad98` is not in filed evidence |
| 6 | Unit 2 re-observation: 37 of 37 passed, LIT `cmt-8ac926b9-2eff-4ebe-9669-9ddd3d8acac5` | `lit-cmt-8ac926b9.json.md` | payload `57d6671dd432a8c4cbcf9bd12b941cd9a231c47973b057cc629429e71c585ec1` | Witness `ecdbd849-5db0-410e-ad1f-c2903fcfbf23`. **GAP:** witness.json appears only as `dd41799b` here and as the truncated `dd41799b…85ff87` in the fork record, so no full digest exists in the repository. Root verification `cf2c93cd6a9811a5a9878d020c264dd8f073e30edec91c60fb6ba2ec22ce3c59` is not filed |
| 7 | Unit 2 regression modules: 118 of 118 passed, LIT `cmt-68d31297-37ad-4bb4-be22-b8d1e7ab6143` | `lit-cmt-68d31297.json.md` | payload `b0e180b4ea53e491a3faeada7dc072ba9733875501007bbad5f0244f643c5fff` | Witness `ecdbd849-5db0-410e-ad1f-c2903fcfbf23`. **GAP:** root verification `3cad2c657a9b2e09fcdea4fa821e6a21bfeb77013ef3ccceffa39a0e728a8506` is not filed |
| 8 | Runtime criterion 8 mutants, LIT `cmt-e37570f3-bc53-4080-bdd9-ad5563f6bab1` | `lit-cmt-e37570f3.json.md` | payload `559189ac86dfcfad3f796054082c0bec423c54cda5bd5d469cb8f8135ce35200` | Instrument author and observer `ecdbd849-5db0-410e-ad1f-c2903fcfbf23`. **GAP:** root verification `0006509d1731540770f84daf3db169f074755cef0a64a8f45826959748c4bd6a` is not filed |
| 9 | Criterion 7 positive control and omission mutant, LIT `cmt-30c143f1-23a4-4848-ac69-a190a2d93699` | `lit-cmt-30c143f1.json.md` | payload `604cd1b08807581f4576a8017f6e7e15f383343652e36112134f905f871f1c40` | Instrument author and observer `ecdbd849-5db0-410e-ad1f-c2903fcfbf23` |
| 10 | Criterion 7 acceptance, LIT `cmt-0a04e5db-74a1-4d14-9ddd-5790077c0244` | `lit-cmt-0a04e5db.json.md` | payload `79f2d2a1d2b9bbfcba1dd97430f75fa22f4dcae59f2a73e6fd08bf34cfaec52d` | Buford disposition; LIT `created_by` is `unknown`. It carries root verification `1b59eb024025fc52f6b1be12d889d1b9f85697cace982eac6d21d65c376d15c7` in full, the only fork-record root digest in filed evidence. It names the independent source reviewer `bc16c7af-7062-456f-a76e-3732d06516b2`, the full UUID behind the fork record's `bc16c7af`. **GAP:** that reviewer's own result is not filed |
| 11 | A5 normative fold acceptance, LIT `cmt-1953a86d-1182-4359-a2ad-1121ac6f9bda` | `lit-cmt-1953a86d.json.md` | payload `4f628ee9b6ca168e02eb122e50faa7cfc03ae2728d5c7b6635690542d20ca96b` | Buford acceptance of A5 preparation only; LIT `created_by` is `unknown`. A5 is now on main through PR #1635 as Proposed; see `.harness/a5_contract_authority.md` |
| 12 | Pass-1 review of PR #1637 at `36493604356a9d088a173a128c18e774a81738b4`: accepted `merge-gate-concurrency:…:d72d7c6d848c:1` (P1), `…:e50f980e5e5d:1` (P2), `merge-gate-spec-conformance:…:f91f2ae5e755:1` (P2) and `merge-gate-witness-adequacy:…:fecae3316331:1` (P2); rejected `merge-gate-spec-conformance:…:cbea0209b6d6:1` | **GAP:** no copy in this pack | none | Recorded in the root-owned `.harness/merge-gate-log.jsonl`, which this correction commit does not include. Root dispositions; the rejection rests on fresh URL bytes reproducing both published Linux v7.2 hashes and anchors |
| 13 | Criterion 3 conflict disposition, LIT `cmt-5dd4c286-9301-48ce-af16-80753940030b` | `lit-cmt-5dd4c286.json.md` | payload `189e83b638d2f8247d025a35cd0a53f109d85169af9275a318bdb53a85a970ab` | Buford disposition of the named conflict between plan v2.56 criterion 3 and B-39 sequential resume (raised by the independent reviewer at `cmt-70a3ed47-b596-4f46-abe7-80eedb64adde`, author analysis `cmt-8b861cb2-2ca3-4057-9621-496dbd72fd47`, reviewer concurrence `cmt-83c5d403-d800-4bd4-9a8e-5cfa7574f45d`); LIT `created_by` is `unknown`. It authorizes preparing the split criterion; it ratifies no wording (row 17 does) |
| 14 | Independent normative review of the fold, GREEN with zero findings at exact delta `9835e15a4a8f437d6a566ce14b91507fabc1ed68..745f234f0000e9abcd0f87624e64883bd57e1494`, LIT `cmt-553de0a0-3dcd-4af9-b87e-dd9987bad06e` | `lit-cmt-553de0a0.json.md` | payload `32906607d444abeda240e44adf1a840be543f8627fe446f6f03a511546434030` | Reviewer facade-reviewer `01a1b610-2b06-77c1-b691-015100725357`; LIT `created_by` is `unknown`. Contract review only, not a source or execution PASS |
| 15 | Integration-lead ratification of `745f234f0000e9abcd0f87624e64883bd57e1494` (tree `3db85ba4aeada24e87555a4a7b5bc0334a303c8c`) and the mechanical filing delegation, LIT `cmt-756042fc-eb54-4a73-b152-61488707f1a2` | `lit-cmt-756042fc.json.md` | payload `c4d74cfef63453ea2771e9b929eb0728a32b5cd68818c90067b995a4645b1a19` | Buford `01a1b616-990f-7410-9535-15c00b4115af`; LIT `created_by` is `unknown`. Clears CP v1.131, plan v2.56 (before row 17), Runtime v1.142 and plan v2.70; grants no source approval |
| 16 | Independent additional normative review of the criterion 3 amendment, GREEN with zero findings at exact delta `46605451280a5a44a973b2e53d025bc86a495006..6270c548c9716ddd45eec0f7d54372f7bd44b234`, LIT `cmt-ae0b7212-8561-48f0-b2d8-89b21cc689a5` | `lit-cmt-ae0b7212.json.md` | payload `ea58108470cffced418e3bd148cc386be262a57fb57fd2af0698c231ff2a018c` | Reviewer facade-reviewer `01a1b621-6231-7120-80fb-2d7c2a6c6dbc`; LIT `created_by` is `unknown`. Accepted for contract coherence only; the reviewer's rerun had no output and earns no independent execution PASS (row 17) |
| 17 | Integration-lead ratification of the criterion 3 delta (diff SHA256 `9e11704c712a558b440f1775cb4d3606824aa885b8021b7340497faa4d2e23bc`, tree `cc238d343deb2a4248fee3e910f1437c867fd202`), LIT `cmt-633ac3d9-9ba9-4e8d-8949-7ab589564986` | `lit-cmt-633ac3d9.json.md` | payload `c06b903df353850447d14316cd4477776fe7e22f64b14679cde079963b062a5b` | Buford `01a1b65e-f098-7da1-80e2-5f08b446cec5`; LIT `created_by` is `unknown`. Ratifies the four-witness criterion 3 split of plan v2.56; the author construction receipt it cites is author evidence |

The seven extracts in rows 5–11 are exact six-line wrappers. Each holds one complete LIT entry,
every field as exported, from a private root literal snapshot. Each was checked before filing:
wrapper and payload hashes, and a parse-back that equals the literal entry. The five extracts in rows
13–17 use the same wrapper and were checked the same way against a `lit export` snapshot taken
2026-11-07, which also reproduced row 10's filed payload byte for byte.

## Source and version dependencies

These contract files were drafted against cleared Runtime v1.133 / plan v2.64 and are now reconciled
against main `39aa78e8d55f68feb4b2ea76cd87abec5245aebd`. Main carries the four Proposed A4 documents
and this record, but none of the A4 source or A4 tests.

- **Fold onto the current cleared heads (2026-11-07).** By the integration lead's scope and numbering
  decision (LIT `cmt-7836db07-b27b-4248-849b-50101a522c0e`), CP v1.128 is folded as v1.131 over cleared v1.130, Runtime
  v1.136 as v1.142 over cleared v1.141 and Runtime plan v2.67 as v2.70 over cleared v2.69; CP plan v2.56
  stays over cleared v2.55. U-CP-106 and U-RT-159 keep their labels; U-RT-160/161 are unchanged. Cleared
  CP v1.129–v1.130 and Runtime v1.137–v1.141 amend no A4 site, so the A4 semantics carry over unchanged.
  At main `bd8c7efd15a146a2a8a42b999426ae74442de69d`, `audit_signing_errors.py` was last changed by #1616
  and `sub_agent_dispatch.py`'s 17 later added lines name no carrier type, so the carrier bases below
  still hold. Cleared files that cite the former slots keep their bytes.
- **Drafting basis: cleared A3 v1.134 / v2.65.** Cleared 2026-10-04 by
  `.harness/clearance/spec-harness-runtime-v1-134-cleared-2026-10-04.md` and
  `.harness/clearance/implementation-plan-harness-runtime-v2-65-cleared-2026-10-04.md`; contracts on
  main through PR #1633 (`763e726585fced31f7c768ee7f503da1955773fd`), source through PR #1643
  (`8d684b42a1f07ddd43f1c43c093cca5f77764eca`). Its authority is
  `.harness/a3_runtime_fence_fold_authority.md`.
- **The returned-arm carrier keeps both bases under v1.134.** v1.134 amends C-RT-38 (Ollama scope and
  the post-effect fence) and the linked C-RT-16 §14.6.3/§14.6.4 accounting. It names no
  `PostEffectAuditSigningError`, `effect_class`, `result_ref` or C-RT-18 §14.8.11 term, and its
  fence exclusions keep the audit-signing hard failures on their existing carriers
  (`Spec_Harness_Runtime_v1_134.md:72-75`). It touches no §14.7, §14.14.8 or C-RT-24 site. On main,
  `harness-runtime/src/harness_runtime/lifecycle/audit_signing_errors.py` and `sub_agent_dispatch.py`
  were last changed by #1616 (`d2095b18`), not by #1643. The `ChildResumeRefusedError` and
  `PostEffectAuditSigningError` bases that v1.142 §0.1 item 1 requires are therefore those of v1.133.
- **A5 stays Proposed.** Runtime v1.135 / plan v2.66 (on main through PR #1635,
  `01cb8d17b18d7d3b531a75d29d778781f3ac03d1`) amends C-RT-05 only; see
  `.harness/a5_contract_authority.md`. The fold order is A3 (U-RT-157) → A5 (U-RT-158) → A4
  (U-RT-159). Under the accepted release campaign's A5-to-A4 dependency, A4 corrections and
  discriminating tests may be prepared against provisional interfaces. The actual A5 interfaces are bound before an
  affected A4 candidate is frozen or integrated. This record changes no A5 decision.
- **Preparation heads (not on main).** Unit 1 `c71bf24c7a76c292c4e7099b80a3744d60ff46bd` (branches
  `pack/a4-final-u1`, `pack/a4-final-u2`), Unit 2 `cf1c916f252a4f49450d81898de5055984b6b94c`
  (`pack/a4-final-u2`) and public test `bba659dc5c22d381e931fa71922c6d7e5da26483`
  (`test/omarchy-public-resume-refusal`). None of their `harness-*` files cites an A4 contract version
  or unit ID (v1.128/v1.131, v1.136/v1.142, v2.67/v2.70, v2.56, U-RT-159, U-CP-106), so a renumber of these documents
  changes no citation at those heads. The heads must be rechecked at whatever head actually lands.
- **Owed result-preserving carrier.** The preparation heads implement the superseded refusal-only
  returned arm. Runtime v1.142 §0.1 item 1's `RefusedChildResultAuditSigningError` (a
  `ChildResumeRefusedError` and a `PostEffectAuditSigningError` with `effect_class = sub-agent-result`,
  the child `RunResult` and its resolved `result_ref`), plan v2.70 criterion 2, criterion 5's
  returned-arm mutations and criterion 4's real-dispatcher, real-leaf witness are owed source work at
  the applicable head, after the A5 binding above.

Buford owns version numbering, clearance markers and artifact-head rows at filing. A renumber of
v1.142 / v2.70 or v1.131 / v2.56 must update every citation of them in the same change.

## Not in this record

Clearance of v1.131, v2.56, v1.142 and v2.70 is recorded by their four markers in `.harness/clearance/`
(dated 2026-11-07), not by this record. Contract clearance is neither source conformance nor installed
acceptance. Installed N1 and the negative-provenance attempt remain
consent-gated.
