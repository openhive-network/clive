from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, Right
from textual.events import Mount
from textual.message import Message
from textual.reactive import reactive, var
from textual.widgets import Label

from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs import (
    AddAuthorityEntryDialog,
    EditAuthorityMemoEntryDialog,
    EditAuthorityRegularEntryDialog,
    EditAuthorityTotalThresholdDialog,
)
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.account_details.authority.common import (
    AuthorityHeader,
    AuthorityItemBase,
    AuthorityRoleBase,
    AuthoritySectionScrollable,
    AuthorityTableBase,
    TopContainer,
)
from clive.__private.ui.screens.account_details.authority.filter_authority import (
    FilterAuthority,
)
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.operations.bindings import OperationActionBindings
from clive.__private.ui.widgets.buttons import (
    AddOneLineButton,
    AddToCartButton,
    EditOneLineButton,
    FinalizeTransactionButton,
    RemoveOneLineButton,
    RestoreButton,
)
from clive.__private.ui.widgets.clive_basic.clive_checkerboard_table import (
    CliveCheckerBoardTableCell,
)
from clive.__private.ui.widgets.clive_basic.clive_collapsible import CliveCollapsible
from clive.__private.ui.widgets.inputs.clive_input import CliveInput
from wax.exceptions.chain_errors import AuthorityCannotBeSatisfiedError, HiveMaxAuthorityMembershipExceededError
from wax.exceptions.validation_errors import NoAuthorityOperationGeneratedError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from textual.app import ComposeResult
    from textual.css.query import DOMQuery
    from textual.widget import Widget

    from clive.__private.core.authority import Authority, AuthorityRoleMemo, AuthorityRoleRegular
    from clive.__private.core.authority.entries import (
        AuthorityEntryMemo,
        AuthorityEntryRegular,
    )
    from clive.__private.models.schemas import AccountUpdate2Operation

NEW_PREFIX: Final[str] = "(new) "
MODIFIED_PREFIX: Final[str] = "*(modified) "


class TransactionButtonsPanel(Horizontal):
    def compose(self) -> ComposeResult:
        with Horizontal(id="transaction-buttons"):
            yield AddToCartButton()
            yield FinalizeTransactionButton()


class ThresholdLabel(Label):
    """
    Widget for displaying threshold information.

    Attributes:
        threshold_value: Current total threshold value.

    Args:
        threshold_value: Initial total threshold value.
    """

    threshold_value: int = reactive(None, init=False, layout=True)  # type: ignore[assignment]

    def __init__(self, threshold_value: int) -> None:
        super().__init__()
        self.set_reactive(self.__class__.threshold_value, threshold_value)  # type: ignore[arg-type]
        self._initial_threshold_value = threshold_value

    def render(self) -> str:
        return self._generate_threshold_text()

    def _generate_threshold_text(self) -> str:
        is_changed = self.threshold_value != self._initial_threshold_value
        prefix = MODIFIED_PREFIX if is_changed else ""
        return f"{prefix}authority total threshold: {self.threshold_value}"


class ModifyTotalThreshold(CliveWidget):
    show_edit_button: bool = reactive(default=False, init=False)  # type: ignore[assignment]

    def __init__(self, role: AuthorityRoleRegular, *, show_edit_button: bool) -> None:
        super().__init__()
        self.set_reactive(self.__class__.show_edit_button, show_edit_button)  # type: ignore[arg-type]
        self._role = role
        self._edit_button = EditOneLineButton(label="Edit threshold")

    @property
    def threshold_label(self) -> ThresholdLabel:
        return self.query_exactly_one(ThresholdLabel)

    @property
    def horizontal(self) -> Horizontal:
        return self.query_exactly_one(Horizontal)

    def compose(self) -> ComposeResult:
        with Horizontal():
            yield ThresholdLabel(self._role.weight_threshold)
            if self.show_edit_button:
                yield self._edit_button

    @on(EditOneLineButton.Pressed)
    def request_edit_authority_total_threshold(self) -> None:
        def edit_total_threshold_callback(new_weight: int | None) -> None:
            if new_weight is None:
                return
            self.threshold_label.threshold_value = new_weight
            self.notify(f"Total threshold of {self._role.level} role was changed to {new_weight}")

        self.app.push_screen(EditAuthorityTotalThresholdDialog(role=self._role), edit_total_threshold_callback)

    def _watch_show_edit_button(self, new_show_edit_button_value: bool) -> None:  # noqa: FBT001
        query = self.query(EditOneLineButton)
        is_mounted = bool(query)

        if new_show_edit_button_value and not is_mounted:
            self.horizontal.mount(self._edit_button)
        else:
            query.remove()


