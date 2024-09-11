from dataclasses import dataclass

from clive.__private.cli.common.common_options_base import CommonOptionsBase
from clive.__private.cli.common.parameters import options


@dataclass(kw_only=True)
class ProfileCommonOptions(CommonOptionsBase):
    profile_name: str = options.profile_name_option
