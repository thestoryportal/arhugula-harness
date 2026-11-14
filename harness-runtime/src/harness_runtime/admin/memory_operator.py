"""`python -m harness_runtime.admin.memory_operator` — the operator memory lifecycle.

One supported operator entrypoint over the EXISTING memory services: inspect
captured evidence, propose semantic/procedural candidates from it, approve or
deny a proposal, and redact / tombstone / expire a record. It is an adapter
only. Every promotion write goes through `PromotionDecisionService` and every
C-MEM-18 transition through `MemoryRedactionService`, so policy, provenance and
the memory-operation ledger keep their single authority.

**Operator decisions are explicit.** `approve` activates a proposal only when the
named operator runs it; nothing here approves on an agent's behalf. A proposal
is re-derived from its cited source before any decision, and a proposal that no
longer matches its source (or is no longer `proposed`) is refused with zero
writes — the entrypoint cannot lend authority to a record the service did not
propose.

**Scope is the source's.** Candidates take the captured record's scope; there is
no scope override, so an operator proposal cannot widen what the source could
reach. Preference candidates need structured preference details and are not
part of this recipe.

**Lifecycle transitions are DRY-RUN BY DEFAULT.** `redact`, `tombstone` and
`expire` report the requested transition and change nothing unless `--apply` is
given; the output distinguishes `requested` from `applied`.
"""

from __future__ import annotations

import argparse
import asyncio
import dataclasses
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path

from harness_is.memory_operation_ledger import MemoryOperationEntry, MemoryOperationKind
from harness_is.memory_path_registry import MemoryRootBinding
from harness_is.memory_policy import MemoryPolicyResolver, PromotionDecision, ReviewMode
from harness_is.memory_record_envelope import (
    MemoryID,
    MemoryRecordKind,
    MemoryScope,
    MemoryVisibility,
)
from harness_is.memory_redaction import MemoryRedactionResult, MemoryRedactionService
from harness_is.memory_redaction_event import MemoryRedactionActor
from harness_is.memory_store import CanonicalMemoryStore, MemoryStoreRecord
from harness_is.state_ledger_entry_schema import Actor, ActorClass

from harness_runtime.lifecycle.memory_migration import (
    CallbackMemoryMigrationService,
    MemoryMigrationReport,
)
from harness_runtime.lifecycle.memory_tool_filesystem import LocalFilesystemMemoryToolBackend
from harness_runtime.lifecycle.memory_tool_types import (
    MemoryCallbackIOError,
    MemoryToolStorageBackend,
)
from harness_runtime.lifecycle.native_memory_adapter import CanonicalNativeMemoryToolBackend
from harness_runtime.memory_compaction_safety import (
    CompactionCandidateDisposition,
    CompactionCandidateDispositionRecord,
    CompactionDecisionResult,
    CompactionSafetyHook,
)
from harness_runtime.memory_promotion import (
    PromotionCandidate,
    PromotionCandidateConfidence,
    PromotionCandidateExtractor,
    PromotionCandidateHint,
    PromotionCandidateKind,
    PromotionDecisionResult,
    PromotionDecisionService,
    PromotionProvenanceChangedError,
    SemanticInjectionPolicy,
    SemanticRecordStatus,
    canonical_candidate_scope,
    promote_decision_for_kind,
)

_EXIT_OK = 0
_EXIT_REFUSED = 1

OPERATOR_PROPOSAL_KINDS = frozenset(PromotionCandidateKind) - {PromotionCandidateKind.PREFERENCE}

# A target's PROPOSE_* decision permits review of the same target its PROMOTE_* names.
_DECISION_KINDS = (MemoryOperationKind.PROMOTE, MemoryOperationKind.DENY_PROMOTION)
_PROPOSE_FOR_PROMOTE = {
    PromotionDecision.PROMOTE_SEMANTIC: PromotionDecision.PROPOSE_SEMANTIC,
    PromotionDecision.PROMOTE_PROCEDURAL: PromotionDecision.PROPOSE_PROCEDURAL,
}


class MemoryOperatorRefusedError(ValueError):
    """The requested operator action is not permitted; nothing was written."""


