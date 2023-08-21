from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Generic, TypeVar, overload

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
from clive.__private.core.commands.save_json import SaveToFileAsJson
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.commands.sign import Sign
from clive.__private.core.commands.sync_data_with_beekeeper import SyncDataWithBeekeeper
from clive.__private.core.commands.update_node_data import DynamicGlobalPropertiesT, UpdateNodeData
from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
    ResultNotAvailable,
)
from clive.__private.core.error_handlers.async_closed import AsyncClosedErrorHandler
from clive.__private.core.error_handlers.communication_failure_notificator import CommunicationFailureNotificator
from clive.__private.core.error_handlers.general_error_notificator import GeneralErrorNotificator
from clive.__private.ui.widgets.clive_widget import CliveWidget

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.commands.abc.command import Command
    from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
        ErrorHandlerContextManager,
    )
    from clive.__private.core.keys import PrivateKeyAliased, PublicKey, PublicKeyAliased
    from clive.__private.core.world import TextualWorld, World
    from clive.__private.storage.accounts import Account
    from clive.models import Operation, Transaction


WorldT = TypeVar("WorldT", bound="World")


class Commands(Generic[WorldT]):
    def __init__(
        self, world: WorldT, *, exception_handlers: list[type[ErrorHandlerContextManager]] | None = None
    ) -> None:
        self._world = world
        self.__exception_handlers = [AsyncClosedErrorHandler, *(exception_handlers or [])]

    async def activate(self, *, password: str, time: timedelta | None = None) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            Activate(
                app_state=self._world.app_state,
                beekeeper=self._world.beekeeper,
                wallet=self._world.profile_data.name,
                password=password,
                time=time,
            )
        )

    async def deactivate(self) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            Deactivate(
                app_state=self._world.app_state,
                beekeeper=self._world.beekeeper,
                wallet=self._world.profile_data.name,
            )
        )

    async def set_timeout(self, *, seconds: int) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            SetTimeout(beekeeper=self._world.beekeeper, seconds=seconds)
        )

    async def build_transaction(
        self, *, operations: list[Operation], expiration: timedelta = timedelta(minutes=30)
    ) -> CommandWithResultWrapper[Transaction]:
        return await self.__surround_with_exception_handlers(
            BuildTransaction(operations=operations, node=self._world.node, expiration=expiration)
        )

    async def sign(self, *, transaction: Transaction, sign_with: PublicKey) -> CommandWithResultWrapper[Transaction]:
        return await self.__surround_with_exception_handlers(
            Sign(
                app_state=self._world.app_state,
                beekeeper=self._world.beekeeper,
                transaction=transaction,
                key=sign_with,
                chain_id=await self._world.node.chain_id,
            )
        )

    async def save_to_file(self, *, transaction: Transaction, path: Path, binary: bool = False) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            SaveToFileAsBinary(transaction=transaction, file_path=path)
            if binary
            else SaveToFileAsJson(transaction=transaction, file_path=path)
        )

    async def broadcast(self, *, transaction: Transaction) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(Broadcast(node=self._world.node, transaction=transaction))

    async def fast_broadcast(self, *, operation: Operation, sign_with: PublicKey) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            FastBroadcast(
                app_state=self._world.app_state,
                node=self._world.node,
                operation=operation,
                beekeeper=self._world.beekeeper,
                sign_with=sign_with,
                chain_id=await self._world.node.chain_id,
            )
        )

    async def import_key(self, *, key_to_import: PrivateKeyAliased) -> CommandWithResultWrapper[PublicKeyAliased]:
        return await self.__surround_with_exception_handlers(
            ImportKey(
                app_state=self._world.app_state,
                wallet=self._world.profile_data.name,
                key_to_import=key_to_import,
                beekeeper=self._world.beekeeper,
            )
        )

    async def remove_key(self, *, password: str, key_to_remove: PublicKey) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            RemoveKey(
                app_state=self._world.app_state,
                wallet=self._world.profile_data.name,
                beekeeper=self._world.beekeeper,
                key_to_remove=key_to_remove,
                password=password,
            )
        )

    async def sync_data_with_beekeeper(self) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            SyncDataWithBeekeeper(
                app_state=self._world.app_state,
                profile_data=self._world.profile_data,
                beekeeper=self._world.beekeeper,
            )
        )

    async def update_node_data(
        self, *, accounts: list[Account] | None = None
    ) -> CommandWithResultWrapper[DynamicGlobalPropertiesT]:
        result = await self.__surround_with_exception_handlers(
            UpdateNodeData(accounts=accounts or [], node=self._world.node)
        )
        if result.success:
            self._world.app_state._dynamic_global_properties = result.result_or_raise
        return result

    @overload
    async def __surround_with_exception_handlers(  # type: ignore[misc]
        self, command: CommandWithResult[CommandResultT]
    ) -> CommandWithResultWrapper[CommandResultT]:
        ...

    @overload
    async def __surround_with_exception_handlers(self, command: Command) -> CommandWrapper:
        ...

    async def __surround_with_exception_handlers(
        self, command: CommandWithResult[CommandResultT] | Command
    ) -> CommandWithResultWrapper[CommandResultT] | CommandWrapper:
        if not self.__exception_handlers:
            if isinstance(command, CommandWithResult):
                await command.execute_with_result()
            else:
                await command.execute()

            return self.__create_command_wrapper(command)

        return await self.__surround_with_exception_handler(command, self.__exception_handlers)  # type: ignore[arg-type]

    @overload
    async def __surround_with_exception_handler(  # type: ignore[misc]
        self,
        command: CommandWithResult[CommandResultT],
        exception_handlers: list[type[ErrorHandlerContextManager]],
        error: Exception | None = None,
    ) -> CommandWithResultWrapper[CommandResultT]:
        ...

    @overload
    async def __surround_with_exception_handler(
        self,
        command: Command,
        exception_handlers: list[type[ErrorHandlerContextManager]],
        error: Exception | None = None,
    ) -> CommandWrapper:
        ...

    async def __surround_with_exception_handler(
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
                await handler.try_to_handle_error(error)
            else:
                # exectue the command only once
                await handler.execute(
                    command.execute_with_result() if isinstance(command, CommandWithResult) else command.execute(),
                )
        except Exception as error:  # noqa: BLE001
            # Try to handle the error with the next exception handler
            return await self.__surround_with_exception_handler(command, exception_handlers[1:], error)
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


class TextualCommands(Commands["TextualWorld"], CliveWidget):
    def __init__(self, world: TextualWorld) -> None:
        super().__init__(world, exception_handlers=[CommunicationFailureNotificator, GeneralErrorNotificator])

    async def activate(self, *, password: str, time: timedelta | None = None) -> CommandWrapper:
        wrapper = await super().activate(password=password, time=time)
        self._world.update_reactive("app_state")
        return wrapper

    async def deactivate(self) -> CommandWrapper:
        wrapper = await super().deactivate()
        self._world.update_reactive("app_state")
        self.app.switch_screen("dashboard_inactive")
        return wrapper
