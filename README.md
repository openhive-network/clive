# clive

<a href="https://gitlab.syncad.com/hive/clive/-/commits/develop" target="_blank" rel="noopener noreferrer" data-qa-selector="badge_image_link" data-qa-link-url="https://gitlab.syncad.com/hive/clive/-/commits/develop" style=""><img src="https://gitlab.syncad.com/hive/clive/badges/develop/pipeline.svg" aria-hidden="true" class="project-badge"></a>

[WORK IN PROGRESS]

# Table of contents

1. [Introduction](#introduction)
2. [Running](#running)
3. [Installation in development mode](#installation-in-development-mode)
4. [Running in development / running from CLI](#running-in-development--running-from-cli)

# Introduction

**clive** is a portmanteau of two words: CLI (command-line-interface) and Hive. Clive is an command line application for interacting with
the [Hive](https://gitlab.syncad.com/hive/hive) blockchain. Clive also has a terminal user-interface (TUI) that supports mouse-based navigation that is inspired by midnight commander. Both the CLI and the TUI are written in Python. Clive is being designed in part to replace the original Hive CLI which is primarily used by power users and for writing tests for Hive.

# Running

The recommended way to run Clive is by using one of the dedicated scripts: `start_clive.sh` or `start_clive_cli.sh`.
These scripts are generated during the CI pipeline and are available for download from the artifacts (for authorized users only).

The latest version of the Clive startup scripts can also be obtained from:
https://gtg.openhive.network/get/clive/

# Installation in development mode

To install Clive in the development mode, it's recommended
to install it via poetry as it includes dependencies used during development.

1. [Install poetry](https://python-poetry.org/docs/#installing-with-the-official-installer)
2. Clone the repository

    ```bash
    git clone https://gitlab.syncad.com/hive/clive.git
    ```

3. Create a virtual environment (you can do it your way, using poetry, pyenv, virtualenv, pipx, etc.)

    ```bash
    cd clive/                # Go to repository root directory
    python3.10 -m venv venv/  # Create virtual environment in the venv/ directory
    . venv/bin/activate      # Activate the virtual environment
    ```

4. Install CLIVE

    ```bash
    poetry install  # Install CLIVE and its dev-dependencies in the virtual environment
    ```

# Running in development / running from CLI

You can simply invoke the TUI application by running the `clive` command.
If you want to use the CLI mode, pass an argument to the `clive` command like `--help`.

 ```bash
 clive         # Run the TUI application
 clive --help  # Run the CLI application
 ```
