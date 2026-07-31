# Class 2 Fork — B-97 half (a): the durable pause journal carries no tenant binding

**Status: FILED 2026-07-31, awaiting operator ratification.** Doc-only filing per the workspace
codex-context-guard rule (fork FILINGS ship doc-only FIRST; no `design-substrate/**` edit rides this
PR). Chain mirrors `B-65`'s and `B-92`'s: **filing (this PR) → operator ratification → spec leg →
impl leg.** Half (b) — cross-process append serialization — is **CLOSED** at PR #1167; this fork
carries the surviving half only.

**Register row.** `B-97` at `.harness/forward-register.yaml:2888` (`status: registered_finding`;
the row deliberately stays `registered_finding` because the enum has no half-closed member) + prose
at `.harness/post-phase-8-forward-register.md` `### B-97`.

**Grounding HEAD.** `3473c9aa`. Every `§`/line cite below was re-resolved at this HEAD; the four
that moved or were found stale are recorded at §10.

---

## §1 The question, and what carries it

`Spec_Harness_Runtime_v1.md` §14.8.11 (`:4804` heading) commits, for the *protected post-effect
result store*, a **full-strength tenant-composite key** (`:4809`) and a **tenant-BOUND lookup whose
cross-tenant attempt is REFUSED TYPED** (`:4812`). The `JournalWorkflowPauseStore` — a comparable
harness-owned durable store, holding `PauseSnapshot`s that since `B-69` carry recovered branch
outputs — has **neither**. It is `workflow_id`-keyed, one file per workflow
(`Spec_Harness_Runtime_v1.md:5826`; `journal_workflow_pause_store.py:358-360`, `sha256(workflow_id)
+ ".jsonl"`), with no tenant anywhere in the key, the path, or the record.

**§14.8.11 is the MODEL, not a binding conformance requirement on this store.** `[HIGH]` Stated
plainly because the distinction was blurred in this filing's first draft and corrected at
out-of-family review round 1 [P2]: §14.8.11's commitment is scoped to the protected result store.
This fork proposes to **extend the analogous property** to the pause journal; it does not report a
violation of an existing contract. What it does report is an **unexplained asymmetry between two
comparable durable stores in one spec** — which is a real thing to resolve, and a weaker thing than
a conformance failure.

**The concrete harm, and its reachability — corrected at review round 2 [P1].** `[HIGH]` The first
draft asserted that a process holds one tenant scope, making cross-tenant confusion *"unreachable
inside one process"*. **That is false.** `config` is a **per-call** parameter on both `run()`
(`api.py:632-636`) and `resume()` (`:1159-1166`), and the module-level `_run_lock` (`:495`) only
**serializes** invocations — it never pins a tenant to the process. A single embedding process that
calls `run(wf, config=cfg_A)` and then `run(wf, config=cfg_B)` with the same `path_bindings` and the
same `workflow_id` reaches the collision **without any multi-deployment topology at all.** The
two-deployment premise (two differently-tenanted deployments sharing one resolved `STATE_LEDGER`
dir) is the *other* route, not the only one — and the single-process route is materially easier to
reach and much easier to reach *accidentally*. Under either route, `workflow_id` is
**operator-authored** (it comes from the workflow manifest, not from a uuid mint), so two tenants
running a workflow of the same name — `"nightly-report"` — collide **by construction**, not by
accident. Tenant B's `resume()` then reads tenant A's snapshot, passes every existing
detect-then-refuse guard (`workflow_id` matches, `step_index` is in range, `snapshot_hash` validates
against its own fields — `Spec_Harness_Runtime_v1.md:3306-3307`), and **executes tenant A's paused
workflow under tenant B's ledger, audit and cost attribution.**

**Why it is a fork rather than an impl task.** It changes the store's **keying**, which is
capture-side. That is the `B-73`/`B-80` split-out discipline that kept it out of the read-only
`B-69` arc in the first place (`Spec_Harness_Runtime_v1.md:27` finding (i)). Four decisions ride
it, none of which an impl leg may settle on its own authority; they are enumerated at §5.

---

## §2 Current behaviour at HEAD `3473c9aa`

| Surface | State |
|---|---|
| Journal path | `<STATE_LEDGER>/pause-journal/<sha256(workflow_id)>.jsonl` — `journal_workflow_pause_store.py:358-360`, `pause_journal_dir_for` `:223` |
| Record shape | **a store-owned wrapper**: `{"workflow_id": …, "pause_snapshot": {…}}`, `json.dumps(sort_keys=True)` — `journal_workflow_pause_store.py:515-519` |
| Read | `_parse_snapshot_attributed` loads the wrapper, compares `record["workflow_id"]`, then validates `record["pause_snapshot"]` — `:594-611` |
| Read disposition | **latest record only, never walk backward** — `Spec_Harness_Runtime_v1.md:5834` (append-only / never-truncated invariant). This is load-bearing for §5.1 |
| Cause vocabulary | `PauseJournalReadCause` — **5 members**, programmatically recounted at this HEAD: `absent` / `empty-journal` / `read-error` / `corrupt-latest` / `workflow-mismatch`. Spec table `Spec_Harness_Runtime_v1.md:3316-3322` (header `:3316`, five rows `:3318`-`:3322`) |
| Capture-side construction | `pause_resume_protocol_factory.py:199-201` — inside `if config.pause_resume_protocol_config.durable:` |
| Read-side construction | `api.py:775` `_read_durable_pause_snapshot(config, workflow, resume_handle)` → `:808` |
| Tenant anywhere in the store | **none** — `JournalWorkflowPauseStore.__init__` takes `journal_dir` only (`:248`). **Including for a deployment whose `config.tenant_id` is already non-`None`** — the store is never handed the scope, so *every* existing record is unattributed regardless of deployment tenancy (§5.3) |
| Sibling that DOES bind tenant | `protected_result_store.py` — `_StoredEnvelope.tenant_id` `:289`, `composite_key` `:298`, `read(tenant_id, composite_key)` `:592`, refusing via a **dedicated peer exception** `ProtectedStoreCrossTenantError` `:219` (raised `:601`, `:636`) |

---

## §3 Three grounding findings that reshape the register row's framing

The register row poses decision (1) as a binary — *tenant in the sha256 FILENAME* **or** *in-record
alongside `workflow_id`* — and attaches to the second the objection that it is *"capture-side and
`snapshot_hash`-adjacent."* Grounding at HEAD partially dissolves that framing. All three findings
are stated because they change the analysis, not to advocate.

### (i) The journal record is ALREADY a store-owned wrapper envelope — so in-record tenant is Runtime-only and hash-inert `[HIGH]`

`_append` does **not** write `snapshot.model_dump()`. It writes a two-key wrapper
(`journal_workflow_pause_store.py:515-518`) whose outer `workflow_id` is a **store-owned duplicate**
of a snapshot field, and `_parse_snapshot_attributed` reads that outer key **before** touching the
embedded snapshot (`:599-600`).

Consequences, each checkable:

- A third wrapper key `tenant_id` touches **no CP type**. `PauseSnapshot` lives at
  `harness-cp/src/harness_cp/pause_resume_protocol_types.py:745` and is untouched — **no CP spec
  amendment is owed for the carrier**, and the arc does not enter C-CP-26 §26.2.
- It is **`snapshot_hash`-inert by construction**. `snapshot_hash` is computed over `PauseSnapshot`'s
  own fields (`Spec_Harness_Runtime_v1.md:3306`); a wrapper key is not one. *(The **journal record
  bytes** do change — see §9's witness (d), sharpened at review round 1 [P2]; the inertness claim is
  about the snapshot hash, not the record.)*
- The cross-tenant check is a **byte-for-byte structural twin of the `workflow-mismatch` check
  already shipped** at `:599-600` — same wrapper, same comparison, same fail-closed shape.

The register's *"`snapshot_hash`-adjacent"* concern is therefore **true of a `PauseSnapshot` field
and false of a wrapper key.** It remains capture-side (the writer must stamp it), which is real, but
capture-side ≠ hash-adjacent, and only the latter is the reason `B-69` excluded it.

### (ii) The tenant scope already exists and already reaches BOTH construction sites `[HIGH]`

`RuntimeConfig.tenant_id: str | None = None` (`types.py:2027`), surfaced at
`HarnessContext.tenant_id` (`types.py:2993`), with a validator forbidding the reserved `"_single"`
value (`types.py:2030-2046`). The single-tenant normalization authority already exists and is
OD-owned: `RuntimeAuditLedgerWriter._SINGLE_TENANT_TAG = "_single"` (`audit_writer.py:338`),
`_tenant_tag` (`:627`).

Both journal-store construction sites already hold `config`: the capture-side factory reads
`config.pause_resume_protocol_config.durable` two lines above the construction
(`pause_resume_protocol_factory.py:199-201`), and the read-side helper takes `config` as its first
parameter (`api.py:775`). **No new config field and no operator data entry is required by any
reading below** — which narrows, but does not eliminate, C11's concern (§7: the surviving
local-deployment cost is an *upgrade* cost, not a configuration one).

### (iii) The sibling's writable-disk argument does NOT transfer — stated honestly, against interest

`protected_result_store.py:280-286` argues that `tenant_id` **alone** is insufficient: under a
writable-disk threat, copying tenant A's ciphertext from reference B's path onto reference A's path
passes both Fernet authentication and the tenant-only check, so the **full composite key** must ride
in-record.

That argument is **load-bearing for an encrypted store and inert for this one.** `[HIGH]` The pause
journal is **plaintext JSONL**. An adversary who can write the journal directory does not need to
relocate a record — they can author one, with any `tenant_id` they choose. There is no
authentication to defeat. **No reading below defends against a writable-disk adversary**, and any
spec text implying otherwise would be false. What is genuinely on offer is **isolation and
mis-addressing prevention between mutually-trusting deployments that share a directory** — which is
exactly the `B-97` premise and a real class of harm, but it must be booked as that and not as a
security boundary. `[MODERATE]` on the claim that no future encryption of this store is
contemplated — none is specified today; if one were, §14.8.11's composite-key reasoning would
transfer wholesale.

---

## §4 The readings

