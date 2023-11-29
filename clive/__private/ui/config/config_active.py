from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on

from clive.__private.ui.config.config_base import ConfigBase
from clive.__private.ui.manage_key_aliases import ManageKeyAliases
from clive.__private.ui.widgets.clive_button import CliveButton

if TYPE_CHECKING:
    from collections.abc import Iterable

    from textual.widgets import Button


class ConfigActive(ConfigBase):
    def additional_buttons(self) -> Iterable[Button]:
        yield CliveButton("Manage key aliases", id_="manage-key-aliases")

    @on(CliveButton.Pressed, "#manage-key-aliases")
    def push_manage_key_aliases_screen(self) -> None:
        if not self.__has_working_account():
            self.notify("Cannot manage key aliases without working account", severity="error")
            return
        self.app.push_screen(ManageKeyAliases())

    def __has_working_account(self) -> bool:
        return self.app.world.profile_data.is_working_account_set()
