# C11 reaction — B-71 (E1-A2, verbatim)

*(Orchestrator note: returned by the genuine C11 agent invocation, 2026-08-12.)*

## Tensions surfaced

**T1 — C10's "comprehension is for prose fields" is circular in exactly the B-71 trigger case.** The B-71 premise is that peer-branch briefs are **byte-identical** — every prose field C10 points to (`escalation_reason` at `webhook_brief_adapter.py:77`, `parent_step_id` at `:78`, `fail_class`/`fail_detail_hash`/`proposed_response_palette` at `:79-83`) is the same string on both peers. Two truncated tokens distinguish the requests to a *machine*; to a *human* reading Slack, `a3f81c…` vs `9e02bd…` distinguishes nothing. The existing prose fields fail, the token fails humanly, and C10's MUST NOT 7 plus his branch_index ban would foreclose the only pre-dispatch-available human-readable discriminators. **Denying all of them re-creates the comprehension half of the bug with extra steps.** The escape is a display-only prose field — which C10's own seam question 4 explicitly invites.

**T2 — C10's MUST 5 indicts a field the payload already ships, and neither primary audited it.** Today's payload *already* advertises actionability: `proposed_response_palette` is projected outward at `webhook_brief_adapter.py:81-83` — approve/edit/reject/respond — on a pre-dispatch request whose response will be **silently dropped** (`pause_state_projection.py:338-341`). The resolvability posture cannot be a new field bolted alongside; it must *qualify the palette that is already there*. Unqualified, it is the exact "manufactured trap" C10's FM 4 names, and it is live at HEAD. The spec leg must bind palette-display to the posture field.

**T3 — C1's snapshot echo is invisible where the operator actually looks; the loop closes one layer short.** The operator never reads internal resume state — the operator-facing surface is the **public projection**, `project_pause_locations` (`pause_state_projection.py:816-827`, CP spec v1.112 §2.1), and the variant that renders a pre-dispatch gate-owning branch — `PreDispatchUniformFallbackOnlyLocation` (`pause_state_projection.py:335-352`) — **deliberately declares no identity field at all** (v1.112 §2.2 constraint 2). Unless the spec leg *also* amends that projection variant to carry the EXTERNAL token (external-token-yes / internal-identity-still-never — different rules), the echo terminates in a struct no operator can see. An echo the operator can't see is no echo.

**T4 — "Which request became actionable" has no carrier in either primary.** When N-1 peers resolve, the last becomes sole unaddressed and the uniform fallback may deliver on next resume (`workflow_driver.py:2851-2898`, esp. `:2891-2897`). No webhook re-fires on that transition. Resolution: (a) the resolvability wording routes the operator to the pause view explicitly; (b) the T3 projection amendment makes that routing usable (match the token); (c) register redelivery-on-posture-change as a follow-on `B-*` under C9's knob — do not absorb here, do not pretend closed.

## The operator-facing field set (designed, committal)

All additions ride `payload_body` (additive keys on the contractually-opaque Mapping per C-CP-21 §21.8; default consumers untouched). Existing five keys (`webhook_brief_adapter.py:76-84`) unchanged.

| Field | Content | Why |
|---|---|---|
| `escalation_instance_id` | The opaque token. Also suffixes the idempotency key. | Machine equality only; matched in the pause view, never typed at an ingress. |
| `branch_context` | **One display-only prose sentence**, minted at `_escalate_to_secondary_channel` from the branch child context, e.g. `"Fan-out branch 4 of step 'collect-reviews' (branch step 'summarize-eu', child workflow 'review-summarizer') — one of several parallel branches of this run."` `None` on the linear path. | The T1 fix. One prose field, not three structured ones, precisely *because of* Hyrum: a sentence is read, not parsed, under an explicit no-format-commitment. Carries the only branch-distinct human-readable data that exist pre-dispatch: the ordinal + the branch's declared step identity. [MEDIUM] on exactly which step-identity members are in composer scope; falsifier: `compose_branch_child_context`, `workflow_driver_types.py:586-648`. |
| `resolvability` | Two-valued string, static at mint: `"addressable"` \| `"held-for-sole-resolution"`. Pre-dispatch gate-owning escalations mint the latter — statically known from placement/branch context; does NOT require live sibling count. | The one structured flag MUST 5 demands. Structured so the default consumer can act with zero code intelligence (render the reply affordance only when `addressable`). The difference between "the trap is documented" and "the trap is disarmed." |
| `resolvability_note` | The verbatim wording below. | Prose for the human who reads only this one message. |

