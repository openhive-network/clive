from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.core.commands.abc.command_with_result import CommandWithResult
from wax.models.authority import WaxAccountAuthorityInfo

if TYPE_CHECKING:
    from wax import IHiveChainInterface


@dataclass(kw_only=True)
class CollectAccountAuthorities(CommandWithResult[WaxAccountAuthorityInfo]):
    wax_interface: IHiveChainInterface
    account: str

    async def _execute(self) -> None:
        self._result = await self.wax_interface.collect_account_authorities(self.account)
