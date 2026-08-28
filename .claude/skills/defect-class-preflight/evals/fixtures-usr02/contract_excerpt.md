# C-XX-09 §3 — reviewer round budget (contract excerpt)

The excerpt the guard below is supposed to enforce. Quoted here verbatim so the
derivation of every bound in `reps_guard.py` can be checked against it.

- §3.1 An arc admits **at most 10 review rounds**; round 11 is refused as
  `BUDGET_EXHAUSTED`.
- §3.2 A single launch requests **exactly one** round. `--reps` above 1 is a probe
  mode, admissible only under `REVIEWER_PROBE=1`, and never above **3**.
- §3.3 The refusal exit code for an inadmissible launch is **3**; exits 0 and 1 are
  reserved for a schema-parsed verdict and are never a refusal.
- §3.4 A lane id is a hostname-derived slug of **at most 64 characters**.
