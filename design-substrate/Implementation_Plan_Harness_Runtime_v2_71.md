# Implementation Plan: Harness Runtime — v2.71 (delta over cleared v2.70)

**Status: PROPOSED — implements Runtime spec v1.144 and CP spec v1.132, whose contract the
integration lead ratified at LIT `arhugula-harness-trial-193` `cmt-1802376e-01d6-43d6-96dc-928e87271e38`.
Review rides the T03 frozen candidate. Not cleared.** Plan v2.66 (A5, U-RT-158) stays separately
PROPOSED and deferred; this unit does not depend on it. An integration collision check of the
v1.144/v1.132/v2.71 numbers and the U-RT-162 unit ID is owed at landing.

## U-RT-162 — operator approval collection at both exposed ingresses (B-315, P2 T03)

**Source:** `harness-runtime/src/harness_runtime/api.py` (`operator=` on `api.run`;
`operator_decision=` on `api.resume`; `operator_resume_context` inside `admit_root_resume`);
`cli/app.py` (TTY reader off the event loop, shared grammar, `--daemon` `elicitation_callback`,
`resume --hitl-response` flags); `lifecycle/mcp_backed_ask_user_question_surface.py`;
`lifecycle/ask_user_question_surface.py`; `lifecycle/hitl_gate_composer.py`;
`lifecycle/mcp_server.py` (`resume_workflow(..., operator_decision=...)`);
`harness-cp/src/harness_cp/hitl_placement.py`; `harness-cp/src/harness_cp/pause_resume_protocol_types.py`.

**Acceptance criteria:** the literal assertions 1–17 of the fork record
`.harness/class_1_fork_operator_approval_collection.md` at SHA256
`01adf206f582baeb2aedf72bb1f65c9aa9ac5a1b317257a34aec9ad9155f9ca2`, each run through the public
ingress the assertion names, with the fixture workflow whose gated step writes one marker file.

**Out of scope:** child-workflow gates, A4's inherited-gate refusal, installed acceptance and live
daemon exposure (held by Runtime v1.137 Rule B7 item 4 as for U-RT-161).
