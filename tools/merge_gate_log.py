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
    merge_gate_log.py binding --lens <id> [--base main]        -> writes the six fields to a
                                                                  file; prints only that path
    merge_gate_log.py emit --pr N --lens <id> --verdict-json F  -> record; exit 0/1/2
    merge_gate_log.py adjudicate --finding-id I --disposition D --actor A -> §5 row; 0/2
    merge_gate_log.py check                                      -> consistency reducer
    merge_gate_log.py reconcile                                  -> re-emit orphan md rows

Emit-time attribution (C-HE-24 §2, v1.6 X6d, U-HE-47): every lens row leaves `emit` with
non-null `cause_attribution` + `unique_catch` (`attribute_lens_row`, applied under the log
lock against the codex rounds already recorded); `adjudicate` is the absorption step's
append-only disposition write.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import time
from collections.abc import Callable, Mapping
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
#: `| <ts> | #<pr> | <head12> | <lens> | <APPROVE|BLOCK|REVIEWER_UNAVAILABLE> | <n> finding(s)
#: | r<round> |`.
#: The round column makes each line's identity exact -- two same-second reruns at one head,
#: lens and verdict are distinct lines (codex R9 P2). The legacy per-PR narrative rows
#: (`| #NNNN | <date> | <branch> | ... |`) do not match it.
_MD_ROW = re.compile(
    r"^\|\s*(?P<ts>\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ)\s*\|\s*#(?P<pr>\d+)\s*\|\s*"
    r"(?P<head>[0-9a-f]{12})\s*\|\s*(?P<lens>merge-gate-[a-z-]+)\s*\|\s*"
    r"(?P<verdict>APPROVE|BLOCK)\s*\|\s*(?P<n>\d+) finding\(s\)\s*\|\s*r(?P<round>\d+)\s*\|"
)
#: The lens contract's trailing line (merge-gate SKILL.md "Parsing -- fail closed"): EXACTLY
#: `VERDICT: APPROVE` or `VERDICT: BLOCK: <reason>` -- a FULL-line match, so `VERDICT: APPROVE
#: or BLOCK` / `VERDICT: APPROVE (tentative)` are ambiguous, not approvals (codex R6 P1), and a
#: bare `VERDICT: BLOCK` without its reason is not a verdict either (merge-gate L3 on #1399).
_VERDICT_LINE = re.compile(r"^VERDICT: (?:(APPROVE)|(BLOCK): \S.*)$")
_ARC_PR_RE = re.compile(r"^pr-(\d+)$")


class GateLogError(RuntimeError):
    """The gate step must fail: the machine record could not be written."""


#: Bounded wait for the emission lock (local reads + two appends).
EMIT_LOCK_TIMEOUT_S = 30.0


def _emit_lock_path(jsonl_path: Path) -> Path:
    return jsonl_path.with_name(jsonl_path.name + ".emit.lock")


def _under_emit_lock(jsonl_path: Path, body: Callable[[], object]) -> object:
    """Serialize every (JSONL-append + md-append) emission and every orphan reconciliation on
    ONE `flock` over a lock file BESIDE the machine log (codex R4 P2: emitter B reconciling A's
    not-yet-md'd emission wrote A's line, then A wrote it again -> a duplicate md row with no
    emission). Beside the JSONL, not the md: the md log may be unwritable (that is the warn
    path) and the JSONL's own lock is taken inside `finding_record` on a separate descriptor
    (a second flock on the same file from one process would self-block). Admissible like
    `finding_record._lock_exclusive`: a REPO-resident record, not QUEUE_DIR coordination
    state (C-HE-02 §1's flock ban is scoped to those modules). Kernel-released on process
    death, so a crashed emitter never wedges the next gate run."""
    lock = _emit_lock_path(jsonl_path)
    try:
        lock.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(lock, os.O_WRONLY | os.O_CREAT, 0o644)
    except OSError as exc:
        # the machine log's directory is unwritable: nothing can be recorded (C-HE-15 §1)
        raise GateLogError(f"gate verdict could not be recorded: emission lock: {exc}") from exc
    try:
        deadline = time.monotonic() + EMIT_LOCK_TIMEOUT_S
        delay = 0.005
        while True:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    raise GateLogError(
                        f"could not lock {lock} within {EMIT_LOCK_TIMEOUT_S}s"
                    ) from None
                time.sleep(delay)
                delay = min(delay * 2, 0.1)
        try:
            return body()
        finally:
            fcntl.flock(fd, fcntl.LOCK_UN)
    finally:
        os.close(fd)


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


#: The producers whose rows ARE the preceding review rounds for the X6d attribution join --
#: the same set `arc_metrics.REVIEW_ROUND_PRODUCERS` reduces rounds from: the codex channel
#: and its D-C failover, which reviews "at the identical bar" (C-HE-17 §3).
CODEX_ROUND_PRODUCERS = frozenset({"codex_review_wrapper", "gemini_review_wrapper"})


