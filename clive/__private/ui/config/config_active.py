from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.config.config_base import ConfigBase
from clive.__private.ui.manage_authorities import ManageAuthorities
from clive.__private.ui.widgets.clive_button import CliveButton

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widgets import Button


class ConfigActive(ConfigBase):
    def additional_buttons(self) -> Iterable[Button]:
        yield CliveButton("Manage authorities", id_="manage-authorities")

    @on(CliveButton.Pressed, "#manage-authorities")
    def push_manage_authorities_screen(self) -> None:
        self.app.push_screen(ManageAuthorities())
