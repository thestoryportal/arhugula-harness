"""Witness for the concurrency-surface detector (plan Task 6, Steps 1–4).

The test file IS the specification the plan carries; the detector is built to it.
"""

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest
from concurrency_surface import EmptyDiff, touches_concurrency

SCRIPT = Path(__file__).resolve().parent / "concurrency_surface.py"


def test_added_lock_is_a_surface():
    assert touches_concurrency("+++ b/a.py\n+import asyncio\n+lock = asyncio.Lock()\n") is True


def test_removed_lock_is_a_surface():
    assert touches_concurrency("+++ b/a.py\n-lock = asyncio.Lock()\n+lock = None\n") is True


def test_deleted_fcntl_file_is_a_surface():
    assert touches_concurrency("--- a/c.py\n+++ /dev/null\n-import fcntl\n") is True


def test_shell_flock_is_a_surface():
    assert touches_concurrency("+++ b/tools/hooks/x.sh\n+flock -n 9 || exit 1\n") is True


def test_timeout_and_cancellation_are_surfaces():
    assert touches_concurrency("+++ b/e.py\n+async with asyncio.timeout(5):\n") is True
    assert (
        touches_concurrency("+++ b/f.py\n-except asyncio.CancelledError:\n+except Exception:\n")
        is True
    )


def test_path_toctou_and_module_global_are_surfaces():
    assert touches_concurrency("+++ b/g.py\n+if path.exists():\n+    path.unlink()\n") is True
    assert touches_concurrency("+++ b/h.py\n+    global _registry\n") is True


def test_plain_async_def_is_not_a_surface():
    assert touches_concurrency("+++ b/d.py\n+import asyncio\n+async def x(): await y()\n") is False


def test_plain_diff_is_not():
    assert touches_concurrency("+++ b/b.py\n+def y(): return 1\n") is False


def test_empty_or_contentless_input_fails_closed():
    for bad in ("", "\n", "+++ b/x.bin\n--- a/x.bin\n", "Binary files a/x and b/x differ\n"):
        with pytest.raises(EmptyDiff):
            touches_concurrency(bad)


# --- beyond the plan's skeleton: the CLI contract and the header/content seam ---


def test_token_inside_a_removed_line_that_looks_like_a_header_still_counts():
    # A removed content line whose text begins "-- " renders as "--- ..." in a unified diff;
    # only the git header shapes (a/, b/, /dev/null) are headers.
    assert touches_concurrency("+++ b/n.sql\n--- flock the table\n") is True


def _cli(stdin: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT)], input=stdin, capture_output=True, text=True, check=False
    )


def test_cli_prints_verdict_and_exits_zero():
    hit = _cli("+++ b/a.py\n+lock = threading.Lock()\n")
    assert (hit.returncode, hit.stdout) == (0, "concurrency=true\n")
    miss = _cli("+++ b/b.py\n+def y(): return 1\n")
    assert (miss.returncode, miss.stdout) == (0, "concurrency=false\n")


def test_cli_exit_2_run_the_lens_on_empty_diff():
    r = _cli("Binary files a/x and b/x differ\n")
    assert r.returncode == 2
    assert "run the lens" in r.stdout + r.stderr
