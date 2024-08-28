from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from textual import on, work
from textual.binding import Binding
from textual.events import Click
from textual.screen import ModalScreen
from textual.widgets import Static

from clive.__private.core.formatters.humanize import humanize_datetime, humanize_hbd_exchange_rate
from clive.__private.settings import safe_settings
from clive.__private.ui.get_css import get_relative_css_path
from clive.__private.ui.widgets.clive_basic.clive_widget import CliveWidget

if TYPE_CHECKING:
    from textual.app import ComposeResult


class WitnessDetailsWidget(Static):
    BORDER_TITLE = "WITNESS DETAILS"


class WitnessDetailsDialog(ModalScreen[None], CliveWidget):
    BINDINGS = [Binding("escape,f3", "request_quit", "Close")]

    CSS_PATH = [get_relative_css_path(__file__)]

    def __init__(self, witness_name: str) -> None:
        super().__init__()
        self.__witness_name = witness_name

    def on_mount(self) -> None:
        self.set_interval(safe_settings.node.refresh_rate_secs, lambda: self.refresh_witness_data())

    def compose(self) -> ComposeResult:
        widget = WitnessDetailsWidget()
        widget.loading = True
        yield widget

    @work(name="governance update modal details")
    async def refresh_witness_data(self) -> None:
        wrapper = await self.commands.find_witness(witness_name=self.__witness_name)

        if wrapper.error_occurred:
            new_witness_data = f"Unable to retrieve witness information:\n{wrapper.error}"
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

        with self.app.batch_update():
            await self.query("*").remove()
            await self.mount(WitnessDetailsWidget(new_witness_data))

    def action_request_quit(self) -> None:
        self.app.pop_screen()

    @on(Click)
    def close_screen_by_click(self) -> None:
        self.app.pop_screen()
