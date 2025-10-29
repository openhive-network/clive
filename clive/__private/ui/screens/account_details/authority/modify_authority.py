from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, Right
from textual.css.query import DOMQuery, NoMatches
from textual.events import Mount
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Static

from clive.__private.core.authority import Authority, AuthorityRoleMemo, AuthorityRoleRegular
from clive.__private.core.authority.entries import (
    AuthorityEntryAccountRegular,
    AuthorityEntryKeyRegular,
    AuthorityEntryMemo,
)
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs import (
    AddAuthorityEntryDialog,
    EditAuthorityTotalThresholdDialog,
    EditMemoEntryDialog,
    EditRegularEntryDialog,
    RestoreOrRemoveEntryDialog,
)
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
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
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
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from wax.exceptions.chain_errors import AuthorityCannotBeSatisfiedError, HiveMaxAuthorityMembershipExceededError
from wax.exceptions.validation_errors import NoAuthorityOperationGeneratedError

from __private.core.commands.data_retrieval.update_node_data.clive_authority_data_provider import CliveAuthorityDataProviderWithTransactionData

if TYPE_CHECKING:
    from collections.abc import Sequence

    from textual.app import ComposeResult
    from textual.widget import Widget

    from clive.__private.models.schemas import AccountUpdate2Operation


class TransactionButtonsPanel(Horizontal):
    def compose(self) -> ComposeResult:
        yield Horizontal(AddToCartButton(), FinalizeTransactionButton(), id="transaction-buttons")


class ThresholdWidget(Static):
    """Widget for displaying threshold information."""


