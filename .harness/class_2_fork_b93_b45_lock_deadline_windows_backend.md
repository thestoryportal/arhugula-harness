# Class 2 Fork — B-93 + B-45 (combined): the same-host lock substrate has neither a liveness deadline nor a Windows serialization backend, and the second gap now withholds a correctness guarantee

**Status: FILED 2026-08-05, awaiting operator ratification.** Doc-only filing per the workspace
codex-context-guard rule (fork FILINGS ship doc-only FIRST; no `design-substrate/**` edit rides this
PR). Chain mirrors `B-88`'s, `B-107`'s, `B-98`'s and `B-97`(a)'s: **filing (this PR) → operator
ratification → build leg(s).** Unlike those four, this filing concludes that **no spec leg is owed
under any reading** — see §3(vii) and §9.

**Register rows.** `B-45` at `.harness/forward-register.yaml:816`–`:879` (`status:
registered_finding`, no `pr:` field) + prose at `.harness/post-phase-8-forward-register.md` `### B-45`
(`:548`–`:563`). `B-93` at `.harness/forward-register.yaml:2924`–`:2930` + prose at `### B-93`
(`:976`–`:987`). Both rows stay `registered_finding` at this filing; status change and `pr:` pointers
ride the ratification leg. **No snapshot/digest change** (the digest is over `id:status` pairs and
neither status moves).

**Why the two rows are filed together.** Each row already names the other as its natural co-rider
(`B-93` prose `:983`, `B-45` prose `:562`), on the ground that both traverse the *identical* primitive
set — nine blocking `flock` acquisition sites across four modules — so doing them together costs one
traversal instead of two. `B-93`'s council clause makes the pairing load-bearing rather than merely
economical: it declares the row *"Council-eligible only if taken **with** B-45 and the Windows
tradeoff makes the deadline semantics non-obvious"* (`forward-register.yaml:2929`). **This filing is
the condition's antecedent**, so the consequent must be adjudicated here rather than deferred — §7
does that.

**Grounding HEAD.** `966bc658`. Every file:line, count and quotation below was re-resolved by direct
read at **this** HEAD — not from either register row, not from the 2026-08-05 sweep that re-stamped
them, and not from recall. **Three claims carried on the rows are falsified or materially weakened at
this HEAD, and one library fact neither row has ever considered changes the shape of the fix.** All
four are recorded at §3 and §10 rather than silently normalized, and the corrected statements — not
the rows' — are used throughout.

**What this filing does NOT do.** It does not re-litigate B-40 (the lock's existence), B-46 (the
first-write TOCTOU), B-97(b) (pause-journal append serialization), or B-73 (the protected-result-store
lock). Those are CLOSED and are treated as settled substrate. It does not re-open the ABBA-avoidance
handoff, which is a preserved invariant under every reading here. It decides **two coupled questions**:
*does the same-host lock substrate get a liveness deadline, and does it get a real Windows backend?*

---

## §1 The question, and what carries it

Two registered rows describe two properties the same nine `fcntl.flock` acquisition sites lack.

**B-93 — no liveness bound.** Every one of the nine blocking acquisitions is a bare
`fcntl.flock(fd, LOCK_EX)` or `LOCK_SH` with no timeout. The exposure the row registers is not the
lock itself but `CanonicalMemoryStore.write_record_guarded` (`harness-is/src/harness_is/memory_store.py:298`),
which holds the root-wide `cross_process_scope_lock` **across a caller-supplied precondition callable**
(`:302`, hold at `:341`). The store's own docstring says it *"knows nothing about what the precondition
tests"* (`:306`–`:307`) — which is exactly what leaves the next precondition author unaware they are
holding a host-wide exclusive lock for the duration of whatever they wrote.

**B-45 — no Windows backend.** Six lock surfaces open with a bare `yield` / `return` on Windows. A
seventh carrier does not even have a platform flag: `reconciler_pause_resume_substrate.py` imports
`fcntl` unconditionally at `:106`, so on Windows that module is an import-time
`ModuleNotFoundError`, not a degraded lock.

**Why these are ONE fork and not two.** `[HIGH]` The deadline shape B-93's close-out step (1)
prescribes — `LOCK_NB` + bounded retry — is the *same code motion* that a Windows backend needs, because
the Windows primitive that can serve here is also a non-blocking probe (§3(iv)). Nine sites is one
traversal; splitting it produces two passes over the same nine call sites with two different retry
helpers, which is the inconsistent-surface outcome B-93's own close-out warns against
(`forward-register.yaml:2928`, *"putting one on a single site would itself be the inconsistent surface"*).

**Why it is Class 2 and not Class 1.** `[HIGH]` No design-substrate artifact is defective. C-IS-09
§9.4 *defers* the serialization mechanism to implementation discretion (§3(vii)), and the IS spec
contains **zero** occurrences of `timeout`, `deadline`, `platform`, or `cross-process`. There is no
contract to repair — there is a choice between substantive alternatives with different costs and
different reversibility, which is the Class 2 discriminator at root `CLAUDE.md` §4.3. The same
classification `B-88`, `B-98`, `B-104` and `B-107` carry.

**The harm, stated precisely and against interest.** `[HIGH]`

- **B-93's harm is entirely prospective.** `write_record_guarded` has **exactly ONE production caller
  at this HEAD** — `_provenance_unchanged` (`harness-runtime/src/harness_runtime/memory_promotion.py:907`,
  invoked at `:911`), bounded at one `read_record` per cited source memory ref. No network, no operator
  wait, no unbounded loop. **The row's own trigger — "the second precondition" — has not fired.** Nothing
  stalls today.
- **B-45's harm is NOT prospective, but it is unreachable.** On Windows the compare-and-commit binding
  degrades silently to in-process-only, and a promotion can activate against superseded provenance
  (§3(iii)). That is a wrong durable write, not a missing optimization. It is unreachable because
  nobody runs this on Windows — but "nobody runs it" is an *operational* fact, and §3(i) shows the
  *design* fact points the other way.

---

## §2 Current behaviour at HEAD `966bc658`

