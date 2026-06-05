# Post-Build Architecture Exploration — Dedicated Agents, Single-File Agents, Eval-Writers, and Autoresearch

**Date:** 2026-06-04
**Provenance:** Synthesis of the design discussion that followed the `optimize-claude-md` skill build (one session). This captures reasoning and decisions-pending — it is a brainstorming record, not a spec.
**Anchors:** the extended `optimize-claude-md` skill lives on branch `skill/optimize-claude-md-portfolio` (commit `a51d751`, **unmerged**); operational learnings are in memory `skill-creator-eval-harness-caveats`.

---

## 0. What prompted this

We extended `optimize-claude-md` from an 81-line single-file reviewer into a portfolio-aware, dual-mode, script-backed skill: `measure.py` (context-cost + bloat map), `check_pointers.py` (pointer-resolution gate with a `--baseline` diff mode), three references (ICM budgets, load-bearing keep-list, relocation pattern), and an eval suite. It graded **15/15 behavioral** (vs 14/15 for the pre-extension baseline) and **10/10 triggering specificity / 8/10 recall**.

The conversation then turned from *what we built* to *how a thing like this should be operated and evaluated* — and every branch kept landing on the same through-line (§6).

---

## 1. A dedicated agent to *operate* the skill

**Framing:** the **skill** is the *how* (discipline + scripts); a **dedicated agent** is the *who/where it runs*, with enforcement. The real question is what the agent layer adds that a main-thread Skill-tool invocation structurally **can't**.

**Three strong value axes:**

1. **Context quarantine — almost on-the-nose here.** A context-*optimization* skill that runs in the main conversation (load SKILL.md + references + `measure.py` output + an 86K-token CLAUDE.md + the relocation work) pays the exact tax it exists to remove. A dedicated agent does that in its own window and returns only the proposed diff + a summary. It eats its own dog food.
2. **Permission-hardened scope-guard.** The skill's core risk is *silent governance drift*. A dedicated agent can carry **enforced** boundaries (deny writes under `design-substrate/`, no merge/push) — turning the most dangerous invariant from "the prose says don't" into "the harness won't let it."
3. **The schedulable unit.** You can't cron the main conversation; you can have a SessionEnd hook / `/schedule` spawn a named agent for the maintenance sweep. For unattended runs it must write via Bash (worktree-pin safety) and checkpoint durably/incrementally.

**The softer axis (behavioral fidelity):** an agent that *adopts* the SKILL.md as its identity follows the discipline more faithfully than the core agent reference-reading it mid-conversation. Real — but this session showed a well-prompted *generic* subagent already gets most of it. The dedicated agent's marginal value here is **standardization** (stop re-writing the invocation prompt) + forceful guardrails, not a transformed output.

**When it is NOT worth it:** rare, supervised, one-off optimizations — a generic subagent + the skill is enough. Cost to watch: a second source of truth that drifts from SKILL.md (ironic for a drift-fighting skill). Mitigation: keep the agent prompt *thin*; defer all content to the skill.

### Under the hood (native Claude Code subagent)

