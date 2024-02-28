from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar, get_type_hints

from clive.__private.core.beekeeper import model  # noqa: TCH001

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper

FooT = TypeVar("FooT", bound=Callable[..., object])


def is_token_already_passed(**kwargs: Any) -> bool:
    return "token" in kwargs and kwargs["token"] is not None


def api(foo: FooT) -> FooT:
    @wraps(foo)
    async def impl(this: BeekeeperApi, **kwargs: Any) -> Any:
        if foo.__name__ not in ["create_session"] and not is_token_already_passed(**kwargs):
            kwargs["token"] = this._owner.token
        return (
            await this._owner._send(
                result_model=get_type_hints(foo)["return"],
                endpoint=f"beekeeper_api.{foo.__name__}",
                **kwargs,
            )
        ).result

    return impl  # type: ignore


class BeekeeperApi:
    def __init__(self, owner: Beekeeper) -> None:
        self._owner = owner

    @api
    async def create(self, *, wallet_name: str, password: str | None = None) -> model.Create:
        raise NotImplementedError

    @api
    async def open(self, *, wallet_name: str) -> model.EmptyResponse:
        """Open wallet file / mount hardware key."""
        raise NotImplementedError

    @api
    async def close(self, *, wallet_name: str) -> model.EmptyResponse:
        """
        Wallet file has been closed / hardware key has been unmounted, other app can access it now.

        Can be called without lock, which is done implicitly.
        """
        raise NotImplementedError

    @api
    async def set_timeout(self, *, seconds: int) -> model.EmptyResponse:
        raise NotImplementedError

    @api
    async def lock_all(self) -> model.EmptyResponse:
        raise NotImplementedError

    @api
    async def lock(self, *, wallet_name: str) -> model.EmptyResponse:
        """Wallet still can be unlocked again and is visible, but private keys are secure."""
        raise NotImplementedError

    @api
    async def unlock(self, *, wallet_name: str, password: str) -> model.EmptyResponse:
        """
        Pass password so private keys are available for signing.

        Can be called without open, which is done implicitly.
        """
        raise NotImplementedError

    @api
    async def import_key(self, *, wallet_name: str, wif_key: str) -> model.ImportKey:
        raise NotImplementedError

    @api
    async def remove_key(self, *, wallet_name: str, password: str, public_key: str) -> model.EmptyResponse:
        raise NotImplementedError

    @api
    async def list_wallets(self) -> model.ListWallets:
        raise NotImplementedError

    @api
    async def list_keys(self, *, wallet_name: str, password: str) -> model.ListKeys:
        raise NotImplementedError

    @api
    async def get_public_keys(self) -> model.GetPublicKeys:
        raise NotImplementedError

    @api
    async def sign_digest(self, *, sig_digest: str, public_key: str) -> model.SignDigest:
        raise NotImplementedError

    @api
    async def sign_transaction(
        self, *, transaction: dict[str, Any], chain_id: str, public_key: str, sig_digest: str
    ) -> model.SignTransaction:
        raise NotImplementedError

    @api
    async def get_info(self) -> model.GetInfo:
        raise NotImplementedError

    @api
    async def create_session(self, *, notifications_endpoint: str, salt: str) -> model.CreateSession:
        raise NotImplementedError

    @api
    async def close_session(self, *, token: None | str = None) -> model.EmptyResponse:
        raise NotImplementedError
