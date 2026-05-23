# Class 1 Fork — Meta-Architecture ↔ CP-spec systemic alignment drift at H_T-CP-15..21

**Filed:** 2026-05-23 at γ-audit follow-on arc post-Meta-Arch v1.1 landing (`40d9f78`) + batch-10 retirement ledger (`eb4475d`).
**Status:** PARTIALLY-APPLIED 2026-05-23 — priority-3 rows H_T-CP-18/20/21 APPLIED at Meta-Arch v1.2; 4 §10.4 rows (H_T-CP-15/16/17/19) + §10.5 missing primitives DEFERRED per operator-ratified PER-ROW-RATIFY routing. See §11 ratification footer.
**Scope:** Phase 7d substitution retirement discipline; halt-execution Class 1 per `Project_Workflow_v1_8.md` §2.7.6 + workspace `CLAUDE.md` §4.3.
**Surfaced by:** `spec-writer` skill FM-1 no-resolution discipline triggered at empirical investigation of §5.8 γ-audit findings replacement-cite candidates during operator-authorized "α+γ, proceed" follow-on arc. Empirical cross-check of Meta-Arch §2.3 + §5.4 H_T-CP-NN row labels against current CP spec v1.2 base contracts revealed systemic semantic divergence across 4 of 7 rows H_T-CP-15..21.
**Disposition:** All per-row α-style replacement-cite fixes for §5.8 γ-audit findings (rows H_T-CP-16 / H_T-CP-17 / H_T-CP-19 / H_T-CP-20 / H_T-CP-21) HALTED. NO further Meta-Arch §5.4 amendment beyond the v1.1 H_T-CP-18 α fix already landed. Routing target: `systems-architect` skill for cross-artifact alignment recommendation, NOT `spec-writer` skill for per-row mechanical fix (which would silently absorb a deeper architectural divergence per FM-1).

---

## 1. The systemic gap

`Phase_7_Meta_Architecture_v1.md` §2.3 H_T components catalog (CP-axis sub-table at lines 145..170) carries per-row anchor cites of the form `C-CP-NN §NN` (e.g., "C-CP-18 §18"). Empirical cross-check at `Spec_Control_Plane_v1_2.md` (base spec; current canonical content per v1.3..v1.11 delta cascade) reveals systemic semantic divergence between the Meta-Arch row LABELS and the current C-CP-NN spec contracts:

| Row | Meta-Arch §2.3 label | Anchor cite | Current C-CP-NN at CP spec v1.2 base | Alignment |
|---|---|---|---|---|
| H_T-CP-15 | "Skills enabling discipline (CP-side composition)" | C-CP-15 §15 | "Cross-sibling audit-ledger discipline" (v1.2 line 1287) | **MISALIGNED** — Skills vs cross-sibling audit |
| H_T-CP-16 | "Memory primitives + `memory.*` consumption" | C-CP-16 §16 | "Four-response palette + audit ledger entry shape" (v1.2 line 1398) | **MISALIGNED** — memory vs HITL palette |
| H_T-CP-17 | "Files primitives + `files.*` consumption" | C-CP-17 §17 | "Three-placement HITL topology primitive + interface signature" (v1.2 line 1460) | **MISALIGNED** — files vs HITL placement |
| H_T-CP-18 | "MCP integration + per-server trust + `mcp.*` consumption" | C-CP-18 §18 | "Synchrony-class × HITL-primitive-shape matrix per persona-tier × D1-engine-class" (v1.2 line 1536) | **MISALIGNED** — MCP vs HITL matrix |
| H_T-CP-19 | "D5 cross-deployment monotonicity" | C-CP-19 §19 | "T-perm-1 D5-layer multiplicative gate-level composition rule with cross-deployment monotonicity" (v1.2 line 1604) | **ALIGNED (label matches contract)** but §5.4 cite still wrong (cites U-CP-46 = audit attrs; correct unit = U-CP-27 = D5 monotonic-descent composition) |
| H_T-CP-20 | "HITL primitive + 4-response palette + `hitl.*` / `audit.*`" | C-CP-20 §20 | "Per-persona-tier audit-ledger cryptographic shape + `audit.*` attribute namespace" (v1.2 line 1706) | **PARTIAL** — `audit.*` aligned with current C-CP-20; HITL palette + `hitl.*` is at current C-CP-16 (4-response palette) NOT current C-CP-20 |
| H_T-CP-21 | "ValidatorFailClass 5-class + operator-burden eval primitive" | C-CP-21 §21 | "Pre-HITL escalation order + `validator.fail.*` taxonomy" (v1.2 line 1829) | **PARTIAL** — `validator.fail.*` taxonomy aligned; "operator-burden eval primitive" not present at current C-CP-21 |

**Pattern.** The Meta-Arch §2.3 + §5.4 H_T-CP-NN labels appear authored against an EARLIER CP-spec contract numbering. The CP spec was renumbered between Meta-Arch authoring (Phase 6.5 Session 4, 2026-05-15) and current state (CP spec v1.2 base + v1.11 cascade). The renumbering was never absorbed at Meta-Architecture.

Mechanistically: Meta-Arch §2.3 row H_T-CP-18 says "MCP integration + per-server trust + `mcp.*` consumption" — that's a coherent H_T primitive intent matching the original ADR-level H_T design. The cite "C-CP-18 §18" was correct at Meta-Arch authoring time. Subsequent CP spec revisions reassigned §18 to a different contract (HITL matrix) without back-propagating the renaming to Meta-Arch §2.3.

---

## 2. Evidence — H_T-CP-18 partial-fix pattern

The v1.1 α fix at row H_T-CP-18 (`40d9f78`) "worked" because:

- The row LABEL ("MCP integration + per-server trust + `mcp.*` consumption") was the ORIGINAL H_T primitive intent — coherent and current.
- The implementing units at L9-septies (U-RT-73 + U-RT-74 + U-RT-75 + U-RT-68 + U-CP-00b) actually materialize that primitive intent at the current implementation layer.
- The fix preserved the row LABEL and re-pointed the cited-unit column to the actual implementing units per the new §5.1.1 material-location-resident convention.
- The stale "C-CP-18 §18" anchor at §2.3 (which now points at HITL matrix, NOT MCP integration) was NOT touched — surfaced as adjacent defect (ii) at v1.1 §0.1 but preserved verbatim per FM-2.

**This pattern only works when the H_T primitive intent (row label) is still a current design commitment AND its implementing units are identifiable at the current plan corpus.** For H_T-CP-16 (memory) and H_T-CP-17 (files), neither precondition is clearly satisfied:

- "Memory primitives + `memory.*` consumption" is a coherent H_T design intent — but `grep memory primitive|memory\.\*` against current CP spec v1.2 base returns 0 hits. Memory primitives may not exist as a current C-CP-* contract at all (potentially dropped during spec revision).
- "Files primitives + `files.*` consumption" — same pattern. `grep files primitive|files\.\*` against current spec returns 0 hits.
- The current Meta-Arch §6.3 cross-axis retirement dependencies enumerate only `anthropic.*` (H_T-CP-1 → H_T-AS-8) and `harness.breaker.*` (F-CP-01 Stage 3b inversion). Neither `memory.*` nor `files.*` appear as retirement-dependency surfaces.

**Possibility:** H_T-CP-16 and H_T-CP-17 may be substitutions for primitives that were entirely deprecated at the CP spec renumbering and never explicitly removed from Meta-Arch §2.3 / §5.4 / §4 capability overlap map.

---

## 3. What this fork is NOT

This fork is NOT a request to re-litigate the H_T-CP-18 α fix at v1.1 (`40d9f78`) or the H_T-CP-18 RETIRE-READY transition at batch-10 (`eb4475d`). The v1.1 fix is APPLIED; batch-10 is filed; H_T-CP-18 is RETIRE-READY at the cumulative ledger. Those landings stand.

This fork is also NOT a request for spec-writer revision to amend §5.4 rows for the 5 §5.8 findings + §2.3 parallel cites against best-guess replacement cites. Per FM-1 spec-writer no-resolution discipline, the spec-writer CANNOT pick replacement cites for findings whose root cause is systemic contract-renumbering drift — that would be silent absorption of a deeper architectural divergence per workspace `CLAUDE.md` §4.3.

This fork IS a request for `systems-architect` skill invocation to produce a cross-artifact alignment recommendation: which H_T-CP-NN primitive labels at Meta-Arch §2.3 + §5.4 are still current design commitments; which need to be re-anchored to current C-CP-NN spec contract numbering; which (if any) should be retired from Meta-Arch as dropped primitives.

---

