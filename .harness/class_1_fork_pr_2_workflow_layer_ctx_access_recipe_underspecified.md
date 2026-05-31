# Class 1 Fork — PR-2 workflow-layer composer ctx-access recipe underspecified

**Filed:** 2026-05-31 by autonomous overnight loop iteration 3
**Trigger:** Probe-first discipline at PR-2 impl arc opening (standing posture amendment 5)
**Status:** PROPOSING — awaits operator AskUserQuestion ratification
**Anchor:** CP spec v1.29 §16.5.12.2 + IS spec v1.3 §5.2 + workspace CLAUDE.md §4.4 X-AL-3

---

## §1 — The structural ambiguity

CP spec v1.29 §16.5.12.2 row 1-4 enumerate per-composer recipe for the 4 workflow-layer composers at CP-axis:

| Composer | Recipe (per spec §16.5.12.2) |
|---|---|
| U-CP-14 `emit_override_state_ledger_entry` | `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)` |
| U-CP-27 `emit_workload_class_selection_state_ledger_entry` | `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)` |
| U-CP-30 `emit_pause_resume_state_ledger_entry` (class method) | `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)` |
| U-CP-37 `emit_hitl_tool_call_rewriting_state_ledger_entry` | `procedural_tier_snapshot_ref = resolve_procedural_tier_snapshot(harness_context)` |

§16.5.12.2 framing: *"`harness_context` is sourced from the composer's containing call stack (workflow_driver step-dispatch ctx pass-through OR composer-construction-site closure capture)."*

**Empirical probe at HEAD `4294d41`:**

| Composer file:line | Signature ctx access? |
|---|---|
| `harness-cp/src/harness_cp/per_step_override_evaluator.py:288` | ❌ No `harness_context` parameter |
| `harness-cp/src/harness_cp/workload_binding_engine_class_selection.py:302` | ❌ No `harness_context` parameter |
| `harness-cp/src/harness_cp/pause_resume_protocol.py:637` (class method) | ❌ Class method on `PauseResumeProtocol`; class body has no ctx attribute |
| `harness-cp/src/harness_cp/hitl_as_tool_call_rewriting.py:249` | ❌ No `harness_context` parameter |

None of the 4 ctx-access workflow-layer composer signatures accept `harness_context`. The composer bodies CANNOT call `resolve_procedural_tier_snapshot(harness_context)` because `harness_context` is not in lexical scope.

The spec's framing "sourced from the composer's containing call stack" is true for the CALLER but does not specify HOW the composer body accesses ctx. PR-2 cannot proceed without choosing a binding mechanism.

---

## §2 — Adjacent constraint: harness-cp ↛ harness-runtime dep graph

`HarnessContext` is declared at `harness-runtime/src/harness_runtime/types.py`. `harness-cp/pyproject.toml` does NOT declare `harness-runtime` as a dependency (verified empirically; the dep graph is harness-runtime → harness-cp, not the reverse). Importing `HarnessContext` directly into harness-cp composer signatures would invert the workspace dep graph and trigger `[[carrier-home-defect-pattern]]`.

Two viable workarounds:
- (i) Re-home `HarnessContext` (or a narrower Protocol surface) to `harness-core` (shared types package)
- (ii) Push the resolver invocation to the caller-site (harness-runtime side); composer accepts the resolved `Identifier` value

---

## §3 — Three readings

### Reading A — composer signature widening with `harness_context: HarnessContext`

Each of the 4 composers gains a kw-only `harness_context: HarnessContext` parameter. Composer body calls `resolve_procedural_tier_snapshot(harness_context)` directly.

**Pros:**
- Mirrors §16.5.12.2 spec text literally
- Symmetric with §16.5.12.3 engine-layer signature extension pattern
- Composer encapsulates the resolver call (single locus of change per composer)

**Cons:**
- Requires re-homing `HarnessContext` to `harness-core` (cross-axis carrier-home reshuffle; cross-axis cascade required)
- Spec §16.5.7's `ledger_writer` floor is a single sibling-callable convention; adding ctx as a different shape (concrete object, not callable) extends the floor's pattern non-trivially
- Cannot be applied to U-CP-30 class method without rethinking PauseResumeProtocol class API surface

### Reading B — composer signature widening with `procedural_tier_snapshot_ref: Identifier`

Each composer gains a kw-only `procedural_tier_snapshot_ref: Identifier` parameter. Caller resolves and passes the Identifier value.

**Pros:**
- ZERO carrier-home reshuffle (Identifier already at harness-is)
- Symmetric with `actor: ActorIdentity` parameter pattern (caller resolves identity context, passes value)
- Composer body remains pure-data: `EntryPayload(action_id=..., procedural_tier_snapshot_ref=..., ...)`
- Compatible with U-CP-30 class method (just another kw-only param)

