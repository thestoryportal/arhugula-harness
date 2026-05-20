# Class 1 Tension — U-RT-43 STATE_LEDGER path: directory vs file conflict

**Filed:** 2026-05-20 at U-RT-43 (bootstrap orchestrator) landing.
**Status:** RESOLVED 2026-05-20 — Path A applied. IS spec v1.3 §1 amended: `PathClass.STATE_LEDGER` + `PathClass.ROUTING_MANIFEST` resolve to DIRECTORIES; canonical filenames `state.jsonl` + `routing.manifest.json` appended at the consumer composer (`initialize_jsonl_event_ledger` in harness-is, `resolve_manifest_residence_path` in harness-cp). rmdir() workaround in `stage_1_is.py` removed. IS 125 / CP 465 / runtime 651 tests green.
**Memory key:** `[[fork-state-ledger-path-dir-vs-file]]` (to author).

---

## 1. Defect

Two existing composers have contradictory expectations of the `STATE_LEDGER`
path-class resolved path:

| Composer | Treats `PATH_CLASS_REGISTRY[STATE_LEDGER]` as | Source |
|---|---|---|
| `materialize_path_registry` (U-RT-10) | DIRECTORY — calls `path.mkdir(parents=True, exist_ok=True)` at stage 1 IS step 1 | `harness-runtime/src/harness_runtime/lifecycle/path_registry.py:111` |
| `materialize_state_ledger` (U-RT-12) → `initialize_jsonl_event_ledger` | FILE — calls `path.read_text()` + `path.touch()` | `harness-is/src/harness_is/jsonl_event_ledger_lifecycle.py:64-70` |

At integration (U-RT-43 stage 1 IS), composer 1 creates `STATE_LEDGER` as a
directory; composer 2 fails with `IsADirectoryError` on `read_text()`.

Per-composer unit tests do not surface the conflict — each test builds its
own `PathResolver` and bypasses the other composer's filesystem effects.

## 2. Workaround landed at U-RT-43

`stage_1_is.execute`, between path-registry and state-ledger composer calls,
detects the dir-vs-file conflict and `rmdir()`s the just-created empty
`STATE_LEDGER` directory so state-ledger composer's own touch logic creates
the file. Inline note at `bootstrap/stage_1_is.py` docstring + code.

The workaround is brittle:
- Relies on `rmdir()` succeeding (which requires empty directory).
- A nonempty STATE_LEDGER directory at bootstrap time silently leaves state in
  place and surfaces as a state_ledger composer failure (which the orchestrator
  wraps as `BootstrapFailure(failed_stage=IS)`, not a path-class defect).
- The path-class contract is unclear to readers; future composers must
  remember the conflict.

## 3. Resolution candidates

| Path | Change locus | Blast radius |
|---|---|---|
| A | IS spec amendment: `STATE_LEDGER` resolves to a DIRECTORY containing `state.jsonl`. State-ledger composer appends `/state.jsonl` to the resolved path. | IS spec C-IS-01 §1 + C-IS-05 §5 + U-IS-12 composer; ~3 sites |
| B | `materialize_path_registry` differentiates file-class vs dir-class members of `PathClass`. New `IS` spec field (or hard-coded list) marking which classes are files. State-ledger remains file-typed. | IS spec C-IS-01 §1 + U-IS-10 schema + U-RT-10 composer; ~3-4 sites |
| C | Status quo + bootstrap-side workaround documented as canonical. | Already in place; minimal further work |
| D | `materialize_path_registry` does NOT mkdir at all; mkdir becomes the consumer's responsibility. Each per-path-class composer (state_ledger, skills load, routing_manifest, prompts) creates its own filesystem residence. | U-RT-10 + each downstream consumer; cleaner separation but more sites |

**Recommendation:** Path A (smallest schema change; matches `state.jsonl` naming convention).

**Smallest blast radius:** Path C (already landed; documented).

## 4. AC carry-forward at U-RT-43

The U-RT-43 ACs (full bootstrap returns HarnessContext; per-stage rollback;
9 lifecycle events) are MET with the workaround. The state-ledger path
treatment is orthogonal to the orchestrator's contract. No AC strike needed.

## 5. Routing per workspace `CLAUDE.md` §4.3

- Class 1 (architectural defect): YES — two composer contracts disagree on the
  shape of a typed surface (PathClass resolved path).
- Route to: design-phase IS spec revision (Path A) OR IS spec + path_registry
  spec amendment (Path B) OR no route (Path C).

Operator decision pending.

---

## Footer

| Field | Value |
|---|---|
| Filed by | U-RT-43 landing (2026-05-20) |
| Workaround | `bootstrap/stage_1_is.py` `rmdir()` between path_registry and state_ledger |
| Memory pattern | `[[carrier-home-defect-pattern]]` (analogous — two contracts disagree on a shared type's shape) |
| Test coverage | `tests/test_bootstrap.py::test_bootstrap_returns_frozen_harness_context` exercises the integration; passing under workaround |

---

## Audit reconciliation (2026-05-20)

**Verified status:** RESOLVED

**Resolving artifact / evidence:** Already labeled RESOLVED 2026-05-20 (Path A — IS spec v1.3 §1 amendment: STATE_LEDGER resolves to directory). Audit confirms.

**Audit context:** Workspace-wide tension-record audit 2026-05-20 (post-U-RT-52 merge to main at 2b945ab). 33 records reviewed against current code + spec state. Result: 28 RESOLVED, 5 DEFERRED-PARTITION, 0 STILL-OPEN. The 'Status' line earlier in this record predates the audit; this section is the current verified state.
