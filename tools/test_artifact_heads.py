"""Tests for `tools/artifact_heads.py` (R-CTX-1 / U-CTX-11).

Three properties this tool exists to get right, each pinned here:
  * FAIL-CLOSED — an unparseable marker aborts the derivation; there is no regex fallback;
  * FAMILY NORMALIZATION — both marker-filename conventions land on one family;
  * VERSION-AWARE SORT — `v1.9 < v1.10 < v1.116`, not lexicographic.
Plus the two gates (generated-vs-committed, marker-completeness) in both directions.
"""

from __future__ import annotations

import re
from pathlib import Path

import artifact_heads as ah
import clearance_frontmatter as cf
import pytest

# ── family normalization: the corpus's TWO filename conventions ─────────────────────────


def test_both_marker_filename_conventions_resolve_to_one_family() -> None:
    """The CamelCase and all-kebab marker filenames must not split a family in two."""
    camel = cf.CLEARANCE_DIR / "Spec_Control_Plane-v1_32-cleared-2026-06-13.md"
    kebab = cf.CLEARANCE_DIR / "spec-control-plane-v1-116-cleared-2026-08-09.md"
    assert camel.exists() and kebab.exists(), "both conventions must still be present"
    assert ah.family_of(cf.parse_marker(camel).artifact) == "spec-control-plane"
    assert ah.family_of(cf.parse_marker(kebab).artifact) == "spec-control-plane"


def test_family_is_derived_from_the_artifact_field_not_the_filename() -> None:
    """11 marker filenames disagree with their own artifact field — the field wins.

    A filename-derived family would emit `prd-v1-2` / `cross-axis-composition`; both are
    wrong, and the second would split the CXA family across two rows.
    """
    cases = {
        "PRD_v1_2-cleared-2026-07-09.md": "prd",
        "cross-axis-composition-v2-23-cleared-2026-07-30.md": "cross-axis-composition-document",
        "Cross_Axis_Composition_Document-v2_17-cleared-2026-05-31.md": (
            "cross-axis-composition-document"
        ),
        "Spec_Memory_Substrate_v1-cleared-2026-07-09.md": "spec-memory-substrate",
        "spec-memory-substrate-v1-3-cleared-2026-08-06.md": "spec-memory-substrate",
    }
    for name, expected in cases.items():
        path = cf.CLEARANCE_DIR / name
        assert path.exists(), name
        assert ah.family_of(cf.parse_marker(path).artifact) == expected


def test_family_strips_only_the_version_suffix() -> None:
    assert ah.family_of("design-substrate/Spec_Control_Plane_v1_116.md") == "spec-control-plane"
    assert ah.family_of("design-substrate/Spec_Action_Surface_v1.md") == "spec-action-surface"
    assert ah.family_of("design-substrate/ADR-D7_memory_substrate.md") == "adr-d7-memory-substrate"
    assert ah.family_of("design-substrate/ADR-D2.md") == "adr-d2"


# ── version-aware sort ──────────────────────────────────────────────────────────────────


def test_versions_sort_numerically_not_lexicographically() -> None:
    ordered = ["v1.9", "v1.10", "v1.32", "v1.99", "v1.116"]
    assert sorted(ordered, key=ah.version_key) == ordered
    # The failure mode this replaces: a plain string sort inverts the pair.
    assert sorted(["v1.9", "v1.116"]) == ["v1.116", "v1.9"]
    assert ah.version_key("v1.116") > ah.version_key("v1.9")


def test_version_tolerates_a_trailing_annotation_but_still_orders_on_the_token() -> None:
    assert ah.version_key("v1.32 (in-place correction; version label unchanged)")[1] == (1, 32)
    assert ah.is_numbered("v1 (Proposed, 2026-07-01)")


def test_an_unnumbered_label_orders_below_every_version_and_is_not_dropped() -> None:
    label = "§10-amendment (prefer-OAuth default)"
    assert not ah.is_numbered(label)
    assert ah.version_key(label) < ah.version_key("v0.1")


