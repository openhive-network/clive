from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand
from clive.__private.cli.exceptions import CLIChainIdFromSettingsNotAvailableError
from clive.__private.settings import safe_settings
from wax.wax_factory import create_hive_chain
from wax.wax_options import WaxChainOptions

if TYPE_CHECKING:
    from wax import IHiveChainInterface


@dataclass(kw_only=True)
class NodeAddressCLICommand(ExternalCLICommand, ABC):
    """
    A command that requires a node address to be provided explicitly.

    Attributes:
        node_address: The HTTP endpoint URL of the Hive node to connect to.
    """

    node_address: str

    def _build_wax_interface(self) -> IHiveChainInterface:
        chain_id = safe_settings.node.chain_id
        if chain_id is None:
            raise CLIChainIdFromSettingsNotAvailableError
        wax_chain_options = WaxChainOptions(chain_id=chain_id, endpoint_url=self.node_address)
        return create_hive_chain(wax_chain_options)
