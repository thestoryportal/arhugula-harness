# Adversarial Review — B2-spec-2 (MCP_TRUST gate-axis materialization)

## Summary

- **Arc reviewed:** R-FS-1 B2 multi-server MCP, **B2-spec-2** leg (gate-axis materialization, F2-02 + T-B2-2).
- **Artifacts:** `design-substrate/Spec_Control_Plane_v1_35.md` (NEW §19.1.2 `MCP_TRUST_GATE_LEVEL_FLOOR`); `.harness/class_1_fork_b2_spec_2_gate_axis_materialization.md`; `.harness/clearance/Spec_Control_Plane-v1_35-cleared-2026-06-16.md`; pointer/ledger refreshes (`CLAUDE.md` §2.3, `harness-cp/CLAUDE.md` §1.2, `claude-artifact-pointers.md` §2.3, `beyond-mvp-capability-boundary-ledger.md`, reshape fork §5/§6).
- **HEAD reviewed at:** `10b3998d`. Posture: design-phase / X-AL-3 bundled-absorption (SPEC-ONLY; no `harness-*/src` edit).
- **Date:** 2026-06-16.

> **⚠ Class-scale disambiguation (load-bearing — the two taxonomies are inverted).** This report uses the **task / §2.7.6 fork-severity polarity the caller acts on: Class 1 = BLOCKING (architectural defect / X-AL-3 extension / unmaterializable), Class 2 = should-fix-pre-merge (scope error / missing reciprocal / drift), Class 3 = informational doc-hygiene.** This is the OPPOSITE of the `harness-adversarial-reviewer` SKILL's native §4.1 scale (where Class 1 = minor / Class 3 = severe). Read every class label below on the task polarity.

- **Finding count:** Class 1 (blocking): **0** · Class 2 (should-fix): **0** · Class 3 (informational): **3**.
- **Highest-severity finding:** F3-01 (stale `gate_level_rule.py` docstrings — register for B2-impl; do NOT fix pre-merge).
- **Verdict:** **APPROVE-WITH-FINDINGS.** The scope-ONLY-CP claim is correct, the floor table is sound, and every load-bearing cite resolves byte-exact at HEAD. No blocking finding; the three Class-3 findings are doc-hygiene to fold into the B2-impl arc, not merge gates.

---

## What was verified byte-exact at HEAD `10b3998d` (the load-bearing chain)

| Claim | Grounded at | Result |
|---|---|---|
| v1.15 §19.1.1.1 row-3 spec-silence ("per-tier → gate-level mapping is §0.8-carried … content is spec-silent") | `Spec_Control_Plane_v1_15.md:67` | ✓ byte-exact (also change-note (i) line 49) |
| v1.2 §19.1 formula names `per_mcp_server_trust_floor(mcp_server)` | `Spec_Control_Plane_v1_2.md:1014`, `:1627`, `:1667` | ✓ the composition term pre-exists |
| `gate_level()` composes ONLY 3 axes (`PER_TOOL_GATE_LEVEL`+`BLAST_RADIUS`+`PERSONA_TIER`) | `gate_level_rule.py:214-218` | ✓ `mcp_trust` absent from `per_axis_floors` |
| `mcp_trust_tier` is a present-but-unconsumed `GateLevelInput` field | `gate_level_rule.py:104` | ✓ |
| `max()` is over escalation rank `AUTO<ASK<DENY` | `gate_level_rule.py:63-76` (`_GateRank`/`_RANK`), `:220-221` | ✓ |
| U-CP-91 "`mcp_trust_tier` … NEVER overridden" landed commitment | `gate_level_rule.py:131-132` | ✓ verbatim quote matches |
| `Axis.MCP_TRUST` already a member, value `"mcp-trust"` (NOT `Axis.MCP_TRUST_TIER`) | `cp_shared_types.py:193`, `:206` | ✓ |
| `MCPTrustTier` is exactly 4 members (L0–L3) | `cp_shared_types.py:172`, `:180-189` | ✓ |
| Inert composer constant `mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE` | `hitl_gate_composer.py:462` | ✓ |
| `five_axis_composition.py` passes `mcp_trust_tier` into `gate_level()` which drops it (vacuous) | `five_axis_composition.py:111-118` | ✓ |
| Runtime §14.8.2 step-4c (v1.49) names `mcp_server_trust_tier` as composer input | `Spec_Harness_Runtime_v1.md:50` | ✓ verbatim: `_hitl_required(persona_tier, blast_radius_tier, mcp_server_trust_tier, per_tool_gate_level)` |
| Runtime v1.51 explicitly carves the gate-axis/composer-wiring to B2-spec-2/B2-impl | `Spec_Harness_Runtime_v1.md:20` | ✓ "gate_level() still composes only 3 … axes … un-flattening it (F2-02) … are the B2-spec-2 leg" |
| AS §10.3 reciprocal cross-ref already points forward to B2-spec-2 (no new AS reciprocal owed) | `Spec_Action_Surface_v1.md:898` | ✓ |

