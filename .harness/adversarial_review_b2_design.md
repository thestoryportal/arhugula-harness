# Adversarial Review — R-FS-1 B2-DESIGN (multi-server MCP client)

**VERDICT: APPROVE-WITH-FINDINGS**

## Summary
- Mode: Phase-7 pre-implementation review (design leg of an X-AL-3-gated arc)
- Artifact reviewed: `.harness/r-fs-1-b2-multi-server-mcp-design-v1.md` (+ council `b2-trust-projection-{c10,c11}.md`)
- Date: 2026-06-15 · HEAD `c0fc9f3`
- Finding count by class (§4.1 review-severity scale): Class 3: 0 · Class 2: 2 · Class 1: 3
- Highest-severity finding: **F2-01** — D3/§3.3/§6 mis-attribute the projection-stub defect: the projection output is *telemetry-only* today; fixing it does NOT un-flatten the gate axis (a different hardcoded site does).
- Disposition recommendation: **clear the design leg with the F2-01 rationale correction folded into the B2-spec leg** (it changes what the spec amendment must say, not whether B2 proceeds). The X-AL-3 classification, the cite-grounding, the fail-class count discipline, and the sequencing call are all sound.

This is a strong, unusually well-grounded design doc. Nearly every byte-exact cite I spot-checked resolved (see "what I verified" below). The one substantive defect is a causal-chain over-claim that the design's own grounding discipline (`[[built-but-vacuous-reground-ledger-asis]]` / grep-vs-e2e) should have caught — it verified the stub *returns a constant* and that the axis *string exists*, but never traced where the projection output is *read*.

---

## Class 2 findings (moderate — current-phase revision)

### F2-01 — D3/§3.3/§6 mis-attribute the stub defect: the projection output is telemetry-only; fixing it does not un-flatten the gate axis
- **Decision-claim vocabulary:** *decided* (the trace is conclusive, not reading-dependent).
- **Location:** design §3 item 3 ("the `PerServerTrustEvaluator` finally acts on per-server intent across N servers"); §2 D3 ("the constant-collapse silently flattens the *locked* `per_mcp_server_trust_tier` axis of the T-perm-1 tunable"); §6 ("vacates the required operator field + flattens the locked T-perm-1 `per_mcp_server_trust_tier` axis"); council `b2-trust-projection-c10.md` §3 VETO #1 + `c11.md` §2.
- **Defect:** The design asserts the stub (`_trust_tier_from_level` → constant `LEVEL_0_REFUSE_REMOTE`) flattens the *gate* axis and that retiring it makes the `PerServerTrustEvaluator` act on per-server intent. **Neither is true at HEAD.** Traced every read of `.trust_tier` (the projection output):
  - `host.trust_tier` flows ONLY into `MCPServerInfo` (`runtime_tool_dispatcher_factory.py:184`, inside the `lookup` callable) → consumed by `MCPClientNamespaceEmitter.set_attribute(ATTR_MCP_SERVER_TRUST_TIER, …)` (`mcp_client_namespace_emitter.py:199`) → the `mcp.server.trust_tier` **span attribute**. The `mcp_client_host.py:128-130` docstring states this verbatim: "read by the dispatcher (U-RT-67) to populate the `mcp.server.trust_tier` span attribute."
  - The **dispatch trust gate** (`runtime_tool_dispatcher.py:628`) calls `evaluate(self._mcp_client_host.server_name, MCPPrimitive.TOOL, contract, self._trust_policy)` — it resolves per-server trust from `TrustPolicy` keyed on `server_name`, and **never reads `host.trust_tier`** (`runtime_tool_dispatcher.py` has zero references to `trust_tier` / `gate_level` / `mcp_trust`).
  - The **gate-level `max()` composition** axis `mcp_trust_tier` is fed by a *separate hardcoded constant* `mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE` at the production HITL gate path (`hitl_gate_composer.py:462`), independent of the projection.
