# Codex Hook Contract Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** Eliminate the observed Codex `PreToolUse` and `PostCompact` parser failures while preserving Claude Code behavior, retaining hard-deny safety, restoring compaction checkpoint context, and proving the real installed Codex host accepts the resulting hook outputs.

**Architecture:** Keep the shared Claude hook producers authoritative and unchanged. Route only the incompatible Codex event registrations through the existing `.codex/hooks/codex_hook_adapter.py` host boundary: suppress an unsupported bare `PreToolUse allow` so Codex can continue into the already-supported `PermissionRequest allow`, preserve a valid `PreToolUse deny`, convert Claude `PostCompact.additionalContext` into Codex-supported universal output, and replay the same context during `SessionStart(source=compact)` for model-facing recovery. Treat leaked legacy loop markers as lifecycle state, not JSON adaptation: clean the current stale markers once and use the existing canonical `loop_deactivate` path for future Codex pause/stop requests.

**Tech Stack:** Python 3.12, Bash, JSON/jq, pytest, installed Codex CLI loopback witness, just, Git/GitHub CI.

---

## Review contract

This plan implements an operational compatibility repair. It does not change `design-substrate/**`, semantic contracts, roadmap ordering, Claude hook schemas, the permission allowlist, or the autonomous-loop safety policy.

> **Execution record:** Tasks 2-4 preserve the original pre-implementation design and RED examples. Where their sample code conflicts with the later **Claude Code Opus 5 review reconciliation**, the reconciliation and final regression tests are authoritative; notably, malformed permission output ships as structured deny with exit 0, timeout budgets are split by host path, and both real adapters remain in the installed-host witness.

Assumptions verified before this plan was written:

- `.codex/hooks.json` currently invokes `tools/hooks/permission-guard.sh` directly for `PreToolUse` and `tools/hooks/postcompact-reinject.sh` directly for `PostCompact`.
- The shared permission guard intentionally emits Claude's bare `PreToolUse permissionDecision: allow`; Codex 0.146.0 rejects that shape unless `updatedInput` is also present.
- The same shared guard's `PermissionRequest decision.behavior: allow` and `PreToolUse permissionDecision: deny` shapes are supported by Codex.
- The shared post-compaction producer emits `hookSpecificOutput.additionalContext`; Codex `PostCompact` accepts only universal top-level output fields.
- The current runtime witness replaces project hook handlers with a recorder, so it proves dispatch but cannot detect a real handler's invalid output.
- `.harness/.loop-active` and `.harness/.loop-halt` are stale local legacy-runner state. The Codex evidence loop does not create either marker.

### Acceptance matrix

| Claim | Required witness | Go condition |
|---|---|---|
| Safe loop-mode `PreToolUse` no longer fails parsing | Adapter unit test plus installed-Codex loopback run with the real adapter enabled | Adapter emits no `PreToolUse` output for bare allow; runtime stderr contains neither the unsupported-decision diagnostic nor a failed-hook diagnostic |
| Loop-mode safe operations can still be approved | Existing direct `PermissionRequest` registration and shared guard test | `PermissionRequest decision.behavior=allow` remains registered and its hermetic test passes |
| Hard stops still block | Adapter unit test using a destructive Git command | Supported `PreToolUse deny` and non-empty reason are preserved exactly |
| `PostCompact` output is host-valid | Adapter unit test, registration test, and installed-host automatic-compaction witness | Output contains only supported universal top-level fields; the real host reports `PostCompact Completed` with no parser diagnostic |
| Compacted sessions recover the checkpoint pointer | Compact-context adapter test plus SessionStart wrapper test | Only `source=compact` appends the session-scoped precompact checkpoint path |
| Claude behavior is unchanged | Existing shared-hook shell tests | Shared allow/deny and `PostCompact.additionalContext` assertions remain green without editing their producers |
| Legacy mode is actually off after the requested pause | Canonical lifecycle command and filesystem checks | `.loop-active`, `.loop-halt`, and `.loop-iter` are absent and a `DEACTIVATE` row is present |
| Full repo parity remains green | `just codex-check`, live witness, CI, merge lenses | Every required gate passes against the final diff and final PR HEAD |

Any failed row is a no-go. Do not weaken or delete an assertion to obtain green. Diagnose, fix the smallest contradicted unit, and replay that row plus every downstream gate affected by the diff.

## File ownership

Implementation may change only:

- `.codex/hooks/codex_hook_adapter.py`
- `.codex/hooks.json`
- `tools/hooks/codex-session-start.sh`
- `tools/test_codex_workflow_parity.py`
- `tools/codex_hook_runtime_witness.py`
- `.codex/hooks/README.md`
- `.codex/notes/claude-codex-parity.md`
- `.harness/merge-gate-log.md` during the mandatory merge gate

The implementation must not edit:

