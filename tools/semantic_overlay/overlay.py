#!/usr/bin/env python3
"""Spec / CXA / substitution semantic-layer overlay over the code graph (R-IF-112).

Single source of truth: the repo at HEAD. Every `harness-*/src/**/*.py` file carries a
*parseable* design-substrate authority cite in its docstring (`C-IS-08`, `U-RT-112`,
`ADR-F2`, `§5.2`, `H_T-CP-19`) — the spec-cite traceability layer surfaced at the
`stages/01-exploration` arc seed (99.6 % of source files; deterministic, no LLM pass).

This module JOINS four layers into ONE Understand-Anything-format graph artifact, so a
single `overlay.json` serves three consumers (advisor framing, R-IF-112):

  * **query CLI**  — the agent-facing "what code cites C-IS-08 / who cites U-RT-112 / what
    is this file's cross-axis seam / what's its substitution / show orphans" reference tool
    (always generated fresh). NB: cites are *presence*, not implementation-correctness.
  * **dashboard**  — UA-format nodes (`file:src/<pkg>/...` id convention) carry the overlay
    attrs + new semantic edge types, so an Understand-Anything KG can be left-join enriched.
  * **`--check`**  — a deterministic drift linter (sibling to `substitution_ledger.py`):
    orphan detection across the four layers.

The four layers:
  1. **spec cites**     — `C-{IS,AS,CP,OD,RT}-NN` contracts, `U-{...}-NN` units, `ADR-{F,D}N`,
                          `§N.M` sections, parsed from docstrings/comments, plus the
                          design-substrate `C-*` keyspace for contract-without-code
                          orphan reporting.
  2. **CXA seams**      — the 33 genuine typed cross-axis seams, read code-resident from
                          `harness-runtime/tests/integration/test_cxa_pattern_p1.py`
                          (`PATTERN_P1_SEAMS`) — NOT the delta-only CXA markdown (v2.19 holds
                          0 physical rows; the canonical tables live at v2.3 + additive deltas
                          — the `[[wrong-version-read-delta-only-baseline]]` hazard).
  3. **substitutions**  — `.harness/substitutions.yaml` (55 rows; H_T-* ↔ axis ↔ disposition),
                          back-linked to the 15 source files that cite an `H_T-*` id directly.
  4. **code structure** — the file is the node; imports/contains edges are left to UA itself.

Freshness (stage-01 finding #2 — a stale overlay *manufactures* the drift it fights):
  * EVERY path (`query` / `summary` / `check`) re-derives from HEAD. `overlay.json` is a
    GITIGNORED build artifact (`build` writes it on demand for the dashboard/enrich consumer);
    nothing reads a stale committed snapshot. If one is committed locally, `check` also
    compares `stats` and fails on staleness (the `substitution_ledger.py` snapshot-pin).

Cross-axis navigation (the layer code↔code graphs are blind to — stage-01 finding #3):
  * `query --seam <edge_label>` resolves a seam to consumer-file/axis ↔ producer-file/axis;
  * `query --file F` emits F's resolved inbound/outbound seam endpoints (not just labels);
  * `query --unit U` surfaces seams where U is an endpoint. NB: these cross-package seams do
    NOT appear in `enrich-ua` output — UA builds per-PACKAGE graphs, so both seam endpoints
    are never in one KG; the cross-axis layer is delivered via overlay.json + the query CLI.

Usage:
    python tools/semantic_overlay/overlay.py build              # write overlay.json
    python tools/semantic_overlay/overlay.py summary            # human counts + orphan report
    python tools/semantic_overlay/overlay.py check              # CI gate; exit 1 on hard drift
    python tools/semantic_overlay/overlay.py query --contract C-IS-08
    python tools/semantic_overlay/overlay.py query --unit U-RT-112
    python tools/semantic_overlay/overlay.py query --file harness-is/src/harness_is/entry_hash.py
    python tools/semantic_overlay/overlay.py query --substitution H_T-CP-19
    python tools/semantic_overlay/overlay.py query --seam "U-CP-30→U-IS-12"
    python tools/semantic_overlay/overlay.py query --orphans
    python tools/semantic_overlay/overlay.py enrich-ua harness-is/.understand-anything/kg.json
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

# --------------------------------------------------------------------------- #
# Paths + constants
# --------------------------------------------------------------------------- #

REPO_ROOT = Path(__file__).resolve().parents[2]
SUBSTITUTIONS_YAML = REPO_ROOT / ".harness" / "substitutions.yaml"
CXA_SEAMS_TEST = REPO_ROOT / "harness-runtime" / "tests" / "integration" / "test_cxa_pattern_p1.py"
OVERLAY_JSON = REPO_ROOT / "tools" / "semantic_overlay" / "overlay.json"
DESIGN_SUBSTRATE = REPO_ROOT / "design-substrate"

# The 7 workspace packages (axis subdirs + shared core + runtime).
PACKAGES = (
    "harness-core",
    "harness-is",
    "harness-as",
    "harness-cp",
    "harness-od",
    "harness-cxa",
    "harness-runtime",
)

# Map a top-level source package-module prefix → axis label.
MODULE_AXIS = {
    "harness_core": "core",
    "harness_is": "IS",
    "harness_as": "AS",
    "harness_cp": "CP",
    "harness_od": "OD",
    "harness_cxa": "CXA",
    "harness_runtime": "RT",
}

# Contract IDs confirmed phantom by canonical spec prose, not real unimplemented
# contracts. `Spec_Harness_Runtime_v1.md`'s v1.93 change-note: "the IS spec
# defines only C-IS-01..10, and this spec's own v1.8 §'Cross-axis citation
# substrate' change-note already flagged 'prior v1 cited C-IS-11/14/15 which
# don't exist.'" Single source of truth for both `overlay.py`'s own
# `contract_without_code` orphan scan and `qa_evidence_matrix.py`'s test-
# citation scan — B-35 (.harness/forward-register.yaml) found C-IS-14 missing
# from the (until-then closure_gate.py-local, now shared) exclusion set.
DOCUMENTED_NON_CONTRACTS = {"C-IS-11", "C-IS-14", "C-IS-15"}

# --------------------------------------------------------------------------- #
# Cite extraction (deterministic — no LLM)
# --------------------------------------------------------------------------- #

# Contracts: C-IS-05, §C-IS-05, C-RT-30, C-MEM-10 ...
RE_CONTRACT = re.compile(r"\bC-(?:IS|AS|CP|OD|RT|CORE|MEM)-\d+", re.ASCII)
# Units: U-IS-01, U-RT-112, U-CORE-02, U-HK-26, U-MEM-20 ...
RE_UNIT = re.compile(r"\bU-(?:IS|AS|CP|OD|RT|CORE|HK|MEM)-\d+", re.ASCII)
# ADRs: ADR-F2, ADR-D5 ...
RE_ADR = re.compile(r"\bADR-[FD]\d+", re.ASCII)
# Substitutions: H_T-IS-1, H_T-CP-19, H_T-AS-8f (the trailing [a-z] suffix
# disambiguates split rows like AS-8d / AS-8e / AS-8f — without it the suffix
# is dropped and all three collapse to the phantom "H_T-AS-8").
RE_SUBST = re.compile(r"\bH_T-(?:IS|AS|CP|OD|RT|CXA)-\d+[a-z]?", re.ASCII)
# Sections: §5, §5.2, §16.5.12 (noisy — kept as a secondary signal, deduped)
RE_SECTION = re.compile(r"§\d+(?:\.\d+)*", re.ASCII)


def extract_cites(text: str) -> dict[str, list[str]]:
    """Pull the five authority-cite classes out of a file's text (sorted, deduped)."""
    return {
        "spec_contracts": sorted(set(RE_CONTRACT.findall(text))),
        "unit_ids": sorted(set(RE_UNIT.findall(text))),
        "adrs": sorted(set(RE_ADR.findall(text))),
        "substitutions": sorted(set(RE_SUBST.findall(text))),
        "section_cites": sorted(set(RE_SECTION.findall(text))),
    }


