# Implementation Plan Template Reference

This reference is loaded when authoring requires the canonical plan section structure, the per-unit template, or examples disambiguating well-formed from malformed units.

---

## 1. Canonical plan section structure

```
# Implementation Plan v<version>

## Status block
(Status: Proposed | Accepted | Superseded; Version; Date; Phase; Skill;
 Promotion path; Source-set; Entry authorization; Exit gate)

## Change-note (vN → vN+1)
(present at revision-pass output; absent at v1.0 initial)

## Shape decision (front-matter)
(axis-led | component-led | milestone-led | dependency-graph-led;
 grounded in specification §X structure or dependency-graph topology)

## §1 Plan summary
(one paragraph; cites specification, ADD, PRD; states unit count, axis
 distribution, foundational anchor units)

## §2 Atomic units
(structured per shape decision; per-unit subsections using the §3
 template below)

## §3 Dependency graph
(textual representation: per-unit dependency lists + topologically
 sorted order + cross-axis dependency callouts)

## §4 Coverage matrix
(rows: spec contracts by ID; columns: plan units by ID; cell mark
 where contract is cited by that unit)

## §5 Cross-cutting integration units
(units whose scope spans multiple axes — cross-axis composition
 implementations consolidated when atomization yields N:1 contract-
 to-unit collapse)

## §6 Open items
(implementation-shape gaps surfaced during planning that warrant
 attention but do not block execution; cites contract carry-forwards
 from spec §6)
```

The status block, change-note position, and §4 coverage-matrix appendix mirror the specification's and PRD's conventions so artifacts share a shape.

---

## 2. Status block conventions

Status values mirror upstream artifacts (`Proposed` until P6-CK clears; `Accepted` after; `Superseded` when a successor version exists). Source-set enumerates the substrate consulted: specification version(s), ADD version, PRD version, persona version. Entry authorization names the workflow phase entry that activated the session. Exit gate names P6-CK as the clearance criterion.

---

## 3. Per-unit template

```
### U-<axis-or-component>-<N>: <one-line title>

**Scope.** <one or two sentences describing the single coherent change>

**Spec linkage.** <C-XX-NN §M for primary contract; additional
contracts cited for multi-contract composition; cite ADR / PRD only
when the spec contract's citation chain is not self-evident>

**Surfaces affected.** <logical file / schema / module names; e.g.,
"routing manifest schema definition", "sandbox tier composition
function", "lease.* span attribute namespace declaration in the OTel
emitter">

**Signatures introduced or modified.** <function / class / schema
signatures, copied from spec or derived from spec contract — do NOT
redesign at this layer>

**Depends on.** <[U-N, U-M, ...] or "(none)" for foundational units;
cross-axis dependencies flagged as "(cross-axis: <axis>)">

**Acceptance criterion (functional).** <testable when the unit is
complete, independent of other unrelated units>

**Acceptance criterion (integration), where applicable.** <testable
when the unit and its declared dependencies are complete>

**Notes (optional).** <implementation-shape observations or carry-
forward flags; do NOT include effort estimates or risk annotations>
```

Field-level discipline:

- **Scope.** One sentence preferred; two sentences when composition formula or surface boundary requires it. Not a description of the contract — a description of the change.
- **Spec linkage.** ID + section is mandatory. ID-only is the trace-omission failure mode.
- **Surfaces affected.** Logical names, not paths. The plan is portable across filesystem layouts; the execution session resolves logical names to paths.
- **Signatures introduced or modified.** Copy-from-spec. The planner is a transcription discipline at this field, not a design discipline. If the signature is not in the spec, the unit is extending the spec → defect.
- **Depends on.** Direct dependencies only. Foundational units declare `(none)`. Cross-axis dependencies declare the axis tag.
- **Acceptance criterion.** Testable. Two flavors: functional (verifiable on this unit alone, given declared dependencies are present) and integration (verifiable when this unit + dependencies are wired together). Integration is omitted when functional acceptance already covers the integration surface.
- **Notes.** Optional. Use for downstream carry-forward flags or implementation-shape observations the executor benefits from knowing. Never use for effort or risk.

---

## 4. Well-formed example (synthetic; illustrates shape only)

