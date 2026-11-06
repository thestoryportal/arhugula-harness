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
            assert args[2:] == (
                f"--force-with-lease=refs/heads/feature:{OLD}",
                "origin",
                f"{FINAL}:refs/heads/feature",
            )
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


@pytest.mark.parametrize(
    "push_urls",
    [
        "https://github.com/other/repo.git\n",
        "https://github.com/owner/repo.git\nhttps://github.com/other/repo.git\n",
    ],
)
def test_different_or_multiple_push_destinations_refuse_before_retarget(push_urls):
    class WrongPush(Remote):
        def __call__(self, *args):
            if args[:5] == ("git", "remote", "get-url", "--push", "--all"):
                return push_urls
            return super().__call__(*args)

    remote = WrongPush()
    with pytest.raises(sp.PublishError, match="push destinations"):
        sp.publish(17, OLD, FINAL, remote)
    assert not remote.events


def test_real_git_lease_rejects_intermediate_advance(tmp_path):
    import subprocess

    def git(*args, cwd=tmp_path, check=True):
        return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=check)

    bare = tmp_path / "remote.git"
    git("init", "--bare", str(bare))
    work = tmp_path / "work"
    git("init", str(work))
    git("config", "user.name", "Test", cwd=work)
    git("config", "user.email", "test@example.invalid", cwd=work)
    git("remote", "add", "origin", str(bare), cwd=work)
    commits = []
    for value in ("old", "intermediate", "final"):
        (work / "file").write_text(value)
        git("add", "file", cwd=work)
        git("commit", "-m", value, cwd=work)
        commits.append(git("rev-parse", "HEAD", cwd=work).stdout.strip())
    old, intermediate, final = commits
    ref = "refs/heads/feature"
    git("push", "origin", f"{old}:{ref}", cwd=work)
    git("merge-base", "--is-ancestor", old, final, cwd=work)
    git("push", "origin", f"{intermediate}:{ref}", cwd=work)
    stale = git(
        "push", f"--force-with-lease={ref}:{old}", "origin", f"{final}:{ref}", cwd=work, check=False
    )
    assert stale.returncode != 0
    assert git("--git-dir", str(bare), "rev-parse", ref).stdout.strip() == intermediate


def test_real_git_effective_push_urls_include_rewrites_and_multipush(tmp_path):
    import subprocess

    def git(*args):
        return (
            subprocess.run(["git", *args], cwd=tmp_path, text=True, capture_output=True, check=True)
            .stdout.strip()
            .splitlines()
        )

    git("init")
    git("remote", "add", "origin", "https://github.com/owner/repo.git")
    git("config", "url.ssh://git@github.com/.pushInsteadOf", "https://github.com/")
    assert git("remote", "get-url", "origin") == ["https://github.com/owner/repo.git"]
    assert git("remote", "get-url", "--push", "--all", "origin") == [
        "ssh://git@github.com/owner/repo.git"
    ]
    git("config", "--add", "remote.origin.pushurl", "https://github.com/owner/repo.git")
    git("config", "--add", "remote.origin.pushurl", "https://github.com/other/repo.git")
    assert git("remote", "get-url", "--push", "--all", "origin") == [
        "https://github.com/owner/repo.git",
        "https://github.com/other/repo.git",
    ]
