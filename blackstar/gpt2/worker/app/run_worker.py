import boto3
import time
import base64
import json
import re
import traceback

import numpy as np
import torch

from transformers import (
    GPT2LMHeadModel,
    GPT2Tokenizer
)

# DECODING THESE REDACTIONS IS PROHIBITED
# UNDER INTERNAL SECURITY DESCRIPTOR 0/1.7/6.3/1.0/2
BLACKSTAR_REDACTIONS = [] # not used anymore

QUEUE_TO_GPT = "https://sqs.eu-west-2.amazonaws.com/622474503675/morkobot-to-gpt"
QUEUE_FROM_GPT = "https://sqs.eu-west-2.amazonaws.com/622474503675/morkobot-from-gpt"
boto3.setup_default_session(region_name='eu-west-2')
sqs = boto3.client('sqs')

def send_response(original_id, time_ms, body):
    sqs.send_message(
        QueueUrl=QUEUE_FROM_GPT,
        MessageBody=json.dumps(body),
        MessageAttributes={
            'OriginalId': {'StringValue': original_id, 'DataType': 'String'},
            'TimeElapsed': {'StringValue': str(time_ms), 'DataType': 'Number'}
        }
    )


def blackstar_clean_text(text: str):
    for i, redaction in enumerate(BLACKSTAR_REDACTIONS):
        decoded = base64.b64decode(redaction).decode('utf-8').strip()
        text = re.sub(re.escape(decoded), f'[BLACKSTAR REDACTED/BSR{i}/TOPSECRET]', text, flags=re.IGNORECASE)
    return text


def set_seed(seed):
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def process_message(model, tokenizer, args):
    prefix = args['prefix']
    encoded_prompt = tokenizer.encode('<|startoftext|>\n' + prefix, add_special_tokens=True, return_tensors="pt")
    encoded_prompt = encoded_prompt.to('cuda')

    stop_token = '<|endoftext|>'

    if encoded_prompt.size()[-1] == 0:
        input_ids = None
    else:
        input_ids = encoded_prompt

    args['input_ids'] = input_ids
    args['do_sample'] = True
    args['num_return_sequences'] = 1

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
        total_sequence = (
            prefix + text[len(tokenizer.decode(encoded_prompt[0], clean_up_tokenization_spaces=True)) :]
        )

        generated_sequences.append(total_sequence)

    output = ''.join(generated_sequences)

    # strip redactions
    #output = blackstar_clean_text(output)

    return output


def run_worker():
    # todo: change this
    set_seed(42)

    model_class = GPT2LMHeadModel
    tokenizer_class = GPT2Tokenizer

    model_path = 'models/trained/enclave'

    tokenizer = tokenizer_class.from_pretrained(model_path)
    model = model_class.from_pretrained(model_path)
    model.to('cuda')

    args_main = {
        'max_length': 256,
        'temperature': 1.0,
        'top_k': 50,
        'top_p': 1,
        'repetition_penalty': 1.0
    }

    while True:
        response = sqs.receive_message(
            QueueUrl=QUEUE_TO_GPT,
            MaxNumberOfMessages=10,
            VisibilityTimeout=10,
            WaitTimeSeconds=2
        )

        # idle to avoid ratelimit
        if not response or not response.get('Messages'):
            time.sleep(1)
            continue
        count = len(response['Messages'])

        for message in response['Messages']:
            sqs.delete_message(
                QueueUrl=QUEUE_TO_GPT,
                ReceiptHandle=message['ReceiptHandle']
            )

            # parse the arguments
            args = {
                'prefix': message['Body']
            }
            
            start_time = time.time()

            response = {}
            try:
                response['result'] = process_message(model, tokenizer, dict(args, **args_main))
            except Exception as e:
                traceback.print_exc()
                send_response(message['MessageId'], 0, {'error': 'Error running the model.'})
                continue
                
            elapsed_ms = int(round((time.time() - start_time) * 1000))

            send_response(message['MessageId'], elapsed_ms, response)

            
        print(f'Processed {count} messages.')

run_worker()
