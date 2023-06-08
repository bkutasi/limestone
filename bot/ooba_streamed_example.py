import asyncio
import json
from websockets.client import connect

HOST = 'localhost:5005'
URI = f'ws://{HOST}/api/v1/stream'

async def run(context):
    # Passed parameters, llama-precise
    request = {
        'prompt': context,
    }

    async with connect(URI) as websocket:
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
            print(response, end='', flush=True)

if __name__ == '__main__':
    prompt = """Write a readme in with Markdown style. 1. :"""
    asyncio.run(print_response_stream(prompt))

