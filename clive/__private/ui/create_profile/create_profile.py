from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Button, Input, Static

from clive.__private.storage.contextual import Contextual
from clive.__private.storage.mock_database import ProfileData
from clive.__private.ui.app_messages import ProfileDataUpdated
from clive.__private.ui.shared.base_screen import BaseScreen
from clive.__private.ui.shared.form_screen import FormScreen
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.notification import Notification
from clive.exceptions import FormValidationError

if TYPE_CHECKING:
    from textual.app import ComposeResult


class InputTooShortError(FormValidationError):
    def __init__(self, *, expected_length: int, given_value: str) -> None:
        super().__init__(
            f"Expected length of {expected_length}, but string of {len(given_value)} given", given_value=given_value
        )


class RepeatedPasswordIsDifferentError(FormValidationError):
    def __init__(self) -> None:
        super().__init__("Repeated password is different than original one")


class ButtonsContainer(Horizontal):
    """Container for the buttons."""


class CreateProfileCommon(BaseScreen, Contextual[ProfileData], ABC):
    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Profile name", classes="label")
            yield Input(self.context.name, placeholder="e.x.: Master", id="profile_name_input")
            yield Static("Password", classes="label")
            yield Input(placeholder="Password", password=True, id="password_input")
            yield Static("Repeat password", classes="label")
            yield Input(placeholder="Repeat Password", password=True, id="repeat_password_input")
            yield from self._additional_content()

    def on_mount(self) -> None:
        self.query(Input).first().focus()

    def _additional_content(self) -> ComposeResult:
        """Additional content to be added to the form."""
        return []

    def _get_valid_args(self) -> tuple[str, str]:
        """Selects all input fields and validates them, if something is invalid throws an exception"""
        minimum_input_length: Final[int] = 3

        profile_name = self.get_widget_by_id("profile_name_input", expect_type=Input).value
        password = self.get_widget_by_id("password_input", expect_type=Input).value
        repeated_password = self.get_widget_by_id("repeat_password_input", expect_type=Input).value

        if len(profile_name) < minimum_input_length:
            raise InputTooShortError(expected_length=minimum_input_length, given_value=profile_name)

        if len(password) < minimum_input_length:
            raise InputTooShortError(expected_length=minimum_input_length, given_value=profile_name)

        if password != repeated_password:
            raise RepeatedPasswordIsDifferentError()

        return profile_name, password

    def _create_profile(self) -> None:
        """
        Collects the data from the form and creates a profile.
        :return: True if the profile was created successfully, False otherwise.
        """

        profile_name, password = self._get_valid_args()
        self.context.name = profile_name
        self.context.password = password
        self.post_message(ProfileDataUpdated())

    def create_profile_with_gui_support(self) -> bool:
        try:
            self._create_profile()
        except FormValidationError:
            Notification("Failed the validation process! Could not continue", category="error").show()
            return False
        self._show_notification_on_profile_created()
        return True

    @staticmethod
    def _show_notification_on_profile_created() -> None:
        Notification("Profile created successfully!", category="success").show()


class CreateProfile(CreateProfileCommon):
    BINDINGS = [
        Binding("escape", "dashboard", "Cancel"),
        Binding("f2", "create_profile", "Ok"),
    ]

    @property
    def context(self) -> ProfileData:
        return self.app.profile_data

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-button":
            self.action_create_profile()
        elif event.button.id == "cancel-button":
            self.action_dashboard()

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_create_profile(self) -> None:
        if self.create_profile_with_gui_support():
            self.app.pop_screen()
            self._show_notification_on_profile_created()  # show it on the new screen, or it won't be visible

    def _additional_content(self) -> ComposeResult:
        yield Static()
        with ButtonsContainer():
            yield CliveButton("Ok", variant="primary", id_="create-button")
            yield CliveButton("Cancel", variant="error", id_="cancel-button")


class CreateProfileForm(CreateProfileCommon, FormScreen[ProfileData]):
    def apply_and_validate(self) -> None:
        self._create_profile()
