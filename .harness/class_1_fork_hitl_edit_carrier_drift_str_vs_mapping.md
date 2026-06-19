# Class 1 fork — HITL EDIT carrier drift (`str` ask-surface ↔ `Mapping` step_payload)

**Status:** ✅ **RESOLVED 2026-06-19 by the R-FS-1 standalone arc `B-EDIT-CARRIER`** (was FILED + INTERIM-LANDED 2026-06-14 at B3-impl-3 / U-RT-120, D-edit.B). The §4 follow-on BUILD arc has LANDED: functional operator EDIT applies (runtime spec **v1.62** §14.8.2 step 4i + NOTE 6-ii amended; clearance `.harness/clearance/Spec_Harness_Runtime-v1_62-cleared-2026-06-19.md`). **Mutation discipline = (A) JSON-decode-then-replace** — the cleared constraints (flat-`str` MCP-elicitation carrier + committed replace-not-merge mandate + arbitrary-nested `step_payload`) foreclose to (A); (B) cannot carry arbitrary nesting, (C) would override replace-not-merge. (A) PRESERVES the committed decision → no operator gate (probe-resolved; FULL-SPEC pre-authorized; the §2/§4 "operator ratification" framing predates the 2026-06-12 FULL-SPEC directive). The interim `HITLGateEditCarrierDriftError` is RETIRED; the new `RT-FAIL-HITL-GATE-EDIT-DECODE` taxonomy code (§14.8) fires only when the operator `str` is not a JSON object. `edited_proposal_hash` is now the POST-mutation payload hash (closes reviewer F3-03). Disposition **D-edit.B** ratified at the cleared B3 design doc `.harness/r-fs-1-b3-smart-hitl-design-v1.md` §5; B3-impl-3 landed the interim honest raise; this arc is the workflow-mutation-discipline arc §4 registered.

**Filed:** 2026-06-14, B3-impl-3 (U-RT-120) implementation arc — empirical orientation at HEAD `16a4758`.
**Authority anchor:** workspace `CLAUDE.md` §4.3 Class 1 routing + §4.4 X-AL-3 silent-absorption discipline; FULL-SPEC directive ([[feedback-full-spec-beyond-mvp-nothing-deferred]]) — every deferred capability is a BUILD arc, design back-flow PRE-AUTHORIZED.
**Workspace precedent:** sibling HITL carrier drift `.harness/class_1_tension_c_rt_18_hitl_span_attribute_carrier_drift.md` (same HITL surface; Class 1). Disposition pattern `[[halt-route-split-ac-pattern]]` (partial-land the materializable half + route the rest). Surfacing precedent — the runtime-shape new fail class — `HITLCellExcludedError` (`hitl_gate_composer.py`).

---

## §1 The gap — a runtime↔CP carrier drift, not a "string payload assumption"

§14.8.2 step 4i `EDIT` branch + NOTE 6-ii (runtime spec, lines 3442 + 3534) mandate **replace-not-merge**:

> step 4i: "`EDIT`: mutate `step` per `gate_result.edited_proposal` (v1.9 MVP shape: the edited proposal replaces `step.step_payload` …); proceed to step 5 with mutated step."
>
> NOTE 6-ii: "v1.9 MVP shape mutates `step.step_payload` by replacement (the edited proposal becomes the new step_payload **verbatim**). … richer mutation (field-level patches, type-aware merging, multi-version-history-tracking) is deferred to a future workflow-mutation-discipline arc. … v1.9 implementations MUST replace-not-merge; consumers MUST treat `gate_result.edited_proposal` as authoritative replacement."

The mandate presumes a **structured** carrier. The CP-canonical gate envelope is `harness_cp.hitl_placement.HITLGateResult.edited_proposal: Mapping[str, Any] | None` (hitl_placement.py:197), and `WorkflowStep.step_payload` is itself `Mapping[str, Any]` (opaque per C-CP-25 §25.3.3.4). So "replace `step_payload` verbatim" is, in the CP world, the trivial `step.model_copy(update={"step_payload": edited_mapping})`.

**The drift.** The wired runtime ask-surface does NOT return a `Mapping`. It returns:

- `AskUserQuestionResult.edited_proposal: str | None` (ask_user_question_surface.py:86), and
- `AskUserQuestionElicitationSchema.edited_proposal: str | None` (mcp_backed_ask_user_question_surface.py:197).

The elicitation schema is `str` **by necessity**: MCP elicitation (`modelcontextprotocol` spec 2025-06-18) requires *"flat objects with primitive properties only"* (docstring, mcp_backed_ask_user_question_surface.py:171-199). It **cannot** deliver a nested `Mapping[str, Any]`. So the structured-elicitation path that would make this plain IMPL (design doc **D-edit.A**) is **unreachable through the wired path** — the elicitation surface is itself flat-`str` constrained.

Therefore replacing a `Mapping` `step_payload` with an operator-supplied **`str`** "verbatim" is genuinely under-specified: NOTE 6-ii's "verbatim" presumes the structured CP carrier that the runtime `str` carrier drifted from. Resolving it requires **minting decode / mutation semantics the cleared spec explicitly DEFERS** ("a future workflow-mutation-discipline arc").

## §2 Candidate mutation disciplines (the follow-on arc decides; NOT pre-decided here)

Per `[[adr-vs-fork-spec-plan-granularity]]` "B3 gaps = fork-don't-resolve." The readings are enumerated for the follow-on arc + operator ratification; B3-impl-3 does NOT pick among them.

