from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual import work
from textual.binding import Binding
from textual.containers import Center
from textual.widgets import Static

from clive.__private.core.formatters.humanize import humanize_datetime, humanize_hbd_exchange_rate
from clive.__private.settings import safe_settings
from clive.__private.ui.clive_widget import CliveWidget
from clive.__private.ui.dialogs.clive_base_dialogs import CliveInfoDialog
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.section import Section

if TYPE_CHECKING:
    from textual.app import ComposeResult


class WitnessDetailsWidget(Static):
    """Display witness details."""


class WitnessDetailsDialog(CliveInfoDialog, CliveWidget):
    BINDINGS = [Binding("escape,f3", "close", "Close")]
    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, witness_name: str) -> None:
        super().__init__(border_title=f"Details for [yellow]{witness_name}[/] witness")
        self._witness_name = witness_name
        self._witness_widget = WitnessDetailsWidget()
        self._witness_widget.loading = True

    def on_mount(self) -> None:
        self.set_interval(safe_settings.node.refresh_rate_secs, lambda: self.refresh_witness_data())

    def create_dialog_content(self) -> ComposeResult:
        with Center(), Section():
            yield self._witness_widget

    @work(name="governance update modal details")
    async def refresh_witness_data(self) -> None:
        wrapper = await self.commands.find_witness(witness_name=self._witness_name)

        if wrapper.error_occurred:
            new_witness_data = "Failed to retrieve witness information."
        else:
            witness = wrapper.result_or_raise
            url = witness.url
            created = humanize_datetime(witness.created)
            missed_blocks = witness.total_missed
            last_block = witness.last_confirmed_block_num
            price_feed = humanize_hbd_exchange_rate(witness.hbd_exchange_rate, with_label=True)
            version = witness.running_version
            now = humanize_datetime(datetime.now().replace(microsecond=0))  # noqa: DTZ005; we want a local time there
            new_witness_data = f"""\
            === Time of the query: {now} ===
                url: {url}
                created: {created}
                missed blocks: {missed_blocks}
                last block: {last_block}
                {price_feed}
                version: {version}\
            """

        self._witness_widget.loading = False
        self._witness_widget.update(new_witness_data)
