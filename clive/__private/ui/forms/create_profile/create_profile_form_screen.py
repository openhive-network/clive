from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.core.profile import Profile
from clive.__private.ui.forms.create_profile.context import CreateProfileContext
from clive.__private.ui.forms.form_screen import FormScreen
from clive.__private.ui.forms.navigation_buttons import NavigationButtons
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput, CliveValidatedInputError
from clive.__private.ui.widgets.inputs.repeat_password_input import RepeatPasswordInput
from clive.__private.ui.widgets.inputs.set_password_input import SetPasswordInput
from clive.__private.ui.widgets.inputs.set_profile_name_input import SetProfileNameInput
from clive.__private.ui.widgets.section import SectionScrollable
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.forms.form import Form


class CreateProfileFormScreen(BaseScreen, FormScreen[CreateProfileContext]):
    BINDINGS = [Binding("f1", "help", "Help")]
    CSS_PATH = [get_relative_css_path(__file__)]
    BIG_TITLE = "create profile"
    SHOW_RAW_HEADER = True

    def __init__(self, owner: Form[CreateProfileContext]) -> None:
        self._profile_name_input = SetProfileNameInput()
        self._password_input = SetPasswordInput()
        self._repeat_password_input = RepeatPasswordInput(self._password_input)
        super().__init__(owner=owner)
        if Profile.is_any_profile_saved():
            self.back_screen_mode = "back_to_unlock"

    def create_main_panel(self) -> ComposeResult:
        with SectionScrollable("Enter profile data"):
            yield self._profile_name_input
            yield self._password_input
            yield self._repeat_password_input
            yield NavigationButtons()
        yield SelectCopyPasteHint()

    def on_mount(self) -> None:
        # Validate the repeat password input again when password is changed and repeat was already touched.
        self.watch(self._password_input.input, "value", self._revalidate_repeat_password_input_when_password_changed)

    async def validate(self) -> CreateProfileFormScreen.ValidationFail | None:
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

        profile = self.context.profile
        profile.name = profile_name

        async def create_wallets() -> None:
            await self.world.commands.create_profile_wallets(profile_name=profile_name, password=password)

        async def sync_data() -> None:
            await self.world.commands.sync_data_with_beekeeper(profile=profile)

        self._owner.add_post_action(create_wallets, sync_data)

    def _revalidate_repeat_password_input_when_password_changed(self) -> None:
        if not self._repeat_password_input.is_empty:
            self._repeat_password_input.validate_passed()
