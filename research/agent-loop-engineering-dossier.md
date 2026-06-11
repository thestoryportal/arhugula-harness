# Agent Loop Engineering — Reference Dossier

> **Purpose.** A technical, reusable reference on the *core agentic iteration loop* (perceive → decide → act → observe → terminate) for the loop-engineering phase of the harness build. Adjacent concerns owned by council voices (orchestration topology, sub-agent boundaries, HITL placement, retry/breaker mechanics, validation gates, routing, observability spans, state persistence, trust/blast-radius) are referenced only where they touch the loop directly — they are **not** re-spec'd here.
>
> **Provenance tiers** (every claim is tagged):
> - **[V]** — adversarially verified by the deep-research workflow (3-vote, ≥2/3 to kill); primary-sourced, mostly 3-0 unanimous.
> - **[P]** — read this session from a primary/official source (URL in Sources); not run through the 3-vote gate but quoted from the source.
> - **[K]** — author's reconstruction of control-flow *shape* for pseudocode. Pseudocode is **illustrative shape, not verbatim API**. No threshold, buffer size, or repo symbol appears in [K] text unless it traces to a [V]/[P] source.
> - **[uncertain]** — named in the brief but not grounded from a primary source this session; do not treat as settled.

---

## Orientation

The verified evidence converges on a small set of canonical loop architectures, each with a concrete control-flow shape, an iteration-state contract (what carries turn-to-turn), and a termination contract. The reflection/refinement family — **ReAct** (thought→action→observation), **Reflexion** (Actor/Evaluator/Self-Reflection three-role with two-tier memory), **Self-Refine** (one frozen LLM as generator/feedback/refiner), **Plan-and-Solve** (zero-shot plan-then-execute prompting), and **CodeAct** (executable Python as a unified action space) — defines the loop *shapes*. Production loop engineering is dominated by two primary-sourced framework implementations: the **OpenAI Agents SDK Runner** loop (three-branch per-turn cycle, `max_turns`→`MaxTurnsExceeded`) and **LangGraph** (Pregel "super-step" iteration, vote-to-halt, `recursion_limit`→`GraphRecursionError`, super-step durable checkpointing). The **Claude Agent SDK / Claude Code** loop is a five-step tool-use cycle (evaluate → tool-call → feed results back → repeat until no tool calls) with `max_turns`/`max_budget_usd` caps, automatic compaction, and fresh-context subagents. The load-bearing hardening surface is **termination**: every verified loop ships a hard iteration cap because, per the agent-architecture survey, single-agent loops without self-evaluation "may get stuck in an endless execution loop." Context management across iterations (compaction, JIT retrieval, recitation, KV-cache stability) and durable checkpointing are the two production concerns where the loop meets real-world cost and reliability limits.

---

## 1. Loop architectures

### 1.1 ReAct — `thought → action → observation` (base shape)

**[V]** The canonical repeating cycle: "an agent first writes a thought about the given task. It then performs an action based on that thought, and the output is observed. This cycle can repeat until the task is complete." (Masterman et al. survey, arXiv 2404.11584 §3.3; original Yao et al. 2022, arXiv 2210.03629.)

```
# [K] control-flow shape
state = {messages: [system, user_task]}
loop:
    thought, action = LLM(state.messages)          # decide
    if action == FINISH: return action.answer       # terminate
    observation = execute(action)                    # act + observe
    state.messages += [thought, action, observation] # carry-forward: full trajectory
    # perceive = re-read accumulated messages next iteration
```

- **Iteration state:** full interleaved trajectory (thought + action + observation) appended each turn; nothing dropped by default.
- **Termination contract:** model emits a terminal `Finish[answer]` action **OR** a hard iteration cap fires. **[V]** Core failure mode is *non-termination*: "Without the ability to self-evaluate and create effective plans, single agents may get stuck in an endless execution loop" (survey §3.2) — which is why every production loop needs explicit termination logic.
- **Impl reference:** Yao et al. 2022 (arXiv 2210.03629); empirical corroboration that LangChain defaults `maxIterations` to bound this loop.

### 1.2 Plan-and-Solve — zero-shot plan-then-execute *prompting* (the ancestor)

**[V]** Replaces the single-shot "Let's think step by step" Zero-shot-CoT trigger with two phases: "first, devising a plan to divide the entire task into smaller subtasks, and then carrying out the subtasks according to the plan." (Wang et al., ACL 2023, arXiv 2305.04091.)

