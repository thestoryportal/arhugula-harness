# Tension 001 Fix — Spec Information Substrate: C-IS-03 §3 sub-role count

## Deliverable

This file contains the edited spec content and change-note as the deliverable. Per
constraints, no repository file (including the fixture) was modified.

**Source fixture (not modified):**
`.claude/skills/spec-writer/evals/fixtures/Spec_Information_Substrate_PRE_tension001_fix.md`

**Resolution applied:** Tension 001 — the C-IS-03 §3 combined-git-tier section enumerates
**five** sub-roles, not four. The §3 sub-role table (Versioning, State-ledger via commit
stream, JSONL event ledger, Shadow-Git checkpointing, Worktree-isolation for concurrent
sub-agent reads) lists 5 rows; ADR-F2 §Decision and the ADD §2.2 Synthesis both enumerate
5. The §3 prose said "four sub-roles" (and the hyphenated adjective form "four-sub-role")
in 5 places. Decided fix: change every such occurrence to "five". Version bumped
v1.2 → v1.3.

---

## 1. Edits applied (5 sites, all within §3 C-IS-03)

| # | Line | Before | After |
|---|---|---|---|
| 1 | 178 | `**Contract surface.** Four-sub-role git tier composition with foundational-vs-opt-in posture per sub-role.` | `**Contract surface.** Five-sub-role git tier composition with foundational-vs-opt-in posture per sub-role.` |
| 2 | 182 | `ADR-F2 v1.2 §Decision (combined git tier serving four-sub-role composition)` | `ADR-F2 v1.2 §Decision (combined git tier serving five-sub-role composition)` |
| 3 | 188 | `The combined git tier serves four sub-roles within a single git repository; each sub-role carries a posture commitment:` | `The combined git tier serves five sub-roles within a single git repository; each sub-role carries a posture commitment:` |
| 4 | 198 | `**Sub-role co-residence contract.** All four sub-roles share the same git repository identity without interference:` | `**Sub-role co-residence contract.** All five sub-roles share the same git repository identity without interference:` |
| 5 | 206 | `**Cross-sub-role consistency invariant.** A given git repository hosts at most one harness state-ledger; the four sub-roles share that ledger.` | `**Cross-sub-role consistency invariant.** A given git repository hosts at most one harness state-ledger; the five sub-roles share that ledger.` |

**Occurrences of "four" deliberately NOT changed** (not git sub-roles — out of Tension 001 scope):
- L62 — "four PRD requirements (R-IS-01 through R-IS-04)"
- L123 — "Four canonical artifact classes reside on the filesystem"
- L138 — "All four artifact classes are filesystem-readable"
- L224 — "four co-located artifact classes" (C-IS-04 deploy unit)
- L233 — "four artifact classes" (C-IS-04)
- L238 — "four artifact classes" (C-IS-04)
- L298 — "four-step discipline" (C-IS-06 hash-chain)
- L655 — "four-step discipline" (C-IS-06, coherence pass)

---

## 2. Version bump

Spec version bumped **v1.2 → v1.3**. The Status block gains a new Revision row +
Revision date row; a new Change-note (v1.2 → v1.3) section is appended between the
Status block and the existing Change-note (v1.1 → v1.2).

### Edited Status block (full section)

```markdown
## Status block

| Field | Value |
|---|---|
| Artifact | `Spec_Information_Substrate_v1.md` |
| Status | **Proposed** (v1.3 — Phase 7 Tension 001 resolution applied; coherence pass preserved verbatim as v1 + v1.1 historical record per Change-note §"§[coherence pass] preservation discipline") |
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
| Revision | v1.2 → v1.3 (Phase 7 Tension 001 resolution — C-IS-03 §3 combined-git-tier sub-role count corrected from "four" to "five" at 5 prose sites; the §3 sub-role table enumerates 5 rows and ADR-F2 §Decision + ADD §2.2 Synthesis both enumerate 5 sub-roles; prose-vs-table count drift corrected per operator-approved Tension 001 fix; all other contracts preserved verbatim) |
| Revision date | 2026-05-15 |
```

### New Change-note section (appended after Status block, before Change-note v1.1 → v1.2)

```markdown
## Change-note (v1.2 → v1.3)

**Scope of revision.** Single-tension resolution pass clearing Phase 7 Tension 001
(Class 1 mechanical — prose-vs-table count drift). The C-IS-03 §3 combined-git-tier
section enumerates a git tier serving **five** sub-roles: the §3 sub-role table commits
5 rows (Versioning; State-ledger via commit stream; JSONL event ledger; Shadow-Git
checkpointing; Worktree-isolation for concurrent sub-agent reads), and ADR-F2 v1.2
§Decision + ADD §2.2 Synthesis both enumerate 5 sub-roles. The §3 prose, however,
stated "four sub-roles" (and the hyphenated adjective form "four-sub-role") at 5 sites.
Decided fix per operator-approved Tension 001 resolution: change every such occurrence
to "five". The §3 sub-role table is the canonical reading; the prose aligns to the
table and to the upstream ADR-F2 / ADD enumeration.

**Sections preserved verbatim at v1.3.** All sections except §3 C-IS-03 prose
(enumerated below) and the Status block. §Front-matter; §1 C-IS-01; §2 C-IS-02;
§3 C-IS-03 sub-role table (already 5 rows — unchanged); §4 C-IS-04; §5 C-IS-05;
§6 C-IS-06; §7 C-IS-07; §8 C-IS-08; §9 C-IS-09; §10 C-IS-10; §[traceability] matrix;
§[carry-forwards]; §[coherence pass] (preserved verbatim as v1 + v1.1 historical
record).

**Changes inline.** Status block (Status row revised; third pair of Revision row +
Revision date row appended for v1.2 → v1.3). This Change-note section (new; appended
between Status block and previous Change-note v1.1 → v1.2). §3 C-IS-03 at 5 prose
sites: "Contract surface" line ("Four-sub-role" → "Five-sub-role"); "ADR commitment(s)
honored" line ("four-sub-role composition" → "five-sub-role composition"); the
"Specification content" lead sentence ("serves four sub-roles" → "serves five
sub-roles"); "Sub-role co-residence contract" line ("All four sub-roles" → "All five
sub-roles"); "Cross-sub-role consistency invariant" line ("the four sub-roles share
that ledger" → "the five sub-roles share that ledger"). Five amendment sites total;
no other content modified. Occurrences of "four" elsewhere in the spec (four PRD
requirements; four artifact classes; four-step hash-chain discipline) refer to
unrelated enumerations and are correctly left unchanged.

**§[coherence pass] preservation discipline.** §[coherence pass] section at v1.3 is
preserved verbatim as the v1 + v1.1 point-in-time audit historical record. The v1.3
Tension 001 resolution is a mechanical count-correction and does not re-run the audit;
audit rows referencing earlier substrate state remain accurate historical record.
```

---

## 3. Edited §3 C-IS-03 section (full, with all 5 fixes applied)

```markdown
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
```

---

## 4. Verification

- §3 sub-role table row count: **5** (matches the corrected prose).
- ADR-F2 §Decision combined-tier enumeration: **5** sub-roles.
- ADD §2.2 Synthesis enumeration: **5** (versioning + commit-stream state-ledger +
  JSONL event ledger + shadow-Git checkpointing + worktree-isolation).
- Prose-vs-table drift: **resolved** — all 5 "four sub-role(s)" sites in §3 now read
  "five".
- Version: **v1.2 → v1.3**, Status block + new Change-note section reflect the bump.
```
