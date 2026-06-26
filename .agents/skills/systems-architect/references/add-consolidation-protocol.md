# ADD Consolidation Protocol — Phase 3d

The structured procedure the systems architect skill applies in Phase 3d. The protocol consolidates a complete set of filed ADRs into a single coherent Architectural Design Document with traceability preserved, without reopening filed decisions.

---

## 1. Operating principles

1. **Consolidate, do not re-deliberate.** Phase 3d reorganizes filed decisions into the canonical pre-PRD artifact. It does not revisit which decisions were correct.
2. **Cite, do not duplicate.** ADRs remain the load-bearing decision artifacts. The ADD synthesizes; it does not paraphrase ADR Rationale or Alternatives Considered into ADD prose.
3. **Preserve traceability bidirectionally.** Every ADR is referenced by at least one ADD section; every ADD section traces to at least one ADR. The traceability matrix is part of the ADD, not a separate artifact.
4. **Surface contradictions; do not patch them.** A contradiction discovered during consolidation is a Phase 3c regression — it is escalated, not edited away inside the ADD.
5. **Stay agnostic on what was not decided.** Decisions deferred to Phase 4+ are listed in the ADD's open-items section; they are not filled in by the consolidation skill.

---

## 2. Inputs and entry verification

### 2.1 Required inputs

Before consolidation begins, verify that all of the following are present and complete:

- **All filed F-ADRs** — the foundational decisions enumerated in Cluster 5 V2 §3 or its successor (the count is project-specific; the workflow phase 3a inventory establishes it).
- **All filed D-ADRs** — every derivative decision required by Phase 3b's session plan.
- **All filed I-ADRs** — every independent decision filed during 3a/3b/3c (zero is acceptable; the I-ADR set may be empty if all I-decisions are deferred to implementation).
- **Phase 3c integration verification report** — `Integration_Verification_Report.md` with cleared status (zero unresolved contradictions).
- **Persona document** — `Persona_Document_v1.md` (read-only; cited but not consumed for new decisions).

### 2.2 Stand-down conditions

If any of the following holds, the consolidation session stands down and surfaces the gap:

- Any F-ADR is missing or in Proposed (not Accepted) status.
- Any D-ADR referenced by an Accepted F-ADR's Consequences section is missing.
- Phase 3c integration verification report is missing or shows unresolved contradictions.
- Persona document is missing.
- The integration verification report flags a regression that has not been resolved.

A stand-down is not a failure; it is the protocol functioning. The consolidation session resumes after the gap is closed.

---

## 3. Procedure

### 3.1 Step 1 — ADR inventory

Build a complete inventory of input ADRs. For each ADR, capture:

| Field | Source |
|---|---|
| ADR ID | Filename |
| Title | ADR §header |
| Class | F / D / I |
| Status | ADR §Status |
| Primary axis | Skill judgment cross-checked against ADR Decision and Consequences |
| Secondary axes | Skill judgment |
| Dependency ADRs | ADR §References |
| Engaged tensions | ADR §Consequences (where it names T-perm-1/2/3) |

The inventory is captured as a table; it is the foundation for both section structure and the traceability matrix.

### 3.2 Step 2 — Section structure

Build the ADD's section structure as follows.

```
§1 Persona summary
   (1 paragraph — references Persona_Document_v1)

§2 Foundational decisions
   §2.1 ADR-F1 — {title}
   §2.2 ADR-F2 — {title}
   ...
   (one subsection per F-ADR, ordered by F-number)

§3 Derivative decisions
   §3.1 Control plane
       §3.1.1 ADR-D{n} — {title}
       ...
   §3.2 Information substrate
       ...
   §3.3 Action surface
       ...
   §3.4 Operational discipline
       ...
   §3.5 Deployment surface
       ...
   (D-ADRs grouped by primary axis; subsection only created if the axis
   has at least one D-ADR)

§4 Independent decisions
   {same axis grouping as §3; omitted entirely if I-ADR set is empty}

§5 Cross-axis integration
   §5.1 Resolved tensions
   §5.2 Permanent tensions accepted
   §5.3 Cross-cutting properties
   (sources: integration verification report)

§6 Open items and deferrals
   §6.1 Decisions deferred to Phase 4 (PRD)
   §6.2 Decisions deferred to implementation
   §6.3 Decisions whose triggers are not yet present

Appendix A — Traceability matrix
Appendix B — ADR inventory table (from §3.1 Step 1)
```

**Section ordering rules:**

