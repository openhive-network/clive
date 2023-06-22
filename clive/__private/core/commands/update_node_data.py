from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from math import ceil
from typing import TYPE_CHECKING, Final, cast

from clive.__private.core.commands.abc.command import Command
from clive.__private.core.iwax import calculate_current_manabar_value, calculate_manabar_full_regeneration_time
from clive.exceptions import CommunicationError
from clive.models import Asset

if TYPE_CHECKING:
    from types import TracebackType

    from clive.__private.core.node.node import Node
    from clive.__private.storage import mock_database
    from clive.__private.storage.mock_database import Account
    from schemas.__private.hive_fields_custom_schemas import Manabar
    from schemas.database_api.fundaments_of_reponses import AccountItemFundament
    from schemas.database_api.response_schemas import GetDynamicGlobalProperties
    from schemas.rc_api.fundaments_of_responses import RcAccount

    dgpo_t = GetDynamicGlobalProperties[Asset.HIVE, Asset.HBD, Asset.VESTS]


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
class UpdateNodeData(Command):
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

            self.__update_manabar(
                dgpo, int(info.core.post_voting_power.amount), info.core.voting_manabar, account.data.vote_manabar
            )

            self.__update_manabar(
                dgpo,
                int(info.core.post_voting_power.amount) // downvote_vote_ratio,
                info.core.downvote_manabar,
                account.data.downvote_manabar,
            )

            if info.rc is not None:
                self.__update_manabar(dgpo, int(info.rc.max_rc), info.rc.rc_manabar, account.data.rc_manabar)

            self.accounts[idx].data.hive_power_balance = self.__calculate_hive_power(dgpo, info.core)
            self.accounts[idx].data.reputation = self.__get_account_reputation(account.name)

            try:
                with SuppressNotExistingApi("account_history_api"):
                    self.accounts[idx].data.warnings = self.__count_warning(account)
                    self.accounts[idx].data.last_transaction = self.__get_newest_account_interactions(
                        account.name
                    ).replace(microsecond=0)
            except Exception as e:
                raise e from e

            self.accounts[idx].data.last_refresh = datetime.utcnow().replace(microsecond=0)

    def __count_warning(self, account: Account) -> int:
        warning_recovery_accounts: Final[set[str]] = {"steem"}
        warnings = int(account.data.recovery_account in warning_recovery_accounts)

        warning_period_in_days: Final[int] = 31
        last_vote_operation_filter: Final[int] = 4096
        last_vote_operation_history = self.node.api.account_history_api.get_account_history(
            account=account.name, operation_filter_low=last_vote_operation_filter, limit=1
        ).history
        # if moment of last voting is x, then raise warning if (x + 1y) > now() > x + (1y - warning period)
        if last_vote_operation_history:
            last_vote_operation_timestamp = last_vote_operation_history[0][1].timestamp
            warnings += int(
                (
                    (
                        year_from_last_vote := last_vote_operation_timestamp.replace(
                            year=last_vote_operation_timestamp.year + 1
                        )
                    )
                    - timedelta(days=warning_period_in_days)
                )
                < datetime.utcnow()
                < year_from_last_vote
            )

        warnings_high_filter, warnings_low_filter = 2048, 571814833029120
        history = self.node.api.account_history_api.get_account_history(
            account=account.name,
            operation_filter_high=warnings_high_filter,
            operation_filter_low=warnings_low_filter,
        ).history
        warnings += len(
            list(
                filter(
                    lambda aop: aop[1].timestamp >= datetime.utcnow().replace(year=datetime.utcnow().year - 1),
                    history,
                )
            )
        )

        return warnings

    def __get_newest_account_interactions(self, account_name: str) -> datetime:
        non_virtual_operations_filter: Final[int] = 0x3FFFFFFFFFFFF
        return (
            self.node.api.account_history_api.get_account_history(
                account=account_name,
                limit=1,
                operation_filter_low=non_virtual_operations_filter,
                include_reversible=True,
            )
            .history[0][1]
            .timestamp
        )

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
        dgpo: dgpo_t,
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
                int(self.__vests_to_hive(account_vesting_shares, dgpo).amount)
                / (10 ** dgpo.total_reward_fund_hive.get_asset_information().precision)
            ),
        )

    def __update_manabar(self, dgpo: dgpo_t, max_mana: int, manabar: Manabar, dest: mock_database.Manabar) -> None:
        power_from_api = int(manabar.current_mana)
        last_update = int(manabar.last_update_time)
        dest.max_value = int(self.__vests_to_hive(max_mana, dgpo).amount)
        dest.value = int(
            self.__vests_to_hive(
                calculate_current_manabar_value(
                    now=int(dgpo.time.timestamp()),
                    max_mana=max_mana,
                    current_mana=power_from_api,
                    last_update_time=last_update,
                ),
                dgpo,
            ).amount
        )

        dest.full_regeneration = (
            calculate_manabar_full_regeneration_time(
                now=int(dgpo.time.timestamp()),
                max_mana=max_mana,
                current_mana=power_from_api,
                last_update_time=last_update,
            )
            - dgpo.time
        )

    def __vests_to_hive(self, amount: int | Asset.VESTS, dgpo: dgpo_t) -> Asset.HIVE:
        if isinstance(amount, Asset.VESTS):
            amount = int(amount.amount)
        return Asset.HIVE(
            amount=int(amount * int(dgpo.total_vesting_fund_hive.amount) / int(dgpo.total_vesting_shares.amount))
        )
