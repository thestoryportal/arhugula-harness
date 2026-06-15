# Adversarial Review — R-FS-1 B3-spec-2 / F-B3-2 (HITL timeout-degradation dispatch-on-mode)

## Summary

- **Mode:** Phase-7 pre-implementation review (design-substrate amendment, pre-merge gate posture per SKILL §A)
- **Artifacts reviewed:**
  - `.harness/class_1_fork_b3_2_timeout_degradation_vocabulary_drift.md` (the F-B3-2 fork doc)
  - `design-substrate/Spec_Harness_Runtime_v1.md` v1.49 → v1.50 amendment (new change-note + new §14.8.9)
- **Date:** 2026-06-14 · **Branch:** `r-fs-1-b3-spec-2` · **HEAD:** `3835408`
- **Finding count:** Class-1/blocking: **0** · Class-2/substantive: **2** · Class-3/doc-hygiene: **3**
- **Highest-severity finding:** F2-01 (untagged load-bearing inference: solo-`fail-open` grant is not ADR-grounded)
- **Disposition recommendation:** **APPROVE-WITH-CLASS-2** — the spec leg is correct, X-AL-3-clean, delta-preserving, and the vocab reconciliation direction + the 3-mode→disposition mapping are sound by direct read. Two substantive sharpenings (a `[MODERATE]` tag on the solo-fail-open inference; the §19.5-auto vs timeout-mode conflation watch) + three doc-hygiene cite nits. None blocks merge.

---

## ⚠️ Class-scale disambiguation (mandatory per SKILL title-section)

This report uses the **task-caller's stated scale** (per the review prompt): **Class 1 = blocking, Class 2 = substantive, Class 3 = doc-hygiene.** That is the **§2.7.6 fork** scale. It is **inverted** from the SKILL's native **§4.1 review-severity** scale (where Class 1 = minor/drift, Class 3 = severe). Class 2 = substantive coincides in both. To avoid the conflation the SKILL warns against, every finding below leads with the caller's scale word in-line (`[BLOCKING]` / `[SUBSTANTIVE]` / `[DOC-HYGIENE]`). No finding here is blocking.

---

## What I read (re-grounded every cite by direct file read)

| Source | What I verified |
|---|---|
| `.harness/class_1_fork_b3_2_timeout_degradation_vocabulary_drift.md` (full) | The finding + ratified reconciliation + §2.5 contract design |
| `design-substrate/Spec_Harness_Runtime_v1.md` — new change-note (lines 3-17) + new §14.8.9 (lines 3765-3795) | The deliverable; read in full |
| `git diff HEAD -- design-substrate/Spec_Harness_Runtime_v1.md` | 47 insertions, 1 deletion; the sole deletion is the version-line bump |
| `git status` | ONLY the runtime spec modified + 2 untracked (`.harness/class_1_fork_b3_2_*` + unrelated `sdlc-research.md`); ZERO CP-spec/ADR/`harness-*/src` change |
| `design-substrate/ADR-D5.md` §1.6 (lines 279-289) | vocab-A `{fail-closed, escalate-secondary-channel, fail-open}`; per-tier table |
| `design-substrate/Spec_Control_Plane_v1_2.md` §20.6 (line 1821) | `degradation_mode_applied ∈ {fail-closed, escalate-secondary-channel, fail-open}` |
| `Spec_Control_Plane_v1_2.md` §21.6 (lines 1908-1922) | = "Sampling discipline for validator-failure spans" — phantom-cite confirmed |
| `Spec_Control_Plane_v1_2.md` §21.8 (lines 1935-1947) | **NEW FIND** — "Timeout-degradation mode at durable-async cells", vocab-A, matching per-tier table |
| `harness-cp/src/harness_cp/hitl_timeout_degradation.py` (lines 1-115) | `TimeoutDegradationKind` vocab-B (l.40-50); table multi→ABORT_WORKFLOW (l.78-83); docstring "C-CP-21 §21.6" (l.3, 41) + §21.8 (webhook); `WebhookConfig.degradation_mode ∈ {fail-closed, escalate-secondary-channel}` vocab-A (l.105-107) |
| runtime spec §14.8.2 step 4i (lines 3440-3445) | `REJECT`→`HITLGateRejectedError`→`RT-FAIL-HITL-GATE-REJECTED` (l.3443); `APPROVE`→proceed-to-5 (l.3441) — both exist |
| runtime spec §14.8.8 / step 4-bis (lines 3431, 3465) + §14.16 (lines 829-958) | durable-async webhook surface exists; `WebhookDeliveryComposer` carrier = **C-RT-20 §14.10.1**; factory = **C-RT-26 §14.16**; `pause_requested_flag` + `PauseResumeProtocol` |
| runtime spec §14.8 failure-mode taxonomy (lines 3557-3560) | `RT-FAIL-HITL-GATE-REJECTED` + `RT-FAIL-HITL-GATE-TIMEOUT` rows |
| `design-substrate/Persona_Document_v1.md` §10.4 (lines 242-263) | cross-axis tension clusters; the compliance-posture anchor — does NOT affirmatively grant fail-open to any tier |
| change-note lineage (lines 1, 3, 19, 35) | v1.50/v1.49/v1.48/v1.47 notes all present → delta-only preservation intact |

