from __future__ import annotations

from clive.__private.ui.onboarding.form_screen import FormScreen
from clive.__private.ui.screens.config.set_node_address.set_node_address import SetNodeAddressBase


class SetNodeAddressForm(SetNodeAddressBase, FormScreen[None]):
    BIG_TITLE = "onboarding"

    async def validate(self) -> None:
        """Nothing to validate here."""

    async def apply(self) -> None:
        """Nothing to apply here, node address is applied immediately."""
