"""Schema-attribute utility enums — U-CP-00b.

Declares `AttributeValueType` and `Cardinality` — the value-type and
cardinality discriminators the CP plan uses to type its `…AttributeSchema`
records (the per-namespace attribute-schema records at U-CP-01/07/11/21/31/37/
46/47). They are plan-introduced auxiliary enums: no single CP spec contract
enumerates them — the unit is traced to the *aggregate* of the seven
attribute-schema contracts (C-CP-01 §1.4, C-CP-03 §3.5, C-CP-07, C-CP-10 §10,
C-CP-18 §16, C-CP-20 §20.4, C-CP-21 §21.5), each of which characterizes
attribute value-types and cardinality in prose.

U-CP-00b is a CP-axis foundational carrier (L0, beside U-CP-00), CP-axis-owned
(operator decision D3 — all consumers are CP-axis units; no cross-axis
sharing, so it resides in `harness-cp`, not `harness-core`).

The member sets are byte-exact relocations of the enums previously declared
inline at U-CP-01 (CP plan v2.4-conformed body lines 175-176). The CP plan
commits the member *sets* only — it assigns no string values; the
SCREAMING_SNAKE_CASE names and lowercase string values here are a Python-stack
naming convention (`StrEnum`, consistent with the other CP-axis enums).

**v2.7 split note.** CP plan v2.6 §2.0b also bundled 9 "CP-owned structured
shared types" into U-CP-00b as name-only signatures. Those were under-specified
at plan grade and are deferred to a future CP plan revision per
`.harness/class_1_tension_u_cp_00b_structured_types.md`; U-CP-00b is the
2-enum carrier only.

Authority: Implementation_Plan_Control_Plane_v2_7.md §2.0b U-CP-00b;
Implementation_Plan_Control_Plane_v2_4.md U-CP-01 body lines 175-176 (the
relocated inline enums).
"""

from __future__ import annotations

from enum import StrEnum


class AttributeValueType(StrEnum):
    """The 5 attribute value-type discriminators (U-CP-00b).

    Closed at cardinality 5. Member set byte-exact with the enum relocated from
    U-CP-01 (CP plan v2.4 body line 175): `STRING | INT | FLOAT | BOOL |
    ENUM_REF`.
    """

    STRING = "string"
    INT = "int"
    FLOAT = "float"
    BOOL = "bool"
    ENUM_REF = "enum_ref"


class Cardinality(StrEnum):
    """The 4 attribute-cardinality discriminators (U-CP-00b).

    Closed at cardinality 4. Member set byte-exact with the enum relocated from
    U-CP-01 (CP plan v2.4 body line 176): `LOW | MEDIUM | HIGH | PER_REQUEST`.
    """

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    PER_REQUEST = "per_request"
