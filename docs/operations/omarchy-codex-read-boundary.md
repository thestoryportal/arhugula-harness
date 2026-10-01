# Codex read boundary on Omarchy

**Codex runs only inside a filesystem read boundary.** A Codex provider without an explicit `read_boundary` refuses to start.

- The default `codex` entry is optional, so it is skipped and the run continues without it.
- A Codex entry you mark `optional = false` without a boundary stops the run with a read-boundary error.

The provider named `codex` always uses this route: a configuration giving it any other `kind` is rejected. This is Runtime spec v1.135 (Proposed); installed acceptance has not run yet.

## What the boundary does

Before Codex starts, a small harness launcher restricts itself with Linux Landlock and then becomes the Codex process. The restriction cannot be lifted, and every process Codex starts inherits it.

| Codex can | Codex cannot |
|---|---|
| execute the Codex binary you pinned by path and SHA-256, and any regular file you list in `executable_paths` (only the pinned binary is hash-checked); whatever they run stays under the same boundary | read your home directory, including `~/.codex` |
| read and write its dedicated home (`codex_home`) | read other processes' `/proc` entries, or reach your files through `/proc/self/root` |
| read and write a fresh scratch directory per call, removed afterwards | connect to local UNIX sockets: agents, keyrings, D-Bus |
| read public DNS and TLS configuration (`/etc/hosts`, `/etc/nsswitch.conf`, `/etc/resolv.conf`, `/etc/ssl/certs`, `/etc/ca-certificates`) | signal processes outside its own boundary |
| use the network (HTTPS to the subscription service) | receive environment variables other than `HOME`, `TMPDIR`, `CODEX_HOME`, `PATH` and `LANG` |

**Limits:**
- The network is not restricted, so a local TCP service that serves files is still reachable.
- A `generic-command` provider under another name runs whatever command you configure, unconfined, including a Codex binary. Generic-command inference is not supported in this release; do not point one at Codex.
- The harness checks that `codex_home` is private and is not your own `~/.codex`, but it cannot see what you put inside it. Keep only the harness login there.
- Claude Code is unchanged.

**When the harness refuses to start Codex.** It refuses before Codex starts, with a read-boundary error naming the reason, when:
- the machine is not `aarch64` or `x86_64`, or the kernel's Landlock ABI is below 9 or unavailable;
- the binary's SHA-256 differs from the pin, or the binary path contains a symlink;
- an `executable_paths` entry is not a regular file (for example, a directory);
- an allowed path is missing, reaches its target through a symlink, or is (or contains) your home directory or a system directory such as `/usr`, `/etc` or `/tmp`;
- `codex_home` is your own `~/.codex`, a directory inside it, or the directory your harness process's `CODEX_HOME` names;
- `codex_home` or `scratch_root` is not a 0700 directory owned by you;
- `codex_home/auth.json` is missing.

## Activating the bounded route

You need three facts the harness cannot guess: the binary's checksum, a dedicated Codex home and a scratch root. The dedicated home must be a new, empty directory, not your existing `~/.codex`. Do not set `CODEX_HOME` in the environment that starts the harness: the harness treats that directory as your interactive Codex home and refuses to grant it. Use the pinned version directory, never mise's `latest`, because the launcher refuses a path containing a symlink.

```bash
# 1. Pin the binary (prints the SHA-256 to copy into the config).
sha256sum /home/<user>/.local/share/mise/installs/codex/<version>/bin/codex

# 2. Create the dedicated home and scratch root (owned by you, mode 0700).
install -d -m 0700 /home/<user>/.local/state/arhugula/codex-home
install -d -m 0700 /home/<user>/.local/state/arhugula/codex-scratch
```

Then add the provider to your runtime TOML. The exact entry below is witnessed to parse by `test_external_cli_codex_read_boundary.py`:

```toml
[[runtime.external_cli_providers]]
provider = "codex"
kind = "codex"
command = "codex"
optional = false

[runtime.external_cli_providers.read_boundary]
executable = "/home/<user>/.local/share/mise/installs/codex/<version>/bin/codex"
executable_sha256 = "<sha256 from step 1>"
codex_home = "/home/<user>/.local/state/arhugula/codex-home"
scratch_root = "/home/<user>/.local/state/arhugula/codex-scratch"
```

`read_only_paths` defaults to the DNS/TLS list above. Override it only with paths that hold no personal data. The harness refuses `/`, `/usr`, `/etc`, your home and anything containing them, including through a symlink. It does not refuse a folder inside your home such as `~/Documents`, so never list one.

## Steps that need your consent (not run yet)

None of these has been executed. Run them only when you have decided to.

1. **Log in once into the dedicated home.** This creates a second login on your ChatGPT subscription and does not copy your existing one. Whether your subscription allows another login is your decision.

   ```bash
   CODEX_HOME=/home/<user>/.local/state/arhugula/codex-home \
     /home/<user>/.local/share/mise/installs/codex/<version>/bin/codex login
   ```

2. **Confirm the version and login status through the boundary**, using the harness's own runner. Set `$HARNESS_PY` to the installed harness interpreter first.

   ```bash
   $HARNESS_PY -c '
   import asyncio
   from pathlib import Path
   from harness_runtime.lifecycle.external_cli_provider import _CodexReadBoundaryRunner
   from harness_runtime.types import CodexReadBoundaryConfig
   cfg = CodexReadBoundaryConfig(
       executable=Path("/home/<user>/.local/share/mise/installs/codex/<version>/bin/codex"),
       executable_sha256="<sha256>",
       codex_home=Path("/home/<user>/.local/state/arhugula/codex-home"),
       scratch_root=Path("/home/<user>/.local/state/arhugula/codex-scratch"),
   )
   runner = _CodexReadBoundaryRunner(cfg)
   for argv in (("codex", "--version"), ("codex", "login", "status")):
       result = asyncio.run(runner.run(argv, stdin="", timeout_seconds=60))
       print(argv[1:], "exit", result.exit_code)
   '
   ```

   Exit 0 for both means the binary runs and the login is visible inside the boundary. A read-boundary error names what refused. If Codex itself fails, it is missing an allowance; record the error before changing anything.

3. **Run the boundary canaries on the installed candidate.** These run no model and no real Codex.

   ```bash
   $HARNESS_PY -m pytest -p no:cacheprovider -q \
     harness-runtime/tests/test_cli_read_boundary.py \
     harness-runtime/tests/test_external_cli_codex_read_boundary.py
   ```

4. **One real inference** through the configured provider, under separate live consent.
