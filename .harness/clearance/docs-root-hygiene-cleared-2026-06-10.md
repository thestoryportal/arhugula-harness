# Docs Root Hygiene Clearance — 2026-06-10

## Scope

Repository documentation hygiene pass covering root Markdown, `.harness` root
Markdown, `design-substrate` root Markdown, and high-level remaining repository
directory hygiene.

## Changes

- Archived historical, non-startup root Markdown files under
  `.harness/archive/root-historical/`.
- Added `.harness/README.md` and `.harness/archive/root-historical/README.md`
  to make the retention policy explicit.
- Added `design-substrate/README.md` documenting why canonical design-substrate
  version files remain root-resident.
- Updated live references to archived root files.

## Boundary

No harness runtime/source implementation behavior changed. Design-substrate
content was not amended semantically; the only new design-substrate file is a
navigation/retention README for operator and agent hygiene.

## Rationale

The audit found that design-substrate filenames are load-bearing exact cite
targets across code, governance, semantic overlay practice, and `.harness`
records. Consolidating them physically would create high drift risk unless a
separate tool-aware design-substrate reindexing arc is opened. The safe hygiene
step is to reduce root clutter and document the retention rules for the large
canonical directories.