- **One file:** `.claude/agents/<name>.md` — YAML frontmatter (`name`, `description`, `tools`, `model`) + a system-prompt body. **No accompanying folder** — the *skill* is the folder; the agent references it by path and `Read`s it at runtime. Bundling a copy re-creates the drift the skill fights.
- **What's in the file:** identity + an *adopt-the-skill* pointer (`Read .claude/skills/optimize-claude-md/SKILL.md and follow it`) + the non-negotiable invariants + the deliverable shape (proposed diff/PR, propose-don't-dispose). ~40 lines.
- **Enforcement split (important):** frontmatter `tools:` only restricts the tool **set** (it can't say "Bash but not `git push`"). The *enforced* path/command guards live in **`settings.json` → `permissions.deny`** (e.g. `Write(./design-substrate/**)`, `Bash(git push:*)`, `Bash(git merge:*)`) and/or a **PreToolUse hook**. The agent file alone is advisory, like SKILL.md.
- **Folder vs file:** agent = single file; its "context folder" = the existing skill. The **council** (`c1…c11/` + `council-orchestrator/`) is the example of *when you bundle folders* — multiple distinct personas each needing their own context. A single skill-operator points, it doesn't bundle.

**Two registries in this repo:** native `.claude/agents/` (clean, harness-recognized — but **none exist yet**) vs. the custom **org-role / `agent-loader`** format the existing `~/.claude/agents/*.md` use (`<!-- agent-id -->` + Department/Ownership/Interfaces). Pick one; they're different file shapes.

---

## 2. Single-file agents (SFA, IndyDevDan / Disler) as a deployment target

**Strong candidate — and a cleaner fit than most**, because the skill already pre-decomposes into the SFA-ideal shape:

| Part | Nature | Built? |
|---|---|---|
| Find the bloat (`measure.py`) | pure computation | ✅ |
| Verify pointers (`check_pointers.py`) | pure computation | ✅ |
| Classify load-bearing vs relocatable; relocate; tighten prose | **judgment → one scoped LLM call** | the prompt-able core |
| Gate: refuse if a pointer broke or a keep-list rule vanished | pure computation | ✅ (the scripts) |
| Emit diff / branch, never merge | deterministic | trivial |

**The "deterministic" nuance:** the *harness* is deterministic; the *relocation* is an LLM call (non-deterministic). Determinism lives in the **gates**, not the generation — same input → not the same bytes, but the same *guarantees* (pointers resolve, guardrails present, or it refuses). A **code-enforced gate is stronger than a prose invariant**.

**Factual correction made during the discussion:** an SFA does **not** require the metered Anthropic API. The judgment slice needs *a model*, which can be:
- `claude -p` (subscription, **no key** — we used exactly this for the triggering tests),
- a **local** model (Ollama / llama.cpp),
- the **Codex** CLI (ChatGPT subscription, $0),
- or the **SDK + key** — Disler's published form, which serves **portability** (a standalone file that runs anywhere), not an inherent requirement.

And the deterministic core needs **no model at all** — it runs like any script. ("Requires the API" was an overstatement generalized wrongly from `run_loop`, which genuinely `import anthropic`s.)

**The menu for this optimizer:**
- **Pure script, no model** — deterministic measure + structural relocation + verify; defer subtle judgment to review. Not even an "agent."
- **Single-file agent, subscription** — one `claude -p` judgment call, wrapped by the existing scripts + the refuse-on-broken-pointer gate. No metered key.
- **Single-file agent, SDK + key** — portable form, only if running *outside* the Claude Code environment.

**SFA vs in-session subagent (not either/or):**
- **SFA** = unattended, composable, reproducible, code-gated, schedulable — the natural home for the **scheduled-maintenance sweep**. Can shell out to Codex for decorrelated review. *Costs:* loses the transcript-aware `advisor`; thinner ambient context (best for *well-understood* files — per-axis `§4` sweeps, the known `§2` relocation).
- **Subagent** = interactive, judgment-rich, subscription-run, `advisor` + Codex in the loop — for novel/subtle passes.
- Both reuse `measure.py` and `check_pointers.py` unchanged.

---

## 3. Evaluating an SFA vs a semantic skill/agent

**Behavioral evals port — and get cleaner.** An SFA is a program with a contract (`uv run optimize_claude_md.py --file X --diff` → diff + exit code):
- The existing `evals.json` assertions already grade *the diff*; they apply verbatim, and the harness *simplifies* (the SFA emits the diff by contract; no subagent orchestration to capture output).
- The deterministic spine becomes **unit-testable** (pytest, no model, no key, CI-gating) — a rigor a prose skill can't reach.
- The LLM-judgment slice still has run-to-run variance → run N times, look at pass-rate ± σ (the *same* benchmark methodology).

**Triggering eval: N/A — and that's a feature.** "Does it auto-activate on the right query / stay silent on near-misses" only exists for *model-selected* targets (skills, agents, tools, MCP-tools). An SFA is **invoked explicitly** (you / cron / CI / another agent), so the entire probabilistic-activation dimension — and the whole `run_eval`/`run_loop` harness pain — **disappears**. (If a *caller-agent* decides whether to invoke the SFA, that's the caller's selection eval, one layer up.)

**Net shift:** skill eval = *triggering* + *behavioral-output* + *prose-adherence*. SFA eval = *behavioral-output* + *gate-correctness* (deterministic unit tests) + **no triggering**. Enforced-by-code beats asked-by-prose → a *more honest* eval substrate.

---

## 4. A meta eval-writer across target types (skills, agents, SFAs, prompts, tools, MCP)

**Reframe:** "write evals for X" is not one task — it's **one shared design backbone + a per-target-type harness.** What actually varies:
1. **The invocation contract** — how you run + detect behavior (Skill-tool + stream-json marker for a skill; Task-tool for an agent; subprocess for an SFA; API/CLI for a prompt; a tool-use scenario for a tool; an MCP client for a server).
2. **Whether there's a *selection* dimension** — skills/agents/tools/MCP-tools are model-selected (need a triggering eval); SFAs/prompts are invoked (that dimension vanishes).

Everything else — failure-mode-first cases, mechanical-vs-judgment assertions, run-N-times, aggregate, render — is shared and transferable.

**Feasibility (honestly graded):**
- **Design brain + scoring + benchmark + viewer: highly feasible — the prototype exists.** `skill-creator` *is* this for one target type (a semantic SKILL.md design discipline calling deterministic scripts).
- **Per-target adapters: the long pole**, trivial → heavy: SFA-runner (subprocess) ≈ trivial; prompt-runner ≈ easy (and largely solved by **promptfoo**); skill-runner ≈ fiddly (the real-install + marker-detection gotchas we hit); agent-runner ≈ moderate; tool-runner ≈ moderate; **MCP ≈ heaviest** (protocol tests + tool-use). The design brain works day one; execution lights up per adapter.
- **The real ceiling on "highly effective" is assertion quality, not plumbing.** The failure mode is shallow, non-discriminating, happy-path-biased assertions (the circularity risk). "Highly effective" requires baked-in anti-shallowness: failure-mode-first, an adversarial case per target, mechanical-over-judge assertions, and a **decorrelated review of the eval set itself** (Codex / human sign-off).

**Semantic or SFA? — layered, and it's the same determinism line:**
- **DESIGN** (classify the contract → pick the eval shape → generate cases + assertions → red-team → sign-off): judgment, context-rich, open-ended per-target, interactive → **semantic** (skill/agent). An SFA is a fixed program; it can't do open-ended per-target eval *design*.
- **EXECUTION** (run the adapter, score, aggregate, render): deterministic, reusable, CI → **SFA/script** adapters.
- **Brain semantic, hands SFA.** If forced to name *the agent* as one, it's **semantic** — the irreducible value is judgment across heterogeneous targets — but it's only as good as the adapters it can call.

**Opening move that makes it work:** "**classify the target's invocation + output contract first**" — that single step lets one agent write *appropriate* evals across all target types instead of one-size-fits-none.

**Pragmatic accelerators:** generalize `skill-creator`; **emit existing artifacts** (promptfoo YAML for prompts/tools, pytest + subprocess for SFA cores, the marker-harness for skills, Task-capture for agents, an MCP client for servers) rather than a new framework; build adapters incrementally; route the writer's *own* eval set through Codex + a human gate (anti-circularity).

---

## 5. Autoresearch (Karpathy) — where the self-improving loop pays off

**What it actually is (grounded in the repo):** `karpathy/autoresearch` (March 2026) is **nanochat-specific** — an agent edits one file (`train.py`), runs a fixed **5-minute** experiment, scores **`val_bpb`** (validation bits-per-byte; vocab-independent so architectures compare fairly), **keeps-if-improved / `git reset`-if-not**, ~100 experiments overnight. Open-ended search in *code space*, not parameter space. The repo itself is LLM-training-specific; the "everyone's using it for skills/prompts/A-B" part is the **community lifting the loop pattern**.

**Where it's useful = its preconditions (the loop is only as good as the weakest one):**
1. A **fast** fitness signal — score in seconds/minutes (throughput *is* the value).
2. A **trustworthy** metric — the number tracks what you actually want (the linchpin).
3. A **fair/comparable** metric — normalized so heterogeneous candidates compare apples-to-apples.
4. **Cheap, reliable rollback** — most experiments fail; the pattern is *volume × cheap-discard*.
5. A **bounded-but-expressive** search space.

**Useful where these hold:** model training; **prompt optimization** (`run_loop` *is* this); skill/agent tuning; **A/B content** (CTR/engagement); hyperparameter/config/perf tuning; codegen-against-a-test-suite; RL-with-a-reward.

**Useless or dangerous where they fail:** evaluation needs human judgment or hours (throughput dies); the metric is a weak proxy → **Goodhart** (the loop self-improves toward *gaming* it); changes are expensive/irreversible (cheap-discard economics break); the search is unbounded/unsafe.

**The linchpin insight:** *the fitness function is the most important artifact in the system; the loop's ceiling **is** the quality of its eval.*

**Connections back to what we built:**
- **`run_loop`** is an autoresearch-shaped loop (search description space; fitness = held-out triggering recall/specificity; keep best by test score). Its failure this session was a **broken fitness harness** (`run_eval` reporting 0) — the *canonical* autoresearch failure mode.
- **`optimize-claude-md`** is a **constrained** variant: it can't just maximize "fewer tokens" because the real objective has a hard constraint (no governance drift). It keeps a change only if **tokens↓ AND the gate passes** — the gate is what makes a self-editing loop safe to run unattended.
- The **eval-writer** (§4) is therefore the *highest-leverage* meta-tool: if fitness functions are the bottleneck, an agent that reliably writes **non-shallow** ones is the multiplier — and the circularity risk becomes *more* dangerous at loop scale (a loop optimizing a shallow eval relentlessly climbs toward gaming it).

---

## 6. The through-line

Every branch converged on the same shape:

> **propose a change → measure it → keep-or-discard via a *trustworthy gate* → repeat.**

And the same decomposition recurred everywhere — **the determinism line**: put determinism in the scaffolding and the *gates*, confine the LLM to the irreducible judgment slice, and **verify the output**. It shows up in `optimize-claude-md` (deterministic measure/verify + fuzzy relocation), in SFA design, in the eval-writer (deterministic adapters + semantic design brain), and in autoresearch (deterministic fitness + open-ended hypothesis).

**The hard part is never the loop** (autoresearch is ~600 lines; `run_loop` is small) — **it's the fitness/eval function you'd trust to run 100× while you sleep.** Good evals are simultaneously the bottleneck and the multiplier. The meta-investment that pays off across all of the above is: build trustworthy, non-shallow, *contract-appropriate* fitness/eval functions — and the agent that writes them — with anti-circularity baked in.

---

## 7. Decisions pending / candidate next builds

- [ ] **Adopt the skill:** merge `skill/optimize-claude-md-portfolio` (`a51d751`) into main (operator action — not done).
- [ ] **Dedicated operator agent?** If yes: which registry — native `.claude/agents/` (clean) or the `agent-loader` org-role format? Pair with `settings.json` deny-rules + a PreToolUse hook for enforced scope.
- [ ] **SFA form of the optimizer?** Subscription `claude -p`, hard-gated, `--apply` propose-only (diff/branch, never merge) so it inherits the never-dispose invariant. (No paid key required.)
- [ ] **Meta eval-writer?** Semantic orchestrator + adapter library; start with the easy adapters (SFA + prompt/promptfoo); "classify the contract first" as the opening move; route its own eval set through Codex + human sign-off.
- [ ] **Autoresearch-style tuning loop** for skills/prompts — *gated on first building a fitness harness you trust* (the `run_eval` lesson: a broken metric makes the whole loop worthless or harmful).

---

## Sources

- [karpathy/autoresearch (GitHub)](https://github.com/karpathy/autoresearch)
- [autoresearch: Karpathy's Blueprint for Agents That Improve Themselves — mager.co](https://www.mager.co/blog/2026-03-14-autoresearch-pattern/)
- [How I Built a Skill That Makes All My Other Skills Better (Using Karpathy's Autoresearch) — aimaker](https://aimaker.substack.com/p/how-i-built-skill-improves-all-skills-karpathy-autoresearch-loop)
- ['The Karpathy Loop': 700 experiments, 2 days — Fortune](https://fortune.com/2026/03/17/andrej-karpathy-loop-autonomous-ai-agents-future/)
