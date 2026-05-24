# Adversarial Review 06 — Implementation_Plan_Harness_Runtime_v2_14.md

## Summary

- **Checkpoint:** P6-CK (Phase-7 pre-implementation review mode — L9-octies cluster opening at U-RT-76)
- **Artifact reviewed:** `design-substrate/Implementation_Plan_Harness_Runtime_v2_14.md` (commit `c2f90e3` on `worktree-cp-16-17-impl-planner-arc`)
- **Date:** 2026-05-23
- **Finding count by class:** Class 3: 0 · Class 2: 4 · Class 1: 3
- **Highest-severity finding:** F2-01 (change-note internal contradiction — adjacent-defect (ii) framing)
- **Disposition recommendation:** **Clearance with current-phase revision (per §4.1.2)** — 4 Class 2 findings require plan-body fix; no upstream-phase artifact revision needed; no Phase-7 §2.7.6 fork triggered. Revision-pass to v2.15 absorbing the 4 Class 2 findings + 3 Class 1 inline fixes recommended BEFORE L9-octies cluster opens at U-RT-76.

---

## Class 3 findings (severe — phase re-opening)

**None.** Discriminator tree walked for each candidate finding; no finding triggers (b) upstream-phase artifact revision OR (c) project-commitment violation per workspace `CLAUDE.md` framing.

---

## Class 2 findings (moderate — current-phase revision)

### F2-01 — Change-note internal contradiction: adjacent-defect (ii) framed as "NOT patched per FM-2" while U-RT-81 AC #3 locks the mapping

- **Location:** `Implementation_Plan_Harness_Runtime_v2_14.md` change-note "Adjacent defects surfaced (NOT patched at this arc per FM-2 no-extension discipline)" header line + adjacent-defect (ii) paragraph + U-RT-81 AC #3 body
- **Defect:** The change-note's section header asserts the 3 adjacent defects are "NOT patched per FM-2 no-extension discipline." But the body of adjacent-defect (ii) (`§14.5.1 step 4 memory.operation.kind enum non-bijective with 5-callback Protocol`) acknowledges that the plan DOES lock the mapping at U-RT-81 AC #3 (`view → "read"`, `create → "write"`, `str_replace → "update"`, `insert → "update"`, `delete → "delete"`; `list` dead). The lock IS a planning patch (per `[[spec-prose-plan-body-drift-pattern]]`) — defensible, but the framing is internally inconsistent: the section header says "NOT patched"; the body says "locked at U-RT-81 AC #3 per plan-body discipline." A reviewer cannot tell whether to treat the mapping as plan-side-locked or spec-deferred-to-implementation. Discipline question: is the §14.5.1 step 4 prose ambiguity (a) patched at plan-body (the lock) OR (b) deferred to follow-on spec revision OR (c) both (lock now, file spec revision later)?
- **Discriminator that classifies as Class 2:** (a) affects substantive content of current-phase artifact — change-note framing must accurately describe what the plan does or doesn't patch; current framing makes the FM-2 discipline-claim non-verifiable.
- **Evidence:** Change-note section header: *"**Adjacent defects surfaced (NOT patched at this arc per FM-2 no-extension discipline).**"* — then adjacent-defect (ii) reads: *"Per the locked mapping above: `list` is dead at v1.17... [the plan] locks the mapping at U-RT-81 AC #3 to give the executor a deterministic instruction."* (`change-note` §3 lines ~38-44).
- **Anti-fabrication attack engaged:** A8 (framing contamination — discipline-claim shape).
- **Axis-domain attack engaged:** CP — spec-vs-plan calibration discipline (Tension 002 pattern: plan-body lock vs spec-deferral).
- **Resolution path:** Disambiguate the change-note framing — either (a) split adjacent-defect (ii) into "locked at plan-body U-RT-81 AC #3 per spec-prose-plan-body drift pattern (executor-deterministic instruction) + future spec revision SHOULD reconcile §14.5.1 step 4 prose" (acknowledging both the lock and the deferred spec fix); OR (b) move adjacent-defect (ii) out of the "NOT patched" section into its own "patched at plan-body" section. The skill does not specify which framing to pick.

