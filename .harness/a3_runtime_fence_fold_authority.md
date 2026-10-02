# A3 Runtime fence fold — authority record

This record pins the authority behind Proposed Runtime v1.134 / plan v2.65 and the fork
record `class_1_fork_a3_ollama_mcp_loop_and_post_effect_retry.md`. The cited files live
outside this repository, so this record carries their full SHA256 values and the facts
this contract relies on. Nothing here is a clearance.

## Design authority

**Hash qualification (documentation provenance, not a new verdict).** Attachments that were not Markdown are kept as Markdown documents named `<original>.md`. Each quotes the complete original payload; the SHA256 values in this record are of that original payload (which a reader can extract and hash), not of the surrounding Markdown document.

Exact copies of the cited files and exact LIT comment snapshots (matched by issue and comment ID from a canonical LIT export) are attached under `.harness/review-evidence/a3-contract-authority/` (`lit-cmt-<first 8 hex>.json.md`). The table's SHA256 values are the attached files' bytes.

| Item | Location (outside this repo) | SHA256 | Kind |
| --- | --- | --- | --- |
| Ollama tool-coverage design verdict | `.harness/review-evidence/a3-contract-authority/ollama-tool-coverage-design-verdict.txt.md` (exact copy; origin orchestration workspace `docs/orchestration/review-evidence/ollama-tool-coverage-design-opus-recovery-1/verdict.txt`) | `a63060a91cd34ba5b27718430582c3f0c4c0b0e283b47be2ca5265c67b22a6bf` | read-only design opinion: "GO-to-author for one Ollama model-MCP-tool slice"; reviewer session `4333390d-a5d1-4a57-8ad6-7c00957b33fb`; pinned RC `dff7d6c9` |
| A2 current-main source review, P2-1 | `.harness/review-evidence/a3-contract-authority/a2-audit-source-review-opus.md` (exact copy; origin orchestration workspace `.local/24h-acceptance/a2-audit-source-review-opus.md`) | `82300db3f24364025b5bad1d06d3a0cc47ddf41adb0822cf1eec09bb601c790e` | read-only source opinion at `5d93b0b`: "a provider retry can re-run a tool loop that already dispatched" |

**LIT origin.** Neither file names its own LIT comment. The comments below were matched
by ticket, comment ID and body in a full export of the canonical LIT workspace
`f2adb6e0-9e45-4bed-971c-c6eace4f0e97`, taken 2026-10-01T12:12:43Z. All are on ticket
`arhugula-harness-trial-193`. The export records each author as `unknown`; the sender
named here is the one the comment body states.

| Item | Assignment comment | Lead acceptance comment |
| --- | --- | --- |
| Ollama design verdict | `cmt-b18100f0-8af0-4115-90b3-6a2f47d2f8d1`, 2026-09-26T20:56:05Z. Lead `01a0df5a` assigns the design to Opus reviewer `4333390d` against `dff7d6c9`. | `cmt-d38509b0-1275-4b26-8f48-a2fe562877f5`, 2026-09-26T21:03:16Z. Records the GO-to-author from the sealed evidence directory, with directory seal `b9a541c1823af1324f87f2f038877ec10732b921cdcebdfdd35f05be04a505a5` "verified 2/2". That comment's v1.134/v1.135 numbering is superseded (see the fork record). |
| A2 source review, P2-1 | `cmt-db1faa6c-64dd-40ac-af61-9fe7021ea284`, 2026-10-01T05:26:37Z. Lead `01a0f594` assigns a read-only current-main review at `5d93b0bf` to Opus reviewer `fd3adf93`. | `cmt-24828b8c-8459-4d04-9411-62cb66405054`, 2026-10-01T05:53:24Z. Records the result file and its P2 (a post-tool-effect provider retry can duplicate a tool effect). |

- **Reviewer's own result.** No LIT comment from either reviewer was found. Each result
  exists only as the file pinned above.
- **Directory seal.** The seal is quoted from the comment; it was not recomputed here.

## Source evidence (observed tests, distinct from the opinions above)

- The provider-free RED at base (`test_post_tool_effect_replay.py`: the tool effect ran
  twice) and the independent 26-pass replay at `619cab32` are source tests. They are
  evidence for `619cab32` only, not for any later head.

## Review of this fold

| Item | Location | SHA256 | Provenance |
| --- | --- | --- | --- |
| Independent Opus contract review (HOLD the fold; 4 P2, 2 P3) | `.harness/review-evidence/a3-contract-authority/opus-a3-contract-review.md` (exact copy; origin orchestration workspace `.local/24h-acceptance/opus-a3-contract-review.md`) | `bbdd65072422e45f39202d9f45a83a377ec2aa2792bf3597fddc529b71ebd204` | LIT `arhugula-harness-trial-193` `cmt-6c7d8283-d4f2-4e3f-b1df-01c3160c1338`; reviewer `40cd9c0e`; captured 2026-10-01T10:23:09.307Z |
| A3 landing plan (Unit 1 / Unit 2 split) | `.harness/review-evidence/a3-contract-authority/a3-landing-unit-plan.md` (exact copy; origin orchestration workspace `.local/24h-acceptance/a3-landing-unit-plan.md`) | `9a85faaeed6c6b8d683f156ac8a79c535dbfa9553995eaa4c3896d76b420e12f` | LIT `cmt-1cc2b9e9-66f2-4826-b29d-835af01fc525`; Codex reviewer `01a0f692` |
| Fold assignment | LIT `arhugula-harness-trial-193` `cmt-e6170fae-d47b-4207-9a59-3927fa1d1209` | — | lead `01a0f594` |

## Source and version dependencies

These contract files were drafted against `619cab32785927142deb01876c260cbb696ec4b1`. A
renumber of v1.134 / v2.65 must update every citation below in the same change:

- `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` lines 1510, 1881, 3883
  and 5057 cite "Runtime v1.134".
- `harness-runtime/src/harness_runtime/lifecycle/post_tool_effect.py` line 1 cites it.
- `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py` line 1301
  cites it.
- The test docstrings `harness-runtime/tests/test_post_tool_effect_replay.py` line 4 and
  `harness-runtime/tests/test_ollama_mcp_tool_loop.py` line 1 cite it.
- The A5 (Runtime v1.135 / plan v2.66) and A4 (v1.136 / v2.67) drafts are numbered on top
  of this one; those trees were not read for this record.

Cleared predecessors: Runtime v1.133 / plan v2.64 at main
`5d93b0bf27e4a6c602ffff7dad49e5dd21be1f22`. The §14.6.4 matrix text is in
`Spec_Harness_Runtime_v1_132.md` (lines 4582-4594 at that commit).
