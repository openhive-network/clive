from __future__ import annotations

from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, Callable

    from clive_local_tools.cli.cli_tester import CLITester


type CLITesterFactory = Callable[[CLITesterVariant], AsyncGenerator[CLITester]]
type CLITesterVariant = Literal["unlocked", "locked", "without remote address", "without session token"]
