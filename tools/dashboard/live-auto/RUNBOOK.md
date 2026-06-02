# live-auto — autonomous orchestration of impeccable "live mode"

Drives the `impeccable` skill's live variant loop **with no human and no
browser**, and (critically) **with no LLM**. The variant content comes from a
pluggable producer; the smoke test uses a canned one. A real run plugs in
human-authored variants through the same hook.

This is the autonomous plumbing on top of the design skill's "live mode". It
plays both roles the live contract normally splits between a human-in-a-browser
and an agent-on-a-poll-loop.

```
tools/dashboard/live-auto/
├── orchestrator.mjs       # the loop driver (+ CLI + createCannedProducer)
├── agent-blueprint.mjs    # verbatim copy of the skill's tested runAgentLoop
│                          #   (dashboard-design/impeccable/tests/live-e2e/agent.mjs)
├── _smoke/
│   ├── seed.html          # throwaway fixture: hero <h1>, lede <p>, cta <a>
│   └── plan.mjs           # 2 moves (h1 bolder→accept v2; a colorize→accept v1)
└── RUNBOOK.md             # this file
```

---

## 0. The one gotcha that decides where you run this

**The `impeccable` skill is installed at the MAIN repo root**
(`/Users/robertrhu/Projects/arhugula-v2/.claude/skills/impeccable/`), **not in
the worktree** the task named as cwd. The deliverables live in the worktree
(`.../.claude/worktrees/r-600-pattern-bake-in-sweep/tools/dashboard/live-auto/`).

`orchestrator.mjs` bridges this automatically: it runs the cwd-sensitive
`live-*.mjs` CLIs with `cwd = projectRoot` (so `git check-ignore` + the
`.impeccable/live/config.json` resolution work against your target file's repo),
and resolves the **scripts dir** via `git rev-parse --git-common-dir` →
main-tree `.claude/skills/impeccable/scripts`. Override with `--scripts-dir=` or
`IMPECCABLE_SCRIPTS_DIR` if your install lives elsewhere.

The smoke test was run from the worktree root and passed; the scripts ran from
the main-root install. No files outside the worktree were modified except the
shared skill's read-only scripts (never written).

---

## 1. Run the loop

```bash
# From the project root that contains your target HTML (here: the worktree root).
node tools/dashboard/live-auto/orchestrator.mjs \
  --file=tools/dashboard/live-auto/_smoke/seed.html \
  --plan=tools/dashboard/live-auto/_smoke/plan.mjs
```

Flags:

| flag | meaning |
|---|---|
| `--file=PATH` | target HTML, relative to `--root` or absolute (**required**) |
| `--plan=PATH` | ESM/JSON module that `default`-exports an array of moves (**required**) |
| `--root=PATH` | project root / cwd for the cwd-sensitive CLIs (default: process cwd) |
| `--producer=PATH` | module default-exporting a `LiveAgent` (your variant producer). Default: built-in tag-aware canned producer |
| `--scripts-dir=PATH` | override the impeccable scripts dir |
| `--no-inject` | skip `live.js` injection (the file-write path does not need it) |
| `--help` | usage |

Exit code is `0` only when **every move completed AND the file ends clean** (no
variant wrappers, no carbonize markers, no injected `live.js`).

Programmatic use:

```js
import { runOrchestrator, createCannedProducer } from './orchestrator.mjs';
const result = await runOrchestrator({
  targetFile: 'public/index.html',
  plan: [ /* moves */ ],
  agent: createCannedProducer(),      // or your real producer
  projectRoot: process.cwd(),
});
// result = { ok, moves, file, clean }
```

A **move**:

```js
{
  elementId?: "hero",          // optional id hint
  classes?:   "hero-title",    // optional class hint (string or string[])
  tag?:       "h1",            // optional tag hint
  text?:      "...",           // optional disambiguating text for live-wrap
  action?:    "bolder",        // one of the 12 visual actions; default "impeccable"
  freeformPrompt?: "...",      // optional
  count?:     3,               // 1-8; default 3
  acceptVariant?: 2,           // which variant to persist; default 1
  pageUrl?:   "/",             // default "/"
}
```

The 12 valid actions: `impeccable bolder quieter distill polish typeset
colorize layout adapt animate delight overdrive`.

---

## 2. Verified event shapes (the human-replacement injection)

In autonomous mode the orchestrator POSTs the events a browser would, to the
live helper server's `POST /events` (`http://127.0.0.1:<port>/events`). Both
shapes below were validated against the skill's real
`live-event-validation.mjs` `validateEvent` — VALID; the malformed variants
listed were correctly rejected.

**generate** (the human clicking "Go"):

```json
{
  "type": "generate",
  "id": "01d6f046",
  "action": "bolder",
  "count": 3,
  "pageUrl": "/",
  "freeformPrompt": "make the hero command the eye",
  "element": {
    "id": "hero",
    "classes": ["hero-title"],
    "tagName": "h1",
    "textContent": "Autonomous live mode",
    "outerHTML": "<h1 id=\"hero\" class=\"hero-title\">Autonomous live mode</h1>"
  },
  "token": "<serverToken>"
}
```

Validator requirements: `id` matches `/^[0-9a-f]{8}$/`; `count` integer 1–8;
`action` in the 12-action enum; `element.outerHTML` non-empty; `pageUrl`
string. `token` must equal the server's token. (Insert mode — `mode:"insert"` —
is a different branch the orchestrator does not use.)