## 4. Three readings

### 4.1 Reading α — full cross-artifact alignment audit + Meta-Arch §2 + §4 + §5 + §6 reconciliation pass

**Action:** Invoke `systems-architect` skill against the full Meta-Arch ↔ CP spec alignment surface. Produce a per-row recommendation for H_T-CP-15..21 (and any other H_T-CP-NN rows surfaced during the audit) covering:

- Is the row's primitive label still a current H_T design commitment?
- If yes, what is the correct current C-CP-NN anchor cite + correct CP plan unit IDs?
- If no, should the row be struck from Meta-Arch §2.3 + §5.4 (and from §4 capability overlap, §6 self-hosting gradient, §7 anti-leakage where referenced)?
- Are there H_T primitives in current CP spec v1.11 that should have Meta-Arch rows but don't (e.g., new contracts added at v1.10 §17.4 `hitl_gate` materialization)?

**Cost:** High — systems-architect cross-artifact deliberation arc; potentially Meta-Arch v1.2 (or v2) revision covering §2 + §4 + §5 + §6 sections. May surface additional follow-on Class 1 forks per row (each requiring spec-writer revision per Meta-Arch §X reading).

**Downstream:** Cleared Meta-Arch ↔ CP-spec alignment enables empirically-verifiable retirement-criterion fidelity across all 21 CP-axis substitutions. Eliminates the contract-renumbering-drift recurrence pattern at the root.

**Disposition: Recommended.** Aligns with operator-ratified γ-audit-appendix discipline (root-cause-fix over surfacing-by-surfacing fix).

### 4.2 Reading β — per-row scoped fixes against best-guess current cites

**Action:** Per surfacing (5 §5.8 findings + §2.3 parallel cites), apply best-guess α-style fixes:

- H_T-CP-18 §2.3: re-anchor to current C-CP-NN that covers MCP integration (per audit — none currently; may need to surface as Class 1 sub-fork)
- H_T-CP-19 §5.4: re-cite to U-CP-27 (D5 monotonic-descent composition) instead of U-CP-46
- H_T-CP-20 §5.4: augment cite to U-CP-37 (4-response palette) + U-CP-46 (audit attrs)
- H_T-CP-21 §5.4: strike U-CP-52 mis-cite
- H_T-CP-16, H_T-CP-17 §5.4: defer — H_T primitive intent may be deprecated; no clear replacement cite

**Cost:** Lower per-row arc but FM-1 violation risk for rows where the H_T primitive intent itself is in question (CP-16 memory, CP-17 files). Silent absorption of deprecated primitives if H_T design has dropped them since Meta-Arch authoring.

**Disposition: NOT RECOMMENDED.** Mixes surface-level cite repair with deeper architectural questions about deprecated primitives.

### 4.3 Reading γ — minimal fix scope + Meta-Arch deprecation marker

**Action:** Apply only the 2 clear-cut surface fixes (H_T-CP-20 augmentation + H_T-CP-21 strike) per §5.8 explicit identification. Add a `[DEPRECATED-PRIMITIVE-CANDIDATE]` marker to H_T-CP-16 + H_T-CP-17 + H_T-CP-19 rows at Meta-Arch §2.3 + §5.4 with footnote pointing to this fork doc. Halt all retirement filings for marked rows pending operator decision on primitive deprecation.

**Cost:** Minimal forward motion + explicit deprecation-candidate surfacing for the deeper questions.

**Disposition: Acceptable alternative if Reading α is too heavy for current arc cadence.** Reading γ provides bounded surface clean-up while preserving the systems-architect routing for the systemic alignment question.

---

## 5. Recommendation

**Reading α (full cross-artifact alignment audit).** Route to `systems-architect` skill invocation against the Meta-Arch ↔ CP spec alignment surface. Per-row recommendations + dropped-primitive identification + new-contract surfacing emerge from a single systems-architect deliberation arc rather than 5 separate per-row arcs.

Pattern density argues for root-cause fix: 3 phantom-cite forks in 2 sessions (sandbox-decision-policy, U-RT-68, H_T-CP-18) + this systemic-drift fork = 4 forks rooted in author-time-vs-implementation-time drift between design substrate artifacts. The α-style per-row fix pattern works for ISOLATED cite errors but cannot remediate systemic drift.

---

## 6. Cross-axis cascade analysis

Routing decision impacts:

- **Reading α:** Meta-Arch revision (v1.2 or v2) likely; may cascade to per-axis CLAUDE.md retirement tables if H_T-CP-* primitive intents are restructured. ZERO immediate code/spec/plan cascade. Subsequent revisions may follow (e.g., CP spec footer notes documenting the renumbering; per-axis CLAUDE.md reconciliation).
- **Reading β:** ZERO cross-axis cascade per-row, but ACCUMULATES silent absorption risk across the column.
- **Reading γ:** ZERO cross-axis cascade. Meta-Arch single-artifact edit with deprecation markers.

L9-septies + 10-CP-D cluster closes stand. H_T-CP-18 v1.1 α fix + batch-10 RETIRE-READY stand. 2751/2751 tests stand at HEAD `eb4475d`.

---

## 7. Routing

Per `Project_Workflow_v1_8.md` §2.7.6 + workspace CLAUDE.md §4.3:

| Step | Action |
|---|---|
| 1 | Operator selects α / β / γ |
| 2 | If α: invoke `systems-architect` skill against Meta-Arch ↔ CP spec alignment surface for H_T-CP-15..21 (and broader §2.3 / §5.4 audit if surfaced). Per-row recommendation outputs route to spec-writer for Meta-Arch revision. Multi-arc work. |
| 3 | If γ: invoke `spec-writer` skill for minimal surface fixes (H_T-CP-20 augmentation + H_T-CP-21 strike) + deprecation markers at H_T-CP-16/17/19 + §2.3 parallel cites. Single-arc work. |
| 4 | All §5.8 γ-audit retirement filings remain HALTED until per-row resolution. The H_T-CP-18 v1.1 α fix + batch-10 RETIRE-READY landing stand (out of scope for this fork). |
| 5 | At resolution close: re-audit Meta-Arch §6 self-hosting milestone gradient + §4 capability overlap map + §7 anti-leakage rules for contract-renumbering-drift surfacing (the §5.8 audit only covered §5.4 cited-unit column). |

---

## 8. Related memory

- `[[fork-h-t-cp-18-phantom-retirement-cite]]` — sibling fork APPLIED-AND-RETIRE-READY at this session (parent of this fork; surfaced the §5.8 audit appendix that this fork generalizes)
- `[[fork-sandbox-decision-policy-phantom-cite]]` — sibling phantom-cite fork APPLIED at L9-septies close
- `[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap]]` — parent fork in the U-RT-68-adjacent drift cluster
- `[[advisor-before-substantive-work-for-cross-axis-blockers]]` — feedback memory whose trigger condition 1 ("AC body cites a type/class/producer not grep-confirmed at HEAD") generalizes to meta-arch cited-unit columns AND to meta-arch row anchor cites (the new dimension this fork surfaces)
- `[[halt-route-split-AC-pattern]]` — sibling pattern for partial-materializability AC bundles; this fork is the *systemic-drift* analog applied to Meta-Architecture alignment audits

---

## 9. Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_meta_arch_cp_spec_renumbering_drift.md` |
| Authored at | 2026-05-23 γ-audit follow-on arc post-Meta-Arch v1.1 + batch-10 landings |
| Authoring authority | `spec-writer` skill FM-1 no-resolution discipline halt-condition + `phase-7-back-flow-routing` skill activation |
| Predecessor | `.harness/class_1_fork_h_t_cp_18_phantom_retirement_cite.md` (APPLIED-AND-RETIRE-READY at this session); §5.8 γ-audit findings appendix at Meta-Arch v1.1 (`40d9f78`); batch-10 retirement ledger (`eb4475d`) |
| Successor consumption | Operator α/β/γ selection → `systems-architect` skill (α path) for cross-artifact alignment recommendation OR `spec-writer` skill (γ path) for minimal surface fix + deprecation markers |
| HEAD at filing | `eb4475d` (batch-10 retirement ledger close); 2751/2751 tests green workspace-wide; clean tree pre-fork-doc |
| Status | OPEN — awaiting operator routing decision |

---

*End of Class 1 fork doc proper. Systems-architect recommendation appended at §10 below per skill §4A.3.*

---

## 10. Systems-architect recommendation (appended 2026-05-23, operator-ratified α path)

### 10.1 Precise tension restatement