**Conclusion of the cite sweep:** ZERO phantom cites. Every file:line / §section / symbol the spec and fork cite resolves byte-exact at HEAD. The `:131-132` U-CP-91 cite, the `:462` cite, the `:104` field cite, the §19.1.1.1-row-3 cite, the v1.2 formula cite, and the runtime step-4c cite are all real and quoted accurately.

---

## Class 1 findings (BLOCKING — architectural defect / X-AL-3 extension / unmaterializable)

**None.** Walked the discriminators explicitly:

- **X-AL-3 anti-extension — clean (verified, not asserted).** v1.35 mints NO new contract ID (it is a sub-section of the existing C-CP-19 §19.1), NO new ADR, NO new fail class, NO new enum member, NO `MCPTrustTier`/`GateLevel` member change. The §19.1 composition formula has named `per_mcp_server_trust_floor(mcp_server)` since v1.2 (`Spec_Control_Plane_v1_2.md:1014`); v1.35 supplies the spec-silent table that v1.15 §19.1.1.1 row 3 explicitly deferred ("owed at follow-on spec-extension arc"). This is the textbook *materialize-the-deferred-content* shape, not a contract-surface extension. `Axis.MCP_TRUST` already exists (`cp_shared_types.py:206`); the spec correctly notes it is making the floor-table determinate, not minting the axis. **X-AL-3-clean is TRUE.**
- **Floor table is materializable + monotone + floor-only (verified against the real `max()` mechanics).** Under `max()` over rank `AUTO(0)<ASK(1)<DENY(2)`: `AUTO` is the identity element, so a high-trust→`AUTO` cell contributes nothing and can never lower the composed gate below blast/persona/per-tool. Monotone-decreasing in trust holds: `DENY(2) ≥ ASK(1) ≥ ASK(1) ≥ AUTO(0)`. The locked T-perm-1 composition + the U-CP-91 non-override commitment are honored (loosening was the foreclosed alternative). **Sound.**
- **Scope-ONLY-CP is correct (the claim most at risk of being wrong — verified, holds).** Every element of the §19.1.2 "Producer" paragraph's runtime chain is ALREADY committed on cleared specs: (a) runtime v1.49 §14.8.2 step-4c names `mcp_server_trust_tier` as the composer input (`:50`); (b) runtime v1.51 line 20 *explicitly scopes* the composer resolved-host read + gate-axis un-flattening to B2-spec-2/B2-impl; (c) §27.8 commits the `MCPServerTrustLevel→MCPTrustTier` projection; (d) v1.51 §14.9.10 commits the tool→server routing index / resolved host. The §19.1.2 producer paragraph therefore *describes* already-committed runtime behavior — it does not *extend* it. The mirror precedent is exact: runtime v1.49 line 50 already ruled "the exact `GateLevelInput` carrier-shape touch is a B3-plan concern (U-CP-43), NOT a C-CP-19 spec change." **No runtime-spec amendment is owed; no AS-spec amendment is owed (the AS §10.3 reciprocal at `:898` already forward-points to B2-spec-2); no ADR/ADD/PRD/CXA change is owed.**