def test_an_empty_version_is_an_error() -> None:
    with pytest.raises(ah.ArtifactHeadsError):
        ah.version_key("   ")


# ── live derivation ─────────────────────────────────────────────────────────────────────


def test_every_family_resolves_to_exactly_one_head() -> None:
    heads = ah.derive()
    assert heads
    assert len({h.family for h in heads}) == len(heads)


def test_head_versions_match_the_marker_the_row_names() -> None:
    """Each row's head version must be the version of the marker it cites — no drift."""
    for head in ah.derive():
        marker = cf.parse_marker(cf.CLEARANCE_DIR / head.marker)
        assert marker.version.strip() == head.version
        assert marker.artifact == head.artifact


def test_head_is_the_maximum_version_in_its_family() -> None:
    heads = {h.family: h for h in ah.derive()}
    seen: dict[str, list[str]] = {}
    for marker in cf.load_all_markers():
        seen.setdefault(ah.family_of(marker.artifact), []).append(marker.version)
    for family, versions in seen.items():
        best = max(versions, key=ah.version_key)
        assert ah.version_key(heads[family].version) == ah.version_key(best), family


def test_control_plane_head_is_the_highest_numbered_not_the_lexicographic_one() -> None:
    """The load-bearing case: 91 CP markers, and v1.99 sorts above v1.116 as a string."""
    cp = next(h for h in ah.derive() if h.family == "spec-control-plane")
    assert ah.version_key(cp.version) == max(
        ah.version_key(m.version)
        for m in cf.load_all_markers()
        if ah.family_of(m.artifact) == "spec-control-plane"
    )
    assert ah.version_key(cp.version)[1] > ah.version_key("v1.99")[1]


# ── fail-closed ─────────────────────────────────────────────────────────────────────────


def _seed(directory: Path, name: str, body: str) -> None:
    (directory / name).write_text(body, encoding="utf-8")


GOOD = (
    "---\nartifact: design-substrate/Spec_X_v1_2.md\nversion: v1.2\n"
    "cleared_at: 2026-01-01\n---\n\nbody\n"
)
BROKEN = "---\nartifact: design-substrate/Spec_X_v1_3.md\nversion: v1.3\nnote: a: b\n---\n\nbody\n"


def test_derivation_aborts_on_an_unparseable_marker_rather_than_skipping_it(
    tmp_path: Path,
) -> None:
    _seed(tmp_path, "good.md", GOOD)
    _seed(tmp_path, "broken.md", BROKEN)
    with pytest.raises(ah.ArtifactHeadsError) as exc:
        ah.derive(tmp_path, tmp_path / "parse-manifest.md")
    assert "not fully parseable" in str(exc.value)


def test_a_broken_marker_would_otherwise_have_changed_the_head(tmp_path: Path) -> None:
    """The counterfactual: skipping `broken.md` silently reports v1.2 as the head."""
    _seed(tmp_path, "good.md", GOOD)
    heads = ah.derive(tmp_path, tmp_path / "parse-manifest.md")
    assert [h.version for h in heads] == ["v1.2"]
    _seed(tmp_path, "broken.md", BROKEN)  # its real version is v1.3 — the true head
    with pytest.raises(ah.ArtifactHeadsError):
        ah.derive(tmp_path, tmp_path / "parse-manifest.md")


def test_cli_exits_nonzero_when_the_corpus_cannot_be_derived(tmp_path: Path) -> None:
    _seed(tmp_path, "broken.md", BROKEN)
    code = ah.main(["--check", "--dir", str(tmp_path), "--manifest", str(tmp_path / "none.md")])
    assert code == 1


# ── gate 1: generated == committed ──────────────────────────────────────────────────────


def test_committed_table_matches_the_generated_one() -> None:
    assert ah.check_generated_matches_committed() == []


