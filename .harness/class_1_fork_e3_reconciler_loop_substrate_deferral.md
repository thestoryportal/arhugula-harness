# Class-1 Fork — E-3 RECONCILER_LOOP substrate-deferral reconciliation (C-CP-07 §7.4)

**Class:** 1 (cleared-contract touch; design-substrate amendment to a P5-CK contract). **Locus:** CP spec C-CP-07 §7.4. **Posture:** back-flow documentation (this `.harness/` file is mode-agnostic; **NO `design-substrate/**` edit until operator ratification** — that is the X-AL-3 line).
**Status:** ✅ **RATIFIED-AND-APPLIED 2026-06-15** — operator ratified the §3 amendment **verbatim** ("Ratify as written") via AskUserQuestion; applied same session as CP spec **v1_33** (`design-substrate/Spec_Control_Plane_v1_33.md` §7.4 re-table) + clearance marker `.harness/clearance/Spec_Control_Plane-v1_33-cleared-2026-06-15.md` + the three pointer refreshes, in the E-spec-3 PR. Decorrelated pre-merge review CLEARED (harness-adversarial-reviewer dedicated agent: 0 blocking, F-1 deployment-admissibility-deferral applied; out-of-family Codex: 2 [P2] governance-hygiene, both applied). §6 below records the ratified disposition (the original draft asked the gate; it is now answered).
**Filed:** 2026-06-15 · **Grounded at HEAD `eb8b90b`** (every cite re-read this session). **Vehicle:** R-FS-1 E sub-program, slice E-spec-3 (the *only* spec leg the E arc owes; E-1/E-2 were impl-against-cleared-spec, landed #564/#566).
**Derivation authority:** `.harness/architect_recommendation_e_engine_fork_vs_impl.md` §4/§6/§7 (systems-architect §4A; decorrelated-reviewed — dedicated agent + out-of-family Codex concurred; advisor was unavailable that session, re-consulted + concurred this session). This fork doc does **not** re-derive the verdict — it pins the concrete amendment the operator ratifies.

---

## 1. The fork (one sentence)

C-CP-07 §7.4's "Deferred to implementation discretion" clause names **event-sourced-replay, save-point-checkpoint, and WAL-segment** as having their substrate deferred to impl-discretion, but **conspicuously omits `reconciler-loop`** — whose substrate §7.1 row-4 + §7.4 floor-(i)/(iii) name concretely and non-deferred as **"K8s controller / etcd + CRD events / etcd compare-and-swap."** That named-vendored-K8s substrate conflicts with **I-6** (committed: hand-rolled reliability primitives, *no vendored K8s*). Reconciling the two committed surfaces requires a **single substrate-deferral sentence** added to §7.4 (mirroring the existing ESR/WAL wording) so the hand-rolled etcd-style reconciler is the spec-blessed candidate rather than a silent divergence.

This is the inverse of substrate *cost*: E-3 carries the largest build (hand-rolled reconciler + a K8s-gated live e2e) but the **narrowest spec touch** — it is the only one of the 5 engine classes whose substrate the cleared spec did *not* already delegate.

## 2. Splitting fact (byte-exact, re-verified this session)

`Spec_Control_Plane_v1_2.md:704` (§7.4 canonical — last substantive definition; `[Preserved verbatim from v1.2]` through head per §4 below):

> **Deferred to implementation discretion.** Specific engine candidate within each cell (Temporal / DBOS / Restate at event-sourced-replay; LangGraph + SqliteSaver vs LangGraph + Postgres at save-point-checkpoint; specific WAL implementation at WAL-segment class); …

`reconciler-loop` is absent. §7.1 row 4 (`:662`): lifecycle ownership = **"K8s controller"**, substrate = **"K8s etcd (Tier-3) + CRD events (Tier-5)"**, mitigation = **"etcd compare-and-swap"**. §7.4 floor row (i)/(iii): **"etcd + CRD events"** / **"etcd compare-and-swap."** Code corroborates the split: `engine_class.py:48` RECONCILER_LOOP docstring reads *"Substrate: K8s CRD reconciler over etcd"* with **no "deferred per §7.4" qualifier** (ESR/WAL docstrings carry the qualifier).

## 3. The exact amendment (what the operator ratifies)

Lands as a **new delta `Spec_Control_Plane_v1_33.md`** (§7.4 re-tabled; all other sections preserved verbatim per delta-only convention). The §7.4 "Deferred to implementation discretion" clause's within-cell parenthetical gains one reconciler-loop member:

> **Deferred to implementation discretion.** Specific engine candidate within each cell (Temporal / DBOS / Restate at event-sourced-replay; LangGraph + SqliteSaver vs LangGraph + Postgres at save-point-checkpoint; specific WAL implementation at WAL-segment class**; specific reconciler-loop substrate at reconciler-loop class — the §7.1 row-4 "K8s controller" lifecycle-ownership and the §7.4 floor-(i)/(iii) "etcd + CRD events / etcd compare-and-swap" substrate are the capability-floor _reference_ implementation (parallel to "Temporal / DBOS / Restate" at event-sourced-replay), not a vendored-K8s mandate; per I-6 (hand-rolled reliability primitives, no vendored K8s) the harness-hosted, hand-rolled etcd-style reconciliation control-loop is the spec-blessed candidate, satisfying the same F3 capability-floor (i)–(iv)**); specific candidate enumeration update procedure under Workflow §4.1.2 Class-2 revision; specific F3-capability-floor verification at workload-binding time.

**Scope discipline.** §7.1/§7.2 stay verbatim (their "K8s controller / K8s-resident" naming is now explicitly the *reference* substrate). The F3 floor (i)–(iv) mechanisms stay — only the substrate that *realizes* them is deferred. No new contract ID; no `EngineClass`/`ResumptionKind` enum change (both closed; RECONCILER_LOOP already a member); X-AL-3-clean (no new primitive — this *reconciles* a cleared contract with a committed invariant).

## 4. Grounding facts (verified this session)

| Fact | Verified |
|---|---|
| True CP spec head = **v1_32** (`design-substrate/Spec_Control_Plane_v1_32.md`); amendment → **v1_33** | `ls … | sort -V | tail` ✅ |
| CLAUDE.md §2.3 cites **v1_30** — a **stale pointer** (v1_31 §29 prompts + v1_32 §25/28 identity-correction landed after); harness-cp/CLAUDE.md §1.2 already at v1_32 | grep ✅ (Class-3 governance drift; note below) |
| §7.4 last-substantive-definition = **v1_2**; v1_30/31/32 touch §16.5/§29/§25-28 — **none re-table §7.4** | per-delta grep ✅ (rec §7 tiebreaker re-confirmed) |
| `_IN_SCOPE_ENGINE_CLASSES` = {PURE_PATTERN, SAVE_POINT, EVENT_SOURCED_REPLAY, WAL_SEGMENT}; only RECONCILER_LOOP raises at `workflow_driver.py:1398` | direct read ✅ (E-3 is the last E class) |

**Class-3 note (not part of this gate):** CLAUDE.md §2.3 CP-spec pointer is stale at v1_30 vs head v1_32. Fold the §2.3 refresh into the E-spec-3 PR (or a sibling roadmap refresh) — mode-agnostic, no design-substrate edit.

## 5. After ratification — pre-authorized build (drive autonomously, no re-gate)

Per the full-spec directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`), everything after "Y" is pre-authorized:

1. **E-spec-3 apply** — spec-writer applies the §3 amendment as v1_33 + change-note + clearance marker (`.harness/clearance/`); refresh CLAUDE.md §2.3 + harness-cp/CLAUDE.md + claude-artifact-pointers §2.4.
2. **E-plan** — decompose E-3 to atomic units (CP: `_IN_SCOPE` += RECONCILER_LOOP + dispatch branch + `_determine_reconciler_*_resume_at`; RT: hand-rolled etcd-style reconciliation substrate per I-6, extending the proven journal/WAL substrate pattern).
3. **E-impl-3** — materialize RECONCILER_LOOP; hand-rolled reconciler control-loop + **non-live (in-memory / filesystem) proof**.
4. **Separate downstream gate (NOT this one):** the **live K8s e2e** is deployment-surface-bound (`engine_class_candidate.py:70` excludes reconciler-loop at local-development; candidate at self-hosted-server + managed-cloud). That is a distinct operator/infra gate at E-impl-3 per `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]` — do **not** bundle it into this spec ratification.

## 6. The single operator decision (this gate) — ✅ RESOLVED

The *one* genuine operator fork in the E sub-program — **ratify the §3 C-CP-07 §7.4 substrate-deferral amendment** (hand-rolled etcd-style per I-6, landing as CP spec v1_33), a P5-CK cleared-contract touch reconciling two committed surfaces (spec-named "K8s controller / etcd + CRD" vs I-6 "no vendored K8s") — was surfaced via AskUserQuestion and **ratified "as written" by the operator on 2026-06-15**. The §3 text landed verbatim at `Spec_Control_Plane_v1_33.md` §7.4. No wording adjustment was requested. The deployment-admissibility under-reach surfaced by the adversarial review (F-1) was added to the §7.4 reconciliation note in-arc (deferred to E-impl-3, §7.2 untouched). Next: E-plan → E-impl-3 (pre-authorized; §5 above).
