# spec-writer deliverable — Tension 001 fix applied to Spec_Information_Substrate

**Constraint compliance.** No repository file was modified. The fixture file `.claude/skills/spec-writer/evals/fixtures/Spec_Information_Substrate_PRE_tension001_fix.md` is left untouched. The full edited spec content and the change-note are reproduced below as the deliverable.

---

## Part A — Change-note (standalone record)

**Change-note (v1.2 → v1.3) — Tension 001 sub-role-count correction**

**Trigger.** `Phase_7_Class_3_Tension_001_*` record — resolved. Tension 001: the §3 C-IS-03 combined-git-tier section has a sub-role count of **five**, not four. The §3 sub-role table (lines 192–196) enumerates 5 rows (Versioning / State-ledger via commit stream / JSONL event ledger / Shadow-Git checkpointing / Worktree-isolation for concurrent sub-agent reads); `ADR-F2 §Decision` and the ADD both enumerate 5 (the ADD quote at C-IS-03 itself lists 5 git roles); but the §3 prose miscounts as "four sub-roles" in 5 places. The decided fix: change every prose "four sub-role(s)" occurrence in C-IS-03 §3 to "five".

**Scope of revision (contract IDs + sections).** C-IS-03 §3 (Combined git tier role decomposition) only. Exactly 5 prose sites, all inside §3:

| Site | Before | After |
|---|---|---|
| §3 Contract surface (line 178) | `Four-sub-role git tier composition` | `Five-sub-role git tier composition` |
| §3 ADR commitment(s) honored (line 182) | `combined git tier serving four-sub-role composition` | `combined git tier serving five-sub-role composition` |
| §3 Specification content lead-in (line 188) | `serves four sub-roles within a single git repository` | `serves five sub-roles within a single git repository` |
| §3 Sub-role co-residence contract (line 198) | `All four sub-roles share the same git repository identity` | `All five sub-roles share the same git repository identity` |
| §3 Cross-sub-role consistency invariant (line 206) | `the four sub-roles share that ledger` | `the five sub-roles share that ledger` |

Hyphenation and capitalization preserved per site (the two adjectival hyphenated forms `Four-sub-role` / `four-sub-role` become `Five-sub-role` / `five-sub-role`; the three noun-phrase forms `four sub-roles` become `five sub-roles`).

**Sections revised.** Status block (Status row revised; third Revision + Revision-date pair appended for v1.2 → v1.3). This Change-note (v1.2 → v1.3) section (new; prepended between the Status block and the existing Change-note (v1.1 → v1.2)). C-IS-03 §3 — the 5 prose sites above.

**Sections preserved verbatim at v1.3.** All sections outside C-IS-03 §3: §Change-note (v1.1 → v1.2); §Change-note (v1 → v1.1); §Front-matter (Axis declaration; Axis-grounding note; PRD requirement scope; ADR scope; Persona-linkage substrate; Scope and out-of-scope); §1 C-IS-01; §2 C-IS-02; §4 C-IS-04; §5 C-IS-05; §6 C-IS-06; §7 C-IS-07; §8 C-IS-08; §9 C-IS-09; §10 C-IS-10; §[carry-forwards]; §[traceability]; §[coherence pass]. Within C-IS-03 §3 itself, everything except the 5 count words is preserved verbatim — including the §3 sub-role table (lines 192–196, already 5 rows), the embedded `ADR-F2 §Decision` / ADD quote at line 182 (the quote enumerates 5 git roles and is consistent with FIVE — only the surrounding count word was wrong), the Sub-role co-residence bullet list, the Deferred-to-implementation-discretion subsection.

**Verbatim-layer note.** The ADD quote in the line-182 "ADR commitment(s) honored" sentence (`"Git serves a combined role: ... versioning ... + ... commit stream + JSONL event ledger ... + ... shadow-Git checkpointing ... + worktree-isolation ..."`) is byte-exact preserved; only the spec-writer's own surrounding prose count word (`four-sub-role` → `five-sub-role`) changed. The verbatim layer round-trips against the resolution source.

**New version.** v1.2 → v1.3.

**Surfaced findings (NOT patched — no-extension discipline).**

- **F-T001-a — numeric-form miscount in §[coherence pass].** §[coherence pass] Audit 6.1, "Contract grade" row (line 657), contains `C-IS-03 4-sub-role schema (enum)` — the same sub-role miscount in numeric form (`4-sub-role`). Tension 001's decided fix authorized only the prose `four sub-role(s)` sites in C-IS-03 §3; it did not authorize edits to the numeric form, and §[coherence pass] is preserved verbatim as the v1 + v1.1 point-in-time historical audit record per the existing §"[coherence pass] preservation discipline" (Change-note v1→v1.1 and v1.1→v1.2). Patching it here would be both a spec extension beyond the authorized fix and a breach of the coherence-pass preservation discipline. Surfaced as a finding for a follow-up operator decision / tension record; **not patched** in this revision.

**Downstream absorption owed (flagged for `implementation-planner` revision-pass).** Any IS-axis plan unit that cites C-IS-03's "four sub-role" cardinality (e.g., U-IS-NN units implementing the combined-git-tier decomposition) inherits the corrected count of FIVE. Cross-file back-references in `Implementation_Plan_Information_Substrate_v2_2.md` are not the spec-writer's edit — they are flagged here for `implementation-planner` revision-pass absorption.

**Tension record disposition.** `Phase_7_Class_3_Tension_001_*` record updated to disposition **applied** (per the `spec-tension-record-pattern`): fix applied to C-IS-03 §3 at 5 sites, spec bumped v1.2 → v1.3, change-note recorded.

---

## Part B — Full edited spec content (v1.3)

```markdown
# Spec — Information Substrate v1

## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Information_Substrate_v1.md` |
| Status | **Proposed** (v1.3 pending Phase 6 entry per `Project_Workflow_v1_2.md` §3.1); final-revision-pass post-P5-CK iter-2 close per `Project_Workflow_v1_2.md` §4.1.2 modified path; coherence pass preserved verbatim as v1 + v1.1 historical record per Change-note §"§[coherence pass] preservation discipline"; v1.2 → v1.3 Phase-7 Tension 001 sub-role-count correction applied |
| Date | 2026-05-13 |
| Phase | 5 — specification authoring (session 1 of 4–6) per `Project_Workflow_v1_2.md` §2.5 |
| Skill | `spec-writer` SKILL.md in Stage-3 final-specification mode per skill description |
| Axis | Information Substrate (per `Phase_5_Entry_Handoff.md` §3.1 axis sequencing) |
| Source-set | `PRD_v1.0.md` §2 (R-IS-01 through R-IS-04); `Architectural_Design_Document_v1.md` v1.2 §2.2 + §5.2.2 + §5.3.3 + §6.3.1; `ADR-F2.md` v1.2 (§Decision + §Rationale (a) + §Rationale (a.1) + §Consequences (a)(b)(c) + §"Permanent tensions engaged"); `Persona_Document_v1.md` §3.1.1 + §3.1.3 + §5.1 + §7 + §8.1 + §10.1 + §10.2 + §10.4 |
| Entry authorization | `Phase_5_Session_1_Session_Prompt.md` §4 entry-gate verified (6/6); `Phase_5_Entry_Handoff.md` §5 preconditions verified |
| ODs applied | OD-5-1.A (per-axis multi-document) + OD-5-2.A (spec-writer judgment; Information Substrate per handoff §3.1) + OD-5-3.A (as-needed council consultant; no escalation invoked at session 1) + OD-5-4.A (aggregate P5-CK at full close) |
| Exit gate | This spec filed at `/mnt/user-data/outputs/`; §[coherence pass] returns ✅ PASS at all five audit dimensions; `Phase_5_Session_2_Session_Prompt.md` authored at session close |
| Revision | v1 → v1.1 (P5-CK iter-1 close mechanical + substantive revision per modified `Project_Workflow_v1_2.md` §4.1.2 path — F-IS-01 substrate-residence statement aligned with five-tier table episodic-row reading; F-IS-02 keying-tuple ↔ entry-shape reconciliation deferred to D-ADR on ledger schema via C-IS-07 §7.4 "Deferred to implementation discretion" subsection per ADR-F2 §Consequences (c); F-IS-03 reclamation operational semantic defined inline at C-IS-09 §9.2 per operator sub-decision; C-IS-01, C-IS-02 table, C-IS-03 through C-IS-10 substantive content preserved verbatim except as enumerated) |
| Revision date | 2026-05-13 |
| Revision | v1.1 → v1.2 (P5-CK iter-2 close final-revision-pass per modified `Project_Workflow_v1_2.md` §4.1.2 path — F-iter2-03 C-IS-10 §10.4 line 551 Action Surface row body-citation bump `ADR-D3 v1.1` → `ADR-D3 v1.2` at two sites (cell-name parenthetical + cell prose citation) per Pattern P2-PHASE-5 use-latest-version discipline; cited content materially unchanged at ADR-D3 v1.2 §1.8.1 Skills loading discipline per `P5-CK_Iteration_2_Close_Handoff.md` §3.5; all other contracts preserved verbatim) |
| Revision date | 2026-05-13 |
| Revision | v1.2 → v1.3 (Phase-7 Class-3 Tension 001 resolution applied — C-IS-03 §3 combined-git-tier sub-role count corrected from "four" to "five" at 5 prose sites to align with the §3 sub-role table (5 rows), ADR-F2 §Decision, and the ADD; numeric-form miscount `4-sub-role` at §[coherence pass] Audit 6.1 surfaced as a finding, not patched, per coherence-pass preservation discipline + no-extension discipline; all other content preserved verbatim) |
| Revision date | 2026-05-15 |

---

## Change-note (v1.2 → v1.3)

