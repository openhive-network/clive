from __future__ import annotations

from typing import Final

import test_tools as tt

WORKING_ACCOUNT: Final[tt.Account] = tt.Account("alice")
WATCHED_ACCOUNTS: Final[list[tt.Account]] = [tt.Account(name) for name in ("bob", "timmy", "john")]

# Additional data for block_log generation:
WORKING_PROFILES: Final[list[tt.Account]] = [WORKING_ACCOUNT, *WATCHED_ACCOUNTS]
WATCHED_PROFILES: Final[dict[str, list[tt.Account]]] = {
    WORKING_PROFILES[0].name: WORKING_PROFILES[1:4],
    WORKING_PROFILES[1].name: [WORKING_PROFILES[0], *WORKING_PROFILES[2:4]],
    WORKING_PROFILES[2].name: [*WORKING_PROFILES[0:2], WORKING_PROFILES[3]],
    WORKING_PROFILES[3].name: WORKING_PROFILES[0:3],
}
WITNESSES_40: Final[list[tt.Account]] = [tt.Account(f"witness-{i+1:02d}") for i in range(40)]