### F2-02 — U-RT-81 missing direct dependency on U-RT-76 (typed exceptions + Protocol type)

- **Location:** `Implementation_Plan_Harness_Runtime_v2_14.md` §1 U-RT-81 `Depends on:` line
- **Defect:** U-RT-81 declares `Depends on: [U-RT-78 (ctx.memory_tool_registry consumed via Protocol), U-RT-79 (ctx field exists post-stage-5), U-RT-77 (callback semantics — MemoryPathViolationError + MemoryCallbackIOError typed exceptions propagated through _execute_with_memory_callbacks)]`. Two direct dependencies are missing: (1) `MemoryToolStorageBackendProtocol` (the helper signature `_execute_with_memory_callbacks(... backend: MemoryToolStorageBackendProtocol, ...)` consumes the Protocol type, declared at U-RT-76 NOT U-RT-77); (2) `MemoryPathViolationError` + `MemoryCallbackIOError` typed exceptions (declared at U-RT-76 per the U-RT-76 Signatures section: *"2 typed exceptions: `class MemoryPathViolationError(Exception)` + `class MemoryCallbackIOError(Exception)`"*; U-RT-77 RAISES them, does not declare them). Per `implementation-planner` SKILL §7 "no-transitive-omission" discipline: a unit's direct dependencies must be declared, not transitively closed via dependency-of-dependency. U-RT-81 imports types from U-RT-76 → U-RT-76 is a direct dep, missing.
- **Discriminator that classifies as Class 2:** (a) affects substantive content of current-phase artifact — missing dependency declarations are a §4.4 implementation-grade-detail failure + §7 coverage discipline violation.
- **Evidence:** U-RT-76 Signatures section declares the 2 typed exceptions + the Protocol; U-RT-81 Signatures section uses both (`_execute_with_memory_callbacks(... backend: MemoryToolStorageBackendProtocol, ...)` + propagates `MemoryCallbackIOError` + `MemoryPathViolationError`); U-RT-81 `Depends on:` list omits U-RT-76 entirely.
- **Anti-fabrication attack engaged:** none directly; this is a §7 dependency-graph hygiene defect.
- **Axis-domain attack engaged:** Runtime — dependency-graph acyclicity is preserved (U-RT-76 → U-RT-78 → U-RT-81 path exists transitively), but per §7 the direct dep must be declared.
- **Resolution path:** Add U-RT-76 as a direct dependency at U-RT-81 `Depends on:` line; clarify the semantic reason (typed-exception declaration + Protocol-type declaration). U-RT-77 dependency may also need its cite-reason adjusted (callback semantics is run-time behavior consumed via the Protocol type, not a direct U-RT-77 type-import).

### F2-03 — AS spec §14.7 vs §14.8 sampling-row cite drift (memory.operation sampling lives at §14.8, not §14.7)