The Meta-Arch §2.3 H_T components catalog CP-axis sub-table (lines 173..179) and §5.4 CP-axis substitution mapping table (lines 442..448) carry per-row anchor cites of the form `C-CP-NN §NN` plus carrier-unit / retirement-criterion unit cites for 7 rows H_T-CP-15..21. Empirical cross-check at HEAD `51502f6` against the canonical authority chain reveals systemic mis-anchoring at authoring time:

**Quoted Meta-Arch §2.3 H_T-CP-15..21 rows:**
```
| H_T-CP-15 | Skills enabling discipline (CP-side composition) | C-CP-15 §15 | U-CP-33 → U-CP-37 | AS consumer |
| H_T-CP-16 | Memory primitives + `memory.*` consumption | C-CP-16 §16 | U-CP-38 → U-CP-41 | AS consumer |
| H_T-CP-17 | Files primitives + `files.*` consumption | C-CP-17 §17 | U-CP-42, U-CP-43, U-CP-44 | AS + IS consumer |
| H_T-CP-18 | MCP integration + per-server trust + `mcp.*` consumption | C-CP-18 §18 | U-CP-45 | AS consumer |
| H_T-CP-19 | D5 cross-deployment monotonicity | C-CP-19 §19 | U-CP-46 | CP-internal |
| H_T-CP-20 | HITL primitive + 4-response palette + `hitl.*` / `audit.*` | C-CP-20 §20 | U-CP-46 | CP-internal |
| H_T-CP-21 | ValidatorFailClass 5-class + operator-burden eval primitive | C-CP-21 §21 | U-CP-47, U-CP-48, U-CP-51, U-CP-52 | CP-internal |
```

**Quoted CP spec v1.2 base contracts at §15..§21:**
```
§15 C-CP-15 — Cross-sibling audit-ledger discipline
§16 C-CP-16 — Four-response palette + audit ledger entry shape
§17 C-CP-17 — Three-placement HITL topology primitive + interface signature
§18 C-CP-18 — Synchrony-class × HITL-primitive-shape matrix per persona-tier × D1-engine-class
§19 C-CP-19 — T-perm-1 D5-layer multiplicative gate-level composition rule with cross-deployment monotonicity
§20 C-CP-20 — Per-persona-tier audit-ledger cryptographic shape + `audit.*` attribute namespace
§21 C-CP-21 — Pre-HITL escalation order + `validator.fail.*` taxonomy
```

**Quoted CP spec v1.10 NEW additions (relevant to recommendation):**
```
§17.4 (NEW) `hitl_gate` canonical signature materialization
§25 (NEW) C-CP-25 — ValidatorFramework
§26 (NEW) C-CP-26 — PauseResumeProtocol
§27 (NEW) C-CP-27 — PerServerTrustEvaluator + MCPClientNamespaceEmitter
```

### 10.2 Authority-chain placement per divergence

Per workspace `CLAUDE.md` §1.3: ADR (F1–F5 + D1–D6) → ADD v1.3 → PRD v1.1 → per-axis spec v1.x → per-axis plan v2.x + CXA v2.8 → Phase 7 implementation. Earlier artifacts canonical for later.

**Load-bearing authority finding.** ADD v1.3 §3 D6 derivative-decisions synthesis enumerates 16 specialization-layer namespace rows (line 116): `anthropic.* / mcp.* / skill.* / managed_agents.* / sandbox.* / hitl.* / topology.fanout.* / subagent.* / engine.* / audit.* / validator.fail.* / files.* / memory.* / harness.breaker.* / retry.* / provider_discriminator`. The 4 namespace primitives at issue (`mcp.* / skill.* / files.* / memory.*`) ARE current ADR-D3 + ADD-D6 commitments. The Meta-Arch row LABELS describing CP-axis consumption of these primitives are coherent with the authority chain at the LABEL level.

**Anchor-cite divergence pattern.** The Meta-Arch row labels (H_T-CP-15..18 = Skills/Memory/Files/MCP) describe CP-axis consumption-side primitives. The anchor cites (`C-CP-15 §15` through `C-CP-18 §18`) point at CP spec sections that contain UNRELATED HITL/audit contracts (cross-sibling audit / palette / HITL topology / synchrony matrix). The anchor cites were never empirically aligned with CP spec content at Meta-Arch authoring time (2026-05-15) — CP spec v1.2 dated 6 days prior carries the §15..§21 contracts under their HITL/audit semantics already.

**Cross-axis primitive home discovery.** AS spec v1 §14 (per C-AS-14) carries the `mcp.* / skill.* / files.* / memory.*` namespace OBSERVABILITY declarations at AS-axis (six-namespace export surface per AS spec line 1311). H_T-AS-6 (SkillFrontmatter) + H_T-AS-7 (Skills filesystem) + H_T-AS-8 (15-namespace observability) carry the AS-side primitive homes. The CP-axis "consumption" rows (H_T-CP-15..18 in Meta-Arch) describe CP-side composition patterns that consume AS-axis primitives but are NOT separately contract-anchored at current CP spec v1.2 base.

**New CP spec contracts at v1.10 unify some of these.** §27 (NEW C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter) is the canonical current contract for MCP-integration client-side surface. §25 (NEW C-CP-25 ValidatorFramework) augments the validator surface previously partial at C-CP-21. §26 (NEW C-CP-26 PauseResumeProtocol) augments the pause/resume surface previously partial at C-CP-22.

### 10.3 §2 discipline application

**Five-axis decomposition.** The 7 Meta-Arch rows decompose across axes:
- H_T-CP-15 Skills, H_T-CP-16 Memory, H_T-CP-17 Files, H_T-CP-18 MCP: **AS axis** (primitive declaration) + **CP axis** (sub-agent dispatch composition) + **OD axis** (`mcp.*` / `skill.*` / `files.*` / `memory.*` namespace consumption at observability)
- H_T-CP-19 D5 cross-deployment monotonicity: **CP axis** (primitive declaration at C-CP-19) + **AS axis** (sandbox-tier-floor composition)
- H_T-CP-20 HITL palette + emission: **CP axis** (C-CP-16 palette + C-CP-17 placement + C-CP-20 audit emission + C-CP-25 validator framework + §17.4 hitl_gate signature) + **OD axis** (`hitl.*` / `audit.*` namespace consumption)
- H_T-CP-21 ValidatorFailClass + operator-burden eval: **CP axis** (C-CP-21 + C-CP-25 NEW) + **OD axis** (operator-burden eval primitive — actually OD-axis-primary)

**Probabilistic-deterministic boundary.** All 7 rows describe deterministic-layer contracts (schemas, enums, protocols, span attribute namespaces). No probabilistic-layer commitments in scope.

**F/D/I classification.** All 7 are D-level (derivative) decisions per ADD §3 — they depend on F-level ADR commitments (F2 state-ledger, F3 lifecycle, F5 observability substrate) + D-level ADRs (D1 engine-class, D3 Anthropic-primitive adoption, D6 observability backend). Divergence severity: D-level mis-anchoring at Meta-Arch — fixable at Meta-Arch revision without disturbing F-level commitments.

### 10.4 Per-row recommendation table

For each row: (a) label-current? (b) recommended anchor cite (c) recommended §5.4 retirement-column cite (d) recommended §2.3 carrier-units cite (e) rationale (f) source-artifact references. Per FM-1, recommendations only; operator decides.

