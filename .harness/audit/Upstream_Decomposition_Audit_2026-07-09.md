# Upstream Decomposition-Completeness Audit — 2026-07-09

**Companion to** `Spec_Implementation_Gap_Audit_2026-07-09.md` (which ran spec→code). This audit runs the **other, higher-leverage direction — design-intent → spec decomposition** — the exact seam the memory-substrate gap lived in and that a spec→code audit is structurally blind to.

**Commissioned by** operator question (2026-07-09): the prior audit compared spec→code; did anything compare the *initial* docs (PRD/ADR/ADD + the design-phase council + the `01-planning` research substrate) against the specs, to surface capabilities that were **committed in intent but silently narrowed in the spec**? (That is how the memory gap surfaced: a committed provider-neutral memory *direction* narrowed to the thin `C-RT-22` Anthropic callback; spec→code saw C-RT-22 built and passed.) Answer: no — this audit closes that gap.

**Operator directive folded in:** "There is no MVP scoping. All beyond-MVP are to be spec'd and built." So a *documented* deferral is not an acceptable resting state — every committed-but-deferred capability is a build target. Only capabilities the research raised but **no ADR/ADD/PRD ever committed** (or an ADR *rejected*) are excluded ("HOW stays committed ADRs", I-6/ADR-F1).

---

## 1. Method

Genuine council-engaged, semantic (not mechanical). For each harness domain, the owning **council voice** (a dedicated agent adopting its `.claude/skills/council/cN/SKILL.md`) compared its domain's **upstream committed intent** — its `01-planning` research cluster + the ADR/ADD/PRD commitments — against the **spec/plan decomposition**, and classified every candidate capability:

- **FULLY_REALIZED** — spec captures the committed intent.
- **SILENT_NARROWING** — intent commits X, spec ships x′, and **nothing in the authority chain or `.harness/` acknowledges it** (the memory class — the prize). Confirmed by an **acknowledgment-grep** (empty = silent).
- **DOCUMENTED_DEFERRAL** — the narrowing IS acknowledged (fork / register / spine-ledger / spec-OQ). Under FULL-SPEC still a build target.
- **EXPLORED_NOT_COMMITTED** — research raised it, no ADR/ADD/PRD committed it (or an ADR rejected it). **Excluded** (re-litigation, foreclosed).

**Calibration:** C3 (state/memory/persistence — the memory voice) was run first as a **positive control**. It correctly did *not* flag memory as an open gap now (built out as C-MEM-02..20 + acknowledged by the fork) yet articulated why the pre-C-MEM state *would* have been SILENT_NARROWING — proving the criterion has the sensitivity that would have caught memory. It discharged the research-noise correctly (e.g. "vector-store as canonical memory" → EXPLORED_NOT_COMMITTED because ADR-D7 Alternative 3 explicitly rejects it). Criterion calibrated → the other 10 voices (C1/C2/C4–C11) fanned out. Every SILENT_NARROWING flag was then **adversarially refuted** (a second agent tries to find the acknowledgment / cross-axis realization / non-commitment) before counting.

11 domains total (C3 pilot + 10 fan-out), ~2.1M agent tokens.

---

## 2. Headline result: ZERO silent decomposition gaps

**No SILENT_NARROWING found in any of the 11 domains.** The memory-gap class — a committed capability silently narrowed in the spec with nothing acknowledging it — **does not recur anywhere in the harness.** This is a *stronger* completeness statement than the spec→code audit gave, because it closes the exact seam that swallowed memory: every narrowing that exists is **acknowledged** somewhere in the authority chain / `.harness/`.