| Surface | State at HEAD |
|---|---|
| **Blocking acquisition sites** | **NINE**, none with a timeout. `cross_process_ledger_lock.py` (six): `_DirLock.acquire` `:133` (`LOCK_EX`), `_acquire_legacy_sidecar_for_writer` `:274` (`LOCK_EX`), `_acquire_legacy_sidecar_if_present` `:330` (`LOCK_EX`/`LOCK_SH`), `cross_process_write_lock` `:406` (`LOCK_EX`), `cross_process_replace_lock` `:507` (`LOCK_EX`), `cross_process_read_lock` `:605` (**`LOCK_SH`**). `harness-runtime` (three): `reconciler_pause_resume_substrate.py:294`, `protected_result_store.py:371`, `journal_workflow_pause_store.py:489` (all `LOCK_EX`) |
| **Entry surfaces** | **SEVEN**: `cross_process_scope_lock` (`cross_process_ledger_lock.py:186`), `cross_process_write_lock` (`:347`), `cross_process_replace_lock` (`:466`), `cross_process_read_lock` (`:550`), `_workflow_lock` (`reconciler_pause_resume_substrate.py:271`), `_cross_process_lock` (`protected_result_store.py:340`), `cross_process_journal_lock` (`journal_workflow_pause_store.py:418`) |
| **Non-blocking probes (NOT coverage)** | **THREE**: `:402`, `:498`, `:599`. Each is a contention *probe*; on `BlockingIOError` each arm **releases the directory lock first** and only then blocks — `:404`→`:406`, `:505`→`:507`, `:603`→`:605`. That release-before-blocking handoff is the ABBA-avoidance invariant, documented in code at `:394`–`:399`, `:500`–`:504`, `:601`–`:602` |
| **Timeout/deadline convention** | **ZERO** in all four carrier modules. One hit repo-wide across them is the word "timeout" inside a prose docstring (`reconciler_pause_resume_substrate.py:80`). No `timeout=` parameter, no deadline computation, no `TimeoutError` raised or caught |
| **Windows no-op LOCK surfaces** | **SIX**: `cross_process_ledger_lock.py:205` (scope), `:358` (write), `:478` (replace), `:560` (read); `protected_result_store.py:363`; `journal_workflow_pause_store.py:477`. Each is `if _IS_WINDOWS: yield; return` |
| **Windows flag declarations** | **THREE**: `cross_process_ledger_lock.py:90`, `protected_result_store.py:48`, `journal_workflow_pause_store.py:104`. **`reconciler_pause_resume_substrate.py` has NO flag** — unconditional `import fcntl` at `:106` |
| **Non-lock `_IS_WINDOWS` uses** | **TWO**, and they are *not* carve-outs: `cross_process_ledger_lock.py:239` and `:297` are `if not _IS_WINDOWS:` guards that add `O_NOFOLLOW` to an `os.open` flag set. A future implementer must not count them as no-op surfaces (§10, item 4) |
| **Windows primitive in tree** | **ZERO** `msvcrt` references in any `.py` file repo-wide. The only `msvcrt` occurrences anywhere are the register's own prose (`forward-register.yaml` ×7, `post-phase-8-forward-register.md` ×8) |
| **The one predicate over the carve-out** | `journal_exclusion_is_degraded()` (`journal_workflow_pause_store.py:402`, `return _IS_WINDOWS` at `:414`), consulted to **refuse by default** at `admin/pause_journal_adoption.py:412`. The only place the codebase *acts* on the carve-out |
| **Guarded-write production callers** | **ONE**: `memory_promotion.py:911`. Test callers: `test_memory_store.py:523`/`:539`/`:564`/`:618`, `test_memory_store_cross_process_guard.py:168`, plus three delegating doubles in `test_u_mem_27_activation_boundary.py` (`:348`, `:397`, `:638`). None supplies an unbounded precondition |
| **Real-second-OS-process contention witnesses** | **TEN**, enumerated at §3(vi) |
| **CI platform coverage** | `ubuntu-latest` only — the sole `runs-on:` value across `.github/workflows/` (12 occurrences); `grep -rn -i "windows" .github/` returns **ZERO hits** |
| **Spec constraint on the mechanism** | **NONE.** C-IS-09 §9.4 defers it (`Spec_Information_Substrate_v1.md:900`); C-IS-07 §7.4 defers it again (`:756`). Across the whole IS spec: `timeout` **0**, `deadline` **0**, `platform` **0**, `cross-process` **0** |

---

## §3 Seven grounding findings that shape the readings

### (i) **WINDOWS IS A COMMITTED HOST-OS SURFACE.** Both rows' "no active Windows target" framing is a claim about operations, and it has been silently doing the work of a claim about the design substrate `[HIGH]`

Both rows lean on the same dismissal. `B-45` close-out: *"low urgency until Windows becomes an active
target, not blocking"* (`forward-register.yaml:857`, prose `:551`). `B-45` item (e): *"Still **not
blocking** — no Windows CI, no active Windows target"* (prose `:558`).

**The design substrate says otherwise, at two byte-exact cites in Accepted artifacts:**

> `design-substrate/Target_Stack_Commitment_v1.md:42` — *"C-STK-10 | **Cross-platform host-OS support
> at design-time** — macOS, Linux, Windows. Each host-OS surfaces a distinct process-tier sandbox
> mechanism (per C-STK-04) and a distinct keychain primitive (per C-STK-05). … Stack must support all
> three host-OS targets without per-OS port forking. [HIGH]"*

> `design-substrate/ADR-F4.md:21` — *"commit **process-tier tech now** (Seatbelt on macOS,
> bubblewrap+socat on Linux/WSL, language-level + filesystem-ACL on Windows-native …)"*, with the
> caveat at `:48`: *"the Windows-native case is structurally weaker than the other two and operator
> awareness is required if Windows-native is the design-time host."*

**And the workspace already knew this** — the sibling row states it verbatim.
`post-phase-8-forward-register.md:536` (the `B-40` CLOSED block, the very arc that created the
carve-out) reads: *"the unconditional top-level `import fcntl` broke `import harness_is` on Windows …
**C-STK-10 commits to macOS/Linux/Windows host-OS support "without per-OS port forking"**; fixed by
gating the import behind `sys.platform == "win32"` and degrading the lock context managers to a no-op
on Windows."* The dismissal that then propagated onto `B-45` dropped the C-STK-10 clause and kept only
the operational half.

**Stated honestly and against my own recommendation.** `[HIGH]` C-STK-10 is a constraint on the
*stack decision* (Python was chosen partly because it ports to all three), not a claim that H_T runs
on Windows today. Windows is **not** a deployment tier — the three committed tiers at `ADR-D2.md:96`,
`:97`, `:98` are `local-development` / `self-hosted-server` / `managed-cloud`, and tier ≠ OS. And the
commitment has **no enforcement anywhere**: zero Windows CI (§2), zero `Operating System` classifiers
and zero `sys_platform` markers in any harness `pyproject.toml` (only `requires-python = ">=3.12"` at
`pyproject.toml:16`, `harness-is/pyproject.toml:8`, `harness-runtime/pyproject.toml:18`), and the
operator's own machine is an Intel x86 Mac.

**The correct statement, which replaces both rows':** Windows is a **design-substrate-contracted
host OS with no CI witness and no packaging declaration.** That is materially different from "not a
committed surface" (which would make the gap a pure feature request) and materially different from
"an active target" (which would make it blocking). It makes the gap a **standing divergence from a
[HIGH]-confidence committed constraint**, currently unobservable. Reading D's demand test must be
keyed on observability, not on the commitment — because the commitment already exists and has for the
whole life of both rows.

### (ii) **`reconciler_pause_resume_substrate` is a different and harder shape than the other three carriers** `[HIGH]`

`B-45` records this at item (c) as a *"blast-radius nuance."* It is more than that: it is the one
carrier whose Windows fix is not "fill in a no-op branch."

Verified at HEAD: `reconciler_pause_resume_substrate.py` contains **zero** `_IS_WINDOWS`
occurrences and imports `fcntl` unconditionally at `:106`; its lock body is `:290`–`:300` with the
acquisition at `:294`. It is imported **module-level** by
`bootstrap/factories/r_cxa_2_producer_loop_factory.py:36`, so on Windows that bootstrap path raises
`ModuleNotFoundError: fcntl` at import time. The other three carriers each declare a flag
(`cross_process_ledger_lock.py:90`, `protected_result_store.py:48`,
`journal_workflow_pause_store.py:104`) and import `fcntl` function-locally.

**Consequence for the readings.** Any reading that touches Windows must decide whether this carrier
gets (a) the same real backend as the other three, or (b) at minimum the flag-plus-function-local-import
shape so that Windows import stops crashing. **(b) is strictly smaller than (a) and is independently
valuable** — it is the difference between "a Windows process cannot start" and "a Windows process
starts with a documented degradation." No reading below treats (b) as optional.

### (iii) **THE CORRECTNESS STAKE, traced end to end — and there are TWO of them, not one** `[HIGH]`

**Stake 1 — the promotion activation.** `MemoryPromotionService._commit_record`
(`memory_promotion.py:840`) is the guarded-write caller. Its docstring states the guarantee the fix
would restore, verbatim at `:871`–`:878`:

> *"CROSS-PROCESS (Codex round-1 [P1]): the store's locks were in-process only, which left the same
> interleaving open between two OS processes sharing one repo-derived memory root - a real topology,
> not a hypothetical one (`harness run` alongside `harness daemon`). The store now takes a per-root
> `cross_process_scope_lock` around this guarded section AND around every mutating write, so the
> capture writers that append new provenance lines DO hold the lock this section holds - which is
> exactly what the service-local alternative could not arrange."*

