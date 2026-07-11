# Spec Layer: Evaluations (Evals)

The specifications implement evaluations ("evals") and validation as a highly disciplined, multi-layered architectural cascade. Rather than treating evaluations as passive logging steps, the harness positions them as active, deterministic outer-loop boundaries that protect against model non-determinism, catch reasoning failures, and monitor real-world alignment.

The specifications codify these evaluation mechanisms across five primary dimensions:

### 1. The Three-Layer Validator Cascade
All tool executions and model outputs flow sequentially through a **deterministic validation staircase** [378, 382, 383] designed to catch errors at the lowest-overhead tier possible before escalating to more expensive reasoning models or humans:
*   **L1 (Syntactic & Type Validation)** [383]: This layer uses **grammar-guided constrained decoding** (via open engines like `XGrammar` [371] and `Outlines` [371], or vendor-native strict-mode JSON schemas) to force the model to output syntactically valid JSON matching target schemas at the token-generation level. This eliminates raw parsing failures upfront while keeping compiling overhead near-zero.
*   **L2 (Semantic & Programmatic Validation)** [383]: If an output passes syntax, it undergoes programmatic semantic verification. This includes running local code-based assertions, regex filters, and executing generated code within secure sandboxes (such as Firecracker/gVisor microVMs) to verify test-cases or runtime safety [383]. Programmatic assertions are modeled after the *PROMPTEVALS* dataset of human-authored criteria [380].
*   **L3 (Judgmental / LLM-as-a-Judge & Human Gates)** [383]: Outputs that require qualitative grading are routed to scoped, binary LLM-as-a-judge classifiers [383]. If the judge detects a failure, the loop is classified under a *Reflexion-recoverable* path [383] (retrying with verbal feedback [382]) or escalated to a Human-in-the-Loop (HITL) gate [383].

### 2. LLM-as-a-Judge Bias Mitigations
To prevent evaluation dashboards from being corrupted by qualitative model biases, the harness implements the **Zheng et al. judge-bias mitigations** [389] to mathematically correct scoring anomalies [362]:
*   **Position Bias** [362]: Models often favor whichever option is presented first. The harness executes a pairwise comparison with a **random position-swapping protocol** [362], rejecting and retrying the evaluation if the judge's score is inconsistent when the positions are inverted [362].
*   **Verbosity & Formality Biases** [362]: Evaluator models exhibit strong preferences for longer or more formally padded outputs, even when they contain reasoning errors [362]. The specifications mitigate this by mandating strict length-normalization inside the judge's prompt and enforcing explicit rubric-based grading [362].
*   **Self-Enhancement Bias** [362]: Models tend to inflate scores for their own family's outputs [362]. The harness forces **cross-family judging** [362] (e.g., utilizing a GPT-class judge to score a Claude-generated artifact) to guarantee neutrality.
*   **Math and Logical Failures** [362]: Default LLM judges often mis-grade technical work [362]. The spec mandates **reference-guided grading** [362], feeding the evaluator model a step-by-step gold-standard solution and chain-of-thought instructions [362], which drops evaluator failure rates from 14/20 down to 3/20 [362].

### 3. Hamel Husain & Shreya Shankar Calibration Loops
The specifications reject prefab, off-the-shelf "helpfulness" metrics in favor of an **error-analysis-first methodology** [326] aligned to real human judgment [326]:
*   **Binary Pass/Fail Scoring** [326]: The system utilizes strict binary pass/fail assertions rather than inconsistent, subjective Likert scales [326]. It enforces a rule where only the *first upstream failure* of a multi-turn trace is annotated [326], allowing developers to isolate the root-cause failure point.
*   **Cohen’s Kappa (κ) Agreement** [326]: To validate the judges themselves, the harness measures chance-corrected agreement (Cohen's κ) between candidate LLM judges and principal human experts [326]. The system is blocked from deploying unless the judge maintains a **κ ≥ 0.7** agreement threshold [326].
*   **Shankar's "Who Validates the Validators?" Loop** [327]: To combat "criteria drift" (where the human definition of a "good" output evolves as they see more agent behavior [327]), the system continuously executes a mixed-initiative alignment loop [327]. A candidate judge is tested against a running 100-trace gold set [327]; if its True Positive Rate (TPR) or True Negative Rate (TNR) drifts below acceptable bounds, the judge prompt is re-baselined [327].

### 4. Telemetry and Dashboard Ingestion
Evals are deeply integrated into the OpenTelemetry (OTel) GenAI span hierarchy to allow operators to inspect system health:
*   **Separate Child Span Emission** [853]: The specifications mandate that evaluation scores and judge actions must emit as **separate child spans** (`skill.activation` [576] or `hitl.gate.evaluated` [698]) rather than being flattened into span events [853]. This is a non-negotiable requirement that preserves trace identity, making "meta-evaluations" (evaluating the performance of the evaluators) possible.
*   **gen_ai.eval.kind** [852]: Every evaluation span carries this discriminator attribute to cleanly separate runtime in-loop blockades (`inline_gate`) from offline out-of-loop judges (`offline_judge`) [852].
*   **Five Operator-Burden Eval Primitives** [852]: The Operational Discipline axis continuously aggregates five specific metrics onto the operator's dashboard to detect degradation:
    1.  `expected_hitl_invocations_per_session` [852]: Measures approval request volume to detect operator fatigue or over-automation.
    2.  `expected_sandbox_violations_per_session` [852]: Tracks security boundary breach attempts.
    3.  `sandbox-tier-routing-accuracy` [852]: Evaluates the accuracy of the 5-axis sandbox assignment engine.
    4.  `cache-hit-rate-alignment-floor` [852]: Verifies if prompt-caching prefix structures are hitting their performance floors.
    5.  `routing-accuracy-holdout` [852]: Measures the accuracy of fallback-chain routing decisions against human intent.
*   **Alignment-Floor Drift Events** [853]: If any of these five metrics fall below the operator-defined floor (e.g., if a model update causes prompt caching to fail or judge κ to drop), the harness triggers a `gen_ai.eval.alignment_floor` event on the trace to signal that the model’s real-world behavior has drifted and needs re-baselining [853].

### 5. Three-Step Gate Cadence
To ensure continuous safety, the specifications construct an explicit **three-step testing and validation cadence** [327]:
*   **Pre-Commit (CI Gate)** [327]: Executes cheap, deterministic, code-based assertions (regex, JSON-schema, compilation checks) over a 20-50 trace development fixture [326]. This gate must run in under 30 seconds to maintain developer velocity [326].
*   **Pre-Deploy (Release Gate)** [327]: Executes the aligned LLM-as-a-judge over a 100-trace held-out gold set [327]. Release to production is gated on the judge satisfying strict **TPR ≥ 0.90, TNR ≥ 0.85, and Cohen's κ ≥ 0.7** thresholds against human ground truth [326, 327].
*   **Post-Deploy (Weekly Audit)** [327]: Operators manually conduct error analysis over at least 100 fresh production traces every week [326]. If a new systemic failure mode is discovered, a new programmatic assertion or judge criteria is minted and checked directly into Git alongside the application code [326].
