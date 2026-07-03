"""Tests for U-MEM-25 memory closeout documentation evidence."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_checker():
    path = ROOT / "tools" / "memory_closeout_check.py"
    assert path.is_file(), "tools/memory_closeout_check.py must exist"
    spec = importlib.util.spec_from_file_location("memory_closeout_check", path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_memory_prd_and_contract_id_extraction() -> None:
    checker = _load_checker()

    assert checker.r_mem_ids(ROOT) == tuple(f"R-MEM-{index:02d}" for index in range(1, 16))
    assert checker.c_mem_ids(ROOT) == tuple(f"C-MEM-{index:02d}" for index in range(1, 21))


def test_memory_closeout_evidence_is_complete() -> None:
    checker = _load_checker()

    report = checker.validate(ROOT)

    assert report.ready, [check.detail for check in report.checks if not check.ok]


def test_memory_docs_are_operator_discoverable_and_source_grounded() -> None:
    checker = _load_checker()
    docs_index = ROOT / "docs" / "README.md"
    memory_doc = ROOT / "docs" / "memory-substrate.md"
    evidence = ROOT / ".harness" / "u-mem-25-memory-closeout-evidence.md"

    assert "memory-substrate.md" in docs_index.read_text(encoding="utf-8")
    assert memory_doc.is_file()
    assert evidence.is_file()
    checker.validate_markdown_links(ROOT, (docs_index, memory_doc, evidence))
