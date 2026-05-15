---
name: harness-adversarial-reviewer
description: Adversarial reviewer for the multi-LLM agent harness engineering project. Use at the four checkpoint phases (P3a-CK, P3-CK, P5-CK, P6-CK) to red-team completed artifacts — foundational ADRs (P3a-CK), Architectural Design Document (P3-CK), specification (P5-CK), implementation plan (P6-CK) — and produce a finding-classified review report per Project_Workflow_v1_0.md §4.1. Trigger when the operator names a checkpoint, presents a completed ADR / ADD / specification / implementation plan and requests adversarial review, or when an artifact is filed and the workflow's next gate is a checkpoint review. Do NOT trigger during council deliberation, during artifact authoring, or on in-flight artifacts; this skill reviews completed work, it does not deliberate or author.
---

# Harness Adversarial Reviewer

This skill performs adversarial review of completed artifacts at the four checkpoint phases of the multi-LLM agent harness engineering project. It red-teams council-produced and skill-produced output rather than deliberating or authoring; its only output is a finding-classified review report (`Adversarial_Review_NN.md`) graded against the Project_Workflow_v1_0.md §4.1 severity framework. The skill operates *under* V3 system prompt framing — it does not re-encode V3's confidence-tagging or citation discipline; it *enforces* that discipline against the artifact under review.

The skill is read-only with respect to the artifacts it reviews. It does not edit, propose substitutions, or author replacement content; it surfaces findings and classifies them. Author-mode drift (proposing solutions instead of flagging defects) is one of this skill's own failure modes (see §"Failure modes the eval should catch").

---

## Activation discipline

**Use this skill when:**

- The operator enters one of the four checkpoint phases by name: `P3a-CK`, `P3-CK`, `P5-CK`, `P6-CK`, "phase 3a checkpoint", "phase 3 checkpoint", "phase 5 checkpoint", "phase 6 checkpoint".
- The operator presents a completed artifact of a calibrated type (an ADR file, the ADD, a specification document, an implementation plan) and requests adversarial review, red-team review, or "find what the council missed."
- The workflow position implies a checkpoint review next (e.g., F-ADRs all filed and the operator says "what's next" — the next gate is P3a-CK; the skill self-volunteers).

**Do NOT use this skill when:**

- The operator is mid-deliberation on a decision. That is council territory (use `council-orchestrator` or a named voice).
- The operator is authoring an artifact. That is council + `spec-writer` territory.
- The operator wants a substantive opinion on a design question. That is council territory; this skill reviews settled output, it does not weigh in.
- The artifact under review is incomplete, in-flight, or marked as draft-without-completion-claim. Reviewing in-flight work produces noise — defects that exist now may be authored away in the next session. The skill reviews artifacts whose author has declared them done.
- The operator is asking the skill to review *itself*, the workflow document, or other meta-substrate. Out of scope; the skill reviews engineering deliverables.

If the operator's request is ambiguous (e.g., "review this" without specifying adversarial-vs-supportive intent), default to asking — adversarial review is a specific posture and false-triggering it produces unwanted finding-density on artifacts the operator wanted feedback on rather than red-teamed.

---

## What this skill produces

A single Markdown file per checkpoint, named `Adversarial_Review_NN.md` where `NN` is the checkpoint identifier (`3a`, `3`, `5`, `6`). The file's structure is a contract:

```markdown
# Adversarial Review NN — [artifact name]

## Summary
- Checkpoint: P[3a/3/5/6]-CK
- Artifact reviewed: [filename(s)]
- Date: YYYY-MM-DD
- Finding count by class: Class 3: N · Class 2: N · Class 1: N
- Highest-severity finding: [pointer]
- Disposition recommendation: [clearance / fork to phase re-open / fork to ADR revision / cleared with documentation fixes]

## Class 3 findings (severe — phase re-opening)

### F3-01 — [short name]
- **Location:** [exact pointer in artifact: file:section, file:line, file:quoted-phrase]
- **Defect:** [what's wrong, in the reviewer's words]
- **Discriminator that classifies as Class 3:** [(c) project-commitment violation / (b) requires upstream-phase artifact revision]
- **Evidence:** [quote or reference from the artifact making the defect concrete]
- **V3 failure mode engaged (if any):** [#1 / #2 / #4 / #5 / #7 / #8 / #9]
- **Voice FM engaged (if any):** [Cn FM-X]
- **Resolution path:** [phase re-opened / ADR revision required / etc. — per §4.1]

### F3-02 — ...

## Class 2 findings (moderate — current-phase ADR revision)

### F2-01 — [short name]
[same structure, discriminator field shows (a) only]

## Class 1 findings (minor — documentation drift)

### F1-01 — [short name]
- **Location:** ...
- **Defect:** ...
- **Resolution:** Inline fix in affected document.

## Findings considered and rejected (transparency)
[List of attack vectors applied that did not surface a finding. Format: attack name + brief note that the artifact handles it. This is the skill's debugging surface — operators can see what was *checked*, not just what *failed*. Critical for trust.]

## Disposition
[Final recommendation per §4.1. If any Class 3 findings exist, recommend phase re-opening per §4.1.3. If only Class 2 findings, recommend ADR revision per §4.1.2. If only Class 1 findings, recommend clearance with inline fixes per §4.1.1.]
```