**The discriminator that orders them** *(surfaced at out-of-family review round 1 [P1]; it was
missed in this filing's first draft and it reverses that draft's recommendation)*:
`read_latest_attributed` reads the **latest record only and MUST NOT walk backward**
(`Spec_Harness_Runtime_v1.md:5834`). Therefore **whether the two tenants share a FILE decides
whether each keeps a resumable stream at all.** A reading that leaves them sharing one file converts
the defect from *wrong execution* into *mutual resume denial* — safer, but still a loss of the
store's core semantic. Only a reading that separates the address space preserves per-tenant
latest-record authority.

### Reading A — path segregation (RECOMMENDED)

The tenant scope enters the **filename** — `<sha256(canonical_encoding(normalized_tenant,
workflow_id))>.jsonl`. The record shape is unchanged.

**The tenant-SUBDIRECTORY variant is foreclosed** *(review round 4 [P1]; this filing's earlier drafts
offered it as an equivalent alternative, which was wrong)*. `RuntimeConfig.tenant_id` accepts
arbitrary strings — including `/`, `..`, an absolute path, and NUL — so a tenant used as a **path
component** can escape the journal root or fail a valid capture, and injectivity alone does not make
it filesystem-safe. The hashed-filename form has no such hazard **by construction**: the sha256 digest
is the only thing that reaches the filesystem. If a future arc wants the subdirectory layout for
operator legibility, it owes an encoded path-safe component **plus** containment validation, and that
is a different decision from this one.

**The encoding MUST be injective, and that is a contract term, not an implementation note**
*(out-of-family review round 3 [P1])*. A naive `tenant + "\x00" + workflow_id` concatenation is
**not** injective: `RuntimeConfig.tenant_id` (`types.py:2027`) and `workflow_id` are both arbitrary
strings, so `("a", "b\0c")` and `("a\0b", "c")` produce identical preimage bytes and therefore **the
same journal path** — recreating the exact cross-tenant collision this reading exists to close, via
programmatically valid inputs. The spec leg MUST require an unambiguous **TOTAL** canonical tuple
encoding — length-prefixed, or a canonical JSON array, or equivalent — one that is injective **over
the full existing input domain**.

**Delimiter *rejection* is NOT an equal alternative** *(review round 6 [P2]; an earlier draft offered
it as one)*. `RuntimeConfig.tenant_id` rejects only `""` and the reserved `"_single"`
(`types.py:2030-2046`) and `workflow_id` is an unconstrained string, so rejecting a delimiter would
make **currently-valid identifiers invalid** — a change to a *public input contract*, not an encoding
detail, and therefore not something an impl leg may choose on its own authority. If the operator
*wants* the validation, the spec leg must ratify it explicitly as an input-contract narrowing.
*(Note the interaction with §5.2: the in-record key of Reading A+B
would catch a collision produced by a non-injective encoding — but that is defence against a defect
the encoding requirement removes outright, and a wrapper field is not the right answer to a broken
key.)*

- **Spec text changed.** §14.14.8's *"Keying = `workflow_id`"* paragraph (`:5826`) is amended to a
  tenant-composite key; §14.14.9.1's `workflow_id`-only keying statement (`:3384`) is amended in
  parallel — *both surfaces, per its own rule*.
- **What it delivers.** Per-tenant address space → **each tenant retains its own latest-record
  authority and resumes correctly.** A wrong-tenant lookup resolves the caller's *own* path and
  returns **`absent`** — and under a segregated address space that is **the truth, not a misleading
  diagnosis** (the caller genuinely has no record for that workflow). *(This filing's first draft
  called it misleading; that was wrong and is corrected here.)*
- **What it does NOT deliver.** A typed cross-tenant refusal in the §14.8.11 `:4812` shape. There is
  nothing to refuse — the other tenant's file is never opened. Decision (2) is **not discharged**;
  it is **dissolved** for the ordinary case.
- **Decisions forced / deferred.** Forces (1) and (3). Dissolves (2) for the ordinary case. Defers (4).
- **Migration.** Every existing `<sha256(workflow_id)>.jsonl` becomes unaddressable → **in-flight
  pauses at the upgrade boundary are abandoned** unless the operator declares an adoption (§5.3).
  Crucially, **no fallback read is proposed**: adding one would create a second read authority over
  one key and fail open at exactly the boundary being built. With no fallback, the legacy file is
  simply an orphan of a retired key — §14.14.8's append-only invariant (`:5834`) is untouched (it
  forbids rewriting and truncating; it does not require reading).
- **Effect on the `B-69` accessor.** Both surfaces move together; the *"BOTH surfaces or NEITHER"*
  rule (`:3384`) is honoured. `PausedWorkflowState` and the cause vocabulary are unchanged.

### Reading B — in-record binding only

A third wrapper key `tenant_id` at `_append` (`:515-518`); the store takes the caller's resolved
scope at construction; `read_latest_attributed` compares it exactly as it already compares
`workflow_id` (`:599-600`) and refuses typed on mismatch. **The path is unchanged.**

- **Spec text changed.** §14.14.8 gains an additive tenant-binding paragraph (the existing keying
  paragraph at `:5826` stays true — the *path* remains `workflow_id`-keyed). §30 and §14.14.9.4 gain
  the refusal member per decision (2). §14.14.9.1 (`:3384`) is unamended.
- **What it delivers.** The §14.8.11 `:4812` shape — a genuine typed cross-tenant refusal on an
  ordinary read. **No path change.** *(Corrected at review round 2 [P1]: this is NOT "zero
  migration". Under the recommended (3a) disposition every pre-upgrade record lacks `tenant_id` and
  is refused, so B abandons outstanding pauses at the upgrade boundary **exactly as A and A+B do**.
  B's advantage over them is that the **path** is stable, not that the upgrade is free.)*
- **What it does NOT deliver — the [P1].** Both tenants keep writing **one file**. After tenant B
  appends, tenant A's read gets B's record, refuses, and — barred from walking backward (`:5834`) —
  **cannot reach its own valid record sitting one line below.** Reading B therefore trades silent
  cross-tenant execution for **mutual resume denial** in exactly the collision scenario that
  motivates the fork. It is strictly safer than today and strictly weaker than A.
- **Decisions forced / deferred.** Forces (1), (2), (3). Defers (4).
- **Effect on the `B-69` accessor.** The accessor's failure channel already **is** a typed raise
  carrying a stable cause identifier (`:3454`); §14.14.9.4 requires both surfaces name a state
  identically and forbids a *"parallel disposition enum"* (`:3455`). B extends that channel;
  `PausedWorkflowState` is unchanged (the cause belongs to the FAILED read, which returns no
  projection — `:3447`).

### Reading A+B — path segregation plus an in-record attribution (RUNNER-UP)

Reading A's path, plus Reading B's wrapper key — **but with the in-record key's role stated
honestly, because it is not what the first draft claimed** *(review round 1 [P2])*: with segregated
paths, an ordinary wrong-tenant lookup never opens the other tenant's file, so the in-record key
**cannot produce a cross-tenant cause for the ordinary case.** What it detects is a record
**mis-filed at the caller's own exact path.**

**And that trigger is much narrower than this filing's second draft claimed** *(review round 3
[P1])*. A whole-directory restore or copy — the ops accident originally cited — **does not reach the
check**: tenant A's journal keeps A's tenant-derived *filename*, tenant B looks up B's different
filename, and the read returns `absent` without ever opening A's file. **Only an explicit relocation
or rename of a record into B's exact path** triggers the wrapper comparison. What genuinely remains:
a deliberate mis-placement; a future change to the path composition that silently re-maps keys; and
defence-in-depth against a non-injective encoding — which the Reading A contract term above removes
outright. The residual is **audit/forensic value** (a stamped record says which tenant owns it) plus
one narrow accident class. **This is why the recommendation at §6 is A, not A+B.**

- **Spec text changed.** A's, plus one additive attribution paragraph and decision (2)'s cause.
- **Delivers.** Per-tenant streams (A) **and** typed detection of an accidentally mis-filed record.
- **Costs.** A's migration; one wrapper key; one comparison.
- **Decisions.** Forces (1), (2) *in its narrowed form*, (3). Defers (4).

### Reading C — defer half (a); declare the posture

**One declarative paragraph** at §14.14.8 declaring that **reuse of one resolved `STATE_LEDGER` /
pause-journal directory across two different tenant scopes is UNSUPPORTED — regardless of process or
deployment topology** — and the row stays registered. *(Two corrections. Round 1 [P2]: the first draft
said "no spec text" in one place and "say so in the spec" in another, leaving C under-determined —
**C carries the paragraph.** Round 4 [P1]: an earlier wording scoped the paragraph to
*differently-tenanted **deployments***, which would have left §1's single-process sequential route —
one embedding process calling `run()`/`resume()` with two tenant configs over one directory —
**neither fixed nor declared unsupported**. The paragraph must be topology-free.)*

- **Decisions.** Defers all four; the spec leg is one paragraph.
- **Honest case for it.** No shipped *deployment recipe* pairs two tenants over one state-ledger dir,
  and §14.8.11's commitment is scoped to *that* store (§1). `[MODERATE]`
- **Honest case against.** It leaves the asymmetry in place and merely stops it being *unexplained* —
  and, given §1, it declares unsupported a configuration a single process can reach with two ordinary
  API calls. A costs a migration and makes that configuration correct instead.

---

## §5 The four decisions, per reading

### §5.1 Decision (1) — key composition

| | Per-tenant latest-record stream | Typed refusal on an ordinary cross-tenant read | Detects a mis-filed record | Widens the closed vocabulary | Legacy pauses abandoned at upgrade (3a) | Path changes | Defends a writable disk |
|---|---|---|---|---|---|---|---|
| **A (path)** | **yes** | no — returns `absent`, which is *true* under segregation | no | **no** | yes | yes | no (§3(iii)) |
| B (record) | **no — mutual resume denial** | yes | n/a | yes | **yes** | no | no |
| A+B | **yes** | dissolved (nothing to open) | only on an **explicit relocation into the exact path** (§4) | yes | yes | yes | no |
| C | n/a | n/a | n/a | no | no | no | no |

*(Two corrections are baked into this table. **Round 2 [P1]:** migration split into **abandonment**
— common to A, B and A+B under (3a) — and **path change**, which is A/A+B-specific; the first draft's
single column recorded B as `none` and hid the shared upgrade cost. **Round 3 [P1]:** A+B's
mis-filing column narrowed from "a restored/copied directory" to "an explicit relocation into the
exact path", because a whole-directory restore keeps the source tenant's filename and is never opened
by the other tenant — see §4. That narrowing is what moves the recommendation from A+B to A.)*

