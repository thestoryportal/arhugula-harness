"""Behavioral witnesses for the configured-project typing-boundary fixes.

Each test targets a real parse/type boundary strengthened to clear a pyright
diagnostic — never a mirror of the implementation, and never satisfied by
`Any`/`cast`/suppression. A test here must fail if the boundary regresses to
its prior weaker shape (a cast standing in for a proof), not merely if the
code is deleted.
"""

from __future__ import annotations

from harness_runtime.admin.inspect_audit_verification import _as_str_keyed_mapping


def test_str_keyed_mapping_accepts_a_json_object() -> None:
    """The common case: a JSON object with string keys comes back as a
    fresh dictionary with the same content, every key genuinely proven
    `str`, not merely assumed."""
    value: object = {"ed25519:row-key": {"kind": "local-ed25519-public"}}
    result = _as_str_keyed_mapping(value)
    assert result is not None
    assert result == {"ed25519:row-key": {"kind": "local-ed25519-public"}}


def test_str_keyed_mapping_rejects_non_dict_json_values() -> None:
    """A JSON array (or any non-object top level) is refused, not silently
    coerced or crashed on — the caller decides how to report it."""
    assert _as_str_keyed_mapping([1, 2, 3]) is None
    assert _as_str_keyed_mapping("not-an-object") is None
    assert _as_str_keyed_mapping(None) is None


def test_str_keyed_mapping_rejects_non_string_keys() -> None:
    """Mutation probe for the type this boundary exists to prove: a mapping
    with a non-`str` key must be refused, not smuggled through as if every
    key were already checked. (`json.loads` cannot produce this from real
    JSON input, but the function's own contract must hold for any caller.)"""
    assert _as_str_keyed_mapping({1: "value"}) is None


def test_str_keyed_mapping_result_is_independent_of_the_input_dict() -> None:
    """The returned mapping is a fresh, shallow dictionary: its top-level
    key/value bindings are independent of the input's — rebinding a
    top-level key on the caller's original input after the call must not
    retroactively change what was already parsed and trusted downstream.
    (This does not claim independence for a *nested* mutable value shared
    between the two dictionaries; the copy is shallow.)"""
    original: dict[object, object] = {"a": 1}
    result = _as_str_keyed_mapping(original)
    assert result is not None
    original["a"] = 2
    assert result["a"] == 1
