import subprocess
from typing import Final


def test_if_entry_point_works():
    # ARRANGE
    entry_point: Final[str] = "clive"
    exit_code_successful: Final[int] = 0

    # ACT
    status, result = subprocess.getstatusoutput(entry_point)

    # ASSERT
    assert status == exit_code_successful, f"`{entry_point}` command failed because of: `{result}`"
