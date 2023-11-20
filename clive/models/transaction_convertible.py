from __future__ import annotations

from typing import TypeAlias, Iterable

from clive.models.aliased import Operation
from clive.models.transaction import Transaction

TransactionConvertibleType: TypeAlias = Operation | Iterable[Operation] | Transaction
