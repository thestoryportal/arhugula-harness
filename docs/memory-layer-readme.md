# Memory Layer README

The harness memory layer is automatic local persistent memory for agents running
inside the harness. On a fresh local checkout, the first inference bootstrap
creates a repo-local memory root at `.harness/memory`, initializes the canonical
directory layout, rebuilds the derived retrieval index, and composes a bounded
memory packet for each model dispatch.

## Plain-Language Overview

The memory layer gives agents a durable project notebook. It stores useful
facts, decisions, preferences, conventions, failure lessons, research notes, and
procedural snapshots in the repo-local harness state directory. Future runs can
retrieve those records and place a small, read-only summary packet into the
model prompt.

This is local-first. The harness-owned filesystem store and derived retrieval
index are the default. Standard memory tools are available for providers that
support tool calls. Provider-native remote memory storage, including Anthropic
native memory APIs, is disabled by default and is the last-priority option when
explicitly enabled.

## Technical Behavior

The automatic runtime binds these components during stage 5 loop initialization:

| Component | Purpose |
| --- | --- |
| `RuntimeConfig.memory` | Operator config for local memory root, token budget, capture toggles, and access modes. |
| `CanonicalMemoryStore` | Source-of-truth filesystem store for canonical memory records and memory operation ledgers. |
| `AutoRefreshingDerivedRetrievalIndexStore` | Derived index that rebuilds on first use or after stale markers. |
| `MemoryRetriever` | Policy-filtered retrieval and packet assembly. |
| `RuntimeMemoryContextComposer` | Per-dispatch access-mode selection, retrieval, and injection ledger writes. |
| `StandardMemoryToolExecutor` | Provider-neutral `memory.*` tool execution for tool-capable providers. |

Access-mode priority is:

1. Provider-neutral standard memory tools when supported and policy-enabled.
2. Local prompt-extension packets.
3. Provider-native remote memory only when explicitly enabled.
4. No memory access when policy or capability denies every mode.

## Configuration

Defaults work without editing `harness.toml`:

```toml
[runtime.memory]
enabled = true
token_budget = 1200
capture_run_events = true
capture_turns = true
prompt_packet_enabled = true
standard_tools_enabled = true
native_provider_enabled = false
policy_id = "policy:automatic-local-memory"
```

Use `root_path` only when you want memory stored outside `.harness/memory`.
Do not put provider keys or tokens in the memory config.

## Usage Workflow

1. Pull the repo and create or update `harness.toml` from `harness.toml.example`.
2. Run a normal harness workflow.
3. The first inference run creates `.harness/memory` and `semantic/index.jsonl`.
4. Agents receive a bounded read-only memory packet on later dispatches.
5. Tool-capable providers can use the standard memory tools under policy.

The memory layer is not a replacement for source control, the roadmap, or
formal design records. It is a persistent retrieval substrate that helps agents
carry useful project context across runs while keeping canonical records,
indexes, and operation ledgers separate.

## Anthropic Native Memory

Anthropic native memory is not required for the harness memory layer. It is a
remote provider API surface, so it is disabled unless
`native_provider_enabled = true`. When enabled, it remains lower priority than
local standard tools and local prompt packets.

## Verification

Useful provider-free checks:

```bash
just memory-closeout-check
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-runtime/tests/test_automatic_memory_runtime.py
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest harness-cp/tests/test_memory_access_mode.py
```
