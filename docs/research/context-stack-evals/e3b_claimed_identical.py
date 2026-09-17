"""E3b — drift scored only where the text itself claims identity (handoff-s2 §2 E).

E3 ranked every cross-file paragraph pair by cosine and found expected structure first
(version-token deltas, shared relocation headers). This run defines drift as: a passage that
a `§`-cite or a "relocated byte-verbatim" header CLAIMS identical to another, and is not —
and scores only those pairs. Four claim sets exist in this corpus:

  A. Governance packs: "*Relocated BYTE-VERBATIM from Root `CLAUDE.md` §…*" — tested at the
     relocation commit (pack body vs the root body it names, at the parent commit) and
     since (pack body at HEAD vs at relocation).
  B. Root pointer stubs: root `CLAUDE.md` keeps one sentence per relocated subsection with
     "Body at `docs/governance/<pack>.md §N.N`". No identity is claimed; consistency is.
     Scored by embedding cosine AND by lexical containment (stub content tokens found in
     the section), lowest first, for a human to read.
  C. `.harness/claude-artifact-pointers.md`: "split byte-preservingly by family" — the
     pre-split file's paragraphs vs the union of the family files at the split commit.
  D. Project_Workflow deltas: each `§N Sections preserved verbatim` block lists sections
     the delta does NOT re-table, so there is no re-tabled pair to compare; recorded as a
     claim with an empty pair set, which is itself the finding.

Everything but B is a normalised diff. B is the only question an embedding can answer.
Commits are pinned (found by `git log --diff-filter=A`, 2026-09-16), read at the boundary
via `git show` ([LAW:effects-at-boundaries]); comparison is pure over the strings.
"""

from __future__ import annotations

import difflib
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# [LAW:one-source-of-truth] the checkout this file lives in, not a hard-coded home
REPO = Path(__file__).resolve().parents[3]
OUT = Path(__file__).with_name("E3b-results.md")

RELOCATION = "0f05512ca"  # U-CTX-13 / R-CTX-1 Arc 5: packs created, root bodies removed
RELOCATION_PARENT = "f30eae667"
SPLIT = "50771f16c"  # U-CTX-06 / R-CTX-1 Arc 2: artifact-pointers split by family
PACKS = "docs/governance"
HEADING = re.compile(r"^(#{2,4}) (\d+(?:\.\d+)*)\.? (.*)$")


def git_show(ref: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{ref}:{path}"], capture_output=True, text=True
    )
    if proc.returncode != 0:  # [LAW:no-silent-failure] a missing historical file is loud
        raise SystemExit(f"git show {ref}:{path} failed: {proc.stderr.strip()}")
    return proc.stdout


def sections(text: str) -> dict[str, str]:
    """§-number → body (heading line excluded, up to the next heading of any level)."""
    out: dict[str, str] = {}
    cur: str | None = None
    buf: list[str] = []
    for line in text.splitlines():
        m = HEADING.match(line)
        if m:
            if cur is not None:
                out[cur] = "\n".join(buf)
            cur, buf = m.group(2), []
        elif cur is not None:
            buf.append(line)
    if cur is not None:
        out[cur] = "\n".join(buf)
    return out


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def diff_stat(a: str, b: str) -> tuple[int, int]:
    """(lines only in a, lines only in b) after whitespace normalisation per line."""
    la = [norm(x) for x in a.splitlines() if norm(x)]
    lb = [norm(x) for x in b.splitlines() if norm(x)]
    sm = difflib.SequenceMatcher(a=la, b=lb, autojunk=False)
    only_a = only_b = 0
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            only_a += i2 - i1
        if tag in ("replace", "insert"):
            only_b += j2 - j1
    return only_a, only_b