class ModifyTotalThreshold(Horizontal):
    edit_button_visible: bool = reactive(default=False, init=False)  # type: ignore[assignment]

    def __init__(self, role: AuthorityRoleRegular, *, parent_collapsed: bool) -> None:
        super().__init__()
        self.set_reactive(self.__class__.edit_button_visible, not parent_collapsed)  # type: ignore[arg-type]
        self._role = role
        self._parent_collapsed = parent_collapsed
        self._edit_button = EditOneLineButton(label="Edit threshold")

    def compose(self) -> ComposeResult:
        yield ThresholdWidget(self._generate_threshold_text(self._role.weight_threshold))
        if not self._parent_collapsed:
            yield self._edit_button

    @property
    def threshold_sign(self) -> ThresholdWidget:
        return self.query_exactly_one(ThresholdWidget)

    @on(EditOneLineButton.Pressed)
    def request_edit_authority_total_threshold(self) -> None:
        def edit_total_threshold_callback(new_weight: int | None) -> None:
            if new_weight is None:
                return
            self.threshold_sign.update(self._generate_threshold_text(new_weight, modified=True))
            self.notify(f"Total threshold of {self._role.level} role was changed to {new_weight}")

        self.app.push_screen(EditAuthorityTotalThresholdDialog(role=self._role), edit_total_threshold_callback)

    @staticmethod
    def _generate_threshold_text(weight_threshold: int, *, modified: bool = False) -> str:
        return f"{'(*modified) ' if modified else ''}authority total threshold: {weight_threshold}"

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

    Attributes:
        MODIFIED_PREFIX: Prefix added when item was modified.
        NEW_PREFIX: Prefix added when item is a new entry.

    Args:
        entry: Object representing the authority entry.
        is_new: Flag to mark that this item is newly added.

    """

    MODIFIED_PREFIX: Final[str] = "*(modified) "
    NEW_PREFIX: Final[str] = "(new) "

    def __init__(
        self,
        entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo,
        *,
        is_new: bool = False,
    ) -> None:
        self._is_new = is_new
        super().__init__(entry)
        self._original_entry = deepcopy(entry)
        self._already_modified = False

    @property
    def value_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#value-cell", CliveCheckerBoardTableCell)

    @property
    def weight_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#weight-cell", CliveCheckerBoardTableCell)

    @property
    def already_modified(self) -> bool:
        return self._already_modified

    @property
    def pure_content(self) -> str:
        """Return just content if item wasn't modified, otherwise skip MODIFIED_PREFIX or NEW_PREFIX."""
        value_cell_content = str(self.value_cell.content)
        if self.already_modified or self._is_new:
            return value_cell_content.split(" ")[1]
        return value_cell_content

    @dataclass
    class RequestEntryRemoval(Message):
        """
        Message sent when entry is about to be removed.

        Attributes:
            entry: entry that is about to be removed.
        """

        entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular

    @dataclass
    class RequestEntryEdit(Message):
        """
        Message sent when entry is about to be edited.

        Attributes:
            entry: entry that is about to be edited.
        """

        entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo

    @dataclass
    class RequestRestoreOrRemoval(Message):
        """
        Message sent when entry is already modified and user will have to choose between complete removal and restoring.

        Attributes:
            entry: entry that is about to be completely removed or restored to its initial state.
            initial_value: initial value of entry.
            initial_weight: initial weight of entry.
        """

        entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular
        initial_value: str
        initial_weight: int

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        cells = [
            CliveCheckerBoardTableCell(
                f"{self.NEW_PREFIX if self._is_new else ''}{self._entry.value}",
                classes="key-or-account" if self._entry.is_weighted else "memo-key",
                id_="value-cell",
            )
        ]

        if self._entry.is_weighted:
            cells.append(
                CliveCheckerBoardTableCell(str(self._entry.ensure_weighted.weight), classes="weight", id_="weight-cell")
            )
            last_cell_content: Widget = Horizontal(
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
        self.post_message(self.RequestEntryEdit(entry=self._entry))

    @on(RemoveOneLineButton.Pressed)
    def request_entry_removal(self) -> None:
        if isinstance(self._entry, (AuthorityEntryKeyRegular, AuthorityEntryAccountRegular)):
            if self._already_modified and not self._is_new:
                self.post_message(
                    self.RequestRestoreOrRemoval(
                        entry=self._entry,
                        initial_value=self._original_entry.value,
                        initial_weight=self._original_entry.ensure_weighted.weight,
                    )
                )
            else:
                self.post_message(self.RequestEntryRemoval(entry=self._entry))

    async def handle_after_item_removal(self) -> None:
        """Handle removal of single entry - modify its content of completely remove it."""
        if self._is_new:
            await self.remove()
        else:
            await self.refresh_content_cells(original_values=True)
            self._apply_strikethrough_to_content_cells()
            self._disable_buttons_within_row()

    async def handle_after_item_restore(self) -> None:
        """Handle restore of single entry - restore its content to original value."""
        self._entry.update_value(self._original_entry.value)
        self._entry.ensure_weighted.update_weight(self._original_entry.ensure_weighted.weight)
        await self.refresh_content_cells()
        self._already_modified = False

    async def refresh_content_cells(self, *, original_values: bool = False, apply_prefix: bool = False) -> None:
        prefix = self.NEW_PREFIX if self._is_new else self.MODIFIED_PREFIX
        value_text = (
            f"{prefix if apply_prefix else ''}{self._original_entry.value if original_values else self._entry.value}"
        )
        await self.value_cell.update_content(value_text)
        if self._entry.is_weighted:
            weight_text = str(
                self._original_entry.ensure_weighted.weight if original_values else self._entry.ensure_weighted.weight
            )
            await self.weight_cell.update_content(weight_text)

    def toggle_already_modified(self) -> None:
        self._already_modified = not self._already_modified

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

        if not isinstance(role, AuthorityRoleMemo):
            widgets_to_mount.append(Right(AddOneLineButton(label="Add new entry"), id="right-button-container"))
            threshold_widget = ModifyTotalThreshold(role, parent_collapsed=self.INITIAL_COLLAPSED_STATE)

        widgets_to_mount.append(ModifyAuthorityTable(role))

        super().__init__(
            *widgets_to_mount,
            role=role,
            title=role.level_display,
            right_hand_side_widget=threshold_widget,
            collapsed=self.INITIAL_COLLAPSED_STATE,
        )
        self.watch(self, "collapsed", self._handle_visibility_of_modify_threshold_button, init=False)

    @property
    def modify_authority_items(self) -> DOMQuery[ModifyAuthorityItem]:
        return self.query(ModifyAuthorityItem)

    @property
    def modify_total_threshold(self) -> ModifyTotalThreshold:
        return self.query_exactly_one(ModifyTotalThreshold)

    @on(AddOneLineButton.Pressed)
    def add_authority_entry(self) -> None:
        def add_entry_callback(new_entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | None) -> None:
            if new_entry is None or not isinstance(self._role, AuthorityRoleRegular):
                return

            assert self._role.has(new_entry.value, new_entry.weight), (
                f"New entry was not added to {self._role.level_display} role."
            )
            authority_table = self.authority_table
            authority_table.mount(ModifyAuthorityItem(new_entry, is_new=True))
            authority_table.update_cell_colors()
            self.notify(f"{new_entry.value} was added to {self._role.level} role")

        if not isinstance(self._role, AuthorityRoleRegular):
            return

        self.app.push_screen(AddAuthorityEntryDialog(role=self._role), add_entry_callback)

    @on(ModifyAuthorityItem.RequestEntryEdit)
    def edit_entry(self, event: ModifyAuthorityItem.RequestEntryEdit) -> None:
        """
        Edit authority entry. Update values in table cells.

        Args:
            event: Event that triggered this method.
        """

        async def edit_entry_callback(
            entry_with_new_values: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | AuthorityEntryMemo | None,
        ) -> None:
            if entry_with_new_values is None:
                return

            entry_not_modified_message = "Entry was not modified."

            for item in self.modify_authority_items:
                if item.pure_content == entry_to_edit:
                    item.update_entry(entry_with_new_values)
                    if isinstance(self._role, AuthorityRoleMemo):
                        assert self._role.value == entry_with_new_values.value, entry_not_modified_message
                    elif isinstance(self._role, AuthorityRoleRegular) and not isinstance(
                        entry_with_new_values, AuthorityEntryMemo
                    ):
                        assert self._role.has(entry_with_new_values.value, entry_with_new_values.weight), (
                            entry_not_modified_message
                        )
                    if not item.already_modified:
                        item.toggle_already_modified()
                    await item.refresh_content_cells(apply_prefix=True)
                    self.app.notify("Entry modified successfully.")
                    return

        entry_to_edit = event.entry.value

        if isinstance(self._role, AuthorityRoleMemo):
            self.app.push_screen(
                EditMemoEntryDialog(role=self._role, entry_current_value=entry_to_edit), edit_entry_callback
            )
        else:
            self.app.push_screen(
                EditRegularEntryDialog(role=self._role, entry_current_value=entry_to_edit), edit_entry_callback
            )

    @on(ModifyAuthorityItem.RequestEntryRemoval)
    async def remove_entry(self, event: ModifyAuthorityItem.RequestEntryRemoval) -> None:
        """
        Remove entry from authority. Update removed row to indicate removal.

        Args:
            event: Event that triggered this method.
        """

        async def handle_authority_entry_removal() -> None:
            for item in self.modify_authority_items:
                if item.entry_value == entry_to_remove:
                    await item.handle_after_item_removal()
                    break

        if not isinstance(self._role, AuthorityRoleRegular):
            return

        entry_to_remove = event.entry.value

        role_level = self._role.level
        self._role.remove(entry_to_remove)
        assert not self._role.has(entry_to_remove), f"Entry {entry_to_remove} was not removed from {role_level} role."
        await handle_authority_entry_removal()
        self.app.notify(f"Entry {entry_to_remove} was removed from {role_level} role.")

    @on(ModifyAuthorityItem.RequestRestoreOrRemoval)
    async def remove_or_restore_entry(self, event: ModifyAuthorityItem.RequestRestoreOrRemoval) -> None:
        """
        Remove or restore already modified entry from authority.

        Args:
            event: Event that triggered this method.
        """

        async def restore_or_remove_entry_callback(result: bool | None) -> None:  # noqa: FBT001
            if result is None:
                return
            role_level = self._role.level_display

            for item in self.modify_authority_items:
                if item.entry_value == entry_to_remove_or_restore.value:
                    if result:
                        self.app.notify(f"Entry {entry_to_remove_or_restore.value} was restored to its original value.")
                        await item.handle_after_item_restore()
                    else:
                        self.app.notify(f"Entry {entry_to_remove_or_restore.value} was removed from {role_level} role.")
                        await item.handle_after_item_removal()
                    break

        if not isinstance(self._role, AuthorityRoleRegular):
            return
        entry_to_remove_or_restore = event.entry
        self.app.push_screen(
            RestoreOrRemoveEntryDialog(
                role=self._role,
                current_entry=entry_to_remove_or_restore,
                initial_value=event.initial_value,
                initial_weight=event.initial_weight,
            ),
            restore_or_remove_entry_callback,
        )

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

    async def build(self, authority: Authority) -> None:
        await self.body.mount_all([ModifyRole(role) for role in authority.roles])

    async def rebuild(self, authority: Authority) -> None:
        with self.app.batch_update():
            await self.body.query("*").remove()
            await self.build(authority)

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


class ModifyAuthority(BaseScreen, OperationActionBindings):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    BIG_TITLE = "Modify authority"
    ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES = False

    def __init__(self) -> None:
        super().__init__()
        working_account = self.profile.accounts.working
        self._authority = deepcopy(working_account.data.authority)
        self._authority.sync_operation_with_transaction(self.profile.transaction)
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

    @on(Mount)
    async def build_modify_working_account_authority_widget(self) -> None:
        await self.working_account_authority_scrollable.build(self._authority)
        self._update_input_suggestions()

    @on(CliveButton.Pressed, "#restore-button")
    async def restore_all_changes(self) -> None:
        self._authority.reset()
        await self.working_account_authority_scrollable.rebuild(self._authority)

    @on(FilterAuthority.AuthorityFilterReady)
    def _apply_authority_filter(self) -> None:
        authority_filter_input = self.filter_authority.authority_filter_input
        filter_pattern = authority_filter_input.value_or_error
        self.working_account_authority_scrollable.filter(filter_pattern)

    @on(FilterAuthority.Cleared)
    def _handle_filter_cleared(self) -> None:
        self.working_account_authority_scrollable.filter_clear()

    @on(CliveInput.Submitted)
    async def prevent_adding_to_cart_while_filtering(self, event: CliveInput.Submitted) -> None:
        """
        Prevent method from operation action bindings not to create operation when filtering is applied.

        Args:
            event: Event that triggered this method.
        """
        event.prevent_default()

    def _create_operation(self) -> AccountUpdate2Operation | None:
        if not self._validate_emptiness_of_regular_roles():
            return None
        try:
            operation = self._authority.finalize(self.world.wax_interface)
        except NoAuthorityOperationGeneratedError as error:
            self.notify(error.message, severity="error")
            return None
        except AuthorityCannotBeSatisfiedError as error:
            self.notify(error.message, severity="error")
            return None
        except HiveMaxAuthorityMembershipExceededError as error:
            self.notify(error.message, severity="error")
            return None
        except RuntimeError:
            self.notify(
                "Something went wrong during operation creation, please check if all "
                "added or edited values are correct.",
                severity="error",
            )
            return None
        return operation

    def _update_input_suggestions(self) -> None:
        input_suggestions: set[str] = set()
        filter_authority = self.filter_authority

        suggestions_to_add = [entry.value for entry in self._authority.get_entries()]
        input_suggestions.update(suggestions_to_add)
        filter_authority.authority_filter_input.clear_suggestions()

        filter_authority.authority_filter_input.add_suggestion(*input_suggestions)

    def _validate_emptiness_of_regular_roles(self) -> bool:
        """
        Validate if every regular role has at least one entry.

        Returns:
            True if all regular roles have at least one entry, False otherwise.
        """
        for role in self._authority.roles:
            if isinstance(role, AuthorityRoleRegular) and role.is_null_authority:
                self.notify(f"{role.level_display} role cannot be empty.", severity="error")
                return False
        return True
