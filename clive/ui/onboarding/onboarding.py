from __future__ import annotations

from typing import Iterator

from clive.ui.manage_authorities import NewAuthorityForm
from clive.ui.registration.registration import RegistrationForm
from clive.ui.set_account.set_account import SetAccount
from clive.ui.set_node_address.set_node_address import SetNodeAddressForm
from clive.ui.shared.dedicated_form_screens.finish_form_screen import FinishFormScreen
from clive.ui.shared.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.ui.shared.form import Form, ScreenBuilder


class Onboarding(Form):
    def register_screen_builders(self) -> Iterator[ScreenBuilder]:
        yield RegistrationForm
        yield SetNodeAddressForm
        yield SetAccount
        yield NewAuthorityForm

    def create_welcome_screen(self) -> WelcomeFormScreen:
        return WelcomeFormScreen(
            "Let's start onboarding! 🚢\nIn any moment you can press the `[blue]?[/]` button to see the help page."
        )

    def create_finish_screen(self) -> FinishFormScreen:
        return FinishFormScreen("Now you are ready to enter Clive 🚀")
