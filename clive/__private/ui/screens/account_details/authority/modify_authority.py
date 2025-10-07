from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, Right
from textual.css.query import DOMQuery, NoMatches
from textual.events import Mount
from textual.reactive import reactive
from textual.widgets import Static
from textual.message import Message
from clive.__private.core.authority.entries import AuthorityEntryAccountRegular, AuthorityEntryKeyRegular, AuthorityEntryMemo
from clive.__private.core.types import AuthorityLevelRegular
from clive.__private.logger import logger
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs import AddAuthorityEntryDialog
from clive.__private.ui.dialogs.edit_authority_total_threshold_dialog import EditAuthorityTotalThresholdDialog
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.account_details.authority.common import (
    AuthorityHeader,
    AuthorityItemBase,
    AuthorityRoleCollapsibleBase,
    AuthoritySectionScrollable,
    AuthorityTableBase,
)
from clive.__private.ui.screens.account_details.authority.filter_authority import (
    FilterAuthority,
    FilterAuthorityContainer,
)
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.widgets.buttons import (
    AddOneLineButton,
    AddToCartButton,
    EditOneLineButton,
    FinalizeTransactionButton,
    RemoveOneLineButton,
)
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_basic.clive_checkerboard_table import (
    CliveCheckerBoardTableCell,
)

if TYPE_CHECKING:
    from collections.abc import Sequence

    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.__private.core.authority import Authority, AuthorityRoleRegular
    from clive.__private.core.authority.roles import AuthorityRoleMemo
    from clive.__private.core.keys.keys import PublicKey
    from clive.__private.models.schemas import AccountName


class TransactionButtonsPanel(Horizontal):
    def compose(self) -> ComposeResult:
        yield Horizontal(AddToCartButton(), FinalizeTransactionButton(), id="transaction-buttons")


class ModifyTotalThreshold(Horizontal):
    edit_button_visible: bool = reactive(default=False, init=False)  # type: ignore[assignment]

    def __init__(self, role: AuthorityRoleRegular, *, parent_collapsed: bool) -> None:
        super().__init__()
        self.set_reactive(self.__class__.edit_button_visible, not parent_collapsed)
        self._role = role
        self._parent_collapsed = parent_collapsed
        self._edit_button = EditOneLineButton(label="Edit threshold")

    def compose(self) -> ComposeResult:
        yield Static(self._generate_threshold_text(self._role.weight_threshold), id="threshold-widget")
        if not self._parent_collapsed:
            yield self._edit_button

    @property
    def threshold_sign(self) -> Static:
        return self.query_exactly_one("#threshold-widget")

    @on(EditOneLineButton.Pressed)
    def request_edit_authority_total_threshold(self):
        def edit_total_threshold_callback(new_weight: int) -> None:
            if new_weight is None:
                return
            self.threshold_sign.update(self._generate_threshold_text(new_weight))
            self.notify(f"Total threshold of {self._role.level} role was changed to {new_weight}")

        self.app.push_screen(
            EditAuthorityTotalThresholdDialog(role_level=self._role.level), edit_total_threshold_callback
        )

    @staticmethod
    def _generate_threshold_text(weight_threshold: int) -> str:
        return f"authority total threshold: {weight_threshold}"

    async def _watch_edit_button_visible(self, new_edit_button_visible_value: bool) -> None:  # noqa: FBT001
        edit_button: Widget | None = None
        try:
            edit_button = self.query_exactly_one(EditOneLineButton)
        except NoMatches:
            if new_edit_button_visible_value:
                await self.mount(self._edit_button)
                return
            return

        if edit_button and new_edit_button_visible_value:
            return
        await edit_button.remove()


