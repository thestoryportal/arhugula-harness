# Arc-open grounding — `B-TOP-LEVEL-CRASH-RESUME-FINAL-STATE-RECONSTRUCT`

*R-FS-1 forward-arc grounding. 2026-06-26. Mode-agnostic process-substrate (no design-substrate change, no code change in this grounding pass). Records the fork-vs-impl probe `B-CHILD-CRASH-RESUME-FINAL-STATE-RECONSTRUCT-finding-v2.md §4` flagged for grounding "at open," and the `#766` git_head narrative registered as "fork-bearing — ground fork-vs-impl at open."*

---

## 0. TL;DR

`#766` built child-scoped final_state reconstruction (`reconstruct_final_state` opt-in; only `child_workflow_runner` passes `True`; top-level `api.run`/`api.resume` pass the default `False` → byte-unchanged suffix-only). This arc is the **top-level** analogue: make a top-level crash-resume / `api.resume` return the COMPLETE `final_state` (reconstructed from the durable committed-prefix outputs) instead of the silently **suffix-only** state it returns today.

**The probe at open (the load-bearing question): is top-level suffix-only resume `final_state` a committed/relied-on semantic, or an unclosed gap?**

**Finding (RESOLVED by empirical probe): impl-not-fork → BUILD default-on.** The provisional read below (§3) leaned fork on the user-facing-default-change framing. An advisor reconcile + a **decisive empirical probe** overturned that as over-caution: the §25.2 insurance read CONFIRMED at source that the spec is silent (v1.75 line 11 states there is **NO** final_state output-equivalence / resume-transparency invariant), and flipping the `execute_workflow` default `False→True` broke **exactly ONE test** — the `#766` flag-isolation control `test_no_reconstruct_leaves_suffix_only_final_state` — across the full CP suite (1395 passed / 1 failed) AND the full runtime suite (**2134 passed / 0 failed**, incl. the live-e2e `api.run`/`api.resume` integration tests). **No real consumer relies on suffix-only.** Per the `#766` advisor's own decision rule (clean-no everywhere → silent-corruption bug-fix → build), this earns the SAME impl-not-fork classification `#766` got for the structurally-identical child case. The "candidate fork" / `#766`-punt-voice was deferral-to-grounding, not evidence-for-fork; the one control test is `#766`'s own punt-language, not an independent commitment. **Disposition: BUILD default-on (CP-only flip), spec amendment DEFINING the resume-transparency invariant (closing the silent gap), no operator gate — FULL-SPEC + pre-authorized back-flow authorize it; report the user-facing change in the PR + handoff.** See §3.5.

---

## 1. The mechanism (already exists — this arc only flips the scope)

`harness-cp/src/harness_cp/workflow_driver.py`:
- `execute_workflow(..., reconstruct_final_state: bool = False)` (`:1770` / `:2038`).
- Seeding gate (`:3313-3330`): `if reconstruct_final_state and resume_at > 0 and engine_class in (EVENT_SOURCED_REPLAY, WAL_SEGMENT)` → read the durable committed prefix `[0, resume_at)` via the shared `_read_durable_replay_prefix` (fail-closed on store↔ledger skew) and seed `accumulated[step_id]`.
- Comment `:3308-3310`: *"Top-level runs pass `reconstruct_final_state=False` (default) → the accepted suffix-only top-level resume semantic is byte-unchanged (the fork-bearing top-level reconstruction is the registered follow-on)."*

`harness-runtime/.../lifecycle/child_workflow_runner.py:187` passes `reconstruct_final_state=True`. The top-level `api.run` (`api.py:539`) / `api.resume` (`api.py:715`) path does NOT — so a top-level crash-resume over a committed prefix returns `final_state` = post-resume steps only, status SUCCESS (silent truncation).

**The arc = make the top-level path reconstruct.** Mechanically trivial (flip a flag / extend the gate). The entire substance is the fork-vs-impl decision below.

## 2. The probe (3 questions, per the `#766` advisor's decision rule)

