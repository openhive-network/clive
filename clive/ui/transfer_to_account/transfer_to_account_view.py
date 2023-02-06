from clive.ui.components.side_panel import SidePanel
from clive.ui.transfer_to_account.trabsfer_to_account_buttons import TransferToAccountButtons
from clive.ui.transfer_to_account.transfer_to_account_panel import TransferToAccountPanel
from clive.ui.views.side_pane_based import SidePanelBased

Main = TransferToAccountPanel
Side = SidePanel["TransferToAccountView"]
Buttons = TransferToAccountButtons


class TransferToAccountView(SidePanelBased[Main, Side, Buttons]):
    def __init__(self, asset: str) -> None:
        self.__asset = asset
        super().__init__(TransferToAccountPanel(self), SidePanel(self), TransferToAccountButtons(self))

    @property
    def asset(self) -> str:
        return self.__asset
