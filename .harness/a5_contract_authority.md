# A5 contract authority record (DRAFT — intended `.harness/a5_contract_authority.md`, not filed)

**Status:** Proposed draft for Runtime spec v1.135 / plan v2.66 (A5 Codex read boundary).
It records where each authority the contract relies on lives and its exact bytes. It is
provenance, not normative content: the contract's behaviour lives entirely in the spec text.
This record does not clear anything.

The SHA256 values below were computed from the files at the listed host origins on
2026-10-01. Six exact full-byte copies, one DERIVED capability summary and four exact LIT snapshots are prepared for the intended in-repo location `.harness/review-evidence/a5-contract-authority/<file>`
(attached in this Proposed candidate; not cleared). LIT provenance is cited only where a local LIT export was
checked. Anything else is marked **GAP**.

## Authorities

**Hash qualification (documentation provenance, not a new verdict).** Attachments that were not Markdown are kept as Markdown documents named `<original>.md`. Each quotes the complete original payload; the SHA256 values in this record are of that original payload (which a reader can extract and hash), not of the surrounding Markdown document.

| # | Authority | Intended copy (`.harness/review-evidence/a5-contract-authority/`) / host origin | SHA256 | Attribution / LIT |
|---|---|---|---|---|
| 1 | First-release profile decision. Its Codex row reads: "Enforce and test a boundary that prevents access to unrelated user files while preserving subscription login. The route stays held until then." This is an agent-authored contract record, not itself direct human consent. | `profile-contract-decision-1.md` / origin `/home/robbo/Work/arhugula-trial/evaluation/production-readiness-arch/profile-contract-decision-1.md` | `f90964269fc1a841c645228f5a02fbfff90bfabe653b2b4aae33172b1af85908` | LIT `cmt-8d4fa328-59f1-406e-bbe6-a56ecd8f5381` (Buford record of an operator answer; names this file's SHA256 `f9096426…`; LIT `created_by` `unknown`; extracted copy `lit-cmt-8d4fa328.json`). It records an agent-relayed operator answer, not direct human consent. The file itself remains untracked in its repository (no Git history) |
| 2 | Independent A5 design GO (feasibility; it did not explicitly approve `executable_paths`) | `a5-opus-design-review.md` / origin `/home/robbo/Work/arhugula-omarchy/.local/24h-acceptance/a5-opus-design-review.md` | `f38694c7c9a369cc743ec3d0aa278cc521c155ef7f486001fa0ebe8d7dbe03e3` | reviewer `fd3adf93-8bd7-4ea0-96fc-e91952ca8b3f` (full UUID as recorded in row 3's in-file attribution; this file itself shows only the prefix); root-preserved LIT record `cmt-2ea82bca-eef7-47b3-b4a2-9e0b76ce37f3` (Buford record; extracted copy `lit-cmt-2ea82bca.json`). This is root's record, not the reviewer's own LIT result and not human consent; **GAP:** the reviewer's original LIT comment is still not verified |
| 3 | Initial A5 HOLD (source blocker persists for Codex, main `5d93b0b`) | `a5-read-boundary-source-review-opus.md` / origin `/home/robbo/Work/arhugula-omarchy/.local/24h-acceptance/a5-read-boundary-source-review-opus.md` | `3884e1748c6bb46f96dfd7d2ee3c411842fd61662e5ba9b2960a565bea10b59c` | in-file attribution `fd3adf93-8bd7-4ea0-96fc-e91952ca8b3f`; **GAP:** LIT comment not verified |
| 4 | Host-capability observation (Landlock ABI 10 active on the preparation host) | DERIVED `host-capability-summary.json.md` (kernel/architecture, Landlock LSM, ABI and errata only; not a copy) / private original retained unpublished at the preparation-host origin | private original `8d0e3ca9ca14138e04725c455d3c2949808b5a269f021f5bc8d23a7a16501746`; summary `eaa76c5e03b5fc0d261339680c6b553373207f5dcd56adeedcddc2fd5bf1079c` | in-file author `f235114c-1e99-4108-a00e-9a5e2755cba9`, assignment `cmt-37c52d97-2779-4f32-906c-6101dfca272c` (also carried in the derived summary); LIT result `cmt-b48505fe-d758-416a-891d-7ba89ec83b55` by `claude_f235114c-1e99-4108-a00e-9a5e2755cba9` names `host-capabilities.json` sha256 `8d0e3ca9…` (prefix) for assignment `cmt-37c52d97` (extracted copy `lit-cmt-b48505fe.json`) |
| 5 | Current qualified source GO on frozen A5 `a2573ac217103bb2c9a72f33b12f3ef86df0abb0` | `a5-final-source-review-report.md` / origin `/home/robbo/Work/arhugula-omarchy/.local/24h-acceptance/a5-final-source-review/report.md` | `0010948561ab2f4dd115cb1f4fa965c26fa3f8db8d97ef23e41eb73490472842` | reviewer `01a0f692-3256-72e3-8d95-4bf7e7046e8f`, assignment `cmt-7445a7ac-c28b-4cd4-a0a6-0ba34ce22f57`; LIT verdict comment `cmt-90822ace-389d-44db-85a3-ddf25a782e30`, verified in the local export `a5-frozen-review-lit.json.md` (`9b96bc04873cd62fb849cc34e8753084e36814de13da95b296ff395035c2c6f7`); the exact snapshot `a5-frozen-review-lit.json.md` is copied into this pack |
| 6 | Independent review of the first N draft (HOLD, three P2s) | `opus-a5-normative-review.md` / origin `/home/robbo/Work/arhugula-omarchy/.local/24h-acceptance/opus-a5-normative-review.md` | `e2ea328c7dfae06c5f55b81c0bf95e1d89846c986fb49f747d5f5a1606d62c0b` | assignment `cmt-37f7cb5e-d375-4c93-972b-7db2ff8e036f`, verified in the local export `opus-a5-normative-review-assignment-lit.json.md` (`823787c089ee0a88db5741799da4d817eebcfef69474683a604d7dda54a638cf`); **GAP:** the review's own LIT result comment was not verified; the exact snapshot `opus-a5-normative-review-assignment-lit.json.md` is copied into this pack |
| 7 | Root disposition accepting all three P2s and selecting an explicit Proposed contract for `executable_paths` | `a5-normative-fix-next.txt.md` / origin `/home/robbo/Work/arhugula-omarchy/.local/a5-normative-fix-next.txt` | `2447bb8891fd5848d45a824564c2c535f3659930c405add0d2990a5ae726fb4c` | LIT `cmt-4a845309-0b9e-4f63-9992-ca22917c3ef2`, verified in the local export `a5-normative-fix-assignment-lit.json.md` (`b03203b58586c915fbcf6bf45c6931763e950acf8bcb2f221d002b3ae0571b3b`); the exact snapshot `a5-normative-fix-assignment-lit.json.md` is copied into this pack |
| 8 | Root unit-ID decision: A5 keeps U-RT-158; A4 moves to U-RT-159 | `a4-unit-id-assignment-lit.json.md` (exact LIT snapshot) / origin orchestration workspace `.local/24h-acceptance/a4-unit-id-assignment-lit.json` | `49837d24d18e5a9d57caf33e20613ba515feca853901142b425e3638cc3d4a6a` | LIT `cmt-fcde66ad-1705-4ba8-bc49-7a4e03d4b0e0` (created 2026-10-01T14:16:49Z; body FROM Buford lead `01a0f594-02cb-72a1-8a9b-46c32e99f1a8`; LIT `created_by` is `unknown`). Agent-authored routing decision, not human consent. The A5 counterpart is `cmt-94d7e8aa-aa45-4d0a-91cc-521e3482be5f` (not copied). **GAP:** the decision rests on root's tracked-tree collision scan `unit-id-collision-live-1419.json`, which is host-only and not in this pack; a collision recheck is owed at landing |

## Portability

Root selected portable evidence. Prepared for `.harness/review-evidence/a5-contract-authority/`
(not yet filed in the product repository):
- **Six exact full-byte copies:** rows 1, 2, 3, 5, 6 and 7, each checked against the SHA256
  above.
- **One DERIVED summary, not a copy:** row 4. It also carries the original's non-secret author and assignment fields. The raw host-capability file stays private and
  unpublished at its origin, because it contains host metadata. The summary carries only the
  kernel/architecture, Landlock LSM, ABI and errata facts, with the private original's
  SHA256. It is evidence from one preparation host, not CI evidence and not proof that any
  runner provides ABI 9 or higher.
- **Four exact LIT snapshots:** rows 5–8, each checked for its recorded SHA256, comment ID
  and issue.
- **Three extracted LIT comments** (rows 1, 2 and 4): single entries copied from root's export
  `a5-authority-gap-candidates-1556.json` (`e8565b4fe55bc8040c7c824813cb000869c1f13096ff7d9c23bd83372f5974dd`), which is a root-export snapshot, not
  human authority.

So this is six exact public copies plus one derived summary, not seven exact copies. Until
filing, the record still resolves only on the preparation host. Host origins are kept for
provenance. The exact copies keep their original bytes, including the host paths they quote and generic host facts in their prose (for example, a review's description of the mode and contents of the operator's `~/.codex`). They contain no credential contents and no raw host-capability metadata; publishing them is a root decision to make with that in view.
The LIT GAPs above are unchanged: copying bytes does not establish a missing LIT link.

## Not in this record

There is no clearance status, no clearance marker content, no head or pointer row, and no
claim that any authority above clears v1.135 or v2.66.
