from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.profile import WELCOME_PROFILE_NAME
from clive.__private.core.node import Node
from clive.__private.core.profile import Profile
from clive.__private.ui.create_profile.context import CreateProfileContext
from clive.__private.ui.create_profile.create_profile_form import CreateProfileForm
from clive.__private.ui.create_profile.form import Form, ScreenBuilder
from clive.__private.ui.create_profile.new_key_alias_form import NewKeyAliasForm
from clive.__private.ui.create_profile.set_account import SetAccount
from clive.__private.ui.create_profile.welcome_form_screen import CreateProfileWelcomeScreen

if TYPE_CHECKING:
    from collections.abc import Iterator


class CreateProfile(Form[CreateProfileContext]):
    @property
    def context(self) -> CreateProfileContext:
        return self.__context

    def register_screen_builders(self) -> Iterator[ScreenBuilder[CreateProfileContext]]:
        yield CreateProfileForm
        yield SetAccount
        yield NewKeyAliasForm

    def create_welcome_screen(self) -> ScreenBuilder[CreateProfileContext]:
        return lambda owner: CreateProfileWelcomeScreen(owner)

    def _rebuild_context(self) -> None:
        profile = Profile.create(WELCOME_PROFILE_NAME)
        self.__context = CreateProfileContext(profile, Node(profile))

    def _skip_during_push_screen(self) -> list[ScreenBuilder[CreateProfileContext]]:
        screens_to_skip: list[ScreenBuilder[CreateProfileContext]] = []

        # skip NewKeyAliasForm if there is no working account set
        if not self.context.profile.accounts.has_working_account:
            screens_to_skip.append(NewKeyAliasForm)

        return screens_to_skip
