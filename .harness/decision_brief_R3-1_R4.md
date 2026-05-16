# Decision Brief — R3.1 (AS micro-pass) + R4 (CP revision)

*Consolidated operator-decision brief, 2026-05-15. 9 decisions. Each: what it
is, the options, the recommendation, why. Approve the batch, or flag the
specific items to change.*

---

## R3.1 — the AS micro-pass (2 decisions)

### D1 — U-AS-20: how the secret-fetching function takes the sandbox tier

`fetch_secret` is the function that retrieves a secret (an API key, a password).
How locked-down the caller is running ("sandbox tier") affects which secrets it
may reach. Question: does `fetch_secret` take that tier as a **plain third
input**, or get it from a **bundled context object**?

- **Option A — plain third input** `(name, scope, tier)`.
- **Option B — bundled context object** `(name, scope)` + a context bundle holding the tier.

**Recommendation: A (plain third input).** The architect just resolved the
*structurally identical* question for the sandbox function (S1/G-1) and chose
"plain input, not bundled" — because a security-significant input hidden inside
a bundle can't be seen in the audit trail and breaks consistency with its
siblings. The same reasoning applies here. Picking A keeps the two functions
consistent with each other and with the decision you already ratified.

### D2 — U-AS-12: the "non-compliance cells" wording  *(genuine judgment call)*

The plan says a solo developer may override sandbox policy "at any cell." The
spec says solo developers may override "at non-compliance cells." Do those
conflict?

- **Reading A — no conflict, just tidy the wording.** "Compliance" is a
  property of the *multi-tenant-compliance* persona's world. A solo developer
  never operates there — so for a solo developer, *every* cell is a
  non-compliance cell, and "any cell" is already correct. Fix = reword the
  acceptance text; no behavior change.
- **Reading B — the plan over-permits.** Treat "compliance cell" as a real
  subset the function must guard against; the function then needs an extra
  input telling it whether a cell is compliance-bound, plus a small spec touch.

**Recommendation: A.** The three persona tiers are solo-developer /
team-binding / multi-tenant-compliance — "compliance" tracks the *persona*, not
an individual cell. A solo developer by definition never sees a compliance
context, so "any cell" faithfully means "any cell they can reach." Reading B
would add an input the function has no way to source. **This is the one I'm
least certain on** — the spec's wording genuinely admits both readings — so
it's the prime candidate if you want to flag one for discussion.

---

## R4 — the CP revision (7 decisions)

### D3 — Q-R4-1: where the new shared-types unit lives

R4 needs a new small unit (U-CP-00b) to hold two shared "kinds of information"
(`AttributeValueType`, `Cardinality`) that 7 CP units all use but nobody defines
in a reachable place. Where does it live: in the **CP plan**, or in the
**shared `harness-core`** area?

**Recommendation: CP plan (U-CP-00b), as R4 proposes.** All 7 users are CP
units — no other part of the system touches these two. `harness-core` is for
things genuinely shared *across* areas; these aren't. Putting it in CP, right
next to the existing U-CP-00, is the honest placement. Clear call.

### D4 — Q-R4-2: the `cardinality` field with no spec column  *(judgment call)*

One CP unit (U-CP-01) has a `cardinality` field, but the spec section it cites
doesn't have a cardinality column — though *other* CP spec sections do.

- **Option A — implementer's discretion.** Cardinality is an established
  concept elsewhere in the CP spec; this one section just doesn't tabulate it.
  Keep the field, fill in sensible values. No spec edit.
- **Option B — extend the spec section** to add a cardinality column.
- **Option C — drop the field.**

**Recommendation: A.** The concept is already spec-blessed in sibling sections,
so it's not an invention — it's a metadata field the section happens not to
tabulate. Filling it in is consistent with the rest of the plan and avoids a
spec edit for a minor, non-load-bearing field.

### D5 — Q-R4-3: the values of a newly-defined category  *(judgment call)*

