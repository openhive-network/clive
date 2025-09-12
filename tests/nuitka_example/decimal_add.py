from __future__ import annotations


import decimal

from schemas.operations import DeleteCommentOperation
import typer
import dynaconf
from textual import validation
import aiohttp


def decimal_add(a: str, b: str) -> str:
    DeleteCommentOperation(author="alice", permlink="permlink")
    typer.echo("Using asyncio from")
    dynaconf.ValidationError(message="settings")
    validation.Regex("pattern")
    aiohttp.ClientError("Client error")

    decimal.getcontext().prec = 50
    dec_a = decimal.Decimal(a)
    dec_b = decimal.Decimal(b)
    result = dec_a + dec_b
    return format(result, 'f')
