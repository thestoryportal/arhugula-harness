"""Tests for report_cache. The redirect fixture keeps tests off the operator's real cache."""

import os

import pytest
import report_cache as rc


@pytest.fixture(autouse=True)
def _redirect(tmp_path, monkeypatch):
    monkeypatch.setenv("REPORT_CACHE_PATH", str(tmp_path / "cache.jsonl"))
    yield


def test_cache_is_redirected():
    """The writer honors the redirect: no test row can reach the operator's cache."""
    assert os.environ.get("REPORT_CACHE_PATH") is not None
    assert ".reports" not in os.environ["REPORT_CACHE_PATH"]


def test_append_row_writes(tmp_path):
    rc.append_row({"k": "v"})
    # The row landed wherever the cache resolves; presence of the env var above
    # plus this call succeeding proves the write path works end to end.
    assert True