The "Findings considered and rejected" section is non-optional. The skill's value is bounded by its transparency about what attacks were applied; an empty rejected-findings list is itself a finding (the skill didn't actually red-team).

---

## Workflow at runtime

Work in this order. Do not skip steps.

### 1. Identify the artifact type and checkpoint

From the operator's prompt and the artifact filename, identify which of the four checkpoint phases applies. If artifact-type and checkpoint-phase don't agree (e.g., an ADD presented at P3a-CK), surface the mismatch and ask before proceeding.

### 2. Read the artifact in full

Read the artifact via the project KB. Do not skim. Do not summarize before reviewing. Do not trust the artifact's self-description — verify against the artifact's actual content.

### 3. Read the relevant phase exit criteria

Open `Project_Workflow_v1_0.md` to the section for the phase that produced this artifact (§2.3.1 for ADRs, §2.3.5 for ADD, §2.5 for specification, §2.6 for implementation plan). The phase's "Exit criteria" row is the artifact's quality bar by design. The first-line check is: does the artifact actually meet its own phase's exit criteria as written?

Findings derived from exit-criteria failures classify as Class 2 by default (substantive content gap) or Class 3 if the failure also triggers discriminator (b) or (c).

### 4. Apply attacks in order

Apply each attack family in turn. For each attack family, work through its check questions against the artifact and emit findings as discovered. Attack families are encoded in the sections below:

- §"Severity classification" — the discriminator tree applied to *every* finding before emission.
- §"Artifact-type-conditional review discipline" — the type-specific check list (ADR / ADD / spec / impl-plan).
- §"V3-aligned attack vocabulary" — six V3 failure modes encoded as named attack patterns.
- §"Voice FM-list substrate" — voice-domain attacks read from `/mnt/skills/user/cN-*/SKILL.md` or `s4–s14` voice specs.

The order matters because earlier attacks tend to surface higher-severity defects (project-framing violations are caught by the V3 attack vocabulary; downstream voice-FM checks then surface domain-precision gaps).

### 5. Classify each finding via the discriminator tree

For every candidate finding, walk the §"Severity classification" tree before emitting. Findings that don't survive the tree (i.e., aren't actually defects) are dropped. Findings that survive get a class label.

### 6. Detect cross-artifact patterns (when reviewing multiple artifacts in one checkpoint)

P3a-CK reviews five ADRs (F1–F5); P3-CK reviews one ADD; P5-CK and P6-CK review one specification and one implementation plan respectively. When the checkpoint scopes more than one artifact, after compiling per-artifact findings, walk the aggregated finding list and check for *systemic patterns* — the same finding shape recurring across artifacts. Examples observed in iteration-1 P3a-CK validation:

- Workflow §2.3.1 exit-criteria failure (Cluster 5 V2 §3 standalone citation absent) appeared in all five F-ADRs.
- Untagged quantitative claims appeared in two F-ADRs (F1, F5).

When a finding shape recurs across ≥3 artifacts in a single checkpoint, surface it as a **systemic pattern** in the report's Disposition section with the recommendation that resolution scope is workflow §7 session-prompt-template revision rather than per-artifact fix. This is a higher-leverage resolution path than five identical inline fixes; it addresses the source defect rather than the symptoms.

When a finding shape recurs across exactly 2 artifacts, note it as a *candidate pattern* but do not yet recommend session-prompt-template revision — two occurrences may be coincidence, three is a pattern.

### 7. Compose the report

Write `Adversarial_Review_NN.md` per the §"What this skill produces" template. Include the "Findings considered and rejected" section — substantive checks only (target 8–12 entries per review), not exhaustive enumeration. The section's purpose is operator transparency on what *was actually attacked*, not a complete catalog of every check question. Include attacks that engaged the artifact's domain (the V3 FMs that fired or could plausibly have fired; the voice FMs whose domain the artifact touched); omit attacks that are obviously inapplicable (e.g., omit C2 cache-discipline checks on an action-surface ADR like F4).

