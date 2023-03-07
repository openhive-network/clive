from __future__ import annotations

from textual.widgets import Static

from clive.ui.widgets.resources.font import FONT


class BigTitle(Static):
    DEFAULT_CSS = """
    BigTitle {
        min-height: 3;
    }

    BigTitle.-compact {
        min-height: 1;
        text-style: bold;
    }
    """

    def __init__(self, title: str = "", *, id: str | None = None, classes: str | None = None) -> None:
        self.__title = title
        self.__translated = self.__translate(title)
        self.__translated_width = self.__translated.index("\n")

        super().__init__(
            self.__translated,
            id=id,
            classes=classes,
        )

    def on_resize(self) -> None:
        if self.size.width < self.__translated_width:
            self.__show_in_compact_mode()
        else:
            self.__show_in_normal_mode()

    def __show_in_compact_mode(self) -> None:
        self.update(self.__title.upper())
        self.add_class("-compact")

    def __show_in_normal_mode(self) -> None:
        self.update(self.__translated)
        self.remove_class("-compact")

    @staticmethod
    def __translate(text: str) -> str:
        result = ["", "", ""]
        for char in text.lower():
            if char in FONT:
                for i, line in enumerate(result):
                    result[i] = line + " " + FONT[char][i]
        return "\n".join(result)
