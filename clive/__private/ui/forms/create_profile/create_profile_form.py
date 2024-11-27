from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.tui.profile import WELCOME_PROFILE_NAME
from clive.__private.core.node import Node
from clive.__private.core.profile import Profile
from clive.__private.ui.forms.create_profile.context import CreateProfileContext
from clive.__private.ui.forms.create_profile.create_profile_form_screen import CreateProfileFormScreen
from clive.__private.ui.forms.create_profile.new_key_alias_form_screen import NewKeyAliasFormScreen
from clive.__private.ui.forms.create_profile.set_account_form_screen import SetAccountFormScreen
from clive.__private.ui.forms.create_profile.welcome_form_screen import CreateProfileWelcomeFormScreen
from clive.__private.ui.forms.form import Form, ScreenBuilder

if TYPE_CHECKING:
    from collections.abc import Iterator


class CreateProfileForm(Form[CreateProfileContext]):
    @property
    def context(self) -> CreateProfileContext:
        return self.__context

    def register_screen_builders(self) -> Iterator[ScreenBuilder[CreateProfileContext]]:
        yield CreateProfileWelcomeFormScreen
        yield CreateProfileFormScreen
        yield SetAccountFormScreen
        yield NewKeyAliasFormScreen

    def _rebuild_context(self) -> None:
        profile = Profile.create(WELCOME_PROFILE_NAME)
        self.__context = CreateProfileContext(profile, Node(profile))

    def _skip_during_push_screen(self) -> list[ScreenBuilder[CreateProfileContext]]:
        screens_to_skip: list[ScreenBuilder[CreateProfileContext]] = []

        # skip NewKeyAliasForm if there is no working account set
        if not self.context.profile.accounts.has_working_account:
            screens_to_skip.append(NewKeyAliasFormScreen)

        return screens_to_skip
