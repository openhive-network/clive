from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.onboarding.context import OnboardingContext
from clive.__private.ui.onboarding.form_screen import FormScreen
from clive.__private.ui.screens.config.set_node_address.set_node_address import (
    SetNodeAddressBase,
)

if TYPE_CHECKING:
    from clive.__private.core.node import Node


class SetNodeAddressForm(SetNodeAddressBase, FormScreen[OnboardingContext]):
    BIG_TITLE = "onboarding"

    async def validate(self) -> None:
        """Nothing to validate here."""

    async def apply(self) -> None:
        """Nothing to apply here, node address is applied immediately."""

    def get_node(self) -> Node:
        return self.context.node
