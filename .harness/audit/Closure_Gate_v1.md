# Closure Gate v1 — the binding "harness coding fully closed" predicate

> **Purpose.** Crystallize the scattered `must_pass` predicates across `R-FS-1` + `R-CL-Q1..Q4` + `R-CL-D1` + `R-CL-C1` (`Project_Roadmap_v1.md` §5) into **one explicit, checkable closure gate**, so "harness coding is fully closed" is an *objective predicate* — not a manual judgment. Authored as the closure instrument feeding the remaining-build audit (`Remaining_Build_Audit_Report.md` §1 + the reliability assessment).
> **Posture:** mode-agnostic (process-substrate; consolidates + operationalizes the existing roadmap R-CL track — it does **not** duplicate, override, or re-author those entries; the roadmap stays canonical). No `design-substrate/**` edit.
> **Authored at:** HEAD `46012d5` (2026-06-20). **Status:** v1 scope (predicate definition + checker contract). The checker tool (`tools/closure_gate.py`) is a defined follow-on, not yet built.

---

## 0. The closure predicate (one sentence)

> **Harness coding is FULLY CLOSED ⟺ all Tier-1 (build-complete) predicates ∧ all Tier-2 (quality/close) predicates are TRUE**, where each predicate resolves to a named evidence source — a CI-gated tool, a coverage-matrix cell, or a phase sign-off (PR + clearance marker). `R-CL-C1` is the human aggregator that asserts the conjunction.

Two tiers, because they answer two different questions and gate two different milestones:

- **Tier 1 — build-complete.** "Is every specified capability BUILT?" Gates **R-FS-1 resolution** (when this is true, the R-CL quality track unblocks). Mostly **automatable**.
- **Tier 2 — quality/close.** "Is the complete harness reviewed, tested-to-evidence, packaged, documented, and certified?" Gates **R-CL-C1** (ship). Mix of **tool-checked + sign-off**.

This separation is load-bearing: it makes "R-FS-1 done" a *machine-checkable* event (Tier 1), and reserves the irreducibly-human judgment for Tier 2.

---

## 1. Tier 1 — build-complete predicates (gate R-FS-1 resolution)