```
### U-AS-3: sandbox_tier composition function — initial wiring

**Scope.** Implement the `sandbox_tier(tool, call_site_context) -> SandboxTier`
composition function per C-AS-02 §2.1 signature and §2.2 formula. Wire the
five floor inputs as named-parameter calls to per-floor resolution functions
implemented in earlier units.

**Spec linkage.** C-AS-02 §2.1, §2.2.

**Surfaces affected.** Sandbox-tier composition module (the function exposing
the C-AS-02 signature to consumers).

**Signatures introduced or modified.** `sandbox_tier(tool, call_site_context)
-> SandboxTier` per C-AS-02 §2.1 (SandboxTier enum per C-AS-01 §1.1).

**Depends on.** [U-AS-1 (SandboxTier enum + C-AS-01 §1.1 substrate),
U-AS-2 (blast_radius_floor resolver per C-AS-02 §2.4),
U-AS-4 (sandbox_tier_floor resolver per C-AS-02 §2.3),
U-AS-5 (mcp_server_trust_tier_floor resolver — F4 C10 five-tier framework),
U-AS-6 (operator_policy_floor resolver per C-AS-02 + D5 §1.5 cross-axis: CP)].

**Acceptance criterion (functional).** Given a tool contract with declared
`minimum_tier` and a call_site_context with declared blast_radius_tier,
deployment_surface, mcp_transport, mcp_server, and persona_tier, the function
returns the `max()` of the five floor inputs as a SandboxTier value. The
verification surface — `sandbox.policy.assigned_tier_reason` enum naming the
winning floor source — is set per C-AS-02 §2.5.

**Acceptance criterion (integration).** When invoked at the `sandbox.enter`
event substrate (C-AS-15), the resolved sandbox.tier is verifiable as the
`max()` of the formula's five inputs and matches the
`sandbox.policy.assigned_tier_reason` attribution.
```

Why this is well-formed:

1. **Atomic** — one coherent change (composition function wiring); single focused session; independently testable given dependencies; coherent rollback boundary at the composition function definition.
2. **Spec-traced** — cites C-AS-02 §2.1 and §2.2; the contract IDs and sections are verifiable against the substrate.
3. **Dependency-aware** — five dependencies named, one cross-axis (operator_policy_floor → CP), no transitive omissions.
4. **Implementation-grade** — names the function signature (transcribed from spec, not redesigned), names the surface ("sandbox-tier composition module"), gives functional and integration acceptance criteria that are testable.

It does NOT name a sandboxing technology, runtime library, or implementation choice — those remain deferred per C-AS-02 spec boundary.

---

## 5. Malformed examples (illustrating the anti-patterns)

### 5.1 Spec extension

```
### U-AS-3: sandbox_tier composition function

**Spec linkage.** C-AS-02 §2.2.
**Surfaces affected.** Sandbox-tier composition module using gVisor runtime
for tier-2-container.
**Signatures introduced or modified.** sandbox_tier(...) plus internal
gVisor lifecycle hooks.
...
```

**Defect.** gVisor is not named in C-AS-02 §2.3 sandbox_tier_floor lookup table. The "Deferred to implementation discretion" section of C-AS-02 explicitly defers specific sandboxing technology. The unit is extending the spec by binding tier-2-container to gVisor. Resolution: back-flow to Phase 5 if the binding is needed; otherwise omit the technology reference.

### 5.2 Under-decomposition

```
### U-AS: Implement the action surface

**Scope.** Implement the entire action surface per Spec_Action_Surface_v1.md.
**Spec linkage.** Spec_Action_Surface_v1.md (entire).
**Depends on.** (none)
**Acceptance criterion.** Action surface complete.
```

**Defect.** Sixteen contracts collapsed into one unit; multi-week effort; no single coherent change; rollback boundary is "the entire axis." Fails §3.1, §3.2, §3.3, §3.4 simultaneously. Resolution: re-atomize per the spec's contract structure.

### 5.3 Over-decomposition

```
### U-AS-3.1: Add the SandboxTier import statement to the composition module
### U-AS-3.2: Define the sandbox_tier function signature
### U-AS-3.3: Add the docstring to sandbox_tier
### U-AS-3.4: Wire the first floor input
### U-AS-3.5: Wire the second floor input
...
```

**Defect.** Single-line edits as units; trivial; rollback boundary at line level is incoherent with `max()` formula's atomic semantics. Fails §3.2. Resolution: coalesce U-AS-3.1 through U-AS-3.5+ into U-AS-3.

### 5.4 Missing dependency

