## Commands Structure

:grey_question: In any time it's possible to use the `-h`/`--help` flag to get help about the current command related
sub-commands
or/and options.

The commands have been designed in a sub-command structure.

The main command is `clive` and it has sub-commands like `clive accounts` or `clive profile`.
The sub-commands can have sub-commands as well. For example, `clive accounts` has sub-commands
like `clive accounts list` or `clive accounts watched`.

In the diagram below, all commands that can be run are enclosed in rectangles, while subcommands that require an
additional command are contained in rectangles with rounded corners.

```mermaid
flowchart LR
    Clive[clive] --> Configuration
    Clive --> Presentation

    subgraph Presentation[Commands related to the presentation of the data]
        Show(show) --> ShowProfiles[profiles]

        Show --> ShowNode[node]

        Show --> ShowAccounts[accounts]

        Show --> ShowKeys[keys]

        Show --> ShowBalances[balances]

        Show -->|"Not implemented yet"| ShowWitnesses[witnesses]
        ShowWitnesses ~~~|"witnesses:<br>- show witnesses the account votes for<br>- possible to list also proxy votes"| ShowWitnesses

        Show -->|"Not implemented yet"| ShowProposals[proposals]

        Show -->|"Not implemented yet"| ShowPending(pending)
        ShowPending --> ShowPendingTransferFromSavings[withdrawals]
        ShowPending --> ShowPendingPowerUps[power-ups]
        ShowPending --> ShowPendingPowerDowns[power-downs]
        ShowPending --> ShowPendingRecurrentTransfers[transfers]
    end

    subgraph Configuration[Configuration related commands]
        Configure(configure) --> ConfigureProfile(profile)
        ConfigureProfile --> CreateProfile[add]
        ConfigureProfile --> DeleteProfile[remove]
        ConfigureProfile --> SetDefaultProfile[set-default]

        Configure --> ConfigureWatchedAccount(watched-account)
        ConfigureWatchedAccount --> AddWatchedAccount[add]
        ConfigureWatchedAccount --> RemoveWatchedAccount[remove]

        Configure --> ConfigureWorkingAccount(working-account)
        ConfigureWorkingAccount --> AddWorkingAccount[add]
        ConfigureWorkingAccount --> RemoveWorkingAccount[remove]

        Configure --> ConfigureKey(key)
        ConfigureKey --> AddKey[add]
        ConfigureKey -->|"Not implemented yet"| RemoveKey[remove]

        Configure --> ConfigureNode(node)
        ConfigureNode --> SetNode[set]
    end

    Clive --> Beekeeper(beekeeper)
    Beekeeper --> BeekeeperClose[close]
    Beekeeper --> BeekeeperInfo[info]
    Beekeeper --> BeekeeperSpawn[spawn]
    Beekeeper --> BeekeeperSync[sync]
    Clive --> Profile(profile)
    Profile --> ProfileShow[show]
    Clive --> Transfer(transfer)
```
