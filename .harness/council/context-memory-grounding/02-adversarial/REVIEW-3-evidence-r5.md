# Adversarial Review #1 — Round 5 (evidence-enrichment) · Stage E2 — verbatim

> Genuine `harness-adversarial-reviewer` invocation · workflow `wf_34b95aca-d0b` · single bounded reviewer, schema-free · red-teams the reconciled E1 deliberation + the proposed DESIGN.md v2 integration plan · 2026-06-04.

> **Verdict: CLEAR-to-E2b-reconcile** — 3 Class-2 in-arc revisions + 2 Class-1 nits, 0 Class-3; cite-verification CLEAN; no missed cross-cutting tensions; 8/9 pattern checklist PASS.

---

The ICM cite **resolves**: `arXiv:2603.16021v2`, "Interpretable Context Methodology: Folder Structure as Agentic Architecture," Van Clief & McDermott, v2 March 18 2026 — byte-exact to the council's cite (`c2.md:11`). The 28-page figure matches the council's "DEEP Dive 1 (ICM...)" framing. Cite-verification is now CLEAN on every load-bearing anchor.

I have everything. Before composing, a final synthesis of my adjudication against the advisor's guidance, then I deliver. The verdict is **CLEAR-to-E2b-reconcile** (the §2.7.6 fork-class equivalent of clear-with-minor-revisions): findings are all name-this-small-thing, none build machinery, additive-only confirmed. Let me write the deliverable.

---

# Adversarial Review #1 (Round 5 evidence-enrichment) — E2

**Verdict:** **CLEAR-to-E2b-reconcile** — the reconciled E1 plan is proportionality-sound, additive-only, and cite-clean; 3 Class-2 (§4.1) in-arc revisions + 2 Class-1 nits, **0 Class-3**. Every revision is *name-this* (an already-true self-check; a base-rate-blind class; a cite resolved), **not** *build-this* — recommending new machinery to harden an anti-bloat arc would itself be the trap (and the council already refused it correctly).

*(Taxonomy note per SKILL: findings below use the §4.1 review-severity scale. Where a disposition would trigger a §2.7.6 Phase-7 execution fork, it is labeled. None here rises to a §2.7.6 Class-1 halt — this is a plan-revision arc, not execution.)*

## Cite-verification

| Cite (load-bearing) | Resolves? | Note |
|---|---|---|
| ICM = `arXiv:2603.16021v2` (CHARTER + `c2.md:11`) | ✅ **CLEAN** | WebFetch-verified: "Interpretable Context Methodology: Folder Structure as Agentic Architecture," Van Clief & McDermott, v2 2026-03-18, 28pp/cs.AI. Byte-exact to the cite. Removes the A4-fabrication risk. |
| `session-end-cleanup.sh` `## MEMORY.md cap` section | ◑ **resolves, line-range slightly off** | Section is at **`:49`–`:58`** (echo `:49`, over-cap logic `:53-54`). Council/cross-read cite "`:49-53`". The anchor + the rider-home claim hold; the upper bound under-counts by 5 lines. **F1-01.** |
| MEMORY.md over-cap NOW (27,051B > 24,400B) | ✅ **CLEAN** | `wc -c` = 27,051B; matches the live session-reminder. WS-3a "active drift surface" premise true. |
| Memory store NOT git-versioned (X-min / FM-H premise) | ✅ **CLEAN** | `git rev-parse` → "not a git repository." The X-min recoverability premise + the §12.5.1-false-claim premise both hold. |
| "`CLAUDE.md §12.5.1` false git-history claim" (DESIGN §5, integration plan MVP-7) | ✅ **CLEAN** | The claim *"Provenance lives in git history at the global memory store"* is at **`CLAUDE.md:651`, inside §12.5.1** (verified). The §-cite is correct. |
| EVID Finding-4: 3 bucket-C true breaks; ≥4-ref unwritten patterns | ✅ **CLEAN** | EVID `:55` — bucket C = **3** (`test-bypass-as-runtime-truth` ×3 → `…-pattern`, etc.); bucket D ≥4-ref = **2** (`plan-revision…` 5×, `strike-revision…` 4×). Health-line "patterns-unwritten->=4-refs" resolves. |
| EVID "39 zero-inbound" archive candidates | ✅ **CLEAN** | EVID `:28`/`:64` — 39/169 (23%), 14 `pr-` + singleton recipes. |
| Live cross-store drift at HEAD (residual-b premise) | ✅ **CLEAN** | `test-bypass-as-runtime-truth` referenced bare in MEMORY.md while real note is `…-pattern.md`; `plan-revision-against-not-yet-built-substrate` has **no note file** (unwritten). Drift is live. |
| reinject-pointer targets resolve at HEAD (residual-b crux) | ✅ **CLEAN — and already-guarded** | `postcompact-reinject.sh:24` reads `roadmap_status.md` (**exists**, 130KB); `:28` checkpoint pointer is **conditionally guarded** (`[ -f "$CK" ] && …`) — graceful-degrade already present. Decisive for residual (b) below. |