```
### U-AS-3: sandbox_tier composition function — initial wiring

**Depends on.** (none)

**Acceptance criterion (functional).** The composition function returns the
max() of the five floor inputs ...
```

**Defect.** Acceptance criterion silently requires `SandboxTier` enum (U-AS-1 product), `blast_radius_floor` resolver (U-AS-2 product), etc. The dependency declaration `(none)` is false. Fails §7 coverage discipline. Resolution: declare the five direct dependencies.

### 5.5 Under-specified acceptance

```
### U-AS-3: sandbox_tier composition

**Acceptance criterion.** Sandbox tier composition works correctly.
```

**Defect.** Not testable; "works correctly" is not a criterion. Fails §4.4. Resolution: rewrite acceptance criterion at testable granularity — name the inputs, the expected output computation, the verification surface.

### 5.6 Trace-omission

```
### U-AS-3: sandbox_tier composition function

**Spec linkage.** Spec_Action_Surface_v1.md (general).
```

**Defect.** Contract-ID + section not cited; "general" is not a citation. Fails §4.2 spec-traceability. Resolution: cite `C-AS-02 §2.1, §2.2` (or whichever specific contract surface authorizes the unit).

### 5.7 Risk/estimate annotation

```
### U-AS-3: sandbox_tier composition function

**Effort estimate.** ~2 days
**Risk.** High (multi-floor composition complexity)
**Acceptance criterion (functional).** ...
```

**Defect.** Per-unit risk and effort annotations are operator pre-decision out-of-scope. Plan is for the executor, not for resourcing. Fails §10 anti-pattern. Resolution: remove these fields; resourcing is a separate artifact owned by the operator.

### 5.8 PR/commit/file-granularity pre-commitment

```
### U-AS-3: sandbox_tier composition function

**Surfaces affected.** /src/sandbox/composition.py:sandbox_tier, lines 47-92,
in a single PR titled "feat: implement sandbox_tier composition per C-AS-02"
with three commits.
```

**Defect.** Specific filesystem path, line numbers, PR title and commit count are stack-dependent and execution-discretion. Plan describes units at logical-rollback-boundary granularity, not at git-mechanics granularity. Resolution: replace with logical surface name ("sandbox-tier composition module").

---

## 6. Coverage matrix shape

Coverage matrix at plan §4 is a contract-by-unit grid. Rows = spec contracts (by ID). Columns = plan units (by ID). Cell marked when the unit cites the contract at `Spec linkage`. Empty row = uncovered contract (defect; coverage gap finding). Empty column = unit without any contract citation (defect; trace-omission finding).

Example fragment:

```
                    | U-IS-1 | U-IS-2 | U-AS-1 | U-AS-2 | U-AS-3 | U-CP-1 | ...
C-IS-05             |   X    |   X    |        |        |        |        |
C-AS-01             |        |        |   X    |        |   X    |        |
C-AS-02 §2.1, §2.2  |        |        |        |        |   X    |        |
C-AS-02 §2.3        |        |        |        |   X    |        |        |
C-AS-02 §2.4        |        |        |        |   X    |        |        |
C-CP-05 §5.1        |        |        |        |        |        |   X    |
...
```

When a contract decomposes into sub-section coverage (C-AS-02 above), the matrix rows split per cited sub-section. This keeps coverage explicit at the section level the trace-back discipline requires.

---

## 7. Cross-cutting integration units (§5 of plan)

When a single unit covers multiple closely-coupled contracts (rare; usually for cross-cutting integration), the unit lives at plan §5 and its `Spec linkage` field cites all governing contracts ordered by primacy. Example shape:

```
### U-X-1: Lifecycle-event emission wiring across topology, HITL, audit

**Scope.** Wire the C-CP-05 lifecycle event substrate to the C-CP-14 topology
namespace, C-CP-20 HITL namespace, and C-CP-20 audit namespace per §5.5
composition table. Single wiring point; multiple downstream consumer
namespaces; bounded refactor scope.

**Spec linkage.** C-CP-05 §5.5 (primary); C-CP-14 §1.9 (topology namespace);
C-CP-20 §1.4.1 (audit namespace); C-CP-20 §1.8 (HITL namespace).

**Surfaces affected.** Lifecycle-event emitter wiring point in the
observability surface.
...
```

Cross-cutting consolidation is justified when atomizing each composition pair into a separate unit produces a thicket of trivial units that fail §3.2 (over-decomposition). Document the consolidation rationale in `Notes`.
