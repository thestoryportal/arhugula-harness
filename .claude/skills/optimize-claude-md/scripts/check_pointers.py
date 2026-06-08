#!/usr/bin/env python3
"""check_pointers.py — does this CLAUDE.md still resolve after optimization?

WHY THIS EXISTS
    The one way an "optimization" silently breaks things is a DANGLING POINTER: you relocate
    a section and a `§4.4` cross-ref now points nowhere; you compress a pointer table and a
    `design-substrate/...` path no longer resolves; you touch a `[[memory-link]]` and it names
    a memory that doesn't exist. A dangling pointer is worse than no optimization. This script
    is the mechanical half of the "verify byte-exact resolution" gate the skill must pass
    before proposing a diff.

WHAT IT CHECKS
    1. File-path pointers (backtick-wrapped or known-prefix) resolve to a real file/dir.
    2. `[[memory-link]]` names resolve to a memory file (if the memory dir can be located).
    3. `§N` / `§N.N` cross-references — see --baseline for the precise, low-false-positive check.

THE --baseline MODE (the important one for an optimization pass)
    Many `§` refs in these files point to OTHER docs ("CXA §2.3.3", "Meta-Architecture §6"), so
    flagging every § target absent from this file would cry wolf. Instead, pass the pre-edit
    file as --baseline: the script flags only `§` targets that EXISTED as a section before and
    are MISSING after — i.e. references your edit just broke by relocating/renumbering. Same for
    paths/links that resolved before and don't now. This is exactly the "grade the diff" check.

USAGE
    python check_pointers.py CLAUDE.md --root /path/repo                 # single-file report
    python check_pointers.py NEW.md --baseline OLD.md --root /path/repo  # what the edit broke
    python check_pointers.py NEW.md --baseline OLD.md --root R --check   # exit 1 if edit broke any
    python check_pointers.py CLAUDE.md --root R --json                   # machine-readable
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess

KNOWN_PREFIXES = (
    "design-substrate/",
    ".harness/",
    "tools/",
    "research/",
    "harness-",
    "ai-docs/",
    ".claude/",
    "scripts/",
    "references/",
)
PATH_EXTS = (".md", ".py", ".toml", ".sh", ".yaml", ".yml", ".json", ".txt", ".html", ".cfg")

RE_BACKTICK = re.compile(r"`([^`]+)`")
RE_LINK = re.compile(r"\[\[([^\]]+)\]\]")
RE_SECREF = re.compile(r"§\s?(\d+(?:\.\d+)*)")
RE_HEADER = re.compile(r"^#{1,6}\s+(\d+(?:\.\d+)*)\b")


def read(path: str) -> str:
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8", errors="replace")


def looks_like_path(tok: str) -> bool:
    tok = tok.strip()
    if " " in tok and not tok.endswith(PATH_EXTS):
        return False
    if "/" not in tok and not tok.endswith(PATH_EXTS):
        return False
    return tok.endswith(PATH_EXTS) or tok.startswith(KNOWN_PREFIXES) or ("/" in tok)


def norm_path(tok: str) -> str:
    """Strip markdown/glob noise to a filesystem-checkable path."""
    # Strip surrounding markdown/sentence punctuation, but NEVER a leading dot:
    # `.harness/`, `.claude/`, `.github/` are real dotpaths, not punctuation. Stripping the
    # leading `.` (the old `.strip(".,;:)( ")`) made every `.harness/<file>` token unresolvable.
    tok = tok.strip().strip(",;:)( ")
    tok = tok.rstrip(".")  # trailing sentence period only; leading dot preserved
    tok = re.split(r"[#:]", tok, maxsplit=1)[0]  # drop #anchor / :line
    tok = tok.replace("/**", "").replace("/*", "")
    if tok.startswith("./"):
        tok = tok[2:]
    return tok.rstrip("/")


def extract_paths(text: str) -> list[tuple[int, str]]:
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in RE_BACKTICK.finditer(line):
            tok = m.group(1)
            if looks_like_path(tok):
                out.append((i, tok))
        # bare known-prefix paths outside backticks (best-effort)
        for m in re.finditer(
            r"(?<![`\w])((?:design-substrate|\.harness|tools|harness-[a-z]+)/[^\s`)\]]+)", line
        ):
            out.append((i, m.group(1)))
    return out


def extract_links(text: str) -> list[tuple[int, str]]:
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in RE_LINK.finditer(line):
            out.append((i, m.group(1).strip()))
    return out


def extract_secrefs(text: str) -> list[tuple[int, str]]:
    out = []
    for i, line in enumerate(text.split("\n"), 1):
        for m in RE_SECREF.finditer(line):
            out.append((i, m.group(1)))
    return out


def section_numbers(text: str) -> set[str]:
    nums = set()
    for line in text.split("\n"):
        m = RE_HEADER.match(line)
        if m:
            nums.add(m.group(1))
    return nums


def derive_memory_dir(root: str) -> str | None:
    enc = re.sub(r"[^A-Za-z0-9]", "-", os.path.abspath(root))
    cand = os.path.expanduser(f"~/.claude/projects/{enc}/memory")
    return cand if os.path.isdir(cand) else None


def build_index(root: str) -> tuple[set[str], set[str]]:
    """(relpaths, basenames) of tracked files — for resolving bare filenames in subdirs.

    A bare filename matching no tracked basename is a real stale reference, not a subdir miss.
    """
    rel: set[str] = set()
    base: set[str] = set()
    try:
        out = subprocess.run(
            ["git", "-C", root, "ls-files"], capture_output=True, text=True, check=True
        ).stdout
        for path in out.splitlines():
            rel.add(path)
            base.add(os.path.basename(path))
    except Exception:
        for dp, _, files in os.walk(root):
            for f in files:
                rel.add(os.path.relpath(os.path.join(dp, f), root))
                base.add(f)
    return rel, base


def resolve_path(tok: str, root: str, index: tuple[set[str], set[str]]) -> bool:
    p = norm_path(tok)
    if not p:
        return True
    if p.startswith("~"):
        return os.path.exists(os.path.expanduser(p))
    if os.path.exists(os.path.join(root, p)):
        return True
    rel, base = index
    # dir-qualified paths must match exactly; a bare filename resolves if any tracked file
    # shares its basename (it lives in a subdir we didn't join) — else it's genuinely stale.
    return (p in rel) if "/" in p else (os.path.basename(p) in base)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check that a CLAUDE.md's pointers resolve.")
    ap.add_argument("file", help="the CLAUDE.md to check (post-edit, in --baseline mode)")
    ap.add_argument("--root", default=".", help="repo root for resolving file paths")
    ap.add_argument(
        "--baseline", default=None, help="pre-edit file; report only what the edit broke"
    )
    ap.add_argument("--memory-dir", default=None, help="memory dir for [[link]] resolution")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--check", action="store_true", help="exit 1 if anything is unresolved/broken")
    args = ap.parse_args(argv)

    text = read(args.file)
    mem = args.memory_dir or derive_memory_dir(args.root)
    index = build_index(args.root)

    # --- resolve current file ---
    bad_paths = [(ln, t) for ln, t in extract_paths(text) if not resolve_path(t, args.root, index)]
    bad_links = []
    if mem:
        for ln, name in extract_links(text):
            if not os.path.isfile(os.path.join(mem, f"{name}.md")):
                bad_links.append((ln, name))
    secs_now = section_numbers(text)

    result = {
        "file": args.file,
        "memory_dir": mem,
        "unresolved_paths": [{"line": ln, "ref": t} for ln, t in bad_paths],
        "unresolved_links": [{"line": ln, "ref": t} for ln, t in bad_links],
    }

    if args.baseline:
        old = read(args.baseline)
        secs_old = section_numbers(old)
        # an intra-file §ref is one whose target was a real section before the edit
        broke_secrefs = sorted(
            {(ln, r) for ln, r in extract_secrefs(text) if r in secs_old and r not in secs_now}
        )
        # paths/links that resolved in baseline but not now (pre-existing breakage is not the
        # edit's fault — only flag what THIS edit broke, so a pure relocation grades clean)
        old_bad_paths = {t for _, t in extract_paths(old) if not resolve_path(t, args.root, index)}
        newly_bad_paths = [(ln, t) for ln, t in bad_paths if t not in old_bad_paths]
        old_bad_links = set()
        if mem:
            old_bad_links = {
                n for _, n in extract_links(old) if not os.path.isfile(os.path.join(mem, f"{n}.md"))
            }
        newly_bad_links = [(ln, n) for ln, n in bad_links if n not in old_bad_links]
        result["newly_broken_section_refs"] = [
            {"line": ln, "ref": f"§{r}"} for ln, r in broke_secrefs
        ]
        result["newly_broken_paths"] = [{"line": ln, "ref": t} for ln, t in newly_bad_paths]
        result["newly_broken_links"] = [{"line": ln, "ref": n} for ln, n in newly_bad_links]
        failing = bool(broke_secrefs or newly_bad_paths or newly_bad_links)
    else:
        # single-file: which §targets are absent here (informational — may be cross-doc refs)
        absent = sorted({r for _, r in extract_secrefs(text) if r not in secs_now})
        result["section_refs_absent_in_file"] = absent
        failing = bool(bad_paths or bad_links)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"check_pointers: {args.file}")
        if args.baseline:
            nb = (
                result["newly_broken_section_refs"]
                + result["newly_broken_paths"]
                + result["newly_broken_links"]
            )
            if not nb:
                print("  OK — the edit broke no previously-resolving pointer.")
            for x in result["newly_broken_section_refs"]:
                print(
                    f"  BROKEN §ref  L{x['line']:<5} {x['ref']} (section existed before, gone now)"
                )
            for x in result["newly_broken_paths"]:
                print(f"  BROKEN path  L{x['line']:<5} {x['ref']}")
            for x in result["newly_broken_links"]:
                print(f"  BROKEN link  L{x['line']:<5} [[{x['ref']}]]")
        else:
            if not bad_paths and not bad_links:
                print(f"  paths ok, links ok ({len(secs_now)} sections).")
            for ln, t in bad_paths:
                print(f"  unresolved path  L{ln:<5} {t}")
            for ln, t in bad_links:
                print(f"  unresolved link  L{ln:<5} [[{t}]]")
            if result["section_refs_absent_in_file"]:
                print(
                    f"  note: {len(result['section_refs_absent_in_file'])} §ref target(s) "
                    f"not sections in THIS file (likely cross-doc; use --baseline to judge edits)"
                )

    return 1 if (args.check and failing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
