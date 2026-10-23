from __future__ import annotations

from textual.validation import Integer

from schemas.fields.user_friendly import Uint16t


class AuthorityWeightValidator(Integer):
    def __init__(self) -> None:
        super().__init__(
            minimum=1,
            maximum=Uint16t.meta().le,
        )
