# Class 3 Tension — ADR-F4 role label mismatch (informational)

**Filed:** 2026-05-16 — surfaced during runtime-gap investigation.
**Defect class:** Class 3 — non-blocking substrate-inventory drift; documentation.

## Observation

`CLAUDE.md` §2.2 maps **ADR-F4 → "Workflow lifecycle primitive"** and
**ADR-D2 → "Sandbox tier"**. But `design-substrate/ADR-F4.md` content is the
**four-tier sandbox-isolation ADR** (title: "Adopt graduated-isolation as a
four-tier sandbox tier-set …"). The §2.2 table and the file content disagree on
which ADR is which.

## Impact

None at present — no unit cites ADR-F4 by role label. Logged because
substrate-inventory drift of this kind misdirects future corpus navigation
(e.g. someone looking for the workflow-lifecycle ADR would open the wrong file).

## Routing target

Operator — reconcile `CLAUDE.md` §2.2 against the actual ADR file contents, OR
correct the ADR filenames. No code impact. Update
`Canonical_Substrate_Inventory.md` once reconciled.

**Status:** OPEN — informational; non-blocking.