**Cite-verification verdict: CLEAN.** Every load-bearing anchor resolves; one line-range nit (F1-01). No phantom, no fabrication, no wrong-shape §-cite.

## Findings (classified)

### F2-01 — Residual (b) is over-framed: the reinject self-check is *already true at HEAD* — name it, don't gate it
- **Location:** DELIBERATION-2 §"Residuals routed to E2" #2; `crossread-r5/b2-c5-unified-gate.md` residual; DESIGN.md §6 (G-LINK row, absent from v1).
- **Defect:** The residual frames a choice — "dormant-G-LINK + self-check" **vs** "pull a minimal G-LINK to MVP-now." But the self-check the fallback depends on **already exists**: `postcompact-reinject.sh:28` conditionally guards the checkpoint pointer (`[ -f "$CK" ]`), and the roadmap target (`:24`) resolves at HEAD. At bare MVP there is **exactly one** standing machine-managed cross-ref surface (the reinject pointer; generator + machine-emitted-supersede are both deferred). One surface earns one self-check in an existing script, **not** a new code-fence-aware gate workstream.
- **Why it matters:** Pulling G-LINK to MVP-now to cover a single, already-degrading-gracefully pointer is the precise CA-2 bloat trap the arc exists to refuse. The proportionality discipline the council enforced everywhere else should apply here too.
- **Discriminator:** (a) — affects substantive content of the v2 plan (the residual's disposition + a missing-from-v1 deliverable), self-contained to this arc.
- **Disposition (decided):** Resolve residual (b) toward **dormant-G-LINK-is-fine**, and add one *naming* deliverable: DESIGN.md v2 should make the **reinject-pointer self-check an explicit MVP recovery deliverable** (it currently lives only in the cross-read; v1 §6 WS-6-6a credits `postcompact-reinject.sh` as §7.2-conformant but does not name pointer-resolvability as a guaranteed property). Name it; do not build G-LINK for it. *(Not a §2.7.6 fork.)*

### F2-02 — Anti-bloat self-application (residual c): the under-examined surface is WS-0 §3 accreting, not the SessionEnd line
- **Location:** DELIBERATION-2 §"Residuals routed to E2" #3 + Finalized plan MVP-4/MVP-5; DESIGN.md §3.
- **Defect:** Residual (c) asks whether "one more SessionEnd line" re-creates WS-5. That surface is **genuinely guarded** and closes (see rejected-findings R-1): boundary-only, 3 integers, grep-derived, rides an existing report. **But the residual aims at the wrong target.** The real proportionality question (c) should pose is at **WS-0 §3**: C8 stacked **two** sharpens onto the success gate this round (E-4 codebook-lens + E-5 base-rate-honesty rule), and **no voice stepped back** to re-confirm WS-0 is still "one matrix, Robert's eyes, no new tooling" (DESIGN.md §3 verbatim). The cross-read closed the SessionEnd-line surface but never audited the gate-accretion surface.
- **Why it matters:** WS-0 *is the acceptance gate* (§2). Accretion onto the gate is higher-stakes than accretion onto a health line — if WS-0 grows a codebook + a recording-rule + (latent) a coverage-floor pressure (F2-03), it drifts from "human-floor binary tally" toward the eval apparatus C8 itself refused. The arc's self-application duty lands hardest here.
- **Discriminator:** (a) — substantive content of the v2 plan (WS-0 §3 proportionality); self-contained.
- **Disposition (decided):** E2b should have a voice (C8, owner) **explicitly re-affirm in DESIGN.md §3 that the two sharpens are annotations on an unchanged manual step** — the codebook-lens is "3 questions asked while grading," the base-rate rule is "one recording clause," and **WS-0 remains one matrix / Robert's eyes / zero new tooling**. A one-sentence proportionality-preserved assertion in §3 closes (c) at its real surface. *(Not a §2.7.6 fork.)*

### F2-03 — Residual (a) reframed: D6 (instruction-conflict) is base-rate-blind with *no* standing mitigation; name the limitation, don't add a floor
- **Location:** DELIBERATION-2 §"Residuals routed to E2" #1; `c8.md` §E2 + §"Residual seam-questions"; `b1-c7…md` (D4 mitigation); DESIGN.md §3 pass condition.
- **Defect:** C8's base-rate finding (the rare classes pass vacuously, 0≤0) is correct and its "annotate not-exercised ≠ passed" is the proportionate fix — a minimum-exposure floor **is** the bloat answer and should stay refused. But the residual treats D4 and D6 symmetrically, and they are **not** symmetric at HEAD: the b1 cross-read established the **health-line ≥4-ref inventory is a standing, non-vacuous D4 signal** (a second indicator beside the gate's observational column). **D6 (instruction-conflict) has no such standing mitigation** — no health-line count, no inventory, no second signal. D6 alone stays fully base-rate-blind.
- **Why it matters:** Asserting "annotate-is-sufficient" uniformly slightly over-claims for D6. The honest posture is: D4's vacuity is *partially mitigated*; D6's is *not*, and that residual blindness is a known limitation of the observational gate — not a defect to fix with machinery, but a thing the plan must *state* so a future reader doesn't read a vacuous D6 pass as validation.
- **Discriminator:** (a) — substantive content (the WS-0 pass-condition annotation); self-contained.
- **Disposition (decided):** Resolve residual (a) toward **annotate (not floor)**, with one refinement: DESIGN.md §3 should **name D6's residual base-rate blindness as a known WS-0 limitation** (distinct from D4, which the health-line inventory partially covers). Class-3-informational in the §2.7.6 sense if it were ever to surface as an execution gap; here it is a §4.1 Class-2 plan-precision fix. *(Not a §2.7.6 fork; flag as a documented gate limitation.)*

