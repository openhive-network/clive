from __future__ import annotations

from typing import Final

import test_tools as tt

WORKING_ACCOUNT: Final[tt.Account] = tt.Account("alice")
WATCHED_ACCOUNTS: Final[list[tt.Account]] = [tt.Account(name) for name in ("bob", "timmy", "john")]