The chain: `_commit_record:903` gates on `SemanticRecordStatus.ACTIVE`; `_provenance_unchanged`
(`:907`–`:908`) re-derives the per-source provenance vector; `:911` calls
`write_record_guarded(record, precondition=_provenance_unchanged)`; a conflict raises
`MemoryStoreGuardedWriteConflictError` (`memory_store.py:343`), re-raised as
`PromotionProvenanceChangedError` at `memory_promotion.py:913`. Inside the store,
`write_record_guarded:341` opens `with self._write_scope(), _FILE_WRITE_LOCK, _JSONL_WRITE_LOCK:` and
`_write_scope` (`:287`, body `:296`) returns
`cross_process_scope_lock(self._registry.canonical_root(...))`.

**On Windows, `cross_process_scope_lock` yields immediately at `cross_process_ledger_lock.py:205`–`:207`.**
The two `threading.RLock`s remain, so the section is still atomic *within* one process. Precisely what
a two-process Windows deployment can corrupt:

> Process A (`harness run`) enters `_commit_record` for an ACTIVE promotion, evaluates
> `_provenance_unchanged` → `True`. Process B (`harness daemon`) appends a new provenance line for one
> of the cited sources — a mutating store write, which on POSIX would have blocked on the scope lock
> and on Windows does not. Process A then performs the write `_provenance_unchanged` authorized. The
> activation commits against provenance already superseded. **`PromotionProvenanceChangedError` is
> never raised**, so the caller observes a clean success. There is no detect-then-refuse, no log line,
> and no durable marker distinguishing this from a correct commit.

The `harness run` / `harness daemon` topology is not my construction — it is named in the store's own
SCOPE paragraph (`memory_store.py:328`–`:329`) and in the promotion docstring (`:873`–`:874`), and it
is witnessed against a genuine second OS process at
`harness-is/tests/test_memory_store_cross_process_guard.py:171`.

**Stake 2 — `commit_seq` uniqueness, which neither row's *prose* connects to Stake 1.** The code
already states it (`memory_store.py:160`–`:163`, verbatim):

> *"On Windows the uniqueness of this token additionally inherits the B-45 bound: the per-root scope
> lock is a no-op there and the ledger-length read is not covered by the JSONL append lock, so two
> writers can mint the same value (register row B-45)."*

Two writers minting the same `commit_seq` defeats the ordering token that B-94/B-95 exist to protect —
so the Windows carve-out is a *shared precondition* of three registered rows, not one. `B-45`'s
2026-08-05 re-check does cite `memory_store.py:154-163`, but files it as evidence that the (e)
sharpening "holds" rather than as a second, independent stake. It is a second stake.

### (iv) **THE MSVCRT PREMISE IS TRUE BUT INCOMPLETE, and the completion changes the fix's shape** `[HIGH]`

Both rows rest the "this is a real design choice" claim on one sentence
(`forward-register.yaml:842`–`:843`, prose `:550`, restated at the 2026-08-05 re-check
`forward-register.yaml:871`–`:872`):

> *"`msvcrt.locking` is byte-range and exclusive-only; it does not cleanly provide the
> shared-reader/exclusive-writer (`LOCK_SH`/`LOCK_EX`) split …"*

**Grounded against the primary source** (https://docs.python.org/3/library/msvcrt.html, accessed
2026-08-05):

- Byte-range: **confirmed** — *"The locked region of the file extends from the current file position
  for nbytes bytes."*
- `LK_LOCK` / `LK_RLCK`: *"Locks the specified bytes. If the bytes cannot be locked, the program
  immediately tries again after 1 second. If, after 10 attempts, the bytes cannot be locked, `OSError`
  is raised."* → **a fixed, non-configurable ~10-second deadline**, not an unbounded block.
- `LK_NBLCK` / `LK_NBRLCK`: *"Locks the specified bytes. If the bytes cannot be locked, `OSError` is
  raised."* → **a non-blocking probe exists.**
- Shared vs exclusive: the docs **do not distinguish** — `LK_RLCK`/`LK_NBRLCK` are documented with
  identical wording to `LK_LOCK`/`LK_NBLCK`. So "exclusive-only" is a fair reading of what the docs
  *guarantee*, but it is a statement about **absence of a documented shared mode**, not a documented
  prohibition. `[MODERATE]` on the precise semantics; `[HIGH]` that no shared face can be *relied on*.

**Two consequences the rows have never drawn.** `[HIGH]`

1. **A non-blocking Windows primitive exists.** `LK_NBLCK` is exactly the `LOCK_NB` shape B-93's
   close-out step (1) prescribes. So the deadline mechanism — non-blocking probe + caller-owned
   bounded retry — is expressible on **both** platforms with one code shape. This is the fact that
   decides §7.
2. **The `LOCK_SH` face is not the blocker it is recorded as** (see (v)).

### (v) **A THIRD OPTION EXISTS, IT IS NAMED IN THE DESIGN SUBSTRATE, AND NO RECORD SHOWS IT WAS EVER REJECTED** `[HIGH]`

`B-45`'s close-out step (1) offers two arms: *"`msvcrt`-based exclusive-only lock with a documented
downgrade of the shared-read guarantee, **or a vetted portable library**"* — the second arm generic and
unnamed (`forward-register.yaml:847`–`:849`).

**The design substrate names it, and recommended adopting it.**

> `design-substrate/Plan_Executability_Audit_v1.md:84` — *"| U-IS-11 | Cross-platform file-lock |
> `filelock` PyPI [HIGH — mature, single-purpose, cross-platform fcntl + Windows binding] |"*

That is a GUARDRAIL row, and `:230` routes the binding decision: *"| File-lock | 1 unit (U-IS-11) |
Session 6 |"*, under the GUARDRAIL contract at `:58` (*"requires a documented binding decision routing
to Session 6 … governance"*).

**No such decision was ever recorded.** `filelock` appears **zero** times in `.harness/`, zero times
in root `CLAUDE.md`, zero times in any Session 6/7 close handoff, and zero times in the shipped
module. The hand-rolled `fcntl` helper arrived two months after U-IS-11 landed, under a *bug* row, and
its recorded rationale is pattern-precedent rather than library evaluation
(`post-phase-8-forward-register.md:535`): *"a same-host `fcntl.flock` helper **mirroring the proven
pattern already shipped at** `harness_runtime.lifecycle.reconciler_pause_resume_substrate._workflow_lock`."*
So the recommended adoption was neither taken nor declined — **it was never adjudicated.**

**What the library actually provides**, probed at session time
(`uv run --with filelock`, version **3.29.4**, 2026-08-05):

| Capability | Evidence |
|---|---|
| Configurable deadline + typed timeout | `FileLock(lock_file, timeout=-1, mode=-1, thread_local=True, *, blocking=True, is_singleton=False, poll_interval=0.05, lifetime=None)`; `filelock.Timeout` exported. This is B-93 steps (1) **and** (2) in one primitive |
| Genuine Windows backend | `WindowsFileLock`; its module (`filelock/_windows.py`) references `msvcrt.LK_NBLCK` and `msvcrt.LK_UNLCK` — i.e. it implements exactly the non-blocking-probe-plus-poll shape (iv)(1) identified |
| Shared/exclusive split | `ReadWriteLock` (added 3.21.0) with `acquire_read` / `acquire_write` / `read_lock` / `write_lock`. Its docstring: *"Cross-process read-write lock backed by SQLite. Allows concurrent shared readers or a single exclusive writer."* Its module references **neither** `fcntl` **nor** `msvcrt` **nor** `LOCK_SH` — it is portable **by construction** |
| Dependency weight | Pure-Python `py3-none-any` wheel; already resolved into `uv.lock:608` transitively via `huggingface-hub` (`uv.lock:1179`), though declared in **no** `pyproject.toml` |

