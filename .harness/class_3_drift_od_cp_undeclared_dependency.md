# Class 3 drift — harness-od undeclared OD→CP + OD→IS consumer dependencies

| Field | Value |
|---|---|
| Class | 3 (informational drift; non-blocking) |
| Filed at | 2026-05-31 (R-200-ci-od-cp-dependency-leak) |
| Filed by | axis-isolation matrix RED leg (PR #147) → roadmap entry resolution |
| Affected artifact | `harness-od/pyproject.toml` (build metadata; NOT design-substrate) |
| HEAD at filing | `f361a0e` (main, post-PR-152) |
| Resolution | Option (a) — declare the deps. Verified green in isolation (887 passed). |

---

## §1 Scope

The `axis-isolation` CI matrix (added at R-200-ci-axis-matrix, PR #147) runs each axis package under `uv sync --package harness-<axis>` (declared-dependency-closure only) + `pytest harness-<axis>/tests`. The `od` leg was RED and carried as ADVISORY (`continue-on-error`) because `harness-od/pyproject.toml` declared only `{harness-core, harness-as}` while `harness-od` actually consumes two further axis packages:

| Consumer | Import | Site | Live? |
|---|---|---|---|
| `harness_cp.engine_namespace.ReplayDisposition` | src | `idempotency_join_dedup.py:40` (+ 8 usages: typed fields, frozensets, branch logic) | **LIVE** — fanned out to `cost_namespace`, `cross_family_rollup`, `cost_record_audit_writer`, and 5+ harness-runtime cost-attribution modules |
| `harness_cp.pause_resume_protocol.{PauseEvent, ResumeAttempt, ResumeOutcome, ResumeOutcomeKind}` | src | `pause_resume_namespace.py:295` | projection **helpers are dead**, but the sibling `PauseResumeAuditPayload` type is consumed by `harness-cxa/.../cp_audit_conversion.py:70` |
| `harness_cp.*` (ActorIdentity, handoff_context, MaterialDiff, validator_framework, workflow_driver_types, sub_agent_gate_level_descent) | tests | `test_pause_resume_audit_helpers.py`, `test_validator_namespace.py`, `test_cross_family_rollup.py`, `test_idempotency_join_dedup.py` | test fixtures |
| `harness_is.state_ledger_entry_schema.{Identifier, Actor, ActorClass}` | tests | `test_pause_resume_audit_helpers.py:62`, `test_validator_namespace.py:118` | test fixtures |

The dashboard/CI-comment framing ("undeclared od→cp dependency … declare the dep **or relocate the seam**") and the per-CI-skill paraphrase of the CXA buckets implied this might be a *reverse-direction* drift to be eliminated. **It is not.** See §2.

## §2 Direction analysis — OD→CP is canonical, not a reverse edge

`harness-od` → `harness-cp` is the **canonical OD→CP consumer direction**, enumerated at CXA v2.18 §2.3.3 (12 edges; preserved verbatim from the v2.1 baseline). OD is the consumer-most-downstream axis: it *ingests* CP-emitted namespaces — explicitly incl. `engine.*` per `harness-od/CLAUDE.md` §1.4 scope-exclusion. `ReplayDisposition` lives in `harness_cp.engine_namespace` and is exactly such an ingested `engine.*` type. The v2.18 §2.4 per-axis attribution records OD outbound = `4 → IS; 10 → AS; 12 → CP = 26`.

`harness-od` → `harness-is` is the **canonical OD→IS consumer direction** (CXA v2.18 §2.3.4; 4 edges).

There is no package cycle:
- `harness-cp` deps = `{core, as}` — **no `od`**. So `od → cp` is acyclic-safe.
- `harness-is` deps = `{core}` — **no `od`**. So `od → is` is acyclic-safe.
- The *reverse* CP→OD audit seam (CXA §2.3.7, 8 edges — CP audit entries → OD audit ledger) is mediated through `harness-cxa` (`cp_audit_conversion.py`), i.e. there is **no direct `cp → od` import**. The two directions are distinct buckets and do not collide at the package level.

Conclusion: the "leak" is purely an **omitted dependency declaration** in build metadata. The imports already existed and resolved at the workspace level (uv resolves all members); only the per-package isolation sync exposed the omission.

## §3 Resolution (option a — declare the deps)

`harness-od/pyproject.toml` now declares `harness-cp` + `harness-is` in `[project.dependencies]` + `[tool.uv.sources]` (workspace), with inline comments citing the canonical CXA buckets. The `od` `continue-on-error` carve-out in `.github/workflows/ci.yml` is dropped — the full 6-leg matrix now blocks.

Verification (exact CI command, this worktree): `uv sync --package harness-od && uv run --no-sync pytest harness-od/tests -m "not e2e"` → **887 passed**.

Option (b) — "relocate the seam" — was rejected: the *forcing* consumer (`ReplayDisposition` in `idempotency_join_dedup.py`) is live OD-internal telemetry logic (C-OD-08 idempotency join/dedup); it cannot be relocated to `harness-cxa`, and re-homing `ReplayDisposition` out of `harness_cp` would violate CP axis-ownership of the engine-replay enum. (b) would at most relocate the *dead* pause-resume projection helpers and would do nothing for the forcing consumer.

## §4 Adjacent observations (not patched — FM-2)

- **(a) test-only `harness_is` dep.** `harness_is` is imported only in `harness-od/tests`, not in `harness-od/src`. The workspace has no `[dependency-groups]` test-group convention (verified across all axis pyprojects), and the CI isolation step pulls only `[project.dependencies]` (test tooling is layered separately as "no harness deps"). So the test-only cross-axis dep is declared in `[project.dependencies]` — slightly broader than src strictly needs, but harmless (uv dedupes), acyclic-safe, and aligned with the canonical OD→IS direction. A future `[dependency-groups]` test-group convention (workspace-wide) could tighten this; out-of-scope for a CI-fix arc.
- **(b) re-home `ReplayDisposition` → harness-core (future hygiene; NOT recommended).** The advisor flagged re-homing the shared enum to `harness-core` as the alternative that would preserve a CP→OD-only direction. Recorded here for operator visibility so the dep declaration is not silently cemented — but it is **not warranted**: OD→CP is a canonical consumer direction (§2), so the dep is correct as-is, and `ReplayDisposition` is a CP-axis concept (ADR-D1 engine replay disposition). Re-homing would be a carrier-home change (design-substrate; its own arc) with no benefit here. Operator may veto the declaration in favor of re-home if a future arc surfaces a reason.
- **(c) heavier od isolation leg.** The od leg now pulls cp's SDK deps (anthropic/openai/ollama + MCP transitive). Expected; reflects reality.

## §5 Routing

Class 3 informational — non-blocking. Touches build metadata (`pyproject.toml`) + CI config (`ci.yml`) only; **no `design-substrate/**` edit** (X-AL-3 guard does not fire). No spec/plan/CXA amendment owed (the CXA OD→CP §2.3.3 + OD→IS §2.3.4 buckets already enumerate these consumer edges). Filed for the record + to correct the "relocate the seam" / reverse-direction framing in the dashboard + CI comment.
