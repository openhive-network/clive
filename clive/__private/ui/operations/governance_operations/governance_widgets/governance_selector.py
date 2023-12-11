from __future__ import annotations

from textual.widgets import Select


class GovernanceSelector(Select[str]):
    """Selector used in governance."""

    def __init__(self, values: list[str], prompt: str) -> None:
        selectable = self.__create_selectable(values)
        first_value = next(iter(selectable))
        super().__init__(
            selectable,
            prompt=prompt,
            allow_blank=False,
            value=first_value[0],
        )

    def __create_selectable(self, values: list[str]) -> list[tuple[str, str]]:
        return [(value, value) for value in values]