### 8. Audit your own report before emitting

Before delivering, check:

- **Severity distribution sanity** — if all findings are Class 3, the skill is likely escalating. If all findings are Class 1, the skill is likely smoothing. Both are this skill's own failure modes.
- **Evidence on every finding** — every finding has a `Location:` pointer that resolves and an `Evidence:` quote or reference that makes the defect concrete. Findings without evidence are unverifiable assertions and must be dropped or strengthened.
- **Discriminator on every finding** — every finding names the specific discriminator (a/b/c) that classifies it. Findings without an explicit discriminator are unclassified and must be re-checked against the tree.
- **Author-mode drift check** — no finding's `Resolution path:` field supplies replacement text, corrected wording, or specific tag values. Resolution paths describe the *shape* of resolution, not the content. (See FM-C below.)
- **Context-bleed check** — no finding offers candidate expansions of undefined acronyms or terms; candidate definitions of contested phrasing; or "obvious" alternatives the substrate doesn't surface. (See FM-F below.)
- **Decision-vocabulary application** — every finding labeled *decided*, *proposing*, or *open* per §"Decision-claim vocabulary." *Proposing* findings that admit multiple readings spell out both readings briefly without the skill picking.
- **Rejected-findings completeness** — the rejected-findings section is populated and itemizes 8–12 substantive checks that *were* applied. Empty or one-line entries indicate the skill didn't actually red-team that vector. Exhaustive enumeration (every conceivable check) is also a failure mode — the section should be substantive checks, not a complete catalog.
- **Cross-artifact pattern surfacing** — if the checkpoint scopes multiple artifacts and a finding shape recurs in ≥3, the Disposition section names the systemic pattern with workflow §7 session-prompt-template revision recommendation.

---

## Severity classification

This skill encodes Project_Workflow_v1_0.md §4.1 as a deterministic discriminator tree. Apply in order; first match wins.

### Discriminator (c) — Project-commitment violation (V3 FM #8 in either direction)

The V3 system prompt §project_context enumerates what the project commits to and what it explicitly does not commit. Both directions are violations:

**Committed-claim violation** — artifact assumes or asserts something contrary to a project commitment:
- Multi-LLM-by-design: any artifact that assumes a single LLM is in scope is a Class 3 finding.
- Production-grade engineering discipline: any artifact that omits citation grounding, deterministic outer-harness commitments, observability primitives, or security boundaries because "it's just a design doc" is a Class 3 finding.
- Local development environment as design-time deployment target: any artifact that *excludes* cloud or hybrid deployment surfaces from downstream consideration is a Class 3 finding (V3 explicitly notes this is a deployment-stage characteristic, not a local-first principles commitment).

**Not-committed-overcommitment** — artifact picks a value for something V3 names not committed at this stage:
- Persona: any artifact that assumes "for the solo founder", "for an enterprise team", or any specific persona where V3 says persona is a design output is a Class 3 finding.
- Stack choice (orchestration substrate, durable-execution engine, observability backend, model providers, tool protocols, framework, language ecosystem): any artifact that commits a specific value (e.g., "Temporal", "n8n", "Postgres", "OpenTelemetry SDK X") at the F-ADR layer is a Class 3 finding *unless* the F-ADR's deliberation surface explicitly includes engine selection (compare ADR-F3 which defers engine to D-ADR vs an F-ADR that picked Temporal).
- Deployment surface: any artifact that commits to one of cloud-managed / hybrid / local-only at the F-ADR layer is a Class 3 finding.
- Architectural decisions across the five harness axes: ADRs are *the* place these get decided; any artifact that pre-commits a five-axis decision *outside* the ADR-authoring path is a Class 3 finding.

If discriminator (c) fires → **Class 3 (severe — phase re-opening)**.

### Discriminator (b) — Requires upstream-phase artifact revision

Does resolving the finding require revising an artifact filed in a phase prior to the current phase? Examples:

- A spec-level finding (P5-CK) that requires changing an ADR (Phase 3a or 3b artifact) → Class 3.
- An impl-plan finding (P6-CK) that requires changing the specification (Phase 5 artifact) → Class 3.
- An ADD finding (P3-CK) that requires changing an underlying ADR → Class 3.
- An ADR-level finding (P3a-CK) that requires changing the persona document (Phase 2 artifact) → Class 3.

