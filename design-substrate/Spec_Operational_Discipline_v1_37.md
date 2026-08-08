# Spec: Operational Discipline — v1.37 (delta over v1.36)

*Delta-only file. The v1.36 body + the entire C-OD-01 … C-OD-34 contract body are PRESERVED VERBATIM (delta-only-spec-file convention). This delta carries exactly ONE amendment — the **C-OD-09 §9.2 always-sampled exception set gains ONE row, 18 → 19**, closing the CP §3.5 ↔ OD §9.2 `fallback.exhausted` sampling-disposition gap that `Spec_Harness_Runtime_v1.md` v1.112 §14.6.3 term **t3′** registered as the NAMED closure gate **`B-116-t3`**. §9.1 and §9.3 are UNTOUCHED; §9.2's other **eighteen** rows are PRESERVED VERBATIM and are cross-referenced here, never restated.*

**Filed:** 2026-08-08
**Authoring authority:** `Spec_Harness_Runtime_v1.md` v1.112 §14.6.3 term **t3′** (*"The CP §3.5 ↔ OD §9.2 `fallback.exhausted` observability-floor gap is hereby **REGISTERED as a named gate**: the full floor guarantee is the separate **`B-116-t3` leg** (OD §9.2 roster 18 → 19 plus its sampling fixtures, priced at the council record `C-c7-reconcile.md`). **`B-116` RATIFIES at this delta but CLOSES only when BOTH the impl leg and the t3 leg land.**"*), which rides the operator ratification of **Reading (II)** 2026-08-07 over the council-unanimous package at `.harness/council/b116-breaker-semantics/`. Applied per workspace `CLAUDE.md` §4.3 back-flow + §4.5 clearance discipline.
**Predecessor:** `Spec_Operational_Discipline_v1_36.md` (v1.36 — the `B-69` arc's OD leg, NEW §C-OD-30.5; cleared 2026-07-30)
**Revision shape:** Delta-only spec file per the OD delta-only convention. v1.36 + all earlier file bodies PRESERVED VERBATIM. v1.37 carries this change-note + exactly ONE amendment: **§C-OD-09 §9.2 gains row 19.** **ZERO new contract numbers** (C-OD-09 already exists — this amends its own table, at the venue where the set is defined); **ZERO new namespace** (C-OD-05 §5.1 roster UNCHANGED at 15); **ZERO new attribute**; **ZERO emission-site change**; **ZERO CP delta**; **ZERO CXA rows** (aggregate frozen at 111); **ZERO hash impact**.

---

## Change-note (v1.36 → v1.37)

### What is wrong today, stated as a fact rather than a characterization

`[HIGH]` `fallback.exhausted` is declared **always-sampled** by the Control Plane at `Spec_Control_Plane_v1_2.md:410` — byte-exact: *"| `fallback.exhausted` | **Always-sampled (head=1.0)** — chain exhaustion is reliability-critical |"*. It is classified in **NEITHER OD sampling regime**: it is not among §9.2's eighteen always-sampled rows (`Spec_Operational_Discipline_v1_2.md:515-532`, re-read directly at this filing), and it is not among C-OD-10 §10.1's thirteen base-rate rows (the shipped substrate `BASE_RATE_SAMPLED_EVENT_CLASSES` carries no `fallback.*` member). **OD therefore carries no sampling disposition for the event at all.**

This is a **spec-vs-spec ingestion gap, not code drift.** The shipped `ALWAYS_SAMPLED_EVENT_CLASSES` was byte-exact conformant to its owning contract before this delta; the substrate did not diverge from OD, OD diverged from CP. Naming this precisely matters, because a "correction of a drift" framing would price the leg as conformance work owing no spec amendment — and there is no amount of conformance work that can put a row into a table the table does not have.

### Why the repair is OD 18 → 19 rather than a CP demotion — three grounds, none of them preference

Applied from the council reconcile record `.harness/council/b116-breaker-semantics/01-council/contributions/C-c7-reconcile.md` §F-03(ii), and re-grounded by direct read at this filing:

1. **Authority — CP declares, OD ingests.** `Spec_Control_Plane_v1_2.md:397` states it plainly: *"Three namespaces declared at this contract are ingested by D6 §1.2 at session 4 (Operational Discipline spec)."* §9.2's own **Source declaration** column already cites `C-CP-03 §3.5` for `fallback.triggered` (OD `:521`) and for `breaker.tripped` (OD `:522`) — **the two siblings of `fallback.exhausted` in the very same CP table, at CP `:409` and CP `:411`.** The third row, at CP `:410`, was dropped in ingestion. Demoting CP would invert the declaring contract in order to repair the ingesting one's omission.
2. **The demote direction is not cheaper.** Because OD classifies the event in neither regime, "demote to base-rate" is not an edit-one-line move: it would require amending CP `:410` **and** adding a §10.1 row (13 → 14) to give the event a regime at all. **Two tables either way — and only one direction preserves the authority chain.**
3. **Merits, with the counter-argument stated rather than suppressed.** CP `:409` gives `fallback.triggered` `tail-keep-on-classification=true`, so at tail-based production surfaces an exhausted event would ride its trigger's preserved failure-tree — a real mitigation, and if it holds, this amendment is belt-and-braces at those surfaces. But that mitigation is **unverified in both directions** and is registered as forward row **`B-123`** (the tail-keep trigger matches a span **name** while the breaker emits a span **event**, so the trigger may be inert). `head=1.0` is the guarantee that does not depend on a trigger that may be inert, and it is the only one that binds at **head-based** local-development as well. The row is not dead-lettered: `fallback.exhausted` has a live emission site at `harness-runtime/src/harness_runtime/lifecycle/retry_breaker_fallback.py:947`.

### §9.3's "inviolable" governs OPERATOR TUNABILITY, not contract revision — so this amendment breaches nothing

`[HIGH]` §9.3's first invariant reads *"The set in §9.2 is a hard floor at the deployment-binding layer; not operator-tunable at base-rate"* (`Spec_Operational_Discipline_v1_2.md:538`). It binds the **deployment-binding layer** against an operator turning a member down. It does not freeze the table against amendment **at the contract venue where the set is defined**, and reading it that way would make C-OD-09 the one contract in this corpus that cannot be corrected. This delta is that venue. *(The word was priced as amendment-cost by two voices during the deliberation; the C7 reconcile ruling at F-03 corrected it, and the correction is adopted here.)*

What "inviolable" **does** establish is why **membership** is the only durable repair: a member cannot be tuned down. An out-of-table mitigation — a per-cell base-rate bump, a tail-keep trigger, a convention — is by construction tunable, and the guarantee `B-116` term t3′ is owed is a guarantee that survives operator tuning.

### Rider (a) — the multi-tenant per-cell cardinality-budget check, EXECUTED, and it PASSES

`[HIGH]` The C7 reconcile registered this as owed **before the leg lands** (F-08: *"the §9.2 membership amendment must be checked against the multi_tenant per-cell cardinality budget before it lands"*), because always-sampled means head=1.0 at **every** cell including the two multi-tenant-compliance cells whose §10.3 base rate is 0.2. The check was run at this filing and the finding is recorded here rather than deferred:

> `fallback.exhausted` is a **terminal, once-per-exhausted-chain span EVENT** — a single emission site (`retry_breaker_fallback.py:947`, on the **outer** span, fired at most once per fully-exhausted dispatch) with a closed low-cardinality attribute set. §9.2 membership changes only the **SAMPLING disposition** of this already-existing event (head=1.0 keep instead of base-rate 0.2 at the multi-tenant production cells) and adds **ZERO emission sites and ZERO per-attempt multiplier**. The `C-OD-11` §11.1 per-cell budget (`per_cell_cardinality_budget.py`: `cell_rate_limit=10_000.0` spans/sec at every ACTIVE cell; `tenant_rate_limit=1_000.0` spans/sec at the two multi-tenant cells) enforces at the **COLLECTOR_BOUNDARY / BACKEND_INGESTION** layer **regardless of sampling decision** — so membership in the §9.2 floor cannot breach the rate budget, and the marginal keep-volume (0.8 × chain-exhaustion rate) is bounded far below it. **CHECK PASSES.**

**The F-08 population question — the actual multi-tenant chain-exhaustion volume — remains explicitly UNMEASURED**, consistent with the C7 reconcile's own FM-K refusal to assert a population claim. What is established is the **structural** result: the sampling disposition of a once-per-exhausted-chain event cannot move a per-cell rate budget that is enforced downstream of sampling at a limit three-to-four orders of magnitude above the event's own ceiling. The volume claim is not made, and no term here depends on one.

### Riders (b), (c), (d) — already registered; cross-referenced, NOT re-minted

The C7 reconcile's t3-leg registration carried four rider rows. (a) is executed above. The other three were minted as forward-register rows at the `B-116` ratification leg and are **cross-referenced here so this delta's scope reads as a decision rather than an omission**:

| Rider | Substance | Register row |
|---|---|---|
| (b) | the `is_classification_trigger` span-name-vs-span-event probe — it decides whether the CP `:409` tail-keep mitigation exists at all | **`B-123`** |
| (c) | `validator.fail.permanence` has no emission site, so §9.2 row `:530` is **inert** at HEAD | **`B-124`** |
| (d) | `harness.breaker.tool_id` is a homonym-in-waiting (breaker-key echo today, tool identity by its C-CP-03 §3.5 gloss) | **`B-125`** |

**None of the three is a precondition of this amendment**, and none is re-litigated here. Rider (c) is worth stating explicitly because it touches this very table: §9.2 row `:530` is inert at HEAD, which means the table this delta amends already contains one member whose qualifier no producer sets. That is `B-124`'s scope and **not** grounds to withhold row 19 — an inert sibling row is an argument for closing `B-124`, not for leaving a live event unclassified.

### What this delta deliberately does NOT do

**No CP edit.** `Spec_Control_Plane_v1_2.md:410` already declares the disposition; the ingesting contract is the one that was wrong. **No §10.1 edit** — `fallback.exhausted` is not and was never a base-rate member, so the C-OD-10 base-rate set is untouched and the §9.2 ⟂ §10.1 disjointness property is UNMOVED (the event enters exactly one regime; it does not join the two `kind`-discriminated dual-regime classes). **No new attribute and no emission-site change** — the event, its span, its attribute set and its single call site are all pre-existing and byte-unchanged; only its sampling disposition moves. **No §14.6.3 restatement** — the Runtime contract's waived-charge terms t1/t2 and the base-rate `retry.*` residual it records are cross-referenced, never restated here.

**No new §9.2 conditional qualifier.** Row 19 is an **unconditional** literal member, like `fallback.triggered` and `breaker.tripped` beside it — not one of the four conditional-by-attribute rows. This is deliberate: the event fires once, terminally, and there is no attribute that would discriminate a keep-worthy exhaustion from a discardable one.

### Cross-axis dispositions

**CP UNCHANGED** — `Spec_Control_Plane_v1_2.md` §3.5 already declares the disposition this delta ingests; cross-referenced, never restated. **Runtime UNCHANGED** — v1.112 §14.6.3 t3′ *registered* this gate and is discharged by this delta's landing; no Runtime text moves. **IS / AS specs UNCHANGED.** **CXA UNCHANGED** — no new cross-package consumption is introduced (the amendment moves a row inside a table OD already owns, consumed by OD's own substrate), so **no row is owed and the aggregate stays frozen at 111**. **C-OD-05 §5.1 namespace roster UNCHANGED at 15** — `fallback.*` is an already-ingested namespace; this adds a member to a sampling set, not a namespace to a roster. **C-OD-11 §11.1 per-cell cardinality budget UNCHANGED** — see rider (a): the budget enforces downstream of sampling and is not a function of §9.2 membership.

