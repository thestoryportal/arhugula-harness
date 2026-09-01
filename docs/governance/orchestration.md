# Governance pack — orchestration + effort discipline

*Relocated BYTE-VERBATIM from Root `CLAUDE.md` §13.2–§13.5 by U-CTX-13 (R-CTX-1 Arc 5, 2026-08-11).*
*The root file keeps every heading with its number and position, plus a resolving
pointer to this file. Query this pack for the detail; do not preload it.*

---

### 13.2 The orchestration decision matrix

| Mechanism | Use when | NOT for | Cost |
|---|---|---|---|
| **Solo** (just Claude) | Mechanical / linear work (spec authoring, impl edits, test writing, back-flow docs); single-fact lookups; follow-ups dictated by tool output | High-stakes design forks; broad audits | cheapest |
| **Transcript-brief review** (Agent subagent) | Decision-forks; stuck; change-of-approach; pre-done sanity (§13.1). The **transcript-aware** half: a fresh-context Agent reviewer handed a written brief of the session — goal, fork, evidence, candidate (a `fork` subagent, which inherits the full conversation, where the venue supports it) | Mechanical steps; repeat reviews on a settled path | cheap (one subagent) |
| **`just codex-review`** (out-of-family Codex; §13.1) | **Default reviewer for a concrete diff/artifact** pre-merge — high-blast-radius changes (hooks, guards, governance docs). Decorrelated from the transcript-brief review; pairs with it, does not replace it. Subscription auth, $0 | Pure design/strategy forks with no diff yet (use the brief-reviewer/council); anything needing transcript context | cheap ($0 subscription; ~1 call/round) |
| **Council** (design-phase; §10.7 + §10.9) | A **design** decision (authoring/revising ADR/spec/plan) with a **nameable multi-domain tension** between 2+ voices (security / blast-radius / observability / cost / reliability / eval-ability / HITL-local-first). Convene **dyadic (2 voices)** by default | Phase 7 impl; single-axis decisions; tensions you can't name in advance (→ single voice + a transcript-brief review) | moderate (one model call) |
| **Adversarial reviewer** (skill; §10.9) | Pre-merge red-team of a *completed* design-substrate amendment or impl arc | In-flight authoring | moderate |
| **Workflow** (multi-agent fan-out; **opt-in** per the Workflow tool rule) | Broad parallelizable audits/sweeps; exhaustive discovery; independent verification of a high-stakes finding; large migrations | Linear/interdependent impl; mechanical edits; anything one context can hold | highest (latency + tokens) — **flag + get a green-light before deploying** |

### 13.3 Effort-level guidance for harness work

- **Normal / High is home base.** High suits the comprehensive nature of harness arcs (spec + impl + tests + clearance + roadmap). The effort knob governs the *thoroughness of the solo pass*; it does NOT change which §13.2 mechanism is appropriate.
- **Ultracode is NOT a standing default.** Most harness work is careful-but-linear, where correctness comes from §13.1 verification (cheap), not from xhigh reasoning or mandatory fan-out. Reserve ultracode for a deliberate exhaustive push the operator explicitly wants. (2026-06-01 retrospective: ultracode's *one* successful investigation workflow found 2 real gaps, but the §13.1 disciplines + the transcript-aware review caught the rest at a fraction of the latency; token cost was ~2-3% of plan limits — **latency + over-engineering are the real cost, not tokens**.)

### 13.4 Worked example — the council that was missed (2026-06-01)

The resolver Reading A-vs-B decision (identity resolver / *vacuous* floor **vs** per-server fields / *meaningful* floor) carried a nameable **C10 ⊥ C11** tension (action-safety/blast-radius wanting a real sandbox floor vs operator-loop/local-deployment wanting minimal per-server config burden) → **council-eligible** by the §10.9 nameable-tension discriminator. It was routed to a transcript-aware review + operator `AskUserQuestion` instead. Both reach a decision; the council surfaces the tension *structurally* before the operator chooses. **Rule of thumb: design decision + nameable cross-domain tension → offer a dyadic council convening (or at minimum name the voices' positions) before the operator `AskUserQuestion`.**

### 13.5 Cross-references

- Council activation + standing posture: §10.7 + §10.9. Voices at `.claude/skills/council/c1..c11` + `council-orchestrator`. Optional out-of-family **Codex decorator** on a convened tension (U-HK-19).
- Out-of-family review: `just codex-review` / `just codex-review-uncommitted` (justfile); pilot record `R-600-codex-out-of-family-review`; division-of-labor-with-advisor ratified 2026-06-03 (U-HK-18); `[[hooks-codex-pilots-decorrelation-validated]]`.
- Cite-grounding + code-side/cross-axis-seam drift instrument: the spec ↔ code ↔ CXA-seam ↔ substitution overlay at `tools/semantic_overlay/` (R-IF-112) + the `overlay-query` skill — the agent-facing `just overlay-query`/`overlay-check` surface for §13.1 (it resolves cites to code carriers + catches code↔cite/seam decay; it does NOT scan `design-substrate/**` sibling specs, so it complements — not replaces — the cross-spec `rg`). `--seam` is the cross-axis layer Understand-Anything's per-package code graph can't show (`[[overlay-query-agent-workflow]]`).
- Transcript-brief review / memory / checkpoint composition: §12.5.
- Posture (design-phase / Phase 7 / mode-agnostic): §11.
- Workflow tool opt-in rule + quality patterns: the Workflow tool description.

---

