"""CP-axis namespace export manifest — U-CP-54.

Implements C-CP-24 §24.1.A/§24.1.B/§24.1.C (the CP-axis namespace export
manifest). Declares the `NamespaceExport` record, the `SourceAuthorityPosture`
and `IngestionTarget` enums, and the `CP_NAMESPACE_EXPORT_MANIFEST` constant —
11 namespace-export references the OD plan Session 4 D6 ingests.

The manifest is **descriptive, not declarative** (acceptance #9): the namespace
declarations themselves live at the source units (U-CP-01/07/11/21/31/46/47);
this manifest exports references only. 11 namespaces — 6 specialization-layer
(§24.1.A), 4 F3-lifecycle-event (§24.1.B), 1 inheritance-composition (§24.1.C)
— 65 CP-axis attributes total (34 + 27 + 4; was stated as 63 until `B-126`
recomputed it — `harness.breaker.*` grew 7 -> 9 at CP spec v1.32).

Authority: Implementation_Plan_Control_Plane_v2_1.md §2.9 U-CP-54 (preserved
verbatim through v2.9); Spec_Control_Plane_v1_2.md §24 C-CP-24
§24.1.A/§24.1.B/§24.1.C.
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
        namespace_name="engine.*",
        attribute_count=3,
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
        namespace_name="hitl.*",
        attribute_count=4,
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
        # 4 is the §24.1.B DECLARED-SUBSET figure, not a namespace cardinality:
        # C-CP-03 §3.5 carries 6 at v1.3 and the wire carries 10 (B-126). See
        # `retry_fallback_namespace.RETRY_WIRE_REGISTER`. Changing this bumps
        # the export sum — a contract-count change, deliberately NOT done here.
        namespace_name="retry.*",
        attribute_count=4,
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
        attribute_count=9,  # v1.32: +cause +cooldown_ms (B-19-BREAKER-AMBIENT-ATTRS)
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
1 §24.1.C), C-CP-24 §24.1 verbatim. 65 CP-axis attributes total.

**What the per-row `attribute_count` is, and is not (register row `B-126`).** It
reports the count DECLARED for that namespace, which is not the same as the
count that reaches the wire. `retry.*` is the live case: this manifest reports 4,
C-CP-03 §3.5 declares 6 at v1.3, and 10 distinct `retry.`-prefixed keys are set
by producers. The sum below is therefore a declared-subset total, not a
cardinality guarantee over the namespaces it names.
"""

#: Total CP-axis attribute count exported to the OD plan Session 4 D6 — the
#: §24.1 (34 + 27 + 4) = 65 sum (acceptance #6). The 65 is a DERIVED sum, so
#: this arithmetic is a reader's aid: §24.1.B is 27, not the 25 its v1.2 rows
#: total, because `harness.breaker.*` grew 7 -> 9 at CP spec v1.32
#: (B-19-BREAKER-AMBIENT-ATTRS) while §24.1.B's own table was never re-tabled.
CP_EXPORTED_ATTRIBUTE_COUNT: int = sum(e.attribute_count for e in CP_NAMESPACE_EXPORT_MANIFEST)
