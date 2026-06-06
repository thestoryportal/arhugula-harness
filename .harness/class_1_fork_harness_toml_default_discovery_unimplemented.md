# Class 1 fork — `harness.toml` default-discovery declared by spec §3.7

**Status:** ✅ APPLIED-AS-READING-A — CWD discovery ratified by operator 2026-06-06; implementation already shipped at PR #279 (`a394032`).
**Filed:** 2026-05-31, during R-100 (`R-100-mvp-operator-usable-cli-shipped`) use-the-product probe.
**Class:** 1 (architectural — the fix shape is non-obvious; "workspace root" is undefined for discovery).
**Blocks:** nothing for R-100 (worked around initially via option (B) — the `just run` recipe passes `--config harness.toml`). This fork governed the spec-conforming closure.

---

## 1. The divergence

Runtime spec v1.39 §3.7 (line 391) declares:

> **Config file.** Path `harness.toml` at workspace root by default; overridable via `--config <path>` CLI flag.

and §14.18.1 (line 241) declares `--config <path>` as "Override **default** `harness.toml` config-file path."

Both assert that `harness.toml` is discovered automatically at the workspace root when `--config` is omitted. At filing time, **the implementation did not do this.**

**Closure:** Reading A was implemented at PR #279 (`a394032`) before this fork doc was refreshed: `RuntimeConfigSource.load(config_file=None)` now discovers `Path.cwd() / DEFAULT_CONFIG_FILE_NAME` when that file exists, and otherwise preserves env+CLI-only behavior.

## 2. Filing evidence (historical; now closed)

1. **Dead constant.** At filing time, `DEFAULT_CONFIG_FILE_NAME = "harness.toml"` was defined and exported in `__all__` at `harness-runtime/src/harness_runtime/config_source.py:43`, but a workspace-wide grep found **no use site** — only its definition + the `__all__` entry. PR #279 wired it through `_discover_default_config()`.

2. **`load(config_file=None)` skipped the file layer.** At filing time, `RuntimeConfigSource.load` documented that when `config_file` was `None`, the config-file layer contributed nothing. PR #279 changed this to CWD-local discovery while retaining the no-file fallback.

3. **Positive-control probe.** At filing time, with a complete, valid `harness.toml` present at CWD, `uv run harness run <manifest>` (no `--config`) **still** failed:

   ```
   RT-FAIL-CLI-CONFIG-LOAD: Missing required fields:
     - deployment_surface
     - repository_root
     - otel
     - default_topology
   ```

   The file present at CWD was not discovered. PR #279 added regression coverage for the positive path, no-file fallback, explicit-config precedence, and the discovery helper.

## 3. The non-obvious part — "workspace root" is undefined

The spec says discover `harness.toml` "at workspace root." But the workspace root is not known *before* config load: `RuntimeConfig.repository_root` is itself a field *inside* `harness.toml`. Discovery cannot key on `repository_root` (circular). Candidate readings:

- **(A) CWD discovery.** Look for `./harness.toml` relative to the process working directory (the dir the operator runs `harness run` from). Standard CLI-tool convention. Simple; matches "just run from your repo root."
- **(B) Upward search.** Walk up from CWD to the filesystem root looking for the first `harness.toml` (git-style). More forgiving of subdir invocation; more surprising.
- **(C) Keep explicit-only.** Treat §3.7 "by default" as aspirational; require `--config` (or the `just` recipe that supplies it) and amend the spec to drop the auto-discovery clause. This is what option (B) for R-100 effectively does at the recipe layer.

Reading (A) was the recommended default (simplest, least surprising, matches the `just run` CWD assumption). The operator ratified Reading A on 2026-06-06; implementation had already landed at PR #279.

## 4. Resolution

Reading A applies:

- `RuntimeConfigSource.load(config_file=None)` attempts CWD-local `harness.toml` discovery via `DEFAULT_CONFIG_FILE_NAME`.
- If the file is absent, the config-file layer contributes nothing, preserving env+CLI-only behavior.
- Explicit `config_file=...` continues to bypass discovery and wins over the CWD default.
- No spec amendment is owed; this is the spec-conforming closure of §3.7 + §14.18.1.

Verification on 2026-06-06: `uv run pytest harness-runtime/tests/test_config_source.py -q` → 19 passed.

## 5. Tracking

Roadmap entry `R-100-mvp-config-discovery` is RESOLVED by PR #279 + this fork-doc status refresh. The misleading "discovers this file by default" claim in `harness.toml.example` was corrected before the implementation; after PR #279 the claim is true under Reading A's CWD semantics.