**Plan disposition.** `Implementation_Plan_Operational_Discipline_v2_32.md` is filed **in the same arc**, carrying NEW unit **U-OD-58** (the roster addition + its fixture conformance). Unlike v1.36, nothing is deferred to a later impl leg: the shape is fully determined by this table, so spec and plan and code land together.

### Historical carry — stated so it is not mistaken for staleness

`Spec_Operational_Discipline_v1_27.md:19` records *"§9.2 always-sampled exception set (18 entries)"* inside a table explicitly headed **"Status at HEAD pre-v1.27"**. That is a **timestamped point-in-time carrier landscape**, correct as of its own filing and PRESERVED VERBATIM under the delta-only convention. It is **not** stale-as-described and is **not** amended here. Forward from this delta, the live count is **19**, and every live count claim in the shipped substrate (`sampling_mode.py`, `alignment_floor_drift_detection.py`, `substrate_seam_exports_aggregate_manifest.py`, and both fixture modules) is reconciled at the same commit.

---

## §1 Amendment — C-OD-09 §9.2 always-sampled exception set: 18 → 19

**Amendment shape.** The §9.2 table at `Spec_Operational_Discipline_v1_2.md:513-532` gains **ONE row, appended as row 19**. **All eighteen existing rows are PRESERVED VERBATIM** — no row is reworded, reordered, removed, or re-qualified. §9.1, §9.3 and the §9 "Deferred to implementation discretion" footer are **UNTOUCHED**. The §9 header block (Contract surface / PRD requirement / ADR commitment / Cross-axis citation / Persona linkage) is **UNCHANGED**; in particular the Cross-axis citation line's existing `C-CP-03 §3.5` reference already names the declaring contract this row ingests, so no citation is added.

