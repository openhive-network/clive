from __future__ import annotations

from distutils.command.build import build
from multiprocessing import cpu_count
from os import environ
from pathlib import Path
from shutil import copyfile, which
from subprocess import run as run_process
from typing import Any

from setuptools import setup


def log(*args: Any) -> None:
    print(*args)  # noqa: T201


class CustomBuild(build):
    output_binary_name = "libwax.so"
    current_dir = Path(__file__).parent.absolute()
    packages_dir = current_dir / "package"
    wax_package_shared_lib = packages_dir / output_binary_name
    build_dir = current_dir / ".build"
    logs_dir = build_dir / "logs"

    def __configure_project(self, cmake_command: str, ninja_command: str | None, make_command: str | None) -> str:
        configure_args = ["-GNinja"]
        build_command = ninja_command
        if build_command is None:
            assert make_command is not None, "cannot find neither ninja nor make"
            log(f"cannot find ninja, using {make_command} instead")
            build_command = make_command
            configure_args = []

        if "BUILD_HIVE_TESTNET" in environ:
            configure_args.append("-DBUILD_HIVE_TESTNET=ON")

        self.build_dir.mkdir(exist_ok=True)
        log(f"build will be performed in: {self.build_dir}")
        self.logs_dir.mkdir(exist_ok=True)
        log(f"all build logs will be saved to: {self.logs_dir.as_posix()}")
        with (self.logs_dir / "cmake_stdout.log").open("w") as stdout, (self.logs_dir / "cmake_stderr.log").open(
            "w"
        ) as stderr:
            log(f"configuring with {cmake_command}")
            run_process(
                [
                    cmake_command,
                    "-S",
                    self.current_dir.as_posix(),
                    "-B",
                    self.build_dir.as_posix(),
                    *configure_args,
                ],
                stdout=stdout,
                stderr=stderr,
            ).check_returncode()
            log("configuration succeed")
            return build_command

    def __build_project(self, build_command: str) -> None:
        with (self.logs_dir / "build_stdout.log").open("w") as stdout, (self.logs_dir / "build_stderr.log").open(
            "w"
        ) as stderr:
            log(f"building with {build_command}")
            run_process(
                [build_command, "-j", f"{cpu_count()}"],
                stdout=stdout,
                stderr=stderr,
                cwd=self.build_dir,
            ).check_returncode()
            log("build succeeded")

    def __discover_binaries(self) -> tuple[str, str | None, str | None]:
        cmake = which("cmake")
        assert cmake is not None, "cannot find cmake"
        ninja = which("ninja")
        make = which("make")
        assert ninja is not None or make is not None, "cannot find any build program"
        return cmake, ninja, make

    @classmethod
    def __git_revision(cls) -> str:
        git_directory = cls.current_dir.parent / ".git"
        head: str = (git_directory / "HEAD").read_text().split(" ")[-1].strip("\n")
        if (branch_ref := (git_directory / head)).exists():
            head = branch_ref.read_text()
        return head[:8]

    @classmethod
    def package_binary_path(cls) -> Path:
        return cls.wax_package_shared_lib.with_stem(cls.wax_package_shared_lib.stem + "-" + cls.__git_revision())

    def __copy_binary_to_package_dir(self) -> None:
        output_binary = self.build_dir / self.output_binary_name
        assert output_binary.exists()
        dest = self.package_binary_path()
        log(f"copying library from {output_binary} to {dest}")
        copyfile(output_binary, dest)

    def run(self) -> None:
        if "WAX_SKIP_BUILD" not in environ:
            cmake, ninja, make = self.__discover_binaries()
            build_command = self.__configure_project(cmake, ninja, make)
            self.__build_project(build_command)
        self.__copy_binary_to_package_dir()
        super().run()


if __name__ == "__main__":
    setup(
        name="wax",
        version="0.0.0",
        packages=["wax"],
        package_dir={"wax": "package"},
        package_data={"wax": [CustomBuild.package_binary_path().name, "wax.pyi", "py.typed"]},
        cmdclass={"build": CustomBuild},  # type: ignore[dict-item]
        install_requires=[
            "cython==0.29.34",
            "setuptools==59.6.0",
            "scikit-build==0.17.2",
            "types-setuptools==67.7.0.2",
        ],
    )
