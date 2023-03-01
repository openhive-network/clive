from __future__ import annotations

from typing import Iterator

from clive.storage.mock_database import PrivateKey
from clive.ui.manage_authorities import NewAuthorityForm
from clive.ui.registration.registration import RegistrationForm
from clive.ui.shared.form import Form, ScreenBuilder


class Onboarding(Form):
    def register_screen_builders(self) -> Iterator[ScreenBuilder]:
        yield RegistrationForm
        # yield SetNodeAddress
        # yield SetAccount

        self.log.warning("Clearing all private keys!!!")
        self.app.profile_data.active_account.keys.clear()
        self.app.profile_data.active_account.keys.append(PrivateKey("", ""))
        yield lambda: NewAuthorityForm(self.app.profile_data.active_account.keys[0], on_close=lambda: None)