- **Discriminator that classifies as Class 2:** (a) — affects the substantive content of a current-phase artifact (the §5 spec-amendment surface + D3 rationale); resolution is self-contained to the B2-spec leg and does NOT require upstream revision (the *mapping decision* — identity-by-ordinal — is unaffected; only the *rationale* and the *amendment scope* change).
- **Evidence:** `grep -rn "trust_tier" harness-runtime/src harness-cp/src` → the only non-telemetry write of a gate-composition `mcp_trust_tier` is the hardcoded constant at `hitl_gate_composer.py:462`; `host.trust_tier` is read only at `runtime_tool_dispatcher_factory.py:184` (telemetry lookup).
- **Why this matters (the load-bearing consequence):** §5's spec-amendment surface scopes the trust-projection fix as "the `PerServerTrustEvaluator` finally acts on per-server intent" (CP — C-CP-27 §27 row). That framing under-scopes the actual reshape: to genuinely un-flatten the *gate* `per_mcp_server_trust_tier` axis, the B2-spec leg must ALSO wire the per-server `host.trust_tier` (or the per-server declared `trust_level`) into the `hitl_gate_composer` `GateLevelInput.mcp_trust_tier` input — which is currently a hardcoded constant at a site the design's §5 table does NOT mention. If the spec leg fixes only the projection (per the current §5 framing), the gate axis stays flat and the design's headline rationale remains unmet.
- **Nuance the finding does NOT contest:** identity-by-ordinal is still the correct *mapping* — the council's faithfulness argument (same closed 4-value set; one-source-of-truth) is sound and independently verified (see rejected findings). The defect is that the design conflates "fix the projection" with "un-flatten the gate axis"; they are separable, and the second requires touching `hitl_gate_composer.py:462`, not just the projection.
- **Resolution path:** B2-spec leg — correct §3.3/§6/D3 rationale to scope the projection fix as a *telemetry-fidelity + declared-intent-propagation* fix, and either (a) add the `hitl_gate_composer` `mcp_trust_tier` wiring to the §5 spec-amendment surface as the site that actually un-flattens the gate axis, or (b) explicitly register the gate-axis wiring as a separate forward item if it is out of B2 scope. No design-substrate edit owed from THIS leg (it is pre-fork).