**Framework-pull discipline does not forbid it.** `[HIGH]` Root `CLAUDE.md` §3.2's four prohibitions
(`:111`–`:114`) name retry/breaker libraries, workflow orchestrators, validation libraries, and
LiteLLM. None reaches file locking. §3.1's `Reliability primitives` row (`:102`) scopes "NO framework"
to *"retry / breaker / idempotency"*. The only clause that reaches this is `Bounded adoption` (`:110`):
adoption is permitted *"if no existing-stack solution meets the unit's acceptance criteria"* — and the
executability audit itself, which is the discipline's own source artifact, concluded exactly that at
`:84`.

**Stated against interest.** `[HIGH]` `ReadWriteLock` is **not** a drop-in. It is SQLite-backed and
requires a `.db` lock file, which changes the **lock-file identity** the current protocol depends on:
`cross_process_write_lock` deliberately locks the *canonical file's own inode* and never creates it
(`cross_process_ledger_lock.py:352`–`:356`), and the Runtime spec makes lock identity contract-relevant
elsewhere — `Spec_Harness_Runtime_v1.md:5971`: *"A directory-tree scope lock is explicitly NOT
SUFFICIENT and MUST NOT be specified: `flock` contends only on the same inode, the house
directory-tree lock uses a different file, and the pause-journal appender does not take it."* Adopting
`ReadWriteLock` for the `LOCK_SH` face is therefore a **protocol migration**, not a substitution.
**And the plain `FileLock` face is an identity migration too, not a drop-in (codex R1 [P1], accepted):**
`FileLock` treats its path as a LOCK FILE — its Unix backend opens with create/truncate semantics — so
it cannot safely target the canonical ledger file's own inode that `cross_process_write_lock`
deliberately locks (`:352`–`:356`); pointing it there risks truncating the ledger. The safe shape is a
SIDECAR lock file — which CHANGES LOCK IDENTITY at every converted site (including the exclusive-only
ones): during any rolling upgrade, an old process contending on the canonical inode and a new process
contending on the sidecar do not exclude each other. Any `filelock` adoption therefore needs a
cutover/interop story per site (the B-97(a) quiesced-cutover precedent is the reference shape), and
"maps onto the exclusive-only sites — SEVEN of the nine (codex R2 corrected an earlier eight: `_acquire_legacy_sidecar_if_present` is reached with `exclusive=False` and `cross_process_read_lock` acquires `LOCK_SH`, so two sites need shared semantics `FileLock` does not have)" must be read as *after* that migration, never as a direct
substitution.

**Net effect on the rows.** The sentence *"the fix stays a real decision: `msvcrt.locking` is
exclusive-only and cannot express the `LOCK_SH` face"* (`forward-register.yaml:871`–`:872`) remains
true **about msvcrt** and is **no longer sufficient as the reason the fix is hard**. The fix is still
a real decision — but the decision is now *which vehicle*, with three arms, not *whether the shared
face must be degraded*.

### (vi) **THE WITNESS AND FOOTPRINT, measured** `[HIGH]`

**Ten** tests spawn a real second OS process and assert lock behaviour:

| Carrier | Witnesses |
|---|---|
| `cross_process_ledger_lock` | `harness-is/tests/test_cross_process_ledger_lock.py:800` (`multiprocessing.get_context("fork")` at `:823`) |
| `memory_store` guarded write | `harness-is/tests/test_memory_store_cross_process_guard.py:171` (fork ctx `:190`) |
| `protected_result_store` | `harness-runtime/tests/test_lifecycle_protected_result_store.py:1176`, `:1267` (`subprocess.Popen` at `:1228`, `:1289`) |
| `reconciler_pause_resume_substrate` | `harness-runtime/tests/test_reconciler_pause_resume_substrate.py:253` (`subprocess.Popen` at `:266`) |
| `journal_workflow_pause_store` | `harness-runtime/tests/test_journal_pause_store_cross_process_append_b97.py:275`, `:322`, `:362`, `:430`, `:533` (spawn helper `_spawn` at `:247`, `_child` at `:257`) |

Every other concurrency witness in these files is **thread**-based and contends only on the
in-process `RLock` face — stated in the suite itself at
`test_cross_process_ledger_lock.py:803`–`:806`. A deadline witness must therefore be process-based; a
thread-based one would pass against the `RLock` and prove nothing.

An existing Windows carve-out witness already exists —
`test_journal_pause_store_cross_process_append_b97.py:752`
(`test_windows_carve_out_round_trips_without_creating_a_lock_file`), which monkeypatches
`_IS_WINDOWS = True` (`:769`). Any Windows backend **must update this test**, because it currently
asserts the *absence* of a lock file as correct behaviour.

**Footprint estimate for the full fix:** 9 acquisition sites + 6 platform branches + 1 unguarded
carrier (§3(ii)) + 1 retry/deadline helper + 1 typed exception + the hold-time contract docstring at
`write_record_guarded`; ~10 witnesses updated and ~4–6 added (one deadline witness per site-class, one
Windows-degradation witness). Medium, single traversal, four modules, no cross-axis edge.

### (vii) **NO SPEC LEG IS OWED UNDER ANY READING — verified, not assumed** `[HIGH]`

Both rows assert this in passing (`B-93` council clause: *"an already-cleared lock mechanism (C-IS-09
§9.4 defers the mechanism to implementation discretion)"*). It is worth verifying because it changes
the legs table from four legs to two.

`design-substrate/Spec_Information_Substrate_v1.md:896` is `### §9.4 Multi-writer scaling boundary`.
Its deferral footer, `:900`, verbatim:

> *"**Deferred to implementation discretion.** Specific worktree directory location convention
> (`.worktrees/<sub-agent-id>/` or alternative); specific worktree-allocation API surface; **specific
> cross-worktree writer-serialization mechanism (advisory lock / leader-election /
> single-threaded-write enforcer)**; specific worktree reclamation cleanup policy."*

C-IS-07 §7.4 defers it a second time, `:756`: *"specific concurrent-writer serialization mechanism
(advisory lock / per-line flock / lease coordination)"* — the only `flock` occurrence in the entire IS
spec.

What the spec **does** commit is *that* writers are serialized: `:742` (*"the C3-pole append-only write
contract serializes writers"*), `:893` (cross-worktree writer serialization), `:774` (the critical
section covers read-prior → compute-hash → append). Across the whole IS spec: `timeout` **0**,
`deadline` **0**, `platform` **0**, `cross-process` **0**, `file lock` **0**.

