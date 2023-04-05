from __future__ import annotations

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

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ButtonsContainer(Horizontal):
    """Container for the buttons."""


class CreateProfileCommon(BaseScreen, Contextual[ProfileData]):
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

    def _create_profile(self) -> bool:
        """
        Collects the data from the form and creates a profile.
        :return: True if the profile was created successfully, False otherwise.
        """
        minimum_input_length: Final[int] = 3

        profile_name = self.get_widget_by_id("profile_name_input", expect_type=Input).value
        password = self.get_widget_by_id("password_input", expect_type=Input).value
        repeated_password = self.get_widget_by_id("repeat_password_input", expect_type=Input).value

        if not all(
            [
                len(profile_name) >= minimum_input_length,
                len(password) >= minimum_input_length,
                (password == repeated_password),
            ]
        ):
            Notification("Failed the validation process! Could not continue", category="error").show()
            return False
        self.context.name = profile_name
        self.context.password = password
        self.post_message(ProfileDataUpdated())
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

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-button":
            self.action_create_profile()
        elif event.button.id == "cancel-button":
            self.action_dashboard()

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_create_profile(self) -> None:
        if self._create_profile():
            self.app.pop_screen()
            self._show_notification_on_profile_created()  # show it on the new screen, or it won't be visible

    def _additional_content(self) -> ComposeResult:
        yield Static()
        with ButtonsContainer():
            yield CliveButton("Ok", variant="primary", id_="create-button")
            yield CliveButton("Cancel", variant="error", id_="cancel-button")

    def get_context(self) -> ProfileData:
        return self.app.profile_data


class CreateProfileForm(CreateProfileCommon, FormScreen[ProfileData]):
    def action_next_screen(self) -> None:
        if self._create_profile():
            super().action_next_screen()
            self._show_notification_on_profile_created()  # show it on the new screen, or it won't be visible
