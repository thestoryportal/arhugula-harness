# Class 1 fork — U-RT-107 daemon `run_workflow` tool signature underspecification

**Status:** PROPOSING — operator ratification required before U-RT-107 substantive code lands.
**Filed:** 2026-05-28, U-RT-107 implementation arc empirical orientation.
**Authority anchor:** workspace `CLAUDE.md` §4.3 Class 1 routing + §4.4 X-AL-3 silent-absorption discipline.
**Workspace precedent:** mirrors `.harness/class_1_fork_u_rt_104_admissibility_keying_and_carrier_defaults.md` filed → ratified → applied single-session 2026-05-28 (same cluster, prior unit). 26th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` posture.

---

## §1 The gap

Runtime spec v1.36 §14.18.1 row `harness run <workflow-file> --daemon` declares the daemon-client surface:

> Connect to `harness daemon` Unix-socket → MCP `run_workflow` tool call → receive `RunResult` → exit

Spec §14.18 change-note line 63 (PRESERVED VERBATIM through v1.32 → v1.36):

> **U-RT-62 FastMCP server (`HarnessMCPServer`) PRESERVED VERBATIM — daemon mode reuses this substrate; ZERO new IPC contract (Q-A=α forecloses SF-2).**

Runtime plan v2.32 §1.8 U-RT-108 (daemon-client mode) Signatures bullet:

> EXTEND U-RT-106 one-shot dispatch with `--daemon` branch: when `--daemon` flag set, INSTEAD of invoking `api.run()` directly, instantiate FastMCP client (Unix-socket transport, same socket path as `harness daemon`) → submit `run_workflow` tool call **with manifest path + config dict** → await response → emit `RunResult` per `--output` mode → exit per §14.18.2 mapping

**The contradiction.** Spec asserts ZERO new IPC contract + U-RT-62 PRESERVED VERBATIM. U-RT-62's `run_workflow(workflow_id: str)` tool (at `harness-runtime/src/harness_runtime/lifecycle/mcp_server.py:168`) consumes a string workflow_id that must already be pre-registered in `HarnessMCPServer.workflow_registry`. In-process `api.run()` pre-registers via `workflow_registry[workflow.workflow_id] = workflow` BEFORE invoking the tool. A remote MCP client over Unix-socket has NO in-process access to write into the daemon's `workflow_registry` — so the spec-declared daemon flow has no mechanism for the client to convey the workflow to the daemon for execution.

Three possible readings:

- **(A) workflow_id = manifest path semantics**. Extend `run_workflow` tool's interpretation of `workflow_id` to accept a filesystem path; daemon's handler loads the manifest from path on each invocation (zero schema-level signature change — semantically widens `workflow_id` from "registry key" to "registry key OR filesystem path").
- **(B) Daemon pre-registers from watched directory**. Operator configures a manifest directory (e.g., `--manifest-dir` flag OR `[runtime] manifest_dir = "..."` in `harness.toml`); daemon at startup loads all manifests + registers into `workflow_registry`; remote clients pass the declared `workflow_id` from a pre-loaded manifest. Signature unchanged.
- **(C) Tool signature additively extended**. `run_workflow(workflow_id: str | None = None, *, manifest_path: str | None = None)` with mutual-exclusion invariant. Backward-compatible at call sites passing `workflow_id`; new daemon-client path passes `manifest_path`. Technically a new IPC contract surface, contradicting spec's "ZERO new IPC contract" framing.

## §2 Per-reading downstream impact

### (A) workflow_id-as-path widening

**Pros**
- Zero schema-level signature change at the MCP tool surface.
- Single tool, single signature; daemon and in-process modes converge on the same call shape.
- Spec "ZERO new IPC contract" reading literally satisfied.

**Cons**
- Semantic widening of `workflow_id` is implicit. The string is overloaded — "registry key" or "filesystem path"? Need a discriminator (e.g., presence of `/` or `.yaml`/`.toml` suffix).
- The handler at U-RT-62 needs to grow a path-resolution branch + manifest-loading code, which is U-RT-104/U-RT-105 substrate consumption. Adds a `WorkflowManifestLoader` import at U-RT-62 — modifies that unit body.
- Concurrent invocations from distinct clients with overlapping path inputs would race on `workflow_registry` writes; need keyed-by-canonical-path-or-id dedup.

### (B) Daemon pre-registers from watched directory

**Pros**
- `run_workflow(workflow_id: str)` signature literally PRESERVED VERBATIM at U-RT-62.
- Daemon-side workflow set is bounded + declarative (operator controls available workflows).
- Concurrent clients invoke against pre-registered workflows; no per-call manifest-load overhead.

**Cons**
- NEW operator-supplied config: `manifest_directory` or `[runtime] manifest_dir`. Requires `RuntimeConfig` extension (X-AL-3 silent absorption risk if not pre-ratified).
- Daemon must reload on filesystem changes OR force operator-restart on manifest updates. Watcher infrastructure adds scope.
- workflow_id collision across manifest files (two files declaring same workflow_id) needs disambiguation policy.
- Implicit coupling: U-RT-108 daemon-client must know which workflow_ids the daemon pre-registered. Out-of-band knowledge.

### (C) Tool signature additively extended

**Pros**
- Both modes explicit at the tool surface.
- Daemon-client passes `manifest_path` (full self-description); no daemon-side pre-registration needed.

**Cons**
- **Directly contradicts spec line 63 "ZERO new IPC contract".** Operator ratification of (C) would supersede that line, requiring a v1.37 spec amendment.
- U-RT-62 signature change requires plan revision (U-RT-62 PRESERVED VERBATIM language at v2.31 + v2.32 must be retracted).
- Adds mutual-exclusion validation to handler body.

## §3 Cross-axis cascade

ZERO at all three readings (intra-runtime-axis only). U-RT-62 + plan §1.7 (U-RT-107) + §1.8 (U-RT-108) absorb the chosen reading; CP / AS / OD / CXA / ADR / ADD / PRD unaffected.

## §4 Adjacent observation — `_state["_current_tool_ctx"]` race

Independent of the signature gap, U-RT-62's `_state["_current_tool_ctx"] = ctx` line (mcp_server.py:215) is a race condition for concurrent invocations from distinct MCP client sessions. Spec §14.18.5 MUSTs "per-session ctx isolation"; current single-shared `_state` dict races. Likely resolves via `contextvars`-based per-call binding OR per-connection bootstrap. Surfaces here for the record; **not patched per FM-2** at this fork — separate sub-finding distinct from the signature gap. Operator-discretion routing at a follow-on arc.

## §5 Adjacent observation — uvicorn vs bootstrap signal-handler conflict

Bootstrap stage 7 installs `loop.add_signal_handler(SIGINT, _on_drain_signal, ctx)` per `harness-runtime/src/harness_runtime/drain.py:147-176`. uvicorn's `serve()` also installs its own SIGINT handler. The two will conflict in daemon mode. Implementation detail (not fork-worthy); resolves via `loop.add_signal_handler` precedence OR uvicorn lifespan hooks OR custom drain shim. Implementer discretion at the apply arc post-ratification.

## §6 Recommendation

**Recommended reading: (A) workflow_id-as-path widening.**

Rationale:
1. Spec "ZERO new IPC contract" line is load-bearing — operator-ratified at v1.32 → v1.36 chain. (A) literally preserves it.
2. Avoids new `RuntimeConfig` field surface (X-AL-3 silent-absorption risk at (B)).
3. Smallest U-RT-62 modification footprint — discriminator + load branch in the handler body, no signature change at the tool decorator.
4. Symmetric with U-RT-106 in-process: `harness run <file>` loads from path on each invocation; `harness run <file> --daemon` does the same path-load INSIDE the daemon's tool handler. Operator mental model unified.

Recommended discriminator at the daemon handler: treat `workflow_id` as a filesystem path iff it contains `/` OR ends in `.yaml` / `.yml` / `.toml`; otherwise treat as a registry key (preserving in-process api.run() pre-registration semantics).

## §7 Q-set for operator ratification

| Q | Question | Recommendation |
|---|---|---|
| Q1 | Which reading? | **(A) workflow_id-as-path widening.** |
| Q2 | At U-RT-62 handler, the discriminator between "registry key" and "filesystem path"? | (i) Path-iff-contains-slash-or-yaml/toml-suffix (recommended). (ii) Always-attempt-registry-first-then-path-fallback. (iii) Operator-explicit prefix marker (e.g., `path://`). |
| Q3 | Should the daemon's per-call manifest-load be cached? | (a) No cache; load on every invocation (simplest; recommended for v1). (b) Path-keyed cache with size bound; invalidate on mtime change. (c) Path-keyed cache without invalidation (operator-restart required for manifest updates). |
| Q4 | Apply at this session (single-arc absorption like U-RT-104 precedent) OR defer? | (a) Apply at this session (recommended; mirrors U-RT-104 precedent at same cluster). (b) Defer to follow-on session. |
| Q5 | Cross-axis cascade? | **(β) NO new CXA edge.** Intra-runtime-axis only. |

## §8 Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-28 during U-RT-107 implementation arc empirical orientation |
| Filer | Phase 7 Phase 2b implementer at worktree `worktree-phase-2b-u-rt-102-cli-scaffolding` |
| Authority anchor | workspace `CLAUDE.md` §4.3 Class 1 routing + §4.4 X-AL-3 silent absorption discipline |
| Predecessor (apply arc) | runtime spec v1.36 + runtime plan v2.32 (U-RT-104 Reading β apply pass) at this cluster, prior unit |
| Successor consumption | runtime spec v1.36 → v1.37 (or canonical-reading amendment at v1.37); runtime plan v2.32 → v2.33; U-RT-62 implementation extension; U-RT-107 + U-RT-108 implementation |
| ZERO cross-axis cascade | Verified — intra-runtime-axis only |
| Status PROPOSING → APPLIED post-ratification | Awaiting operator AskUserQuestion |