**(a) Spec/ADR — does anything commit suffix-only as intended? NO.**
- CP spec delta chain (`Spec_Control_Plane_v1_*.md`, head v1.75): `final_state` + resume grep finds NO positive statement that a resumed `final_state` is suffix-only by design. §25.2 defines `final_state` for the no-crash happy path only.
- Runtime spec §25 mentions suffix-only ONLY as the #746 SUBAGENT-revert *trap* ("a suffix-only/empty child `final_state`"), i.e. a known hazard, not a designed feature.
- ADR-D1 §1.1 commits the channel/INPUT-side replay (inter-step dataflow), not the OUTPUT-side `final_state` fidelity (per `#766`'s advisor grounding). → **leans impl.**

**(b) Existing test asserting suffix-only as the contract? ONE, flag-isolation.**
- `harness-cp/tests/test_workflow_driver.py:1349` `test_no_reconstruct_leaves_suffix_only_final_state` asserts `result.final_state.keys() == {"step-2"}` when `reconstruct_final_state` is default-off (the path `api.run` takes). Docstring (`:1352-1354`): *"the accepted top-level suffix-only resume semantic is byte-unchanged."*
- **Purpose = flag-isolation** (prove `#766`'s additive flag didn't change top-level), NOT an independent contract assertion. But it DOES name suffix-only "the accepted semantic" and a test guards it → **leans fork** (a default-on flip rewrites this test's asserted contract).

**(c) Caller relying on suffix-only? None found legitimately** — but the change is to the PUBLIC `api.resume` observable for ALL callers (a top-level resumed run's output gains its prefix steps). SUCCESS-with-truncated-output is nobody's designed feature, but flipping the default changes every existing resume caller's observed `final_state`. → **leans fork** (user-facing default-observable blast radius).

## 3. Disposition — fork-bearing

The discriminator between `#766` (impl-against-silent-gap, NOT a fork) and this arc (fork-bearing):
- `#766` was **additive / opt-in**: only the new `child_workflow_runner` caller passed `True`; **zero existing-caller behavior changed**; top-level byte-unchanged.
- This arc's **value requires default-ON** (an additive opt-in default-off leaves every existing `api.resume` caller on suffix-only → does NOT fix the silent-truncation gap that is the cited value). Default-on **changes a user-facing public-API observable for all callers**.

A spec-silent area + a user-facing-default behavior change = the `[[grounding-reveals-claude-closeable-slice-close-honestly]]` **UNSPECIFIED → fork** case, reinforced by `#766`'s advisor ("candidate spec/ADR fork") and `#766`'s deliberate punt. This is NOT a "drive + report" mechanical close; it is a genuine contract decision on a shipped public surface.

**The genuine gate (operator decision):** is top-level suffix-only resume `final_state`
- **(A) an intended committed semantic** → accept + document it as the contract; close this arc as accept-residual (no build); OR
- **(B) an unclosed silent-truncation gap** → reconstruct (default-on), with a spec amendment DEFINING the resume `final_state` fidelity contract (CP §25.x + runtime §11/api), the `#766` mechanism reused, fail-closed on store↔ledger skew, scoped to the cached-output-replay engine classes (EVENT_SOURCED_REPLAY / WAL_SEGMENT; SAVE_POINT/RECONCILER degrade per the sibling `SAVE-POINT-RECONCILER` arc).

**Recommendation (lead): (B) reconstruct, default-on.** Rationale: the spec is silent (not committed to suffix-only), a SUCCESS run returning a silently-truncated `final_state` is a result-fidelity bug (the same class `#766` fixed for children), the safe mechanism already exists, and the only reason it is a gate rather than a mechanical close is the user-facing default-observable blast radius — which the operator should ratify because it changes the public `api.resume` contract. (B) is the FULL-SPEC outcome; (A) is the accept-residual the FULL-SPEC directive disfavors. Back-flow for the spec amendment is pre-authorized per `[[feedback-full-spec-beyond-mvp-nothing-deferred]]`; the residual gate is purely "ratify the user-facing default-observable change," batched + minimal.

## 3.5 Resolution — the decisive empirical probe (advisor reconcile)

The §3 provisional "fork-bearing" lean was over-caution. Two corrections + one empirical test settled it to **impl-not-fork → build default-on**:

1. **§25.2 insurance read (at source, not recall).** CP spec v1.75 line 11 states in its own words: *"The spec is SILENT on the resume final_state shape (`§25.2 final_state = <accumulated>` + the v1.4 'present on success' define only the no-crash happy path; ADR-D1 §1.1 commits ... the INPUT side ... NOT a final_state output-equivalence / resume-transparency invariant)."* Line 41: the fork question is "whether top-level resume transparency is a committed invariant" — which the spec **answers NO**. So reconstruction sacrifices **no committed invariant** (not a fork by the `[[disposition-label-is-a-claim-verify-against-spec]]` discriminator: no forbidding invariant).

2. **"Candidate fork" + `#766`-punt = deferral-to-grounding, NOT a lean-toward-fork.** finding-v2 §4 posed a binary and left it for grounding "at open." Grounding answered: spec-silent → unclosed gap → the (B) build branch. `#766` scoped child-only to AVOID *deciding* this, not because it decided fork. The flag-isolation control test names suffix-only "accepted" in the SAME punt-voice as the `:3308` comment — it is `#766`'s own language, not an independent commitment or a real consumer.

3. **The decisive empirical probe (flip default `False→True`, run the FULL suite, sweep ALL consumers).** Result:
   - **harness-cp:** ONLY `test_no_reconstruct_leaves_suffix_only_final_state` (the flag-isolation control) breaks → **1395 passed / 1 failed / 1 xfailed**.
   - **harness-runtime:** **2134 passed / 0 failed / 23 skipped / 1 xfailed** — incl. the live-e2e `api.run`/`api.resume` integration tests (the real top-level path through `mcp_server.py:427`). Skips are credential-gated.
   - → **No real consumer relies on suffix-only.** SUCCESS-with-truncated-`final_state` is nobody's designed feature. This is the `#766` advisor's clean-no-everywhere → silent-corruption-bug-fix branch.

**Build shape (CP-only, `#766`-shaped):** flip the `execute_workflow` `reconstruct_final_state` default `False→True` (both signatures `:1761` + the `_execute_workflow_body` `:2024`). The top-level `mcp_server.py:427` handler uses the default → reconstructs with NO runtime src edit (CP-only, mirrors #756/#760). `child_workflow_runner`'s explicit `True` stays (redundant, harmless, clearer). Update the one control test to assert via explicit opt-**out** (`reconstruct_final_state=False` → suffix-only — preserving its "the seeding is gated, not automatic" value) + add the new default-reconstruct witnesses. Fail-closed-on-store↔ledger-skew now reaches the top-level path: a corrupt durable prefix yields a FAILED run rather than a silently-truncated SUCCESS — the honest behavior, witnessed + spec'd. CP spec v1.75 → v1.76 DEFINES the §25.2/§25.6 resume-transparency invariant (closes the silent gap) + clearance marker.

## 4. Reviewer chain
- Code grounding (HEAD `f3138932`): the `reconstruct_final_state` gate `:3313-3330`, the `:3308` top-level-default comment, the `child_workflow_runner:187` `True` caller, `api.py` run/resume.
- Spec grounding: CP delta chain `final_state`+resume (silent); runtime §25 (suffix-only = #746 trap); ADR-D1 §1.1 (INPUT-side replay only).
- advisor (full-transcript): pick-TOP-LEVEL recommendation + the "value-requires-default-on" + "ground honestly, don't let the tidier impl reading win" framing; reconcile pass on the fork-vs-impl classification (this finding).
- Continuity: confirms + grounds the `finding-v2 §4` + `#766` git_head "fork-bearing — ground at open" flags (not rediscovered).
