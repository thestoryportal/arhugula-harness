# Probabilistic-Deterministic Boundary

The single most load-bearing discipline in agent-harness architecture. Every architectural element lives on one side of this boundary; production reliability lives on the deterministic side; the LLM lives on the probabilistic side.

---

## 1. The boundary

```
        ┌──────────────────────────────────────────┐
        │                                          │
        │   PROBABILISTIC SIDE (LLM inference)     │
        │                                          │
        │   • plan generation                      │
        │   • code generation                      │
        │   • content generation                   │
        │   • intent classification                │
        │   • judgment under ambiguity             │
        │   • language understanding               │
        │   • tool-call argument selection         │
        │   • LLM-as-judge (in eval, not in gate)  │
        │                                          │
        └──────────────────┬───────────────────────┘
                           │
        ═══════════════════╪═══════════════════════  THE BOUNDARY
                           │
        ┌──────────────────┴───────────────────────┐
        │                                          │
        │   DETERMINISTIC SIDE (outer harness)     │
        │                                          │
        │   • schemas / typecheckers / linters     │
        │   • validators / gates                   │
        │   • idempotency keys                     │
        │   • sandboxes                            │
        │   • retry policies (with full jitter)    │
        │   • circuit breakers                     │
        │   • timeouts (per-attempt + total)       │
        │   • durable execution                    │
        │   • audit ledger                         │
        │   • secrets store                        │
        │   • observability spans                  │
        │   • rate limiters                        │
        │   • RBAC / trust gates                   │
        │                                          │
        └──────────────────────────────────────────┘
```

**Operating principle:** *Production reliability lives in the deterministic outer harness.* When a reliability property is asserted, locate the mechanism that makes it true; if the mechanism is "the LLM will be careful," the property is not asserted, only hoped for.

---

## 2. Common boundary placements

| Concern | Probabilistic side | Deterministic side |
|---|---|---|
| **Tool calling** | LLM selects tool, generates arguments | Schema validates arguments; strict mode enforces shape; rejected calls trigger reflexion or error |
| **Structured output** | LLM generates structured payload | Schema validation; on validation failure, retry-with-feedback |
| **Code generation** | LLM emits code | Linter, typechecker, sandbox execution, test pass/fail |
| **HITL trigger** | LLM may signal need for HITL via reasoning | Trigger catalog deterministically routes to operator for tool calls in defined trust tiers |
| **Recovery from failure** | LLM may propose recovery | Circuit breaker, retry policy, durable execution checkpoint, rollback |
| **Idempotency** | LLM may attempt to re-issue an action | Deterministic idempotency key generation per `keyShape`; retry coordinator; once-and-only-once at the side-effect boundary |
| **Trust / authorization** | LLM may request access | Per-tool gate policy (allow / ask / deny) keyed on blast-radius taxonomy |
| **Eval gate vs. eval observation** | LLM-as-judge produces a score | Deterministic threshold gates the score; the gate is the deterministic element |
| **Cost / rate limiting** | LLM may make as many calls as the harness allows | Rate limiter, total-budget timeout, breaker, per-call cost cap |
| **Audit** | LLM emits action with reasoning | Deterministic ledger entry with hash-chain integrity, structure-not-content |

---

## 3. Antipatterns: probabilistic-side reliability

These patterns place reliability on the probabilistic side. They fail under load and under adversarial inputs. Replacing them with deterministic-side equivalents is the discipline.

### 3.1 "Prompt the model to be careful"

**Symptom:** "We instruct the model to confirm before running irreversible operations."

**Why it fails:** the model's compliance is non-deterministic. Adversarial inputs, prompt injection, or simple drift will produce confirmations that do not happen.

**Correction:** trust gate keyed on tool blast radius. Irreversible operations land in a tier that requires HITL approval at the deterministic harness layer, not at LLM judgment.

### 3.2 "Let the model retry"

**Symptom:** "On error, the model can decide to retry."

