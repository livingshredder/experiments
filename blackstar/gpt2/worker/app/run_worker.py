import time
import base64
import json
import re
import logging
import traceback

import numpy as np
import torch
import pika
import pika.channel

from typing import List
from pathlib import Path
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# DECODING THESE REDACTIONS IS PROHIBITED
# UNDER INTERNAL SECURITY DESCRIPTOR 0/1.7/6.3/1.0/2
BLACKSTAR_REDACTIONS = []  # not used anymore

logging.basicConfig(level=logging.DEBUG)


def set_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def blackstar_clean_text(text: str):
    for i, redaction in enumerate(BLACKSTAR_REDACTIONS):
        decoded = base64.b64decode(redaction).decode("utf-8").strip()
        text = re.sub(
            re.escape(decoded),
            f"[BLACKSTAR REDACTED/BSR{i}/TOPSECRET]",
            text,
            flags=re.IGNORECASE,
        )
    return text


class BlackstarWorker:
    def __init__(self, models: List[str], queue_name: str):
        self._queue_name = queue_name

        self._models = {}
        for name in models:
            logging.info(f"Loading model {name}")
            path = Path.cwd().joinpath(f"models/trained/{name}")

            tokenizer = GPT2Tokenizer.from_pretrained(path)
            model = GPT2LMHeadModel.from_pretrained(path)
            model.to("cuda")
            
            self._models[name] = {
                "tokenizer": tokenizer,
                "model": model,
            }

    def _send_response(self, original_id, time_ms, body):
        pass

    def _process_message(self, args: dict) -> str:
        model_obj = self._models[args["model"]]
        model: GPT2LMHeadModel = model_obj["model"]
        tokenizer: GPT2Tokenizer = model_obj["tokenizer"]

        prefix = args["prefix"]
        encoded_prompt = tokenizer.encode(
            "<|startoftext|>\n" + prefix, add_special_tokens=True, return_tensors="pt"
        )
        encoded_prompt = encoded_prompt.to("cuda")

        stop_token = "<|endoftext|>"

        if encoded_prompt.size()[-1] == 0:
            input_ids = None
        else:
            input_ids = encoded_prompt

        args["input_ids"] = input_ids
        args["do_sample"] = True
        args["num_return_sequences"] = 1

        output_sequences = model.generate(**args)

        # Remove the batch dimension when returning multiple sequences
        if len(output_sequences.shape) > 2:
            output_sequences.squeeze_()

        generated_sequences = []

        for sequence in output_sequences:
            sequence = sequence.tolist()

            # Decode text
            text = tokenizer.decode(sequence, clean_up_tokenization_spaces=True)

            # Remove all text after the stop token
            text = text[: text.find(stop_token) if stop_token else None]

            # Add the prompt at the beginning of the sequence. Remove the excess text that was used for pre-processing
            total_sequence = text[
                len(
                    tokenizer.decode(
                        encoded_prompt[0], clean_up_tokenization_spaces=True
                    )
                ) :
            ]

            generated_sequences.append(total_sequence)

        output = "".join(generated_sequences)

        # strip redactions
        # output = blackstar_clean_text(output)

        return output

    def run(self):
        # todo: change this
        set_seed(42)

        logging.info("Worker is running")

        params = pika.ConnectionParameters("localhost")
        conn = pika.BlockingConnection(params)

        with conn:
            channel: pika.channel.Channel = conn.channel()
            channel.queue_declare(self._queue_name)

            for method_frame, properties, body in channel.consume(self._queue_name):
                logging.debug(f"processing request for correlation ID {properties.correlation_id}")

                # parse the arguments
                try:
                    payload = json.loads(body)
                except json.JSONDecodeError:
                    logging.exception("Failed to decode payload, message is invalid")
                    channel.basic_reject(method_frame.delivery_tag, False)

                start_time = time.time()

                response = {}
                try:
                    response["result"] = self._process_message(payload)
                except Exception as e:
                    traceback.print_exc()
                    response["error"] = "Error running the model. Check the logs for exception details."

                response["time"] = int(round((time.time() - start_time) * 1000))

                channel.basic_publish(
                    exchange="",
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id
                    ),
                    body=json.dumps(response)
                )
                channel.basic_ack(method_frame.delivery_tag)

                logging.debug(f"request finished for correlation ID {properties.correlation_id}")


worker = BlackstarWorker(["blackstar1", "enclave"], "bsr_gpt2_worker")
worker.run()
