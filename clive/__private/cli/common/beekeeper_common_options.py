from dataclasses import dataclass
from typing import Optional

from clive.__private.cli.common.common_options_base import CommonOptionsBase
from clive.__private.cli.common.parameters import options


@dataclass(kw_only=True)
class BeekeeperCommonOptions(CommonOptionsBase):
    beekeeper_remote: Optional[str] = options.beekeeper_remote
