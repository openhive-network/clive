from __future__ import annotations

from dataclasses import dataclass

from clive.__private.cli.commands.abc.world_based_command import WorldBasedCommand
from clive.__private.cli.print_cli import print_cli
from clive.__private.core.constants.setting_identifiers import BEEKEEPER_SESSION_TOKEN
from clive.__private.settings import clive_prefixed_envvar


@dataclass(kw_only=True)
class BeekeeperCreateSession(WorldBasedCommand):
    echo_token_only: bool

    @property
    def should_validate_if_session_token_required(self) -> bool:
        return False

    @property
    def should_require_unlocked_wallet(self) -> bool:
        return False

    async def _run(self) -> None:
        session = await self.world.beekeeper_manager.beekeeper.create_session()
        token = await session.token
        if self.echo_token_only:
            message = token
        else:
            message = (
                f"A new session was created, token is: {token}\n"
                "If you want to use that Beekeeper session in Clive CLI env, please set:\n"
                f"export {clive_prefixed_envvar(BEEKEEPER_SESSION_TOKEN)}={token}"
            )
        print_cli(message)

    async def _hook_before_entering_context_manager(self) -> None:
        """Display information about using Beekeeper if not using echo-token-only flag."""
        if not self.echo_token_only:
            await super()._hook_before_entering_context_manager()