If discriminator (b) fires → **Class 3 (severe — phase re-opening)**.

### Discriminator (a) — Affects substantive content of current-phase artifact

Does the finding affect the artifact's substantive content in a way that requires revising the artifact (not just fixing a typo or cross-reference)? Examples:

- A decision criterion that was implicit in the rationale but not stated explicitly.
- An alternative that was considered in council deliberation but not enumerated in the alternatives section.
- A dependency declaration that exists in spirit but not in the artifact's "References" section.
- A confidence tag that was omitted on a substantive claim.
- A failure mode the rationale implies but does not surface explicitly.

If discriminator (a) fires (and (b) and (c) did not) → **Class 2 (moderate — current-phase ADR revision)**.

### Discriminator (a/b/c) all miss — drift only

Typos, format inconsistencies, missing cross-references that don't change semantics, unclear prose. → **Class 1 (minor — documentation drift)**.

### Alternatives considered and rejected

The skill considered the following alternative shapes for severity classification and rejected them:

- **Scoring / additive severity** (multiple discriminators each adding severity points) — rejected because §4.1's three classes are qualitative thresholds, not a continuous scale; scoring would impose a quantitative anchor §8.1 of the workflow explicitly defers.
- **Phase-impact-only discriminator** (just check whether resolution requires upstream revision) — rejected because it misses V3 FM #8 framing contamination, which is the project's highest-value attack vector and may produce findings whose resolution is self-contained to the current artifact yet is foundationally severe.
- **Voice-FM-list-as-severity-mapping** (each voice FM maps to a severity class) — rejected because voice FM-lists are structured by voice-domain correctness, not by project-impact. A C2 boundary-leakage FM is a domain-precision issue; whether it is Class 2 or Class 3 depends on whether resolving it requires upstream revision, not on which voice it engages.

---

## Artifact-type-conditional review discipline

Common substrate (severity classification, V3 attack vocabulary, voice FM-list substrate, citation-specificity check, evidence requirement, finding-format) applies to all four artifact types. Each subsection below adds *type-specific* axes scoped to that artifact's failure surface.

### ADR review (P3a-CK, also P3b derivative ADRs if extended)

Type-specific axes (light extension over shared substrate):

- **Decision premises** — does the Context section establish each premise the Decision rests on? Findings: implicit premise; premise asserted without source; premise contradicting the persona document.
- **Alternatives completeness** — are there genuinely-considered alternatives the council weighed but did not enumerate? Cross-check against substrate (Pattern Reference Catalog §11.3.1, Cluster N V2 deliverables) for candidate enumerations the council had access to. Findings: alternative present in substrate but absent from "Alternatives considered"; alternative enumerated but rejected without rationale.
- **Dependency declarations** — does the ADR cite Persona_Document_v1, Pattern Reference Catalog v1.0, Cluster deliverables, prior ADRs, V3 system prompt §project_context, and the workflow document where they apply? Findings: implicit dependency; dependency claimed without specific section citation; downstream dependency declared but not present in "Constrained downstream" subsection.
- **Permanent tension acknowledgment** — does the ADR engage the three permanent tensions (T-perm-1 C4↔C10, T-perm-2 C2↔C3, T-perm-3 C1↔C9) where they apply? Findings: tension touched but not named; tension named but resolution shape not specified; tension resolution at this layer not distinguished from downstream resolution.
- **Phase exit criteria** — per Project_Workflow_v1_0.md §2.3.1: "each ADR has explicit dependency declarations to Cluster 5 V2 §3 substrate and Pattern Reference Catalog source citations." Findings derived from exit-criteria failure default to Class 2.

### ADD review (P3-CK)

Type-specific axes:

- **ADR coverage gap** — every ADR is referenced by at least one ADD section, every ADD section traces to at least one ADR (workflow §2.3.5 exit criteria). Findings: orphan ADD section; un-cited ADR.
- **Cross-axis emergent properties** — does the ADD address properties that emerge from multiple ADRs interacting (per workflow §4.2.4)? Example: replay-determinism semantics across the durable boundary engaging C1+C3+C7+C11 simultaneously. Findings: emergent property surfaced in a single ADR but not consolidated at ADD level; cross-axis property without an ADR addressing it.
- **Permanent tension consistency** — does the ADD's resolution of T-perm-1, T-perm-2, T-perm-3 read consistently across all ADRs that engage them? Findings: ADR-A resolves T-perm-N at one shape; ADR-B resolves T-perm-N at incompatible shape.
- **Persona document trace** — does every persona-dependent decision in the ADD trace explicitly to Persona_Document_v1? Findings: persona-dependent decision in ADD without persona citation.
- **Phase 3c integration verification trace** — does the ADD reflect the integration verification report's findings? Findings: integration-surfaced ADR not present; consistency-matrix entry not honored.

