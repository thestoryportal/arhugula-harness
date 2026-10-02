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

**Third revision note (PR #1635 pass-1 fix round; newly Proposed; independent review owed).** Absorbs four accepted pass-1 P2 findings at `829caa06`: IDs `<lens>:829caa06150d808cb937923ea6b5d8c41c638e45:<key>:1`, witness adequacy keys `b5019966c535`, `18e304506ed6` and `431d9c18ee0d`, and spec conformance key `0fb7e6390481`.
- **Revised:** the Authority line (pinned rows versus ID-only GAP rows); criteria 1-3; the 158a and 158b probes; Held elements.
- **Coverage delta:** spec v1.135 §0 Activation and refusal items 4 (with item 8's group settle), 6.2 and 6.4 (the `SIGNAL` scope and the bits 0-16 mask) gain real-path criteria and mutation probes. These are new Proposed obligations. No test was run for them, and no prepared source is claimed to meet them.
- The earlier notes' "preserved verbatim" lines speak as of their own revisions.

**Fourth revision note (PR #1635 pass-2 fix round; newly Proposed; independent review owed).** Absorbs two accepted pass-2 P2 findings at `84b896fd`: IDs `merge-gate-witness-adequacy:84b896fd8090518bf9d63b096c7fbe5ab9840bde:<key>:1`, keys `120296876b31` (device-node witness) and `e20abc1fd56b` (cleanup after a group member outlives the leader).
- **Revised:** criterion 1 gains the device-node discriminator; criterion 2's scratch clause requires a group member that outlives the leader; the matching probes, 158a, 158b and Held elements follow.
- **Superseded:** the earlier Held reason that the kernel refuses device-node creation before Landlock decides.
- These remain Proposed obligations: no test was run and no device operation was performed.

**Fold annotation (portable fold and final preparation; not part of the original notes).** After these notes were written, the portable fold (`cmt-ba871dbe-7034-4da4-807d-5493f43a81fc`) and final preparation (`cmt-a413de85-5a9e-4987-8c40-c50542d5c7cf`) changed them: the first note's coverage-delta and finding bullets were marked historical; the second note's unit-id bullet now cites the full root decision `cmt-fcde66ad-1705-4ba8-bc49-7a4e03d4b0e0` instead of a host-only scan file; and both notes' "kept as written" and "preserved verbatim" lines are now qualified as of their revision. No acceptance criterion or portion text changed in this annotation.

## §0.1 U-RT-158 — Codex read boundary (Landlock exec launcher)

- **Authority:** Runtime spec v1.135; fork record `.harness/class_1_fork_a5_codex_read_boundary.md`; authority record `.harness/a5_contract_authority.md` (Proposed; not cleared), which pins the design GO, the initial HOLD, the host-capability observation, the source GO, the first N review and its root disposition `cmt-4a845309-0b9e-4f63-9992-ca22917c3ef2` (rows 2-7). The N-correction review `cmt-151c24f0-6048-4dad-9c69-c21987260072` and its disposition `cmt-94d7e8aa-aa45-4d0a-91cc-521e3482be5f` (row 9), and the fold sources `cmt-ba871dbe-7034-4da4-807d-5493f43a81fc` and `cmt-a413de85-5a9e-4987-8c40-c50542d5c7cf` (row 10), are cited by ID only: GAP, not pinned.
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
   - pin mismatch, a symlinked or missing executable, and a missing allowed path are refused before exec;
   - an unsupported architecture, an ABI below 9, and an ABI query failing with `ENOSYS`, `EOPNOTSUPP` or `EINVAL` are each refused before exec, with exit 125 and the refusal marker, by the real launcher entry point run in a disposable child (spec v1.135 §0, Activation and refusal, item 6.2). The fixture may inject the reported architecture and ABI result as a source-level parameter of that entry point; a call to the pure helper alone does not satisfy this, and the production launcher reads no test switch;
   - a confined child gets `EPERM` signalling a process outside its domain (an unconfined sibling owned by the same user), and succeeds signalling its own confined descendant (item 6.4, the `SIGNAL` scope);
   - outside the grants, a confined child is denied writing, creating, truncating and removing fixture files under the fake operator `HOME`; the same operations succeed inside `codex_home` and scratch (item 6.4, the grants);
   - the applied ruleset handles exactly bits 0-16 (item 6.4). Each right a provider-free fixture can exercise has one denied operation outside the grants and an allowed control inside them: `EXECUTE`, `WRITE_FILE`, `READ_FILE`, `READ_DIR`, `REMOVE_DIR`, `REMOVE_FILE`, `MAKE_DIR`, `MAKE_REG`, `MAKE_SOCK`, `MAKE_FIFO`, `MAKE_SYM`, `REFER` and `TRUNCATE`. `MAKE_CHAR` and `MAKE_BLOCK` use the device-node discriminator below; the rest are HELD (see Held elements);
   - device nodes: an unprivileged confined child's `mknod` of a character device and of a block device outside the grants fails with `EACCES` from Landlock, while the same call under a control ruleset that leaves the right unhandled fails with `EPERM` from the missing `CAP_MKNOD`. No node is created in either case, and an errno alone, without its control, is not the witness. Basis: in upstream Linux v7.2, `filename_mknodat` calls `security_path_mknod` before `vfs_mknod`'s `CAP_MKNOD` check. That is a source reading of `fs/namei.c` (SHA256 `d5498d87be97efd71286e27a30c34ce92a5e059e37540de11e93d1b8aad36c4a`) and `security/landlock/fs.c` (`35b7514d1677e4e537eebf6a1ad747ebd137f263a12b705b2a3d8da81f8b0af0`) at tag `v7.2`, not an observation of the running kernel. Prerequisites: the fixture holds no `CAP_MKNOD`, and no sandbox refuses `mknod` before Landlock; where either fails, this case is HELD and says which;
   - a non-regular (directory) executable_paths entry is refused at launch (spec v1.135 §0, Activation and refusal, item 6.4).
2. `harness-runtime/tests/test_external_cli_codex_read_boundary.py`:
   - an unconfigured Codex refuses, including with `auth_check=False`, and the optional default degrades;
   - auth and inference argv are wrapped;
   - unsafe or missing homes and a missing `auth.json` are refused before spawn;
   - the fake operator `~/.codex`, a directory inside it, and the runtime's `CODEX_HOME` are refused as `codex_home`;
   - `provider = "codex"` with kind `generic-command` fails validation, and real stage-3a default construction without a boundary degrades (optional) or raises (required) without running Codex;
   - the child environment is exactly the five variables (a dummy secret is excluded);
   - scratch lives under `scratch_root`. The owned fake child leads its process group and leaves a group member that outlives it and keeps using scratch. Scratch still exists after the leader exits, until that member is reaped, and is deleted only after the whole group settles, on success, on error and on cancellation (items 4 and 8);
   - exit 125 maps to the typed error;
   - group cancellation reaches an owned fake child.
3. Mutation probes, each turning a named test red:
   - skipping the restriction;
   - a broad-home allowance;
   - a bare-runner fallback;
   - removing the canonical-target check, the protected-root identity check, the sealed interactive residence, `close_range`, or the kind-identity validator;
   - removing the `executable_paths` regular-file check;
   - omitting the architecture or ABI check from the launcher entry path, or moving it after exec;
   - dropping `SIGNAL` from the scoped set, or narrowing the handled mask (the denial case of each exercisable right goes red; omitting bit 6 or 11 turns the device-node `EACCES` case into `EPERM`);
   - deleting the scratch cleanup, or running it once the leader is reaped but before the outliving group member settles.
4. Existing external-CLI suites still pass. Ruff and pyright (venv) are clean.

Installed Codex version, login, status, inference and the runtime trace are NOT RUN and need separate operator consent.

### §0.1a Execution portions

U-RT-158 is delivered as three portions, in order: N → 158a → 158b → 158c. It is complete only when all three are verified and criteria 1-4 hold together on the combined head. A head carrying only 158a or 158b implements U-RT-158 partially.

- **158a — launcher (inactive).** Spec v1.135 §0, Activation and refusal item 6, and Observable guarantees. `cli_read_boundary.py` and its test. Nothing in production imports it at this head. Criterion 1 and the static part of criterion 4 (ruff and pyright clean on its files), plus mutation probes: skipping the restriction, a broad-home allowance, removing the canonical-target check, the protected-root identity check, the sealed interactive residence, `close_range`, the `executable_paths` regular-file check, the architecture or ABI check on the entry path, the `SIGNAL` scope and the handled mask, including bits 6 and 11.
- **158b — configuration and provider.** Spec v1.135 §0, Configuration, and Activation and refusal items 1-5, 7 and 8. `types.py` and `external_cli_provider.py` with their tests. Criteria 2 and 4, plus mutation probes: a bare-runner fallback, removing the kind-identity validator, and deleting the scratch cleanup or running it after the leader is reaped but before the group settles.
- **158c — operator doc.** Spec v1.135 §0, Configuration (the operator surface). `docs/operations/omarchy-codex-read-boundary.md`; `docs_completeness --check` passes.

**Held elements.** The socket canaries in criterion 1 stay HELD under the standing socket permission and are not waived: U-RT-158 is not complete until they run with permission. CI must run criterion 1 on a runner with measured Landlock ABI 9 or higher and Landlock active; that is currently UNVERIFIED. `IOCTL_DEV` has no provider-free witness and stays HELD until a fixture shows a device ioctl denied by Landlock rather than by the device. `MAKE_CHAR` and `MAKE_BLOCK` are HELD only where the device-node case's prerequisites fail. `MAKE_SOCK` is listed as exercisable, but its witness needs `bind()` on a pathname socket; whether the standing socket permission covers that is open (B-308), and nothing here waives that permission. `RESOLVE_UNIX` is witnessed only by the HELD socket canaries.

**Size.** The unit's landing size includes the authority record, the operator doc, the clearance markers and the pointer updates. No total is claimed here.

## §0.2 Review boundary

- Independent source and design review of the exact head is required.
- Clearance markers and head rows are filed only after it.
- U-RT-157 (A3) review and filing stay independent of this unit.