| Row | Label current? | Recommended anchor | Recommended §5.4 retirement-column cite | Recommended §2.3 carrier-units cite | Rationale | Source artifacts |
|---|---|---|---|---|---|---|
| **H_T-CP-15** Skills enabling discipline (CP-side composition) | **PARTIAL** — Skills primitive itself is AS-axis (H_T-AS-6 / H_T-AS-7); the "CP-side composition" qualifier refers to U-CP-28..30 SubAgentBrief schema which references skills loading via brief. No dedicated C-CP-NN contract for Skills-loading composition. | **STRIKE C-CP-15 §15 anchor** (current C-CP-15 is cross-sibling audit-ledger, unrelated). Replace with **cross-axis cite** `C-AS-05 §5 + C-AS-06 §6 + C-AS-07 §7 (Skills primitive declaration) + C-CP-13 §13 (HandoffContext + SubAgentBrief brief loading)`. | Replace `U-CP-33 → U-CP-37` (which actually implement C-CP-14/15 multi-agent spans + cross-sibling audit) with **cross-axis cite** `U-AS-20..U-AS-27 (Skills authoring + filesystem residence) + U-CP-28..U-CP-30 (HandoffContext + SubAgentBrief composing skills via brief)`. | Same as §5.4 (material-location-resident reading per Meta-Arch v1.1 §5.1.1) | Skills are AS-axis primitives per ADR-D3 v1.2 §1.8.1; H_T-AS-6 + H_T-AS-7 at Meta-Arch §5.3 already cover AS-side. CP-side composition is implicit in HandoffContext schema. Current U-CP-33..37 are unrelated to skills. | AS spec v1 §5..§8 + §14; ADR-D3 v1.2 §1.8.1; Meta-Arch §5.3 H_T-AS-6/7; v2.1 plan U-AS-20..27 + U-CP-28..30 |
| **H_T-CP-16** Memory primitives + `memory.*` consumption | **PARTIAL** — `memory.*` namespace IS current ADR-D6 commitment (ADD §3 16-namespace list); but the namespace home + consumer pattern is AS-axis observability (H_T-AS-8) + OD-axis ingestion. No dedicated CP-axis memory consumer contract. | **STRIKE C-CP-16 §16 anchor** (current C-CP-16 is 4-response palette, unrelated). Replace with **cross-axis cite** `C-AS-14 §14.7 (memory.* namespace 6-attribute span schema at AS) + ADR-D3 v1.2 §1.8.1 memory namespace block`. May warrant CP-axis EXISTENCE-OF-PRIMITIVE deprecation discussion. | Replace `U-CP-38 → U-CP-41` (which implement HITL placement + persona-tier matrix, unrelated to memory) with **cross-axis cite** to AS-axis units emitting `memory.*` (U-AS-28..U-AS-32 per H_T-AS-8 cite) OR **STRIKE THIS ROW** if CP-axis has no dedicated memory consumption surface. | Same as §5.4 | `memory.*` is AS-emitted + OD-consumed observability namespace. No current CP spec contract carries memory consumption surface. H_T-AS-8 already covers emission; OD-axis covers consumption. The CP-axis row appears to be a phantom architectural commitment. Operator decision: STRIKE OR retain as cross-axis-cite-only pointer. | AS spec v1 §14.7; ADR-D3 v1.2 §1.8.1; Meta-Arch §5.3 H_T-AS-8 |
| **H_T-CP-17** Files primitives + `files.*` consumption | **PARTIAL** — same pattern as H_T-CP-16. `files.*` is AS-emitted observability namespace + OD-axis ingestion. No dedicated CP-axis files consumer contract. | **STRIKE C-CP-17 §17 anchor** (current C-CP-17 is 3-placement HITL topology). Replace with **cross-axis cite** `C-AS-14 §14.6 (files.* namespace 8-attribute span schema at AS) + ADR-D3 v1.2 §1.8.1 files namespace block`. | Replace `U-CP-42, U-CP-43, U-CP-44` (which implement audit-ledger crypto + signing-key, unrelated to files) with **cross-axis cite** to AS-axis units emitting `files.*` (U-AS-28..U-AS-32 per H_T-AS-8) OR **STRIKE THIS ROW**. | Same as §5.4 | Same as H_T-CP-16 — phantom CP-axis architectural commitment. Operator decision: STRIKE OR retain as cross-axis-cite-only pointer. | AS spec v1 §14.6; ADR-D3 v1.2 §1.8.1; Meta-Arch §5.3 H_T-AS-8 |
| **H_T-CP-18** MCP integration + per-server trust + `mcp.*` consumption | **YES — current commitment** at CP spec v1.10 NEW §27 (PerServerTrustEvaluator + MCPClientNamespaceEmitter). Materialized at L9-septies. Already RETIRE-READY at batch-10. | **REPLACE** `C-CP-18 §18` (current C-CP-18 is Synchrony × HITL matrix) **with** `C-CP-27 §27` (NEW C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter — the actual contract). | **PRESERVED VERBATIM at v1.1 α fix:** `U-CP-00b + U-RT-73 + U-RT-74 + U-RT-75 + U-RT-68`. No change at this arc. | **§2.3 carrier-units cell:** REPLACE `U-CP-45` with subset of §5.4 cites under carrier semantics. Recommendation: `U-CP-00b` (carrier-only — the MCPTrustTier + PerServerTrustEvaluator carriers; runtime wiring units U-RT-73/74/75 + U-RT-68 are dispatch-binding not carrier per §2.3 column semantic). | The v1.10 §27 contract is the canonical anchor. §5.4 cite stands per v1.1 α fix. §2.3 anchor + carrier need updating. | CP spec v1.10 §27; AS spec §14.2 (mcp.*); Meta-Arch v1.1 §5.4 row H_T-CP-18; batch-10 ledger |
| **H_T-CP-19** D5 cross-deployment monotonicity | **YES — current commitment** at CP spec C-CP-19 §19 (T-perm-1 D5-layer composition + cross-deployment monotonicity). | **PRESERVE** `C-CP-19 §19` anchor — actually aligned. | **REPLACE** `U-CP-46` (which implements 7 audit.* attrs, unrelated to D5 monotonicity) **with** `U-CP-26 + U-CP-27` (U-CP-26 declares default-downgrade Tier-3 → Tier-1; U-CP-27 implements gate-level monotonic descent + cross-deployment monotonicity composition per C-CP-12 §12). | **§2.3 carrier-units cell:** REPLACE `U-CP-46` with `U-CP-26 + U-CP-27`. | U-CP-27 v2.1 line 1388 "Implement sub-agent gate-level monotonic descent + override audit + cross-deployment monotonicity composition" implements C-CP-12 §12.2..§12.5. Note: implements C-CP-12 not C-CP-19 in v2.1 — the C-CP-19 cross-deployment monotonicity surface MAY be sub-component of C-CP-12 §12 monotonic descent OR may need second-pass clarification. **Tiebreaker check needed:** confirm C-CP-19 §19's 4-axis multiplicative formula is materialized by U-CP-43 (4-axis gate-level rule) vs U-CP-27 (monotonic descent + cross-deployment composition); both may be cited. | CP spec v1.2 §19 + §12; v2.1 U-CP-26 + U-CP-27 + U-CP-43 |
| **H_T-CP-20** HITL primitive + 4-response palette + `hitl.*` / `audit.*` | **YES — current commitment**, split across multiple contracts. Already RETIRED at batch-9 (operational e2e via U-RT-62). | **AUGMENT** `C-CP-20 §20` (audit.* attribute namespace) **with** `C-CP-16 §16` (4-response palette declaration) **+** `C-CP-17 §17 + §17.4` (3-placement HITL topology + NEW hitl_gate canonical signature at v1.10). The full HITL primitive surface is multi-contract. | **AUGMENT** `U-CP-46` (audit.* attrs only) with `U-CP-37` (4-response palette declaration — v2.1 line 1924 implements C-CP-16 §16) **+** `U-CP-38 + U-CP-39` (HITL placement + tool-call rewriting per C-CP-17). H_T-CP-20 RETIRED at batch-9 used implicit U-CP-37 + U-CP-46 surface — this augmentation makes the cite explicit. | Same as §5.4 | The HITL primitive is multi-contract by design. Single-cite was insufficient. U-CP-37 + U-CP-46 are both cited at batch-9 §1.1 already; augmentation makes the §5.4 cite consistent with the retirement-event filing. | CP spec v1.2 §16 + §17 + §20; v1.10 §17.4; v2.1 U-CP-37 + U-CP-38 + U-CP-39 + U-CP-46; batch-9 ledger §1.1 |
| **H_T-CP-21** ValidatorFailClass 5-class + operator-burden eval primitive | **PARTIAL** — `ValidatorFailClass` + `validator.fail.*` taxonomy at C-CP-21 ✓. Augmented at v1.10 §25 NEW C-CP-25 ValidatorFramework. "Operator-burden eval primitive" actually OD-axis-primary (OD spec C-OD-NN). | **AUGMENT** `C-CP-21 §21` **with** `C-CP-25 §25` (NEW ValidatorFramework at v1.10). Surface "operator-burden eval primitive" qualifier MAY warrant cross-axis cite to OD spec C-OD-NN if operator-burden eval is canonically OD-axis. | **STRIKE** `U-CP-52` from cite (U-CP-52 implements HITL timeout-degradation + webhook delivery per §5.8 audit; mis-cited). **PRESERVE** `U-CP-47 + U-CP-48 + U-CP-51`. **CONSIDER** adding `U-CP-66` or successor unit for C-CP-25 ValidatorFramework materialization at v1.10 (need to verify in plan v2.16 cascade). | Same as §5.4 | C-CP-25 NEW at v1.10 augments validator surface; H_T-CP-21 row predates v1.10 addition. Operator-burden eval primitive is OD-axis-primary per OD spec C-OD-NN (verify exact §). U-CP-52 strike per §5.8 finding. | CP spec v1.2 §21; v1.10 §25; v2.1 U-CP-47/48/51/52; OD spec for operator-burden eval primitive |

