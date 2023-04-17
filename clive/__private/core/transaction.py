from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from clive.__private.logger import logger

if TYPE_CHECKING:
    from clive.__private.storage.mock_database import PrivateKey
    from clive.models.operation import Operation


class Transaction:
    def __init__(self) -> None:
        self.__operations: list[Operation] = []
        self.__signatures: list[PrivateKey] = []

    def __len__(self) -> int:
        return len(self.__operations)

    def __str__(self) -> str:
        return f"Transaction(operations={self.__operations})"

    @property
    def operations(self) -> list[Operation]:
        """Get the copy of the operations list"""
        return self.__operations.copy()

    def add(self, *operations: Operation) -> None:
        self.__operations.extend(operations)

    def remove(self, *operations: Operation) -> None:
        for operation in operations:
            self.__operations.remove(operation)

    def clear(self) -> None:
        self.__operations.clear()

    def get(self, index: int) -> Operation:
        return self.__operations[index]

    def swap_order(self, index1: int, index2: int) -> None:
        self.__operations[index1], self.__operations[index2] = self.__operations[index2], self.__operations[index1]

    def broadcast(self) -> None:
        logger.info(f"Broadcasting transaction: {self}")

    def sign(self, key: PrivateKey) -> None:
        self.__signatures.append(key)
        logger.info(f"Signed {self} with key: {key.key_name}")

    def save_to_file(self, file_path: Path) -> None:
        logger.info(f"Saving transaction to file: {file_path}")
        with Path(file_path).open("w") as file:
            json.dump(
                self.__get_transaction_file_format(),
                file,
                default=vars,
            )

    def __get_transaction_file_format(self) -> dict[str, Any]:
        return {
            "ops_in_trx": self.operations,
            "signatures": self.__signatures,
        }