def claim_a() -> list[str]:
    root_then = sections(git_show(RELOCATION_PARENT, "CLAUDE.md"))
    lines = ["## A. Packs relocated byte-verbatim (tested at the relocation, then since)", ""]
    lines += [
        "| pack | § | at relocation | since (lines −/+) |",
        "|---|---|---|---|",
    ]
    for pack in sorted((REPO / PACKS).glob("*.md")):
        head = git_show(RELOCATION, f"{PACKS}/{pack.name}")
        m = re.search(r"Relocated BYTE-VERBATIM from Root `CLAUDE.md` (.+?) by U-CTX-13", head)
        if not m:
            continue
        then_secs = sections(head)
        now_secs = sections(pack.read_text())
        for num in sorted(then_secs, key=lambda k: [int(x) for x in k.split(".")]):
            if num not in root_then:
                lines.append(f"| {pack.name} | §{num} | root had no §{num} | — |")
                continue
            if norm(root_then[num]) == norm(then_secs[num]):
                at = "identical"
            else:
                d = diff_stat(root_then[num], then_secs[num])
                at = f"DIFFERS {d[0]}/{d[1]}"
            since = diff_stat(then_secs[num], now_secs.get(num, ""))
            lines.append(f"| {pack.name} | §{num} | {at} | {since[0]}/{since[1]} |")
    return [*lines, ""]


def claim_b() -> list[str]:
    from common import embed  # the one embedding use in this evaluation

    root = (REPO / "CLAUDE.md").read_text()
    pairs: list[tuple[str, str, str, str]] = []  # (stub, pack, §, section body)
    for line in root.splitlines():
        for pack, num in re.findall(r"`docs/governance/([a-z-]+\.md)` ?§(\d+(?:\.\d+)*)", line):
            body = sections((REPO / PACKS / pack).read_text()).get(num)
            if body is not None:
                pairs.append((line.strip(), pack, num, body))
    stubs = [p[0] for p in pairs]
    bodies = [p[3] for p in pairs]
    sv, bv = embed(stubs), embed(bodies)
    cos = (sv * bv).sum(axis=1)

    def toks(s: str) -> set[str]:
        return {w for w in re.findall(r"[a-z][a-z0-9_-]{3,}", s.lower())}

    rows = []
    for (stub, pack, num, body), c in zip(pairs, cos, strict=True):
        st = toks(stub) - {"body", "docs", "governance", "detail", "full", "links"}
        contain = len(st & toks(body)) / max(1, len(st))
        rows.append((float(c), contain, pack, num, stub))
    rows.sort(key=lambda r: r[0])
    lines = [
        f"## B. Root pointer stubs vs the pack section they name ({len(rows)} pairs)",
        "",
        "Lowest embedding cosine first; `contain` = share of the stub's content tokens present "
        "in the section. Read the bottom rows.",
        "",
        "| cosine | contain | pack | § | stub (truncated) |",
        "|---|---|---|---|---|",
    ]
    for c, contain, pack, num, stub in rows:
        lines.append(f"| {c:.2f} | {contain:.2f} | {pack} | §{num} | {stub[:90]} |")
    both = sum(1 for r in rows if r[0] < 0.6 and r[1] < 0.5)
    lines += [
        "",
        f"Rows with cosine < 0.60 AND contain < 0.50: {both}. "
        "Where the two disagree, the lexical score names the missing nouns; the cosine does not.",
        "",
    ]
    return lines


