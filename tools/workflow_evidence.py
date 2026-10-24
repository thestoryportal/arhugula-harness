#!/usr/bin/env python3
"""WO-U04 / WP-03 — reusable verification bound to its declared inputs (spec WS-08
§10.1-10.2, WS-15 §17.1).

`build_manifest` observes, for one `CheckRequest`, the exact files a check depends on:
everything Git can discover under its discovery domains (tracked plus genuine untracked
files), every explicit input (checker, config, lock and task subjects, read even when
ignored), each with byte-exact path, kind, effective Git mode and content digest. Files
under a policy-validated artifact root leave discovery; explicit inputs never do.
Anything the manifest cannot identify faithfully becomes a typed `Refusal`.

`reuse_result` is a pure decision: a prior passed `CheckReceipt` is reusable only when
the current manifest has no refusals and every identity component matches; otherwise
each differing component is named. Reuse is identity/equivalence evidence with explicit
limits, never a cached pass for different inputs or a semantic approval.

WO-U19 / WP-14 (spec WS-12, WS-13) adds installed reuse on the same identities.
`install_reuse` judges whether a current `InstalledCandidate` may reuse an accepted
build/install (`valid`, `impact_review_required`, `invalid` or `unknown`); a later head
reuses it only through an equivalence over the installed inputs. `bind_acceptance` admits
only a passed installed run of the final candidate, or of an accepted candidate carried to
it by a valid reuse. `accepted_build_install` reads the native accepted build evidence
without rewriting it; `observe_install` re-reads an existing install by hashing files.
A `ScenarioContract` must be complete before `admit_scenario` lets it start, and
`judge_scenario` passes only the specific expected outcome.

Nothing here runs a checker, publishes a receipt or changes a gate; it is inactive until
the coherent adoption (WP-17) wires it into the guard.
"""

from __future__ import annotations

import base64
import csv
import hashlib
import json
import os
import posixpath
import re
import stat
import subprocess
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Literal, NamedTuple, cast

from tools.workflow_policy import WorkflowPolicy, canonical_digest

SCHEMA_VERSION = 1

FileKind = Literal["file", "symlink", "deleted"]
Closure = Literal["declared", "unknown"]
RecordResult = Literal["passed", "held", "failed", "error"]

_RESULTS: tuple[RecordResult, ...] = ("passed", "held", "failed", "error")
_ENVELOPE_FIELDS = (
    "schema_version",
    "record_id",
    "record_type",
    "policy_id",
    "policy_version",
    "unit_id",
    "producer",
    "created_at",
    "subject",
    "inputs",
    "result",
    "artifacts",
    "supersedes",
    "limits",
)
_MANIFEST_FIELDS = (
    "schema_version",
    "unit",
    "repository",
    "scope",
    "head",
    "material_base",
    "checker",
    "policy",
    "domains",
    "explicit",
    "environment",
    "files",
    "refusals",
)
# Provenance, not identity (WS-08): the same bytes verified from the worktree, the index
# or a commit are the same inputs; refusals are judged separately by `reuse_result`.
_PROVENANCE_FIELDS = frozenset({"unit", "scope", "head", "refusals"})
_MODES: Mapping[str, FileKind] = MappingProxyType(
    {"100644": "file", "100755": "file", "120000": "symlink"}
)
_SHA256 = re.compile(r"[0-9a-f]{64}")
_SCOPE = re.compile(r"working_tree|index|git_tree")
_GIT_OID = re.compile(r"[0-9a-f]{40}|[0-9a-f]{64}")
_RFC3339_UTC = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z")
_LIMITS = (
    "Input identity only: equal inputs, not semantic approval of the result.",
    "No cross-policy compatibility mapping; any policy change invalidates.",
)


class EvidenceError(ValueError):
    """Invalid request, observation or receipt; `field` names the offending part (WS-18)."""

    def __init__(self, field: str, problem: str) -> None:
        super().__init__(f"{field}: {problem}")
        self.field = field


def _relative(value: object, field: str) -> str:
    """A repository-relative POSIX path already in canonical form."""
    if not isinstance(value, str) or not value:
        raise EvidenceError(field, "must be a nonempty path")
    parts = value.split("/")
    if value.startswith("/") or posixpath.normpath(value) != value or ".." in parts:
        raise EvidenceError(field, f"{value!r} is not a canonical repository-relative path")
    return value


def _under(path: str, root: str) -> bool:
    return path == root or path.startswith(root + "/")


