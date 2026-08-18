# E1-B — Cross-read debate: reconciled disposition

*Seam-routed confirm-back. Each primary received the consultant positions naming it and answered
COHERE / CONFLICT / REFINE. **E1 gate: reconciled to internal zero** — every consultant challenge
answered, no unreconciled seam remains.*

Orchestrator note: every load-bearing claim below was independently re-grounded at HEAD by the
orchestrator before being recorded. Verification cites are inline.

---

## 1. Seam outcomes

| Seam | Challenge | Outcome |
|---|---|---|
| **C1 ↔ C11** | Coalescing placement: merge door vs. temporal | **C1 CONFLICT→conceded.** "C11 is right and I was topologically wrong… I withdraw 'at the merge door' entirely." |
| **C1 ↔ C5** | Open Decision #3 stated at the wrong grain | **C1 COHERE.** Concedes the split follows from its *own* Question B: "the coarser framing was wrong-grained." |
| **C1 ↔ C10** | Implicit precondition is not a gate | **C1 COHERE.** Item 13 must refuse-to-start on a deterministic check. |
| **C3 ↔ C9** (pid inertness) | "Provenance only" leaves the field reachable | **C3 REFINE.** pid/host move under a nested key the state machine never imports. |
| **C3/C9 ↔ artifact item 5** | flock is a mechanism-family change | **BOTH CONCUR — item 5 killed as written.** |
| **C3 ↔ C5** | The new `gh` check is an unclassified gate | **C3 accepts fully**, grounded in the file's own existing rule. |
| **C3 ↔ C7** | Wrong instrument; reservation-as-sensor; missing provenance | **C3 accepts both halves** + one REFINE. |
| **C8 ↔ C5** | Probe (a) not constructible | **C8 CONCEDES fully.** "A real miss on my part, not a nitpick." |
| **C8 ↔ C7** | `concurrent_lanes` provenance class | **C8 ACCEPTS `derived`** + one refinement. |
| **C8 ↔ C11** | Measure vs. build-first | **C8 partial concession**: shape ships now, constants measured. |

## 2. Rulings that change the design

### 2.1 Phase 0 item 5 (flock) is KILLED as written — two voices, independently

C9 first: introducing `fcntl` advisory locking into `arc_metrics.py` is a **mechanism-family change
the artifact never declares**. C3 then verified and conceded its own design never needed it.

**Orchestrator verification:** `rg -c flock tools/arc_metrics.py` → **0**. The file states its
philosophy twice — `:677` *"no lock is needed to say so"*; `:719` *"Same structural fix as the queue
itself -- no lock required."* **CONFIRMED.**

C3's ruling: *"**No lock, anywhere, in this design.**"* Item 5 **re-scopes** to wrapping `drain()`'s
uncaught `os.replace` calls (success path `:754`, `AbortError` path `:746`) in
`try/except FileNotFoundError`, ABA loser logs-and-yields rather than crashing. The reservation's
transitions use the same defensive pattern from the start.

**Second-order consequence:** the fork+flock deadlock hazard C5 warned about for probe (a) becomes
*moot* once no flock lands — but the subprocess instrument is independently required anyway (§2.2).

### 2.2 AC#2 probe (a) was NOT CONSTRUCTIBLE — restated

C5's falsification, **orchestrator-verified**: `REPO`/`LEDGER`/`QUEUE_DIR` are module-level globals
(`:44-45`, `:59`); `rg -c 'threading|concurrent.futures'` → **0**. `monkeypatch.setattr(am, "REPO", …)`
mutates the one shared module object, so two in-process threads cannot observe different values.

C8 conceded fully and named the meta-hazard:

> "Had probe (a) shipped as I originally endorsed it, it would have been a **false-GREEN certificate
> on the exact hazard Phase 0 claims to close** — the same 'absent verdict reads as clean' failure
> the design doc itself opens with (X1)."

