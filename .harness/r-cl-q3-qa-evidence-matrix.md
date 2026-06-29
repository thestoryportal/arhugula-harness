# R-CL-Q3 QA Evidence Matrix

Status: evidence for `.harness/audit/Closure_Gate_v1.md` G2.3.

## Summary

| Predicate | Value |
| --- | ---: |
| Contracts with test proof | 123/123 |
| Contracts missing test proof | 0 |
| CXA seams wired | 31/31 |
| CXA seams missing endpoint | 0 |

## Product Probes

| Tier | Probe | Evidence |
| --- | --- | --- |
| In-process | Track B runtime flow | `harness-runtime/tests/integration/test_track_b_e2e.py` |
| Local API/tool | R100 AC2 tool-step E2E | `harness-runtime/tests/integration/test_r100_ac2_tool_step_e2e.py` |
| Live substrate | Environment-gated smoke path | `harness-runtime/tests/integration/test_r_cl_p3_live_multi_tier_e2e.py` |

## Contract Evidence

| Contract | Source carriers | Test proofs | First proof |
| --- | ---: | ---: | --- |
| C-AS-01 | 4 | 3 | `harness-as/tests/test_forced_tier_resolution.py` |
| C-AS-02 | 12 | 7 | `harness-as/tests/test_blast_radius_floor.py` |
| C-AS-03 | 10 | 4 | `harness-as/tests/test_tool_contract.py` |
| C-AS-04 | 5 | 3 | `harness-as/tests/test_mcp_invocation_fail_class.py` |
| C-AS-05 | 3 | 3 | `harness-as/tests/test_secret_fetch.py` |
| C-AS-06 | 6 | 2 | `harness-as/tests/test_secret_allowlist.py` |
| C-AS-07 | 3 | 1 | `harness-as/tests/test_secret_fail_class.py` |
| C-AS-08 | 6 | 3 | `harness-as/tests/test_secret_fetch_audit.py` |
| C-AS-09 | 8 | 5 | `harness-as/tests/test_deployment_matrix.py` |
| C-AS-10 | 8 | 5 | `harness-as/tests/test_mcp_transport_floor.py` |
| C-AS-11 | 7 | 3 | `harness-as/tests/test_sub_agent_sandbox_tier.py` |
| C-AS-12 | 8 | 5 | `harness-as/tests/test_cross_deployment_monotonicity.py` |
| C-AS-13 | 6 | 4 | `harness-as/tests/test_anthropic_graceful_degradation.py` |
| C-AS-14 | 16 | 8 | `harness-as/tests/test_anthropic_attribute_namespaces.py` |
| C-AS-15 | 16 | 9 | `harness-as/tests/test_sandbox_attribute_schema.py` |
| C-AS-16 | 3 | 3 | `harness-as/tests/test_as_substrate_seam_exports.py` |
| C-CP-01 | 15 | 7 | `harness-cp/tests/test_per_role_catalog.py` |
| C-CP-02 | 12 | 6 | `harness-cp/tests/test_embedding_routing.py` |
| C-CP-03 | 14 | 8 | `harness-cp/tests/test_fall_through_procedure.py` |
| C-CP-04 | 8 | 4 | `harness-cp/tests/test_cross_family_fallback_chain.py` |
| C-CP-05 | 10 | 7 | `harness-core/tests/test_u_core_01.py` |
| C-CP-06 | 13 | 4 | `harness-cp/tests/test_workflow_manifest_entry.py` |
| C-CP-07 | 11 | 8 | `harness-core/tests/test_workload_class.py` |
| C-CP-08 | 10 | 5 | `harness-cp/tests/test_f2_substrate_join_discipline.py` |
| C-CP-09 | 7 | 1 | `harness-cp/tests/test_engine_namespace.py` |
| C-CP-10 | 6 | 5 | `harness-cp/tests/test_topology_pattern.py` |
| C-CP-11 | 9 | 6 | `harness-cp/tests/test_per_engine_class_topology_overlay.py` |
| C-CP-12 | 9 | 8 | `harness-cp/tests/test_default_downgrade_rule.py` |
| C-CP-13 | 17 | 5 | `harness-cp/tests/test_brief_authoring_inheritance.py` |
| C-CP-14 | 9 | 5 | `harness-cp/tests/test_concurrent_prompt_cache_warmup.py` |
| C-CP-15 | 4 | 4 | `harness-cp/tests/test_cross_sibling_cryptographic_shape.py` |
| C-CP-16 | 14 | 10 | `harness-cp/tests/test_hitl_response_palette.py` |
| C-CP-17 | 13 | 4 | `harness-cp/tests/test_hitl_as_tool_call_rewriting.py` |
| C-CP-18 | 9 | 3 | `harness-cp/tests/test_both_by_tier_overlay.py` |
| C-CP-19 | 16 | 7 | `harness-cp/tests/test_cp_shared_types.py` |
| C-CP-20 | 14 | 5 | `harness-cp/tests/test_audit_hitl_span_namespace.py` |
| C-CP-21 | 24 | 10 | `harness-cp/tests/test_both_by_tier_overlay.py` |
| C-CP-22 | 13 | 9 | `harness-cp/tests/test_material_diff_detection.py` |
| C-CP-23 | 1 | 1 | `harness-cp/tests/test_t_perm_3_composition.py` |
| C-CP-24 | 8 | 6 | `harness-cp/tests/test_cp_cross_axis_composition_manifest.py` |
| C-CP-25 | 20 | 13 | `harness-cp/tests/test_validator_framework.py` |
| C-CP-26 | 4 | 6 | `harness-cp/tests/test_pause_resume_protocol_attempt_resume.py` |
| C-CP-27 | 3 | 3 | `harness-cp/tests/test_mcp_client_namespace_emitter.py` |
| C-CP-28 | 4 | 1 | `harness-runtime/tests/integration/test_u_rt_92_validator_escalation_full_execution_path.py` |
| C-CP-29 | 2 | 1 | `harness-cp/tests/test_per_role_catalog.py` |
| C-CP-49 | 1 | 2 | `harness-runtime/tests/integration/test_u_rt_124_reconciler_engine_recovery_go_live.py` |
| C-CP-50 | 1 | 2 | `harness-runtime/tests/integration/test_u_rt_124_reconciler_engine_recovery_go_live.py` |
| C-IS-01 | 12 | 2 | `harness-is/tests/test_path_class_registry.py` |
| C-IS-02 | 4 | 2 | `harness-is/tests/test_artifact_tier_registry.py` |
| C-IS-03 | 4 | 3 | `harness-is/tests/test_atomic_deploy_event.py` |
| C-IS-04 | 2 | 2 | `harness-is/tests/test_atomic_deploy_event.py` |
| C-IS-05 | 33 | 17 | `harness-as/tests/test_sandbox_event_idempotency.py` |
| C-IS-06 | 26 | 9 | `harness-as/tests/test_secret_outputs_hash.py` |
| C-IS-07 | 13 | 8 | `harness-cp/tests/test_workflow_driver_buffered_append.py` |
| C-IS-08 | 9 | 7 | `harness-is/tests/test_atomic_deploy_event.py` |
| C-IS-09 | 5 | 4 | `harness-is/tests/test_git_tier_sub_role_taxonomy.py` |
| C-IS-10 | 14 | 1 | `harness-is/tests/test_substrate_seam_exports.py` |
| C-IS-11 | 0 | 1 | `tools/test_closure_gate.py` |
| C-IS-13 | 9 | 1 | `harness-od/tests/test_local_first_otlp_collector.py` |
| C-IS-14 | 1 | 1 | `harness-od/tests/test_multi_tenant_trace_separation_and_audit_ledger.py` |
| C-OD-01 | 8 | 3 | `harness-od/tests/test_observability_matrix.py` |
| C-OD-02 | 3 | 1 | `harness-od/tests/test_per_cell_backend_class.py` |
| C-OD-03 | 2 | 1 | `harness-od/tests/test_deferral_envelope.py` |
| C-OD-04 | 16 | 3 | `harness-cp/tests/test_routing_namespace.py` |
| C-OD-05 | 12 | 5 | `harness-od/tests/test_as_source_namespace_verification.py` |
| C-OD-06 | 3 | 1 | `harness-od/tests/test_f3_lifecycle_event_mapping.py` |
| C-OD-07 | 9 | 3 | `harness-cp/tests/test_retry_fallback_namespace.py` |
| C-OD-08 | 3 | 1 | `harness-od/tests/test_namespace_collision_discipline.py` |
| C-OD-09 | 13 | 6 | `harness-od/tests/test_composite_sampler.py` |
| C-OD-10 | 7 | 4 | `harness-od/tests/test_base_rate_set_and_envelope.py` |
| C-OD-11 | 5 | 2 | `harness-od/tests/test_attribute_class_enforcement.py` |
| C-OD-12 | 8 | 3 | `harness-od/tests/test_content_structure_discipline.py` |
| C-OD-13 | 12 | 5 | `harness-od/tests/test_cross_deployment_monotonic_tightening.py` |
| C-OD-14 | 15 | 12 | `harness-od/tests/test_audit_ledger_types.py` |
| C-OD-15 | 12 | 1 | `harness-od/tests/test_cross_family_rollup.py` |
| C-OD-16 | 3 | 2 | `harness-od/tests/test_cost_attribution_dashboard_binding.py` |
| C-OD-17 | 6 | 5 | `harness-od/tests/test_eval_vs_runtime_gate.py` |
| C-OD-18 | 3 | 2 | `harness-od/tests/test_alignment_floor_drift_detection.py` |
| C-OD-19 | 9 | 4 | `harness-od/tests/test_local_first_otlp_collector.py` |
| C-OD-20 | 6 | 3 | `harness-od/tests/test_per_sandbox_tier_otlp_reachability.py` |
| C-OD-21 | 13 | 3 | `harness-od/tests/test_cost_attribution_dashboard_binding.py` |
| C-OD-22 | 5 | 2 | `harness-od/tests/test_bridging_arc_table.py` |
| C-OD-23 | 4 | 1 | `harness-od/tests/test_substrate_seam_exports_aggregate_manifest.py` |
| C-OD-24 | 9 | 6 | `harness-cxa/tests/test_u_cp_72_converter_6_prefix_extension.py` |
| C-OD-26 | 12 | 4 | `harness-runtime/tests/test_lifecycle_cost_attribution_llm_dispatch.py` |
| C-OD-29 | 5 | 2 | `harness-cp/tests/test_workflow_driver_validator_hook.py` |
| C-OD-30 | 4 | 4 | `harness-cp/tests/test_pause_resume_protocol_spans.py` |
| C-OD-34 | 6 | 4 | `harness-od/tests/test_prompt_governance_gradient.py` |
| C-RT-01 | 5 | 1 | `harness-runtime/tests/test_bootstrap_stage.py` |
| C-RT-02 | 26 | 5 | `harness-core/tests/test_u_core_02.py` |
| C-RT-03 | 9 | 5 | `harness-runtime/tests/test_config_collector_config.py` |
| C-RT-04 | 28 | 4 | `harness-runtime/tests/integration/test_cp_is_caller_site_integration.py` |
| C-RT-05 | 6 | 1 | `harness-runtime/tests/test_lifecycle_providers.py` |
| C-RT-06 | 7 | 3 | `harness-runtime/tests/integration/test_cross_surface_emission_suite.py` |
| C-RT-07 | 6 | 1 | `harness-runtime/tests/test_lifecycle_collector_daemon.py` |
| C-RT-08 | 5 | 1 | `harness-runtime/tests/test_api.py` |
| C-RT-09 | 11 | 4 | `harness-runtime/tests/integration/test_r_cc_1_api_resume.py` |
| C-RT-10 | 9 | 2 | `harness-cp/tests/test_workflow_driver_drain.py` |
| C-RT-11 | 7 | 3 | `harness-runtime/tests/test_api.py` |
| C-RT-12 | 7 | 4 | `harness-runtime/tests/test_lifecycle_as_is_wiring.py` |
| C-RT-13 | 5 | 2 | `harness-runtime/tests/test_admin_inspect.py` |
| C-RT-14 | 7 | 2 | `harness-runtime/tests/integration/test_run_smoke.py` |
| C-RT-15 | 13 | 7 | `harness-runtime/tests/integration/test_r300_cross_family_fallback_e2e.py` |
| C-RT-16 | 17 | 9 | `harness-cp/tests/test_per_step_override_evaluator.py` |
| C-RT-17 | 12 | 10 | `harness-cp/tests/test_workflow_driver.py` |
| C-RT-18 | 7 | 7 | `harness-cp/tests/test_hitl_placement.py` |
| C-RT-19 | 11 | 1 | `harness-runtime/tests/test_lifecycle_retry_breaker_tool.py` |
| C-RT-20 | 4 | 2 | `harness-runtime/tests/integration/test_u_rt_98_webhook_delivery_composer_binding_chain.py` |
| C-RT-21 | 7 | 4 | `harness-runtime/tests/test_bootstrap.py` |
| C-RT-22 | 5 | 2 | `harness-runtime/tests/test_bootstrap.py` |
| C-RT-23 | 1 | 1 | `harness-runtime/tests/test_u_rt_83_validator_framework_field_landing.py` |
| C-RT-24 | 9 | 1 | `harness-runtime/tests/integration/test_u_rt_89_pause_resume_full_execution_path.py` |
| C-RT-25 | 2 | 1 | `harness-runtime/tests/integration/test_u_rt_92_validator_escalation_full_execution_path.py` |
| C-RT-26 | 4 | 1 | `harness-runtime/tests/test_types.py` |
| C-RT-27 | 4 | 2 | `harness-runtime/tests/test_lifecycle_skill_activation.py` |
| C-RT-28 | 8 | 4 | `harness-cp/tests/test_workflow_driver.py` |
| C-RT-29 | 3 | 1 | `harness-runtime/tests/test_cli_scaffold.py` |
| C-RT-30 | 2 | 1 | `harness-runtime/tests/integration/test_track_b_e2e.py` |
| C-RT-31 | 11 | 5 | `harness-cp/tests/test_workflow_driver_fanout_pause.py` |
| C-RT-32 | 6 | 1 | `harness-runtime/tests/test_types.py` |
| C-RT-33 | 1 | 1 | `harness-runtime/tests/integration/test_post_join_synthesis_live_e2e.py` |
| C-RT-34 | 9 | 6 | `harness-cp/tests/test_workflow_driver_decentralized_handoff.py` |
| C-RT-35 | 4 | 9 | `harness-cp/tests/test_workflow_driver_fanout_pause.py` |
