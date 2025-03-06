import json
from typing import AsyncGenerator, Generator
import aiohttp
import asyncio
import requests
import websockets


import logging
logger = logging.getLogger(__name__)

class Stream:
    def __init__(
        self,
        backend: str,
        URI: str,
        max_new_tokens: str,
        model: str,
        streaming: bool,
    ) -> None:
        """
        Initializes a new instance of the Streamer class.

        :param backend: The backend to use for generating text.
        :param URI: The URI of the backend service.
        """
        self.backend = backend
        self.URI = URI
        self.model = model
        self.max_new_tokens = max_new_tokens
        self.streaming = streaming

    async def openai(self, prompt: str) -> AsyncGenerator[str, None]:
        """
        Generates text using the OpenAI backend.

        :param prompt: The prompt to use for generating text.
        :return: An async generator that yields the generated text.
        """
        request = {
            "messages": prompt,
            "model": self.model,
            "stream": True,
            "temperature": 1,
            "max_tokens": self.max_new_tokens,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.URI, json=request) as r:
                if r.status != 200:
                    logger.warning(f"Request failed with status code: {r.status}")
                    yield f"Request failed with status code: {r.status}"
                    return

                async for chunk in r.content:
                    # Decode and clean the chunk
                    decoded_chunk = chunk.decode("utf-8").strip()

                    if not decoded_chunk:
                        continue

                    if decoded_chunk.startswith("data:"):
                        # Handle completion signal
                        if decoded_chunk == "data: [DONE]":
                            break

                        # Extract JSON content
                        json_str = decoded_chunk[len("data:") :].strip()
                        if json_str == "[DONE]":
                            break

                        try:
                            data = json.loads(json_str)
                            # Extract text from the first choice
                            choice = data["choices"][0]
                            text_content = choice.get("delta", {}).get("content", "")

                            # Yield the text content directly
                            if text_content:
                                yield text_content

                        except (json.JSONDecodeError, KeyError, IndexError) as e:
                            logger.error(f"Error processing chunk: {e}")
                            logger.error(f"Problematic chunk content: {decoded_chunk}")


    async def printer(self, prompt: str = "This is an instruction:") -> None:
        """
        Prints generated text to the console.

        :param prompt: The prompt to use for generating text.
        """
        try:
            if self.backend == "exllama":
                generator = self.exllama(prompt)
                for response in generator:
                    logger.info(response, end="", flush=True)
            elif self.backend == "ooba":
                generator = self.ooba(prompt)
                async for response in generator:
                    logger.info(response, end="", flush=True)
            elif self.backend == "aphrodite":
                generator = self.aphrodite(prompt)
                async for response in generator:
                    logger.info(response, end="", flush=True)
            elif self.backend == "sglang":
                generator = self.sglang(prompt)
                async for response in generator:
                    logger.info(response, end="", flush=True)
            elif self.backend == "openai":
                generator = self.openai(prompt)
                async for response in generator:
                    logger.info(response, end="", flush=True)

        except Exception as e:
            # Handle any exceptions that might occur
            logger.error(f"An error occurred: {e}")
