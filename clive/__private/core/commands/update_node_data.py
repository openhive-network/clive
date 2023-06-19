from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import ceil
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.command import Command
from clive.exceptions import CommunicationError
from clive.models import Asset  # noqa: TCH001
from schemas.database_api.fundaments_of_reponses import AccountItemFundament

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node
    from clive.__private.storage.mock_database import Account


@dataclass
class UpdateNodeData(Command[None]):
    account: Account
    node: Node

    def execute(self) -> None:
        try:
            # try to get reputation
            reputation = self.node.api.reputation_api.get_account_reputations(
                account_lower_bound=self.account.name, limit=1
            ).reputations
            assert len(reputation) == 1 and reputation[0].account == self.account.name
            self.account.data.reputation = int(reputation[0].reputation)
        except CommunicationError as e:
            if not (
                isinstance(error_dict := e.args[-1], dict)
                and (error := error_dict.get("error", {}))
                and (error_data := error.get("data", {}))
                and (stack := error_data.get("stack", [{}])[0])
                and (data := stack.get("data", {}))
                and (data.get("api", False) == "reputation_api")
            ):
                raise e from e

        response = self.node.api.database_api.find_accounts(accounts=[self.account.name]).accounts
        accounts = list(filter(lambda x: isinstance(x, AccountItemFundament) and x.name == self.account.name, response))
        assert len(accounts) == 1 and isinstance(accounts[0], AccountItemFundament)
        account: AccountItemFundament[Asset.HIVE, Asset.HBD, Asset.VESTS] = accounts[0]

        self.account.data.hive_balance = account.balance
        self.account.data.hive_dollars = account.hbd_balance
        self.account.data.hive_savings = account.savings_balance
        self.account.data.hbd_savings = account.savings_hbd_balance
        self.account.data.hive_unclaimed = account.reward_hive_balance
        self.account.data.hbd_unclaimed = account.reward_hbd_balance
        self.account.data.hp_unclaimed = account.reward_vesting_balance

        # max manabars
        downvote_vote_ratio: Final[int] = 4
        # TODO: add rc
        max_voting_manabar = int(account.post_voting_power.amount)
        max_downvoting_manabar = max_voting_manabar // downvote_vote_ratio

        # manabars current fulfillment
        percent_100: Final[int] = 100
        # TODO: add rc
        self.account.data.voting_power = int(account.voting_manabar.current_mana) * percent_100 // max_voting_manabar
        self.account.data.down_vote_power = (
            int(account.downvote_manabar.current_mana) * percent_100 // max_downvoting_manabar
        )

        # time to fully refresh
        # change after merge: https://gitlab.syncad.com/hive/hive/-/issues/507
        amount_of_days_to_fully_regen: Final[int] = 5
        amount_of_hours_in_day: Final[int] = 24
        hours_to_filly_regen = amount_of_days_to_fully_regen * amount_of_hours_in_day

        # TODO: add rc

        # voting manabar regen
        self.account.data.hours_until_full_refresh_voting_power = int(
            (1.0 - (self.account.data.voting_power / percent_100)) * hours_to_filly_regen
        )

        # downvoting manabar regen
        self.account.data.hours_until_full_refresh_downvoting_power = int(
            (1.0 - (self.account.data.down_vote_power / percent_100)) * hours_to_filly_regen
        )

        # calculate hive_power_balance
        dgpo = self.node.api.database_api.get_dynamic_global_properties()
        account_vesting_shares = (
            int(account.vesting_shares.amount)
            - int(account.delegated_vesting_shares.amount)
            + int(account.received_vesting_shares.amount)
        )
        self.account.data.hive_power_balance = ceil(
            int(account_vesting_shares)
            * int(dgpo.total_vesting_fund_hive.amount)
            / int(dgpo.total_vesting_shares.amount)
            / 10 ** dgpo.total_reward_fund_hive.get_asset_information().precision
        )

        self.account.data.last_refresh = datetime.now().replace(microsecond=0)
