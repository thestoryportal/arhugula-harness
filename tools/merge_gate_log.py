#!/usr/bin/env python3
"""C-HE-23 §2: the merge-gate log's structured sibling. JSONL first, markdown second.

The sibling is a machine projection of the same fact written by the same producer in the
same step -- not a second authority. A failed markdown write leaves the JSONL row and logs a
`warn` finding; a failed JSONL write fails the gate step (a verdict that cannot be recorded
does not count, C-HE-15 §1 -- BLOCK-equivalent for the calling skill).

The lens verdict is the `merge-gate.schema.json` shape (C-HE-15 §4): `verdict`, `findings`
and the six binding values the orchestrator computed (`binding`) and the lens copied
verbatim. Parsing and binding byte-compare go through `review_wrapper_common.parse_verdict`,
row minting through `review_wrapper_common.emit_outcome` (ids and `round_n` minted under
the log lock -- never a per-invocation ordinal, U-HE-01 interface note).

CLI (what `.claude/skills/merge-gate/SKILL.md` calls):
    merge_gate_log.py binding --lens <id> [--base main]        -> the six fields, JSON
    merge_gate_log.py emit --pr N --lens <id> --verdict-json F  -> record; exit 0/1/2
    merge_gate_log.py check                                      -> consistency reducer
    merge_gate_log.py reconcile                                  -> re-emit orphan md rows
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import finding_record as fr
import review_wrapper_common as rw

REPO = Path(__file__).resolve().parent.parent
GATE_LOG_MD = REPO / ".harness" / "merge-gate-log.md"
#: Every carrier of the lens configuration, on BOTH runners: the Claude skill, its Codex
#: projection, and the Codex lens prompts. `config_hash` fingerprints all of them (sorted,
#: existing ones), so a gate run on either runner binds to the same configuration identity and
#: a change to any carrier changes the hash (gemini R1 P2: one carrier alone ignored the other).
CONFIG_CARRIERS = (
    REPO / ".claude" / "skills" / "merge-gate" / "SKILL.md",
    REPO / ".agents" / "skills" / "merge-gate" / "SKILL.md",
)
CONFIG_CARRIER_GLOB = (REPO / ".codex" / "notes" / "merge-gate-lenses", "*.md")
CHANNEL = "merge-gate"
PROMPT_VERSION = "merge-gate-lens-v1"
_LENS_RE = re.compile(r"^merge-gate-[a-z-]+$")
#: The structured markdown line this module writes (the reducer reads ONLY this shape):
#: `| <ts> | #<pr> | <head12> | <lens> | <APPROVE|BLOCK|REVIEWER_UNAVAILABLE> | <n> finding(s) |`.
#: The legacy per-PR narrative rows (`| #NNNN | <date> | <branch> | ... |`) do not match it.
_MD_ROW = re.compile(
    r"^\|\s*(?P<ts>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\s*\|\s*#(?P<pr>\d+)\s*\|\s*"
    r"(?P<head>[0-9a-f]{12})\s*\|\s*(?P<lens>merge-gate-[a-z-]+)\s*\|\s*"
    r"(?P<verdict>APPROVE|BLOCK)\s*\|"
)
_ARC_PR_RE = re.compile(r"^pr-(\d+)$")


class GateLogError(RuntimeError):
    """The gate step must fail: the machine record could not be written."""


def config_carriers() -> list[Path]:
    d, pat = CONFIG_CARRIER_GLOB
    found = [p for p in CONFIG_CARRIERS if p.exists()]
    if d.is_dir():
        found.extend(sorted(d.glob(pat)))
    return found


def config_hash() -> str:
    """The lens configuration IS the carrier text (all runners): one digest over every
    existing carrier, each prefixed by its REPO-relative path so a rename is a change too."""
    carriers = config_carriers()
    if not carriers:
        return "noskill"
    h = hashlib.sha256()
    for p in carriers:
        h.update(str(p.relative_to(REPO)).encode() + b"\0" + p.read_bytes() + b"\0")
    return h.hexdigest()[:16]


def lens_binding(
    repo: Path,
    base: str,
    lens: str,
    *,
    prompt_version: str = PROMPT_VERSION,
    cfg_hash: str | None = None,
) -> dict[str, str]:
    """The orchestrator's OWN six binding values for one lens (C-HE-15 §4), never read from
    the lens. `reviewer_identity` is the lens id (schema: `^merge-gate-[a-z-]+$`)."""
    if not _LENS_RE.match(lens):
        raise GateLogError(f"lens id {lens!r} must match ^merge-gate-[a-z-]+$")
    b = rw.compute_binding(
        repo,
        base,
        channel=CHANNEL,
        prompt_version=prompt_version,
        config_hash=cfg_hash if cfg_hash is not None else config_hash(),
    )
    b["reviewer_identity"] = lens
    return b


def verdict_of(row: dict) -> str | None:
    """APPROVE / BLOCK from a gate row's `finding_type` (the wrapper encoding), else None."""
    ft = row.get("finding_type", "")
    if ft == "clean-approve":
        return "APPROVE"
    if ft == "terminal-block":
        return "BLOCK"
    return None