### F1-01 — `session-end-cleanup.sh` line-range cite under-counts
- **Location:** DELIBERATION-2 Finalized plan MVP-3 + `b1-c7…md`:25/33 + `c7.md`:21 — all cite "`session-end-cleanup.sh:49-53`".
- **Defect:** The `## MEMORY.md cap` section runs `:49`–`:58` (the over-cap echo is at `:53-54`, the `else`/fi at `:55-56`). "`:49-53`" truncates the section.
- **Resolution:** Inline cite correction to the actual range (`:49-58`, or simply `:49`) when the rider lands in DESIGN.md v2. Drift-only; semantics unaffected.

### F1-02 — Two distinct count-shapes both labeled "health line" risk a downstream conflation
- **Location:** EVID `:60`/Finding-4 recommends "a single periodic memory-health line (orphan %, density, true-break count)"; the b1 cross-read MVP shape is a **three-integer** line (`notes-superseded`, `notes-untouched`, `patterns-unwritten->=4-refs`) — a **different triple**.
- **Defect:** The EVID-recommended triple (orphan%/density/true-break) and the reconciled MVP triple (superseded/stale/≥4-ref) are *not the same three counts*. A downstream executor reading both could wire the wrong set.
- **Resolution:** When MVP-3 lands in v2, state the canonical three integers explicitly and note they supersede EVID Finding-4's illustrative triple. Drift-only.