---

## Class 2 findings (SHOULD-FIX PRE-MERGE — scope error / missing reciprocal / drift)

**None.** The scope claim, the floor-table soundness, and the reciprocal-completeness all hold (see Class 1 walk + the rejected-findings section). No pre-merge scope correction or reciprocal is owed.

---

## Class 3 findings (informational — doc-hygiene; fold into B2-impl, NOT merge gates)

### F3-01 — `gate_level_rule.py` "spec-silent" docstrings become stale on merge (register for B2-impl docstring refresh)

- **Location:** `harness-cp/src/harness_cp/gate_level_rule.py` — module docstring `:6-13` + `:26-27`; field docstring `:105-110`; `GateLevelComputation` docstring `:138-141`; `gate_level()` body docstring `:190-195`. All assert variants of *"per-tier → gate-level mapping is spec-silent … owed at follow-on spec-extension arc"* and *"MCP_TRUST 4th axis remains unmaterialized per §0.8 row 2 PARTIAL-ADVANCE."*
- **Defect:** The moment v1.35 merges, "spec-silent … owed at follow-on arc" is factually false — the table is now committed at CP §19.1.2. This is the **stale-carry-text disposition** pattern (a finding flagged at v_N gets resolved downstream but the carry-text is not refreshed).
- **Discriminator (task scale):** Class 3 informational — it is a code-docstring describing spec state, not a contract/scope/architecture defect; it does not block merge and (critically) MUST NOT be fixed in this PR.
- **Why it matters:** A future Phase-7 implementer reading `gate_level_rule.py` will see "spec-silent" and may not realize the mapping is now committed.
- **Resolution path:** Fold the `gate_level_rule.py` docstring refresh into the **B2-impl** arc (fork §4 item 2 "realize §19.1.2 at `gate_level_rule.py` `per_axis_floors`" — the realizing edit naturally rewrites these docstrings). **Do NOT touch `harness-cp/src` in this SPEC-ONLY PR** — that would break the clean SPEC-ONLY / §11.4 posture. Note: fork §4 explicitly registers only the `hitl_gate_composer.py:462` docstring (item 4); the `gate_level_rule.py` docstrings (5+ sites) are NOT explicitly enumerated as registered B2-impl scope. Recommend the fork §4 add an explicit line so the refresh is not missed at B2-impl. Confidence **[HIGH]** (the staleness is mechanical; the disposition is the only judgment).

### F3-02 — Runtime v1.51 "3 of 5 axes" framing is loose post-v1.35 (pre-existing; reconcile at a future runtime delta)

- **Location:** `design-substrate/Spec_Harness_Runtime_v1.md:20` — *"`gate_level()` still composes only 3 of 5 axes (the `mcp_trust_tier` gate axis stays the inert hardcoded constant…)."*
- **Defect:** Post-v1.35 the precise framing is **"3-of-4 → 4-of-4 §19.1 D5-layer axes"** (the four §19.1 HITL axes). The "3 of 5" count folds in the orthogonal §19.3 `SANDBOX_TIER` D2-layer axis (`Axis` enum is 5-member at `cp_shared_types.py:212`), which `gate_level()` genuinely never composes. The arc itself caught this exact conflation: the reshape-fork §5 as-built correction (staged diff) explicitly flags *"(b) the composition is 3-of-4 → 4-of-4 §19.1 D5-layer axes (the '3-of-5'/'4-of-5' count … conflated in the orthogonal §19.3 `SANDBOX_TIER` D2-layer axis)."*
- **Discriminator (task scale):** Class 3 informational — **pre-existing on cleared v1.51 (PRESERVED VERBATIM), NOT introduced by this arc.** It is loose-but-not-wrong (`gate_level()` truly never composes `SANDBOX_TIER`). It does NOT make the runtime spec incorrect, and it does NOT flip the scope verdict to "runtime amendment owed."
- **Resolution path:** Reconcile at the next runtime-spec delta (a future B2-impl or B-arc runtime touch); no action in this PR. Confidence **[HIGH]**.