**Scope of revision.** Single-tension correction pass clearing `Phase_7_Class_3_Tension_001_*` (Class 3 — informational/documentation defect: a sub-role-count miscount internal to C-IS-03 §3 prose). Tension 001 resolution: the combined-git-tier sub-role count is **five**, not four. The §3 sub-role table at lines 192–196 enumerates 5 rows (Versioning; State-ledger via commit stream; JSONL event ledger; Shadow-Git checkpointing; Worktree-isolation for concurrent sub-agent reads); `ADR-F2 §Decision` and the ADD both enumerate 5 (the ADD quote embedded at C-IS-03's "ADR commitment(s) honored" sentence itself lists 5 git roles). The §3 prose miscounted as "four sub-roles" / "four-sub-role" in 5 places. The decided fix — and the entirety of this revision — is to change every such prose count word from "four" to "five".

**Changes inline.** Status block (Status row revised; third Revision row + Revision date row appended for v1.2 → v1.3). This Change-note (v1.2 → v1.3) section (new; prepended between the Status block and the previous Change-note v1.1 → v1.2). §3 C-IS-03 — 5 prose count-word sites: (1) Contract surface — `Four-sub-role` → `Five-sub-role`; (2) ADR commitment(s) honored — `four-sub-role composition` → `five-sub-role composition`; (3) Specification content lead-in — `serves four sub-roles` → `serves five sub-roles`; (4) Sub-role co-residence contract — `All four sub-roles` → `All five sub-roles`; (5) Cross-sub-role consistency invariant — `the four sub-roles share that ledger` → `the five sub-roles share that ledger`. Five amendment sites total; no other content modified.

**Sections preserved verbatim at v1.3.** §Change-note (v1.1 → v1.2); §Change-note (v1 → v1.1); §Front-matter (Axis declaration; Axis-grounding note; PRD requirement scope; ADR scope; Persona-linkage substrate; Scope and out-of-scope); §1 C-IS-01 (canonical filesystem path contract); §2 C-IS-02 (artifact-tier layering schema); §4 C-IS-04 (atomic deploy contract); §5 C-IS-05 (state-ledger entry-shape signature); §6 C-IS-06 (hash-chain integrity); §7 C-IS-07 (read/write contract pair); §8 C-IS-08 (shadow-Git checkpoint contract); §9 C-IS-09 (worktree-isolation contract); §10 C-IS-10 (substrate seam exports surface); §[carry-forwards]; §[traceability]; §[coherence pass]. Within §3 C-IS-03 itself, all content except the 5 count words is preserved verbatim — the §3 sub-role table (lines 192–196; already 5 rows), the embedded ADR-F2 §Decision / ADD quote (which enumerates 5 git roles and is consistent with FIVE — only the spec-writer's surrounding prose count word changed), the Sub-role co-residence bullet list, the Cross-sub-role consistency invariant prose, and the Deferred-to-implementation-discretion subsection.

**Surfaced findings (not patched).** §[coherence pass] Audit 6.1 "Contract grade" row contains the same miscount in numeric form — `C-IS-03 4-sub-role schema (enum)`. Tension 001 authorized only the prose `four sub-role(s)` sites in C-IS-03 §3; §[coherence pass] is preserved verbatim as the v1 + v1.1 point-in-time historical audit record per the §"[coherence pass] preservation discipline" below. Patching the numeric form would be a spec extension beyond the authorized fix and a breach of coherence-pass preservation. Surfaced here as finding **F-T001-a** for a follow-up operator decision; not patched in this revision.

**Downstream absorption owed.** IS-axis plan units in `Implementation_Plan_Information_Substrate_v2_2.md` that cite C-IS-03's combined-git-tier sub-role cardinality inherit the corrected count of FIVE. Cross-file back-reference absorption is `implementation-planner` revision-pass work, flagged here, not done in this spec edit.

**§[coherence pass] preservation discipline.** §[coherence pass] at v1.3 is preserved verbatim as the v1 + v1.1 point-in-time audit historical record. Its `4-sub-role` numeric form is accurate as historical record of the v1 audit state; the v1.2 → v1.3 Tension 001 correction does not re-run the audit. Per the v1 → v1.1 and v1.1 → v1.2 §"[coherence pass] preservation discipline" precedent.

---

## Change-note (v1.1 → v1.2)

**Scope of revision.** Single-finding final revision pass clearing `Adversarial_Review_5_iter2.md` F-iter2-03 / Pattern P2-PHASE-5 (Class 1 mechanical — body-citation drift `ADR-D3 v1.1` → `v1.2` at C-IS-10 §10.4 Action Surface row, line 551, two sites in one table row: cell-name parenthetical + citation in cell prose). Cited content materially unchanged at ADR-D3 v1.2 per `P5-CK_Iteration_2_Close_Handoff.md` §3.5; token-level alignment only under use-latest-version discipline. Single mechanical bump applied at this revision pass per `P5-CK_Iteration_2_Final_Revision_Pass_Session_Prompt.md` §5.1 Stage 2.

**Sections preserved verbatim at v1.2.** §Front-matter (Axis declaration; Axis-grounding note; Persona summary; PRD requirement scope; ADR commitment scope; cross-axis citation table; Deferred to implementation discretion); §2 C-IS-01 (workflow root layer schema); §2 C-IS-02 (five-tier table; substrate residence; survival semantics; cross-tier traceability); §3 C-IS-03 (combined git tier role decomposition); §4 C-IS-04 (workflow-class-tunable shadow-Git checkpointing); §5 C-IS-05 (state-ledger entry-shape signature); §6 C-IS-06 (hash-chain integrity); §7 C-IS-07 (idempotent-write keying tuple, read contract, composition format, multi-seam T-perm-2 engagement, Deferred-to-implementation-discretion subsection); §8 C-IS-08 (shadow-Git checkpoint contract); §9 C-IS-09 (per-sub-agent worktree opt-in declaration, worktree-termination contract, concurrent-read isolation invariant, multi-writer scaling boundary, all Deferred-to-implementation-discretion subsections); §10 C-IS-10 §10.1, §10.2, §10.3, §10.5, §10.6, §10.7, §10.8 (all substrate seam exports except §10.4 Action Surface row at line 551); §[traceability] matrix; §[carry-forwards]; §[coherence pass] (preserved verbatim as v1 + v1.1 historical record).

**Changes inline.** Status block (Status row revised; second pair of Revision row + Revision date row appended for v1.1 → v1.2). This Change-note section (new; appended between Status block and previous Change-note v1 → v1.1). §10 C-IS-10 §10.4 Action Surface row at line 551 (two body-citation sites in one table row: `(D3 v1.1 Skills loading discipline)` → `(D3 v1.2 Skills loading discipline)` cell-name parenthetical + `per ADR-D3 v1.1` → `per ADR-D3 v1.2` citation in cell prose). Two amendment sites total; no other content modified.

**§[coherence pass] preservation discipline.** §[coherence pass] section at v1.2 is preserved verbatim as the v1 + v1.1 point-in-time audit historical record. Audit rows referencing v1 substrate state and v1.1 D-ADR-citation state are accurate historical record of those audit passes; v1.2 final-revision-pass mechanical body-citation bump does not re-run the audit. Per `P5-CK_Iteration_2_Final_Revision_Pass_Session_Prompt.md` §5.2 §[coherence pass] preservation discipline.

---

## Change-note (v1 → v1.1)

**Scope of revision.** Three-finding revision pass clearing `Adversarial_Review_5.md` F-IS-01 (Class 2 — C-IS-02 tier-residence internal contradiction at episodic tier), F-IS-02 (Class 2 — C-IS-07 keying tuple not reconciled with C-IS-05 entry-shape signature), and F-IS-03 (Class 1 — C-IS-09 §9.2 "reclamation" operational-semantic ambiguity). All three findings resolvable at this single axis-spec revision pass per `P5-CK_Iteration_1_Close_Handoff.md` §3.2 + §3.3.

**F-IS-01 Path A resolution per operator sub-decision.** C-IS-02 §"Tier composition contract" / "Substrate residence" statement at line 132 rewritten to align with the five-tier table at lines 122–128. The table commits `episodic` tier as "Filesystem (run-bounded paths)" with no git surface; the revised substrate-residence statement reads "all durable-survival tiers (semantic / procedural / durable) reside on filesystem AND git per ADR-F2 §Decision combined-tier role; working and episodic tiers reside on filesystem only (no git)". The table is the canonical reading; the statement aligns to the table.

**F-IS-02 Path B resolution per operator sub-decision.** C-IS-07 §7.1 idempotent-write keying tuple `(thread_id, step_id, idempotency_key)` retained verbatim (canonical per ADR-F2 §Consequences (c) Stripe-style convention citation). The relationship between the keying tuple and the C-IS-05 six-field entry shape is explicitly deferred to a downstream D-ADR on ledger schema via a new entry at C-IS-07 §7.4 "Deferred to implementation discretion" subsection. The deferral cites ADR-F2 §Consequences (c) "defers the relationship reconciliation to the D-ADR on ledger schema fields" as the upstream-substrate authority. F2-12 active engagement on ledger-schema D-ADR per ADD §6.3.1 + PRD §[carry-forwards] [CF-1] (parallel `council-orchestrator` C7+C9 session at operator discretion) is the open downstream resolution path; this revision does not pre-empt that work.

**F-IS-03 Path C resolution per operator sub-decision.** C-IS-09 §9.2 worktree-termination contract row at line 456 receives inline definition of "reclamation" operational semantic: reclamation = `git worktree remove` invocation + directory contents removal, triggered at operator-policy-controlled lifecycle-marker boundary. The mechanical operation and the policy trigger are both specified; specific lifecycle-marker policy is operator territory at workflow-binding time and remains at the existing C-IS-09 §9.4 "Deferred to implementation discretion" subsection ("specific worktree reclamation cleanup policy").

**Sections preserved verbatim.** §1 Axis declaration / Axis-grounding note / Persona summary; §2 C-IS-01 (workflow root layer schema); §2 C-IS-02 five-tier table at lines 122–128 (the canonical reading; substrate-residence statement aligns to the table, not vice-versa); §2 C-IS-02 Survival semantics + Cross-tier traceability paragraphs; §3 C-IS-03 (combined git tier role decomposition); §4 C-IS-04 (workflow-class-tunable shadow-Git checkpointing); §5 C-IS-05 (state-ledger entry-shape signature — the six-field tuple); §6 C-IS-06 (hash-chain integrity); §7 C-IS-07 §7.1 keying tuple statement (canonical per ADR-F2 §Consequences (c)); §7 C-IS-07 §7.2 read contract; §7 C-IS-07 §7.3 composition format; §7 C-IS-07 §7.4 multi-seam T-perm-2 engagement; §8 C-IS-08 (shadow-Git checkpoint contract); §9 C-IS-09 §9.1 + §9.3 + §9.4 (per-sub-agent worktree opt-in declaration, concurrent-read isolation invariant, multi-writer scaling boundary, all Deferred-to-implementation-discretion subsections); §10 C-IS-10 (substrate seam exports surface); §[traceability] matrix; §[carry-forwards]; §[coherence pass] (preserved verbatim as v1 point-in-time historical audit per PRD v1.0 → v1.0.1 precedent).

**Status posture.** `Status: Proposed (v1.1 pending P5-CK iteration 2 clearance per Project_Workflow_v1_2.md §3.1)`. v1.1 enters P5-CK iteration 2 as input artifact alongside ADR-D3 v1.2, PRD v1.0.1, and the three other Phase 5 spec revisions per handoff §6.1 entry-gate checklist.

**Changes inline.** Status block (Status row revised; Revision row + Revision date row appended). This Change-note section (new). §2 C-IS-02 substrate-residence statement at line 132 (rewrite). §7 C-IS-07 §7.4 "Deferred to implementation discretion" subsection at line 373 (append new entry covering keying-tuple ↔ entry-shape deferral). §9 C-IS-09 §9.2 worktree-termination contract row at line 456 (inline reclamation definition). No other content modified.

**§[coherence pass] preservation discipline.** §[coherence pass] section is v1 point-in-time audit; v1.1 mechanical revision does not re-run the audit. Audit rows referencing v1 substrate state are accurate historical record. v1.1 → v1.2 (if needed at iteration 2 entry or post-iter-2) is the proper moment for fresh coherence pass.

---

## Front-matter

### Axis declaration

Per OD-5-2.A spec-writer judgment with handoff §3.1 recommendation followed: **Information Substrate** is the session-1 axis. Rationale:

- **Smallest axis surface.** One foundational ADR (F2 v1.2); four PRD requirements (R-IS-01 through R-IS-04). No D-ADRs in axis per ADD §3.2 OD applied.
- **Substrate seam priority.** The F2 state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` is the harness-canonical join key against which every downstream axis composes — engine event history (Control Plane via D1), audit-ledger cryptographic shape (Operational Discipline via D5), sandbox-violation events (Action Surface via D2), span emission (Operational Discipline via D6) all join on `idempotency_key` per ADD §2.2 Synthesis. Authoring the substrate seam first locks the composition surface for sessions 2–4.
- **Session 1 warmup.** Exercising the inversion-discipline analog (`Phase_5_Session_1_Session_Prompt.md` §1.2 + `Phase_5_Entry_Handoff.md` §6.3) at the smallest axis surface before scaling to denser axes (Control Plane at 5 ADRs / 12 PRD requirements).

### Axis-grounding note

The Information Substrate axis hosts **one foundational ADR** (F2 v1.2 — filesystem + git canonical state substrate with files-as-artifacts and combined git tier) per ADD §2.2. §3 (Information Substrate D-ADRs) is empty per ADD §3.2 OD applied. Cross-axis composition with the control plane (F3 ↔ F2 substrate seam per ADD §2.3), action surface (F5 ↔ F2 audit composition per ADD §2.5), and operational discipline (D6 ↔ F2 span schema composition per ADD §3.4.1) is captured at C-IS-10 (substrate seam exports surface) for downstream-axis specs to consume by citation.

### PRD requirement scope

| PRD requirement | Observer role | Primary ADR section citation |
|---|---|---|
| R-IS-01 — Files-as-artifacts at canonical filesystem paths | Production-time operator + Downstream maintainer | ADR-F2 v1.2 §Decision; ADD §2.2 Synthesis |
| R-IS-02 — Git as combined-tier state record | Downstream maintainer | ADR-F2 v1.2 §Decision; ADD §2.2 Synthesis |
| R-IS-03 — State-ledger entry shape with hash-chain integrity | Downstream maintainer | ADR-F2 v1.2 §Decision + §Rationale (a.1); ADD §2.2 Synthesis |
| R-IS-04 — Workload-class-opt-in shadow-Git checkpoint and worktree isolation | Production-time operator + Downstream maintainer | ADR-F2 v1.2 §Decision; ADD §2.2 Synthesis |

### ADR scope

| ADR | Version | Role in axis |
|---|---|---|
| F2 | v1.2 | Sole foundational ADR; commits filesystem + git canonical state substrate; commits artifact-tier layering, combined git tier role, state-ledger entry shape, hash-chain integrity construction discipline, workload-class-opt-in shadow-Git + worktree-isolation |

### Persona-linkage substrate

| Persona anchor | Inheriting requirement(s) |
|---|---|
| §3.1.1 (software engineering — F2 leverage maximal) | R-IS-04 |
| §3.1.3 (pipeline automation — durability tier mandatory) | R-IS-04 |
| §5.1 (state lives on local filesystem + remote git) | R-IS-01, R-IS-02 |
| §7 (workflow-definition surface — both markdown-spec-driven and code-driven authoring) | R-IS-01 |
| §8.1 (software-engineering action surface — code execution + filesystem + git as primary) | R-IS-04 |
| §10.1 (filesystem + git as canonical state shape — operator-confirmed locked principle) | R-IS-01 |
| §10.2 (cost-attribution-per-span composes against the JSONL event ledger as per-event audit surface) | R-IS-02, R-IS-03 |
| §10.4 (compliance-readiness — hash-chained audit ledger foundational primitive) | R-IS-02, R-IS-03 |

### Scope and out-of-scope

| In scope | Out of scope |
|---|---|
| Specification-grade contract precision for R-IS-01 through R-IS-04 (signatures, schemas, formulas, enums, surface contracts) | New architectural commitments (Phase 3 territory; back-flow to ADR revision if surfaced) |
| Citation-by-section to PRD requirements + ADR commitments + ADD synthesis paragraphs | ADR revision; ADD revision; PRD revision |
| Persona-linkage trace preservation from PRD requirements | Cross-axis spec coherence beyond substrate seam exports (deferred to session 5 composition document per handoff §3.1) |
| Substrate seam exports surface (C-IS-10) for downstream-axis specs to consume by citation | Action-surface, control-plane, operational-discipline contracts (sessions 2–4) |
| §[carry-forwards] inheritance from PRD §[carry-forwards] | F2-12 closure (parallel `council-orchestrator` C7+C9 session territory; carry-forward only here) |
| Deferred-to-implementation discretion notation per Workflow §2.5.1 exit criteria language | Implementation-grade choices beyond specification surface (specific library bindings beyond ADR-declared, specific file paths beyond canonical-path declaration, specific provider candidates) |

---

## §1 C-IS-01 — Canonical filesystem path contract

**Contract surface.** Path-class enumeration with stability invariants and visibility surface.

**PRD requirement(s) satisfied.** R-IS-01 (files-as-artifacts at canonical filesystem paths).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (filesystem + git canonical state substrate; Skills, prompts, routing manifest, state-ledger all authored as files); ADD §2.2 Synthesis.

**Persona linkage.** Persona §5.1 (state lives on local filesystem + remote git); §7 (workflow-definition surface — both markdown-spec-driven and code-driven authoring); §10.1 (filesystem + git as canonical state shape — operator-confirmed locked principle).

**Specification content.**

Four canonical artifact classes reside on the filesystem; each class declares its path-residence contract:

| Class | Path-residence contract | Path-stability invariant | Visibility surface |
|---|---|---|---|
| Skills | SKILL.md-as-directory (folder-with-SKILL.md), one folder per skill; folder name is the skill identifier; SKILL.md frontmatter carries `name` + `description` (required) and `allowed-tools` + `disable-model-invocation` + `license` + `dependencies` (optional) per agentskills.io open standard ratified 18 Dec 2025 [HIGH — ADR-F2 v1.2 §Rationale (a)] | Folder identifier stable across runs of the same workflow; SKILL.md frontmatter schema stable across runs | Filesystem-readable to production-time operator during a run; filesystem-readable to downstream maintainer after termination |
| Prompts | Plain-text-file-in-git; one file per prompt artifact; prompts loaded as stable static-prefix content per Cluster 2 V2 §1.2 prompt-cache hierarchy [HIGH — ADR-F2 v1.2 §Rationale (b)(ii)] | File path stable across runs; file content cache-prefix-integrity-preserving | Filesystem-readable to production-time operator during a run; filesystem-readable to downstream maintainer after termination |
| Routing manifest | Single file in git per ADR-F1 v1.2 Consequences §(a) "manifest-layer model assignment as auditable default at every call site"; manifest declares per-agent-role + per-workflow-class + per-step model assignments | File path stable across runs (workflow-class-bound); manifest content immutable within a run | Filesystem-readable to production-time operator during a run; filesystem-readable to downstream maintainer after termination |
| State-ledger | Two-mode composite per C-IS-03 §3 (git commit stream as one mode; JSONL event ledger as second mode); JSONL ledger file at workflow-canonical path; commit stream at workflow-bound git repository | JSONL path stable across runs of the same workflow; git repository identity stable across runs of the same workflow | Filesystem-readable to production-time operator during a run; filesystem-readable to downstream maintainer after termination |

**Stability invariants.**

- A path identifier is **workflow-canonical** if it is stable across all runs of the same workflow class.
- A path identifier MAY vary across workflow classes; the contract does not commit to project-global canonical paths.
- A path identifier MAY vary across deployment surfaces per ADD §3 OD-2.A deployment-surface flex; canonical-path declaration commits only that *some* stable path exists per (workflow class, deployment surface) cell.

**Visibility surface contract.** All four artifact classes are filesystem-readable to (a) the production-time operator during a run via direct filesystem access on the host, and (b) the downstream maintainer after run termination via the durable filesystem persisting beyond run lifetime. No artifact class is held in-memory-only.

**Deferred to implementation discretion.** Specific canonical path strings per workflow class per deployment-surface cell (e.g., `.harness/skills/`, `harness/prompts/`, `routing.manifest.json` literal paths) are implementation-grade choices not committed by ADR substrate; binding occurs at implementation (Phase 6).

---

## §2 C-IS-02 — Artifact-tier layering schema

**Contract surface.** Five-tier model with tier-to-artifact-class mapping and tier composition contract.

**PRD requirement(s) satisfied.** R-IS-01 (files-as-artifacts at canonical filesystem paths; artifact-tier layering as the layering contract).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (artifact-tier layering composing working / episodic / semantic / procedural / durable); ADR-F2 v1.2 §Rationale (a) (P-IS-1 D-on-schema variation: ICM five-layer prescriptive, 12-Factor minimum-viable, Anthropic progress-file pattern as the loosest viable shape); ADD §2.2 Synthesis.

**Persona linkage.** Persona §5.1 (state lives on local filesystem + remote git); §10.1 (filesystem + git as canonical state shape — operator-confirmed locked principle).

**Specification content.**

The five-tier artifact layering schema commits the following layer enumeration:

| Tier | Semantic role | Substrate residence | Survives across |
|---|---|---|---|
| `working` | Per-run scratch state | Filesystem (run-bounded temporary paths) | A single inference call within a run |
| `episodic` | Per-run history; in-flight conversational state | Filesystem (run-bounded paths) | Multiple inference calls within a run; restart only via durable-execution engine replay |
| `semantic` | Cross-run knowledge artifacts; learned content | Filesystem + git (semantic-tier paths) | Run termination; carries forward into future runs |
| `procedural` | Workflow-class procedural artifacts (Skills, prompts, routing manifest) | Filesystem + git (procedural-tier paths) | Run termination + workflow versioning; carries forward across workflow versions |
| `durable` | Append-only state-ledger + JSONL event ledger + audit ledger | Filesystem + git (state-ledger paths per C-IS-05) | Run termination + restart + crash recovery; chain-integrity-verified per C-IS-06 |

**Tier composition contract.**

- **Substrate residence.** All durable-survival tiers (`semantic`, `procedural`, `durable`) reside on filesystem AND git per ADR-F2 §Decision combined-tier role; `working` and `episodic` tiers reside on filesystem only (no git) — consistent with the substrate-residence column of the five-tier table (see §2 lines 122–128).
- **Survival semantics.** Each tier's "survives across" property is a contract: artifacts at tier T are guaranteed to be readable at all future times within T's survival scope. `working` and `episodic` survival is run-bounded; `semantic`, `procedural`, and `durable` survival is durable across runs.
- **Cross-tier traceability.** Every `durable`-tier ledger entry references the `procedural`-tier artifacts in scope at the entry's write-time via the `action_id` field (per C-IS-05). This composition enables replay of the procedural-tier state at any prior durable-tier entry timestamp.

**Deferred to implementation discretion.** Specific filesystem path conventions per tier (e.g., `.harness/working/`, `.harness/episodic/`, `.harness/semantic/`); tier-internal subdivisions (e.g., per-workload-class subdirectories); cross-deployment-surface tier-residence overrides per ADD §3 OD-2.A flex.

---

## §3 C-IS-03 — Combined git tier role decomposition

**Contract surface.** Five-sub-role git tier composition with foundational-vs-opt-in posture per sub-role.

**PRD requirement(s) satisfied.** R-IS-02 (git as combined-tier state record).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (combined git tier serving five-sub-role composition); ADD §2.2 Synthesis ("Git serves a combined role: code/spec/prompt/manifest/Skill versioning (foundational) + append-only state-ledger via commit stream + JSONL event ledger (foundational) + on-demand shadow-Git checkpointing (workload-class-opt-in) + worktree-isolation for concurrent sub-agent reads (workload-class-opt-in)").

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit ledger as foundational primitive); §5.1 (remote git of GitHub/GitLab class); §10.2 (cost-attribution-per-span composes against the JSONL event ledger).

**Specification content.**

The combined git tier serves five sub-roles within a single git repository; each sub-role carries a posture commitment:

| Sub-role | Function | Posture | Composition contract |
|---|---|---|---|
| **Versioning** | Code/spec/prompt/manifest/Skill atomic versioning via git commit history | **Foundational** (always-on; no opt-out) | Composes with C-IS-04 atomic deploy contract |
| **State-ledger via commit stream** | Append-only state-ledger expressed as the git commit stream itself (commit hashes form a chain natively); workflow-canonical commit cadence per workflow class | **Foundational** (always-on; no opt-out) | Composes with JSONL event ledger sub-role; commit-stream-as-coarse-grain-ledger pairs with JSONL-as-fine-grain-ledger |
| **JSONL event ledger** | Per-event append-only JSONL file at workflow-canonical path (per C-IS-01); per-event records carry the canonical six-field entry shape (per C-IS-05); hash-chain integrity constructed per C-IS-06 | **Foundational** (always-on; no opt-out) | Composes with commit-stream sub-role and with C-IS-05 + C-IS-06 entry-shape + hash-chain commitments |
| **Shadow-Git checkpointing** | On-demand checkpoint snapshots via shadow-repository pattern (Cline / kilocode / Roo Code precedent per ADR-F2 §Rationale (a)) | **Workload-class-opt-in** (per workflow manifest declaration per C-IS-08) | Composes with C-IS-08 contract; opt-out workloads do not produce shadow-Git artifacts |
| **Worktree-isolation for concurrent sub-agent reads** | Per-sub-agent worktree directories via `git worktree` primitives; isolates concurrent reads from sibling sub-agents | **Workload-class-opt-in** (per workflow manifest declaration per C-IS-09) | Composes with C-IS-09 contract; opt-out workloads do not allocate worktree directories |

**Sub-role co-residence contract.** All five sub-roles share the same git repository identity without interference:

- Versioning operates on the main repository's branch heads.
- State-ledger via commit stream operates on the main branch's commit history; commit messages MAY encode state-ledger-relevant metadata.
- JSONL event ledger is a file artifact tracked in git (versioned via the versioning sub-role); appends to the file produce diff-traceable commits.
- Shadow-Git checkpointing operates via separate shadow refs/branches; does not pollute the main branch commit history.
- Worktree-isolation creates per-sub-agent working directories pointing at the same `.git` storage backend; reads do not contest with one another.

**Cross-sub-role consistency invariant.** A given git repository hosts at most one harness state-ledger; the five sub-roles share that ledger. Cross-repository state-ledger composition is out of scope at F2 substrate layer; per-tenant repository isolation at multi-tenant binding is the F2-compatible scaling shape per ADR-F2 §Consequences (a).

**Deferred to implementation discretion.** Specific commit cadence policy per workflow class; specific commit message conventions for state-ledger-relevant metadata; specific shadow-ref / shadow-branch naming conventions; specific worktree directory naming conventions; specific git hosting backend (GitHub / GitLab / Gitea / self-hosted) per deployment-surface cell.

---

## §4 C-IS-04 — Atomic prompt + code + eval + manifest deploy contract

**Contract surface.** Atomicity contract over the prompt + code + eval + manifest deploy unit.

**PRD requirement(s) satisfied.** R-IS-02 (git log inspection reveals atomic prompt+code+eval+manifest deploys).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Consequences (a) ("Prompts-as-files in git, atomically deployed alongside code and evals (Cluster 2 V2 §3.4.1 [HIGH])"; "Eval-set residence in git enables atomic prompt+code+eval deploys"); ADD §2.2 Synthesis.

**Persona linkage.** Persona §5.1 (state lives on local filesystem + remote git); §7 (pragmatic-mixed ecosystem affinity — git-as-deploy-substrate compatible with all language ecosystems).

**Specification content.**

The deploy unit consists of four co-located artifact classes:

- **Prompts** — plain-text prompt files per C-IS-01.
- **Code** — workflow implementation code (Python-first per Persona §7).
- **Eval-sets** — eval-set artifacts (eval inputs, expected outputs, eval scripts) co-located with the code they evaluate.
- **Routing manifest** — per ADR-F1 v1.2 Consequences §(a) manifest-layer model assignment.

**Atomicity contract.**

A "deploy" event is the application of a single git commit (or atomic commit-group via merge commit / tagged release) that updates one or more of the four artifact classes. The atomicity property commits:

| Property | Contract |
|---|---|
| **All-or-nothing per commit** | A commit either applies all its prompt + code + eval + manifest changes or applies none of them; partial application is precluded by git's commit atomicity at the storage layer |
| **Single-version observability** | The downstream maintainer inspecting any single git commit observes a coherent snapshot of all four artifact classes at that commit's revision |
| **Composition with C-IS-03 commit-stream sub-role** | Every deploy commit is itself a state-ledger entry at the commit-stream sub-role (per C-IS-03); the commit's message metadata MAY tag the deploy as a release |
| **Composition with C-IS-08 shadow-Git checkpointing** | Shadow-Git checkpoints (per C-IS-08) are orthogonal to deploys; checkpoint cadence and deploy cadence are independent commitments |

**Verification surface.** Git log inspection at any commit reveals the prompt + code + eval + manifest revision active at that commit; bisection across the commit history isolates regression boundaries per atomic deploy unit.

**Deferred to implementation discretion.** Specific deploy tagging conventions; specific eval-set file format (JSON / YAML / JSONL); specific commit-message-driven deploy-event annotation conventions.

---

## §5 C-IS-05 — State-ledger entry shape signature

**Contract surface.** Six-field record type with per-field type/format/semantic precision.

**PRD requirement(s) satisfied.** R-IS-03 (state-ledger entry shape with hash-chain integrity — entry shape half).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (state-ledger entry shape); ADD §2.2 Synthesis ("the state-ledger entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)` becomes the harness-canonical substrate").

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit foundational primitive); §10.2 (cost-attribution-per-span composes against the JSONL event ledger as the per-event audit surface).

**Specification content.**

The state-ledger entry record is a six-field tuple with the following per-field specification:

| Field | Type / format | Semantic | Constraint |
|---|---|---|---|
| `action_id` | Identifier — unique per action occurrence | Identifies the action this entry records | Unique within the ledger; harness-generated; MAY encode action class / sub-class metadata |
| `idempotency_key` | Identifier — stable per logical operation | Harness-canonical join key per ADD §2.2 Synthesis | Stable across retry attempts of the same logical operation; the join key for cross-axis composition (engine event history at D1, audit-ledger signing at D5, sandbox-violation events at D2, span emission at D6) per ADD §2.2 closing sentence |
| `actor` | Identifier — agent / sub-agent / operator | Identifies the entity that originated the action | Drawn from the active workflow's actor namespace |
| `response_hash` | Bytes — SHA-256 digest | Hash of the canonical-JSON byte representation of the entry's payload content | Per-entry hash discipline per C-IS-06 |
| `timestamp` | Timestamp — monotonic ordering | The wall-clock instant the entry was written | Monotonically non-decreasing within a ledger (subject to clock-skew tolerance documented at implementation) |
| `prior_event_hash` | Bytes — SHA-256 digest OR all-zeros sentinel | The SHA-256 of the canonical-JSON byte representation of the prior entry; all-zeros sentinel for chain-inception entries | Chain-construction discipline per C-IS-06 |

**Field-shape extensibility commitment.** Per ADR-F2 §Rationale (a.1) "The *specific* canonicalization library binding ... and any per-workload-class extensions to the entry shape are D-derivative downstream per Consequences §(c)." The six-field shape above is the **F-layer minimum**; per-workload-class extensions are D-derivative.

**Composition with cross-axis seams.**

- D1 v1.1 engine event history joins on `idempotency_key` per ADD §3.1.1 + ADR-D1 v1.1.
- D5 v1.3 audit-ledger entries inherit the entry shape and add `audit.*` attribute namespace per ADR-D5 v1.3 §1.4 + §1.4.1.
- D2 v1.1 sandbox-violation events join on `idempotency_key` per ADR-D2 v1.1 §1.8.
- D6 v1.1 cost-attribution-per-span joins on `idempotency_key` per ADR-D6 v1.1 §1.5.

These cross-axis joins are documented at C-IS-10 (substrate seam exports surface).

**Deferred to implementation discretion.** Specific identifier format for `action_id` (UUID v4 / ULID / monotonic-counter); specific format for `idempotency_key` (Stripe-style hex string / UUID / structured); specific timestamp format (ISO 8601 / RFC 3339 / Unix-epoch nanoseconds); per-workload-class extensions to the six-field shape (D-derivative per ADR-F2 §Consequences (c)).

---

## §6 C-IS-06 — Hash-chain integrity construction discipline

**Contract surface.** Construction-time discipline + verification-time procedure + tamper-evidence contract.

**PRD requirement(s) satisfied.** R-IS-03 (state-ledger entry shape with hash-chain integrity — hash-chain integrity half).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Rationale (a.1) "Hash-chain integrity construction as F-layer commitment" (full sub-section); ADD §2.2 Synthesis.

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit foundational primitive); §10.2 (cost-attribution-per-span composes against the JSONL event ledger as per-event audit surface).

