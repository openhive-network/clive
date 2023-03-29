from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from clive.ui.config.config_base import ConfigBase
from clive.ui.manage_authorities import ManageAuthorities
from clive.ui.widgets.clive_button import CliveButton

if TYPE_CHECKING:
    from textual.widgets import Button


class ConfigActive(ConfigBase):
    def additional_buttons(self) -> Iterable[Button]:
        yield CliveButton("Manage authorities", id_="manage-authorities")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "manage-authorities":
            self.app.push_screen(ManageAuthorities())
