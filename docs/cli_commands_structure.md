---
hide:
    - toc
    - navigation
---

## Commands Structure

The commands have been designed in a sub-command structure.

In any time it's possible to use the `-h`/`--help` flag to get help about the current command, related sub-commands
or/and options.

The main command is `clive` and it has sub-commands like `clive configure` or `clive show`. The sub-commands can have
sub-commands as well.

In the tree below, you can see all the commands and sub-commands that `clive` has:

```
clive
├── configure
│ ├── chain-id
│ │ ├── set
│ │ └── unset
│ ├── key
│ │ ├── add
│ │ └── remove
│ ├── known-account
│ │ ├── add
│ │ ├── disable
│ │ ├── enable
│ │ └── remove
│ ├── node
│ │ └── set
│ ├── profile
│ │ ├── create
│ │ └── delete
│ ├── tracked-account
│ │ ├── add
│ │ └── remove
│ └── working-account
│ └── switch
├── show
│ ├── active-authority
│ ├── account
│ ├── accounts
│ ├── balances
│ ├── chain
│ ├── hive-power
│ ├── keys
│ ├── memo-key
│ ├── node
│ ├── new-account-token
│ ├── owner-authority
│ ├── pending
│ │ ├── account-recovery
│ │ ├── change-recovery-account
│ │ ├── convert
│ │ ├── decline-voting-rights
│ │ ├── power-down
│ │ ├── power-ups
│ │ ├── removed-delegations
│ │ └── withdrawals
│ ├── posting-authority
│ ├── profile
│ ├── profiles
│ ├── proposals
│ ├── proposal
│ ├── proxy
│ ├── rc
│ ├── transaction-status
│ ├── transfer-schedule
│ ├── witnesses
│ ├── witness
│ └── orders
├── process
│ ├── account-creation
│ ├── claim
│ │ ├── new-account-token
│ │ └── rewards
│ ├── convert
│ ├── custom-json
│ ├── delegations
│ │ ├── remove
│ │ └── set
│ ├── order
│ │ ├── cancel
│ │ └── create
│ ├── power-down
│ │ ├── cancel
│ │ ├── restart
│ │ └── start
│ ├── rc-delegations
│ │ ├── remove
│ │ └── set
│ ├── power-up
│ ├── proxy
│ │ ├── clear
│ │ └── set
│ ├── account-recovery
│ │ ├── change
│ │ ├── recover
│ │ └── request
│ ├── savings
│ │ ├── deposit
│ │ ├── withdrawal
│ │ └── withdrawal-cancel
│ ├── transaction
│ ├── transfer
│ ├── transfer-schedule
│ │ ├── create
│ │ ├── modify
│ │ └── remove
│ ├── update-active-authority
│ │ ├── add-account
│ │ ├── add-key
│ │ ├── modify-account
│ │ ├── modify-key
│ │ ├── remove-account
│ │ └── remove-key
│ ├── update-memo-key
│ ├── update-owner-authority
│ │ ├── add-account
│ │ ├── add-key
│ │ ├── modify-account
│ │ ├── modify-key
│ │ ├── remove-account
│ │ └── remove-key
│ ├── update-posting-authority
│ │ ├── add-account
│ │ ├── add-key
│ │ ├── modify-account
│ │ ├── modify-key
│ │ ├── remove-account
│ │ └── remove-key
│ ├── update-witness
│ ├── vote-proposal
│ │ ├── add
│ │ └── remove
│ ├── vote-witness
│ │ ├── add
│ │ └── remove
│ ├── voting-rights
│ │ ├── cancel-decline
│ │ └── decline
│ └── withdraw-routes
│ ├── remove
│ └── set
├── generate
│ ├── key-from-seed
│ ├── public-key
│ ├── random-key
│ └── secret-phrase
├── crypto
│ └── decrypt
├── beekeeper
│ ├── close
│ ├── create-session
│ ├── info
│ └── spawn
├── lock
└── unlock
```
