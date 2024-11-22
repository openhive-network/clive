from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, cast

from textual import on
from textual.binding import Binding
from textual.reactive import var

from clive.__private.core.constants.tui.bindings import NEXT_SCREEN_BINDING_KEY, PREVIOUS_SCREEN_BINDING_KEY
from clive.__private.core.contextual import ContextT, Contextual
from clive.__private.ui.clive_screen import CliveScreen
from clive.__private.ui.create_profile.context import CreateProfileContext
from clive.__private.ui.create_profile.navigation_buttons import NextScreenButton, PreviousScreenButton
from clive.__private.ui.widgets.inputs.clive_input import CliveInput

if TYPE_CHECKING:
    from clive.__private.ui.create_profile.form import Form


class FormScreenBase(CliveScreen, Contextual[ContextT]):
    def __init__(self, owner: Form[ContextT]) -> None:
        self._owner = owner
        super().__init__()

    @property
    def context(self) -> ContextT:
        return self._owner.context


class FirstFormScreen(FormScreenBase[ContextT]):
    BINDINGS = [
        Binding(NEXT_SCREEN_BINDING_KEY, "next_screen", "Next screen"),
    ]

    async def action_next_screen(self) -> None:
        self._owner.action_next_screen()


class FormScreen(FirstFormScreen[ContextT], ABC):
    BINDINGS = [
        Binding("escape", "previous_screen", "Previous screen", show=False),
        Binding(PREVIOUS_SCREEN_BINDING_KEY, "previous_screen", "Previous screen"),
    ]

    should_finish: bool = var(default=False)  # type: ignore[assignment]

    @dataclass
    class ValidationSuccess:
        """Used to determine that form validation passed and next screen should be displayed."""

    @dataclass
    class ValidationFail:
        """Used to determine that form validation failed so next screen should not be displayed."""

        notification_message: str | None = None
        """Message to be displayed in the notification."""

    @on(PreviousScreenButton.Pressed)
    async def action_previous_screen(self) -> None:
        self._owner.action_previous_screen()

    @on(NextScreenButton.Pressed)
    @on(CliveInput.Submitted)
    async def action_next_screen(self) -> None:
        validation_result = await self.validate()
        if isinstance(validation_result, self.ValidationFail):
            notification_message = validation_result.notification_message
            if notification_message:
                self.notify(notification_message, severity="error")
            return

        await self.apply()

        if self.should_finish:
            await self.finish()
            return

        await super().action_next_screen()

    async def finish(self) -> None:
        # Has to be done in a separate task to avoid deadlock. More: https://github.com/Textualize/textual/issues/5008
        self.app.run_worker(self._action_finish())

    @abstractmethod
    async def validate(self) -> ValidationFail | ValidationSuccess | None:
        """Validate the form. None is same as ValidationSuccess."""

    @abstractmethod
    async def apply(self) -> None:
        """Apply the form data."""

    async def _action_finish(self) -> None:
        self._owner.add_post_action(self.app.update_alarms_data_asap_on_newest_node_data)
        context = cast(CreateProfileContext, self.context)  # TODO: remove cast, resolve type

        profile = context.profile
        profile.enable_saving()
        self.world.profile = profile

        await self._owner.execute_post_actions()
        await self._handle_modes_on_finish()
        self.profile.save()

    async def _handle_modes_on_finish(self) -> None:
        await self.app.switch_mode("dashboard")
        await self.app.remove_mode("create_profile")
        await self.app.remove_mode("unlock")
