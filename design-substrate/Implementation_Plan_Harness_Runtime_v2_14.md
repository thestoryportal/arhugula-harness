# Implementation Plan — Harness Runtime v2.14

## Change-note (v2.13 → v2.14)

**Scope of revision.** Class 1 fork resolution absorption pass for `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §16 RATIFIED-AMENDED (operator-ratified 2026-05-23, same session as §11 PROVISIONAL filing + §13 systems-architect Mode 3 recommendation + §14 routing). Absorbs runtime spec v1.16 → v1.17 (2026-05-23, commit `3810320`): NEW §14.5.1 sub-section at C-RT-15 (Memory tool storage-backend callback binding); NEW §14.12 C-RT-22 contract (`MemoryToolRegistry` + `MemoryToolStorageBackendProtocol` — 5 CRUD callbacks per ADR-D3 §1.1 #11 on `/memories` paths); NEW optional field `memory_tool_backend_config` at §3 C-RT-02 RuntimeConfig; NEW field `memory_tool_registry` at §4 C-RT-04 HarnessContext; 3 NEW fail classes (`RT-FAIL-MEMORY-BACKEND-RESOLUTION` / `RT-FAIL-MEMORY-CALLBACK-IO` / `RT-FAIL-MEMORY-PATH-VIOLATION`); NEW stage-5 `materialize_memory_tool_registry_stage` factory contract.

**Source of fix.** `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` §16 operator-ratified 2026-05-23:
- **§14.A** — Amend §11 in-place (preserve §6.D operator-opt-in; revise §6.A/B/C/E)
- **§14.B** — Accept §13.6 architect Mode 3 recommendation (Memory at NEW callback-registry contract consumed by C-RT-15, NOT C-RT-19 extension; MCP/Memory/Files structurally divergent per ADR-D3 §1.1 #10 + #11)
- **§14.C** — **Memory-only at this opening; Files arc deferred indefinitely** (no current downstream blocker; §14.6 files.* footer note NOT authored at AS spec v1.5; no Files API contract authoring at runtime spec v1.17)
- **§14.D** — **Local-filesystem backend at retirement-gate** scope; S3 / ENCRYPTED_FILESYSTEM / DATABASE deferred to operator-discretion follow-on retirement-batch arcs
- **§14.E** — N/A (Files deferred per §14.C)

**Spec authority chain.** Runtime spec v1.17 (4 amendment sites — §3 C-RT-02 row append + §4 C-RT-04 row append + §14.5.1 NEW sub-section + §14.12 NEW C-RT-22 contract). AS spec v1.5 §14.7 NEW producer-site reference footer note (co-published 2026-05-23 same commit). All other axis artifacts unchanged: harness-core plan v1.2 / CP spec v1.11 / CP plan v2.17 / OD spec v1.9 / OD plan v2.15 / CXA v2.8 / Meta-Arch v1.5 — ZERO cross-axis cascade per fork doc §5 + architect §13 recommendation §13.6.D.

**Plan shape preserved.** v2.13's L9-septies cluster + L9-sexies cluster + all prior content preserved verbatim. NEW **L9-octies** cluster appended at §1 below, decomposing C-RT-22 + C-RT-15 §14.5.1 amendment into 7 atomic units (U-RT-76..U-RT-82). NO v2.13 unit body change; NO v2.13 AC change; NO v2.13 DAG topology change at the L9-septies / L9-sexies internal structure; ONLY a new L9-octies cluster appended with internal edges plus 2 within-cluster cross-package consumption cites against already-landed `MemoryToolStorageBackend` enum at `harness-as/src/harness_as/anthropic_graceful_degradation.py:88` (no new CXA edge per fork doc §5).

**Sections preserved verbatim from v2.13.** Entire v2.13 file body preserved (change-note + §1 L9-septies cluster + §2 DAG topology + §3 coverage matrix + filing footer). The v2.12 + v2.11 + ... + v2.0 + v2 chain preserved transitively.

**Status posture.** Proposed (v2.13) → **Proposed (v2.14)**. v2.14 is an additive new-cluster authoring under FM-2 no-extension discipline — 7 NEW units decomposing the NEW v1.17 contract surface (C-RT-22 + C-RT-15 §14.5.1); no v2.13 unit re-decomposition; no v2.13 AC body change; no contract removal.

**Inner-loop mechanism discretion (per spec §14.5.1 + §14.12.7 deferral).** The composer-step amendment at U-RT-81 below cites the C-RT-15 §14.5.1 callback-binding contract surface verbatim per FM-3 verbatim discipline but does NOT pre-commit to one of the three landing options enumerated at spec v1.17 §14.5.1 (α SDK-internal beta `context-management-2025-06-27` handling / β harness-authored inner loop / γ sibling-composer wrap). The unit AC verifies the contract-surface invariants (callback wiring; `memory.*` emission per AS spec v1.5 §14.7; fail-class propagation per C-RT-22 §14.12.4) — implementation arc selects α/β/γ per empirical SDK-capability verification at landing per FM-2 no-extension discipline.

**Callback → kind enum mapping locked at plan-body (advisor coherence-pass finding 2026-05-23).** Spec v1.17 §14.5.1 step 4 says `memory.operation.kind ∈ {read, write, update, delete, list}` "corresponding to the 5 CRUD callbacks", but the 5 Protocol callbacks (`view` / `create` / `delete` / `str_replace` / `insert`) do NOT bijectively map to the 5 enum values (`list` has no callback; both `str_replace` + `insert` naturally map to `update`). Per `[[spec-prose-plan-body-drift-pattern]]`: the plan locks the mapping at U-RT-81 AC #3 to give the executor a deterministic instruction (mapping: `view → read`, `create → write`, `str_replace → update`, `insert → update`, `delete → delete`; `list` enum value is dead at v1.17 — never emitted by any callback site). The spec-prose ambiguity surfaced as adjacent-defect (ii) below.

**Adjacent defects surfaced (NOT patched at this arc per FM-2 no-extension discipline).**

- **(i) §14.12.3 stage-5 ordering self-contradiction.** Spec v1.17 §14.12.3 says "Runs at stage 5 after `materialize_runtime_tool_dispatcher_stage`" AND "ordering is arbitrary within stage 5 LOOP_INIT" in consecutive sentences. U-RT-80 picks the second reading (no ordering dependency on tool dispatcher) per the spec's explicit "arbitrary" sentence. Surfaced for next runtime-spec revision pass to resolve.
- **(ii) §14.5.1 step 4 `memory.operation.kind` enum non-bijective with 5-callback Protocol.** Per the locked mapping above: `list` is dead at v1.17 (no callback emits it); `str_replace` + `insert` both map to `update` (2 callbacks → 1 enum value). The spec-prose "corresponding to the 5 CRUD callbacks" is loose; a future spec revision SHOULD either (a) add a callback for `list` (e.g., a `list` CRUD callback per `/memories` directory enumeration semantics) OR (b) strike `list` from the enum + document the non-bijective `update` mapping at §14.5.1 step 4 prose.
- **(iii) U-RT-81 cite at v1.17 §14.5.1 step 5 to `workflow_driver.py:380-389`.** Empirically verified at HEAD: actual driver try/except blocks are at `workflow_driver.py:618-635` per step-dispatcher invocation site (line 380-389 docstring earlier in the file references `§25.3.3.4 try/except`; the line cite for the try/except boundary itself is :618-635). Plan U-RT-81 cite below uses the corrected line range. Spec-side cite at v1.17 §14.5.1 step 5 should be corrected at next runtime-spec revision pass.

**Downstream absorption owed (post-v2.14).**
(a) Workspace `CLAUDE.md` §2.3 runtime spec row already at v1.17 per spec-writer commit `3810320`; no further bump at this arc.
(b) Workspace `CLAUDE.md` §2.4 runtime plan row version bump (v2.13 → v2.14); unit count 76 → 83 (U-RT-00..U-RT-70 + U-RT-71..U-RT-82). Co-published this arc.
(c) Workspace `CLAUDE.md` §2.3 AS spec row already at v1.5 per spec-writer commit `3810320`; no further bump at this arc.
(d) Phase 7 cluster-open authorization for L9-octies at next session per `phase-7-implementation` skill discipline. Cluster sequencing: L9-octies opens with U-RT-76 as the L0 entry-point (U-RT-76 → {U-RT-77, U-RT-78} → U-RT-79 → U-RT-80 → U-RT-81 → U-RT-82 per DAG below).
(e) NO CXA v2.8 amendment owed at this arc per fork doc §5 + architect §13.6.D — `memory_tool_registry` ctx-binding consumes already-landed `MemoryToolStorageBackend` enum carrier without new cross-axis composition seam.
(f) NO CP / OD / AS plan amendments owed at this arc per fork doc §5 (ZERO cross-axis cascade).
(g) NO harness-core plan amendment owed at this arc — Memory tool primitives all home at harness-runtime per §13.6.A architect recommendation (Runtime owns executable lifecycle; harness-core not implicated).
(h) Retirement-batch arc owed post-landing: batch-12 (or later) records H_T-CP-16 STILL-BOUNDED → RETIRE-READY per §16 §6.D operator-opt-in pattern (structural criterion-B MET via factory wiring at U-RT-80 landing); full RETIRED gates on operator-bound `memory_tool_backend_config` non-default + local-filesystem-backend e2e (U-RT-82) exercise at follow-on arc per §16 §6.C v2 C.vii scope. H_T-CP-17 status unchanged (PARTIAL preserved per §14.C Files arc deferral).

---

## §1 — L9-octies cluster — NEW: C-RT-22 Memory tool primitive + C-RT-15 §14.5.1 callback-injection amendment

### U-RT-76 — MemoryToolStorageBackendProtocol + MemoryToolBackendConfig sub-model carriers

- **Implements:** Runtime spec **v1.17** §14.12.1 (architectural surfaces introduced — `MemoryToolStorageBackendProtocol` PEP-544 Protocol declaration + `MemoryToolBackendConfig` RuntimeConfig sub-model).
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/memory_tool_types.py` (NEW — Protocol + sub-model module).
- **Signatures:**
  - `@runtime_checkable class MemoryToolStorageBackendProtocol(Protocol)` with 5 async methods (`view(path: str) -> bytes` / `create(path: str, content: bytes) -> None` / `delete(path: str) -> None` / `str_replace(path: str, old: str, new: str) -> None` / `insert(path: str, line: int, content: str) -> None`) verbatim per §14.12.1.
  - `@dataclass(frozen=True) class MemoryToolBackendConfig` with fields `backend: MemoryToolStorageBackend` + `backend_params: Mapping[str, str] | None = None` verbatim per §14.12.1.
  - 2 typed exceptions: `class MemoryPathViolationError(Exception)` + `class MemoryCallbackIOError(Exception)` — consumed by C-RT-22 §14.12.4 fail-class mapping at U-RT-80/U-RT-81 surfaces.
  - `MemoryToolStorageBackend` enum imported from `harness_as.anthropic_graceful_degradation` (already landed at `harness-as/src/harness_as/anthropic_graceful_degradation.py:88`; no new edge per fork doc §5).