---

## Per-claim findings (the 9 load-bearing claims from the review brief)

### Claim 1 — Vocab-A is canonical; vocab-B is the code drift. → **CONFIRMED (decided)**
Direct read: ADR-D5 §1.6 (l.282-285) + CP §20.6 (l.1821) both use vocab-A `{fail-closed, escalate-secondary-channel, fail-open}`. Code `hitl_timeout_degradation.py:40-50` uses vocab-B `{continue-as-reject, escalate-to-review-board, abort-workflow}`. Authority chain (CLAUDE.md §1.3: ADR > spec > plan > code) makes vocab-A canonical. **The fork direction is correct.** *Strengthening corroboration the fork under-claimed:* CP **§21.8** (a SECOND in-spec vocab-A authority — see F3-01) + the code's OWN `WebhookConfig.degradation_mode` (vocab-A at l.105) = three independent vocab-A anchors vs one drifted enum.

### Claim 2 — 3-mode → existing-disposition mapping is sound. → **CONFIRMED (decided)**
Re-read each surface:
- `fail-closed`→REJECT: step 4i `REJECT` (l.3443) raises `HITLGateRejectedError`→`RT-FAIL-HITL-GATE-REJECTED`. **Exists; supports the routing.**
- `escalate-secondary-channel`→webhook §14.8.8: the durable-async webhook surface (l.3431, 3465; C-RT-20 carrier + C-RT-26 factory) with `pause_requested_flag` + `PauseResumeProtocol` is **built and exists**. The "review-board sub-surface dissolves into the built webhook path" claim is **TRUE** — there is no separate "review board" primitive anywhere in the runtime spec; `escalate-secondary-channel` genuinely routes through the already-built §14.8.8 path. **Not a new primitive.** ✓
- `fail-open`→proceed: step 4i `APPROVE` (l.3441) = proceed-to-step-5 with `step` unchanged. **Exists; supports the routing.** ✓

### Claim 3 — Per-tier default table matches ADR-D5 §1.6 byte-exactly. → **CONFIRMED (decided)**
§14.8.9 table (DEFAULT column) vs ADR-D5 §1.6 (l.282-285), byte-for-byte:
| Tier | §14.8.9 default | ADR-D5 §1.6 | Match |
|---|---|---|---|
| solo-developer | `fail-closed` | `fail-closed` | ✓ |
| team-binding | `escalate-secondary-channel` (default); `fail-closed` configurable | identical | ✓ |
| multi-tenant-compliance | `fail-closed` + alerting; `fail-open` prohibited | identical (Persona §10.4) | ✓ |
**No transcription error in the default table.** (The OVERRIDE column carries an inference — see F2-01.)

### Claim 4 — `fail-open`@multi structural-prohibition (AC-1) detect-then-refuse. → **CONFIRMED (decided)**
AC-1 (§14.8.9, l.3789): multi configuring `fail-open` MUST be refused at config/bootstrap (detect-then-refuse; typed config error; contrasting-baseline test). Grounded in ADR-D5 §1.6 ("compliance posture incompatible with `fail-open`"). Mirrors the F-B3-1 multi structural-foreclosure. **Sound** — and consistent with the `[[conformance-validator-disciplines]]` detect-then-refuse + contrasting-baseline shape.

### Claim 5 — ZERO CP-spec / ADR edit (X-AL-3). → **CONFIRMED (decided)**
`git status` + `git diff --stat`: only `Spec_Harness_Runtime_v1.md` modified + the new fork doc untracked. **ZERO** `design-substrate/ADR-D5.md`, **ZERO** `Spec_Control_Plane_*`, **ZERO** `harness-*/src` edit. The fork RECONCILES code→ADR (at B3-impl-2); it does NOT change the ADR. **X-AL-3-clean.** The amendment is a runtime-spec extension consuming the (unchanged) foundational ADR-D5 + CP §20.6.

