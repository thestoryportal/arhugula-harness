# Run the first workflow with local Ollama

`ollama-first.toml` sends one short prompt to the local `llama3.2:3b` model. Its matching `ollama.local.toml.example` selects Ollama alone, needs no API key, and keeps run state under this checkout's `.harness/onboarding/` directory.

On Omarchy or another Arch Linux installation, have Python 3.12, `uv`, and Ollama available. From the repository root, prepare the locked Python workspace and the local model:

```sh
uv sync --frozen --all-packages
ollama pull llama3.2:3b
```

Start Ollama with `ollama serve` in another terminal if it is not already running. The example expects it at `http://127.0.0.1:11434`; `ollama list` should show `llama3.2:3b`. Model download and the first run require local Ollama; neither uses a hosted provider.

Copy the runtime config, then replace **every** `/absolute/path/to/your/workspace` with the absolute path printed by `pwd -P`:

```sh
cp examples/ollama.local.toml.example harness.toml
pwd -P
${EDITOR:-vi} harness.toml
uv run --no-sync harness run examples/ollama-first.toml --config harness.toml
```

A successful one-shot run prints a completed status, the workflow id, and an audit-ledger head hash (the hash varies):

```text
status:    completed
workflow:  example-ollama-first
ledger:    <64-character hash>
```

The CLI does not print the model's reply in text mode. The state ledger is `.harness/onboarding/state-ledger/state.jsonl`; `STATE_LEDGER` binds its parent directory. The runtime also writes its index and worktree state under `.harness/`. The config names a loopback OTLP endpoint at port 4317; without a collector, trace export can report connection errors even when the workflow completes.

`minimal.toml` remains an optional hosted Anthropic example. It selects `claude-haiku-4-5` and needs an Anthropic credential and a matching runtime provider and fallback chain. The generic `harness.toml.example` defaults to subscription CLI routing, so copying it unchanged does **not** configure the Anthropic-only route for `minimal.toml`. Keep credentials out of TOML; the local-development secret backend supports the OS keyring with environment fallback.

## Multi-step topology examples (local Ollama)

Two further manifests run real multi-step topologies against the same local `llama3.2:3b` model, with no hosted provider and an empty fallback chain. Prompts and `num_predict` are small on purpose.

- `ollama-decentralized-handoff.toml` — `pipeline-automation`, `decentralized-handoff`, three sequential stage-expert inference steps (`stage-draft`, `stage-review`, `stage-finalize`). It runs with the config from the previous section unchanged.
- `ollama-parallelization.toml` — `research`, `parallelization`, two peer inference branches (`branch-overview`, `branch-risks`). Parallelization is admissible only for research and content-creation, and `ollama.local.toml.example` binds paths for `pipeline-automation` only, so add research bindings to your `harness.toml` before running it. Insert this block above the `[runtime.routing_manifest]` table and replace the path prefix as before:

```toml
[[runtime.path_bindings.raw_entries]]
path_class = "SKILLS"
workflow_class = "research"
deployment_surface = "local-development"
path = "/absolute/path/to/your/workspace/.agents/skills"

[[runtime.path_bindings.raw_entries]]
path_class = "PROMPTS"
workflow_class = "research"
deployment_surface = "local-development"
path = "/absolute/path/to/your/workspace/.harness/onboarding/prompts"

[[runtime.path_bindings.raw_entries]]
path_class = "ROUTING_MANIFEST"
workflow_class = "research"
deployment_surface = "local-development"
path = "/absolute/path/to/your/workspace/.harness/onboarding/routing-manifest"

[[runtime.path_bindings.raw_entries]]
path_class = "STATE_LEDGER"
workflow_class = "research"
deployment_surface = "local-development"
path = "/absolute/path/to/your/workspace/.harness/onboarding/state-ledger"
```

```sh
uv run --no-sync harness run examples/ollama-decentralized-handoff.toml --config harness.toml
uv run --no-sync harness run examples/ollama-parallelization.toml --config harness.toml
```

These two manifests are checked provider-free (they load through the real manifest loader and their payloads validate), but they are **not yet witnessed** end to end: an installed-candidate run against a live local model, in a quiet Ollama window, is still open. Do not read a successful `completed` status here as that acceptance. The other topologies (evaluator-optimizer, orchestrator-workers, hierarchical delegation) have no local manifest yet, and the `examples/workflows/topology/*.yaml` files remain admissibility fixtures with a stand-in child, not runnable workflows.
