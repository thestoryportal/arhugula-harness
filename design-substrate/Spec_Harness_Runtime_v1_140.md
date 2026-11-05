# Spec: Harness Runtime — v1.140 (delta over v1.138)

*Delta-only file. One contract amended: C-RT-17 §14.7.2 sub-agent dispatch composer, step 1 (payload
parse), now resolves the effective brief from CP v1.130 §25.11.1.4(4) `lead_brief`. Every other
v1.138 and earlier term remains in force. Proposed v1.139 (PR #1705, skill content at hook 2) is not
a head and is not amended. The two deltas touch disjoint contracts.*

**Status: PROPOSED — contract text for independent review and integration-lead ratification. Not
cleared; no source, CI, landing or installed claim.**

**Filed:** 2026-11-05

**Authority:** paired with `Spec_Control_Plane_v1_130.md` (LIT `arhugula-harness-trial-193.qrf`
`cmt-9e26c9ad`).

**Predecessor:** `Spec_Harness_Runtime_v1_138.md` (head). **Paired CP delta:**
`Spec_Control_Plane_v1_130.md`.

## §0 Change-note (v1.138 → v1.140)

| Site | Before | After |
|---|---|---|
| C-RT-17 §14.7.2 step 1 | `step.step_payload → SubAgentDispatchPayload`; every later step reads `payload.brief` | After the parse, `payload` is rebound once to the effective payload, whose brief is `step_context.lead_brief` when that is set. Every later step reads only the effective payload |

## §1 Amended §14.7.2 step 1 — effective brief

1. **One resolution.** Immediately after `SubAgentDispatchPayload.model_validate`, the composer binds
   `payload = payload.model_copy(update={"brief": step_context.lead_brief})` when
   `step_context.lead_brief` is not `None`, and keeps the parsed payload otherwise. This is the only
   site that reads `step_context.lead_brief`. No later site reads the declared brief.
2. **Readers.** At harness `7c8f3af9` the later readers in
   `harness_runtime/lifecycle/sub_agent_dispatch.py` are the handoff context composition (lines
   539-540), the dispatch `response_hash` (line 749) and the gate-level descent `sub_agent_brief`
   (line 933). All of them consume the effective payload, so the child's handoff, descent and audit
   join key agree on one brief.
3. **Unchanged.** `SubAgentDispatchPayload` keeps `brief` required. The declared brief applies to
   every `DECLARED_POOL` run. Under `LEAD_PLAN`, CP v1.130 §25.11.1.3(2) gives every sub-agent
   worker a lead brief, so the declared brief reaches no reader. Child identity (`child_workflow_id`), manifest and steps come only from the
   declared payload.

## §2 Witnesses

| ID | Behavior | Mutant it kills |
|---|---|---|
| RW1 | A worker context with `lead_brief` set: the handoff context objective, `response_hash` and descent `sub_agent_brief` all derive from the lead brief (shared with CP v1.130 W3) | Any one reader left on the declared brief |
| RW2 | `lead_brief=None`: all three readers derive from the declared brief, byte-identical to v1.138 behavior | Resolution that drops or rewrites the declared brief |

## §3 Status

PROPOSED. Clears only together with CP v1.130, by independent review GREEN of the exact head and
integration-lead ratification, followed by a clearance marker and an artifact-heads refresh. Source
landing, CI and installed acceptance remain owed.
