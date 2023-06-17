import json
from typing import AsyncGenerator, Generator
import requests
import websockets


class Stream:
    def __init__(
        self,
        backend: str,
        URI: str,
        max_new_tokens: str,
    ) -> None:
        """
        Initializes a new instance of the Streamer class.

        :param backend: The backend to use for generating text.
        :param URI: The URI of the backend service.
        """
        self.backend = backend
        self.URI = URI
        self.max_new_tokens = max_new_tokens

    def exllama(self, prompt: str) -> Generator[str, None, None]:
        """
        Generates text using the exllama backend.

        :param prompt: The prompt to use for generating text.
        :return: A generator that yields the generated text.
        """
        request = {"prompt": prompt, "max_new_tokens": self.max_new_tokens}
        r = requests.post(self.URI, json=request, stream=True)

        if r.status_code == 200:
            for token in r.iter_content():
                if token:
                    yield token.decode("utf-8")
        else:
            yield f"Request failed with status code: {r.status_code}"

    async def ooba(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generates text using the ooba backend.

        :param prompt: The prompt to use for generating text.
        :return: An async generator that yields the generated text.
        """
        request = {"prompt": prompt,
                   "max_new_tokens": self.max_new_tokens,
                    "repetition_penalty": 1.07,
                    "temperature": 1.53,
                    "top_a": 0.04,
                    "top_k": 33,
                    "top_p": 0.64
}

        async with websockets.connect(self.URI) as websocket:
            await websocket.send(json.dumps(request))

            while True:
                token = await websocket.recv()

                token = json.loads(token)

                event = token.get("event")
                if event == "text_stream":
                    yield token["text"]
                elif event == "stream_end":
                    yield ""
                    return

    async def printer(self, prompt: str = "This is an instruction:") -> None:
        """
        Prints generated text to the console.

        :param prompt: The prompt to use for generating text.
        """
        try:
            if self.backend == "exllama":
                generator = self.exllama(prompt)
                for response in generator:
                    print(response, end="", flush=True)
            elif self.backend == "ooba":
                generator = self.ooba(prompt)
                async for response in generator:
                    await print(response, end="", flush=True)
        except Exception as e:
            # Handle any exceptions that might occur
            print(f"An error occurred: {e}")
