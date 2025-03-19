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
        self.log(f"[handle_connection] Client connected: {websocket.remote_address}")
        self.connected_clients.add(websocket)

        send_task = asyncio.create_task(self.send_messages(websocket))
        receive_task = asyncio.create_task(self.receive_messages(websocket))

        try:
            await asyncio.gather(send_task, receive_task)
            
        except websockets.exceptions.ConnectionClosed:
            self.log(f"[handle_connection] Client disconnected: {websocket.remote_address}")
            
        finally:
            self.connected_clients.remove(websocket)
            send_task.cancel()
            receive_task.cancel()
            self.log(f"[handle_connection] Connection closed: {websocket.remote_address}")


    async def receive_messages(self, websocket):
        """Receives messages from the client and places them in the incoming queue."""
        try:
            async for message in websocket:
                event = json.loads(message)
                self.log(f"[receive_messages] Received: {event}")
                await self.incoming_events_queue.put(event)
                self.log("[receive_messages] Event added to received events queue.")

            self.log("[receive_messages] Message reception loop ended. Connection likely closed by client.")
                    
        except websockets.exceptions.ConnectionClosed as e:
            self.log(f"[receive_messages] Client disconnected unexpectedly: {e}")

        except Exception as e:
            self.log(f"[receive_messages] Unexpected error in receive_messages: {e}")

    async def send_messages(self, websocket):
        """Continuously sends messages from the outgoing queue to the client."""
        try:
            while not self.shutdown_event.is_set():
                if not self.outgoing_events_queue.empty():
                    message = await self.outgoing_events_queue.get()
                    
                    if message is None:
                        self.log("[send_messages] Received stop signal. Closing send_messages loop.")
                        break
                    
                    self.log(f"[send_messages] Detected message in the output queue: {message}")
                    
                    try:
                        await websocket.send(json.dumps(message))  # Ensure JSON format
                        self.log(f"[send_messages] Data Sent: {message}")
                    
                    except websockets.exceptions.ConnectionClosed:
                        self.log("[send_messages] WebSocket connection closed while sending message.")
                        break
                
                await asyncio.sleep(0.1)  # Sleep briefly to prevent high CPU usage

            self.log("[send_messages] Message transmission loop ended.")
                    
        except asyncio.CancelledError:
            pass  # Task was cancelled (client disconnected)

    async def start_server(self):
        """Creates and starts the WebSocket server."""
        self.server = await websockets.serve(self.handle_connection, self.host, self.port)
        self.log(f"Server started on ws://{self.host}:{self.port}")

        await self.server.wait_closed()
        self.log("Server stopped.")
        

    def run(self):
        """Runs the WebSocket server in an event loop."""
        
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        server_task = loop.create_task(self.start_server())

        while not self.shutdown_event.is_set():
            loop.run_forever()

        server_task.cancel()  # Cancel the server task before exiting


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