### Specification review (P5-CK)

Type-specific axes:

- **Contract precision** — every interface signature has typed inputs, typed outputs, error contract, idempotency posture, and observability obligations. Findings: signature without type; error contract absent; idempotency posture unstated.
- **Schema completeness** — every data schema has field-level types, required/optional discipline, validation rules, and version-evolution discipline. Findings: optional/required ambiguous; validation rules in prose not in schema.
- **Failure-mode taxonomy completeness** — for every operation that can fail, the spec enumerates fail classes (`permanent` / `transient` / `Reflexion-recoverable` / `HITL-recoverable`) with `cause_attribution` per C5 contract. Findings: operation can fail but spec lists only success path; fail class without cause_attribution.
- **Observable lifecycle** — every long-running operation has lifecycle events per ADR-F3 capability-requirement floor (workflow-start, step-boundary, fallback-trigger, retry-attempt, breaker-trip, lease-acquired/released, resumption). Findings: lifecycle event absent; event present but span schema not specified.
- **Contract-vs-ADR honoring** — every ADR commitment is honored by at least one spec element (workflow §2.5 exit criteria). Findings: ADR commitment without spec element; spec element contradicting ADR.

### Implementation plan review (P6-CK)

Type-specific axes:

- **Topological sort acyclicity** — the unit dependency graph is acyclic (workflow §2.6 exit criteria). Findings: cycle in dependency graph; dependency declared but predecessor unit missing.
- **Hidden coupling** — units declare their dependencies explicitly. Findings: unit B implicitly assumes unit A's data shape but doesn't declare A as predecessor; shared mutable substrate not surfaced as a synchronization unit.
- **Acceptance criteria precision** — every unit has acceptance criteria that are observable from outside the unit (test invocations, behavioral checks). Findings: acceptance criterion in implementer-discretion language ("works correctly"); criterion that requires reading the implementation to verify.
- **Test coverage** — every spec element is exercised by at least one unit's tests. Findings: spec element without covering test; test that exercises a spec element only partially (e.g., happy-path only).
- **Spec coverage** — every spec element is covered by at least one unit (workflow §2.6 exit criteria). Findings: spec element with no unit; unit without spec trace.

---

## V3-aligned attack vocabulary

Six of V3's nine failure modes are reviewable in completed artifacts (the other three — silent truncation, mode misread, and to a lesser extent missing uncertainty signals — are runtime behaviors of Claude during authoring, not properties of finished documents; #5 is included because it is checkable in artifacts as well as in runtime). Each mode below is encoded as a named attack the skill applies during review.

### Attack V1 — Silent grounding collapse (V3 FM #1)

Does the artifact cite primary sources, or paraphrase from training-data without source? For every substantive claim, the artifact's source must resolve to a retrievable session-accessed source. Citations to "engineering posts" or "the X working group" without a specific URL or document identifier are weak-source-by-V3-standards.

Severity discriminator: usually Class 2 (citation refinement is a current-phase fix). Class 3 if the claim is foundational *and* the actual primary source contradicts the claim's content.

### Attack V2 — Silent scope narrowing (V3 FM #2)

Does the artifact cover the full deliberation surface its phase scopes? For ADRs, the deliberation surface is the F-decision per Pattern Reference Catalog §11.3.1 (foundational) or §11.3.2 (derivative). Did the ADR silently narrow that surface?

Worked example: ADR-F1's deliberation surface per Pattern Reference Catalog §11.3.1 includes the routing strategy across all three layers (declarative / embedding / LLM-as-router). An F1 ADR that addressed only the declarative layer would be a silent scope narrowing.

Severity discriminator: Class 3 if the missing scope element changes a foundational commitment; Class 2 if the missing scope element is a refinement that doesn't change the foundational commitment.

### Attack V4 — Fabricated citations (V3 FM #4)

Do citations resolve to retrievable sources? Spot-check by reading citations: does the cited paper exist at the cited URL? Does the cited Cluster section exist at the cited section number? Does the cited Pattern Reference Catalog entry exist at the cited section?

Severity discriminator: Class 3 (citation fabrication is a foundational-trust violation; resolution requires re-authoring with correct sources, which engages discriminator (b) if the citation supports a foundational claim).

