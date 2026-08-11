"""Tests for `tools/clearance_frontmatter.py` (R-CTX-1 / U-CTX-10).

Two halves:
  * the LIVE corpus — every `.harness/clearance/*.md` parses or is manifest-exempt;
  * the GATE ITSELF — fail-closed behaviour, proved with synthetic directories so the
    negative cases never depend on the live corpus being broken.
"""

from __future__ import annotations

import json
from pathlib import Path

import clearance_frontmatter as cf
import pytest
import yaml

# ── live corpus ─────────────────────────────────────────────────────────────────────────


def test_live_corpus_passes_the_gate() -> None:
    assert cf.check() == []


def test_live_corpus_has_no_unparseable_non_exempt_marker() -> None:
    manifest = cf.load_manifest()
    for path in cf.iter_marker_paths():
        if path.name in manifest:
            continue
        cf.parse_marker(path)  # raises on failure — that IS the assertion


def test_manifest_rows_all_exist_and_are_still_non_markers() -> None:
    manifest = cf.load_manifest()
    assert manifest, "the exemption manifest must not be empty-by-accident"
    for name, (klass, reason) in manifest.items():
        path = cf.CLEARANCE_DIR / name
        assert path.exists(), f"{name} listed in the manifest but absent"
        assert klass.strip("`"), f"{name} has no exemption class"
        assert reason.strip(), f"{name} has no exemption reason"
        with pytest.raises(cf.ClearanceFrontmatterError):
            cf.parse_marker(path)


def test_repair_is_idempotent_on_the_live_corpus(tmp_path: Path) -> None:
    """Re-running the repairer over the corpus-as-committed must change nothing."""
    for path in cf.iter_marker_paths():
        block = cf.split_frontmatter(path.read_text(encoding="utf-8"))
        if block is None or path.name in cf.load_manifest():
            continue
        assert cf.repair_frontmatter(block) == block, f"{path.name} would still be rewritten"


# ── the repair contract ─────────────────────────────────────────────────────────────────


def test_repair_quotes_a_colon_space_scalar_preserving_the_text() -> None:
    block = "artifact: design-substrate/X.md\nversion: v1.0\nnote: Reading A: the wide one\n"
    repaired = cf.repair_frontmatter(block)
    parsed = yaml.safe_load(repaired)
    assert parsed["note"] == "Reading A: the wide one"
    assert 'note: "Reading A: the wide one"' in repaired


def test_repair_quotes_a_whitespace_hash_scalar_that_would_silently_truncate() -> None:
    block = "artifact: design-substrate/X.md\nversion: v1.0\nnote: merged at PR #529\n"
    # The hazard: unrepaired, YAML reads this as `merged at PR` — a silent content loss.
    assert yaml.safe_load(block)["note"] == "merged at PR"
    parsed = yaml.safe_load(cf.repair_frontmatter(block))
    assert parsed["note"] == "merged at PR #529"


def test_repair_leaves_a_clean_scalar_byte_identical() -> None:
    block = (
        "artifact: design-substrate/X.md\nversion: v1.0\ncleared_at: 2026-06-13T19:30:00-06:00\n"
    )
    assert cf.repair_frontmatter(block) == block


def test_repair_folds_a_multiline_plain_scalar_into_one_quoted_line() -> None:
    block = (
        "artifact: design-substrate/X.md\nversion: v1.0\n"
        "reviewer_chain:\n  - first: part\n      second part\n"
    )
    repaired = cf.repair_frontmatter(block)
    assert yaml.safe_load(repaired)["reviewer_chain"] == ["first: part second part"]
    assert repaired.count("\n") == 4  # the continuation line is folded away


def test_repair_never_edits_the_body() -> None:
    text = (
        "---\nartifact: design-substrate/X.md\nversion: v1.0\nnote: a: b\n---\n"
        "\n# Body\n\nprose: with colon\n"
    )
    block = cf.split_frontmatter(text)
    assert block is not None
    tail = text[len(cf.FRONTMATTER_OPEN) + len(block) :]
    rebuilt = cf.FRONTMATTER_OPEN + cf.repair_frontmatter(block) + tail
    assert rebuilt.split("\n---\n", 1)[1] == text.split("\n---\n", 1)[1]


def test_repair_emits_json_quoting_which_is_valid_yaml_for_awkward_text() -> None:
    awkward = 'a: b — "quoted" \\ backslash # hash\ttab'
    block = f"artifact: design-substrate/X.md\nversion: v1.0\nnote: {awkward}\n"
    repaired = cf.repair_frontmatter(block)
    assert json.dumps(awkward, ensure_ascii=False) in repaired
    assert yaml.safe_load(repaired)["note"] == awkward


def test_repair_refuses_an_unmodelled_line_instead_of_guessing() -> None:
    # A flush-left line that is neither a key, a list item, nor a continuation.
    block = "artifact: design-substrate/X.md\nversion: v1.0\nbare text line\n"
    with pytest.raises(cf.ClearanceFrontmatterError):
        cf.repair_frontmatter(block)