def _md_line(ts: str, pr: int, head_sha: str, lens: str, terminal: str, n_findings: int) -> str:
    return f"| {ts} | #{pr} | {head_sha[:12]} | {lens} | {terminal} | {n_findings} finding(s) |\n"


def emit_gate_row(
    *,
    pr: int,
    lens: str,
    outcome: rw.ReviewOutcome,
    arc_id: str | None = None,
    lane_id: str | None = None,
    round_n: int | None = None,
    md_path: Path | None = None,
    jsonl_path: Path | None = None,
) -> list[dict]:
    """Record one lens outcome: (1) the JSONL observations FIRST (`rw.emit_outcome`, one
    critical section: `round_n` + every `finding_id` minted under the log lock), then (2) one
    structured markdown line. Returns the JSONL rows as written. Both paths resolve AT CALL
    TIME (never bound at def time) so a test's monkeypatch is honoured and a fixture run can
    never reach the tracked logs."""
    if not _LENS_RE.match(lens):
        raise GateLogError(f"lens id {lens!r} must match ^merge-gate-[a-z-]+$")
    arc_id = arc_id or f"pr-{pr}"
    lane_id = lane_id or rw.env_arc_and_lane()[1]
    md_path = md_path or GATE_LOG_MD
    jsonl_path = jsonl_path or fr.GATE_LOG_JSONL
    try:
        rows = rw.emit_outcome(
            outcome, producer=lens, arc_id=arc_id, lane_id=lane_id, round_n=round_n, path=jsonl_path
        )
    except (OSError, fr.RecordError) as exc:  # (1) machine record FIRST; unrecordable = no verdict
        raise GateLogError(f"gate verdict could not be recorded: {exc}") from exc
    head = rows[0]["head_sha"] or "nohead"
    try:
        with md_path.open("a", encoding="utf-8") as fh:  # (2) human view second
            fh.write(
                _md_line(rows[0]["ts"], pr, head, lens, outcome.terminal, len(outcome.findings))
            )
    except OSError as exc:
        # The machine record stands; the failure is itself a recorded `warn` finding so the
        # consistency reducer can tell "md write failed" from "crashed between the writes".
        # Emitted under the SAME producer (the lens) so the reducer keys it per lens: one
        # lens's md failure must not suppress another lens's orphan at the same head (gemini
        # R1 P2). `lineage_claim=wrapper` marks it as this module's, not the lens's, finding.
        try:
            fr.append_observation(
                dict(
                    location=str(md_path),
                    observed_evidence=f"markdown write failed: {exc}",
                    expected_contract="C-HE-23 §2 markdown sibling",
                    severity="warn",
                    finding_type="transient-retry",
                    lineage_claim="wrapper",
                    producer=lens,
                ),
                fr.Envelope(
                    record_kind="finding",
                    ts=fr.now_iso(),
                    arc_id=arc_id,
                    lane_id=lane_id,
                    head_sha=rows[0]["head_sha"],
                    base_sha=rows[0]["base_sha"],
                    diff_digest=rows[0]["diff_digest"],
                    round_n=rows[0]["round_n"],
                    cause_attribution="markdown_write_failed",
                ),
                jsonl_path,
            )
        except (OSError, fr.RecordError) as warn_exc:
            # The verdict rows ARE recorded; without the warn the reducer will class them as
            # orphans and the next gate run re-emits the md line (C-HE-23 §2). Reported, not
            # raised: raising here would turn a recorded verdict into "not recorded".
            print(f"merge-gate-log: md-failure warn not recorded: {warn_exc}", file=sys.stderr)
        print(f"merge-gate-log: markdown write failed, JSONL row stands: {exc}", file=sys.stderr)
    return rows


def read_md_rows(md_path: Path | None = None) -> list[dict]:
    md_path = md_path or GATE_LOG_MD
    if not md_path.exists():
        return []
    out = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        m = _MD_ROW.match(line)
        if m:
            out.append(
                {
                    "ts": m["ts"],
                    "pr": int(m["pr"]),
                    "head_sha": m["head"],
                    "lens": m["lens"],
                    "verdict": m["verdict"],
                }
            )
    return out


def _gate_rows(jsonl_path: Path) -> list[dict]:
    """JSONL rows the reducer compares: lens verdict rows (finding / no_finding) on a `pr-N`
    arc. Wrapper rows (codex/gemini) and unavailability markers are not gate verdicts."""
    return [
        r
        for r in fr.read_rows(jsonl_path)
        if r["record_kind"] in ("finding", "no_finding")
        and _LENS_RE.match(r["producer"])
        and _ARC_PR_RE.match(r["arc_id"])
        and verdict_of(r) is not None
        # the join is ON head_sha (C-HE-23 §2): a row with no head has no sibling to compare
        # against, and a re-emitted `nohead` md line could never be re-parsed (gemini R1 P2)
        and r["head_sha"]
    ]


