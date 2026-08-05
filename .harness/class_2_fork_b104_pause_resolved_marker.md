# Class 2 Fork — B-104: the pause journal writes no pause-RESOLVED marker

**Status: RATIFIED 2026-08-01 as READING D — DECLARE + DEFER, and RE-AFFIRMED in the 2026-08-05 operator ratification batch.** (Filed 2026-08-01 at PR #1181; Component 1 landed at Runtime spec v1.110, PR #1182.) See `## §11 RATIFICATION`, and `§11.5` for the re-affirmation. Doc-only filing per the workspace
codex-context-guard rule (fork FILINGS ship doc-only FIRST; no `design-substrate/**` edit rides this
PR). Chain mirrors `B-96`'s, `B-97`(a)'s, `B-107`'s and `B-98`'s: **filing (this PR) → operator
ratification → spec leg (if owed) → impl leg.**

**Register row.** `B-104` at `.harness/forward-register.yaml:3396`–`:3460` (`status:
registered_finding`, `pr: '#pending'`) + prose at `.harness/post-phase-8-forward-register.md:1116`.
The row's `pr:` pointer and any status change ride the **ratification** leg, not this PR.

**Grounding HEAD.** `e1a2e7fb`. Every `§`/line cite below was re-resolved by direct read at this
HEAD, and the one load-bearing behavioural claim was settled by **empirical probe**, not by reading
(§3(ii)). The row's own three anchors are **confirmed byte-exact**: the store has **no removal path
of any kind** (zero `unlink` / `os.remove` / write-mode `open` / `truncate()` call sites in
`journal_workflow_pause_store.py` — the two `truncate` substring hits at `:214` / `:256` are prose
naming the invariant) ✓; `PauseJournalReadCause` is **CLOSED at FIVE** members
(`journal_workflow_pause_store.py:107`; `ABSENT` `:120`, `EMPTY_JOURNAL` `:142`, `READ_ERROR`
`:157`, `CORRUPT_LATEST` `:164`, `WORKFLOW_MISMATCH` `:182`) ✓; and the §13.7 surface emits the
upper-bound disclaimer in both renderings (`admin/pause_journal_enumeration.py:71`–`:77`) ✓.

**Spec-side carry, verified UNMOVED.** Term 3-bis lives at `Spec_Harness_Runtime_v1.md:1299` inside
the §13.7 term table (`:1294`–`:1304`, section heading `:1288`), and is byte-identical at the
**v1.109** head this HEAD carries (`:1`) — preserved verbatim across the v1.109 (`B-100`) delta. Its
sibling carries are the §14.14.8 recourse statement at `:5944` (*"drain, then verify against a bound
you can see"*) and the v1.108 change-note's *"findings surfaced, NOT patched"* block at `:43`.

**What this filing does NOT do.** It does not re-open `B-97`(a)'s ratified Reading A (path
segregation, (3a) abandon-by-default, the five-member vocabulary pinned at five) — that is
operator-ratified and gate-2 cleared. It does not re-open `B-97`(b)'s append-lock construction. It
does not depend on `B-96`'s unratified outcome, though it cites `B-96`'s sidecar pricing as an input
(§3(iv)). It **corrects the row's own `close_out`** where grounding falsifies its framing — in two
places, one of them against this filing's own recommendation — and composes the result into the
operator's decision.

---

## §1 The question, and what carries it

The pause journal is append-only and **never truncated**, and **nothing is written when a resume
succeeds** — no resolved marker, no status field, no removal path anywhere in the store. A journal
whose pause was successfully resumed is therefore **byte-indistinguishable** from one whose pause is
still outstanding, and §13.7's enumeration can only bound the at-risk set **from ABOVE**.

The row names **two candidate shapes and chooses neither** — (a) a resolved SENTINEL RECORD appended
at successful resume, (b) an out-of-band per-journal MARKER FILE — and imposes a **self-gate before
either**: *"check FIRST whether an operator who has the §13.7 upper bound plus their own drain
procedure actually needs the discrimination, because a marker bought for a need nobody has is a
capture-side change against a hash-adjacent record for nothing"*
(`.harness/forward-register.yaml:3441`–`:3443`).

**This filing answers that gate first, and the answer is layered rather than binary.** `[HIGH]`

- **The discrimination IS structurally required by the confirmation half of the drain recourse, and
  no other mechanism can supply it.** The enumerated listing is **monotone non-decreasing** under a
  perfect drain — resolution writes nothing and removes nothing — so an operator who resolves every
  outstanding pause sees the **identical listing** they saw before. Only the **zero** case
  self-confirms (§3(i)).
- **But the at-risk set the recourse operates on is a FROZEN, ONE-TIME, DRAINABLE set**, not a
  growing one. Every operator flow that consumes the discrimination — (3a) abandon, (3b) adoption,
  disposal — is scoped to `LEGACY`-classified journals, and **no code path creates a legacy journal
  after the cutover** (`journal_workflow_pause_store.py:674`, the sole derivation site, with the
  no-fallback-read rule stated at `:668`–`:672`). The ambiguity therefore attaches to a bounded,
  dated migration the disposal tool can empty — **not to steady-state operation** (§3(i)).
- **The demand-side conclusion, stated exactly:** the gap is real and permanent, but **at HEAD no
  surviving operator flow acts on the outstanding/resolved distinction for a post-cutover journal**,
  and the one flow that does is one-shot. That is a deferral case, not an absence-of-gap case
  (§3(i), §6).

**And grounding relocates the row's own decision surface in three places:**

- **The row's hypothesized third option — derive the resolution from records the system already
  writes — is FALSIFIED.** Nothing durable records a *successful* resume with an identity joinable
  to a journal filename. The precise missing links are named at §3(iii); a viable-looking near-miss
  is grounded and rejected on a tenant-ambiguity test.
- **The row's two sub-decisions under (a) do not both survive as decisions, and (a) carries a THIRD
  cost the row does not name.** One is **forced** by the shipped read path — a sentinel that is a
  valid `PauseSnapshot` is **RESUMABLE**, so it must not be one. The second is confirmed genuine and
  sharper than the row states: absent a vocabulary change, a resolved journal reports
  `corrupt-latest` **with `indeterminate=True`**, i.e. as an in-flight torn append (empirically
  probed). And the third — **the sixth cause member forces a CROSS-AXIS OD schema leg**, because
  `harness-od` re-declares the same five-value vocabulary independently and the accessor converts
  across them by value (§3(ii)).
- **Every build reading needs an OCCURRENCE KEY, and its composition is already decided in-house.**
  None of the three shapes is safe keyed on workflow identity alone: a resume followed by a
  *re-pause* leaves a stale resolution that reads as a **false all-clear**. The shipped §30 staleness
  token already solves exactly this problem with exactly the right composition — **record count folded
  with the latest raw line's digest** — and states why the digest alone is insufficient (§3(vi)).
- **The row's "second authority" objection to (b) is weaker than it states, and this filing concedes
  it against its own runner-up.** The journal is not a first authority over *"is this pause
  outstanding"* — it cannot answer that question at all — so a marker is the first and only
  authority over an unanswered question, not a second over an answered one. The real (b) hazard is
  narrower and is named at §3(iv), together with two in-house precedents that price it.

---

## §2 Current behaviour at HEAD `e1a2e7fb`

| Surface | State |
|---|---|
| **The store** | `JournalWorkflowPauseStore` (`journal_workflow_pause_store.py:498`). Public surface: `capture` `:531`, `read_latest` `:535`, `read_latest_attributed` `:548`. **No removal, truncation, or rewrite path exists** — verified by token sweep, not by reading intent |
| **The record shape** | `_append` `:689`, record built at `:773`–`:776`: **exactly two keys** — the store-owned wrapper `workflow_id` and the embedded `pause_snapshot` (`snapshot.model_dump(mode="json")`). Serialized `json.dumps(record, sort_keys=True)` `:777` |
| **The key derivation** | `_journal_file` `:665`, **the ONLY key-derivation site**, returning `pause_journal_filename(self._tenant_scope, workflow_id)` `:674`. Its docstring states the rule the row invokes for (b): *"**There is NO fallback read** … a fallback would create a second read authority over one key and fail open at exactly the boundary being built"* `:668`–`:672` |
| **The read's cause vocabulary** | `PauseJournalReadCause` `:107` — **CLOSED at FIVE**, pinned there by the `B-97`(a) ratification (`Spec_Harness_Runtime_v1.md:5901` §14.14.8; the PR #1170 body states *"the five-member `PauseJournalReadCause` vocabulary stays CLOSED at five"*) |
| **The parse** | `_parse_snapshot_attributed` `:841`–`:873`. Wrapper mismatch → `WORKFLOW_MISMATCH` `:858`; `PauseSnapshot.model_validate(record["pause_snapshot"])` `:859`; **any** `ValueError`/`ValidationError`/`KeyError`/`TypeError` → `CORRUPT_LATEST` `:870`–`:873` |
| **The indeterminacy routing** | `read_latest_attributed` sets `indeterminate=cause is PauseJournalReadCause.CORRUPT_LATEST` `:658` — the *"a concurrent append may be in flight"* disposition (`B-102`) |
| **The §13.7 enumeration** | `admin/pause_journal_enumeration.py`. `EnumeratedJournal` `:117` — **FIVE** fields (`path`, `record_count`, `latest_record_digest`, `workflow_id`, `classification`). `UPPER_BOUND_DISCLAIMER` `:71`–`:77`, whose docstring `:66`–`:70` names `B-104` by ID |
| **What the enumeration MAY read** | `_wrapper_workflow_id` `:322`–`:342` — the **store-owned wrapper keys only**. Its docstring pins the boundary: *"§13.7 term 4's boundary is **the EMBEDDED SNAPSHOT, not the record**"* `:323`–`:327`. Spec term 4 at `Spec_Harness_Runtime_v1.md:1301`, term 3-ter at `:1300` |
| **The classification** | `JournalIdentityClass` `:80` — **THREE** members (`LEGACY` `:95`, `CURRENT_FORMAT` `:99`, `NOT_ATTRIBUTABLE` `:106`). `identity_actionable` `:167`–`:175` is **`LEGACY` only**; `adoptable` `:177`–`:189` delegates to it |
| **Disposal** | `admin/pause_journal_disposal.py`. Delete set `targets = orphans` `:168` where `orphans = [j for j in journals if j.adoptable]` `:97` — **LEGACY only, and no flag widens it** (`:164`–`:167`). Dry-run default `:178`; refusal `:202` |
| **Adoption** | `admin/pause_journal_adoption.py`. `AdoptionDisposition` `:154` — **SEVEN** members. Durable account `DEFAULT_ACCOUNT_FILENAME = "pause-journal-adoption-account.jsonl"` `:142`, landing **beside** the journal directory, not inside it `:138`–`:141` |
| **The OD pause-state sink** | `PreBootstrapPauseStateSink` (`lifecycle/pre_bootstrap_pause_state_sink.py:68`) → `<STATE_LEDGER>/pause-state-audit/events.jsonl` (`:57`, `:60`, `:63`). Append-only, `fsync`-ed, torn-append self-healing `:86`–`:93` — **the same hardenings as the journal, deliberately** |
| **That sink's vocabulary** | `PauseStateEventKind` (`harness-od/src/harness_od/pause_resume_namespace.py:501`) — **TWO** members: `ACCESSOR_READ` `:504`, `STALENESS_REFUSED_RESUME` `:508`. Payload `PauseStateAuditPayload` `:515` — `extra="forbid"`, `frozen`, **NINE** fields, `workflow_id` `:553`, **and NO tenant field**; an outcome-split `model_validator` at `:588` |
| **The OD-side MIRROR of the cause vocabulary** | `PauseStateCauseAttribution` (`pause_resume_namespace.py:482`) — the **SAME five values**, **independently re-declared** because *"`harness-od` must not import `harness-runtime` (the axis direction runs the other way), so the vocabulary is re-declared, not re-derived — and any divergence from the Runtime-side enum fails the cross-surface identity witness the §30 contract term requires"* `:486`–`:489`. The accessor converts **by value**: `PauseStateCauseAttribution(cause.value)` (`api.py:1163`) |
| **The §30 staleness token — the in-house occurrence key** | `lifecycle/pause_state_staleness.py:17`–`:27`: the token *"folds the journal's **record count** together with a digest of its **latest raw record line**"*, sound because the append-only invariant makes the count monotone and incrementing on every `capture()`. It explicitly rejects `snapshot_hash` (fail-open — *"two successive LINEAR pauses at the same `step_index` hash IDENTICALLY"*, `:10`–`:12`) and `(snapshot_hash, created_at)` (a luck argument, `:13`–`:15`) |
| **The operator CLI** | `harness_runtime/cli/app.py` — **SEVEN** commands: `run` `:247`, `daemon` `:584`, `inspect` `:639`, `shutdown` `:663`, `migrate-audit-sidecar` `:686`, `adopt-pause-journals` `:728`, `dispose-pause-journals` `:755`. **There is no `resume` command.** Resume is a library API only (`api.py`) |
| **Drain ⊥ resume** | `resume()` raises `HarnessDraining` once the process drain flag is set, and the flag is **one-way for process lifetime** (`api.py:1257`–`:1264`). So *"drain pauses"* cannot mean *"SIGTERM, then resume"* — it means **resolve first, in a non-drained process, then drain** |

---

## §3 Seven grounding findings

### (i) THE DEMAND GATE, ANSWERED — the discrimination IS required by the confirmation half, but the set it bounds is FROZEN and DRAINABLE `[HIGH]`

The row's gate asks whether an operator with the §13.7 upper bound plus their own drain procedure
needs the discrimination. **Walking the three flows gives a split answer, and the split is the
finding.**

**(3a) PRE-UPGRADE DRAIN → CUTOVER.** The recourse decomposes into three operator capabilities. Two
exist; the middle one has no operator surface, and the third cannot close.

| Capability | State at HEAD |
|---|---|
| **See that pauses are outstanding** | **Upper bound only.** §13.7 lists every canonical journal with its identity and two scalars (`inspect.py:946`–`:983`), stamped with `UPPER_BOUND_DISCLAIMER` |
| **Drive pauses to resolution** | **NO OPERATOR SURFACE.** The CLI's seven commands contain no `resume` (§2). Resolution is a library call the *embedding application* makes. And it must precede the drain: `resume()` refuses once drained, one-way (`api.py:1259`–`:1264`) |
| **Refuse new work** | **YES.** `harness-shutdown` → SIGTERM → drain flag; `harness_runtime/drain.py` records `C-RT-11` FULL-LAND at 2026-05-20 |
| **Confirm the drain completed** | **Process quiescence YES; pause-set-empty NO** (below) |

**THE CONFIRMATION CANNOT CLOSE, and the mechanism is arithmetic rather than ergonomic.** `[HIGH]`
Resolution writes nothing and removes nothing, so **the enumerated record count and file set are
monotone non-decreasing across a drain**. An operator who resolves every outstanding pause perfectly
sees **the exact listing they saw before**. Process exit cannot substitute: a durable pause survives
process death *by design* — the store's own docstring says the journal exists *"so a `DURABLE_ASYNC`
workflow-layer pause [is] survivable across a process restart"* (`journal_workflow_pause_store.py:3`–`:8`).
**The only self-confirming case is ZERO** (an empty listing bounds the outstanding set at zero with no
discriminator needed), and that case is unavailable on any deployment that has ever taken a durable
pause. The spec concedes exactly this shape at `Spec_Harness_Runtime_v1.md:5944`: *"The recourse is
therefore 'drain, then verify against a bound you can see', not 'read off the live pause list' — the
latter does not exist at this version."*

**PR #1170's `shutdown_cli` refresh does NOT change this, and the row's task framing should not be
read as though it did.** `[HIGH]` Verified by `git show 07b3e04b`: the change is **78 insertions / 16
deletions in docstring, `--wait` help text and one runtime message — ZERO logic change**, stated
verbatim in the diff. What it fixed was a **false self-description** (the tool claimed its own drain
was *"STRUCK"* pending `[[fork-u-rt-44-workflow-loop-drain]]`, a fork that closed 2026-05-20), which
the spec names as *"the second leg of why that recourse read as unavailable"* (`:1292`). **So the
recourse is now correctly *described* and its refuse-new-work half is genuinely actionable — and its
confirmation half is exactly as open as before.** The fix removed a phantom blocker, not this one.

**BUT — the counter-weight, and it is decisive for the recommendation.** `[HIGH]` **The at-risk set
is FROZEN, ONE-TIME, and DRAINABLE.**

1. **Every consumer of the discrimination is scoped to `LEGACY`.** Disposal's delete set is
   `adoptable` = `identity_actionable` = `classification is LEGACY`
   (`pause_journal_disposal.py:97`, `:168`; `pause_journal_enumeration.py:175`, `:189`). Adoption's
   §14.14.8 fifth mechanical term binds it to the same set. §13.7 reports `CURRENT_FORMAT` as
   *"ordinary state, not at risk"* (`pause_journal_enumeration.py:99`–`:104`).
2. **No code path creates a `LEGACY` journal after the cutover.** `_journal_file` is *"the ONLY
   key-derivation site"* and consumes the tenant-composite derivation unconditionally (`:665`–`:674`).
3. **Therefore the ambiguous-and-consequential set never grows**, and the disposal tool can empty it.
4. **Post-cutover, no *migration* flow acts on the distinction.** Disposal retains `CURRENT_FORMAT`
   unconditionally; adoption refuses it; §13.7 reports it as ordinary state.
   **⚠ CORRECTED at out-of-family round 2 [P1]: this bullet originally read *"nothing in the product
   acts on the distinction"*, which is FALSE.** Two shipped **tenant-facing** surfaces read
   current-format journals in steady state and are silently blind to it — see §3(vii), which is the
   single largest change review made to this filing and which **amends the recommendation** rather
   than merely annotating it.

**(ii) POST-UPGRADE FORENSICS ON ABANDONED ORPHANS.** The same §13.7 surface serves both phases —
there is no separate forensics surface. An operator can conclude *which* workflows were at risk
(term 3-ter's wrapper identity), *how many records* each holds, and that (3b) can still operate.
They **cannot** conclude whether any of them actually lost anything. The honest post-mortem sentence
is *"at most N workflows were at risk, named as follows; whether any actually lost state is
unknowable from here."* **That is a real ceiling on a real question** — and it is the strongest
demand-side point in the row's favour. It is also, at HEAD, a **one-shot** ceiling attached to a
dated event.

**(iii) DISPOSAL'S REFUSE-WHILE-RECOVERABLE.** Its safety **does** rest on over-estimating
recoverability, and the direction is **CONSERVATIVE** — see §3(v), which also records the
uncomfortable consequence that a discriminator would make disposal *more* aggressive, not safer.

**Stated against interest.** `[HIGH]` **(1)** The "frozen set" argument holds only until the **next**
keying change, which §14.14.8 explicitly contemplates: *"A future encoding change is a KEYING change
and MUST take this arc's fork path."* At that point the accumulated directory holds one journal per
workflow that has *ever* paused durably, and the upper bound over that set is close to vacuous. This
filing does not argue the gap away — it argues it is **not yet load-bearing**, and D-2 exists so the
row fires on exactly that event. **(2)** Like `B-98`, the resolution-knowledge argument assumes the
party performing the cutover is the party that ran the resumes. That holds at the design-time
`solo-developer` persona and fails at `team-binding` / `multi-tenant-compliance` (the committed
bridging arc, root `CLAUDE.md` §10.2) — which is why D-3 is a trigger rather than an argument.

### (ii) THE SENTINEL'S TWO SUB-DECISIONS — ONE IS FORCED BY SHIPPED CODE, THE OTHER IS SHARPER THAN THE ROW STATES `[HIGH]`

The row names two decisions under (a) and correctly refuses to let an impl leg settle them: *"whether
that sentinel is a `PauseSnapshot` at all, and … what the five-member cause vocabulary reports for a
resolved journal"* (`.harness/forward-register.yaml:3436`–`:3438`). **Grounding forces the first and
sharpens the second.**

**DECISION 1 IS FORCED — a `PauseSnapshot` sentinel is RESUMABLE.** `[HIGH]` `read_latest_attributed`
returns the latest record's parsed snapshot (`:646`–`:661`), and `read_latest` `:535` feeds
`resume()`. A sentinel that validates as a `PauseSnapshot` therefore becomes **resumable state** —
the harness would resume *from the marker*. There is no branch anywhere that would exclude it,
because no code knows the concept. **The sentinel MUST therefore be a wrapper-level record, not a
`PauseSnapshot`**, and that is not a preference — it is the only non-defective option. *This closes
the row's first sub-decision by falsification rather than by choice.*

**AND THE WRAPPER LAYER IS EXACTLY THE LAYER BOTH READERS ALREADY TREAT AS STORE-OWNED**, which is
the finding that makes (a) cheap on the read side. The record already has precisely two wrapper keys
(`:773`–`:776`), the enumeration already reads wrapper keys and only wrapper keys
(`_wrapper_workflow_id:322`–`:342`), and §13.7 term 4's boundary is stated as *"the EMBEDDED
SNAPSHOT, not the record"* (`Spec_Harness_Runtime_v1.md:1301`). **So the enumeration could read a
third wrapper key and report the journal resolved WITHOUT any term-4 amendment and without
deserializing anything.** `[HIGH]`

**DECISION 2 IS GENUINE — and the default outcome is worse than "unspecified".** `[HIGH]`
**Established by empirical probe at this HEAD, not by reading:**

```
wrapper-only sentinel  {"pause_resolved": true, "workflow_id": "wf-1"}
    -> (None, PauseJournalReadCause.CORRUPT_LATEST)
null-snapshot sentinel {"pause_snapshot": null, "workflow_id": "wf-1"}
    -> (None, PauseJournalReadCause.CORRUPT_LATEST)
```

`record["pause_snapshot"]` raises `KeyError`, which `:870` catches into `CORRUPT_LATEST` `:873`. And
`read_latest_attributed:658` then sets **`indeterminate=True`** for that cause. **So a cleanly
resolved journal would present to the operator as a corrupt record that may be an in-flight torn
append and is worth re-reading** — the single most misleading disposition in the five-member set.

**Consequence, stated precisely: shape (a) is NOT additive against the pinned vocabulary.** A sixth
member (or an explicit re-purposing) is **mandatory**, not optional, and it must carry its own
`retryable` / `indeterminate` dispositions. That is a `B-97`(a)-ratified surface — the vocabulary was
pinned at five *by that ratification* — so it is squarely an operator decision and not an impl one,
exactly as the row says. **The row is right that this decision exists; it under-states how bad the
no-decision default is.**

**AND THE SIXTH MEMBER FORCES A CROSS-AXIS OD LEG — a third cost neither the row nor this filing's
first draft named, and it is the round's single most consequential finding.** `[HIGH]` *(Surfaced at
out-of-family review round 1 [P1]; verified by direct read, and it **flips this filing's
runner-up** — §6.)* The five-value vocabulary exists **TWICE**, deliberately: `PauseJournalReadCause`
in `harness-runtime` (`journal_workflow_pause_store.py:107`) and `PauseStateCauseAttribution`
**independently re-declared** in `harness-od` (`pause_resume_namespace.py:482`–`:498`), because the
axis direction forbids OD importing Runtime. Its own docstring states the coupling as a contract:
*"any divergence from the Runtime-side enum fails the cross-surface identity witness the §30 contract
term requires"* (`:488`–`:489`). And the accessor converts **by value** at
`api.py:1163` — `PauseStateCauseAttribution(cause.value)` — a `StrEnum` lookup that **raises
`ValueError` on an unknown value**. **So a Runtime-only sixth member does not merely diverge; it
breaks the §C-OD-30.5 accessor audit emission** the `B-69` arc exists to guarantee, on the exact
read that encounters a resolved journal. **Reading A therefore owes an OD spec + plan leg too** — the
same U-OD-57-shaped obligation this filing charged only to Reading C.

**Hash disposition — the row's "hash-adjacent record" caution, checked.** `[MODERATE]` The store
computes no hash over the record: `_append` serializes and appends (`:773`–`:793`); the only digest
is the enumeration's `sha256` of the latest **raw line** (`pause_journal_enumeration.py:309`) and the
store's identical computation at `:645`. A sentinel appended after a snapshot changes what
`latest_record_digest` reports — which is *desirable* here (it is what makes a re-pause detectable)
but is a visible change to a value §13.7 term 3 declares. The `PauseSnapshot.snapshot_hash` that
`resume()` validates is computed **inside** the snapshot and is untouched by an appended
non-snapshot record. **So "hash-adjacent" is accurate but narrower than it sounds: no integrity hash
is invalidated; one reported diagnostic scalar changes meaning.**

### (iii) THE ROW'S HYPOTHESIZED THIRD SHAPE — "derive it from records the system already writes" — IS **FALSIFIED** `[HIGH]`

Before pricing a new write, the honest question is whether a successful resume already leaves a
durable trace with an identity joinable to a journal filename. **It does not.** The join key is
`pause_journal_filename(tenant_scope, workflow_id)` (`journal_workflow_pause_store.py:370`, over
`encode_pause_journal_key` `:320`) — **both components required**. Four sink families were walked:

| Sink | Durable write at successful resume | Joinable to a journal | Stock default |
|---|---|---|---|
| **IS state ledger** | **YES**, two writes — `emit_pause_resume_state_ledger_entry(... RESUME_ATTEMPTED)` (`harness-cp/src/harness_cp/workflow_driver.py:3216`) and the per-step entry (`:6003`, called `:5779`) | **NO.** `StateLedgerEntry` has **no `workflow_id` field** (`harness-is/src/harness_is/state_ledger_entry_schema.py:158`); the resume entry's `action_id` is the **constant** `"cp.pause-resume-protocol"` (`harness-cp/src/harness_cp/pause_resume_protocol.py:1025`), with the workflow only inside an unre-derivable sha256 preimage. The step entry *does* carry `workflow:{id}:step:{n}` (`workflow_driver.py:6020`) but **carries no tenant** and fires on every step of every run | YES |
| **OD audit ledger** | **NO.** `_project_resume_outcome_to_audit_payload` (`harness-od/src/harness_od/pause_resume_namespace.py:373`) has **zero production callers**; the CP §16.5 pause/resume composer emits zero audit entries by contract (`pause_resume_protocol.py:1080`–`:1081`) | n/a | writer yes, event no |
| **OD pre-bootstrap pause-state sink** | **NO.** Vocabulary **CLOSED at two** — `ACCESSOR_READ`, `STALENESS_REFUSED_RESUME` (`pause_resume_namespace.py:501`–`:512`). The precondition emits **only on the refusal branch** | *would* be partial — `workflow_id` cleartext `:553`, **no tenant field** | yes |
| **Adoption account / WAL / reconciler / engine-output / OTel** | **NO** on resume. The adoption account is written by an **operator CLI**, never by a resume (`pause_journal_adoption.py:771`–`:805`); engine-output is **default opt-out**; OTel exports over gRPC, not to a file | n/a | n/a |

**Bottom line: there is no derive-from-existing-records shape.** `[HIGH]` The failure is a clean
split: the one record that is **resume-specific** carries no re-derivable identity (and fires before
the success test, `workflow_driver.py:3216` preceding `:3229`), while the records that carry a
cleartext `workflow_id` are neither resume-specific nor **tenant**-qualified. Under `B-97`'s own
premise topology — two differently-tenanted deployments sharing one resolved `STATE_LEDGER` dir — a
resume by tenant *A* would read as a resolution of tenant *B*'s journal, and **a false "resolved" is
the dangerous direction**: it is precisely the false all-clear the §14.14.8 failure-mode asymmetry
exists to prevent.

**What grounding put in its place is a genuinely different shape the row does not name.** The
**nearest miss is one enum member wide**: the OD pre-bootstrap pause-state sink is already durable,
already `fsync`-ed with the journal's own torn-append hardening
(`pre_bootstrap_pause_state_sink.py:86`–`:115`), already co-located under `STATE_LEDGER`, already
admin-reachable as a plain file, and already keyed on a cleartext `workflow_id`. It records
pause-state *reads* and staleness *refusals*, but **not** a successful resume. Adding that event is a
**new capture-side write into an EXISTING sink** rather than a new artifact — which is a materially
different cost profile from both (a) and (b). It is carried forward as **Reading C** (§4), with its
tenant defect priced rather than hidden.

### (iv) (b)'s "SECOND AUTHORITY" PRICING IS WEAKER THAN THE ROW STATES — conceded AGAINST this filing's runner-up `[HIGH]`

The row rejects (b) because a marker file *"adds a second authority over one journal's state, the
exact defect the no-fallback-read rule exists to prevent"*
(`.harness/forward-register.yaml:3439`–`:3440`). **Two corrections, and the first runs against this
filing's own preference ordering.**

**Correction 1 — the journal is not a FIRST authority over the question a marker would answer.**
The no-fallback-read rule (`journal_workflow_pause_store.py:668`–`:672`) forbids a **second read
path for the same key** — a fallback that would *"fail open at exactly the boundary being built"*.
A resolved-marker answers a question the journal **cannot answer at all**; it is the first and only
authority over an unanswered question, not a competing answer to an answered one. **Invoking the
no-fallback-read rule here is a category slide, and this filing records it as such even though it
weakens (b)'s rival.**

**Correction 2 — the real hazard is narrower, and it has a clean mechanical answer that is already
specified in-house.** The genuine second-authority risk is **divergence over time**: a workflow that
pauses, resumes, and pauses *again* leaves a stale "resolved" marker beside a genuinely outstanding
journal — the **false all-clear** direction. That is closable without a mutable marker, by keying the
marker row on the **occurrence** it resolved rather than on the workflow — and the correct
composition is not a fresh design decision but the shipped §30 staleness token's, reproduced at
§3(vi). **This is not a property unique to (b): §3(vi) establishes it as a requirement common to all
three build readings**, which is why the row's framing of (b) as uniquely exposed to a
state-divergence defect does not survive.

**And the artifact class already has TWO in-house precedents, which reprices (b) downward.**

- **The adoption account** — `pause-journal-adoption-account.jsonl` (`pause_journal_adoption.py:142`),
  a durable append-only JSONL artifact **beside** the journal directory (`:138`–`:141`), keyed by
  journal filename, with fsync + directory-fsync + write-ahead intent rows. It carries an explicit
  **`K-17` determination** that **no OD-owned carrier is owed** for such an account (`:171`–`:203`),
  on four grounded reasons — no existing OD namespace admits it; the emission machinery is
  unreachable from a stopped harness (§13.5 row 5); §13.7 declared the same absence; declaring one
  would be an X-AL-3 violation. **That determination is directly reusable rationale for (b)**, and it
  is the single largest cost the row implicitly assumes (b) would pay and that it would not.
- **`B-96`'s Reading C sidecar** — an out-of-band observation-state record for the SIBLING protected
  result store (`.harness/class_2_fork_b96_gc_grace_elapsed_time_bound.md:260`–`:287`). **Its round-6
  [P1] finding transfers, and the transfer is FAVOURABLE here.** `B-96` withdrew its fate-sharing
  claim against interest: *"A selective backup/restore, a dotfile-skipping copy, or an operator
  cleanup that preserves `*.entry` while dropping the sidecar leaves every payload and no observation
  timestamp"* (`:327`–`:335`). **The same non-fate-sharing holds for a B-104 marker — but the loss
  direction is opposite.** In `B-96`, sidecar loss lengthens retention indefinitely (a real if benign
  defect). **Here, marker loss degrades exactly to the status quo: the journal reads as outstanding,
  the bound reverts to today's upper bound, and the operator over-estimates.** That is the
  conservative direction and it is the same direction the whole surface already fails in.

**Noted without depending on it** `[MODERATE]`: `B-96`'s Reading C is **unratified**, and this
filing takes no position on it. If ratified it would establish a second live sidecar for the sibling
store and narrow (b)'s novelty further; if declined on the fate-sharing ground, that ground is
weaker here for the reason just given. **Either outcome leaves this filing's ordering unchanged**,
which is why the interaction is recorded rather than leaned on.

### (v) A DISCRIMINATOR *ENABLES* DISPOSAL TO BECOME MORE AGGRESSIVE — a question every build reading must ANSWER, not a cost it must PAY `[HIGH]`

Disposal's safety today rests on **over-estimating recoverability**, by construction. Its refusal
predicate keys on **format**, never on liveness:

```python
orphans = [journal for journal in journals if journal.adoptable]        # :97
targets = orphans                                                       # :168
if orphans and not args.acknowledge_discarding_recoverable_state:       # :202
    ... return _EXIT_REFUSED
```

A `LEGACY` journal whose pause was resolved months ago still returns `adoptable=True`, still enters
`orphans`, and still trips the refusal. The module states the identity outright: *"The orphan class
and the (3b)-recoverable class are THE SAME SET"* (`:79`–`:84`). **Every misclassification runs in
the retain direction** — unreadable identity, `NOT_ATTRIBUTABLE` co-tenant journals, and
resolved-but-legacy journals are all retained (`:164`–`:167`). The module records that the *inverse*
predicate was a round-1 [P1] bug and would have been the unsafe direction (`:86`–`:93`).

**So the honest consequence of ANY of (a)/(b)/(c):** the delete set stays `LEGACY`-only (retention at
`:164`–`:168` is unconditional and no flag widens it), but the **acknowledgement gate at `:202`
would be re-keyed** from *"orphans exist"* to *"outstanding orphans exist"*. A directory whose legacy
journals are all resolved would then satisfy `--delete` with **no acknowledgement**, and the tool
would unlink files it presently refuses to touch. Architecturally that is *correct* — a resolved
journal holds nothing to recover — but it converts a **universally-firing brake into a conditional
one**, and it moves the failure mode of a wrong discriminator from *retention* to *deletion*.

**Scoped honestly, and corrected against this filing's own recommendation.** `[HIGH]` *(Out-of-family
review round 1 [P2], upheld.)* An earlier draft called this a **mandatory build cost** and used it as
a fourth argument for deferral. **That over-stated it and biased the recommendation.** Re-keying is
**not** forced by any of A/B/C — the gate is a separate, independently decidable predicate, and
§9 presents *"stay format-keyed"* as an explicit and perfectly coherent option (a resolved journal is
still a *legacy* journal, and refusing to delete it is still safe). So the correct statement is:
**the discrimination makes a more aggressive disposal POSSIBLE, and every build reading therefore owes
an explicit decision on whether the gate re-keys.** That is an obligation the row does not name, and
it is a real one — but it is **not** a reason to prefer D, and this filing no longer counts it as
one.