**accept** (the human picking a variant):

```json
{
  "type": "accept",
  "id": "01d6f046",
  "variantId": "2",
  "token": "<serverToken>"
}
```

Validator requirements: same `id` as the generate; `variantId` is a **string**
matching `/^[0-9]{1,3}$/` (NOT a number — `2` fails, `"2"` passes). Optional
`paramValues` must be a plain object if present (e.g.
`{"lightness":0.7,"face":"serif"}`); `live-accept.mjs` bakes these into a
`<!-- impeccable-param-values ID: {...} -->` sibling comment that carbonize
cleanup reads.

**The agent half replies on a different endpoint.** After it wraps + writes
variants it POSTs `{token, type:"done", id, file}` to `/poll`; after accept +
cleanup it POSTs `{token, type:"accept", id, data:{_acceptResult}}` to `/poll`.
The server **404s a poll reply whose `id` is not a pending/acknowledged event**
(`unknown_poll_reply_id`) — which is *why* the human-half must POST `generate`
to `/events` first (it enqueues the pending event the agent then leases and
acknowledges). This ordering is load-bearing.

---

## 3. The variant-producer hook (how a real run plugs in)

The agent half is the skill's own tested `runAgentLoop`, which calls
`agent.generateVariants(event, context)` for every pick. **That call is the
LLM-replacement seam.** A `LiveAgent`:

```js
// my-producer.mjs
export default function createProducer() {
  return {
    // event   = the generate event (element.outerHTML, action, freeformPrompt, count, ...)
    // context = { wrapTarget, wrapInfo }  — wrapInfo.styleMode is "scoped" | "astro-global-prefixed"
    async generateVariants(event, context) {
      return {
        scopedCss: '/* @scope ([data-impeccable-variant="N"]) { :scope > tag { ... } } */',
        variants: [
          { innerHtml: '<h1 class="hero-title">...</h1>', params: [ /* 0-4 knobs */ ] },
          // ... event.count variants, each ONE top-level element matching the original tag
        ],
      };
    },
    // optional: handleSteer(event, context), applyManualEdits(event, context)
  };
}
```

Run with it: `--producer=./my-producer.mjs`.

For the smoke test, the default `createCannedProducer()` (in `orchestrator.mjs`)
emits 3 trivial, distinct, **tag-aware** variants (color / weight / case) with
one param knob each across range/steps/toggle. Unlike the e2e fixture's
`createFakeAgent` (hardcoded to `<h1.hero-title>`), it reads
`event.element.tagName` so a multi-move plan over different tags stays faithful.
**It never calls an LLM and makes no network calls.** Note: the canned producer
rebuilds the element from tag+class+text, so it does not preserve `id`/`href` on
the accepted element — a real producer authoring full `innerHtml` would.

This is the model the task points at: `tests/live-e2e/agent.mjs`'s fake agent is
canned with no LLM; the LLM-backed `agents/llm-agent.mjs` slots into the same
interface and is **never run here**.

---

## 4. How the loop is sequenced (and the sync channel)

Per move, the orchestrator:

1. resolves the move's selector hints against the on-disk file (recovers tag +
   text for fidelity),
2. mints a fresh 8-hex `id`, POSTs `generate` to `/events`,
3. **waits (level-triggered file poll) until `data-impeccable-variant="1"`
   appears** in the target file — i.e. the agent has wrapped + written variants,
4. POSTs `accept` (with `variantId` as a string),
5. **waits until the file is scrubbed** (no `data-impeccable-variant=`, no
   `impeccable-carbonize-start`, no `impeccable-variants-start`) — i.e.
   `live-accept.mjs` + carbonize cleanup have run,
6. advances to the next move.

On finish: aborts the agent loop, then `live-server.mjs stop` (which runs
`live-inject.mjs --remove` to strip the `live.js` tag), then greps the final
file for any leftover markers + the injected script tag.

**Why file-poll, not SSE:** the server *does* broadcast `done`/`accept` over the
`GET /events` SSE stream (intended for the browser), and a browser-less consumer
could subscribe to it. But the file-state markers are level-triggered and
race-free, so they're the deterministic sync channel for autonomous runs.
Subscribing to SSE before the first generate is the alternative if you want
edge-triggered signaling. Either is correct; the orchestrator uses file-poll.

---

## 5. Final screenshot (documented, not required — the harness ships no headless browser)

The live harness has no bundled headless browser. To eyeball the accepted
result, serve the file and view it. Pick one:

