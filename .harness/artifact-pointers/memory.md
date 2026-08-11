# Memory — artifact pointer lineage

*Split byte-preservingly from `.harness/claude-artifact-pointers.md` at the U-CTX-03/04/05/06 R-CTX-1 context-optimization arc (2026-08-10, `B-17`/R-ICM-1 lineage). Old path is now a resolving stub — see `.harness/claude-artifact-pointers.md`. Loaded on demand only; never part of the default session-start read path.*

---

**Current head is DERIVED, not carried here.** This file is a lineage ARCHIVE; the authoritative per-family head version is derived from the `.harness/clearance/` marker corpus into `.harness/artifact-heads.md` by `tools/artifact_heads.py` (R-CTX-1 / U-CTX-11), and two CI gates keep that table current. Head labels inline below are reconciled at each arc but the generated table wins on any disagreement.

**This pointer file predates Memory's inclusion in the §2.3/§2.4 tables above** (neither table above carries a `Memory` row — `Spec_Memory_Substrate_v1.md` / `Implementation_Plan_Memory_Substrate_v1.md` were adopted after this pointer file's table snapshot was taken). For the LIVE Memory spec/plan pointer, consult root `CLAUDE.md` §2.3/§2.4 directly (the `**Memory ...**` clause). What DOES live here is the pre-head/post-head relocated dated lineage for the Memory axis's ADR + spec + plan, byte-preserved verbatim from root `CLAUDE.md`:

## §2.2 relocated — ADR-D7 lineage

### §2.2 change-note lineage relocated 2026-07-30 (B-17 R-ICM-1 follow-on)

**C6 ADR-D7 dated adoption marker (proposed / cleared)** — relocated verbatim from root `CLAUDE.md` §2.2:

**New (2026-07-01, cleared 2026-07-09):** 

**C7 ADR-D7 §15/§86 in-place-correction note** — relocated verbatim from root `CLAUDE.md` §2.2:

 (its §15/§86 "external CLI routing … not in this repo" claim is corrected in-place — the routing was ported to `main` at PR #914, `R-300-external-cli-oauth-routing`)



## §2.3 / §2.4 head rows

Added at the R-CTX-1 U-CTX-12 reconciliation: this file carried only relocated PRE-head lineage, with no row naming the current head at all — the one shape the sibling family files could not drift into because they at least asserted a head.

| Axis | Spec |
|---|---|
| Memory | `Spec_Memory_Substrate_v1.md` (**v1.3 — canonical HEAD**, cleared 2026-08-06 — the `B-88` spec leg: C-MEM-19 gains `input_validation_failure` as a SEVENTH failure class, plus the NEW `### Input validation failure` subsection carrying the ratified A-ii type boundary, the coverage statement scoping the class to the classify-routed population, and the re-typed sites' fail-fast retry disposition; two invariants appended. ZERO contract numbers, ZERO hash impact, ZERO CXA rows. Clearance `spec-memory-substrate-v1-3-cleared-2026-08-06.md`. Predecessor v1.2, cleared 2026-07-29) |

| Axis | Plan | Unit count |
|---|---|---|
| Memory | `Implementation_Plan_Memory_Substrate_v1.md` (**v1.3 — canonical HEAD**, cleared 2026-08-06 — the `B-88` plan leg: U-MEM-22's failure-class acceptance extended to seven values in place, plus NEW U-MEM-28 at G8 decomposing the impl leg (enum member, declaration flip, the A-ii six-site re-typing with its receiving-type constraints, fail-fast preservation, and the witnesses). Clearance `implementation-plan-memory-substrate-v1-3-cleared-2026-08-06.md`. Predecessor v1.2, cleared 2026-07-29) | 28 units (U-MEM-01 – U-MEM-28) |

## §2.3 relocated — Memory spec lineage

### §2.3 change-note lineage relocated 2026-07-30 (B-17 R-ICM-1)

**C1 Memory spec pre-head lineage (Proposed / v1.1 B-86 delta)** — relocated verbatim from root `CLAUDE.md` §2.3:

Proposed 2026-07-01, cleared 2026-07-09; v1.1 cleared 2026-07-28 — the `B-86` spec leg: C-MEM-03 `provider_family` value domain + `null` semantics + run-level derivation rule, C-MEM-13 cross-family withhold invariant, C-MEM-14 exposure qualification; 

**C2 Memory spec post-head lineage (B-92 delta narrative)** — relocated verbatim from root `CLAUDE.md` §2.3:

 — the RATIFIED `B-92` spec leg (reading B, flag + gate): C-MEM-10 cross-family-captured promotion candidates carry the `cross_family_capture` risk-flag vocabulary value AND are review-required / never auto-promotable, plus C-MEM-03's NEW tri-state hash-inert `MemoryRecordEnvelope.captured_cross_family` field answering the fork's Q2 at `(i-envelope-bool)` on a stored-version-present/absent requirement (this reverses v1.1's zero-new-field posture, deliberately and on the record); threat model unchanged at both deltas


## §2.4 relocated — Memory plan lineage

### §2.4 change-note lineage relocated 2026-07-30 (B-17 R-ICM-1)

**C4 Memory plan pre-head lineage (v1 / v1.1 B-86 plan delta)** — relocated verbatim from root `CLAUDE.md` §2.4:

v1 cleared 2026-07-09, v1.1 cleared 2026-07-28 — the `B-86` spec leg's plan delta: NEW U-MEM-26 cross-family withhold guard + writer-side composed-scope repair; 

**C5 Memory plan post-head lineage (B-92 plan delta)** — relocated verbatim from root `CLAUDE.md` §2.4:

 — the `B-92` spec leg's plan delta: NEW U-MEM-27 cross-family-captured promotion gate, one central origin-aware tri-state derivation (`_capture` determines the origin disposition from `event_kind` and passes it into `_record`, which computes the final value by gating the family comparison over `provider` + resolved scope) plus the review gate at both promotion entry points, depends on U-MEM-26