class ModifyAuthorityItem(AuthorityItemBase):
    """
    Class for items in the modify authority table.

    Attributes:
        entry: Object representing the authority entry.
        is_modified: Flag indicating if the item is modified.
        is_removed: Flag indicating if the item is removed.

    Args:
        entry: Object representing the authority entry.
        is_new: Flag to mark that this item is newly added.

    """

    entry: AuthorityEntryRegular | AuthorityEntryMemo = var(None, init=False)  # type: ignore[assignment]

    is_modified: bool = var(default=False, init=False)  # type: ignore[assignment]
    is_removed: bool = var(default=False, init=False)  # type: ignore[assignment]

    @dataclass
    class RequestEntryRemoval(Message):
        """
        Message sent when entry is about to be removed.

        Attributes:
            entry: entry that is about to be removed.
        """

        entry: AuthorityEntryRegular

    @dataclass
    class RequestEntryEdit(Message):
        """
        Message sent when entry is about to be edited.

        Attributes:
            entry: entry that is about to be edited.
        """

        entry: AuthorityEntryRegular | AuthorityEntryMemo

    def __init__(
        self,
        entry: AuthorityEntryRegular | AuthorityEntryMemo,
        *,
        is_new: bool = False,
    ) -> None:
        self._is_new = is_new
        super().__init__(entry)
        self.set_reactive(self.__class__.entry, entry)  # type: ignore[arg-type]
        self._original_entry = deepcopy(entry)

    @property
    def value_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#value-cell", CliveCheckerBoardTableCell)

    @property
    def weight_cell(self) -> CliveCheckerBoardTableCell:
        return self.query_exactly_one("#weight-cell", CliveCheckerBoardTableCell)

    @property
    def is_new(self) -> bool:
        return self._is_new

    def strikethrough(self) -> None:
        """Strikethrough content of cells in this row, disable buttons and mark it as removed."""
        self.is_removed = True
        self.is_modified = False
        self.entry = self._original_entry

    def squash(self, new_entry: AuthorityEntryRegular) -> None:
        """
        Used when new entry value matches already removed entry.

        Args:
            new_entry: New entry to squash with removed one.
        """
        self.is_removed = False
        self.is_modified = self._is_entry_changed(new_entry)
        self.entry = new_entry

    def edit_entry(self, new_entry: AuthorityEntryRegular | AuthorityEntryMemo) -> None:
        if not self.is_new:
            self.is_modified = self._is_entry_changed(new_entry)
        self.entry = new_entry

    def _create_cells(self) -> list[CliveCheckerBoardTableCell]:
        return [
            self._create_value_cell(),
            *self._maybe_create_weight_cell(),
            self._create_action_cell(),
        ]

    def _create_value_cell(self) -> CliveCheckerBoardTableCell:
        entry = self._entry
        classes = "key-or-account" if entry.is_weighted else "memo-key"
        return CliveCheckerBoardTableCell(entry.value, classes=classes, id_="value-cell")

    def _maybe_create_weight_cell(self) -> list[CliveCheckerBoardTableCell]:
        entry = self._entry
        if not entry.is_weighted:
            return []

        return [
            CliveCheckerBoardTableCell(
                str(entry.ensure_weighted.weight),
                classes="weight",
                id_="weight-cell",
            )
        ]

    def _create_action_cell(self) -> CliveCheckerBoardTableCell:
        if self._entry.is_weighted:
            content: Widget = Horizontal(
                EditOneLineButton(),
                RemoveOneLineButton(),
                id="action-buttons",
            )
        else:
            content = EditOneLineButton(label="Change", id_="edit-memo-button")

        return CliveCheckerBoardTableCell(content, classes="action")

    @on(Mount)
    async def _set_initial_prefix(self) -> None:
        await self._update_value_cell(self.entry.value)

    @on(EditOneLineButton.Pressed)
    def _request_entry_edit(self) -> None:
        self.post_message(self.RequestEntryEdit(entry=self.entry))

    @on(RemoveOneLineButton.Pressed)
    def _request_entry_removal(self) -> None:
        self.post_message(self.RequestEntryRemoval(entry=self.entry.ensure_regular))

    async def _watch_entry(self, new_entry: AuthorityEntryRegular | AuthorityEntryMemo) -> None:
        self._entry = new_entry
        await self._update_value_cell(new_entry.value)
        if new_entry.is_weighted:
            await self.weight_cell.update_content(str(new_entry.ensure_weighted.weight))

    def _watch_is_removed(self, is_removed: bool) -> None:  # noqa: FBT001
        striked_text_class_name = "striked-text"
        self.value_cell.set_class(is_removed, striked_text_class_name)
        self.weight_cell.set_class(is_removed, striked_text_class_name)
        self.disabled = is_removed

    async def _update_value_cell(self, value: str) -> None:
        await self.value_cell.update_content(self._prefixed(value))

    def _prefixed(self, value: str) -> str:
        if self.is_new:
            return f"{NEW_PREFIX}{value}"
        if self.is_modified:
            return f"{MODIFIED_PREFIX}{value}"
        return value

    def _is_entry_changed(self, new_entry: AuthorityEntryRegular | AuthorityEntryMemo) -> bool:
        if new_entry.is_weighted:
            return self._original_entry.ensure_weighted.weight != new_entry.ensure_weighted.weight
        return self._original_entry.value != new_entry.value


