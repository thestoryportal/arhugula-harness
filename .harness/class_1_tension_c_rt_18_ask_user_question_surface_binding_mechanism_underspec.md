# Class 1 Tension — C-RT-18 §14.8.3 `AskUserQuestionSurface` H_E binding mechanism underspec

**Filed:** 2026-05-21 — Phase 7 sub-phase 7b pre-implementation review of U-RT-60 at HEAD `c783b06`. Surfaced by `harness-adversarial-reviewer` skill Phase-7 pre-implementation review mode at `.harness/adversarial_review_u_rt_60_pre_impl.md` F3-01 (PROPOSING Class 3 per §4.1 review-severity scale). **Operator ratified F3-01 Class 3 reading 2026-05-21** → routed via `phase-7-back-flow-routing` skill per §4.1 Step 1.a (spec contract under-specifies a surface) + §3.1 routing table (Phase 5 spec revision-pass; in-CLI per workspace `CLAUDE.md` §4.3 + memory `[[design-substrate-divergence]]`).
**Surfaced by:** F3-01 from the U-RT-60 adversarial review record. Routed here via `phase-7-back-flow-routing` skill §4.1 Step 1 classification.
**Substitutions at stake:** **H_T-CP-20** (HITL primitive + 4-response palette + `hitl.*` / `audit.*` namespaces; retirement-gating per Meta-Architecture §5 line 23). The defect at hand is the H_E *binding mechanism* — i.e., the substitution-mechanism category per `Phase_7_Meta_Architecture_v1.md` §5 6-category catalogue (H_E-direct / MCP-server / convention / shell-out / manual / authoring-only) by which the runtime invokes the H_E `AskUserQuestion` tool. Pinning the mechanism is load-bearing for the X-AL-2 retirement-criterion B reading at spec §14.8.3 ("H_E surface IS still invoked at the H_E binding").
**Defect class:** Class 1 — spec contract under-specifies a surface; design-phase artifact requires revision per workspace `CLAUDE.md` §4.3 + X-AL-3 (no silent H_T design extension at Phase 7).

---

## Defect

The `AskUserQuestionSurface` Protocol is declared at spec `Spec_Harness_Runtime_v1.md` §14.8.1 item 2 + bound at bootstrap stage 5 per §14.8.3 — but the **substitution-mechanism category** by which the runtime Python code (`harness-runtime/lifecycle/hitl_gate_composer.py`) invokes the H_E `AskUserQuestion` tool and receives its result is unpinned at the spec-authoring layer.

State of surrounding artifacts:

| Surface | What it specifies | What it does NOT specify |
|---|---|---|
| `Spec_Harness_Runtime_v1.md` §14.8.1 item 2 (line 1455–1459) | `AskUserQuestionSurface` Protocol signature: `async def ask(prompt, options, timeout) -> AskUserQuestionResult`; `AskUserQuestionResult` carrier fields; Protocol surface H_T-canonical (replaceable post-bootstrap by `deliver_webhook` per future C-RT-19 arc) | Which substitution-mechanism category per Meta-Architecture §5 backs the H_E binding; HOW Python runtime emits the question and receives the response; the await-semantics (single-process callback / IPC / MCP request-response) |
| `Spec_Harness_Runtime_v1.md` §14.8.3 (line 1504–1508) | "Synchronous operator-turn invocation per Q1 ratification"; "H_E-backed implementation that wraps Claude Code's `AskUserQuestion` mechanism"; X-AL-2 retirement-criterion B reading | Mechanism category; WHO observes the runtime's emission; WHO injects the operator's response back into the awaiting coroutine |
| `Spec_Harness_Runtime_v1.md` §14.8 "Deferred to implementation discretion" (line 1605) | "Whether `AskUserQuestionSurface` is constructed at bootstrap stage 5 or earlier (suggest stage 5 for symmetry with other dispatcher bindings; **H_E surface availability assumed throughout bootstrap**)" | "H_E surface availability assumed" is precisely the defect surface — the spec asserts the surface is available without naming the category that makes it available |
| `Phase_7_Meta_Architecture_v1.md` §5 line 23 (H_T-CP-20 substitution row) | H_E substitute for H_T-CP-20 = "`AskUserQuestion` tool + permission-prompt approval"; substitution-mechanism category column not enumerated for this row | Which of the 6 categories (H_E-direct / MCP-server / convention / shell-out / manual / authoring-only) the substitution-mechanism column should carry for this row |
| `Phase_7_Meta_Architecture_v1.md` §5 narrative on H_T-CP-20 ("Covers: HITL invocation surface. Does NOT cover: 4-response palette; namespace emission") | The H_E `AskUserQuestion` tool carries the *invocation surface* but not the palette or namespace emission — those are H_T-canonical and emit at the composer | HOW the H_T-canonical composer reaches the H_E invocation surface across the H_E↔H_T substrate boundary (X-AL-1 boundary at MCP server process per workspace `CLAUDE.md` invariant I-4) |
| Runtime plan v2.7 L9-quater AC #2 (commit `fdaf1d7`) | "Bootstrap stage 5 binds `ctx.ask_user_question_surface` to an H_E-backed implementation wrapping Claude Code's `AskUserQuestion` mechanism per spec §14.8.3" | Inherits the spec gap verbatim |

