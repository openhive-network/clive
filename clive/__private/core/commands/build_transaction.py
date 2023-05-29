from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import TYPE_CHECKING, Final

from clive.__private.core.commands.command import Command
from clive.models import Transaction

if TYPE_CHECKING:
    from clive.__private.core.node.node import Node
    from clive.models import Operation


@dataclass
class BuildTransaction(Command[Transaction]):
    operations: list[Operation]
    node: Node
    expiration: timedelta = timedelta(minutes=30)

    def execute(self) -> None:
        self._result = Transaction(operations=self.operations)

        # get dynamic global properties
        gdpo = self.node.api.database_api.get_dynamic_global_properties()

        # set header
        block_id = gdpo.head_block_id
        block_id_hash = self.__convert_block_id_to_ripmed160_hash_table(block_id)
        self._result.ref_block_num = self.__swap_u32(block_id_hash[0])  # type: ignore[assignment]
        self._result.ref_block_prefix = block_id_hash[1]  # type: ignore[assignment]

        # set expiration
        self._result.expiration = gdpo.time + self.expiration

    @classmethod
    def __swap_u32(cls, x: int) -> int:
        # source: https://stackoverflow.com/a/35906430/11738218
        return int.from_bytes(x.to_bytes(4, byteorder="little"), byteorder="big", signed=False)

    @classmethod
    def __convert_block_id_to_ripmed160_hash_table(cls, block_id: str) -> tuple[int, int, int, int, int]:
        return tuple(  # type: ignore[return-value]
            [
                int.from_bytes(bytes.fromhex(chunk), byteorder="little", signed=False)
                for chunk in cls.__split_block_id(block_id)
            ]
        )

    @classmethod
    def __split_block_id(cls, block_id: str) -> tuple[str, str, str, str, str]:
        amount_of_uint32t_chunks: Final[int] = 5
        length_of_block_id: Final[int] = len(block_id)
        chars_per_chunk: Final[int] = int(length_of_block_id / amount_of_uint32t_chunks)
        return tuple([block_id[i : i + chars_per_chunk] for i in range(0, length_of_block_id, chars_per_chunk)])  # type: ignore[return-value]