- **Location:** `Implementation_Plan_Harness_Runtime_v2_14.md` U-RT-81 AC #3 + AC #4 + change-note callback-mapping-lock paragraph
- **Defect:** Plan cites "AS spec §14.7 sampling-row" + "per AS spec §14.7" for the `memory.operation` head=1.0 sampling discipline (e.g., AC #3: *"Span head-sampled at 1.0 per AS spec §14.7 sampling-row (write/update/delete head=1.0 audit-floor commitment per ADR-D3 v1.2 §1.8.1)"*). Empirical verification at HEAD: AS spec v1.5 §14.7 contains the `memory.*` 6-attribute namespace TABLE (lines 1157-1166); the sampling discipline table containing the `memory.operation` row (`head=1.0 at kind ∈ {write, update, delete}; base-rate at kind ∈ {read, list}`) lives at §14.8 (lines 1168-1182). The cite drift originates in an AS spec internal inconsistency: §14.7 footer note (lines ~95) claims `"sampling discipline (head=1.0 at kind ∈ {write, update, delete} audit-floor; base-rate at kind ∈ {read, list}) declared at this §14.7 are canonical"` — but the sampling discipline is structurally declared at §14.8, not §14.7. The plan absorbed the AS spec footer-note's incorrect self-claim. Per `Project_Workflow_v1_8.md` §7.4 citation byte-exact discipline + workspace `CLAUDE.md` invariant I-1: cites must point at the actual section, not at a footnote's mis-claim of its own location.
- **Discriminator that classifies as Class 2:** (a) affects substantive content of current-phase artifact — citation precision is a §4.2 + §9 spec-traceability discipline obligation; the cite drift is also an AS spec adjacent defect that the plan should either correct (cite §14.8) or surface (note the AS spec internal inconsistency) but not silently absorb.
- **Evidence:** Verified via grep against `design-substrate/Spec_Action_Surface_v1.md`: §14.7 starts at line 1157 with the 6-attribute namespace table; §14.8 starts at line 1168 with "### §14.8 Sampling discipline + audit-floor commitments" header; `memory.operation` sampling row is at line 1179, inside §14.8.
- **Anti-fabrication attack engaged:** A4-adjacent (citation precision; the cite resolves to the wrong section even though the source exists).
- **Axis-domain attack engaged:** AS — namespace-vs-sampling discipline (different §-pin owners; §14.7 owns the attribute schema, §14.8 owns the sampling commitment).
- **Resolution path:** At U-RT-81 ACs #3 + #4 + change-note, cite "AS spec §14.8 sampling-row for `memory.operation`" (not "§14.7 sampling-row"). Optionally surface the AS spec footer-note self-claim drift as a new adjacent-defect (iv) so the next AS-spec revision pass reconciles the footer-note's location claim.

### F2-04 — CP spec §25.3.3.4 citation may not resolve at CP spec v1.11

- **Location:** `Implementation_Plan_Harness_Runtime_v2_14.md` U-RT-81 Implements line + adjacent-defect (iii)
- **Defect:** Plan cites *"propagate ... to driver `try/except` at `workflow_driver.py:618-635` per C-CP-25 §25.3.3.4 step-dispatcher invocation site"* + adjacent-defect (iii) cites *"the line cite for the try/except boundary itself is :618-635"*. Empirical verification at HEAD via grep `§25\.3\.3\|25\.3\.3\.4` against `design-substrate/Spec_Control_Plane_v1_11.md` returns **empty**. The cite is referenced in `harness-cp/src/harness_cp/workflow_driver.py:203` docstring as *"The driver's try/except per C-CP-25 §25.3.3.4"* — confirming the cite has been used historically — but cannot be verified to currently exist in CP spec v1.11. Possible causes: §25.3.3.4 was renumbered in a recent CP spec revision (v1.10 → v1.11 path-γ absorption); §25.3.3.4 was struck; the cite has always been imprecise (e.g., actual section is §25.3.3 without `.4` decimal).
- **Discriminator that classifies as Class 2:** (a) affects substantive content of current-phase artifact — citation precision per workspace `CLAUDE.md` I-1 + `Project_Workflow_v1_8.md` §7.4. Pre-decided as Class 2 (not Class 3 for upstream-revision) because the citation appears in CP spec v1.11's prior versions and reflects a real driver-try/except contract — only the §-pin needs resolution; CP-spec revision is not the resolution path.
- **Evidence:** `grep -n "§25\.3\.3\|25\.3\.3\.4" design-substrate/Spec_Control_Plane_v1_11.md` returns empty (verified at HEAD `c2f90e3`); but the cite resolves to a real surface at `harness-cp/src/harness_cp/workflow_driver.py:203` docstring.
- **Anti-fabrication attack engaged:** A4 (citation may not resolve; A4 is escalated to Class 3 only if the underlying claim is foundational — here the claim is verifiable in code, just the §-pin needs re-resolution).
- **Axis-domain attack engaged:** CP — spec section numbering stability across path-γ absorption.
- **Resolution path:** Grep CP spec v1.11 for the actual §-pin governing the driver try/except step-dispatcher contract (likely §25.3.3 or §25.4 step-dispatcher row); update U-RT-81 cite + adjacent-defect (iii) prose. If the cite is genuinely missing from CP spec v1.11, surface as a separate Class 3 finding requiring CP-spec revision-pass to re-add (currently surfaced as Class 2 pending grep-resolution).

---

## Class 1 findings (minor — documentation drift)

### F1-01 — "5 CRUD callbacks per ADR-D3 §1.1 #11" framing imprecise — 5-callback enumeration originates at runtime spec §14.12.1, not ADR-D3

- **Location:** `Implementation_Plan_Harness_Runtime_v2_14.md` change-note opening paragraph + U-RT-76 Signatures + multiple "per ADR-D3 §1.1 #11" cites
- **Defect:** Plan cites *"5 CRUD callbacks per ADR-D3 §1.1 #11 on `/memories` paths"* + similar at multiple sites. Empirical: ADR-D3 v1.2 §1.1 #11 (line 89) says *"filesystem-style interface in `/memories` Claude controls"* + Memory tool primitive metadata + line 538 references *"(create/read/update/delete file operations)"* — 4 CRUD operations (CRUD = create/read/update/delete) + filesystem-style. The 5-callback enumeration (`view` / `create` / `delete` / `str_replace` / `insert`) originates at runtime spec v1.17 §14.12.1, not ADR-D3 §1.1 #11. The cite ADR-D3 §1.1 #11 is the *foundational* primitive declaration; the *5-callback Protocol shape* is a runtime-spec elaboration (informed by Anthropic SDK `BetaAbstractMemoryTool` helper enumeration). Cite shape only — not a substantive defect; the cite chain is correct (ADR-D3 → runtime spec §14.12.1).
- **Discriminator:** drift only — does not affect substantive content; cite shape clarity only.
- **Evidence:** ADR-D3 v1.2 line 89 + line 538 (verified) — 4-op CRUD framing; runtime spec v1.17 §14.12.1 lines 2271-2304 — 5-callback Protocol declaration.
- **Resolution:** Inline fix — change "5 CRUD callbacks per ADR-D3 §1.1 #11" to "5 CRUD callbacks per runtime spec §14.12.1 (per ADR-D3 §1.1 #11 filesystem-style interface foundation)" at each occurrence in the plan.

### F1-02 — §14.12.2 invariant 4 "no retry inside callback" not explicitly covered by any AC

- **Location:** `Implementation_Plan_Harness_Runtime_v2_14.md` §3 coverage matrix C-RT-22 §14.12.2 row
- **Defect:** Spec v1.17 §14.12.2 invariant 4 reads: *"No retry inside the callback. Storage-backend I/O failures propagate as `MemoryCallbackIOError` → `RT-FAIL-MEMORY-CALLBACK-IO` (transient per C-RT-14 fail-class taxonomy). Retry MAY be wrapped at the C-RT-15 dispatcher level (deferred to follow-on retry-wrap arc per implementation discretion); v1.17 contract does not specify retry semantics inside the callback boundary."* Plan coverage row for §14.12.2 cites U-RT-77 (path validation + concurrency) + U-RT-81 (span emission per callback) — neither AC explicitly verifies "no retry inside callback". U-RT-77 ACs do not explicitly assert the absence of retry logic in the 5 callback methods. The invariant is implicit (no retry is implemented because no AC requires retry) but not explicitly tested.
- **Discriminator:** drift only — implicit handling is a §10 anti-pattern "smoothing" risk if material; here the invariant is bounded and the U-RT-77 AC body's absence of retry is structurally evident.
- **Evidence:** U-RT-77 ACs #1-8 cover create/view/delete/str_replace/insert / path-discipline / concurrency / pyright — no AC for "no retry inside callback".
- **Resolution:** Inline fix — add an AC at U-RT-77 (e.g., AC #9): *"Callbacks do not retry on `MemoryCallbackIOError`; transient I/O failure propagates immediately to caller (verified via mock filesystem raising transient `OSError` — backend raises `MemoryCallbackIOError` on first attempt without retry)."*

### F1-03 — §14.12.5 invariant 6 backend-lifecycle shutdown-registry hook not addressed at U-RT-77

- **Location:** `Implementation_Plan_Harness_Runtime_v2_14.md` §3 coverage matrix C-RT-22 §14.12.5 row
- **Defect:** Spec v1.17 §14.12.5 invariant 6 (verified at runtime spec line 2385) reads: *"Backend lifecycle owned by backend. Per-backend cleanup (e.g., S3 client connection close at shutdown) deferred to implementation discretion via C-RT-10 shutdown sequence — implementations MAY register shutdown hooks via `ctx.shutdown_registry.register(...)` (existing primitive) for per-backend cleanup; not required."* Plan coverage row for §14.12.5 covers invariants 1-5 (resolved-once / Protocol-conformance / path-discipline / secret-redaction / sampling) — invariant 6 not covered. Per spec text, registration is "not required" → intentional non-coverage; U-RT-77 LocalFilesystemMemoryToolBackend at v2.14 scope does not need shutdown hooks (filesystem closes per-file at I/O completion). However, the coverage matrix should explicitly acknowledge invariant 6 as "spec-deferred: not required at filesystem backend; will become coverage-relevant at follow-on S3 / DATABASE backend arcs" so the executor at U-RT-77 doesn't silently extend by adding unneeded shutdown logic.
- **Discriminator:** drift only — coverage matrix completeness; the invariant's "not required" qualifier means the non-coverage is correct, only the matrix should surface the rationale.
- **Evidence:** §3 coverage matrix row for §14.12.5 invariants lists 1-5 only; invariant 6 absent.
- **Resolution:** Inline fix — extend §3 coverage matrix C-RT-22 §14.12.5 row with explicit note: *"Invariant 6 (backend-lifecycle shutdown_registry hook) spec-deferred 'not required' — non-coverage intentional at v2.14 filesystem backend scope; becomes coverage-relevant at future S3 / DATABASE backend arcs per §14.D follow-on retirement-batch scope."*

---

## Findings considered and rejected (transparency)

The following attack vectors were applied. Vectors that surfaced findings are listed above; vectors that did not surface findings are recorded here per skill §"FM-J: Empty rejected-findings section" discipline.

1. **Atomicity per implementation-planner SKILL §3 (4 criteria) on each of 7 units (U-RT-76..U-RT-82).** Walked each unit against the 4 criteria (single coherent change / single focused session / independently testable / coherent rollback boundary). All 7 pass.
   - U-RT-76 bundles Protocol + sub-model + 2 typed exceptions in one file — coherent as "type-carriers introduction"; single focused session; testable via importable + isinstance; coherent rollback boundary (one file). Pass.
   - U-RT-79 bundles RuntimeConfig + HarnessContext field appends across 2 files — coherent as "schema-extension landing" (analogous to v2.12 U-RT-72 pattern that bundled mcp_client_host + tool_dispatcher field appends across the same 2 files). Pass.
   - U-RT-80 bundles factory + stage-5 wiring + fail-class registration across 3 files — coherent as "stage-5 factory landing" (analogous to v2.12 U-RT-75 pattern). Pass.
   - U-RT-81 amends single file (`llm_dispatch.py`) with detect-helper + callback-helper + span-helper + composer-step body — coherent as "C-RT-15 §14.5.1 amendment landing"; α/β/γ discretion bounded behind `_execute_with_memory_callbacks` helper signature. Pass.
   - U-RT-82 separate e2e test file with 2 test functions (write-path + skip-gating) — coherent as "e2e test landing"; deterministic-prompt fixture eliminates LLM-behavior flakiness. Pass.
2. **Spec-traceability against runtime spec v1.17 §14.12.1-7.** §14.12.1 architectural surfaces covered (U-RT-76 + U-RT-78); §14.12.2 per-callback discipline covered (U-RT-77 + U-RT-81; invariant 4 surfaced as F1-02); §14.12.3 lifecycle stage covered (U-RT-80); §14.12.4 failure-mode taxonomy covered (U-RT-80 + U-RT-81); §14.12.5 invariants covered 1-5 (invariant 6 surfaced as F1-03 — spec-deferred); §14.12.6 X-AL-2 retirement implications covered (U-RT-82); §14.12.7 deferrals correctly NOT coverage targets per FM-2.
3. **Cross-axis cascade verification (plan asserts ZERO cascade).** Grep against `design-substrate/Cross_Axis_Composition_Document_v2_8.md` for `memory_tool|MemoryToolStorageBackend` returns empty — CXA v2.8 has no Memory tool rows. Per fork doc §5 + architect §13.6.D operator-ratified ruling: consumption of already-landed `MemoryToolStorageBackend` enum + `memory_tool_storage_backend` resolver at `harness-as/src/harness_as/anthropic_graceful_degradation.py:88` + `:248` is treated as cross-package consumption against existing carriers, NOT a new CXA-enumerable edge. The ZERO-cascade claim is operator-ratified and verifiable. Pass.
4. **Dependency-graph acyclicity (Kahn execution against L9-octies edges).** 12 within-cluster edges declared; acyclic verified per change-note §2 DAG topology delta — independently re-walked: U-RT-76 (no deps) → {U-RT-77, U-RT-78} → U-RT-79 → U-RT-80 → U-RT-81 → U-RT-82. No cycle path; topological sort exists. Pass.
5. **Missing dependency surfacing per §7 no-transitive-omission discipline.** Walked each unit's `Depends on:` line against signatures + AC body — U-RT-81 missing U-RT-76 surfaced as F2-02; other units' dep declarations match their direct imports/types/AC requirements.
6. **FM-2 no-extension discipline on U-RT-77 LocalFilesystemMemoryToolBackend implementation choices.** U-RT-77 picks `defaultdict[str, asyncio.Lock]` for concurrency (stdlib; spec §14.12.2 step 3 explicitly says "MAY use `asyncio.Lock` per path"); takes `root: Path` constructor (spec §14.12.7 defers PathClass extension to implementation-arc discretion; `root: Path` direct-pass respects deferral); raises `MemoryPathViolationError` BEFORE filesystem I/O (spec §14.12.5 invariant 3 mandates this); 100-concurrent-call test invocation (test-mechanism, not spec extension). All implementation choices stay within spec-committed surface. Pass.
7. **Inner-loop α/β/γ mechanism discretion preservation at U-RT-81.** U-RT-81 ACs verify the contract-surface (callback wiring at #2; `memory.*` emission at #3, #4; fail-class propagation at #5, #6; secret-redaction at #7; backwards-compat at #8) — none of these ACs require a specific α/β/γ choice. The `_execute_with_memory_callbacks(...)` helper signature encapsulates mechanism choice behind a stable boundary. Discretion preserved per FM-2. Pass.
8. **Adjacent-defects 3-pack verification (not plan-side patches in disguise).** (i) Stage-5 ordering self-contradiction — explicitly NOT patched; U-RT-80 picks the "arbitrary" reading; surface-only ✓. (ii) §14.5.1 step 4 enum non-bijective — surfaced as F2-01 (the lock at U-RT-81 #3 IS a plan-body patch; the "NOT patched per FM-2" framing is inconsistent). (iii) workflow_driver.py line-range — explicitly patched at U-RT-81 cite (`:618-635`); change-note discloses the patch + surfaces spec-side cite drift for future spec revision ✓.
9. **Citation byte-exactness against runtime spec v1.17.** Spot-checked §14.5.1 + §14.12.1 + §14.12.2 + §14.12.3 + §14.12.4 + §14.12.5 + §14.12.6 + §3 C-RT-02 + §4 C-RT-04 cites — all resolve at HEAD. ADR-D3 §1.1 #11 cite framing surfaced as F1-01 (cite chain correct; framing imprecise). AS spec §14.7 vs §14.8 sampling-row cite drift surfaced as F2-03. CP §25.3.3.4 cite surfaced as F2-04 (grep returns empty in current CP v1.11).
10. **Coverage-matrix gap audit against §14.12.5 6-invariant set.** Invariants 1-5 covered; invariant 6 surfaced as F1-03 (spec-deferred "not required" — non-coverage intentional).
11. **Anti-fabrication Attack A1 (silent grounding collapse).** Plan cites concrete file:line locations + spec section numbers + ADR section numbers throughout; no "engineering posts" or weak-source claims. Pass.
12. **Anti-fabrication Attack A5 (missing uncertainty signals).** Plan does not introduce confidence-tagged claims (it inherits from spec-side `[HIGH]` tags via cite chain); no uncalibrated claims requiring [HIGH]/[MODERATE]/[SPECULATIVE] tags. Pass.

**Patterns not engaged:** A2 (silent scope narrowing — N/A; plan scope is operator-ratified at §14.C Memory-only); A7 (weak-source escalation — N/A; no source claims escalated); A9 (cross-project context bleed — N/A; all cites resolve to `design-substrate/` filesystem).

---

## Disposition

**Clearance with current-phase revision (per §4.1.2).** 4 Class 2 findings require plan-body revision; 3 Class 1 inline fixes recommended. No Class 3 findings → no Phase-3a/3b/3d/5 upstream-phase artifact revision triggered. No `Project_Workflow_v1_8.md` §2.7.6 Phase-7 fork triggered (the spec-prose-plan-body drift at F2-01 is in-scope for plan-body revision; the cite drifts at F2-03 + F2-04 are in-scope for plan-body cite-fix; the missing dep at F2-02 is in-scope for plan-body dep-list edit).

**Recommended revision-pass sequence (v2.14 → v2.15):**

1. **F2-01** — Restructure change-note adjacent-defects section to disambiguate "patched at plan-body" (the §14.5.1 enum lock) vs "deferred to follow-on spec revision" (the §14.12.3 stage-5 ordering ambiguity). Either split section into two sub-sections OR re-frame adjacent-defect (ii) header as "Patched at plan-body U-RT-81 AC #3 per spec-prose-plan-body drift pattern; future spec revision SHOULD reconcile prose."
2. **F2-02** — Add U-RT-76 as direct dep at U-RT-81 `Depends on:` line; clarify semantic reason (Protocol type + typed-exception declarations); optionally revise U-RT-77 dep cite-reason.
3. **F2-03** — Replace "AS spec §14.7 sampling-row" with "AS spec §14.8 sampling-row for memory.operation" at U-RT-81 ACs #3 + #4 + change-note. Optionally surface AS spec §14.7 footer-note self-claim drift as new adjacent-defect (iv) for future AS-spec revision-pass.
4. **F2-04** — Grep CP spec v1.11 for the actual §-pin governing the driver try/except contract; if found, update U-RT-81 + adjacent-defect (iii) cite. If genuinely absent, escalate to Class 3 (CP spec revision-pass owed).
5. **F1-01** — Inline cite-shape clarification at change-note + U-RT-76 + U-RT-78 occurrences.
6. **F1-02** — Add AC at U-RT-77 verifying "no retry inside callback" invariant.
7. **F1-03** — Extend coverage matrix C-RT-22 §14.12.5 row with explicit invariant-6 spec-deferred note.

**Cluster opening at U-RT-76 should NOT proceed until F2-04 (CP §25.3.3.4 grep-verification) is resolved** — if the cite genuinely doesn't resolve in CP spec v1.11, it escalates to Class 3 and triggers a CP-spec revision-pass back-flow per workspace `CLAUDE.md` §4.3 before the runtime-plan unit can land its citation against a non-existent spec surface. The other 6 findings can be absorbed at v2.15 in parallel with cluster opening if F2-04 resolves cleanly.

**No systemic cross-artifact pattern surfaced** (single-artifact review; pattern detection requires ≥3 artifacts per skill §6 + §7 audit).

---

## Filing footer

| Field | Value |
|---|---|
| Artifact reviewed | `design-substrate/Implementation_Plan_Harness_Runtime_v2_14.md` at commit `c2f90e3` |
| Checkpoint | P6-CK (Phase-7 pre-implementation review mode — L9-octies cluster opening at U-RT-76) |
| Phase 7 fork triggered | NONE (no §2.7.6 Phase-7 fork class triggered; all 4 Class 2 findings + 3 Class 1 findings resolvable at plan-body revision) |
| Class 3 / Class 2 / Class 1 counts | 0 / 4 / 3 |
| Disposition | Clearance with current-phase revision (v2.14 → v2.15 absorption) per §4.1.2 |
| F2-04 resolution dependency | CP spec v1.11 §-pin grep-verification gate before L9-octies opens at U-RT-76; if cite genuinely missing → escalate F2-04 to Class 3 + back-flow per CLAUDE.md §4.3 |
| Adversarial-reviewer mode | Phase-7 pre-implementation review (per skill §"Use this skill when (Phase-7 pre-implementation review mode)") |
| Date | 2026-05-23 |