def _key(row: dict) -> tuple[int, str, str, str]:
    """The md-joinable key: `(pr, head12, lens, verdict)`."""
    m = _ARC_PR_RE.match(row["arc_id"])
    assert m is not None  # filtered by _gate_rows
    return (int(m.group(1)), (row["head_sha"] or "")[:12], row["producer"], verdict_of(row) or "")


def _emissions(jsonl_path: Path) -> dict[tuple, list[dict]]:
    """Gate rows grouped per EMISSION -- `(pr, head12, lens, verdict, round_n)` -- each worth
    exactly one md line. A BLOCK emission is several finding rows; an APPROVE one `no_finding`
    row. Keyed with the round so a second run at the same head is its own emission (codex R2
    P2: first-row-per-key dedupe lost every later round)."""
    out: dict[tuple, list[dict]] = {}
    for r in _gate_rows(jsonl_path):
        out.setdefault((*_key(r), r["round_n"]), []).append(r)
    return out


def consistency_report(md_path: Path | None = None, jsonl_path: Path | None = None) -> dict:
    """C-HE-23 §2 reducer. `missing_jsonl`: a markdown row with no JSONL sibling on the same
    `(pr, head_sha, lens, verdict)` -- the spec's `(pr, head_sha, verdict)` join, refined by
    lens so one lens's sibling never vouches for another's. `orphan_jsonl`: an emission with
    NEITHER a markdown sibling NOR its own `markdown_write_failed` warn (same head, lens AND
    round) -- the crash-between-the-two-writes class, reconciled by `reconcile_orphans`; one
    representative row per orphan emission is returned. Md lines are counted per key, so N
    emissions at one key need N md lines (or warns). Markdown rows that predate the first JSONL
    verdict are outside the comparison (the sibling did not exist)."""
    md_path = md_path or GATE_LOG_MD
    jsonl_path = jsonl_path or fr.GATE_LOG_JSONL
    emissions = _emissions(jsonl_path)
    first_ts = min((rows[0]["ts"] for rows in emissions.values()), default=None)
    md = [r for r in read_md_rows(md_path) if first_ts is not None and r["ts"] >= first_ts]
    md_count: dict[tuple, int] = {}
    for r in md:
        k = (r["pr"], r["head_sha"], r["lens"], r["verdict"])
        md_count[k] = md_count.get(k, 0) + 1
    jl_short = {k[:4] for k in emissions}
    # a warn vouches for ONE emission: same head, same lens, same round (codex R2 P2 -- keyed
    # without the round, a round-1 md failure would hide a round-2 crash between the writes)
    warned = {
        (r["head_sha"], r["producer"], r["round_n"])
        for r in fr.read_rows(jsonl_path)
        if r.get("cause_attribution") == "markdown_write_failed"
    }
    missing = sorted(k for k in md_count if k not in jl_short)
    orphan: list[dict] = []
    for short in sorted(jl_short):
        unwarned = [
            rows[0]
            for k, rows in sorted(emissions.items(), key=lambda kv: kv[0][4])
            if k[:4] == short and (rows[0]["head_sha"], rows[0]["producer"], k[4]) not in warned
        ]
        n = len(unwarned) - md_count.get(short, 0)
        if n > 0:
            orphan.extend(unwarned[-n:])  # the latest emissions are the ones without a line
    return {"missing_jsonl": missing, "orphan_jsonl": orphan}


def reconcile_orphans(md_path: Path | None = None, jsonl_path: Path | None = None) -> int:
    """Re-emit the markdown line for every orphan emission (next gate run, C-HE-23 §2).
    Touches the md file only when there is something to write."""
    md_path = md_path or GATE_LOG_MD
    jsonl_path = jsonl_path or fr.GATE_LOG_JSONL
    orphans = consistency_report(md_path, jsonl_path)["orphan_jsonl"]
    if not orphans:
        return 0
    emissions = _emissions(jsonl_path)
    with md_path.open("a", encoding="utf-8") as fh:
        for r in orphans:
            k = _key(r)
            n_findings = sum(
                1 for x in emissions[(*k, r["round_n"])] if x["record_kind"] == "finding"
            )
            fh.write(_md_line(r["ts"], k[0], r["head_sha"], k[2], k[3], n_findings))
    return len(orphans)


