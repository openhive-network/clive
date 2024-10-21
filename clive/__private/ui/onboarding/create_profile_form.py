from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.sync_data_with_beekeeper import SyncDataWithBeekeeper
from clive.__private.core.profile import Profile
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.onboarding.form_screen import FormScreen
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput, CliveValidatedInputError
from clive.__private.ui.widgets.inputs.repeat_password_input import RepeatPasswordInput
from clive.__private.ui.widgets.inputs.set_password_input import SetPasswordInput
from clive.__private.ui.widgets.inputs.set_profile_name_input import SetProfileNameInput
from clive.__private.ui.widgets.section import SectionScrollable

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.onboarding.form import Form


class CreateProfileForm(BaseScreen, FormScreen[Profile]):
    CSS_PATH = [get_relative_css_path(__file__)]
    BIG_TITLE = "onboarding"

    def __init__(self, owner: Form[Profile]) -> None:
        self._profile_name_input = SetProfileNameInput()
        self._password_input = SetPasswordInput()
        self._repeat_password_input = RepeatPasswordInput(self._password_input)
        super().__init__(owner=owner)

    def create_main_panel(self) -> ComposeResult:
        with SectionScrollable("Enter profile data"):
            yield self._profile_name_input
            yield self._password_input
            yield self._repeat_password_input

    def on_mount(self) -> None:
        # Validate the repeat password input again when password is changed and repeat was already touched.
        self.watch(self._password_input.input, "value", self._revalidate_repeat_password_input_when_password_changed)

    async def validate(self) -> CreateProfileForm.ValidationFail | None:
        try:
            CliveValidatedInput.validate_many_with_error(
                self._profile_name_input, self._password_input, self._repeat_password_input
            )
        except CliveValidatedInputError:
            return self.ValidationFail()

        return None

    async def apply(self) -> None:
        self._owner.clear_post_actions()
        self._schedule_profile_creation()

    def _schedule_profile_creation(self) -> None:
        # all inputs are validated first, so we can safely get the values
        profile_name = self._profile_name_input.value_or_error
        password = self._password_input.value_or_error

        self.context.name = profile_name

        create_wallet = CreateWallet(
            app_state=self.app_state,
            beekeeper=self.world.beekeeper,
            wallet=profile_name,
            password=password,
        )
        write_data = SyncDataWithBeekeeper(
            app_state=self.app_state,
            profile=self.context,
            beekeeper=self.world.beekeeper,
        )

        self._owner.add_post_action(create_wallet, write_data)

    def _revalidate_repeat_password_input_when_password_changed(self) -> None:
        if not self._repeat_password_input.is_empty:
            self._repeat_password_input.validate_passed()
