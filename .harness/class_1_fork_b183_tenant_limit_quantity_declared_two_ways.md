# Class 1 Fork — `B-183`: the C-OD-11 §11.1 per-tenant limit's QUANTITY is declared two ways, and the "spans/sec" reading originates in an implementation docstring that two cleared spec deltas then quoted forward

**Filed:** 2026-08-16 (`B-183` close-out step (2) — the fork doc the row declared OWED at PR #1378)
**Status:** OPEN — Class 1 (design-phase artifact requires revision)
**Halt target:** any arc that authorises a **production caller** for `assert_per_tenant_cardinality_isolation`, or that "corrects" `per_cell_cardinality_budget.py:58`'s unit comment in place. **Nothing in flight is blocked today** — the helper has no production caller, so this is filed at discovery, not at obstruction, per `CLAUDE.md` §4.3.
**Routing target:** `Spec_Operational_Discipline_v1_37.md` rider (a) and `Spec_Operational_Discipline_v1_38.md` §(the `B-133` step-3 paragraph) — the two **cleared** deltas that state the per-tenant cap in `spans/sec`. Secondary, only under disposition (B): `Spec_Operational_Discipline_v1_2.md` §11.1 + §11.4 and `C-OD-21` §21.4.
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
about the tenant limit in prose, it says **cardinality**. So the conflict is not
three-surfaces-disagree; it is **one label against everything else**, and the label's
provenance is traceable.

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

**Row 9 is a parenthetical that describes the implementation file by name.** It reads as a
*report of what the code contains*, not as an independent contract declaration — and what
the code contains, at rows 7-8, is the docstring. Row 10 then refers back to *"the C-OD-11
§11.1 1,000 spans/sec budget"* as an established term. **[MODERATE confidence]** that the
`spans/sec` unit entered canonical spec text by being quoted forward from the
implementation's own comment rather than by an independent ruling. *Falsifier:* any
pre-v1.37 surface, or ADR-D6 §1.3's resident body (see §2.4), stating the per-tenant cap in
spans/sec independently of `per_cell_cardinality_budget.py`. **This fork does not claim the
provenance is proven** — it claims the disposition should not rest on rows 9-10 without
checking it.

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
framing and §11.1's "rate limits" parenthetical both stand**, and it is why this fork does
**not** route §11.1 unless disposition (B) is chosen.

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

**(A) — CARDINALITY (distinct attribute-value series). RECOMMENDED.**
Declare the per-tenant cap a bound on distinct attribute-value series. Amend v1.37 rider (a)
and v1.38's phrase by delta to drop `spans/sec` **for the tenant cap**; correct
`per_cell_cardinality_budget.py:49-50,58`. **No code behaviour changes** — the comparison
already implements this. *Supported by:* rows 1-6, including the plan's own AC for this
function and the counter's declared shape; the code is already conformant. *Costs:* a spec
delta amending two cleared deltas' prose.

**(B) — SPANS/SEC.** Declare the cap a rate on admitted spans. Requires: a new counter
carrying a span count (or re-purposing `observed_series`, contradicting plan v2_6:721), a
reader for `observation_window`, an amendment to plan AC `:2186` and to `observed_series`'s
declared shape, and a re-reading of §11's cardinality framing and `C-OD-21` §21.4's row
title. *Supported by:* rows 7-10. *Costs:* amends the execution authority and the contract
surface, and makes the shipped comparison wrong.

**(C) — BOTH, as two fields.** Keep `tenant_rate_limit` as a cardinality bound and note that
`cell_rate_limit` is genuinely a span rate (its plan comment at `:978` says so, and nothing
contradicts it). The record then legitimately carries two different quantities, and only the
**names** mislead — a rename (`tenant_series_budget`) would be the honest repair.
*Consideration:* this is (A) plus a naming decision, and it is the reading that best fits
every surface at once. It is listed separately because the rename touches a frozen
`PerCellCardinalityBudget` field name and therefore needs the same ratification.

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
design** (disposition (C)). What they actually share is only that v1.37 rider (a) describes
both in one parenthetical. `B-182`'s open question — whether a declared cap with no consumer
is correct-by-design external enforcement or a gap — is **largely independent** of the
quantity decision here. The `B-182` row's close-out step (4) (*"Settle `B-183`'s quantity
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
| The `spans/sec` label plausibly originates in the code docstring | A pre-v1.37 surface stating it independently of `per_cell_cardinality_budget.py` |
| Nothing is blocked today | A production caller for `assert_per_tenant_cardinality_isolation` appearing in `harness-*/src` |

---

## §8 — Confidence tags

| Claim | Confidence |
|---|---|
| The plan's `spans/sec` comment is on `cell_rate_limit`, not `tenant_rate_limit` | **HIGH** — read at `:977-978` this session |
| The plan's AC `:2186` and counter shape v2_6`:721` both declare cardinality, and the code conforms | **HIGH** — all three read this session |
| v1.37/v1.38 state the tenant cap in `spans/sec` in cleared spec text | **HIGH** — quoted byte-exact |
| §11.1's "rate limits" parenthetical names a mechanism, not a quantity | **MODERATE** — a coherent reading of `:623` + `:1207` + §11.4, not an explicit statement anywhere |
| The `spans/sec` unit was quoted forward from the implementation docstring | **MODERATE** — provenance-shaped inference from v1.37's parenthetical form; explicitly not proven |
| ADR-D6 §1.3's body is absent from this workspace | **HIGH** — `ADR-D6_v1_2.md` is the only D6 file; `:227-229` is a bracket placeholder |
| Disposition (A) is the lowest-cost reconciliation | **MODERATE** — follows from the evidence balance, but the non-resident ADR §1.3 could overturn it |

---

## §9 — Open questions and recommended next probes

1. **Read ADR-D6 v1.1 §1.3 in the design-phase workspace.** It is the cited root authority
   and is not resident here. It may settle decision 1 outright, and it is the cheapest probe.
2. **Establish the provenance of `spans/sec`.** Search the pre-v1.37 OD chain and the D6
   corpus for any independent statement of a per-tenant span rate. If none exists, (A)
   becomes near-mechanical.
3. **Decide the temporal dimension (§5) in the same pass**, and say explicitly what
   `observation_window` is for under the chosen reading.
4. **Decide whether `cell_rate_limit` is in scope.** This fork's position is that it is not
   (§6(ii)) — but the operator may prefer to settle both fields' quantities in one delta,
   since v1.37 rider (a) describes them in one sentence and a delta will touch that sentence
   either way.
5. **Council:** not obviously owed. Under (A) this is single-domain (C7/OD) unit-and-contract
   coherence with a clear evidence balance. If disposition (B) is seriously entertained — it
   would make the shipped comparison wrong at a compliance surface — that is a C7 ⊥ C10
   tension worth a dyadic convening.

---

**Filed under** `CLAUDE.md` §4.3 Class 1 routing; `Project_Workflow_v1_8.md` §2.7.6.
**Cross-ref:** `B-183` (this row), `B-182` (the sibling, decoupled at §6(ii)), `B-137`
(the row `B-182` grounds), `B-133` (whose F-08 rider produced v1.37's paragraph).