**The trade is not "refusal vs. no refusal"; it is "availability vs. a refusal you only need because
you kept the address space shared."** `[HIGH]` Path segregation makes the ordinary cross-tenant
refusal *unnecessary* rather than *unavailable* — the read never reaches another tenant's state.
That is a stronger isolation property than a refusal computed after reading it.

### §5.2 Decision (2) — refusal semantics, in the form the reading leaves it

Under **B**, this is the register's question as posed: a cross-tenant refusal needs a **sixth**
member in the deliberately CLOSED five-member `PauseJournalReadCause` (5 members, recounted
programmatically at §2; the `v1.107` leg explicitly declined a sixth —
`Spec_Harness_Runtime_v1.md:3324`, *"The five-member vocabulary is UNCHANGED"*).

Under **A+B** the question **narrows**: the condition to name is not "you read another tenant's
record" but "**a record mis-filed at your own path**". Two shapes:

- **(2a) a sixth member — e.g. `tenant-mismatch`.** Argument for: **homogeneity.** The existing
  `workflow-mismatch` member (`:3322`) is itself an **identity-mismatch** cause, not an
  I/O-or-corruption one, and it is computed at exactly the site a tenant check would be
  (`journal_workflow_pause_store.py:599-600`). And the operator repair is genuinely distinct —
  *"this journal file holds another deployment's records; you likely restored or copied a directory"*
  — which is precisely the distinction §30 exists to preserve (`:3326`, *"`empty-journal` MUST NOT
  fold into `absent`"*). Satisfies §14.14.9.4's one-vocabulary rule (`:3455`) with no new machinery.
- **(2b) fold into `corrupt-latest`.** Defensible — a mis-filed record *is* "the record we would
  resume from is unusable" (`:3321`) — and it mints nothing. Against: it discards the one repair
  instruction the operator can act on.
- **(2c) a peer refusal class**, mirroring `ProtectedStoreCrossTenantError` (`:219`). Against:
  §14.14.9.4 forbids a *"parallel disposition enum"* on the accessor surface and requires both
  surfaces name a state identically (`:3455`), so this needs a paired class on **both** surfaces —
  more machinery than (2a) for the sole benefit of a count staying at five.

**Recommended: (2a).** `[MODERATE]` The closed-vocabulary property protects against *collapse*
(§30's stated purpose), not against *growth*; a distinguishable cause with its own operator repair
is what the vocabulary is for.

#### §5.2.1 Reading B needs a SECOND cause — for the untenanted legacy record *(round 8-9 [P2])*

This applies **only if B is ratified**, and it must be settled at gate 1 rather than discovered at
the spec leg. Under B the path never changes, so a legacy record **is found** by the read — and it is
a *well-formed* record whose owner is simply **unknown**. Neither existing candidate fits: labelling
it `cross-tenant` **asserts a mismatch that was never established**, and folding it into
`corrupt-latest` **mis-states a record that parses perfectly**. Three shapes, and B's ratification
must pick one:

- **(B-2-i) a SEVENTH member — e.g. `untenanted-legacy`** — honest and distinctly repairable
  (*"this record predates tenant binding; adopt it via (3b) or accept the abandonment"*). Cost: B
  would widen the closed vocabulary by **two** members, not one, which materially worsens B's
  standing against A on §5.1's vocabulary column.
- **(B-2-ii) widen `cross-tenant`'s DEFINITION** to *"the record's tenant attribution is absent or
  does not match"* — one member, at the cost of a name that over-claims for half its domain (the
  `corrupt-latest` definition-widening at `:3324` is the in-house precedent for this move).
- **(B-2-iii) fold into `absent`** — *"no record readable **for this tenant**"*. Cheapest and
  arguably true under a tenant-scoped reading of "absent", but it collapses a repairable state into a
  permanent one, which is the collapse §30 exists to undo.

**If B is ratified, (B-2-ii) is the recommendation** `[SPECULATIVE]` — it keeps the vocabulary at six
and follows a precedent this very spec set. *(A/A+B do not reach this question: their legacy record
lives at a retired key and is never read, so it has no cause at all — §5.3.1.)*

**A disclosure note that applies to B and NOT to A+B.** `[MODERATE]` Under B, a cross-tenant cause
tells a non-owning caller that a record **exists** for that `workflow_id` under another tenant — an
existence oracle. Under A+B the reader is at its **own** path, so no cross-tenant existence is
disclosed and the concern does not arise. One more asymmetry favouring A+B.

### §5.3 Decision (3) — migration, restated as the real decision it is

*(Rewritten at out-of-family review round 1 [P1]. The first draft recommended "a legacy record with
no `tenant_id` belongs to the single-tenant scope" — **that is false.** The store is never handed
the scope at all today (§2), so a deployment whose `config.tenant_id` is already non-`None` has
records that are equally unattributed. Absence proves nothing about ownership, and the first draft's
rule would have refused the true owner and abandoned a valid pending pause without saying so.)*

Legacy records are **unattributed, full stop.** Three dispositions:

- **(3a) ABANDON — recommended.** Legacy records are not adopted by any tenant. Under A/A+B this is
  automatic (the key retired; no fallback read). Under B it is an explicit refusal rule. **The cost
  is bounded and should be stated in the spec, not discovered:** a durable pause is a *human-latency*
  event, so the loss window is "pauses outstanding at the moment of upgrade", and the operator's
  recourse is to drain pauses before upgrading. This is the fail-closed direction and it matches the
  store's own disposition.
- **(3b) OPERATOR-DECLARED ADOPTION.** A one-time, explicitly-declared config assertion — *"legacy
  untenanted records in this directory belong to tenant X"* — materialized as a bounded,
  operator-invoked **migration**, whose exact shape is **reading-dependent** — a coupling this
  filing's second draft got wrong by prescribing one shape for all readings *(review round 3 [P1]:
  unconditional stamping under Reading A would silently add the wrapper key Reading A excludes,
  converting the ratified reading into A+B)*:

  - **Under A** — a pure **relocation**: records are written to the tenant-scoped path with the
    record shape **unchanged**, so the five-member vocabulary and the no-wrapper-key promise both
    hold.
  - **Under A+B** — a **parse-and-stamp** migration, since a copy alone is insufficient *(review
    round 2 [P1]: the copied wrapper still lacks `tenant_id`, so the new comparison rejects it at the
    new path and the adoption silently achieves nothing)*.
  - **Under B** — a stamped **re-append** of the latest legacy record **to the same file** (B changes
    no path), which the append-only invariant permits by construction: an append rewrites and
    truncates nothing, and the newly-appended stamped record simply becomes the latest.

  **The source-file rule is reading-scoped** *(review round 6 [P2]; an earlier draft stated it
  unconditionally, which B cannot satisfy)*: under **A/A+B** the legacy file is **left untouched** and
  becomes an unread orphan; under **B** the legacy file **is** the target and is **appended to, never
  rewritten or truncated**. Both satisfy `:5834`; only A/A+B produce an orphan.

  **(3b) additionally REQUIRES a quiescent cutover, and that is a contract term** *(review round 4
  [P1])*. "Exactly one deployment owns the directory" is **not sufficient**: that owner can append to
  the legacy journal **after** the migration has copied it, leaving the tenant-scoped target holding
  an **older** record that a later resume would then treat as authoritative — stale-state resume,
  which is the precise harm §14.14.8's fail-closed latest-record disposition exists to prevent. The
  migration MUST run against a **drained/quiesced** owner, or hold an exclusion that remains
  effective **through completion** (the per-workflow `flock` half (b) already ships is the obvious
  primitive, but the *requirement* is the contract term, not the mechanism).

  **And quiescence alone is still insufficient — the TARGET must hold no NEW-FORMAT record** *(review
  round 8 [P1]; the test refined at round 9 [P2])*. If the upgraded deployment has **already captured
  a pause at the new tenant-scoped key**, a later adoption copies or stamps **older** legacy state on
  top of — or, under B, appends it *after* — **newer** state, making stale state authoritative. That
  is the same stale-resume harm one step removed. The contract term is therefore three-part: **(1)**
  the owner is quiesced through completion; **(2)** adoption runs **before any new-format write** and
  **refuses a target that already holds one**; **(3)** if the operator wants adoption after
  new-format writes exist, the spec must specify a **newest-record-preserving merge** rather than
  leaving the ordering to the impl leg.

  **Term (2) is deliberately NOT "the target file is empty."** Under **A/A+B** the target is a *new*
  path, so the two coincide and "empty" reads naturally. Under **B** they do not: B re-appends into
  the **same** file, which by construction already contains the very records being adopted, so an
  empty-file precondition would make B's adoption **impossible**. The general form —
  *no tenant-stamped record at the target yet* — reduces to "empty" under A/A+B and to "not already
  stamped" under B. **Safe when exactly one deployment owns the directory, that owner is quiesced, AND
  the target holds no new-format record**; **must be refused otherwise** — which is precisely the
  `B-97` premise, so the declaration cannot be made unconditionally safe. Available; not the default.

  **Fourth term — adoption MUST PUBLISH CRASH-ATOMICALLY** *(round 11 [P1])*. Quiescence and the
  empty-target test exclude **concurrent writers**; neither excludes the **migration process dying
  mid-flight**. An interrupted parse-and-stamp can leave the new path holding a valid but **older
  prefix** of the journal, or a **torn final record** — after which the latest-only, fail-closed
  reader either resumes stale state or is permanently wedged, with every stated precondition having
  held. The adopted journal MUST become visible **only** through a **crash-atomic, durable,
  no-replace publication** (write aside → make bytes durable → atomic no-replace commit → make the
  destination directory entry durable), with **recoverable retry semantics** so an interrupted
  adoption can simply be re-run. **This is not a new invention** — it is the publication contract
  §14.8.11 already states for the protected result store (`:4809`), and the spec leg should mirror it
  rather than re-derive it.
- **(3c) PERMISSIVE — rejected.** Any caller may read a legacy record. This makes the untenanted
  scope a permanent universal key: the defect with a name.

**Recommended: (3a) default, with (3b) available as an explicit operator declaration.**

#### §5.3.1 Sub-decision — does a legacy journal get a DIAGNOSTIC probe? *(surfaced at review round 2 [P1])*

