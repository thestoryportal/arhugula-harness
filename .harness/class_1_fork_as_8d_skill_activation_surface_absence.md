# Class 1 Fork — H_T-AS-8d `skill.*` namespace producer-site absence + activation-surface design gap

**Status:** ✅ FULLY-APPLIED (apply arc landed same-session 2026-05-28 in 3 commits: 471e0e2 spec+plan + 83251b2 impl+tests + this commit doc-update; H_T-AS-8d STILL-BOUNDED → RETIRE-READY)

**Operator ratification (2026-05-28):**

| Q | Answer | Note |
|---|---|---|
| Q1 | **(B) IN-SCOPE-MVP** | schema-stub + operator-opt-in emission; mirrors CP-18/CP-21/CP-22 RETIRE-READY pattern; transits AS-8d STILL-BOUNDED → RETIRE-READY at apply arc close |
| Q2 | **(d) HYBRID all 3 hooks** | per-LLM-dispatch + per-workflow-init + operator-explicit; `activation_mode` enum discriminates which fired. Most faithful to AS spec §14.4 3-value enum intent; preserves Claude Code taxonomy verbatim under Q3=(i) by mapping each hook to one enum value descriptively: per-LLM-dispatch → `tool_search`; per-workflow-init → `frontmatter_only`; operator-explicit → `filesystem_read` |
| Q3 | **(i) PRESERVE** | AS spec §14.4 enum values preserved verbatim; runtime spec extension documents the H_T-runtime mapping per Q2=(d) hook-to-enum-value assignment |
| Q4 | **(q) NEW module** | `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py` per Memory-tool precedent |
| Q5 | **(β) NO new CXA edge** | CXA v2.15 unchanged; OD §C-OD-08 already declares cross-namespace ingestion |

**Apply-arc scope refinement (per Q2=(d) hybrid):** 3 hook binding sites raise the apply-arc cost estimate from the §3 Q1=B baseline (~3-5 commits) to ~5-7 commits. Each hook is its own binding site (per-LLM-dispatch at `lifecycle/llm_dispatch.py`; per-workflow-init at workflow startup composer; operator-explicit at `ctx.activate_skill` surface).

**Filed at:** 2026-05-28

**Filer:** spec-writer skill (FM-1 trigger at AS-8d gate-text re-verification)

