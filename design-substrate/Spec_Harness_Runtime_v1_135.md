# Specification — Harness Runtime v1.135 (delta over v1.134)

**Status:** Proposed. This is the bundled back-flow source arc for A5; its fork record is `.harness/class_1_fork_a5_codex_read_boundary.md`. Runtime v1.133 remains the cleared head until v1.134 and this delta are independently reviewed and cleared.

It is layered on the corrected Proposed v1.134 A3 fold (the A3 C-RT-38 Ollama scope, the post-effect fence and the linked C-RT-16 accounting). Every v1.134 and earlier term is preserved unchanged. The only proposed addition is C-RT-05 "Codex subscription-CLI read boundary" below. Neither v1.134 nor v1.135 is cleared.

**Numbering:** Proposed v1.135, relative to Proposed v1.134. The number is stable only if v1.134 clears first, this fold is accepted, and a current-main collision check finds no other v1.135 cleared first. Renumbering is not content-neutral: A5 source comments cite "Runtime v1.135" (at `a2573ac2`: `harness-runtime/src/harness_runtime/types.py`, `harness-runtime/src/harness_runtime/lifecycle/external_cli_provider.py` and `harness-runtime/src/harness_runtime/lifecycle/cli_read_boundary.py`), as do the A5 tests (`test_cli_read_boundary.py`, `test_external_cli_codex_read_boundary.py`, `test_external_cli_codex_isolation.py`) and the operator doc `docs/operations/omarchy-codex-read-boundary.md`, and the A4 (v1.136) draft is numbered on top of it. A renumber must update every one of those citations in the same change.

**Correction note (newly Proposed; independent review owed).** After the independent review of the first v1.135 draft, this draft states the existing `executable_paths` allowance in C-RT-05: its configuration row, its grant, its non-regular-file refusal and the fact that it is not content-pinned. It also names the supported architectures. The frozen A5 source already implements these. The original feasibility design GO did not explicitly approve the extra field, so this is a new Proposed contract statement, not a retroactive design-GO claim. Authority: `.harness/a5_contract_authority.md` (draft; not filed). [HIGH] for the source facts (read at `a2573ac2`).

