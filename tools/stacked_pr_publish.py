#!/usr/bin/env python3
"""Retarget a stacked PR before publishing its final fast-forward head."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable


class PublishError(ValueError):
    pass


def run(*args: str) -> str:
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    if result.returncode:
        raise PublishError(
            f"{args[0]} failed ({result.returncode}): {result.stderr or result.stdout}"
        )
    return result.stdout


def publish(pr: int, old_head: str, final_head: str, call: Callable[..., str] = run) -> None:
    if pr <= 0 or any(not re.fullmatch(r"[0-9a-f]{40}", sha) for sha in (old_head, final_head)):
        raise PublishError("PR and full old/final commit IDs are required")
    if old_head == final_head:
        raise PublishError("final head must differ to trigger PR synchronize")

    def view() -> dict:
        data = json.loads(
            call(
                "gh",
                "pr",
                "view",
                str(pr),
                "--json",
                "state,baseRefName,baseRefOid,headRefName,headRefOid,isCrossRepository,url",
            )
        )
        if (
            data["state"] != "OPEN"
            or data["isCrossRepository"] is not False
            or data["headRefOid"] != old_head
            or not data["headRefName"]
        ):
            raise PublishError("PR state, repository or old head changed")
        return data

    initial = view()
    pr_url = re.fullmatch(r"https://github\.com/([^/]+/[^/]+)/pull/[0-9]+", initial["url"])
    remote_url = call("git", "remote", "get-url", "origin").strip()
    remote = re.fullmatch(
        r"(?:https://github\.com/|git@github\.com:|ssh://git@github\.com/)([^/]+/[^/]+?)(?:\.git)?",
        remote_url,
    )
    if pr_url is None or remote is None or pr_url[1].lower() != remote[1].lower():
        raise PublishError("origin and PR repository do not match")
    final = call("git", "rev-parse", "--verify", f"{final_head}^{{commit}}").strip()
    if final != final_head:
        raise PublishError("final commit does not resolve exactly")
    call("git", "merge-base", "--is-ancestor", old_head, final_head)
    refs = call("git", "ls-remote", "origin", "refs/heads/main").splitlines()
    if len(refs) != 1:
        raise PublishError("origin main did not resolve uniquely")
    parts = refs[0].split()
    if (
        len(parts) != 2
        or parts[1] != "refs/heads/main"
        or not re.fullmatch(r"[0-9a-f]{40}", parts[0])
    ):
        raise PublishError("origin main returned an invalid ref")
    main_head = parts[0]
    call("git", "merge-base", "--is-ancestor", main_head, final_head)
    if initial["baseRefName"] != "main":
        call("gh", "pr", "edit", str(pr), "--base", "main")
    current = view()
    if (
        current["baseRefName"] != "main"
        or current["baseRefOid"] != main_head
        or current["headRefName"] != initial["headRefName"]
    ):
        raise PublishError("PR base or head branch changed during retarget")
    remote_head = call("git", "ls-remote", "origin", f"refs/heads/{current['headRefName']}")
    if remote_head.split() != [old_head, f"refs/heads/{current['headRefName']}"]:
        raise PublishError("origin branch changed during retarget")
    # [LAW:no-ambient-temporal-coupling] Retarget must finish before synchronize;
    # The final synchronize event must describe the intended base and final head.
    call("git", "push", "origin", f"{final_head}:refs/heads/{current['headRefName']}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pr", type=int)
    parser.add_argument("--old-head", required=True)
    parser.add_argument("--final-head", required=True)
    args = parser.parse_args(argv)
    try:
        publish(args.pr, args.old_head, args.final_head)
    except (PublishError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"stacked-pr-publish: {exc}", file=sys.stderr)
        return 3
    print(f"stacked-pr-publish: published {args.final_head} to PR #{args.pr} on main")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
