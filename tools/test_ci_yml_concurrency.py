"""U-HE-24 — ci.yml concurrency keyed by SHA for `main` pushes (C-HE-06 §4).

The merge door (C-HE-06 §4(vii)) holds its lease until the merge commit's OWN
post-merge run reaches `success`. With the group keyed by `github.ref`, every
push to `main` shares one concurrency group, so lane B's landing would cancel
lane A's post-merge run and A could never satisfy (vii). Keying `main` pushes
by SHA gives each merge commit its own group; PR-event semantics are unchanged.
"""

from pathlib import Path

import yaml

_CI_YML = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yml"


def test_main_push_concurrency_keyed_by_sha() -> None:
    ci = yaml.safe_load(_CI_YML.read_text())
    group = ci["concurrency"]["group"]
    # push only fires for main; WO-U10 groups PR runs by PR number (see
    # test_ci_result_binding.py routing lens for the evaluated behavior).
    assert "github.event_name == 'push' && github.sha ||" in group
    assert ci["concurrency"]["cancel-in-progress"] == "${{ github.event_name != 'push' }}"


def test_group_prefix_unchanged() -> None:
    # The group still namespaces by workflow; a PR's superseded runs share its
    # PR-number group and keep cancelling (WO-U10).
    ci = yaml.safe_load(_CI_YML.read_text())
    group = ci["concurrency"]["group"]
    assert group.startswith("ci-${{ github.workflow }}-")
