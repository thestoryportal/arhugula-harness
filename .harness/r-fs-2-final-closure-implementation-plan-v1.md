# R-FS-2 — Final-Closure Implementation Plan v1 — 2026-07-11

**What this is.** The single consolidated atomic-unit register that brings the harness build to **full closure as the spec outlines**. It merges three sources into one loop-consumable document:

1. **Pre-NotebookLM-audit open register** — items already known-open before `NotebookLM_Spec_Layer_Overview_Audit_2026-07-11.md`: B-19/U-2 breaker attrs, Gap D (R-100 AC#2), F1-01 WAL residual, doc-hygiene residuals, and the held/credential-gated set.
2. **Untracked documented deferrals** the NotebookLM audit surfaced — `B-18-KEEPALIVE` and `B-18-LANEB-PROMPT-SEMVER` (both named at the 3c DDR §8 "Deferred / registered follow-ons (SPINE `B-*`)" table, `u1-3c-prewarm-design-decision-record.md:138-152`, never entered any ledger).
3. **PARTIAL verdicts** from that audit — spec-committed capabilities with an identifiable unbuilt half (OAuth-RS enforcement, MCP signature gate, SKILL.md frontmatter validator, tool_search runtime, two-row rotation runtime, C-OD-17/18/19 envelope surfaces).

**What this is NOT.** Not design-substrate (no X-AL-3 guard applies to this file; §1.3 authority chain — the specs win on conflict). Not a second roadmap: it plugs into the existing §12 machinery via arc-ledger registration (Unit 0). Research-only material the specs never committed is **excluded** (Appendix C) — closure is measured against the spec, not against the research corpus.

**Standing directives honored.** FULL-SPEC ("all beyond-MVP spec'd and built"; documented deferral ≠ resting state — #918 §0). No-parking (§12.4.1): operator-gated units are DRIVEN to their genuine gate, then surfaced batched. Held decisions honored: R-1 managed-cloud stays held unless the operator reverses it (Appendix B). Framework-pull discipline (I-6) binds every unit.

---

## 0. Loop-consumption protocol

- **Unit 0 (U-CL-00) lands this plan + the arc registrations in one PR.** Registering rows flips `snapshot.rfs1_status` → `active` (the `tools/arc_ledger.py` zero-open invariant runs in reverse), which re-arms the §4/§12 next-action derivation. From then on, `/loop continue` = normal `roadmap-continue` iterations: session-start audit → pick next registered arc per the wave order below → ground → build with tests → `ship-pr` → fixed-point refresh.
- **Arc mechanics** (unchanged from R-FS-1): one PR per arc (bundled-absorption where a spec delta is owed, with a `.harness/clearance/` marker per §4.5); `registered` rows carry `decompose_at_open: true`; grounding-at-open is mandatory (`[[r-cxa-seam-wiring-is-producer-discovery]]`, `[[grounding-reveals-claude-closeable-slice-close-honestly]]` — a grounding-first unit below MAY close as already-realized/no-op with evidence; that is a legitimate close).
- **Review ritual** (while advisor + Codex remain down): Fable-5 fallback BOTH roles per arc — pre-build design-packet review + post-build diff review with fails-on-main re-verification by execution (`[[fable5-fallback-reviewer]]`). Revert to advisor+codex when they return.
- **Witness discipline:** every behavioral unit ships fail-on-main witnesses (by execution, not grep); byte-preservation controls where the unit claims "X unchanged".
- **Closure criterion (G2):** R-FS-2 is closed when (i) every Wave 1–4 arc is `closed` or `resolved` with evidence AND the Wave-5 sweep PR has landed, (ii) every Appendix B gate has been surfaced to the operator at least once in a batched AUQ and either answered or re-affirmed held, (iii) the registered queue is empty again and the umbrella row closes (`rfs1_status` returns to `resolved`), and (iv) a terminating closure report is filed at `.harness/audit/`.
- **#918 deferral accounting (source-2 completeness):** T-1..T-9 verified at HEAD — T-1 Arc R closed; T-2 B4 closed; T-3 B-TAIL closed (#717); T-4 fallback-family closed; T-5 realized (`MCP_TRUST_GATE_LEVEL_FLOOR` live in `gate_level_rule.py`); T-6 B3 closed; T-7 built (`harness_cp/hitl_timeout_degradation.py`, C-CP-21 §21.8, F-B3-2 operator-ratified 2026-06-14); T-8 B-EDIT-CARRIER-DURABLE-ASYNC-RESUME closed (#683); T-9's sole residual is the rotation sliver = Wave 1 `B-AUDIT-KEY-ROTATION-RUNTIME`. U-1 closed by the B-18 family; U-2 = Wave 4 `B-19`; R-1 = Appendix B held.

---

## 1. Unit 0 — U-CL-00 · Plan landing + registration

| Field | Value |
|---|---|
| Scope | Land this document; **first add the `R-FS-2` umbrella row itself** (`id: R-FS-2`, `kind: standalone`, `status: remaining` while active — closed/resolved at G2 with the closure report as deliverable; `tools/arc_ledger.py:169-174` rejects any `parent_arc` not in the ledger's id set, so the umbrella must exist before its children); then add one `registered` row per Wave 1–4 arc below (schema per existing rows: `id`, `title`, `kind: standalone`, `status: registered`, `decompose_at_open: true`, `owner_axis`, `parent_arc: R-FS-2`, `anticipated_scope` = the unit's Authority+Scope cells — **stripping any concrete `U-XX-nn` ids**, which the `arc_ledger.py:184-187` regex tripwire rejects in `anticipated_scope`; for the sweep unit use its Authority+Method cells, same strip rule); bump `snapshot` in the same commit (`standalone_registered: 0→N`, `rfs1_status: resolved→active`); update `.harness/roadmap_status.md` next-action to R-FS-2 Wave 1; regenerate the dashboard. |
| Acceptance | `python3 tools/arc_ledger.py --check` green; CI arc-ledger job green; dashboard next-action names this plan. |
| Gate | None. Wave-5 hygiene and Appendix-B items are NOT registered as arcs (hygiene lands as one sweep PR; gated items enter the ledger only if their gate opens). |
| Size | S |
| Note | When each arc later closes, its row needs the `pr:` chip for `tools/dashboard/generate.py` (known latent CI bite per `[[regenerate-roadmap-html-after-source-edit]]`). |

---

## 2. Wave 1 — committed-and-unbuilt, no gates (cleanest closes first)

### B-18-KEEPALIVE · Boot-time cache pre-warm + keep-alive loop *(owner: Runtime)*

- **Authority.** ADR-D3 §1.5:189-190 (cleared, byte-verified): `pre_warm: max_tokens=0 at process boot per Cluster 2 V2 §[HIGH] Pattern P1.3; keep-alive every 4min for 5min TTL caches`. Named `B-18-KEEPALIVE (R2)` at the 3c DDR §8; deferral + default recorded at `u1-slice3b-epoch-partition-design.md` §3.3/§4.3 ("C11-safe default when built: **opt-in, default off**"; R2 = skip-under-cost-ceiling carve-out deferred with the mechanism).
- **Current state.** Zero code (verified twice: audit + adversarial reviewer). The fan-out cohort warm-up (ADR-D4 §1.8, built through #933) is a *different, sibling* mechanism.
- **Scope.** (1) Runtime spec delta committing the executable shape + clearance marker (bundled-absorption arc). (2) `RuntimeConfig` opt-in fields (e.g. `prompt_cache_boot_prewarm: bool = False`, `prompt_cache_keepalive: bool = False`) threaded through BOTH env loaders (`[[runtimeconfig-scalar-needs-both-env-loaders]]`). (3) Boot pre-warm at the stage-5/daemon seam: one minimal dispatch against the parent-agent cacheable epoch. **Adaptation decision to record in the spec delta:** `max_tokens=0` is not a valid `messages.create` call (`llm_dispatch.py:1917`) — adapt to the minimal valid ping (`max_tokens=1`), mirroring the 3c precedent (no cache-ack signal → await completion). (4) Keep-alive task: every 4min, only for **5-minute-TTL** epochs (1h-TTL epochs excluded by design), daemon-scoped, cancelled at shutdown/drain; per-run isolation respected (`[[run-scoped-ctx-holder-daemon-isolation]]`). (5) Cost attribution: pings flow through the normal dispatch path so `cost_formula` + `anthropic.*` cache attrs record them (no shadow spend). (6) **R2 disposition recorded in the spec delta** — the skip-under-cost-ceiling carve-out was deferred *with* this mechanism (slice-3b §3.3); building KEEPALIVE is where R2 gets decided: build the carve-out or explicitly re-defer with rationale (the DDR row is literally "B-18-KEEPALIVE (R2)").
- **Acceptance.** Default-off byte-identical dispatch (control witness); opt-in boot ping observed with `anthropic.cache_breakpoint_id` + `cache_read/creation` attrs; keep-alive fires on a fake clock ≤ TTL and never for 1h epochs; drain cancels cleanly; fail-on-main witnesses for the gating predicate.
- **Gate:** none (opt-in default-off IS the ratified posture). **Size:** M.

### B-WAL-F1-01-EXACTLY-ONCE · WAL completed-run-retry duplicate `cp.resume-attempted` *(owner: CP)*

- **Authority.** C-CP-07 §7.4 floor-(ii) idempotency-keyed exactly-once; residual doc `.harness/r-fs-1-e-impl-3c-f1-01-wal-exactly-once.md` (🔵 OPEN, non-gating; fix-shape "apply the same completed-run guard … symmetrically" at its §fix; the "symmetric fix-shape ready" phrasing is the forward register's, `post-phase-8-forward-register.md:181`).
- **Scope.** Apply the documented symmetric fix-shape; witness pins single `resume:`-prefixed emission on completed-run retry.
- **Acceptance.** Fix-shape doc's own repro flips red→green; no other status/fail_class byte changes (control). **Gate:** none. **Size:** S.

### B-SKILL-FRONTMATTER-VALIDATOR · SKILL.md frontmatter constraint enforcement *(owner: AS)*

- **Authority.** Substrate-committed constraints ONLY: name ≤64 chars + description non-empty ≤1024 (ADR-D3 Rationale prose, [HIGH]-cited Anthropic schema); `frontmatter.version` + `version_sha` both required (ADR-D3 §1.8.1:331). The external agentskills.io extras ("lowercase-alphanumeric", "no vendor reserved words") are **NOT committed in-substrate** (greps empty; AS spec :1203 defers authoring schemata beyond frontmatter to discretion) — enforcing them without a spec delta would be silent design extension.
- **Current state.** Skills residence + activation telemetry + adoption matrix built; **no production frontmatter validator located** (audit §2.3 #5).
- **Scope.** Grounding-first (locate the exact spec table; confirm no validator hides in `procedural_tier_snapshot.py`/loaders); then a pure validation function at the skills filesystem-load seam enforcing the committed set, fail-closed with a typed rejection reason enum (mirror `validate_tool_contract_at_registration` shape, `tool_contract.py:167-194`). If the full external-schema table is wanted, that is a **spec-delta leg first** (bundled-absorption + clearance) — record the choice either way.
- **Acceptance.** Rejection tests per constraint; accepted-fixture control; wired at the real load path (not tests-only). **Gate:** none. **Size:** S.

### B-AUDIT-KEY-ROTATION-RUNTIME · Two-row rotation dual-signature path *(owner: OD)*

- **Authority.** ADR-D5 v1.3 §1.4 (operator-selected Option (a): rotation event = two ledger entries sharing `rotation_correlation_id`; outgoing key signs period-N row, incoming key signs period-N+1 row; auditor-walk semantics specified in the ADR prose).
- **Current state.** `sign_audit_entry`/`verify_hash_chain_integrity` built (`multi_tenant_trace_separation_and_audit_ledger.py:177,211`); 3-algorithm enum built; **no rotation-pair writer/verifier located** (audit §4 item 3; [MODERATE] — re-ground at open).
- **Scope.** Rotation-event writer producing the co-signed pair + `rotation_correlation_id`; extend the verify walk per the ADR's external-auditor semantics (sibling lookup, both signatures, chain continuity across the boundary); solo-tier no-op preserved (column NULL).
- **Acceptance.** Round-trip witness: rotate → verify passes; tamper either sibling → verify fails; non-rotation entries unaffected (control). **Gate:** none (persona-tier-gated *in production use*, not in build). **Size:** M.

---

## 3. Wave 2 — committed builds, medium

### B-18-LANEB-PROMPT-SEMVER · Operator-declared semver on `PromptVersion` *(owner: IS; bundled-absorption)*

- **Authority.** ADR-D3 §1.8.1 commits the concept for skills ("operator may bump `frontmatter.version` … without changing every byte", both-required with `version_sha`); the prompt-side analogue was named at DDR §8 + slice-3b §4.2 as an IS-spec amendment, **optional** (version_sha remains the cache key).
- **Disposition.** BUILD by default under FULL-SPEC (a documented deferral is a build target); the operator may strike this row at the Unit-0 PR review — that is the one-time skip window, recorded either way.
- **Scope.** IS-spec delta adding the optional field to the `PromptVersion` shape + clearance marker; `prompt_manifest.py` optional field (default None — byte-compatible with every existing manifest); explicitly **cache-inert** (spec text must state it does not participate in cohort/cache identity — that is `version_sha`'s job; `[[new-surface-audit-hash-and-config-not-carrier]]`).
- **Acceptance.** Manifest round-trip with/without the field; cohort_key/cacheable-epoch witnesses byte-unchanged (control); spec delta cleared. **Gate:** strike-window at Unit-0 review only. **Size:** S-M.

### B-TOOL-SEARCH-RUNTIME · `tool_search` capability-discovery path *(owner: AS/Runtime)*

- **Authority.** ADR-D3 §1.5 cache-prefix integrity discipline (committed): "per-MCP capability discovery via `tool_search` rather than `tools[]` mutation"; C-AS-13 adoption matrix models the mode; `skill.activation_mode = tool_search` exists in the attr schema.
- **Current state.** Frozen superset (built) is the current realization; **no runtime search-dispatch mechanism** (audit §2.3 #7).
- **Scope.** Grounding-first: read the C-AS-13 §13.2 adoption-depth cell for tool_search at current workload classes — if the committed depth for every live cell is "deferred/not-adopted", close as **adoption-depth-honored** with evidence; otherwise build: a search tool inside the frozen superset returning deferred schemas on demand, `skill.activation` span emission in tool_search mode, cache-prefix invariance witness (tools[] bytes unchanged across searches — the entire point of the mechanism).
- **Acceptance.** Either a cited adoption-depth close, or: search round-trip e2e + frozen-superset byte-invariance witness + span mode emission. **Gate:** none. **Size:** M (or S close).

### B-OD19-LOCAL-INSPECTION · C-OD-19 named-primitive completion *(owner: OD; decompose-at-open into 3 slices)*

- **Authority.** C-OD-19 §19 contract surface (OD spec v1.2:1049-1091): "In-process collector signature + sqlite ring-buffer trace storage + **TUI trace browser surfacing**"; §19.3 TUI primitive table; §922/§976 (five operator-burden primitives surfaced as scoped ring-buffer queries; alerting optional via TUI threshold annotation). Deferral formally registered in-code (`deferral_envelope.py:270-276`, closure target phase-6-implementation) — under FULL-SPEC that target is now due.
- **Current state.** Collector + ring buffer + `sqlite_span_store_reader` + `harness-inspect` read-only CLI built; TUI browser, ring-buffer rotation (Phase-2 markers `local_first_otlp_collector.py:36,234,264`), and the otelcol-contrib config manifest unbuilt.
- **Slices.** (a) **TUI trace browser**: terminal-native scoped-query browser over the sqlite ring buffer — ledger/trace walk, five-primitive views, threshold annotation. Framework-pull check at design: prefer stdlib `curses` (bounded adoption applies to any TUI library; operator machine is Intel x86 macOS — bias light, `[[operator-dev-machine-and-dep-preference]]`). Reuse `sqlite_span_store_reader` + `harness-inspect` internals — extend, don't fork. (b) **Ring-buffer rotation**: §19.2 **commits the 24h default, operator-tunable** — pin that default; only the mechanism (size/time/hybrid) is discretion. Crash-safe, verified against live collector writes. (c) **otelcol-contrib config manifest**: grounding-first — §19.1 commits an "in-process otelcol-contrib instance" but the as-built collector is the hand-rolled `local_first_otlp_collector.py` (BUILT-MODIFIED); ground what the manifest configures when no otelcol-contrib binary runs, and whether a spec-reconciliation note is owed (possible small spec-delta outcome) before authoring the artifact.
- **Acceptance.** (a) browser walks a seeded ring buffer + renders the five primitives (scripted TUI test or headless render harness); (b) rotation witness (fill → rotate → chain-readable) + 24h-default pin; (c) manifest validates against the in-process collector, or a cited reconciliation close. **Gate:** none. **Size:** L (a=M-L, b=S-M, c=S).

### B-OD17-EVAL-LOOP-TOOLING · Holdout-set + operator review-loop tooling *(owner: OD)*

- **Authority.** C-OD-17 §17.3:976 (Husain manual-review → categorize → automate → align loop against the ring buffer, operator self-curation); envelope entry (child-span emission API built; **holdout-set construction protocol + loop tooling + per-cell dashboard query authoring** deferred to phase-6).
- **Hard boundary.** `[[eval-harness-refused-as-governance-gate]]`: NO model-judge as a governance gate — the committed surface is **operator-manual** review tooling. The κ/TPR/TNR/gold-set numbers are research-only (excluded, Appendix C). Any model-judge component proposal = halt + Class-1 fork, not this unit.
- **Scope.** Holdout-set construction: deterministic sampler drawing N traces from the ring buffer into a versioned holdout file; review-loop CLI (or TUI-browser view, compose with B-OD19 slice a): present trace → operator categorizes → categorization appended to a durable review ledger; "automate" step = operator-authored assertion stubs checked into the repo (tooling scaffolds the file, human writes the assertion).
- **Acceptance.** Holdout determinism witness; review round-trip persists; zero model calls in the loop (control assert). **Gate:** none (model-judge variants are out of scope by standing refusal). **Size:** M. **Depends:** B-OD19(a) optional compose, not blocking.

### B-OD18-DRIFT-ALGORITHM · Per-primitive drift computation + re-baselining *(owner: OD)*

- **Authority.** C-OD-18 §18.1-18.2 (drift thresholds; `gen_ai.eval.alignment_floor.drift_detected` event — emission BUILT at `alignment_floor_drift_detection.py`); envelope entry defers "drift-detection **algorithm** per primitive + re-baselining cycle workflow + dashboard alerting integration + eval-kind enforcement at SDK boundary".
- **Scope.** Grounding-first (how much of the algorithm the built emitter already computes vs receives); then: per-primitive current-value computation over the ring-buffer observation window (the five C-OD-17 primitives), threshold comparison feeding the existing event emitter, re-baselining workflow = operator-facing recompute + threshold-update path (config-driven values stay deployment-binding); eval-kind SDK-boundary enforcement (reject offline_judge spans emitted through the inline path — a validation guard, not a judge).
- **Acceptance.** Synthetic-window drift witness (floor breach → event with correct 4-attr set; no breach → silence); re-baseline round-trip; eval-kind guard fail-closed test. **Gate:** none. **Size:** M.

---

## 4. Wave 3 — grounding-first sweeps (legitimate close = already-realized / spec-honored no-op)

### B-MCP-OAUTH-RS-ENFORCE · Remote-MCP L2/L3 OAuth-RS validation *(owner: AS/Runtime)*

- **Authority.** AS spec C-AS-10 §10.3 four-level `streamable_http` trust taxonomy (enum BUILT, `discriminators.py:31-43`; STDIO floor BUILT) + ADR-D2/ADR-D3 OAuth 2.1 mandatory-for-remote commitments.
- **Grounding question (decides the unit).** (1) Read C-AS-10 §10.3's "Deferred to implementation discretion" block verbatim — does connection-time OAuth-RS validation sit inside it, and does any committed sentence make L2/L3 connection *conditional* on OAuth-RS status? (2) Does ANY streamable-HTTP client path exist at `mcp_client_host_factory.py` (R-800 proved stdio only)? Then: **(A)** no remote-HTTP client + no committed conditional → close as **deployment-binding-honored** with cites (fail-closed today: L0_REFUSE + no HTTP path = structurally can't connect un-validated); **(B)** committed conditional exists → build the fail-closed gate at the client-host connect seam (PKCE + RFC 8707 resource-indicator checks before L2/L3 session establishment), stdio path byte-unchanged.
- **Acceptance.** (A) cited close in the arc record; or (B) connect-refusal witnesses per trust level + stdio control. **Gate:** none for the gate-shape; a *live* remote-HTTP e2e is credential-gated → Appendix B if (B). **Size:** S close / M build.

### B-MCP-PRIMITIVE-SIG-GATE · `mcp.primitive.signature.sha256` verification gate *(owner: AS)*

- **Authority question.** The 7-attr namespace incl. the signature attr is canonical + emitted (AS §14.3:207, `MCPClientNamespaceEmitter` per C-CP-27). The **registration-time verification gate** (rug-pull protection) — locate its commitment: grep AS spec §14.3 body + C-AS-03 registration contract + ADR-D2 for a committed verify-on-mutation behavior. **(A)** committed → build: persist first-seen hash per primitive in the tool registry; on re-registration/dispatch mismatch emit a violation (compose with existing violation event shapes) and fail closed per gate level. **(B)** attr-only (observability, no gate committed) → close as **research-only-gate / attr-complete** with cites.
- **Acceptance.** (A) mutation witness (tamper description → violation + refusal) + stable-hash control; or (B) cited close. **Gate:** none. **Size:** S-M.

### B-OD-ENVELOPE-P6-SWEEP · Remaining phase-6 deferral-envelope dispositions *(owner: OD)*

- **Authority.** `deferral_envelope.py` — 14 entries carry `closure_target=phase_6_implementation`; C-OD-17/18/19 are covered by their own Wave-2 units; this sweep dispositions the remaining **11**: C-OD-01 (cell-identification API + transition state-machine + binding persistence), C-OD-04 (SDK binding + exporter), C-OD-05 (cross-SDK namespace conformance harness), C-OD-06 (span-event emission API + sibling correlation), C-OD-07 (breaker OTLP emission), C-OD-08 (runtime cross-namespace validation), C-OD-09 (tail-sampling decision algorithm), C-OD-12 (default-off filter), C-OD-13 (eval-grade redaction pipeline), C-OD-22 (transition-planning UX + cross-cell config), C-OD-23 (cross-spec citation strings + seam versioning).
- **Method.** Per entry: body-read contract §  + locate realizing code (most are expected **already-realized** by the OD build — e.g. C-OD-04→`otel_genai_base`, C-OD-07→U-RT-58, C-OD-09→`composite_sampler`/`tail_keep_span_processor`, C-OD-12→`content_structure_discipline`, C-OD-13→`RedactionSpanProcessor`) → classify {already-realized (cite) / scoped-build (register a follow-on row) / genuinely-discretionary-no-op (cite the discretion sentence)}. Presence≠correctness: for "already-realized", cite the *consumer-visible surface*, not a filename (`[[verification-shape-sharpened-grep-vs-e2e]]`).
- **Post-v1.2 blocks.** The envelope enumerates OD spec v1.2 §1–§23 only; the v1.8 delta added C-OD-25..33 with four further "Deferred to implementation discretion" blocks (§25.5, §26.5, §27.5, §28.5) — pre-reviewed 2026-07-11: each names a default already realized in the built contracts (terminal-close-only; per-provider rate-table; lazy-on-write; placeholder rates). The sweep confirms + records those four alongside the 11, so the disposition table is complete over the whole OD chain.
- **Acceptance.** A disposition table (all 11 v1.2 rows + the 4 v1.8 blocks, evidence-cited) filed at `.harness/`; follow-on rows registered for any scoped-build findings. **Gate:** none. **Size:** M (read-heavy, code-light).

### B-COST-REPLAY-DEDUP-WITNESS · Replay-dedup cost join verification *(owner: OD)*

- **Authority.** D6 §1.5 / C-OD-14 (cost-attribution joins on `idempotency_key`; replay must not double-count). Flagged [MODERATE — not independently re-executed] at the audit.
- **Scope.** Verify-first: a witness that replays a completed step (journal_resume path) and asserts the cost rollup is emitted once. If the join is missing → smallest fix at the cost-record accumulator.
- **Acceptance.** The witness, green (or red→green with the fix). **Gate:** none. **Size:** S.

---

## 5. Wave 4 — operator-gate-driven (drive to the gate; ONE batched AUQ)

### B-19-BREAKER-AMBIENT-ATTRS · `breaker.cause` + `breaker.cooldown_ms` *(owner: CP/OD)*

- **Authority.** CP spec v1 4-attr ambient set, consciously dropped at v1→v1.1 ("Semantic-loss note"); #918 U-2: re-introduction **operator-discretionary** ("surface the ambient-vs-event redundancy first" — dashboard standing note).
- **Drive-to-gate.** Claude authors the redundancy analysis (what the 7-attr *event* schema already answers vs what ambient *state* adds: current-cause-while-open, remaining-cooldown for schedulers/dashboards; cite `harness_breaker_schema.py` + consumers) → **AUQ: build / skip-and-close**. If build: attrs at the breaker registry + OD ingestion row (namespace_map is CLOSED-schema — the addition is itself a spec-delta leg, `[[closed-schema-extension-enforced-vs-advisory]]`).
- **Gate:** operator AUQ (batched with Gap D below). **Size:** S analysis + S-M build.

### B-GAPD-TOOLONLY-BOOTSTRAP · Conditional provider ping for tool-only workflows *(owner: Runtime)*

- **Authority.** `post-phase-8-forward-register.md` B-10 residual: bootstrap pings ≥1 provider regardless of step kind (R-100 AC#2 `must_pass[3]` strict reading); **registered Class-1 fork candidate**, nameable **C9⊥C11** tension (fail-fast reliability ⊥ tool-only ergonomics), dyadic-council-eligible per §10.9.
- **Drive-to-gate.** File the Class-1 fork doc; convene the dyadic council (C9 + C11) with probe-first discipline (the probe: what exactly breaks downstream if no provider is pinged and a later step needs one — is a deferred-fail path already typed?) → operator ratification AUQ → on ratify: make the stage-3a ping conditional on the workflow containing an inference step; `test_r100_ac2_tool_step_e2e` un-gated for the tool-only case.
- **Gate:** operator ratification (this is the genuine Class-1 fork the register reserves to the operator). **Size:** M end-to-end.

*(AUQ batching rule: both Wave-4 gates + any Appendix-B re-affirmations surface in ONE AskUserQuestion when Wave 4 opens — not drip-fed.)*

---

## 6. Wave 5 — hygiene close (one sweep PR, after code waves)

### B-HYGIENE-CITE-POINTER-SWEEP *(mode-agnostic + design-phase doc legs)*

1. Root `CLAUDE.md` §1.1 "12-namespace OTel schema" → 15 (cite C-OD-05 map); §2.3 CP pointer v1.86 → current head (the #933-dispositioned catch-up).
2. The ~14 `C-IS-13 §13.5` redundant-cite sites → drop the redundant cite per the recorded convention (clearance marker `Spec_Harness_Runtime-v1_93-cleared-2026-07-09.md`; "correct fix is to drop, NOT inject the seam anchor").
3. Any stale-carry text the Wave 1–4 arcs surface (per-arc notes accumulate here rather than blocking their PRs).
- **Acceptance.** `just overlay-check` green; cross-spec `rg` for the touched cite-shapes clean; X-AL-3 guard satisfied via clearance markers where `design-substrate/**` is touched. **Gate:** none. **Size:** S-M.

---

## 7. Frozen build order

```
U-CL-00 → [B-18-KEEPALIVE → B-WAL-F1-01-EXACTLY-ONCE → B-SKILL-FRONTMATTER-VALIDATOR
           → B-AUDIT-KEY-ROTATION-RUNTIME]                                               (Wave 1)
        → [B-18-LANEB-PROMPT-SEMVER → B-TOOL-SEARCH-RUNTIME → B-OD19-LOCAL-INSPECTION
           → B-OD17-EVAL-LOOP-TOOLING → B-OD18-DRIFT-ALGORITHM]                          (Wave 2)
        → [B-MCP-OAUTH-RS-ENFORCE → B-MCP-PRIMITIVE-SIG-GATE → B-OD-ENVELOPE-P6-SWEEP
           → B-COST-REPLAY-DEDUP-WITNESS]                                                (Wave 3)
        → [B-19-BREAKER-AMBIENT-ATTRS + B-GAPD-TOOLONLY-BOOTSTRAP
           — one batched AUQ, then their builds]                                         (Wave 4)
        → B-HYGIENE-CITE-POINTER-SWEEP (sweep PR, not a ledger arc)                      (Wave 5)
        → G2 closure report
```
*(Ids above are the exact ledger registration ids.)*

Rationale: Wave 1 = unambiguously committed + unbuilt + gate-free (cleanest value first); Wave 2 = medium builds incl. the one strike-window item early enough to matter; Wave 3 = sweeps whose honest outcome may be "close with evidence" (cheap, but AFTER the concrete builds so the sweeps see final state); Wave 4 last-but-one so the single AUQ batches everything the loop needs from the operator; hygiene last (touches files the code waves settle). Within a wave, order is top-to-bottom as listed but arcs are independent unless a `Depends` note says otherwise.

---

## Appendix A — Excluded: research-only, never spec-committed (closure does NOT require these)

Per the NotebookLM audit (§2 tables + §3): `clear_thinking_20251015` (zero design-substrate presence — verified), XGrammar/Outlines constrained decoding (I-6 foreclosed; Pydantic v2 is the committed L1), XML structured-event message encoding (typed event records are the as-built shape), code-execution-with-MCP servers-as-files, MicroCompact/AutoCompact/Full compaction tiers + `/compact` (H_E features), pre-compaction NOTES.md rule, CONTEXT.md-Inputs section routing (ICM research), JIT-retrieval enforcement, docs-over-outputs invariant, Zheng judge-bias protocol + κ/TPR/TNR/gold-set numbers, three-step gate cadence at named fixture scales, plateau early-stopping, inputs-disabled verifier-agent discipline, skill self-evolution, Meta-Harness outer-loop optimization, named markdown personas, numeric context-window targets. Building any of these would be X-AL-3 design extension — route to design-phase first if ever wanted.

## Appendix B — Held / credential- / infra-gated (surfaced, not built; honor holds)

| Item | Gate | Standing disposition |
|---|---|---|
| B-13 memory-tool managed-DB **live** proof | operator PostgreSQL DSN + explicit approval | Built; fire on creds (`[[feedback-background-agent-no-unilateral-paid-calls-or-secret-relocation]]`) |
| R-1 managed-cloud deployment-surface dispatch (Persona §9; AS-8f Q1=(C)) | operator-ratified **HELD** (2026-05-28; re-confirmed) | Honor the hold; re-affirm at the Wave-4 AUQ, do not build |
| Arc-R L2/L3 routing + B4 per-role runtime-indexing **production activation** | standing 2nd provider + activation gate | Built, production-inert; activation is deployment posture, not a build gap |
| Antigravity / legacy-Gemini / generic-command CLI auth confirmations | local CLIs/probe presence | Live gates, fire when present |
| 9 deferral-envelope DEPLOY-targeted entries (C-OD-02/03/10/11/14/15/16/20/21 slivers) | deployment-binding-time **by contract** | Not phase-6 targets; close at deployment binding |
| E-O multi-evaluator warm-up/partition | contingent tripwire (runtime spec v1.96 item 9) | Fires only if a multi-evaluator cell is ever registered |
| Remote-MCP **live** HTTP e2e (if B-MCP-OAUTH-RS-ENFORCE lands branch B) | remote server + creds | Follows the B-10/R-800 live-gate pattern |

## Appendix C — Recurring lanes (unchanged by this plan)

`R-600-pattern-bake-in-sweep` cadence-5 is due (~#923–#933 span) and continues as a lane, not an R-FS-2 arc; `R-IF-roadmap-refresh` fixed-point protocol unchanged; out-of-family review remains the codified per-arc gate.

---

*Filed 2026-07-11 as the R-FS-2 umbrella register. Mechanism mirror: R-FS-1 (`.harness/beyond-mvp-capability-boundary-ledger.md` + arc-ledger rows + §12 derivation). Grounding: `NotebookLM_Spec_Layer_Overview_Audit_2026-07-11.md` (+ its Fable-5 adversarial review), `Spec_Implementation_Gap_Audit_2026-07-09.md`, `Upstream_Decomposition_Audit_2026-07-09.md`, `u1-3c-prewarm-design-decision-record.md` §8, `u1-slice3b-epoch-partition-design.md` §3.3/§4.3, `deferral_envelope.py`, `post-phase-8-forward-register.md`, `r-fs-1-e-impl-3c-f1-01-wal-exactly-once.md`. Authority chain per root `CLAUDE.md` §1.3 — on any conflict, design-substrate wins and this register yields.*
