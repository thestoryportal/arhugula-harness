# Fidelity Discipline — Worked Examples

Reference for the `spec-writer` skill. Load when the SKILL.md body is insufficient.

---

## 1. The verbatim round-trip check

When a resolution specifies text *verbatim*, the applied edit must reproduce it byte-exact — same characters, same casing, same ordering.

**Example (Tension 002 shape).** A resolution states: the canonical `TopologyPattern` enum is the spec C-CP-10 §10.1 vocabulary —

```
single-threaded-linear, orchestrator-workers, decentralized-handoff,
hierarchical-delegation, evaluator-optimizer, parallelization
```

Applying this means writing those six tokens **exactly**. Not `SINGLE_THREADED_LINEAR` (re-cased), not `decentralised-handoff` (spelling drift), not a reordered list. After the edit, copy the six tokens out of the spec file and diff them against the resolution source — a zero-change diff is the pass condition (`Project_Workflow_v1_8.md` §7.4.2).

**Failure shape:** the edit "cleans up" the enum to Python `UPPER_SNAKE` because that looks like a Python enum. That is verbatim drift (FM-3). The resolution said what the members are; if a casing transform were intended, the resolution would have said so.

---

## 2. The no-extension boundary

The authorized fix is exactly what the resolution names. Everything else is out of scope.

**In scope:** the resolution says "replace the §10.1 enum with the six-member vocabulary and realign acceptance criterion #1 to cite it." → Edit the §10.1 enum; edit acceptance #1. Done.

**Out of scope — surface as a finding, do not patch:**
- A neighbouring `CascadePolicy` enum that diverges the same way but the resolution did not mention. → Change-note finding F-1: "CascadePolicy at §10.x diverges similarly; not in this fix's scope; recommend a separate tension/resolution."
- A §10.2/§10.3 section-anchor mislabel noticed while editing. → Change-note finding F-2.
- An admissibility matrix that now reads oddly against the new enum. → If the resolution named it, in scope; if not, finding.

**Test:** "Did the resolution authorize this specific change?" Yes → apply. No → finding. "It's obviously also broken" is not authorization.

---

## 3. Change-note template

Prepend to the spec file (or update the existing change-note block):

```
## Change-note — v<NEW> (<date>)

**Trigger:** <Phase_7_Class_N_Tension_NNN_*.md filename | operator decision ref>
**Scope:** <contract IDs + section numbers changed, e.g. C-CP-10 §10.1, §10.1 AC#1>
**Revised:** <one line per revised section>
**Preserved verbatim:** <sections/contracts explicitly unchanged — must match the file>
**Findings surfaced (not patched):**
- F-1: <adjacent defect, out of scope, recommended routing>
**Downstream absorption owed:** <plan units citing the revised contract — for implementation-planner revision-pass>
**Version:** v<OLD> → v<NEW>
```

The change-note and the `Phase_7_Class_N_Tension` record must agree. After applying, update the tension record's disposition to "applied — spec v<NEW>".

---

## 4. Back-reference reconciliation

A revised contract is cited from three places:

1. **Intra-file** — other sections of the same spec citing the revised section. → The spec-writer updates these as part of the edit.
2. **The ADD / PRD** — up the authority chain. → These are *above* the spec in the chain (`CLAUDE.md` §1.3); a spec fix does not edit them. If the fix reveals an ADD/PRD inconsistency, that is a finding routed to `systems-architect`, not a spec-writer edit.
3. **Plan units** — down the chain, citing the revised contract by ID + section. → Not the spec-writer's edit. Flag in the change-note under "downstream absorption owed"; `implementation-planner` revision-pass absorbs it.

The spec-writer's reconciliation scope is exactly layer 1. Layers 2 and 3 are flagged, not edited.
