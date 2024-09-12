from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.common.parameters import options
from clive.__private.cli.common.parameters.groups.parameter_group import ParameterGroup

if TYPE_CHECKING:
    from clive.__private.models import Asset


@dataclass(kw_only=True)
class TransferOptionsGroup(ParameterGroup):
    amount: "Asset.LiquidT" = options.liquid_amount
    memo: str = options.memo_value
    from_account: str = options.from_account_name
