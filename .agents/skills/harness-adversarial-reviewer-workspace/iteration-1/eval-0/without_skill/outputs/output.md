# Adversarial Red-Team Review — C-IS-03 (Combined git tier role decomposition)

**Artifact under review:** `Spec_Information_Substrate_v1_PREFIX_tension001.md` §3 C-IS-03 (lines 176–209)
**Review scope:** C-IS-03 as written, plus its declared compositions with C-IS-01, C-IS-02, C-IS-04, C-IS-05, C-IS-06, C-IS-07, C-IS-08, C-IS-09, and the §[traceability] matrix.
**Posture:** Hard red-team prior to spec lock. Findings are classified by severity. Class 1 = blocks lock; Class 2 = must resolve or explicitly defer with rationale; Class 3 = should fix, non-blocking.
**Verdict:** **DO NOT LOCK.** Two Class 1 defects (F-1, F-2) and one Class 1-adjacent integrity gap (F-3) must be resolved first. C-IS-03 as written is internally inconsistent on its own headline count and ships an unreconciled dual-chain integrity model.

---

## Class 1 — Blocks lock

### F-1 — The headline "four sub-roles" count contradicts the spec's own enumeration

C-IS-03 declares its contract surface as a **four**-sub-role decomposition in three places:

- Line 178: *"Four-sub-role git tier composition with foundational-vs-opt-in posture per sub-role."*
- Line 188: *"The combined git tier serves **four sub-roles** within a single git repository."*
- The §[coherence pass] Audit 6.1 (line 657) reinforces: *"C-IS-03 4-sub-role schema (enum)."*

But every actual enumeration in the section lists **five**:

1. The sub-role table (lines 190–196) has five rows: **Versioning**, **State-ledger via commit stream**, **JSONL event ledger**, **Shadow-Git checkpointing**, **Worktree-isolation**.
2. The "Sub-role co-residence contract" bullets (lines 200–204) enumerate five matching items.
3. The ADD §2.2 Synthesis quotation embedded at line 182 enumerates five distinct roles: *"code/spec/prompt/manifest/Skill versioning ... + ... state-ledger via commit stream ... + JSONL event ledger ... + ... shadow-Git checkpointing ... + worktree-isolation."*

This is not a wording nuance. The contract surface — the thing P5-CK clears and Phase 6 implements — is mis-stated. Either the count is wrong (should be five) or the table conflates two rows that the prose treats as one. The likely root cause: the author mentally grouped "commit stream" and "JSONL event ledger" as one composite "state-ledger" sub-role (C-IS-01 line 130 actually calls the state-ledger a *"Two-mode composite"*), but then split them into two table rows without updating the count. The spec must pick one model and apply it consistently across line 178, line 188, the table, the co-residence bullets, and the §[coherence pass] audit row. As written, the canonical contract surface is undefined.

**Severity:** Class 1. A spec cannot be locked when it disagrees with itself on the cardinality of its only contract surface.

### F-2 — Two independent hash chains are committed and never reconciled

C-IS-03 commits **two** distinct integrity-bearing chains and treats them as a complementary pair without ever specifying how they relate:

- **Commit-stream chain.** Table row 2 (line 193): *"Append-only state-ledger expressed as the git commit stream itself (commit hashes form a chain natively)."* This is git's native parent-commit Merkle DAG — SHA-1 (or SHA-256 in git's newer object format) over commit objects.
- **JSONL `prior_event_hash` chain.** Table row 3 (line 194) plus C-IS-06: a `SHA-256(canonicalize(entry))` chain over six-field JSONL entries, with RFC 8785 JCS canonicalization, an `ALL_ZEROS_SENTINEL` inception, and a `verify_chain` procedure.

Line 193 frames them as *"commit-stream-as-coarse-grain-ledger pairs with JSONL-as-fine-grain-ledger."* That is the entire reconciliation the spec offers — an adjective pair. It never specifies:

