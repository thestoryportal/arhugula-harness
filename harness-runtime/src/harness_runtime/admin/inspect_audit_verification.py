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


_SINGLE_TAG = "_single"


@dataclass(frozen=True)
class _SidecarContent:
    tagged_entries: tuple[tuple[str, AuditLedgerEntry], ...]
    observed_identities: tuple[tuple[str, str], ...]
    baseline_identities: tuple[tuple[str, str], ...]
    row_key_ids: frozenset[str]

    @property
    def entries(self) -> tuple[AuditLedgerEntry, ...]:
        return tuple(entry for _, entry in self.tagged_entries)


def _read_sidecar(sidecar_path: Path) -> _SidecarContent:
    """Read-only parse of the `audit-entries.jsonl` sidecar.

    Full rows are `{"tenant_tag": str, "entry": {...}}`; baseline rows carry
    `legacy_baseline` and contribute an observed identity only. An
    unparseable row raises `ValueError` (fail-closed — verification cannot
    run over unprovable history).
    """
    entries: list[tuple[str, AuditLedgerEntry]] = []
    observed: list[tuple[str, str]] = []
    baseline: list[tuple[str, str]] = []
    key_ids: set[str] = set()
    seen_identities: set[tuple[str, str]] = set()

    def _claim_identity(tag: str, entry_hash: str, line_number: int) -> None:
        # The writer's membership index treats ANY duplicate
        # `(tenant_tag, entry_hash)` as external mutation — the read side
        # fails closed on the second occurrence (codex round-3 P1: coverage
        # uses sets and non-chained signatures verify independently, so a
        # duplicated row would otherwise still VERIFY).
        identity = (tag, entry_hash)
        if identity in seen_identities:
            raise ValueError(
                f"sidecar line {line_number}: duplicate identity {identity!r} "
                f"— the writer never appends a duplicate; treating as "
                f"external mutation"
            )
        seen_identities.add(identity)

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
            # The writer's actual shape (`adopt_legacy_is_refs`, mirrored by
            # the sidecar folder at `audit_writer.py`):
            # `{"legacy_baseline": [[tag, hash], ...]}` — ONE row carrying
            # an ARRAY of source-identity pairs (codex round-1 P1 on this
            # leg: the previous per-row tenant_tag/entry_hash reading
            # silently dropped every baseline pair). These are BASELINE-ONLY
            # observations — the shape the OD verifier's §21.2.2 row-6
            # cross-check consumes; full-entry rows are NOT baselines.
            pairs_obj = row["legacy_baseline"]
            if not isinstance(pairs_obj, list):
                raise ValueError(
                    f"sidecar line {line_number}: legacy_baseline must be an "
                    f"array of [tag, hash] pairs"
                )
            for pair in cast("list[object]", pairs_obj):
                if (
                    not isinstance(pair, list)
                    or len(cast("list[object]", pair)) != 2
                    or not all(isinstance(part, str) for part in cast("list[object]", pair))
                ):
                    raise ValueError(
                        f"sidecar line {line_number}: malformed legacy_baseline pair {pair!r}"
                    )
                tag_str, hash_str = cast("list[str]", pair)
                _claim_identity(tag_str, hash_str, line_number)
                observed.append((tag_str, hash_str))
                baseline.append((tag_str, hash_str))
            continue
        entry_obj = row.get("entry")
        tag = row.get("tenant_tag")
        if not isinstance(entry_obj, dict) or not isinstance(tag, str):
            raise ValueError(f"sidecar line {line_number} lacks tenant_tag/entry")
        entry = AuditLedgerEntry.model_validate(entry_obj)
        _claim_identity(tag, entry.entry_hash, line_number)
        entries.append((tag, entry))
        observed.append((tag, entry.entry_hash))
        key_ids.add(entry.signature_attrs.audit_signature_key_id)
    return _SidecarContent(
        tagged_entries=tuple(entries),
        observed_identities=tuple(observed),
        baseline_identities=tuple(baseline),
        row_key_ids=frozenset(key_ids),
    )


