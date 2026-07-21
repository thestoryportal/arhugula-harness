"""`harness-inspect` §13.5 audit-signature verification inputs (U-RT-138).

Implements Runtime spec v1.101 NEW §13.5 (C-RT-13 verification inputs rows
1-7) + the §13 exit-contract amendment, per Runtime plan v2.49 §1.5.
Verification SEMANTICS are OD-owned (OD v1.34 §21.2.2 — the U-OD-55
verifier) and reach this surface through the §20.3.1 CP blocking walk
(`harness_cp.audit_walk_verification.run_blocking_audit_walk`) behind the
composition-root adapter (`lifecycle/audit_walk_adapter.OdVerifierWalkAdapter`)
— THIS module is the first production injection site of the CP v2.38 §3
mediation seam.

**Engagement predicate.** The audit-verification disposition governs when
the inspection ENCOUNTERS the audit surface: any of the four audit inputs
(`--audit-sidecar` / `--expected-tenant` / `--signing-key-map` /
`--cutover-record`) is supplied, OR the resolved sidecar path exists. A
deployment with no audit sidecar and no audit inputs makes no audit claim —
the pre-v1.101 ledger summary is unchanged for it. Once engaged:

- ABSENT the authoritative `--runtime-config` input → explicit `UNVERIFIED`
  with a NONZERO exit (fail-safe: the `RuntimeConfig` DEFAULT tier is
  SOLO_DEVELOPER, so an unconfigured MTC inspection must never silently
  pass — the tier is NEVER defaulted here; plan acc 2, codex round-6 P1).
- Config shows a sub-MTC tier + NO verification inputs → the pre-v1.101
  hash-only inspection behavior PRESERVED VERBATIM (the caller proceeds
  with the plain summary).
- Config shows MULTI_TENANT_COMPLIANCE → backend inputs
  (`--signing-key-map` + `--cutover-record`) REQUIRED, or the result is an
  explicit `UNVERIFIED` disposition with a NONZERO exit — silent hash-only
  success PROHIBITED (OD v1.34 §21.2.2 row 8).
- ANY sidecar row present WITHOUT a cutover record → `UNVERIFIED` nonzero:
  era is NEVER observation-inferred (codex rounds 24/25 — tenant-tagged
  v1.33 four-tuple history is observationally indistinguishable from
  five-tuple rows). A greenfield v1.101+ ledger carries an AUTHENTICATED
  EMPTY record emitted at initialization.
- A cutover record failing authentication against the operator-PINNED
  `audit_cutover_record_key_id` is REJECTED with a typed error — never
  downgraded to absent-record fallback (a forged record must never drive
  exemption, era selection, or retagging; plan codex round-3 P1). The
  inspection ITSELF enforces the pinned-key physical distinctness and the
  mapping-authoritative algorithm (codex round-42): a valid record signed
  by an ordinary row key, or carrying an algorithm differing from the
  pinned mapping entry, is REJECTED at inspect.
- Reverse coverage (codex round-52): a sidecar row absent from the IS
  ledger's `audit:` refs is SURPLUS and fails the MTC audit; migrated
  history whose IS action ids remain `audit:_single:<hash>` matches through
  the record-derived alias projection (codex round-53) and is NOT surplus.

**Read-only invariant (§13 / plan acc 3):** every input is opened
read-only; this module writes nothing.

**Key map form (plan acc 4 implementation discretion):** `--signing-key-map`
is a JSON object keyed `"<algorithm>:<key_id>"`, each value an
`AuditSigningConfig`-shaped backend spec consumed by
`config.audit_signing.make_audit_signing_backend` — the operator-supplied
form of the §21.2.2 row-1 PER-ROW resolver (NOT a single backend).
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from harness_core import PersonaTier
from harness_cp.audit_walk_verification import (
    BlockingAuditWalkResult,
    WalkResultKind,
    run_blocking_audit_walk,
)
from harness_od.audit_cutover_record import (
    AuditCutoverRecord,
    verify_cutover_record_signature,
)
from harness_od.audit_ledger_types import AuditLedgerEntry, SignatureAlgorithm
from harness_od.per_family_audit_verification import VerificationBackendKeyUnknownError

from harness_runtime.lifecycle.audit_walk_adapter import OdVerifierWalkAdapter

if TYPE_CHECKING:
    from harness_cp.f5_signing_key_resolution import SigningBackend

    from harness_runtime.types import RuntimeConfig

__all__ = [
    "AUDIT_UNVERIFIED_FAIL_CLASS",
    "AuditInspectionOutcome",
    "ForgedCutoverRecordError",
    "run_audit_inspection",
]

AUDIT_UNVERIFIED_FAIL_CLASS = "RT-FAIL-AUDIT-UNVERIFIED"

#: §13 exit-contract amendment (plan acc 4 discretion): 0 stays success; 2
#: stays RT-FAIL-INSPECT-PATH; 3 = explicit UNVERIFIED disposition; 4 =
#: verification RAN and the audit FAILED.
EXIT_AUDIT_UNVERIFIED = 3
EXIT_AUDIT_FAILED = 4


class ForgedCutoverRecordError(Exception):
    """A cutover record failed authentication against the PINNED key — a
    TYPED rejection, never downgraded to absent-record fallback (a forged
    record must never drive exemption, era selection, or retagging)."""


@dataclass(frozen=True)
class AuditInspectionOutcome:
    """The §13.5 verification disposition + report material."""

    disposition: str  # "verified" | "unverified" | "failed" | "hash-only-preserved"
    exit_code: int
    detail: str
    walk_result: BlockingAuditWalkResult | None = None
    surplus_rows: tuple[str, ...] = ()
    report: dict[str, Any] = field(default_factory=lambda: dict[str, Any]())

    def as_report(self) -> dict[str, Any]:
        base: dict[str, Any] = {
            "audit_verification": {
                "disposition": self.disposition,
                "detail": self.detail,
                **(
                    {"fail_class": AUDIT_UNVERIFIED_FAIL_CLASS}
                    if self.disposition == "unverified"
                    else {}
                ),
                **({"surplus_rows": list(self.surplus_rows)} if self.surplus_rows else {}),
            }
        }
        if self.walk_result is not None:
            base["audit_verification"]["walk"] = {
                "kind": self.walk_result.kind.value,
                "detail": self.walk_result.detail,
                "signature_dispositions": dict(self.walk_result.signature_dispositions),
                "baseline_divergences": list(self.walk_result.baseline_divergences),
            }
        base["audit_verification"].update(self.report)
        return base


def _unverified(detail: str) -> AuditInspectionOutcome:
    return AuditInspectionOutcome(
        disposition="unverified",
        exit_code=EXIT_AUDIT_UNVERIFIED,
        detail=f"{AUDIT_UNVERIFIED_FAIL_CLASS}: {detail}",
    )


@dataclass(frozen=True)
class _SidecarContent:
    entries: tuple[AuditLedgerEntry, ...]
    observed_identities: tuple[tuple[str, str], ...]
    row_key_ids: frozenset[str]


def _read_sidecar(sidecar_path: Path) -> _SidecarContent:
    """Read-only parse of the `audit-entries.jsonl` sidecar.

    Full rows are `{"tenant_tag": str, "entry": {...}}`; baseline rows carry
    `legacy_baseline` and contribute an observed identity only. An
    unparseable row raises `ValueError` (fail-closed — verification cannot
    run over unprovable history).
    """
    entries: list[AuditLedgerEntry] = []
    observed: list[tuple[str, str]] = []
    key_ids: set[str] = set()
    for line_number, line in enumerate(
        sidecar_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        parsed: object = json.loads(line)
        if not isinstance(parsed, dict):
            raise ValueError(f"sidecar line {line_number} is not a JSON object")
        row = cast("dict[str, object]", parsed)
        if "legacy_baseline" in row:
            tag = row.get("tenant_tag")
            entry_hash = row.get("entry_hash")
            if isinstance(tag, str) and isinstance(entry_hash, str):
                observed.append((tag, entry_hash))
            continue
        entry_obj = row.get("entry")
        tag = row.get("tenant_tag")
        if not isinstance(entry_obj, dict) or not isinstance(tag, str):
            raise ValueError(f"sidecar line {line_number} lacks tenant_tag/entry")
        entry = AuditLedgerEntry.model_validate(entry_obj)
        entries.append(entry)
        observed.append((tag, entry.entry_hash))
        key_ids.add(entry.signature_attrs.audit_signature_key_id)
    return _SidecarContent(
        entries=tuple(entries),
        observed_identities=tuple(observed),
        row_key_ids=frozenset(key_ids),
    )


def _load_key_map(path: Path) -> dict[str, SigningBackend]:
    """Parse the operator key map into per-`(algorithm, key_id)` backends."""
    from harness_runtime.config.audit_signing import make_audit_signing_backend
    from harness_runtime.types import AuditSigningConfig

    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("--signing-key-map must be a JSON object")
    backends: dict[str, SigningBackend] = {}
    for map_key, spec in cast("dict[str, object]", raw).items():
        if ":" not in map_key:
            raise ValueError(f"key-map key {map_key!r} must be '<algorithm>:<key_id>'")
        backend = make_audit_signing_backend(AuditSigningConfig.model_validate(spec))
        if backend is None:
            raise ValueError(
                f"key-map entry {map_key!r} resolves to no backend "
                f'(backend="none" is not a verification backend)'
            )
        backends[map_key] = backend
    return backends


def _load_authenticated_record(
    record_path: Path,
    *,
    pinned_key_id: str | None,
    ledger_binding_id: str | None,
    key_map: dict[str, SigningBackend],
    row_key_ids: frozenset[str],
) -> tuple[AuditCutoverRecord, bytes]:
    """Load + authenticate the cutover record — typed rejection, never
    absent-record fallback."""
    lines = record_path.read_text(encoding="utf-8").splitlines()
    if len(lines) != 2:
        raise ForgedCutoverRecordError(
            f"cutover record {record_path} must be exactly 2 lines "
            f"(record + signature), found {len(lines)}"
        )
    record_line, signature_line = lines
    try:
        record = AuditCutoverRecord.model_validate_json(record_line)
        signature = bytes.fromhex(signature_line)
    except (ValueError, Exception) as exc:
        raise ForgedCutoverRecordError(
            f"cutover record {record_path} is unparseable: {exc}"
        ) from exc

    if pinned_key_id is None:
        raise ForgedCutoverRecordError(
            "no pinned audit_cutover_record_key_id in the supplied runtime "
            "config — the pinned key is the ONLY v1.101 anchor mode; a "
            "record cannot be trusted without it"
        )
    if record.key_id != pinned_key_id:
        raise ForgedCutoverRecordError(
            f"cutover record key_id={record.key_id!r} disagrees with the "
            f"pinned audit_cutover_record_key_id={pinned_key_id!r}"
        )
    # Pinned-key physical distinctness at inspect (codex round-42): a valid
    # record signed by an ordinary ROW key is rejected.
    if record.key_id in row_key_ids:
        raise ForgedCutoverRecordError(
            f"cutover record key_id={record.key_id!r} also signs ordinary "
            f"sidecar rows — the record key MUST be physically distinct from "
            f"every row-signing key"
        )
    if ledger_binding_id is not None and record.ledger_binding_id != ledger_binding_id:
        raise ForgedCutoverRecordError(
            f"cutover record ledger_binding_id={record.ledger_binding_id!r} "
            f"disagrees with the configured audit_ledger_binding_id="
            f"{ledger_binding_id!r}"
        )
    map_key = f"{record.algorithm.value}:{record.key_id}"
    backend = key_map.get(map_key)
    if backend is None:
        # Mapping-authoritative algorithm (codex round-42): an algorithm
        # differing from the pinned mapping entry means no mapping row
        # matches — rejected, never trusted on the record's own metadata.
        raise ForgedCutoverRecordError(
            f"no key-map entry for {map_key!r} — the algorithm authority is "
            f"the mapping, never the record's own metadata"
        )
    if not verify_cutover_record_signature(record, signature, backend=backend):
        raise ForgedCutoverRecordError(
            f"cutover record {record_path} failed signature verification "
            f"against the pinned key — tampered, forged, or signed under "
            f"different key material"
        )
    return record, signature


def _surplus_rows(
    observed_identities: tuple[tuple[str, str], ...],
    ledger_audit_refs: frozenset[str],
    record: AuditCutoverRecord,
) -> tuple[str, ...]:
    """Reverse coverage (codex rounds 52/53): sidecar rows absent from the
    IS ledger's `audit:` refs are SURPLUS — with the record-derived alias
    projection so migrated history (IS ids still `audit:_single:<hash>`)
    matches and is NOT reported surplus."""
    recorded_source_tags = {row.entry_hash: row.source_tag for row in record.rows}
    surplus: list[str] = []
    for tag, entry_hash in observed_identities:
        current_ref = f"audit:{tag}:{entry_hash}"
        if current_ref in ledger_audit_refs:
            continue
        source_tag = recorded_source_tags.get(entry_hash)
        if source_tag is not None and f"audit:{source_tag}:{entry_hash}" in ledger_audit_refs:
            continue  # migrated row — matches through the alias projection
        surplus.append(current_ref)
    return tuple(surplus)


def run_audit_inspection(
    *,
    sidecar_path: Path,
    runtime_config: RuntimeConfig | None,
    expected_tenant: str | None,
    key_map_path: Path | None,
    cutover_record_path: Path | None,
    ledger_audit_refs: frozenset[str],
) -> AuditInspectionOutcome:
    """The §13.5 audit-verification disposition (caller pre-checks the
    engagement predicate and resolves the IS ledger's `audit:` refs)."""
    if runtime_config is None:
        return _unverified(
            "no authoritative --runtime-config supplied — the inspector "
            "cannot distinguish MULTI_TENANT_COMPLIANCE's mandatory posture "
            "from lower tiers (the config DEFAULT tier is SOLO_DEVELOPER and "
            "is never assumed here); explicit UNVERIFIED, nonzero exit"
        )

    is_mtc = runtime_config.persona_tier == PersonaTier.MULTI_TENANT_COMPLIANCE
    have_backend_inputs = key_map_path is not None and cutover_record_path is not None

    if not have_backend_inputs:
        if is_mtc:
            return _unverified(
                "MULTI_TENANT_COMPLIANCE inspection requires --signing-key-map "
                "AND --cutover-record — silent hash-only success is prohibited "
                "(OD v1.34 §21.2.2 row 8)"
            )
        return AuditInspectionOutcome(
            disposition="hash-only-preserved",
            exit_code=0,
            detail=(
                "sub-MTC tier per the supplied authoritative config, no "
                "verification inputs — pre-v1.101 hash-only inspection "
                "behavior preserved verbatim"
            ),
        )

    try:
        sidecar = (
            _read_sidecar(sidecar_path)
            if sidecar_path.is_file()
            else _SidecarContent(entries=(), observed_identities=(), row_key_ids=frozenset())
        )
    except (ValueError, OSError) as exc:
        return _unverified(f"audit sidecar {sidecar_path} unreadable/unparseable: {exc}")

    try:
        key_map = _load_key_map(key_map_path)  # type: ignore[arg-type]  # narrowed above
    except (ValueError, OSError) as exc:
        return _unverified(f"--signing-key-map unusable: {exc}")

    # The record is REQUIRED whenever ANY row exists (era never inferred);
    # its authentication failures are TYPED and never absent-fallback.
    record, signature = _load_authenticated_record(
        cutover_record_path,  # type: ignore[arg-type]  # narrowed above
        pinned_key_id=runtime_config.audit_cutover_record_key_id,
        ledger_binding_id=runtime_config.audit_ledger_binding_id,
        key_map=key_map,
        row_key_ids=sidecar.row_key_ids,
    )

    surplus = _surplus_rows(sidecar.observed_identities, ledger_audit_refs, record)
    if surplus and is_mtc:
        return AuditInspectionOutcome(
            disposition="failed",
            exit_code=EXIT_AUDIT_FAILED,
            detail=(
                f"{len(surplus)} SURPLUS sidecar row(s) absent from the IS "
                f"ledger's audit: refs — a copied/planted row fails the MTC "
                f"audit (reverse coverage)"
            ),
            surplus_rows=surplus,
        )

    def resolver(algo: SignatureAlgorithm, key_id: str) -> object:
        backend = key_map.get(f"{algo.value}:{key_id}")
        if backend is None:
            raise VerificationBackendKeyUnknownError(
                f"no key-map entry for ({algo.value!r}, {key_id!r})"
            )
        return backend

    adapter = OdVerifierWalkAdapter(
        backend_resolver=resolver,  # type: ignore[arg-type]  # SigningBackend Protocol
        cutover_record=record,
        cutover_record_signature=signature,
        expected_cutover_record_key_id=runtime_config.audit_cutover_record_key_id,
        ledger_binding_id=runtime_config.audit_ledger_binding_id,
    )
    walk = run_blocking_audit_walk(
        sidecar.entries,
        verifier=adapter,
        tenant_scope=expected_tenant,
        observed_baseline_identities=sidecar.observed_identities,
    )
    if walk.kind is WalkResultKind.PASSED:
        return AuditInspectionOutcome(
            disposition="verified", exit_code=0, detail=walk.detail, walk_result=walk
        )
    if walk.kind is WalkResultKind.FAILED:
        return AuditInspectionOutcome(
            disposition="failed",
            exit_code=EXIT_AUDIT_FAILED,
            detail=walk.detail,
            walk_result=walk,
        )
    return AuditInspectionOutcome(
        disposition="unverified",
        exit_code=EXIT_AUDIT_UNVERIFIED,
        detail=f"{AUDIT_UNVERIFIED_FAIL_CLASS}: {walk.detail}",
        walk_result=walk,
    )
