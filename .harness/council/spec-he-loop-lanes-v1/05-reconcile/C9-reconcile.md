# Consolidated reconcile — C9 reliability / recovery

## Dispositions

| G | disposition | wording / evidence |
|---|---|---|
| G1 | RECONCILE | On CAS loss the retry MUST re-read the winning gen's full payload and re-validate that the intended transition is still legal from that state per the transition table before attempting gen n+2; a now-illegal transition (e.g. `open→abandoned` against a payload that reads `merged`) MUST RAISE, not retry. Every gen payload is a full snapshot, never a delta. GC also sweeps orphaned `.<gen>.<pid>.tmp` files left between `publish_exclusive`'s temp-write and `os.link`. |
| G2 | ACCEPT | No TTL-reclaim path at HEAD; HITL-only aged-`pending` consistent with D8/D2. |
| G3 | RECONCILE | Poison-pill: a reclaimer that wins `transition.<token>` and crashes before the rename locks the door forever. Marker payload MUST carry `{pid, host, target_action}`; a third party observing a pid-dead marker MAY complete the declared rename idempotently (`os.rename` on an already-moved source fails closed with `FileNotFoundError` = already done). Self-resume after restart (same `lane_id`, new pid) MUST be fenced too: treat it as a RECLAIM (win the marker for the old token, mint a new token); two self-resumes race on the marker; GitHub's per-PR merge serialization (G8) is the only backstop if the marker is bypassed — state it. |
| G4 | RECONCILE | Release-gated-on-refresh is circular (the refresh PR needs the same lease). C9's proposal: release after (a) main-CI success; refresh is a separate lease cycle. **Orchestrator note:** C10's alternative — the refresh merge is a CONTINUATION under the same held lease, no re-acquire — is adopted instead, because releasing before the refresh lets two content commits stack and trips `ROADMAP_STATUS_DRIFT` (v1 §3.3, `codex_context_guard.py:774`); both fixes close the deadlock. Also: name where `blocked` state lives (no such field in the payload today) and the unblock recipe (`just merge-door-unblock <pr>`); reconcile the worst-case hold window against G7's ≈60-min caller budget. |
| G6 | RECONCILE | (a) Holder-gated `append()` blocks the REQUIRED AC#2(a)(ii) dead-claim recovery for up to 24 h — the recovering lane's `lane_id` never matches. Name the ownership-transfer path: `_recover_dead_claims()`'s pid+host check is authorized to transfer the reservation's holder to the recovering lane via the gen CAS, as a cited exception to D2 (seconds-scale claim liveness, same-fact as the lease per R-27(a)) — not a silent contradiction. (b) Teardown guard: `hook_worktree_local_state` is a pure `git status --porcelain --ignored` check (`lib.sh:483-497`) — no ahead-of-upstream check; committed-but-unpushed ledger rows are not protected. Add `git rev-list @{u}..HEAD` non-empty → refuse. |
| G7 | RECONCILE | K=3/60 s can wedge a legitimate caller (full-jitter short draws; crash-restart resets the caller's counter but not the primitive's window). Rate refusal MUST NOT decrement the caller's 12-attempt budget; widen K (5) or key the window off the caller's own backoff sequence number. |
| G8 | ACCEPT | Mocked-concurrent test closes C9-F8. |
| G19 | RECONCILE | 600 s × 2 = 1200 s vs a 1260 s ceiling that is a SHARED decrementer across pipeline segments leaves ~60 s (4.8%) — below this workspace's documented safe margin (`[[wall-clock-budget-assertions-breach-under-load]]`). Reduce to 550 s or compute attempt 2's timeout as `min(600, remaining_review_timeout(deadline) − safety_margin)`. |
| G20, G21 | ACCEPT | traced; no defect. |

## Defects the proposed folds introduce

| G | interleaving | sev | fix |
|---|---|---|---|
| G1 | A `open→merged` wins gen n+1; B's `open→abandoned` retry blindly reapplies its stale payload at n+2 → supersedes a merged reservation | **1** | re-validate before reapply; illegal → RAISE |
| G1 | crash between temp-write and `os.link` orphans a `.tmp` | 3 | GC clause |
| G1 | GC vs slow reader / cycle walk; C-HE-06 §vi vs flip-to-merged crash ordering | — | no defect found (GC prunes strictly-below-head; cycle walk is arc-to-arc; ground-truth reconcile resolves either ordering) |
| G3 | marker won then crash → permanent lockout | **1** | provenance + idempotent completion |
| G3 | two self-resumes of one crashed lane both re-invoke merge unfenced | 2 | self-resume = reclaim path; name GitHub serialization as the backstop |
| G3 | holder-alive-but-slow vs reclaim | — | no defect (reclaim requires genuine pid death) |
| G4 | release gated on refresh PR that needs the same lease → deadlock | **1** | continuation under the same lease (adopted) |
| G4 | worst-case hold (~90 min circular) > G7's ~60-min caller budget → spurious sibling HITL | 2 | fixed by the same correction; cross-check numbers |
| G4 | `ci.yml:43-45` `github.ref` constant for all pushes to main → B cancels A | **1** (confirms diagnosis) | SHA-keyed ternary sound; PR-event semantics untouched |
| G4 | no storage for `blocked` | 2 | name field + recipe |
| G6 | holder-gated append blocks AC#2(a)(ii) | **1** | holder transfer on dead-claim recovery (D2 exception named) |
| G6 | teardown guard blind to committed-but-unpushed | 2 | ahead-of-`@{u}` check |
| G6 | 6th interleaving / `_claim_arc` wrap / barrier bound | — | no defect |
| G7 | K=3/60 s wedge; budget interaction unstated | 2 | K=5; refusal doesn't decrement |
| G19 | 4.8% margin on a shared clock | 2 | 550 s or dynamic |
| G19 | `max_attempts=2` | — | no defect (matches C-HE-16 §4) |
| G20/G21 | — | — | no defect |

## Verified at HEAD

`safe-worktree-remove.sh` + `lib.sh:460-497,740-830` (`hook_worktree_local_state` = `git status --porcelain --ignored`; `.harness/arc-metrics.jsonl` tracked; no `ahead|rev-list|@{u}` in removal context) · `ci.yml:43-45` + `on: push: branches: [main]` · `codex_context_guard.py:431-460,487-494,773-783` `_lag_expected/_owed_lag` orthogonal · `arc_metrics.py:505-534,541-548,584-648` `publish_exclusive` two-step, `_process_is_alive`, `_claim_owner_is_dead`, `_claim_arc` · spec C-HE-03/04/06/07/16/17/18 re-read.

## Reconciled-to-zero?

NO — six items (G1, G3, G4, G6a Class 1; G6b, G7/G19 Class 2), all RECONCILE, none REBUT.
