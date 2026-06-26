# C-IS-03 §3 Count Inconsistency — Fix

## Finding

The adversarial reviewer flagged a count inconsistency in **§3 C-IS-03 — Combined git tier role decomposition**. The prose and the table disagree on how many git-tier sub-roles exist:

- **Prose says FOUR.**
  - Contract surface (line 178): "**Four-sub-role** git tier composition with foundational-vs-opt-in posture per sub-role."
  - Specification content lead-in (line 188): "The combined git tier serves **four sub-roles** within a single git repository; each sub-role carries a posture commitment:"
  - ADR commitment text (line 182): "(combined git tier serving **four-sub-role** composition)"

- **Table says FIVE.** The Sub-role table (lines 190–196) enumerates five rows:
  1. Versioning — Foundational
  2. State-ledger via commit stream — Foundational
  3. JSONL event ledger — Foundational
  4. Shadow-Git checkpointing — Workload-class-opt-in
  5. Worktree-isolation for concurrent sub-agent reads — Workload-class-opt-in

## Resolution — the table (FIVE) is canonical; the prose count is wrong

The table reading is corroborated by the ADD §2.2 Synthesis quotation embedded verbatim in the same section's ADR-commitment field (line 182), which itself enumerates **five** distinct roles:

> "Git serves a combined role: code/spec/prompt/manifest/Skill versioning (foundational) **[1]** + append-only state-ledger via commit stream **[2]** + JSONL event ledger **[3]** (foundational) + on-demand shadow-Git checkpointing (workload-class-opt-in) **[4]** + worktree-isolation for concurrent sub-agent reads (workload-class-opt-in) **[5]**".

The "four" prose count is a stale artifact: it counts "state-ledger via commit stream + JSONL event ledger" as a single composite sub-role, but the table (and the ADD synthesis) correctly splits them into two distinct sub-roles each carrying its own row, function, posture, and composition contract. The downstream "five-tier table" at line 130 likewise references "Two-mode composite per C-IS-03 §3" — the commit stream and JSONL ledger are explicitly two modes/sub-roles, not one.

The five sub-roles, their functions, postures, and composition contracts are all fully and correctly specified in the table; only the cardinality words in the prose are defective. Therefore the fix is to correct the prose count from "four" to "five" in all three locations, not to alter the table.

Per the design-substrate revision discipline, the spec contract content (the table) is preserved verbatim; only the inconsistent prose cardinality is reconciled to it.

## Corrected §3 C-IS-03 (changed lines marked)

> **CHANGED** — line 178 (Contract surface): "Four-sub-role" → "Five-sub-role"

**Contract surface.** Five-sub-role git tier composition with foundational-vs-opt-in posture per sub-role.

**PRD requirement(s) satisfied.** R-IS-02 (git as combined-tier state record).

> **CHANGED** — line 182 (ADR commitment): "four-sub-role" → "five-sub-role"

**ADR commitment(s) honored.** ADR-F2 v1.2 §Decision (combined git tier serving five-sub-role composition); ADD §2.2 Synthesis ("Git serves a combined role: code/spec/prompt/manifest/Skill versioning (foundational) + append-only state-ledger via commit stream + JSONL event ledger (foundational) + on-demand shadow-Git checkpointing (workload-class-opt-in) + worktree-isolation for concurrent sub-agent reads (workload-class-opt-in)").

**Persona linkage.** Persona §10.4 (compliance-readiness — hash-chained audit ledger as foundational primitive); §5.1 (remote git of GitHub/GitLab class); §10.2 (cost-attribution-per-span composes against the JSONL event ledger).

**Specification content.**

> **CHANGED** — line 188 (spec content lead-in): "four sub-roles" → "five sub-roles"

The combined git tier serves five sub-roles within a single git repository; each sub-role carries a posture commitment:

