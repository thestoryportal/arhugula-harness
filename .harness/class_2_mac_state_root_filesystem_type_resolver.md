# Class 2 decision record — host filesystem-type reader for C-RT-36 state-root placement (macOS)

**Date.** 2026-11-14. **Posture.** Bundled-absorption arc (one `design-substrate/` row + the implementing `harness-runtime/src` change + tests), filed per root `CLAUDE.md` §4.3/§11.4.

## Operator direction (verbatim)

> Linux only is no longer a requirement. This build is now focused wholly on Mac OS deployment

## Defect

`Spec_Harness_Runtime_v1.md` §14.25 C-RT-36, row `fs-undetermined`, named `/proc/self/mountinfo` as the only source of the state root's filesystem type. `harness_runtime.config.state_placement.linux_filesystem_type` implemented exactly that, and was the default `filesystem_type` for `bootstrap_state_root` / `probe_state_root` / `revalidate_state_root` / `place_state_dir` and the explicit argument at `bootstrap/stage_1_is.py` and `lifecycle/root_resume_admission.py`.

Observed on macOS 26.6.2 arm64 with the installed candidate b6709c4d:

- declared `state_placement` → `RT-FAIL-BOOTSTRAP: bootstrap failed at stage IS (1): StateRootPlacementError: RT-FAIL-STATE-ROOT-PLACEMENT:fs-undetermined`
- no `state_placement` → the fresh run's pause-journal root `place_state_dir` hit the same reader → `FreshRunAdmissionError` (Rule B3), so no workflow body ran on macOS at all.

## Decision

Keep the seam (`filesystem_type: Callable[[Path], str | None]`) and the guarantees ("unknown is never durable"; `tmpfs`/`ramfs` refused). Add one more instance of the reader behavior and select the host's reader once, as a value:

- `darwin_filesystem_type(path)` — `statfs(2)` `f_fstypename` via `ctypes` (returns e.g. `apfs`, `devfs`; `None` on failure).
- `host_filesystem_type` — `linux_filesystem_type` on Linux, `darwin_filesystem_type` on macOS, an always-`None` reader elsewhere. It is the one default/argument everywhere the Linux reader was.

Spec row amended to name the per-platform mount-table reader; dated change-note added at the head of `Spec_Harness_Runtime_v1.md`. The versioned delta copies (`Spec_Harness_Runtime_v1_130.md` … `_139.md`) are history and keep their original row text.

Tests: `test_state_placement.py` gains darwin-guarded resolver tests and a host-selection test; tests that monkeypatched the resolver by name now patch `host_filesystem_type`.

## Not changed

Isolation tiers, forcing flags, provider holds, deferrals, every other C-RT-36 check and its order.