**Specification content.**

Hash-chain integrity is constructed **at write-time** via the following four-step discipline (per ADR-F2 §Rationale (a.1)):

### §6.1 Per-entry canonicalization

**Signature.** `canonicalize(entry: StateLedgerEntry) -> bytes`

**Discipline.** Each state-ledger entry is canonicalized to a deterministic byte representation prior to hashing. RFC 8785 JSON Canonicalization Scheme (JCS) is the corpus-converged baseline candidate **[MODERATE — per ADR-F2 §Rationale (a.1), library binding to be confirmed at the D-ADR on canonicalization library per language ecosystem]**.

**Contract.** Canonicalization is deterministic — given the same logical entry, two canonicalizations on different runs / machines / library versions of the same canonicalization scheme produce identical byte sequences. Non-determinism in canonicalization is a contract violation.

### §6.2 Per-entry hash computation

**Signature.** `response_hash = SHA-256(canonicalize(entry))`

**Discipline.** The SHA-256 digest of the canonical-JSON byte representation produces the entry's `response_hash` field (per C-IS-05).

**Contract.** SHA-256 is the committed hash function at the F-layer; alternative hash functions are precluded at F2 substrate. The 256-bit digest output is the contract surface.

### §6.3 Chain construction at write-time

**Signature.** For entry N (1-indexed):
- If N = 1 (chain inception): `entry[N].prior_event_hash = ALL_ZEROS_SENTINEL` (32 bytes of zero)
- If N > 1: `entry[N].prior_event_hash = SHA-256(canonicalize(entry[N-1]))`