def attribute_lens_row(obs: dict, log_rows: list[dict]) -> dict:
    """C-HE-24 §2 (v1.6 X6d): populate `cause_attribution` + `unique_catch` on every
    merge-gate lens observation at emission time -- null-everywhere attribution ([B] F16:
    44/44 rows) is not legal for new merge-gate rows, and this attributor is the single
    writer-side enforcement point (every new lens row flows through `emit_gate_row`).

    Gate-lens `unique_catch` join, spec-fixed so the emitter invents nothing: true iff no
    same-arc `finding` row from a codex round matches on `(location, finding_type)` -- an
    intra-arc heuristic keyed on location+type, never `finding_id` (C-HE-24 §4's
    cross-`head_sha` identity exclusion stands). Marker rows carry `unique_catch=false`
    (nothing caught, so nothing uniquely caught) -- non-null, per the every-lens-row rule."""
    if obs["record_kind"] == "reviewer_unavailable":
        # cause_attribution already carries reviewer_unavailable_<class> from outcome_rows
        return {**obs, "unique_catch": False}
    if obs["record_kind"] == "no_finding":
        return {**obs, "cause_attribution": "clean_approve", "unique_catch": False}
    matched = any(
        r["record_kind"] == "finding"
        and r["arc_id"] == obs["arc_id"]
        and r["producer"] in CODEX_ROUND_PRODUCERS
        and r["location"] == obs["location"]
        and r["finding_type"] == obs["finding_type"]
        for r in log_rows
    )
    return {
        **obs,
        "cause_attribution": "codex_round_overlap" if matched else "gate_unique_catch",
        "unique_catch": not matched,
    }


def verdict_of(row: dict) -> str | None:
    """APPROVE / BLOCK from a gate row's `finding_type` (the wrapper encoding), else None."""
    ft = row.get("finding_type", "")
    if ft == "clean-approve":
        return "APPROVE"
    if ft == "terminal-block":
        return "BLOCK"
    return None


def _md_line(
    ts: str, pr: int, head_sha: str, lens: str, terminal: str, n_findings: int, round_n: int
) -> str:
    return (
        f"| {ts} | #{pr} | {head_sha[:12]} | {lens} | {terminal} | {n_findings} finding(s) "
        f"| r{round_n} |\n"
    )


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
    return _under_emit_lock(  # type: ignore[return-value]
        jsonl_path,
        lambda: _emit_gate_row_locked(
            pr, lens, outcome, arc_id, lane_id, round_n, md_path, jsonl_path
        ),
    )


