from __future__ import annotations
import importlib

import oxidized_importer
import sys
import os

def monkey_patch_debug():
    orig_find_spec = oxidized_importer.OxidizedFinder.find_spec

    def debug_find_spec(self, fullname, path=None, target=None):
        print(f"[OXIDIZED] Asked for: {fullname}")
        spec = orig_find_spec(self, fullname, path, target)
        if spec is None:
            print(f"[OXIDIZED] => NOT FOUND, passing to next finder.")
        else:
            print(f"[OXIDIZED] => FOUND!")
        return spec

    oxidized_importer.OxidizedFinder.find_spec = debug_find_spec

# for name in sorted(sys.modules.keys()):
#     print("sys.modules:", name)

# monkey_patch_debug()
# Load those resources into an instance of our custom importer. This
# will read the index in the passed data structure and make all
# resources immediately available for importing.
finder = oxidized_importer.OxidizedFinder(relative_path_origin=os.getcwd())
finder.index_file_memory_mapped("/workspace/clive_workspace/clive/oxidized_resources")

# If the relative path of filesystem-based resources is not relative
# to the current executable (which is likely the ``python3`` executable),
# you'll need to set ``origin`` to the directory the resources are
# relative to.
# finder = oxidized_importer.OxidizedFinder(
#     relative_path_origin=os.path.dirname(os.path.abspath(__file__)),
# )
# finder = oxidized_importer.OxidizedFinder(
#     relative_path_origin="/workspace/clive_workspace/clive/")
# packed_data = finder.serialize_indexed_resources()

# finder.index_bytes(packed_data)


# Register the meta path finder as the first item, making it the
# first finder that is consulted.
# sys.meta_path.insert(0, finder)
# print(f"Indexy{finder.indexed_resources()}")
print("Udało się zaimportować oxidized_importer")
# At this point, you should be able to ``import`` modules defined
# in the resources data
# for name in sorted(sys.modules.keys()):
#     print("sys.modules po operacji:", name)

from decimal_add import decimal_add
from decimal_multi import decimal_multi

def compose(a: str, b: str) -> str:
    return decimal_add(a, b) + " " + decimal_multi(a, b)

if __name__ == "__main__":
    print(compose("1.1", "2.2"))