- `tools/hooks/permission-guard.sh`
- `tools/hooks/postcompact-reinject.sh`
- their Claude-facing shell tests except to add a non-mutating invocation to an aggregate gate
- `design-substrate/**`
- `.harness/roadmap_status.md` in the implementation PR; this repair does not advance a semantic roadmap unit, but the mandatory §12.2 one-file terminating refresh still follows the substantive merge. The current next action remains the operator-owned `B-124` ratification, followed by `B-147`, `B-145`, and `B-144`.

---

### Task 1: Initialize the evidence-bound repair arc

**Files:**

- Create locally: `.harness/codex_loop_state.json` through the existing recipe
- Verify only: `AGENTS.md`, `.harness/roadmap_status.md`, `.harness/handoff/README-resume.md`, `.codex/notes/deterministic-context-workflow.md`

- [ ] **Step 1: Reuse the dedicated reviewed-plan worktree and promote its branch**

The plan already lives in the required isolated worktree. After approval, run:

```bash
cd /Users/robertrhu/Projects/arhugula-v2/.codex-worktrees/codex-hook-contract-fix-plan
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
git branch -m fix/codex-hook-contract-recovery
```

Expected: the worktree contains only the committed reviewed plan, is now on `fix/codex-hook-contract-recovery`, and remains registered by `git worktree list`. Do not create a second worktree or drop the plan commit by branching again from `main`.

- [ ] **Step 2: Bootstrap the Codex autonomous arc**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-autonomous-arc codex-hook-contract-recovery
```

Expected: `worktree_ready` and `preflight` are recorded as passed; `.harness/codex_loop_state.json` names this branch and worktree.

- [ ] **Step 3: Record the plan gate**

```bash
just codex-loop-record --phase plan --status passed \
  --command "docs/superpowers/plans/2026-08-10-codex-hook-contract-recovery.md" \
  --evidence "approved host-adapter repair; owned files and acceptance matrix fixed"
```

Expected: `just codex-loop-status` shows `plan: passed` after `preflight`.

- [ ] **Step 4: Run the current witness as an observation-layer control**

```bash
HARNESS_LOOP=1 UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-hook-runtime-witness
```

Expected on the unmodified base: the witness passes because it substitutes recorders for every real project handler. Record this as a positive control and explicit coverage gap, not as evidence that the real outputs are valid. The required RED is created and recorded in Task 2.

---

### Task 2: Normalize `PreToolUse` at the Codex adapter boundary

**Files:**

- Modify: `.codex/hooks/codex_hook_adapter.py`
- Modify: `.codex/hooks.json`
- Test: `tools/test_codex_workflow_parity.py`

- [ ] **Step 1: Add failing adapter tests for the three legal outcomes**

Add tests beside the existing adapter tests in `tools/test_codex_workflow_parity.py`. Use a temporary Git repository with `.harness/.loop-active`, set `CLAUDE_PROJECT_DIR` to it, and invoke the adapter through `_run_adapter`.

```python
def _loop_repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".harness").mkdir()
    (tmp_path / ".harness" / ".loop-active").touch()
    return tmp_path


def test_permission_guard_adapter_suppresses_bare_pretool_allow(tmp_path: Path) -> None:
    repo = _loop_repo(tmp_path)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Grep",
        "tool_input": {"path": str(repo)},
        "cwd": str(repo),
    }

    proc = _run_adapter("permission-guard", payload, cwd=repo)

    assert proc.returncode == 0, proc.stderr
    assert proc.stdout == ""


def test_permission_guard_adapter_preserves_supported_pretool_deny(tmp_path: Path) -> None:
    repo = _loop_repo(tmp_path)
    payload = {
        "hook_event_name": "PreToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": "git push --force origin main"},
        "cwd": str(repo),
    }

    proc = _run_adapter("permission-guard", payload, cwd=repo)

    assert proc.returncode == 0, proc.stderr
    specific = json.loads(proc.stdout)["hookSpecificOutput"]
    assert specific["hookEventName"] == "PreToolUse"
    assert specific["permissionDecision"] == "deny"
    assert specific["permissionDecisionReason"].strip()


