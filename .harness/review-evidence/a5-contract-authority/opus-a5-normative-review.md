**Preparation verdict: HOLD on all three files: spec, plan and fork.** The reconciliation onto the corrected A3 fold is mechanical and faithful. But three P2s need small normative edits first, and two of them repeat the same classes of finding I raised on the A3 fold:
1. the spec's "grants exactly" list leaves out a grant the source makes;
2. the plan has no execution-portion map for the U1/U2/U3 delivery;
3. the plan's and fork's authority citations can't be resolved from the repo.

This is a preparation review. I'm not attesting clearance or merge readiness.

## Pins and inputs

**Read:**
- the brief and LIT snapshot (`cmt-37f7cb5e…`; root `repair_paused=false`);
- the draft spec (87 lines), plan (46) and fork (46);
- `evidence.md` and the logs: the frozen-vs-draft diffs and the version-citation list.

**Source compared:** frozen A5 at `a2573ac2` (the production diff from my earlier reads, plus the test files as needed) and the corrected A3 fold head `2217c7eb…` (author's pin).

**Laws:** Laws:Application-Spec (with craft), Laws:Code and Laws:Prose (with craft) are retained. I applied only Application-Spec's condition→effect and observed-vs-inferred lenses, because this is an internal design contract, not a clean-room spec.

**Hashes:** the draft SHA256 values are root's and the author's; I can't compute them.

## Reconciliation (verified)

- **Mechanical, as claimed.**
  - Spec: only the header changed (+4/−2): the Status line, layering on the *corrected* v1.134, and a new Numbering paragraph.
  - Fork: two lineage phrases changed. Plan: one Status line changed (+1/−1).
  - The C-RT-05 body, U-RT-158, Open and Clearance are byte-preserved according to the diffs.
- **Citation list is accurate.** The Numbering paragraph's file list matches `a5-version-citations-at-a2573ac2.txt`: 7 source/doc lines and 4 test lines across the three listed files. Listing files without line numbers is the right choice.
- **Predecessor wording is accurate:** v1.133 / v2.64 is the cleared head; v1.134 is Proposed; A3 → A5 → A4.

## P2s

**P2-1: the spec's grant list omits `executable_paths` (spec `:13-21`, `:44-51`).**
- **Source:** `CodexReadBoundaryConfig.executable_paths` exists (types delta: "Extra FILES the process may execute… a directory here refuses at launch"). The runner passes it to the launcher (`launcher_argv`: `executable_paths=_canonical(config.executable_paths)`). The launcher grants each such file `EXECUTE | READ_FILE` and refuses a non-regular file (`_restrict`, the `executable_paths` loop).
- **Spec:** the configuration table has no such field, and item 6.4 says the ruleset "grants exactly" the executable, the two read-write directories, the read-only paths and the two devices.
- **Trigger:** any configured `executable_paths` entry. The default is empty, so default behaviour matches the spec.
- **Impact:** a clearance would certify a security-boundary contract whose "exactly" list is incomplete for a configurable execute grant. That isn't a read escape, because executed files inherit the restriction. The U3 doc's "execute the one Codex binary you pinned" shares the omission.
- **Minimal correction:** add a table row for `executable_paths` (absolute paths to regular files; default empty; a directory refuses at launch). Add the grant "read and execute on each `executable_paths` file". Add a refusal for a non-regular one.

**P2-2: the plan has no execution-portion map, and the doc isn't in it (plan `:5-47`).**
- **Gap:** the packaging delivers U-RT-158 as U1 (inactive launcher), U2 (wired config and runner) and U3 (operator doc). v2.66 has one unit with combined criteria 1–4, and its Source list leaves out `docs/operations/omarchy-codex-read-boundary.md` entirely.
- **Consequence:** this is the same class as the A3 split I flagged and A3 then corrected with §0.1a. A U1-only head either over-claims U-RT-158 or fails criteria 2 and 4. U3 has no plan authority at all.
- **Minimal correction:** add §0.1a with three portions, and state that U-RT-158 is complete only when all three are verified on the combined head. Nothing in the existing unit body changes.
  - **158a:** launcher only; inactive. Criterion 1 plus the launcher probes: skipped restriction, broad-home allowance, canonical-target, protected-root identity, sealed residence, `close_range`.
  - **158b:** types and provider. Criteria 2 and 4, plus the bare-runner-fallback and kind-identity probes.
  - **158c:** the operator doc, with `docs_completeness`.

**P2-3: authority can't be resolved (plan `:7`; fork `:3`, `:8-9`).**
- **Unresolvable citations:**
  - the plan cites "the independent A5 design GO", and the fork says "after an independent design GO", with no location or hash;
  - the fork cites "the independent A5 HOLD review" with no pointer;
  - the fork cites `a5-preparation/host-capabilities.json`, a path in the orchestration workspace, not the repo.
- **Consequence:** this is the same standard the A3 fold met with `.harness/a3_runtime_fence_fold_authority.md`. As it stands, the authority claims can't be checked from the product repo.
- **Minimal correction:** an authority record inside the repo (or an extension of the A3 one) with full SHA256 values and locations for the design GO, the HOLD review and the host-capability observation. Mark any LIT provenance that's missing as an explicit gap. Point the plan and fork at it.

## P3s (document them; they don't block)

- **Criterion wording (plan acceptance 2):** "the environment excludes a dummy secret" is weaker than spec item 5. The test already asserts exact equality with the five variables (`test_external_cli_codex_read_boundary.py:293-299`), so reword the criterion to "exactly the five variables". The author's "partial" flag was right about the wording; the witness itself is complete.
- **Socket canaries (plan acceptance 1):** this criterion requires the socket canaries (`test_cli_read_boundary.py:196-216`), which are under the standing permission hold and were deselected in packaging. The plan should say the socket element stays HELD and can't be waived, and that U-RT-158 isn't complete until it runs with permission.
- **CI prerequisite:** acceptance 1 runs "on this host's Landlock". The plan should state that CI needs a runner with Landlock ABI 9 or higher; that is currently unverified.
- **Architecture not named (spec 6.2):** "require a supported architecture" should name it exactly: aarch64 and x86_64 (`cli_read_boundary.py:65`).
- **Retained P3, unchanged:** spec `:71`, the configured-symlink refusal overstatement.
- **Collision check scope:** besides the version numbers, check the **unit id** U-RT-158 against the A4 draft. I didn't read A4.

## Spec → plan coverage (my check)

- **Covered:** configuration and kind identity; refusal items 1–4, 6, 7 and 8; the observable guarantees (`HOME` and `~/.codex`, parent `/proc/<pid>/environ` and the `/proc/self/root` escape at test `:155-171`; descendants; descriptors; allowed home and scratch).
- **Covered by the test but understated in the plan:** item 5, the environment.
- **Not covered in either the contract or the plan:** `executable_paths` (P2-1).
- **Witnessed but held:** the sockets.
- **Limits:** stated as non-claims, appropriately.

## Author evidence vs my review

- **Author's work:** byte extraction with `git show`, `reconcile.py`, the diffs, the citation list and the coverage audit. These are the author's runs.
- **My review:** reads of the drafts, the diffs and the cited source/test spans.
- **Not run by anyone:** clearance tooling, the full gate, and the socket/CI canaries.

## Not judged

- The A4 draft: its numbering and U-RT id.
- Draft file hashes.
- Whether the corrected A3 at `2217c7eb` differs from `01310c42` beyond the cell-10 closure. That disposition is root's record.

## Still owed (not written here)

1. After the P2 fixes: independent acceptance of the fold; then clearance of A3 first, which is held at the marker permission boundary.
2. Markers for v1.135 and v2.66 in the v1.133/v2.64 format; pointer updates or "no change" entries for `CLAUDE.md`, `.harness/artifact-heads.md`, `.harness/artifact-pointers/*` and the forward registers.
3. A collision recheck of the version numbers and the unit id at landing.
4. The formal review cycle with producer rows, then CI (including the Landlock-ABI and socket-node decisions), main landing and post-main CI.
5. Installed: Codex login, status, canaries and inference, each under its own consent.

RELEASED, no handles held. I made no writes or commands and started no agents.
