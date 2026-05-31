# Class 2 Fork Record — U-CP-74 override state-ledger entry `actor` field malformation

**Filed:** 2026-05-29 (probe v2 closure arc — exercises U-CP-74 production firing site via `harness run`).
**Class:** 2 (in-execution operator decision — two valid fixes, semantics-preserving at the wire; operator owns caller-side-vs-composer-side preference).
**Status:** ✅ APPLIED-AS-READING-A 2026-05-29 (extended to sibling scope per follow-on operator AskUserQuestion). Operator AskUserQuestion at apply-arc opening ratified Reading A (caller-side conform) + bundled single-PR shape; second AskUserQuestion mid-arc ratified sibling-scope extension to 3 sibling U-CP-76 firing sites carrying the identical bug pattern. Patches at:

- `harness-cp/src/harness_cp/workflow_driver.py:851` — U-CP-74 RESOLVE_STEP_BINDING emission (original Reading A site)
- `harness-cp/src/harness_cp/workflow_driver.py:581` — U-CP-76 RESUME_ATTEMPTED emission
- `harness-cp/src/harness_cp/workflow_driver.py:811` — U-CP-76 PAUSE_CAPTURED emission (drain-flag path)
- `harness-cp/src/harness_cp/workflow_driver.py:982` — U-CP-76 PAUSE_CAPTURED emission (HITL-signal path)

All 4 sites now pass `ActorIdentity(ctx.ledger_writer.actor.actor_id)` instead of `ctx.ledger_writer.actor`; `ActorIdentity` import added at line 49. NEW regression test `test_caller_site_override_emission_actor_id_is_clean_identity` at `harness-runtime/tests/integration/test_cp_is_caller_site_integration.py` asserts `actor.actor_id` is the bare identity string and contains no Pydantic field-repr characters (`=` / `<`). 803/803 harness-cp + integration tests + 1306/1306 harness-runtime tests pass + 10 skipped. Probe v2 re-run post-Reading-A confirms wire entry now carries `"actor_id":"harness-runtime"` (was `"actor_id":"actor_class=<ActorClass.AGENT: 'agent'> actor_id='harness-runtime'"`). Idempotency key 3-tuple shape identical pre/post (outcome bytes unaffected by actor change). ZERO spec amendment (CP spec v1.27 §16.5.3 preserved verbatim); ZERO cross-axis cascade. The 3 sibling U-CP-76 firing sites were not exercised by probe v2 (which targeted U-CP-74 via `per_step_overrides`); the sibling defects were surfaced by post-PR-#83 grep extension of the `actor=ctx.ledger_writer.actor` pattern across `harness-cp/src/`. Two non-bug sites at `workflow_driver.py:910` (StepExecutionContext.parent_actor — Actor-typed slot, correct) + `workflow_driver.py:1363` (EntryPayload.actor — Actor-typed slot, correct) preserved verbatim. Filed at PR #83.

**Composer-side residual carry.** Reading B (composer-side conform + spec v1.27 → v1.28 §16.5.3 amendment) NOT applied. The 6 `harness-cp/src/harness_cp/*.py` composer bodies still carry the defensive `actor=Actor(actor_class=ActorClass.AGENT, actor_id=str(actor))` wrapping that defeated the original Reading A application. At the 4 firing sites patched at this arc, caller now passes `ActorIdentity` (str-newtype) so `str(actor)` is a no-op. The 4 NON-production-firing composer surfaces (U-CP-75 workload-class-selection + U-CP-77 HITL rewriting + U-CP-78/79 engine-layer free functions) preserve the defensive wrapping but emit nothing at production. If any future production caller fires those composers without passing a proper `ActorIdentity`, the defect re-surfaces — Reading B would foreclose this systematically.
**Surfaced by:** `use-the-product` probe v2 — operator-facing `harness run` against a TOML manifest with `per_step_overrides` populated for `s1` (probe v1 used empty `per_step_overrides = {}` and never reached the U-CP-74 firing-site path).
**Surfacing PR:** probe-v2-per-step-overrides worktree (this branch).
**Anchors:** CP spec v1.27 §16.5.3 `EntryPayload` field-set; CP spec v1.27 §16.5.7 firing-site discipline; `harness-cp/src/harness_cp/per_step_override_evaluator.py:281-314` composer; `harness-cp/src/harness_cp/workflow_driver.py:843-853` firing site; `harness-is/src/harness_is/state_ledger_entry_schema.py:53` `Actor` Pydantic model.

---

## 1. The defect

