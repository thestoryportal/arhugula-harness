Attribution: fd3adf93-8bd7-4ea0-96fc-e91952ca8b3f

# A5 subscription-CLI read boundary (main 5d93b0b): source blocker persists for Codex

**HOLD.** The first-release hold reads: "Enforce and test a boundary that prevents access to unrelated user files while preserving subscription login. The route stays held until then." Current source removes the model's tool entry points, but nothing the harness enforces stops the Codex process from reading unrelated user files. So the hold can't close on the current source. Claude's hold is separate and is a proof-only item.

**Authority:**
- `session-control.json` routes Buford as 01a0f594 and this UUID as reviewer, with `repair_paused=false`.
- **The governing contract** is the first-release decision, `/home/robbo/Work/arhugula-trial/evaluation/production-readiness-arch/profile-contract-decision-1.md`: line 8 says "Codex read exposure remains a release hold", and line 44 states the closure condition quoted above.
- **What the Runtime spec says:** the current head, `Spec_Harness_Runtime_v1_133.md`, is a C-RT-03-only change on top of v1.132, and v1.132 has no containment contract for the external CLIs. Its only CLI statement is that the model tool loop excludes them (`:7263`). `external_cli_provider.py:7-10` cites ADR-D7 and C-RT-05 for provider construction, not for containment.

**What I verified myself** (static reading only):
- `current-main-gaps.md` A5 (`:56-65`);
- `external_cli_provider.py:1-60`, `:176-231`, `:360-553`, `:792-906`, `:1050-1125`;
- `tests/test_external_cli_codex_isolation.py`, the list of test names and the header;
- the argv pin in `tests/test_external_cli_provider.py:436-470`.

I ran nothing. Every installed canary is NOT RUN.

## Model tool capability and process filesystem access are separate
- **What source removes: the model's tool entry points.**
  - `_codex_inference_argv` (`:822-872`) passes `--ignore-user-config`, 17 `--disable` feature switches and `-c web_search="disabled"`.
  - The closed JSONL grammar (`:1062-1125`) refuses the whole answer if any tool item or unrecognised item appears.
  - The tests pin the exact argv (`test_external_cli_provider.py:436-470`) and the parser refusals (`test_external_cli_codex_isolation.py:87-580`).
- **What source doesn't constrain: what the Codex process can read.**
  - `--sandbox read-only` limits writes by commands Codex spawns. It doesn't limit reads, so it isn't read containment.
  - The child runs as the same user. It gets the full environment minus five API-key variables, including `HOME`, `CODEX_HOME` and any other secrets (`_scrubbed_child_env`, `:364-368`).
  - Its cwd is an empty private directory (`:503-553`). That cwd isn't a filesystem boundary.
  - There's no bwrap, namespace, Landlock or seccomp wrapper anywhere in the runner.

## P2-1: no enforced read boundary on the Codex route
- **Trigger:** any Codex feature that can read files and isn't on the disable list. Examples:
  - a read or list tool added in a newer CLI version;
  - a built-in tool not gated by these feature flags;
  - instructions or context Codex loads from the user's home directory.
- **Why the current measures don't close it:**
  - The 17 switches are a deny-list of feature names. Nothing pins or checks the Codex CLI version: the only version mention is the comment at `:833`. The comment that "unknown `--disable` switches make older CLIs fail closed" covers older versions, not new tools in newer ones.
  - The JSONL refusal is "detection after the fact, not prevention", in the module's own words (`:1107`). By the time it refuses, Codex has already run the tool and sent its result upstream in the model turn.
- **Impact:** an unrelated user file's contents can reach the provider. The harness then refuses the answer, but the read and the upload have already happened. That's exactly what the hold names.
- **What source does achieve:** the read content won't reach the harness's own output, and the model has no listed tool entry points. That's useful as a second boundary, but it doesn't enforce the hold.

## Claude route
- **Argv** (`:796-815`): `--tools ""` (an empty allow-list of tools), `--strict-mcp-config` with no config, `--safe-mode`, `--permission-mode dontAsk`, `--no-session-persistence`.
- **Environment:** a strict allow-list (`:197-230`), which still includes `HOME` so login works.
- **The Claude hold is different** (`:45`): hook and MCP suppression, an output cap, error hygiene and live grandchild cancellation. That's proof-only. Its canaries are NOT RUN, and nothing here establishes them.

## Smallest enforcing seam
- **Where:** only in `_CodexSubprocessRunner` (`:548-553`), the single production place the Codex process is started (`_PrivateCwdSubprocessRunner._run_process`, `:450-500`). It would wrap the exec in a filesystem allow-list that fails closed if it can't be established.
- **How:** either Landlock (an unprivileged Linux security module whose limits pass to child processes) or bubblewrap or a user namespace. The visible paths would be:
  - read-only: the pinned Codex binary and its runtime libraries, CA certificates, the DNS resolver config, `/proc`, `/dev/null`, `/dev/urandom`;
  - read-write only as needed: the Codex home directory holding `auth.json`, so login and token refresh still work;
  - the private cwd.

  `HOME` would then point to a fresh empty directory. No fallback to an unwrapped run.
- **For consistency:** apply the same allow-list environment that Claude already uses.
- **Required canaries, owned by the harness and run on the installed candidate:**
  1. **A boundary probe independent of the model.** Run a harness-owned reader under the same wrapper against a random-token canary file in `$HOME`, outside the Codex home. The probe must get EACCES or ENOENT. This doesn't rely on what the model does.
  2. **Login is preserved.** Under the wrapper, `codex login status` succeeds and one real inference returns an agent message.
  3. **Fail-closed setup.** If the boundary can't be set up, for example because Landlock or user namespaces are unavailable, the dispatch is refused.
  4. **The tool-item refusal still works.**
  5. **The CLI version is recorded and pinned,** so the disable list is checked against that version.
- **Unknowns to check:**
  - whether the Omarchy kernel's Landlock ABI or unprivileged user namespaces are available;
  - which files the pinned Codex binary needs at runtime and whether it writes outside its home directory under `--ephemeral`;
  - how token refresh behaves when the boundary restricts the home directory.

## P3 (non-blocking)
- **Hard-coded `/tmp`.** The private cwd is always created under `/tmp` (`:519`), ignoring `TMPDIR`. On this host, where `/tmp` is full, every CLI dispatch would fail loudly at `mkdtemp`. That's operational, not a containment issue.
- **Codex's environment is a deny-list.** Codex gets everything except five keys, while Claude gets an allow-list. Credentials such as cloud or GitHub tokens therefore reach the Codex child. The model has no tool to read them, but it's broader than necessary.

## Not established
- I can't judge from source whether the pinned Codex binary has read tools outside the disabled features.
- No installed canary or live dispatch has run for Codex or Claude.
- Whether a decision to accept "pinned version, tool-entry refusal and installed canary" without an OS boundary satisfies "enforce … a boundary that prevents access" is for the user or Buford to rule on. My source reading is that it doesn't: nothing in the harness enforces it. The route should stay held.

I made no writes and ran nothing. RELEASED: no handles. Please record this with my attribution.