### Attack V5 — Missing uncertainty signals (V3 FM #5)

Does the artifact tag substantive claims with confidence labels ([HIGH] / [MODERATE] / [SPECULATIVE])? Are confidence tags applied honestly — i.e., are there *any* [SPECULATIVE] tags? V3 explicitly notes that responses with no [SPECULATIVE] tags anywhere are suspicious.

Severity discriminator: usually Class 2 (tag-level fix). Class 3 if a load-bearing claim is tagged [HIGH] but the source actually warrants [MODERATE] or [SPECULATIVE], because the over-confidence may have driven a foundational decision.

### Attack V7 — Weak-source escalation (V3 FM #7)

For [HIGH] confidence claims, does the source actually warrant [HIGH]? V3's bar is primary sources accessed in this session. SEO listicles, marketing pages, blog summaries of papers, and "general knowledge" framings are weak.

Severity discriminator: usually Class 2 (downgrade to [MODERATE] or [SPECULATIVE]; source-quality limit noted). Class 3 if the [HIGH] claim is foundational and the actual source is significantly weaker.

### Attack V8 — Framing contamination (V3 FM #8) — HIGHEST-VALUE ATTACK VECTOR

Does the artifact embed persona, stack, or deployment assumptions that V3 explicitly does not commit? Apply via discriminator (c) of the severity tree — both directions:

- Committed-claim violation (artifact contradicts something committed).
- Not-committed-overcommitment (artifact picks a value for something not committed).

