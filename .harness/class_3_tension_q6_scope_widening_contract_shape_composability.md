# Class 3 Tension — Q6 scope-widening: contract-shape composability surface

**Status.** FILED (informational; non-blocking per `Project_Workflow_v1_8.md` §2.7.6 Class 3).

**Filed at.** 2026-05-21 alongside `class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch.md` RATIFICATION (HEAD ≈ this commit). Operator Q6 disposition at the architect-recommendation AskUserQuestion turn: "File Class 3 informational addendum now."

**Class.** **3 (informational)** per `Project_Workflow_v1_8.md` §2.7.6 — observation requiring documentation; non-blocking. This record does NOT halt Phase 7 execution; it widens the scope of an already-pinned Q6 follow-on arc.

---

## 1. Observation

The c_rt_18 span-attribute-carrier-drift fork (RATIFIED at HEAD `95a9436`) surfaced a Q6 systemic-pattern observation: 4 adversarial-review-missed defects at U-RT-58/59/60 sequence, all at CP↔runtime cross-axis attribute / binding surfaces. The Q6 disposition pinned **3 skill-body extensions** scoped to **attribute-name** discipline:

1. `harness-adversarial-reviewer` — carrier-vs-narrative attribute-name diff at pre-impl review
2. `phase-7-implementation` Step 2 — attribute-name cross-check against canonical carrier before composer code lays down
3. `spec-writer` — carrier-diff at any spec revision touching attribute names

The U-RT-60 wrap-asymmetry sync/async mismatch fork (`class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch.md`, RATIFIED 2026-05-21 at HEAD ≈ this commit) is the **5th adversarial-review-missed defect** at U-RT-58/59/60 sequence — but the **first contract-shape-composability defect**, not an attribute-name defect.

**None of the 3 attribute-name-scoped Q6 extensions would catch a contract-shape-composability defect at pre-impl review.** Counter-factual analysis at the architect recommendation (§2 Q6 of the wrap-asymmetry fork record):

- (a) `harness-adversarial-reviewer` carrier-diff — NO. Catches narrative-vs-carrier drift on attribute names; not wrap-chain composability.
- (b) `phase-7-implementation` Step 2 attribute-name cross-check — PARTIAL. Would catch it only if Step 2 were extended to "verify cited wrap chain is materializable at the target stack's sync/async surface" — current Q6 articulation is attribute-name-only.
- (c) `spec-writer` carrier-diff at attribute revision — NO. Wrap-asymmetry was authored at v1.9 spec growth (before partial impl), not at a spec revision.

## 2. Recommended scope-widening

Per the architect mode 3 recommendation §7.2 Q6 [MODERATE-HIGH], Q6 extension scope must widen from **attribute-name** to **contract-shape composability** at the same 3 skill surfaces:

| Skill | Currently-pinned extension (attribute-name) | NEW extension (contract-shape composability) |
|---|---|---|
| `harness-adversarial-reviewer` | At pre-spec-clearance + pre-impl review: carrier-vs-narrative attribute-name diff between cited canonical CP carrier and spec narrative attribute references | At pre-spec-clearance + pre-impl review of any contract declaring a wrap chain across previously-landed wrappers: verify sync/async posture of each layer + inner-call shape of the outer layer (e.g., `async def dispatch` strictly `await self.inner.dispatch(...)` requires async inner) + Protocol satisfaction at registry boundary |
| `phase-7-implementation` Step 2 | Cited-spec attribute-name cross-check vs canonical carrier; halt before composer code if narrative ↔ carrier divergence detected | **Wrap-chain composability check:** for every cited wrap chain in the spec contract, verify each layer's sync/async posture matches the inner-call shape of its outer layer; halt before stage-N wiring if mismatch detected |
| `spec-writer` | At any spec revision touching attribute names, mandate canonical-carrier diff | **Composability declaration:** at any spec authoring declaring a wrap chain (e.g., spec §14.8.1 wrap-asymmetry table), mandate explicit sync/async posture statement for each layer + verify against landed wrapper inner-call shapes (or note "future-arc commitment" if wrapper not yet landed) |

