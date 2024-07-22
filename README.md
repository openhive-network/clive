# clive

<a href="https://gitlab.syncad.com/hive/clive/-/commits/develop" target="_blank" rel="noopener noreferrer" data-qa-selector="badge_image_link" data-qa-link-url="https://gitlab.syncad.com/hive/clive/-/commits/develop" style=""><img src="https://gitlab.syncad.com/hive/clive/badges/develop/pipeline.svg" aria-hidden="true" class="project-badge"></a>

[WORK IN PROGRESS]

# Table of contents

1. [Introduction](#introduction)
2. [Requirements](#requirements)
3. [Installation in development mode](#installation-in-development-mode)
4. [Running](#running)
5. [Running via Docker](#running-via-docker)

# Introduction

**clive** is a combination of the cli and hive words. It's an interactive command line application for interacting with
the [Hive](https://gitlab.syncad.com/hive/hive) blockchain. Inspired by midnight commander, written in Python.

# Requirements

- python3.10
- poetry (for development)

# Installation in development mode

Since clive is still in development, it's not available on PyPI. To install it in development mode, it's recommended
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

# Running

You can simply invoke the TUI application by running the `clive` command.
If you want to use the CLI mode, pass any argument to the `clive` command.

 ```bash
 clive         # Run the TUI application
 clive --help  # Run the CLI application
 ```

# Running via Docker

In order to run clive via Docker, you need to have Docker installed on your machine. You can find the installation
instructions [here](https://docs.docker.com/get-docker/).

You can then run a docker container with your desired version of Clive.
It's recommended to use official clive docker images available at https://hub.docker.com/r/hiveio/clive/tags

The simplest way to run clive is to do it via the `run_instance.sh` script like:

 ```bash
# e.g: ./scripts/run_instance.sh hiveio/clive:v1.27.5.13
./scripts/run_instance.sh <latest_version>
```

If you want to run clive in the CLI mode, you should include the `--cli` flag in the command:

```bash
./scripts/run_instance.sh <latest_version> --cli
```

For more information about the script, you can run it with the `--help` flag:

 ```bash
./scripts/run_instance.sh --help
```

That's the desired approach, because the `run_instance.sh` script will take care of any additional flags that need to be
passed to the `docker run`. Like the one that remaps the detach keys to `ctrl-@,ctrl-q` to avoid detaching from the
container when interacting with the TUI. Additionally, it will automatically map the volume to the data directory used
inside container to persist the data and configuration between runs.

However, if you still want to run clive manually via `docker run`, which is not recommended, you can see what the docker
invocation command should look like in the mentioned `run_instance.sh` script.

It should be similar to the following command, but we do not guarantee that this line will work as expected, as the
script may be updated:

```bash
docker run -ti -v ./clive-data:/root/.clive --detach-keys 'ctrl-@,ctrl-q' <latest_version>
```
