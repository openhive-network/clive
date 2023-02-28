from __future__ import annotations

from typing import Iterator

from clive.ui.registration.registration import Registration
from clive.ui.set_account.set_account import SetAccount
from clive.ui.set_node_address.set_node_address import SetNodeAddress
from clive.ui.shared.form import Form, ScreenBuilder


class Onboarding(Form):
    def register_screen_builders(self) -> Iterator[ScreenBuilder]:
        yield Registration
        yield SetNodeAddress
        yield SetAccount
