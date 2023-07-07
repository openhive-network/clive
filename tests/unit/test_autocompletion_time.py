from __future__ import annotations

import subprocess

import pytest

from clive.__private.logger import logger


@pytest.mark.sequential()
def test_autocompletion_time() -> None:
    # ARRANGE
    seconds_threshold = 0.4
    command = "_CLIVE_COMPLETE=1 TIMEFORMAT='%U' /bin/bash -c 'time python3 -X importtime clive/main.py --help'"

    # ACT
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # ASSERT
    output = result.stderr.strip()

    import_time = float(output.splitlines()[-1])

    logger.info(f"Cumulative import time: {import_time:.2f}s")
    logger.info(output)

    message = (
        f"Autocompletion time `{import_time:.2f}s` exceeds `{seconds_threshold}s`\n"
        "Please check for any unnecessary imports in autocompletion mode."
    )
    assert import_time < seconds_threshold, message
