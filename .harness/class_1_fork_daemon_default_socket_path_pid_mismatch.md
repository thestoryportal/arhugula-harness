# Class 1 Fork Record — `harness daemon` default socket-path PID mismatch

**Filed:** 2026-05-29 (probe v4 — operator-facing daemon-mode probe surfaced finding #1).
**Class:** 1 (operator-facing default contract structurally cannot work; spec silent on the resolution mechanism).
**Status:** ⏳ PROPOSING — operator-routed apply-arc owed at follow-on session.
**Surfaced by:** `[[use-the-product-probe]]` cardinality 4 — attempted `harness daemon` + `harness run --daemon` happy-path from operator perspective; daemon binds at one socket, client looks at a different socket, "daemon not running?" emitted while daemon IS running.
**Surfacing PR:** probe-v4 worktree this session (no production change yet).
**Anchors:** runtime spec v1.39 §14.18.1 line 232–233 (daemon ↔ client coordination invariant); impl at `harness-runtime/src/harness_runtime/cli/app.py:368-373` `_default_daemon_socket_path` body; consumed at `:297` (client) + `:486` (daemon-mode default resolution sites).

---

## 1. The defect

`_default_daemon_socket_path()` is defined as:

```python
def _default_daemon_socket_path() -> Path:
    """Default Unix-socket path for the daemon — `/tmp/harness-daemon-{pid}.sock`."""
    import os
    import tempfile

    return Path(tempfile.gettempdir()) / f"harness-daemon-{os.getpid()}.sock"
```

Both the daemon entrypoint (when `--socket-path` is not supplied) AND the daemon-client (when `--socket-path` is not supplied on `harness run --daemon`) call this same function. But each runs in its own process, so `os.getpid()` returns different values:

- Daemon process binds at `/tmp/harness-daemon-<DAEMON_PID>.sock`
- Client process attempts to connect at `/tmp/harness-daemon-<CLIENT_PID>.sock`

These paths never match unless the operator explicitly threads `--socket-path` to both invocations. The client's existence check fails at `app.py:299-304`:

```python
if not resolved_socket.exists():
    _print_fail_class(
        "RT-FAIL-CLI-DAEMON-CONNECTION",
        f"socket path {resolved_socket} does not exist (daemon not running?)",
    )
```

The error message claims the daemon is not running. In the operator-facing default path, the daemon IS running — at a different socket.

## 2. Empirical surfacing

Probe v4 sequence at HEAD `eb46f26` (post-PR #84 merge):

1. Inspected `_default_daemon_socket_path()` at `cli/app.py:368-373`; observed `os.getpid()` coupling.
2. Verified callers — same function at both client side (`:297`) and daemon side (`:486`); each computes its own PID.
3. Integration test `test_ac3_daemon_mode_equivalent_to_one_shot_with_real_llm` PASSES (11.75s against real Anthropic) because the test explicitly threads `socket_path=tmp_path / "smoke.sock"` to BOTH the daemon subprocess AND the client invocation via shared variable — never exercises the default-path code.
4. Operator-facing happy path (`harness daemon` in one terminal, `harness run --daemon <wf>` in another, both without `--socket-path`) structurally cannot succeed at HEAD.

The PID-suffix is unconditional; no env-var fallback, no shared discovery file, no symlink to "current daemon".

## 3. Three Readings

### Reading A — single well-known default path

Drop `os.getpid()` from `_default_daemon_socket_path()`; use `/tmp/harness-daemon.sock` (or `${XDG_RUNTIME_DIR}/harness-daemon.sock` on Linux). Daemon binds there; client looks there. Default Just Works for single-daemon-per-host operator scenarios.

- **Pros:** Operator-facing default actually works. Matches Postgres/Docker/systemd conventions. Minimal LOC.
- **Cons:** Multi-daemon-per-host operator scenarios require explicit `--socket-path` for at least one. Tests already pass explicit paths (no test-isolation regression). Stale socket from a previous-run daemon crash could collide with new daemon startup (standard mitigation: bind-with-cleanup on `EADDRINUSE`).

**Recommended.**

### Reading B — pidfile-based discovery

Daemon writes `${XDG_RUNTIME_DIR}/harness-daemon.pid` (or `/tmp/harness-daemon.pid` fallback) containing its socket-path on bind. Client reads pidfile (or `$HARNESS_DAEMON_SOCKET` env override) to discover the socket. Default still PID-suffixed but discoverable.

- **Pros:** Preserves multi-daemon support without explicit `--socket-path` on client. Standard daemon-discovery shape.
- **Cons:** Two new surfaces (pidfile write + read). XDG_RUNTIME_DIR semantics differ on macOS (no canonical equivalent). Pidfile staleness adds a new failure mode.

### Reading C — spec narrow + required-flag

Amend spec v1.39 §14.18.1 to declare `--socket-path` REQUIRED on both `harness daemon` and `harness run --daemon`. Drop `_default_daemon_socket_path()`. Operator sees "missing required option" instead of "daemon not running".

- **Pros:** ZERO ambiguity. Operator can't accidentally invoke a broken default.
- **Cons:** Worst operator UX of the three — every daemon invocation requires the flag. Spec-narrowing under operator-facing apply discipline is the less-conservative direction (per PR #84 Reading-A precedent).

## 4. Adjacent observations (NOT patched per FM-2)

(a) **`harness daemon` without `harness.toml` emits Pydantic dict-repr to stderr** — bootstrap probe earlier surfaced `RT-FAIL-CLI-CONFIG-LOAD: Pydantic validation failed: [{'type': 'missing', 'loc': ('deployment_surface',), 'msg': 'Field required', 'input': {}, 'url': 'https://errors.pydantic.dev/2.13/v/missing'}, ...]`. Spec-canonical fail-class IS emitted (per §14.18.4 `RT-FAIL-CLI-CONFIG-LOAD` → exit 3), but the payload is Python dict `repr()`. Operator UX gap: no `harness init` template-generator; no human-readable "missing fields: deployment_surface, repository_root, otel, default_topology"; no pointer to docs. Class 3 informational; routes to follow-on operator-UX-polish arc.

(b) **SIGINT mid-workflow drain not probed at this arc** — operator probe goal included SIGINT-during-step. Per `[[fork-u-rt-44-workflow-loop-drain]]`, the in-flight drain primitive is STRUCK; mid-step SIGINT sets `drained_flag` but the workflow loop does NOT check it mid-step. Probe deferred: requires (i) a long-running step (e.g., LLM call with high `max_tokens`) AND (ii) instrumentation to verify the daemon-side drain semantics match operator expectation. Class 3 informational; meaningful probe owed at separate arc once `[[fork-u-rt-44]]` is resolved.

(c) **`ollama` provider degraded warning at daemon bootstrap** — `ProviderDegradedWarning: provider='ollama': degraded (unreachable): Failed to connect to Ollama` emitted at every daemon startup when `ollama_optional=true` and no Ollama daemon is running locally. Expected behavior per the allowlist semantic, but the warning at every bootstrap could be silenced when `ollama_optional=true`. Class 3 informational; routes separately.

(d) **`_default_daemon_socket_path` docstring is silently wrong** — the docstring says "Default Unix-socket path for the daemon" without disclosing the PID-coupling. Operator reading the docstring would reasonably assume daemon and client compute the same default. Class 3 informational; closure can ride the Reading-A apply if chosen.

## 5. Probe-pattern continues to validate

- PR #79 §4(e) cardinality 1 (YAML loader, 17 findings)
- PR #83 cardinality 2 (U-CP-74 actor malformation)
- PR #84 cardinality 3 (parent-app subcommand registration gap)
- This finding cardinality 4 (default-socket-path PID-coupling)

The use-the-product-probe pattern continues to surface operator-facing defects that within-process integration tests structurally cannot catch. The `mech-beta-ac3` test passes because it threads explicit `socket_path=tmp_path / "smoke.sock"` to both subprocess + client; it never exercises the default-path code that the operator hits first.

## 6. Test plan

- [ ] Review Readings A + B + C + adjacent observations
- [ ] AskUserQuestion at apply-arc opening (Reading A recommended — single-daemon-per-host happy path Just Works; multi-daemon retains `--socket-path` override)
- [ ] Apply arc ships either default-path rename (Reading A) OR pidfile-discovery (Reading B) OR spec narrowing + required flag (Reading C)
- [ ] Adjacent observation (a) — author `harness init` template generator OR spec-clarify the dict-repr fail-class payload — bounded follow-on
- [ ] Adjacent observation (b) — SIGINT mid-step probe owed after `[[fork-u-rt-44]]` resolution

## 7. Closure-back-reference

Per `[[use-the-product-probe]]` discipline: every probe ratification arc updates the pattern memory entry with the new cardinality + findings list. This fork doc's apply-pass MUST update `memory/use-the-product-probe-pattern.md` to cardinality 4.
