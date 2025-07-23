from __future__ import annotations

from dataclasses import dataclass

from clive.__private.before_launch import prepare_before_launch
from clive.__private.cli.commands.abc.external_cli_command import ExternalCLICommand


@dataclass(kw_only=True)
class Init(ExternalCLICommand):
    async def _run(self) -> None:
        prepare_before_launch(
            enable_textual_logger=False,
            enable_stream_handlers=False,
        )
