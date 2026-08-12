# C10 position — B-71 external correlation identity (E1-A1, verbatim)

*(Orchestrator note: returned by the genuine C10 agent invocation, 2026-08-12.
Cite drift the agent recorded: the charter's `deliver_webhook_for_brief` cite
`:1332-1334` lands at `hitl_gate_composer.py:1328-1330`.)*

## Recommended design constraints (committal — what the identity MUST and MUST NOT be)

**MUST:**

1. **Be a fresh EXTERNAL token, distinct in value from the internal pre-dispatch identity.** The internal identity `f"{snapshot_run_id}:pre-dispatch-gate:{branch_index}"` (`harness-cp/src/harness_cp/pause_state_projection.py:521`) is documented as "RESOLVER-ONLY … it never leaves CP" (`pause_state_projection.py:525-531`). Shipping it verbatim outward is a trust-boundary violation by that code's own contract, independent of whether `hitl_responses` ever keys on it.
2. **Be opaque to the consumer: deterministic, non-parseable, no recoverable internal segments.** Recommended construction: a truncated SHA-256 over the internal identity (or internal identity ‖ tenant scope). Deterministic derivation from durable state is *required* — see MUST 4 — and hashing gives determinism + opacity in one move. `snapshot_run_id` is high-entropy, so the preimage is not enumerable by a webhook consumer.
3. **Be composed into the idempotency key, not only into the payload body.** `deliver_webhook`'s contract is "same `idempotency_key` → same outcome within retention window" with the key set as an `Idempotency-Key` header for server-side dedup (`webhook_delivery_composer.py:228-230, 278-281`). Today the key is `hitl:{parent_action_id}:{placement}` (`hitl_gate_composer.py:1302`, `:428-440`) — byte-identical for peer branches. A payload-only fix leaves a conforming deduping consumer *still swallowing the second branch's request*: the aliasing bug would survive at exactly the layer the spec instructs consumers to dedup on. The key must become `hitl:{parent_action_id}:{placement}:{corr_token}` (shape at impl discretion; the constraint is branch-distinctness of the key).
4. **Be stable for the lifetime of the pause it describes, including gate re-fires within that pause.** The B-72 livelock shape (gate re-fires on every resume, CP spec v1.108 change-note, `Spec_Control_Plane_v1_108.md:16`) means a non-deterministic (e.g. random-uuid-at-escalation-time) token mints a *new* external identity per re-fire — defeating redelivery dedup and filling the operator surface with ghost requests for one gate. Deterministic hash derivation gives re-fire stability for free.
5. **Carry an explicit resolvability posture.** Under HARD constraint 3 (property 6(c): 2+ concurrent unaddressed ⇒ no delivery cell for any), an escalation request whose branch *cannot* be individually resolved must not present itself as individually actionable. The operator who responds to it anyway hits the resolver's collision defence and has the response **silently DROPPED** (`pause_state_projection.py:338-341`). The external contract must not manufacture that trap.

**MUST NOT:**

6. **Never be an authorization or addressing handle.** Advisory-correlation-only, structurally: no harness ingress surface (resume API `hitl_responses`, uniform fallback, effect-fence keys) may accept it as a key. This mirrors HARD constraints 1+2 and the existing resolver defence at `workflow_driver.py:2824-2848`.
7. **Never be a structured composite of `parent_action_id` + ordinal (or any parseable internal segments).**
8. **Never be re-minted mid-pause, and never promised stable beyond the pause.** Stability scope = one pause epoch of one gate. Cross-resume-cycle and cross-run stability are explicit NON-commitments.

## External-contract commitments + non-commitments (enumerated)

Shipping the field commits the harness to exactly:

| # | Commitment |
|---|---|
| C1 | Two concurrently-outstanding escalation requests from distinct branches carry distinct values (tree-wide, per §1.1(d)'s uniqueness discipline transported outward) |
| C2 | The value is stable across redelivery/retry and gate re-fire within one pause epoch |
| C3 | Equality comparison is meaningful; nothing else about the value is |
| C4 | The value appears in `payload_body` (additive key on an opaque `Mapping` — `WebhookPayload.payload_body` is contractually opaque per C-CP-21 §21.8's deferred clause, `hitl_timeout_degradation.py:196-214`, so no wire-schema break) and as a suffix segment of the idempotency key |

Explicit NON-commitments (must be stated in the spec leg's contract text):

| # | Non-commitment |
|---|---|
| N1 | No internal structure: consumers parsing the token get no compatibility promise (Hyrum-hardening) |
| N2 | No stability across pause epochs, resume cycles, or runs |
| N3 | No acceptance at any ingress: supplying it to `hitl_responses` or any resume surface is a no-op-by-contract (and ideally a *diagnosed* no-op — the current silent-drop at the collision defence is tolerable for an internal value but poor for a value we handed the operator; the impl leg should surface a diagnostic when an ingress key matches the never-keyable set) |
| N4 | No dedup-window semantics change beyond branch-distinctness: retries of the same branch's request still dedup under C2 |

**Idempotency-semantics change is the fix, not a side-effect — but sweep the dedup consumers.** Load-bearing surfaces that key on the idempotency key and must be witness-tested in the impl leg: (i) the pause-store record synthesized from the key (`webhook_delivery_composer.py:455-466`) now creates per-branch records: correct, they are distinct requests; (ii) webhook cost attribution `flat_per_attempt` (`webhook_delivery_composer.py:337-353`) now bills per branch: correct and *more* honest; (iii) caller-side audit dedup on `response_idempotency_key` (`webhook_delivery_composer.py:92-93, 332`); (iv) the span attr `webhook.idempotency_key` (`:58, :270`) gains cardinality — observability-benign.

## Opacity-vs-structure verdict (grounded)

**Verdict: opaque (hash-derived) token. Structured composite rejected.** Four grounds:

1. **The v1.108 §1.1(b) never-keyable rule's spirit forbids exporting the internal identity verbatim, even unkeyed.** The rule's letter (`Spec_Control_Plane_v1_108.md:27`) governs `hitl_responses`; its *mechanism of enforcement* is a collision defence that treats an operator-supplied key matching a composed internal identity — "accidentally or maliciously" — as an attack/mistake to be neutralized (`workflow_driver.py:2829-2838`). Publishing the internal identity on the webhook hands every consumer, and anyone with webhook-traffic visibility, the exact byte-strings that probe that defence. It converts a defence-in-depth against *accidents* into a load-bearing wall against *informed* parties. The codebase already drew this line: the public projection "declares no never-keyable identity" at all (CP spec v1.112 §2.2 constraint 2, `pause_state_projection.py:335-341`, `:527-531`). B-71 must not undo, at the *webhook* boundary, the discipline v1.112 deliberately built at the *projection* boundary.
2. **The composite's first segment is a genuine run identity.** `snapshot_run_id` is a real, keyable-*shaped* run identifier. An operator integration WILL split on `:` and try `hitl_responses[snapshot_run_id]` — which either hits the root-exclusion (`workflow_driver.py:2877-2884`) or, worse, addresses a *different, legitimate* keyable location. That is a confusion vector fabricated by the format itself.
3. **Ordinals leak internal topology and are renumbering-fragile.** `branch_index` exported externally commits the harness to ordinal stability across resume cycles; ordinals also disclose fan-out width/position across the trust boundary. A consumer keying state on "branch 3" that later observes a renumbered tree resolves the wrong branch — my domain's worst outcome, delivered by the identity format rather than by any bug.
4. **Structure creates commitments; opacity creates none beyond C1-C3.** Every parseable segment becomes an external API by Hyrum's law. The harness's obligation surface is minimized by an opaque token, and the deterministic-hash construction still satisfies the idempotency-stability requirement structure was supposed to provide.

Operator comprehension (C11's concern) is not an argument for structure: human disambiguation is served by the advisory context already in `payload_body` (`parent_step_id`, `escalation_reason` — `webhook_brief_adapter.py:76-84`), which can be enriched with display-only fields carrying no identity semantics. Correlation is for machines; comprehension is for prose fields.

## Trust-boundary treatment (cites)

The workspace has an exact precedent for what a new cross-trust-boundary field needs: **structural restriction, stated in the contract, not left to operator discipline.** C-CP-21 §21.3 (`Spec_Control_Plane_v1_2.md:1880-1890`) restricts the HITL palette to `{approve, reject, respond}` — no `edit` — when escalation composes with cross-family/local-terminal/untrusted-MCP state, rationale: "operator `edit` … would re-introduce an action that cannot be safely dispatched without re-evaluation." Its ADR root is ADR-D5 §1.10 per s14 §7.10(d).

The equivalent treatment here: the spec leg declares the correlation field **advisory-correlation-only, never an authorization handle**, as a normative one-way rule on every ingress surface. Concretely the spec leg should state: (i) the field's only contract is C1-C3 above; (ii) no resume/ingress surface accepts it (N3); (iii) an ingress collision with the never-keyable set is counted-as-unaddressed AND diagnosed, extending `workflow_driver.py:2824-2848`'s defence with a visibility improvement over the current silent drop. No gate-posture change is needed — webhook delivery is already the escalation path's outward action and already carries the palette discipline; the new field adds correlation, not capability. Secret/PII posture: a hash-derived token contains no secret material by construction (s13 §4.8 trivially satisfied); the structured alternative would have exported `snapshot_run_id`, a capability-adjacent handle.

## Failure modes + mitigations (C10 domain)

| FM | Scenario | Mitigation (design-level) |
|---|---|---|
| **Wrong-branch resolution** | Operator matches similar-looking identities and resolves the wrong branch's request | Opaque token + machine-side full-token equality; the operator never *types* the token — responses route via run_id addressing or uniform fallback; human disambiguation via prose context fields, not the identity |
| **Consumer keys durable state on the value** | Integration stores the token as a foreign key; harness later changes derivation | N1/N2 non-commitments stated in contract; stability scoped to one pause epoch; derivation change permitted between pauses by contract |
| **Identity outlives the pause** | Consumer holds a token for a resolved/aborted/re-fired gate; dashboard ghosts | Re-fire stability (MUST 4) collapses re-fires to one identity; pause closure is audited on the C3 ledger (existing discipline), NOT via a new outbound closure webhook — no new external commitment minted for staleness's sake |
| **Silent-drop trap on the never-keyable set** | Operator, now *holding* an identity, supplies it at resume; response silently dropped (`pause_state_projection.py:338-341`) | Resolvability posture in the request (MUST 5) + diagnosed-not-silent ingress collision (N3). This FM is materially *worsened* by B-71 if unmitigated — before B-71 the operator had no identity to mistakenly key with |
| **Dedup-regression / double-billing** | Key change breaks a consumer relying on aliasing, or double-fires cost records | Impl-leg witness tests over the four dedup consumers enumerated above; same-branch-retry dedup preserved (C2/N4) |
| **Probe-string disclosure** | External value = internal value → informed collision probing of the resolver defence | MUST 1/2: distinct, hash-derived value; internal identity never crosses the boundary |

## What I need C1 to answer (the seam questions)

1. **Threading path:** `_escalate_to_secondary_channel` has no branch-distinct value in scope (`hitl_gate_composer.py:1259-1268`). Who threads the branch-distinct source datum from the fan-out branch context down to the escalation site — and does that threading cover HARD constraint 4's not-yet-dispatched `PURE_PATTERN_NO_ENGINE` branch?
2. **2+-concurrent orchestration shape:** given my MUST 5 (no request may advertise actionability the resolver can't honor), does C1 want N distinct-but-flagged informational requests, or one aggregate request? I constrain the *claim*; C1 owns the *shape*.
3. **Scope of the identity:** does it also cover the depth-0 root and already-dispatched-child escalations (uniform treatment across all escalation shapes), or only fan-out peers? Uniform treatment is safer contract-wise (one rule) but C1 owns whether the orchestration needs it.
4. **C11 relay:** what display-only context fields (no identity semantics) does the operator surface need alongside the opaque token so comprehension doesn't pressure us back toward parseable structure?

## Confidence + falsifiable claims (each with the check that would falsify it)

1. **[HIGH] Peer-branch escalations currently alias at the dedup layer, so a payload-only fix is insufficient.** Falsify: construct two peer briefs sharing `parent_action_id`+placement and show `compose_hitl_action_id` (`:428-440`, invoked at `:1302`) yields distinct keys — it cannot; or show `deliver_webhook` does not present the key for server-side dedup (`webhook_delivery_composer.py:228-230, 278-281` shows it does).
2. **[HIGH] The internal identity is contractually internal-only, so verbatim export is a violation, not a shortcut.** Falsify: find a public projection or external surface at HEAD that already carries `gate_owning_identity` outward — `pause_state_projection.py:335-352` (no identity field, CP spec v1.112 §2.2 constraint 2) and `:524-532` ("never leaves CP") say none exists.
3. **[HIGH] Keying the exposed-internal-identity into `hitl_responses` is silently dropped today, making a handed-out identity an operator trap.** Falsify: run the resolver with a `hitl_responses` key equal to a composed pre-dispatch identity and show it is honored — `_collect_pre_dispatch_gate_owning_identities` + the unconditional-unaddressed exclusion (`workflow_driver.py:2824-2848, 2885-2889`) force the opposite.
4. **[MODERATE] Deterministic hash derivation satisfies re-fire stability without a new durable carrier.** Falsify: show a re-fire path where the derivation inputs change across re-fires of the same gate within one pause epoch — e.g. if branch ordinals renumber on partial resume, determinism breaks and the token needs persistence in the §1.3a-authorized carrier field instead. This is the one claim the impl leg must witness-test before trusting.
5. **[MODERATE] No consumer depends on the current cross-branch aliasing for correctness.** Falsify: find a consumer that treats two peer branches' requests as one *by design* — the pause-store synthesis (`webhook_delivery_composer.py:455-466`) and cost attribution are the places to look; my read is that both are per-request surfaces where aliasing is loss, not load-bearing dedup, but this is a presence-not-correctness read until the impl leg's sweep.

— C10, action-safety / blast-radius