def _read_text(arg: str) -> str:
    return sys.stdin.read() if arg == "-" else Path(arg).read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="merge_gate_log", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("binding", help="print the six binding fields for one lens")
    b.add_argument("--lens", required=True)
    b.add_argument("--base", default="main")
    b.add_argument("--prompt-version", default=PROMPT_VERSION)
    b.add_argument("--config-hash", default=None)

    e = sub.add_parser("emit", help="record one lens verdict: JSONL first, markdown second")
    e.add_argument("--pr", type=int, required=True)
    e.add_argument("--lens", required=True)
    e.add_argument("--verdict-json", required=True, help="file with the lens output, or '-'")
    e.add_argument("--base", default="main")
    e.add_argument("--arc-id", default=None)
    e.add_argument("--lane-id", default=None)
    e.add_argument("--round-n", type=int, default=None)
    e.add_argument("--prompt-version", default=PROMPT_VERSION)
    e.add_argument("--config-hash", default=None)

    sub.add_parser("check", help="C-HE-23 §2 consistency reducer (exit 1 on a missing sibling)")
    sub.add_parser("reconcile", help="re-emit markdown rows for orphan JSONL verdicts")

    args = p.parse_args(argv)
    if args.cmd == "binding":
        try:
            print(
                json.dumps(
                    lens_binding(
                        REPO,
                        args.base,
                        args.lens,
                        prompt_version=args.prompt_version,
                        cfg_hash=args.config_hash,
                    ),
                    indent=2,
                    sort_keys=True,
                )
            )
        except GateLogError as exc:
            print(f"merge-gate-log: {exc}", file=sys.stderr)
            return 2
        return 0
    if args.cmd == "emit":
        try:
            # "the next gate run" (C-HE-23 §2): re-emit the md line of any orphan JSONL
            # verdict left by an earlier crash between the two writes (codex R2 P3)
            n = reconcile_orphans()
            if n:
                print(f"merge-gate-log: reconciled {n} orphan md row(s) from an earlier run")
            expected = lens_binding(
                REPO,
                args.base,
                args.lens,
                prompt_version=args.prompt_version,
                cfg_hash=args.config_hash,
            )
            outcome = rw.parse_verdict(CHANNEL, _read_text(args.verdict_json), expected)
            if outcome.terminal == "REVIEWER_UNAVAILABLE":
                # held to the orchestrator's binding so the marker row is bound to its head
                outcome.binding = dict(expected)
                outcome.failure_class = "transient"  # the remedy is re-running the lens
            rows = emit_gate_row(
                pr=args.pr,
                lens=args.lens,
                outcome=outcome,
                arc_id=args.arc_id,
                lane_id=args.lane_id,
                round_n=args.round_n,
            )
        except GateLogError as exc:
            print(
                f"merge-gate-log: NOT RECORDED ({exc}) -- the lens verdict does not count",
                file=sys.stderr,
            )
            return 2
        except Exception as exc:  # any other failure is "not recorded", never "BLOCK"
            # A missing verdict file, a failed git call, a malformed log: exit 2, not the
            # uncaught-exception exit 1 that the skills read as "BLOCK recorded" (codex R2 P2).
            print(
                f"merge-gate-log: NOT RECORDED ({type(exc).__name__}: {exc}) -- "
                "the lens verdict does not count",
                file=sys.stderr,
            )
            return 2
        print(
            f"merge-gate-log: {args.lens} {outcome.terminal} recorded "
            f"(round {rows[0]['round_n']}, {len(rows)} row(s), head {rows[0]['head_sha']})"
            + (f" -- {outcome.reason}" if outcome.reason else "")
        )
        # HEAD-moved guard (codex R2 P1): the rows are a true record of `expected["head_sha"]`,
        # but if the checkout moved while we recorded, this is NOT a verdict for the current
        # head -- the skill must not read exit 0/1 as one. Same rule as the codex wrapper.
        head_now = rw._git(REPO, "rev-parse", "HEAD")
        if head_now != expected["head_sha"]:
            print(
                f"merge-gate-log: HEAD moved during emit ({expected['head_sha'][:12]} -> "
                f"{head_now[:12]}); the recorded verdict is for the former head and does not "
                "count for the current checkout -- re-run the lens",
                file=sys.stderr,
            )
            return 2
        return rw.exit_code(outcome)
    if args.cmd == "check":
        rep = consistency_report()
        for k in rep["missing_jsonl"]:
            print(f"MISSING-JSONL pr={k[0]} head={k[1]} lens={k[2]} verdict={k[3]}")
        for r in rep["orphan_jsonl"]:
            print(f"ORPHAN-JSONL {r['finding_id']}")
        print(
            f"merge-gate-log: {len(rep['missing_jsonl'])} missing JSONL sibling(s), "
            f"{len(rep['orphan_jsonl'])} orphan JSONL verdict(s)"
        )
        return 1 if rep["missing_jsonl"] else 0  # orphans reconcile on the next gate run
    print(f"reconciled {reconcile_orphans()} orphan row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