class ModifyAuthorityTable(AuthorityTableBase):
    LAST_COLUMN_HEADER_TITLE: Final[str] = "Action"

    def __init__(self, role: AuthorityRoleRegular | AuthorityRoleMemo) -> None:
        super().__init__(
            header=AuthorityHeader(last_column_header_title=self.LAST_COLUMN_HEADER_TITLE, memo_header=role.is_memo)
        )
        self._role = role

    @property
    def modify_authority_items(self) -> DOMQuery[ModifyAuthorityItem]:
        return self.query(ModifyAuthorityItem)

    def create_static_rows(self) -> Sequence[ModifyAuthorityItem]:
        return [ModifyAuthorityItem(entry) for entry in self._role.get_entries()]

    async def add_entry(
        self,
        new_entry: AuthorityEntryRegular | AuthorityEntryMemo,
    ) -> None:
        for item in self.query(ModifyAuthorityItem):
            if item.is_removed and item.entry.value == new_entry.value:
                item.squash(new_entry.ensure_regular)
                return

        await self.add_row(ModifyAuthorityItem(new_entry, is_new=True))

    def edit_entry(
        self,
        entry_to_edit: AuthorityEntryRegular | AuthorityEntryMemo,
        edited_entry: AuthorityEntryRegular | AuthorityEntryMemo,
    ) -> None:
        for item in self.modify_authority_items:
            if item.entry.value == entry_to_edit.value:
                item.edit_entry(edited_entry)
                return

    async def remove_entry(self, entry_to_remove: str) -> None:
        for index, item in enumerate(self.modify_authority_items):
            if item.entry.value == entry_to_remove:
                if item.is_new:
                    await self.remove_row(index)
                else:
                    item.strikethrough()
                break


