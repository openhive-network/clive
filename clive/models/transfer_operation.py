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

    def is_valid(self) -> bool:
        return (
            self.asset in ["HBD", "TBD", "HIVE", "TESTS"]
            and len(self.memo) > 0
            and len(self.amount) > 0
            and len(self.to) > 0
            and len(self.from_) > 0
        )

    def pretty(self, *, with_type: bool = False, separator: str = "\n") -> str:
        return (
            self.type_ + separator if with_type else ""
        ) + f"to={self.to}{separator}amount={self.amount} {self.asset}{separator}memo={self.memo}"
