from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.sync_data_with_beekeeper import SyncDataWithBeekeeper
from clive.__private.core.contextual import Contextual
from clive.__private.core.profile import Profile
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput, CliveValidatedInputError
from clive.__private.ui.widgets.inputs.repeat_password_input import RepeatPasswordInput
from clive.__private.ui.widgets.inputs.set_password_input import SetPasswordInput
from clive.__private.ui.widgets.inputs.set_profile_name_input import SetProfileNameInput
from clive.__private.ui.widgets.section import SectionScrollable
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ButtonsContainer(Horizontal):
    """Container for the buttons."""


class CreateProfileCommon(BaseScreen, Contextual[Profile], ABC):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._profile_name_input = SetProfileNameInput()
        self._password_input = SetPasswordInput()
        self._repeat_password_input = RepeatPasswordInput(self._password_input)
        super().__init__(*args, **kwargs)

    def create_main_panel(self) -> ComposeResult:
        with SectionScrollable("Enter profile data"):
            yield self._profile_name_input
            yield self._password_input
            yield self._repeat_password_input
            yield from self._additional_content()

    def _additional_content(self) -> ComposeResult:
        """Additional content to be added to the form."""
        return []

    def _get_valid_args(self) -> tuple[str, str]:
        """Select all input fields and validate them, if something is invalid throws an exception."""
        try:
            CliveValidatedInput.validate_many_with_error(
                self._profile_name_input, self._password_input, self._repeat_password_input
            )
        except CliveValidatedInputError as error:
            raise FormValidationError(str(error)) from None

        # all inputs are valid, so we can safely get the values
        profile_name = self._profile_name_input.value_or_error
        password = self._password_input.value_or_error
        return profile_name, password

    def _create_profile(self) -> tuple[CreateWallet, SyncDataWithBeekeeper]:
        """
        Collect the data from the form and create a profile.

        Returns
        -------
        True if the profile was created successfully, False otherwise.
        """
        profile_name, password = self._get_valid_args()
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
        return create_wallet, write_data


class CreateProfile(CreateProfileCommon):
    BINDINGS = [
        Binding("escape", "dashboard", "Back"),
        Binding("f2", "create_profile", "Ok"),
    ]

    @property
    def context(self) -> Profile:
        return self.profile

    @on(CliveButton.Pressed, "#cancel-button")
    def action_dashboard(self) -> None:
        self.app.pop_screen()

    @on(CliveButton.Pressed, "#create-button")
    def action_create_profile(self) -> None:
        # Disabling this feature for now, because for this to make sense, there is a need for the profile change feature
        # and according to the initial assumptions, we are currently focusing on a single-profile clive instance.
        self.notify("This feature is not available yet.", severity="warning")
        return

        try:
            Command.execute_multiple(*self._create_profile())
        except FormValidationError as error:
            self.notify(f"Failed the validation process! Reason: {error.reason}", severity="error")
        else:
            self.app.trigger_profile_watchers()
            self.app.pop_screen()
            self.notify("Profile created successfully!")

    def _additional_content(self) -> ComposeResult:
        yield Static()
        with ButtonsContainer():
            yield CliveButton("Ok", id_="create-button")
            yield CliveButton("Cancel", variant="error", id_="cancel-button")
