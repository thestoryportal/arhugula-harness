# Memory — artifact pointer lineage

*Split byte-preservingly from `.harness/claude-artifact-pointers.md` at the U-CTX-03/04/05/06 R-CTX-1 context-optimization arc (2026-08-10, `B-17`/R-ICM-1 lineage). Old path is now a resolving stub — see `.harness/claude-artifact-pointers.md`. Loaded on demand only; never part of the default session-start read path.*

---

**This pointer file predates Memory's inclusion in the §2.3/§2.4 tables above** (neither table above carries a `Memory` row — `Spec_Memory_Substrate_v1.md` / `Implementation_Plan_Memory_Substrate_v1.md` were adopted after this pointer file's table snapshot was taken). For the LIVE Memory spec/plan pointer, consult root `CLAUDE.md` §2.3/§2.4 directly (the `**Memory ...**` clause). What DOES live here is the pre-head/post-head relocated dated lineage for the Memory axis's ADR + spec + plan, byte-preserved verbatim from root `CLAUDE.md`:

## §2.2 relocated — ADR-D7 lineage

### §2.2 change-note lineage relocated 2026-07-30 (B-17 R-ICM-1 follow-on)

**C6 ADR-D7 dated adoption marker (proposed / cleared)** — relocated verbatim from root `CLAUDE.md` §2.2:

**New (2026-07-01, cleared 2026-07-09):** 

**C7 ADR-D7 §15/§86 in-place-correction note** — relocated verbatim from root `CLAUDE.md` §2.2:

 (its §15/§86 "external CLI routing … not in this repo" claim is corrected in-place — the routing was ported to `main` at PR #914, `R-300-external-cli-oauth-routing`)



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

