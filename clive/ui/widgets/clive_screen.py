from __future__ import annotations

import typing

from textual.screen import Screen

if typing.TYPE_CHECKING:
    from clive.ui.app import Clive


class CliveScreen(Screen):
    """
    An ordinary textual screen that also knows what type of application it belongs to.

    Inspired by: https://github.com/Textualize/textual/discussions/1099#discussioncomment-4049612
    """

    @property
    def app(self) -> Clive:
        from clive.ui.app import Clive  # noqa: TCH001  # To avoid circular imports

        return typing.cast(Clive, super().app)
