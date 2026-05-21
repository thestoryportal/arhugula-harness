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

*(To be appended at the next skill invocation by `systems-architect` skill mode 3. Pattern matches `class_1_tension_cp_20_hitl_gate_composer_underspec.md` "Systems-architect mode 3 resolution recommendation" section + the U-RT-59 Fork 2 systems-architect arc.)*

## Operator ratification

*(To be appended after operator ratifies the systems-architect mode 3 recommendation. Pattern matches the prior fork records' ratification sections.)*

## Status

- **AUTHORING** (this filing) — fork record filed; systems-architect mode 3 not yet invoked.
- Next state: **PROPOSING** at systems-architect mode 3 recommendation append.
- Next state: **RATIFIED** at operator ratification append.
- Next state: **APPLIED** at spec v1.10 + plan v2.8 co-publication landing.
- Next state: **RESOLVED** at U-RT-60 implementation arc landing against the v1.10 §14.8.3 mechanism pin.
