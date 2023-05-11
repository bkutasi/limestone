import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("Websockets package not found. Make sure it's installed.") 

# This is to test the host and port of the API server.

HOST = 'localhost:5005'
URI = f'ws://{HOST}/api/v1/stream'

async def run(context):
    # Passed parameters, llama-precise
    request = {
        'prompt': context,
        'max_new_tokens': 1024,
        'do_sample': True,
        'temperature': 0.7,
        'top_p': 0.1,
        'typical_p': 1,
        'repetition_penalty': 1.18,
        'top_k': 40,
        'min_length': 0,
        'no_repeat_ngram_size': 0,
        'num_beams': 1,
        'penalty_alpha': 0,
        'length_penalty': 1,
        'early_stopping': False,
        'seed': -1,
        'add_bos_token': True,
        'truncation_length': 2048,
        'ban_eos_token': False,
        'skip_special_tokens': False,
        'stopping_strings': []
    }

    async with websockets.connect(URI) as websocket:
        streaming = True
        await websocket.send(json.dumps(request))

        yield context # Remove this if you just want to see the reply

        while streaming is True:
            incoming_data = await websocket.recv()
            incoming_data = json.loads(incoming_data)

            match incoming_data['event']:
                case 'text_stream':
                    yield incoming_data['text']
                case 'stream_end':
                    streaming = False
                    yield streaming

# This fucntion is used to print the response stream by token to the console.
async def print_response_stream(prompt):
    generator = run(prompt)
    async for response in generator:
        if response is not False:
            print(response, end='')
            sys.stdout.flush() # If we don't flush, we won't see tokens in realtime.

if __name__ == '__main__':
    prompt = """Write a readme in with Markdown style."""
    asyncio.run(print_response_stream(prompt))