### 10.5 Missing-primitive surfacing

Current CP spec v1.10 adds 3 NEW contracts not represented at Meta-Arch §2.3 + §5.4:

| New contract | Section | Current Meta-Arch coverage | Recommendation |
|---|---|---|---|
| **§17.4 NEW `hitl_gate` canonical signature materialization** | v1.10 §17.4 | **NOT REPRESENTED** at Meta-Arch §2.3 + §5.4. Materialized at U-CP-71 (per plan v2.16/v2.17). | ADD NEW Meta-Arch row OR include as augmentation to H_T-CP-20 (per §10.4 above). |
| **§25 NEW C-CP-25 ValidatorFramework** | v1.10 §25 | **NOT REPRESENTED** as separate Meta-Arch row. Validator surface is at H_T-CP-21 but doesn't cite C-CP-25. | Include as augmentation to H_T-CP-21 (per §10.4 above) OR ADD NEW Meta-Arch row H_T-CP-25 if Validator framework warrants separate substitution row. |
| **§26 NEW C-CP-26 PauseResumeProtocol** | v1.10 §26 | Meta-Arch H_T-CP-22 covers "Pause/resume protocol + state_summary snapshot + material-diff" — anchor `C-CP-22 §22` (current C-CP-22 is Context revalidation, NOT the full PauseResume protocol). | **AUGMENT H_T-CP-22 anchor** with `C-CP-22 §22 + C-CP-26 §26` (NEW). Tension-resolution recommendation similar to H_T-CP-20. |
| **§27 NEW C-CP-27 PerServerTrustEvaluator + MCPClientNamespaceEmitter** | v1.10 §27 | **Represented at H_T-CP-18** but anchor cite is stale (C-CP-18 §18 vs correct C-CP-27 §27). | Per §10.4 H_T-CP-18 recommendation. |
| **§27 NEW C-CP-27 MaterialDiffPolicy** | v1.11 §27 (per workspace CLAUDE.md §2.3 v1.11 footnote) | Not represented. | ADD NEW Meta-Arch row OR augment H_T-CP-22 (pause/resume material-diff). |

### 10.6 Cascade reconciliation owed

If recommendations land, downstream absorption owed:

(a) **Meta-Arch §2.3 H_T components catalog** — 7 row updates (H_T-CP-15..21) + potentially 1-2 new rows (hitl_gate / ValidatorFramework / MaterialDiffPolicy). Multi-cell amendment.

(b) **Meta-Arch §4 capability overlap map** (§4.4.3 CP-axis classification at lines 327..346) — currently states e.g., "H_T-CP-15 ✓ Automatic Skills enabling per frontmatter" matching the OLD label. Per row recommendation in §10.4, the rationale column needs update if anchor + cite shift. 7 row updates.

(c) **Meta-Arch §5.4 CP-axis substitution mapping** — 7 row updates per §10.4. Some rows may be STRUCK entirely (H_T-CP-16 / H_T-CP-17 if operator decides those are not separable CP-axis substitutions). Substitution count change at §5.7 if rows struck (49 total may decrease).

(d) **Meta-Arch §5.7 substitution-type breakdown** — count update if §5.4 rows are added/struck. Total cell (currently 49) updates accordingly.

(e) **Meta-Arch §5.8 γ-audit findings appendix** (v1.1) — preserved verbatim; per-row finding dispositions update from "operator-decision-owed" to "resolved per v1.2 systems-architect recommendation" as each lands.

(f) **Meta-Arch §6 self-hosting milestone gradient** (per `Phase_7_Meta_Architecture_v1.md` §6.3.1 + §6.3.2) — currently references H_T-CP-1 → H_T-AS-8 (anthropic.*) + F-CP-01 Stage 3b. No direct dependency on H_T-CP-15..21. No update owed if those rows shift unless new cross-axis retirement dependencies surface from the recommendation.

(g) **Meta-Arch §7 anti-leakage rules** (18 axis + 3 cross-cutting) — per workspace CLAUDE.md §4.1, CP-axis substitution count cited as 21 entries. If H_T-CP-15..17 are STRUCK (3 rows) the CP-axis count drops to 18 entries. Per-axis rule referencing this count needs amendment.

(h) **Workspace `CLAUDE.md` §2.1** — currently cites `Phase_7_Meta_Architecture_v1.md` without version stamp. If Meta-Arch v1.1 → v1.2 absorption lands, no §2.1 update required (no version stamp + no entry-count claim).

(i) **Per-axis `CLAUDE.md` retirement tables** (`harness-cp/CLAUDE.md` §4.1 per workspace CLAUDE.md §2.5) — per-axis CP retirement table may reference H_T-CP-15..21 rows; needs reconciliation pass.

(j) **Retirement ledger batches 1..10** — preserved verbatim per forward-only ledger discipline at workspace CLAUDE.md §4.3. Past batches stand. Future batches (batch-11+) cite the updated Meta-Arch v1.2 row labels + anchor cites.

(k) **`phase-7d-retirement-ledger-v2.md`** (if present at workspace root) — per-primitive ledger may need update for STRUCK rows (move to "deprecated H_T-CP-* row" section).

### 10.7 Tiebreaker check

Two load-bearing facts that determine recommendation determinacy:

**(1) For H_T-CP-19:** Does `Implementation_Plan_Control_Plane_v2_*.md` cumulative cascade cite U-CP-27 as implementing C-CP-19 §19 cross-deployment monotonicity, OR is C-CP-19 fully implemented at U-CP-43 (4-axis multiplicative gate-level rule, v2.1 line 2289)? Tiebreaker: cite both per material-location-resident reading IF both contribute distinct sub-surfaces of C-CP-19 §19's 4-axis composition formula + cross-deployment monotonicity invariant.

**(2) For H_T-CP-16 / H_T-CP-17 (Memory / Files):** Does any current CP-axis plan unit implement a memory or files PRIMITIVE (not just observability emission)? If yes, the row is KEEP-WITH-RE-HOMED-CITES; if no, the row is STRIKE-AS-PHANTOM-CP-AXIS-COMMITMENT. Empirical check: `grep -rE 'memory primitive|files primitive' design-substrate/Implementation_Plan_Control_Plane_v2_*.md`. If zero substantive hits, recommendation defaults to STRIKE.

Both tiebreaker checks are bounded empirical verifications routable to spec-writer at the v1.2 revision arc.

### 10.8 Fork class

**Class 1 (halt-execution).** Per workspace CLAUDE.md §4.3 + `Project_Workflow_v1_8.md` §2.7.6. Routing target: design-phase back-flow → Meta-Architecture revision (v1.1 → v1.2). Halt scope: all §5.8 γ-audit per-row retirement filings at HEAD `eb4475d` (NOT the H_T-CP-18 v1.1 α fix + batch-10 RETIRE-READY which stand). Resolution unblocks future retirement filings for H_T-CP-15/16/17/19/20/21 + per row cleanup.

### 10.9 Recommended next steps

| Step | Action | Skill |
|---|---|---|
| 1 | **Operator ratification** of per-row recommendations at §10.4 + missing-primitive surfacing at §10.5. Per-row dispositions: KEEP-AND-RE-HOME / KEEP-AND-AUGMENT / STRIKE. | Operator |
| 2 | **Tiebreaker resolution** for H_T-CP-19 (U-CP-27 vs U-CP-43 vs both) + H_T-CP-16/17 (STRIKE vs re-home). | Operator + empirical grep |
| 3 | **Meta-Arch v1.1 → v1.2 revision** absorbing ratified recommendations + missing-primitive additions. Multi-amendment arc: §0.1 NEW change-note (v1.1 → v1.2) + §2.3 row updates + §4.4.3 rationale updates + §5.4 row updates + §5.7 count update + possibly §6.3 cross-axis dependency additions + §7 count amendment. | `spec-writer` skill |
| 4 | **§5.8 audit appendix update** marking per-row findings RESOLVED at v1.2. | Part of step 3. |
| 5 | **Per-row retirement filing re-invocation** for H_T-CP-15/16/17/19/20/21 against v1.2 re-pointed cites. Each yields RETIRED / RETIRE-READY / STILL-BOUNDED per criterion-A ∧ criterion-B evaluation. | `phase-7-substitution-retirement` skill, per-row arcs |
| 6 | **Re-audit §5.2 (IS) / §5.3 (AS) / §5.5 (OD) / §5.6 (CXA)** for analogous mis-anchoring pattern — recurrence-likelihood high per §5.8 §0.1 recurrence-pattern observation. | Operator-discretion follow-on; routed at next adversarial-review cadence per axis |

