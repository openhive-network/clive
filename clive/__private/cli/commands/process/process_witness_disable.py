from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.core.constants import NULL_ACCOUNT_KEY_VALUE
from schemas.fields.basic import PublicKey
from schemas.operations import WitnessSetPropertiesOperation


@dataclass(kw_only=True)
class ProcessWitnessDisable(OperationCommand):
    owner: str
    """None means RC will be used instead of payment in Hive"""

    async def _create_operation(self) -> WitnessSetPropertiesOperation:
        null_key = PublicKey(NULL_ACCOUNT_KEY_VALUE)
        import typer

        typer.echo(f"{null_key}")

        props = [("new_signing_key", "028bb6e3bfd8633279430bd6026a1178e8e311fe4700902f647856a9f32ae82a8b")]

        return WitnessSetPropertiesOperation(owner=self.owner, props=props)