- Whether the two chains must agree (e.g., does each JSONL append correspond to a commit, and must the commit's tree contain that exact JSONL line?).
- What `verify_chain` (C-IS-06.4) means when the JSONL chain verifies but the commit stream has been rewritten, or vice versa.
- Which chain is authoritative for tamper-evidence under R-IS-03's acceptance criterion. C-IS-06.5's tamper-evidence table is written **exclusively** against the JSONL chain — it never mentions the commit stream — yet C-IS-03 line 193 asserts the commit stream *is* a state-ledger with chained hashes.
- The cross-granularity mapping: one commit can span many JSONL entries (see F-4), so "coarse" and "fine" are not two views of one chain — they are two chains at different resolutions with no declared join.

A state ledger with two integrity mechanisms and no statement of their relationship is under-specified at the most safety-critical point in the axis. Phase 6 cannot implement `verify_chain` against this. Compliance-readiness (Persona §10.4, cited at line 184) depends on a *single, defined* answer to "is the ledger intact?"

**Severity:** Class 1. The integrity model is the load-bearing claim of the Information Substrate axis, and it is bifurcated without resolution.

### F-3 — Tamper-evidence is asserted for the commit-stream sub-role but the substrate does not provide it

C-IS-03 row 2 (line 193) and the co-residence bullet at line 201 assert the git commit stream is an *"append-only state-ledger."* C-IS-06.5 builds an entire tamper-evidence contract on the premise that entries are append-only and immutable.

Git history is **not** append-only at the substrate layer. `git rebase`, `git commit --amend`, `git filter-branch`/`filter-repo`, `git reset` + force-push, and `git update-ref` all rewrite history. "Append-only" for the commit stream is a **policy** the harness must enforce — it is not, unlike git's per-commit content atomicity (correctly cited in C-IS-04 line 237), a property git gives you for free.

C-IS-03 specifies no enforcement contract: no ref-protection requirement, no no-force-push invariant, no signed-commit / signed-tag requirement, no statement of who holds write access to the ledger ref. C-IS-08 §8.4 carefully isolates shadow refs so they *"do not pollute the main branch,"* which shows the authors were thinking about ref hygiene — but the main-branch ledger ref itself has no protection contract. Without it, the commit-stream "tamper-evidence" is defeated by any actor with push access silently rewriting history; the chain still verifies because the rewrite reconstructs valid parent links.

Contrast: the JSONL chain (C-IS-06) is genuinely tamper-evident because `prior_event_hash` is content-derived and a mid-chain edit breaks downstream verification. The commit-stream chain has no equivalent guarantee unless the spec adds a ref-immutability contract.

**Severity:** Class 1-adjacent. If F-2 is resolved by declaring the JSONL chain authoritative and demoting the commit stream to a non-integrity-bearing convenience, this collapses into F-2. If the commit stream is retained as an integrity surface, this is an independent Class 1 gap.

---

## Class 2 — Must resolve or explicitly defer with rationale

### F-4 — JSONL-append-to-commit cadence is contradictory across sections

C-IS-03 co-residence bullet 3 (line 202): *"JSONL event ledger is a file artifact tracked in git ... appends to the file produce diff-traceable commits."* Read literally, every JSONL append produces a commit — i.e., commit-stream cadence collapses to per-event.

This contradicts the rest of the spec:

- C-IS-03's own table row 2 (line 193): commit cadence is *"workflow-canonical commit cadence per workflow class"* — i.e., tunable, not fixed at per-event.
- C-IS-03 "Deferred to implementation discretion" (line 208): *"Specific commit cadence policy per workflow class"* is deferred — which presupposes cadence is variable.
- C-IS-08 §8.2 establishes that cadence in this system is workload-tunable across `per_step` / `per_tool_call` / `per_significant_change` / `per_explicit_marker`.

So: is there one commit per JSONL append (line 202's plain reading), or is JSONL-append cadence decoupled from commit cadence (line 193 + line 208)? The two readings have materially different consequences — per-append committing inflates repo size (the exact failure mode C-IS-08 §8.2 cites as the rationale for `per_explicit_marker` on pipeline workloads) and forces the JSONL chain and the commit chain into lockstep (relevant to F-2). The spec must state the relationship explicitly.

### F-5 — Versioning sub-role artifact-class list disagrees with C-IS-04

C-IS-03 table row 1 (line 192) says the Versioning sub-role covers *"Code/spec/prompt/manifest/Skill."* C-IS-04 — the atomic deploy contract, which row 1 explicitly says it *"Composes with"* — enumerates the deploy unit as **four** artifact classes: *"Prompts ... Code ... Eval-sets ... Routing manifest"* (lines 224–229).

Discrepancies:
- C-IS-03 lists **Skill** and **spec**; C-IS-04 does not.
- C-IS-04 lists **Eval-sets**; C-IS-03's row-1 list omits evals entirely.

C-IS-04's heading is literally *"Atomic prompt + code + eval + manifest deploy contract."* If versioning and atomic deploy are composed (they are, per line 192 and line 239), the set of atomically-versioned artifact classes must be identical in both contracts. Right now a reader cannot tell whether Skills and specs are atomically deployed, or whether eval-sets are versioned by the Versioning sub-role. This also propagates to C-IS-01, which enumerates exactly four filesystem artifact classes (Skills, Prompts, Routing manifest, State-ledger — no "spec," no "eval-set" as a top-level class). Three sections, three different artifact-class lists.

### F-6 — C-IS-03 is under-traced: claims R-IS-02 only, but delivers R-IS-03 substance

C-IS-03 "PRD requirement(s) satisfied" (line 180) lists **R-IS-02 only**. The §[traceability] matrix (line 635) confirms: *"C-IS-03 (R-IS-02)."*

But C-IS-03 table row 3 (line 194) states the JSONL event ledger sub-role *"per-event records carry the canonical six-field entry shape (per C-IS-05); hash-chain integrity constructed per C-IS-06."* Entry shape and hash-chain integrity **are** R-IS-03 (per C-IS-05 line 252 and C-IS-06 line 290, both traced to R-IS-03). C-IS-03 is therefore a composition point for R-IS-03 and should trace to `R-IS-02 + R-IS-03`, consistent with how C-IS-07 (line 356) and C-IS-10 (line 635) are traced to both.

The §[coherence pass] Audit 6.2 (line 666) claims *"Every session-1 PRD requirement has ≥1 spec contract"* passes — that aggregate pass is unaffected, which is precisely why this gap is easy to miss. But the per-contract traceability is wrong, and a locked spec with an under-traced contract invites a Phase 6 implementer to build the JSONL sub-role without consulting the R-IS-03 acceptance criteria.

### F-7 — Worktree-isolation framed "for reads" while the underlying primitive is read/write

C-IS-03 table row 5 (line 196) and the co-residence bullet at line 204 frame worktree-isolation strictly as a *concurrent-read* primitive: *"isolates concurrent reads from sibling sub-agents"*, *"reads do not contest with one another."* C-IS-09's title is "Worktree-isolation contract" and §9.3 is a "Concurrent-read isolation invariant."

`git worktree` is a generic working-directory primitive. A sub-agent in its own worktree can **write** — edit files, stage, commit — and nothing in C-IS-03 or C-IS-09 §9.1–§9.3 forecloses it. The spec never states the contract for the write case:
- Is sub-agent write into a worktree prohibited (read-only mount)? If so, by what mechanism, and what happens on a write attempt?
- If permitted, how do concurrent sub-agent writes compose with the C-IS-07 §7.1 C3-pole append-only single-writer contract, and with the "at most one harness state-ledger per repo" cross-sub-role consistency invariant (line 206)?

The §[carry-forwards] / cross-axis surface cites *"Cognition's single-threaded-write convergence"* (C-IS-09 ADR citation, line 469) — which signals the authors know multi-writer is the hazard — yet C-IS-03's decomposition presents worktrees as a benign read primitive with no write-boundary contract. This is a latent X-AL boundary gap.

### F-8 — Shadow-Git ⊕ worktree composition (both opt-ins enabled) is unaddressed

C-IS-03 presents Shadow-Git (row 4) and Worktree-isolation (row 5) as two independent opt-in sub-roles. C-IS-08 §8.4 says shadow refs live in *"the same git repository"* and share the `.git` backend. C-IS-09 §9.2 gives each sub-agent its own worktree directory pointing at *"the same `.git` storage backend"* (C-IS-03 line 204).

When **both** opt-ins are enabled, a sub-agent performing a shadow-Git checkpoint from inside its worktree writes to a ref namespace (`refs/shadow/...`) shared with every sibling worktree and the main working directory. C-IS-03's "co-residence contract" (lines 198–204) asserts the sub-roles *"share the same git repository identity without interference"* but never analyzes this specific four-way interaction. Open questions: do per-sub-agent checkpoints collide in the shared `refs/shadow/` namespace? Is checkpoint cadence per-worktree or per-repo? Does a rollback (C-IS-08 §8.3, *"filesystem-bounded"*) in one worktree affect siblings? The "without interference" claim is asserted, not demonstrated, for the one composition that actually risks interference.

### F-9 — "Append-only state-ledger" vs C-IS-08 rollback is glossed

C-IS-08 §8.3 correctly notes rollback *"does NOT restore the state-ledger ... rollback writes a new entry recording the rollback event."* Good. But C-IS-03's co-residence bullet 3 (line 202) says the JSONL ledger file is *"tracked in git (versioned via the versioning sub-role)."* If the ledger file is git-tracked and a shadow-Git checkpoint snapshots tracked paths, a rollback could restore an **older version of the JSONL ledger file itself** — directly violating append-only. C-IS-08 §8.3's "filesystem-bounded ... under the workflow's tracked paths" does not carve the ledger file out. C-IS-03 should state explicitly that the state-ledger path is excluded from shadow-Git rollback scope, or reconcile the contradiction.

---

## Class 3 — Should fix, non-blocking

### F-10 — The "four/five-sub-role decomposition" is presented as the contract surface, but only holds at maximal opt-in

Two of the sub-roles (Shadow-Git, Worktree-isolation) are `workload-class-opt-in`. For the common workload that opts out of both, the runtime composition is a 3-sub-role tier, not 4 or 5. C-IS-03 presents the full decomposition as *the* contract surface (line 178) without distinguishing the always-on foundational core (Versioning + commit-stream + JSONL = the minimum guaranteed shape) from the opt-in extensions. The §[coherence pass] "Contract grade" audit (line 657) calls C-IS-03 a *"4-sub-role schema (enum)"* — but an enum two of whose members are conditionally absent is a surface/runtime conflation. Recommend the spec explicitly name the foundational-3 as the guaranteed substrate and the opt-in-2 as extensions.

### F-11 — Multi-tenant ledger composition asserted "F2-compatible" with no contract

The cross-sub-role consistency invariant (line 206) says cross-repository state-ledger composition is *"out of scope at F2 substrate layer"* but *"per-tenant repository isolation at multi-tenant binding is the F2-compatible scaling shape."* This asserts a scaling posture (one repo/ledger per tenant) while declining to specify how — or whether — multiple per-tenant ledgers compose for a tenant-spanning audit. For a compliance-readiness persona (§10.4) this is a foreseeable need. Either state that tenant-spanning audit is explicitly out of scope, or note it as a known gap; right now it reads as resolved when it is merely deferred-by-omission.

### F-12 — `ALL_ZEROS_SENTINEL` width is type-ambiguous against the commit-stream chain

C-IS-06.3 defines chain inception as *"`ALL_ZEROS_SENTINEL` (32 bytes of zero)"* — sized for SHA-256. The commit-stream sub-role (C-IS-03 row 2) relies on git's native commit hashes, which are 20-byte SHA-1 in git's default object format. If F-2 is resolved by ever cross-referencing the two chains, the sentinel width and hash width mismatch matters. Minor, but flag it so the F-2 resolution does not silently inherit a width bug.

### F-13 — "diff-traceable commits" claim assumes JSONL line ordering stability

Line 202 claims JSONL appends *"produce diff-traceable commits."* A clean append-only diff (single added line at EOF) holds only if nothing rewrites earlier lines and the file uses stable line ordering. The C-IS-07 §7.1 idempotent-write contract says a duplicate-key write *"is a no-op against the existing entry"* — fine — but if any implementation ever compacts, re-sorts, or rewrites the JSONL file, the "diff-traceable" property silently breaks. Recommend stating the append-only-file invariant explicitly rather than leaving it implied.

---

## Summary table

| # | Finding | Class | Root issue |
|---|---|---|---|
| F-1 | "Four sub-roles" headline contradicts the five-row table / bullets / ADD quote | 1 | Contract-surface cardinality undefined |
| F-2 | Commit-stream chain and JSONL `prior_event_hash` chain never reconciled | 1 | Bifurcated integrity model |
| F-3 | Commit-stream "append-only / tamper-evident" not guaranteed by git substrate | 1 | Policy claim presented as substrate guarantee; no ref-protection contract |
| F-4 | JSONL-append-per-commit (line 202) contradicts tunable commit cadence (lines 193, 208) | 2 | Cadence coupling under-specified |
| F-5 | Versioning artifact-class list disagrees with C-IS-04 and C-IS-01 | 2 | Three sections, three artifact-class lists |
| F-6 | C-IS-03 traced to R-IS-02 only; delivers R-IS-03 substance via C-IS-05/06 | 2 | Under-traced contract |
| F-7 | Worktrees framed "for reads"; primitive permits writes; write contract absent | 2 | Latent multi-writer / X-AL gap |
| F-8 | Shadow-Git ⊕ worktree (both opt-ins on) composition unanalyzed | 2 | "Without interference" asserted, not shown |
| F-9 | git-tracked JSONL ledger file rollback-able by shadow-Git → violates append-only | 2 | Rollback scope does not exclude the ledger path |
| F-10 | 4/5-sub-role decomposition only holds at maximal opt-in | 3 | Surface vs runtime conflation |
| F-11 | Multi-tenant ledger composition asserted "F2-compatible" with no contract | 3 | Deferred-by-omission, reads as resolved |
| F-12 | `ALL_ZEROS_SENTINEL` 32-byte width vs git 20-byte SHA-1 commit hashes | 3 | Width mismatch latent in any F-2 fix |
| F-13 | "diff-traceable commits" assumes unstated append-only line-ordering invariant | 3 | Implicit invariant |

## Recommended disposition before lock

1. **F-1** — Pick four or five sub-roles; apply consistently to lines 178, 188, the table, the co-residence bullets, and the §[coherence pass] Audit 6.1 row. Mechanical but mandatory.
2. **F-2 + F-3** — Decide the integrity model. Cleanest resolution: declare the JSONL `prior_event_hash` chain (C-IS-06) the single authoritative tamper-evidence surface; demote the commit stream to a non-integrity-bearing versioning/coarse-history convenience; delete or heavily qualify the "commit hashes form a chain natively" framing. If the commit stream is retained as an integrity surface, add an explicit ref-immutability / no-force-push / protected-ref contract and resolve the dual-chain `verify_chain` semantics. Either way, C-IS-06.5's tamper-evidence table must state which chain(s) it covers.
3. **F-4, F-5, F-6, F-9** — Resolve in this revision pass; each is a localized inconsistency with a clear fix and a definite right answer.
4. **F-7, F-8** — Either specify the worktree write boundary and the dual-opt-in composition, or explicitly scope them out with rationale. Do not lock with these silently open.
5. **F-10 – F-13** — Address opportunistically; none blocks lock, but F-12 must be re-checked when F-2 is resolved.

Note on revision-pass discipline: the v1 → v1.1 change-note lists C-IS-03 among sections *"preserved verbatim."* F-1 through F-9 indicate C-IS-03 was not adversarially re-examined during the tension001 pass. Resolving the Class 1 findings requires substantive C-IS-03 edits, which means a v1.2 (not a verbatim-preservation) revision and a fresh coherence pass — the change-note at line 52 already anticipates v1.2 as *"the proper moment for fresh coherence pass."* That moment is now.