- **Depends on:** (none — foundational carrier within L9-octies cluster; consumes already-landed `MemoryToolStorageBackend` enum from harness-as as cross-package import).
- **ACs:**
  1. `MemoryToolStorageBackendProtocol` importable; `@runtime_checkable` decorator applied; passes `isinstance(obj, MemoryToolStorageBackendProtocol)` at runtime against an object implementing all 5 methods with correct async signatures.
  2. `MemoryToolBackendConfig` instantiable as frozen dataclass; `backend` field accepts any `MemoryToolStorageBackend` enum value; `backend_params` defaults to `None`.
  3. `MemoryPathViolationError` + `MemoryCallbackIOError` importable as `Exception` subclasses (separate types — not aliased).
  4. Cross-package import of `MemoryToolStorageBackend` from `harness_as.anthropic_graceful_degradation` resolves at pyright strict + at runtime.
  5. Importable; pyright strict mode passes.

### U-RT-77 — LocalFilesystemMemoryToolBackend implementation (FILESYSTEM enum)

- **Implements:** Runtime spec **v1.17** §14.12.3 step 2 (`MemoryToolStorageBackend.FILESYSTEM` → filesystem-backed implementation) + §14.12.2 per-callback invocation discipline (path validation at every callback; async-only Protocol surface; no retry inside callback) + §14.12.5 invariants 3 (path discipline enforced at backend BEFORE I/O) + 6 (per-backend lifecycle owned by backend).
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/memory_tool_filesystem.py` (NEW — filesystem-backed implementation module).
- **Signatures:**
  - `class LocalFilesystemMemoryToolBackend` satisfying `MemoryToolStorageBackendProtocol` (PEP-544 conformance verified via `@runtime_checkable` at U-RT-76).
  - Constructor: `def __init__(self, *, root: Path)` — accepts a deployment-surface-resolved root path (e.g., the parent of `/memories` scope on disk).
  - 5 async methods implementing the Protocol — each MUST validate `path` against `/memories/` scope per §14.12.5 invariant 3 BEFORE filesystem I/O.
  - Path-validation helper: `def _validate_path(self, path: str) -> Path` raising `MemoryPathViolationError` (from U-RT-76 typed-exception carriers) on path-traversal attempts (e.g., paths containing `..`, absolute paths outside scope, paths not prefixed with `/memories/`).
  - Concurrency: per-path `asyncio.Lock` per §14.12.2 invariant 3 (backend implementation owns concurrency model) — backend MAY use `defaultdict[str, asyncio.Lock]` keyed on validated path.
- **Depends on:** [U-RT-76 (Protocol + typed exceptions)].
- **ACs:**
  1. `LocalFilesystemMemoryToolBackend(root=tmp_path)` instantiates without error; satisfies `MemoryToolStorageBackendProtocol` (verified via `isinstance(backend, MemoryToolStorageBackendProtocol)` after U-RT-76 makes the Protocol `@runtime_checkable`).
  2. `await backend.create("/memories/foo.txt", b"hello")` writes file; `await backend.view("/memories/foo.txt") == b"hello"`; `await backend.delete("/memories/foo.txt")` removes file; subsequent `view` raises `MemoryCallbackIOError`.
  3. `await backend.str_replace("/memories/foo.txt", "hello", "world")` after create → `view` returns `b"world"`.
  4. `await backend.insert("/memories/foo.txt", 2, "inserted\n")` after create with multi-line content → expected line 2 contains `"inserted\n"`.
  5. Path-discipline enforcement: `await backend.view("../etc/passwd")` raises `MemoryPathViolationError` BEFORE filesystem I/O attempt (verified via mock filesystem call recorder — no `open()` invoked).
  6. Path-discipline enforcement: `await backend.view("/etc/passwd")` raises `MemoryPathViolationError` (absolute path outside `/memories/` scope).
  7. Concurrency: 100 concurrent `create` calls to distinct paths complete without exception; 100 concurrent `str_replace` calls to the same path complete without race (final content deterministic per serial semantics of per-path lock).
  8. Importable; pyright strict mode passes.

### U-RT-78 — MemoryToolRegistry class

- **Implements:** Runtime spec **v1.17** §14.12.1 (`MemoryToolRegistry` class declaration — `resolve_backend(deployment_surface) → MemoryToolStorageBackendProtocol` + `configured_backend` property returning `MemoryToolStorageBackend` enum value) + §14.12.5 invariant 1 (storage-backend resolved exactly once per bootstrap; no re-resolution at dispatch-time).
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/memory_tool_registry.py` (NEW — registry module).
- **Signatures:**
  - `class MemoryToolRegistry`:
    - Constructor: `def __init__(self, *, backend: MemoryToolStorageBackendProtocol, configured_backend: MemoryToolStorageBackend)` — receives the pre-resolved backend implementation + the enum-value identity for span-attribute emission per §14.12.5 invariant 1 (resolution happens at factory; registry stores the result).
    - `def resolve_backend(self, deployment_surface: DeploymentSurface) -> MemoryToolStorageBackendProtocol` — returns the stored backend (deployment_surface param accepted for API-shape stability per §14.12.1 signature but ignored at MVP since resolution is bootstrap-time-frozen per invariant 1; future multi-surface support is implementation-arc discretion per §14.12.7).
    - `@property def configured_backend(self) -> MemoryToolStorageBackend` — returns the stored enum value.
  - `DeploymentSurface` imported from existing harness-runtime config types.
