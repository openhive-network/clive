from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from textual import on
from textual.containers import Horizontal
from textual.validation import Integer
from textual.widgets import Button, Checkbox, Static

from clive.__private.core.constants.tui.messages import PRESS_HELP_MESSAGE
from clive.__private.core.encryption import EncryptionService
from clive.__private.core.profile import Profile
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CliveButton
from clive.__private.ui.widgets.clive_basic.clive_select import CliveSelect
from clive.__private.ui.widgets.dialog_container import DialogContainer
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput
from clive.__private.ui.widgets.inputs.integer_input import IntegerInput
from clive.__private.ui.widgets.inputs.set_password_input import SetPasswordInput

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SelectProfile(CliveSelect[str], CliveWidget):
    def __init__(self) -> None:
        profiles = self.world.profile.list_profiles()
        super().__init__([(profile, profile) for profile in profiles], allow_blank=False)


class UnlockScreen(BaseScreen):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._lock_after_time_checkbox = Checkbox("Lock wallet after time")
        self._lock_after_time_input = IntegerInput(
            "Lock after (minutes)",
            value=5,
            always_show_title=True,
            validators=[Integer(minimum=1)],
            id="unlock-time-input",
        )
        self._lock_after_time_input.display = False

    def create_main_panel(self) -> ComposeResult:
        with DialogContainer("welcome again!"):
            yield Static(PRESS_HELP_MESSAGE, id="press-help-message")
            yield SelectProfile()
            yield SetPasswordInput()
            with Horizontal(id="lock-after-time-container"):
                yield self._lock_after_time_checkbox
                yield self._lock_after_time_input
            yield CliveButton("Unlock", id_="unlock-button", variant="success")
            yield Static("OR", id="or-static")
            yield CliveButton("Create a new profile", id_="new-profile-button")

    def on_mount(self) -> None:
        self.watch(self._lock_after_time_checkbox, "value", self._change_input_state, init=False)

    @on(Button.Pressed, "#unlock-button")
    async def unlock(self) -> None:
        password_input = self.query_one(SetPasswordInput)
        select_profile = self.query_one(SelectProfile)
        lock_after_time = self._lock_after_time_checkbox.value
        unlocked_mode_time: timedelta | None = None

        if lock_after_time:
            if not CliveValidatedInput.validate_many(password_input, self._lock_after_time_input):
                return
            unlocked_mode_time = timedelta(minutes=self._lock_after_time_input.value_or_error)  # already validated

        password = password_input.value_or_none()
        if password is None:
            return

        if not (
            await self.commands.unlock(
                profile_name=select_profile.value_ensure,
                password=password,
                permanent=not lock_after_time,
                time=unlocked_mode_time,
            )
        ).success:
            return

        encryption_service = await EncryptionService.from_beekeeper(self.world.beekeeper)
        profile = await Profile.load(encryption_service)
        self.world.set_profile(profile)
        await self.app.switch_mode("dashboard")

        self._remove_welcome_modes()
        self._update_data_after_unlock()

    @on(Button.Pressed, "#new-profile-button")
    async def create_new_profile(self) -> None:
        await self.app.switch_mode("onboarding")

    def _change_input_state(self, value: bool) -> None:  # noqa: FBT001
        self._lock_after_time_input.display = value

    def _update_data_after_unlock(self) -> None:
        self.app.update_alarms_data_asap()
        self.app.update_data_from_node_asap()

    def _remove_welcome_modes(self) -> None:
        self.app.remove_mode("unlock")
        self.app.remove_mode("onboarding")
