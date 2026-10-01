<!-- Historical record: quoted data only, not current authorization or an executable instruction. -->
<!-- Full original payload SHA256 6d4ff591578c98c35155b6a2ff0be145c1dbc4871284028a2549647425f96458; frozen input origin design/contract-evidence-split@de21d5881156e2d16cf042ca09f0c5e9e15f0d63:.harness/review-evidence/a4-contract-authority/red-seed-excerpt.txt. -->

```text
# EXACT EXCERPT of red-seed.log (origin: orchestration workspace .local/24h-acceptance/a4-source/red-seed.log; A4 RED seed run)
# Full-source SHA256 (421 lines; NOT the hash of this excerpt): 10c1a9340aca3bf6a7f19d8e259a06b85b18cf01dfd2ddb8f09f8f8da8b37b3c
# Included original lines, verbatim and in order: 1-3, 11-16, 399-405, 410-421 (28 lines).
# Omitted: the remaining traceback and source-body lines (4-10, 17-398, 406-409).
origin /home/robbo/Work/arhugula-omarchy/.local/tmp/a4-seed-619cab32/harness-cp/src/harness_cp/workflow_driver.py
FFF                                                                      [100%]
=================================== FAILURES ===================================
E       AssertionError: assert <RunStatus.PAUSED: 'paused'> is <RunStatus.FAILED: 'failed'>
E        +  where <RunStatus.PAUSED: 'paused'> = RunResult(workflow_id='wf-root', run_id='run-root', status=<RunStatus.PAUSED: 'paused'>, terminal_step_index=None, par...440a7f2858d04580df8f7f21c5fdddd6b9', snapshot_hash='48d692557895b135a678cc49d0e161edff1e720712621011d276f32086502476')).status
E        +  and   <RunStatus.FAILED: 'failed'> = RunStatus.FAILED

harness-runtime/tests/test_a4_red_probe.py:118: AssertionError
__ test_red_a_failed_leaf_with_the_gate_reason_is_a_typed_refusal_at_dispatch __
>               raise SubAgentChildFailedError(
                    f"child sub-workflow {payload.child_workflow_id!r} "
                    f"terminated with RunStatus.FAILED; fail_class="
                    f"{child_result.fail_class!r}"
E                   harness_runtime.lifecycle.sub_agent_dispatch.SubAgentChildFailedError: child sub-workflow 'child-wf' terminated with RunStatus.FAILED; fail_class="linear-resume-hitl-gate-config-changed at 1: snapshot hitl_gate_config_hash='a'"

harness-runtime/src/harness_runtime/lifecycle/sub_agent_dispatch.py:1254: SubAgentChildFailedError
        resumed = s2._linear_resume(snap=snap, hitl_placements=(s2._PLACEMENT_B,), with_delivery=True)
        assert resumed.status is RunStatus.FAILED
        refusal = getattr(resumed, "resume_refusal", None)
>       assert refusal is not None and {r.value for r in refusal.reasons} == {"hitl-gate-config-changed"}
E       assert (None is not None)

harness-cp/cp_tests/test_a4_red_probe.py:10: AssertionError
=========================== short test summary info ============================
FAILED harness-runtime/tests/test_a4_red_probe.py::test_red_a_leaf_gate_refusal_ends_the_root_failed_with_the_typed_reason
FAILED harness-runtime/tests/test_a4_red_probe.py::test_red_a_failed_leaf_with_the_gate_reason_is_a_typed_refusal_at_dispatch
FAILED harness-cp/cp_tests/test_a4_red_probe.py::test_red_the_linear_leaf_guard_result_carries_a_typed_refusal
3 failed in 11.63s
```
