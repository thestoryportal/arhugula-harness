# Cross-Axis Composition Document (v2.22)

*Delta over v2.21. v2.22 is an **additive forward-capability registration** (no contract change to any plan-canonical edge, no edge-semantics change to the 7c baseline) that registers the **B-33 rotation-pair-evidence composition** as ONE new runtime-mediated cross-axis edge, mirroring the v2.21 §2.3.9 B-54 registration shape exactly — a DISTINCT edge for a DISTINCT injected verifier (rotation-pair evidence for `verify_rotation_6_steps`, not the audit walk `AuditWalkVerifier` §2.3.9 already registers). The plan-canonical §2.1 aggregate (**107** = 37 genuine + 48 convention + 22 phase-2-runtime) is **frozen verbatim**; the §2.3.8 R-PM-1 family (2 edges) and the §2.3.9 B-54 edge (1 edge) are **frozen verbatim**. A NEW §2.3.10 registers **1 runtime-mediated edge** — **CP→OD rotation-pair-evidence lookup** (the C-CP-20 §20.3.2 `verify_rotation_6_steps` extension consumes the OD spec v1.35 §24.8 per-correlation-id evidence accessor through a CP-owned injection Protocol composed at the `harness-runtime` composition root per CP v1.105 §2 / CP plan v2.41 U-CP-44/45 / Runtime plan v2.53 U-RT-147) — reporting **107 plan-canonical + 2 R-PM-1 + 1 B-54 + 1 B-33 = 111 total cross-axis relationships**. ZERO change to §2.1 / §2.2 / §2.3.1–§2.3.9 / §2.4 / §3 (all preserved verbatim). Authored at the RATIFIED B-33 apply arc's spec+plan leg, bundled-absorption per workspace `CLAUDE.md` §11.4. 2026-07-23.*

## §0 Change note (v2.21 → v2.22)

### §0.1 Revision context — the B-33 rotation-pair-evidence seam

The RATIFIED B-33 arc (fork `.harness/class_1_fork_b33_rotation_correlation_carrier.md`, RATIFIED 2026-07-21, Option A) extends the CP-owned `verify_rotation_6_steps` (C-CP-20 §20.3.2) to consume the NEW OD spec v1.35 §24.8 per-correlation-id rotation-pair evidence accessor. The reconciliation deliberately creates **no package-level import edge** — `harness-cp` declares its own `RotationPairEvidenceProvider` Protocol + `RotationPairEvidence` DTO and never imports `harness-od` (mirroring the SAME no-cross-import discipline the §2.3.9 `AuditWalkVerifier` seam already established); the `harness-runtime` composition root (U-RT-147, a SECOND independent adapter alongside U-RT-138's) supplies the concrete adapter over OD's `find_rotation_pair_evidence`. This is the SAME registration logic §2.3.9 applied to the B-54 seam — a distinct injected verifier deserves its own row, not a folded-in amendment of §2.3.9 (the two Protocols, adapters, and OD-side accessors are wired independently per Runtime spec v1.105 §13.6's own framing).

### §0.2 What is added (and what is frozen)

**Added:** §2.3.10 — the **B-33 rotation-pair-evidence forward-capability seam** (1 runtime-mediated edge), plus the aggregate clause update (§0.5).

**Frozen verbatim (NOT touched by v2.22):** §2.1 aggregate 4×4 matrix (107) + 37/48/22 sub-split; §2.2 axis-level dependency graph; §2.3.1–§2.3.9 per-bucket rows (including the 2 R-PM-1 edges + the 1 B-54 edge); §2.4; §3.

### §0.3 The registered edge (runtime-mediated, R-planned)

Direction respects the consumer→producer convention; the IMPORT-level axis acyclicity (OD→CP canonical per §2.3.3; `harness-cp` MUST NOT import `harness-od`) is PRESERVED — the edge is mediated entirely at the runtime composition root:

| # | Bucket | Consumer (axis) | Producer (axis) | What flows | Composition site | Fail-loud |
|---|---|---|---|---|---|---|
| 1 | **CP→OD** | CP §20.3.2 `verify_rotation_6_steps` extension (C-CP-20; CP v1.105 §2) | OD §24.8 per-correlation-id rotation-pair evidence accessor (C-OD-24; OD v1.35, plan unit U-OD-56) | `RotationPairEvidence` (correlation id + pair presence + both key periods + both key ids) through the CP-owned typed boundary; `RotationPairIntegrityBreach` (tamper) and `RotationPairEvidenceUnavailableError` (infra) propagate distinctly, never folded together | `harness-runtime` composition root — the U-RT-147 adapter wraps the real OD accessor in the CP Protocol and injects it into `verify_rotation_6_steps`; wired INDEPENDENTLY of the sibling U-RT-138 `AuditWalkVerifier` adapter at the same composition root | `PROBE_VERIFY_AT_READ` WITHOUT an injected evidence provider returns an explicit incomplete result, never the pre-v1.105 simulated pass (CP v1.105 §1) |

### §0.4 Why R-class, and why "R-planned" (this leg — spec+plan only)

Same classification logic as v2.21 §0.4: no new genuine-typed (G) inter-axis import seam is created — the Protocol is CP-owned, the adapter runtime-owned, so the edge is **R (runtime-mediated composition)**. This registration lands at the SPEC+PLAN leg of the arc — the producer (U-OD-56), consumer amendment (U-CP-44/45), and adapter (U-RT-147) are all OPEN plan units at this filing — so this §2.3.10 table is tagged **`R-planned`**, mirroring §2.3.9's own initial tagging. The impl arc's landing PR flips this cell `R-live` in place, per the same one-cell-edit + clearance prescription §2.3.9 already demonstrated (marker precedent: `.harness/clearance/cross-axis-composition-v2-21-r-live-flip-cleared-2026-07-20.md`).

### §0.5 Aggregate clause

**107 plan-canonical (FROZEN) + 2 R-PM-1 forward-capability (§2.3.8, `R-live`) + 1 B-54 audit-verification forward-capability (§2.3.9, `R-live` since 2026-07-20/PR #1067) + 1 B-33 rotation-pair-evidence forward-capability (§2.3.10, `R-planned` — flips `R-live` at the impl arc) = 111 total cross-axis relationships.**

## §2.3.10 — B-33 rotation-pair-evidence forward-capability seam (NEW at v2.22)

| # | Edge | Class | Consumer | Producer | Mediation | Status |
|---|---|---|---|---|---|---|
| 1 | CP→OD rotation-pair-evidence lookup | R (runtime-mediated) | C-CP-20 §20.3.2 `verify_rotation_6_steps` via the CP-owned injected `RotationPairEvidenceProvider` Protocol (CP v1.105 §2) | C-OD-24 §24.8 per-correlation-id evidence accessor (OD v1.35; U-OD-56) | U-RT-147 composition-root adapter (`harness-runtime` imports both; `harness-cp` never imports `harness-od` — package-graph witness owed at CP plan v2.41 impl) | **`R-planned`** — spec+plan-applied at this filing (2026-07-23); flips `R-live` at the impl arc's landing PR (mirroring §2.3.9's own flip precedent) |

*All prior sections preserved verbatim per the delta convention. Clearance marker owed at `.harness/clearance/cross-axis-composition-v2-22-cleared-2026-07-23.md`.*
