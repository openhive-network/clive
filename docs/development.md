---
hide:
    - navigation
---

## Installation in development mode

---

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

## Running in development

---

Running in development mode works the same way as running from the CLI environment. Please refer to the
[Using the CLI environment](index.md#using-the-cli-environment) section. The only prerequisite is to spawn the beekeeper
if you want to run the CLI commands. It can be done with `clive beekeeper spawn` command. You can also use the
`clive-dev` instead of the `clive` entry point to include extra debugging information.
