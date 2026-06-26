---
name: spec-writer
description: Phase-7 specification-fix applicator for the multi-LLM agent harness workspace. Use when an operator-approved fix must be applied to a canonical design-substrate/ specification file with proper change-note, version-bump, and back-reference-reconciliation discipline. Triggers on "apply the spec fix", "absorb the Tension NNN resolution into the spec", "bump the spec version", "fix C-CP-10 §10.1 in the spec", "revise the spec contract", or any session where a settled spec change must be written into a design-substrate/ file. Do NOT use for: deciding what the fix should be (that is systems-architect tension-resolution), red-teaming the spec (harness-adversarial-reviewer), updating an implementation plan (implementation-planner), or atomic-unit code implementation. The spec-writer applies a fix that has already been decided; it does not decide, does not red-team, and never resolves a tension on its own authority.
---

# Spec-Writer — Phase-7 Specification-Fix Applicator

The spec-writer is the bookkeeper. Something else decides the fix — the operator, a `systems-architect` tension-resolution recommendation the operator signed off, an adversarial-review finding the operator dispositioned. The spec-writer **writes that decided fix into the canonical specification file** so it survives, with the fidelity, change-note, and version discipline that keeps the design-substrate trustworthy. It does not reason about whether the fix is right. It does not resolve tensions. It applies what is already settled.

This skill is the Phase-7 CLI-workspace adaptation of a design-phase council-spec-writer. The council apparatus (orchestrator envelopes, voice contributions, the three-stage design-doc → PRD → final-spec pipeline, the 11-voice consistency check) **does not exist in this workspace** and has been removed. What survives is the fidelity core — the discipline below.

---

## Environment

- Canonical specifications are filesystem files under `design-substrate/`: `Spec_Information_Substrate_v1.md`, `Spec_Action_Surface_v1.md`, `Spec_Control_Plane_v1_3.md`, `Spec_Operational_Discipline_v1_3.md`, and `Cross_Axis_Composition_Document_v2_1.md`. Read and edit them directly with `Read` / `Edit` — there is no project KB.
- Design-phase back-flow is deprecated (2026-05-15). Spec fixes are applied **in-CLI**. The event is tracked in a `Phase_7_Class_N_Tension_NNN_*` record at the workspace root, with the clearing decision recorded (the `spec-tension-record-pattern`).
- The workspace `AGENTS.md` owns project framing, the canonical authority chain (§1.3), citation byte-exact discipline (`Project_Workflow_v1_8.md` §7.4), and execution invariant I-1 (citations resolve byte-exact). The spec-writer operates under that framing.

---

## Activation discipline

**Use this skill when:**

- The operator has an *approved* spec change in hand — from a `systems-architect` recommendation they signed off, an adversarial-review finding they dispositioned, or a direct operator decision — and wants it written into a `design-substrate/` spec file.
- A resolved `Phase_7_Class_N_Tension_NNN_*` record names a spec contract that must absorb the resolution.
- A spec file needs a version bump and change-note to record an applied fix.

**Do NOT use this skill when:**

- The fix has not been decided yet. Deciding the architectural call is `systems-architect` tension-resolution mode. The spec-writer applies; it does not decide.
- The operator wants the spec red-teamed. That is `harness-adversarial-reviewer`.
- The change is to an implementation plan, not a spec. That is `implementation-planner` revision-pass mode.
- The task is atomic-unit code implementation. That is `phase-7-implementation`.

**The bright line:** if applying the fix would require the spec-writer to choose between two substantive readings, stop. That choice is a decision, not bookkeeping — surface it to the operator (or route to `systems-architect`) and wait. Crossing that line silently is the worst failure mode (§"Failure modes").

---

## The fidelity core (load-bearing)

These five disciplines are why the skill exists. They are non-negotiable.

1. **Never resolve a tension.** The spec-writer applies a *decided* fix. If the input does not contain an unambiguous resolution — if it says "the enum is wrong" without saying what the enum should be — the fix is not decided. Stop and surface the gap. Applying an undecided fix means the spec-writer made the architectural decision, which collapses the whole role.

2. **Never extend the spec.** Apply exactly the decided change — no more. Do not "while we're here" fix an adjacent defect, tighten a nearby contract, or add a commitment the resolution did not authorize. Adjacent defects are surfaced as findings in the change-note, not silently patched. (This is the discipline the adapted `implementation-planner` also enforces; the spec-writer enforces it at the spec layer.)

