# Class 1 Tension — U-RT-44 in-flight step drain unmaterializable until CP workflow loop lands

**Status:** OPEN
**Filed:** 2026-05-20 (Phase 2 Session 7, U-RT-44 landing)
**Trigger unit:** U-RT-44 (`design-substrate/Spec_Harness_Runtime_v1.md` §11 C-RT-11)
**Pattern:** `[[halt-route-split-AC-pattern]]`
**Routing target:** runtime spec C-RT-11 + CP-axis workflow loop primitive (not yet specified)

---

## Surface

`Spec_Harness_Runtime_v1.md` §11 C-RT-11 commits 3 drain surfaces:

1. ✅ `HarnessContext.drained_flag` set by signal handler — runtime-owned, landed at U-RT-44.
2. ❌ **CP workflow lifecycle loop polls `ctx.drained_flag.is_set()` at each lifecycle boundary** (per-step entry, per-step exit, per-topology-dispatch entry); on flag-set, completes current step, emits event, returns `RunResult(status='drained')`.
3. ✅ `harness_runtime.run()` rejects new invocations with `HarnessDraining` — runtime-owned, landed at U-RT-44.

Surface (2) is the materialization site for U-RT-44 AC #2: "an in-flight step completes within bounded wait OR surfaces typed timeout."

## Defect

**There is no CP workflow lifecycle loop landed in the runtime body.** `harness_runtime.api.run()` raises `WorkflowExecutionNotYetLandedError` post-bootstrap. Bootstrap completes; execution body is the next-unit horizon. No in-flight step exists to drain.

The spec acknowledges this asymmetry in §11 risk surface:

> If CP later surfaces a native drain primitive (e.g., a CP-level `WorkflowDrainController` type), refactor `harness-runtime/` to delegate drain to CP. This contract becomes a thin adapter. Until then, drain ownership is runtime-axis-local.

But the spec's "runtime-axis-local drain" presumes a runtime-owned workflow loop polls the flag. No such loop exists in the runtime body — and the session-3 atomic decomposition assigns workflow-loop execution to CP-axis composition, not the runtime axis.

## U-RT-44 partial-land

- AC #1 (SIGTERM sets flag) — LAND.
- AC #3 (no new ingress post-drain) — LAND.
- **AC #2 (in-flight step drain) — STRUCK** pending fork resolution.

## Resolution paths

### Path A — Wait for CP workflow loop unit; refactor U-RT-44 at that point [RECOMMENDED]

When the CP workflow loop primitive lands (likely U-RT-49+ E2E surface or a CP-axis follow-up), refactor U-RT-44 to:

- Add `_should_drain(ctx)` polling hook called at lifecycle boundaries by the CP loop.
- Add bounded-wait timeout primitive (composable with `shutdown(ctx, timeout=...)` per C-RT-10).
- Add `RunResult(status='drained')` return path from the CP loop on flag detection.

**Pros:** matches spec §11 risk surface's explicit guidance ("until then, drain ownership is runtime-axis-local" — but in practice no runtime-axis loop exists yet); smallest blast radius; respects axis boundaries; AC #2 lands at the natural materialization site.

**Cons:** AC #2 lives in carry-forward state until the loop unit lands. Carry-forward tracked at `[[carried-fork-audit-before-cluster]]`.

### Path B — Land runtime-side workflow loop scaffolding now [REJECTED]

Add a thin polling loop in `harness_runtime/` that wraps a `WorkflowObject.execute_step()` callable (currently undefined) and polls `drained_flag` between steps.

**Pros:** AC #2 lands now.

**Cons:** scope creep (not in U-RT-44 atomic decomposition); commits to a workflow-step contract that should be a CP-axis decision; risks anti-leakage violation (X-AL-3 silent H_T design extension at Phase 7 execution time).

### Path C — Re-spec C-RT-11 to drop AC #2 from runtime axis entirely [REJECTED]

Move AC #2 commitments to the CP-axis spec (`Spec_Control_Plane_v1_3.md`).

**Pros:** clean axis boundaries.

**Cons:** spec architectural call — Phase 7 execution should not unilaterally restructure axis ownership. If the operator wants this, route through design-substrate revision.

## Operator decision

**Path A recommended.** Sign-off via in-session AskUserQuestion at U-RT-44 land time.

## Carry-forward state

- AC #2 added to `[[phase-7-remaining-workflow]]` under "Open carry-forwards".
- `[[carried-fork-audit-before-cluster]]` discipline applies before L11 (E2E + Pattern P1) opens.
- Refactor target unit: most likely U-RT-49 (E2E happy-path) or a follow-up CP-axis unit that lands the workflow lifecycle loop.

## Provenance

- Spec source: `design-substrate/Spec_Harness_Runtime_v1.md` v1.1 §11 C-RT-11 lines 618–642
- Decomposition source: `.harness/phase-2-session-3-track-a-atomic-decomposition.md` L10 U-RT-44 block
- Predecessor session checkpoint: `~/.gstack/projects/arhugula-v2/checkpoints/20260520-011553-l9-opens-u-rt-43-bootstrap-orchestrator-landed.md`
