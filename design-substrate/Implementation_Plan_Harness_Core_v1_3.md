# Implementation Plan — Harness Core v1.3

**Status:** Proposed (delta over v1.2)

*Delta-only plan file. v1.2 + v1.1 bodies (U-CORE-01 + U-CORE-02 + the R2–R5 per-axis passes) PRESERVED VERBATIM in their own files. v1.3 is the Core plan leg of the RATIFIED **B-48 apply arc** (`.harness/class_2_fork_b48_sync_subagent_dispatch_offload.md`, option B AS RECOMMENDED 2026-07-18; C1⊥C9 dyad 16/16 CONFIRM): it authors ONE NEW unit — **U-CORE-03**, the shared typed capacity-exhausted error class — per the v1.2 §0.5 discipline that authoring a shared Core class alongside a RuntimeConfig extension is a coherent change requiring its own U-CORE unit (apply-PR codex round 7). Unit count 2 → 3.*

## §0 Change note (v1.2 → v1.3)

The B-48 executor arc (Runtime spec v1.102 §14.8.10 + CP spec v1.102 §25.11 + plans Runtime v2.50 / CP v2.39) needs ONE shared exception type consumed across the package boundary: the CP fan-out admission raises it through the CP-declared capacity-authority Protocol, and the runtime dispatch sites raise it at the §14.8.10 executor's own fail-fast — per the workspace carrier-home discipline (a cross-axis type in one axis package is the Class-1 cycle hazard), it homes in `harness-core`, which both `harness-cp` and `harness-runtime` already depend on.

## §1 NEW U-CORE-03 — shared typed capacity-exhausted error

**Implements:** the canonical typed raise of Runtime spec v1.102 §14.8.10.5 (the fail-class row maps to this type) + the CP-declared capacity-authority Protocol's raise contract (CP plan v2.39; CP spec v1.102 §1).

**Depends on:** [U-CORE-01 (the package skeleton/carrier conventions)].

**Consumed by (cross-package, declared here for the DAG):** Runtime plan v2.50 U-RT-140 (taxonomy row mapping) + U-RT-141 (the executor + capacity-authority adapter raise it) + CP plan v2.39 U-CP-101 (the Protocol declaration raises it); U-CP-85/86/88 consume it ONLY through U-CP-101 (no direct edge — codex round-34).

**Acceptance criteria:**

1. ONE exception class in `harness_core` (name implementation-discretion, non-binding suggestion `SubAgentDispatchCapacityError`), carrying: the requested frame count, the available capacity at rejection, the overflowing dispatch **step id**, and the **descent chain** (the C1 typed step-attributable condition from the dyad) — all constructor-supplied by the raising site; the class itself performs no capacity logic (a carrier, not an authority).
2. Frozen/slotted per the existing `harness_core` carrier conventions; no imports beyond stdlib/pydantic (leaf-safe — importable by every package without cycles).
3. RESERVATION-LEASE context (apply-PR codex round 7, mirrored from the CP/Runtime plans): the error is raised at ADMISSION time only — it never fires for an already-admitted job; lease lifecycle (held to actual job termination or fence-drain acknowledgement, exactly-once release) is executor-owned (U-RT-141), not error-owned.

**Tests (PD-8 mutation-probed):** `test_capacity_error_carries_step_and_descent` (constructor round-trip: step id + descent chain + counts surface on the raised instance — mutation probe: dropping a field fails); `test_capacity_error_importable_from_cp_and_runtime_without_cycle` (both packages import the class; the package graph stays acyclic — mutation probe: relocating the class into `harness_runtime` makes the CP import fail).

## §2 Coverage + DAG delta

| Surface | Unit |
|---|---|
| The shared capacity error class (Runtime v1.102 §14.8.10.5 canonical type; CP v1.102 §1 Protocol raise) | U-CORE-03 (NEW) |

DAG: U-CORE-03 ← U-CORE-01. Cross-package consumers (declared, Kahn-relevant, reconciled at codex round-34 — the CP consumers reach the error THROUGH the U-CP-101 Protocol, not by direct dependency): U-RT-140, U-RT-141, and U-CP-101 ← U-CORE-03; U-CP-85/86/88 ← U-CP-101 only (the CP plan's authoritative shape — both graphs identical). Acyclic — U-CORE-03 has no outbound edge beyond U-CORE-01.

*End of Implementation Plan — Harness Core v1.3. Three units (U-CORE-01 + U-CORE-02 + U-CORE-03). Clearance marker at `.harness/clearance/implementation-plan-harness-core-v1-3-cleared-2026-07-19.md`.*
