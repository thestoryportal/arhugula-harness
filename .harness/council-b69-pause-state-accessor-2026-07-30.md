# Council record — B-69: the durable-pause-state read accessor

*Genuine multi-voice council per `.harness/council/council-workflow.harness-aware.yaml` + `COUNCIL-WORKFLOW.md`. Design-phase posture (workspace `CLAUDE.md` §11): `design-substrate/**` READ-ONLY at this arc — the spec-writer apply leg is a separate follow-on. Convened 2026-07-30. Deliverable = this record; no design-substrate edit, no code.*

| Field | Value |
|---|---|
| Question | **B-69 — what API shape should the Runtime spec author for the durable-pause-state read accessor, and how is the exposure tradeoff resolved?** |
| Register row | `.harness/forward-register.yaml` `B-69` (status `registered_finding`) + `.harness/post-phase-8-forward-register.md` §B-69 (lines 605-609) |
| Row's own council disposition | *"**TBD at build time** — narrow implementation-discretion follow-on in scope shape, but the read-accessor's own API design … is a real design choice worth a dyadic council pass if it turns out non-obvious."* — **discharged by this record** |
| Spec heads pre-bound at convening | Runtime `Spec_Harness_Runtime_v1.md` **v1.106** (cleared 2026-07-23); CP head **v1.111**, with the delta-chain caveat that the load-bearing scope-limit notes resolve byte-exact only at **v1.106** / **v1.107** |
| Outcome | **Converged.** One operator-tier question survives — a **scope** question, not the exposure tradeoff (§8) |

---

## §0 — Convening block

### 0.1 Nameable-tension gate (CLAUDE.md §10.9 amendment 1)

**PASS.** The tension was nameable in advance and is recorded verbatim on the register row itself (`post-phase-8-forward-register.md:609`): *"exposing partial durable state pre-resume vs. keeping `resume()` a single atomic call."*

Named spine, expanded to voice terms before convening:

> **Exposure / blast-radius (C10) ⊥ operator-loop ergonomics + crash-recovery reliability (C11 / C9).**
> A new caller-facing read of durably-persisted internal state widens the disclosure surface and is reachable without committing to a resume — **against** — the crash-recovery operator cannot compose a correctly-keyed `ResumeContext` at all without those identities, and a second API call carries its own read-then-resume reliability cost.

### 0.2 Layer identification + roster (the `layer_voice_map` router)

The question straddles **CP** (workflow lifecycle / HITL placement) and **OD** (HITL primitives), with a **Runtime-owned carrier** and an owed **CXA** classification. Applying the spec's `cross_cutting` rule (union the touched layers' primaries, cap the *primary* set by genuine domain center, promote a normally-consultant voice when the evidence is squarely its domain):

| Voice | Role | Layer-map provenance | Why |
|---|---|---|---|
| **C10** — action safety / blast radius | **Primary** | CP-consultant + OD-consultant, **promoted to first-class** | Owns one pole of the spine outright. The disclosure/payload question *is* C10's domain; a council that put C10 in a reacting seat would have inverted the tension. |
| **C11** — operator loop / local deployment | **Primary** | OD primary | Owns the other pole. The accessor exists for exactly one actor — a human at a terminal after a crash — and C11 owns that actor's contract. |
| **C9** — reliability / recovery | **Consultant (A2)** | CP primary | **The dyadic-default expansion, justified below.** |

**Dyadic default (amendment 2) — deliberately expanded to 3, with the justification stated rather than assumed.** The distinct third axis-specific concern is **read↔resume atomicity**: the accessor is by construction invoked *between* two other operations, `read_latest` has latest-record semantics, and §14.14.8 itself documents a `(workflow_id, run_id)` multi-run re-open trigger. Neither pole owns that — C10 owns *who may read*, C11 owns *what the operator needs*; **neither owns whether the two-call sequence is recovery-safe**. Layer-C scoring placed it above threshold on reachability (an already-documented re-open trigger) and on blast radius (a mis-keyed HITL response carries audit-attribution stakes per CP v1.106 §1.2 property 4).

*This expansion was load-bearing, not decorative: C9's A2 produced the single most consequential finding of the convening (§4, SEAM 2) and both primaries withdrew claims in response. A dyadic C10⊥C11 council would have converged cleanly on a design that is net-negative on the path it was built for.*

**Scored below threshold, recorded so the omission is a decision:** **C5** (validation-contract) — the projection DTO's closed-schema shape is genuinely C5's, but it is *subsumed* here: the payload boundary is decided by the C10⊥C11 tension, and C5 would have arrived as a consultant with no independent position. **C3** (state/memory/persistence) — invoked by name in-record (the store's shape and any tier/locking primitive are C3's) but not convened; both surviving store-level findings are routed OUT of this arc (§10), so C3 has nothing to decide here. **C7** (observability) — the trace-emission obligation is declared by C10/C9/C11; the *schema* is C7's and is named as owed, not authored here.

### 0.3 Cross-cutting concern register (slim CCR per amendment 3)

**Touched:**

| Concern | Owner | One-sentence pre-check |
|---|---|---|
| security / blast-radius | C10 | Engaged as a primary pole; resolved by probe + payload boundary (§2, §6). |
| hitl-local-first | C11 | Engaged as a primary pole; the accessor's only actor is the local recovery operator. |
| reliability / recovery | C9 | Engaged as the expansion consultant; produced the convening's decisive finding. |
| observability | C7 | **Not convened.** Emission obligation declared by three voices; schema named as owed (§9). |
| validation / contract | C5 | **Not convened.** Failure-taxonomy instrument routed *through* C5's existing taxonomy rather than extending it — no new fail class is proposed (§6.4). |

**Not touched (`n/a`):** cost (C6), eval-ability (C8 — one measurable surfaced in-record and handed forward, §10), orchestration-lifecycle (C1 — no iteration count, fan-out shape, or termination criterion at stake).

### 0.4 Stage record

