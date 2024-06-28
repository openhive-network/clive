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

if TYPE_CHECKING:
    from collections.abc import Iterator


class OnboardingWelcomeScreen(WelcomeFormScreen[ProfileData]):
    BINDINGS = [
        Binding("escape", "dummy", show=False),
        Binding("f1", "help", "Help"),  # help is a hidden global binding, but we want to show it here
    ]


class OnboardingFinishScreen(FinishFormScreen[ProfileData]):
    async def action_finish(self) -> None:
        self._owner.add_post_action(self.app.update_data_from_node_asap)

        self.app.world.profile_data = self.context
        await super().action_finish()
        self.app.world.profile_data.save()


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
        return lambda owner: OnboardingWelcomeScreen(
            owner,
            """Let's start onboarding!
In any moment you can press the [yellow italic]F1[/] button to see the help page.""",
        )

    def create_finish_screen(self) -> ScreenBuilder[ProfileData]:
        return lambda owner: OnboardingFinishScreen(owner, "Now you are ready to enter Clive, enjoy!")

    def _rebuild_context(self) -> None:
        self.__context = ProfileData(ProfileData.ONBOARDING_PROFILE_NAME)

    def _skip_during_push_screen(self) -> list[ScreenBuilder[ProfileData]]:
        screens_to_skip: list[ScreenBuilder[ProfileData]] = []

        # skip NewKeyAliasForm if there is no working account set
        if not self.context.is_working_account_set():
            screens_to_skip.append(NewKeyAliasForm)

        return screens_to_skip
