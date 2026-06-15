# Class 1 Fork — F-B3-2 precondition: timeout-degradation VOCABULARY drift (code ⊥ foundational ADR-D5 + cleared CP spec §20.6)

**Type:** Class 1 (a code-vs-foundational-ADR divergence on a committed surface — surfaced during B3-spec-2 arc-open grounding; reshapes the F-B3-2 design premise and must resolve BEFORE F-B3-2 authors the runtime dispatch-on-mode contract).

**Status:** ✅ RATIFIED 2026-06-14 (operator AskUserQuestion) — **Reconcile code → ADR-D5 vocab** (§2.2, the recommended authority-chain path; NO ADR change). The canonical timeout-degradation vocabulary is **vocab-A** `{fail-closed, escalate-secondary-channel, fail-open}` (ADR-D5 §1.6 + cleared CP spec §20.6). Resolution split across B3-spec-2 (this fork + the runtime-spec dispatch-on-mode contract, authored against vocab-A) and B3-impl-2 (the code enum reconciliation `TimeoutDegradationKind` vocab-B → vocab-A + the dispatch-on-mode wiring + cross-ref updates). See §2.4 for the corrected (smaller) F-B3-2 scope.

---

## §1 — The gap

The B3 design (`.harness/r-fs-1-b3-smart-hitl-design-v1.md` §6.2, cleared #549) scoped **F-B3-2 (G4b)** as: *make the runtime timeout path dispatch on the `TimeoutDegradationKind` rather than unconditionally raise* — with the kinds named `{CONTINUE_AS_REJECT, ESCALATE_TO_REVIEW_BOARD, ABORT_WORKFLOW}` "by their CP definitions (C-CP-21 §21.6)." **Arc-open grounding falsifies that premise.** There are TWO competing timeout-degradation vocabularies in the workspace, and the one the design named is the **non-canonical (drifted) code formulation**.

### §1.1 Vocab-A — the CANONICAL authority

| Source | Vocabulary | Per-persona-tier mapping |
|---|---|---|
| **Cleared CP spec v1.2 §21.8** (`Spec_Control_Plane_v1_2.md` lines 1935-1947 — *"Timeout-degradation mode at durable-async cells"*; **the on-point per-tier control-flow mode table**) | `{fail-closed, escalate-secondary-channel, fail-open}` | solo→`fail-closed`; team→`escalate-secondary-channel` (default) / `fail-closed` (configurable); multi→`fail-closed` + alerting (**`fail-open` prohibited** per Persona §10.4) |
| **ADR-D5 §1.6** (foundational; `design-substrate/ADR-D5.md` lines 281-287) | `{fail-closed, escalate-secondary-channel, fail-open}` | identical per-tier table to CP §21.8 (the foundational source it derives from) |
| **Cleared CP spec v1.2 §20.6** (`Spec_Control_Plane_v1_2.md` line 1821) | the `hitl.invocation.timed_out` span attribute `hitl.timeout.degradation_mode_applied ∈ {fail-closed, escalate-secondary-channel, fail-open}` | (span-attribute value-set; matches the §21.8 + ADR vocabulary) |
| **NOTE — `fail-open` is assigned to NO tier** by any of the three authorities | `fail-open` appears ONLY in the multi-tenant *prohibition* clause | no tier (incl. solo) is affirmatively granted `fail-open` as a usable mode (decorrelated-review catch — see §2.5) |

### §1.2 Vocab-B — the CODE drift

| Source | Vocabulary | Per-persona-tier mapping |
|---|---|---|
| **CODE** `harness-cp/src/harness_cp/hitl_timeout_degradation.py:40` (`TimeoutDegradationKind` + `TIMEOUT_DEGRADATION_TABLE`) | `{continue-as-reject, escalate-to-review-board, abort-workflow}` | solo→`CONTINUE_AS_REJECT`; team→`ESCALATE_TO_REVIEW_BOARD`; multi→`ABORT_WORKFLOW` |
| **Early CP plans** v2 / v2.1 (pre-convergence; `Implementation_Plan_Control_Plane_v2.md`, `_v2_1.md`) | same vocab-B | — |

The code docstrings cite **"C-CP-21 §21.6"** as the authority — a **WRONG-SECTION cite**: CP v1.2 §21.6 is *"Sampling discipline for validator-failure spans"* (line 1914), NOT timeout degradation. The real per-tier timeout-degradation **mode** table is **CP §21.8** (*"Timeout-degradation mode at durable-async cells"*, lines 1935-1947) — in **vocab-A** — corroborated by ADR-D5 §1.6 (foundational) + the CP §20.6 span value-set. (The original draft of this fork claimed "§20.6 is the CP spec's only timeout surface" — that was wrong; §21.8 is the on-point mode table. Decorrelated-review correction.) The drift was previously catalogued as **"marginal, not escalated"** pre-wiring at `.harness/verbatim_audit_cp_plan.md` (U-CP-52: *"plan values … re-express spec §21.8's … modes; the plan cites §21.6 while the content is at §21.8"*); B3 **escalates** it because this arc *wires* the dispatch, making the semantic divergence behaviorally live (esp. the multi `abort-workflow`-vs-`fail-closed` disposition difference).

### §1.3 The semantic divergences (not just renaming)

| Tier | Vocab-A (canonical) | Vocab-B (code) | Same behavior? |
|---|---|---|---|
| solo | `fail-closed` (deny on timeout) | `CONTINUE_AS_REJECT` (treat as REJECT) | **YES** — same semantics, different name |
| team | `escalate-secondary-channel` (on-call rotation) | `ESCALATE_TO_REVIEW_BOARD` (raise gate; 2nd invocation) | **NO** — secondary-channel (notify another channel) ≠ review-board (a re-invocation at a raised level). Different mechanism. |
| multi | `fail-closed` + alerting | `ABORT_WORKFLOW` (terminal) | **NO** — fail-closed (treat-as-reject + alert, workflow continues with a denied step) ≠ abort-workflow (terminal stop). **Different disposition on the compliance tier.** |

`fail-open` (vocab-A, prohibited at multi) has no vocab-B equivalent; `ABORT_WORKFLOW` (vocab-B) has no vocab-A equivalent.

### §1.4 Why Class 1

The divergence is between **CODE** and a **FOUNDATIONAL ADR** (ADR-D5) + a **cleared spec** (CP §20.6). Per CLAUDE.md §1.3 authority chain (ADR > spec > plan > code) and §10.2 (revisiting a committed surface requires Class-1 fork → ADR back-flow), the reconciliation touches a committed surface (the live code behavior AND the foundational ADR's compliance-tier posture). It is NOT a doc-hygiene nit — `ABORT_WORKFLOW` vs `fail-closed` at multi-tenant-compliance is a materially different runtime disposition on the compliance tier.

---

## §2 — Authority-chain analysis + impact on F-B3-2

### §2.1 Canonical direction (authority chain)

By CLAUDE.md §1.3 (ADR > spec > plan > code), **vocab-A is canonical** (ADR-D5 §1.6 foundational + cleared CP spec §20.6). Vocab-B is a plan-era formulation (early CP plans v2/v2.1) that the **code implemented and never reconciled** when the plan/spec converged to vocab-A. Classic plan-converged-but-code-stale drift.

### §2.2 The conservative resolution (recommended)

Reconcile **code → vocab-A**: rename `TimeoutDegradationKind` to the canonical vocabulary (`{fail-closed, escalate-secondary-channel, fail-open}`), fix the per-tier table to match CP §21.8 + ADR-D5 §1.6 (multi → `fail-closed` + alerting, NOT abort-workflow; team → `escalate-secondary-channel`), fix the wrong-section "§21.6" cite → **§21.8**. This honors the authority chain, requires **no ADR change**, and aligns the code with the CP §21.8 mode table + the §20.6 span vocabulary it must emit.

### §2.3 The alternative (ADR-D5 back-flow)

IF the operator judges vocab-B's semantics superior (e.g., `ABORT_WORKFLOW` is the right multi-tenant timeout disposition, or a `review-board` re-invocation is wanted over a `secondary-channel` notify), then ADR-D5 §1.6 must be **revised via ADR back-flow** (foundational — Class-1 → ADR amendment) to adopt vocab-B, and the CP spec §20.6 span value-set updated to match. This is the heavier path and re-opens a foundational commitment.

### §2.4 Impact on F-B3-2 (why this blocks B3-spec-2)

The design §6.2 G4b dispatch-on-kind table is written against **vocab-B** (`CONTINUE_AS_REJECT` / `ESCALATE_TO_REVIEW_BOARD` / `ABORT_WORKFLOW`). Under §2.2 (recommended), the corrected F-B3-2 must author the runtime dispatch-on-**mode** against **vocab-A**:
- `fail-closed` → route through the **REJECT** disposition (step fails as rejected) — the design's CONTINUE_AS_REJECT row, corrected name.
- `escalate-secondary-channel` → the webhook/secondary-channel escalation (composes with the **already-built** `WebhookConfig.degradation_mode ∈ {fail-closed, escalate-secondary-channel}` at `hitl_timeout_degradation.py:105` — note the WebhookConfig ALREADY uses vocab-A, a second corroboration that vocab-A is canonical) — NOT the design's heavier "review board re-invocation."
- `fail-open` → **NOT a granted mode** (the cleared authorities assign it to no tier; it appears only in the multi-tenant prohibition) → **no dispatch path**; registered as owing ADR-D5 §1.6 + CP §21.8 ratification before it could be a usable mode. (This is a distinct axis from F-B3-1's §19.5 gate-LEVEL override: §19.5 governs *whether to gate at all*; the timeout-MODE governs *what to do when a fired gate times out* — do not conflate them.)

So the corrected F-B3-2 scope is **different and likely SMALLER** than the design's vocab-B framing (the heaviest sub-surface, ESCALATE_TO_REVIEW_BOARD's "review board re-invocation," dissolves into the already-built `escalate-secondary-channel` webhook path). **F-B3-2 cannot be authored until the vocabulary is reconciled** — authoring against vocab-B would deepen the drift (X-AL-3).

**Corroboration that vocab-A is canonical:** the SAME code file (`hitl_timeout_degradation.py:105-107`) declares `WebhookConfig.degradation_mode ∈ {fail-closed, escalate-secondary-channel}` (vocab-A) for the webhook-ingress path — so the code ALREADY uses vocab-A in one place and vocab-B (the `TimeoutDegradationKind` enum) in another. The drift is internal to the code too.

### §2.5 The corrected F-B3-2 dispatch-on-mode contract (the B3-spec-2 spec deliverable)

The actual G4b fork: the runtime timeout path (§14.8.2 step 4f) currently consults nothing and **unconditionally raises** `RT-FAIL-HITL-GATE-TIMEOUT` (design §1.2 break #3). F-B3-2 replaces the unconditional raise with **dispatch on the consulted mode** (`on_hitl_timeout(persona_tier) → degradation_mode`, vocab-A). Crucially, the **two ADR/CP-granted modes** (`fail-closed`, `escalate-secondary-channel`) map onto **disposition surfaces that ALREADY EXIST** at §14.8.2 step 4i — confirming the corrected scope is SMALLER than the design's vocab-B framing (no new "review-board re-invocation loop guard"); `fail-open` is not a granted mode (see the table below):

| Mode (vocab-A) | Timeout disposition | Existing surface it routes through |
|---|---|---|
| `fail-closed` | treat the timeout as a **REJECT** (deny the step; fail-safe) | step 4i `REJECT` → raise `HITLGateRejectedError` → `RT-FAIL-HITL-GATE-REJECTED` (verbatim — the timeout enters the same rejection path) |
| `escalate-secondary-channel` | deliver the gate to the **secondary channel** (webhook) + pause/await | the already-built durable-async webhook surface §14.8.8 (`WebhookDeliveryComposer` C-RT-26 + `WebhookConfig.degradation_mode ∈ {fail-closed, escalate-secondary-channel}` at `hitl_timeout_degradation.py:105`) — NOT a new "review board" primitive |
| `fail-open` | **NOT a granted mode** — refused at all tiers | — (no dispatch path; detect-then-refuse; registered as owing ADR-D5 §1.6 + CP §21.8 ratification) |

So the design's `ABORT_WORKFLOW` row **disappears** (no vocab-A equivalent), the **two granted modes** are `fail-closed` + `escalate-secondary-channel`, and `fail-open` is a value-set token **assigned to no tier** by the cleared authorities (registered-not-granted — the decorrelated-review catch; granting it = a runtime extension needing ADR/CP ratification, X-AL-3 register-don't-extend mirroring F-B3-1). The default per-tier mapping (CP §21.8 + ADR-D5 §1.6): solo→`fail-closed`; team→`escalate-secondary-channel` (default) / `fail-closed` (configurable); multi→`fail-closed`+alerting (NEVER `fail-open`).

**B3-spec-2 spec leg** authors this dispatch-on-mode as a runtime-spec §14.8.x extension (the G4b control-flow fork; runtime v1.49→v1.50): timeout → consult `on_hitl_timeout` (G4a, the mode + the `degradation_mode_applied` audit attribute) → dispatch on the granted mode (the 2 active rows above) rather than the unconditional raise. **B3-impl-2** lands (a) the code-enum reconciliation `TimeoutDegradationKind` drifted-re-expression → vocab-A `{fail-closed, escalate-secondary-channel, fail-open}` + the per-tier table fix (multi→fail-closed) + the wrong-section §21.6→§21.8-cite fix + cross-ref updates (OD spec / CP plan / tests), and (b) the dispatch-on-mode wiring at the composer timeout path. **The `fail-open`-refused-at-all-tiers AC** (detect-then-refuse: a deployment configuring `fail-open` at ANY tier raises at config/bootstrap, never silently honored — multi is the explicit ADR/CP prohibition, solo/team are not-yet-granted; the C10 guard + X-AL-3, mirroring the F-B3-1 register-don't-extend disposition).

---

## §3 — Operator decision owed

**The genuine gate:** which reconciliation direction for the timeout-degradation vocabulary?

- **(Recommended) Reconcile code → vocab-A** (CP §21.8 + ADR-D5 §1.6 + CP §20.6 canonical) — no ADR change; corrects the code drift + the wrong-section §21.6→§21.8 cite; F-B3-2 then authors dispatch on the **2 granted modes** (`fail-closed`, `escalate-secondary-channel`); `fail-open` is registered-not-granted (assigned to no tier by the cleared authorities) (smaller scope; the review-board sub-surface dissolves into the built webhook secondary-channel path).
- **ADR-D5 back-flow to vocab-B** — revise the foundational ADR + CP §20.6 to adopt `{continue-as-reject, escalate-to-review-board, abort-workflow}` (heavier; re-opens a foundational commitment; needed only if abort-workflow@multi / review-board@team are judged superior).

The FULL-SPEC directive ("HOW stays committed ADRs") favors the recommended path (preserve the foundational ADR; fix the code drift). The reconciliation is then an impl + a thin runtime-spec authoring of the dispatch-on-mode (the actual G4b control-flow fork), against the corrected vocabulary.

---

## §4 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_b3_2_timeout_degradation_vocabulary_drift.md` |
| Arc | R-FS-1 child arc **B3** (smart-HITL), **B3-spec-2** arc-open (F-B3-2 precondition) |
| HEAD at surfacing | `bd12cfc` (post-#551 / post-refresh) |
| Surfaced by | B3-spec-2 arc-open grounding (re-ground-at-arc-open per design §8.3 + `[[built-but-vacuous-reground-ledger-asis]]`; the design's cites are leads, presence-not-correctness) |
| Authority | CP spec v1.2 **§21.8** (lines 1935-1947, the per-tier mode table) + ADR-D5 §1.6 (foundational; lines 281-287) + cleared CP spec v1.2 §20.6 (line 1821, span attr) = vocab-A canonical; `hitl_timeout_degradation.py:40` = vocab-B code drift; **wrong-section** "C-CP-21 §21.6" cite (real §21.6 = validator-span-sampling; real timeout table = §21.8); `fail-open` assigned to no tier by any authority |
| Recommendation | Reconcile code → vocab-A (no ADR change); then author F-B3-2 dispatch-on-mode against vocab-A |
| Blocks | F-B3-2 authoring (the design §6.2 vocab-B premise is falsified) |
| Next | operator ratifies the reconciliation direction → reconcile code (+ thin runtime-spec dispatch-on-mode = F-B3-2) → B3-plan → B3-impl-2 |

---

*End of F-B3-2 precondition fork. Surfaces a code↔foundational-ADR-D5 timeout-degradation vocabulary drift that reshapes (and likely shrinks) F-B3-2. Recommended: reconcile code→vocab-A per the authority chain.*
