from __future__ import annotations

from typing import TYPE_CHECKING

from textual.containers import Grid
from textual.widgets import Input, Static

from clive.__private.ui.operations.operation_base import OperationBase
from clive.__private.ui.widgets.big_title import BigTitle
from clive.__private.ui.widgets.ellipsed_static import EllipsedStatic
from clive.__private.ui.widgets.view_bag import ViewBag
from clive.models import Asset
from schemas.operations import AccountCreateOperation

if TYPE_CHECKING:
    from textual.app import ComposeResult

    from schemas.__private.hive_fields_basic_schemas import AssetHiveHF26


class Body(Grid):
    """All the content of the screen, excluding the title."""


class PlaceTaker(Static):
    """Container used for making correct layout of owner authority part."""


class AdditionalPlaceTaker(Static):
    """Container used for making correct layout of active authority part."""


class AdditionalPlaceTaker2(Static):
    """Container used for making correct layout of posting authority part."""


class AccountCreate(OperationBase):
    def __init__(self) -> None:
        super().__init__()

        self.__new_account_name_input = Input(placeholder="e.g: alice")
        self.__fee_input = Input(placeholder="e.g: 1.000")

        self.__weight_threshold_owner_input = Input(placeholder="e.g: 1")
        self.__account_auths_owner_input = Input(placeholder="e.g: alice, 1; bob, 1. Notice: split pair of values by ;")
        self.__key_auths_owner_input = Input(
            placeholder=(
                "e.g: STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9, 1. Notice: split pair of values by ;"
            )
        )

        self.__weight_threshold_active_input = Input(placeholder="e.g: 1")
        self.__account_auths_active_input = Input(
            placeholder="e.g: alice, 1; bob, 1. Notice: split pair of values by ;"
        )
        self.__key_auths_active_input = Input(
            placeholder=(
                "e.g: STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9, 1. Notice: split pair of values by ;"
            )
        )

        self.__weight_threshold_posting_input = Input(placeholder="e.g: 1")
        self.__account_auths_posting_input = Input(
            placeholder="e.g: alice, 1; bob, 1. Notice: split pair of values by ;"
        )
        self.__key_auths_posting_input = Input(
            placeholder=(
                "e.g: STM6vJmrwaX5TjgTS9dPH8KsArso5m91fVodJvv91j7G765wqcNM9, 1. Notice: split pair of values by ;"
            )
        )

        self.__memo_key_input = Input(placeholder="e.g: STM8ZSyzjPm48GmUuMSRufkVYkwYbZzbxeMysAVp7KFQwbTf98TcG")
        self.__json_metadata_input = Input(placeholder="e.g: {}")

    def create_left_panel(self) -> ComposeResult:
        with ViewBag():
            yield BigTitle("Account create")
            with Body():
                yield Static("creator", classes="label")
                yield EllipsedStatic(str(self.app.world.profile_data.working_account.name), id_="creator-label")
                yield Static("new account name", classes="label")
                yield self.__new_account_name_input
                yield Static("fee", classes="label")
                yield self.__fee_input
                yield Static("memo key", classes="label")
                yield self.__memo_key_input
                yield Static("json metadata", classes="label")
                yield self.__json_metadata_input
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

    def _create_operation(self) -> AccountCreateOperation[AssetHiveHF26]:
        valid_owner_account_auths = OperationBase._split_auths_fields(self.__account_auths_owner_input.value)
        valid_owner_key_auths = OperationBase._split_auths_fields(self.__key_auths_owner_input.value)

        valid_active_account_auths = OperationBase._split_auths_fields(self.__account_auths_active_input.value)
        valid_active_key_auths = OperationBase._split_auths_fields(self.__key_auths_active_input.value)

        valid_posting_account_auths = OperationBase._split_auths_fields(self.__account_auths_posting_input.value)
        valid_posting_key_auths = OperationBase._split_auths_fields(self.__key_auths_posting_input.value)

        owner_authority_field = {
            "weight_threshold": int(self.__weight_threshold_owner_input.value),
            "account_auths": valid_owner_account_auths,
            "key_auths": valid_owner_key_auths,
        }

        active_authority_field = {
            "weight_threshold": int(self.__weight_threshold_active_input.value),
            "account_auths": valid_active_account_auths,
            "key_auths": valid_active_key_auths,
        }

        posting_authority_field = {
            "weight_threshold": int(self.__weight_threshold_posting_input.value),
            "account_auths": valid_posting_account_auths,
            "key_auths": valid_posting_key_auths,
        }

        return AccountCreateOperation(
            creator=str(self.app.world.profile_data.name),
            fee=Asset.hive(float(self.__fee_input.value)),
            new_account_name=self.__new_account_name_input.value,
            owner=owner_authority_field,
            active=active_authority_field,
            posting=posting_authority_field,
            memo_key=self.__memo_key_input.value,
            json_metadata=self.__json_metadata_input.value,
        )