**Discipline.** The `prior_event_hash` field of entry N references the SHA-256 of entry N−1's canonical-JSON byte representation. Chain-inception entries reference the all-zeros sentinel hash.

**Contract.** The chain is constructed **at write-time** — entries cannot be written without `prior_event_hash` being computed against the prior entry. Concurrent-writer contention on the chain head is precluded by the C3-pole write contract (per C-IS-07).

### §6.4 Chain verification on demand

**Signature.** `verify_chain(ledger: List[StateLedgerEntry]) -> ChainVerificationResult`

**Discipline.** Chain integrity is verified by:
1. For each entry N in the ledger, re-canonicalize entry N to produce `canonical_bytes[N] = canonicalize(entry[N])`.
2. Re-compute `computed_hash[N] = SHA-256(canonical_bytes[N])`.
3. Verify that `entry[N+1].prior_event_hash == computed_hash[N]` for every N from 1 to len(ledger) − 1.
4. Verify that `entry[1].prior_event_hash == ALL_ZEROS_SENTINEL`.

**Contract.** Tamper-evidence is the verification's failure mode at any chain position — if any entry has been modified, the chain verification at the modified position (or any position downstream of it) fails. The verification surface is end-to-end inspectable by the downstream maintainer per R-IS-03 acceptance criterion.

