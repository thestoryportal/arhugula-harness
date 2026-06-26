# Persona-Surfacing Protocol — Phase 2

The structured dialogue protocol the systems architect skill applies in Phase 2. The protocol elicits persona, workloads, scale, integration surface, hard constraints, and soft preferences without proposing architectural decisions.

---

## 1. Operating principles

1. **Elicit, do not assume.** Every dimension is probed; if the operator cannot answer, the gap is captured as a finding, not filled by inference.
2. **Capture incidental answers.** When the operator answers an unasked question while answering an asked one, capture the answer and continue with unasked dimensions.
3. **Surface implications, defer decisions.** When the answer obviously implies an architectural decision, name the implication and defer the decision to Phase 3a/3b. The persona document records the implication; it does not record the decision.
4. **Distinguish hard from soft.** Hard constraints have non-negotiable sources (compliance, contractual, physical); soft preferences are tractable and revisable. Tag each constraint accordingly.
5. **Stay inside the persona scope.** Phase 2 surfaces persona; it does not architect. If the operator pulls toward architecture, redirect: "That decision belongs in Phase 3; for now, what does it imply about the persona?"

---

## 2. The six dimensions, in order

The dimensions are probed in this order because earlier answers shape later questions.

### 2.1 Dimension 1 — User

**Elicit:** who operates the harness.

**Probe questions:**

1. Who runs the harness day-to-day? Sole operator, small team, or multi-tenant?
2. What is the operator's role and operating expertise? (engineer, analyst, content creator, ops, mixed)
3. Is the operator the same person across sessions, or does it vary?
4. Does the operator have direct access to the harness's host environment, or is the operator interacting through a layer (CLI, web UI, API consumer, scheduled trigger)?

**Follow-up triggers:**

- "Multi-tenant" → probe tenant-isolation expectations (data, cost, model access).
- "Varies across sessions" → probe whether session-state continuity is required.
- "Layer between operator and host" → probe the layer's shape (this affects deployment surface).

**Stop condition:** operator can be described in one sentence including role, expertise level, and access pattern.

### 2.2 Dimension 2 — Workloads

**Elicit:** what task classes the harness must handle.

**Probe questions:**

1. What are the primary task classes? (software engineering, content creation, pipeline automation, research, customer support, computer-use, data analysis, other)
2. What is the typical work-unit shape — single short task, multi-step session, long-running pipeline?
3. What is the cardinality — one task at a time, parallel tasks, batch?
4. Are there secondary task classes that surface less often but must be supported?
5. Is there a task class the harness must explicitly NOT handle (out-of-scope)?

**Follow-up triggers:**

- Multiple primary task classes → probe whether they share infrastructure or are siloed.
- "Long-running pipeline" → probe expected duration; this surfaces durable-execution implications without committing to a substrate.
- "Computer-use" → probe sandbox/isolation expectations; this surfaces reliability target.
- Out-of-scope task class → capture explicitly; useful for scoping later.

**Stop condition:** primary and secondary task classes enumerated; typical work-unit shape stated for each.

### 2.3 Dimension 3 — Scale

**Elicit:** concurrency, throughput, retention, reliability target.

**Probe questions:**

1. How many concurrent harness instances are expected? (1, low single digits, tens, hundreds, more)
2. How many tasks per day, per week? (rough order of magnitude)
3. How long is the typical session? (minutes, hours, days)
4. How long must task history and artifacts be retained? (current session, days, months, years)
5. What reliability target applies — completion rate, latency budget, availability? (99%, 99.9%, 99.99%, hard real-time)

**Follow-up triggers:**

- "1 concurrent instance" → confirm; this materially simplifies control plane.
- "Thousands of tasks per day" → probe burst pattern; reliability target needs concrete shape.
- "Retain for years" → probe whether the audit ledger is the retention surface or a separate system.
- "99.9% or higher" → name the implication: production reliability lives in the deterministic outer harness; the operator should understand that scale implies investment in validators, gates, and audit. Do not commit to mechanisms.

**Stop condition:** concurrency, throughput, retention, and reliability target each captured with at least order-of-magnitude precision.

### 2.4 Dimension 4 — Integration surface

**Elicit:** what external systems the harness must reach.

**Probe questions:**

1. What external APIs must the harness call? (cloud providers, SaaS, internal services)
2. What file systems must it read or write? (local disk, network filesystems, cloud storage)
3. What repositories must it operate on? (git, package registries)
4. What model providers are in scope? (Anthropic, OpenAI, others; cardinality)
5. What tool surfaces are required? (MCP servers, custom tools, computer-use, browser, terminal)
6. What integrations are explicitly out of scope?

**Follow-up triggers:**

- Multiple model providers → confirms multi-LLM commitment per V3 framing.
- "Computer-use" → probe whether this is design-time-only or production-target; affects deployment surface.
- "Cloud storage" → probe regions, encryption, latency expectations.
- Out-of-scope integrations → capture; protects against scope creep later.

**Stop condition:** every integration class is captured as in-scope or out-of-scope; the in-scope items have at least vendor or shape detail.

### 2.5 Dimension 5 — Hard constraints

**Elicit:** non-negotiable rules.

**Probe questions:**