### F2-02 — §5 spec-amendment surface omits the `hitl_gate_composer` / gate-composition consumer of the trust axis
- **Decision-claim vocabulary:** *decided*.
- **Location:** design §5 table (the row set) + §5 prose "the ~8 carriers + ~10 `ctx.mcp_client_host` consumers (dispatcher_factory info-lookup, `shutdown.py` drain-all-hosts, `mutable_context`, docker/e2b drivers, `validator_escalation_composer`)".
- **Defect:** The §5 consumer enumeration is accurate for the `mcp_client_host` *field reshape* (exactly 10 files reference `mcp_client_host` in `harness-runtime/src/`, verified — the design's "~10" is precise). BUT the trust-axis reshape (D3) has a consumer the enumeration misses entirely: the HITL gate composition (`hitl_gate_composer.py:457-462` → `gate_level()` → `five_axis_composition` / `gate_level_rule.GateLevelInput.mcp_trust_tier`). This is the site where the `per_mcp_server_trust_tier` axis the design claims to un-flatten actually enters the `max()`. Because §5 scopes the trust amendment only at "C-CP-27 §27 trust projection home," the spec leg has no pointer to the gate-composition consumer.
- **Discriminator that classifies as Class 2:** (a) — substantive completeness gap in the §5 amendment surface; a missed consumer is a spec-coverage hole (the impl-plan §"Spec coverage" exit-criterion shape).
- **Evidence:** `hitl_gate_composer.py:462` `mcp_trust_tier=MCPTrustTier.LEVEL_0_REFUSE_REMOTE` (hardcoded); `gate_level_rule.py:104` + `five_axis_composition.py:71` carry `mcp_trust_tier: MCPTrustTier` as the locked-axis input. None appears in §5.
- **Resolution path:** B2-spec leg — extend the §5 amendment surface (or the B2-plan revision-pass) to name the gate-composition `mcp_trust_tier` wiring as part of the trust reshape, OR register it as a separate forward item with explicit rationale. (Composes with F2-01; same root.)

---

## Class 1 findings (minor — documentation drift)

### F1-01 — D1's `server_name`-vs-`client_name` distinctness rationale is forward-looking, presented as current-state
- **Location:** design §2 D1 ("**Key = the host's `server_name`** … NOT `client_name`"; "keep config-key (`client_name`) and runtime-identity (`server_name`) distinct").
- **Defect:** At HEAD the factory sets `server_name=entry.client_name` (`mcp_client_host_factory.py:176`) — the two identities are the **same value** today. D1's rationale for keying on `server_name` "to keep config-key and runtime-identity distinct" is notional/forward-looking, not a current-state distinction. The key choice is still defensible (routing + trust + spans all read `server_name`), but the *distinctness* justification is aspirational. Honest framing would tag it as such.
- **Resolution:** Inline note in the D1 rationale (or at the B2-spec leg) that `server_name == client_name` today and the distinctness is a forward property the `ServerName` alias would preserve, not a present-state fact.

### F1-02 — §1 cite `:629` for `server_name` is one of a pair; design elsewhere writes `:624/:629/:718` and `:617/:624/:628/:718` inconsistently
- **Location:** design §1 ("reads `self._mcp_client_host.server_name` (`:624/:629/:718`)") vs §1 dispatcher bullet ("`:617/:624/:628/:718`") vs §9 verification ("dispatcher `:617/:624/:628/:718`").
- **Defect:** Minor cite-set inconsistency: the design variously lists `:629` and `:628` for adjacent dispatcher reads. Verified at HEAD: `:617` (tool_registry.get), `:624` (server_name in the ToolContractUnknownError f-string), `:628` (trust_evaluator.evaluate `server_name` arg), `:718` (emit-span `server_name`). `:629` is the continuation line of the `:624` error string. Both `:628` and `:629` resolve to real reads; the inconsistency is cosmetic, not a phantom cite.
- **Resolution:** Inline — pick one canonical cite-set (`:617/:624/:628/:718`) and use it consistently.

### F1-03 — §1 paraphrase "binds to `ctx.mcp_client_host`" omits that §14.9.3 binds via `materialize_runtime_tool_dispatcher_stage`, not the host factory
- **Location:** design §1 ("§14.9.3 stage-3a — `materialize_mcp_client_host_stage(config: RuntimeConfig) → MCPClientHost` … binds to `ctx.mcp_client_host`").
- **Defect:** Faithful to the spec (§14.9.3 line 3874: "Binds to `ctx.mcp_client_host`"). Minor: the dispatcher/evaluator/emitter binding is the *separate* stage-5 `materialize_runtime_tool_dispatcher_stage` factory (§14.9.3 lines 3876-3881), and the design's §5 table row collapses both into "§14.9.3 stage-3a + stage-5 factory." Accurate but slightly compressed — the reshape touches TWO factory contracts (host materialization at 3a, dispatcher/index/per-host-resolver at 5), and the per-host resolver/driver (D4) lives in the stage-5 factory, not stage-3a. The §5 row should not read as if one factory carries all of it.
- **Resolution:** Inline at the B2-spec leg — split the §5 "§14.9.3 stage-3a + stage-5 factory" row so the host-materialization (3a) and the routing-index + per-host-resolver/driver (5) obligations are distinct.

---

## Findings considered and rejected (transparency — substantive checks applied)

1. **A4 — Fabricated citations (the highest-value attack).** Spot-checked a representative load-bearing sample byte-exact at HEAD `c0fc9f3`; ALL resolved:
   - `mcp_client_host_factory.py:173` (`entry = config.mcp_clients[0]`) ✓; `:197` (the constant-collapse stub `return MCPTrustTier.LEVEL_0_REFUSE_REMOTE`) ✓.
   - `runtime_tool_dispatcher.py:617` (tool_registry.get) ✓, `:624` (server_name) ✓, `:628` (evaluate) ✓, `:718` (span server_name) ✓.
   - `runtime_tool_dispatcher_factory.py:269/:281` (`config.mcp_clients[0]` for resolver AND driver) ✓ — the B2↔B6 seam is real.
   - `sandbox_tier_floor.py:141-152` (STDIO→TIER_3_MICROVM; L0→REFUSE; L2→TIER_4_FULL_VM; L1/L3→floor) ✓ live + non-vacuous.
   - `per_server_trust_evaluator.py` unknown-server refuse-default (`_CONSERVATIVE_MIN_TIER = LEVEL_0_REFUSE_REMOTE`, `_default_tier_resolver` CONSERVATIVE→MIN) ✓ (design cites `:88/:102-115`; actual: `_CONSERVATIVE_MIN_TIER` at :88, `_default_tier_resolver` at ~102-116 — resolves).
   - `types.py:1242` (`mcp_clients: list[MCPClientConfig]`) ✓, `:592` (`trust_level: MCPServerTrustLevel`, REQUIRED no-default) ✓, `:1650` (`mcp_clients: dict[ClientName, MCPClient]`) ✓.
   - `ADR-D2.md:69` — the T-perm-1 axis string `per_tool_gate_level × per_mcp_server_trust_tier × persona_tier × blast_radius_tier × sandbox_tier` ✓ byte-exact at line 69.
   - **Outcome:** no fabricated-cite finding. This is exceptional grounding discipline; the design's "re-grounded by §-anchor after the #550 dossier drifted" claim is borne out.

2. **Spec-cite drift (§14.9.x by §-anchor).** §14.9.1 dispatch body (steps read `ctx.mcp_client_host`) ✓; §14.9.3 factory `→ MCPClientHost` singular (line 3874) ✓; §14.9.6 inv 1 "MCP host instance started exactly once per bootstrap … one subprocess per `MCPClientHost`; HTTP transport opens one client connection pool per host … Idempotent restart out of scope at v1" (line 3916) ✓ verbatim; C-RT-04 confirmed as the `HarnessContext` schema section (§4) with `mcp_client_host: MCPClientHost` singular at line 2282 ✓. **Outcome:** the design's §-anchor re-grounding survived; no stale-line-number finding (the design explicitly disclaimed the drifted #550 line numbers and re-resolved).

3. **Fail-class count-preservation discipline (the precision trap).** Design §5 claims "Preserve the existing '8 new' + '9th' verbatim counts; this is the 10th." Verified: §14.9.5 says "8 new fail classes added" (8 rows) ✓; §14.9.9 says "the §14.9.5 '8 new fail classes' count is PRESERVED VERBATIM; this is the 9th, declared here" (line 3983) ✓. So `RT-FAIL-MCP-TOOL-NAME-COLLISION` would indeed be the 10th, and the count-preservation pattern reference is byte-faithful. **Outcome:** no count-drift finding — this is a model application of the discipline.

4. **A8 — Framing contamination / X-AL-3 anti-extension (the most load-bearing rule).** §7 classifies B2 as X-AL-3 territory and routes the actual `design-substrate/**` amendment to a B2-spec Class 1 fork + clearance marker. THIS PR authors only `.harness/`. Verified the doc makes NO design-substrate edit and correctly stays pre-fork (recommend, don't apply). The §2 framing ("operator ratifies at the B2-spec leg") is correct posture. **Outcome:** no X-AL-3 violation — the classification is correct and the doc is clean.

5. **D3 mapping correctness (council outcome — probed independently, not taken on council authority).** Verified the two enums are the same closed 4-value set: AS `MCPServerTrustLevel` {L0_REFUSE_REMOTE, L1_SIGNED_PINNED, L2_SANDBOX_ALL, L3_ALLOW_WITH_AUDIT} (`sandbox_tier_floor.py:59-67`) ↔ CP `MCPTrustTier` {LEVEL_0…LEVEL_3} (`cp_shared_types.py:172`, docstring "Byte-exact factor-out … enumerated at … C-AS-10 §10.3" ✓ against AS spec §10.3 lines 877-886). Identity-by-ordinal is the unique faithful realization. The "transport belongs to the floor not the projection" argument is verified (the floor at `:141-152` prices in transport; `_trust_tier_from_level` takes only `level`). The "where it lives = CP" claim is verified (`harness-as/CLAUDE.md §1.4` line 48: "function lives in CP; AS surface declares the per-transport floor only"). **Outcome:** the *mapping* is sound — I did NOT find a C10 safety requirement that belongs inside the projection. (The defect is the *rationale*, F2-01, not the mapping.)

6. **D2 fail-loud-on-collision foreclosure check.** Fail-loud-at-bootstrap honors the detect-then-refuse discipline; the design explicitly registers server-qualified addressing as a forward item (not silently foreclosed) and flags collision policy for ratification. **Outcome:** no silent-foreclosure finding — D2 is well-scoped and the one genuinely deployment-dependent call is correctly surfaced.

7. **D4 B2↔B6 coupling check.** Verified both B2 and B6 land on the same `config.mcp_clients[0]` consumption (`runtime_tool_dispatcher_factory.py:269` resolver / `:281` driver). The "per-host outer (B2) × per-tool inner (B6) nests cleanly" claim is structurally sound: B2 generalizes `[0]`→per-host-keyed; B6 adds an inner per-tool map. No hand-waved coupling — the §14.9.9 "per-server-uniform / per-tool is a future arc" scope boundary backs the nesting. **Outcome:** no co-design-barrier finding; B2-first is the right call.

8. **D5 silent-defer check (halt-route-split-AC pattern).** Idempotent-restart is correctly NOT folded into B2 and is registered as a named forward arc (`B2-restart`, sibling to the §14.9.6 inv 1 "operator-driven restart arc" the spec already names). Under FULL-SPEC this is a registered BUILD item, not a deferred-and-dropped scope narrowing. **Outcome:** no silent-defer finding — this is the correct halt-route discipline.

9. **Cross-spec drift probe (§C mandatory).** Grepped CXA `Cross_Axis_Composition_Document_v2_20.md` for `mcp_client_host` / `PerServerTrustEvaluator` / `MCPTrustTier` — zero matches, so the field reshape does not directly touch a declared CXA seam (no CXA amendment owed). The §8 ripple claim (`[[shared-is-shape-change-ripples-cross-axis-field-asserts]]` + CXA-P1 enumeration) is grounded: `test_cxa_pattern_p1.py` exists at `harness-runtime/tests/integration/`, so the field-shape change will plausibly trip cross-axis field asserts at impl time — the design correctly warns to "run the broader suite." **Outcome:** no missed-sibling-spec finding; the §8 ripple warning is accurate.

10. **Council primary-collapse check (§10.9 nameable-tension discriminator).** The C10⊥C11 tension is genuinely nameable (action-safety wanting a projection-internal safety mechanism vs operator-burden wanting faithful pass-through), and C10's veto runs opposite to the naive framing (it vetoes RETAINING the stub, not relaxing safety) — so the convening was not a cosmetic-consultant collapse. **Outcome:** no FM-"council-that-converged-to-single-voice" finding; the dyadic convening was substantive. (But note F2-01: both voices' "flattens the locked T-perm-1 gate axis" claim is the same mis-attribution — the council surfaced the right *mapping* on a partly-wrong *premise*.)

---

## Disposition

**APPROVE-WITH-FINDINGS.** No Class 3 findings → no phase re-opening, no upstream-artifact revision owed. The design leg is X-AL-3-clean, exceptionally well-grounded (every load-bearing cite resolved byte-exact), and correctly routes the actual extension to the B2-spec Class 1 fork. The X-AL-3 classification (§7), the fail-class count discipline (§5), the B2-first sequencing (D4), and the FULL-SPEC forward-item registration (D5) are all sound.

The two Class 2 findings (F2-01, F2-02) share one root: **the design over-claims the causal reach of the trust-projection fix.** The projection output (`host.trust_tier`) is telemetry-only at HEAD; the gate `mcp_trust_tier` axis is fed by a *separate* hardcoded constant (`hitl_gate_composer.py:462`) that §5 never names. This does not block the design leg — but the B2-spec leg MUST (a) correct the §3.3/§6/D3 rationale to scope the projection fix honestly (telemetry-fidelity + declared-intent propagation, NOT gate-axis un-flattening on its own), and (b) add the `hitl_gate_composer` gate-composition wiring to the spec-amendment surface as the site that actually un-flattens the locked `per_mcp_server_trust_tier` axis, or register it as an explicit forward item. The three Class 1 findings are inline doc-hygiene for the spec/plan leg.

Recommended next step: clear B2-DESIGN; carry F2-01/F2-02 into the B2-spec leg's amendment surface (not a fork blocker — it sharpens what the fork amends).

---

## Confidence + what I verified vs took on trust

**Confidence: [HIGH]** on F2-01/F2-02 (the trust_tier consumer trace is conclusive — I read every read/write of `.trust_tier` across `harness-runtime/src` + `harness-cp/src`); **[HIGH]** on the rejected-findings cite verifications (all byte-checked at HEAD `c0fc9f3`); **[MODERATE]** on F1-03's "two-factory" framing severity (it is genuinely minor and may be intentional compression).

**Verified empirically (read at HEAD this session):** every code cite in the rejected-findings §1 list; the §14.9.1/.3/.5/.6/.9 spec bodies by §-anchor; the fail-class count chain (§14.9.5 "8 new" + §14.9.9 "9th"); the AS↔CP enum identity (both enum bodies + the C-AS-10 §10.3 spec table + the CP docstring); `ADR-D2.md:69` axis string; `harness-as/CLAUDE.md §1.4` trust-home; the 10-file `mcp_client_host` consumer count; the `hitl_gate_composer.py:462` hardcoded gate-axis constant; the `test_cxa_pattern_p1.py` existence; the CXA-doc absence of an MCP seam.

**Took on trust (NOT independently re-verified):**
- The B1-DESIGN / B3-DESIGN / R-PM-1 precedent PRs (#527/#549/#505) cited in §0 — I did not open them; I trust the "mode-agnostic design leg merges on its own" precedent claim.
- The #550 grounding-sweep dossier's *drifted* line numbers — the design disclaims them and re-grounds by §-anchor; I verified the re-grounded anchors, not the dossier's old numbers.
- Whether `RT-FAIL-MCP-TOOL-NAME-COLLISION` is genuinely the right fail-class NAME/shape vs an existing taxonomy entry — I verified the *count* (10th) and that no same-named class exists in §14.9.5/.9, but did not exhaustively grep the full runtime fail-class taxonomy for a semantically-overlapping collision class.
- The council voices' SKILL.md-internal §-cites (s14 §4.1, §7.10, etc.) — I verified their *code/spec* cites (floor, evaluator, enums) but not the internal voice-framework section numbers.
- E2E behavior of the eventual reshape — this is a design doc; no runtime exercise was possible or expected at this leg.

*Filed by harness-adversarial-reviewer. Read-only review; no artifact edited. The single substantive finding (F2-01) was surfaced by tracing the projection-output consumer chain — the grep-vs-e2e / built-but-vacuous discipline applied to the artifact under review, not just enforced by it.*
