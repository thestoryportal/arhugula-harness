# Class 1 Fork — `B-183`: the C-OD-11 §11.1 per-tenant limit's QUANTITY is declared two ways — the cleared SPEC reasons with it as a span rate, while the PLAN and the shipped code implement a distinct-series cardinality bound

**Filed:** 2026-08-16 (`B-183` close-out step (2) — the fork doc the row declared OWED at PR #1378)
**Status:** OPEN — Class 1 (design-phase artifact requires revision)
**Halt target:** **every consumer and every MEASUREMENT of `tenant_rate_limit`**, not only code callers (broadened at out-of-family review round 2 [P2]) — (a) any arc authorising a **production caller** for `assert_per_tenant_cardinality_isolation`; (b) any arc "correcting" `per_cell_cardinality_budget.py:49-50,58`'s unit comment in place; (c) **`B-133` close-out step (3) / `B-137`'s F-08 per-tenant keep-volume measurement**, which compares a keep-volume against this very cap and would therefore **silently assume disposition (B)** before ratification; and (d) any external collector or backend enforcement configured against this cap, which bypasses the helper entirely. **Nothing in flight is blocked today** — the helper has no production caller and the F-08 measurement is unperformed — so this is filed at discovery, not at obstruction, per `CLAUDE.md` §4.3.
**Routing target — under EVERY disposition** (corrected at review round 2 [P2]; an earlier line made the contract route conditional on (B) and omitted the plan entirely): **(1) `C-OD-11` §11.1 + §11.4** and **`C-OD-21` §21.4** — the canonical contract must state the quantity explicitly and must define what `observation_window` means, since the **temporal decision (§5) is owed under (A) just as much as under (B)** and the contract is silent on it today. **(2) The OD plan** — the `PerCellCardinalityBudget` signature (`v2:977-978`), U-OD-31's AC 5 (`v2:2186`) and the `CardinalityCounters` shape (`v2_6:721`); under (B) these need substantive amendment, under (A) at minimum the window's role. **(3) `Spec_Operational_Discipline_v1_37.md` rider (a) + `v1_38.md:69`** — the two cleared deltas whose prose reasons in `spans/sec`, and which carry the still-open keep-volume question that (A) would invalidate.
**Detection mode:** corpus grounding at HEAD `fcddd96f`, every quote re-read this session. Witness at `harness-od/tests/test_b183_tenant_limit_quantity_conflict.py` (7 tests, landed #1378) — **and that module's own framing is corrected by this fork; see §6.**

---

## §1 — What the register row asked, and what grounding answered

`B-183`'s close-out step (2), rewritten at #1378, said the quantity is **not** choosable at
Phase 7 and must go to a fork doc: *"`C-OD-11` frames the contract as CARDINALITY while the
OD plan's field signature and spec deltas v1.37/v1.38 quantify the same limit in spans/sec,
and the code compares series."*

**Grounding the plan line-by-line falsifies one third of that sentence, and the correction
changes the disposition.** The OD plan's field-signature comment that says `spans/sec` is
attached to **`cell_rate_limit`**, not to `tenant_rate_limit`:

```
  tenant_rate_limit    : Option<float>             // None at non-multi-tenant cells; Some at multi-tenant
  cell_rate_limit      : float                     // per-cell global rate limit (spans/sec)
```
— `Implementation_Plan_Operational_Discipline_v2.md:977-978`

The tenant field carries **no unit at all** in the signature. And everywhere the plan speaks
about the tenant limit in prose, it says **cardinality** — including the acceptance criterion
for this exact function.

**But the correction runs both ways.** This fork's first draft concluded the conflict was
*"one label against everything else"* and recommended the cardinality reading. That was too
quick: v1.37 does not merely *mention* `spans/sec`, it **reasons with the cap as a bound on
admitted span throughput** and leaves an **open measurement question** phrased in those units
(§2.2).

**And the correction to THAT was too quick as well — this fork has now swung twice, and the
stable framing is neither.** A second draft ranked the spec passage over the plan via the
`CLAUDE.md` §1.3 authority chain. **Review round 2 [P2] falsified it, correctly:** §1.3 orders
*artifact levels* (ADR → ADD → PRD → spec → plan), not passages **within one artifact**, and
both readings live inside the **same OD spec lineage**. Worse for that argument, v1.37 is
delta-only and declares it carries *"exactly ONE amendment — the C-OD-09 §9.2 always-sampled
exception set gains ONE row"* (`v1_37:3-8`), and it lists **`C-OD-11` §11.1 as UNCHANGED**
(`:106`) — as does v1.39 (`:47-58`). A change-note rider that **explicitly disclaims amending
`C-OD-11`** cannot be `C-OD-11`'s override.

> **The stable shape: an INTERNAL CONTRADICTION inside the OD spec lineage.** `C-OD-11`'s
> canonical **contract body** frames the cap as cardinality, and the plan and shipped code
> implement exactly that. Two later deltas' **change-note prose** reasons about the same cap in
> `spans/sec` while each declaring `C-OD-11` unchanged. Nothing in the authority chain ranks
> one over the other; resolution needs **ADR-D6 §1.3** (§2.4 — not resident here) or a **new OD
> amendment** that reconciles the rider prose with the contract body.

**This fork makes no recommendation between the dispositions, and the two statements below are
deliberately kept apart** (a draft ran them together and review round 4 [P2] flagged the
contradiction — if precedence were normative here, (A) would already have won and the menu
would not be neutral):

- **No CODIFIED rule ranks them.** `CLAUDE.md` §1.3 orders artifact levels only, and this
  workspace codifies no precedence *within* an artifact. So nothing in governance decides it.
- **There is an EVIDENTIARY argument, not a ruling.** A contract body is the surface a reader
  is meant to treat as the contract, and a change-note rider that explicitly disclaims amending
  that contract is weaker evidence of intent. That is a real point for (A) — but it is a
  *reading*, and this filing does not elevate it to a rule.

Against it, (A) genuinely invalidates a still-open, cleared measurement question (§4). **That
balance is the operator's to strike, which is precisely why this is routed.**

---

## §2 — The evidence, per surface

### §2.1 What declares the tenant quantity as CARDINALITY (distinct attribute-value series)

| # | Surface | Quote |
|---|---|---|
| 1 | `Spec_Operational_Discipline_v1_2.md:605` — §11 heading | *"§11 C-OD-11 — **Cardinality** budget per cell + cardinality-safe-attribute discipline"* |
| 2 | ibid., §11 contract surface | *"Per-cell **cardinality** budget + cardinality-safe-attribute enumeration for metric dimensions."* |
| 3 | ibid.`:1207` — `C-OD-21` §21.4 row | *"**Per-tenant cardinality isolation**"* |
| 4 | `Implementation_Plan_Operational_Discipline_v2.md:991` | *"`tenant_rate_limit` is `Some` at cell-7 and cell-8 (multi-tenant cells per C-OD-21 §21.4 per-tenant **cardinality** isolation)"* |
| 5 | ibid.`:2186` — **the acceptance criterion for the very function in question** | *"`assert_per_tenant_cardinality_isolation` returns `Err(PerTenantCardinalityViolation)` when **per-tenant cardinality** exceeds `tenant_rate_limit` from U-OD-13."* |
| 6 | `Implementation_Plan_Operational_Discipline_v2_6.md:721` — the counter's declared shape | *"`observed_series : int // observed distinct attribute-value series…`"* |

Rows 5 and 6 are the load-bearing pair: the **execution authority** declares that this
function checks *cardinality*, and declares the quantity it checks as *distinct
attribute-value series*. **The shipped code conforms to both** —
`multi_tenant_cross_cutting_enforcement.py:177-178` carries the plan's comment verbatim
(*"observed distinct attribute-value series for this tenant"*) and `:266` compares that
count. The implementation is **not** deviating from its plan here.

### §2.2 What declares it as a SPANS-PER-SECOND RATE

| # | Surface | Quote | Kind |
|---|---|---|---|
| 7 | `per_cell_cardinality_budget.py:58` | *"per-tenant rate limit (spans/sec) — `None` at non-multi-tenant cells."* | **implementation docstring** |
| 8 | ibid.`:49-50` | *"`tenant_rate_limit` is `None` at non-multi-tenant cells and a `float` (per-tenant **spans/sec**)…"* | **implementation docstring** |
| 9 | `Spec_Operational_Discipline_v1_37.md` rider (a) | *"(`per_cell_cardinality_budget.py`: `cell_rate_limit=10_000.0` spans/sec at every ACTIVE cell; `tenant_rate_limit=1_000.0` spans/sec at the two multi-tenant cells)"* | **cleared spec text** |
| 10 | `Spec_Operational_Discipline_v1_38.md:69` | *"the C-OD-11 §11.1 1,000 spans/sec budget"* | **cleared spec text** |

**Rows 9-10 are INDEPENDENT NORMATIVE USE, not a report of the docstring. An earlier draft
of this fork said otherwise and is corrected here (out-of-family review [P1]).** Row 9's
parenthetical does cite the implementation file by name, and read alone it looks descriptive.
But the sentence it sits in is a **structural-compatibility ruling** that reasons *with* the
cap as a bound on admitted spans: the budget *"enforces at the COLLECTOR_BOUNDARY /
BACKEND_INGESTION layer independently of any sampling decision — sampling governs which spans
are KEPT within the admitted stream, not the admitted rate — so §9.2 membership **cannot admit
throughput past the enforced caps**."* And v1.37 immediately continues (`:40`):

> *"**The POPULATION question — the actual multi-tenant chain-exhaustion volume, and whether
> the realized keep-volume approaches the per-tenant 1,000 spans/sec budget — remains
> explicitly OPEN**"*

That is the cleared spec posing a **still-open measurement question** that compares a
**keep-volume** — spans kept per unit time — against the per-tenant cap. It is carried
forward as `B-133`'s close-out step (3), and v1.38`:69` re-states it as *"the C7 F-08
per-tenant keep-volume measurement against the C-OD-11 §11.1 1,000 spans/sec budget."*
**A distinct-series cardinality bound would make that open question malformed.** So the
span-rate reading is load-bearing for a ruling and an owed measurement in cleared spec text,
not an inherited label.

**This is what makes the fork real rather than a docstring tidy.** It does **not**, however,
make `spans/sec` the higher-authority reading — a second draft of this fork argued that via
the `CLAUDE.md` §1.3 chain and **review round 2 [P2] falsified it** (§1): §1.3 orders artifact
*levels*, not passages within one artifact, and v1.37 explicitly declares `C-OD-11` §11.1
**UNCHANGED** (`:106`, echoed at v1.39`:47-58`) while carrying *"exactly ONE amendment"* to
`C-OD-09` (`:3-8`). What rows 9-10 establish is narrower and still decisive: the span-rate
reading is **load-bearing for a cleared ruling and an owed measurement**, so it cannot be
dismissed as an inherited label. The evidence is genuinely two-sided — **a contract body
(cardinality, implemented) against change-note prose that reasons in spans/sec and leaves an
open question in those units** — and §1.3 does not break the tie.

### §2.3 A third naming that is a MECHANISM, not a quantity

§11.1's own multi-tenant row declares both words in **one sentence**:

> `| multi-tenant-compliance × * | Per-cell cardinality budget + per-tenant cardinality isolation (per-tenant rate limits at OTLP collector boundary or at backend ingestion per C-OD-21) |`
> — `Spec_Operational_Discipline_v1_2.md:623`

and §11.4's deferral clause says *"specific per-tenant **rate-limit** implementation at
multi-tenant-compliance cells (composes at Phase 6+)"*, while `C-OD-21` §21.4's body
(`:1207`) repeats *"per-tenant **rate limits** at OTLP collector boundary or at backend
ingestion"*.

**Read carefully, these name the enforcement MECHANISM — collector-boundary rate limiting —
and the PROPERTY it protects — cardinality isolation.** A collector rate-limits a stream in
order to bound cardinality downstream. So §11.1 is not self-contradictory; it is a property
plus the mechanism that delivers it. **This is the reading that lets §11's cardinality
framing and §11.1's "rate limits" parenthetical both stand** without either being a defect.

**It does NOT mean §11.1 escapes routing** — an earlier line here said the fork routes §11.1
only under (B), which contradicted the header's routing target and is corrected (review round
3 [P2]). §11.1 is routed under **every** disposition: whichever quantity is chosen, the
canonical contract has to **say so explicitly** rather than leave the reader to infer it from a
mechanism parenthetical, and §11.1/§11.4 are also where `observation_window`'s meaning must
land for decision 2 (§5). What this section establishes is only that §11.1 is not *itself*
self-contradictory — not that it is already sufficient.

### §2.4 The root ADR paragraph is NOT RESIDENT in this workspace

`C-OD-11` cites its authority as *"ADR-D6 v1.1 §1.3 cardinality budget per cell paragraph"*.
`ADR-D6_v1_2.md:227-229` carries **a placeholder, not the text**:

> `### 1.3 Sampling discipline`
> `[Preserved verbatim from v1.1 §1.3 — head-based-dev / tail-based-prod with always-sampled list + base-rate-sampled list + tail-keep-on-classification list.]`

`ADR-D6_v1_2.md` is the only D6 file in `design-substrate/`, and no file in the workspace
carries a D6 §1.3 body. **The decision therefore cannot be closed by appeal to the root ADR
from inside this workspace** — the design-phase workspace holds that paragraph. Whoever
dispositions this fork should read it there first; it may settle the question outright.
*(Aside, non-blocking: the v1.1 → v1.2 change-note at `:33` lists §1.3 as containing a
"cardinality budget per cell" paragraph, which the §1.3 stub's own bracket summary omits.)*

---

## §3 — Why this is Class 1 and not a Phase-7 absorption

The Phase-7-shaped repair is one line: change `per_cell_cardinality_budget.py:58` to say
*cardinality*, and the code, the plan AC, the counter's declared shape and §11's framing all
agree. **Taking it unilaterally is exactly the X-AL-3 violation the guard exists for**, for
two reasons:

1. It would put the implementation in direct contradiction with **two cleared spec deltas**
   (rows 9-10). A Phase-7 edit cannot amend cleared spec text; leaving the contradiction in
   place is silent absorption of a design-phase defect — `CLAUDE.md` §4.3's worst failure mode.
2. Declaring *which quantity a compliance cap governs* is a contract statement. §11.1's row
   sits on `C-OD-21` §21.4 per-tenant cardinality isolation at the two multi-tenant cells —
   a **compliance** surface. The unit is not a docstring detail there.

**An earlier pass of this same arc made the mirror-image error** in the other direction: it
read only §11's cardinality framing, concluded the `spans/sec` docstrings were stray, and was
about to correct them — before finding rows 9-10. Both errors have the same shape: acting on
a partial read of the corpus. That is why this is routed rather than repaired.

---

## §4 — Dispositions (decision 1 of 2: the QUANTITY)

**No disposition is recommended.** The first draft of this fork recommended (A); out-of-family
review [P1] showed that rested on downgrading v1.37/v1.38 to descriptive text, which §2.2
withdraws. Each option below carries a real, named cost, and choosing between them is the
operator's call.

**(A) — CARDINALITY (distinct attribute-value series).**
Declare the per-tenant cap a bound on distinct attribute-value series. **No code behaviour
changes** — the comparison already implements this. *Supported by:* rows 1-6, including the
plan's own AC for this function and the counter's declared shape. *Costs:* amends **two
cleared spec deltas**' prose; and it **invalidates v1.37's
still-open POPULATION question and `B-133`'s owed close-out step (3)**, which are both phrased
as a keep-volume-in-spans/sec comparison. Those would have to be re-expressed, not merely
re-worded — you cannot measure a span keep-volume against a series budget. **That
consequence, not the docstring, is (A)'s real price.**

**(B) — SPANS/SEC.** Declare the cap a rate on admitted spans. *Supported by:* rows 7-10. It also **preserves v1.37's
open population question and `B-133` step (3) as posed** — the one thing (A) breaks. *(Not
supported by the §1.3 authority chain; that argument appeared in a draft and was falsified at
review round 2 — see §1.)* *Requires:* a new counter carrying a
span count (or re-purposing `observed_series`, contradicting plan v2_6`:721`), a reader for
`observation_window`, amendments to plan AC `:2186` and to `observed_series`'s declared shape,
and a re-reading of §11's cardinality framing and `C-OD-21` §21.4's row title. *Costs:* amends
the execution authority, and makes the shipped comparison **wrong at a compliance surface** —
which is real work, not a relabel.

**(C) — BOTH, as two fields.** Keep `tenant_rate_limit` as a cardinality bound and note that
`cell_rate_limit` is genuinely a span rate (its plan comment at `:978` says so, and nothing
contradicts it). The record then legitimately carries two different quantities, and only the
**names** mislead — a rename (`tenant_series_budget`) would be the honest repair. *Note:* (C)
is (A) plus a rename, so it **inherits (A)'s cost** — v1.37's population question still has to
be re-expressed, and v1.37 treats *both* caps in one throughput argument. The rename also
touches a frozen `PerCellCardinalityBudget` field name and needs the same ratification.

**Not a disposition: leaving it.** The row is `design_substrate_gated`; a future caller
inherits whichever semantics are documented, and the two labels currently disagree.

---

## §5 — Decision 2 of 2: the TEMPORAL interpretation. It does NOT follow from decision 1.

`CardinalityCounters` carries an `observation_window` that the comparison never reads — the
field name appears exactly once in that module, at its own declaration. **Settling the
quantity does not settle this**, because even under (A) the cap could mean:

- **standing / concurrent** distinct-series cardinality (window irrelevant → the field is
  vestigial and should be removed, or typed as advisory metadata);
- **distinct series per window** (window load-bearing → the comparison must read it, and
  1,000 over `"1m"` must not equal 1,000 over `"1s"`);
- a **cardinality rate** (new-series-per-second → needs both fields and a division).

The field's presence, and the `_rate_limit` suffix, are evidence *for* the second or third.
Nothing observed this session decides among them. §11.4 defers *"specific cardinality-budget
numeric thresholds per cell"* to implementation discretion, but that defers the **threshold**,
not the **dimension**. **This decision is owed in the same pass as decision 1**; a resolving
delta that settles quantity alone leaves `B-183` open.

---

## §6 — Two corrections this fork makes to already-merged artifacts

**(i) `B-183`'s register row overstates the plan's role, and this fork supersedes it.** The
row says *"the OD plan's own field signature says SPANS/SEC"* for the tenant limit. It does
not — that comment is on `cell_rate_limit` (`:978`), and the plan's tenant-side prose says
cardinality at `:991` and `:2186`. The register text is corrected in the same PR as this
filing.

**(ii) `B-183` does NOT govern `B-182`'s half, and the merged claim that it does is
withdrawn.** #1378's register text and refresh PR body both say *"one decision governs both
halves, since `cell_rate_limit` carries the same spans/sec documentation."* Grounding shows
the opposite: `cell_rate_limit`'s plan comment (`:978`) declares it a **span rate**, and
nothing contradicts that — so the two fields plausibly carry **different quantities by
design** (disposition (C)). What they actually share is only that v1.37 rider (a) treats
both caps inside one admitted-throughput argument. `B-182`'s open question — whether a declared
cap with no consumer is correct-by-design external enforcement or a gap — is **largely
independent** of the quantity decision here. **The decoupling is disposition-dependent:** under
(B) the tenant cap becomes a span rate too and the two fields re-unify, so a delta settling
(B) should say explicitly whether it governs `cell_rate_limit` as well. The `B-182` row's close-out step (4) (*"Settle `B-183`'s quantity
question first if any consumer is authorised"*) still holds in the narrow form it states, and
only in that form.

**(iii) The #1378 witness module's framing needs the same correction, and it cannot ride this
PR.** `test_the_plan_signature_declares_spans_per_second` reads `:978` — the **cell** limit —
inside a module about the **tenant** limit. Its assertion is factually true and stays green,
but its stated relevance is wrong. Fork docs match the codex guard's `DESIGN_RE`, so a
doc-only filing cannot carry a test edit; **the correction is owed as an impl-only follow-up
PR** and is recorded on the `B-183` row.

---

## §7 — What would falsify this fork

| Claim | Falsifier |
|---|---|
| The plan attaches no unit to `tenant_rate_limit` | A unit comment appearing on plan `:977`, or any plan surface quantifying the tenant cap |
| The plan's AC for this function says cardinality | `:2186` changing wording |
| `observed_series` is declared as distinct series | plan v2_6`:721` changing, or the code comment at `:177` diverging from it |
| Only v1.37/v1.38 assert tenant = spans/sec in spec text | Any other OD delta, or a resident ADR-D6 §1.3, stating it |
| v1.37/v1.38 use the cap as a span rate independently (not merely quoting the docstring) | v1.37`:38-40` or v1.38`:69` being re-worded so the population/keep-volume question no longer compares spans against the cap |
| Nothing is blocked today | **Any** halt-target condition materialising (review round 3 [P2] — this row previously named only the first): a production caller for `assert_per_tenant_cardinality_isolation` in `harness-*/src`; **`B-133` step (3) / `B-137`'s F-08 keep-volume measurement starting**; or an external collector/backend being configured to enforce this cap |

---

## §8 — Confidence tags

| Claim | Confidence |
|---|---|
| The plan's `spans/sec` comment is on `cell_rate_limit`, not `tenant_rate_limit` | **HIGH** — read at `:977-978` this session |
| The plan's AC `:2186` and counter shape v2_6`:721` both declare cardinality, and the code conforms | **HIGH** — all three read this session |
| v1.37/v1.38 state the tenant cap in `spans/sec` in cleared spec text | **HIGH** — quoted byte-exact |
| §11.1's "rate limits" parenthetical names a mechanism, not a quantity | **MODERATE** — a coherent reading of `:623` + `:1207` + §11.4, not an explicit statement anywhere |
| v1.37/v1.38 constitute independent normative use of the span-rate reading | **HIGH** — v1.37`:40` poses an OPEN keep-volume-vs-budget question in spans/sec, re-stated at v1.38`:69`; both re-read this session. *(This fork's first draft rated the opposite claim MODERATE and was wrong — corrected at review [P1].)* |
| ADR-D6 §1.3's body is absent from this workspace | **HIGH** — `ADR-D6_v1_2.md` is the only D6 file; `:227-229` is a bracket placeholder |
| No disposition is recommended | By design — the contradiction is INTERNAL to the OD spec lineage (contract body vs change-note rider), so §1.3 does not break the tie; each option's cost is named at §4 instead |
| §1.3 does NOT rank v1.37's rider over `C-OD-11` | **HIGH** — v1.37`:3-8` declares one amendment (C-OD-09) and `:106` lists C-OD-11 §11.1 UNCHANGED; v1.39`:47-58` repeats it. *(Two drafts of this fork got this wrong in opposite directions; corrected at review round 2 [P2].)* |

---

## §9 — Open questions and recommended next probes

1. **Read ADR-D6 v1.1 §1.3 in the design-phase workspace.** It is the cited root authority
   and is not resident here. It may settle decision 1 outright, and it is the cheapest probe.
2. **Decide what happens to v1.37's open POPULATION question under (A).** It and `B-133`'s
   close-out step (3) are phrased as a keep-volume-in-spans/sec comparison against this cap;
   under (A) they are malformed and must be re-expressed, not re-worded. This is the concrete
   cost that decides between (A) and (B), and it is the second-cheapest probe after (1).
3. **Decide the temporal dimension (§5) in the same pass**, and say explicitly what
   `observation_window` is for under the chosen reading.
4. **Decide whether `cell_rate_limit` is in scope.** This fork's position is that it is not
   (§6(ii)) — but the operator may prefer to settle both fields' quantities in one delta,
   since v1.37 rider (a) describes them in one sentence and a delta will touch that sentence
   either way.
5. **Council: likely owed, and the first draft of this fork said otherwise.** With the
   evidence two-sided — a contract body against change-note prose, with no authority rule to
   break the tie — this is no longer single-domain coherence: it sets what a **compliance** cap
   measures at the two multi-tenant cells (C10) against what the observability substrate can
   actually count and afford (C7). **A dyadic C7 ⊥ C10 convening is the recommended shape**,
   with probes (1) and (2) run first so it deliberates on evidence rather than on readings.

---

**Filed under** `CLAUDE.md` §4.3 Class 1 routing; `Project_Workflow_v1_8.md` §2.7.6.
**Cross-ref:** `B-183` (this row), `B-182` (the sibling, decoupled at §6(ii)), `B-137`
(the row `B-182` grounds), `B-133` (whose F-08 rider produced v1.37's paragraph).
