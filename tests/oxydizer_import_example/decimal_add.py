from __future__ import annotations


import os
import sys

import oxidized_importer

# # Load those resources into an instance of our custom importer. This
# # will read the index in the passed data structure and make all
# # resources immediately available for importing.
# finder = oxidized_importer.OxidizedFinder()
# finder.index_file_memory_mapped("oxidized_resources")

# # If the relative path of filesystem-based resources is not relative
# # to the current executable (which is likely the ``python3`` executable),
# # you'll need to set ``origin`` to the directory the resources are
# # relative to.
# finder = oxidized_importer.OxidizedFinder(
#     relative_path_origin=os.path.dirname(os.path.abspath(__file__)),
# )
# packed_data = finder.serialize_indexed_resources()

# finder.index_bytes(packed_data)

# # Register the meta path finder as the first item, making it the
# # first finder that is consulted.
# sys.meta_path.insert(0, finder)
# print("Udało się zaimportować oxidized_importer")
# # At this point, you should be able to ``import`` modules defined
# # in the resources data

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
