# R-FS-1 Final-Closure Program — the last two arcs (operator-AUTHORIZED 2026-06-22)

*Process-substrate. The methodical design→build plan for the two committed-invariant-amendment arcs the operator authorized for the R-FS-1 full-spec build. Operator decision 2026-06-22: build BOTH (declined the "declare build-complete now" option) → genuine full-spec closure per the standing FULL-SPEC directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]`). **NOTE: these two builds are necessary but NOT sufficient for closure — the `closure_gate.py` G1.1 gate is `registered + gated == 0`, and one `gated` arc (`B-TAIL-CONDITIONAL-SAMPLING`) also requires disposition (see Done definition below). On all THREE dispositioned, R-FS-1 resolves and the R-CL-Q1 quality track admits.***

## Gate status

Both arcs were `operator_gated` because each SACRIFICES a committed design invariant (not a deferred capability — a deliberate omission protecting an invariant). The operator AUTHORIZED both invariant changes on 2026-06-22. The gate is therefore CLEARED *in principle*; the SPECIFIC amendment mechanism for each is still designed-then-ratified per the pipeline below (the operator authorized the direction; the council designs the safest/cleanest mechanism and surfaces residual tensions for a focused ratification before the spec amendment lands).

## Shared pipeline (per arc — committed-invariant-amendment discipline)

Each arc is a full design-first cycle, NOT impl-to-cleared-spec:

1. **Council** (`/council-workflow` or a dyadic convening) — resolve the nameable cross-domain tension + design the amendment mechanism. Dyadic default (§10.9): probe-first, pre-bind to current spec versions at session-start, surface the TENSION before the mechanism.
2. **Operator ratification of the mechanism** — a focused AskUserQuestion on the SPECIFIC design (e.g. opt-in shape, scope limits, audit posture), not the direction (already authorized). Required for the safety-sensitive arc (b); recommended for (a).
3. **Spec amendment** (`spec-writer`) — write the amendment into the canonical spec with change-note + version bump + clearance marker. This is the X-AL-3 explicit-extension that makes the build legal.
4. **Implementation** (`phase-7-implementation`) — build with FULL-CHAIN witnesses (`[[full-chain-witness-not-half-proofs]]`), negative controls, and a proof the DEFAULT (non-opted) path is byte-identical.
5. **Decorrelated review** — `harness-adversarial-reviewer` (pre-merge red-team) + out-of-family Codex on the diff + advisor (transcript-aware). High blast radius (committed-invariant change) → the full triad, reconcile-to-zero.
6. **PR + merge + §12.2 terminating refresh** (the §12.2.1 fixed point).

Each arc may be one bundled-absorption PR (§11.4) or a design/spec PR + impl PR, decided at arc-open after the council.

---

## Arc (b) — `B-HITL-PLACEMENT-PER-STEP-LOOSEN`  [SEQUENCE: FIRST]

**Why first:** CP-axis-contained (a per-step placement carrier + the `fold_step_hitl_placements` change + a monotone-posture amendment); smaller blast radius; establishes the amendment rhythm before the larger cross-axis arc (a). *(Adjustable — operator may flip to do (a) first for capability value.)*

- **Committed invariant being amended:** monotone-HITL — per-step overrides only TIGHTEN, never loosen (the §17.1 "all cells" safety floor; the §19.1 `max()`-over-rank gate-level posture; `per_tool`/`mcp_trust` "NEVER overridden" U-CP-91; the v1.49 fold built ADD-only by construction). *(spec-writer verifies byte-exact at amendment.)*
- **Nameable tension (council):** **C10 action-safety / blast-radius ⊥ C11 operator-loop / local-deployment** — the exact §13.4 worked-example dyad. Human-oversight floor vs per-step ergonomics (skip a gate on a known-safe step → less approval fatigue).
- **Candidate amendment shape (council to refine + operator to ratify):** an OPT-IN, removal/replace-capable per-step placement carrier (a `removed_positions` set or a `replace`-mode discriminator); gate-removal/loosening LOGGED to the audit ledger (no silent oversight drop); HARD scope limits (e.g. `mcp_trust` / `per_tool` floors stay non-removable; possibly only operator-classified-safe positions removable). The monotone floor stays the default for every non-opted workflow.

### Council-vetted design (2026-06-23 — C10⊥C11 dyad + advisor red-team; spec-writer input)

Genuine dyadic council (C10 action-safety + C11 operator-loop as dedicated agents, independent → cross-read) + advisor red-team, all byte-exact-grounded. The candidate sharpened materially; **the genuinely-new surface is much NARROWER than "per-step loosen any gate":**

- **§19.5 OVERLAP (lead this at ratification — C11):** the workspace ALREADY shipped `HITLAutoApprovePolicy` (U-CP-91 / CP §19.5; `harness-runtime/.../lifecycle/hitl_auto_approve_policy.py`) — a gate-LEVEL loosening that lowers persona/blast floor cells to AUTO so an existing `PRE_ACTION` gate computes AUTO + skips (solo-only, auto-audited, hard floors preserved). This already relieves the most common over-gating case (PRE_ACTION on a read-only/local-mutation step at solo). So broad-"b" is mostly already built; the genuinely-new slice is small.
- **Loosenable set = `{SUB_AGENT_BOUNDARY}` ONLY (forced, not a choice):** (1) `PRE_ACTION` is **structurally excluded** — C10's file:line-grounded bypass-seam finding: `PRE_ACTION` is the §19.1 `_hitl_required` call-site that evaluates the mcp_trust/per_tool/blast-radius floors (`hitl_gate_composer.py` ~:80-82; §17.1 table `Spec_Control_Plane_v1_2.md:1478`), so removing/narrowing it deletes the floor-evaluation site → the U-CP-91 floors stay intact-but-UNCONSULTED (`[[enforce-floor-no-bypass-seam]]`). Make it unrepresentable in the carrier (a `LoosenablePlacementKind` enum that excludes PRE_ACTION), not a runtime guard — this is the spec JUSTIFICATION, not a preference. (2) `VALIDATOR_ESCALATION` is **already foreclosed at the wrap-time composer** ("Foreclose VALIDATOR_ESCALATION per Q5 ratification", `hitl_gate_composer.py:74,242-246`) — it does NOT fire a wrap-time gate (it fires via the §14.15 validator-outcome re-entry path), so a wrap-time placement removal is a no-op/wrong-layer. Register VALIDATOR_ESCALATION-path loosening as a follow-on only if a real need appears.
- **Remove-not-replace (both voices):** a typed named-position **removal** (`removed_positions: frozenset[LoosenablePlacementKind]`), NOT attribute-tuning — a `tool_filter`-narrowing REPLACE silently ungates other tools while the position still reads "present" (the v1.49 docstring's named footgun). All-or-nothing removal is loud/greppable/schema-visible.
- **Floor-clamp is LOAD-BEARING (advisor Check 1 — verified NOT vacuous):** the `SUB_AGENT_BOUNDARY` composer (`c_rt_17`, host-less) DOES compute `gate_level()` with blast_radius + per_tool floors when its placement matches (`hitl_gate_composer.py:80-82,465-471`), so removing a SUB_AGENT_BOUNDARY gate on a high-blast dispatch WOULD bypass those floors → the fold must **refuse/clamp** a removal when the step's resolved blast_radius (or per_tool) floors the gate to ASK/DENY (the decline-mirror, `[[gate-enforcement-site-and-timing-asymmetry]]`). This converges with C11's "removable only when resolved `blast_radius_tier ∈ {read-only, local-mutation}`" scope. Blast-radius is re-resolved per-step at composition (the composer's `blast_radius_resolver`), so a dispatch that resolves higher is re-floored automatically (bounds classification-drift).
- **Persona-tier floor (C11, load-bearing — mirror §19.5 verbatim):** `solo-developer` PERMITTED; `team-binding` = **registered follow-on** (multi-operator accountability semantics — don't silently drop); `multi-tenant-compliance` **structurally foreclosed** (the composer never applies the knob at this tier, mirroring `hitl_gate_composer.py:1416-1417`).
- **Auto-audited, fail-CLOSED, NO operator prose (both voices reconciled):** every applied removal auto-emits a non-vacuous audit entry at the fold/compose site (mirror the §19.5 skip-audit), `raise_on_failure=True` → a removal NEVER goes live un-audited (C10: audit is the only remaining containment for a removed preventive gate). REJECT per-removal justification text / manual per-position classification as usability-defeating shelf-ware (C11: it relocates friction; the §19.5 precedent works because audit is automatic).
- **Opt-in, default byte-identical:** absent the carrier, `fold_step_hitl_placements` stays ADD-only verbatim (the negative-control the closure plan demands).
- **Verification bar:** witness BOTH the add (still works) AND the remove/replace (the new capability) by-execution; a negative control proving the default path is byte-identical + monotone; a witness that a removed gate is AUDITED; a witness that the non-removable floors (mcp_trust/per_tool) reject removal.
- **Footgun to design out:** a misconfigured workflow silently dropping human oversight on a step that mattered. The mechanism must make gate-removal LOUD (typed, audited, scope-limited), never an accidental side-effect of an override.

---

## Arc (a) — `B-POSTJOIN-LLM-SYNTHESIS`  [SEQUENCE: SECOND]

- **What it builds:** an LLM-dispatched synthesis step that runs after a concurrent fan-out (ORCHESTRATOR_WORKERS / PARALLELIZATION / HIERARCHICAL_DELEGATION) completes — reads the sibling worker outputs and composes a synthesized result via a model call (the canonical orchestrator-workers "orchestrator synthesizes" shape the deterministic fold currently omits).
- **Committed invariant being amended:** C-CP-25 §25.12 deterministic composition — the aggregation is a PURE function of the branch-index-ordered worker set (`_aggregate_orchestrator_workers` / `_aggregate_parallelization`; "first-to-finish-wins is forbidden"). An LLM synthesis makes the COMPOSITION non-deterministic. *(spec-writer verifies byte-exact at amendment.)*
- **Nameable tension (council):** determinism / reproducibility / replay-integrity / hash-chain (C-axis reliability + replay + audit voices, e.g. C1 orchestration ⊥ a CP-reliability/replay voice) ⊥ canonical-synthesis capability-completeness.
- **Candidate amendment shape (council to refine):** an OPT-IN synthesis step/mode; the deterministic fold stays the DEFAULT, byte-identical; the non-determinism is DOCUMENTED in the §25.12 contract + surfaced in replay/hash semantics (a synthesized aggregate is not a pure function of inputs → the replay/audit caveat is explicit, not silent). Likely a new `StepKind` or a post-join dispatch on the fan-out strategies, gated behind an opt-in flag.
- **Cross-axis surface:** CP (the synthesis dispatch + the §25.12 amendment) + runtime (the LLM dispatch through the real provider; the inter-step channel becomes the non-vacuous CONSUMER that `B-INTERSTEP-NONLINEAR` lacked — recording sibling outputs is now non-hollow because this synthesis step READS them). Replay (§14.23) + hash-chain implications must be reasoned about explicitly.
- **Verification bar:** full-chain witness through the REAL dispatcher (synthesis step receives the actual sibling outputs + a model composes them — no proxy); the DEFAULT deterministic-fold path proven byte-identical; the replay/hash behavior under synthesis documented + tested (what a resumed synthesized run does).
- **Composition note:** this arc is what makes `B-INTERSTEP-NONLINEAR`'s recording non-hollow — the post-join synthesis step is the consumer. Re-open the §14.21 concurrent-fan-out recording AS PART OF this arc (the recording + the consumer ship together, never recording-only — the exact hollow-carrier trap that resolved B-INTERSTEP-NONLINEAR).

---

## Done definition (full-spec closure)

The exit gate is `tools/closure_gate.py` **G1.1** = `standalone_registered == 0 AND standalone_gated == 0` (the forward register fully empty). Landing the two authorized arcs drives `standalone_registered` → 0, but does **NOT** by itself satisfy G1.1: one `status: gated` arc remains — **`B-TAIL-CONDITIONAL-SAMPLING`** (`standalone_gated == 1`, dependency-blocked on R-420/R-421). So closure requires THREE dispositions, not two:

1. **Build `B-HITL-PLACEMENT-PER-STEP-LOOSEN`** (registered → closed) — sequence first.
2. **Build `B-POSTJOIN-LLM-SYNTHESIS`** (registered → closed) — sequence second.
3. **Disposition `B-TAIL-CONDITIONAL-SAMPLING`** (gated → resolved/closed) — the closure-step re-check. R-420/R-421 are in the roadmap "Closed/parked" set, so its blocker is likely already lifted; at closure time, re-ground it (is it now buildable, or resolvable-as-NA per a §9.2-sampling spec read?) and dispose it to 0. This is a separate disposition, NOT folded into the operator's "build a & b" authorization — surface it explicitly when it's reached.

When all three reach the closed/resolved state → `standalone_registered + standalone_gated == 0` → **G1.1 passes → R-FS-1 build-complete (resolves)** → the **R-CL-Q1 whole-harness quality track admits** (the Tier-2 5-dimension coverage matrix + quality pass on the complete full-spec harness). That is genuine full-spec closure. (Run `just closure-gate` / `closure_gate.py --check` to confirm G1.1 empirically before declaring done — do not eyeball it.)