def test_gate_fails_when_the_committed_table_is_stale(tmp_path: Path) -> None:
    corpus = tmp_path / "clearance"
    corpus.mkdir()
    _seed(corpus, "good.md", GOOD)
    table = tmp_path / "artifact-heads.md"
    table.write_text("# stale\n", encoding="utf-8")
    violations = ah.check_generated_matches_committed(table, corpus, tmp_path / "none.md")
    assert len(violations) == 1
    assert "stale" in violations[0]


def test_gate_fails_when_the_committed_table_is_missing(tmp_path: Path) -> None:
    _seed(tmp_path, "good.md", GOOD)
    violations = ah.check_generated_matches_committed(
        tmp_path / "absent.md", tmp_path, tmp_path / "none.md"
    )
    assert len(violations) == 1
    assert "missing" in violations[0]


def test_regenerating_the_table_closes_the_gate(tmp_path: Path) -> None:
    corpus = tmp_path / "clearance"
    corpus.mkdir()
    _seed(corpus, "good.md", GOOD)
    table = tmp_path / "artifact-heads.md"
    table.write_text(ah.render(ah.derive(corpus, tmp_path / "none.md")), encoding="utf-8")
    assert ah.check_generated_matches_committed(table, corpus, tmp_path / "none.md") == []


# ── gate 2: marker completeness ─────────────────────────────────────────────────────────


def test_live_completeness_gate_is_green() -> None:
    assert ah.check_completeness() == []


def test_completeness_fails_when_a_head_names_a_missing_artifact(tmp_path: Path) -> None:
    _seed(
        tmp_path,
        "ghost.md",
        "---\nartifact: design-substrate/Does_Not_Exist_v9_9.md\nversion: v9.9\n---\n\nbody\n",
    )
    violations = ah.check_completeness(tmp_path, tmp_path / "none.md")
    assert any("missing artifact" in v for v in violations)


def test_completeness_fails_on_a_design_substrate_head_with_no_version_number(
    tmp_path: Path,
) -> None:
    _seed(
        tmp_path,
        "labelled.md",
        "---\nartifact: design-substrate/Spec_Action_Surface_v1.md\n"
        "version: §10-amendment\n---\n\nbody\n",
    )
    violations = ah.check_completeness(tmp_path, tmp_path / "none.md")
    assert any("unnumbered label" in v for v in violations)


def test_every_family_carrying_a_marker_appears_in_the_committed_table() -> None:
    table = ah.TABLE_PATH.read_text(encoding="utf-8")
    families = {ah.family_of(m.artifact) for m in cf.load_all_markers()}
    assert families, "the corpus must not be empty"
    for family in families:
        assert f"| `{family}` |" in table, family


# ── R-CTX-1 / U-CTX-12: live head venues agree with the derived table ───────────────────
# The stale-carry defect this arc closed: root `CLAUDE.md` §2.3 named the AS spec head as
# `v1.13` and §2.4 named `Implementation_Plan_Action_Surface_v1_4.md`, while the corpus had
# cleared `v1.14` / `v1.6` on 2026-07-15 — a gap the AS spec's own clearance marker Notes
# had flagged as owed. These pins keep every live head venue tied to the DERIVED head.
# Nothing below hardcodes a version; every expectation comes from `derive()`.

LIVE_HEAD_VENUES = (
    "CLAUDE.md",
    ".harness/artifact-pointers/is.md",
    ".harness/artifact-pointers/as.md",
    ".harness/artifact-pointers/cp.md",
    ".harness/artifact-pointers/od.md",
    ".harness/artifact-pointers/runtime.md",
    ".harness/artifact-pointers/memory.md",
    ".harness/artifact-pointers/cxa.md",
    "harness-is/CLAUDE.md",
    "harness-as/CLAUDE.md",
    "harness-cp/CLAUDE.md",
    "harness-od/CLAUDE.md",
    "AGENTS.md",
    "CONTEXT.md",
)