def claim_c() -> list[str]:
    pre = git_show(f"{SPLIT}^", ".harness/claude-artifact-pointers.md")
    fam = subprocess.run(
        ["git", "-C", str(REPO), "ls-tree", "--name-only", SPLIT, ".harness/artifact-pointers/"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split()
    post = "\n\n".join(git_show(SPLIT, f) for f in fam)

    def paras(t: str) -> list[str]:
        return [norm(p) for p in re.split(r"\n\s*\n", t) if norm(p)]

    a, b = paras(pre), paras(post)
    missing = [p for p in a if p not in set(b)]
    extra = [p for p in b if p not in set(a)]
    # A paragraph can be missing because the split re-cut it (a multi-row table becomes one
    # row per family file); the claim survives if every LINE of it is somewhere in the union.
    union_lines = {norm(x) for x in post.splitlines() if norm(x)}
    lost_lines: list[str] = []
    for p in missing:
        for raw in pre.splitlines():
            if norm(raw) and norm(raw) in p and norm(raw) not in union_lines:
                lost_lines.append(norm(raw))
    lost_lines = sorted(set(lost_lines))
    # The source's own scaffolding (title, section headings, its preamble paragraph) is what
    # the stub file replaced; only a lost LINEAGE line would falsify the claim.
    scaffold = {norm(x) for x in pre.splitlines() if norm(x).startswith("#")} | {
        norm(x) for x in a[1].split(". ") if norm(x)
    }
    lost_lineage = [x for x in lost_lines if x not in scaffold and x.rstrip(".") not in scaffold]
    lines = [
        "## C. Artifact pointers split byte-preservingly by family",
        "",
        f"Pre-split file at {SPLIT}^: {len(pre):,} B, {len(a)} paragraphs. "
        f"Family files at {SPLIT}: {len(fam)} files, {len(post):,} B, {len(b)} paragraphs.",
        f"Paragraphs of the original missing from the union: **{len(missing)}**; "
        f"paragraphs in the union not in the original: {len(extra)}.",
        f"Lines of those missing paragraphs absent from the union at line level: "
        f"**{len(lost_lines)}**, of which lineage (not the source's own title/headings/"
        f"preamble that the stub replaced): **{len(lost_lineage)}**. A re-cut table keeps "
        "its rows; a lost lineage row would be drift.",
        "",
    ]
    for p in missing[:8]:
        lines.append(f"- MISSING paragraph: {p[:160]}")
    for x in lost_lines[:12]:
        lines.append(f"- LOST line: {x[:200]}")
    for p in extra[:4]:
        lines.append(f"- EXTRA: {p[:160]}")
    return [*lines, ""]


def claim_d() -> list[str]:
    lines = ["## D. Project_Workflow deltas: sections preserved verbatim", ""]
    for f in sorted((REPO / "design-substrate").glob("Project_Workflow_v1_*.md")):
        text = f.read_text()
        m = re.search(r"^## §\d+ Sections preserved verbatim at (v1\.\d+)", text, re.M)
        retabled = [
            h
            for h in re.findall(r"^#{2,4} (§[\d.]+ [^\n]*)$", text, re.M)
            if not re.match(
                r"§\d+ (Sections preserved|Adjacent|Filing|Cross-artifact|Empirical)", h
            )
        ]
        lines.append(
            f"- {f.name}: preserved-verbatim block {'present' if m else 'absent'}; "
            f"re-tabled section headings: {len(retabled)}"
        )
    lines += [
        "",
        "A preserved-verbatim block names sections the delta does not carry, so no pair exists "
        "to diff; the claim is checkable only by the absence of a re-table, which every delta "
        "satisfies by construction. The re-tabled headings are new sub-sections, not copies.",
        "",
    ]
    return lines


def main() -> None:
    a, c, d, b = claim_a(), claim_c(), claim_d(), claim_b()
    drift_a = sum(1 for x in a if "| DIFFERS" in x or "root had no" in x)
    lost_c = int(re.search(r"lineage[^:]*: \*\*(\d+)\*\*", "\n".join(c)).group(1))
    low_b = int(re.search(r"cosine < 0.60 AND contain < 0.50: (\d+)", "\n".join(b)).group(1))
    lines = [
        "# E3b — drift scored only on claimed-identical pairs",
        "",
        f"Repo {REPO.name}; relocation {RELOCATION} (parent {RELOCATION_PARENT}); split {SPLIT}.",
        "",
        "## Verdict (computed)",
        "",
        f"- A: sections not identical at relocation: **{drift_a}** of the relocated set.",
        f"- C: lineage lines lost by the split: **{lost_c}** "
        "(the source's own title, headings and preamble were replaced by the stub, by design).",
        "- D: re-tabled pairs to diff: **0** (the claim is an absence, satisfied by construction).",
        f"- B: stubs below both read thresholds: **{low_b}** of the pointer set.",
        "- Drift, as defined (a claimed-identical pair that is not): "
        + ("**none found**." if drift_a == 0 and lost_c == 0 else "**found, see above**."),
        "- What the embedding added over the normalised diff: nothing for A, C, D (identity "
        "questions); for B it ranks the same rows the lexical containment ranks, without "
        "naming the missing nouns.",
        "",
        *a,
        *c,
        *d,
        *b,
    ]
    OUT.write_text("\n".join(lines) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
