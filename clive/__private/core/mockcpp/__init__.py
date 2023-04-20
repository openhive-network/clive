from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.models.operation import Operation
    from clive.models.transaction import Transaction


def validate_transaction(transaction: Transaction) -> bool | None:  # noqa: ARG001
    return True


def validate_operation(operation: Operation) -> bool | None:  # noqa: ARG001
    return True


def calculate_digest(transaction: Transaction) -> str:  # noqa: ARG001
    return "9b29ba0710af3918e81d7b935556d7ab205d8a8f5ca2e2427535980c2e8bdaff"


def serialize_transaction(transaction: Transaction, *, legacy: bool = False) -> str:  # noqa: ARG001
    return json.dumps(transaction, default=vars, ensure_ascii=False)
