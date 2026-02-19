from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.common.constants import social_action_validates_bad_account
from clive.__private.cli.exceptions import CLITransactionBadAccountError
from clive.__private.core.accounts.account_manager import AccountManager
from clive.__private.models.schemas import CustomJsonOperation

if TYPE_CHECKING:
    from clive.__private.cli.common.constants import SocialAction
    from clive.__private.cli.types import ComposeTransaction


@dataclass(kw_only=True)
class ProcessFollow(OperationCommand):
    """
    Command for social operations (follow, unfollow, mute, unmute).

    These operations use a custom_json operation with id="follow" and posting authority.
    """

    follower: str
    following: str
    action: SocialAction

    async def validate(self) -> None:
        if social_action_validates_bad_account(self.action):
            self._validate_following_not_bad_account()
        await super().validate()

    def _validate_following_not_bad_account(self) -> None:
        """Validate that the target account is not a bad account."""
        if AccountManager.is_account_bad(self.following):
            raise CLITransactionBadAccountError(self.following)

    async def _create_operations(self) -> ComposeTransaction:
        from clive.__private.core.wax_operation_wrapper import WaxFollowOperationWrapper  # noqa: PLC0415

        wrapper = WaxFollowOperationWrapper.create(follower=self.follower, following=self.following, action=self.action)
        yield wrapper.to_schemas(self.world.wax_interface, CustomJsonOperation)
