#!/bin/bash

data_dir="./data"
keys_dir=./"keys"
env_file=".env"

env_blob="API_KEY_ID = ''
PRIVATE_KEY_PATH = 'keys/key.pem'
BASE_URL = 'https://api.elections.kalshi.com/trade-api/v2/'"


if [ ! -d "$data_dir" ]; then
    mkdir data
fi

if [ ! -d "$keys_dir" ]; then
    mkdir keys
fi


if [ ! -e "$env_file" ]; then
    touch .env
    echo "$env_blob" > .env
fi

python3 -m venv .venv 
source .venv/bin/activate 
pip install -r requirements.txt
