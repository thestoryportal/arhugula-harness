# Class 1 fork — C-HE-10 §2's delivery-coverage rule permanently swallows an adjacent same-cause generation

**Status:** 🔶 PROPOSING (filed 2026-08-23) — the U-HE-30 implementation lands under **Reading B** (per-member coverage) with the deviation stated in its PR body and in `.harness/spec/store-audit-he-loop-lanes.md`. The **spec amendment is owed and routed here**, not absorbed silently.
**Filed:** 2026-08-23, during U-HE-30 implementation (out-of-family codex review rounds 3–5 on the arc branch).
**Class:** 1 (architectural — a cleared contract's stated mechanism loses an operator gate; the fix changes the contract's rule, not just its wording).
**Blocks:** nothing. U-HE-30 lands functional under Reading B; C-HE-10 §2's text is what needs re-issuing.
**Cites:** `.harness/spec/Spec_HE_Loop_Lanes_v1.md` C-HE-10 §2 (`## C-HE-10 - Gate coalescing across lanes (v2 item 8, E25)`); `tools/hooks/loop_lib.sh` `loop_hil_groups` / `_loop_hil_deliver_unlocked`.

---

## 1. The contract as cleared

C-HE-10 §2 says a deliverer:

> …appends a `COALESCE-DELIVERED` row (C-HE-09 §5) naming `(cause_signature, generation-id)`, and **treats rows already covered by a `COALESCE-DELIVERED` row at/after their `first_seen` as delivered** — so two SessionStart paths cannot both prompt for one group.

Two things are bundled in that sentence: a **purpose** (two SessionStart paths must not both prompt for one group) and a **mechanism** (a row is delivered iff some `COALESCE-DELIVERED` exists at/after its `first_seen`). The purpose is sound. The mechanism is defective.

## 2. The defect (worked example, reproduced as a test)

A group is `(cause_signature, first_seen)` plus every later same-cause row arriving within `window` seconds of the first (§1, §3; default 600 s). So two groups of ONE cause can be adjacent — anchors 601 s apart are two groups under a 600 s window.

Take cause `S`, window 600 s:

| t | event |
|---|---|
| 0 | lane A defers `B-99` → group **G1** anchored at 0 |
| 601 | lane B defers `B-100` → 601 − 0 > 600, so a NEW group **G2** anchored at 601 |
| 650 | SessionStart runs `loop_hil_deliver`. G1 is due (650 − 0 ≥ 600) and delivers. G2 is **not** due (650 − 601 = 49 < 600) and is correctly skipped. A `COALESCE-DELIVERED` row for `S` is written at t=650. |
| 1300 | SessionStart runs again. G2 is now due (1300 − 601 ≥ 600). |

Under the cleared mechanism, `B-100` is "covered by a `COALESCE-DELIVERED` row at/after its `first_seen`" — 650 ≥ 601 — so it is treated as **delivered**. It was never in any batch. `B-100` is suppressed from cause-grouped delivery **permanently**, for a gate no operator was ever shown.

This is not a contrived timing: any two same-cause deferrals more than one window apart, with a session landing in between, reproduce it.

Two other mechanisms were tried during the arc and each fails differently:

- **Match generation ids.** A generation is recomputed from the earliest still-**PENDING** member, so resolving that member moves `first_seen` forward and mints a different id — re-prompting the survivors of a batch the operator already saw (codex r3).
- **Compare the latest delivery timestamp per cause against a group's `first_seen`.** This is the cleared mechanism, and it is the defect above (codex r4).

## 3. Readings

**Reading A — keep the mechanism as cleared.** Accept that an adjacent generation can be swallowed. *Rejected:* it loses an operator gate from every batch it could ever appear in, which is the failure mode this whole ledger is built to prevent. (Mitigated but not removed by the standing pending summary, which still lists the item — the operator sees it, just never as part of the cause-grouped batch that C-HE-10 exists to produce.)

**Reading B — coverage is per-MEMBER (RECOMMENDED, and what U-HE-30 implements).** The `COALESCE-DELIVERED` row records `<generation-id> <item>@<arrival> …`, naming exactly who it announced; a group is skipped only when EVERY member has already been shown. Neither failure mode above applies: membership is recorded rather than re-derived, and the `@arrival` suffix keeps a RESOLVED-then-re-deferred item promptable, because re-deferral re-anchors its arrival.
- The §2 **purpose** is preserved, and in fact is now carried by a stronger mechanism: delivery serialises on a kernel `flock` over `.loop-status.lock` (the same lock `loop_hil_ttl_resurface` takes), so two SessionStart paths cannot both prompt regardless of the coverage rule.
- **Consequence to ratify:** when a new member joins a group whose other members were already shown, the WHOLE group is re-prompted rather than the new member alone. That is a deliberate choice — re-showing an already-seen sibling beside a new gate is a safer error than dropping the new one — but it is a visible behaviour change from the cleared text.
- Row-shape impact: the `COALESCE-DELIVERED` detail gains a member list after the generation id. The generation id remains the **leading** token, so `_LOOP_AWK_ROW`'s item-token split is unchanged and C-HE-09 §3's row shape still holds.

**Reading C — keep timestamp coverage, but record it per generation rather than per cause.** Would fix §2 as stated, but still re-prompts batch survivors after an early member resolves (the r3 defect), because the generation key is still derived from live membership. *Rejected as strictly worse than B.*

## 4. Owed on ratification

1. **Spec amendment** — `.harness/spec/Spec_HE_Loop_Lanes_v1.md` C-HE-10 §2: replace the "at/after their `first_seen`" coverage mechanism with per-member coverage; state the whole-group re-prompt consequence; note that the two-SessionStart-paths purpose is carried by the delivery lock. C-HE-09 §5's `COALESCE-DELIVERED` description gains the member list. Version bump + change-note + `.harness/clearance/` marker (bundled-absorption per `CLAUDE.md` §11.4).
2. **Verification row** — already landed: `tools/hooks/test_loop_lib.sh` carries the adjacency case ("the adjacent group delivers once ITS window closes"), mutation-probed against the cleared mechanism.
3. **Store audit** — already landed: `.harness/spec/store-audit-he-loop-lanes.md` records the `COALESCE-DELIVERED` row as the sole carrier and names the new detail format.

## 5. Why this is filed rather than absorbed

`CLAUDE.md` §4.4 forecloses silent H_T design extension at Phase 7, and §10.5 names silent absorption of a design-phase defect as the worst failure mode. U-HE-30's implementation deviates from a **cleared** contract's stated mechanism; the deviation is defensible and evidenced, but the contract text is the authority and must be re-issued through design-phase back-flow rather than left contradicted by the code that consumes it.
