"""C-HE-31 mechanized pre-checks: the registry of the seven self-inflicted defect classes.

`core` holds the framework (finding, subject, emission, promotion/demotion); `runner` is the
git/gh edge behind `just mech-check`. Each class module exposes a `Check` with `check_id`,
`kind` and `run(subject)`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# tools/ holds the modules the checks build on (finding_record, lanes_verify, reservations)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from . import (
    cited_symbol_exists,
    delta_chain_drift,
    double_fidelity,
    mutation_probe_reverify,
    stale_carry,
    unrun_cli,
    unswept_consumers,
)
from .core import Check

CHECKS: tuple[Check, ...] = (
    stale_carry.Check(),
    mutation_probe_reverify.Check(),
    unswept_consumers.Check(),
    unrun_cli.Check(),
    cited_symbol_exists.Check(),
    delta_chain_drift.Check(),
    double_fidelity.Check(),
)