---

### (vi) EVERY BUILD READING NEEDS AN OCCURRENCE KEY — and its composition is ALREADY DECIDED IN-HOUSE `[HIGH]`

*(Surfaced as three separate out-of-family round-1 [P1]s — one against each build reading — and
absorbed here as ONE finding, because they are one defect wearing three costumes.)*

**The defect.** A resolution recorded against a *workflow* is stale the moment that workflow pauses
again. All three build readings were drafted keyed on workflow identity (plus, for C, a tenant), and
**all three therefore admit a FALSE ALL-CLEAR** — the dangerous direction, and the exact direction
§14.14.8's failure-mode asymmetry argument exists to foreclose:

| Reading | The concrete race |
|---|---|
| **A** | The resume→sentinel sequence is **not atomic**. `_append`'s lock serializes *appends*, nothing more (`journal_workflow_pause_store.py:687`). A concurrent `capture()` landing between the resume's read and the sentinel's append leaves the **sentinel as the latest record over a genuinely outstanding pause**. *This falsifies this filing's own "no staleness window exists by construction" claim for A, which was its principal advantage over B.* |
| **B** | A marker keyed on `latest_record_digest` alone still matches if a subsequent capture happens to write **identical bytes** |
| **C** | An event carrying `(tenant, workflow_id)` cannot say *which* pause it resolved; the next pause inherits the old resolution |