### §1.1 The new row

| Event class | Source declaration | Rationale |
|---|---|---|
| `fallback.exhausted` | C-CP-03 §3.5 (F1 / F3 capability-floor (iv)) | Reliability-critical — terminal once-per-exhausted-chain event; the CP-declared always-sampled disposition (`Spec_Control_Plane_v1_2.md:410`) was dropped at original OD ingestion while its two CP-table siblings `fallback.triggered` / `breaker.tripped` were absorbed |

**The Source-declaration cell is byte-identical in form to `fallback.triggered`'s** (OD `:521`), and deliberately so: the two rows ingest from the same CP table under the same ADR lineage, and a divergent citation shape at row 19 would misdescribe a sibling as a different kind of thing.

### §1.2 Post-amendment cardinality — stated as contract

**The §9.2 always-sampled exception set is EXACTLY NINETEEN members.** The four conditional-by-attribute rows are UNCHANGED at four (`files.operation`, `memory.operation`, `validator.fail.*`, and the root-conditional `subagent.span`); row 19 is **unconditional**. The two wildcard entries are UNCHANGED at two (`audit.*`, `validator.fail.*`), so the literal-vs-prefix decomposition the SDK-boundary lookup derives moves **17 literals + 2 prefixes** (from 16 + 2).

### §1.3 What is NOT changed by this row — each stated so its absence reads as a decision