The U-RT-60 implementation arc cannot bind `ctx.ask_user_question_surface` at bootstrap stage 5 without selecting a substitution-mechanism category. The selection is an **architectural decision** per Meta-Architecture §5 6-category discipline, NOT implementation discretion — because:

1. The choice impacts whether condition B of X-AL-2 retirement criterion is satisfied at U-RT-60 landing (the bounded-transport carry-forward reading at spec §14.8.3 assumes a specific transport-category shape).
2. The choice impacts the bootstrap stage-5 binding code shape (single-process callback ≠ MCP request-response ≠ stdout-marker protocol).
3. The choice impacts test-fixture mock semantics (a `MockAskUserQuestionSurface` for single-process callback has different shape than one for MCP request-response).
4. The choice impacts the post-bootstrap durable-async swap at the future C-RT-19 / U-RT-61 arc (some categories admit a cleaner swap than others).
5. The X-AL-1 H_E↔H_T substrate-boundary discipline (process isolation at MCP server process per workspace `CLAUDE.md` invariant I-4) constrains the choice — single-process callback may violate the boundary discipline depending on reading.

## Evidence — current state at HEAD (`c783b06`)

```
# Spec §14.8.3 narrative — H_E binding mechanism not pinned
$ sed -n '1504,1508p' design-substrate/Spec_Harness_Runtime_v1.md
### §14.8.3 HITL gate delivery via AskUserQuestion at sub-phase 7b (Q1 ratification)

Per Q1 ratification, the v1.9 H_E surface for HITL gate delivery is the
`AskUserQuestionSurface` Protocol, bound at bootstrap stage 5 to an H_E-backed
implementation that wraps Claude Code's `AskUserQuestion` mechanism. ...

# Spec §14.8 deferred-list entry — confirms WHEN deferred but not HOW
$ grep -n "AskUserQuestionSurface is constructed" design-substrate/Spec_Harness_Runtime_v1.md
1605:- Whether `AskUserQuestionSurface` is constructed at bootstrap stage 5 or earlier (suggest stage 5 for symmetry with other dispatcher bindings; H_E surface availability assumed throughout bootstrap).

# Plan AC #2 — inherits the gap
$ grep -A2 "AskUserQuestionSurface" .harness/phase-2-session-3-track-a-atomic-decomposition.md | head -6
# (AC #2 cites spec §14.8.3 by reference; no mechanism pin)

# Meta-Architecture §5 H_T-CP-20 row — substitution-mechanism column unenumerated
$ grep -B1 -A4 "H_T-CP-20" design-substrate/Phase_7_Meta_Architecture_v1.md | head -20
# (H_E substitute = "AskUserQuestion tool + permission-prompt approval"; mechanism category not in row)

# Current runtime — no production callsite exists for AskUserQuestion at all
$ grep -rn "AskUserQuestion\|ask_user_question" harness-runtime/src/ harness-cp/src/ 2>/dev/null
# (no matches — the production callsite is what U-RT-60 lands)
```

