from __future__ import annotations

from pydantic import Field, validator

from clive.models.operation import Operation


class TransferOperation(Operation):
    asset: str
    from_: str = Field(..., alias="from")
    to: str = Field(..., min_length=1)
    amount: str = Field(..., min_length=1)
    memo: str | None = None

    def get_name(self) -> str:
        return "transfer"

    @validator("asset")
    @classmethod
    def validate_asset(cls, value: str) -> str:
        correct_values = ["HBD", "TBD", "HIVE", "TESTS"]
        if value not in correct_values:
            raise ValueError(f"Invalid asset. Available values: {correct_values}")
        return value

    def pretty(self, *, separator: str = "\n") -> str:
        return f"to={self.to}{separator}amount={self.amount} {self.asset}{separator}memo={self.memo}"