`ParentRelation` describes how one workflow event relates to another. It was
used but never defined. R4 proposes defining it with three values:
`{ROOT, CHILD_OF, DELEGATED_TO}`.

Note: there's a *similar* category elsewhere in the plan, `ParentRelationship`,
with values `{ROOT, CHILD_OF, SIBLING_OF}` — same first two, different third
(`DELEGATED_TO` vs `SIBLING_OF`).

**Recommendation: accept R4's `{ROOT, CHILD_OF, DELEGATED_TO}`, but this is a
genuine call.** R4's set fits lifecycle-event relations (an event is a root, a
child of another, or delegated from another). But you may want the two similar
categories reconciled to one vocabulary. Flag this if you'd like the
`ParentRelation` / `ParentRelationship` overlap looked at.

### D6 — Q-R4-4: where two identity labels live

`MCPServerID` and `ToolName` — labels identifying a tool server and a tool.
AS-owned (the tools/servers area) or `harness-core` (shared)?

**Recommendation: AS-owned.** Tools and tool-servers are the Action Surface's
domain; AS is the natural owner. CP, which also uses them, picks them up via a
normal cross-area link. Minor, clear.

### D7 — Q-R4-5: a dependency-ordering fix + a carried item

Two things bundled. (1) Two CP units (U-CP-03, U-CP-05) are listed in the wrong
build order relative to their actual dependency. (2) U-CP-23 has a separate,
older "single-vs-dual" wording mismatch.

**Recommendation:** Fix the build-order listing — it's mechanical, just follow
the real dependency. Leave U-CP-23's wording mismatch as a *separately tracked*
item (it's a different kind of issue — wording, not materializability — already
logged as fork-queue item 4); it gets handled on its own, not folded into R4.

### D8 — Q-R4-6: a re-check of one already-built unit

U-CP-15 is already built. The audit noticed its `CapabilityFloor` part was
waved through earlier without a deep check against the spec. Low-severity,
informational.

**Recommendation: schedule a targeted re-check** of U-CP-15 when the coding
lane resumes — bundled with the other "re-check already-built units" to-dos
(U-IS-02, U-AS-02, U-AS-04 are in the same bucket). Not blocking anything now.

### D9 — Q-R4-7: a duplicate that needs one name to win

Two units defined the *same* 8-class event taxonomy under two names:
the already-built U-CP-10 called it `LifecycleEventClass`; the new shared unit
U-CORE-01 (which you ratified in R1) calls it `WorkflowEventClass`. One has to
go.

**Recommendation: `WorkflowEventClass` survives** (R4's recommendation).
U-CORE-01 is the shared carrier — the whole conformance principle is "define
shared things once, in the shared place." U-CP-10 gets converted to *use* the
shared one. Consequence to know: U-CP-10 is already built, so its source code
gets re-pointed to the shared name — that's added to the same "re-check
already-built units" bucket as D8. (`ActorIdentity` placement, also in this
question — minor, accept R4's call.)

---

## Summary

| # | Decision | Recommendation | Type |
|---|---|---|---|
| D1 | U-AS-20 function shape | Plain third input (A) | Clear |
| D2 | U-AS-12 "non-compliance cells" | Reading A — wording fix | **Judgment call** |
| D3 | U-CP-00b home | CP plan | Clear |
| D4 | U-CP-01 `cardinality` field | Implementer discretion (A) | Judgment call |
| D5 | `ParentRelation` values | Accept R4's set | **Judgment call** |
| D6 | `MCPServerID`/`ToolName` home | AS-owned | Clear |
| D7 | U-CP-03/05 order + U-CP-23 | Fix order; U-CP-23 tracked separately | Clear |
| D8 | U-CP-15 re-check | Schedule with resume | Clear |
| D9 | U-CP-10 duplicate name | `WorkflowEventClass` wins | Judgment call (principled) |

Approve all 9 as recommended, or name the ones to change.
