from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Literal, Self, cast

from clive.__private.cli.exceptions import CLITransactionNotSignedError
from clive.__private.core.keys.keys import PublicKey
from clive.__private.models.asset import Asset
from schemas.operations.transfer_operation import TransferOperation

if TYPE_CHECKING:
    from clive.__private.core.accounts.accounts import Account
    from clive.__private.core.ensure_transaction import TransactionConvertibleType
    from clive.__private.core.types import AlreadySignedMode, AuthorityLevelRegular
    from clive.__private.core.world import World
    from clive.__private.models.schemas import OperationUnion
    from clive.__private.models.transaction import Transaction


AuthorityAction = Literal["add-account", "add-key", "remove-account", "remove-key", "modify-account", "modify-key"]


class ProcessCommandBase(ABC):
    def __init__(
        self,
        world: World,
        sign_with: str | None,
        save_file: str | Path | None,
        *,
        broadcast: bool,
        autosign: bool | None,
    ) -> None:
        super().__init__()
        self.world = world
        self.sign_with = sign_with
        self.save_file = save_file
        self._broadcast = broadcast
        self._autosign = autosign

    @abstractmethod
    async def _create_operation(self) -> OperationUnion:
        """Get the operation to be processed."""

    async def _get_transaction_content(self) -> TransactionConvertibleType:
        return await self._create_operation()

    async def validate(self) -> None:
        if self._broadcast and not self.sign_with:
            raise CLITransactionNotSignedError  # zduplikowana funkcjonalnosć, do poprawy

    async def _run(self) -> Transaction:
        await self.validate()
        return (
            await self.world.commands.perform_actions_on_transaction(
                content=await self._get_transaction_content(),
                sign_key=PublicKey(value=self.sign_with) if self.sign_with else None,
                autosign=bool(self._autosign),
                save_file_path=Path(self.save_file) if self.save_file else None,
                broadcast=self._broadcast,
            )
        ).result_or_raise

    async def run(self) -> Transaction:
        await self.validate()
        return await self._run()


class ProcessTransfer(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        from_account: str,
        to: str,
        amount: str | Asset.LiquidT,
        memo: str,
        sign_with: str | None,
        save_file: str | Path | None,
        *,
        broadcast: bool,
        autosign: bool | None,
    ) -> None:
        super().__init__(
            world=world,
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
        )
        self.world = world
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
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        from_file: str | Path,
        already_signed_mode: AlreadySignedMode,
        sign_with: str | None,
        save_file: str | Path | None,
        *,
        force_unsign: bool,
        force: bool,
        broadcast: bool,
        autosign: bool | None,
    ) -> None:
        super().__init__(
            world=world,
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
        )
        self.world = world
        self.from_file = from_file
        self.force_unsign = force_unsign
        self.already_signed_mode = already_signed_mode
        self.force = force

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessAuthority(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        authority_type: AuthorityLevelRegular,
        account_name: str,
        threshold: int,
        sign_with: str | None,
        save_file: str | Path | None,
        *,
        broadcast: bool,
        autosign: bool | None,
    ) -> None:
        super().__init__(
            world=world,
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
        )
        self.world = world
        self.authority_type = authority_type
        self.account_name = account_name
        self.threshold = threshold

    def add_key(
        self,
        *,
        key: str | PublicKey,
        weight: int,
    ) -> Self:
        raise Exception(f"Not implemented yet {key}, {weight}")  # noqa: TRY002
        return self

    def add_account(
        self,
        *,
        account: str | Account,
        weight: int,
    ) -> Self:
        raise Exception(f"Not implemented yet {account}, {weight}")  # noqa: TRY002
        return self

    def remove_key(
        self,
        *,
        key: str | PublicKey,
    ) -> Self:
        raise Exception(f"Not implemented yet {key}")  # noqa: TRY002
        return self

    def remove_account(
        self,
        *,
        account: str | Account,
    ) -> Self:
        raise Exception(f"Not implemented yet {account}")  # noqa: TRY002
        return self

    def modify_key(
        self,
        *,
        key: str | PublicKey,
        weight: int,
    ) -> Self:
        raise Exception(f"Not implemented yet {key}, {weight}")  # noqa: TRY002
        return self

    def modify_account(
        self,
        *,
        account: str | Account,
        weight: int,
    ) -> Self:
        raise Exception(f"Not implemented yet {account}, {weight}")  # noqa: TRY002
        return self

    async def fire(self) -> Transaction:
        return await self.run()

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessPowerDownStart(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        account_name: str,
        amount: str | Asset.LiquidT,
        sign_with: str | None,
        save_file: str | Path | None,
        *,
        broadcast: bool,
        autosign: bool | None,
    ) -> None:
        super().__init__(
            world=world,
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
        )
        self.world = world
        self.account_name = account_name
        self.amount = amount

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessPowerDownRestart(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        account_name: str,
        amount: str | Asset.LiquidT,
        sign_with: str | None,
        save_file: str | Path | None,
        *,
        broadcast: bool,
        autosign: bool | None,
    ) -> None:
        super().__init__(
            world=world,
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
        )
        self.world = world
        self.account_name = account_name
        self.amount = amount

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessPowerDownCancel(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        account_name: str,
        sign_with: str | None,
        save_file: str | Path | None,
        *,
        broadcast: bool,
        autosign: bool | None,
    ) -> None:
        super().__init__(
            world=world,
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
        )
        self.world = world
        self.account_name = account_name

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessPowerUp(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        sign_with: str | None,
        save_file: str | Path | None,
        *,
        force: bool,
        broadcast: bool,
        autosign: bool | None,
    ) -> None:
        super().__init__(
            world=world,
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
        )
        self.world = world
        self.from_account = from_account
        self.to_account = to_account
        self.amount = amount
        self.force = force

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessCustomJson(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        id_: str,
        json: str | Path,
        authorize: str | list[str] | None,
        authorize_by_active: str | list[str] | None,
        sign_with: str | None,
        save_file: str | Path | None,
        *,
        broadcast: bool,
        autosign: bool | None,
    ) -> None:
        super().__init__(
            world=world,
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast if broadcast is not None else True,
            autosign=autosign,
        )
        self.id_ = id_
        self.json = json
        self.authorize = authorize
        self.authorize_by_active = authorize_by_active

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")
