# Phase 7 sub-phase 7d — substitution retirement ledger (partial)

**Filed:** 2026-05-17, Phase 7 sub-phase 7d (partial pass). **Skill:** `phase-7-substitution-retirement`.
**Scope:** partial 7d — full closure is gated on Phase 2 (runtime + composition root).

---

## Framing — read this first

This ledger is **process discipline, not progress**. The honest project-status takeaway:

> Phase 7 **design-time** work is complete (7b: all axis units landed; 7c: cross-axis edges reclassified + verified). **Runtime-side substitution retirement is fully gated on Phase 2.**

Per `Phase_7_Meta_Architecture_v1.md` §10.4.2, the retirement criterion's **condition B** ("substituted H_E surface no longer invoked at substitution site") is verified *via runtime trace inspection*. **There is no H_T runtime** — no composition root, no entrypoint (the runtime-entrypoint design gap, `class_1_tension_runtime_entrypoint_design_gap.md`, operator-ruled to Phase 2). Therefore condition B cannot be met for any runtime-active substitution, and **no runtime-active substitution can retire at partial 7d**.

The value of this pass: per skill §5.2/§5.3, **silent carry-forward is forbidden** — every non-retired substitution must be *explicitly* classified bounded-residual with documented rationale. This ledger does that for all 49.

## Retirement criterion (X-AL-2 / Meta-Architecture §10.4.2)

`Retirement = Condition A ∧ Condition B`
- **A** — cited unit IDs landed (acceptance tests passing). **Universally TRUE** — 7b complete (IS 17/17, AS 33/33, CP 58/58, OD 35/35) + 7c.
- **B** — H_E surface no longer invoked at substitution site (runtime trace inspection). **Universally FALSE for runtime-active substitutions** — no runtime exists.

→ For every runtime-active substitution: `A ∧ B = TRUE ∧ FALSE = FALSE`. Not retired.

## Substitution-set reconciliation

The Meta-Architecture §5 table has 51 enumerated rows; §5.7 / skill §2.1 state **49 substitutions**. Reconciliation: the §5.4 CP table carries 23 rows, but **H_T-CP-2 and H_T-CP-5 are dependency-only** ("None — depends on H_T-CP-1") — not substitutions in their own right; they have no independent scaffold and retire when H_T-CP-1 retires. 23 − 2 = 21 CP substitutions. IS 9 + AS 6 + CP 21 + OD 8 + CXA 5 = **49**. *(Class 3 observation: the §5.4 header "21 entries" vs 23 table rows is unobvious without this reconciliation — a Meta-Architecture §5 clarity defect; non-blocking.)*

---

## §1 RETIRED (4) — authoring-only substitutions

Per skill §6.3, the 4 authoring-only substitutions retire at design-phase artifact close (already retired at Phase 6.5 entry — they never carried a runtime surface). Confirmed both conditions: A — carrier units landed; B — no runtime surface ever existed (the substitution was "consult the plan/manifest text"; the manifest is now landed code).

| Substitution | Primitive | Carrier units (landed) | Status |
|---|---|---|---|
| H_T-IS-10 | IS substrate seam exports manifest | U-IS-17 | ✅ RETIRED (authoring close) |
| H_T-AS-9 | AS substrate seam exports manifest | U-AS-33 | ✅ RETIRED (authoring close) |
| H_T-CP-24 | CP substrate seam exports + F2-12 closure manifest | U-CP-54, U-CP-55 | ✅ RETIRED (authoring close) |
| H_T-OD-8 | OD aggregate manifest + F-CP-01 Stage 3b inversion (authoring artifact) | U-OD-34 | ✅ RETIRED (authoring close) |

*Note:* **H_T-OD-1** is NOT authoring-only despite a partial authoring-artifact clause — its §5.5 substitution also carries an active `CLAUDE.md`-convention surface ("scope deferrals tracked in `CLAUDE.md`"). It is runtime-active → bounded-residual (§2).

---

## §2 BOUNDED-RESIDUAL (45) — carried forward to Phase 2

Every substitution below: **condition A MET** (carrier units landed at 7b/7c), **condition B UNMET** (no H_T runtime; the H_E substitution surface remains the operative path). **Shared rationale:** retirement requires an operational H_T runtime to displace the H_E surface; the runtime + composition root is Phase 2 scope (`class_1_tension_runtime_entrypoint_design_gap.md`, operator-ruled). **Unblocking milestone:** Phase 2 runtime stand-up, then per-substitution runtime-trace verification of condition B.

### §2.1 IS axis (8 bounded-residual)
H_T-IS-1, H_T-IS-2, H_T-IS-4, H_T-IS-5, H_T-IS-6, H_T-IS-7, H_T-IS-8, H_T-IS-9 — all carrier units (U-IS-01..16) landed; H_E surfaces still operative (`CLAUDE.md` path/tier convention; `Bash(git *)`; `.harness/state.jsonl` via `Bash` python-c/`cat>>`; stdlib `hashlib`; H_E Checkpointing; `EnterWorktree`).

