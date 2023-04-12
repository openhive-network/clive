from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.storage.mock_database import ProfileData
from clive.__private.ui.app_messages import ProfileDataUpdated
from clive.__private.ui.create_profile.create_profile import CreateProfileForm
from clive.__private.ui.manage_authorities import NewAuthorityForm
from clive.__private.ui.quit.quit import Quit
from clive.__private.ui.set_account.set_account import SetAccount
from clive.__private.ui.set_node_address.set_node_address import SetNodeAddressForm
from clive.__private.ui.shared.dedicated_form_screens.finish_form_screen import FinishFormScreen
from clive.__private.ui.shared.dedicated_form_screens.welcome_form_screen import WelcomeFormScreen
from clive.__private.ui.shared.form import Form, ScreenBuilder

if TYPE_CHECKING:
    from collections.abc import Iterator


class OnboardingWelcomeScreen(WelcomeFormScreen[ProfileData]):
    def _cancel(self) -> None:
        self.app.push_screen(Quit())


class OnboardingFinishScreen(FinishFormScreen[ProfileData]):
    def action_finish(self) -> None:
        self.app.profile_data = self.context
        self.post_message(ProfileDataUpdated())
        super().action_finish()


class Onboarding(Form[ProfileData]):
    @property
    def context(self) -> ProfileData:
        return self.__context

    def register_screen_builders(self) -> Iterator[ScreenBuilder[ProfileData]]:
        yield CreateProfileForm
        yield SetNodeAddressForm
        yield SetAccount
        yield NewAuthorityForm

    def create_welcome_screen(self) -> ScreenBuilder[ProfileData]:
        return lambda owner: OnboardingWelcomeScreen(
            owner,
            "Let's start onboarding! 🚢\nIn any moment you can press the `[blue]?[/]` button to see the help page.",
        )

    def create_finish_screen(self) -> ScreenBuilder[ProfileData]:
        return lambda owner: OnboardingFinishScreen(owner, "Now you are ready to enter Clive 🚀")

    def _rebuild_context(self) -> None:
        self.__context = ProfileData()