class LifecycleTransition(StrEnum):
    """The C-MEM-18 transitions this entrypoint exposes."""

    REDACT = "redact"
    TOMBSTONE = "tombstone"
    EXPIRE = "expire"


@dataclass(frozen=True)
class LifecyclePlan:
    """A requested-but-not-applied transition (the dry-run result)."""

    transition: LifecycleTransition
    memory_id: MemoryID
    current_redaction_state: str
    reason: str


def record_kind_of(memory_id: MemoryID) -> MemoryRecordKind:
    """Recover the record kind from a `mem:{tier}:{kind}:{hex}` id."""

    parts = str(memory_id).split(":")
    if len(parts) != 4 or parts[0] != "mem":
        raise MemoryOperatorRefusedError(f"not a memory id: {memory_id!s}")
    try:
        return MemoryRecordKind(parts[2])
    except ValueError as exc:
        raise MemoryOperatorRefusedError(f"unknown record kind in {memory_id!s}") from exc


class MemoryOperator:
    """Operator-attributed access to the canonical store's existing services."""

    def __init__(
        self,
        *,
        store: CanonicalMemoryStore,
        policy_resolver: MemoryPolicyResolver,
        operator_id: str,
        policy_ref: str | None = None,
        run_id: str | None = None,
        project: str | None = None,
    ) -> None:
        if not operator_id.strip():
            raise MemoryOperatorRefusedError("an operator identity is required")
        self._store = store
        self._policy_resolver = policy_resolver
        self._actor = Actor(actor_class=ActorClass.OPERATOR, actor_id=operator_id)
        self._policy_ref = policy_ref
        self._run_id = run_id
        self._project = project

    def inspect(self, memory_id: MemoryID) -> MemoryStoreRecord:
        return self._store.read_record(
            memory_id, record_kind_of(memory_id), run_id=self._run_id, audit_mode=True
        )

    def operations(self) -> list[MemoryOperationEntry]:
        return self._store.read_memory_operations()

    def propose(
        self,
        source_id: MemoryID,
        *,
        kind: PromotionCandidateKind,
        statement: str,
        confidence: PromotionCandidateConfidence,
        timestamp: datetime,
    ) -> PromotionDecisionResult:
        if kind not in OPERATOR_PROPOSAL_KINDS:
            raise MemoryOperatorRefusedError(f"{kind.value} candidates are not operator-proposable")
        self._require_promotion_policy(kind)
        source = self._read_source(source_id)
        candidate = self._extractor().extract_from_hint(
            source,
            PromotionCandidateHint(
                proposed_kind=kind,
                statement=statement,
                confidence=confidence,
                suggested_scope=source.envelope.scope,
            ),
        )
        return self._service().propose_for_review(
            candidate, timestamp=timestamp, injection_policy=SemanticInjectionPolicy.NEVER
        )

    def approve(
        self,
        proposal_id: MemoryID,
        *,
        source_id: MemoryID,
        injection_policy: SemanticInjectionPolicy,
        timestamp: datetime,
        rationale: str | None = None,
    ) -> PromotionDecisionResult:
        candidate = self._proposed_candidate(proposal_id, source_id)
        self._require_promotion_policy(candidate.proposed_kind)

        # Re-checked inside the activation's guarded write: a source re-scoped after
        # the check above must not activate the proposal under its old scope.
        def _source_scope_unchanged() -> bool:
            source = self._read_source(source_id)
            return canonical_candidate_scope(source.envelope.scope) == candidate.suggested_scope

        try:
            return self._service().approve(
                candidate,
                timestamp=timestamp,
                injection_policy=injection_policy,
                operator_approved=True,
                rationale=rationale,
                activation_precondition=_source_scope_unchanged,
            )
        except PromotionProvenanceChangedError as exc:
            raise MemoryOperatorRefusedError(
                f"source {source_id!s} changed during approval; nothing was activated"
            ) from exc

    def deny(
        self,
        proposal_id: MemoryID,
        *,
        source_id: MemoryID,
        reason: str,
        timestamp: datetime,
    ) -> PromotionDecisionResult:
        if not reason.strip():
            raise MemoryOperatorRefusedError("a denial reason is required")
        candidate = self._proposed_candidate(proposal_id, source_id)
        return self._service().deny(candidate, timestamp=timestamp, reason=reason)

    def lifecycle(
        self,
        transition: LifecycleTransition,
        memory_id: MemoryID,
        *,
        reason: str,
        replacement_summary: str | None,
        timestamp: datetime,
        apply: bool,
    ) -> LifecyclePlan | MemoryRedactionResult:
        if not reason.strip():
            raise MemoryOperatorRefusedError(f"a {transition.value} reason is required")
        record = self.inspect(memory_id)
        if not apply:
            return LifecyclePlan(
                transition=transition,
                memory_id=memory_id,
                current_redaction_state=record.envelope.redaction_state.value,
                reason=reason,
            )
        service = MemoryRedactionService(
            store=self._store,
            operation_actor=self._actor,
            event_actor=MemoryRedactionActor.OPERATOR,
            policy_ref=self._policy_ref,
            run_id=self._run_id,
        )
        method = {
            LifecycleTransition.REDACT: service.redact_content,
            LifecycleTransition.TOMBSTONE: service.tombstone,
            LifecycleTransition.EXPIRE: service.expire_for_retention,
        }[transition]
        return method(
            memory_id,
            record.envelope.kind,
            timestamp=timestamp,
            reason=reason,
            replacement_summary=replacement_summary,
        )

    async def migrate(
        self,
        legacy_root: Path,
        paths: Sequence[str],
        *,
        migration_id: str,
        visibility: MemoryVisibility,
        apply: bool,
    ) -> MemoryMigrationReport:
        """Read legacy filesystem callback memory; write it to canonical memory only on apply."""

        service = CallbackMemoryMigrationService(
            source_backend=LocalFilesystemMemoryToolBackend(root=legacy_root),
            canonical_backend=CanonicalNativeMemoryToolBackend(
                store=self._store,
                policy_resolver=self._policy_resolver,
                scope=MemoryScope(project=self._project, visibility=visibility),
                actor=self._actor,
                run_id=self._require_run_id("migrate"),
                policy_ref=self._policy_ref,
            ),
            migration_id=migration_id,
            source_backend_name=MemoryToolStorageBackend.FILESYSTEM.value,
        )
        try:
            return await (service.migrate(paths) if apply else service.dry_run(paths))
        except MemoryCallbackIOError as exc:
            raise MemoryOperatorRefusedError(f"migration refused: {exc}") from exc

    def compact(
        self,
        compaction_id: str,
        *,
        source_ids: Sequence[MemoryID],
        dispositions: Sequence[CompactionCandidateDispositionRecord],
        summary: str,
        timestamp: datetime,
        apply: bool,
    ) -> tuple[PromotionCandidate, ...] | CompactionDecisionResult:
        """List the sources' compaction candidates; persist the dispositions only on apply."""

        hook = CompactionSafetyHook(
            store=self._store,
            actor=self._actor,
            run_id=self._require_run_id("compact"),
            policy_ref=self._policy_ref,
            extractor=self._extractor(),
        )
        candidates = hook.extract_candidates([self._read_source(s) for s in source_ids])
        if not apply:
            return candidates
        return hook.complete_compaction(
            compaction_id=compaction_id,
            candidates=candidates,
            dispositions=dispositions,
            timestamp=timestamp,
            summary=summary,
        )

    def _require_run_id(self, action: str) -> str:
        if self._run_id is None:
            raise MemoryOperatorRefusedError(f"{action} requires --run-id")
        return self._run_id

    def _require_promotion_policy(self, kind: PromotionCandidateKind) -> None:
        # Resolved at every decision, so a policy changed since the proposal governs it.
        resolution = self._policy_resolver.resolve_promotion()
        if resolution.review_mode is ReviewMode.FORBIDDEN:
            raise MemoryOperatorRefusedError("memory promotion review is forbidden")
        promote = promote_decision_for_kind(kind)
        if resolution.promotion_decision not in (promote, _PROPOSE_FOR_PROMOTE[promote]):
            raise MemoryOperatorRefusedError(
                f"memory promotion policy {resolution.promotion_decision.value} "
                f"does not permit {kind.value} candidates"
            )

    def _proposed_candidate(self, proposal_id: MemoryID, source_id: MemoryID) -> PromotionCandidate:
        proposal = self._store.read_record(
            proposal_id, record_kind_of(proposal_id), run_id=self._run_id
        )
        content = proposal.content
        if content.get("status") != SemanticRecordStatus.PROPOSED.value:
            raise MemoryOperatorRefusedError(
                f"{proposal_id!s} is {content.get('status')!s}, not proposed"
            )
        source = self._read_source(source_id)
        if canonical_candidate_scope(source.envelope.scope) != proposal.envelope.scope:
            raise MemoryOperatorRefusedError(
                f"source {source_id!s} scope changed since {proposal_id!s} was proposed"
            )
        procedural = "procedural_update" in content
        candidate = self._extractor().extract_from_hint(
            source,
            PromotionCandidateHint(
                proposed_kind=(
                    PromotionCandidateKind.PROCEDURAL_UPDATE
                    if procedural
                    else PromotionCandidateKind(str(content["semantic_kind"]))
                ),
                statement=str(content["procedural_update" if procedural else "statement"]),
                confidence=PromotionCandidateConfidence(str(content["confidence"])),
                suggested_scope=proposal.envelope.scope,
            ),
        )
        # The proposal's candidate id was derived from its source; a re-derivation
        # that disagrees means the named source is not the one that was proposed.
        if candidate.candidate_id != content["snapshot_id" if procedural else "candidate_id"]:
            raise MemoryOperatorRefusedError(
                f"{proposal_id!s} was not proposed from source {source_id!s}"
            )
        # The store is content-addressed: a decision writes a NEW record and the proposal
        # stays `proposed`, so the status check above cannot see an earlier decision. The
        # append-only operation ledger can: one decision per candidate, ever.
        # [LAW:one-source-of-truth]
        decided = self._prior_decision(candidate.candidate_id)
        if decided is not None:
            raise MemoryOperatorRefusedError(
                f"{proposal_id!s} was already decided ({decided.value}); "
                "a decided candidate cannot be decided again"
            )
        return candidate

    def _prior_decision(self, candidate_id: str) -> MemoryOperationKind | None:
        marker = f":{candidate_id}:"
        for entry in self._store.read_memory_operations():
            if entry.operation_kind in _DECISION_KINDS and marker in str(entry.action_id):
                return entry.operation_kind
        return None

    def _read_source(self, source_id: MemoryID) -> MemoryStoreRecord:
        return self._store.read_record(source_id, record_kind_of(source_id), run_id=self._run_id)

    def _extractor(self) -> PromotionCandidateExtractor:
        return PromotionCandidateExtractor(self._policy_resolver)

    def _service(self) -> PromotionDecisionService:
        return PromotionDecisionService(
            store=self._store,
            actor=self._actor,
            policy_ref=self._policy_ref,
            run_id=self._run_id,
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m harness_runtime.admin.memory_operator",
        description="Operator memory lifecycle over the canonical memory store.",
    )
    parser.add_argument(
        "--config", type=Path, default=None, help="harness.toml (default: auto-discover)"
    )
    parser.add_argument(
        "--memory-root", type=Path, default=None, help="override the configured memory root"
    )
    parser.add_argument("--operator", required=True, help="attributable operator identity")
    parser.add_argument("--run-id", default=None, help="run that owns run-keyed records")
    commands = parser.add_subparsers(dest="command", required=True)

    inspect = commands.add_parser("inspect", help="print one record (audit view)")
    inspect.add_argument("memory_id")
    commands.add_parser("operations", help="print the memory-operation ledger")

    propose = commands.add_parser("propose", help="propose a candidate from captured evidence")
    propose.add_argument("source_id")
    propose.add_argument(
        "--kind", required=True, choices=sorted(kind.value for kind in OPERATOR_PROPOSAL_KINDS)
    )
    propose.add_argument("--statement", required=True)
    propose.add_argument(
        "--confidence",
        default=PromotionCandidateConfidence.MEDIUM.value,
        choices=[value.value for value in PromotionCandidateConfidence],
    )

    approve = commands.add_parser("approve", help="activate a proposal")
    approve.add_argument("proposal_id")
    approve.add_argument("--source", required=True, dest="source_id")
    approve.add_argument(
        "--injection-policy",
        required=True,
        choices=[value.value for value in SemanticInjectionPolicy],
    )
    approve.add_argument("--rationale", default=None)

    deny = commands.add_parser("deny", help="deny a proposal")
    deny.add_argument("proposal_id")
    deny.add_argument("--source", required=True, dest="source_id")
    deny.add_argument("--reason", required=True)

    for transition in LifecycleTransition:
        lifecycle = commands.add_parser(transition.value, help=f"{transition.value} a record")
        lifecycle.add_argument("memory_id")
        lifecycle.add_argument("--reason", required=True)
        lifecycle.add_argument("--replacement-summary", default=None)
        lifecycle.add_argument("--apply", action="store_true", help="perform it (default: dry run)")

    migrate = commands.add_parser("migrate", help="migrate legacy filesystem callback memory")
    migrate.add_argument("legacy_root", type=Path)
    migrate.add_argument("paths", nargs="+", metavar="/memories/PATH")
    migrate.add_argument("--migration-id", required=True)
    migrate.add_argument(
        "--visibility",
        default=MemoryVisibility.PRIVATE.value,
        choices=[value.value for value in MemoryVisibility],
    )
    migrate.add_argument("--apply", action="store_true", help="write it (default: dry run)")

    compact = commands.add_parser("compact", help="record compaction candidate dispositions")
    compact.add_argument("compaction_id")
    compact.add_argument("--source", required=True, action="append", dest="source_ids")
    compact.add_argument("--summary", required=True)
    compact.add_argument(
        "--disposition",
        nargs=3,
        action="append",
        default=[],
        metavar=("CANDIDATE_ID", "DISPOSITION", "RATIONALE"),
    )
    compact.add_argument(
        "--promoted-to",
        nargs=2,
        action="append",
        default=[],
        metavar=("CANDIDATE_ID", "MEMORY_ID"),
    )
    compact.add_argument("--apply", action="store_true", help="persist it (default: dry run)")
    return parser


