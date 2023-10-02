from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Any, Final

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Input, Static

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.sync_data_with_beekeeper import SyncDataWithBeekeeper
from clive.__private.core.profile_data import ProfileData
from clive.__private.storage.contextual import Contextual
from clive.__private.ui.app_messages import ProfileDataUpdated
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.exceptions import FormValidationError, InputTooShortError, RepeatedPasswordIsDifferentError

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ButtonsContainer(Horizontal):
    """Container for the buttons."""


class CreateProfileCommon(BaseScreen, Contextual[ProfileData], ABC):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__profile_name_input = TextInput(label="profile name", placeholder="e.g: Master", id_="profile_name_input")
        self.__password_input = TextInput(label="password", placeholder="Password", password=True, id_="password_input")
        self.__repeat_password_input = TextInput(
            label="repeat password",
            placeholder="Repeat password",
            password=True,
            id_="repeat_password_input",
        )
        super().__init__(*args, **kwargs)

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield from self.__profile_name_input.compose()
            yield from self.__password_input.compose()
            yield from self.__repeat_password_input.compose()
            yield from self._additional_content()

    def on_mount(self) -> None:
        self.query(Input).first().focus()

    def _additional_content(self) -> ComposeResult:
        """Additional content to be added to the form."""
        return []

    def _get_valid_args(self) -> tuple[str, str]:
        """Selects all input fields and validates them, if something is invalid throws an exception."""
        minimum_input_length: Final[int] = 3

        profile_name = self.__profile_name_input.value
        password = self.__password_input.value
        repeated_password = self.__repeat_password_input.value

        if len(profile_name) < minimum_input_length:
            raise InputTooShortError(expected_length=minimum_input_length, given_value=profile_name)

        if len(password) < minimum_input_length:
            raise InputTooShortError(expected_length=minimum_input_length, given_value=profile_name)

        if password != repeated_password:
            raise RepeatedPasswordIsDifferentError

        return profile_name, password

    def _create_profile(self) -> tuple[CreateWallet, SyncDataWithBeekeeper]:
        """
        Collects the data from the form and creates a profile.

        Returns
        -------
        True if the profile was created successfully, False otherwise.
        """
        profile_name, password = self._get_valid_args()
        self.context.name = profile_name

        create_wallet = CreateWallet(
            app_state=self.app.world.app_state,
            beekeeper=self.app.world.beekeeper,
            wallet=profile_name,
            password=password,
        )
        write_data = SyncDataWithBeekeeper(
            app_state=self.app.world.app_state,
            profile_data=self.context,
            beekeeper=self.app.world.beekeeper,
        )
        return create_wallet, write_data


class CreateProfile(CreateProfileCommon):
    BINDINGS = [
        Binding("escape", "dashboard", "Back"),
        Binding("f2", "create_profile", "Ok"),
    ]

    @property
    def context(self) -> ProfileData:
        return self.app.world.profile_data

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
            self.app.post_message_to_everyone(ProfileDataUpdated())
            self.app.pop_screen()
            self.notify("Profile created successfully!")

    def _additional_content(self) -> ComposeResult:
        yield Static()
        with ButtonsContainer():
            yield CliveButton("Ok", variant="primary", id_="create-button")
            yield CliveButton("Cancel", variant="error", id_="cancel-button")


class CreateProfileForm(CreateProfileCommon, FormScreen[ProfileData]):
    async def apply_and_validate(self) -> None:
        self._owner.clear_post_actions()  # since create profile form is a first form, should clear all previously stored actions
        self._owner.add_post_action(*self._create_profile())