The H_E↔H_T substrate boundary discipline (X-AL-1: "MCP server boundary; process isolation, not convention" per workspace `CLAUDE.md` §1.1 + invariant I-4) is the cross-cutting anti-leakage rule that constrains the mechanism choice. Single-process callback semantics may bend that discipline; the choice deserves explicit architectural commitment.

## Routing target

Per `phase-7-back-flow-routing` skill §3.1 routing table: **Phase 5 spec revision-pass**. In-CLI per workspace `CLAUDE.md` §4.3 + memory `[[design-substrate-divergence]]` (design-phase back-flow deprecated 2026-05-15; workspace `design-substrate/` is canonical; spec edits in-CLI). Cascade absorptions:

| Affected artifact | Revision required |
|---|---|
| `design-substrate/Spec_Harness_Runtime_v1.md` v1.9 → v1.10 | Amendment at §14.8.3 to pin the substitution-mechanism category (one of 6 per Meta-Architecture §5); cascade NOTE-update at §14.8.1 item 2 narrative + "Deferred to implementation discretion" list (the WHEN entry stays; the HOW entry moves out of the list to §14.8.3 narrative) |
| `design-substrate/Phase_7_Meta_Architecture_v1.md` §5 line 23 H_T-CP-20 row | If the mechanism-category column is enumerated per row in Meta-Architecture §5 (verify at amendment time), update the row's mechanism-category cell to the operator-ratified value. Co-publication or NOTE-form absorption per scope. |
| `.harness/phase-2-session-3-track-a-atomic-decomposition.md` plan v2.7 → v2.8 | Co-publication AC #2 + AC #14 amendment absorbing the spec choice; co-absorbs F2-01/F2-02/F2-03 + F1-01/F1-02/F1-03 secondary findings from the adversarial review record |
| Workspace `CLAUDE.md` §2.3 contract count | Runtime spec version bump v1.9 → v1.10 absorbed |

## Halt state

- **Halt point:** U-RT-60 implementation arc not yet opened (pre-implementation review surfaced the fork before any code lands).
- **Halt timestamp:** 2026-05-21 (this session).
- **Halt rationale:** F3-01 per `.harness/adversarial_review_u_rt_60_pre_impl.md`; operator-ratified Class 3 reading.
- **Resumption requires:** spec v1.9 → v1.10 amendment landed in-CLI; plan v2.7 → v2.8 co-publication; then `phase-7-implementation` skill re-opens U-RT-60 against the re-clearance state.

## Operator-surface decision points

The systems-architect mode 3 resolution recommendation (to be appended below at the next skill invocation) will produce a chain-grounded recommendation among the candidate mechanisms. Operator decision required across at minimum the following question chain:

**Q1 — Substitution-mechanism category selection.** Which of the 6 Meta-Architecture §5 categories backs the H_E `AskUserQuestion` binding at v1.10 MVP?

- **(i) MCP-server-backed.** Runtime emits a tool call through an MCP host; an H_E-side handler intercepts the call and forwards to AskUserQuestion; result re-injected through the MCP response channel. *Precedent: Meta-Architecture §5 MCP-server category covers 12 substitutions; X-AL-1 boundary discipline cleanest at the MCP server process.* Trade-off: requires an MCP-host integration shim; adds boot-time MCP wiring.
- **(ii) H_E-direct via stdout-marker protocol.** Runtime emits a structured `ASK_USER_QUESTION:` JSON marker to stdout; Claude Code interprets the marker, dispatches AskUserQuestion, re-injects the response via a side-channel (stdin / file / socket) that the awaiting runtime coroutine polls. *Precedent: Meta-Architecture §5 "shell-out" + "convention" hybrid; analogous shape to git shadow-Git substitute (shell-out category).* Trade-off: shell-marker protocol is fragile against unrelated stdout noise; X-AL-1 boundary preserved by process isolation but coupling via stdout convention.
- **(iii) Single-process callback.** Runtime invoked INSIDE the Claude Code agent loop (Python harness imported as a library by the H_E agent runtime); `AskUserQuestionSurface` bound to a Python callable that the agent loop services synchronously via Claude Code's tool-invocation API. *Precedent: Meta-Architecture §5 "H_E-direct" category covers 11 substitutions (Edit / Read / Write etc.).* Trade-off: cleanest binding shape + cleanest test mock; but possibly bends X-AL-1 boundary discipline (the runtime + H_E agent share a process; isolation by convention, not by process).
- **(iv) Operator-proposed fourth.** Operator may surface a category not enumerated above.