def _operator_from_config(args: argparse.Namespace) -> MemoryOperator:
    # Lazy: config loading pulls the runtime config surface, which `--help` should not pay.
    # The runtime's own policy derivation, so the operator sees the policy capture ran under.
    from harness_runtime.automatic_memory import (
        _policy_from_config,  # pyright: ignore[reportPrivateUsage]
    )
    from harness_runtime.config.state_placement import (
        StateKind,
        StateRootPlacementError,
        probe_declared_state_root,
        require_inside_state_root,
        resolve_state_path,
    )
    from harness_runtime.config_source import RuntimeConfigLoadError, RuntimeConfigSource

    try:
        config = RuntimeConfigSource.load(config_file=args.config)
    except RuntimeConfigLoadError as exc:
        raise MemoryOperatorRefusedError(str(exc)) from exc
    # [LAW:one-source-of-truth] The read-only probe every admin consumer calls (inspect,
    # migrate-audit-sidecar): a declared placement derives its stores from the verified
    # root; one that cannot be verified refuses, typed, instead of a checkout-local path.
    try:
        verified = probe_declared_state_root(config)
        memory_root = (
            require_inside_state_root(args.memory_root, config, verified, what="--memory-root")
            if args.memory_root is not None
            else (
                require_inside_state_root(
                    config.memory.root_path, config, verified, what="memory.root_path"
                )
                if config.memory.root_path is not None
                else resolve_state_path(StateKind.MEMORY, config, verified)
            )
        )
    except StateRootPlacementError as exc:
        raise MemoryOperatorRefusedError(str(exc)) from exc
    policy = _policy_from_config(config)
    store = CanonicalMemoryStore(
        root_binding=MemoryRootBinding(default_root=memory_root),
        deployment_surface=config.deployment_surface,
    )
    return MemoryOperator(
        store=store,
        policy_resolver=MemoryPolicyResolver(policy),
        operator_id=args.operator,
        policy_ref=policy.policy_id,
        run_id=args.run_id,
        project=config.repository_root.name,
    )


