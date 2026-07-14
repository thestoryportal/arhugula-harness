# Class 1 Fork — CLI exit-code mapping never assigned a disposition to `RunResult.status == "paused"`; the CLI silently collapses it onto `failed`'s exit code

**Status:** PROPOSING

**Filed at:** 2026-07-14

**Filer:** roadmap-continue no-parking sweep (post-#996 session; B-27 grounding)

**Surfaced by:** Direct read of `harness-runtime/src/harness_runtime/cli/app.py` against `design-substrate/Spec_Harness_Runtime_v1.md` §14.18.2, cross-referenced against the runtime spec's own status/exit-code amendment history.

**Classification:** Class 1 (spec contract under-specifies a surface — §14.18.2's exit-code table was never amended when a later spec revision introduced a new non-terminal `RunResult.status` value).

---

## §1 — The gap

### §1.1 — `paused` is a real, non-terminal `RunResult.status` value

`RunResult.status` is a `Literal["completed", "drained", "failed", "paused", "partial"]` (`harness-runtime/src/harness_runtime/api.py:310`). The docstring at `api.py:313` is explicit that `'paused'` (cite: `C-RT-35, R-CC-1 arc #3`) is a **non-terminal** outcome — distinct in kind from `failed`/`drained` (terminal, non-resumable) and closer in kind to a graceful in-flight state: a workflow-layer `PauseSnapshot` is captured (`api.py:390`, `RunResult(status='paused', pause_snapshot=...)` at `api.py:726`) so the caller can persist it and later call `resume()`. `harness_cp.workflow_driver` confirms this at the CP layer: `CascadePolicy.PAUSE: RunStatus.PAUSED` (`workflow_driver.py:2021`) and multiple `status=RunStatus.PAUSED` returns tied to HITL-gate / cascade-pause flows (e.g. `workflow_driver.py:4243`, `4277`, `4323`, `4517`, `4582`).

### §1.2 — §14.18.2's exit-code table never names `paused`

`design-substrate/Spec_Harness_Runtime_v1.md` §14.18.2 (authored at v1.35, **PRESERVED VERBATIM through the current v1.99 HEAD** per the repeated "§14.18.x PRESERVED VERBATIM" change-note lines at v1.36/v1.38/v1.39) declares:

| Exit code | Meaning | Trigger |
|---|---|---|
| `0` | SUCCESS | `RunResult.status == SUCCESS` |
| `1` | WORKFLOW_FAILURE | `RunResult.status in {FAILED, PARTIAL, DRAINED}` (strict — PARTIAL maps to 1 unless operator override at iteration-2) |
| `2` | MANIFEST_ERROR | ... |
| `3` | CONFIG_ERROR | ... |
| `4` | RUNTIME_BOOTSTRAP_ERROR | ... |

`PAUSED` is absent from the `1` row's trigger set entirely — not included, not excluded, simply never named. This is not an oversight visible only in retrospect: the runtime spec's own §9 change-note (documenting the *later* addition of `'partial'` to the status `Literal`) says explicitly: *"ADD `'partial'` to the `status` `Literal` (type-widen — minor bump, **exactly mirroring v1.45's `'paused'`**)... exit-code stays `1` (the §14.18.2 mapping already lists `PARTIAL → 1`...)"*. In other words: when `'partial'` was added at a later spec revision, the author explicitly revisited and extended §14.18.2's row-1 trigger set to include `PARTIAL`. When `'paused'` was added at v1.45 (earlier in the same lineage, per the same change-note's own "mirroring v1.45's `'paused'`" framing), **no equivalent §14.18.2 amendment happened** — the row-1 trigger set was never extended to name `PAUSED` at all.

### §1.3 — Production code inherits the gap by falling through to the same exit code as `failed`

`harness-runtime/src/harness_runtime/cli/app.py:345-350` (one-shot mode):

```python
# --- Stage 6: emit RunResult + exit per §14.18.2 ----------------------
_emit_run_result(run_result, output=output)
if run_result.status == "completed":
    raise typer.Exit(code=EXIT_SUCCESS)
# status ∈ {"drained", "failed"} → exit 1
raise typer.Exit(code=EXIT_WORKFLOW_FAIL)
```

The trailing comment (`status ∈ {"drained", "failed"} → exit 1`) is itself stale — it doesn't even mention `partial`, which per §1.2 is spec-confirmed to also fall into this branch — but more importantly, `paused` ALSO falls through this `else` branch today (there is no distinct arm for it), landing on `EXIT_WORKFLOW_FAIL` (exit code `1`) exactly like a genuine `failed` run. The daemon-mode path (`app.py:223-229`, `_CP_STATUS_TO_EXIT_CODE`) shows the identical pattern: `"success"`, `"drained"`, `"failed"`, `"partial"`, `"pending"` are enumerated explicitly, `"paused"` is absent from the dict entirely and falls through to the `dict.get(status, EXIT_WORKFLOW_FAIL)` default at `app.py:305` — same collapse onto exit `1`.

### §1.4 — Why this is a real (not cosmetic) defect

A `paused` run is semantically closer to "still in progress, needs a follow-up `resume()` call" than to "this run failed and needs investigation." A CI pipeline, orchestration script, or operator shell wrapper invoking `harness run` and branching on exit code cannot currently distinguish "the workflow genuinely failed" from "the workflow paused for HITL/cascade-pause and is waiting to be resumed" — both surface as exit `1`. This is the same category of gap the runtime spec's own C-OD-05 HITL palette and CP's 4-response HITL discipline are designed to make legible; the CLI's exit-code surface currently erases that legibility at the outermost operator-facing boundary.

No CLI `resume` subcommand exists yet (`harness-runtime/src/harness_runtime/cli/app.py` only registers `run`, `daemon`, `inspect`, `shutdown` — grep-confirmed, zero `@app.command("resume")`), so today a paused run's exit code has no immediate practical consequence for a human operator invoking `harness run` interactively. The gap becomes load-bearing the moment (a) a CLI `resume` subcommand ships, or (b) any automation branches on `harness run`'s exit code to decide whether to retry vs. resume vs. alert.

---

## §2 — Proposed readings

**Q1 — What exit code (if any) should `RunResult.status == "paused"` produce?**

- **(A) New dedicated exit code `5` (`PAUSED_RESUMABLE`)** — extends the existing 0–4 enumeration by one. Cleanly distinguishes "needs `resume()`" from "needs investigation" at the shell-script level. Requires a §14.18.2 table amendment (new row) + a `EXIT_PAUSED = 5` constant + explicit dict entries at both call sites. **RECOMMENDED** — the closed, small, purpose-built exit-code enumeration this spec chose (Q-G=(a) "strict") is exactly the kind of surface where a new *distinct* semantic (non-terminal-but-non-success) deserves its own code rather than reusing an existing one.
- **(B) Reuse exit code `0` (SUCCESS)** — treat "paused, cleanly captured, awaiting resume" as a successful outcome of *this* invocation (the process did what it was supposed to do: stop cleanly and persist state). Mirrors how some tools treat "no error, but more work remains" as exit 0 with output signaling the remaining work. Risk: silently conflates "genuinely done" with "not done yet, paused" for naive callers that only check `$?`.
- **(C) Reuse exit code `1` (WORKFLOW_FAILURE), but document it explicitly** — accept the current de facto behavior as canonical; amend §14.18.2's row-1 trigger set to explicitly list `PAUSED` alongside `FAILED, PARTIAL, DRAINED` (closing the spec-vs-code drift without changing behavior). Minimal blast radius; but does not resolve the operator-legibility gap from §1.4 — a paused-for-HITL run is still indistinguishable from a hard failure by exit code alone (the `--output json` payload's `status` field remains the only way to discriminate, which requires the caller to parse output rather than branch on `$?`).
- **(D) Defer entirely — no exit-code amendment now** — rationale: `paused` genuinely cannot arise from `harness run`'s one-shot code path today unless a HITL gate or cascade-pause policy fires, and no `resume` CLI subcommand exists to act on it yet. Document the drift as a known, intentionally-deferred gap (Class 3-adjacent) until a `resume` subcommand ships, at which point the exit-code semantics matter in practice. Foreclosed candidate if the operator wants the drift closed now rather than carried.

