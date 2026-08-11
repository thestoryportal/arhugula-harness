# Governance pack — substitution + clearance

*Relocated BYTE-VERBATIM from Root `CLAUDE.md` §4.1, §4.2, §4.5 by U-CTX-13 (R-CTX-1 Arc 5, 2026-08-11).*
*The root file keeps every heading with its number and position, plus a resolving
pointer to this file. Query this pack for the detail; do not preload it.*

---

### 4.1 H_T ↔ H_E substitution discipline

Per `Phase_7_Meta_Architecture_v1.md` §5 (49-row substitution mapping table) + §6 (self-hosting milestone gradient) + §7 (18 axis + 3 cross-cutting anti-leakage rules):

H_E provides bounded substitutions for not-yet-built H_T primitives across 6 substitution-mechanism categories.

**Both tables below are the FROZEN design-phase §5 declaration, not the live tally** — a distinction the pre-R-CTX-1 text elided, which is how the per-axis row went stale. `Phase_7_Meta_Architecture_v1.md` is design-substrate and immutable here (X-AL-3, §4.4); its §5 declares 49 rows and its §5.7 breaks them down by mechanism. The **live** ledger has since decomposed rows (batch-24 split the monolithic `H_T-AS-8` into six sub-rows), so the live cardinality and the live per-axis split both exceed these figures. Per §4.2, live counts are **never** hand-maintained inline — derive them:

```
uv run python tools/substitution_ledger.py --summary   # or --json
```

Design-phase mechanism breakdown, per `Phase_7_Meta_Architecture_v1.md` §5.7 (totals 49):

| Mechanism      | Count | Examples |
|---|---|---|
| H_E-direct     | 11    | H_E filesystem ops; `Edit` / `Read` / `Write` tools |
| MCP-server     | 12    | Substitution routed through MCP server boundary |
| Convention     | 9     | Operator-authored `CLAUDE.md` / prompts |
| Shell-out      | 8     | `Bash` invocations of `git`, `sha256sum`, `python -c` |
| Manual         | 5     | Operator-driven gates (review, approval) |
| Authoring-only | 4     | Substitutions retired at authoring close |

Mechanism is a design-phase attribute only: `.harness/substitutions.yaml` carries no `mechanism` field, so this breakdown has **no** live counterpart and cannot be re-derived. Treat it as history.

Design-phase per-axis counts, per the `Phase_7_Meta_Architecture_v1.md` §5.2–§5.6 section headers: IS=9 / AS=6 / CP=21 / OD=8 / CXA=5 (totals 49). **The live per-axis split is different and is derived, not written here** — `tools/substitution_ledger.py --summary` prints the `axis row-count` line.

### 4.2 Substitution retirement discipline

Per X-AL-2 (Meta-Architecture §7.7):

> Retirement = (cited unit IDs landed) ∧ (substituted H_E surface no longer invoked at substitution site). Both conditions required.

Partial retirement is non-retirement. The `phase-7-substitution-retirement` skill at `.claude/skills/` governs retirement event discipline. Substitution retirement triggers throughout 7b–7d sub-phases, not only at 7d.

**Canonical accounting (R-600).** `.harness/phase-8-graduation.md` records the **frozen Phase-8 close snapshot**: **46/54 RETIRED (85.2%) + 49/54 pipeline-advanced (90.7%)**. That snapshot is a historical milestone, not the live tally. The live per-row dispositions and live counts are the **single source of truth at `.harness/substitutions.yaml`**, DERIVED by `tools/substitution_ledger.py` and surfaced by the status-refresh flow (the CI tally gate `--check` fails on an impossible tally — the count-drift defect class that produced the original `48/54` cannot recur). Cite the derived live number from the tool when needed; do not hand-maintain live counts inline in guidance.

### 4.5 Clearance markers (P5-CK / P6-CK / Phase 7 absorption)

When a design-substrate artifact version is operationally accepted for Phase 7 consumption — whether via original P5-CK / P6-CK adversarial review, Phase 7 in-flight absorption arc, retirement-event doc-hygiene refresh, or architect-recommendation-driven amendment — a **clearance marker** is filed at `.harness/clearance/`.

Marker filename: `.harness/clearance/{artifact-slug}-v{version}-cleared-{YYYY-MM-DD}.md`. Frontmatter pins the artifact path + version + clearance event type + reviewer chain + merge commit. Body narrates what changed and what was reviewed. See `.harness/clearance/README.md` for full convention and `.harness/clearance/TEMPLATE.md` for the shape.

The X-AL-3 guard (§4.4) recognizes clearance markers as back-flow documentation — a PR that lands a design-substrate edit alongside a new clearance marker passes the guard automatically.

Phase 7 sessions consuming a design-substrate artifact SHOULD verify a matching clearance marker exists before treating the artifact's version as canonical. Missing marker → halt + route to operator (the convention is currently advisory at v1; future skill-side enforcement will tighten this).

Retroactive scope: markers are NOT retroactive for back-catalog (pre-2026-05-29). Implicit clearance applies for pre-existing artifacts merged to main and not subsequently invalidated by a fork doc. Forward from 2026-05-29, every design-substrate amendment SHOULD include a clearance marker in the same PR.

---

