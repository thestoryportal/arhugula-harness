# Five-Axis Checklist

The five harness axes are the canonical decomposition for agent-harness architectural concerns. Every architectural decision lives on one or more axes; the axis (or axes) determine which patterns, which voices, and which substrate sections apply.

---

## 1. Axis definitions

### 1.1 Control plane

**Owns:** orchestration topology, control flow, sub-agent boundaries, parallelism mode, hand-off mechanics, loop termination criteria, HITL placement in the topology.

**Question form:** *Where do things plug in? What runs when? Who hands off to whom?*

**Boundary marker:** if the decision is about *the shape of the agent graph or its execution flow*, it is control plane. If the decision is about *what an agent does at a given node*, it is action surface (see §1.3).

### 1.2 Information substrate

**Owns:** what state lives where, how it is read and written, how it persists or expires, how it flows between agents and across runs, attention budget per inference, prompt-cache breakpoint placement, JIT retrieval triggers, durable-state tier, memory-tier residence, pruning policies.

**Question form:** *What does the harness know? Where is that knowledge stored? How does it get into and out of the inference?*

**Boundary marker:** if the decision is about *what enters one inference call*, it is within-turn information substrate. If the decision is about *what persists across inferences or across runs*, it is durable information substrate. The two are sub-axes of the same axis but warrant separate treatment in ADRs.

### 1.3 Action surface

**Owns:** tool contracts (I/O schemas, namespacing, descriptions, strict mode), MCP server boundaries, server-vs-client tool placement, Skills content (the action-surface side, not the within-turn-loading side), idempotency contracts, tool-selection-at-scale.

**Question form:** *What can the harness do in the world? What is the contract for each capability?*

**Boundary marker:** if the decision is about *whether an agent CAN do something*, it is action surface. If the decision is about *whether an agent IS ALLOWED to do something at runtime*, it is operational discipline (trust boundary). Action surface is the contract; operational discipline is the gate.

### 1.4 Operational discipline

**Owns:** observability (spans, traces, attribute schema, sampling), evaluation (eval sets, holdout, judge alignment, regression detection), retry (backoff, idempotency keys, total-budget timeouts), breakers (per-model, per-provider), validators (schema gates, judge gates, evaluator-optimizer loops), trust boundary (per-tool gate policy, blast-radius taxonomy, MCP trust tiers, sandbox), audit ledger, secrets, cost attribution, latency budgets.

**Question form:** *How does the harness behave reliably under load and under failure? What does the operator see? What gets caught before it hits the world?*

**Boundary marker:** the broadest axis. The discriminator is *production reliability and operability*. If a decision is about behavior visible in normal operation, it is likely action surface or control plane; if it is about what catches failure, what observes behavior, what gates risky actions, or what the operator depends on to debug — it is operational discipline.

### 1.5 Deployment surface

**Owns:** the platform shape on which the harness runs — local-dev, cloud-managed, hybrid, on-prem, K8s, serverless, container; the OS-level integration assumptions; the substrate-level dependencies (what runtime, what filesystem, what process model).

**Question form:** *Where does this run? What does the runtime environment provide?*

**Boundary marker:** if the decision is about *the platform the harness assumes*, it is deployment surface. If the decision is about *what the harness does on that platform*, it is one of the other four axes.

---

## 2. Axis assignment rules

Every architectural decision is tagged with **one PRIMARY axis** and zero or more SECONDARY axes.

| Tag | Meaning |
|---|---|
| **PRIMARY** | The decision's load-bearing concern. The voice that owns this axis is the primary voice for the decision. |
| **SECONDARY** | The decision affects this axis materially but does not originate in it. The voice that owns this axis is consulted, not primary. |
| **TANGENTIAL** | The decision touches this axis incidentally; no voice involvement required. |

**Single-PRIMARY rule.** A decision has exactly one PRIMARY axis. If a decision appears to have two PRIMARY axes, it is probably two decisions and should be split into two ADRs.

