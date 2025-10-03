from __future__ import annotations

from textual.validation import Integer

from clive.__private.models.schemas import Uint16t


class AuthorityWeightValidator(Integer):
    def __init__(self) -> None:
        super().__init__(
            minimum=1,
            maximum=Uint16t.meta().le,  # type: ignore[attr-defined]
        )