**Why it fails:** model may retry without backoff, may retry indefinitely, may retry idempotently when the previous call had a side effect.

**Correction:** deterministic retry policy with full jitter, per-attempt and total-budget timeouts, idempotency-key coordination, breaker on persistent failure.

### 3.3 "LLM-as-judge as the gate"

**Symptom:** "We run a judge model to score the output, and accept if score > threshold."

**Why it fails (partly):** the judge is itself probabilistic. The judge's alignment with ground truth must be measured (out-of-loop) before its score is trusted. A single-judge gate without judge-human alignment is a feel-good gate.

**Correction:** the judge can be in the loop, but the threshold is a deterministic element, AND the judge's alignment is measured against a held-out human-labeled set out of loop. The gate's pass/fail rate at the threshold is itself a property to evaluate. (See `c5-validation-contract` and `c8-eval-engineer` voices for the gate-vs-eval split.)

### 3.4 "Schema in the prompt"

**Symptom:** "We tell the model to output JSON matching this schema."

**Why it fails:** the model occasionally outputs malformed JSON. Production cannot tolerate "occasionally."

**Correction:** structured-output API (Anthropic tool-use parameter, OpenAI structured outputs, etc.) enforces shape at the API boundary. Schema validation is deterministic.

### 3.5 "Confidence in the output"

**Symptom:** "The model says it is confident, so we proceed."

**Why it fails:** model self-reported confidence is poorly calibrated and easily contaminated by sycophancy.

**Correction:** confidence is observed by the deterministic harness — does the output pass the gate, does the test pass, does the schema validate. Model self-confidence is logged for debugging, not gated on.

### 3.6 "Sandbox by prompt"

**Symptom:** "We tell the model not to access the network."

**Why it fails:** the sandbox is the prompt, which is to say there is no sandbox.

**Correction:** the sandbox is a process-isolation, network-namespace, filesystem-namespace, or microVM boundary that the LLM cannot escape regardless of what it produces. The sandbox is deterministic.

---

## 4. Where the LLM legitimately owns reliability

The LLM is the right component when:

- The task is genuinely probabilistic (translation, summarization, classification under ambiguity).
- The output will be consumed by a downstream deterministic check (the LLM proposes; the harness disposes).
- The cost of a wrong answer is low or the failure mode is recoverable.
- A deterministic alternative does not exist or is materially worse.

**Operating principle:** the LLM is a powerful but unreliable component. The deterministic harness is the reliability layer. Both are needed; production-grade architecture is about *which decisions live where*.

---

## 5. Boundary placement in each phase

| Phase | Boundary discipline use |
|---|---|
| **Phase 2 — persona surfacing** | When the operator surfaces a reliability target (e.g., "99.9% completion rate"), name the deterministic mechanism that will deliver it. Do not allow reliability targets to be set without identifying which harness layer carries them. |
| **Phase 3a/3b — ADRs** | Every ADR's Decision states which side of the boundary the decided element lives on. Rationale cites the failure mode prevented; if the failure mode is "the LLM might..." the prevention mechanism must be deterministic. |
| **Phase 3c — integration verification** | Cross-axis tensions often surface as boundary disputes (e.g., "does the validator live in the LLM or in the gate"). The verification report names the boundary placement explicitly. |
| **Phase 3d — ADD consolidation** | The ADD's section structure surfaces the boundary repeatedly: every operational-discipline decision is on the deterministic side; the ADD's prose makes this visible by stating boundary placement at first reference. |

---

## 6. Quick test

For any architectural element X, ask:

1. **What guarantees X's reliability property?**
2. **Is the guarantor a schema, validator, gate, idempotency key, sandbox, breaker, retry policy, or audit ledger?**

If yes → X is on the deterministic side; the boundary is correctly placed.
If no, and the guarantor is "the LLM" → X is on the probabilistic side; the boundary is incorrectly placed for a reliability-critical property; a deterministic mechanism must be added.
If no, and the guarantor is "I haven't decided" → the architectural decision is incomplete.