### §2.2 AS axis (5 bounded-residual)
H_T-AS-1, H_T-AS-2, H_T-AS-4, H_T-AS-5, H_T-AS-8 — carrier units (U-AS-01..32) landed; H_E surfaces still operative (`--permission-mode`; FastMCP server-side authoring; OTel-at-MCP-server emission). H_T-AS-8 additionally blocked on the §3 cross-axis dependency (`anthropic.*` needs H_T-CP-1).

### §2.3 CP axis (21 bounded-residual)
H_T-CP-1, H_T-CP-3, H_T-CP-4, H_T-CP-6, H_T-CP-8, H_T-CP-9, H_T-CP-10, H_T-CP-11, H_T-CP-12, H_T-CP-13, H_T-CP-14, H_T-CP-16, H_T-CP-17, H_T-CP-18, H_T-CP-19, H_T-CP-20, H_T-CP-21, H_T-CP-22, H_T-CP-23 — carrier units landed; H_E surfaces operative (`--model`, `--fallback-model`, `CLAUDE.md` conventions, `Agent` tool, `/compact`, `AskUserQuestion`, `claude mcp`, etc.). **Plus the 2 dependency-only rows H_T-CP-2 and H_T-CP-5** — no independent scaffold; retire jointly with H_T-CP-1. (19 + 2 = 21.)

### §2.4 OD axis (7 bounded-residual)
H_T-OD-1, H_T-OD-2, H_T-OD-3, H_T-OD-4, H_T-OD-5, H_T-OD-6, H_T-OD-7 — carrier units (U-OD-01..33) landed; H_E surfaces operative (`CLAUDE.md` deferral tracking; OTel SDK at MCP server; project-authored Sampler/SpanProcessor at server side; `/cost`/`--max-budget-usd`; `Bash`-launched Collector subprocess; manual operator verification).

### §2.5 CXA seams (4 bounded-residual)
H_T-CXA-1, H_T-CXA-2, H_T-CXA-3, H_T-CXA-4 — endpoint clusters landed; 7c reclassification (CXA v2.3) found the cross-axis surface is 22 genuine typed seams + 46 convention-level + 24 phase-2-runtime. The genuine typed seams are wired *in code*, but the substitution's H_E surface (convention-based composition + the dev workflow) is still the operative path absent a runtime. H_T-CXA-5 — see §3.

**Total bounded-residual: 45** (IS 8 + AS 5 + CP 21 + OD 7 + CXA 4).

---

## §3 Cross-axis retirement dependencies (Meta-Architecture §6.3) — both DORMANT

| Dependency | Status |
|---|---|
| §6.3.1 H_T-CP-1 → H_T-AS-8 (`anthropic.*` namespace unblock) | **DORMANT** — H_T-CP-1 not retired (bounded-residual §2.3). `anthropic.*` remains absent until H_T-CP-1 retires at Phase 2. |
| §6.3.2 H_T-OD-2 + H_T-CP-24 → H_T-CXA-5 (F-CP-01 Stage 3b inversion seam) | **DORMANT** — asymmetric: H_T-CP-24 is authoring-only and *authoring-retired* (§1), but H_T-OD-2 is bounded-residual (§2.4), and the inversion seam operationally requires **both endpoints' runtime substrates active** — which CP-24's authoring close does NOT deliver. The cascade does not fire until H_T-OD-2 retires at Phase 2. Do not read "CP-24 retired" as half-firing this cascade. |

---

## §4 §9 Class 2 substitution-risk surface — REMAINS OPEN

**The most consequential unmet project commitment.** Per Meta-Architecture §9 + §10.4.3: H_T-CP-1 is substituted by single-LLM (`--model claude-sonnet-4-6`) during Phase 7; the **multi-LLM project commitment (ADR-F1 v1.2) is unmet at runtime**. The §9 Class 2 surface closes only at the 7d exit gate, which *requires U-CP-01 runtime retirement* (§10.4.3). Partial 7d cannot close it. **The multi-LLM commitment remains unmet at runtime until Phase 2.** (Met at design + specification + as landed code; unmet at runtime.)

---

## §5 7d closure status

| | |
|---|---|
| Authoring-only retired | 4 / 4 ✅ |
| Runtime-active retired | 0 / 45 — all bounded-residual, condition B gated on Phase 2 runtime |
| 7d full closure | **NOT reached** — requires Phase 2 runtime + per-substitution runtime-trace condition-B verification |
| §9 Class 2 multi-LLM surface | OPEN — closes at Phase 2 7d exit gate |
| Silent carry-forward | NONE — all 49 explicitly classified (§1 + §2) |

Partial 7d is **complete as a partial pass**: the retirement ledger is explicit and exhaustive. Phase 7 sub-phases 7a/7b/7c are design-time-complete; 7d full closure is a Phase 2 deliverable.

---

## §6 Operator ratification required (one consolidated Class 2)

Per skill §5.3, each bounded-residual carry-forward requires operator authorization. The 45 share **one** rationale (Phase 2 runtime gap) under an **already-ruled** routing decision (`class_1_tension_runtime_entrypoint_design_gap.md` — operator ruled the runtime gap to Phase 2). This is therefore **one consolidated Class 2**, not 45: *ratify the 45 substitutions as bounded-residual carried to Phase 2 under the existing runtime-gap → Phase 2 routing decision.*