def _emit_gate_row_locked(
    pr: int,
    lens: str,
    outcome: rw.ReviewOutcome,
    arc_id: str,
    lane_id: str,
    round_n: int | None,
    md_path: Path,
    jsonl_path: Path,
) -> list[dict]:
    try:
        rows = rw.emit_outcome(
            outcome,
            producer=lens,
            arc_id=arc_id,
            lane_id=lane_id,
            round_n=round_n,
            path=jsonl_path,
            attributor=attribute_lens_row,  # X6d: emit-time attribution, same critical section
        )
    except (OSError, fr.RecordError) as exc:  # (1) machine record FIRST; unrecordable = no verdict
        raise GateLogError(f"gate verdict could not be recorded: {exc}") from exc
    head = rows[0]["head_sha"] or "nohead"
    try:
        with md_path.open("a", encoding="utf-8") as fh:  # (2) human view second
            fh.write(
                _md_line(
                    rows[0]["ts"],
                    pr,
                    head,
                    lens,
                    outcome.terminal,
                    len(outcome.findings),
                    rows[0]["round_n"],
                )
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
                    unique_catch=False,  # X6d: no null-attribution lens-producer rows
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


#: The lane's persisted identity (lane-init's single-writer file, U-HE-31) — the
#: holder-binding authority for headless adjudication, read from DISK, never from env.
LANE_ID_FILE = REPO / ".harness" / ".lane-id"


def arc_not_held_reason(arc_id: str) -> str | None:
    """The holder-state authority half of headless adjudication (codex r5 P1: the
    HARNESS_ARC_ID prefix is caller-chosen text, not authority — the record_phase pattern
    binds the claim to reservation state instead). None = `arc_id` has a live
    (pending/open) reservation HELD by this lane per the persisted `.harness/.lane-id`;
    otherwise the refusal reason. Fail-closed: a missing reservations substrate, absent
    lane file, unreadable store, terminal state, or another lane's hold all REFUSE — a
    historical (merged/abandoned) arc is terminal, so its findings can never be disposed
    through the auto-allowed venue."""
    try:
        import reservations as rs
    except ImportError:
        return "no reservations substrate: arc-bound adjudication requires it"
    try:
        lane = LANE_ID_FILE.read_text(encoding="utf-8").strip()
    except OSError as exc:
        return f"lane identity unreadable ({exc}): not a lane venue"
    try:
        res = rs.current(arc_id)  # -> tuple[generation, payload] | None
    except Exception as exc:
        return f"reservation store unreadable ({exc})"
    if res is None:
        return f"arc {arc_id!r} has no reservation"
    head = res[1]
    if head.get("state") not in ("pending", "open"):
        return f"arc {arc_id!r} reservation is terminal ({head.get('state')!r})"
    if head.get("lane_id") != lane:
        return f"arc {arc_id!r} is held by lane {head.get('lane_id')!r}, not this lane"
    return None


def adjudicate(
    finding_id: str,
    disposition: str,
    actor: str,
    jsonl_path: Path | None = None,
    expected_arc: str | None = None,
) -> dict:
    """C-HE-24 §5 (v1.6 X6d): append ONE `finding_adjudication` row for `finding_id` -- the
    absorption step's disposition write. The row copies the finding's immutable core verbatim
    (two rows with one id differ only by ts / record_kind / disposition / disposition_actor /
    unique_catch) and carries a later `ts`; `unique_catch` is carried forward so the reducer's
    last row keeps the emit-time attribution. Every §5 invariant -- actor ≠ producer, strictly
    later ts, finding-rows-only, no-write-after-adjudication -- is enforced at the single
    write-time checkpoint (`finding_record.validate` / `_check_against_prior_rows`), not here.
    `expected_arc` is the arc-binding authority half (codex r4 P1): when given, a target
    row from any OTHER arc is refused — the CLI passes `HARNESS_ARC_ID`, so the guard's
    auto-allowed headless form can only dispose the current arc's own findings; a
    cross-arc adjudication requires the operator venue (no env, ask-gated command).
    Raises `GateLogError` for an unknown finding_id; a `RecordError` propagates from the
    append (never swallowed)."""
    jsonl_path = jsonl_path or fr.GATE_LOG_JSONL
    prior = [r for r in fr.read_rows(jsonl_path) if r["finding_id"] == finding_id]
    if not prior:
        raise GateLogError(f"no row with finding_id {finding_id!r} on {jsonl_path}")
    base = prior[0]  # core-immutable fields are identical across the lineage
    if expected_arc is not None:
        if base["arc_id"] != expected_arc:
            raise GateLogError(
                f"finding {finding_id!r} belongs to arc {base['arc_id']!r}, not the current "
                f"arc {expected_arc!r} — cross-arc adjudication is an operator action"
            )
        # Holder check at the TIGHTEST window (codex r6 P2; held + registered as B-222 at
        # r7/r8): re-verified here, immediately before the append, not only at the CLI
        # edge. The residual race is the append itself — reservation store and gate log
        # have no common lock. Held rationale: a §6 holder transfer is dead-claim
        # recovery of a crashed/idle lane, not a concurrent adversary, and the row this
        # invocation lands is exactly the row it was authorized to write moments earlier
        # — the transfer changes nothing about the invocation's own content (its
        # disposition/actor were chosen by the then-authorized caller, and both venue
        # actors are absorbers bound to the same finding lineage).
        reason = arc_not_held_reason(expected_arc)
        if reason is not None:
            raise GateLogError(reason)
    row = {
        **base,
        "record_kind": "finding_adjudication",
        "ts": fr.now_iso(),
        "disposition": disposition,
        "disposition_actor": actor,
        "unique_catch": prior[-1]["unique_catch"],
    }
    fr.append_row(row, jsonl_path)
    return row


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
                    "n_findings": int(m["n"]),
                    "round_n": int(m["round"]),
                }
            )
    return out


def _gate_rows(jsonl_path: Path) -> list[dict]:
    """JSONL rows the reducer compares: lens verdict rows (finding / no_finding). Wrapper rows
    (codex/gemini) and unavailability markers are not gate verdicts. The arc_id's SHAPE is not
    a filter (U-HE-47 codex r5 P1): since U-HE-34 the carriers pass the reservation arc id, so
    a `pr-N`-only filter silently dropped every such verdict from the comparison and reported
    its md line as MISSING-JSONL (23 live rows at the fix's head)."""
    return [
        r
        for r in fr.read_rows(jsonl_path)
        if r["record_kind"] in ("finding", "no_finding")
        and _LENS_RE.match(r["producer"])
        and verdict_of(r) is not None
        # the join is ON head_sha (C-HE-23 §2): a row with no head has no sibling to compare
        # against, and a re-emitted `nohead` md line could never be re-parsed (gemini R1 P2)
        and r["head_sha"]
    ]


