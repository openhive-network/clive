from __future__ import annotations

from pathlib import Path

import test_tools as tt

from clive.__private.core.beekeeper import Beekeeper


def check_with_pattern(generated_file: Path) -> None:
    pattern_file_path = Path(__file__).parent / "patterns" / "config.ini"
    pattern = pattern_file_path.read_text()
    incoming = generated_file.read_text()
    assert pattern.strip() == incoming.strip(), "Generated config is different than pattern."


def test_default_config() -> None:
    """Test will check if beekeeper default config hasn't changed."""
    # ARRANGE & ACT
    path_to_generated_config = tt.context.get_current_directory() / "config.ini"
    Beekeeper().generate_beekeepers_default_config(destination=path_to_generated_config)

    # ASSERT
    check_with_pattern(path_to_generated_config)
