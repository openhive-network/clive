from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.view_bag import ViewBag
from schemas.operations import AccountUpdate2Operation

if TYPE_CHECKING:
    from textual.app import ComposeResult


class Body(Grid):
    """All the content of the screen, excluding the title"""


class PlaceTaker(Static):
    """Container used for making correct layout of owner authority part"""


class AdditionalPlaceTaker(Static):
    """Container used for making correct layout of active authority part"""


class AdditionalPlaceTaker2(Static):
    """Container used for making correct layout of posting authority part"""


class AccountUpdate2(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__account_input = Input(placeholder="e.g: alice")
        self.__memo_key_input = Input(placeholder="e.g: STM8ZSyzjPm48GmUuMSRufkVYkwYbZzbxeMysAVp7KFQwbTf98TcG")
        self.__json_metadata_input = Input(placeholder="e.g: {}")
        self.__posting_json_metadata = Input(placeholder="e.g: {}")

        self.__weight_threshold_owner_input = Input("None", placeholder="e.g: 1")
        self.__account_auths_owner_input = Input(
            "None", placeholder="e.g: alice, 1; bob, 1. Notice: split pair of values by ;"
        )
        self.__key_auths_owner_input = Input(
            "None",
            placeholder="e.g: STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9, 1. Notice: split pair of values by ;",
        )

        self.__weight_threshold_active_input = Input("None", placeholder="e.g: 1")
        self.__account_auths_active_input = Input(
            "None", placeholder="e.g: alice, 1; bob, 1. Notice: split pair of values by ;"
        )
        self.__key_auths_active_input = Input(
            "None",
            placeholder="e.g: STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9, 1. "
            "Notice: split pair of values by ;",
        )

        self.__weight_threshold_posting_input = Input("None", placeholder="e.g: 1")
        self.__account_auths_posting_input = Input(
            "None", placeholder="e.g: alice, 1; bob, 1. Notice: split pair of values by ;"
        )
        self.__key_auths_posting_input = Input(
            "None",
            placeholder="e.g: STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9, 1. "
            "Notice: split pair of values by ;",
        )

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account update two")
            with Body():
                yield Static("account", classes="label")
                yield self.__account_input
                yield Static("memo key", classes="label")
                yield self.__memo_key_input
                yield Static("json metadata", classes="label")
                yield self.__json_metadata_input
                yield Static("posting json metadata", classes="label")
                yield self.__posting_json_metadata
                yield PlaceTaker()
                yield BigTitle("owner authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_owner_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_owner_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_owner_input
                yield AdditionalPlaceTaker()
                yield BigTitle("active authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_active_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_active_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_active_input
                yield AdditionalPlaceTaker2()
                yield BigTitle("posting authority")
                yield Static("weight threshold", classes="label")
                yield self.__weight_threshold_posting_input
                yield Static("account auths", classes="label")
                yield self.__account_auths_posting_input
                yield Static("key auths", classes="label")
                yield self.__key_auths_posting_input

    def _create_operation(self) -> AccountUpdate2Operation:
        valid_owner_account_auths = OperationBase._split_auths_fields(self.__account_auths_owner_input.value)
        valid_owner_key_auths = OperationBase._split_auths_fields(self.__key_auths_owner_input.value)

        valid_active_account_auths = OperationBase._split_auths_fields(self.__account_auths_active_input.value)
        valid_active_key_auths = OperationBase._split_auths_fields(self.__key_auths_active_input.value)

        valid_posting_account_auths = OperationBase._split_auths_fields(self.__account_auths_posting_input.value)
        valid_posting_key_auths = OperationBase._split_auths_fields(self.__key_auths_posting_input.value)

        if self.__weight_threshold_owner_input.value != "None":
            owner_authority_field = {
                "weight_threshold": int(self.__weight_threshold_owner_input.value),
                "account_auths": valid_owner_account_auths,
                "key_auths": valid_owner_key_auths,
            }
        else:
            owner_authority_field = None

        if self.__weight_threshold_active_input.value != "None":
            active_authority_field = {
                "weight_threshold": int(self.__weight_threshold_active_input.value),
                "account_auths": valid_active_account_auths,
                "key_auths": valid_active_key_auths,
            }
        else:
            active_authority_field = None

        if self.__weight_threshold_posting_input.value != "None":
            posting_authority_field = {
                "weight_threshold": int(self.__weight_threshold_posting_input.value),
                "account_auths": valid_posting_account_auths,
                "key_auths": valid_posting_key_auths,
            }
        else:
            posting_authority_field = None

        return AccountUpdate2Operation(
            account=self.__account_input.value,
            memo_key=self.__memo_key_input.value,
            active=active_authority_field,
            posting=posting_authority_field,
            owner=owner_authority_field,
            json_metadata=self.__json_metadata_input.value,
            posting_json_metadata=self.__posting_json_metadata.value,
        )