- **Depends on:** [U-RT-76 (Protocol type)].
- **ACs:**
  1. `MemoryToolRegistry(backend=fake_backend, configured_backend=MemoryToolStorageBackend.FILESYSTEM)` instantiates; `.resolve_backend(DeploymentSurface.LOCAL_DEV) is fake_backend`; `.configured_backend == MemoryToolStorageBackend.FILESYSTEM`.
  2. `resolve_backend` is callable with any `DeploymentSurface` value and returns the same backend instance (bootstrap-time-frozen per invariant 1).
  3. Importable; pyright strict mode passes.

### U-RT-79 — RuntimeConfig.memory_tool_backend_config + HarnessContext.memory_tool_registry field landings

- **Implements:** Runtime spec **v1.17** §3 C-RT-02 RuntimeConfig field-table extension (NEW optional `memory_tool_backend_config: MemoryToolBackendConfig | None = None`) + §4 C-RT-04 HarnessContext field-table extension (NEW `memory_tool_registry: MemoryToolRegistry`, stage 5).
- **Files:**
  - `harness-runtime/src/harness_runtime/config.py` (EXTEND — `RuntimeConfig` Pydantic v2 BaseModel field-table extension).
  - `harness-runtime/src/harness_runtime/harness_context.py` (EXTEND — `_MutableHarnessContext` + `HarnessContext` field-table extension; mirrors v2.12 U-RT-72 pattern for `mcp_client_host` + `tool_dispatcher` field additions).
