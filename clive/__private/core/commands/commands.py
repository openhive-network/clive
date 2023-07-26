from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, overload

from clive.__private.core.commands.abc.command_with_result import CommandResultT, CommandWithResult
from clive.__private.core.commands.activate import Activate
from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.build_transaction import BuildTransaction
from clive.__private.core.commands.command_wrappers import CommandWithResultWrapper, CommandWrapper
from clive.__private.core.commands.deactivate import Deactivate
from clive.__private.core.commands.fast_broadcast import FastBroadcast
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.commands.remove_key import RemoveKey
from clive.__private.core.commands.save_binary import SaveToFileAsBinary
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.commands.sign import Sign
from clive.__private.core.commands.sync_data_with_beekeeper import SyncDataWithBeekeeper
from clive.__private.core.commands.update_node_data import UpdateNodeData
from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
    ResultNotAvailable,
)

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.commands.abc.command import Command
    from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
        ErrorHandlerContextManager,
    )
    from clive.__private.core.keys import PrivateKeyAliased, PublicKey, PublicKeyAliased
    from clive.__private.core.world import World
    from clive.__private.storage.mock_database import Account
    from clive.models import Operation, Transaction


class Commands:
    def __init__(
        self, world: World, *, exception_handlers: list[type[ErrorHandlerContextManager]] | None = None
    ) -> None:
        self.__world = world
        self.__exception_handlers = exception_handlers

    def activate(self, *, password: str, time: timedelta | None = None) -> CommandWrapper:
        return self.__surround_with_exception_handlers(
            Activate(
                beekeeper=self.__world.beekeeper, wallet=self.__world.profile_data.name, password=password, time=time
            )
        )

    def deactivate(self) -> CommandWrapper:
        return self.__surround_with_exception_handlers(
            Deactivate(beekeeper=self.__world.beekeeper, wallet=self.__world.profile_data.name)
        )

    def set_timeout(self, *, seconds: int) -> CommandWrapper:
        return self.__surround_with_exception_handlers(SetTimeout(beekeeper=self.__world.beekeeper, seconds=seconds))

    def build_transaction(
        self, *, operations: list[Operation], expiration: timedelta = timedelta(minutes=30)
    ) -> CommandWithResultWrapper[Transaction]:
        return self.__surround_with_exception_handlers(
            BuildTransaction(operations=operations, node=self.__world.node, expiration=expiration)
        )

    def sign(self, *, transaction: Transaction, sign_with: PublicKey) -> CommandWithResultWrapper[Transaction]:
        return self.__surround_with_exception_handlers(
            Sign(
                beekeeper=self.__world.beekeeper,
                transaction=transaction,
                key=sign_with,
                chain_id=self.__world.node.chain_id,
            )
        )

    def save_to_file(self, *, transaction: Transaction, path: Path) -> CommandWrapper:
        return self.__surround_with_exception_handlers(SaveToFileAsBinary(transaction=transaction, file_path=path))

    def broadcast(self, *, transaction: Transaction) -> CommandWrapper:
        return self.__surround_with_exception_handlers(Broadcast(node=self.__world.node, transaction=transaction))

    def fast_broadcast(self, *, operation: Operation, sign_with: PublicKey) -> CommandWrapper:
        return self.__surround_with_exception_handlers(
            FastBroadcast(
                node=self.__world.node,
                operation=operation,
                beekeeper=self.__world.beekeeper,
                sign_with=sign_with,
                chain_id=self.__world.node.chain_id,
            )
        )

    def import_key(self, *, key_to_import: PrivateKeyAliased) -> CommandWithResultWrapper[PublicKeyAliased]:
        return self.__surround_with_exception_handlers(
            ImportKey(
                app_state=self.__world.app_state,
                wallet=self.__world.profile_data.name,
                key_to_import=key_to_import,
                beekeeper=self.__world.beekeeper,
            )
        )

    def remove_key(self, *, password: str, key_to_remove: PublicKey) -> CommandWrapper:
        return self.__surround_with_exception_handlers(
            RemoveKey(
                app_state=self.__world.app_state,
                wallet=self.__world.profile_data.name,
                beekeeper=self.__world.beekeeper,
                key_to_remove=key_to_remove,
                password=password,
            )
        )

    def sync_data_with_beekeeper(self) -> CommandWrapper:
        return self.__surround_with_exception_handlers(
            SyncDataWithBeekeeper(
                app_state=self.__world.app_state,
                profile_data=self.__world.profile_data,
                beekeeper=self.__world.beekeeper,
            )
        )

    def update_node_data(self, *, accounts: list[Account] | None = None) -> CommandWrapper:
        wrapper = self.__surround_with_exception_handlers(
            UpdateNodeData(accounts=accounts or [], node=self.__world.node)
        )

        if wrapper.error_occurred:
            return CommandWrapper(command=wrapper.command, error=wrapper.error)

        self.__world.app_state._dynamic_global_properties = wrapper.result_or_raise
        return CommandWrapper(command=wrapper.command)

    @overload
    def __surround_with_exception_handlers(  # type: ignore[misc]
        self, command: CommandWithResult[CommandResultT]
    ) -> CommandWithResultWrapper[CommandResultT]:
        ...

    @overload
    def __surround_with_exception_handlers(self, command: Command) -> CommandWrapper:
        ...

    def __surround_with_exception_handlers(
        self, command: CommandWithResult[CommandResultT] | Command
    ) -> CommandWithResultWrapper[CommandResultT] | CommandWrapper:
        if not self.__exception_handlers:
            if isinstance(command, CommandWithResult):
                command.execute_with_result()
            else:
                command.execute()
            return self.__create_command_wrapper(command)

        return self.__surround_with_exception_handler(command, self.__exception_handlers)

    @overload
    def __surround_with_exception_handler(  # type: ignore[misc]
        self,
        command: CommandWithResult[CommandResultT],
        exception_handlers: list[type[ErrorHandlerContextManager]],
        error: Exception | None = None,
    ) -> CommandWithResultWrapper[CommandResultT]:
        ...

    @overload
    def __surround_with_exception_handler(
        self,
        command: Command,
        exception_handlers: list[type[ErrorHandlerContextManager]],
        error: Exception | None = None,
    ) -> CommandWrapper:
        ...

    def __surround_with_exception_handler(
        self,
        command: Command | CommandWithResult[CommandResultT],
        exception_handlers: list[type[ErrorHandlerContextManager]],
        error: Exception | None = None,
    ) -> CommandWrapper | CommandWithResultWrapper[CommandResultT]:
        try:
            next_exception_handler = exception_handlers[0]
        except IndexError:
            # No more exception handlers
            assert error is not None
            raise error

        handler = next_exception_handler()

        try:
            if error:
                handler.try_to_handle_error(error)
            else:
                # exectue the command only once
                handler.execute(
                    command.execute_with_result if isinstance(command, CommandWithResult) else command.execute
                )
        except Exception as error:  # noqa: BLE001
            # Try to handle the error with the next exception handler
            assert self.__exception_handlers
            self.__surround_with_exception_handler(command, self.__exception_handlers[1:], error)

        return self.__create_command_wrapper(command, handler.error)

    @overload
    def __create_command_wrapper(  # type: ignore[misc]
        self, command: CommandWithResult[CommandResultT], error: Exception | None = None
    ) -> CommandWithResultWrapper[CommandResultT]:
        ...

    @overload
    def __create_command_wrapper(self, command: Command, error: Exception | None = None) -> CommandWrapper:
        ...

    def __create_command_wrapper(
        self, command: Command | CommandWithResult[CommandResultT], error: Exception | None = None
    ) -> CommandWrapper | CommandWithResultWrapper[CommandResultT]:
        if isinstance(command, CommandWithResult):
            result = command.result if error is None else ResultNotAvailable(exception=error)
            return CommandWithResultWrapper(command=command, result=result, error=error)
        return CommandWrapper(command=command, error=error)