def _load_key_map(path: Path) -> tuple[dict[str, SigningBackend], dict[str, str]]:
    """Parse the operator key map into per-`(algorithm, key_id)` backends.

    Also returns per-entry BACKING-MATERIAL fingerprints (the physical KMS
    ARN the logical `key_id` maps to, falling back to the whole canonical
    `key_arns` mapping) — codex round-2 P1 on this leg: the record-key
    physical-distinctness check must compare backing material, not logical
    `key_id` strings; two distinct ids aliasing one ARN share a key.
    """
    from harness_runtime.config.audit_signing import make_audit_signing_backend
    from harness_runtime.types import AuditSigningConfig

    raw: object = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("--signing-key-map must be a JSON object")
    backends: dict[str, SigningBackend] = {}
    materials: dict[str, str] = {}
    for map_key, spec in cast("dict[str, object]", raw).items():
        if ":" not in map_key:
            raise ValueError(f"key-map key {map_key!r} must be '<algorithm>:<key_id>'")
        config = AuditSigningConfig.model_validate(spec)
        backend = make_audit_signing_backend(config)
        if backend is None:
            raise ValueError(
                f"key-map entry {map_key!r} resolves to no backend "
                f'(backend="none" is not a verification backend)'
            )
        backends[map_key] = backend
        key_id = map_key.split(":", 1)[1]
        materials[map_key] = config.key_arns.get(key_id) or json.dumps(
            sorted(config.key_arns.items()), separators=(",", ":")
        )
    return backends, materials


