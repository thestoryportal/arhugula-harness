Independent read-only Opus40cd9c0e final, UTC 2026-10-01T10:23:09.307Z; assignment cmt-6c7d8283-d4f2-4e3f-b1df-01c3160c1338. Captured verbatim by Buford. No execution or clearance claimed.

**Verdict: hold the fold.** At `619cab32`, Proposed Runtime v1.134 and plan v2.65 match the source on almost every behaviour I traced: the provider call and reply parsing, the fence lifetime, the charging rule and the memory-batch validation. But they can't be used as authority yet. Four P2 contract defects need small edits first, and the review, clearance and pointer-update steps still have to happen. The fold should be one substantive contract unit landing before source Unit 1. I checked this against canonical main `5d93b0bf`.

**Pins and inputs:**
- A3 HEAD: `refs/heads/feat/omarchy-ollama-mcp-loop` resolves to `619cab32…`.
- The typed pointer you sent had a garbled path. I read the correct snapshot (`cmt-6c7d8283…`, my UUID). `repair_paused=false`.
- I loaded Laws:Application-Spec and its craft. That law governs clean-room behavioural specs; these are internal design contracts. So I used only its condition→effect and errors-are-contract rules.
- I read the repo's back-flow rules: `CLAUDE.md` §4.4, §4.5 and §11.4, and the `phase-7-back-flow-routing` skill. Laws:Code is retained from earlier.

## What already matches 619 (my reads)

- **Provider boundary covers the call and reply parsing.**
  - Anthropic: `fence.provider_call()` wraps create, the wire-reached mark, await, tool-block extraction, the response bundle and assistant projection (`llm_dispatch.py:3917-3936`).
  - Ollama: the call (`:5088-5092`) and, in a separate guard, usage, mapping, tool calls and the assistant message (`:5112-5119`). Keeping them separate is what lets only the call trigger the first-turn tools fallback.
- **Effects and validation stay outside the provider boundary.**
  - Memory batch validation and the iteration-bound check run before any execution (`:5122-5136`).
  - A memory execution is `entering_effect` (`:5141`).
  - An MCP batch folds `dispatched` into the fence (`:4964-4974`).
- **One effect state per attempt.** `tool_effect_fence.guard()` wraps the whole `infer()` (`:1514-1535`). The claim that turn capture is inside that guard comes from the fork record and the Codex probe; I didn't trace capture's call site.
- **Retry wrapper.**
  - It never retries or advances a carrier, and it records `retry.terminal` and the origin (`retry_breaker_fallback.py:1300-1317`).
  - A provider-origin fault is charged through the generic waiver test and `breaker.cause` (`:1497-1527`).
  - Signing failures, an already-fenced carrier and `BaseException` signals pass through unchanged (`post_tool_effect.py:97-102`).
- **Ollama route behaviours.**
  - The nonce is `uuid4().hex`, minted once per dispatch (`:5082`), with id `ollama:<nonce>:<turn>:<index>` (`:5158`).
  - The superset projection replaces `payload.tools` (`:5068-5076`).
  - Malformed calls are refused (`:5149-5156`).
  - The bound is 16 (`:5134-5136`).
  - Only the first call takes the tools-unsupported retry (`:5095`).
- **The B-84 memory-only exclusion is preserved.** The C-RT-38 arm is chosen only with both a superset and the loop; otherwise the old memory arm runs (`:1877-1902`), and nothing there marks the fence as started.

## P2 contract defects to fix in the fold

1. **The amendment to the half-open matrix is wrong and loose.**
   - The cleared §14.6.4 matrix says "Nine cells, exhaustive over the ways a half-open trial can end" (Runtime v1.132 `:4582-4594`).
   - v1.134 says a provider-origin carrier "is §14.6.4 cell 5". That holds only for transient faults. A malformed reply (row 2b) or a 401/403 is cell 2. A waived fault is cell 3, which re-arms and does not charge, and the code already treats it that way (`:1515-1520`).
   - The non-provider carrier is put "under the existing cells 6-8 disposition" without its own row. It is an ordinary `Exception`, not one of the causes named in cells 6–9, and the spec never states its emission.
   - **Smallest amendment:** add **cell 10, post-tool-effect carrier**.
     - Provider origin: the cell its `fault` would select (2, 3 or 5), with that cell's emission.
     - Non-provider origin: never charged; INCONCLUSIVE → re-arm, as cell 3, with emission as cell 3.
     - In a `closed` breaker: provider origin charges unless waived; non-provider records nothing.
   - Also replace the sentence "In a half-open trial, it is §14.6.4 cell 5".
   - **Not traced:** I took the outer arm that releases an unrecorded trial from the comment at `:1308-1309`.