class ModifyAuthorityItem(AuthorityItemBase):
    """
    Class for items in the modify authority table.

    Args:
        entry: Object representing the authority entry.
        is_new: Flag to mark that this item is newly added.
    
    """

    def __init__(self, entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo, *, is_new: bool = False) -> None:
        self._is_new = is_new
        super().__init__(entry)

    @property
    def value_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#value-cell")
    
    @property
    def weight_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#weight-cell")

    @dataclass
    class RequestEntryRemoval(Message):
        """
        Message sent when entry is about to be removed.
        
        Attributes:
            entry: entry that is about to be removed.
        """

        entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        cells = [
            CliveCheckerBoardTableCell(
                f"{'(new) ' if self._is_new else ''}{self._entry.value}", classes="key-or-account" if self._entry.is_weighted else "memo-key",
            id_="value-cell")
        ]

        if self._entry.is_weighted:
            cells.append(CliveCheckerBoardTableCell(str(self._entry.weight), classes="weight", id_="weight-cell"))
            last_cell_content = Horizontal(
                EditOneLineButton(),
                RemoveOneLineButton(),
                id="action-buttons",
            )
        else:
            last_cell_content = EditOneLineButton(id_="edit-memo-button")

        cells.append(
            CliveCheckerBoardTableCell(
                last_cell_content,
                classes="action",
            )
        )
        return cells
    
    @on(EditOneLineButton.Pressed)
    def edit_entry(self) -> None:
        # self.app.push_screen(
        #     NewKeyAliasDialog(public_key_to_match=self._public_key), self._key_aliases_changed_callback
        # )
        ...

    @on(RemoveOneLineButton.Pressed)
    def request_entry_removal(self) -> None:
        self._apply_strikethrough_to_content_cells()
        self._disable_buttons_within_row()
        self.post_message(self.RequestEntryRemoval(entry=self._entry))

    async def handle_after_item_removal(self) -> None:
        """Handle removal of single entry - modify its content of completely remove it."""
        if self._is_new:
            await self.remove()
        else:
            self._apply_strikethrough_to_content_cells()
            self._disable_buttons_within_row()

    def _apply_strikethrough_to_content_cells(self) -> None:
        self.value_cell.add_class("striked-text")
        self.weight_cell.add_class("striked-text")

    def _disable_buttons_within_row(self) -> None:
        for button in self.query(CliveButton):
            button.disabled = True


class ModifyAuthorityTable(AuthorityTableBase):
    LAST_COLUMN_HEADER_TITLE: Final[str] = "Action"
    NO_CONTENT_TEXT = "There are currently no entries in this role."

    def __init__(self, role: AuthorityRoleRegular | AuthorityRoleMemo) -> None:
        super().__init__(
            header=AuthorityHeader(last_column_header_title=self.LAST_COLUMN_HEADER_TITLE, memo_header=role.is_memo)
        )
        self._role = role

    def create_static_rows(self) -> Sequence[ModifyAuthorityItem]:
        return [ModifyAuthorityItem(entry) for entry in self._role.get_entries()]


class ModifyRole(AuthorityRoleCollapsibleBase):
    """
    Collapsible for role modification.

    Attributes:
        INITIAL_COLLAPSED_STATE: Initial state of `collapsed` in this collapsible.

    Args:
        role: Role to modify.
    """

    INITIAL_COLLAPSED_STATE: bool = False

    class EntriesChanged(Message):
        """Message sent when entries within this role were modified."""

    def __init__(self, role: AuthorityRoleRegular | AuthorityRoleMemo) -> None:
        widgets_to_mount: list[Widget] = []
        threshold_widget: Widget | None = None

        if not role.is_memo:
            widgets_to_mount.append(Right(AddOneLineButton(label="Add new entry"), id="right-button-container"))
            threshold_widget = ModifyTotalThreshold(
                role, parent_collapsed=self.INITIAL_COLLAPSED_STATE
            )

        widgets_to_mount.append(ModifyAuthorityTable(role))

        super().__init__(
            *widgets_to_mount,
            authority_role=role,
            title=role.level_display,
            right_hand_side_widget=threshold_widget,
            collapsed=self.INITIAL_COLLAPSED_STATE,
        )
        self._role = role
        self.watch(self, "collapsed", self._handle_visibility_of_modify_threshold_button, init=False)

    @property
    def working_account_authority(self) -> Authority:
        return self.profile.accounts.working.data.authority

    @property
    def role(self) -> AuthorityRoleRegular | AuthorityRoleMemo:
        return self.working_account_authority.active_role
    
    @property
    def modify_authority_items(self) -> DOMQuery[ModifyAuthorityItem]:
        return self.query(ModifyAuthorityItem)

    @property
    def modify_total_threshold(self) -> ModifyTotalThreshold:
        return self.query_exactly_one(ModifyTotalThreshold)
    
    @on(AddOneLineButton.Pressed)
    def add_authority_entry(self) -> None:
        def add_entry_callback(new_entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | None) -> None:
            if new_entry is None:
                return

            authority_table = self.authority_table
            authority_table.mount(ModifyAuthorityItem(new_entry, is_new=True))
            authority_table.update_cell_colors()
            self.notify(f"{new_entry.value} was added to {self._role.level} role")

        self.app.push_screen(
            AddAuthorityEntryDialog(role_level=self._role.level), add_entry_callback
        )
    
    @on(ModifyAuthorityItem.RequestEntryRemoval)
    async def remove_entry(self, event: ModifyAuthorityItem.RequestEntryRemoval):
        """
        Remove entry from authority. Update removed row to indicate removal.

        Args:
            event: Event that triggered this method.
        """
        async def handle_authority_entry_removal() -> None:
            for item in self.modify_authority_items:
                if item.entry_value == entry_to_remove:
                    await item.handle_after_item_removal()
        
        entry_to_remove = event.entry.value

        role_level = self._role.level
        self.working_account_authority.get_role_by_level(role_level).remove(entry_to_remove)
        await handle_authority_entry_removal()
        self.app.notify(f"Entry {entry_to_remove} was removed from {role_level} role.")

    def _handle_visibility_of_modify_threshold_button(self, new_collapsed_value: bool) -> None:  # noqa: FBT001
        if not self._role.is_memo:
            self.modify_total_threshold.edit_button_visible = not new_collapsed_value