def _has_any_cite(cites: dict[str, list[str]]) -> bool:
    # Section cites alone are too noisy to count as "carries an authority cite".
    return any(cites[k] for k in ("spec_contracts", "unit_ids", "adrs", "substitutions"))


# --------------------------------------------------------------------------- #
# Layer loaders
# --------------------------------------------------------------------------- #


def load_substitutions(path: Path = SUBSTITUTIONS_YAML) -> list[dict[str, Any]]:
    """The 55 H_T-* substitution rows (single source of truth, R-600)."""
    doc = yaml.safe_load(path.read_text(encoding="utf-8"))
    return list(doc.get("substitutions", []))


def load_cxa_seams(path: Path = CXA_SEAMS_TEST) -> list[dict[str, str]]:
    """The genuine typed CXA seams, read code-resident from PATTERN_P1_SEAMS.

    AST-parses the tuple literal — no import side effects, no markdown parse. Each seam:
    ``(edge_label, consumer_module, producer_module, symbol)``.
    """
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    seam_tuple: ast.AST | None = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "PATTERN_P1_SEAMS":
                    seam_tuple = node.value
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            if node.target.id == "PATTERN_P1_SEAMS" and node.value is not None:
                seam_tuple = node.value
    if seam_tuple is None:
        raise ValueError(f"PATTERN_P1_SEAMS not found in {path}")

    seams: list[dict[str, str]] = []
    for elt in getattr(seam_tuple, "elts", []):
        if not isinstance(elt, ast.Tuple) or len(elt.elts) != 4:
            continue
        try:
            label, consumer, producer, symbol = (ast.literal_eval(e) for e in elt.elts)
        except (ValueError, SyntaxError):
            continue
        seams.append(
            {
                "edge_label": label,
                "consumer_module": consumer,
                "producer_module": producer,
                "symbol": symbol,
            }
        )
    return seams


