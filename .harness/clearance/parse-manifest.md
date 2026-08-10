# `.harness/clearance/parse-manifest.md` — frontmatter parse-gate exemptions

**R-CTX-1 / U-CTX-10.** `tools/clearance_frontmatter.py --check` requires EVERY
`.harness/clearance/*.md` to carry a YAML frontmatter block that (a) parses to a mapping
with a non-empty `artifact` and `version`, and (b) contains no *lossy* scalar — one whose
stored text is not what YAML reads back. The gate is **fail-closed**: a file that neither
satisfies both nor appears in the table below is a CI failure, never a silent skip.

This file is the complete, explicit exemption set — the files under `.harness/clearance/`
that are *not* clearance markers and therefore have no marker frontmatter to validate. Each
row states the reason. The gate also fails when a row here **starts** parsing as a valid
marker (a stale exemption), so the table cannot silently over-exempt.

## Exemptions

| File | Class | Reason |
|---|---|---|
| `parse-manifest.md` | `not-a-marker` | This file — the gate's own exemption table. Listed here rather than special-cased in `tools/clearance_frontmatter.py` so the exemption set stays entirely data, with no name hard-coded in the gate. |
| `README.md` | `not-a-marker` | Directory convention document for `.harness/clearance/` (root `CLAUDE.md` §4.5 cites it as the convention home). Carries no frontmatter and clears no artifact. |
| `TEMPLATE.md` | `not-a-marker` | The marker skeleton new markers are copied from. Its frontmatter is a placeholder shape (`artifact: design-substrate/<filename>`, `version: v<X.Y>`, a `clearance_type: <one of: ...>` enumeration) that is deliberately not valid YAML and names no real artifact. Quoting the placeholders would make the template teach the wrong shape. |
| `docs-root-hygiene-cleared-2026-06-10.md` | `no-frontmatter` | A narrative repository-documentation hygiene record filed under the `-cleared-` filename convention but predating the frontmatter convention. It records a hygiene pass, not a `design-substrate/` artifact version, so it has no `artifact`/`version` pair to carry. |

## Repair posture for everything else

Every other marker was repaired by `tools/clearance_frontmatter.py --fix`, which is
**quoting-only**: a broken or lossy plain scalar is re-emitted as the same text inside a
YAML double-quoted scalar. No value is reworded, reordered, added, or removed; any scalar
already carrying an explicit YAML style (quoted / folded / literal) and any scalar YAML
already reads losslessly are left byte-identical.

Two scalar hazards drove the repair (root `CLAUDE.md` §12 editing conventions / the
`[[yaml-plain-scalar-hash-and-quoting-hazard]]` pattern):

- **`: ` (colon-space) inside a plain scalar** — YAML reads it as a nested mapping key, so
  the whole block fails to parse (`mapping values are not allowed here`). 70 markers were
  unparseable on this hazard at the arc's grounding sweep.
- **whitespace-preceded `#`** — parses, but silently truncates the value at the `#`
  (`PR #529` reads back as `PR`). This one is invisible to a parse-only gate, which is why
  the gate's second clause (no lossy scalar) exists and why the repair covers the whole
  corpus rather than only the files that failed to parse.

Counts are deliberately not carried inline here: `--check` recomputes them, and its success
line reports the live parse/exempt split.
