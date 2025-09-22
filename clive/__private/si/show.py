from dataclasses import dataclass
from clive.__private.core.accounts.accounts import TrackedAccount
from clive.__private.si.base import CliveSi

@dataclass
class Balances:
    hbd_liquid: str
    hbd_savings: str
    hbd_unclaimed: str
    hive_liquid: str
    hive_savings: str
    hive_unclaimed: str

class ShowInterface:
    def __init__(self, clive_instance: "CliveSi") -> None:
        self.clive = clive_instance
    
    def profiles(self):
        pass

    async def balances(self, account_name: str, account_name_option: str | None = None) -> Balances:
        account = TrackedAccount(name=account_name)
        await self.clive.world.commands.update_node_data(accounts=[account])

        balances = account.data
        return Balances(
            hbd_liquid=balances.hbd_balance,
            hbd_savings=balances.hbd_savings,
            hbd_unclaimed=balances.hbd_unclaimed,
            hive_liquid=balances.hive_balance,
            hive_savings=balances.hive_savings,
            hive_unclaimed=balances.hive_unclaimed,
        )
