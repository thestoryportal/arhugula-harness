# CXA 7c — placeholder carrier-ID resolution table

**Filed:** 2026-05-16, Phase 7 sub-phase 7c prerequisite pass. **Status:** RESOLVED — feeds CXA v2.2 + OD plan v2.11.

Resolution method: each placeholder resolved to the canonical carrier unit by the cited
contract anchor against the producer-axis plan coverage table (skill §4.1.c; F3-02 precedent).
No carrier ID invented (X-AL-3). Descriptive-hint imprecisions noted as Class 3, non-blocking.

## §2.3.4 OD → IS — 6 → 4 edges (operator decision 2026-05-16: wire 4, OD plan v2.4 canonical)

Already canonically resolved at OD plan v2.4 §0.4.2 (C3-15 Path (i-refined)). CXA v2.1 §2.3.4 was stale.

| Source | Carrier | Contract anchor | Disposition |
|---|---|---|---|
| U-OD-20 | U-IS-12 | C-IS-10 §10.2 | resolved (OD v2.4) |
| U-OD-30 | U-IS-11 | C-IS-10 §10.5 | remapped (OD v2.4; was U-IS-NN C-IS-14 §14.2) |
| U-OD-30 | U-IS-10 | C-IS-10 §10.3 | remapped (OD v2.4; was U-IS-NN C-IS-13 §13.5) |
| U-OD-34 | U-IS-17 | IS substrate seam exports | terminal |
| ~~U-OD-27 → sqlite substrate~~ | — | ~~C-IS-13 §13.2~~ | DELETED (OD v2.4 — mis-routed; OD-axis internal) |
| ~~U-OD-27 → ring-buffer eviction~~ | — | ~~C-IS-08 §8.4~~ | DELETED (OD v2.4 — mis-routed; sqlite-internal OD policy) |

## §2.3.5 OD → AS — 10 edges (8 placeholders resolved)

| Source | Carrier | Contract anchor | Producer-plan evidence |
|---|---|---|---|
| U-OD-06 | U-AS-33 | C-AS-16 §16.1 + §16.4 | already resolved (terminal exporter) |
| U-OD-17 | **U-AS-14** | C-AS-12 §12.1 | AS plan v1 coverage §2145; §12.1 = 5-axis multiplicative tunable |
| U-OD-19 | **U-AS-19** | C-AS-15 §15.6 | AS plan v1 coverage §2150 |
| U-OD-23 | **U-AS-18** | C-AS-15 §15.4 | AS plan v1 coverage §2149 |
| U-OD-23 | **U-AS-31** | C-AS-14 §14.2 | AS plan v1 coverage §2103 (anthropic.* namespace) |
| U-OD-29 | **U-AS-15** | C-AS-12 §12.4 | AS plan v1 coverage §2146; §12.4 = cross-deployment monotonicity |
| U-OD-33 | **U-AS-14** | C-AS-12 §12.1 | as U-OD-17 |
| U-OD-33 | **U-AS-19** | C-AS-15 §15.6 | as U-OD-19 |
| U-OD-33 | **U-AS-15** | C-AS-12 §12.4 | as U-OD-29 |
| U-OD-34 | U-AS-33 | AS substrate seam exports | terminal |

## §2.3.6 OD → CP — 12 edges (7 placeholders resolved)

| Source | Carrier | Contract anchor | Producer-plan evidence |
|---|---|---|---|
| U-OD-07 | U-CP-54 | C-CP-24 §24.1.A + §24.1.B | already resolved |
| U-OD-08 | U-CP-54 | C-CP-24 §24.1.B | already resolved |
| U-OD-09 | U-CP-54 | C-CP-24 §24.1.C | already resolved (F-CP-01 Stage 3b inversion) |
| U-OD-17 | **U-CP-43** | C-CP-19 §19.2 | CP plan coverage §3503 (§19.2 = cross-deployment monotonicity) |
| U-OD-19 | **U-CP-32** | C-CP-14 §14.1 | CP plan coverage §3453 |
| U-OD-21 | **U-CP-09** | C-CP-04 | CP plan v2 U-CP-09 Implements C-CP-04 §4.1–4.3 |
| U-OD-23 | **U-CP-46** | C-CP-20 §20.6 | U-CP-46 declares 4 hitl.* span attribute schemas |
| U-OD-26 | **U-CP-47** | C-CP-21 §21.5 | CP plan coverage §3527 |
| U-OD-30 | **U-CP-46** | C-CP-20 §20.4 | CP plan coverage §3516 |
| U-OD-33 | **U-CP-43** | C-CP-19 §19.2 | as U-OD-17 |
| U-OD-34 | U-CP-54 | CP substrate seam exports | terminal |
| U-OD-34 | U-CP-55 | C-CP-24 §24.4 | already resolved (F2-12 inheritance) |

## Class 3 informational items (non-blocking; logged for forward catch)

- **C3-CXA-7c-1.** CXA v2.1 §2.3.5 descriptive hints attach "D2 sandbox-tier monotonicity"
  to C-AS-12 §12.1, but AS spec §12.1 is the 5-axis multiplicative tunable; §12.4 is the
  cross-deployment monotonicity contract. Contract anchors are correct; OD unit bodies
  (U-OD-33 §22.4) confirm intent to compose against §12.1. Hint prose only — corrected at CXA v2.2.
- **C3-CXA-7c-2.** CXA v2.1 §2.3.6 cites bare `C-CP-19` for the U-OD-17 / U-OD-33 edges.
  Refined to `C-CP-19 §19.2` (cross-deployment monotonicity sub-section) at CXA v2.2 — precision improvement.
- **C3-CXA-7c-3.** C-CP-20 §20.6 (HITL-event span schema) is materially carried by U-CP-46
  ("4 hitl.* span attribute schemas") but U-CP-46's Implements line cites §20.4/§20.5 only;
  CP plan coverage table maps the 4 hitl.* attributes to §20.5. Carrier is unambiguous (U-CP-46);
  the §20.5/§20.6 Implements-line imprecision is a CP-plan citation-precision item — folded into CP plan v2.10.
