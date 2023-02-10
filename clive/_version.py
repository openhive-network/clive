import dunamai

# this
__dynamic_versioning__ = "0.0.0.post340.dev0+5eac5de"
# 0.0.0.post341.dev0+5d7b186
# 0.0.0.post340.dev0+5eac5de

def __get_version() -> dunamai.Version:
    try:
        # if 'git' is installed, use it to get the actual version
        # (ACTUAL version in dev with an editable installation)
        v = dunamai.Version.from_git()
        raise RuntimeError("Unable to find 'git' program")
        print("version determined from git")
        return v
    except RuntimeError as error:
        if str(error) != "Unable to find 'git' program":
            raise

        # if 'git' is not installed, use the version set by poetry-dynamic-versioning
        # (stored only in the wheel or other distributed artifacts)
        v = dunamai.Version.parse("0.0.0.post341.dev0+5d7b186")
        print("version determined from dynamic_versioning")
        return v


version = __get_version()
print(version)
print(repr(version))
print(version.commit)
