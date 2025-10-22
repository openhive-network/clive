from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from textual import on
from textual.binding import Binding
from textual.containers import Horizontal, Right
from textual.events import Mount
from textual.message import Message
from textual.reactive import reactive
from textual.widgets import Label

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
from clive.__private.ui.widgets.no_content_available import NoContentAvailable
from wax.exceptions.chain_errors import AuthorityCannotBeSatisfiedError, HiveMaxAuthorityMembershipExceededError
from wax.exceptions.validation_errors import NoAuthorityOperationGeneratedError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from textual.app import ComposeResult
    from textual.css.query import DOMQuery
    from textual.widget import Widget

    from clive.__private.models.schemas import AccountUpdate2Operation


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
        return f"{
            '(*modified) ' if self.threshold_value != self._initial_threshold_value else ''
        }authority total threshold: {self.threshold_value}"


class ModifyTotalThreshold(Horizontal):
    show_edit_button: bool = reactive(default=False, init=False)  # type: ignore[assignment]

    def __init__(self, role: AuthorityRoleRegular, *, show_edit_button: bool) -> None:
        super().__init__()
        self.set_reactive(self.__class__.show_edit_button, show_edit_button)  # type: ignore[arg-type]
        self._role = role
        self._edit_button = EditOneLineButton(label="Edit threshold")

    @property
    def threshold_label(self) -> ThresholdLabel:
        return self.query_exactly_one(ThresholdLabel)

    def compose(self) -> ComposeResult:
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

    async def _watch_show_edit_button(self, new_show_edit_button_value: bool) -> None:  # noqa: FBT001
        query = self.query(EditOneLineButton)
        is_mounted = bool(query)

        if new_show_edit_button_value and not is_mounted:
            self.mount(self._edit_button)
        else:
            query.remove()


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

    def __init__(
        self,
        entry: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo,
        *,
        is_new: bool = False,
    ) -> None:
        self._is_new = is_new
        super().__init__(entry)
        self._already_modified = False
        self._already_removed = False

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
    def already_removed(self) -> bool:
        return self._already_removed

    @property
    def pure_content(self) -> str:
        """Return just content if item wasn't modified, otherwise skip MODIFIED_PREFIX or NEW_PREFIX."""
        value_cell_content = str(self.value_cell.content)
        if (not self.already_removed and self.already_modified) or self._is_new:
            return value_cell_content.split(" ")[1]
        return value_cell_content

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
            self.post_message(self.RequestEntryRemoval(entry=self._entry))

    async def remove_or_strikethrough(
        self, initial_value_of_entry: str | None = None, initial_weight_of_entry: int | None = None
    ) -> None:
        """
        Handle removal of single entry - modify its content of completely remove it.

        Args:
            initial_value_of_entry: Initial value of the entry that was removed.
            initial_weight_of_entry: Initial weight of the entry that was removed.
        """
        if self._is_new:
            await self.remove()
        else:
            await self.refresh_content_cells(value=initial_value_of_entry, weight=initial_weight_of_entry)
            self.toggle_strikethrough_on_content_cells()
            self.toggle_row_buttons_disabled()
            self._already_removed = True

    async def refresh_content_cells(
        self, *, value: str | None = None, weight: int | None = None, apply_prefix: bool = False
    ) -> None:
        prefix = self.NEW_PREFIX if self._is_new else self.MODIFIED_PREFIX
        value_text = f"{prefix if apply_prefix else ''}{value if value else self._entry.value}"
        await self.value_cell.update_content(value_text)
        if self._entry.is_weighted:
            weight_text = str(weight if weight else self._entry.ensure_weighted.weight)
            await self.weight_cell.update_content(weight_text)

    def toggle_already_modified(self) -> None:
        self._already_modified = not self._already_modified

    def toggle_row_buttons_disabled(self) -> None:
        for button in self.query(CliveButton):
            button.disabled = not button.disabled

    def toggle_strikethrough_on_content_cells(self) -> None:
        striked_text_class_name = "striked-text"
        self.value_cell.toggle_class(striked_text_class_name)
        self.weight_cell.toggle_class(striked_text_class_name)