### 10.10 Operator-decides marker

**This is a SystemsArchitect deliverable, NOT a decided fix.** Per skill §4A.4 + spec-writer FM-1: the operator holds decision authority. The recommendation traces every fact to canonical authority chain sources for verifiability. Per-row dispositions (KEEP / AUGMENT / STRIKE) require operator ratification before any Meta-Arch v1.2 revision arc opens. Spec-writer cannot apply without that ratification.

If operator chooses BLANKET-RATIFY: all recommendations at §10.4 + §10.5 land at the single v1.2 revision arc. If operator chooses PER-ROW-RATIFY: each row routes separately through ratification → spec-writer arc cadence (slower but lower-risk per row). If operator chooses DEFER-DEEPER-AUDIT: a parallel-axis audit pass (§5.2 IS / §5.3 AS / §5.5 OD / §5.6 CXA) precedes the v1.2 revision to surface analogous mis-anchoring patterns.

Recommendation: **PER-ROW-RATIFY with §10.4 H_T-CP-18 + H_T-CP-20 + H_T-CP-21 prioritized first** (highest-confidence recommendations + already-touched-at-recent-arcs). H_T-CP-15/16/17 + H_T-CP-19 follow at subsequent arcs after tiebreaker resolution. Missing-primitive additions (§10.5) follow at last arc after primary 7 rows resolved.

---

*End of systems-architect recommendation §10. Per skill §4A.3 + workspace CLAUDE.md §4.3: this recommendation is APPENDED to the Class 1 fork doc; the fork stands OPEN until operator ratifies per-row dispositions and spec-writer absorbs at Meta-Arch v1.2.*

---

## 11. Partial ratification 2026-05-23 — priority-3 rows APPLIED at Meta-Arch v1.2

**Status:** OPEN → **PARTIALLY-APPLIED**.

**Applied dispositions (3 of 7 §10.4 rows):**

- ✓ **H_T-CP-18 §2.3 row** — anchor re-anchored from stale `C-CP-18 §18` → `C-CP-27 §27`; carrier units re-pointed from stale `U-CP-45` → `U-CP-00b`
- ✓ **H_T-CP-20 §2.3 + §5.4 rows** — anchor augmented to `C-CP-16 §16 + C-CP-17 §17 + §17.4 + C-CP-20 §20`; carrier/retirement cites augmented to `U-CP-37 + U-CP-38 + U-CP-39 + U-CP-46`
- ✓ **H_T-CP-21 §2.3 + §5.4 rows** — anchor augmented to `C-CP-21 §21 + C-CP-25 §25`; `U-CP-52` STRUCK from carrier/retirement cites

**Absorbing arc:** Meta-Arch v1.1 → v1.2 at this session. Spec-writer skill applied 6 amendment sites (3 §2.3 + 2 §5.4 + 1 §5.8 disposition update) per operator-ratified PER-ROW-RATIFY priority-3 dispositions (AskUserQuestion 2026-05-23).

**Deferred dispositions (4 of 7 §10.4 rows + missing-primitive surfacing at §10.5):**

- ⏸ **H_T-CP-15** (Skills enabling discipline) — STRIKE C-CP-15 §15 anchor; cross-axis re-cite to AS-axis. Awaiting follow-on arc.
- ⏸ **H_T-CP-16** (Memory primitives + memory.*) — STRIKE OR cross-axis cite only. Tiebreaker §10.7 (2) required: empirical grep for CP-axis memory PRIMITIVE.
- ⏸ **H_T-CP-17** (Files primitives + files.*) — same as H_T-CP-16. Tiebreaker §10.7 (2) required.
- ⏸ **H_T-CP-19** (D5 cross-deployment monotonicity) — REPLACE U-CP-46 cite with U-CP-26 + U-CP-27. Tiebreaker §10.7 (1) required: U-CP-27 vs U-CP-43 cite shape.
- ⏸ **Missing primitives §10.5** — 4 NEW v1.10/v1.11 contracts (§17.4 hitl_gate / §25 C-CP-25 / §26 C-CP-26 / §27 MaterialDiffPolicy) owed Meta-Arch §2.3 + §5.4 rows. Awaiting follow-on arc.

**Routing for deferred dispositions:**

1. Tiebreaker resolution arc — operator-discretion timing; empirical grep for §10.7 questions.
2. Per-row spec-writer arcs for H_T-CP-15/16/17/19 (4 rows) following tiebreaker resolution.
3. Missing-primitive addition arc(s) — possibly bundled with §10.5 systems-architect re-invocation for missing-primitive row authoring (these are ADD-style additions, not pure cite fixes).
4. Cross-row coherence-pass audit at §4.4.3 CP-axis classification (per v1.2 §0.2 adjacent defect (i)) — refresh "Brief rationale" descriptors against current retirement-status transitions.

**Fork status post-this-arc:** Class 1 PARTIALLY-APPLIED. The fork remains OPEN for the 4 deferred §10.4 rows + missing-primitive §10.5 additions. Subsequent ratification arcs will append further §N sections documenting each disposition application.

**Meta-Arch v1.2 commits at this session:**
- Spec-writer absorption commit: (this session, immediately following this fork-doc update)
- Fork-doc PARTIALLY-APPLIED status update: (this session)

ZERO cross-axis cascade. L9-septies + 10-CP-D cluster closes stand. H_T-CP-18 v1.1 α fix + batch-10 RETIRE-READY at `eb4475d` stand. 2751/2751 tests stand.

---

*End of §11 partial ratification. Fork doc status: PARTIALLY-APPLIED. 4 §10.4 rows + §10.5 missing primitives remain OPEN.*

---

## 12. §10.7 tiebreaker resolution + §10.4 deferred-row ratification (2026-05-23, follow-on arc)

**Tiebreaker arc:** Operator authorized "Tiebreaker grep for deferred rows" routing at session resume (AskUserQuestion 2026-05-23 post-checkpoint resume). Empirical investigation against canonical CP plan v2.17 + CP spec v1.11 + (for U-CP-27/43 atomic-unit bodies which live at v2.1/v2.4 amendment layers, since v2.10+ are delta-amendment files) the cumulative cascade.

### 12.1 §10.7 Question (1) — H_T-CP-19 cite shape

**Empirical findings:**

| Unit | Definition site | `Implements:` anchor | Role in C-CP-19 §19 surface |
|---|---|---|---|
| U-CP-43 | v2.4 line 435 (most recent amendment); v2.1 line 2289 base | `[C-CP-19 §19.1, §19.2, §19.4]` | **PRIMARY producer** of `gate_level()` 4-axis multiplicative rule + `_hitl_required` + persona-tier floor. The sole CP-corpus unit anchoring directly on C-CP-19 §19 |
| U-CP-27 | v2.1 line 1388 | `[C-CP-12 §12.2, §12.3, §12.4, §12.5]` | **Consumer** — implements C-CP-12 monotonic-descent + cross-deployment monotonicity composition; `Depends on: [..., U-CP-43, ...]`; consumes `gate_level()` from U-CP-43 at parent dispatch site |
| U-CP-26 | (default-downgrade rule) | (per v2.x plan) | Upstream sub-input to U-CP-43's per-axis floors |

**Anchor-vs-label gap.** Meta-Arch row label "D5 cross-deployment monotonicity" describes U-CP-27's C-CP-12 §12 composition surface. Anchor cite `C-CP-19 §19` describes U-CP-43's 4-axis multiplicative + cross-deployment monotonicity invariant (per CP spec v1.2 line 1604).

**Operator ratification (AskUserQuestion 2026-05-23, session H_T-CP-15..21 deferred rows arc):** **Union: U-CP-26 + U-CP-27 + U-CP-43** (material-location-resident reading per Meta-Arch v1.1 §5.1.1). Surfaces both the formula producer (U-CP-43) and the cross-deployment monotonicity composition consumers (U-CP-26 + U-CP-27). Aligns with H_T-CP-20 multi-cite pattern absorbed at Meta-Arch v1.2.

### 12.2 §10.7 Question (2) — H_T-CP-15 / H_T-CP-16 / H_T-CP-17 primitive grep

**Empirical findings (canonical CP plan v2.17 + CP spec v1.11):**

| Search term | CP plan v2.17 hits | CP spec v1.11 hits |
|---|---|---|
| `memory primitive` | 0 | 0 |
| `files primitive` | 0 | 0 |
| `skills primitive` / `skill primitive` | 0 | 0 |

