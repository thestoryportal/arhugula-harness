# Spec: Control Plane — v1.33 (delta over v1.32)

---

## Change-note (v1.32 → v1.33)

**Scope of revision.** A single **substrate-deferral reconciliation** at **C-CP-07 §7.4** — the "Deferred to implementation discretion" clause gains one within-cell member: `reconciler-loop`. This is the **E-spec-3 leg** of the R-FS-1 E durable-execution-engine sub-program — the *only* spec touch the E arc owes (E-1 `EVENT_SOURCED_REPLAY` + E-2 `WAL_SEGMENT` were impl-against-cleared-spec, landed at PRs #564/#566 with no spec bump per the U-CP-56 precedent).

**The reconciliation.** C-CP-07 §7.4's deferral clause (v1.2, preserved verbatim through v1.32) names **event-sourced-replay, save-point-checkpoint, and WAL-segment** as having their substrate "deferred to implementation discretion," but **omits `reconciler-loop`** — whose substrate §7.1 row-4 + §7.4 floor-(i)/(iii) name concretely and non-deferred as "K8s controller / etcd + CRD events / etcd compare-and-swap." That named-vendored-K8s substrate conflicts with **I-6** (committed execution invariant, root `CLAUDE.md` §3.1/§3.2: hand-rolled reliability primitives, **no vendored K8s/Temporal/Kafka**). v1.33 reconciles the two committed surfaces: the §7.1/§7.4 "K8s controller / etcd" naming is re-read as the capability-floor **reference** implementation (parallel to "Temporal / DBOS / Restate" at event-sourced-replay), **not a vendored-K8s mandate**, and the harness-hosted hand-rolled etcd-style reconciliation control-loop (per I-6) is the spec-blessed candidate satisfying the same F3 floor (i)–(iv).

**Authoring authority.** R-FS-1 E sub-program, slice E-spec-3, per the architect recommendation `.harness/architect_recommendation_e_engine_fork_vs_impl.md` §4/§6/§7 (systems-architect §4A; decorrelated-reviewed — dedicated agent + out-of-family Codex concurred) + the Class-1 fork `.harness/class_1_fork_e3_reconciler_loop_substrate_deferral.md`. **Operator-ratified 2026-06-15** (the §7.4 amendment text ratified verbatim via AskUserQuestion — the single genuine operator fork in the E sub-program, a P5-CK cleared-contract touch reconciling two committed surfaces). Directive: `[[feedback-full-spec-beyond-mvp-nothing-deferred]]` (FULL-SPEC standing directive, roadmap §5.0).

**v1.32 + prior body PRESERVED VERBATIM.** All v1.32 content — §25.10–§25.18 (the C-CP-25 non-linear topology extension) + §29 / C-CP-29 `PromptSelectionManifest` + §1/§16.5.x/§25.1–§25.9/§26–§28 — is PRESERVED VERBATIM per the delta-only-spec-file convention. The §7.4 **capability-floor table (i)–(iv) is preserved verbatim**; the **only** change is the addition of the `reconciler-loop` member to the "Deferred to implementation discretion" paragraph's within-cell parenthetical. §7.1 (five-element taxonomy) + §7.2 (per-deployment-surface candidate mapping) are **PRESERVED VERBATIM** — their "K8s controller" / "K8s-resident" naming is the reference substrate, now explicitly read as such by the §7.4 amendment (no edit to §7.1/§7.2 text).

**No new contract ID; no new ADR; no `EngineClass`/`ResumptionKind` enum change; no six-field / hash-chain / ADR-F2 change.** The `EngineClass` enum is closed at 5 (ADR-D1 §1.1 + C-CP-07 §7.1; `reconciler-loop` already a member); `ResumptionKind` closed at 5 (C-CP-08 §8.1; `reconciler_converge` already mapped). v1.33 **reconciles** a cleared contract with a committed invariant — it introduces no new primitive (X-AL-3-clean).

**Trigger.** R-FS-1 E sub-program reaching its last engine class. At HEAD, `_IN_SCOPE_ENGINE_CLASSES` = {`PURE_PATTERN_NO_ENGINE`, `SAVE_POINT_CHECKPOINT`, `EVENT_SOURCED_REPLAY`, `WAL_SEGMENT`} (`workflow_driver.py:187-214`); only `RECONCILER_LOOP` still raises `EngineClassNotYetMaterializedError` (`:1398`). `engine_class.py:48` corroborates the split — its RECONCILER_LOOP docstring reads "Substrate: K8s CRD reconciler over etcd" with **no "deferred per §7.4" qualifier** (the ESR/WAL docstrings carry it).

**Committed HOW preserved (full-spec WHAT-vs-HOW).** The reconciler control-loop is **hand-rolled** (I-6: NO vendored K8s/etcd-operator/Temporal). The 8 §8.1 lifecycle events compose the same §5.1 closed-at-8 taxonomy (no new event class). The live-K8s e2e is deployment-surface-bound (`engine_class_candidate.py:70` excludes reconciler-loop at `local-development`; candidate at `self-hosted-server` + `managed-cloud`) — a **separate downstream deployment-surface gate** at E-impl-3, not part of this spec reconciliation. The §7.2 / ADR-D1 §1.2 **deployment-admissibility** of the hand-rolled reconciler (whether the harness-hosted reading widens its `local-development` placement) is likewise deferred to E-impl-3 — see the §7.4 reconciliation note; §7.2 is preserved verbatim here.

---

## §7.4 (RE-TABLED) C-CP-07 — Capability-floor preservation per class

*Re-tabled at v1.33 with the substrate-deferral reconciliation in the closing paragraph. The capability-floor table below is **PRESERVED VERBATIM** from v1.2; only the "Deferred to implementation discretion" paragraph changes (the `reconciler-loop` member added). §7.1/§7.2/§7.3 are NOT re-tabled (preserved verbatim).*

Per ADR-D1 v1.1 §1.4 (preserved verbatim from substrate read):

| F3 capability-floor | event-sourced-replay | save-point-checkpoint | pure-pattern-no-engine | reconciler-loop | WAL-segment |
|---|---|---|---|---|---|
| (i) Durable replay across restart | Engine event history | Checkpointer state + harness composition | F2 filesystem-journal + state-ledger | etcd + CRD events | WAL segment replay |
| (ii) Idempotency-keyed exactly-once via F2 ledger | F2 ledger joined on `idempotency_key` | F2 ledger joined on `idempotency_key` | F2 ledger native | F2 ledger joined; reconciler reads ledger | F2 ledger joined per segment |
| (iii) Lease coordination | Engine-native (Temporal placement; DBOS transaction) | Application-level (Redis / DB unique constraint / worktree per `Spec_Information_Substrate_v1.md` C-IS-09) | Harness-owned (worktree isolation per C-IS-09) | etcd compare-and-swap | Per-segment harness-owned |
| (iv) Observable lifecycle | Eight events per C-CP-05 §5.1 — engine emits via engine-event-bridge to OTel | Eight events per C-CP-05 §5.1 — harness emits at save-point boundaries | Eight events per C-CP-05 §5.1 — harness emits at filesystem-journal cadence | Eight events per C-CP-05 §5.1 — CRD reconciler emits | Eight events per C-CP-05 §5.1 — WAL emits at segment boundaries |

**Deferred to implementation discretion.** Specific engine candidate within each cell (Temporal / DBOS / Restate at event-sourced-replay; LangGraph + SqliteSaver vs LangGraph + Postgres at save-point-checkpoint; specific WAL implementation at WAL-segment class; **specific reconciler-loop substrate at reconciler-loop class — the §7.1 row-4 "K8s controller" lifecycle-ownership and the §7.4 floor-(i)/(iii) "etcd + CRD events / etcd compare-and-swap" substrate are the capability-floor _reference_ implementation (parallel to "Temporal / DBOS / Restate" at event-sourced-replay), not a vendored-K8s mandate; per I-6 (hand-rolled reliability primitives, no vendored K8s) the harness-hosted, hand-rolled etcd-style reconciliation control-loop is the spec-blessed candidate, satisfying the same F3 capability-floor (i)–(iv)**); specific candidate enumeration update procedure under Workflow §4.1.2 Class-2 revision; specific F3-capability-floor verification at workload-binding time.

**Reconciliation note (v1.33).** The reconciler-loop deferral mirrors the event-sourced-replay / WAL-segment wording exactly: the floor (i)–(iv) *mechanisms* are committed; only the substrate that *realizes* them is at implementation discretion. The F3 floor is preserved — a hand-rolled etcd-style store (a level-triggered, read/diff/converge reconcile loop with a compare-and-swap lease over an own-format durable store, joined to the F2 state-ledger on `idempotency_key`) satisfies (i)–(iv) without vendoring K8s. The §7.1 "K8s controller" lifecycle-ownership row reads as "harness-hosted reconciler control-loop" under this deferral, consistent with the §7.1 `pure-pattern-no-engine` / `WAL-segment` "Harness" ownership rows.

**Deployment-admissibility NOT resolved here (deferred to E-impl-3).** This substrate-deferral does **not** touch §7.2's per-deployment-surface candidate mapping (which lists `reconciler-loop (K8s-resident)` only at `self-hosted-server` + `managed-cloud` and excludes it at `local-development`). That mapping is **ADR-D1 §1.2-rooted**, not §7.4-internal. Whether the now-hand-rolled, harness-hosted reading widens reconciler-loop's `local-development` admissibility (it no longer "requires K8s control plane" in the `engine_class_candidate.py` sense) is a **deployment-placement question deferred to E-impl-3** — to be resolved against ADR-D1 §1.2 at materialization, not pre-decided by this reconciliation. Until then §7.2 stands verbatim and the existing exclusion holds.

---

## §-preserved-verbatim

| Section | Identity | v1.33 status |
|---|---|---|
| §1 — §16.5.12.X canonical-reading lineage | — | PRESERVED VERBATIM |
| §7.1 — §7.3 | **C-CP-07 — engine-class taxonomy / candidate mapping / workload-binding** | PRESERVED VERBATIM (the "K8s controller / K8s-resident" naming is the reference substrate, now read as such per the §7.4 amendment) |
| §7.4 capability-floor table (i)–(iv) | **C-CP-07** | PRESERVED VERBATIM (re-tabled above unchanged; only the closing deferral paragraph gained the `reconciler-loop` member) |
| §8 — C-CP-08 resumption semantics (incl. §8.1 `reconciler_converge`) | **C-CP-08** | PRESERVED VERBATIM (closed-at-5 ResumptionKind; reconciler-loop already mapped) |
| §25.1 — §25.18 | **C-CP-25 — WorkflowDriver** (incl. v1.32 non-linear topology extension) | PRESERVED VERBATIM |
| §26 — §29 | **C-CP-26 / C-CP-27 / C-CP-28 / C-CP-29** | PRESERVED VERBATIM |

§7.4's amendment is a within-paragraph addition to the existing C-CP-07 contract; no prior section is amended, reinterpreted, or superseded (§7.1's substrate naming is re-read, not edited).