1. Are there compliance requirements? (HIPAA, SOC2, GDPR, internal policies, contractual)
2. Are there latency budgets that are hard requirements (not preferences)?
3. Are there cost ceilings that are hard requirements?
4. Are there data-locality or data-residency requirements?
5. Are there vendor restrictions? (vendor allowlist, vendor blocklist)
6. Are there IP-handling rules? (no third-party-model on internal code, no logs of customer data, etc.)

**Follow-up triggers:**

- Compliance regime → probe specific obligations (audit, retention, encryption-at-rest, access logs).
- "No specific compliance" → confirm; this is a softer constraint set.
- Vendor restriction → capture explicitly; this can eliminate substrate choices in Phase 3b.

**Stop condition:** hard-constraint list enumerated; each item has a stated source (regulation name, contract, policy doc).

### 2.6 Dimension 6 — Soft preferences

**Elicit:** preferences that shape but do not bind decisions.

**Probe questions:**

1. What stack does the operator already know well? (languages, frameworks, runtimes)
2. What ecosystem does the operator prefer? (Anthropic-native, OpenAI-native, vendor-neutral)
3. Are there team conventions that should be honored? (testing style, observability tooling, deployment patterns)
4. Are there aesthetic or ergonomic preferences? (terminal-first vs. UI-first, declarative vs. imperative)

**Follow-up triggers:**

- Strong stack preference → capture as soft; do not let it bind decisions before Phase 3.
- "No preference" → capture; this widens the option space for Phase 3.

**Stop condition:** soft-preference list enumerated; each tagged as soft.

---

## 3. Output structure

The persona-surfacing session produces draft material for `Persona_Document_v1.md` with the following sections.

```
# Persona Document v1

## §1 Persona definition
{One paragraph capturing user, primary workloads, scale order-of-magnitude,
and integration-surface highlights. Written so that a downstream reader
can hold the persona in mind without rereading.}

## §2 User
{Output of Dimension 1.}

## §3 Workloads
{Output of Dimension 2; one subsection per primary task class plus a
list of secondary task classes.}

## §4 Scale
{Output of Dimension 3 with the four sub-fields explicitly tagged.}

## §5 Integration surface
{Output of Dimension 4 with in-scope and out-of-scope clearly separated.}

## §6 Hard constraints
{Output of Dimension 5; each item with stated source.}

## §7 Soft preferences
{Output of Dimension 6; each item tagged soft.}

## §8 Workload-shape implications
{For each primary workload class from §3, what it implies for each
of the five axes. This is implications-only; it does not commit to
mechanisms or specific patterns.}

## §9 Deployment-surface implications
{What the persona implies for deployment surface. If persona forces
a specific surface (e.g., "local-development design-time target"),
state it. If persona constrains the surface but does not pick, state
the constraints. If persona is neutral, state that.}

## §10 Persona-dependent decision pre-classifications
{Three lists:
- Persona-answered: decisions whose outcome the persona directly
  determines.
- Persona-constrained: decisions whose option space the persona
  narrows.
- Persona-open: decisions on which the persona has no bearing.

Each entry is a decision name with a short reason and the source
dimension(s) (§§2–7).}

## §11 Open items
{Dimensions or sub-fields the operator could not answer in this
session, with proposed next steps for closing each gap.}
```

---

## 4. What the protocol explicitly does NOT do

- **Does not propose architectural decisions.** Implications are surfaced; decisions are deferred.
- **Does not commit to a stack.** Stack-related answers are captured under §7 (soft preferences), not as commitments.
- **Does not assume a persona dimension.** If a dimension cannot be answered, it goes in §11 (open items) with a closing path; it is NOT filled by inference.
- **Does not introduce confidence tags inside the persona document beyond what V3 mandates.** V3's confidence schema applies to substantive factual claims, not to persona statements (which are operator-asserted, not researched).
- **Does not produce ADRs.** ADRs are Phase 3a/3b outputs.
- **Does not redirect to council voices.** The persona-surfacing session is operator-and-skill, not operator-and-council.

---

## 5. Anti-patterns specific to persona surfacing

| Anti-pattern | Symptom | Correction |
|---|---|---|
| **Persona inference** | "I'll assume a solo developer..." | Stop. Ask the operator. The persona is operator-asserted, not skill-inferred. |
| **Stack-as-persona** | Surfacing "the operator wants Temporal" as a persona attribute | Stack preference is a soft preference (§7). It is not a persona attribute. |
| **Architecture-as-persona** | "The persona is multi-LLM-with-filesystem-substrate..." | Multi-LLM is a project commitment (V3). Filesystem-substrate is a Phase 3a F-decision. Persona is the user/workloads/scale/integration/constraints. |
| **Premature decision** | Producing an ADR-shaped output during persona surfacing | Phase 2 produces the persona document, not ADRs. Capture implications; defer decisions. |
| **Hard-soft conflation** | Tagging operator preferences as hard constraints | Hard constraints have external sources (compliance, contract, policy). "I prefer Python" is soft. |
| **Dimension-skip** | Skipping a dimension because it "doesn't seem relevant" | Probe all six dimensions. If the answer is "not applicable," capture that explicitly; the absence is itself a finding. |