**Default branch confirmed.** Zero CP-corpus carrier for Memory/Files/Skills primitives. Per fork doc §10.4 default branch: STRIKE anchor + cross-axis re-cite to AS-axis primitive home.

**Operator ratification (same AskUserQuestion 2026-05-23):** All 3 rows → **STRIKE** disposition confirmed. Routing for spec-writer arc: bundle all 4 deferred rows (H_T-CP-15/16/17 STRIKE + H_T-CP-19 union-cite) into single Meta-Arch v1.2 → v1.3 absorption arc.

### 12.3 Ratified §10.4 dispositions (bundled spec-writer arc → Meta-Arch v1.3)

| Row | §2.3 anchor cite | §2.3 carrier units | §5.4 retirement-criterion cite | §5.8 disposition |
|---|---|---|---|---|
| **H_T-CP-15** | **STRIKE** `C-CP-15 §15`; replace with cross-axis cite `C-AS-05 §5 + C-AS-06 §6 + C-AS-07 §7 (Skills primitive declaration) + C-CP-13 §13 (HandoffContext + SubAgentBrief brief loading)` | **STRIKE** `U-CP-33 → U-CP-37`; replace with `U-AS-20..U-AS-27 (Skills authoring + filesystem residence) + U-CP-28..U-CP-30 (HandoffContext + SubAgentBrief composing skills via brief)` | Same as §2.3 cross-axis cite (material-location-resident reading per v1.1 §5.1.1) | RESOLVED at v1.3 |
| **H_T-CP-16** | **STRIKE** `C-CP-16 §16` anchor (current C-CP-16 is audit-ledger entry schema, unrelated to memory primitive); replace with cross-axis cite to AS-axis primitive home + observability namespace `C-AS-14 §14 (memory.* namespace export) + AS-axis primitive declarations` (specific cite shape per spec-writer arc; default = AS spec §14 memory.* export) | **STRIKE** existing carrier; cross-axis re-cite to AS-axis primitive consumers + OD observability consumer | Same as §2.3 cross-axis cite | RESOLVED at v1.3 |
| **H_T-CP-17** | **STRIKE** `C-CP-17 §17` anchor; replace with cross-axis cite `C-AS-14 §14 (files.* namespace export) + AS-axis primitive declarations` (parallel to H_T-CP-16) | **STRIKE** existing carrier; cross-axis re-cite (parallel) | Same as §2.3 cross-axis cite | RESOLVED at v1.3 |
| **H_T-CP-19** | **PRESERVE** `C-CP-19 §19` anchor (aligned) | **REPLACE** `U-CP-46` with **`U-CP-26 + U-CP-27 + U-CP-43`** (union; per §12.1 tiebreaker) | Same as §2.3 union cite | RESOLVED at v1.3 |

**Spec-writer arc scope:** Single absorption commit landing Meta-Arch v1.2 → v1.3 with the 4-row amendment table above. §2.3 + §5.4 row updates + §5.8 disposition updates (5 row dispositions: 4 RESOLVED at v1.3 + H_T-CP-18/20/21 already RESOLVED at v1.2 — only the 4 new RESOLVED transitions are amended). Preserve verbatim all v1.2 content outside amendment sites. FM-2 no-extension discipline: do NOT add missing-primitive rows (§10.5) — those remain DEFERRED to subsequent arc.

### 12.4 Adjacent items NOT addressed at this arc (FM-2 discipline)

- **§4.4.3 CP-axis classification descriptor refresh** (per v1.2 §0.2 adjacent defect (i)) — descriptor rationale columns for H_T-CP-15/16/17/19 not refreshed at v1.3; routed to follow-on cross-row coherence-pass arc
- **§10.5 missing primitives** (4 NEW v1.10/v1.11 contracts: §17.4 hitl_gate / §25 ValidatorFramework / §26 PauseResumeProtocol / §27 MaterialDiffPolicy) — remain DEFERRED to systems-architect re-invocation arc (ADD-style additions, not pure cite fixes)
- **CP-axis substitution count (§4.1 workspace CLAUDE.md cite)** — currently states 21 entries. With H_T-CP-15/16/17 STRIKE dispositions, count becomes 18 entries. Workspace CLAUDE.md §4.1 amendment routed to follow-on session (or bundled with missing-primitive arc that re-establishes count)
- **Per-axis `harness-cp/CLAUDE.md` §4.1 retirement table** — may reference deferred rows; reconciliation routed to follow-on arc
- **§5.8 γ-audit appendix follow-on** — Meta-Arch v1.1 §5.8 listed 5 findings (H_T-CP-16/17/19/20/21). At v1.2, H_T-CP-20/21 marked RESOLVED. At v1.3, H_T-CP-16/17/19 will be marked RESOLVED. H_T-CP-15 was NOT in §5.8 (it was identified at fork doc §10.4 as parallel pattern); v1.3 may add a §5.8 footnote noting v1.3 absorbs H_T-CP-15 alongside the original 5 findings

### 12.5 Post-arc fork status

After Meta-Arch v1.3 absorbing arc lands: 7 of 7 §10.4 rows APPLIED; §10.5 missing primitives remain OPEN. Fork status will advance from PARTIALLY-APPLIED → APPLIED-EXCEPT-MISSING-PRIMITIVES. Full close awaits the systems-architect re-invocation arc for §10.5 4-primitive addition (and any subsequent operator-ratification of those additions).

ZERO cross-axis cascade expected from v1.3 absorption (mirrors v1.2 zero-cascade pattern). 2751/2751 tests expected to stand.

---

*End of §12 tiebreaker resolution + ratification. Fork doc status post-§12: PARTIALLY-APPLIED with all 7 §10.4 rows now RATIFIED (3 APPLIED at v1.2 + 4 RATIFIED-AWAITING-v1.3-ABSORBING-ARC). §10.5 missing primitives remain OPEN.*

---

## 13. v1.3 absorbing arc — partial application + new sibling fork (2026-05-23, same session as §12)

**Absorbing arc.** Meta-Arch v1.2 → v1.3 spec-writer arc executed against §12.3 ratified disposition table. **FM-1 + FM-3 HALT condition surfaced** during empirical verification pass: §12.3 cite shapes for H_T-CP-15/16/17 borrowed Meta-Arch §2.2 H_T-AS-6/7/8 carrier cites that are themselves empirically phantom (U-AS-20..U-AS-27 implement SECRETS surface, not Skills/memory/files). Spec-writer filed new sibling Class 1 fork `.harness/class_1_fork_meta_arch_section_2_2_as_axis_carrier_phantom_cites.md` documenting the §2.2 recurrence and HALTed H_T-CP-15/16/17 application. H_T-CP-19 cites (U-CP-26 + U-CP-27 + U-CP-43) verify empirically clean and proceed at v1.3.

**Per-row landing status:**

| §10.4 / §12.3 row | v1.3 disposition | Authority for status |
|---|---|---|
| **H_T-CP-15** | **DEFERRED-AT-v1.3** — sibling fork §12.3 borrowed §2.2 H_T-AS-6/7 carrier phantoms; cite shape owed | New fork `class_1_fork_meta_arch_section_2_2_as_axis_carrier_phantom_cites.md` §4 PARTIAL-APPLY routing |
| **H_T-CP-16** | **DEFERRED-AT-v1.3** — same | Same |
| **H_T-CP-17** | **DEFERRED-AT-v1.3** — same | Same |
| **H_T-CP-19** | ✓ **APPLIED at v1.3** — §2.3 + §5.4 carrier-cite re-pointed to U-CP-26 + U-CP-27 + U-CP-43; §5.8 disposition row updated to RESOLVED at v1.3 | Meta-Arch v1.3 §0.3 Site 1/2/3 |

**Sibling fork filed at same session.** `.harness/class_1_fork_meta_arch_section_2_2_as_axis_carrier_phantom_cites.md` — Class 1, OPEN. Documents §2.2 H_T-AS-6/7/8 carrier-cite phantom recurrence (analogous to original §5.4 fork at §2.3/§5.4 CP-axis). Routing target = `systems-architect` skill at follow-on arc for refined AS-axis cite shapes + sibling-fork H_T-CP-15/16/17 re-ratification.

**Fork status post-§13.** PARTIALLY-APPLIED → **APPLIED-EXCEPT-(H_T-CP-15/16/17 + missing-primitives + §2.2-AS-axis-recurrence)**. Total §10.4 row applications: 4/7 (H_T-CP-18 at v1.1; H_T-CP-20 + H_T-CP-21 at v1.2; H_T-CP-19 at v1.3). 3/7 deferred to sibling-fork resolution. §10.5 missing-primitive 4 NEW contracts (§17.4/§25/§26/§27) remain OPEN at separate routing track.

