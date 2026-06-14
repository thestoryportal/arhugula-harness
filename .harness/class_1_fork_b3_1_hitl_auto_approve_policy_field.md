# Class 1 Fork — F-B3-1: `hitl_auto_approve_policy` C-RT-03 RuntimeConfig field (the §19.5 operator-policy override authoring schema, Reading-C tunable-floor)

**Type:** Class 1 (design-substrate amendment — a NEW declared `RuntimeConfig` field is minted → a new contract surface → X-AL-3 back-flow owed per the design §8.1 silent-absorption guard F1-02).

**Status:** ✅ APPLIED 2026-06-14 — operator-ratified at the B3-spec-1 front-gate 2026-06-14 (via AskUserQuestion, preceded by a genuine dyadic **C10⊥C11** council per design §3.3 / §8.1): **(Q1) default-value = READ_ONLY auto-ON** + **(Q2) materialization = a declared `hitl_auto_approve_policy` field → this narrow runtime-spec fork**. Applied at **runtime spec v1.48 → v1.49** (NEW §3 C-RT-03 field row + NEW `HITLAutoApprovePolicy` sub-model at §3.8 + §14.8.2 step-4c consumption description + clearance marker `Spec_Harness_Runtime-v1_49-cleared-2026-06-14.md`). **SPEC-ONLY** — the field is declared + its consumption semantics specified; the composer wiring lands at **B3-impl-1** (the field is **inert in production until B3-impl-1**). NO `harness-*/src/**` edit at this arc. ZERO CP-spec / IS-spec / AS-spec / ADR / ADD / PRD cascade (see §4).

---

## §1 — The gap

### §1.1 The deferred authoring schema

CP spec **v1.2 §19.5** ("Operator-policy override surface composition") + the **§19.1** floor enumeration define the *semantics* and the *per-tier permissions* of an operator-policy override of a `max()` floor, but **explicitly defer the authoring schema** (CP v1.2 §19.5 deferred-list, line 1702):

> **Deferred to implementation discretion.** … specific operator-policy override authoring schema (manifest field / API call / TUI action — composes with `Spec_Action_Surface_v1.md` C-AS-12 §12.5).