- **Signatures:**
  - `class RuntimeConfig`: append optional field `memory_tool_backend_config: MemoryToolBackendConfig | None = None`. `MemoryToolBackendConfig` imported from `harness_runtime.lifecycle.memory_tool_types` per U-RT-76.
  - `class _MutableHarnessContext`: append field `memory_tool_registry: MemoryToolRegistry | None = None` (None during stages 1-4; bound at stage 5).
  - `class HarnessContext` (frozen post-bootstrap): append field `memory_tool_registry: MemoryToolRegistry` (non-Optional — bootstrap fails if stage 5 didn't bind).
- **Depends on:** [U-RT-76 (MemoryToolBackendConfig sub-model), U-RT-78 (MemoryToolRegistry type)].
- **ACs:**
  1. `RuntimeConfig(deployment_surface=..., ..., memory_tool_backend_config=None)` instantiates without ValidationError.
  2. `RuntimeConfig(...)` instantiated WITHOUT the new field preserves v1.16-shape backwards-compatibility (field defaults to `None` per Pydantic field default; existing callers do not break).
  3. `RuntimeConfig(..., memory_tool_backend_config=MemoryToolBackendConfig(backend=MemoryToolStorageBackend.FILESYSTEM), ...)` accepts an operator-supplied config instance and stores it on the frozen model.
  4. `RuntimeConfig(..., memory_tool_backend_config="not_a_config", ...)` raises typed `ValidationError` per Pydantic field validation (type mismatch).
  5. `HarnessContext.memory_tool_registry` accessible on a fully-bootstrapped context as a `MemoryToolRegistry` instance.
  6. Per-field minor-version-bump invariant per C-RT-02 v1.1 version-evolution clause preserved (new optional field → minor bump v1.16 → v1.17 already absorbed at spec-writer arc).
  7. Importable; pyright strict mode passes.

### U-RT-80 — materialize_memory_tool_registry_stage factory + stage-5 wiring

- **Implements:** Runtime spec **v1.17** §14.12.3 stage-5 factory contract — 3-step composition body: (1) resolve configured backend per `config.memory_tool_backend_config` override OR via `harness_as.anthropic_graceful_degradation.memory_tool_storage_backend(config.deployment_surface)` resolver default; (2) construct storage-backend implementation per resolved `MemoryToolStorageBackend` enum value (only `FILESYSTEM` implemented at v2.14 per §14.D operator ratification — other enum values raise `RT-FAIL-MEMORY-BACKEND-RESOLUTION` per §14.12.4 with clear "deferred to follow-on retirement-batch arc" message); (3) construct `MemoryToolRegistry` bound to the storage-backend implementation; bind to `ctx.memory_tool_registry`. NEW fail class `RT-FAIL-MEMORY-BACKEND-RESOLUTION` added per §14.12.4 (bootstrap aborts on resolution OR construction failure per ADR-F4 v1.1 §Consequences (c) fail-closed). Stage-5 ordering per §14.12.3: arbitrary within stage 5 LOOP_INIT (no dependency on `materialize_runtime_tool_dispatcher_stage`).
- **Files:**
  - `harness-runtime/src/harness_runtime/bootstrap/factories/memory_tool_registry_factory.py` (NEW — factory body module; mirrors existing factory-module pattern at `harness-runtime/src/harness_runtime/bootstrap/factories/`).
  - `harness-runtime/src/harness_runtime/bootstrap/stage_5.py` (EXTEND — stage-5 LOOP_INIT registers the new factory invocation; mirrors v2.12 U-RT-75 wiring pattern for `materialize_runtime_tool_dispatcher_stage`).
  - `harness-runtime/src/harness_runtime/lifecycle/fail_classes.py` (EXTEND — add `RT-FAIL-MEMORY-BACKEND-RESOLUTION` to the §14 runtime-local fail-class taxonomy enumeration).
- **Signatures:**
  - `async def materialize_memory_tool_registry_stage(config: RuntimeConfig, ctx: _MutableHarnessContext) -> MemoryToolRegistry`. Factory body executes 3 steps verbatim per spec v1.17 §14.12.3 prose; binds the registry to `ctx.memory_tool_registry` during composition; returns the registry for the stage-5 callsite to inspect.
  - Backend-selection helper: resolves `config.memory_tool_backend_config.backend` if set, else picks one from `harness_as.anthropic_graceful_degradation.memory_tool_storage_backend(config.deployment_surface)` per the graceful-degradation resolver — the resolver returns `frozenset[MemoryToolStorageBackend]` per `harness-as/src/harness_as/anthropic_graceful_degradation.py:248`; v2.14 picks `MemoryToolStorageBackend.FILESYSTEM` if present in the frozenset (the only backend with an implementation landed at v2.14 per §14.D); raises `RT-FAIL-MEMORY-BACKEND-RESOLUTION` otherwise.
  - Stage-5 callsite invocation: `ctx.memory_tool_registry = await materialize_memory_tool_registry_stage(config, ctx)`.
- **Depends on:** [U-RT-76 (Protocol + sub-model), U-RT-77 (filesystem backend implementation), U-RT-78 (Registry class), U-RT-79 (config + ctx fields)].
- **ACs:**
  1. `materialize_memory_tool_registry_stage(config, ctx)` with `config.memory_tool_backend_config=None` + `config.deployment_surface=DeploymentSurface.LOCAL_DEV` returns a `MemoryToolRegistry` whose `.configured_backend == MemoryToolStorageBackend.FILESYSTEM` (per the `_MEMORY_BACKENDS[LOCAL_DEV]` frozenset at `harness-as/src/harness_as/anthropic_graceful_degradation.py:222` containing FILESYSTEM).
  2. `materialize_memory_tool_registry_stage(config, ctx)` with `config.memory_tool_backend_config=MemoryToolBackendConfig(backend=MemoryToolStorageBackend.FILESYSTEM)` returns a registry whose `.configured_backend == MemoryToolStorageBackend.FILESYSTEM` (operator override honored).
  3. `materialize_memory_tool_registry_stage(config, ctx)` with `config.memory_tool_backend_config=MemoryToolBackendConfig(backend=MemoryToolStorageBackend.S3)` raises `RT-FAIL-MEMORY-BACKEND-RESOLUTION` with a message naming the unimplemented backend AND a "deferred to follow-on retirement-batch arc per fork-doc §14.D" pointer (carries the §14.D scope-ratification context forward at the runtime error surface per `[[halt-route-split-AC-pattern]]` discipline).
  4. Stage-5 LOOP_INIT invocation: after stage 5 completes, `ctx.memory_tool_registry` is bound to a `MemoryToolRegistry` instance with non-None `.backend`.
  5. Bootstrap-abort behavior: if the factory raises `RT-FAIL-MEMORY-BACKEND-RESOLUTION`, bootstrap propagates the error per ADR-F4 v1.1 §Consequences (c) fail-closed (verified via end-to-end bootstrap test).
  6. Integration test: full bootstrap with `RuntimeConfig(deployment_surface=LOCAL_DEV, memory_tool_backend_config=None)` produces a `HarnessContext` with `.memory_tool_registry.configured_backend == FILESYSTEM` and `.memory_tool_registry.resolve_backend(LOCAL_DEV)` returns a `LocalFilesystemMemoryToolBackend` instance.
  7. **Protocol-conformance enforcement per §14.12.5 invariant 2.** Factory MUST verify the constructed backend satisfies `MemoryToolStorageBackendProtocol` via `@runtime_checkable` introspection BEFORE binding to `ctx.memory_tool_registry`. Given a backend object missing one or more of the 5 required methods (e.g., a mock object with only `view` defined), the factory raises `RT-FAIL-MEMORY-BACKEND-RESOLUTION` with a message naming the missing method(s) — verified via test fixture instantiating an incomplete-Protocol backend object.
  8. Importable; pyright strict mode passes.

### U-RT-81 — C-RT-15 §14.5.1 callback-injection composer-step at llm_dispatch.py

- **Implements:** Runtime spec **v1.17** §14.5.1 (Memory tool storage-backend callback binding) composer-step amendment — per-dispatch invariants 1-5: detect memory tool in `step.step_payload.tools` (`type == "memory_20250818"` per ADR-D3 §1.1 #11); resolve storage backend via `ctx.memory_tool_registry.resolve_backend(ctx.config.deployment_surface)`; wire 5 CRUD callbacks into SDK tool-use → tool-result inner loop; emit `memory.operation` span per AS spec v1.5 §14.7 6-attribute namespace at each callback invocation; propagate `MemoryCallbackIOError` → `RT-FAIL-MEMORY-CALLBACK-IO` + `MemoryPathViolationError` → `RT-FAIL-MEMORY-PATH-VIOLATION` to driver `try/except` at `workflow_driver.py:618-635` per C-CP-25 §25.3.3.4 step-dispatcher invocation site (HEAD-verified line range; spec §14.5.1 step 5 cite of `:380-389` corrected at adjacent-defect (iii) above). Adds 2 NEW fail classes (`RT-FAIL-MEMORY-CALLBACK-IO` transient + `RT-FAIL-MEMORY-PATH-VIOLATION` permanent) per §14.12.4 to the §14 runtime-local fail-class taxonomy.
- **Inner-loop mechanism (FM-2 discretion).** Per spec v1.17 §14.5.1 + §14.12.7 + this plan's change-note: the implementation arc selects one of the three landing options enumerated at spec §14.5.1 — (α) Anthropic SDK beta `context-management-2025-06-27` SDK-internal callback-registration hook (if exposed); (β) harness-authored inner loop wrapping `messages.create` polling for `tool_use` response → callback execution → `tool_result` re-dispatch; (γ) harness-authored sibling-composer to C-RT-15 wrapping the dispatcher with memory-tool loop. Implementation-arc SHOULD verify SDK-capability empirically BEFORE landing (per `[[advisor-before-substantive-work-for-cross-axis-blockers]]` discipline; default to β if SDK doesn't expose the registration hook). Plan AC verifies the contract surface (callback binding + `memory.*` emission + fail-class propagation), not the mechanism per FM-2 no-extension discipline.
- **Files:** `harness-runtime/src/harness_runtime/lifecycle/llm_dispatch.py` (EXTEND — C-RT-15 composer body amended at the §14.5 step 4 dispatch site to detect Memory tool + wire callbacks; mirrors structural-pattern divergence from §14.3 mcp.* per AS spec v1.5 §14.7 producer-site footer note: per-callback emission, NOT per-dispatch).
- **Signatures:**
  - Composer-step amendment at the existing C-RT-15 `RuntimeLLMDispatcher.dispatch(...)` body (no new top-level class introduction — extension of the existing composer per §14.5 step 4):
    - Detect-memory-tool helper: `def _step_has_memory_tool(step: WorkflowStep) -> bool` — iterates `step.step_payload.tools`; returns True iff any element has `type == "memory_20250818"`.
    - Callback-binding helper (mechanism-discretion-bounded shim): `async def _execute_with_memory_callbacks(messages_create_kwargs, backend: MemoryToolStorageBackendProtocol, tracer: Tracer, backend_enum: MemoryToolStorageBackend, context_editing_active: bool) -> MessagesResponse` — encapsulates the chosen α/β/γ mechanism behind a single helper signature; AC verifies behavior at the helper boundary so mechanism choice is FM-2-bounded.
    - Span-emission helper: `def _emit_memory_operation_span(tracer: Tracer, kind: str, path: str, backend: MemoryToolStorageBackend, bytes_read: int | None, bytes_written: int | None, context_editing_active: bool) -> ContextManager[Span]` — emits the `memory.*` 6-attribute namespace per AS spec v1.5 §14.7 row-by-row (`memory.operation.kind` ∈ {read/write/update/delete/list}; `memory.path`; `memory.backend`; optional `memory.bytes_read` / `memory.bytes_written`; `memory.context_editing_active`).
- **Depends on:** [U-RT-78 (ctx.memory_tool_registry consumed via Protocol), U-RT-79 (ctx field exists post-stage-5), U-RT-77 (callback semantics — `MemoryPathViolationError` + `MemoryCallbackIOError` typed exceptions propagated through `_execute_with_memory_callbacks`)].
- **ACs:**
  1. **Detect-memory-tool branch.** `dispatch(step, ctx)` with `step.step_payload.tools` containing `{"type": "memory_20250818", ...}` invokes `_execute_with_memory_callbacks` (verified via mock-patched helper); `dispatch(step, ctx)` with `step.step_payload.tools` absent OR not containing memory tool definition does NOT invoke the helper (existing §14.5 step 4 path preserved verbatim).
  2. **Callback wiring.** `_execute_with_memory_callbacks` invoked with a `LocalFilesystemMemoryToolBackend` + a mocked `messages.create` returning a `tool_use` content block invoking `memory` `create` operation executes the backend's `create` callback with the correct `path` + `content` args.
  3. **`memory.*` namespace emission + callback → kind enum mapping LOCKED at plan-body (per change-note adjacent-defect (ii)).** Each callback invocation emits ONE `memory.operation` span with `memory.operation.kind` per the locked bijection: `view → "read"`, `create → "write"`, `str_replace → "update"`, `insert → "update"`, `delete → "delete"`. The spec-prose enum value `"list"` is dead at v1.17 (NO callback emits it; future spec revision MAY add a `list` callback per adjacent-defect (ii)). Backend `create("/memories/foo", b"hi")` invocation emits span with `memory.operation.kind == "write"`, `memory.path == "/memories/foo"`, `memory.backend == <enum value>`, `memory.bytes_written == len(content)`, `memory.bytes_read == None`, `memory.context_editing_active == <bool>`. Span head-sampled at 1.0 per AS spec §14.7 sampling-row (write/update/delete head=1.0 audit-floor commitment per ADR-D3 v1.2 §1.8.1).
  4. **`memory.*` namespace emission (read + insert + update branches).** Backend `view("/memories/foo")` invocation emits span with `kind == "read"`, `bytes_read == len(response)`, `bytes_written == None`; base-rate-sampled per AS spec §14.7. Backend `str_replace(...)` invocation emits span with `kind == "update"`, head-sampled. Backend `insert(...)` invocation emits span with `kind == "update"`, head-sampled. Backend `delete(...)` invocation emits span with `kind == "delete"`, head-sampled.
  5. **Fail-class propagation (`RT-FAIL-MEMORY-CALLBACK-IO`).** Backend `create` raising `MemoryCallbackIOError` propagates as typed `RT-FAIL-MEMORY-CALLBACK-IO` to the C-RT-15 dispatcher boundary; driver `try/except` at `workflow_driver.py:380-389` surfaces step-failure (verified via driver-level integration test).
  6. **Fail-class propagation (`RT-FAIL-MEMORY-PATH-VIOLATION`).** Backend invocation raising `MemoryPathViolationError` propagates as typed `RT-FAIL-MEMORY-PATH-VIOLATION` to the C-RT-15 dispatcher boundary; permanent per fail-class taxonomy (not retried).
  7. **Secret-redaction invariant (`memory.path` only structure, never content).** Span attribute set contains `memory.path` (string — path within `/memories` per AS spec v1.5 §14.7 `memory.path` row "structure-not-content discipline") but does NOT contain backend content bytes per §14.12.5 invariant 4 + AS spec §14.7 row 2 + AS spec §14.9 forward-reference to D6 §1.4 redaction discipline (verified via SpanProcessor inspection — no `memory.content` or equivalent attribute emitted).
  8. **Backwards-compat for non-memory dispatches.** Existing §14.5 dispatch path (without memory tool in payload) preserves all v2.13 ACs at the C-RT-15 composer — no regression in retry/breaker/fallback wrap composition, GenAI semconv emission, anthropic.* cache attribute emission.
  9. Importable; pyright strict mode passes.

### U-RT-82 — End-to-end test: local-filesystem backend + real Anthropic API messages.create with tools=[memory_tool]

- **Implements:** Runtime spec **v1.17** §14.12.6 (X-AL-2 retirement implications — full RETIRED transition prerequisites per §16 §6.C v2 C.vii scope: operator-bound `RuntimeConfig.memory_tool_backend_config` non-default + local-filesystem-backend e2e exercise: real Anthropic API `messages.create` call with `tools=[memory_tool]` + `MemoryToolStorageBackend.FILESYSTEM` backend wired through the registry; LLM-driven `create`/`view`/`str_replace` callback invocation observed; `memory.*` namespace emitted at each callback span).
- **Files:** `harness-runtime/tests/e2e/test_memory_tool_filesystem_e2e.py` (NEW — e2e integration test module).
- **Test scope per §14.D ratification.** ONLY local-filesystem backend at this arc per operator §14.D scope. S3 / ENCRYPTED_FILESYSTEM / DATABASE e2e tests deferred to operator-discretion follow-on retirement-batch arcs per §16 §6.C v2 C.vii.
- **Signatures:**
  - `async def test_memory_tool_filesystem_e2e_write_path()` — full bootstrap with `RuntimeConfig(deployment_surface=LOCAL_DEV, memory_tool_backend_config=MemoryToolBackendConfig(backend=MemoryToolStorageBackend.FILESYSTEM))`; constructs a workflow with a single LLM-dispatch step whose `step_payload.tools` includes the Anthropic Memory tool definition (`{"type": "memory_20250818", ...}` + `extra_headers={"anthropic-beta": "context-management-2025-06-27"}` per ADR-D3 §1.1 #11); executes the workflow against the real Anthropic API (gated behind `ANTHROPIC_API_KEY` env var fixture); asserts the `create` callback invoked at the filesystem backend with the expected path + content per the deterministic-prompt fixture.
  - **Deterministic-prompt fixture (eliminates LLM-behavior flakiness per advisor coherence-pass finding 2026-05-23).** The test uses a fixed system prompt + user message pair that explicitly instructs the LLM to invoke the Memory tool's `create` operation with a known path + content: system prompt names the Memory tool capability + instructs "use the Memory tool's `create` operation to save the following content to `/memories/notes.txt`"; user message contains the fixture content string. Implementer SHOULD verify prompt effectiveness empirically (per `[[advisor-before-substantive-work-for-cross-axis-blockers]]`) before landing — if a recent model variant changes Memory tool invocation behavior, the prompt MAY need adjustment per implementation-arc discretion (FM-2-bounded; not a spec extension).
  - `async def test_memory_tool_filesystem_e2e_skip_without_credential()` — separate test verifying the gating mechanism: marked `@pytest.mark.e2e` + `@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), ...)` skip-decorator semantics.
  - Test gating: both tests marked `@pytest.mark.e2e` + `@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), ...)` to allow CI to skip when no credential is available; explicit fixture for `tmp_path` as backend root.
- **Depends on:** [U-RT-76, U-RT-77, U-RT-78, U-RT-79, U-RT-80, U-RT-81 (all L9-octies cluster units must be landed)].
- **ACs:**
  1. Test runs with `ANTHROPIC_API_KEY` set: completes within reasonable timeout (~30s); the `create` callback invoked at the filesystem backend with `path == "/memories/notes.txt"` (verified via backend method-call recorder); the file at the resolved filesystem path contains the fixture content.
  2. Test runs without `ANTHROPIC_API_KEY`: skips cleanly per `@pytest.mark.skipif` gate (no false failure in CI).
  3. **Deterministic-prompt write-path assertion (per advisor coherence-pass finding 2026-05-23).** The `create` callback is invoked at least once per test invocation against a real Anthropic API; the deterministic-prompt fixture forces this outcome (LLM-behavior flakiness mitigated by explicit prompt instruction naming `create` operation + path). If the LLM nonetheless declines to invoke `create`, the test fails with a clear diagnostic message naming the prompt-content + LLM response (NOT a generic "no callback invoked" failure) so the implementer can adjust the prompt per FM-2 discretion.
  4. Test asserts the corresponding `memory.operation` span exists for the `create` callback invocation with `memory.operation.kind == "write"` + non-default `memory.backend` attribute matching `MemoryToolStorageBackend.FILESYSTEM` + `memory.path == "/memories/notes.txt"` + `memory.bytes_written == len(fixture_content)`.
  5. Test cleans up backend root directory at teardown (no test artifacts persisted between runs).
  6. Importable; pyright strict mode passes.

---

## §2 — DAG topology delta (v2.13 → v2.14)

NEW L9-octies cluster appended with internal edges. No edges into v2.13 units (L9-octies is structurally independent of L9-septies + L9-sexies per fork doc §5 ZERO cross-axis cascade + architect §13.6.D recommendation: Memory tool primitive is independent of retry/breaker/MCP/sub-agent/HITL composers). No edges from v2.13 units into L9-octies (existing composer stack does not consume the Memory tool registry — only the C-RT-15 dispatcher composer-step amendment at U-RT-81 consumes ctx.memory_tool_registry).

Topological sort within L9-octies (acyclic verified via Kahn execution):

```
L9-octies (NEW at v2.14):
  L0-within-cluster: U-RT-76 (Protocol + sub-model + typed-exception carriers; no within-cluster deps;
                              cross-package consumes already-landed MemoryToolStorageBackend enum at harness-as)
  L1-within-cluster: U-RT-77 (←76 — filesystem backend impl),
                     U-RT-78 (←76 — Registry class)
  L2-within-cluster: U-RT-79 (←76, ←78 — config + ctx field landings)
  L3-within-cluster: U-RT-80 (←76, ←77, ←78, ←79 — factory + stage-5 wiring;
                              cross-package consumes already-landed memory_tool_storage_backend resolver at harness-as)
  L4-within-cluster: U-RT-81 (←77, ←78, ←79 — composer-step amendment at llm_dispatch.py)
  L5-within-cluster: U-RT-82 (←76, ←77, ←78, ←79, ←80, ←81 — e2e full-loop test)
```

**Cluster-boundary edges:** none. L9-octies is fully internal-edge — no within-axis-cross-package edge to harness-core (Memory tool primitive homed entirely at harness-runtime per §13.6.A architect recommendation); no cross-axis edge to harness-cp / harness-as / harness-od / harness-cxa (consumption of already-landed `MemoryToolStorageBackend` enum + `memory_tool_storage_backend` resolver at `harness-as` is cross-package consumption against existing carriers, NOT a new dependency edge requiring CXA v2.8 amendment per fork doc §5).

**Cross-axis edges:** unchanged from v2.13. L9-octies adds ZERO new cross-axis edges per fork doc §5 + architect §13.6.D. CXA v2.8 unchanged.

DAG verified acyclic via Kahn execution (delta layer): 12 new edges consumed (all within-L9-octies); 0 new cluster-boundary edges; remaining edge set ∅. No cycle path within L9-octies (U-RT-76 has no deps; topological order computable).

---

## §3 — Coverage matrix delta (v2.13 → v2.14)

| Contract (spec v1.17) | Units covering | Change at v2.14 |
|---|---|---|
| C-RT-02 §3 RuntimeConfig (NEW optional `memory_tool_backend_config` field) | U-RT-79 | NEW row at v2.14 (additive field landing) |
| C-RT-04 §4 HarnessContext (NEW `memory_tool_registry` field, stage 5) | U-RT-79 | NEW row at v2.14 (additive field landing) |
| C-RT-15 §14.5.1 Memory tool storage-backend callback binding (NEW sub-section) | U-RT-81 | NEW row at v2.14 (composer-step amendment) |
| C-RT-22 §14.12.1 architectural surfaces (Protocol + Registry + sub-model) | U-RT-76 (Protocol + sub-model + typed exceptions), U-RT-78 (Registry class) | NEW row at v2.14 |
| C-RT-22 §14.12.2 per-callback invocation discipline (path validation; one span per callback; backend concurrency; no retry inside callback) | U-RT-77 (path validation + concurrency), U-RT-81 (span emission per callback) | NEW row at v2.14 |
| C-RT-22 §14.12.3 lifecycle stage placement (stage-5 factory) | U-RT-80 | NEW row at v2.14 |
| C-RT-22 §14.12.4 failure-mode taxonomy (3 NEW fail classes) | U-RT-80 (`RT-FAIL-MEMORY-BACKEND-RESOLUTION`), U-RT-81 (`RT-FAIL-MEMORY-CALLBACK-IO` + `RT-FAIL-MEMORY-PATH-VIOLATION`) | NEW row at v2.14 |
| C-RT-22 §14.12.5 invariants (resolved-once, Protocol-conformance, path-discipline, secret-redaction, sampling, backend-lifecycle) | U-RT-77 (path-discipline at backend, invariant 3), U-RT-78 (resolved-once, invariant 1), U-RT-80 (Protocol-conformance via `@runtime_checkable` introspection at stage-5 binding, invariant 2 — AC #7 added at coherence-pass), U-RT-81 (secret-redaction + sampling, invariants 4-5) | NEW row at v2.14 |
| C-RT-22 §14.12.6 X-AL-2 retirement implications (full RETIRED prerequisites: operator-bound config + e2e exercise) | U-RT-82 | NEW row at v2.14 |
| All other v1.17 contracts | preserved verbatim from v2.13 coverage | (no change) |

**Coverage gap audit:** none surfaced at coherence pass.
- C-RT-22 §14.12.7 "Deferred to implementation discretion" surfaces (storage-backend module organization, filesystem-backend root path resolution, per-backend concurrency model, inner-loop mechanism, operator-defined backend introspection, backend telemetry-attribution) — explicitly deferred per spec §14.12.7 + FM-2; not coverage gaps per `implementation-planner` SKILL.md §4.4 (no spec extension — implementation-discretion deferrals are NOT plan-side coverage targets).
- Spec v1.17 §16 §6.D PRESERVED ratification (operator-opt-in RETIRE-READY pattern) covered transitively via U-RT-80 (structural criterion-B MET at factory wiring) + U-RT-82 (full RETIRED gate exercise).

**Cite-precision audit:** all v2.14 cites against runtime spec point at **v1.17** (latest filed version per `Project_Workflow_v1_8.md` §7.4 use-latest-version body-citation-alignment clause). Cross-axis cites: AS spec v1.5 §14.7 (memory.* namespace) + AS spec v1.5 §14.8 (sampling) + AS spec v1.5 §14.9 (redaction) all at latest filed version. ADR-D3 v1.2 §1.1 #11 (Memory tool client-side classification) + ADR-D3 v1.2 §1.8.1 (memory.* namespace declaration + sensitive-data commitment) cited at v1.2 (current ADR-D3 version per workspace CLAUDE.md §2.2).

**Already-landed cross-axis consumption cites:**
- `MemoryToolStorageBackend` enum at `harness-as/src/harness_as/anthropic_graceful_degradation.py:88` (consumed at U-RT-76 + U-RT-78 + U-RT-79 + U-RT-80)
- `memory_tool_storage_backend(deployment_surface)` resolver at `harness-as/src/harness_as/anthropic_graceful_degradation.py:248` (consumed at U-RT-80)
- `DeploymentSurface` enum at existing harness-runtime config types (consumed at U-RT-78)
- `_MEMORY_BACKENDS[DeploymentSurface.LOCAL_DEV]` data at `harness-as/src/harness_as/anthropic_graceful_degradation.py:222` (used at U-RT-80 AC #1 expected-output derivation)

---

## Filing footer

| Field | Value |
|---|---|
| Artifact | `Implementation_Plan_Harness_Runtime_v2_14.md` |
| Version | v2.14 |
| Filing event | Class 1 fork H_T-CP-16+17 executable-consumer-absence resolution absorption pass (Memory-only scope per §14.C); runtime spec v1.16 → v1.17 + AS spec v1.4 → v1.5 co-published `3810320`; workspace CLAUDE.md §2.3 version-row bumps co-published `7e13c19`; 2026-05-23 |
| Predecessor | `Implementation_Plan_Harness_Runtime_v2_13.md` (v2.13 substantive content preserved verbatim outside the additive L9-octies cluster authoring) |
| New units | 7 — U-RT-76 (Protocol + sub-model + typed-exception carriers) + U-RT-77 (LocalFilesystemMemoryToolBackend impl) + U-RT-78 (MemoryToolRegistry class) + U-RT-79 (RuntimeConfig + HarnessContext field landings) + U-RT-80 (materialize_memory_tool_registry_stage factory + stage-5 wiring) + U-RT-81 (C-RT-15 §14.5.1 callback-injection composer-step at llm_dispatch.py) + U-RT-82 (e2e test: local-filesystem backend + real Anthropic API messages.create with tools=[memory_tool]) |
| Revised units | 0 at this plan (all v2.13 units preserved verbatim) |
| Cluster | NEW L9-octies cluster appended; L9-septies + L9-sexies preserved verbatim |
| Cross-axis dependencies | unchanged from v2.13. L9-octies adds 0 new CXA edges per fork doc §5 + architect §13.6.D (consumption of already-landed `MemoryToolStorageBackend` enum + `memory_tool_storage_backend` resolver at harness-as is cross-package consumption against existing carriers, NOT a new CXA edge) |
| DAG verification | Kahn-acyclic; 12 new within-L9-octies edges consumed; 0 new cluster-boundary edges; ∅ remaining edges |
| Coverage verification | All v1.17 spec contracts covered ≥ 1 unit (NEW C-RT-22 §14.12.1-6 fully covered across U-RT-76..U-RT-82; C-RT-15 §14.5.1 covered at U-RT-81; §3 + §4 field-table extensions covered at U-RT-79; §14.12.7 implementation-discretion deferrals NOT plan-side coverage targets per FM-2) |
| Fork ratification | `.harness/class_1_fork_h_t_cp_16_17_executable_consumer_absence.md` RATIFIED-AMENDED 2026-05-23 (§16); §14 operator dispositions §14.A through §14.E |
| Inner-loop mechanism discretion | α / β / γ enumerated at spec v1.17 §14.5.1 + this plan's change-note; U-RT-81 unit AC verifies contract-surface invariants only; mechanism selection per FM-2 no-extension discipline at implementation arc (verify SDK capability empirically — `[[advisor-before-substantive-work-for-cross-axis-blockers]]`); default to β if SDK doesn't expose Anthropic beta `context-management-2025-06-27` callback-registration hook |
| Retirement-batch absorption owed | batch-12 (or later): H_T-CP-16 STILL-BOUNDED → RETIRE-READY at U-RT-80 landing per §16 §6.D operator-opt-in; full RETIRED gates on operator-bound `memory_tool_backend_config` non-default + U-RT-82 e2e exercise per §16 §6.C v2 C.vii local-fs scope. H_T-CP-17 unchanged (PARTIAL preserved per §14.C Files arc deferral) |
| Date | 2026-05-23 |
