---
name: roadmap-continue
description: Run one iteration of the workspace roadmap loop — the "continue" ritual — end to end. Use when the operator says "/roadmap-continue", "continue", "drive the roadmap", "next action", or otherwise asks the agent to pick up and advance the next roadmap item. Codifies the §12 loop (session-start audit → derive next action → ground empirically → implement with tests → PR) so it runs the same way every time. Do NOT use to merely report status (that is read-only) — use it to actually advance an item.
---

# roadmap-continue — one turn of the roadmap loop (U-HK-23)

The single-command form of the "continue" ritual. This skill does **not** re-state the
protocol — it **executes the canonical §12 protocol** so the recipe can never drift from
the source of truth (the §10.5 stale-carry failure mode). Read the cited sections live.

## The loop (each step is governed by a canonical section — follow it there)

1. **Session-start audit — CLAUDE.md §12.1.** Read `.harness/roadmap_status.md`; recompute
   `workspace_state_hash` (recipe at `Project_Roadmap_v1.md` §7.1); compare to the
   dashboard. **Mismatch → HALT + reconcile (§12.3).** Honor the §12.1 step-6 fixed-point
   carve-out: a one-commit lag after a terminating refresh PR is *expected*, not drift —
   silently update, do not spawn a refresh. (The SessionStart hook usually pre-injects the
   `[ROADMAP]` block; if so, trust it.)
2. **Derive the next action — `Project_Roadmap_v1.md` §4.** Take the dashboard's `## Next
   action`. If the auto-`ACTIVE` queue is empty, apply the **no-parking directive (§12.4.1)**:
   pick the highest-value forward item, do NOT stop citing "operator-owned."
3. **Ground first.** Before authoring, empirically verify the item's premise at HEAD
   (`[[r-cxa-seam-wiring-is-producer-discovery]]`, `[[grounding-reveals-claude-closeable-slice-close-honestly]]`). Grounding usually reveals a real Claude-closeable slice inside a
   nominally "gated" item — or reveals the genuine gate. Call `advisor()` before substantive
   cross-axis work (§13.1).
4. **Implement with tests.** Posture-correct edits (§11). Hermetic test per new unit;
   `just check`; out-of-family `just codex-review` to convergence (§13.1).
5. **Surface only the genuine gate.** Per §12.4.1: a real architectural/scoping decision, a
   credential, a paid-call authorization, or an irreversible action → ONE batched
   `AskUserQuestion` (§14.2). Never fire a paid call / relocate a secret unilaterally
   (`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`). Otherwise
   default to doing + reporting.
6. **Ship.** Hand off to the `ship-pr` skill (the PR + fixed-point-refresh half).

## When the queue is genuinely slice-exhausted

If grounding shows the highest-value item reaches a real gate with no buildable slice left
(creds / infra / a HELD operator decision / a dispositioned design arc), that is the
**no-parking-compliant terminal** — report the gate honestly, do not invent busywork. This
is reaching the gate after honest grounding, not parking.

## Notes

- This skill is the WHEN/HOW-TO-LOOP; the canonical text is §12 + `Project_Roadmap_v1.md`.
  If they disagree with anything written here, **the canonical sections win** — re-read them.
- Pairs with `ship-pr` (the close + refresh half) and the SessionStart roadmap hook.
