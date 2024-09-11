from dataclasses import dataclass, field
from typing import Optional

from clive.__private.cli.common.common_options_base import CommonOptionsBase
from clive.__private.cli.common.parameters import options


@dataclass(kw_only=True)
class WorldCommonOptions(CommonOptionsBase):
    profile_name: str = options.profile_name_option
    beekeeper_remote: Optional[str] = options.beekeeper_remote_option
    use_beekeeper: bool = field(default=True, metadata={"ignore": True})


@dataclass(kw_only=True)
class WorldWithoutBeekeeperCommonOptions(CommonOptionsBase):
    profile_name: str = options.profile_name_option
    use_beekeeper: bool = field(default=False, metadata={"ignore": True})
