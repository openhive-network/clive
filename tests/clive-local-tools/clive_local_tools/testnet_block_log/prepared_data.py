from __future__ import annotations

from pathlib import Path

from test_tools import BlockLog
from test_tools.__private.node_config import NodeConfig


def get_alternate_chain_spec_path() -> Path:
    return Path(__file__).parent.absolute() / "alternate-chain-spec.json"


def get_block_log() -> BlockLog:
    path = Path(__file__).parent.absolute() / "blockchain" / "block_log"
    return BlockLog(path)


def get_config() -> NodeConfig:
    path = Path(__file__).parent.absolute() / "config.ini"
    config = NodeConfig()
    config.load_from_file(path)
    return config


def get_time_offset() -> str:
    path = Path(__file__).parent.absolute() / "timestamp"
    with Path.open(path) as file:
        return file.read()
