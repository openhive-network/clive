from __future__ import annotations

from typing import TYPE_CHECKING

import test_tools as tt

from clive_local_tools.testnet_block_log.constants import (
    BLOCK_LOG_WITH_CONFIG_DIRECTORY,
    EXTRA_TIME_SHIFT_FOR_GOVERNANCE_AND_REWARDS,
)

if TYPE_CHECKING:
    from beekeepy.interfaces import HttpUrl


def get_config(webserver_http_endpoint: HttpUrl | None = None) -> tt.NodeConfig:
    config = tt.NodeConfig.from_path(BLOCK_LOG_WITH_CONFIG_DIRECTORY)
    if webserver_http_endpoint is not None:
        config.webserver_http_endpoint = webserver_http_endpoint
    return config


def get_alternate_chain_spec() -> tt.AlternateChainSpecs:
    return tt.AlternateChainSpecs.parse_file(BLOCK_LOG_WITH_CONFIG_DIRECTORY)


def get_block_log() -> tt.BlockLog:
    return tt.BlockLog(BLOCK_LOG_WITH_CONFIG_DIRECTORY)


def get_time_control(block_log: tt.BlockLog) -> tt.StartTimeControl:
    block_log_time = block_log.get_head_block_time()
    return tt.StartTimeControl(start_time=block_log_time + EXTRA_TIME_SHIFT_FOR_GOVERNANCE_AND_REWARDS)


def run_node(webserver_http_endpoint: HttpUrl | None = None) -> tt.RawNode:
    config = get_config(webserver_http_endpoint)
    alternate_chain_spec = get_alternate_chain_spec()
    block_log = get_block_log()
    time_control = get_time_control(block_log)

    node = tt.RawNode()
    node.config.load(config)
    node.run(replay_from=block_log, time_control=time_control, alternate_chain_specs=alternate_chain_spec)
    return node
