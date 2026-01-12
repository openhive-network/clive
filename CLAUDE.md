# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Clive** is a CLI and TUI (Terminal User Interface) application for interacting with the Hive blockchain. It's written
in Python and designed to replace the original Hive CLI for power users and testing. The TUI features mouse-based
navigation inspired by midnight commander.

-   **Main entry point**: `clive` - automatically launches TUI when run without arguments, or CLI mode when arguments
    are provided like `clive` for TUI and `clive --help` for CLI
-   **Development entry point**: `clive-dev` - includes extra debugging information
-   **Python version**: (see `requires-python` in `pyproject.toml`, restricted due to wax dependency)
-   **Build system**: Poetry
-   **Main branch**: `develop` (use this for PRs, not `main`)

## GitLab Instance

This project uses **gitlab.syncad.com**, NOT gitlab.com.

-   Repository: https://gitlab.syncad.com/hive/clive
-   Use `glab api "projects/hive%2Fclive/..."` for API calls

## Claude Code Commands

Available slash commands for development workflows:

| Command        | Description                                                   |
| -------------- | ------------------------------------------------------------- |
| `/smoke`       | Run smoke test                                                |
| `/lint`        | Run all pre-commit hooks                                      |
| `/test <args>` | Run pytest with shortcuts: `unit`, `cli`, `tui`, `functional` |
| `/reflection`  | Analyze and improve Claude Code configuration                 |

## Essential Commands

### Installation and Setup

```bash
# Install dependencies (must be run from repository root)
poetry install

# When updating dependencies and hive submodule is updated also, test-tools should be forced to uninstall first
pip uninstall -y test-tools && poetry install
```

### Running Clive

```bash
# Launch TUI (default)
clive

# Use CLI mode
clive --help
clive show profile
clive configure profile create

# Development mode with debug info (useful for presenting full stack-trace instead of pretty errors in CLI)
clive-dev
```

### Linting and Formatting

```bash
# Run all pre-commit hooks (include tools like ruff, mypy and additional hooks)
pre-commit run --all-files

# Lint with Ruff
ruff check clive/ tests/

# Format code
ruff format clive/ tests/

# Type checking
mypy clive/ tests/
```

### Testing

