from __future__ import annotations

import subprocess
from pathlib import Path

from clive.__private.logger import logger
from clive.main import __file__ as path_to_clive_main


def test_autocompletion_time() -> None:
    # ARRANGE
    seconds_threshold = 0.5
    path = Path(path_to_clive_main).absolute().as_posix()
    command = f"_CLIVE_COMPLETE=1 TIMEFORMAT='%U' /bin/bash -c 'time python3 -X importtime {path} --help'"

    # ACT
    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

    # ASSERT
    assert result.returncode == 0

    output = result.stderr.strip()

    import_time = float(output.splitlines()[-1].replace(",", "."))

    logger.info(f"Cumulative import time: {import_time:.2f}s")
    logger.info(output)

    message = (
        f"Autocompletion time `{import_time}s` exceeds `{seconds_threshold}s`\n"
        "Please check for any unnecessary imports in autocompletion mode."
    )
    assert import_time < seconds_threshold, message