def test_permission_guard_adapter_fails_closed_on_non_decision_output(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    adapter = _adapter_module()
    monkeypatch.setattr(adapter, "run_claude_hook", lambda *_args: {"systemMessage": "bad"})

    assert adapter.permission_guard({"hook_event_name": "PreToolUse"}) == 2
```

If `_adapter_module()` is not already present, add it using the same `importlib.util` pattern as `_runtime_witness_module()`.

- [ ] **Step 2: Update registration assertions before implementation**

Change the registration expectation for `PreToolUse`, matcher `*`, from `permission-guard.sh` to both `codex_hook_adapter.py` and `permission-guard`. Leave `PermissionRequest`, matcher `*`, expecting `permission_request.py` and the direct `permission-guard.sh`.

- [ ] **Step 3: Run the narrow tests to prove RED**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest \
  tools/test_codex_workflow_parity.py \
  -k 'permission_guard_adapter or hooks_cover_supported_claude_lifecycle' -q
```

Expected: new tests fail because the mode is absent and `PreToolUse` still points directly at the shared shell producer.

- [ ] **Step 4: Record the red gate before implementing**

```bash
just codex-loop-record --phase red --status failed \
  --command "UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest tools/test_codex_workflow_parity.py -k 'permission_guard_adapter or hooks_cover_supported_claude_lifecycle' -q" \
  --evidence "adapter mode absent and Codex PreToolUse still directly registered to unsupported bare-allow producer"
```

Expected: the failing test command and exact assertion are recorded before any implementation edit.

- [ ] **Step 5: Implement a typed normalization boundary**

Add a function to `.codex/hooks/codex_hook_adapter.py` that accepts only the shared producer's supported decision variants. Bare allow becomes no opinion; supported deny passes through; malformed or unexpected output exits nonzero so the safety hook fails closed.

```python
def permission_guard(payload: dict[str, Any]) -> int:
    if payload.get("hook_event_name") != "PreToolUse":
        print("permission-guard adapter requires PreToolUse", file=sys.stderr)
        return 2

    response = run_claude_hook(
        "tools/hooks/permission-guard.sh", payload, project_dir(payload)
    )
    if response is None:
        return 0
    specific = response.get("hookSpecificOutput")
    if not isinstance(specific, dict) or specific.get("hookEventName") != "PreToolUse":
        print("permission-guard adapter received invalid shared output", file=sys.stderr)
        return 2

    decision = specific.get("permissionDecision")
    if decision == "allow":
        # Codex approval and rewrites belong to PermissionRequest, not PreToolUse.
        return 0
    if decision == "deny" and isinstance(
        specific.get("permissionDecisionReason"), str
    ) and specific["permissionDecisionReason"].strip():
        print(json.dumps(response, separators=(",", ":")))
        return 0

    print("permission-guard adapter received unsupported shared decision", file=sys.stderr)
    return 2
```

Extend `main()`'s explicit mode set and dispatch without changing the existing two modes.

- [ ] **Step 6: Route only Codex `PreToolUse` through the adapter**

In `.codex/hooks.json`, replace only the wildcard `PreToolUse` guard command:

```json
"command": "/usr/bin/python3 \"$(git rev-parse --show-toplevel)/.codex/hooks/codex_hook_adapter.py\" permission-guard"
```

Do not change the wildcard `PermissionRequest` guard command. That direct shared producer is the supported approval channel after the `PreToolUse` adapter returns no opinion.

- [ ] **Step 7: Run the narrow tests to prove GREEN**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest \
  tools/test_codex_workflow_parity.py \
  -k 'permission_guard_adapter or hooks_cover_supported_claude_lifecycle' -q
bash tools/hooks/test_permission_guard.sh
```

Expected: adapter tests pass; the existing Claude shared-hook suite still proves bare allow, hard deny, and PermissionRequest behavior.

- [ ] **Step 8: Checkpoint the atomic permission unit without committing**

```bash
git diff --check
just codex-checkpoint permission-adapter-green
```

Expected: the permission-boundary diff is clean and the checkpoint records its green tests. Do not commit yet: this repository's autonomous-loop contract places the implementation commit after decorrelated review and closeout.

---

### Task 3: Adapt `PostCompact` and re-inject checkpoint context on compact SessionStart

**Files:**

- Modify: `.codex/hooks/codex_hook_adapter.py`
- Modify: `.codex/hooks.json`
- Modify: `tools/hooks/codex-session-start.sh`
- Test: `tools/test_codex_workflow_parity.py`
- Verify unchanged: `tools/hooks/postcompact-reinject.sh`, `tools/hooks/test_postcompact_reinject.sh`

- [ ] **Step 1: Add failing tests for Codex PostCompact output**

Add adapter tests that build a temporary repository with `.harness/roadmap_status.md` and a session-scoped checkpoint.

```python
def test_post_compact_adapter_emits_only_universal_output(tmp_path: Path) -> None:
    repo = _checkpoint_repo(tmp_path, session_id="session-a")
    payload = {"hook_event_name": "PostCompact", "session_id": "session-a", "cwd": str(repo)}

    proc = _run_adapter("post-compact", payload, cwd=repo)

    assert proc.returncode == 0, proc.stderr
    output = json.loads(proc.stdout)
    assert set(output) == {"systemMessage"}
    assert "precompact-latest-session-a.md" in output["systemMessage"]


def test_compact_context_mode_returns_raw_model_context(tmp_path: Path) -> None:
    repo = _checkpoint_repo(tmp_path, session_id="session-a")
    payload = {"hook_event_name": "SessionStart", "source": "compact", "session_id": "session-a", "cwd": str(repo)}

    proc = _run_adapter("compact-context", payload, cwd=repo)

    assert proc.returncode == 0, proc.stderr
    assert "precompact-latest-session-a.md" in proc.stdout
    assert "hookSpecificOutput" not in proc.stdout
```

Use this fixture so the existing shared producer sees a real branch, HEAD, roadmap pointer, and session-scoped checkpoint:

```python
def _checkpoint_repo(tmp_path: Path, *, session_id: str) -> Path:
    subprocess.run(["git", "init", "-q", "-b", "main", str(tmp_path)], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "config", "user.name", "Test"], check=True)
    checkpoint_dir = tmp_path / ".harness" / ".checkpoints"
    checkpoint_dir.mkdir(parents=True)
    (tmp_path / ".harness" / "roadmap_status.md").write_text(
        "# Status\n\n## Next action\n\n**`U-TEST-01`** verify hooks.\n",
        encoding="utf-8",
    )
    (checkpoint_dir / f"precompact-latest-{session_id}.md").touch()
    subprocess.run(["git", "-C", str(tmp_path), "add", ".harness/roadmap_status.md"], check=True)
    subprocess.run(["git", "-C", str(tmp_path), "commit", "-qm", "fixture"], check=True)
    return tmp_path
