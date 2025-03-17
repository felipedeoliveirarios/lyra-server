import asyncio
import threading
import websockets
import json
from datetime import datetime

class WebSocketHandler:
    def __init__(self, incoming_events_queue, outgoing_events_queue, shutdown_event, host="localhost", port=443):
        """Initialize WebSocket server settings."""
        self.host = host
        self.port = port
        self.server_thread = None
        self.connected_clients = set()
        self.shutdown_event = shutdown_event
        self.incoming_events_queue = incoming_events_queue
        self.outgoing_events_queue = outgoing_events_queue


    async def handle_connection(self, websocket, path):
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


    async def receive_messages(self, websocket):
        """Receives messages from the client and places them in the incoming queue."""
        try:
            async for message in websocket:
                event = json.loads(message)
                self.log(f"Received: {event}")
                self.incoming_events_queue.put(event)
                
        except websockets.exceptions.ConnectionClosed:
            pass  # Client disconnected, exit the function

    async def send_messages(self, websocket):
        """Sends messages from the outgoing queue to the client."""
        try:
            while True:
                message = self.outgoing_events_queue.get()
                
                if websocket.open:  # Ensure the socket is still open
                    asyncio.run_coroutine_threadsafe(websocket.send(message), asyncio.get_event_loop())
                    self.log(f"Sent: {message}")
                
                self.outgoing_events_queue.task_done()
                
        except asyncio.CancelledError:
            pass  # Task was cancelled (client disconnected)


    async def start_server(self):
        """Creates and starts the WebSocket server."""
        self.server = await websockets.serve(self.handle_connection, self.host, self.port)
        self.log(f"Server started on ws://{self.host}:{self.port}")

        await self.server.wait_closed()


    def send_event(self, event):
        """Enqueues an event message to be sent to all connected clients."""
        self.outgoing_events_queue.put(event)  # Just put the event in the queue (blocking call)



    def run(self):
        """Runs the WebSocket server in an event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.start_server())
        loop.run_forever()


    def start(self):
        """Starts WebSocket server in a separate thread."""
        self.log("Starting server thread.")
        
        self.server_thread = threading.Thread(target=self.run, daemon=True)
        self.server_thread.start()


    def stop(self):
        """Stops the WebSocket server and closes all connections."""
        self.log("Stopping server.")
        
        for client in self.connected_clients.copy():
            asyncio.run_coroutine_threadsafe(client.close(), asyncio.get_event_loop())


    def join(self):
        """Waits for the WebSocket server thread to finish."""
        if self.server_thread:
            self.server_thread.join()


    def log(self, msg):
        log_msg = f'{datetime.now()} [{self.__class__.__name__}] {msg}'
        print(log_msg)
