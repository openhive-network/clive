from __future__ import annotations

from abc import ABC, abstractmethod
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Self, cast

from clive.__private.cli.commands.process.process_account_update import (
    ProcessAccountUpdate,
    add_account,
    add_key,
    modify_account,
    modify_key,
    remove_account,
    remove_key,
    set_threshold,
    update_authority,
)
from clive.__private.cli.exceptions import CLITransactionNotSignedError
from clive.__private.core.keys.keys import PublicKey
from clive.__private.models.asset import Asset
from schemas.operations.transfer_operation import TransferOperation

if TYPE_CHECKING:
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.types import AlreadySignedMode, AuthorityLevelRegular
    from clive.__private.core.world import World
    from clive.__private.models.schemas import OperationUnion
    from clive.__private.models.transaction import Transaction


AuthorityAction = Literal["add-account", "add-key", "remove-account", "remove-key", "modify-account", "modify-key"]


class ProcessCommandBase(ABC):
    def __init__(self, world: World) -> None:
        super().__init__()
        self.world = world
        self._sign_with: str | None = None
        self._save_file: str | Path | None = None
        self._broadcast: bool = False
        self._autosign: bool | None = None

    @abstractmethod
    async def _create_operation(self) -> OperationUnion:
        """Get the operation to be processed."""

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        return await self._create_operation()

    async def validate(self) -> None:
        if self._broadcast and not self._sign_with:
            raise CLITransactionNotSignedError  # zduplikowana funkcjonalnosć, do poprawy

    async def _run(self) -> Transaction:
        await self.validate()
        return (
            await self.world.commands.perform_actions_on_transaction(
                content=await self._get_transaction_content(),
                sign_key=PublicKey(value=self._sign_with) if self._sign_with else None,
                autosign=bool(self._autosign),
                save_file_path=Path(self._save_file) if self._save_file else None,
                broadcast=self._broadcast,
            )
        ).result_or_raise

    async def finalize(
        self,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> Transaction:
        """Finalize the operation with specified signing and broadcasting options."""
        self._sign_with = sign_with
        self._save_file = save_file
        self._broadcast = broadcast
        self._autosign = autosign
        return await self._run()


class ProcessTransfer(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        from_account: str,
        to: str,
        amount: str | Asset.LiquidT,
        memo: str = "",
    ) -> None:
        super().__init__(world)
        self.from_account = from_account
        self.to = to
        self.amount = amount
        self.memo = memo

    async def _create_operation(self) -> TransferOperation:
        amount = Asset.from_legacy(self.amount) if isinstance(self.amount, str) else self.amount
        if not isinstance(amount, Asset.LiquidT):
            amount = cast("Asset.LiquidT", amount)
        return TransferOperation(
            from_=self.from_account,
            to=self.to,
            amount=amount,
            memo=self.memo,
        )


class ProcessTransaction(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        from_file: str | Path,
        already_signed_mode: AlreadySignedMode,
        *,
        force_unsign: bool,
        force: bool,
    ) -> None:
        super().__init__(world)
        self.from_file = from_file
        self.force_unsign = force_unsign
        self.already_signed_mode = already_signed_mode
        self.force = force

    async def _run(
        self,
        *,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        broadcast: bool = False,
        autosign: bool | None = None,
    ) -> Transaction:
        from clive.__private.cli.commands.process.process_transaction import ProcessTransaction  # noqa: PLC0415

        transaction = ProcessTransaction(
            from_file=self.from_file,
            force_unsign=self.force_unsign,
            already_signed_mode=self.already_signed_mode,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            force=self.force,
            autosign=autosign,
        )
        await transaction.validate()

        await self.validate(broadcast=broadcast, sign_with=sign_with)
        return (
            await self.world.commands.perform_actions_on_transaction(
                content=await transaction.get_transaction(),
                sign_key=PublicKey(value=sign_with) if sign_with else None,
                autosign=bool(autosign),
                save_file_path=Path(save_file) if save_file else None,
                broadcast=broadcast,
            )
        ).result_or_raise

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessAuthority(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        authority_type: AuthorityLevelRegular,
        account_name: str,
        threshold: int,
    ) -> None:
        super().__init__(world)
        self.authority_type = authority_type
        self.account_name = account_name
        self.threshold = threshold
        self.process_account_update = ProcessAccountUpdate(account_name=account_name)
        self._set_threshold()

    def _set_threshold(self) -> None:
        set_threshold_function = partial(set_threshold, threshold=self.threshold)
        update_function = partial(update_authority, attribute=self.authority_type, callback=set_threshold_function)
        self.process_account_update.add_callback(update_function)

    def add_key(
        self,
        *,
        key: str,
        weight: int,
    ) -> Self:
        add_key_function = partial(add_key, key=key, weight=weight)
        update_function = partial(update_authority, attribute=self.authority_type, callback=add_key_function)
        self.process_account_update.add_callback(update_function)
        return self

    def add_account(
        self,
        *,
        account_name: str,
        weight: int,
    ) -> Self:
        add_account_function = partial(add_account, account=account_name, weight=weight)
        update_function = partial(update_authority, attribute=self.authority_type, callback=add_account_function)
        self.process_account_update.add_callback(update_function)
        return self

    def remove_key(
        self,
        *,
        key: str,
    ) -> Self:
        remove_key_function = partial(remove_key, key=key)
        update_function = partial(update_authority, attribute=self.authority_type, callback=remove_key_function)
        self.process_account_update.add_callback(update_function)
        return self

    def remove_account(
        self,
        *,
        account: str,
    ) -> Self:
        remove_account_function = partial(remove_account, account=account)
        update_function = partial(update_authority, attribute=self.authority_type, callback=remove_account_function)
        self.process_account_update.add_callback(update_function)
        return self

    def modify_key(
        self,
        *,
        key: str,
        weight: int,
    ) -> Self:
        modify_key_function = partial(modify_key, key=key, weight=weight)
        update_function = partial(update_authority, attribute=self.authority_type, callback=modify_key_function)
        self.process_account_update.add_callback(update_function)
        return self

    def modify_account(
        self,
        *,
        account: str,
        weight: int,
    ) -> Self:
        modify_account_function = partial(modify_account, account=account, weight=weight)
        update_function = partial(update_authority, attribute=self.authority_type, callback=modify_account_function)
        self.process_account_update.add_callback(update_function)
        return self

    async def _run(
        self,
        *,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        broadcast: bool = False,
        autosign: bool | None = None,
    ) -> Transaction:
        self.process_account_update.modify_common_options(
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=str(save_file) if save_file else None,
            autosign=autosign,
        )

        await self.validate(broadcast=broadcast, sign_with=sign_with)
        await self.process_account_update.run()
        return await self.process_account_update.get_transaction()

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("Unused method.")


class ProcessPowerDownStart(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> None:
        super().__init__(world)
        self.account_name = account_name
        self.amount = amount

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessPowerDownRestart(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> None:
        super().__init__(world)
        self.account_name = account_name
        self.amount = amount

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessPowerDownCancel(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        account_name: str,
    ) -> None:
        super().__init__(world)
        self.account_name = account_name

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessPowerUp(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        *,
        force: bool,
    ) -> None:
        super().__init__(world)
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.force = force

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessCustomJson(ProcessCommandBase):
    def __init__(
        self,
        world: World,
        id_: str,
        json: str | Path,
        authorize: str | list[str] | None,
        authorize_by_active: str | list[str] | None,
    ) -> None:
        super().__init__(world)
        self.id_ = id_
        self.json = json
        self.authorize = authorize
        self.authorize_by_active = authorize_by_active

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")
