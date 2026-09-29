# Tutorial: First workflow on Omarchy or Arch Linux

Run `examples/ollama-first.toml` against a local Ollama server. This one-shot workflow uses `llama3.2:3b` and requires no hosted API key.

## 1. Prepare the local tools

Install Python 3.12, `uv`, and Ollama, then run these commands from the repository root:

```sh
uv sync --frozen --all-packages
ollama pull llama3.2:3b
```

Keep Ollama running at `http://127.0.0.1:11434`. If it is not already running, start `ollama serve` in a separate terminal. Check that `ollama list` includes `llama3.2:3b`.

## 2. Copy and edit the runtime config

```sh
cp examples/ollama.local.toml.example harness.toml
pwd -P
${EDITOR:-vi} harness.toml
```

Replace every `/absolute/path/to/your/workspace` with the absolute checkout path from `pwd -P`. The config enables only Ollama, points to its loopback host, and binds the four required path classes for `pipeline-automation`. Stage 1 creates the `.harness/onboarding/` directories when the workflow starts. `STATE_LEDGER` must remain a directory path: the runtime creates `state.jsonl` inside it.

This tutorial config keeps state under the checkout's `.harness/onboarding/`, so it is non-durable and not restore-safe. For state outside the checkout, see [External state root](how-to-deploy.md#external-state-root-omarchy-production-profile).

## 3. Run the workflow

```sh
uv run --no-sync harness run examples/ollama-first.toml --config harness.toml
```

On success the command exits `0` and prints:

```text
status:    completed
workflow:  example-ollama-first
ledger:    <64-character hash>
```

On a successful run, the default text mode prints `status:`, `workflow:`, and `ledger:` — not the model's reply. If the run fails instead, it additionally writes `failure:` and `detail:` to stderr, interpolating the run's failure class and detail message. Inspect the state ledger with:

```sh
uv run --no-sync harness-inspect --ledger-path .harness/onboarding/state-ledger/state.jsonl
```

The `--ledger-path` flag is required here: `harness-inspect`'s own default (`.harness/state.jsonl`) does not match this profile's configured `STATE_LEDGER` location, so running the bare command with no flag reports the file missing even after a successful run.

An unreachable Ollama server is a bootstrap failure because this profile sets `ollama_optional = false`. A local trace-export warning can appear if no collector is listening on the configured loopback OTLP port 4317.

The older `examples/minimal.toml` is an optional hosted Anthropic workflow. It requires a provider credential and a runtime config whose enabled provider and fallback chain select Anthropic. The generic `harness.toml.example` instead defaults to subscription CLI routing; its defaults are not the config for this local Ollama tutorial.

## Source Grounding

- **Ollama host and port.** [`examples/ollama.local.toml.example`](../examples/ollama.local.toml.example#L11) sets `ollama_host = "http://127.0.0.1:11434"`, matching step 1's `ollama serve` default.
- **The four path classes.** [`examples/ollama.local.toml.example`](../examples/ollama.local.toml.example#L24-L46) binds `SKILLS`, `PROMPTS`, `ROUTING_MANIFEST`, and `STATE_LEDGER` — the same four names the runtime's path registry looks up, listed in [`stage_1_is.py`](../harness-runtime/src/harness_runtime/bootstrap/stage_1_is.py#L13-L15).
- **Stage 1 creates the onboarding directories.** [`stage_1_is.py`](../harness-runtime/src/harness_runtime/bootstrap/stage_1_is.py#L7-L11) runs the path registry before anything else, and the [registry call](../harness-runtime/src/harness_runtime/bootstrap/stage_1_is.py#L89-L93) creates every one of those directories on disk.
- **`STATE_LEDGER` is a directory; `state.jsonl` is the file inside it.** The runtime opens the ledger by calling [`initialize_jsonl_event_ledger`](../harness-runtime/src/harness_runtime/lifecycle/state_ledger.py#L131), whose own body [resolves the `STATE_LEDGER` directory and appends `state.jsonl` to it](../harness-is/src/harness_is/jsonl_event_ledger_lifecycle.py#L76-L78). For this tutorial's config, that is `.harness/onboarding/state-ledger/state.jsonl` — the path the `harness-inspect` command above uses.
- **The CLI's text output.** [`app.py`'s `_emit_run_result`](../harness-runtime/src/harness_runtime/cli/app.py#L133-L144) prints `status:`, `workflow:`, and `ledger:` on success — not the model's reply. On failure it also writes `failure:` and `detail:` to stderr, interpolating `result.failure_cause`'s class and detail message.
- **An unreachable Ollama server fails the run.** [The Ollama provider setup](../harness-runtime/src/harness_runtime/lifecycle/providers.py#L776-L789) only tolerates a connection failure when `ollama_optional` is `true`; this tutorial's config sets it `false`.
- **`examples/minimal.toml` needs Anthropic.** Its [`[default_model_binding]`](../examples/minimal.toml#L33-L35) and [`fallback_chain.primary`](../examples/minimal.toml#L31) both name the `anthropic` provider.
- **`harness.toml.example` defaults to subscription CLI routing.** Its [`[[runtime.external_cli_providers]]` tables](../harness.toml.example#L94-L116) are on by default, per [the file's own comment](../harness.toml.example#L81).
