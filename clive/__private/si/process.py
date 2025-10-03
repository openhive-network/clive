from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.si.core.process import (
    ProcessAuthority,
    ProcessCustomJson,
    ProcessPowerDownCancel,
    ProcessPowerDownRestart,
    ProcessPowerDownStart,
    ProcessPowerUp,
    ProcessTransaction,
    ProcessTransfer,
)

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.types import AlreadySignedMode
    from clive.__private.models.asset import Asset
    from clive.__private.models.transaction import Transaction
    from clive.__private.si.base import ProfileBase


class ProcessInterface:
    """Interface for processing blockchain operations (transfers, authorities, power, custom JSON)."""

    def __init__(self, clive_instance: ProfileBase) -> None:
        self.clive = clive_instance

    async def transfer(  # noqa: PLR0913
        self,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        memo: str = "",
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> Transaction:
        """Transfer funds between accounts."""
        return await ProcessTransfer(
            world=self.clive.world,
            from_account=from_account,
            to=to_account,
            amount=amount,
            memo=memo,
            sign_with=sign_with,
            save_file=save_file,
            broadcast=broadcast,
            autosign=autosign,
        ).run()

    async def transaction(  # noqa: PLR0913
        self,
        from_file: str | Path,
        *,
        force_unsign: bool,
        already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT,
        sign_with: str | None = None,
        broadcast: bool = True,
        save_file: str | Path | None = None,
        autosign: bool | None = None,
        force: bool = False,
    ) -> Transaction:
        """Process a transaction from a file."""
        return await ProcessTransaction(
            world=self.clive.world,
            from_file=from_file,
            force_unsign=force_unsign,
            already_signed_mode=already_signed_mode,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            force=force,
            autosign=autosign,
        ).run()

    def update_owner_authority(  # noqa: PLR0913
        self,
        account_name: str,
        *,
        threshold: int,
        sign_with: str | None = None,
        broadcast: bool = True,
        save_file: str | Path | None = None,
        autosign: bool | None = None,
    ) -> ProcessAuthority:
        """Update owner authority for an account."""
        return ProcessAuthority(
            world=self.clive.world,
            authority_type="owner",
            account_name=account_name,
            threshold=threshold,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        )

    def update_active_authority(  # noqa: PLR0913
        self,
        account_name: str,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        *,
        threshold: int,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> ProcessAuthority:
        """Update active authority for an account."""
        return ProcessAuthority(
            world=self.clive.world,
            authority_type="active",
            account_name=account_name,
            threshold=threshold,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        )

    def update_posting_authority(  # noqa: PLR0913
        self,
        account_name: str,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        *,
        threshold: int,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> ProcessAuthority:
        """Update posting authority for an account."""
        return ProcessAuthority(
            world=self.clive.world,
            authority_type="posting",
            account_name=account_name,
            threshold=threshold,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        )

    async def process_power_down_start(  # noqa: PLR0913
        self,
        account_name: str,
        amount: str | Asset.LiquidT,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> None:
        """Start power down for an account."""
        await ProcessPowerDownStart(
            world=self.clive.world,
            account_name=account_name,
            amount=amount,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        ).run()

    async def process_power_down_restart(  # noqa: PLR0913
        self,
        account_name: str,
        amount: str | Asset.LiquidT,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> None:
        """Restart power down for an account."""
        await ProcessPowerDownRestart(
            world=self.clive.world,
            account_name=account_name,
            amount=amount,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        ).run()

    async def process_power_down_cancel(
        self,
        account_name: str,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> None:
        """Cancel power down for an account."""
        await ProcessPowerDownCancel(
            world=self.clive.world,
            account_name=account_name,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        ).run()

    async def process_power_up(  # noqa: PLR0913
        self,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        *,
        force: bool,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> None:
        """Power up (stake) funds from one account to another."""
        await ProcessPowerUp(
            world=self.clive.world,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            force=force,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        ).run()

    async def process_custom_json(  # noqa: PLR0913
        self,
        id_: str,
        json: str | Path,
        authorize: str | list[str] | None = None,
        authorize_by_active: str | list[str] | None = None,
        sign_with: str | None = None,
        save_file: str | Path | None = None,
        *,
        broadcast: bool = True,
        autosign: bool | None = None,
    ) -> None:
        """Process a custom JSON operation."""
        await ProcessCustomJson(
            world=self.clive.world,
            id_=id_,
            json=json,
            authorize=authorize,
            authorize_by_active=authorize_by_active,
            sign_with=sign_with,
            broadcast=broadcast,
            save_file=save_file,
            autosign=autosign,
        ).run()