# (venue, family) pairs that MUST name the derived head adjacent to the artifact name.
HEAD_PINS = (
    ("CLAUDE.md", "spec-action-surface"),
    ("CLAUDE.md", "spec-information-substrate"),
    ("CLAUDE.md", "spec-memory-substrate"),
    ("CLAUDE.md", "spec-control-plane"),
    ("CLAUDE.md", "spec-operational-discipline"),
    ("CLAUDE.md", "spec-harness-runtime"),
    (".harness/artifact-pointers/as.md", "spec-action-surface"),
    (".harness/artifact-pointers/is.md", "spec-information-substrate"),
    (".harness/artifact-pointers/memory.md", "spec-memory-substrate"),
    ("harness-as/CLAUDE.md", "spec-action-surface"),
    ("harness-is/CLAUDE.md", "spec-information-substrate"),
)

# Families whose head is encoded in a VERSIONED filename — the venue must name that file.
FILENAME_PINS = (
    ("CLAUDE.md", "implementation-plan-action-surface"),
    ("CLAUDE.md", "implementation-plan-information-substrate"),
    ("CLAUDE.md", "implementation-plan-control-plane"),
    ("CLAUDE.md", "implementation-plan-operational-discipline"),
    ("CLAUDE.md", "implementation-plan-harness-runtime"),
    ("CLAUDE.md", "cross-axis-composition-document"),
    (".harness/artifact-pointers/as.md", "implementation-plan-action-surface"),
    (".harness/artifact-pointers/is.md", "implementation-plan-information-substrate"),
    (".harness/artifact-pointers/cxa.md", "cross-axis-composition-document"),
)

_ADJACENT_WINDOW = 90


@pytest.mark.parametrize(("venue", "family"), HEAD_PINS)
def test_live_venue_names_the_derived_head_adjacent_to_the_artifact(
    venue: str, family: str
) -> None:
    head = next(h for h in ah.derive() if h.family == family)
    basename = head.artifact.rsplit("/", 1)[-1]
    text = (ah.REPO_ROOT / venue).read_text(encoding="utf-8")
    windows = []
    start = 0
    while (idx := text.find(basename, start)) != -1:
        windows.append(text[idx : idx + len(basename) + _ADJACENT_WINDOW])
        start = idx + 1
    assert windows, f"{venue} does not mention {basename}"
    assert any(head.version in w for w in windows), (
        f"{venue} names {basename} but not its derived head {head.version} within "
        f"{_ADJACENT_WINDOW} chars — the stale-carry shape this pin exists to catch"
    )


@pytest.mark.parametrize(("venue", "family"), FILENAME_PINS)
def test_live_venue_names_the_derived_head_filename(venue: str, family: str) -> None:
    head = next(h for h in ah.derive() if h.family == family)
    basename = head.artifact.rsplit("/", 1)[-1]
    text = (ah.REPO_ROOT / venue).read_text(encoding="utf-8")
    assert basename in text, f"{venue} does not name the derived head file {basename}"


def test_no_live_venue_still_carries_the_superseded_as_head() -> None:
    """The E6-scoped stale-AS gate, as an assertion rather than a one-off grep.

    Scoped to LIVE head venues with the version bound ADJACENT to the AS artifact name.
    `design-substrate/**` is excluded by construction: it is immutable here (X-AL-3) and
    legitimately contains the whole version history.
    """
    stale = re.compile(
        r"Action_Surface_v1_4"
        r"|Spec_Action_Surface_v1\.md[^\n]{0,60}v1\.13"
        r"|v1\.13[^\n]{0,60}Spec_Action_Surface"
    )
    # Positive control: the pattern must fire on the pre-repair shape.
    assert stale.search("AS `Spec_Action_Surface_v1.md` (v1.13), CP ...")
    assert stale.search("AS `Implementation_Plan_Action_Surface_v1_4.md`, CP ...")

    hits = []
    for venue in LIVE_HEAD_VENUES:
        path = ah.REPO_ROOT / venue
        if not path.exists():
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if stale.search(line):
                hits.append(f"{venue}:{lineno}")
    assert hits == [], f"superseded AS head still carried at: {hits}"
