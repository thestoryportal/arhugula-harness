Actual reviewer 40cd9c0e-ad5c-41bb-8899-70c02173cae4 end_turn 2026-10-01T08:01:23.636Z

**Design GO on one recommendation.** Extend `ChildResumeRefusal` by one member, `hitl-gate-config-changed`, and add one typed refusal carrier to `RunResult`. Runtime's sub-agent dispatch then re-raises that carrier as the existing `ChildResumeRefusedError` instead of `SubAgentChildFailedError`. The parent's existing typed handling then does the rest. The N1 requirement stays exactly as you stated it. This is a source design, not acceptance.

## Root cause at current main (`5d93b0bf`, my reads)

The original triage still holds at current bytes, and the defect is wider than N1. The typed refusal is lost at every level above the first, not just once.

1. **The leaf refuses correctly but untyped.** G is LINEAR. Its guard returns FAILED with `linear-resume-hitl-gate-config-changed at …` before any step runs (`workflow_driver.py:5363-5380`). By then, `ClaimedChildAdmission.run_with_child_authority` has already claimed and started G (`claimed_child_admission.py:90-104`). G returns normally, so it is not a gateway refusal.
2. **Runtime makes it generic.** C's dispatch of G turns any FAILED child into `SubAgentChildFailedError` (`sub_agent_dispatch.py:1216-1258`). Only a *raised* `ChildResumeRefusedError` is typed (`:1155`).
3. **C records the branch as done.** C's ORCHESTRATOR_WORKERS worker catches the generic error and records a `completed` terminal with no output (`workflow_driver.py:14956-14973`). Only `ChildResumeRefusedError` is terminal (`:14872-14876`, and `:15219-15229`, which runs before any policy branch).
4. **The same loss repeats at R.** Even if C did refuse, C returns `RunResult(FAILED, "orchestrator-workers-child-resume-refused (…)")` built from a plain string (`:3214-3224`). R's dispatch of C goes back through `:1254` and becomes generic again. Root and mid are both ORCHESTRATOR_WORKERS (`preaction_installed_witness.py:362-370`).
   - The same seam would also lose an *existing* Runtime refusal two levels down, for example a grandchild `claim-busy`. That is my inference from the code; I did not trace it in a test. I found no test that carries a depth-2 refusal up to the root; `test_b104_task4c_child_resume_refusal.py` covers one level only.
5. **The contract doesn't define the parent side.** CP v1.124 §0.2–§0.4 closes the set at nine Runtime-raised members and says nothing about how a refusal moves through more than one level.
6. **Not re-read at current bytes:** the cascade-pause capture lines and the `TEAM_BINDING`→`PAUSE` mapping. For those I am relying on the triage.

**Why not the alternatives:**
- **Raise from the CP leaf:** this breaks the §25.2 rule that a run *returns* its result, and changes what the depth-0 root does. It also does nothing for step 4, where C *returns* FAILED.
- **Map an existing member** such as `snapshot-mismatch`: that would be false, because the snapshot is valid.
- **Classify from `fail_class` text:** this is the forbidden string-shaped approach.

The step-4 hop needs a typed value on `RunResult` whatever else is chosen.

## The change

**Contract: CP delta, next free version after v1.124.** Buford resolves version numbers. I read nothing past v1.124.
1. `ChildResumeRefusal` grows to ten members: `hitl-gate-config-changed`. It means: the child was admitted, and its own resume found that its applicable HITL gate configuration differs from the capture, before any of its steps ran.
2. Add one frozen value type, `ResumeRefusal`, holding a non-empty set of reasons and `audit_signing_failed: bool`.
3. Add `RunResult.resume_refusal: ResumeRefusal | None`. It is non-None only when `status == FAILED`, enforced by a model validator. It is set in exactly two places:
   - the pre-step HITL-config resume guards (LINEAR `:5373`, evaluator-optimizer `:11679`, decentralized-handoff `:15989`);
   - every refused terminal: ORCHESTRATOR_WORKERS `:14571` and `:15225`, PARALLELIZATION `:9913` and `:10616`.
4. Build the fail class and the carrier together from the same recorded refusals, so they cannot disagree. The fail-class format, the sort order and the leaf's own `fail_class` text are unchanged.
5. `ChildResumeRefusedError` carries a `ResumeRefusal`. The current `(reason, detail, *, audit_signing_failed)` constructor stays for single-reason callers. Add one constructor that takes a `ResumeRefusal`. There must be only one stored representation; callers of `.reason` migrate to it, including `sub_agent_dispatch.py:1176`, which would otherwise drop reasons.
6. Restate the at-most-once limit:
   - the refused descendant ran no step;
   - at an ancestor in between, siblings already dispatched in this same resume may have run, under the existing barrier terms;
   - every ancestor ends FAILED with no capture;
   - the root record is consumed by its started claim.

