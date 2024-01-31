from __future__ import annotations

from typing import Final

from clive.__private.core.beekeeper import Beekeeper
from clive_local_tools.models import Keys, WalletInfo
import test_tools as tt

DIGEST_TO_SIGN: Final[str] = "9B29BA0710AF3918E81D7B935556D7AB205D8A8F5CA2E2427535980C2E8BDAFF"
MAX_BEEKEEPER_SESSION_AMOUNT: Final[int] = 64


async def test() -> None:
    # Tworzymy pomocnicza obiekt reprezentujacy wallet z piecioma parami kluczy priv/pub
    wallet = WalletInfo(name="name", password="pass", keys=Keys(count=5))
    async with await Beekeeper().launch() as beekeeper:
        # Tworzymy fizyczny wallet i importujemy do niego klucz
        await beekeeper.api.create(wallet_name=wallet.name, password=wallet.password)
        for pair in wallet.keys.pairs:
            await beekeeper.api.import_key(wallet_name=wallet.name, wif_key=pair.private_key.value)
        await beekeeper.api.lock(wallet_name=wallet.name)

        # Tworzymy maksymalna liczbe sesji (64)
        sessions = [beekeeper.token]
        notification_endpoint = beekeeper.notification_server_http_endpoint.as_string(with_protocol=False)
        for nr in range(MAX_BEEKEEPER_SESSION_AMOUNT - 1):  # -1 bo beekeeper w launch tworzy pierwsza sesje nie jawnie
            new_session = (
                await beekeeper.api.create_session(notifications_endpoint=notification_endpoint, salt=f"salt-{nr}")
            ).token
            sessions.append(new_session)

        # Otwieramy wallet w kazdej sesji, i podpisujemy
        for session in sessions:
            tt.logger.info(f"Start session {session}")
            async with beekeeper.with_session(session):
                await beekeeper.api.unlock(wallet_name=wallet.name, password=wallet.password)

                for pair in wallet.keys.pairs:
                    signature = (await beekeeper.api.sign_digest(sig_digest=DIGEST_TO_SIGN,
                                                                 public_key=pair.public_key.value)).signature
                    tt.logger.info(f"Signature {signature} in session {session}")
                    assert signature is not None
