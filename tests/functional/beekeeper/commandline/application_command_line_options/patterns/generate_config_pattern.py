from __future__ import annotations

from pathlib import Path

from clive.__private.core.beekeeper import Beekeeper

if __name__ == "__main__":
    config_pattern_file = Path(__file__).parent / "config.ini"
    Beekeeper().generate_beekeepers_default_config(destination=config_pattern_file)