def test_repair_leaves_an_already_quoted_scalar_byte_identical() -> None:
    """Idempotence: an explicitly-quoted scalar must never be re-quoted (double-escaped)."""
    block = 'artifact: design-substrate/X.md\nversion: v1.0\nnote: "already: quoted"\n'
    assert cf.repair_frontmatter(block) == block
    # And a second pass over the repairer's OWN output is a no-op.
    once = cf.repair_frontmatter("artifact: design-substrate/X.md\nversion: v1.0\nnote: a: b\n")
    assert cf.repair_frontmatter(once) == once


# ── fail-closed gate behaviour ──────────────────────────────────────────────────────────


def _seed(directory: Path, name: str, body: str) -> Path:
    path = directory / name
    path.write_text(body, encoding="utf-8")
    return path


GOOD = "---\nartifact: design-substrate/X.md\nversion: v1.0\n---\n\nbody\n"
BROKEN = "---\nartifact: design-substrate/X.md\nversion: v1.0\nnote: a: b\n---\n\nbody\n"
NO_FM = "# Just a document\n"


def test_gate_fails_on_an_unlisted_broken_marker(tmp_path: Path) -> None:
    _seed(tmp_path, "good-v1-0-cleared-2026-01-01.md", GOOD)
    _seed(tmp_path, "bad-v1-0-cleared-2026-01-01.md", BROKEN)
    violations = cf.check(tmp_path, tmp_path / "parse-manifest.md")
    assert len(violations) == 1
    assert "bad-v1-0-cleared-2026-01-01.md" in violations[0]


def test_gate_fails_on_an_unlisted_frontmatter_less_file(tmp_path: Path) -> None:
    _seed(tmp_path, "stray.md", NO_FM)
    violations = cf.check(tmp_path, tmp_path / "parse-manifest.md")
    assert len(violations) == 1
    assert "no YAML frontmatter" in violations[0]


def test_gate_fails_on_a_marker_missing_artifact_or_version(tmp_path: Path) -> None:
    _seed(tmp_path, "m.md", "---\nartifact: design-substrate/X.md\n---\n\nbody\n")
    violations = cf.check(tmp_path, tmp_path / "parse-manifest.md")
    assert len(violations) == 1
    assert "missing `version`" in violations[0]


def test_gate_fails_on_a_manifest_row_whose_file_vanished(tmp_path: Path) -> None:
    _seed(tmp_path, "good-v1-0-cleared-2026-01-01.md", GOOD)
    manifest = _seed(
        tmp_path,
        "parse-manifest.md",
        "| File | Class | Reason |\n|---|---|---|\n| `ghost.md` | `not-a-marker` | gone |\n",
    )
    violations = cf.check(tmp_path, manifest)
    assert any("ghost.md" in v and "absent" in v for v in violations)


def test_gate_fails_on_a_stale_exemption_that_now_parses(tmp_path: Path) -> None:
    _seed(tmp_path, "good-v1-0-cleared-2026-01-01.md", GOOD)
    manifest = _seed(
        tmp_path,
        "parse-manifest.md",
        "| File | Class | Reason |\n|---|---|---|\n"
        "| `good-v1-0-cleared-2026-01-01.md` | `not-a-marker` | stale |\n",
    )
    violations = cf.check(tmp_path, manifest)
    assert any("stale exemption" in v for v in violations)


def test_a_missing_manifest_exempts_nothing(tmp_path: Path) -> None:
    """An absent manifest must be the EMPTY exemption set, never a permissive one."""
    _seed(tmp_path, "stray.md", NO_FM)
    assert cf.load_manifest(tmp_path / "does-not-exist.md") == {}
    assert cf.check(tmp_path, tmp_path / "does-not-exist.md")


def test_gate_passes_when_every_broken_file_is_listed(tmp_path: Path) -> None:
    _seed(tmp_path, "good-v1-0-cleared-2026-01-01.md", GOOD)
    _seed(tmp_path, "stray.md", NO_FM)
    manifest = _seed(
        tmp_path,
        "parse-manifest.md",
        "| File | Class | Reason |\n|---|---|---|\n"
        "| `parse-manifest.md` | `not-a-marker` | self |\n"
        "| `stray.md` | `no-frontmatter` | narrative record |\n",
    )
    assert cf.check(tmp_path, manifest) == []


def test_block_scalar_frontmatter_is_preserved_byte_identically(tmp_path: Path) -> None:
    """codex round-1 (PR-4): a literal/folded block scalar carries an explicit
    YAML style — the repairer must NEVER collapse it into a quoted string with
    the style token as content (the corruption shipped on two real markers)."""
    block = (
        "artifact: design-substrate/X_v1.md\n"
        "version: v1.0\n"
        "notes: |\n"
        "  A body line with a : colon-space hazard inside the block.\n"
        "  A second line # with a hash.\n"
        "summary:\n"
        "  - >-\n"
        "    folded entry line one\n"
        "    line two\n"
    )
    repaired = cf.repair_frontmatter(block)
    assert "notes: |\n" in repaired
    assert "- >-\n" in repaired
    assert '"|' not in repaired and '">-' not in repaired
    # idempotent: a second pass changes nothing
    assert cf.repair_frontmatter(repaired) == repaired
