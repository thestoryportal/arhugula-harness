# Wave 5 hooks — outcome status (U-HK-42 / U-HK-43 / U-HK-44)

The hook half of the R-IF-116 insights-residue program (`.harness/r-if-116-insights-residue-plan.md`,
features 1 and 4). Three units, three PRs, all merged. Every claim below was re-read at this
file's authoring HEAD against the merged sources; test counts are the scripts' own PASS lines
from a run at that HEAD, not recalled figures.

| Unit | PR | Shipped in |
|---|---|---|
| U-HK-42 — YAML parse-check branch in postedit-lint | #1198 | `tools/hooks/postedit-lint.sh`, `tools/hooks/test_postedit_lint.sh` |
| U-HK-43 — subagent lifecycle registry | #1200 | `tools/hooks/subagent-validate.sh`, `tools/hooks/test_subagent_validate.sh`, `.gitignore` |
| U-HK-44 — unreconciled sweep + locked prune | #1202 | `tools/hooks/loop-gc.sh`, `tools/hooks/test_loop_gc.sh` |

## U-HK-42 — YAML parse-check branch in postedit-lint (#1198)

**What shipped.** The PostToolUse gate at `postedit-lint.sh:34` widened from `.py`-only to
`case "$FILE" in *.py) KIND=py ;; *.yaml|*.yml) KIND=yaml ;; *) exit 0 ;; esac`. The YAML branch
(`postedit-lint.sh:43-71`) runs `list(yaml.safe_load_all(open(...)))` under `hook_bounded 10`,
preferring `"$PROJECT_DIR/.venv/bin/python"` when executable and falling back to
`uv run --quiet python` (`postedit-lint.sh:44-48`) — `uv run --with` appears nowhere, by design
(`postedit-lint.sh:10-12`). A parse error is emitted as advisory `additionalContext`
(`postedit-lint.sh:68-70`); a clean parse is silent (`postedit-lint.sh:66`).

**Beyond the unit's stated ACs.** The checker body always exits 0, so a nonzero rc can only mean
the *checker* failed — stale `.venv` without pyyaml, missing `uv`, or a `hook_bounded` timeout.
That case emits an explicit `parse-check UNAVAILABLE` advisory (`postedit-lint.sh:58-64`) rather
than taking the silent clean path, because a checker-unavailable "clean" disables the advisory
unnoticed.

**Test evidence.** `bash tools/hooks/test_postedit_lint.sh` → `PASS=19 FAIL=0`.

**Known residual (documented, accepted).** The header states the limit honestly
(`postedit-lint.sh:14-18`): the parse check catches unquoted `: ` scalars and indentation/tab
errors, but does **not** catch ` #NNN` comment-truncation — `notes: shipped in #1189` is valid
YAML whose value silently truncates at the `#`. No `#`-regex advisory was added; it is
false-positive-heavy, the same rejection class as HARDENING_PLAN D3/D13. The CI ledger checks
remain the hard gate; this hook is advisory only (`postedit-lint.sh:4-6`).

## U-HK-43 — subagent lifecycle registry (#1200)

**What shipped.** `_registry_append()` (`subagent-validate.sh:61-119`) appends one compact JSON
row `{ts, event, session, agent_id, transcript, cwd}` to `.harness/.agents-registry.jsonl`
(gitignored with its `.tmp.*` and `.lock` siblings at `.gitignore:113-115`). Three event kinds
(`subagent-validate.sh:40-44`): `start`, terminal `stop`, and nonterminal `stop_blocked`. It is
called on SubagentStart (`:122`), on the `stop_hook_active` early exit (`:131` — an accepted
terminal stop that would otherwise leave a permanent phantom unreconciled key), on both arms of
the `last_assistant_message` path (`:141`, `:144`), on the fail-open no-transcript and
unknown-shape paths (`:153`, `:160`), and on both arms of the transcript read (`:175`, `:178`).

**The locking and bounding contract.** The whole acquire→append→release runs inside ONE
`/usr/bin/python3` invocation carrying payload by argv, never stdin (`subagent-validate.sh:69-72`).
The lock is a sibling `.lock` taken FIRST; the registry fd is opened for append only inside the
locked region and never carried across U-HK-44's rename (`subagent-validate.sh:99-103`,
`:114-116`). The ~2s deadline is self-imposed because this hook has no `hook_bounded` wrapper and
the registrations carry no settings timeout (`subagent-validate.sh:53-57`); it governs lock
ACQUISITION only and is structurally inert once the lock is held (`subagent-validate.sh:112-113`).
Past the deadline the write is skipped entirely, never partial (`subagent-validate.sh:109-110`).
Rows ≥ 4000 bytes are dropped rather than risked (`subagent-validate.sh:92-95`).

**Test evidence.** `bash tools/hooks/test_subagent_validate.sh` → `43 passed, 0 failed`.

