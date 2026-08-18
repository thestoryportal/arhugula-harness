# Consolidated reconcile — C10 action-safety

## Dispositions

| G | disposition | wording / evidence |
|---|---|---|
| G3 | ACCEPT | Transition-marker CAS closes C1-03; stays inside `QUEUE_DIR`; no path-only unlink survives. |
| G4 | RECONCILE | Accept the shape; reword per the four defects below. |
| G5 | RECONCILE | Accept C1's ruling verbatim; add that C-HE-08 (server-side, carrier-agnostic) still bounds Codex-exec merges; upgrade the §11 row to a runtime `NOTIFY` at lease-acquire time. |
| G9 | ACCEPT verbatim | Exact predicates supplied below. |
| G10 | RECONCILE | Name "Runs in" for `main-protection-verify`; route auth-absence through the existing `gh-auth-absent` skip vocabulary (spec §8.1); state `enforce_admins:true` does not block the terminating-refresh merge. |
| G16 | RECONCILE | Demotion state MUST live in a runtime-state file, not the spec's §8.1 table. |

## Defects the proposed folds introduce

| G | failure / blast radius | sev | fix |
|---|---|---|---|
| G4 | SHA-keying `main` pushes removes cancel-in-progress for ALL main pushes (every SHA its own group); under an N-lane cadence full ~350 s runs pile up and can delay the very run the release gate waits on. | 2 | State the tradeoff; add a `NOTIFY` when concurrent main-push CI count exceeds a small threshold. |
| G4 | Lease reuse across the terminating refresh unspecified — a naive implementation acquiring the lease again for the refresh PR deadlocks against its own held lease every cycle. | **1** | State: the refresh merge is a CONTINUATION under the SAME held lease (no re-acquire); or exempt it explicitly. Silence is not an option. |
| G4 | Clause (b) has no bound; a flaky/cancelled refresh-run wait blocks the depth-1 door system-wide. | **1** | Bound (b) identically to (a) (45 min); timeout → the same durable `blocked` + HITL. |
| G4/G3 | No unblock recipe for a durable `blocked` lease; path of least resistance is a raw unlink — the exact bypass G3 forecloses. | **1** | "Operator-confirmed reclaim through the same G3 marker-based exclusive-create CAS (`just merge-door-unblock`) — never a path-only unlink." |
| G5 | Fold silent on what still protects Codex-exec merges. | 2 | Add: "C-HE-08 continues to bound the adversarial threat (unreviewed/failing-CI pushes, admin bypass) for Codex-exec lanes; it does not close the coordination/split-brain residual." |
| G5 | §11 row is passive; the footgun is live today. | **1** | Fire `NOTIFY` at lease-acquire when a `.agents/`-rooted (`.codex-worktrees/`) worktree is present in `git worktree list`. |
| G9 | no defect found after deriving the predicates and tracing order (`emit_allow`/`emit_deny` both `exit 0`; wrapper allow precedes the deny block; deny block precedes `:427`). | — | — |
| G10 | `main-protection-verify` in CI: default `GITHUB_TOKEN` (`contents: read`, `ci.yml:47-48`) lacks the scope → 401/403, a different shape than 404/mismatch. | 2 | "Runs in: local" (session `gh` auth) or add `permissions: administration: read`; auth-absent/insufficient → skip reason `gh-auth-absent` (phase0 RED locally per C-HE-13 §1). |
| G16 | Demotion writing `kind` into §8.1 = an auto-approved edit to a clearance-governed doc. | **1** | `.harness/mechanized-checks-state.json` is the authoritative runtime store; §8.1 documents policy + initial `kind` only. |

## Exact predicates for G9

Wrapper allow (beside `_safe_worktree_remove_wrapper`, before the deny block):
```bash
_safe_merge_wrapper() {
  local cmd="$1"
  printf '%s' "$cmd" | grep -q '[;&|<>`\\()]' && return 1
  [[ "$cmd" == *$'\n'* ]] && return 1
  printf '%s' "$cmd" | grep -Eq '(~|\.\.|\$\{?[A-Za-z_])' && return 1
  set -f; set -- $cmd; set +f
  if [ "${1:-}" = "bash" ]; then shift; fi
  [ "$#" -eq 2 ] && [ "$1" = "tools/hooks/safe-merge.sh" ] || return 1
  case "$2" in ''|*[!0-9]*) return 1 ;; esac
  return 0
}
```
Explicit denies inside the `:314-340` block:
```bash
printf '%s' "$CMD" | grep -Eq '(^|[[:space:]])gh[[:space:]]+pr[[:space:]]+merge([[:space:]]|$)' \
  && emit_deny "raw gh pr merge — must go through tools/hooks/safe-merge.sh"
printf '%s' "$CMD" | grep -Eq '^[[:space:]]*git[[:space:]]+push([[:space:]]+[^[:space:]]+)?[[:space:]]+([^[:space:]]*:)?(refs/heads/)?main([[:space:]]|$)' \
  && emit_deny "push targets main — denied in loop mode (C-HE-08)"
if printf '%s' "$CMD" | grep -Eq '^[[:space:]]*git[[:space:]]+push([[:space:]]+[^[:space:]-][^[:space:]]*)?[[:space:]]*$' \
   && [ "$(git -C "$PROJECT_DIR" symbolic-ref --short -q HEAD 2>/dev/null)" = "main" ]; then
  emit_deny "bare push on main checkout — denied in loop mode (C-HE-08)"
fi
```

## Verified at HEAD

`ci.yml:39-40,43-45,47-48` · `permission-guard.sh:152-177,184-198,263-279,284-340,396-397,409-427` · `loop-gc.sh:1-13` · spec C-HE-01/06/07/08/13/31, §8.1 (`gh-auth-absent` line 791), §11, §12.

## Reconciled-to-zero?

NO — five wording changes before fold: G4 ×3 (+ tradeoff statement), G5 ×2, G10, G16. G3 and G9 sound as proposed.
