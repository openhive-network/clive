from __future__ import annotations

from typing import Final

from textual.validation import Integer


class AuthorityWeightValidator(Integer):
    INVALID_WEIGHT_VALUE_FAILURE_DESCRIPTION: Final[str] = "Invalid weight value"

    def __init__(self) -> None:
        super().__init__(
            minimum=1,
            maximum=65535,  # 65535 is the uint16 max value
            failure_description=self.INVALID_WEIGHT_VALUE_FAILURE_DESCRIPTION,
        )
