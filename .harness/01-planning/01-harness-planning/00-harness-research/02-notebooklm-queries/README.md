# Research Notebooks — NotebookLM-Extracted Briefs

13 markdown files extracted from the harness engineering NotebookLM (Drive folder `1-4JA3NrKAp9SaYruPH-82mavg4oWUhm3`, source: `https://notebooklm.google.com/notebook/57b8d946-830c-42dd-b201-ac117a8af951`). These are **Phase 2 priming substrate** authored 2026-05-09 — predating the design-phase corpus crystallization into ADRs + ADD + PRD + per-axis specs.

The corpus is **derivative-redundant for settled design decisions** but **high-value for external-authority grounding** when a voice's position needs anchoring beyond intra-spec authority. Use for council voice external-authority citations + Phase 7 implementation grounding (production failure modes from real systems: LangGraph, Temporal, OpenAI Agents SDK, Anthropic Multi-Agent Research, Cognition Devin, kilocode, openrig, ICM, Meta-Harness, etc.) + adversarial reviewer's external-canon mode.

---

## File inventory

| File | Scope | Maps to canonical |
|---|---|---|
| `brainstorm-synthesis-for-phase-2.md` | Phase 2 persona-surfacing synthesis (36KB master doc — F1-F5 + T1-T4 + per-axis convergence/divergence + 23-question architect scaffold) | ADD v1.3 + Phase 2 persona work + workflow §0 selective-loading discipline |
| `filesystem-as-universal-substrate.md` | Stanford Meta-Harness + ICM convergence on filesystem-as-substrate | ADR-F2 (filesystem + git substrate) |
| `architectural-primitives-tools-mcp-skills.md` | 3-primitive decomposition (in-process / MCP / Skills) with process boundary + trust gradient + context economics | ADR-D3 + AS spec C-AS-01..C-AS-15 |
| `gating-and-evaluation-architecture.md` | In-loop gating vs out-of-loop Husain-loop eval; TPR/TNR/κ alignment floors; judge-base-model collision | CP spec C-CP-19/20 (HITL palette) + OD spec validator/eval surfaces + C5/C8 voices |
| `architectural-tensions-multi-tenant-deployment.md` | T3 per-task vs per-company deployment unit; Paperclip vs kilocode honest absorption | ADR-D5 cross-deployment monotonicity + Phase 2 persona |
| `three-control-knobs-cost-optimization.md` | Model routing + prompt caching + Batch API; CARGO/xRouter empirical metrics | ADR-D6 cost-attribution + C6/C7 voices |
| `five-tier-durability-model.md` | filesystem / git / checkpoints / vector store / ledger tier mapping across studied harnesses | IS spec C-IS-02 (5-tier durability) + ADR-F2 |
| `architectural-blueprints-hitl.md` | 3-tier HITL granularity (coarse / medium / fine) with integration cost and workload tolerances | ADR-D5 v1.4 HITL palette + CP spec §17 + C11 voice |
| `architectural-personas.md` | Solo / small-team / enterprise persona constraints + harness fit + binding strength | Phase 2 persona work + ADR-D2 |
| `engineering-operational-discipline.md` | Why most harnesses underweight OD; 7 commitments of production-grade-from-day-one | OD axis (whole) + ADD v1.3 §operational discipline |
| `architecting-portable-multi-llm-harnesses.md` | Brain/Hands/Session abstraction tax; F1-F5 trace through deployment-surface flexibility | ADR-F1 + ADR-D2 + Phase 6.5 deployment surface |
| `architectural-tensions-and-tradeoffs.md` | T1-T4 catalog tensions + honest absorption vs displacement (12-Factor / Anthropic / ICM / MCP) | T-perm-1/2/3 council framing + Workflow §4.3 back-flow |
| `architectural-topologies-multi-agent-systems.md` | 5 topology classes (orchestrator-worker / decentralized handoff / hierarchical / evaluator-optimizer / single-agent ReAct) with workload predictors | ADR-D4 v1.1 TopologyPattern 6-class enum + CP-AL-1 sub-agent boundary |

---

## Voice → notebook mapping (council orchestrator quick-reference)

When a council voice needs external-authority citation during deliberation, prefer these per-voice anchors over the larger `research/agent-harness-eng-research-cluster-N-*.md` files (which are deep dives ~600 lines each; the notebooks/ briefs are 5-7KB concentrated synthesis layers).