### F3-03 — `beyond-mvp-capability-boundary-ledger.md` carries the old `Axis.MCP_TRUST_TIER` / "3-of-5" carve-out framing below the new LANDED annotation

- **Location:** `.harness/beyond-mvp-capability-boundary-ledger.md` — the B2-spec-2 carve-out paragraph (registered 2026-06-16) names `Axis.MCP_TRUST_TIER` and "3-of-5→4-of-5"; the **wrong** enum name (it is `Axis.MCP_TRUST`) and the conflated count.
- **Defect:** The pre-existing carve-out prose carries the wrong enum name + count.
- **Discriminator (task scale):** Class 3 informational, and **already mitigated in this very PR**: the staged diff PREPENDS a "✅ LANDED 2026-06-16 — As-built corrections to the carve-out framing below: (a) the `Axis` enum member is `Axis.MCP_TRUST` (already present), not `Axis.MCP_TRUST_TIER`; (b) the composition is 3-of-4 → 4-of-4 §19.1 D5-layer axes…" annotation directly above the stale prose. The correction is present; the old prose is preserved verbatim below it (forward-only ledger discipline).
- **Resolution path:** None required — the prepended as-built correction discharges it. (Noted only for transparency; the arc handled it correctly.) Confidence **[HIGH]**.

---

## Findings considered and rejected (what was attacked and held)