### §6.5 Tamper-evidence contract

| Tamper scenario | Verification outcome |
|---|---|
| Entry-content modification (any field except `prior_event_hash`) | `computed_hash[N]` recomputes differently from `entry[N+1].prior_event_hash` → verification fails at position N+1 |
| `prior_event_hash` modification | Verification fails at the modified entry (its `prior_event_hash` no longer matches `computed_hash` of the prior entry) |
| Entry deletion (mid-chain) | Verification fails at the deletion position; the "new" entry at that position's `prior_event_hash` references a now-absent prior |
| Entry insertion (mid-chain) | Verification fails at the next downstream entry; the inserted entry's `prior_event_hash` either matches the wrong entry or fails the chain construction check |
| Chain-inception modification | Verification fails at entry 1 (`prior_event_hash` no longer equals the all-zeros sentinel) |

**Deferred to implementation discretion.** Specific canonicalization library binding per language ecosystem (RFC 8785 JCS reference implementation per Python / Go / Rust / TypeScript — D-derivative per ADR-F2 §Consequences (c)); specific SHA-256 implementation binding (language-stdlib / cryptography-library); specific verification-procedure performance optimizations (batch-verification / lazy-verification / streaming-verification).

---

## §7 C-IS-07 — State-ledger read/write contract pair (T-perm-2 F2-layer resolution)

**Contract surface.** Read/write contract pair at the state-ledger seam expressing T-perm-2 (C2 ↔ C3 — within-turn vs across-turn) F2-layer resolution shape.

**PRD requirement(s) satisfied.** R-IS-02 (JSONL event ledger) + R-IS-03 (state-ledger entry shape with hash-chain integrity — composition discipline).

**ADR commitment(s) honored.** ADR-F2 v1.2 §"Permanent tensions engaged" (T-perm-2 F2-layer resolution shape: read/write contract pair); ADR-F2 v1.2 §Consequences (c) "D-ADR on ledger entry schema fields and canonicalization library binding" (full sub-section on C3 write contract + C2 read contract composition); ADD §5.2.2 T-perm-2 F2-layer resolution.

**Persona linkage.** Persona §10.4 (compliance-readiness foundational primitive — hash-chained audit ledger); §10.2 (cost-attribution-per-span composes against the JSONL event ledger as per-event audit surface).

**Specification content.**

T-perm-2 (C2 ↔ C3 — within-turn vs across-turn) is **structurally permanent** per ADD §5.2.2; F2-layer resolution shape is a **read/write contract pair** at the state-ledger seam.

### §7.1 C3-pole write contract

| Property | Contract |
|---|---|
| **Append-only** | Writes to the state-ledger append new entries; existing entries are immutable post-write |
| **Structured** | Every entry conforms to the six-field shape per C-IS-05 |
| **JSON-not-Markdown** | Structured entry fields are JSON-encoded; Markdown-only representation is precluded per ADR-F2 §Rationale (b)(iii) Anthropic Nov 26 2025 guidance [HIGH] |
| **Idempotent** | Writes are keyed on `(thread_id, step_id, idempotency_key)` per Stripe-style convention per ADR-F2 §Consequences (c); a second write with the same key is a no-op against the existing entry |
| **Per-event JSONL with stable indexable shape** | The on-disk representation is JSONL (one entry per line); the line-per-entry structure enables indexable access without parsing the entire ledger |
| **Hash-chain-integrity-preserving** | Every write computes `response_hash` and `prior_event_hash` per C-IS-06 before persisting the entry |

### §7.2 C2-pole read contract

| Property | Contract |
|---|---|
| **Selective** | Reads target specific entries or entry-ranges; full-ledger reads are precluded as the default read mode |
| **Bounded** | Reads at session start consume a bounded window of recent entries; bounding policy is workload-class-tunable |
| **Navigation-primitive-mediated** | Reads occur via navigation primitives exposed as Skills or in-process tools (per ADR-F2 §Consequences (c)); direct full-file `cat`-style reads are precluded for the read contract |
| **Read-into-dynamic-suffix** | Read content enters the model's dynamic suffix (not the static prefix); prompt-cache integrity is preserved by construction (per ADR-F2 §Rationale (b)(ii) cache-prefix detonation prevention) |

### §7.3 Composition format

**Composition format.** JSONL with stable indexable per-event shape per ADR-F2 §"Permanent tensions engaged".

The composition contract commits:

- **Storage representation** — JSONL file (one JSON-serialized entry per line) at workflow-canonical path per C-IS-01.
- **Per-entry shape** — six-field record per C-IS-05.
- **Indexable access** — line-per-entry structure permits offset-based indexing; navigation primitives exposed as Skills or in-process tools per the C2-pole read contract.
- **Concurrent access** — the C3-pole append-only write contract serializes writers; the C2-pole selective read contract permits concurrent readers.

### §7.4 Multi-seam T-perm-2 engagement (cross-axis context)

T-perm-2 is engaged at **three seams** per ADD §5.2.2:

| Seam | F-layer resolution | Cross-axis specification reference |
|---|---|---|
| State-ledger seam | F2-layer (this contract C-IS-07) | This specification |
| Secrets-in-sandbox-environment seam | F5-layer closure (tier-aware composition with F4 tier-set) | Action Surface specification (session 2) |
| OTLP collector boundary seam | D6-layer commitment (within-turn streaming + across-turn durable trace storage) | Operational Discipline specification (session 4) |

D-layer adjacency engagements at D1 (engine event history Tier-3 vs F2 state-ledger Tier-5 join on `idempotency_key`), D3 (Skills loading discipline vs filesystem residence), D4 (HandoffContext serialization), D5 (HITL pause-resume context revalidation), D6 (OTLP collector boundary) compose against this F2-layer contract without altering it (per ADD §5.2.2 D-layer adjacency rules).

**Deferred to implementation discretion.** Specific navigation primitive APIs (`read_entry(id)`, `read_range(start, end)`, `read_recent(n)`, `read_by_idempotency_key(key)` etc.); specific bounding-window-size defaults per workload class; specific concurrent-writer serialization mechanism (advisory lock / per-line flock / lease coordination); **the relationship between the C-IS-07 §7.1 idempotent-write keying tuple `(thread_id, step_id, idempotency_key)` and the C-IS-05 six-field entry shape `(action_id, idempotency_key, actor, response_hash, timestamp, prior_event_hash)`** — specifically, whether `thread_id` and `step_id` are (i) embedded within `action_id`'s encoded metadata, (ii) implicit in run-context that scopes `idempotency_key` uniqueness, (iii) supplied as separate write-arguments not persisted as entry fields, or (iv) per-workload-class extension fields — is deferred to the downstream D-ADR on ledger schema per ADR-F2 §Consequences (c) "defers the relationship reconciliation to the D-ADR on ledger schema fields"; F2-12 active engagement (parallel `council-orchestrator` C7+C9 session per ADD §6.3.1 + PRD §[carry-forwards] [CF-1]) is the open downstream resolution path.

---

## §8 C-IS-08 — Workload-class-opt-in shadow-Git checkpoint contract

**Contract surface.** Manifest declaration shape + checkpoint cadence parameter + reversal granularity contract.

