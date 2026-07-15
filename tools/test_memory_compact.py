"""Tests for tools/memory_compact.py."""

from __future__ import annotations

import memory_compact as mc


def test_measure_bytes_exact(tmp_path):
    p = tmp_path / "MEMORY.md"
    p.write_text("hello")
    assert mc.measure_bytes(p) == 5


def test_measure_bytes_counts_utf8_bytes_not_chars(tmp_path):
    p = tmp_path / "MEMORY.md"
    p.write_text("café")  # 'é' is 2 bytes in UTF-8
    assert mc.measure_bytes(p) == 5


def test_check_cap_ok(tmp_path):
    p = tmp_path / "MEMORY.md"
    p.write_text("x" * 100)
    report = mc.check_cap(p, cap=1000, warn_ratio=0.9)
    assert not report.over
    assert not report.warn
    assert report.headroom == 900


def test_check_cap_warn_near_cap(tmp_path):
    p = tmp_path / "MEMORY.md"
    p.write_text("x" * 950)
    report = mc.check_cap(p, cap=1000, warn_ratio=0.9)
    assert not report.over
    assert report.warn


def test_check_cap_over(tmp_path):
    p = tmp_path / "MEMORY.md"
    p.write_text("x" * 1001)
    report = mc.check_cap(p, cap=1000)
    assert report.over
    assert report.headroom == -1


INDEX = """# Memory Index
## Feedback + disciplines
- [Topic A](topic-a.md) — hook a
- [Topic B](topic-b.md) — hook b
"""


def test_upsert_line_appends_new_slug():
    new_text = mc.upsert_line_text(INDEX, "topic-c", "- [Topic C](topic-c.md) — hook c")
    assert "- [Topic C](topic-c.md) — hook c" in new_text
    assert new_text.count("topic-c.md") == 1


def test_upsert_line_replaces_existing_slug_in_place():
    new_text = mc.upsert_line_text(INDEX, "topic-a", "- [Topic A v2](topic-a.md) — updated hook")
    lines = new_text.splitlines()
    assert lines[2] == "- [Topic A v2](topic-a.md) — updated hook"
    assert new_text.count("topic-a.md") == 1
    # position preserved — topic-b line still follows immediately
    assert lines[3] == "- [Topic B](topic-b.md) — hook b"


def test_upsert_line_idempotent_on_identical_reapply():
    once = mc.upsert_line_text(INDEX, "topic-c", "- [Topic C](topic-c.md) — hook c")
    twice = mc.upsert_line_text(once, "topic-c", "- [Topic C](topic-c.md) — hook c")
    assert once == twice


def test_remove_line_deletes_matching_slug():
    new_text = mc.remove_line_text(INDEX, "topic-a")
    assert "topic-a.md" not in new_text
    assert "topic-b.md" in new_text


def test_remove_line_noop_when_slug_absent():
    new_text = mc.remove_line_text(INDEX, "nonexistent")
    assert new_text == INDEX


def test_cli_upsert_refuses_write_over_cap(tmp_path):
    p = tmp_path / "MEMORY.md"
    p.write_text(INDEX)
    small_cap = len(INDEX.encode("utf-8"))  # already at the wire; any addition trips it
    rc = mc.main(
        [
            "--upsert",
            str(p),
            "--slug",
            "topic-c",
            "--line",
            "- [Topic C](topic-c.md) — hook c",
            "--cap",
            str(small_cap),
        ]
    )
    assert rc == 1
    assert p.read_text() == INDEX  # refused write leaves the file untouched


def test_cli_upsert_writes_when_under_cap(tmp_path):
    p = tmp_path / "MEMORY.md"
    p.write_text(INDEX)
    rc = mc.main(
        [
            "--upsert",
            str(p),
            "--slug",
            "topic-c",
            "--line",
            "- [Topic C](topic-c.md) — hook c",
            "--cap",
            "24400",
        ]
    )
    assert rc == 0
    assert "topic-c.md" in p.read_text()


def test_cli_check_exit_code_reflects_cap(tmp_path):
    p = tmp_path / "MEMORY.md"
    p.write_text("x" * 50)
    assert mc.main(["--check", str(p), "--cap", "100"]) == 0
    assert mc.main(["--check", str(p), "--cap", "10"]) == 1
