# B-96 council record — in-family adversarial round-3 findings (2026-08-01)

The in-family round-3 pass ran to completion after the fold was interrupted; its full report lived only in the orchestrator session, so the actionable content is preserved here for the finisher. **Disposition: cleared with current-phase revision — ZERO Class-3; the C-2 verdict and all TWELVE conditions verified CLEAN** (condition counts, per-pass arithmetic, all round-2 empirical claims re-verified by direct read, anchor-drift note exactly right incl. the +14/+17 split, B-108 row schema-clean and tool-verified, X-AL-3 clean).

**The shared shape of all three Class-2s — fix as ONE propagation sweep, not three point edits:** each is a correction applied to the output but not propagated to the text that supports it. After fixing, sweep: "does any OTHER text in the record still assert what a fold retired?"

## Class 2 (fix before ready-for-review)

- **F2-01** — §4A.1 (line ~267 + supporting ~260–265) still asserts verbatim the round-2-falsified premise "the report log survives process exit" AND the retired trend argument ("oldest-entry age strictly growing at each reset"), contradicting folded conditions #6/#7(c)/#8(b)/#12. Line ~262's "stops growing past the condition-#7 bound" is doubly stale (C3-1: #7 states no evaluable bound). Fix: mark the superseded step in place (the record's own discipline at §4.2b/§4.3(2)/P8/condition #4), don't silently delete.
- **F2-02** — condition #8 (line ~418) carries BOTH the retired three-way attribution table sentence ("Crossed with the age... discriminates... ⇒ the repeating sidecar-loss loop") AND its round-3 replacement forbidding exactly that ("CANDIDATE readings the operator discriminates, never an attribution the surface asserts"; "'age over bound' is NOT a predicate the store can evaluate"). Reconcile or mark the earlier sentence superseded — a spec-writer transcribing top-down currently encodes the forbidden form first.
- **F2-03** — the line-5 COMPLETE banner calls §11.2c an "in-family adversarial pass"; §11.2c's own heading says OUT-of-family (`just codex-review`). Also this in-family round-3 pass is recorded nowhere in §11 — add §11.2d (this file is the source) and fix the banner's family labels + scope its completeness claim in the same edit.

## Class 1 (inline)

- **F1-01** — §11 preamble (~line 491) says "Three decorrelated passes"; §11 enumerates four (+ §11.2d makes five).
- **F1-02** — same line: "five of the fifteen absorbed findings" — denominator wrong under every reading (per-pass rows: 6+12+3+5 = 26 before §11.2d). Recompute; numerator (five Codex-alone) is correct.
- **F1-03** — §7.1 preamble (~line 407) attributes the last amendment to the round-2 fold; round 3's NARROWING amended #8 after that. Extend the provenance sentence; the twelve count is TRUE and needs no change.
- **F1-04** — §6 TENSION-1 Stakes row (~line 376) over-reaches: condition #11's fail-safe half is a correctness term derived from #4 and would be owed under C3's original position too; only #11's EMISSION half traces to TENSION-1. Scope the claim or state the reading intended.

## Verified-clean list (do NOT re-litigate)

Condition set = 12 everywhere; per-pass header arithmetic; nothing load-bearing lost in the round-2 replacement; #5↔#6↔#9↔#12 candidate-class union consistent; #6↔#7(c)↔#8(b)↔#12 durability-consistent (sole inconsistency is F2-01's turn text); all round-2 code claims byte-verified (`:797`–`:802`, `:543`, `:590`, zero handler config in all seven src trees, emissions `:830/:839/:849/:855`); B-108 row + snapshot + `--check` green (108 items / 19 registered_finding); mkstemp name-reuse cannot break the grace (fresh mtime fails past-TTL at `:777`); anchor map v1.109→v1.110 byte-exact. B-108's "30 emission sites" vs a 29 measurement is a regex artifact, not a finding. External-canon mode: un-run, concurred low-yield — keep recorded as such.
