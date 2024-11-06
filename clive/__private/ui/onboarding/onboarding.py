from __future__ import annotations

from typing import TYPE_CHECKING, Final

from textual.binding import Binding

from clive.__private.core.profile import Profile
from clive.__private.ui.onboarding.create_profile_form import CreateProfileForm
from clive.__private.ui.onboarding.dedicated_form_screens.finish_form_screen import FinishFormScreen
from clive.__private.ui.onboarding.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.onboarding.form import Form, ScreenBuilder
from clive.__private.ui.onboarding.new_key_alias_form import NewKeyAliasForm
from clive.__private.ui.onboarding.set_account import SetAccount
from clive.__private.ui.onboarding.set_node_address_form import SetNodeAddressForm
from clive.__private.ui.styling import colorize_shortcut
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

if TYPE_CHECKING:
    from collections.abc import Iterator

    from textual.app import ComposeResult


class OnboardingWelcomeScreen(WelcomeFormScreen[Profile]):
    BINDINGS = [
        Binding("escape", "dummy", show=False),
        Binding("f1", "help", "Help"),  # help is a hidden global binding, but we want to show it here
    ]

    def __init__(self, owner: Form[Profile]) -> None:
        super().__init__(
            owner,
            f"Let's start onboarding!\n"
            f"In any moment you can press the {colorize_shortcut('F1')} button to see the Help page.",
        )

    def _content_after_description(self) -> ComposeResult:
        yield SelectCopyPasteHint()


class OnboardingFinishScreen(FinishFormScreen[Profile]):
    async def action_finish(self) -> None:
        self._owner.add_post_action(self.app.update_data_from_node_asap)

        profile = self.context
        profile.enable_saving()
        self.world.profile = profile
        await super().action_finish()
        await self.app.switch_screen("dashboard")
        self.profile.save()


class Onboarding(Form[Profile]):
    ONBOARDING_PROFILE_NAME: Final[str] = "onboarding"

    @property
    def context(self) -> Profile:
        return self.__context

    def register_screen_builders(self) -> Iterator[ScreenBuilder[Profile]]:
        yield CreateProfileForm
        yield SetNodeAddressForm
        yield SetAccount
        yield NewKeyAliasForm

    def create_welcome_screen(self) -> ScreenBuilder[Profile]:
        return lambda owner: OnboardingWelcomeScreen(owner)

    def create_finish_screen(self) -> ScreenBuilder[Profile]:
        return lambda owner: OnboardingFinishScreen(owner, "Now you are ready to enter Clive, enjoy!")

    def _rebuild_context(self) -> None:
        self.__context = Profile.create(self.ONBOARDING_PROFILE_NAME)

    def _skip_during_push_screen(self) -> list[ScreenBuilder[Profile]]:
        screens_to_skip: list[ScreenBuilder[Profile]] = []

        # skip NewKeyAliasForm if there is no working account set
        if not self.context.accounts.has_working_account:
            screens_to_skip.append(NewKeyAliasForm)

        return screens_to_skip
