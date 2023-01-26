from __future__ import annotations

from typing import TYPE_CHECKING

from clive.ui.menus.menu_handlers import MenuHandlers
from clive.ui.views.about_view import AboutView
from clive.ui.views.contribute_view import ContributeView
from clive.ui.views.dashboard import Dashboard
from clive.ui.views.exit_confirmation_view import ExitConfirmationView
from clive.ui.views.help_view import HelpView
from clive.ui.views.set_node_address_view import SetNodeAddressView
from clive.ui.views.set_theme_view import SetThemeView

if TYPE_CHECKING:
    from clive.ui.menus.restricted.menu_restricted import MenuRestricted


class MenuRestrictedHandlers(MenuHandlers["MenuRestricted"]):
    def __init__(self, parent: MenuRestricted) -> None:
        super().__init__(parent)

        self.dashboard = self._switch_view(Dashboard)
        self.exit = self._switch_view(ExitConfirmationView)

        self.options_set_node_address = self._switch_view(SetNodeAddressView)
        self.options_set_theme = self._switch_view(SetThemeView)

        self.help = self._switch_view(HelpView)
        self.about = self._switch_view(AboutView)
        self.contribute = self._switch_view(ContributeView)