```

- [ ] **Step 2: Add failing registration and behavioral SessionStart routing tests**

Change the `PostCompact`, matcher `*`, expectation to `codex_hook_adapter.py` plus `post-compact`. Add a parametrized wrapper test beside `test_session_start_bounds_advisory_hygiene`. Copy the wrapper and its shell dependencies into the temporary tree as that test already does, then install this adapter stub at the relative path the wrapper invokes:

```python
(tmp_path / ".codex" / "hooks" / "codex_hook_adapter.py").write_text(
    "import sys\n"
    "assert sys.argv[1] == 'compact-context'\n"
    "print('precompact-latest-wrapper-session.md')\n",
    encoding="utf-8",
)
```

Run the copied wrapper once with `source="startup"` and once with `source="compact"`, using distinct session IDs. Assert the pointer is absent from startup output and present in compact output. Retain the existing source-order assertion and extend it so the adapter call sorts after `loop-gc.sh` and before the final `lease_action activate`.

- [ ] **Step 3: Run the narrow tests to prove RED**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest \
  tools/test_codex_workflow_parity.py \
  -k 'post_compact_adapter or compact_context or hooks_cover_supported_claude_lifecycle' -q
```

Expected: the two adapter modes and wrapper routing do not yet exist.

- [ ] **Step 4: Reuse the shared Claude producer as the single content source**

Add these functions to `.codex/hooks/codex_hook_adapter.py`:

```python
def compact_context(payload: dict[str, Any]) -> str | None:
    return additional_context(
        run_claude_hook("tools/hooks/postcompact-reinject.sh", payload, project_dir(payload))
    )


def post_compact(payload: dict[str, Any]) -> int:
    context = compact_context(payload)
    if context:
        print(json.dumps({"systemMessage": context}, separators=(",", ":")))
    return 0


def print_compact_context(payload: dict[str, Any]) -> int:
    context = compact_context(payload)
    if context:
        print(context)
    return 0
```

Add `post-compact` and `compact-context` to `main()`'s explicit mode set and dispatch table. The universal `systemMessage` makes the `PostCompact` result host-valid; the raw mode exists only for the SessionStart wrapper and must never be registered as a hook command.

- [ ] **Step 5: Route Codex PostCompact through the adapter**

In `.codex/hooks.json`, replace the direct shared command with:

```json
"command": "/usr/bin/python3 \"$(git rev-parse --show-toplevel)/.codex/hooks/codex_hook_adapter.py\" post-compact"
```

- [ ] **Step 6: Append compact-only context in the SessionStart wrapper**

In `tools/hooks/codex-session-start.sh`, parse the source and invoke the raw adapter mode only for compaction resumes:

```bash
SOURCE=$(printf '%s' "$PAYLOAD" \
  | jq -r 'if (.source? | type) == "string" then .source else "" end') \
  || { echo "codex-session-start: invalid SessionStart payload" >&2; exit 2; }
COMPACT_CONTEXT=""
if [ "$SOURCE" = "compact" ]; then
  COMPACT_CONTEXT=$(printf '%s' "$PAYLOAD" \
    | /usr/bin/python3 "$_DIR/../../.codex/hooks/codex_hook_adapter.py" compact-context) \
    || exit $?
fi
```

Append `COMPACT_CONTEXT` to `CONTEXT` using the wrapper's existing newline pattern. Do not invoke it for `startup`, `resume`, or `clear`.

- [ ] **Step 7: Run compact-path tests and the unchanged Claude producer suite**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest \
  tools/test_codex_workflow_parity.py \
  -k 'post_compact_adapter or compact_context or hooks_cover_supported_claude_lifecycle' -q
