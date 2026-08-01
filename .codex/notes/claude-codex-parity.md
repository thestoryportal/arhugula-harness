# Claude-to-Codex parity — 2026-08-01

This is the durable audit record for replacing Claude as the interactive runner
without discarding compatible workflow capability. "Surgical" means no unrelated
repo churn; it does not mean reduced parity.

## Capability matrix

| Surface | Claude posture immediately before handoff | Codex adoption |
|---|---|---|
| Project governance | `CLAUDE.md`, axis files, `CONTEXT.md` | `AGENTS.md` compact projections plus targeted canonical `CLAUDE.md` lineage |
| Hooks | 12 lifecycle groups in `.claude/settings.json` | Every Codex-supported behavior is wired in `.codex/hooks.json`; see `.codex/hooks/README.md` |
| Tracked project skills | 35 canonical skills, including council and shipping workflows | 35/35 discovery entrypoints; native workflow skills where runner mechanics differ, full-body bridges elsewhere |
| Operator-installed design skills | `frontend-design`, `impeccable`, `taste-skill`, `ui-ux-pro-max` under the root checkout's project `.claude/skills/` | Same source bodies adopted through tracked Codex bridge entrypoints; no copy, deletion, shortening, or deprecation |
| Global gstack skills | Claude skill catalog | Same gstack packages are already present in Codex's discovered skill catalog |
| Project memory | Claude project `memory/MEMORY.md` plus linked topic files | Mandatory discipline digest at startup; task-relevant index/topic lookup remains available and required |
| Context checkpoints | gstack `context-save` / `context-restore` and repo handoffs | Same gstack skills plus `.harness/handoff/README-resume.md` and Codex deterministic checkpoints; all advisory until HEAD verification |
| Out-of-family review | Codex reviewed Claude-authored diffs | Antigravity (`agy`) through `just gemini-review` reviews Codex-authored diffs |
| Pre-merge review | Three fresh agent lenses | Three fresh ephemeral read-only `codex exec` lenses; all-approve and logged |
| CI | Green PR CI, then green `main` CI | Same, including merge-SHA pinning and terminating-refresh `main` CI before forward work |
| Git autonomy | Safe scoped commands with destructive operations guarded | Same scoped approvals plus permission guard; force push, history rewrite, remote delete, and force cleanup remain denied |
| Session UI | Claude status line and lifecycle output | Codex user-level TUI `status_line` provides model/context/branch/usage state; hook lifecycle output remains visible |
| Early-June Codex profile | Isolated `~/.codex-arhugula` home with `CLAUDE.md` fallback and a small copied skill set | Preserved read-only as historical/recovery state; the primary Codex home plus repo projections carry the compatible behavior forward without deleting its history |

## Skill bridge contract

A bridge skill is not a shortened rewrite. It requires the executing Codex agent
to read the complete canonical `.claude/skills/**/SKILL.md` and every reference
that file routes to, then follow that workflow with only these runner translations:

- Claude `Agent` / `Task` becomes a dedicated Codex subagent or isolated `codex exec`.
- `AskUserQuestion` becomes the Codex user-input surface only for a genuine user-owned fork.
- Claude scratch output becomes `/tmp` or another ignored scratch path.
- Reviewer routing follows authorship: Claude author → Codex review; Codex author → Antigravity.
- Transcript-aware advisor judgment remains the interactive controller's job and is complemented, never silently replaced, by the out-of-family artifact review.

The Codex-native `roadmap-continue`, `ship-pr`, `codex-autonomous-loop`, and
`merge-gate` skills encode the current runner-specific fixed point explicitly.

## Hooks and trust

Codex 0.144.4 exposes `SessionStart`, `SessionEnd`, `SubagentStart`,
`SubagentStop`, `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`,
`PostCompact`, `UserPromptSubmit`, and `Stop`. It does not expose dedicated
`PostToolUseFailure` or `StopFailure` events. Failed Bash calls still emit
`PostToolUse`, so the adapter preserves Claude's failure capture there.
`StopFailure` is the one non-event-exact gap and must remain visible rather than
being described as full parity.

Hook trust is separate from project trust. Codex persists trust by the exact
handler-definition hash in `~/.codex/config.toml`. After this hook set lands,
use `/hooks` in the Codex TUI to inspect and trust every new or changed handler.
Do not normalize bypassing trust in the autonomous launcher.

The operator granted standing authorization on 2026-08-01 for `just gemini-review` to use
the OAuth-authenticated Antigravity `agy` CLI subscription and disclose the current repository
diff on every forward arc; Codex must not ask for that approval again. Direct Gemini/Google
API calls, API keys, service-account credentials, and Vertex project routing are forbidden for
this review. `tools/agy_review.py` supplies tracked and untracked changes directly, strips those
provider credential/routing variables, stays in plan mode, and fails closed unless the final
non-empty output line is an exact approval or block.