def _key(row: dict) -> tuple[str, str, str]:
    """The md-joinable key: `(head12, lens, verdict)`. `pr` is NOT in the key — the JSONL row
    carries the reservation arc, not the PR (the md line is the pr authority; ts + finding
    count + round disambiguate emissions at one key, and tamper-evidence is out of scope —
    C-HE-23 §2 drops hash-chaining for append-only adjudication)."""
    return ((row["head_sha"] or "")[:12], row["producer"], verdict_of(row) or "")


def _emissions(jsonl_path: Path) -> dict[tuple, list[dict]]:
    """Gate rows grouped per EMISSION -- `(arc_id, head12, lens, verdict, round_n)` -- each
    worth exactly one md line. A BLOCK emission is several finding rows; an APPROVE one
    `no_finding` row. Keyed with the round so a second run at the same head is its own
    emission (codex R2 P2: first-row-per-key dedupe lost every later round), and with the
    ARC so two arcs gating one head at the same round stay distinct emissions (codex R4 P2,
    re-keyed from pr to arc_id at U-HE-47 r5 -- the arc is on every row; the pr is not)."""
    out: dict[tuple, list[dict]] = {}
    for r in _gate_rows(jsonl_path):
        out.setdefault((r["arc_id"], *_key(r), r["round_n"]), []).append(r)
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
    # EVERY structured md line is compared -- no time window (codex R3 P1: with zero surviving
    # emissions a window filtered every md row out, so a deleted machine log passed). Only
    # this module writes the structured shape; the legacy narrative rows never match it.
    # keyed WITHOUT pr (codex r5 P1): the JSONL side carries the reservation arc, not the PR,
    # so pr lives only on the md line — it rides along in the value for reporting.
    md_by_key: dict[tuple, list[tuple[str, int, int, int]]] = {}
    for r in read_md_rows(md_path):
        k = (r["head_sha"], r["lens"], r["verdict"])
        md_by_key.setdefault(k, []).append((r["ts"], r["n_findings"], r["round_n"], r["pr"]))
    # a warn vouches for ONE emission: same head, same lens, same round (codex R2 P2 -- keyed
    # without the round, a round-1 md failure would hide a round-2 crash between the writes)
    warned = {
        (r["arc_id"], r["head_sha"], r["producer"], r["round_n"])
        for r in fr.read_rows(jsonl_path)
        if r.get("cause_attribution") == "markdown_write_failed"
    }
    # per key, the UNWARNED emissions (as (ts, finding_count, representative row), latest
    # round last) and the md lines (as (ts, finding_count)) must match as MULTISETS (codex R3
    # P2: key membership alone let one emission vouch for N md rows, and a BLOCK that lost a
    # finding row stayed green; codex R8 P2: without `ts` a duplicated round-1 line could
    # stand in for a lost round-2 line -- each md line carries its emission's ts, and
    # `reconcile_orphans` re-emits with that same ts)
    em_by_key: dict[tuple, list[tuple[str, int, int, dict]]] = {}
    for k, rows in sorted(emissions.items(), key=lambda kv: kv[0][4]):
        # the warn vouches for ONE emission: same arc, head, lens AND round (codex R2/R4
        # P2 -- two arcs at one head+lens both have a round 1)
        if (k[0], rows[0]["head_sha"], rows[0]["producer"], k[4]) in warned:
            continue
        n_findings = sum(1 for x in rows if x["record_kind"] == "finding")
        em_by_key.setdefault(k[1:4], []).append((rows[0]["ts"], n_findings, k[4], rows[0]))
    missing: list[tuple] = []
    orphan: list[dict] = []
    for k in sorted(set(md_by_key) | set(em_by_key)):
        ems = list(em_by_key.get(k, []))
        for ts, n, rn, pr in sorted(md_by_key.get(k, [])):
            match = next(
                (i for i, (ets, c, er, _) in enumerate(ems) if (ets, c, er) == (ts, n, rn)), None
            )
            if match is None:
                # an md line with no emission of that identity; pr reported from the md side
                missing.append((pr, *k, ts, n, rn))
            else:
                ems.pop(match)
        orphan.extend(row for _, _, _, row in ems)  # emissions left without an md line
    return {"missing_jsonl": missing, "orphan_jsonl": orphan}


def _pr_of(row: dict) -> int | None:
    """The PR an orphan emission belongs to — from a `pr-N` arc id, or nothing. The md
    line is the ONLY pr authority; the reservation store is deliberately NOT consulted
    (codex r6 P2 -> r7 P1, settled by deletion: its `pr` is mutable across the arc's
    life, so any reconstruction from it can relabel an old verdict — head-binding only
    narrowed the window. A lost md line for a reservation-arc emission is REPORTED and
    left standing by the caller, never re-derived from a second, mutable authority)."""
    m = _ARC_PR_RE.match(row["arc_id"])
    return int(m.group(1)) if m else None


