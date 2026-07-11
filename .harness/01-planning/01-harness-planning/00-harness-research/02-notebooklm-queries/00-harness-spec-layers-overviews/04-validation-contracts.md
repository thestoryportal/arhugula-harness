# Spec Layer: Validation Contracts

The specifications for the custom multi-LLM agent harness do not rely on a single validation layer. Instead, they implement validation contracts as a **layered, deterministic cascade** distributed across the Information Substrate, Action Surface, Control Plane, and Operational Discipline axes. This architecture is designed to capture, classify, and isolate failures—shifting from simple syntactic checks to runtime sandbox containment, logical retry-exit loops, and out-of-loop meta-evaluations.

Here is exactly how these validation contracts are architected and enforced across the specifications:

### 1. Syntactic and Input Validation (Boundary Verification)
The outermost layer of the harness ensures that all inputs, schemas, and writes adhere to strict structural constraints before execution ever occurs:
*   **Constrained Decoding (Syntactic Parsing)**: To guarantee that LLM outputs conform to target schemas, the specifications utilize grammar-guided decoding layers (such as `XGrammar` [371] or `Outlines` [371]) to enforce 100% compliance at the token-generation level. This bypasses the need for post-hoc syntactic parsing and mitigates "Format Tax" reasoning degradation by keeping schemas pre-compiled and optimized [363].
*   **Tool Contract Invariants**: During design-time tool registration, the harness enforces a mandatory schema validation check. Any tool contract submitted without a declared `minimum_tier` parameter is immediately rejected [540].
*   **Idempotency-Keyed Write Validation**: To prevent duplicate executions of side-effecting tools across retry or replay cycles, the write seam (C3-pole) validates incoming ledger writes [758]. Writes are strictly keyed on the `(thread_id, step_id, idempotency_key)` tuple, ensuring that repeated identical operations resolve as safe no-ops [758, 760].

### 2. Sandbox, Containment, and Access Validation (The Execution Gate)
When an agent attempts to execute a tool or run generated code, the harness dynamically validates its security permissions and containment boundaries:
*   **5-Axis Multiplicative Gate-Level Formula (`T-perm-1`)**: Real-time tool-call validation is handled by a monotonically rising `max()` composition rule [590]:
    $$	ext{gate\_level} = \max(	ext{per\_tool\_gate\_level}, 	ext{per\_mcp\_server\_trust\_tier\_floor}, 	ext{persona\_tier\_floor}, 	ext{blast\_radius\_floor}, 	ext{sandbox\_tier\_floor})$$
    If the resolved gate level evaluates to `ask`, the tool call is blocked and rewritten into a human-in-the-loop (HITL) variant [567, 570]. If it evaluates to `deny`, the execution is structurally rejected and routed directly to a restricted-palette human gate [692, 693].
*   **Sub-Agent Monotonic-Ascension Validation**: At sub-agent dispatch, the Control Plane and Action Surface specifications enforce a strict containment contract [565, 669]. A child sub-agent’s sandbox isolation tier must always meet or exceed its parent's tier ($	ext{sub-agent tier} \geq 	ext{parent tier}$). Any attempt to downgrade isolation structurally fails and triggers a `policy_override` violation event [692].
*   **Failure-Class Taxonomies**: Failures are programmatically validated and mapped into explicit, cause-attributed schemas [378, 382]. For example, sandbox violations are classified into the `sandbox.fail.class` enum [584] (`escape_attempt`, `egress_denied`, `timeout`, `oom`, `signal`, `exit_nonzero`, `policy_override`), while secrets failures are categorized via the `secret.fail.class` enum [553] (`secret_unknown`, `secret_unavailable`, `secret_expired`, `secret_locked`, `secret_revoked`) to dictate exact retry-or-escalate behavior.

