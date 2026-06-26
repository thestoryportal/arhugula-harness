# Adversarial Review 5 — Spec_Action_Surface_v1, §1 C-AS-01 (four-tier sandbox contract)

## Summary
- Checkpoint: P5-CK (specification adversarial review — scoped pass: §1 C-AS-01 only, per operator request)
- Artifact reviewed: `design-substrate/Spec_Action_Surface_v1.md` §1 C-AS-01 (lines 125–166); upstream traces ADR-F4 `ADR-F4.md`, ADR-D2 `ADR-D2.md`, ADD v1.3 §2.4
- Date: 2026-05-15
- Finding count by class: Class 3: 1 · Class 2: 4 · Class 1: 3
- Highest-severity finding: F3-01 — tier-label semantics contradict the mechanism-class column and the F4 microVM/full-VM distinction
- Disposition recommendation: Fork to upstream-phase artifact revision. One Class-3 finding present (discriminator (b) — resolution requires either an ADR-F4 v1.1 revision or a determination that the label drift is spec-local). Per §4.1.3 the highest-severity finding governs disposition. See §Disposition for the precise fork shape and the Reading-1/Reading-2 split that determines whether the Class-3 escalation holds.

**Scope note.** The operator scoped this review to C-AS-01 §1 only ("the four-tier sandbox contract"). This is a partial-artifact pass, not a full P5-CK specification review. Findings about §2–§16 are out of scope and not enumerated; however, where a §1 defect propagates into a §2+ contract (notably C-AS-02 composition and C-AS-04 fail-class), that propagation is noted as evidence of blast radius, not reviewed as a separate finding. A full P5-CK clearance still requires review of the remaining contracts.

---

## Class 3 findings (severe — phase re-opening)