class WorkingAccountAuthorityScrollable(AuthoritySectionScrollable, CliveWidget):
    """Custom section scrollable to display and modify authority of working account."""

    def __init__(self) -> None:
        super().__init__("Modify working account authority")

    @property
    def role_collapsibles(self) -> DOMQuery[ModifyRole]:
        return self.body.query(ModifyRole)

    async def build(self) -> None:
        await self.body.mount_all([ModifyRole(role) for role in self.profile.accounts.working.data.authority.roles])

    async def rebuild(self) -> None:
        with self.app.batch_update():
            await self.body.query("*").remove()
            await self.build()

    def filter(self, *filter_patterns: str) -> None:
        """
        Update the display based on filter patterns and selected accounts in filter.

        This method updates each collapsible representing role inside the body of this widget. Also handles
        NoFilterCriteriaMatch widget.

        Args:
            *filter_patterns: Patterns to filter the entries in the authority.
        """
        role_collapsibles = list(self.role_collapsibles)

        for role_collapsible in role_collapsibles:
            role_collapsible.filter(*filter_patterns)

        is_any_role_collapsible_displayed = any(collapsible.display for collapsible in role_collapsibles)
        if is_any_role_collapsible_displayed:
            self._remove_no_filter_criteria_match_widget()
            return

        self._mount_no_filter_criteria_match_widget()

    def filter_clear(self) -> None:
        role_collapsibles = list(self.role_collapsibles)

        for role_collapsible in role_collapsibles:
            role_collapsible.filter_clear()
            role_collapsible.display = True
        self._remove_no_filter_criteria_match_widget()


class ModifyAuthority(BaseScreen):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    BIG_TITLE = "Modify authority"

    def __init__(self) -> None:
        super().__init__()
        working_account = self.profile.accounts.working
        self.set_reactive(self.__class__.subtitle, f"for the {working_account.name} account")  # type: ignore[arg-type]

    def create_main_panel(self) -> ComposeResult:
        restore_button = CliveButton(label="Restore all changes", variant="error", id_="restore-button")
        yield FilterAuthorityContainer(action_button=restore_button)
        yield WorkingAccountAuthorityScrollable()
        yield TransactionButtonsPanel()

    @property
    def filter_authority(self) -> FilterAuthority:
        return self.query_exactly_one(FilterAuthority)

    @property
    def working_account_authority_scrollable(self) -> WorkingAccountAuthorityScrollable:
        return self.query_exactly_one(WorkingAccountAuthorityScrollable)

    @property
    def working_account_authority(self) -> Authority:
        return self.profile.accounts.working.data.authority

    @on(Mount)
    async def build_modify_working_account_authority_widget(self) -> None:
        await self.working_account_authority_scrollable.build()
        self._update_input_suggestions()

    @on(CliveButton.Pressed, "#restore-button")
    async def restore_all_changes(self) -> None:
        self.working_account_authority.reset()
        await self.working_account_authority_scrollable.rebuild()

    @on(AddToCartButton.Pressed)
    def test_testerinho(self) -> None:
        logger.debug(f"OWNER ROLE OBJECT: {id(self.working_account_authority.owner_role)}")
        logger.debug(f"WAS OWNER CHANGED? {self.working_account_authority.owner_role.changed}")

    @on(FilterAuthority.AuthorityFilterReady)
    def _apply_authority_filter(self) -> None:
        authority_filter_input = self.filter_authority.authority_filter_input
        filter_pattern = authority_filter_input.value_or_error
        self.working_account_authority_scrollable.filter(filter_pattern)

    @on(FilterAuthority.Cleared)
    def _handle_filter_cleared(self) -> None:
        self.working_account_authority_scrollable.filter_clear()

    # async def _add_entry():
    #     # entry_to_add
    #     # role_level
    #     self.working_account_authority.get_role_by_level(role_level).add(entry_to_remove.value)
    #     await self.working_account_authority_scrollable.rebuild()


    def _update_input_suggestions(self) -> None:
        input_suggestions: set[str] = set()
        filter_authority = self.filter_authority

        suggestions_to_add = [entry.value for entry in self.working_account_authority.get_entries()]
        input_suggestions.update(suggestions_to_add)
        filter_authority.authority_filter_input.clear_suggestions()

        filter_authority.authority_filter_input.add_suggestion(*input_suggestions)
