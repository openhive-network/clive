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
flowchart TD
    Clive[clive] --> Configuration

    subgraph Configuration
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

    Clive[clive] --> Accounts(accounts)
    Accounts --> AccountsList[list]
    Accounts --> AccountsWatched(watched)
    Accounts --> AccountsWorking(working)
    AccountsWatched --> AccountsWatchedList[list]
    AccountsWorking --> AccountsWorkingShow[show]
    Clive --> Beekeeper(beekeeper)
    Beekeeper --> BeekeeperClose[close]
    Beekeeper --> BeekeeperInfo[info]
    Beekeeper --> BeekeeperSpawn[spawn]
    Beekeeper --> BeekeeperSync[sync]
    Clive --> List(list)
    List --> ListBalances[balances]
    List --> ListKeys[keys]
    List --> ListNode[node]
    List --> ListProfiles[profiles]
    Clive --> Profile(profile)
    Profile --> ProfileListAll[list-all]
    Profile --> ProfileShow[show]
    Clive --> Transfer(transfer)
```
