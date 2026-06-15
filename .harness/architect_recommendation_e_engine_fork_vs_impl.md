# Architect Recommendation — E sub-program: fork-vs-impl, per engine class

**Mode:** systems-architect Phase-7 tension-resolution (§4A). **Posture:** mode-agnostic (back-flow documentation; authors only this `.harness/` file — no `design-substrate/**` or `harness-*/src` edit). X-AL-3-clean.
**Filed:** 2026-06-15 · **Grounded at HEAD `0500aa4`** (every spec/code/fork cite resolved by direct read this session).
**The skill holds NO decision authority** — this renders the *canonical reading* traced to the authority chain (`CLAUDE.md` §1.3). The operator decides.
**Tension under resolution:** the just-merged E-DESIGN doc (`.harness/r-fs-1-e-engine-classes-design-v1.md`, PR #558) classified **all 3** unbuilt engine classes as **FORK-owed** (X-AL-3 driver-boundary design-extension → E-spec-1/2/3). A deeper re-grounding suggests **E-1 and E-2 are impl-against-cleared-spec (no fork)** and only **E-3 may need a narrow reconciliation**. This record resolves which reading is canonical, per class.

---

## §0 — Verdict (per class)

| Slice | Engine class | **Verdict** | Authority basis |
|---|---|---|---|
| **E-1** | `EVENT_SOURCED_REPLAY` | **impl-against-cleared-spec (NO fork)** | C-CP-07 §7.1 row 1 + §7.4 (candidate Temporal/DBOS/Restate **explicitly** "Deferred to implementation discretion") + C-CP-08 §8.1 `engine_replay` + U-CP-56 precedent + I-6 |
| **E-2** | `WAL_SEGMENT` | **impl-against-cleared-spec (NO fork)** | C-CP-07 §7.1 row 5 + §7.4 ("**specific WAL implementation at WAL-segment**" explicitly deferred to impl discretion) + C-CP-08 §8.1 `segment_replay` + U-CP-56 precedent + I-6 |
| **E-3** | `RECONCILER_LOOP` | **narrow-fork-owed** — precise underspec named in §4 | C-CP-07 §7.1 row 4 + §7.4 (reconciler-loop is the **ONE class whose substrate is NOT in the §7.4 impl-discretion clause**; spec names "etcd + CRD events / K8s controller" concretely) ⊥ I-6 ("no vendored K8s; hand-roll etcd-style") |

**The U-CP-56 precedent CONTROLS** for E-1 and E-2 (see §2). **I-6 is COMMITTED, not a new decision** — it constrains *which substrate* fills the §7.4-deferred slot (hand-rolled), it does not create a fork. The design doc inverted the authority chain for E-1/E-2 (treated the *driver-layer* `_IN_SCOPE_ENGINE_CLASSES` widening as a design-extension; the cleared spec + the U-CP-56 precedent both show it is impl).

---

## §1 — Tension stated precisely (the divergent positions)

**Position A (design doc PR #558, §0 + §3–§5 + §7.1).** Quote: *"E-1 / E-2 / E-3 … FORK (driver-boundary design-extension, X-AL-3) … adding a class to `_IN_SCOPE_ENGINE_CLASSES` + driver dispatch is a design-extension at the driver boundary (X-AL-3)."* → 3 certain forks; each owes an E-spec-N runtime/CP spec amendment + clearance marker before impl.

**Position B (this re-grounding).** The cleared C-CP-07 / C-CP-08 contracts already commit the per-class durable-execution *semantics* for all 5 classes; §7.4 explicitly **defers the substrate choice to implementation discretion** for event-sourced-replay and WAL-segment; I-6 (committed) names the hand-rolled substrate. Adding a class to `_IN_SCOPE_ENGINE_CLASSES` + a driver dispatch fork is **impl against the cleared spec** (U-CP-56 did exactly this for save-point-checkpoint with NO spec bump). → E-1/E-2 are impl; only E-3 carries a genuine spec divergence.

**The splitting fact** (the single byte-exact discriminator, re-read this session at `Spec_Control_Plane_v1_2.md:704`):

> **Deferred to implementation discretion.** Specific engine candidate within each cell (Temporal / DBOS / Restate **at event-sourced-replay**; LangGraph + SqliteSaver vs LangGraph + Postgres at save-point-checkpoint; **specific WAL implementation at WAL-segment class**); …

§7.4 names **event-sourced-replay, save-point-checkpoint, and WAL-segment** as having their substrate "deferred to implementation discretion." **`reconciler-loop` is conspicuously absent from that clause.** Its substrate is named concretely and non-deferred throughout §7.1 ("K8s controller"), §7.2 ("K8s-resident"), §7.4 floor-(i) ("etcd + CRD events"), floor-(iii) ("etcd compare-and-swap"). This asymmetry in the *cleared spec itself* is what splits E-3 from E-1/E-2.

---

## §2 — The U-CP-56 precedent CONTROLS for E-1 / E-2

**What U-CP-56 did** (`git show 402a7ea`, branch close per `.harness/class_1_tension_u_cp_56_resumption_underspec.md`): materialized `SAVE_POINT_CHECKPOINT` (and `PURE_PATTERN_NO_ENGINE`) into `_IN_SCOPE_ENGINE_CLASSES` and added driver dispatch (the `:1445` save-point fork) **as impl against `Spec_Control_Plane_v1_4` / C-CP-25** — **NOT** a new engine-semantics spec amendment. Commit message §"Scope at v1.4 (preserved)": *"SINGLE_THREADED_LINEAR topology + pure-pattern-no-engine + save-point-checkpoint engine classes only."* The `_IN_SCOPE` subset is an **impl-scoping choice**.

**The narrow fork U-CP-56 *did* file** was NOT about engine-class membership or engine semantics. It was `.harness/class_1_tension_u_cp_56_resumption_underspec.md` — AC #6 *save-point replay-resumption read at re-entry* — and its resolution explicitly closed **"No spec bump required"** / **"Plan-only revision suffices"** (fork §11, §"No spec bump rationale"). The underspec was two *substrate-primitive gaps* (`WorkflowManifestEntry.entry_version` missing; no prefix-match read primitive), **not** the engine-class durable-execution semantics. The semantics were cleared; only a downstream read-primitive detail was underspec, and even that resolved plan-only.

**Mapping to E-1 / E-2.** Adding `EVENT_SOURCED_REPLAY` / `WAL_SEGMENT` to `_IN_SCOPE_ENGINE_CLASSES` + a driver dispatch fork is the **same move U-CP-56 made for save-point-checkpoint** — impl against the cleared C-CP-07/08 taxonomy. The spec already commits:
- the *lifecycle ownership* (§7.1: event-sourced-replay = Engine; WAL-segment = Harness),
- the *resumption semantics* (§8.1: `engine_replay` "replay from Event History deterministically, activity outputs cached"; `segment_replay` "replay from WAL segments; per-segment dedup"),
- the *F2-ledger join discipline* (§8.2), and
- the *capability-floor* per class (§7.4 floor (i)-(iv)).

What §7.4 leaves open — the *specific* event-store/WAL implementation — is exactly the impl-discretion slot. **Filling that slot with a hand-rolled substrate is impl, not a spec amendment.** This is the ratified workspace pattern `[[cleared-spec-resolves-it-before-first-principles-fix]]` ("impl-to-cleared-spec ≠ X-AL-3 fork") + `[[grounding-reveals-claude-closeable-slice-close-honestly]]` ("spec'd → build").

**Corroborating code evidence** (the impl layer's own self-classification): `engine_class.py` docstrings — EVENT_SOURCED_REPLAY: *"candidate enumeration deferred per §7.4"*; WAL_SEGMENT: *"implementation deferred per §7.4"*; RECONCILER_LOOP: *"Substrate: K8s CRD reconciler over etcd"* with **NO "deferred per §7.4" qualifier.** The code already encodes the same split this recommendation derives from the spec.

---

## §3 — Why the design doc's "all-3-fork" reading does not hold for E-1 / E-2

The design doc inherited its framing from two upstream sources, both of which I re-grounded:

1. **The Path-(i) fork (`class_1_fork_path_i…`, filed 2026-05-25).** Its §4 options A/B/C say "Design-phase back-flow required." **But its filing date is PRE the full-spec directive (2026-06-12), and its "back-flow required" answered the SCOPE question (build-or-not), which full-spec has since answered.** Re-reading the fork: §4 is a *routing menu* (build A/B/C vs defer D/E); the operator chose **(E) defer**. The fork never adjudicated that the *semantics* are underspec — it adjudicated whether to *spend the build effort*. §7 "Closure conditions" conflates "design-phase back-flow re-issues spec+plan" with the build itself; that conflation is the load-bearing error the design doc inherited. Full-spec re-opens the *scope* decision; it does not convert cleared semantics into underspec.

2. **The grounding sweep (`r-fs-1-remaining-arcs-grounding-sweep-v1.md` Arc-E).** This is an Explore-style sweep (`[[subagent-landscape-reports-need-regrounding]]` — presence-not-correctness). It asserts "adding a class to `_IN_SCOPE_ENGINE_CLASSES` + driver dispatch is a design-extension at the driver boundary (X-AL-3)" without re-deriving against the C-CP-07 §7 body **or** the U-CP-56 precedent. The design doc + its adversarial reviewer inherited the framing rather than re-deriving it. (The design doc's §9 records advisor() was unavailable across 4 attempts that session, so the transcript-aware reviewer never checked this leg.)

**The X-AL-3 test, applied correctly.** X-AL-3 (I-2) forecloses *silent H_T design extension* — surfacing a **new H_T primitive** at execution-time and absorbing it as canonical. Materializing E-1/E-2 introduces **no new primitive**: the `EngineClass` enum is closed at 5 (committed at ADR-D1 §1.1 + C-CP-07 §7.1), the resumption-kind enum is closed at 5 (C-CP-08 §8.1), the F3 floors are cleared (§7.4). E-1/E-2 *consume* cleared closed enumerations. The `_IN_SCOPE_ENGINE_CLASSES` set is an **impl-internal scoping frozenset**, not a spec contract — widening it is the same act U-CP-56 performed under "no spec bump." Treating a later artifact (the driver's in-scope set) as canonical over the earlier cleared spec is the **authority-chain inversion** anti-pattern (SKILL §5).

---

## §4 — E-3 RECONCILER_LOOP: the genuine narrow fork (precise underspec named)

E-3 is **not** symmetric with E-1/E-2. The divergence is real and lives in the cleared spec:

**The precise underspec / divergence.** C-CP-07 §7.1 row 4 commits reconciler-loop's **lifecycle ownership = "K8s controller"** and its substrate = "etcd + CRD events" (§7.4 floor (i)), "etcd compare-and-swap" (floor (iii)) — and **does NOT place reconciler-loop in the §7.4 "deferred to implementation discretion" clause** (unlike event-sourced-replay and WAL-segment). The cleared spec therefore reads reconciler-loop as a **vendored-K8s-resident** engine. I-6 (committed, `CLAUDE.md` §3.1/§3.2; SPINE ledger §17 WHAT-vs-HOW) mandates **hand-rolled, NO vendored K8s** ("hand-roll etcd-style"). These two committed surfaces **conflict on the substrate** for this one class:

> **Cleared spec (C-CP-07 §7.1/§7.4):** reconciler-loop lifecycle owned by a *K8s controller*, substrate = *etcd + CRD events* (NOT deferred to impl discretion).
> **I-6 (committed):** hand-roll the durable engines; NO vendored K8s.

For event-sourced-replay/WAL-segment, I-6 + §7.4 *compose cleanly* — §7.4 already defers the substrate, so I-6 just selects "hand-rolled" within an open slot. For reconciler-loop, §7.4 does **not** open that slot, so reconciling "K8s controller / etcd CRD" (spec) with "hand-rolled etcd-style, no K8s" (I-6) requires a **narrow spec reconciliation**: an explicit C-CP-07 §7.4 amendment adding reconciler-loop to the impl-discretion clause (parallel to how event-sourced-replay/WAL-segment are already worded), so the hand-rolled etcd-style substrate is the spec-blessed candidate rather than a silent divergence from the named "K8s controller / etcd + CRD" substrate.

**Scope of the E-3 fork (narrow).** It is NOT "the reconciler-loop semantics are unbuilt/undesigned" — the semantics (read/diff/converge, level-triggered idempotent reconcile, etcd compare-and-swap lease, the 8 lifecycle events) are cleared at §7.1/§7.4/§8.1 (`reconciler_converge`). The fork is **the single substrate-binding sentence**: amend §7.4 to defer reconciler-loop's substrate to impl discretion (hand-rolled etcd-style per I-6), mirroring the existing event-sourced-replay/WAL-segment wording. This is a one-line-class spec reconciliation, not a full spec leg.

**Note — this is the inverse of the design doc's E-3 framing.** The design doc treats E-3 as the *hardest/largest* fork (25-45 commits, infra-gated). On *substrate cost* that ordering is right. But on *fork-necessity*, E-3 is the **only** class needing a spec touch, and the spec touch itself is narrow (the substrate-deferral sentence). The build cost (hand-rolled reconciler + the K8s-infra-gated live e2e per `engine_class_candidate.py:70`) is orthogonal to the fork question.

**The infra gate is NOT a fork trigger.** `engine_class_candidate.py:70` excludes reconciler-loop at `local-development` ("requires K8s control plane") but lists it as a candidate at `self-hosted-server` + `managed-cloud` — exactly mirroring C-CP-07 §7.2. The hand-rolled reconciler logic + non-live (in-memory/filesystem) proof are buildable today; only the *live K8s e2e* carries the deployment-surface gate. That gate is a live-proof boundary (a genuine operator decision per `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`), not a spec-fork.

---

## §5 — Five-axis + F/D/I placement (SKILL §2 discipline)

- **Control plane** (primary). The engine-class taxonomy is CP-axis (C-CP-07/08). The `_IN_SCOPE_ENGINE_CLASSES` + driver dispatch is CP-internal.
- **Information substrate** (secondary). The hand-rolled substrates (event store / segment log / etcd-style store) are on-disk state → the IS PathClass placement (§6.2 of the design doc) is the one CP↔IS seam. Per `[[cross-spec-enum-overlap-carrier-segregation]]`, resolve descriptively (recommend `STATE_LEDGER`); halt only on conflicting-semantics on a shared carrier. This is a *conditional* IS sub-fork, decided with each driver — not an E-1/E-2 blocker.
- **Operational discipline** (secondary). The C-CP-49/50 (= U-CP-49/U-CP-50) engine-layer pause/resume composers are cleared+built (CP §16.5, substantively v1.25/v1.26, canonical-reading-amended v1.30); firing them from a real driver is impl. The R-CXA-2 CP→IS engine-layer seam goes live at the first real producer (E-1). **No fork** — this leg of the design doc is correct. **[E-plan annotation 2026-06-15:** the "first real producer (E-1)" attribution is **SUPERSEDED** by the E-plan's empirical re-grounding — the engine recovery loop is a C-CP-22 pause/resume-SNAPSHOT surface, EVENT_SOURCED_REPLAY's §8.1 semantic is deterministic event-history replay with no discrete snapshot-pause boundary, and it is not a §18.1 DURABLE_ASYNC cell (`test_u_rt_95:129-131`) — so R-CXA-2 engine-layer activation homes at **E-2 (WAL_SEGMENT)**, not E-1. This §5 verdict's CORE holds (firing C-CP-49/50 from a real driver is impl-not-fork); only the which-class attribution moves. See `.harness/r-fs-1-e-plan-decomposition.md` §5 + CP plan v2.34 §6 O-CP-4.]**
- **Deployment surface.** Reconciler-loop's K8s residence is the only deployment-surface-bound divergence (§4).
- **Probabilistic-deterministic boundary.** All 3 engines are deterministic-side (durable execution, replay, idempotency) — squarely the harness's reliability layer. I-6's hand-roll mandate keeps reliability in the deterministic outer harness, consistent with SKILL §2.2.

**F/D/I.** The engine-class *taxonomy* is **Foundational** (ADR-D1, cleared). The *specific substrate per class* is **Derivative** — and for event-sourced-replay/WAL-segment the spec **already delegated** that derivative choice to impl discretion (§7.4). E-3's substrate is the one derivative the spec did NOT delegate → the narrow reconciliation. No foundational decision is reopened by any slice.

---

## §6 — Fork classification (Workflow §2.7.6) + recommended next-action

| Slice | Fork class | Implication for execution |
|---|---|---|
| **E-1** EVENT_SOURCED_REPLAY | **No fork (Class 3 informational at most)** — impl against cleared C-CP-07/08; substrate deferred to impl discretion per §7.4; I-6 selects hand-rolled. Optional Class-3 note that the §7.4-deferred slot is being filled hand-rolled. | Proceed to E-plan → E-impl directly. No spec leg, no clearance marker owed. |
| **E-2** WAL_SEGMENT | **No fork (Class 3 informational at most)** — same basis; §7.4 explicitly defers "specific WAL implementation." Extend #475 `JournalEnginePauseResumeSubstrate` via a REAL driver. | Proceed to E-plan → E-impl directly. Un-skips Path-(i) `test_u_rt_95` at this slice. |
| **E-3** RECONCILER_LOOP | **Class 1 narrow-fork** — C-CP-07 §7.4 amendment adding reconciler-loop to the impl-discretion substrate clause (hand-rolled etcd-style per I-6), reconciling §7.1 "K8s controller / etcd + CRD" with I-6 "no vendored K8s." Narrow (one substrate-deferral sentence) + clearance marker. | Author the narrow E-spec-3 leg (substrate-deferral reconciliation only) → clearance marker → then E-plan → E-impl. Live K8s e2e is a separate deployment-surface operator gate, not part of the fork. |

**Recommended next-action for the E sub-program:**

> **E-plan-then-impl for E-1 + E-2 (no spec leg).** For E-3, author a *single narrow* C-CP-07 §7.4 substrate-deferral reconciliation (mirror the event-sourced-replay/WAL-segment wording) + clearance marker, then E-plan → E-impl. Drop the planned E-spec-1 and E-spec-2 spec legs entirely; they are not owed.

This collapses 3 spec legs → 1 narrow reconciliation, removing ~2 unnecessary design-substrate amendment arcs while staying X-AL-3-clean (E-1/E-2 introduce no new primitive; E-3's reconciliation is documented back-flow).

---

## §7 — Open question for the operator vs Claude-resolvable

**Claude-resolvable (rendered here, no operator decision needed):**
- E-1/E-2 = impl-against-cleared-spec — determined by §7.4 byte-exact + U-CP-56 precedent + I-6 (all committed/cleared surfaces). The skill renders this as the canonical reading; no genuine fork to surface.
- The IS PathClass placement (recommend `STATE_LEDGER`) is descriptively resolvable per `[[cross-spec-enum-overlap-carrier-segregation]]`, decided with each driver.

**Genuine operator decision (one, and only one architectural fork):**
- **E-3's narrow C-CP-07 §7.4 reconciliation.** Because it touches a *cleared spec contract* (C-CP-07, P5-CK) and reconciles two **committed** surfaces (the spec's named "K8s controller / etcd + CRD" substrate vs I-6's "hand-roll, no vendored K8s"), it requires explicit operator sign-off before the spec-writer applies it — even though the full-spec directive pre-authorizes the *build*, the *reconciliation of a cleared contract* is the operator's to ratify. Recommended framing: "ratify the E-3 §7.4 substrate-deferral amendment (hand-rolled etcd-style) — Y/adjust." (Lead with the recommendation per `CLAUDE.md` §1.)

**Tiebreaker check (the single fact that, if confirmed, makes this determinate):** *Confirm C-CP-07 §7 + §8.1-§8.3 are "preserved verbatim from v1.2" through the entire CP delta chain to head v1_32* — i.e. no later delta re-tabled §7.1/§7.4 to add reconciler-loop to the impl-discretion clause or to remove event-sourced-replay/WAL-segment from it. **CONFIRMED this session:** v1_3 §7 reads "[Preserved verbatim from v1.2.]"; v1_3 §8.1-§8.3 read "[Preserved verbatim from v1.2.]"; only §8.4 + §9 took the F2-12 closure amendment (which touches `engine.*` span attributes, not the taxonomy or the §7.4 deferral clause). The v1_2 §7.1/§7.4/§8.1 body is the last substantive definition → canonical at head.

---

## §8 — Evidence ledger (cites re-grounded by direct read this session)

| # | Cite | Verified |
|---|---|---|
| 1 | `Spec_Control_Plane_v1_2.md:641-704` C-CP-07 §7.1/§7.2/§7.4 (taxonomy, candidate mapping, capability-floor) | ✅ read |
| 2 | `Spec_Control_Plane_v1_2.md:708-770` C-CP-08 §8.1-§8.4 (resumption-kind enum, F2 join) | ✅ read |
| 3 | `Spec_Control_Plane_v1_2.md:704` §7.4 deferral clause — names event-sourced-replay + save-point + WAL-segment; **omits reconciler-loop** | ✅ read (the splitting fact) |
| 4 | `Spec_Control_Plane_v1_3.md:133-161` — §7 "[Preserved verbatim from v1.2]"; §8.1-8.3 "[Preserved verbatim]" (delta-chain canonical-version confirm) | ✅ read |
| 5 | `git show 402a7ea` U-CP-56 PARTIAL-LAND — save-point added to `_IN_SCOPE` as impl against v1.4/C-CP-25, no engine-semantics spec amendment | ✅ read |
| 6 | `.harness/class_1_tension_u_cp_56_resumption_underspec.md` — the narrow fork was AC#6 read-primitive underspec, resolved "No spec bump required / plan-only" | ✅ read |
| 7 | `.harness/class_1_fork_path_i…md` — §4 routing menu; closed (E) defer; filed 2026-05-25 PRE full-spec; "back-flow required" answered SCOPE not SEMANTICS | ✅ read |
| 8 | `harness-cp/src/harness_cp/workflow_driver.py:183-184,1351-1352,1445` — `_IN_SCOPE` = {PURE_PATTERN, SAVE_POINT}; gate raises for the 3; save-point dispatch fork | ✅ read |
| 9 | `harness-cp/src/harness_cp/engine_class.py:23-55` — docstrings: ESR "candidate deferred per §7.4"; WAL "implementation deferred per §7.4"; RECONCILER "Substrate: K8s CRD over etcd" (no deferral) | ✅ read |
| 10 | `harness-cp/src/harness_cp/engine_class_candidate.py:60-100` — ESR+WAL candidates at LOCAL_DEV; only RECONCILER excluded ("requires K8s control plane"); RECONCILER candidate at server+managed | ✅ read |
| 11 | `.harness/beyond-mvp-capability-boundary-ledger.md:17` — I-6 WHAT-vs-HOW: hand-roll durable engines, NO vendored framework; directive sets WHAT not HOW | ✅ read |
| 12 | `CLAUDE.md` §3.1/§3.2 I-6; §1.3 authority chain; SKILL §4A/§5 (authority-chain-inversion, decide-not-recommend) | ✅ read |
| 13 | `design-substrate/Spec_Control_Plane_v1_30.md:24` — U-CP-49/U-CP-50 are the engine-layer §16.5.2 composers (the design doc's "C-CP-49/50"); cleared+built | ✅ read |

**Decorrelated review.** `advisor()` was attempted (overloaded across 5 attempts this/prior turn, as it was during the design doc's own session per its §9). **Out-of-family `just codex-review` ran on the correction PR (#560) and CONCURRED on the substance** — it did not dispute E-1/E-2=impl or E-3=narrow-fork; its only finding was a governance-status-wording nit ("decorrelated-confirmed" was stated ahead of this codex pass), since fixed. So the fork-vs-impl reversal is confirmed by two decorrelated reviewers (this systems-architect dedicated agent's independent primary-source re-derivation + Codex); advisor remains the one unavailable check. A re-attempt of `advisor()` when available is still welcome before the operator ratifies the E-3 §7.4 reconciliation, but is no longer the sole decorrelated gate.

---

## §9 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/architect_recommendation_e_engine_fork_vs_impl.md` |
| Mode | systems-architect §4A tension-resolution (recommendation; operator decides) |
| Grounded at HEAD | `0500aa4` |
| Resolves tension in | `.harness/r-fs-1-e-engine-classes-design-v1.md` §0/§3/§7.1 (all-3-fork classification) |
| Verdict | E-1 impl / E-2 impl / **E-3 narrow-fork** (§7.4 substrate-deferral reconciliation) |
| Controlling precedent | **U-CP-56** (`402a7ea`) — save-point added to `_IN_SCOPE` as impl, no engine-semantics spec bump |
| Splitting fact | C-CP-07 §7.4 impl-discretion clause names ESR+save-point+WAL but **omits reconciler-loop** |
| Operator decision owed | E-3 §7.4 reconciliation ratification only (cleared-contract touch reconciling spec-substrate vs I-6) |
| Successor | E-plan (E-1+E-2 direct); E-spec-3 (narrow §7.4 reconciliation) + clearance → E-plan → E-impl |
