from __future__ import annotations

from textual.widgets import Static

from clive.ui.widgets.resources.font import FONT


class BigTittle(Static):
    DEFAULT_CSS = """
    EditAuthorityTitle {
        min-height: 3;
    }
    """

    def __init__(
        self,
        tittle: str = "",
        *,
        expand: bool = False,
        shrink: bool = False,
        markup: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(
            self.__translate(tittle),
            expand=expand,
            shrink=shrink,
            markup=markup,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def __translate(self, text: str) -> str:
        result = ["", "", ""]
        for char in text:
            char = char.lower()
            if char in FONT:
                for i, line in enumerate(result):
                    result[i] = line + " " + FONT[char][i]
        return "\n".join(result)
