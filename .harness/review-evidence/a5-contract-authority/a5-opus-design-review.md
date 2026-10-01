Actual reviewer fd3adf93, end_turn 2026-10-01T07:27:23.482Z

# A5 Landlock design: source-design GO to author the isolated A5 arc

There are no P1 or P2 findings. The design can meet the contract as written, but only after the enforcement is observed. This is a judgement of feasibility, not a result.

**Authority and inputs:**
- `session-control.json` routes Buford as 01a0f594 and this UUID as reviewer, with `repair_paused=false`.
- I read only `a5-preparation/proposal.md` and `host-capabilities.json`, and I ran nothing.

## Capability shown versus behaviour not yet run
- **Shown on the host:**
  - Landlock is in the active LSM list;
  - a non-mutating query reported ABI 10 and errata 15;
  - Codex 0.159.2 is a static aarch64 ELF reached through mise's `latest` symlink;
  - `~/.codex` is mode 0755 and holds the operator's history, state and config.
- **Not run:** `landlock_restrict_self`, every canary, `codex --version`, `login status`, and any trace.
- **Wording fix:** "This host can enforce that today" should read "has the capabilities to enforce".

## Design judgments
- **The boundary is the right one for this contract.**
  - A launcher that runs before exec at the single spawn site (`_CodexSubprocessRunner`) restricts itself and then execs Codex. Every descendant inherits the restriction and can't lift it.
  - Handling every filesystem right for the ABI makes the rule set deny-by-default.
  - `RESOLVE_UNIX` and the abstract-socket scope close local IPC paths: D-Bus, the keyring, agent sockets and X11.
  - `SCOPE_SIGNAL` doesn't stop the harness signalling inward. Because the launcher execs rather than forks, the pid and process group are preserved, so `_settle_process` and the existing cancellation ownership are unchanged.
  - Network not being handled is deliberate and disclosed.
- **Sound mechanics to keep:**
  - Restricting itself after exec in the child, not in a `preexec_fn` in the threaded parent.
  - Closing every descriptor above 2 before building rules, with the rule descriptors opened `O_PATH|O_CLOEXEC`.
  - `PR_SET_NO_NEW_PRIVS` before restricting.
  - **One requirement to state:** `landlock_restrict_self` and `prctl` act on the calling thread only. The launcher must do both, and the `execve`, from the same single thread, before any other thread exists. CPython with `-I -m` satisfies that if the module starts no threads.
- **Dedicated harness Codex home: yes.** It meets "prevents access to unrelated user files while preserving subscription login" without changing any live authorization.
  - Source can be built before the operator's separate `codex login` consent with `CODEX_HOME` set.
  - A missing home or `auth.json` refuses.
  - Reusing `~/.codex` doesn't meet the contract, as the proposal also concludes.
- **Paths, inodes and links:**
  - **Symlinks:** rules attach to inodes, and a symlink pointing outside is denied at its target.
  - **Hard links:** a sandboxed `link()` can't import an outside inode, because of Landlock's REFER rules and `protected_hardlinks`. The remaining risk is pre-placed links, which the 0700 harness-owned home check addresses.
  - **`/proc`:** keep it denied by default. Magic links such as `/proc/self/root/...` resolve to the target's real location, so they don't bypass the rules, but the canary should prove that.

## Proof obligations for the arc (each must fail closed)
1. **A contract delta first:** a Runtime spec and plan delta with a back-flow record, defining the enforcement contract on the subscription-CLI route. No new H_T primitive.
2. **Source API, no ambient paths:**
   - new config fields for an absolute pinned Codex executable (refusing a final-component symlink or a mise `latest` path) and its expected version or hash;
   - the harness home, required to be 0700 and owned by the harness user;
   - fixed, explicit source defaults for the DNS and TLS allowances: no `/`, `/usr` or `HOME`.
   - **Recommendation:** exec through the verified descriptor (`execveat` with `AT_EMPTY_PATH` or `os.execve(fd)`) to close the gap between checking and executing.
3. **The ABI matrix:** refuse below 9 and on `ENOSYS`, `EOPNOTSUPP` or `EINVAL`. Compute the handled mask from the ABI. Use syscalls 444, 445 and 446 directly, which are the same on every architecture.
4. **One rule-set builder** shared by `--probe` and the real exec path.
5. **Model-free canaries, with errno only:**
   - a random-token file in `$HOME`, expecting `EACCES`;
   - a `~/.codex` path, expecting `EACCES`;
   - the parent's `/proc/<ppid>/environ` and `/proc/self/root/<home canary>`, both expecting `EACCES`;
   - a pathname socket under `/run/user`, expecting `EACCES`;
   - an abstract socket, expecting `EPERM`;
   - positive controls in the harness home and the private cwd;
   - the harness's group SIGKILL still reaching a launched fake child.

   A real restriction runs only inside a disposable child, never in the pytest process.
6. **The runner:**
   - it always wraps, with no unwrapped path;
   - the environment becomes an allow-list (hygiene, not containment);
   - launcher exit codes map to typed refusals;
   - the private cwd moves off `/tmp`.
7. **Owned measurements that need separate authorization, all NOT RUN:** the runtime path set traced with denial logging under the launcher, the shape of token-refresh writes and whether `REFER` is needed, `--version` and `login status`, and one bounded inference.

## P3 (non-blocking)
- **Indirect reads through local TCP services aren't covered.** Network isn't handled, so a local TCP service that serves files remains reachable. That's outside a filesystem boundary and should be stated as a limit.
- **The wording fix above** ("can enforce today" should read "has the capabilities to enforce").
- **Open operator decision:** whether a second login on the same subscription is allowed.

This isn't A5 acceptance or consent to log in or run inference. I made no writes and ran nothing. RELEASED: no handles. Please record this.
