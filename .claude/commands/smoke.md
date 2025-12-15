Run the smoke test to quickly verify basic CLI functionality.

Execute this command:

```bash
pytest -n 2 tests/functional/cli/show/test_show_account.py::test_show_account tests/functional/cli/process/test_process_transfer.py::test_process_transfer
```

Report the results concisely - whether tests passed or failed, and any errors encountered.