**Surfaced by:** Empirical re-verification of H_T-AS-8d retirement gate at `harness-as/CLAUDE.md` per advisor pre-substantive consultation (24th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]`).

**Classification:** Class 1 (halt-execution; design extension surfaced at Phase 7 execution per X-AL-3 + Workflow v1.10 §2.7.6 + Phase_7_Kickoff_Prompt.md §6).

---

## §1 — The gap

AS spec C-AS-14 §14.4 declares a 6-attribute `skill.*` namespace on a `skill.activation` span:

| Attribute | Type | Semantic |
|---|---|---|
| `skill.id` | string | Canonical Skill identifier |
| `skill.name` | string | SKILL.md frontmatter `name` |
| `skill.version_sha` | string (hex) | Git content hash (replay-determinism anchor) |
| `skill.frontmatter.version` | string | SKILL.md frontmatter `version` (migration-tracking) |
| `skill.body_tokens` | int | Cost attribution |
| `skill.activation_mode` | enum string | `frontmatter_only` / `tool_search` / `filesystem_read` |

AS-side schema substrate LANDED at U-AS-31 (`SKILL_NAMESPACE_SCHEMA` carrier + `validate_skill_attributes_carry_both_version_fields` enforcement at `harness-as/src/harness_as/anthropic_attribute_namespaces.py:178`). Sampling policy LANDED at U-AS-32 (`AuditFloorScope.SKILL_ACTIVATION_DESIGN_TIME_ALWAYS_SAMPLED` at `harness-as/src/harness_as/anthropic_primitive_sampling.py:82`).

**Gap 1 — no producer site.** `grep -rn "skill.activation" harness-runtime/src/` returns ZERO span emission. `harness-runtime/src/harness_runtime/lifecycle/skills.py` (U-RT-13 loader) populates `ctx.skills: dict[SkillID, Skill]` at stage-2 but never emits a `skill.activation` span.

**Gap 2 — 3-of-6 attributes uncomputed at load.** `SkillManifest` at `harness-runtime/src/harness_runtime/lifecycle/skills.py:39` carries 4 fields (`skill_id` / `name` / `description` / `version`):
- `skill.id` ≈ `skill_id` ✓
- `skill.name` ≈ `name` ✓
- `skill.frontmatter.version` ≈ `version` ✓
- `skill.version_sha` ✗ (git content hash; not computed)
- `skill.body_tokens` ✗ (int; not computed)
- `skill.activation_mode` ✗ (enum; not stored)

**Gap 3 — no activation event at H_T runtime.** `ctx.skills` is populated; nothing in the codebase invokes a loaded Skill. The runtime LLM dispatch path (`harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py`) does NOT reference `ctx.skills`. No callsite in `harness-runtime/` reads from `ctx.skills` after load. Skills load and sit dormant.

**Gap 4 — `activation_mode` enum vocabulary is Claude Code taxonomy.** The 3 enum values (`frontmatter_only` / `tool_search` / `filesystem_read`) describe Claude Code's Skill activation discriminators. H_T runtime has no analog — no tool-search loop; no frontmatter-driven dispatch; no programmatic Skill invocation surface.

Net consequence: **H_T cannot emit `skill.activation` spans because H_T has no concept of activating a Skill at runtime.** The producer-side is absent not because the carrier is unauthored but because the *event* is undefined.

---

## §2 — Three readings

**Reading A — IN-SCOPE-NOW: full activation surface + producer site at this fork's apply arc.** Author Skills loading runtime composer extension + activation event + `SkillActivationSpanEmitter` carrier; emit `skill.activation` span at activation site; compute `version_sha` at load; compute `body_tokens` at load; pin `activation_mode` taxonomy at H_T-runtime-canonical values.

Pros: closes AS-8d STILL-BOUNDED → RETIRED in one cascade. Closes the spec's §14.4 producer-side declaration without carry-text staleness.

Cons: requires resolution of "what activates a Skill at H_T?" — the harder of the 4 gaps. The Claude Code 3-enum taxonomy doesn't transplant. Authoring a new activation surface at H_T is a genuine design extension scope.

Estimated cost: ~5-8 commits including runtime spec extension (new C-RT-NN contract for activation surface) + runtime plan extension (new L-N cluster) + AS spec §14.4 amendment (re-anchor `activation_mode` enum to H_T-canonical taxonomy if Claude Code values don't apply) + production binding + tests.

**Reading B — IN-SCOPE-MVP: schema-stub + emission gated on operator config (mirror of CP-18 / CP-21 / CP-22 operator-opt-in shape).** Author the loader extension (compute `version_sha` + `body_tokens` at load; store `activation_mode` per a NEW H_T-runtime enum); author the `SkillActivationSpanEmitter` carrier; bind emission at a NEW operator-config-gated activation event (e.g., `RuntimeConfig.skill_activation_hook: SkillActivationHook | None = None` — default None = no activation, no emission). Operator opt-in turns it on.

Pros: discipline-pure under X-AL-3 (config-gated landing = no silent design extension). Matches CP-18/CP-21/CP-22 RETIRE-READY pattern (carrier MET; emission MET-when-operator-binds).

Cons: AS-8d transits PARTIAL → RETIRE-READY at best; cannot achieve RETIRED at this fork's close. Defers the harder "what is activation at H_T?" question.

Estimated cost: ~3-5 commits per gate-text estimate. Mirrors L9-decies / L9-undecies / L9-quaterdecies binding-chain cluster shape.

**Reading C — DEFER INDEFINITELY (mirror of H_T-AS-8e `files.*` per runtime spec v1.17 §14.C).** Mark AS-8d as STILL-BOUNDED-INDEFINITELY per X-AL-2 bounded-residual; document the activation-surface design gap as pre-scope; route resolution to a future H_T design extension arc at operator-discretion timing (post-bootstrap; post-MVP).

Pros: discipline-pure under X-AL-3 (no Phase-7-time design extension). Defers a 5-8-commit arc that doesn't gate any other unit; AS-8d has no downstream consumer. Matches the AS-8e precedent for "carrier-substrate-MET; activation-surface-design-gated".

Cons: AS-axis 8/11 RETIRED ceiling at active-substitution view (AS-8d remains in STILL-BOUNDED bucket alongside AS-8e + AS-8f).

Estimated cost: ~1 commit — STILL-BOUNDED → STILL-BOUNDED-INDEFINITELY row refresh at `harness-as/CLAUDE.md` + AS spec v1.7 §14.4 footer note + cross-artifact cite refresh.

---

## §3 — Operator decisions

**Q1 — Scope reading.**

- (A) IN-SCOPE-NOW full activation surface
- (B) IN-SCOPE-MVP schema-stub + operator-opt-in emission (RECOMMENDED — mirrors CP-18/CP-21/CP-22 precedent; discipline-pure under X-AL-3; transits AS-8d → RETIRE-READY)
- (C) DEFER INDEFINITELY (mirror AS-8e files.* precedent)

**Q2 — Activation-surface design (IF Q1=A or B).** What event constitutes "Skill activation" at H_T runtime?

- (a) Per-LLM-dispatch hook — emit `skill.activation` before each `llm_dispatch.py` call, one span per activated Skill loaded into prompt context. `activation_mode` taxonomy re-anchored to H_T-canonical values (e.g., `prompt_inclusion` / `tool_match` / `explicit_invocation`).
- (b) Per-workflow-init hook — emit `skill.activation` once per loaded Skill at workflow startup if any pre-condition matches. Activation = "Skill enters scope for this workflow."
- (c) Operator-explicit registration — emit only when operator calls a NEW `ctx.activate_skill(skill_id)` surface explicitly. No automatic activation. (RECOMMENDED — lowest design-extension surface; operator authors activation policy; H_T provides the emission carrier only.)
- (d) Hybrid — author all 3 hooks; `activation_mode` enum discriminates which fired. Most faithful to the AS spec §14.4 3-value enum intent (if the spec preserves the Claude Code taxonomy semantically).

**Q3 — AS spec §14.4 `activation_mode` enum disposition (IF Q1=A or B).**

- (i) PRESERVE VERBATIM Claude Code taxonomy values (`frontmatter_only` / `tool_search` / `filesystem_read`); document the semantic re-anchoring at the runtime spec extension (these values describe Claude Code activation discriminators but H_T uses them descriptively per author intent). (RECOMMENDED if Q1=B + Q2=c — minimum-spec-surface posture.)
- (ii) AMEND AS spec §14.4 enum at this fork's apply arc to H_T-canonical taxonomy (e.g., `prompt_inclusion` / `tool_match` / `explicit_invocation` per Q2(d)). Re-anchors the spec to H_T semantics.
- (iii) PRESERVE per Reading C (no amendment if Q1=C).

**Q4 — Loader+emitter residence (IF Q1=A or B).**

- (p) Extend existing `harness-runtime/src/harness_runtime/lifecycle/skills.py` (U-RT-13 module) with activation event + emitter. Loader-and-emitter co-residence.
- (q) NEW module `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py` per Memory-tool precedent (`memory_tool_dispatch.py` is a separate module from any Memory loader). Loader-vs-activation separation. (RECOMMENDED — matches Memory-tool precedent.)

**Q5 — Cross-axis cascade (IF Q1=A or B).** New CXA seam edges expected:

- (α) `harness-runtime` (activation event) → `harness-od` (`SKILL_NAMESPACE_SCHEMA` consumer for ingestion at OD §C-OD-08 §8.4 cross-namespace ingestion table). Symmetric to existing `mcp.*` / `memory.*` namespace ingestion seams.
- (β) NO new edge — spec-level ingestion is already implicit at OD §C-OD-08 since the AS-side carrier (`SKILL_NAMESPACE_SCHEMA`) is canonical reference; runtime emission is producer-side, OD ingestion is consumer-side, both already declared. (RECOMMENDED — no cascade verified empirically.)

**Recommendations (advisor-blessed):** Q1 = **B** (IN-SCOPE-MVP); Q2 = **(c)** operator-explicit; Q3 = **(i)** preserve verbatim; Q4 = **(q)** NEW module per Memory-tool precedent; Q5 = **(β)** no new edge.

---

## §4 — Downstream cascade

### IF Q1 = A or B selected

**Spec amendments:**
- Runtime spec v1.31 → v1.32 — NEW §14.NN C-RT-NN `SkillActivationSpanEmitter` contract surface + activation-event Protocol declaration. Sibling to §14.12 C-RT-22 (`MemoryToolRegistry`) Memory-tool precedent.
- Runtime spec — NEW field `RuntimeConfig.skill_activation_hook: SkillActivationHook | None = None` at §3 C-RT-02.
- Runtime spec — NEW field `HarnessContext.skill_activation_emitter: SkillActivationSpanEmitter | None` at §4 C-RT-04.
- AS spec v1.7 — §14.4 footer note documenting H_T-runtime activation surface + Reading-canonical `activation_mode` taxonomy (per Q3).

**Plan amendments:**
- Runtime plan v2.27 → v2.28 — NEW L-N cluster (~3-5 atomic units per Q4) decomposing the C-RT-NN landing.
- AS plan v1.4 — §0 change-note absorbing AS spec §14.4 footer note (no new AC).

**Production binding:**
- `harness-runtime/src/harness_runtime/lifecycle/skills.py` (U-RT-13) — EXTEND with `version_sha` + `body_tokens` + `activation_mode` computation at load.
- NEW `harness-runtime/src/harness_runtime/lifecycle/skill_activation.py` (per Q4=q) — `SkillActivationSpanEmitter` class + activation Protocol + emit method.
- Stage-N factory at `harness-runtime/src/harness_runtime/bootstrap/` — `materialize_skill_activation_emitter_stage`.
- Operator-config-gated activation surface (per Q1=B + Q2=c) — `ctx.activate_skill(skill_id, mode)` method or equivalent.

**Cross-axis cascade:**
- Q5 = β (advisor recommendation): NO new CXA edge; CXA v2.15 unchanged.
- Q5 = α (alternative): CXA v2.15 → v2.16 — NEW §2.3.x row at the AS→OD bucket or OD→AS bucket per directional convention.

**Retirement gate transit:**
- AS-8d STILL-BOUNDED → RETIRE-READY at apply-arc close (Q1=B; operator-opt-in shape with carrier MET + emission MET-when-bound).
- AS-8d STILL-BOUNDED → RETIRED at apply-arc close (Q1=A; full activation surface + producer site + emission verified).

### IF Q1 = C selected

**Spec amendments:**
- AS spec v1.7 — §14.4 footer note documenting H_T-runtime activation-surface design gap + STILL-BOUNDED-INDEFINITELY routing per X-AL-2 bounded-residual.
- Runtime spec — NO amendment.

**Plan amendments:**
- AS plan v1.4 — §0 change-note absorbing AS spec §14.4 footer note (no new AC).
- Runtime plan — NO amendment.

**Production binding:**
- NONE.

**Cross-axis cascade:**
- NONE.

**Retirement gate transit:**
- AS-8d STILL-BOUNDED → STILL-BOUNDED-INDEFINITELY.
- AS-axis active-substitution view: 8/10 RETIRED (80.0%) preserved; AS-8d joins AS-8e in the INDEFINITE bucket.

---

## §5 — Pattern catalogued

Same shape as `class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` (Memory tool, 2026-05-23):

- AS-side schema substrate LANDED.
- Runtime activation surface ABSENT.
- Producer-binding chain not yet authored.
- Fork doc filed at Phase 7 execution time per X-AL-3 (no silent design extension).
- Operator ratifies scope (A/B/C); apply arc lands per ratification.

Pattern name candidate: **executable-consumer-absence at AS-emission-namespace**. Distinct from `executable-consumer-absence at runtime-Protocol-binding` (Memory tool was Protocol-binding; this is namespace-emission). Both share the "schema-substrate-MET + runtime-activation-surface-ABSENT" structural form.

**Distinctive feature of AS-8d:** `activation_mode` enum at AS spec §14.4 declares Claude Code taxonomy values that may not map cleanly to H_T runtime. Q3 surfaces whether the spec amendment is owed at apply-arc to re-anchor the taxonomy. (Memory tool had no such taxonomy-divergence issue.)

---

## §6 — Filing footer

| Field | Value |
|---|---|
| Filed at | 2026-05-28 |
| Filer | spec-writer skill (FM-1 trigger at AS-8d gate-text re-verification) |
| Source of detection | Empirical re-verification of H_T-AS-8d retirement gate at `harness-as/CLAUDE.md` post-OD-5 verdict (C); 24th application of `[[advisor-before-substantive-work-for-cross-axis-blockers]]` |
| Classification | Class 1 (halt-execution; design extension surfaced at Phase 7 execution per X-AL-3 + Workflow v1.10 §2.7.6) |
| Ratification owed | Operator AskUserQuestion at fork doc close — Q1 + (Q2/Q3/Q4/Q5 if Q1=A or B) |
| Apply-arc shape | Fresh-session per advisor pre-substantive consultation (3-5 commits at Q1=B; 5-8 commits at Q1=A; 1 commit at Q1=C) |
| Status | PROPOSING |
