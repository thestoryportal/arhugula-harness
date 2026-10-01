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

> **Not durable.** This onboarding config keeps run state under the checkout's `.harness/` directory, so it is non-durable and not restore-safe. For state outside the checkout, use an `omarchy.*.toml.example` profile and follow [External state root](../docs/how-to-deploy.md#external-state-root-omarchy-production-profile). The Codex profile is HELD.

A successful one-shot run prints a completed status, the workflow id, and an audit-ledger head hash (the hash varies):

```text
status:    completed
workflow:  example-ollama-first
ledger:    <64-character hash>
```

The CLI does not print the model's reply in text mode. The state ledger is `.harness/onboarding/state-ledger/state.jsonl`; `STATE_LEDGER` binds its parent directory. The runtime also writes its index and worktree state under `.harness/`. The config names a loopback OTLP endpoint at port 4317; without a collector, trace export can report connection errors even when the workflow completes.

`minimal.toml` remains an optional hosted Anthropic example. **It is not a supported surface of the first self-hosted Omarchy release**, which runs local Ollama with no paid hosted provider or API key. It selects `claude-haiku-4-5` and needs an Anthropic credential and a matching runtime provider and fallback chain. The generic `harness.toml.example` defaults to subscription CLI routing, so copying it unchanged does **not** configure the Anthropic-only route for `minimal.toml`. Keep credentials out of TOML; the local-development secret backend supports the OS keyring with environment fallback.

## Multi-step topology examples (local Ollama)

Five further manifests run real multi-step topologies against the same local `llama3.2:3b` model, with no hosted provider and an empty fallback chain. Prompts and `num_predict` are small on purpose.

- `ollama-decentralized-handoff.toml` — `pipeline-automation`, `decentralized-handoff`, three sequential stage-expert inference steps (`stage-draft`, `stage-review`, `stage-finalize`). Stages 2 and 3 act on the previous stage's output, which the runtime only delivers when `inter_step_data_flow` is on. The shared config leaves it off, so this example has its own config, `ollama.handoff.local.toml.example`: the shared config plus that one flag. Prepare and run it like this:

```sh
cp examples/ollama.handoff.local.toml.example harness.handoff.toml
${EDITOR:-vi} harness.handoff.toml   # replace every /absolute/path/to/your/workspace
uv run --no-sync harness run examples/ollama-decentralized-handoff.toml --config harness.handoff.toml
```

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
uv run --no-sync harness run examples/ollama-parallelization.toml --config harness.toml
```

- `ollama-orchestrator-workers.toml` — `research`, `orchestrator-workers`. The lead step (`lead-plan`) runs first; two workers (`worker-benefits`, `worker-costs`) then run concurrently; a terminal `post-join-synthesis` step (`synthesize-brief`) receives the worker outputs after the barrier and writes the final brief. It uses the same `harness.toml` with research bindings as the parallelization example:

```sh
uv run --no-sync harness run examples/ollama-orchestrator-workers.toml --config harness.toml
```

- `ollama-hierarchical-delegation.toml` — `research`, `hierarchical-delegation`. The root lead has two children: a direct worker and a `sub-agent-dispatch` step whose child workflow is itself hierarchical (a lead and two workers). A post-join synthesis step composes the root children's outputs. A parent may have at most three direct children; the driver refuses a fourth instead of dropping it. If you edit the brief, recompute its `summary_hash`, as the comment in the manifest explains. Same config:

```sh
uv run --no-sync harness run examples/ollama-hierarchical-delegation.toml --config harness.toml
```

- `ollama-evaluator-optimizer.toml` — `content-creation`, `evaluator-optimizer`. A generator step writes a tagline; an evaluator step judges it and replies with one JSON object, `{"accepted": true|false, "feedback": "..."}`. The driver repeats generate and evaluate until the evaluator accepts or three iterations have run. Reaching that cap still ends the run `completed`, with `accepted` false in its final state, and text-mode output does not show the verdict, so `completed` does not mean the tagline was accepted. A reply that is not exactly that object (an extra key, a quoted boolean, a reply cut off by `num_predict`) fails the run. The evaluator asks Ollama for that shape through structured outputs (`format`), which needs an Ollama release with JSON-schema `format` support. The evaluator only sees the draft, and the regenerate step only sees the feedback, when `inter_step_data_flow` is on. Use `harness.handoff.toml` and add content-creation bindings to it, above its `[runtime.routing_manifest]` table:

```toml
[[runtime.path_bindings.raw_entries]]
path_class = "SKILLS"
workflow_class = "content-creation"
deployment_surface = "local-development"
path = "/absolute/path/to/your/workspace/.agents/skills"

[[runtime.path_bindings.raw_entries]]
path_class = "PROMPTS"
workflow_class = "content-creation"
deployment_surface = "local-development"
path = "/absolute/path/to/your/workspace/.harness/onboarding/prompts"

[[runtime.path_bindings.raw_entries]]
path_class = "ROUTING_MANIFEST"
workflow_class = "content-creation"
deployment_surface = "local-development"
path = "/absolute/path/to/your/workspace/.harness/onboarding/routing-manifest"

[[runtime.path_bindings.raw_entries]]
path_class = "STATE_LEDGER"
workflow_class = "content-creation"
deployment_surface = "local-development"
path = "/absolute/path/to/your/workspace/.harness/onboarding/state-ledger"
```

```sh
uv run --no-sync harness run examples/ollama-evaluator-optimizer.toml --config harness.handoff.toml
```

**What these topology examples do not show yet.** In current source the orchestrator-workers and hierarchical worker sets are the declared steps; the lead runs and is recorded as its own step, but its output neither chooses nor reaches the workers, and the synthesis sees worker outputs only. None of these examples declares an approval gate, so they do not exercise HITL placement inheritance into delegated children. Every step uses `tools = []`: the Ollama arm does not yet run an MCP tool loop, so no example here depends on a served MCP tool.

The parallelization and handoff manifests are checked provider-free (they load through the real manifest loader, their payloads validate, and a recording provider double shows the handoff stages receiving the prior stage's output under the handoff config). The evaluator-optimizer, orchestrator-workers and hierarchical-delegation manifests are checked provider-free by `harness-runtime/tests/test_omarchy_offline_examples.py`: they load through the same loader, their topology is admissible for their workload, their configs with the README bindings resolve every path class, and the delegated brief's `summary_hash` matches its canonical hash. A recording stand-in for Ollama also runs the evaluator-optimizer loop (draft to evaluator, feedback to regenerate, the cap) and the orchestrator-workers synthesis (worker outputs only) through the real driver and dispatcher. All five are **not yet witnessed** end to end: an installed-candidate run against a live local model, in a quiet Ollama window, is still open for each. Do not read a successful `completed` status here as that acceptance. The `examples/workflows/topology/*.yaml` files remain admissibility fixtures with a stand-in child, not runnable workflows.
