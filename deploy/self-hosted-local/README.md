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

1. Start the Docker daemon on the Omarchy/Arch host.
2. Create an operator-owned Grafana admin password file outside the checkout. The
   prompt hides the password; the commands do not print or store it in shell
   history. Keep this exported path in the shell that runs the stack commands:

   ```bash
   grafana_secret_dir="$HOME/.local/share/arhugula/secrets"
   install -d -m 0700 "$grafana_secret_dir"
   grafana_secret_file="$grafana_secret_dir/grafana-admin-password"
   umask 077
   read -r -s -p "Grafana admin password: " grafana_password
   printf '\n'
   printf '%s' "$grafana_password" > "$grafana_secret_file"
   unset grafana_password
   chmod 0644 "$grafana_secret_file"
   export R420_GRAFANA_ADMIN_PASSWORD_FILE="$grafana_secret_file"
   test -s "$R420_GRAFANA_ADMIN_PASSWORD_FILE"
   ```

   The host directory is mode `0700`, so other host users cannot traverse to
   the file. The file is mode `0644` because file-sourced Compose secrets are
   bind mounts and Compose cannot remap their ownership or mode for Grafana's
   non-root user. Only Grafana receives this read-only secret at
   `/run/secrets/grafana_admin_password`; it is not committed or copied into
   Compose environment values. See [Docker's Compose secret permissions](https://docs.docker.com/reference/compose-file/services/#secrets)
   and [Grafana's `__FILE` setting](https://grafana.com/docs/grafana/latest/setup-grafana/configure-docker/#configure-grafana-with-docker-secrets).
   Re-export the path in any later shell before `up`, `status`, or `down`.

   Before starting the stack, check the resolved Compose model. The command
   prints only a pass message; it does not print the password or the secret file
   contents:

   ```sh
   docker compose -f deploy/self-hosted-local/compose.yaml config --format json |
     python3 -c 'import json, os, sys
m = json.load(sys.stdin)
s = m["services"]
p = [entry for service in s.values() for entry in service.get("ports", [])]
assert len(p) == 4 and all(entry.get("host_ip") == "127.0.0.1" for entry in p)
g = s["grafana"]
assert g["environment"]["GF_AUTH_ANONYMOUS_ENABLED"] == "false"
assert "GF_SECURITY_ADMIN_PASSWORD" not in g["environment"]
assert g["environment"]["GF_SECURITY_ADMIN_PASSWORD__FILE"] == "/run/secrets/grafana_admin_password"
assert g["secrets"][0]["source"] == "grafana_admin_password"
assert m["secrets"]["grafana_admin_password"]["file"] == os.environ["R420_GRAFANA_ADMIN_PASSWORD_FILE"]
print("Compose OK: four loopback ports, anonymous access off, file secret mounted")'
   ```

   Compose refuses to resolve this stack when
   `R420_GRAFANA_ADMIN_PASSWORD_FILE` is unset or empty. The configuration
   check proves the planned mounts and bindings; Grafana login and secret-file
   readability still need the later live stack gate.

3. Copy `harness.selfhosted.local.example.toml` to a local, gitignored config:

   ```sh
   cp deploy/self-hosted-local/harness.selfhosted.local.example.toml harness.selfhosted.local.toml
   ```

4. Replace every `/absolute/path/to/arhugula-v2` placeholder with this
   workspace root.
5. Prepare the path-class bindings the live e2e resolves. The template binds
   four `PathClass` members per workflow class; three of them point at
   directories this repo does not ship:

   ```sh
   mkdir -p prompts routing_manifest
   ```

   - `PROMPTS` → `<root>/prompts` and `ROUTING_MANIFEST` → `<root>/routing_manifest`
     may be **empty**. Bootstrap stage 1 (`materialize_path_registry`) creates
     every resolved path with `Path.mkdir(parents=True, exist_ok=True)`, so
     pre-creating them is optional — but if you skip it, the run leaves
     `prompts/` untracked at the workspace root (`routing_manifest/` is already
     gitignored). Routing data itself is read
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

6. Put the R-420 sentinel value in the OS keyring under service `harness`.
   The included no-paid template expects keyring item name `r420_probe_key`:

   ```sh
   uv run python -c 'import keyring; keyring.set_password("harness", "r420_probe_key", "r420-local-sentinel")'
   ```
7. Start the local backend:

   ```sh
   just r420-self-hosted-stack-up
   ```

8. Run the non-mutating static gate:

   ```sh
   just r420-self-hosted-readiness harness.selfhosted.local.toml
   ```

9. Start the harness daemon against the self-hosted config:

   ```sh
   uv run harness daemon --config harness.selfhosted.local.toml
   ```

10. Or run the full local live e2e in one command:

   ```sh
   just r420-self-hosted-live-e2e harness.selfhosted.local.toml
   ```

   This step needs a tier-3 execution driver — see
   [Tier-3 sandbox driver](#tier-3-sandbox-driver-required-for-the-r-420-live-e2e)
   below. Without one it aborts at dispatch with
   `SandboxDriverUnavailableError: resolved tier 'tier-3-microvm'`.

11. Run the R-430 tail-keep collector proof against the same local stack:

   ```sh
   just r430-tail-keep-live-e2e harness.selfhosted.local.toml
   ```

   The command emits one `sandbox.violation` trace and one non-triggering
   trace through the real OTLP collector. Passing output ends with
   `trigger-trace-preserved=true` and `non-trigger-trace-exported=false`.

12. Run the R-500 multi-tenant self-hosted proof against the same local stack:

   ```sh
   just r500-multitenant-live-e2e harness.selfhosted.local.toml
   ```

   The command overlays two non-default `tenant_id` values and
   `multi-tenant-compliance` onto the config, emits `audit.*` traces through
   the real OTLP collector, and exercises a temporary tenant-scoped audit
   ledger. Passing output ends with `tenant-resource-separated=true`,
   `content-redacted=true`, and `audit-ledger-separated=true`.

13. Open Grafana at `http://127.0.0.1:3000`. The `grafana-data` volume may
    already hold admin credentials from an earlier initialization. Grafana's
    configured admin password is [set only on first run](https://grafana.com/docs/grafana/latest/setup-grafana/configure-grafana/#admin_password),
    so changing this file does not rotate an existing volume's password. Verify
    login and use Grafana's password-reset procedure for an existing instance;
    do not remove its volume as a password reset.
Stop the backend with:

```sh
just r420-self-hosted-stack-down
```

## Tier-3 sandbox driver (required for the R-420 live e2e)

The `r420-echo` MCP client in the template declares
`default_minimum_tier = "tier-1-process"`, but that is a floor *request*, not the
resolved tier. **C-AS-02 §2.3 row 3 floors any stdio MCP transport at
`TIER_3_MICROVM`** (`harness-as/src/harness_as/sandbox_tier_floor.py` — the
`MCPTransport.STDIO` branch returns `_tier_max(SandboxTier.TIER_3_MICROVM,
floor)`), so `r420-echo` always resolves to tier-3 and the live e2e needs a
tier-3 execution driver. Without one, step 9 aborts at dispatch:

```text
SandboxDriverUnavailableError: resolved tier 'tier-3-microvm'
```

This is the enforced contract behaving correctly, not a config bug. Close it with
config only — no harness code change:

1. Provision a Linux daemon with the gVisor runtime registered **under the exact
   name `runsc`**. This is not generic tier-3 compatibility: the tier-3 branch of
   `runtime_tool_dispatcher_factory.py` always constructs
   `GVisorRunscToolRunnerExecutionDriver`, whose `runtime` field defaults to
   `"runsc"` and is emitted verbatim as `--runtime runsc` in the `docker run`
   argv (`harness-runtime/src/harness_runtime/lifecycle/
   docker_tool_execution_driver.py`). A daemon offering some other tier-3 runtime
   — or gVisor registered under a different name — fails at container start.
   gVisor is Linux-only and never runs on the macOS host directly, so macOS
   operators need a VM. Lima is one option — the same `r411-gvisor` VM the R-411
   gVisor smoke uses (`.harness/release-candidate-deployment-readiness-runbook.md`
   §4 and its `R411_GVISOR_DOCKER_COMMAND` recipe). Verify with
   `docker info` on the daemon: `runsc` must appear under `Runtimes`.
2. Write a one-line wrapper script. `SandboxDriverConfig.docker_binary` is
   exec'd as `argv[0]` with **no shell**, so a multi-word remote invocation must
   live in a single executable file:

   ```sh
   #!/bin/sh
   exec env LIMA_HOME=/path/to/lima-home limactl shell <vm> sudo docker "$@"
   ```

   Keep it outside version control (for example under the gitignored
   `.harness/r420-scratch/`) and `chmod +x` it.
3. Uncomment the `[runtime.mcp_clients.sandbox_driver]` block in
   `harness.selfhosted.local.example.toml` (copied into your local config) and
   point `docker_binary` at that script's absolute path. Pre-pull the `image`
   inside the VM. Keep `network = "none"`. The `command` reads the MCP request
   JSON on stdin and must echo the real `tool_args.value` back — a constant
   response makes the e2e pass without proving transit.
4. **Leave `default_sandbox_tech` and `default_sandbox_provider` unset** (the
   template ships them commented out). They are the `sandbox.enter` span labels,
   and an explicit operator value **survives the row-3 raise** — the resolver
   re-derives them from the raised tier only when they are `None`
   (`harness-runtime/src/harness_runtime/config/sandbox_defaults.py`). Pinning
   them to the tier-1 pair `"host-process"` / `"host"` therefore makes every span
   claim host execution for a tool that actually ran under gVisor `runsc`:
   security telemetry that lies about the isolation applied. Unset, they derive
   to `gvisor` / `runsc` alongside the delivered tier.

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
