# Class 1 Tension — CXA §2.3.1 declares 6 AS→IS edges with no typed-seam realization

**Status:** ✅ RESOLVED 2026-05-17 — operator authorized the per-edge reclassification. The 6 forked AS→IS edges are dispositioned in `Cross_Axis_Composition_Document_v2_3.md` §2.3.1: blocker A (U-AS-25→U-IS-08) → convention-level; blocker B (U-AS-27→U-IS-11) → phase-2-runtime; blocker C (U-AS-29→U-IS-01/02) → convention-level ×2; blocker D (U-AS-30→U-IS-01/02) → spurious, struck ×2. The audit generalized to all 6 buckets — see CXA v2.3 §0.
**Filed:** 2026-05-17, Phase 7 sub-phase 7c, bucket-1 (AS→IS) wiring.
**Detected by:** `phase-7-cross-axis-composition` §4.2/§7 at bucket-1 wiring; routed via `phase-7-back-flow-routing` §6.5.

---

## Defect

CXA v2.2 §2.3.1 declares **13 typed AS→IS cross-axis edges**. At bucket-1 wiring, **7 resolved to genuine typed seams** (Pydantic v2 model imports — `phase-7-cross-axis-composition` §4.3). The other **6 have no typed-seam realization**: at 7b they materialized as convention / scheme / descriptor / runtime-level relationships. Per CXA-AL-1 (`Phase_7_Meta_Architecture_v1.md` §7.6) — "convention-based composition ≠ typed seam contracts" — the CXA §2.3.1 enumeration over-declares: it counts 6 convention-level relationships as typed edges.

§2.3.1 was inherited verbatim from CXA v2.1 (the 7c prerequisite pass did not touch §2.3.1).

## The 7 wired edges (verified — partial-land)

| AS unit | IS target | Seam | Wire |
|---|---|---|---|
| U-AS-19 | U-IS-07 / U-IS-12 | state-ledger entry / idempotency-key join | `from harness_is import Identifier`; `type IdempotencyKey = Identifier` |
| U-AS-26 | U-IS-07 / U-IS-09 / U-IS-10 | state-ledger entry / chain-link / verification | `from harness_is.state_ledger_entry_schema import …`; `chain_link_construction`; `chain_verification` (already wired at 7b) |
| U-AS-28 | U-IS-01 / U-IS-02 | filesystem path contract | `from harness_is import PathClass, PathClassMetadata` (already wired at 7b) |

harness-is pyright: 0 errors introduced (3 pre-existing baseline — `test_secret_allowlist.py`, unrelated). harness-is 125 tests green; harness-as 302 tests green. `Identifier` added to `harness_is/__init__.py __all__`.

## The 6 forked edges

| # | Edge | CXA-declared seam | 7b reality | Sub-class |
|---|---|---|---|---|
| A | U-AS-25 → U-IS-08 | HASH_CHAIN_CONSTRUCTION (canonicalize carrier) | U-IS-08's `canonicalize` is `StateLedgerEntry`-typed; U-AS-25 operates on a `(secret_name, scope, rotated_at)` triple and **re-applies the C-IS-06 §6.1 scheme** (NFC + sorted-key JSON). Scheme-level inheritance, not a type import. `secret_outputs_hash.py` docstring already calls this "a Class 3 cross-axis observation". | scheme-inheritance |
| B | U-AS-27 → U-IS-11 | JSONL_EVENT_LEDGER_FORMAT_EXPORT (write contract) | U-IS-11 exports `append_ledger_entry`; U-AS-27's `emit_secret_fetch_audit` **composes** the audit entry and returns it — the `.harness/state.jsonl` append is a **runtime concern (Phase 2)**. Importing `append_ledger_entry` would be dead code. | Phase-2 runtime |
| C | U-AS-29 → U-IS-01, U-IS-02 (2 edges) | FILESYSTEM_PATH_CONTRACT_EXPORT | `engine_class_composition.py` expresses §13.3 column-5 filesystem residence as a **free-text `skills_filesystem_residence: str` descriptor** ("Harness reads SKILL.md from F2 filesystem", "SKILL.md mounted as ConfigMap / PVC"). Not a `PathClass` consumption. | prose descriptor |
| D | U-AS-30 → U-IS-01, U-IS-02 (2 edges) | FILESYSTEM_PATH_CONTRACT_EXPORT | `anthropic_graceful_degradation.py` §13.6 step 8 uses the **AS-local `MemoryToolStorageBackend` StrEnum** (`filesystem`/`s3`/`database`/…). No IS path-class type consumed — the CXA edge has no AS-side referent at all. | spurious / AS-local |

## Why Class 1 (not Class 2 / Class 3)

`phase-7-back-flow-routing` §6.5: a CXA edge enumeration contradicting consumer-side realization is **Class 1 — CXA defect OR consumer-side plan defect; operator decides locus.** §2.4: "When uncertain, default to Class 1." The CXA §2.3.1 typed-edge enumeration is a Phase-6 design artifact and is incorrect as filed — 6 declared typed edges are not typed. Silent absorption (wiring 6 fake imports to hit "13/13") is the X-AL-3 / CXA-AL-1 anti-pattern explicitly foreclosed.

## Resolution options (operator decides)

**Option 1 — Reclassify in CXA (recommended).** The 6 are genuinely not typed seams; the 7b authors implemented them faithfully as convention/scheme/runtime/descriptor relationships (U-AS-25's docstring pre-flagged it). CXA v2.3 §2.3.1: typed AS→IS edges **13 → 7**; the 6 reclassified into a documented "convention-level / scheme-inheritance / Phase-2-deferred seam" sub-table (non-typed, non-counted). Aggregate cross-axis typed edges **99 → 93**. No AS-plan or IS-plan change. Risk: the same over-declaration likely exists in the other 5 buckets (CP→IS 36, CP→AS 24, OD→*) — a systemic CXA-typed-edge audit may be owed.

**Option 2 — Force typed seams.** Revise the AS plan/spec so U-AS-25/27/29/30 consume IS types: IS factors a reusable `canonicalize` primitive (A); U-AS-29 `skills_filesystem_residence` becomes `PathClass`-typed (C); etc. Heavier — AS plan + IS plan revisions, re-landing 4 AS units, and Blocker B (runtime write) genuinely cannot become a 7c type-import regardless.

**Option 3 — Mixed.** Per-edge disposition: A → reclassify scheme-inheritance; B → reclassify Phase-2-deferred; C → force typed (U-AS-29 should arguably consume `PathClass`); D → investigate whether the CXA edge is simply spurious.

## Halt state

| Element | Value |
|---|---|
| Halt point | 7c bucket-1 (AS→IS) close — 7/13 edges wired, 6 forked |
| Routing target | CXA revision (Phase-6 CXA channel; in-CLI per design-substrate-canonical discipline) — possibly + AS/IS plan if Option 2/3 |
| Resumption | Operator picks resolution option → CXA v2.3 (± AS/IS plan) → bucket-1 close → bucket 2 (CP→IS) opens |
| Buckets 2–6 | NOT opened. If Option 1 + systemic audit: buckets 2–6 may carry the same defect. |
