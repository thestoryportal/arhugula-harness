# Spec: Control Plane — v1.118 (delta over v1.117)

*Delta-only file. v1.117 and every earlier C-CP-01 … C-CP-29 body are preserved
verbatim except at the two amendment sites named below: the C-CP-24 §24.1 `Attribute
count` column receives its first explicit DEFINITION, and under it the §24.1.A
`hitl.*` row's countless cell ("per-event attributes across 4 span names") becomes the
enumerated `11 attributes across 4 span names`. This is the register row `B-153`
adjudication — the third same-class case split out of `B-144` at its venue-A close
(PR #1311), quarantined there by v1.117 §0.5 ("this delta's re-table must NOT be read
as ratifying the span-names-as-attributes interpretation"). No new attribute, name,
sampling rule, or contract number is minted — the 11 figure is the C-CP-20 §20.6
distinct-declared-key enumeration that OD has committed to since C-OD-05 §5.1 row 6
("11 attributes across 4 span names") and that `harness_od/namespace_map.py` already
ingests. One same-PR companion delta carries the owed plan half —
`Implementation_Plan_Control_Plane_v2_51.md` (the U-CP-54 acceptance re-pin 68 → 75).
No OD, Runtime, or CXA artifact is amended: the OD side was already correct.*

**Filed:** 2026-08-11
**Authority:** Register row `B-153` close_out steps (1)–(3); the `B-144` venue-A
precedent (a declared live export claim carried INTO §24.1, PR #1311); C-OD-05 §5.1
row 6 (`Spec_Operational_Discipline_v1_2.md:334`) as the live cross-axis
counterexample that grounded the row.
**Predecessor:** `Spec_Control_Plane_v1_117.md`

## §0 Change-note (v1.117 → v1.118)

### §0.1 The defect

The §24.1.A `hitl.*` row (`Spec_Control_Plane_v1_2.md:2148`) is the only §24.1 row
whose `Attribute count` cell carries NO count — "per-event attributes across 4 span
names" — while `cp_namespace_export_manifest.py` pins `attribute_count=4`: the code
counted SPAN NAMES as attributes. Unlike the two B-144 rows this was not a stale count
with a live figure waiting at another CP venue — no CP venue declared ANY hitl.*
attribute count — so the repair required deciding what the column MEANS (v1.117 §0.5
deliberately withheld that ratification and minted `B-153`).

### §0.2 The column definition (NEW; first explicit ratification)

The C-CP-24 §24.1 `Attribute count` column states, per namespace row, **the
namespace's declared live export claim in DISTINCT attribute keys** — the cardinality
of the set of attribute names the row's source contract declares for that namespace,
counted once per key regardless of how many span names or events carry the key.
Consequences, stated so each is a decision:

1. **Span names are not attributes.** A row's span-name count never stands in for its
   attribute count (the manifest's hitl `4` was exactly that error).
2. **Intra-row cross-event repeats count once.** `hitl.gate.level` appears on both
   `hitl.gate.evaluated` and `hitl.invocation.opened` (a §20.6 cross-event reference)
   and contributes ONE key to the row.
3. **The cross-namespace sum caveat of v1.117 §0.3 STANDS unchanged.** The CP-axis
   export sum remains a sum of declared row counts, not a distinct-key cardinality
   across rows (`engine.replay_disposition` stays counted under both `engine.*` and
   the §3.5 retry set — a declared cross-namespace composition attribute).
4. **Parent-span reads are not row exports.** Identities §20.6 reads from canonical
   parent-span attributes (`gen_ai.tool.name`, `mcp.server.name`) belong to their own
   namespaces and never count toward `hitl.*`.

### §0.3 The `hitl.*` cell, enumerated from C-CP-20 §20.6

The four span names declare, per the §20.6 table (`Spec_Control_Plane_v1_2.md:1816-1821`):

| Span name | Declared `hitl.*` keys | New keys |
|---|---|---|
| `hitl.gate.evaluated` | `hitl.gate.level`, `hitl.gate.persona_tier`, `hitl.gate.required` | 3 |
| `hitl.invocation.opened` | `hitl.gate.level` (cross-event reference), `hitl.invocation.placement`, `hitl.invocation.handoff_context_size_bytes`, `hitl.invocation.audit_ledger_entry_id` | 3 |
| `hitl.invocation.responded` | `hitl.response.class`, `hitl.response.latency_ms`, `hitl.response.summary_hash` | 3 |
| `hitl.invocation.timed_out` | `hitl.timeout.duration_ms`, `hitl.timeout.degradation_mode_applied` | 2 |

**11 distinct keys across 4 span names.** The §24.1.A `hitl.*` `Attribute count` cell
becomes `11 attributes across 4 span names (C-CP-20 §20.6 distinct declared keys)`;
every other cell of the row — source contract, always-sampled discipline, D6 ingest
row — is preserved verbatim. This RECONCILES the row with the standing OD commitment:
C-OD-05 §5.1 row 6 has carried "11 attributes across 4 span names" since OD v1.2, and
`harness_od/namespace_map.py` ingests 11 citing C-CP-20 §20.6 — the cross-axis
counterexample recorded on the register row, now the ratified figure.

### §0.4 The `audit.*` qualifier row, audited under the same definition — CONFORMS

Close_out step (2)'s companion audit: the `audit.*` cell "7 attributes per
persona-tier emission discipline" is a true distinct-key count — §20.4 is titled
"Seven `audit.*` span attribute declarations" and tables exactly seven distinct keys
(`audit.signature.sha256` / `.prior_hash` / `.value` / `.algorithm` / `.key_id` /
`.key_period` + `audit.actor.id`); the "per persona-tier emission discipline"
qualifier describes §20.5's per-tier emission subsets, not a different counting rule.
No edit owed; recorded here so the audit is a decision, not an omission.

### §0.5 Subtotal + sum cascade

The §24.1.A subtotal moves 35 → 42 (hitl 4 → 11; engine 4 + topology 10 + subagent 7
+ hitl 11 + audit 7 + validator.fail 3), and the declared CP-axis export sum moves
68 → 75 (42 + 29 + 4). The §24.1.B subtotal (29) and the routing.* row (4) are
untouched.

### §0.6 Same-PR downstream cascade (bundled absorption per root `CLAUDE.md` §11.4)

`cp_namespace_export_manifest.py`: `hitl.*` `attribute_count` 4 → 11 (comment
rewritten to cite the §20.6 enumeration; the span-names-as-attributes reading
retires); module-docstring sum arithmetic 68 → 75 (42 + 29 + 4).
`cp_cross_axis_composition_manifest.py`: derives from `CP_EXPORTED_ATTRIBUTE_COUNT`
(since v1.117) — follows automatically, no edit. Test
`test_cp_namespace_export_manifest.py`: hitl per-row expectation 4 → 11;
acceptance-#6 sum assertion renamed `test_total_attribute_count_seventy_five`, 68 →
75. NEW cross-package witness at `harness-runtime/tests/test_lifecycle_od_cp_wiring.py`
comparing every OD CP-source `namespace_map` row count against its CP manifest row —
the #1311-recorded "no cross-package map↔manifest count comparison" residual was
ill-defined until this column ratification and is closed by it. The companion plan
delta v2.51 re-pins U-CP-54's inherited acceptance figures. The Runtime bootstrap
inversion check (breaker row only, 9 == 9) is unaffected. OD-side: NO delta —
C-OD-05 §5.1 row 6 and `namespace_map.py` already carry 11.

*End of v1.118 delta. All other content of the C-CP chain preserved verbatim.*