| ID | Predicate | Evidence source | Auto? | Check |
|---|---|---|---|---|
| **G1.1** | Forward register **empty** — every `registered` + `gated` standalone arc is opened, grounded, built, and moved to `closed`/`resolved` | `.harness/arc-ledger.yaml` snapshot `standalone_registered == 0 ∧ standalone_gated == 0` | ✅ | `tools/arc_ledger.py --check` (extend to assert zero registered/gated) |
| **G1.2** | Arc-ledger tally **consistent** (no impossible/stale count) | arc-ledger snapshot vs derived | ✅ | `tools/arc_ledger.py --check` (existing CI gate) |
| **G1.3** | **No contract orphans** (head-scoped) — every canonical-head `C-*` has a code carrier | overlay `contract_without_code` resolves to ∅ — or only the documented `C-IS-11` corrected-non-cite (the head runtime-spec names it in prose). **Head-scoping landed (RB-DOC-03): 6 phantoms → 1** | ✅ | `just overlay-query --orphans` |
| **G1.4** | **No unit orphans** (head-scoped) — every canonical-head `U-*` has a code carrier (or is a documented non-unit) | overlay `unit_without_code` (head-scoped class added, audit §B) reviewed → every entry resolved to built/non-unit (current set = the audit's 7 resolved + `U-CP-71` Meta-Arch mention). **Advisory, not auto-zero** (delta-plans under-count; range-marker + contract-cited units appear) | ◐ | `just overlay-query --orphans` |
| **G1.5** | **CXA seams complete** — no seam missing an endpoint; the 31/37 count collision reconciled (RB-CXA-03) | overlay `cxa_seam_missing_endpoint == 0` (HARD gate) | ✅ | `just overlay-check` |
| **G1.6** | **Substitutions retired-or-ratified** — 54/54 retired; every bounded-residual explicitly operator-ratified | `tools/substitution_ledger.py --check` (tally) + residual ratification markers | ✅ tally / ☐ ratify | `tools/substitution_ledger.py --check` |
| **G1.7** | **No genuinely-open forks** — every `class_*_fork_*.md` is APPLIED/RESOLVED, or each OPEN one is operator-ratified | fork-status triage → 0 OPEN (the engine-durable-resume one re-grounded/closed — RB-RT-07) | ◐ semi | fork-headline scan (candidate: a `--check` mode) |
| **G1.8** | **FULL-SPEC honored** — no capability closed as `deferred`/`bounded-residual` without an explicit operator re-ratification (the §5.0 directive) | clearance / ratification markers for each residual (RB-CP-09, RB-SUB-01/02) | ☐ operator | clearance markers + roadmap status |

`✅*` = automatable *after* the audit's §B tooling fixes land (RB-DOC-03 head-scoping + the head-scoped unit class). Until then G1.3/G1.4 mis-report (the phantom-orphan defect this gate must not inherit).

**Tier-1 close = R-FS-1 RESOLVED.** When G1.1–G1.8 are all true, the standalone `B-*` register is empty and the spec is fully built → R-CL-Q1..C1 unblock.

---

## 2. Tier 2 — quality/close predicates (gate R-CL-C1 ship)

Each maps to an existing R-CL phase `must_pass` (`Project_Roadmap_v1.md` §5). The gate does not re-define them — it points at them and records sign-off.

| ID | Phase | Predicate (from the phase `must_pass`) | Auto? | Evidence |
|---|---|---|---|---|
| **G2.1** | R-CL-Q1 | Per-package review (codex + `/code-review` + `/simplify`) all findings closed; clean-checkout-to-green DevEx; `just check` green at a fixed point | ◐ tool+signoff | Q1 close PR + `just check` |
| **G2.2** | R-CL-Q2 | Threat-model + per-surface security test (sandbox/secrets/MCP-trust/redaction/audit-integrity/supply-chain); `/security-review`; every finding fixed-or-risk-accepted; **no secret/PII in any telemetry** | ◐ tool+signoff | Q2 close PR + threat-model doc |
| **G2.3** | R-CL-Q3 | Full suite green at a verified fixed point; **every `C-*` contract has ≥1 executed-path proof (the coverage/evidence matrix)**; tri-tier use-the-product probes | ✅ coverage + ◐ | Q3 close PR + coverage matrix |
| **G2.4** | R-CL-Q4 | `uv build` wheels + pinned reproducible install; per-tier images (self-hosted/managed-cloud/sandbox runners); one-command bring-up to readiness-green from a fresh env | ✅ build | Q4 close PR + deploy artifacts |
| **G2.5** | R-CL-D1 | Feature + dependency + user/operator + deployment + architecture/API docs authored; every claim cite-grounded vs HEAD; docs-completeness check (every public surface documented) | ◐ tool+signoff | D1 close PR (absorbs RB-DOC-01 per-package READMEs) |
| **G2.6** | R-CL-C1 | **The 5-dimension coverage matrix = 100%** (§3 below) + final adversarial+council completeness critic + phase-9 promotion model applied to remaining bounded-residuals | ✅ matrix + ☐ critic | C1 certification PR + shipped release |

Also gating into Tier 2: **R-CL-P3** (persona TEAM_BINDING breadth e2e — RB-ACT-03, `APPLIED-PENDING-OPERATOR-E2E`) is a `blocks: [Q1,Q2,Q3]` predecessor; its e2e proof is a Tier-2 entry condition.

---

## 3. The 5-dimension coverage matrix (the heart of R-CL-C1)

The C1 `must_pass` is the binding closure object. For **every** item in the denominator, all 5 dimensions must be TRUE:

**Denominator** (from the audit): **108 head `C-*` contracts** + **the CXA typed seams** (31 code-resident / 37 plan-canonical — reconcile per RB-CXA-03 so the count is unambiguous) + **11 ADRs** (F1–F5, D1–D6).

| Dimension | Means | Evidence source | Auto? |
|---|---|---|---|
| **built** | a code carrier exists | overlay (carrier resolved) | ✅ |
| **activated** | production-exercised (a live/e2e proof ran) **or** explicitly ratified-dormant (deployment-gated, e.g. RB-ACT-01/02, RB-SUB-01/02) | evidence ledger (`.harness/codex_credential_gates.jsonl` + e2e records) + dormant-ratification markers | ◐ |
| **tested** | ≥1 executed-path test (not grep) | coverage/evidence matrix (R-CL-Q3) | ✅ |
| **reviewed** | an adversarial / codex review record exists | clearance markers + `.harness/adversarial-review-*` | ◐ |
| **documented** | appears in the D1 doc suite | docs-completeness cross-ref (R-CL-D1) | ◐ |

This matrix is exactly the **per-unit correctness evidence** the reliability assessment flagged as the gap between "present" and "closed." The audit verified **built** (and partially **tested**); C1's matrix is where **activated ∧ tested ∧ reviewed ∧ documented** get certified per item.

---

## 4. Checker contract — `tools/closure_gate.py` (defined; follow-on build)

Mirrors the proven `arc_ledger.py --check` / `substitution_ledger.py --check` pattern (a derive-then-assert CI gate, no hand-maintained state).

```
just closure-gate            # human-readable report: every G-predicate, status, evidence
just closure-gate --check    # exit 1 if any AUTOMATABLE predicate (G1.1-G1.6, G1.5, G2.3-matrix-built/tested, §3) is false
                             #   prints the MANUAL predicates (G1.7/G1.8, G2.1/2/5/6-critic) as a checklist with sign-off status
```

- **Automatable subset** (asserted by `--check`): G1.1, G1.2, G1.3, G1.4, G1.5, G1.6-tally, and the **built + tested** columns of §3. These compose the existing overlay + arc-ledger + substitution-ledger derivations — no new source of truth.
- **Manual subset** (reported, not asserted): G1.7 fork-triage, G1.8 residual ratification, G2.1/2/5 phase sign-offs, G2.6 completeness critic, and the **activated + reviewed + documented** columns of §3 — each resolved from clearance markers / phase-close PRs.
- **Output is derived fresh from HEAD** (git + filesystem + roadmap), never hand-copied — the anti-drift discipline (`[[regenerate-roadmap-html-after-source-edit]]`).

**Closure is declared** when `just closure-gate --check` is green **and** every manual predicate has a recorded sign-off → R-CL-C1's certification PR cites the green gate as its evidence.

---

## 5. Decisions folded in (reversible; flag if you disagree)

1. **Two-tier split** (build-complete vs quality/close) rather than one flat list — makes "R-FS-1 done" machine-checkable and isolates the human judgment to Tier 2.
2. **The gate delegates, never duplicates** — every predicate points at an existing tool/roadmap-entry/marker. No second source of truth (the R-IF-114 lesson).
3. **Dormant-ratified counts as `activated`** for the coverage matrix — a deployment-gated capability (multi-provider routing, MANAGED_CLOUD) is "activated" via its one-time live proof + a ratified-dormant marker, not a standing deployment (otherwise closure is hostage to ops). This is the one substantive judgment call; an alternative is to require standing deployment, which would pull RB-ACT-01/02 into the critical path.
4. **The checker asserts only the automatable subset**; manual predicates are *reported with sign-off status*, not faked-green. A closure claim therefore always shows exactly which human gates remain.

---

## 6. Current standing (informational, HEAD `46012d5`)

- **Tier 1:** G1.2 ✅ (arc_ledger --check green), G1.5 ✅ (cxa 31/31 HARD green), G1.6-tally ✅ (54/54), **G1.3 ✅ now head-scoped (6 phantoms → 1 documented C-IS-11)**, **G1.4 ◐ head-scoped advisory live (8 entries, all audit-resolved non-gaps)**. G1.1 ✗ (14 registered + 1 gated arcs remain — R-FS-1 ACTIVE). G1.7 ◐ (1 likely-stale OPEN fork). G1.8 ☐ (bounded-residuals pending FULL-SPEC ratify-or-build).
- **Tier 2:** all BLOCKED behind R-FS-1 (correctly — quality runs once on the complete harness). R-CL-P3 e2e pending.
- **Net:** Tier-1 is the live frontier (R-FS-1); Tier-2 is gated and not yet startable. The gate makes this state explicit and machine-checkable rather than narrative.

---

*Closure gate v1. Consolidates `Project_Roadmap_v1.md` §5 R-FS-1 + R-CL-Q1..Q4/D1/C1 `must_pass`. Checker `tools/closure_gate.py` is a defined follow-on. Mode-agnostic; no design-substrate edit.*