## The 4 routed residuals — adjudication

**(a) C8 base-rate floor — "not-exercised ≠ passed" sufficient, or minimum-exposure floor?** → **Council disposition HOLDS (annotate, not floor)**, with the **F2-03 refinement**: the asymmetry between D4 (partially mitigated by the standing ≥4-ref health-line inventory) and **D6 (no standing mitigation, fully base-rate-blind)** must be named. A floor is correctly refused as bloat. No Class-1 gap. → **Class-2 (F2-03): name D6's limitation.**

**(b) Dormant-G-LINK reinject-pointer gap — "dormant + self-check" sufficient, or pull G-LINK to MVP-now?** → **Council disposition HOLDS (dormant-is-fine)**, and is in fact **stronger than the council claimed**: the self-check is *already present at HEAD* (`postcompact-reinject.sh:28` conditional guard) and the roadmap target resolves. The live cross-store drift I confirmed is a *memory-note* break, **not** the reinject pointer. No case for MVP-now-G-LINK. → **Class-2 (F2-01): name the (already-true) self-check as an explicit MVP deliverable; do not gate.**

**(c) Anti-bloat self-application — does the v2 aggregate re-introduce CA-2 bloat?** → **The SessionEnd-line surface is genuinely guarded and CLOSES** (rejected-finding R-1). **But the residual aimed wrong** — the real un-audited surface is **WS-0 §3 gate-accretion** (two sharpens, no step-back). → **Class-2 (F2-02): C8 re-affirms WS-0 stays one-matrix/Robert's-eyes/no-tooling at §3.**

**(d) C7↔C11 sequencing (low-stakes)** — "when WS-5 dashboard lands, does it absorb the counts or does SessionEnd stay their home?" → **Council disposition HOLDS (SessionEnd is permanent MVP home; dashboard adds a render later).** This is correctly low-stakes, correctly deferred, and correctly flagged as C7↔C11-co-primary-iff-the-dashboard-sequences. **No finding** — it is a clean forward-pointer, not an open gap. The b1 cross-read closed it cleanly.

## Missed cross-cutting tensions

The Phase-B cross-read was unusually thorough (2 seam closures + 2 confirm-backs, zero CONFLICT). I hunted the seams between the 8 MVP items and the set-asides for an uncaught dependency. Findings:

