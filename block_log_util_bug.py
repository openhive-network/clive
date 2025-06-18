from __future__ import annotations

import concurrent
from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Final

import test_tools as tt

from clive_local_tools.testnet_block_log.constants import BLOCK_LOG_WITH_CONFIG_DIRECTORY

TOTAL_TASK_NUM: Final[int] = 2000


def get_head_block_time(i: int) -> datetime:
    log_directory = Path.cwd() / "block_log_util_logs"
    log_directory.mkdir(exist_ok=True)
    log_file = log_directory / f"log_{i}"
    block_log_head_block_time = tt.BlockLog(BLOCK_LOG_WITH_CONFIG_DIRECTORY).get_head_block_time(log_file=log_file)
    return block_log_head_block_time


def trigger_block_log_util_bug() -> None:
    with ProcessPoolExecutor() as executor:
        total_tasks = list(range(TOTAL_TASK_NUM))
        future_to_i = {executor.submit(get_head_block_time, i=i): i for i in total_tasks}
        completed_i: list[int] = []

        for future in concurrent.futures.as_completed(future_to_i):
            i = future_to_i[future]
            result = future.result()
            print(f"{i}: {result}")
            completed_i.append(i)
            remaining = sorted(set(total_tasks) - set(completed_i))
            print(f"remaining: {len(remaining)} tasks - {remaining[:10]}{' and more' if len(remaining) > 10 else ''}")


if __name__ == "__main__":
    trigger_block_log_util_bug()