### Claim 6 — Spec-only / inert-until-B3-impl-2. → **CONFIRMED (decided)**
§14.8.9 (l.3767) + change-note (l.5, l.17): "SPEC-ONLY — the dispatch wiring + the code-enum reconciliation land at B3-impl-2; the dispatch is inert in production until B3-impl-2 (the v1.9 §14.8.2 step-4f unconditional raise stands until then)." No `harness-*/src` edit in the diff. **The spec/impl split is honest** — this is the SPEC leg; the code still using vocab-B is *correct for this PR* (the reconciliation is explicitly B3-impl-2 / AC-2). This is NOT a silent deferral of a spec feature — the deferral is named, scoped, and carries closure ACs.

### Claim 7 — Delta-only preservation. → **CONFIRMED (decided)**
Change-notes v1.50/v1.49/v1.48/v1.47 all present (lines 3/19/35/...). The diff's ONLY deletion is the version-line bump (`v1.49`→`v1.50`). The v1.9 step-4f body (l.3432) + the failure-mode rows (l.3557-3560) are NOT edited in place — the two amendments are **canonical-reading amendments** (additive re-reads) + the additive §14.8.9. **Delta-only convention honored.**

### Claim 8 — Byte-exact cites. → **CONFIRMED with 3 doc-hygiene nits** (see F3-01/02/03)
ADR-D5 §1.6 (l.279-289) ✓; CP §20.6 (l.1821) ✓; §14.8.2 step-4i (l.3440-3445) ✓; failure-mode rows (l.3557-3560) ✓; §14.8.8 webhook surface ✓; `hitl_timeout_degradation.py:40/105` line cites ✓; phantom §21.6 ✓. Nits: F3-01 (the §21.8 omission + the over-broad "only timeout surface" clause), F3-02 (`WebhookDeliveryComposer` cited as C-RT-26 — carrier is C-RT-20 §14.10.1), F3-03 (§14.8.9 doesn't cite §21.8 as a CP-axis mode authority).

### Claim 9 — 9-item workspace pattern checklist. → **CLEAN, with one honesty win**
- **Stale-carry-text:** clean (the amendment is additive; it does not carry stale framing).
- **Sibling-spec staleness:** clean (consumes ADR-D5 + CP §20.6/§21.8 at their canonical shape).
- **Forward-cite phantom:** the amendment correctly *identifies and corrects* the code's phantom "C-CP-21 §21.6" — it does not itself introduce one. ✓
- **Plan-against-not-built:** N/A (spec leg; explicitly defers wiring to B3-impl-2 with ACs).
- **Spec-prose-vs-plan drift:** N/A.
- **Verification grep-vs-e2e:** AC-3 (l.3791) explicitly mandates e2e ("verify by execution … not a green call-site unit test", citing `[[built-but-vacuous-reground-ledger-asis]]`). ✓ Strong.
- **X-AL-3 anti-extension:** clean (Claim 5).
- **Halt-route-split-AC:** clean — the materializable spec (dispatch contract) lands now; the unmaterializable-until-impl parts (code reconciliation + wiring) are split to B3-impl-2 with named ACs. Textbook `[[halt-route-split-ac-pattern]]`.
- **Honesty win:** the design §6.2 vocab-B premise IS correctly identified as **falsified-by-grounding** (change-note l.7 names it explicitly) and the correction is honest — the amendment does NOT silently absorb the code drift; it routes the code reconciliation to B3-impl-2 / AC-2 and consumes vocab-A in the spec. **No silently-absorbed fork.**

---

## Class-2 (SUBSTANTIVE) findings

### F2-01 [SUBSTANTIVE] — Solo-`fail-open` grant is a load-bearing inference, not ADR-grounded (untagged)
- **Location:** §14.8.9 per-tier table OVERRIDE column ("solo-developer | `fail-closed` | operator may configure `fail-open`") + the `fail-open` row "**SOLO-configurable only**" (l.3786) + fork doc §2.5 row 3 ("solo-configurable only").
- **Defect:** **ADR-D5 §1.6 does not affirmatively grant `fail-open` to ANY tier.** Across all of ADR-D5 §1.6, CP §20.6, and CP §21.8, the token `fail-open` appears ONLY in the multi-tenant *prohibition* clause ("compliance posture incompatible with `fail-open`"). The solo default is `fail-closed`. The claim "solo MAY configure `fail-open`" is an **inference** ("`fail-open` is in the §20.6 value-set + it is prohibited only at multi → therefore admissible at solo"). That inference is reasonable and is the most-faithful reading, but it is **load-bearing** (the entire `fail-open`→proceed branch needs a legitimate tier to be reachable) and it is presented as if directly grounded.
- **Discriminator:** §4.1 (a) — affects substantive content of the current-phase artifact (an inference presented as grounded; the design doc itself tags comparable inferences `[MODERATE]`).
- **Resolution path:** tag the solo-`fail-open` admissibility as a `[MODERATE]` inference (mirroring the design's own `[MODERATE]` tag on the in-`max()` reading), OR add a cite to whatever surface affirmatively grants it. Do not edit the ADR. Inert-until-B3-impl-2, so non-blocking — but the inference should be surfaced before B3-impl-2 builds the solo-fail-open branch on it. *(decided — the text supports a single reading: it is an inference.)*

### F2-02 [SUBSTANTIVE] — `fail-open` rationale leans on §19.5 "auto-approve", conflating GATE-LEVEL with timeout-MODE (watch for B3-impl-2)
- **Location:** fork doc §2.5 row 3 ("the §19.5-adjacent auto-approve-on-timeout posture") + design §6.2 framing. (The v1.50 §14.8.9 text itself does NOT repeat this conflation — it cites only step-4i APPROVE-equivalent, which is correct.)
- **Defect:** §19.5 is the **operator-policy override of a `max()` GATE-LEVEL floor** (auto/ask/deny — *whether to gate*). Timeout-degradation **mode** (`fail-closed`/`escalate`/`fail-open` — *what to do when an already-fired gate times out*) is a **different axis**. Using "§19.5 auto-approve" as the *grounding* for timeout-`fail-open` conflates the two surfaces. The disposition mapping (`fail-open`→step-4i APPROVE-equivalent) is correct; the *rationale cite* to §19.5 is the soft spot.
- **Discriminator:** §4.1 (a) — substantive (a grounding-cite category error in the fork doc's rationale; could mislead B3-impl-2 into reusing §19.5 machinery for timeout-fail-open).
- **Resolution path:** in the fork doc (or carried into B3-impl-2), decouple the timeout-`fail-open` rationale from §19.5 gate-level override; ground it on the §20.6/§21.8 mode value-set + F2-01's tagged inference instead. Non-blocking (fork doc is process-substrate; the spec text is clean). *(decided.)*

---

## Class-3 (DOC-HYGIENE) findings

### F3-01 [DOC-HYGIENE] — Fork doc §1.2 "the CP spec's only timeout surface is the §20.6 span value-set" is FALSE
- **Location:** fork doc §1.2 (l.27): *"The timeout-degradation table is not authored anywhere in the CP spec as a control-flow contract; the CP spec's only timeout surface is the §20.6 span-attribute value-set (vocab-A)."*
- **Defect:** CP spec v1.2 **§21.8** ("Timeout-degradation mode at durable-async cells", l.1935-1947) IS a CP-spec timeout surface — a per-persona-tier mode TABLE in vocab-A, matching ADR-D5 §1.6 byte-for-byte. The clause "the only timeout surface is §20.6" is **incorrect**. (The adjacent clause "not authored … as a control-flow contract" is defensible — §21.8 is a mode/policy table, not runtime control flow — so scope the correction to the "only … §20.6" clause; don't over-broaden.) **This error makes the fork's conclusion STRONGER, not weaker** — §21.8 is a third independent vocab-A authority. But the factual claim is wrong and should be corrected so a downstream reader doesn't trust "only §20.6."
- **Discriminator:** §4.1 (a/b/c miss) — drift only; a factual mis-statement in a process-substrate doc that does not change the (correct) conclusion.
- **Resolution path:** correct fork doc §1.2 to acknowledge §21.8 as a (corroborating) CP-axis vocab-A mode surface. Inline fix.

### F3-02 [DOC-HYGIENE] — `WebhookDeliveryComposer` cited as "C-RT-26"; the carrier contract is C-RT-20 §14.10.1
- **Location:** §14.8.9 escalate-secondary-channel row (l.3785: "`WebhookDeliveryComposer` C-RT-26") + fork doc §2.5 row 2 (same cite).
- **Defect:** The `WebhookDeliveryComposer` **carrier class** is **C-RT-20 §14.10.1** (verified l.590, l.835, l.1148). **C-RT-26 §14.16** is the *binding-chain factory* (`materialize_webhook_delivery_composer_stage`), not the composer itself. The routing claim is unaffected (both contracts are real and both are part of the webhook surface), so this is purely a contract-number imprecision on the carrier.
- **Discriminator:** §4.1 (a/b/c miss) — drift only.
- **Resolution path:** cite "`WebhookDeliveryComposer` C-RT-20 §14.10.1 (+ C-RT-26 §14.16 binding-chain factory)". Inline fix.

### F3-03 [DOC-HYGIENE] — §14.8.9 reproduces §21.8's table verbatim but does not cite §21.8
- **Location:** §14.8.9 "Canonical vocabulary (vocab-A)" + per-tier table (l.3777-3783); change-note "Source of fix" (l.7).
- **Defect:** The §14.8.9 per-tier table is byte-identical to CP **§21.8**, yet the cite chain names only ADR-D5 §1.6 + CP §20.6. §21.8 is the most on-point CP-axis *mode* authority (§20.6 is the *span value-set*; §21.8 is the *per-tier mode table*). Citing it would tighten the grounding.
- **Discriminator:** §4.1 (a/b/c miss) — drift only (a strengthening cite omission).
- **Resolution path:** add CP §21.8 to the §14.8.9 vocabulary-authority cite (alongside ADR-D5 §1.6 + CP §20.6). Inline fix.

---

## Findings considered and rejected (transparency)

1. **X-AL-3 silent design extension (A8 framing-contamination)** — checked: ZERO ADR/CP-spec/src edit; the amendment consumes the unchanged foundational ADR. Clean.
2. **Phantom-cite introduction (A4 / checklist #3)** — checked: the amendment *corrects* the code's phantom §21.6; it introduces none. The new §14.8.9 cites resolve (modulo the F3-02/03 nits). Clean.
3. **Per-tier default-table transcription error** — checked byte-for-byte vs ADR-D5 §1.6: exact match. No error.
4. **Disposition-surface non-existence** — checked: step 4i REJECT/APPROVE (l.3441/3443) + §14.8.8 webhook (l.3431/3465) all exist and support the claimed routing. No phantom surface.
5. **Silent deferral of a spec feature** (smoothing FM-G) — checked: the code-reconciliation deferral to B3-impl-2 is named, scoped, and carries closure ACs (AC-2/AC-3); the spec leg fully authors the contract. Honest split, not a hidden gap.
6. **sync-cell → escalate-secondary-channel → §14.8.8 cross-over hole** — checked: §14.8.9 "Deferred to impl discretion" (l.3794) explicitly handles the unbound-webhook/pause-composer case ("`escalate-secondary-channel` degrades to `fail-closed` — the safe fallback"). Handled.
7. **Delta-only body-edit violation** — checked: the only deletion is the version-line bump; v1.9 step-4f body + failure-mode rows preserved verbatim; amendments are additive/canonical-reading. Clean.
8. **Halt-route-split-AC mis-application** — checked: materializable (the dispatch contract) lands now; unmaterializable-until-impl (code reconcile + wiring) split with ACs. Correct application, not a defect.
9. **`fail-open`@multi prohibition under-specified** — checked: AC-1 is detect-then-refuse at config/bootstrap with a mandated contrasting-baseline test, grounded in ADR-D5 §1.6. Adequately specified.
10. **Author-mode drift in this report** — self-audit: all resolution paths describe the *shape* of resolution (tag / cite / correct-the-clause), no verbatim replacement text supplied.

---

## Disposition

**APPROVE-WITH-CLASS-2.** The B3-spec-2 / F-B3-2 deliverable is correct, X-AL-3-clean, delta-preserving, and the keystone claims (vocab-A canonical; 3-mode→existing-disposition mapping; per-tier default table byte-exact; fail-open@multi structural prohibition; spec-only/inert split) all hold by direct read. No blocking finding.

Two **substantive** items to address before/at B3-impl-2 (neither blocks this PR merge):
- **F2-01** — tag the solo-`fail-open` admissibility as a `[MODERATE]` inference (it is not affirmatively granted by ADR-D5 §1.6; it is inferred from the value-set + multi-only prohibition).
- **F2-02** — decouple the timeout-`fail-open` rationale from §19.5 (gate-level ≠ timeout-mode); the v1.50 spec text is already clean, this is a fork-doc rationale fix carried to B3-impl-2.

Three **doc-hygiene** cite nits (inline fixes; none change a conclusion):
- **F3-01** — fork doc §1.2 "only §20.6 timeout surface" is false (§21.8 exists; corroborates vocab-A).
- **F3-02** — `WebhookDeliveryComposer` is C-RT-20 §14.10.1 (C-RT-26 is the factory).
- **F3-03** — §14.8.9 should cite CP §21.8 as the per-tier mode authority.

**No §2.7.6 Phase-7 fork results** from this review — all findings resolve within the current artifacts (spec text + fork doc) without upstream-phase revision.