def reconcile_orphans(
    md_path: Path | None = None,
    jsonl_path: Path | None = None,
    *,
    arc_id: str | None = None,
    pr: int | None = None,
    head_sha: str | None = None,
) -> int:
    """Re-emit the markdown line for every orphan emission (next gate run, C-HE-23 §2).
    Touches the md file only when there is something to write.

    PR recovery has exactly two authorities, neither mutable (codex r7 P1 -> r8 P2 ->
    r9 P2): a `pr-N` arc id on the row itself, or — for reservation-arc rows — the
    CALLER's own `(arc_id, pr, head_sha)` triple when `emit` runs reconciliation: the
    gate rerun after a crash invokes `emit --pr N --arc-id <arc>` at the SAME reviewed
    head, so recovery fires only for orphans matching BOTH the arc and this
    invocation's head — the pr trusted here is exactly the pr the same invocation is
    about to write on its own md line, and a later-head or mistyped invocation cannot
    relabel an older emission. Any other orphan is reported loudly and left standing —
    never re-derived from the mutable reservation store."""
    md_path = md_path or GATE_LOG_MD
    jsonl_path = jsonl_path or fr.GATE_LOG_JSONL

    def body() -> int:
        orphans = consistency_report(md_path, jsonl_path)["orphan_jsonl"]
        if not orphans:
            return 0
        emissions = _emissions(jsonl_path)
        written = 0
        with md_path.open("a", encoding="utf-8") as fh:
            for r in orphans:
                row_pr = _pr_of(r)
                if (
                    row_pr is None
                    and arc_id is not None
                    and r["arc_id"] == arc_id
                    and head_sha is not None
                    and r["head_sha"] == head_sha
                ):
                    row_pr = pr
                if row_pr is None:
                    print(
                        f"merge-gate-log: orphan for arc {r['arc_id']!r} round {r['round_n']} "
                        "has no recoverable PR; left standing",
                        file=sys.stderr,
                    )
                    continue
                k = _key(r)
                n_findings = sum(
                    1
                    for x in emissions[(r["arc_id"], *k, r["round_n"])]
                    if x["record_kind"] == "finding"
                )
                fh.write(
                    _md_line(r["ts"], row_pr, r["head_sha"], k[1], k[2], n_findings, r["round_n"])
                )
                written += 1
        return written

    # under the same lock emission holds: an in-flight emitter's JSONL-but-not-yet-md state
    # is never observable here (codex R4 P2)
    return int(_under_emit_lock(jsonl_path, body))  # type: ignore[arg-type]


#: Where lens responses live for `emit` (the skills write them here; gitignored).
LENS_SCRATCH = REPO / ".harness" / "tmp"
#: The trust root `open_scratch_dir()` walks down from, validating EVERY component below it.
#: Stated rather than implied, because a containment claim needs a stopping point: this is the
#: directory holding the module being executed, so an actor who can replace it has already
#: replaced this code and no check here could bind them. Above the anchor is out of scope by
#: construction; below it, nothing is (codex r3 P2 -- `O_NOFOLLOW` on `tmp` alone left
#: `.harness` itself swappable for a symlink containing a real `tmp`).
SCRATCH_ANCHOR = REPO


def open_scratch_dir() -> int:
    """A descriptor for `LENS_SCRATCH`, refusing a symlink at ANY component (codex r1/r2/r3).

    Returns an fd rather than a path because the path-shaped version of this rule was
    check-then-use: `is_symlink()` answered a question about the directory, and every later
    `mkdir` / `os.open` / `os.replace` re-traversed the name, so another process could swap a
    component in between and the auto-allowed recipe would publish outside the repository.
    Each component from `SCRATCH_ANCHOR` down is opened `O_DIRECTORY|O_NOFOLLOW` relative to
    the previous descriptor, so the check and the capture are the same syscall at every level
    and callers then work `dir_fd`-relative against an inode no later rename can repoint.
    ONE enforcer, so `binding` and `emit` cannot drift apart.

    The caller owns the returned fd and must close it.
    """
    try:
        parts = LENS_SCRATCH.relative_to(SCRATCH_ANCHOR).parts
    except ValueError as exc:  # a scratch dir outside its own anchor is a wiring error
        raise GateLogError(f"{LENS_SCRATCH} is not under {SCRATCH_ANCHOR}") from exc
    try:
        fd = os.open(SCRATCH_ANCHOR, os.O_RDONLY | os.O_DIRECTORY)
    except OSError as exc:
        raise GateLogError(f"{SCRATCH_ANCHOR} is not a usable scratch anchor: {exc}") from exc
    for part in parts:
        # Provision descriptor-relative, never through the path. A `mkdir(parents=True)` on
        # `LENS_SCRATCH` runs BEFORE any of this and follows symlinked ancestors, so a
        # `.harness` pointing at a writable outside directory with no `tmp` child had the
        # auto-allowed recipe CREATE that outside `tmp` before the refusal ever fired
        # (codex r4 P2). Best-effort here on purpose: the open below is the single authority
        # on whether this component is usable, and it reports the one specific refusal.
        with contextlib.suppress(OSError):
            os.mkdir(part, 0o755, dir_fd=fd)
        try:
            nxt = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=fd)
        except OSError as exc:
            os.close(fd)
            raise GateLogError(
                f"{LENS_SCRATCH} is not a usable scratch directory ({part!r}): {exc}"
            ) from exc
        os.close(fd)
        fd = nxt
    return fd


