#!/usr/bin/env python3
"""Run an OAuth-authenticated Antigravity CLI diff review and fail closed."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

LOG_PATH = "/tmp/arhugula-agy-review.log"
PROVIDER_ENV = (
    "GEMINI_API_KEY",
    "GOOGLE_API_KEY",
    "GOOGLE_GENAI_USE_VERTEXAI",
    "GOOGLE_APPLICATION_CREDENTIALS",
    "GOOGLE_CLOUD_PROJECT",
    "GOOGLE_CLOUD_LOCATION",
)
VERDICTS = {"VERDICT: APPROVE", "VERDICT: BLOCK"}


def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        errors="replace",
        check=False,
    )


def collect_diff(repo: Path, base: str) -> str:
    tracked = run_git(repo, "diff", "--merge-base", "--binary", base)
    if tracked.returncode != 0:
        raise RuntimeError(tracked.stderr.strip() or "git diff failed")

    untracked = run_git(repo, "ls-files", "--others", "--exclude-standard", "-z")
    if untracked.returncode != 0:
        raise RuntimeError(untracked.stderr.strip() or "git ls-files failed")

    parts = [tracked.stdout]
    for relative_path in filter(None, untracked.stdout.split("\0")):
        patch = run_git(
            repo,
            "diff",
            "--no-index",
            "--binary",
            "--",
            "/dev/null",
            relative_path,
        )
        if patch.returncode not in {0, 1}:
            raise RuntimeError(
                patch.stderr.strip() or f"could not diff untracked file: {relative_path}"
            )
        parts.append(patch.stdout)

    diff = "".join(parts).strip()
    if not diff:
        raise RuntimeError("review diff is empty")
    return diff


def review_prompt(repo: Path, diff: str) -> str:
    return (
        f"""You are an out-of-family code reviewer for an agent-harness monorepo.
The authoritative workspace root is {repo}. Read surrounding source only from that
workspace; do not use a common checkout, sibling worktree, or other repository copy.
Review the complete concrete diff below for real defects: correctness, hook and
permission semantics, contract drift, unsafe state handling, and tests that
would stay green if the change were reverted. Number findings F1..Fn tagged
[P1]/[P2]/[P3] with file:line; no style nits. Do not edit files.
Do not invoke terminal commands or request command permission: the complete diff is supplied
below, and workspace read-only file tools are available if surrounding context
is essential. Do not invoke URL, browser, or MCP tools. Do not read dotfiles,
environment files, or user configuration. End with exactly VERDICT: APPROVE or
VERDICT: BLOCK as the final non-empty line.

<diff>
"""
        + diff
        + "\n</diff>"
    )


def run_review(repo: Path, base: str) -> int:
    try:
        diff = collect_diff(repo, base)
    except RuntimeError as exc:
        print(f"agy-review: {exc}", file=sys.stderr)
        return 2

    env = os.environ.copy()
    for name in PROVIDER_ENV:
        env.pop(name, None)
    try:
        proc = subprocess.run(
            [
                "agy",
                "--sandbox",
                "--dangerously-skip-permissions",
                "--mode",
                "plan",
                "--model",
                "gemini-3.6-flash-high",
                "--log-file",
                LOG_PATH,
                "--print-timeout",
                "10m",
                "-p",
                review_prompt(repo, diff),
            ],
            cwd=repo,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=660,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"agy-review: reviewer unavailable: {exc}", file=sys.stderr)
        return 2

    output = proc.stdout.strip()
    if proc.returncode != 0:
        if output:
            print(output)
        detail = proc.stderr.strip() or f"exit {proc.returncode}"
        print(f"agy-review: reviewer failed: {detail}", file=sys.stderr)
        return proc.returncode

    final_line = next((line.strip() for line in reversed(output.splitlines()) if line.strip()), "")
    if final_line not in VERDICTS:
        if output:
            print(output, file=sys.stderr)
        print("agy-review: missing exact final verdict", file=sys.stderr)
        return 2

    print(output)
    if final_line == "VERDICT: BLOCK":
        print("agy-review: blocking findings require resolution", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="main")
    args = parser.parse_args()
    return run_review(Path.cwd(), args.base)


if __name__ == "__main__":
    raise SystemExit(main())
