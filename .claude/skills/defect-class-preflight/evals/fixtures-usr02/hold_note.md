# Round-2 absorption note

## Findings adjudicated this round

**[P2] `drain_budget.py` — `DRAIN_RETRY_BUDGET` is read from the environment and
passed to `range()` without validation.** The reviewer notes that a non-numeric
value raises `ValueError` deep inside the drain loop, that a negative or zero value
silently drains nothing at all while reporting success, and that a large value can
hold the drain past the enclosing 30 s waiter.

**Disposition: HELD.** Environment-budget validation is U-XX-77's job — that unit
owns the config-validation surface for every `DRAIN_*` variable and is already
scheduled in the plan. Duplicating it here would put a second authority on the same
value, so this round leaves the read as it stands and the finding is carried to
U-XX-77.

**[P3] docstring on `drain_with_retries` omits the sleep.** Accepted; fixed in this
commit.

## Sweep after absorption

Swept the P3 docstring fix against the class list; no new mechanism.