def load_spec_contracts(path: Path = DESIGN_SUBSTRATE) -> dict[str, list[str]]:
    """Return the design-substrate C-* contract keyspace with source files.

    This is the deterministic source for the advisory "contract without landed code"
    orphan class. It scans prose only; implementation correctness remains outside scope.
    """
    contracts: dict[str, set[str]] = defaultdict(set)
    if not path.is_dir():
        return {}
    for spec_file in sorted(path.rglob("*.md")):
        try:
            text = spec_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for contract in RE_CONTRACT.findall(text):
            contracts[contract].add(_rel(spec_file))
    return {k: sorted(v) for k, v in sorted(contracts.items())}


# --------------------------------------------------------------------------- #
# Canonical-head scoping. The design-substrate is a delta chain that RETAINS
# every version, so a C-*/U-* that cites ONLY a superseded version file is a
# phantom, not a real gap ([[wrong-version-read-delta-only-baseline]]). The
# orphan classes scope to canonical heads — the max-version file per versioned
# family plus every non-versioned file (living specs, ADRs, ADD, PRD) — so they
# stop reporting superseded-version phantoms (audit finding RB-DOC-03).
# --------------------------------------------------------------------------- #

RE_VERSION_STEM = re.compile(r"^(?P<family>.+?)_v(?P<major>\d+)(?:_(?P<minor>\d+))?$")


def canonical_head_md_files(path: Path = DESIGN_SUBSTRATE) -> set[str]:
    """Repo-relative md paths that are canonical heads: the max-version file per
    versioned family (Spec_Control_Plane_v1_43.md beats _v1_5.md) plus every file
    with no parseable ``_vN[_M]`` suffix."""
    if not path.is_dir():
        return set()
    best: dict[str, tuple[tuple[int, int], str]] = {}
    singletons: set[str] = set()
    for f in sorted(path.rglob("*.md")):
        m = RE_VERSION_STEM.match(f.stem)
        if not m:
            singletons.add(_rel(f))
            continue
        key = (int(m.group("major")), int(m.group("minor") or 0))
        cur = best.get(m.group("family"))
        if cur is None or key > cur[0]:
            best[m.group("family")] = (key, _rel(f))
    return singletons | {v[1] for v in best.values()}


def load_spec_units(path: Path = DESIGN_SUBSTRATE) -> dict[str, list[str]]:
    """The design-substrate U-* unit keyspace with source files. Mirrors
    load_spec_contracts for the head-scoped unit-without-code orphan class."""
    units: dict[str, set[str]] = defaultdict(set)
    if not path.is_dir():
        return {}
    for spec_file in sorted(path.rglob("*.md")):
        try:
            text = spec_file.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for unit in RE_UNIT.findall(text):
            units[unit].add(_rel(spec_file))
    return {k: sorted(v) for k, v in sorted(units.items())}


# --------------------------------------------------------------------------- #
# Module ↔ file path resolution
# --------------------------------------------------------------------------- #


def _iter_source_files() -> list[Path]:
    files: list[Path] = []
    for pkg in PACKAGES:
        src = REPO_ROOT / pkg / "src"
        if not src.is_dir():
            continue
        files.extend(sorted(src.rglob("*.py")))
    return files