**PRD requirement(s) satisfied.** R-IS-04 (workload-class-opt-in shadow-Git checkpoint and worktree isolation — shadow-Git half).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (on-demand shadow-Git checkpointing workload-class-opt-in); ADR-F2 v1.2 §Consequences (a) "Shadow-Git checkpointing as a workload-class-opt-in primitive (P-OD-4)"; ADD §2.2 Synthesis.

**Persona linkage.** Persona §3.1.1 (software engineering — F2 leverage maximal); §8.1 (software-engineering action surface — code execution + filesystem + git as primary).

**Specification content.**

### §8.1 Opt-in declaration shape

A workflow opts into shadow-Git checkpointing via its workflow manifest. The opt-in declaration shape commits:

| Field | Type | Semantic |
|---|---|---|
| `shadow_git_enabled` | Boolean | `true` ⇒ workflow produces shadow-Git checkpoint snapshots; `false` (default) ⇒ no shadow-Git artifacts |
| `shadow_git_cadence` | Enum / structured | Checkpoint cadence policy per §8.2 below; required when `shadow_git_enabled = true` |

### §8.2 Checkpoint cadence parameter

Checkpoint cadence is **workload-class-tunable** per ADR-F2 §Rationale (a) (workload-class-shaped fine-grained reversal). Cadence enumeration:

| Cadence value | Trigger semantic |
|---|---|
| `per_step` | Snapshot after every step boundary (highest granularity; corpus precedent: Cline's per-step pattern per ADR-F2 §Rationale (a)) |
| `per_tool_call` | Snapshot after every tool invocation that mutates filesystem state |
| `per_significant_change` | Snapshot triggered by workflow-defined "significant change" predicate (workload-class-shaped) |
| `per_explicit_marker` | Snapshot only when workflow explicitly invokes a `checkpoint()` marker |

**Cadence selection rule.** Persona §3.1.1 (software engineering — F2 leverage maximal) implies `per_step` or `per_tool_call` cadence as the default for software-engineering workloads where reversal granularity is high-value. Persona §3.1.3 (pipeline automation — durability tier mandatory) implies `per_explicit_marker` cadence as the default for hours-long-step pipeline workloads where per-step cadence inflates repo size without proportional reliability gain (per ADR-F2 §Rationale (a) Alternative 3 rejection).

### §8.3 Reversal granularity contract

A shadow-Git checkpoint is **rollback-targetable** — the harness can restore the workflow's filesystem state to the snapshot's contents. Rollback semantics:

- **Atomic** — rollback applies the checkpoint's state in full or not at all (per shadow-Git's git-native atomicity).
- **Filesystem-bounded** — rollback restores filesystem state under the workflow's tracked paths; rollback does NOT restore the state-ledger (the ledger is append-only per C-IS-07; rollback writes a new entry recording the rollback event).
- **Workflow-state-coherent** — after rollback, the workflow's filesystem state matches the checkpoint's recorded state; in-flight inference state is not restored (per C2-pole within-turn boundary).

### §8.4 Composition with C-IS-03 sub-roles

Shadow-Git checkpointing is implemented via **shadow refs / shadow branches** within the same git repository as the versioning + commit-stream-state-ledger sub-roles (per C-IS-03 sub-role co-residence contract). Shadow-Git artifacts do **not** pollute the main branch commit history; downstream maintainers inspecting the main branch see deploys + state-ledger commits, not per-step checkpoints.

**Deferred to implementation discretion.** Specific shadow-ref naming convention (`refs/shadow/<workflow-id>/<checkpoint-id>` or alternative); specific snapshot retention policy (keep-all / keep-last-N / age-bounded); specific rollback API surface; specific cadence-policy authoring schema in workflow manifest (YAML / JSON / TOML).

---

## §9 C-IS-09 — Workload-class-opt-in worktree-isolation contract

**Contract surface.** Manifest declaration shape + per-sub-agent worktree directory contract + concurrent-read isolation invariant.

**PRD requirement(s) satisfied.** R-IS-04 (workload-class-opt-in shadow-Git checkpoint and worktree isolation — worktree-isolation half).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (worktree-isolation for concurrent sub-agent reads workload-class-opt-in); ADR-F2 v1.2 §Consequences (a) "Worktree-isolation for the concurrent-sub-agent-read subset that fans out reads while preserving Cognition's single-threaded-write convergence"; ADD §2.2 Synthesis.

**Persona linkage.** Persona §3.1.1 (software engineering — F2 leverage maximal); §3.1.3 (pipeline automation — durability tier mandatory); §8.1 (software-engineering action surface).

**Specification content.**

### §9.1 Opt-in declaration shape

A workflow opts into worktree-isolation via its workflow manifest:

| Field | Type | Semantic |
|---|---|---|
| `worktree_isolation_enabled` | Boolean | `true` ⇒ sub-agent fan-out allocates per-sub-agent worktree directories; `false` (default) ⇒ no worktree allocation |
| `worktree_concurrency_cap` | Integer (optional) | Maximum concurrent sub-agent worktrees per workflow run; default unbounded (subject to filesystem capacity); per ADR-D4 v1.1 fan-out cap composition (cross-axis reference) |

### §9.2 Per-sub-agent worktree directory contract

When `worktree_isolation_enabled = true`, sub-agent fan-out (per ADR-D4 v1.1 orchestrator-workers / decentralized-handoff / hierarchical-delegation patterns) triggers per-sub-agent worktree allocation:

| Property | Contract |
|---|---|
| **Per-sub-agent worktree** | Each fanned-out sub-agent receives an isolated worktree directory pointing at the same `.git` storage backend as the parent workflow |
| **Worktree identity** | Worktree identifier is harness-generated; stable for the lifetime of the sub-agent |
| **Worktree termination** | Worktree directory is reclaimed at sub-agent termination (success or failure); **reclamation** = `git worktree remove` invocation + directory contents removal, triggered at an operator-policy-controlled lifecycle-marker boundary; reclamation MUST NOT delete the underlying `.git` storage backend |

### §9.3 Concurrent-read isolation invariant

| Invariant | Contract |
|---|---|
| **Read-read non-interference** | Concurrent sub-agents reading the same artifact via their respective worktrees do not block one another |
| **Read-write non-interference within worktree** | Sub-agent reads within its worktree are isolated from concurrent writes occurring in sibling worktrees (per `git worktree` semantics) |
| **Cross-worktree writer serialization** | Concurrent writes across sibling worktrees against the same `.git` storage backend are serialized per Cognition single-threaded-write convergence (per ADR-F2 §Consequences (a) reference to Brainstorm synthesis §1) |
| **Composition with sub-agent boundary** | Worktree-isolation composes with ADR-D4 v1.1 §1.5 sub-agent privilege inheritance + ADR-D2 v1.1 §1.4 sub-agent sandbox-tier monotonicity + ADR-D5 v1.3 §1.5.2 cross-deployment monotonicity per ADD §5.3.2 sub-agent boundary as monotonic-only descent (cross-axis composition — Action Surface + Control Plane specs detail downstream) |

### §9.4 Multi-writer scaling boundary

Multi-writer scaling beyond worktree-isolation requires a downstream D-ADR on coordination shape per ADR-F2 §Consequences (b) "Concurrent writes to substrate." Worktree-isolation is the F2-compatible scaling shape for the design-time persona; multi-tenant scaling at the bridging-arc binding adopts per-tenant repo isolation as the F2-compatible scaling shape per ADR-F2 §Consequences (a) "Per-tenant repo isolation as a clean F2-compatible scaling pattern at the bridging-arc multi-tenant binding (kilocode-style)".

**Deferred to implementation discretion.** Specific worktree directory location convention (`.worktrees/<sub-agent-id>/` or alternative); specific worktree-allocation API surface; specific cross-worktree writer-serialization mechanism (advisory lock / leader-election / single-threaded-write enforcer); specific worktree reclamation cleanup policy.

---

## §10 C-IS-10 — Substrate seam exports surface (cross-axis composition)

**Contract surface.** Substrate seams that F2 exports for downstream-axis specifications to consume by citation.

**PRD requirement(s) satisfied.** R-IS-01 (canonical filesystem paths) + R-IS-02 (combined git tier) + R-IS-03 (state-ledger entry shape with hash-chain integrity) — cross-axis composition surface.

**ADR commitment(s) honored.** ADR-F2 v1.2 §Consequences (c) (full enumeration of eleven downstream surfaces); ADD §2.2 Synthesis (state-ledger entry shape as "the harness-canonical substrate against which every downstream action composes"); ADD §5.2.2 T-perm-2 F2-layer resolution.

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit ledger as foundational primitive); §10.2 (cost-attribution-per-span composes against the JSONL event ledger).

**Specification content.**

The Information Substrate axis exports the following seams for cross-axis specifications (sessions 2–4 + session 5 composition document) to compose against by citation. Each seam declares (i) the export surface, (ii) the consuming axis/axes, (iii) the cross-axis composition reference.

### §10.1 State-ledger entry shape export

**Export surface.** Six-field record per C-IS-05.

**Consuming axes.**

| Consuming axis | Composition reference | Cross-spec citation target |
|---|---|---|
| Control Plane (D1 v1.1 engine event history) | Engine event history joins on `idempotency_key`; engine ledger is Tier-3 durability; F2 state-ledger is Tier-5 durability; the two ledgers compose at the join (per ADR-F3 v1.1 §Consequences (a) + ADR-D1 v1.1) | `Spec_Control_Plane_v1.md` C-CP-* on `idempotency_key` join |
| Operational Discipline (D5 v1.3 audit-ledger cryptographic shape) | Audit-ledger entries inherit the entry shape and add `audit.*` attribute namespace per persona-tier cryptographic shape (solo / team / multi-tenant) per ADR-D5 v1.3 §1.4 + §1.4.1 | `Spec_Operational_Discipline_v1.md` C-OD-* on audit-ledger composition |
| Action Surface (D2 v1.1 sandbox-violation events) | Sandbox-violation events join on `idempotency_key` per ADR-D2 v1.1 §1.8 fail-class taxonomy | `Spec_Action_Surface_v1.md` C-AS-* on sandbox-violation event shape |
| Operational Discipline (D6 v1.1 cost-attribution-per-span) | `cost.*` per-span attribution joins on `idempotency_key` to avoid double-counting on replay per ADR-D6 v1.1 §1.5 | `Spec_Operational_Discipline_v1.md` C-OD-* on cost-attribution |

### §10.2 Idempotency-key join export

**Export surface.** `idempotency_key` field per C-IS-05; harness-canonical join key per ADD §2.2 Synthesis closing sentence.

**Consuming axes.** All three downstream axes consume `idempotency_key` as the cross-axis join key for replay-safe composition (per ADD §2.2 closing sentence "engine event history (when adopted at D1), audit-ledger signing (D5), and sandbox-violation events (D2) all join on `idempotency_key`").

