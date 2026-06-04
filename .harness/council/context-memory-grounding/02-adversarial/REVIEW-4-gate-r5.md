# Adversarial Review #2 (GATE) — Round 5 (evidence-enrichment) · Stage E4 — verbatim

> Genuine `harness-adversarial-reviewer` invocation · workflow `wf_de7a33be-c4e` · single bounded gate-reviewer, schema-free · residual sweep on candidate DESIGN.md v2 + the consolidated reconcile · 2026-06-04.

---

The advisor confirms my analysis and sharpens the classification decisively: this is **CLEAR-WITH-FOLD**, not LOOP-BACK. The key insight I'll fold in: WS-3a has a live byte-count-*independent* MVP trigger (the 2 dangling patterns at 5/5 + store-not-git-versioned), so the falsified number is drift, not a workstream-killer. And critically — the *event that falsified the number* (an ad-hoc, apparently-lossy compaction that dropped ~75 index entries between session-context-assembly and now) is itself a live D4 incident that **reaffirms** WS-3a's enforced/non-lossy/supersede-mark contract. The finding strengthens the plan.

Let me do the residual-close verification the advisor flagged (guardrail 3) before composing, plus a quick confirm of the anti-bloat self-application watch-points in §9 and the INCOMPLETE verdict in §3 — these are quick re-reads of v2 text I already have, so I can confirm them directly. I have everything I need. Let me write the deliverable.

# Adversarial Review #2 (GATE) — Round 5 evidence-enrichment — E4

**Verdict: CLEAR-WITH-FOLD** — v2 correctly absorbed all 7 consolidated dispositions + the 4 routed residuals; the only material empirical failure is the **MEMORY.md "over-cap now (27,051B)" premise (§5 WS-3a), which is stale at HEAD (actual 10,306B, under cap)** — a §4.1-Class-1 drift / §2.7.6-Class-3 informational fold, NOT a loop-back, because WS-3a's MVP inclusion rests on a live *byte-count-independent* trigger that still holds. Fold the reframe + 2 trivial cite nits, then commit.