| Rule | Rationale |
|---|---|
| §2 ordered by F-number | F-numbers reflect Phase 3a session order, which reflects the dependency DAG. Preserves the ordering Phase 3a established. |
| §3 grouped by primary axis | D-ADRs are most usefully read together by axis (the reader entering the ADD is typically operating in one axis at a time). |
| §3 axis order: control plane → information substrate → action surface → operational discipline → deployment surface | Five-axis canonical order from `references/five-axis-checklist.md`. |
| §5 last among substantive sections | Cross-axis integration is the synthesis layer; it presupposes §§2–4 have been read. |
| Open items after substantive sections | Open items are forward-looking; they belong after the decided content. |

### 3.3 Step 3 — Section drafting

For each section of the ADD, draft prose that synthesizes the underlying ADR(s).

**Section template — F-decision subsection:**

```markdown
### §2.{n} ADR-F{n} — {title}

**Decision summary.** {One-sentence restatement of the ADR's Decision
line. Cite ADR-F{n} parenthetically.}

**Persona linkage.** {How the persona forced or constrained this decision.
If persona-open, state that and explain what shaped the decision instead.
Cite Persona_Document_v1 §{section}.}

**Substrate linkage.** {Substrate evidence that informed the decision.
Cite specific deliverable + section.}

**Downstream consequences.** {What this F-decision constrains downstream.
Cite the D-ADRs or I-ADRs that depend on it. If no downstream ADRs depend
on it (rare for an F-decision; would suggest misclassification),
explicitly note that.}

**Engaged tensions.** {If the ADR engages a permanent tension, state
which one and how the resolution shape works. Cite the integration
verification report.}
```

**Section template — D-decision subsection:**

```markdown
#### §3.{x}.{n} ADR-D{n} — {title}

**Constrained by.** {The F-ADRs (and any prior D-ADRs) that constrain
this decision's option space. Cite by ADR ID.}

**Decision summary.** {One-sentence restatement of the ADR's Decision
line. Cite ADR-D{n} parenthetically.}

**Rationale highlights.** {Two- or three-sentence summary of the load-
bearing rationale. Do NOT duplicate the ADR's full Rationale; this is
synthesis. Cite ADR-D{n} for the full Rationale.}

**Operational implications.** {What this decision implies for downstream
operational discipline — gates, validators, observability. Cite ADRs
that capture those implications, or note them as Phase-4-or-later.}
```

**Section template — Cross-axis integration (§5.1 resolved tensions):**

```markdown
### §5.1 Resolved tensions

The integration verification (Integration_Verification_Report.md §{section})
identified the following cross-axis tensions, each resolved by an ADR
or ADR pair.

#### §5.1.{n} {Tension name}
- Engaged ADRs: {ADR-IDs}
- Tension form: {one sentence describing the conflict}
- Resolution: {one paragraph describing how the cited ADRs resolve the
  tension}
- Verification: {citation to the integration report's section}
```

### 3.4 Step 4 — Traceability matrix

Build the traceability matrix as Appendix A. Format:

| ADR ID | §1 | §2.1 | §2.2 | ... | §3.1.1 | ... | §5.1 | §5.2 | ... |
|---|---|---|---|---|---|---|---|---|---|
| ADR-F1 |  | ✓ |  |  | ✓ |  | ✓ |  |  |
| ADR-F2 |  |  | ✓ |  |  |  | ✓ |  |  |
| ... |  |  |  |  |  |  |  |  |  |

A `✓` indicates the ADR is cited (by ID) in that ADD section.

**Verification rules:**

- Every row has at least one `✓`. (Every ADR is referenced.)
- Every column has at least one `✓`, except §1 (persona summary) which references the persona document, not ADRs.
- Failure to satisfy either rule indicates either a missing citation or an extraneous section. Resolve before ADD is filed.

### 3.5 Step 5 — Coherence pass

Read the ADD end-to-end. Verify:

1. **No contradictions with cited ADRs.** Every ADD claim about an ADR's content matches the ADR's actual content.
2. **No contradictions with the integration verification report.** Tensions described in §5 match the report.
3. **No contradictions internal to the ADD.** §2 claims are consistent with §3 claims.
4. **No new decisions.** No section asserts a position not already filed in an ADR.
5. **Citation specificity.** Every ADR citation is by ID; every substrate citation is by deliverable + section; every persona citation is by document + section. (V3 citation rules apply.)
6. **Confidence-tag posture.** ADD prose is restatement of filed decisions; substantive factual claims that go beyond restatement (e.g., synthesis claims about cross-cutting properties) carry V3 confidence tags. Pure ADR-restatement claims do not require tags because their authority is the cited ADR.

