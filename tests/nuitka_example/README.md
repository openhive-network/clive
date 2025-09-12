__BUILD__

_before run_:

    pip install nuitka
    pip install patchelf

_command_:

    nuitka --standalone --jobs=16 --lto=yes --static-libpython=yes --output-dir=nuitkabuild --follow-imports --include-module=aiohttp --include-module=textual --include-module=dynaconf --include-module=typer --include-module=decimal compose.py


--standalone: This option creates a fully self-contained application, meaning all necessary Python modules, libraries, and the interpreter itself are bundled together. The final executable will work on other machines without needing a Python installation.

--jobs=16: This sets the number of parallel jobs (threads) to 16 for the compilation process. Using more jobs can significantly speed up the compilation on multi-core processors.

--lto=yes: This enables Link-Time Optimization (LTO). LTO is an advanced compiler optimization that happens at link time. It allows the compiler to make better decisions about what code to remove or optimize, resulting in a smaller, more efficient executable.

--static-libpython=yes: This option links the Python interpreter statically into the executable. This is another way to ensure the application is fully standalone and doesn't rely on a system-wide Python installation.

--output-dir=nuitkabuild: This specifies the directory where Nuitka will place the compiled output. The final executable and its dependencies will be in a folder named nuitkabuild.

--follow-imports: This tells Nuitka to analyze the code and automatically include all modules that are imported by the main script and its dependencies. This is a very common and useful option for bundling all required code.

--include-module=<module_name>: This is a powerful option for manually including modules that Nuitka's automatic import analysis might miss. It's often used for modules that are dynamically imported or for which Nuitka's import detection is not perfect.

_run_:

    time ./nuitkabuild/compose.dist/compose.bin