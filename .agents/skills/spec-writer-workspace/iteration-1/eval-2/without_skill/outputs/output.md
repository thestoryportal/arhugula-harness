# Spec Fix Deliverable — C-IS-03 §3: "four sub-roles" → "five"

**Source spec:** `.claude/skills/spec-writer/evals/fixtures/Spec_Information_Substrate_PRE_tension001_fix.md`
**Authorized change:** In C-IS-03 §3, change every "four sub-roles" to "five".
**Scope:** C-IS-03 §3 only (lines 176–209 of source). Fixture file NOT modified per constraints — edited content reproduced here as the deliverable.

---

## Change-Note

| Field | Value |
|---|---|
| Tension | tension001 |
| Contract affected | C-IS-03 §3 — Combined git tier role decomposition |
| Change | Prose count "four sub-roles" → "five" (sub-role table already enumerates five rows: Versioning, State-ledger via commit stream, JSONL event ledger, Shadow-Git checkpointing, Worktree-isolation). The prose count was stale against the table; this aligns the count to the canonical five-row table. |
| Occurrences changed | 3 literal "four sub-roles" strings within C-IS-03 §3 (source lines 188, 198, 206) |
| Occurrences NOT changed (out of authorized scope / not literal match) | Line 178 "Four-sub-role git tier composition"; line 182 "combined git tier serving four-sub-role composition" (Contract surface / ADR-commitment prose — hyphenated "four-sub-role", not the string "four sub-roles"); line 657 coherence-pass matrix "C-IS-03 4-sub-role schema" (outside §3). These were left untouched because the authorized change is exactly "every 'four sub-roles'" and is scoped to C-IS-03 §3. |

---

## Edited C-IS-03 §3 (full section, fix applied)

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

## Diff summary (3 lines changed)

| Source line | Before | After |
|---|---|---|
| 188 | `The combined git tier serves four sub-roles within a single git repository;` | `The combined git tier serves five sub-roles within a single git repository;` |
| 198 | `**Sub-role co-residence contract.** All four sub-roles share the same git repository identity` | `**Sub-role co-residence contract.** All five sub-roles share the same git repository identity` |
| 206 | `at most one harness state-ledger; the four sub-roles share that ledger.` | `at most one harness state-ledger; the five sub-roles share that ledger.` |

All three changes are within C-IS-03 §3. No other sections or files modified.
