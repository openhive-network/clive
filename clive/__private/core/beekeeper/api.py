from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any, TypeVar, get_type_hints

from clive.__private.core.beekeeper import model  # noqa: TCH001

if TYPE_CHECKING:
    from clive.__private.core.beekeeper import Beekeeper

FooT = TypeVar("FooT", bound=Callable[..., object])


def api(foo: FooT) -> FooT:
    @wraps(foo)
    def impl(this: BeekeeperApi, **kwargs: Any) -> Any:
        if foo.__name__ not in ["create_session"]:
            kwargs["token"] = this._owner.token
        return this._owner._send(
            response=get_type_hints(foo)["return"],
            endpoint=f"beekeeper_api.{foo.__name__}",
            **kwargs,
        ).result

    return impl  # type: ignore


class BeekeeperApi:
    def __init__(self, owner: Beekeeper) -> None:
        self._owner = owner

    @api
    def create(self, *, wallet_name: str, password: str | None = None) -> model.Create:
        raise NotImplementedError()

    @api
    def open(self, *, wallet_name: str) -> model.EmptyResponse:  # noqa: A003
        raise NotImplementedError()

    @api
    def set_timeout(self, *, seconds: int) -> model.EmptyResponse:
        raise NotImplementedError()

    @api
    def lock_all(self) -> model.EmptyResponse:
        raise NotImplementedError()

    @api
    def lock(self, *, wallet_name: str) -> model.EmptyResponse:
        raise NotImplementedError()

    @api
    def unlock(self, *, wallet_name: str, password: str) -> model.EmptyResponse:
        raise NotImplementedError()

    @api
    def import_key(self, *, wallet_name: str, wif_key: str) -> model.ImportKey:
        raise NotImplementedError()

    @api
    def remove_key(self, *, wallet_name: str, password: str, public_key: str) -> model.EmptyResponse:
        raise NotImplementedError()

    @api
    def list_wallets(self) -> model.ListWallets:
        raise NotImplementedError()

    @api
    def list_keys(self, *, wallet_name: str, password: str) -> model.ListKeys:
        raise NotImplementedError()

    @api
    def get_public_keys(self) -> model.GetPublicKeys:
        raise NotImplementedError()

    @api
    def sign_digest(self, *, sig_digest: str, public_key: str) -> model.SignDigest:
        raise NotImplementedError()

    @api
    def sign_transaction(
        self, *, transaction: dict[str, Any], chain_id: str, public_key: str, sig_digest: str
    ) -> model.SignTransaction:
        raise NotImplementedError()

    @api
    def get_info(self) -> model.GetInfo:
        raise NotImplementedError()

    @api
    def create_session(self, *, notifications_endpoint: str, salt: str) -> model.CreateSession:
        raise NotImplementedError()

    @api
    def close_session(self) -> model.EmptyResponse:
        raise NotImplementedError()
