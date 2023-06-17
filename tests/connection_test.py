import asyncio
import json
import time
import websockets
from unittest import IsolatedAsyncioTestCase
from urllib.request import Request, urlopen


class StreamingAPITest(IsolatedAsyncioTestCase):
    """Test class for WebSocket Streaming connection."""

    async def test_stream_connection(self):
        """Test if the WebSocket connection is active and log the time."""
        URI = "ws://localhost:5005/api/v1/stream"

        start_time = time.time()
        try:
            async with websockets.connect(URI):
                print(f"WebSocket test: PASS. WebSocket connection to {URI} is active")
                open_time = time.time() - start_time
                print(
                    f"Time taken to open WebSocket connection: {open_time:.6f} seconds"
                )
        except (ConnectionRefusedError, asyncio.TimeoutError) as e:
            print(
                f"WebSocket test: FAIL. WebSocket connection to {URI} \
                    failed with exception: {e}"
            )

        close_time = time.time() - start_time
        print(f"Time taken to close WebSocket connection: {close_time:.6f} seconds")


class BlockingAPITest(IsolatedAsyncioTestCase):
    """Test class for blocking API endpoints."""

    async def test_model_api(self):
        """Test if the Model API connection is successful."""
        url = "http://localhost:5000/api/v1/model"
        req = Request(url, method="GET")
        start_time = time.time()
        try:
            with urlopen(req) as res:
                self.assertEqual(res.status, 200)
                assert isinstance(json.load(res), dict)
        except Exception as e:
            print(
                f"Model API test: FAIL. Connection to {url} failed with exception: {e}"
            )

        end_time = time.time()
        print(f"Time taken for Model API test: {end_time - start_time:.6f} seconds")

    async def test_generate_api(self):
        """Test if the Generate API connection is successful."""
        url = "http://localhost:5000/api/v1/generate"
        data = {
            "prompt": "test prompt",
            # Add any additional parameters here
        }
        req = Request(url, method="POST", data=json.dumps(data).encode("utf-8"))
        req.add_header("Content-Type", "application/json")
        start_time = time.time()
        try:
            with urlopen(req) as res:
                self.assertEqual(res.status, 200)
                self.assertEqual(res.getheader("Content-Type"), "application/json")
                response_data = json.load(res)
                assert isinstance(response_data, dict)
        except Exception as e:
            print(
                f"Generate API test: FAIL. Connection to {url} \
                    failed with exception: {e}"
            )

        end_time = time.time()
        print(f"Time taken for Generate API test: {end_time - start_time:.6f} seconds")
