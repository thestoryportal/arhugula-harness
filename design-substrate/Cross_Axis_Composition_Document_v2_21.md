# Cross-Axis Composition Document (v2.21)

*Delta over v2.20. v2.21 is an **additive forward-capability registration** (no contract change to any plan-canonical edge, no edge-semantics change to the 7c baseline) that registers the **B-54 audit-verification composition** as ONE new runtime-mediated cross-axis edge, mirroring the v2.20 §2.3.8 R-PM-1 registration shape exactly. The plan-canonical §2.1 aggregate (**107** = 37 genuine + 48 convention + 22 phase-2-runtime) is **frozen verbatim**; the §2.3.8 R-PM-1 family (2 edges) is **frozen verbatim**. A NEW §2.3.9 registers **1 runtime-mediated edge** — **CP→OD audit-signature verification** (the C-CP-20 §20.3.1 blocking audit-walk consumes the OD v1.34 §21.2.2 backend-aware verifier through a CP-owned injection Protocol composed at the `harness-runtime` composition root per CP v1.101 §3 / CP plan v2.38 U-CP-44/45 / Runtime plan v2.49 U-RT-138) — reporting **107 plan-canonical + 2 R-PM-1 + 1 B-54 = 110 total cross-axis relationships**. ZERO change to §2.1 / §2.2 / §2.3.1–§2.3.8 / §2.4 / §3 (all preserved verbatim). Authored at the RATIFIED B-51/B-52/B-54 apply arc (Arc A, PR #1056), bundled-absorption per workspace `CLAUDE.md` §11.4. 2026-07-18.*

## §0 Change note (v2.20 → v2.21)

### §0.1 Revision context — the B-54 verifier seam (apply-arc codex rounds 33/46)

The RATIFIED B-51/B-52/B-54 arc (fork `.harness/class_1_fork_b51_b52_b54_od_signing_amendment_arc.md`, all ten gate items AS RECOMMENDED 2026-07-18) reconciles the CP-owned §20.3.1 blocking audit-walk with the NEW OD v1.34 §21.2.2 backend-aware verification API (CP v1.101 §3, gate item 5). The reconciliation deliberately creates **no package-level import edge** — `harness-cp` declares its own injected-verifier Protocol + result boundary and never imports `harness-od` (witness-pinned at CP plan v2.38); the `harness-runtime` composition root (U-RT-138) supplies the adapter over the real U-OD-55 verifier. Out-of-family review (apply-arc round 46) correctly held that a runtime-mediated consumer→producer relationship is EXACTLY what this document's §2.3.8 precedent registers — leaving it unregistered would hide a load-bearing dependency from the canonical seam graph and the overlay.

### §0.2 What is added (and what is frozen)

**Added:** §2.3.9 — the **B-54 audit-verification forward-capability seam** (1 runtime-mediated edge), plus the aggregate clause update (§0.5).

**Frozen verbatim (NOT touched by v2.21):** §2.1 aggregate 4×4 matrix (107) + 37/48/22 sub-split; §2.2 axis-level dependency graph; §2.3.1–§2.3.8 per-bucket rows (including the 2 R-PM-1 edges); §2.4; §3.

### §0.3 The registered edge (runtime-mediated, R-live)

Direction respects the consumer→producer convention; the IMPORT-level axis acyclicity (OD→CP canonical per §2.3.3; `harness-cp` MUST NOT import `harness-od`) is PRESERVED — the edge is mediated entirely at the runtime composition root:

| # | Bucket | Consumer (axis) | Producer (axis) | What flows | Composition site | Fail-loud |
|---|---|---|---|---|---|---|
| 1 | **CP→OD** | CP §20.3.1 blocking audit-walk (C-CP-20; CP v1.101 §3) | OD §21.2.2 backend-aware signature verifier (C-OD-21; OD v1.34, plan unit U-OD-55) | per-entry verification verdicts through the CP-owned discriminated boundary (VALID / INVALID-with-reason incl. the hash-chain discriminator / CP availability type; defects propagate unwrapped) | `harness-runtime` composition root — the U-RT-138 adapter wraps the real U-OD-55 verifier in the CP Protocol and injects it wherever the walk is invoked (`harness-inspect` is the first production site) | walk WITHOUT an injected verifier returns explicit INCOMPLETE/UNVERIFIED, never a hash-only pass (CP v1.101 §3 row 1b) |

### §0.4 Why R-class, and why "R-planned" not "R-live"

Same classification logic as v2.20 §0.4: no new genuine-typed (G) inter-axis import seam is created — the Protocol is CP-owned, the adapter runtime-owned, so the edge is **R (runtime-mediated composition)**. UNLIKE the R-PM-1 edges (materialized-live at their registration), this edge's producers are SPEC-APPLIED but the impl arc is pending (U-OD-55 / U-CP-44/45 amendments / U-RT-138 are open plan units at OD v2.29 / CP v2.38 / Runtime v2.49) — the §2.3.9 table tagged it **`R-planned`** at registration; the impl arc landed at PR #1067 (2026-07-20) and the tag is now **`R-live`** per this section's own one-cell-edit + clearance prescription (marker at `.harness/clearance/cross-axis-composition-v2-21-r-live-flip-2026-07-20.md`).

### §0.5 Aggregate clause

**107 plan-canonical (FROZEN) + 2 R-PM-1 forward-capability (§2.3.8, `R-live`) + 1 B-54 audit-verification forward-capability (§2.3.9, `R-live` since 2026-07-20/PR #1067) = 110 total cross-axis relationships.**

## §2.3.9 — B-54 audit-verification forward-capability seam (NEW at v2.21)

| # | Edge | Class | Consumer | Producer | Mediation | Status |
|---|---|---|---|---|---|---|
| 1 | CP→OD audit-signature verification | R (runtime-mediated) | C-CP-20 §20.3.1 walk via the CP-owned injected-verifier Protocol (CP v1.101 §3) | C-OD-21 §21.2.2 backend-aware verifier (OD v1.34; U-OD-55) | U-RT-138 composition-root adapter (`harness-runtime` imports both; `harness-cp` never imports `harness-od` — package-graph witness at CP plan v2.38) | **`R-live`** — spec-applied at the Arc A apply pass (PR #1056); FLIPPED `R-planned` → `R-live` in-place 2026-07-20 at the impl arc's landing (PR #1067: U-CP-44/45/42 ⊕ U-RT-138 — the walk, the CP result boundary, the U-RT-138 adapter, and the `harness-inspect` §13.5 injection site all landed; the one-cell flip this row itself prescribed) |

*All prior sections preserved verbatim per the delta convention. Clearance marker at `.harness/clearance/cross-axis-composition-v2-21-cleared-2026-07-18.md`.*
