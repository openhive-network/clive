from __future__ import annotations

import stat

import test_tools as tt

from clive.__private.ui.bindings import CLIVE_PREDEFINED_BINDINGS
from clive_local_tools.tui.bindings.helpers import DEFAULT_BINDINGS_FILE_PATH


def main() -> None:
    CLIVE_PREDEFINED_BINDINGS.dump_toml(DEFAULT_BINDINGS_FILE_PATH)
    DEFAULT_BINDINGS_FILE_PATH.chmod(stat.S_IRUSR | stat.S_IWUSR)
    tt.logger.info(f"File `{DEFAULT_BINDINGS_FILE_PATH}` with default bindings was regenerated")


if __name__ == "__main__":
    main()
