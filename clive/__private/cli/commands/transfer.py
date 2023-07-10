from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.models import Asset
from schemas.__private.hive_fields_basic_schemas import AssetHbdHF26, AssetHiveHF26
from schemas.__private.operations import TransferOperation


@dataclass(kw_only=True)
class Transfer(OperationCommand):
    to: str
    amount: str
    memo: str

    def _create_operation(self) -> TransferOperation[AssetHiveHF26, AssetHbdHF26]:
        return TransferOperation(
            from_=self.world.profile_data.working_account.name,
            to=self.to,
            amount=Asset.from_legacy(self.amount.upper()),
            memo=self.memo,
        )