**Q2 — Scope of the amendment, if Q1 ≠ D.**

- (i) CLI-layer only — amend `app.py`'s two call sites (`_CP_STATUS_TO_EXIT_CODE` dict + the one-shot `if/else`) + the stale trailing comment at `app.py:349`. No spec change if Q1=C is read as "already implicitly covered by the `else` fallthrough" — but Q1=C as proposed above explicitly recommends a spec-table amendment for documentation accuracy even if behavior is unchanged.
- (ii) Spec + CLI — amend §14.18.2's table (new row for Q1=A, or extend the row-1 trigger set for Q1=C) AND the two `app.py` call sites, keeping spec and code in sync (mirrors how `PARTIAL`'s addition was handled — spec amended, then code cited as already-conformant). **RECOMMENDED** regardless of which Q1 reading is chosen, since the whole point of this fork is that a prior instance of exactly this drift-without-spec-amendment is what created the gap.

**Q3 — Does a future `resume` CLI subcommand need co-design here, or is it fully out of scope?**

- (a) Out of scope — this fork only closes the *existing* `run` command's exit-code gap; a `resume` subcommand is a separate, larger surface (needs its own manifest/socket/ledger-reload design) and should be its own future arc, not bundled here.
- (b) In scope — since `PAUSED_RESUMABLE`'s value (per Q1=A) is only meaningful in the context of "and now what," at minimum note in the fork's resolution that a follow-on `resume` subcommand should honor the same exit-code convention once it exists. **RECOMMENDED** as a documentation note only, not an implementation obligation of this fork.