```bash
# Serve the directory (the file-write path does NOT need this to run — only to view)
python3 -m http.server 8123 --directory tools/dashboard/live-auto/_smoke
# then open http://127.0.0.1:8123/seed.html in any browser, or claude-in-chrome.
```

```bash
# If Chrome/Chromium is on PATH, one-shot screenshot:
chrome --headless --screenshot=/tmp/seed.png --window-size=1200,800 \
  "http://127.0.0.1:8123/seed.html"
# (binary name varies: google-chrome / chromium / "Google Chrome")
```

The skill's own e2e suite uses Playwright Chromium for real-browser assertions
(`tests/live-e2e/session.mjs`) — that is a heavier path and is **not** part of
this autonomous tooling.

---

## 6. Gotchas

- **Generated-file refusal (`is-generated.mjs`).** `live-wrap.mjs` refuses to
  write into files that are **gitignored** OR carry a `@generated` /
  `GENERATED FILE` / `AUTO-GENERATED` / `DO NOT EDIT` header in the first ~300
  bytes. The smoke `seed.html` is a plain file under a tracked dir and is **not**
  gitignored, so wrap treats it as source. Untracked-but-not-ignored is fine —
  wrap does NOT require the file to be `git add`-ed. If your target *is*
  generated, wrap returns `fallback:"agent-driven"` and the deterministic path
  doesn't apply (see live.md "Handle fallback").
- **`styleMode`: scoped vs astro-global.** `live-wrap.mjs` returns
  `styleMode` (`scoped` for plain HTML/Vite/etc.; `astro-global-prefixed` for
  Astro). The canned producer authors `@scope (...)` for scoped and explicit
  `[data-impeccable-variant="N"]` prefixes for astro-global. A real producer
  must branch on `context.wrapInfo.styleMode` too.
- **Port conflicts.** `live-server.mjs` auto-detects from 8400 up. If a stale
  server holds the port, `--background` errors with "already running"; run
  `node <scripts>/live-server.mjs stop` first. The orchestrator stops its own
  server on teardown (including the `finally` on error).
- **Journal / durable recovery.** The server keeps an append-only journal under
  `.impeccable/live/sessions/`. This is **local recovery state, not project
  source** — leave it. If a run is interrupted mid-move, `live-status.mjs` /
  `live-resume.mjs` (run with cwd=projectRoot) replay unacknowledged work; the
  server requeues pending events on restart. `.impeccable/live/config.json`
  persists as project config between runs (harmless; the orchestrator rewrites
  it each run from `--file`).
- **`unknown_poll_reply_id` 404.** Means the agent tried to reply to `/poll`
  for an id the server never enqueued — i.e. the human-half didn't POST the
  `generate`/`accept` to `/events` first, or used a mismatched id. The
  orchestrator always POSTs to `/events` before the agent picks the event up, so
  this only bites if you wire a custom driver.
- **`variantId` must be a string.** `accept` with a numeric `variantId` is
  rejected by `validateEvent`. The orchestrator coerces with `String(...)`.
- **cwd sensitivity.** Always invoke with the project root as cwd (or pass
  `--root`). `git check-ignore` and config resolution are relative to cwd; the
  orchestrator runs the CLIs with `cwd = projectRoot` for you.
- **No-inject mode.** Because nothing loads the page in a browser, the file-write
  path works with `--no-inject`. Injection is left ON by default only to
  exercise the inject/remove cleanup symmetry; `--no-inject` is faster and
  equally clean.

---

## 7. Smoke-test result (recorded)

`node orchestrator.mjs --file=_smoke/seed.html --plan=_smoke/plan.mjs` →
**exit 0**, run twice (idempotent). Key proof lines:

```
[move 1/2] id=01d6f046 action=bolder target=<h1#hero.hero-title> accept=v2
  [agent] scaffolded: .../seed.html insertLine=24      # wrap landed
  [human] variants present in file                     # 3 variants written
  [agent] carbonize cleanup done on .../seed.html       # live-accept + cleanup
  [human] accept persisted + file scrubbed clean
[move 2/2] id=7623d6d4 action=colorize target=<a#cta.cta> accept=v1
  ... (same shape over a different tag)
[orchestrator] DONE moves=2/2 clean=true
```

Post-run grep for `impeccable-variants-start | impeccable-carbonize-start |
data-impeccable-variant | data-impeccable-css | live.js | localhost:8400` →
**no matches (CLEAN)**; accepted `<h1 class="hero-title">` + `<a class="cta">`
present; `live.js` removed; server stopped; port freed.

---

## 8. Real-run readiness — what's still needed

- A **real variant producer** (`--producer`) authoring full, identity-preserving
  `innerHtml` (the canned one drops `id`/`href`). It must honor `count`,
  `styleMode`, and the param budget from live.md §7.
- For a **live browser** session (human-in-the-loop hybrid), CSP allowance for
  `http://localhost:8400` may be needed (live.md "CSP detection"); irrelevant to
  the headless file-write path used here.
- Nothing else blocks an autonomous run: the loop, event shapes, sync channel,
  wrap/accept/carbonize, and teardown are all verified end-to-end.
