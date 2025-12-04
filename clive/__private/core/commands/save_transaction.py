from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Literal

from clive.__private.core import iwax
from clive.__private.core.commands.abc.command import Command
from clive.__private.core.constants.data_retrieval import DEFAULT_SERIALIZATION_MODE

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.types import SerializationMode
    from clive.__private.models.transaction import Transaction


@dataclass(kw_only=True)
class SaveTransaction(Command):
    transaction: Transaction
    file_path: Path
    serialization_mode: SerializationMode = DEFAULT_SERIALIZATION_MODE
    force_format: Literal["json", "bin"] | None = None
    """If not provided, the format will be determined by the file extension automatically."""

    async def _execute(self) -> None:
        if self.serialization_mode == "legacy":
            raise NotImplementedError("Legacy serialization mode is not yet implemented for saving transactions.")

        if self.force_format == "json":
            self.__save_as_json()
        elif self.force_format == "bin":
            self.__save_as_binary()
        else:
            self.__save_as_binary() if self.__should_save_as_binary() else self.__save_as_json()

    def __save_as_json(self) -> None:
        serialized = self.transaction.json(
            order="sorted",
            indent=4,
        )
        self.file_path.write_text(serialized)

    def __save_as_binary(self) -> None:
        serialized = iwax.serialize_transaction(self.transaction)
        self.file_path.write_bytes(serialized)

    def __should_save_as_binary(self) -> bool:
        return self.file_path.suffix in (".bin", ".binary")