The B3 design (`.harness/r-fs-1-b3-smart-hitl-design-v1.md`, cleared #549) established (§1.3, the keystone finding) that **conditional gating is structurally impossible at HEAD** without this override: `PERSONA_TIER_GATE_LEVEL_FLOOR` maps all three persona tiers to `ASK` (`gate_level_rule.py:150`), so `max()` ≥ ASK always → `hitl_required` is always True. The only spec-acknowledged path to a sub-ASK (skippable) gate is the §19.5 operator-policy floor override — and its authoring schema is the deferred surface above. **F-B3-1 mints that schema.**

### §1.2 Why this is a fork (not impl-against-cleared-spec)

The B3 design §3.3 D-cond.2 left the materialization site **conditional**: a bootstrap-supplied override applied at the gate-site helper (consuming the §19.5-cleared semantics via impl-discretion) would have been impl-against-cleared-spec (NO fork); a **new declared `RuntimeConfig` field** is a new contract surface → narrow runtime-spec fork. The design's **silent-absorption guard (adversarial F1-02, §8.1)** is explicit:

> the "no-fork" branch is valid **only iff ZERO new declared override-policy field** is minted; ANY persisted operator-declared override field (`RuntimeConfig`/manifest/bootstrap param) is a new contract surface → the narrow fork IS owed (X-AL-3).

The operator ratified the **declared-field** materialization (Q2). Therefore **the fork IS owed.** This doc is the X-AL-3 back-flow companion to the `design-substrate/**` edit (CLAUDE.md §4.4 / §4.5).

---

## §2 — The decision (operator-ratified)

### §2.1 The field

NEW field on `RuntimeConfig` (C-RT-03 §3), carried by a NEW frozen harness-runtime sub-model `HITLAutoApprovePolicy` (§3.8):

```python
class HITLAutoApprovePolicy(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    # §19.1 line 1639 — persona_tier_floor[SOLO_DEVELOPER] → AUTO
    #   ("operator may override to auto for non-irreversible"). Default ON ⇒ READ_ONLY auto-ON.
    solo_persona_floor_auto: bool = True
    # §19.1 line 1634 — blast_radius_floor[LOCAL_MUTATION] → AUTO
    #   ("configurable to auto at solo-developer"). Default OFF ⇒ operator opt-in.
    solo_local_mutation_floor_auto: bool = False

# on RuntimeConfig:
hitl_auto_approve_policy: HITLAutoApprovePolicy = HITLAutoApprovePolicy()
```

This is **Reading C (tunable floor)** per design §3.3 — an **in-`max()` floor-value reconfiguration**, NOT Reading D's rejected post-`max()` `Mapping[(persona_tier, blast_radius_tier), bool]` bypass. The two-bool **named-cell** shape is the load-bearing choice: it can express **exactly** the two §19.1-annotated floor cells and **nothing else**, so a Reading-D post-`max()` bypass is **not representable** (there is no "skip the gate" knob — only "this specific floor cell is AUTO instead of ASK"), and EXTERNAL_* override is **structurally foreclosed** (no field can express it). Per the design checkpoint guidance: *"Pick a shape that makes post-`max()` misuse hard; don't let a `Mapping[...,bool]` become a Reading-D bypass."* — satisfied by construction.

### §2.2 The default + the arithmetic (operator Q1 = READ_ONLY auto-ON)

Default `HITLAutoApprovePolicy()` = `{solo_persona_floor_auto: True, solo_local_mutation_floor_auto: False}`. The composer applies the knobs **only when `binding.persona_tier == SOLO_DEVELOPER`** (the field is solo-scoped — see §2.3). The resulting `gate_level = max(per_tool, blast_radius_floor, persona_tier_floor, mcp_trust_floor)` per §19.1 at solo, with the default policy applied:

| Step blast radius | blast floor | persona floor (after default policy) | `max()` | Outcome |
|---|---|---|---|---|
| **READ_ONLY** | `AUTO` (§19.1 line 1633) | `AUTO` (persona knob ON) | `AUTO` | **skip** ✅ READ_ONLY auto-ON |
| **LOCAL_MUTATION** | `ASK` (knob 2 OFF) | `AUTO` | `ASK` | **gate** ✅ opt-in (flip `solo_local_mutation_floor_auto`) |
| **EXTERNAL_REVERSIBLE** | `ASK` (no knob) | `AUTO` | `ASK` | **gate** ✅ hard-stop (not representable) |
| **EXTERNAL_IRREVERSIBLE** | `ASK` (no knob) | `AUTO` | `ASK` | **gate** ✅ hard-stop (not representable) |

(`per_tool` and `mcp_trust` floors compose into the same `max()`; a `deny`-tier tool or an untrusted MCP server independently raises the gate regardless of the policy — the policy can only *lower* the two named cells, never override `per_tool`/`mcp_trust`.) Flipping `solo_local_mutation_floor_auto=True` lowers the LOCAL_MUTATION blast floor to AUTO ⇒ LOCAL_MUTATION solo actions auto-approve; EXTERNAL_* stay `ASK` (still not representable). This is **exactly** the operator's ratified posture: **READ_ONLY auto-ON / LOCAL_MUTATION opt-in / EXTERNAL_* hard-stop.**

**Spec-faithfulness of the default.** Making persona[SOLO]→AUTO the *default* (not opt-in) is consistent with CP §19.5 line 1698 — at solo-developer the *"operator IS the policy authority"* — and with §19.1 line 1639's *"operator may override to auto for non-irreversible"* (the override is permitted; the non-irreversible scope is enforced structurally because the blast floor still backstops LOCAL_MUTATION+ and EXTERNAL_*). It is a deliberate behavior change vs the current always-gate (that change *is* "smart HITL" = the gate sometimes skips), made structurally fail-safe by the blast-floor backstop and ratified by the C10⊥C11 council + operator.

### §2.3 Solo-scoping ⇒ team a registered follow-on, multi structurally foreclosed (C10 safety is structural)

The field's knobs are **persona-scoped to `SOLO_DEVELOPER`**; the composer applies them only when `binding.persona_tier == SOLO_DEVELOPER`. Consequences, each load-bearing for C10:

- **multi-tenant-compliance: structurally foreclosed.** The field **cannot express** a multi-tenant override (no `multi_*` knob; the solo knobs don't apply at multi). CP §19.5 line 1700 ("structurally prohibited") is satisfied **by construction** — there is no override *attempt* to emit a violation event for. A separate refusal guard is therefore **not owed** (it would guard an unrepresentable state).
- **team-binding: a registered owed follow-on, NOT silently dropped.** CP §19.5 line 1699 permits team override at non-`external-irreversible` cells (hash-chained audit per C-IS-06). F-B3-1 does **not** build the team override surface (the design §3.3 Reading C scoped the tunable-floor to solo). Per the FULL-SPEC directive this is **registered as owed** (§6), not deferred-and-forgotten — and it is gated behind the §19.1↔§19.5 reconciliation in §2.4 for its contested cell.

### §2.4 C10 spec-asymmetry — §19.1 ⊥ §19.5 on the external-reversible cell (registered, not resolved)

A genuine **internal inconsistency in the cleared CP spec** (the council's C10 spec-asymmetry AC):

- **§19.5 line 1696** — solo "Permitted … override of **any** `max()` floor" (and line 1699 team "non-`external-irreversible`" ⇒ permits external-**reversible**).
- **§19.1 line 1635** — `blast_radius_floor: external-reversible → ask` carries **no** solo-auto annotation (vs line 1634 local-mutation's explicit "(configurable to auto at solo-developer)").
- **§19.1 line 1640** — team `"no auto override on external-*"` (forbids external-reversible) — directly contradicts §19.5 line 1699 (permits it).

So §19.1's per-cell annotations are **more restrictive** than §19.5's per-tier statements on the **external-reversible** cell, for both solo and team. **F-B3-1 does not resolve this** (resolving a cleared-spec inconsistency in the permissive direction would be a silent design extension — X-AL-3). Instead it **sidesteps it conservatively**: the field's expressible domain is the two cells where §19.1 and §19.5 **agree** the override is permitted (persona[SOLO] line 1639 ∩ §19.5 line 1698; blast[LOCAL_MUTATION] line 1634 ∩ §19.5 line 1698). The external-reversible solo-override (the contested cell) is **not representable** and is **registered (§6) as owing a CP-spec §19.1↔§19.5 reconciliation arc** before it could be built. The operator's 2026-06-14 **EXTERNAL_* hard-stop** ratification is the **standing answer** for the contested cell.

---

## §3 — Carrier home + the C-RT-03-only decision (the Q3 trace)

### §3.1 C-RT-03 only — no C-RT-04 `HarnessContext` field

The §14.8.2 **step-4c** consumption site (runtime spec line 1937; v1.22 amendment) calls `_hitl_required(persona_tier, blast_radius_tier, mcp_server_trust_tier, per_tool_gate_level)` per C-CP-19 §19.1. The composer (`RuntimeHITLGateComposer`, constructed at bootstrap **stage-5**) reads its inputs from `binding` + its own instance state — it does **NOT** read `ctx.<field>` at dispatch. The policy is therefore threaded into the composer **at stage-5 construction** (the stage factory takes `config`, reads `config.hitl_auto_approve_policy`, and holds it as composer instance state) — exactly the way the existing opt-in fields whose consumer is the composer-itself are handled.

This is the **distinguishing trace** vs the `validator_framework` / `pause_resume_protocol` / `webhook_delivery_composer` precedents, which carry the field at **both** C-RT-03 *and* C-RT-04 **only because** the driver/composer reads `ctx.<field>` *at dispatch*. The HITL gate composer does not — so **C-RT-03 suffices; no C-RT-04 field is owed.** (Net: +1 RuntimeConfig field, +0 HarnessContext field, +0 new C-RT-NN contract, +0 fail class.)

### §3.2 The `gate_level()` carrier-shape touch → B3-plan (no CP-spec fork)

Reading C consumes the override **in-`max()`** — the composer lowers the §19.1-annotated floor cell **before** `gate_level()` composes the max. The exact code-carrier shape for *how* the lowered floor reaches `harness_cp.gate_level_rule.gate_level()` (a new optional param on the frozen `GateLevelInput`, or a separate override argument) is a **U-CP-43 plan-carrier concern**, **not** the C-CP-19 §19.1 *spec* contract. `GateLevelInput` is `frozen, extra="forbid"` (`gate_level_rule.py`), so the carrier-shape touch is a real code change — but it is a **CP-plan** decision (B3-plan), not a CP-spec amendment. **No CP-spec file is edited by F-B3-1.** (Per advisor pre-substantive: *"GateLevelInput is a U-CP-43 PLAN-carrier concern, not the C-CP-19 SPEC contract → no CP-spec fork … forward only the code-carrier-shape touch to B3-plan."*)

---

## §4 — Downstream cascade

| Artifact | Cascade |
|---|---|
| **Runtime spec** | v1.48 → v1.49: NEW §3 C-RT-03 field row + NEW `HITLAutoApprovePolicy` sub-model §3.8 + §14.8.2 step-4c consumption description. (this arc) |
| **CP spec** | **ZERO edit.** §19.5 already specs the override surface + tier-permissions; F-B3-1 materializes the deferred authoring schema, it does not change §19.1/§19.5. The §19.1↔§19.5 internal inconsistency (§2.4) is **registered (§6)**, not patched here (resolving it = a separate CP-spec arc). |
| **CP plan** | The `gate_level()` carrier-shape touch (U-CP-43) is sequenced at **B3-plan** (§3.2) — not this arc. |
| **AS spec / IS spec / ADR / ADD / PRD** | ZERO. `hitl_auto_approve_policy` + `HITLAutoApprovePolicy` are intra-runtime-spec (operator-supply config + a harness-runtime sub-model). Verified by grep this arc — no consumer references the field name (field does not exist pre-v1.49). |
| **Runtime plan** | B3-plan decomposes the consumption (composer stage-5 ingestion + in-`max()` application + the C10 audit emission AC) into atomic units (U-RT-NN) per design §8.3. |

---

## §5 — Acceptance criteria carried to B3-impl-1 (the two council ACs)

**AC-1 (C10 audit-wiring guard — `[[built-but-vacuous-reground-ledger-asis]]` trap).** CP §19.5 line 1698 mandates *"each override emits audit-ledger entry per C-CP-20 §20.1."* B3-impl-1 MUST verify, by execution, that each policy-applied floor-lowering (each skip the policy causes) emits the §20.1 audit-ledger entry — and that the emission is **not vacuous** (BODY-read, not docstring; a populated entry, not a constant). A green unit test that asserts the call-site exists is **insufficient** — exercise the actual skip path and confirm the audit entry lands. **The skip MUST NOT go live before this is verified wired.**

**AC-2 (C10 spec-asymmetry — §2.4).** B3-impl-1 + the B3 adversarial review MUST confirm the field's expressible domain is **exactly** the two §19.1-blessed cells (persona[SOLO], blast[LOCAL_MUTATION]); a contrasting-baseline test MUST show **EXTERNAL_REVERSIBLE solo-override is not representable** (the §2.4 asymmetry is resolved structurally, not silently widened). If a future arc wants external-reversible solo-override, it MUST first land the §19.1↔§19.5 reconciliation (§6).

---

## §6 — FULL-SPEC register (owed follow-on build arcs — NOT deferred/dropped)

Per the FULL-SPEC standing directive (`[[feedback-full-spec-beyond-mvp-nothing-deferred]]` — nothing sacrificed; every un-built spec capability is a registered BUILD arc, design back-flow pre-authorized), the §19.5 cells F-B3-1 does **not** build are **registered**, not deferred-and-forgotten:

1. **Team-binding override surface** (§19.5 line 1699 — team override at non-`external-irreversible`, hash-chained audit per C-IS-06). Owed as a follow-on F-B3-1-team arc. Its **local-mutation** cell is buildable directly (§19.1 line 1640 permits non-external); its **external-reversible** cell is contested (§19.1 line 1640 forbids ⊥ §19.5 line 1699 permits) → gated behind item 3.
2. **Multi-tenant-compliance** — no build owed (structurally foreclosed by solo-scoping per §2.3; CP §19.5 line 1700 satisfied by construction).
3. **CP-spec §19.1↔§19.5 reconciliation arc** (the §2.4 external-reversible inconsistency). A Class-1 fork **against the CP spec** that decides whether external-reversible solo/team override is a real §19.5 feature (requiring §19.1 line 1635/1640 amendment) or correctly foreclosed by §19.1's per-cell floors. **Prerequisite** for any external-reversible override. The operator's 2026-06-14 EXTERNAL_* hard-stop is the standing answer until this arc opens.

These are leads for their arc-open, not commitments materialized here (presence-not-correctness — re-ground at each arc-open).

---

## §7 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_b3_1_hitl_auto_approve_policy_field.md` |
| Arc | R-FS-1 child arc **B3** (smart-HITL), **B3-spec-1** leg (F-B3-1) |
| Posture | design-phase bundled-absorption (X-AL-3 back-flow companion to the runtime-spec v1.49 edit) |
| HEAD at authoring | `deff887` |
| Design authority | `.harness/r-fs-1-b3-smart-hitl-design-v1.md` §3.3 (D-cond.2 Reading C) + §8.1 (F-B3-1) + §8.3 (sequence); cleared #549 |
| Operator ratification | B3-spec-1 front-gate 2026-06-14 — Q1 = READ_ONLY auto-ON; Q2 = declared field + narrow fork (preceded by a genuine dyadic C10⊥C11 council) |
| Spec authority | CP spec **v1.2 §19.1** (floor enumeration; lines 1633-1642) + **§19.4** (`_hitl_required` truth table) + **§19.5** (override surface + per-tier permissions; lines 1692-1702) — defined at v1.2, carried verbatim to head v1.32, NOT re-tabled (delta-baseline §-cite convention) |
| Decision | NEW `RuntimeConfig.hitl_auto_approve_policy: HITLAutoApprovePolicy` (two-bool solo-scoped tunable-floor sub-model) + §14.8.2 step-4c in-`max()` consumption; C-RT-03 only; SPEC-ONLY, impl → B3-impl-1, inert until then |
| Cascade | runtime spec v1.49 only; ZERO CP/IS/AS/ADR/ADD/PRD; `gate_level()` carrier-shape → B3-plan (U-CP-43) |
| ACs to B3-impl-1 | AC-1 C10 audit-wiring (verify §20.1 emission not-vacuous before skip goes live); AC-2 C10 spec-asymmetry (EXTERNAL_REVERSIBLE not representable) |
| FULL-SPEC register | team override + §19.1↔§19.5 reconciliation registered as owed build arcs (§6) — not dropped |
| Decorrelated review | harness-adversarial-reviewer (genuine dedicated agent, pre-merge) + `just codex-review` + advisor() — record at the clearance marker |
| Next | B3-spec-2 (F-B3-2 timeout-degradation-disposition, Class-1) per design §8.3 |

---

*End of F-B3-1 Class 1 fork. Materializes the CP §19.5 deferred authoring schema as a runtime-spec field; resolves NOTHING in CP §19.1/§19.5 (the internal asymmetry is registered, not patched). SPEC-ONLY; impl at B3-impl-1.*
