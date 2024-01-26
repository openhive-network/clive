from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.core.formatters.humanize import (
    humanize_hbd_exchange_rate,
    humanize_hbd_interest_rate,
    humanize_votes_with_comma,
    humanize_witness_status,
)


@dataclass(kw_only=True)
class ShowWitness(WorldBasedCommand):
    name: str

    async def _run(self) -> None:
        wrapper = await self.world.commands.find_witness(witness_name=self.name)
        witness = wrapper.result_or_raise

        gdpo = await self.world.node.api.database_api.get_dynamic_global_properties()
        votes = humanize_votes_with_comma(witness.votes, gdpo.total_vesting_fund_hive, gdpo.total_vesting_shares)

        account_creation_fee: str | None = None
        if witness.props.account_creation_fee:
            account_creation_fee = witness.props.account_creation_fee.as_legacy()
        hbd_interest_rate: str | None = None
        if witness.props.hbd_interest_rate:
            hbd_interest_rate = humanize_hbd_interest_rate(witness.props.hbd_interest_rate)
        props_as_legacy = witness.props.copy(exclude={"account_creation_fee", "hbd_interest_rate"}, deep=True)

        table = Table(title=f"Details of `{self.name}` witness", show_header=False)

        table.add_row("created", f"{witness.created}")
        table.add_row("url", f"{witness.url}")
        table.add_row("total votes", f"{votes}")
        table.add_row("hardfork time vote", f"{witness.hardfork_time_vote}")
        table.add_row("hardfork version vote", f"{witness.hardfork_version_vote}")
        table.add_row("price feed", f"{humanize_hbd_exchange_rate(witness.hbd_exchange_rate)}")
        table.add_row("last confirmed block num", f"{witness.last_confirmed_block_num}")
        table.add_row("last hbd exchange update", f"{witness.last_hbd_exchange_update}")
        table.add_row("last work", f"{witness.last_work}")
        table.add_row("props", f"{props_as_legacy}")
        table.add_row("running version", f"{witness.running_version}")
        table.add_row("signing key", f"{witness.signing_key}")
        table.add_row("total missed", f"{witness.total_missed}")
        table.add_row("account creation fee", f"{account_creation_fee}")
        table.add_row("hbd interest rate", f"{hbd_interest_rate}")
        table.add_row("status", f"{humanize_witness_status(witness.signing_key)}")

        console = Console()
        console.print(table)
