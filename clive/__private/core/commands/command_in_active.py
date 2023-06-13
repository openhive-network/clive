from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.activate import Activate, WalletDoesNotExistsError
from clive.__private.core.commands.command import Command, CommandT
from clive.__private.core.commands.create_wallet import CreateWallet

if TYPE_CHECKING:
    from clive.__private.core.app_state import AppState
    from clive.__private.core.beekeeper import Beekeeper


@dataclass
class CommandInActive(Command[CommandT], ABC):
    """
    CommandInActive is an abstract class that defines a common interface for executing commands that require the
    application to be in active mode. If the application is not in active mode, the command will try to activate
    and then execute the command.
    """

    app_state: AppState
    beekeeper: Beekeeper
    wallet: str
    password: str

    def execute(self) -> None:
        if not self.app_state.is_active():
            self.__activate()
            self.execute()
        self._execute()

    def __activate(self) -> None:
        try:
            Activate(beekeeper=self.beekeeper, wallet=self.wallet, password=self.password).execute()
        except WalletDoesNotExistsError:
            self.password = CreateWallet(
                beekeeper=self.beekeeper, wallet=self.wallet, password=self.password
            ).execute_with_result()
