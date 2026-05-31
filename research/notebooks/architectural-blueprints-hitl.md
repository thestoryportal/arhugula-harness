# Architectural Blueprints for Human-in-the-Loop AI Systems

The corpus reveals that Human-in-the-Loop (HITL) is no longer treated as a separate pipeline or exception, but as a first-class architectural primitive (e.g., HumanLayer's Factor 7: "Contact humans with tool calls"). The design space spans from simple, synchronous gates to complex, multi-day durable interruptions.

Here is the spectrum of HITL primitive designs, their costs, and workload fits:

## 1. Coarse: Approve/Deny on Tool Call

This design gates specific tool executions behind a binary prompt. Examples include Claude Code's `deny -> ask -> allow` permission modes and HumanLayer's `@hl.require_approval()` decorator.

- **(a) Operator-Experience Cost:** If triggered frequently, this leads directly to "approval fatigue." At a low review rate, decision quality plummets as users begin to blindly approve or switch to "bypass/YOLO" modes to clear the queue. It adds synchronous latency, as the agent waits idle for a click.
- **(b) Integration Cost:** Low. It can be easily implemented with simple decorators or CLI prompts and works within a single-process, in-memory topology without requiring complex state management.
- **(c) Workload Tolerances:**
  - **Can tolerate:** Infrequent, irreversible, or high-blast-radius actions (e.g., database writes, financial transactions, sending emails to clients).
  - **Cannot tolerate:** Highly iterative, exploratory tasks (e.g., a coding agent running 50 grep searches), where the sheer volume of requests will break the operator's patience.

## 2. Medium: Rubric-Prompt Review / Dry-Run Validation

Instead of gating the raw tool call, the system executes a prediction or runs an evaluator, then surfaces a "human handoff packet" (containing the proposed action, model confidence, failed attempts, and alternatives). This aligns with the "dry-run-then-approve" pattern and the "evaluator-optimizer" loop with human grading.

- **(a) Operator-Experience Cost:** Requires more focused attention per session, but significantly improves decision quality. Because the human reviews predicted outcomes or rubric scores rather than raw API calls, they can make informed judgments. It increases latency by requiring the model to generate the prediction or evaluation before pausing.
- **(b) Integration Cost:** Moderate. It requires building a mock execution environment or evaluator step, standardizing the format of the human-handoff packet, and often requires a dedicated UI panel or dashboard to render the context properly.
- **(c) Workload Tolerances:**
  - **Can tolerate:** Asynchronous software engineering (reviewing a generated PR), content creation (approving a draft before publishing), and complex data pipeline changes.
  - **Cannot tolerate:** Real-time customer service or sub-second latency voice agents where doubling the inference time for a dry-run breaks the UX.

## 3. Fine-Grained: Interrupt/Resume at Any Agent Step

This design pauses the actual workflow execution graph, allowing the human to edit state, override decisions, or provide missing context before resuming. Examples include LangGraph's `interrupt()` and Temporal's durable signals.

- **(a) Operator-Experience Cost:** Excellent for the operator, as they can respond asynchronously (in minutes or days) without burning compute resources. The operator can inspect the exact workflow state and alter it, providing high decision quality.
- **(b) Integration Cost:** High. It strictly requires a persistent checkpointer (e.g., SQLite/Postgres for LangGraph) or a full durable execution engine (like Temporal or Inngest). Furthermore, resuming a workflow often re-executes the interrupted node from the beginning, meaning all side effects prior to the interrupt **must be written as idempotent operations**. Failure to handle timeouts leaves "stale interrupt threads" bloating the database indefinitely.
- **(c) Workload Tolerances:**
  - **Can tolerate:** Multi-day enterprise workflows, asynchronous Slack/email approvals, and long-horizon tasks.
  - **Cannot tolerate:** Ephemeral, stateless scripts, or deployments lacking a database to store the checkpointed state.

## Closing: Operator-Availability Assumptions for Phase 2

Because the HITL mechanism dictates your orchestration infrastructure, the systems architect must surface the following operator-availability assumptions in Phase 2:

- **What is the expected human response SLA?**
  - If the operator will respond synchronously (**< 1 minute**), the system can rely on simple, in-process blocking (e.g., LangGraph's `interrupt()` backed by local SQLite).
  - If the operator will respond asynchronously (**> 1 minute to several days** via Slack or email), a durable execution substrate (Temporal, HumanLayer webhooks, or Postgres checkpointing) is **mandatory** to survive process restarts and avoid compute waste.
- **What is the timeout and abandonment policy?** If humans are asynchronous, the architect must define SLA bounds (e.g., a 5-day timeout). If a human never responds, the workflow must have a deterministic fallback (e.g., mark as rejected or escalate) to prevent deadlocked graphs and unbounded state growth.
- **What is the operator's "approval budget"?** The architect must define hard caps on human handoffs (e.g., max 1 handoff per agent step) to prevent the agent from spamming the operator and inducing approval fatigue.
