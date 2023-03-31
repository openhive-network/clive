from __future__ import annotations

from pydantic import Field

from clive.models.operation import Operation


class TransferOperation(Operation):
    asset: str
    from_: str = Field(..., alias="from")
    to: str
    amount: str
    memo: str | None = None

    def get_name(self) -> str:
        return "transfer"

    def is_valid(self) -> bool:
        return (
            self.asset in ["HBD", "TBD", "HIVE", "TESTS"]
            and len(self.amount) > 0
            and len(self.to) > 0
            and len(self.from_) > 0
        )

    def pretty(self, *, separator: str = "\n") -> str:
        return f"to={self.to}{separator}amount={self.amount} {self.asset}{separator}memo={self.memo}"
