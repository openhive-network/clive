from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, ClassVar

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command import Command
from clive.__private.core.commands.unsign import UnSign
from clive.__private.models.schemas import HiveInt

if TYPE_CHECKING:
    from clive.__private.core.node import Node
    from clive.__private.models.transaction import Transaction


@dataclass(kw_only=True)
class UpdateTransactionMetadata(Command):
    DEFAULT_GDPO_TIME_RELATIVE_EXPIRATION: ClassVar[timedelta] = timedelta(minutes=30)

    transaction: Transaction
    node: Node
    expiration: timedelta = DEFAULT_GDPO_TIME_RELATIVE_EXPIRATION
    """Expiration relative to the gdpo time."""

    async def _execute(self) -> None:
        # clear existing signatures
        self.transaction = await UnSign(transaction=self.transaction).execute_with_result()

        # get dynamic global properties
        gdpo = await self.node.api.database_api.get_dynamic_global_properties()
        block_id = gdpo.head_block_id

        # set header
        tapos_data = iwax.get_tapos_data(block_id)
        ref_block_num = tapos_data.ref_block_num
        ref_block_prefix = tapos_data.ref_block_prefix

        assert ref_block_num >= 0, f"ref_block_num value `{ref_block_num}` is invalid`"
        assert ref_block_prefix > 0, f"ref_block_prefix value `{ref_block_prefix}` is invalid`"

        self.transaction.ref_block_num = HiveInt(ref_block_num)
        self.transaction.ref_block_prefix = HiveInt(ref_block_prefix)

        # set expiration
        self.transaction.expiration = gdpo.time + self.expiration
