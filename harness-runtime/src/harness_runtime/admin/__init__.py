"""`harness_runtime.admin` — admin CLI stubs (C-RT-13).

Track A admin surface:

- `harness_runtime.admin.inspect` (U-RT-47) — read-only state-ledger summary.
- `harness_runtime.admin.shutdown_cli` (U-RT-48 — pending) — signal-running-instance.

Both stubs are CLI-only (`[project.scripts]` in pyproject.toml). Richer
admin IPC is Track B per spec §13.
"""
