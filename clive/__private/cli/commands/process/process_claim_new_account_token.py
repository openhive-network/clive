from __future__ import annotations

import errno
from dataclasses import dataclass
from typing import TYPE_CHECKING

from click.core import ParameterSource

from clive.__private.cli.commands.abc.operation_command import OperationCommand
from clive.__private.cli.exceptions import CLIPrettyError
from clive.__private.core.constants.node import HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION
from clive.__private.core.profile_data import ProfileData
from clive.models import Asset
from schemas.operations import ClaimAccountOperation

if TYPE_CHECKING:
    import typer


@dataclass(kw_only=True)
class ProcessClaimNewAccountToken(OperationCommand):
    creator_param_name: str
    ctx: typer.Context
    fee: Asset.Hive | None
    """None means RC will be used instead of payment in Hive"""

    @property
    def creator(self) -> str:
        return self._get_working_account_name(self.creator_param_name)

    def _get_working_account_name(self, param_name: str) -> str:
        def is_default(name: str) -> bool:
            return self.ctx.get_parameter_source(name) == ParameterSource.DEFAULT

        try:
            param_value = self.ctx.params[param_name]
        except KeyError as error:
            raise AssertionError(f"Parameter {param_name} not found in context params of {self.ctx.params}.") from error

        message = f"Expected {param_name} to be a string, got {type(param_value)} of {param_value}."
        assert isinstance(param_value, str), message

        if is_default("profile_name"):
            return param_value

        if is_default(param_name):
            # if profile_name is not default, then we have to get working account name from the given profile
            # if not explicitly given
            return ProfileData.get_working_account_name(self.profile_name)

        # when both profile name and working account name are given - use this explicitly given working account name
        return param_value

    async def _create_operation(self) -> ClaimAccountOperation:
        if self.fee == Asset.hive(HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION):
            raise CLIClaimAccountTokenZeroFeeError
        fee = self.fee if self.fee is not None else Asset.hive(HIVE_FEE_TO_USE_RC_IN_CLAIM_ACCOUNT_TOKEN_OPERATION)

        return ClaimAccountOperation(creator=self.creator, fee=fee)


class CLIClaimAccountTokenZeroFeeError(CLIPrettyError):
    def __init__(self) -> None:
        message = "Fee can't be zero, to use resource credits skip the fee option."
        super().__init__(message, errno.E2BIG)
