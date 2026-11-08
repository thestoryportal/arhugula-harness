# How To Operate The Runtime

Use this page for routine CLI and daemon operation. It avoids live-provider
setup details except where a workflow dispatch actually requires provider
credentials.

## Run One Workflow

Use one-shot mode when you want the CLI process to load config, load one
workflow manifest, dispatch it, print the result, and exit:

```sh
uv run harness run examples/minimal.toml --config harness.toml
```

Useful flags:

| Flag | Purpose |
| --- | --- |
| `--config <path>` | Use a specific TOML runtime config instead of CWD discovery. |
| `--output text|json` | Select text or JSON result output. |
| `--provider <name>` | Override the workflow default provider for this invocation. |
| `--model <name>` | Override the workflow default model for this invocation. |
| `--tenant-id <id>` | Override `RuntimeConfig.tenant_id`. |
| `--daemon` | Dispatch through a running daemon instead of one-shot bootstrap. |
| `--socket-path <path>` | Select the daemon Unix socket for daemon-client mode. |
| `--daemon-result-timeout-seconds <seconds>` | Set a finite positive wait for a daemon workflow result (default: 3600 seconds; requires `--daemon`). |

## Resume A Paused Workflow

`harness resume` continues the latest durable workflow-layer pause of a
workflow. Pass the same manifest the paused run used; its `workflow_id` is the
resume handle:

```sh
uv run harness resume examples/minimal.toml --config harness.toml
```

The command accepts only `--config`, `--tenant-id` and `--output`, which mean
what they mean for `run`. It has no `--provider`, `--model` or `--daemon`, and
it takes no snapshot or resume context. Resume runs in one-shot mode and keeps
the paused run's `run_id`.

Only the latest pause journal record for the `workflow_id` can be resumed.
That record is either a workflow-layer pause or an engine-native pause of a
WAL-segment or reconciler-loop workflow; both resume the same way and keep
the original `run_id`. An engine-native resume continues at the paused step
and never re-runs the steps that completed before the pause. If the engine's
own pause record is gone, the resume is refused as
`engine-pause-record-absent`; if the manifest now declares a different engine
class, it is refused as `engine-class-mismatch`. An engine-native pause
captured by a runtime older than this one has no journal record of its own;
when the workflow has no other record, its resume is refused as `handle` with
cause `absent`. If any run of the same workflow
started after the pause, the resume is refused as `pause-record-superseded`,
so do not `harness run` a paused workflow you mean to resume.

A resume that the runtime refuses before the workflow starts exits 6, or 7
when the refusal is a claim refusal. With `--output json`, stdout carries one
JSON refusal value under the protocol `harness.resume-refusal.v1`: its `kind`,
its `RT-FAIL-RESUME-*` `fail_class` and the typed facts for that kind. Text
mode prints the same fields to stderr after `resume refused:`. Neither form
includes raw error text, paths, tenant identifiers or claim tokens. Read the
`kind` to learn why a resume was refused; the exit code alone does not say.

A config that loads but does not bind the pause protocol is refused with kind
`protocol-not-bound` and exit 6. A config file that fails to load still exits 3.

## Declare The Pause-Journal Root

Durable pause and resume need one pause-journal root per installation. You
declare it in one file, at a fixed place under the environment of the
interpreter that runs the harness:

```text
<sys.prefix>/etc/arhugula/installation-state.json
```

For a project checkout, `sys.prefix` is the `.venv` directory. Print it with:

```sh
uv run python -c 'import sys; print(sys.prefix)'
```

The file holds exactly one declaration naming an existing directory by an
absolute path written without `.`, `..` or a trailing slash:

```json
{"pause_journal_root_declarations": [{"installation_root": "/srv/arhugula/pause-journal"}]}
```

You create and edit this file; the runtime never writes it. No flag,
environment variable, working directory or config setting selects another file
or another root. `harness run`, `harness resume` and `harness inspect` read it
afresh on every invocation. The daemon reads it once at startup, so restart the
daemon after you change it.