## 3. Empirical pattern reinforcement (5 cases across U-RT-58/59/60)

| # | Fork | Defect class | Adversarial-review pre-impl? | Q6 attribute-name extension catches? | Q6 contract-shape-composability extension catches? |
|---|---|---|---|---|---|
| 1 | U-RT-58 retry-attribute drift (`fork-cp-3-retry-breaker-composer-underspec`) | Attribute name + composer scope | Missed | YES (carrier-diff) | YES |
| 2 | U-RT-59 CP→OD audit-write gap (`class_1_tension_u_rt_59_cp_to_od_audit_write_gap`) | Cross-axis composition + converter homing | Missed | PARTIAL | YES (wrap-chain ↔ cross-axis edge check is composability adjacent) |
| 3 | C-RT-18 AskUserQuestion H_E binding mechanism (`class_1_tension_c_rt_18_ask_user_question_surface_binding_mechanism_underspec`) | Binding-mechanism category under-spec | Missed | NO (no attribute name involved) | PARTIAL (mechanism category is composability-adjacent; depends on extension definition) |
| 4 | C-RT-18 span attribute carrier drift (`class_1_tension_c_rt_18_hitl_span_attribute_carrier_drift`) | Attribute name (hand-coded vs canonical carrier) | Missed | YES (carrier-diff — exactly the defect that drove Q6 extension) | YES |
| 5 | C-RT-18 wrap-asymmetry sync/async mismatch (`class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch`) | Contract-shape composability (sync HITL inner of async retry inner-await) | Missed | NO | YES (this exact extension) |

**Pattern observation:** the attribute-name-only Q6 extension catches 2 of 5 fully + 1 partially; the proposed contract-shape-composability extension catches 5 of 5. **Scope-widening is well-founded.**

## 4. Routing

- **Class 3 informational** per `Project_Workflow_v1_8.md` §2.7.6. Does NOT block Phase 7 execution.
- **Q6 follow-on arc** ownership stays with the operator (per the c_rt_18 span-attr-carrier-drift fork Q6 disposition — operator-scheduled independently of U-RT-60 resumption). This record amends the Q6 scope; it does NOT shift the scheduling.
- **Implementation skill-body edits** are authored at the Q6 follow-on arc, not now. The three skill files at `.claude/skills/{harness-adversarial-reviewer,phase-7-implementation,spec-writer}/SKILL.md` receive the NEW extension columns from §2 above.
- **Re-evaluation trigger.** If a 6th adversarial-review-missed defect surfaces at U-RT-58/59/60 (or subsequent runtime / CP / OD axis work) BEFORE the Q6 follow-on arc lands, file a NEW Class 3 record cataloguing the defect class + counter-factual analysis against both attribute-name AND contract-shape-composability extension definitions. If the 6th defect is neither — widen Q6 scope again.

## 5. Cross-references

- `class_1_tension_c_rt_18_hitl_span_attribute_carrier_drift.md` §7 (Q6 originating disposition; 3 extension surfaces pinned)
- `class_1_tension_u_rt_60_wrap_asymmetry_sync_async_mismatch.md` §2 Q6 + §7.2 Q6 (counter-factual analysis at architect recommendation time + scope-widening recommendation)
- `Project_Workflow_v1_8.md` §2.7.6 (Class 3 informational routing)
- Workspace `CLAUDE.md` §4.3 ("Silent absorption of design-phase defects is the worst failure mode") — Q6 extensions are the meta-discipline that closes the silent-absorption surface upstream of fork-filing

## 6. Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-21 alongside wrap-asymmetry fork RATIFICATION |
| Filed by | systems-architect mode 3 recommendation (Q6 disposition; operator-ratified) |
| Status | FILED (Class 3 informational; non-blocking) |
| Resolution target | Q6 follow-on arc landing (operator-scheduled independently) |
| Re-evaluation trigger | 6th adversarial-review-missed defect surfacing pre-Q6-follow-on landing OR Q6 follow-on arc opening |

---

*End of Class 3 record. Status: FILED. Operator schedules Q6 follow-on arc independently; this record widens the scope ratified at that arc to include contract-shape composability alongside attribute-name discipline.*
