#!/bin/bash

INITIAL_MODEL=$1 # gpt2 or path to pretrained
OUTPUT_MODEL="enclave"
#WANDB_API_KEY=""
#python3 ./concat.py ./data/input.txt

docker run --runtime=nvidia \
-e WANDB_API_KEY="$WANDB_API_KEY" \
-v "$(pwd)/models":/app/models -v "$(pwd)/data":/app/data \
--entrypoint "python3" \
-it blackstar-worker \
./run_language_modeling.py \
--cache_dir "models/pretrained" \
--output_dir "models/trained/$OUTPUT_MODEL" \
--model_type "gpt2" \
--model_name_or_path "$INITIAL_MODEL" \
--do_train --train_data_file "data/enclave.txt" \
--per_device_train_batch_size=2 \
--num_train_epochs=10 \
--overwrite_output_dir