- **Trigger:** root disposition `cmt-4a845309-0b9e-4f63-9992-ca22917c3ef2` on the independent N review (three P2s accepted).
- **Scope (C-RT-05 only):** the configuration table (`executable_paths` row); launcher item 6.2 (architectures); item 6.4 (the grant, and the regular-file launch condition); Limits (content pinning).
- **Preserved verbatim:** every other C-RT-05 sentence, including the configured-symlink refusal sentence under Observable guarantees, and every v1.134 and earlier term.
- **Findings surfaced (not patched):** no dedicated witness exists for refusing a non-regular `executable_paths` entry; the configured-symlink refusal sentence remains overstated (retained P3); the unit id U-RT-158 collides with the A4 draft plan v2.67 (HOLD). (Historical, as of this first correction. Since then root decision `cmt-fcde66ad-1705-4ba8-bc49-7a4e03d4b0e0` kept U-RT-158 for A5 and moved A4 to U-RT-159, and a directory-entry witness test was prepared; see plan v2.66's second revision note.)
- **Downstream absorption owed:** plan v2.66 (execution portions, authority and criterion wording), the fork record, and the operator doc. *(Historical: these are now prepared in the drafts; independent formal clearance is still owed.)*

**Fold annotation (portable fold and final preparation; not part of the original notes).** After these notes were written, the portable fold (`cmt-ba871dbe-7034-4da4-807d-5493f43a81fc`) and final preparation (`cmt-a413de85-5a9e-4987-8c40-c50542d5c7cf`) changed them: the "Findings surfaced" bullet gained a historical qualification, and the "Downstream absorption owed" bullet was marked historical. No other sentence of this note changed.

## §0 Change-note (v1.134 → v1.135) — proposed A5 addition

[HIGH] **Codex subscription-CLI read boundary.** A first-release Codex process must not be able to read unrelated user files, and it must still use its subscription login (first-release contract, `profile-contract-decision-1.md`).

**Configuration.** `ExternalCLIProviderConfig` gains an optional `read_boundary: CodexReadBoundaryConfig`, allowed only for kind `codex`. Its fields:

| Field | Requirement |
|---|---|
| `executable` | absolute path |
| `executable_sha256` | 64 lowercase hex |
| `codex_home` | absolute path, the dedicated harness Codex home |
| `scratch_root` | absolute path |
| `read_only_paths` | absolute paths; default `/etc/hosts`, `/etc/nsswitch.conf`, `/etc/resolv.conf`, `/etc/ssl/certs`, `/etc/ca-certificates` |
| `executable_paths` | absolute paths to regular files the process may also execute (for example a dynamic loader); default empty |

A provider whose name equals an adapter kind (`claude-code`, `codex`, `antigravity`, `gemini`, `generic-command`) must have that kind. For example, `provider = "codex"` with `kind = "generic-command"` fails configuration validation, so the named Codex provider cannot reach an unconfined runner.

**Activation and refusal.**

1. A Codex provider with no `read_boundary` and no injected runner fails construction with `ExternalCLIReadBoundaryError` (an `ExternalCLICommandError`), whatever `auth_check` is. The existing mapping makes that `ProviderTransientError`: the default `optional=True` Codex entry degrades, and a required one fails. No Codex process runs.
2. With a `read_boundary`, both the auth check and every inference run only through the launcher.
3. Before every spawn the runtime refuses, with `ExternalCLIReadBoundaryError` and no process, when:
   - `codex_home` or `scratch_root` is missing, unreadable as metadata, not a directory, a symlink, not owned by the effective user, or not mode 0700;
   - `codex_home/auth.json` is absent or its metadata is unreadable (checked with `stat` only; it is never read).
4. Each call gets a fresh private scratch directory from `mkdtemp` under `scratch_root`. It is removed after the process group settles.
5. The child environment is exactly:
   - `HOME` and `TMPDIR` set to that scratch;
   - `CODEX_HOME` set to `codex_home`;
   - `PATH=/usr/bin:/bin`;
   - `LANG=C.UTF-8`.

   No other parent variable is passed. This is hygiene; the read boundary is item 6.
6. **The launcher.** `<harness interpreter> -I -S <launcher> <spec> -- <argv tail>` runs these steps in one thread, before any other thread exists. Any failure prints one stderr line starting `arhugula-read-boundary-refused:`, exits 125 and never runs Codex:
   1. Close every file descriptor at or above 3, including any above the current soft `RLIMIT_NOFILE`. A failed close is a refusal.
   2. Require a supported architecture (`aarch64` or `x86_64`) and Landlock ABI 9 or higher. An ABI query returning `ENOSYS`, `EOPNOTSUPP` or `EINVAL`, or ABI below 9, is a refusal.
   3. Open the executable without following a final symlink. Require a regular file whose SHA-256, read through that descriptor, equals the pin.
   4. Create a ruleset that:
      - handles every filesystem access right from `EXECUTE` through `RESOLVE_UNIX` (bits 0-16);
      - scopes `ABSTRACT_UNIX_SOCKET` and `SIGNAL`;
      - grants exactly:
        - read and execute on the executable file;
        - read and execute on each `executable_paths` file;
        - read, write, create, remove, truncate and refer beneath `codex_home` and the call's scratch;
        - read beneath each `read_only_paths` entry;
        - read and write on `/dev/null` and `/dev/urandom`.

      The runtime declares each allowance by its canonical target. The executable is declared as configured, so a symlinked pin path refuses. The launcher opens each allowance once without following symlinks, and grants that same descriptor only if all of these hold. Otherwise it refuses:
      - the path exists;
      - for an `executable_paths` entry, it is a regular file;
      - it is not a symlink, and the descriptor's path equals the declared path, so a symlink in any component refuses;
      - its device and inode are not those of a protected root or any ancestor of one. The protected roots are the runtime process's `HOME`, `/usr`, `/home`, `/root`, `/etc`, `/run/user`, `/var`, `/tmp` and `/sys`;
      - it is not, does not contain, and does not lie inside a sealed root. The sealed roots are the runtime process's interactive Codex home (its `CODEX_HOME`, else `HOME/.codex`) and `/proc`.
   5. Set no-new-privs, restrict itself, then execute the verified descriptor.
7. The runtime maps exit 125 with the marker to `ExternalCLIReadBoundaryError`. There is never an unrestricted retry or fallback.
8. Cancellation keeps the existing `start_new_session` process-group settle: the launcher becomes the Codex process, with the same pid and group.

**Observable guarantees (source canaries).** Under the launcher, a child:
- gets `EACCES` opening files under the operator's `HOME` or `~/.codex`, outside the allowances;
- gets `EACCES` on `/proc/<pid>/environ` of its parent;
- gets `EACCES` on `/proc/self/root/<denied path>`;
- is denied connecting to pathname UNIX sockets created outside its domain (`EACCES`) and abstract sockets (`EPERM`);
- passes the restriction to its descendants;
- inherits no descriptor at or above 3, including one above a soft `RLIMIT_NOFILE` lowered before launch;
- can read and write inside `codex_home` and its scratch.

The launch refuses, before Codex runs, when an allowance is the operator `HOME` or an ancestor of it, a symlink to one, or a path reached through a symlinked ancestor. It also refuses when `codex_home` is the operator's `~/.codex`, a directory inside it, or the directory named by the runtime process's `CODEX_HOME`.

**Limits (not claimed).**
- Network access is not restricted: HTTPS and any local TCP service remain reachable, including one that serves files.
- A `generic-command` provider under a name other than an adapter kind can run any configured command, including a Codex binary, unconfined. Generic-command inference is a first-release exclusion; closing this needs a contract decision, not command-string matching.
- The runtime cannot prove that `codex_home` holds only harness state. It proves only that the directory is private and is not the interactive residence or an alias of it.
- An allowance under the operator `HOME` other than the interactive residence (for example `~/Documents`) is trusted configuration and is not refused.
- Bind-mount aliases are compared by device and inode by design. No bind-mount case was exercised: UNVERIFIED.
- An unknown future ABI is accepted with the bits 0–16 mask.
- An injected runner is accepted by caller convention.
- Preflight ownership/mode metadata is not bound to the descriptor the launcher grants.
- The executable inode can be modified in place by its owner after verification.
- Only the primary executable is content-pinned. An `executable_paths` file is not hash-checked; it is trusted configuration and runs under the same restriction.
- The Claude route is unchanged.
- The Codex runtime path set, the token-refresh write shape, `codex --version`, `login status` and real inference are unmeasured and need separate operator consent.
- Source canaries are not installed acceptance.

**Scope.** C-RT-05 subscription-CLI provider configuration and process boundary only. No new H_T primitive, CXA row, cross-axis edge or fail class.
