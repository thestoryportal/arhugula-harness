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

Nothing here runs a checker, publishes a receipt or changes a gate; it is inactive until
the coherent adoption (WP-17) wires it into the guard.
"""

from __future__ import annotations

import hashlib
import json
import os
import posixpath
import re
import stat
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import Literal, cast

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


def _reference(value: object, field: str) -> None:
    doc = _object(value, field)
    _exact_keys(doc, ("uri", "sha256", "bytes"), field)
    _text(doc["uri"], field + ".uri")
    _matching(doc["sha256"], _SHA256, field + ".sha256")
    size = doc["bytes"]
    if type(size) is not int or size < 0:
        raise EvidenceError(field + ".bytes", "must be a nonnegative integer")


def _envelope(raw: bytes, record_type: str) -> tuple[dict[str, object], dict[str, object]]:
    """[LAW:single-enforcer] the WS-08 envelope checks every record type shares."""
    doc = _decode(raw)
    _exact_keys(doc, _ENVELOPE_FIELDS, "receipt")
    if doc["schema_version"] != SCHEMA_VERSION or type(doc["schema_version"]) is not int:
        raise EvidenceError("schema_version", f"unsupported; expected {SCHEMA_VERSION}")
    if doc["record_type"] != record_type:
        raise EvidenceError("record_type", f"must be {record_type}")
    if doc["result"] not in _RESULTS:
        raise EvidenceError("result", f"must be one of {', '.join(_RESULTS)}")
    _int(doc["policy_version"], "policy_version")
    _matching(doc["created_at"], _RFC3339_UTC, "created_at")
    _text(doc["record_id"], "record_id")
    _object(doc["producer"], "producer")
    for name in ("artifacts", "supersedes"):
        for index, item in enumerate(_array(doc[name], name)):
            _reference(item, f"{name}[{index}]")
    _strings(doc["limits"], "limits")
    subject = _object(doc["subject"], "subject")
    _exact_keys(subject, ("repository", "head", "base"), "subject")
    return doc, _object(doc["inputs"], "inputs")


def parse_receipt(raw: bytes) -> CheckReceipt:
    """The single checkpoint for a WS-08 check receipt; raises `EvidenceError`."""
    doc, inputs = _envelope(raw, "check")
    # `_envelope` admitted only a WS-08 result value.
    result = cast(RecordResult, doc["result"])
    _exact_keys(inputs, ("manifest", "manifest_sha256"), "inputs")
    manifest = parse_manifest(inputs["manifest"])
    if _matching(inputs["manifest_sha256"], _SHA256, "inputs.manifest_sha256") != manifest.key:
        raise EvidenceError("inputs.manifest_sha256", "does not match the manifest")
    if _envelope_identity(doc) != _manifest_identity(manifest, manifest.head):
        raise EvidenceError("subject", "envelope identity disagrees with its manifest")
    return CheckReceipt(record_id=cast(str, doc["record_id"]), result=result, manifest=manifest)


def _envelope_identity(doc: dict[str, object]) -> tuple[object, ...]:
    subject = cast(dict[str, object], doc["subject"])
    return (
        doc["policy_id"],
        doc["policy_version"],
        doc["unit_id"],
        subject["repository"],
        subject["head"],
        subject["base"],
    )


def _manifest_identity(manifest: InputManifest, head: str) -> tuple[object, ...]:
    return (
        manifest.policy_id,
        manifest.policy_version,
        manifest.unit,
        manifest.repository,
        head,
        manifest.material_base,
    )


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
    head: str,
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
            "head": head,
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
        head=manifest.head,
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
    """A published judgment that a prior result's inputs equal those at another head."""

    record_id: str
    prior_record: str
    prior_head: str
    current_head: str
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
        head=current.head,
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
    doc, inputs = _envelope(raw, "equivalence")
    _exact_keys(inputs, _EQUIVALENCE_INPUTS, "inputs")
    if doc["result"] != "passed":
        raise EvidenceError("result", "an equivalence record must be passed")
    current_head = _matching(inputs["current_head"], _GIT_OID, "inputs.current_head")
    if cast(dict[str, object], doc["subject"])["head"] != current_head:
        raise EvidenceError("subject", "head disagrees with inputs.current_head")
    return EquivalenceReceipt(
        record_id=cast(str, doc["record_id"]),
        prior_record=_text(inputs["prior_record"], "inputs.prior_record"),
        prior_head=_matching(inputs["prior_head"], _GIT_OID, "inputs.prior_head"),
        current_head=current_head,
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


def _differences(prior: CheckReceipt, current: InputManifest) -> list[str]:
    then, now = prior.manifest.identity(), current.identity()
    return (
        [refusal.code for refusal in current.refusals]
        + (["prior_incomplete"] if prior.manifest.refusals else [])
        + (["prior_not_passed"] if prior.result != "passed" else [])
        # [LAW:dataflow-not-control-flow] every identity component is compared the same way.
        + [f"{name}_changed" for name in now if then[name] != now[name]]
    )


def _equivalence_gap(
    prior: CheckReceipt, current: InputManifest, equivalence: EquivalenceReceipt | None
) -> list[str]:
    """WS-08: reuse across heads needs a published equivalence binding exactly this pair."""
    if equivalence is None:
        return [] if prior.manifest.head == current.head else ["equivalence_required"]
    bound = (equivalence.prior_record, equivalence.prior_head, equivalence.current_head)
    expected = (prior.record_id, prior.manifest.head, current.head)
    return [] if bound == expected and equivalence.key == current.key else ["equivalence_mismatch"]


def reuse_result(
    prior: CheckReceipt | ReceiptDefect,
    current: InputManifest,
    equivalence: EquivalenceReceipt | None = None,
) -> ReuseDecision:
    """Reuse a prior result only for identical declared inputs; never runs a command."""
    if isinstance(prior, ReceiptDefect):
        return ReuseDecision(False, ("prior_unreadable",), None, current.key, None)
    reasons = tuple(
        dict.fromkeys(_differences(prior, current) + _equivalence_gap(prior, current, equivalence))
    )
    return ReuseDecision(
        not reasons,
        reasons,
        prior.record_id,
        current.key,
        None if equivalence is None else equivalence.record_id,
    )
