# S1 — C-AS-02 `sandbox_tier_floor` Reconciliation Recommendation

*`systems-architect` pass S1, Phase-7 tension-resolution mode (SKILL.md §4A). Authored 2026-05-15. This is a **recommendation**; the operator decides; a later `spec-writer` pass applies. No `design-substrate/` file, plan, spec, or source edited in this pass.*

---

## 0. Scope

Reconcile the C-AS-02 `sandbox_tier_floor` contract self-contradiction surfaced by the AS-plan verbatim audit (`verbatim_audit_as_plan.md`, F3-01 / Pattern A2) and re-stated three-way by the R3 implementation-planner (`revision_R3_as_plan.md` §9 / Q-R3-1). The defect spans `Spec_Action_Surface_v1.md` §2.2, §2.3, §11.1 — and, this pass finds, §12.1 and §10.2 as cross-referencing sections — into ONE coherent `sandbox_tier_floor` signature + lookup contract.

---

## 1. The contradiction — precise statement

`sandbox_tier_floor` is called at **four distinct spec call sites** plus a §10.2 reference, with **three different signatures**:

| Spec site | Call as written | Has `tool`? | Trust-level input? |
|---|---|---|---|
| §2.2 composition formula | `sandbox_tier_floor(tool, call_site_context.deployment_surface, call_site_context.blast_radius_tier, call_site_context.mcp_transport)` | **yes** (4-arg) | no — only `mcp_transport` |
| §10.2 prose ("Floor input" row) | `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport)` | yes (4-arg) | no |
| §12.1 5-axis `gate_level` body | `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport)` | yes (4-arg) | no |
| §11.1 sub-agent body | `sandbox_tier_floor(blast_radius, deployment_surface, mcp_transport)` | **NO** (3-arg) | no |

**Disagreement 1 — the `tool` argument.** §2.2 / §10.2 / §12.1 pass `tool` as the first argument; §11.1 omits it entirely and passes only 3 arguments. The same named function has two arities in one spec.

**Disagreement 2 — the trust-level input (the R3 three-way gap).** §2.3's `sandbox_tier_floor` lookup table has **nine rows**; rows 4–6 are keyed on **MCP server trust level**:

> | Remote MCP, trust level 0 (refuse-remote) | `REFUSE` ... |
> | Remote MCP, trust level 2 (sandbox-all) | `max(tier-4-full-vm, blast_radius_floor)` ... |
> | Remote MCP, trust level 1 (signed-pinned) OR trust level 3 (allow-with-audit) | `blast_radius_floor` |

The lookup table **requires a trust-level value** to select among rows 4–6. But **no call site threads a trust level** — every call site passes `mcp_transport` (a `MCPTransport` enum: STDIO / Streamable-HTTP / SSE / …), not an MCP-server trust level (the 5-tier Level-0..3 framework). Trust level is *not derivable* from transport: a Streamable-HTTP server can be Level 1, 2, or 3. §2.3 row 3 ("STDIO MCP transport, any blast-radius") is transport-keyed and *is* expressible from the signature; rows 4–6 are trust-level-keyed and are **NOT expressible from any current `sandbox_tier_floor` signature**. The §2.3 table demands an input its own §2.2 call site does not supply — the spec under-specifies its own contract.

**Why this is genuinely three-way.** §2.2 has `tool` but no trust level; §2.3 needs a trust level (and is silent on whether it needs `tool`); §11.1 has neither `tool` nor trust level and is the *shortest* signature. No two of the three agree.

The R3 sub-options for Disagreement 2:
- **G-1** — trust level is an explicit `sandbox_tier_floor` argument (signature grows a `mcp_trust_level` / `mcp_server` parameter).
- **G-2** — trust level is carried by an existing argument (e.g., the `tool` / call-site object carries enough context to resolve trust level internally).

---

## 2. Authority-chain placement