Under A/A+B with (3a) there is **no legacy fallback read**, so the reader computes only the new
tenant-scoped path and a legacy-only journal produces the ordinary **`absent`** — which is *true* for
the new key but tells an operator whose pause has just been abandoned by an upgrade **nothing about
why**. Two shapes, and the choice is genuinely open:

- **(i) accept ordinary `absent`** — zero new machinery, and the abandonment is documented in the
  spec's migration paragraph rather than in the runtime signal. Simplest, and it keeps the read path
  single-authority.
- **(ii) a DIAGNOSTIC-ONLY legacy probe ON THE `resume()` / accessor READ PATH — NOT RECOMMENDED.**
  The reader would additionally stat the *legacy* path and report a distinct cause. It was recommended
  in this filing's second draft and is **withdrawn at review round 3 [P2]: it reintroduces the
  existence oracle** §5.2 credits A/A+B with eliminating. **Every** tenant probes the *same* legacy
  path, so a distinct cause tells a non-owning caller that an untenanted record exists for a **guessed
  `workflow_id`** — the disclosure the segregated address space exists to remove, restored through the
  diagnostic door.
- **(iii) the diagnostic on an OPERATOR-ONLY ADMIN surface — RECOMMENDED.** The same information, on a
  surface whose caller is the machine's operator rather than a tenant-scoped workflow caller (the
  existing `harness_runtime/admin/` family is the natural home). It MUST NOT parse, return, or resume
  from the legacy record — it reports existence and points at the migration rule. This keeps the
  runtime read path single-authority **and** oracle-free while still telling the human whose pause was
  abandoned *why*.

**Recommended: (i) on the read path + (iii) on the admin surface.** The motivation §30 states for its
own cause refinement (`:3326`) — an operator repair the caller cannot act on is a livelock with good
manners — is satisfied by (iii) without paying (ii)'s disclosure. **(i) alone is a defensible
ratification**; if chosen, the abandonment must be stated in the spec migration paragraph loudly
enough that `absent` is not a surprise. Under Reading **B** the sub-decision does not arise (the path
is unchanged, so the legacy record is *found* and refused with a real cause).

#### §5.3.2 A MIXED-VERSION cutover term is owed by every non-C reading *(round 10 [P1])*

The (3a) cost is stated above as *"pauses outstanding at the moment of upgrade"*. **That bound only
holds for an atomic cutover**, and nothing so far requires one:

- **Under A/A+B**, an old process in a rolling deployment keeps appending to the **legacy** path after
  new readers have switched to the tenant-scoped one. Every such pause is lost, not just those
  outstanding when the upgrade began — the loss window is the whole rollout, and it is *silent*.
- **Under B it is worse, and the mechanism is verifiable at HEAD**: `_parse_snapshot_attributed`
  (`journal_workflow_pause_store.py:594-611`) reads `record.get("workflow_id")` and
  `record["pause_snapshot"]` and **ignores unknown wrapper keys**. An **old reader** on the unchanged
  path therefore accepts a **new tenant-stamped record without checking its tenant** — the binding is
  silently bypassed for the whole mixed window, on the very path B leaves in place. `[HIGH]`

**Contract term owed at the spec leg, for A, A+B and B alike — and the two candidates are NOT
alternatives** *(sharpened at round 11 [P1], which correctly pressed the point this paragraph had
already half-conceded)*:

- **(a) a no-mixed-version / quiesced cutover — MANDATORY for THIS transition.** All writers upgraded
  before any reader switches. `[HIGH]`
- **(b) a record-version marker an old reader REJECTS — forward-compat only, and NOT a substitute for
  (a).** Pre-upgrade readers **cannot be retrofitted** to honour a marker they were never written to
  see, so selecting (b) *instead of* (a) would still strand A/A+B pauses written to legacy paths and
  would still let B's old readers accept tenant-stamped records without checking the tenant. A marker
  can only protect the **next** transition. Worth adopting **in addition** to (a) if the operator
  expects further keying changes; never in place of it.

(a) composes with (3b)'s quiescence requirement rather than adding a second mechanism.

### §5.4 Decision (4) — the `(workflow_id, run_id)` rider

§14.14.8 names multi-run-disambiguation as the **only** documented re-open trigger (`:5826`), and
§14.14.9.1 binds it *"to BOTH surfaces or NEITHER"* (`:3384`). The register's argument for bundling
is that both are keying changes and *"a second keying arc would pay the migration cost twice."*

**The rider should NOT be bundled.** `[HIGH]` The bundling argument is a cost argument; the rider's
actual blocker is **feasibility**. `run_id` is *"the identifier the caller does **not** know after a
crash"* (`journal_workflow_pause_store.py:26-31`; §14.14.8 `:5826` says the same), and §14.14.9.1's
keying rule is *"key on what you can act on"* — a `(workflow_id, run_id)` handle asks the
crash-recovery caller for the one thing the crash destroyed. `tenant_id` is the exact opposite: it
comes from config (`types.py:2027`) and is always known. **They are not two instances of one
change**, and bundling an infeasible extension into a feasible one would stall both.

*(The cost half of the argument does survive under A/A+B, which do pay a migration — but a shared
cost is not a reason to bundle a change that cannot be specified. If the rider is ever taken, it will
need its own resolution of the post-crash-unknowability problem first.)*

Recommended: **(4) answered NO for this arc, explicitly**, with the §14.14.8 re-open trigger left
standing verbatim plus a one-sentence spec note recording that the tenant binding was evaluated
against it and found independent — so a later session does not re-litigate the bundling.

---

## §6 Recommendation — **Reading A**, with an injective key encoding + (3a) + §5.3.1(i)/(iii) `[MODERATE]`

**In one line: segregate the journal address space by tenant under an encoding that is injective by
contract, leave the record shape and the five-member vocabulary untouched, abandon unattributed
legacy records by default with the diagnostic on an operator-only admin surface, and do not bundle
the `run_id` rider.**

Grounded rationale:

1. **It preserves per-tenant resumability** (§4 discriminator, §5.1) — the property Reading B
   destroys and Reading C leaves unsupported. *(Shared with A+B; it is A-and-A+B's advantage over B
   and C.)*
2. **Its isolation property is stronger than a refusal** — the read never reaches another tenant's
   state, so the ordinary cross-tenant refusal is *unnecessary*, not unavailable (§5.1).
3. **It discloses nothing cross-tenant** — the reader is always at its own path (§5.2) — and the
   §5.3.1(iii) admin-only diagnostic keeps that true at the legacy path too.
4. **It costs the closed vocabulary nothing.** No sixth member, no `RT-FAIL-*` peer, no
   §14.14.9.4 both-surfaces coordination — the `v1.107` leg's explicit *"the five-member vocabulary
   is UNCHANGED"* (`:3324`) survives intact. Under the simplicity discipline this is the decisive
   margin over A+B, because A+B's remaining trigger is narrow (item 5).
5. **A+B's marginal benefit collapsed under grounding** (review round 3 [P1]). A whole-directory
   restore never reaches the wrapper comparison — the source tenant's filename is preserved and the
   other tenant looks up a different one. Only an **explicit relocation into the exact path** trips
   it, and the one systemic case that would have (a non-injective key) is removed outright by the
   §4 encoding contract term rather than papered over by a second check.
6. Its migration is **bounded and statable** — abandon in-flight pauses at the upgrade boundary, with
   an operator-declared **relocation** available (§5.3) — and **does not touch §14.14.8's
   append-only invariant** (`:5834`): nothing is rewritten, and no fallback read is added.

**Runner-up: Reading A+B.** It buys audit/forensic attribution (a record that says which tenant owns
it), defence-in-depth against a future path-composition change, and consistency with the §14.8.11
sibling's in-record binding — for one wrapper field, one comparison, and a sixth cause member.
**Why not:** after round 3, the accident class it catches is narrow and largely deliberate, while the
cost — widening a vocabulary the previous spec leg deliberately closed — is immediate and permanent.
**If the operator weighs cross-store consistency with §14.8.11, or forensic attribution, above the
closed vocabulary, A+B is a fully defensible ratification** and this filing does not argue otherwise;
note only that choosing A+B also changes (3b)'s shape from relocation to parse-and-stamp (§5.3).