**F2-12 carry-forward note.** The replay-trace-emission contract (D1 v1.1 → v1.2) is deferred per ADD §6.3.1 + PRD §[carry-forwards] [CF-1]; specifically, the span re-emission semantics under engine replay, `retry.attempt` sibling-span discipline, and trace-ingestion dedup composition with F2 `idempotency_key` remain open until D1 v1.2 + D6 v1.2 land. This carries forward to this spec's §[carry-forwards].

### §10.3 Hash-chain construction discipline export

**Export surface.** Canonicalize → SHA-256 → prior-event-hash chaining per C-IS-06.

**Consuming axes.**

| Consuming axis | Composition reference |
|---|---|
| Operational Discipline (D5 v1.3 audit-ledger) | Audit-ledger uses the F2 hash-chain construction at team-binding+ persona tiers per ADR-D5 v1.3 §1.4 + §1.4.1 |
| Operational Discipline (D5 v1.3 audit signing extension) | Multi-tenant-compliance persona tier extends hash-chain with cryptographic signature (`audit.signature.value` + `audit.signature.algorithm` + `audit.signature.key_id` + `audit.signature.key_period`) per ADR-D5 v1.3 §1.4 |

### §10.4 Filesystem path contract export

**Export surface.** Canonical filesystem path classes per C-IS-01.

**Consuming axes.**

| Consuming axis | Composition reference |
|---|---|
| Action Surface (D3 v1.2 Skills loading discipline) | Skills-as-files load from filesystem per cache-prefix integrity discipline per ADR-D3 v1.2 |
| Control Plane (F1 v1.2 routing manifest residence) | Routing manifest resides at canonical filesystem path per ADR-F1 v1.2 Consequences §(a) |

### §10.5 JSONL event ledger format export

**Export surface.** JSONL with stable indexable per-event shape per C-IS-07 §7.3 composition format.

**Consuming axes.**

| Consuming axis | Composition reference |
|---|---|
| Operational Discipline (D6 v1.1 OTLP collector boundary) | OTLP collector boundary composes against the F2 JSONL event ledger at within-turn streaming + across-turn durable trace storage per ADR-D6 v1.1 §1.7 (T-perm-2 D6-layer commitment per ADD §5.2.2) |

### §10.6 Workload-class-opt-in shadow-Git + worktree-isolation export

**Export surface.** Manifest declaration shapes per C-IS-08 + C-IS-09.

**Consuming axes.**

| Consuming axis | Composition reference |
|---|---|
| Control Plane (D4 v1.1 sub-agent fan-out) | Worktree-isolation composes with D4 sub-agent privilege inheritance + sandbox-tier monotonicity + cross-deployment monotonicity per ADD §5.3.2 sub-agent boundary as monotonic-only descent |
| Control Plane (D5 v1.3 cross-deployment monotonicity) | Shadow-Git checkpoint cadence engages T-perm-3 at the shadow-Git checkpoint cadence vs retry-mechanics seam per ADR-F2 §"Permanent tensions engaged" T-perm-3 touch + ADD §5.2.3 residual surface |

**Deferred to implementation discretion.** Specific cross-spec citation strings (resolved at sessions 2–4 + session 5 composition document); specific seam-versioning convention if F2 ever revises (out of scope at v1).

---

## §[carry-forwards]

This meta-section documents PRD-inherited carry-forward items per `Phase_5_Session_1_Session_Prompt.md` §5.4. Entries are **documentation, not contract-bearing** — they do not engage the §[coherence pass] §6.1 per-contract audit; they engage the spec's operator-visibility surface.

### [CF-1] F2-12 — D1 v1.1 → v1.2 replay-trace-emission contract

**Status.** 🔄 Deferred-acknowledged at ADD v1.2 §6.3.1 (inherited at PRD v1.0 §[carry-forwards] [CF-1]; inherited at this spec); not blocking session 1 entry; not blocking session 1 filing.

**Scope.** D1 v1.1 → v1.2 replay-trace-emission contract covering: (i) span re-emission semantics under engine replay (event-sourced-replay engines: do spans re-emit, or is replay a deterministic re-read without new span emission?); (ii) `retry.attempt` sibling-span discipline (does the retry emit `retry.attempt` event AND a new sibling span per D6 §1.2?); (iii) trace-ingestion dedup composition with F2 `idempotency_key` (cost-attribution-per-span at D6 §1.5 must avoid double-counting on replay).

**Information Substrate spec impact.** The F2 `idempotency_key` export per C-IS-10 §10.2 is the harness-canonical join key; replay-trace-emission semantics that consume this join key are downstream-axis contracts (Control Plane and Operational Discipline). C-IS-10 §10.2 includes the F2-12 carry-forward note in line. **No Information Substrate contract is open** as a function of F2-12 — the F2 substrate surface (entry shape, hash-chain construction, idempotency-key export) is fully closed at v1.0 of this spec.

**Forward routing.** Parallel `council-orchestrator` C7+C9 session at operator discretion per ADD §6.3.1 active path. Closure expected as D1 v1.2 + D6 v1.2; absorbed into ADD v1.3; PRD revision pass produces `PRD_v1.1.md`; Phase 5 revision-pass at affected spec sections (Control Plane spec + Operational Discipline spec); Information Substrate spec is NOT a revision target for F2-12 closure.

### [CF-2] Workflow §7 substrate-skill propagation

**Status.** Open operator decision; outside P3-CK closure scope; outside PRD scope; outside Phase 5 scope.

**Origin.** `Project_Workflow_Revision_log.md` v1.4 entry line 297 footnote — `add-consolidation-protocol.md` §3.5 Step 5 substrate-skill update to reference Workflow v1.4 §2.3.5 clause (iv) is a separate skill-substrate revision not in v1.4 scope.

**Information Substrate spec impact.** Not in spec scope (skill-substrate revision is neither architectural commitment nor observable behavior nor specification-grade contract). Documented here for operator-visibility per inheritance from PRD §[carry-forwards] [CF-2].

**Forward routing.** Operator decision at discretion. No specification revision is triggered by skill-substrate propagation.

---

## §[traceability]