`CLAUDE.md` §1.3 chain: **ADR → ADD → PRD → per-axis spec → per-axis plan**. ADR-D2 (sandbox-tier composition) and ADR-F4 (foundational sandbox) sit **above** `Spec_Action_Surface_v1`. The AS spec's §2 explicitly cites **ADR-D2 v1.1 §1.5.1** as the source of the `sandbox_tier_floor` axis ("D2 §1.5.1 NEW"). The ADR is therefore the tiebreaker for the signature shape — *if it commits one*.

### 2.1 What ADR-D2 / ADR-F4 actually commit

**ADR-F4 v1.1 §Decision** — commits the `max()` composition `max(contract.minimum_tier, blast_radius_floor, mcp_server_trust_tier_floor, operator_policy_floor)`. **F4 does NOT name `sandbox_tier_floor` at all** — `sandbox_tier_floor` is a D2 addition. F4 is silent on the `sandbox_tier_floor` signature; it is *not* the governing artifact for this tension.

**ADR-D2 v1.1 §1.5.1** (the cited authority) — gives the canonical form:

> `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport)` ... `// D2 NEW`
>
> followed by a `where:` block whose rows include `(remote MCP, level 0) → REFUSE`, `(remote MCP, level 2 sandbox-all) → max(Tier 4, blast_radius_floor)`, `(remote MCP, level 1 / level 3, *) → blast_radius_floor`.

**ADR-D2 v1.1 §1.4** — gives the sub-agent form:

> `sandbox_tier_floor(blast_radius, deployment_surface, mcp_transport)` — **3-arg, no `tool`.**

### 2.2 The decisive finding: the contradiction is INHERITED FROM the ADR, not introduced by the spec

This is the load-bearing fact for the recommendation. **ADR-D2 itself carries the identical contradiction.** D2 §1.5.1 writes the 4-arg form *with* `tool`; D2 §1.4 writes the 3-arg form *without* `tool`. And D2 §1.5.1's `where:` block keys rows on `(remote MCP, level N)` while the signature only carries `mcp_transport` — D2's *own* `where:` block is inexpressible from D2's *own* signature.

Consequence for authority-chain reasoning:

- **Disagreement 1 (`tool` arg)** — the spec did not diverge from the ADR; the spec **faithfully transcribed** an ADR that is internally inconsistent (§1.5.1 4-arg vs §1.4 3-arg). The spec is not "the artifact in error" here. Conforming the spec to "the ADR" is impossible because the ADR disagrees with itself.
- **Disagreement 2 (trust level)** — likewise: the §2.3 table is a faithful transcription of D2 §1.5.1's `where:` block, which itself presupposes a trust-level lookup the D2 signature never threads. The under-specification originates **at the ADR layer**.

Per SKILL.md §4A.4: this is **not** the "an artifact simply diverged from the chain → conform it" case. The authority chain is *internally contradictory at its governing node*. The chain does not under-determine the *answer* (the architecturally correct reconciliation is determinable — see §3), but it does mean the fix cannot be a pure spec conformance: **ADR-D2 itself requires a revision** in the same reconciliation, or the spec revision will re-diverge from its cited ADR.

---

## 3. Recommended canonical contract

The §2 discipline (probabilistic-deterministic boundary; five-axis; decision-ordering) plus the ADR-D2 §1.5.1 substance determine the architecturally correct shape. The recommendation has three parts.

### 3.1 Disagreement 1 — the `tool` argument: **RECOMMEND `tool` IS retained (4-arg family canonical); §11.1 is the divergent site**

**Decided** by the substance of D2 §1.5.1's own `where:` block, independent of the §1.4-vs-§1.5.1 surface inconsistency:

The `where:` block's first two rows — `(computer-use model bound, *) → Tier 4` and `(LLM-generated code execution, *) → Tier 4` — are **properties of the tool**, not of `blast_radius` / `deployment_surface` / `mcp_transport`. "Computer-use model bound" and "LLM-generated code execution" are tool/call-site classifications (cf. C-AS-01 §1.3 forced-tier rules, U-AS-02's `forced_tier(ctx)` landed unit). A 3-arg `sandbox_tier_floor(blast_radius, deployment_surface, mcp_transport)` **cannot evaluate rows 1–2** of its own lookup table. Therefore the 3-arg §11.1 / D2 §1.4 form is **structurally under-specified** — it is missing the input its lookup table's top two rows require. The 4-arg form with `tool` is the only one of the two that can evaluate the full table.