**Q2 — X-AL-2 retirement-criterion B reading impact.** Does the chosen mechanism change the v1.10 §14.8.3 retirement-criterion B reading? Spec v1.9 currently reads: "The H_E `AskUserQuestion` surface remains as the bounded delivery transport per ... analogous to MCP-server substitution mechanism category." If operator picks (i) MCP-server, that reading is direct. If operator picks (ii) shell-out or (iii) H_E-direct, the analogy must be amended to the chosen category. Does the retirement reading hold under all three categories, or does the choice gate retirement readiness?

**Q3 — `MockAskUserQuestionSurface` test-fixture shape.** Each category implies a different mock shape. The spec §14.8 "Deferred to implementation discretion" list currently suggests a "queue of canned `AskUserQuestionResult` values per call" — this works for all three categories at the test layer, but the integration-test layer needs a category-specific harness. Confirm fixture shape lives at implementation discretion OR pin at spec amendment.

**Q4 — Post-bootstrap durable-async swap impact (C-RT-19 / U-RT-61 future arc).** Does the chosen v1.10 MVP category constrain the future durable-async swap to `deliver_webhook`? E.g., if (iii) single-process callback is chosen at v1.10, the future durable-async impl must bridge from in-process Python to out-of-process webhook delivery — same conceptual swap. If (i) MCP-server is chosen, the swap stays inside the MCP envelope. Confirm the chosen category leaves the swap surface clean.

**Q5 — Cascade impact on Meta-Architecture §5 H_T-CP-20 row.** Spec §14.8.3 amendment co-publishes with Meta-Architecture §5 row update for the mechanism-category column. Does the operator want a single-arc co-publication (one commit) or sequential (spec v1.10 first, Meta-Architecture row update as a follow-on Class 3 drift-resolution arc)?

---

## Systems-architect mode 3 resolution recommendation

*Filed 2026-05-21 by `systems-architect` skill mode 3 against the 5-question chain at "Operator-surface decision points" above. Per skill §4A.4: this is a recommendation, NOT a decision; operator holds decision authority and may counter-propose. Per skill §4A.2 procedure: chain-grounded against the canonical authority chain at workspace `CLAUDE.md` §1.3 — earlier-in-chain artifacts canonical for later.*

### Tension statement (precise)

Three artifacts diverge:

1. **Spec `Spec_Harness_Runtime_v1.md` v1.9 §14.8.3 line 1504–1508 (`design-substrate/Spec_Harness_Runtime_v1.md:1504`):** `"Per Q1 ratification, the v1.9 H_E surface for HITL gate delivery is the AskUserQuestionSurface Protocol, bound at bootstrap stage 5 to an H_E-backed implementation that wraps Claude Code's AskUserQuestion mechanism."` — names the Protocol-level binding; does not name the substitution-mechanism category by which Python runtime reaches the H_E tool.
2. **Workspace `CLAUDE.md` invariant I-4 (`CLAUDE.md` §8):** `"H_E ↔ H_T substrate boundary at MCP server process; process isolation, not convention"` (also at `Phase_7_Meta_Architecture_v1.md` §7 X-AL-1) — pins the boundary mechanism to MCP server process + process isolation.
3. **`Phase_7_Meta_Architecture_v1.md` §5.4 line 384 (`design-substrate/Phase_7_Meta_Architecture_v1.md:384`):** H_T-CP-20 substitution row reads `"AskUserQuestion tool + permission-prompt approval; no 4-response palette; no hitl.* / audit.* namespaces"` — names the H_E surface but the §5.4 table does NOT carry a per-row substitution-mechanism-category column (verified at table read; §5.7 carries only the aggregate breakdown across 6 categories). The mechanism category for this row is implicit.

The divergence is between (1)'s under-specification of the binding mechanism and (2)'s explicit X-AL-1 commitment that the boundary IS at the MCP server process. (3) makes the gap visible at the Meta-Architecture layer (no per-row category enumeration).

### Per-artifact authority-chain placement

Per workspace `CLAUDE.md` §1.3 authority chain (ADR → ADD → PRD → per-axis spec → per-axis plan + CXA):

