# Implementation Plan: Harness Runtime — v2.66 (delta over v2.65)

**Status:** Proposed. This is the execution map for Runtime spec v1.135's A5 addition, layered on the corrected Proposed v2.65 A3 fold. v2.64 is the last cleared head until v2.65 and this delta are independently reviewed and cleared. Existing unit bodies, including v2.65's U-RT-157 and its execution portions, are unchanged. Number stability follows the spec v1.135 header: a renumber is not content-neutral and must update the citations listed there.

**Revision note (newly Proposed; independent review owed).** Absorbs the spec v1.135 correction and root disposition `cmt-4a845309-0b9e-4f63-9992-ca22917c3ef2`.
- **Revised:** the U-RT-158 Authority line (authority record); Source (the operator doc); acceptance criterion 2 (environment wording, "exactly the five variables"); new §0.1a execution portions.
- **Preserved verbatim (as of this revision):** every other line of U-RT-158 and §0.2.
- **Coverage delta:** the operator doc maps to 158c; the `executable_paths` refusal has no witness (gap, not patched). *(Historical; superseded by the second revision note.)*
- **Dependency delta:** N → 158a → 158b → 158c (acyclic).
- **Finding:** the unit id U-RT-158 collides with the A4 draft plan v2.67; HOLD, not renumbered. *(Historical; settled by root decision `cmt-fcde66ad-1705-4ba8-bc49-7a4e03d4b0e0`.)*

**Second revision note (newly Proposed; independent review owed).** Absorbs the independent review of the N correction (`cmt-151c24f0-6048-4dad-9c69-c21987260072`) and root disposition `cmt-94d7e8aa-aa45-4d0a-91cc-521e3482be5f`. The first note above was kept as written at this revision; it was later annotated (see the fold annotation below).
- **Revised:** criterion 1 adds the directory `executable_paths` refusal; criterion 3 adds its mutation probe; §0.1a gives 158a that probe and the static part of criterion 4, and cites spec sections for each portion.
- **Coverage delta:** spec v1.135 §0 Activation and refusal item 6.4 ("for an `executable_paths` entry, it is a regular file") now maps to criterion 1 and 158a. A witness test was prepared separately and is not part of any accepted head.
- **Unit id:** root decision `cmt-fcde66ad-1705-4ba8-bc49-7a4e03d4b0e0` kept U-RT-158 for A5 and assigned U-RT-159 to A4 (exact LIT snapshot in the authority record). The A4 renumber, the folded heads and the collision recheck are still owed; this plan is not cleared.
- **Preserved verbatim (as of this revision):** every other line.

**Fold annotation (portable fold and final preparation; not part of the original notes).** After these notes were written, the portable fold (`cmt-ba871dbe-7034-4da4-807d-5493f43a81fc`) and final preparation (`cmt-a413de85-5a9e-4987-8c40-c50542d5c7cf`) changed them: the first note's coverage-delta and finding bullets were marked historical; the second note's unit-id bullet now cites the full root decision `cmt-fcde66ad-1705-4ba8-bc49-7a4e03d4b0e0` instead of a host-only scan file; and both notes' "kept as written" and "preserved verbatim" lines are now qualified as of their revision. No acceptance criterion or portion text changed in this annotation.

## §0.1 U-RT-158 — Codex read boundary (Landlock exec launcher)

- **Authority:** Runtime spec v1.135; fork record `.harness/class_1_fork_a5_codex_read_boundary.md`; authority record `.harness/a5_contract_authority.md` (draft; not filed) for the design GO, the initial HOLD, the host-capability observation, the source GO, the N review and the root disposition.
- **Dependencies:** C-RT-05 external-CLI provider construction. No CP, CXA or cross-axis edge.

**Source:**
- `harness-runtime/src/harness_runtime/lifecycle/cli_read_boundary.py` (new): a standard-library launcher plus the pure ruleset-spec builder.
- `harness-runtime/src/harness_runtime/lifecycle/external_cli_provider.py`: the boundary runner, pre-spawn checks, the environment allow-list, private scratch, refusal mapping, and the Codex constructor that refuses without a boundary.
- `harness-runtime/src/harness_runtime/types.py`: `CodexReadBoundaryConfig` and `ExternalCLIProviderConfig.read_boundary`.
- `docs/operations/omarchy-codex-read-boundary.md` (new): the operator guide for the configuration surface.

