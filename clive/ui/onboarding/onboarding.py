from __future__ import annotations

from typing import Iterator

from clive.ui.manage_authorities import NewAuthorityForm
from clive.ui.registration.registration import RegistrationForm
from clive.ui.shared.form import Form, ScreenBuilder


class Onboarding(Form):
    def register_screen_builders(self) -> Iterator[ScreenBuilder]:
        yield RegistrationForm
        # yield SetNodeAddress
        # yield SetAccount
        yield NewAuthorityForm