def run(operator: MemoryOperator, args: argparse.Namespace, *, now: datetime) -> object:
    """Dispatch one parsed command; returns its JSON-serializable result."""

    command: str = args.command
    if command == "inspect":
        return operator.inspect(MemoryID(args.memory_id)).model_dump()
    if command == "operations":
        return [entry.model_dump() for entry in operator.operations()]
    if command == "propose":
        result = operator.propose(
            MemoryID(args.source_id),
            kind=PromotionCandidateKind(args.kind),
            statement=args.statement,
            confidence=PromotionCandidateConfidence(args.confidence),
            timestamp=now,
        )
        return _decision_json(result)
    if command == "approve":
        result = operator.approve(
            MemoryID(args.proposal_id),
            source_id=MemoryID(args.source_id),
            injection_policy=SemanticInjectionPolicy(args.injection_policy),
            timestamp=now,
            rationale=args.rationale,
        )
        return _decision_json(result)
    if command == "deny":
        result = operator.deny(
            MemoryID(args.proposal_id),
            source_id=MemoryID(args.source_id),
            reason=args.reason,
            timestamp=now,
        )
        return _decision_json(result)
    if command == "migrate":
        report = asyncio.run(
            operator.migrate(
                args.legacy_root,
                args.paths,
                migration_id=args.migration_id,
                visibility=MemoryVisibility(args.visibility),
                apply=args.apply,
            )
        )
        return {
            "migration_id": report.migration_id,
            "applied": not report.dry_run,
            "items": [dataclasses.asdict(item) for item in report.items],
        }
    if command == "compact":
        targets = dict(args.promoted_to)
        compaction = operator.compact(
            args.compaction_id,
            source_ids=[MemoryID(source) for source in args.source_ids],
            dispositions=[
                CompactionCandidateDispositionRecord(
                    candidate_id=candidate_id,
                    disposition=CompactionCandidateDisposition(disposition),
                    rationale=rationale,
                    target_memory_ref=targets.get(candidate_id),
                )
                for candidate_id, disposition, rationale in args.disposition
            ],
            summary=args.summary,
            timestamp=now,
            apply=args.apply,
        )
        if isinstance(compaction, tuple):
            return {
                "applied": False,
                "candidates": [candidate.model_dump() for candidate in compaction],
            }
        return {
            "applied": True,
            "memory_id": str(compaction.memory_id),
            "candidate_count": compaction.candidate_count,
            "content": compaction.record.content,
        }
    outcome = operator.lifecycle(
        LifecycleTransition(command),
        MemoryID(args.memory_id),
        reason=args.reason,
        replacement_summary=args.replacement_summary,
        timestamp=now,
        apply=args.apply,
    )
    if isinstance(outcome, LifecyclePlan):
        return {
            "requested": outcome.transition.value,
            "applied": False,
            "memory_id": str(outcome.memory_id),
            "current_redaction_state": outcome.current_redaction_state,
            "reason": outcome.reason,
        }
    return {
        "requested": command,
        "applied": True,
        "memory_id": str(outcome.record.envelope.memory_id),
        "redaction_state": outcome.record.envelope.redaction_state.value,
        "operation_ref": str(outcome.operation_action_id),
    }


def _decision_json(result: PromotionDecisionResult) -> dict[str, object]:
    return {
        "status": result.status.value,
        "memory_id": str(result.memory_id),
        "operation_kind": result.operation_kind.value,
        "source_refs": [ref.model_dump(mode="json") for ref in result.record.envelope.source_refs],
        "content": result.record.content,
    }


def _json_value(value: object) -> object:
    # Envelope and ledger hashes are raw bytes; pydantic's JSON mode would utf-8 decode them.
    if isinstance(value, bytes):
        return value.hex()
    if isinstance(value, StrEnum):
        return value.value
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns a process exit code (0 success / 1 refused / 2 argparse usage)."""
    args = build_parser().parse_args(argv)
    try:
        operator = _operator_from_config(args)
        output = run(operator, args, now=datetime.now(UTC))
    except MemoryOperatorRefusedError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return _EXIT_REFUSED
    except (ValueError, OSError, RuntimeError) as exc:
        print(f"refused: {type(exc).__name__}: {exc}", file=sys.stderr)
        return _EXIT_REFUSED
    print(json.dumps(output, indent=2, sort_keys=True, default=_json_value))
    return _EXIT_OK


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
