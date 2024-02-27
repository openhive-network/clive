import os
from pathlib import Path

import test_tools as tt
from hive_local_tools import ALTERNATE_CHAIN_JSON_FILENAME
from tests.functional.full_block_generator.generate_block_log_with_varied_signature_types import WITNESSES

from tests.functional.full_block_generator.full_block_generator import SHARED_MEMORY_FILE_SIZE, \
    WEBSERVER_THREAD_POOL_SIZE, SHARED_MEMORY_FILE_DIRECTORY, SIGNATURE_TYPE


def infinite_init_node(signature_type):
    # fixme: delete after repair ( https://gitlab.syncad.com/hive/test-tools/-/issues/44 ). From this
    generated_directory = Path(__file__).parent / "generated"
    if not os.path.exists(generated_directory):
        os.makedirs(generated_directory)
    # fixme: To this

    block_log_directory = Path(__file__).parent / f"block_log_{signature_type}"
    block_log = tt.BlockLog(block_log_directory / "block_log")
    alternate_chain_spec_path = block_log_directory / ALTERNATE_CHAIN_JSON_FILENAME

    node = tt.InitNode()

    node.config.plugin.remove("account_by_key")
    node.config.plugin.remove("state_snapshot")
    node.config.plugin.remove("account_by_key_api")
    node.config.shared_file_size = f"{SHARED_MEMORY_FILE_SIZE}G"
    node.config.webserver_thread_pool_size = f"{str(WEBSERVER_THREAD_POOL_SIZE)}"
    node.config.webserver_http_endpoint = "0.0.0.0:22023"
    node.config.log_logger = (
        '{"name":"default","level":"info","appender":"stderr"} '
        '{"name":"user","level":"debug","appender":"stderr"} '
        '{"name":"chainlock","level":"error","appender":"p2p"} '
        '{"name":"sync","level":"debug","appender":"p2p"} '
        '{"name":"p2p","level":"debug","appender":"p2p"}'
    )

    for witness in WITNESSES:
        key = tt.Account(witness).private_key
        node.config.witness.append(witness)
        node.config.private_key.append(key)

    node.run(
        replay_from=block_log,
        time_offset=tt.Time.serialize(block_log.get_head_block_time(), format_=tt.TimeFormats.TIME_OFFSET_FORMAT),
        wait_for_live=True,
        arguments=[
            f"--alternate-chain-spec={str(alternate_chain_spec_path)}",
            f"--shared-file-dir={SHARED_MEMORY_FILE_DIRECTORY}",
        ],
    )

    while True:
        node.wait_number_of_blocks(1)


if __name__ == '__main__':
    infinite_init_node(SIGNATURE_TYPE)
