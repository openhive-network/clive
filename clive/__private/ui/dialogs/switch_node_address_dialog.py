from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.ui.dialogs.clive_base_dialogs import CliveActionDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.node_widgets import NodesList, SelectedNodeAddress
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult


class SwitchNodeAddressDialog(CliveActionDialog):
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self) -> None:
        super().__init__(border_title="Switch node address")

    def create_dialog_content(self) -> ComposeResult:
        with Section():
            yield SelectedNodeAddress(self.node.http_endpoint)
            yield NodesList()

    async def _perform_confirmation(self) -> bool:
        change_node_succeeded = await self.query_exactly_one(NodesList).save_selected_node_address()
        return change_node_succeeded  # noqa: RET504
