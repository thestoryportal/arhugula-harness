# Relocation pattern — shrink the file without losing the content (R-ICM-1)

Most of a bloated CLAUDE.md is not *rules* — it's *reference* loaded every session but needed
almost never: version-history lineage, per-spec change-note chains, exhaustive pointer tables.
The fix is **not** deletion (loses provenance, breaks cross-references) and **not** blind
truncation (risks a guardrail). It is **relocation**: move the heavy reference content to a doc
loaded on demand, and leave a resolving pointer where it used to be.

This is the highest-leverage move available — the audit's **R-ICM-1** ("split the L0 monolith")
— because one section (§2 "Canonical artifact pointers") is ~81% of the root file and is almost
pure pointer-plus-lineage.

## The pattern

1. **Identify the target** with `measure.py`: a section or set of long lines that is heavy AND
   classified relocatable (history / lineage / pointer-bulk), not load-bearing discipline.
1a. **Scan the block for embedded rules BEFORE you move it.** "Relocatable" is a property of
   *content*, not of a *section name*. A section that looks like pure provenance — an
   "Appendix", "historical notes", a "change-log", a lineage table — can have a load-bearing rule
   buried in it (a stray `CP-AL-1`/`X-AL-3` reminder, a paid-call/secret boundary, an invariant)
   that appears *only* there. The keep-list in `load-bearing.md` is organized by section name, so
   a rule hiding in an off-name section is exactly the one a section-matching pass misses. Before
   relocating any bulk block, read it line-by-line against the keep-list *rules* (not section
   names) and **extract every embedded load-bearing line to stay in the slimmed file** (re-home it
   under its proper section, byte-for-byte). Move only what is left — the genuine provenance. A
   whole-section sweep that carries an embedded guardrail into the home is a dropped guardrail, not
   a relocation; `guardrails_preserved` hard-fails it.

   **Classify by operativeness, not by framing.** Provenance *form* is not the test — a still-in-force
   rule is load-bearing no matter how it's dressed. A dated, past-tense, narrated bullet
   ("On 2026-05-20, after a long thread, the conclusion still in force is that … `CP-AL-1` forbids
   collapsing the boundary") reads as change-history but carries a live rule in its tail. Ask of each
   line: *is this still a rule the agent must obey?* — not *does this look like history?* The trap is
   exactly the bullet that opens as a date and closes as a guardrail. When a rule is **fused into** a
   provenance sentence and can't be cleanly lifted as its own line, treat the **whole mixed unit as
   load-bearing and keep it verbatim** — the rule's presence wins; don't reword to split it (that
   orphans the original line and fails `relocation_not_deletion`). Relocate only the bullets that are
   *pure* provenance — the ones that assert no rule the project must still obey.
1b. **Check what still points INTO the block before you move it.** A block is not relocatable
   just because *it* is reference-heavy — another *retained* rule may depend on it. Before
   relocating any section, grep the slimmed-file content you are keeping for `§`-references (and
   "see §N", "per §N", "defers to §N") whose target is *inside* the block you are about to move.
   A kept rule that says "resolve the conflict by the precedence in §2.3" is **load-bearing on
   §2.3's continued existence at that number**: relocate §2.3 wholesale and the reference dangles
   (`pointers_resolve` hard-fails) — and if §2.3 was also the *only* place an anchor rule was
   stated, the anchor vanishes too (`guardrails_preserved` hard-fails). When a retained rule
   points into a relocation target, **keep the pointed-at subsection (its number, header, and
   body) in the slimmed file** and relocate the rest of the block around it; do not rewrite the
   dependent rule to re-point at the home (that edits a load-bearing line and orphans the original).
   The dependent rule and its target travel together — either both stay, or you have not finished
   the relocation.
2. **Pick a home** — a doc OUTSIDE the always-loaded set but reachable on demand. Good homes:
   a sibling index like `.harness/artifact-pointers.md`, or the canonical files themselves (the
   spec/plan files already carry their own change-notes). **Never** relocate *into*
   `design-substrate/**` (that's the X-AL-3 line) — but you may *point to* design-substrate
   files, since they are already the canonical home for spec/plan lineage. The CLAUDE.md should
   reference that lineage, not duplicate it.
3. **Move the content verbatim** — byte-for-byte into the new home. A relocation is a pure move,
   not an edit; provenance must survive intact. *Every* line you remove from the section lands in
   the home — including the section's descriptive / connective prose, not only the data rows.
   Dropping the framing sentences as "fluff" while moving the table is the most common relocation
   failure: it reads as a deletion, not a move, and loses the context that explained why the data
   mattered. If a line is worth removing from the always-loaded file, it is worth re-homing.
4. **Leave a resolving pointer** where it was — one line naming the new location and what's
   there, so anyone who needs the detail knows exactly where to look. The pointer stub is a *new*
   line you write; it does NOT substitute for re-homing the original. In particular, the section's
   **original header counts as content** — if you shorten or retitle the heading for the stub (a
   verbose "## 2. Canonical artifact pointers, per-axis version lineage, and the full amendment
   history…" becomes "## 2. Canonical artifact pointers"), the original long header is a *removed*
   line and must land in the home verbatim too. "I kept the header" is the trap: a retitled header
   is an edit, not a kept line, and it orphans the original.

   **A line shaped like a pointer can BE the rule, not point to one.** "Re-home the pointer, leave a
   resolving reference" is the move for a *genuine* pointer — a line whose whole job is to send the
   reader to relocatable content stated in full elsewhere. But a sentence can wear pointer clothing
   ("For the paid-call / secret-relocation boundary, see the operator-feedback record: … never fire
   the paid call or relocate the secret without operator authorization") while its tail is the *only*
   place that rule is operatively stated. Relocating it as a "mere citation" drops the rule
   (`guardrails_preserved` hard-fails on the anchor that lived only there). The test is not the "see
   X" framing — it is **does the rule it states live, in force, anywhere that stays loaded?** If yes,
   the line is a true pointer → relocate it. If the operative clause lives nowhere else, the
   pointer-shaped line is the rule's sole home → keep the operative clause in the slimmed file
   (relocate only the genuine provenance it also references). Same operativeness-not-framing test as
   the dated-bullet and worked-example traps, applied to citation-shaped lines.

   **Stub hygiene: a stub references its HOME by path — not the moved block's old §-cross-refs.** A
   relocated section often contained `§`-cross-references to *other* sections ("…detail logged at
   §15"). When you condense that section into a numbered stub, do not carry those internal
   cross-refs into the stub. The trap appears when two sibling provenance streams (§14 lineage and
   §15 retirement-log) both relocate but asymmetrically: you leave a numbered §14 stub that inherits
   §14's "see §15", while §15 is fully absorbed into a home and loses its section number — now the
   stub's `§15` dangles (`pointers_resolve` hard-fails). A stub points at *its home by path* and
   nothing else; if the reader needs the §15 material, it travels with the relocated content into
   the home, where the cross-ref still resolves in context. Before finalizing any stub, grep it for
   `§`-refs and confirm each target is still a section in the slimmed file — drop (don't inherit) any
   ref to a sibling you also relocated.
5. **Verify the move lost nothing**, then verify resolution (below), before proposing the diff.
   The pure-move check is mechanical: diff the slimmed file against the original and confirm
   **every removed line — header, prose, and data alike — appears byte-for-byte in some new home**.
   A removed line that is in neither the slimmed file nor a home is a silent deletion, not a
   relocation, no matter how innocuous it looks (a shortened header is the classic miss). If a line
   left the always-loaded file, it must be re-homed verbatim.

## Worked example (root §2.4)

Before — the always-loaded file carries the full lineage inline (a single ~54 KB line):
```
### 2.4 Per-axis plans (Phase 6 canonical — execution authority)
- harness-cp plan: Implementation_Plan_CP_v2.3.md … [full v1.0→v2.3 change-note lineage, 54 KB] …
```
After — the file carries the pointer; the lineage stays where it belongs:
```
### 2.4 Per-axis plans (Phase 6 canonical — execution authority)
Canonical plans + change-note lineage live in `design-substrate/` (authority), indexed at
`.harness/artifact-pointers.md`. Current heads: CP v2.3 · OD v2.4 · AS v1 · IS v2.2.
```
The 54 KB of lineage is not lost — it's loaded when actually needed, not on every turn. The
always-loaded cost drops from ~54 KB to ~200 bytes for that pointer.

## Byte-exact resolution check (mandatory before proposing)

An optimization that leaves a dangling pointer is worse than no optimization. After editing,
confirm — and let `scripts/check_pointers.py <file>` do the mechanical half:

- Every `[[memory-link]]` you touched still names a real memory file.
- Every `§N` / `§N.N` cross-reference still resolves to a section that still exists.
- Every file path / artifact pointer you introduced or kept resolves to a file that exists.
- The relocated block is present byte-for-byte in its new home (diff the moved block — it must
  be a pure move, not a paraphrase).

This mirrors the existing skill's §10.4 "verify byte-exact before flagging" discipline: a cite
you cannot resolve is either a real defect to fix or a relocation you haven't finished.