1. **X-AL-3 silent extension (the most load-bearing check).** Audited whether v1.35 mints any primitive / contract ID / enum member / fail class / ADR change. It does not — §19.1.2 is additive sub-content under the existing C-CP-19 §19.1, supplying v1.15's explicitly-deferred table. `Axis.MCP_TRUST` pre-exists at `cp_shared_types.py:206`. **Held — X-AL-3-clean.**
2. **Forward-cite phantom (full cite sweep).** Spot-grounded every file:line / §section / symbol in the spec + fork against HEAD `10b3998d` (table above). The U-CP-91 `:131-132`, the `:462`, the `:104`, the §19.1.1.1-row-3, the v1.2 formula, and the runtime step-4c cites all resolve byte-exact. **Held — zero phantom cites.** (Minor: the spec change-note cites `:214-221` for the `max()`; the dict opens at 214 and the `max()` runs at 220-221 — an inclusive range capturing the construct, accurate not phantom.)
3. **Scope-ONLY-CP / "ZERO runtime-spec change" (the claim most likely to be wrong).** Verified each leg of the runtime chain is already committed (v1.49 step-4c input naming; v1.51 line-20 explicit B2-spec-2 carve-out; §27.8 projection; §14.9.10 routing index). The §19.1.2 producer paragraph describes — does not extend — runtime behavior. **Held — no runtime amendment owed.**
4. **"ZERO AS-spec change" / missing reciprocal.** B2-spec-1 added an AS §10.3 reciprocal cross-ref (telemetry projection). Checked whether the gate-floor materialization owes a NEW reciprocal: AS §10.3 (`Spec_Action_Surface_v1.md:898`) ALREADY forward-points to "the separate B2-spec-2 leg" for the gate-axis. The gate-floor mapping homes CP-side (the trust-framework function lives in CP per `harness-cp/CLAUDE.md` §1.4). **Held — no new AS reciprocal owed.**
5. **Cross-spec drift grep (all siblings, incl. OD).** Grepped `design-substrate/**` for `MCP_TRUST_GATE_LEVEL_FLOOR` / `§19.1.2` / `per_mcp_server_trust_floor` cite-shapes. The new symbols appear in no sibling (net-new in v1.35); the `per_mcp_server_trust_floor` hits are the pre-existing v1.2 formula term. OD spec has zero MCP_TRUST cite-shape. **Held — no sibling-spec drift, no OD reciprocal.**
6. **Floor-table soundness — L3→AUTO.** AUTO is rank 0 (the `max` identity), so the trust axis contributes nothing at highest trust; it can never lower the gate below blast/persona/per-tool. **Held — L3→AUTO is provably safe (never lowers the gate).**
7. **Floor-table soundness — L0→DENY (redundant or defense-in-depth?).** The §27 dispatch trust gate (`PerServerTrustEvaluator.evaluate(server_name, …)`) independently refuses remote-L0 at registration/dispatch. The §19.1.2 `DENY` gate-floor bites only a non-remote/allow-listed L0 server that nonetheless reaches the gate. **Held — defense-in-depth, conservative, not redundant-harmful.**
8. **Floor-only / monotone direction (T-B2-2 probe vs council).** Re-derived the `max()`-foreclosure independently: loosening is not expressible as a floor under `max()`, and U-CP-91 (`:131-132`) makes `mcp_trust` non-override a landed on-main commitment — trust-loosening would reverse on-main + break locked T-perm-1. The CLAUDE.md §10.9 probe-first / nameable-tension discriminator correctly routes this to probe-resolved (a council would collapse to single-voice). **Held — probe-resolution is the right mechanism; floor-only is structurally forced.**
9. **Telemetry/gate/dispatch three-consumer distinctness.** Confirmed §19.1.2 (`MCPTrustTier→GateLevel`, gate `max()`) is orthogonal to §27.8 (`MCPServerTrustLevel→MCPTrustTier`, telemetry span attr) and §27 dispatch (`PerServerTrustEvaluator` keyed on `server_name`). All three consume `MCPTrustTier`; only §19.1.2 feeds `gate_level()`. **Held — no consumer conflation.**
10. **L2_SANDBOX_ALL → ASK (the one genuine deployment-judgment cell).** The fork tags this **[MODERATE]** (Table A chose ASK; Table C's AUTO was the reversible alternative the operator declined). This is an operator-ratified value choice on a reversible knob, not a defect. **Held — operator-ratified judgment, not a finding;** the [MODERATE] honesty tag is appropriate and correctly surfaced.
11. **Verification-shape (grep vs e2e).** The spec defers closure to a B2-impl e2e contrasting-baseline test (L0→DENY forced / L3→blast-decides) + the `five_axis_composition.py` pass-through becoming non-vacuous. This is the correct by-execution shape for a SPEC-ONLY arc (the table is inert until impl). **Held — verification-shape is sound and deferred to the right arc.**
12. **Halt-route-split-AC.** The arc cleanly splits SPEC (commit the table now) from IMPL (wire `per_axis_floors` + composer resolved-host at B2-impl) — the materializable atom landed, the impl atom registered as B2-plan/B2-impl forward items. **Held — clean split, no silent absorption.**

---

## Disposition

**APPROVE-WITH-FINDINGS.**

- **0 Class-1 (blocking) findings.** The scope-ONLY-CP claim is correct (runtime + AS + ADR all already committed / already-reciprocal); the floor table is sound (monotone, floor-only, L0→DENY defense-in-depth, L3→AUTO never-lowers); X-AL-3-clean is verified true (no new primitive/contract/enum/ADR); every load-bearing cite resolves byte-exact at HEAD `10b3998d`; the enum-name (`Axis.MCP_TRUST` not `MCP_TRUST_TIER`) and count (3-of-4 not 3-of-5) drifts the task warned about were caught and self-corrected by the arc.
- **0 Class-2 (should-fix-pre-merge) findings.**
- **3 Class-3 (informational) findings**, all doc-hygiene to fold into B2-impl (F3-01 `gate_level_rule.py` stale docstrings — recommend the fork §4 explicitly register them; F3-02 runtime "3 of 5" pre-existing loose framing; F3-03 already mitigated by the prepended as-built correction). None is a merge gate.

The SPEC-ONLY posture is intact (no `harness-*/src` edit), the delta-only-spec preservation is honored (§19.1/§19.1.1/§19.3/§19.4/§19.5 + §27.1–§27.8 PRESERVED VERBATIM; only additive §19.1.2), and the clearance marker + fork doc + pointer refreshes are consistent with the amendment. Cleared for merge.

*Reviewer: harness-adversarial-reviewer (dedicated agent). Severity polarity: task / §2.7.6 fork scale (Class 1 = blocking). HEAD `10b3998d`. 2026-06-16.*