If any verification fails, do not patch the ADD. Surface the failure. The patch path is per §4.

---

## 4. Escalation rules

### 4.1 If a contradiction surfaces between two ADRs during consolidation

This is a Phase 3c regression. The integration verification was supposed to catch it. Surface it explicitly:

> **Phase 3c regression detected.** ADR-{X} and ADR-{Y} contain conflicting positions on {topic}. The Phase 3c integration report (§{section}) does not address this conflict. Per workflow §4.2.1 (or §4.2.2 if cross-axis), back-flow to the appropriate Phase 3a/3b session is required before consolidation can proceed.

Do not attempt to resolve the contradiction inside the ADD. The ADD is a consolidation artifact, not a decision artifact.

### 4.2 If a contradiction surfaces between an ADR and the persona document

The persona document is read-only context for Phase 3d but a normative input for Phase 3a/3b. A contradiction here implies that one of the Phase 3a/3b sessions made a decision that diverges from the persona without amending the persona. Surface explicitly:

> **Persona-decision divergence detected.** ADR-{X} adopts {position} which diverges from Persona_Document_v1 §{section} ({persona statement}). Per workflow §4.3, back-flow is required: either ADR-{X} is revised to align with the persona, or the persona document is revised with explicit acknowledgment that the persona has shifted.

### 4.3 If an ADR is missing that another ADR depends on

Phase 3c was supposed to catch this. Surface explicitly per workflow §4.2.3 and stand down pending the missing ADR's authoring.

### 4.4 If the operator pulls toward reopening a decision

Redirect:

> Phase 3d does not reopen decisions. {Decision in question} is filed as {ADR-X} with {status}. If new evidence has surfaced that warrants revisiting, the path is: file the new evidence, propose a successor ADR, route through Phase 3a/3b/3c. The ADD will be reconsolidated after the successor ADR is Accepted.

---

## 5. Output

### 5.1 Deliverable

`Architectural_Design_Document_v1.md` containing:

- §§1–6 as per §3.2 above
- Appendix A — traceability matrix
- Appendix B — ADR inventory table

### 5.2 Quality bar

The ADD must satisfy:

| Property | Verification |
|---|---|
| **Traceability** | Every ADR referenced; every section traces |
| **No new decisions** | Coherence pass §3.5 item 4 |
| **No reopened decisions** | Coherence pass §3.5 item 1 + §3.5 item 2 |
| **Citation specificity** | Coherence pass §3.5 item 5 |
| **Five-axis structure preserved** | Section ordering rules §3.2 |
| **F → D → I tier preserved** | Section ordering rules §3.2 |
| **Tensions surfaced** | §5.1 / §5.2 populated where engaged ADRs cite tensions |

### 5.3 Out of scope

The ADD does not contain:

- Implementation guidance (Phase 6+)
- PRD-style observable-behavior descriptions (Phase 4)
- Substrate research findings beyond what is cited from prior deliverables
- New ADRs (Phase 3a/3b)
- Operator-experience or product-experience descriptions (Phase 4)

---

## 6. Anti-patterns specific to ADD consolidation

| Anti-pattern | Symptom | Correction |
|---|---|---|
| **Decision restatement** | ADD subsection paraphrases the ADR's Rationale verbatim | Synthesize; cite ADR for the full Rationale |
| **New decisions** | ADD §3 subsection includes a position not in any filed ADR | Surface as Phase 3a/3b regression; do not include |
| **Patched contradictions** | ADD smooths over a conflict between two ADRs | Surface as Phase 3c regression; do not smooth |
| **Persona drift** | ADD §1 persona summary contradicts the persona document | Use the persona document verbatim or by close paraphrase with citation |
| **Section overcollapse** | All D-decisions placed in one undifferentiated §3 | Group by primary axis per §3.2 |
| **Section overexpansion** | Subsection per ADR for ADRs that share an axis and tightly couple | Group tightly coupled D-ADRs in one subsection with multiple ADR cites |
| **Traceability skip** | Some ADRs not referenced anywhere in the ADD | Either cite the ADR or remove it from the inventory (it is a missing-Phase-3c-finding) |
| **Tension elision** | §5 omitted because "the integration report didn't flag any" | The integration report acknowledges all three permanent tensions explicitly per workflow §2.3.4 exit criteria; §5.2 must reference them |
