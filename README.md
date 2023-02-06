# clive

<a href="https://gitlab.syncad.com/hive/clive/-/commits/develop" target="_blank" rel="noopener noreferrer" data-qa-selector="badge_image_link" data-qa-link-url="https://gitlab.syncad.com/hive/clive/-/commits/develop" style=""><img src="https://gitlab.syncad.com/hive/clive/badges/develop/pipeline.svg" aria-hidden="true" class="project-badge"></a>

[WORK IN PROGRESS]

# Table of contents

1. [Introduction](#introduction)
2. [Requirements](#requirements)
3. [Installation in development mode](#installation)
4. [Running](#running)
5. [Running via Docker](#running-via-docker)

# Introduction

**clive** is a combination of the cli and hive words. It's an interactive command line application for interacting with
the [Hive](https://gitlab.syncad.com/hive/hive) blockchain. Inspired by midnight commander, written in Python.

# Requirements

- python3.8
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
    python3.8 -m venv venv/  # Create virtual environment in the venv/ directory
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

Then you can run a docker container always with the latest master/develop version of clive by running the following
command (depending on the branch you want to use, e.g. develop):

 ```bash
docker pull registry.gitlab.syncad.com/hive/clive/develop:latest   && docker run -ti  registry.gitlab.syncad.com/hive/clive/develop:latest
 ```

If you want to run clive via CLI, you can pass any argument to the `docker run` command:

 ```bash
docker run -ti  registry.gitlab.syncad.com/hive/clive/develop:latest --help
 ```
