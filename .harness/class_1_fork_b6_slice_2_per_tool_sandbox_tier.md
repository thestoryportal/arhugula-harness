# Class 1 fork — B6 Slice 2: per-tool sandbox-tier resolution (`B-PER-TOOL-SANDBOX-TIER`)

**Fork class:** Class 1 (design-substrate amendment — lifts the spec-carved-out per-server-uniform→per-tool sandbox boundary; runtime spec §14.9.9/§14.9.10/§14.9.11 + AS spec C-AS-03 §3.1).
**Arc:** R-FS-1 **B6 Slice 2** — the genuine per-tool sandbox granularity the runtime spec names as "the distinct future arc B6" (§14.9.9 Scope boundary; §14.9.10 D4 "per-host outer × per-tool inner"; §14.9.10 inv-3 / Scope-boundary (b)). Successor to **B6 Slice 1** (#630, `1a7dc6e` — per-host STDIO transport-floor `compose_transport_floor`, runtime v1.54 §14.9.8). The last FROZEN arc of the R-FS-1 umbrella.
**Posture:** Design-phase / X-AL-3 design-fork-first → bundled-absorption (runtime v1.55→v1.56 + AS v1.10→v1.11 + clearance + impl + tests in one PR).
**Status:** ✅ **OPTION A RATIFIED 2026-06-17** (operator AskUserQuestion: "Full per-tool (A)" selected — per-host driver registry keyed by tier, per-dispatch selection, delivered==resolved, relaxes §14.9.9/§14.9.10 inv-3). Branch `r-fs-1-b6-slice-2-per-tool-sandbox-tier` off `origin/main` `bca9a61` (#636). Bundled-absorption arc OPEN.

---

## §0 — What this arc is

**B6 Slice 2 = per-tool sandbox tier.** B6 Slice 1 (#630) composed the per-*host* transport floor (`compose_transport_floor(effective, entry)` raises `effective.sandbox_tier` to `mcp_transport_floor(host.transport, host.trust, host.blast_radius)` — STDIO→TIER_3), but the per-host resolver is still **constant** per `(contract, step)`: `_build_default_policy_sandbox_resolver` returns the same `SandboxDispatchDecision` for every tool on a host (`runtime_tool_dispatcher_factory.py:103` — `resolve(_contract, _step)` ignores both args). B6 Slice 2 replaces that constant with a per-`(contract, step)` call to the full 10-row `sandbox_tier_floor(tool, deployment_surface, blast_radius_tier, mcp_transport, mcp_server)` (C-AS-02 §2.3 / `harness-as/.../sandbox_tier_floor.py:115`), `max()`-composed with the §14.9.8 deployment-surface default, so the per-tool rows become reachable **per tool**:

- **Rows 1-2** — forcing (`forces_computer_use` / `forces_code_execution` → `TIER_4_FULL_VM`). Currently unreachable: the resolver never reads tool metadata.
- **Rows 7-10** — per-tool blast-radius default (via `blast_radius_floor(contract.blast_radius_tier)`). Slice 1's floor used the host's single `blast_radius`; Slice 2 uses each tool's own `blast_radius_tier`.
- Rows 3-6 (transport/trust) reproduce Slice 1's per-host floor per-tool (`sandbox_tier_floor` rows 3-6 ≡ `mcp_transport_floor`, AS C-AS-10 §10.1 AC5) — so the full function **subsumes** `compose_transport_floor` in the per-tool path; the STDIO TIER_3 floor survives (row 3).

The dispatch seam already threads the per-tool inputs — the resolver body and the driver granularity change; the dispatcher is byte-unchanged:

```
runtime_tool_dispatcher.py:752   tool_execution_driver = self._tool_execution_drivers.get(server_name, default)   # picked per-HOST
runtime_tool_dispatcher.py:788   sandbox_decision = sandbox_resolver(contract, step)   # contract+step ALREADY passed; constant body today
runtime_tool_dispatcher.py:863   await tool_execution_driver.call_tool(sandbox_decision=…)   # driver self-guards == required_tier
```

---

## §1 — Grounding (byte-grounded at HEAD `bca9a61`)

**Two structural surfaces must change (both confirmed by worktree body-read at `bca9a61`, NOT ledger prose):**

**Surface (a) — `ToolContract` cannot feed `sandbox_tier_floor` rows 1-2.** `ToolContract` (`tool_contract.py:62`) carries `minimum_tier` + `blast_radius_tier` + `required_secrets` — NOT the `ToolMetadata` forcing discriminators (`forces_computer_use` / `forces_code_execution` / `is_deterministic_inhouse`, declared at `sandbox_tier_floor.py:46`). So the per-tool resolver has `contract.blast_radius_tier` (rows 7-10) but no way to reach rows 1-2/7. `ToolContract` + `RawContractInput` + the validator must carry the three discriminators (additive, safe defaults), rippling to the v1.40 stage-3a `MCPToolContractConverter`.

**Surface (b) — the per-host construction-time driver is exact-match.** Drivers self-guard `sandbox_decision.tier is not self.required_tier → raise` (`docker_tool_execution_driver.py:71`, `e2b_tool_execution_driver.py:89`). The factory builds **one** driver per host (`runtime_tool_dispatcher_factory.py:333`), selected once by the host's single `effective_sandbox.sandbox_tier`. A per-tool tier that differs from the host's construction-time driver tier raises. **Per-tool tier resolution cannot land without reconciling this** — the one operator gate (Option A ratified).

**Continuity with B6 Slice 1 (verified at `bca9a61`, no regression):**
- `compose_transport_floor` (`sandbox_defaults.py:135`) is subsumed by `sandbox_tier_floor` rows 3-6 (per-tool). The per-tool resolver maxes the **surface default** (`resolve_effective_sandbox_defaults`, WITHOUT the host-blast transport floor) with the full per-tool `sandbox_tier_floor` — so a STDIO tool still floors to TIER_3 (row 3, per-tool), preserving Slice 1's mandate while refining the blast input from per-host to per-tool.
- **Tools static.** `tool_registry` is "immutable after start()" (`mcp_client_host.py:67`); the host's tool set — hence its reachable tiers — is fixed at the stage-5 factory, making the per-host per-tier driver registry computable.

**Second behavioral delta (named, not gated).** Keying the fail-close on **per-tool reachable tiers** means a host with **zero tools** no longer eager-fail-closes at bootstrap (B6 Slice 1's per-host floor did, regardless of tools). Correct under the per-tool model — a tool-less host (immutable registry) exposes no dispatch surface, so it under-sandboxes nothing; the ADR-D2 §1.3 STDIO→TIER_3 mandate still bites at each STDIO tool (which floors to TIER_3 and requires a microVM driver or fail-closes). Folding the per-host floor back into the reachable set to restore eager fail-close was rejected — it re-couples the driver requirement to the host's coarse blast radius (the exact coupling B6 Slice 2 removes). Encoded as `test_toolless_stdio_server_needs_no_driver` + `test_bare_*_with_tool_*_fails_loud`.

---

## §2 — The decision

### §2.1 — NOT gated (adopt-and-note — routine additive legs)

Per `[[spec-leg-split-on-ratification-boundary]]`, these land without an operator gate:
1. **`ToolContract` carries the `ToolMetadata` discriminators** (surface (a)). Additive, safe non-forcing defaults (`False`) → every existing contract resolves byte-identically. Routine AS-spec leg (C-AS-03 §3.1).
2. **The resolver body** — `resolve(contract, step)` = `max(surface_default.sandbox_tier, sandbox_tier_floor(ToolMetadata(contract), surface, contract.blast_radius_tier, host.transport, mcp_server))`. Identical under both driver options.

### §2.2 — Shared mechanism (both options safe)

Resolver returns a per-tool tier; the §14.9.4 floor check enforces `tier ≥ contract.minimum_tier`; the driver delivers **≥** the resolved tier (FR-1, never silent downgrade). Both options below satisfy FR-1.

### §2.3 — THE GATE (ratified Option A): driver-granularity A vs B

| | **Option A — per-tool driver (RATIFIED)** | Option B — pin-at-max + relax guard |
|---|---|---|
| Mechanism | Per-host `dict[SandboxTier, ToolExecutionDriver]` registry; dispatch selects by resolved tier. | One host driver pinned at the host's max tier; guard `==`→`>=`. |
| inv-3 | **RELAXED** → per-dispatch selection. (operator-gated) | preserved. |
| delivered vs resolved | **==** (faithful audit + cost). | ≥ (over-isolates; span/cost emit RESOLVED tier ≠ delivered → fidelity gap vs CA #625). |
| Config | one driver per reachable tier. | one driver per host. |

**Both safe** (delivered ≥ resolved; floor check still raises). Not C10⊥C11 security — **precision + audit/cost fidelity (C5/C8 → A) vs config-burden (C11 → B)**. Operator ratified **A** under the FULL-SPEC directive — the faithful "per-host outer × per-tool inner" (§14.9.10 D4) with no fidelity gap.

**Impl of Option A (minimal-surface):** a `PerTierToolExecutionDriver` *implements* the `ToolExecutionDriver` protocol, holds the per-tier registry, and selects `registry[sandbox_decision.tier]` inside its own `call_tool`. The factory builds one composite per host; the dispatcher's `dict[ServerName, ToolExecutionDriver]` field + dispatch body + `for_single_host` stay **byte-unchanged** (spec §14.9.11 defers "the registry carrier shape" to impl-discretion). The per-dispatch selection (inv-3 relaxation) lives inside the composite.

---

## §3 — X-AL-3 classification + spec cascade

**Class 1 (design-fork-first).** Bundled-absorption PR:
1. **Runtime spec** v1.55 → **v1.56** — new **§14.9.11** (per-tool sandbox resolution + per-dispatch driver selection; inv-3 relaxation). Change-note + clearance marker.
2. **AS spec** v1.10 → **v1.11** — C-AS-03 §3.1 field-table extension (`ToolMetadata` discriminators, additive). Change-note + clearance marker.
3. **Impl** — `harness-as/tool_contract.py` (3 fields + `RawContractInput` + validator); `harness-runtime/config/sandbox_defaults.py` (`resolve_per_tool_sandbox_defaults` SSOT helper); `runtime_tool_dispatcher_factory.py` (`_build_per_tool_sandbox_resolver` + `PerTierToolExecutionDriver` + per-host loop rewire); **`types.py` + `mcp_client_host_factory.py`** — per-server `default_forces_*` / `default_is_deterministic_inhouse` fields on `MCPClientConfig` + the stage-3a `_build_default_policy_converter` stamping them, so the **production MCP-discovered path** populates the discriminators (else the forcing rows are vacuous in production — Codex finding, §5). Dispatcher unchanged.
4. **Tests** — forcing rows 1-2 reachable; per-tool blast rows 7-10; Slice-1 STDIO TIER_3 floor survives (row 3); per-tier driver selection + delivered==resolved; floor-violation raise; mixed-tier host registry.

---

## §4 — Forward items (registered — `[[spine-ledger-forward-arc-registration]]`)

- **`B-MCP-HOST-REMOTE-TRANSPORT`** (already registered, B6 Slice 1) — composes (rows 4-6 trust become per-tool-reachable on remote hosts).
- `is_deterministic_inhouse` lands on `ToolContract` with the other two (full `ToolMetadata` triad) even though `sandbox_tier_floor` reads it only at row 7 — avoids a second carrier-extension arc.

---

## §5 — Verification + filing footer

**Grounding verified at HEAD `bca9a61` (worktree, this session):** `sandbox_tier_floor.py:115/46`; `tool_contract.py:62`; `runtime_tool_dispatcher_factory.py:91/103/327/333` (constant resolver + Slice-1 `compose_transport_floor` + per-host single driver); `sandbox_defaults.py:135` (`compose_transport_floor`, `EffectiveSandboxDefaults.assigned_tier_reason`); `runtime_tool_dispatcher.py:140/752/788/863` (`ToolExecutionDriver` protocol = `call_tool` only; per-host driver pick; resolver call; driver call); `docker_tool_execution_driver.py:71` + `e2b:89` (exact-match guard); `mcp_client_host.py:67` (tools immutable after start()); §14.9.9 Scope-boundary + §14.9.10 D4/inv-3 (spec carves B6 as future arc). **Note:** an early grounding pass mis-read the operator's *main checkout* (`cc55a43`, ~#626, behind origin — missing Slice 1) via absolute paths; corrected to worktree paths off `bca9a61` (`[[worktree-path-and-edit-guard-gotchas]]`).

**Decorrelated review:** advisor (this session) — confirmed design-fork-first → gate → impl; reframed the gate to fork (b) only, both-safe; surfaced the Option-B cost-fidelity discriminator that decided Option A. **Codex (out-of-family, committed-diff)** — caught a [P2] both advisor + I missed (`[[hooks-codex-pilots-decorrelation-validated]]`): the production `MCPToolContractConverter` did not populate the new discriminators, so the forcing rows were **vacuous on the MCP-discovered path** (reachable only for manually-built contracts — the `[[built-but-vacuous-reground-ledger-asis]]` class). Closed by the per-server `default_forces_*` fields + the converter stamping them + `test_converter_stamps_per_server_forcing_discriminators`.

| Field | Value |
|---|---|
| Artifact | `.harness/class_1_fork_b6_slice_2_per_tool_sandbox_tier.md` |
| Authored | 2026-06-17 (Phase 7, R-FS-1 B6 Slice 2, design-fork-first) |
| Status | ✅ Option A ratified → bundled-absorption (runtime v1.56 §14.9.11 + AS v1.11 §3.1 + impl + tests) |
| Authority chain | ADR-D2 §1.5.1 + ADR-F4 §Decision → C-AS-02 §2.3 → runtime §14.9.9/§14.9.10 (carve-out) → this fork |
