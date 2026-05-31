# The Gating and Evaluation Architecture of LLM Agents

The corpus reveals a strict architectural distinction: **in-loop deterministic gating** is a runtime reliability mechanism designed to catch schema violations and immediate execution errors, while **out-of-loop statistical eval** is an offline alignment and observability mechanism designed to combat generalization failures and criteria drift.

## 1. In-Loop Gating: Deterministic Contracts

**Demonstrations of the contract:**

- **12-Factor Agents** relies heavily on in-loop gating through its "stateless reducer" and "tools are structured outputs" principles, feeding deterministic schema-validation errors immediately back into the context window for retry.
- **Claude Code** implements a strict in-loop Go-based guardrail engine that evaluates every tool call with a "deny-first" pipeline, blocking unpermitted operations before they execute.
- **OpenAI Agents SDK** uses explicit input, output, and tool guardrails that raise exceptions or return a `tripwire_triggered` flag to halt execution entirely.
- **LangGraph** manages the retry-on-fail versus exit-on-permanent-fail boundary by utilizing a configurable `RetryPolicy` on specific nodes, allowing the graph to safely retry transient errors while exiting on permanent validation failures.

**Co-location vs. Decoupling:**

- **Decoupled:** The 12-Factor methodology strictly decouples the gate from the validator, keeping the control flow and schema validation in standard application code outside of the LLM framework.
- **Co-located:** In contrast, the OpenAI Agents SDK co-locates the gates directly on the agent and tool definitions via decorators and built-in flags.

## 2. Out-of-Loop Eval Discipline: The Husain Loop

The "Husain loop" rejects eval-driven development in favor of **error-analysis-first** engineering. The loop requires a "benevolent dictator" (a principal domain expert) to manually review traces, write open-coded critiques, group them via axial coding into a taxonomy of failure modes, and only then build automated evaluators to track those specific failures.

- **Where it is demonstrated:** This discipline is explicitly supported by dedicated observability platforms like **Arize Phoenix** and **VoltAgent's VoltOps** console, which treat traces as first-class data for building and refining evaluators. Hamel Husain's own evals-skills plugin explicitly operationalizes this workflow by shipping error-analysis and judge-prompting workflows as Skills for coding agents.
- **Measuring Judge-Human Alignment:** Alignment is measured by splitting the human-labeled data into dev and held-out test sets. Rather than relying on simple accuracy (which fails on imbalanced datasets), alignment is measured using **True Positive Rate (TPR)**, **True Negative Rate (TNR)**, and **Cohen's Kappa (κ)** to account for chance-corrected inter-annotator agreement.
- **The Alignment Floor:** The corpus surfaces a strict quantitative floor for trusting an LLM-as-a-judge: it must achieve **TPR ≥ 0.9, TNR ≥ 0.85, and Cohen's κ ≥ 0.7** against the human expert's labels.

## 3. Judge-Base-Model Collision (Self-Enhancement Bias)

When the evaluator and the target agent share the same base model, they are susceptible to what Zheng et al. officially terms **"self-enhancement bias."**

- **Corpus Findings:** Zheng et al.'s research demonstrates that this bias is significant: GPT-4 favored its own answers with a 10% higher win rate, and Claude-v1 favored itself by 25%.
- **Flagged vs. Resolved:** In academic literature, this is **flagged** as a vulnerability, with researchers recommending cross-family models (e.g., a GPT-4 judge evaluating Claude output) as a mitigation. However, in production engineering, it is pragmatically **resolved/bypassed**. Husain explicitly notes that "using the same model for both task and judge is usually fine," countering the theoretical concern with the operational reality that as long as the judge passes the strict TPR/TNR calibration floor against human ground-truth, the underlying bias is mitigated.

## 4. Meta-Eval: Evaluating the Evaluator

Meta-eval treats the validator not as a static rule, but as a model requiring its own continuous evaluation, primarily because of **"criteria drift"**—the phenomenon where human evaluators change their definitions of success after observing real model outputs.

- **Exhibiting Meta-Eval:** Frameworks like EvalGen operationalize this by generating candidate LLM grader prompts and selecting the ones that best align with a human-graded subset. Out-of-loop platforms (Arize Phoenix, LangSmith) treat evaluators as artifacts requiring continuous tuning on a 100-trace held-out test set.
- **Treating the Validator as Ground Truth:** Conversely, in-loop agentic patterns like **Reflexion** treat their validators (often unit tests) as absolute ground truth. The corpus highlights the extreme danger of this: Reflexion actually *underperformed* baselines on the MBPP benchmark specifically because its unit-test evaluator had a 16.3% false-positive rate. When an agent treats an unreliable validator as ground truth, it induces endless, token-burning self-correction loops that degrade performance.

## Phase 2 Questions for the Systems Architect

Because the choice between in-loop gating and out-of-loop evaluation is dictated by the workload rather than the architecture, the systems architect must answer these questions in Phase 2:

1. **What is the objective-to-subjective ratio of our success criteria?** (If success can be mathematically or syntactically proven via linters and schemas, we must build in-loop deterministic gates. If success is subjective—like "appropriate tone" or "sound architectural reasoning"—we must defer to out-of-loop LLM-as-a-judge pipelines to prevent slowing down the runtime.)
2. **Who is the "benevolent dictator" for this workload?** (If we cannot identify a single principal domain expert to manually review traces and resolve annotation conflicts for our holdout set, we cannot build a reliable out-of-loop LLM judge.)
3. **What is our false-positive tolerance for in-loop validators?** (If an in-loop gate fails a valid LLM output, it triggers a costly retry loop. Do we have the telemetry in place to monitor the true-positive/true-negative rates of our deterministic gates before they burn our token budget?)
