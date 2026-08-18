# Council — Spec_HE_Loop_Lanes_v1 clearance review

**Convened** 2026-08-18 · **Operator directive** D4 (2026-08-18): clearance = adversarial review + Codex + convened harness council; `advisor()` removed. D10: autonomous to close (per-convening halts waived); roster as below; commit/PR/clearance-marker remain operator-gated.

**Target** `.harness/spec/Spec_HE_Loop_Lanes_v1.md` (35 `C-HE-*` contracts; authored from `.harness/adr/ADR-HE-1..4` + corpus). **Repo at** `17011f89c`.

**Roster (harness-aware layer router, multi-axis CP+OD+AS → primaries capped at genuine center):**
- Primaries (E1 A1, independent, blind): **C9** reliability/recovery · **C10** action-safety/blast-radius · **C7** observability
- Consultants (E1 A2, react to primaries): **C5** validation/contract · **C1** orchestration · **C11** operator loop · **C8** eval
- E2 adversarial: `harness-adversarial-reviewer` (Phase-7 pre-implementation mode over a spec)
- E3 out-of-family: Codex (`codex exec`, cold descriptive primer; gate iteration 1 = 6/10, iteration 2 = 7/10 already recorded at `03-codex/`)
- Consolidated reconcile (E2b+E3b merged per COUNCIL-WORKFLOW §2 reorder) → E4 residual sweep → fold + change-note.

**Spine tensions routed to the voices (T1–T10):**
- T1 C-HE-07: P1 wrapper enforcement supersedes R-19 (guard as ordering engine vs blast-radius classifier)
- T2 C-HE-09: single-file `loop_status.md` at shared venue vs v2 item 7 split-by-kind; ACTIVATE scoping
- T3 C-HE-24: ratified 8-field core (+envelope) with 3-field `Finding` projection vs R-25 3-field retarget
- T4 C-HE-06 §8: caller backoff+jitter vs D3 fail-fast lease (E43 #13)
- T5 C-HE-02 §6 / C-HE-04 §3: token-compare takeover + E9 re-publish — sufficient, and lock-free-consistent?
- T6 C-HE-06 §5: OPEN-branch single re-issue vs "never invoked twice"
- T7 C-HE-31 §3/§4: P9(c) boundary siting + advisory→blocking promotion after 20 clean arcs
- T8 C-HE-08: both fences (D5) — `required_status_checks` contexts + `enforce_admins` vs the terminating-refresh path
- T9 C-HE-29: kill threshold "< 2 unique catches in 15"
- T10 §6: sequencing (S3 audit before S4b; instrument-before-claim; pilots vs Phase 0)

**Rules:** genuine invocation (agent adopts its skill first); voices verify at HEAD, never trust the spec's `[V]`; ratified decisions (D-A..D-D, D5–D8) are not re-litigated — consequences may be flagged; findings classified Class 1 / 2 / 3; ledger written by the orchestrator from returned markdown.
