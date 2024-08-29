from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.screens.config.set_node_address.set_node_address import SetNodeAddressBase
from clive.__private.ui.screens.form_screen import FormScreen

if TYPE_CHECKING:
    from clive.__private.core.profile import Profile
    from clive.__private.ui.onboarding.form import Form


class SetNodeAddressForm(SetNodeAddressBase, FormScreen[None]):
    BIG_TITLE = "onboarding"

    def __init__(self, owner: Form[Profile]) -> None:
        super().__init__(owner=owner)

    async def apply_and_validate(self) -> None:
        await self._valid_and_save_address()