bash tools/hooks/test_postcompact_reinject.sh
```

Expected: Codex output is universal-only; compact context carries the correct session checkpoint; Claude output remains `hookSpecificOutput.additionalContext`.

- [ ] **Step 8: Checkpoint the atomic compaction unit without committing**

```bash
git diff --check
just codex-checkpoint compact-context-green
```

Expected: the compaction unit and its tests are captured in a fresh checkpoint with no shared producer changes. Keep the complete implementation uncommitted until the loop's commit gate.

---

### Task 4: Make the provider-free witness exercise the real permission adapter

**Files:**

- Modify: `tools/codex_hook_runtime_witness.py`
- Test: `tools/test_codex_workflow_parity.py`

- [ ] **Step 1: Add failing witness-construction tests**

Add tests proving `_witness_hooks` substitutes an absolute real `permission-guard` adapter command while replacing all unrelated handlers with the recorder.

```python
def test_runtime_witness_preserves_only_real_permission_adapter(tmp_path: Path) -> None:
    witness = _runtime_witness_module()
    hooks = witness._witness_hooks(tmp_path / "record.py")
    commands = [
        hook["command"]
        for group in hooks["hooks"]["PreToolUse"]
        for hook in group["hooks"]
    ]

    real = [command for command in commands if command.endswith(" permission-guard")]
    assert len(real) == 1
    assert str(witness.ROOT / ".codex" / "hooks" / "codex_hook_adapter.py") in real[0]
    assert all(
        "record.py" in command or command == real[0]
        for command in commands
    )
```

Add an assertion helper test that supplies stderr containing the known invalid-output diagnostic and expects a `RuntimeError`.

- [ ] **Step 2: Run witness unit tests to prove RED**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest \
  tools/test_codex_workflow_parity.py -k 'runtime_witness' -q
```

Expected: `_witness_hooks` currently replaces the permission adapter too, so the preservation assertion fails.

- [ ] **Step 3: Substitute exactly one absolute real handler in the generated hook config**

Refactor `_witness_hooks` so it first locates a project registration containing both `codex_hook_adapter.py` and `permission-guard`. Replace that registration with an absolute command pointing back to the repository under test; every other command remains replaced by the recorder. Copying the registered command unchanged is incorrect because its `git rev-parse --show-toplevel` would resolve inside the temporary witness repository, where `.codex/hooks/codex_hook_adapter.py` does not exist. Fail if zero or more than one real permission adapter registration is found.

```python
def _is_permission_adapter(command: str) -> bool:
    return "codex_hook_adapter.py" in command and command.rstrip().endswith(
        " permission-guard"
    )


def _permission_adapter_command() -> str:
    return " ".join(
        (
            shlex.quote(sys.executable),
            shlex.quote(str(ROOT / ".codex" / "hooks" / "codex_hook_adapter.py")),
            "permission-guard",
        )
    )
```

The generated config must therefore exercise project-owned normalization while the recorder continues to prove dispatch for lifecycle and tool phases.

- [ ] **Step 4: Arm only the synthetic loopback process**

Set these environment values immediately before the witness `codex exec` subprocess:

```python
env["HARNESS_LOOP"] = "1"
env["CLAUDE_PROJECT_DIR"] = str(repo)
```

This forces the shared producer to emit its bare allow for the witness's safe Bash and `apply_patch` calls. The adapter must suppress it. The environment dies with the child process and must not mutate the operator's shell or repository markers.

- [ ] **Step 5: Fail on host parser diagnostics even when Codex exits zero**

Add a helper that scans combined stdout/stderr for both observed failure families:

```python
HOOK_FAILURE_MARKERS = (
    "unsupported permissionDecision:allow",
    "PreToolUse Failed",
    "invalid PostCompact hook JSON output",
    "PostCompact Failed",
)


def _assert_no_hook_parser_failure(stdout: str, stderr: str) -> None:
    combined = f"{stdout}\n{stderr}"
    found = [marker for marker in HOOK_FAILURE_MARKERS if marker in combined]
    if found:
        raise RuntimeError(f"Codex reported hook parser failure: {found}")
```

Call it before `_assert_witness`. Include `real_handlers: ["PreToolUse:permission-guard"]` in the final JSON evidence.

- [ ] **Step 6: Run the unit lane and installed-host witness**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest \
  tools/test_codex_workflow_parity.py -k 'runtime_witness' -q
UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-hook-runtime-witness
```

Expected: all required event/effect assertions pass; JSON evidence names the real adapter; no hook parser marker appears.

- [ ] **Step 7: Checkpoint the atomic runtime-witness unit without committing**

```bash
git diff --check
just codex-checkpoint real-handler-witness-green
```

Expected: the witness hardening is green and identified by its own checkpoint while remaining part of the uncommitted implementation diff.

---

### Task 5: Retire leaked legacy loop state through the canonical lifecycle

**Files:**

- Modify local ignored state only: `.harness/.loop-active`, `.harness/.loop-halt`, `.harness/.loop-iter`, `.harness/loop_status.md`
- Verify only: `.agents/skills/loop-stop/SKILL.md`, `.claude/skills/loop-stop/SKILL.md`, `tools/hooks/loop_lib.sh`

This task runs only after Tasks 2 through 4 are green. It is not committed. It is authorized by the operator's prior instruction to pause after the current arc.

Run every command in this task from the affected shared root, not from the implementation worktree; loop markers are worktree-local.

- [ ] **Step 1: Prove the exact pre-cleanup state**

```bash
cd /Users/robertrhu/Projects/arhugula-v2
for path in .harness/.loop-active .harness/.loop-halt .harness/.loop-iter; do
  if [ -e "$path" ]; then stat -f '%N %Sm' "$path"; else echo "$path absent"; fi
done
tail -n 20 .harness/loop_status.md
```

Expected for the known incident: active and halt markers exist without a later deactivation row.

- [ ] **Step 2: Run the canonical idempotent deactivation**

```bash
source tools/hooks/lib.sh && source tools/hooks/loop_lib.sh && loop_deactivate "operator pause after Codex hook diagnosis"
```

Expected: exit 0 and one `DEACTIVATE` ledger row.

- [ ] **Step 3: Verify mode and markers**

```bash
echo "loop mode: $(loop_mode_active && echo ON || echo OFF)"
test ! -e .harness/.loop-active
test ! -e .harness/.loop-halt
test ! -e .harness/.loop-iter
tail -n 5 .harness/loop_status.md
```

Expected: `loop mode: OFF`, all three marker checks pass, and the named deactivation reason is visible.

- [ ] **Step 4: Verify Git remains unchanged by local cleanup**

```bash
git status --short
```

Expected: no tracked diff from this task. If the ledger or markers appear as tracked changes, stop before staging and diagnose ignore-policy drift.

---

### Task 6: Document the host boundary and operational verification

**Files:**

- Modify: `.codex/hooks/README.md`
- Modify: `.codex/notes/claude-codex-parity.md`
- Test: `tools/test_codex_workflow_parity.py`

- [ ] **Step 1: Add the exact contract map to the hook README**

Document these mappings without copying volatile source code:

| Event | Claude producer | Codex boundary | Codex behavior |
|---|---|---|---|
| `PreToolUse` bare safe allow | `permission-guard.sh` | adapter `permission-guard` | no opinion; supported `PermissionRequest` decides approval; an allow carrying `updatedInput` fail-closes to structured deny because the adapter cannot safely translate a Claude rewrite |
| `PreToolUse` hard deny | `permission-guard.sh` | adapter `permission-guard` | preserves deny and reason |
| `PostCompact` context | `postcompact-reinject.sh` | adapter `post-compact` | universal `systemMessage` only |
| compact model context | same producer | adapter `compact-context` called by SessionStart wrapper | appends context only for `source=compact` |

State that the shared producer tests are Claude contract tests and the installed-host witness is the Codex parser proof.

- [ ] **Step 2: Correct the parity note's trust statement**

In `.codex/notes/claude-codex-parity.md`, record that parity means equivalent effect, not byte-identical output schema. Name the real-host witness limitation and its new exception: all handlers remain recorder substitutes except the single real `PreToolUse` permission adapter.

- [ ] **Step 3: Add documentation assertions**

In `tools/test_codex_workflow_parity.py`, assert the README contains `PermissionRequest`, `compact-context`, and `equivalent effect`, and that the parity note names the real permission adapter witness.

- [ ] **Step 4: Run the documentation and parity tests**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest \
  tools/test_codex_workflow_parity.py -q
```

Expected: the complete workflow parity test file passes.

- [ ] **Step 5: Checkpoint the documentation unit without committing**

```bash
git diff --check
just codex-checkpoint hook-contract-docs-green
```

Expected: documentation and its assertions are present in the uncommitted implementation diff and named by a fresh checkpoint.

---

### Task 7: Run the final local validation matrix

**Files:**

- Verify: all owned files
- Update locally: `.harness/codex_loop_state.json` through gate records

- [ ] **Step 1: Run the shared Claude contract tests**

```bash
bash tools/hooks/test_permission_guard.sh
bash tools/hooks/test_postcompact_reinject.sh
```

Expected: both scripts report zero failures. These are the non-regression proof that the shared producers were preserved.

- [ ] **Step 2: Run the focused Codex parity suite**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache uv run pytest tools/test_codex_workflow_parity.py -q
```

Expected: all tests pass with no deselected failure hidden by a `-k` filter.

- [ ] **Step 3: Run the installed-host witness with loop mode forced in-process**

```bash
HARNESS_LOOP=1 UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-hook-runtime-witness
```

Expected: status `PASS`, both tool phase pairs, both file effects, and `real_handlers` naming the permission adapter; no parser diagnostic in stdout or stderr.

- [ ] **Step 4: Record implementation and narrow verification**

```bash
just codex-loop-record --phase implementation --status passed \
  --command "git diff --stat" \
  --evidence "Codex-only adapter and compact SessionStart routing implemented; shared Claude producers unchanged"
