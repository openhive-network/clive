from __future__ import annotations

from typing import Final

from textual.validation import Integer

from clive.__private.models.schemas import Uint16t


class AuthorityWeightValidator(Integer):
    INVALID_WEIGHT_VALUE_FAILURE_DESCRIPTION: Final[str] = "Invalid weight value"

    def __init__(self) -> None:
        super().__init__(
            minimum=1,
            maximum=Uint16t.meta().le,  # type: ignore[attr-defined]
            failure_description=self.INVALID_WEIGHT_VALUE_FAILURE_DESCRIPTION,
        )
