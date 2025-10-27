from __future__ import annotations

from typing import TYPE_CHECKING

from clive.__private.core.constants.data_retrieval import ALREADY_SIGNED_MODE_DEFAULT
from clive.__private.si.chaining import (
    AuthorityChain,
    CustomJsonChain,
    PowerDownCancelChain,
    PowerDownRestartChain,
    PowerDownStartChain,
    PowerUpChain,
    TransactionChain,
    TransferChain,
)

if TYPE_CHECKING:
    from pathlib import Path

    from clive.__private.core.types import AlreadySignedMode
    from clive.__private.models.asset import Asset
    from clive.__private.si.base import ProfileBase


class ProcessInterface:
    """Interface for processing blockchain operations (transfers, authorities, power, custom JSON)."""

    def __init__(self, clive_instance: ProfileBase) -> None:
        self.clive = clive_instance

    def transfer(
        self,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        memo: str = "",
    ) -> TransferChain:
        """Transfer funds between accounts."""
        return TransferChain(
            world=self.clive.world,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            memo=memo,
        )

    def transaction(
        self,
        from_file: str | Path,
        *,
        force_unsign: bool | None = None,
        already_signed_mode: AlreadySignedMode = ALREADY_SIGNED_MODE_DEFAULT,
        force: bool = False,
    ) -> TransactionChain:
        """Process a transaction from a file."""
        return TransactionChain(
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
    ) -> AuthorityChain:
        """Update owner authority for an account."""
        return AuthorityChain(
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
    ) -> AuthorityChain:
        """Update active authority for an account."""
        return AuthorityChain(
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
    ) -> AuthorityChain:
        """Update posting authority for an account."""
        return AuthorityChain(
            world=self.clive.world,
            authority_type="posting",
            account_name=account_name,
            threshold=threshold,
        )

    def power_down_start(
        self,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> PowerDownStartChain:
        """Start power down for an account."""
        return PowerDownStartChain(
            world=self.clive.world,
            account_name=account_name,
            amount=amount,
        )

    def power_down_restart(
        self,
        account_name: str,
        amount: str | Asset.LiquidT,
    ) -> PowerDownRestartChain:
        """Restart power down for an account."""
        return PowerDownRestartChain(
            world=self.clive.world,
            account_name=account_name,
            amount=amount,
        )

    def power_down_cancel(
        self,
        account_name: str,
    ) -> PowerDownCancelChain:
        """Cancel power down for an account."""
        return PowerDownCancelChain(
            world=self.clive.world,
            account_name=account_name,
        )

    def power_up(
        self,
        from_account: str,
        to_account: str,
        amount: str | Asset.LiquidT,
        *,
        force: bool,
    ) -> PowerUpChain:
        """Power up (stake) funds from one account to another."""
        return PowerUpChain(
            world=self.clive.world,
            from_account=from_account,
            to_account=to_account,
            amount=amount,
            force=force,
        )

    def custom_json(
        self,
        id_: str,
        json: str | Path,
        authorize: str | list[str] | None = None,
        authorize_by_active: str | list[str] | None = None,
    ) -> CustomJsonChain:
        """Process a custom JSON operation."""
        return CustomJsonChain(
            world=self.clive.world,
            id_=id_,
            json=json,
            authorize=authorize,
            authorize_by_active=authorize_by_active,
        )