## Permissions and safe Git command shape

Codex has three separate permission layers; treating them as one is what made
the handoff look intermittent:

1. `~/.codex/rules/default.rules` persists scoped command decisions. A TUI
   "always allow" choice writes a `prefix_rule` there and takes effect after a
   restart.
2. The trusted repo hooks enforce the narrower arhugula policy. In autonomous
   loop mode they allow the controller lifecycle, normal Git/PR transport,
   exact `git merge --no-edit main|origin/main` topic sync, and fresh ephemeral
   read-only merge lenses; they still deny rebase/history rewrite, force push,
   force cleanup, remote deletion, paid calls and credential mutation.
3. The active sandbox or organization-managed requirements decide whether even
   an approved command can write protected paths or use network/localhost.
   `workspace-write` makes both a checkout's `.git` and a linked worktree's
   resolved common Git directory read-only. Therefore **leaving the worktree is
   not a permission fix** and also abandons the repo's isolation discipline.

For ordinary interactive work, keep `workspace-write` and persist only reviewed
command prefixes. For the operator-approved full autonomous loop, use the named,
opt-in profile template at
`.codex/notes/arhugula-forward.config.toml.example`:

```bash
cp .codex/notes/arhugula-forward.config.toml.example \
  ~/.codex/arhugula-forward.config.toml
codex --profile arhugula-forward --cd /Users/robertrhu/Projects/arhugula-v2
```

This uses the current primary Codex home, so current models, plugins, gstack,
skills, memory and rules remain available. It supersedes the need to launch the
older isolated `codex-arhugula` wrapper without deleting that recovery profile.
It intentionally keeps `approval_policy = "on-request"` and auto-review; it does
not use `--dangerously-bypass-approvals-and-sandbox` or bypass hook trust. Trust
the landed hooks through `/hooks` before starting the first loop.

The named profile removes the local command sandbox only for sessions launched
with `--profile arhugula-forward`, which is required for Git metadata writes,
localhost integration fixtures and the `agy`/GitHub transport. Organization-
managed requirements can still forbid that profile or specific actions; user
rules and project hooks cannot broaden a managed tenant ceiling. If `codex
doctor --summary` still reports restricted filesystem/network after launching
the profile, restart in a non-managed local CLI environment or have the tenant
requirements changed—the repository cannot override it.

The early-June profile remains valuable evidence rather than a deprecated
dead end. Its exact sessions, history, state and copied skills remain under
`~/.codex-arhugula/CODEX_HOME/`; query them when an old-runtime claim needs exact
reconstruction. The current `~/.codex/memories/MEMORY.md` also indexes the
relevant early-June rollouts. The named forward profile deliberately overlays
the current primary `~/.codex/config.toml`, so it retains the modern status line,
plugins, gstack catalog, rules and memories instead of forking them again.

Run normal Git operations with the isolated worktree supplied as the command
working directory:

```text
git add <explicit paths>
git commit -m <message>
git push
git pull --ff-only
git worktree add|list|remove <non-force args>
git branch -d <verified merged local branch>
```

Do not use `git add -A`. Do not approve a broad push rule that would obscure a
force push. The permission guard continues to deny force push, history rewrite,
force worktree removal, force local-branch deletion, and remote-branch deletion.

## Memory and restore rule

Codex must not flatten Claude's project memory into a stale prose copy. Query:

1. `~/.claude/projects/-Users-robertrhu-Projects-arhugula-v2/memory/MEMORY.md`
2. only the linked task-relevant topic files
3. `~/.gstack/projects/arhugula-v2/checkpoints/` when resuming historical work
4. `.harness/handoff/README-resume.md` for current cross-runner handoff

Then verify branch, HEAD, worktrees, roadmap status, loop state, source, and CI.
The checked-in `.codex/notes/discipline-digest.md` is the mandatory startup
subset; the full memory and checkpoint stores remain valuable searchable evidence.

## Shipping fixed point

For a substantive Codex-authored arc:

1. isolated worktree + preflight + TDD/local gates
2. Standing-authorized Antigravity review through `just gemini-review`; no per-run approval
3. closeout, explicit staging, commit, push, PR
4. final PR-head CI and current base-main CI green; stale prior branch inventory reconciled
5. three fresh Codex lenses all approve; log row committed and CI green
6. re-read head SHA and merge with `--match-head-commit`
7. merge SHA's own `main` push CI green
8. immediate terminating refresh when owed; refresh `main` CI green
9. local main sync, worktree/branch disposition, loop check
10. reflection + gstack `context-save`, then initialize the next arc

No forward arc begins between steps 6 and 10.
