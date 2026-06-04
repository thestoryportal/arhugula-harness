# Stage 3 — Codex + advisor evaluation SYNTHESIS

The two decorrelated evaluators of the reconciled PLAN (`04-reconciliation/round2-reconciled.md` §C+§D). **advisor()** = transcript-aware, in-family (weak-evidence concurrence). **Codex** = out-of-family (gpt-5.5, $0), prompted FRESH (not told the advisor's findings). Full evals: `advisor-eval.md`, `codex-eval.md`.

**Headline:** the two independently converged on the #1 issue — **the PLAN optimizes byte-count, not the operator's actual pain (DRIFT)** — which makes it the strongest signal of the whole arc. This is **plan-changing** → Stage 3b (codex/advisor ⟷ council reconcile) is warranted, run targeted.

---

## Convergence / disagreement map

| | advisor (in-family) | Codex (out-of-family) | Status |
|---|---|---|---|
| **Drift-disconnect** (#1) | #1+#2: proxy-chain never reaches drift; no outcome validation | #1 "Metric substitution" + DRIFT-CONNECTION "Weak… a context slimming plan, not yet a drift-reduction plan" | **CONVERGENT — decisive** |
| **Governance-native bloat irony** | (in-family — could not see) | #2: the plan adds ledgers/gates/hooks/dashboards/loops = the bureaucracy that caused the bloat | **OUT-OF-FAMILY catch** |
| **Verify-before-evict** | (not raised) | #3 + WS-1 risk: prove nothing active depends on §2; archive must be *actually* git-versioned | **OUT-OF-FAMILY catch** |
| **"X" / memory durability** | #3: drop X to detect-only (memory = regenerable hints) | #5 + X-risk: detect-only insufficient — build *minimal recoverability now* (snapshot/version); defer only locking | **DISAGREEMENT → resolved (Codex)** |
| **G1 gate posture** | (implicit) | WS-RISK: guardrail-not-religion; effective-context; override/waiver; warn-then-hard-fail | refinement |
| **"reconciled-to-zero" ≠ correctness** | own caveat (in-family) | #4: same-family agreement ≠ correctness | CONVERGENT (meta) |
| **Process / right-size** | don't fire 2 more 6-agent workflows | (#2 implies it) | adopted |

---

## Consolidated findings the council must reconcile (CA-1 … CA-7)

| CA | Finding | Source | Owner voice(s) | Required PLAN-v3 delta |
|---|---|---|---|---|
| **CA-1** | **DRIFT-DISCONNECT (HIGHEST, convergent).** The PLAN optimizes byte-count/cost; it does NOT define "drift," baseline it, or validate that drift falls. And "what to KEEP + how to POSITION it" (attention budget; a 40KB prefix still rots mid-window) is under-developed vs "evict." | advisor#1+#2, Codex#1+DRIFT | **C8** (drift metric + before/after probe) + **C2** (first-class keep/position WS; reframe the PLAN's success criterion from byte-count → drift-reduction) | (a) C8 defines a **drift metric** (stale-rule use / wrong-canonical-artifact / forgotten-constraint / memory-pollution / bad-resumption / instruction-conflict) + a **before/after use-the-product probe** (slimmed vs current CLAUDE.md). (b) C2 adds **WS-0 "retained-content / attention-positioning"** as first-class (not an eviction byproduct). (c) success criterion = measured drift-reduction, not byte≤cap. |
| **CA-2** | **GOVERNANCE-NATIVE BLOAT IRONY (out-of-family).** The plan's own additions (ledgers/gates/hooks/dashboards/reconciliation/home-of-record) are the same context-bureaucracy that may have caused the bloat. | Codex#2 | **orchestrator + all** | Apply a hard anti-bloat proportionality filter to the PLAN's OWN additions. MVP genuinely minimal; defer aggressively; every new artifact must justify itself against the drift metric. (Self-applies to this loop: collapse Stage-4.) |
| **CA-3** | **VERIFY-BEFORE-EVICT (out-of-family).** WS-1 assumes §2 provenance is historical ballast — true only after proving no active rule/hook/grep-path/recovery/canonical-decision depends on it; and the archive target must be *actually* git-versioned (not "git history somewhere"). | Codex#3 + WS-1 risk | **C2** | WS-1 gains a **precondition**: extract live invariants into a compact contract + a dependency-scan (grep for §2-cell references in rules/hooks/scripts) BEFORE eviction; the archive/index target is a real versioned location. |
| **CA-4** | **MEMORY ROLLBACK is load-bearing (disagreement → resolved toward Codex).** The store-not-git-versioned gap (§C) means a bad write/delete is unrecoverable *regardless of races* → minimal recoverability is load-bearing now; only locking is deferrable. | Codex#5 vs advisor#3 | **C3** | "X" reshaped: **MVP = minimal recoverability** (snapshot/version the memory store + atomic writes + stale-base detection). **Deferred = full serialization/locking** (trigger-gated on an observed race). Detect-only is rejected (can't restore a lost entry). |
| **CA-5** | **G1 guardrail-not-religion.** | Codex WS-RISK | **C5** | G1 measures **effective loaded context** (not raw bytes alone); has an explicit **override/waiver** path; **warning-mode before a clean baseline, hard-fail after**; never forces unreadable compression. Composes with the C5↔C9 never-halt resolution (CI-time guardrail, not in-loop blocker). |
| **CA-6** | **MEMORY.md retention closer to MVP.** MEMORY.md IS session-loaded (every session) → its compaction/retention is MVP-adjacent, not deferred-tail. | Codex MVP-SLICE | **C3** | Promote **enforced MEMORY.md compaction** into the MVP slice (it is session-loaded → directly affects what enters context = drift-relevant). |
| **CA-7** | **"reconciled-to-zero" ≠ correctness (meta).** Same-family agreement is shared taste/blind-spots, not validation. | Codex#4 + advisor caveat | **orchestrator** | The PLAN's validation rests on the CA-1 use-the-product probe, NOT council agreement. State this explicitly in DESIGN.md (the deliverable is falsifiable by the probe). |

---

## Stage 3b plan (targeted — NOT a 6-agent fan-out, per CA-2 + advisor right-size)

Genuine council reconcile with these findings, scoped to the owners: **C8** (NEW — the genuinely-missing eval voice; CA-1 drift metric + probe), **C2** (CA-1 keep/position WS + reframe; CA-3 verify-before-evict), **C3** (CA-4 minimal-recoverability; CA-6 MEMORY.md retention to MVP), **C5** (CA-5 G1 guardrail). CA-2 + CA-7 are orchestrator-applied disciplines folded into the consolidation. C1/C7/C9 carry forward unchanged (their lanes settled in Round 2; C9's X is covered by C3's CA-4).

Output → Round 3 reconciliation → **PLAN-shape v3** (drift-connected + proportionate + minimal-recoverability) → Stage 4 focused adversarial confirmation → `DESIGN.md`.