**Acceptance (provider-free source canaries; disposable children only):**
1. `harness-runtime/tests/test_cli_read_boundary.py`, through the real launcher on this host's Landlock:
   - denied: unrelated `HOME` and `~/.codex` fixture files, the parent's `/proc` `environ`, the `/proc/self/root` escape, and pathname and abstract socket canaries;
   - allowed: home and scratch;
   - an inherited descriptor is closed, including fd 256 above a soft limit lowered to 64;
   - broad allowances (`/`, `/usr`, `/home`, the fake operator `HOME`, its parent), a symlink to that `HOME`, a symlinked ancestor, and the fake `~/.codex` or a directory inside it are refused at launch;
   - a descendant stays confined;
   - pin mismatch, a symlinked or missing executable, a missing allowed path, and unsupported ABI or syscall errors are refused before exec;
   - a non-regular (directory) executable_paths entry is refused at launch (spec v1.135 §0, Activation and refusal, item 6.4).
2. `harness-runtime/tests/test_external_cli_codex_read_boundary.py`:
   - an unconfigured Codex refuses, including with `auth_check=False`, and the optional default degrades;
   - auth and inference argv are wrapped;
   - unsafe or missing homes and a missing `auth.json` are refused before spawn;
   - the fake operator `~/.codex`, a directory inside it, and the runtime's `CODEX_HOME` are refused as `codex_home`;
   - `provider = "codex"` with kind `generic-command` fails validation, and real stage-3a default construction without a boundary degrades (optional) or raises (required) without running Codex;
   - the child environment is exactly the five variables (a dummy secret is excluded);
   - scratch lives under `scratch_root`;
   - exit 125 maps to the typed error;
   - group cancellation reaches an owned fake child.
3. Mutation probes, each turning a named test red:
   - skipping the restriction;
   - a broad-home allowance;
   - a bare-runner fallback;
   - removing the canonical-target check, the protected-root identity check, the sealed interactive residence, `close_range`, or the kind-identity validator;
   - removing the `executable_paths` regular-file check.
4. Existing external-CLI suites still pass. Ruff and pyright (venv) are clean.

Installed Codex version, login, status, inference and the runtime trace are NOT RUN and need separate operator consent.

### §0.1a Execution portions

U-RT-158 is delivered as three portions, in order: N → 158a → 158b → 158c. It is complete only when all three are verified and criteria 1-4 hold together on the combined head. A head carrying only 158a or 158b implements U-RT-158 partially.

- **158a — launcher (inactive).** Spec v1.135 §0, Activation and refusal item 6, and Observable guarantees. `cli_read_boundary.py` and its test. Nothing in production imports it at this head. Criterion 1 and the static part of criterion 4 (ruff and pyright clean on its files), plus mutation probes: skipping the restriction, a broad-home allowance, removing the canonical-target check, the protected-root identity check, the sealed interactive residence, `close_range`, and the `executable_paths` regular-file check.
- **158b — configuration and provider.** Spec v1.135 §0, Configuration, and Activation and refusal items 1-5, 7 and 8. `types.py` and `external_cli_provider.py` with their tests. Criteria 2 and 4, plus mutation probes: a bare-runner fallback and removing the kind-identity validator.
- **158c — operator doc.** Spec v1.135 §0, Configuration (the operator surface). `docs/operations/omarchy-codex-read-boundary.md`; `docs_completeness --check` passes.

**Held elements.** The socket canaries in criterion 1 stay HELD under the standing socket permission and are not waived: U-RT-158 is not complete until they run with permission. CI must run criterion 1 on a runner with measured Landlock ABI 9 or higher and Landlock active; that is currently UNVERIFIED.

**Size.** The unit's landing size includes the authority record, the operator doc, the clearance markers and the pointer updates. No total is claimed here.

## §0.2 Review boundary

- Independent source and design review of the exact head is required.
- Clearance markers and head rows are filed only after it.
- U-RT-157 (A3) review and filing stay independent of this unit.
