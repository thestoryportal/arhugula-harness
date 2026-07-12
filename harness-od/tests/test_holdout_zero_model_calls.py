"""B-OD17-EVAL-LOOP-TOOLING — zero-model-calls control assert.

Acceptance: "zero model calls in the loop (control assert)"
(`.harness/r-fs-2-final-closure-implementation-plan-v1.md` §3
B-OD17-EVAL-LOOP-TOOLING). Per the standing model-judge-as-governance-gate
refusal (`[[eval-harness-refused-as-governance-gate]]`), none of the three
holdout-loop modules may import or call an LLM client, provider SDK, or the
harness's own dispatcher — this is a structural check, not a behavioral
mock, so it cannot be defeated by a code path the specific test scenario
happens not to exercise.
"""

from __future__ import annotations

import ast
from pathlib import Path

import harness_od.holdout_assertion_scaffold as scaffold_module
import harness_od.holdout_review_ledger as ledger_module
import harness_od.holdout_set as holdout_module

_MODEL_RELATED_TOKENS = (
    "anthropic",
    "openai",
    "ollama",
    "llm",
    "dispatcher",
    "provider",
    "judge",
)


def _imported_module_names(source_path: Path) -> set[str]:
    tree = ast.parse(source_path.read_text())
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_holdout_modules_import_no_model_related_module() -> None:
    """None of the three holdout-loop modules import anything whose module
    path contains a model/provider/judge-shaped token."""
    for module in (holdout_module, ledger_module, scaffold_module):
        source_path = Path(module.__file__)  # type: ignore[arg-type]
        imported = _imported_module_names(source_path)
        offending = {
            name
            for name in imported
            if any(token in name.lower() for token in _MODEL_RELATED_TOKENS)
        }
        assert not offending, f"{module.__name__} imports model-related module(s): {offending}"


def test_holdout_modules_do_not_reference_model_call_identifiers_in_source() -> None:
    """Belt-and-suspenders: no model/provider/judge token appears anywhere in
    the three modules' own source text (docstrings aside — this catches a
    call added without a corresponding top-level import, e.g. a lazy
    `import anthropic` inside a function body)."""
    for module in (holdout_module, ledger_module, scaffold_module):
        source_path = Path(module.__file__)  # type: ignore[arg-type]
        tree = ast.parse(source_path.read_text())
        call_names: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                call_names.update(alias.name.lower() for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                call_names.add(node.module.lower())
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                call_names.add(node.func.id.lower())
        offending = {
            name for name in call_names if any(token in name for token in _MODEL_RELATED_TOKENS)
        }
        assert not offending, f"{module.__name__} references: {offending}"
