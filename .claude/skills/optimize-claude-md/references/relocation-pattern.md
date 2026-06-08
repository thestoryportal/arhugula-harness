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
2. **Pick a home** — a doc OUTSIDE the always-loaded set but reachable on demand. Good homes:
   a sibling index like `.harness/artifact-pointers.md`, or the canonical files themselves (the
   spec/plan files already carry their own change-notes). **Never** relocate *into*
   `design-substrate/**` (that's the X-AL-3 line) — but you may *point to* design-substrate
   files, since they are already the canonical home for spec/plan lineage. The CLAUDE.md should
   reference that lineage, not duplicate it.
3. **Move the content verbatim** — byte-for-byte into the new home. A relocation is a pure move,
   not an edit; provenance must survive intact.
4. **Leave a resolving pointer** where it was — one line naming the new location and what's
   there, so anyone who needs the detail knows exactly where to look.
5. **Verify resolution** (below) before proposing the diff.

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
