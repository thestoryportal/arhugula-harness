"""CP-axis namespace export manifest — U-CP-54.

Implements C-CP-24 §24.1.A/§24.1.B/§24.1.C (the CP-axis namespace export
manifest). Declares the `NamespaceExport` record, the `SourceAuthorityPosture`
and `IngestionTarget` enums, and the `CP_NAMESPACE_EXPORT_MANIFEST` constant —
11 namespace-export references the OD plan Session 4 D6 ingests.

The manifest is **descriptive, not declarative** (acceptance #9): the namespace
declarations themselves live at the source units (U-CP-01/07/11/21/31/46/47);
this manifest exports references only. 11 namespaces — 6 specialization-layer
(§24.1.A), 4 F3-lifecycle-event (§24.1.B), 1 inheritance-composition (§24.1.C)
— 75 CP-axis attributes total (42 + 29 + 4; was 63, then 65 after `B-126`
recomputed the `harness.breaker.*` 7 -> 9 growth from OD spec v1.32, then 68
at the CP v1.117 `B-144` venue-A re-table: retry.* 4 -> 6 + engine.* 3 -> 4,
then 75 at the CP v1.118 `B-153` column ratification: hitl.* 4 -> 11).

Authority: Implementation_Plan_Control_Plane_v2_1.md §2.9 U-CP-54 as re-pinned
at Implementation_Plan_Control_Plane_v2_51.md; Spec_Control_Plane_v1_2.md §24
C-CP-24 §24.1.A/§24.1.B/§24.1.C as re-tabled at Spec_Control_Plane_v1_117.md
and column-ratified at Spec_Control_Plane_v1_118.md (B-153).
"""

from __future__ import annotations

from enum import StrEnum

from harness_core import UnitId
from pydantic import BaseModel, ConfigDict


class SourceAuthorityPosture(StrEnum):
    """The source-authority posture of an exported namespace (C-CP-24 §24.1)."""

    OWNED_BY_CP = "owned-by-cp"
    SUBSTRATE_ANCHORED_OUTSIDE_CP = "substrate-anchored-outside-cp"
    """`harness.breaker.*` per F2-16 — canonical schema at OD C-OD-07 §7.1."""

    COMPOSED_FROM_CROSS_AXIS = "composed-from-cross-axis"
    """Composition of CP + IS or CP + AS sources."""


class IngestionTarget(StrEnum):
    """The OD-plan D6 ingestion target for an exported namespace (C-CP-24 §24.1)."""

    OD_PLAN_SESSION_4_D6_SECTION_1_2 = "od-plan-session-4-d6-section-1-2"
    """Specialization-layer namespaces."""

    OD_PLAN_SESSION_4_D6_SECTION_1_4 = "od-plan-session-4-d6-section-1-4"
    """F3 lifecycle-event attributes."""

    OD_PLAN_SESSION_4_D6_SECTION_1_5 = "od-plan-session-4-d6-section-1-5"
    """Inheritance from the parent LLM inference span (per AS spec v1.7 §14.1
    alias-term; runtime span-name format owned by OD spec v1.12 §C-OD-04 §4.1)."""


