# Checkpoint — R-700-closure-accounting-draft (resume artifact)

> **READ THIS FIRST; DO NOT RE-DERIVE.** This checkpoint was authored at the end of a session (2026-06-01) immediately before a `/clear`. The operator asked for two deliverables (below) and explicitly said: *"Before you continue with this work I will need to clear this session for a fresh one. Ensure all context is landed before clear so we pick up seamlessly."* So the prior session deliberately did **not** start the drafting — it landed this checkpoint instead. Your job on resume: produce the two deliverables per the spec below. Posture: **mode-agnostic** (process-substrate compilation; reads `design-substrate/` + `harness-*/CLAUDE.md` + `.harness/` but authors only `.harness/` output + roadmap/dashboard). NOT a design-substrate amendment (no X-AL-3 / clearance-marker owed unless you choose to amend a spec).

---

## The task (operator request, verbatim intent)

Draft a **definitive remaining-to-full-harness-closure log**, in two parts:

**Part A — the substitution closure log (= draft `R-700` Phase-8 substitution-accounting).** A single table enumerating **all 54 raw-ledger substitution rows** with, per row: substitution ID + name + axis + current tier + closing batch (if closed) + disposition class (substantive-RETIRED / RETIRED-AS-AUTHORING-ONLY / RETIRED-AS-BOUNDED-RESIDUAL / PARTIAL / STILL-BOUNDED-INDEFINITELY). This is the comprehensive accounting that does **not yet exist as a single artifact** — compiling it IS the Claude-executable draft of the `R-700` deliverable (the operator still owns the final Phase-8 review/ratification).

**Part B — all remainings BEYOND substitutions.** A register of the infra-gated Surface-V entries (`R-410..R-440`) **plus** `R-100-mvp-config-discovery`. Operator asked for: **a summary AND details for each, referencing how each has been spec'd** — in terms of **vendor, the user-persona-level / deployment-surface it executes at, the spec/ADR cites**, and Claude-executable-vs-infra-gated status.

Suggested output: ONE file `.harness/R-700-phase-8-closure-accounting-draft.md` with Part A + Part B (your judgment on splitting into two sibling files is fine). Then RESOLVE this entry + update the dashboard.

---

## RESOLVED FACTS from the prior session (verified at HEAD `aff487e8` / post-PR-#204; do not re-derive)

### Current closure state
- **48/54 RETIRED (88.9%)**; **pipeline-advanced 49/54 (90.7%)** per `.harness/phase-7d-retirement-ledger-v2.md` §11.5 (latest batch = **batch-51**).
- **Only 3 NON-RETIRED rows surface in the live per-axis `§4.1`** (grepped this session):
  1. **H_T-OD-4** (Pre-Collector redaction SpanProcessor) — **PARTIAL (refined)** → roadmap **R-008**. The ONE genuinely-open substitution. Needs §13.1 per-session redaction toggle (session-control substrate) + §13.2 opaque-token tokenization.
  2. **H_T-AS-8e** (files.* namespace) — **STILL-BOUNDED-INDEFINITELY** → **R-005**. Deferred-by-design (runtime spec v1.17 §14.C Memory-only MVP scope); closes bounded-residual at Phase 8.
  3. **H_T-AS-8f** (managed_agents.* namespace) — **STILL-BOUNDED-INDEFINITELY** → **R-006**. Deferred-by-design (`class_1_fork_as_8f_...` Q1=(C)); closes bounded-residual at Phase 8.
- IS = 9/9 RETIRED; CP = all RETIRED/authoring/bounded (0 open rows; ledger says "21/22"); OD = 7/8 (OD-4 the lone PARTIAL).

### ⚠️ Arithmetic gap to RESOLVE in Part A (the real work)
48 RETIRED + 3 open (OD-4, AS-8e, AS-8f) = 51, but the denominator is **54** → **~3 rows are unaccounted in the per-axis §4.1 view**. They are almost certainly: **CXA's 5 substitutions** (Meta-Arch §5.6 — `harness-cxa/` has **NO** `CLAUDE.md §4.1` file, so CXA substitution status is NOT in the per-axis surface; check the ledger + Meta-Arch §5.6) **+ authoring-only/bounded tail rows** + the CP "21/22" extra row. **Part A must reconcile all 54 rows to exactly 48 RETIRED + 6 non-RETIRED (or correct the count).** This reconciliation is precisely why the comprehensive log doesn't exist yet.

