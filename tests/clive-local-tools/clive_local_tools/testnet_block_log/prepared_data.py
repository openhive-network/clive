from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import test_tools as tt
from test_tools import BlockLog

if TYPE_CHECKING:
    from beekeepy.interfaces import HttpUrl


def get_alternate_chain_spec_path() -> Path:
    return Path(__file__).parent.absolute() / "alternate-chain-spec.json"


def get_block_log() -> BlockLog:
    path = Path(__file__).parent.absolute() / "blockchain"
    return BlockLog(path)


def get_config() -> tt.NodeConfig:
    path = Path(__file__).parent.absolute() / "config.ini"
    return tt.NodeConfig.from_path(path)


def get_time_offset() -> str:
    path = Path(__file__).parent.absolute() / "timestamp"
    with Path.open(path) as file:
        return file.read()


def run_node(webserver_http_endpoint: HttpUrl | None = None) -> tt.RawNode:
    config = get_config()
    block_log = get_block_log()
    alternate_chain_spec = tt.AlternateChainSpecs.parse_file(get_alternate_chain_spec_path())
    time_offset = get_time_offset()

    node = tt.RawNode()
    node.config.load(config)
    if webserver_http_endpoint is not None:
        node.config.webserver_http_endpoint = webserver_http_endpoint
    node.run(replay_from=block_log, time_control=time_offset, alternate_chain_specs=alternate_chain_spec)
    return node