| Sub-role | Function | Posture | Composition contract |
|---|---|---|---|
| **Versioning** | Code/spec/prompt/manifest/Skill atomic versioning via git commit history | **Foundational** (always-on; no opt-out) | Composes with C-IS-04 atomic deploy contract |
| **State-ledger via commit stream** | Append-only state-ledger expressed as the git commit stream itself (commit hashes form a chain natively); workflow-canonical commit cadence per workflow class | **Foundational** (always-on; no opt-out) | Composes with JSONL event ledger sub-role; commit-stream-as-coarse-grain-ledger pairs with JSONL-as-fine-grain-ledger |
| **JSONL event ledger** | Per-event append-only JSONL file at workflow-canonical path (per C-IS-01); per-event records carry the canonical six-field entry shape (per C-IS-05); hash-chain integrity constructed per C-IS-06 | **Foundational** (always-on; no opt-out) | Composes with commit-stream sub-role and with C-IS-05 + C-IS-06 entry-shape + hash-chain commitments |
| **Shadow-Git checkpointing** | On-demand checkpoint snapshots via shadow-repository pattern (Cline / kilocode / Roo Code precedent per ADR-F2 §Rationale (a)) | **Workload-class-opt-in** (per workflow manifest declaration per C-IS-08) | Composes with C-IS-08 contract; opt-out workloads do not produce shadow-Git artifacts |
| **Worktree-isolation for concurrent sub-agent reads** | Per-sub-agent worktree directories via `git worktree` primitives; isolates concurrent reads from sibling sub-agents | **Workload-class-opt-in** (per workflow manifest declaration per C-IS-09) | Composes with C-IS-09 contract; opt-out workloads do not allocate worktree directories |

**Sub-role co-residence contract.** All five sub-roles share the same git repository identity without interference:

> **CHANGED** — "All four sub-roles" → "All five sub-roles" (co-residence contract lead-in)

- Versioning operates on the main repository's branch heads.
- State-ledger via commit stream operates on the main branch's commit history; commit messages MAY encode state-ledger-relevant metadata.
- JSONL event ledger is a file artifact tracked in git (versioned via the versioning sub-role); appends to the file produce diff-traceable commits.
- Shadow-Git checkpointing operates via separate shadow refs/branches; does not pollute the main branch commit history.
- Worktree-isolation creates per-sub-agent working directories pointing at the same `.git` storage backend; reads do not contest with one another.

**Cross-sub-role consistency invariant.** A given git repository hosts at most one harness state-ledger; the five sub-roles share that ledger. Cross-repository state-ledger composition is out of scope at F2 substrate layer; per-tenant repository isolation at multi-tenant binding is the F2-compatible scaling shape per ADR-F2 §Consequences (a).

> **CHANGED** — "the four sub-roles share that ledger" → "the five sub-roles share that ledger"

**Deferred to implementation discretion.** Specific commit cadence policy per workflow class; specific commit message conventions for state-ledger-relevant metadata; specific shadow-ref / shadow-branch naming conventions; specific worktree directory naming conventions; specific git hosting backend (GitHub / GitLab / Gitea / self-hosted) per deployment-surface cell.

## Summary of edits

| Location | Before | After |
|---|---|---|
| §3 Contract surface (line 178) | "Four-sub-role" | "Five-sub-role" |
| §3 ADR commitment (line 182) | "four-sub-role composition" | "five-sub-role composition" |
| §3 Specification content lead-in (line 188) | "serves four sub-roles" | "serves five sub-roles" |
| §3 Sub-role co-residence contract (line 198) | "All four sub-roles" | "All five sub-roles" |
| §3 Cross-sub-role consistency invariant (line 206) | "the four sub-roles share that ledger" | "the five sub-roles share that ledger" |

The table content is preserved verbatim. Only the prose cardinality words are reconciled to the canonical five-row table and the ADD §2.2 Synthesis enumeration.

## Note — other count references outside §3 (informational, not in scope of this fix)

Lines 657 and 658 reference C-IS-03 as a "4-sub-role schema" and a contract that defers "tier subdivisions". The "4-sub-role schema" label at line 657 is the same stale count and would also need correction to "5-sub-role schema" for full document consistency. This fix targets the §3 inconsistency the reviewer flagged; the line 657 reference is flagged here so it can be reconciled in the same revision pass.