**Restated probe (a):** `subprocess.Popen` per simulated lane, each with its own git-inited
`tmp_path` worktree, sharing one `QUEUE_DIR`, filesystem rendezvous barrier, **not** `multiprocessing`
fork. **Implementer constraint C8 flagged:** `REPO`/`LEDGER` have **no env override** today (unlike
`QUEUE_DIR`'s `ARC_METRICS_QUEUE_DIR` at `:60-63`), so the harness needs either a copied/symlinked
`arc_metrics.py` per fake repo, or a new override.

**Probe (b) certified by C5**, conditional on the fixture contract: follow
`tools/test_arc_metrics.py:174-187` — leave `REPO`/`LEDGER` at production values and monkeypatch
`am.run` directly. The other **17** occurrences relocate `LEDGER`, break `LEDGER.relative_to(REPO)`,
and hit the wrong early-return branch — the false-GREEN.

### 2.3 The reservation design, final

- **Three-state enum** `pending → open → terminal{merged|abandoned}` with mandatory `superseded_by`.
- **pid/host structurally unreachable** from the state machine (nested key, never imported) — not
  merely "provenance only."
- **Ground-truth staleness** via `gh pr view`, with C9's three-tier table: `pending` → age-only
  silent reclaim; `open`+ground-truth → instant event; `open`+stuck → **warn via the existing 24h
  HITL queue, never auto-reclaim** (because `gh` cannot distinguish "slow" from "abandoned" — the
  ambiguous middle moves, it doesn't vanish).
- **Fail-safe on `gh` transient failure → "still open," never reclaimable.** Carries forward the
  file's own rule, **orchestrator-verified verbatim** at `:586-588`: *"Unknown ownership is never
  treated as dead… guessing wrong hands a live peer's arc to a second drain."*
- **No lock** (§2.1). Atomic create + atomic rename only.
- **Full provenance table** assigned; `pid`/`host` additionally carry
  `reachable_from_state_machine: false`, because provenance class alone doesn't encode inertness.

### 2.4 Detection: v1 restates the gap rather than closing it

C7: Phase 0 items 1–8 are **fixes, not instruments**; only item 9 is a detection surface — one, for
19+1 modes — and even it is a **binary CI gate, not a queryable signal**. Fix requires no new
mechanism: pair every Phase 0 fix with a finding-row emission using the **already-ratified L0.2′
record**, and have item 9 write to it rather than only gate CI.

**`concurrent_lanes` is `derived`, not `declared`** — orchestrator-verified at `:13-14`, `:124`
(`declared` = operator judgement, *"never inferred"*). **C3's reservation record is the sensor**:
count `open`-state reservations at the instant this arc's reservation flips `pending→open`.
C8's refinement: a point-in-time scalar under-counts an arc that gains company mid-window — prefer a
min/max-over-window pair.

### 2.5 Gate-coalescing (Open Decision #4) — narrowed, not open

**C11 ruling: one batched prompt**; §12.4.1 forecloses N-sequential. The mechanism **already
exists** — `loop_pending_hil_summary()` / `loop_cap_list()` / `_loop_pending_hil_rows()`
(`loop_lib.sh:165, 191-225`), asynchronous, capped at 3 + "(+N more)", rendered at the operator's
next touch. **Extend, don't invent.**

**C11's genuinely new addition:** *correlated-cause collapse*. Reduction by item-id alone still
yields 4 rows for one shared reviewer outage — drip-fed in substance. Add a `cause_signature`
second reduction key within a bounded window → one row naming all affected lanes, one response
resolving all. `edit` dropped from the response palette; TTL 24h.

**Orchestrator verification:** `grep -c 'coalesc\|batched'` on the artifact → **1** (Open Decision
#4's own description). **The finding was recorded and never enacted.**

### 2.6 X9 — a live defect, new to both prior arcs

C10 checked the client-side gate neither prior arc examined. **Orchestrator-verified:**
`permission-guard.sh:427` auto-allows bare `git push` in loop mode inside a long alternation with
**no destination-branch predicate**; the deny-list at `:321-327` catches only
`--force`/`--force-with-lease`/`-f`/`--mirror`/`--prune`/`--delete`/`:`. With `main` unprotected
server-side, this is **one auto-approved tool call from unreviewed content on `main`, at N=1, today.**

**C10 rules YES on branch protection** (Open Decision #5): every legitimate path already goes
through `gh pr merge`, so protection blocks nothing real and closes both halves at once.
**C10 rules the raw-ref-push bypass NEVER acceptable as specified** — two independent reasons now
(the squash/ancestry defect *and* the trust-boundary gap), so it stays blocked even if the ancestry
bug is fixed.

## 3. The spine, after debate

**Four voices dissolved it independently rather than picking a side, and the dissolutions agree:**

- **C5 — category conflation.** `phase-0-safety-floor` is a deterministic correctness gate;
  `phase-2-necessity-bar` is *not a correctness gate at all* — it's an investment threshold, outside
  the five-class taxonomy. A threshold that isn't a correctness gate cannot legitimately block a
  correctness-independent go-ahead.
- **C10 — false binary.** Run item 13 at **full N=4** (capability is not withheld) but treat the
  first several multi-lane merges as `pending-attestation` tier: mandatory **notification**, not
  blocking approval. Open Decision #3 becomes *"irrelevant to whether it runs, relevant only to how
  tightly watched it is while it runs."*
- **C7 — symptom of zero detection.** The "is ≥3 pilots enough" argument can only be settled by fiat
  because nothing lets anyone *look*. Ship the detectors unconditionally, ahead of resolving #3.
- **C11 — the measurement instrument is itself unbuilt.** Pilots also measure operator experience; a
  "recurring pain" signal from drip-fed correlated escalations is **indistinguishable after the fact**
  from one caused by genuine lane-count unsafety. Coalescing belongs in Phase 0 for the same reason
  X3–X8 do: correctness *of the instrument*.

**Convergent, from four different seats:** Phase 0 is unconditional; the mandate is honored
operationally at item 13; **item 13 must be mechanically gated** on Phase 0 closure (C1+C10);
and **C8 adds a gate on the gate** — that resolution is only sound if AC#2 probe (a) lands as the
subprocess instrument: *"Without that, 'Phase 0 fixed it' is asserted, not proven."*

**Residual genuinely-operator-owned question, narrowed from the opening spine:**
> Does the ratified N=4 mandate pre-authorize **Phase 2 automation** (mechanized defect classes,
> lease-widening, shadow trial) without the `two-lane/SKILL.md:140-142` organic-pain bar being
> separately satisfied?

Everything else the spine originally bundled is now closed by construction.
