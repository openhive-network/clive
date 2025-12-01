# clive

<a href="https://gitlab.syncad.com/hive/clive/-/commits/develop" target="_blank" rel="noopener noreferrer" data-qa-selector="badge_image_link" data-qa-link-url="https://gitlab.syncad.com/hive/clive/-/commits/develop" style=""><img src="https://gitlab.syncad.com/hive/clive/badges/develop/pipeline.svg" aria-hidden="true" class="project-badge"></a>

[WORK IN PROGRESS]

# Table of contents

1. [Introduction](#introduction)
2. [Running](#running)
3. [Using the CLI environment](#using-the-cli-environment)
4. [Installation in development mode](#installation-in-development-mode)
5. [Running in development](#running-in-development)

# Introduction

**clive** is a portmanteau of two words: CLI (command-line-interface) and Hive. Clive is an command line application for
interacting with the [Hive](https://gitlab.syncad.com/hive/hive) blockchain. Clive also has a terminal user-interface
(TUI) that supports mouse-based navigation that is inspired by midnight commander. Both the CLI and the TUI are written
in Python. Clive is being designed in part to replace the original Hive CLI which is primarily used by power users and
for writing tests for Hive.

# Running

The recommended way to run Clive is by using one of the dedicated scripts: `start_clive.sh` or `start_clive_cli.sh`.

The latest version of the Clive startup scripts can be obtained from: https://gtg.openhive.network/get/clive/

These scripts are generated during the CI pipeline and are available for download from the artifacts (for authorized
users only).

Using `start_clive.sh` will start the TUI application, while `start_clive_cli.sh` will enter the CLI environment.

# Using the CLI environment

For a full overview of all available commands and sub-commands, see the
[Clive CLI commands structure](./docs/cli_commands_structure.md).

You can simply invoke the TUI application by running the `clive` command with no arguments. If you want to use the CLI
mode, pass an argument or subcommand to the `clive` command like `--help` or `show profile`.

```bash
clive               # Start the TUI application
clive --help        # See help for the CLI application
clive show profile  # Run the `show profile` CLI command
```

# Installation in development mode

To install Clive in the development mode (from sources), it's recommended to install it via poetry as poetry is the
build system that Clive uses.

1. [Install poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
2. Clone the repository

    ```bash
    git clone https://gitlab.syncad.com/hive/clive.git
    ```

3. Create a virtual environment (you can do it your way, using poetry, pyenv, virtualenv, pipx, etc.)

    ```bash
    cd clive/                 # Go to repository root directory
    python -m venv venv/      # Create virtual environment in the venv/ directory
    . venv/bin/activate       # Activate the virtual environment
    ```

4. Install CLIVE

    ```bash
    poetry install  # Install CLIVE and its dev-dependencies in the virtual environment
    ```

# Running in development

Running in development mode works the same way as running from the CLI environment. It is explained
[in the section above](#using-the-cli-environment). The only prerequisite is to spawn the beekeeper if you want to run
the CLI commands. It can be done with `clive beekeeper spawn` command. You can also use the `clive-dev` instead of the
`clive` entry point to include extra debugging information.
