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
    Clive --> Processing
    Clive --> BeekeeperRelated

    subgraph BeekeeperRelated[Beekeeper related commands]
        Beekeeper(beekeeper) --> BeekeeperSpawn[spawn]
        Beekeeper --> BeekeeperClose[close]
        Beekeeper --> BeekeeperInfo[info]
    end

   subgraph Processing[Commands related to performing certain actions]
        Process(process) --> ProcessTransfer[transfer]
        Process -->|"Not implemented yet"|ProcessDeposit[deposit]
        Process -->|"Not implemented yet"|ProcessWithdrawal[withdrawal]
        Process -->|"Not implemented yet"|ProcessCancelWithdrawal[cancel-withdrawal]
        Process -->|"Not implemented yet"|ProcessPowerUp[power-up]
        Process -->|"Not implemented yet"|ProcessPowerDown[power-down]
        Process -->|"Not implemented yet"|ProcessUpdateAccount[update-account]
        Process -->|"Not implemented yet"|ProcessChangeAuthority[change-authority]
        Process -->|"Not implemented yet"|ProcessSetProxy[set-proxy]
        Process -->|"Not implemented yet"|ProcessClaimToken[claim-token]

        Process -->|"Not implemented yet"|ProcessVoteWitness(vote-witness)
        ProcessVoteWitness --> ProcessVoteWitnessAdd[add]
        ProcessVoteWitness --> ProcessVoteWitnessRemove[remove]

        Process -->|"Not implemented yet"|ProcessVoteProposal(vote-proposal)
        ProcessVoteProposal --> ProcessVoteProposalAdd[add]
        ProcessVoteProposal --> ProcessVoteProposalRemove[remove]

        Process -->|"Not implemented yet"|ProcessTransaction[transaction]
    end

    subgraph Presentation[Commands related to the presentation of the data]
        Show(show) --> ShowProfiles[profiles]

        Show --> ShowProfile[profile]

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
```
