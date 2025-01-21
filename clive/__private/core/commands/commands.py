from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generic, Iterable, Literal, TypeVar, overload

from clive.__private.core.commands.abc.command_with_result import CommandResultT, CommandWithResult
from clive.__private.core.commands.broadcast import Broadcast
from clive.__private.core.commands.build_transaction import BuildTransaction
from clive.__private.core.commands.command_wrappers import CommandWithResultWrapper, CommandWrapper
from clive.__private.core.commands.create_wallet import CreateWallet
from clive.__private.core.commands.data_retrieval.chain_data import ChainData, ChainDataRetrieval
from clive.__private.core.commands.data_retrieval.find_scheduled_transfers import (
    AccountScheduledTransferData,
    FindScheduledTransfers,
)
from clive.__private.core.commands.data_retrieval.find_vesting_delegation_expirations import (
    FindVestingDelegationExpirations,
    VestingDelegationExpirationData,
)
from clive.__private.core.commands.data_retrieval.get_dynamic_global_properties import GetDynamicGlobalProperties
from clive.__private.core.commands.data_retrieval.hive_power_data import HivePowerData, HivePowerDataRetrieval
from clive.__private.core.commands.data_retrieval.proposals_data import ProposalsData, ProposalsDataRetrieval
from clive.__private.core.commands.data_retrieval.savings_data import SavingsData, SavingsDataRetrieval
from clive.__private.core.commands.data_retrieval.update_alarms_data import UpdateAlarmsData
from clive.__private.core.commands.data_retrieval.update_node_data import UpdateNodeData
from clive.__private.core.commands.data_retrieval.witnesses_data import (
    WitnessesData,
    WitnessesDataRetrieval,
)
from clive.__private.core.commands.does_account_exist_in_node import DoesAccountExistsInNode
from clive.__private.core.commands.find_accounts import FindAccounts
from clive.__private.core.commands.find_proposal import FindProposal
from clive.__private.core.commands.find_transaction import FindTransaction
from clive.__private.core.commands.find_witness import FindWitness
from clive.__private.core.commands.get_unlocked_profile_name import GetUnlockedWallet
from clive.__private.core.commands.get_wallet_names import GetWalletNames, WalletStatus
from clive.__private.core.commands.import_key import ImportKey
from clive.__private.core.commands.is_password_valid import IsPasswordValid
from clive.__private.core.commands.load_transaction import LoadTransaction
from clive.__private.core.commands.lock import Lock
from clive.__private.core.commands.lock_all import LockAll
from clive.__private.core.commands.perform_actions_on_transaction import PerformActionsOnTransaction
from clive.__private.core.commands.remove_key import RemoveKey
from clive.__private.core.commands.save_transaction import SaveTransaction
from clive.__private.core.commands.set_timeout import SetTimeout
from clive.__private.core.commands.sign import ALREADY_SIGNED_MODE_DEFAULT, AlreadySignedMode, Sign
from clive.__private.core.commands.sync_data_with_beekeeper import SyncDataWithBeekeeper
from clive.__private.core.commands.sync_state_with_beekeeper import SyncStateWithBeekeeper
from clive.__private.core.commands.unlock import Unlock
from clive.__private.core.commands.unsign import UnSign
from clive.__private.core.commands.update_transaction_metadata import (
    UpdateTransactionMetadata,
)
from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
    ResultNotAvailable,
)
from clive.__private.core.error_handlers.communication_failure_notificator import CommunicationFailureNotificator
from clive.__private.core.error_handlers.general_error_notificator import GeneralErrorNotificator
from clive.__private.ui.clive_dom_node import CliveDOMNode

if TYPE_CHECKING:
    from datetime import timedelta
    from pathlib import Path

    from beekeepy import AsyncUnlockedWallet

    from clive.__private.core.accounts.accounts import TrackedAccount
    from clive.__private.core.app_state import LockSource
    from clive.__private.core.commands.abc.command import Command
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.error_handlers.abc.error_handler_context_manager import (
        AnyErrorHandlerContextManager,
    )
    from clive.__private.core.keys import PrivateKeyAliased, PublicKey, PublicKeyAliased
    from clive.__private.core.world import CLIWorld, TUIWorld, World
    from clive.__private.models import Transaction
    from clive.__private.models.schemas import (
        Account,
        DynamicGlobalProperties,
        Proposal,
        TransactionStatus,
        Witness,
    )

WorldT_co = TypeVar("WorldT_co", bound="World", covariant=True)


