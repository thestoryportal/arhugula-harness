# How To Deploy

The repository currently exposes provider-free readiness checks and explicit
live/provisioned runbooks. Use the static gates first; run live commands only
after the required local services, cloud resources, and operator approvals are
in place.

## Build And Validate Runtime Packages

Run the Q4 packaging gate:

```sh
just q4-packaging-check
```

The gate builds all workspace wheels, exports a hashed third-party
`requirements.lock.txt` from `uv.lock`, verifies runtime CLI entry points, checks
the runtime Dockerfile targets, and confirms one-command readiness recipes are
present.

## Build Runtime Images

After producing the dist directory described by the Q4 gate, build image
targets from `deploy/images/harness-runtime.Dockerfile`:

```sh
docker build -f deploy/images/harness-runtime.Dockerfile --target self-hosted-daemon -t arhugula/harness:self-hosted dist
docker build -f deploy/images/harness-runtime.Dockerfile --target managed-cloud-daemon -t arhugula/harness:managed-cloud dist
docker build -f deploy/images/harness-runtime.Dockerfile --target sandbox-runner -t arhugula/harness:sandbox-runner dist
```

The image recipe installs third-party packages from the hashed requirements
export and then installs workspace wheels from the wheelhouse without resolving
new dependencies.

## Self-Hosted Local Readiness

The local self-hosted stack in `deploy/self-hosted-local/` provides OTel
Collector, Tempo, and Grafana while the harness daemon runs as a host process.

Static readiness:

```sh
just r420-self-hosted-readiness harness.selfhosted.local.toml
```

Local stack lifecycle:

```sh
just r420-self-hosted-stack-up
just r420-self-hosted-stack-down
```

Live self-hosted e2e commands in that runbook require Docker and local service
setup. They do not make hosted-provider inference calls when using the documented
local Ollama/sentinel path, but they do start local services and dispatch through
the daemon.

## Managed-Cloud Readiness

The managed-cloud runbook in `deploy/managed-cloud/` validates the non-mutating
shape before any hosted sandbox or cloud trace proof:

```sh
just r421-managed-cloud-readiness harness.managed-cloud.toml --hosted-sandbox-provider e2b
```

Resolve-only E2B secret validation fetches from GCP Secret Manager but does not
create a hosted sandbox:

```sh
uv run python tools/r421_e2b_live_probe.py --config harness.managed-cloud.toml --resolve-only
```

The full managed-cloud live e2e creates a hosted E2B sandbox, emits OTLP to the
managed collector, and polls Cloud Trace. Treat that command as usage-billed and
operator-approved only.

## External state root (Omarchy production profile)

Three additive, complete profiles declare a state placement for Omarchy (Arch Linux
ARM) with local Ollama or a subscription CLI. Paid hosted providers are excluded.

| Profile | Route | Status |
| --- | --- | --- |
| `examples/omarchy.ollama.toml.example` | local Ollama | source-checked only |
| `examples/omarchy.claude-code.toml.example` | Claude Code subscription CLI | source-checked only |
| `examples/omarchy.codex.toml.example` | Codex subscription CLI | **HELD**: the CLI's filesystem read exposure is a separate boundary that is not enforced or tested. A loadable config is not launch acceptance. |

Each profile has two literal placeholders you must edit: `/absolute/path/to/your/workspace`
(this checkout) and `/absolute/path/to/your/state-root` (used in `[runtime.state_placement]`
and again as the parent of the `STATE_LEDGER` cell). No `~` or environment variable is
expanded. An unedited placeholder is refused at bootstrap (`parent-missing`).

Setup, in order:

1. Stop every harness service and worker.
2. Choose a durable root outside every checkout, every linked worktree and every
   restore, snapshot or clean scope, on a real filesystem (`tmpfs` and `ramfs` are
   refused). The root must be absent (bootstrap creates it 0700 and stamps a marker) or
   an empty 0700 directory you own. Its parent must already exist, be owned by you or
   root, and not be writable by group or others.
3. List every restore, snapshot, backup or dotfile-restore target you know of in
   `forbidden_roots`. The verifier discovers Git checkouts itself, but an empty list is
   not evidence that no other restore scope exists.
4. Inspect legacy checkout state. If a previous run left non-empty `.harness/effect-fence`,
   `.harness/engine-recovery-*`, `.harness/protected-results`, `.harness/memories*`,
   `.harness/memory` or `.harness/onboarding/state-ledger`, bootstrap refuses with
   `legacy-state-present`. Archive or migrate it yourself first; the harness never copies
   or deletes it. A custom older ledger binding is not detected; inventory it yourself.
5. Edit both placeholders, then run. The first run creates and stamps the root. There is
   no read-only placement-check command yet, and `inspect` does not report placement.

`/home/robbo/.local/state/arhugula-harness` is a host path that is a candidate, not accepted.
Its acceptance waits on the installed host inventory and restore-scope witness (S5). It is never a default and does not appear in any profile.

Limits you must not read past:

- These profiles do not enable durable pause/resume. That waits on the reviewed B-104
  claim gateway, recovery path and CLI/MCP integration.
- The tutorial and handoff examples are unchanged: they keep state in the checkout and
  declare no placement (non-durable).
- The Gemini and Antigravity overlays are not part of this first release.
- Source tests check the loader and verifier only. Installed restore, filesystem, CLI
  output and launch acceptance are separate, later gates.

## Deployment Boundary

Static readiness checks are safe to run as provider-free CI/local gates. Live
deployment proofs can start daemons, contact collectors, fetch secrets, create
hosted sandboxes, or call providers; keep those on explicit operator approval.

## Source Grounding

This page is grounded in `deploy/images/README.md`,
`deploy/images/harness-runtime.Dockerfile`, `tools/q4_packaging_gate.py`,
`deploy/self-hosted-local/README.md`, `tools/self_hosted_readiness.py`,
`deploy/managed-cloud/README.md`, `tools/managed_cloud_readiness.py`,
`tools/r421_e2b_live_probe.py`, and `justfile`.