---

## §-filing footer

| Field | Value |
|---|---|
| Artifact | `Spec_Control_Plane_v1_33.md` |
| Authored at | Phase 7 / R-FS-1 E sub-program (E-spec-3 — reconciler-loop substrate-deferral reconciliation), 2026-06-15 |
| Authoring authority | `.harness/architect_recommendation_e_engine_fork_vs_impl.md` §4/§6/§7 + `.harness/class_1_fork_e3_reconciler_loop_substrate_deferral.md`; operator-ratified 2026-06-15; R-FS-1 §5.0 full-spec directive |
| Predecessor | `Spec_Control_Plane_v1_32.md` (v1.32) |
| Co-published (this PR) | the Class-1 fork doc `.harness/class_1_fork_e3_reconciler_loop_substrate_deferral.md` + clearance marker `.harness/clearance/Spec_Control_Plane-v1_33-cleared-2026-06-15.md` + pointer refreshes (root `CLAUDE.md` §2.3, `harness-cp/CLAUDE.md` §1.2, `claude-artifact-pointers.md` §2.3 — CP spec head v1_30/v1_32 → v1_33). **Owed at post-merge:** the §12.2.1 roadmap fixed-point refresh (a terminating refresh PR, not part of this substantive PR). |
| Coordinated next arcs | E-plan (decompose E-3 RECONCILER_LOOP to atomic units — CP `_IN_SCOPE` += RECONCILER_LOOP + dispatch branch; RT hand-rolled etcd-style reconciliation substrate) → E-impl-3 (materialize + non-live proof). Live-K8s e2e = separate deployment-surface gate at E-impl-3. |
| Revision policy | Delta-only spec file per workspace `CLAUDE.md` §2.3 convention; v1.32 body + §7.1–§7.3 + §7.4 floor table + §8 + §25–§29 PRESERVED VERBATIM; the §7.4 deferral paragraph gains the `reconciler-loop` member only |

---

*End of `Spec_Control_Plane_v1_33.md`. Parent guidance at workspace root `CLAUDE.md`. C-CP-07 §7.1/§7.4 canonical body at `Spec_Control_Plane_v1_2.md` §7. Architect recommendation at `.harness/architect_recommendation_e_engine_fork_vs_impl.md`. Fork doc at `.harness/class_1_fork_e3_reconciler_loop_substrate_deferral.md`.*
