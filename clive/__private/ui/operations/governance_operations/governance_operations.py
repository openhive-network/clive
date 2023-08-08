from __future__ import annotations

from typing import TYPE_CHECKING

from textual import on
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import DataTable, Input, SelectionList, Static, TabbedContent, Checkbox

from clive.__private.ui.operations.cart_based_screen.cart_based_screen import CartBasedScreen
from clive.__private.ui.operations.raw.account_witness_proxy.account_witness_proxy import AccountWitnessProxy
from clive.__private.ui.widgets.clive_button import CliveButton
from clive.__private.ui.widgets.clive_widget import CliveWidget
from clive.__private.ui.widgets.scrollable_tab_pane import ScrollableTabPane

if TYPE_CHECKING:
    from textual.app import ComposeResult


class ProxyPresent(Container):
    """Container which is displaying when account has proxy set."""

    def __init__(self, proxy: str):
        self.__proxy = proxy
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Static(f"Current proxy for account: {self.__proxy}", id="current-proxy")
        with Horizontal(id="delete-proxy-container"):
            yield Static("", classes="empty")
            yield Static("Delete current proxy", classes="action-proxy-label")
            yield CliveButton("Delete", id_="delete-proxy-button")
            yield Static("", classes="empty")

    @on(CliveButton.Pressed)
    def push_proxy_operation_delete_screen(self, event: CliveButton.Pressed) -> None:
        if event.button.id == "delete-proxy-button":
            self.app.push_screen(AccountWitnessProxy(delete_proxy=True))


class ProxyAbsent(Container):
    """Container which is displaying when account has not proxy set."""

    def compose(self) -> ComposeResult:
        with Horizontal(id="set-proxy-container"):
            yield Static("", classes="empty")
            yield Static("Click to set proxy for your account", classes="action-proxy-label")
            yield CliveButton("Set proxy", id_="set-proxy-button")
            yield Static("", classes="empty")
        yield Static("Notice: after setting proxy your votes for witnesses would be deleted!", id="proxy-warning")

    @on(CliveButton.Pressed)
    def push_proxy_operation_set_screen(self, event: CliveButton.Pressed) -> None:
        if event.button.id == "set-proxy-button":
            self.app.push_screen(AccountWitnessProxy())


class ProxyTab(ScrollableTabPane, CliveWidget):
    """Tab with all activities related with proxy."""

    def compose(self) -> ComposeResult:
        yield Static(
            "You cannot have set proxy and vote for witnesses/proposals at the same time",
            id="proxy-vote-information",
        )
        if proxy := self.app.world.profile_data.working_account.data.proxy:
            yield ProxyPresent(proxy=proxy)
        else:
            yield ProxyAbsent()


class WitnessList(SelectionList[str]):
    pass


ROWS = [("Rank", "Witness", "Votes received", "Price feed", "")]


class VoteForWitnessTable(DataTable[str]):
    pass


class DeleteVoteForWitnessTable(DataTable[str]):
    pass


class WitnessesTab(ScrollableTabPane, CliveWidget):
    """Tab with all activities related with witnesses."""

    def compose(self) -> ComposeResult:
        witnesses = [
            "1 blocktrades",
            "2 stoodkev",
            "3 gtg",
            "4 steempeak",
            "5 arcange",
            "6 ausbitbank",
            "7 roelandp",
            "8 gtg",
            "9 vote",
            "10 witness",
            "11 witness2",
            "12 hive",
            "13 alice",
            "14 bob",
            "15 charlie",
            "16 hiveio",
            "17 bob2",
            "18 alice2",
            "19 alice3",
            "20 alice5",
            "21 bob5",
            "22bob7",
            "23 bob8",
            "24 alice7",
            "25 charlie2",
            "26 charlie3",
            "27 charlie5",
            "28 charlie8",
            "29 charlie10",
            "30 charlie11",
        ]
        witnesses_list = [(witness, witness) for witness in witnesses]

        witnesses_selection_list: WitnessList = WitnessList(*witnesses_list)

        with Horizontal(id="test"):
            yield witnesses_selection_list
            with Vertical(id="witness-information-tables"):
                yield Static("You will vote for the witnesses:", classes="vote-witness-information")
                yield VoteForWitnessTable()
                yield Static("You will cancel votes for the witnesses:", classes="vote-witness-information")
                yield DeleteVoteForWitnessTable()
        yield Input("Place for filters", id="filters")

    def on_mount(self) -> None:
        table_vote = self.query_one(VoteForWitnessTable)
        table_vote.add_columns(*ROWS[0])

        table_delete_vote = self.query_one(DeleteVoteForWitnessTable)
        table_delete_vote.add_columns(*ROWS[0])

    @on(WitnessList.SelectedChanged)
    def add_or_delete_vote(self) -> None:
        id_ = 1
        votes = self.query_one(VoteForWitnessTable)
        witnesses = self.query_one(WitnessList).selected

        for witness in witnesses:
            if not votes.rows.get(witness):
                votes.add_row(str(id_), "blocktrades", "122", "0.355", "delete")
                id_ += 1


class Proposal(Container):
    def compose(self) -> ComposeResult:
        with Horizontal(id="proposal-container"):
            yield Checkbox()
            with Vertical(id="proposal-parameters"):
                yield Static("HBD stabilizer evolution May 2023 #264", id="proposal-title")
                yield Static("May 23, 2023 - Nov 22, 2023 (183 days) 4.39m HBD (Daily 24k HBD)",
                             id="proposal-pay")
                yield Static("by smooth for hbdstabilizer", id="proposal-author")


class ProposalsTab(ScrollableTabPane):
    """Tab with all activities related with witnesses."""
    def compose(self) -> ComposeResult:
        with Horizontal(id="list-proposals"):
            with Vertical(id="proposale"):
                yield Proposal()
                yield Proposal()
                yield Proposal()
                yield Proposal()
                yield Proposal()
                yield Proposal()
                yield Proposal()
                yield Proposal()
            with Vertical(id="voted-proposals"):
                yield Static("You will vote for the proposals:", id="vote-proposals")
                with Horizontal(id="proposal-x"):
                    yield Static("HBD stabilizer evolution May 2023", id="first-proposal")
                    yield Static("X", id="remove")
            yield Static("You will cancel votes for the proposals:", id="delete-vote-proposals")


class Governance(CartBasedScreen):
    BINDINGS = [
        Binding("escape", "pop_screen", "Cancel"),
    ]

    def create_left_panel(self) -> ComposeResult:
        with TabbedContent():
            yield ProxyTab("Proxy")
            yield WitnessesTab("Witnesses")
            yield ProposalsTab("Proposals")
