# C10 — Action-Safety / Blast-Radius — contribution

**Topic:** R-FS-1 arc B2 (multi-server MCP, DESIGN leg) — the AS `MCPServerTrustLevel` → CP `MCPTrustTier` projection (`_trust_tier_from_level`, currently a vacuous stub collapsing to `LEVEL_0_REFUSE_REMOTE`).

**Single question:** does the projection need a safety mechanism *inside* it (transport-aware clamp / conservative floor / registration-time refuse), or is C10's posture already discharged by the separate per-transport sandbox floor + the `PerServerTrustEvaluator`, such that the projection should be pure identity-by-ordinal?

---

## 1. C10 position

**Identity-by-ordinal suffices. The projection should be a faithful 1:1 value-set map (`L0→LEVEL_0`, …, `L3→LEVEL_3`) with NO clamp, NO conservative floor, and NO registration-refuse logic inside it.** Every containment property the prompt asks about already lives — *materialized and non-vacuous* — in two separate, multiplicatively-composing mechanisms that I verified at HEAD: the **per-MCP-transport `sandbox_tier_floor`** (AS C-AS-10 §10.1 / ADR-D2 §1.3) and the **`PerServerTrustEvaluator`** policy gate (CP C-CP-27 §27). Putting a *second* transport clamp inside the projection would duplicate the floor's transport authority (one-source-of-truth violation) and is the symmetric over-gating discipline failure (FM-F). C10's actual VETO is aimed the *other* way: I veto **retaining the current conservative-collapse-to-`LEVEL_0` as the production mapping**, because it vacates the operator's REQUIRED per-server `trust_level` declaration on the CP gate side and silently retires the locked `per_mcp_server_trust_tier` T-perm-1 axis (ADR-D2 §1.5). Identity-by-ordinal is the *fix* for that defect, not a relaxation of safety.

---

## 2. Reasoning (byte-verified cites)

### 2.1 The transport-aware clamp already exists — in the floor, not the projection

I read the floor **function body** (not just its docstring — per the `[[built-but-vacuous-reground-ledger-asis]]` discipline). At `harness-as/src/harness_as/sandbox_tier_floor.py:115-155`, `sandbox_tier_floor(...)` is **live and non-vacuous**:

- Line 141-142 — **STDIO transport → `max(TIER_3_MICROVM, floor)`** regardless of declared blast-radius.
- Lines 146-152 — remote (HTTP+SSE) keyed on `mcp_server.trust_level`: **`L0_REFUSE_REMOTE → REFUSE`** (line 148), **`L2_SANDBOX_ALL → max(TIER_4_FULL_VM, floor)`** (line 150), else `floor`.

This is byte-faithful to the canonical contract. **C-AS-10 §10.1** (`design-substrate/Spec_Action_Surface_v1.md:857-867`) tables exactly this: STDIO → `tier-3-microvm` minimum; HTTP+SSE Level 0 → `REFUSE` (sentinel) at registration; Level 2 → `tier-4-full-vm` minimum with allow-listed upstream domains. **ADR-D2 §1.3** (`design-substrate/ADR-D2.md:111-113` + summary line :67) commits the same "Tier 3 minimum for STDIO MCP transports regardless of declared blast-radius." The transport-awareness the prompt asks me to consider building into the projection is therefore **already the floor's job, and the floor performs it.** "A remote http/sse server cannot project above L1 without extra attestation" is *over-built* relative to the canonical design: a remote L2 server doesn't get clamped *down* — it gets its sandbox floor *raised* to tier-4-full-vm with egress allow-listing (the lethal-trifecta cut per ADR-D2 :53 Cluster 4 §2.3.2). Containment is by **isolation-tier raise**, not by trust-tier suppression.

### 2.2 The trust tier is one input to a `max()`, not the containment itself

Per **ADR-F4 v1.1** (cited at `design-substrate/ADR-D2.md:49`): graduated-isolation, per-tool tier = `max(contract.minimum_tier, blast_radius_floor, mcp_server_trust_tier_floor, operator_policy_floor)` per call site. The `MCPTrustTier` the projection produces is **one floor among four** feeding the monotone `max()`. The projection's job is to *deliver the operator's declared per-server trust level faithfully* into that composition; the containment math is downstream and additive. A clamp inside the projection would be inserting a fifth, redundant barrier *before* the `max()` that already exists to be the barrier.

### 2.3 The CP-side gate consumes the tier and enforces it — keyed on server_name, multi-server-ready

**C-CP-27 §27** (last substantively tabled at `design-substrate/Spec_Control_Plane_v1_10.md:380-509`) is the runtime gate the projected `MCPTrustTier` flows into. `PerServerTrustEvaluator.evaluate(server_name, primitive, tool_contract, operator_policy)` (§27.1) gates **every** MCP-as-client call (§27.6 invariant 2: "no bypass path"), with **deny-wins** (§27.6 invariant 3 / `deny_list`), tier-floor (`TIER_FLOOR_VIOLATION`), and the operator-ratified **unknown-server = ALLOW-with-tier-floor** path (§27.6 invariant 4, Decision 3.D1) where unknown servers resolve via `TierDerivationRule.CONSERVATIVE = MIN(MCPTrustTier members)` (§27.2). This is the correct home for "a conservative floor" and "a registration-time refuse" — and it *already has them*, keyed on `server_name`, hence multi-server-ready by construction. The projection feeds this gate; it must not pre-empt it.

### 2.4 Defense-in-depth is already multiplicative; a third barrier would be drift-prone

