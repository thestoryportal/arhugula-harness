# Spec: Control Plane — v1.117 (delta over v1.116)

*Delta-only file. v1.116, v1.115, and every earlier C-CP-01 … C-CP-29 body are preserved
verbatim except at the single amendment site named below: the C-CP-24 §24.1.B
F3-capability-floor lifecycle-event-attribute export table is RE-TABLED to the live,
already-ratified attribute counts. This is the register row `B-144` step-(2) venue
resolution: the two-venue count divergence (§24.1.B vs C-CP-03 §3.5 / OD C-OD-07 §7.1)
is resolved by carrying the superseding figures INTO §24.1.B, not by declaring §24.1 a
v1.2-frozen historical snapshot. No new attribute, name, sampling rule, or contract
number is minted — both count changes propagate supersessions ratified years-of-deltas
ago at their own venues (CP v1.3; OD v1.32). No Runtime, OD, CXA, or plan artifact is
amended.*

**Filed:** 2026-08-11
**Authority:** Register row `B-144` close_out step (2), resolved venue **A** via the
U-HK-13 two-reviewer resolver 2026-08-11 (codex = A, advisor = A, agreement recorded at
`.harness/loop_status.md`); OD spec v1.32's own change-note, which already mandated the
downstream CP count surfaces be updated ("Downstream code-level cardinality checks …
are updated in the same PR", `Spec_Operational_Discipline_v1_32.md` §"Cardinality").
**Predecessor:** `Spec_Control_Plane_v1_116.md`

## §0 Change-note (v1.116 → v1.117)

### §0.1 The defect

§24.1.B is declared at exactly one venue in the delta chain —
`Spec_Control_Plane_v1_2.md:2152-2166` — and was never re-tabled after two amendments
at other venues superseded its `Attribute count` column:

1. **`retry.*` 4 → 6 at CP v1.3.** `Spec_Control_Plane_v1_3.md:76` REPLACED the
   retry-attempt attribute set wholesale. All four v1.2 names the §24.1.B figure
   counts (`retry.attempt` / `retry.cause` / `retry.backoff_ms` / `retry.policy`) are
   retired; the six live names are `retry.attempt_number` / `retry.original_span_id` /
   `retry.delay_ms` / `retry.cause_attribution` / `retry.fail_class` /
   `engine.replay_disposition`. The v1.3 change-note routed a downstream export update
   (§24.4) but never named §24.1's own sub-table.
2. **`harness.breaker.*` 7 → 9 at OD v1.32.** `Spec_Operational_Discipline_v1_32.md`
   amended the C-OD-07 §7.1 canonical schema (+`cause` +`cooldown_ms`,
   B-19-BREAKER-AMBIENT-ATTRS) — the very authority §24.1.B's breaker row defers to
   ("7 attributes (per OD C-OD-07 §7.1 canonical schema)"). Note the venue: the growth
   is an **OD**-chain amendment; `Spec_Control_Plane_v1_32.md` contains zero breaker
   mentions. Code-side comments citing a bare "v1.32" for this growth are corrected to
   "OD v1.32" in the same-PR cascade (§0.4).

The code manifest (`harness-cp/src/harness_cp/cp_namespace_export_manifest.py`)
resolved the divergence inconsistently, one row each way — `retry.* = 4` (tracking the
stale §24.1.B row) but `harness.breaker.* = 9` (tracking the live C-OD-07 §7.1) — so
the manifest conformed to neither venue as a whole.

### §0.2 The ratified venue

Re-tabling (venue A) was preferred over a historical-snapshot declaration (venue B)
because: the retry figure counts a RETIRED set — a snapshot declaration would preserve
a row describing four attribute names that exist nowhere in the corpus; the breaker
row would permanently contradict the C-OD-07 §7.1 authority it explicitly cites; and a
snapshot posture would force the manifest's `harness.breaker.* = 9` row to regress to
7 or carry a permanently-declared divergence. §24.1's own composition-path summary
(`Spec_Control_Plane_v1_2.md:2167`) states the export table exists "to prevent the
export-claim ↔ ingest-reality structural conflation" — venue B would institutionalize
exactly that conflation. A repo-wide probe found no OD-side consumer of the 65-sum
figure (D6 ingestion is per-attribute-set, not sum-pinned); the only consumer is CP's
own acceptance-#6 test, whose docstring already records the sum as a moving figure
(63 → 65 at the OD v1.32 absorption).

### §0.3 Amendment site (the re-tabled §24.1.B)

The §24.1.B table at `Spec_Control_Plane_v1_2.md:2154-2159` is superseded by the table
below. The `fallback.*` and `lease.*` rows are carried BYTE-VERBATIM; only the
`retry.*` and `harness.breaker.*` `Attribute count` cells change (plus, on the breaker
row, the explicit OD-v1.32 lineage note inside the existing citation parenthetical).
The §24.1.B sub-heading, the §24.1.C table, and the composition-path summary paragraph
at `:2167` are PRESERVED VERBATIM.

| Namespace | Source contract | Attribute count | Always-sampled discipline | D6 lifecycle event mapping | Canonical anchor |
|---|---|---|---|---|---|
| `fallback.*` | C-CP-03 §3.5 | 9 attributes | `fallback.triggered` / `fallback.exhausted` always-sampled per C-CP-03 §3.5 | `fallback.triggered` span event on parent + new sibling fallback span (D6 §1.2 line 127) | ADR-F3 v1.1 capability-floor (iv) |
| `retry.*` | C-CP-03 §3.5 (v1.3 amendment) | 6 attributes | Base-rate at 1st attempt; always-sampled at 2nd onward per C-CP-03 §3.5 | `retry.attempt` span event on parent + new sibling retry span (D6 §1.2 line 128) | ADR-F3 v1.1 capability-floor (iv) |
| `lease.*` | C-CP-05 §5.3 | 5 attributes | Base-rate per C-CP-05 §5.4 | `lease.acquired` / `lease.released` span events on parent (D6 §1.2 lines 130–131) | ADR-F3 v1.1 capability-floor (iv) |
| `harness.breaker.*` | C-CP-03 §3.5 (CP-side deployment composition); `c9-reliability-recovery` SKILL.md (substrate-anchored canonical declaration per F2-16 closure and Workflow v1.3 §2.3.3.1 clause (iii)) | 9 attributes (per OD C-OD-07 §7.1 canonical schema as amended at OD v1.32, B-19-BREAKER-AMBIENT-ATTRS; enumerated at D6 §1.2.1) | `breaker.tripped` always-sampled per C-CP-03 §3.5 + D6 §1.3 | `breaker.tripped` span event on parent (D6 §1.2 line 129); nine-attribute schema at D6 §1.2.1 | `c9-reliability-recovery` SKILL.md substrate (NOT CP-anchored); CP consumes but does not own the canonical declaration |

The §24.1.B subtotal therefore moves 25 → 29 as declared (the code manifest's
previously-derived 27 was the half-absorbed state: breaker carried, retry not), and
the declared CP-axis export sum moves 65 → 67 (34 + 29 + 4).

### §0.4 Same-PR downstream cascade (bundled absorption per root `CLAUDE.md` §11.4)

`cp_namespace_export_manifest.py`: `retry.*` `attribute_count` 4 → 6 (comment rewritten
— the declared-subset caveat retires; the count now matches C-CP-03 §3.5 v1.3, though
the WIRE still carries more `retry.`-prefixed keys than the declared set, per the
`B-126` register discipline, which this delta does not change); breaker-row and
module-docstring comments correct the bare "v1.32" lineage cite to OD v1.32; the
module docstring's sum arithmetic updates to 67. Test
`test_cp_namespace_export_manifest.py`: per-row expectation `retry.*` 4 → 6;
acceptance-#6 sum assertion 65 → 67. The Runtime bootstrap inversion check
(`verify_harness_breaker_namespace_inversion`) compares the breaker row only (9 == 9)
and is unaffected. No other consumer of the sum exists in any `harness-*/src` tree
(swept 2026-08-11).

### §0.5 Explicitly OUT OF SCOPE — the `hitl.*` column-semantics question (→ `B-153`)

The third same-class case recorded at register row `B-144` — the §24.1.A `hitl.*` row
carries NO count ("per-event attributes across 4 span names",
`Spec_Control_Plane_v1_2.md:2148`) while the manifest pins `attribute_count=4`,
i.e. counts span names as attributes — is NOT adjudicated here. Its repair is a
decision about what the `Attribute count` COLUMN MEANS, which could ripple to other
§24.1.A rows (e.g. `audit.*` "7 attributes per persona-tier emission discipline") and
requires enumerating C-CP-20 §20.6. It is minted as register row `B-153`. The 67 sum
above carries hitl's unadjudicated 4 unchanged; this delta's re-table must NOT be read
as ratifying the span-names-as-attributes interpretation.

*End of v1.117 delta. All other content of the C-CP chain preserved verbatim.*
