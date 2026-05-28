"""U-RT-104 — `WorkflowManifestLoader` for YAML / TOML workflow manifests.

Implements C-RT-30 per runtime spec v1.36 §14.19 + SF-1 §3 + §4. Lands the
loader skeleton: file-extension dispatch (`.yaml` / `.yml` → strictyaml,
`.toml` → tomllib stdlib), 8 typed exceptions, intermediate Pydantic carrier
projecting to the SF-1 §3.1 schema body, + 9 invariants per spec §14.19.4.

Per the v1.36 canonical-reading amendment, the deployment-surface-keyed
engine_class admissibility check defers to the runtime caller (U-RT-106).
U-CP-22 workload-keyed topology admissibility runs at load-time per AC #12.

Per plan v2.32 §1.2, U-RT-104 AC #11 reframes to enum-validity only (covered
by AC #9). U-RT-105 will extend `load()` to return a full `WorkflowObject`
Protocol-conformant value; v1.36 lands the intermediate `WorkflowManifest`
carrier shape.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any, ClassVar, cast

import strictyaml  # pyright: ignore[reportMissingTypeStubs]
from harness_core.persona_tier import PersonaTier
from harness_core.workload_class import WorkloadClass
from harness_cp.engine_class import EngineClass
from harness_cp.gate_level_rule import GateLevel
from harness_cp.per_workload_class_topology import (
    is_topology_permitted_for_workload,
)
from harness_cp.topology_pattern import TopologyPattern
from harness_cp.workflow_driver_types import StepKind
from pydantic import BaseModel, ConfigDict, ValidationError

__all__ = [
    "ManifestAdmissibilityError",
    "ManifestEnumValueError",
    "ManifestParseError",
    "ManifestSchemaError",
    "ManifestStepIDCollisionError",
    "MANIFEST_VERSION_V1",
    "SUPPORTED_MANIFEST_EXTENSIONS",
    "UnsupportedManifestFormatError",
    "UnsupportedManifestVersionError",
    "WorkflowManifest",
    "WorkflowManifestLoadError",
    "WorkflowManifestLoader",
]


MANIFEST_VERSION_V1 = 1
SUPPORTED_MANIFEST_EXTENSIONS: frozenset[str] = frozenset({".yaml", ".yml", ".toml"})


# ---------------------------------------------------------------------------
# Typed exception taxonomy (spec v1.36 §14.19.2)
# ---------------------------------------------------------------------------


class WorkflowManifestLoadError(Exception):
    """Base for the 7 typed exceptions; all CLI errors map at §14.18.4."""

    FAIL_CLASS: ClassVar[str] = "RT-FAIL-CLI-MANIFEST-LOAD"

    def __init__(self, reason: str, *, source: str | None = None) -> None:
        self.reason = reason
        self.source = source
        suffix = f" [source={source}]" if source else ""
        super().__init__(f"{self.FAIL_CLASS}: {reason}{suffix}")


class UnsupportedManifestFormatError(WorkflowManifestLoadError):
    FAIL_CLASS: ClassVar[str] = "RT-FAIL-CLI-MANIFEST-FORMAT-UNSUPPORTED"


class UnsupportedManifestVersionError(WorkflowManifestLoadError):
    FAIL_CLASS: ClassVar[str] = "RT-FAIL-CLI-MANIFEST-VERSION-UNSUPPORTED"


class ManifestParseError(WorkflowManifestLoadError):
    FAIL_CLASS: ClassVar[str] = "RT-FAIL-CLI-MANIFEST-PARSE"


class ManifestSchemaError(WorkflowManifestLoadError):
    FAIL_CLASS: ClassVar[str] = "RT-FAIL-CLI-MANIFEST-SCHEMA"


class ManifestEnumValueError(WorkflowManifestLoadError):
    FAIL_CLASS: ClassVar[str] = "RT-FAIL-CLI-MANIFEST-ENUM-VALUE"


class ManifestStepIDCollisionError(WorkflowManifestLoadError):
    FAIL_CLASS: ClassVar[str] = "RT-FAIL-CLI-MANIFEST-STEP-ID-COLLISION"


class ManifestAdmissibilityError(WorkflowManifestLoadError):
    """Topology admissibility per U-CP-22; engine_class admissibility per
    U-RT-106 caller (NOT raised by this loader at v1.36, per fork doc β)."""

    FAIL_CLASS: ClassVar[str] = "RT-FAIL-CLI-MANIFEST-ADMISSIBILITY"


# ---------------------------------------------------------------------------
# Intermediate Pydantic carrier (SF-1 §3.1 shape; not WorkflowManifestEntry)
# ---------------------------------------------------------------------------


class _ModelBindingSection(BaseModel):
    """`default_model_binding` table from SF-1 §3.1."""

    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)

    provider: str
    model: str


class _StepEntry(BaseModel):
    """Single `steps[]` entry from SF-1 §3.1."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    step_id: str
    step_kind: StepKind
    step_payload: dict[str, Any]


