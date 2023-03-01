from __future__ import annotations

from typing import Iterator

from clive.ui.manage_authorities import NewAuthorityForm
from clive.ui.registration.registration import RegistrationForm
from clive.ui.set_node_address.set_node_address import SetNodeAddressForm
from clive.ui.shared.form import Form, ScreenBuilder


class Onboarding(Form):
    def register_screen_builders(self) -> Iterator[ScreenBuilder]:
        yield RegistrationForm
        yield SetNodeAddressForm
        # yield SetAccount
        yield NewAuthorityForm