→ **Recommendation:** the canonical signature retains `tool`. The §2.2 / §10.2 / §12.1 4-arg form is canonical. **§11.1 and ADR-D2 §1.4 are the divergent sites** — the sub-agent call site must thread `tool` (the sub-agent's tool/call-site) through to `sandbox_tier_floor`, exactly as the parent call site does. This is architecturally forced, not a preference: a sub-agent invoking a computer-use-bound or code-execution tool must hit rows 1–2 of the floor table just as the parent does; omitting `tool` at the sub-agent boundary would silently skip the strongest forcing conditions — a containment regression, precisely the failure ADR-D2 §1.4's own rationale ("attacker-controlled sub-agent dispatch ... containment regression") exists to prevent. Authority basis: ADR-D2 §1.5.1 lookup-table semantics (rows 1–2 are tool-keyed) + ADR-D2 §1.4 stated rationale.

### 3.2 Disagreement 2 — trust level: **RECOMMEND G-1 (explicit argument), via an explicit `mcp_server` / trust-level parameter**

**Decided** at the architectural level, by the probabilistic-deterministic boundary discipline (§2.2) and by parity with the enclosing `max()` composition:

1. **The §2.2 `max()` composition already threads `mcp_server` as a sibling floor.** §2.2 line 196 calls `mcp_server_trust_tier_floor(call_site_context.mcp_server)` — `call_site_context.mcp_server` is an *already-defined call-site field*. The trust-level input `sandbox_tier_floor` needs is **the same `mcp_server`** the sibling floor consumes. G-1 does not invent a new input; it threads an input the contract already has at the call site into a function that demonstrably needs it.

2. **Transport ≠ trust level — the inputs are not interchangeable.** `mcp_transport` (STDIO / Streamable-HTTP / SSE) and MCP-server trust tier (Level 0–3, the Cluster 4 §2.3.3 four-level posture, surfaced in the spec at §10.3) are orthogonal. §2.3 row 3 is transport-keyed; rows 4–6 are trust-level-keyed. A correct `sandbox_tier_floor` needs **both**. The current signature carries only transport; it must additionally carry the trust-level input.

3. **G-2 (carrier-borne) is rejected on determinism + auditability grounds.** G-2 would have `sandbox_tier_floor` reach into `tool` / a call-site object and resolve trust level internally. That (a) hides a control-flow-significant input inside an opaque carrier, defeating the §2.5 / C-AS-15 `assigned_tier_reason` audit surface — which exists to make "which floor won and on what input" verifiable at the `sandbox.enter` event; (b) breaks signature parity with the four sibling floors in the §2.2 `max()`, every one of which takes its discriminating input as an *explicit, named argument* (`call_site_context.taint_state`, `.mcp_server`, `.persona_tier`); (c) makes the function's behavior depend on carrier-internal structure that no other spec section pins. The deterministic outer harness (§2.2 invariant: "every floor expresses its concern") requires each floor's inputs to be explicit and inspectable. G-1 keeps `sandbox_tier_floor` parallel to its siblings; G-2 makes it the lone exception.

→ **Recommendation:** **G-1.** `sandbox_tier_floor` gains an explicit MCP-server / trust-level parameter — preferably `mcp_server` (the same object §2.2 already passes to `mcp_server_trust_tier_floor`), from which trust level is read, OR a directly-typed `mcp_server_trust_level` if the operator prefers the narrowest possible parameter. *The choice between passing `mcp_server` vs a pre-resolved `mcp_server_trust_level` is a minor proposing-level detail for the `spec-writer` — both satisfy G-1; passing `mcp_server` is recommended for call-site parity with §2.2 line 196.*

**Trust-level cardinality check (confirms the 5-arg shape is stable).** §2.3 rows 4–6 and §10.3 enumerate exactly **four** MCP-server trust levels (Level 0 refuse-remote / 1 signed-pinned / 2 sandbox-all / 3 allow-with-audit), per Cluster 4 §2.3.3. §10.3's parenthetical "ADR-D5 v1.3 §1.5 five-tier framework" refers to a **different** cross-axis composition — the CP-axis `per_mcp_server_trust_floor` axis at Control Plane session 3 — not the `sandbox_tier_floor` lookup. There is no fifth trust-level row; the recommended `(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server) -> SandboxTier | REFUSE` shape is not enlarged by it. The `mcp_server` argument's typing is therefore the straightforward "carries a 4-valued trust level" case.

### 3.3 The recommended canonical signature

**Proposing** (the operator ratifies; `spec-writer` materializes the exact parameter names/order):

```
sandbox_tier_floor(
    tool,                  # rows 1–2: computer-use / code-execution forcing (tool-keyed)
    deployment_surface,
    blast_radius_tier,
    mcp_transport,         # row 3: STDIO-keyed
    mcp_server             # rows 4–6: remote-MCP trust-level-keyed (Level 0–3); REFUSE sentinel
) -> SandboxTier | REFUSE
```

— a **5-argument** signature. Note this is exactly the shape U-AS-06's plan Signatures block already declared (the audit's F3-01 "5-param `sandbox_tier_floor`, adds `mcp_trust_level`"): **the plan was not wrong about the arity — it correctly detected the spec/ADR was 1 argument short.** The plan's instinct was right; what was missing was the spec/ADR authority for it. This recommendation supplies that authority direction (pending operator ratification).

