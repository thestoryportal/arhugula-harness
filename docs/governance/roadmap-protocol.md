# Governance pack — roadmap + drift-detection protocol

*Relocated BYTE-VERBATIM from Root `CLAUDE.md` §12, §12.1, §12.2, §12.3, §12.5, §12.5.1–§12.5.4 by U-CTX-13 (R-CTX-1 Arc 5, 2026-08-11).*
*The root file keeps every heading with its number and position, plus a resolving
pointer to this file. Query this pack for the detail; do not preload it.*

---

## 12. Roadmap + drift-detection protocol

*Operationalizes `Project_Roadmap_v1.md` (workspace root) + `.harness/roadmap_status.md`. Closes the gap between "roadmap exists" and "roadmap drives execution." Per operator directive 2026-05-31: future sessions derive their next action from the roadmap without operator AUQ.*

*(2026-07-14: the prior operator-facing HTML dashboard — `tools/dashboard/generate.py` + the committed `tools/dashboard/roadmap.html` snapshot, published via GitHub Pages — was eliminated per operator direction. `.harness/roadmap_status.md` is the sole surviving mechanism this section governs; it was never rendered by the HTML dashboard, so nothing here changes in substance — only the vocabulary drops "dashboard" as a synonym for it.)*

### 12.1 Mandatory session-start audit

**Automation:** the audit fires automatically via the `SessionStart` hook at `.claude/settings.json` → `tools/roadmap-audit/session-start.sh`. Hook output (a compact `[ROADMAP]` / `[ROADMAP DRIFT]` block) is injected into the session preamble before Claude processes the operator's first message. Claude SHOULD honor the hook output; if the hook fails to fire (CI environment, custom Claude Code config), apply the procedure manually per the steps below.

Before the first substantive edit in any session, Claude MUST:

1. Read `.harness/roadmap_status.md` (the live head only — when a historical `## Next action` round is needed, grep/query `.harness/roadmap-next-action-archive.md` by PR/`B-`/`R-`-id/round rather than reading it wholesale).
2. Compute `workspace_state_hash` per the recipe at `Project_Roadmap_v1.md` §7.1 step 2:
   - `git rev-parse HEAD` (first 8 chars)
   - sorted open-PR list from `gh pr list --state open --json number,headRefName`
   - count of `.harness/class_1_fork_*.md` + `.harness/class_2_fork_*.md` (open fork docs)
   - latest retirement-batch path from `ls .harness/phase-7d-retirement-events-batch-*.md | sort -V | tail -1`
   - `sha256(concat).hexdigest()[:12]`
3. Compare with `roadmap_status.md`'s recorded `workspace_state_hash`.
4. **Mismatch → HALT.** Do not proceed to substantive work. Surface to operator with reconciliation options:
   - (a) refresh `roadmap_status.md` from current state, proceed
   - (b) revert workspace to the recorded state (only if drift is uncommitted)
   - (c) operator manually resolves
5. **Match → proceed** to next-action derivation per `Project_Roadmap_v1.md` §4.
6. **Fixed-point carve-out** (per §12.2.1). If `roadmap_status.md`'s recorded `workspace_state_hash` does NOT match current state, but the most recent merge commit on main is a terminating refresh PR (title **begins with** `ops: roadmap status refresh ` — suffix format-agnostic per §12.2.1), AND the recorded hash matches `compute(state at merge_commit~1)` (the state immediately before that refresh-merge), the drift is the expected lag-by-one-commit per §12.2.1. Treat as MATCH; silently recompute and update the stored hash against current HEAD; proceed. Do NOT spawn a new refresh PR.

This audit is the load-bearing discipline. Skipping it = silent drift = the failure mode the roadmap was authored to prevent.

### 12.2 Mandatory post-PR-merge audit

After any PR merges to main (whether merged by Claude or operator):

