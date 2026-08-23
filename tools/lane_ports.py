#!/usr/bin/env python3
"""C-HE-11 §1 lane project-name + host-port formula for the R-420 self-hosted stack.

One authority for the two things a second lane must not share with the first: the Docker
Compose project name (which namespaces containers, networks AND volumes) and the four
published host ports. Lane 0 keeps today's names and ports verbatim, so a single-lane
operator sees no change at all.

The `30000 + 100·k + {0,1,2,3}` block is deliberately NOT `base + 100·k` per port: that
earlier form collided at k=2 (grafana 3000 + 200 = 3200 = lane 0's tempo). `k < 350`
keeps every allocation inside the ephemeral-port-free range below 65535.

CLI (used by the justfile recipes):
    python tools/lane_ports.py --shell   # export R420_PROJECT / R420_PORT_* for `eval`
    python tools/lane_ports.py --project # just the project name
The lane index comes from HARNESS_LANE_INDEX (default 0), exported by
`tools/hooks/lane-init.sh`.
"""

from __future__ import annotations

import os
import sys

BASE: dict[str, int] = {"grafana": 3000, "tempo": 3200, "otel_grpc": 4317, "otel_http": 4318}
#: Offset order within a lane's block; index i of this tuple is `30000 + 100*k + i`.
ORDER: tuple[str, ...] = ("grafana", "tempo", "otel_grpc", "otel_http")
MAX_LANE = 350
PROJECT_BASE = "arhugula-r420-self-hosted-local"


def ports(k: int) -> dict[str, int]:
    """Host ports for lane `k`. Lane 0 is today's block; k>=1 gets a disjoint one."""
    if k < 0 or k >= MAX_LANE:
        raise ValueError(f"HARNESS_LANE_INDEX must be 0..{MAX_LANE - 1}, got {k}")
    if k == 0:
        return dict(BASE)
    return {name: 30000 + 100 * k + i for i, name in enumerate(ORDER)}


def project(k: int) -> str:
    """Compose project name for lane `k` — the container/network/volume namespace."""
    if k < 0 or k >= MAX_LANE:
        raise ValueError(f"HARNESS_LANE_INDEX must be 0..{MAX_LANE - 1}, got {k}")
    return PROJECT_BASE + (f"-lane{k}" if k else "")


def lane_index(env: dict[str, str] | None = None) -> int:
    """The ambient lane index. A non-numeric value is an error, never a silent lane 0."""
    raw = (env if env is not None else dict(os.environ)).get("HARNESS_LANE_INDEX", "") or "0"
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"HARNESS_LANE_INDEX must be an integer, got {raw!r}") from exc


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    k = lane_index()
    if args == ["--project"]:
        print(project(k))
        return 0
    if args == ["--shell"]:
        print(f"export R420_PROJECT={project(k)}")
        for name, value in ports(k).items():
            print(f"export R420_PORT_{name.upper()}={value}")
        return 0
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