- **[V]** Zero-shot PS "consistently outperforms Zero-shot-CoT across all datasets by a large margin," is "comparable to or exceeds Zero-shot-Program-of-Thought," and reaches "comparable performance with 8-shot CoT prompting on the math reasoning problem" (10 datasets, 3 reasoning types). **Caveat:** GPT-3 / `text-davinci-003`-era; the strongest results use the PS+ variant.
- **Critical distinction (per advisor + the workflow's own nuance note):** PS elicits both phases *within one CoT chain* — it is the conceptual **ancestor** of orchestrated plan-then-execute agents, **not** a literal two-call orchestration. The orchestrated form is §1.3.
- **Iteration state:** single reasoning chain (plan text → execution text). **Termination:** chain completes / answer emitted (no loop cap — it is prompting, not an iterated agent).

### 1.3 Plan-and-Execute family — orchestrated plan → execute-step → replan

**[P]** Distinct from §1.2: the planner produces a multi-step plan up front, an executor runs each step, then a replanner decides finish-or-continue. Source: LangChain "Planning Agents" writeup (www.langchain.com/blog/planning-agents).

```
# [K] control-flow shape (Plan-and-Execute)
state = {input, plan: [], past_steps: [], response: None}
state.plan = planner(input)                          # plan up front, once
while state.plan:
    step = state.plan[0]
    result = executor_agent(step)                    # often a ReAct sub-agent (§1.1)
    state.past_steps += [(step, result)]
    decision = replanner(state)                       # replan node
    if decision.is_response: return decision.response # terminate
    state.plan = decision.new_plan                    # else overwrite remaining plan
```

- **[P] Termination contract:** "Once execution is completed, the agent is called again with a re-planning prompt, letting it decide whether to finish with a response or whether to generate a follow-up plan."
- **[P] Vs ReAct:** "prompts an LLM to generate a multi-step plan to complete a large task" up front, "avoiding LLM calls between tool invocations" — cheaper than ReAct's per-action thought loop. Limitation: "still is restricted by serial tool calling."
- **Variants (same source):**
  - **ReWOO** **[P]** — planner emits interleaved `Plan`/`E#` task lines with variable substitution (e.g. `#E2`) so the worker executes the whole plan with no per-step replanning; "each task can have only the required context."
  - **LLMCompiler** **[P]** — planner "streams a DAG of tasks. Each task contains a tool, arguments, and list of dependencies"; a Task-Fetching Unit "schedules and executes the tasks…once their dependencies are met"; a Joiner can "dynamically replan or finish based on the entire graph history." Claimed **3.6× speedup** via parallel + streamed task parsing.
  - Underlying papers referenced by the writeup: Plan-and-Solve (2305.04091), ReWOO (arXiv 2305.18323 [uncertain — not retrieved]), LLMCompiler (arXiv 2312.04511 [uncertain — not retrieved]).

### 1.4 Reflexion — Actor / Evaluator / Self-Reflection with two-tier memory

**[V]** Three-role architecture that "reinforce[s] language agents not by updating weights, but instead through linguistic feedback… verbally reflect on task feedback signals, then maintain their own reflective text in an episodic memory buffer to induce better decision-making in subsequent trials." (Shinn et al., NeurIPS 2023, arXiv 2303.11366.)

```
# [K] control-flow shape
long_term = []                                       # episodic reflection buffer (fixed capacity)
for trial in range(max_trials):
    trajectory = actor.rollout(task, memory=long_term)   # Actor: ReAct/CoT inner loop
    reward = evaluator(trajectory)                        # Evaluator: heuristic or LLM/self-test
    if reward == SUCCESS: return trajectory               # terminate (goal satisfied)
    reflection = self_reflection(trajectory, reward)      # verbal lesson, natural language
    long_term.append(reflection)                          # carry across trials
```

- **[V] Two-tier memory:** "trajectory history serves as the short-term memory while outputs from the Self-Reflection model are stored in long-term memory." Short-term = per-trial trajectory; long-term = fixed-capacity buffer of verbal reflections. Reflective text from a failed trial feeds the next trial.
- **Termination contract:** Evaluator returns success **OR** `max_trials` exhausted. Reflection fires only on failure/sub-optimal reward.
- **Impl reference:** arXiv 2303.11366; reference impl noted by corroborating sources (promptingguide.ai, BayJarvis).

### 1.5 Self-Refine — single frozen LLM, `generate → feedback → refine`

**[V]** "Self-Refine does not require any supervised training data, additional training, or reinforcement learning, and instead uses a single LLM as the generator, refiner, and feedback provider"; "the same LLM provides feedback for its output and uses it to refine itself, iteratively." (Madaan et al., NeurIPS 2023, arXiv 2303.17651, Algorithm 1.)

```
# [K] control-flow shape (Algorithm 1)
y = LLM_generate(x)
for t in range(max_iters):
    fb = LLM_feedback(x, y)                # same model critiques its own output
    if fb.is_stop_signal: break           # model-judged "good enough"
    y = LLM_refine(x, y, fb)              # prior feedback + outputs appended to prompt
return y
```

- **Iteration state:** prior outputs **and** prior feedback are appended to the prompt across iterations (history accumulates).
- **Termination contract:** model-emitted stop signal in the feedback step **OR** `max_iters` cap.
- **[V] Convergence win (the canonical reflection-cost-vs-accuracy quantification):** outputs improve "by ~20% absolute on average in task performance" across "7 diverse tasks." **Caveat (vote 2-1):** ~20% is an *average* over heterogeneous tasks with high per-task variance, GPT-3/`text-davinci-003`-era — treat as directional, not a guarantee.

### 1.6 CodeAct — executable code as the unified action space

**[V]** "executable Python code to consolidate LLM agents' actions into a unified action space" replacing "constrained" JSON/text actions; "Integrated with a Python interpreter, CodeAct can execute code actions and dynamically revise prior actions or emit new actions upon new observations through multi-turn interactions." (Wang et al., ICML 2024, arXiv 2402.01030, PMLR 235:50208.)

```
# [K] control-flow shape
state.messages = [system, user_task]
loop:
    code = LLM(state.messages)                 # action = a Python program (not JSON)
    if no_code_block(code): return code.text    # terminate: natural-language answer, no action
    stdout, stderr = python_interpreter(code)   # interpreter IN the loop
    obs = stderr or stdout                       # error-as-observation (see §4)
    state.messages += [code, obs]               # carry-forward
```

- **Iteration state:** message history of (code, execution observation) pairs; the live interpreter session can also carry variable bindings across turns.
- **Termination contract:** the model emits a turn with no executable code block (a final answer).
- **Self-correction:** code-execution errors (stack traces) feed back as observations, driving in-loop repair.
- **Impl reference:** github.com/xingyaoww/code-act; basis for OpenHands/`CodeActAgent`.

### 1.7 Tree / graph-search loops — ToT (grounded), LATS (by reference)

**[P] Tree of Thoughts (ToT)** "generalizes over the popular Chain of Thought approach" by "exploration over coherent units of text (thoughts) that serve as intermediate steps," with an LLM **state evaluator** doing "self-evaluating choices to decide the next course of action" and search that supports "looking ahead or backtracking when necessary to make global choices." (Yao et al., NeurIPS 2023, arXiv 2305.10601.)

```
# [K] control-flow shape (BFS variant)
frontier = [root_state]
for step in range(max_depth):
    candidates = []
    for s in frontier:
        thoughts = thought_generator(s, k)        # propose k next-step thoughts
        for th in thoughts:
            v = state_evaluator(s + th)            # LLM scores promise of partial solution
            candidates.append((s + th, v))
    frontier = top_b(candidates, b)               # keep best b (beam); backtrack = drop dead branches
    if any(is_solution(s) for s,_ in candidates): return solution   # terminate
```

- **Four components (ToT framing):** thought decomposition · thought generator · state evaluator · search algorithm (BFS/DFS).
- **[P] Benchmark:** Game of 24 — ToT **74%** vs GPT-4 CoT **4%**.
- **Termination contract:** a solution state is reached **OR** the search budget (depth × branching, or node-visit cap) is exhausted; dead branches pruned by the evaluator.
- **LATS (Language Agent Tree Search), arXiv 2310.04406** — `[uncertain]` (named as the MCTS-based successor that adds value backpropagation + Reflexion-style reflection over a ToT-like tree; **internals not retrieved this session** — do not cite mechanism detail without fetching). Deliberately scoped out in favor of grounding ToT.

### 1.8 Evaluator-Optimizer (generator ⇄ critic loop)

**[P]** Anthropic's named workflow: "One LLM generates responses while another provides evaluation feedback in a loop," useful when "iterative refinement provides measurable value." (anthropic.com/engineering/building-effective-agents.) This is the two-model generalization of Self-Refine (§1.5): the critic is a *separate* role/model, and the loop exits when the evaluator accepts or a cap fires. (Mechanically identical loop shape to §1.5 with `LLM_feedback` → a distinct evaluator model.)

---

## 2. Termination & convergence

**Hard iteration caps are universal** — the primary defense against runaway iteration. Concrete, primary-sourced thresholds:

| Loop | Cap mechanism | Threshold | On exceed | Source |
|---|---|---|---|---|
| OpenAI Agents SDK | `max_turns` | configurable; **no default limit** | raise `MaxTurnsExceeded` | **[V]** openai docs/repo |
| OpenAI Agents SDK | `max_turns=None` | disables the cap | — | **[V]** |
| LangGraph | `recursion_limit` | **1000** (from v1.0.6); historically **25** | raise `GraphRecursionError` | **[V]** version-dependent |
| Claude Agent SDK | `max_turns` (tool-use turns only) | no default | `ResultMessage.subtype = error_max_turns` | **[P]** |
| Claude Agent SDK | `max_budget_usd` | no default | `error_max_budget_usd` | **[P]** budget-based exit |
| RP-ReAct | per-tier step caps | RPA ≤10, PEA ≤10/query → **100** worst-case; plain ReAct baseline **20** | terminate | **[V]** preprint |
| ReAct (LangChain) | `maxIterations` | empirical default (commonly cited 15) | stop | **[V]** corroboration |

**Goal-satisfaction / structural success contracts:**

- **[V] OpenAI three-branch contract:** the loop ends *only* when the LLM "produces text output with the desired type, and there are no tool calls." **Nuance that survived adversarial review:** the str-vs-structured-`output_type` distinction *matters* — the over-broad claim "this holds regardless of `output_type`" was **refuted (1-2)**. With no `output_type`, any text-without-tool-calls ends the loop; with a structured `output_type`, the output must validate against that type.
- **[V] LangGraph vote-to-halt:** nodes start inactive, activate on receiving a message; "after each super-step nodes with no pending messages become inactive"; "the graph execution terminates when all nodes are inactive and no messages are in transit."
- **[P] Claude SDK:** "Claude continues calling tools and processing results until it produces a response with no tool calls," at which point the loop ends and yields a `ResultMessage`. Result subtypes encode *why* it stopped: `success` / `error_max_turns` / `error_max_budget_usd` / `error_during_execution` / `error_max_structured_output_retries`.

**Budget-based exits.** **[P]** Claude SDK `max_budget_usd` caps spend; Anthropic guidance: "Setting a budget is a good default for production agents." **[P]** Anthropic loop guidance: "it's also common to include stopping conditions (such as a maximum number of iterations) to maintain control."

**Replanning / self-correction as a convergence mechanism.** **[V] RP-ReAct** is supervisor-triggered, not blind retry: on failure/unexpected output the Reasoner-Planner "reasons to diagnose the probable cause of the failure and dynamically formulates a new corrective step." Exit on `<Finish>answer</Finish>`. (Molinari & Ciravegna, arXiv 2512.03560 — **non-archival AAAI-2026-workshop preprint, Dec 2025**; descriptive design, not efficacy.)

**Stall / no-progress / oscillation detection — HONEST GAP.** The deep-research pass found **no verified claim with concrete thresholds** for stall, no-progress, or oscillation detection *distinct from* the blunt iteration cap. Frameworks ship the hard cap (above); they do **not**, in the verified set, ship a documented "same-action-N-times" or "no-state-change" detector with a named threshold. **Do not invent one.** If the harness needs stall/oscillation detection, it is a design decision to be specified, not a documented industry default. (Open question carried in §Open Questions.)

---

## 3. Context management across iterations

The loop's context window is finite working memory that **accumulates every turn** and degrades with length — so what to carry / compact / drop is a first-class loop concern.

**Context accumulates; nothing resets between turns.** **[P]** "The context window… does not reset between turns within a session. Everything accumulates: the system prompt, tool definitions, conversation history, tool inputs, and tool outputs." (Claude SDK agent-loop doc.) Large tool outputs are the dominant consumer.

**Context rot — the empirical reason long loops degrade.** **[P]** Chroma (18 LLMs incl. GPT-4.1, Claude 4, Gemini 2.5, Qwen3): "model performance varies significantly as input length changes, even on simple tasks"; "models do not use their context uniformly; instead, their performance grows increasingly unreliable as input length grows." Specific effects:
- **Distractor effect:** "even a single distractor reduces performance," multiple compound, and "distractors do not have uniform impact."
- **Position:** "Accuracy is highest when the unique word is placed near the beginning of the sequence, especially as input length increases."
- **Needle-question similarity:** lower semantic similarity between question and answer → steeper degradation with length.
- **[P]** Anthropic frames the mechanism as a finite "attention budget": "As the number of tokens in the context window increases, the model's ability to accurately recall information from that context decreases."

**Compaction — carry-forward vs drop.** **[P]** (Anthropic + Claude SDK.) Fires when "a conversation [is] nearing the context window limit"; "summarizes older history to free space, keeping your most recent exchanges and key decisions intact." Tuning: "Start by maximizing recall… then iterate to improve precision by eliminating superfluous content." **Preserve:** "architectural decisions, unresolved bugs, and implementation details" + "the five most recently accessed files." **Drop:** "redundant tool outputs or messages" — "Once a tool has been called deep in the message history, why would the agent need to see the raw result again?" SDK signal: a `compact_boundary` system message; `PreCompact` hook can archive the full transcript first.

**JIT (just-in-time) retrieval vs pre-loading.** **[P]** Agents "maintain lightweight identifiers (file paths, stored queries, web links, etc.) and use these references to dynamically load data into context at runtime using tools." Trade-off: "Runtime exploration is slower than retrieving pre-computed data" but reduces context pollution. Best agents use a **hybrid**: some data up front for speed, autonomous exploration as needed. **Retrieval trigger tied to loop state:** load a reference only when the current step needs it (not pre-loaded into the prefix).

**Structured note-taking / scratchpad (external working memory).** **[P]** "The agent regularly writes notes persisted to memory outside of the context window… pulled back into the context window at later times" (e.g. `NOTES.md`, to-do lists) to "track progress across complex tasks… that would otherwise be lost across dozens of tool calls."

**Recitation (goal re-injection).** **[P]** Manus: agents "create a `todo.md` file — and update it step-by-step…checking off completed items," pushing "the global plan into the model's recent attention span, avoiding…goal misalignment." Combats lost-in-the-middle over "approximately 50 tool calls per typical task."

**File-system-as-context (unbounded external memory).** **[P]** Manus treats "the file system as the ultimate context: unlimited in size, persistent by nature, and directly operable by the agent." Compression must stay **restorable** — drop cached content but keep the URL/path so nothing is irreversibly lost.

**Sub-agent context offload.** **[P]** A subagent "returns a condensed, distilled summary of its work (often 1,000–2,000 tokens)" to the coordinator — the parent's context grows by the summary, not the full sub-trajectory (see §6.4).

**No numeric token budget is specified** by the Anthropic guidance — it is explicitly relative ("smallest possible set of high-signal tokens"). The only hard numbers grounded this session are the 1,000–2,000-token subagent summary and Manus's KV-cache cost figures (§4 / §6).

---

## 4. Action / observation handling

**Tool results feed straight back as the next observation.** **[V]** OpenAI: "If the LLM produces tool calls, we run those tool calls, append the results, and re-run the loop." **[P]** Claude SDK: "The SDK runs each requested tool and collects the results. Each set of tool results feeds back to Claude for the next decision," yielded as a `UserMessage` carrying the tool-result content.

**Error-as-observation (do not hide failures).** **[V/P]** Two grounded mechanisms:
- **[V] CodeAct:** stderr / stack traces re-enter as observations, enabling in-loop repair (§1.6).
- **[P] Manus:** "leave the wrong turns in"—when "the model sees a failed action—and the resulting observation or stack trace—it implicitly updates its internal beliefs," reducing repeated mistakes. **[P]** Claude SDK: when a tool is denied, "Claude receives a rejection message as the tool result and typically attempts a different approach."

```
# [K] error-as-observation shape
result = execute(action)
obs = result.ok ? format(result.value) : format_error(result.stderr)  # errors are first-class observations
state.messages += [action, obs]    # failed actions re-enter the loop, NOT silently dropped
```

**Parallel vs sequential execution *within a turn*.** **[P]** Claude SDK: when Claude requests multiple tool calls in one turn, "Read-only tools (like `Read`, `Glob`, `Grep`, and MCP tools marked as read-only) can run concurrently. Tools that modify state (like `Edit`, `Write`, and `Bash`) run sequentially to avoid conflicts." Custom tools default to sequential; set `readOnlyHint` to allow parallel. **[V]** LangGraph: "Nodes that run in parallel are part of the same super-step, while nodes that run sequentially belong to separate super-steps." (Intra-turn concurrency beyond these two is **[uncertain]** — not separately verified.)

**Tool-result formatting.** **[P]** Results are returned to the model as structured tool-result content blocks (Claude SDK `UserMessage` / OpenAI appended tool outputs). Large outputs are the main context cost (§3); the loop, not the model, decides truncation/compaction policy.

---

## 5. Reflection & self-correction mechanics

**Two grounded reflection shapes, by feedback locus:**

1. **Verbal episodic reflection across trials — Reflexion (§1.4).** **[V]** Self-Reflection model emits a *natural-language* lesson on failure; it is stored in the long-term buffer and prepended to the next trial. **Fires:** only after the Evaluator returns failure/sub-optimal. **Format:** free-text verbal feedback (not a scalar reward). **Retry-exit:** Evaluator success OR `max_trials`.

2. **Self-critique within one task — Self-Refine (§1.5) / Evaluator-Optimizer (§1.8).** **[V/P]** Same model (Self-Refine) or a separate critic (Evaluator-Optimizer) produces feedback on the current output; the refiner consumes it. **Fires:** every iteration until a stop signal. **Format:** targeted feedback on the specific output. **Retry-exit:** model-judged "good enough" stop signal OR `max_iters`.

```
# [K] unified reflection loop (parameterize the feedback source)
attempt = generate(task)
for i in range(max_iters):
    verdict = evaluate(attempt)                  # heuristic | self-test | LLM-judge | separate critic
    if verdict.accepted: return attempt          # retry-exit on success
    feedback = reflect(attempt, verdict)         # scalar reward → verbal lesson
    attempt = revise(task, attempt, feedback, memory)   # memory: append-only across iters
return attempt                                    # retry-exit on cap
```

**When reflection fires — the cost/accuracy tension (made explicit per brief).** Reflection adds 1+ extra model call(s) per iteration. **[V]** Self-Refine's ~20%-absolute-average gain is the headline benefit, but it is GPT-3-era with high per-task variance — i.e. reflection pays off unevenly. **Tension:** reflect-every-iteration (Self-Refine) maximizes correction but multiplies cost; reflect-only-on-failure (Reflexion) is cheaper but needs a reliable Evaluator to know when to fire. **[V]** The refuted "models commit early → snowball divergence" rationale (vote 1-2) is **excluded** — do not use early-commitment-snowball as the justification for reflection.

**Verbal-feedback format guidance.** **[V]** Reflexion's reflections are concrete, trajectory-specific lessons ("I failed because… next time I should…"), stored verbatim — not a numeric score. This is the distinguishing design choice vs scalar-reward RL.

---

## 6. Claude Code / Anthropic-specific implementation

### 6.1 The five-step loop (Claude Agent SDK = Claude Code's loop)

**[P]** (code.claude.com/docs/en/agent-sdk/agent-loop.) "the SDK runs the same execution loop that powers Claude Code":

1. **Receive prompt** — Claude gets prompt + system prompt + tool definitions + conversation history; SDK yields a `SystemMessage` subtype `"init"`.
2. **Evaluate and respond** — Claude returns text and/or tool-call requests; SDK yields an `AssistantMessage`.
3. **Execute tools** — SDK runs each requested tool, collects results; results feed back. `PreToolUse`/`PostToolUse` hooks can intercept/block.
4. **Repeat** — steps 2–3 are one **turn**; "Claude continues calling tools and processing results until it produces a response with no tool calls."
5. **Return result** — final `AssistantMessage` (no tool calls) + a `ResultMessage` (final text, token usage, cost, session ID).

**Turn = one round trip** (model output incl. tool calls → SDK executes → results feed back) "without yielding control back to your code. Turns continue until Claude produces output with no tool calls." `max_turns` "counts tool-use turns only"; `max_budget_usd` caps by spend.

### 6.2 Termination & result subtypes
**[P]** `ResultMessage.subtype` ∈ {`success`, `error_max_turns`, `error_max_budget_usd`, `error_during_execution`, `error_max_structured_output_retries`}; only `success` carries the `result` text. A `stop_reason` (`end_turn` / `max_tokens` / `refusal`) reports why the model stopped its final turn. (Full mapping in §2 table.)

### 6.3 Prompt-cache interaction with iterative context
**[P]** "Content that stays the same across turns (system prompt, tool definitions, CLAUDE.md) is automatically prompt cached, which reduces cost and latency for repeated prefixes." Implication for the loop: keep the prefix **stable** so the growing conversation reuses the cache. **[P]** Manus quantifies the stakes: with Claude Sonnet, cached input is **$0.30/MTok vs $3.00/MTok uncached — a 10× difference**; "even a single-token difference can invalidate the cache from that token onward," so avoid second-precise timestamps in the prefix and keep context **append-only** with deterministic serialization.

### 6.4 Subagents / the `Task`→`Agent` loop
**[P]** (code.claude.com/docs/en/agent-sdk/subagents.) Claude spawns subagents via the **`Agent`** tool (renamed from **`Task`** in Claude Code v2.1.63; `Task` still appears in `system:init` tool lists for back-compat).
- **Fresh context:** "Each subagent runs in its own fresh conversation. Intermediate tool calls and results stay inside the subagent; only its final message returns to the parent." The only parent→child channel is the `Agent` tool's prompt string.
- **What it inherits:** its own system prompt + the Agent-tool prompt; project CLAUDE.md; tool definitions (or the `tools` subset). It does **not** receive the parent's history, system prompt, or preloaded skills.
- **Parallelism:** "Multiple subagents can run concurrently, so independent subtasks finish in the time of the slowest one."
- **Resumability:** the Agent-tool result carries `agentId: <id>`; resume by capturing `session_id` + `agentId` and passing `resume: sessionId`. Subagent transcripts persist in separate files (unaffected by main-conversation compaction; cleaned per `cleanupPeriodDays`, default 30).
- **No nesting:** "Subagents cannot spawn their own subagents."
- **Per-subagent config (`AgentDefinition`):** `description`, `prompt`, `tools`, `model`, `skills`, `maxTurns`, `effort`, `background`, `permissionMode`.
- **Scale beyond turn-by-turn:** for "dozens to hundreds of agents," the `Workflow` tool "moves the orchestration into a script the runtime executes outside the conversation context."

### 6.5 Extended thinking / effort vs the loop
**[P]** `effort` ∈ {low, medium, high, xhigh, max} "controls how much reasoning Claude applies" *per response*; **independent of** extended thinking ("a separate feature that produces visible chain-of-thought blocks"). You can combine them freely. `effort` is set per-session or per-subagent (overrides session). (How extended-thinking blocks are retained across turns is **[uncertain]** — not documented in the loop page.)

### 6.6 Anthropic's documented loop-design guidance
**[P]** (anthropic.com/engineering/building-effective-agents.) "Agents are typically just LLMs using tools based on environmental feedback in a loop." "During execution, it's crucial for the agents to gain 'ground truth' from the environment at each step (such as tool call results or code execution)." "Agents can then pause for human feedback at checkpoints or when encountering blockers." Stopping: "it's also common to include stopping conditions (such as a maximum number of iterations)." Design principles: **simplicity**, **transparency** (show the planning steps), and a well-documented **agent-computer interface (ACI)**. Agents vs workflows: workflows = "LLMs and tools…orchestrated through predefined code paths"; agents = "LLMs dynamically direct their own processes and tool usage."

---

## 7. Production loop hardening

**Durable checkpointing of loop state.** **[V]** LangGraph "checkpoints loop state at every super-step into thread-keyed (`thread_id`) snapshots, with per-task (node-level) writes persisted as tasks complete." Concretely: `PregelRunner.commit` accumulates writes as tasks complete; "if another node in the same super-step fails, the successful nodes' writes are already durable and don't need to be re-run on resume" — on failure "the error is stored in `pending_writes`" and "the checkpoint version is NOT advanced; the state remains at the beginning of the superstep that failed."

**Resumability mid-loop.** **[V]** Super-step granularity: on resume the **failed node is re-run; its successful siblings are skipped** (their writes are already durable). Thread-keyed via `{"configurable": {"thread_id": "1"}}`. **[P]** Claude SDK: capture `ResultMessage.session_id`; resume restores "files that were read, analysis that was performed, and actions that were taken"; sessions can also be **forked** to branch an approach. Subagents resume independently via `agentId` (§6.4). **Caveat [V]:** the Diagrid critique disputes LangGraph's *broad* durable-execution guarantees vs Temporal/Dapr (no infra-level auto-retry; explicit resume required) — but does **not** contradict the specific super-step `pending_writes` mechanism above.

**Idempotency of loop steps.** Not directly grounded in the verified set. The append-only / restorable-compression discipline (§3, §6.3) and "checkpoint version not advanced on failure" (above) are the *enabling* primitives — re-running a failed super-step is safe **because** successful sibling writes are already committed and not replayed. A genuinely idempotent tool step (same inputs → same effect) is required for safe replay; this is a harness design obligation, **[uncertain]** as a documented framework guarantee.

**Observability of per-iteration spans.** **[V]** LangGraph's super-step is the natural per-iteration span boundary (parallel nodes share a super-step; sequential nodes are separate super-steps). **[P]** Claude SDK exposes per-turn observability through the message stream (`AssistantMessage` per turn, `UserMessage` per tool result, `compact_boundary` events, `SubagentStart`/`SubagentStop` hooks, "tool progress, rate limits, task notifications" in the TS SDK) plus per-result `total_cost_usd`, `usage`, `num_turns`. Hooks (`PreToolUse`/`PostToolUse`/`Stop`/`PreCompact`/`SubagentStart`/`SubagentStop`) "run in your application process, not inside the agent's context window," so instrumentation does not consume context. (Mapping these to OTel spans is the harness OD-axis concern, not re-spec'd here.)

---

## Pattern Decision Matrix

| Pattern | Loop shape | Best-fit use case | Termination contract | Key cost / tension |
|---|---|---|---|---|
| **ReAct** | `thought→action→observation`, append trajectory | General tool-use; interactive reasoning+acting | `Finish[answer]` action OR iteration cap | Non-termination risk; needs explicit cap |
| **Plan-and-Solve** (prompting) | plan-then-execute *within one CoT chain* | Zero-shot multi-step reasoning w/o exemplars | chain completes (no loop) | Single-pass; no in-loop correction; GPT-3-era results |
| **Plan-and-Execute** (orchestrated) | plan → execute-step → replan | Large tasks; fewer LLM calls than per-action ReAct | replanner returns response vs new plan | Serial tool calls; replan cost |
| **ReWOO** | full plan w/ variable substitution → execute → solve | Cut replanning calls; isolate per-task context | solver integrates outputs | Brittle if up-front plan is wrong |
| **LLMCompiler** | DAG of tasks → parallel fetch-execute → joiner | Parallelizable tool-heavy tasks (≈3.6× speedup) | joiner finishes vs replans | DAG planning complexity |
| **Reflexion** | actor-rollout → evaluate → verbal-reflect → retry | Multi-trial tasks with a usable success signal | Evaluator success OR `max_trials` | Needs reliable Evaluator; extra reflection call on failure |
| **Self-Refine** | `generate→feedback→refine` (one frozen LLM) | Single-output quality lift, no training | model stop signal OR `max_iters` | +1 call/iter; ~20% gain (high variance) |
| **Evaluator-Optimizer** | generator ⇄ separate critic in a loop | When refinement value is measurable | evaluator accepts OR cap | 2 models; critic quality is the ceiling |
| **CodeAct** | code → interpret → observe | Code/data tasks; rich action space; error-repair | turn with no code block | Sandbox/exec safety; interpreter in loop |
| **Tree of Thoughts** | generate thoughts → state-eval → search (BFS/DFS) + backtrack | Hard search/planning (Game-of-24 74% vs 4%) | solution found OR search budget | Many LLM evals/node; expensive |
| **LATS** `[uncertain]` | MCTS over thoughts + value backprop + reflection | Deliberate search needing learning across rollouts | solution OR node/iteration budget | Highest eval cost (internals not retrieved) |
| **OpenAI Agents SDK** | 3-branch: final-output / handoff / tool-calls→rerun | Production multi-agent w/ handoffs | text of desired type + no tool calls; `max_turns` | `output_type` validation; turn budget |
| **LangGraph** | Pregel super-step; vote-to-halt | Durable, resumable graph agents | all nodes inactive & no messages; `recursion_limit` | Graph authoring; cap is version-dependent (25↔1000) |
| **Claude Agent SDK** | 5-step tool-use cycle until no tool calls | Claude-native autonomous agents + subagents | no-tool-call response; `max_turns`/`max_budget_usd` | Context accumulation; compaction tuning |

---

## Sources

**Consumed this session — primary papers (verified claims, [V]):**
- ReAct — Yao et al. 2022 — https://arxiv.org/abs/2210.03629
- Reflexion — Shinn et al., NeurIPS 2023 — https://arxiv.org/abs/2303.11366
- Self-Refine — Madaan et al., NeurIPS 2023 — https://arxiv.org/abs/2303.17651
- Plan-and-Solve — Wang et al., ACL 2023 — https://arxiv.org/abs/2305.04091
- CodeAct — Wang et al., ICML 2024 — https://arxiv.org/abs/2402.01030 · repo https://github.com/xingyaoww/code-act
- Tree of Thoughts — Yao et al., NeurIPS 2023 — https://arxiv.org/abs/2305.10601
- Agentic-architecture survey — Masterman et al. — https://arxiv.org/pdf/2404.11584 (§3.2, §3.3)
- RP-ReAct — Molinari & Ciravegna, Dec 2025 — https://arxiv.org/html/2512.03560v1 *(non-archival preprint)*

**Consumed this session — framework docs/source (verified, [V]):**
- OpenAI Agents SDK — https://openai.github.io/openai-agents-python/running_agents/ · https://github.com/openai/openai-agents-python
- LangGraph — https://github.com/langchain-ai/langgraph · graph-api/persistence/durable-execution under https://docs.langchain.com/oss/python/langgraph/

**Consumed this session — primary sources for gap sections ([P], not 3-vote-verified but quoted):**
- Claude Agent SDK — agent loop — https://code.claude.com/docs/en/agent-sdk/agent-loop
- Claude Agent SDK — subagents — https://code.claude.com/docs/en/agent-sdk/subagents
- Anthropic — Building Effective Agents — https://www.anthropic.com/engineering/building-effective-agents
- Anthropic — Effective Context Engineering for AI Agents — https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Manus — Context Engineering for AI Agents — https://manus.im/blog/Context-Engineering-for-AI-Agents-Lessons-from-Building-Manus
- Chroma — Context Rot (18 LLMs) — https://www.trychroma.com/research/context-rot
- LangChain — Planning Agents (Plan-and-Execute / ReWOO / LLMCompiler) — https://www.langchain.com/blog/planning-agents

**Referenced but NOT retrieved this session (do not treat as grounded):**
- LATS — https://arxiv.org/abs/2310.04406 `[uncertain]`
- ReWOO paper — arXiv 2305.18323 `[uncertain]`; LLMCompiler paper — arXiv 2312.04511 `[uncertain]` (named by the LangChain writeup; not independently fetched)
- Also fetched by the workflow but not load-bearing here: https://research.trychroma.com/context-rot (→ redirect to trychroma.com), https://claude.com/blog/building-agents-with-the-claude-agent-sdk, https://code.claude.com/docs/en/how-claude-code-works, https://platform.claude.com/cookbook/..., https://pydantic.dev/docs/ai/api/pydantic-ai/agent/

**Seed sources provided but NOT retrieved / produced no verified claim (excluded from grounding per provenance discipline):**
- https://github.com/agenticloops-ai · https://github.com/Saik0s/agent-loop *(seed repos — never retrieved)*
- Seed blogs (addyosmani, lushbinary, mindstudio, stevekinney, datasciencedojo, mem0): the deep-research pass reports **none survived into the verified claim set** — only primary papers/docs did. Treat their "loop engineering" framing as unverified.

---

*Provenance note: 23 claims tagged **[V]** were adversarially verified (3-vote, 21/23 high-confidence, all 3-0 unanimous except Self-Refine ~20% [2-1] and Plan-and-Solve benchmark [2-1]). 2 claims were **refuted** and excluded: the "early-commitment snowball" rationale for reflection, and the over-broad "final-output rule holds regardless of `output_type`." Sections 3 and 6 are grounded in **[P]** primary fetches because no claim in those dimensions survived the workflow's top-25 verification cut — their absence from [V] is a verification-budget artifact, not a finding of falsity.*
