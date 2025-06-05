from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Final

import test_tools as tt
from test_tools import BlockLog

if TYPE_CHECKING:
    from datetime import timedelta

    from beekeepy.interfaces import HttpUrl

EXTRA_TIME_SHIFT_FOR_GOVERNANCE: Final[timedelta] = tt.Time.days(1)


def get_alternate_chain_spec_path() -> Path:
    return Path(__file__).parent.absolute() / "alternate-chain-spec.json"


def get_block_log() -> BlockLog:
    path = Path(__file__).parent.absolute() / "blockchain"
    return BlockLog(path)


def get_config() -> tt.NodeConfig:
    path = Path(__file__).parent.absolute() / "config.ini"
    return tt.NodeConfig.from_path(path)


def get_time_control(block_log: BlockLog) -> tt.StartTimeControl:
    block_log_time = block_log.get_head_block_time()
    return tt.StartTimeControl(start_time=block_log_time + EXTRA_TIME_SHIFT_FOR_GOVERNANCE)


def run_node(webserver_http_endpoint: HttpUrl | None = None) -> tt.RawNode:
    config = get_config()
    block_log = get_block_log()
    alternate_chain_spec = tt.AlternateChainSpecs.parse_file(get_alternate_chain_spec_path())
    time_control = get_time_control(block_log)

    node = tt.RawNode()
    node.config.load(config)
    if webserver_http_endpoint is not None:
        node.config.webserver_http_endpoint = webserver_http_endpoint
    node.run(replay_from=block_log, time_control=time_control, alternate_chain_specs=alternate_chain_spec)
    return node
