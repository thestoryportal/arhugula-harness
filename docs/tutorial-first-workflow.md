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

The CLI's text output reports run status and the audit-ledger head hash; it does not display the model's reply. Inspect `.harness/onboarding/state-ledger/state.jsonl` for the state ledger. An unreachable Ollama server is a bootstrap failure because this profile sets `ollama_optional = false`. A local trace-export warning can appear if no collector is listening on the configured loopback OTLP port 4317.

The older `examples/minimal.toml` is an optional hosted Anthropic workflow. It requires a provider credential and a runtime config whose enabled provider and fallback chain select Anthropic. The generic `harness.toml.example` instead defaults to subscription CLI routing; its defaults are not the config for this local Ollama tutorial.
