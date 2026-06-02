# Dashboard design discipline — the 4-skill autonomous loop

*Authoritative process note for any change to the operator dashboard's **visual
design**. Established 2026-06-01. Applies to every session (mode-agnostic).*

---

## The rule

**Visual/design edits to the operator dashboard go through the 4-skill
autonomous loop — never hand-authored.** Functional/data wiring in
`tools/dashboard/generate.py` (new sections, new data series, parsing) is
authored directly; the *visual elevation* of those elements is produced by the
loop.

The split:

| Edit kind | Who does it |
|---|---|
| Data plumbing, new functional sections, parsing, charts' data | Authored directly in `generate.py` (Python) |
| Visual design — styling, hierarchy, color, motion, polish of HTML elements | The **4-skill loop** (`tools/dashboard/live-auto/`) |

## The 4 skills

The loop's variant producer (`tools/dashboard/live-auto/producer-skillchain.mjs`)
spawns a headless, **read-only** `claude` agent (tools: `Skill,Read,Grep,Glob`)
that invokes these four installed skills for design guidance, then authors
in-identity elevation variants:

1. **`impeccable`** — applies the named visual action discipline (`bolder`,
   `quieter`, `distill`, `polish`, `typeset`, `colorize`, `layout`, `adapt`,
   `animate`, `delight`, `overdrive`).
2. **`design-taste-frontend`** — anti-slop "tells".
3. **`ui-ux-pro-max`** — accessibility + hierarchy + status-not-by-color-alone.
4. **`frontend-design`** — intentional aesthetic direction.

The agent reuses the element's existing CSS classes verbatim (carbonize-safe);
it invents no new class names. The four skills are the **installed** ones at
`~/.claude/skills`; the copies under `dashboard-design/*-skill/` are local
reference clones only and are **gitignored** (≈88MB — not vendored).

## How to run it

The loop is the `impeccable` skill's autonomous "live mode" orchestration. Full
how-to, flags, event shapes, and gotchas: **`tools/dashboard/live-auto/RUNBOOK.md`**.

```bash
# Genuine 4-skill run (spawns headless claude agents = paid Anthropic calls).
# Invoke through `just` so dotenv-load supplies the claude CLI its Anthropic
# creds — never source .env directly (workspace memory [[secrets-via-just-recipe]]).
node tools/dashboard/live-auto/orchestrator.mjs \
  --file=<target.html> --plan=<plan.mjs> \
  --producer=tools/dashboard/live-auto/producer-skillchain.mjs
```

The producer expects a clean skills-only workspace (`SKILLCHAIN_WS`) that
symlinks just the 4 design skills — see `producer-skillchain.mjs` header. A
wrapper `just` recipe is added the first time the loop is run end-to-end.

- **Cost.** Each loop move spawns one `claude` agent (`claude-sonnet-4-6`,
  ~$0.035+ baseline). Paid calls require explicit operator approval per
  workspace memory `[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`.
- **No-LLM smoke.** `orchestrator.mjs` with the default canned producer exercises
  the orchestration without any LLM/network (see RUNBOOK §7).

## The live dashboard

A persistent local copy runs at **http://localhost:8137/** (launchd:
`org.thestoryportal.harness-dashboard`), regenerating from live workspace data on
every page load. It is owned by the launchd service — do **not** start a second
server on 8137. After a new `generate.py` merges to `main`, re-point the service
(`~/.harness-dashboard/`) at it. See workspace memory
`[[local-dashboard-launchd-service]]`.

## Canonical design

The committed canonical design is **Almanac Noir / instrument ledger** (candidate
B), emitted by `tools/dashboard/generate.py`. Its design tokens (dark `--ground`,
`--bone` text, single `--amber` signal accent, `--ember` alerts-only, hairline
rules, 2px radius, Big Shoulders Display / IBM Plex Sans / JetBrains Mono) live in
the generator's `:root` block. **A dedicated Almanac Noir design-system reference
is still owed** — author it via the discipline above (or as a faithful
reverse-description of the generator's tokens) rather than hand-designing anew.

The prior **Mustard Editorial** system (light paper ground, mustard offset
shadows, serif display) is **superseded** and is not committed here. The
`candidates/` A/B exploration outputs are gitignored (regenerable loop outputs).