- **(A) JSON-decode the operator `str` → `Mapping`, then replace-not-merge.** Mirrors the IMPL-discretion convention already landed for the *tool-args* HITL surface at `r_cxa_2_producer_loop_factory._parse_edited_arguments` (`json.loads` + "must be a JSON object" guard). **Pros:** functional EDIT; one landed precedent in-repo. **Cons:** the precedent has **no cleared-spec backing for the step-payload surface** (grep of `design-substrate/` for `_parse_edited_arguments` / "JSON object of tool arguments" → empty); applying it here mints mutation semantics → would be X-AL-3 if done silently at execution; step_payload for an `INFERENCE_STEP` is a full `ProviderAgnosticPayload` (messages/tools/params) — asking the operator to retype the whole structure as JSON is a heavy + error-prone ask; needs a typed-failure path for invalid-JSON / non-Mapping.
- **(B) Structured-flat elicitation — typed-field EDIT.** Extend the elicitation schema with flat typed fields the operator edits individually (within MCP's primitive-only constraint), then reassemble into the `Mapping`. **Pros:** stays inside MCP flat-schema; typed. **Cons:** can only edit a fixed flat field-set; can't express arbitrary nested payload edits; couples the elicitation schema to step_payload shape.
- **(C) Richer mutation — field-level patches / type-aware merge.** The full NOTE 6-ii deferred family (patches, type-aware merging, multi-version history). **Pros:** most expressive. **Cons:** largest scope; needs a patch grammar + audit-diff discipline (the `edited_proposal_hash` "post-mutation payload hash, not the diff" note interacts here).

## §3 The interim landing (B3-impl-3, U-RT-120) — what shipped now

Under D-edit.B, B3-impl-3 lands the **honest typed raise**, not the silent drop:

1. **`HITLGateEditCarrierDriftError(Exception)`** (`hitl_gate_composer.py`) — docstring docks to this fork; surfaces as **RuntimeError-shape** to the driver (the `HITLCellExcludedError` precedent), **NOT** pre-registered into the §14.8 `RT-FAIL-*` taxonomy. The carrier-healing arc (§4) owns the eventual taxonomy registration when functional EDIT lands.
2. **Step 4i `EDIT` branch** raises it (replacing the prior `pass`). The **prior `pass` was silent non-compliance** — it accepted EDIT then dispatched the step *unchanged*, dropping the operator's edit in violation of "consumers MUST treat `edited_proposal` as authoritative replacement." The audit at step 4h still records the operator's edit faithfully (`edited_proposal_hash` over the operator `str`) **before** the raise — symmetric to the REJECT path's rejection-audit preservation.
3. **Contrasting-baseline test** `test_edit_str_carrier_drift_raises_no_silent_dispatch` asserts the silent-drop is GONE (`inner.calls == []`), the typed raise fires, and the audit fact is preserved. APPROVE / REJECT / RESPOND branches unchanged (regression-safe).

This satisfies the cleared mandate's *intent* (no silent drop, no silent absorption) without minting the deferred mutation semantics.

## §4 Follow-on BUILD arc (REGISTERED — live forward work, NOT a defer)

**Arc:** *HITL EDIT carrier-healing / structured-edit workflow-mutation-discipline.* Scope: (a) pick the mutation discipline (§2 A/B/C) with operator ratification; (b) amend runtime spec NOTE 6-ii (and/or mint a structured-edit contract); (c) land **functional** EDIT (replace-not-merge actually applies); (d) register the `RT-FAIL-*` taxonomy code + retire `HITLGateEditCarrierDriftError`'s interim runtime-shape surfacing; (e) resolve the **`edited_proposal_hash` "post-mutation payload hash" semantics for the no-mutation interim** — at this arc the raise pre-empts mutation, so the hash is over the operator's *pre-mutation* `str` (reviewer F3-03); the carrier-healing arc makes the mutation real, restoring NOTE 6-ii's post-mutation-hash framing. This is a design-substrate amendment arc (it WILL edit `design-substrate/` and carry this fork doc as its X-AL-3 back-flow + a clearance marker).

**Sequencing.** **Registered as a live forward arc — `B-EDIT-CARRIER` at `.harness/beyond-mvp-capability-boundary-ledger.md` (the R-FS-1 SPINE inventory; sibling to `B-INTERSTEP` + `B-FANOUT-PAUSE`, the other implementation-surfaced forward arcs)** → roadmap §5 R-FS-1 (the SPINE is roadmap §5's authoritative child-arc inventory per `Project_Roadmap_v1.md` §5 R-FS-1 `notes`). Sequenced behind the remaining R-FS-1 child-arc order (B3 → E → B2 → R → B4 → CA → B5 → B6 → B7 → M per `.harness/r-fs-1-b3-smart-hitl-design-v1.md` §8); currently queued at the tail — pull-forward is the operator's call. Per the FULL-SPEC directive this arc is a committed BUILD — functional operator EDIT is in scope for R-FS-1, **not deferred indefinitely** (EDIT ships non-functional / raises only until this arc lands).

---

## §5 Filing footer

| Field | Value |
|---|---|
| Fork class | Class 1 (under-specification → design-substrate artifact revision required at the follow-on arc) |
| Filed at | B3-impl-3 (U-RT-120), 2026-06-14, HEAD `16a4758` |
| Disposition | D-edit.B (ratified at cleared B3 design doc §5; advisor-reconfirmed) |
| Interim landing | `HITLGateEditCarrierDriftError` typed raise at §14.8.2 step 4i (this arc) |
| Design-substrate touched this arc | NONE (Phase-7 posture: harness-runtime/src + tests + this `.harness/` fork doc only) |
| Follow-on arc | HITL EDIT carrier-healing / structured-edit mutation-discipline (§4) — registered live forward work |
| Authority | workspace `CLAUDE.md` §4.3 + §4.4; FULL-SPEC directive; `.harness/r-fs-1-b3-smart-hitl-design-v1.md` §5 |