### F3-01 — Tier-3/Tier-4 labels and mechanism classes contradict the F4 microVM-vs-full-VM distinction
- **Decision-claim label:** *proposing* (classification is reading-dependent; see both readings below).
- **Location:** `Spec_Action_Surface_v1.md` §1.1 tier-set enumeration table, lines 145–146 — rows `tier-3-microvm` and `tier-4-full-vm`.
- **Defect:** The four-tier set is internally self-contradictory across three columns.
  - The identifier `tier-3-microvm` carries the tier label "Tier 3 **container** isolation" and a mechanism class of "Shared-kernel **container** (Docker / Podman) OR user-space kernel (gVisor) OR microVM-backed container (Kata)." The identifier says microVM; the label and mechanism column say container. ADR-F4 §Decision commits the tier-set as the ordered set "process / **container** / **microVM** / full-VM" — i.e., F4 treats *container* and *microVM* as **two distinct tiers**. The spec collapses F4's container tier and microVM tier into a single `tier-3-microvm` row, then re-uses the word "container" as that row's label.
  - F4 Consequences §(a) states the full-VM tier exists "as a distinct tier separate from microVM, **preventing the conflation Alternatives §1 below names as a structural failure**." The spec's `tier-3-microvm` row mixes Docker (a shared-kernel container, F4's container tier) with Kata/gVisor (microVM / user-space kernel, F4's microVM tier) into one tier — which is precisely the conflation F4 calls a structural failure, just shifted one tier down.
  - The escape-risk column compounds the contradiction: `tier-3-microvm` is annotated "Docker medium / gVisor low / Kata very low" — a single tier whose escape risk spans three of F4's risk bands. §1.2's "tier monotonicity per §1.1 escape-risk descending" invariant is not well-defined when one tier's escape risk is itself a range overlapping adjacent tiers.
- **Discriminator that classifies as Class 3:** (b) — requires upstream-phase artifact revision. If F4's tier-set ("process / container / microVM / full-VM") is the canonical four-tier ordering, the spec has silently re-bucketed it (container+microVM merged into `tier-3-microvm`; the spec's `tier-2-container` is F4's process-adjacent tier). Reconciling the spec to F4 changes the tier *cardinality semantics*, which is an ADR-F4 commitment. Alternatively, if the spec's four tiers are the intended set and F4's enumeration is loose prose, then F4 needs a clarifying revision so the canonical authority chain (ADR → spec) is not inverted. Either branch requires touching a Phase 3a artifact → Class 3.
- **Evidence:**
  - ADR-F4 §Decision: "Commit at the F4 layer to a **four-tier sandbox-isolation tier-set** (process / container / microVM / full-VM)".
  - ADR-F4 §Consequences (a): "Persona §5.1 computer-use-at-production-with-stronger-sandbox-tier requirement met via the full-VM tier ... as a distinct tier separate from microVM, preventing the conflation Alternatives §1 below names as a structural failure."
  - Spec line 145: identifier `tier-3-microvm`, label "Tier 3 container isolation", mechanism "Shared-kernel container (Docker / Podman) OR ... OR microVM-backed container (Kata)".
  - Spec line 144: identifier `tier-2-container`, label "Tier 2 process isolation", mechanism "Process isolation with seccomp / namespacing / sandbox-exec".
- **Two readings (operator must pick to fix classification):**
  - *Reading 1 — drift only (Class 1).* The four `tier-N` identifiers are the canonical set; the human-readable "Tier N <X> isolation" labels are sloppy and one column is misnamed. Fix is a label correction inside the spec, no semantic change. Under this reading the finding is Class 1.
  - *Reading 2 — structural re-bucketing (Class 3).* F4 commits container and microVM as separate tiers; the spec has merged them and the merge is load-bearing (it determines what `code-execution-2025-08-25` forcing to `tier-4-full-vm` actually means, and whether Docker-tier work and Kata-tier work are distinguishable at the `sandbox.tier` span attribute). Under this reading the merge is a substantive deviation from an F4 commitment → Class 3 via discriminator (b).
  The reviewer cannot determine from the spec text alone which reading the authors intended — §1.1's identifiers say one thing, the labels say another, and F4's prose says a third. This is why the finding is *proposing*, not *decided*.
- **V3 failure mode engaged:** #2 (silent scope narrowing) — F4's four-tier deliberation surface (process/container/microVM/full-VM as four distinct mechanism classes) appears narrowed to three distinct mechanism bands plus one merged band in the spec.
- **Voice FM engaged:** C10 (action safety) domain — the escape-risk monotonicity the tier-set exists to express is the C10 concern; a tier whose escape risk is a range undermines the gating guarantee C10 owns.
- **Resolution path:** Halt §1 clearance. Operator determines whether F4's "process / container / microVM / full-VM" is four distinct tiers (→ ADR-F4 v1.1 revision OR spec re-bucketing to restore four mechanism-distinct tiers) or whether the spec's identifiers are canonical and F4 prose is loose (→ ADR-F4 clarifying revision). Do not absorb the label/mechanism mismatch silently — per workspace CLAUDE.md §4.3, silent absorption of an ADR-vs-spec divergence contaminates every unit built against C-AS-01.

---

## Class 2 findings (moderate — current-phase artifact revision)

### F2-01 — `tier-3-microvm` escape-risk cell is a three-valued range, defeating the §1.2 monotonicity invariant
- **Decision-claim label:** *decided*.
- **Location:** `Spec_Action_Surface_v1.md` §1.1, line 145, escape-risk column ("Docker medium / gVisor low / Kata very low"); §1.2, line 154, "Per-tier capability lower bound" invariant ("tier monotonicity per §1.1 escape-risk descending").
- **Defect:** §1.2 asserts tier monotonicity grounded in "escape-risk descending" across §1.1's rows. But `tier-3-microvm`'s escape-risk cell holds three values spanning "medium" down to "very low." "Medium" overlaps `tier-2-container`'s "Medium (kernel CVE class)"; "very low" overlaps `tier-4-full-vm`'s "Very low (hardware boundary)." A monotonic-descending invariant cannot be evaluated against a tier whose risk is non-scalar and overlaps both neighbors. The invariant is stated but not satisfiable as written.
- **Discriminator:** (a) — affects substantive content of the current-phase artifact; the monotonicity invariant is a contract element downstream units (C-AS-02 `max()` composition correctness) rely on. Resolution is self-contained to the spec → Class 2. (Escalates to Class 3 only if F3-01 Reading 2 holds, since the fix is then the same re-bucketing.)
- **Evidence:** Line 145 escape-risk cell verbatim: "Docker medium / gVisor low / Kata very low". Line 154: "higher tiers structurally accommodate lower-tier operations (tier monotonicity per §1.1 escape-risk descending)".
- **V3 failure mode engaged:** #5 (missing uncertainty signals) — the range is presented as a flat capability cell with a [HIGH] Cluster 3 §2.2 citation, but the within-cell variance is not tagged or reconciled with the monotonicity claim.
- **Resolution path:** Revise §1.1/§1.2 so the monotonicity invariant references a well-ordered per-tier escape-risk value, or restate the invariant to not depend on a scalar escape-risk ordering. The reviewer does not prescribe which.

### F2-02 — Forced-tier rule wording is inconsistent between §1.3 and the C-AS-01 mechanism column
- **Decision-claim label:** *decided*.
- **Location:** `Spec_Action_Surface_v1.md` §1.3 line 162 vs §1.1 line 146.
- **Defect:** §1.3 forces `code-execution-2025-08-25` to `tier-4-full-vm` and annotates it "(microVM minimum)". Forcing to the *full-VM* tier while annotating "microVM minimum" is contradictory on its face — a microVM minimum is satisfied by `tier-3-microvm`, not `tier-4-full-vm`. Line 146's capability column for `tier-4-full-vm` says "LLM-generated code execution mandatory," and C-AS-02 §2.3 line 216 says "LLM-generated code execution ... `tier-4-full-vm` (microVM minimum; E2B Firecracker class)." Three sites describe the same forcing rule with two different tier names ("microVM minimum" vs "tier-4-full-vm"). If `tier-3-microvm` and `tier-4-full-vm` are genuinely distinct tiers (per F3-01), the forced tier for LLM-generated code is ambiguous: microVM or full-VM.
- **Discriminator:** (a) — substantive content of the current-phase artifact; a forcing rule that names two tiers is a contract defect downstream units cannot implement deterministically → Class 2.
- **Evidence:** §1.3 line 162: "`tier-4-full-vm` (microVM minimum)". §2.3 line 216: "`tier-4-full-vm` (microVM minimum; E2B Firecracker class)". F4 §Consequences (a): "microVM mandatory for LLM-generated code per §8.1" — F4 itself says *microVM*, not full-VM, for code execution.
- **V3 failure mode engaged:** #2 (silent scope narrowing) — the gap between F4's "microVM mandatory" and the spec's "tier-4-full-vm forced" is unreconciled.
- **Resolution path:** Reconcile the forced tier for `code-execution-2025-08-25` across §1.3, §1.1, and §2.3 to a single tier name; reconcile against F4 §Consequences (a)'s "microVM mandatory for LLM-generated code." If the intended tier is microVM, the parenthetical "(microVM minimum)" and the `tier-4-full-vm` target disagree and one is wrong; the reviewer flags the disagreement and does not pick.

### F2-03 — `tier-1-process` capability requirement embeds a persona value ("solo-developer non-compliance cells") without a persona citation at the contract row
- **Decision-claim label:** *decided*.
- **Location:** `Spec_Action_Surface_v1.md` §1.1 line 143, `tier-1-process` capability-requirement cell: "deterministic in-house tools at solo-developer non-compliance cells (operator-tunable under §1.5.2 policy override)".
- **Defect:** The tier-set enumeration is the foundational enum (C-AS-01 §1.1). Its `tier-1-process` row scopes the read-only/in-house exception to "solo-developer non-compliance cells" — a persona-specific deployment cell. C-AS-01's "Persona linkage" header (line 133) cites Persona §5.1, §8.1, §10.1, but not the persona section that establishes the solo-developer × compliance cell matrix. The phrase reads as an authoring-time persona assumption baked into the enum without a traceable persona citation at the point of use. Per the ADR/spec review discipline, a persona-dependent claim must trace explicitly to the persona document.
- **Discriminator:** (a) — the missing citation is a substantive trace gap in a current-phase artifact; resolution is adding an explicit citation, self-contained to the spec → Class 2. (Does not reach discriminator (c): the spec is not *overcommitting* a persona — the persona is already a design output; it is failing to *cite* the persona section the cell-matrix lives in.)
- **Evidence:** Line 143 cell text quoted above; C-AS-01 §Persona linkage line 133 cites only §5.1/§8.1/§10.1. The "non-compliance cells" terminology is also used at §2.3 line 221 and C-AS-12 §1.5.2 — i.e., it is load-bearing terminology, which makes the missing first-use citation a real gap, not cosmetic.
- **V3 failure mode engaged:** #1 (silent grounding collapse) — a substantive scoping claim without a resolvable primary-source citation at its point of assertion.
- **Resolution path:** Add the specific persona-document section citation establishing the solo-developer × compliance cell matrix to C-AS-01 (either the §Persona linkage header or the §1.1 row). The reviewer does not supply the section number.

### F2-04 — Cardinality-bound invariant cites the wrong revision-class authority
- **Decision-claim label:** *proposing* (depends on whether "Class-2 ADR-F4 revision" is intended as a workflow-class label or a typo).
- **Location:** `Spec_Action_Surface_v1.md` §1.2 line 153, "Cardinality bound": "Four values; new tier additions are a Workflow §4.1.2 Class-2 ADR-F4 revision".
- **Defect:** §1.2 asserts that adding a fifth sandbox tier is a Workflow §4.1.2 Class-2 revision. Workflow §4.1.2 Class 2 is defined as "ADR or document revision required within the current phase ... downstream phases are not invalidated." Adding a sandbox tier changes the C-AS-01 enum cardinality, which is consumed by C-AS-02's `SandboxTier` type (§2.1 line 187), C-AS-04's fail-class composition, and the `sandbox.*` span schema exported to OD (front-matter line 62). A tier addition therefore invalidates already-authored downstream contracts and, at Phase 7, already-built code — that is the Workflow §4.1.3 Class-3 profile ("foundational defect that invalidates downstream work"), not Class 2. The spec under-classifies the blast radius of its own cardinality change.
- **Discriminator:** (a) — the mis-citation is substantive: it tells a future operator that a tier addition is a contained current-phase revision when it is in fact a downstream-invalidating change. Resolution is self-contained to the spec (correct the cited class) → Class 2.
- **Evidence:** Line 153 verbatim. Workflow §4.1.2: "downstream phases are not invalidated." Workflow §4.1.3: "Foundational defect that invalidates downstream work ... Affected downstream phases ... are halted." `SandboxTier` is consumed at §2.1 line 187 and across C-AS-02/04 and the OD span export.
- **Two readings:** Reading 1 — the authors meant Class 2 and the under-classification is the defect (the finding stands as stated). Reading 2 — "Class-2" is a typo for "Class-3" and the citation should read §4.1.3. Either way the current text is wrong; the reviewer flags the mismatch and lets the operator confirm which class the cardinality invariant should name.
- **Resolution path:** Reconcile the cardinality-bound invariant's cited Workflow revision class against the actual downstream-invalidation profile of a tier-set cardinality change.

---

## Class 1 findings (minor — documentation drift)

### F1-01 — Tier-label numbering style is internally inconsistent
- **Location:** `Spec_Action_Surface_v1.md` §1.1 lines 143–146, "Tier label" column.
- **Defect:** Labels read "Tier 1 minimal isolation", "Tier 2 process isolation", "Tier 3 container isolation", "Tier 4 VM isolation" — the qualifier word ("minimal" / "process" / "container" / "VM") follows a different naming logic per row (severity adjective, then mechanism nouns) with no consistent scheme. This is cosmetic prose drift independent of the F3-01 semantic contradiction.
- **Resolution:** Inline fix in the affected document — regularize the label column to one naming scheme.

### F1-02 — Cold-start units and precision are presented inconsistently across rows
- **Location:** `Spec_Action_Surface_v1.md` §1.1 lines 143–146, "Cold-start" column.
- **Defect:** Cold-start values mix formats: "<10 ms", "10–50 ms", "100–150 ms", "Firecracker ~150 ms / full-VM seconds". The last cell switches unit (ms → seconds) and adds a per-mechanism split absent from the other rows. Not a semantic defect; a presentation inconsistency.
- **Resolution:** Inline fix — normalize the cold-start column format.

### F1-03 — "(microVM minimum)" parenthetical in §1.3 is undefined terminology on first use
- **Location:** `Spec_Action_Surface_v1.md` §1.3 line 162.
- **Defect:** The parenthetical "(microVM minimum)" appears without the spec defining what "minimum" qualifies relative to a forced tier. (The substantive contradiction this parenthetical creates is F2-02; the *drift* component is that the term is used without definition.) Flagged separately as drift; the reviewer does not propose a definition (operator-resolution territory).
- **Resolution:** Inline fix — define or remove the parenthetical once F2-02 is dispositioned.

---

## Findings considered and rejected (transparency)

The following attack vectors were applied to C-AS-01 §1 and did **not** surface a finding; the artifact handles them.

1. **Attack V8 — framing contamination (committed-claim violation).** Checked whether §1 assumes a single-LLM scope or excludes cloud/hybrid deployment surfaces. It does not — §1.1 and §1.3 are deployment-surface-parametric ("any deployment surface"), and tier mechanism classes span local and vendor-managed (E2B/Firecracker). No Class-3 framing violation. *(How a finding would have arisen: a tier row hard-coding "local-only" mechanisms.)*

2. **Attack V8 — framing contamination (not-committed-overcommitment of stack).** Checked whether §1 commits a specific sandbox provider at the spec layer where F4/D2 defer it. It does not — §1.3's "Deferred to implementation discretion" block explicitly defers microVM/full-VM mechanism and container-runtime selection to D2 §1.10 and Pattern Reference Catalog §11.3.2. Stack deferral is honored.

3. **Attack V4 — fabricated citations.** Spot-checked C-AS-01's ADR citations: ADR-F4 §Decision does commit the four-tier set; ADR-F4 §Consequences (a) does discuss `sandbox.tier` as structural attribute and the microVM/full-VM distinction; ADD §2.4 is the cited synthesis. The cited sections resolve. (The Cluster 3 §2.2 escape-risk citation could not be verified — Cluster deliverables are not in the workspace design-substrate set; noted as a verification limit, not a finding.)

4. **Spec-axis: failure-mode taxonomy completeness.** §1 is an enum contract, not an operation contract; fail-class taxonomy lives in C-AS-04. §1 itself does not own a failure surface, so the taxonomy-completeness axis does not fire on §1.

5. **Spec-axis: observable lifecycle.** Checked whether §1's tier-set has the observability hooks it needs. §1.2 names `sandbox.tier` / `sandbox.tech` as the structural/discriminator attributes and §2.5 places verification at the `sandbox.enter` event; §1's observability obligation is met by reference. No finding on §1.

6. **Attack V2 — silent scope narrowing on forced-tier rules.** Checked whether §1.3 enumerates all F4/D2 forcing conditions. §1.3 lists two (code-execution beta, computer-use) and both trace to ADR-D2 §1.1. No third forcing condition was found in F4/D2 that §1.3 omits. (The *wording* of the code-execution rule is defective — see F2-02 — but no forcing condition is missing.)

7. **Contract-vs-ADR honoring — `max()` composition.** Checked whether §1 contradicts F4's `max()`-composition commitment. §1 correctly scopes itself to the *enum* and defers composition to C-AS-02; no contradiction. (The label/mechanism contradiction is F3-01, a different axis.)

8. **Cardinality bound — is "four" itself defensible?** Checked whether four tiers is the right count vs F4. F4 §Decision commits exactly four tiers; the spec commits four. The *count* matches; the *bucketing of mechanisms into the four* is what F3-01 disputes, not the cardinality.

9. **Author-mode drift self-check (FM-C).** Verified no Resolution-path field above supplies replacement text, corrected tier labels, or specific citation section numbers. Confirmed — all resolution paths describe resolution shape only.

10. **Voice-FM mechanical-application self-check (FM-D).** The C10 FM engaged at F3-01 was applied as an *outcome* check (does the artifact's tier-set undermine escape-risk gating?), not a mechanism check (did a voice cross a boundary). Confirmed outcome-grounded.

---

## Disposition

Per Workflow §4.1.3, the highest-severity finding governs disposition. **One Class-3 finding (F3-01) is present**, classified *proposing* because its severity is reading-dependent:

- If **Reading 2** holds (F4 commits container and microVM as four mechanism-distinct tiers, and the spec's `tier-3-microvm` row has merged two of them), the disposition is **fork to ADR-F4 revision OR spec re-bucketing** — a Phase 3a artifact is touched, the §1 contract is halted, and C-AS-02/C-AS-04 and the OD `sandbox.*` span export are re-evaluated against the corrected tier-set.
- If **Reading 1** holds (the `tier-N` identifiers are canonical and only the human-readable label/mechanism columns are sloppy), F3-01 collapses to Class 1 and the disposition for §1 is **clearance with inline fixes** (F1-01/02/03 plus the four Class-2 items as current-phase spec revisions).

**The reviewer cannot pick the reading from the artifact text** — §1.1's identifiers, §1.1's labels, §1.1's mechanism column, and ADR-F4 §Decision's prose mutually disagree. **Operator decision is required before §1 can be cleared.** Recommended operator action: confirm against ADR-F4 §Decision and §Alternatives §1 (the "conflation as structural failure" passage) whether the harness has four mechanism-distinct tiers or four identifier-distinct tiers, then route F3-01 accordingly.

Independent of the F3-01 reading, the four Class-2 findings (F2-01 monotonicity-invariant non-evaluability, F2-02 forced-tier wording inconsistency, F2-03 missing persona citation, F2-04 cardinality-bound mis-class) require current-phase spec revision and should be resolved in the same revision pass.

**Systemic pattern note.** This is a single-contract scoped pass, so the §6 cross-artifact ≥3-occurrence pattern test does not formally apply. However, three of the eight findings (F3-01, F2-01, F2-02) share one root: the `tier-3-microvm` / `tier-4-full-vm` rows carry mechanism, label, escape-risk, and forced-tier content that is internally and upstream-inconsistent. If the full P5-CK pass over §2–§16 finds the same microVM/full-VM ambiguity recurring in C-AS-02/C-AS-04 (the `sandbox_tier_floor` table at §2.3 already shows the "(microVM minimum)" wording at line 216), the resolution scope is a single tier-set reconciliation at C-AS-01, not per-contract patches. Flagged as a *candidate pattern* (2–3 occurrences within scope); a full-spec pass is needed to confirm it as systemic.

---

*Scoped P5-CK pass — C-AS-01 §1 only. Full specification clearance requires review of C-AS-02 through C-AS-16. Out-of-scope contracts not enumerated.*