2. **The plan's execution map can't express the planned two-unit landing.**
   - v2.65 §0.1 is one U-RT-157 unit: one source list (including the Ollama branch), combined acceptance criteria 1–4, and §0.2 "run on the reviewed head".
   - Landing Unit 1 against it would either over-claim U-RT-157 or fail its acceptance criteria.
   - **Amendment:** two explicit portions.
     - **157a:** the shared fence, the retry wrapper and the Anthropic arm.
     - **157b:** the Ollama route.
     - Allocate the criteria and mutation probes between them. In particular, the memory `write_note` 529 case, nonce, superset, fallback, routing and provider-over-memory probes belong to 157b.
     - Name the Anthropic-derived controls Unit 1 needs: non-provider closed/half-open, and identity of cancellation and a tripped fence.
     - State that U-RT-157 is complete only when 157b is verified.
   - This is a changed contract and needs its own independent review.
3. **The authority pointers can't be resolved from the product repo.**
   - Spec v1.134 §Scope and the fork record cite the design verdict at `docs/orchestration/review-evidence/…` "in the orchestration workspace", outside the product repo, with a truncated hash `a63060a9…`.
   - The fork record cites "A2 current-main source review, P2-1" with no pointer at all.
   - Cleared v1.133, by contrast, cites ADRs inside the repo (`Spec_Harness_Runtime_v1_133.md:15`).
   - **Amendment:** full SHA256 values plus a stable record inside the repo (a `.harness` record), or move the authority into the fork record.
4. **The version number is hard-coded in source.**
   - The spec header says a renumber at integration happens "without any change to its content". But source docstrings already cite "Runtime v1.134" (`post_tool_effect.py:1`, `llm_dispatch.py:1510,1881,3883,5057`).
   - Renumbering would leave those stale.
   - **Fix:** freeze the number at fold acceptance (the A5 and A4 numbering already assumes it), or cite the clause rather than the version in source.

## P3 items

- **Tools-unsupported discriminator.** Spec item 4 doesn't state it. The code matches HTTP 400 with the substring `does not support tools` and fails closed if the wording changes (`:5212`, `:5215-5229`). Put that in the spec.
- **Projection required fields.** The projection reads `entry["description"]` (`:4999`). An entry without a description would raise before any effect and go to retry classification. Either state that `description` is required for a superset entry or tolerate its absence. I have not verified that every superset entry has one.

## What still blocks using v1.134 / v2.65 as authority, even after fixes

- **Status:** both files say Proposed. Plan §0.2 requires an independent out-of-family source **and spec** review before clearance markers are filed. The Codex and Opus reviews so far were of source; none was a spec/back-flow review of the fold.
- **Clearance markers missing:** `.harness/clearance/spec-harness-runtime-v1-134-cleared-<date>.md` and the plan v2.65 marker, in the v1.133 marker's format (reviewer chain, file SHA, back-reference to the fork record, supersedes).
- **Derived pointers not updated:** the files on main that name the current head are `CLAUDE.md`, `.harness/artifact-heads.md`, `.harness/artifact-pointers/{spec-heads,plan-heads,runtime}.md`, `.harness/forward-register.yaml` and `.harness/post-phase-8-forward-register.md`. Each needs updating or an explicit "no change" in the fold.
- **CI guard:** `x-al-3-guard.yml` is triggered by `design-substrate/**` changes and requires the paired fork record in the same PR.
- **"Cleared" is not earned by tests passing:** the 26-pass replay and the author's mutation runs are source evidence for 619 only.

## Size, lineage and fold unit

- **Size:** the contract files main→619 total **190 changed lines**: spec 86, plan 72, fork 32, all additions. My reads match the pinned numstat. The inherited figure of 184 was wrong. The fold adds roughly 20–35 lines for the amendments, plus 2 clearance markers and the pointer updates.
- **Lineage:** A5 (Runtime 135 / plan 266) and A4 (Runtime 136 / plan 267) are numbered on top of 134/265. So either the A3 fold clears first, or their predecessor references must be rebased. I didn't read either tree, and I'm not assigning numbers.
- **Recommended fold unit:** one design-substrate plus `.harness` PR containing the corrected v1.134/v2.65, the fork record (with the corrections section kept), the two markers and the pointer updates. Its independent spec/back-flow review happens first. Source Unit 1 (298 lines) follows as a separate Phase 7 PR, then Unit 2 (267). The original proposed bytes and attribution stay preserved.

**Limits:** I ran nothing and wrote nothing, and didn't trace turn capture's call site or the outer release arm. I didn't read A4 or A5. Nothing here is a ratification or clearance.

RELEASED, no handles held.
