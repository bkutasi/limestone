from unittest import IsolatedAsyncioTestCase
from bot.streamer import Stream
from typing import AsyncGenerator, Generator


class StreamTest(IsolatedAsyncioTestCase):
    async def test_ooba(self):
        """Test if the Stream API connection is successful."""
        backend = "ooba"
        URI = "ws://localhost:5005/api/v1/stream"
        max_new_tokens = "1"

        try:
            stream = Stream(backend, URI, max_new_tokens)
            generator = stream.ooba("test prompt")
            assert isinstance(stream, Stream)
            assert isinstance(stream.ooba("test prompt"), AsyncGenerator)

            for response in generator:
                assert "Bad Request" not in response
        except Exception as e:
            self.fail(f"Connection to Stream API test failed with exception: {e}")

    async def test_exllama(self):
        """Test if the Stream API connection is successful."""
        backend = "exllama"
        URI = "http://localhost:5005/generate"
        max_new_tokens = "1"

        try:
            stream = Stream(backend, URI, max_new_tokens)
            generator = stream.exllama("test prompt")
            assert isinstance(stream, Stream)
            assert isinstance(generator, Generator)

            for response in generator:
                assert "Bad Request" not in response
        except Exception as e:
            self.fail(f"Connection to Stream API test failed with exception: {e}")
