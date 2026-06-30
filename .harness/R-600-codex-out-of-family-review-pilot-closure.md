# R-600 Codex out-of-family review pilot closure

**Arc:** `R-600-codex-out-of-family-review`  
**Closed on:** 2026-06-30  
**Posture:** mode-agnostic process-governance closure

## Disposition

`R-600-codex-out-of-family-review` is ready to move from ACTIVE pilot to RESOLVED.

The pilot's tooling close shape already landed: `just codex-review`, `just codex-review-uncommitted`, and the subscription-auth guard exist as the operator's out-of-family artifact review path. The open question was whether the A/B observation produced enough signal to keep and institutionalize the discipline.

## Evidence

- `CLAUDE.md` now makes `just codex-review` the default out-of-family concrete-diff reviewer and explicitly says it earned its keep on Wave 1/2.
- `.codex/notes/codex-autonomous-loop.md` keeps out-of-family review as a mandatory pre-merge gate for autonomous arcs.
- Multiple later clearance/fork artifacts record unique Codex catches on high-blast-radius diffs, including built-but-vacuous runtime-loader plumbing, at-most-once crash-resume issues, and governance/doc drift that in-family review did not catch.
- The uncommitted-review flaw audit narrowed the safe default to branch-vs-base review and preserved local substitute/decorrelated checks when tenant policy blocks private uncommitted-diff upload.

## Ongoing Rule

Resolving the roadmap pilot does not remove the review discipline. It means the pilot is no longer an open roadmap item: out-of-family review is now a standing engineering gate, with tenant-policy exceptions recorded locally when uncommitted private-diff upload is blocked.