**Contract: Runtime delta, next free version.** It must not overlap A5's proposed v1.135, which I did not read. It amends §14.7.2 step 7, the FAILED row:
- A FAILED child with `resume_refusal` raises `ChildResumeRefusedError` carrying that refusal, after the same best-effort audit as the `:1155` path.
- If signing fails closed, it raises `RefusedChildAuditSigningError` carrying the full refusal, never `PostEffectAuditSigningError`.
- Any other FAILED child stays `SubAgentChildFailedError`, so a worker that genuinely ran and errored keeps today's semantics.
- Fence and cancellation `BaseException` signals are untouched.

**Source files:**
- `harness-cp/src/harness_cp/workflow_driver_types.py`: the enum, `ResumeRefusal`, the `RunResult` field and its validator, and the error constructor.
- `harness-cp/src/harness_cp/workflow_driver.py`: the three guards and the refused-terminal builder.
- `harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py`: the FAILED arm.
- `harness-runtime/src/harness_runtime/lifecycle/audit_signing_errors.py`: `RefusedChildAuditSigningError` takes a `ResumeRefusal`.
- No change to the claim store or to `api.resume`. The docstring at `api.py:1322-1323` says the started claim is what refuses a record that was already resumed. With no new capture, the second resume therefore hits the same consumed record, which gives `claim-refused`. That is inferred from the docstring, not traced.
- The witness needs no change. Its `ROOT_FAMILY` and `REFUSAL_REASON` already match `orchestrator-workers-child-resume-refused (hitl-gate-config-changed)`.

**Scope decision for Buford:** the two fan-out gate-owning sites (`:8521` and `:12628`) return a string from `_resume_body_mismatch`. Including them means changing that closure's return type to a typed mismatch. **I recommend including them** for a uniform contract. If they are deferred, name the limit. Other pre-step child FAILED results (material diff, step index out of range) can also be laundered at `:1254`. They are a named follow-up, not part of this fix.

## Provider-free proof (red, green, mutation)

**Tests:**
- **Values** (`cp_tests/test_b104_child_resume_refusal_values.py`): ten members and their spellings; sorted rendering such as `… (claim-busy; hitl-gate-config-changed)`.
- **CP carrier** (new `cp_tests/` file):
  - each of the three guards gives FAILED with `resume_refusal.reasons == {hitl-gate-config-changed}`, unchanged leaf text, and zero steps dispatched;
  - a step that genuinely raises gives `resume_refusal is None`;
  - refused terminals carry the union of reasons plus the audit flag;
  - the validator rejects the carrier on a status other than FAILED;
  - a stub dispatcher raising a multi-reason refusal gives a parent fail class with the sorted union.
- **Runtime dispatch** (new `harness-runtime/tests/` file):
  - FAILED with the carrier raises typed, with the audit composed;
  - a fail-closed signing failure raises `RefusedChildAuditSigningError` with the full set;
  - FAILED without the carrier raises `SubAgentChildFailedError`;
  - the post-effect signing path is unchanged.
- **Integration** (real durable protocol, `ClaimedChildAdmission` bound as in the S1 tests), R(ORCHESTRATOR_WORKERS)→C(ORCHESTRATOR_WORKERS)→G(LINEAR):
  - With R's placement removed, the first resume gives root FAILED with exactly `orchestrator-workers-child-resume-refused (hitl-gate-config-changed)`, `pause_snapshot` None, an unchanged record count, no witness.a/c/d calls and no `hitl:` audit or webhook.
  - The second resume raises `ResumeClaimRefusedError(claim-refused)`.
  - Add a depth-2 grandchild `claim-busy` case that reaches the root typed.
  - Add a control case: a grandchild that genuinely errors under `pause` behaves exactly as today.

**Mutations that must turn a test red:**
1. Drop the carrier at the leaf guard.
2. Map a FAILED child with the carrier to the generic error.
3. Set the carrier at a refused terminal but not in its fail class, or the reverse.
4. Set the carrier on every FAILED result. The control case must catch this.
5. Classify by a `fail_class` substring. Test with a FAILED child whose text contains `hitl-gate-config-changed` but has no carrier.
6. Use `PostEffectAuditSigningError` for a refusal whose audit signing fails.

## Installed obligations

- After the fix lands in the final candidate artifact: one consent-gated installed N1 run (`run` → `resume-lowered` → `resume-lowered-again`) on the existing witness bytes.
- The triage caveat still applies: C declares its own `PRE_ACTION(witness.a)`, so N1 proves that the inherited set changed, not that the policy was lost.

## Ruling on n3

The source tests do cover wrong head, receipt, startup hook and wheel pin (`test_preaction_installed_witness.py:678`, `:712`, `:728`). A positive installed run passes those gates; it is not negative evidence. For full goal fidelity, **one bounded installed negative-provenance attempt is required**:
- Run the witness against the installed artifact with one deliberately wrong *expected receipt digest* supplied by the operator. This needs no change to the artifact; avoid wheel or hook mutation.
- Assert a refused exit, no scenario or output directory, no service or spawned process, and a retained log.
- It needs the same consent gate as any installed run.

## Other limits

- Typing of the witness file is still UNKNOWN until a scoped compiler run is done.
- I did not read the A5 drafts or anything past CP v1.124 and Runtime v1.133.
- I ran nothing, so the green, red and mutation results above are obligations, not evidence.

RELEASED, no handles held. I made no writes or commands and started no agents.
