# R-FS-1 B3 — Smart-HITL Decision Intelligence: Design

**Authored:** 2026-06-14 · **Arc:** R-FS-1 (full-spec build program) child arc **B3** (the 2nd sub-program per the frozen `B1 → B3 → E → B2 → R → B4 → CA → B5 → B6 → B7 → M` order; B1 topology-orchestration COMPLETE through #548). · **Posture:** **mode-agnostic** (process-substrate; design-first PR per the B1-DESIGN precedent `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` / R-PM-1 #505; authors only this `.harness/` file; **X-AL-3-clean** — ZERO `design-substrate/**` or `harness-*/src/**` edit). · **Spine:** `.harness/beyond-mvp-capability-boundary-ledger.md` Bucket B row **B3**.

**What this doc is.** The design leg of the B3 sub-program — research → **design** → spec → plan → implement. It (1) **corrects the spine ledger's stale AS-IS** for B3 by direct read at HEAD `8608bc1`, (2) enumerates the **precisely-dispositioned gap-set** (fork-vs-impl per the cleared spec text), (3) makes the **keystone architectural decisions** (D-cond / D-palette / D-edit / D-oq6 / D-handoff), and (4) sequences the **downstream spec/plan/impl arcs**. It decides; it does not author spec/plan/code (those are B3-spec-N / B3-plan / B3-impl-N).

**Decorrelated review:** advisor() (pre-substantive, ×2 + pre-done) + out-of-family Codex + harness-adversarial-reviewer (genuine agent, pre-merge). Record at §9.

---

## §0 — TL;DR

The spine ledger's B3 row ("HITL gate decision intelligence: always-on + full-palette, placeholder placement matrix") is **behaviorally accurate but mis-attributes the cause.** Direct read of `hitl_gate_composer.py` + the cleared specs at HEAD shows the decision-logic **machinery is built** (`evaluate_hitl_required` 4-axis predicate, `compute_effective_palette` narrowing, `on_hitl_timeout` 3-tier degradation table) — it is **unwired in the production path**, not unbuilt. The ledger read the stale **docstring** (`hitl_gate_composer.py:56-81`, the "v1.11 MVP defaults" carry-text), not the body (lines 909-927, which route through the Reading-B v1.22 consumption helpers).

The B3 build is therefore **"wire the existing intelligence + resolve the §19.1 conditional-skip semantics + close the EDIT/degradation residuals,"** smaller and more surgical than a from-scratch design — but with **one deeper finding the ledger missed**: the gate cannot conditionally skip **even when fully wired**, because the `PERSONA_TIER_GATE_LEVEL_FLOOR` maps **all three** persona tiers to `ASK` and the composition is `max()` → computed gate level is always ≥ ASK → `hitl_required` is always True. The only spec mechanism for a skip is the **operator-policy override of a `max()` floor** (§19.5; an **in-`max()` floor-value reconfiguration**, per-tier-permissioned — solo permitted, multi prohibited), whose **authoring schema** is impl-discretion-deferred (the override *surface* + tier-gating are cleared contract). So conditional gating (B3's headline) is a genuine build, not a wiring nit.

**Gap-set & disposition (detail §2):**

| Gap | Classification | Why |
|---|---|---|
| **G1** conditional gating (§19.5 in-`max()` floor override + per-step blast_radius) | **IMPL** (override surface §19.5-cleared; logic impl-discretion) + **narrow fork** *only if* a new authoring-schema field is minted (materialization-site choice) | §19.5 specs the override + tier-gating; only authoring schema deferred |
| **G2** palette `gate_level` wiring (compute-once, thread to 4d) | **IMPL** (against cleared §14.8.2 step 4d) | spec mandates `gate_level=<from 4c>`; code hardcodes ASK |
| **G2c** `per_tool_gate_level` producer (the **DENY-reaching** axis — makes deny-row narrowing reachable) | **IMPL** (faithful carrier factor-out; C-AS-03/C-AS-12 declare it, `ToolContract` carrier missing) | without it, G2 is **behaviorally inert** (`gate_level` never DENY → deny-row never fires) |
| **G3** EDIT replace-not-merge | **IMPL** (non-compliance vs NOTE 6-ii) + **possible sub-fork** (str↔Mapping carrier drift) | NOTE 6-ii: "MUST replace-not-merge" |
| **G4a** OQ-6 degradation *attribute* | **IMPL** (against cleared §14.8.2 step 4f) | spec mandates the `hitl_timeout_degradation` consult |
| **G4b** OQ-6 degradation *control-flow* (apply the kind) | **FORK** (X-AL-3 — runtime spec always raises) | CP contract defines kinds as control-flow; runtime shadow wires audit-attr-only |
| **G5** HandoffContext non-empty summary | **distinct follow-on arc** (spec-legitimately-minimal) | §14.7.3: `summary_text=""` is the MVP shape; non-empty = "Summarization model invocation per C-CP-21 §21.4" |

**Net:** **1 certain fork** (G4b degradation-control-flow) **+ 1 conditional fork** (G1's §19.5 authoring-schema field *iff* a new declared field is minted; else impl-discretion) **+ 4 impl-against-cleared-spec gaps** (G2 + **G2c** per-tool producer — ship together or G2 is inert; G3 — sub-fork only under D-edit.B carrier-drift; G4a) **+ 1 structural cleanup** (compute `gate_level` once) **+ 1 follow-on producer arc** (G5 summarization). Downstream sequence at §8.

---

## §1 — Re-grounding (the ledger correction)

### §1.1 What the ledger claims vs what HEAD shows

The spine ledger (`beyond-mvp-capability-boundary-ledger.md`, Bucket B row B3, authored 2026-06-12 at HEAD `3d805d2`) states:

> **B3** — HITL gate decision intelligence: always-on + full-palette, placeholder placement matrix. … `_hitl_required` is **always True on a matching placement** (no conditional predicate), the response palette is **`DEFAULT_FULL_PALETTE` unconditionally** (no per-cell narrowing/escalation), and `HandoffContext`/placement composition is a placeholder. Evidence: `hitl_gate_composer.py:56-81`; `:181-185`.

The cited lines **56-81** are the module **docstring** ("Carry-forward operative defaults at v1.11 MVP"), which *is* stale-carry text. The composer **body** (HEAD `8608bc1`, `hitl_gate_composer.py:909-927`) routes through:

- **4c** → `_evaluate_hitl_required_tolerant(binding, placement)` → consumes the 4-axis `evaluate_hitl_required` (`hitl_required_consumption.py`) **when** binding exposes `persona_tier` + `blast_radius_tier`; falls back to `placement.requires_hitl` default-True only for partial/test-fixture bindings.
- **4d** → `_compute_effective_palette_tolerant(binding)` → consumes `compute_effective_palette` (`effective_palette.py`), which genuinely narrows (deny-row → `{REJECT,RESPOND}`; cross-trust intersection; validator-brief intersection).
- **4a** → `_compose_hitl_handoff_context(step_context, step)` → builds a real 7-field `HandoffContext`.
- **4b** → `matrix_cell_for(persona_tier, engine_class)` + `is_excluded` + the durable-async synchrony branch (`§14.8.8.1`).

So the **machinery is built** (across the Reading-B v1.22 + validator-composer + HITL-gate-as-pause-trigger arcs); the ledger's "no conditional predicate / no narrowing machinery" framing is incorrect. The correct framing: **built, unwired in the production path.**

### §1.2 Why "unwired in production" — the three wiring breaks

The ledger's *behavioral* claim (always-fires, full-palette) is nonetheless correct in production, because of three breaks between the machinery and the production binding:

1. **`StepEffectiveBinding` lacks `blast_radius_tier`.** The production per-step binding (`per_step_override_evaluator.py:126`, C-CP-06 §6.2) carries `{step_id, model_binding, engine_class, hitl_placement, override_applied, override_audit_ref, persona_tier}` — **no `blast_radius_tier`, no `per_tool_gate_level`**. So `_evaluate_hitl_required_tolerant` reads `getattr(binding, "blast_radius_tier", None) → None` → falls back to the default-True path. The 4-axis predicate is **unreachable in production.**
2. **Wrap-time palette inputs are hardcoded sentinels.** `_compute_effective_palette_tolerant` calls `compute_effective_palette(gate_level=GateLevel.ASK, cross_trust_state=NONE, validator_escalation_brief=None)` — `gate_level` is **hardcoded ASK** (not threaded from 4c), so the narrowing always returns `FULL_PALETTE`. (`cross_trust_state=NONE` is **spec-correct** at wrap-time — see §4.)
3. **Timeout path emits a placeholder.** The `AskUserQuestionTimeoutError` branch sets `hitl.timeout.degradation_mode_applied = "default"` (a literal string) and **never consults** `on_hitl_timeout(...)`; it unconditionally raises `HITLGateTimeoutError`.

### §1.3 The deeper finding the ledger missed — conditional skip is structurally impossible at HEAD

Even if break #1 is fixed (thread `blast_radius_tier`), **the gate still always fires.** The `gate_level()` composition (`gate_level_rule.py:165`) is `max()` over the materialized axis floors, and `PERSONA_TIER_GATE_LEVEL_FLOOR` (`:150`) maps **all three** persona tiers to `GateLevel.ASK`:

```python
PERSONA_TIER_GATE_LEVEL_FLOOR = {
    SOLO_DEVELOPER: ASK,  TEAM_BINDING: ASK,  MULTI_TENANT_COMPLIANCE: ASK,
}
```

`max(ASK, blast_floor, per_tool_floor) ≥ ASK` always → `hitl_required` (`= computed_gate_level ∈ {ASK, DENY}`) is **always True**, regardless of `blast_radius_tier`. The blast floor can only *raise* (LOCAL_MUTATION+ → ASK) or contribute nothing (READ_ONLY → AUTO); it can never pull the `max()` below the persona floor's ASK.

This is **faithful to the cleared spec.** CP spec v1.2 §19.1 (preserved verbatim through v1.15; v1.15 §19.1.1 only disambiguated the per-axis cite-shape) declares:

```
persona_tier_floor:
    solo-developer  → ask  (operator may override to auto for non-irreversible)
    team-binding    → ask
    multi-tenant    → ask
```

The all-ASK table is canonical. The **only** spec-acknowledged path to a sub-ASK (skippable) gate is the parenthetical **"operator may override to auto for non-irreversible"** — and that override's **authoring schema is "deferred to implementation discretion"** (CP spec v1.2 §19.1 deferred-list: *"specific operator-policy override authoring schema (manifest field / API call / TUI action — composes with `Spec_Action_Surface_v1.md` C-AS-12 §12.5)"*).

**How the override composes — §19.5 (read it; it is the keystone fact).** The spec models the override as **"operator-policy override of any `max()` floor"** (§19.5 title + table) — i.e. an **in-`max()` floor-value reconfiguration**, NOT a separate post-`max()` bypass layer. `[MODERATE — this in-`max()` reading is an **inference** from §19.5's literal "override of any `max()` floor"; the spec does not state "in-`max()`" vs "post-`max()`" verbatim. It is the most faithful reading and is carried as a Reading-C design decision (§3.3), not a spec mandate.]` Two confirmations in the §19.1 body itself: `blast_radius_floor: local-mutation → ask` is annotated *"(configurable to auto at solo-developer)"* (line 1634) and `persona_tier_floor: solo-developer → ask` is annotated *"(operator may override to auto for non-irreversible)"* (line 1639). So the operator reconfigures a **floor value**, and `max()` then composes the (possibly-lowered) floors: for solo + READ_ONLY, `max(per_tool=AUTO, blast=AUTO, persona=AUTO→override) = AUTO` → `_hitl_required = false` → **skip** (§19.4 truth table: `auto → false → dispatches without HITL`). Critically, **§19.5 already specs the override surface + its per-tier permissions** — `solo-developer` permitted (operator IS the policy authority), `team-binding` permitted **only at non-`external-irreversible`**, `multi-tenant-compliance` **structurally prohibited** (override attempts emit an audit-ledger violation event). Only the **authoring schema** (the config/manifest field through which the operator declares the override) is impl-discretion-deferred; the override *semantics* + tier-gating are cleared contract. The §1.3-draft "the override REPLACES the persona floor, not a `max()` axis" framing was wrong and is corrected here.

**Consequence for B3.** Conditional gating (the gate *sometimes* skipping → "smart HITL") is a genuine **build**, not a wiring nit. It requires materializing the §19.5 override authoring schema (impl-discretion-deferred; the override *surface* is specced) plus a per-step blast_radius resolver to evaluate "non-irreversible." The fail-safe tier-gating is **spec-mandated** (§19.5), not a config default we invent. This is the keystone — §3.

---

## §2 — Dispositioned gap-set

Each gap classified by the **fork-vs-impl discriminator**: a gap whose resolution is *mandated by the cleared spec* is **IMPL** (impl-against-cleared-spec; no back-flow). A gap whose resolution requires a *new or changed contract surface* is a **FORK** (X-AL-3; design-substrate amendment first).

| # | Gap | AS-IS (HEAD `8608bc1`) | Cleared-spec disposition | Class |
|---|---|---|---|---|
| **G1** | Conditional gating — gate always fires | persona floor all-ASK + `max()` ⟹ always ASK; §19.5 override authoring-schema unbuilt; per-step `blast_radius` not produced | **§19.5** specs the override surface ("override of any `max()` floor") + per-tier permissions; authoring schema = **impl discretion** (v1.2 deferred-list + C-AS-12 §12.5) | **IMPL** (blast resolver + §19.5-cleared override logic). **Narrow fork** *only if* a new authoring-schema field is minted (Reading C/D/E materialization site) — §3 decides. |
| **G2** | Palette `gate_level` wiring | `_compute_effective_palette_tolerant` hardcodes `gate_level=ASK` | §14.8.2 step 4d MANDATES `gate_level=<from 4c>` | **IMPL** (coupled to G1; compute once, thread to 4d) |
| **G2b** | Palette `cross_trust_state` | hardcodes `NONE` | spec line 3353: cross-trust applies **only at §14.15 re-entry, not wrap-time**; state is not knowable pre-dispatch | **NO GAP** (spec-correct) |
| **G2c** | `per_tool_gate_level` producer — the **only** axis that reaches DENY (persona+blast top at ASK) | `ToolContract` carries `minimum_tier`+`blast_radius_tier`, **no per-tool gate-level**; §3.2 resolves only blast → `gate_level` never DENY → deny-row narrowing **inert** (green-but-unreachable) | C-AS-03 frontmatter (`tier ∈ {auto,ask,deny}`, line 1155) + C-AS-12 §12.1 (line 1002) **declare** it; landed `ToolContract` carrier missing | **IMPL** (faithful carrier factor-out, U-CP-00c precedent; verify thin-AS-reconciliation at B3-spec) — **ships with G2** (§4.1) |
| **G3** | EDIT replace-not-merge | step 4i `EDIT` branch is `pass` — payload never replaced | §14.8.2 step 4i + NOTE 6-ii: **"MUST replace-not-merge"** `step.step_payload` | **IMPL** (non-compliance). **Sub-fork** owed *only* under D-edit.B (runtime-`str` ↔ CP-`Mapping` carrier drift); the structured-elicitation path (D-edit.A) collapses it to plain IMPL — §5. |
| **G4a** | OQ-6 degradation *attribute* | emits `"default"` literal | §14.8.2 step 4f MANDATES `harness_cp.hitl_timeout_degradation` consult for `degradation_mode_applied` + `audit.policy.*` | **IMPL** (thin — `on_hitl_timeout` is persona_tier-only) |
| **G4b** | OQ-6 degradation *control-flow* | always raises `HITLGateTimeoutError` | §14.8.2 step 4f wires degradation as **audit-attr only**; CP §21.6 defines the kinds (CONTINUE_AS_REJECT / ESCALATE / ABORT) as **control-flow** | **FORK** (X-AL-3 — building the disposition-change extends the runtime contract) |
| **G5** | HandoffContext non-empty summary | `summary_text=""`, `summary_hash=sha256(b"")`, `agent_confidence=None` | §14.7.3: empty is the **legitimate v1.6 MVP shape**; non-empty = "Summarization model invocation per C-CP-21 §21.4" | **distinct follow-on arc** (in-scope under FULL-SPEC; separate summarization-producer build) |

**Already-correct (no gap), recorded to prevent re-litigation:**
- Matrix-cell resolution + `is_excluded` (4b) — built + wired (`matrix_cell_for`).
- Synchrony-class + durable-async branch (`§14.8.8.1`) — built (HITL-gate-as-pause-trigger arc, runtime v1.24-v1.26).
- The 4-span canonical shape + 4-substep audit-write — built (c_rt_18 carrier-drift arc, APPLIED).
- VALIDATOR_ESCALATION un-foreclosure (Reading B v1.22) — fires via §14.15 mid-step re-entry; wrap-time filters it out.

**4b ⊥ 4c orthogonality (pre-empting a reviewer probe).** The two persona-tier reads are **independent axes**, not a missed input to each other: **4b** resolves `matrix_cell_for(persona_tier, engine_class) → synchrony_class` — *how to wait* (sync-blocking vs durable-async vs both-by-tier); **4c** resolves `gate_level(persona_tier, blast_radius, per_tool, mcp_trust) → required?` — *whether to gate*. `engine_class` drives 4b only; it is **not** an input to the 4c gate-level composition (the §19.1 axis set is `{per_tool, blast_radius, mcp_trust, persona_tier}` — `engine_class` is absent by design). G1 (conditional gating) therefore does not touch the 4b synchrony path, and the already-built durable-async branch is unaffected.

---

## §3 — D-cond (G1): conditional gating — the keystone

### §3.1 The precise gap

Two coupled sub-gaps:

- **G1-skip:** the gate must be able to return **AUTO** (skip) for low-risk actions at the appropriate persona tier. Today it cannot (§1.3). The mechanism is the §19.1 **operator-override-to-AUTO for non-irreversible** at solo-developer (impl-discretion-deferred authoring schema).
- **G1-blast:** evaluating "non-irreversible" + the `blast_radius_floor` axis requires a **per-step `blast_radius_tier`**, which is not produced anywhere today for a per-step binding.

### §3.2 G1-blast — the producer (advisor's keystone concern, `[[r-cxa-seam-wiring-is-producer-discovery]]`)

`blast_radius_tier` is an **AS concept** (`harness_as.sandbox_tier.BlastRadiusTier`: `READ_ONLY / LOCAL_MUTATION / EXTERNAL_REVERSIBLE / EXTERNAL_IRREVERSIBLE`). **No** per-step carrier exists: `WorkflowManifestEntry`, `WorkflowStep`, `StepOverride`, `StepEffectiveBinding` carry none (confirmed by direct grep). The blast_radius of a step is therefore **not a lookup — it must be resolved per step-kind**, and the resolution is semantically well-determined:

| Step kind | blast_radius source | Rationale |
|---|---|---|
| **INFERENCE_STEP** | `READ_ONLY` | A provider chat-completion has **no external side effect** — it produces text. Side effects come from downstream TOOL/SUB_AGENT steps, each independently gated. (This is *why* an inference-bearing workflow can still be `AUTO` — the inference itself is read-only.) |
| **TOOL_STEP** | the tool's `ToolContract.blast_radius_tier` (AS C-AS-03), looked up by `tool_id` from the step payload | the tool *is* the side-effecting action; its contract declares the blast radius |
| **SUB_AGENT_DISPATCH** | the child ceiling — existing `compute_child_blast_radius_ceiling` / `_blast_radius_of(sandbox_tier)` (`sub_agent_gate_level_descent.py`) | a sub-agent's blast radius is bounded by its sandbox tier ceiling (already derived for gate-level descent) |
| **DECLARATIVE_STEP / HITL_STEP** | `READ_ONLY` | no external effect |

**Design decision D-cond.1:** B3 builds a **`resolve_step_blast_radius(step, ctx) → BlastRadiusTier`** per-step-kind resolver (the table above). This is **impl-against-cleared-spec** — the spec's deferred-list explicitly leaves "specific `blast_radius_floor(tool)` lookup" to implementation (Action-Surface territory) and the per-kind semantics are determined by the existing AS contracts; no new contract surface is minted.

### §3.3 G1-skip — the override authoring schema (the §19.5 surface)

The override-to-AUTO consumes `{persona_tier, blast_radius, operator-policy}`. `persona_tier` is on the binding; `blast_radius` comes from D-cond.1; the **operator-policy** is the §19.5 *"operator-policy override of any `max()` floor"* surface — **already specced** (per-tier-permissioned: solo permitted, team non-`external-irreversible` only, multi prohibited), with only its **authoring schema** impl-discretion-deferred (§19.1 deferred-list + C-AS-12 §12.5). Per §1.3, the override is an **in-`max()` floor-value reconfiguration**, not a post-`max()` bypass. Two design choices fall out: (a) where `blast_radius` is resolved, and (b) how the override authoring schema materializes.

**(a) blast_radius resolution site.**

- **A1 — gate-site resolution (recommended; no CP-contract change).** Resolve `blast_radius` via `resolve_step_blast_radius(step, ctx)` at the composer site (step 4c), feeding a real `GateLevelInput` to `evaluate_hitl_required`. `StepEffectiveBinding` is untouched.
- **A2 — binding-field (C-CP-06 fork).** Add `blast_radius_tier: BlastRadiusTier` to `StepEffectiveBinding`, resolved at `resolve_step_binding(...)`. A **C-CP-06 §6.2 contract change** → Class-1 fork.

**Recommendation A1.** `blast_radius` is **derived, not authored** — a function of the step (§3.2 per-kind table), not an override-able binding field; putting it on `StepEffectiveBinding` (whose semantic is "override-applied per-step binding") is a category mismatch. A1 keeps the logic at the **runtime composition layer** where the Reading-B v1.22 helpers already live (`_evaluate_hitl_required_tolerant` already `getattr`-reaches for these axes — A1 makes the values *real* instead of `None`) and avoids a CP-contract fork for a non-CP-contract value.

**(b) override authoring schema materialization** — three readings:

- **Reading C — tunable floor (recommended; in-`max()`, lightest).** The operator overrides a **floor value** that already feeds `max()` — e.g. a config surface that sets `persona_tier_floor[SOLO]` (and/or `blast_radius_floor[LOCAL_MUTATION]`) to `AUTO` for non-`external-irreversible`, default unchanged (`ASK`). The skip composes *inside* the existing `max()` (`max(AUTO, AUTO, AUTO)=AUTO`); **no post-`max()` bypass layer**. Most faithful to §19.5 ("override of any `max()` floor") and to §19.1's own "(configurable to auto at solo-developer)" annotations.
- **Reading D — new bypass mapping.** A new `RuntimeConfig.hitl_auto_approve_policy: Mapping[(persona_tier, blast_radius_tier), bool]` evaluated *after* `max()`. Heavier; introduces a bypass layer §19.5 does not model; a mis-set entry *could* attempt to lower a tier the floor forbids (caught only by an added guard). **Rejected** — it re-models a cleared composition.
- **Reading E — per-step-override reuse.** Compose the override through the **existing** `StepOverride` / per-step-override mechanism (C-CP-06 §6.2 already carries `hitl_placement` overrides). Viable but couples a *policy* (which tiers/blast-radii auto-approve) to a *per-step manifest authoring* surface — the §19.5 surface is operator-policy-level, not per-step.

**Design decision D-cond.2 — Reading C (tunable floor), materialized as the override authoring schema.** Because §19.5 already specs the override *surface* + tier-gating, the open question is only the **authoring-schema field**. Whether this needs a **fork** depends on the materialization site: a new `RuntimeConfig`/`MCPClientConfig`-style field is a contract-surface change → narrow **runtime-spec fork** (same shape as `step_dispatch_timeout_seconds`); a bootstrap-supplied override applied at the gate-site helper (no new *spec* field, consuming the §19.5-cleared semantics via impl-discretion) is **impl-against-cleared-spec**. **B3-spec-1 ratifies which** (the materialization-site choice is the operator gate, not the override semantics — those are cleared). Conservative default in all readings: floors **unchanged** (`ASK`) unless the operator explicitly opts a (solo, non-irreversible) cell to `AUTO`.

> **Tension named (for §9 review / dyadic council).** D-cond.2 carries a **C10 ⊥ C11** tension: action-safety/blast-radius (C10) wants the *default* to gate (fail-safe: never auto-approve an un-classified action), while operator-loop/local-first (C11) wants solo-developer ergonomics (don't prompt on every read-only inference). **§19.5 already resolves the structural half fail-safe**: the override is multi-prohibited + team-restricted by cleared contract, and under Reading C (in-`max()`) a mis-set solo override **structurally cannot** lower team/multi (their floors stay `ASK`, and §19.5 forbids their override) — a *stronger* fail-safe than a post-`max()` bypass (Reading D), which is the C10 argument *for* Reading C. The residual tension is only the **default-value + the materialization-site fork scope** at solo. Nameable → §13.4 discriminator: **offer a dyadic C10⊥C11 convening at B3-spec-1 ratification** (mirrors the B1-spec-1 cascade-cancel council).

### §3.4 What G1 unblocks

Once D-cond lands, 4c computes a **real `gate_level`** per step. This (a) makes the gate genuinely conditional (READ_ONLY solo inference → AUTO → skip), and (b) supplies the real `gate_level` that **G2** threads into 4d. G1 and G2 are therefore one coupled impl cluster.

---

## §4 — D-palette (G2): wire the real gate_level into 4d

**Gap.** `_compute_effective_palette_tolerant` hardcodes `gate_level=GateLevel.ASK`; the spec (§14.8.2 step 4d, v1.22) mandates `gate_level=<from 4c>`. **`cross_trust_state=NONE` is spec-correct at wrap-time** (line 3353: the cross-trust restriction applies only at the §14.15 mid-step re-entry path where validator-escalation context is in scope; cross-trust state is not knowable pre-dispatch).

**Structural cleanup (D-palette).** Today `gate_level` is computed inside `_evaluate_hitl_required_tolerant` (for the bool) and then **discarded**; `_compute_effective_palette_tolerant` re-hardcodes ASK. The fix computes the `GateLevelComputation` **once** at step 4c and threads `computed_gate_level` to both the `hitl_required` bool **and** `compute_effective_palette`. This is **impl-against-cleared-spec** (it realizes the mandated `gate_level=<from 4c>`), and it removes a redundant double-computation.

### §4.1 — G2c: the deny-row narrowing is unreachable without a `per_tool_gate_level` producer (green-but-unreachable trap)

**The trap (advisor pre-done #4 — every prior review missed it).** The *only* wrap-time palette narrowing is the §19.4 **deny-row** (`gate_level == DENY → {REJECT, RESPOND}`); cross-trust + validator-brief narrowing are §14.15-only (per G2b). But after **G1-as-scoped**, wrap-time `gate_level = max(per_tool, blast, persona)` where **persona tops at ASK** (all-ASK floor) and **blast tops at ASK** (`BLAST_RADIUS_GATE_LEVEL_FLOOR` has no DENY entry — `gate_level_rule.py:136`). The *only* axis that reaches DENY is **`per_tool_gate_level`** — and §3.2's producer resolves only `blast_radius`; `per_tool_gate_level` still `getattr`-defaults to AUTO. So **wrap-time `gate_level ∈ {AUTO, ASK}` only → never DENY → the deny-row narrowing never fires** → threading `gate_level` (D-palette) is **behaviorally inert in production** until the per-tool axis is produced. (The original §4 draft claimed "a DENY gate level (e.g. a deny-tier tool) yields `{REJECT, RESPOND}`" — that payoff is unbuildable without the producer below; corrected here.)

**G2c — the `per_tool_gate_level` producer.** The per-tool gate-level (`tier ∈ {auto, ask, deny}`) **is spec-declared**: AS C-AS-03 frontmatter declares `tier ∈ {auto, ask, deny}` per-tool (AS spec line 1155) and C-AS-12 §12.1 carries `per_tool_gate_level` as the C4 axis of the `max()` (AS spec line 1002). But the **landed `ToolContract` carries no such field** — `tool_contract.py:77-80` has `minimum_tier: SandboxTier` + `blast_radius_tier: BlastRadiusTier` only, **no `per_tool_gate_level` / `{auto,ask,deny}`**. So the DENY-reaching axis has **no landed carrier anywhere** (the same producer-discovery shape as G1-blast, `[[r-cxa-seam-wiring-is-producer-discovery]]`).

**Design decision D-palette.2.** B3 builds the `per_tool_gate_level` producer alongside the §3.2 blast resolver: for TOOL_STEP, resolve **both** `blast_radius` and `per_tool_gate_level` from the tool's contract (default `AUTO` when the tool declares no tier); for INFERENCE/SUB_AGENT, `per_tool_gate_level = AUTO` (no per-tool tier). Because C-AS-03/C-AS-12 **already declare** the per-tool gate-level semantics, materializing the `ToolContract` carrier is **impl-against-cleared-spec** (a faithful carrier factor-out, the U-CP-00c precedent: concept ADR/spec-committed, only the declaration site missing) — **verify at B3-spec** whether a thin AS-spec reconciliation (adding the field to the C-AS-03 carrier table explicitly) is owed vs a pure impl factor-out. With D-palette.2, a deny-tier tool reaches `gate_level=DENY`, the §4 example becomes **reachable**, and the deny-row narrowing is genuinely live — closing the green-but-unreachable trap. **G2 (thread gate_level) and G2c (produce the deny-reaching axis) ship together**; G2 alone is inert.

---

## §5 — D-edit (G3): EDIT replace-not-merge

**Gap.** Step 4i `EDIT` branch is `pass`; the cleared spec mandates replacement: §14.8.2 step 4i (*"the edited proposal replaces `step.step_payload`"*) + NOTE 6-ii (*"v1.9 implementations **MUST replace-not-merge**; consumers MUST treat `gate_result.edited_proposal` as authoritative replacement"*). So the current code is **non-compliant** with the cleared spec.

**The real under-specification — a runtime↔CP carrier drift (adversarial F2-01).** The source of the difficulty is **not** "NOTE 6-ii assumes a string payload" — it is a **carrier drift** between the runtime ask-surface and the CP-canonical envelope:

- the **runtime** result the composer consumes is `AskUserQuestionResult.edited_proposal: str | None` (`ask_user_question_surface.py:86`; the composer `.encode("utf-8")`s it at `hitl_gate_composer.py:432`/`:737`) — **`str`**;
- but `WorkflowStep.step_payload` is `Mapping[str, Any]` (`workflow_driver_types.py:99`, opaque per C-CP-25 §25.3.3.4) and the **CP-canonical** gate envelope `HITLGateResult.edited_proposal` is `Mapping[str, Any] | None` (`hitl_placement.py:197`) — **structured**.

So "replace verbatim" (NOTE 6-ii) of a `Mapping` `step_payload` by an operator-supplied **`str`** is under-specified because the **runtime carrier (`str`) drifted from the CP carrier (`Mapping`)** — NOTE 6-ii's "verbatim" in fact *presumes* the structured CP carrier.

**Design decision D-edit — two readings, B3-spec picks:**
- **D-edit.A — IMPL, no sub-fork (preferred if reachable).** Obtain a **structured** `edited_proposal` matching the `Mapping` carrier via the §14.8.3 v1.12 structured-elicitation surface (`ctx.elicit(message, schema)`, runtime spec line 3379). Then replace-not-merge is `Mapping → Mapping` verbatim = plain **IMPL** (`step.model_copy(update={"step_payload": edited})`), the sub-fork collapses, and the runtime↔CP carrier drift is healed.
- **D-edit.B — sub-fork.** If B3 keeps the `str` ask-surface result, the `str → Mapping[str,Any]` replacement is genuinely under-specified → file `class_*_fork_hitl_edit_carrier_drift_str_vs_mapping.md` routed to a follow-on workflow-mutation-discipline arc (per NOTE 6-ii's own deferral of "richer mutation — field-level patches, type-aware merging"). This honors the cleared mandate without silently absorbing the drift (`[[halt-route-split-ac-pattern]]`).

The **core** (replace-not-merge over a string-shaped payload) is IMPL either way; the sub-fork is owed **only** under D-edit.B. B3-spec-1/impl resolves which by checking whether the structured-elicitation path is wired.

---

## §6 — D-oq6 (G4): timeout-degradation

### §6.1 G4a — degradation *attribute* (IMPL)

**Gap.** The timeout path emits `degradation_mode_applied = "default"`; §14.8.2 step 4f mandates the value come "from per-persona-tier `harness_cp.hitl_timeout_degradation` consult" (+ the `audit.policy.*` namespace at audit composition). **Thin** (advisor de-risk): `on_hitl_timeout(invocation, persona_tier)` **ignores its `invocation` arg** (`hitl_timeout_degradation.py:166` `_ = invocation`) — it is persona_tier-only, and `persona_tier` is already on the production binding. So G4a is **pure attribute wiring**: call `on_hitl_timeout(_, binding.persona_tier) → TimeoutDegradationKind`, set `degradation_mode_applied = kind.value`, and derive the `audit.policy.*` value at the partial-audit composition. No `HITLInvocation` construction needed. **Impl-against-cleared-spec.**

### §6.2 G4b — degradation *control-flow* (FORK)

**Gap.** The `TimeoutDegradationKind` values are **control-flow semantics** by their CP definitions (C-CP-21 §21.6): `CONTINUE_AS_REJECT` ("treat the timeout as a REJECT response"), `ESCALATE_TO_REVIEW_BOARD` ("raise the gate level; a second invocation"), `ABORT_WORKFLOW` ("terminal"). But the cleared **runtime** spec (§14.8.2 step 4f + the `RT-FAIL-HITL-GATE-TIMEOUT` fail-class row) wires the kind as an **audit attribute only** and **always raises `HITLGateTimeoutError`** regardless of the kind. So the runtime composer **never actually applies** the degradation — a CP-contract-vs-runtime-shadow drift.

Under the FULL-SPEC directive, the **full degradation semantics are in scope** (nothing deferred). But making the kind change the disposition is a **runtime-contract extension** (the cleared spec mandates the raise) → **X-AL-3 fork**. The mapping:

| Kind | Current (cleared) | Full-spec target | Notes |
|---|---|---|---|
| `CONTINUE_AS_REJECT` | raise `HITLGateTimeoutError` | route through the **REJECT** disposition (`HITLGateRejectedError`-equivalent; step fails as rejected) | semantically distinct fail-class from a raw timeout |
| `ESCALATE_TO_REVIEW_BOARD` | raise | **re-invoke** the gate at a raised level (a second invocation) | bounded re-invocation; needs a loop guard + the "review board" surface (TEAM/MULTI) — **largest sub-surface; may itself split** |
| `ABORT_WORKFLOW` | raise (→ step failure → driver) | **terminal** workflow abort (no further steps) | closest to current raise; the driver maps to terminal |

**Design decision D-oq6b.** B3-spec authors the runtime-side **degradation-disposition contract** (a §14.8.x extension: timeout → consult `on_hitl_timeout` → **dispatch on the kind** rather than unconditional raise). The `ESCALATE_TO_REVIEW_BOARD` re-invocation sub-surface is the heaviest (it needs a re-invocation loop guard + the raised-level second gate); per the B1/U-RT-59 narrow-scope precedent, **the spec may scope CONTINUE_AS_REJECT + ABORT_WORKFLOW first** (both terminal-ish, low blast radius) and **stage ESCALATE_TO_REVIEW_BOARD as a bounded follow-on** — to be ratified at the B3-spec arc (operator gate, since the scope-split text matters). This fork is the B3-spec-2 deliverable.

---

## §7 — D-handoff (G5): HandoffContext summary

**Gap.** `_compose_hitl_handoff_context` builds the 7-field context with `summary_text=""`, `summary_hash=sha256(b"")`, `agent_confidence=None`, `failed_attempts=()` — the operator sees an **empty summary** at the gate, arguably core "decision intelligence."

**Disposition (advisor's don't-drop-it).** This is **spec-legitimately-minimal**, not a defect: §14.7.3 (the sibling sub-agent-dispatch composition table, line 3178) documents `state_summary.summary_text = empty string` as the **v1.6 MVP shape**, with the named beyond-MVP producer **"Summarization model invocation per C-CP-21 §21.4."** So a non-empty summary is a **distinct capability** — an LLM summarization call over the relevant ledger entries — not a wiring fix.

**Design decision D-handoff.** Under FULL-SPEC, G5 **is** a build item, but it is a **separate follow-on producer arc** (`B3-impl-handoff-summary` or a dedicated R-FS-1 child), **not bundled into the G1-G4 wiring core**: (i) it is a different mechanism (a summarization-model invocation, an inference call, not a composer wiring); (ii) it composes with — does not block — the conditional-gating + palette + degradation core; (iii) bundling an LLM-call producer into the wiring arc would conflate two unrelated blast radii. **Explicitly in-scope, explicitly sequenced after the core** (§8). This is the honest disposition — it does not vanish (`§10.5` silent-scope-narrowing), and it is not force-fit into the keystone.

---

## §8 — Fork inventory + downstream arc sequence

### §8.1 Forks owed (design-substrate amendments, X-AL-3 back-flow)

| Fork | Surface | Shape | Ratification gate |
|---|---|---|---|
| **F-B3-1** | §19.5 override authoring schema (D-cond.2 / Reading C tunable-floor) — operator-policy floor-reconfiguration surface | materialization-site choice: new config field (narrow fork) vs gate-site bootstrap surface consuming §19.5-cleared semantics (impl-discretion) + §14.8.2 step-4c consumption. **Silent-absorption guard (adversarial F1-02):** the "no-fork" branch is valid **only iff ZERO new declared override-policy field** is minted; ANY persisted operator-declared override field (`RuntimeConfig`/manifest/bootstrap param) is a new contract surface → the narrow fork IS owed (X-AL-3). Downstream MUST NOT read "no fork" as a blanket license. | **C10⊥C11 dyadic council** (§19.5 already fail-safe-gates the tiers) → operator ratify (default-value + materialization-site/fork-scope) |
| **F-B3-2** | timeout-degradation-disposition (D-oq6b / G4b) — dispatch-on-kind vs unconditional-raise | runtime spec §14.8.x extension | operator ratify the **scope-split** (CONTINUE_AS_REJECT+ABORT first vs all-3) |
| **(sub-fork)** | EDIT carrier-drift (D-edit.B / G3) — runtime-`str` ↔ CP-`Mapping` `edited_proposal` | filed `class_*_fork_hitl_edit_carrier_drift_str_vs_mapping.md` **only if** the `str` ask-surface result is kept (D-edit.A structured-elicitation collapses it to IMPL) | routed to workflow-mutation-discipline arc (NOTE 6-ii) — not blocking |

### §8.2 Impl-against-cleared-spec (no fork)

- **G1-blast** — `resolve_step_blast_radius` per-step-kind resolver (D-cond.1).
- **G2** — compute `gate_level` once, thread to 4d (D-palette).
- **G2c** — `per_tool_gate_level` producer (TOOL→`ToolContract` tier, else AUTO); faithful carrier factor-out making the deny-row narrowing reachable (D-palette.2); ships with G2.
- **G3** — EDIT replace-not-merge, string-payload case (D-edit; sub-fork only under D-edit.B).
- **G4a** — `on_hitl_timeout` → `degradation_mode_applied` attribute (D-oq6a).

### §8.3 Sequence (research → design[this] → spec → plan → impl)

```
B3-design  ✅ (this doc)
  → B3-spec-1  : F-B3-1 §19.5 override authoring schema (Reading C tunable-floor) + §14.8.2 step-4c
                 consumption. MATERIALIZATION SITE UNRESOLVED at design — new config field (narrow
                 runtime-spec fork) vs gate-site bootstrap surface consuming §19.5-cleared semantics
                 (impl-against-cleared-spec, NO fork). Preceded by C10⊥C11 dyadic council; operator
                 ratifies {default-value, materialization-site → fork-scope}. The fork is OWED ONLY
                 IF the config-field site is chosen.
  → B3-spec-2  : F-B3-2 §14.8.x timeout-degradation-disposition (operator ratify scope-split)
  → B3-plan    : atomic-unit decomposition of B3-spec-1/2 + the impl-against-cleared-spec gaps
                 (U-RT-NN: blast resolver, gate_level-once, palette-thread, EDIT-replace,
                  degradation-attr, degradation-dispatch) — coverage-matrix-complete
  → B3-impl-1  : G1-blast resolver + G2c per-tool-gate-level producer (ToolContract carrier) + G1-skip
                 override consumption + G2 palette-thread (coupled cluster — G2 is INERT without G2c)
  → B3-impl-2  : G4a degradation-attr + G4b degradation-dispatch (per ratified scope)
  → B3-impl-3  : G3 EDIT replace-not-merge
  → B3-impl-handoff : G5 summarization producer (separate; composes, not blocks)
  → retirement/Q1 hygiene: refresh the spine ledger B3 row (machinery-built-unwired correction);
                            the stale `hitl_gate_composer.py:56-81` docstring → Q1 doc-hygiene
```

B3 supplies the **OQ-6 producer** (Bucket A) at B3-impl-2: the composer's timeout path **is** the "wall-clock-wait orchestrator" the OQ-6 confirm-defer was gated on — wiring `on_hitl_timeout` + the degradation dispatch closes OQ-6's producer-gate. (OQ-5/OQ-7 operator-burden auto-degradation — `OperatorBurdenEvaluator.should_degrade()`, runtime §14.x — remains genuinely-hollow per Bucket A; **not** in B3 scope; flagged to avoid conflation.)

---

## §9 — Decorrelated review record

| Reviewer | Role | Disposition |
|---|---|---|
| **advisor()** pre-substantive #1 | caught the **unread `cp_20_underspec` Class-1 tension** (+ 2 forks) before authoring; flagged G4b ≠ string-fix; flagged cross_trust provenance | applied — read all on-point docs first (`[[cleared-spec-resolves-it-before-first-principles-fix]]`) |
| **advisor()** pre-substantive #2 | flagged G1 **producer-discovery** (blast_radius has no per-step carrier) + **HandoffContext silently dropped**; de-risked G4a (`on_hitl_timeout` ignores `invocation`) | applied — §3.2 producer table + §7 G5 disposition + §6.1 G4a-thin |
| **advisor()** pre-done #3 | caught the **§19.5 override-composition blind spot** — I'd asserted "the override REPLACES the floor, not a `max()` axis" without reading the override-mechanism text | applied — read §19.5 ("override of any `max()` floor" = **in-`max()` reconfiguration**); corrected §0/§1.3, added **Reading C** (tunable floor), refined F-B3-1, added **4b⊥4c orthogonality** note (`[[verification-shape-sharpened-grep-vs-e2e]]` — verify before asserting settled) |
| **out-of-family Codex** | **[P2]** §8.3 sequence pre-selected the unresolved override materialization site (`hitl_auto_approve_policy` config field) while §3.3/§8.1 leave it open — would drive an unnecessary runtime-spec fork if the operator picks the gate-site option | applied — §8.3 made conditional (materialization-site UNRESOLVED; fork owed **only if** config-field site chosen) |
| **harness-adversarial-reviewer** (genuine dedicated agent, adopts SKILL.md; 26 tool-uses, re-grounded every cite) | **APPROVE-WITH-CLASS-2.** All six fork-vs-impl calls correct by direct read; keystone (gate-always-fires) confirmed in `gate_level_rule.py`; §19.5 currency clean at v1.32; **no silently-absorbed fork**. F2-01: G3's `edited_proposal:str` claim is *correct* for the runtime carrier it names, but the real issue is a **runtime-`str` ↔ CP-`Mapping` carrier drift** + an omitted IMPL-via-structured-elicitation branch. F1-01/02/03: in-`max()` is inference (tag it); guard the "no-fork" branch; tag uncertain steps. | applied — §5 rewritten to the carrier-drift framing + D-edit.A (elicitation→IMPL) / D-edit.B (sub-fork); §1.3 `[MODERATE]` tag; §8.1 F-B3-1 silent-absorption guard |

| **advisor()** pre-done #4 | caught a **completeness gap all three reviews missed**: after G1-as-scoped, wrap-time `gate_level ∈ {AUTO,ASK}` only (per_tool never DENY, its producer unbuilt) → **G2's deny-row narrowing is behaviorally inert** (green-but-unreachable), and §4 claimed a "deny-tier tool" payoff §3 couldn't build (internal contradiction) | applied — added **G2c** (`per_tool_gate_level` producer, faithful carrier factor-out; C-AS-03/C-AS-12 declare it, `ToolContract` carrier missing) at §4.1; corrected §4; G2+G2c ship together (§8) |

**Adversarial verdict (§9.1).** APPROVE-WITH-CLASS-2; full report filed at `.harness/adversarial-review-r-fs-1-b3-design.md` (B1 arc-#6 precedent). Net: the doc's core deliverable — the fork-vs-impl classification — is **correct at HEAD**; the two genuine forks (F-B3-1 §19.5 authoring-schema *iff* a new declared field; F-B3-2 G4b timeout-degradation-disposition = Class-1 halt-execution) are correctly identified and routed; the one Class-2 finding sharpened G3's reasoning without changing its IMPL core. The post-review advisor #4 G2c finding closed a green-but-unreachable trap (the only blocking completeness hole) — no classification changed (G2c is IMPL).

**Key re-grounding wins over the spine ledger** (the value of this design pass): (1) **machinery-built-unwired** not unbuilt; (2) the **all-ASK persona floor** makes conditional skip impossible even when wired (the ledger missed this — the real keystone); (3) the override is an **in-`max()` floor reconfiguration** (§19.5), spec-permissioned per-tier (fail-safe is cleared contract, not an invented default), **not** a post-`max()` bypass; (4) the **G4a/G4b split** (attribute-impl vs control-flow-fork); (5) **G2b cross_trust=NONE is spec-correct**, not a gap; (6) **HandoffContext is spec-legitimately-minimal**, a distinct summarization arc.

---

## §10 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/r-fs-1-b3-smart-hitl-design-v1.md` |
| Arc | R-FS-1 child arc B3 (smart-HITL), design leg |
| Posture | mode-agnostic (process-substrate); X-AL-3-clean (ZERO `design-substrate/**` or `harness-*/src/**` edit) |
| HEAD at authoring | `8608bc1` |
| Precedent | `.harness/r-fs-1-b1-topology-orchestration-design-v1.md` (B1-DESIGN, design-first PR) |
| Ground truth read | `hitl_gate_composer.py`, `hitl_required_consumption.py`, `effective_palette.py`, `gate_level_rule.py`, `per_step_override_evaluator.py`, `hitl_timeout_degradation.py`; CP spec v1.2 **§19.1/§19.4/§19.5** (composition + `_hitl_required` truth table + operator-policy override surface) + v1.15 §19.1.1; runtime spec §14.8.2/§14.8.7 (NOTE 6-ii/6-iv); `cp_20_hitl_gate_composer_underspec` (origin), `step_dispatch_timeout` (FULLY-APPLIED, distinct), `rewrite_tool_call` (Reading-D defer), `c_rt_18 carrier-drift` (APPLIED), `hitl_gate_as_pause_trigger` (acted-on) |
| Forks owed | F-B3-1 (§19.5 override authoring-schema — conditional; fork *iff* a new declared field is minted), F-B3-2 (timeout-degradation-disposition — certain Class-1); EDIT carrier-drift sub-fork conditional (D-edit.B only) |
| Next | B3-spec-1 (F-B3-1, preceded by C10⊥C11 dyadic council) after this doc's decorrelated review + PR merge |
| Decorrelated review | **complete** — advisor ×4 (incl. the §19.5 in-`max()` correction + the G2c green-but-unreachable catch) + Codex [P2] (fixed) + genuine adversarial agent **APPROVE-WITH-CLASS-2** (filed `.harness/adversarial-review-r-fs-1-b3-design.md`); all findings applied (§9) |

---

*End of R-FS-1 B3 smart-HITL design. Decides; does not author spec/plan/code. Downstream: B3-spec-1/2 → B3-plan → B3-impl-N per §8.3. R-CL-Q1→C1 remain BLOCKED behind R-FS-1.*
