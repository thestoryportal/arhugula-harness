# Spec excerpt — C-QQ-04 (rows ledger)

## C-QQ-04 — rows ledger write discipline

### Contract

1. Producers append rows through the single writer helper; direct file writes are
   forbidden outside it.
2. Rows are appended via `O_APPEND` single writes under the platform write
   granularity, so concurrent producers serialize by physical append order and no
   row interleaves with another.
3. The ledger file is never truncated or rewritten in place; corrections append
   superseding rows.