def _utf8_order(paths: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(sorted(paths, key=lambda path: path.encode()))


@dataclass(frozen=True)
class WorkingTree:
    """Files as they are on disk, including genuine untracked ones."""


@dataclass(frozen=True)
class Index:
    """The staged bytes a commit would record."""


@dataclass(frozen=True)
class GitTree:
    rev: str


Scope = WorkingTree | Index | GitTree


def _scope_name(scope: Scope) -> str:
    match scope:
        case WorkingTree():
            return "working_tree"
        case Index():
            return "index"
        case GitTree():
            return "git_tree"


@dataclass(frozen=True)
class Checker:
    name: str
    version: str
    argv: tuple[str, ...]


@dataclass(frozen=True)
class CheckRequest:
    """One reusable check's declared input set (WS-08 §10.1).

    `domains` are discovery directories whose membership matters; `explicit` are files
    that are inputs regardless of discovery or artifact classification (checker, config,
    locks, task subjects). `material_base` is set only for a base-sensitive checker.
    """

    unit: str
    repository: str
    scope: Scope
    policy: WorkflowPolicy
    checker: Checker
    domains: tuple[str, ...]
    explicit: tuple[str, ...]
    environment: Mapping[str, str]
    material_base: str | None
    closure: Closure

    def __post_init__(self) -> None:
        # [LAW:parse-dont-validate] a constructed request holds only canonical paths.
        for field in ("domains", "explicit"):
            for index, path in enumerate(getattr(self, field)):
                _relative(path, f"{field}[{index}]")


@dataclass(frozen=True)
class FileEntry:
    path: str
    kind: FileKind
    mode: str | None
    sha256: str | None

    def to_json(self) -> dict[str, object]:
        return {"path": self.path, "kind": self.kind, "mode": self.mode, "sha256": self.sha256}


@dataclass(frozen=True)
class Refusal:
    """Something the manifest could not identify faithfully; it forbids reuse."""

    code: str
    detail: str


@dataclass(frozen=True)
class Classification:
    code_roots: tuple[str, ...]
    artifact_roots: tuple[str, ...]


@dataclass(frozen=True)
class InputManifest:
    unit: str
    repository: str
    scope: str
    head: str
    material_base: str | None
    checker: Checker
    policy_id: str
    policy_version: int
    policy_digest: str
    domains: tuple[str, ...]
    explicit: tuple[str, ...]
    environment: Mapping[str, str]
    files: tuple[FileEntry, ...]
    refusals: tuple[Refusal, ...]

    def to_json(self) -> dict[str, object]:
        return {
            "schema_version": SCHEMA_VERSION,
            "unit": self.unit,
            "repository": self.repository,
            "scope": self.scope,
            "head": self.head,
            "material_base": self.material_base,
            "checker": {
                "name": self.checker.name,
                "version": self.checker.version,
                "argv": list(self.checker.argv),
            },
            "policy": {
                "policy_id": self.policy_id,
                "policy_version": self.policy_version,
                "digest": self.policy_digest,
            },
            "domains": list(self.domains),
            "explicit": list(self.explicit),
            "environment": dict(sorted(self.environment.items())),
            "files": [entry.to_json() for entry in self.files],
            "refusals": [{"code": r.code, "detail": r.detail} for r in self.refusals],
        }

    def identity(self) -> dict[str, object]:
        """The components the check key covers; membership is named apart from bytes."""
        doc = {k: v for k, v in self.to_json().items() if k not in _PROVENANCE_FIELDS}
        doc["membership"] = [entry.path for entry in self.files]
        return doc

    @property
    def key(self) -> str:
        return canonical_digest(self.identity())


# --- classification ----------------------------------------------------------------------


def _object(value: object, field: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise EvidenceError(field, "must be a JSON object")
    return cast(dict[str, object], value)


def _array(value: object, field: str) -> list[object]:
    if not isinstance(value, list):
        raise EvidenceError(field, "must be a JSON array")
    return cast(list[object], value)


def _exact_keys(doc: dict[str, object], expected: tuple[str, ...], field: str) -> None:
    if set(doc) != set(expected):
        raise EvidenceError(field, f"fields must be exactly {', '.join(expected)}")


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(field, "must be a nonempty string")
    return value


def parse_classification(rule: Mapping[str, object]) -> Classification:
    """The policy's `artifact_roots` rule: declared code roots and validated artifact roots."""
    _exact_keys(dict(rule), ("code_roots", "artifact_roots"), "artifact_roots")
    code_roots = _array(rule["code_roots"], "artifact_roots.code_roots")
    artifact_roots: list[str] = []
    for index, item in enumerate(_array(rule["artifact_roots"], "artifact_roots.artifact_roots")):
        field = f"artifact_roots.artifact_roots[{index}]"
        entry = _object(item, field)
        _exact_keys(entry, ("root", "purpose"), field)
        _text(entry["purpose"], field + ".purpose")
        artifact_roots.append(_relative(entry["root"], field + ".root"))
    return Classification(
        code_roots=tuple(
            _relative(root, f"artifact_roots.code_roots[{index}]")
            for index, root in enumerate(code_roots)
        ),
        artifact_roots=tuple(artifact_roots),
    )


def _classification(policy: WorkflowPolicy) -> tuple[Classification, tuple[Refusal, ...]]:
    """The roots discovery may prune, plus refusals; an unusable rule prunes nothing."""
    try:
        classification = parse_classification(policy.rules["artifact_roots"])
    except EvidenceError as exc:
        return Classification((), ()), (Refusal("classification_invalid", str(exc)),)
    # [LAW:single-enforcer] no artifact declaration may claim any part of a code root
    # (WS-15 §17.1); the overlap is ambiguous, so it prunes nothing and forbids reuse.
    overlaps = tuple(
        Refusal("classification_ambiguous", f"{artifact} overlaps code root {code}")
        for artifact in classification.artifact_roots
        for code in classification.code_roots
        if _under(artifact, code) or _under(code, artifact)
    )
    usable = classification.artifact_roots if not overlaps else ()
    return Classification(classification.code_roots, usable), overlaps


# --- observation: the only effects -------------------------------------------------------


def _git(root: Path, *args: str, stdin: bytes = b"") -> bytes:
    # --literal-pathspecs: a requested path is a path, never a glob or magic signature.
    proc = subprocess.run(
        ["git", "--literal-pathspecs", *args],
        cwd=root,
        input=stdin,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        detail = proc.stderr.decode("utf-8", errors="replace").strip()
        raise EvidenceError("git", f"{' '.join(args[:2])} failed: {detail}")
    return proc.stdout


def _listing(root: Path, args: tuple[str, ...], paths: tuple[str, ...]) -> list[bytes]:
    """NUL-separated Git listing restricted to `paths`."""
    # Git treats an empty pathspec as the whole repository; no paths means no files.
    out = _git(root, *args, "--", *paths) if paths else b""
    return sorted(set(filter(None, out.split(b"\0"))))


def _revision(root: Path, rev: str) -> str:
    out = _git(root, "rev-parse", "--verify", "--end-of-options", rev + "^{commit}")
    return out.decode().strip()


def _sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _symlink_escapes(path: str, target: bytes) -> bool:
    text = target.decode("utf-8", errors="surrogateescape")
    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(path), text))
    return posixpath.isabs(text) or resolved == ".." or resolved.startswith("../")


def _entry(path: str, mode: str, content: bytes) -> FileEntry | Refusal:
    """One present file; a symlink is identified by its target and never traversed."""
    kind = _MODES.get(mode)
    if kind is None:
        return Refusal("unsupported_entry", f"{path}: Git mode {mode}")
    if kind == "symlink" and _symlink_escapes(path, content):
        return Refusal("symlink_escape", f"{path} -> {content!r}")
    return FileEntry(path, kind, mode, _sha256(content))


def _decoded(raw: bytes) -> str | Refusal:
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        # WS-08: refuse rather than let a lossy conversion alias or drop the path.
        return Refusal("unsupported_path", repr(raw))


def _symlinked_ancestor(root: Path, path: str) -> str | None:
    """The first directory on `path` that is a symlink; reading through it would traverse."""
    parts = path.split("/")[:-1]
    prefixes = ("/".join(parts[: depth + 1]) for depth in range(len(parts)))
    return next((prefix for prefix in prefixes if (root / prefix).is_symlink()), None)


def _read_worktree(root: Path, path: str) -> FileEntry | Refusal:
    # Git never discovers files beyond a symlink, but an explicit input is read by name:
    # a symlinked ancestor would silently substitute bytes from wherever it points.
    ancestor = _symlinked_ancestor(root, path)
    if ancestor is not None:
        return Refusal("symlink_traversal", f"{path} passes through symlink {ancestor}")
    full = os.fsencode(root) + b"/" + path.encode()
    try:
        info = os.lstat(full)
    except FileNotFoundError:
        return FileEntry(path, "deleted", None, None)
    if stat.S_ISLNK(info.st_mode):
        return _entry(path, "120000", os.readlink(full))
    if not stat.S_ISREG(info.st_mode):
        return Refusal("unsupported_entry", f"{path}: not a regular file or symlink")
    mode = "100755" if info.st_mode & stat.S_IXUSR else "100644"
    with open(full, "rb") as handle:
        return _entry(path, mode, handle.read())


def _observe_worktree(root: Path, request: CheckRequest) -> list[FileEntry | Refusal]:
    listed = ("ls-files", "-z", "--cached", "--others", "--exclude-standard")
    names = [_decoded(raw) for raw in _listing(root, listed, request.domains)]
    # Explicit inputs are read by name, so an ignored historical driver stays visible.
    paths = sorted({name for name in names if isinstance(name, str)} | set(request.explicit))
    refusals: list[FileEntry | Refusal] = [name for name in names if isinstance(name, Refusal)]
    return refusals + [_read_worktree(root, path) for path in paths]


def _blobs(root: Path, oids: list[str]) -> list[bytes]:
    out = _git(root, "cat-file", "--batch", stdin="".join(oid + "\n" for oid in oids).encode())
    contents: list[bytes] = []
    offset = 0
    for oid in oids:
        header_end = out.index(b"\n", offset)
        header = out[offset:header_end].decode().split()
        if len(header) != 3 or header[0] != oid or header[1] != "blob":
            raise EvidenceError("git", f"cat-file returned {header!r} for {oid}")
        start = header_end + 1
        contents.append(out[start : start + int(header[2])])
        offset = start + int(header[2]) + 1
    return contents


def _object_rows(
    root: Path, scope: Index | GitTree, paths: tuple[str, ...]
) -> dict[bytes, tuple[str, str]]:
    """Raw path to (mode, object id) for every staged or committed file under `paths`."""
    rows: dict[bytes, tuple[str, str]] = {}
    match scope:
        case Index():
            for row in _listing(root, ("ls-files", "-z", "--stage"), paths):
                meta, raw_path = row.split(b"\t", 1)
                mode, oid, stage = meta.decode().split()
                # A nonzero stage is an unresolved merge: no single staged identity exists.
                rows[raw_path] = (mode if stage == "0" else "unmerged", oid)
        case GitTree(rev=rev):
            for row in _listing(root, ("ls-tree", "-r", "-z", "--full-tree", rev), paths):
                meta, raw_path = row.split(b"\t", 1)
                mode, _, oid = meta.decode().split()
                rows[raw_path] = (mode, oid)
    return rows


def _observe_objects(
    root: Path, scope: Index | GitTree, request: CheckRequest
) -> list[FileEntry | Refusal]:
    rows = _object_rows(root, scope, request.domains) | _object_rows(root, scope, request.explicit)
    names = {raw: _decoded(raw) for raw in rows}
    # Only blob modes have content to hash; any other mode becomes a refusal in `_entry`.
    readable = [
        raw for raw, name in names.items() if isinstance(name, str) and rows[raw][0] in _MODES
    ]
    blobs = dict(zip(readable, _blobs(root, [rows[raw][1] for raw in readable]), strict=True))
    observed: list[FileEntry | Refusal] = [
        name if isinstance(name, Refusal) else _entry(name, rows[raw][0], blobs.get(raw, b""))
        for raw, name in names.items()
    ]
    absent = [path for path in request.explicit if path.encode() not in rows]
    return observed + [FileEntry(path, "deleted", None, None) for path in absent]


def build_manifest(root: Path, request: CheckRequest) -> InputManifest:
    """[LAW:effects-at-boundaries] the one place inputs are observed from Git and disk."""
    toplevel = _git(root, "rev-parse", "--show-toplevel").decode().strip()
    if Path(toplevel).resolve() != root.resolve():
        raise EvidenceError("root", f"{root} is not the repository top level {toplevel}")
    match request.scope:
        case WorkingTree():
            head, observed = _revision(root, "HEAD"), _observe_worktree(root, request)
        case Index() as index:
            head, observed = _revision(root, "HEAD"), _observe_objects(root, index, request)
        case GitTree(rev=rev) as tree:
            head, observed = _revision(root, rev), _observe_objects(root, tree, request)
    material_base = (
        None if request.material_base is None else _revision(root, request.material_base)
    )
    return assemble_manifest(request, head=head, material_base=material_base, observed=observed)


def assemble_manifest(
    request: CheckRequest,
    *,
    head: str,
    material_base: str | None,
    observed: list[FileEntry | Refusal],
) -> InputManifest:
    """Pure: observed entries to a canonical manifest, pruning only validated artifacts."""
    classification, refusals = _classification(request.policy)
    entries = [item for item in observed if isinstance(item, FileEntry)]
    # [LAW:one-source-of-truth] an explicit task input outranks any artifact declaration.
    kept = {
        entry.path: entry
        for entry in entries
        if entry.path in request.explicit
        or not any(_under(entry.path, root) for root in classification.artifact_roots)
    }
    closure = (
        (Refusal("dependency_closure_unknown", request.checker.name),)
        if request.closure == "unknown"
        else ()
    )
    return InputManifest(
        unit=request.unit,
        repository=request.repository,
        scope=_scope_name(request.scope),
        head=head,
        material_base=material_base,
        checker=request.checker,
        policy_id=request.policy.policy_id,
        policy_version=request.policy.policy_version,
        policy_digest=request.policy.digest,
        domains=_utf8_order(tuple(set(request.domains))),
        explicit=_utf8_order(tuple(set(request.explicit))),
        environment=MappingProxyType(dict(sorted(request.environment.items()))),
        files=tuple(kept[path] for path in _utf8_order(tuple(kept))),
        refusals=refusals + tuple(item for item in observed if isinstance(item, Refusal)) + closure,
    )


# --- receipts ----------------------------------------------------------------------------


@dataclass(frozen=True)
class CheckReceipt:
    record_id: str
    result: RecordResult
    manifest: InputManifest


@dataclass(frozen=True)
class ReceiptDefect:
    """The prior receipt could not be read or parsed; it is never reusable."""

    reason: str


def _no_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
    doc: dict[str, object] = {}
    for key, value in pairs:
        if key in doc:
            raise EvidenceError(key, "duplicate key")
        doc[key] = value
    return doc


def _reject_float(text: str) -> object:
    raise EvidenceError("receipt", f"floats are not permitted: {text}")


def _decode(raw: bytes) -> dict[str, object]:
    try:
        doc = json.loads(
            raw,
            object_pairs_hook=_no_duplicates,
            parse_float=_reject_float,
            parse_constant=_reject_float,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise EvidenceError("receipt", f"not JSON: {exc}") from exc
    return _object(doc, "receipt")


def _int(value: object, field: str) -> int:
    if type(value) is not int or value < 1:
        raise EvidenceError(field, "must be a positive integer")
    return value


def _matching(value: object, pattern: re.Pattern[str], field: str) -> str:
    if not isinstance(value, str) or not pattern.fullmatch(value):
        raise EvidenceError(field, "malformed")
    return value


def _strings(value: object, field: str) -> tuple[str, ...]:
    return tuple(_text(item, field) for item in _array(value, field))


def _file_entry(value: object, field: str) -> FileEntry:
    doc = _object(value, field)
    _exact_keys(doc, ("path", "kind", "mode", "sha256"), field)
    path = _relative(doc["path"], field + ".path")
    if doc["kind"] == "deleted" and doc["mode"] is None and doc["sha256"] is None:
        return FileEntry(path, "deleted", None, None)
    mode = doc["mode"]
    if not isinstance(mode, str) or _MODES.get(mode) != doc["kind"]:
        raise EvidenceError(field, "kind and mode disagree")
    return FileEntry(path, _MODES[mode], mode, _matching(doc["sha256"], _SHA256, field + ".sha256"))


def parse_manifest(value: object) -> InputManifest:
    doc = _object(value, "manifest")
    _exact_keys(doc, _MANIFEST_FIELDS, "manifest")
    if doc["schema_version"] != SCHEMA_VERSION or type(doc["schema_version"]) is not int:
        raise EvidenceError("manifest.schema_version", f"must be {SCHEMA_VERSION}")
    checker = _object(doc["checker"], "manifest.checker")
    _exact_keys(checker, ("name", "version", "argv"), "manifest.checker")
    policy = _object(doc["policy"], "manifest.policy")
    _exact_keys(policy, ("policy_id", "policy_version", "digest"), "manifest.policy")
    environment = _object(doc["environment"], "manifest.environment")
    base = doc["material_base"]
    refusals: list[Refusal] = []
    for index, item in enumerate(_array(doc["refusals"], "manifest.refusals")):
        refusal = _object(item, f"manifest.refusals[{index}]")
        _exact_keys(refusal, ("code", "detail"), f"manifest.refusals[{index}]")
        refusals.append(Refusal(_text(refusal["code"], "code"), _text(refusal["detail"], "detail")))
    return InputManifest(
        unit=_text(doc["unit"], "manifest.unit"),
        repository=_text(doc["repository"], "manifest.repository"),
        scope=_matching(doc["scope"], _SCOPE, "manifest.scope"),
        head=_matching(doc["head"], _GIT_OID, "manifest.head"),
        material_base=None if base is None else _matching(base, _GIT_OID, "manifest.material_base"),
        checker=Checker(
            name=_text(checker["name"], "manifest.checker.name"),
            version=_text(checker["version"], "manifest.checker.version"),
            argv=_strings(checker["argv"], "manifest.checker.argv"),
        ),
        policy_id=_text(policy["policy_id"], "manifest.policy.policy_id"),
        policy_version=_int(policy["policy_version"], "manifest.policy.policy_version"),
        policy_digest=_matching(policy["digest"], _SHA256, "manifest.policy.digest"),
        domains=tuple(
            _relative(path, "manifest.domains") for path in _array(doc["domains"], "domains")
        ),
        explicit=tuple(
            _relative(path, "manifest.explicit") for path in _array(doc["explicit"], "explicit")
        ),
        environment=MappingProxyType(
            {key: _text(value, f"manifest.environment.{key}") for key, value in environment.items()}
        ),
        files=tuple(
            _file_entry(item, f"manifest.files[{index}]")
            for index, item in enumerate(_array(doc["files"], "manifest.files"))
        ),
        refusals=tuple(refusals),
    )


@dataclass(frozen=True)
class Reference:
    """An immutable artifact reference (WS-08 §10.1)."""

    uri: str
    sha256: str
    bytes: int


def _reference(value: object, field: str) -> Reference:
    doc = _object(value, field)
    _exact_keys(doc, ("uri", "sha256", "bytes"), field)
    size = doc["bytes"]
    if type(size) is not int or size < 0:
        raise EvidenceError(field + ".bytes", "must be a nonnegative integer")
    return Reference(
        _text(doc["uri"], field + ".uri"),
        _matching(doc["sha256"], _SHA256, field + ".sha256"),
        size,
    )


@dataclass(frozen=True)
class RecordIdentity:
    """What a WS-08 record says it is about; it must agree with the inputs it certifies."""

    policy_id: str
    policy_version: int
    unit: str
    repository: str
    head: str
    base: str | None


def _manifest_identity(manifest: InputManifest) -> RecordIdentity:
    return RecordIdentity(
        policy_id=manifest.policy_id,
        policy_version=manifest.policy_version,
        unit=manifest.unit,
        repository=manifest.repository,
        head=manifest.head,
        base=manifest.material_base,
    )


def _envelope(
    raw: bytes, record_type: str
) -> tuple[dict[str, object], RecordIdentity, dict[str, object]]:
    """[LAW:single-enforcer] the WS-08 envelope checks every record type shares."""
    doc = _decode(raw)
    _exact_keys(doc, _ENVELOPE_FIELDS, "receipt")
    if doc["schema_version"] != SCHEMA_VERSION or type(doc["schema_version"]) is not int:
        raise EvidenceError("schema_version", f"unsupported; expected {SCHEMA_VERSION}")
    if doc["record_type"] != record_type:
        raise EvidenceError("record_type", f"must be {record_type}")
    if doc["result"] not in _RESULTS:
        raise EvidenceError("result", f"must be one of {', '.join(_RESULTS)}")
    _matching(doc["created_at"], _RFC3339_UTC, "created_at")
    _text(doc["record_id"], "record_id")
    _object(doc["producer"], "producer")
    for name in ("artifacts", "supersedes"):
        for index, item in enumerate(_array(doc[name], name)):
            _reference(item, f"{name}[{index}]")
    _strings(doc["limits"], "limits")
    subject = _object(doc["subject"], "subject")
    _exact_keys(subject, ("repository", "head", "base"), "subject")
    base = subject["base"]
    # [LAW:parse-dont-validate] the identity is kept, so a consumer compares it, not trusts it.
    identity = RecordIdentity(
        policy_id=_text(doc["policy_id"], "policy_id"),
        policy_version=_int(doc["policy_version"], "policy_version"),
        unit=_text(doc["unit_id"], "unit_id"),
        repository=_text(subject["repository"], "subject.repository"),
        head=_matching(subject["head"], _GIT_OID, "subject.head"),
        base=None if base is None else _matching(base, _GIT_OID, "subject.base"),
    )
    return doc, identity, _object(doc["inputs"], "inputs")


def parse_receipt(raw: bytes) -> CheckReceipt:
    """The single checkpoint for a WS-08 check receipt; raises `EvidenceError`."""
    doc, identity, inputs = _envelope(raw, "check")
    # `_envelope` admitted only a WS-08 result value.
    result = cast(RecordResult, doc["result"])
    _exact_keys(inputs, ("manifest", "manifest_sha256"), "inputs")
    manifest = parse_manifest(inputs["manifest"])
    if _matching(inputs["manifest_sha256"], _SHA256, "inputs.manifest_sha256") != manifest.key:
        raise EvidenceError("inputs.manifest_sha256", "does not match the manifest")
    if identity != _manifest_identity(manifest):
        raise EvidenceError("subject", "envelope identity disagrees with its manifest")
    return CheckReceipt(record_id=cast(str, doc["record_id"]), result=result, manifest=manifest)


def load_receipt(raw: bytes) -> CheckReceipt | ReceiptDefect:
    """Receipt bytes as read to a receipt or typed defect."""
    try:
        return parse_receipt(raw)
    except EvidenceError as exc:
        return ReceiptDefect(str(exc))


def _record(
    manifest: InputManifest,
    *,
    record_type: str,
    record_id: str,
    producer: Mapping[str, str],
    created_at: str,
    result: RecordResult,
    inputs: dict[str, object],
    artifacts: list[dict[str, object]],
) -> dict[str, object]:
    return {
        "schema_version": SCHEMA_VERSION,
        "record_id": record_id,
        "record_type": record_type,
        "policy_id": manifest.policy_id,
        "policy_version": manifest.policy_version,
        "unit_id": manifest.unit,
        "producer": dict(producer),
        "created_at": created_at,
        "subject": {
            "repository": manifest.repository,
            "head": manifest.head,
            "base": manifest.material_base,
        },
        "inputs": inputs,
        "result": result,
        "artifacts": artifacts,
        "supersedes": [],
        "limits": list(_LIMITS),
    }


def check_receipt(
    manifest: InputManifest,
    *,
    record_id: str,
    producer: Mapping[str, str],
    created_at: str,
    result: RecordResult,
    artifacts: list[dict[str, object]],
) -> dict[str, object]:
    """Pure: the WS-08 check record describing one run; its producer publishes it."""
    return _record(
        manifest,
        record_type="check",
        record_id=record_id,
        producer=producer,
        created_at=created_at,
        result=result,
        inputs={"manifest": manifest.to_json(), "manifest_sha256": manifest.key},
        artifacts=artifacts,
    )


# --- equivalence -------------------------------------------------------------------------


@dataclass(frozen=True)
class EquivalenceReceipt:
    """A published judgment that a prior result's inputs equal those at another head;
    `identity` is the current manifest the record claims to describe."""

    record_id: str
    prior_record: str
    prior_head: str
    identity: RecordIdentity
    key: str


_EQUIVALENCE_INPUTS = ("prior_record", "prior_head", "current_head", "manifest_sha256")


def equivalence_record(
    prior: CheckReceipt,
    current: InputManifest,
    *,
    record_id: str,
    producer: Mapping[str, str],
    created_at: str,
) -> dict[str, object]:
    """Pure: the WS-08 equivalence record for identical inputs; refuses any difference."""
    differences = _differences(prior, current)
    if differences:
        raise EvidenceError("equivalence", f"inputs are not equivalent: {', '.join(differences)}")
    return _record(
        current,
        record_type="equivalence",
        record_id=record_id,
        producer=producer,
        created_at=created_at,
        result="passed",
        inputs={
            "prior_record": prior.record_id,
            "prior_head": prior.manifest.head,
            "current_head": current.head,
            "manifest_sha256": current.key,
        },
        artifacts=[],
    )


def parse_equivalence(raw: bytes) -> EquivalenceReceipt:
    """The single checkpoint for a published equivalence record; raises `EvidenceError`."""
    doc, identity, inputs = _envelope(raw, "equivalence")
    _exact_keys(inputs, _EQUIVALENCE_INPUTS, "inputs")
    if doc["result"] != "passed":
        raise EvidenceError("result", "an equivalence record must be passed")
    if _matching(inputs["current_head"], _GIT_OID, "inputs.current_head") != identity.head:
        raise EvidenceError("subject", "head disagrees with inputs.current_head")
    return EquivalenceReceipt(
        record_id=cast(str, doc["record_id"]),
        prior_record=_text(inputs["prior_record"], "inputs.prior_record"),
        prior_head=_matching(inputs["prior_head"], _GIT_OID, "inputs.prior_head"),
        identity=identity,
        key=_matching(inputs["manifest_sha256"], _SHA256, "inputs.manifest_sha256"),
    )


# --- reuse -------------------------------------------------------------------------------


@dataclass(frozen=True)
class ReuseDecision:
    """`reusable` with WS-18 reason codes; the prior record, key and any equivalence
    record are the reference a reused result carries."""

    reusable: bool
    reasons: tuple[str, ...]
    prior_record: str | None
    key: str
    equivalence: str | None


def _incomplete(prior: InputManifest, current: InputManifest) -> list[str]:
    """What neither manifest could identify: refusals make any comparison unknown."""
    return [refusal.code for refusal in current.refusals] + (
        ["prior_incomplete"] if prior.refusals else []
    )


def _changed(prior: InputManifest, current: InputManifest) -> list[str]:
    then, now = prior.identity(), current.identity()
    # [LAW:dataflow-not-control-flow] every identity component is compared the same way.
    return [f"{name}_changed" for name in now if then[name] != now[name]]


def _differences(prior: CheckReceipt, current: InputManifest) -> list[str]:
    return (
        _incomplete(prior.manifest, current)
        + (["prior_not_passed"] if prior.result != "passed" else [])
        + _changed(prior.manifest, current)
    )


def _equivalence_gap(
    prior_record: str,
    prior: InputManifest,
    current: InputManifest,
    equivalence: EquivalenceReceipt | None,
) -> list[str]:
    """WS-08 §10.1: reuse across heads needs a published equivalence binding exactly this
    prior record and this current manifest's full identity; any inconsistency refuses."""
    if equivalence is None:
        return [] if prior.head == current.head else ["equivalence_required"]
    bound = (
        equivalence.prior_record,
        equivalence.prior_head,
        equivalence.identity,
        equivalence.key,
    )
    expected = (prior_record, prior.head, _manifest_identity(current), current.key)
    return [] if bound == expected else ["equivalence_mismatch"]


def reuse_result(
    prior: CheckReceipt | ReceiptDefect,
    current: InputManifest,
    equivalence: EquivalenceReceipt | None = None,
) -> ReuseDecision:
    """Reuse a prior result only for identical declared inputs; never runs a command."""
    if isinstance(prior, ReceiptDefect):
        return ReuseDecision(False, ("prior_unreadable",), None, current.key, None)
    reasons = tuple(
        dict.fromkeys(
            _differences(prior, current)
            + _equivalence_gap(prior.record_id, prior.manifest, current, equivalence)
        )
    )
    return ReuseDecision(
        not reasons,
        reasons,
        prior.record_id,
        current.key,
        None if equivalence is None else equivalence.record_id,
    )


# --- installed candidates (WS-12) --------------------------------------------------------

InstallDisposition = Literal["valid", "impact_review_required", "invalid", "unknown"]
# Worst first: a proven artifact difference outranks uncertainty, which outranks an input
# change that a documented impact review may still clear. Only `valid` permits reuse.
_DISPOSITIONS: tuple[InstallDisposition, ...] = (
    "invalid",
    "unknown",
    "impact_review_required",
    "valid",
)

Facts = Mapping[str, str | None]
Graded = list[tuple[InstallDisposition, str]]


class _Shape(NamedTuple):
    """How one fact reads when it verifies the install, and when it observes a defect.
    A family fact (`member` set) is every key `<name><member>`: at least one, each named."""

    verified: re.Pattern[str]
    failed: re.Pattern[str] = re.compile(r"(?!)")  # most facts have no defect form
    member: re.Pattern[str] | None = None


# A distribution file's basename or an installed package's name - never empty or a path.
_MEMBER = re.compile(r"[A-Za-z0-9][\w.+-]*")

# [LAW:one-source-of-truth] WS-12's mandatory observations of every installed candidate.
# Only the verified shape completes a fact; an observed defect (failed origin check, RECORD
# difference, editable install) is invalid, and blank or free text is not an observation.
_ABSOLUTE = _Shape(re.compile(r"/\S.*"))
_TOKEN = _Shape(re.compile(r"\S+"))
_REQUIRED_FACTS: Mapping[str, Mapping[str, _Shape]] = MappingProxyType(
    {
        "artifact": {
            "distribution:": _Shape(_SHA256, member=_MEMBER),
            "installed:": _Shape(
                re.compile(r"version=\S+; editable=false; record=[1-9]\d* verified"),
                re.compile(
                    r"version=\S+; editable=(true; record=\d+ verified(, [1-9]\d* differ)?"
                    r"|false; record=\d+ verified, [1-9]\d* differ)"
                ),
                _MEMBER,
            ),
            "site_packages": _Shape(re.compile(r"/\S.*/site-packages")),
            "origins": _Shape(
                re.compile(r"[1-9]\d* harness modules in site-packages"),
                re.compile(r"origin check failed: \d+ failures"),
            ),
        },
        "environment": {
            "python": _ABSOLUTE,
            "os": _TOKEN,
            "kernel": _TOKEN,
            "architecture": _TOKEN,
            # A pin is the digest of the accepted resource-pin record, never a description.
            "resources": _Shape(re.compile(r"sha256:[0-9a-f]{64}")),
        },
    }
)
_GAP_GRADES: Mapping[str, InstallDisposition] = MappingProxyType(
    {"failed": "invalid", "unknown": "unknown"}
)


def _state(value: str | None, shape: _Shape) -> str:
    if value is not None and shape.verified.fullmatch(value):
        return "verified"
    return "failed" if value is not None and shape.failed.fullmatch(value) else "unknown"


def _states(facts: Facts, name: str, shape: _Shape) -> set[str]:
    if shape.member is None:
        return {_state(facts.get(name), shape)}
    # [LAW:parse-dont-validate] an unnamed member identifies nothing, whatever its value.
    members = [key.removeprefix(name) for key in facts if key.startswith(name)]
    return {
        _state(facts[name + member], shape) if shape.member.fullmatch(member) else "unknown"
        for member in members
    } or {"unknown"}


def _fact_gaps(candidate: InstalledCandidate) -> Graded:
    facts = {"artifact": candidate.artifact, "environment": candidate.environment}
    return [
        (grade, f"{group}.{name.rstrip(':')}_{state}")
        for group, shapes in _REQUIRED_FACTS.items()
        for name, shape in shapes.items()
        for state, grade in _GAP_GRADES.items()
        if state in _states(facts[group], name, shape)
    ]


def candidate_gaps(candidate: InstalledCandidate) -> tuple[str, ...]:
    """[LAW:single-enforcer] every mandatory observation `candidate` lacks; empty means it
    is completely identified and may be reused, admitted or accepted."""
    return tuple(f"source.{refusal.code}" for refusal in candidate.source.refusals) + tuple(
        code for _, code in _fact_gaps(candidate)
    )


@dataclass(frozen=True)
class InstalledCandidate:
    """One installed environment (WS-12): the installed code/contract/config/lock inputs it
    was built from, its artifact facts (distribution hashes, per-package version, editable
    status and RECORD verification, install path, import origins) and toolchain pins.
    A `None` fact was not observed: it is never equal to anything, including `None`."""

    source: InputManifest
    artifact: Facts
    environment: Facts

    def to_json(self) -> dict[str, object]:
        return {
            "head": self.source.head,
            "source": self.source.key,
            "artifact": dict(sorted(self.artifact.items())),
            "environment": dict(sorted(self.environment.items())),
        }

    @property
    def key(self) -> str:
        # The head is part of the candidate: a later revision with unchanged installed bytes
        # is still a different candidate, and only an equivalence carries results across.
        return canonical_digest(self.to_json())


@dataclass(frozen=True)
class AcceptedInstall:
    """A build/install some record accepted, and the candidate it describes."""

    record_id: str
    candidate: InstalledCandidate


@dataclass(frozen=True)
class InstallReuse:
    """Whether `current` may reuse an accepted install; reasons name every component."""

    disposition: InstallDisposition
    reasons: tuple[str, ...]
    accepted_record: str
    accepted_key: str
    current_key: str
    equivalence: str | None


def _graded(grade: InstallDisposition, codes: Iterable[str]) -> Graded:
    return [(grade, code) for code in codes]


def _fact_reasons(group: str, then: Facts, now: Facts, changed: InstallDisposition) -> Graded:
    graded: Graded = []
    for name in _utf8_order(tuple(set(then) | set(now))):
        before, after = then.get(name), now.get(name)
        if before is None or after is None:
            graded.append(("unknown", f"{group}.{name}_unknown"))
        elif before != after:
            graded.append((changed, f"{group}.{name}_changed"))
    return graded


def install_reuse(
    accepted: AcceptedInstall,
    current: InstalledCandidate,
    equivalence: EquivalenceReceipt | None = None,
) -> InstallReuse:
    """Pure WS-12 disposition: changed installed inputs or toolchain pins need an impact
    review, a changed artifact is a different install, anything unobserved is unknown, and
    a later head reuses only through an equivalence bound to this accepted record."""
    then = accepted.candidate
    graded: Graded = (
        _graded("unknown", (f"source.{code}" for code in _incomplete(then.source, current.source)))
        + _graded(
            "impact_review_required",
            (
                f"source.{code}"
                for code in _changed(then.source, current.source)
                + _equivalence_gap(accepted.record_id, then.source, current.source, equivalence)
            ),
        )
        + _fact_reasons("artifact", then.artifact, current.artifact, "invalid")
        + _fact_reasons(
            "environment", then.environment, current.environment, "impact_review_required"
        )
        + _fact_gaps(then)
        + _fact_gaps(current)
    )
    worst = min((_DISPOSITIONS.index(grade) for grade, _ in graded), default=len(_DISPOSITIONS) - 1)
    return InstallReuse(
        disposition=_DISPOSITIONS[worst],
        reasons=tuple(dict.fromkeys(code for _, code in graded)),
        accepted_record=accepted.record_id,
        accepted_key=then.key,
        current_key=current.key,
        equivalence=None if equivalence is None else equivalence.record_id,
    )


def install_equivalence_record(
    accepted: AcceptedInstall,
    current: InstalledCandidate,
    *,
    record_id: str,
    producer: Mapping[str, str],
    created_at: str,
) -> dict[str, object]:
    """Pure: the WS-08 equivalence record proving `current` has the accepted installed
    inputs; refuses any difference. Only installed inputs are compared, so it proves a
    gate-only revision, never a rebuilt or changed artifact."""
    prior = CheckReceipt(accepted.record_id, "passed", accepted.candidate.source)
    return equivalence_record(
        prior, current.source, record_id=record_id, producer=producer, created_at=created_at
    )


# --- installed acceptance ----------------------------------------------------------------


@dataclass(frozen=True)
class InstalledRun:
    """A scenario result produced by executing one installed candidate, named by key."""

    record_id: str
    scenario: str
    candidate_key: str
    result: RecordResult


Proof = CheckReceipt | AcceptedInstall | InstalledRun


@dataclass(frozen=True)
class AcceptanceBinding:
    """Whether a proof stands as installed acceptance of `final_key` at `final_head`; a
    carried result names its run's own candidate and the equivalence that carried it."""

    accepted: bool
    reasons: tuple[str, ...]
    final_key: str
    final_head: str
    run: str | None
    run_candidate: str | None
    equivalence: str | None


def _carry_gap(
    run: InstalledRun, final: InstalledCandidate, carried: InstallReuse | None
) -> list[str]:
    if run.candidate_key == final.key:
        return []
    if carried is None or (carried.accepted_key, carried.current_key) != (
        run.candidate_key,
        final.key,
    ):
        return ["candidate_mismatch"]
    return [] if carried.disposition == "valid" else [f"reuse_{carried.disposition}"]


def bind_acceptance(
    proof: Proof, final: InstalledCandidate, carried: InstallReuse | None = None
) -> AcceptanceBinding:
    """WS-12: only a passed installed run of a completely observed final candidate - or of
    an accepted candidate carried to it by a valid reuse - is installed acceptance. Source
    checks and build/install proof never are."""
    match proof:
        case CheckReceipt():
            reasons, run = ["source_proof_is_not_installed_acceptance"], None
        case AcceptedInstall():
            reasons, run = ["build_proof_is_not_installed_acceptance"], None
        case InstalledRun():
            not_passed = [] if proof.result == "passed" else ["run_not_passed"]
            reasons, run = not_passed + _carry_gap(proof, final, carried), proof
    reasons += [f"final.{gap}" for gap in candidate_gaps(final)]
    carried_by = (
        carried.equivalence
        if run is not None and carried is not None and run.candidate_key == carried.accepted_key
        else None
    )
    return AcceptanceBinding(
        accepted=not reasons,
        reasons=tuple(reasons),
        final_key=final.key,
        final_head=final.source.head,
        run=None if run is None else run.record_id,
        run_candidate=None if run is None else run.candidate_key,
        equivalence=carried_by,
    )


# --- native install evidence: the only effects in this section ---------------------------


# The native acceptance's own status for accepted build/install evidence; nothing else is.
_ACCEPTED_BUILD = "BUILD_INSTALL_EVIDENCE_ACCEPTED_ONLY"


def _package(name: str) -> str:
    """Distribution name in its installed (dist-info) spelling."""
    return name.replace("-", "_")


def _installed_fact(version: str, editable: bool, verified: int, differing: int) -> str:
    record = f"{verified} verified" + (f", {differing} differ" if differing else "")
    return f"version={version}; editable={str(editable).lower()}; record={record}"


def accepted_build_install(
    acceptance: bytes, execution_result: bytes, source: InputManifest
) -> AcceptedInstall:
    """Adapter for the native accepted build (`build-evidence-acceptance.json` and the
    `execution-result.json` it pins): read in their own schema, never rewritten. Raises
    `EvidenceError` when the pair is inconsistent or names another source head."""
    accepted = _decode(acceptance)
    if _text(accepted.get("status"), "acceptance.status") != _ACCEPTED_BUILD:
        raise EvidenceError("acceptance.status", "is not an accepted build/install")
    pinned = _object(accepted.get("result"), "acceptance.result")
    _exact_keys(pinned, ("path", "sha256", "bytes"), "acceptance.result")
    if (pinned["sha256"], pinned["bytes"]) != (_sha256(execution_result), len(execution_result)):
        raise EvidenceError("acceptance.result", "does not pin these execution-result bytes")
    result = _decode(execution_result)
    verified = _object(
        result.get("inputs_verified_before"), "execution_result.inputs_verified_before"
    )
    main = _GIT_OID.match(_text(verified.get("main"), "inputs_verified_before.main"))
    if main is None or main.group() != source.head:
        raise EvidenceError(
            "inputs_verified_before.main", f"does not name source head {source.head}"
        )
    installed = _object(result.get("installed"), "execution_result.installed")
    pins = _object(
        _object(result.get("artifacts"), "artifacts").get("dist_sha256_file"), "dist_sha256_file"
    )
    distributions: dict[str, str | None] = {}
    for line in _strings(pins.get("content"), "dist_sha256_file.content"):
        digest, name = line.split("  ", 1)
        distributions[f"distribution:{name}"] = _matching(
            digest, _SHA256, f"dist_sha256_file[{name}]"
        )
    packages = {
        f"installed:{_package(name)}": _installed_fact(
            _text(dist.get("version"), f"dists.{name}.version"),
            _object(dist, f"dists.{name}").get("direct_url") is not None,
            _int(dist.get("record_files_verified"), f"dists.{name}.record_files_verified"),
            0,
        )
        for name, dist in (
            (name, _object(value, f"dists.{name}"))
            for name, value in _object(installed.get("dists"), "installed.dists").items()
        )
    }
    origin_failures = _array(installed.get("v1_failures"), "installed.v1_failures")
    loaded = _int(installed.get("harness_modules_loaded"), "installed.harness_modules_loaded")
    origins = (
        f"{loaded} harness modules in site-packages"
        if installed.get("all_modules_in_site") is True and not origin_failures
        else f"origin check failed: {len(origin_failures)} failures"
    )
    candidate = InstalledCandidate(
        source=source,
        artifact=MappingProxyType(
            distributions
            | packages
            | {
                "site_packages": _text(installed.get("site_packages"), "installed.site_packages"),
                "origins": origins,
            }
        ),
        environment=MappingProxyType(
            {"python": _text(installed.get("python_realpath"), "installed.python_realpath")}
        ),
    )
    return AcceptedInstall(record_id=f"sha256:{_sha256(acceptance)}", candidate=candidate)


def _record_check(site: Path, record: Path) -> tuple[int, int]:
    """(verified, differing) RECORD entries; a missing or changed file differs."""
    verified = differing = 0
    for path, digest, _ in csv.reader(record.read_text(encoding="utf-8").splitlines()):
        if not digest:
            continue  # RECORD lists itself and bytecode without hashes.
        target = site / path
        actual = (
            "sha256="
            + base64.urlsafe_b64encode(hashlib.sha256(target.read_bytes()).digest())
            .rstrip(b"=")
            .decode()
            if target.is_file()
            else None
        )
        verified, differing = (
            (verified + 1, differing) if actual == digest else (verified, differing + 1)
        )
    return verified, differing


def _metadata_version(info: Path) -> str | None:
    lines = (info / "METADATA").read_text(encoding="utf-8").splitlines()
    return next((line.split(": ", 1)[1] for line in lines if line.startswith("Version: ")), None)


def _installed(site: Path, package: str) -> str | None:
    """One package's installed fact, or `None` when it is absent, ambiguous or unversioned."""
    infos = sorted(site.glob(f"{package}-*.dist-info"))
    version = _metadata_version(infos[0]) if len(infos) == 1 else None
    if version is None:
        return None
    verified, differing = _record_check(site, infos[0] / "RECORD")
    return _installed_fact(version, (infos[0] / "direct_url.json").exists(), verified, differing)


def observe_install(
    exec_root: Path, packages: tuple[str, ...], *, origins: str | None, resources: str | None
) -> tuple[Facts, Facts]:
    """[LAW:effects-at-boundaries] read an existing install's artifact, toolchain and host
    facts by hashing files and asking the kernel; it never runs the installed interpreter.
    `origins` and `resources` come from an installed origin check's receipt and the accepted
    resource pins, or `None` while not observed."""
    site = next(iter(sorted((exec_root / "venv" / "lib").glob("python3.*/site-packages"))), None)
    distributions: dict[str, str | None] = {
        f"distribution:{path.name}": _sha256(path.read_bytes())
        for path in sorted((exec_root / "dist").iterdir())
        if path.is_file()
    }
    installed: dict[str, str | None] = {
        f"installed:{package}": None if site is None else _installed(site, package)
        for package in packages
    }
    python = exec_root / "venv" / "bin" / "python"
    artifact = (
        distributions
        | installed
        | {
            "site_packages": None if site is None else str(site),
            "origins": origins,
        }
    )
    host = os.uname()
    environment = {
        "python": os.path.realpath(python) if python.exists() else None,
        "os": host.sysname,
        "kernel": host.release,
        "architecture": host.machine,
        "resources": resources,
    }
    return MappingProxyType(artifact), MappingProxyType(environment)


# --- scenario contracts (WS-13) ----------------------------------------------------------


@dataclass(frozen=True)
class Behaves:
    """The scenario is expected to meet its accepted criteria."""


@dataclass(frozen=True)
class Refuses:
    """The scenario is expected to be refused with exactly this code."""

    code: str


@dataclass(frozen=True)
class Fails:
    """The product is expected to fail in one specified way, named by this code; a bare
    nonzero exit or an infrastructure failure never proves it."""

    code: str


Expected = Behaves | Refuses | Fails


@dataclass(frozen=True)
class Threshold:
    value: str
    source: Reference


@dataclass(frozen=True)
class Resource:
    """Who owns one process, container, service or durable state, and how it is reclaimed."""

    owner: str
    reclaim: str


@dataclass(frozen=True)
class ScenarioContract:
    """Everything WS-13 §15.2 requires before a scenario may start: its identity, version
    and acceptance IDs; the exact candidate and run; literal argv, cwd and environment
    allowlist; the prerequisites it requires; its accepted workload, outcome, thresholds and
    timeout with their sources; the owner and reclamation of every resource it touches; its
    author and separate witness; where evidence goes; and what the start, pre- and
    post-cleanup observations record."""

    scenario: str
    version: str
    acceptance: tuple[str, ...]
    candidate: str
    run: str
    argv: tuple[str, ...]
    cwd: str
    environment: Mapping[str, str]
    requires: tuple[str, ...]
    workload: Reference
    expected: Expected
    thresholds: Mapping[str, Threshold]
    timeout: Threshold
    resources: Mapping[str, Resource]
    author: str
    witness: str
    evidence: str
    start: str
    precleanup: str
    postcleanup: str


_CONTRACT_FIELDS = (
    "schema_version",
    "scenario",
    "version",
    "acceptance",
    "candidate",
    "run",
    "argv",
    "cwd",
    "environment",
    "requires",
    "workload",
    "expected",
    "thresholds",
    "timeout",
    "resources",
    "attribution",
    "evidence",
    "observations",
)


def _expected(value: object) -> Expected:
    doc = _object(value, "expected")
    match doc.get("outcome"):
        case "behaves":
            _exact_keys(doc, ("outcome",), "expected")
            return Behaves()
        case "refuses":
            _exact_keys(doc, ("outcome", "code"), "expected")
            return Refuses(_text(doc["code"], "expected.code"))
        case "fails":
            _exact_keys(doc, ("outcome", "code"), "expected")
            return Fails(_text(doc["code"], "expected.code"))
        case other:
            raise EvidenceError(
                "expected.outcome", f"must be behaves, refuses or fails, not {other!r}"
            )


def _threshold(value: object, field: str) -> Threshold:
    doc = _object(value, field)
    _exact_keys(doc, ("value", "source"), field)
    return Threshold(
        _text(doc["value"], f"{field}.value"), _reference(doc["source"], f"{field}.source")
    )


def _resource(value: object, field: str) -> Resource:
    doc = _object(value, field)
    _exact_keys(doc, ("owner", "reclaim"), field)
    return Resource(
        _text(doc["owner"], f"{field}.owner"), _text(doc["reclaim"], f"{field}.reclaim")
    )


def _nonempty[T](items: T, field: str) -> T:
    if not items:
        raise EvidenceError(field, "must not be empty")
    return items


def _absolute(value: object, field: str) -> str:
    path = _text(value, field)
    if not Path(path).is_absolute():
        raise EvidenceError(field, "must be an absolute path")
    return path


def parse_scenario_contract(raw: bytes) -> ScenarioContract:
    """The single checkpoint a scenario passes before it may start: any missing or empty
    §15.2 obligation raises `EvidenceError` naming it."""
    doc = _decode(raw)
    _exact_keys(doc, _CONTRACT_FIELDS, "contract")
    if doc["schema_version"] != SCHEMA_VERSION or type(doc["schema_version"]) is not int:
        raise EvidenceError("schema_version", f"must be {SCHEMA_VERSION}")
    expected = _expected(doc["expected"])
    thresholds = {
        name: _threshold(value, f"thresholds.{name}")
        for name, value in _object(doc["thresholds"], "thresholds").items()
    }
    # A refusal or failure is judged by its code; meeting criteria needs a threshold.
    if isinstance(expected, Behaves):
        _nonempty(thresholds, "thresholds")
    attribution = _object(doc["attribution"], "attribution")
    _exact_keys(attribution, ("author", "witness"), "attribution")
    author = _text(attribution["author"], "attribution.author")
    witness = _text(attribution["witness"], "attribution.witness")
    if witness == author:
        raise EvidenceError("attribution.witness", "must be independent of the author")
    observations = _object(doc["observations"], "observations")
    _exact_keys(observations, ("start", "precleanup", "postcleanup"), "observations")
    resources = _nonempty(_object(doc["resources"], "resources"), "resources")
    return ScenarioContract(
        scenario=_text(doc["scenario"], "scenario"),
        version=_text(doc["version"], "version"),
        acceptance=_nonempty(_strings(doc["acceptance"], "acceptance"), "acceptance"),
        candidate=_matching(doc["candidate"], _SHA256, "candidate"),
        run=_text(doc["run"], "run"),
        argv=_nonempty(_strings(doc["argv"], "argv"), "argv"),
        cwd=_absolute(doc["cwd"], "cwd"),
        environment=MappingProxyType(
            {
                k: _text(v, f"environment.{k}")
                for k, v in _object(doc["environment"], "environment").items()
            }
        ),
        requires=_nonempty(_strings(doc["requires"], "requires"), "requires"),
        workload=_reference(doc["workload"], "workload"),
        expected=expected,
        thresholds=MappingProxyType(thresholds),
        timeout=_threshold(doc["timeout"], "timeout"),
        resources=MappingProxyType(
            {k: _resource(v, f"resources.{k}") for k, v in resources.items()}
        ),
        author=author,
        witness=witness,
        evidence=_text(doc["evidence"], "evidence"),
        start=_text(observations["start"], "observations.start"),
        precleanup=_text(observations["precleanup"], "observations.precleanup"),
        postcleanup=_text(observations["postcleanup"], "observations.postcleanup"),
    )


# WS-13 §15.1 prerequisite register states; only `ready` lets a dependent scenario start.
PrerequisiteState = Literal["ready", "missing", "denied", "unknown"]


@dataclass(frozen=True)
class AcceptedScenario:
    """The original accepted obligations a scenario contract must copy unchanged."""

    workload: Reference
    thresholds: Mapping[str, Threshold]
    timeout: Threshold


def admit_scenario(
    contract: ScenarioContract,
    candidate: InstalledCandidate,
    accepted: AcceptedScenario,
    prerequisites: Mapping[str, PrerequisiteState],
) -> tuple[str, ...]:
    """Why `contract` may not start against `candidate`; empty means admitted. Every
    required prerequisite must be registered `ready`, and the accepted workload, timeout and
    thresholds are the original obligations: none may be dropped, added or changed, so a
    shortened soak or relaxed bound refuses."""
    return (
        (() if contract.candidate == candidate.key else ("candidate_mismatch",))
        + tuple(f"candidate.{gap}" for gap in candidate_gaps(candidate))
        + tuple(
            f"prerequisite.{name}_{prerequisites.get(name, 'unknown')}"
            for name in contract.requires
            if prerequisites.get(name) != "ready"
        )
        + (() if contract.workload == accepted.workload else ("workload_differs",))
        + (() if contract.timeout == accepted.timeout else ("timeout_differs",))
        + tuple(
            f"threshold.{name}_differs"
            for name in _utf8_order(tuple(set(accepted.thresholds) | set(contract.thresholds)))
            if contract.thresholds.get(name) != accepted.thresholds.get(name)
        )
    )


@dataclass(frozen=True)
class Behaved:
    """The run met its criteria, as judged by the scenario's own witness."""


@dataclass(frozen=True)
class Refused:
    code: str


@dataclass(frozen=True)
class Failed:
    """The product failed, and its structured result names how."""

    code: str


@dataclass(frozen=True)
class InfrastructureFailed:
    """The run could not exercise the product; it says nothing about product behavior."""

    detail: str


Outcome = Behaved | Refused | Failed | InfrastructureFailed


@dataclass(frozen=True)
class ScenarioObservation:
    outcome: Outcome
    precleanup: Reference
    postcleanup: Reference | None


def judge_scenario(expected: Expected, observation: ScenarioObservation) -> RecordResult:
    """Pass only the specific expected outcome: an expected refusal or product failure
    passes only with its own code. Infrastructure failure is an error, never product
    behavior; a missing post-cleanup observation holds a pass but cannot hide a failure."""
    match observation.outcome, expected:
        case InfrastructureFailed(), _:
            return "error"
        case Behaved(), Behaves():
            pass
        case Refused(code=got), Refuses(code=want) if got == want:
            pass
        case Failed(code=got), Fails(code=want) if got == want:
            pass
        case _:
            return "failed"
    return "held" if observation.postcleanup is None else "passed"