class ModifyRole(AuthorityRoleBase):
    """
    Collapsible for role modification.

    Attributes:
        INITIAL_COLLAPSED_STATE: Initial state of `collapsed` in this collapsible.

    Args:
        role: Role to modify.
    """

    INITIAL_COLLAPSED_STATE: bool = False

    class RequestSuggestionUpdate(Message):
        """Request to update input suggestions after adding, removing or editing an entry."""

    def __init__(self, role: AuthorityRoleRegular | AuthorityRoleMemo) -> None:
        super().__init__(role=role)
        self._collapsible = self._create_collapsible()
        self.watch(self._collapsible, "collapsed", self._handle_visibility_of_modify_threshold_button, init=False)

    @property
    def authority_table(self) -> ModifyAuthorityTable:
        return self.query_exactly_one(ModifyAuthorityTable)

    @property
    def modify_total_threshold(self) -> ModifyTotalThreshold:
        return self.query_exactly_one(ModifyTotalThreshold)

    def compose(self) -> ComposeResult:
        with self._collapsible:
            if self._role.is_regular:
                with Right(id="right-button-container"):
                    yield AddOneLineButton(label="Add new entry")
            yield ModifyAuthorityTable(self._role)

    @on(AddOneLineButton.Pressed)
    def add_entry(self) -> None:
        async def add_entry_callback(new_entry: AuthorityEntryRegular | None) -> None:
            if new_entry is None:
                return

            await self.authority_table.add_entry(new_entry)
            self.notify(f"{new_entry.value} was added to {role.level} role")
            self.post_message(self.RequestSuggestionUpdate())

        role = self._role.ensure_regular
        self.app.push_screen(AddAuthorityEntryDialog(role=role), add_entry_callback)

    @on(ModifyAuthorityItem.RequestEntryEdit)
    def edit_entry(self, event: ModifyAuthorityItem.RequestEntryEdit) -> None:
        """
        Edit authority entry. Update values in table cells.

        Args:
            event: Event that triggered this method.
        """

        def edit_entry_callback(
            edited_entry: AuthorityEntryRegular | AuthorityEntryMemo | None,
        ) -> None:
            if edited_entry is None:
                return

            self.authority_table.edit_entry(entry_to_edit, edited_entry)
            self.app.notify("Entry modified successfully.")
            self.post_message(self.RequestSuggestionUpdate())

        entry_to_edit = event.entry

        if self._role.is_memo:
            self.app.push_screen(EditAuthorityMemoEntryDialog(self._role.ensure_memo), edit_entry_callback)
            return

        self.app.push_screen(
            EditAuthorityRegularEntryDialog(self._role.ensure_regular, entry_to_edit.ensure_regular),
            edit_entry_callback,
        )

    @on(ModifyAuthorityItem.RequestEntryRemoval)
    async def remove_entry(self, event: ModifyAuthorityItem.RequestEntryRemoval) -> None:
        """
        Remove entry from authority. Update removed row to indicate removal.

        Args:
            event: Event that triggered this method.
        """
        entry_to_remove = event.entry.value
        role = self._role.ensure_regular
        role_level = role.level
        role.remove(entry_to_remove)
        assert not role.has(entry_to_remove), f"Entry {entry_to_remove} was not removed from {role_level} role."
        await self.authority_table.remove_entry(entry_to_remove)
        self.app.notify(f"Entry {entry_to_remove} was removed from {role_level} role.")
        self.post_message(self.RequestSuggestionUpdate())

    def _create_collapsible(self) -> CliveCollapsible:
        threshold_widget: Widget | None = None

        if self._role.is_regular:
            threshold_widget = ModifyTotalThreshold(
                self._role.ensure_regular, show_edit_button=not self.INITIAL_COLLAPSED_STATE
            )
        return CliveCollapsible(
            right_hand_side_content=threshold_widget,
            title=self._role.level_display,
            collapsed=self.INITIAL_COLLAPSED_STATE,
        )

    def _handle_visibility_of_modify_threshold_button(self, new_collapsed_value: bool) -> None:  # noqa: FBT001
        if self._role.is_regular:
            self.modify_total_threshold.show_edit_button = not new_collapsed_value


