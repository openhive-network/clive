from clive.__private.models.transaction import Transaction
from clive.__private.si.base import CliveSi
from schemas.operations.transfer_operation import TransferOperation
from schemas.fields.assets import AssetBase
from wax.helpy._interfaces.asset.asset import Asset

class ProcessInterface:
    def __init__(self, clive_instance: "CliveSi") -> None:
        self.clive = clive_instance

    async def transfer(
        self,
        from_account: str,
        to: str,
        amount: str,
        memo: str = "",
        sign_with: str | None = None,
        broadcast: bool = True,  # noqa: FBT001
        save_file: str | None = None,
    ) -> Transaction:

        transfer_operation = TransferOperation(
                from_=from_account,
                to=to,
                amount=Asset.from_legacy(amount),
                memo=memo,
            )
        
        return (await self.clive.world.commands.perform_actions_on_transaction(
                content=transfer_operation,
                broadcast=broadcast,
            )).result_or_raise