class Commands(Generic[WorldT_co]):
    def __init__(
        self,
        world: WorldT_co,
        exception_handlers: list[type[AnyErrorHandlerContextManager]] | None = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        # Multiple inheritance friendly, passes arguments to next object in MRO.
        super().__init__(*args, **kwargs)

        self._world = world
        self.__exception_handlers = [*(exception_handlers or [])]

    async def create_wallet(self, *, password: str | None) -> CommandWithResultWrapper[str]:
        return await self.__surround_with_exception_handlers(
            CreateWallet(
                app_state=self._world.app_state,
                session=self._world.session,
                wallet_name=self._world.profile.name,
                password=password,
                world=self._world,
            )
        )

    async def does_account_exists_in_node(self, *, account_name: str) -> CommandWithResultWrapper[bool]:
        return await self.__surround_with_exception_handlers(
            DoesAccountExistsInNode(node=self._world.node, account_name=account_name)
        )

    async def unlock(
        self, *, profile_name: str | None = None, password: str, time: timedelta | None = None, permanent: bool = False
    ) -> CommandWrapper:
        """
        Return a CommandWrapper instance to unlock the wallet with given parameters.

        Args:
        ----
        profile_name: Name of the wallet to unlock. If None, the world wallet will be unlocked.
        password: Password to unlock the wallet.
        time: Time to unlock the wallet. Do not need to pass when unlocking permanently.
        permanent: Whether to unlock the wallet permanently.
        """
        return await self.__surround_with_exception_handlers(
            Unlock(
                password=password,
                app_state=self._world.app_state,
                session=self._world.session,
                wallet_name=profile_name or self._world.profile.name,
                time=time,
                permanent=permanent,
                world=self._world,
            )
        )

    async def lock(self) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            Lock(
                app_state=self._world.app_state,
                wallet=self._world.wallet,
            )
        )

    async def lock_all(self) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            LockAll(
                app_state=self._world.app_state,
                session=self._world.session,
            )
        )

    async def get_unlocked_profile_name(self) -> CommandWithResultWrapper[AsyncUnlockedWallet]:
        return await self.__surround_with_exception_handlers(GetUnlockedWallet(session=self._world.session))

    async def get_wallet_names(self, filter_by_status: WalletStatus = "all") -> CommandWithResultWrapper[list[str]]:
        return await self.__surround_with_exception_handlers(
            GetWalletNames(session=self._world.session, filter_by_status=filter_by_status)
        )

    async def is_password_valid(self, *, password: str) -> CommandWithResultWrapper[bool]:
        return await self.__surround_with_exception_handlers(
            IsPasswordValid(
                beekeeper=self._world.beekeeper,
                wallet=self._world.profile.name,
                password=password,
            )
        )

    async def set_timeout(self, *, seconds: int) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(SetTimeout(session=self._world.session, seconds=seconds))

    async def perform_actions_on_transaction(  # noqa: PLR0913
        self,
        *,
        content: TransactionConvertibleType,
        sign_key: PublicKey | None = None,
        already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT,
        force_unsign: bool = False,
        chain_id: str | None = None,
        save_file_path: Path | None = None,
        force_save_format: Literal["json", "bin"] | None = None,
        broadcast: bool = False,
    ) -> CommandWithResultWrapper[Transaction]:
        return await self.__surround_with_exception_handlers(
            PerformActionsOnTransaction(
                content=content,
                app_state=self._world.app_state,
                node=self._world.node,
                wallet=self._world.wallet if sign_key else None,
                sign_key=sign_key,
                already_signed_mode=already_signed_mode,
                force_unsign=force_unsign,
                chain_id=chain_id,
                save_file_path=save_file_path,
                force_save_format=force_save_format,
                broadcast=broadcast,
            )
        )

    async def build_transaction(
        self,
        *,
        content: TransactionConvertibleType,
        force_update_metadata: bool = BuildTransaction.DEFAULT_FORCE_UPDATE_METADATA,
    ) -> CommandWithResultWrapper[Transaction]:
        return await self.__surround_with_exception_handlers(
            BuildTransaction(
                content=content,
                force_update_metadata=force_update_metadata,
                node=self._world.node,
            )
        )

    async def update_transaction_metadata(
        self,
        *,
        transaction: Transaction,
        expiration: timedelta = UpdateTransactionMetadata.DEFAULT_GDPO_TIME_RELATIVE_EXPIRATION,
    ) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            UpdateTransactionMetadata(
                transaction=transaction,
                node=self._world.node,
                expiration=expiration,
            )
        )

    async def sign(
        self,
        *,
        transaction: Transaction,
        sign_with: PublicKey,
        already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT,
        chain_id: str | None = None,
    ) -> CommandWithResultWrapper[Transaction]:
        return await self.__surround_with_exception_handlers(
            Sign(
                wallet=self._world.wallet,
                transaction=transaction,
                key=sign_with,
                chain_id=chain_id or await self._world.node.chain_id,
                already_signed_mode=already_signed_mode,
            )
        )

    async def unsign(self, *, transaction: Transaction) -> CommandWithResultWrapper[Transaction]:
        return await self.__surround_with_exception_handlers(
            UnSign(
                transaction=transaction,
            )
        )

    async def save_to_file(
        self, *, transaction: Transaction, path: Path, force_format: Literal["json", "bin"] | None = None
    ) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            SaveTransaction(transaction=transaction, file_path=path, force_format=force_format)
        )

    async def load_transaction_from_file(self, *, path: Path) -> CommandWithResultWrapper[Transaction]:
        return await self.__surround_with_exception_handlers(LoadTransaction(file_path=path))

    async def broadcast(self, *, transaction: Transaction) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(Broadcast(node=self._world.node, transaction=transaction))

    async def import_key(self, *, key_to_import: PrivateKeyAliased) -> CommandWithResultWrapper[PublicKeyAliased]:
        return await self.__surround_with_exception_handlers(
            ImportKey(
                wallet=self._world.wallet,
                key_to_import=key_to_import,
            )
        )

    async def remove_key(self, *, key_to_remove: PublicKey) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            RemoveKey(
                wallet=self._world.wallet,
                key_to_remove=key_to_remove,
            )
        )

    async def sync_data_with_beekeeper(self) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            SyncDataWithBeekeeper(
                wallet=self._world.wallet,
                profile=self._world.profile,
            )
        )

    async def sync_state_with_beekeeper(self, source: LockSource = "unknown") -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            SyncStateWithBeekeeper(wallet=self._world._optional_wallet, app_state=self._world.app_state, source=source)
        )

    async def get_dynamic_global_properties(self) -> CommandWithResultWrapper[DynamicGlobalProperties]:
        result = await self.__surround_with_exception_handlers(GetDynamicGlobalProperties(node=self._world.node))
        if result.success:
            await self._world.node.cached.update_dynamic_global_properties(result.result_or_raise)
        return result

    async def update_node_data(
        self, *, accounts: Iterable[TrackedAccount] | None = None
    ) -> CommandWithResultWrapper[DynamicGlobalProperties]:
        result = await self.__surround_with_exception_handlers(
            UpdateNodeData(accounts=list(accounts or []), node=self._world.node)
        )
        if result.success:
            await self._world.node.cached.update_dynamic_global_properties(result.result_or_raise)
        return result

    async def update_alarms_data(self, *, accounts: Iterable[TrackedAccount] | None = None) -> CommandWrapper:
        return await self.__surround_with_exception_handlers(
            UpdateAlarmsData(accounts=list(accounts) if accounts is not None else [], node=self._world.node)
        )

    async def retrieve_savings_data(self, *, account_name: str) -> CommandWithResultWrapper[SavingsData]:
        return await self.__surround_with_exception_handlers(
            SavingsDataRetrieval(node=self._world.node, account_name=account_name)
        )

    async def retrieve_witnesses_data(
        self,
        *,
        account_name: str,
        mode: WitnessesDataRetrieval.Modes = WitnessesDataRetrieval.DEFAULT_MODE,
        witness_name_pattern: str | None = None,
        search_by_name_limit: int = WitnessesDataRetrieval.DEFAULT_SEARCH_BY_NAME_LIMIT,
    ) -> CommandWithResultWrapper[WitnessesData]:
        return await self.__surround_with_exception_handlers(
            WitnessesDataRetrieval(
                node=self._world.node,
                account_name=account_name,
                mode=mode,
                witness_name_pattern=witness_name_pattern,
                search_by_pattern_limit=search_by_name_limit,
            )
        )

    async def retrieve_proposals_data(
        self,
        *,
        account_name: str,
        order: ProposalsDataRetrieval.Orders = ProposalsDataRetrieval.DEFAULT_ORDER,
        order_direction: ProposalsDataRetrieval.OrderDirections = ProposalsDataRetrieval.DEFAULT_ORDER_DIRECTION,
        status: ProposalsDataRetrieval.Statuses = ProposalsDataRetrieval.DEFAULT_STATUS,
    ) -> CommandWithResultWrapper[ProposalsData]:
        return await self.__surround_with_exception_handlers(
            ProposalsDataRetrieval(
                node=self._world.node,
                account_name=account_name,
                order=order,
                order_direction=order_direction,
                status=status,
            )
        )

    async def retrieve_hp_data(
        self,
        *,
        account_name: str,
    ) -> CommandWithResultWrapper[HivePowerData]:
        return await self.__surround_with_exception_handlers(
            HivePowerDataRetrieval(node=self._world.node, account_name=account_name)
        )

    async def retrieve_chain_data(self) -> CommandWithResultWrapper[ChainData]:
        return await self.__surround_with_exception_handlers(ChainDataRetrieval(node=self._world.node))

    async def find_transaction(self, *, transaction_id: str) -> CommandWithResultWrapper[TransactionStatus]:
        return await self.__surround_with_exception_handlers(
            FindTransaction(node=self._world.node, transaction_id=transaction_id)
        )

    async def find_witness(self, *, witness_name: str) -> CommandWithResultWrapper[Witness]:
        return await self.__surround_with_exception_handlers(
            FindWitness(node=self._world.node, witness_name=witness_name)
        )

    async def find_proposal(self, *, proposal_id: int) -> CommandWithResultWrapper[Proposal]:
        return await self.__surround_with_exception_handlers(
            FindProposal(node=self._world.node, proposal_id=proposal_id)
        )

    async def find_accounts(self, *, accounts: list[str]) -> CommandWithResultWrapper[list[Account]]:
        return await self.__surround_with_exception_handlers(FindAccounts(node=self._world.node, accounts=accounts))

    async def find_vesting_delegation_expirations(
        self, *, account: str
    ) -> CommandWithResultWrapper[list[VestingDelegationExpirationData]]:
        return await self.__surround_with_exception_handlers(
            FindVestingDelegationExpirations(node=self._world.node, account=account)
        )

    async def find_scheduled_transfers(
        self, *, account_name: str
    ) -> CommandWithResultWrapper[AccountScheduledTransferData]:
        return await self.__surround_with_exception_handlers(
            FindScheduledTransfers(node=self._world.node, account_name=account_name)
        )

    @overload
    async def __surround_with_exception_handlers(  # type: ignore[overload-overlap]
        self, command: CommandWithResult[CommandResultT]
    ) -> CommandWithResultWrapper[CommandResultT]: ...

    @overload
    async def __surround_with_exception_handlers(self, command: Command) -> CommandWrapper: ...

    async def __surround_with_exception_handlers(
        self, command: CommandWithResult[CommandResultT] | Command
    ) -> CommandWithResultWrapper[CommandResultT] | CommandWrapper:
        if not self.__exception_handlers:
            if isinstance(command, CommandWithResult):
                await command.execute_with_result()
            else:
                await command.execute()

            return self.__create_command_wrapper(command)

        return await self.__surround_with_exception_handler(command, self.__exception_handlers)

    @overload
    async def __surround_with_exception_handler(  # type: ignore[overload-overlap]
        self,
        command: CommandWithResult[CommandResultT],
        exception_handlers: list[type[AnyErrorHandlerContextManager]],
        error: Exception | None = None,
    ) -> CommandWithResultWrapper[CommandResultT]: ...

    @overload
    async def __surround_with_exception_handler(
        self,
        command: Command,
        exception_handlers: list[type[AnyErrorHandlerContextManager]],
        error: Exception | None = None,
    ) -> CommandWrapper: ...

    async def __surround_with_exception_handler(
        self,
        command: Command | CommandWithResult[CommandResultT],
        exception_handlers: list[type[AnyErrorHandlerContextManager]],
        error: Exception | None = None,
    ) -> CommandWrapper | CommandWithResultWrapper[CommandResultT]:
        try:
            next_exception_handler = exception_handlers[0]
        except IndexError:
            # No more exception handlers
            assert error is not None
            raise error from None

        handler = next_exception_handler()

        try:
            if error:
                await handler.try_to_handle_error(error)
            else:
                # exectue the command only once
                await handler.execute(
                    command.execute_with_result() if isinstance(command, CommandWithResult) else command.execute(),
                )
        except Exception as exception:  # noqa: BLE001
            # Try to handle the error with the next exception handler
            return await self.__surround_with_exception_handler(command, exception_handlers[1:], exception)
        return self.__create_command_wrapper(command, handler.error)

    @overload
    def __create_command_wrapper(  # type: ignore[overload-overlap]
        self, command: CommandWithResult[CommandResultT], error: Exception | None = None
    ) -> CommandWithResultWrapper[CommandResultT]: ...

    @overload
    def __create_command_wrapper(self, command: Command, error: Exception | None = None) -> CommandWrapper: ...

    def __create_command_wrapper(
        self, command: Command | CommandWithResult[CommandResultT], error: Exception | None = None
    ) -> CommandWrapper | CommandWithResultWrapper[CommandResultT]:
        if isinstance(command, CommandWithResult):
            result = command.result if error is None else ResultNotAvailable(exception=error)
            return CommandWithResultWrapper(command=command, result=result, error=error)
        return CommandWrapper(command=command, error=error)


class CLICommands(Commands["CLIWorld"]):
    def __init__(self, world: CLIWorld) -> None:
        super().__init__(world, exception_handlers=[CommunicationFailureNotificator, GeneralErrorNotificator])


class TUICommands(Commands["TUIWorld"], CliveDOMNode):
    def __init__(self, world: TUIWorld) -> None:
        super().__init__(world, exception_handlers=[CommunicationFailureNotificator, GeneralErrorNotificator])
