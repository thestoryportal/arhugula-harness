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
"self-hosted-keyring"`.

## Runbook

1. Start Docker Desktop.
2. Copy `harness.selfhosted.local.example.toml` to a local, gitignored config:

   ```sh
   cp deploy/self-hosted-local/harness.selfhosted.local.example.toml harness.selfhosted.local.toml
   ```

3. Replace every `/absolute/path/to/arhugula-v2` placeholder with this
   workspace root.
4. Put the needed provider secret values in the OS keyring under service
   `harness`. For the included Anthropic-only template, the keyring item name
   is `anthropic_key`.
5. Start the local backend:

   ```sh
   just r420-self-hosted-stack-up
   ```

6. Run the non-mutating static gate:

   ```sh
   just r420-self-hosted-readiness harness.selfhosted.local.toml
   ```

7. Start the harness daemon against the self-hosted config:

   ```sh
   uv run harness daemon --config harness.selfhosted.local.toml
   ```

8. Open Grafana at `http://127.0.0.1:3000`.

Stop the backend with:

```sh
just r420-self-hosted-stack-down
```

## Boundaries

The static readiness command does not start the daemon, probe OTLP, fetch
secrets, call a provider, or spend provider credits. The first paid operation is
the later daemon e2e if it runs an inference workflow against a real provider.

This local stack is sufficient to prepare and exercise R-420 on a single
operator machine. It is not the R-421 managed-cloud substrate.
