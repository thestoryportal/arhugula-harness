# Run the first workflow with local Ollama

`ollama-first.toml` sends one short prompt to the local `llama3.2:3b` model. Its matching `ollama.local.toml.example` selects Ollama alone, needs no API key, and keeps run state under this checkout's `.harness/onboarding/` directory.

> **At this release this config cannot complete a fresh run.** Every fresh `harness run` places its pause-journal root under a declared external state root (Runtime spec v1.137 Rule B3). `ollama.local.toml.example` and `ollama.handoff.local.toml.example` declare no `[runtime.state_placement]` table, so a run with either stops before its first step and reports `state-root placement refused (placement-required)`. Both files still load, and the provider-free checks still use them. To complete the first workflow, follow [Complete a first run](#complete-a-first-run-external-state-root).

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

## Complete a first run (external state root)

A fresh run needs three things that the config above does not give it: a declared state root outside every checkout, an installation-state document that names the pause-journal root, and that directory inside the state root. `omarchy.ollama.toml.example` is the same local Ollama route with the state placement declared.

1. Copy the profile and replace both placeholders: `/absolute/path/to/your/workspace` with the path printed by `pwd -P`, and `/absolute/path/to/your/state-root` with an absolute path outside every checkout. [External state root](../docs/how-to-deploy.md#external-state-root-omarchy-production-profile) lists the rules that path must meet.

   ```sh
   cp examples/omarchy.ollama.toml.example harness.toml
   ${EDITOR:-vi} harness.toml
   ```

2. Write the installation-state document under the interpreter's prefix. Set `STATE_ROOT` to the state root you chose in step 1:

   ```sh
   STATE_ROOT=/absolute/path/to/your/state-root
   PREFIX=$(uv run --no-sync python -c 'import sys; print(sys.prefix)')
   mkdir -p "$PREFIX/etc/arhugula"
   printf '{"pause_journal_root_declarations": [{"installation_root": "%s/pause-journal"}]}\n' \
     "$STATE_ROOT" > "$PREFIX/etc/arhugula/installation-state.json"
   ```

3. Run once. This run creates and stamps the state root, then stops with `pause-journal root unresolved (missing)`, because the runtime refuses a state root that already holds files it did not stamp, so you cannot create the directory first:

   ```sh
   uv run --no-sync harness run examples/ollama-first.toml --config harness.toml
   ```

4. Create the pause-journal root inside the stamped state root and run again:

   ```sh
   mkdir -m 700 "$STATE_ROOT/pause-journal"
   uv run --no-sync harness run examples/ollama-first.toml --config harness.toml
   ```

The second run prints the completed status shown above. Its state ledger is `state-ledger/state.jsonl` under the state root. If an earlier run with the checkout-local config left `.harness/onboarding/state-ledger` behind, bootstrap refuses with `legacy-state-present`; move that directory out of the checkout first.

The topology examples below name the checkout-local configs. To complete them, use the config from this section instead: add the same path-binding blocks, with each `STATE_LEDGER` path set to `state-ledger` under your state root, and set `inter_step_data_flow = true` where an example asks for the handoff config.

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

**What these topology examples do not show yet.** The orchestrator-workers and hierarchical manifests use the default declared-pool worker selection: their worker sets are the declared steps, and the lead runs and is recorded as its own step, but its output neither chooses nor reaches the workers, and the synthesis sees worker outputs only. A manifest can opt into the lead-directed plan (CP v1.130 §25.11.1) with `worker_selection = "lead-plan"` in its `[workflow]` table; the loader refuses it on any topology other than orchestrator-workers or hierarchical-delegation. Under that plan the lead's output carries a `worker_plan` list that selects, orders and briefs workers from the declared pool. These examples stay on declared-pool because their lead is an Ollama inference step, and the runtime does not yet turn a model reply into a `worker_plan`, so a lead-plan run of them would have no plan to follow. None of these examples declares an approval gate, so they do not exercise HITL placement inheritance into delegated children. Every step uses `tools = []` and the `ollama.local.toml.example` and `ollama.handoff.local.toml.example` configs they run with set `mcp_clients = []`, so no example here depends on a served MCP tool. That is a choice of these examples, not a limit of the Ollama arm: with an MCP client configured in `mcp_clients`, source offers its tools to the Ollama model and answers the model's tool calls through the runtime's HITL tool loop (Runtime v1.134 C-RT-38).

The parallelization and handoff manifests are checked provider-free (they load through the real manifest loader, their payloads validate, and a recording provider double shows the handoff stages receiving the prior stage's output under the handoff config). The evaluator-optimizer, orchestrator-workers and hierarchical-delegation manifests are checked provider-free by `harness-runtime/tests/test_omarchy_offline_examples.py`: they load through the same loader, their topology is admissible for their workload, their configs with the README bindings resolve every path class, and the delegated brief's `summary_hash` matches its canonical hash. A recording stand-in for Ollama also runs the evaluator-optimizer loop (draft to evaluator, feedback to regenerate, the cap) and the orchestrator-workers synthesis (worker outputs only) through the real driver and dispatcher. All five are **not yet witnessed** end to end: an installed-candidate run against a live local model, in a quiet Ollama window, is still open for each. Do not read a successful `completed` status here as that acceptance. The `examples/workflows/topology/*.yaml` files remain admissibility fixtures with a stand-in child, not runnable workflows.

## Offline embedding routing (Omarchy profile)

`omarchy.offline-embedding.toml.example` is the Omarchy Ollama profile with Layer-2 embedding routing turned on, reading a pinned local `BAAI/bge-small-en-v1.5` model with no network access. It needs the optional embedding extra, the model files and a `SHA256SUMS` manifest in place first; follow [Offline embedding for Omarchy](../docs/operations/omarchy-offline-embedding.md).
