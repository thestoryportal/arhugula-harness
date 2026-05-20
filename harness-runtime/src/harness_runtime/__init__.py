"""`harness-runtime` — H_T composition root.

Per `CLAUDE.md` §3.3 and `design-substrate/Spec_Harness_Runtime_v1.md` v1.1,
this package owns runtime composition of the axis libraries:

- Bootstrap orchestration (9 stages per C-RT-01).
- Provider SDK lifecycle (F-P2-4; C-RT-05).
- TracerProvider lifecycle (F-P2-3; C-RT-06).
- In-process OTLP collector daemon supervision (F-P2-5; C-RT-07).
- Cross-axis seam wiring (C-RT-12; 24 phase-2-runtime edges).
- `run()` Python API (F-P2-2; C-RT-08).

Public API surface lands at L9 (U-RT-42). At L0 this module is intentionally
empty; the types are surfaced via `harness_runtime.types` until U-RT-42 lands
the `run()` entry point.
"""

from __future__ import annotations
