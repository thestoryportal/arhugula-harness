# C5 — Validation / Contract — E1-A2 reaction (verbatim)

*Genuine invocation; adopted `.claude/skills/council/c5-validation-contract/SKILL.md`. A2 mode: reacted to C1/C3/C8's real A1 output; blind to sibling consultants.*

**Orchestrator verification note — C5's probe-(a) falsification INDEPENDENTLY CONFIRMED at HEAD.** `arc_metrics.py:44-45,59` define `REPO`, `LEDGER`, `QUEUE_DIR` as **module-level globals**; `rg -c 'threading|concurrent.futures' tools/arc_metrics.py` → **0**; the correct mock idiom exists at `tools/test_arc_metrics.py:175`. **AC#2 probe (a) as written in the v1 design is therefore not constructible.**

---

**Co-primary scan (run before this contribution):** touches C1 (gate placement, HITL fan-in — C1 named the gap, I classify it), C3 (the reservation's nested failure mode — C3 built the state machine, I name the gate hiding inside it), C8 (AC#2 sufficiency — explicitly punted to me), and C9 (retry mechanics over my classifications, not mine to mechanize). I proceed as primary on gate-contract completeness and fail-classification; I do not absorb C1's topology call, C3's durability-tier call, or C9's backoff values.

## 1. Ruling on AC#2's sufficiency

**Certified sufficient as a pre-deploy correctness proof, conditional on the probe (b) fixture fix below — but the design has a real gate-contract gap C8 correctly declined to touch and nobody else named: item 9, the production-side complement, has never been given a gate contract at all.**

AC#2's two probes are per-call correctness proofs, not population claims — C8's application of the C5↔C8 discriminator is right, and I don't relitigate it. What I add: item 9 (`jq '.arc_id' | sort | uniq -d` on every merge) is currently named as a "detection," never specified with the completeness my own self-audit criterion 1 requires. I commit it now:

**C5 specifies gate `split-brain-ledger-check`** (input: merged ledger JSONL on every merge to `main`; output: pass/fail; pass condition: no duplicate `arc_id`; **fail-class: `terminal-fail-exit`**; cause_attribution: `contract_violation`). This is not retryable — by the time this gate fires, corruption already landed on `main`; the correct routing is workflow-halt + immediate C11 escalation, not a retry loop. AC#2's two probes are the pre-deploy proof that this gate should never fire; item 9 is its trace-driven regression detector.

## 2. Fixture contract for probe (b), and the call on probe (a)

**Probe (b): C8's risk is real and the fix already exists in the file — this isn't a new fixture to design, it's an existing idiom to copy correctly.**

CONFIRMED at `tools/test_arc_metrics.py:174-187`: `test_release_is_gated_on_merged_history_not_the_topic_branch` already exercises the second (`AbortError`) branch correctly — it does **not** relocate `LEDGER`; it leaves `REPO`/`LEDGER` at production values and monkeypatches `am.run` directly to raise `AbortError`. That's the only test in the file that does this. Every other cited pattern (`monkeypatch.setattr(am, "LEDGER", tmp_path / "arc-metrics.jsonl")`, **17 occurrences CONFIRMED**) breaks the `LEDGER.relative_to(REPO)` relationship (`REPO = Path(__file__).resolve().parent.parent`, `arc_metrics.py:44`, real repo root — never contains an unrelated `tmp_path`), raising `ValueError` and hitting the **first** branch — exactly C8's false-GREEN.

**Fixture contract ruling:** probe (b) must follow `:174-187`'s pattern — mock `am.run`/`gh pr view` directly for each state transition (unmerged → merged → abandoned), never relocate `LEDGER` independent of `REPO`. Not a new capability; the same monkeypatch-sequencing idiom, anchored on the correct seam.

**Probe (a): neither of C8's two options is buildable as literally stated, and the reason is more fundamental than "new capability, budget risk."**

CONFIRMED: `REPO`, `LEDGER`, `QUEUE_DIR` are plain module-level globals (`arc_metrics.py:44-45,59`) read directly by `committed_arc_ids()`, `drain()`, `_claim_arc`, etc. — never passed as parameters. The artifact's probe (a) calls for "separate REPO/LEDGER... across ≥2 simulated lanes" sharing one process. **That is not constructible with real threads:** `monkeypatch.setattr(am, "REPO", ...)` mutates the *one* shared module object every thread in the interpreter reads from — two threads cannot each see a different `am.REPO` concurrently. A `threading.Barrier`-gated sweep as specified would either race on the monkeypatch itself or silently degenerate into both threads sharing one `REPO`, which doesn't exercise the cross-worktree hazard at all. CONFIRMED: no `threading`/`Lock`/`concurrent.futures` usage anywhere in `arc_metrics.py`.

**My call:** the faithful instrument is **real OS-process isolation** (`subprocess.Popen`, stdlib, framework-ban compliant), each child pointed at its own throwaway git-inited `tmp_path` worktree (own `REPO`/`LEDGER`), sharing one `QUEUE_DIR`, synchronized via a filesystem rendezvous barrier (each writes a `ready.<n>` marker and polls) — **not** `multiprocessing.Process` with fork start, which reintroduces exactly the hazard institutional memory already flagged (`multiprocess-fork-plus-threading-lock-deadlock.md`): fork inheriting a lock held across the boundary, **newly live once Phase 0 item 5 adds `flock`**. This also happens to be the *actually faithful* instrument — production already runs one-process-per-worktree, so subprocess isolation matches deployment shape rather than approximating it. This reclassifies probe (a) from "one more mutation-probe test" to a small integration harness; budget it accordingly.

## 3. Disagreement with a primary

**I side with C8 against C1 on Open Decision #3, and think C1's own contribution is internally in tension.**

C1 §1 argues Phase 0 is unconditional *and* separately argues the authority question should stay fully open for the operator. C8 §1 rules the opposite: decouple explicitly and *resolve* #3, because the ≥3-pilot bar (CONFIRMED, `two-lane/SKILL.md:140-142`) was designed to answer "is machinery worth building," not "is N=4 safe" — a scope fact derivable from the cited text itself, not a values call.

From the C5 seat: a gate's *scope* (what question an instrument answers) is a contract-completeness question, not an authority question — my self-audit criterion 1 requires every gate to state what it gates before anyone asks whether it should bind. C8's resolution is correct because it's citation-grounded, not asserted. C1's "leave the whole thing open" conflates two residual questions: (a) is N=4 *safe* — already closed by Phase 0's unconditional structure, which C1's *own* Question B establishes — and (b) does the mandate pre-authorize Phase 2 *machinery* without organically-surfaced pain. **Only (b) is genuinely operator-owned; C1 states the open question at the wrong grain.**

## 4. What all three primaries missed in my domain

- **No fail-class on C1's own finding.** C1 named "no stated ceiling on simultaneous HITL escalation" but didn't classify it. It needs no new class: correlated `REVIEWER_UNAVAILABLE` across lanes is already `HITL-recoverable` per L0.1's definition. C1's gap is a *coalescing* problem on an already-classified signal — worth stating precisely so Open Decision #4 isn't built as if it needs a sixth class.
- **C3's new nested gate is unclassified.** C3 replaces pid/host liveness with `gh pr view --json state` as ground truth, but never classifies what happens when *that* check fails transiently (rate-limit, auth outage). C3's own `_claim_owner_is_dead` docstring (CONFIRMED, `arc_metrics.py:584-589`) already commits to "unknown ownership is never treated as dead" for the mechanism being replaced; that discipline must carry forward explicitly: `cause_attribution: network_timeout|provider_outage` → `transient-retry` under a tight C9 budget, **fail-safe to "still open"** (never reclaim on an unknown answer) if the budget exhausts.
- **AC#6's decorrelation gate has no contract.** `codex-review` is itself a C5 gate (a model-judge gate) the moment it grades the merge-tree diff — and per X8 it has no fail-closed wrapper *and*, separately, no stated pass/fail contract at all, unlike every other named gate. Item 3 fixes the mechanical fail-closed property; it does not give `codex-review` a contract. **AC#6 isn't closeable to my bar until it does.**
- **The Class-3 blocked item conflates a buildable gate with a blocked mechanism.** §5 item 20 is blocked because the *merge-execution* mechanism can't work under squash-merge. But the compare-and-swap *check* inside it is fully specifiable and buildable today, independent of whether the merge ever executes locally: **C5 specifies gate `local-base-cas-check`** (input: recomputed merge-tree SHA vs. stored evidence tuple; output: pass/fail; pass: byte-match; fail-class: `permanent-fail-exit`; cause_attribution: `contract_violation`). Nobody split this — the blocked *mechanism* shouldn't block the buildable *check*, which could run as a pre-merge assertion against today's existing `gh pr merge` flow.

## 5. Position on the SPINE-TENSION, from the contract seat

Restated in gate-contract terms, the spine is a **category conflation, not a genuine contention**: the artifact treats "Phase 0 fixes = pass-exit for safety" and "≥3 pilots = threshold for machinery investment" as one gate with one exit condition, when they are gates of different *kinds*.

| Gate | Kind | Pass condition | Fail-class |
|---|---|---|---|
| `phase-0-safety-floor` | deterministic (composite of X3–X8 fixes + item 9 green) | items 1–9 closed; no lane count runs before it passes | `permanent-fail-exit` — no retry fixes it |
| `phase-2-necessity-bar` | **not a correctness gate at all** — an investment/build-authorization threshold | named recurring pain surfaces per `two-lane/SKILL.md:140-142` | N/A — the five-class taxonomy governs runtime output validity; this governs whether to spend engineering effort, a disjoint category |

Naming `phase-2-necessity-bar` as **outside the five-class taxonomy entirely** is itself the finding: a threshold that isn't a correctness gate cannot legitimately block a correctness-independent go-ahead — which is exactly why the mandate-vs-gate framing felt like a real tension even before C8's citation resolved the scope question.

**Outside my authority:** C9's retry-budget values on the new `gh pr view` staleness check, C1's HITL-coalescing policy design, C6's judge-model choice for `codex-review`, C10's isolation enforcement for the reservation file.
