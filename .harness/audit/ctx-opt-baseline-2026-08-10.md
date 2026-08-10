# R-CTX-1 U-CTX-01 — Config-Hygiene Baseline Snapshot (2026-08-10, PRE-change)

Captured BEFORE any U-CTX-01 config change, per the approved plan's snapshot-first AC
(execution doc: `~/.gstack/projects/arhugula-v2/checkpoints/r-ctx-1-implementation-plan-v1.md`;
register rows B-148/B-149). All surfaces below are MACHINE-LOCAL config
(`~/.claude/*`, `~/.claude.json`, repo `.claude/settings.local.json` — gitignored);
this committed snapshot is the durable pre-state record + per-change revert recipes.

## 1. skillOverrides (repo `.claude/settings.local.json`, gitignored)

Pre-change: **75 entries, all `"off"`**. None of the 18 U-CTX-01 targets present
(verified by script 2026-08-10). Full pre-change key list:

```
anywidget-generator, auto-paper-demo, autoplan, benchmark, blender-assembly,
browse, canary, careful, codex, create-github-action-workflow-specification,
create-implementation-plan, cso, design-consultation, design-html, design-review,
design-shotgun, devex-review, find-skills, graphify, gstack, gstack-upgrade,
guard, health, implement-paper, implement-paper-auto, investigate,
javascript-typescript-jest, jupyter-to-marimo, land-and-deploy, learn,
marimo-batch, marimo-notebook, marimo-pair, n8n-code-javascript,
n8n-mcp-tools-expert, n8n-node-configuration, n8n-workflow-patterns,
office-hours, open-gstack-browser, pair-agent, plan-ceo-review,
plan-design-review, plan-devex-review, plan-eng-review, pnpm,
prd-to-agentic-spec, prd-to-engineering-spec,
project-workflow-analysis-blueprint-generator, qa, qa-only, retro, review,
setup-browser-cookies, setup-deploy, ship, skill-builder,
skill-scenario-generator, streamlit-to-marimo, typescript-advanced-types,
typescript-mcp-server-generator, unfreeze, unocss, vercel-cli-with-tokens,
vercel-composition-patterns, vercel-react-best-practices,
vercel-react-native-skills, vercel-react-view-transitions, vite, vitepress,
vitest, vue-best-practices, vue-router-best-practices,
vue-testing-best-practices, wasm-compatibility, web-design-guidelines
```

Note: `gstack` was ALREADY off pre-program (not a U-CTX-01 change). The plan's
KEEP list (context-save, context-restore, _gstack-command, gstack `bin/` runtime
dep, icm-workspace, notebooklm, document-generate/-release, brainstorming,
writing-plans, diagram, spec) is untouched by this unit.

**Change applied (post-snapshot):** +18 entries `"off"`: algorithmic-art,
cate-theme, add-molab-badge, connect-chrome, scrape, skillify, setup-gbrain,
sync-gbrain, ios-clean, ios-sync, ios-design-review, ios-qa, ios-fix, freeze,
landing-report, make-pdf, benchmark-models, plan-tune.
**Revert:** delete those 18 keys from `skillOverrides` in
`.claude/settings.local.json` (one `python -c` dict-del or hand edit).

## 2. Plugins (`~/.claude/plugins/installed_plugins.json` v2 + `~/.claude/settings.json` enabledPlugins)

Pre-change inventory (name@marketplace · scope · version):

| Plugin | Scope | Version | Note |
|---|---|---|---|
| frontend-design@claude-plugins-official | user | 7b918e0631d5 | untouched |
| context7@claude-plugins-official | user | 7b918e0631d5 | **disabled by this unit** |
| swift-lsp@claude-plugins-official | user | 1.0.0 | untouched |
| coderabbit@claude-plugins-official | local (`~/Projects/arhugula`) | 1.1.1 | untouched (D3: CodeRabbit intact) |
| andrej-karpathy-skills@karpathy-skills | local (`~/Projects/arhugula`) | 1.0.0 | untouched |
| learn@agentskill-sh | user | 1.0.0 | already disabled in enabledPlugins |
| skill-creator@claude-plugins-official | user | 7b918e0631d5 | untouched |
| understand-anything@understand-anything | local ×2 (`~/Projects/arhugula-v2` + `…/.codex-worktrees/codex-hook-contract-fix-plan`, the latter installed 2026-08-10T12:59Z) | 2.7.6 | **uninstalled by this unit** |

Pre-change `enabledPlugins` (`~/.claude/settings.json`):
`context7@claude-plugins-official: true`, `learn@agentskill-sh: false`,
`skill-creator@claude-plugins-official: true`.
`extraKnownMarketplaces` includes `understand-anything` (github
`Lum1104/Understand-Anything`) — marketplace registration LEFT in place
(minimal-change; revert of the uninstall is a one-line reinstall).

**Changes applied (post-snapshot):**
- `claude plugin uninstall understand-anything` (both local-scope entries).
  **Revert:** `claude plugin install understand-anything@understand-anything`
  from `~/Projects/arhugula-v2` (marketplace registration retained).
- `claude plugin disable context7@claude-plugins-official`.
  **Revert:** `claude plugin enable context7@claude-plugins-official`.

## 3. Global MCP servers (`~/.claude.json` top-level `mcpServers`)

Pre-change: three entries — none of which any arhugula-v2 session uses:

| Name | Transport | Config (secrets redacted) |
|---|---|---|
| blender | stdio | `uvx blender-mcp` |
| Neon | http | `https://mcp.neon.tech/mcp`, `Authorization: Bearer <REDACTED — napi_… key, lives only in ~/.claude.json>` |
| pencil | stdio | `/Applications/Pencil.app/…/mcp-server-darwin-x64 --app desktop --agent claudeCodeCLI` |

Project-scope mcpServers elsewhere in `~/.claude.json` (context only, untouched):
story-portal: chat-history/github/chrome-devtools · arhugula: notebooklm ·
Projects: ruflo · ruflo: ruflo.

**Disposition: LEFT GLOBAL + noted (the plan's "unknown dest → leave + note"
fallback).** No destination project for blender/Neon/pencil is recorded anywhere
this session can verify (no candidate project under `~/Projects/` names them in
its `.mcp.json`, and guessing would relocate a live credential). Relocation —
per-project `claude mcp add` at the real destination then `claude mcp remove -s user`
globally — is deferred to the operator or a later wave with destination knowledge.
The Neon bearer token was NOT moved or copied anywhere by this unit
(`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`).

## 4. Skill-directory symlinks (`~/.claude/skills/`)

Pre-change: one symlink — `library -> /Users/robertrhu/Projects/agent-deployment-framework/skills/library`
— target **does not exist** (dangling; verified `ls` ENOENT 2026-08-10).

**Change applied (post-snapshot):** `rm ~/.claude/skills/library`.
**Revert:** `ln -s /Users/robertrhu/Projects/agent-deployment-framework/skills/library ~/.claude/skills/library`
(only meaningful if the target repo is restored).

## 5. Repo MCP registration state (context for U-CTX-02, NOT changed by this unit)

`.claude/settings.local.json`: `enableAllProjectMcpServers: true`;
`enabledMcpjsonServers: [harness-7a-scaffold, dribbble]`;
`disabledMcpjsonServers: [notebooklm, agentvibes]`. `.mcp.json` edits (remove
dribbble + harness-7a-scaffold, keep notebooklm registered-and-disabled) are
U-CTX-02 / PR-1 scope.