def _load_authenticated_record(
    record_path: Path,
    *,
    pinned_key_id: str | None,
    ledger_binding_id: str | None,
    key_map: dict[str, SigningBackend],
    key_materials: dict[str, str],
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
    # BACKING-material distinctness (codex round-2 P1): two distinct logical
    # key_ids aliasing the same KMS ARN share one physical key — the record
    # trust anchor must be independent of every row-signing key's material.
    record_map_key = f"{record.algorithm.value}:{record.key_id}"
    # A persisted row key with NO key-map entry makes record/row physical
    # separation UNPROVABLE (codex round-3 P1: a record marking that row
    # placeholder_exempt skips signature resolution entirely, so nothing
    # else would surface the gap) — fail closed, matching bootstrap's
    # every-key-mapped validation.
    mapped_key_ids = {map_key.split(":", 1)[1] for map_key in key_materials}
    unmapped = sorted(row_key_ids - mapped_key_ids)
    if unmapped:
        raise ForgedCutoverRecordError(
            f"sidecar row-signing key(s) {unmapped!r} have no "
            f"--signing-key-map entry — record/row physical key separation "
            f"cannot be proven for unmapped persisted keys"
        )
    record_material = key_materials.get(record_map_key)
    row_materials = {
        material
        for map_key, material in key_materials.items()
        if map_key != record_map_key and map_key.split(":", 1)[1] in row_key_ids
    }
    if record_material is not None and record_material in row_materials:
        raise ForgedCutoverRecordError(
            f"cutover record key {record_map_key!r} shares backing key "
            f"material with a row-signing key — the record trust anchor "
            f"must be physically independent (logical key_id distinctness "
            f"is not sufficient)"
        )
    if ledger_binding_id is None:
        # The OD verifier hard-REQUIRES the binding once a record is
        # supplied (§21.2.2 row 4 cross-ledger guard) — refuse HERE with the
        # typed rejection rather than letting the walk raise an unwrapped
        # CutoverRecordValidationError defect.
        raise ForgedCutoverRecordError(
            "no audit_ledger_binding_id in the supplied runtime config — a "
            "cutover record cannot be bound to this deployment's sidecar "
            "without it (the §21.2.2 row-4 cross-ledger guard is REQUIRED, "
            "never skipped)"
        )
    if record.ledger_binding_id != ledger_binding_id:
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


def _alias_source_tags(record: AuditCutoverRecord) -> dict[tuple[str, str], str]:
    """Record-derived alias map keyed by DESTINATION identity
    `(tenant_scope, entry_hash)` → `source_tag` — never `entry_hash` alone
    (codex round-1 P2 on this leg: two record rows legitimately sharing a
    pre-v1.34 entry hash across tenants would overwrite each other in a
    hash-only dict, making reverse coverage row-order-dependent)."""
    return {(row.tenant_scope, row.entry_hash): row.source_tag for row in record.rows}


def _surplus_rows(
    observed_identities: tuple[tuple[str, str], ...],
    ledger_audit_refs: frozenset[str],
    record: AuditCutoverRecord,
) -> tuple[str, ...]:
    """Reverse coverage (codex rounds 52/53): sidecar rows absent from the
    IS ledger's `audit:` refs are SURPLUS — with the record-derived alias
    projection so migrated history (IS ids still `audit:_single:<hash>`)
    matches and is NOT reported surplus."""
    aliases = _alias_source_tags(record)
    surplus: list[str] = []
    for tag, entry_hash in observed_identities:
        current_ref = f"audit:{tag}:{entry_hash}"
        if current_ref in ledger_audit_refs:
            continue
        source_tag = aliases.get((tag, entry_hash))
        if source_tag is not None and f"audit:{source_tag}:{entry_hash}" in ledger_audit_refs:
            continue  # migrated row — matches through the alias projection
        surplus.append(current_ref)
    return tuple(surplus)


def _missing_ledger_refs(
    observed_identities: tuple[tuple[str, str], ...],
    ledger_audit_refs: frozenset[str],
    record: AuditCutoverRecord,
) -> tuple[str, ...]:
    """FORWARD coverage (codex round-1 P1 on this leg): an IS ledger
    `audit:` ref whose sidecar row is DELETED never reaches the verifier —
    without this check an authenticated empty record could report VERIFIED
    over truncated audit history. Alias-projected the same way as
    `_surplus_rows` so migrated history covers its `_single`-form ref."""
    aliases = _alias_source_tags(record)
    covered: set[str] = set()
    for tag, entry_hash in observed_identities:
        covered.add(f"audit:{tag}:{entry_hash}")
        source_tag = aliases.get((tag, entry_hash))
        if source_tag is not None:
            covered.add(f"audit:{source_tag}:{entry_hash}")
    return tuple(sorted(ledger_audit_refs - covered))


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

    if expected_tenant is not None:
        # Validate through the SAME OD rule-set signing uses — a reserved
        # ("_single") or empty tenant is an INPUT error reported as the
        # explicit nonzero disposition, never an unwrapped normalizer
        # ValueError mid-walk (codex round-3 P2).
        from harness_od.multi_tenant_trace_separation_and_audit_ledger import signing_token

        try:
            signing_token(expected_tenant)
        except ValueError as exc:
            return _unverified(f"--expected-tenant invalid: {exc}")

    is_mtc = runtime_config.persona_tier == PersonaTier.MULTI_TENANT_COMPLIANCE
    have_backend_inputs = key_map_path is not None and cutover_record_path is not None
    any_verification_input = (
        key_map_path is not None or cutover_record_path is not None or expected_tenant is not None
    )

    if not have_backend_inputs:
        if is_mtc:
            return _unverified(
                "MULTI_TENANT_COMPLIANCE inspection requires --signing-key-map "
                "AND --cutover-record — silent hash-only success is prohibited "
                "(OD v1.34 §21.2.2 row 8)"
            )
        if any_verification_input:
            # Verification was REQUESTED but the input set is incomplete —
            # never silently fall back to hash-only (the record is required
            # whenever any row exists; era is never observation-inferred).
            missing = [
                name
                for name, value in (
                    ("--signing-key-map", key_map_path),
                    ("--cutover-record", cutover_record_path),
                )
                if value is None
            ]
            return _unverified(
                f"verification inputs incomplete (missing {', '.join(missing)}) "
                f"— a partial input set never degrades to hash-only"
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
            else _SidecarContent(
                tagged_entries=(),
                observed_identities=(),
                baseline_identities=(),
                row_key_ids=frozenset(),
            )
        )
    except (ValueError, OSError) as exc:
        return _unverified(f"audit sidecar {sidecar_path} unreadable/unparseable: {exc}")

    try:
        key_map, key_materials = _load_key_map(
            key_map_path  # type: ignore[arg-type]  # narrowed above
        )
    except (ValueError, OSError) as exc:
        return _unverified(f"--signing-key-map unusable: {exc}")

    # The record is REQUIRED whenever ANY row exists (era never inferred);
    # its authentication failures are TYPED and never absent-fallback. An
    # unreadable/missing record FILE is an input failure, not a forgery —
    # explicit UNVERIFIED, never a traceback (codex round-1 P2 on this leg).
    try:
        record, signature = _load_authenticated_record(
            cutover_record_path,  # type: ignore[arg-type]  # narrowed above
            pinned_key_id=runtime_config.audit_cutover_record_key_id,
            ledger_binding_id=runtime_config.audit_ledger_binding_id,
            key_map=key_map,
            key_materials=key_materials,
            row_key_ids=sidecar.row_key_ids,
        )
    except OSError as exc:
        return _unverified(f"--cutover-record unreadable: {exc}")

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

    missing = _missing_ledger_refs(sidecar.observed_identities, ledger_audit_refs, record)
    if missing and is_mtc:
        return AuditInspectionOutcome(
            disposition="failed",
            exit_code=EXIT_AUDIT_FAILED,
            detail=(
                f"{len(missing)} IS ledger audit: ref(s) with NO surviving "
                f"sidecar row — deleted/truncated audit history fails the "
                f"MTC audit (forward coverage): {', '.join(missing)}"
            ),
        )

    # Observed-vs-recorded baseline COMPLETENESS (codex round-2 P1): an
    # observed legacy-baseline identity no record row claims (by SOURCE
    # identity, any scope) would otherwise be silently dropped by the scope
    # grouping — the OD §21.2.2 row-6 check must never be bypassable by
    # simply not naming an identity in the record. Tier-independent, like
    # the walk's own divergence failures.
    recorded_source_identities = {(row.source_tag, row.entry_hash) for row in record.rows}
    unrecorded = [
        (tag, entry_hash)
        for tag, entry_hash in sidecar.baseline_identities
        if (tag, entry_hash) not in recorded_source_identities
    ]
    if unrecorded:
        return AuditInspectionOutcome(
            disposition="failed",
            exit_code=EXIT_AUDIT_FAILED,
            detail=(
                f"{len(unrecorded)} observed legacy-baseline identity(ies) "
                f"absent from the authenticated cutover record (OD v1.34 "
                f"§21.2.2 row 6 completeness — an unrecorded baseline never "
                f"passes): "
                + ", ".join(f"({tag!r}, {entry_hash!r})" for tag, entry_hash in unrecorded)
            ),
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
    walks = [
        run_blocking_audit_walk(
            group_entries,
            verifier=adapter,
            tenant_scope=scope,
            observed_baseline_identities=group_baselines,
        )
        for scope, group_entries, group_baselines in _scoped_walk_groups(
            sidecar, record, expected_tenant
        )
    ]
    failed = next((w for w in walks if w.kind is WalkResultKind.FAILED), None)
    if failed is not None:
        return AuditInspectionOutcome(
            disposition="failed",
            exit_code=EXIT_AUDIT_FAILED,
            detail=failed.detail,
            walk_result=failed,
        )
    incomplete = next((w for w in walks if w.kind is WalkResultKind.INCOMPLETE_UNVERIFIED), None)
    if incomplete is not None:
        return AuditInspectionOutcome(
            disposition="unverified",
            exit_code=EXIT_AUDIT_UNVERIFIED,
            detail=f"{AUDIT_UNVERIFIED_FAIL_CLASS}: {incomplete.detail}",
            walk_result=incomplete,
        )
    merged = _merge_passed_walks(walks)
    return AuditInspectionOutcome(
        disposition="verified", exit_code=0, detail=merged.detail, walk_result=merged
    )


def _scoped_walk_groups(
    sidecar: _SidecarContent,
    record: AuditCutoverRecord,
    expected_tenant: str | None,
) -> list[tuple[str | None, list[AuditLedgerEntry], list[tuple[str, str]]]]:
    """Partition sidecar content into per-tenant-scope walk groups.

    The OD verifier is SINGLE-scope (its five-segment message reconstruction
    uses one tenant token) — passing a mixed multi-tenant batch under one
    `expected_tenant` falsely reports SIGNATURE_INVALID for every other
    tenant's valid rows (codex round-1 P1 on this leg). Grouping:

    - each explicit tenant tag (or ONLY `expected_tenant` when supplied)
      walks under its own scope;
    - a `"_single"`-tagged row CLAIMED by an authenticated record row for a
      scope (destination identity match) joins THAT scope's walk — its
      recorded disposition governs it there;
    - record `tenant_scope`s with no sidecar tag still get a walk (their
      baseline claims must be cross-checked, never skipped);
    - unclaimed `"_single"` rows walk untenanted (`scope=None`, the
      pre-tenant four-tuple era).
    """
    claimed = {(row.tenant_scope, row.entry_hash) for row in record.rows}
    if expected_tenant is not None:
        scopes = [expected_tenant]
    else:
        scopes = sorted(
            {tag for tag, _ in sidecar.tagged_entries if tag != _SINGLE_TAG}
            | {tag for tag, _ in sidecar.baseline_identities if tag != _SINGLE_TAG}
            | {row.tenant_scope for row in record.rows}
        )

    groups: list[tuple[str | None, list[AuditLedgerEntry], list[tuple[str, str]]]] = []
    consumed_single_hashes: set[str] = set()
    for scope in scopes:
        group_entries: list[AuditLedgerEntry] = []
        for tag, entry in sidecar.tagged_entries:
            if tag == scope:
                group_entries.append(entry)
            elif tag == _SINGLE_TAG and (scope, entry.entry_hash) in claimed:
                group_entries.append(entry)
                consumed_single_hashes.add(entry.entry_hash)
        group_baselines = [
            (tag, entry_hash)
            for tag, entry_hash in sidecar.baseline_identities
            if tag == scope or (tag == _SINGLE_TAG and (scope, entry_hash) in claimed)
        ]
        groups.append((scope, group_entries, group_baselines))

    leftover = [
        entry
        for tag, entry in sidecar.tagged_entries
        if tag == _SINGLE_TAG and entry.entry_hash not in consumed_single_hashes
    ]
    if leftover or not groups:
        groups.append((None, leftover, []))
    return groups


def _merge_passed_walks(walks: list[BlockingAuditWalkResult]) -> BlockingAuditWalkResult:
    """Merge all-PASSED per-scope walks into one report carrier."""
    if len(walks) == 1:
        return walks[0]
    dispositions: dict[str, int] = {}
    for walk in walks:
        for key, count in walk.signature_dispositions.items():
            dispositions[key] = dispositions.get(key, 0) + count
    return BlockingAuditWalkResult(
        kind=WalkResultKind.PASSED,
        detail=(
            f"audit PASSED across {len(walks)} tenant-scope walk group(s): "
            + "; ".join(w.detail for w in walks)
        ),
        signature_dispositions=dispositions,
        exempt_entries=tuple(v for w in walks for v in w.exempt_entries),
    )
