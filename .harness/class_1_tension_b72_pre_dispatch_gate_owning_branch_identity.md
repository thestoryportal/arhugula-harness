# Class 1 Tension Record — B-72: CP spec v1.106 §1.2 properties 1/4/5 don't name a pre-dispatch gate-owning branch's identity

**Filed:** 2026-07-25 (`systems-architect` tension-resolution mode, invoked from `roadmap-continue`, `advisor()` unavailable this turn — recommendation grounded directly against verbatim spec text + verbatim code, out-of-family `just codex-review` used as the decorrelated check in advisor's place)
**Class:** 1 (halt-execution; design-phase artifact requires revision)
**Status:** RECOMMENDATION PRODUCED — awaiting `spec-writer` application + `just codex-review` convergence (this record's own author drafts the delta directly, per the established B-39/B-70/B-33 same-arc precedent of the recommending pass also drafting the CONTRACT-altitude text, subject to out-of-family review before merge)
**Surfaced by:** `.harness/class_1_fork_b72_gate_ownership_missing_carrier.md` rounds 6-7 (empirical instrumentation of the real round-3 reproduction test + direct read of `sub_agent_dispatch.py`'s dispatch call site)

---

## 1. The tension, stated precisely

`Spec_Control_Plane_v1_106.md` §1.2 (PRESERVED VERBATIM through v1.107) states three properties governing the HITL delivery mechanism for fan-out branches:

**Property 1 (per-branch-distinct resolution):**
> "For any two DISTINCT concurrently-paused GATE-OWNING branches ... the mechanism MUST deliver each gate-owning branch its OWN `hitl_response_for(child_run_id)` resolution (keyed by the paused child's own `run_id`, not `branch_path`...)"

**Property 4 (multi-child fallback-safety, Safety clause):**
> "For a given resume cycle, let the 'unaddressed gate-owning set' be every gate-owning branch paused this cycle whose own `child_run_id` is NOT a key in `hitl_responses` ... The uniform `hitl_response` fallback MAY resolve a gate-owning branch's `hitl_response_for(child_run_id)` call ONLY when that branch is the SOLE member of the unaddressed gate-owning set this cycle."

**Property 5 (gate-owning vs. container definitional split):**
> "Transitively-paused container/ancestor branches are not gate-owning ... it never itself dispatched into a HITL gate, never itself needs a `hitl_responses` key, and MUST always be traversable..."

**The tension:** properties 1 and 4 are written entirely in terms of `child_run_id` as the identifying key for a gate-owning branch — both explicitly say "whose own `child_run_id`" / "keyed by the paused child's own `run_id`." Property 5's OWN definitional test for "gate-owning" is "it [did] dispatch into its own HITL gate" — a test that says nothing about whether a CHILD RUN exists yet. Empirically confirmed (B-72 rounds 3/6/7, `.harness/class_1_fork_b72_gate_ownership_missing_carrier.md`): a `SUB_AGENT_DISPATCH` branch's own `SUB_AGENT_BOUNDARY` gate can fire and pause the run BEFORE `RuntimeSubAgentDispatcher.dispatch()` / `_dispatch_inner` ever runs — i.e., before any child run, and therefore any `child_run_id`, exists. Per property 5's own test, this branch IS gate-owning (it dispatched into its own gate — that's how it paused). But properties 1 and 4's vocabulary (`child_run_id`) cannot describe it, because the thing they key on doesn't exist yet. Neither property's text contemplates this case; it is not addressed, not excluded, not mentioned.

Round 7 additionally confirmed this is not a corner case reachable only under contrived conditions: `compose_child_run_id_seed` (`sub_agent_dispatch.py:363-395`) — the existing deterministic pre-dispatch identity-minting mechanism — is gated on `subagent_child_recoverable`, which excludes `PURE_PATTERN_NO_ENGINE`, the exact engine class the B-72 reproduction (and plausibly many real `SUB_AGENT_DISPATCH` branches with no durable per-step engine) uses. For that engine class, no deterministic seed exists at all — a fresh `uuid` is minted only at the moment of actual dispatch.

## 2. Authority-chain placement

No artifact senior to CP spec v1.106/v1.107 §1.2 speaks to `child_run_id`-based HITL addressing at all — ADR-D5 v1.5 (cross-deployment monotonicity + HITL palette) governs the 4-response palette and placement taxonomy at a much higher level of abstraction and does not specify per-branch addressing keys. This is not a spec-vs-ADR or spec-vs-plan divergence; it is an **internal coherence gap within CP spec v1.106 §1.2 itself** — property 5's own definitional test names a category (pre-dispatch gate-owning) that properties 1 and 4's own chosen vocabulary cannot express. Per `CLAUDE.md` §4.3's Class 1 routing table, an under-specified spec contract routes to Phase 5 spec revision-pass — the CP spec.

## 3. Five-axis + probabilistic-deterministic analysis

- **Control plane** (primary axis). Topology (`PARALLELIZATION`/`ORCHESTRATOR_WORKERS`), HITL placement, sub-agent dispatch sequencing — squarely CP.
- **Information substrate** (secondary). Whatever carrier records this identity lives on `PeerFanOutResumeState`/`FanOutResumeState` — CP-owned pause/resume carrier types (C-CP-25/26), not IS-owned state-ledger surface.
- **Deterministic-layer placement.** The fix is a carrier + a counting rule — squarely deterministic, not an LLM judgment call. No probabilistic/deterministic boundary blur risk.
- **Decision class: Derivative (D), not Foundational.** This composes onto the ALREADY-COMMITTED B-39 HITL delivery mechanism (property 1-5, cleared at v1.106) to cover a case that mechanism's own authors did not originally contemplate. It does not touch any F-ADR, does not widen any existing carrier's PUBLIC shape (property 1's `hitl_responses` key stays exactly as fixed), and does not reopen the ADR-D5 HITL palette decision.

## 4. Resolution recommendation

**Property 4's Safety clause is the ONLY place that structurally needs a gate-owning branch's identity, and it needs it for exactly two purposes: (i) internal counting toward "unaddressed gate-owning set" membership, and (ii) the SOLE-member comparison.** Neither purpose requires the identity to be externally addressable or `run_id`-shaped — that requirement belongs to property 1, and property 1 only applies "for any two DISTINCT concurrently-paused GATE-OWNING branches" needing DISTINCT, KEYED resolutions.

This decomposes the gap into two independently-satisfiable pieces:

1. **A pre-dispatch gate-owning branch must be countable in property 4's Safety-clause "unaddressed gate-owning set,"** using an identity that is internal-only — never placed in `hitl_responses`, never required to be `run_id`-shaped, never required to be externally knowable to an operator. This alone is sufficient to fix the B-72 round-3 reproduction (a single, sole gate-owning branch): once correctly counted, the uniform `hitl_response` fallback already applies per property 4's existing text — no keying required, no `B-71` dependency, no engine-recoverability dependency.
2. **A pre-dispatch gate-owning branch cannot satisfy property 1's per-branch-distinct KEYED resolution** when 2+ gate-owning branches (at least one pre-dispatch) are concurrently unaddressed — no externally-knowable, `run_id`-shaped identity exists before dispatch (round 7: true even for a recoverable-engine child, absent a further extension, since the operator has no way to LEARN a pre-minted `run_id` before responding — `B-71`'s own scope, confirmed narrower in round 7, only covers an ALREADY-DISPATCHED child's exposure). This case is genuinely **not closeable by this spec-leg** — it stays open, gated on `B-71` (and, if ever pursued, a further Runtime-side early-minting extension `B-71` does not currently cover).

**This resolves the fork-doc's (a)/(b)/(c) framing: neither (b) widen property 1's key to a union, nor (c) a wholly separate delivery path, is needed.** Property 1's `run_id`-shaped key is untouched. What CP spec v1.106 §1.2 is missing is a narrow, ADDITIVE property — **property 6** — that:

- Names the third sub-case property 5's own test already logically implies but never states: a gate-owning branch (per property 5's test) that has not yet produced a child run ("pre-dispatch gate-owning").
- States property 4's Safety-clause counting/SOLE-membership test MUST include pre-dispatch gate-owning branches in the "unaddressed gate-owning set," using an implementation-discretion internal identity (CONTRACT altitude — no carrier field name or shape prescribed, mirroring how properties 1-4 already defer their own resolver mechanism to the impl leg).
- States explicitly that a pre-dispatch gate-owning branch is NEVER eligible for property 1's KEYED `hitl_responses` resolution (no `child_run_id` exists to key by) — only ever resolvable via property 4's uniform fallback, and only when it is the sole member of the unaddressed set. If not sole, it re-pauses INERT — a stated, accepted liveness limitation (not a defect), forward-dependent on `B-71`.

This is narrow and additive: it does not edit properties 1-5's existing text, does not widen any carrier's public shape, and closes exactly `B-72`'s net-position item (1) while leaving items (2)/(3)/(4) (keyed multi-peer addressing, the resolver's general set-membership mechanism, `B-72`'s own round-1 hybrid case) exactly as open as rounds 5/6/7 already scoped them.

## 5. Tiebreaker check

**Does property 4's Safety-clause text, as already written, implicitly cover the pre-dispatch case (reading "whose own `child_run_id` is NOT a key" as vacuously true when no `child_run_id` exists), making a new property unnecessary?**

Checked directly against the text: "every gate-owning branch paused this cycle whose own `child_run_id`..." — a possessive "its own X" construction presupposes X exists to be "its own" of. A branch with no `child_run_id` at all is not clearly "a gate-owning branch whose `child_run_id` is not a key" versus simply outside the clause's contemplated domain. This is genuinely ambiguous by strict reading, but the safer, `CLAUDE.md` X-AL-3-compliant reading is: **silence is a gap, not implicit coverage** — stretching existing text to cover a case its own authors were demonstrably not thinking about (per the round-3/4/5 correction history of this exact section) would itself be an uncontrolled silent extension. **Confirmed: this is a genuine spec gap requiring the new property, not an already-covered case.**

## 6. Fork classification

**Class 1** (halt-execution; design artifact requires revision) per `CLAUDE.md` §4.3 — spec contract under-specifies a surface. Routes to Phase 5 spec revision-pass: CP spec v1.107 → v1.108 (property 6, additive; §1.2 properties 1-5 text PRESERVED VERBATIM), CP plan v2.43 → v2.44 (deferred-bucket note, mirroring how properties 1-4 were deferred at v2.42 §5 — zero new unit, the resolver mechanism stays impl-leg-deferred), clearance marker.

**Operator sign-off status:** the operator already ratified "open the CP spec-leg now, co-designed with `B-71`" via `AskUserQuestion` (2026-07-25). This recommendation's finding — that neither (b) nor (c) is needed, and B-71 is NOT a co-requisite for closing item (1) specifically — narrows scope relative to what was authorized, not widens it. Per this arc's own precedent (B-39 rounds 1-7, B-70), spec-leg CONTENT decisions of this shape are drafted by the recommending pass and verified by out-of-family `just codex-review` before merge, not re-ratified via a fresh `AskUserQuestion` each round — reserved for genuinely new forks (this arc's own Q1/Q2, B-70's "should we do this at all"). No new fork of that kind is present here.