Use `/smoke`, `/lint`, and `/test` slash commands for common workflows (see
[Claude Code Commands](#claude-code-commands)).

```bash
# Run a specific test (example)
pytest tests/unit/test_date_utils.py::test_specific_function -v

# Run with timeout (important for tests that may hang)
pytest --timeout=600

# Run without parallelization (for debugging)
pytest -n 0
```

**Note**: Tests require the embedded testnet dependencies. Some tests spawn local Hive nodes using `test-tools`.

## Architecture

### Configuration

**Global settings** can be configured via:

1. **Settings files** (in order of precedence):

    - `~/.clive/settings.toml` (user settings, higher priority)
    - `{project_root}/settings.toml` (project defaults)

2. **Environment variables** override settings files using the format:

    ```bash
    CLIVE_{GROUP}__{KEY}=value
    ```

    Example: `CLIVE_NODE__CHAIN_ID=abc123` overrides `[NODE] CHAIN_ID` in settings.toml

3. **Special environment variable**: `CLIVE_DATA_PATH` controls the Clive data directory (default: `~/.clive`). This
   also determines where user settings are loaded from (`$CLIVE_DATA_PATH/settings.toml`).

**Per-profile settings** are stored separately for each profile and configured via `clive configure`:

-   Tracked accounts (working account + watched accounts)
-   Known accounts (and enable/disable feature)
-   Key aliases
-   Node address
-   Chain ID

See `clive configure --help` for all available options.

### Core Architecture Pattern: Command Pattern

Clive uses a **Command Pattern** for all operations that interact with the blockchain or beekeeper:

-   **Commands location**: `clive/__private/core/commands/`
-   **Base classes**: All commands inherit from `Command` (in `abc/command.py`)
-   **Execution**: Commands are async and executed via `await command.execute()`
-   **Command hierarchy**:
    -   `Command` - Base class with `_execute()` method
    -   `CommandWithResult` - Commands that return a value
    -   `CommandRestricted` - Base for commands with execution preconditions
    -   `CommandInUnlocked` - Commands requiring unlocked user wallet
    -   `CommandEncryption` - Commands requiring both unlocked user wallet and encryption wallet
    -   `CommandPasswordSecured` - Commands requiring a password
    -   `CommandDataRetrieval` - Commands that fetch data from the node
    -   `CommandCachedDataRetrieval` - Data retrieval with caching support

### World Object - Application Container

`World` (`clive/__private/core/world.py`) is the top-level container and single source of truth:

-   `world.profile` - Current user profile (settings, accounts, keys)
-   `world.node` - Hive node connection for API calls
-   `world.commands` - Access to all command instances
-   `world.beekeeper_manager` - Manages beekeeper (key storage) lifecycle
-   `world.app_state` - Application state (locked/unlocked, etc.)

**Important**: Direct `world.node` API calls should be avoided in CLI/TUI. Use `world.commands` instead, which handles
errors properly.

### Profile System

Profiles (`clive/__private/core/profile.py`) store user configuration:

-   **Working account**: The currently active Hive account
-   **Watched accounts**: Accounts being monitored
-   **Known accounts**: Accounts approved for transactions. CLI requires explicit addition before broadcasting
    operations (configurable via `enable`/`disable`). TUI automatically adds accounts when operations are added to cart
    (also configurable). Managed via `clive configure known-account`
-   **Key aliases**: Named public keys
-   **Transaction**: Pending transaction operations
-   **Node address**: Hive node endpoint
-   **Chain ID**: Blockchain identifier (like a mainnet/mirrornet/testnet)

Profiles are persisted to disk via `PersistentStorageService` with encryption support.

**Note**: Tracked accounts is a combination of working account and watched accounts.

### Dual Interface Architecture

**CLI Mode** (`clive/__private/cli/`):

-   Built with **Typer** for command-line interface
-   Main command groups: `configure`, `show`, `process`, `beekeeper`, `generate`, `unlock`, `lock`
-   For complete CLI command structure, see `docs/cli_commands_structure.md`
-   CLI implementation in `clive/__private/cli/`
-   Most of the commands —especially those that interact with profile— require Beekeeper (via the
    `CLIVE_BEEKEEPER__REMOTE_ADDRESS` and `CLIVE_BEEKEEPER__SESSION_TOKEN` environment variables) for profile encryption
    and decryption.
-   Commands `clive beekeeper spawn` and `clive beekeeper create-session` can be used for preparing the CLI environment.

**TUI Mode** (`clive/__private/ui/`):

-   Built with **Textual** (Python TUI framework)
-   Main app: `clive/__private/ui/app.py` (Clive class)
-   Screens in `clive/__private/ui/screens/`
-   Widgets in `clive/__private/ui/widgets/`
-   Styling: TCSS (a Textual variation of CSS) files stored as .scss due to better syntax highlighting
-   TUI can be used in environment where Beekeeper is already running (`CLIVE_BEEKEEPER__REMOTE_ADDRESS` and
    `CLIVE_BEEKEEPER__SESSION_TOKEN` env vars are set), but without them, beekeeper will be automatically spawned and
    session will be created when starting TUI.

### Beekeeper Integration

Clive uses **beekeepy** (async Python wrapper) to communicate with Hive's beekeeper for key management:

-   **BeekeeperManager**: `clive/__private/core/beekeeper_manager.py`
-   Beekeeper stores keys in encrypted wallets
-   Beekeeper wallets are stored in the `~/.clive/beekeeper` directory (or `$CLIVE_DATA_PATH/beekeeper` if customized)
-   Two wallet types: user wallets (for signing) and encryption wallets (for encrypting profile data)
-   Wallets must be unlocked before use
-   Beekeeper address and session token can be pointed with respective setting in the `settings.toml` file or via env
    var that would have higher precedence

### Blockchain Communication

-   **Node interaction**: `clive/__private/core/node/node.py`
-   **API wrapper**: `clive/__private/core/node/async_hived/` - async wrapper around Hive node APIs
-   **Wax integration**: Uses `hiveio-wax` for transaction building and signing
-   **Operation models**: `clive/__private/models/schemas.py` - Pydantic models for Hive operations

### Storage and Migrations

-   **Storage service**: `clive/__private/storage/service/service.py`
-   **Converters**: Runtime models ↔ Storage models
-   **Migrations**: `clive/__private/storage/migrations/` - versioned profile schema migrations
-   Profiles are stored as encrypted files (location can controlled by `CLIVE_DATA_PATH` environment variable, default:
    `~/.clive/data/`)

## Test Organization

Tests are organized into two main categories:

-   **`tests/unit/`** - Unit tests for individual components (keys, storage, commands, etc.)
-   **`tests/functional/`** - Functional tests split by interface:
    -   `functional/cli/` - CLI command tests
    -   `functional/tui/` - TUI interaction tests

**Test fixtures and patterns**:

Common fixtures (`tests/conftest.py`):

-   `world` - Async World instance
-   `beekeeper` - Async beekeeper instance from beekeepy (spawned automatically)
-   `node` - Local testnet node (spawned automatically via test-tools)

CLI test patterns (`tests/functional/cli/`):

-   Uses `CLITester` from `clive-local-tools` package
-   `cli_tester` fixture - Provides typed CLI testing interface with command invocation and output checking

TUI test patterns (`tests/functional/tui/`):

-   Uses `ClivePilot` (Textual's async test driver)
-   `prepared_env` fixture - Returns `(node, wallet, pilot)` tuple with TUI ready on Unlock screen
-   `prepared_tui_on_dashboard` fixture - TUI already authenticated and on Dashboard screen
-   `node_with_wallet` fixture - Test node with initialized wallet
-   Tests interact with TUI via pilot (e.g., `pilot.click()`, `pilot.press()`)

## Development Guidelines

### Code Style

-   **Strict mypy**: Type hints are required and strictly enforced
-   **Ruff**: Comprehensive linting with "ALL" rules (see `pyproject.toml` for ignored rules)
-   **Future imports**: All files must have `from __future__ import annotations` (enforced by ruff)
-   **Docstrings**: Google style, checked by pydoclint (no redundant type hints in docstrings)
-   **Line length**: See `line-length` in `pyproject.toml` (currently 120 characters)

### Important Conventions

1. **Private modules**: Implementation details are in `__private/` directories
2. **No direct initialization**: Some classes (like `Profile`) use factory methods instead of `__init__`
3. **Command pattern**: Always use commands for blockchain operations, not direct API calls
4. **Async context managers**: Many resources (World, Node) require async context manager usage
5. **Settings**: Use `safe_settings` from `clive/__private/settings` for reading configuration

### When Working With Tests

-   Pytest tests use `test-tools` from the Hive submodule for spawning local nodes
-   For manual tests, local testnet node can be started manually via `testnet_node.py`
-   Both `testnet_node.py` and `test-tools` based tests require executables from the `hive` submodule pointed by the
    `HIVE_BUILD_ROOT_PATH` environment variable
-   Beekeeper is spawned automatically by test fixtures when needed
-   Tests modify settings to use test directories, not user's actual Clive data
-   The `clive-local-tools` package provides test helpers and checkers

### Useful Commands

#### GitLab CLI (glab)

```bash
# Find MR for a branch
glab mr list --source-branch=<branch>

# Add comment to MR
glab mr note <MR_NUMBER> --message "..."

# Get pipeline job details
glab api "projects/hive%2Fclive/pipelines/<ID>/jobs"

# Get job logs
glab api "projects/hive%2Fclive/jobs/<ID>/trace"
```

### CI Environment

Tests run in CI with:

-   Parallel processes configurable via `PYTEST_NUMBER_OF_PROCESSES` (see `.gitlab-ci.yml`, default: 16)
-   Timeout configurable via `PYTEST_TIMEOUT_MINUTES` (typically 10 minutes for most test suites)
-   Separate jobs for unit tests, CLI tests, and TUI tests
-   Tests run against installed wheel (not editable install)

## Code Review Guidelines

When reviewing MRs for the Clive project:

### Publishing Reviews on GitLab

-   Each identified problem should have its own thread on the relevant code line
-   After creating all threads, add a summary comment with references to all threads
-   Use full URLs to reference threads in the summary (see `gitlab-discussions` skill for formatting rules)

### Naming Conventions

-   Prefer `self._name` (single underscore) over `self.__name` (double underscore) for private attributes
-   Exceptions should inherit from `CliveError`

### General Coding Practices

-   Don't forget to call `super().__init__()` in subclass `__init__` when parent class has its own `__init__`
-   Don't create empty `__init__` methods that add nothing (e.g., just `pass` or only `super().__init__()`)
-   All public classes, functions, and methods should have docstrings
-   Be careful when accessing list elements (e.g., `list[0]`):
    -   If certain the element exists, use assertion for clear error message
    -   If uncertain, use proper error handling with custom exceptions
-   Remove unused code/methods - don't leave dead code
-   Prefer one clear usage pattern in docstrings; keep examples focused
-   Avoid empty methods with just `pass` - remove them or add docstring (then `pass` is not needed)
-   Avoid `assert isinstance()` for type validation (can be disabled with `-O` flag) - use proper type checking
-   Classes with `abstractmethod` should inherit from `ABC`
-   Accept specific types in function signatures, not `Any` or `object` unless required
-   For file path parameters, accept `str | Path` for flexibility
-   Make boolean parameters keyword-only to avoid cryptic calls (avoids ruff FBT001)
-   Place `TYPE_CHECKING` imports after regular imports

### Class Structure

Keep method ordering logical and consistent:

-   Group related methods together
-   Public API before private implementation
-   Properties near the top, after `__init__`

Suggested order:

1. Magic methods (`__init__`, `__str__`, etc.)
2. Public properties
3. Private properties
4. Public methods
5. Private methods

Factory methods and static/class methods may be placed higher depending on context (e.g., before regular instance
methods).

### Test Conventions

-   Use standalone test functions, not test classes (helper classes are fine)
-   Follow AAA format (ARRANGE-ACT-ASSERT) with comments
-   Import from public API instead of `__private` when possible
-   Fixtures should be in `conftest.py`
-   Split tests per command/feature into separate files

### Code Quality

-   Avoid mypy suppressions (`# type: ignore`) and ruff suppressions (`# noqa:`) - fix issues instead
-   If suppression is necessary, it should be a last resort with justification
-   Pydoclint errors should be fixed; adding to baseline only as a last resort with justification