**Axis-collapse failure mode.** Treating every decision as living on one axis (e.g., "everything is operational discipline because reliability matters") is axis collapse. The discipline is to locate the decision's *origin* — the constraint or pattern that forced it — and that origin's axis is PRIMARY.

---

## 3. Common cross-axis tensions

Three tensions are permanent in agent-harness architecture. Every project encounters them; the discipline is to surface them, not to expect to eliminate them.

### 3.1 T-perm-1: Action surface ↔ Operational discipline (tool reach vs. blast radius)

**Tension form:** wider tool reach is more useful and more dangerous. Per-tool gate policy under blast-radius taxonomy is the resolution lever.

**Surfaces in:** tool addition decisions, MCP server inclusion decisions, sandbox policy, HITL trigger catalog.

**Resolution shape:** tier tools by blast radius (read-only / contained-write / external-write / irreversible); apply gate policy per tier; HITL on the high tiers; sandbox on the contained tiers.

### 3.2 T-perm-2: Information substrate ↔ Operational discipline (state durability vs. cost / context cost)

**Tension form:** more durable, denser, longer-lived state is more useful and more expensive (token cost, storage cost, attention cost). Pruning, compaction, and tier-residence policy are the resolution levers.

**Surfaces in:** memory-tier decisions, prompt-cache strategy, context-window budget, pruning policy, vector-store-vs-filesystem-vs-ledger decisions.

**Resolution shape:** tier state by durability requirement; compact or prune the upper tiers; cite explicitly which tier each state element lives in.

### 3.3 T-perm-3: Control plane ↔ Operational discipline (parallelism vs. retry / breaker semantics)

**Tension form:** more parallelism is faster and harder to make reliable. Single-threaded-write defaults, idempotency-key generation, and per-key retry coordination are the resolution levers.

**Surfaces in:** multi-agent topology, tool fan-out, pipeline parallelism, sub-agent delegation.

**Resolution shape:** parallelism is a deliberate per-decision opt-in, not a default. Where parallelism is adopted, idempotency contracts must be specified per side-effecting tool.

---

## 4. Axis-collapse antipatterns

| Antipattern | Symptom | Correction |
|---|---|---|
| **All-operational-discipline** | Every decision tagged operational discipline because "reliability matters" | Locate the *origin* of the decision; tag that as PRIMARY. Operational discipline is SECONDARY when reliability is a consequence of the decision, not its origin. |
| **Axis-by-voice** | Tagging the axis based on which voice happens to be in the room | Tag based on the decision's content, not its convener |
| **Diffuse PRIMARY** | A decision tagged PRIMARY on three axes | The decision is too broad; split into three ADRs |
| **Substrate-as-axis** | Tagging substrate as a separate axis | Substrate is not an axis; deployment surface and information substrate cover it |
| **HITL-as-axis** | Tagging HITL as a separate axis | HITL placement is control-plane; HITL primitive is operational discipline; HITL trigger catalog is operational discipline |

---

## 5. Quick-reference tag table

| Decision class | Typical PRIMARY axis | Typical SECONDARY axes |
|---|---|---|
| Multi-agent topology | Control plane | Information substrate, Operational discipline |
| Tool contract / MCP server | Action surface | Operational discipline |
| State durability tier | Information substrate | Operational discipline |
| Retry / breaker policy | Operational discipline | Control plane |
| Provider abstraction shape | Information substrate | Action surface, Operational discipline |
| Sandbox isolation policy | Operational discipline | Action surface, Deployment surface |
| HITL placement | Control plane | Operational discipline |
| HITL primitive (the queue, palette, resume) | Operational discipline | Control plane |
| Observability backend | Operational discipline | Deployment surface |
| Durable-execution substrate | Operational discipline | Control plane, Deployment surface |
| Filesystem-as-substrate adoption depth | Information substrate | Deployment surface |
| Secrets abstraction | Operational discipline | Deployment surface |
| Local-dev vs. cloud-managed | Deployment surface | (all others SECONDARY at most) |
