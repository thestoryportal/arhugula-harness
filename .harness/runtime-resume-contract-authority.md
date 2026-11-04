# Runtime resume contract authority record

**Status:** Proposed provenance for Runtime spec v1.137 / plan v2.68 (superseded-record refusal and
`harness resume`), filed at this path; not cleared. It records where each authority the contract
relies on lives and its exact bytes. It is provenance, not normative content: the contract's behaviour
lives entirely in the spec text. This record does not clear, ratify or release anything.

The SHA256 values below were computed on 2026-11-04 from the files at the listed host origins, all
under the root orchestration checkout `.local/release-campaign-20261103/`. Those files are host-only
and are not copied here. The three LIT entries are extracted into
`.harness/review-evidence/runtime-resume-contract-authority/<file>`; each SHA256 is of the one-line
compact JSON payload in its document, not of the Markdown document or of the source export
(`a3c6ddc4a0f638cf5b856e36143182d2884cacfc05cbba9b0e160458c3061daf`, retained host-only at
`.local/release-campaign-20261103/profile-coder-2130a477/lit-export-20261104.json`).

## Authorities

| # | Authority | Copy / host origin | SHA256 | Attribution / LIT |
|---|---|---|---|---|
| 1 | B-310 v4 CLI resume request definition (the request, results and exits, required witnesses) | host-only `profile-coder-3fa0757d/b310-proposal-v4/proposal.md` | `9a6f07f05d239f2d32541ae4eaeab958ec8312c6242d78bb911b602ae56a43ed` | author profile-coder `3fa0757d`; independent GREEN pass 3 `cmt-20aa995a-a179-403f-8b2f-adb2b4d394c0` (ID only; bytes not pinned here) |
| 2 | Integration-lead disposition: B-310 v4 definition accepted; B-314 broadened to the superseded-record prerequisite with the original engine-native obligation kept open; B-313 ninth-arm direction; one combined contract with a named author and reviewer | host-only `buford-continuation-01a1a5c4/b310-v4-definition-disposition.json`; LIT entry `lit-cmt-fe2c7b08.json.md` | file `a1f8713e9a7143500152e4eb9190cd08c0459088aa17f95374618de5ef137eba`; entry `655081478efc1c7bebe22008c9bc8c753c070722168402dd8ed9b8382784feec` | LIT `cmt-fe2c7b08-00c3-4838-8b9e-562d34699de4` (body FROM Buford integration lead `01a1a61a`; LIT `created_by` `unknown`). Agent-authored routing and scope decision under the accepted release campaign, not direct human consent |
| 3 | B-313 v2 closed root refusal value (eight arms, MCP and CLI presentation, required proof) | host-only `buford-continuation-01a1a5c4/b313-proposal-v2/proposal.md` | `c63b16f754b4298790e6682d1b435f7def232a50d2c7287eb97cccd8b3e9dfc3` | Buford-authored proposal. The first independent B-313 review pass (HOLD, facade-reviewer `01a1a5ea`) is spent: `cmt-e57e2b45-0cd1-495f-a401-17ffb5105f4c` (ID only; bytes not pinned here) |
| 4 | Combined-contract work record: one candidate covering items 1–3, author, reviewer, baseline | LIT entry `lit-cmt-9a055b8f.json.md` | `9355786af7f6984a5b3ecb2df569fb1acff9c769f1cbf27c7d0163e2c26b79af` | LIT `cmt-9a055b8f-010e-47ae-88f4-de8a21817bbc`, `created_by` `claude_dcd8fbeb-5a25-4c49-93f9-a632ef4d0813` (profile-coder author), under claim `cmt-792618a5` |
| 5 | Author grounding: mechanism facts and the open questions Q1–Q5 at H `14b785d8` | host-only `profile-coder-dcd8fbeb/combined-contract-grounding.md` | `231f2cbf62306569ce1fda68d561eaee1580f00ba0a46bab5403b76bfaf01a90` | profile-coder `dcd8fbeb`; recorded under item 4 |
| 6 | Author closure of Q1–Q5 (single enforcer, record format, reader semantics, precedence, witnesses), the direct input to spec v1.137 | host-only `profile-coder-ccb4ae89/q1-q5-closure.md`; LIT entry `lit-cmt-bfd03da3.json.md` | file `c4cd24fd2d0498d41fdd7540ef073f5a77f7cda9d3587b70527f06da36168439`; entry `b9bf23d8a186b30fc900e1c31ede9c1753f92ef53dbbb6e18fff2dfd2a543eae` | LIT `cmt-bfd03da3-7b82-4e01-8350-bd445944f82c`, `created_by` `claude_ccb4ae89-f171-455d-a075-1836f4037e4b`. Author decisions, not independently reviewed or ratified before this candidate's review |
| 7 | Integration-lead disposition of the first correction: B-310 v4 cross-binding invariant kept with no binding exception (spec Rule B7 records the missing shared authority); companion OD C-OD-30.5.1 owner and bounded OD spec/plan delta paths | LIT entry `lit-cmt-1ba063e7.json.md` | `a8be8e03b25446e558777ec75fadb446c1569fc8b6c52277d3e82c059b900da2` | LIT `cmt-1ba063e7-3bd6-42df-b628-639aeed7f2bb`, Buford integration lead `01a1a61a` |
| 8 | Integration-lead disposition of the second correction HOLD `cmt-1087cb00`: the Rule B7 root is the only journal location (binding-cell fan-out removed); prerequisite owners named: retained root storage selection and binding evidence Buford, C-IS-01 companion profile-coder under claim `cmt-792618a5` | LIT entry `lit-cmt-8b76cb48.json.md` | `550bd4961b5ad9c1dc13c964571f137997c22ade8a2ab841ac76d282965e9c51` | LIT `cmt-8b76cb48-6e7a-4d2c-8e83-e7dc2fc62e64`, Buford integration lead `01a1a61a` |

## Portability

The pack at `.harness/review-evidence/runtime-resume-contract-authority/` holds five extracted LIT
entries (items 2, 4, 6, 7 and 8), each one complete entry with every exported field. The four host files are
pinned by SHA256 only; a reviewer reads them at the host origin. Items 1 and 3 cite their review
comments by ID only. Copying bytes would not establish a missing LIT link, and none of these items is
human consent.

## Not in this record

There is no clearance status, no clearance marker content, no head or pointer row, and no claim that
any authority above clears or ratifies v1.137 or v2.68.
