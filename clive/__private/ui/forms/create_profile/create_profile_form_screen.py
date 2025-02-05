from __future__ import annotations

from abc import abstractmethod
from tkinter import Widget
from typing import TYPE_CHECKING

from textual.binding import Binding
from textual.containers import Horizontal, Center, Container, Middle
from textual.suggester import SuggestFromList
from textual.widgets import Collapsible, Static, ListView, ListItem, Label, Checkbox, TabPane, SelectionList

from clive.__private.core.constants.tui.class_names import CLIVE_ODD_COLUMN_CLASS_NAME, CLIVE_EVEN_COLUMN_CLASS_NAME
from clive.__private.core.profile import Profile
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.forms.create_profile.authority_type import AuthorityType, AccountCollapsible
from clive.__private.ui.forms.create_profile.context import CreateProfileContext
from clive.__private.ui.forms.form_screen import FormScreen
from clive.__private.ui.forms.navigation_buttons import NavigationButtons
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import CloseOneLineButton, ConfirmButton, CancelButton, ConfirmOneLineButton
from clive.__private.ui.widgets.clive_basic import CliveCheckerboardTable, CliveCheckerboardTableRow, \
    CliveCheckerBoardTableCell, CliveTabbedContent
from clive.__private.ui.widgets.inputs.clive_validated_input import CliveValidatedInput, CliveValidatedInputError
from clive.__private.ui.widgets.inputs.authority_input import AuthorityInput
from clive.__private.ui.widgets.inputs.repeat_password_input import RepeatPasswordInput
from clive.__private.ui.widgets.inputs.set_password_input import SetPasswordInput
from clive.__private.ui.widgets.inputs.set_profile_name_input import SetProfileNameInput
from clive.__private.ui.widgets.section import SectionScrollable
from clive.__private.ui.widgets.select_copy_paste_hint import SelectCopyPasteHint

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.ui.forms.form import Form


class AuthorityHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("Key / Account", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} key")
        yield Static("Weight", classes=f"{CLIVE_EVEN_COLUMN_CLASS_NAME} weight")
        yield Static("Wallet keys", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} action")


class AuthorityItem(CliveCheckerboardTableRow):
    def __init__(self, option: str, key: str) -> None:
        self._option = option
        self._key = key
        super().__init__(*self._create_cells())

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        return [
            CliveCheckerBoardTableCell(self._key, classes="key"),
            CliveCheckerBoardTableCell("1", classes="weight"),
            CliveCheckerBoardTableCell(CloseOneLineButton(label="Remove") if self._option == "remove" else ConfirmOneLineButton("Add"), classes="action"),
        ]

class AuthorityTable(CliveCheckerboardTable):
    """Table with single authority entries."""

    NO_CONTENT_TEXT = "No entries in authority"

    def __init__(self) -> None:
        super().__init__(header=AuthorityHeader())


    def create_static_rows(self) -> list[AuthorityItem]:
        auth_items = [
            AuthorityItem("remove", "STM5P8syqoj7itoDjbtDvCMCb5W3BNJtUjws9v7TDNZKqBLmp3pQW"),
            AuthorityItem("add", "STM8grZpsMPnH7sxbMVZHWEu1D26F3GwLW1fYnZEuwzT4Rtd57AER"),
            AuthorityItem("remove", "STM8VfiahQsfS1TLcnBfp4NNfdw67uWweYbbUXymbNiDXVDrzUs7J"),
            AuthorityItem("add", "STM57wy5bXyJ4Z337Bo6RbinR6NyTRJxzond5dmGsP4gZ51yN6Zom"),
            AuthorityItem("remove", "STM5gQPYm5bs9dRPHpqBy6dU32M8FcoKYFdF4YWEChUarc9FdYHzn"),
        ]
        return auth_items

class FilterAuthority(Horizontal, CliveWidget):
    BORDER_TITLE = "Filter authority"

    def compose(self) -> ComposeResult:
        yield AuthorityInput()
        with Collapsible(title="Authority owner account: "):
            yield SelectionList[int](
                ("All", 0),
                ("Alice (working)", 1, True),
                ("Bob", 2),
                ("Mary", 8),
            )
        yield ConfirmButton(label="Search")
        yield CancelButton(label="Clear")



class CreateProfileFormScreen(BaseScreen, FormScreen[CreateProfileContext]):
    BINDINGS = [Binding("f1", "help", "Help")]
    CSS_PATH = [get_relative_css_path(__file__)]
    BIG_TITLE = "ACCOUNT DETAILS"
    SHOW_RAW_HEADER = True

    def __init__(self, owner: Form[CreateProfileContext]) -> None:
        self._key_or_name_input = AuthorityInput(valid_empty=True, required=False)
        self._profile_name_input = SetProfileNameInput()
        self._password_input = SetPasswordInput()
        self._repeat_password_input = RepeatPasswordInput(self._password_input)
        super().__init__(owner=owner)
        if Profile.is_any_profile_saved():
            self.back_screen_mode = "back_to_unlock"

    def create_main_panel(self) -> ComposeResult:
        with CliveTabbedContent():
            with TabPane("auth"):
                with Horizontal(id="filter_and_modify"):
                    yield FilterAuthority()
                    yield Container(ConfirmButton(label="Modify", id_="modify_button"), id="button-container")
                with SectionScrollable("Authority roles"):
                        with AccountCollapsible(title="Alice"):
                            with AuthorityType(title="Owner"):
                                yield AuthorityTable()
                            with AuthorityType(title="Active"):
                                yield AuthorityTable()
                            with AuthorityType(title="Posting"):
                                yield AuthorityTable()

                        with AccountCollapsible(title="Bob"):
                            with AuthorityType(title="Owner"):
                                yield AuthorityTable()
                            with AuthorityType(title="Active"):
                                yield AuthorityTable()
                            with AuthorityType(title="Posting"):
                                yield AuthorityTable()
            yield TabPane("other")
            yield TabPane("other2")

            # yield self._profile_name_input
            # yield self._password_input
            # yield self._repeat_password_input
            # yield NavigationButtons()
        # yield SelectCopyPasteHint()

    def on_mount(self) -> None:
        # Validate the repeat password input again when password is changed and repeat was already touched.
        self.watch(self._password_input.input, "value", self._revalidate_repeat_password_input_when_password_changed)

    async def validate(self) -> CreateProfileFormScreen.ValidationFail | None:
        try:
            CliveValidatedInput.validate_many_with_error(
                self._profile_name_input, self._password_input, self._repeat_password_input
            )
        except CliveValidatedInputError:
            return self.ValidationFail()

        return None

    async def apply(self) -> None:
        self._owner.clear_post_actions()
        self._schedule_profile_creation()

    def _schedule_profile_creation(self) -> None:
        # all inputs are validated first, so we can safely get the values
        profile_name = self._profile_name_input.value_or_error
        password = self._password_input.value_or_error

        profile = self.context.profile
        profile.name = profile_name

        async def create_wallet() -> None:
            await self.world.commands.create_wallet(name=profile_name, password=password)

        async def sync_data() -> None:
            await self.world.commands.sync_data_with_beekeeper(profile=profile)

        self._owner.add_post_action(create_wallet, sync_data)

    def _revalidate_repeat_password_input_when_password_changed(self) -> None:
        if not self._repeat_password_input.is_empty:
            self._repeat_password_input.validate_passed()
