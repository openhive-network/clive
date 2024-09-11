from dataclasses import dataclass
from typing import TYPE_CHECKING

from clive.__private.cli.common.common_options_base import CommonOptionsBase
from clive.__private.cli.common.parameters import options
from clive.__private.cli.common.parameters.options import liquid_amount_option, memo_value_option

if TYPE_CHECKING:
    from clive.__private.models import Asset


@dataclass(kw_only=True)
class TransferCommonOptions(CommonOptionsBase):
    amount: "Asset.LiquidT" = liquid_amount_option
    memo: str = memo_value_option
    from_account: str = options.from_account_name_option
