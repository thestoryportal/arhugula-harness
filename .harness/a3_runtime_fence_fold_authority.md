# A3 Runtime fence fold — authority record

This record pins the authority behind Runtime v1.134 / plan v2.65 and the fork
record `class_1_fork_a3_ollama_mcp_loop_and_post_effect_retry.md`. The review evidence
is attached in this repository; external origin paths are historical provenance.
The paired clearance markers below accept source consumption, not landing or installation.

## Design authority

**Hash qualification (documentation provenance, not a new verdict).** Attachments that were not Markdown are kept as Markdown documents named `<original>.md`. Each quotes the complete original payload; the SHA256 values in this record are of that original payload (which a reader can extract and hash), not of the surrounding Markdown document.

Exact copies of the cited files and exact LIT comment snapshots (matched by issue and comment ID from a canonical LIT export) are attached under `.harness/review-evidence/a3-contract-authority/` (`lit-cmt-<first 8 hex>.json.md`). Table hashes cover original payload bytes: the fenced `text` payload with its final newline for `ollama-tool-coverage-design-verdict.txt.md`, and the complete bytes for the originally Markdown files. They do not cover the verdict's Markdown wrapper (wrapper SHA256 `9f23d323ab954de51f01651aa2da21c7e7ec4739a47ee80e997942a0bc429f3b`).

| Item | Repository evidence (historical origin in parentheses) | Original-payload SHA256 | Kind |
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

These contract files were first drafted against `619cab32785927142deb01876c260cbb696ec4b1`.
They are now reconciled against two baselines:

- **Main `c995ec9f9fa5945a40ffe30734b859bb6e88e2a8`** carries these documents and the
  A5/A4 drafts, but none of the A3 source. No main source file cites "Runtime v1.134".
- **Candidate `a06c0abd8d09a78b1fc63ff2b9c2c98b79dcba5d`** (branch
  `ship/a3-source09-20261004`, committed but not on main) implements the integrated A3
  source, including the accepted two-file preparation beyond `47ca58b5`. It is not landed or installed. Its citations must be rechecked at whatever head
  actually lands.

A renumber of v1.134 / v2.65 must update every citation below in the same change. So must
any edit that moves spec line 57, which the candidate cites by line number.

- At `a06c0abd`, `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` lines
  1510, 1881, 3883 and 5057 cite "Runtime v1.134".
- At `a06c0abd`, `post_tool_effect.py` line 1 and `retry_breaker_fallback.py` line 1301
  cite it.
- At `a06c0abd`, `harness-cp/src/harness_cp/retry_fallback_namespace.py` lines 260-261
  give the `retry.post_tool_effect.origin` register row's declaring authority as
  `Spec_Harness_Runtime_v1_134.md:57`, and line 304 cites v1.134 §0.
- At `a06c0abd`, `harness-cp/cp_tests/test_b126_retry_wire_register.py` line 473 cites
  it, as do the test docstrings `harness-runtime/tests/test_post_tool_effect_replay.py`
  line 4, `test_ollama_mcp_tool_loop.py` line 1 and `test_post_tool_effect_cell10.py`
  line 1.
- On main, A5 Runtime v1.135 is a delta over Proposed v1.134
  (`Spec_Harness_Runtime_v1_135.md:1,5`). A4 v1.136 is grounded on cleared v1.133 and
  folds after v1.134 and v1.135 without overlapping their amendment sites, in the order
  A3 (U-RT-157) → A5 (U-RT-158) → A4 (U-RT-159) (`Spec_Harness_Runtime_v1_136.md:12-14`).
  Plan v2.66 is layered on Proposed v2.65
  (`Implementation_Plan_Harness_Runtime_v2_66.md:3`), and plan v2.67 states the same order
  (`Implementation_Plan_Harness_Runtime_v2_67.md:3-5`). CP spec v1.128 line 13 names
  "A3 v1.134".

Cleared predecessors: Runtime v1.133 / plan v2.64 at main
`5d93b0bf27e4a6c602ffff7dad49e5dd21be1f22`. The §14.6.4 matrix text is in
`Spec_Harness_Runtime_v1_132.md` (lines 4582-4594 at that commit).

## Integrated source acceptance and clearance

- **Actual authorizing assignment:** LIT `arhugula-harness-trial-193` `cmt-5b08f51a-a023-4f11-bba6-3970a76bc2a4`, attached as `.harness/review-evidence/a3-contract-authority/lit-cmt-5b08f51a.json.md` (JSON snapshot payload SHA256 `7122a8664845e8fdb7689c985fb327d95e6a402b825803f726c0b556db54c59d`). The body explicitly authorizes the documented bundled-absorption arc; its original sender and historical constraints are retained as evidence.
- **Independent source/spec GO:** Opus session `d83e2830-0511-4caf-bfd8-17170b3dd8e8`, actual result `.harness/review-evidence/a3-contract-authority/source09-independent-review.md` (complete result SHA256 `23eefcb76f4271b182324114ad8530897399c54f56f4c52f7001245a2386af39`). The reviewer read all 14 source paths against the Proposed spec and plan. Its two pending evidence items were supplied by full `just codex-check`, receipt `/mnt/mac/arhugula-artifacts/run-l2t65vtq/receipt.json`: pyright 0 errors/warnings; parity 2658 passed; lane-init 164 passed with bash/zsh; provider-free regression 9399 passed, 2 skipped, 44 deselected, 1 xfailed. Targeted source tests 540 passed and all 22 plan mutations were detected at identical bytes.
- **Exact candidate binding:** `.harness/review-evidence/a3-contract-authority/source09-reviewed-bytes.json.md` pins `a06c0abd8d09a78b1fc63ff2b9c2c98b79dcba5d`, the original review manifest, all 14 source hashes and the terminal gate receipt. The review's historical `47ca58b5` name does not identify the unequal integrated successor; the byte binding does.
- **Lead acceptance:** `.harness/review-evidence/a3-contract-authority/lit-cmt-b5e7d30d.json.md`, actual LIT `cmt-b5e7d30d-8ccc-4440-8fac-6c61b8e22bd4` (snapshot payload SHA256 `42f7e1230556787976cde71ea5d1805ce6e1962c85b3b6b245e65b42f952e08d`), accepts only the bounded source/spec judgment after the missing gates were supplied.
- **Clearance:** `.harness/clearance/spec-harness-runtime-v1-134-cleared-2026-10-04.md` and `.harness/clearance/implementation-plan-harness-runtime-v2-65-cleared-2026-10-04.md` clear source-consumption authority after that independent review. Formal canonical review is still 0/5; source PR CI, main landing, post-main CI and installed Ollama/audit/signing/C-RT-38 acceptance remain owed.
- **Carried notes:** actual open LIT follow-up `arhugula-harness-trial-193.5i4` is attached once as `.harness/review-evidence/a3-contract-authority/lit-followup-193-5i4.json.md`, preserving all three PR1641 notes verbatim and `APPROVE` / `findings=[]`. B-295's schema/prompt conflict and B-298's doc-only/next-pass divergence remain OPEN. B-307's A5/A4 dependency cross-check was already fulfilled by this record's Source and version dependencies; remaining prose/provenance corrections are prepared in this source arc, pending its review and landing.
