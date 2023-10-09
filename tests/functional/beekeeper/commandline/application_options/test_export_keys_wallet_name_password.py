from __future__ import annotations

import json
from pathlib import Path
from typing import Final

from clive.__private.core.beekeeper import Beekeeper

PRIVATE_AND_PUBLIC_KEYS: Final[dict[str, str]] = {
    "6jACfK3P5xYFJQvavCwz5M8KR5EW3TcmSesArj9LJVGAq85qor": "5HwHC7y2WtCL18J9QMqX7awDe1GDsUTg7cfw734m2qFkdMQK92q",
    "5hjCkhcMKcXQMppa97XUbDR5dWC3c2K8h23P1ajEi2fT9YuagW": "5J7m49WCKnRBTo1HyJisBinn8Lk3syYaXsrzdFmfDxkejHLwZ1m",
    "5EjyFcCNidBSivAtTKvWWwWRNjakcRMB79QrbwMKprcTRBHtXz": "5JqStPwQgnXBdyRDDxCDyjfC8oNjgJuZsBkT6MMz6FopydAebbC",
    "8RgQ3yexUZjcVGxQ2i3cKywwKwhxqzwtCHPQznGUYvQ15ZvahW": "5JowdvuiDxoeLhzoSEKK74TCiwTaUHvxtRH3fkbweVEJZEsQJoc",
    "77P1n96ojdXcKpd5BRUhVmk7qFTfM2q2UkWSKg63Xi7NKyK2Q1": "5Khrc9PX4S8wAUUmX4h2JpBgf4bhvPyFT5RQ6tGfVpKEudwpYjZ",
}


def check_dumped_keys(wallet_path: Path, extracted_keys: dict[str, str]) -> None:
    """Check if keys has been saved in dumped {wallet_name}.keys file."""
    with wallet_path.open() as keys_file:
        keys = json.load(keys_file)
        assert extracted_keys == keys
        assert extracted_keys == PRIVATE_AND_PUBLIC_KEYS

    wallet_path.unlink()


async def test_export_keys(tmp_path: Path) -> None:
    """Test will check command line flag --export-keys-wallet-name --export-keys-wallet-password."""
    wallet_name = "test_export_keys"
    wallet_name_keys = f"{wallet_name}.keys"

    extract_path = tmp_path / wallet_name
    extract_path.mkdir()

    async with Beekeeper() as beekeeper:
        create = await beekeeper.api.create(wallet_name=wallet_name)
        await beekeeper.api.open(wallet_name=wallet_name)
        await beekeeper.api.unlock(password=create.password, wallet_name=wallet_name)
        for key in PRIVATE_AND_PUBLIC_KEYS.values():
            await beekeeper.api.import_key(wif_key=key, wallet_name=wallet_name)

        keys = await beekeeper.export_keys_wallet(
            wallet_name=wallet_name, wallet_password=create.password, extract_to=extract_path
        )
        # Check extract_to path
        check_dumped_keys(extract_path / wallet_name_keys, keys)
        # Check default path of wallet_name.keys
        check_dumped_keys(Path.cwd() / wallet_name_keys, keys)

    bk = Beekeeper()
    keys1 = await bk.export_keys_wallet(
        wallet_name=wallet_name, wallet_password=create.password, extract_to=extract_path
    )
    check_dumped_keys(extract_path / wallet_name_keys, keys1)
    check_dumped_keys(Path.cwd() / wallet_name_keys, keys1)
    assert bk.is_running is False
