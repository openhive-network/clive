from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from textual import __name__ as textual_package_name

from clive.__private.ui import __name__ as ui_package_name
from clive.main import __file__ as path_to_clive_main
from wax import __name__ as wax_package_name


def _get_imports_tree(file_path: Path, *args: str) -> str:
    command = f"/bin/bash -c 'python3 -X importtime {file_path.absolute().as_posix()}"
    if args:
        command += f" {' '.join(args)}'"

    result = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)

    stderr = result.stderr
    assert result.returncode == 0, f"Failed to get imports tree:\n{stderr}"

    return stderr


def _get_cli_help_imports_tree() -> str:
    return _get_imports_tree(Path(path_to_clive_main), "--help")


@pytest.mark.parametrize(("package_name"), [ui_package_name, textual_package_name, wax_package_name])
def test_not_imported_during_cli_help(package_name: str) -> None:
    # ACT
    cli_imports_tree = _get_cli_help_imports_tree()

    # ASSERT
    assert package_name not in cli_imports_tree, f"{package_name} shouldn't be imported during CLI help."
