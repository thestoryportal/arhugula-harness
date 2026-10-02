# A4 contract authority record

**Status:** Proposed provenance for CP spec v1.128 / plan v2.56 (U-CP-106) and Runtime spec v1.136 /
plan v2.67 (U-RT-159), the A4 typed resume refusal; not cleared. It maps each authority and evidence
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
states, not of the wrapper. For the seven extracted LIT entries, it is of the one-line compact JSON
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

The seven extracts in rows 5–11 are exact six-line wrappers. Each holds one complete LIT entry,
every field as exported, from a private root literal snapshot. Each was checked before filing:
wrapper and payload hashes, and a parse-back that equals the literal entry.

## Not in this record

There is no clearance status, no clearance marker, no head or pointer row, and no claim that any
item above clears v1.128, v2.56, v1.136 or v2.67. A Proposed document or a source GO is neither
clearance nor installed acceptance. Installed N1 and the negative-provenance attempt remain
consent-gated.