1. Recompute `workspace_state_hash` per §12.1 step 2.
2. Update `.harness/roadmap_status.md`:
   - `workspace_state_hash` → new value
   - `last_refreshed` → ISO 8601 now
   - `recently_completed` → prepend the merged PR (drop oldest if >5 entries)
   - `in_flight` → remove merged PR, add any newly-opened PRs
   - `next_action` → re-derive per `Project_Roadmap_v1.md` §4 (the superseded paragraph is REPLACED in the live head, never left accumulating inline — U-CTX-03's head-byte-budget `--check` gate enforces this; its text — taken verbatim from the live head's git history, label rewritten `Current` → `Prior next action (post-#N)` — is appended to the PRIOR-ONLY `.harness/roadmap-next-action-archive.md` by the NEXT content PR, never by the terminating refresh commit itself, whose changed-set stays exactly `.harness/roadmap_status.md` per §12.2.1)
   - **arc-ledger** — if an R-FS-1 arc transited (an arc closed/resolved, or a new arc/unit surfaced), edit the `.harness/arc-ledger.yaml` row **AND** bump its `snapshot:` block in the **same commit** (forward-only; the blocking CI `arc-ledger` job + `tools/arc_ledger.py --check` fail on an impossible/stale tally). There is no parseable markdown copy to drift (the old `.harness/r-fs-1-arc-and-unit-map.md` is a retired pointer stub).
3. If any R-NNN entry at `Project_Roadmap_v1.md` §5 closed at this PR, mark it `RESOLVED` and refresh `next_pointer` propagation.
4. Commit with a title beginning `ops: roadmap status refresh ` (e.g. `…post-PR-NN` or `…post-#NN`; the §12.2.1 carve-out keys on the prefix, suffix format-free). Push.

### 12.3 Halt-and-reconcile protocol

When drift is detected at session-start audit OR when an R-NNN entry's `depends_on` resolution is empirically false at workspace state OR when an unexpected file appears under `design-substrate/**` / `harness-*/src/**` not accounted in any open PR:

1. State `DRIFT DETECTED` in session output.
2. Enumerate the divergence: what `roadmap_status.md` claims vs. what the workspace shows.
3. Present the 3 reconciliation options (§12.1 step 4) via AskUserQuestion.
4. Do NOT make any substantive edits until operator response.
5. After response: update `.harness/roadmap_status.md`, then resume execution per the resolved direction.

### 12.5 Memory hygiene + checkpointing integration

The roadmap is one of three durable persistence mechanisms; this section names how all three compose. Without this integration, memory + checkpoints drift away from roadmap state and the audit protocol catches roadmap_status.md drift but misses memory/checkpoint drift.

**Three persistence mechanisms.**

| Mechanism | Surface | Scope | Authority |
|---|---|---|---|
| **Roadmap + status** | `Project_Roadmap_v1.md` + `.harness/roadmap_status.md` | Cross-session next-action + workspace state | This §12 |
| **Auto-memory** | `~/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/` | Patterns, feedback, project context, references, learnings | Global `~/.claude/CLAUDE.md` auto-memory section |
| **Checkpoints** | `~/.gstack/projects/thestoryportal-arhugula-harness/checkpoints/` | Mid-arc transient state for cross-session resume | gstack `/context-save` + `/context-restore` skills |

**Distinction by scope.**

- **Roadmap = "what's next, durably."** Survives across all sessions; refreshed at every PR merge.
- **Memory = "non-obvious patterns + user preferences."** Survives across all sessions; refreshed event-driven (cardinality ≥2, user feedback, etc.).
- **Checkpoint = "where I was in this specific arc."** Transient; advisory at resume per `[[feedback-checkpoint-remaining-work-is-advisory-not-authoritative]]`.

#### 12.5.1 Memory hygiene disciplines (always-on)