| Voice | Primary notebook(s) | Use when |
|---|---|---|
| **C1 — Orchestration & Control** | `architectural-topologies-multi-agent-systems.md` | Topology choice; sub-agent boundary; fan-out vs serial |
| **C2 — Context Engineering** | `filesystem-as-universal-substrate.md` + `five-tier-durability-model.md` §"Memory tier architectures" | Within-turn context + prompt caching breakpoints |
| **C3 — State, Memory & Persistence** | `five-tier-durability-model.md` + `filesystem-as-universal-substrate.md` | Durable state tier choice; hash-chain ledger; checkpoint cadence |
| **C4 — Tools & Integration** | `architectural-primitives-tools-mcp-skills.md` | Tool contracts; MCP integration; Skills vs MCP boundary |
| **C5 — Validation Contract** | `gating-and-evaluation-architecture.md` §"In-loop gating" | Gate shape; fail-class taxonomy; evaluator-optimizer |
| **C6 — Model Routing** | `three-control-knobs-cost-optimization.md` §"Model routing" | Routing strategy; provider portability; cost knobs |
| **C7 — Observability** | `engineering-operational-discipline.md` §"OTel observability" + `three-control-knobs-cost-optimization.md` §"Prompt caching" | Span schema; cost attribution; cardinality |
| **C8 — Eval Engineer** | `gating-and-evaluation-architecture.md` §"Husain loop" + §"Meta-eval" | Eval methodology; judge alignment; held-out test sets |
| **C9 — Reliability & Recovery** | `engineering-operational-discipline.md` §"Circuit breakers" + `architecting-portable-multi-llm-harnesses.md` §"F3" | Retry/backoff; breaker; fallback timing |
| **C10 — Action Safety & Blast Radius** | `engineering-operational-discipline.md` §"Sandbox isolation" + `architectural-primitives-tools-mcp-skills.md` §"Trust gradient" | Blast radius; sandbox tier; trust gradient |
| **C11 — Operator Loop & Local Deployment** | `architectural-blueprints-hitl.md` + `architectural-personas.md` | HITL primitive granularity; local-first; operator-availability assumptions |

**Cross-cutting / multi-voice references:**

- `brainstorm-synthesis-for-phase-2.md` — master synthesis; primary source for permanent tensions T1-T4 framing + F1-F5 foundational decisions
- `architectural-tensions-and-tradeoffs.md` — honest absorption vs displacement patterns (relevant to all permanent-tension deliberations)
- `architectural-personas.md` — persona binding strength (relevant to Phase 2 persona work + any persona-gated decision)

---

## Citation discipline

When citing these notebooks during deliberation:

1. **Cite the notebook file + section** — e.g., `research/notebooks/five-tier-durability-model.md §"Ledger (Event Sourced) Tier"`. Section anchors are stable.
2. **Distinguish from internal authority** — these are external-authority anchors (industry/academia synthesis). Internal authority lives at `design-substrate/` (ADRs / ADD / PRD / specs / plans). Voices should be explicit about which they're invoking.
3. **Confidence cap = MODERATE** — per the Brainstorm Synthesis provenance footer: "This synthesis is NotebookLM's reading of the corpus, not direct corpus extraction. Specific harness claims should be verified against the actual primary research artifacts before becoming load-bearing in any foundational ADR."
4. **Probe-first discipline applies** — if a voice asserts "the canonical reference says X" and the assertion is contested, the orchestrator MUST grep the cited file (or escalate to the underlying NotebookLM corpus) before resolving the tension. Council surfaces, primary sources decide.

---

## Underlying NotebookLM corpus

The 13 briefs here are extractions from a larger NotebookLM project at:

**URL:** `https://notebooklm.google.com/notebook/57b8d946-830c-42dd-b201-ac117a8af951`

The NotebookLM contains:
- The harness engineering project's primary research material (Sessions 1–3, Clusters 1–5 V2, Triaged Source Inventory, Pattern Reference Catalog v1.0) — same as `research/agent-harness-eng-research-*.md`
- **28 supplemental URL-scrape topical compilations** (1140 successful scrapes across topics `01_Anthropic_Claude_Core` through `28_Misc_Tools_Resources`) — primary-source material NOT in this workspace's `research/` corpus

**On-demand invocation criterion:** the static extracts here cover the high-frequency synthesis-layer need. Reserve interactive NotebookLM MCP query for **specific novel-question events**:

- Workflow v1.14+ revision arc (Phase 7 → Phase 8 retirement, cross-cutting concern application against canonical SDLC)
- `agentic-engineeriing-sdlc.md` cross-reference work (currently at `research/agentic-engineeriing-sdlc.md`)
- Adversarial reviewer external-canon mode flagging a divergence that the static `research/` + `research/notebooks/` corpus can't adjudicate
- New harness instances that ship after 2026-05-09 source-cutoff (current state-of-the-art question)

NotebookLM MCP setup is NOT installed at this workspace as of 2026-05-31. Setup is deferred until the on-demand criterion above is hit.