def binding_path(lens: str, values: Mapping[str, str]) -> Path:
    """Where `binding` publishes one lens's six values (U-SR-03, charter WR-09).

    A prompt names this path so the orchestrator never handles a value: both round-3 lens
    corruptions were orchestrator TRANSCRIPTION errors -- a truncated `head_sha` and a
    spliced `base_sha` -- not lens errors ([B] F3).

    The name is CONTENT-ADDRESSED: a digest over all six values, so identical name implies
    identical contents and the file is immutable by construction. Keyed on anything less,
    it is a mutable cell that two invocations share -- a lens launched against one contract
    can read values republished under another and copy them into its verdict, and `emit`,
    which recomputes against the current state, accepts the mismatch (codex r1 P1 on the
    lens-only key, r2 P1 on lens+head: `base_sha`, `diff_digest`, `config_hash` and
    `prompt_version` all vary independently of the head, and `config_hash` changes whenever
    a carrier is edited mid-arc, which this very arc does). Digesting the whole binding
    closes every dimension at once instead of one per review round. The lens id stays in the
    name for legibility only; `_LENS_RE` has already accepted it, so it carries no separator.
    """
    digest = hashlib.sha256(
        json.dumps(values, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return LENS_SCRATCH / f"merge-gate-binding-{lens}-{digest}.json"


#: The only files a post-gate "log-only" commit may touch (C-HE-23 §2 sibling + human view).
GATE_ROW_FILES = frozenset({".harness/merge-gate-log.jsonl", ".harness/merge-gate-log.md"})


def _blob(repo: Path, ref: str, path: str) -> bytes:
    """The file's bytes at `ref`, or b"" when absent there."""
    proc = subprocess.run(
        ["git", "-C", str(repo), "show", f"{ref}:{path}"], capture_output=True, check=False
    )
    return proc.stdout if proc.returncode == 0 else b""


def landing_delta(
    reviewed_head: str, final_head: str = "HEAD", repo: Path | None = None
) -> list[str]:
    """What in reviewed..final is NOT a gate-row append. Empty means the approvals transfer
    (a gate-row-only delta, the rule both merge-gate carriers state); anything else means the
    final head carries unreviewed change and the gate must re-run (codex R8 P1; the U-HE-23
    landing predicate, landed early). A gate-log file counts as a row append ONLY if its
    reviewed-head bytes are a strict prefix of its final-head bytes -- a truncation, rewrite
    or deletion of either log is a change, not a record (codex R9 P2)."""
    repo = repo or REPO
    out = rw._git(repo, "diff", "--name-only", reviewed_head, final_head)
    changed = [f.strip() for f in out.splitlines() if f.strip()]
    bad: list[str] = []
    for f in changed:
        if f not in GATE_ROW_FILES:
            bad.append(f)
            continue
        before, after = _blob(repo, reviewed_head, f), _blob(repo, final_head, f)
        if not after.startswith(before) or len(after) <= len(before):
            bad.append(f"{f} (not an append: rewritten, truncated or removed)")
    return sorted(bad)


def _read_text(arg: str) -> str:
    """`-` (stdin) or a REGULAR file that RESOLVES under `.harness/tmp/` -- the documented
    scratch dir. A relative path is the only shape the permission guard auto-allows, and a
    relative symlink could point anywhere (codex R7 P2); resolving first and pinning the
    destination closes that, and the content is never echoed (see the VERDICT-line check)."""
    if arg == "-":
        return sys.stdin.read()
    name = Path(arg).name
    bad = GateLogError(
        f"--verdict-json must be '-' or a regular file directly under {LENS_SCRATCH} (got {arg!r})"
    )
    # The documented shape is flat (`.harness/tmp/merge-gate-lens-<id>.txt` in both merge-gate
    # carriers), so the read is `dir_fd`-relative to the captured scratch inode and a name
    # carrying any separator is refused outright -- no traversal, and no re-walk of a path
    # another process could repoint between the check and the open (codex R7 P2, r2 P2).
    if not name or name != arg.rsplit("/", 1)[-1]:
        raise bad
    dfd = open_scratch_dir()
    try:
        # The supplied directory must BE the captured one, compared by identity. Comparing
        # its BASENAME accepted `other/tmp/verdict.txt` while the read still came from
        # `.harness/tmp/verdict.txt` -- emit would record a different, possibly stale verdict
        # instead of failing closed (codex r4 P2). `samestat` cannot be fooled by naming.
        try:
            same = os.path.samestat(os.stat(Path(arg).parent), os.fstat(dfd))
        except OSError as exc:
            raise bad from exc
        if not same:
            raise bad
        # `O_NONBLOCK` so the TYPE check can happen at all: a FIFO planted at this
        # auto-allowed name makes a blocking `O_RDONLY` wait for a writer forever, so
        # `emit` wedges before `fstat` ever runs and a local actor can stall the gate
        # (codex r5 P2). This is the class-1 rider's own idiom -- `O_NOFOLLOW|O_NONBLOCK`
        # plus a post-open `S_ISREG` -- which the first draft applied only by halves. On a
        # regular file the flag has no further effect.
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=dfd)
    except OSError as exc:
        raise bad from exc
    finally:
        os.close(dfd)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise bad
        return stream.read().decode("utf-8")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="merge_gate_log", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("binding", help="print the six binding fields for one lens")
    b.add_argument("--lens", required=True)
    b.add_argument("--base", default="main")
    b.add_argument("--prompt-version", default=PROMPT_VERSION)

    e = sub.add_parser("emit", help="record one lens verdict: JSONL first, markdown second")
    e.add_argument("--pr", type=int, required=True)
    e.add_argument("--lens", required=True)
    e.add_argument("--verdict-json", required=True, help="file with the lens output, or '-'")
    e.add_argument("--base", default="main")
    e.add_argument("--arc-id", default=None)
    e.add_argument("--lane-id", default=None)
    e.add_argument("--round-n", type=int, default=None)
    e.add_argument("--prompt-version", default=PROMPT_VERSION)

    a = sub.add_parser(
        "adjudicate", help="append the C-HE-24 §5 finding_adjudication row (absorption step)"
    )
    a.add_argument("--finding-id", required=True)
    a.add_argument("--disposition", required=True, choices=["accepted", "rejected", "suppressed"])
    a.add_argument(
        "--actor",
        required=True,
        help="disposition_actor: the adjudicating party; must differ from the finding's producer",
    )

    sub.add_parser("check", help="C-HE-23 §2 consistency reducer (exit 1 on a missing sibling)")
    sub.add_parser("reconcile", help="re-emit markdown rows for orphan JSONL verdicts")
    ld = sub.add_parser(
        "landing-delta", help="exit 1 if reviewed..final touches anything but the gate-log rows"
    )
    ld.add_argument("--reviewed", required=True, help="the head the lenses approved")
    ld.add_argument("--final", default="HEAD", help="the head about to merge")

    args = p.parse_args(argv)
    if args.cmd == "binding":
        # `config_hash` is ALWAYS the independent digest of the current carriers -- no CLI
        # override on either command (codex R5 P2: a shared arbitrary value would let a verdict
        # bind to nothing); tests patch `config_hash` itself.
        try:
            values = lens_binding(REPO, args.base, args.lens, prompt_version=args.prompt_version)
            dfd = open_scratch_dir()  # provisions the chain itself, inside the walk
        except GateLogError as exc:
            print(f"merge-gate-log: {exc}", file=sys.stderr)
            return 2
        # [LAW:effects-at-boundaries] `lens_binding` computes; the write happens here, at the
        # CLI edge. The values are published to a FILE and stdout carries only its path
        # (charter WR-09): a value the orchestrator never sees is a value it cannot mistype.
        out = binding_path(args.lens, values)
        # Everything below is relative to the descriptor opened above, never to the name:
        # temp-then-`os.replace` so a lens never reads a half-written binding, `O_EXCL` so a
        # pre-planted temp fails loudly instead of being written through, `O_NOFOLLOW` so
        # neither component is a symlink, and `dir_fd=` so no step can be redirected by a
        # rename of `.harness/tmp` after the check (codex r2 P2).
        tmp_name = f"{out.name}.{os.getpid()}.tmp"
        try:
            try:
                fd = os.open(
                    tmp_name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=dfd,
                )
                with os.fdopen(fd, "w", encoding="utf-8") as stream:
                    stream.write(json.dumps(values, indent=2, sort_keys=True) + "\n")
                os.replace(tmp_name, out.name, src_dir_fd=dfd, dst_dir_fd=dfd)
            except OSError as exc:
                # A planted temp name, a full disk, or a failed replace is a gate error like
                # any other -- exit 2 with a message, never an uncaught traceback (codex r3
                # P3). The temp is removed on the way out so a transient failure cannot make
                # the NEXT run fail with `O_EXCL` on a leftover it did not create.
                with contextlib.suppress(OSError):
                    os.unlink(tmp_name, dir_fd=dfd)
                print(f"merge-gate-log: could not publish {out.name}: {exc}", file=sys.stderr)
                return 2
        finally:
            os.close(dfd)
        print(out)
        return 0
    if args.cmd == "emit":
        try:
            expected = lens_binding(REPO, args.base, args.lens, prompt_version=args.prompt_version)
            # "the next gate run" (C-HE-23 §2): re-emit the md line of any orphan JSONL
            # verdict left by an earlier crash between the two writes (codex R2 P3).
            # This invocation's own (arc, pr, head) triple is the recovery authority for
            # the same arc's reservation-arc orphans (codex r8 P2, head-bound at r9 P2:
            # recovery fires only for orphans AT THIS INVOCATION's reviewed head — the
            # gate-rerun-after-crash scenario — so a later-head or mistyped-pr run can
            # never relabel an older emission; those stay loudly standing).
            n = reconcile_orphans(
                arc_id=args.arc_id or f"pr-{args.pr}",
                pr=args.pr,
                head_sha=expected["head_sha"],
            )
            if n:
                print(f"merge-gate-log: reconciled {n} orphan md row(s) from an earlier run")
            text = _read_text(args.verdict_json)
            outcome = rw.parse_verdict(CHANNEL, text, expected)
            if outcome.terminal in ("APPROVE", "BLOCK"):
                # the lens contract's trailing `VERDICT:` line must AGREE with the schema
                # block -- JSON APPROVE + `VERDICT: BLOCK` (or no line) is not a verdict
                # (codex R3 P2); the block alone never records an ambiguous response
                tail = [ln.strip() for ln in text.splitlines() if ln.strip()]
                m = _VERDICT_LINE.fullmatch(tail[-1]) if tail else None
                line_verdict = (m.group(1) or m.group(2)) if m else None
                if line_verdict != outcome.terminal:
                    outcome = rw.ReviewOutcome(
                        "REVIEWER_UNAVAILABLE",
                        CHANNEL,
                        None,
                        "final VERDICT line absent or disagrees with the schema block",
                        [],
                        None,
                        outcome.source,
                    )
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
        try:
            head_now = rw._git(REPO, "rev-parse", "HEAD")
        except Exception as exc:  # the record stands; whether it is for THIS head is unknown
            print(
                f"merge-gate-log: recorded, but HEAD could not be re-read ({exc}) -- the verdict "
                "does not count for the current checkout; re-run the lens",
                file=sys.stderr,
            )
            return 2
        if head_now != expected["head_sha"]:
            print(
                f"merge-gate-log: HEAD moved during emit ({expected['head_sha'][:12]} -> "
                f"{head_now[:12]}); the recorded verdict is for the former head and does not "
                "count for the current checkout -- re-run the lens",
                file=sys.stderr,
            )
            return 2
        return rw.exit_code(outcome)
    if args.cmd == "adjudicate":
        # the guard-required headless form: HARNESS_ARC_ID names an arc, and that claim is
        # bound to reservation HOLDER state inside adjudicate(), immediately before the
        # append (codex r5 P1 authority; codex r6 P2 window), never to the caller's text.
        expected_arc = os.environ.get("HARNESS_ARC_ID")
        try:
            row = adjudicate(
                args.finding_id,
                args.disposition,
                args.actor,
                expected_arc=expected_arc,
            )
        except (GateLogError, fr.RecordError) as exc:
            print(f"merge-gate-log: NOT ADJUDICATED ({exc})", file=sys.stderr)
            return 2
        except Exception as exc:  # OSError etc.: "not recorded" is exit 2, never exit 1
            # Same rule as `emit` (codex R2 P2 there; codex r1 P3 here): an unreadable or
            # unwritable log is NOT a recorded disposition -- the skill's exit-2 retry
            # handling must see it, and exit 1 is not part of this verb's contract.
            print(
                f"merge-gate-log: NOT ADJUDICATED ({type(exc).__name__}: {exc})",
                file=sys.stderr,
            )
            return 2
        print(
            f"merge-gate-log: {row['finding_id']} disposed {row['disposition']} "
            f"by {row['disposition_actor']}"
        )
        return 0
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
    if args.cmd == "landing-delta":
        try:
            extra = landing_delta(args.reviewed, args.final)
        except Exception as exc:  # an unresolvable ref is NOT a clean delta
            print(f"merge-gate-log: landing delta could not be computed: {exc}", file=sys.stderr)
            return 2
        for f in extra:
            print(f"UNREVIEWED {f}")
        print(
            f"merge-gate-log: {args.reviewed[:12]}..{args.final[:12]} touches "
            f"{len(extra)} non-gate-row file(s); approvals "
            + ("TRANSFER" if not extra else "DO NOT TRANSFER -- re-gate")
        )
        return 1 if extra else 0
    print(f"reconciled {reconcile_orphans()} orphan row(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
