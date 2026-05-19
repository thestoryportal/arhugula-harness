# Phase 2 — Class 1 Fork F-P2-1: Composition-Root Package Placement

**Status:** ✅ **RESOLVED 2026-05-19** — operator ratification.
**Source:** Phase 2 Session 2 Track A strawman, `phase-2-session-2-track-a-strawman.md` §6.
**Type:** Operator design call (not a spec-surface defect).

---

## Defect

The Track A runtime strawman names a composition root — the wiring + lifecycle +
entrypoint layer above the existing 6 axis packages — but the corpus does not specify
where it lives. The `class_1_tension_runtime_entrypoint_design_gap.md` (RESOLVED →
Phase 2) named a new package as a *candidate* but did not decide.

## Options surfaced

1. **New `harness-runtime/` package** — clean separation; mirrors axis-package shape;
   natural home for Track B's DevEx-plane code; ~30 lines of pyproject + scaffolding.
2. **Co-locate in `harness-cxa/`** — no new package; but conflates seam instantiation
   (CXA's intent) with composition-root concerns; CXA likely stays sparse anyway given
   the 22 genuine typed seams already live distributed across axis packages.
3. **Hybrid — seams in `harness-cxa/`, runtime in new package** — cleanest separation,
   but risks two thin packages given the distributed-seam reality.

## Resolution

**Option 1 — new `harness-runtime/` package.**

Operator-ratified rationale:
- The composition root has distinct concerns from CXA seam instantiation (lifecycle,
  provider clients, CLI, agent-loop dispatch vs. byte-exact cross-axis type wiring).
- Track B's DevEx agentic plane will land substantial new code — it needs a home that
  semantically fits ("the operating brain") and a runtime package provides one.
- `harness-cxa/` stays sparse-or-distributed by design; co-locating muddies its intent
  without giving it real load.
- Adding a uv workspace member is mechanical and is the established workspace pattern.

## What this resolves

| Question | Resolved |
|---|---|
| Where does the composition root live? | `harness-runtime/` |
| Where does the CLI entrypoint live? | `harness-runtime/src/harness_runtime/__main__.py` + `[project.scripts]` entry in root `pyproject.toml` |
| Where do bootstrap stages 1–5 (per strawman §3) live? | `harness-runtime/src/harness_runtime/` |
| Where does Track B's DevEx-plane code land? | `harness-runtime/` (specific module structure TBD by Track B) |
| What happens to `harness-cxa/`? | Stays per CXA v2.3 — seam instantiation lives distributed across axis packages; CXA package retained for any future centralized cross-axis utilities |

## What this does NOT resolve

- The package itself is not scaffolded yet. Scaffolding (`pyproject.toml`, `src/harness_runtime/__init__.py`, uv workspace member entry, root `[project.scripts]`) is implementation work for Session 3+ once atomic-decomposition begins.
- F-P2-2 through F-P2-5 (spec-surface gaps) remain open. Resolving F-P2-1 unblocks only one dimension of Session 3.

## Filing footer

| Field | Value |
|---|---|
| Artifact | `phase_2_fork_F-P2-1_runtime_package_placement.md` |
| Authority | Operator ratification at Phase 2 Session 2 close, 2026-05-19 |
| Predecessor | `phase-2-session-2-track-a-strawman.md` §6 (fork surfaced) |
| Successor | Session 3 atomic-decomposition (package scaffolding lands as the first units); also unblocks F-P2-3/F-P2-4/F-P2-5 spec-fix discipline (they can now name `harness-runtime` as the configuration site / owning module) |
