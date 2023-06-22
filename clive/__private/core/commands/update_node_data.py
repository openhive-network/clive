from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from math import ceil
from typing import TYPE_CHECKING, Final, cast

from clive.__private.core.commands.command import Command
from clive.__private.core.iwax import calculate_current_manabar_value, calculate_manabar_full_regeneration_time
from clive.exceptions import CommunicationError
from clive.models import Asset  # noqa: TCH001

if TYPE_CHECKING:
    from datetime import datetime
    from types import TracebackType

    from clive.__private.core.node.node import Node
    from clive.__private.storage.mock_database import Account
    from schemas.__private.hive_fields_custom_schemas import Manabar
    from schemas.database_api.fundaments_of_reponses import AccountItemFundament
    from schemas.database_api.response_schemas import GetDynamicGlobalProperties
    from schemas.rc_api.fundaments_of_responses import RcAccount


class SuppressNotExistingApi:
    def __init__(self, api: str) -> None:
        self.__api_name = api

    def __enter__(self) -> None:
        return None

    def __exit__(self, _: type[Exception] | None, ex: Exception | None, __: TracebackType | None) -> bool:
        return ex is None or (  # if false, rethrows
            ex is not None
            and isinstance(ex, CommunicationError)
            and (
                isinstance(error_dict := ex.args[-1], dict)
                and (error := error_dict.get("error", {}))
                and (error_data := error.get("data", {}))
                and (stack := error_data.get("stack", [{}])[0])
                and (data := stack.get("data", {}))
                and (data.get("api", False) == self.__api_name)
            )
        )


@dataclass
class UpdateNodeData(Command[None]):
    accounts: list[Account]
    node: Node

    def execute(self) -> None:
        @dataclass
        class AccountApiInfo:
            core: AccountItemFundament[Asset.HIVE, Asset.HBD, Asset.VESTS] | None = None
            rc: RcAccount[Asset.VESTS] | None = None

        downvote_vote_ratio: Final[int] = 4
        api_accounts: dict[str, AccountApiInfo] = defaultdict(lambda: AccountApiInfo())
        account_names = [acc.name for acc in self.accounts]

        with SuppressNotExistingApi("rc_api"):
            rc_accounts = self.node.api.rc_api.find_rc_accounts(accounts=account_names).rc_accounts
            for rc_account in rc_accounts:
                api_accounts[rc_account.account].rc = rc_account
            assert len(api_accounts) == len(self.accounts), "invalid amount of accounts after rc api call"

        for core_account in self.node.api.database_api.find_accounts(accounts=account_names).accounts:
            api_accounts[core_account.name].core = core_account
        assert len(api_accounts) == len(self.accounts), "invalid amount of accounts after database api call"

        dgpo = self.node.api.database_api.get_dynamic_global_properties()
        for idx, account in enumerate(self.accounts):
            assert account.name in api_accounts, "account is not present in queried collection"
            info = api_accounts[account.name]
            assert info.core is not None, "database did not returned any data?"

            self.accounts[idx].data.hive_balance = info.core.balance
            self.accounts[idx].data.hive_dollars = info.core.hbd_balance
            self.accounts[idx].data.hive_savings = info.core.savings_balance
            self.accounts[idx].data.hbd_savings = info.core.savings_hbd_balance
            self.accounts[idx].data.hive_unclaimed = info.core.reward_hive_balance
            self.accounts[idx].data.hbd_unclaimed = info.core.reward_hbd_balance
            self.accounts[idx].data.hp_unclaimed = info.core.reward_vesting_balance
            self.accounts[idx].data.recovery_account = info.core.recovery_account

            (
                self.accounts[idx].data.voting_power,
                self.accounts[idx].data.hours_until_full_refresh_voting_power,
            ) = self.__calculate_manabar(dgpo.time, int(info.core.post_voting_power.amount), info.core.voting_manabar)

            (
                self.accounts[idx].data.down_vote_power,
                self.accounts[idx].data.hours_until_full_refresh_downvoting_power,
            ) = self.__calculate_manabar(
                dgpo.time, int(info.core.post_voting_power.amount) // downvote_vote_ratio, info.core.downvote_manabar
            )

            if info.rc is not None:
                (
                    self.accounts[idx].data.rc,
                    self.accounts[idx].data.hours_until_full_refresh_rc,
                ) = self.__calculate_manabar(dgpo.time, int(info.rc.max_rc), info.rc.rc_manabar)

            self.accounts[idx].data.hive_power_balance = self.__calculate_hive_power(dgpo, info.core)
            self.accounts[idx].data.reputation = self.__get_account_reputation(account.name)

    def __get_account_reputation(self, account_name: str) -> int:
        with SuppressNotExistingApi("reputation_api"):
            reputation = self.node.api.reputation_api.get_account_reputations(
                account_lower_bound=account_name, limit=1
            ).reputations
            assert len(reputation) == 1 and reputation[0].account == account_name, "reputation data malformed"
            return int(reputation[0].reputation)
        return 0

    def __calculate_hive_power(
        self,
        dgpo: GetDynamicGlobalProperties[Asset.HIVE, Asset.HBD, Asset.VESTS],
        account: AccountItemFundament[Asset.HIVE, Asset.HBD, Asset.VESTS],
    ) -> int:
        account_vesting_shares = (
            int(account.vesting_shares.amount)
            - int(account.delegated_vesting_shares.amount)
            + int(account.received_vesting_shares.amount)
        )
        return cast(
            int,
            ceil(
                int(account_vesting_shares)
                * int(dgpo.total_vesting_fund_hive.amount)
                / int(dgpo.total_vesting_shares.amount)
                / (10 ** dgpo.total_reward_fund_hive.get_asset_information().precision)
            ),
        )

    def __calculate_manabar(self, now: datetime, max_mana: int, manabar: Manabar) -> tuple[int, float]:
        amount_of_seconds_in_hour: Final[int] = 3600
        percent_100: Final[int] = 100

        voting_power_from_api = int(manabar.current_mana)
        voting_power_last_update = int(manabar.last_update_time)
        current_value = (
            calculate_current_manabar_value(
                now=int(now.timestamp()),
                max_mana=max_mana,
                current_mana=voting_power_from_api,
                last_update_time=voting_power_last_update,
            )
            * percent_100
        ) // max_mana

        hours_to_replenish = (
            calculate_manabar_full_regeneration_time(
                now=int(now.timestamp()),
                max_mana=max_mana,
                current_mana=voting_power_from_api,
                last_update_time=voting_power_last_update,
            )
            - now
        ).total_seconds() / amount_of_seconds_in_hour
        return current_value, hours_to_replenish