**Reading B is NOT recommended** and this filing's first draft recommending it was wrong; the reason
is recorded at §4 and §10 rather than quietly removed. **Reading C is not recommended** but is not
unreasonable — it is the correct choice if the operator's judgment is that reusing one journal
directory across two tenant scopes is permanently out of scope **regardless of process or deployment
topology** (the topology-free form §4 settled at round 4; a deployment-scoped phrasing would leave
§1's single-process sequential route undeclared), in which case the honest form is the declarative
paragraph, not silence.

---

## §7 Council position — **convene a dyadic C3 ⊥ C11 before the spec leg** `[MODERATE]`

The register row's `council:` field (`.harness/forward-register.yaml:2983-2986`) states the condition
is *"now unconditionally MET: opening (a) means convening"*, naming **C3 (state/persistence keying)
⊥ C11 (operator-loop / local-deployment)** with the antecedent *"**if** a tenant key adds
local-deployment config burden."*

Per the probe-first discipline (`CLAUDE.md` §10.9 amendment 5) the probe was run before proposing a
convening, and it produced a **split result that this filing reports rather than rounds off**:

- **The antecedent as literally written is FALSE *on the default path*.** No reading adds a config
  field or any operator data entry **when (3a) abandonment is the default** — `RuntimeConfig.tenant_id`
  already exists, defaults to `None`, and already reaches both construction sites (§3(ii)). On
  *configuration* burden for the default path, C11 has nothing to attach to.
- **But it is TRUE if (3b) is selected** *(round 11 [P2]; an earlier draft used the blanket "no
  operator data entry" claim to dismiss the register's literal antecedent, which over-reached)*.
  (3b) requires an explicit **operator-declared assertion** that legacy records belong to tenant X,
  plus a quiesced, empty-target, crash-atomically-published migration run (§5.3). **That is exactly
  the declaration burden the register row's antecedent names**, and it is one of the two things the
  dyadic is convened to price — so C11 must weigh **both** the upgrade cost of (3a) **and** the
  declaration burden of (3b), not just the former.
- **But the recommended reading carries a different local-deployment cost the row did not
  anticipate:** under A/A+B the journal **path changes for every deployment including the
  single-tenant local default** (whose scope normalizes to the `_single` sentinel), so an upgrade
  **orphans existing journals and abandons in-flight pauses** (§5.3). That is squarely C11's
  surface — it is an upgrade/operator-loop burden rather than a configuration one, and it is
  **exactly the kind of cost a local-first voice exists to price against C3's keying-correctness
  argument.**

**The tension is therefore live, in a restated form, and the convening is owed.** `[MODERATE]` The
honest framing for the voices is: *does per-tenant address-space isolation justify orphaning every
existing local journal at upgrade?* — with C11 additionally able to argue for **(3b) as the default
rather than the escape**, and, on the diagnostic, for **§5.3.1(i) alone versus (i)+(iii)** (i.e. is a
separate operator-only admin surface worth building, or is a well-documented `absent` enough?). Those
are the two sub-decisions most sensitive to that voice. **The withdrawn (ii) is NOT on the table**
*(round 5 [P2] caught an earlier phrasing here that would have sent C11 to weigh it)* — it is an
existence oracle and §5.3.1 forecloses it.

**One framing this filing had to withdraw** *(review round 2 [P1])*: a first draft of this section
asked the question with the rider *"when the harm it prevents requires a topology no local deployment
has."* **That rider is false.** §1 now records that `config` is a per-call parameter on `run()` and
`resume()` and that `_run_lock` never pins a tenant, so a **single local process** that runs two
differently-tenanted configs over the same `workflow_id` reaches the collision with no
multi-deployment topology at all. C11 must price the upgrade cost against a harm that is reachable
locally — which strengthens C3's side of the tension relative to how the register row framed it.

*(This filing's first draft argued the opposite — a probe-resolution and no convening — on the
strength of a recommendation of Reading B, whose supposed zero-migration property made C11's concern
vacuous. Review round 1's [P1] removed that reading. **And the exemption does not survive for B
either** *(round 8 [P2])*: round 2 [P1] established that B abandons every pre-upgrade pause under
(3a) exactly as A and A+B do — the same upgrade/operator-loop cost that triggers C11. **The dyadic is
therefore owed under A, A+B AND B**; only Reading C is exempt, because it keys nothing and abandons
nothing. Recorded rather than silently reversed.)*

**Sequencing — TWO gates, not one** *(corrected at review round 7 [P1], which caught a real
contradiction: §8's single ask settles the (3a)-vs-(3b) default and the §5.3.1 diagnostic, which are
exactly the sub-decisions §7 assigns C3/C11 to price — convening afterwards would have the operator
decide without the input the council exists to supply, and would leave a council disagreement with no
ratification path)*:

1. **Gate 1 — ratify the READING** (§8's four options). The voices should price a *decided* reading,
   not adjudicate between four; that part of the original sequencing stands.
2. **Convene the C3/C11 dyadic** on the two sub-decisions it is competent for: **(3a)-abandon vs
   (3b)-adopt as the default**, and **§5.3.1(i) alone vs (i)+(iii)**.
3. **Gate 2 — a NARROW second ask** confirming or overriding those two sub-decisions in light of the
   council record. It is one `AskUserQuestion` with two rows, not a re-litigation of the reading.

The remaining sub-decisions — the injective encoding (§4), the refusal shape (§5.2), and the no-rider
call (§5.4) — carry no C3/C11 tension and are settled at gate 1.

**Gate 2's row count is reading-dependent** *(round 9 [P2])*: **two rows under A/A+B** (the (3a)/(3b)
default **and** the §5.3.1 diagnostic); **one row under B** — only the (3a)/(3b) default, because
§5.3.1 does not arise when the path never changes and the legacy record is found. **Reading C is
exempt entirely** (it keys nothing and abandons nothing, so no convening is owed and there is no
gate 2). Asking B the diagnostic question would be asking an inapplicable question, which is its own
failure mode.

---

## §8 The ratification ask — ONE decision

> **B-97 half (a) — how should the durable pause journal bind its tenant scope?**

The four register decisions ride the answer as follows:

| Option | (1) key composition | (2) refusal | (3) legacy records | (3.1) legacy diagnostic | (4) `run_id` rider | Council |
|---|---|---|---|---|---|---|
| **(A) RECOMMENDED — path segregation, injective encoding** | tenant in the sha256 filename under a **contractually injective** encoding (§4); record shape **unchanged** | **none needed** — the five-member vocabulary stays closed | **abandon** by default (3a); operator-declared **relocation** available (3b) | ordinary `absent` on the read path **+ an operator-only admin diagnostic** (§5.3.1(i)+(iii)) | **NOT bundled** — independent, §5.4 | **C3/C11 dyadic owed** before the spec leg |
| (A+B) RUNNER-UP — segregated path + in-record attribution | as A, **plus** a wrapper `tenant_id` key | **sixth member `tenant-mismatch`** (2a), scoped to an **explicit relocation into the exact path** | abandon (3a); adoption becomes **parse-and-stamp** (3b) | same as A | not bundled | **C3/C11 dyadic owed** |
| (B) in-record alone | wrapper key only; path unchanged | sixth member `cross-tenant` **AND a settled disposition for the untenanted legacy record** — §5.2.1's (B-2-i) seventh member / **(B-2-ii) widen `cross-tenant`'s definition (recommended if B is taken)** / (B-2-iii) fold into `absent`. Settled at gate 1, never at the spec leg | explicit refusal rule (3a) — **also abandons** pre-upgrade pauses | n/a — the legacy record is found and refused per the previous column | not bundled | **owed** — round 8 [P2]: B abandons pre-upgrade pauses too, which is C11's cost; gate 2 is **one row** for B (§7) |
| (C) defer | none — one declarative paragraph stating the shared-directory topology is unsupported | none | none | n/a | none | not owed |

A ratification of **(A)** also ratifies the four sub-decisions in its row (injective encoding / 3a /
§5.3.1(i)+(iii) / no-rider); each is argued at §4-§5 and any one may be overridden in the answer
without changing the reading. **Note one coupling:** selecting A+B instead of A also changes (3b)'s
shape from a pure relocation to a parse-and-stamp migration (§5.3).

**This ask is GATE 1 of two** (§7, corrected at review round 7 [P1]). Two of its rows — the
**(3a)/(3b) default** and the **§5.3.1 diagnostic** — are the ones the C3/C11 dyadic is convened to
price, so under A/A+B they are ratified here **provisionally** and re-confirmed at a narrow **gate 2**
after the council record lands. The reading itself, the encoding requirement, the refusal shape and
the no-rider call are settled at gate 1 outright.

*(The ask is put to the operator by the orchestrating session via `AskUserQuestion` per `CLAUDE.md`
§14.2 — this filing does not run it.)*

---

## §9 Sequencing, and what each leg owes

**Leg 1 — this filing (doc-only PR).** No `design-substrate/**` edit; no register flip; no
`roadmap_status.md` touch. The `B-97` row's `pr:` and status flip ride the ratification/spec legs.

**Leg 2 — operator ratification.** `AskUserQuestion` on §8. Outcome recorded as a
`## §11 RATIFICATION` section appended to this file (the `B-92` precedent), plus the register row's
`close_out`. **Unless C is ratified, leg 2 is not complete until all three of its steps have run**
*(round 8 [P1] caught the sequence handing the council record straight to leg 3, which would let the
spec leg begin on sub-decisions the operator never re-confirmed)*:

  1. **Gate 1** — the §8 ask (reading + the settled sub-decisions; the (3a)/(3b) default and the
     §5.3.1 diagnostic are **provisional**).
  2. **The C3/C11 dyadic** on those two provisional rows (§7). Owed under **A, A+B and B**; not under C.
  3. **Gate 2** — a narrow `AskUserQuestion` confirming or overriding them in light of the council
     record: **two rows under A/A+B**, **one row under B** (§7 — the diagnostic question does not
     arise for B). **Leg 3 MUST NOT open before gate 2 answers.**

Two register obligations also ride this leg (surfaced at review rounds 5-6; neither may ride *this*
doc-only PR):

- **Flip the `B-97` row to `design_substrate_gated` + record this filing's PR pointer.**
  `registered_finding` under-describes a half whose design question is filed and awaiting
  ratification. **`design_substrate_gated` is a REAL member at HEAD** — 12 occurrences in
  `.harness/forward-register.yaml`, 9 in `tools/forward_register.py` — and it exists precisely for a
  filed fork awaiting ratification / spec application. *(Self-correction, round 6 [P2]: this filing's
  round-5 note claimed the value "does not exist at HEAD". That was **wrong** — it came from counting
  only the values currently **held** by rows (`closed` × 81 / `registered_finding` × 21 / `held` × 1)
  and reading a zero occupancy as a missing member. Recorded rather than quietly fixed; it is a
  textbook instance of `[[verify-observation-layer-before-concluding-defect]]` in miniature.)*
  **Why it is not done in THIS PR — stated precisely, because the reason matters** *(round 7 [P2]
  pressed for doing it here)*: the filing session's **standing instruction** scopes this PR to the
  single new fork doc, with the register flip riding the ratification leg. That is a **scoping
  decision**, not a guard requirement — `.harness/forward-register.yaml` is *not* an implementation
  surface matched by `DESIGN_IMPL_MIX`, so an earlier wording of this bullet over-attributed the
  restriction to that guard and is corrected here. The flip is leg 2's **first** action, not a
  deferral of the question, and the reviewer's substantive point (the register under-reports the gate
  between PRs) is accepted in full.
- **Split the blocking-`flock` follow-up to its own `B-*` row BEFORE `B-97` closes.** It is excluded
  from every leg below; leaving it parked only in `B-97`'s prose means it vanishes from
  `forward_register.py --open` the moment this arc closes the row — or, if the row is held open for
  it, falsely implies half (a) is unfinished. `[[spine-ledger-forward-arc-registration]]`.

**Leg 3 — spec leg.** Owes, for the ratified reading:

0. **The injective-encoding contract term** (§4, review rounds 3 + 6 [P1]/[P2]) — under A/A+B the
   amended keying paragraph MUST require a **TOTAL canonical encoding, injective over the full
   existing input domain**. A path key whose preimage is ambiguous re-creates the very collision the
   reading closes. The *exact* encoding is impl discretion only **once** that requirement is
   spec-stated. **Delimiter rejection is NOT available to this leg by default** *(round 7 [P2]: an
   earlier wording of this item offered it, contradicting §4)* — it narrows a public input contract
   (`tenant_id` rejects only `""`/`"_single"`; `workflow_id` is unconstrained) and may be adopted
   **only if the operator explicitly selected it** at ratification.
1. **`Spec_Harness_Runtime_v1.md` §14.14.8** — the keying amendment (`:5826`, under A/A+B) and/or the
   additive attribution paragraph, plus the **legacy-record disposition** stated explicitly (§5.3) —
   an abandonment rule that is discovered rather than specified is the failure mode this item exists
   to prevent.
2. **§30** — under A+B/B, the new cause's table row (`:3316`-`:3322`) and its `RT-FAIL-*` taxonomy
   row; **and §14.14.9.4** (`:3455`) so both surfaces name it identically. Under A alone: **no
   vocabulary change** — state that as a decision, not an omission.
3. **§14.14.9.1** (`:3384`) — amended under A/A+B (both-surfaces-or-neither); unamended under B, with
   the reason stated so the omission reads as a decision.
4. **Folded in — FOUR stale-as-described refreshes this leg is the natural carrier for** (each
   verified present at HEAD `3473c9aa`; the fourth added at review round 2 [P2]):
   - `:3313` §30 term 5 — *"makes no claim about cross-process write-write serialization of the
     journal, which remains unguarded"* — false as described since PR #1167. The **asserted property
     is unchanged** (the supersession-window claim); only the parenthetical description of the store
     is stale. Not a Class-1 halt.
   - `:3319` §30 `empty-journal` row — *"cross-process append serialization is explicitly unresolved
     (registered at `B-97`)"* — same disposition; the `empty-journal` indeterminacy never depended on
     append serialization and is **unchanged**.
   - `Spec_Harness_Runtime_v1.md:27` — the `v1.107` change-note's finding (i) cites §14.8.11 at
     `:4636`/`:4639`; both are stale by ~168 lines (live anchors `:4809`/`:4812`). One occurrence
     each, both on line 27, recounted programmatically.
   - **`Spec_Harness_Runtime_v1.md:5824`** — the §14.14.8 substrate contract still reads *"append +
     `fsync` + directory-`fsync`-**on-new-file**"*. PR #1167 made **both** directory fsyncs
     UNCONDITIONAL (the parent before the lock, the journal dir after every append) precisely because
     every flag-gated form left a crash window a later writer skips forever. This is a **current
     contract statement inconsistent with the shipped mechanism**, and — unlike the two §30 sentences
     above — the stale text is the *mechanism description itself*, not a parenthetical. *(Missed by
     this filing's first two drafts; caught at review round 2 [P2].)*
4-bis. **The `absent` row itself must be TENANT-SCOPED under A/A+B** *(round 10 [P2]; this corrects an
   earlier claim of this filing, flagged below)*. §30's `absent` row (`:3318`) reads *"no journal
   record exists for this `workflow_id`"*, with the operator repair *"this workflow never journaled a
   pause — check `durable=True`"*. Once the key is tenant-composite, `absent` means *no record for
   this **tenant-composite key***, and it is returned for **two** states where that repair is
   actively wrong: a **wrong-tenant** lookup, and an **abandoned legacy** record (§5.3.1(i)). The row's
   meaning **and** its repair text must be tenant-scoped. **No new cause member is required** — this
   is a definition amendment, like `corrupt-latest`'s at `:3324`.
5. **Folded in — `B-102`** (`.harness/forward-register.yaml:3121`): its cause-table amendment
   (`corrupt-latest` `:3321` and `absent` `:3318` carrying the same cross-process reachability
   qualification `empty-journal` already carries at `:3319`) touches the **same table**. Its
   `close_out` records that it needs **no new cause member**, so it composes with (2a) rather than
   competing. Landing both together avoids two amendments to one cleared table. *(An earlier draft
   said `B-102` is **the only** reason to touch §30 under Reading A — **corrected at round 10 [P2]**:
   item 4-bis is a second, independent reason, and both land in the same row.)*
5-bis. **The mixed-version cutover term** (§5.3.2, round 10 [P1]) — owed under A, A+B and B; it is a
   migration-contract statement in the §14.14.8 amendment, not a §30 cause.
5-ter. **Close `B-102`'s register row in the SAME leg that applies its amendment** *(round 11 [P2])*.
   Item 5 folds `B-102`'s cause-table change into this leg's spec text; if its row's `status` / `pr` /
   `close_out` are not updated in the same PR, `forward_register.py --open` keeps presenting shipped
   work as open and invites a duplicate arc. The leg's register obligations are therefore **three**
   rows, not two: `B-97` (flip), the NEW blocking-`flock` row (split at leg 2), and `B-102` (close).
6. **Plan delta** — Runtime plan (a new `U-RT-*`). No CP plan unit is owed for the in-record half
   (§3(i)); under A/A+B, re-check whether §14.14.9.1's keying amendment pulls a CP-side unit.
7. **CXA** — expected classification-only, no new §2.3 row (Runtime-internal store; the `B-69`
   precedent at `Cross_Axis_Composition_Document_v2_23.md`). To be **determined, not assumed**.
8. **Clearance markers** per `CLAUDE.md` §4.5, and an adversarial-review pass per §10.9.

**Explicitly NOT folded in, so it is not silently dropped:** the `B-97`(b) forward note — the `flock`
is a **blocking syscall taken on the event loop** (`capture()` is called synchronously from the async
`capture_pause_snapshot`; the sibling grew `resolve_result_ref_off_loop` for exactly this). It is a
**mechanism/latency** question with no keying content and no spec text; folding it into a keying arc
would mix two unrelated review surfaces. **It must be split to its own `B-*` register row at leg 2**
(round 5 [P2]) — parking it in `B-97`'s prose loses it the moment this arc closes that row.

**Leg 4 — impl leg.** Under the recommended Reading A: the path composition at `_journal_file`
(`:358-360`) and the tenant scope threaded to both construction sites
(`pause_resume_protocol_factory.py:201`, `api.py:808`) — plus, under A+B only, the wrapper key at
`_append` (`:515-518`), the comparison beside the existing `workflow_id` check (`:599-600`), the
cause member, and the accessor-side carry. **Witnesses, by execution and mutation-probed** per
Workflow v1.18 PD-8:

- **(a)** two differently-tenanted stores over one directory, both capturing the **same
  `workflow_id`**, each read back its **own** snapshot — the per-tenant-stream property, and the
  witness that would have failed under Reading B. **Run it BOTH ways**: as two processes, and as
  **two sequential `run()` calls in ONE process with different `config.tenant_id`** — the §1
  reachability route that round 2 [P1] established.
- **(a′) injectivity** *(round 3 [P1])* — the pairs `("a", "b\0c")` and `("a\0b", "c")` (and a
  length-varying family around them) resolve to **distinct** journal paths. This witness fails
  against a naive delimiter concatenation, which is exactly why it exists.
- **(b)** *(A+B only)* a record explicitly relocated into another tenant's exact path is refused
  typed with the new cause, on **both** surfaces, reporting the **same** identifier. **Do NOT** write
  this as a whole-directory restore — round 3 [P1] established that shape never reaches the check.
- **(c)** a legacy (legacy-path) record is **not** resumable by default. *Shape follows §5.3.1*: under
  **(i)** it asserts the ordinary **`absent`** and nothing more — a witness demanding the refusal
  "name the abandonment rule" is **unsatisfiable** with no read-path probe, which is what the first
  two drafts wrote; under **(iii)** the admin surface additionally reports the legacy journal's
  existence **and** returns no snapshot. Under Reading **B** it asserts the typed refusal directly.
- **(c′) no oracle** *(round 3 [P2])* — a tenant-scoped read of a `workflow_id` whose only journal is
  the untenanted legacy one is **indistinguishable** from a read of a `workflow_id` that never
  existed. This is the witness that would have failed under the withdrawn §5.3.1(ii).
- **(d)** *(A+B only)* `snapshot_hash` is **identical** for a snapshot journaled before and after the
  change. *Scope, sharpened at review round 1 [P2]:* the **journal record bytes necessarily differ**
  (a new wrapper key changes `json.dumps` output for every record, including the single-tenant
  default) — the inertness claim is about `snapshot_hash` alone, and this witness must assert exactly
  that, not record-byte equality.
- **(e)** the mutation probe — remove the tenant component from the path composition, assert (a)
  fails.

---

## §10 Cite re-verification at HEAD `3473c9aa`, and review record

**Cites that moved or were found stale** (all recorded at §9 item 4 as spec-leg obligations, since
they live in `design-substrate/` and cannot ride this doc-only PR):

| Cite | As carried | At HEAD `3473c9aa` |
|---|---|---|
| §14.8.11 anchors in the `v1.107` change-note (`Spec_Harness_Runtime_v1.md:27`) | `:4636` / `:4639` | **stale** → `:4809` / `:4812` |
| §30 term 5 unguarded-serialization sentence | live | `:3313` — **stale-as-described** since PR #1167 |
| §30 `empty-journal` row's *"explicitly unresolved"* | live | `:3319` — **stale-as-described** since PR #1167 |
| §14.14.8 substrate contract *"directory-`fsync`-on-new-file"* | live | `:5824` — **stale-as-described** since PR #1167 (both dir fsyncs are now unconditional); the stale text is the mechanism description itself |
| Register-row framing *"`snapshot_hash`-adjacent"* | asserted | **partially false** — §3(i); true of a `PauseSnapshot` field, false of a wrapper key |
| Register-row council antecedent *"adds local-deployment config burden"* | asserted | **false as written, true in a restated form** — §7 |
| This filing's own draft-1 claim *"unreachable inside one process"* | asserted | **FALSE** — `config` is per-call on `run()`/`resume()`, `_run_lock` never pins a tenant (§1) |

**Cites verified unmoved:** §14.8.11 heading `:4804`, tenant-composite `:4809`, tenant-bound lookup
`:4812`; §14.14.8 keying `:5826`, append-only invariant `:5834`; §14.14.9.1 both-surfaces-or-neither
`:3384`; §14.14.9.4 `:3451`-`:3457`; §30 cause table `:3316`-`:3322`.

**Programmatic recounts** (not eyeballed): `PauseJournalReadCause` = **5** members; §30 cause table =
**5** data rows (`:3318`-`:3322`); `:4636`/`:4639` = **1** occurrence each, both at line 27; the
register's enumerated decisions = **4**.

### §10.1 Out-of-family review — `just codex-review-uncommitted`

**Round 1 — 6 findings (2 × [P1], 4 × [P2]); all 6 ACCEPTED, none disputed.** The two [P1]s reversed
the filing's recommendation and its council disposition:

| # | Finding | Disposition |
|---|---|---|
| [P1] | Legacy tenantless records are **not** provably single-tenant-owned — the store never receives the scope today, so a *tenanted* deployment's existing records are equally unattributed; the draft's rule would have refused the true owner and abandoned a valid pause | **ACCEPTED.** §5.3 rewritten from a fiat rule into a three-option migration/abandonment decision with the cost stated |
| [P1] | Reading B leaves both tenants writing **one file**; with latest-record-only reads that never walk backward (`:5834`), it converts cross-tenant execution into **mutual resume denial** — path segregation preserves per-tenant latest-record authority, which the draft did not credit | **ACCEPTED, decisive.** New §4 discriminator; recommendation moved **B → A+B**; §5.1 table rebuilt |
| [P2] | The hybrid cannot deliver a typed refusal for an ordinary cross-tenant read — segregated paths mean the other file is never opened | **ACCEPTED.** §4/§5.2 restate the in-record key as **mis-filing detection**, and §5.1 marks the ordinary refusal *dissolved*, not delivered |
| [P2] | The same-tenant compatibility witness was unachievable as written — a new wrapper key necessarily changes record bytes | **ACCEPTED.** Witness (d) rescoped to `snapshot_hash` explicitly, with the record-byte change stated |
| [P2] | Reading C was under-determined — "no spec text" in one section, "state it in the spec" in another | **ACCEPTED.** C now carries **one declarative paragraph**, consistently in §4, §6, §8, §9 |
| [P2] | §14.8.11 was described as a *mandate* on the pause journal; it is scoped to the protected result store | **ACCEPTED.** §1 now states it is the **model, not a conformance requirement**, and the recommendation no longer leans on it |

**Round 2 — 6 findings (4 × [P1], 2 × [P2]); all 6 ACCEPTED, none disputed.** No finding disturbed
the round-1 recommendation; four corrected claims *inside* it, one added a missed stale site, one
corrected an overstatement of the recommendation's uniqueness:

| # | Finding | Disposition |
|---|---|---|
| [P1] | The collision is reachable **inside one process** — `config` is per-call on `run()` (`api.py:632-636`) and `resume()` (`:1159-1166`); `_run_lock` (`:495`) only serializes and never pins a tenant. The two-deployment premise understated reachability | **ACCEPTED, verified empirically.** §1 rewritten; §7's *"a topology no local deployment has"* rider **withdrawn** and the withdrawal recorded |
| [P1] | Reading B's migration is not `none` — under (3a) its pre-upgrade records lack `tenant_id` and are refused, so B abandons outstanding pauses too | **ACCEPTED.** §5.1's migration column split into **abandonment** (shared by A/B/A+B) and **path change** (A/A+B only); §4's "zero migration" corrected |
| [P1] | (3b) adoption by **copy** is insufficient under A+B — the copied wrapper still lacks `tenant_id` and is rejected at the new path | **ACCEPTED.** (3b) is now an explicit **parse-and-stamp migration**, source untouched; the B-side equivalent (stamped re-append) named |
| [P1] | The legacy-abandonment witness was unsatisfiable — with no legacy probe, a legacy-only journal yields ordinary `absent` | **ACCEPTED.** NEW §5.3.1 sub-decision (accept `absent` vs a **diagnostic-only** legacy probe that never parses or resumes); witness (c) rewritten per-branch |
| [P2] | `Spec_Harness_Runtime_v1.md:5824` is also stale — the substrate contract still says `directory-fsync-on-new-file` while #1167 made both dir fsyncs unconditional | **ACCEPTED.** Added as the **fourth** fold-in at §9 item 4 and to the §10 table |
| [P2] | Reading A also preserves per-tenant resumability, so it is not an A+B-only advantage | **ACCEPTED.** §6 rationale items 1-3 and 5 re-attributed as **shared with A**; item 4 isolates the one thing A+B adds |

**Round 3 — 5 findings (3 × [P1], 2 × [P2]); all 5 ACCEPTED, none disputed.** One collapsed the
recommended reading's marginal case:

| # | Finding | Disposition |
|---|---|---|
| [P1] | The proposed `tenant + "\0" + workflow_id` key is **not injective** — `("a","b\0c")` and `("a\0b","c")` hash identically, re-creating the cross-tenant collision through valid inputs | **ACCEPTED.** §4 now carries an **injective-encoding contract term**; NEW spec-leg item 0; NEW witness (a′) |
| [P1] | A whole-directory restore **never reaches** the A+B wrapper comparison (the source tenant's filename is preserved; the other tenant looks up a different one), so the cited ops accident does not support A+B over A | **ACCEPTED, decisive.** §4/§5.1 narrowed to "explicit relocation into the exact path"; **recommendation moved A+B → A**; witness (b) re-specified so it cannot be written as a restore |
| [P1] | Under Reading A, (3b)'s unconditional stamping adds the wrapper key A excludes — silently converting the ratified reading into A+B | **ACCEPTED.** (3b) is now **reading-dependent**: relocation under A, parse-and-stamp under A+B, re-append under B; the coupling is stated at §8 |
| [P2] | The §5.3.1(ii) read-path diagnostic is an **existence oracle** — all tenants probe the same legacy path, so a distinct cause discloses a record for a guessed `workflow_id` | **ACCEPTED, recommendation withdrawn.** NEW §5.3.1(iii) moves the diagnostic to an **operator-only admin surface**; NEW witness (c′) asserts indistinguishability |
| [P2] | Reading C's "a topology no shipped configuration produces" premise is stale against §1's own correction | **ACCEPTED.** Narrowed to "no shipped deployment *recipe* pairs two tenants over one dir", which is what remains true |

**Round 4 — 3 findings, all [P1]; all 3 ACCEPTED, none disputed.** All three sharpen contract terms
*inside* the settled Reading A — none moved the recommendation:

| # | Finding | Disposition |
|---|---|---|
| [P1] | (3b) adoption is unsafe against a **live** owner — the owner can append to the legacy journal after the migration copies it, leaving the tenant-scoped target holding an older authoritative record (stale-state resume) | **ACCEPTED.** (3b) now REQUIRES a **quiescent/drained cutover or an exclusion effective through completion**, as a contract term |
| [P1] | Reading C's paragraph named *differently-tenanted **deployments***, leaving §1's single-process sequential route neither fixed nor declared unsupported | **ACCEPTED.** C's paragraph is now **topology-free**: reuse of one journal directory across two tenant scopes is unsupported regardless of process or deployment topology |
| [P1] | The tenant-**subdirectory** variant is path-unsafe — `tenant_id` accepts `/`, `..`, absolute paths and NUL; injectivity alone does not make a path component safe | **ACCEPTED.** The subdirectory alternative is **removed**; the hashed-filename form is path-safe by construction, and a future subdirectory layout owes encoding + containment validation as its own decision |

**Round 5 — 4 findings, ALL [P2] (no [P1] for the first time); all 4 dispositioned, one PARTIALLY
accepted with the divergence stated.** The severity drop from 3×[P1] to 0×[P1] is the convergence
signal:

| # | Finding | Disposition |
|---|---|---|
| [P2] | §6's Reading-C sentence still used **deployment-scoped** wording that §4 had already corrected | **ACCEPTED.** §6 now carries the topology-free form |
| [P2] | §7 sent C11 to weigh the **withdrawn** read-path probe (ii) rather than the live (i)-vs-(iii) choice | **ACCEPTED.** §7's C11 brief now names (i) vs (i)+(iii) and states (ii) is foreclosed |
| [P2] | The blocking-`flock` follow-up would be lost from `--open` when `B-97` closes | **ACCEPTED.** Leg 2 now owes a **split to its own `B-*` row** before closure |
| [P2] | Move the row to `design_substrate_gated` on a `B-70`/`B-92` precedent | **PARTIALLY ACCEPTED — the substance, not the prescription.** The direction is right and is now a leg-2 obligation; but the named status value **does not exist at HEAD** (programmatic count: `closed` × 81, `registered_finding` × 21, `held` × 1) and `B-70`/`B-92` are both `closed`, so the claimed precedent is not verifiable. Recorded as *refresh the row's prose to FILED + AWAITING RATIFICATION*, with any new enum member left to the ratification leg |

**Round 6 — 3 findings, all [P2]; all 3 ACCEPTED, including one that OVERTURNS a round-5 claim of
this filing's own:**

| # | Finding | Disposition |
|---|---|---|
| [P2] | `design_substrate_gated` **does** exist at HEAD — round 5's note claiming otherwise was wrong | **ACCEPTED, self-correction recorded in-body** (§9 leg 2). Verified: 12 occurrences in the register, 9 in `tools/forward_register.py`. The round-5 error came from counting only values **held** by rows and reading zero occupancy as a missing member. The **action** (the row flip) still rides leg 2, because the fork-filing PR is doc-only by standing instruction and by the `DESIGN_IMPL_MIX` guard |
| [P2] | Delimiter **rejection** is a public input-contract change, not an encoding detail — `tenant_id` rejects only `""`/`"_single"` and `workflow_id` is unconstrained | **ACCEPTED.** §4 now requires a **TOTAL** canonical encoding and demotes rejection to an explicit spec-leg-ratified input-contract narrowing |
| [P2] | Reading B's stamped re-append necessarily writes the legacy file, so it cannot also satisfy an unconditional "source untouched" rule | **ACCEPTED.** The source-file rule is now **reading-scoped**: orphan under A/A+B, append-never-rewrite under B; both satisfy `:5834` |

**Round 7 — 3 findings (1 × [P1], 2 × [P2]); 2 ACCEPTED, 1 accepted-in-substance-declined-in-action:**

| # | Finding | Disposition |
|---|---|---|
| [P1] | **Sequencing contradiction** — §8's single ask settles the (3a)/(3b) default and the §5.3.1 diagnostic, but §7 convenes C3/C11 to price exactly those; convening afterwards has the operator decide without the council's input and leaves a disagreement with no ratification path | **ACCEPTED.** §7 restructured into **two gates**: gate 1 ratifies the reading → dyadic convenes on the two priced sub-decisions → gate 2 is a narrow two-row confirm/override. §8 now labels itself gate 1 and marks those two rows **provisional** |
| [P2] | Leg-3 item 0 still permitted delimiter rejection, contradicting §4's ruling that rejection is an unratified input-contract narrowing | **ACCEPTED.** Item 0 now requires a **total** encoding and admits rejection only on explicit operator selection |
| [P2] | Do the register flip in the filing PR — `forward-register.yaml` is not a `DESIGN_IMPL_MIX` surface | **SUBSTANCE ACCEPTED, ACTION DECLINED.** The point that the register under-reports the gate is correct and the flip is leg 2's first action; but this PR's doc-only scope is a **standing instruction**, not a guard consequence — the over-attribution to `DESIGN_IMPL_MIX` in the previous draft is corrected in-body |

**Round 8 — 4 findings (2 × [P1], 2 × [P2]); all 4 ACCEPTED:**

| # | Finding | Disposition |
|---|---|---|
| [P1] | Quiescence is **not sufficient** for (3b) — if the upgraded deployment already captured a pause at the new key, adoption writes **older** legacy state over/after **newer** state | **ACCEPTED.** (3b)'s contract term is now three-part: quiesced owner **+** adoption before any new-format write **+** refusal of an already-populated target, or an explicitly specified newest-record-preserving merge |
| [P1] | **Gate 2 was missing from leg 2's obligations** — the sequence handed the council record straight to leg 3 | **ACCEPTED.** Leg 2 is now an explicit three-step sequence, with **"leg 3 MUST NOT open before gate 2 answers"** stated |
| [P2] | Reading B's legacy refusal cause is undefined — an untenanted record has *unknown* ownership, so `cross-tenant` mislabels it and `corrupt-latest` mis-states a well-formed record | **ACCEPTED.** §8's B row now requires the cause to be **settled at ratification**, not left to the impl leg |
| [P2] | The council exemption for B does not survive round 2's own correction — B abandons pre-upgrade pauses too, which is C11's cost | **ACCEPTED.** The dyadic is now owed under **A, A+B and B**; only C is exempt |

**Round 9 — 3 findings, ALL [P2], and all three confined to Reading B's internal decision surface**
(none touched the recommended reading); all 3 ACCEPTED:

| # | Finding | Disposition |
|---|---|---|
| [P2] | Reading B's legacy refusal cause was named as an obligation but never *specified* — gate 1 could not actually settle it | **ACCEPTED.** NEW §5.2.1 gives three shapes ((B-2-i) seventh member / (B-2-ii) widen `cross-tenant`'s definition / (B-2-iii) fold into `absent`) with a recommendation |
| [P2] | The round-8 empty-target rule makes B's adoption **impossible** — B re-appends into the file that already holds the records being adopted | **ACCEPTED.** Term (2) restated as *no **tenant-stamped** record at the target*, which reduces to "empty" under A/A+B and "not already stamped" under B |
| [P2] | Gate 2 was specified as two rows for every reading, but §5.3.1's diagnostic question does not arise under B | **ACCEPTED.** Gate 2 is **two rows under A/A+B, one row under B**, exempt under C |

**Round 10 — 2 findings (1 × [P1], 1 × [P2]); both ACCEPTED. The [P1] struck the RECOMMENDED reading,
which is the reopening criterion the round-9 exit note had just declared — so the exit was
REOPENED rather than defended.** That is the note working as designed, and it is recorded as such:

| # | Finding | Disposition |
|---|---|---|
| [P1] | **Mixed-version rollout** — the (3a) loss bound *"pauses outstanding at the moment of upgrade"* holds only for an atomic cutover. Old processes keep writing legacy paths through a rolling deploy (A/A+B); and under **B** `_parse_snapshot_attributed` (`:594-611`) **ignores unknown wrapper keys**, so an old reader accepts a new tenant-stamped record **without checking the tenant** — the binding is silently bypassed for the whole mixed window | **ACCEPTED, verified at HEAD.** NEW §5.3.2 requires a **no-mixed-version / quiesced cutover** (recommended) or a version marker old readers reject (noted as non-retroactive); NEW spec-leg item 5-bis |
| [P2] | Under a tenant-composite key, §30's `absent` row (`:3318`) and its operator repair become **wrong** for a wrong-tenant lookup and for an abandoned legacy record; `B-102` is therefore **not** the only reason to touch §30 under Reading A | **ACCEPTED.** NEW spec-leg item 4-bis tenant-scopes the row's meaning + repair (a definition amendment, no new member); the earlier "only reason" claim is corrected in place |

**Round 11 — 4 findings (2 × [P1], 2 × [P2]); all 4 ACCEPTED. Every one is an ADDITIVE obligation on
a downstream leg, not a defect in the analysis or the recommendation:**

| # | Finding | Disposition |
|---|---|---|
| [P1] | §5.3.2's (a) and (b) were offered as alternatives, but (b) cannot close **this** window — old readers cannot be retrofitted to reject a marker they never knew about | **ACCEPTED.** (a) is now **MANDATORY** for this transition; (b) is demoted to a forward-compat addition, explicitly never a substitute |
| [P1] | (3b) adoption is not **crash-atomic** — quiescence and the empty-target test exclude concurrent writers, not the migration process dying mid-flight, which can leave a valid older prefix or a torn final record at the new path | **ACCEPTED.** (3b) gains a **fourth** contract term: crash-atomic, durable, no-replace publication with recoverable retry, mirroring §14.8.11 `:4809` rather than re-deriving it |
| [P2] | §7's blanket *"no reading adds operator data entry"* is false when (3b) is selected — (3b) requires an operator-declared assertion, which is the register antecedent's literal declaration burden | **ACCEPTED.** §7 now splits the antecedent: false on the (3a) default path, **true under (3b)**, and C11 is briefed to price both |
| [P2] | Folding `B-102`'s amendment in without closing its **row** leaves shipped work presenting as open in `--open` | **ACCEPTED.** NEW leg-3 item 5-ter; the leg's register obligations are now **three** rows |

### **SOUNDNESS EXIT — declared after round 11 (first declared after round 9; REOPENED by round 10's [P1] against the recommended reading; re-declared and held here). This filing is CLOSED to further review rounds.**

**PD-9 non-convergence discriminators, applied on the record at round 10** *(Workflow v1.19 §7.5;
run because 10 rounds is where "converging" and "arms race" become hard to tell apart)*:

1. **Did the round-10 [P1] INVALIDATE the recommended reading's premise, or NARROW it?** — **Narrow.**
   Reading A's premise is *segregate the address space so no read reaches another tenant's state*.
   The mixed-version finding leaves that premise untouched and adds a **transition-window** contract
   term (§5.3.2). Same premise, tighter mechanics → per the discriminator, **apply, run one more
   round, then exit** — which is exactly what rounds 10→11 did. Had it invalidated the premise, the
   correct response would have been to restructure and let the ratification carry the choice, **not**
   to swap recommendations silently at round 10.
2. **Has the recommendation flipped 3+ times?** — **No: twice.** B → A+B (round 1 [P1]: a shared file
   destroys per-tenant resumability) → A (round 3 [P1]: A+B's cited accident class does not reach the
   check). Both flips were forced by **verified facts about HEAD**, not reviewer preference, and each
   moved *toward* the simpler reading. **Below the `[[reviewer-oscillation-register-and-hold]]` cap of
   3** — register-and-hold is therefore **not** triggered, and this note records the count so a later
   session need not re-derive it.
3. **Is the finding stream still about the artifact's decision surface, or about its obligation
   list?** — **Obligations.** All four round-11 findings were additive spec-leg terms. That is the
   signal the decision surface has stabilised.

The exit criterion is **soundness, not reviewer silence**
(`[[deferred-mechanism-spec-leg-exit-on-soundness]]`). Rounds 1-3 moved load-bearing substance (the
recommended reading twice, the council disposition once). Rounds 4-6 sharpened contract terms inside
the settled reading. Rounds 7-9 produced zero findings against the recommended reading (round 7's
[P1] was a sequencing repair; round 8 split between a real (3b) hazard and two book-keeping repairs;
**all three** of round 9's concerned Reading B, which this filing does not recommend — completing a
non-recommended option's decision surface is the filing's job, not a defect in it). **Round 10 then
produced a genuine [P1] against the recommended reading — the mixed-version rollout window — and the
round-9 exit was reopened to absorb it, which is the only correct response to a criterion the note
itself had named.**

**Round 11's four findings were all ADDITIVE obligations on downstream legs** — a mandatory-cutover
tightening, a crash-atomic publication term, a burden-analysis split, and a register-closure line —
**not defects in the readings, the recommendation, or the sequencing.** That is the shape a filing
converges to, and it is the exit condition: the document's *decision surface* is stable while its
*obligation list* grows, and an obligation list can be extended at the spec leg without re-opening the
operator's question.

The held exit rests on this: the arc of severity is **decisively downward** (3 recommendation-moving
[P1]s in rounds 1-3 → 1 recommendation-touching [P1] in round 10, on a transition-window property
rather than the design → 0 in round 11), and every surviving item is a **spec-leg obligation this
filing names**, not an unresolved question inside it. Per
`[[non-convergent-adversarial-hardening-arms-race]]`, continuing to round 12+ would be chasing an
arms race against a stable artifact.

**What that binds, by rule rather than by enumeration:** any *non-recommended* reading's remaining
under-specification is a **gate-1 obligation** (the operator must be told what selecting it would
leave open) and is discharged for A+B, B and C at §4, §5.2.1, §5.3 and §8. Any surface not listed
there is, by this note, **not silently in scope for an impl leg**. Findings that would reopen this
filing regardless: a defect in the **recommended** Reading A, in the injective-encoding contract
term, in the two-gate sequencing, or in a cite that fails to resolve at HEAD.

**Reversals and withdrawals are recorded in-body rather than silently applied.** The recommendation
moved **B → A+B** (round 1 [P1]: a shared file destroys per-tenant resumability) and then **A+B → A**
(round 3 [P1]: A+B's marginal accident class does not exist as claimed); the council disposition
flipped to *convene* at round 1 and its supporting rider was withdrawn at round 2; the §5.3.1
diagnostic recommendation was withdrawn at round 3. Each move followed a **verified factual
correction**, not reviewer preference — the `[[reviewer-oscillation-register-and-hold]]` cap is not
engaged, and the `[[over-correction-away-from-mostly-right-baseline]]` discipline runs the other way
here, because the draft-1 baseline was wrong on load-bearing properties rather than mostly-right.
