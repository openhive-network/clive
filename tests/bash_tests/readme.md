beekeeper binary is needed to run tests scripts, it should be pointed by env variable CLIVE_BEEKEEPER__PATH
testnet hived binary is also needed to run tests, expected in env variable HIVED_PATH

other variables:

CLIVE_DATA_PATH - optional, in tests default is $(pwd)/generated_clive_data/$BATS_TEST_NAME/.clive
HIVED_DATA_PATH - optional, in tests default is $(pwd)/generated_clive_data/$BATS_TEST_NAME/.hived
