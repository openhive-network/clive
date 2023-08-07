from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Static

from clive.__private.ui.operations.raw_operation_base_screen import RawOperationBaseScreen
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.inputs.custom_input import CustomInput
from clive.__private.ui.widgets.inputs.input_label import InputLabel
from clive.__private.ui.widgets.placeholders_constants import ASSET_AMOUNT_PLACEHOLDER
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import ClaimRewardBalanceOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of a grid."""


class ClaimRewardBalance(RawOperationBaseScreen):
    def __init__(self) -> None:
        super().__init__()

        self.__reward_hive_input = CustomInput(label="reward hive", placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__reward_hbd_input = CustomInput(label="reward hbd", placeholder=ASSET_AMOUNT_PLACEHOLDER)
        self.__reward_vests_input = CustomInput(label="reward vests", placeholder=ASSET_AMOUNT_PLACEHOLDER)

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Claim reward balance")
            with Body():
                yield InputLabel("account")
                yield EllipsedStatic(self.app.world.profile_data.working_account.name, id_="account-label")
                yield PlaceTaker()
                yield from self.__reward_hive_input.compose()
                yield from self.__reward_hbd_input.compose()
                yield from self.__reward_vests_input.compose()

    def _create_operation(self) -> ClaimRewardBalanceOperation[Asset.Hive, Asset.Hbd, Asset.Vests]:
        return ClaimRewardBalanceOperation(
            account=self.app.world.profile_data.name,
            reward_hive=Asset.hive(self.__reward_hive_input.value),
            reward_hbd=Asset.hbd(self.__reward_hbd_input.value),
            reward_vests=Asset.vests(self.__reward_vests_input.value),
        )