| Stage | What ran | Gate |
|---|---|---|
| pre-convene | tension gate · layer/roster · spine · grounding packet | PASS |
| **E1·A1** | C10 + C11, **independent, blind to each other**, genuine agent invocations each adopting its own `cN/SKILL.md` | both returned positioned contributions with named contested claims |
| **probe** | 4 orchestrator probes at primary source **before** any TENSION block (amendment 5) | P1-P3 established; **P4 = a new finding that cut against the consultant's own carrier** |
| **E1·A2** | C9, introduced to react to the primaries' **real verbatim output** | surfaced tension, not concurrence |
| **E1·B** | cross-read DEBATE, seam-routed, all three engaging peers **by name** | **reconciled to internal zero** (§5) |
| **E2** | in-family `harness-adversarial-reviewer`, genuine invocation | 0 Class 3 · 7 Class 2 · 4 Class 1 — *"cleared with current-phase revision"* |
| **E3** | out-of-family `just codex-review-uncommitted` (GPT-5.6, $0 subscription) | 4 × [P1] + 1 × [P2], **near-zero overlap with E2** |
| **E2b+E3b** | **consolidated reconcile** (the spec's authorized reorder) — C9 + C10 re-invoked against the merged finding set | **reconciled to zero**; C9 conceded 4/4 in its domain |
| **E4** | bounded residual sweep, re-verified at HEAD | **CLEAR-TO-COMMIT**, 2 residuals carried in-record |

---

## §1 — Grounding (verified byte-exact at session-time, 2026-07-30)

Every cite below was resolved by direct `Read` during the convening; voices independently re-verified rather than trusting the briefing packet, and two of them caught orchestrator-supplied errors by doing so.

### 1.1 The verdict that made this a spec-leg question at all

| Cite | Content |
|---|---|
| `Spec_Harness_Runtime_v1.md` **:3274** (v1.106) | *"Lifting this requires a follow-on accessor exposing the durably-journaled pause state (§14.14.8) to `resume_handle` callers before `resume_context` construction — **registered, NOT designed or scoped by this delta**."* |
| `Spec_Control_Plane_v1_106.md` **:250** | *"Two round-3-registered follow-ons, **NEITHER resolved by this spec leg**"* — (a) is this accessor. |
| `Spec_Control_Plane_v1_107.md` **:36** | Round-5 correction: round 4's citation of B-69 was *"aspirational, not accurate"* — B-69's row then named only HITL child `run_id`s. Fixed by widening the row. **⇒ the accessor MUST expose BOTH identity kinds: paused-children `run_id`s AND effect-fence `idempotency_key`s.** |
| `Spec_Harness_Runtime_v1.md` **:680** (v1.46 change-note) | v1.46's own amendments are framed as *"both extending existing contracts (**no new operation**)"* — by contrast a caller-facing read **is** a new operation on the C-RT surface. |

### 1.2 What already exists

| Surface | Cite | Status |
|---|---|---|
| Durable store | `Spec_Harness_Runtime_v1.md` §14.14.8 (**:5634** ff.); `journal_workflow_pause_store.py:119` | `capture(snapshot)` + `read_latest(workflow_id) -> PauseSnapshot \| None`, fail-closed on absent/torn/corrupt/mismatch. Per-workflow file, **append-only, never truncated**, latest-record. |
| The read, today | `api.py:682` `_read_durable_pause_snapshot(config, workflow, resume_handle)` | **module-private**; called at `api.py:866` from *inside* `resume()`. |
| `resume()` | `api.py:715-722`; `Spec_Harness_Runtime_v1.md` :3252-3300 | `resume_context` is a **parameter of the same call** — the caller must already have built it. |
| CP tree-walks | `workflow_driver.py:2781` `_collect_gate_owning_run_ids`; `:2906` `_collect_effect_fence_idempotency_keys` | **private**; honor the gate-owning-vs-container distinction (CP v1.106 property 5) + B-72's never-keyable pre-dispatch identities (v1.108). |
| The existing CP→Runtime crossing | `mcp_server.py:266-278` | **THREE** sibling public CP computations already consumed cross-axis — each returning a **single scalar**. A **projection-returning** sibling (§6.6) is what is missing. |

### 1.3 The concrete payload surface

`PauseSnapshot` (`pause_resume_protocol_types.py:745`, frozen, `extra="forbid"`) carries `workflow_id`, `run_id`, `step_index`, `pause_reason`, `state_summary`, `snapshot_hash`, `created_at`, `state_ledger_anchor`, `hitl_gate_config_hash`, plus nested resume-state carriers. Reachable inside it: `StateSummary.summary_text: str` — **free text** (`handoff_context.py:182`); and `FanOutResumeState.orchestrator_output` (`pause_resume_protocol_types.py:321`) plus each `FanOutBranchResumeState.output` reached through `FanOutResumeState.branches` (`:333` is the container tuple; the payload field is on the branch carrier) — **model-generated payloads**.

**`state_summary`'s real provenance (corrected at the E2 pass).** `capture_pause_snapshot` sources it from exactly one place — `pause_resume_protocol.py:455`, `self._pause_context_reader()`. The MVP binding is the injected placeholder at `bootstrap/factories/pause_resume_protocol_factory.py:88-107` (`summary_text=""`, `summary_hash="0"*64`), whose own docstring marks it **explicitly deferred** and whose successor *"reads the current ledger head."* This matters twice below: at P4, and at §6.2's exclusion argument.

---

## §2 — Probe-first results (amendment 5: primary sources decide, councils surface)

Four probes were run at primary source **before** any TENSION block was emitted. P1-P3 confirmed voice claims; **P4 is an orchestrator finding no voice had surfaced, and it reversed the consultant's own proposed mechanism.**

### P0 — the authority-equivalence probe (run pre-convening; handed to both primaries as contestable)

`_read_durable_pause_snapshot(config, workflow, resume_handle)` takes **exactly** the three inputs `resume(workflow, resume_handle=..., config=...)` already requires. `resume()` already performs this read *and then executes the workflow*. **A read accessor with the same inputs grants a strict subset of the authority an already-shipped public surface grants to the identical caller. Reading is strictly weaker than resuming.** `[HIGH]`

**C10 accepted it and then strengthened it against its own interest** — verified at `api.py:1138`, `_build_run_result` carries `pause_snapshot=cp_result.pause_snapshot if status == "paused" else None`, and it serves `resume()` too. **So a `resume_handle` caller already receives the raw `PauseSnapshot` — every field — whenever the resumed run re-pauses.** *(Independently re-verified by the orchestrator.)* C10's conclusion, verbatim: *"**B-69 is not a disclosure question.** … The gap B-69 closes is **temporal, not authorizational**."*

### P1 — CP v1.106 property 4's sole-member carve-out. `[HIGH]`

`Spec_Control_Plane_v1_106.md` **:208**, verbatim in relevant part:

> *"let the 'unaddressed gate-owning set' be every gate-owning branch paused **this cycle** whose own `child_run_id` is NOT a key in `hitl_responses` … The uniform `hitl_response` fallback MAY resolve a gate-owning branch's `hitl_response_for(child_run_id)` call **ONLY when that branch is the SOLE member of the unaddressed gate-owning set this cycle**."*

Set membership is computed against the **live cycle**, never against the operator's keys. **C9's misattribution path is permitted by the letter of the invariant.**

### P2 — `resume()`'s own read-then-act is deliberately NOT racy. `[HIGH]`

`api.py:839-855`, verbatim in relevant part:

> *"Concurrency guard BEFORE the durable-store read (Codex-caught, this arc) … Correct because: (a) the store is only written while the lock is held …, and (b) the guard → store read → `async with _run_lock` segment below is **`await`-free**, so under asyncio's cooperative scheduling no other coroutine can acquire the lock (and thus write the store) between this check and our own acquisition."*

The guard sits at `:851`, structurally **before** `_read_durable_pause_snapshot` at `:866`. **⇒ C10's A1 pricing as "bounded and pre-existing" is wrong as applied.** C10 conceded on independent verification.

**SCOPED at the E2 pass (the first statement of P2 overreached).** `_run_lock` is a module-level **per-process** `asyncio.Lock` (`api.py:402`), and `_append` writes through a plain `path.open("a")` with no `O_EXCL`, lockfile, or advisory lock (`journal_workflow_pause_store.py:186`). The corrected conclusion, in C9's words:

> `resume()`'s read-then-act is non-racy **within one process** by construction. **Across processes it is unguarded**, so a cross-process read-then-act window exists today, pre-accessor. ⇒ The accessor does **not** introduce the first read-then-act window. It introduces the first window that is (a) **human-length** rather than scheduler- or call-length, and (b) **present in the single-process deployment** where the existing window is closed by construction.

**Vocabulary correction (C9, reconcile round — adopted throughout this record).** *"The record should drop 'TOCTOU' in favour of **'supersession window'**. TOCTOU implies a race; this harm needs no race, which is precisely why it is reachable at the tier with no concurrency."* The load-bearing framing is unaffected either way: *"the snapshot is re-derived; the response map is not"* makes no claim about processes, locks, or windows — **even under perfect cross-process serialization the operator's map would still have been composed against a snapshot a subsequent legitimate `capture()` superseded.**

### P3 — the nominated fence carrier does cover the paused-children set. `[HIGH]`

`pause_resume_protocol.py:726-772`: `_compute_snapshot_hash` covers `(workflow_id, run_id, step_index, state_summary)` plus each resume-state carrier **when present**, with `fan_out_resume.paused_child_branches` dropped-when-empty and *"include it (covering the nested child cursors recursively) only when a paused-child branch is actually present."*

### P4 — **NEW ORCHESTRATOR FINDING**: that same carrier is **fail-open** for the linear case. `[HIGH]`

*(Re-grounded at the E2 adversarial pass — the first statement of P4 cited the wrong construction sites. The conclusion survives; the justification is narrower and, importantly, **time-limited**.)*

For a pause with no fan-out carrier (LINEAR / single-step / the three sequential sites), `_compute_snapshot_hash`'s canonical dict is `(workflow_id, run_id, step_index, state_summary)` plus `hitl_gate_config_hash` when non-`None`. Four verified facts:

1. `run_id` is **reused** across resume — `Spec_Harness_Runtime_v1.md` **:3273**: *"The resumed run reuses `pause_snapshot.run_id` (audit/ledger coherence), NOT a fresh run identifier."*
2. `state_summary` comes solely from the injected `pause_context_reader` (§1.3), whose MVP binding is a **constant placeholder** — so it is invariant across successive pauses. **This is a property of a deliberately deferred placeholder, not a structural property of the hash.**
3. `created_at` is **not a parameter** of `_compute_snapshot_hash`.
4. `hitl_gate_config_hash` **is** a parameter (`pause_resume_protocol.py:738`) and **is** hashed when non-`None` (`:835-839`), and it **is** populated at the LINEAR / `EVALUATOR_OPTIMIZER` / `DECENTRALIZED_HANDOFF` sites — so the HITL-gated linear hash covers **five** elements, not four. It nonetheless **cannot discriminate a re-pause**: `_captured_hitl_gate_config_hash` (`workflow_driver.py:2741-2778`) derives purely from `(step, manifest_entry, default_model_binding)` via `fold_step_hitl_placements(...)` + `binding.removed_placements` — **deterministic in the workflow body, therefore identical across successive pauses of the same step.** It discriminates a config *edit*, never a *re-pause*.

**⇒ Two genuinely distinct successive pauses of the same linear workflow at the same `step_index` produce an IDENTICAL `snapshot_hash`.** A fence built on it would falsely **MATCH** — fail **open** — in exactly the shape most common at the `solo-developer` tier (C11: the ordinary request-changes / re-gate loop).

**The time-limited half is itself an argument (C10, reconcile round).** Because fact 2 rests on a placeholder scheduled for replacement, a `snapshot_hash` fence *"would fail now and appear to work later."* **That is the sharpest available defence of §6.3's property-not-composition ruling: the substrate is in flux, so naming a composition is guaranteed to age wrong.** P4's premise in its first form reproduced the stale docstring at `pause_resume_protocol_types.py:776-777`, which still describes a four-element hash — see §10.

**What P4 does NOT do (C9, reconcile round):** it does not establish the fence's necessity. *"The fence's necessity never derived from P4. It derives from SEAM 2 / W2 — composed-map supersession — which is indifferent to what the hash covers. P4 defeated only my nominated carrier."*

**C11 amplified it twice:** `hitl_gate_config_hash` does not rescue the case (its own docstring scopes it to the gate *configuration* of the step resumed into — **invariant across successive pauses of the same gate**; it discriminates a config *edit*, not a *re-pause*); and the collision is reachable through the ordinary **request-changes / re-gate loop**, i.e. the most common multi-turn HITL interaction at that tier.

**C9 verified P4 independently and conceded its own carrier**, recording the shape of the error: *"I verified my carrier against `paused_child_branches` — the shape my own finding used. I never ran it against the shape my finding is most reachable through."*

---

## §3 — Voice positions (E1·A1 + A2)

Full verbatim contributions were carried in the convening ledger; the load-bearing content is preserved below. Every voice was a **genuine dedicated agent invocation** that first read and adopted its own `cN/SKILL.md` — no orchestrator ventriloquism.

### C10 (primary) — action safety / blast radius

- **Exposure: resolved, and further than P0 claimed** (P0 strengthening above). *"Manufacturing a confidentiality objection here would be exactly FM-F (over-gating) and I decline to make one."*
- **Three residuals survive:** **R-1** open-ended schema coupling (*"not hypothetical: `PauseSnapshot` gained `hitl_gate_config_hash` this month"*); **R-2** an un-audited read; **R-3** the pause journal lacks the tenant-composite key + typed cross-tenant refusal that Runtime §14.8.11 (**:4636**, **:4639**) already commits for comparable durable state — **real, PRE-EXISTING, and explicitly to be kept OUT of B-69's scope** (B-73/B-80 split-out precedent).
- **The instinctive C10 answer is the trap.** *"An operator handed three opaque uuid `run_id`s cannot compose a correct `hitl_responses` map; they can only guess. **Under-informing the deciding human is itself an action-safety failure**, not a conservative default."*
- **Payload line:** a closed-set typed projection. `summary_text` excluded — and the exclusion is **free**, since it is `""` at every production pause path (P4 fact 2).
- **Shape:** standalone read function ADOPT; pre-flight mode **REJECT — "THE TRAP"**; `RunResult` field REJECT.
- **Named as owed, not assumed:** typed absent-vs-corrupt dispositions; a trace emission; **no gate, no HITL trigger**; a CXA row.

### C11 (primary) — operator loop / local deployment

- **Reframes the arc:** *"This is not 'multi-child addressing is unsupported.' **This is a durable approval queue with no enumeration read.** … A durable queue nobody can list has lost the property durability was bought for."*
- **Bare identities are unanswerable** — *"the operator has approved a UUID … **ritual approval** … a non-skippable gate the operator cannot understand is worse than no gate, because it launders an uninformed decision as an audited approval."* Insufficient on **audit-integrity** grounds, not ergonomic ones.
- **`pause_reason` is the field nobody had named and it is load-bearing** — since the 2026-07-24 widening the accessor returns a **heterogeneous** set, and `pause_reason` (**6**-class, incl. `EFFECT_FENCE_AMBIGUOUS`) is what tells the operator whether an entry belongs in `hitl_responses` or `effect_fence_resolutions`.
- **Declines the richest field, unprompted** — `summary_text` is *"agent-authored prose of unbounded provenance."* And **declines gate description empirically**: it *"is not in the durable snapshot at all"* — capture-side scope, owed to its own row.
- **Two register framings inverted:** the `durable=True` opt-in adds **zero** new config burden (anyone who can reach this problem already flipped it); and *"the atomicity concern and the accessor's audience do not overlap"* — atomicity is valuable to a programmatic caller, who already holds the snapshot and will never invoke this.

### C9 (consultant, A2) — reliability / recovery

Convened to adjudicate the atomicity question neither primary owned. Verdict:

> **The two-call sequence is recovery-safe for the IDENTITIES and recovery-unsafe for the CARDINALITY JUDGMENT.** Identities self-invalidate on a map miss. Cardinality claims fail **silently and in the harmful direction** — and case-disambiguation is, by C11's own argument, the accessor's *first* value.

- **The mechanism (P1):** stale read shows {A,B,C}; the live cycle's unaddressed gate-owning set is exactly {D}. D is the **SOLE** member → the uniform fallback **MAY resolve** → `hitl_response_for(D)` misses the map → **D receives the operator's uniform default, authored for branches the operator saw and D was not among them.** Cross-cycle misattribution, reached through a path property 4 *explicitly permits*.
- **Honest framing:** *"The accessor does not create this hazard. Today the operator supplying a uniform response is knowingly guessing. The accessor's contribution is to convert a **known guess into a believed fact**."*
- **The distinction that is the entire finding:** *"'`resume()` re-reads the journal, therefore the caller's read is untrusted' … proves the **snapshot** is re-derived. It does NOT prove the operator's **response map** was composed against the same snapshot. **Two different objects; only one is re-derived.**"*
- **Requirement:** a resume composed against a stale read MUST be **refusable by construction**, not safe by luck — refusal-only, compare-and-refuse, no value causing execution.
- **The append-only opportunity:** because the journal is never truncated, *"the substrate ALREADY retains everything a staleness fence, a read-side audit, or multi-run disambiguation would need. **No capture-side carrier change is owed**"* — so C11's capture-side pricing (correct for gate description) does **not** transfer to the reliability concerns.
- **Failure taxonomy, stronger rationale than C10's:** the `OSError` cause is **`transient`** in the fail-class taxonomy, and the four-causes-one-`None` collapse *"erases the classification the retry mechanism is defined to consume"* — a recovery-correctness defect, not an ergonomics one.

---

## §4 — TENSION block

Four seams were routed for the cross-read debate. **Outcome: all four resolved — three probe-resolved, one resolved by symmetric empirical defeat. Zero surfaced-unresolved.**

### SEAM 1 — C9 ⊥ C11 · `snapshot_hash`: display noise or correctness mechanism?

**The sharpest seam of the convening.** C11's A1 excluded it from the payload as operator noise; C9's A2 called that a category error — *"C11 evaluated it as **display** and excluded it; evaluated as **mechanism** it is the single cheapest correctness field available."* C9: *"I would rather have it on the record as a disagreement than smoothed."*

**Status: `surfaced + probe-resolved`, and resolved so that neither voice loses.** P4 showed the nominated carrier is fail-open. C10 named why that resolves rather than splits the seam: *"C11 was right that `snapshot_hash` is display noise, C9 right that a mechanism token is required — **they were evaluating different objects.**"* C11 reached the same place independently: *"**The field I excluded and the field C9 wants are not the same field**, and saying so is the honest resolution of this seam rather than a smoothing of it."*

**Resolution: an opaque accessor-minted staleness token. The spec states the required PROPERTY, never a composition.** C11 rejected `(snapshot_hash, created_at)` by holding C9 to C9's own standard — *"that is a **luck argument** about clock granularity and monotonicity, and C9's own requirement was 'refusable by construction, not safe by luck.'"* C9 accepted being held to it. C10 added the precedent argument: naming a composition *"would repeat the exact v1.106 §14.8.8.10 error — prescribing a composition against a substrate nobody re-verified. **P4 IS that error, caught one round earlier this time.**"*

### SEAM 2 — C9 ⊥ C11/C10 · is the two-call sequence recovery-safe?

**Status: `surfaced + probe-resolved` (P1, P2). The decisive seam of the convening.**

**C11 withdrew both of its fail-safe claims** — and sharpened C9's finding *against itself*:

> *"My §4.3 claim 3 reasoned from property 4's **2+-member** clause and never engaged the **1-member** clause at all. That is not an over-read by C9; it is an under-read by me."*
> **The 1→1 shape is worse than C9's 3→1.** The DTO shows the operator **one** paused location, A — *"exactly the case where supplying a bare uniform `hitl_response` is the ergonomically correct thing to do."* The live cycle's sole gate-owning member is D. D is the sole unaddressed member → the fallback resolves → the response lands on a branch the operator never saw. *"**It is reachable through the single-location happy path**, which is the most common HITL shape at solo-developer tier — and it is the exact case my §1 named as the accessor's first value."*

**C11 also resolved C9's own stated falsifier against itself.** C9 had put on the record that its finding shrinks if a live writer is unreachable in any deployment anyone runs. C11, owning that judgment, split it: concurrent *processes* on a shared `STATE_LEDGER` dir → **routed to R-3, not priced here**; but an interleaved second `capture()` → **reachable at C11's own tier**, because *"the second writer is not a rival process — **it is the harness itself, on an intervening resume**,"* under the supervised-daemon (`launchd KeepAlive` / `systemd Restart=on-failure`) arrangement that *"is not an exotic configuration — it is **THE** configuration a crash produces."*

**The discriminator that makes that split coherent (supplied by C9 at the reconcile round; the E2 pass correctly flagged it as missing, and without it SEAM 2's rescue reads as colliding with its own R-3 carve-out).** A supervised daemon plus a human at a terminal *is* two processes sharing the resolved `STATE_LEDGER` dir — so the split is not concurrency-vs-none, it is **two different failure modes that happen to involve the same two processes**:

| | Requires | Failure | Home |
|---|---|---|---|
| **Concurrent write-write** | two writers appending *simultaneously* | store-integrity: interleaved / torn records, no serialization primitive | **R-3** — correctly routed out (§10) |
| **Sequential interleaving** | only that *some* writer runs *in the interval* | **supersession**: two well-formed records, no corruption, the operator's map silently superseded | **SEAM 2** — priced here |

*"It is not writing at the same time; it is writing in between. One writer at a time, both records well-formed."* **The harm needs no concurrency at all** — which is exactly why it reaches the single-process tier.

**C11's position change, verbatim:** *"An accessor without a staleness fence is not 'incomplete,' it is **net-negative on the path it was built for**, and I no longer recommend shipping the read alone."*

### SEAM 3 — C10 ⊥ C11 · gate description: closed-vocabulary field or decline?

**Status: `surfaced + resolved by symmetric empirical defeat` — the cleanest outcome available.**

C11 declined gate description because no such field exists in the durable snapshot. C10 countered that an ergonomics claim should be answered with *another closed-vocabulary field* (floating the HITL placement enum), never a `str`. **Both voices then independently grepped and found the same fact:** every `placement` occurrence in `pause_resume_protocol_types.py` is docstring prose; `HITLPlacementKind` is a `StrEnum` at `hitl_placement.py:55` but **no durable pause carrier declares a field of that type.**

C11: *"The seam closes not because I win but because the same empirical fact defeats both proposals — which is a better outcome than either of us arguing preference."* C10: *"My closed-vocabulary counter-proposal was capture-side scope wearing the same costume I accused C11's prose of wearing."*

`hitl_gate_config_hash` was tested as a substitute and rejected by both on its surviving ground: it is a **material-diff identity, not a description** — an opaque sha256 whose only operator-meaningful semantic is "the gate config changed since capture." *(A second ground offered in-debate — that it is "absent in exactly the multi-child fan-out case" — is **STRUCK**: the E2 pass verified a per-branch analogue at `PreDispatchGateOwningBranchResumeState.hitl_gate_config_hash`, `pause_resume_protocol_types.py:265`. C10 at reconcile: *"My SEAM 3 concession rested on the `placement` grep, not on this — untouched."*)*

**Two exchanges landed inside this seam, in opposite directions.** C11 **accepted** C10's `step_kind` — with C10 adding the nuance that it is declared `str`, closed-vocabulary *by provenance* not by type, so the DTO should **declare** the domain rather than inherit `str` (*"the difference between a promise and an invariant"*). *(The E2 pass then found the acceptance over-broad — `step_kind` is declared at `:248` / `:712` / `:980` but **NOT** on `PausedChildBranchResumeState` (`:893-944`, exactly four fields), the carrier supplying B-69's primary addressing key. Resolved per-variant at §6.2 rather than blanket-included or routed out.)* And C11 **corrected** C10's `pause_reason` from 5-class to **6**-class, tracing the miscount to stale carry-text in the type's own docstrings. C10 accepted, and priced the correction as more than a digit: *"My A1 listed `pause_reason` under 'closed enums, zero free-text' — priced as **orientation**. C11 priced it correctly: `pause_reason` is the **map-routing discriminator**, and routing an entry into the wrong map is a misattribution of the same class property 4 exists to prevent. **`pause_reason` moves from cheap-include to required-for-safety.**"*

### SEAM 4 — all three · does the fence change the deliverable's scope?

**Status: `surfaced + adjudicated`.** Both primaries converged on "the read must not ship alone" but homed the fence differently — C11 bundle (one arc), C10 two spec surfaces / one arc gate.

**C9 adjudicated (it owns recovery sequencing) and ruled for C10's formulation on X-AL-3 grounds, not reliability preference:**

> *"The precondition amends the already-cleared `RT-FAIL-RESUME-*` pre-bootstrap battery. B-69's register row authorizes an **accessor**. Folding an amendment to a different cleared contract inside that row is the silent-extension the rule exists to forbid."*

**With one C9-native upgrade:** C10's *"B-69 MUST NOT be declared closed while the precondition is unshipped"* is prose, *"and prose sequencing constraints are precisely the ones dropped at a session handoff."* Restated in the shape this workspace already enforces — **X-AL-2's conjunctive form: B-69 closes iff (accessor landed) ∧ (precondition landed ∧ exercised by W3). Partial is non-closure.** Checkable at the register rather than remembered. Plus C11's ordering point, which the criterion alone does not cover: the criterion prevents *closure*, not *landing* — **same arc, same merge**; otherwise *"land the regression and register the fix,"* which is the shape this workspace's discipline exists to prevent.

---

## §5 — Reconciliation to zero (concession ledger)

Reconciled-to-internal-zero at the E1·B gate. Recorded as a ledger rather than a claim, because *who conceded what* is the evidence that the council was genuine and not a primary-collapse.

| # | Position | Held by | Outcome |
|---|---|---|---|
| 1 | "TOCTOU is bounded and pre-existing" | C10 (A1) | **WITHDRAWN** on P2. *"I priced a **scheduler-length** window that has been closed, when the accessor opens a **human-length** one that has never existed."* *(SHARPENED, not re-withdrawn, at the reconcile — ledger row 15: "has never existed" is too strong **cross-process**; the scheduler-length-vs-human-length class distinction survives verbatim.)* |
| 2 | Residual belongs at the `(workflow_id, run_id)` re-open trigger | C10 (A1) | **WITHDRAWN.** `run_id` is reused across resume (:3273), so that keying would not close the window. **Staleness ≠ multi-run disambiguation.** |
| 3 | "Any new `resume()` parameter is the trap" | C10 (A1) | **WITHDRAWN.** *"My asymmetry does NOT reach it … a spec leg reading my §3 as 'no new `resume()` parameter, full stop' would be reading me wrongly, and I want that correction on the record explicitly."* **The MODE rejection stands, unreversed** (C9 flagged the row-label-vs-body risk and asked it be stated so it does not ship as a stale-carry). |
| 4 | Typed absent-vs-corrupt via a new disposition enum | C10 (A1) | **INSTRUMENT REPLACED.** *"My §4(d) argument does turn on me."* Requirement C10's; instrument + rationale C9's. |
| 5 | Closed-vocabulary gate field (HITL placement enum) | C10 (A1) | **WITHDRAWN** on its own grep — capture-side scope, symmetrically with C11's prose. |
| 6 | `pause_reason` is 5-class, priced as orientation | C10 (A1) | **CORRECTED to 6-class and re-priced as required-for-safety.** *"C11 got there first."* |
| 7 | §4.3 claim 3 — "a stale read yields a wrong key, not a mis-delivery" | C11 (A1) | **WITHDRAWN.** *"That is not an over-read by C9; it is an under-read by me."* And **sharpened against itself** to the 1→1 shape. |
| 8 | §4.3 claim 1 — "the writer is dead" | C11 (A1) | **WITHDRAWN** — not on the multi-process case (declined and routed to R-3) but on the supervised-daemon auto-resume shape at C11's own tier. |
| 9 | `snapshot_hash` excluded from the payload as display noise | C11 (A1) | **REASONING CONCEDED, CONCLUSION UPHELD on new grounds.** *"My exclusion criterion … is a **legibility** test, and it is the wrong test for a token the operator never reads"* — but P4 vindicates the exclusion of *that field*. |
| 10 | `snapshot_hash` as the staleness-fence carrier | C9 (A2) | **WITHDRAWN** on independent verification of P4. *"I asserted 'refusable by construction' for a carrier I had only construction-checked on one branch of the rule. That is FM-shaped for my own voice."* |
| 11 | Shape · payload core · `summary_text` exclusion · `workflow_id`-only keying · no gate · no HITL trigger | all three | **AGREED FROM INDEPENDENT A1s** — recorded as a finding, not a silence. |

**Two C9 additions accepted after the ledger closed, each answering a peer constraint rather than restating a position:**

- **Omission is not an escape value.** Accepting C10's no-escape-value constraint, C9 drew the distinction C10 had not: a caller who omits the token *made no claim* — omitted → byte-identical to today is what preserves the crash-recovery path that exists now. **The fence is refusal-only AND claim-scoped: it protects a composed claim; it does not make fencing mandatory.** *"A spec leg that reads 'refusal-only' as 'unfenced resume is now impossible' would be overstating it, and I would rather state the limit than have it discovered."*
- **The fence NARROWS, it does not CLOSE.** C10's §5 harm — *a decorative fence retires the register row that would have gotten the window closed* — *"applies with almost equal force to a **sound** one."* **⇒ The row must be booked as a mitigation, never as "closed."** *(At the consolidated reconcile this was sharpened further: C9 withdrew the sub-resolution residual entirely as avoidable — §10 — so the caution now attaches to the **unstated substrate invariant** rather than to an accepted collision. The discipline is unchanged: book a mitigation as a mitigation.)*

### 5.1 — Consolidated-reconcile ledger (post-review; §12)

| # | Position | Held by | Outcome |
|---|---|---|---|
| 12 | "Omission is not an escape value; the fence is claim-scoped" | C9 (round B) | **STRUCK.** *"A control that requires an affirmative extra act from every well-intentioned caller is safe-by-diligence, which is a species of luck."* Replaced by a required typed carrier + non-downgradability (§6.3). |
| 13 | Sub-resolution collision accepted as residual "booked as a race" | C9 (round B) | **WITHDRAWN as avoidable.** The excluding caveat over-generalized position-as-counter to position-as-change-detector (§10). |
| 14 | "The token must be content-derived, **never positional**" | C9 (round B) | **NARROWED** to reject position-as-semantic-counter only. |
| 15 | P2 as stated ("the FIRST surface to reopen that window") | orchestrator probe | **SCOPED to in-process** (§2 P2); "TOCTOU" replaced by **"supersession window"** throughout. |
| 16 | §8.2 as an A/B binary | orchestrator | **THIRD OPTION ADDED (A′)** and recommended — merge-coupling is separably decidable from the closure criterion (§8.2). |
| 17 | Flat payload row with a dual-kind key + boolean discriminator | C10 (A1) / orchestrator | **REPLACED** by a four-variant closed union — the flat shape made an illegal state representable (§6.2). |
| 18 | CP publishes **set**-returning siblings | C10 (A1) | **WIDENED** to typed location projections; one-authority argument *strengthened*, not contradicted (§6.6). |
| 19 | `step_kind` is "free (already captured)" | C10 (A1), accepted by C11 (round B) | **CORRECTED** — absent from the primary carrier; resolved per-variant (§6.2). |
| 20 | `summary_text` exclusion is "free because empty" | C10 (A1) | **RE-ARGUED** onto the forward-channel leg; "free today" conceded as under-grounded + time-limited (§6.2), with a reopening trigger registered (§10). |

**Zero unreconciled findings at the E4 gate.** Two residuals are carried explicitly rather than folded (§12 E4).

---

## §6 — RECOMMENDED READING

### 6.1 API shape — a NEW standalone module-level read function

**Unanimous, from three independent A1s.** A new public async read on the `harness_runtime.api` surface, taking the **identical triple** `(workflow, resume_handle, config)` that `resume()` already requires — promoting the shape of the existing module-private `_read_durable_pause_snapshot` (`api.py:682`) rather than inventing an input.

The ergonomic argument is unusually clean (C11): *"a pre-flight read that demanded information the operator does not yet possess would be worthless. **This one demands precisely what they are already holding.**"* The blast-radius argument is independent and agrees (C10): one new symbol, its own return type, its own failure attribution, reviewable and **retractable in isolation**.

**Keyed `workflow_id`-only**, matching `resume()` exactly — *"key on what you can act on; fence on what you read."* Keying more precisely than `resume()` can act on would let an operator inspect a state they cannot then resume.

**Framing (C11, and it is a design constraint, not a nicety):** do not name it after the journal. The operator's question is ***"what is this workflow waiting on?"*** — *"naming the accessor after the journal invites the payload to drift toward the journal's shape."*

### 6.2 Payload — a NEW typed projection DTO, closed-schema

Not bare identities (unanswerable — *ritual approval*, an audit-integrity failure). Not the raw `PauseSnapshot` (open-ended schema coupling — R-1 is not hypothetical; the type gained a field this month).

**Shape: a CLOSED DISCRIMINATED UNION of four location variants, NOT a flat row with optional fields.** *(Revised at the consolidated reconcile after an out-of-family [P1] found the flat shape could not represent a third state at all — see §12. C10 owns this ruling.)*

The first draft encoded one fact across two orthogonal fields — a dual-kind `addressing key` plus a boolean gate-owning-vs-container flag — **which is precisely what made the illegal state representable.** Collapse them: **make the resolution channel the discriminant, and let a key field exist only on the variants that have one.**

| Variant | Source carrier | Key field | Semantics |
|---|---|---|---|
| **`HitlAddressable`** | `PausedChildBranchResumeState` (`:893-944`) | child `run_id` | keys `hitl_responses` |
| **`EffectFenceAddressable`** | `EffectFencePausedBranchResumeState` (`:980`) / `OrchestratorEffectFencePausedResumeState` (`:712`) | `idempotency_key` | keys `effect_fence_resolutions` |
| **`UniformFallbackOnly`** | `PreDispatchGateOwningBranchResumeState` (`:248`) | **none — field ABSENT** | gate-owning, always unaddressed, resolvable ONLY by the uniform fallback when sole (CP v1.108 §1.1(a)+(b)) |
| **`TransitivelyPaused`** | container node | **none — field ABSENT** | not gate-owning, not counted; position only |

**Why the third variant exists at all, and why it was nearly missed.** `_collect_gate_owning_run_ids` (`workflow_driver.py:2781-2825`) returns a `list[str]` **mixing** genuine child `run_id`s with `_pre_dispatch_gate_owning_branch_identity(...)`-composed strings (`:2679`), and `compute_hitl_uniform_fallback_eligible_run_id` (`:2856-2903`) forces every such identity into the unaddressed set unconditionally (`:2895-2899`). Read against CP v1.108 §1.1(a)/(b), a pre-dispatch gate is **three things at once — counted, never-keyable, AND required to be delivered the uniform response when sole.** That is a state the flat shape had no room for.

**Three constraints on the union, each load-bearing (C10):**

1. **`UniformFallbackOnly` carries no identity value at all — not opaque, not redacted, *absent*.** The internal identity is resolver-only, and *"anything the DTO surfaces will eventually be pasted into a map."* This makes v1.108 §1.1(b)'s prohibition **a type invariant rather than a convention — the field does not exist to misuse**, which is strictly stronger than an opaque token because there is nothing to paste. **The harm being foreclosed is specific and is the worst of the three:** the identity is a `run_id`-shaped string, so an operator who keys it hits the resolver's collision defence (`:2890-2894`), which counts that response as *unaddressed* — **the response is silently DROPPED, not refused. Livelock with no diagnostic.**
2. **Enumeration MUST be TOTAL over gate-owning locations.** Not tidiness: property 4's sole-member rule fires at exactly 1, and the DTO's contents are what the operator reasons from when judging whether a uniform response is safe. *"Omit pre-dispatch locations and that judgment **inverts** — the operator concludes 'one location, uniform is safe' when the true set has two."*
3. **The variant name must state the channel.** Rendering a required-delivery path as "not addressable" reads as a dead end and drives abandon/restart; `UniformFallbackOnly` states both facts.

**Fields carried on every variant:**

| Field | Grounding | Why |
|---|---|---|
| **`pause_reason`** (**6**-class incl. `EFFECT_FENCE_AMBIGUOUS`) | `pause_resume_protocol_types.py:49-76` | **Required-for-safety**, not orientation: the **map-routing discriminator**. Misrouting is a misattribution of property 4's class. **BOTH identity kinds are mandatory** per CP v1.107 `:34`'s round-4 scope-limit note as corrected at `:36`. |
| **workflow position** — `step_index`; `step_id`; `branch_index` where the carrier has them | `PauseSnapshot.step_index`; `PausedChildBranchResumeState.step_id`; `FanOutBranchResumeState.branch_index` | Structural, hash-covered, author-written. **Position is what `UniformFallbackOnly` gives the operator in place of a key, and it is sufficient.** |
| **`created_at`** (or a derived age) | `PauseSnapshot.created_at`, epoch ms | Double load: C11's staleness/TTL guard **and** the real cross-pause discriminator (`run_id` is reused, so it is not one). |
| **the opaque staleness token** (§6.3) | accessor-minted, one per read | Mechanism, not display. |

**`step_kind` — declared PER VARIANT, neither blanket-included nor routed out.** It is captured at `:248`, `:712`, `:980` — i.e. free on **three of the four** variants — and **absent from `PausedChildBranchResumeState`**, exactly the primary one. Routing it out discards three free fields to accommodate one gap; adding it capture-side is a hash-affecting change requiring §1.3a-style authorization inside a read-only arc. The union makes the resolution automatic: **each variant declares the fields its carrier actually has.** *(C10: "the record's blanket row was only wrong **because** the union was missing; fixing the union fixes it as a side effect.")* Where present, **declare the closed domain — do not inherit `str`.**

**EXCLUDED, each for a stated reason:** `state_summary.summary_text`; `FanOutResumeState.orchestrator_output` and each branch's `output` (model-generated payload — a *channel* claim, not a confidentiality one, since P0 shows it is already caller-reachable); `external_references` / `relevant_entries`; `snapshot_hash` / `state_ledger_anchor` / `hitl_gate_config_hash` (opaque digests an operator might wrongly believe they should act on); the raw `PauseSnapshot`; **gate description** (not in the durable snapshot at all — capture-side scope, routed out at §10).

**The `summary_text` exclusion, RE-ARGUED (C10, reconcile round) — it gets STRONGER, and the record must say why.** The debate-round argument had two legs, and the E2 pass falsified one of them. Leg (i) — *"the exclusion is free, since `summary_text` is `""` everywhere"* — is **time-limited and was under-grounded**: the emptiness is a property of the deferred placeholder reader (§1.3), whose documented successor *"reads the current ledger head."* Leg (ii) — the unbounded forward channel — is **confirmed and now carries the argument alone**:

> *"The placeholder is a placeholder **for real ledger content**, with no redaction contract anywhere. An exclusion decided while the field is empty is free; the same exclusion after it carries ledger content is a **removal from a shipped caller-facing contract**, which nobody makes. Decide it now, and state it as forward-load-bearing, not as free-because-empty."*

**Honest counter, left unsmoothed:** when the reader is composed for real, C11's ergonomics case for inclusion genuinely reopens. So a **reopening trigger** is registered (§10), not a gate: when §14.14.7's deferral is discharged, the projection's field set MUST be re-adjudicated, with a redaction contract as a **precondition** of any inclusion. C10 explicitly declined the available over-gate — demanding a redaction gate now — on the ground that *"the field is excluded, so there is nothing to redact, and gating an absent channel is textbook over-gating."*

### 6.3 The staleness fence — a refusal-only precondition on `resume()`, opaque-token-carried

**The council's most consequential output, and it is not what the register row anticipated.**

- **Property, never composition.** The spec states: *the token MUST differ between any two durably-journaled pause records of the same workflow that a caller could successively observe.* Composition is **impl discretion, verified by execution**, per the §14.8.8.10 CONTRACT-not-mechanism precedent this very spec set for itself. **Do NOT name `snapshot_hash`, and do NOT name `(snapshot_hash, created_at)`** — P4 is the proof that naming a composition three rounds before anyone executes it is exactly the v1.106 error.
- **Zero new persistence owed.** `_append` writes the **full** `snapshot.model_dump(mode="json")` per record, append-only, never truncated — so `created_at` is in the *record* even though it is not in the *hash*, and a content-derived identity over the record as read is available with no capture-side change. *(Caveat, C9: the torn-append self-heal leaves ignored non-latest lines, so **record count is not a clean pause counter** — the token must be content-derived, never positional.)*
- **Refusal-only, by construction not convention (C10's shape constraint, accepted unconditionally):** the value domain contains **no** member meaning *proceed regardless* — no `force=True`, no `fence="skip"`, no sentinel, and it must not be typed as a union that could later admit one. *"The moment an escape value exists, the object has silently become the mode flag I rejected, and it will be reached for the first time an operator hits a mismatch they believe is spurious."*
- **BINDING IS REQUIRED, NOT OPTIONAL — the token rides a required typed carrier.** *(Revised at the consolidated reconcile. An out-of-family [P1] found that an OPTIONAL token makes omission itself the prohibited escape: `resume()` cannot distinguish "read the accessor, then omitted" from "never read," so **every accessor user's default path is unfenced**. C9's earlier claim-scoping — "omitted → byte-identical to today; omission is not an escape" — is **STRUCK, not softened**.)* C9's concession, verbatim: *"My rebuttal answered the **adversarial** caller. Codex is answering the **default** caller, and the default is the whole population the fence exists for … An optional token makes the mitigation opt-in for precisely the callers it protects. My own stated requirement was 'refusable by construction, not safe by luck.' **A control that requires an affirmative extra act from every well-intentioned caller is safe-by-diligence, which is a species of luck.**"* Three requirements:
  1. Responses composed from an accessor read arrive in a form that **carries the token non-optionally**, so `resume()` can distinguish read-then-omitted (now *unrepresentable*) from never-read.
  2. The **legacy no-read path is its own variant**, carrying no token, semantically **byte-identical to today**. This pays the byte-compat cost claim-scoping was protecting — *"and it pays it better than optionality did, because the type now records which path the caller is on instead of inferring it from an absence."*
  3. **The legacy variant MUST NOT be constructible from an accessor-derived one** — no downgrade, no `.without_token()`, no field mutation (frozen carriers, consistent with `PauseSnapshot`). **This is what keeps C10's no-escape rule intact:** C10's harm requires the escape to be reachable *as a response to a refusal*; non-downgradability makes the unfenced variant reachable only by a caller who never read. *"Without this constraint, the fix **is** the escape value C10 forbade; with it, it is not."*
- **Fail-closed on inability to mint (C9, unchanged and reinforced):** if the accessor cannot compute a token, it must not return a projection carrying an absent token that the resume then reads as "no claim." **No-token-returned must mean no-projection-returned.**
- **Co-requisite: the spec leg MUST state the substrate invariant the property depends on.** *(Added at the reconcile.)* §6.3's property is satisfiable only because the per-workflow journal is append-only and never truncated — but **that invariant is nowhere stated in the spec.** `Spec_Harness_Runtime_v1.md:5651` says *"append + `fsync` + directory-`fsync`-on-new-file, latest-record semantics, fail-closed-on-corruption"* — "append" is descriptive; "never truncated" appears nowhere. C9: *"Building a stated absolute property on an unstated substrate invariant is **exactly the v1.106 §14.8.8.10 error P4 caught** — one layer down."* State it as a §14.14.8 property, not an inherited behavior.
- **The refusal's operator-facing text is a C11 obligation, not a typed code alone:** it must say, in prose, *the workflow's paused state changed since your read; re-read and recompose.* *"A refusal the operator cannot act on is a livelock with good manners."*

### 6.4 Failure taxonomy — a cause-attribution refinement, NOT a new fail class

`read_latest` returns `None` for **five** distinguishable causes (`journal_workflow_pause_store.py:127-139`), and Runtime `:3291` collapses them again into one `RT-FAIL-RESUME-HANDLE-UNKNOWN`.

The collapse must not stand — **but the stronger reason is C9's, not the ergonomic one**: the `OSError` cause is **`transient`** in the fail-class taxonomy, and a collapsed `None` presents as permanent absence, **erasing the classification the retry mechanism is defined to consume.**

**Instrument:** a **cause-attribution refinement of the EXISTING fail class** — `absent` / `empty-journal` / `read-error` / `corrupt-latest` / `workflow-mismatch` — carried **identically by both surfaces**, as **stable identifiers** (not prose; prose is unconsumable by a routing decision and reconstructs the collapse in better clothes). **No new peer fail class is minted.**

*(The vocabulary was four members at first draft; the E2 pass found `read_latest` has **five** distinguishable `None` branches — `not path.exists()` → **absent**; `OSError`/`UnicodeDecodeError` → **read-error**; `not lines` → **empty-but-present, which had no member**; `_parse_snapshot` → **corrupt-latest** or **workflow-mismatch**. C9 ruled at the reconcile that `empty-journal` must NOT fold into `absent` despite sharing the *permanent* retry routing: "**collapsing on shared routing is the exact defect §6.4 exists to undo**," and the two carry different operator repairs — `absent` → this workflow never journaled a pause, check `durable=True`; `empty-journal` → a capture began and did not complete, the pause is lost, do not expect resume.)* A parallel disposition enum on the accessor would recreate C10's own two-authorities drift — the accessor saying `CORRUPT` while `resume()` says `RT-FAIL-RESUME-HANDLE-UNKNOWN` gives the operator two names for one state.

**C10's rider, accepted after C9 tested it:** the attribution names the **cause class**, never the underlying exception text or resolved filesystem path — *"an `OSError` rendered verbatim discloses resolved filesystem paths on a surface whose entire justification is that it discloses nothing new."* C9 confirmed a bare class still carries the full routing decision (`read-error` → transient → re-invoke is meaningful; `absent`/`workflow-mismatch` → permanent → re-invoking is useless), and recorded that it accepted *"as a test passed, not a concession reflex."*

### 6.5 Standing postures — declared so each absence is a decision, not an omission

| Posture | Ruling |
|---|---|
| HITL gate on the accessor | **NONE.** Read-only blast radius; zero new entries in the escalation catalog. C10 kept this through the debate: *"I have added none under debate pressure … FM-F held."* |
| Internal retry on the read | **NONE.** *"The operator IS the retry loop"* — an internal retry buys nothing a human cannot trivially do and hides the read-error signal. |
| Idempotency key | **NONE owed.** The read is naturally idempotent under content-hash shape. |
| Trace emission | **REQUIRED** (three voices). Carries: read attempt, cause-attribution, `workflow_id`, count of returned identities — **never** the identities' associated payload. **Emit the token at BOTH the read and the refusing resume**, so a stale-read refusal is reconstructable as one causal pair. Schema is C7's, named as owed. |
| `operator_response_capture_posture` | **NOT ENGAGED** — the accessor is a read and captures no operator response. |

### 6.6 CXA classification recommendation — **CP publishes; Runtime consumes; a row is owed**

**Recommendation: the CP private tree-walks gain a PUBLIC sibling returning an ORDERED SEQUENCE OF TYPED LOCATION PROJECTIONS that Runtime consumes.** Runtime must **not** re-walk the snapshot itself.

*(First drafted as "set-returning siblings." An out-of-family [P2] found that self-contradictory: the §6.2 DTO needs position, step, branch, reason and addressability **per location**, which bare identifier sets cannot populate without Runtime re-walking — the very thing this section forbids. C10 sustained it and sharpened the direction of the fix:*

> *"The two are separable and both reviewers conflated them. **One-authority is about the CLASSIFICATION** — gate-owning vs container vs never-keyable — and a bare identifier set is exactly what **destroys** it, since the classification lives in the carrier rows the walk visits and the caller must re-derive it. The finding therefore **strengthens** §6.6 rather than contradicting it; only the word 'set-returning' was wrong."*

*And it is worse than filed in one respect: under §6.2's union, the pre-dispatch internal identity must **not cross the seam at all** — a set of identifier strings is not merely insufficient, it carries the one value that must not be carried.)*

**What CP must publish:** one function returning an ordered sequence of typed location projections — the **authoritative classification** (the §6.2 variant) plus tree position — minus Runtime-owned fields. Runtime composes the caller-facing DTO by adding **only** root-level and accessor-minted fields (`created_at`, the staleness token, the cause attribution).

**Acceptance criterion, checkable rather than prose (C10):** *Runtime's accessor contains **no recursion over `PauseSnapshot`** and reads **no nested resume-carrier field**.* That is the operational form of one-authority; "must not re-walk" as prose is not verifiable.

The argument is **safety, not bookkeeping**, and both primaries reached it independently:

- **C10:** the gate-owning-vs-container distinction (v1.106 property 5) plus B-72's never-keyable identities (v1.108) is a *safety* classification. Re-walking gives it **a second authority, and the two can drift** — *"an accessor that lists a container branch as addressable invites the operator to key a response the resolver will refuse (livelock); an accessor that omits a gate-owning branch the resolver counts leaves it unaddressed (misattribution — the exact property-4 harm)."*
- **C11:** *"The operator-facing enumeration must be the same computation the resolver uses, **or the loop lies to the operator**."* Gate-ownership semantics have been corrected three times in six weeks (v1.106 property 5, v1.108 property 6, v1.111 property 8) — a second authority would have had three opportunities to diverge already.

**The classification statement the spec leg must author, stated precisely (and modelled on the CP v1.110 / plan v2.46 precedent, where an initially-claimed "zero cross-axis cascade" was corrected pre-merge to "the touch is real, same established boundary, no NEW seam"):**

> The projection-returning surface rides the **EXISTING** CP→Runtime crossing point already used by three sibling public computations at `mcp_server.py:266-278` (`compute_hitl_uniform_fallback_eligible_run_id`, `compute_effect_fence_uniform_fallback_eligible_key`, `compute_effect_fence_tree_wide_abort_present`). **No NEW crossing point is introduced — but the touch is real and MUST be named, not assumed away.** **And the PAYLOAD widens materially — from three scalars to a structured sequence — which the classification statement MUST say** (C10: *"do not let 'no new crossing point' carry weight it cannot"*). Whether that lands as a NEW `Cross_Axis_Composition_Document` §2.3 row or as coverage under the existing crossing is the CXA determination owed at the spec leg; **it must be stated explicitly, never carried forward unexamined** (the discipline CP v1.106 `:250` applied to itself).

`[MODERATE]` on the row-vs-coverage mechanics — that is CXA's call, not the council's. `[HIGH]` on the one-authority principle and on the obligation to state it.

---

## §7 — Runner-up, and why not

**Runner-up: an optional pre-flight MODE on `resume()`.** It is the runner-up because it is *superficially the tidiest* — one call, no second surface, and it appears to preserve the atomicity the register row worried about losing.

**Rejected unanimously, and the reason is worth carrying into the spec leg verbatim so it is not re-proposed:**

- **C10:** `resume()`'s entire safety story is a stack of detect-then-refuse guards *culminating in execute* (`RT-FAIL-RESUME-ARGS` / `-PROTOCOL-NOT-BOUND` / `-WORKFLOW-MISMATCH` / `-STEP-INDEX-OUT-OF-RANGE`, Runtime :3275-3279). A mode flag makes every one of them mode-conditional and introduces a **fail-open mode-confusion hazard on the single call in the system that starts paid, effectful, ledger-writing execution. The asymmetry is total — a read mistaken for a resume executes side effects; a resume mistaken for a read merely no-ops.** *"You do not put a 'don't actually do it' flag on the function whose job is doing it."*
- **C11:** *"It does not preserve atomicity; it destroys it"* — the failure mode of getting the flag wrong is *executing a workflow you meant to inspect*. Plus concurrency-guard contamination: `resume()` raises `RT-FAIL-CONCURRENT-RUN` when a call is in flight (`api.py:851-855`), so a mode would plausibly refuse an operator a **read** because of exactly the in-flight state they most want to inspect.
- **The mode's one genuine appeal is answered without adopting it.** Its "no TOCTOU" pitch is real — and §6.3's refusal-only precondition captures it, because **a precondition is a different object from a mode**: no value of it causes execution. C9 drew the distinction and C10 conceded its own asymmetry does not reach it. **The mode rejection stands unreversed; the precondition is admissible.**

**Second runner-up: a field on `RunResult` — rejected as structurally circular.** You obtain a `RunResult` only by having already run or resumed, which is precisely what the crash-recovery caller lacks. *"Option (c) puts the map inside the box the operator cannot open"* — it serves only the `pause_snapshot` caller, who already holds every identity.

---

## §8 — Operator-tier fork

### 8.1 The exposure tradeoff needs NO operator gate — stated plainly

The register row anticipated the exposure tradeoff as the likely operator question. **It is not one.** P0 + C10's strengthening establish that the accessor grants a strict subset of the authority `resume()` already grants the identical caller with the identical inputs, and that the raw snapshot is *already* caller-reachable on re-pause. The two residuals P0 left open (schema coupling; repeated pre-resume inspection) are both answered by the **payload** decision, not by a gate. **All three voices converged, including — decisively — the voice whose domain would have owned the objection.** C10 declined to manufacture one and named doing so as its own failure mode (FM-F, over-gating).

**No gate is proposed here. Manufacturing one would be the failure this council's own discipline names.**

### 8.2 One operator-tier question DOES survive — and it is a SCOPE question

The council converged on what is *right*. It cannot self-authorize the *scope* that follows, and C9's SEAM-4 adjudication says so explicitly on X-AL-3 grounds: **B-69's register row authorizes an accessor. The staleness precondition amends a DIFFERENT, already-cleared contract** (the `resume()` pre-bootstrap fail-class battery, Runtime v1.106 §30 / C-RT-35). Folding that into B-69's row silently is precisely the design-extension X-AL-3 forbids — and this workspace's own precedent (B-70, 2026-07-24) routes exactly this shape to an operator `AskUserQuestion` before the spec leg opens.

> ### THE QUESTION
>
> **B-69's spec leg needs to author a durable-pause-state read accessor. The council found — unanimously, after two voices withdrew their contrary claims — that shipping that accessor ALONE is net-negative on the crash-recovery path it exists to serve: it converts the operator's known guess into a believed fact, and a stale enumeration plus a uniform default can deliver a HITL response to a branch the operator never saw (CP v1.106 property 4's sole-member carve-out permits it). The mitigation is a refusal-only staleness precondition on `resume()` — which amends an already-cleared contract that B-69's register row does not authorize.**
>
> **(A′) — CO-REQUISITE, SEQUENCED. ← the council's recommendation.** Both surfaces authorized under **one arc gate** with the X-AL-2 conjunctive closure criterion: B-69 closes iff *(accessor landed) ∧ (precondition landed ∧ exercised by the W3 mutation-probe)*; partial is non-closure. The spec surfaces and their impl units **MAY land in separate merges within the arc**, subject to one ordering constraint: **the staleness precondition lands first or simultaneously — never after.** No interval exists in which an unfenced accessor is reachable on `main`.
>
> **(A) — CO-REQUISITE, CO-MERGED.** As (A′), but additionally requiring both surfaces to land in the **same merge**.
>
> **(B) — ACCESSOR-ONLY.** Author the accessor alone under B-69's existing authorization and register the staleness/fencing hazard as its own new `B-*` row for a later arc.
>
> **Council recommendation: (A′), with (A) acceptable and (B) rejected.**
>
> *(The A/B pair was the first draft; the E2 pass found it had narrowed the choice set past what the council actually adjudicated — C9 ruled for two-surfaces/one-gate, and C11's "same arc, same merge" was a **separate** addition. C9 at the reconcile: the two are **separably decidable** — the conjunctive criterion governs *when B-69 may be called done* (a **register** state), merge-coupling governs *when the surface becomes reachable on `main`* (an **operational** state) — and **"the minimum that closes the operational harm is landing ORDER, not landing ATOMICITY."** C9 prefers (A′) over (A) on this arc's own stated value: a single merge carrying three spec surfaces, two-plus impl units and W1-W4 is a large diff, against C10's §6.1 argument for the standalone read being "retractable in isolation" — **fusing them forfeits that for no additional safety.** `[HIGH]` on separability; `[MODERATE]` on (A′)-over-(A), a reviewability judgment rather than a reliability one.)*
>
> (B) remains *"land the regression and register the fix,"* the shape this workspace's discipline exists to prevent. **The council's reason for surfacing this at all is authority, not doubt:** it is a scope expansion against a cleared contract, which is the operator's to grant.
>
> **One sizing correction the operator should have (C9, reconcile round).** §6.3's required typed carrier may need to live on **CP's** `ResumeContext` (v1.106 `:28`, where `hitl_responses` lives; `:95` is the very scope-limit B-69 lifts) rather than Runtime-side — in which case the arc carries **three** spec surfaces, not two. The alternative (Runtime-only: `resume()` accepts the accessor's projection object alongside the responses) is simpler but leaves *"these responses came from **this** read"* untyped. C9 recommends the CP carrier and flags that it **makes (A′)/(A) larger than described — not a new gate, a correction to the size of the one already asked.** `[MODERATE]` on which reading the spec leg lands.

### 8.3 What is NOT being asked

Not the exposure tradeoff (§8.1). Not the API shape, the payload boundary, the failure-taxonomy instrument, or the CXA classification — all converged with concessions in every direction and are carried as recommendations, not options. Not R-3 or the other routed-out findings (§10), which are register work, not gates.

---

## §9 — Minimal spec-delta set the spec leg should author

*Nothing below is built. Every item is **owed**, per X-AL-3 — this record authors no design-substrate text and asserts no landed surface.*

| # | Artifact | Delta | Gate |
|---|---|---|---|
| **1** | `Spec_Harness_Runtime_v1.md` → **v1.107** | **NEW contract surface** for the accessor. Recommended home: a NEW **§14.14.9** sibling to §14.14.8 (the store it reads), cross-referenced from C-RT-35 §30 — *or* a new `C-RT-*` contract if the spec-writer judges a caller-facing read to warrant its own contract number (`:680`'s "no new operation" framing says this one **is** a new operation). Carries: the signature + `(workflow, resume_handle, config)` input triple; the typed projection DTO (§6.2, closed-schema, declared domains); `workflow_id`-only keying; the fail-closed-on-inability-to-mint rule; the no-gate / no-HITL-trigger / no-internal-retry postures. | — |
| **2** | `Spec_Harness_Runtime_v1.md` (same delta) | **AMEND `:3274`** — the `resume()` "Resume-context one-shot delivery" invariant bullet. Its scope-limit note ends *"registered, NOT designed or scoped by this delta"*; that sentence is **discharged** and must be replaced by a cross-reference to the new surface, not left as stale-carry. | — |
| **3** | `Spec_Harness_Runtime_v1.md` (same delta) | **NEW: the refusal-only staleness precondition** on `resume()` + its cause-attribution refinement. Extends the `:3288-3294` fail taxonomy with a staleness fail class and the four-way cause attribution on the EXISTING `RT-FAIL-RESUME-HANDLE-UNKNOWN` (**no new peer class for the attribution**). States the token **property**, never a composition. | **operator gate §8.2** |
| **3b** | `Spec_Control_Plane_v1_111.md` → **v1.112** *(conditional)* | **The required typed response carrier** binding accessor-derived responses to their staleness token (§6.3), if the spec leg lands C9's recommended CP-homed reading rather than the Runtime-only one — amending `ResumeContext` (v1.106 `:28`). Non-downgradable from accessor-derived to legacy variant. **This is the "third spec surface" the §8.2 sizing correction names.** | **operator gate §8.2** |
| **4** | `Spec_Control_Plane_v1_111.md` → **v1.112** | **Lift the v1.106 `:250` scope-limit** — follow-on (a) is no longer unresolved. **Lift the v1.107 `resume_handle` scope-limit note** — the note itself is the **round-4** correction at `:34`; `:36` is the separate round-5 correction that fixed B-69's *citation* by widening the row to both identity kinds. **NEW: the public projection-returning surface** over `_collect_gate_owning_run_ids` / `_collect_effect_fence_idempotency_keys` (§6.6 — typed location projections, **not** bare identifier sets), publishing the four-variant classification of §6.2 including the never-keyable pre-dispatch identities (v1.108) — which **must not cross the seam as a value**. *(Delta-chain note: these are amendments to notes that live at v1.106/v1.107; the delta must say so, or the lift will not resolve byte-exact.)* | — |
| **5** | `Cross_Axis_Composition_Document_v2_22.md` → **v2.23** | The **CXA classification statement** per §6.6 — explicit, re-verified at the pass, never carried forward unexamined. Row-vs-existing-coverage is CXA's determination. | — |
| **5b** | `Spec_Operational_Discipline_v1_35.md` → **v1.36** *(or an explicit statement that it rides an existing namespace)* | **The trace-emission home** for the read + refusing resume (§6.5), which this record rules REQUIRED. OD owns the observability namespace schema (root `CLAUDE.md` §1.1; `harness-cp/CLAUDE.md` §1.4: *"Authoritative schema lives at OD spec"*). *(Added at the E2 pass — the first draft ruled the emission REQUIRED at §6.5 but gave it no delta row, and "named as owed" inside §6.5 does not discharge it: **§9 is the artifact the spec-writer works from.** C10 accepts the row and scopes it: it states the obligation and leaves new-namespace-vs-existing to OD's determination, mirroring §6.6's own row-vs-coverage discipline.)* | — |
| **6** | `Implementation_Plan_Harness_Runtime_v2_54.md` → **v2.55** | **NEW U-RT unit** for the accessor + DTO + fail attribution, carrying the **§11** witnesses as acceptance criteria (**W2 in the 1→1 shape is the primary witness**). Under (A′) the precondition rides the same unit or a paired sibling, landing **first or simultaneously** — never later, and **not a later arc**. | — |
| **7** | `Implementation_Plan_Control_Plane_v2_46.md` → **v2.47** | Plan delta for the CP-published **projection-returning** surface + the §6.2 four-variant classification (amend the owning unit; a deferred coverage-matrix row is the wrong instrument here — unlike v2.43/v2.44/v2.46, this surface *does* have an owner). Carries C10's checkable one-authority criterion: *Runtime's accessor contains no recursion over `PauseSnapshot` and reads no nested resume-carrier field.* | — |
| **8** | `.harness/clearance/` | One marker per amended artifact, per §4.5. | — |
| **9** | `.harness/forward-register.yaml` + `post-phase-8-forward-register.md` | B-69: `registered_finding` → `design_substrate_gated` (or `open` post-gate); `council:` **TBD at build time → ran 2026-07-30, converged, record at this file**. **Closure criterion recorded in X-AL-2 conjunctive form** per §4/SEAM-4. Plus the §10 rows. *(Deliberately NOT touched by this arc — the register update rides the spec leg.)* | — |

---

## §10 — Findings routed OUT of this arc (registered, not absorbed)

*Per the B-64/B-67/B-73/B-80 split-out discipline. Each is real; none is B-69's.*

| Finding | Disposition |
|---|---|
| **R-3 — the pause journal carries no tenant binding.** Runtime §14.8.11 (`:4636`, `:4639`) commits a full-strength tenant-composite key + typed cross-tenant refusal for comparable durable state; `JournalWorkflowPauseStore` is `workflow_id`-keyed, one file per workflow — and now carries recovered branch outputs. | **NEW `B-*` row. PRE-EXISTING, not B-69's** (`resume()` reads the same key today; the accessor adds zero tenant exposure). **Urgency raised** by an independent reliability finding: two processes sharing a resolved `STATE_LEDGER` dir are serialized by **nothing** — `_append` uses a plain `open("a")`, no `O_EXCL`, no lockfile, no advisory lock — so the store's threat model is *weaker* than the one §14.8.11 already protects. **Boundary unchanged:** fixing it changes the store's **keying**, dragging a capture-side change into a read-only arc. |
| **~~The staleness residual after fencing~~ — WITHDRAWN at the consolidated reconcile.** The first draft booked a sub-token-resolution collision (two pauses inside one millisecond, if `created_at` were the discriminator) as an accepted *race*. An out-of-family [P1] found this **contradicts §6.3's own absolute property**, and offered the constructive half: require a genuinely collision-free identity derived from the append-only journal. | **C9 CONCEDED and withdrew the residual as an artifact of its own over-generalized caveat.** *"My caveat — 'record count is not a clean pause counter, so the token must be content-derived, never positional' — rejects position-as-**semantic-counter**, and I illegitimately extended it to position-as-**change-detector**. Those are different uses: a counter must mean 'N pauses happened'; a staleness discriminator need only change monotonically between any two successively observable records."* Verified: `_append` writes one full JSON line per record (`:179`, `:189`) via `path.open("a")` (`:186`) with **no truncation anywhere in the class** — so a growth-derived identity separates even two byte-identical records, which content-derivation cannot. Torn appends degrade safely (partial trailing line → `_parse_snapshot` fails → `None` → fail-closed, the refusing direction). **⇒ §6.3's property stands unweakened; the residual is unnecessary rather than acceptable.** §6.3's CONTRACT-not-mechanism ruling is unchanged — *"I am not naming file length as the carrier; I am withdrawing the caveat that **excluded the whole class it belongs to**"* — and the **substrate-invariant co-requisite at §6.3 is the price of that** (the append-only/never-truncated invariant is an implementation fact the spec does not state). **Surviving, demoted:** if the impl leg finds two successive journal records byte-identical in full, that is a **capture-side observability finding to route** — it no longer implies the fence cannot fire. |
| **`summary_text` reopening trigger** (C10, reconcile round). The §6.2 exclusion now rests on the forward-channel leg alone, because the "free today" leg is a property of a deferred placeholder whose successor *"reads the current ledger head."* | **Registered as a named condition, NOT a gate.** When §14.14.7's deferral is discharged and a real `pause_context_reader` is composed, the projection's field set MUST be re-adjudicated, with **a redaction contract as a precondition of any inclusion**. C10 explicitly declined the available over-gate (demanding a redaction gate now): *"the field is excluded, so there is nothing to redact, and gating an absent channel is textbook over-gating."* The trigger exists so this record's justification cannot go stale silently. |
| **Gate description / question text is absent from durable state.** Verified across every `PauseSnapshot` field, and symmetrically for C10's `HITLPlacementKind` counter-proposal — no durable pause carrier declares a field of either kind. | **NEW `B-*` row if the operator loop later demands it.** Capture-side, hash-affecting, X-AL-3-relevant — materially bigger than a read-only projection. Explicitly declined for this arc by the ergonomics voice. Note this is adjacent to but **distinct from** `B-71` (which adds a run-instance correlation id to `HITLEscalationBrief`/the webhook payload). |
| **Class 3 cite-hygiene inside `pause_resume_protocol_types.py`** — **three** stale docstrings, count re-verified programmatically at the E2 pass. `PauseSnapshot`'s class docstring says *"8-field pause-snapshot envelope"* for a **15**-field type *(the first draft of this very row said "nine" — a second miscount, in the row whose own justification is that enumerating from these docstrings undercounts; recounted and confirmed at 15)*. `pause_reason`'s docstring says *"5-class enum"* for a **six**-member enum. And `snapshot_hash`'s docstring at `:776-777` still describes a **four-element** hash — **the very docstring whose staleness P4's first premise reproduced.** | **Fold into the spec leg's impl arc.** Not cosmetic: a projection arc enumerating from these docstrings will undercount `EFFECT_FENCE_AMBIGUOUS` — **the one member carrying the 2026-07-24 widening's weight** — and mis-state the hash's coverage. It caused **two** real miscounts inside this convening, one of them in the correction itself. |
| **Divergent durable-pause postures (C11, FM-I, flagged against its own matrix).** The HITL approval queue is durable + TTL-bounded + per-item status + surfaced on next operator-touch; the §14.14.8 journal is per-workflow latest-record, **no TTL, no status, no enumeration**. | **Recorded, not actioned.** Unifying tier semantics is C3's surface and would be scope creep. **Constraint carried forward:** the DTO must not be shaped to imply the journal *is* the `hitl_queue`. |
| **Eval measurable (C8's methodology, C9's surfacing).** **Fence *false-match* rate** — refusal rate alone would have shown a `snapshot_hash` fence as perfectly quiet, *"quiet because it never fired, which is indistinguishable from quiet because nothing was stale."* | **Handed to C8.** The one measurement that would have caught P4 empirically. |

---

## §11 — Witnesses owed at the impl leg (by EXECUTION, not grep)

C9's standing refusal, and it is the sharpest sentence of the convening: *"'`resume()` re-reads the journal, therefore the caller's read is untrusted' … proves the **snapshot** is re-derived. It does NOT prove the operator's **response map** was composed against the same snapshot. **Two different objects; only one is re-derived. That distinction is the entire finding.**"*

| # | Witness | Why grep cannot substitute |
|---|---|---|
| **W1** | Wrong-key case constructed with **2+** unaddressed gate-owning branches → assert INERT re-pause per property 4's 2+-member clause. | A one-branch witness proves nothing about that clause — the sole-member carve-out is the *other* branch of the rule, and it is the unsafe one. |
| **W2** *(PRIMARY)* | **The sole-member misattribution, in the 1→1 shape** (C11's sharpening; 3→1 secondary): stale read enumerating one location A + a supplied uniform `hitl_response`; live cycle's sole gate-owning member is D ∉ {A}. Assert D does **not** receive the uniform response **under a fence** — and, **without** the fence, assert that it **does**. | The load-bearing witness of the whole arc. **C9's own falsifier, on the record:** *"If it comes back showing D is refused by some path I have not found, my entire §1 finding collapses."* |
| **W2′** | Run W2's 1→1 shape **with a `snapshot_hash`-based fence installed** and assert it **still misattributes**. | Converts P4 from a reasoned finding to an executed one, and prevents a later session re-nominating the carrier this council conceded. |
| **W3** | The fence by **mutation-probe** (Workflow v1.18 PD-8): capture → read → force a **real** second `capture()` (a genuine re-pause, not a synthesized record) → resume with the stale token → assert typed refusal → **remove the fence check → assert the misattribution reappears**. | Green-alone is not proof a guard is load-bearing. **This witness is half of B-69's conjunctive closure criterion.** |
| **W4** *(CHARACTERIZATION — re-scoped at the reconcile)* | C11's capture-side companion: construct two successive LINEAR pauses at the same `step_index` via the request-changes / re-gate loop and assert their `snapshot_hash` values are **equal** — **injecting the placeholder `pause_context_reader` in the test rather than depending on the default binding.** | *"If they differ, P4's reach is narrower than I argued and my amplification should be struck."* **C9's re-scope (F2-01 consequence):** as first written this asserts a **placeholder property**. When a real reader lands and `state_summary` varies, W4 fails *for a good reason* — and a future session will "repair" it, the wrong disposition. **Annotate that its correct disposition on placeholder replacement is DELETION or INVERSION, never repair.** W4 is secondary regardless; **W2′ is the load-bearing empirical form of P4 and is unaffected.** |

---

## §12 — Review passes

### E2 — in-family adversarial (`harness-adversarial-reviewer`, genuine invocation)

Severity scale is `Project_Workflow_v1_8.md` §4.1 — **Class 1 = minor, Class 2 = moderate, Class 3 = severe.**

**Verdict: 0 Class 3 · 7 Class 2 · 4 Class 1 — "Cleared with current-phase revision."** All eleven are folded above.

It **tested and upheld** the three load-bearing conclusions: P4's collision; the property-4 misattribution path (*"I hunted for a refusing guard and found none … **`resume_context` is never validated against the snapshot at all**"*); and §8.2's legitimacy as a real X-AL-3 scope gate rather than a manufactured one. It also specifically expected and failed to find a v1.111 delta-chain error, confirmed all load-bearing spec cites byte-exact, confirmed P0, §6.6's three-sibling grounding, the `workflow_driver.py` symbols, R-3's grounding, the 6-class correction, SEAM 3's symmetric defeat, and X-AL-3/posture cleanliness; it called the witness shape (by-execution, PD-8 mutation probe, falsifier on record) **a strength**.

Its diagnosis of where the record failed: *"Its **grounding discipline** is where it fails — four of its cites point at docstrings, sibling carriers, or container fields rather than the surfaces the arguments need, and in three of those cases the wrong surface is the one a spec-writer would carry forward."* Folded at §1.3 (`:333`), §2 P4 (F2-01/F2-02), §4 SEAM 2 (F2-06) and SEAM 3, §6.2 (`step_kind`), §6.4 (fifth cause), §8.2 (choice set), §9 (OD row, `§10`→`§11`, `:34`/`:36`), §10 (field recount + third docstring), §11 (W4).

### E3 — out-of-family (`just codex-review-uncommitted`, GPT-5.6, $0 subscription)

**4 × [P1] + 1 × [P2], with near-ZERO overlap against the in-family pass** — which is the decorrelation this stage is paid for, and it earned its keep: **three of the five changed what the spec leg will write.**

| Finding | Disposition |
|---|---|
| **[P1] Bind accessor-derived responses to the token** — an omitted optional token is indistinguishable from "never read," so omission *is* the prohibited proceed-regardless escape | **SUSTAINED.** C9 conceded and struck its own claim-scoping (§6.3). |
| **[P1] Model never-keyable pre-dispatch gates explicitly** | **SUSTAINED, and found stronger than filed** — C10 identified a third harm (a `run_id`-shaped identity keyed by an operator is **silently dropped**, not refused). Drove the four-variant union (§6.2). |
| **[P1] Token uniqueness contradicts the accepted residual** | **SUSTAINED.** C9 withdrew the residual as avoidable (§10) and stated the substrate-invariant co-requisite (§6.3). |
| **[P1] §12 claimed passes it did not record** | **SUSTAINED — this section.** |
| **[P2] CP's set-returning surfaces cannot populate the DTO** | **SUSTAINED on shape**; C10 held that it *strengthens* rather than contradicts one-authority (§6.6) and added the checkable acceptance criterion. |

**Deviation on record.** The workflow's E3 discipline gives Codex a *descriptive primer only, never the council's conclusions*. Here the artifact under review **is** the conclusions, so Codex necessarily saw them — this was the caller's explicit instruction and is the standard `CLAUDE.md` §13.1 pre-merge artifact-review mode, not the cold-primer research mode. **Decorrelation held empirically** (near-zero finding overlap). `advisor()` was not separately invoked; the in-family adversarial pass served the Claude-family half of the decorrelated pair.

### E2b/E3b — consolidated reconcile (the spec's authorized reorder)

E2b and E3b were **collapsed into one consolidated reconcile** after all reviewer input was gathered, per `council-workflow.harness-aware.yaml` → `reorder_options.consolidated_reconcile`. C9 and C10 were re-invoked as genuine agents against the merged finding set.

**Reconciled to zero. C9 conceded 4 of 4 findings in its domain** (*"A1 and A3 are both cases of me under-generalizing my own 'by construction, not by luck' standard one layer below where I applied it. The out-of-family reviewer caught both; that is what it is for."*). **C10 sustained both Codex findings in its domain**, resolved `step_kind` as a side effect of the union, re-argued the `summary_text` exclusion onto its surviving leg, and **explicitly declined an available over-gate** — closing with an FM-F check: *"the accessor still carries no HITL gate and zero new escalation-catalog entries."*

**One convergence C9 flagged for the spec leg:** A1, A2 and F2-03 *"are all **discriminated-variant** problems on the same two objects (the projection DTO and the response carrier). The spec leg should author the discrimination once"* — or it will ship three ad-hoc shapes. That shape decision belongs with C5 (closed-schema contract) and CP.

### E4 — residual sweep

Re-verified at HEAD after the fold, by direct read rather than by trusting the plan: `PausedChildBranchResumeState`'s four fields (`:893-944`); `PauseSnapshot`'s **15** declared fields; `_run_lock` as a module-level `asyncio.Lock` (`api.py:402`); `_compute_snapshot_hash`'s `hitl_gate_config_hash` parameter (`:738`) and its hashing (`:835-839`); the `pause_context_reader` placeholder (`pause_resume_protocol_factory.py:88-107`); `read_latest`'s five `None` branches (`:127-139`).

**Verdict: CLEAR-TO-COMMIT.** The record is advisory, edits no canonical artifact, and every recommendation is phrased as owed to a spec leg. **Two residuals carried, both named in-record rather than folded:** the CP-vs-Runtime home of the response carrier (§8.2 sizing correction, `[MODERATE]`), and the CXA row-vs-coverage mechanics (§6.6, CXA's determination). Neither blocks the operator gate.

---

## §13 — Filing footer

| Field | Value |
|---|---|
| Artifact | `.harness/council-b69-pause-state-accessor-2026-07-30.md` |
| Convened | 2026-07-30 |
| Workflow | `.harness/council/council-workflow.harness-aware.yaml` v1 (harness-layer-aware) |
| Posture | Design-phase (`CLAUDE.md` §11) — `design-substrate/**` READ-ONLY at this arc |
| Voices | **C10** (primary, promoted) · **C11** (primary) · **C9** (consultant, dyadic-default expansion justified at §0.2) — each a genuine dedicated agent invocation adopting its own `cN/SKILL.md` |
| Stages run | pre-convene · E1·A1 (independent/blind) · probe · E1·A2 (react-to-real-output) · E1·B (cross-read debate) · E2 adversarial · E3 out-of-family Codex · E2b+E3b consolidated reconcile · E4 gate — **all recorded at §12** |
| Reconcile | **internal zero at E1·B** (11 ledger rows, §5) · **zero again at the consolidated reconcile** (9 further rows, §5.1) — 20 positions withdrawn, replaced or corrected across all three voices and the orchestrator's own probes |
| Tension outcome | 4 seams · **4 resolved** (3 probe-resolved, 1 by symmetric empirical defeat) · **0 surfaced-unresolved** |
| Reviewer divergence | E2 and E3 produced **near-zero finding overlap** — the decorrelation signal. Three of Codex's five findings changed what the spec leg will write; none had been caught in-family. |
| E4 verdict | **CLEAR-TO-COMMIT**, 2 residuals carried explicitly (§12) |
| Operator gate | **ONE**, at §8.2 — a **scope** question (co-requisite precondition), **not** the exposure tradeoff. Three options; council recommends **(A′)**. |
| Register effect | **NONE at this arc.** `forward-register.yaml` + `roadmap_status.md` deliberately untouched; the B-69 row update rides the spec leg (§9 row 9). |
| Authority | Advisory. This record recommends; it does not amend any canonical artifact. Per §1.3 authority chain, `design-substrate/**` wins on any conflict. |

