#!/usr/bin/python3
"""Read-only procfs observer: does a process of one user retain a reference inside a tree?

Prints the first referencing PID and exits 0, exits 10 when the observation completed
and found none, and exits 20 when any process of that user could not be fully observed.
It never writes, signals or removes anything, so an operator may run it - and only it -
with read privilege when the host hides same-user processes (lib.sh launcher seam).
"""

import argparse
import os
import sys
from pathlib import Path

FOUND, NONE, UNKNOWN = 0, 10, 20


def inside(target: str, candidate: str) -> bool:
    if candidate.endswith(" (deleted)"):
        candidate = candidate[: -len(" (deleted)")]
    if not os.path.isabs(candidate):
        return False
    candidate = os.path.normpath(candidate)
    try:
        return os.path.commonpath((target, candidate)) == target
    except ValueError:
        return False


def observe(proc_root: Path, uid: int, target: str) -> tuple[int, str]:
    unknown = False
    for process in proc_root.iterdir():
        if not process.name.isdigit():
            continue
        try:
            if process.stat().st_uid != uid:
                continue
        except FileNotFoundError:
            continue
        except OSError:
            unknown = True
            continue
        links = [process / "cwd", process / "root"]
        try:
            links.extend((process / "fd").iterdir())
        except FileNotFoundError:
            continue
        except OSError:
            unknown = True
        for link in links:
            try:
                candidate = os.readlink(link)
            except FileNotFoundError:
                continue
            except OSError:
                unknown = True
                continue
            if inside(target, candidate):
                return FOUND, process.name
        try:
            maps = (process / "maps").read_text(encoding="utf-8", errors="replace").splitlines()
        except FileNotFoundError:
            continue
        except OSError:
            unknown = True
            continue
        for mapping in maps:
            fields = mapping.split(maxsplit=5)
            if len(fields) == 6 and inside(target, fields[5]):
                return FOUND, process.name
    return (UNKNOWN if unknown else NONE), ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    # [LAW:one-source-of-truth] the caller names the user; under a privileged launcher
    # geteuid() is the launcher's identity, not the remover's.
    parser.add_argument("--uid", type=int, required=True)
    parser.add_argument("--proc-root", type=Path, default=Path("/proc"))
    parser.add_argument("target")
    args = parser.parse_args()
    status, pid = observe(args.proc_root, args.uid, os.path.realpath(args.target))
    if pid:
        print(pid)
    return status


if __name__ == "__main__":
    sys.exit(main())
