# Council Record — `B-96` Reading C: the reclaim-ceiling sub-decision (C-1 ⊥ C-2)

**Convened 2026-08-01. C3 primary + C10 consultant + C7 Layer-D add. Scope: the ONE held sub-decision. Verdict: C-2.**

> **DRAFT — NOT RECONCILED-TO-ZERO. <!-- WIP: resume here -->** Deliberation is COMPLETE and the **verdict is stable** (unanimous across three voices; attacked on arithmetic, on its impossibility result, on cite fidelity, on primary-collapse and on scope, and undisturbed by all of it). Reviewer rounds are **not** complete: out-of-family round 1 (6 findings) and the in-family adversarial pass (12 findings) are **fully absorbed**; **out-of-family round 2 returned 3 further findings that are VERIFIED and UPHELD but NOT YET FOLDED** — see **§11.2b**. Two are routed to their authoring voices and had not returned when work was halted by operator pause. **Do not treat §7.1's condition set or §6's TENSION block as final until §11.2b is closed** — specifically, condition #5 under-covers `.tmp-*` observations, condition #6's adequacy argument rests on a log-durability premise that is **false at HEAD**, and §6's TENSION-1 records a position no convened voice held.

**Authority.** `.harness/class_2_fork_b96_gc_grace_elapsed_time_bound.md` §7 (*"CONVENE — dyadic C3 + C7, scoped to the single question 'C-1 or C-2'"*) + §8's held sub-ask + `.harness/forward-register.yaml:2860` `B-96`'s `council:` field (*"conditional … convene if the elapsed-time variant is taken"*). The operator **RATIFIED Reading C** on 2026-08-01, post-filing (PR #1179), which fires the condition.

**Posture.** Design-phase, additive-only. This record is `.harness/` back-flow documentation. **No `design-substrate/**` file is edited by this arc** — the spec leg the fork's §9 owes is a separate, later PR. X-AL-3 clean (independently confirmed at §11).

**Grounding HEAD.** `04214750`. `git diff --stat 6d557c26..HEAD` over `protected_result_store.py`, `types.py`, `Spec_Harness_Runtime_v1.md` and `test_lifecycle_protected_result_store.py` is **EMPTY** — every line cite in the fork doc resolves unchanged at this HEAD, re-verified by direct read rather than carried.

---

## §0 Convening Block

| Field | Value |
|---|---|
| **Question type** | **Tradeoff** (durability axis — the prompt asks for a build/don't-build decision between two named forms), with a **Contract** sub-question (what §14.8.11 must carry). Classified per `routing-rubric.md` Layer B: *"if the prompt asks for a decision … it's a tradeoff."* |
| **Voices convened** | **C3 — State, Memory & Persistence** (PRIMARY) · **C10 — Action Safety & Blast Radius** (CONSULTANT) · **C7 — Observability** (CONSULTANT, **Layer-D add**, joined after round 1) |
| **Routing rationale, per voice** | **C3 (primary):** the question is *"should the reclaim rule carry a second, mtime-keyed term"* — a durability/eviction-policy contract over durable state. C3's strong-keyword band carries *retention policy*, *garbage collection*, *eviction policy*, *durability*, *crash recovery*, *atomicity*, *filesystem state*, *idempotent write* (`voice-roster.md:37`); Layer B's Tradeoff row routes the durability axis to C3. No other voice is a candidate for primary. **C10 (consultant):** sole owner of cross-cutting concern #1 (`voice-roster.md:112`), which is the concern the disputed spec term invokes by name — *"an unbounded store of **sensitive payloads**"* — and the holder of the retention-side position the fork names. **C7 (Layer-D add):** sole owner of concern #2 (`voice-roster.md:113`); added at round 2 because the convening had produced **binding emission conditions** with an emission predicate defect that neither convened voice caught (§11 R-1). Layer D auto-approves at total ≤ 5. |
| **Convening size** | 2 → **3** (dyadic default, expanded by a Layer-D add with the distinct third concern named, per the 2026-05-31 standing amendment + `routing-rubric.md` Layer D) |
| **Nameable tension, declared in advance** | *"An age authority that cannot predate publication"* (C3) ⊥ *"a retention bound with one fewer premise, where the payload is sensitive"* (concern #1). Both positions were live and neither was refuted by any source the fork could reach — the §10.9 nameable-tension discriminator is satisfied. |
| **Voices considered, NOT convened** | **C8 (Eval)**, **C9 (Reliability)**, **C11 (Operator loop / local-first)** — see §0.1 |
| **Pre-check status** | CCR emitted **before** voice contributions (§1). Six concerns pre-checked; four Touched, two `n/a`. |
| **Mechanism** | Genuine invocation. Each voice ran as a dedicated agent that FIRST adopted its `.claude/skills/council/cN-*/SKILL.md` and then acted. The orchestrator composed the envelope and wrote this ledger; it did not speak for the voices. *(Not verifiable from this artifact alone — noted at §11.)* |

### §0.1 Second-voice selection — the fork named C7/C8; Layer C scoring said **C10**; C7 was then added at Layer D

**The orchestrator's convening brief explicitly authorized the re-check**, in terms: *"check the orchestrator's voice-domain map and select the second voice per Layer C scoring if C7 is not the right holder of the retention-bound concern; the filing named C3+C7."* `routing-rubric.md` Layer A is an **operator** override and is terminal *when the operator names voices*; here the operator's instruction was the opposite — it named the filing's assignment and directed that it be re-scored. Recording that authorization explicitly, because without it the substitution would read as a silent deviation from a filed, operator-visible disposition.

**The Layer C scoring:**

- The disputed term is §14.8.11's *"a signing outage must not grow an unbounded store of **sensitive payloads**"* — data **at rest**. That is cross-cutting concern **#1 security & blast radius**, whose **sole owner is C10** (`voice-roster.md:112`, verified byte-exact). C10's strong-keyword band carries *secrets at rest*, *content capture posture*, *blast-radius classification*, *audit trail / audit integrity*, *redaction* — all of which this question hits.
- **C7's** band (`voice-roster.md:69`) is *OTel / span / trace / attribute / sampling / exporter*. **Nothing in the held sub-decision itself is span-shaped**, which is why C7 was not the *retention-bound* holder.
- **C8's** stake (is the bound measurable?) is carried by conditions #8/#12 and their owner is C7. Not separately convened.
- **C9** — the repair-flow consumer's retry policy. C3 declared the seam and did not specify it; the fork's §3(iii) grounds that **no production consumer exists at HEAD**. Nothing to adjudicate.
- **C11** — the round-6 [P1] operational-independence premise (a selective backup or dotfile-skipping cleanup drops the sidecar) is C11-flavoured. It was posed to **both** convened voices as a required item rather than convened separately; both engaged it substantively.

**Then the substitution's cost surfaced, and C7 was convened after all.** The re-score was right about *the retention-bound concern* and incomplete about *the convening's output*: the deliberation produced **binding observability conditions**, and out-of-family review (§11 C-1) correctly found that the observability owner was absent while its domain was being legislated. **C7 was added at Layer D** — both convened voices had explicitly deferred emission *schema* to it, which is a Layer-D self-volunteer in substance. C7's contribution (§4A) then **found a real defect in the emission predicate C3 and C10 had authored**, which is the strongest available evidence that the add was owed rather than ceremonial.

**Net disposition:** the fork's `C3 ⊥ C7/C8` framing was **mis-assigned on the retention concern** (C10 owns it) and **right that C7 was owed** (for the emission surface). The final convening — **C3 + C10 + C7** — satisfies both readings. Recorded as a correction to the fork, not a silent normalization.

### §0.2 A limit on this convening's adversarial depth, stated plainly

**No convened voice argued C-1.** C10 was convened to hold the retention side and instead **defeated C-1 from inside its own domain** (§4.2, §4.3); C7 concurred with C-2 and confined itself to emission. The register's C7/C8 assignment (`forward-register.yaml:2908`–`:2911`) was **role-based, not keyword-based** — it named the voices expected to *want* the bound, and §0.1's rebuttal addresses the keyword reading only.

So the C-1 side was tested by **three** mechanisms rather than by an advocate: (i) C10's own construction attempt across three ceiling variants, all of which it killed (§4.2); (ii) the adversarial reviewer's construction of a **fourth** variant (`ctime`-keyed) that C10 had not enumerated — which is a genuine finding and which dies for the same reason as the first (§4.2b); (iii) the fork's own six out-of-family rounds, four of which sharpened C-1's pricing specifically. **That is a real but not identical substitute for an advocate, and the record does not claim otherwise.**

---

## §1 CCR (slim mode)

**Touched:**

| # | Concern | Owner status | Pre-check note |
|---|---|---|---|
| 1 | Security & blast radius | **C10 — convened** | The whole retention side. C10 classified the two failure modes under its own four-tier taxonomy (`c10-action-safety-blast-radius/SKILL.md:141`, `:159`) and found them non-comparable — §4.5. |
| 2 | Observability hooks | **C7 — convened (Layer-D add, round 2)** | Initially marked handled-by-reference; **that was wrong and was corrected** (§0.1). C7 owns conditions #6/#8/#11/#12 and rewrote two of them. |
| 4 | Reliability & failure containment | C9 — **handled-by-reference**: `c9-reliability-recovery/SKILL.md` §"cross-cutting obligations" (breaker/gating semantics) | C10 declared **nothing owed**: GC is not a gated action; the `:4905` fail-closed write disposition is unchanged by either form. Declared rather than left implicit. |
| 5 | Eval-ability | C8 — **handled-by-reference**: `c8-eval-engineer/SKILL.md` §"standing pre-check on what's measurable about a contract being designed" | C3 surfaced that *"the store is bounded"* is **not measurable at HEAD** — `I` is un-instrumented, so the retention statement is unfalsifiable in the field **under both forms**. C7 then showed a sweep-time-only gauge does not fix it and specified a pull surface (#8). |
| 6 | HITL & local-first | C11 — **handled-by-reference**: `c11-operator-loop-local-deployment/SKILL.md` §"escalation trigger catalog" | C10 **declined** to add an escalation trigger under C-2 (gate-fatigue on a path with no operator context) and recorded, asymmetrically, that **C-1 *would* raise the trigger question** — an ungated `write-bounded-irreversible` action the fork never priced. |

**n/a:** #3 token economy & cost — addressed quantitatively (≈80 bytes/entry; one `os.replace` + two fsyncs per sweep that finds any past-TTL entry, on a path already holding both locks) and found negligible by both voices; no cost-owner voice convened.

---

## §2 Probe log (probe-first discipline, §10.9 amendment 5)

Run by the orchestrator **before** convening, and re-verified independently after each voice returned and again by the adversarial pass (§11). Every finding resolved by direct read at HEAD `04214750`.

| # | Probe | Finding |
|---|---|---|
| **P1** | Do the fork's cites still resolve? | **YES.** `git diff --stat 6d557c26..HEAD` over the four carrier files is empty. No cite drift. |
| **P2** | §14.8.11's retention word | **"unbounded"**, not "exactly TTL" (`Spec_Harness_Runtime_v1.md:4909`; head **v1.109** at `:1`). A `k×TTL` or `≈2×TTL` bound satisfies the term. **This probe was already spent by the filing — which is why the tension RELOCATED into the ceiling choice rather than dissolving.** |
| **P3** | Does the deferred-to-discretion list cover a grace? | **NO** (`:4911` names the TTL config carrier's field name and default value, the envelope/DEK format, the typed refusal/declaration class names, the expiry report-line format, the composite-key serialization, the module/class/API names, and the repair-acknowledgement marker shape — **no grace**). A spec leg is genuinely owed. Confirms the fork's §9. |
| **P4** | How many production sweep triggers? | **Exactly THREE** (whole-tree grep): `bootstrap/stage_4_od.py:123`, `shutdown.py:800`, and `_maybe_opportunistic_gc_sweep` (`protected_result_store.py:882`) reached **only** from `write_once` (`:399`). **No timer, no periodic sweep anywhere.** The opportunistic trigger is **write-driven, not time-driven**. |
| **P5** | Where does the opportunistic sweep sit relative to publication? | **BEFORE it**, in the same `write_once` call (`:399`, with `:392`–`:398` stating why: *"Sweeping first can only ever touch OLDER entries — this one doesn't exist yet"*). An entry's first possible observation is **always a strictly later sweep**. |
| **P6** | Is `I` (the sweep interval) bounded? | **NO — under BOTH forms and at HEAD today.** One-shot `harness run`: the next sweep is the next process invocation, which may never come. Daemon: needs a further write or shutdown. **This is the finding that reprices the whole retention argument (§3.4).** |
| **P7** | Δ, quantified | normal path ≈ 0 (post-commit stamp `:581`); **B-77 crash window** = fsync(tmp fd) `:567` + `os.link` `:570` + `_fsync_dir` `:571` → sub-ms to a few ms on the committed surfaces; **B-74 coarse FS** Δ ≤ G, and the `B-74` row itself scopes that to *"legacy FAT32, or certain network filesystem configurations; **NOT** the modern POSIX filesystems — ext4/APFS/NTFS — this workspace's committed local-development/self-hosted-server/managed-cloud deployment surfaces default to"* (`.harness/forward-register.yaml:1718`–`:1721`). |
| **P8** | Δ in the `B-74` witness — **an orchestrator correction to the fork, itself corrected twice under review** | The fork cites the witness as *"Δ ≈ 1.0s"* (§3(ii), §4, §10.1 rounds 3–5). **That number is not what the test produces.** The witness spins on `while not 0.3 <= time.time() % 1.0 < 0.9` (`test_lifecycle_protected_result_store.py:1966`) before publishing, to make the flooring error deterministic and kill a ~10% flake. **This record's first correction — "Δ ∈ [0.3, 0.9) guaranteed" — was ALSO wrong, in both directions, and both errors were caught under review (§11 C-6, F1-06):** the guard constrains the clock **at loop exit**, while the flooring stamp lands later, inside `write_once` after serialize/encrypt/mkstemp/write/fsync (`:557`, `:581`). So the fraction at the *stamp* can exceed `0.9` **and**, if the second boundary is crossed, can fall near zero. **The honest statement:** Δ is the fractional part of wall-clock **at the patched `os.utime` call**, which the phase guard makes *overwhelmingly likely* to sit in `[0.3, 0.9)` because `write_once` completes in milliseconds, but **does not guarantee**. The test's operative enforcement is its own `:1973` assertion (`time.time() - mtime > 0.1`), which only bounds Δ **below** at the TTL. |
| **P8-a** | What P8 does to the §3.3(b) discriminator | **The conclusion holds and is sharpened.** Under C-1 k=2 the first-sweep firing threshold is `k·TTL = 0.2` and the phase guard's floor is `0.3`, so the inversion is the overwhelmingly common case — but because Δ is not *guaranteed*, C-1 would make `:1975` **nondeterministic** rather than deterministically inverted. **A flaky witness on a live-entry-survival assertion is worse than a deterministically inverted one**, so this strengthens rather than weakens the finding. At k≥4 (threshold ≥0.4) the witness would no longer reliably demonstrate the regression at all. |
| **P9** | `_entry_path` shape (C10's §6 ground) | **Confirmed** (`:379`–`:381`): `sha256(composite_key).hexdigest() + ".entry"` — entry filenames are **one-way**; the flat store root leaks neither tenant nor ref. `read()` (`:598`) does `composite_key.split(":", 1)[0]`, i.e. **the composite key is simultaneously the retrieval capability AND a cleartext tenant discriminator**. `_observe_expired` today receives **filenames, never composite keys**. |
| **P10** | Encryption-at-rest (C10's §3 ground) | **Confirmed** (`:4904` + `protected_result_store.py:300`–`:308`, encrypt at `:446`): the payload is encrypted under a **locally-held, provisioning-time-wrapped DEK**, independent of the audit-signing KMS. Neither the fork nor the register row uses this fact anywhere. |
| **P11** | Is there a metrics pipeline or an OTel log bridge? *(C7's probe, round 2)* | **NO to both.** Whole-tree grep for `get_meter` / `MeterProvider` across `harness-od`, `harness-runtime`, `harness-cp`, `harness-core`: **empty**. Same for `LoggerProvider` / `LoggingHandler` across `harness-od` + `harness-runtime`: **empty**. The report log is a stdlib-logger sink that never enters the OTel pipeline. **Load-bearing for conditions #8 and #12.** |

**Probe outcome, stated per the discipline:** the probes **did not resolve** the C-1 ⊥ C-2 tension by themselves — P2 was already spent by the filing. What P4/P5/P6, P9/P10 and P11 did was **reprice both sides and constrain the emission surface**, which is what let three voices converge on the merits rather than on preference. The convening was owed and was not a formality.

---

## §3 C3 — State, Memory & Persistence (PRIMARY). **Position: C-2.**

First cite, pre-bound: `Spec_Harness_Runtime_v1.md` **v1.109** §14.8.11 `:4909`. C3 opened on a half of that sentence the fork never used: it forbids *"silent loss of the last reference to a paid effect"* and licenses only the typed reporting of an **expired** entry's collection. **A reclaim that destroys a live entry is not an expiry, so no report-line makes it conforming.** C-1 admits that outcome by construction; C-2 does not.

### §3.1 The ceiling is not a second safety term — it is `B-74`'s twice-declined TTL floor, re-introduced implicitly and unenforced `[HIGH]`

C-1's reclaim rule is a **disjunction**: reclaim if (grace satisfied) **OR** (`now − mtime > k·TTL`). *A disjunction's safety is the minimum over its arms, never the maximum.* The ceiling arm consults `mtime` and nothing else — and `mtime`'s untrustworthiness as an age authority is the **thesis of all three rows**, not a side finding.

The ceiling is safe iff `Δ ≤ (k−1)·TTL`. On a volume of granularity `G`, `Δ ≤ G`, so the ceiling is safe **iff `TTL ≥ G/(k−1)`**. That is a TTL floor keyed on the filesystem's timestamp granularity — `B-74`'s explicitly declined close_out option (declined twice: once by Codex, once by advisor) — **re-introduced with `k` as the fudge factor, and never evaluated**. The explicit floor was declined *because `G` is unprobed* (`forward-register.yaml:1731`–`:1734`); C-1 does not solve that, it assumes a value for it and, when the assumption is violated, does not refuse — it silently deletes a live entry.

> **C3 is not proposing a floor. C3 is observing that C-1 *is* one, in the one shape the arc already rejected.**

### §3.2 `k` cannot be tuned out of this `[HIGH]`

| | safety regime | retention |
|---|---|---|
| C-1, k=2 | `Δ ≤ 1·TTL` | `2·TTL + I` |
| C-1, k=10 | `Δ ≤ 9·TTL` | `10·TTL + I` |
| **C-2** | **all Δ** | `2·TTL + 2I` |

`k` moves safety and retention **one-for-one in the same direction**. At the `k` that makes C-1 safe against an unprobed `G`, its retention is worse than C-2's *on the very axis C-1 exists to improve*; at the `k` that makes its retention better, it is unsafe. **There is no setting delivering both.** Corollary, conceded cleanly rather than hedged: **there is no safe ceiling** — restated precisely at §4.2b after review.

*(Attacked at §11 F-rejected-2 with a large-`I` counterexample — at k=3, T=1, I=100, C-1's 103 beats C-2's 202. The claim survives because its antecedent is "the `k` that makes C-1 safe against an **unprobed** `G`", which is unsatisfiable at any finite `k`.)*

### §3.3 The regression case, quantified — and it is a green test at HEAD that C-1 inverts `[HIGH]`

| | wrongful window | width | sweeps needed in it |
|---|---|---|---|
| **HEAD** (sweep-count) | `t ∈ (t_pub + TTL − Δ, t_pub + TTL]` | `Δ` | **TWO** |
| **C-1** (ceiling arm) | `t ∈ (m + k·TTL, t_pub + TTL]` | `Δ − (k−1)·TTL` | **ONE** |
| **C-2** | **∅** | — | — |

Non-empty iff `Δ > (k−1)·TTL`; first-observation firing additionally needs `s + Δ > k·TTL` for observation delay `s`; wrongfulness needs `s ≤ TTL`. Jointly satisfiable iff `Δ > (k−1)·TTL`, so **at k=2, `Δ > TTL`**. *(Re-derived independently by C3, by C10, and by the adversarial pass — §11 F-rejected-1. Every step confirmed; nothing to correct.)*

**Two things that arithmetic understates.**

**(a) The sweep-count column is the point.** Every reachability argument on the `B-74`/`B-77` arcs has been about whether *two* sweeps fall inside `Δ` — a **conjunction of two independent timing facts**. C-1 deletes one conjunct. **The reachable set widens even where the window narrows.**

**(b) It is not a hypothetical regime.** At `test_lifecycle_protected_result_store.py:1924`–`:1982` (`ttl_seconds=0.1`, coarse-floored `utime`):

```
:1975   assert store.gc_sweep(now=time.time()) == []                        # LIVE ENTRY SURVIVES
:1976   assert store.read("tenant-a", ref) == "live despite a coarse mtime"
:1982   assert store.gc_sweep(now=time.time()) == [entry_path.stem]         # B-74 RESIDUAL, pinned
```

Under **C-1 k=2** the ceiling test at `:1975` is `Δ + s > 0.2`, satisfied at the **first** sweep for the phase-guarded Δ (P8/P8-a). `:1975` flips to `== [entry_path.stem]` and `:1976` **raises `ProtectedStoreEntryNotFoundError`** — the impl leg would rewrite a green assertion whose subject is literally *"live despite a coarse mtime"* into an assertion that the live entry was destroyed, and would void the **mutation probe** recorded in that test's own docstring (`:1946`–`:1948`), which derives its meaning from `:1975` failing when the grace is removed.

Under **C-2**, `:1975`/`:1976` survive **unchanged** and only `:1982` flips to `== []` — exactly what its own comment at `:1978`–`:1981` demands.

> **One form updates the pin the pin asked to be updated. The other inverts the assertion the pin was placed to protect.** This is the cleanest empirical discriminator on the table and it is checkable at HEAD today. *(Independently re-derived against the live test by the adversarial pass — §11 F-rejected-3.)*

### §3.4 P6 reprices the retention argument: `I` dominates both bounds `[HIGH]`

At k=2, `C-1 = 2·TTL + I` and `C-2 = 2·TTL + 2I`. **The TTL terms are identical.** The entire retention advantage C-1 purchases — for which it pays a live-entry loss — **is exactly one `I`**, and `I` is unbounded under both forms and at HEAD today.

**And C-2's `2I` is not additive against HEAD the way the formula suggests** `[MODERATE]`. `_root_observed_expired` is module-level and in-process (`:111`), so HEAD **discards every observation at process exit**. In the one-shot shape, HEAD's run-2 bootstrap starts from an empty registry, records, and refuses — reclaim waits for run 2's *shutdown*. C-2's durable record means run 2's **bootstrap** reclaims whenever `I ≥ TTL`. **In that regime C-2 reclaims *sooner* than HEAD**, because the durable record recovers observation work HEAD throws away at every process boundary.

### §3.5 The two C-2 premises, stress-tested

**(a) Sweep cadence — not a differentiator in DIRECTION; not identical in MAGNITUDE.** It is HEAD's premise, C-1's premise, and the spec's own (`:4909` requires *"a periodic-**or-opportunistic** RUNTIME sweep"*; the shipped opportunistic arm satisfies the letter). *(Corrected under review — §11 F1-04: no sweep ⇒ no reclaim under either form, so the direction is symmetric, but C-2 carries `2I` to C-1's `I`, i.e. **twice the sensitivity**. The original *"tightens BOTH identically"* wording overstated the symmetry and is withdrawn.)*

*Class-3 observation, surfaced against interest and explicitly NOT a third option:* the spec's **purpose clause** for that arm is *"a long-lived daemon that never restarts must still bound the store."* The shipped trigger being write-driven (P4) means a daemon that suffers one signing failure and then goes quiet **never sweeps again until shutdown**. Latent gap at HEAD, **pre-existing and orthogonal to C-1/C-2** — a separate register row, and per the fork's soundness exit it does not reopen the filing. Raised because it is the correct answer to the retention-side concern: *if you want a bound with fewer premises, the highest-leverage move is making `I` bounded, not making the reclaim rule unsafe.*

**(b) Sidecar durability — the round-6 [P1] withdrawal is factually correct; its weight is disputed on three grounds.**

1. **The record is a derived index, not a second authority** `[HIGH]`, with a falsification criterion offered up front: *if record absence can produce any outcome other than longer retention, it is an authority and C3 is wrong.*
2. **One of the two named loss channels is eliminable inside the ratified carrier at zero cost** `[HIGH]`. Round 6 names *"a selective backup/restore, a **dotfile-skipping copy**, or an operator cleanup."* `(C-i)` requires only disjointness from both sweep globs — **a dot prefix is not required**. A **non-dot-leading** name satisfies the constraint identically and is immune to the dotfile channel.
3. **Compounding requires a loss cadence faster than `TTL + I`** `[MODERATE]` — more than once a day at factory default. Not a steady state; a broken operational loop. And the same loop pointed one directory-entry to the left destroys the `*.entry` payloads themselves, which no ceiling prevents.

---

## §4 C10 — Action Safety & Blast Radius (CONSULTANT). **Type: propose-refinement. Verdict: C-2**, reached on its own grounds, not by deference.

C10 deliberately did **not** open on C3's `:4909`. Its anchor is §14.8.11's **disposition posture** three bullets above: `:4903` write-once *"REFUSED TYPED, never overwritten"*, `:4905` *"FAIL-CLOSED store-write disposition … SAYS SO TYPED"*, `:4906` cross-tenant *"REFUSED TYPED"* — and `:4904`, the encryption bullet **neither the fork nor C3 had used anywhere** (grep-verified: zero hits for `4904` in the fork doc).

### §4.1 C-1 inserts the section's only fail-OPEN term `[HIGH]` — a C10 finding, not a C3 one

C3's floor-identity is right; C10 sharpens *why the two objects differ*. The declined floor is a **config-time typed refusal**. The ceiling is a **runtime silent destructive action taken on an unchecked precondition** — a precondition (`Δ ≤ (k−1)·TTL`) that is never evaluated, whose violation is never surfaced, and whose consequence is destruction of the last recoverable copy of a completed paid effect.

> In C10's permission-pipeline vocabulary this is **a gate that returns `allow` on an input it never read** — under-gating (FM-E), in the one section of this spec that is fail-closed at every other branch.

### §4.2 C10 tried to break C3's "no safe ceiling" **on its own side's behalf** and could not `[HIGH]`

It constructed and tested three variants — the two the fork's §7 floats (*"a record-keyed ceiling, or a larger `k`"*, `class_2_fork…:562`–`:563`) plus a **hybrid of its own construction** *(attribution corrected under review — §11 F1-05; the hybrid appears nowhere in the fork)*:

| Ceiling variant | Publication-bounded? | Robust under record loss? | Disposition |
|---|---|---|---|
| **mtime-keyed, larger `k`** (fork-floated) | No — safe only for `Δ ≤ (k−1)·TTL`; **no finite `k` is universally safe** (`Δ ≤ G` unprobed; `ttl_seconds` has `gt=0.0`, no floor, `types.py:1827`) | Yes | Retention degrades exactly as fast as safety improves. **DEAD** |
| **record-keyed** (fork-floated) — `now − first_observed_at > k·TTL` | **Yes** — inherits `t_first_obs ≥ t_pub` | **No** — it consults the record | Not a third form: **collapses into C-2 with a larger grace constant**. **DEAD as a C-1 variant** |
| **hybrid** (C10's own) — ceiling fires only when the record is ABSENT | No | Nominally yes | The mechanism **cannot distinguish "never observed" from "record lost"** — that indistinguishability **IS** the ratified fail-safe direction. In every case where it fires it has reduced to the plain mtime ceiling and inherits its full unsafety. **DEAD** |

### §4.2b The generalization — **restated after review; C10's original premise was false as stated** `[HIGH]`

C10 originally generalized: *"the only other age signal the store owns is `mtime`."* **The adversarial pass falsified that premise (§11 F2-01) and it is corrected here rather than quietly kept.** The store owns at least two further age signals:

- **Inode `ctime`** — a **fourth variant** neither C10 nor the fork enumerated. Empirically probed by the reviewer: after `os.utime(path, (t−5000, t−5000))`, `mtime_age = 5000.0` while `ctime_age ≈ 0` — **userspace cannot push `ctime` backward**, and `os.link` sets it to link time. A `ctime`-keyed ceiling is therefore record-loss-robust **and** immune to the entire `B-77` crash-window Δ. **This is a strict improvement over the mtime-keyed variant and the strongest C-1 form found on this arc.**
- **`_StoredEnvelope.written_at`** (`protected_result_store.py:296`) — a second stored age signal, named in the fork's own §2 table.

**Both die, and the corrected generalization is narrower and true:**

> **Every ceiling that is robust under record loss must key on a signal the store can read without the record. The only such signals are the entry's own filesystem timestamps and its embedded `written_at`. `written_at` predates publication by construction (it is stamped pre-serialization/encryption) and was rejected for exactly that reason at `B-68`. The filesystem timestamps — `mtime` and `ctime` alike — are stored at the volume's granularity `G`, so any ceiling keyed on either inherits `Δ ≤ G` on a coarse volume and lands back on the unprobed-`G` TTL floor of §3.1. Therefore no record-loss-robust ceiling avoids the twice-declined floor.**

**Confidence, honestly split:** the `ctime` probe is `[HIGH]` (directly measured). The claim that `ctime` inherits coarse-volume flooring is `[MODERATE]` — asserted structurally (it shares the inode timestamp storage `mtime` uses, and `B-74`'s framing at `forward-register.yaml:1745`–`:1746` is about *what a coarse filesystem stores*, not about when the value is taken), **not** measured; no coarse volume was available. **This is the single weakest load-bearing link in the record and it is flagged as such**, with a spec-leg consequence at §7.2.

**What the correction does to the verdict: nothing.** The fourth variant is strictly better than the first and dies for the same reason. But **C10's original wording foreclosed a search it had not exhausted**, and a foreclosure claim that survives only because a fourth candidate happens to fail is not the claim that was made. Corrected rather than defended.

### §4.3 C10 corrects C3's §3.4 as INCOMPLETE-as-presented, then reframes it `[HIGH]`

The arithmetic is re-derived and confirmed. **But read alone it overstates the equivalence:** C-1's `2·TTL + I` holds under **total** record loss, whereas C-2 under a **repeating** loss loop has no TTL-side bound at all. §3.4 and §3.5(b)(3) must be read **together**; §3.4 in isolation is the typical case and omits the tail that is C-1's entire reason to exist.

**Then the blast-radius reframe C3 could not make:**

1. **A bound with an unbounded term is not a bound.** C-1 offers `k·TTL + I` where `I` is unbounded in the one-shot shape. *The retention guarantee the retention side is being asked to buy — at the price of a live paid-effect payload — does not exist as a guarantee in the field.*
2. **The store is encrypted at rest under a locally-held DEK** (`:4904`; `protected_result_store.py:300`–`:308`, encrypt at `:446`). **Stated precisely, after an out-of-family correction (§11 C-5):** encryption changes the **access prerequisite**, not the post-compromise blast radius. *Conditional on DEK compromise*, exposed volume scales roughly **linearly** with residency — doubling retention roughly doubles the resident records available. What the bullet establishes is only that **the unconditional exposure is gated on a separate event** (whether the locally-held DEK is compromised at all), which is where the dominant probability mass sits. `[MODERATE]` on the quantification; `[HIGH]` on the direction. **The original wording — *"changes the blast radius by essentially nothing"* — overstated this and contradicted C3's own §5.4 caveat; it is withdrawn.**

> **Net, on the corrected wording: the retention-hours axis is a real but second-order term for C10's concern, and it is not what carries the verdict.** The verdict is carried by §4.5's tier asymmetry, which is independent of residency entirely.

### §4.4 C10 DEFENDS the round-6 withdrawal — and shows it does not carry C-1 `[HIGH]`

The withdrawal is factually correct and properly made against interest; C10 does not soften it. It fails to carry C-1 for one reason, stated as a rule:

> **A premise-count argument favours the option with fewer premises only if that option's bound is real.** Per §4.3, C-1's is not — its own bound carries the same unbounded-`I` cadence premise. **Fewer premises on a guarantee that does not hold is not an improvement.**

On C3's "derived index" typing: C10 **applied C3's own falsification criterion and reports it HOLDS** — under C-2's conjunction, record absence makes the second conjunct false ⇒ no reclaim ⇒ strictly longer retention. **The typing survives.** But C10 **refuses the inference** C3 drew from it (§5.1).

On the non-dot-leading name: **concurred, with a coupling caveat** — a non-dot-leading name is *more visible* to operator globs and naive copies, so visibility is acceptable **only** under the contents restriction, which makes that restriction load-bearing rather than descriptive. And it removes **one of three** channels; selective backup and operator cleanup remain. *The withdrawal is narrowed, not retired, and the answer to the remainder is observability, not denial.*

### §4.5 The blast-radius classification — C10's own taxonomy makes the two failures non-comparable `[HIGH]`

| Failure | Tier | Default gate |
|---|---|---|
| C-1's ceiling destroying a live entry — irreversible loss of the last recoverable copy of a **completed paid effect** (the report log holds only a redacted digest) | **`write-bounded-irreversible`** | `gate-on-every-call` with HITL |
| C-2's lengthened residency of ciphertext under a locally-held DEK | footprint growth on an encrypted store; nearest classification `read-only`-adjacent | `open` |

*(Vocabulary verified against `c10-action-safety-blast-radius/SKILL.md:141`, `:159` by the adversarial pass — not fabricated.)*

> **C-1 does not merely regress liveness — it introduces an UNGATED `write-bounded-irreversible` action into the store**, which under C10's own taxonomy would owe a gate the fork never priced. C10 is **not** asking for that gate (§4.7); it is pricing the option honestly. **C-2 introduces no gated action at all.**

### §4.6 The typed-expiry report line becomes FALSE under C-1 `[HIGH]`

`:4909` requires *"TTL expiry surfaces as a TYPED report-log line."* Under C-1 the ceiling firing on a live entry emits a line **named "TTL expiry" for an entry that has not expired** — an audit-trail emission that **misreports the event class**. Under C10's audit-integrity discipline, *a trail that records a destructive action under the wrong class is worse than no record*: it is the shape that defeats post-hoc forensics.

**C7 reinforced this from its own domain (§4A):** because the harness has **no OTel log bridge and no metrics pipeline** (P11), the report log is the **only** forensic artifact this store produces — so a misreported destructive action is not one failure among several, it is *a false entry in the sole record*.

### §4.7 Stated AGAINST interest — arguments C10's brief invited that do NOT survive grounding

- **Tenant-deletion / erasure obligations — the keyword probe is clean but the CLAIM was over-scoped, and is narrowed here** `[HIGH]`. A grep for `erasure|GDPR|right to be forgotten` across `design-substrate/` returns four files and **every hit is unrelated** (`ADR-F4:27`/`:72` and `Target_Stack_Commitment_v1:43` are *"capability erasure"* / *"feature-erasure"*; `Spec_Harness_Runtime_v1:3988` is *"the LCD-union feature-erasure move"*). **That much is reproducible and was independently re-run (§11 F2-04.)** But C10's conclusion — *"there is no committed data-erasure obligation anywhere in the corpus"* — generalized past what three keywords can support. **A wider probe finds the corpus's actual retention vocabulary**, which C10 never touched: `Spec_Operational_Discipline_v1_25.md` carries *"retention controls under attestation-bound retention policy"* among the Persona §10.4 compliance-readiness **foundational, not bolt-on** primitives, plus `§C-OD-27.2 row 3 (retention policy default 7 days)` at `:62`, and `PRD_v1_2.md:234` defers the retention-policy *syntax* (i.e. the obligation exists; its syntax is what is open). **The claim is narrowed to the three keywords actually searched.** Disposition of the wider anchor at §7.2 — it is the strongest un-argued case for C-1 on this record, and it is tier-conditional (`multi-tenant-compliance`) and not live at HEAD.
- **Backup / replica propagation:** no committed backup or replication contract exists for this store to propagate into. Not an argument C10 can make.
- **`PersonaTier` gradient: does NOT reach this store today.** `persona_tier` (`types.py:2059`, default `SOLO_DEVELOPER`) drives the sampler base-rate and the redaction-processor override toggle (`Spec_Harness_Runtime_v1.md:965`); `protected_result_store_ttl_seconds` (`types.py:1827`) is **tier-independent**. Whether it *should* be tier-gated is a **Class-3 observation, explicitly NOT owed by this leg** (proposing it here would be X-AL-3).
- **Key-compromise window:** real, second-order, and on the corrected wording it argues C10's own side **down** (§4.3(2)).
- **Reachability, stated symmetrically:** on **committed** surfaces the reachable Δ is the crash-window Δ (sub-ms to a few ms), so C-1 at k=2 bites only at `ttl_seconds` below a few ms — supported (`gt=0.0`) but ~7 orders below the 86400s default. **Neither C-1's regression nor C-2's retention cost is a default-path exposure.** The decision is therefore made on **contract conformance and blast-radius classification, not incident likelihood** — the fork's own §6.1 framing, affirmed rather than inflated.

---

## §4A C7 — Observability (CONSULTANT, Layer-D add). **Type: propose-refinement.** Concurs with C-2; **finds a real defect in the emission predicate C3 and C10 authored without it.**

First cite, pre-bound: `Spec_Harness_Runtime_v1.md` **v1.109** §14.8.11 `:4909` — *"TTL expiry surfaces as a **TYPED report-log line**."* C7's opening move is that this clause is not only C3's prohibition: **it is the section's carrier declaration**, and the council's three added conditions had been reasoning as though the carrier were open.

### §4A.1 The (C-b) predicate was DEFECTIVE — and the defect originated in the condition's NAME `[HIGH]`

The out-of-family finding (§11 C-2) is upheld, and C7 traces it one step further back than the reviewer did. C10 bound the condition as *"record **loss** must be observable"* — an obligation **whose title is a diagnosis**. C3 then built the predicate the title asked for, and the predicate inherited the verdict. **Naming an emission is schema design**; the §1 handoff (*"C10 declares emission; schema is C7's"*) was correct in form, but the declaration had already fixed the schema's semantics.

**Option (i) — a durable initialization/migration marker — is DEAD, on a ground neither the reviewer nor either voice stated** `[HIGH]`: the marker would live in the store root, alongside the record, so **every** loss channel round 6 names (selective backup/restore, dotfile-skipping copy, operator cleanup) takes **the marker and the record together**. *A discriminator that fate-shares with the artifact it discriminates yields zero discrimination in the loss case.* Placing it outside the root is a second carrier, foreclosed by the ratified `(C-i)`. The `B-97`(a) cutover-marker precedent does **not** transfer — that migration's problem is *keying*, not *co-resident durability*.

**C7 takes option (ii): emit the FACT, not the verdict** `[HIGH]`. This is not a concession to operator burden — *it is C10's own §4.6 rule applied consistently*: an emission must not name an event under a class the emitter cannot support. An emission asserting *"record LOST"* on a first-cutover sweep is the same defect one level over. **The council's own principle refutes the council's own predicate.** C7's discipline names the boundary **fact-not-verdict**: a single emission is a runtime fact; *"a repeating loss loop is occurring"* is a claim over a **population** of emissions, and baking a population-claim into one emission is a schema-level leak (the C7↔C8 cut, C7's to enforce).

**Is (ii) adequate for C3's §3.5(b)(3) purpose — converting *"a repeating loss loop is implausible"* from assumption to measurement? YES, but only with a field neither voice attached to it** `[HIGH]`. A bare *"a fresh grace is starting"* line is **not** sufficient: in the one-shot shape every run emits one, and one-per-run is indistinguishable from steady state. What makes repetition diagnostic is **co-emitting condition #8's oldest-resident-entry age**:

- benign cutover → resets **once**; the oldest-entry age thereafter stops growing past the condition-#7 bound;
- repeating loss → resets **again and again**, and because the entries survive while only the record dies, the oldest-entry age is **strictly growing** at each reset.

> **(C-b) and (C-c) are therefore not two conditions — the #8 gauge is the field that makes the #6 emission diagnostic without asserting a diagnosis.** Fusing them costs zero extra state.

Two limits stated against C7's own recommendation: `[MODERATE]` the cross-reset comparison works because **the report log survives process exit** — precisely the property the in-process registry (`:111`) lacks, which is not a coincidence but the same asymmetry C3 §3.4 exploits. `[SPECULATIVE]` the growing-age signal fails if the same loop that drops the record **also** drops the entries; **(ii) makes the loss-preserving loop measurable and leaves the loss-everything loop unmeasured** — strictly better than today and strictly less than complete.

### §4A.2 Invalid records — the `os.replace` assertion is **correctly premised and over-concluded** `[HIGH]`

The fork's §4 reads: *"This makes **corrupt** unreachable (a torn write leaves only an orphan temp), leaving **absent** as the sole loss state"* (`class_2_fork…:283`).

- The **parenthetical is correctly scoped**: `os.replace` does make a torn write **from this store's own publication path** unreachable. That claim survives.
- The **conclusion does not.** Disk-level corruption, truncation by a restore, a manual edit, and a record written in an incompatible form by a different build each leave a file that **exists** and cannot be trusted. The file-absence predicate fires on none of them, the timestamps are unrecoverable, and the grace must restart — silently, today.

**Fail-safe direction, stated as a TOTALITY rather than a case list:** any outcome other than *a record was read, parsed whole, and its entries are usable* reads as **no observation, for every name** — and **never a partial trust** of the rows that happen to parse, *because a corrupted row that parses can carry a `first_observed_at` earlier than the truth, which SHORTENS retention — the one direction condition #4 forbids.*

**And this emission may be classified as a fault where #6's may not** — no benign cause produces it: the store's own publication is atomic, so it never writes a record in that shape, and there is no cutover case to confuse it with. That asymmetry is why it is a separate condition (#11), not a clause of #6.

### §4A.3 The emission surface — carrier, namespace, cardinality, redaction `[HIGH]`

- **Namespace: none of C-OD-05 §5.1's fifteen fits, and none is needed.** The roster (heading at the OD baseline body `:377`, rows `:381`–`:395`; recorded UNCHANGED at `Spec_Operational_Discipline_v1_36.md:103`, `:122`) is `anthropic.*`, `mcp.*`, `skill.*`, `managed_agents.*`, `sandbox.*`, `hitl.*`, `topology.*`, `subagent.*`, `engine.*`, `audit.*`, `validator.fail.*`, `files.*`, `memory.*`, `harness.breaker.*`, `provider_discriminator`. The nearest candidate `audit.*` is the **CP-owned audit-ledger** namespace, and §5.2's *source-as-authoritative-declarer* invariant forbids this contract re-declaring attribute names inside it. **And the roster is not the universe** — C-OD-30 minted a `pause.*`/`resume.*` family that appears in none of the 15 rows; §5.1 is the **D6 cross-axis ingestion manifest**, not an exhaustive catalogue. C7 therefore **mints nothing and routes nothing**, because per the carrier finding no namespace is required at all.
- **Carrier: report-log lines** — the one §14.8.11 `:4909` already chose, and the one the shipped GC emissions already use (`logger.warning` at `:839`, `:855`; `logger.error` at `:830`, `:849`). **Not metrics** — P11 found no metrics pipeline, so #8 must say *reported value*, never *instrument*. **Not spans** — two of the three triggers (bootstrap `stage_4_od.py:123`, shutdown `shutdown.py:800`) run outside any workflow trace, so a span would be a parentless root emitted once per process, buying neither nesting nor propagation.
- **Content: condition #5's restriction binds the EMISSIONS more tightly than it binds the record** `[HIGH]`. The record sits in the store root under deployment permissions; the report log goes wherever logging is configured — routinely a shared aggregator, a different retention policy, a wider reader set. **A content restriction that binds the at-rest artifact but not the emission describing it leaks the field it was written to protect.** The entry FILENAME (one-way sha256) is emittable; the COMPOSITE KEY never is, in whole or in part. *(The shipped lines already honour this — they emit `digest = entry_path.stem` at `:820`.)* One place the log is legitimately looser, **preserved deliberately**: the shipped expiry line emits `tenant=%s` (`:840`) from the decrypted envelope, inside the ratified surface — **not retracted** — but the new #6/#11 emissions describe the *record*, run without any decrypt, and **MUST NOT acquire a tenant tag by decrypting entries to get one**.
- **Cardinality, stated carrier-independently:** an entry digest MAY appear in an emission's **body** but **MUST NOT be used as a dimension or label of any aggregate** — digests are per-`uuid4` and unbounded by construction. `[SPECULATIVE]` on whether a metrics leg ever materializes to make this bite; the term is written so a later aggregate cannot inherit the hazard.
- **Redaction: `persona_tier` does NOT reach this carrier, and that is a finding** `[HIGH]`. Per C-RT-03's field row (`Spec_Harness_Runtime_v1.md:965`), `persona_tier` drives exactly two OD materializers — `HarnessCompositeSampler`'s base rate and `RedactionSpanProcessor`'s per-persona override toggle — **both span-pipeline surfaces**, and P11 found **no OTel log bridge**. *Distinct from C10 §4.7's Class-3 TTL observation: this is a live property of the carrier THIS leg selects.* **Consequence: condition #5 is the ONLY content control these emissions have** — load-bearing a *second* time, for a *different* reason than the non-dot-leading name.

### §4A.4 Condition #8 — C3's narrowing is **right, and it left a hole** `[HIGH]`

**The concession first, unhedged:** C3's prohibition on caching the oldest-resident-entry age is **correct and must stand verbatim**, for exactly C3's reason — a cached value is a second authority and goes stale in precisely the crash window `B-77` names.

**The hole is not the narrowing but what it left unaccompanied.** Condition #8 as merged specified a sweep-time computation and **no surface at which the value can be read when no sweep is running**. P4/P6 establish all three triggers are event-driven; C3's own §3.5(a) names the pathology (a daemon that goes quiet never sweeps again).

> **The oldest-entry age is therefore emitted least often exactly as it grows largest. A quantity produced only by the mechanism whose absence *is* the fault cannot falsify that fault.** (C-c) as merged did not deliver what C10 bound it to deliver.

**The fix must not reach for either forbidden exit** — not a periodic timer (the separately-routed cadence gap), not caching (C3's prohibition stands). C7 specifies a **pull surface on the existing `harness-inspect` admin CLI**, on the **§13.7 precedent in this same spec, one arc old** (`Spec_Harness_Runtime_v1.md:1288`–`:1302`). The fit is structural, not analogical: §13.7 was minted for *"a durable class of orphaned journals that no code path in the product can reach or list"* with *"irreversible sha256 digests"* filenames (`:1292`) — the same shape as a store root of `sha256(...).entry` files only a sweep ever enumerates. It is recorded as *"an extension of the existing `harness-inspect` row, not a new subcommand"* (`:1290`); its term 5 (`:1302`) supplies the engagement predicate (root absent → output byte-unchanged); its term 3-bis (`:1299`) supplies the obligation to state what the surface **cannot** tell. **X-AL-3 clean: no new namespace, no new span family, no new subcommand.**

**Does instrumenting `I` belong in this leg? NO — and the boundary is precise rather than deferred** `[HIGH]`. Instrumenting `I` requires either durable last-sweep state (which reopens condition #5's closed content set) or periodic sweeps (the routed cadence gap). **Both exits leave this leg.** But this leg is not thereby silent: **the pull surface substitutes for `I` on the question (C-c) actually asked** — an operator who can read the oldest-entry age on demand can falsify *"the store is bounded"* **without knowing `I` at all**. That is a resolution of C3's §3.5(a) finding, not a punt on it.

### §4A.5 Where C7 says each voice crossed or under-served its domain

| Voice / section | C7's finding |
|---|---|
| **C10 §4.8 (C-b)** | **Under-specified, and the under-specification is the defect's origin** — binding an obligation *named* as a verdict fixed the schema's semantics before schema was handed over. The right binding is *"a grace **reset** must be observable"*. `[HIGH]` |
| **C3 §5.3 (C-b) sub-clause** | **Overstepped, and that is where the defect entered.** C3 was right that the naive per-name predicate misfires; its substitute — *"thereafter absence is unambiguously loss"* — is an **observability claim about what an emitter may infer**, made by the persistence voice, **and it is false**: it relocates the ambiguity to the cutover sweep rather than removing it. `[HIGH]` |
| **C3 §5.3 (C-c) narrowing** | **Correct in C3's own domain, but it silently decided a question in C7's** — by leaving sweep-time as the *only* surface it settled the surface question by omission. `[HIGH]` |
| **C10 §4.6** | **Did not overstep** — audit-integrity is C10's. C7 extends it: the same rule applied to (C-b) is what forces option (ii). **C10 supplied the principle that refutes C10's own predicate.** `[HIGH]` |
| **§1 CCR row 2** | The handoff was correct in form and failed in substance, because the conditions handed over were already **named** in schema terms and **no one checked what carrier §14.8.11 had already chosen**. `[MODERATE]` |

---

## §5 Cross-read debate — the genuine intra-council disagreements and their resolution

The consultants did **not** collapse into the primary. C10 refused an inference of C3's and corrected C3's presentation; C7 then found a defect in a condition C3 and C10 had jointly authored, and told both where they had overstepped.

### §5.1 DISAGREEMENT 1 — *"the record may be discarded freely"* → **C3 WITHDRAWS**

- **C3 (original):** the record is a derived index, therefore *"the record may be discarded freely; discarding it costs reclaim latency and nothing else"* — and therefore **no backup invariant is owed**, contra the fork's §6 point-4 concession.
- **C10:** the typing survives, but the index is **WEAK** — it cannot be reconstructed *with its original value*; a rebuild **restarts the clock**. So its loss is a latency event whose latency is **unbounded under repetition**, and *silent, unbounded lengthening of the residency of sensitive material is indistinguishable in effect from a retention failure, however it is typed.* **The invariant owed is not "back it up" — it is "make its loss OBSERVABLE."**
- **C3 confirm-back — WITHDRAWN** `[HIGH]`: *"I over-reached by exactly one inferential step: from not-an-authority to not-worth-observing. Those do not follow from one another."* The gloss is struck; condition #4 carries unchanged without it; (C-b) replaces it.

> **C3 further records that the withdrawal *improves* its own position:** its compounding argument (§3.5(b)(3)) asserted the implausibility of a fault **with no means of detecting it** — *"the same shape of claim I criticised C-1 for making about Δ."* (C-b) converts that assumption into a measurement. **C3: "I should have carried it myself."**

### §5.2 CORRECTION — §3.4 read alone overstates the equivalence → **C3 ACCEPTS**

Accepted without reservation, and consolidated by C3 into the honest form:

> **C-1 buys a tail bound; the tail it bounds is, at HEAD, undetectable — which is why (C-b) is the cheaper purchase of the same assurance.** With (C-b) adopted, the repeating-loss loop becomes an **observable operational fault** rather than silent unbounded residency, and C-1's remaining advantage narrows to *"handles the fault without an operator"* vs *"reports the fault to an operator."* §14.8.11's uniform posture — refuse typed, report typed, never silently degrade (`:4903`, `:4905`, `:4906`, `:4909`) — settles that against C-1.

### §5.3 C3 adopts all three C10 conditions, with one strengthening, one sub-clause, one narrowing

- **(C-a) ADOPTED — and C3 strengthened it with a cite neither voice had used** `[HIGH]`: `_StoredEnvelope` carries `composite_key: str` (`protected_result_store.py:298`) and the envelope is pickled and **encrypted** before publication (`:446`). **The design already treats the composite key as material requiring encryption at rest.** A cleartext sidecar carrying it would create *a second, cleartext copy of a field the store deliberately encrypts* — a direct contradiction of `:4904`. C3 also notes C10's condition catches a failure C3's own weaker wording did **not**: an impl leg could sincerely read `{composite_key, first_observed_at}` as satisfying *"digests and timestamps"*, since the composite key *contains a uuid4 that reads as a digest*.
- **(C-b) ADOPTED — requires NO state the store does not already have** (a derived predicate over the verified past-TTL name set at `:788`/`:795` and the record just read at `:797`). **C3 added a sub-clause** keying on the record FILE's absence rather than per-name gaps. **That sub-clause's second half — *"thereafter absence is unambiguously loss"* — was subsequently FALSIFIED by out-of-family review and by C7 (§4A.1) and is REMOVED**; the file-vs-per-name half survives and is carried into condition #6.
- **(C-c) ADOPTED with one narrowing** `[HIGH]`: the "why a reclaim fired" discriminator **is** computable without a second authority — `max(m + TTL, first_observed_at + TTL)`, derived not stored. **C3 declines to bind "oldest resident entry's age" as a STORED quantity** — computed at sweep time from the existing `stat()` pass (`:753`, `:784`), never cached. *(Upheld verbatim by C7, which then added the pull surface the narrowing left missing — §4A.4.)*

### §5.4 The two DEK / report-line findings — both confirmed by C3

- **DEK (`:4904`):** confirmed by direct read; **moves C3's cost accounting, not its content condition.** C3 had priced C-1's purchase as one `I`; the DEK fact says the confidentiality *value* of that `I` is smaller than the arithmetic alone showed. **C3 explicitly declines to push further than C10 did:** *this does not make residency irrelevant — disk exhaustion and post-compromise blast radius both scale with it.* **That caveat is what out-of-family review later used to correct C10's own over-statement (§4.3(2)); C3 was right and C10's wording, not C3's, was the error.**
- **False report line:** **COMPOSES, does not duplicate.** Same sentence, two failures — C3's is the **prohibition** half, C10's the **emission** half. *"C10's is the stronger for a corpus where the ledger is the recovery substrate: an unlicensed action leaves a true record of a wrong act; a misreported one leaves a false record, and only the second is unrecoverable by later audit."* Adopted as an independent ground, credited to C10, and reinforced by C7 (§4.6).

### §5.5 DISAGREEMENT 2 — C7 vs the joint C3+C10 emission predicate → **both authors' clause REMOVED**

Recorded as a genuine disagreement rather than folded silently: the (C-b) predicate as jointly authored by C10 (naming) and C3 (sub-clause) was **defective**, was found so first by an out-of-family reviewer with no transcript and then independently traced to its origin by C7, and **neither original author's formulation survives** into condition #6. See §4A.1. Resolved by replacement in the same round; not a standing tension.

---

## §6 TENSION block

**TENSION-1 — SURFACED → RESOLVED (consultant conceded the tension's own premise).**

| Field | Value |
|---|---|
| **Parties** | C3 (State, Memory & Persistence) ⊥ C10 (Action Safety & Blast Radius) |
| **Issue** | Whether the elapsed-time grace should carry an absolute mtime-keyed reclaim ceiling (C-1) or stand alone (C-2). |
| **C3's position** | An age authority that cannot predate publication is the whole point; a ceiling that can fire early re-opens the class the arc exists to close — and *is*, in identity, `B-74`'s twice-declined TTL floor, unenforced. |
| **C10's position (the fork's framing, which C10 was convened to hold and did not adopt)** | A retention bound carrying one fewer premise is worth paying for where the payload is sensitive. |
| **Stakes** | Whether `B-96` / the `B-77` residual / `B-74` **close** or stay **open-and-narrowed**; whether `test_…:1975`'s live-entry-survives assertion is preserved or inverted; what §14.8.11 must carry. |
| **Status** | **`resolved-by-concession` — resolved WITHIN the convening, by the consultant defeating its own side's argument on two independent counts it owns.** (i) *The bound C-1 offers is not a bound* — its `k·TTL + I` carries the same unbounded-`I` cadence premise (P6). (ii) *The payload it protects is ciphertext under a locally-held DEK* (`:4904`), so the unconditional exposure is gated on a separate event. **C-1 was withdrawn from the retention side, not conceded to C3's argument.** — **Vocabulary note:** `output-templates.md`'s Status enum is `[open \| escalated to Layer 2 \| promoted to Layer 3]`, plus the standing amendment's `surfaced + probe-resolved`. **Neither fits**: no Layer-2 arbiter pass occurred, and §2 explicitly disclaims probe-resolution. `resolved-by-concession` is a **new value** naming a case the template does not cover; flagged here rather than borrowing the Layer-2 word, and routed at §7.2 as a template amendment the orchestrator skill may want. |
| **Layer-3 check** | Does **not** engage T-perm-1 (C4↔C10), T-perm-2 (C2↔C3) or T-perm-3 (C1↔C9). C3 explicitly recorded that no C2 compaction surface is engaged. Not a permanent tension. |

**TENSION-2 — SURFACED → RESOLVED BY REPLACEMENT (same round).** C7 ⊥ {C3, C10} on the (C-b) emission predicate (§5.5). Both original formulations removed; condition #6 replaced. Recorded for completeness; not standing.

---

## §7 VERDICT — **C-2** (grace term alone, no absolute ceiling), carrier `(C-i)`

**Unanimous across three voices, reached from non-overlapping grounds.** C3: age-authority integrity + the implicit-floor identity + the witness-inversion discriminator. C10: under-gating / fail-open in a fail-closed section + false audit emission + the non-existence of the bound C-1 sells. C7: concurrence, plus the finding that the report log is the store's **sole** forensic artifact, which sharpens C10's misreported-event-class argument.

**Each voice conceded something against interest.** C3 withdrew *"discard freely"* and accepted the §3.4 incompleteness. C10 declined three arguments its own brief invited, could not break C3's impossibility claim when it tried on its own side's behalf, and later had its `:4904` wording and its `mtime`-only enumeration corrected under review. C7 stated two limits against its own recommended option.

**No forced third form.** A third was actively hunted: C10 constructed and killed the **record-keyed** and **hybrid absent-record** ceilings; the adversarial pass constructed a **fourth**, `ctime`-keyed variant that C10 had missed — the strongest C-1 form found on this arc — and it dies for the same reason (§4.2b). **Manufacturing one would violate the fork's soundness exit; none was manufactured, and the one that was found is recorded as tested-and-dead rather than suppressed.**

### §7.1 The conditions the spec leg must carry — jointly held, **no CONTESTED items**

Twelve conditions for `Spec_Harness_Runtime_v1.md` §14.8.11 under C-2. Module/API names, the record's file name and serialization format, and concrete emission field keys / message shapes stay in the deferred-to-discretion list at `:4911`, which already names the expiry report-line format.

| # | Condition | Provenance |
|---|---|---|
| **1** | **Conjunctive reclaim rule, no third path.** Reclaim requires BOTH (a) mtime-derived age past TTL AND (b) elapsed time past TTL since a **durably recorded first observation**. State explicitly that **there is no other reclaim path** — a spec stating only the grace leaves C-1 re-derivable at the impl leg. | C3; C10, C7 concur |
| **2** | **Publication bound, stated normatively.** Reclaim never precedes `publication + TTL`. This is what makes the grace a contract term rather than a heuristic, and what closes `B-74` without a resolution floor. | C3 |
| **3** | **Sampling point.** `first_observed_at` is sampled at the **locked, post-re-verification observation point** (`:797`, inside the lock opened at `:781`) — **never** at `gc_sweep`'s pre-enumeration `current_time` (`:714`). The recorded time must not precede the entry's observed existence. | fork §3(ii)(c); load-bearing under C-2 in a way it would not be under C-1, since under C-2 the lemma **is** the reclaim rule |
| **4** | **Derived index, not authority.** Record absence reads as *no observation* and can only **lengthen** retention, never shorten it. *(The "may be discarded freely" gloss is WITHDRAWN and must not appear.)* | C3, as amended by C10 |
| **5** | **CLOSED content set — `{entry filename, first_observed_at}`, keyed on the entry FILENAME** (already a one-way sha256, `:379`–`:381`). The `result_ref` / composite key MUST NOT appear in whole or in part; no tenant tag, no plaintext, no ciphertext. **State the reason in the spec:** the composite key is simultaneously the retrieval capability and a cleartext tenant discriminator (`:598`), **and is already carried encrypted inside `_StoredEnvelope`** (`:298`, encrypted at `:446`) — a cleartext copy would contradict `:4904`. **Per condition #12 this restriction binds every emission derived from the record, more tightly than it binds the record itself.** Closed-set, not illustrative. | C10 (highest-value finding), strengthened by C3, extended to emissions by C7 |
| **6** | **A grace RESET is emitted as an OBSERVED FACT, never as a diagnosis.** When a sweep finds the root holds past-TTL entries **and** no observation record was read, emit a report-log line stating the observed state and nothing beyond it: that **no observation record was read**, the **count** of past-TTL entries, and the **oldest resident entry's age** (condition #8's sweep-time value, same `stat()` pass) — and therefore that a **fresh grace begins**. **The line MUST NOT assert, name or classify the record as LOST.** State normatively why: at the first sweep of a store predating the record, the observable state is **IDENTICAL** to genuine loss and **no state the store may hold distinguishes them** — a durable initialization marker would live in the same root and be removed by the same cleanup, **fate-sharing with the artifact it would discriminate**. **A repeating loss loop is made visible by REPETITION together with the oldest-entry age** (benign cutover resets once and its oldest age stops growing; repeated loss resets repeatedly with a **strictly growing** oldest age), and the report log persists across process boundaries where no in-process state does. **Emission is unconditional and per-occurrence** — no in-process suppression, since in the one-shot shape there is no second occurrence within one process to wait for. The record is written at every sweep that runs, **including when the observed set is empty** (condition #9 semantics); **the spec MUST NOT state or imply that this makes a later absence unambiguously loss.** Requires no state the store does not already have. | **C7** (replacing the defective C10-named / C3-sub-claused predicate) |
| **7** | **Retention statement — CONDITIONAL, with the condition observable.** (a) typical worst case `2 × TTL` plus **up to TWO** sweep-trigger intervals (one to the first post-TTL observation, one more to the post-grace reclaim); (b) the trigger interval is **unbounded in the one-shot process shape** and is **pre-existing at HEAD**, not introduced by this grace; (c) the bound is **conditional on the record's presence and readability**, and that condition is emitted per #6 and #11. **No unconditional "bounded by N × TTL" claim is available under either form.** | C10's correction, absorbed by C3; interval count corrected under out-of-family review (§11 C-3) |
| **8** | **"Bounded" must be FALSIFIABLE IN THE FIELD — at TWO surfaces.** The quantity is the **oldest resident entry's age**, **computed at sweep time from the existing `stat()` pass (`:753`, `:784`), NEVER cached between sweeps** (a cached value is a second authority and goes stale in precisely the `B-77` crash window). Surfaced at **both**: **(a)** as a **field of** every sweep's report-log emission (the reclaim line and the #6/#11 reset lines), never a separate line; **(b)** an **operator-facing READ-ONLY enumeration on the existing `harness-inspect` admin CLI requiring no sweep**, on the §13.7 precedent (`:1288`–`:1302`) — an **extension of the existing row, not a new subcommand**; engaging only when the store root exists, output byte-unchanged otherwise; the same `stat()`-derived age at read time; and **stating in its own output what it cannot tell** (snapshot at read time; entries present does not imply a sweep will run). **(b) is owed by THIS leg**: all three triggers are event-driven, so under (a) alone the age is emitted least often exactly as it grows largest, and a quantity produced only by the mechanism whose absence *is* the fault cannot falsify that fault. **This does NOT resolve `I`**, which stays in its own register row — the pull surface is what makes #7 falsifiable **without** `I`. **Plus** the **which-reclaim-term-fired-last** discriminator (`max(m + TTL, first_observed_at + TTL)`, derived at the reclaim site, never stored) as an **attribute of the reclaim emission**, not a standalone one. | C10 binds it; C3 narrows the caching; **C7 adds the pull surface and the attribute placement** |
| **9** | **Record lifecycle.** Names no longer present are dropped (**replace-not-accumulate**, the existing `:879` semantics), so the record is bounded by the entry set. A retention mechanism that grows its own unbounded metadata reproduces the failure it fixes one level up. | C3 |
| **10** | **Reading B retired explicitly**, so no future impl leg builds the row's `close_out` verbatim and ships an unbounded-retention regression in the one-shot shape. **Owed under every answer.** | fork §8; all three voices |
| **11** | **An UNREADABLE or INVALID record reads as NO OBSERVATION, TOTALLY — and is emitted as a FAULT, which #6 is not.** The reachable loss states are **absent** AND **unreadable**. `os.replace` makes a torn write **from this store's own publication path** unreachable; it does **not** make an unreadable record unreachable — disk corruption, truncation by a restore, a manual edit, or a record written in an incompatible form by another build each leave a file that **exists** and cannot be trusted. **The spec MUST NOT carry the conclusion that absence is the sole loss state.** **Fail-safe as a TOTALITY:** any outcome other than *read, parsed whole, entries usable* reads as **no observation for every name** — **never partial trust** of rows that happen to parse, because a corrupted row that parses can carry a `first_observed_at` **earlier than the truth** and thereby **shorten** retention, the one direction #4 forbids. Emission uses #12's carrier and content rules, discriminated as **record present but unreadable**; **unlike #6 it MAY be classified as a fault**, since no benign cause produces it. | **C7** |
| **12** | **The emission surface — carrier, content, cardinality, redaction.** Every emission this section owes rides the **TYPED REPORT-LOG LINE** §14.8.11 already names (`:4909`), the carrier the shipped sweep emissions use. **NOT spans** (two of three triggers run outside any workflow trace; a span would be a parentless root buying neither nesting nor propagation). **NOT metrics** (no metrics pipeline exists, so #8's "age" denotes a **reported value**, never an instrument). **No new namespace is minted and the C-OD-05 §5.1 roster is UNCHANGED** — none of its fifteen rows is the home for a Runtime-owned store's GC, and the nearest candidate `audit.*` is the CP-owned audit-ledger namespace whose attributes §5.2's source-as-authoritative-declarer invariant forbids this contract re-declaring. **Content:** #5's closed set binds the record **and every emission derived from it** — the entry FILENAME MAY appear; the composite key **MUST NOT**, in any emission, because the report log is routinely readable under a wider audience and a different retention policy than the store root. The #6/#11 emissions derive from the `stat()` pass and the record read **ALONE** — they **MUST NOT decrypt an entry** and therefore carry no tenant identity. *(The existing TTL-expiry line's decrypted tenant tag is inside the ratified surface and is NOT retracted.)* **Cardinality:** an entry digest MAY appear in an emission body but **MUST NOT be a dimension or label of any aggregate** — digests are per-`uuid4`, unbounded by construction. **Redaction:** `persona_tier`'s gradient is a **span-processor** surface and there is **no OTel log bridge**, so it does **NOT** reach this carrier and MUST NOT be relied on — **condition #5 is consequently the ONLY content control these emissions have.** | **C7** |

**§14.8.11 must NOT acquire:** a `ttl_seconds` floor (declined twice on the `B-74` arc); any numeric `k`; a **hard periodic-sweep requirement** — `:4909`'s *"periodic-or-opportunistic"* already licenses the shipped shape, verified by direct read, **no amendment owed there**; a new OTel namespace or span family.

**Carrier refinement — routed to the IMPL leg, not the spec leg.** The sidecar's name must be disjoint from both sweep globs (`*.entry`, `.tmp-*`) **and SHOULD NOT be dot-leading** — a non-dot name closes the dotfile-skipping loss channel round 6 named. **This is a `(C-i)` carrier sub-option refinement, which the fork's §10.1 soundness exit assigns to the impl leg** (*"A finding that a carrier sub-option (C-i/C-ii/C-iii) has a defect is an impl-leg finding"*), so it is recorded here as an impl-leg acceptance condition and deliberately **not** promoted to a `design-substrate/**` term. *(Condition #5 — the content restriction — is a different object: it governs sensitive material and its emissions, which §14.8.11 owns, so it is spec-leg. The split is deliberate; see §7.2.)*

### §7.2 Scope of this convening's output relative to the §8 ratified ask — **stated as an expansion, not presented as settled**

The convening's scope was *"the single question 'C-1 or C-2'"*. It returns **twelve** binding spec-leg conditions, **five of which (#5, #6, #8, #11, #12) did not exist in the fork's §8 ask.** Flagged explicitly rather than folded in, per the adversarial pass's F2-05:

- **Conditions #1–#4, #7, #9, #10 ride the ratified answer directly** — they are what selecting C-2 *means* as a contract, and the fork's §9 spec-leg row already owes them.
- **Conditions #5, #6, #8, #11, #12 are EXPANSIONS.** Their claim to ride the ratification is that they are **conditions of the selected form** — C-2's bound rests on the record's presence and readability (fork §4's own two-premise framing), so a spec that states C-2 without stating what happens when that premise fails states an incomplete contract. **The operator's visibility on them is the spec leg's clearance marker (`CLAUDE.md` §4.5), not this record.** If the operator judges that they owe a fresh decision rather than riding the Reading-C ratification, that is a **Class 2** routing (in-execution operator decision), and this record surfaces it rather than assuming the answer.
- **Condition #5's routing was itself contested and is split.** The soundness exit assigns carrier sub-option defects to the impl leg. The **file-name/dot-leading** half is therefore impl-leg (above). The **content-restriction** half is spec-leg, because C7 showed it binds the *emissions* (§4A.3) — and emissions of sensitive material are §14.8.11's own subject, not the carrier's.

**One anchor the record does NOT dispose of, flagged for the spec leg.** §4.7's narrowing surfaced the corpus's actual retention vocabulary — *"retention controls under attestation-bound retention policy"* among Persona §10.4's compliance-readiness **foundational** primitives, and `§C-OD-27.2 row 3 (retention policy default 7 days)`. **That is the strongest un-argued case for C-1 on this record**: an attestation-bound retention policy wants an unconditional bound, which is exactly what C-2 lacks and C-1 nominally offers. Blunting factors, stated: the primitives are gated to the **`multi-tenant-compliance`** tier; the OD spec structurally excludes the multi-tenant-compliance × local-development cell; and the anchor is **not live at HEAD** (`persona_tier` defaults to `SOLO_DEVELOPER` and does not reach this store at all). **Disposition: the spec leg MUST state condition #7's conditional bound explicitly enough that a future tier-binding arc can see what it would need to strengthen** — and it is recorded here as a known, tier-conditional counter-anchor rather than left for rediscovery. It does **not** reopen the verdict: C-1's ceiling would not deliver an unconditional bound either (P6).

### §7.3 One template gap surfaced, routed not absorbed

`output-templates.md`'s TENSION `Status` enum has **no value for a tension resolved inside the convening by a party conceding its own premise** — the case here. `resolved-by-concession` is used at §6 and flagged as a **proposed template amendment** for `council-orchestrator/references/output-templates.md`. **Not applied by this arc** (that file is `.claude/` workspace-operational, a different posture); routed as a follow-on.

---

## §8 `B-74`-residue implication — its filing is DEFERRED pending this answer

**Under the C-2 verdict, `B-74` CLOSES — and closes in the shape its own `close_out` asks for.** `[HIGH]` All three voices reached this independently; the adversarial pass re-derived it against the live test.

- `B-74`'s two stated options (`forward-register.yaml:1731`–`:1732`) are *"reject TTLs below a guaranteed timestamp resolution"* (declined twice — once by Codex, once by advisor) or *"use an age authority that cannot predate publication by more than the TTL."* **C-2 delivers the second structurally** — no volume probe, no floor, no knowledge of `G` required — because the age authority stops being mtime-alone.
- The residual as currently scoped — *"a rounding error EXCEEDING the gap between two consecutive sweeps"* — is **DISSOLVED, not narrowed**: the inter-sweep gap ceases to be a term in the reclaim decision at all.
- The advisor cross-reference carried in that row (*"ground as a single does-the-age-authority-stay-mtime question before building either in isolation"*) is **answered**, and answered by C-2 and by nothing else on the table.
- **Witness disposition:** `:1982` flips `== [entry_path.stem]` → `== []` and is **re-pinned as a positive witness** that the live entry survives both sweeps — exactly what its own comment at `:1978`–`:1981` instructs. `:1975` and `:1976` are **untouched**.

**Had C-1 been selected, `B-74` would have stayed OPEN and its "narrowing" would have been one-directional.** Scope tightens on the Δ axis (`> the inter-sweep gap` → `> (k−1)·TTL`) but **widens on two others**: (i) it becomes a **first-observation** loss needing one sweep rather than two — a strictly larger reachable set; (ii) the bounding quantity changes from the inter-sweep gap, which a deployment can *lengthen* to buy safety, to `(k−1)·TTL`, which cannot be raised without raising retention one-for-one. And `:1975` would become **nondeterministic** (P8-a), voiding that test's recorded mutation probe.

**Two corrections the `B-74` filing must carry forward, both surfaced here:**

1. **The Δ figure.** Neither the fork's *"Δ ≈ 1.0s"* nor this record's first correction *"Δ ∈ [0.3, 0.9) guaranteed"* is right. Per P8, Δ is the fractional part of wall-clock **at the patched `os.utime` call**, phase-guarded only at loop exit; `[0.3, 0.9)` is *overwhelmingly likely*, not guaranteed. **The impl leg must not inherit either number as a fact.**
2. **The stale anchor's HOME.** `:4883` — the stale line anchor for §14.8.11's bounded-retention bullet — lives in the **`B-74` row at `forward-register.yaml:1755`**, NOT in the `B-96` row. The `B-96` row (`:2902`) carries only the bare label `Runtime v1.108 SS14.8.11` with **no line anchor at all**. *(This record's own first draft repeated the fork's mis-attribution while claiming to be catching it — corrected under review, §11 F2-02.)* **Both refreshes are owed, to two different rows.**

---

## §9 Sequencing — what this record changes, and what it does not

**Chain (unchanged from the fork's §9, now with the sub-decision filled in):** filing (#1179) → **operator ratification of Reading C (done, 2026-08-01)** → **this convening (this PR — resolves C-1/C-2 to C-2)** → **spec leg** → **impl leg**.

| Leg | Owed |
|---|---|
| **This PR** | This record only. **Doc-only.** No `design-substrate/**` edit, no register mutation, no `roadmap_status.md` refresh — deliberately out of scope. |
| **Ratification-leg bookkeeping** (a later PR, not this one) | `B-96` row (`:2860`): `close_out` amended to retire Reading B and record **C-2 selected**; `status: design_substrate_gated`; `pr:` pointer; the bare **`v1.108`** label at `:2902` refreshed to **v1.109**. **`B-74` row (`:1711`):** the stale **`:4883` at v1.108** anchor at `:1755` refreshed to **`:4909` at v1.109**, and the row cross-referenced to this record and to the `B-96` impl leg. The *"no persisted sidecar"* reversal recorded on `B-77`'s row (`:1879`) so it is not later read as unratified drift. |
| **Spec leg** | A Runtime §14.8.11 amendment carrying **the twelve conditions at §7.1**, with **§7.2's expansion flag** surfaced in the clearance marker per `CLAUDE.md` §4.5. **Spec + impl do NOT land together**, per the `B-33`/`B-39`/`B-59`/`B-69`/`B-70`/`B-72`/`B-97`/`B-107` precedent *(list carried from the fork's §9; not individually re-verified here)*. **CXA disposition — determined, not assumed:** the adversarial pass ran the cross-spec probe and found CP v1.103 §1 row 6, CP v1.103 §14/§18, CP v1.112 §55 and Runtime plans v2.51/v2.56 all cross-reference §14.8.11 as the **Runtime-owned definition site**, *"never restated here"* — so **no sibling text is stranded and no CXA delta is owed**; the spec leg records that determination rather than omitting it. |
| **Impl leg** | Per the fork's §9 impl row, **plus** conditions #5/#6/#8/#11/#12, **plus** the **non-dot-leading sidecar name** (impl-leg per §7.1's routing split). `B-96`, the `B-77` residual and `B-74` all flip to `closed` **only when this leg merges**. |

**Explicitly NOT owed by any leg, restated so it is not re-derived:** narrowing `ttl_seconds` or adding a TTL floor; any fourth reordering of `_publish_atomic`'s two-stamp pipeline; carriers `(C-ii)` / `(C-iii)`.

**Three items carried forward as out-of-scope, agreed, none a tension:**

1. **The write-driven-cadence gap** (P4 + §3.5(a)): `_maybe_opportunistic_gc_sweep` fires only from `write_once`, so a daemon that suffers one signing failure and then goes quiet never sweeps again until shutdown — exactly the scenario §14.8.11's *"a long-lived daemon that never restarts must still bound the store"* purpose clause names. **Pre-existing at HEAD; orthogonal to C-1/C-2** (symmetric in direction, though C-2 carries `2I` to C-1's `I` — §3.5(a) as corrected). Per the fork's soundness exit this does **not** reopen the filing. **Recommended as a NEW register row**; a bounded `I` is the higher-leverage move for anyone who actually wants a retention bound. Condition #8's pull surface substitutes for it on the falsifiability question but does not close it.
2. **`PersonaTier` tier-gating of `protected_result_store_ttl_seconds`** (C10 §4.7): tier-independent today. A Class-3 observation **explicitly not owed by this leg** — proposing it here would be X-AL-3. **Related but distinct** from C7's finding that `persona_tier` does not reach the emission carrier either (§4A.3), which *is* in scope and is condition #12.
3. **The `output-templates.md` TENSION-Status gap** (§7.3) — a `.claude/` workspace-operational follow-on, different posture, not applied here.

---

## §11 Review record — reconcile-to-zero

Three decorrelated passes ran against this record before it was committed, wired per `CLAUDE.md` §13.1 and the council workflow's E2/E3 stages. **The Codex pass got no council conclusions and no adversarial findings — it read only the artifact.** Where they converged, confidence rises; **five of the fifteen absorbed findings came from Codex alone, which is the decorrelated catch the in-family reviewers structurally miss.**

### §11.1 Out-of-family — `just codex-review-uncommitted` (gpt-5.6-sol), round 1: 2 [P1] + 4 [P2], **all six upheld in substance**

| # | Finding | Disposition |
|---|---|---|
| **C-1** [P1] | *"Honor the required C7 council override … replacing C7 with C10 leaves the required observability owner absent while this record adds binding observability conditions."* | **UPHELD in substance; its stated ground is half-right.** Codex has **no transcript** by design, so it could not see that the orchestrator's brief **explicitly authorized** the Layer-C re-check — Layer A is an *operator* override, and the operator's instruction here was to re-score. **But the substantive half is correct and was the round's most valuable finding: the record legislated C7's domain without C7.** Answered by **actually convening C7** as a Layer-D add (§0.1, §4A), which found a real defect neither convened voice had caught. **The authorization is now recorded at §0.1**, which the first draft omitted. |
| **C-2** [P1] | *"Distinguish initialization from record loss"* — on the first post-cutover sweep of an existing store, entries-present/record-absent is **identical** to genuine loss; emit-before-create false-alarms every upgrade, create-before-check hides genuine deletion. | **UPHELD.** C3's *"thereafter absence is unambiguously loss"* sub-clause is **false** — it relocates the ambiguity rather than removing it. Routed to C7, which traced it to the condition's *name* and answered with **fact-not-verdict** emission, and additionally killed the reviewer's own suggested fix (a durable init marker **fate-shares** with the record). **Condition #6 fully replaced.** |
| **C-3** [P2] | *"Include both sweep intervals in the retention bound"* — condition #7 said `2×TTL + I` while §3.4/§4.3 say `2×TTL + 2I`. | **UPHELD** — a genuine internal inconsistency. **Condition #7 corrected to "up to TWO sweep-trigger intervals."** |
| **C-4** [P2] | *"Treat invalid sidecars as observable loss"* — the file-absence predicate misses truncated / malformed / unreadable / incompatibly-restored records. | **UPHELD.** `os.replace` prevents torn *publication*, not corruption. Routed to C7 → **NEW condition #11**, with a totality fail-safe (no partial trust of rows that parse) that goes beyond what the reviewer asked. |
| **C-5** [P2] | *"Reprice DEK compromise by retained data volume"* — encryption changes the access prerequisite, not the post-compromise blast radius; §5.4 already concedes residency scaling, making C10's claim internally inconsistent. | **UPHELD.** C10's *"changes the blast radius by essentially nothing"* **overstated** and contradicted C3's own §5.4 caveat. **§4.3(2) rewritten** to the conditional claim; the verdict rests on §4.5's tier asymmetry, which is residency-independent. |
| **C-6** [P2] | *"Stop claiming the phase guard guarantees delta"* — the guard checks phase before `write_once`, but encryption/locking/writes/fsyncs precede the patched `os.utime`. | **UPHELD, and it corrects THIS RECORD's own correction of the fork.** P8 rewritten; the honest statement is *overwhelmingly likely, not guaranteed*. **P8-a added:** under C-1 the witness becomes **nondeterministic** rather than deterministically inverted — which strengthens the finding, since a flaky live-entry-survival assertion is worse. **Carried into §8 so the impl leg inherits neither wrong number.** |

### §11.2 In-family adversarial (`harness-adversarial-reviewer`, pre-merge gate posture): **Class 3: 0 · Class 2: 5 · Class 1: 7.** Disposition *"cleared with current-phase revision; the C-2 verdict is NOT disturbed."*

| # | Finding | Disposition |
|---|---|---|
| **F2-01** | **§4.2's impossibility premise is factually false** — *"the only other age signal the store owns is `mtime`"* ignores inode **`ctime`** (probed: userspace cannot push it backward; `os.link` sets it to link time) and **`_StoredEnvelope.written_at`** (`:296`). A `ctime`-keyed ceiling is record-loss-robust **and** immune to the whole `B-77` crash-window Δ. | **UPHELD — the most valuable finding of the three passes.** The verdict survives (`ctime` shares inode timestamp storage, so it inherits `Δ ≤ G` and lands back on the unprobed-`G` floor; `written_at` was rejected at `B-68` for predating publication) — **but a foreclosure claim that survives only because a fourth untested candidate happens to fail is not the claim that was made.** **§4.2b added**, restating the generalization narrowly and truly, recording the `ctime` variant as **tested-and-dead** rather than unenumerated, and **flagging the coarse-`ctime` step as `[MODERATE]`, structural-not-measured — the record's single weakest load-bearing link.** |
| **F2-02** | **The claimed stale-carry catch is mis-scoped.** `:4883` appears **once** in `forward-register.yaml`, at **`:1755` — inside the `B-74` row**, not `B-96`. The `B-96` row carries a bare `v1.108` label with no anchor. The record repeated the fork's mis-attribution *while claiming to catch it*. | **UPHELD.** §9's bookkeeping row **split across both rows**; §8 carries the correction so the `B-74` filing inherits it. |
| **F2-03** | **The substitution's consequence is undisclosed: no convened voice held C-1.** C10 owns both sides; once framed in C10's vocabulary the outcome is near-determined, so the surfaced tension was **intra-C10**. The register's C7/C8 assignment was **role-based**, and §0.1 rebutted only the keyword reading. | **UPHELD.** **§0.2 added**, stating the limit plainly and naming the three substitutes for an advocate (C10's own construction attempt; the reviewer's fourth variant; the fork's six out-of-family rounds). The reviewer separately verified this is **not** primary-collapse — C10 anchors on `:4904`, which appears **nowhere** in the fork; it refused a C3 inference and declined three arguments its brief invited. |
| **F2-04** | **§4.7's corpus-wide erasure claim is grounded on an under-scoped grep.** The grep is reproducible; the generalization is not. The corpus's actual retention vocabulary — *"retention controls under attestation-bound retention policy"*, `§C-OD-27.2 row 3`, `PRD_v1_2.md:234` — is untouched, and **it argues FOR an unconditional ceiling.** | **UPHELD.** §4.7 **narrowed to the three keywords actually searched**, and the wider anchor **disposed of explicitly at §7.2** as *the strongest un-argued case for C-1 on this record* — tier-conditional (`multi-tenant-compliance`), structurally excluded from the local-development cell, not live at HEAD, and **not** delivered by C-1's ceiling either (P6). |
| **F2-05** | **Conditions #5/#6/#8 expand the §8 ratified ask without flagging the expansion; #5's promotion to a spec term contradicts the soundness exit** (*"a carrier sub-option defect is an impl-leg finding"*). Not X-AL-3 — scope expansion inside a legitimate back-flow channel, presented without the expansion being named. | **UPHELD.** **§7.2 added**, naming #5/#6/#8/#11/#12 as expansions, stating their claim to ride the ratification, and surfacing the **Class 2** routing if the operator disagrees. **Condition #5 SPLIT** — the file-name/dot-leading half **routed to the impl leg** per the exit; the content-restriction half stays spec-leg because C7 showed it binds the *emissions*, which §14.8.11 owns. |
| **F1-01** | Convening Block missing contract-required **`Routing rationale`** (one sentence per convened voice) and **`Pre-check status`**; nothing explained why C3 was primary. | **UPHELD; both fields added to §0.** |
| **F1-02** | CCR `handled-by-reference` rows carry no specific citation; two owner-status values outside the template vocabulary. | **UPHELD; §1 rows now carry SKILL.md-section citations and template-conformant owner status.** |
| **F1-03** | TENSION `Status` borrowed the Layer-2 word `Resolved`, which the template reserves for an operator-requested arbiter pass. | **UPHELD.** §6 now uses **`resolved-by-concession`** and **§7.3 routes the template gap** rather than absorbing it. |
| **F1-04** | *"Tightens BOTH forms identically"* contradicts the record's own arithmetic — direction symmetric, **magnitude not** (`2I` vs `I`). | **UPHELD; §3.5(a) and §9 item 1 corrected.** |
| **F1-05** | Variant-count attribution drift — the fork floats **two** ceiling variants; `hybrid` appears nowhere in it and is C10's own construction. | **UPHELD; §4.2's table now attributes each variant to its source.** |
| **F1-06** | P8's **upper** bound is a guard-exit property, not a stamp-time guarantee. | **UPHELD — converges with Codex C-6 from the opposite direction** (Codex found the fraction can fall near zero; the adversarial pass found it can exceed 0.9). Both folded into P8. **This convergence is the strongest signal in the review record.** |
| **F1-07** | §9's leg table omits the **CXA classification** every comparable arc records. | **UPHELD.** The reviewer ran the determination itself and found it **clean — no delta owed**; **§9 now states it** rather than omitting it. |

**Findings the adversarial pass raised and REJECTED after testing** (recorded because the attempts are the evidence): the §3.3/§3.4/§5.3 arithmetic re-derived step-by-step with **nothing to correct**; §3.2's no-`k`-delivers-both attacked with a large-`I` counterexample and **survived** on its antecedent; §3.3(b)'s witness-inversion re-derived **against the live test** and confirmed; P4/P5/P9/P10 and every §14.8.11 anchor (`:4903`–`:4911`) verified **byte-exact**; the grounding-HEAD empty-diff claim confirmed; C10's blast-radius tier vocabulary confirmed **not fabricated**; condition #7 confirmed to **sell no bound it does not have**; the cross-spec drift probe (mandatory per §10.9 amendment 3) found **no stale restated contract**; X-AL-3 **clean**.

**What the adversarial pass could NOT verify, stated rather than claimed:** coarse-filesystem flooring of `ctime` specifically (no coarse volume available — the `[MODERATE]` at §4.2b); the §0 *"genuine invocation"* claim (unverifiable from the artifact; content-consistency is the strongest available proxy); the eight-arc spec-then-impl precedent list at §9; and **external-canon mode was not run** — judged low-yield for an internal retention/GC tradeoff with no obvious industry counterpart in `.harness/01-planning/`. **That is the one attack family this review did not apply.**

### §11.2b Out-of-family round 2 — **3 findings OPEN, NOT YET FOLDED** <!-- WIP: resume here -->

**Status: this record is NOT reconciled-to-zero.** A second Codex round ran against the §11.1/§11.2-reconciled text and returned **2 [P1] + 1 [P2], all NEW (none re-raised)**. Work was halted by operator pause before they were absorbed. **The C-2 verdict is not in question in any of them** — all three attack conditions and the TENSION classification, not the answer.

| # | Finding | Status |
|---|---|---|
| **C2-1** [P1] | **Condition #5's closed set omits a live GC candidate class.** `gc_sweep` passes **both** `verified_entries` **and** `verified_tmp` names to `_observe_expired` (`protected_result_store.py:797`–`:800`), and `test_crash_orphaned_temp_file_survives_its_first_observed_sweep` (`test_lifecycle_protected_result_store.py:2068`) pins the `.tmp-*` grace. Condition #5 names only *"entry filename"* and grounds it on *"already a one-way sha256"* — **true of `.entry`, FALSE of `.tmp-*`**, whose names come from `tempfile.mkstemp(dir=root, prefix=".tmp-")` (`:543`). A conforming impl could not durably record temp-file observations, forcing it to either reclaim orphan temps on first sight or never reclaim them. | **VERIFIED BY THE ORCHESTRATOR, UPHELD, NOT YET FOLDED.** Fix owed: condition #5 must name **both** candidate classes, and scope the one-way-sha256 rationale to `.entry`; conditions #6/#9/#12 must be checked for the same under-coverage. Routed to C10 (the condition's author) — **not yet returned.** |
| **C2-2** [P1] | **The cross-run log-durability premise is false at HEAD.** C7's `[MODERATE]`-tagged §4A.1 step — *"the report log survives process exit"* — is what makes option (ii)'s reset-repetition diagnostic. **Whole-tree grep across `harness-runtime/src`, `harness-od/src`, `harness-cp/src`, `harness-core/src`, `harness-is/src`, `harness-as/src` for `basicConfig` / `dictConfig` / `addHandler` / `logging.config` / `StreamHandler` / `FileHandler` returns ZERO matches in production source.** With no handler configured, `logger.warning` falls through to Python's handler-of-last-resort → **stderr only**. In the one-shot shape nothing accumulates across runs, so the repeating-loss loop stays undetectable. | **VERIFIED BY THE ORCHESTRATOR, UPHELD, NOT YET FOLDED.** Does **not** touch carrier selection, #11, or #12's content terms — it touches exactly whether #6's fact-emission is *sufficient* for the purpose (C-b) was made binding to serve. Routed to C7 with three candidate answers, of which the most promising is that **#8(b)'s pull surface already answers it** (a strictly-growing oldest-entry age read on demand shows the loop **without** cross-run emission comparison) — **C7 not yet returned.** |
| **C2-3** [P2] | **§6's TENSION-1 records a position no convened voice held.** The record's own §0.2 states that **no convened voice argued C-1**, and the TENSION row itself labels C10's position *"the fork's framing, which C10 was convened to hold and did not adopt."* The orchestrator contract permits a TENSION block only when convened voices **actually** disagreed, with positions taken **from their turns**. Labelling this `C3 ⊥ C10` / `resolved-by-concession` therefore records a dispute that did not occur. | **UPHELD (orchestrator-owned; no voice input needed), NOT YET FOLDED.** Fix owed: **C-1/C-2 is the QUESTION, answered unanimously — not a tension.** Reclassify it as a tested-and-rejected alternative in §7 (three independent construction attempts: C10's two variants + its hybrid, the adversarial pass's `ctime` variant, the fork's six rounds). Promote the **genuine** convened-voice disagreements to the TENSION block: **§5.1** (C3 ⊥ C10 on *"discard freely"*, resolved by C3's withdrawal) and **§5.5** (C7 ⊥ {C3, C10} on the emission predicate, resolved by replacement). Also record as a finding in its own right that **the tension the fork PREDICTED (C3 ⊥ C7/C8) did not materialize** — that non-materialization is the honest headline, and §7.3's proposed `resolved-by-concession` template value should be re-examined once §6 is corrected, since it may no longer be needed. |

**Nothing else is owed to reach reconcile-to-zero on the current evidence** — but a round 3 has not run, so convergence is asserted for rounds 1–2 only, and not claimed overall.

### §11.3 Convergence and reconcile status

- **Codex ∩ adversarial converged on one finding from opposite directions** (P8's Δ bound — C-6 and F1-06). Per §13.1 that convergence is the strongest available signal, and P8 is now stated with both error directions named.
- **Codex alone caught** C-2 (init-vs-loss), C-3 (interval count), C-4 (invalid records), C-5 (DEK repricing) and the substance of C-1 (absent observability owner) — **five decorrelated catches, three of which produced new binding conditions (#6 replaced, #11, #12).**
- **The adversarial pass alone caught** F2-01 (the false impossibility premise + a fourth ceiling variant), F2-02 (mis-scoped stale-carry), F2-03 (the undisclosed convening limit), F2-04 (the under-scoped negative claim), F2-05 (unflagged scope expansion) and the six template/consistency drifts.
- **Reconciled to zero:** every finding from both passes is UPHELD and absorbed above. **Zero findings rejected on the merits; zero deferred.** The one item deliberately not closed is external-canon mode, recorded as un-run rather than claimed.
- **No finding disturbed the verdict.** The C-2 answer was attacked on its arithmetic, on its impossibility result, on its cite fidelity, on primary-collapse and on scope — and survived all five. **What the passes changed was the record's support and hand-off, which is exactly what a pre-merge gate is for.**