| Artifact | Chain position | Authority for this tension |
|---|---|---|
| `Phase_7_Meta_Architecture_v1.md` §7 X-AL-1 (also workspace `CLAUDE.md` invariant I-4) | Governance/cross-cutting anti-leakage rule; sibling-canonical with ADR layer per workspace `CLAUDE.md` §2.1 | **Highest** — X-AL-1 is a cross-cutting invariant binding all axes; pins the H_E↔H_T boundary mechanism |
| `Phase_7_Meta_Architecture_v1.md` §5 (6-category catalogue at §5.7) | Substitution discipline governance | **Constrains the choice set** — operator selects from the 6 categories; cannot pick outside |
| ADR-D1 v1.2 (HITL primitive) | Foundational ADR derivative | Authority for HITL semantics; silent on the H_E binding mechanism (the substitution mechanism is a Phase-7 concern; ADR-D1 v1.2 predates the substitution catalogue) |
| Spec `Spec_Harness_Runtime_v1.md` v1.9 §14.8.3 | Per-axis spec | **Diverges** from X-AL-1 by under-specifying the boundary mechanism; X-AL-1 is canonical for the divergence |
| Plan v2.7 L9-quater AC #2 | Per-axis plan | Inherits the spec under-specification |

The authority chain reading is unambiguous: **X-AL-1 (workspace `CLAUDE.md` invariant I-4 + `Phase_7_Meta_Architecture_v1.md` §7) is the canonical authority** for "where does the H_E↔H_T boundary live." X-AL-1 pins it to the MCP server process. The spec v1.9 §14.8.3 narrative is silent on the mechanism, but the chain canonical reading is that the mechanism MUST preserve the X-AL-1 boundary.

### §2 discipline analysis

**Five-axis decomposition.** This tension lives primarily at:
- **Action surface (AS)** — AskUserQuestion is a tool-invocation surface; the binding mechanism shapes how tool calls cross the H_E↔H_T boundary. Touches AS-AL-2 ("H_E built-in tools are NOT user-extensible H_T tools. All H_T tool surface lives behind MCP server boundary" — Meta-Architecture §7 line 522).
- **Control plane (CP)** — HITL invocation is CP-axis-owned (C-CP-20 §20 + H_T-CP-20 substitution); binding-mechanism choice impacts CP composer body shape at C-RT-18.
- **Operational discipline (OD)** — audit-write + span emission at composer body depend on the await-semantics shape of the binding mechanism.

**Probabilistic-deterministic boundary.** The HITL invocation IS the operator-feedback channel — it bridges deterministic harness execution (the composer body emits the gate; spans + audit are deterministic) into the operator's probabilistic judgment. The binding mechanism sits entirely on the deterministic side: it must be reliable, replayable in tests, and have well-defined error semantics. **Mechanism (iii) single-process callback** introduces an unusual reliability surface (the Python runtime and the H_E agent loop share a process; an exception in the runtime can crash the agent or vice versa) — this places reliability on shared-process semantics rather than on process isolation, weakening the deterministic-side discipline.

**Decision ordering (F/D/I).** The binding-mechanism choice is **F-class (foundational)** at the H_E↔H_T boundary layer — it constrains every downstream substitution that requires runtime-to-H_E-tool dispatch (and there will be more: `deliver_webhook` at C-RT-19 / U-RT-61; potentially other future tool dispatches). An F-class divergence from X-AL-1 is more severe than a D-class one per §2.3 of this skill.

**Cross-axis verification.** AS-AL-2 (Meta-Architecture §7 line 522) explicitly states "All H_T tool surface lives behind MCP server boundary." AskUserQuestion at the C-RT-18 composer body is an H_T-side surface (the H_T composer calls into it); even though AskUserQuestion is an H_E tool not an H_T tool, the *binding to it* is an H_T composer surface. AS-AL-2's spirit (and X-AL-1's letter) put that binding behind the MCP server boundary.

### Recommendations (5-Q chain)

#### Q1 — Substitution-mechanism category selection

**Recommendation: (i) MCP-server-backed.** [HIGH]

