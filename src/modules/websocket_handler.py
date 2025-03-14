import asyncio
import threading
import websockets
import json
from datetime import datetime

class WebSocketHandler:
    def __init__(self, event_queue, shutdown_event, host="localhost", port=443):
        """Initialize WebSocket server settings."""
        self.host = host
        self.port = port
        self.event_queue = event_queue 
        self.shutdown_event = shutdown_event
        self.server_thread = None
        self.connected_clients = set()
        self.outgoing_messages = asyncio.Queue()


    async def handle_connection(self, websocket, path):
        """Handles incoming WebSocket messages from clients."""
        self.log(f"Client connected: {websocket.remote_address}")
        self.connected_clients.add(websocket)
        
        send_task = asyncio.create_task(self.send_messages(websocket))

        try:
            async for message in websocket:
                event = json.loads(message)
                self.log(f"Received: {event}")

                # Put the event into the processing queue
                self.event_queue.put(event)

        except websockets.exceptions.ConnectionClosed:
            self.log(f"Client disconnected: {websocket.remote_address}")

        finally:
            self.connected_clients.remove(websocket)
            send_task.cancel()
    
    
    async def send_messages(self, websocket):
        """Sends messages from the outgoing queue to a connected client."""
        try:
            while True:
                message = await self.outgoing_messages.get()
                
                if websocket.open:  # Ensure the socket is still open
                    await websocket.send(message)
                    
                self.outgoing_messages.task_done()
                
        except asyncio.CancelledError:
            pass  # Task was cancelled (client disconnected)


    async def start_server(self):
        """Creates and starts the WebSocket server."""
        self.server = await websockets.serve(self.handle_connection, self.host, self.port)
        self.log(f"Server started on ws://{self.host}:{self.port}")

        await self.server.wait_closed()
    
    
    def send_event(self, event):
        """Queues an event message to be sent to all connected clients."""
        asyncio.run_coroutine_threadsafe(self.outgoing_messages.put(event), asyncio.get_event_loop())


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