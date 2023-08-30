### What this MR does?

Ex.: This MR fixes bug from issue #xx; This MR adds feature `foo`; This MR obsoletes `boo`

---
### Basic checks

 - [ ] Both for testnet and mainnet version
    - [ ] Check is onboarding works
    - [ ] Activate and deactivate profile
    - [ ] Create transfer operation and add it to cart
    - [ ] Remove operation from cart
    - [ ] Verify is Dashboard refreshing in intervals (~3s)
    - [ ] Verify is Dashboard provides valid data
    - [ ] Add new authority and remove it

 - [ ] Just for testnet
    - [ ] Fast broadcast Transfer operation
    - [ ] Broadcast Transfer operation from cart
    - [ ] Save Transaction to file
