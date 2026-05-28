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

**Status:** ✅ CLOSED-via-Path-A 2026-05-27 — broader audit at closure arc surfaced 8 of 11 §2.2 rows mismatched (not just F4/D2): §2.2 labels were from an older ADR numbering scheme; current ADR file content is canonical. Path A applied: workspace `CLAUDE.md` §2.2 re-labeled to match current file content at all 8 mismatched rows (F2 "State ledger primitive" → "Filesystem + git state substrate"; F3 "Index primitive" → "Stateless-reducer durable-execution pattern"; F4 "Workflow lifecycle primitive" → "Graduated-isolation sandbox tier-set"; F5 "Observability substrate primitive" → "Tier-aware secret-fetch abstraction"; D1 "HITL primitive" → "Durable-execution engine-class commitment"; D2 "Sandbox tier" → "Per-deployment-surface sandbox provider commitment"; D3 "Validation contract" → "Anthropic-primitive adoption depth"; D4 "Cost attribution" → "Multi-agent topology — six-pattern taxonomy"; D5 "Topology pattern" → "HITL synchrony palette" [§1.4 storage-form sub-row note preserved verbatim]; D6 "OTel schema" → "Observability backend + OTel schema (12 namespaces)"). F1 + (D2 sandbox cite kept-as-correct) preserved. ZERO design-substrate/ touch; ZERO cross-axis cascade. Sub-species 3.broader-scope-discovered-at-closure-arc — variant of resolved-but-carry-stale where the carry's flagged scope was narrower than the actual defect surface; closure arc audit caught the broader scope before applying.

_Original filing footer:_ **Status:** OPEN — informational; non-blocking.