class ModifyAuthorityTable(AuthorityTableBase):
    LAST_COLUMN_HEADER_TITLE: Final[str] = "Action"
    NO_CONTENT_TEXT = "There are currently no entries in this role."

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
        new_entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | AuthorityEntryMemo,
        *,
        is_first_entry: bool,
    ) -> None:
        is_no_content_available_mounted = bool(self.query(NoContentAvailable))

        if is_first_entry and is_no_content_available_mounted:
            self.rows.remove()
            self.mount(
                AuthorityHeader(last_column_header_title=self.LAST_COLUMN_HEADER_TITLE, memo_header=self._role.is_memo)
            )

        for item in self.query(ModifyAuthorityItem):
            if item.already_removed and item.pure_content == new_entry.value:
                item.toggle_strikethrough_on_content_cells()
                use_prefix = False
                if item.weight_cell.content != str(new_entry.ensure_weighted.weight):
                    item.toggle_already_modified()
                    use_prefix = True
                await item.refresh_content_cells(
                    value=new_entry.value, weight=new_entry.ensure_weighted.weight, apply_prefix=use_prefix
                )
                item.toggle_row_buttons_disabled()
                return

        self.mount(ModifyAuthorityItem(new_entry, is_new=True))
        self.update_cell_colors()

    async def edit_entry(
        self,
        entry_to_edit: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo,
        entry_with_new_values: AuthorityEntryKeyRegular | AuthorityEntryAccountRegular | AuthorityEntryMemo,
    ) -> None:
        for item in self.modify_authority_items:
            if item.pure_content == entry_to_edit.value:
                item.update_entry(entry_with_new_values)
                if not item.already_modified:
                    item.toggle_already_modified()
                await item.refresh_content_cells(apply_prefix=True)
                self.app.notify("Entry modified successfully.")
                return

    async def remove_entry(self, entry_to_remove: str) -> None:
        for item in self.modify_authority_items:
            if item.entry_value == entry_to_remove:
                await item.remove_or_strikethrough(item.entry.initial_value, item.entry.ensure_weighted.initial_weight)
                break
        if not bool(self.rows):
            self.query_exactly_one(AuthorityHeader).remove()
            self.mount(self.get_no_content_available_widget())


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
        self._role = role
        widgets_to_mount, threshold_widget = self._create_widgets()
        super().__init__(
            *widgets_to_mount,
            role=role,
            title=role.level_display,
            right_hand_side_content=threshold_widget,
            collapsed=self.INITIAL_COLLAPSED_STATE,
        )
        self.watch(self, "collapsed", self._handle_visibility_of_modify_threshold_button, init=False)

    @property
    def authority_table(self) -> ModifyAuthorityTable:
        return self.query_exactly_one(ModifyAuthorityTable)

    @property
    def modify_total_threshold(self) -> ModifyTotalThreshold:
        return self.query_exactly_one(ModifyTotalThreshold)

    @on(AddOneLineButton.Pressed)
    async def add_authority_entry(self) -> None:
        async def add_entry_callback(new_entry: AuthorityEntryAccountRegular | AuthorityEntryKeyRegular | None) -> None:
            if new_entry is None:
                return

            assert role.has(new_entry.value, new_entry.weight), f"New entry was not added to {role.level_display} role."
            await self.authority_table.add_entry(new_entry, is_first_entry=is_first_entry)
            self.notify(f"{new_entry.value} was added to {role.level} role")

        role = self._role.ensure_regular
        is_first_entry = role.is_null_authority
        self.app.push_screen(AddAuthorityEntryDialog(role=role), add_entry_callback)

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

            await self.authority_table.edit_entry(entry_to_edit, entry_with_new_values)

        entry_to_edit = event.entry

        if isinstance(self._role, AuthorityRoleMemo):
            self.app.push_screen(EditMemoEntryDialog(self._role), edit_entry_callback)
        elif isinstance(self._role, AuthorityRoleRegular) and not isinstance(entry_to_edit, AuthorityEntryMemo):
            self.app.push_screen(EditRegularEntryDialog(self._role, entry_to_edit), edit_entry_callback)

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

    def _create_widgets(self) -> tuple[list[Widget], Widget | None]:
        widgets_to_mount: list[Widget] = []
        threshold_widget: Widget | None = None

        if self._role.is_regular:
            widgets_to_mount.append(Right(AddOneLineButton(label="Add new entry"), id="right-button-container"))
            threshold_widget = ModifyTotalThreshold(
                self._role.ensure_regular, show_edit_button=not self.INITIAL_COLLAPSED_STATE
            )

        widgets_to_mount.append(ModifyAuthorityTable(self._role))
        return widgets_to_mount, threshold_widget

    def _handle_visibility_of_modify_threshold_button(self, new_collapsed_value: bool) -> None:  # noqa: FBT001
        if self._role.is_regular:
            self.modify_total_threshold.show_edit_button = not new_collapsed_value


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
    def working_account_authority_scrollable(self) -> WorkingAccountAuthorityScrollable:
        return self.query_exactly_one(WorkingAccountAuthorityScrollable)

    def create_main_panel(self) -> ComposeResult:
        restore_button = CliveButton(label="Restore all changes", variant="error", id_="restore-button")
        yield FilterAuthorityContainer(action_button=restore_button)
        yield WorkingAccountAuthorityScrollable()
        yield TransactionButtonsPanel()

    @on(Mount)
    async def build_modify_working_account_authority_widget(self) -> None:
        await self.working_account_authority_scrollable.build(self._authority)
        self._update_input_suggestions()

    @on(CliveButton.Pressed, "#restore-button")
    async def restore_all_changes(self) -> None:
        self._authority.reset()
        self.filter_authority.apply_default_filter()
        await self.working_account_authority_scrollable.rebuild(self._authority)
        self.notify("All roles were restored.")

    @on(FilterAuthority.AuthorityFilterReady)
    def _apply_authority_filter(self) -> None:
        authority_filter_input = self.filter_authority.authority_filter_input
        filter_pattern = authority_filter_input.value_or_error
        self.working_account_authority_scrollable.filter(filter_pattern)

    @on(FilterAuthority.Cleared)
    def _handle_filter_cleared(self) -> None:
        self.working_account_authority_scrollable.filter_clear()

    @on(CliveInput.Submitted)
    async def _prevent_adding_to_cart_while_filtering(self, event: CliveInput.Submitted) -> None:
        """
        Prevent method from operation action bindings not to create operation when filtering is applied.

        Args:
            event: Event that triggered this method.
        """
        event.prevent_default()

    def _create_operation(self) -> AccountUpdate2Operation | None:
        try:
            operation = self._authority.to_schemas(self.world.wax_interface)
        except NoAuthorityOperationGeneratedError as error:
            self.notify(f"{error.message} Can't proceed.", severity="error")
            return None
        except AuthorityCannotBeSatisfiedError as error:
            self.notify(error.message, severity="error")
            return None
        except HiveMaxAuthorityMembershipExceededError as error:
            self.notify(error.message, severity="error")
            return None
        except RuntimeError:  # connected issue https://gitlab.syncad.com/hive/wax/-/issues/131
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
