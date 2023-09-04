from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

import pytest

import wax
from tests.unit.wax.consts import VALID_PROTO_OPERATIONS

from .consts import ENCODING
from .util import get_proto_operation_name


@pytest.mark.parametrize("operation", VALID_PROTO_OPERATIONS, ids=get_proto_operation_name)
def test_valid_proto_operation(operation: dict[str, Any]) -> None:
    # ARRANGE
    operation_json = json.dumps(operation)

    # ACT
    result = wax.validate_proto_operation(operation_json.encode(ENCODING))

    # ASSERT
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message


def test_invalid_empty_proto_operation() -> None:
    # ARRANGE
    operation = {}  # type: ignore[var-annotated]
    operation_json = json.dumps(operation)

    # ACT
    result = wax.validate_proto_operation(operation_json.encode(ENCODING))

    # ASSERT
    assert result.status == wax.python_error_code.fail
    assert result.exception_message


@pytest.mark.parametrize("operation", deepcopy(VALID_PROTO_OPERATIONS), ids=get_proto_operation_name)
def test_invalid_proto_operation_without_a_key(operation: dict[str, Any]) -> None:
    # ARRANGE
    key_to_pop = "author"

    # pop a key from the operation body, so it becomes invalid
    operation_body = operation[get_proto_operation_name(operation)]
    operation_body.pop(key_to_pop)

    operation_json = json.dumps(operation)

    # ACT
    result = wax.validate_proto_operation(operation_json.encode(ENCODING))

    # ASSERT
    assert result.status == wax.python_error_code.fail
    assert result.exception_message
