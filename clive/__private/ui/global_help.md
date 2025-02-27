# Clive

**Clive** is an interactive command-line wallet for the Hive blockchain. The name "Clive" is a portmanteau of the words "cli" (command-line interface) and "hive". Clive's interface was inspired by midnight commander. Clive is written in python and uses the Wax library to communicate with Hive network nodes.

## Global bindings:

| Binding  | Action                    |
|:--------:|---------------------------|
|   `F1`   | Show help                 |
|   `F7`   | Go to transaction summary |
|   `F8`   | Go to dashboard           |
|   `F9`   | Go to config              |
| `Ctrl+Q` | Quit                      |
| `Ctrl+S` | Screenshot                |
|   `C`    | Clear notifications       |


## How to select, copy and paste text inside TUI app like Clive?

To select some text hold `Shift` while you click and drag.

Copy/Paste action shortcuts depend on the environment (mainly terminal) in which Clive was launched. You may check:
* on `Windows`: `Ctrl+C` and `Ctrl+V` or `select text` and press `Right Mouse Button` to paste.
* on `Linux`: `Ctrl+Shift+C` and `Ctrl+Shift+V` or `select text` and press `Middle Mouse Button` to paste.

If none of the above works, you may also try `Ctrl+Insert` and `Shift+Insert`. \
Otherwise, you should check this for your environment/terminal as it is often quite specific or configurable and we're unable to indicate a universal solution.