class WorkingAccountAuthority(CliveWidget):
    """
    Display and modify authority of working account.

    Args:
        authority: Authority of working account.
    """

    def __init__(self, authority: Authority) -> None:
        super().__init__()
        self._authority = authority

    @property
    def authority_section_scrollable(self) -> AuthoritySectionScrollable:
        return self.query_exactly_one(AuthoritySectionScrollable)

    @property
    def role_collapsibles(self) -> DOMQuery[ModifyRole]:
        return self.query(ModifyRole)

    def compose(self) -> ComposeResult:
        with AuthoritySectionScrollable("Modify working account authority"):
            yield from [ModifyRole(role) for role in self._authority.roles]

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
            self.authority_section_scrollable.remove_no_filter_criteria_match_widget()
            return

        self.authority_section_scrollable.mount_no_filter_criteria_match_widget()

    def filter_clear(self) -> None:
        role_collapsibles = list(self.role_collapsibles)

        for role_collapsible in role_collapsibles:
            role_collapsible.filter_clear()
            role_collapsible.display = True
        self.authority_section_scrollable.remove_no_filter_criteria_match_widget()


class ModifyAuthority(BaseScreen, OperationActionBindings):
    DEFAULT_CSS = get_css_from_relative_path(__file__)

    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    BIG_TITLE = "Modify authority"
    ALLOW_THE_SAME_OPERATION_IN_CART_MULTIPLE_TIMES = False
    POP_SCREEN_AFTER_ADDING_OPERATION_TO_CART = True
    SHOW_INVALID_OPERATION_WARNING_NOTIFICATION = False

    def __init__(self) -> None:
        super().__init__()
        working_account = self.profile.accounts.working
        self._authority = deepcopy(working_account.data.authority)
        self.set_reactive(self.__class__.subtitle, f"for the {working_account.name} account")  # type: ignore[arg-type]

    @property
    def filter_authority(self) -> FilterAuthority:
        return self.query_exactly_one(FilterAuthority)

    @property
    def working_account_authority(self) -> WorkingAccountAuthority:
        return self.query_exactly_one(WorkingAccountAuthority)

    def create_main_panel(self) -> ComposeResult:
        yield TopContainer(action_button=RestoreButton(label="Restore all changes"))
        yield WorkingAccountAuthority(self._authority)
        yield TransactionButtonsPanel()

    @on(RestoreButton.Pressed)
    async def restore_all_changes(self) -> None:
        self._authority.reset()
        self.filter_authority.apply_default_filter()
        await self.working_account_authority.recompose()
        self.notify("All roles were restored.")
        self._update_input_suggestions()

    @on(FilterAuthority.AuthorityFilterReady)
    def _apply_authority_filter(self) -> None:
        authority_filter_input = self.filter_authority.authority_filter_input
        filter_pattern = authority_filter_input.value_or_error
        self.working_account_authority.filter(filter_pattern)

    @on(FilterAuthority.Cleared)
    def _handle_filter_cleared(self) -> None:
        self.working_account_authority.filter_clear()

    @on(CliveInput.Submitted)
    def _prevent_adding_to_cart_while_filtering(self, event: CliveInput.Submitted) -> None:
        """
        Prevent method from operation action bindings not to create operation when filtering is applied.

        Args:
            event: Event that triggered this method.
        """
        event.prevent_default()

    @on(Mount)
    @on(ModifyRole.RequestSuggestionUpdate)
    def _update_input_suggestions(self) -> None:
        input_suggestions: set[str] = set()
        filter_authority = self.filter_authority

        suggestions_to_add = [entry.value for entry in self._authority.get_entries()]
        input_suggestions.update(suggestions_to_add)
        filter_authority.authority_filter_input.clear_suggestions()
        filter_authority.authority_filter_input.add_suggestion(*input_suggestions)

    def _create_operation(self) -> AccountUpdate2Operation | None:
        try:
            operation = self._authority.to_schemas(self.world.wax_interface)
        except (
            NoAuthorityOperationGeneratedError,
            AuthorityCannotBeSatisfiedError,
            HiveMaxAuthorityMembershipExceededError,
        ) as error:
            self.notify(str(error), severity="warning")
            return None
        except RuntimeError:  # connected issue https://gitlab.syncad.com/hive/wax/-/issues/131
            self.notify(
                "Something went wrong during operation creation, please check if all "
                "added or edited values are correct.",
                severity="warning",
            )
            return None
        return operation