**Therefore:** a deadline is a *liveness property of an unconstrained mechanism*; a Windows backend is
a *platform realization of an unconstrained mechanism*. Neither adds, removes, or reinterprets a
contract term. **Zero spec delta, zero plan delta, zero contract numbers, zero CXA rows, zero hash
impact, zero clearance markers.** X-AL-3 is not engaged — this is impl-to-cleared-spec, exactly as
B-40 itself was recorded (`post-phase-8-forward-register.md`, B-40 block: *"requirement was settled
(C-IS-09 §9.3 + C-MEM-08), mechanism was implementation discretion (§9.4); impl-to-cleared-spec"*).

**The one caveat, stated rather than smoothed.** If the operator selects the `filelock` vehicle, the
*substrate* changes (a new declared dependency). That is a Session-6-class binding decision the
executability audit already routed and that was never recorded (§3(v)) — it is a **stack** decision,
not a **spec** decision. It belongs in the ratification, not in a spec leg.

---

## §4 The readings

All four readings preserve, without exception: the release-before-blocking ABBA handoff
(`cross_process_ledger_lock.py:394`–`:399`, `:500`–`:504`, `:601`–`:602`), the reentrant per-thread
`_DirLock` face, the "lock never creates the canonical file" property (`:352`–`:356`), and the legacy
sidecar coexistence protocol. Any reading that breaks one of those is out of scope by construction.

### Reading A — the full combined fix

Deadline at **all nine** acquisition sites (`LOCK_NB` probe + bounded retry with backoff), **one new
typed timeout exception** distinct from `MemoryStoreGuardedWriteConflictError`, a **real Windows
serialization backend** replacing all six no-ops, the §3(ii) flag-plus-function-local-import repair at
`reconciler_pause_resume_substrate`, and the hold-time contract documented at `write_record_guarded`.
One traversal, four modules.

- **For.** Discharges both rows completely; one traversal instead of two; the deadline code motion and
  the Windows non-blocking-probe motion are the same motion (§3(iv)(1)); closes the §3(iii) correctness
  stakes; honours the C-STK-10 commitment (§3(i)).
- **Against, and it is decisive on the Windows half.** `[HIGH]` **There is no Windows CI, so the
  Windows backend cannot be witnessed.** Worse than untested: landing it flips
  `journal_exclusion_is_degraded()` (`journal_workflow_pause_store.py:414`) from `True` to `False` on
  Windows, and its one consumer — `admin/pause_journal_adoption.py:412`, which **refuses by default**
  where the primitive degrades — would stop refusing. **A declared, safe degradation would be replaced
  by an unverified exclusion claim.** That is a strictly worse posture than today's, and it is not
  fixed by choosing a better backend; it is fixed only by a Windows CI witness.
- **Sub-decision A-i (naming + home).** `CrossProcessLockTimeoutError`, homed at **`harness-core`**.
  Grounds: all four carriers must raise one nominal type — ONE in `harness-is`
  (`cross_process_ledger_lock.py`, six of the nine sites) and THREE in `harness-runtime` (the
  reconciler, protected-result, and journal stores; codex R1 [P3] corrected an earlier two-and-two
  misstatement); `harness-core` has zero workspace dependencies (`harness-core/pyproject.toml:9`–`:11`)
  so nothing can cycle; and there is direct precedent —
  `ValidatorEscalationGateTimeoutError` (`harness-core/src/harness_core/validator_escalation_errors.py:43`),
  re-homed for exactly this carrier-home reason (`:1`–`:13`). **Fallback:** `harness-is`, alongside the
  five `MemoryStore*Error` types (`memory_store.py:75`–`:91`) or beside `_DirLock`; legal because
  `harness-runtime` already imports `harness_is` 124× including `harness_is.cross_process_ledger_lock`
  directly (`admin/record_migration.py:48`) while `harness-is` imports `harness_runtime` **zero** times.
  **Illegal under any reading:** defining it in `harness-runtime` — that inverts the direction and
  violates the IS 0-outbound invariant (`harness-is/CLAUDE.md` §2.3).
- **Sub-decision A-ii (vehicle).** Hand-rolled `LOCK_NB`+retry, or `filelock` (§3(v)). Under A the
  library is more attractive than under any other reading, because it supplies the deadline **and** the
  Windows backend **and** (via `ReadWriteLock`) the shared face in one adoption — at the cost of the
  lock-file-identity migration §3(v) records against interest.

### Reading B — deadline now; Windows serialization stays documented-degraded *(RECOMMENDED)*

B-93's half in full: deadline at all nine sites, the new typed exception, the hold-time contract at
`write_record_guarded`. **Plus** the §3(ii) minimal Windows repair — give
`reconciler_pause_resume_substrate` the `_IS_WINDOWS` flag and function-local `fcntl` import its three
sibling carriers already have, so a Windows process **starts** with a documented degradation instead of
crashing at import. B-45's serialization backend is **not** built; `B-45` re-registers with the
sharpened demand test at §4/Reading D and with its "no active Windows target" framing corrected per
§3(i).

- **For.** `[HIGH]` Everything in B is **verifiable on the CI that exists** — ten process-based
  contention witnesses already run on `ubuntu-latest` (§3(vi)). It preserves the safe declared
  degradation: `journal_exclusion_is_degraded()` keeps returning `True` on Windows, so the adoption
  tool keeps refusing by default. It performs the code motion the later Windows leg needs, making that
  leg **smaller**, not larger. And it addresses the one gap whose trigger can fire **silently** — the
  second `write_record_guarded` precondition, which the seam gives its author no signal about.
- **Against.** It leaves the §3(iii) correctness stakes open, and they are the only *correctness* items
  in either row. It also leaves a [HIGH]-confidence committed constraint (C-STK-10) diverged, though
  §3(i) establishes that divergence has stood unenforced since before either row existed.
- **The import repair is not a serialization claim.** Stated explicitly so it is not mistaken for one:
  giving the reconciler a flag makes Windows *start*; it does **not** make Windows *exclude*. The
  degradation is unchanged in kind, only in blast radius.

### Reading C — Windows backend now; deadline deferred

The mirror of B. Six no-ops replaced, the reconciler given a real backend, deadline deferred.

- **Dominated, and recorded so it is not re-proposed.** `[HIGH]` C takes the one half that **cannot be
  witnessed** and leaves the one half that **can**. It converts `journal_exclusion_is_degraded()` from a
  true statement into an unverified one, disarming the only place the codebase currently *acts*
  defensively on this carve-out. And it forgoes the deadline's code motion, so a later B leg must
  re-traverse all nine sites — the exact double traversal both rows filed to avoid. C is strictly the
  riskiest of the four and is recommended against under every discriminator at §6.

### Reading D — defer both under a falsifiable demand test

Neither half is built. Both rows stay `registered_finding` with their premises re-stamped per §3 and
§10, and re-open on any of:

| Test | Fires when | Why it is the right trigger |
|---|---|---|
| **D-0** | A **second** production `write_record_guarded` caller appears — i.e. any new `precondition=` argument beyond `_provenance_unchanged` (`memory_promotion.py:911`) | B-93's own registered trigger, unchanged. The first caller whose precondition is unbounded converts the row from latent to live |
| **D-1** | A **Windows CI job** is added to `.github/workflows/` (today: `runs-on: ubuntu-latest` ×12, zero Windows) | The gate on B-45's half is *witnessability*, not backend choice (Reading A's "against"). Windows CI is the precondition that makes any backend landable |
| **D-2** | An operator or deployment asks for a Windows host, OR any packaging surface declares one (an `Operating System ::` classifier or a `sys_platform` marker in a harness `pyproject.toml` — today: zero) | Converts the C-STK-10 commitment from a design-time constraint into an observable target |
| **D-3** | An **observed stall** — any report or log of a same-host memory writer blocked indefinitely | The empirical falsifier of "no live hazard at HEAD" |
| **D-4** | A **third** row is registered against this same lock substrate (today: `B-45`, `B-93`, plus `B-45`'s accepted O-1 lock-identity residual and `B-94`/`B-95` which inherit the `commit_seq` bound at §3(iii) Stake 2) | Accumulating rows against one primitive is itself evidence that the substrate, not the individual gaps, is the unit of work |

- **For.** Every harm in both rows is currently unreachable; the substrate has been through repeated
  adversarial hardening rounds (B-40, B-46, B-73, B-97) and carries documented ABBA/TOCTOU invariants,
  so a nine-site traversal for zero observable benefit is a genuine regression-risk trade.
- **Against.** D-0's trigger is **silent** — the seam explicitly knows nothing about its preconditions,
  so the author who fires it gets no signal, and the row's re-check depends on a human noticing. That
  is the one demand test in the set that cannot be relied on to fire.

---

## §5 The decisions, and two variants considered and dominated

**There are exactly TWO decisions**, and they are separable:

1. **Does the same-host lock substrate get a liveness deadline now?** (B-93's half — A or B say yes; C
   or D say not yet.)
2. **Does it get a real Windows serialization backend now?** (B-45's half — A or C say yes; B or D say
   not yet.)

Two sub-decisions ride decision 1 and need **no separate gate**: **A-i** the exception's name and home
(recommendation + fallback stated at §4), and **A-ii** the vehicle (hand-rolled vs `filelock`) — with
one exception noted below.

**Variant E — adopt `filelock` as the vehicle without deciding either half.** Considered and
**dominated as a standalone**, but it is *not* dominated as a sub-decision. Declaring the dependency
alone changes nothing at runtime; the value only arrives when a reading consumes it. However, §3(v)
establishes that the `filelock` binding decision was **routed to Session 6 and never recorded** — so if
the operator selects A or B *and* prefers the library vehicle, that selection **is** the missing
Session-6 binding record and should be stated as such in the ratification. It is a stack decision, not
a spec decision (§3(vii)).

**Variant F — put the deadline only on `cross_process_scope_lock`, the one site the B-93 hazard
actually reaches.** Considered and **dominated**, on the rows' own trap 1: one entry surface can block
at up to **three** distinct sites in sequence — for `cross_process_write_lock`, the directory lock
(`:133`, reached via `_dir_lock_for` at `:365`), then the legacy sidecar (`:274`, reached at `:386`),
then the file lock (`:406`). A deadline on one leaves the entry surface with no end-to-end bound, which
is worse than none: it produces a *partial* guarantee that reads as a total one. Verified at HEAD by
direct read of `cross_process_write_lock:363`–`:406`.

---

## §6 Recommendation — **Reading B**, runner-up **Reading D**, and the discriminators

**RECOMMENDED: Reading B** (deadline at all nine + the typed exception + the §3(ii) import repair;
Windows serialization deferred). `[MODERATE]`

Grounds, in order of weight:

1. **The witnessability asymmetry.** `[HIGH]` This is the decisive finding of the filing. B's half is
   fully verifiable on `ubuntu-latest` against ten existing process-based witnesses. B-45's half is
   **not verifiable at all** today, and landing an unverified exclusion claim is *worse than the
   documented no-op it replaces*, because `journal_exclusion_is_degraded()` → `False` disarms the one
   defensive consumer at `admin/pause_journal_adoption.py:412`. The Windows half is gated on **CI**,
   not on the backend choice — which is precisely what neither row's close-out says (both frame step (1),
   the backend pick, as the gate).