Running `harness run` against a manifest with one `per_step_overrides` entry populated for `s1` emits 3 state-ledger entries (vs probe v1's 2). The U-CP-74 emission (entry 1, action_id=`cp.per-step-override-application`) carries a malformed `actor` field:

```json
{
  "action_id": "cp.per-step-override-application",
  "idempotency_key": "ac374bd4a84edd2353f2d614193626595463deeb079cafca138ebb2b4ef72f35",
  "actor": {
    "actor_class": "agent",
    "actor_id": "actor_class=<ActorClass.AGENT: 'agent'> actor_id='harness-runtime'"
  },
  "response_hash": "8926bf017f73338a79a87d0bd2bcf689ec6adf2a4fdc89cbea20c0e5edf7d1a0",
  "timestamp": "2026-05-29T21:23:39.975936+00:00",
  "prior_event_hash": "0000…00000"
}
```

`actor.actor_id` is the Pydantic field-repr of the upstream `Actor` model, not the actor identity string `"harness-runtime"`. The two sibling entries (audit-single + workflow step) emitted on the same run carry the clean `"actor_id": "harness-runtime"` shape.

Verified at HEAD `e216cc0` (probe-v2 worktree based off main post PR #82). Hash chain validates; idempotency key conforms to v1.27 §16.5.4 3-tuple shape; only `actor.actor_id` is wrong.

---

## 2. Root cause

`emit_override_state_ledger_entry` at `per_step_override_evaluator.py:281` declares:

```python
async def emit_override_state_ledger_entry(
    *,
    workflow_id: str,
    step_id: str,
    post_override_step_config: Mapping[str, Any],
    actor: ActorIdentity,                      # ← signature claims str-newtype
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
) -> WriteResult:
    ...
    payload = EntryPayload(
        ...
        actor=Actor(actor_class=ActorClass.AGENT, actor_id=str(actor)),  # ← line 311
        ...
    )
```

`ActorIdentity` is `NewType("ActorIdentity", str)` per `harness-cp/src/harness_cp/cp_shared_types.py:53`. The composer assumes a string input and applies `str(actor)` defensively.

Caller at `workflow_driver.py:851` passes:

```python
_run_protocol_method_sync(
    _cp_is_wiring.emit_override_state_ledger_entry(
        workflow_id=manifest_entry.workflow_id,
        step_id=str(step.step_id),
        post_override_step_config=binding.model_dump(mode="json"),
        actor=ctx.ledger_writer.actor,   # ← passes Actor Pydantic model, not ActorIdentity
    )
)
```

`ctx.ledger_writer.actor` is an `Actor` Pydantic instance (declared `actor: Actor` at `harness-is/.../state_ledger_write.py:73`). `str(actor)` on a Pydantic model returns the field-repr (`"actor_class=<ActorClass.AGENT: 'agent'> actor_id='harness-runtime'"`), which then becomes the nested `actor_id` string.

U-CP-74 is the ONLY firing-site path that re-wraps `actor` as a NEW `Actor`. The five sibling composers (U-CP-75..U-CP-79) accept `Actor` directly and pass it through to `EntryPayload.actor`.

Caller-side (`workflow_driver.py:851`) and composer-side signature (`actor: ActorIdentity`) disagree on whether the input is a string or an `Actor`. The current behavior is the visible artifact of that disagreement.

---

## 3. The two valid fixes

### Reading A — Caller-side conform

Change `workflow_driver.py:851` to pass the string:

```python
actor=ctx.ledger_writer.actor.actor_id,
```

**Pros:**
- Composer signature unchanged (CP spec v1.27 §16.5.3 cite preserved verbatim — actor declared `ActorIdentity`).
- Minimal blast radius — one-line caller-side change at one site.
- No test-fixture churn outside the override path.

**Cons:**
- Asymmetric with the 5 sibling composers (U-CP-75..U-CP-79) which receive `Actor` directly. The whole §16.5 composer family becomes mixed: U-CP-74 takes a string, U-CP-75..79 take an `Actor`. Future readers must remember the asymmetry.
- Drops the upstream `actor.actor_class` distinction — the override entry always emits `actor_class=AGENT` regardless of caller-class. If a future caller is a non-AGENT (operator-explicit override?), the AGENT hardcode at line 311 silently absorbs the wrong class.

### Reading B — Composer-side conform

Drop the re-wrapping at `per_step_override_evaluator.py:311`; accept `Actor` directly:

```python
async def emit_override_state_ledger_entry(
    *,
    workflow_id: str,
    step_id: str,
    post_override_step_config: Mapping[str, Any],
    actor: Actor,                              # ← was ActorIdentity
    ledger_writer: Callable[[EntryPayload], Awaitable[WriteResult]],
) -> WriteResult:
    ...
    payload = EntryPayload(
        ...
        actor=actor,                           # ← drop re-wrapping
        ...
    )
```

**Pros:**
- Symmetric with the 5 sibling §16.5 composers — entire family takes `Actor`.
- `actor_class` flows through honestly from caller.
- Caller already passes `Actor` at every §16.5 firing site; no per-site adjustment.

**Cons:**
- CP spec v1.27 §16.5.3 declares the field as `actor: ActorIdentity` at U-CP-14 (the table at §16.5.3 row 1). Reading B requires either (i) a v1.28 spec amendment widening the row to `actor: Actor`, or (ii) a canonical-reading amendment reinterpreting `ActorIdentity` as a structural alias for `Actor` at the §16.5 contract surface. Either is a documented spec arc — non-trivial vs Reading A's one-line patch.
- The 13 NEW tests at U-CP-74 landing (PR #78) likely fixture `ActorIdentity` strings; would require fixture refresh.

---

## 4. Why this is Class 2, not Class 1

The wire-level entry IS persisted; hash chain validates; the override IS detected as override-applied; the run completes successfully end-to-end. The defect is at the `actor.actor_id` semantic only — operator-facing audit-trail readers see a Pydantic repr string instead of an actor identity. No silent X-AL-3 design extension; no production halt; no upstream substrate gap.

Operator owns the choice because both fixes preserve the wire-level invariants (hash chain + idempotency key + action_id + timestamp). The choice is a taste call between (i) keep spec text byte-exact, fix one caller site (Reading A); or (ii) make §16.5 composer family symmetric, amend spec at next §16.5 revision-pass (Reading B).

If left unaddressed, the misshape preserves at every per-step-override entry in production audit trails. Not corrupting — diagnostic-confusing.

---

## 5. Probe v2 framing

This finding sharpens two pre-existing workspace patterns:

**`[[use-the-product-probe]]` (catalogued at PR #79 §4(e)).** Probe v2 IS a second cardinality of the pattern — operator-facing `harness run` end-to-end exercise surfaced a U-CP-74 production-firing-site defect that 13 unit tests + 1 e2e test (PR #78) all PASS without surfacing. The unit tests at U-CP-74 likely fixture `ActorIdentity` strings directly (matching the composer signature), so they never exercise the caller-side type-mismatch path. The probe IS the discovery surface.

**Probe-v2 also validates `[[h-t-rt-35-retire-ready-batch-45]]` discipline:** PR #78 transit `vacuous-RETIRED → genuine-via-execution` IS achieved at probe v2 — U-CP-74 firing site reaches production via the operator-facing CLI surface, emits the 3rd ledger entry with canonical action_id, and the hash chain validates. The actor defect is orthogonal to the transit verification.

---

## 6. Adjacent observations (not patched per FM-2)

(a) **The override entry is emitted FIRST** (genesis position, `prior_event_hash="0" * 64`) — BEFORE the workflow-genesis audit entry. This is per `workflow_driver.py:828` ordering: `resolve_step_binding` → U-CP-74 emit → §25.3.3.3 lease → §25.3.3.4 dispatch. The audit-single entry at row 2 chains from the override row. CP spec v1.27 §16.5.7 documents "post-resolve-pre-return" firing discipline — consistent. NOT a defect; observation.

(b) **`ctx.ledger_writer.actor.actor_class` is hardcoded `ActorClass.AGENT`** at composer line 311. Currently no production path constructs a non-AGENT ledger writer, but if future override-application surfaces emit from operator-explicit contexts (HITL approve/reject), the AGENT hardcode silently absorbs the actor-class shift. Reading B closes this; Reading A preserves it.

(c) **Justfile `_probe` recipe was added temporarily** to support `--config` flag (existing `just run` lacks it). Probe-arc recipe to be reverted at fork-doc apply-pass close.

---

## 7. Disposition pending

| Disposition | Trigger |
|---|---|
| ✅ APPLIED-AS-READING-A | Operator selects Reading A; one-line caller-side patch + 1 NEW test verifying actor_id roundtrip; ship as apply-PR; close this fork doc |
| ✅ APPLIED-AS-READING-B | Operator selects Reading B; spec v1.27 → v1.28 amendment widening §16.5.3 row 1 + composer signature change + caller-site no-op + fixture refresh + ship as apply-PR; close this fork doc |
| 🟡 DEFERRED | Operator routes to later session; carry as bounded-residual; preserve probe-v2 finding at checkpoint |

Operator AskUserQuestion at apply-arc opening — recommend Reading A (minimal blast radius; preserves spec verbatim).

---

*Filed at probe-v2 closure 2026-05-29. Sibling-class pattern to `class_2_fork_od_spec_declared_but_not_emitted_attributes.md` (declared-but-wire-broken surface; operator-decided semantic-preserving fix). U-CP-74 (S) sibling-variant landing PR #78 + probe-v2 closure arc compose the discovery-evidence chain.*
