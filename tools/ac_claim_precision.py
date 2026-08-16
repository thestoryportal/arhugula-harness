"""B-167 step 3: measure what a claim-versus-recount gate would actually fire on.

`B-167` steps 1–2 established that a format-scoped acceptance-criteria recount **is**
buildable and exact where it applies (285 of 386 plan blocks), and landed it as
`leg_selfcheck.derive_acceptance_criteria_count` — **deliberately unwired**. Step 3 is the
precondition for wiring it: *"measure false positives against a sample of already-merged
arcs before wiring it into the pre-push path; a gate is only as useful as its precision."*

This module is that measurement, kept as code so the verdict can be re-derived rather than
trusted.

**What it measures.** Every `N acceptance criteria` / `N ACs` claim in `design-substrate/`
and `.harness/` that can be associated with a unit whose count the recount derives, then
compares. A disagreement is what a gate would fire on.

**Result (2026-08-16): the gate is NOT viable, and the cause is intrinsic.** 37 claims are
associable with a single, unambiguously-owning unit; **23 disagree — a 62% fire rate — and
18 of those 23 sit on lines carrying several numbers at once**, e.g.

    | U-RT-111 unit body | 7 ACs (12 declared with 5 STRUCK at v2.36 ...) |

Both numbers are correct: the plan states a **live** count and a **declared** count in one
sentence, because a delta chain records what was struck. A comparison gate cannot tell
which number it is looking at, and no better matcher fixes that — the ambiguity is in the
artifact, by design. At 62% firing with ~78% of firings legitimate, the gate would be muted
within two rounds, which is the outcome `B-167`'s own reasoning says to avoid.

**Three measurement traps this module exists to not repeat**, each caught before the
verdict was trusted and each having moved the number:

1. A first pass read **identifier digits as counts** — `U-CP-56 acceptance criteria` scored
   as a claim of *56* — and reported **68%**. Condemning a design on a strawman
   implementation is its own failure, so `U-XX-NN` / `#NN` / `vN.M` digits are excluded.
2. Attribution by **proximity** picked a cited dependency instead of the claim's owner on
   lines naming several units, manufacturing disagreements. Only claims with exactly ONE
   unit id on the line are scored now (out-of-family review [P2]).
3. The scan ingested **its own reporting carrier**: the register paragraph recording this
   result quotes the `7 ACs (12 declared…)` example, so the figure depended on having
   published it. `_REPORTING_CARRIERS` excludes it.

The honest rate after all three is **62%**, and the verdict is unchanged.

**Disposition.** The recount stays a *derivation* utility — a human or an arc can ask "what
is the real count?" and get an exact answer. The automatic claim-versus-truth comparison is
**refuted by measurement**, and `leg_selfcheck`'s existing claims-versus-claims check plus
diff context remains the sound ceiling, exactly as that tool's docstring already states.

Run: `python tools/ac_claim_precision.py`
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import leg_selfcheck as ls

ROOT = Path(__file__).resolve().parents[1]

_WORDS = {
    w: i
    for i, w in enumerate(
        "zero one two three four five six seven eight nine ten eleven twelve thirteen "
        "fourteen fifteen sixteen seventeen eighteen nineteen twenty".split()
    )
}

#: `N acceptance criteria` / `N ACs`. The leading look-behind keeps the digits of an
#: identifier (`U-CP-56`, `#12`, `v2.36`) from being read as the claimed count.
_CLAIM_RE = re.compile(
    r"(?<![\w#.-])(\d{1,2}|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|"
    r"thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\s+"
    r"(?:acceptance\s+criteri\w+|ACs?\b)",
    re.IGNORECASE,
)
_UNIT_RE = re.compile(r"\bU-[A-Z]+-\d+\b")
_UNIT_HEAD_RE = re.compile(r"^#+.*\bU-[A-Z]+-\d+\b.*$", re.MULTILINE)
#: Digit runs that belong to an identifier rather than to a count.
_IDENT_RE = re.compile(r"\b[A-Z]-[A-Z]+-\d+\b|#\d+\b|\bv\d+[._]\d+\b")
#: Carriers that RECORD this measurement's result. Scanning them is self-reference.
_REPORTING_CARRIERS = frozenset({"post-phase-8-forward-register.md"})

#: A line carrying three or more bare numbers is the declared-vs-struck-vs-live shape.
_BARE_NUMBER_RE = re.compile(r"(?<![\w#.-])\d{1,2}\b")


@dataclass(frozen=True)
class Precision:
    """What a claim-versus-recount gate would do against the real corpus."""

    units_with_derived_count: int
    associable_claims: int
    agree: int
    disagree: int
    disagree_on_multi_number_lines: int

    @property
    def fire_rate(self) -> float:
        return self.disagree / self.associable_claims if self.associable_claims else 0.0


def derived_counts(root: Path | None = None) -> dict[str, set[int]]:
    """Unit id → every count the recount derives for it across the plan corpus."""
    base = root or ROOT
    truth: dict[str, set[int]] = {}
    for path in sorted((base / "design-substrate").glob("Implementation_Plan_*.md")):
        text = path.read_text(encoding="utf-8")
        heads = list(_UNIT_HEAD_RE.finditer(text))
        for i, head in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
            count = ls.derive_acceptance_criteria_count(text[head.start() : end])
            if count is None:
                continue
            unit = _UNIT_RE.search(head.group(0))
            if unit:
                truth.setdefault(unit.group(0), set()).add(count)
    return truth


def _claimed_value(token: str) -> int | None:
    token = token.lower()
    return int(token) if token.isdigit() else _WORDS.get(token)


def measure(root: Path | None = None) -> Precision:
    """Compare every associable claim against the derived count."""
    base = root or ROOT
    truth = derived_counts(base)
    associable = agree = disagree = multi = 0

    for folder in ("design-substrate", ".harness"):
        for path in (base / folder).rglob("*.md"):
            # The register is where this measurement's RESULT is written, and that write
            # quotes the `7 ACs (12 declared…)` example verbatim. Scanning it would make
            # the reported figure depend on having reported it (review [P2]).
            if path.name in _REPORTING_CARRIERS:
                continue
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                ident_spans = [(m.start(), m.end()) for m in _IDENT_RE.finditer(line)]
                for claim in _CLAIM_RE.finditer(line):
                    if any(a <= claim.start(1) < b for a, b in ident_spans):
                        continue
                    value = _claimed_value(claim.group(1))
                    if value is None:
                        continue
                    # Ownership must be STRUCTURALLY unambiguous (review [P2]). A line
                    # naming several units — "…U-CP-34… 12 ACs for U-RT-111" — cannot be
                    # attributed by proximity: nearest-left picks the cited dependency and
                    # manufactures a disagreement. Those artificial firings would inflate
                    # the very rate this measurement uses to refute the gate.
                    units = {u.group(0) for u in _UNIT_RE.finditer(line)}
                    if len(units) != 1:
                        continue
                    unit_id = next(iter(units))
                    if unit_id not in truth:
                        continue
                    associable += 1
                    if value in truth[unit_id]:
                        agree += 1
                        continue
                    disagree += 1
                    if len(_BARE_NUMBER_RE.findall(line)) > 2:
                        multi += 1

    return Precision(len(truth), associable, agree, disagree, multi)


def main() -> int:
    p = measure()
    print("B-167 step 3 — claim-versus-recount precision")
    print(f"  units with a derived count     : {p.units_with_derived_count}")
    print(f"  claims associable to one       : {p.associable_claims}")
    print(f"    agree                        : {p.agree}")
    print(f"    disagree (a gate would fire) : {p.disagree}")
    print(f"      on multi-number lines      : {p.disagree_on_multi_number_lines}")
    print(f"  fire rate                      : {p.fire_rate * 100:.0f}%")
    print()
    print("  VERDICT: not viable as a gate. The dominant disagreement is a line stating a")
    print("  LIVE and a DECLARED count together ('7 ACs (12 declared with 5 STRUCK)'), where")
    print("  both numbers are correct. No matcher resolves that — the ambiguity is in the")
    print("  artifact. The recount stays a derivation utility; claims-versus-claims plus")
    print("  diff context remains the sound ceiling.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