### Authoritative sources (grep these — they ARE the log inputs)
1. **Per-axis `§4.1`** (live truth): `harness-{is,as,cp,od}/CLAUDE.md` §4.1 substitution tables.
2. **Retirement ledger** (cumulative + forward-only supersession): `.harness/phase-7d-retirement-ledger-v2.md` §11 (+ §4 for the runtime-only reading) + the per-batch records `.harness/phase-7d-retirement-events-batch-{1..51}.md`.
3. **Meta-Arch §5** (the canonical 49-row → 54-decomposed substitution map): `design-substrate/Phase_7_Meta_Architecture_v1.md` §5.2 IS / §5.3 AS / §5.4 CP / §5.5 OD / §5.6 CXA. (Note: AS-8 monolithic decomposed into 6 sub-rows AS-8a..8f at batch-24, taking the raw count 49 → 54.)
4. **Roadmap** `Project_Roadmap_v1.md` §5 + `.harness/roadmap_status.md` — R-NNN work-item layer + R-700 gate.

### What this session already landed (context — do NOT redo)
- **R-007 + R-009 RESOLVED** at batch-51 (PR #200): H_T-OD-3 substantive RETIRED (gate-text-stale audit) + H_T-OD-6 RETIRED-AS-BOUNDED-RESIDUAL (FIRST bounded-residual close in ledger). See `.harness/phase-7d-retirement-events-batch-51.md` + ledger §11.4i/§11.4j + memory `[[r-007-r-009-od-retirement-condition-b-discriminator]]`.
- **R-600-workflow-v1-14-amendment RESOLVED** (PR #201): NEW §7.5 process-discipline catalogue. must_pass[1] N/A operator-ratified (PR #203).
- Dashboard refreshed (PRs #202 + #204).

---

## Part B captured data (verified from roadmap §5 this session — enrich with the cited specs on resume)

The 12-cell **`deployment_matrix.py`** = persona_tier × deployment_surface; sandbox provider-class maps per cell. Grep `deployment_matrix.py` + **ADR-D2** (graduated-isolation / per-deployment-surface sandbox provider) + **ADR-F4** (4-tier blast-radius) + **ADR-F5** (tier-aware secret-fetch) + **C-AS-15 §15** (sandbox tier schema) for the precise per-cell mapping the deliverable needs.

| Entry | Status | Vendor / mechanism class | Surface / persona | Spec cites | Notes |
|---|---|---|---|---|---|
| **R-410** TIER_2_CONTAINER exec | PROPOSED (live/infra-gated) | real container runtime (Docker/Podman/runc-class) | ≥ LOCAL/SELF_HOSTED per matrix | C-AS-15 §15; runtime spec v1.41 §14.9.8 (sandbox-decision-resolver, no C-RT-NN) | **The honest heart of Surface V.** At HEAD sandbox tier/provider are observability+policy annotations ONLY — `mcp_client_host.call_tool` always uses in-process FastMCP stdio regardless of tier. Almost certainly opens a Class 1 fork: the execution-driver contract (resolved-tier → actual sandbox mechanism) is unspecified beyond the §14.9.8 resolver. |
| **R-411** TIER_3 microVM exec | PROPOSED (infra-gated); dep R-410 | gVisor / Kata / shared-kernel container | per matrix | C-AS-15 §15 | EXTERNAL_REVERSIBLE blast-radius. |
| **R-412** TIER_4 full-VM exec | PROPOSED (infra-gated); dep R-411 + R-421 | firecracker / full-VM | **MANAGED_CLOUD-only** per deployment_matrix.py | C-AS-15 §15 | FULL_VM reserved exclusively for MANAGED_CLOUD; EXTERNAL_IRREVERSIBLE; deferred-far per ADR-D2. |
| **R-420** SELF_HOSTED_SERVER e2e | PROPOSED (operator/infra-gated) | real long-running server + real OTLP collector + tier secrets backend | **SELF_HOSTED_SERVER** | C-RT-29 §14.18 (daemon mode, FastMCP Unix-socket); C-OD-09 §9.1 | First real non-LOCAL surface; unblocks R-430 + R-440. Operator provisions server+collector+secrets. |
| **R-421** MANAGED_CLOUD e2e | PROPOSED (operator/infra-gated); dep R-420 | cloud env + cloud secrets + FULL_VM + managed collector | **MANAGED_CLOUD** | C-RT-29 §14.18; C-OD-13 §13.1 | Secrets via in-sandbox encrypted-fs per ADR-F5; MANAGED_CLOUD per-cell sampler + redaction posture. |
| **R-430** OTLP tail-keep preservation | PROPOSED (infra-gated); dep R-420 | real OTLP collector | SELF_HOSTED+ | C-OD-09 §9.1, §9.2 | TailKeepSpanProcessor buffer logic exists; the drop/keep preservation semantic is **collector-side** (needs a real collector to verify classification-trigger preservation). |
| **R-440** tier-level secrets backend | PROPOSED (infra-gated); dep R-420 | Vault / cloud secrets manager | SELF_HOSTED (tier-level) vs MANAGED_CLOUD (in-sandbox) | ADR-F5 §1; C-AS-05 §5.1 `fetch_secret` | At HEAD `provider_secrets.py` documents tier-level vs in-sandbox backends but ships ONLY LOCAL keyring + env-fallback (PR #16 binding-fix). Mirror precedent `[[pr-16-keyring-env-fallback-adr-f5]]`. |
| **R-100-mvp-config-discovery** | BLOCKED | n/a (CLI config-load) | LOCAL (SOLO_DEVELOPER) | C-RT-30 §3.7 (line 391); C-RT-29 §14.18.1 | BLOCKED on `.harness/class_1_fork_harness_toml_default_discovery_unimplemented.md` (PROPOSING). Spec declares `harness.toml` discovered at workspace root "by default"; impl never wired it — `DEFAULT_CONFIG_FILE_NAME` (config_source.py:43) is a dead constant. "Workspace root" undefined (CWD vs config's own repository_root — circular). Fork readings: (A) CWD discovery / (B) upward search / (C) spec amendment dropping the clause. Worked around in R-100 via `just run` passing `--config`. **Does NOT block the MVP.** Needs operator fork-ratification. |

**For Part B the operator wants per-entry: summary + details (vendor, persona/surface level, spec cites).** The table above is the spine; on resume, read the full roadmap §5 entries + the cited spec/ADR sections to flesh out each with the precise vendor options + the deployment_matrix.py per-cell persona×surface mapping.

---

## On-resume procedure
1. Read this checkpoint (done).
2. Run the §12.1 session-start audit (the SessionStart hook fires it). Expect MATCH (the prior session left a terminating refresh; lag-by-one carve-out).
3. Produce Part A: grep the 4 authoritative sources, compile the 54-row table, **reconcile the arithmetic gap** (CXA 5 + CP-22 + authoring/bounded tail → exactly 48 RETIRED + 6 non-RETIRED, or correct).
4. Produce Part B: the 8-entry register above, fleshed with spec/ADR/deployment_matrix detail.
5. Write `.harness/R-700-phase-8-closure-accounting-draft.md`; consider an `advisor()` pass before declaring done (verify the 54-row reconciliation is sound — the arithmetic gap is the main correctness risk).
6. RESOLVE `R-700-closure-accounting-draft` in the roadmap; remove this checkpoint's `resume:` pointer; refresh the dashboard (terminating refresh).
7. The DRAFT feeds `R-700-phase-8-substitution-accounting` (still BLOCKED — operator owns the final Phase-8 review/ratification + the bounded-residual sign-offs for AS-8e/AS-8f/OD-6).
