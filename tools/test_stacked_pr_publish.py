"""The published head's synchronize event must see the intended PR base."""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stacked_pr_publish as sp

OLD = "a" * 40
FINAL = "b" * 40
MAIN = "d" * 40


class Remote:
    def __init__(self, base="stack", head=OLD):
        self.pr = {
            "state": "OPEN",
            "baseRefName": base,
            "baseRefOid": MAIN,
            "headRefName": "feature",
            "headRefOid": head,
            "isCrossRepository": False,
            "url": "https://github.com/owner/repo/pull/17",
        }
        self.events = []

    def __call__(self, *args):
        if args[:3] == ("gh", "pr", "view"):
            return json.dumps(self.pr)
        if args[:3] == ("gh", "pr", "edit"):
            self.pr["baseRefName"] = args[-1]
            self.events.append(("edited", self.pr["baseRefName"]))
            return ""
        if args[:2] == ("git", "rev-parse"):
            return FINAL + "\n"
        if args[:3] == ("git", "remote", "get-url"):
            return "https://github.com/owner/repo.git\n"
        if args[:2] == ("git", "merge-base"):
            return ""
        if args[:2] == ("git", "ls-remote"):
            sha = MAIN if args[-1] == "refs/heads/main" else OLD
            return sha + "\t" + args[-1] + "\n"
        if args[:2] == ("git", "push"):
            self.events.append(("synchronize", self.pr["baseRefName"]))
            return ""
        raise AssertionError(args)


def test_retarget_finishes_before_publishing_final_head():
    remote = Remote()
    sp.publish(17, OLD, FINAL, remote)
    assert remote.events == [("edited", "main"), ("synchronize", "main")]


def test_main_base_needs_one_synchronize_and_no_edit():
    remote = Remote(base="main")
    sp.publish(17, OLD, FINAL, remote)
    assert remote.events == [("synchronize", "main")]


def test_moved_head_or_non_fast_forward_never_publishes():
    remote = Remote(head="c" * 40)
    with pytest.raises(sp.PublishError, match="head changed"):
        sp.publish(17, OLD, FINAL, remote)
    assert not remote.events

    class Diverged(Remote):
        def __call__(self, *args):
            if args[:2] == ("git", "merge-base"):
                raise sp.PublishError("not a fast forward")
            return super().__call__(*args)

    remote = Diverged()
    with pytest.raises(sp.PublishError, match="fast forward"):
        sp.publish(17, OLD, FINAL, remote)
    assert not remote.events


def test_retarget_failure_does_not_push():
    class Denied(Remote):
        def __call__(self, *args):
            if args[:3] == ("gh", "pr", "edit"):
                raise sp.PublishError("permission denied")
            return super().__call__(*args)

    remote = Denied()
    with pytest.raises(sp.PublishError, match="permission denied"):
        sp.publish(17, OLD, FINAL, remote)
    assert not remote.events


def test_wrong_origin_or_moved_base_never_pushes():
    class WrongOrigin(Remote):
        def __call__(self, *args):
            if args[:3] == ("git", "remote", "get-url"):
                return "https://github.com/elsewhere/repo.git\n"
            return super().__call__(*args)

    remote = WrongOrigin()
    with pytest.raises(sp.PublishError, match="repository do not match"):
        sp.publish(17, OLD, FINAL, remote)
    assert not remote.events

    class MovedBase(Remote):
        def __call__(self, *args):
            result = super().__call__(*args)
            if args[:3] == ("gh", "pr", "edit"):
                self.pr["baseRefOid"] = "c" * 40
            return result

    remote = MovedBase()
    with pytest.raises(sp.PublishError, match="base or head branch changed"):
        sp.publish(17, OLD, FINAL, remote)
    assert remote.events == [("edited", "main")]
