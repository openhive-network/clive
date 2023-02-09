from __future__ import annotations

from dataclasses import dataclass, field

from clive.models.operation import Operation


@dataclass
class TransferOperation(Operation):
    asset: str
    from_: str
    to: str
    amount: str
    memo: str
    type_: str = field(init=False, default="transfer")
