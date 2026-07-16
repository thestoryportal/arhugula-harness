---
artifact: design-substrate/ADR-D5.md
version: v1.5
cleared_at: 2026-07-16T00:00:00-06:00
clearance_type: Phase-7-absorbed-via-roadmap-continue
back_reference:
  - design-substrate/ADR-D8_audit_signing_backend.md (v1, Accepted — the sibling ADR this delta cross-references)
  - .harness/clearance/ADR-D8_audit_signing_backend-cleared-2026-07-16.md
  - .harness/forward-register.yaml (B-36 entry, CLOSED)
merge_commit: pending (pre-merge at filing time)
reviewer_chain:
  - "out-of-family Codex review on the initial B-36/ADR-D8 PR landing found ADR-D5.md §1.4 row 3 was left with no cross-reference to the new ADR-D8 despite ADR-D8's own clearance marker asserting the row's deferral was closed for the AWS case — a real, concrete inconsistency, not a style nit; fixed same session"
  - ruff/pyright not applicable (prose-only design-substrate change, no code)
supersedes: null
superseded_by: null
---

# Clearance — `ADR-D5 v1.5` prose-only cross-reference to `ADR-D8`

Records the operational acceptance, for Phase-7 consumption, of `design-substrate/ADR-D5.md` at
v1.5 (delta over v1.4). This is a **bundled design+impl absorption arc** companion delta — landed
in the same PR as `ADR-D8_audit_signing_backend.md` (v1, Accepted) and `B-36`'s closure, per
CLAUDE.md §11.4.

**Scope of revision.** §1.4's per-persona-tier signing-key residence table, row 3
(`multi-tenant-compliance`), gains two sentences: a forward-pointer to `ADR-D8` (which resolves
this row's F5-prod-tech deferral for the AWS case via KMS delegated signing — a different,
more tightly-scoped AWS service than the row's literal "AWS Secrets Manager" enumeration) and a
one-line note in the adjacent "F5 composition contract" column. No table row/column shape change;
no algorithm-default change (Ed25519 remains the default, honored exactly by `ADR-D8`'s choice);
all other §1.4 content, and every other section of the ADR, preserved verbatim.

**Why this delta exists.** An out-of-family Codex review on the initial `B-36`/`ADR-D8` PR
landing correctly flagged that `ADR-D8`'s own clearance marker claimed to close ADR-D5 §1.4 row
3's deferral "for the AWS case," while `ADR-D5.md` itself remained textually unchanged and
unlinked to `ADR-D8` — a reader of the canonical ADR in isolation had no way to discover the
resolution existed. This delta closes that gap, matching the precedent set by the `B-25`/`ADR-D2`
v1.2→v1.3 arc (which amended the sibling artifact it was correcting, in the same PR, rather than
leaving the cross-reference undiscoverable).

## Notes

- Phase 7 consumers may rely on this version (v1.5) as canonical for §1.4's signing-key residence
  table.
- See `.harness/clearance/README.md` for marker discipline.
