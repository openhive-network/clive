import os
import stat
import sys

import oxidized_importer

from schemas.operations import DeleteCommentOperation
import typer
import dynaconf
from textual import validation
import aiohttp

# Create a collector to help with managing resources.
collector = oxidized_importer.OxidizedResourceCollector(
    allowed_locations=["in-memory", "filesystem-relative"]
)

# Add all known Python resources by scanning sys.path.
# Note: this will pull in the Python standard library and
# any other installed packages, which may not be desirable!
for path in sys.path:
    # Only directories can be scanned by oxidized_importer.
    if os.path.isdir(path):
        for resource in oxidized_importer.find_resources_in_path(path):
            if isinstance(resource, oxidized_importer.PythonExtensionModule):
                collector.add_filesystem_relative("oxidizer_lib", resource)
            else:
                collector.add_in_memory(resource)
print(1)
# Turn the collected resources into ``OxidizedResource`` and file
# install rules.
resources, file_installs = collector.oxidize()

print(2)
# Now index the resources so we can serialize them.
finder = oxidized_importer.OxidizedFinder(relative_path_origin=os.getcwd())
finder.add_resources(resources)
print(3)

# Turn the indexed resources into an opaque blob.
print(f"indexed_resources {finder.indexed_resources()}")

packed_data = finder.serialize_indexed_resources()
print(3)

# Write out that data somewhere.
with open("oxidized_resources", "wb") as fh:
    fh.write(packed_data)
print(4)

# Then for all the file installs, materialize those files.
for (path, data, executable) in file_installs:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("wb") as fh:
        fh.write(data)

    if executable:
        path.chmod(path.stat().st_mode | stat.S_IEXEC)
print(5)
