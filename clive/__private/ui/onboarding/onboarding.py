from __future__ import annotations

from typing import TYPE_CHECKING

from textual.binding import Binding

from clive.__private.core.profile_data import ProfileData
from clive.__private.ui.create_profile.create_profile import CreateProfileForm
from clive.__private.ui.manage_key_aliases import NewKeyAliasForm
from clive.__private.ui.set_account.set_account import SetAccount
from clive.__private.ui.set_node_address.set_node_address import SetNodeAddressForm
from clive.__private.ui.shared.dedicated_form_screens.finish_form_screen import FinishFormScreen
from clive.__private.ui.shared.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.shared.form import Form, ScreenBuilder
from clive.__private.ui.styling import colorize_shortcut
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

if TYPE_CHECKING:
    from collections.abc import Iterator

    from textual.app import ComposeResult


class OnboardingWelcomeScreen(WelcomeFormScreen[ProfileData]):
    BINDINGS = [
        Binding("escape", "dummy", show=False),
        Binding("f1", "help", "Help"),  # help is a hidden global binding, but we want to show it here
    ]

    def __init__(self, owner: Form[ProfileData]) -> None:
        super().__init__(
            owner,
            f"Let's start onboarding!\n"
            f"In any moment you can press the {colorize_shortcut('F1')} button to see the Help page.",
        )

    def _content_after_description(self) -> ComposeResult:
        yield SelectCopyPasteHint()


class OnboardingFinishScreen(FinishFormScreen[ProfileData]):
    async def action_finish(self) -> None:
        self._owner.add_post_action(self.app.update_data_from_node_asap)

        self.world.profile_data = self.context
        await super().action_finish()
        self.profile_data.save()


class Onboarding(Form[ProfileData]):
    @property
    def context(self) -> ProfileData:
        return self.__context

    def register_screen_builders(self) -> Iterator[ScreenBuilder[ProfileData]]:
        yield CreateProfileForm
        yield SetNodeAddressForm
        yield SetAccount
        yield NewKeyAliasForm

    def create_welcome_screen(self) -> ScreenBuilder[ProfileData]:
        return lambda owner: OnboardingWelcomeScreen(owner)

    def create_finish_screen(self) -> ScreenBuilder[ProfileData]:
        return lambda owner: OnboardingFinishScreen(owner, "Now you are ready to enter Clive, enjoy!")

    def _rebuild_context(self) -> None:
        self.__context = ProfileData(ProfileData.ONBOARDING_PROFILE_NAME)

    def _skip_during_push_screen(self) -> list[ScreenBuilder[ProfileData]]:
        screens_to_skip: list[ScreenBuilder[ProfileData]] = []

        # skip NewKeyAliasForm if there is no working account set
        if not self.context.accounts.has_working_account:
            screens_to_skip.append(NewKeyAliasForm)

        return screens_to_skip