| Discipline | When |
|---|---|
| **Save patterns at cardinality ≥2** | Second instance of a `[[pattern]]` surfaces → write `memory/<slug>.md` + index line in `MEMORY.md`. Cardinality 1 = candidate noted in change-note; ≥2 = save. |
| **Save feedback symmetrically** | Corrections AND confirmations both save. Asymmetric saving drifts behavior toward over-cautious. |
| **Update existing entries, do not duplicate** | Check `MEMORY.md` index before authoring new; refresh existing entry if topic matches. |
| **Verify cited memory before acting** | Memory can be stale. If memory names a file/function/flag, grep first; halt + refresh if false (per Workflow v1.13 §7.4.7.3). |
| **Mind the 24,400-byte MEMORY.md cap** | Before saving context to MEMORY, first precisely measure the exact byte size before writing any memory context and proactively trim the file in a single pass based on the measurement rather than iterative edits. When trimming, change existing status lines in place instead of appending redundant fields. . Compaction = shorten descriptions, drop superseded entries (full text preserved at `memory/<slug>.md`). |
| **Delete superseded entries** | Wrong / outdated → remove from index, not just append. Provenance lives in git history at the global memory store. |
| **No code-derivable saves** | Don't save what `git log` / source code shows. Memory is for non-obvious surprises, not architecture. |
| **Periodic audit** | Cadence ~every 20 entries or operator-discretion (current cadence: round-3 audits via R-IF-NNN PRs). |

#### 12.5.2 Checkpoint disciplines (event-driven)

`/context-save-lean` (the workspace copy of the gstack save flow, U-SR-08/WR-15) fires when:

- Session approaches compaction or substantive multi-step arc is mid-flight.
- Session ends with uncommitted state operator may want to resume.
- Before risky operations (force-push, large refactor, design-phase amendment) — save first so resume is possible.

`/context-restore` fires at session start when prior work was in-flight (cross-branch default; Conductor workspace handoff use case).

**Checkpoint × roadmap interaction.** `roadmap_status.md` supersedes checkpoints for cross-session next-action derivation. Checkpoints retain value for mid-arc state (Decisions Made, Remaining Work within a single arc not yet PR'd). When resuming from a checkpoint, always:

1. Read the checkpoint for context.
2. Run the §12.1 session-start audit against current workspace state.
3. If checkpoint's "Remaining Work" diverges from `roadmap_status.md`'s next_action → trust `roadmap_status.md`, treat the checkpoint as advisory orientation.

#### 12.5.3 R-NNN closure cascade (post-close audit)

After any R-NNN closes (PR merge), the post-merge audit at §12.2 MUST also:

1. **Memory check** — if the R-NNN's close surfaced a new pattern at cardinality ≥2, write memory entry + MEMORY.md line in the same PR (or follow-on PR if scope tightness requires).
2. **Memory refresh** — if the close superseded an existing memory entry (e.g., a pattern's status changed, a finding closed), update the entry in the same PR.
3. **Checkpoint clean** — a checkpoint is **"resolved"** when its `branch:` is in the merged set (the squash-merge-safe `gh pr list --state merged` head-ref cross-ref, per `[[squash-merge-branch-prune-recipe]]`) — a machine-checkable test, not a free-text "Remaining Work fully addressed" judgment. As-built (U-HK-26..29 reconciliation, review-doc §10 R-2): the **PreCompact snapshots** at `.harness/.checkpoints/` are *thin temporal* records — `session-end-cleanup.sh`'s keep-10 prune is their correct lifecycle (archival adds no value). The richer **gstack `/context-save`** checkpoints at `~/.gstack/.../checkpoints/` are append-only history by default; archiving resolved ones to a `checkpoints/archive/` subdir is *optional* low-value hygiene — not a standing requirement, and deliberately **not** automated (no two-system resolved-detection machinery was built).

#### 12.5.4 Pre-substantive memory + checkpoint discipline

Before authoring against a memory or checkpoint claim:

| Source | Pre-substantive check |
|---|---|
| Memory entry says "X exists at file Y line Z" | Grep / read to verify. Memory is frozen at write-time. |
| Memory entry summarizes "recent activity" | Prefer `git log` / source code over recalling the snapshot. |
| Checkpoint says "Remaining Work item 3" | Empirically verify against HEAD before acting (per `[[feedback-checkpoint-remaining-work-is-advisory-not-authoritative]]`). |
| Memory cites a `[[pattern]]` that drives decision | Verify the pattern still has cardinality ≥2 at current memory state (patterns can be retired). |

