from __future__ import annotations
from typing import TYPE_CHECKING
from clive.__private.ui.get_css import get_css_from_relative_path
from clive.__private.ui.screens.account_details.authority.authority import AuthorityTable, FilterAuthority
from clive.__private.ui.screens.base_screen import BaseScreen
from clive.__private.ui.screens.operations.bindings.operation_action_bindings import OperationActionBindings
from textual.containers import Container, Horizontal, Middle
from textual.widgets import Collapsible, Static
from textual.binding import Binding
from clive.__private.ui.widgets.inputs.text_input import TextInput
from clive.__private.ui.widgets.buttons import (
    AddToCartButton,
    FinalizeTransactionButton,
)
from clive.__private.logger import logger
from clive.__private.ui.widgets.buttons.clive_button import CliveButton
from clive.__private.ui.widgets.clive_basic.clive_checkerboard_table import CliveCheckerboardTable

from wax.complex_operations.account_update import AccountAuthorityUpdateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult
    from wax.models.authority import WaxAuthority
    from wax.models.basic import PublicKey
    from wax.models.authority import WaxAccountAuthorityInfo

class DockedButtonPanel(Horizontal):
    def compose(self) -> ComposeResult:
        yield Horizontal(AddToCartButton(), FinalizeTransactionButton(), id="button-container")

class ModifyTotalThreshold(Horizontal):
    """Widget to modify the total threshold of the authority."""
    def __init__(self, total_threshold: int) -> None:
        super().__init__()
        self._total_threshold = total_threshold

    def compose(self) -> ComposeResult:
        yield Middle(Static("authority threshold:"))
        yield TextInput(title="threshold")

# class ModifyAuthorityTable(AuthorityTable):
#     ...

# class ModifyAuthorityType(Collapsible):
#      def __init__(
#         self,
#         account_authorities: WaxAuthority | PublicKey | None,
#         *,
#         title: str,
#         filter_pattern: str | None = None,
#         collapsed: bool = False,
#     ) -> None:
#         # self._total_threshold = account_authorities.weight_threshold
#         super().__init__(
#             # INCLUDE ADDITIONAL WIDGET WITH MODIFY TOTAL THRESHOLD
#             ModifyAuthorityTable(account_authorities, filter_pattern=filter_pattern), title=title, collapsed=collapsed
#         )


class ModifyAuthority(BaseScreen):
    DEFAULT_CSS = get_css_from_relative_path(__file__)
    
    BINDINGS = [Binding("escape", "app.pop_screen", "Back")]
    BIG_TITLE = "Authority management"

    def __init__(self, filter_input_entry: str | None, selected_filter_options: list[str]) -> None:
        super().__init__()
        self._selected_filter_options = selected_filter_options
        self._filter_input_entry = filter_input_entry

    async def on_mount(self) -> None:
        operation = await AccountAuthorityUpdateOperation.create_for(self.world.wax_interface, "gtg")
        logger.debug(f"ROLES: {operation.categories.hive.account}")

    def create_main_panel(self) -> ComposeResult:
        with Horizontal(id="filter-and-modify"):
            yield FilterAuthority(accounts=self._selected_filter_options)
            yield Container(
                CliveButton(label="Restore", variant="error", id_="restore-button"),
                id="button-container",
            )
        yield ModifyTotalThreshold(1)
        yield DockedButtonPanel()
        # yield self._authority_roles

    