2. **The silent-trigger asymmetry.** `[HIGH]` Of the two gaps, only B-93's can fire without anyone
   noticing. The Windows gap requires someone to *deliberately run this on Windows* — a loud,
   deliberate act. The deadline gap requires only that someone write a new precondition, from a seam
   whose own docstring advertises that it "knows nothing about what the precondition tests." Demand
   test D-0 is the one test in §4/Reading D that cannot be relied on to fire; D-1/D-2 are reliable.
3. **The code motion is shared and one-directional.** `[MODERATE]` Doing the deadline first makes the
   later Windows leg smaller, because the `LOCK_NB`-probe-plus-retry shape is the same shape
   `msvcrt.LK_NBLCK` needs (§3(iv)(1)). Doing Windows first (Reading C) does not reciprocate. So B is
   the ordering that costs one-and-a-bit traversals rather than two.
4. **B preserves the safe posture.** `[HIGH]` It leaves every Windows degradation *declared* and every
   defensive refusal *armed*, while correcting the register's account of *why* they are declared
   (§3(i)).

**A note against my own recommendation.** `[HIGH]` Reading D's core argument is real and I do not
discount it: **every** harm in both rows is unreachable at HEAD, the substrate carries hardening
invariants earned over four closed rows, and nine sites of edits to concurrency code for zero
observable benefit is exactly the risk profile the workspace's own non-convergent-hardening discipline
warns against. The margin between B and D is **narrow**, and an operator who weighs regression risk on
a hardened substrate above a silent-trigger risk is reading the same facts correctly and should pick D.
I am not confident enough to call D wrong; I am confident A and C are worse than both.

**RUNNER-UP: Reading D**, *not* Reading A. Reason: A's Windows half is not merely expensive, it is
**posture-negative** until Windows CI exists (ground 1). D is a defensible waiting position with
falsifiable exits; A is a commitment to ship something no test can check. Under this workspace's
asymmetry reasoning (a deferral costs a re-check; an unverified durable-correctness claim costs a wrong
write nobody detects), D is the safer of the two.

**THE DISCRIMINATORS — what flips the choice.** `[HIGH]`

> **Discriminator 1 (decides the Windows half): can a cross-process lock backend be landed responsibly
> without a witness that it excludes?**
>
> - **No** — then the Windows half is gated on Windows CI, not on the backend pick, and **B or D is
>   right**. This is my reading, and it is the reading `admin/pause_journal_adoption.py:412` already
>   encodes in shipped code: that call site treats "the primitive degrades" as a *refuse* condition,
>   which only stays sound while the degradation predicate is true-by-construction.
> - **Yes** — if the operator holds that a well-reviewed backend plus the existing `_IS_WINDOWS`-monkeypatched
>   carve-out tests (`test_journal_pause_store_cross_process_append_b97.py:752`/`:769`) constitute
>   adequate witness — then **A is right**, and it should be taken as one traversal.

> **Discriminator 2 (decides the deadline half): is a host-wide stall with no diagnostic recoverable
> cheaply enough to wait for?**
>
> - **No** — an autonomous harness that wedges every same-host memory writer with no error, no log and
>   no timeout is expensive to diagnose even though `kill -9` ends it — then **B is right**.
> - **Yes** — a stall is loud in practice, trivially recoverable, and the deadline can be added
>   *when* D-0 fires with the fix's cost unchanged — then **D is right**.

> **Discriminator 3 (decides the vehicle, only if 1 or 2 selects a build): is the never-recorded
> Session-6 `filelock` binding (§3(v)) a decision to make now, or a decision the workspace already made
> by shipping `fcntl` twice?**
>
> - If **now**: `filelock` supplies deadline + Windows + shared face in one adoption, at the cost of a
>   lock-file-identity migration at EVERY converted site — not just the `LOCK_SH` face: per §3(v),
>   plain `FileLock` cannot target the canonical inode either (create/truncate semantics), so each of
>   the nine sites needs a sidecar plus an interop or quiesced-cutover plan (old canonical-inode
>   lockers and new sidecar lockers do not exclude each other during a rolling upgrade).
> - If **already made by conduct**: hand-roll the `LOCK_NB`+retry helper, and record the hand-roll as
>   the Session-6 binding so the audit's GUARDRAIL row stops standing open.

**Two operator sentences decide this fork** — one answering discriminator 1, one answering
discriminator 2. Discriminator 3 only needs an answer if either is a build.

---

## §7 Council position — the condition is MET and the probe RESOLVES it: **NO convening for Readings B, C or D**; a Reading-A selection owes one `[HIGH]`

**The condition.** `B-93`'s council clause is conditional, not a flat "no"
(`forward-register.yaml:2929`, prose `:984`): *"Council-eligible only if it is taken **WITH** B-45 and
the Windows-backend tradeoff makes the deadline semantics non-obvious."* This filing takes the two
rows together, so the antecedent holds and the consequent must be adjudicated here. `B-45`'s own clause
is the mirror (`forward-register.yaml:875`–`:877`): *"council-eligible AT BUILD TIME only if the
msvcrt-exclusive-only-lock tradeoff … turns out non-obvious once actually scoped."*

**The probe** (root `CLAUDE.md` §10.9, council posture amendment 5 — empirical probe at the most
specific primary source before any TENSION block). The question is narrow and answerable: *does the
Windows backend choice change what the deadline means or how it is expressed?*

Probed at the primary sources, 2026-08-05 (§3(iv), §3(v)):

- `msvcrt.locking` exposes `LK_NBLCK` — *"Locks the specified bytes. If the bytes cannot be locked,
  `OSError` is raised"* — a **non-blocking** mode. So the deadline shape B-93 prescribes (`LOCK_NB`
  probe + caller-owned bounded retry) is expressible **identically on both platforms**.
- `msvcrt`'s only *blocking* mode, `LK_LOCK`, carries a **fixed, non-configurable ~10 s** deadline (10
  attempts × 1 s → `OSError`). So even the degenerate Windows path already has a bound; it is the
  POSIX path that is unbounded. The backend choice cannot make the deadline *less* expressible.
