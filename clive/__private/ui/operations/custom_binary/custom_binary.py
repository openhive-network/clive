from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Label, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import CustomBinaryOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container using for making correct layout of  required auths"""


class AdditionalPlaceTaker(Static):
    """Container using for making correct layout of information label"""


class CustomBinary(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__required_owner_auths_input = Input(placeholder="e.g: alice, bob")
        self.__required_active_auths_input = Input(placeholder="e.g: charlie, bob")
        self.__required_posting_auths_input = Input(placeholder="e.g: alice, charlie")
        self.__id_input = Input(placeholder="e.g: 1000")
        self.__data_input = Input(placeholder="Custom data input")
        self.__required_auths_weight_threshold_input = Input(placeholder="e.g: 1 / 1")
        self.__required_auths_account_auths_input = Input(placeholder="e.g: alice, 1/bob, 1")
        self.__required_auths_key_auths_input = Input(
            placeholder="e.g: STM5Tki3ecCdCCHCjhhwvQvXuKryL2s34Ma6CXsRzntSUTYVYxCQ9, 1"
        )

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Custom binary")
            with Body():
                yield Static("required owner auths", classes="label")
                yield self.__required_owner_auths_input
                yield Static("required active auths", classes="label")
                yield self.__required_active_auths_input
                yield Static("required posting auths", classes="label")
                yield self.__required_posting_auths_input
                yield Static("id", classes="label")
                yield self.__id_input
                yield Static("data", classes="label")
                yield self.__data_input
                yield PlaceTaker()
                yield BigTitle("required auths")
                yield Static("weight threshold", classes="label")
                yield self.__required_auths_weight_threshold_input
                yield Static("account auths", classes="label")
                yield self.__required_auths_account_auths_input
                yield Static("key auths", classes="label")
                yield self.__required_auths_key_auths_input
                yield AdditionalPlaceTaker()
                yield Label(
                    "In required auths you can add few authorities, so if start adding new split it by /",
                    classes="information",
                )

    def _create_operation(self) -> CustomBinaryOperation:
        """
        In this operation user can put few authorities field, to deal with this user separate  authorities by '/;.
        In auths where user put few account names user separate it by ','
        """
        required_owner_auths_in_list = self.__required_owner_auths_input.value.split(",")
        required_owner_auths_in_list = [x.strip(" ") for x in required_owner_auths_in_list]

        required_active_auths_in_list = self.__required_active_auths_input.value.split(",")
        required_active_auths_in_list = [x.strip(" ") for x in required_active_auths_in_list]

        required_posting_auths_in_list = self.__required_posting_auths_input.value.split(",")
        required_posting_auths_in_list = [x.strip(" ") for x in required_posting_auths_in_list]

        split_weight_threshold = self.__required_auths_weight_threshold_input.value.split("/")
        split_weight_threshold = [x.strip(" ") for x in split_weight_threshold]

        split_account_auths = self.__required_auths_account_auths_input.value.split("/")
        split_account_auths = [x.strip(" ") for x in split_account_auths]

        split_key_auths = self.__required_auths_key_auths_input.value.split("/")
        split_key_auths = [x.strip(" ") for x in split_key_auths]

        required_auths = []
        for weight, account, key in zip(split_weight_threshold, split_account_auths, split_key_auths, strict=True):
            account_auths = OperationBase._split_auths_fields(account)
            key_auths = OperationBase._split_auths_fields(key)

            authority = {
                "weight_threshold": int(weight),
                "account_auths": account_auths,
                "key_auths": key_auths,
            }
            required_auths.append(authority)

        return CustomBinaryOperation(
            required_owner_auths=required_owner_auths_in_list,
            required_active_auths=required_active_auths_in_list,
            required_posting_auths=required_posting_auths_in_list,
            required_auths=required_auths,
            id_=int(self.__id_input.value),
            data=[self.__data_input.value],
        )