Per my §4.3 framework, the per-transport floor and the per-server trust posture **compose multiplicatively, not contend** — server-level posture sets *eligibility*, per-call floor/gate sets the *runtime gate*. The mechanical evidence seals it: `_trust_tier_from_level(level)` (`mcp_client_host_factory.py:197`) takes **only `level`** — no transport input. A transport-aware clamp would require widening the signature to re-take `mcp_transport`, duplicating the floor's transport authority and creating **a second authority for transport×level** — exactly the one-source-of-truth violation (`no-contract-widening` discriminator). The narrow signature is *positive evidence* that transport was deliberately assigned to the floor, not the projection.

### 2.5 The enums are the same closed 4-value set

AS `MCPServerTrustLevel` (`sandbox_tier_floor.py:59-67`) and CP `MCPTrustTier` (`cp_shared_types.py:172`) are the identical 4-level set; the CP docstring declares it a "Byte-exact factor-out … enumerated at … C-AS-10 §10.3" — confirmed against the spec at `Spec_Action_Surface_v1.md:877-886`. A same-set→same-set map has exactly one faithful realization: identity-by-ordinal. Any non-identity map is, by definition, either a clamp (suppressing operator intent) or a re-encoding (inviting drift).

---

## 3. What I would VETO

**VETO #1 — retaining the conservative-collapse as the production mapping (the live defect; over-gating / FM-F).** The current stub (`mcp_client_host_factory.py:197`) returns a *constant* `LEVEL_0_REFUSE_REMOTE` regardless of input. `trust_level` is a **REQUIRED, no-default operator field** (`types.py:592`); the operator declares it per server precisely so the CP gate can act on it. Collapsing it to a constant means the `PerServerTrustEvaluator` receives the same tier whether the operator declared `L0` or `L3` — **the operator's per-server declaration is vacated on the CP gate side**, and the locked `per_mcp_server_trust_tier` axis of the T-perm-1 tunable (`per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier`, ADR-D2 §1.5 / `ADR-D2.md:69`) is silently retired to a single value. "Conservative = safe" is the symmetric discipline failure to under-gating; I veto it as a *production* mapping. (As an MVP placeholder it is acceptable and honestly labelled; this arc is its retirement.)

**VETO #2 — any transport-aware clamp / extra-attestation gate / registration-refuse placed INSIDE the projection.** This duplicates C-AS-10 §10.1 floor authority and C-CP-27 §27 gate authority, requires widening `_trust_tier_from_level`'s signature to re-take `mcp_transport`, and creates a third barrier that drifts against the two single-authority mechanisms. Defense-in-depth here is *already* multiplicative (floor ⊥ evaluator); a redundant-but-drifting barrier is strictly worse than single-authority. I veto it as a one-source-of-truth violation.

**What I do NOT veto, and explicitly affirm:** pure identity-by-ordinal (`L0→LEVEL_0` … `L3→LEVEL_3`). It is the correct, safe production mapping.

---

## 4. Residual risk accepted

Identity faithfully propagates an operator's **mis-declaration** of a per-server `trust_level` (e.g., declaring a sketchy remote server `L3_ALLOW_WITH_AUDIT`). C10 accepts this residual, because the containment does not depend on the projection second-guessing the operator:

1. **The transport floor applies regardless of declared level.** A remote server declared `L0` → `REFUSE` at registration (`sandbox_tier_floor.py:148`); declared `L2` → tier-4-full-vm + egress allow-list (:150). A mis-declared remote `L3` still rides the per-tool `blast_radius_floor` and `operator_policy_floor` in the `max()`; high-blast actions remain gated by the blast-radius tier independent of MCP trust.
2. **Unknown servers never touch identity** — they take the separate `TierDerivationRule.CONSERVATIVE = MIN` path with mandatory audit (C-CP-27 §27.6 invariant 4 / Decision 3.D1). Identity governs only *operator-declared, known* servers.
3. **Mis-declaration is an operator-policy concern at declaration-time**, owned by the operator + audit ledger (trust-level assignment is recorded per C-AS-10 §10.3 + C-AS-08 composition), not a projection-time concern. Per the maximal-action-surface posture (§4.1), C10's primary defense for operator-trusted surfaces is rich tamper-evident audit + the `mcp.trust.evaluate` span (C-CP-27 §27.4), not preventive distrust of the operator's own declaration.

This residual is the *correct* operating point of the C4↔C10 T-perm-1 tension: faithful capability surface (operator declares trust), with containment carried by the floor + gate + audit, not by a paternalistic projection.

---

## 5. Confidence

**[HIGH].** The position rests on three byte-verified live mechanisms (floor body at `sandbox_tier_floor.py:115-155`, evaluator contract at `Spec_Control_Plane_v1_10.md:380-509`, the spec tables at `Spec_Action_Surface_v1.md:857-886`) plus the canonical posture (ADR-D2 §1.3/§1.5, ADR-F4 v1.1 `max()` composition). The floor-vacuity check passed — the containment my argument borrows is empirically real, not a stub — which is what licenses HIGH rather than MODERATE.

---

*Filed by C10 (Action-Safety / Blast-Radius Theorist). Voice-fidelity note: this contribution names the containment **location** and the trust **property**; it does not redesign the closed-at-4 enum, rule on whether the MCP-client capability should exist (C4), author the evaluator's gate mechanics (C11/CP), or pick the operator's per-server tier (operator decision at Stage 3). No co-primary recusal triggered — this is a pure trust-boundary-discipline question with the floor (AS) and gate (CP) mechanisms already cleared and materialized.*
