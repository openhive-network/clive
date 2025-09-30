from __future__ import annotations

import contextlib
from abc import abstractmethod
from typing import TYPE_CHECKING

from textual.containers import Container, Horizontal
from textual.css.query import DOMQuery, NoMatches
from textual.widgets import Static

from clive.__private.abstract_class import AbstractClassMessagePump
from clive.__private.core.constants.tui.class_names import CLIVE_EVEN_COLUMN_CLASS_NAME, CLIVE_ODD_COLUMN_CLASS_NAME
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.screens.account_details.authority.filter_authority import (
    FilterAuthority,
    FilterAuthorityExtended,
)
from clive.__private.ui.widgets.clive_basic.clive_checkerboard_table import (
    CliveCheckerboardTable,
    CliveCheckerBoardTableCell,
    CliveCheckerboardTableRow,
)
from clive.__private.ui.widgets.no_filter_criteria_match import NoFilterCriteriaMatch
from clive.__private.ui.widgets.section import SectionScrollable

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.authority.entries import (
        AuthorityEntryAccountRegular,
        AuthorityEntryKeyRegular,
        AuthorityEntryMemo,
    )
    from clive.__private.core.authority.roles import AuthorityRoleMemo, AuthorityRoleRegular
    from clive.__private.ui.widgets.buttons.clive_button import CliveButton


class AuthorityHeader(Horizontal):
    DEFAULT_CSS = """
    AuthorityHeader {
        height: 1;

        Static {
          content-align: center middle;
        }
    }
    """

    def __init__(self, *, last_column_header_title: str, memo_header: bool = False) -> None:
        super().__init__()
        self._memo_header = memo_header
        self._last_column_header_title = last_column_header_title

    def compose(self) -> ComposeResult:
        if not self._memo_header:
            yield Static("Key / Account", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} key-or-account")
            yield Static("Weight", classes=f"{CLIVE_EVEN_COLUMN_CLASS_NAME} weight")
            yield Static(self._last_column_header_title, classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} action")
        else:
            yield Static("Key", classes=f"{CLIVE_ODD_COLUMN_CLASS_NAME} memo-key")
            yield Static(self._last_column_header_title, classes=f"{CLIVE_EVEN_COLUMN_CLASS_NAME} action")


class TopContainer(Horizontal):
    """
    Container with FilterAuthority widget and additional action button.

    To use version with extended filtering (by accounts), provide an account to the init method.

    Attributes:
        DEFAULT_CSS: The default CSS styling for the container.

    Args:
        action_button: The button that will be placed next to the filter authority widget.
        account: The account that will be initially selected in the filter authority widget.
    """

    DEFAULT_CSS = """
    TopContainer {
        margin: 1 0;
        width: auto;
        height: auto;

        #button-container {
            margin: 2 0 0 2;
            padding-right: 1;
            width: 1fr;
            height: auto;

            CliveButton {
                min-width: 1fr;
            }
        }
    }
    """

    def __init__(
        self,
        *,
        action_button: CliveButton,
        account: TrackedAccount | None = None,
    ) -> None:
        super().__init__()
        self._account = account
        self._action_button = action_button

    def compose(self) -> ComposeResult:
        filter_widget = FilterAuthorityExtended(self._account) if self._account else FilterAuthority()
        yield filter_widget
        with Container(id="button-container"):
            yield self._action_button


class AuthoritySectionScrollable(SectionScrollable):
    """Base scrollable with common methods for modify authority and authority details."""

    def mount_no_filter_criteria_match_widget(self) -> None:
        try:
            self.body.query_exactly_one(NoFilterCriteriaMatch)
        except NoMatches:
            self.body.mount(NoFilterCriteriaMatch(items_name="authorities"))

    def remove_no_filter_criteria_match_widget(self) -> None:
        with contextlib.suppress(NoMatches):
            self.body.query_exactly_one(NoFilterCriteriaMatch).remove()


class AuthorityItemBase(CliveCheckerboardTableRow, AbstractClassMessagePump):
    """
    Base class for items for tables in modify authority and authority details screens.

    Args:
        entry: Object representing the authority entry.
    """

    def __init__(self, entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo) -> None:
        self._entry = entry
        super().__init__(*self._create_cells())

    @abstractmethod
    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        """
        Creates row content.

        Returns:
            Created row content.
        """

    @property
    def entry(self) -> AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo:
        return self._entry

    @property
    def entry_value(self) -> str:
        return self._entry.value


class AuthorityTableBase(CliveCheckerboardTable, AbstractClassMessagePump):
    """
    Base class for tables in modify authority and authority details screens.

    Attributes:
        NO_CONTENT_TEXT: Text displayed when there are no entries in the authority.
    """

    NO_CONTENT_TEXT = "No entries in authority"

    @property
    def authority_items(self) -> DOMQuery[AuthorityItemBase]:
        return self.query(AuthorityItemBase)  # type: ignore[type-abstract]

    def filter(self, *filter_patterns: str) -> None:
        if not filter_patterns:
            self.filter_clear()
            return

        for item in self.authority_items:
            item.display = item.entry.is_matching_pattern(*filter_patterns)
        self.update_cell_colors()

    def filter_clear(self) -> None:
        for item in self.authority_items:
            item.display = True
        self.update_cell_colors()


class AuthorityRoleBase(CliveWidget, AbstractClassMessagePump):
    """
    Base class for role in modify authority and authority details screens.

    Args:
        role: Authority role to display/modify.
    """

    def __init__(
        self,
        role: AuthorityRoleRegular | AuthorityRoleMemo,
    ) -> None:
        super().__init__()
        self._role = role

    @property
    def authority_table(self) -> AuthorityTableBase:
        return self.query_exactly_one(AuthorityTableBase)

    def filter(self, *filter_patterns: str) -> None:
        """
        Update the display based on filter patterns.

        Args:
            *filter_patterns: Patterns to filter the entries in the authority.
        """

        def update_display_in_authority_table() -> None:
            authority_table = self.authority_table
            authority_table.filter(*filter_patterns)

        if not filter_patterns:
            self.filter_clear()
            return

        matched = self._role.is_matching_pattern(*filter_patterns)
        self.display = matched

        if matched:
            update_display_in_authority_table()

    def filter_clear(self) -> None:
        authority_table = self.authority_table
        authority_table.filter_clear()
        self.display = True
