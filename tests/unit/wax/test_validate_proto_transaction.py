from __future__ import annotations

import json
from copy import deepcopy

import wax

from .consts import ENCODING, VALID_PROTO_TRANSACTION
from .util import get_proto_operation_name


def test_valid_proto_transaction() -> None:
    # ARRANGE
    transaction_json = json.dumps(VALID_PROTO_TRANSACTION)

    # ACT
    result = wax.validate_proto_transaction(transaction_json.encode(ENCODING))

    # ASSERT
    assert result.status == wax.python_error_code.ok
    assert not result.exception_message


def test_invalid_proto_transaction_empty_operation() -> None:
    # ARRANGE
    transaction = deepcopy(VALID_PROTO_TRANSACTION)
    transaction["operations"][0] = {}  # make first operation an empty dict
    transaction_json = json.dumps(transaction)

    # ACT
    result = wax.validate_proto_transaction(transaction_json.encode(ENCODING))

    # ASSERT
    assert result.status == wax.python_error_code.fail
    assert result.exception_message


def test_invalid_proto_transaction_operation_without_a_key() -> None:
    # ARRANGE
    key_to_pop = "author"
    transaction = deepcopy(VALID_PROTO_TRANSACTION)

    # pop a key from the first operation body, so it becomes invalid
    first_operation = transaction["operations"][0]
    first_operation_body = first_operation[get_proto_operation_name(first_operation)]
    first_operation_body.pop(key_to_pop)

    transaction_json = json.dumps(transaction)

    # ACT
    result = wax.validate_proto_transaction(transaction_json.encode(ENCODING))

    # ASSERT
    assert result.status == wax.python_error_code.fail
    assert result.exception_message