just codex-loop-record --phase narrow_verify --status passed \
  --command "shared hook tests; workflow parity pytest; installed Codex runtime witness" \
  --evidence "all acceptance rows green; real host emitted no parser failures"
```

Expected: both gates bind to the current branch, HEAD, and worktree fingerprint.

- [ ] **Step 5: Run the PR-ready provider-free gate**

```bash
UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-check
```

Expected: synchronization, lint, formatting, type checking, documentation/closure checks, parity, and all non-e2e tests pass.

- [ ] **Step 6: Record the local gate**

```bash
just codex-loop-record --phase local_gate --status passed \
  --command "UV_CACHE_DIR=/tmp/arhugula-uv-cache just codex-check" \
  --evidence "full provider-free PR-ready gate passed on final diff"
```

- [ ] **Step 7: Inspect the exact diff and absence of forbidden scope**

```bash
git diff --check
git diff --name-only
git diff --name-only main...HEAD
git status --short --branch
```

Expected: no whitespace errors; the uncommitted list contains only owned implementation files; the committed range contains only the reviewed plan artifact; no unrelated changes exist.

---

### Task 8: Obtain decorrelated review and close the implementation branch

**Files:**

- Modify only if a reviewer identifies a real defect: the smallest owned file set from the finding
- Modify during merge gate: `.harness/merge-gate-log.md`
- Do not modify: `.harness/roadmap_status.md`

- [ ] **Step 1: Run the grounding pass against actual diff content**

Re-read every file/line claim in the PR draft, recompute the registration count from `.codex/hooks.json`, verify the installed Codex version used by the witness, and confirm all recorded gates match the current worktree fingerprint.

- [ ] **Step 2: Run out-of-family review for Codex-authored work**

```bash
claude -p --model opus --output-format json --disable-slash-commands --tools "" \
  --safe-mode --strict-mcp-config --mcp-config '{"mcpServers":{}}'
```

Expected: a fresh authenticated Claude Code Opus 5 review returns exit 0, a successful JSON envelope with non-empty output, and final `VERDICT: APPROVE`. The prompt contains the final diff and acceptance contract but no Gemini findings. A malformed response, empty output, wrong model, or `BLOCK` is a failed gate.

- [ ] **Step 3: Reconcile review findings and replay affected checks**

For each finding, verify it against the actual diff. Fix only confirmed defects. After any change, rerun the focused test, `just codex-check`, the installed-host witness, and the out-of-family review on the delta.

- [ ] **Step 4: Record review and closeout gates**

```bash
just codex-loop-record --phase decorrelated_review --status passed \
  --command "claude -p --model opus --output-format json --disable-slash-commands --tools '' --safe-mode --strict-mcp-config" \
  --evidence "fresh Claude Code Opus 5 review returned a successful non-empty JSON envelope and VERDICT: APPROVE on final diff without Gemini findings"
just codex-closeout
just codex-loop-record --phase closeout --status passed \
  --command "just codex-closeout" \
  --evidence "fresh closeout checkpoint accepted on final diff"
```

Expected: no hard closeout finding. Report any warning in the PR body.

- [ ] **Step 5: Commit the complete reviewed implementation with explicit paths**

Stage the explicit owned implementation set; Git ignores unchanged paths:

```bash
git add .codex/hooks/codex_hook_adapter.py .codex/hooks.json \
  tools/hooks/codex-session-start.sh tools/test_codex_workflow_parity.py \
  tools/codex_hook_runtime_witness.py .codex/hooks/README.md \
  .codex/notes/claude-codex-parity.md
git diff --cached --check
git commit -m "fix: adapt shared hooks to Codex contracts"
```

Confirm `git diff --cached --name-only` contains only reviewer-confirmed owned changes; never use `git add -A`. If review required a delta, it is included in this same final implementation commit after its affected checks were replayed.

- [ ] **Step 6: Record the commit gate**

```bash
COMMIT_SHA=$(git rev-parse HEAD)
just codex-loop-record --phase commit --status passed \
  --command "git commit -m 'fix: adapt shared hooks to Codex contracts'" \
  --evidence "final reviewed implementation committed at ${COMMIT_SHA} after closeout"