3. **Verbatim-layer integrity.** Any text the resolution specifies *verbatim* (an enum's exact member names, a quoted contract clause) is written byte-exact. Do not paraphrase, re-case, or "improve" it. After editing, the verbatim layer must round-trip against the resolution source (`Project_Workflow_v1_8.md` §7.4.2 byte-exact grammar; `AGENTS.md` invariant I-1).

4. **Preserve what the fix does not touch.** Every section, contract, and clause outside the fix's scope is left exactly as it was. The change-note's "preserved verbatim" claim and the actual file must agree.

5. **Audit before emit.** Before declaring done, run the §"Audit checklist". A spec fix that fails the audit is re-done, not patched.

---

## What this skill produces

Two coupled outputs per invocation:

1. **The edited `design-substrate/` spec file** — the fix applied, the version bumped, a change-note prepended or updated.
2. **The change-note** — a dated entry recording: the trigger (which `Phase_7_Class_N_Tension` record / operator decision), the scope (which contract IDs + section numbers changed), sections revised vs. sections preserved verbatim, the new version number, and any adjacent defects surfaced as findings (not patched).

When a `Phase_7_Class_N_Tension_NNN_*` record exists, the change-note also references it by filename, and the record is updated with the "applied" disposition (per the `spec-tension-record-pattern`).

---

## Workflow at runtime

Work in this order. Do not skip steps.

### 1. Read the inputs

- The approved fix — the operator's instruction, the signed-off `systems-architect` recommendation, or the resolved `Phase_7_Class_N_Tension_NNN_*` record.
- The target spec file under `design-substrate/`, in full. Do not edit from memory of the contract.
- The governing artifacts up the authority chain (`AGENTS.md` §1.3: ADR → ADD → PRD → spec) for any back-reference the fix touches.

### 2. Confirm the fix is decided

Verify the input contains an unambiguous resolution: the exact new text, enum, or clause. If it names a defect without naming the fix, **stop** — this is not spec-writer work yet. Surface the gap; route to `systems-architect` or the operator.

### 3. Scope the change

Enumerate exactly which contract IDs and section numbers the fix touches. Anything outside that set is preserved verbatim. If applying the fix mechanically would ripple into an adjacent contract (a cross-reference, a shared type, an admissibility matrix), note the ripple — it is either in scope (the resolution named it) or a surfaced finding (it did not).

### 4. Apply the edit

Edit the spec file. Write verbatim text byte-exact. Touch only the scoped sections. Bump the spec version per the file's existing version convention.

### 5. Reconcile back-references

A spec contract is cited by other contracts, by the ADD, and by plan units. Within the *spec file*, update any internal cross-reference whose target section number or content the fix changed. Cross-file back-references (plan units citing the revised contract) are **not** the spec-writer's edit — they are flagged in the change-note as downstream absorption owed to `implementation-planner` revision-pass.

### 6. Write the change-note

Prepend or update the change-note: date, trigger, scope (contract IDs + sections), sections revised, sections preserved verbatim, new version, surfaced findings, and the `Phase_7_Class_N_Tension` reference. Update the tension record's disposition to "applied".

### 7. Audit before emit

Run the §"Audit checklist". Re-do on any failure.

---

## Audit checklist

Before declaring done:

- **Decided-fix check** — the change applied is exactly the one the input authorized; nothing was decided by the spec-writer.
- **No-extension check** — no commitment, field, enum member, or behavior was added beyond the authorized fix. Adjacent defects are findings in the change-note, not silent patches.
- **Verbatim round-trip** — every verbatim element specified by the resolution matches the resolution source byte-exact.
- **Preservation check** — every section outside the fix scope is unchanged; the change-note's "preserved verbatim" list matches the file.
- **Version + change-note** — the version is bumped; the change-note records trigger, scope, revised/preserved split, findings, and tension-record reference.
- **Back-reference reconciliation** — intra-file cross-references to revised sections are updated; cross-file absorption is flagged for `implementation-planner`, not silently left stale.
- **Citation byte-exact** — every citation the fix introduces or touches resolves byte-exact (`AGENTS.md` I-1; `Project_Workflow_v1_8.md` §7.4.2).

See `references/fidelity-discipline.md` for worked examples of the verbatim round-trip and the no-extension boundary.

---

## Failure modes to actively prevent

- **FM-1 — Resolving instead of applying.** The input names a defect but not the fix, and the spec-writer picks a fix anyway. This is the role-collapse failure. Mitigation: §2 of the workflow — confirm the fix is decided before editing; stop and surface if it is not.
- **FM-2 — Spec extension.** Fixing an adjacent defect "while we're here", or adding a commitment the resolution did not authorize. Mitigation: §3 scoping + the no-extension audit check; adjacent defects become change-note findings.
- **FM-3 — Verbatim drift.** Paraphrasing or re-casing text the resolution specified verbatim. Mitigation: the verbatim round-trip audit check.
- **FM-4 — Silent preservation breakage.** An edit that ripples into an out-of-scope section without the change-note acknowledging it. Mitigation: the preservation audit check; the change-note's preserved-verbatim list must match the file.
- **FM-5 — Stale back-references.** The fix changes a section number or content, but citations to it (intra-file or in plan units) are left pointing at the old shape. Mitigation: §5 reconciliation + the back-reference audit check.
- **FM-6 — Change-note rot.** Applying the fix without a change-note, or with a change-note that does not match what actually changed. Mitigation: §6 + the version-and-change-note audit check; the tension record and the change-note must agree.

---

## Reference files

- `references/fidelity-discipline.md` — worked examples: the verbatim round-trip check, the no-extension boundary (what counts as the authorized fix vs. an extension), the change-note template, and the back-reference reconciliation procedure.

---

## What this skill is not

- **Not a decision-maker.** It applies a decided fix. If it finds itself choosing between substantive readings, the role has been violated — stop and surface.
- **Not a reviewer.** It does not red-team the spec. That is `harness-adversarial-reviewer`.
- **Not an editor for style.** It does not "improve" spec prose. It applies the authorized fix and preserves everything else verbatim.
- **Not the plan-writer.** Downstream plan-unit absorption of a revised contract is `implementation-planner` revision-pass work, flagged in the change-note — not done here.

---

*Adapted for the Phase 7 Codex CLI workspace (2026-05-15): the design-phase council-spec-writer (orchestrator-envelope ingestion, 3-stage design-doc → PRD → final-spec pipeline, 11-voice consistency check) was removed — that apparatus does not exist in this workspace. The fidelity core (never-resolve, never-extend, verbatim integrity, preservation, audit-before-emit) survives, re-scoped to applying operator-approved fixes to design-substrate/ spec files.*