**Known residual — `stop_blocked` semantics (by design, not a defect).** A blocked stop is
recorded as `stop_blocked`, *not* as terminal `stop` (`subagent-validate.sh:43-44`, emitted at
`:141` and `:175`), because the gate emits `decision:block` and the subagent retries: only an
accepted result reconciles. The consequence is deliberate — a session that dies mid-retry stays
visible to the U-HK-44 sweep instead of being silently zeroed. The correlation key is `agent_id`
with a PARENT-FIRST transcript fallback (`.transcript_path // .agent_transcript_path`,
`subagent-validate.sh:67-68`), because SubagentStart payloads never carry
`agent_transcript_path`; child-first would file a start and its stop under unmatchable keys
(`subagent-validate.sh:45-48`). Fan-out siblings sharing one parent path is expected and is
handled by U-HK-44's per-key counting, not here.

## U-HK-44 — unreconciled sweep + locked prune (#1202)

**What shipped.** An extension of the existing `[hygiene]` SessionStart composition in
`loop-gc.sh` — no new hook. The sweep+prune is one `/usr/bin/python3` invocation
(`loop-gc.sh:61`, framing comment at `:47-57`) gated on a cheap `[ -f "$REGISTRY" ]` pre-check
(`loop-gc.sh:59-60`), with
`STALE = 30 * 60.0`, `KEEP = 7 * 86400.0`, `DEADLINE = 2.0` (`loop-gc.sh:70-72`). The clause is
appended to the composed `[hygiene]` message at `loop-gc.sh:324`, alongside the pre-existing
stale-worktree and memory clauses. Terminology is UNRECONCILED, never "orphaned" — Agent-tool
subagents are API tasks with no pid and no `kill -0`, and nothing is killed (`loop-gc.sh:48-51`).

**Sweep accounting.** Per-key chronological fold (`loop-gc.sh:137-172`): rows are processed in
append order and a `stop` only offsets `start`s that precede it, with the balance floored at zero
(`loop-gc.sh:172`) so a surplus stop cannot bank credit against a future sibling's start.
`stop_blocked` reconciles nothing (`loop-gc.sh:117`). Schema-invalid rows — a syntactically valid
object with a non-string `agent_id`/`transcript` — are demoted to malformed and skipped rather
than crashing the sweep (`loop-gc.sh:119-133`). A deficit only alarms when the recorded
transcript's mtime is older than `STALE` (`loop-gc.sh:181-186`), so live fan-outs never alarm; a
recorded-but-missing path is treated as certainly-not-live (`loop-gc.sh:183-185`).

**Prune.** A tmp-file + `os.replace` rewrite under the SAME advisory lock the U-HK-43 appender
takes (`loop-gc.sh:195-220`) — an unlocked swap races a concurrent append onto the replaced inode
and silently loses accepted events. Lock busy past the deadline → skip this tick, SessionStart is
never blocked (`loop-gc.sh:218-219`). Abandoned `.tmp.*` files left by a crashed prune are
unlinked while the lock is held (`loop-gc.sh:221-229`). Pruning is WHOLE-KEY-HISTORY
(`loop-gc.sh:236-241`): a key is dropped only when its newest parseable row is past the horizon,
so per-key lifecycle balance is preserved by construction. The sweep runs from the prune's LOCKED
re-read when the lock was acquired, else the unlocked pre-read (`loop-gc.sh:303-304`,
`loop-gc.sh:139-143`).

**Test evidence.** `bash tools/hooks/test_loop_gc.sh` → `66 passed, 0 failed`.

**Known residual — masked ordering on a shared fallback key (accepted, documented in-code).**
Recorded at `loop-gc.sh:150-160`: the mirror ordering — recorded start A, *skipped* start B, stop
B — masks A when the two share a fallback key, and no sweep-side algorithm can discriminate it.
With `agent_id` absent, sibling rows carry no per-sibling identity and no join key exists at Start
time. Rejecting count-matched stops would convert the false negative into a standing false
positive on every legitimate shared-key reconcile. The window is bounded: it requires `agent_id`
absent AND a skipped start (pathological >2s lock starvation, or the appender's 4000-byte
over-long-row drop) AND a sibling collision; blast radius is one missed advisory hygiene line,
never a hard-gate loss. **Reopen trigger: `agent_id` observed absent in real fan-out payloads.**

## Wave status

All three units are merged and their hermetic tests are auto-discovered by
`tools/codex-parity-check.sh:20` (CI-blocking). No wave-5 hook work remains open; the two
residuals above are accepted-and-documented with the reopen triggers stated, not deferred work
items. The end-to-end witnesses named in the plan's Verification section
(`.harness/r-if-116-insights-residue-plan.md:117`) are live-session observations, not CI gates,
and are not claimed here.
