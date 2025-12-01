hide: - navigation

## Introduction

---

clive is a portmanteau of two words: CLI (command-line-interface) and Hive. Clive is an command line application for
interacting with the [Hive](https://gitlab.syncad.com/hive/hive) blockchain. Clive also has a terminal user-interface
(TUI) that supports mouse-based navigation that is inspired by midnight commander. Both the CLI and the TUI are written
in Python. Clive is being designed in part to replace the original Hive CLI which is primarily used by power users and
for writing tests for Hive.

## Running

---

The recommended way to run Clive is by using one of the dedicated scripts: `start_clive.sh` or `start_clive_cli.sh`.

The latest version of the Clive startup scripts can be obtained from [there](https://gtg.openhive.network/get/clive/).

These scripts are generated during the CI pipeline and are available for download from the artifacts (for authorized
users only).

Using `start_clive.sh` will start the TUI application, while `start_clive_cli.sh` will enter the CLI environment.

## Using the CLI environment

---

You can simply invoke the TUI application by running the `clive` command with no arguments. If you want to use the CLI
mode, pass an argument or subcommand to the `clive` command like `--help` or `show profile`.

```bash
clive               # Start the TUI application
clive --help        # See help for the CLI application
clive show profile  # Run the `show profile` CLI command
```

## Table of contents

---

Quickly find what you're looking for depending on your use case by looking at the different pages.

1. [Home](index.md)
2. [Development](development.md)
3. [CLI commands structure](cli_commands_structure.md)
4. [Reference](reference.md)
