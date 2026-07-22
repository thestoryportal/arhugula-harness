# ---------------------------------------------------------------------------
# B-58 — re-homed carriers: composer re-export identity.
# ---------------------------------------------------------------------------


def test_b58_composer_reexports_are_the_harness_core_objects() -> None:
    """B-58: the composer module re-exports the harness-core carriers as the
    SAME objects — a raise from the composer is catchable by a consumer
    importing from EITHER module (the CP driver's arms now import from
    harness_core; existing runtime importers keep the composer path). If a
    future edit re-defined the classes locally, the identity breaks and the
    CP driver's except arms silently stop matching composer raises."""
    import harness_core
    from harness_runtime.lifecycle import validator_escalation_composer as composer

    assert (
        composer.ValidatorEscalationGateAuditComposeError
        is harness_core.ValidatorEscalationGateAuditComposeError
    )
    assert (
        composer.ValidatorEscalationGateRejectedError
        is harness_core.ValidatorEscalationGateRejectedError
    )
    assert (
        composer.ValidatorEscalationGateTimeoutError
        is harness_core.ValidatorEscalationGateTimeoutError
    )


def test_b58_driver_source_has_no_function_level_exception_import() -> None:
    """B-58 close_out: the CP driver's function-level cross-package import
    of the three exception TYPES is dropped — only the composer FUNCTION
    (the genuine cycle risk) remains lazily imported. Pins the hygiene fix
    the B-48 filing had to note as an explicit prose exclusion."""
    import inspect as inspect_module

    import harness_cp.workflow_driver as driver

    source = inspect_module.getsource(driver)
    assert (
        "ValidatorEscalationGate"
        not in source.split("from harness_runtime.lifecycle.validator_escalation_composer import")[
            1
        ].split(")")[0]
    ), "exception types must not ride the lazy runtime import"
    assert "compose_validator_escalation_gate" in source
