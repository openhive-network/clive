from __future__ import annotations

from clive.__private.cli.common.parameters import options
from clive.__private.cli.common.parameters.utils import make_argument_related_option

account_name = make_argument_related_option(options.account_name)
profile_name = make_argument_related_option(options.profile_name)
