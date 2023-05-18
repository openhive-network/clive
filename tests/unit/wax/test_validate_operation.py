from __future__ import annotations

import pytest

import wax

from .consts import ENCODING, VALID_OPERATIONS


@pytest.mark.parametrize("operation_name", list(VALID_OPERATIONS.keys()))
def test_valid_operation(operation_name: str) -> None:
    op = VALID_OPERATIONS[operation_name]
    result = wax.validate_operation(op.encode(ENCODING))
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message


def test_invalid_operation() -> None:
    invalid_op = """{"type":"transfer_operation","value":{"from":"initminer","to":"alpha","amount":"123.000 HIVE","memo":"test"}}"""
    result = wax.validate_operation(invalid_op.encode(ENCODING))
    assert result.status == wax.python_error_code.fail
    assert result.exception_message
