from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Horizontal
from textual.widgets import Static

from clive.__private.core import iwax
from clive.__private.core.constants.tui.texts import LOADING_TEXT
from clive.__private.core.formatters.humanize import humanize_asset, humanize_percent, humanize_timedelta
from clive.__private.ui.widgets.clive_basic import CliveDataTable, CliveDataTableRow

if TYPE_CHECKING:
    from typing import Final

    from textual.app import ComposeResult

    from clive.__private.core.commands.data_retrieval.rc_data import RcData


class RcInfoTableRow(CliveDataTableRow):
    BALANCE_CELL_CLASS: Final[str] = "rc-balance-cell"

    def __init__(self, title: str) -> None:
        super().__init__(
            title,
            Static(LOADING_TEXT, classes=self.BALANCE_CELL_CLASS),
            Static(LOADING_TEXT, classes=self.BALANCE_CELL_CLASS),
            dynamic=True,
        )


class RcInfoTableHeader(Horizontal):
    def compose(self) -> ComposeResult:
        yield Static("RC Source", id="rc-name-header")
        yield Static("Amount [HP]", classes="rc-balance-header")
        yield Static("Amount [VESTS]", classes="rc-balance-header")


def _rc_as_hp(rc_amount: int, content: RcData) -> str:
    return humanize_asset(iwax.calculate_vests_to_hp(rc_amount, content.gdpo), show_symbol=False)


def _rc_as_vests(rc_amount: int) -> str:
    return humanize_asset(iwax.vests(rc_amount), show_symbol=False)


class RcInfoTableFromStakeRow(RcInfoTableRow):
    def __init__(self) -> None:
        super().__init__("From stake")

    def get_new_values(self, content: RcData) -> tuple[str, ...]:
        return _rc_as_hp(content.owned_rc_from_stake, content), _rc_as_vests(content.owned_rc_from_stake)


class RcInfoTableDelegatedRow(RcInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Delegated out")

    def get_new_values(self, content: RcData) -> tuple[str, ...]:
        return (
            humanize_asset(
                iwax.calculate_vests_to_hp(content.delegated_rc, content.gdpo), show_symbol=False, sign_prefix="-"
            ),
            humanize_asset(iwax.vests(content.delegated_rc), show_symbol=False, sign_prefix="-"),
        )


class RcInfoTableReceivedRow(RcInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Received")

    def get_new_values(self, content: RcData) -> tuple[str, ...]:
        return (
            humanize_asset(
                iwax.calculate_vests_to_hp(content.received_delegated_rc, content.gdpo),
                show_symbol=False,
                sign_prefix="+",
            ),
            humanize_asset(iwax.vests(content.received_delegated_rc), show_symbol=False, sign_prefix="+"),
        )


class RcInfoTableMaxRcRow(RcInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Max RC")

    def get_new_values(self, content: RcData) -> tuple[str, ...]:
        return _rc_as_hp(content.max_rc, content), _rc_as_vests(content.max_rc)


class RcInfoTableCurrentRcRow(RcInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Current RC")

    def get_new_values(self, content: RcData) -> tuple[str, ...]:
        return _rc_as_hp(content.current_mana, content), _rc_as_vests(content.current_mana)


class RcInfoTablePercentageRow(RcInfoTableRow):
    def __init__(self) -> None:
        super().__init__("RC %")

    def get_new_values(self, content: RcData) -> tuple[str, ...]:
        return humanize_percent(content.rc_percentage), ""


class RcInfoTableRegenerationRow(RcInfoTableRow):
    def __init__(self) -> None:
        super().__init__("Full regeneration in")

    def get_new_values(self, content: RcData) -> tuple[str, ...]:
        return humanize_timedelta(content.full_regeneration), ""


class RcDataTable(CliveDataTable):
    def __init__(self) -> None:
        super().__init__(
            RcInfoTableHeader(),
            RcInfoTableFromStakeRow(),
            RcInfoTableDelegatedRow(),
            RcInfoTableReceivedRow(),
            RcInfoTableMaxRcRow(),
            RcInfoTableCurrentRcRow(),
            RcInfoTablePercentageRow(),
            RcInfoTableRegenerationRow(),
            dynamic=True,
        )
