# B-145 grounding — GAP 1 is an intra-spec self-duplicate; the row splits

*Filed 2026-08-11 by the loop orchestrator (close-out step 1+2+3 discharge; all
cites re-read at HEAD `5f2852cf` this session).*

## The step-1 re-ground (offsets unchanged at HEAD)

`Spec_Harness_Runtime_v1.md` §14.6 step bullets `:4227-4230` and §14.9 bullets
`:5684-5687` stand as the register row describes: five `retry.terminal` values
per path (success / fail-fast / retry / max-attempts / escalate), plus
`retry.backoff_ms` at the retry bullets (:4229, :5685) and
`retry.cause_class = "{class_name}"` at the fail-fast bullets (:4228, :5686).

## The step-3 check — and its answer

The close-out ordered: *"CHECK FIRST whether that duplicates retry.fail_class …
the honest disposition may be a spec correction retiring the redundant
attribute rather than an emission."* The check lands one key over from where
the row guessed, and hits **both** GAP-1 keys:

- **The SAME spec sections already mandate the same values under the §3.5
  names.** `:4225` (§14.6 inner-span bullet) and `:5682` (§14.9 inner-span
  bullet) declare the inner span carries the canonical C-CP-03 §3.5
  6-attribute schema — explicitly including **`retry.delay_ms` (integer;
  jittered delay per full-jitter backoff)** and **`retry.cause_attribution`
  (string; open-set enum from the C5 cause_attribution catalog)**. The CP spec
  declares the same rows at `Spec_Control_Plane_v1_116.md:2715-2716`.
- **The producers conform to the §3.5 names.** Tool path
  (`harness-runtime/src/harness_runtime/lifecycle/retry_breaker_tool.py`):
  `retry.delay_ms` at :245/:263/:277/:291/:301 (the jittered backoff in ms on
  the retry branch, 0 elsewhere) and `retry.cause_attribution =
  type(exc).__name__` at :292 on the fail-fast branch — exactly the
  "{class_name}" the `retry.cause_class` bullet asks for. Dispatch path
  mirrors (`retry_breaker_fallback.py` staircase region ~:1364-1431).

So `retry.backoff_ms` and `retry.cause_class` are **informal step-bullet
aliases for values the same steps' own schema declaration already carries as
`retry.delay_ms` and `retry.cause_attribution`** — intra-spec prose drift, not
missing derivations. Wiring them would put duplicate keys on the wire for
every retry attempt.

## The split disposition

- **GAP 1 → spec leg (design-substrate; route per X-AL-3 before building).**
  The honest fix is a Runtime spec correction aligning the four step-bullet
  mentions (:4228, :4229, :5685, :5686) to the §3.5 names (`retry.delay_ms`,
  `retry.cause_attribution`) — or an explicit alias-retirement note — plus the
  paired `RETRY_WIRE_REGISTER` re-disposition (the two `emitted=False` rows at
  `harness-cp/src/harness_cp/retry_fallback_namespace.py:288-301` stop being
  conformance gaps and become retired aliases; the pinning test
  `test_unemitted_keys_are_exactly_the_two_b145_registers` changes in the same
  commit). NOT buildable as silent impl; needs the spec delta + clearance
  marker per §4.4/§4.5.
- **GAP 2 → impl repair (Phase 7; buildable now, independent of GAP 1).**
  Value-level conformance with no naming question: (a) tool path — split the
  collapsed else at `retry_breaker_tool.py:274-288` so staircase escalation
  past STAGE_2 stamps `retry.terminal="escalate"` and only genuine
  `max_attempts` exhaustion stamps `"max-attempts"` (the B-127/B-131
  misattribution lesson is binding: pass the disposition through, per-branch
  witnesses); (b) dispatch path — wire all five terminal values at the
  `retry_breaker_fallback.py` staircase region (currently zero of five; only
  the non-mandated `audit-signing-fail-closed` at :1294).

## Register effect

`B-145` stays `registered_finding` with this split recorded in its
build-state; the next closer picks up GAP 2 as a self-contained impl arc and
GAP 1 as a spec-leg arc (bundled-absorption with back-flow doc, or two PRs).
The step-1 sweep discipline (emission-position, not bare literal) was honored:
producer sites were read directly; the register declaration home was excluded.