All four+ call sites conform to this one signature:
- §2.2 / §10.2 / §12.1 — already 4-arg with `tool`; **add the `mcp_server` argument** (already available as `call_site_context.mcp_server`).
- §11.1 sub-agent — currently 3-arg; **add both `tool` and `mcp_server`**, becoming the full 5-arg form (the sub-agent's own tool + call-site).

---

## 4. Spec sections the `spec-writer` pass must edit

The `spec-writer` pass (after operator ratification) edits the following. **Edit shapes only — text is the `spec-writer`'s to author.**

| Section | Edit shape |
|---|---|
| **§2.2** composition formula | Change the `sandbox_tier_floor(...)` call from 4-arg to 5-arg — add `call_site_context.mcp_server` as the fifth argument. |
| **§2.3** `sandbox_tier_floor` lookup table | No row changes needed — the 9 rows are correct. Add a contract note that the table's rows 4–6 are keyed on the **MCP-server trust level** read from the `mcp_server` argument, and rows 1–2 on the `tool` argument; i.e., make explicit which argument keys which row band. This closes the "table needs an input the signature lacks" gap by tying each row band to a named argument. |
| **§2.1** composition signature | No change — `sandbox_tier(tool, call_site_context)` is unaffected; `call_site_context` already carries `mcp_server`. (Confirm in passing that `call_site_context`'s field set is documented to include `mcp_server` — it is used at §2.2 line 196 already.) |
| **§11.1** sub-agent tier-resolution signature | Change `sub_agent_sandbox_tier` body's `sandbox_tier_floor(blast_radius, deployment_surface, mcp_transport)` to the canonical 5-arg form — add `tool` and `mcp_server`. The `sub_agent_sandbox_tier` *outer* signature may also need a `tool` / `mcp_server` parameter so it has them to pass through (currently 4 params: `parent_sandbox_tier, blast_radius, mcp_transport, deployment_surface`). |
| **§12.1** 5-axis `gate_level` body | Change the `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport)` call to the 5-arg form — add `mcp_server` (the `gate_level` outer signature already has `mcp_server` as a parameter). |
| **§10.2** "Floor input to `sandbox_tier_floor()`" row | Update the prose `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport)` reference to the 5-arg form for consistency. |
| **Change-note / §[traceability]** | Record the C-AS-02 signature reconciliation; bump AS spec version. |

### 4.1 ADR-D2 must be revised in the same reconciliation — NOT spec-only

Per §2.2: the contradiction originates at ADR-D2. A spec-only fix re-diverges the spec from its cited ADR (`CLAUDE.md` invariant I-1 — citations resolve byte-exact; an authority-chain inversion otherwise). **ADR-D2 v1.1 §1.4 and §1.5.1 must both be revised** so the ADR's two `sandbox_tier_floor` renderings agree on the 5-arg form, and §1.5.1's `where:` block is annotated to tie its `(remote MCP, level N)` rows to an explicit `mcp_server` argument. This is an **ADR-level edit** — it is above the `spec-writer`'s spec-only remit and is the part of this tension that makes the fork **Class 1 (halt-execution)**: a foundational/derivative ADR requires revision before the affected units (U-AS-06, U-AS-09) land. (Under the back-flow-deprecated posture, the ADR-D2 revision is done in-CLI, but it is still an ADR edit, sequenced before or with the spec edit, and requires explicit operator authorization since it touches a D-ADR.)

---

## 5. Downstream consumers — units the R3.1 micro-pass finalizes

The reconciliation, once landed, unblocks these AS plan units (per `verbatim_audit_as_plan.md` + `revision_R3_as_plan.md`):

| Unit | What finalizes |
|---|---|
| **U-AS-06** | The `sandbox_tier_floor` carrier unit. Its Signatures block already declares the 5-arg form (F3-01) — the audit flagged it as divergent *only because the spec was short*. Once the spec/ADR adopts the 5-arg signature, U-AS-06's body is conformant; R3.1 finalizes its acceptance criteria + the `tool` parameter's type (see the `ToolMetadata` Pattern-B carrier question — separate tension, not in S1 scope). |
| **U-AS-09** | `sub_agent_sandbox_tier` carrier. The audit's Pattern-A2 second instance — its 5-param body is the *consumer-side propagation* of the same gap. Once §11.1 adopts the 5-arg `sandbox_tier_floor` and a `tool`-bearing `sub_agent_sandbox_tier` outer signature, U-AS-09's body conforms. R3.1 finalizes it in the same micro-pass as U-AS-06. |
| **U-AS-05** | `blast_radius_floor` carrier — consumed by `sandbox_tier_floor`. No signature change, but verify it still composes; likely no edit. |
| **U-AS-10** | `lookup_cell_with_forcing` — consumes the §9 forcing conditions that feed §2.3 rows 1–2. Confirm the `tool`/forcing path is consistent; likely no signature edit from S1, but R3.1 should re-check. |
| **U-AS-13** | `mcp_transport_floor` — sibling, transport-keyed; unaffected by the trust-level add (confirms the transport ≠ trust-level orthogonality). No edit. |
| **U-AS-08, U-AS-16, U-AS-33** | Propagation consumers of the C-AS-02 surface (`AssignedTierReason`, `sandbox.policy.assigned_tier_reason`, the export manifest). The `assigned_tier_reason` enum value `sandbox_tier_floor` is unaffected by the signature change; no S1-driven edit, but U-AS-33's manifest carrier citations re-verify once U-AS-06/09 conform. |

The R3.1 micro-pass finalizes **U-AS-06 and U-AS-09 bodies specifically** once this reconciliation lands; U-AS-05/10/13 are re-verify-only.

---

## 6. Decision vocabulary — what is decided vs proposing vs open

| Element | Status | Basis |
|---|---|---|
| Canonical signature retains `tool`; §11.1/D2 §1.4 are the divergent 3-arg sites | **decided** | ADR-D2 §1.5.1 `where:` rows 1–2 are tool-keyed → a 3-arg form cannot evaluate its own lookup table. Architecturally forced. |
| Trust level is threaded as an **explicit argument** — G-1, not G-2 | **decided** (authority-chain-determinate; operator ratification owed) | Probabilistic-deterministic boundary (§2.2 "every floor expresses its concern" + the C-AS-15 `assigned_tier_reason` audit surface) + signature parity with the four sibling `max()` floors, all explicit-arg. G-2 hides a control-significant input in an opaque carrier. "Decided" here means *decidable from the §2 discipline* — it is a recommendation; the operator ratifies (SKILL.md §4A.4). |
| 5-argument canonical signature `(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server)` | **proposing** | The arity and argument set are decided; exact parameter names/order is `spec-writer` materialization. |
| Pass `mcp_server` object vs a pre-resolved `mcp_server_trust_level` scalar | **proposing** | Both satisfy G-1. `mcp_server` recommended for parity with §2.2 line 196's `mcp_server_trust_tier_floor(call_site_context.mcp_server)`. Minor; operator may pick the scalar. |
| ADR-D2 §1.4 + §1.5.1 must be revised alongside the spec | **decided** | The contradiction originates at the ADR; a spec-only fix re-diverges from the cited ADR (I-1). |
| Whether `sub_agent_sandbox_tier`'s *outer* signature gains `tool`/`mcp_server` params | **proposing** | Forced in substance (it must have them to pass through), but the exact outer-signature shape is `spec-writer`/`implementation-planner` materialization. |

**Nothing in this tension is genuinely *open* (operator-decision-required because the authority chain under-determines it).** The R3 framed G-1 vs G-2 as an open fork; this pass finds the §2 discipline (deterministic-boundary + sibling-floor parity + the audit-surface requirement) **determines G-1**. The one residual operator choice — `mcp_server` object vs `mcp_server_trust_level` scalar — is a *proposing*-level materialization detail, not an architectural fork: either way the signature is 5-arg and trust level is explicit. The operator's role here is **ratification** of a determinate recommendation plus **authorization** of the ADR-D2 edit (because it touches a D-ADR), not adjudication between live architectural alternatives.

---

## 7. Fork classification

Per `Project_Workflow_v1_8.md` §2.7.6: **Class 1 (halt-execution).** A design-phase artifact requires revision before the affected units land — and not only the AS spec but **ADR-D2** (a D-ADR). U-AS-06 and U-AS-09 landings remain halted until: (1) operator ratifies this recommendation; (2) ADR-D2 §1.4/§1.5.1 revised (in-CLI, back-flow deprecated, but ADR-level + operator-authorized); (3) `spec-writer` reconciles C-AS-02 §2.2/§2.3/§11.1/§12.1/§10.2 + version bump; (4) `implementation-planner` R3.1 micro-pass finalizes U-AS-06/U-AS-09 bodies; (5) re-clear; (6) land.

---

## 8. Tiebreaker check

The single verifiable fact that makes this recommendation determinate: **confirm no ADR-D2 / ADR-F4 revision postdates `Spec_Action_Surface_v1` v1.1 that re-commits the `sandbox_tier_floor` signature.** Checked: ADR-D2 is at v1.1 (P3c-CK iter-1 close); its v1→v1.1 change-note records F2-05 / F1-01 / F1-02 mechanical alignment — F1-01 touched §1.4's `sub_agent_sandbox_tier` *parameter naming* (`parent_tier`→`parent_sandbox_tier`) but **not** the `sandbox_tier_floor` arity. No D2/F4 revision re-enumerates the `sandbox_tier_floor` signature. ADR-F4 is silent on `sandbox_tier_floor` entirely (it is a D2 addition). **The recommendation is determinate**: the contradiction is a genuine ADR-D2-level internal inconsistency, not a spec drift from a settled ADR, and the §2-discipline resolves both disagreements without an open architectural fork.

**Load-bearing-artifact flag:** the resolution **requires editing ADR-D2, a D-ADR.** Per SKILL.md §4A.5 this requires **explicit operator sign-off** beyond ratification of the spec direction. It touches no `CLAUDE.md` anti-leakage rule and no F-ADR (F4 is untouched — it never named `sandbox_tier_floor`).

---

*End S1 recommendation. Operator decides; `spec-writer` (C-AS-02 §2.2/§2.3/§11.1/§12.1/§10.2 + ADR-D2 §1.4/§1.5.1) and `implementation-planner` (R3.1 micro-pass, U-AS-06/U-AS-09) apply on ratification.*
