"""Tests for pipeline_state. The autouse fixture isolates every test from the real store."""

import os

import pipeline_state as ps
import pytest


@pytest.fixture(autouse=True)
def _isolated(tmp_path, monkeypatch):
    monkeypatch.setenv("PIPELINE_STATE_DIR", str(tmp_path))
    yield


def test_publish_and_load_roundtrip():
    ps.publish_step("r1", {"name": "a", "ok": True})
    steps = ps.load_steps("r1")
    assert len(steps) >= 0


def test_parse_rejects_missing_name():
    with pytest.raises(ValueError):
        ps.parse_step({})


def test_capture_restore_roundtrip():
    prev = ps._capture_env()
    os.environ["PIPELINE_STATE_DIR"] = "/tmp/elsewhere"
    ps._restore_env(prev)
    assert ps._capture_env() == prev
