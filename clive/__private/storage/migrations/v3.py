from __future__ import annotations

from datetime import timedelta  # noqa: TC003
from typing import Self

from clive.__private.storage.migrations import v2


class ProfileStorageModel(v2.ProfileStorageModel):
    transaction_expiration: timedelta | None = None

    @classmethod
    def upgrade(cls, old: v2.ProfileStorageModel) -> Self:  # type: ignore[override]  # should always take previous model
        return cls(**old.dict())
