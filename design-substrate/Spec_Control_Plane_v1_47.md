# Spec: Control Plane — v1.47 (delta over v1.46)

---

## Change-note (v1.46 → v1.47)

**Scope of revision.** One additive clause on a single **C-CP-08 §8.1** table cell — the `segment_replay` (`WAL-segment`) `resumption.kind` row gains the **"activity outputs cached and replayed"** capability the `event-sourced-replay` row already declares. This materializes the **§8.1 cached-output-replay refinement for `WAL_SEGMENT`**, the CP-side capability declaration paired with **runtime spec v1.65 → v1.66** (which extends the §14.23 C-RT-32 `EngineOutputStore` producer gate + resume-side rehydrate from `EVENT_SOURCED_REPLAY` to `WAL_SEGMENT`). R-FS-1 standalone `B-*` arc **`B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT`** (spine ledger).

**The amendment (§8.1 `segment_replay` row).** The v1.2 §8.1 "Per-engine-class resumption-kind enum" table row for `segment_replay` reads:

> | `segment_replay` | `WAL-segment` | Replay from WAL segments; per-segment dedup |

**Amended reading (v1.47):**

> | `segment_replay` | `WAL-segment` | Replay from WAL segments; per-segment dedup; **activity outputs cached and replayed** |

This brings the `WAL-segment` row to capability-parity with the `event-sourced-replay` row ("Prior steps replay from Event History deterministically; activity outputs cached and replayed; no re-execution of activities") **for the cached-output-replay clause specifically**. The two classes already share the `EngineOutputStore` substrate (runtime C-RT-32) and the same F2-prefix `resume_at` computation, so the refinement is the EVENT_SOURCED_REPLAY shape applied to the segment-replay class.

**Why additive / no operator gate.** The clause is a capability ADDITION (WAL_SEGMENT gains the cached-output replay EVENT_SOURCED_REPLAY already has); it SACRIFICES no committed invariant and changes no other §8.1 row, no fail-class, no contract, no enum. The runtime producer gate stays closed for non-replay engine classes (`SAVE_POINT_CHECKPOINT` / `PURE_PATTERN_NO_ENGINE` never write a never-rehydrated journal). The opt-out default (`engine_output_replay=False`) is byte-identical. FULL-SPEC-pre-authorized (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`).

**Sections preserved verbatim from v1.46.** All v1.2 §8.1 rows other than `segment_replay`, all of §7 / §8.2 / §8.3 / §25.x / §26.x, and every prior delta (v1.3 … v1.46) are PRESERVED VERBATIM. Per the delta-only convention, the canonical §8.1 reading is the v1.2 table as amended by this v1.47 `segment_replay`-row clause.

**Cross-references.**
- Runtime spec v1.65 → v1.66 (the §14.23.5 producer-gate extension + §14.23.7 `B-ENGINE-OUTPUT-REPLAY-WAL-SEGMENT` LANDED) co-lands with this CP delta in the same PR (bundled-absorption).
- Impl: `harness-cp/src/harness_cp/workflow_driver.py` — the producer gate (record) + the WAL_SEGMENT resume-block rehydrate, both extended from `EVENT_SOURCED_REPLAY` to `WAL_SEGMENT`.
- Clearance markers: `.harness/clearance/Spec_Control_Plane-v1_47-cleared-2026-06-21.md` + `.harness/clearance/Spec_Harness_Runtime-v1_66-cleared-2026-06-21.md`.

---

*End of v1.47 delta. Canonical CP spec = v1.2 base + deltas v1.3 … v1.47.*
