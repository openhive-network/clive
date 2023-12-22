## Commands Structure

The commands have been designed in a sub-command structure.

:grey_question: In any time it's possible to use the `-h`/`--help` flag to get help about the current command,
related sub-commands or/and options.

The main command is `clive` and it has sub-commands like `clive configure` or `clive show`.
The sub-commands can have sub-commands as well.

In the diagram below, all commands that can be run are enclosed in rectangles, while subcommands that require an
additional command are contained in rectangles with rounded corners. (i.e. only the top-down leafs are runnable
commands, the rest are sub-commands)

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
        Process --> ProcessTransaction[transaction]

        Process --> ProcessSavings(savings)
        ProcessSavings --> ProcessSavingsDeposit[deposit]
        ProcessSavings --> ProcessSavingsWithdrawal[withdrawal]
        ProcessSavings --> ProcessSavingsWithdrawalCancel[withdrawal-cancel]
        Process --> ProcessProxy[proxy]
        ProcessProxy --> ProcessProxySet[set]
        ProcessProxy --> ProcessProxyClear[clear]

        Process -->|"Not implemented yet"|ProcessPowerUp[power-up]
        Process -->|"Not implemented yet"|ProcessPowerDown[power-down]
        Process -->|"Not implemented yet"|ProcessUpdateAccount[update-account]
        Process -->|"Not implemented yet"|ProcessChangeAuthority[change-authority]
        Process -->|"Not implemented yet"|ProcessClaimToken[claim-token]

        Process --> ProcessVoteWitness(vote-witness)
        ProcessVoteWitness --> ProcessVoteWitnessAdd[add]
        ProcessVoteWitness --> ProcessVoteWitnessRemove[remove]

        Process --> ProcessVoteProposal(vote-proposal)
        ProcessVoteProposal --> ProcessVoteProposalAdd[add]
        ProcessVoteProposal --> ProcessVoteProposalRemove[remove]
    end

    subgraph Presentation[Commands related to the presentation of the data]
        Show(show) --> ShowProfiles[profiles]

        Show --> ShowProfile[profile]

        Show --> ShowNode[node]

        Show --> ShowAccounts[accounts]

        Show --> ShowKeys[keys]

        Show --> ShowBalances[balances]

        Show --> ShowTransactionStatus[transaction-status]

        Show --> ShowProxy[proxy]

        Show --> ShowWitnesses[witnesses]
        ShowWitnesses ~~~|"witnesses:<br>- show witnesses the account votes for<br>- possible to list also proxy votes"| ShowWitnesses

        Show --> ShowWitness[witness]
        ShowWitness ~~~|"witness:<br>- show details of chosen witnesses"| ShowWitness

        Show --> ShowProposals[proposals]

        Show --> ShowPending(pending)
        ShowPending --> ShowPendingTransferFromSavings[withdrawals]
        ShowPending -->|"Not implemented yet"| ShowPendingPowerUps[power-ups]
        ShowPending -->|"Not implemented yet"| ShowPendingPowerDowns[power-downs]
        ShowPending -->|"Not implemented yet"| ShowPendingRecurrentTransfers[transfers]
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
        ConfigureKey --> RemoveKey[remove]

        Configure --> ConfigureNode(node)
        ConfigureNode --> SetNode[set]
    end
```
