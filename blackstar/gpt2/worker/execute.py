import uuid
import json
import textwrap
import argparse

import pika
import pika.channel
import gingerit.gingerit

class TaskExecutor:
    def __init__(self, queue_name: str):
        self._queue_name = queue_name

        params = pika.ConnectionParameters("localhost")
        self._conn = pika.BlockingConnection(params)

        self._channel: pika.channel.Channel = self._conn.channel()
        
        # create our temporary callback queue
        result = self._channel.queue_declare(queue="", exclusive=True)
        self._callback_queue = result.method.queue

        self._channel.basic_consume(
            queue=self._callback_queue,
            on_message_callback=self._on_response,
            auto_ack=True
        )

        self._response: dict = None
        self._corr_id: str = None
    
    def _on_response(self, ch, method, props, body):
        if self._corr_id == props.correlation_id:
            self._response = json.loads(body)
    
    def call(self, params: dict) -> dict:
        self._response = None
        self._corr_id = str(uuid.uuid4())

        self._channel.basic_publish(
            exchange="",
            routing_key=self._queue_name,
            properties=pika.BasicProperties(
                reply_to=self._callback_queue,
                correlation_id=self._corr_id
            ),
            body=json.dumps(params)
        )

        while self._response is None:
            self._conn.process_data_events()
        return self._response

parser = argparse.ArgumentParser(description="Blackstar Task Executor")
parser.add_argument("-m", "--model", required=True, help="The model to use to generate the text")
parser.add_argument("-p", "--prefix", required=True, help="The text to use as the prefix")
parser.add_argument("-l", "--max-length", type=int, default=256)
parser.add_argument("-t", "--temperature", type=float, default=1.0)
parser.add_argument("-a", "--prefix-append", action="store_true", help="Appends the prefix to the output")
parser.add_argument("-w", "--wrap-output", action="store_true", help="Text-wraps the output")
parser.add_argument("-g", "--correct-grammar", action="store_true", help="Corrects the grammar using a specified service")
parser.add_argument("--top-k", type=int, default=50)
parser.add_argument("--top-p", type=int, default=1)
parser.add_argument("--repetition_penalty", type=float, default=1.0)

args = parser.parse_args()

params = {
    "model": args.model,
    "prefix": args.prefix,
    "max_length": args.max_length,
    "temperature": args.temperature,
    "top_k": args.top_k,
    "top_p": args.top_p,
    "repetition_penalty": args.repetition_penalty,
}

with open("hack.txt", "r") as f:
    params["prefix"] = f.read()

executor = TaskExecutor("bsr_gpt2_worker")
result = executor.call(params)

if "error" in result:
    print(f"GPT2 service returned an error: {result['error']}")
    exit(1)

output: str = result["result"]
if args.prefix_append:
    output = params["prefix"] + output

output = output.strip()
if args.correct_grammar:
    parser = gingerit.gingerit.GingerIt()
    parsed = parser.parse(output)
    if len(parsed.get("corrections", [])) > 0:
        output = parsed["result"]
if args.wrap_output:
    wrapper = textwrap.TextWrapper()
    output = wrapper.fill(output)

print(output)
print(f"\nExecution completed in {result['time']}ms.")
