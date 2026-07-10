# U-1 slice 3b — cacheable-epoch / partition design (fork resolution + council probe-resolution)

*Output of the fresh-session epoch/partition DESIGN arc (2026-07-10), the next-action reframed at the post-3a grounding (dashboard `git_head` `06a33abe`). This arc was deferred TO a fresh session because the coupled 3c build is a high-blast-radius fan-out concurrency change. It resolves the two open questions the slice-3 findings (`u1-slice3-findings-and-f1-c10-gap.md` §Correction) left for a fresh session: (1) the `major-version-of-system-prompt` fork discriminator, and (2) the prescribed C2⊥C11 ttl council. Both are resolved by probe; the residual build boundary + forward-arc registration are set below.*

---

## 0. TL;DR

- **Fork → BUILD, not X-AL-3 back-flow.** `[HIGH]` A cache-correct epoch key is derivable from existing substrate *now*: Anthropic's prompt cache is byte-exact, and `active_prompt_version.version_sha` (harness-is `PromptVersion`) **is** the byte-exact content identity of the system-prompt prefix component. Back-flow is only forced when a named primitive has *no* coherent derivation — this one has one. The back-flow branch is foreclosed.
- **Council → probe-resolved (no convening).** `[HIGH]` ADR-D3 §1.5 (lines 187-190) already commits the ttl policy the prescribed C2⊥C11 council would decide (`5min default; 1hr at Persona §6 cost-ceiling cells; keep-alive every 4min`). Convening a dyadic council to re-decide a cleared-ADR surface is re-litigating §10.2 (Class 1 territory). The C2/C11 positions are surfaced inline (§3); the genuine residual is a narrow impl-discretion predicate.
- **Two lanes, do not collapse** (advisor correction): **Lane A** (version_sha-keyed epoch) = pure Phase-7 build; **Lane B** (add a semantic-major *field* to `PromptVersion`) = design-substrate IS-spec amendment, and **not required** — version_sha is the cache-correct key.
- **This session builds the one clean, non-hollow, low-blast-radius slice: workload-class-aware cache ttl (3b-ttl).** The version_sha cohort identity + the ADR-D4 §1.8 fan-out pre-warm (3c) are **coupled** (version_sha's only consumer is the pre-warm) and 3c is the deferred high-blast-radius fan-out change → registered for a dedicated session.

---

## 1. Arc lineage + the two open questions

The slice-3 findings closed 3a (F1 — child-scoped downgraded `frozen_tool_superset`, PR #921) and left the slice-3 tail as `B-18-EPOCH-PARTITION` (3b epoch primitive) + `B-18-3C-PREWARM` (3c pre-warm). The §Correction established that 3b + 3c bottom out on ONE blocker — the cacheable-epoch PARTITION keyed on `(role, workload) × major-version-of-system-prompt` (ADR-D3 §1.5) — and posed two fresh-session questions:

- **Q1 (fork discriminator, do NOT prejudge):** is `major-version-of-system-prompt` **derivable from existing substrate** (→ BUILD) or **genuinely absent** (→ X-AL-3 back-flow to ADR-D3 / the prompt spec)?
- **Q2 (prescribed council):** the epoch ttl carries a nameable **C2 (cache-amortization / aggressive-long-ttl) ⊥ C11 (cost-ceiling-aware ttl)** tension → a dyadic council convening per §10.9.

Both are resolved below by empirical probe, per `[[probe-resolves-fork-prescribed-council]]` (a fork's "convene council" prescription is not binding — probe first; an on-substrate committed invariant foreclosing a branch → probe-resolved + voices-inline; scope any residual).

---

## 2. Q1 — fork resolution: BUILD (back-flow foreclosed)

### 2.1 The load-bearing reason — a cache-correct key is derivable now

`[HIGH]` **Anthropic's prompt cache is byte-exact.** A cache HIT requires the cached prefix to match the request prefix byte-for-byte (ADR-D3 §1.5 line 204: "content-hash participates in cache-breakpoint identity"; ADR-F2 §Rationale(b)(ii): "any change to the `tools` array invalidates the entire cache"). Therefore the *only* cache-correct epoch key for "which dispatches can share a warm cache" is the **byte-exact content hash of the cacheable prefix** `[frozen_tool_superset + system_prompt]`.

`[HIGH]` The substrate already carries exactly that identity:
- system-prompt component → `active_prompt_version.version_sha` = `sha256(content)` (`harness_is.prompt_manifest.PromptVersion`, verified: `version_sha` derived from `content`, the derive-invariant enforced at construction).
- tool component → the deterministic `frozen_tool_superset` (already computed + canonically serialized at stage 5, slices 1/2/3a).

Grouping any **coarser** than byte-exact content would be a *cache-correctness bug* — two different-byte prompts sharing a "major version" do **not** share an Anthropic cache entry, so warming one would not warm the other. So the derivable key is not merely sufficient; a coarser semantic-major key would be **wrong** for cache-hit grouping.

### 2.2 The semantic "major version" is a lifecycle dimension, not the cache-hit key

`[MODERATE]` `major-version-of-system-prompt` (ADR-D3 §1.5 line 187) names the operator-facing **lifecycle/ttl policy** dimension (when to keep-alive / roll over / invalidate), distinct from cache-hit identity. The design commits the *concept* of an operator-declared semantic version distinct from the content hash — but for **SKILLS**, not prompts: ADR-D3 §1.8.1 (line 331, load-bearing) commits `skill.frontmatter.version` as "the operator-declared semantic version ... an operator may bump `frontmatter.version` from 1.0 to 1.1 without changing every byte," alongside `skill.version_sha` (the content hash), "both required."

`[HIGH]` For **PROMPTS**, the carrier (`PromptVersion`) has only `version_sha` + `content`; the semantic-version analogue is absent, and `major-version-of-system-prompt` is named exactly once (§1.5 line 187). Adding a semantic-major field is therefore an **analogy-driven carrier extension** (Lane B, §5), NOT a concept already committed for prompts. But it is **not required** for the epoch primitive: version_sha is the cache-correct key.

### 2.3 Verdict

`[HIGH]` **BUILD, not back-flow.** X-AL-3 back-flow is foreclosed because `major-version-of-system-prompt` has a coherent derivation (version_sha) against existing substrate — no design *extension* is needed to build the cacheable-epoch primitive. This is `[[cleared-spec-resolves-it-before-first-principles-fix]]` + `[[grounding-reveals-claude-closeable-slice-close-honestly]]` (spec'd → build). The semantic-major field (Lane B) is a *separate, optional* design-substrate amendment, deliberately not collapsed into the build.

---

## 3. Q2 — council probe-resolution: the ttl policy is already committed

### 3.1 What ADR-D3 §1.5 already commits (the cleared surface)

```
cacheable_epoch: workload-class × major-version-of-system-prompt        # line 187
ttl: 5min default; 1hr at Persona §6 cost-ceiling cells where epoch > 5min   # line 188
pre_warm: max_tokens=0 at process boot; keep-alive every 4min for 5min TTL caches  # lines 189-190
```

`[HIGH]` The ttl VALUES (5min / 1hr), the 1hr TRIGGER (cost-ceiling cells where epoch > 5min), and the keep-alive CADENCE (every 4min) are **committed in the cleared ADR**. The observability schema already ingests both (`anthropic.cache_ttl_seconds` ∈ {300, 3600}, `llm_dispatch.py:361-368`). Re-deciding these via a council is re-litigating a §10.2-committed surface → Class 1 territory, not design work.

### 3.2 C2 ⊥ C11 positions (surfaced inline, per probe-resolves-council)

- **C2 (cache-amortization):** aggressive long ttl + keep-alive maximizes cache-hit rate → the 4–10× cost-detonation avoidance (ADR-F2 §(b)(ii)). Wants 1hr broadly + keep-alive.
- **C11 (cost-ceiling-aware ttl):** the 1hr cache-write is 2× base (vs 5m at 1.25×) and every keep-alive is itself a cache-write — unbounded keep-alive can *detonate* a tight per-class ceiling (Persona §6 per-workload-class ceiling, operator-asserted). Wants 5m default + bounded/opt-in keep-alive.

`[HIGH]` **The cleared ADR already adjudicates this**: 5m is the *default* (C11's safe floor), 1hr is *scoped to cost-ceiling cells where the >5min epoch is beneficial* (C2's win, gated by C11's cost logic). The tension is resolved in favor of a cost-aware default with an opt-in long-ttl for the cells that benefit.

### 3.3 The genuine residual (narrow, impl-discretion)

`[MODERATE]` Two slivers the ADR leaves to implementation, neither a design fork:

- **R1 — the 1hr-selection predicate.** Persona §6 (lines 117-124) has no cell matrix — just "Cost ceiling | Per-workload-class ceiling (different limits per class) | **Operator-asserted**." So "cost-ceiling cells" resolves to an **operator-config predicate**. Impl-discretion: expose an opt-in per-workload-class surface, default 5m (byte-identical to today). Choice recorded in §4.2.
- **R2 — keep-alive under cost pressure.** The flat "every 4min" does not cover a C11 skip-under-ceiling-pressure carve-out. `[SPECULATIVE]` This lives with the **pre-warm/keep-alive mechanism (3c-adjacent)**, which is deferred — so R2 is deferred with it, not decided here. The C11-safe default when keep-alive is built: **opt-in, default off**.

**Council verdict: probe-resolved. No convening.** `[[probe-resolves-fork-prescribed-council]]`.

---

## 4. The cacheable-epoch primitive design

### 4.1 Epoch key (the committed keying, cache-correct)

`[HIGH]` `cacheable_epoch = (agent_role, workload_class) × prefix_content_hash`, where `prefix_content_hash = sha256(canonical(frozen_tool_superset) ‖ active_prompt_version.version_sha)`. Byte-exact ⇒ two dispatches share a warm cache **iff** their `[tools + system]` prefixes are byte-identical. Invalidation is automatic: any content change → new `version_sha` → new epoch → clean cache miss (never the silent zero-cache failure mode — ADR-F2 §(b)(ii)). Extended-thinking mode is committed per epoch (ADR-D3 §1.5 line 205; already gated at the slice-1/2 marker).

### 4.2 ttl selection (the buildable-now half; ADR-D3 §1.5 line 188)

`[HIGH]` `select_cache_ttl(workload_class, config) → "5m" | "1h"`. Default `"5m"` for every workload-class (byte-identical to today). Operator opt-in surface (R1): a RuntimeConfig field naming the workload-classes that use the 1hr tier (their "cost-ceiling cells"). Bound onto `RuntimeLLMDispatcher.cache_ttl` at stage 5 (run-scoped constant, the `frozen_tool_superset` precedent), consumed at the translate seam replacing the hardcoded `{"ttl": "5m"}`.

### 4.3 Keep-alive / pre-warm (deferred with 3c)

`[MODERATE]` `pre_warm: max_tokens=0 at boot; keep-alive every 4min` (ADR-D3 §1.5 lines 189-190) is a distinct mechanism whose consumer is the fan-out pre-warm cohort (3c). Deferred (§5). C11-safe default when built: opt-in, default off (R2).

---

## 5. Build decomposition + lane split

| Unit | What | Consumer | Blast radius | Disposition |
|---|---|---|---|---|
| **3b-ttl** | workload-class-aware cache ttl (5m/1h); `RuntimeLLMDispatcher.cache_ttl` bound at stage 5; opt-in RuntimeConfig field | the translate seam (live — replaces hardcoded 5m) | **low** (defaulted byte-identical; no fan-out) | **BUILD THIS SESSION** |
| **3b-epochkey** | the version_sha-keyed cohort identity (§4.1) | the fan-out pre-warm (3c) ONLY | n/a standalone (hollow without 3c) | **DEFER + register** (build with 3c) |
| **3c-prewarm** | ADR-D4 §1.8 concurrent-cache pre-warm: serialize `branch[0]` to completion, release `branch[1..N-1]` | fan-out driver | **HIGH** (fan-out concurrency change; composes with B-FANOUT effect-fence / cascade / drain / crash-resume) | **DEFER + register** (dedicated session, guardrails per findings §Correction) |
| **Lane-B semantic-major** | add an operator-declared semantic-version field to `PromptVersion` (skill `frontmatter.version` analogue) | migration-tracking / lifecycle only | IS-spec touch | **DEFER + register** (IS-spec amendment; NOT required — version_sha is the cache key) |

**Why 3b-ttl standalone is non-hollow but 3b-epochkey standalone is hollow:** ttl-selection keys on `workload_class` and has a LIVE consumer (the translate seam's ttl value). The version_sha cohort identity keys the *pre-warm cohort* and has NO consumer until 3c ships — building it now would be a producer-without-consumer (`[[r-cxa-seam-wiring-is-producer-discovery]]`: DEFER-don't-wire when hollow).

---

## 6. Forward-arc registration (SPINE ledger `B-*`)

- **`B-18-EPOCH-PARTITION`** — RESHAPED. The ttl half ships this session (3b-ttl); the residual = **3b-epochkey** (version_sha cohort identity, §4.1), which ships coupled with 3c (its only consumer).
- **`B-18-3C-PREWARM`** — unchanged; the high-blast-radius fan-out pre-warm; dedicated session; build-guardrails at `u1-slice3-findings-and-f1-c10-gap.md` §Correction (opt-in gate on `frozen_tool_superset is not None` ∧ fan-out cap > 1 ∧ same-prefix; await `branch[0]` to completion — no Anthropic cache-ack signal; same-epoch-sibling witness).
- **`B-18-LANEB-PROMPT-SEMVER`** — NEW. Add an operator-declared semantic-version field to `PromptVersion` (skill `frontmatter.version` analogue, ADR-D3 §1.8.1). IS-spec amendment (bundled-absorption, clearance marker). Optional (migration-tracking); NOT a cache-correctness dependency.
- **`B-18-CACHE-TTL-OBSERVABILITY`** — NEW, **decorrelation-validated** (both the advisor and out-of-family Codex [P2] converged on it during the 3b-ttl review). `_extract_anthropic_cache_request_attrs` scans only `payload.messages`, so the tools/system-block `cache_control` breakpoint's `anthropic.cache_ttl_seconds` is unrecorded. This is **pre-existing** — slices 1/2/3a's 5m marker is equally unobserved (the marker lives on the *translated kwargs*, not the frozen `payload`) — but 3b makes it higher-value: the ttl now *varies for cost control*, so the operator has no direct `cache_ttl_seconds` signal that 1h took effect (the *effect* is still observable via `anthropic.cache_read/creation_input_tokens`). Fix = thread the placed-marker ttl from the translate seam to `_anthropic_response_bundle`, closing it uniformly for slices 1/2/3a/3b. A shared response-bundle-path refactor → its own arc, NOT folded into 3b-ttl (surgical discipline; wire behavior is correct so it does not block).

---

## 7. What this session ships

3b-ttl as a **bundled-absorption arc** (the slice-1/2/3a cadence): runtime spec v1.96 → v1.97 (materializes ADR-D3 §1.5 line 188 ttl-selection) + clearance marker + impl + tests + decorrelated review (advisor + `just codex-review`). IS / CP / OD / AS / ADR / CXA specs UNCHANGED. `ProviderAgnosticPayload` stays FROZEN (ADR-F1); OpenAI/Ollama translators UNCHANGED; default `"5m"` → byte-identical to pre-3b-ttl.
