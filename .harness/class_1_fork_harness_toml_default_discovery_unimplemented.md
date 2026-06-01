# Class 1 fork — `harness.toml` default-discovery declared by spec §3.7 but unimplemented

**Status:** PROPOSING — awaiting operator ratification (Reading + "workspace root" semantics).
**Filed:** 2026-05-31, during R-100 (`R-100-mvp-operator-usable-cli-shipped`) use-the-product probe.
**Class:** 1 (architectural — the fix shape is non-obvious; "workspace root" is undefined for discovery).
**Blocks:** nothing for R-100 (worked around via option (B) — the `just run` recipe passes `--config harness.toml`). This fork governs the spec-conforming closure.

---

## 1. The divergence

Runtime spec v1.39 §3.7 (line 391) declares:

> **Config file.** Path `harness.toml` at workspace root by default; overridable via `--config <path>` CLI flag.

and §14.18.1 (line 241) declares `--config <path>` as "Override **default** `harness.toml` config-file path."

Both assert that `harness.toml` is discovered automatically at the workspace root when `--config` is omitted. **The implementation does not do this.**

## 2. Evidence (empirically substantiated this arc)

1. **Dead constant.** `DEFAULT_CONFIG_FILE_NAME = "harness.toml"` is defined and exported in `__all__` at `harness-runtime/src/harness_runtime/config_source.py:43`, but a workspace-wide grep finds **no use site** — only its definition + the `__all__` entry. The default-path constant was declared and never wired.

2. **`load(config_file=None)` skips the file layer.** `RuntimeConfigSource.load` docstring (config_source.py:173): "When `None`, the config-file layer contributes nothing (the precedence reduces to env + CLI)." The CLI `run`/`daemon` commands pass `config_file=config` where `config` is the `--config` flag value (default `None`). So with no `--config`, no file is consulted.

3. **Positive-control probe.** With a complete, valid `harness.toml` present at CWD, `uv run harness run <manifest>` (no `--config`) **still** fails:

   ```
   RT-FAIL-CLI-CONFIG-LOAD: Missing required fields:
     - deployment_surface
     - repository_root
     - otel
     - default_topology
   ```

   The file present at CWD is not discovered. Discovery is definitively unimplemented (not merely a missing-file failure).

## 3. The non-obvious part — "workspace root" is undefined

The spec says discover `harness.toml` "at workspace root." But the workspace root is not known *before* config load: `RuntimeConfig.repository_root` is itself a field *inside* `harness.toml`. Discovery cannot key on `repository_root` (circular). Candidate readings:

- **(A) CWD discovery.** Look for `./harness.toml` relative to the process working directory (the dir the operator runs `harness run` from). Standard CLI-tool convention. Simple; matches "just run from your repo root."
- **(B) Upward search.** Walk up from CWD to the filesystem root looking for the first `harness.toml` (git-style). More forgiving of subdir invocation; more surprising.
- **(C) Keep explicit-only.** Treat §3.7 "by default" as aspirational; require `--config` (or the `just` recipe that supplies it) and amend the spec to drop the auto-discovery clause. This is what option (B) for R-100 effectively does at the recipe layer.

Reading (A) is the recommended default (simplest, least surprising, matches the `just run` CWD assumption). Reading (C) is a spec amendment, not an impl fix.

## 4. Resolution path

- If (A)/(B): implement discovery at the CLI/config-source layer (when `--config` is None, attempt `DEFAULT_CONFIG_FILE_NAME` at CWD [+ optional upward search]); fall back to env+CLI-only when absent (preserve today's behavior for the no-file case). Spec-**conforming** — closes the §3.7 gap, no X-AL-3 extension. Needs tests.
- If (C): spec amendment at §3.7 + §14.18.1 dropping/softening the "by default" clause; retire the dead `DEFAULT_CONFIG_FILE_NAME` constant.

ZERO of these block R-100 — the MVP smoke is operator-usable today via `just run` (which passes `--config harness.toml`).

## 5. Tracking

Roadmap entry `R-100-mvp-config-discovery` (BLOCKED on this fork's ratification). The misleading "discovers this file by default" claim in `harness.toml.example` was corrected to describe the actual `--config`-passing flow + a pointer to this doc.
