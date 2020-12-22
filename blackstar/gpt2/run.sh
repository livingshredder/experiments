#!/bin/sh
docker run --runtime=nvidia \
-v "$(pwd)/models":/app/models \
-e WANDB_API_KEY="$WANDB_API_KEY" \
-e AWS_DEFAULT_REGION="$AWS_DEFAULT_REGION" -e AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" -e AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
-it blackstar-worker "$@"
