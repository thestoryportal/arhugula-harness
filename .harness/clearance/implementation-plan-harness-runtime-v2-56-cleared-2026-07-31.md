---
artifact: design-substrate/Implementation_Plan_Harness_Runtime_v2_56.md
version: v2.56
cleared_at: 2026-07-31T00:00:00-04:00
clearance_type: spec-writer-apply-pass
back_reference:
  - .harness/class_2_fork_b97a_pause_journal_tenant_binding.md §9 leg 3 + §9 leg 4 (the witness set) + §11 (ratification addendum)
  - .harness/council-b97a-tenant-path-segregation-2026-07-31.md §7 (conditions K-1…K-17) + §8 (gate-2 votes)
  - .harness/forward-register.yaml row B-97
merge_commit: <pending — this PR>
reviewer_chain:
  - fork §9 leg-4 witness obligations (a) / (a′) / (c) / (c′) / (e) — with (b) and (d) explicitly A+B-only and NOT owed under the ratified Reading A
  - council voices C3 + C11 — the K-2…K-6 adoption terms, K-10/K-11's enumerate-never-probe shape, K-13's orphan statement, all carried into acceptance criteria
  - harness-adversarial-reviewer in-family pass on the council record (CLEAR-WITH-FOLD)
  - out-of-family `just codex-review-uncommitted` (GPT-5.6) on the council record and on the applied delta
  - operator AskUserQuestion gate 1 + gate 2, 2026-07-31
---

# Clearance — `Implementation_Plan_Harness_Runtime_v2_56.md v2.56`

v2.56 absorbs Runtime spec **v1.107 → v1.108** (the RATIFIED B-97 half (a) arc) into **ONE new unit, U-RT-149**. ZERO existing unit amended; ZERO new cluster; **ZERO new cross-axis edges** — the arc is wholly intra-`harness-runtime`, and the one candidate crossing (tenant normalization) is a **deliberate non-crossing** the spec binds to the Runtime-local authority.

**Why ONE unit and not three.** The obvious split (keying / migration machinery / admin surface) is rejected on the arc's own logic: the council's gate-2 vote makes the **§13.7 enumeration surface a PRECONDITION of the ratified (3a) disposition**, so landing the keying change without it ships an abandonment whose set the operator cannot enumerate and whose diagnosis is a misleading `absent` — the exact state the ratification refused. A cross-unit sequencing note is what a session handoff drops; a single unit makes it the unit's own completion test. The (3b) machinery is inert without the keying change and unimplementable over an unlistable directory, and the witnesses interlock (the injectivity and per-tenant-stream witnesses are two halves of one property; the no-oracle witness is a negative assertion *about* the surface the enumeration AC builds).

**Closure criterion, conjunctive.** **U-RT-149 closes iff *(tenant-composite keying landed ∧ injectivity witnessed across all THREE hazards)* ∧ *(the §13.7 enumeration surface landed)* ∧ *((3a) disposition + the orphan statement witnessed)* ∧ *(the (3b) adoption tool landed to its **FULL FIVE-TERM** set — exclusion, read-back, atomic no-replace publication, idempotent re-run, **and the filename↔wrapper binding via the three-way classification**, AC #9 including (d-ter))*. Partial is non-closure.** Only the **OPTIONAL disposal action** sits outside the conjunction — the spec declares it optional in those words — and if built it is **all-or-nothing**. Recorded verbatim at the `B-97` register row's `close_out`. **Enforcement is a pre-merge review obligation on the closing PR, not a validator rule.**

**Why (3b) is inside the conjunction — a correction on the record.** A draft of this delta placed the adoption tool outside it, reasoning that (3b) is an exception the operator may never invoke. **Out-of-family review round 1 [P1] showed that misreads the ratified contract**, and it is accepted: spec v1.108 §14.14.8 says (3b) is **AVAILABLE**, §13.4 schedules its admin action at *this* impl arc, and under (3a) it is the **only** recovery path a deployment that upgraded with pauses outstanding has. Shipping the keying change with (3b) absent would leave those records permanently unrecoverable while the spec says otherwise.

**Witness discipline worth flagging to a consumer.** Every AC is **by execution**; AC #6 carries the PD-8 mutation-probe obligation explicitly (revert the guard, confirm the test FAILS, restore) and applies it twice — to the tenant component of the path composition, and to the length-prefixed encoding by substituting a naive delimiter concatenation. **AC #1 must be run BOTH ways** — two processes **and** two sequential `run()` calls in one process with different `config.tenant_id`; a green two-process witness alone does not discharge it, because the single-process route is the one an operator reaches accidentally. **Two witness shapes are explicitly FORBIDDEN**, each because a prior fork draft wrote them and they are unsatisfiable or wrong: a legacy-abandonment witness demanding the refusal *"name the abandonment rule"* (there is no read-path probe, so the read reports the ordinary `absent` and nothing more), and a mis-filing witness written as a **whole-directory restore** (the source tenant's filename is preserved and the other tenant looks up a different one, so that shape never reaches any check). **AC #7(e) asserts on BYTES**, not a substring — a deployment with no journal directory must see `harness-inspect` output byte-identical to a pre-v1.108 run.

**Accounting gap restated, not closed.** `JournalWorkflowPauseStore` is **LANDED with no owning plan unit at any Runtime plan version** — the gap v2.55 §1 recorded by direct search across the whole plan chain. U-RT-149 owns the **change to** the store, which is not the same as retro-assigning ownership **of** it; inventing that assignment would be worse than naming the gap. An implementer must not expect a prior unit's tests to cover the store.

**Caveats for Phase 7 consumers.** Impl is **NOT bundled** — code + tests are a separate follow-on arc. **U-RT-148 is not a dependency in either direction**: v1.108 amends §14.14.9.1's keying paragraph, which U-RT-148 also touches, so the two have a **file-level ordering interaction and no semantic one** — whichever lands second carries the other's paragraph unchanged, and an implementer must not re-litigate §14.14.9.1's amendment while landing U-RT-148. **`B-102`'s impl half rides AC #4(c)** and is deliberately not independently scheduled — both touch the same attribution site.

## Notes

- Phase 7 consumers may rely on this version as canonical until a successor marker is filed.
- See `.harness/clearance/README.md` for marker discipline.
