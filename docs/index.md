hide:
    - toc
    - navigation


# Home

## Introduction

---
clive is a portmanteau of two words: CLI (command-line-interface) and Hive. Clive is an command line application for interacting with
the Hive blockchain. Clive also has a terminal user-interface (TUI) that supports mouse-based navigation that is inspired by midnight commander. Both the CLI and the TUI are written in Python. Clive is being designed in part to replace the original Hive CLI which is primarily used by power users and for writing tests for Hive.

## Running

---
The recommended way to run Clive is by using one of the dedicated scripts: start_clive.sh or start_clive_cli.sh.
The latest version of the Clive startup scripts can be obtained from:
https://gtg.openhive.network/get/clive/
These scripts are generated during the CI pipeline and are available for download from the artifacts (for authorized users only).
Using start_clive.sh will start the TUI application, while start_clive_cli.sh will enter the CLI environment.

## Using the CLI environment

---
You can simply invoke the TUI application by running the clive command with no arguments.
If you want to use the CLI mode, pass an argument or subcommand to the clive command like --help or show profile.

```
clive               # Start the TUI application
clive --help        # See help for the CLI application
clive show profile  # Run the `show profile` CLI command
```

## Installation in development mode

---
To install Clive in the development mode (from sources), it's recommended
to install it via poetry as poetry is the build system that Clive uses.


1 Install poetry


2 Clone the repository

```
git clone https://gitlab.syncad.com/hive/clive.git
```

3 Create a virtual environment (you can do it your way, using poetry, pyenv, virtualenv, pipx, etc.)
```
cd clive/                 # Go to repository root directory
python -m venv venv/      # Create virtual environment in the venv/ directory
. venv/bin/activate       # Activate the virtual environment
```

4 Install CLIVE
```
poetry install  # Install CLIVE and its dev-dependencies in the virtual environment
```

## Running in development

---
Running in development mode works the same way as running from the CLI environment. It is explained in the section above.
The only prerequisite is to spawn the beekeeper if you want to run the CLI commands. It can be done with clive beekeeper spawn command.
You can also use the clive-dev instead of the clive entry point to include extra debugging information.


## Table of contents

---

Quickly find what you're looking for depending on
your use case by looking at the different pages.

1. [Home](index.md)
2. [Reference](Reference.md)
