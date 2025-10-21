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

    def transfer(  # noqa: PLR0913
        self,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        memo: str = "",
    ) -> ProcessTransfer:
        """Transfer funds between accounts."""
        return ProcessTransfer(
            world=self.clive.world,
            from_account=from_account,
            to=to_account,
            amount=amount,
            memo=memo,
        )

    def transaction(  # noqa: PLR0913
        self,
        from_file: str | Path,
        *,
        force_unsign: bool,
        already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT,
        force: bool = False,
    ) -> ProcessTransaction:
        """Process a transaction from a file."""
        return ProcessTransaction(
            world=self.clive.world,
            from_file=from_file,
            force_unsign=force_unsign,
            already_signed_mode=already_signed_mode,
            force=force,
        )

    def update_owner_authority(
        self,
        account_name: str,
        *,
        threshold: int,
    ) -> ProcessAuthority:
        """Update owner authority for an account."""
        return ProcessAuthority(
            world=self.clive.world,
            authority_type="owner",
            account_name=account_name,
            threshold=threshold,
        )

    def update_active_authority(
        self,
        account_name: str,
        *,
        threshold: int,
    ) -> ProcessAuthority:
        """Update active authority for an account."""
        return ProcessAuthority(
            world=self.clive.world,
            authority_type="active",
            account_name=account_name,
            threshold=threshold,
        )

    def update_posting_authority(
        self,
        account_name: str,
        *,
        threshold: int,
    ) -> ProcessAuthority:
        """Update posting authority for an account."""
        return ProcessAuthority(
            world=self.clive.world,
            authority_type="posting",
            account_name=account_name,
            threshold=threshold,
        )

    def power_down_start(  # noqa: PLR0913
        self,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> ProcessPowerDownStart:
        """Start power down for an account."""
        return ProcessPowerDownStart(
            world=self.clive.world,
            account_name=account_name,
            amount=amount,
        )

    def power_down_restart(  # noqa: PLR0913
        self,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> ProcessPowerDownRestart:
        """Restart power down for an account."""
        return ProcessPowerDownRestart(
            world=self.clive.world,
            account_name=account_name,
            amount=amount,
        )

    def power_down_cancel(
        self,
        account_name: str,
    ) -> ProcessPowerDownCancel:
        """Cancel power down for an account."""
        return ProcessPowerDownCancel(
            world=self.clive.world,
            account_name=account_name,
        )

    def power_up(  # noqa: PLR0913
        self,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        *,
        force: bool,
    ) -> ProcessPowerUp:
        """Power up (stake) funds from one account to another."""
        return ProcessPowerUp(
            world=self.clive.world,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            force=force,
        )

    def custom_json(  # noqa: PLR0913
        self,
        id_: str,
        json: str | Path,
        authorize: str | list[str] | None = None,
        authorize_by_active: str | list[str] | None = None,
    ) -> ProcessCustomJson:
        """Process a custom JSON operation."""
        return ProcessCustomJson(
            world=self.clive.world,
            id_=id_,
            json=json,
            authorize=authorize,
            authorize_by_active=authorize_by_active,
        )
