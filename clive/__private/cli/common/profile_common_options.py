from dataclasses import dataclass
from typing import Optional

from clive.__private.cli.common.common_options_base import CommonOptionsBase
from clive.__private.cli.common.parameters import argument_related_options, arguments, options
from clive.__private.cli.common.parameters.ensure_single_value import ensure_single_value_profile_name


@dataclass(kw_only=True)
class ProfileCommonOptions(CommonOptionsBase):
    profile_name: str = options.profile_name


@dataclass(kw_only=True)
class ProfileCommonOptionsWithPositionalName(CommonOptionsBase):
    profile_name: Optional[str] = arguments.profile_name
    profile_name_option: Optional[str] = argument_related_options.profile_name

    def ensure_single_profile_name_value(self) -> str:
        return ensure_single_value_profile_name(self.profile_name, self.profile_name_option)  # type: ignore[no-any-return]