```

Expected: `commit` follows `closeout`, and the recorded SHA is the current topic HEAD.

- [ ] **Step 7: Push, open the PR, and state tracking non-applicability**

Push `fix/codex-hook-contract-recovery` and open a PR whose body includes:

- the two original diagnostics;
- the acceptance matrix results and exact commands;
- the installed Codex version;
- the statement that `.harness/roadmap_status.md` is not changed in the implementation PR because this is an operational compatibility repair; the mandatory §12.2 one-file refresh still follows, and the current next action remains the operator-owned `B-124` ratification;
- the one-time ignored marker cleanup result;
- any skipped checks, with reason.

Record `push` and `pr_opened` through `just codex-loop-record` in required order; the `commit` gate was already recorded in Step 6.

- [ ] **Step 8: Require final-head CI and the three fresh merge lenses**

Wait until every required CI job on the final PR HEAD is terminal green. Then execute the `merge-gate` skill with three fresh Codex contexts for concurrency, spec conformance, and test witness. All must approve. Append and commit the resulting row to `.harness/merge-gate-log.md`, then wait for CI again on that new final HEAD.

- [ ] **Step 9: Merge and prove post-merge health**

Merge only with `--match-head-commit`, wait for the merge SHA's own `main` CI, and record `merged`. Then execute the mandatory §12.2 audit and land a terminating refresh PR whose only changed file is `.harness/roadmap_status.md`; record `post_merge_refresh` only after that refresh merge and its own `main` CI are green. The refresh must state that the compatibility repair changed no semantic roadmap-unit status and that the operator-owned `B-124` ratification remains next.

Sync local `main` to `origin/main`, record `main_synced`, emit the arc exit report while the worktree exists, dispose of the worktree and verified merged branch, record `worktree_disposition`, then run:

```bash
just codex-loop-check
```

Expected: the full loop check passes only after disposition.

- [ ] **Step 10: Preserve context and pause for HIL**

Run the gstack `context-save` skill after the merge fixed point. The saved context must name the implementation and refresh PRs, both merge SHAs and CI states, runtime-witness result, loop-marker cleanup result, the operator-owned `B-124` ratification as the unchanged next action, and the exact resume posture. Stop after presenting the result; do not select a `B-124` reading or start `B-147` until the operator reviews the completed repair.

### Claude Code Opus 5 review reconciliation

The operator replaced the planned Gemini artifact gate with fresh tool-less Claude Code Opus 5 reviews. Each review received the complete then-current diff, contract, and verification claims, but no Gemini or prior-Claude findings. Confirmed findings were closed with regression coverage: Codex permission responses are reconstructed from supported fields only; a bare `allow` emits no Codex opinion so `PermissionRequest` remains the sole approval boundary, while any future allow carrying `updatedInput` fail-closes to structured deny because the adapter cannot safely translate the Claude rewrite; producer failures and malformed permission decisions become the same structured deny already proven against the installed host; PostCompact producer failures return valid universal diagnostic JSON with exit 0; compact context prefers a valid event payload over an accompanying advisory; PostCompact and compact SessionStart have separate 20-second and 2-second producer budgets; every compact producer failure preserves the rest of SessionStart with an explicit recovery instruction; and the witness uses the exact production `/usr/bin/python3` commands. The strengthened witness records three real permission-adapter entries and one real PostCompact-adapter entry, drives a force-push deny whose pre-effect marker must stay absent, forces automatic compaction, requires the host's `PostCompact Completed` status without parser diagnostics, and proves safe Bash and apply_patch effects across five complete model exchanges. Claims about `HARNESS_LOOP=1` not enabling the real permission path and about the witness accepting a noncanonical adapter command were rejected against `loop_mode_active` and the exact-command guards.

---

## Rollback boundary

If the adapter causes a new Codex startup or permission regression before merge, discard only the uncommitted owned implementation diff and leave the reviewed plan commit plus shared Claude producers untouched. If a regression is discovered after merge, revert the single implementation commit in a focused PR. The safe emergency posture is to remove the incompatible Codex `PostCompact` registration and the Codex wildcard `PreToolUse` guard registration; Codex then falls back to its normal permission layer and compact `SessionStart` posture while hard-deny parity is temporarily unavailable. Record that degradation explicitly and restore the adapter only after the installed-host witness passes.

## Final go/no-go record

The repair is a **GO** only when all eight acceptance rows are green, the real installed Codex witness has recorded three executions of the actual permission adapter and one execution of the actual PostCompact adapter under `HARNESS_LOOP=1`, the host reports `PostCompact Completed`, the force-push deny marker is absent, both allowed tool effects exist, Claude producer tests remain unchanged and green, the three merge lenses approve final HEAD, CI is green on both PR HEAD and merge SHA, ignored legacy markers are absent, and context-save records a pause for HIL.

The repair is a **NO-GO** if any parser failure remains, safe approval depends on a bare Codex `PreToolUse allow`, any producer failure can fall through rather than returning a structured deny, a deny reason is lost, compact SessionStart lacks its session-scoped checkpoint pointer or recovery instruction, a shared Claude producer had to change, or the runtime witness still substitutes a recorder for either adapter it claims to validate.
