import subprocess
from typing import Final

import pytest


@pytest.mark.xfail(reason="Should be resumed when CLI commands are implemented and clive --help is available")
def test_if_entry_point_works() -> None:
    # ARRANGE
    entry_point: Final[str] = "clive --help"
    exit_code_successful: Final[int] = 0

    # ACT
    status, result = subprocess.getstatusoutput(entry_point)

    # ASSERT
    assert status == exit_code_successful, f"`{entry_point}` command failed because of: `{result}`"