def _rel(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def _node_id(path: Path) -> str:
    """Repo-relative UA-style id: ``file:harness-is/src/harness_is/entry_hash.py``."""
    return f"file:{_rel(path)}"


def _ua_id(path: Path) -> str:
    """Per-package UA id for left-join enrichment: ``file:src/harness_is/entry_hash.py``.

    Understand-Anything generates per-package KGs whose node ids are package-relative
    (``src/<pkg_module>/...``). Storing this lets ``enrich-ua`` match by id.
    """
    rel = _rel(path)
    # strip the leading "<pkg>/" segment → "src/<pkg_module>/..."
    parts = rel.split("/", 1)
    return f"file:{parts[1]}" if len(parts) == 2 else f"file:{rel}"


def _build_module_index(files: list[Path]) -> dict[str, Path]:
    """Map a dotted module name (``harness_cp.routing_manifest_residence``,
    ``harness_runtime.lifecycle.cp_is_wiring``) → its file Path.
    """
    index: dict[str, Path] = {}
    for f in files:
        rel = _rel(f)  # e.g. harness-cp/src/harness_cp/routing_manifest_residence.py
        try:
            after_src = rel.split("/src/", 1)[1]  # harness_cp/routing_manifest_residence.py
        except IndexError:
            continue
        dotted = after_src[:-3].replace("/", ".")  # drop .py, slashes→dots
        if dotted.endswith(".__init__"):
            dotted = dotted[: -len(".__init__")]
        index[dotted] = f
    return index


def _axis_of(path: Path) -> str:
    rel = _rel(path)
    try:
        mod_root = rel.split("/src/", 1)[1].split("/", 1)[0]
    except IndexError:
        return "?"
    return MODULE_AXIS.get(mod_root, "?")


# --------------------------------------------------------------------------- #
# Overlay derivation (PURE — returns the graph; asserts nothing)
# --------------------------------------------------------------------------- #


def derive() -> dict[str, Any]:
    """Build the UA-format semantic-overlay graph from HEAD. Pure; no I/O writes."""
    files = _iter_source_files()
    substitutions = load_substitutions()
    seams = load_cxa_seams()
    spec_contracts = load_spec_contracts()
    module_index = _build_module_index(files)

    # ---- nodes ---------------------------------------------------------- #
    nodes: list[dict[str, Any]] = []
    node_by_id: dict[str, dict[str, Any]] = {}
    # reverse indices for the query layer
    contract_to_files: dict[str, list[str]] = defaultdict(list)
    unit_to_files: dict[str, list[str]] = defaultdict(list)
    adr_to_files: dict[str, list[str]] = defaultdict(list)
    subst_to_files: dict[str, list[str]] = defaultdict(list)

    for f in files:
        text = f.read_text(encoding="utf-8", errors="replace")
        cites = extract_cites(text)
        nid = _node_id(f)
        node = {
            "id": nid,
            "ua_id": _ua_id(f),
            "type": "file",
            "name": f.name,
            "filePath": _rel(f),
            "package": _rel(f).split("/", 1)[0],
            "axis": _axis_of(f),
            "spec_contracts": cites["spec_contracts"],
            "unit_ids": cites["unit_ids"],
            "adrs": cites["adrs"],
            "substitutions": cites["substitutions"],
            "section_cites": cites["section_cites"],
            "cxa_role": [],  # filled below: "producer:<edge>" / "consumer:<edge>"
        }
        nodes.append(node)
        node_by_id[nid] = node
        for c in cites["spec_contracts"]:
            contract_to_files[c].append(nid)
        for u in cites["unit_ids"]:
            unit_to_files[u].append(nid)
        for a in cites["adrs"]:
            adr_to_files[a].append(nid)
        for s in cites["substitutions"]:
            subst_to_files[s].append(nid)

    # ---- CXA seam edges (semantic edge type) + resolved-seam records ----- #
    edges: list[dict[str, Any]] = []
    seam_orphans: list[dict[str, str]] = []
    seam_records: list[dict[str, Any]] = []  # fully-resolved seams (the navigable layer)
    # file id → {"inbound": [...], "outbound": [...]} seam endpoints, for --file query
    file_seams: dict[str, dict[str, list]] = defaultdict(lambda: {"inbound": [], "outbound": []})
    for seam in seams:
        prod = module_index.get(seam["producer_module"])
        cons = module_index.get(seam["consumer_module"])
        prod_id = _node_id(prod) if prod else None
        cons_id = _node_id(cons) if cons else None
        if prod is None or cons is None:
            seam_orphans.append(
                {
                    "edge_label": seam["edge_label"],
                    "symbol": seam["symbol"],
                    "missing_producer": None if prod else seam["producer_module"],
                    "missing_consumer": None if cons else seam["consumer_module"],
                }
            )
            continue
        edges.append(
            {
                "source": cons_id,
                "target": prod_id,
                "type": "cxa_seam",
                "edge_label": seam["edge_label"],
                "symbol": seam["symbol"],
                "direction": "forward",
                "weight": 1.0,
            }
        )
        node_by_id[cons_id]["cxa_role"].append(f"consumer:{seam['edge_label']}")
        node_by_id[prod_id]["cxa_role"].append(f"producer:{seam['edge_label']}")
        record = {
            "edge_label": seam["edge_label"],
            "symbol": seam["symbol"],
            "consumer_file": cons_id,
            "consumer_module": seam["consumer_module"],
            "consumer_axis": _axis_of(cons),
            "producer_file": prod_id,
            "producer_module": seam["producer_module"],
            "producer_axis": _axis_of(prod),
        }
        seam_records.append(record)
        # the consumer imports the symbol from the producer → outbound from consumer
        file_seams[cons_id]["outbound"].append(
            {
                "edge_label": record["edge_label"],
                "symbol": record["symbol"],
                "producer_file": prod_id,
                "producer_axis": record["producer_axis"],
            }
        )
        file_seams[prod_id]["inbound"].append(
            {
                "edge_label": record["edge_label"],
                "symbol": record["symbol"],
                "consumer_file": cons_id,
                "consumer_axis": record["consumer_axis"],
            }
        )

    # dedupe cxa_role lists + attach resolved seam endpoints to each node
    for node in nodes:
        node["cxa_role"] = sorted(set(node["cxa_role"]))
        node["cxa_seams"] = file_seams.get(node["id"], {"inbound": [], "outbound": []})

    # ---- substitution edges (file → H_T-*, the 15 direct carriers) ------ #
    subst_index = {s["id"]: s for s in substitutions}
    for s_id, file_ids in subst_to_files.items():
        meta = subst_index.get(s_id, {})
        for nid in file_ids:
            edges.append(
                {
                    "source": nid,
                    "target": f"substitution:{s_id}",
                    "type": "substitution_carrier",
                    "disposition": meta.get("disposition"),
                    "axis": meta.get("axis"),
                    "direction": "forward",
                    "weight": 1.0,
                }
            )

    # ---- orphan detection (the linter) ---------------------------------- #
    # (1) code-with-no-cite — RELIABLE
    uncited = [
        n["filePath"]
        for n in nodes
        if not _has_any_cite(
            {k: n[k] for k in ("spec_contracts", "unit_ids", "adrs", "substitutions")}
        )
        and n["name"] != "__init__.py"  # re-export aggregators legitimately bare
    ]
    # (2) substitution-with-no-H_T-carrier-file — RELIABLE but honest about thinness
    carried = set(subst_to_files.keys())
    substitution_no_carrier = [
        {"id": s["id"], "axis": s["axis"], "disposition": s["disposition"]}
        for s in substitutions
        if s["id"] not in carried
    ]
    # (3) cxa-seam-with-missing-producer-or-consumer-file — RELIABLE (already collected)
    # (4) contract-keyspace coverage — ADVISORY, canonical-head-scoped (RB-DOC-03).
    #     A C-* in a head file with no source-file cite may be a real implementation
    #     gap, an authoring-only contract, or an obsolete prose row. Contracts that
    #     cite ONLY superseded versions are phantoms and are EXCLUDED. Advisory; the
    #     linter flags but does not fail the build.
    head_md = canonical_head_md_files()
    spec_units = load_spec_units()
    contract_without_code = [
        {"id": contract, "spec_files": files}
        for contract, files in sorted(spec_contracts.items())
        if contract not in contract_to_files
        and contract not in DOCUMENTED_NON_CONTRACTS
        and any(sf in head_md for sf in files)
    ]
    # (5) unit-keyspace coverage — ADVISORY, canonical-head-scoped. Delta-only plans do
    #     NOT re-table historical units, so this catches only head-defined U-* with no
    #     code carrier. Known non-gaps may appear (range-marker IDs; units cited in src
    #     by their contract instead of the U-* token) — advisory, not a gate.
    unit_without_code = [
        {"id": unit, "spec_files": files}
        for unit, files in sorted(spec_units.items())
        if unit not in unit_to_files and any(sf in head_md for sf in files)
    ]

    # ---- assemble --------------------------------------------------------- #
    graph: dict[str, Any] = {
        "version": "1.0",
        "schema": "semantic-overlay/ua-compatible",
        "generator": "tools/semantic_overlay/overlay.py",
        "project": {
            "name": "arhugula-v2 (multi-LLM agent harness)",
            "overlay": "spec ↔ code ↔ CXA-seam ↔ substitution",
        },
        "nodes": nodes,
        "edges": edges,
        "seams": seam_records,
        "indices": {
            "contract_to_files": {k: sorted(v) for k, v in sorted(contract_to_files.items())},
            "unit_to_files": {k: sorted(v) for k, v in sorted(unit_to_files.items())},
            "adr_to_files": {k: sorted(v) for k, v in sorted(adr_to_files.items())},
            "substitution_to_files": {k: sorted(v) for k, v in sorted(subst_to_files.items())},
            "seam_by_label": {r["edge_label"]: r for r in seam_records},
            "spec_contract_to_files": spec_contracts,
        },
        "orphans": {
            "code_without_cite": sorted(uncited),
            "contract_without_code": contract_without_code,
            "unit_without_code": unit_without_code,
            "substitution_without_carrier": substitution_no_carrier,
            "cxa_seam_missing_endpoint": seam_orphans,
        },
        "stats": {
            "source_files": len(nodes),
            "files_with_cite": len(nodes) - len(uncited),
            "spec_contracts_total": len(spec_contracts),
            "spec_units_total": len(spec_units),
            "distinct_contracts": len(contract_to_files),
            "distinct_units": len(unit_to_files),
            "distinct_adrs": len(adr_to_files),
            "cxa_seams_total": len(seams),
            "cxa_seams_wired": len(seams) - len(seam_orphans),
            "substitutions_total": len(substitutions),
            "substitutions_with_carrier": len(carried),
            "edges_cxa": sum(1 for e in edges if e["type"] == "cxa_seam"),
            "edges_substitution": sum(1 for e in edges if e["type"] == "substitution_carrier"),
        },
    }
    return graph


# --------------------------------------------------------------------------- #
# Validation (the --check linter; HARD vs SOFT drift)
# --------------------------------------------------------------------------- #


def validate(graph: dict[str, Any]) -> list[str]:
    """Return HARD-drift violation strings (each → CI failure). Soft/advisory orphan
    classes (code-without-cite count, substitution thinness) are reported, not failed —
    they reflect genuine repo state, not a regression."""
    violations: list[str] = []
    orphans = graph["orphans"]

    # HARD: a genuine CXA seam whose producer OR consumer module no longer resolves to a
    # file means the seam test enumerates a symbol the code base dropped/renamed — real
    # cross-axis drift. This is the one class that MUST gate.
    for so in orphans["cxa_seam_missing_endpoint"]:
        miss = so.get("missing_producer") or so.get("missing_consumer")
        side = "producer" if so.get("missing_producer") else "consumer"
        violations.append(
            f"CXA seam {so['edge_label']} ({so['symbol']}): {side} module "
            f"'{miss}' does not resolve to any source file (PATTERN_P1_SEAMS drift)."
        )

    # HARD: the committed overlay.json (if present) must match the fresh derivation —
    # a stale committed artifact manufactures drift (stage-01 finding #2). Mirrors the
    # substitution-ledger snapshot-pin discipline.
    if OVERLAY_JSON.exists() and _overlay_json_is_tracked():
        committed = json.loads(OVERLAY_JSON.read_text(encoding="utf-8"))
        if committed.get("stats") != graph["stats"]:
            violations.append(
                "Committed overlay.json stats are stale vs HEAD — re-run "
                "`overlay.py build` and commit (a stale overlay manufactures drift)."
            )
    return violations


def _overlay_json_is_tracked() -> bool:
    """Return True only when overlay.json is part of the git index."""
    try:
        rel = OVERLAY_JSON.relative_to(REPO_ROOT)
    except ValueError:
        return False

    result = subprocess.run(
        ["git", "ls-files", "--error-unmatch", str(rel)],
        cwd=REPO_ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
        text=True,
    )
    return result.returncode == 0


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #


def _print_summary(graph: dict[str, Any]) -> None:
    s = graph["stats"]
    o = graph["orphans"]
    print("Semantic overlay — spec ↔ code ↔ CXA-seam ↔ substitution\n")
    print(f"  source files            : {s['source_files']}")
    print(
        f"  files carrying a cite   : {s['files_with_cite']} "
        f"({100 * s['files_with_cite'] / max(s['source_files'], 1):.1f} %)"
    )
    print(f"  distinct contracts cited: {s['distinct_contracts']}")
    print(f"  spec contracts scanned  : {s['spec_contracts_total']}")
    print(f"  distinct units cited    : {s['distinct_units']}")
    print(f"  distinct ADRs cited     : {s['distinct_adrs']}")
    print(
        f"  CXA seams               : {s['cxa_seams_wired']}/{s['cxa_seams_total']} wired "
        f"→ {s['edges_cxa']} edges"
    )
    print(
        f"  substitutions           : {s['substitutions_with_carrier']}/{s['substitutions_total']} "
        f"with a direct H_T-* carrier file → {s['edges_substitution']} edges"
    )
    print("\norphans (drift candidates):")
    print(f"  code without a cite          : {len(o['code_without_cite'])}")
    for fp in o["code_without_cite"]:
        print(f"      · {fp}")
    print(f"  CXA seam missing an endpoint : {len(o['cxa_seam_missing_endpoint'])} (HARD if >0)")
    for so in o["cxa_seam_missing_endpoint"]:
        print(f"      · {so['edge_label']} ({so['symbol']})")
    print(
        f"  contract w/o code cite      : {len(o['contract_without_code'])} "
        "(advisory — canonical-head-scoped; cite absence is not proof of non-implementation)"
    )
    for co in o["contract_without_code"]:
        print(f"      · {co['id']} ({', '.join(co['spec_files'])})")
    print(
        f"  unit w/o code cite          : {len(o['unit_without_code'])} "
        "(advisory — canonical-head-scoped; may include range-marker / contract-cited units)"
    )
    for uo in o["unit_without_code"]:
        print(f"      · {uo['id']} ({', '.join(uo['spec_files'])})")
    print(
        f"  substitution w/o carrier file: {len(o['substitution_without_carrier'])} "
        "(advisory — most carriers are named in rationale, not docstrings)"
    )


def _query(graph: dict[str, Any], args: argparse.Namespace) -> int:
    idx = graph["indices"]
    if args.contract:
        files = idx["contract_to_files"].get(args.contract, [])
        print(json.dumps({"contract": args.contract, "files": files}, indent=2))
        return 0 if files else 1
    if args.unit:
        files = idx["unit_to_files"].get(args.unit, [])
        # also surface any CXA seam where this unit is an endpoint (label e.g. U-CP-30→U-IS-12)
        seams = [r for r in graph["seams"] if args.unit in r["edge_label"]]
        print(json.dumps({"unit": args.unit, "files_citing": files, "cxa_seams": seams}, indent=2))
        return 0 if (files or seams) else 1
    if args.seam:
        rec = idx["seam_by_label"].get(args.seam)
        if rec is None:
            # tolerate a unit-id fragment: return all seams touching it
            matches = [r for r in graph["seams"] if args.seam in r["edge_label"]]
            print(json.dumps({"seam": args.seam, "matches": matches}, indent=2))
            return 0 if matches else 1
        print(json.dumps(rec, indent=2))
        return 0
    if args.adr:
        files = idx["adr_to_files"].get(args.adr, [])
        print(json.dumps({"adr": args.adr, "files": files}, indent=2))
        return 0 if files else 1
    if args.substitution:
        files = idx["substitution_to_files"].get(args.substitution, [])
        subst = next(
            (s for s in load_substitutions() if s["id"] == args.substitution),
            None,
        )
        print(json.dumps({"substitution": subst, "carrier_files": files}, indent=2))
        return 0 if subst else 1
    if args.file:
        target = f"file:{args.file}" if not args.file.startswith("file:") else args.file
        node = next(
            (n for n in graph["nodes"] if n["id"] == target or n["filePath"] == args.file), None
        )
        if node is None:
            print(f"no node for {args.file}", file=sys.stderr)
            return 1
        print(json.dumps(node, indent=2))
        return 0
    if args.orphans:
        print(json.dumps(graph["orphans"], indent=2))
        return 0
    print(
        "specify one of --contract/--unit/--adr/--substitution/--file/--seam/--orphans",
        file=sys.stderr,
    )
    return 2


def _enrich_ua(graph: dict[str, Any], ua_path: Path) -> int:
    """Left-join the overlay attrs onto an existing Understand-Anything KG (by ua_id).
    Writes ``<name>.overlay.json`` next to it — never mutates the original in place."""
    ua_path = ua_path.resolve()
    ua = json.loads(ua_path.read_text(encoding="utf-8"))
    by_ua_id = {n["ua_id"]: n for n in graph["nodes"]}
    matched = 0
    for node in ua.get("nodes", []):
        ov = by_ua_id.get(node.get("id"))
        if ov is None:
            continue
        matched += 1
        node["overlay"] = {
            "spec_contracts": ov["spec_contracts"],
            "unit_ids": ov["unit_ids"],
            "adrs": ov["adrs"],
            "substitutions": ov["substitutions"],
            "cxa_role": ov["cxa_role"],
            "axis": ov["axis"],
        }
    # carry the cxa seam edges that connect two enriched nodes
    ua_ids = {n["id"] for n in ua.get("nodes", [])}
    repo_to_ua = {n["id"]: n["ua_id"] for n in graph["nodes"]}
    seam_edges = []
    for e in graph["edges"]:
        if e["type"] != "cxa_seam":
            continue
        src = repo_to_ua.get(e["source"])
        tgt = repo_to_ua.get(e["target"])
        if src in ua_ids and tgt in ua_ids:
            seam_edges.append({**e, "source": src, "target": tgt})
    ua.setdefault("edges", []).extend(seam_edges)
    out = ua_path.with_suffix(".overlay.json")
    out.write_text(json.dumps(ua, indent=2) + "\n", encoding="utf-8")
    print(f"enriched {matched} nodes + {len(seam_edges)} cxa edges → {_rel(out)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("build", help="write overlay.json from HEAD")
    sub.add_parser("summary", help="human-readable counts + orphan report")
    sub.add_parser("check", help="CI gate; exit 1 on hard drift")
    p_json = sub.add_parser("json", help="emit the full overlay graph to stdout")
    p_json.add_argument("--indent", type=int, default=2)

    p_q = sub.add_parser("query", help="agent-facing reference lookups")
    p_q.add_argument("--contract", help="files citing a C-*-NN contract")
    p_q.add_argument("--unit", help="files citing a U-*-NN unit + seams where it is an endpoint")
    p_q.add_argument("--adr", help="files citing an ADR-*")
    p_q.add_argument("--substitution", help="H_T-* substitution metadata + carrier files")
    p_q.add_argument("--file", help="a file's full overlay node (cites + resolved CXA seams)")
    p_q.add_argument("--seam", help="resolve a CXA seam by edge_label (or a unit-id fragment)")
    p_q.add_argument("--orphans", action="store_true")

    p_e = sub.add_parser("enrich-ua", help="left-join overlay onto an Understand-Anything KG")
    p_e.add_argument("ua_path", help="path to a knowledge-graph.json")

    args = parser.parse_args(argv)
    graph = derive()  # always fresh from HEAD

    if args.cmd == "build":
        OVERLAY_JSON.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
        print(
            f"wrote {_rel(OVERLAY_JSON)} — {graph['stats']['source_files']} nodes, "
            f"{len(graph['edges'])} edges"
        )
        return 0
    if args.cmd == "summary":
        _print_summary(graph)
        return 0
    if args.cmd == "check":
        violations = validate(graph)
        if violations:
            print("SEMANTIC-OVERLAY DRIFT (hard):", file=sys.stderr)
            for v in violations:
                print(f"  ✗ {v}", file=sys.stderr)
            return 1
        print(
            f"semantic overlay OK — {graph['stats']['source_files']} nodes, "
            f"{graph['stats']['cxa_seams_wired']}/{graph['stats']['cxa_seams_total']} seams wired"
        )
        return 0
    if args.cmd == "json":
        print(json.dumps(graph, indent=args.indent))
        return 0
    if args.cmd == "query":
        return _query(graph, args)
    if args.cmd == "enrich-ua":
        return _enrich_ua(graph, Path(args.ua_path))
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