PRD-requirement-to-spec-contract sub-matrix for the Information Substrate axis. Rows = 4 PRD requirements; columns = 10 spec contracts. `✓` indicates the contract satisfies the requirement (≥1 contract surface implements the requirement's observable behavior).

| PRD requirement | C-IS-01 | C-IS-02 | C-IS-03 | C-IS-04 | C-IS-05 | C-IS-06 | C-IS-07 | C-IS-08 | C-IS-09 | C-IS-10 |
|---|---|---|---|---|---|---|---|---|---|---|
| R-IS-01 — Files-as-artifacts at canonical filesystem paths | ✓ | ✓ |  |  |  |  |  |  |  | ✓ |
| R-IS-02 — Git as combined-tier state record |  |  | ✓ | ✓ |  |  | ✓ |  |  | ✓ |
| R-IS-03 — State-ledger entry shape with hash-chain integrity |  |  |  |  | ✓ | ✓ | ✓ |  |  | ✓ |
| R-IS-04 — Workload-class-opt-in shadow-Git checkpoint and worktree isolation |  |  |  |  |  |  |  | ✓ | ✓ |  |

**Bidirectional verification.**

| Verification rule | Result |
|---|---|
| Every PRD requirement has ≥1 spec contract satisfying it | ✅ — R-IS-01 (3 contracts); R-IS-02 (4 contracts); R-IS-03 (4 contracts); R-IS-04 (2 contracts) |
| Every spec contract has ≥1 PRD requirement it satisfies | ✅ — C-IS-01 (R-IS-01); C-IS-02 (R-IS-01); C-IS-03 (R-IS-02); C-IS-04 (R-IS-02); C-IS-05 (R-IS-03); C-IS-06 (R-IS-03); C-IS-07 (R-IS-02 + R-IS-03); C-IS-08 (R-IS-04); C-IS-09 (R-IS-04); C-IS-10 (R-IS-01 + R-IS-02 + R-IS-03) |
| 4 PRD requirements present (axis-in-scope) | ✅ — R-IS-01, R-IS-02, R-IS-03, R-IS-04 |
| 10 spec contracts present | ✅ — C-IS-01 through C-IS-10 |
| ADR substrate cited at substrate version | ✅ — ADR-F2 v1.2 cited per `Phase_5_Entry_Handoff.md` §5 substrate version |

**Sub-matrix verification: PASS (5/5 rules).**

---

## §[coherence pass]

Pre-emission self-audit per `Phase_5_Session_1_Session_Prompt.md` §6. Five audit dimensions; spec does not file unless all five return ✅ PASS.

### Audit 6.1 — Per-contract audit (10 contracts × 7 sub-dimensions)

| Sub-dimension | Verification posture | Result |
|---|---|---|
| PRD requirement trace | Every spec contract cites ≥1 PRD R-ID; cited requirement is in session-1 axis scope (R-IS-01 through R-IS-04) | ✅ PASS — spot-check: C-IS-01 cites R-IS-01; C-IS-05 cites R-IS-03; C-IS-07 cites R-IS-02 + R-IS-03; C-IS-10 cites R-IS-01 + R-IS-02 + R-IS-03. 10 of 10 contracts carry PRD requirement citations |
| ADR commitment trace | Every spec contract cites ≥1 ADR by ID **and** section (per inversion-discipline analog) | ✅ PASS — spot-check: C-IS-04 cites `ADR-F2 v1.2 §Consequences (a)`; C-IS-05 cites `ADR-F2 v1.2 §Decision + ADD §2.2 Synthesis`; C-IS-06 cites `ADR-F2 v1.2 §Rationale (a.1)`; C-IS-07 cites `ADR-F2 v1.2 §"Permanent tensions engaged" + §Consequences (c) + ADD §5.2.2`. 10 of 10 contracts carry section-level ADR citations |
| No-architecture-introduction | No spec contract adds architectural commitment beyond ADR-F2 v1.2 + ADD v1.2 content; contracts compose committed material into specification-grade precision | ✅ PASS — all 10 contracts derive directly from ADR-F2 §Decision + §Rationale + §Consequences + ADD §2.2 + §5.2.2 + §5.3.3. No contract asserts a substrate property F2 does not commit. Section §[carry-forwards] [CF-1] explicitly notes that the F2 substrate surface is fully closed at v1.0; F2-12 is downstream-axis territory |
| Translate-not-restate | No spec contract restates PRD observable-behavior text or ADR Decision text verbatim; contracts translate via composition | ✅ PASS — every contract section provides specification-grade structure (signatures, schemas, formulas, enums, surface contracts) absent from PRD prose; ADR Decision text is cited by section, not restated. Spot-check: C-IS-06 §6.1 through §6.5 decomposes ADR-F2 §Rationale (a.1) four-step discipline into per-step signatures + per-step contracts (the four-step discipline is asserted at ADR but not signatured) |
| Persona linkage preserved | Every spec contract preserves the persona §X.y anchor from its parent PRD requirement | ✅ PASS — spot-check: C-IS-01 carries Persona §5.1 + §7 + §10.1 inherited from R-IS-01; C-IS-05 carries Persona §10.4 + §10.2 inherited from R-IS-03; C-IS-08 carries Persona §3.1.1 + §8.1 inherited from R-IS-04. 10 of 10 contracts carry persona anchors |
| Contract grade | Every spec contract sits at specification grade (signature / schema / formula / enum / surface contract); no implementation-grade choices beyond what ADRs commit | ✅ PASS — contract surfaces are: C-IS-01 path-class enumeration + stability invariants (schema); C-IS-02 5-tier schema (enum); C-IS-03 4-sub-role schema (enum); C-IS-04 atomicity contract (surface contract); C-IS-05 six-field record signature (schema); C-IS-06 4-step discipline (signatures); C-IS-07 read/write contract pair (surface contract); C-IS-08 manifest declaration shape + cadence enum (schema + enum); C-IS-09 manifest declaration shape + invariants (schema + surface contract); C-IS-10 export surfaces (surface contract). No implementation-grade commitments beyond ADR-declared (specific path strings, library bindings, API surfaces explicitly deferred) |
| Deferred-to-implementation discretion documented | Contracts that defer detail to Phase 6 implementation discretion per Workflow §2.5.1 exit criteria language carry explicit "deferred to implementation discretion" notation | ✅ PASS — 9 of 10 contracts carry explicit "Deferred to implementation discretion" notation (C-IS-10 is a meta-contract referencing other contracts' implementation deferrals); deferrals include: specific canonical path strings (C-IS-01); tier subdivisions (C-IS-02); commit cadence / message conventions (C-IS-03); deploy tagging (C-IS-04); identifier formats (C-IS-05); library bindings (C-IS-06); navigation primitive APIs (C-IS-07); shadow-ref naming + retention (C-IS-08); worktree directory location + reclamation (C-IS-09) |

**Audit 6.1 aggregate: ✅ PASS (7/7 sub-dimensions across all 10 contracts).**

### Audit 6.2 — PRD-requirement-to-spec sub-matrix audit (Information Substrate axis only)

| Sub-dimension | Result |
|---|---|
| Every session-1 PRD requirement has ≥1 spec contract satisfying it | ✅ PASS — R-IS-01 (3 contracts: C-IS-01, C-IS-02, C-IS-10); R-IS-02 (4 contracts: C-IS-03, C-IS-04, C-IS-07, C-IS-10); R-IS-03 (4 contracts: C-IS-05, C-IS-06, C-IS-07, C-IS-10); R-IS-04 (2 contracts: C-IS-08, C-IS-09) |
| Every session-1 spec contract has ≥1 PRD requirement it satisfies | ✅ PASS — no orphan contracts; every C-IS-01 through C-IS-10 cites ≥1 PRD R-ID |
| ADR commitments cited at session-1 spec are at versions matching PRD substrate set | ✅ PASS — ADR-F2 cited at v1.2; matches `Phase_5_Entry_Handoff.md` §5 substrate version table; matches PRD §"ADR substrate set" table |

**Audit 6.2 aggregate: ✅ PASS (3/3 rules).**

### Audit 6.3 — Front-matter audit (session-1 spec)

| Sub-dimension | Result |
|---|---|
| Session-1 axis declared at front-matter | ✅ PASS — Status block records "Axis: Information Substrate"; Front-matter §"Axis declaration" + §"Axis-grounding note" carry rationale per OD-5-2.A handoff recommendation |
| PRD substrate reference | ✅ PASS — `PRD_v1.0.md` §2 cited at Status block Source-set + Front-matter §"PRD requirement scope" |
| ADR substrate reference | ✅ PASS — ADR-F2 v1.2 enumerated at Status block Source-set + Front-matter §"ADR scope" table |
| ADD substrate reference | ✅ PASS — ADD v1.2 §2.2 + §5.2.2 + §5.3.3 + §6.3.1 cited at Status block Source-set; ADD §2.2 Synthesis cited at every contract that derives from F2 substrate |
| Persona substrate reference | ✅ PASS — Persona Document §3.1.1 + §3.1.3 + §5.1 + §7 + §8.1 + §10.1 + §10.2 + §10.4 enumerated at Status block Source-set + Front-matter §"Persona-linkage substrate" table; per-contract persona linkage inherited |
| Status posture | ✅ PASS — `Status: Proposed` per `Project_Workflow_v1_2.md` §3.1 (no clearance until P5-CK per Workflow §2.5.1 OD-5-4.A) |

**Audit 6.3 aggregate: ✅ PASS (6/6 sub-dimensions).**

### Audit 6.4 — §[carry-forwards] inheritance audit

| Sub-dimension | Result |
|---|---|
| F2-12 carry-forward documented at session-1 spec | ✅ PASS — [CF-1] entry inherits PRD v1.0 §[carry-forwards] [CF-1] verbatim; explicit Information Substrate spec impact statement documents that no Information Substrate contract is open as a function of F2-12 (F2 substrate surface fully closed at v1.0); forward routing documented |
| Workflow §7 substrate-skill propagation carry-forward documented | ✅ PASS — [CF-2] entry inherits PRD v1.0 §[carry-forwards] [CF-2] verbatim; explicit Information Substrate spec impact statement documents non-engagement |
| Carry-forward entries labeled as non-contract-bearing | ✅ PASS — meta-section preamble explicitly states "Entries are documentation, not contract-bearing — they do not engage the §[coherence pass] §6.1 per-contract audit" |

**Audit 6.4 aggregate: ✅ PASS (3/3 sub-dimensions).**

### Audit 6.5 — V3 deference audit

| Sub-dimension | Result |
|---|---|
| Confidence-tag schema | ✅ PASS — V3 `[HIGH]` / `[MODERATE]` / `[SPECULATIVE]` schema preserved; tags applied at the two specification surfaces where uncertainty surfaces: C-IS-01 SKILL.md spec cited as [HIGH] (agentskills.io ratified open standard per ADR-F2 §Rationale (a)); C-IS-06 §6.1 canonicalization library binding flagged [MODERATE] per ADR-F2 §Rationale (a.1) (library binding deferred to D-ADR per ADR-F2 §Consequences (c)) |
| Citations resolve at section level | ✅ PASS — every ADR citation verified by reading the ADR section at the indicated location during substrate read (`view` calls on ADR-F2.md, PRD_v1.0.md, Architectural_Design_Document_v1.md, Phase_5_Entry_Handoff.md at session entry); every persona §X.y anchor verifiable at the indicated section (anchors inherited from PRD §[coherence pass] which audited persona anchors at PRD filing) |
| Anti-fabrication discipline applied | ✅ PASS — no fabricated PRD requirements; no fabricated ADR sections; no invented benchmarks / vendor capabilities; substrate retrieved via `view` against ADR-F2.md + PRD_v1.0.md + Architectural_Design_Document_v1.md + Phase_5_Entry_Handoff.md at session execution before emission |
| Workflow v1.4 §2.3.5 clause (iv) analog | ✅ PASS — section-level citation discipline applied at contract granularity (analog to PRD requirement-granularity citation); every contract carries ADR-ID + section pair in its "ADR commitment(s) honored" sub-section |

**Audit 6.5 aggregate: ✅ PASS (4/4 sub-dimensions).**

### Coherence pass aggregate

| Audit dimension | Result |
|---|---|
| 6.1 Per-contract audit | ✅ PASS (7/7) |
| 6.2 PRD-requirement-to-spec sub-matrix audit | ✅ PASS (3/3) |
| 6.3 Front-matter audit | ✅ PASS (6/6) |
| 6.4 §[carry-forwards] inheritance audit | ✅ PASS (3/3) |
| 6.5 V3 deference audit | ✅ PASS (4/4) |

**Coherence pass: ✅ PASS at all five dimensions. Spec authorized for filing.**

---

*Filed 2026-05-13 at Phase 5 session 1 close → Phase 5 session 2 entry boundary. Session 1 scope: Information Substrate axis specification per OD-5-2.A spec-writer judgment (handoff §3.1 recommendation followed); output `Spec_Information_Substrate_v1.md` per OD-5-1.A axis-led decomposition. Phase 5 arc continues to session 2 (Action Surface) per `Phase_5_Entry_Handoff.md` §3.1 axis sequencing; session 2 session prompt filed at `Phase_5_Session_2_Session_Prompt.md`. Aggregate P5-CK at full specification close per Workflow §2.5.1 + OD-5-4.A. Phase 5 session 2 entry-gate AUTHORIZED against this spec + `Spec_Action_Surface_v1.md` axis substrate.*
```

---

## Part C — Audit checklist (run before emit)

- **Decided-fix check** — ✅ The change applied is exactly the Tension 001 resolution: change every prose "four sub-role(s)" in C-IS-03 §3 to "five". Nothing was decided by the spec-writer; the operator's resolution named the exact change.
- **No-extension check** — ✅ No commitment, field, enum member, or behavior added. The numeric-form miscount `4-sub-role` at §[coherence pass] Audit 6.1 was *surfaced as finding F-T001-a*, not patched. The §3 table, the ADD quote, and all other sections are untouched.
- **Verbatim round-trip** — ✅ The ADD quote at C-IS-03 line 182 ("Git serves a combined role: ...") is byte-exact preserved; it enumerates 5 git roles and is consistent with the corrected count of FIVE. The §3 sub-role table's 5 rows are byte-exact preserved.
- **Preservation check** — ✅ Every section outside C-IS-03 §3 is unchanged; the change-note's "preserved verbatim" list matches the emitted file.
- **Version + change-note** — ✅ Version bumped v1.2 → v1.3 (Status block Status row + new Revision/Revision-date pair); a "Change-note (v1.2 → v1.3)" section is prepended recording trigger, scope, revised/preserved split, surfaced finding, and the `Phase_7_Class_3_Tension_001_*` reference.
- **Back-reference reconciliation** — ✅ No intra-file cross-reference targets a section number that changed (only count words within C-IS-03 §3 changed; section numbering is unchanged). Cross-file absorption (IS-axis plan units citing C-IS-03 sub-role cardinality) is flagged for `implementation-planner` revision-pass in the change-note, not silently left stale.
- **Citation byte-exact** — ✅ No citation was introduced or altered; the only edits are the 5 count words.

**Audit: PASS. Deliverable ready.**