- `filelock`'s Windows backend (`filelock/_windows.py`) is built on exactly `msvcrt.LK_NBLCK` +
  `LK_UNLCK` — independent confirmation that non-blocking-probe-plus-poll is the shape a real Windows
  backend takes.

**Probe result: ORTHOGONAL.** The Windows backend decides the **exclusion granularity** (whether a
shared-reader face survives). The deadline decides **liveness** (how long a caller waits and what it is
told). Neither constrains the other: a shared face can be deadline-bounded, an exclusive-only face can
be deadline-bounded, and the typed-timeout semantics (a liveness outcome distinct from
`MemoryStoreGuardedWriteConflictError`'s precondition outcome) are identical either way. **The
antecedent's consequent is FALSE — the Windows tradeoff does not make the deadline semantics
non-obvious. Surfaced as `probe-resolved`; no dyad is convened.**

**The one residual coupling, named rather than hidden.** `[MODERATE]` Under sub-decision A-ii's
library arm, `filelock` supplies its **own** `Timeout` exception and its own `timeout=` parameter, so
the typed-exception design becomes subordinate to the library's rather than independently chosen. That
is a real coupling — but it is an **implementation-vehicle** coupling resolved inside one arc by one
author, not a cross-domain value tension between two voices with different interests. It does not meet
the nameable-tension discriminator (posture amendment 1), and convening a dyad over it would be the
primary-collapse failure the amendments exist to prevent.

**What WOULD owe a convening.** `[HIGH]` **A selection of Reading A** — building the Windows backend
before a Windows CI witness exists — carries a genuine, nameable, cross-domain tension:

> **C3 (information-substrate integrity) ⊥ C11 (operator-loop / local-deployment).** C3's interest:
> an unverified exclusion claim is *worse* than a declared no-op, because it disarms the one defensive
> consumer (`admin/pause_journal_adoption.py:412`) and puts durable-write correctness behind an
> untested primitive. C11's interest: a [HIGH]-confidence committed cross-platform target
> (C-STK-10) that is permanently non-functional is a broken commitment, and "wait for CI" is a
> deferral that may never end.

That tension is namable **in advance**, which is the discriminator's own test. **A Reading-A selection
should be routed to a dyadic C3 ⊥ C11 convening before any Windows code is authored.** Readings B, C
and D do not owe one — B and D leave the degradation declared, and C is recommended against on grounds
that do not require a council to see.

---

## §8 The ratification ask — TWO decisions, one optional third

| # | Decision | Options | Recommendation |
|---|---|---|---|
| **1** | Windows serialization backend — build now? | **Yes** (A or C) → routes to a **C3 ⊥ C11 dyadic convening** first (§7). **No** (B or D) → `B-45` stays `registered_finding` with demand tests **D-1** (Windows CI) and **D-2** (a declared Windows target) | **No.** Gated on witnessability, not on backend choice (§6, discriminator 1) |
| **2** | Liveness deadline — build now? | **Yes** (A or B) → nine sites, one typed exception, the hold-time contract, plus the §3(ii) import repair. **No** (C or D) → `B-93` stays `registered_finding` with demand tests **D-0**, **D-3**, **D-4** | **Yes**, at moderate confidence; **D is a defensible answer** (§6, discriminator 2) |
| **3** *(only if 1 or 2 is Yes)* | Vehicle | Hand-rolled `LOCK_NB`+retry, **or** adopt `filelock` — which also settles the never-recorded Session-6 GUARDRAIL binding (§3(v)) | Hand-rolled for decision 2 alone (SEVEN of nine sites are exclusive-only and need no shared face — `_acquire_legacy_sidecar_if_present(exclusive=False)` and `cross_process_read_lock` both require shared semantics, per §3(v)); revisit `filelock` if decision 1 later goes Yes |

**The recommended combination is (1 = No, 2 = Yes, 3 = hand-rolled) — i.e. Reading B.**

**Carried by any answer, no separate gate.** The §10 drift repairs — two substantive corrections
(§10 items 1 and 2) and three precision items — ride **this** filing's register touch, in place, on
both surfaces, per the replace-not-append discipline. They are not deferred to ratification, because
two of them are statements the rows currently make that this filing's own grounding falsifies.

---

## §9 Sequencing, and what each leg owes

**No spec leg exists in this table under any reading** — established at §3(vii), not assumed. That is
the structural difference between this filing and `B-88`/`B-98`/`B-104`/`B-107`, each of which owed a
`design-substrate/**` amendment.

| Leg | Owes | Gate |
|---|---|---|
| **This filing** (doc-only) | The filing + the FILED sentence on both rows' `close_out` and prose + the §10 corrections applied in place on both surfaces. Both rows stay `registered_finding`; **no snapshot/digest change** (digest is over `id:status`, status unmoved); **no `design-substrate/**` edit**, so the X-AL-3 guard passes on the `.harness/` back-flow doc | — |
| **Ratification** | Operator answers decisions 1 and 2 (and 3 if either is Yes) via `AskUserQuestion`; a `§12 RATIFICATION` section is appended here; each row's `pr:` pointer set; status flips only for a row whose half is a Yes | Operator |
| **Council** *(decision 1 = Yes only)* | Dyadic **C3 ⊥ C11** convening per §7, before any Windows code is authored | Follows ratification |
| **Deadline build leg** *(decision 2 = Yes)* | Nine acquisition sites bounded; one typed exception at its ratified home (A-i); the ABBA release-before-blocking handoff preserved at all three probe arms; the hold-time contract documented at `write_record_guarded`; the §3(ii) reconciler import repair; ≥1 process-based deadline witness per site-class + a mutation probe per the PD-8 discipline (revert the bound, confirm the witness fails, restore). **Closes `B-93`** | CI + out-of-family artifact review SELECTED BY AUTHORSHIP (`just codex-review` for Claude-authored work; `just gemini-review` if Codex authors the leg — self-review is not out-of-family, AGENTS.md) + `merge-gate` 3-lens (code-touching) |
| **Windows build leg** *(decision 1 = Yes)* | Six no-op surfaces replaced; the reconciler given a real backend; **`test_journal_pause_store_cross_process_append_b97.py:752` updated** — it currently asserts the *absence* of a lock file as correct Windows behaviour and would be a false green; `journal_exclusion_is_degraded()`'s contract restated (it becomes a claim about the backend, not about the platform); the `admin/pause_journal_adoption.py:412` refuse-by-default consult re-adjudicated. **Closes `B-45`** — and per `B-45` item (b) the close is a **multi-surface doc sweep** across the 6+ sites that cite this row as the workspace's Windows posture | Windows CI (per §6 discriminator 1) + out-of-family artifact review selected by authorship (same rule as the deadline leg) + `merge-gate` |
| **Re-registration leg** *(any half = No)* | The declining row's demand tests written into its `close_out` and prose, and its Windows-framing correction (§10 item 1) confirmed carried. **No status change** | — |

**Ordering note.** If both decisions are Yes, the deadline leg **must precede** the Windows leg —
ground 3 at §6. Reversing the order re-traverses all nine sites twice, which is the outcome both rows
were filed to avoid.

---

## §10 Cite re-verification at HEAD `966bc658`, and the drift found

Every cite in this filing was resolved by direct read at **this** HEAD. Every count was recounted at
this HEAD. The 2026-08-05 sweep that re-stamped both rows ran at HEAD `43d4dda5`; nothing here is
carried from it unverified.

**Verified as cited.**

| Cite | Verified |
|---|---|
| Nine blocking `flock` sites — `cross_process_ledger_lock.py:133`/`:274`/`:330`/`:406`/`:507`/`:605`; `reconciler_pause_resume_substrate.py:294`; `protected_result_store.py:371`; `journal_workflow_pause_store.py:489` | ✓ all nine, individually |
| Three `LOCK_NB` probes `:402`/`:498`/`:599`, each releasing the dir lock before blocking | ✓ read `:390`–`:419`, `:488`–`:512`, `:590`–`:611` |
| Seven entry surfaces `:186`/`:347`/`:466`/`:550` + `:271`/`:340`/`:418` | ✓ |
| Six `_IS_WINDOWS` no-op surfaces `:205`/`:358`/`:478`/`:560`; `:363`; `:477` | ✓ |
| Flag declarations `:90`, `:48`, `:104`; reconciler has none, unconditional `import fcntl` at `:106` | ✓ |
| `journal_exclusion_is_degraded()` `:402`, `return _IS_WINDOWS` `:414`; consult at `admin/pause_journal_adoption.py:412` | ✓ |
| ZERO `msvcrt` in any `.py`; ZERO timeout/deadline code in all four carriers | ✓ (one prose-only hit, `reconciler_pause_resume_substrate.py:80`) |
| `write_record_guarded` `:298`, precondition param `:302`, hold `:341`, `_write_scope` `:287`/`:296` | ✓ |
| Promotion chain `_commit_record:840`, CROSS-PROCESS docstring `:871`–`:878`, `_provenance_unchanged:907`, call `:911`, re-raise `:913` | ✓ |
| `commit_seq` Windows-uniqueness docstring `memory_store.py:160`–`:163` | ✓ verbatim |
| C-IS-09 §9.4 heading `Spec_Information_Substrate_v1.md:896`, deferral footer `:900`; C-IS-07 §7.4 `:756` | ✓ verbatim |
| `Target_Stack_Commitment_v1.md:42` (C-STK-10); `ADR-F4.md:21`, `:48` | ✓ verbatim |
| `Plan_Executability_Audit_v1.md:84` (`filelock` GUARDRAIL), `:230` (Session-6 routing), `:58` (GUARDRAIL contract) | ✓ verbatim |
| Ten real-second-OS-process witnesses (§3(vi)) | ✓ each `def test_` line + spawn call |
| Exception homes — `MemoryStoreGuardedWriteConflictError` `memory_store.py:91` (`RuntimeError`); `harness-core` precedent `validator_escalation_errors.py:43` + rationale `:1`–`:13` | ✓ |
| Import direction — `harness-is` → `harness_runtime` **zero** imports; `harness-runtime` → `harness_is` **124** | ✓ |

**DRIFT AND CORRECTIONS FOUND — five items. Items 1 and 2 are substantive and are corrected in place
on BOTH register surfaces in this same commit.**

| # | Row claim | Verified at HEAD `966bc658` | Class |
|---|---|---|---|
| **1** | `B-45`: *"low urgency until Windows becomes an active target"* (`forward-register.yaml:857`, prose `:551`) and *"Still not blocking — no Windows CI, **no active Windows target**"* (prose `:558`, YAML `:824`) | **MISLEADING AS A DISPOSITIONAL GROUND.** The operational half is true (zero Windows CI, zero packaging declaration, operator on x86 macOS). The implied design-substrate half is **false**: `Target_Stack_Commitment_v1.md:42` commits macOS/Linux/**Windows** host-OS support at `[HIGH]` *"without per-OS port forking"*, and `ADR-F4.md:21`/`:48` commits a Windows-native process-tier case. The `B-40` row (`post-phase-8-forward-register.md:536`) already quotes C-STK-10 verbatim — the clause was dropped when the dismissal propagated to `B-45`. **Corrected in place, both surfaces, date-stamped 2026-08-05.** `B-93` inherits nothing here (it makes no Windows claim) | **2** |
| **2** | `B-45`: *"the fix stays a real decision: `msvcrt.locking` is exclusive-only and cannot express the `LOCK_SH` face"* (`forward-register.yaml:871`–`:872`; the same premise at `:842`–`:843` / prose `:550`) | **TRUE ABOUT MSVCRT, INSUFFICIENT AS THE REASON.** `msvcrt` also exposes `LK_NBLCK` (non-blocking), and the shared face has a portable third arm the row's own generic *"or a vetted portable library"* never named: `filelock` **3.29.4** ships `ReadWriteLock` (SQLite-backed, *"concurrent shared readers or a single exclusive writer"*, referencing neither `fcntl` nor `msvcrt`), `WindowsFileLock` (on `msvcrt.LK_NBLCK`), and `FileLock(timeout=…)` + `Timeout`. And `Plan_Executability_Audit_v1.md:84` **recommended `filelock` at [HIGH]** for U-IS-11, routed to Session 6 at `:230` — **a binding decision no artifact in this workspace ever records.** Adoption does not violate framework-pull §3.2 (four named prohibitions, none reaching file locking). **Corrected in place, both surfaces, date-stamped 2026-08-05** | **2** |
| **3** | `B-93` + the sweep: *"`_provenance_unchanged` at `memory_promotion.py:911`"* | **OFF-BY-CITE.** `:911` is the `write_record_guarded(...)` **call**; the `def _provenance_unchanged()` is at **`:907`** (body `:908`). The claim is unaffected; the cite is not the definition it names. Corrected in place | 3 |
| **4** | `B-93`: the test-caller list *"`test_memory_store.py:523/:539/:564/:618` + `test_memory_store_cross_process_guard.py:168`"* | **INCOMPLETE.** `harness-runtime/tests/test_u_mem_27_activation_boundary.py` also carries **four** `write_record_guarded` definitions (`:273`, `:342`, `:391`, `:629`) and **three** delegating calls (`:348`, `:397`, `:638`). All are protocol-conforming doubles; **none supplies a new precondition**, so the trigger verdict ("has NOT fired") is unchanged. Recorded so a later re-check does not read the list as exhaustive | 3 |
| **5** | Neither row records this | **NEW, additive.** `cross_process_ledger_lock.py` carries **two further** `_IS_WINDOWS` occurrences that are **not** lock carve-outs — `:239` and `:297`, both `if not _IS_WINDOWS:` guards adding `O_NOFOLLOW` to an `os.open` flag set inside the legacy-sidecar helpers. A grep-driven implementer counting `_IS_WINDOWS` would read **eight** surfaces where there are **six**. Recorded so the Windows leg does not "fill in" two flag guards as if they were no-ops | 3 |

**Not re-verified this pass — stated rather than smoothed.**

- **`B-45` item (b)'s downstream doc-cite inventory** (*"cited from 6+ production/test surfaces"* —
  `audit_writer.py:783`/`:1074`/`:1527`, `redaction_token_audit_map.py:112`, `shutdown.py:117`,
  `test_cross_process_ledger_lock.py:24`, three skip-reasons at
  `test_u_rt_134_audit_signing_fail_closed.py:1106`/`:1205`/`:1263`). Only the six no-op **lock**
  surfaces were re-read. That inventory bears on the *retirement sweep* the Windows leg owes, not on
  any reading here. The same tail was flagged unverified by the 2026-08-05 sweep; it remains unverified.
- **`filelock`'s `ReadWriteLock` behaviour under genuine Windows contention.** Its API, backing store
  and platform-independence were probed at session time on macOS; its Windows semantics were **not**
  exercised — for the same reason the whole Windows half is gated (no Windows host, no Windows CI).
  This is stated as an unverified property of a candidate vehicle, not as a recommendation to trust it.
- **`msvcrt`'s shared-vs-exclusive semantics.** The Python docs (accessed 2026-08-05) document
  `LK_RLCK`/`LK_NBRLCK` with wording identical to `LK_LOCK`/`LK_NBLCK` and draw no shared/exclusive
  distinction. "Exclusive-only" is therefore recorded at `[MODERATE]` as a statement about what the
  docs *guarantee*, not at `[HIGH]` as a documented prohibition.

**Review record.** *(R0 — initial authoring, this commit. Out-of-family `just codex-review` and the
`merge-gate` lenses run at the orchestrator's leg; rounds are appended here.)*



