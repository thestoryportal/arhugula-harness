# Spec Layer: Reliability and Recovery

The specifications for the custom multi-LLM agent harness implement reliability and recovery as a multi-layered, deterministic architecture. Rather than relying on fragile, in-process runtime loops, the harness wraps stochastic model calls in rigid execution boundaries, crash-recovery mechanisms, and fail-safe fallback policies.

The core reliability and recovery frameworks are built across the following five operational layers:

### 1. Durable Execution and Replay Resumption (F3)
To ensure the harness can survive arbitrary process crashes or host failures, the Control Plane commits to a **Durable-Execution-as-the-Coordination-Spine** contract [608]. This framework is governed by a five-element engine-class taxonomy [654]:
*   **`event-sourced-replay`** (e.g., Temporal or DBOS-native) [654].
*   **`save-point-checkpoint`** (e.g., LangGraph-native checkpointers) [654].
*   **`pure-pattern-no-engine`** (filesystem-journal backed) [654].
*   **`reconciler-loop`** (Kubernetes-native etcd state) [654].
*   **`WAL-segment`** (append-only segment log) [654].

Regardless of the underlying engine, the system enforces a strict **durable capability floor** [608]. Upon resuming from a crash, the engine emits a `workflow.resumption` event containing a dedicated `resumption.kind` attribute (`engine_replay`, `save_point_resume`, `journal_resume`, `reconciler_converge`, or `segment_replay` [657]). This protocol forces the runtime to reconstitute state by replaying completed steps, short-circuiting previously executed tool operations, and reading cached outputs directly from the ledger rather than re-triggering side effects [657].

### 2. Idempotency Keys and the State Ledger
To support safe re-execution during replay loops, the harness integrates a **two-phase-commit-by-convention** using strict idempotency controls [322].
*   **Idempotency Key Construction**: Every side-effecting tool execution or state transition requires an idempotency key structured deterministically as:
    $$	ext{idempotency\_key} = 	ext{sha256}(	ext{conversation\_id} \mathbin{\Vert} 	ext{step\_index} \mathbin{\Vert} 	ext{tool} \mathbin{\Vert} 	ext{canonical\_args})$$ [404]
*   **The State-Ledger Contract**: This key is coupled to an append-only State Ledger [751]. Every ledger entry is committed in a strict, structured, line-by-line JSONL format [758] under a six-field record signature:
    $$	ext{Record} = (	ext{action\_id}, 	ext{idempotency\_key}, 	ext{actor}, 	ext{response\_hash}, 	ext{timestamp}, 	ext{prior\_event\_hash})$$ [754]
*   **Cryptographic Hash-Chaining**: To prevent log tampering or state corruption, each entry's `prior_event_hash` cryptographically chains to the preceding entry using deterministic RFC 8785 JSON Canonicalization Scheme (JCS) serialization and SHA-256 hashing [757].

If a duplicate write with an identical key is attempted during recovery, the ledger treats it as a safe, idempotent no-op and returns the pre-cached result [758].

### 3. Jittered Backoff, Rate-Limit Isolation, and Retry Budgets
The harness encapsulates all remote model calls in a deterministic retry wrapper designed to prevent cascading network failures and "retry storms" [404]:
*   **Full Jitter Backoff**: For standard transient failures, the harness utilizes **Full Jitter** exponential backoff as its default algorithm [404]. Based on empirical SRE profiling, Full Jitter minimizes total API call counts and smooths out synchronized contention spikes better than Equal or no-jitter alternatives [401].
*   **Discriminative Error Classification**: The recovery layer distinguishes between different HTTP and provider-level errors:
    *   *HTTP 429 (`rate_limit_error` [401])* instantly pauses execution and honors the provider's `retry-after` header [401].
    *   *HTTP 529 (`overloaded_error` [401])* represents provider-side capacity overload [401]. It triggers backoff retries but does not count against the agent’s internal retry quota [401].
    *   *HTTP 402* returned by Anthropic Max subscriptions during rate-limit exhaustion is mapped to a 429 backoff [401].
*   **Retry Budgets**: To prevent runaway loops under load, the harness enforces a **global retry budget** that caps total retry attempts as a fraction of overall forward traffic (recommended at a maximum of 10% [404]).

### 4. Circuit Breakers and Cross-Family Fallback Chains
If a particular model endpoint degrades permanently, the harness uses circuit breakers to route around the failure [404]:
*   **Per-Endpoint Circuit Breakers**: Breakers are pinned per `{provider, model}` instance [404]. If consecutive slow calls or failures exceed a defined sliding-window threshold [401], the breaker transitions to `OPEN`, immediately bypassing the model and emitting a `breaker.tripped` event [401].
*   **The Seven-Attribute Schema**: Tripped events are recorded under a canonical namespace containing: `scope`, `from_state`, `to_state`, `trigger_count`, `permanent_fail_repeats`, `tool_id`, and `model_version` [401].
*   **Cross-Family Fallback**: When an active breaker trips, the model-routing engine shifts execution down a fallback chain [404, 642].
*   **Provider-Sticky Session Keys**: To avoid destroying high-value provider-side prompt caches during fallback, the harness employs **provider-sticky session keys** [401]. The routing engine exhausts same-provider model variants (e.g., falling back from Claude Opus to Claude Sonnet) before executing a cross-family switch (e.g., Anthropic to OpenAI), which completely invalidates prompt-cache prefix structures [401, 642].

### 5. The Pre-Human-in-the-Loop (HITL) Escalation Staircase
For semantic or programmatic errors, the Control Plane operates a **pre-HITL escalation staircase** that attempts automated recovery before notifying the operator [700]:
*   **Five-Class Validator Fail Taxonomy**: Failures are discriminated and mapped to specific recovery paths [702]:
    1.  `transient-retry`: Routes back to the jittered backoff loop [702].
    2.  `Reflexion-recoverable`: Initiates an in-loop verbal self-correction cycle [702]. Evaluator feedback (unit-test failures, schema mismatches) is summarized and stitched back into the context window for a clean-context re-attempt [382].
    3.  `HITL-recoverable`: Pauses the thread and opens a manual approval queue.
    4.  `permanent-fail-exit`: Immediately bypasses the retry staircase [702]. High-risk boundaries (untrusted MCP calls, local-terminal commands, cross-family fallbacks) escalate directly to a restricted-palette human gate [683, 702].
    5.  `terminal-fail-exit`: Halts the workflow instantly and throws a critical system alert [702].
*   **Staircase Execution**:
    *   *First Failure*: Triggers standard retry with backoff or Reflexion [702].
    *   *Second Failure*: Triggers a **model-tier escalation** [659, 669]. The harness hot-swaps the active model to a more capable, higher-tier reasoning family (such as swapping a fast `Haiku` worker for a `Sonnet` or `Opus` model) to resolve the logical roadblock [659, 669].
    *   *Third Failure / Budget Exhaustion*: Escalates to a validator-escalation HITL gate, packaging all execution traces, failed attempts, and alternatives for the operator [702].
*   **Adaptive Early-Stopping (Plateau Detection)**: If the evaluator detects that consecutive Reflexion attempts fail to yield improvement ($\Delta	ext{score} < \epsilon$ over three iterations), the harness halts the loop early to conserve tokens, skipping straight to human escalation [363].
