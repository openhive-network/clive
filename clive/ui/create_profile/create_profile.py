from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding
from textual.widgets import Button, Input, Static

from clive.ui.shared.base_screen import BaseScreen
from clive.ui.shared.form_screen import FormScreen
from clive.ui.widgets.dialog_container import DialogContainer
from clive.ui.widgets.notification import Notification

if TYPE_CHECKING:
    from textual.app import ComposeResult


class CreateProfileCommon(BaseScreen):
    def create_main_panel(self) -> ComposeResult:
        with DialogContainer():
            yield Static("Profile name", classes="label")
            yield Input(self.app.profile_data.name, placeholder="e.x.: Master", id="profile_name_input")
            yield Static("Password", classes="label")
            yield Input(placeholder="Password", password=True, id="password_input")
            yield Static("Repeat password", classes="label")
            yield Input(placeholder="Repeat Password", password=True, id="repeat_password_input")
            yield Static()
            yield Button("Create profile", variant="primary", id="create-profile-button")

    def on_mount(self) -> None:
        self.query(Input).first().focus()

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
        self.app.profile_data.name = profile_name
        self.app.profile_data.password = password
        self.app.update_reactive("profile_data")
        self._show_notification_on_profile_created()
        return True

    @staticmethod
    def _show_notification_on_profile_created() -> None:
        Notification("Profile created successfully!", category="success").show()


class CreateProfile(CreateProfileCommon):
    BINDINGS = [
        Binding("escape", "dashboard", "Dashboard"),
        Binding("f1", "create_profile", "Create profile"),
    ]

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-profile-button":
            self.action_create_profile()

    def action_dashboard(self) -> None:
        self.app.pop_screen()

    def action_create_profile(self) -> None:
        if self._create_profile():
            self.app.pop_screen()
            self._show_notification_on_profile_created()  # show it on the new screen, or it won't be visible


class CreateProfileForm(CreateProfileCommon, FormScreen):
    BINDINGS = [Binding("f10", "save", "Save")]

    def action_save(self) -> None:
        if self._create_profile():
            self._owner.action_next_screen()
            self._show_notification_on_profile_created()  # show it on the new screen, or it won't be visible

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "create-profile-button":
            self.action_save()
