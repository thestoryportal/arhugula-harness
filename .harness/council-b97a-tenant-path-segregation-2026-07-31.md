# Council record — `B-97` half (a): per-tenant pause-journal path segregation

*Narrow dyadic re-confirm of the operator-RATIFIED Reading A, convened 2026-07-31 per the fork's own §7/§9 sequencing (gate 1 → **this convening** → gate 2). Grounding HEAD `6e9473e6`.*

| Field | Value |
|---|---|
| Arc | `B-97` half (a) — the durable pause journal carries no tenant binding |
| Primary authority | `.harness/class_2_fork_b97a_pause_journal_tenant_binding.md` (filed PR #1168, merged `59ec1b32`) |
| Register row | `B-97` at `.harness/forward-register.yaml:2888`; `council:` field `:2983-2986` |
| Ratified reading | **A** — per-tenant path segregation, contractually injective encoding, record shape unchanged, five-cause vocabulary intact, mandatory quiesced cutover (operator, 2026-07-31) |
| Convening posture | **Narrow RE-CONFIRM.** The reading is ratified and was NOT on the table |
| Voices | **C3** (state / memory / persistence) ⊥ **C11** (operator loop / local deployment) — dyadic, both primary |
| Spec pre-bind | Runtime `Spec_Harness_Runtime_v1.md` **v1.107** per workspace `CLAUDE.md` §2.3 |
| **Verdict** | **CONFIRM-WITH-CONDITIONS** — unanimous, independently reached, decorrelated grounds |
| Conditions | **17** (`K-1`…`K-17`; 15 LOAD-BEARING, 2 RECOMMENDED) — §7 |
| Posture | Design-phase. This record is the ONLY file this arc writes. No `design-substrate/**` edit, no register flip, no `roadmap_status.md` touch |

---

## §0 — Convening block

### 0.1 Nameable-tension gate (`CLAUDE.md` §10.9 amendment 1)

**Named in advance, before convening:** *does per-tenant address-space isolation (C3's keying-correctness interest) justify orphaning every existing local journal at upgrade and requiring a cutover no operator can verify (C11's operator-loop interest)?* The gate is **PASSED** — the tension is nameable, it is the register row's own `council:` field, and it survived the probe that split its antecedent (§2 P0).

**Voices considered, not convened.** **C10** (action safety / blast radius) — the §5.3.1(ii) existence-oracle question is squarely C10's, but it is **already settled by withdrawal** at the fork's review round 3; convening C10 to re-weigh a foreclosed option is the question-that-does-not-arise failure mode. **C9** (reliability / recovery) — owns the five causes' retry routing, which no condition here touches; handled-by-reference in C3's turn. **C7** (observability) — the admin surface emits state; span design is a follow-on. **C8** (eval) — the witness set is already enumerated at the fork's §9 leg 4.

### 0.2 Layer identification + roster

Layer = **IS** (state / persistence keying) crossed with the **operator-loop** cross-cutting concern. Per the `layer_voice_map`, IS primaries are C2/C3; C2 (context engineering) is not engaged (no prompt surface, no topology change). **Dyadic default honoured** — 2 voices, no consultant tier, no expansion.

### 0.3 Cross-cutting concern register (slim CCR per amendment 3)

| Concern | Touched | Pre-check note |
|---|---|---|
| **Reliability / recovery** | YES | The whole arc is a recovery-substrate re-keying; the live question is whether a violated cutover degrades refusing or silently. Answered at P4 — it degrades **silently** for (3b). |
| **HITL / local-first** | YES | C11's seat. The upgrade cost lands on the single-tenant local default, whose path changes even though it never had a tenant problem. |
| **Cost** | YES (bounded) | One never-growing orphan file per pre-cutover workflow; the real cost is the upgrade event, not storage. |
| **Security / blast radius** | Partially — **handled by reference** | The fork §3(iii) already establishes that no reading defends a writable-disk adversary; the withdrawn (ii) oracle is C10's and is foreclosed. No new exposure is created by any condition below. |
| n/a | — | Observability, eval-ability: not engaged beyond the witness set the fork already enumerates. |

### 0.4 Stage record

| Stage | What ran | Outcome |
|---|---|---|
| pre-convene | Fork read in full (1028 lines); orchestrator probes P0–P7 | Antecedent split confirmed; two disputes pre-identified |
| **E1·A1** | C3 and C11 convened as **genuine dedicated agents**, each adopting its own `SKILL.md` first, **independent and blind** to each other | Two decorrelated positions, both CONFIRM-WITH-CONDITIONS |
| **E1·B** | Cross-read debate — each voice engaged the other **by name**, with orchestrator probes P5/P6 supplied | 12 converged points; reciprocal concessions in both directions; 1 genuine residual |
| **orchestrator adjudication** | The residual (C3's target-lock) resolved at primary source | Superseded by a term already in the fork — see `K-4` |
| **E2** | In-family adversarial pass over this record | §11.1 |
| **E3** | Out-of-family `just codex-review-uncommitted` (GPT-5.6, subscription, $0) | §11.2 |
| **E4** | Residual sweep + re-verify at HEAD | §11.3 |

**Mechanism note.** Every voice turn was a **genuine invocation** — a dedicated agent that first adopted its `cN/SKILL.md` and then spoke. The orchestrator composed the envelope, ran the probes, and wrote this ledger; it did **not** speak for either voice. Both voices independently re-verified every orchestrator probe at source before absorbing it, and both recorded corrections to their own prior positions in-body rather than silently restating.

---

## §1 — Scope: what was, and was not, on the table

**On the table — exactly three items**, per the fork's §7 brief:

1. The **mandatory quiesced cutover** (§5.3.2(a) + §5.3's quiescence term) — who quiesces, how it is verified, and whether a violation is detectable-refusing or silent.
2. The **untenanted-legacy disposition** — (3a) abandon-by-default, and what the operator-facing diagnostic owes: §5.3.1 **(i)** alone vs **(i)+(iii)**.
3. The **injective-encoding choice as config-vs-constant**.

**NOT on the table, and not relitigated:** Reading A vs A+B vs B vs C (ratified); §5.3.1**(ii)** (withdrawn at the fork's round 3 as an existence oracle — neither voice was permitted to weigh it and neither did); the refusal shape §5.2; the no-rider call §5.4; the two-gate sequencing.

**Reopening criteria, per the fork's own SOUNDNESS EXIT note (`:1017-1018`):** a defect in the recommended Reading A, in the injective-encoding contract term, in the two-gate sequencing, or a cite that fails to resolve at HEAD. **None is met.** Both voices swept for them independently and both reported the same negative. This record does **not** manufacture a finding to appear rigorous — the reading is confirmed, and what follows are conditions on the *spec leg*, not doubts about the *reading*.

---

## §2 — Orchestrator probes (amendment 5: council surfaces, primary sources decide)

All run by the orchestrator at HEAD `6e9473e6` and re-verified independently by both voices. Counts are programmatic, not eyeballed.

### P0 — the register's council antecedent SPLITS `[HIGH]`

The row's `council:` field (`.harness/forward-register.yaml:2983-2986`) conditions the convening on *"if a tenant key adds local-deployment config burden."* Verified: `RuntimeConfig.tenant_id` already exists (`harness-runtime/src/harness_runtime/types.py:2027`), defaults `None`, and already reaches **both** construction sites — capture-side (`bootstrap/factories/pause_resume_protocol_factory.py:199-201`) and read-side (`api.py:775`, store built at `:808`, `config` its first parameter). **Zero config burden on the (3a) default path.** The antecedent as literally written is therefore FALSE — but the convening is owed on the **restated** cost the row did not anticipate (the upgrade/abandonment burden), exactly as the fork's §7 records. The fork's split is confirmed, not rounded off.

### P1 — no directory-scoped liveness predicate exists `[HIGH]`

`pidfile_path` defaults to `repository_root / ".harness/runtime.pid"` (`types.py:2171-2179`; `repository_root` at `:1702`), while the journal directory resolves from `config.path_bindings` via `PathResolver` (`lifecycle/journal_workflow_pause_store.py:223-234`). The two are **independently configured**. Under `B-97`'s own premise topology — two differently-tenanted deployments sharing one resolved `STATE_LEDGER` dir — there are two pidfiles in two unrelated trees and **neither is reachable from the journal directory**. Corroborating: `"quiesc"` occurs **0 times** in `Spec_Harness_Runtime_v1.md` (programmatic); the adjacent vocabulary is *drain*, which is per-process and in-flight-step scoped.

### P2 — the in-house migration precedent leaves quiescence UNENFORCED, and enforces the other half `[HIGH]`

`admin/migrate_audit_sidecar.py:25` states *"Run ONCE per upgraded deployment, while no harness process is active"* as **docstring prose with no liveness probe, no pidfile read, no lock**. The same module *does* enforce its target-state precondition **in code** (`:26-28`, `:59` — *"refuses to run when a sidecar already exists"*). This is precisely the asymmetry the fork's §5.3 terms (1) and (2) reproduce: **the empty-target term is machine-checked; the quiescence term is prose.** The module also records why it exists at all — an earlier migration *"had no supported invocation path … so every pre-sidecar deployment's first audit read or append failed permanently"* (`:6-8`). This workspace has already shipped this exact upgrade defect once.

### P3 — nothing enumerates the pause-journal directory `[HIGH]`

Full sweep of `harness-runtime/src`: the only consumers are `pause_journal_dir_for` (`journal_workflow_pause_store.py:223`), `api.py:808`, and `pause_resume_protocol_factory.py:201` — **each resolving exactly one `sha256`-named path** via `_journal_file` (`:358-361`). No `glob`/`iterdir` touches the directory anywhere. The store states it as a design property (`:218-219`: *"Reads open one sha256-named path directly and nothing globs this directory"*). Independently corroborated: the `harness_runtime/admin/` family is **8 modules**, and a case-insensitive match for `pause` hits **zero** of them; `harness-inspect` contains the string 0 times. **Consequence:** §5.3's stated recourse — *"the operator's recourse is to drain pauses before upgrading"* — has **no supporting surface at HEAD**, and the filenames are irreversible digests, so even a manual `ls` yields opaque hex.

### P4 — a violated (3b) adoption is SILENT and it EXECUTES `[HIGH]` — the strongest finding of the convening

Checked against every shipped guard. An adopted-but-stale record is **internally self-consistent**, so:

- §30 snapshot-workflow match (`Spec_Harness_Runtime_v1.md:3306`) — **passes**.
- Step-index range (`:3307`) — **passes**.
- `snapshot_hash` — **passes**; `:3306` states it validates against the snapshot's *own embedded fields*.
- The NEW v1.107 staleness precondition — **does not fire at all** on the ordinary durable-restart path: `api.py:840-841` is `if not isinstance(resume_context, AccessorDerivedResumeContext): return`, and every `resume_handle` crash-recovery caller is exactly that case. Even when it does fire, `:852-866` compares against the journal's *current* state, so a stale **copy** is indistinguishable from a fresh read.

**Not one shipped guard is a recency check.** Compounding: the store carries **no hash chain** (unlike C-IS-05's 6-field chained ledger) — `snapshot_hash` is an intra-record self-hash with no `previous_hash` link — so a publication that **drops complete records** (a truncated prefix) leaves **no structural trace and no post-hoc forensic path** — there is no gap signal to detect. *(Narrowed at E3 [P2], which correctly rebutted a broader earlier claim: a **torn tail** IS detectable — the partial latest line fails to parse and the read returns `corrupt-latest`, while `_append`'s leading-newline self-heal preserves the fragment as its own non-latest line, `journal_workflow_pause_store.py:475-481`. The undetectable case is dropped complete records, not a torn one.)* By contrast a violated **(3a)** cutover degrades to `ABSENT` (`journal_workflow_pause_store.py:293-301`) — refusing, but **misdiagnosing**, since §30's `absent` repair (`:3318`) reads *"this workflow never journaled a pause — check `durable=True`"*.

### P5 — the directory-tree lock is MECHANICALLY INERT here `[HIGH]`

`harness-is/src/harness_is/cross_process_ledger_lock.py:174` — `SCOPE_LOCK_FILENAME = ".cross-process-scope.lock"`; `:210` — `lock_file = scope_root / SCOPE_LOCK_FILENAME`. The pause journal's append lock is a **different inode**: `PAUSE_JOURNAL_LOCK_SUFFIX = ".lock"` appended to the journal path (`journal_workflow_pause_store.py:210-220`, composed at `:416`). `flock` contends **only on the same inode**. The scope-lock module states the failure condition in its own words at `:193-195` — it serializes *"any writer in the tree **that takes the same scope lock** … (**a writer outside it is simply unserialized**)"*. The pause-journal appender does not take it. **A migration holding the scope lock over the journal directory would exclude ZERO writers.**

### P6 — there are TWO in-house tenant-normalization authorities, with INCOMPATIBLE untenanted dispositions, BY DESIGN `[HIGH]`

- OD's `sidecar_tag` → `_normalize_tenant_tag`: `None → "_single"` (a **reserved string literal**), consumed by `lifecycle/audit_writer.py:627-643` (`_tenant_tag`).
- Runtime-local `normalize_tenant_scope` (`lifecycle/protected_result_store.py:183-199`): `None → None`, refusing `""`/`"_single"`. Its docstring states the divergence is deliberate: *"The store's own tenant-tag normalization (**Runtime-local; mirrors OD v1.34 §21.2.1 row 2's rule-set without importing OD's private helper**)."*

Further, `_encode_scope_prefix` (`:247-262`) records the reserved-sentinel scheme as **a defect it fixed**: *"The round-7 scheme hex-encoded a reserved sentinel STRING for the `None` case … but `RuntimeConfig.tenant_id`'s own validator reserves only `""`/`"_single"`, so a config-valid deployment named `_untenanted` silently lost ALL post-effect recovery under that fix. Prefixing with a marker character (`u`/`t`) outside `_encode_tenant_tag`'s hex alphabet (`0-9a-f`) makes the two branches disjoint for EVERY possible tenant string, **so no literal needs reserving at all**."*

**Consequence for the fork:** §7's parenthetical *"the single-tenant local default (whose scope normalizes to the `_single` sentinel)"* is **FALSE at HEAD** — no normalization is bound for this store at all, and the sibling Runtime store's authority yields `None`, not `"_single"`. **This does not reopen the reading:** the untenanted default's path changes either way, because `sha256(workflow_id)` cannot equal `sha256(encode(None, workflow_id))` under any total encoding. The **conclusion stands; the mechanism description is wrong** and is a spec-leg correction (`K-16`).

### P7 — already-shipped primitives the conditions consume, at zero new persistence `[HIGH]`

- `PauseJournalReadResult.record_count` (`journal_workflow_pause_store.py:197-200`) — *"Monotonically non-decreasing … so two successively observable records always differ here"* — and `latest_record_digest` (`:202-203`). Minted by the `B-69` leg; exactly the read-back-verification primitive.
- The half-(b) per-workflow `flock` (`:364-429`), crash-clean (*"released on process death"*, `:371-372`), **documented no-op on Windows** (`:411-413`).
- §14.8.11 `:4809`'s publication contract, verbatim: *"Creation is collision-safe WRITE-ONCE: a write against an existing key is REFUSED TYPED, never overwritten. Publication is CRASH-ATOMIC and DURABLE … BEFORE the atomic no-replace commit exposes the composite key, and the DESTINATION directory metadata is made durable AFTER the commit."*
- Two in-house injective-encoding disciplines: the **length-prefixed segment** shape (`harness-od/src/harness_od/multi_tenant_trace_separation_and_audit_ledger.py:281`, docstring `:295-303` — the *"B-23 injectivity shape"*, injective **across arity**), and the **hex-encode + out-of-alphabet marker** shape (`protected_result_store.py:237-262`).
- The `harness-inspect` **read-only invariant**, spec-declared at `Spec_Harness_Runtime_v1.md:3693` and enforced in code at `admin/inspect.py:22-25` (*"MUST NOT write to any file. Tested via chmod-readonly fixture"*), with an extension precedent at spec `:1199` (§13.5 audit-verification inputs *"extends the §13 admin-CLI contract"*) and `admin/inspect.py:115-122` (`--browse`).

---

## §3 — Voice positions

Both voices produced a full independent position (E1·A1) and then engaged the peer by name (E1·B). What follows is the **net** position with the movements recorded; neither voice's text is smoothed.

### C3 — state / memory / persistence

**Framing.** The pause journal is a *Tier-3 checkpoint store on a Tier-5 medium* — append-only write, latest-record-only read (`Spec_Harness_Runtime_v1.md:5834`). The **keying** defect is Tier-3; every hard question left is Tier-5. Ratified-A is correctly a Tier-3 fix.

**Item 1 — cutover.** *"The operator invokes; but the operator must not be the mechanism."* Replace declared quiescence with a **mechanically-held exclusion + read-back verification**, which together make quiescence an optimization rather than a safety property. Produced P4 (the silent-(3b) guard-battery proof) and the no-hash-chain observation.

**Item 2 — legacy disposition.** Abandon-by-default is acceptable; **(i) alone is not**, because ratified-A **creates** a durable class that is *"unreachable and unenumerable by any code path in the product"* while `:5834` forbids removing its records — an FM-G pruning-silent failure **owned by this arc**, not pre-existing.

**Item 3 — encoding.** Fixed **constant**, never configurable: *"a location knob relocates an address space; a derivation knob re-partitions it."* Named the length-prefix family, and independently verified the **normalization layer's injectivity** — a check nobody had run — reporting it as a clean confirm rather than dressing it as a finding.

**Movements at E1·B (recorded, not smoothed).** Adopted C11's ground for (iii) as **primary**, demoting its own. Accepted C11's three sharpenings. **Conceded it had over-priced the landing** (a §13.4 inventory row → a cheaper §13.5-shaped extension). **Dropped its disposal requirement** on discovering the `harness-inspect` read-only invariant forecloses it. Conceded that its exclusion term was **ambiguous exactly where it mattered** — it had not named which path the lock is taken on. **Withdrew its C-9 delegation target** under P6 — *"my cited delegate was wrong, and I withdraw it"* — with three reasons given so the record shows reasoning rather than capitulation, chiefly that the audit-domain precedent's mandatory delegation exists to keep a **join key** byte-identical across two producers, and *"the pause-journal key joins to nothing outside itself."*

### C11 — operator loop / local deployment

**Item 1 — cutover.** *"Do not spec it as an operator instruction; spec it as a refusal the tool computes."* Produced P1 and the §13.4/§13.5 landing analysis. Its decisive framing: *"stating an unverifiable MUST is precisely how you get a migration that 'held every stated precondition' and corrupted anyway."*

**Item 2 — legacy disposition.** Produced P3, and with it the finding that reframes the whole sub-decision: §5.3's stated recourse is **not actionable at HEAD**, so (3a) as written is not *"abandon a bounded set"* but *"abandon an unknowable set and misdiagnose it afterwards."* Therefore **(iii) is a precondition of ratifying (3a)**, with three sharpenings the fork does not carry — **pre-flight** as well as post-mortem; **enumerate**, never probe a derived path (*"a single-path probe on an admin binary is the withdrawn (ii) in a hat"*); land on **`harness-inspect`**, not a new binary, engaging only when a journal directory exists so an ordinary local developer's output is byte-unchanged.

**Argued AGAINST its own axis's instinct on (3b)-as-default** — which §7 explicitly invited it to propose — on three grounds: the failure-mode asymmetry; that (3b) *"makes the harness ask every upgrading operator to attest to something the system deliberately never wrote down"* (the store is never handed a scope — `__init__` takes `journal_dir` only, `:248-249`); and that the burden/benefit runs backwards on the local default, where the loss is cheapest.

**Item 3 — encoding.** Fixed constant; found that the encoding *"already exists at HEAD as a hardcoded module constant with zero configuration surface"*, and that **both** of its historical refinements were collision fixes a config knob would re-open per deployment.

**Movements at E1·B.** **Conceded the directory-tree lock** under P5 (*"my proposal was mechanically inert"*). **Adopted C3's read-back verification**, and sharpened its justification beyond what C3 gave — it covers the three cases the lock structurally cannot: a **pre-#1167 writer that takes no lock at all**, the **Windows no-op**, and **filesystem-level interference**; *"read-back, not the lock, is what makes the migration safe in the scenario the cutover term was written for."* **Adopted C3's asymmetry condition wholesale** (*"I had it as rationale; C3 makes it spec text, which is strictly better … an unwritten default rationale is a default a later arc flips on convenience"*). **Moved to C3's encoding shape** (length-prefixed segments handle the untenanted branch by segment count alone — no marker character needed).

---

## §4 — TENSION block

### SEAM 1 — C3 ⊥ C11 · the (3b) exclusion primitive — **surfaced + PROBE-RESOLVED, both ways**

**Positions.** C3: hold *the same exclusion the append path takes* (the per-workflow `flock`). C11: hold a **directory-tree** lock, because *"the per-workflow choice was correct for the append path and is the wrong reflex for a migration"* — and take it on the **legacy source** path, not the target.

**Probe (P5) resolves it, splitting the pair.** C3 supplies the correct **lock object**; C11 supplies the correct **target**. Neither alone is right: a tree lock contends on a different inode and excludes zero appenders, while locking the tenant-composite target excludes nothing that matters because a straggler computes the **legacy** key. **Status: probe-resolved; both voices conceded their own half at E1·B on independent re-verification.** Merged at `K-2`.

### SEAM 2 — C3 ⊥ C11 · does the exclusion need a SECOND lock on the TARGET? — **surfaced + ORCHESTRATOR-ADJUDICATED**

**Position (C3, E1·B).** Yes — legacy-only leaves the round-8 empty-target test as a **TOCTOU race**: test target empty → an upgraded writer captures at the new key → adoption publishes over **newer** state. C3 flagged this itself as possibly *"convergence-on-inspection rather than genuine dispute"*, since C11 (writing in parallel) had not addressed it.

**Adjudication at primary source.** The hazard is real; the second lock is **not** the fix. §14.8.11 `:4809` — the publication contract the fork's §5.3 fourth term already imports — is **WRITE-ONCE with an atomic no-replace commit**: *"a write against an existing key is REFUSED TYPED, never overwritten."* Under a no-replace commit, a target created between the pre-check and the publish makes the **publish fail**, not overwrite. The commit **is** the empty-target enforcement, atomically; any separate pre-check is advisory only. **This resolves the seam by REMOVING a mechanism rather than adding one** — a second lock would be redundant with the atomic commit and would add a second lock-ordering hazard. Recorded at `K-4`, with the residual re-run interaction (`K-5`) stated.

**Status: adjudicated; C3's hazard accepted, C3's remedy superseded by a term the fork already carries.**

### SEAM 3 — C3 ⊥ C11 · the tenant-normalization delegate — **surfaced + PROBE-RESOLVED in C11's favour**

**Positions.** C3 (E1·A): delegate to *"the existing single normalization authority"*, citing `audit_writer._tenant_tag:627-643` — *"a third copy would be the same defect a third time."* C11: reject that delegate; it maps `None` to a reserved literal and imports a scheme the sibling durable store **fixed**.

**Probe (P6) resolves it.** There is no *single* authority — there are two, with incompatible untenanted dispositions, and the Runtime-local one is a **deliberate, documented non-import**, not drift. **C3 withdrew at E1·B**, adding the sharper reason: the audit precedent's delegation is mandatory because a **join key** must stay byte-identical across two producers, and the pause-journal key **joins to nothing outside itself**.

**Status: probe-resolved and conceded.** Merged at `K-15`. C11's still-contested table lists this as open only because both voices wrote their E1·B turns in parallel; C3's concession is on the record and this seam is **closed**.

### SEAM 4 — C3 ⊥ C11 · does this arc owe a retention POLICY? — **surfaced + CONVERGED on a floor, residual scoped OUT**

**Positions.** C3: *"a retention policy nobody can execute is not a policy"* — (iii) is the enumeration surface a policy requires, plus an operator-invoked disposal action. C11: *"I will not let this arc author a retention policy … naming an unmanaged class honestly is a complete discharge of this arc's duty toward it."*

**Resolution — converged on the floor, from both directions.** C3 **dropped disposal** on discovering the `harness-inspect` read-only invariant (P7) forecloses it — *"my disposal requirement is defeated by a mechanism, not by preference."* C11 independently reached the same constraint and routed disposal to a **separate** `python -m` surface, adding an operator-loop hazard C3 had not priced: *"an operator who upgrades, discovers via (iii) that pauses were abandoned, and reaches for disposal has destroyed their only (3b) recovery path using the very tool that told them the records existed."*

**The LOAD-BEARING floor both voices hold:** state the permanence **and** state the orphan-vs-live-record distinction. C3's clause forecloses a misreading in one direction (*"and may never be removed"*), C11's statement forecloses it in the other (*"the harness will silently reclaim these"*). **A disposal action is OPTIONAL** and, if specified, carries C11's constraints. **A retention policy — default, tunable, sweep trigger — is explicitly a FOLLOW-ON ARC and is NOT owed here.** Merged at `K-13`.

### SEAM 5 — C3 ⊥ C11 · how hard to state quiescence — **surfaced + CONVERGED, each correcting the other**

**Positions.** C11: the spec MUST NOT state quiescence as a discharged precondition, and MUST record that no verification mechanism exists. C3: keep the term hard, but replace declaration with mechanism.

**Resolution.** Each corrected the other and both said so. C11 stopped C3 from stating an unverifiable precondition. C3 stopped C11 from concluding a disclaimer is all that remains — *"liveness detection and mutual exclusion are different objects. The migration does not need to know whether a writer exists; it needs to prevent one from writing during its window"*, and holding the lock is **verifiable by construction** (either it was held or the adoption did not run). C3 answered C11's standing invitation honestly: *"I cannot [name a directory-scoped liveness predicate], and I say so plainly: there is none."*

**Merged three-part term:** (a) the negative fact; (b) the mechanically-discharged exclusion; (c) an explicit no-substitute clause. **Status: converged.** `K-1` + `K-2`.

---

## §5 — Reconciliation to zero (concession ledger)

Twelve converged points, reciprocal concessions in both directions, zero unresolved seams.

| # | Point | Movement |
|---|---|---|
| 1 | Ratified-A is **sound** | Both CONFIRM-WITH-CONDITIONS, **independently and blind**. Decorrelated agreement on the load-bearing question. |
| 2 | **(i)+(iii)**, not (i) alone | Converged from **decorrelated reasons**; each voice adopted the other's as primary — C3 took C11's non-actionable-recourse ground, C11 took C3's unenumerable-durable-class ground. |
| 3 | (iii) is **pre-flight, enumerating, on `harness-inspect`** | C11's three sharpenings adopted whole by C3, which also conceded it had **over-priced** the landing. C3's rider added: report `record_count` + `latest_record_digest`. |
| 4 | §30 `absent` tenant-scoped, **meaning AND repair text** | C3's C-5 = C11-3 = the fork's own item 4-bis — now reached from **three** independent directions. |
| 5 | Encoding is a fixed **CONSTANT**, no config surface | Both independently, unaffected by either probe. |
| 6 | Encoding **shape** | **C11 moved to C3's** length-prefix family (injective across arity → the untenanted branch is disjoint by segment count, no marker needed). |
| 7 | **(3a) stays default; (3b) NOT default** | Both — on two independent grounds (C3's detectability asymmetry; C11's non-enumerability). C11 argued against its own axis's instinct here. |
| 8 | **Exclusion primitive** | **C11 conceded** the tree lock (P5); **C3 conceded** its target was ambiguous where it mattered. |
| 9 | **Read-back verification** | **C11 adopted C3's**, and sharpened the justification past what C3 gave (the three cases the lock structurally cannot cover). |
| 10 | **Asymmetry as spec text** | **C11 adopted C3's wholesale**, with a reason C3 had not stated (an unwritten default rationale gets flipped later on convenience). |
| 11 | **Normalization delegate** | **C3 withdrew** its OD delegate under P6; both now bind the Runtime-local authority. |
| 12 | Orphan-vs-live-record distinction must be **stated** | C3's textual half accepted by C11 and merged with C11's permanence statement; C3 **dropped** disposal from the (iii) surface. |

**Reconciled to zero.** Every seam is closed by probe, by adjudication, or by mutual concession. The one item C11's table lists as open (SEAM 3) was already conceded by C3 in the parallel turn.

---

## §6 — VERDICT

## **CONFIRM-WITH-CONDITIONS**

Ratified **Reading A** is **sound**. Both voices reached this independently and blind, from decorrelated seats, and neither found a defect meeting the fork's own reopening criteria:

- **No defect in Reading A.** The §4 discriminator holds at HEAD: `:5834` genuinely forbids walking backward, so a shared file genuinely destroys per-tenant latest-record authority, and path segregation genuinely preserves it.
- **No defect in the injective-encoding contract term.** Stronger than a bare confirm — C3 verified the **normalization layer's** injectivity, a layer nobody had checked, and it holds; and C11 found the encoding discipline **already realized in-house as a zero-config constant**, which is the strongest available confirmation of a term the fork spent three review rounds deriving.
- **No defect in the two-gate sequencing.**
- **No cite fails to resolve at HEAD.** Two immaterial line-range drifts, both declared at `K-16(c)`.
- **The config-burden antecedent is genuinely absent** (P0) — path segregation costs the local operator **zero configuration**.

**What the conditions are, and are not.** They are **not** doubt about the reading. They are obligations the arc's own logic requires and the filing does not yet carry, in three clusters: **(a)** the quiesced-cutover term as written rests on a precondition no operator can verify (P1, P2), and a violated (3b) is **silent and executes** (P4) — so the safety weight must move from declaration to mechanism; **(b)** ratified-A **creates** a durable class nothing can enumerate (P3), which makes §5.3's own stated recourse non-actionable and (3a)'s cost bound unknowable; **(c)** the encoding must bind three distinct injectivity hazards, not the one the fork's §4 names.

**Explicitly NOT found:** any reason to revisit the reading, the abandon-by-default disposition, the closed five-member vocabulary, or the no-rider call.

---

## §7 — CONDITIONS (the spec leg's obligations)

Merged, unified, renumbered. **17 conditions — 15 LOAD-BEARING, 2 RECOMMENDED** (recount programmatic). Each is phrased so a spec-writer can apply it, and each traces to a probe or a named seam.

### Cluster A — the cutover (scope item 1)

| # | Condition | Weight |
|---|---|---|
| **K-1** | **No unverifiable precondition.** §14.14.8's migration text MUST NOT state directory quiescence as a *discharged* precondition. It MUST state the negative fact: the harness provides **no mechanism** by which an operator can verify that no writer holds the resolved pause-journal directory — the pidfile is keyed to `repository_root` while the journal resolves from `path_bindings`, so it is **not an authority** over that directory. Operator-declared quiescence is **never** a substitute for `K-2`/`K-3`. → P1, P2, SEAM 5 | **LOAD-BEARING** |
| **K-2** | **Legacy-source exclusion.** A (3b) adoption MUST hold, per journal, an exclusive `flock` of the same construction the append path takes (`journal_workflow_pause_store.py:414-429`, `PAUSE_JOURNAL_LOCK_SUFFIX`) on the **LEGACY source** journal's lock file — the inode a straggler appender contends on — continuously from before the source read until after the target publication commits. A **directory-tree scope lock is explicitly NOT sufficient and MUST NOT be specified**: it contends on a different inode and excludes zero appenders. → P5, SEAM 1 | **LOAD-BEARING** |
| **K-3** | **Read-back verification against the legacy source.** As its final act under the exclusion and before publishing, the adoption MUST re-read the legacy source and compare `record_count` and `latest_record_digest` (`:197-203`; already shipped, **zero new persistence**) against the copied values, refusing and leaving the target unpublished on any difference. The spec MUST state what this check does and does **NOT** do, in those words: it **DETECTS interference within the `[source read, read-back]` window** — covering the pre-PR-#1167 writer that takes no lock at all, the platform where the lock is a no-op, and filesystem-level interference — and thereby **NARROWS, but does NOT CLOSE**, the residual. **It MUST NOT be stated as covering, or making safe, the §5.3.2 mixed-version window.** The residual, named: a lockless straggler that appends to the legacy path *after* the read-back leaves the target holding an older record than the source, with every condition here satisfied. **What that residual rests on is §5.3.2(a)'s MANDATORY no-mixed-version cutover — which `K-1` states is unverifiable — and nothing else.** Note also that under the **(3a) default no adoption runs at all**, so `K-2`–`K-6` never execute and the mixed-version window rests on §5.3.2(a) alone; these conditions harden (3b), they do not substitute for the cutover. Stating otherwise would commit the exact error `K-1` names — a migration that "held every stated precondition" and corrupted anyway. → P7, SEAM 1, E2 F3 / E3 [P1] | **LOAD-BEARING** |
| **K-4** | **The no-replace commit IS the empty-target enforcement.** The round-8 empty-target precondition MUST be specified as discharged by the **write-once, crash-atomic, no-replace publication** already required by §5.3's fourth term on the §14.8.11 `:4809` model — *a write against an existing key is REFUSED TYPED, never overwritten* — and **NOT** by a separate pre-check. A pre-check without exclusion is a time-of-check/time-of-use race against an upgraded capture landing at the new key; the atomic commit closes it by construction. Any pre-check is **advisory only** and MUST be stated as such. **No second lock on the target is required or permitted** — it would be redundant with the atomic commit and would add a lock-ordering hazard. → SEAM 2 (orchestrator-adjudicated) | **LOAD-BEARING** |
| **K-5** | **Per-journal sequencing; idempotent and re-runnable.** Adoption MUST sequence strictly per journal (acquire → read → copy → verify → publish crash-atomically → release → advance), never holding journal *i*'s lock while taking journal *i+1*'s, so the instantaneous blocking footprint equals one append's and the cross-workflow blocking deliberately rejected at `:374-391` is not reintroduced. Each journal is therefore independently all-or-nothing and the operation as a whole is **directory-non-atomic**; it MUST therefore be **idempotent and re-runnable**, completing a **directory-level** partial migration on re-run. **The re-run's skip decision REQUIRES an explicit discriminator, and the spec MUST name it.** A no-replace commit yields one undifferentiated signal (*target exists*), and because Reading A leaves the **record shape unchanged**, an adopted record and an upgraded writer's fresh capture are structurally identical: treating every existing target as *done* would accept foreign or newer state, while refusing every existing target would break the promised recoverable retry. The only Reading-A-compatible discriminator is **content equality between the target and the exclusion-held legacy source the run would publish** — identical → already published, **skip**; different → **foreign, REFUSE** — with `K-4`'s write-once commit as the backstop for the race. **The round-9 restatement of term (2) is NOT authority for a *done* branch**: it governs the *form* of the empty-target test per reading (under Reading A the target is a new path, so "no tenant-stamped record" and "empty" coincide, and an already-adopted target is non-empty and would be refused). An earlier draft of this condition mis-cited it; recorded rather than silently corrected. **Scope note:** `K-4`'s crash-atomic publication already guarantees an **interrupted** adoption leaves *no* target, so the skip branch is needed only for **whole journals already done**, never for a partially-written one. Because the store carries no hash chain, a publication that dropped complete records would leave no structural trace (P4, as narrowed there), so **repeatability is the only available recovery**. → P4, P7, SEAM 1, E2 F1 / E3 [P1] | **LOAD-BEARING** |
| **K-6** | **Refuse where the primitive degrades.** Where the exclusion is a documented platform no-op (`:411-413`), adoption MUST **refuse by default** rather than proceed on a declaration. A read-back-only mode MAY be offered solely under an explicit operator flag whose weaker guarantee is stated in the refusal text; **silent degradation of the guard is prohibited**. Cost stated: such an operator loses (3b), not correctness — (3a) remains fully available. → P7 | **LOAD-BEARING** |
| **K-7** | **Name the silence.** The spec MUST state that a violated adoption produces a resume against **stale-but-internally-consistent** state which passes **every** shipped guard — snapshot-workflow match, step-index range, `snapshot_hash` self-validation, and the v1.107 staleness precondition (which fences a stale **read**, not a stale **copy**, and does not fire at all when the resume context was not composed against an accessor read). The store carries **no hash chain**, so no structural tamper-evidence and no post-hoc forensic path exist. `K-2`–`K-6` stand in place of a runtime detection that does not exist. → P4 | **LOAD-BEARING** |
| **K-8** | **The (3a) default is a decision, stated with its ground.** §14.14.8 MUST record the failure-mode asymmetry as the **stated reason** (3a) is the default: a violated (3a) cutover fails **refusing** (availability loss); a violated (3b) adoption fails **silently and executes** (correctness loss). Combined with the non-enumerability of the abandoned set, this — not a general fail-closed preference — is why (3a) is the default and (3b) an explicit, bounded, mechanically-verified exception. An unwritten default rationale is a default a later arc flips on convenience. → P3, P4 | **LOAD-BEARING** |

### Cluster B — the legacy disposition and the operator surface (scope item 2)

| # | Condition | Weight |
|---|---|---|
| **K-9** | **Tenant-scope §30's `absent` — meaning AND repair text.** The `absent` row (`:3318`) MUST be amended to a tenant-composite reading: *no record for this tenant-composite key*, returned for **three** states — a workflow that never journaled, a **wrong-tenant** lookup, and an **abandoned legacy** record. The shipped repair (*"this workflow never journaled a pause — check `durable=True`"*) is **actively wrong** for the latter two and sends the operator away from the cause. **Definition amendment; no new cause member.** *(= the fork's own item 4-bis, reached independently by both voices.)* → P4 | **LOAD-BEARING** |
| **K-10** | **§5.3.1 = (i) + (iii), and (iii) is a PRECONDITION of ratifying (3a).** Not an optional companion: ratified-A converts the legacy journal into a durable class **no code path can reach or list**, while `:5834` forbids removing its records — so without (iii), (3a) is not *"abandon a bounded set"* but *"abandon a set the operator cannot enumerate, then misdiagnose it as `absent` afterwards"*, and §5.3's own stated recourse (*"drain pauses before upgrading"*) is **not executable**. (iii) MUST: (a) **ENUMERATE** the directory, never probe a single derived path — a single-path probe on an admin binary reintroduces the withdrawn (ii) oracle; (b) be usable **BEFORE** an upgrade as well as after; (c) report existence plus `record_count` and `latest_record_digest`, so the operator learns *how much would be lost*, not merely *that something exists*; (d) **NEVER** parse, return, or resume a snapshot; (e) engage only when a journal directory exists, so a deployment with no journal sees byte-unchanged output and zero added burden (the §13.5 engagement-predicate shape). The listing prohibition is scoped to the **tenant-facing runtime read path**, which stays single-authority, resolves exactly one key, and **MUST NOT** gain enumeration. **Admin-tier surfaces MAY enumerate** — (iii), any (3b) adoption tool, and any disposal action each require it, since the journals they operate on are opaque `sha256`-named files no caller can otherwise discover, and `K-5`'s per-journal sequencing is unimplementable without it. *(An earlier draft made (iii) the ONLY permitted lister, contradicting `K-5` and `K-12`; corrected at E3 [P2] rather than silently.)* → P3, P7, SEAM 4, E3 [P2] | **LOAD-BEARING** |
| **K-11** | **Landing: extend `harness-inspect`; disposal MUST NOT live there.** (iii) MUST land as an extension of the existing `harness-inspect` surface (spec `:1199` §13.5 precedent; `--browse` at `admin/inspect.py:115-122`), not a new binary, and MUST satisfy §13's read-only invariants **verbatim** (`:3693`; `admin/inspect.py:22-25`, enforced by a chmod-readonly fixture). Any **disposal** action is a destructive write and is therefore **foreclosed from that surface by the invariant**; if specified it is a **separate** `python -m` admin action on the `migrate-audit-sidecar` precedent. → P7, SEAM 4 | **LOAD-BEARING** |
| **K-12** | **§13.4 CLI-inventory rows are owed, in this spec leg.** The operator-facing CLI inventory is spec-committed (`:1184-1193`); the `harness migrate-audit-sidecar` row (`:1191`) is the standing precedent that an admin migration/inspection surface is a **spec-leg obligation, not impl discretion**. (iii), any (3b) adoption tool, and any disposal action each owe a row; implementation MAY remain `python -m`. **This is not on the fork's §9 leg-3 list and must be added.** → P7 | **LOAD-BEARING** |
| **K-13** | **Orphan statement — both halves.** §14.14.8 MUST state: *Journals orphaned at the retired key are retained indefinitely and are never reclaimed by the harness — no pruner is specified and none is owed. The append-only / never-truncated invariant governs records of a **live** journal and does not extend to a retired-key orphan; an operator may remove one, and the harness will never do so on its own.* Both halves are required: the permanence half so an operator need not infer it, the distinction half so a later arc is not blocked by ambiguity — the `:5836`-class error this section itself warns about, in the other direction. A disposal action is **OPTIONAL**; if specified it MUST be **dry-run by default** and MUST refuse while (3b) adoption remains possible absent an explicit operator acknowledgment that recoverable state is being discarded. **A retention policy — default, tunable, sweep trigger — is a FOLLOW-ON ARC and is explicitly NOT owed here.** → P3, SEAM 4 | **LOAD-BEARING** |

### Cluster C — the encoding (scope item 3)

| # | Condition | Weight |
|---|---|---|
| **K-14** | **The encoding is a CONSTANT of the implementation — no configuration surface.** A configurable key derivation is a second authority over one durable address space: flipping it re-addresses every `(tenant, workflow_id)`, orphaning every journal **silently, with no migration and no diagnostic** — converting this arc's one-time, dated, documented upgrade event into a repeatable, undated, operator-triggerable one. `RuntimeConfig` carries *location* overrides and **no derivation override anywhere**; the two are categorically different. Burden runs the same way: a constant costs the operator nothing; a knob costs a field, a default, a validator, a doc paragraph telling the operator never to touch it, and a permanent footgun. A future encoding change is a **keying change** and MUST take this arc's fork path. *(Noted honestly: this leaves the encoding unversioned. That is correct pressure — it keeps the cost visible at a spec leg. Insurance against a NEXT transition belongs at §5.3.2(b)'s record-version marker, explicitly not a config knob.)* → P7 | **LOAD-BEARING** |
| **K-15** | **Total injective encoding + the Runtime-local normalization delegate + all THREE hazards.** The tenant component MUST be obtained by delegating to the **Runtime-local** `normalize_tenant_scope` (`protected_result_store.py:183-199`); it MUST NOT be delegated to `harness_od.sidecar_tag` / `audit_writer._tenant_tag`, whose `None → "_single"` disposition is **incompatible** with the Runtime-local authority's (P6) and would bind this store to a **reserved literal** it has no need to reserve; and it MUST NOT be a third re-derivation. *(Stated precisely, because an earlier draft over-claimed and E2 F4 caught it: the sibling's recorded defect at `protected_result_store.py:250-259` concerned a sentinel the `RuntimeConfig` validator does **NOT** reserve — `_untenanted` — whereas `"_single"` **is** validator-reserved (`types.py:2030-2048`) and OD refuses it as a real tenant, so OD's scheme is **not an instance** of that defect. The objection stands as a **category** argument — a disjoint-by-construction scheme needs no reserved literal at all (`:257-259`) — not as an instance claim. The condition's conclusion is unaffected: it rests on P6's incompatible-disposition finding and on C3's join-key withdrawal, both untouched.)* The encoding MUST be **TOTAL and injective over `(str \| None) × str`**, treating the untenanted branch as a **distinct value** — not an absent field, not a reserved literal — realized on an in-house discipline (the length-prefixed canonical-segment shape is injective across arity and handles the untenanted branch by segment count alone) rather than a freshly minted equivalent: a menu of "some injective encoding" lets two conformant implementations resolve the same tuple to **different paths with no migration between them**. The spec MUST close **all three** recorded hazards, not only the one §4 names: **(a)** `None`-vs-real **branch collision**; **(b)** a tenant containing the composition **delimiter**; **(c)** **field-boundary shift** between tenant and `workflow_id` — §4 names only (c), and *a spec leg that closes (c) alone still ships a collidable key*. The spec MUST NOT state that this store's untenanted scope normalizes to `_single`. → P6, SEAM 3 | **LOAD-BEARING** |

### Cluster D — corrections and postures

| # | Condition | Weight |
|---|---|---|
| **K-16** | **Fold-in corrections.** (a) Fork §7's *"whose scope normalizes to the `_single` sentinel"* is **FALSE at HEAD** and MUST be corrected at the spec leg — the **conclusion stands** (the untenanted path changes under any total encoding), only the mechanism description is wrong. (b) Add `harness-shutdown`'s stale drain self-description as a **FIFTH** stale-as-described fold-in beside the four the fork already carries (`:3313`, `:3319`, `:27`, `:5824`): `admin/shutdown_cli.py:21-28`, `--help` `:97-99`, and the **operator-facing runtime message** `:252-254` all say the workflow-loop drain is STRUCK and `--wait` will time out, while `drain.py:5-17` records C-RT-11 FULL-LAND at 2026-05-20 with `[[fork-u-rt-44-workflow-loop-drain]]` CLOSED. This is not merely adjacent — it is the **second leg** of why *"drain pauses before upgrading"* is not actionable. *(Scoped precisely: the handler at `drain.py:124-138` still only sets `drained_flag` and does not call `shutdown()`, so the docstring's claim about `shutdown()` is NOT stale; what is stale is the STRUCK/fork-open framing. The refresh must correct the stale half without over-claiming the other.)* (c) Cite hygiene: the fork carries `_parse_snapshot_attributed` at `:594-611`; at HEAD the body runs to `:615` with an additional embedded-snapshot check at `:602-610`. Immaterial to the analysis. → P6, and orchestrator re-grounding | **RECOMMENDED** |
| **K-17** | **No HITL gate on the upgrade or the adoption.** The operator is the actor; both emit an **audit record**, not an approval prompt. Any confirmation on a destructive disposal action is an **in-command confirmation**, not a gate. Gating an operator-invoked migration on an operator approval is empty ritual. | **RECOMMENDED** |

---

## §8 — Gate-2 votes (the two rows the dyadic was convened to price)

Per the fork's §7 sequencing, gate 2 is **two rows under Reading A**. The council's input:

| Gate-2 row | Council vote | Ground |
|---|---|---|
| **(3a)-abandon vs (3b)-adopt as the DEFAULT** | **CONFIRM (3a) as the default**, unanimous | Two independent grounds: the **detectability asymmetry** — a violated (3a) fails refusing, a violated (3b) fails **silently and executes** (P4) — and the **non-enumerability** of the abandoned set (P3). (3b) remains available as an explicit, bounded exception **only under `K-2`–`K-6`**. C11 argued against (3b)-as-default *against its own axis's instinct*, having been explicitly briefed by §7 to consider proposing it. |
| **§5.3.1 (i) alone vs (i)+(iii)** | **(i)+(iii)**, unanimous — and **(iii) is a PRECONDITION of (3a) being ratifiable as stated**, not an optional companion | Converged from **decorrelated reasons** (P3): C11's — §5.3's own recourse sentence is not executable at HEAD; C3's — the arc **creates** an unenumerable durable class. Each voice adopted the other's reason as primary. Scoped at `K-10`/`K-11`. |

**On both rows the council's input SUPPORTS a confirm** — it found no reason to override either and strengthened the ground for both. **The answer remains the operator's.** Gate 2 is *"a NARROW second ask confirming **or overriding** those two sub-decisions"* (fork `:635-636`); this record supplies input to that ask and does not settle it, and **leg 3 MUST NOT open before gate 2 answers** (fork `:693-695`). Whichever way gate 2 lands, §7's conditions are the substance the spec leg carries.

---

## §9 — Spec-leg handoff

**Additive to the fork's §9 leg-3 list, which stands.** What this convening adds or changes:

1. **`K-1`–`K-8` rewrite the fork's §5.3 term (1) and §5.3.2(a).** The quiesced-cutover term as filed rests on an unverifiable precondition; the replacement is the negative fact + a mechanically-discharged exclusion + read-back verification + the no-replace commit as the empty-target authority. §5.3.2(a) remains **MANDATORY** and is unchanged in force — `K-3` explains *why* it is what makes the mixed-version window safe.
2. **`K-4` supersedes the fork's round-8 term (2) as a separate pre-check** — it is discharged by the round-11 crash-atomic publication term, not beside it. The fork's own three-part/four-part term list should be restated as: exclusion (`K-2`), read-back (`K-3`), atomic no-replace publication which *is* the empty-target enforcement (`K-4`), idempotent re-run (`K-5`).
3. **`K-9` = the fork's item 4-bis**, independently confirmed from the code side by both voices. Lands in the same §30 row as the folded-in `B-102` amendment (fork §9 item 5).
4. **`K-10`–`K-13` are the §5.3.1 resolution**, and `K-12` adds a **§13.4 CLI-inventory obligation the fork's §9 does not list**.
5. **`K-15` extends the fork's §4 injective-encoding term from one hazard to three**, and corrects its normalization mechanism (`K-16(a)`).
6. **`K-16(b)` adds a FIFTH stale-as-described fold-in** to the fork's four.
7. **Unchanged and NOT reopened:** Reading A; the closed five-member vocabulary (**no new cause member is owed by any condition here** — `K-9` is a definition amendment); the no-rider call (§5.4); CXA classification (expected classification-only, to be determined not assumed); the plan delta (a new `U-RT-*`); clearance markers + adversarial review per `CLAUDE.md` §4.5/§10.9.

**Leg-2 obligations still outstanding at this HEAD** (stated because this record is one of leg 2's three steps, and none of them rides this doc-only PR): the fork carries **no `## §11 RATIFICATION` section** (verified — the string appears only in §9's instruction at `:685`); the `B-97` register row is still `status: registered_finding` / `pr: '#pending'` (`:2888-2892`) and owes the flip to `design_substrate_gated`; and the blocking-`flock`-on-the-event-loop follow-up still owes its **own `B-*` row** before `B-97` closes. **Gate 2 must answer before leg 3 opens** (fork §9, round-8 [P1]).

---

## §10 — Findings routed OUT (registered, not absorbed)

| Finding | Disposition |
|---|---|
| **`harness-shutdown`'s stale drain self-description**, including in operator-facing runtime output | NOT this arc's defect, but this arc's cutover term is the first contract to depend on that tool. Folded in as `K-16(b)` rather than registered separately, because it is the second leg of the non-actionable-recourse problem `K-10` exists to repair. |
| **`admin/__init__.py:3-11` describes the admin surface as *"Track A admin surface (both landed)"* naming 3 modules; there are 8** | Cosmetic index staleness. Refresh in whatever leg lands `K-10`/`K-11`; not owed independently. |
| **A retention POLICY for the orphan class** (default, tunable, sweep trigger, `:5834` interaction) | **Explicitly routed OUT** per SEAM 4. `K-13` names the class and states its permanence; a lifecycle subsystem is a follow-on arc and MUST NOT be grafted onto a keying change. |
| **The pause journal carries no hash chain** (no `previous_hash`, no splice detection) | Observed, **not** raised as a defect: this is not the chained ledger and C-IS-05's construction obligation does not attach. Its consequence is absorbed at `K-7` (name the silence) and `K-5` (repeatability as the only recovery). Register only if a future arc proposes tamper-evidence for this store. |

---

## §11 — Review passes

Both reviewers ran against this record **before** it was committed. They were wired **decorrelated** per `CLAUDE.md` §13.1: the adversarial pass is in-family and read the record plus the fork; Codex is out-of-family, got no council conclusions and no adversarial findings, and read only the artifact. **Where they converged, confidence rises; where Codex alone caught something, that is the decorrelated catch the in-family reviewers structurally miss — three of the seven absorbed findings are of that kind.**

### 11.1 E2 — in-family adversarial (`harness-adversarial-reviewer`, genuine dedicated-agent invocation)

**Verdict: CLEAR-WITH-FOLD.** No §2.7.6 Class-1 halt fork; no X-AL-3 violation; no finding against the ratified reading, the injective-encoding term, or the two-gate sequencing. **7 findings — 1 [P1], 3 [P2], 3 [P3]; all 7 ACCEPTED, none disputed.**

| # | Sev | Finding | Disposition |
|---|---|---|---|
| F1 | **[P1]** | `K-5`'s *"already-adopted target as done"* **mis-attributed to round 9** (which restates term (2)'s *form* per reading, and under Reading A makes a non-empty target **REFUSED**), and presupposes a mine-vs-foreign discriminator Reading A cannot supply — the record shape is unchanged, so an adopted record and a fresh capture are structurally identical, and `K-5`'s own step list contains **no target-inspection site** | **ACCEPTED.** `K-5` rewritten: attribution dropped and the mis-cite recorded in-body; the content-equality discriminator named explicitly; the skip branch scoped to whole-journals-already-done, since `K-4` already guarantees an interrupted adoption leaves no target |
| F2 | [P2] | §8 **pre-empted the operator's gate-2 answer** (*"the operator's gate-2 answer is therefore a confirm"*) where fork `:635-636` reserves gate 2 as *"confirming **or overriding**"* | **ACCEPTED.** §8 restated as the council's **input**, with the override branch and the leg-3 bar preserved |
| F3 | [P2] | `K-3` **over-claimed** — a before-publish read-back *narrows* an interference window, it does not *close* one; the prescribed spec text said *"covers"* / *"makes safe"*. Falsifying interleaving supplied with all of `K-1`…`K-6` satisfied. Self-inconsistent with `K-1`'s own discipline | **ACCEPTED.** `K-3` downgraded to *detects / narrows*, with the residual named and routed back to §5.3.2(a) |
| F4 | [P2] | `K-15` **mischaracterized the sibling's recorded defect** — that defect concerned `_untenanted`, a sentinel the validator does NOT reserve; `"_single"` **is** validator-reserved, so OD's scheme is not an instance of it | **ACCEPTED.** The instance-claim struck; the objection restated as a **category** argument. `K-15`'s conclusion is untouched — it rests on P6 and on C3's join-key withdrawal |
| F5 | [P3] | §12 seam tally **3/1/1** vs §4's actual **2/1/2** | **ACCEPTED.** Corrected |
| F6 | [P3] | `admin/migrate_audit_sidecar.py:8-10` → actual span `:6-8`; and §6's *"one drift"* is **two** | **ACCEPTED.** Both corrected |
| F7 | [P3] | §0.4 *"4 reciprocal corrections"* vs §5 *"five reciprocal concessions"* — one stage, two numbers | **ACCEPTED.** The fragile numeral **removed from both**, since the §5 table enumerates the movements |

**Recount:** 15 claims recounted programmatically — **13 MATCH, 2 DRIFT** (F5, F7). **Cite sweep:** ≈75 targets re-resolved at HEAD, **1 failure** (F6) plus one verbatim-casing slip, both corrected. **Checklist:** all 9 items engaged; findings raised on item 3 (forward-looking cite phantom → F6) and item 6 (prose-vs-body drift → F1); item 9 (halt-route-split-AC) assessed *"exemplary"* for `K-13`'s and `K-11`'s mechanism-based splits.

**What it attacked and could not break** — recorded because a pass with no stated attack surface is not a pass. `K-4`'s central adjudication survived a direct attempt on the interleaving C3 feared (*"under a genuine atomic no-replace commit the publish fails; newer state is never overwritten"*), the reverse ordering, and a lock-ordering starvation attempt — *"`K-4`'s central claim holds. What broke was only its composition with `K-5`."* `K-2`'s exclusion target survived the between-operations straggler cases, with the sole escapee being the lockless writer that `K-3` is assigned. **P4 was re-traced end-to-end** through `api.py:1303-1366` rather than trusted, and **holds, including its second leg**. Scope discipline came back clean — the record was found to **harden** the withdrawn (ii) rather than erode it. On smoothing, the council's cardinal failure mode: *"This is the opposite of smoothing"*, citing the record's own disclosure of SEAM 2's parallel-turn exposure and §3's record of C11 arguing against its own axis's instinct.

### 11.2 E3 — out-of-family (`just codex-review-uncommitted`, GPT-5.6, ChatGPT subscription, $0, codex-cli 0.144.4)

**6 findings — 3 [P1], 3 [P2]; all 6 dispositioned, 5 ACCEPTED, 1 ACCEPTED-AS-NARROWED.** X-AL-1 note: Codex is H_E dev tooling, not H_T's OpenAI provider.

| # | Sev | Finding | Disposition |
|---|---|---|---|
| 1 | **[P1]** | *"Retain a real barrier against legacy writers"* — under the **(3a) default no adoption runs at all**, so `K-2`–`K-5` never execute; and under (3b) a pre-#1167 writer can append after `K-3`'s final read. These conditions **cannot replace** §5.3.2(a) | **ACCEPTED — CONVERGENT with E2 F3.** `K-3` now states the non-closure explicitly and re-affirms §5.3.2(a) as MANDATORY and un-substitutable, including Codex's (3a) observation, which E2 did not make |
| 2 | **[P1]** | *"Define how retries recognize an adopted target"* — no-replace establishes only *target exists*; with the record shape unchanged and no receipt, the tool cannot distinguish its own prior publication from an upgraded writer's capture | **ACCEPTED — CONVERGENT with E2 F1**, reached independently and from a different direction (E2 from the mis-cite, Codex from the retry semantics). Resolved by the same `K-5` rewrite |
| 3 | **[P1]** | *"Complete the required review evidence before filing"* — the stage table and footer attest E2/E3/E4 ran while all three sections were placeholders | **ACCEPTED — Codex-only, and correct.** This §11 is the fix. The finding is itself evidence the pass was genuine: it could only be raised by a reviewer reading the artifact as filed |
| 4 | [P2] | *"Permit the adoption tool to discover migration inputs"* — `K-11` made `harness-inspect` the **only** permitted lister, but `K-5` requires per-journal iteration and `K-12` requires an adoption tool over opaque `sha256`-named files | **ACCEPTED — Codex-only, and a genuine internal contradiction both voices and E2 missed.** `K-11`'s prohibition rescoped to the tenant-facing runtime read path; admin-tier surfaces may enumerate |
| 5 | [P2] | *"Correct the torn-tail detection claim"* — a torn trailing append **is** detectable (`corrupt-latest`, plus the self-heal preserving the fragment as a non-latest line) | **ACCEPTED-AS-NARROWED — Codex-only, verified by the orchestrator at `journal_workflow_pause_store.py:475-481` before absorption.** The claim is narrowed to **dropped complete records**; the no-hash-chain consequence survives in that narrower and correct form |
| 6 | [P2] | *"Correct the seam-resolution counts"* — 2/1/2, not 3/1/1 | **ACCEPTED — CONVERGENT with E2 F5** |

### 11.3 E4 — residual sweep + re-verify at HEAD

- **Convergence.** Three findings were reached by **both** reviewers independently (E2 F1 ≡ E3 #2; E2 F3 ≡ E3 #1; E2 F5 ≡ E3 #6). Per `CLAUDE.md` §13.1 that agreement raises confidence; and the three **Codex-only** catches (#3, #4, #5) are the decorrelated class the in-family reviewers structurally miss. **No reviewer disagreement was suppressed** — E3 #5 is the one case where a reviewer **rebutted the record on a fact**, and it was verified at source and accepted rather than argued.
- **No finding met the fork's reopening criteria** (`:1017-1018`). Every one of the 13 absorbed findings landed on a **condition's wording, a count, or a cite** — none on Reading A, the injective-encoding term, the two-gate sequencing, or an unresolvable cite. **The verdict is unchanged at CONFIRM-WITH-CONDITIONS**, and the condition *set* is unchanged at 17 — `K-3`, `K-5`, `K-11`, `K-15` were **rewritten**, none added and none dropped.
- **Re-verified at HEAD after the fixes:** 17 conditions `K-1`…`K-17` contiguous; 15 LOAD-BEARING / 2 RECOMMENDED; 5 seam headings at 2 probe-resolved / 1 adjudicated / 2 converged; 8 probes P0–P7; 12 reconciliation rows — all programmatic.
- **Self-referential-loop check** (`[[self-referential-review-loop-discriminator]]`): the finding stream moved from **substance** (F1/F3/#1/#2/#4 — real defects in condition wording) to **book-keeping** (F5/F6/F7/#6) to **narration**. Per the discriminator, **stop here.** No round 2 is owed: the decision surface — the verdict, the 17-condition set, the gate-2 votes — was untouched by every finding.

---

## §12 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/council-b97a-tenant-path-segregation-2026-07-31.md` |
| Convened | 2026-07-31, HEAD `6e9473e6` |
| Stage sequence | pre-convene probes → E1·A1 (blind) → E1·B (cross-read) → orchestrator adjudication → E2 → E3 → E4 |
| Voices | C3 (state/memory/persistence), C11 (operator-loop/local-deployment) — dyadic, both primary, both genuine dedicated-agent invocations |
| Verdict | **CONFIRM-WITH-CONDITIONS** (unanimous, independently reached) |
| Conditions | 17 (`K-1`…`K-17`) — 15 LOAD-BEARING, 2 RECOMMENDED |
| Seams | 5 — 2 probe-resolved, 1 orchestrator-adjudicated, 2 converged; **0 unresolved** |
| Posture | Design-phase. `design-substrate/**` READ ONLY; this record is the only file written |
| Consumes | `.harness/class_2_fork_b97a_pause_journal_tenant_binding.md`; `Spec_Harness_Runtime_v1.md` v1.107 |
| Feeds | Gate 2 (`AskUserQuestion`, two rows) → the `B-97`(a) spec leg |
| Precedent | `.harness/council-b69-pause-state-accessor-2026-07-30.md` (same store, adjacent arc) |
