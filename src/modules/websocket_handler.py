import asyncio
import threading
import websockets
import json
from datetime import datetime

class WebSocketHandler:
    def __init__(self, incoming_events_queue: asyncio.Queue, outgoing_events_queue: asyncio.Queue, shutdown_event, host="localhost", port=5000):
        """Initialize WebSocket server settings."""
        self.host = host
        self.port = port
        self.server_thread = None
        self.connected_clients = set()
        self.shutdown_event = shutdown_event
        self.incoming_events_queue = incoming_events_queue
        self.outgoing_events_queue = outgoing_events_queue


    async def handle_connection(self, websocket):
        """Handles a new WebSocket connection."""
        self.log(f"Client connected: {websocket.remote_address}")
        self.connected_clients.add(websocket)

        send_task = asyncio.create_task(self.send_messages(websocket))
        receive_task = asyncio.create_task(self.receive_messages(websocket))

        try:
            await asyncio.gather(send_task, receive_task)
            
        except websockets.exceptions.ConnectionClosed:
            self.log(f"Client disconnected: {websocket.remote_address}")
            
        finally:
            self.connected_clients.remove(websocket)
            send_task.cancel()
            receive_task.cancel()
            self.log(f"Connection closed: {websocket.remote_address}")


    async def receive_messages(self, websocket):
        """Receives messages from the client and places them in the incoming queue."""
        try:
            async for message in websocket:
                event = json.loads(message)
                self.log(f"Received: {event}")
                await self.incoming_events_queue.put(event)
                self.log("Event added to queue.")
                
        except websockets.exceptions.ConnectionClosed:
            pass  # Client disconnected, exit the function

    async def send_messages(self, websocket):
        """Sends messages from the outgoing queue to the client."""
        try:
            while True:
                message = await self.outgoing_events_queue.get()
                
                try:
                    await websocket.send(str(message))
                    self.log(f"Sent: {message}")
                
                except websockets.exceptions.ConnectionClosed:
                    # Connection is closed, exit the loop
                    self.log(f"WebSocket connection closed while sending message.")
                    break
                
        except asyncio.CancelledError:
            pass  # Task was cancelled (client disconnected)


    async def start_server(self):
        """Creates and starts the WebSocket server."""
        self.server = await websockets.serve(self.handle_connection, self.host, self.port)
        self.log(f"Server started on ws://{self.host}:{self.port}")

        await self.server.wait_closed()
        self.log("Server stopped.")


    def send_event(self, event):
        """Enqueues an event message to be sent to all connected clients."""
        self.outgoing_events_queue.put(event)  # Just put the event in the queue (blocking call)



    def run(self):
        """Runs the WebSocket server in an event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        server_task = loop.create_task(self.start_server())

        while not self.shutdown_event.is_set():
            loop.run_until_complete(asyncio.sleep(0.1))  # Allow loop to check shutdown

        server_task.cancel()  # Cancel the server task before exiting
        loop.stop()
        loop.close()


    def start(self):
        """Starts WebSocket server in a separate thread."""
        self.log("Starting server thread...")
        
        self.server_thread = threading.Thread(target=self.run, daemon=True)
        self.server_thread.start()


    def stop(self):
        """Stops the WebSocket server and closes all connections."""
        self.log("Stopping server.")

        for client in self.connected_clients.copy():
            asyncio.run_coroutine_threadsafe(client.close(), asyncio.get_event_loop())

        if self.server:
            self.server.close()  # Stop accepting new connections
            asyncio.run_coroutine_threadsafe(self.server.wait_closed(), asyncio.get_event_loop())

        self.shutdown_event.set()  # Signal shutdown for other components

    def join(self):
        """Waits for the WebSocket server thread to finish."""
        if self.server_thread:
            self.server_thread.join()


    def log(self, msg):
        log_msg = f'{datetime.now()} [{self.__class__.__name__}] {msg}'
        print(log_msg)