class _WorkflowSection(BaseModel):
    """`workflow` table from SF-1 §3.1.

    Optional structured fields (`layer_budgets`, `fallback_chain`,
    `hitl_placements`, `sub_agent_briefs`, `per_step_overrides`) are kept
    opaque at the intermediate-carrier layer — full projection to the CP
    `WorkflowManifestEntry` shape lands at U-RT-105. Enum fields validate
    eagerly per spec §14.19.4 invariants 2 + 3.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    workflow_id: str
    workload_class: WorkloadClass
    persona_tier: PersonaTier
    engine_class: EngineClass
    topology_pattern: TopologyPattern
    entry_version: int = 1
    default_gate_level: GateLevel | None = None
    layer_budgets: list[Any] = []
    fallback_chain: dict[str, Any] | None = None
    hitl_placements: list[Any] = []
    sub_agent_briefs: list[Any] | None = None
    per_step_overrides: dict[str, Any] = {}


class WorkflowManifest(BaseModel):
    """Intermediate loader-internal carrier projecting the SF-1 §3.1 schema.

    Frozen + ``extra=forbid`` gives closed-schema (invariant 1), eager
    validation (invariant 2), and idempotency (invariant 7) — equal inputs
    produce ``__eq__``-equal carriers.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: int
    workflow: _WorkflowSection
    default_model_binding: _ModelBindingSection
    steps: list[_StepEntry]


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