**Cons:**
- §16.5.12.2 spec recipe column reads as "composer calls resolver" — Reading B pushes the call to the caller
- Each caller-site (workflow_driver step-dispatch + sub_agent_dispatch + 1-3 other surfaces) must explicitly invoke `resolve_procedural_tier_snapshot(ctx)` before composer invocation
- §16.5.12.5 HALT-on-resolver-failure posture (composer-site) is structurally shifted to caller-site

### Reading C — uniform `procedural_tier_snapshot_resolver: Callable[[], Identifier]` (mirror §16.5.12.3)

Each of the 4 workflow-layer composers gains the same `procedural_tier_snapshot_resolver: Callable[[], Identifier]` kw-only parameter that §16.5.12.3 authors for engine-layer composers. ALL 6 composers (workflow + engine) carry uniform treatment.

**Pros:**
- Collapses the workflow-vs-engine split at §16.5.12.2 into a single signature pattern
- Symmetric with `ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]]` floor at §16.5.7
- Composer encapsulates the resolver invocation (per §16.5.12.5 HALT-on-resolver-failure)
- ZERO carrier-home reshuffle (`Callable` + `Identifier` already typeable)
- Caller-side: `procedural_tier_snapshot_resolver=make_procedural_tier_snapshot_resolver(ctx)` — uniform binding

**Cons:**
- Diverges from §16.5.12.2 row 1-4 spec text (which writes the recipe as a direct `resolve_procedural_tier_snapshot(harness_context)` call, not a resolver-closure invocation)
- Would require spec-side canonical-reading amendment at §16.5.12.2 collapsing the workflow-vs-engine split

---

## §4 — Why halt: X-AL-3 + workspace pattern discipline

Per workspace CLAUDE.md §4.4 X-AL-3: "no silent H_T design extension at Phase 7 execution."

Each reading constitutes a contract surface decision:
- Reading A: re-homes `HarnessContext` cross-axis (silent re-home = X-AL-3 violation)
- Reading B: shifts HALT-posture composer-site → caller-site (silent shift = X-AL-3 violation)
- Reading C: collapses the §16.5.12.2 workflow/engine split into uniform treatment (silent canonical-reading amendment = X-AL-3 violation)

The autonomous loop cannot pick any reading without operator AskUserQuestion ratification. Pattern catalogued: `[[spec-prose-recipe-vs-existing-composer-signature-divergence]]` — sub-species candidate at workflow v1.13 §7.4.7.2 (cardinality 1; await second instance).

This is a sibling pattern to `[[plan-revision-against-not-yet-built-substrate]]` at the spec-vs-impl-state interface: PR-1 (CP spec v1.29) authored a recipe that the existing composer signatures cannot satisfy. The recipe presumed a composer-signature reshape that PR-1 did not author. PR-2 surfaces the gap at impl arc opening.

---

## §5 — Closure path

Operator AskUserQuestion at morning session:

**Q1 — Reading selection:** (A) ctx-passthrough with `HarnessContext` re-home / (B) caller-resolves + passes `Identifier` / (C) uniform resolver-closure

**Q2 — Spec amendment shape:** if Reading C wins, author CP spec v1.30 canonical-reading amendment at §16.5.12.2 collapsing the workflow/engine split. If Reading A wins, author CP spec v1.30 amendment + harness-core carrier-home extension. If Reading B wins, author CP spec v1.30 canonical-reading amendment at §16.5.12.5 (HALT-posture shifts caller-site) + §16.5.12.2 recipe column.

**Q3 — Cross-axis cascade scope:** Reading A requires `HarnessContext` Protocol surface at harness-core (cascade to harness-runtime + harness-cp + harness-as imports). Readings B + C have ZERO cross-axis cascade beyond CP spec amendment.

**Q4 — PR-2 + PR-3 stack reshape:** original PR-2 (9 ctx-access sites) + PR-3 (3 engine-layer sites) shape pre-supposed §16.5.12.2 split. If Reading C wins, all 6 composers carry uniform signature; PR-2 + PR-3 collapse into single PR-stack body.

---

## §6 — Provenance

Surfaced by probe-first discipline at PR-2 opening (workspace CLAUDE.md §10.9 standing posture amendment 5). The probe ran in 3 minutes; would have surfaced as X-AL-3 violation 30+ minutes into impl arc if discipline were skipped.

Validates the 2026-05-31 council orchestrator pilot bake-in: probe-first discipline at substantive arc opening catches structural ambiguity before code is authored.

ZERO impl + ZERO test + ZERO design-substrate edit at this filing. Routes for morning-Robert.

**Workspace pattern + sub-species candidate also catalogued:**
- `[[spec-recipe-references-symbol-not-in-composer-scope]]` — at v1.13 §7.4.7.2 sub-species column candidate; cardinality 1 (this filing); awaits second instance before workflow-doc promotion.
- Sibling discriminator to `[[plan-revision-against-not-yet-built-substrate]]` (which operates at plan-vs-impl-state); this pattern operates at spec-recipe-vs-composer-signature.
