# Class 1 Fork — Meta-Architecture ↔ CP-spec systemic alignment drift at H_T-CP-15..21

**Filed:** 2026-05-23 at γ-audit follow-on arc post-Meta-Arch v1.1 landing (`40d9f78`) + batch-10 retirement ledger (`eb4475d`).
**Status:** OPEN — awaiting `systems-architect` skill invocation for cross-artifact alignment recommendation.
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

*End of Class 1 fork doc. ALL §5.8 γ-audit per-row retirement filings HALTED pending α/β/γ resolution. The H_T-CP-18 v1.1 α fix + batch-10 RETIRE-READY landing at HEAD `eb4475d` stand and are NOT in scope for this fork.*