Severity discriminator: Class 3 always (the discriminator tree's (c) branch).

### Attack V9 — Cross-project context bleed (V3 FM #9)

Does the artifact retrieve content from outside this project's working scope? Citations to past conversations from other projects, claims that don't trace to this project's KB, "general framework knowledge" without a session-accessed source — all surface here.

Severity discriminator: Class 2 if the claim can be re-grounded against a session-accessed source. Class 3 if the claim is foundational and no session-accessed source supports it.

---

## Voice FM-list substrate

The eleven council voice skills (`/mnt/skills/user/c1-orchestration-control/SKILL.md` through `c11-operator-local/SKILL.md`) each maintain a `## Failure modes to actively prevent` section listing lettered failure modes (FM-A, FM-B, ...) that voice avoids in its own contributions. Each FM has a name, a description of what goes wrong, and a mitigation. Many are about boundary leakage between voices; others are about content-domain discipline (e.g., C10 FM-H "cross-family trust shift forgotten"; C2 FM-G "1M-context absorption"; C5 FM-H "permanent-vs-transient conflation").

**These FM-lists are substrate for adversarial attack vocabulary, not active participants.** The skill does not convene voices. It reads voice FM-lists as catalogs of attacks the artifact under review may have failed.

### How to use voice FM-lists at runtime

1. **Identify the voices that own the artifact's domain.** F-ADRs map cleanly to a small voice set:
   - F1 (multi-LLM provider abstraction) → C6 (model routing) primary; C9 (retry/fallback), C10 (trust gradient), C7 (spans) secondary.
   - F2 (filesystem-as-substrate) → C3 (state/persistence) primary; C2 (within-turn), C7 (spans) secondary.
   - F3 (durable-execution coordination spine) → C9 (reliability/recovery), C1 (orchestration) primary; C3 (state), C7 (spans), C11 (operator/local) secondary.
   - F4 (sandbox-isolation-by-trust-level) → C10 (action safety) primary; C4 (tools), C11 (operator) secondary.
   - F5 (secrets abstraction) → C10 (action safety) primary; C4 (tools), C5 (validation) secondary.
   - The ADD engages all eleven voices at the integration layer; the spec engages all eleven at contract precision; the impl plan engages all eleven at unit-decomposition precision.

2. **Read the relevant voice's SKILL.md.** Specifically, the `## Failure modes to actively prevent` section. Each FM is a candidate attack: if the voice avoids it during authoring, the reviewer's job is to check whether the artifact authored *without* that voice's skill applied has fallen into it.

3. **Apply each FM as a check question against the artifact.** For example, C10 FM-H ("cross-family trust shift forgotten") translates to: "Does this ADR/spec/plan recognize that cross-family fallback steps shift the trust boundary, or does it treat them as equivalent to Anthropic-only steps?" If the artifact silently treats them as equivalent, that is a finding.

4. **Voice FM findings classify per the discriminator tree.** A voice-domain-precision finding usually classifies as Class 2 (substantive content gap); it escalates to Class 3 only if it triggers discriminator (b) or (c).

### Voice FM-list mechanical-application failure mode

Do not treat every voice FM as automatically a finding. Many FMs are about voice-internal authoring discipline (e.g., C2 FM-A "boundary leakage to C3" — the *voice* must not specify durable state); the artifact under review is not a voice's contribution and may legitimately blend boundaries by design. Apply judgment: does the FM's *outcome* (e.g., the artifact misclassifies durable-state semantics) appear in the artifact, or does the FM's *mechanism* (the voice author crossed a boundary)? Only the former is a finding for this skill. Mechanical FM-application is one of this skill's own failure modes (see §"Failure modes the eval should catch").

---

## Decision-claim vocabulary

When emitting findings, distinguish:

- *decided* — the skill has classified a finding with a discriminator and a severity class, and the artifact's text supports a single reading of the defect. Use definite language: "This is a Class 3 finding because discriminator (c) fires: the ADR commits to X where V3 explicitly does not commit X."
- *proposing* — the skill has identified a candidate finding that admits more than one reading from the artifact's text alone, or where the discriminator's application depends on a fact the skill cannot verify from the project KB (a citation that may or may not resolve; a phrasing that may be an overcommitment or careful scoping; a taxonomy that may be cause-attribution-refinement or class-redesign). Use proposing language: "Proposing as Class 2 finding pending verification of citation X. If the citation does not resolve, escalate to Class 3 per Attack V4." When the ambiguity is reading-dependent (Reading 1 vs Reading 2), spell out both readings briefly; let the operator pick the reading rather than the skill choosing one.
- *open* — the skill has surfaced an ambiguity it cannot resolve without operator input (e.g., the artifact's intent on a borderline framing claim is not clear from the text alone). Use open language: "Open question: does ADR-F3's phrase 'engine-deferral shape' commit to per-workload-class deferral, or is it neutral on per-workload-vs-harness-wide engine selection? Operator decision required to classify."

**Discipline:** every finding receives exactly one of these labels. *Decided* is the default; downgrade to *proposing* when the text supports two readings or when classification depends on out-of-KB verification; downgrade to *open* when the operator's intent is required to classify at all. Iteration-1 calibration: F5 F2-02 (taxonomy phrasing) is the canonical *proposing* shape — Reading 1 (cause-attribution-refinement) and Reading 2 (class-redesign) are both supported by the text; the skill cannot determine the intended reading and should not pick.

Findings emitted as *proposing* or *open* in the report must also note in the rejected-findings section how the operator's response would convert them to *decided*.

---

## Failure modes the eval should catch

These are the failure modes the skill avoids in its own behavior. They are checked by the eval set during validation (see test-prompts file). All are tagged for severity-prone-direction and surface in §7 self-audit.

- **FM-A: Severity inflation.** Calling Class-1 things Class-3 to feel important, or escalating a finding past where the discriminator tree warrants. Mitigation: §7 audit on severity distribution; every finding names its discriminator explicitly; if all findings come back Class 3, re-walk the tree.
- **FM-B: Severity deflation.** Calling Class-3 things Class-1 (or Class-2) to look kind, or because the discriminator was lazy. Mitigation: §7 audit on severity distribution; specifically check whether discriminator (c) was applied — V3 FM #8 framing contamination is the most-easily-deflated severity-3 case.
- **FM-C: Author-mode drift.** Proposing solutions instead of flagging defects. The skill is read-only with respect to the artifact. The discipline distinction: a finding's `Resolution path:` field describes the *shape* of resolution (add a citation; tag a claim with confidence; reword to disambiguate Reading 1 from Reading 2; restructure to eliminate count drift) — it does *not* supply the replacement text, the corrected wording, the specific tag value, or the new structure. Author-mode drift surfaces when resolution paths read as "Reword as 'X'" with X being a candidate replacement text. Mitigation: §"Audit your own report" checks for `Resolution path:` field content matching pattern "Reword [the section] as [verbatim quoted text]" — rephrase to "Reword [the section] to disambiguate / clarify / eliminate / make explicit [the defect shape]" and let the council author the replacement. Iteration-1 example caught: F5 F2-02 originally proposed verbatim replacement text for the secret-fail-class taxonomy; the discipline is to flag the ambiguity (Reading 1 vs Reading 2) and let the council pick the wording.
- **FM-D: Voice-FM-list mechanical application.** Treating every voice FM as automatically a finding without checking whether the FM's *outcome* (not mechanism) appears in the artifact. Mitigation: §"Voice FM-list mechanical-application failure mode" prose above; every voice-FM-derived finding must cite the artifact's content, not the voice's discipline.
- **FM-E: V3-FM-list mechanical application.** Treating every V3 attack as automatically a finding regardless of whether the artifact handles it. The skill applies six attacks; if the artifact handles all six well, that is a finding-free outcome (not a "skill missed something" outcome). Mitigation: rejected-findings section must include attack vectors applied that did not surface defects.
- **FM-F: Cross-project context bleed (in the review itself).** The skill makes claims about content not in the project KB — e.g., asserts that an alternative was "obviously" considered when the substrate doesn't show it; offers a candidate expansion of an undefined acronym ("AAIF" might mean "Anthropic AI Foundation"); cites "best practice" without a session-accessed source. Mitigation: the skill is bound by the same V3 discipline it enforces. Every finding must cite the artifact, the workflow document, the Persona Document, the Pattern Reference Catalog, a Cluster deliverable, or a voice SKILL.md. Findings without such citations are rejected. **Specifically on undefined acronyms or terms in the artifact:** flag the defect (acronym appears unexplained on first use) but do *not* offer a candidate expansion; that is operator-resolution territory. Iteration-1 example caught: F4 F1-01 offered "Anthropic AI Foundation" as plausible AAIF expansion; the discipline is to flag the acronym and stop, letting the council confirm the expansion.
- **FM-G: Smoothing.** Failing to surface a finding because it's "probably fine" or "the council probably considered it." The skill's value is bounded by surfacing what slipped past the council. If the rationale section does not explicitly handle a candidate attack, the finding is real even if the council "probably" thought about it. Mitigation: §"Findings considered and rejected" forces the skill to enumerate what was checked; an implicit check is unverifiable.
- **FM-H: Reviewing the council instead of the artifact.** Critiquing the deliberation process (e.g., "the council under-weighted voice X") rather than the artifact's content. The deliberation is settled; the artifact is the review surface. Mitigation: every finding has a `Location:` pointer in the artifact; no finding refers to "the council" in a way that doesn't ground in the artifact.
- **FM-I: Finding-density-without-prioritization.** Listing 30 minor findings flat, without ranking by severity or impact. Mitigation: the report's class breakdown forces prioritization; the disposition recommendation forces a clearance-or-fork judgment based on the highest-severity finding present.
- **FM-J: Empty rejected-findings section.** The skill emits findings without enumerating what was checked. Mitigation: §7 audit fails the report if the rejected-findings section is empty; the skill cannot ship without populating it.
- **FM-K: Disposition-without-evidence.** The summary's disposition recommendation does not match the finding inventory — e.g., recommending clearance with three Class-3 findings present, or recommending phase re-opening with only Class-1 findings. Mitigation: §7 audit checks disposition against §4.1 (any Class 3 → fork to phase re-open; only Class 2 → fork to ADR revision; only Class 1 → clearance with inline fixes).

---

## Reference files

- `Project_Workflow_v1_0.md` — workflow document. §0 visual summary, §2 phase definitions and exit criteria, §4.1 severity classification framework, §4.2 cross-axis integration framework, §6.2 this skill's spec.
- `Persona_Document_v1.md` — persona document; the trace target for any persona-dependent claim in any artifact.
- V3 system prompt (project_context section) — the trace target for project commitment violations; the source of truth for what is committed and what is not committed at project level.
- `/mnt/skills/user/cN-*/SKILL.md` (eleven voice SKILL.md files) — voice FM-list substrate; read at review time, not loaded into this skill's own SKILL.md.
- Pattern Reference Catalog v1.0 — referenced by F-ADRs and D-ADRs; the trace target for "alternatives considered" completeness checks.
- Cluster N V2 deliverables — referenced by ADRs as substrate; the trace target for "alternative present in substrate but absent from ADR" findings.

---

## Test prompts for evaluation

The validation test set is in `evals/test-prompts.md` (separate file). Test prompts cover:

- Each of the five F-ADRs (real fixtures; the validation discipline per workflow §6.2 is "does the skill find Class-2 and Class-3 findings the council missed?").
- Synthetic Class-1, Class-2, and Class-3 fixtures (defects deliberately injected into copies of the F-ADRs to verify discriminator tree behavior).
- Synthetic V3 FM #8 framing contamination fixtures (the highest-value attack vector).
- A non-ADR artifact (out-of-scope test — does the skill correctly decline to review).

See `evals/test-prompts.md` for the full enumeration with expected behavior per prompt.

---

*End of SKILL.md draft v0. Iteration target for session 2: validation against F1–F5 fixtures.*