Per-voice: all 10 fan-out voices returned empty bucket-1; C3 returned empty bucket-1. The one strong cross-axis lead (C3's trace-context ledger entry-shape extension) resolved to FULLY_REALIZED (decomposed in the OD axis, not IS). Research-noise was cleanly discharged (the criterion did not flood).

---

## 3. 12 DOCUMENTED_DEFERRALS — under FULL-SPEC, build targets

Every narrowing that exists is acknowledged. Under the FULL-SPEC directive each is a build target. Categorized by tracking status (this is the actionable split):

### 3a. NET-NEW — documented but UNREGISTERED (re-grounded by hand) — promote to build arcs

| # | Voice | Capability | Committed at | Deferred at | Registered? |
|---|---|---|---|---|---|
| **U-1** | C2 | **Runtime emission of Anthropic `cache_control` breakpoints** on structured/multi-block system content (the executable half of the ADR-D3 §1.5 "prompt-cache breakpoint placement contract"). The static-prefix/dynamic-suffix *discipline* + the *observation* attrs are built; the harness never AUTHORS a breakpoint (string-only system prompt). | **ADR-D3 §1.5** (committed, item 5 of 9); ADR-F1/F2 "D-ADR on prompt-cache discipline per provider" | Runtime spec §14.5.2:3620-3621 (OQ-1 string-only + OQ-2 perf follow-on) | **NO** — grep of beyond-mvp ledger + arc-ledger + forward register + roadmap = empty. Load-bearing C2 cost lever (cache-miss = 4–10× input-token cost per ADR-F2 §Rationale(b)(ii)). |
| **U-2** | C9 | **Breaker ambient-state attributes `breaker.cause`** (trip-cause enum) **+ `breaker.cooldown_ms`** (cooldown duration) — the *why*/*how-long* of a breaker trip. | CP spec v1 4-attribute `breaker.*` set | CP spec v1→v1.1 change-note (line 72) **"Semantic-loss note"**: dropped when replaced by the OD 7-attribute *event* schema (no direct OD equivalent) | **NO** — grep empty. **Nuance:** line 47 flags re-introduction as **"operator-discretionary, forward-flagged, adjudicated NOT-FINDING at iter-2."** A *conscious* design drop (event-schema vs ambient-state), not an oversight → genuinely a discretionary build call. |

### 3b. Already TRACKED (in the beyond-MVP ledger / arc-ledger / fork docs) — known targets; several built-but-gated

| # | Voice | Capability (committed → narrowed) | Tracking anchor | Status |
|---|---|---|---|---|
| T-1 | C6 | Layered routing **L2 EMBEDDING + L3 LLM_AS_ROUTER** (ADR-F1 three-tier strategy) | Arc R (`r-fs-1-r-routing-intelligence-design-v1.md`; arc-ledger; PR #602/#606) | **BUILT, production-inert until a 2nd provider + routing-activation gate** |
| T-2 | C6 | **Per-agent-role** runtime model dispatch (ADR-F1 §Consequences a) | beyond-mvp ledger row **B4**; frozen order …R→B4→CA… | *(as audited 2026-07-09)* Carried structurally; **runtime-indexing gated to R-300-second-provider** — **superseded, see the 2026-07-27 correction note below** |
| T-3 | C7 | **Production tail-based sampling ENFORCEMENT** (ADR-D6 §1.3 two-posture) | beyond-mvp ledger **B-TAIL-CONDITIONAL-SAMPLING** | Registered forward arc |
| T-4 | C7 | **Cross-family fallback `provider_discriminator` production population** (ADR-D6 §1.2 + ADR-F1) | beyond-mvp ledger **B-FALLBACK-CHAIN-FAMILY-COST-COMPOSITION** | **BUILT 2026-06-18** |
| T-5 | C10 | **Per-MCP-server-trust-tier GATE axis** into the HITL `gate_level()` max() (ADR-D2 §1.5.1 + ADR-D5) | Acknowledged in-spec at AS spec C-AS-10 §10.3 | Spec-acknowledged deferral |
| T-6 | C11 | **Smart-HITL decision intelligence** (conditional gating + palette narrowing + placement matrix; ADR-D5 §1.3) | Arc **B3** (`class_1_fork_b3_1_hitl_auto_approve_policy_field.md`, operator-ratified) | Core-value arc; partially built |
| T-7 | C11 | **HITL timeout-degradation dispatch-on-mode per persona tier** (ADR-D5 §1.6) | fork **F-B3-2**; runtime spec v1.50 change-note | Registered ("fail-open → no tier") |
| T-8 | C11 | **Durable-async EDIT/REJECT resume-response integration** (ADR-D5 §1.1 palette at durable-async cells) | **FM-2 / B-EDIT-CARRIER-DURABLE-ASYNC-RESUME** (runtime spec v1.62) | Registered forward arc |
| T-9 | C11 | **Per-persona-tier audit-ledger cryptographic shape** (append-only→hash-chained→signed; Ed25519 + rotation + F5 secrets; per-persona redaction toggle) | ADR-D5 / Persona tiers; runtime spec | Registered / persona-tier gated |

#### Correction note — 2026-07-27 (row T-2)

This audit is a **frozen point-in-time record dated 2026-07-09**; the original T-2 status text
is preserved above rather than rewritten. T-2's status is **false at HEAD** and is corrected here:

- **Per-agent-role runtime model dispatch is BUILT**, not "gated to `R-300-second-provider`", and
  the gating arc itself (`R-300-multi-llm-second-provider`) **RESOLVED 2026-06-03** (PR #281 + #283).
- **Routing half:** `llm_dispatch.py:1015` resolves `_role = step_context.agent_role or
  _MVP_DEFAULT_AGENT_ROLE`; `:1040` indexes `manifest.per_role_bindings`. The authority site is
  `retry_breaker_fallback.py:743-749`, whose `_effective_chain` per-role branch promotes
  `role_binding.preferred_model_binding` through the U-RT-114 §14.5.3 chain-augmentation.
- **Prompt half:** `prompt_selection.py:245` `resolve_per_role_system_prompts` (docstring:
  "R-FS-1 arc B4 — per-role prompt threading, runtime spec §14.5.3") is bound at
  `stage_0_preamble.py:97` onto `ctx.per_role_system_prompts` and indexed at dispatch on
  `step_context.agent_role`.
- The tracking anchor (beyond-mvp ledger row **B4**) was corrected in the same pass.

The stale claim originated as a carry-text from the PR #509 record and survived into this audit;
it is the `[[stale-carry-text-disposition]]` defect class, not an error in the audit's method.


### 3c. Operator-ratified DEFER — the new directive overrides a prior hold (surface, don't silently reverse)

| # | Voice | Capability | Prior ratification | Tension |
|---|---|---|---|---|
| **R-1** | C11 | **Managed-cloud deployment-surface dispatch** (Persona §9/§10.2 + ADR-D2 §1.1 3-tier surface × blast-radius matrix; the `managed_agents.*` production path) | fork **AS-8f**: **Q1=(C) DEFER INDEFINITELY**, operator-ratified **2026-05-28** | The new "all beyond-MVP spec'd + built" directive **overrides** this prior held decision. Worth explicit confirmation — reversing an operator-ratified hold is the operator's call, not a silent flip. |

---

## 4. Conclusion + what FULL-SPEC implies

**No silent decomposition gaps — the corpus's committed intent is faithfully decomposed, with every narrowing acknowledged.** The memory gap was the *last* of its class; this audit confirms no sibling silent gaps survive.

Under FULL-SPEC, the 12 acknowledged deferrals are all build targets. The actionable structure:
- **U-1 (cache_control breakpoint emission)** — the cleanest net-new build arc: a committed ADR-D3 §1.5 contract, unregistered, real cost lever. Register + build.
- **U-2 (breaker.cause/cooldown_ms)** — net-new but *operator-discretionary* per the design record (a conscious event-vs-ambient schema choice). Surface for the build/skip call.
- **R-1 (managed-cloud dispatch)** — was operator-ratified DEFER-INDEFINITELY; the new directive overrides — confirm.
- **T-1..T-9** — already tracked. Several are **built but gated on a 2nd provider** (Arc R, per-role B4) — an *infra* gate, not a build gap: the code exists; a second provider activates it. The rest (B-TAIL, B3 smart-HITL, F-B3-2, FM-2 EDIT, per-persona crypto) are registered forward arcs to drive under FULL-SPEC.

**Scope honesty:** this is a *semantic* audit — its verdicts are council-voice judgments, adversarially checked for silent-narrowing and hand-re-grounded for the 2 net-new unregistered findings. The 9 tracked items were confirmed present in the ledgers by acknowledgment-grep but not each independently re-built-verified (they carry their own arc records). "Zero silent gaps" is the load-bearing claim and it is strongly supported.

---

*Filed 2026-07-09. Method: council voices C1–C11 (genuine SKILL.md adoption) over `01-planning` corpus + ADR/ADD/PRD vs specs; 3-bucket discriminator + acknowledgment-grep; C3 positive-control calibration; adversarial silent-narrowing refutation. Companion: `Spec_Implementation_Gap_Audit_2026-07-09.md` (spec→code).*
