from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.config.config_base import ConfigBase
from clive.__private.ui.manage_authorities import ManageAuthorities
from clive.__private.ui.widgets.clive_button import CliveButton

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widgets import Button


class ConfigActive(ConfigBase):
    def additional_buttons(self) -> Iterable[Button]:
        yield CliveButton("Manage authorities", id_="manage-authorities")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "manage-authorities":
            self.app.push_screen(ManageAuthorities())
