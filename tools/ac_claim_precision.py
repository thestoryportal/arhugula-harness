"""B-167 step 3: the OBSTACLES a claim-versus-recount gate must solve. NOT a precision figure.

`B-167` steps 1–2 established that a format-scoped acceptance-criteria recount **is**
buildable and exact where it applies (285 of 386 plan blocks), and landed it as
`leg_selfcheck.derive_acceptance_criteria_count` — **deliberately unwired**. Step 3 asks
for a false-positive measurement *"before wiring it into the pre-push path; a gate is only
as useful as its precision."*

**This module does NOT deliver that measurement, and step 3 is NOT complete.** Three
successive attempts produced 68%, then 40%, then 62%, each after out-of-family review found
a different methodological flaw — and the third round showed the *classification* behind the
verdict was itself unsupported. Reporting a fourth number would be guessing with extra
steps. What survives, and is genuinely useful, is the **census of obstacles** each attempt
uncovered: every one is a real shape in this corpus that a naive comparison mishandles.

**The obstacles, each observed here.**

1. **Identifier digits read as counts.** `U-CP-56 acceptance criteria` is not a claim of
   fifty-six. Excluding `U-XX-NN` / `#NN` / `vN.M` moved the figure 68% → 40%.
2. **Attribution by proximity.** On a line naming several units — *"…U-CP-34… 12 ACs for
   U-RT-111"* — nearest-left picks the cited dependency and manufactures a disagreement.
   Only single-unit lines can be attributed structurally.
3. **Self-reference.** The register paragraph recording a result quotes the corpus examples
   it cites, so the measured figure came to depend on having published it.
4. **Revision collapse — UNSOLVED.** This corpus keeps every delta revision, so a unit-id
   key collapses them: `U-AS-06` derives `{6, 8}`, which lets a **stale** claim of 6 score
   as agreement, while `U-RT-106`'s v2.32 claims are compared against a v2.31 body. **Neither
   models what a pre-push gate would have seen when each arc merged.**
5. **Count semantics — UNSOLVED.** Not every match is a total-count claim. `+1 AC`,
   `ZERO acceptance criterion change`, `STRUCK 4 ACs` and `AC #1` are deltas and references.
   The `>2 bare numbers` heuristic below cannot tell those from a genuine live-versus-declared
   line, so **any claim that "most firings are legitimate ambiguity" is unsupported.**
6. **Carrier population.** `leg_selfcheck.check_counts` treats `.md`, `.yaml` and `.yml` as
   eligible; this scan reads `.md` only, so its population is not the gate's population.

**What a sound step-3 measurement requires** — stated so the next attempt does not repeat
these: replay each merged arc against its **then-current plan head** (or otherwise preserve
revision identity); **validate count semantics** before classifying a firing, excluding
delta and reference forms and confirming true live-versus-declared cases individually; and
use the **gate's own carrier eligibility**. That is substantial work, and it is what step 3
actually costs.

**Disposition.** `B-167` stays **open**. The recount remains a *derivation* utility and
remains **unwired**; `leg_selfcheck`'s claims-versus-claims check plus diff context remains
the shipped behaviour, as its docstring already says. No refutation of the gate is claimed,
and no endorsement either — the honest state is *not yet measured*.

The counters below are retained because they locate the obstacle shapes, not because their
ratio means anything. Run: `python tools/ac_claim_precision.py`
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
    print("  NOT A PRECISION FIGURE. Revision collapse and unvalidated count semantics")
    print("  (obstacles 4 and 5 in the module docstring) are UNSOLVED, so this ratio does")
    print("  not model the gate. B-167 step 3 remains incomplete and the recount stays")
    print("  unwired. See the docstring for what a sound measurement requires.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
