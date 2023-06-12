#!/bin/bash

poetry run python testnet_node.py &

sleep 15

poetry run clive