### 3. Logical Gating and the Pre-HITL Escalation Staircase
If a tool execution fails or fails to meet programmatic verification predicates, the Control Plane executes a structured escalation staircase to manage recovery before involving the human operator:
*   **The Discriminated Five-Class Fail Taxonomy**: Under `validator.fail.class` [702], validation failures are classified into five distinct buckets:
    1.  `transient-retry`: Retried via standard exponential backoff with full jitter.
    2.  `Reflexion-recoverable`: Triggers an intra-attempt verbal reinforcement loop where evaluator feedback is stitched back into the context window for the next trial [382].
    3.  `HITL-recoverable`: Pauses execution and requests human intervention.
    4.  `permanent-fail-exit`: Automatically **skips the retry staircase** for high-risk, cross-trust-boundary operations (such as untrusted MCP calls or local-terminal writes) [683, 702] and escalates directly to a restricted-palette human gate.
    5.  `terminal-fail-exit`: Instantly halts the workflow and triggers a terminal notification [702].
*   **Model-Tier Escalation**: On the second consecutive validation failure, the staircase executes a **model-tier escalation** [659, 669]. It programmatically hot-swaps the active model for a more capable reasoning family (e.g., upgrading a faster `Haiku` worker to `Sonnet` or `Opus`) to resolve the reasoning bottleneck before finally falling back to a human gate on the third failure [659, 669].
*   **Asymmetric Two-Agent Verification**: For high-risk operations, the specifications allow composing an independent, parallel **Verifier Agent** [389]. To prevent semantic bias or context poisoning, the verifier runs in parallel as a read-only observer with its inputs strictly restricted or disabled [389]. Its programmatic verdict is fed directly to the validator-escalation gate.

### 4. Cryptographic Ledger and Trace Integrity Validation
To ensure compliance-readiness and protect against tampering, the harness treats the state history itself as a verifiable cryptographic ledger:
*   **State-Ledger Hash-Chaining**: Every F2 state-ledger entry is canonicalized to a deterministic byte sequence using the RFC 8785 JSON Canonicalization Scheme (JCS) and hashed via SHA-256 [757]. Each entry embeds the prior entry's hash in its `prior_event_hash` field [754]. The downstream operator can mathematically verify the ledger's integrity on-demand by traversing this chain [757].
*   **Cross-Sibling Merkle-Root Verification**: For parallel sub-agent runs, the parent orchestrator reads sibling F2 entries, hashes their respective chains, constructs a Merkle tree, and writes the resulting cryptographic root as a `sibling_ledger_root` to a separate `parent_fanout_close_entry` primitive [677, 679].
*   **Multi-Tenant Signing Key Rotation**: At the `multi-tenant-compliance` tier, entries are cryptographically signed using an asymmetric key fetched via the `fetch_secret` abstraction [697]. Key rotations are validated using a **two-row rotation verification pattern** that forces the old and new keys to co-sign the rotation boundary [697].

### 5. Out-of-Loop Evaluators and Drift Detection
To monitor alignment and prevent systemic performance degradation over time, the Operational Discipline axis separates runtime gates from out-of-loop evaluations:
*   **`gen_ai.eval.kind` Separation**: Telemetry traces explicitly separate inline enforcement from offline evaluation using the `gen_ai.eval.kind` attribute [852], distinguishing `inline_gate` (blocking runtime validators) from `offline_judge` (non-blocking meta-evaluations).
*   **Separate Child Span Emission**: To preserve full traceability for meta-evaluations (evaluating the evaluators), the spec mandates that offline evaluations must emit as **separate child spans** rather than inline span events [853]. This enables the harness to run multi-agent evaluations over prior traces without context pollution.
*   **Alignment-Floor Drift Detection**: The harness continuously measures five core operator-burden primitives (including expected HITL invocations, expected sandbox violations, and cache-hit-rate alignment floors) [852]. If the computed ratio falls below a defined threshold, a `gen_ai.eval.alignment_floor` drift-detection event is emitted to signal that the model’s real-world behavior has drifted and needs re-baselining [853].
*   **Error-Analysis-First Calibration**: The out-of-loop evaluation suite utilizes Hamel Husain's alignment-loop methodology, establishing binary pass/fail assertions calibrated against a 100-trace human gold set and measuring inter-annotator agreement using chance-corrected Cohen's Kappa [326].
