# Class 1 fork — CXA-1 (AS→IS): secret-fetch audit production caller fires at a bootstrap stage that precedes the AS→IS wiring stage

**Status:** ✅ APPLIED-AS-READING-D (operator AskUserQuestion 2026-06-01) — **don't wire; defer.** The apply-arc empirical orientation (advisor-prompted, §2.6) found the bootstrap-value fetch path does not fit this `resolve()`-shaped event AND the entire `SecretFetchEvent` machinery has **zero production producer** — wiring bootstrap-value with sentinels would be a hollow seam (vacuous-close / `test-bypass-as-runtime-truth`). R-CXA-1 must_pass #1 stays **deferred / PARTIAL**; no production code change. must_pass #1 re-opens when a real scoped-`resolve()` producer exists OR the `SecretFetchEvent` contract is reshaped for the name-only bootstrap path (Reading C, a design-substrate amendment). Originally filed PROPOSING; Reading B was first ratified but found unwritable-as-previewed at the apply arc (§2.6).
**Filed:** 2026-06-01, during the post-R-300 / post-R-100 "continue" derivation. The roadmap's top Claude-executable post-Phase-8 lever (`R-CXA-1-as-is-seam`) was grounded before opening; must_pass #1 ("a production caller invokes `emit_secret_fetch_audit_entry`") surfaces a bootstrap-ordering / substrate-lifecycle mismatch — the same shape as the U-RT-111 saga — so it routes to back-flow rather than being silently wired.
**Class:** 1 (architectural — closing the seam's first edge requires a bootstrap stage-ordering / resolver-signature decision; wiring it without ratification would be a silent X-AL-3 design extension to the bootstrap contract).
**Blocks:** `R-CXA-1-as-is-seam` must_pass #1 (the secret-fetch production-caller edge). Transitively gates `R-700-phase-8-substitution-accounting` (CXA-1 is one of the open non-RETIRED rows). Does NOT block must_pass #2 (the remaining ~12 AS source-unit edges) directly — those are a separate, larger sub-arc that may surface their own per-edge firing-site questions.
**Security finding (resolved — NOT a blocker):** the audit event is **metadata-only by design** — see §2.4. Emitting on secret-fetch does not leak secret material.

---

## 1. The divergence

`R-CXA-1-as-is-seam` must_pass #1 asks for "a production caller [to invoke] `emit_secret_fetch_audit_entry` (AS secret-fetch driver path lands)." The AS→IS emitter exists and is 7c-tested, but has **zero production callers** (the dashboard's PARTIAL framing). Wiring the real caller means: every live secret fetch should compose + persist one AS→IS audit-ledger entry.

The blocker: **the live secret-fetch path fires at a bootstrap stage that runs BEFORE the stage at which the AS→IS emitter is materialized.** The firing site precedes its own wiring stage — structurally the U-RT-111 AC#2 / sandbox-decision-resolver shape (`class_1_fork_tool_step_no_bootstrap_sandbox_decision_resolver.md` §1).

## 2. Evidence (code-level, conclusive — verified at HEAD `10083aa`)

### 2.1 The emitter materializes at stage 6 (CXA_WIRING)
- `harness-runtime/src/harness_runtime/bootstrap/__init__.py:101-110` — `_STAGE_MODULES` order: `0 PREAMBLE → 1 IS → 2 AS → 3a CP_CLIENTS → 3b CP_ROUTING → 4 OD → 5 LOOP_INIT → 6 CXA_WIRING → 7 INGRESS`.
- `harness-runtime/src/harness_runtime/bootstrap/stage_6_cxa_wiring.py:62` — `assert ctx.ledger_writer is not None, "stage 1 IS must precede stage 6 CXA_WIRING"`; `:70` — `ctx.cxa_stages["as_is_wiring"] = materialize_as_is_wiring_stage(config, ctx.ledger_writer)`. The `RuntimeAsIsWiring` emitter (`lifecycle/as_is_wiring.py:82`, `emit_secret_fetch_audit_entry` at `:96`) is built **at stage 6**.

### 2.2 The live secret-fetch fires eagerly at stage 3a (CP_CLIENTS)
- `harness-runtime/src/harness_runtime/bootstrap/stage_0_preamble.py:42` — `ctx.keyring_resolver = make_keyring_resolver(config.provider_secrets)` (resolver built at stage 0).
- `harness-runtime/src/harness_runtime/bootstrap/stage_3a_cp_clients.py:44` — `stage = await materialize_provider_clients_stage(config, ctx.keyring_resolver)` (`providers.py:630`). The resolver is invoked **eagerly here**: the R-100 AC#2 e2e this session emitted `ProviderDegradedWarning: provider='anthropic': degraded (unreachable): keyring entry 'anthropic_key' not found` from `stage_3a_cp_clients.py:44` — i.e., the resolve was attempted at stage 3a, not lazily at first inference.

### 2.3 The ordering mismatch
- `ledger_writer` is ready at the fetch site (stage 1 IS < stage 3a) — so the durable substrate exists.
- The `RuntimeAsIsWiring` emitter is **not** (stage 6 CXA_WIRING > stage 3a) — so the canonical emit surface the seam was built around is unavailable at the firing site.

To wire must_pass #1 you must either move the emitter earlier, emit at stage 3a through the already-available `ledger_writer` (bypassing the stage-6 wrapper), or buffer-and-flush — each a bootstrap-contract decision.

### 2.4 Security (metadata-only by design — NOT a blocker)
`harness-as/src/harness_as/secret_fetch_audit.py:45` — `class SecretFetchEvent(BaseModel)` with `model_config = ConfigDict(extra="forbid", frozen=True)` and fields `{secret_name, secret_scope, secret_last_rotated_at ("version attribute — structure, not value"), actor, timestamp, thread_id, step_id}`. **No secret-value field**, extras forbidden. Composing/persisting it records *that* a secret was fetched (name + scope + rotation version + outcome), never the value. The emission is security-safe.

### 2.5 Bootstrap-scoped identifiers
`emit_secret_fetch_audit_entry` builds a `WriteKey(thread_id=event.thread_id, step_id=event.step_id, ...)` (`as_is_wiring.py:120-124`). Secret-fetch fires at bootstrap, outside any workflow/step — the code already anticipates this (`as_is_wiring.py:110-113`: "Secret-fetch audit entries fire at bootstrap / provider-construction — outside an active workflow context — so the D-derivative sidecar does not apply"; `procedural_tier_snapshot_ref` left `None`-canonical). So bootstrap-sentinel identifiers (e.g., `Identifier("bootstrap")` / `Identifier("secret-fetch:<provider>")`) are the natural choice — a sub-decision of whichever Reading is chosen.

### 2.6 Apply-arc finding — Reading B is unwritable as previewed; the event has no real producer (verified at HEAD `9936dfc`)

The ratified Reading B preview showed `secret_scope=ref.scope` and `secret_last_rotated_at=meta.rotated_at`. **Neither `ref` nor `meta` exists at the emit site:**

1. **Bootstrap path is value-not-ref.** `construct_anthropic_adapter` / `construct_openai_adapter` (`providers.py:328` / `:438`) call `resolver.resolve_bootstrap_value(NAME)` → a bare `str`. The scoped `KeyringSecretResolver.resolve(name, scope, tier) -> SecretRef` (`provider_secrets.py:131`) — the only path that produces a scope-bearing `SecretRef` — is **never called in production** (the sole `.resolve(` hits in `src/` are `pathlib.Path.resolve()`). So at the fetch site there is no scope and no `SecretRef`.
2. **`secret_last_rotated_at` has no production source at all.** Keyring exposes no rotation metadata; `rotated_at` appears in `src/` only as the field definition + the fingerprint-hash consumer. Nothing can populate it truthfully.
3. **Sentinels are material, not cosmetic.** Both `secret_scope` and `secret_last_rotated_at` feed `canonicalize_concat_secret_fingerprint(secret_name, secret_scope, secret_last_rotated_at)` (`secret_outputs_hash.py:83`). Sentinel both → the fingerprint collapses to `f(secret_name)`, so it can never detect a rotation or scope change — the entire reason the fields exist.
4. **Fire-once-forever idempotency.** `_idempotency_key = sha256(thread_id, step_id, secret_name, secret_scope.name)` (`secret_fetch_audit.py`) — no timestamp. Constant bootstrap-sentinel identifiers → the same key every boot → one ledger entry per provider **ever**; every subsequent bootstrap is an `IDEMPOTENT_NOOP`. The "audit" would not record per-boot fetches.
5. **No real producer anywhere.** `RuntimeAsIsWiring.emit_secret_fetch_audit_entry` has zero production callers; `harness_as.secret_fetch_emission.emit_secret_fetch_audit` (`:102`) *composes-and-discards* (drops the composed entry). Nothing threads a real secret fetch into this machinery. It is speculative substrate.

**Conclusion:** wiring bootstrap-value into this `resolve()`-shaped event with sentinels satisfies the *letter* of must_pass #1 (a production caller invokes the emitter) while producing a hollow, fingerprint-defeated, fire-once seam — the vacuous-close anti-pattern. Operator ratified **Reading D** (defer) on this finding.

## 3. The decision

The bootstrap-ordering choice is a single-axis runtime/bootstrap-contract decision (no cross-domain value tension; security is safe per §2.4 → **not council-eligible**). It does need ratification because each Reading changes the bootstrap contract.

### Readings

- **(A) Materialize the AS→IS emitter early.** `RuntimeAsIsWiring` depends only on `ledger_writer` (ready at stage 1). Build it right after stage 1 IS (or in stage 2 AS) and thread it into stage 3a so each fetch emits. **Cleanest reuse** of the existing wrapper. **Tradeoff:** moves one CXA edge out of the canonical stage-6 CXA_WIRING home → breaks the "all CXA wiring at stage 6" convention for this edge.

- **(B) Emit directly at stage 3a via the available `ledger_writer` (RECOMMENDED).** At stage 3a `ctx.ledger_writer` exists; construct the `SecretFetchEvent` + call `compose_secret_fetch_audit_entry` (`secret_fetch_audit.py:76`) + `ledger_writer.append(...)` at the resolver-invocation site (or wrap a throwaway `RuntimeAsIsWiring(ctx.ledger_writer)` there). **Most surgical** — no stage reorder, stage 6 stays the canonical home for the *other* AS→IS edges, secret-fetch is correctly treated as the one bootstrap-scoped edge. **Tradeoff:** special-cases secret-fetch as a stage-3a emit rather than a stage-6 one.

- **(C) Buffer-and-flush.** Collect secret-fetch events at stage 3a in a bootstrap buffer; flush through the stage-6 `RuntimeAsIsWiring` emitter. Mirrors the existing `bootstrap_emission_buffer` span pattern (`__init__.py:16`). **Keeps both** eager-fetch-at-3a and canonical-wiring-at-6. **Tradeoff:** heaviest — adds a buffer + flush step for one edge.

- **(D) Reframe: secret-fetch audit is bootstrap infrastructure, not a per-workflow AS→IS edge.** Question whether the bootstrap secret-fetch belongs on the C-RT-12 §12.2 per-step AS→IS seam at all, vs. a bootstrap-audit channel. The seam (C-RT-12 §12.2) is the canonical home and the event type already models bootstrap-scoped fetches (§2.5), so this is likely a NO — but it is the framing question to settle before A/B/C.

**Recommendation:** **(B)** — surgical, no ordering-convention break, treats the single bootstrap-scoped edge as a bootstrap-stage emit while leaving stage-6 canonical for the remaining ~12 per-step edges. With bootstrap-sentinel identifiers per §2.5. Ratification still required (it changes the stage-3a contract to consume `ctx.ledger_writer`).

## 4. Scope note (do not over-read)

This fork is about **must_pass #1** (the secret-fetch production-caller edge + its bootstrap-ordering blocker). **must_pass #2** ("remaining ~12 AS source-unit audit-emission callbacks threaded through `AsIsWiring`", per CXA v2.18 §2.3.1's 13 AS→IS edges) is a separate, larger sub-arc. Those edges fire at various lifecycle points and may each surface their own firing-site questions — they are NOT resolved by this fork. CXA-1 → fully wired only when both must_pass clauses land.

## 5. Resolution log

- **2026-06-01 — Reading B first ratified** (operator AskUserQuestion, side-by-side preview). Apply arc opened.
- **2026-06-01 — apply-arc empirical orientation (§2.6) + advisor reconcile** found Reading B unwritable-as-previewed and the event producerless. Re-surfaced the corrected picture.
- **2026-06-01 — Reading D ratified** (operator AskUserQuestion): don't wire; defer. R-CXA-1 must_pass #1 stays PARTIAL; ZERO production code change. Re-opens on a real scoped-`resolve()` producer OR a Reading-C contract reshape. Recorded here; roadmap §5 R-CXA-1 + dashboard refreshed.

**Note for a future arc:** before R-CXA-1 must_pass #1 can land non-vacuously, the upstream question is "what is the *real* producer of a secret-fetch audit?" — i.e., does any workflow-time path call the scoped `resolve()` with a genuine scope, and should that (not bootstrap-value provider construction) be the emit site? That is a producer-discovery question, not a bootstrap-ordering one. The bootstrap-ordering blocker this fork named is real but secondary — it only bites once a real producer exists.