**Q4 — Cross-axis cascade.**

Per the same reasoning as the sibling fork `class_1_fork_topology_admissibility_check_load_time_vs_runtime_asymmetry.md` (§14.18.x is intra-runtime-axis, zero cross-axis touch for CLI-only amendments): this fork's resolution touches only `design-substrate/Spec_Harness_Runtime_v1.md` §14.18.2 (if Q2=ii) + `harness-runtime/src/harness_runtime/cli/app.py`. `RunResult.status` itself (the `Literal` enum) is unchanged by any reading here — only the exit-code *mapping* changes. No CP / AS / OD / IS / CXA / ADR / ADD / PRD touch under any reading.

- (α) Q1=A or C, Q2=ii → runtime spec v1.99 → v1.100 (§14.18.2 amendment) + `harness-runtime/src/harness_runtime/cli/app.py`. ZERO cross-axis cascade.
- (β) Q1=B or D → no spec amendment; at most a code comment / doc-hygiene note. ZERO cross-axis cascade.

---

## §3 — Filing footer

| Field | Value |
|---|---|
| Artifact | `class_1_fork_cli_exit_code_paused_status_undefined.md` |
| Status | PROPOSING |
| Filed at | 2026-07-14 |
| Authority anchors | `design-substrate/Spec_Harness_Runtime_v1.md` §14.18.2 (exit-code mapping table, authored v1.35, preserved verbatim through v1.99); §9 change-note documenting `PARTIAL`'s addition + explicit "mirroring v1.45's `paused`" framing (v1.6x-era delta; exact version not re-derived here — the change-note text is quoted verbatim above and is self-dating via its own "mirroring v1.45" cite) |
| Empirical anchors | `harness-runtime/src/harness_runtime/api.py:310,313,390,726,958,963,965,1136-1138` (`RunResult.status` Literal + `paused` semantics + `PauseSnapshot`); `harness-runtime/src/harness_runtime/cli/app.py:47-51,221-229,345-350` (exit-code constants + both mapping call sites); `harness-cp/src/harness_cp/workflow_driver.py:2021,4243,4277,4323,4517,4582` (`RunStatus.PAUSED` production returns, confirming `paused` is a live, reachable status, not dead code) |
| Zero production callers claim | NOT applicable here (unlike B-24/B-25) — `RunStatus.PAUSED` has multiple confirmed production return sites in `workflow_driver.py`; the gap is reachable today whenever a HITL gate or cascade-pause policy fires during a one-shot `harness run` invocation |
| Resolution path | Per workspace `CLAUDE.md` §4.3 Class 1 → route to Phase 5 spec revision-pass (runtime spec §14.18.2) if Q2=ii, else CLI-only doc/code fix. Apply arc lands at follow-on PR with clearance marker per `CLAUDE.md` §4.5 if the spec is amended |
| Cross-axis cascade | Per Q4: ZERO under every reading — intra-runtime-axis only |
| Registered at | `.harness/forward-register.yaml` id `B-27` / `.harness/post-phase-8-forward-register.md` §"B-27" |
