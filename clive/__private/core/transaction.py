from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clive.models.operation import Operation


class Transaction:
    def __init__(self) -> None:
        self.__operations: list[Operation] = []

    def __len__(self) -> int:
        return len(self.__operations)

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