**Chain citation:**
- **Primary:** workspace `CLAUDE.md` invariant I-4 (`CLAUDE.md` §8) + `Phase_7_Meta_Architecture_v1.md` §7 X-AL-1 — "H_E ↔ H_T substrate boundary at MCP server process; process isolation, not convention."
- **Reinforcing:** Meta-Architecture §7 AS-AL-2 (line 522) — "All H_T tool surface lives behind MCP server boundary."
- **Reinforcing:** Meta-Architecture §5.7 substitution-type breakdown — MCP-server category is the largest single category (12 of 49 substitutions); the project has the strongest substrate of precedent for this category among the three candidates.
- **Reinforcing:** spec §14.8.3 line 1506 already analogizes the retirement reading to "MCP-server substitution mechanism category" — the spec's own retirement-criterion reading anticipates this choice.

**Why (ii) and (iii) fail the chain:**
- **(ii) stdout-marker protocol** preserves process isolation (Python + H_E agent in separate processes) but holds the boundary by *convention* (the stdout-marker JSON structure). X-AL-1's "process isolation, not convention" reading explicitly forecloses this — convention-held boundaries are exactly what X-AL-1 prohibits. **Class 3 framing-contamination read** (would weaken X-AL-1 at exactly the substitution boundary the H_T-CP-20 retirement depends on).
- **(iii) single-process callback** abolishes process isolation by construction (Python runtime imported as library into H_E agent process). Directly contradicts X-AL-1. **Class 3 framing-contamination read** (would invalidate the cross-cutting invariant for one substitution; cascade hazard for future runtime-to-H_E-tool dispatches).

**Operator counter-propose surface:** if operator's reading of X-AL-1 differs (e.g., reads "process isolation" as meaning "the H_T design is isolated from H_E concerns at the design layer, not at the runtime process layer"), the recommendation flips — but that re-reading would require an X-AL-1 amendment first (workflow revision per `phase-7-back-flow-routing` skill §3.1 routing table → workflow channel; bigger arc).

#### Q2 — X-AL-2 retirement-criterion B reading impact

**Recommendation: Spec v1.10 §14.8.3 retirement reading simplifies from "analogous to MCP-server" to "via MCP-server".** [HIGH]

**Chain citation:** spec v1.9 §14.8.3 line 1506 currently reads `"... the substitution is structurally framed as 'H_E AskUserQuestion wrapped by H_T 4-response palette + namespace emission.' ... the H_E delivery primitive remains as the bounded transport, analogous to Phase_7_Meta_Architecture_v1.md 'MCP-server' substitution mechanism category."` If Q1 picks (i), the analogy becomes direct: the bounded transport IS the MCP-server category, not analogous to it. The v1.10 amendment drops "analogous to" and asserts directly. Retirement-criterion B reading at H_T-CP-20 landing event becomes: "condition B satisfied: H_T-canonical surfaces (4-response palette + `hitl.*` / `audit.*` namespaces) compose at production execution path; H_E AskUserQuestion remains as MCP-server-category bounded transport per Meta-Architecture §5 substitution-mechanism convention; the bounded-transport carry-forward is in-class with the 11 other MCP-server-category substitutions."

**Operator counter-propose surface:** operator may wish to defer the spec-narrative simplification to a follow-on Class 3 drift-resolution (keep "analogous to" at v1.10 to preserve revision-scope minimality). Recommendation: simplify at v1.10 — the analogy-vs-direct phrasing is small but load-bearing for retirement-event clarity.

#### Q3 — `MockAskUserQuestionSurface` test-fixture shape

**Recommendation: leave at implementation discretion; pin the Protocol-level mock at spec via single sentence.** [HIGH]

**Chain citation:** spec v1.9 §14.8 "Deferred to implementation discretion" line 1606 already suggests `"a MockAskUserQuestionSurface fixture that returns a queue of canned AskUserQuestionResult values per call"`. This Protocol-level mock works for any of the 3 mechanism categories at the unit-test layer (the mock satisfies the `AskUserQuestionSurface` Protocol; underlying mechanism is abstracted away). The integration-test layer needs a mechanism-specific harness — at (i) MCP-server, this is an `InMemoryMCPHostFixture` or equivalent; at (ii)/(iii) it would be different — but the integration-test harness is downstream impl discretion regardless.

