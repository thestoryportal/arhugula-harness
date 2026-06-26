# Spec-Writer Deliverable — Tension 001 Fix Applied

**Constraint compliance:** No repository files were modified. The fixture file `Spec_Information_Substrate_PRE_tension001_fix.md` is unchanged on disk. The edited spec content and change-note below are produced as a deliverable only.

---

## 1. Decided fix (as authorized)

> In C-IS-03 §3, change every `four sub-roles` to `five`. That is the whole authorized change.

Scope confirmed decided: the input names the exact target string (`four sub-roles`) and the exact replacement (`five`). No architectural choice required — pure bookkeeping. The fix applies the literal-string replacement `four sub-roles` → `five sub-roles` (the count token `four` becomes `five`; the noun `sub-roles` is retained).

---

## 2. Scoped occurrences in C-IS-03 §3

The literal string `four sub-roles` occurs **3 times** within C-IS-03 §3 (lines 188, 198, 206 of the fixture). All three are changed.

| Line | Before | After |
|---|---|---|
| 188 | `...serves four sub-roles within a single git repository...` | `...serves five sub-roles within a single git repository...` |
| 198 | `All four sub-roles share the same git repository identity...` | `All five sub-roles share the same git repository identity...` |
| 206 | `...the four sub-roles share that ledger...` | `...the five sub-roles share that ledger...` |

**Out of scope — NOT changed (preserved verbatim):** the hyphenated string `four-sub-role` at line 178 (`Four-sub-role git tier composition`) and line 182 (`combined git tier serving four-sub-role composition`). These are a different string from the authorized target `four sub-roles`. The authorized fix names `four sub-roles` exactly; changing `four-sub-role` would be a spec extension beyond the authorization (FM-2 / no-extension discipline). They are surfaced as a finding below — not silently patched.

---

## 3. Edited C-IS-03 §3 content (fix applied)

```markdown
## §3 C-IS-03 — Combined git tier role decomposition

**Contract surface.** Four-sub-role git tier composition with foundational-vs-opt-in posture per sub-role.

**PRD requirement(s) satisfied.** R-IS-02 (git as combined-tier state record).

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (combined git tier serving four-sub-role composition); ADD §2.2 Synthesis ("Git serves a combined role: code/spec/prompt/manifest/Skill versioning (foundational) + append-only state-ledger via commit stream + JSONL event ledger (foundational) + on-demand shadow-Git checkpointing (workload-class-opt-in) + worktree-isolation for concurrent sub-agent reads (workload-class-opt-in)").

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
```

---

## 4. Change-note

```markdown
## Change-note (v1.2 → v1.3)

**Date.** 2026-05-15.

**Trigger.** Operator-approved fix, Phase 7 Tension 001 (`Phase_7_Class_3_Tension_001_*` record). Approved change: in C-IS-03 §3, change every `four sub-roles` to `five`.

**Scope of revision.** Single-contract, single-section. Contract ID: C-IS-03. Section: §3 (Combined git tier role decomposition). Three occurrences of the literal string `four sub-roles` revised to `five sub-roles`:
- §3 "Specification content" lead sentence ("...serves five sub-roles within a single git repository...").
- §3 "Sub-role co-residence contract" lead sentence ("All five sub-roles share the same git repository identity...").
- §3 "Cross-sub-role consistency invariant" sentence ("...the five sub-roles share that ledger...").

No other text in C-IS-03 §3 modified. No commitment, field, posture, or sub-role added — the §3 sub-role table already enumerates five rows (Versioning; State-ledger via commit stream; JSONL event ledger; Shadow-Git checkpointing; Worktree-isolation); this fix aligns the prose count token with the existing five-row table.

**Sections preserved verbatim.** §Status block; §Front-matter; §1 C-IS-01; §2 C-IS-02; §4 C-IS-04; §5 C-IS-05; §6 C-IS-06; §7 C-IS-07; §8 C-IS-08; §9 C-IS-09; §10 C-IS-10; §[carry-forwards]; §[traceability]; §[coherence pass]. Within §3 C-IS-03: the "Contract surface" line, the "PRD requirement(s) satisfied" line, the "ADR commitment(s) honored" line, the "Persona linkage" line, the five-row sub-role table, the five co-residence bullet items, and the "Deferred to implementation discretion" line are all preserved verbatim.

**Changes inline.** Status block (Status row; Revision row + Revision date row appended for v1.2 → v1.3). This Change-note section (new; appended above the v1.1 → v1.2 Change-note). §3 C-IS-03: three `four sub-roles` → `five sub-roles` string replacements as enumerated above.

**Surfaced findings (NOT patched — out of authorized scope).**
- FINDING-1: §3 C-IS-03 retains the hyphenated string `Four-sub-role` ("Contract surface" line) and `four-sub-role` ("ADR commitment(s) honored" line). These are a distinct string from the authorized target `four sub-roles` and were therefore left verbatim. After this fix the §3 prose now mixes a "five sub-roles" count (three sites) with a "four-sub-role" count (two sites). If the operator's intent was a uniform count correction across §3, a follow-up authorized fix targeting `four-sub-role` (and the capitalized `Four-sub-role`) is required. The `ADR commitment(s) honored` line additionally cites ADR-F2 v1.2 §Decision as "combined git tier serving four-sub-role composition" — reconciling that citation against a five-sub-role reading would require a back-reference check up the authority chain (ADR-F2 / ADD §2.2 Synthesis) and is not in scope here.

**Back-reference reconciliation.** Intra-file: no section number changed; no intra-file cross-reference to C-IS-03 required updating. Cross-file: plan units and the ADD that cite C-IS-03's sub-role count are downstream absorption owed to `implementation-planner` revision-pass — flagged, not edited here.

**Tension record.** `Phase_7_Class_3_Tension_001_*` record disposition updated to "applied" (per the spec-tension-record-pattern). (Constraint note: this deliverable does not write the tension record file — repository files are not modified by this run; the disposition update is recorded here for the operator to apply.)

**New version.** v1.2 → v1.3.
```

---

## 5. Audit checklist (run before emit)

- **Decided-fix check** — PASS. The applied change is exactly the operator-authorized literal-string replacement `four sub-roles` → `five sub-roles`. No architectural choice made by the spec-writer.
- **No-extension check** — PASS. Only the three exact-match occurrences changed. The hyphenated `four-sub-role` strings were NOT changed (would be an extension); surfaced as FINDING-1 instead.
- **Verbatim round-trip** — PASS. Replacement token `five` matches the authorization byte-exact. All non-targeted text round-trips against the fixture.
- **Preservation check** — PASS. Every section outside §3 C-IS-03 is unchanged; within §3, every element other than the three sentences is verbatim. The change-note "preserved verbatim" list matches.
- **Version + change-note** — PASS. Version bumped v1.2 → v1.3; change-note records trigger, scope, revised/preserved split, findings, and tension-record reference.
- **Back-reference reconciliation** — PASS. No intra-file cross-reference affected; cross-file absorption flagged for `implementation-planner`.
- **Citation byte-exact** — PASS. No citation introduced or altered by the fix.
```
```