class NamespaceExport(BaseModel):
    """One CP-axis namespace export reference (C-CP-24 §24.1)."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    namespace_name: str
    attribute_count: int
    source_unit: UnitId
    ingestion_target: IngestionTarget
    sub_section_authority: str
    """The C-CP-24 sub-section anchor."""

    source_authority_posture: SourceAuthorityPosture


_D6_1_2 = IngestionTarget.OD_PLAN_SESSION_4_D6_SECTION_1_2
_D6_1_4 = IngestionTarget.OD_PLAN_SESSION_4_D6_SECTION_1_4
_D6_1_5 = IngestionTarget.OD_PLAN_SESSION_4_D6_SECTION_1_5
_OWNED = SourceAuthorityPosture.OWNED_BY_CP

CP_NAMESPACE_EXPORT_MANIFEST: tuple[NamespaceExport, ...] = (
    # --- §24.1.A — 6 specialization-layer namespaces (D6 §1.2 direct ingest) -
    NamespaceExport(
        # 4 per C-CP-09 §9.1 as extended at CP v1.3 (+engine.replay_disposition,
        # the ratified 4th row), carried into §24.1.A at CP v1.117 (B-144
        # venue-A rule, out-of-family round-2 catch). See
        # `engine_namespace.ENGINE_NAMESPACE_SCHEMA` (already 4).
        namespace_name="engine.*",
        attribute_count=4,
        source_unit=UnitId("U-CP-21"),
        ingestion_target=_D6_1_2,
        sub_section_authority="C-CP-24 §24.1.A",
        source_authority_posture=_OWNED,
    ),
    NamespaceExport(
        namespace_name="topology.*",
        attribute_count=10,
        source_unit=UnitId("U-CP-31"),
        ingestion_target=_D6_1_2,
        sub_section_authority="C-CP-24 §24.1.A",
        source_authority_posture=_OWNED,
    ),
    NamespaceExport(
        namespace_name="subagent.*",
        attribute_count=7,
        source_unit=UnitId("U-CP-31"),
        ingestion_target=_D6_1_2,
        sub_section_authority="C-CP-24 §24.1.A",
        source_authority_posture=_OWNED,
    ),
    NamespaceExport(
        # 11 distinct declared keys across 4 span names per C-CP-20 §20.6,
        # ratified at CP v1.118 (B-153) — matching OD C-OD-05 §5.1 row 6 and
        # harness_od/namespace_map.py. The prior 4 counted SPAN NAMES as
        # attributes (the span-names-as-attributes reading v1.117 §0.5
        # explicitly declined to ratify).
        namespace_name="hitl.*",
        attribute_count=11,
        source_unit=UnitId("U-CP-46"),
        ingestion_target=_D6_1_2,
        sub_section_authority="C-CP-24 §24.1.A",
        source_authority_posture=_OWNED,
    ),
    NamespaceExport(
        namespace_name="audit.*",
        attribute_count=7,
        source_unit=UnitId("U-CP-46"),
        ingestion_target=_D6_1_2,
        sub_section_authority="C-CP-24 §24.1.A",
        source_authority_posture=_OWNED,
    ),
    NamespaceExport(
        namespace_name="validator.fail.*",
        attribute_count=3,
        source_unit=UnitId("U-CP-47"),
        ingestion_target=_D6_1_2,
        sub_section_authority="C-CP-24 §24.1.A",
        source_authority_posture=_OWNED,
    ),
    # --- §24.1.B — 4 F3-lifecycle-event-attribute namespaces (D6 §1.4) -------
    NamespaceExport(
        namespace_name="fallback.*",
        attribute_count=9,
        source_unit=UnitId("U-CP-07"),
        ingestion_target=_D6_1_4,
        sub_section_authority="C-CP-24 §24.1.B",
        source_authority_posture=_OWNED,
    ),
    NamespaceExport(
        # 6 per C-CP-03 §3.5 v1.3, carried into §24.1.B at CP v1.117 (B-144
        # venue-A re-table). Declared count, not wire cardinality: the wire
        # carries more `retry.`-prefixed keys than the declared set (B-126).
        # See `retry_fallback_namespace.RETRY_WIRE_REGISTER`.
        namespace_name="retry.*",
        attribute_count=6,
        source_unit=UnitId("U-CP-07"),
        ingestion_target=_D6_1_4,
        sub_section_authority="C-CP-24 §24.1.B",
        source_authority_posture=_OWNED,
    ),
    NamespaceExport(
        namespace_name="lease.*",
        attribute_count=5,
        source_unit=UnitId("U-CP-11"),
        ingestion_target=_D6_1_4,
        sub_section_authority="C-CP-24 §24.1.B",
        source_authority_posture=_OWNED,
    ),
    NamespaceExport(
        namespace_name="harness.breaker.*",
        attribute_count=9,  # OD v1.32: +cause +cooldown_ms (B-19-BREAKER-AMBIENT-ATTRS)
        source_unit=UnitId("U-CP-07"),
        ingestion_target=_D6_1_4,
        sub_section_authority="C-CP-24 §24.1.B",
        source_authority_posture=SourceAuthorityPosture.SUBSTRATE_ANCHORED_OUTSIDE_CP,
    ),
    # --- §24.1.C — 1 inheritance-composition namespace (NOT D6 §1.2 ingest) --
    NamespaceExport(
        namespace_name="routing.*",
        attribute_count=4,
        source_unit=UnitId("U-CP-01"),
        ingestion_target=_D6_1_5,
        sub_section_authority="C-CP-24 §24.1.C",
        source_authority_posture=_OWNED,
    ),
)
"""The CP-axis namespace export manifest — 11 entries (6 §24.1.A + 4 §24.1.B +
1 §24.1.C), C-CP-24 §24.1 verbatim (as re-tabled at CP v1.117, B-144 venue A,
and column-ratified at CP v1.118, B-153). 75 CP-axis attributes total.

**What the per-row `attribute_count` is, and is not (register row `B-126`).** It
reports the count DECLARED for that namespace, which is not the same as the
count that reaches the wire. `retry.*` is the live case: this manifest and
C-CP-03 §3.5 v1.3 both declare 6, but 10 distinct `retry.`-prefixed keys are
set by producers. The sum below is therefore a declared total, not a
cardinality guarantee over the namespaces it names.
"""

#: Total CP-axis attribute count exported to the OD plan Session 4 D6 — the
#: §24.1 (42 + 29 + 4) = 75 sum (acceptance #6). All four ratified count
#: amendments (`retry.*` 4 -> 6 at C-CP-03 §3.5 v1.3; `harness.breaker.*`
#: 7 -> 9 at OD spec v1.32, B-19-BREAKER-AMBIENT-ATTRS; `engine.*` 3 -> 4 at
#: C-CP-09 §9.1 v1.3; `hitl.*` 4 -> 11 at C-CP-24 §24.1 v1.118, B-153) are
#: carried in §24.1 itself, so the declared table and this sum agree. The sum counts
#: `engine.replay_disposition` under both `engine.*` and the §3.5 retry set
#: (a declared cross-namespace composition attribute) — it is a sum of
#: declared row counts, not a distinct-key cardinality.
CP_EXPORTED_ATTRIBUTE_COUNT: int = sum(e.attribute_count for e in CP_NAMESPACE_EXPORT_MANIFEST)
