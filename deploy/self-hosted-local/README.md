# R-420 local self-hosted stack

This directory is the local, operator-owned SELF_HOSTED_SERVER bootstrap for
R-420. It runs the telemetry backend in Docker Compose while the harness daemon
continues to run as a host process.

The stack contains:

- OpenTelemetry Collector Contrib, listening on OTLP gRPC `127.0.0.1:4317`
  and OTLP HTTP `127.0.0.1:4318`
- Grafana Tempo, receiving traces from the collector over Docker networking
- Grafana, pre-provisioned with a Tempo data source at `http://tempo:3200`

No provider credentials are stored in this directory. Provider secrets remain
in the OS keyring through `[runtime.provider_secrets] backend =
"self-hosted-keyring"`. The default live e2e uses local Ollama and a
non-secret sentinel keyring entry, so it makes no hosted-provider call.

## Runbook

1. Start Docker Desktop.
2. Copy `harness.selfhosted.local.example.toml` to a local, gitignored config:

   ```sh
   cp deploy/self-hosted-local/harness.selfhosted.local.example.toml harness.selfhosted.local.toml
   ```

3. Replace every `/absolute/path/to/arhugula-v2` placeholder with this
   workspace root.
4. Prepare the path-class bindings the live e2e resolves. The template binds
   four `PathClass` members per workflow class; three of them point at
   directories this repo does not ship:

   ```sh
   mkdir -p prompts routing_manifest
   ```

   - `PROMPTS` → `<root>/prompts` and `ROUTING_MANIFEST` → `<root>/routing_manifest`
     may be **empty**. Bootstrap stage 1 (`materialize_path_registry`) creates
     every resolved path with `Path.mkdir(parents=True, exist_ok=True)`, so
     pre-creating them is optional — but if you skip it, the run leaves two new
     untracked directories at the workspace root. Routing data itself is read
     from the `[runtime.routing_manifest]` table in the config, not from files
     in that directory.
   - `STATE_LEDGER` → the template already binds a **throwaway scratch
     directory**:

     ```toml
     path = "/absolute/path/to/arhugula-v2/.harness/r420-scratch"
     ```

     `STATE_LEDGER` resolves to a **directory**, not a file (IS spec v1.3 §1
     amendment). `initialize_jsonl_event_ledger` creates that directory and
     opens the ledger at `<dir>/state.jsonl`, so a binding that itself ends in
     `state.jsonl` produces `r420-scratch/state.jsonl/state.jsonl`.

     Do **not** repoint this at `<root>/.harness/state.jsonl`, this repo's real
     hash-chained ledger **file**. That binding does not merely pollute the live
     ledger — it aborts the run before it starts: bootstrap stage 1
     `materialize_path_registry` calls `Path.mkdir(parents=True, exist_ok=True)`
     on every resolved path, and `mkdir` raises `FileExistsError` on an existing
     non-directory, ahead of any chain verification. The shipped scratch
     directory gives the smoke run an empty ledger and a clean genesis chain.
     The directory is gitignored (`.harness/r420-scratch/`), so a stray `git add`
     cannot commit the run's state; delete it when the run is done.

5. Put the R-420 sentinel value in the OS keyring under service `harness`.
   The included no-paid template expects keyring item name `r420_probe_key`:

   ```sh
   uv run python -c 'import keyring; keyring.set_password("harness", "r420_probe_key", "r420-local-sentinel")'
   ```
6. Start the local backend:

   ```sh
   just r420-self-hosted-stack-up
   ```

7. Run the non-mutating static gate:

   ```sh
   just r420-self-hosted-readiness harness.selfhosted.local.toml
   ```

8. Start the harness daemon against the self-hosted config:

   ```sh
   uv run harness daemon --config harness.selfhosted.local.toml
   ```

9. Or run the full local live e2e in one command:

   ```sh
   just r420-self-hosted-live-e2e harness.selfhosted.local.toml
   ```

10. Run the R-430 tail-keep collector proof against the same local stack:

   ```sh
   just r430-tail-keep-live-e2e harness.selfhosted.local.toml
   ```

   The command emits one `sandbox.violation` trace and one non-triggering
   trace through the real OTLP collector. Passing output ends with
   `trigger-trace-preserved=true` and `non-trigger-trace-exported=false`.

11. Run the R-500 multi-tenant self-hosted proof against the same local stack:

   ```sh
   just r500-multitenant-live-e2e harness.selfhosted.local.toml
   ```

   The command overlays two non-default `tenant_id` values and
   `multi-tenant-compliance` onto the config, emits `audit.*` traces through
   the real OTLP collector, and exercises a temporary tenant-scoped audit
   ledger. Passing output ends with `tenant-resource-separated=true`,
   `content-redacted=true`, and `audit-ledger-separated=true`.

12. Open Grafana at `http://127.0.0.1:3000`.

Stop the backend with:

```sh
just r420-self-hosted-stack-down
```

## Boundaries

The static readiness command does not start the daemon, probe OTLP, fetch
secrets, call a provider, or spend provider credits. The live e2e command does
start the daemon, probe the local OTLP endpoint, resolve the keyring sentinel,
and dispatch a tool workflow through the daemon. It does not run hosted-provider
inference.

This local stack is sufficient to close R-420 on a single operator machine
when `just r420-self-hosted-live-e2e harness.selfhosted.local.toml` passes. It
also provides the local real-collector substrate for R-430 when
`just r430-tail-keep-live-e2e harness.selfhosted.local.toml` passes, and for
R-500 when `just r500-multitenant-live-e2e harness.selfhosted.local.toml`
passes. It is not the R-421 managed-cloud substrate.