**The composition is not an open design question.** `[HIGH]` The shipped §30 staleness token solves
precisely this problem and states why: it *"folds the journal's **record count** together with a
digest of its **latest raw record line**"*, sound **because** *"no path in the store rewrites,
truncates, compacts, rotates, prunes or removes a previously-appended record, so the record count is
monotonically non-decreasing and increments on every `capture()`"*
(`pause_state_staleness.py:17`–`:27`). It explicitly rejects `snapshot_hash` as fail-open (*"two
successive LINEAR pauses at the same `step_index` hash IDENTICALLY"*, `:10`–`:12`) and
`(snapshot_hash, created_at)` as a luck argument (`:13`–`:15`). **Digest alone is exactly the
insufficiency that module was written to name.**

**Consequences, and they redistribute the cost between readings rather than adding to all three
equally:**

- **A must become a COMPARE-AND-APPEND**: under `_append`'s existing lock, verify the journal's
  record count and latest digest still equal the ones the resume read, and refuse the sentinel
  otherwise. Cheap — the lock is already held and both scalars are already computed at `:645`/`:659`
  — but it is **engineering, not construction**, which is the claim this filing had to withdraw.
- **B must key its marker rows on `(record_count, latest_record_digest)`**, not the digest alone. Also
  cheap: the enumeration already computes both (`pause_journal_enumeration.py:299`–`:319`).
- **C must carry an occurrence key on an OD-owned payload**, on top of the tenant qualifier it already
  needed — **compounding** its OD leg rather than adding a separate one.
- **And B inherits one cross-surface obligation the others do not**: the store computes its digest
  over `str.splitlines()` (`journal_workflow_pause_store.py:634`, `:645`) while the enumeration uses
  `bytes.splitlines()` (`pause_journal_enumeration.py:299`, `:309`), which select different latest
  lines for a journal containing a raw `\x0b`, `\x85` or `U+2028` — the divergence the row's own
  `notes` field records. Store-written journals cannot contain those (`ensure_ascii` defaults `True`
  at `:777`), so the two agree for everything the product writes; but **B joins a store-side write to
  an enumeration-side read through that scalar**, so it owes **ONE pinned raw-byte computation as a
  contract term** rather than two coincidentally-agreeing ones. *(Round 1 [P2]: the earlier claim
  that the `notes` divergence was "unengaged by every reading" was true for A/C/D and false for B.)*

**AND THE OCCURRENCE KEY IS UNAVAILABLE ON ONE OF THE TWO RESUME BRANCHES — a scope limit every
build reading owes explicitly.** `[HIGH]` *(Out-of-family round 3 [P1], verified.)* `resume()` accepts
**exactly one of** `pause_snapshot` or `resume_handle` (`api.py:1272`). Only the `resume_handle`
branch reads the journal (`:1321`); the `pause_snapshot` branch takes the caller's snapshot directly
at `:1338`–`:1340` and **never opens the journal at all** — so at the moment of a successful resume
there is **no observed `(record_count, latest_record_digest)` to bind a resolution to**, even though
the pause it resolves may well have been durably journaled. Each build reading must therefore choose,
and **state**, one of:

- **(α) bind by a fresh read** — perform a journal read at resolution time purely to obtain the
  occurrence key (cheap for A, which is already at the store; a new read for B and C); or
- **(β) scope out** — record resolutions only for `resume_handle` resumes and **declare that
  snapshot-supplied durable resumes remain ambiguous**, which keeps the bound honest but leaves a
  named hole.

**What is NOT acceptable is (γ): emitting an occurrence-unbound resolution**, which reintroduces the
false all-clear this whole finding exists to close. *An impl leg choosing silently between α and β is
how a bound comes to be trusted for a case it never covered.*

**The net effect on the ordering is small but real**: A loses a structural advantage and gains an
engineering obligation; B gains two cheap ones; C compounds an expensive one; and **all three inherit
the α/β decision**.

---

### (vii) THE AMBIGUITY IS **NOT** CONFINED TO THE LEGACY SET — two shipped tenant-facing surfaces are silently blind to it, and **only Reading A can serve them** `[HIGH]`

*(Surfaced at out-of-family review round 2 [P1]; verified by direct read. It **falsifies §3(i)
bullet 4 as first written** and is the reason §4's Reading D now carries a mandatory declaration
component and §6's runner-up moved a second time.)*

**The mechanism.** Two public surfaces read the journal in steady state, on **current-format**
journals, through one shared helper:

| Surface | Path |
|---|---|
| `read_paused_workflow_state(workflow, resume_handle, config)` | `api.py:925` → `_read_durable_pause_snapshot` `:1036` |
| `resume(workflow, resume_handle=...)` | `api.py:1321` → the same helper |
| the shared helper | `_read_durable_pause_snapshot` `:775`, deliberately shared *"[by] the `resume_handle` path AND the §14.14.9 accessor, so the two surfaces cannot"* diverge (`:812`), returning `store.read_latest_attributed(...)` `:820` |

Because a successful resume writes nothing, **the latest record remains the resolved pause**. So in a
**fresh process after a crash — the exact scenario the `B-69` accessor was built for, where the
caller holds no `RunResult`** — `read_paused_workflow_state` reports a resolved pause as the current
one with no indicator, and a `resume(resume_handle=...)` against it re-enters that snapshot.

**Scoped honestly, and NOT over-claimed.** `[MODERATE]` This is **not** demonstrated to be a
correctness loss: a re-entered resume re-executes from the pause point with already-captured effects
fenced by the store's no-replace publication, and a caller passing `resume_handle` is *asserting* an
intent to resume rather than being told the pause is live. **What IS established at `[HIGH]` is a
DISCLOSURE ASYMMETRY**: the identical limit was made **explicit contract text** on the admin surface
— §13.7 term 3-bis, *"writes NO pause-resolved marker … byte-indistinguishable"*
(`Spec_Harness_Runtime_v1.md:1299`) — and is **nowhere declared on the tenant-facing read path**.
§14.14.8's latest-record-only paragraphs (`:5922`, `:5979`) state that the read never walks
*backward*; **neither states that the latest record may itself be already resolved.** A grep for
*"already resumed"* / *"after a successful resume"* / *"resolved pause"* across the Runtime spec
returns the limit **only** at `:1296` and `:1302` — both inside §13.7.

**AND THIS RE-ORDERS THE BUILD READINGS — but by COST AND NEW MECHANISM, not by contract
exclusion.** `[MODERATE]` *(Scoped at out-of-family round 3 [P1], which caught this section
contradicting §3(iv) of this same filing — the exclusivity claim below originally read "only A can,
because the no-fallback rule forbids the others", while §3(iv) correction 1 had already established
that the no-fallback rule governs an alternate read path for the SAME key answering the SAME
question, which companion resolution state is not. **The reviewer is right and the stronger claim is
WITHDRAWN.**)*

| Reading | Closes the §13.7 enumeration bound? | Closes the §14.14.9 accessor / `resume()` blindness? |
|---|---|---|
| **A** (sentinel in the journal) | **YES** — the enumeration reads it at the wrapper layer | **YES, AT ZERO NEW READ.** The fact lands *in* the record the single-authority latest-record read already opens (`read_latest_attributed:570`–`:661`) |
| **B** (marker file) | **YES** | **POSSIBLE, but it is a NEW MECHANISM.** A per-journal sibling path is **not** enumeration, so §13.7 term 7 does not forbid it — but the runtime read would have to open a **second file per read** and the spec leg would owe an explicit second-read term plus a disposition for *"marker unreadable"* (fail-open would be the false all-clear; fail-closed would deny a resumable pause on an unrelated I/O error). **Not free, and not merely a docstring** |
| **C** (OD sink event) | **YES** | **EFFECTIVELY NO.** The sink is a **single shared multi-workflow file** (`pause-state-audit/events.jsonl`) whose only retrieval surface is `read_all()` (`pre_bootstrap_pause_state_sink.py:152`) — a whole-file scan on every runtime read, which is the enumeration-shaped access term 7 exists to keep off that path |

**So the two demands are served differently, and the operator's choice depends on which they mean to
serve.** An operator who wants only a tighter cutover bound should prefer **B** on cost. An operator
who wants the accessor to stop reporting resolved pauses as current should prefer **A**, not because
B is forbidden there but because **A closes it with no new read, no new failure mode and no new spec
term, while B closes it only by acquiring all three.** *This is the structural fact the row's
two-candidate framing obscures — and it is a cost gradient, not a prohibition.*

---

## §4 The readings

### Reading A — a wrapper-level RESOLVED SENTINEL RECORD appended at successful resume

- **Shape.** At a successful resume, append one record to the same journal carrying the store-owned
  wrapper `workflow_id` plus a resolution key — **and NOT a `pause_snapshot`**, which §3(ii) forces.
- **Vocabulary.** **A SIXTH `PauseJournalReadCause` member is MANDATORY**, with its own
  `retryable=False`, `indeterminate=False` disposition. Without it a resolved journal reports
  `corrupt-latest` + `indeterminate=True` — an actively wrong, retry-inviting diagnosis (§3(ii),
  empirically probed). **This is the ratified-surface decision the row correctly refuses to let an
  impl leg settle**: the five-member closure is a `B-97`(a) gate-2 ratified property.
- **AND AN OD SPEC + PLAN LEG IS OWED** *(round 1 [P1] — this was absent from the first draft and it
  is A's largest single cost)*. `harness-od` re-declares the same five values independently
  (`pause_resume_namespace.py:482`–`:498`) and the accessor converts by value at `api.py:1163`, where
  an unknown value raises `ValueError` and breaks the §C-OD-30.5 audit emission (§3(ii)).
- **Read side.** One added wrapper-key read in `_wrapper_workflow_id`'s sibling; **no term-4
  amendment**, because the wrapper is already the permitted layer (`Spec_Harness_Runtime_v1.md:1301`;
  `pause_journal_enumeration.py:323`–`:327`). One added `EnumeratedJournal` field.
- **Against the append-only invariant.** Cheapest available — an append rewrites and truncates
  nothing, so §14.14.8's substrate invariant is satisfied by construction rather than argued around.
  **This remains A's one genuinely uncontested advantage.**
- **Occurrence binding — ENGINEERED, not structural** *(round 1 [P1]; the first draft's
  "self-invalidating by construction" claim is WITHDRAWN)*. A re-pause *after* the sentinel is
  self-detecting, but a `capture()` landing between the resume's read and the sentinel's append makes
  the sentinel latest over a live pause. A must **compare-and-append** under the existing lock
  against the count and digest the resume observed (§3(vi)).
- **Costs.** (1) The vocabulary decision. (2) **The OD leg.** (3) The compare-and-append. (4) It
  changes what `latest_record_digest` reports for a resolved journal — desirable but contract-visible
  under §13.7 term 3. (5) It puts a write on the **resume success path**, which today writes nothing
  to the store; the write must be ordered so a crash between resume-commit and sentinel-append leaves
  the journal reading *outstanding* (the conservative direction), not resolved.
- **Does NOT need.** Any new file, any new artifact class, any second read authority.

### Reading B — an out-of-band per-journal MARKER FILE

- **Shape.** A durable append-only artifact beside the journal directory (the adoption-account
  placement, `pause_journal_adoption.py:138`–`:142`), each row carrying the journal filename plus the
  **`(record_count, latest_record_digest)` pair** it resolved — the §30 staleness token's own
  composition (§3(vi)), not the digest alone.
- **Record shape untouched, AND NO OD LEG IS OWED.** The journal's two-key wrapper, the **five-member
  vocabulary**, the read path, `§30`'s cause table and OD's mirrored `PauseStateCauseAttribution` are
  **all byte-unchanged** — B never mints a cause, so the cross-axis coupling that costs A an OD leg
  (§3(ii)) does not arise. The marker is read only by the admin-tier §13.7 surface, running against a
  stopped harness, which is exactly the class the adoption account's `K-17` determination already
  cleared as owing no OD carrier (`pause_journal_adoption.py:171`–`:203`). **This is B's largest
  advantage and it emerged only at review.** **⚠ But `K-17` is NOT dispositive for B, and treating it
  as such under-prices B** *(round 3 [P2], upheld)*: two of `K-17`'s four grounds do not transfer —
  ground 2 turns on *"admin binaries run against a STOPPED harness"* while **B writes during a LIVE
  resume**, and ground 1 turns on the event being outside the OD `pause.*` / `resume.*` family, which
  is exactly the family Reading C places this same event *inside*. **B may well still owe no OD leg —
  it mints no cause, widens no OD payload and emits no OD event — but that requires ITS OWN
  determination at the spec leg, on B's own facts, not an inherited one.**
- **Second-authority pricing, corrected.** Weaker than the row states (§3(iv), correction 1) and
  mechanically closable (correction 2), with two in-house precedents.
- **Costs, and they are the honest ones.** (1) **Non-fate-sharing** with the journal (`B-96` round-6
  [P1]) — though loss degrades to today's upper bound, the conservative direction. (2) Occurrence
  binding is **engineered** rather than structural — but so is A's, after §3(vi). (3) **ONE PINNED
  RAW-BYTE DIGEST COMPUTATION is owed as a contract term**, because B joins a store-side write to an
  enumeration-side read through a scalar the two surfaces currently compute with `str.splitlines()`
  and `bytes.splitlines()` respectively (§3(vi)). (4) The §13.7 canonical-name filter must be
  **witnessed** to exclude it — it already would (`CANONICAL_JOURNAL_NAME_PATTERN`,
  `pause_journal_enumeration.py:61`, `<64hex>.jsonl` exactly), but the exclusion becomes a contract
  term, exactly as term 1 already requires for the lock files and adoption write-asides
  (`Spec_Harness_Runtime_v1.md:1296`). (5) One more artifact an operator's backup procedure must know
  about.

### Reading C — a RESUME-RESOLVED event in the EXISTING OD §C-OD-30.5 pause-state sink

*The shape grounding produced in place of the falsified derive-from-existing-records option
(§3(iii)). It is a **new capture-side write**, but into an **existing** durable sink, not a new
artifact.*

- **Shape.** A third `PauseStateEventKind` member emitted at successful resume, landing in
  `<STATE_LEDGER>/pause-state-audit/events.jsonl` via `PreBootstrapPauseStateSink.emit`
  (`pre_bootstrap_pause_state_sink.py:83`). §13.7 correlates by `workflow_id`.
- **Buys.** Zero interaction with the journal record shape, the five-member vocabulary, the
  append-only invariant, and `latest_record_digest`. The sink shares the journal's `PathResolver`
  resolution (`:173`–`:192`), *"for the same reason (a fresh process must find what a prior process
  wrote)"* (`:16`–`:17`).
- **Costs, and they are the largest of the three.**
  1. **AN OD SPEC + PLAN LEG IS OWED.** `PauseStateEventKind` is an OD-owned schema surface
     (§C-OD-30.5); the `B-69` leg established that such a change owes an OD spec **and** plan delta
     with its own unit (U-OD-57) — the precedent the adoption tool's own `K-17` determination cites
     (`pause_journal_adoption.py:196`–`:199`). A Runtime unit cannot author it.
  2. **`PauseStateAuditPayload` is `extra="forbid"` + `frozen` with an outcome-split
     `model_validator`** (`pause_resume_namespace.py:548`, `:588`). A third kind must be given a row
     in that split table; it is not a bare enum append.
  3. **THE TENANT DEFECT.** The payload carries `workflow_id` and **no tenant field** (`:553`); the
     journal address is `(tenant_scope, workflow_id)`. Under `B-97`'s own shared-`STATE_LEDGER`
     premise, tenant *A*'s resume would mark tenant *B*'s journal resolved — **a false all-clear**.
  4. **AND AN OCCURRENCE KEY ON TOP OF THAT** *(round 1 [P1])*. A tenant qualifier alone does **not**
     close the false all-clear: a resume followed by a re-pause leaves an event with the identical
     `(tenant, workflow_id)` as the new outstanding state. C needs `(record_count,
     latest_record_digest)` — or the staleness token — **as further OD-owned payload fields**, so
     costs 3 and 4 **compound into one enlarged OD leg** rather than adding separately (§3(vi)).
  5. **THE SINK'S DURABILITY IS NOT THE JOURNAL'S** *(round 1 [P2]; the first draft's claim that it
     "already carries the journal's own hardening" is WITHDRAWN)*. `emit()` takes **no cross-process
     lock**, and its two directory fsyncs are **CONDITIONAL** — `if is_new_file:` `:112` and
     `if dir_is_new:` `:114` — which is precisely the flag-gated shape the journal's `_append`
     docstring argues at length is unsound, *"because the flags are process-local and the crash they
     guard against is another process's"* (`journal_workflow_pause_store.py:703`–`:731`). Under the
     multi-process topology C would be serving, that hardening is **work C owes**, not work it
     inherits.
- **Verdict.** Correct in kind, **most expensive by a widening margin**, and the only reading that can
  be wrong in the dangerous direction on two independent axes. Recorded because it is the only shape
  that touches neither the journal nor a new file — a property an operator may weigh differently than
  this filing does.

### Reading D — DECLARE the limit symmetrically, then DEFER the discriminator

*Amended at out-of-family round 2 [P1]: D was drafted as a pure deferral. §3(vii) makes a pure
deferral **untenable**, because the limit is contract text on one surface and undeclared on the two
tenant-facing surfaces that share it. **The declaration is therefore a MANDATORY component of D, not
an optional companion** — and it is precisely the move this arc already made once, at §13.7 term
3-bis, when it chose to "scope the claim honestly rather than patch".*

**Component 1 — DECLARE (mandatory, spec text only, zero code).** A term on the §14.14.9 accessor /
§30 read path, symmetric with §13.7 term 3-bis: *the latest durable record may itself be an
already-resolved pause; the read reports the latest record, not a liveness claim.* This costs one
spec paragraph plus a docstring on **BOTH** affected public surfaces — `read_paused_workflow_state`
(`api.py:925`) **and `resume()` (`api.py:1170`), whose `resume_handle` parameter documentation
(`:1197`, `:1223`) is separately consulted and would otherwise leave that caller unwarned** *(round 3
[P2]: an earlier draft scheduled only the accessor's docstring, which would have disclosed the limit
on the weaker of the two surfaces and left it undisclosed on the one that actually executes)*. It
closes the `[HIGH]` half of §3(vii) — the disclosure asymmetry — without building any discriminator.
**It does not close the blindness; it stops the blindness being undisclosed**, which is the same
trade the row itself already accepted for the enumeration.

**Component 2 — DEFER the discriminator**, keep `status: registered_finding`, amend the `close_out`
with §3's grounding, and record a **falsifiable** demand test — **four disjuncts, any one fires**:

- **D-0 — A RETENTION / PRUNING POLICY ARC OPENS. *(Dominant.)*** §14.14.8 states *"A retention
  POLICY — a default, a tunable, a sweep trigger — is a FOLLOW-ON ARC and is explicitly NOT owed
  here"* (`pause_journal_disposal.py:14`–`:17`). **A pruner is UNBUILDABLE without this
  discriminator**: it cannot be permitted to reclaim an outstanding pause, and format-keying gives it
  nothing — post-cutover every journal is `CURRENT_FORMAT`. This is the sharpest trigger and it
  dominates the other three, because it is the one condition under which the absence becomes a hard
  blocker rather than a ceiling.
- **D-1 — ANY SURFACE BRANCHES ON LIVENESS, or a stale re-resume is OBSERVED.**
  *(Re-scoped at round 2 [P2]. The first form — "a second flow acts on the distinction for a
  current-format journal" — was **already satisfied at HEAD** by §3(vii) and would have made the
  trigger vacuous on the day it was written.)* Two disjuncts, both checkable: **(a)** any code path
  makes a control-flow decision conditioned on whether a durable pause is outstanding (as opposed to
  merely *reading the latest record and being blind to it*, which is HEAD's shipped behaviour and is
  what Component 1 declares); **or (b)** an operator-loop report of a `resume(resume_handle=...)`
  re-entering an already-resolved snapshot in a fresh process. *The harm class, not the asymmetry —
  the asymmetry is discharged by Component 1.*
- **D-2 — A SECOND KEYING CHANGE IS OPENED.** §14.14.8 contemplates one (*"A future encoding change
  is a KEYING change and MUST take this arc's fork path"*). It re-runs the whole (3a)/(3b) cutover
  over an accumulated directory holding one journal per workflow that ever paused — where the upper
  bound approaches vacuity. *This is §3(i)'s own against-interest point, promoted to a trigger.*
- **D-3 — THE RESUMER CEASES TO BE THE PARTY PERFORMING THE CUTOVER.** The workspace advances past
  `solo-developer` on the committed bridging arc (root `CLAUDE.md` §10.2), so the operator confirming
  a drain is not the party who ran the `resume()` calls and cannot supply the confirmation
  out-of-band. *Same shape as `B-98`'s D-1(b), and it is the same premise.*

**Explicitly NOT a trigger on its own:** the §13.7 listing merely being loose. That is the row's
already-disclosed, already-contract-stated condition (term 3-bis) and is what the
`UPPER_BOUND_DISCLAIMER` exists to communicate.

---

## §5 The row's decisions — one collapses, one is confirmed and sharpened, and THREE are not in the row

| Decision | Disposition after grounding |
|---|---|
| **(a)-1 — is the sentinel a `PauseSnapshot`?** | **FORCED, not decided. NO.** A valid `PauseSnapshot` sentinel is **resumable** — the harness would resume from the marker (§3(ii)). The only non-defective form is a wrapper-level record, which is also the layer both readers already treat as store-owned |
| **(a)-2 — what does the five-member vocabulary report?** | **CONFIRMED GENUINE, and the no-decision default is worse than "unspecified":** `corrupt-latest` **with `indeterminate=True`** — an in-flight-torn-append diagnosis for a cleanly resolved journal (empirically probed). A **sixth member is MANDATORY** under A, and the five-member closure is a `B-97`(a)-ratified property, so this is squarely an operator decision |
| **(b) — the second-authority objection** | **WEAKER THAN STATED** (conceded against this filing's original ordering): the journal is not a first authority over a question it cannot answer, and the divergence hazard is not unique to (b) — §3(vi) makes it common to all three (§3(iv)) |
| **— NOT IN THE ROW (1): the sixth cause member forces a CROSS-AXIS OD LEG** | `harness-od` re-declares the vocabulary independently and the accessor converts by value; an unknown value raises. **This is what makes A more expensive than B, and it inverted this filing's runner-up** (§3(ii), §6) |
| **— NOT IN THE ROW (2): every build reading needs an OCCURRENCE KEY** | Workflow-keyed resolution admits a **false all-clear** on re-pause, in all three shapes. The composition is not open — the shipped §30 staleness token already pins `(record_count, latest_record_digest)` and says why the digest alone fails (§3(vi)) |
| **— NOT IN THE ROW (3): does disposal's acknowledgement gate re-key?** | **A QUESTION EVERY BUILD READING MUST ANSWER — not a cost it must pay.** A discriminator *enables* converting a universally-firing brake into a conditional one; staying format-keyed is a coherent option. Owed as an explicit decision, **not** an argument for D (§3(v)) |

---

## §6 Recommendation — **Reading D (DECLARE + DEFER)**, runner-up **A**, and AGAINST **C** on cost

`[MODERATE]` **Recommend D — in its round-2-amended form, where Component 1's symmetric declaration
is mandatory.** A pure deferral is no longer defensible (§3(vii)); a deferral that first makes the
limit visible on the surfaces that carry it is.

1. **The demand gate answers NO for the flows that would ACT on the distinction — but only after
   §3(vii) narrows what that means.** `[HIGH]` Every consumer that *branches* on the distinction is
   `LEGACY`-scoped, and **no code path creates a legacy journal after the cutover**
   (`journal_workflow_pause_store.py:674`), so the ambiguous-and-consequential set is **frozen,
   one-time, and drainable by the shipped disposal tool**. **What §3(vii) establishes is different
   and must not be blurred into this:** two tenant-facing surfaces are *blind* to the distinction in
   steady state — they do not consume it, they silently assume it. **Blindness that is DECLARED is a
   scoped limit; blindness that is UNDECLARED is a defect.** Component 1 converts the second into the
   first at the cost of one spec paragraph, which is exactly the trade §13.7 term 3-bis already made
   for the enumeration. **D-0** then exists so the row fires the moment a retention policy makes the
   absence a hard blocker rather than a declared ceiling.
2. **The confirmation gap is real, permanent, and NOT closed by this recommendation.** `[HIGH]` The
   listing is monotone non-decreasing under a perfect drain; only the zero case self-confirms; the
   spec already states this as contract text (`:5944`). **This filing does not claim the gap is
   imaginary** — it claims the party who *performed* the resolutions holds the confirmation
   out-of-band at the current persona tier, exactly as `B-98`'s webhook argument runs, and that D-3
   is the trigger for when that stops being true.
3. **Every build reading is MORE expensive than the row prices it, and the increase is cross-axis.**
   `[HIGH]` Grounding added an obligation to each: A owes an **OD spec + plan leg** it appeared not to
   (§3(ii)) plus a compare-and-append; B owes a pinned digest computation; C compounds its OD leg
   twice over. **All three also owe an occurrence key** (§3(vi)). None of this makes the readings
   wrong — it makes the row's implicit "small capture-side change" framing wrong.
4. **The row's own gate language is satisfied honestly.** *"A marker bought for a need nobody has is
   a capture-side change against a hash-adjacent record for nothing."* Grounding finds the need is
   **held by exactly one dated flow whose set is drainable**, so the gate's own test returns
   defer — and the gate is now falsifiable rather than a judgement.
5. **Additivity means no reading gets more EXPENSIVE by waiting** — for A, a sixth vocabulary member
   and a wrapper key are both additive against journals written without them (an old journal simply
   never carries the sentinel and reads outstanding, the conservative direction); for B, a marker file
   is a new artifact whose absence is today's behaviour. **But waiting is NOT cost-free, and the
   distinction matters** *(round 2 [P2], upheld)*: **every pause resolved during the deferral leaves
   no durable trace, and no later implementation can backfill it.** Journals that pass through the
   deferral window stay permanently ambiguous, so the accumulated ambiguity a future pruner or keying
   migration inherits is strictly monotone in the deferral's length. **This is a real cost of D and
   is counted as one**, not argued away — it is bounded only by how long D lasts, which is what makes
   D-0's dominance load-bearing.

**NOT counted as a reason for D, and withdrawn from an earlier draft:** the disposal-brake argument.
§3(v) records that re-keying is **not** forced by any build reading, so the false-deletion risk is
not inherent to A/B/C and must not be scored against them *(round 1 [P2], upheld — the draft's fourth
point was biasing the recommendation toward its own conclusion)*.

**Runner-up: A — and this element MOVED TWICE, on two different grounds. Both moves are recorded
as moves, and the element is now at the `[[reviewer-oscillation-register-and-hold]]` two-of-three
mark.** `[MODERATE]`

| Round | Ground | Effect |
|---|---|---|
| **Draft** | A self-invalidates by construction; A needs no OD leg | A > B |
| **Round 1 [P1] ×2** | **Both premises FALSIFIED** — the resume→sentinel sequence is not atomic (§3(vi)); the sixth cause member breaks OD's independently re-declared mirror at `api.py:1163`, so **A owes an OD leg and B owes none** (§3(ii)) | **B > A** on cost |
| **Round 2 [P1]** | **A NEW, ORTHOGONAL ground: reach, not cost.** §3(vii) — a steady-state surface is blind to the distinction, and A closes it where B does not | **A > B** on reach |
| **Round 3 [P1]** | **The reach ground WEAKENED, not reversed.** B is **not contract-forbidden** from the runtime read (the exclusivity claim contradicted this filing's own §3(iv) and is withdrawn); it is only more expensive there — a second per-read file open, a new failure mode, a new spec term | **A > B narrowly**, on a cost gradient rather than a prohibition |

**THE ELEMENT IS HELD HERE.** `[HIGH]` Three movements on one element is
`[[reviewer-oscillation-register-and-hold]]`'s stop signal, and this is the third. **The filing
therefore presents the ordering CONDITIONALLY and routes the adjudication to the ratification (and,
under A, to the §7 convening) rather than patching it a fourth time.** Two things bound the risk, and
neither is a claim that the movement was harmless: round 1's cost finding **is not withdrawn** (A
really does owe an OD leg B does not), and round 3 **weakened rather than reversed** round 2 — the
sequence is *A → B → A → A-narrowly*, a converging refinement onto a finer partition, not an
oscillation between two stable poles.

**The honest ordering is therefore conditional rather than absolute:**

- **If the operator's demand is a tighter CUTOVER BOUND → B**, on cost. It is sufficient, cheapest,
  and owes no cross-axis leg.
- **If the operator's demand is that the ACCESSOR stop reporting resolved pauses as current → A**,
  which reaches that surface at **zero new read**; B reaches it only by acquiring a second per-read
  file open, an unreadable-marker disposition and a new spec term (§3(vii)). A's OD leg is the price
  of reach, not waste.
- **A is named the runner-up, narrowly**, because §3(vii)'s surface is *steady-state* while the
  cutover bound is *one-shot*, and a shape that serves both at lower marginal mechanism dominates one
  that serves the smaller and more perishable demand.

**Stated against this ordering, and this is the HELD disagreement rather than a rhetorical
concession:** if the operator judges §3(vii)'s harm adequately discharged by Component 1's
declaration alone — defensible, since the harm is `[MODERATE]`, effects are fenced, and no consuming
surface exists — then A's reach buys nothing, **B is cheaper on every remaining axis, and B is the
correct runner-up.** Round 3 narrowed the gap far enough that this filing does not claim to settle
it; **the ratification does.**

**Recommend AGAINST C.** `[HIGH]` Not on kind — it is architecturally the cleanest, touching neither
the journal nor a new file — but on **cost plus a defect the others lack**: it owes a full OD spec +
plan leg with its own unit (the U-OD-57 precedent), a row in a `frozen` payload's outcome-split
validator, **and** a tenant qualifier on an OD-owned payload without which tenant *A*'s resume marks
tenant *B*'s journal resolved. **That last is a false all-clear** — the exact failure direction
§14.14.8's asymmetry argument exists to foreclose — so C is not a smaller change wearing a larger
costume; it is the largest change, and the only one that can be wrong in the dangerous direction.

**§6.1 Stated against interest.** `[HIGH]` **(1)** D leaves a real, permanent, contract-acknowledged
ceiling in place on the one question post-upgrade forensics exists to answer — *"did this cutover
actually lose anything?"* — and **no surface in the product can answer it, individually or in
aggregate.** The honest operator sentence remains *"at most N were at risk; whether any lost state is
unknowable from here."* **(2)** The frozen-set argument that carries point 1 has a **dated
expiry**: §14.14.8 itself contemplates a future keying change, and at that point the accumulated
directory approaches "every workflow that ever paused" and the bound approaches vacuity — which is
why D-2 is a trigger rather than an argument. **(3)** The out-of-band-confirmation argument rests on
the same unstated premise `B-98` records and the committed persona arc will eventually break, which
is why D-3 exists. **(4)** The strongest single fact *against* D is that §3(ii)'s cross-axis coupling
means the absence is not costless to leave: OD's mirrored vocabulary is already load-bearing, so the
longer the sixth member waits the more surfaces bind to a five that was pinned for a different
reason. **This filing does not claim the gap is imaginary — it claims that at HEAD the consequential
set is frozen and drainable, every reading is additively closeable at any time, and no demand signal
accompanies it.**

---

## §7 Council position — **PROBE-RESOLVED for D; CONVENE, dyadic, ONLY if the operator selects A**

The row's `council` field is already **conditional**: *"convene only if shape (a) is taken, since
that is where the closed-vocabulary and record-shape questions bite; a pure documentation close needs
no convening"* (`.harness/forward-register.yaml:3455`–`:3459`), on a named **C3 ⊥ C11** tension —
state/persistence integrity wanting the record shape and append-only invariant left alone, against
operator-loop wanting an answerable *"is anything actually outstanding"*. Per CLAUDE.md §10.9
amendment 5 a probe was run before taking a position, and per
`[[probe-resolves-fork-prescribed-council]]` the row's prescription is not binding on the result.

**What the probe resolved.** `[HIGH]` Two facts, each empirical. **(1)** The record-shape half of
C3's position is **decided by shipped code, not by preference**: a `PauseSnapshot` sentinel is
resumable, so the only available form is a wrapper-level record — there is nothing for C3 and C11 to
disagree about on that sub-decision (§3(ii)). **(2)** C11's operator-loop case is **narrower than the
row assumes**: at HEAD no post-cutover flow consumes the distinction, and the flow that does is
one-shot over a drainable set (§3(i)). So under D the two voices are not in tension — C3 gets the
record untouched and C11 loses nothing they can currently act on.

**What the probe did NOT resolve.** `[MODERATE]` The **sixth-cause-member** question is genuinely
contested inside Reading A, and it is exactly C3's ground: the five-member closure is a `B-97`(a)
gate-2 ratified property, and re-opening it to add a member with `retryable=False` /
`indeterminate=False` semantics is a persistence-contract change, while C11 needs *some* honest
disposition because the default (`corrupt-latest` + `indeterminate=True`) actively misleads. **That
is a real disagreement with a real stake**, and it only exists under A.

- **If the operator selects D → NO convening owed.** Probe-resolved.
- **If the operator selects A → a dyadic C3 ⊥ C11 convening is OWED before the spec leg**, scoped to
  the sixth-member question (name, semantics, `retryable`/`indeterminate` dispositions) **and to its
  cross-axis leg** — §3(ii) makes the member an OD-visible change, not a Runtime-local one, which
  raises rather than lowers C3's stake. Not decorative: this is the live decision.
- **If the operator selects B → NO convening owed on the record shape** (B does not touch it, nor
  OD's mirror), but the §3(v) disposal-brake question still needs an answer at the spec leg; route to
  **C11** directly plus `advisor()`.
- **If the operator selects C → a convening is owed with C7 or C8 added**, since C introduces an
  OD-owned schema surface plus a disclosure/tenant question the C3 ⊥ C11 pair does not cover, and
  §3(vi) enlarges the payload further.
- **Under D, the convening is additionally owed at D-0** — a retention policy makes the tension live
  by making the absence a blocker.

This **narrows the row's conditional** (from *"convene if (a)"* to *"convene if (a), on one named
sub-decision; route B and C differently"*) rather than reversing it, and is recorded as a narrowing.

---

## §8 The ratification ask — ONE decision, four options

**PRIMARY.**

> **Does `B-104` resolve as D (DECLARE + DEFER: **Component 1**, a MANDATORY spec term on the
> §14.14.9 / §30 read path declaring that the latest durable record may itself be an already-resolved
> pause — symmetric with §13.7 term 3-bis, spec text only, zero code, closing the disclosure
> asymmetry §3(vii) found; **Component 2**, defer the discriminator, amend the `close_out` with §3's
> grounding, record the FOUR-disjunct demand test **D-0 / D-1 / D-2 / D-3** — D-0, a
> retention/pruning-policy arc, being dominant because a pruner is unbuildable without the
> discriminator — and keep `status: registered_finding`) — or as A (a WRAPPER-LEVEL resolved sentinel appended at successful resume
> under a COMPARE-AND-APPEND, introducing no new artifact, but **requiring a SIXTH
> `PauseJournalReadCause` member** — which re-opens a `B-97`(a)-ratified five-member closure **AND
> forces a cross-axis OD spec + plan leg**, because `harness-od` re-declares the same vocabulary and
> the accessor converts by value) — or as B (an out-of-band per-journal marker file beside the journal
> directory, keyed on `(record_count, latest_record_digest)`, leaving the record shape, the read path,
> §30's cause table and OD's mirrored vocabulary **all byte-unchanged and owing NO OD leg**, at the
> cost of a non-fate-sharing artifact plus one pinned raw-byte digest computation) — or as C (a third
> `PauseStateEventKind` in the EXISTING OD §C-OD-30.5 pause-state sink, touching neither the journal
> nor a new file, at the cost of a full OD spec + plan leg carrying **both** a tenant qualifier and an
> occurrence key — without which one tenant's resume, or one earlier resume, marks a live journal
> resolved — plus the cross-process locking and unconditional dirent hardening that sink does not
> have)?**
>
> **Note carried into the decision (§3(vii)):** **A closes the `read_paused_workflow_state` /
> `resume(resume_handle=...)` blindness at zero new read; B can close it only by acquiring a second
> per-read file open, an unreadable-marker disposition and a new spec term; C effectively cannot (its
> sink's only retrieval surface is a whole-file scan).** This is a cost gradient, **not** a contract
> prohibition — an earlier draft claimed the latter and it was withdrawn at round 3.
>
> **Carried by A, B and C alike:** the **α/β decision** for the `pause_snapshot` resume branch, which
> reads no journal and therefore offers no occurrence key (`api.py:1338`–`:1340`) — bind by a fresh
> read, or scope out and declare snapshot-supplied durable resumes ambiguous. **Never γ (an
> occurrence-unbound resolution).**

**Recommended: D (in its amended, declaration-carrying form).** **Runner-up: A, narrowly and HELD**
*(this element moved three times — B at round 1 on cost, A at round 2 on reach, A-narrowly at round 3
when the reach ground weakened; per `[[reviewer-oscillation-register-and-hold]]` it is registered and
held rather than patched a fourth time, and the A-vs-B adjudication is the operator's; §6)*.
**Recommended against: C on cost.**

**Carried by any answer, requiring no separate decision:**

- **The `close_out` is AMENDED** to record: (a) that the row's hypothesized derive-from-existing
  option is **FALSIFIED**, with the two precise missing links (no resume-specific record carries a
  re-derivable identity; no identity-bearing record is tenant-qualified) and the near-miss named as
  Reading C rather than left as an unexplored possibility; (b) that sub-decision (a)-1 is **FORCED,
  not open** — a `PauseSnapshot` sentinel is resumable; (c) that sub-decision (a)-2 is **confirmed
  genuine and its default is worse than unspecified** — `corrupt-latest` + `indeterminate=True`,
  empirically probed; (d) that the **second-authority objection to (b) does not hold as written**,
  with the category slide named and the two in-house precedents (the adoption account's reusable
  `K-17` determination; `B-96` Reading C's round-6 fate-sharing withdrawal, whose loss direction is
  **conservative** here) recorded; (e) that the ambiguous-and-consequential set is **frozen,
  one-time and drainable** because every consumer is `LEGACY`-scoped and no path creates a legacy
  journal post-cutover; (f) the **NOT-IN-THE-ROW cross-axis cost** — the sixth cause member forces an
  **OD spec + plan leg**, because `harness-od` re-declares the vocabulary independently
  (`pause_resume_namespace.py:482`–`:498`) and `api.py:1163` converts by value, so a Runtime-only
  member breaks the §C-OD-30.5 accessor emission; (g) the **NOT-IN-THE-ROW occurrence-key
  requirement** common to all three build readings, with the composition pinned to the shipped §30
  staleness token's `(record_count, latest_record_digest)` rather than left open; and (h) that any
  build reading **may** re-key disposal's acknowledgement gate from unconditional to conditional —
  an explicit decision each owes, **not** an automatic consequence and **not** an argument for
  deferral; and (i) **the §3(vii) SCOPE CORRECTION** — the ambiguity is **NOT** confined to the
  legacy set: `read_paused_workflow_state` (`api.py:925`) and `resume(resume_handle=...)` (`:1321`)
  share `_read_durable_pause_snapshot` (`:775`) and report an already-resolved pause as the current
  one in steady state, with the limit being **contract text at §13.7 term 3-bis and UNDECLARED on
  both of them** — and that **only Reading A can close it**, the runtime read being single-authority
  by contract.
- **Under D, Component 1's declaration is NOT optional** and must be recorded on the row as owed, or
  the ratification lands a pure deferral §3(vii) has already falsified.
- **The full demand test — D-0, D-1, D-2 AND D-3 — is recorded on the row**, with D-0 marked
  dominant and **D-1 in its round-2 re-scoped form** (a surface *branching* on liveness, or an
  observed stale re-resume). *(A retention-policy arc is the one condition that turns the ceiling
  into a blocker; a register trigger omitting it would fail to reopen the row for the arc it most
  matters to. And D-1's FIRST form was already satisfied at HEAD by §3(vii), which would have made
  the trigger vacuous the day it was written.)*
- **The `council` field is NARROWED** from *"convene only if shape (a)"* to §7's per-reading form
  (A → dyadic C3 ⊥ C11 scoped to the sixth member + the disposal brake; B → C11 + `advisor()`, no
  convening; C → convening **plus** C7/C8; D → none, plus one owed at D-0).
- **PR #1170's scope is recorded correctly on the row**: it was a **strings-only** self-description
  refresh (78/16, zero logic), which removed a *phantom* blocker on the drain recourse and left this
  one untouched — so the row must not be read as having been narrowed by it.

---

## §9 Sequencing, and what each leg owes

**Chain: this filing → ratification (+ the §7 convening under A, or A-shaped under C) → spec leg
(A / B / C only) → impl leg.**

| Leg | Owed under **D** | Owed under **A** | Owed under **B** | Owed under **C** |
|---|---|---|---|---|
| **Ratification** | operator answer; row `pr:`; `close_out` amended per §8; `council` narrowed; `status` stays `registered_finding` | operator answer; `pr:`; **the §7 dyadic C3 ⊥ C11 scoped to the sixth cause member + the §3(v) disposal brake**; then `status: open` | operator answer; `pr:`; no convening; the §3(v) disposal-brake answer deferred to the spec leg; `status: open` | operator answer; `pr:`; **convening with C7 or C8 added** (OD-owned schema + tenant/disclosure); `status: open` |
| **Spec leg** | **COMPONENT 1 IS OWED** — a §14.14.9 / §30 term declaring that the latest durable record may itself be an already-resolved pause, symmetric with §13.7 term 3-bis, plus the matching docstrings on **BOTH** public surfaces (`read_paused_workflow_state` `api.py:925` **and** `resume()` `:1170`/`:1223`). **Spec text + two docstrings; zero code, zero contract numbers, zero hash impact.** No other design extension | Runtime §14.14.8 record-shape term for the wrapper-level sentinel + **§30's cause table amended to SIX** with the new member's `retryable`/`indeterminate` dispositions (`Spec_Harness_Runtime_v1.md:3351`) + §13.7 term 3 amended for the added `EnumeratedJournal` field and the changed `latest_record_digest` semantics + term 3-bis **narrowed, not deleted** — **PLUS an OD spec + plan delta mirroring the sixth value into `PauseStateCauseAttribution`** (§3(ii)) | Runtime §14.14.8 marker-artifact term (placement, `(count, digest)` keying, durability, **ONE pinned raw-byte digest computation**) + §13.7 term 1's canonical-name exclusion extended to it as a **witnessed contract term** + term 3-bis narrowed. **Record shape, §30, the five-member vocabulary AND OD's mirror PRESERVED VERBATIM; NO OD leg** | **OD spec + plan delta with its own unit** (U-OD-57 precedent) for the third `PauseStateEventKind`, its outcome-split row, **a tenant qualifier AND an occurrence key on `PauseStateAuditPayload`** + the sink's cross-process locking and unconditional dirent terms + Runtime §13.7 correlation term + term 3-bis narrowed |
| **Impl leg** | none | wrapper-level **compare-and-append** on the resume success path under `_append`'s existing lock, **ordered so a crash leaves the journal reading OUTSTANDING**; the sixth cause member wired through `_parse_snapshot_attributed`, `read_latest_attributed:658`'s indeterminacy routing **and OD's mirror**; the enumeration's added wrapper-key read; **a mutation-probe witness** that removing the sixth member reproduces the probed `corrupt-latest` + `indeterminate=True` misdiagnosis; **a witness that a `capture()` interleaved between the resume's read and the sentinel append is REFUSED, not overwritten** | `(count, digest)`-keyed marker rows with the store's own fsync + dirent + torn-append hardening; the §13.7 exclusion **witnessed, not assumed**; a witness that a journal grown past the recorded pair reads outstanding again — **including the identical-bytes case, where the digest alone would still match** | the sink emission + payload widening + tenant qualifier + occurrence key + the sink's own locking/dirent hardening; a witness that a co-tenant resume does **NOT** mark another tenant's journal resolved, **and** that a re-pause after a recorded resolution does not |
| **Disposal brake (§3(v))** | untouched | **explicit decision owed at the spec leg** — does `:202`'s gate re-key to *"outstanding orphans"*, or deliberately stay format-keyed? Either is coherent; the silence is not | same | same |
| **The α/β decision (§3(vi))** | n/a | **owed at the spec leg** — the `pause_snapshot` branch (`api.py:1338`–`:1340`) reads no journal, so bind by a fresh read (α) or scope out and DECLARE snapshot-supplied durable resumes ambiguous (β). **Never γ** | same | same |
| **OD determination** | n/a | **OWED — an OD spec + plan delta** mirroring the sixth cause value (§3(ii)) | **OWED as a DETERMINATION, not assumed** — `K-17` does not transfer (B writes during a live resume; the event sits in the OD `resume.*` family), so B must make its own on its own facts (round 3 [P2]) | **OWED — the largest**, carrying the event kind, the outcome-split row, the tenant qualifier and the occurrence key |
| **Row disposition** | stays `registered_finding` with a **falsifiable** trigger; re-check on **D-0** (dominant) / D-1 / D-2 / D-3 | closes at the impl leg | closes at the impl leg | closes at the impl leg |

**Not owed by any leg, explicitly:** re-opening `B-97`(a)'s ratified path segregation, (3a)
abandon-by-default, or the migration contract; re-opening `B-97`(b)'s append-lock construction;
adding a **fallback read** to the store (`journal_workflow_pause_store.py:668`–`:672` forbids it and
nothing here needs it); adding enumeration to the tenant-facing runtime read path (§13.7 term 7,
`Spec_Harness_Runtime_v1.md:1304`); a retention/pruning policy (§14.14.8 declares it a follow-on arc,
and D-0 is precisely its trigger); and any dependence on `B-96`'s unratified outcome.

**Priority note, carried to the ratification rather than decided here.** `[MODERATE]` If the operator
wants the operator-loop win at lowest total cost, the **cheapest actionable improvement is not in any
of these readings**: it is that the drain recourse has **no `resume` operator surface at all** (§2 —
seven CLI commands, none of them resume), so *"drive pauses to resolution"* is available only to the
embedding application. A resolution surface would make the drain half executable end-to-end, at which
point the confirmation half is what remains. **This filing does not recommend opening that** — it
records that the two are ordered and that the register does not currently say so.

---

## §10 Cite re-verification at HEAD `e1a2e7fb`, and review record

**Code cites — all re-resolved by direct read at this HEAD.**
`harness-runtime/src/harness_runtime/lifecycle/journal_workflow_pause_store.py`: `:3`–`:8` the
survivability rationale ✓ · `:107` `PauseJournalReadCause` (`:120`/`:142`/`:157`/`:164`/`:182`) ✓ ·
`:209` `PauseJournalReadResult` (the `:214`/`:256` invariant prose) ✓ · `:320` / `:370` / `:384` the
three key derivations ✓ · `:498` the store · `:531`/`:535`/`:548` the public surface ✓ · `:645` the
latest-line digest ✓ · `:658` the `CORRUPT_LATEST` indeterminacy routing ✓ · `:665`–`:674`
`_journal_file`, the sole derivation site + the no-fallback-read rule at `:668`–`:672` ✓ · `:689`
`_append` (record `:773`–`:776`, serialization `:777`, the locked section `:787`–`:798`) ✓ ·
`:841`–`:873` `_parse_snapshot_attributed` (`:858` mismatch, `:859` the validate, `:870`–`:873` the
catch) ✓.
`harness-runtime/src/harness_runtime/admin/pause_journal_enumeration.py`: `:61`
`CANONICAL_JOURNAL_NAME_PATTERN` ✓ · `:66`–`:77` the `B-104`-naming docstring + `UPPER_BOUND_DISCLAIMER` ✓ ·
`:80`–`:114` `JournalIdentityClass` (3 members) ✓ · `:117`–`:156` `EnumeratedJournal` (5 fields) ✓ ·
`:167`–`:189` `identity_actionable` / `adoptable` ✓ · `:299`–`:319` the raw-bytes scalars ✓ ·
`:322`–`:342` `_wrapper_workflow_id` + its term-4 boundary note at `:323`–`:327` ✓.
`harness-runtime/src/harness_runtime/admin/pause_journal_disposal.py`: `:7`–`:12` the orphan
statement ✓ · `:14`–`:17` the retention-policy follow-on declaration ✓ · `:79`–`:84` *"THE SAME
SET"* ✓ · `:86`–`:93` the round-1 inverse-predicate correction ✓ · `:97`/`:98` orphans/retained ✓ ·
`:164`–`:168` the unconditional retention ✓ · `:178` dry-run-first ✓ · `:202`–`:211` the refusal ✓.
`harness-runtime/src/harness_runtime/admin/pause_journal_adoption.py`: `:138`–`:142`
`DEFAULT_ACCOUNT_FILENAME` + the beside-not-inside placement ✓ · `:154`–`:203` `AdoptionDisposition`
(7 members) + the **`K-17` no-OD-carrier determination**, four grounds `:180`–`:199` ✓ · `:771`–`:805`
the CLI `main` ✓.
`harness-runtime/src/harness_runtime/lifecycle/pre_bootstrap_pause_state_sink.py`: `:16`–`:17` the
same-resolution rationale ✓ · `:57`/`:60`/`:63` the sink location ✓ · `:68` the class · `:83` `emit` ·
**`:112` / `:114` the two CONDITIONAL dirent fsyncs, and the absence of any cross-process lock** ✓
*(round 1 [P2])* · **`:152`–`:170` `read_all`, the sink's ONLY retrieval surface — a whole-file scan**
✓ *(round 3 [P1])* · `:173`–`:192` `pause_state_sink_for` ✓.
`harness-runtime/src/harness_runtime/lifecycle/pause_state_staleness.py`: `:1`–`:32` the token as a
PROPERTY; `:10`–`:12` the `snapshot_hash` fail-open rejection; `:13`–`:15` the `(snapshot_hash,
created_at)` luck rejection; **`:17`–`:27` the chosen `(record_count, latest-raw-line digest)`
composition and its append-only soundness argument** ✓ *(round 1 [P1])*.
`harness-od/src/harness_od/pause_resume_namespace.py`: `:373` `_project_resume_outcome_to_audit_payload`
(zero production callers) ✓ · **`:482`–`:498` `PauseStateCauseAttribution` — the independently
re-declared FIVE, with the no-import rationale at `:486`–`:487` and the cross-surface-identity
contract term at `:488`–`:489`** ✓ *(round 1 [P1])* · `:501`–`:512` `PauseStateEventKind` (2 members) ✓ ·
`:515`–`:586` `PauseStateAuditPayload` (`:548` `extra="forbid"`+`frozen`; 9 fields; `:553`
`workflow_id`; **no tenant field**) ✓ · `:588` the outcome-split validator ✓.
`harness-runtime/src/harness_runtime/api.py`: **`:775`–`:820` `_read_durable_pause_snapshot`, the
shared helper (`:812` the "so the two surfaces cannot" diverge comment, `:820` the delegation to
`read_latest_attributed`)** ✓ *(round 2 [P1])* · `:925`–`:1036` `read_paused_workflow_state` (`:944`–`:953`
the strict-subset-of-`resume()` rationale, `:948` the re-pause note, `:1036` the helper call) ✓ ·
**`:1156`–`:1167` the accessor's sink emission, `:1163` `PauseStateCauseAttribution(cause.value)` —
the by-value conversion that raises on an unknown member** ✓ *(round 1 [P1])* · `:1170` `resume()`,
`:1197` / `:1223` the `resume_handle` parameter documentation ✓ *(round 3 [P2])* · `:1257`–`:1264` the
one-way drain refusal ✓ · `:1272` the exactly-one-of guard ✓ · `:1314`–`:1337` the handle branch
(`:1321` the journal read) ✓ · **`:1338`–`:1340` the `pause_snapshot` branch, which opens NO journal**
✓ *(round 3 [P1])* · `:1345`–`:1350` the workflow-mismatch refusal ✓.
`harness-runtime/src/harness_runtime/cli/app.py`: `:247`/`:584`/`:639`/`:663`/`:686`/`:728`/`:755` —
seven commands, **no `resume`** ✓.
`harness-runtime/src/harness_runtime/admin/inspect.py:946`–`:983` the §13.7 engagement ✓.
`harness-cp/src/harness_cp/workflow_driver.py`: `:3216` the `RESUME_ATTEMPTED` emission, `:3229` the
success test it precedes ✓ · `:6003`/`:6020` the step-ledger entry + its `action_id` shape ✓.
`harness-cp/src/harness_cp/pause_resume_protocol.py`: `:1025` the constant `action_id` ✓ ·
`:1080`–`:1081` the zero-audit-entry contract ✓.
`harness-is/src/harness_is/state_ledger_entry_schema.py:158` — `StateLedgerEntry`, **no `workflow_id`
field** ✓.

**Spec cites — all re-resolved at this HEAD.** `Spec_Harness_Runtime_v1.md:1` head **v1.109** ✓
(matches root `CLAUDE.md` §2.3 — probed for pointer drift per
`[[wrong-version-read-delta-only-baseline]]`, **none found**) · `:35` change-note (D) ✓ · `:43` the
*"findings surfaced, NOT patched"* block ✓ · `:1288` §13.7 heading, `:1292` the precondition
rationale + the *"second leg"* sentence, `:1294`–`:1304` the seven-term table (`:1296` term 1,
`:1299` **term 3-bis, byte-verified**, `:1300` term 3-ter, `:1301` term 4, `:1304` term 7) ✓ ·
`:1306` §13.7.1 ✓ · `:3351` §30 `C-RT-35` ✓ · `:5901` §14.14.8 ✓ · `:5944` the *"drain, then verify
against a bound you can see"* concession ✓ · `:5981` the append-only invariant statement ✓.
`.harness/forward-register.yaml:3396`–`:3460` the `B-104` row (`:3436`–`:3438` the two sub-decisions;
`:3439`–`:3440` the second-authority objection; `:3441`–`:3443` the self-imposed grounding gate;
`:3445`–`:3454` the dated re-check; `:3455`–`:3459` the conditional council) ✓.
`.harness/post-phase-8-forward-register.md:1116` the prose heading ✓.
`.harness/class_2_fork_b96_gc_grace_elapsed_time_bound.md:260`–`:287` Reading C's common terms,
`:327`–`:335` the round-6 fate-sharing withdrawal ✓.
`git show 07b3e04b` — PR #1170, `shutdown_cli.py` **+78/−16, docstring/help/message only, zero logic
change**, self-stated in the diff ✓.

**Counts, recounted programmatically at this filing** *(re-run after round 1)*.
`PauseJournalReadCause` members **5** · `PauseStateCauseAttribution` members **5** (**the same five
values, declared twice**) · `PauseStateEventKind` members **2** · `PauseStateAuditPayload` fields
**9**, tenant fields **0**, occurrence-key fields **0** ·
`JournalIdentityClass` members **3** · `EnumeratedJournal` fields **5** · `AdoptionDisposition`
members **7** · CLI commands **7**, named `resume` **0** · store removal/truncation/rewrite call
sites **0** (`unlink` 0 · `os.remove` 0 · `shutil.rmtree` 0 · write-mode `open` 0; the two `truncate`
substring hits are prose at `:214`/`:256`) · journal wrapper keys **2** · readings **4**, viable
**4**, recommended **1** · demand-test disjuncts **4** · grounding findings **7** · `resume()` snapshot
sources **2**, of which journal-reading **1** (`api.py:1314` vs `:1338`) · public surfaces sharing
`_read_durable_pause_snapshot` **2** · out-of-family rounds **3**, findings **13**, upheld **13**,
absorbed against this filing's interest **3**.

**Empirical probe (the one behavioural claim not settled by reading).** Both candidate sentinel
shapes were passed to the shipped `JournalWorkflowPauseStore._parse_snapshot_attributed` at this
HEAD; both returned `(None, PauseJournalReadCause.CORRUPT_LATEST)`, which `read_latest_attributed:658`
routes to `indeterminate=True`. *This is the finding that turns the row's second sub-decision from
"unspecified" into "actively wrong by default", and it is the reason §3(ii) is stated as forced
rather than as an argument.*

**Findings recorded, not absorbed.** (a) The `B-104` row's `notes` field carries an O-3 lens-1
observation about `str.splitlines()` vs `bytes.splitlines()` divergence, scoped as *"a bound on the
enumeration's arithmetic under HAND-EDITED or foreign-written journals, not as a live defect"*
(`.harness/forward-register.yaml:3399`–`:3412`). **Confirmed unchanged, and confirmed UNENGAGED by
A, C and D** — none alters `ensure_ascii`, and A's wrapper record would be serialized by the same
`json.dumps(record, sort_keys=True)` at `:777`. **It IS engaged by B** *(round 1 [P2] — an earlier
draft said "every reading", which was false for exactly one)*, which joins the two surfaces through
that scalar; absorbed as B's pinned-computation cost at §3(vi) and §9, and still **not** re-registered
as a live defect. (b) The absence of any `resume` operator surface (§9's priority note) is an
observation about the drain recourse's *first* half; it is recorded on the row's cross-ref, not
opened here.

### §10.1 Out-of-family review — `just codex-review-uncommitted`

**Round 1 — four [P1] + three [P2], ALL UPHELD by direct verification, and one of them FLIPPED the
runner-up.**

- **[P1] "Add the OD schema leg required by Reading A" — UPHELD, and it is the round's real yield.**
  Verified: `harness-od` re-declares the five-value cause vocabulary independently at
  `pause_resume_namespace.py:482`–`:498` (with the axis-direction rationale stated in its own
  docstring), and the accessor converts by value at `api.py:1163`, where an unknown member raises
  `ValueError` and breaks the §C-OD-30.5 emission. **The draft's claim that A needs "no OD leg" was
  simply wrong**, and it was one of the three claims ranking A above B. Absorbed as a new sub-finding
  at §3(ii), a cost line in §4 Reading A, a §5 row, §6's runner-up table, §8's option text and §9's
  spec/impl cells — **and it inverted the runner-up from A to B**, recorded as a reversal at §6
  rather than presented as refinement.
- **[P1] "Bind Reading A's sentinel to the resumed record" — UPHELD.** `_append`'s lock serializes
  appends only; the resume→sentinel sequence is not atomic, so an interleaved `capture()` leaves the
  sentinel latest over a live pause. **This falsified A's "no staleness window exists by
  construction" claim** — its second ranking advantage over B. Absorbed into the new §3(vi).
- **[P1] "Include record count in Reading B's marker key" — UPHELD, and the fix was already
  specified in-house.** `pause_state_staleness.py:17`–`:27` states the `(record_count, latest-line
  digest)` composition **and** why digest-alone and hash-alone fail. Absorbed into §3(vi) and B's
  shape.
- **[P1] "Bind Reading C's event to a specific pause record" — UPHELD.** A tenant qualifier alone
  does not close C's false all-clear; a re-pause inherits the old resolution. Absorbed as C's cost 4,
  compounding rather than adding to its OD leg.
  *These three [P1]s are one defect in three costumes and are absorbed as a single finding (§3(vi)),
  which is also what makes their differential effect on the ordering visible.*
- **[P2] "Account for concurrency in Reading C's sink" — UPHELD.** `PreBootstrapPauseStateSink.emit`
  takes no cross-process lock and its dirent fsyncs are **conditional** (`:112`, `:114`) — the exact
  flag-gated shape the journal's `_append` docstring argues is unsound (`:703`–`:731`). The draft's
  "already carries the journal's own durability hardening" is **withdrawn**; absorbed as C's cost 5.
- **[P2] "Canonicalize Reading B's cross-surface digest" — UPHELD as a SCOPE correction.** The
  `notes`-field splitlines divergence is unengaged by A/C/D and **engaged by B**, which joins a
  store-side write to an enumeration-side read through that scalar. Absorbed as B's pinned-computation
  cost and as a correction to §10's "findings recorded" note.
- **[P2] "Do not treat disposal re-keying as mandatory" — UPHELD, and it was biasing the
  recommendation.** §6 called re-keying a *"mandatory build cost"* while §9 simultaneously offered
  *"stay format-keyed"* as an option — an internal contradiction that scored a false-deletion risk
  against A/B/C. **Absorbed by re-titling §3(v), rewriting its close, and DELETING the argument from
  §6's numbered points**, with the withdrawal stated explicitly.

**Net effect of round 1 on the disposition.** `[HIGH]` **The recommendation (D) did NOT move**, and
four of the seven findings strengthen it by raising every build reading's price. **The runner-up DID
move, A → B, on a falsified premise rather than a preference.** One finding (the disposal-brake [P2])
ran *against* D and was absorbed against interest by removing a point from §6.

**Round 2 — one [P1] + one [P2], both UPHELD; the [P1] is the strongest finding of the review and it
AMENDED the recommendation.**

- **[P1] "Account for existing current-format pause consumers" — UPHELD, and it falsified this
  filing's central containment claim.** Verified by direct read: `read_paused_workflow_state`
  (`api.py:925`) and `resume(resume_handle=...)` (`:1321`) both reach
  `_read_durable_pause_snapshot` (`:775` → `store.read_latest_attributed` `:820`), which the helper's
  own comment says is shared *"[by] the `resume_handle` path AND the §14.14.9 accessor, so the two
  surfaces cannot"* diverge (`:812`). Since a successful resume writes nothing, both report the
  resolved pause as current — **in steady state, on current-format journals**, which §3(i) bullet 4
  claimed nothing did. Absorbed as the new **§3(vii)**, a correction stamped into §3(i) bullet 4
  itself, a **mandatory declaration component added to Reading D**, a re-scoped **D-1** (its first
  form was already satisfied and therefore vacuous), §6 point 1, §8 and §9's spec-leg cell.
  **Two things were NOT conceded on the reviewer's framing, and are recorded as scope limits:**
  (1) *"duplicate workflow execution"* is not established — already-captured effects are fenced by
  the store's no-replace publication, so the harm is priced `[MODERATE]`, not as a proven correctness
  loss; and (2) the finding does **not** show a surface *consuming* the distinction, only surfaces
  *blind* to it — which is why the absorbed disposition is a **declaration** (making the blindness a
  scoped limit, the trade §13.7 term 3-bis already made) rather than a build.
  **And it re-ordered the readings on a NEW axis**: because the runtime read is single-authority by
  contract (§13.7 term 7; the no-fallback rule at `journal_workflow_pause_store.py:668`–`:672`),
  **only A can close this surface** — which moved the runner-up B → A on *reach* without withdrawing
  round 1's *cost* finding. **Both moves are recorded at §6; the element is at two of the three-flip
  cap and is HELD there.**
- **[P2] "Do not treat deferral as cost-free" — UPHELD.** §6 point 5 argued additivity implied no
  cost to waiting. Additivity means no reading becomes more *expensive*; it does not mean nothing is
  *lost*. Every pause resolved during the deferral leaves no durable trace and **cannot be
  backfilled**, so the ambiguity a future pruner or keying migration inherits grows monotonically
  with the deferral's length. Absorbed by rewriting point 5 to count it as a real cost of D and
  tying it to D-0's dominance.

**Round 3 — two [P1] + two [P2], all UPHELD; ZERO against the disposition, and one is a
SELF-CONSISTENCY defect this filing introduced at round 2.**

- **[P1] "Re-evaluate the claim that only A can serve runtime reads" — UPHELD, and it caught this
  filing contradicting ITSELF.** §3(iv) correction 1 had established (against this filing's own
  runner-up, at round 0) that the no-fallback-read rule governs *an alternate read path for the same
  key answering the same question*, which companion resolution state is not. §3(vii) then invoked
  that same rule to declare B **structurally** admin-only. **Both cannot be true, and §3(iv) is the
  correct half.** A per-journal sibling path is not enumeration, so §13.7 term 7 does not forbid the
  runtime read consulting a marker. **The exclusivity claim is WITHDRAWN** and replaced with the
  honest cost gradient: A reaches the surface at **zero new read**; B reaches it by acquiring a
  second per-read file open, an unreadable-marker disposition (fail-open = the false all-clear;
  fail-closed = denying a resumable pause on an unrelated I/O error) and a new spec term; C
  effectively cannot, because its sink's only retrieval surface is a **whole-file scan**
  (`pre_bootstrap_pause_state_sink.py:152`) — enumeration-shaped access on the one path term 7 keeps
  it off. Absorbed at §3(vii)'s table and prose, §6's ordering, §8's carried note. **This WEAKENED
  round 2's ground without reversing it, which is the third movement on that element and the reason
  §6 now HOLDS it** rather than patching again.
- **[P1] "Cover the caller-supplied snapshot resume path" — UPHELD, verified at
  `api.py:1338`–`:1340`.** `resume()` takes exactly one of `pause_snapshot` / `resume_handle`
  (`:1272`); only the handle branch reads the journal (`:1321`). The snapshot branch assigns the
  caller's object directly and **never opens the journal**, so no occurrence key exists at resolution
  time — leaving every build reading free to silently emit an unbound resolution, which is precisely
  the false all-clear §3(vi) exists to close. Absorbed as an explicit **α / β / never-γ** decision
  owed by all three readings, at §3(vi), §8's carried note and a new §9 row.
- **[P2] "Make a B-specific OD emission determination" — UPHELD as a SCOPE correction.** `K-17`'s
  grounds do not all transfer: ground 2 turns on admin binaries running against a **stopped** harness
  while B writes during a **live** resume, and ground 1 turns on the event sitting outside the OD
  `pause.*` / `resume.*` family — which is exactly where Reading C places this same event. **B may
  still owe no OD leg, but it owes its own determination**, and treating `K-17` as dispositive
  under-priced B in the ranking. Absorbed at §4 Reading B and as a new §9 row.
- **[P2] "Warn both public read surfaces under option D" — UPHELD.** Component 1 scheduled a
  docstring only for `read_paused_workflow_state`, leaving `resume()`'s separately-documented
  `resume_handle` parameter (`api.py:1197`, `:1223`) unwarned — i.e. disclosing the limit on the
  surface that *reads* and not on the one that *executes*. Absorbed at Reading D Component 1 and
  §9's spec-leg cell.

**SOUNDNESS EXIT — declared after round 3, on SOUNDNESS rather than on reviewer quiet.**
`[[deferred-mechanism-spec-leg-exit-on-soundness]]` is the governing discipline: a filing whose
disposition is a **deferral** exits when the disposition is sound and honestly priced, **not** when
the reviewer runs out of prose to sharpen. **Thirteen findings across three rounds**, every one
verified by direct read or empirical probe *before* absorption, every one absorbed as substance, and
**three absorbed against this filing's own interest** (the disposal-brake point deleted from §6; the
deferral-is-not-cost-free cost added to D; the exclusivity claim withdrawn from §3(vii)).

**The discriminator is met.** Round 2 produced the last finding that touched the disposition, and it
**amended** D (adding the mandatory declaration) rather than displacing it. **Round 3 produced ZERO
findings against the disposition** — one self-consistency defect, one scope gap, two precision
corrections, all in *how the options are described and instructed*. The
`[[non-convergent-adversarial-hardening-arms-race]]` Q5 test — *does the finding invalidate the
carrier's premise?* — answers **NO** for round 3 on all four. Continuing would be the arms-race
pattern this workspace stops on. **This filing is CLOSED to further mechanism rounds**; the remaining
open items are ratification decisions, and the one genuinely unsettled element (A vs B as runner-up)
is **registered and held** at §6 rather than carried into a fourth round.

**Enumeration cap, stated as a binding rule.** The consumer surfaces at §3(vii), the resume branches
at §3(vi), the sink retrieval path, and the `LEGACY`-scoped consumers at §3(i) are this filing's
**verified-at-HEAD inventory, not a closed set**. Any surface of the same kind this filing did not
list is bound **by the rule**, not excused by its absence from the list — the spec/impl leg
inventories rather than inherits.

---

## §11 RATIFICATION

**Status: RATIFIED 2026-08-01 as READING D — DECLARE + DEFER. Component 1 (the MANDATORY
declaration) is APPLIED at the same PR as this addendum: Runtime spec v1.109 → v1.110. Component 2
(the discriminator) is DEFERRED with the four-disjunct demand test on the register row. Per §9's `D`
column there is NO impl leg.**

The `B-92` / `B-97`(a) precedent is followed: the outcome is recorded here verbatim-in-substance
rather than only at the register row, so the decision travels with the filing a later session
actually reads.

### §11.1 The gate — the reading (operator `AskUserQuestion`, 2026-08-01)

> **Operator selected: READING D — DECLARE the resolved-ambiguity limit SYMMETRICALLY (Component 1,
> MANDATORY), then DEFER the discriminator with the fork's falsifiable triggers (D-0…D-3).**
>
> **Component 1 is ratified in its amended, declaration-carrying form** — the round-2 amendment that
> made the declaration mandatory rather than optional, on §3(vii)'s ground that the limit is contract
> text at §13.7 term 3-bis and **undeclared on both tenant-facing surfaces that share
> `_read_durable_pause_snapshot`**. A pure deferral was NOT ratified and is explicitly foreclosed.
>
> **Component 2 is ratified with D-0 DOMINANT** — *a retention / pruning-policy arc opening*, because
> a pruner cannot be permitted to reclaim an outstanding pause and is therefore **unbuildable**
> without the discriminator: format-keying gives it nothing, since post-cutover every journal is
> `CURRENT_FORMAT`. **D-1, D-2 and D-3 are ratified in the forms §4 states them**, D-1 in its round-2
> re-scoped form (a surface **branching** on liveness, or an observed stale re-resume in a fresh
> process) — the first form having been already satisfied at HEAD by §3(vii) and therefore vacuous.
>
> **`status` stays `registered_finding`.** No sentinel record, no marker file, no OD event kind, no
> sixth cause member.

**Readings A, B and C were NOT selected and are NOT partially adopted.** The runner-up, **A, was
registered-and-held** at §6 per `[[reviewer-oscillation-register-and-hold]]` and is **not** advanced
by this ratification; the A-vs-B adjudication remains the operator's if D-0…D-3 ever fires.

### §11.2 What Component 1 landed — the SPEC leg, applied at this PR

**Runtime spec v1.109 → v1.110, TWO amendment sites, both pure declarations of an EXISTING limit.**

| §9 obligation (the `D` spec-leg row) | Disposition |
|---|---|
| A §14.14.9 term declaring that the latest durable record may itself be an already-resolved pause, symmetric with §13.7 term 3-bis | **APPLIED** — a new closing paragraph at **§14.14.9.1**: the read reports the **latest durable record**, which is **not a liveness claim**; the projection is authority for *what the latest durable pause was waiting on*, **never** for *the workflow is paused right now* |
| The same term on the **§30** read path | **APPLIED** — a NEW invariant bullet immediately after `Durable-handle read (v1.46)`, stating the substance **in full** rather than by pointer, plus the sharpening §14.14.9.1 does not need: `resume()`'s shipped guards validate **integrity and applicability, never outstandingness**, and the §30 staleness precondition fences a composed claim against a **CHANGED** record — so a re-resume of an **unchanged, already-resolved** record presents no mismatch and **is admitted** |
| The matching docstrings on **BOTH** public surfaces — `read_paused_workflow_state` (`api.py:925`) **and** `resume()` (`:1170`, `:1197`/`:1223` — this filing's PRE-LEG anchors) | **APPLIED on both, and on `resume()` twice**: the durable-handle prose **and** the separately-consulted `resume_handle` parameter entry, per round 3 [P2]'s correction that disclosing on the accessor alone would warn the weaker surface and leave the one that **executes** unwarned. **ZERO logic changed.** **POST-EDIT anchors, recomputed in the landed tree because these very insertions shift `api.py`'s lower half:** `read_paused_workflow_state` `:925` (unchanged — the insertions sit below its `def`), `resume()` **`:1190`**, its `resume_handle` parameter entry **`:1260`**, and its durable read **`:1360`**. *(Caught at out-of-family review round 2 [P2] on this leg; the pre-leg cites in this filing's body stay as written, being correct against the version that authored them.)* |
| Spec text + two docstrings; **zero code, zero contract numbers, zero hash impact**; no other design extension | **HELD EXACTLY.** No `C-RT-*` minted (a doc-only leg cannot); no carrier retyped; no field added; no `snapshot_hash` impact; the five-member `PauseJournalReadCause` vocabulary stays **CLOSED at five**; §13.7 / §13.7.1 / §14.14.8 / §14.14.9.2 – §14.14.9.6 / §30's cause table + failure-mode taxonomy **PRESERVED VERBATIM** |
| Impl leg | **NONE OWED** — §9's `D` column says so, and nothing here creates one |
| Plan deltas | **NONE OWED** — no Runtime unit, no OD unit, no CP unit. Verified, not assumed: `B-104` is cited at **no** implementation plan and at **no** acceptance criterion, so no plan cite contradicts the deferral |
| CXA | **NO row, NO delta** — this leg introduces **no cross-package consumption at all**; aggregate stays frozen at 111 |
| Clearance | `.harness/clearance/spec-harness-runtime-v1-110-cleared-2026-08-01.md` |

### §11.3 What the ratification carries, per §8's "carried by any answer" list

**The `close_out` is AMENDED**, items (a) – (i): the hypothesized derive-from-existing option is
**FALSIFIED** with its two missing links and Reading C named as the near-miss; sub-decision (a)-1 is
**FORCED, not open** (a `PauseSnapshot` sentinel is resumable); (a)-2 is **confirmed genuine with a
default worse than unspecified** (`corrupt-latest` + `indeterminate=True`, empirically probed); the
**second-authority objection to (b) does not hold as written**; the ambiguous-and-consequential set is
**frozen, one-time and drainable**; the **NOT-IN-THE-ROW cross-axis cost** (a sixth cause member forces
an OD spec + plan leg) is recorded; the **NOT-IN-THE-ROW occurrence-key requirement** is pinned to the
shipped §30 staleness token's `(record_count, latest_record_digest)`; the disposal-brake re-key is
recorded as **an explicit decision each build reading owes, NOT an argument for deferral**; and the
**§3(vii) SCOPE CORRECTION** — the ambiguity is **NOT** confined to the legacy set.

**Component 1's declaration is recorded on the row as OWED-AND-DISCHARGED**, not as an optional
companion — the §8 bullet that forbids landing a pure deferral is honoured by having landed the spec
delta in the same PR as this addendum.

**The `council` field is NARROWED** to §7's per-reading form: under D, **none is owed now**, and one
is owed at **D-0**.

**PR #1170's scope is recorded correctly on the row** — a **strings-only** self-description refresh
(78/16, zero logic) that removed a *phantom* blocker on the drain recourse and left this one
untouched; the row must not be read as having been narrowed by it.

### §11.4 The §9 priority note, carried forward and NOT acted on

`[MODERATE]` The cheapest actionable operator-loop improvement is in none of the four readings: the
drain recourse has **no `resume` ADMIN-CLI command** (§2 — the admin surface ships seven commands,
none of them resume), so an operator driving pauses to resolution must call the **public
package-root Python API `harness_runtime.resume()`** from their own code.

**Precision carried by this addendum, corrected at out-of-family review round 4 [P2].** `resume()`
**IS a SUPPORTED surface** — it is one of the **three** package-root async functions `B-106`'s own
ruling enumerates as the operator-facing API (`run` / `resume` / `read_paused_workflow_state`). What
`B-106` ruled **NOT SUPPORTED** is the distinct **embedder** path (direct `run_bootstrap()` /
`ctx.pause_resume_protocol` access). §2's finding is therefore about an **absent CLI affordance, not
an absent capability**, and an earlier draft of this section conflated the two. This ratification
does **not** open that CLI surface; it records that the two are ordered, which the register now
says.

### §11.5 Re-affirmation in the 2026-08-05 ratification batch

**`B-104` was carried into the standing eight-decision operator batch answered on 2026-08-05, and the
operator's verdict is READING D — DECLARE + DEFER, unchanged.**

- **Nothing new is owed.** **Component 1**, the mandatory symmetric declaration, already landed at
  **Runtime spec v1.109 → v1.110** (PR #1182, clearance marker
  `.harness/clearance/spec-harness-runtime-v1-110-cleared-2026-08-01.md`), and **Component 2**, the
  capture-side discriminator, stays **DEFERRED** under the four-disjunct demand test with **D-0 (a
  retention / pruning-policy arc) dominant**. `status` stays `registered_finding`; there is no impl
  leg.
- **Readings A, B and C remain NOT selected.** The runner-up **A** remains *registered-and-held* per
  `[[reviewer-oscillation-register-and-hold]]` and is **not** advanced by this re-affirmation; the
  A-vs-B adjudication remains the operator's if D-0…D-3 ever fires.
- **One bookkeeping repair rides this leg.** The register row's `pr:` pointer still read `#pending`
  for the ratification leg; it now names **#1182**, plus the 2026-08-05 batch record.