**v1.3 commits at this session.**
- Sibling fork filing: this session, `.harness/class_1_fork_meta_arch_section_2_2_as_axis_carrier_phantom_cites.md`
- Meta-Arch v1.3 absorption: this session, `design-substrate/Phase_7_Meta_Architecture_v1.md`
- §13 footer update at this fork: this session
- Single bundled commit (per operator routing choice)

**Pattern recurrence observation.** Including this surfacing, **5 phantom-cite/mis-anchoring Class 1 forks** filed across 3-session cluster:
1. `[[fork-sandbox-decision-policy-phantom-cite]]` — APPLIED L9-septies
2. `[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap]]` — APPLIED L9-septies arc
3. `[[fork-h-t-cp-18-phantom-retirement-cite]]` — APPLIED-AND-RETIRE-READY (Meta-Arch v1.1)
4. `[[fork-meta-arch-cp-spec-renumbering-drift]]` (this fork) — APPLIED-EXCEPT-(3-rows + missing-primitives) (Meta-Arch v1.2 + v1.3)
5. **NEW: `class_1_fork_meta_arch_section_2_2_as_axis_carrier_phantom_cites`** — OPEN (Meta-Arch §2.2 AS-axis recurrence)

The recurrence-pattern observation at v1.1 §5.8 and §10.6 (k) is now empirically reinforced. Memory pattern at `[[advisor-before-substantive-work-for-cross-axis-blockers]]` trigger surface expanded to include "borrowed cite shape from another Meta-Arch section without empirical verification of the borrowed cite" — see new fork §7.

ZERO cross-axis cascade at v1.3 (H_T-CP-19 single-row scope, all cites within CP plan v2.x). L9-septies + 10-CP-D cluster closes stand. H_T-CP-18 batch-10 RETIRE-READY at `eb4475d` stands. 2751/2751 tests stand.

---

*End of §13 v1.3 absorbing arc + new sibling fork filing. Fork doc status post-§13: APPLIED-EXCEPT-(H_T-CP-15/16/17 + missing-primitives + §2.2-AS-axis-recurrence). 4 of 7 §10.4 rows APPLIED. 3 rows + §10.5 missing primitives + new §2.2 recurrence carried at follow-on arcs.*

---

## 14. v1.4 absorbing arc — H_T-CP-15/16/17 APPLIED via new-sibling-fork §6 cite shapes (2026-05-23, same session as §13)

**Absorbing arc.** Meta-Arch v1.3 → v1.4 spec-writer arc executed against new sibling fork `.harness/class_1_fork_meta_arch_section_2_2_as_axis_carrier_phantom_cites.md` §6 systems-architect ratified recommendation (operator AskUserQuestion 2026-05-23: ratify all 6 rows + ambiguities a.i + b.i + c.i). Single bundled commit landed Meta-Arch v1.4 + new-sibling-fork §7 application footer + this §14 footer.

**§12.3 disposition replacement.** This fork's §12.3 ratified dispositions for H_T-CP-15/16/17 borrowed Meta-Arch §2.2 H_T-AS-6/7 phantom cites (per `[[fork-meta-arch-section-2-2-as-axis-carrier-phantom-cites]]` §3 cross-fork dependency analysis). New-sibling-fork §6.4.4/§6.4.5/§6.4.6 REPLACE those phantom-bearing dispositions with empirically-verified AS-axis primitive home cites. v1.4 spec-writer applied the REPLACEMENT dispositions, not the §12.3 originals.

**Per-row application status (all 7 §10.4 rows now closed):**

| §10.4 row | v1.4 final disposition | Cite shape applied | Application arc |
|---|---|---|---|
| H_T-CP-15 | ✓ APPLIED via new-sibling-fork §6.4.4 | `C-AS-13 + C-AS-14 §14.4 + C-CP-13 §13` / `U-AS-28 + U-AS-31 + U-CP-28..30` | v1.4 (this session) |
| H_T-CP-16 | ✓ APPLIED via new-sibling-fork §6.4.5 | `C-AS-13 §13.1 row 11 + C-AS-14 §14.7` / `U-AS-28 + U-AS-31` at §2.3 + §5.4 | v1.4 (this session) |
| H_T-CP-17 | ✓ APPLIED via new-sibling-fork §6.4.6 | `C-AS-13 §13.1 row 10 + C-AS-14 §14.6` / `U-AS-28 + U-AS-31` at §2.3 + §5.4 | v1.4 (this session) |
| H_T-CP-18 | ✓ APPLIED (carry-forward from v1.1 + v1.2) | §5.4 v1.1 α fix + §2.3 v1.2 re-anchor to C-CP-27 §27 + U-CP-00b | v1.1 + v1.2 |
| H_T-CP-19 | ✓ APPLIED via §12.3 ratification (clean cites) | `C-CP-19 §19` / `U-CP-26 + U-CP-27 + U-CP-43` at §2.3 + §5.4 | v1.3 (this session, earlier) |
| H_T-CP-20 | ✓ APPLIED (carry-forward from v1.2) | §2.3 multi-contract anchor augment + §5.4 carrier augment | v1.2 |
| H_T-CP-21 | ✓ APPLIED (carry-forward from v1.2) | §2.3 anchor augment to C-CP-21 + C-CP-25 + §5.4 U-CP-52 strike | v1.2 |

**§5.8 audit-summary table cumulative status (post-v1.4):**

| Bucket | v1.4 count | Members |
|---|---|---|
| Resolved | 6 of 6 H_T-CP-* findings (1 α fix + 5 §5.8 audit findings) | H_T-CP-18 (v1.1) + H_T-CP-20/21 (v1.2) + H_T-CP-19 (v1.3) + H_T-CP-16/17 (v1.4) |
| Clean (no defect identified) | 17 | (enumerated at §5.8) |

All H_T-CP-* §5.8 phantom-or-partial findings RESOLVED across v1.1 + v1.2 + v1.3 + v1.4. The original Class 1 fork at this doc is functionally CLOSED for all §10.4 row dispositions.

**Fork status post-§14.** APPLIED-EXCEPT-(H_T-CP-15/16/17 + missing-primitives + §2.2-AS-axis-recurrence) → **APPLIED-EXCEPT-missing-primitives**. The §2.2-AS-axis-recurrence + H_T-CP-15/16/17 deferred dispositions both RESOLVED at v1.4 via new sibling fork. §10.5 missing-primitive 4 NEW contracts (§17.4/§25/§26/§27) remain OPEN at separate routing track.

**Pattern density observation.** Across this fork + new sibling fork + 3 prior phantom-cite forks in the 3-session cluster, the consistent surfacing mechanism is **empirical-verification pass at apply-time** rather than at recommendation-authoring time. The fork chain:
1. `[[fork-sandbox-decision-policy-phantom-cite]]` — surfaced by `spec-writer` empirical grep before commit
2. `[[fork-u-rt-68-retry-wrap-and-bootstrap-wiring-gap]]` — surfaced by `phase-7-implementation` shape mismatch
3. `[[fork-h-t-cp-18-phantom-retirement-cite]]` — surfaced by `phase-7-substitution-retirement` cite verification
4. This fork (`[[fork-meta-arch-cp-spec-renumbering-drift]]`) — surfaced by retirement-event replacement-cite investigation
5. `[[fork-meta-arch-section-2-2-as-axis-carrier-phantom-cites]]` — surfaced by `spec-writer` apply-time verification of `systems-architect` recommendation's borrowed cite shapes

The structural lesson: every layer in the recommendation → ratification → application chain must perform empirical verification of cited surfaces, because each layer's verification scope is bounded. `systems-architect` reasons against the authority chain but does not always grep the apply-side files; `spec-writer` greps the apply-side files but does not always reason against the upstream authority chain. The FM-1 + FM-3 disciplines at `spec-writer` empirical-verification pass are the critical structural safeguard against cross-layer phantom propagation.

ZERO cross-axis cascade at v1.4. L9-septies + 10-CP-D cluster closes stand. H_T-CP-18 batch-10 RETIRE-READY at `eb4475d` stands. 2751/2751 tests stand.

---

*End of §14 v1.4 absorbing arc. Fork doc status post-§14: APPLIED-EXCEPT-missing-primitives. 7/7 §10.4 rows now APPLIED. New-sibling-fork §6/§7 RESOLVED parallel. §10.5 missing-primitives + per-row retirement filings + parallel-axis audit + §4.4.3 coherence pass carried at follow-on arcs.*
