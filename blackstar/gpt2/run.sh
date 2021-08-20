#!/bin/sh
docker run --runtime=nvidia --network=host \
-v "$(pwd)/models":/app/models \
-e WANDB_API_KEY="$WANDB_API_KEY" \
-it blackstar-worker "$@"
