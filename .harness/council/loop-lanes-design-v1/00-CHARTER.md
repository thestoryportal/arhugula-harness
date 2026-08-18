# Charter — Council over `HARNESS-LOOP-AND-LANES-DESIGN-v1`

**Opened** 2026-08-17 · **Spec** `.harness/council/council-workflow.harness-aware.yaml` (v1,
harness-layer-aware) · **Posture** design-phase companion, additive-only (CLAUDE.md §11, X-AL-3).

**Artifact under deliberation:**
`~/.gstack/projects/arhugula-v2/research/HARNESS-LOOP-AND-LANES-DESIGN-v1.md` — the consolidated
authoritative design merging the loop-engineering arc (`loop-eng-2026-08-16/`) and the parallel
agents/worktrees arc (`parallel-lanes-2026-08-17/`), with this harness codebase as grounding.

---

## 1. Nameable-tension gate — PASS

Per `pre_convening.nameable_tension_gate`, a council convenes only if a cross-domain tension can be
**named in advance**. It can:

> **SPINE-TENSION: evidence-gate ⊥ operator-mandate.**
>
> The design defers *all* 4-lane machinery behind ≥3 manual pilot runs and the O1 probe, resting on
> (a) the workspace's own rule at `two-lane/SKILL.md:140-142` — *"Follow-on orchestration is
> registered only after ≥3 manual pilot runs surface a named recurring pain"* — and (b) the
> counterfactual-first discipline (build nothing whose necessity an unrun experiment would settle).
>
> Against that: the operator's requirement is a **fixed, top-down, ratified mandate** for 4 lanes,
> and CLAUDE.md §12.4.1 states operator-labelled items are Claude-driven and must not be *parked*.
>
> **Does deferring honor the requirement, or park it?**

This is genuinely cross-domain, not a single voice's call:
- **C1 / C8** hold the evidence-first position (topology needs the counterfactual; a claim without a
  run baseline is unlicensed).
- **C11** holds the operator's stated need and the anti-parking discipline.
- **C10** argues *toward* deferral from the opposite direction (blast radius of 4 concurrent writers
  with ~0 detections).
- **C5** notes the contracts that would license the faster path are unwritten drafts.
- **C3** holds the live defect set that is real *now*, at N=1, independent of the dispute.

Secondary tensions carried into the round:
- **T2 — build-parallel/land-serial framing.** Honest architecture, or an implicit redefinition of
  "parallel" that should be surfaced to the operator explicitly? (C1 ⊥ C11)
- **T3 — where the reservation's durable authority lives**, and whether it inherits the same
  cross-latency hazard it fixes. (C3 ⊥ C9)
- **T4 — branch protection on `main`** (currently none; verified twice). A cheap partial base fence,
  but a posture change. (C10 ⊥ C4/C5)
- **T5 — detection debt.** 19 named failure modes, ~0 emitted signals. Does Phase 0 ship without
  them? (C7 ⊥ C1)

## 2. Layer identification

Multi-axis. The artifact touches:

| Layer | Why |
|---|---|
| **IS** | the ledger/queue/reservation defect set; `loop_status.md` state split; record extension |
| **CP** | lease protocol vs coordinator; merge-door topology; reviewer failover; HITL routing |
| **OD** | detections, gate semantics, operator surface, cost/observability |

## 3. Roster (per `layer_voice_map` + `cross_cutting`)

**Primaries (3 — genuine domain center, within the 2–3 cap):**
- **C1** orchestration / lifecycle — owns the topology and sequencing claims
- **C3** state / memory / persistence — owns the ledger + reservation, the concrete substance
- **C8** eval — **PROMOTED to primary.** The spine is *what evidence licenses building*, squarely
  eval's domain. This mirrors the lived precedent, which promoted C8 "because the fresh research
  was eval-gates."

**Consultants (5, selected by seam relevance):** C9 reliability · C5 validation/contract ·
C10 blast radius · C11 operator loop · C7 observability.

**Cap override declared:** 8 voices vs the nominal 5. Justification — the artifact spans three axes
and carries **five open operator decisions**, each owned by a different voice (failover→C6/C9,
TTL→C11, pilot-gate→C1/C8, gate-coalescing→C11, branch protection→C10). Running fewer would leave a
ratified open decision unowned. (Lived precedent ran 7, operator-justified.)

**CCR — cross-cutting concerns → owner:** security/blast-radius→C10 · observability→C7 ·
reliability/recovery→C9 · eval-ability→C8 · HITL/local-first→C11 · validation-contract→C5 ·
orchestration/lifecycle→C1.

**Not convened:** C2 (context engineering), C4 (tools), C6 (model routing) — each contributed to the
lanes arc and their findings are already folded into the artifact; no *new* nameable tension for
them here. C6's reviewer-concurrency finding is carried as a standing input to C9/C5 rather than a
seat.

## 4. HIL posture for this run

The operator has authorized autonomous running. Per `hil_gates` + the prose companion §4, the
full-council halt gates (E1, E2b/E3b consolidated) are **waived**, and the run **still stops** at
destructive / irreversible / outward-facing boundaries — concretely: **no commit and no PR without
explicit operator direction.** All other stages proceed.

**Reorder taken:** the `consolidated_reconcile` option — E2b + E3b collapse into ONE reconcile after
adversarial + Codex + advisor input is gathered. Preserves reconcile-to-zero, fewer convenings.

## 5. Ledger tree

```
00-CHARTER.md            ← this file
01-council/contributions/    A1 primaries (verbatim)
01-council/reactions/        A2 consultants (verbatim)
01-council/debate/           B cross-read seam debate
02-adversarial/              E2 red-team
03-codex-advisor/            E3 decorrelated evaluators
04-reconciliation/           consolidated reconcile-to-zero
DELIVERABLE.md               E4 gate outcome → v2 + change-note
```

Orchestrator writes the ledger from returned agent markdown (no parallel-write races). Fan-out is
gentle: waves of ≤3 concurrent agents.