**Recommended spec amendment:** v1.10 §14.8 deferred-list entry for `MockAskUserQuestionSurface` is upgraded from "suggest" to "MUST satisfy the AskUserQuestionSurface Protocol; the queue-of-canned-results shape is reference for the unit-test layer; integration-test layer harness is implementation discretion." Single sentence; preserves discretion at the layer where it belongs.

**Operator counter-propose surface:** operator may wish to pin the integration-test harness shape at spec — recommendation declines this because the integration-test harness is mechanism-specific and pinning it forecloses future durable-async swap testing flexibility.

#### Q4 — Post-bootstrap durable-async swap impact (C-RT-19 / U-RT-61 future arc)

**Recommendation: (i) MCP-server-backed v1.10 MVP leaves the swap surface cleanest — the durable-async impl stays inside the MCP envelope.** [HIGH]

**Chain citation:** Meta-Architecture §5 line 25 H_T-CP-22 (pause/resume) substitution row + spec §14.8.3 line 1508 — `"At that arc, the AskUserQuestionSurface Protocol gains a durable-async implementation; bootstrap binds the durable-async impl conditionally on deployment surface."` Under (i), the durable-async impl is an MCP-server with different transport semantics (long-polling response, webhook callback, etc.) but the same H_T↔MCP-server seam — the swap is contained inside the MCP envelope. The H_T Python runtime sees only the Protocol change (`ask` returns immediately with a pending-handle; subsequent `resume` call delivers the response); the MCP-server-side impl swap is transparent to H_T.

**Under (ii) stdout-marker:** the durable-async swap requires bridging stdout protocol to webhook delivery — different transport categorically; requires runtime-side switch logic conditional on deployment surface. Bigger refactor.