Without the file, the root is unbound. The runtime never falls back to a
default root: invalid JSON, a missing or non-list
`pause_journal_root_declarations`, zero or several declarations, a relative or
non-normalized path, a path that is not a directory, or a directory that
overlaps one of the config's path bindings all leave the root unresolved. Then
a run whose config enables durable pause-resume fails at bootstrap, and
`harness resume` is refused with kind `protocol-not-bound`.

## Run The Daemon

Start the FastMCP-backed daemon over a Unix socket:

```sh
uv run harness daemon --config harness.toml
```

The `just daemon` recipe runs the same command with `--config harness.toml`.
Daemon mode loads runtime config once, binds the runtime server, and serves
until interrupted or shut down.

Dispatch to a running daemon:

```sh
uv run harness run examples/minimal.toml --daemon
```

The `just run-daemon examples/minimal.toml` recipe uses this client path.
For a run expected to take more than one hour, set
`--daemon-result-timeout-seconds` above its expected duration. The limit covers
the client's wait for the MCP result. If it expires, the client exits with
`RT-FAIL-CLI-DAEMON-RESULT` and code 4, without a workflow result. Expiry does
not prove that the daemon cancelled the run. Session teardown, including the
daemon's DELETE response, has a separate 30-second maximum. If teardown
expires, the client reports the same result fail class and exit code without
printing the workflow result. The client does not retry either failure.

## Inspect And Shut Down

The parent CLI exposes pass-through admin commands:

```sh
uv run harness inspect --help
uv run harness shutdown --help
```

The package also preserves standalone admin scripts:

```sh
uv run harness-inspect --help
uv run harness-shutdown --help
```

Use `inspect` for read-only state and trace summaries. Use `shutdown` to signal
a running harness process to drain and exit through the admin shutdown path.

## Exit Codes

| Code | Meaning |
| ---: | --- |
| `0` | Successful CLI command or completed workflow. |
| `1` | Workflow-level failure or unknown daemon workflow status. |
| `2` | CLI option usage, workflow manifest load, or admissibility error. |
| `3` | Runtime config load error. |
| `4` | Bootstrap, daemon connection/startup, or daemon MCP result error. |
| `5` | Workflow paused: the one-shot run result or daemon workflow status is `paused`. Continue it with `harness resume`, whether it paused at the workflow layer or inside a WAL-segment or reconciler-loop engine. Running the workflow again with `harness run` starts a new run instead of resuming. A pause captured before the runtime bound its pause-journal root, or an engine-native pause captured before the runtime journaled engine pauses, cannot be resumed; its files stay on disk as operator-owned data. |
| `6` | Resume refused before the workflow started (`RESUME_REFUSED`): the refusal `kind` is `arguments`, `handle`, `depth`, `protocol-not-bound`, `pause-state-stale`, `workflow-mismatch`, `step-index-out-of-range`, `pause-record-superseded`, `engine-pause-record-absent` or `engine-class-mismatch`. |
| `7` | Resume claim refused (`RESUME_CLAIM_REFUSED`): refusal kind `claim`, with its `reason`. |

## Config Practices

- Keep `harness.toml` local and gitignored.
- Keep secrets out of TOML. Provider secret selectors belong in
  `[runtime.provider_secrets]`; actual secret values come from the configured
  backend.
- Use `harness.toml.example` as the full operator template for required fields,
  path bindings, OTel endpoint, routing manifest, and provider optionality.

## Source Grounding

This page is grounded in `harness-runtime/src/harness_runtime/cli/app.py`,
`harness-runtime/src/harness_runtime/resume_refusal.py`, `harness-runtime/pyproject.toml`,
`harness-runtime/src/harness_runtime/admin/inspect.py`,
`harness-runtime/src/harness_runtime/admin/shutdown_cli.py`,
`harness-runtime/src/harness_runtime/lifecycle/installation_state.py`,
`harness-runtime/src/harness_runtime/lifecycle/pause_journal_root_resolver.py`,
`harness-runtime/src/harness_runtime/lifecycle/journal_workflow_pause_store.py`,
`harness-runtime/src/harness_runtime/lifecycle/engine_recovery_loop.py`,
`harness-is/src/harness_is/pause_journal_root.py`,
`harness-runtime/src/harness_runtime/config_source.py`, `harness.toml.example`,
and `justfile`.