class WorkflowManifestLoader:
    """Loads a YAML / TOML workflow manifest into a :class:`WorkflowManifest`.

    U-RT-105 will extend ``load()`` to return a full ``WorkflowObject``
    Protocol-conformant value; U-RT-104 lands the intermediate carrier shape
    and the 7 typed exception surface.
    """

    @classmethod
    def load(cls, path: Path) -> WorkflowManifest:
        """Parse + validate the manifest at ``path``.

        Raises one of the 7 :class:`WorkflowManifestLoadError` subclasses.
        On success, returns a frozen :class:`WorkflowManifest` carrier
        satisfying spec §14.19.4 invariants 1-9 except for engine_class
        deployment-surface admissibility (deferred to U-RT-106 per fork
        doc β).
        """
        document = cls._parse(path)
        cls._check_version(document, source=str(path))
        carrier = cls._build_carrier(document, source=str(path))
        cls._check_step_id_uniqueness(carrier, source=str(path))
        cls._check_topology_admissibility(carrier, source=str(path))
        return carrier

    # ---------- parse ----------

    @classmethod
    def _parse(cls, path: Path) -> dict[str, Any]:
        suffix = path.suffix.lower()
        if suffix not in SUPPORTED_MANIFEST_EXTENSIONS:
            raise UnsupportedManifestFormatError(
                f"unsupported extension {suffix!r}; expected one of "
                f"{sorted(SUPPORTED_MANIFEST_EXTENSIONS)}",
                source=str(path),
            )
        try:
            raw_bytes = path.read_bytes()
        except OSError as exc:
            raise ManifestParseError(
                f"manifest file read failed: {exc}",
                source=str(path),
            ) from exc
        if suffix == ".toml":
            return cls._parse_toml(raw_bytes, source=str(path))
        return cls._parse_yaml(raw_bytes, source=str(path))

    @staticmethod
    def _parse_yaml(raw_bytes: bytes, source: str) -> dict[str, Any]:
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ManifestParseError(
                f"manifest is not valid UTF-8: {exc}",
                source=source,
            ) from exc
        try:
            parsed = cast(
                Any,
                strictyaml.dirty_load(  # pyright: ignore[reportUnknownMemberType]
                    text, allow_flow_style=True
                ),
            )
        except strictyaml.YAMLError as exc:
            raise ManifestParseError(
                f"YAML parse error: {exc}",
                source=source,
            ) from exc
        data = parsed.data
        if not isinstance(data, dict):
            raise ManifestSchemaError(
                "top-level YAML value must be a mapping",
                source=source,
            )
        return dict(cast(dict[str, Any], data))

    @staticmethod
    def _parse_toml(raw_bytes: bytes, source: str) -> dict[str, Any]:
        try:
            text = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ManifestParseError(
                f"manifest is not valid UTF-8: {exc}",
                source=source,
            ) from exc
        try:
            return tomllib.loads(text)
        except tomllib.TOMLDecodeError as exc:
            raise ManifestParseError(
                f"TOML parse error: {exc}",
                source=source,
            ) from exc

    # ---------- version check ----------

    @classmethod
    def _check_version(cls, document: dict[str, Any], *, source: str) -> None:
        if "version" not in document:
            raise UnsupportedManifestVersionError(
                "required field 'version' is absent at top level",
                source=source,
            )
        raw_version = document["version"]
        # YAML scalars from strictyaml.dirty_load may arrive as str even when
        # the source said `version: 1` — coerce-via-int once and compare.
        try:
            version = int(str(raw_version))
        except (ValueError, TypeError) as exc:
            raise UnsupportedManifestVersionError(
                f"'version' must be the integer {MANIFEST_VERSION_V1}; got "
                f"{raw_version!r}",
                source=source,
            ) from exc
        if version != MANIFEST_VERSION_V1:
            raise UnsupportedManifestVersionError(
                f"'version' must equal {MANIFEST_VERSION_V1}; got {version}",
                source=source,
            )
        document["version"] = version  # normalize for downstream Pydantic

    # ---------- carrier construction ----------

    @classmethod
    def _build_carrier(
        cls, document: dict[str, Any], *, source: str
    ) -> WorkflowManifest:
        # Coerce YAML-typed scalars at the boundary. strictyaml.dirty_load
        # returns strings for non-flow-style scalars; TOML preserves types.
        cls._coerce_int_fields(document, source=source)
        try:
            return WorkflowManifest.model_validate(document)
        except ValidationError as exc:
            raise cls._project_validation_error(exc, source=source) from exc

    @staticmethod
    def _coerce_int_fields(document: dict[str, Any], *, source: str) -> None:
        """Coerce known integer fields when YAML scalars arrived as strings.

        Currently only ``workflow.entry_version`` needs explicit coercion;
        version was handled at ``_check_version``. step_payload scalars stay
        opaque per AC #14.19.4 invariant 9 (JSON-serializability at U-RT-105).
        """
        workflow_section = document.get("workflow")
        if not isinstance(workflow_section, dict):
            return
        workflow_dict = cast(dict[str, Any], workflow_section)
        if "entry_version" in workflow_dict:
            raw = workflow_dict["entry_version"]
            if isinstance(raw, str):
                try:
                    workflow_dict["entry_version"] = int(raw)
                except ValueError as exc:
                    raise ManifestSchemaError(
                        f"'workflow.entry_version' must be an integer; got {raw!r}",
                        source=source,
                    ) from exc

    @staticmethod
    def _project_validation_error(
        exc: ValidationError, *, source: str
    ) -> WorkflowManifestLoadError:
        """Discriminate Pydantic errors → typed taxonomy.

        StrEnum coercion failures map to ``ManifestEnumValueError`` (AC #9);
        any other validation failure (missing field, unknown field, type
        mismatch) maps to ``ManifestSchemaError`` (AC #6 / #7 / #8).
        """
        for err in exc.errors():
            err_type = err.get("type", "")
            if "enum" in err_type:
                location = ".".join(str(loc) for loc in err.get("loc", ()))
                raise ManifestEnumValueError(
                    f"invalid enum value at '{location}': {err.get('msg', '')}",
                    source=source,
                )
        return ManifestSchemaError(
            f"schema validation failed: {exc.errors()}",
            source=source,
        )

    # ---------- step-id uniqueness (invariant 4) ----------

    @staticmethod
    def _check_step_id_uniqueness(
        manifest: WorkflowManifest, *, source: str
    ) -> None:
        seen: dict[str, int] = {}
        for idx, step in enumerate(manifest.steps):
            if step.step_id in seen:
                raise ManifestStepIDCollisionError(
                    f"step_id {step.step_id!r} appears at steps[{seen[step.step_id]}] "
                    f"and steps[{idx}]; step_ids MUST be unique within a workflow",
                    source=source,
                )
            seen[step.step_id] = idx

    # ---------- topology admissibility (AC #12, U-CP-22) ----------

    @staticmethod
    def _check_topology_admissibility(
        manifest: WorkflowManifest, *, source: str
    ) -> None:
        if not is_topology_permitted_for_workload(
            manifest.workflow.topology_pattern,
            manifest.workflow.workload_class,
        ):
            raise ManifestAdmissibilityError(
                f"topology_pattern {manifest.workflow.topology_pattern.value!r} "
                f"is not admissible for workload_class "
                f"{manifest.workflow.workload_class.value!r} per U-CP-22 "
                f"is_topology_permitted_for_workload",
                source=source,
            )