**Deliberately absent:** a structured `branch_index` integer; a live "N outstanding" count (the mint site cannot know it honestly; a stale count in a durable webhook body is worse than none); any new webhook event kind.

## The resolvability-posture wording (drafted verbatim)

For `resolvability: "held-for-sole-resolution"`:

> **This approval request cannot be answered individually yet.** It belongs to a parallel branch that has not been dispatched, so there is no per-request address to reply to. If other approval requests from this same paused run are open, answer those first: this request is honored automatically once it is the **last one remaining** — the response you supply at the next resume then applies to it. A response aimed at this request while others remain open is ignored safely: the run stays paused, nothing is lost or executed, and the resume outcome reports that the response did not attach. To see this run's open requests and which are answerable now, open the run's pause view and match this request's correlation id (`escalation_instance_id`). If this request goes unanswered it expires per the request TTL.

For `resolvability: "addressable"`:

> **This approval request is individually answerable now.** Reply with one of the proposed responses; your response applies to this request only.

Notes: "reports that the response did not attach" presumes the diagnosed-no-op lands where specified below — the wording and the diagnosis are one commitment. The wording names *the pause view*, not a specific CLI incantation ([MEDIUM] — bind to the projection's actual operator surface at the spec leg).

## branch_index adjudication (from the operator's chair)

**C10 wins on the structured field; C1's comprehension need is real and is served in prose.** (1) The ordinal is genuinely load-bearing for a human — in the N-instances-of-one-template fan-out it is the **only** human-distinguishable datum (the internal identity itself discriminates by branch_index, not step_id). So "branch 4" must reach the operator's eyes. (2) But not as a structured field — C10's ground 3 is about machine consumption and is correct there; prose with an explicit no-format-commitment lets a human read it while giving a parser nothing contractual. (3) The disclosure objection is thin at Tier-1 and already conceded locally: `branch_index` is *already operator-visible* on the local pause projection (`PreDispatchUniformFallbackOnlyLocation.branch_index: int`, `pause_state_projection.py:352`). The webhook question is only whether *third parties on the webhook path* may see it; display prose keeps the machine-facing contract ordinal-free while the Tier-1 human — who IS the webhook consumer — still reads it. To C1: the operator reads, in order: (1) the manifest-authored step name (the thing they wrote), (2) the ordinal, (3) `escalation_reason`. `child_workflow_id` is the *least* useful discriminator (sharing it is the collision premise). Lead the `branch_context` sentence with the step name.

## Where the diagnosed no-op must land

1. **The resume outcome itself (primary, mandatory).** Today the observable outcome of a wrongly-keyed response is *the run pauses again with no explanation* (`workflow_driver.py:2885-2894`, docstring `:2877-2889`). The resume path's returned/raised pause outcome must carry a diagnostics collection: every `hitl_responses` key that matched no addressable location, with a reason class (`never-keyable` / `no-such-location` / `not-sole-member-yet`). [MEDIUM] on the exact result shape — impl leg grounds the carrier.
2. **The pause snapshot / public projection (secondary, mandatory).** The diagnosis must persist onto the new snapshot and render through `project_pause_locations`, joined by `escalation_instance_id` per T3. Serves the async-channel operator who inspects hours later.
3. **A report-log line (tertiary, never sufficient alone).** Solo operators do not tail logs.

## Burden verdict

**PASS, zero-config, conditional on three things:** (1) the display fields (`branch_context`, `resolvability`, `resolvability_note`) ship by default, not behind a flag; (2) `resolvability` is structured (two values) so suppressing the reply affordance needs no consumer-side intelligence; (3) the diagnosed no-op lands on the resume outcome and pause view, not only in a log. With those, the local-first operator gets branch-distinct, self-explaining requests over the same dumb webhook they already have — the whole ask.

— C11, operator loop / local-first