| Surface | Disposition |
|---|---|
| §9.1 per-deployment-surface sampling mode | **UNCHANGED.** Row 19 binds at head=1.0 across all cells under §9.2's own preamble; it introduces no per-surface branch |
| §9.3 sampling-discipline invariants | **UNCHANGED, and all three now bind row 19** — the floor is inviolable at the deployment-binding layer, per-cell sampling within the set stays uniform |
| C-OD-10 §10.1 base-rate set (13 rows) | **UNCHANGED.** `fallback.exhausted` is not a base-rate member and never was; regime disjointness over non-`kind`-discriminated classes is preserved by construction |
| C-OD-10 §10.2 tail-keep triggers (3 rows) | **UNCHANGED.** Whether the existing breaker trigger is inert is `B-123`'s question, and head=1.0 is deliberately the guarantee that does not depend on its answer |
| C-OD-11 §11.1 per-cell cardinality budget | **UNCHANGED** — see rider (a): enforcement is at COLLECTOR_BOUNDARY / BACKEND_INGESTION, downstream of and independent of the sampling decision |
| C-OD-05 §5.1 namespace roster (15) | **UNCHANGED.** `fallback.*` is already ingested; this adds a set member, not a namespace |
| The event's attributes, span, and emission site | **UNCHANGED, byte-for-byte.** This delta moves a sampling disposition and nothing else |

### §1.4 Deferred to implementation discretion

**Nothing new.** §9's existing "Deferred to implementation discretion" footer is preserved verbatim and its four deferrals govern row 19 exactly as they govern the other eighteen. This delta adds no deferral of its own — the row's realization is a set-membership addition whose acceptance criteria are fully determined at `Implementation_Plan_Operational_Discipline_v2_32.md` U-OD-58.

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `design-substrate/Spec_Operational_Discipline_v1_37.md` |
| Version | v1.37 (delta over v1.36) |
| Predecessor | `Spec_Operational_Discipline_v1_36.md` |
| Authoring authority | `Spec_Harness_Runtime_v1.md` v1.112 §14.6.3 term **t3′** (the NAMED closure gate `B-116-t3`); council record `.harness/council/b116-breaker-semantics/01-council/contributions/C-c7-reconcile.md` §F-03 + §F-08 + the t3-leg registration block; operator ratification of Reading (II) 2026-08-07 |
| Contract-body change | **ADDITIVE only** — ONE row appended to the C-OD-09 §9.2 table (18 → 19). Eighteen existing rows, §9.1, §9.3 and the §9 header block PRESERVED VERBATIM. ZERO new contract numbers; ZERO new namespace (C-OD-05 §5.1 roster unchanged at 15); ZERO new attribute; ZERO emission-site change; ZERO hash impact |
| Cross-axis cascade | **NONE.** CP already declares the disposition (`Spec_Control_Plane_v1_2.md:410`) — zero CP delta; Runtime v1.112 §14.6.3 t3′ is DISCHARGED by this delta's landing with zero Runtime text moved; IS / AS unchanged; CXA aggregate frozen at 111 (no new cross-package consumption) |
| Rider dispositions | (a) F-08 multi-tenant per-cell cardinality-budget check — **EXECUTED at this filing, PASSES** (structural result; the population question explicitly unmeasured). (b)/(c)/(d) cross-referenced to already-minted rows `B-123` / `B-124` / `B-125` — **not re-minted, and none is a precondition of this row** |
| Plan delta | `Implementation_Plan_Operational_Discipline_v2_32.md` — NEW **U-OD-58**, filed in the SAME arc (nothing deferred to a later leg) |
| Impl leg | **BUNDLED** — the roster addition and its five fixture edit points land in this same PR under U-OD-58 |
| Register consequence | **`B-116` CLOSES at this leg.** Its §14.6.3 t3′ gate stated closure requires BOTH the impl leg (U-RT-152, merged PR #1271) and this t3 leg; with this delta both have landed |
| Skill discipline | `spec-writer` apply pass — applies the registered t3′ gate at the direction the council record grounded, executes the one rider it left owed, and decides nothing the record left open |
| Date | 2026-08-08 |