*(Taxonomy note per SKILL: findings below use the §4.1 review-severity scale, where Class-3 is severe. The task's verdict line uses the §2.7.6 Phase-7 fork scale, where Class-3 is informational/foldable. Each finding is dual-labeled to prevent the conflation. **No finding rises to a §2.7.6 Class-1 halt** — this is a plan-revision arc, not execution.)*

---

## Absorption check

Per-disposition fold verification against the consolidated reconcile (`c{8,9,3,5,2,7}.md`) → DESIGN.md v2:

| Reconciled disposition | Absorbed in v2? | Cite |
|---|---|---|
| **C8 ITEM-1** — `INCOMPLETE-on-{D4,D6}` verdict; REBUT minimum-exposure floor; FOLD D4-vs-D6 asymmetry | **YES** | §3 pass-condition ¶: "WS-0 returns `INCOMPLETE-on-{D4,D6}`, never a clean `SOUND`/`PASS`"; "A minimum-exposure floor is **rebutted**… *report* coverage, don't *force* it"; "D4 carries a *second standing signal*… D6 has no standing mitigation". Also §0 change-note, §2, §8 step 4, §10. |
| **C8 ITEM-6** — re-affirm WS-0 = one matrix / Robert's eyes / zero tooling (covering all 3 labels) | **YES** | §3 "Proportionality re-affirmed (C8, F2-02)": codebook-lens + `not-exercised` cell-rule + `INCOMPLETE` verdict "are **all reads off the one matrix Robert already fills**… WS-0 remains one matrix, Robert's eyes, zero new tooling." |
| **C9 ITEM-2** — dormant-G-LINK + `[ -f ]` SUFFICIENT; name reinject-pointer-resolvability MVP deliverable; no G-LINK pulled | **YES** | §5 X-min: "the `postcompact-reinject.sh:28` `[ -f ]` absence-guard is the floor… the *resolution-validation* dimension… rides the deferred G-LINK `--check` *when live*, **NOT G1**". §6 G-LINK row + §7 recovery-pointer lane. |
| **C3 ITEM-3** — FOLD degree-keyed selection rule into WS-3a; HOLD dir-split set-aside; REBUT compute engine (grep-by-eye); thresholds moving | **YES** | §5 WS-3a "Degree-keyed selection rule": KEEP-HOT ≥5 / KEEP-LINKED 1–4 / ARCHIVE-JIT the 39; "Thresholds operator-tunable against a moving count (the top hub grew 65→83…)"; "Report the degree by eye (`grep \| wc -l`); do **not** build a degree-recompute engine"; dir-split "**refused**". |
| **C3 ITEM-4** — NEW one-time MVP hygiene write of the 2 dangling patterns; recurring consolidation DEFERRED | **YES** | §5 WS-3a "One-time hygiene": writes the 2 named slugs; "the *recurring* consolidation mechanism stays deferred (§6)". §6 row confirms recurring stays deferred. |
| **C5 ITEM-5** — L1 scoped to scan-discovered invariants, NOT the hard-coded `[i]` example; rides WS-1; judge-free | **YES** | §5 WS-1 "L1 deterministic assertion": "Scope to *scan-discovered invariants* — the `[i]`-citation check is an *illustration of the form*, not a hard-coded work-item… Judge-free (catch-rate 1.0…), MVP-admissible where κ/TPR/TNR/L2-judge are not." §7 L1 lane. |
| **C7 ITEM-7** — un-anchored INDEX discharges T3 legibility-lien; 3-integer line canonical + supersedes EVID triple; line stays exactly 3 | **YES** | §5 WS-2a: "discharges C7's T3 legibility-lien (the lien requires version-discoverability, not `#section`-precision)". §5 WS-3a health-line: 3 named integers "**supersede** EVID Finding-4's illustrative `orphan%/density/true-break` triple". §7 health-line: "stays exactly 3 integers". |

**Spot-checks the mandate named — all present:**
- **WS-0 `INCOMPLETE-on-{D4,D6}` verdict (§3):** present, with the D4-discharge-via-≥4-ref-inventory / D6-no-mitigation asymmetry.
- **minimum-exposure floor REBUTTED (not snuck back):** §3 explicitly "is rebutted"; §0 calls it "adopted over a minimum-exposure floor, which was rebutted as bloat." Not reintroduced anywhere.
- **degree-key + supersede-mark + 3-integer health-line + 2-note hygiene (§5 WS-3a):** all four present and correctly scoped.
- **L1 scoped to dependency-scan invariants, not the `[i]` example (§5 WS-1):** present.
- **FM-H decentralized-handoff/store-OCC sharpen + reinject-pointer requirement riding `[ -f ]` / G-LINK NOT G1 (§5 X-min + §7):** present; §5 "FM-H is a *decentralized-handoff* topology… serialization must live at the store (OCC), not the topology"; §7 "rides the `[ -f ]` guard / G-LINK, **NOT G1**".
- **G-LINK DEFER→MVP-on-trigger + recurring consolidation deferred (§6):** both deferred rows present with named triggers.
- **un-anchored INDEX floor + do-not-invent / do-not-author guardrails (§5 WS-2a):** present ("do **NOT** invent `GC.md`/`ROUTING.md`/`CATALOG.md`… do **NOT** author `WORKFLOWS.md`… forbid `@import`-ing").
- **C7 T3-lien discharge + canonical-3-integer supersession (§3/§5):** present.

**Absorption verdict: COMPLETE.** Every reconciled disposition folded; no disposition dropped, none silently mutated.

---

## Empirical re-verification at HEAD

I re-grepped/read every load-bearing claim (did NOT take the plan's word):

| Claim | Verified? | Note |
|---|---|---|
| MEMORY.md = **27,051B > 24,400B** (§5 WS-3a premise) | ❌ **FAILS** | `wc -c` at canonical path = **10,306B / 56 lines / 45 index entries**, mtime **Jun 4 06:27 today** — **UNDER cap**. The 27,051B was true when v2 + E2 + the reconcile were authored earlier today; an interceding ad-hoc compaction (my session-context shows 25.6KB / ~120 entries → now 10.3KB / 45 entries, ~75 index entries dropped at 06:27) falsified it. → **F1-G1 (fold).** *See finding below — the falsifying event reaffirms WS-3a, it does not weaken it.* |
| 2 dangling ≥4-ref patterns unwritten (`plan-revision-against-not-yet-built-substrate` + `strike-revision-on-refined-second-tier-reason`) | ✅ **CLEAN** | Both note files **absent**; in-degree **5** and **5**. v2 §5 says "both ~5 inbound refs, no note file at HEAD" — **correct**. (E2's "4×" for the strike pattern was the error; v2's "~5" is right.) The WS-3a MVP trigger is live. |
| `session-end-cleanup.sh` MEMORY.md-cap section at **:49-58** | ◑ **resolves; 2-line over-count** | Section is `:49`–`:56` (echo `:49`, over-cap logic `:52-53`, `else`/fi/`}` `:54-57`). v2's `:49-58` (the F1-01 fold of `:49-53`) over-counts by ~2 lines. Anchor + rider-home hold. Drift-only nit. |
| `CLAUDE.md §12.5.1` false-git-claim at **:651** | ✅ **CLEAN** | `CLAUDE.md:651` = "Provenance lives in git history at the global memory store." Byte-exact; §-cite correct. |
| moving hub count **65→83** (advisor-…) | ✅ **CLEAN** | `grep \| wc -l` = **83** at HEAD. C2's grep claim + the "re-derive at slim-time" reframe confirmed. |
| reinject-pointer targets resolve (`postcompact-reinject.sh:24` roadmap / `:28` `[ -f ]` guard) | ✅ **CLEAN; guard 2 lines off** | `:24` = `hook_roadmap_next .harness/roadmap_status.md`; `:28` = `CK=…precompact-latest.md`; `:30` = the `[ -f "$CK" ]` absence-guard. The guard is at `:30` not `:28` (immaterial cite-drift); the absence-guard exists exactly as claimed and graceful-degrades. |
| memory store NOT git-versioned (X-min / FM-H / §12.5.1-false premise) | ✅ **CLEAN** | `git rev-parse` → "not a git repository." All three premises hold. |

**Net: one material failure (MEMORY.md byte premise) + two immaterial cite-drifts (`:49-58`, `:30`-not-`:28`); every other anchor verifies byte-exact.** The MEMORY.md failure is a fold, not a blocker — adjudicated below.

---

## Anti-bloat self-application

The arc's own discipline turned on v2, per the 5 mandated watch-points (§9 restates all five verbatim; I verified each holds in the actual fold text, not just the §9 assertion):

| Watch-point | Verdict | Evidence |
|---|---|---|
| Degree-key stays **grep-by-eye** (not a daemon) | **PASS** | §5 WS-3a: "Report the degree by eye (`grep \| wc -l`); do **not** build a degree-recompute engine." §9 restates. C2+C3 both pre-bounded it. |
| One-time hygiene stays a **finite 2-note write** (not the recurring pass promoted) | **PASS** | §5 WS-3a: "A finite one-time MVP write; the *recurring* consolidation mechanism stays deferred (§6)." §6 row keeps recurring deferred. |
| L1 stays a **one-shot precondition** (not a standing CI gate) | **PASS** | §5 WS-1: "a code assertion fired **once at slim-time**". §9: "L1 stays a one-shot precondition (not a standing CI gate)." |
| INCOMPLETE verdict stays a **matrix read** (not new tooling) | **PASS** | §3: "all reads off the one matrix Robert already fills — none adds a session, tool, synthetic case, or model-judge." §9: "the INCOMPLETE verdict stays a matrix read (not new tooling)." |
| SessionEnd line stays **exactly 3 integers** (not accreted to 5 by re-importing EVID's triple) | **PASS** | §5 WS-3a: "**exactly three** grep-derived integers"; "These three **supersede** EVID Finding-4's illustrative… triple" (supersede, not append). §7: "stays exactly 3 integers." C7 R2 explicitly watched the back-door triple-expansion. |

**Did 8 folds make v2 the governance-bloat the arc refuses? NO.** v2 is ~143 lines; the MVP table is still 6 rows (§4); every Round-5 fold is a *rule/one-shot/rider* on an existing workstream, never a new MVP workstream (the only new *mechanism*, G-LINK, is DEFERRED §6). The deferred tail (§6) remains large-on-purpose (8 rows). The proportionality spine held in the artifact, not just in assertion — **PASS on all 5 watch-points.**

---

## INCOMPLETE-verdict falsifiability

**Sound — a real gate that can return INCOMPLETE and block a clean SOUND; not ceremony.**

Pressure-tested on the mandate's four sub-questions:

1. **Can WS-0 actually return INCOMPLETE and block a clean SOUND?** **Yes.** The verdict is a *third value at the verdict level* (§3): when D4 or D6 has zero incidents in *both* arms, the output is literally `INCOMPLETE-on-{D4,D6}`, "never a clean `SOUND`/`PASS`." A `SOUND` *requires* those classes were exercised OR an explicit operator waiver. This is the C8-ITEM-1 insight that a footnote doesn't travel with a binary PASS but a verdict value does — the honesty is structurally enforced, not prose-appended.

2. **Is the D4-vs-D6 asymmetry sound?** **Yes, and empirically grounded.** D4 carries a *second standing signal* — the §5 WS-3a `≥4-ref-unwritten` health-line inventory (I verified this signal is live: 2 patterns at 5/5 right now) — so `INCOMPLETE-on-D4` may be *discharged* by that inventory. D6 (instruction-conflict) has **no** standing mitigation — no health-line count, no inventory — so `INCOMPLETE-on-D6` is "the only honest verdict when D6 is unexercised." The asymmetry isn't ornamental; it changes which INCOMPLETE is discharge-able. Sound.

3. **Does "report coverage, don't force it" genuinely protect against the rare-class false-green, or just relabel it?** **Genuinely protects.** The failure mode is: Arm B improves D1/D2 while D4/D6 sit at 0≤0 and a naive gate reads PASS — the slim ships validated on classes it never tested. INCOMPLETE refuses that PASS *without* importing the minimum-exposure floor (which would force synthetic session-curation — the CA-2 bloat). It is strictly more honest than annotate (a footnote a PASS-reader skips) and strictly cheaper than a floor (no forced coverage). It does not relabel; it changes the gate's *output contract* so the un-measured case cannot masquerade as the measured one.

4. **Is it proportionate?** **Yes** — zero new tooling; one additional verdict value read off the one matrix Robert already fills. It is the eval-engineer's minimum duty (the gate must not lie about what it didn't measure) discharged at near-zero cost.

The verdict is the right altitude: the minimum-exposure floor over-reached (forcing function/machinery), the annotate-only footnote under-reached (doesn't travel with a binary PASS), the verdict value is exactly right. **Falsifiable, not ceremony.**

---

## Findings (classified)

### F-G1 — MEMORY.md "over-cap now (27,051B)" premise is stale at HEAD; reframe (do not number-bump)

- **Location:** DESIGN.md §5 WS-3a: *"the index stays ≤ cap by compaction; MEMORY.md is loaded every session and over-cap now (27,051B > 24,400B)."* (Also echoed §0 change-note context.)
- **Defect:** `wc -c` at the canonical path returns **10,306B / 45 index entries** (mtime Jun 4 06:27 today) — the file is **UNDER cap (42% of the 24,400B limit)**. The 27,051B figure was accurate when v2 / the E2 review / the consolidated reconcile were authored earlier today (and matches this session's loaded system-reminder, 25.6KB / ~120 entries), but an **interceding ad-hoc compaction dropped ~75 index entries at 06:27**, falsifying the instantaneous byte premise. This is the workspace's named *sibling-staleness / stale-carry-text* defect class (SKILL checklist items 1–2), and it is precisely the first item the gate mandate flagged to re-verify.
- **Why it does NOT loop the arc:** WS-3a's MVP inclusion does **not** depend on the instantaneous byte count. It rests on a **live, byte-count-independent trigger** I verified at HEAD: the 2 dangling ≥4-ref patterns (5/5, no file) + the store-not-git-versioned recoverability gap. The byte count is a fast-moving number the plan *elsewhere* correctly treats as re-derive-at-slim-time (the 65→83 hub). A naive number-bump (`27,051→10,306`) would invert "over-cap" to "under-cap" and make WS-3a's own headline read as self-defeating ("enforced compaction… under cap now") — the wrong fix. The correct fold **re-grounds the premise on the robust facts**: MEMORY.md is *loaded every session* + *oscillates across the cap under churn* + *the ≥4-ref hygiene trigger is met now* + *the store is not versioned*.
- **The sharp point (corroboration, changes nothing in the verdict):** the very event that falsified the number is a **live D4 (memory-pollution) incident** — an unenforced, apparently-lossy compaction silently dropping ~75 index entries between session-context assembly and now. That is *exactly* what WS-3a's enforced / supersede-mark / non-lossy contract exists to replace. **The finding strengthens the plan; it does not weaken it.** v2 should state this explicitly so a downstream reader does not misread "under-cap-now ⇒ WS-3a unneeded."
- **Discriminator:** (a) — affects substantive content of the v2 plan (a load-bearing WS-3a premise), self-contained to this arc; resolution does not touch any upstream-phase artifact. → **§4.1 Class-1 (drift)** / **§2.7.6 Class-3 (informational; fold + commit).** *Decided.* **Not a §2.7.6 Class-1 halt — no LOOP-BACK.**
- **Resolution path (shape, not text):** reframe the WS-3a premise to the byte-count-independent justification (loaded-every-session + cap-oscillation-under-churn + the live 2-pattern hygiene trigger + store-not-versioned); drop the instantaneous byte assertion as load-bearing; add a one-line note that the interceding lossy compaction is the live D4 the enforced-compaction contract addresses. Fold at commit; do not loop.

### F-G2 — Two immaterial cite-drifts (fold with F-G1)

- **Location:** §5 WS-3a (`session-end-cleanup.sh:49-58`); §5 X-min + §7 (`postcompact-reinject.sh:28`).
- **Defect:** The cap section is `:49`–`:56` (closing brace `:57`), not `:49-58` (the F1-01 fold itself over-counts by ~2 lines). The `[ -f "$CK" ]` absence-guard is at `:30`, not `:28` (`:28` is the `CK=` assignment). Both anchors resolve; semantics unaffected.
- **Discriminator:** (a/b/c) all miss — line-range drift that doesn't change semantics. → **§4.1 Class-1 (drift).** *Decided.*
- **Resolution path:** inline cite correction when the fold lands (`:49-56` and `:30`).

**No Class-2 (§4.1) or Class-3 (§4.1) findings. No §2.7.6 Class-1 (halt) findings. No NEW Class-1-equivalent architectural defect introduced by the v2 enrichment.**

---

## The 4 routed residuals — closed in v2 text?

Per the consolidated reconcile's "Residuals carried to E4" + the gate mandate item 5:

1. **Reinject-pointer + `superseded_by` share ONE link-`--check` input set when G-LINK promotes (C9+C3).** **CLOSED** — §6 G-LINK row: "When live, the reinject pointer + `superseded_by` share **one input set**." Validator-target list in the same row names both. ✅
2. **C5's home-correction: recovery-pointer rides `[ -f ]` guard / G-LINK target-class, NOT G1 (byte-budget ≠ link-integrity).** **CLOSED** — §5 X-min: "rides the deferred G-LINK `--check` *when live*, **NOT G1**"; §7 recovery-pointer lane: "rides the `[ -f ]` guard / G-LINK, **NOT G1** (byte-budget ≠ link-integrity)"; §5 WS-4 G1: "G1 is… **byte-budget, NOT link-integrity**." No conflation in the §6 wording. ✅
3. **Anti-bloat watch — folds stay rules/one-shots (degree-key grep-by-eye / hygiene finite / L1 one-shot / INCOMPLETE matrix-read / 3-integer line).** **CLOSED** — all 5 verified above (§9 restates verbatim + I confirmed each in the actual fold text). ✅
4. **F1-01 (cite range) + F1-02 (canonical 3 integers + EVID-triple supersession).** **FOLDED** — §5 WS-3a folds both (F1-01 as `:49-58` — itself slightly off per F-G2; F1-02 names the canonical 3 integers + the supersession). ✅

Plus the **F1-01/F1-02 folds** the mandate named separately: present in §5 WS-3a (F1-02 correct; F1-01's range off by 2 lines per F-G2). **All 4 residuals genuinely closed in v2 text; none left open.**

---

## Findings considered and rejected (transparency)

- **R-1 — INCOMPLETE verdict is decorative / unfalsifiable:** REJECTED. Pressure-tested on all 4 axes (verdict-level value, D4/D6 asymmetry empirically grounded, protects-not-relabels, proportionate). D6 can genuinely block a clean SOUND. Sound gate.
- **R-2 — minimum-exposure floor snuck back in under another name:** REJECTED. §3 explicitly rebuts it; §0 records it as "rebutted as bloat"; no §4/§5/§6 text reintroduces forced coverage. The INCOMPLETE verdict is the *lighter* alternative, not a relabeled floor.
- **R-3 — A8 framing contamination (persona/stack/deployment overcommit):** REJECTED. v2 is rigorously solo-developer-scoped; every fold filtered against the solo+drift lens; the long canon-refusal list (numbered-folders, dir-split, consolidation daemon, eval cascade, embedding rot-scores) IS the proportionality discipline A8 protects. No committed surface violated; no not-committed value picked.
- **R-4 — A4 fabricated cite (ICM=arXiv:2603.16021v2):** REJECTED — E2 WebFetch-verified byte-exact; v2 §0/§5 cite it consistently; not re-litigated here.
- **R-5 — degree-key / hygiene / L1 / health-line accreted into machinery (the gate's own discipline failing):** REJECTED — all 5 anti-bloat watch-points PASS in the actual fold text, not just §9's assertion.
- **R-6 — X-AL-3 / additive-only / plan-not-execution violation introduced by enrichment:** REJECTED — §9 hard-lane discipline intact; no `design-substrate/**` content, no `harness-*/src`, no `R-NNN`, no versioned-copy deletion; the §12.5.1 correction is explicitly routed as *execution-arc* work under the clearance/`design-phase-direct` hatch. The plan remains a plan.
- **R-7 — number-bump fix for F-G1 (27,051→10,306):** REJECTED as the resolution — it inverts the WS-3a headline to self-defeating. The reframe (byte-count-independent premise) is the correct fold; confirmed with the advisor.
- **R-8 — second blocker manufactured from the cite-drifts (`:49-58`, `:28`):** REJECTED — both immaterial, fold-only; manufacturing a blocker to look thorough is the trap the mandate warned against.
- **R-9 — reviewing the council instead of the artifact (FM-H):** Self-check — every finding grounds in a DESIGN.md § or a verified HEAD file:location (`MEMORY.md` 10,306B, `CLAUDE.md:651`, hub-83, `postcompact-reinject.sh:30`), not in "a voice under-weighted X."
- **R-10 — proportionality-as-soft-over-adoption (the meta-attack):** REJECTED — re-tested on v2: 6-row MVP unchanged, every Round-5 fold a rider/one-shot, the only new mechanism (G-LINK) deferred. The de-bloat effort did not become bloat in the enriched artifact.

---

## Verdict + what (if anything) must change before commit

**CLEAR-WITH-FOLD** (§2.7.6 Class-3 only — fold + commit; no §2.7.6 Class-1/2 open; no LOOP-BACK).

v2 correctly absorbed all 7 consolidated dispositions and closed all 4 routed residuals in text; the INCOMPLETE verdict is a genuine falsifiable gate; the 5 anti-bloat watch-points all PASS; cite-verification is otherwise byte-exact; no NEW Class-1 architectural defect and no X-AL-3 / additive-only / plan-not-execution violation was introduced.

**Two folds before commit (both §4.1 Class-1 drift / §2.7.6 Class-3 informational — neither loops the arc):**

1. **F-G1 (material):** Reframe the §5 WS-3a premise off the stale instantaneous byte count. MEMORY.md is **10,306B (under cap) at HEAD** — re-ground WS-3a on its byte-count-independent justification (loaded-every-session + cap-oscillation-under-churn + the live 2-dangling-pattern hygiene trigger, verified 5/5 + store-not-versioned). Add one line noting the interceding ad-hoc lossy compaction (~75 index entries dropped at 06:27) is the live D4 incident the enforced/non-lossy/supersede-mark contract exists to prevent — **so the finding reaffirms WS-3a rather than weakening it.** Do **not** number-bump (that would invert the headline to self-defeating).
2. **F-G2 (trivial):** Correct the two cite-drifts at fold-time — `session-end-cleanup.sh:49-56` (not `:49-58`) and `postcompact-reinject.sh:30` (not `:28`).

Record both in v2 §5 WS-3a (+ the §-cite corrections), then **commit**. The arc does not re-open. The proportionality spine held under its own discipline.