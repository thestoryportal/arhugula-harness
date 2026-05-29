# Class 1 Fork Record — `harness` CLI parent app missing `inspect` + `shutdown` subcommands

**Filed:** 2026-05-29 (probe v3 — operator-facing `harness-inspect` probe surfaced finding #2).
**Class:** 1 (spec/impl divergence at design-substrate cite vs production code; operator owns spec-narrow-vs-impl-extension routing).
**Status:** ✅ APPLIED-AS-READING-A 2026-05-29. Operator-routed apply-arc at PR #84 closure. Two thin pass-through subcommand registrations at `harness-runtime/src/harness_runtime/cli/app.py` delegate to the admin modules' existing `main(argv)` entrypoints via `ctx.args` forwarding; `context_settings={"ignore_unknown_options": True, "allow_extra_args": True, "help_option_names": []}` lets `--help` flow through to argparse (revealing the actual flag inventory). Admin modules at `harness_runtime/admin/inspect.py` + `admin/shutdown_cli.py` PRESERVED VERBATIM — no signature change; argparse-only discipline per spec §13 footer maintained. Standalone `harness-inspect` + `harness-shutdown` binaries at `[project.scripts]` ALSO PRESERVED (operator muscle memory). +1 NEW test extending AC #1 (`test_harness_top_help_lists_all_four_subcommands`) + 3 NEW tests (`test_harness_inspect_help_delegates_to_admin_argparse` + `test_harness_shutdown_help_delegates_to_admin_argparse` + `test_harness_inspect_runs_admin_body_against_real_ledger`). 1308/1308 harness-runtime tests pass + 10 skipped (was 1306 at PR #83 close; +2 net from +4 NEW minus AC #1 rename). Probe v3 re-run post-Reading-A: `harness --help` lists all 4 subcommands; `harness inspect --ledger-path ...` works end-to-end against probe-v2 ledger; `harness inspect --help` shows argparse flag inventory verbatim. ZERO spec amendment (§13.4 + §14.18.1 preserved verbatim; impl converges to spec); ZERO cross-axis cascade.

**Reading B (spec narrowing) NOT applied** — preserved as carry-residual at §3 for future operator routing if 5-subcommand parent dispatcher proves operationally unnecessary. Reading A is the more conservative apply: closes spec/impl gap by extending impl rather than narrowing spec. Internal spec contradiction at §13.4 row 378 ("MAY become subcommands at iteration-2" vs "5-subcommand parent namespace") remains as doc-drift — recommend spec-side doc-hygiene refresh at next workflow-doc revision pass to strike the "iteration-2" tail clause now that the apply landed at iteration-1.
**Surfaced by:** `[[use-the-product-probe]]` cardinality 3 — invoked `harness --help` after PR #82 sync; observed only 2 subcommands (`run` + `daemon`); spec §13.4 + §14.18.1 declare 5 subcommands at parent app.
**Surfacing PR:** probe-v3 worktree this session (no production change yet).
**Anchors:** runtime spec v1.39 §13.4 (`§366`) + §14.18.1 (`§227-235`) + §14.18 cite at `§205+207`; impl at `harness-runtime/src/harness_runtime/cli/app.py:252+488` (only 2 `@app.command` registrations); standalone binaries at `[project.scripts]` `harness-inspect = "harness_runtime.admin.inspect:main"` + `harness-shutdown = "harness_runtime.admin.shutdown_cli:main"`.

---

## 1. The defect

Spec §13.4 line 372-378 declares:

> **5-subcommand registration table** (Track A admin: `harness-inspect`, `harness-shutdown`; Track B operator: `harness run`, `harness daemon`, `harness inspect`, `harness shutdown`)
> **Subcommand structure invariant (Q-J=(a) flat).** All 5 subcommands compose under flat `harness <subcommand>` namespace.

Spec §14.18.1 table at §227-235 enumerates 5 subcommands at the `harness` parent app:
- `harness run <workflow-file>` ✅ landed at `cli/app.py:252`
- `harness run <workflow-file> --daemon` ✅ landed at same
- `harness daemon` ✅ landed at `cli/app.py:488`
- `harness inspect` ❌ NOT registered at parent app
- `harness shutdown` ❌ NOT registered at parent app

Empirical confirmation at HEAD `e216cc0`:

```
$ uv run harness --help
Commands:
  run     Invoke a workflow (one-shot, or daemon-client when --daemon is set).
  daemon  Start the harness daemon (FastMCP server, Unix-socket transport).

$ uv run harness inspect --help
Error: No such command 'inspect'.
RT-FAIL-CLI-ARG-INVALID
```

Standalone binaries `harness-inspect` + `harness-shutdown` ARE registered at `[project.scripts]` and DO work via `uv run harness-inspect`. Only the parent-app subcommand surface is missing.

---

## 2. Root cause

`cli/app.py` registers exactly two `@app.command(...)` decorators (`run` at :252 + `daemon` at :488). The 2 Track A admin stubs (`harness-inspect` + `harness-shutdown`) live at `harness_runtime/admin/inspect.py` + `admin/shutdown_cli.py` with their own `main()` entrypoints, registered at `harness-runtime/pyproject.toml [project.scripts]` as standalone hyphenated binaries.

Spec §14.18.1 table row 4 + 5 reads:
> `harness inspect` | (Existing Track A admin stub — PRESERVED VERBATIM per `harness-inspect` registration)

The "PRESERVED VERBATIM per `harness-inspect` registration" wording is the source of ambiguity that may have led to the impl gap. Two readings:

- **Reading (i):** `harness inspect` subcommand at parent app delegates to the same handler as `harness-inspect` standalone (operator can invoke either way). The standalone binary IS preserved verbatim; the parent-app subcommand is the NEW registration.
- **Reading (ii):** `harness inspect` is NOT a NEW subcommand at parent app; the existing standalone binary `harness-inspect` IS the entirety of the registration; the spec row just acknowledges that the surface exists.

§13.4 line 378 disambiguates toward Reading (i): "**All 5 subcommands compose under flat `harness <subcommand>` namespace**". 5 means 5 — including inspect + shutdown.

§13.4 row 378 tail clause adds: "they MAY become subcommands of `harness` at iteration-2 (preserves operator muscle memory)" — this reads toward Reading (ii) at iteration-1.

**Internal spec contradiction.** §13.4 row 378 declares "5-subcommand parent namespace" AND "MAY become subcommands at iteration-2". Cannot be both at v1.

---

## 3. The two valid fixes

### Reading A — Impl extension (register inspect + shutdown at parent app)

Add 2 `@app.command(...)` registrations at `cli/app.py` delegating to the existing standalone `main()` functions:

```python
from harness_runtime.admin import inspect as _inspect_admin
from harness_runtime.admin import shutdown_cli as _shutdown_admin


@app.command("inspect")
def inspect(
    ledger_path: Path = typer.Option(...),
    collector_path: Path | None = typer.Option(None),
    last_n: int = typer.Option(10),
    json_output: bool = typer.Option(False, "--json"),
) -> None:
    """Read-only summary of state ledger + collector traces."""
    _inspect_admin.main_with_args(
        ledger_path=ledger_path,
        collector_path=collector_path,
        last_n=last_n,
        json=json_output,
    )


@app.command("shutdown")
def shutdown(
    pidfile: Path = typer.Option(...),
) -> None:
    """Signal a running harness instance to shut down gracefully."""
    _shutdown_admin.main_with_args(pidfile=pidfile)
```

Requires `main_with_args(...)` wrapper at the 2 admin modules if they currently take `argv` from `sys.argv` only.

**Pros:**
- Closes spec/impl gap at §14.18.1 5-subcommand table verbatim.
- Operator gets both `harness inspect` AND `harness-inspect` (muscle memory + parent-app discoverability).
- `harness --help` correctly enumerates the operator surface.

**Cons:**
- Couples cli/app.py to admin modules (currently independent).
- 2 NEW `main_with_args(...)` wrappers needed at the admin modules; or refactor existing `main()` to take args.
- ~50 LOC + 2-4 NEW tests covering parent-app subcommand registration + delegation.

### Reading B — Spec narrowing (declare 2-subcommand parent + 2 standalone-only)

Amend spec §13.4 + §14.18.1 to declare:
- Parent `harness` app: 2 subcommands at v1 (`run`, `daemon`)
- Track A admin: 2 standalone binaries (`harness-inspect`, `harness-shutdown`); NOT registered at parent app at v1
- iteration-2 (deferred): MAY register `inspect` + `shutdown` at parent app

§13.4 row 378 "5-subcommand parent namespace" → "2-subcommand parent namespace + 2 admin standalone binaries"
§14.18.1 table rows 4 + 5 STRUCK
§13.4 row 378 "MAY become subcommands of `harness` at iteration-2" PRESERVED

**Pros:**
- Spec catches up to impl (current state).
- Honest about the operator surface gap.
- Resolves internal spec contradiction toward Reading (ii).
- No production code change; pure spec narrowing.
- Spec v1.39 → v1.40 single-focus amendment.

**Cons:**
- Operator surface stays narrower (less discoverable; `harness --help` doesn't list inspect/shutdown).
- Defers convergence to iteration-2.
- The §14.18.1 5-subcommand table is one of the more empirically-tested parts of the runtime spec; narrowing it sets precedent for "spec catches up to impl" rather than "impl catches up to spec".

---

## 4. Why this is Class 1

Spec §13.4 + §14.18.1 declare a contract that production code does not implement. Per workspace `CLAUDE.md` §4.3 Class 1 routing: "Architectural defect; design-phase artifact requires revision" — applies whether the resolution is (A) impl extension to match spec or (B) spec narrowing to match impl. Operator owns which direction the convergence goes.

Both readings preserve wire-level invariants (existing `harness-inspect` + `harness-shutdown` standalone surfaces remain operational at both readings). Operator-facing CLI surface differs: Reading A widens parent-app `--help` to 5 commands; Reading B narrows spec to 2 + 2.

---

## 5. Probe v3 framing

This finding sharpens `[[use-the-product-probe]]` at cardinality 3:
- PR #79 §4(e) cardinality 1: probe of YAML workflow loading surfaced 17 findings
- PR #83 cardinality 2: probe of U-CP-74 production firing site surfaced actor field malformation
- This finding cardinality 3: probe of `harness inspect` parent-app subcommand surfaced spec/impl divergence

Pattern continues to validate: file end-to-end CLI probes BEFORE continuing pure-code closure arcs; the probe surfaces defects that tests + spec-grep miss.

---

## 6. Adjacent observations (not patched per FM-2)

(a) **`uv sync --all-packages` required after every `git pull` that adds deps.** Main worktree's `.venv` was at pre-PR-#82 state (missing `pyyaml`); `harness --help` failed with `ModuleNotFoundError: No module named 'yaml'`. Standard uv-workspace pattern; documentation candidate at `harness run minimal config recipe` memory or `justfile`. NOT a defect; UX friction.

(b) **`harness-inspect --collector-path` accepted-but-unused.** Pre-existing per `[[fork-trace-storage-pathclass-gap]]` (U-RT-30 PARTIAL-LAND); `harness-inspect` emits "in-memory collector storage at HEAD; on-disk sqlite path resolution STRUCK" explicitly. Honest reporting; not a defect at this surface.

(c) **`audit:_single:<hash>` action_id not in CXA v2.9 §0.3 8-prefix table.** The middle entry of probe-v2 ledger carries `action_id=audit:_single:56ba1cf7…`. Canonical 8-prefix table at CXA §0.3 lists `dispatch:` / `hitl:` / `hitl_webhook:` / `operator_burden:` / `validator:` / `pause:` / `resume:` / `mcp_trust:` / `cost:`. `audit:_single:` is a 10th prefix not in the canonical table. Possibly drift; routes to separate fork investigation arc.

(d) **Cost rollup N/A at `harness-inspect`.** Pre-existing per spec §10 step 2 over-specification; documented at `class_3_drift_u_rt_45_cost_chain_stateless.md`. Honest reporting; not a defect at this surface.

---

## 7. Disposition pending

| Disposition | Trigger |
|---|---|
| ✅ APPLIED-AS-READING-A | Operator selects Reading A; impl extension at `cli/app.py` registering 2 NEW subcommands delegating to admin standalone `main()` functions; ~50 LOC + 2-4 NEW tests; ship as apply-PR; close this fork doc |
| ✅ APPLIED-AS-READING-B | Operator selects Reading B; spec v1.39 → v1.40 §13.4 + §14.18.1 amendment narrowing 5-subcommand → 2-subcommand parent + 2 standalone; X-AL-3 CI guard satisfied via this fork doc + clearance marker `.harness/clearance/Spec_Harness_Runtime-v1_40-cleared-2026-05-29.md`; ship as apply-PR; close this fork doc |
| 🟡 DEFERRED | Operator routes to later session; carry as bounded-residual; document at workspace `CLAUDE.md` §2.3 runtime spec row or future arc |

Operator AskUserQuestion at apply-arc opening — recommend Reading A (closes operator-discoverability gap; preserves spec §14.18.1 verbatim; smaller blast radius than spec amendment).

---

*Filed at probe-v3 closure 2026-05-29. Sibling-class pattern to `class_2_fork_u_cp_74_actor_field_malformation.md` (CLI-discovery-via-probe surfaces spec/impl divergence; operator-decided convergence direction).*