**Under (iii) single-process callback:** the durable-async swap requires bridging from in-process Python callable to out-of-process webhook delivery — the biggest refactor of the three (the in-process binding semantics fundamentally don't match a durable-async webhook pattern). Likely requires re-authoring the runtime composer to support both modes side-by-side.

**Operator counter-propose surface:** operator may judge the C-RT-19 / U-RT-61 arc remote enough that v1.10 MVP should not constrain on it. Recommendation: even at remote-arc-distance, (i) is the strict superset choice — the swap is no harder under (i) than under any alternative.

#### Q5 — Co-publication scope vs sequential

**Recommendation: single-arc co-publication of spec v1.9 → v1.10 + plan v2.7 → v2.8 — Meta-Architecture §5 amendment deferred as separate Class 3 follow-on (if at all).** [HIGH]

**Chain citation:** verified at this skill invocation that `Phase_7_Meta_Architecture_v1.md` §5.4 line 384 (H_T-CP-20 row) does NOT carry a per-row substitution-mechanism-category column — only §5.7 carries the aggregate breakdown. The cascade absorption originally speculated at the fork record's "Routing target" table ("Meta-Architecture §5 line 23 H_T-CP-20 row mechanism-category column") was based on a misreading of §5's table layout. The actual cascade is:

| Artifact | Required at v1.10 arc | Optional follow-on |
|---|---|---|
| `Spec_Harness_Runtime_v1.md` v1.9 → v1.10 §14.8.3 | YES — pin (i) MCP-server-backed; simplify retirement reading per Q2; upgrade MockAskUserQuestionSurface entry per Q3 | — |
| `Spec_Harness_Runtime_v1.md` v1.10 cascade NOTE-update at §14.8.1 item 2 + §14.8 deferred-list | YES — narrative consistency | — |
| `.harness/phase-2-session-3-track-a-atomic-decomposition.md` v2.7 → v2.8 | YES — co-publication AC #2 + AC #14 absorbing the spec choice; co-absorbing F2-01 + F2-02 + F2-03 + F1-01 + F1-02 + F1-03 secondary findings from adversarial-review record | — |
| Workspace `CLAUDE.md` §2.3 contract count | YES if contract count tracks spec version (verify; if so, single-line update) | — |
| `Phase_7_Meta_Architecture_v1.md` §5.4 per-row mechanism-category column addition | NO — separate scope, would touch all 49 rows | Optional Class 3 drift-resolution follow-on; not blocking |
| `Phase_7_Meta_Architecture_v1.md` §5.7 aggregate count update | NO — choosing (i) does not change category counts (AskUserQuestion is already implicit-MCP-server in the aggregate per the §10 line 942 reading) | None expected |

**Single-arc shape:** matches U-RT-58 / U-RT-59 Fork 2 / U-RT-60 cp_20 fork precedent — spec amendment + plan absorption in one commit (or 2 closely-spaced commits per the spec-writer + implementation-planner skill separation). The adversarial-review F2 + F1 secondary findings absorb into the same plan v2.8 revision rather than requiring a separate revision.

**Operator counter-propose surface:** operator may wish to commit the Meta-Architecture §5.4 per-row column addition at this arc as a hardening pass on the substitution catalogue. Recommendation declines — that touches 49 rows and is meaningfully larger than this fork's scope; would benefit from its own systems-architect arc to determine the canonical category for each row.

### Tiebreaker check

**Single verifiable fact that determines the recommendation:** confirm that `Phase_7_Meta_Architecture_v1.md` §7 X-AL-1 reading "process isolation, not convention" has NOT been amended in any post-2026-05-14 revision. If X-AL-1 has been amended to admit convention-held boundaries (which would be a meaningful workflow-revision-scope change), the Q1 recommendation flips and (iii) single-process callback becomes operator-decision-eligible. Confirmed at this filing: workspace `CLAUDE.md` §8 invariant I-4 (the in-workspace pointer to X-AL-1) reads the original "process isolation, not convention" without amendment as of HEAD `c8f63dc`. ✓

**Secondary tiebreaker:** confirm that no ADR-D1 v1.2 revision postdates X-AL-1 in a way that would carve out a HITL-specific exception. Verified at this filing: ADR-D1 v1.2 (per workspace `CLAUDE.md` §2.2 table) is the latest version; no v1.3 exists; no HITL-specific X-AL-1 exception ADR exists. ✓

Both tiebreakers pass; Q1 recommendation (i) MCP-server-backed is determinate against the authority chain.

### Fork class restatement

Per `Project_Workflow_v1_8.md` §2.7.6 + `phase-7-back-flow-routing` skill §2.1: **Class 1 (halt-execution)** as filed at the fork record. Implications for Phase-7 execution:

- U-RT-60 implementation arc REMAINS HALTED until spec v1.10 + plan v2.8 co-publication lands.
- The recommendation does NOT decide the fork; operator ratification at next AskUserQuestion turn converts the recommendation to applied resolution.
- On operator ratification, the routing chain proceeds: `spec-writer` skill applies spec v1.10 amendment; `implementation-planner` skill applies plan v2.8 absorption (or co-publication); `phase-7-implementation` skill re-opens U-RT-60 against the v1.10 contract.

### Operator decides

Per skill §4A.4: **the operator holds decision authority.** The above recommendation is grounded against the authority chain; the operator may ratify, counter-propose with a chain-grounded alternative reading (e.g., X-AL-1 amendment), or escalate any of the 5 questions for further deliberation.

---

## Operator ratification

*(To be appended after operator ratifies the systems-architect mode 3 recommendation. Pattern matches the prior fork records' ratification sections.)*

## Status

- **AUTHORING** — fork record filed at HEAD `c8f63dc` 2026-05-21.
- **PROPOSING** (this state) — systems-architect mode 3 recommendation appended 2026-05-21. Recommendation: Q1 = (i) MCP-server-backed; Q2 = simplify retirement reading "analogous to" → "via"; Q3 = leave at impl discretion + upgrade spec language; Q4 = (i) leaves swap surface cleanest; Q5 = single-arc co-publication (spec v1.10 + plan v2.8; Meta-Architecture §5 amendment optional Class 3 follow-on). All 5 recommendations chain-grounded against workspace `CLAUDE.md` invariant I-4 + Meta-Architecture §7 X-AL-1 + §5 6-category catalogue + spec §14.8.3 retirement reading. Tiebreaker checks pass.
- Next state: **RATIFIED** at operator ratification append.
- Next state: **APPLIED** at spec v1.10 + plan v2.8 co-publication landing.
- Next state: **RESOLVED** at U-RT-60 implementation arc landing against the v1.10 §14.8.3 mechanism pin.
