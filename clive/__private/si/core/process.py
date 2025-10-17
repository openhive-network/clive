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
    def __init__(  # noqa: PLR0913
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
    def __init__(  # noqa: PLR0913
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

    async def _create_operation(self) -> TransferOperation:
        raise NotImplementedError("This will be implemented in future.")


class ProcessAuthority(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
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
        self.actions: list[tuple[AuthorityAction, dict[str, any]]] = []

    def add_key(
        self,
        *,
        key: str | PublicKey,
        weight: int,
    ) -> Self:
        self.actions.append(("add-key", {"key": key, "weight": weight}))
        return self

    def add_account(
        self,
        *,
        account_name: str,
        weight: int,
    ) -> Self:
        # Tymczasowo rzuć wyjątek zgodnie z oczekiwaniem z przykładu
        raise Exception(f"Not implemented yet {account_name}, {weight}")  # noqa: TRY002

    def remove_key(
        self,
        *,
        key: str | PublicKey,
    ) -> Self:
        self.actions.append(("remove-key", {"key": key}))
        return self

    def remove_account(
        self,
        *,
        account: str | Account,
    ) -> Self:
        self.actions.append(("remove-account", {"account": account}))
        return self

    def modify_key(
        self,
        *,
        key: str | PublicKey,
        weight: int,
    ) -> Self:
        self.actions.append(("modify-key", {"key": key, "weight": weight}))
        return self

    def modify_account(
        self,
        *,
        account: str | Account,
        weight: int,
    ) -> Self:
        self.actions.append(("modify-account", {"account": account, "weight": weight}))
        return self

    async def _create_operation(self) -> TransferOperation:
        # Tymczasowa implementacja - w przyszłości będzie używać odpowiedniej operacji authority
        raise NotImplementedError("Authority operations not yet fully implemented")


class ProcessPowerDownStart(ProcessCommandBase):
    def __init__(  # noqa: PLR0913
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
    def __init__(  # noqa: PLR0913
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
    def __init__(  # noqa: PLR0913
        self,
        world: World,
        account_name: str,
    ) -> None:
        super().__init__(world)
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
    def __init__(  # noqa: PLR0913
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