- **C7's T3 legibility-lien vs C2's deferred generator — CHECKED, holds.** C7 (`c7.md`:38) filed its T3 lien as "rides on E2 landing **as generated**." C2's confirm-back **defers the generator** and ships the **un-anchored `artifact→version` INDEX** as the MVP floor. I pressure-tested whether eviction (WS-1, MVP) outruns C7's navigation guarantee: it does **not** — C7's lien is about `canonical=vN` *discoverability*, which the un-anchored `artifact→version` map satisfies directly (you can find the canonical version without inline-carry; you just don't get `#section` precision, which is the deferred enhancement). The lien is satisfied by the floor. **Not a missed tension** — but worth one confirming line in E2b that C7 accepts the un-anchored floor discharges its T3 lien (C2's confirm-back asserted this for C7; C7 has not confirmed-back in R5 Phase B). *Low-stakes; folds into F2-02's E2b pass.*
- **D3 (forgotten task-constraint) double-assignment — CHECKED, clean.** C1 (`c1.md`:42/50) routes D3 to "WS-1 positioning half + WS-0 column" as already-covered. No MVP item *builds* a D3 remediation; WS-1's keep/position half (DESIGN §5) is the lever. No silent dependency — the assignment is explicit and consistent across C1 + WS-0.
- **MVP-7 (FM-H store-OCC) ↔ the false §12.5.1 claim — CHECKED, clean.** The execution-arc note to correct `CLAUDE.md:651` is consistently scoped as *execution-arc work, not this-arc* across DESIGN §5 X-min, §9, and C3's confirm-back. No leak into the plan-arc's additive-only boundary.

**Net: no uncaught cross-cutting tension.** The cross-read genuinely closed the seams. (The prior arc's adversarial #1 caught 2 missed tensions because the isolated voices had *not* cross-read; this round they did, and it shows.)

## 9-item pattern checklist

| # | Item | Verdict |
|---|---|---|
| 1 | Stale-carry-text disposition | **PASS** — v2 is a fresh enrichment, not a carried framing; C2/C9 both self-corrected stale prior headlines (cache-as-gate; co-requisite→deferred). |
| 2 | Sibling-spec staleness | **PASS** — IS spec cited at v1.3 consistently across all 7 voices; no version drift. |
| 3 | Forward-looking cite phantom | **PASS** — every cited surface (`session-end-cleanup.sh`, `postcompact-reinject.sh`, `roadmap_status.md`, EVID counts, ICM arXiv) resolves at HEAD. F1-01 is a line-range nit, not a phantom. |
| 4 | Checkpoint-listed-as-open-but-already-applied | **FLAG (→ F2-01)** — residual (b)'s "self-check" is treated as a to-decide when it is *already present* at HEAD. The exact shape this checklist item names. |
| 5 | Plan-revision-against-not-yet-built-substrate | **PASS** — every MVP item targets an existing surface (WS-0/1/2a/3a/4-G1/X-min all in v1); enrichments sharpen, none cite an unbuilt firing-site. (The plan *is* a plan for a future execution arc — that is the arc's declared nature, not this pattern.) |
| 6 | Spec-prose-vs-plan-body drift | **PASS** — n/a; no spec body touched (additive-only, design-substrate untouched). |
| 7 | Verification-shape grep-vs-e2e | **PASS** — WS-0 is explicitly a human-graded counterfactual *probe over real sessions*, not a grep; the L1 deterministic assertion is correctly scoped as the *ex-ante* half with the human probe as the *ex-post* half. Verification shape is sound. |
| 8 | X-AL-3 anti-extension | **PASS** — additive-only, plan-not-execution; no `design-substrate/**`, no `harness-*/src`, no `R-NNN` touched; the one design-substrate-adjacent item (correct §12.5.1) is explicitly deferred to the execution arc under the clearance/`design-phase-direct` hatch (DESIGN §9). Clean. |
| 9 | Halt-route-split-AC | **PASS** — n/a at plan-revision altitude; no ACs bundling materializable+unmaterializable atoms. |

**Checklist: 8 PASS / 1 FLAG (item 4 → F2-01).**

## What E2b (the council) must reconcile

Three Class-2 findings, all *name-this* (no machinery to build):

1. **F2-01 (residual b, C5×C9):** Resolve toward dormant-G-LINK-is-fine; **name the reinject-pointer self-check as an explicit MVP recovery deliverable** in DESIGN.md v2 §6 (it is already true at HEAD via `postcompact-reinject.sh:28`'s conditional guard — name the property, do not build G-LINK).
2. **F2-02 (residual c, C8 owner):** The SessionEnd line closes; the **real surface is WS-0 §3 gate-accretion** — C8 should add one sentence to §3 affirming the codebook-lens (E-4) + base-rate rule (E-5) are annotations on an **unchanged** manual step (one matrix / Robert's eyes / zero new tooling).
3. **F2-03 (residual a, C8 owner):** Hold annotate-not-floor; **name D6's residual base-rate blindness** as a known WS-0 limitation, distinct from D4 (which the health-line ≥4-ref inventory partially mitigates).

Plus 2 Class-1 inline nits to fold when MVP-3 lands (no E2b debate needed): **F1-01** (`session-end-cleanup.sh` cite `:49-53`→`:49-58`), **F1-02** (state the canonical 3 health-line integers; note they supersede EVID Finding-4's illustrative triple).

**One confirming line worth getting** (not a finding): C7 should confirm-back that C2's deferred-generator / un-anchored-INDEX floor discharges C7's T3 legibility-lien (C2 asserted it *for* C7; C7 hasn't confirmed in R5 Phase B).

---

### Findings considered and rejected (transparency)

- **R-1 — "one more SessionEnd line re-creates WS-5" (residual c, literal reading):** REJECTED as a finding. The line is boundary-only, three grep-derived integers, on a report that already runs (`session-end-cleanup.sh:49`), zero continuous-surface affordance — the antithesis of the WS-5 mid-session dashboard. The b1 cross-read's proportionality guard holds. (Surfaced the *real* (c) surface as F2-02 instead.)
- **R-2 — A8 framing contamination (persona/stack/deployment overcommit):** REJECTED. The plan is rigorously solo-developer-scoped, every item filtered against the solo lens; no committed-surface violated, no not-committed value picked. The whole arc *is* the proportionality discipline A8 protects.
- **R-3 — A4 fabricated citation (ICM):** REJECTED after WebFetch — `arXiv:2603.16021v2` resolves byte-exact (title/authors/date confirmed). Was the highest-value A4 target; cleared.
- **R-4 — A5/A7 missing-uncertainty / weak-source escalation:** REJECTED. The contributions tag confidence ([HIGH]/[MODERATE]) and route external-canon vs repo-empirical correctly (C3 explicitly rules "repo-empirical beats external-canon at the drift gate" — the right epistemic posture). C2 tags the generator-lands-MVP question [MODERATE], honestly.
- **R-5 — FM-H domain attack (concurrent-write / lost-update unrecoverable):** REJECTED as a *new* finding — the council surfaced it itself (X-min, the §12.5.1-false-claim, store-OCC), and C1's decentralized-handoff topology-class sharpen (MVP-7) forecloses the tempting wrong-fix. Domain concern present and handled.
- **R-6 — CP-domain enum/topology drift:** N/A — this is a governance-layer plan, not a CP-axis spec; no `TopologyPattern` enum surface under review. (C1's "decentralized-handoff" is a *descriptive* topology-class cite, not a 6-class-enum commitment.)
- **R-7 — External-canon divergence (SKILL §D):** REJECTED. The plan *consumes* canon (CoALA/Letta/ICM/Zep/OCC) as citation-enriching and explicitly refuses the over-adoptions (numbered-folder, episodic/semantic dir-split, consolidation daemon, 3-tier eval cascade, embedding-drift rot-scores) with stated drift+solo rationale. The divergences are *intentional + rationale-backed* (SKILL §D category (a)) — the proportionality refusals ARE the ADR-level rationale. No accidental divergence.
- **R-8 — Reviewing-the-council instead of the artifact (FM-H):** Self-check — every finding above grounds in a file:location (DELIBERATION-2, DESIGN.md §, a contribution, a verified HEAD surface), not in "the council under-weighted X."
- **R-9 — Proportionality-as-soft-over-adoption (the meta-attack, item 6 of mandate):** REJECTED. I tested whether "8 MVP sharpens" is itself a disguised over-adoption. It is not: every MVP item maps to a named WS-0 drift class (E-1→D2, E-3→D1+D4, E-4 hardens the instrument, E-5 protects gate integrity, E-6→D1+D4 observability, E-7→D4, E-8 corrects a measurement claim, MVP-6 L1→verify-before-evict). **Five of the eight are sharpens/riders of existing workstreams; zero new MVP workstreams; the one new mechanism (G-LINK) is DEFERRED.** The de-bloat effort genuinely did not become bloat — the spine verdict ("all 7 voices resolved toward proportionality, each refusing the bloat its own lane was most tempted by") is borne out by the artifact, not just asserted.