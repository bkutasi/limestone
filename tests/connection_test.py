import json
import socket
import time
import websockets
from unittest import IsolatedAsyncioTestCase
import unittest

from bot.streamer import Stream


class ConnectionTest(IsolatedAsyncioTestCase):
    """
    A class for testing WebSocket and normal socket connections.
    """

    async def test_websocket_connection(self):
        URI = "ws://localhost:5005/api/v1/stream"

        try:
            async with websockets.connect(URI):
                # If this line is reached, the connection was successful
                print(f"WebSocket test: PASS. WebSocket connection to {URI} is active")
        except ConnectionRefusedError:
            self.fail(
                f"WebSocket test: FAIL. WebSocket connection to {URI} was refused"
            )

    async def test_ooba(self):
        backend = "ooba"
        URI = "ws://localhost:5005/api/v1/stream"
        max_new_tokens = "1"

        stream = Stream(backend, URI, max_new_tokens)

        assert isinstance(stream, Stream)


class OtherTests:
    @staticmethod
    async def check_websocket_connection(uri):
        """
        Check if a WebSocket connection to the specified URI is still active.

        This method sends some data to the server and waits for a response.
        If a response is received, it indicates that the connection is still active.

        :param uri: The URI of the WebSocket server to connect to.
        """
        async with websockets.connect(uri) as websocket:
            start_time = time.time()
            # Send some data to the server
            await websocket.send(json.dumps({"prompt": "The rivers will flow and"}))

            # Wait for a response from the server
            response = await websocket.recv()
            # Print the response

            print(f"WebSocket test: PASS. WebSocket connection to {uri} is active")
            end_time = time.time()
            print(f"Coroutine took {end_time - start_time} seconds to run")
            # Assert that a response was received from the server
            assert response, f"No response received from WebSocket connection to {uri}"

    @staticmethod
    def check_socket_connection(host, port, path):
        """
        Check if a normal socket connection to the specified host and port is still active.

        This method creates a new socket and connects to the server at the specified
        host and port. It sends an HTTP GET request for the specified path and checks
        if it receives a response. If a response is received, it indicates that the
        connection is still active.

        :param host: The hostname of the server to connect to.
        :param port: The port number of the server to connect to.
        :param path: The path of the resource to request from the server.
        """
        try:
            # Create a new socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect to the server
            sock.connect((host, port))

            # Send an HTTP GET request for the specified path
            request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\n\r\n"
            sock.sendall(request.encode())

            # Receive data from the server
            data = sock.recv(1024)

            print(f"Socket test: PASS. Socket connection to {host}:{port} is active")
        except Exception as e:
            print(f"Error checking socket connection to {host}:{port}: {e}")


unittest.main()
"""# Check the WebSocket connection
websocket_uri = "ws://localhost:5005/api/v1/stream"
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

start_time = time.time()
result = loop.run_until_complete(
    ConnectionTest.check_websocket_connection(websocket_uri)
)

end_time = time.time()

print(f"Event loop took {end_time - start_time} seconds to run")
"""
