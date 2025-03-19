import threading
import asyncio
import signal
import sys

from datetime import datetime
from modules.websocket_handler import WebSocketHandler
from modules.echo_event_processor import EchoEventProcessor

class Main:
    def __init__(self):
        """Initialize the external event queue, internal event queue, shutdown 
        event, and necessary components."""
        
        self.incoming_events_queue = asyncio.Queue()
        self.outgoing_events_queue = asyncio.Queue()
        self.shutdown_event = threading.Event()

        # Initialize components
        self.websocket_server = WebSocketHandler(self.incoming_events_queue, self.outgoing_events_queue, self.shutdown_event)
        self.event_processor = EchoEventProcessor(self.incoming_events_queue, self.outgoing_events_queue, self.shutdown_event)

    def start(self):
        """Starts all components."""
        self.log("Setting up signal handlers...")

        # Register signal handlers for graceful shutdown (before starting services)
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)

        self.log("Starting services...")

        # Start WebSocket Server and Event Processor
        self.websocket_server.start()
        self.event_processor.start()

        self.log("Services running.")

    def shutdown_handler(self, signal_received, frame):
        """Handles graceful shutdown when termination signals are received."""
        self.log("Shutting down gracefully...")

        self.shutdown_event.set()  # Signal shutdown

        # Stop WebSocket server and event processor
        self.websocket_server.stop()
        self.event_processor.stop()

        self.log("Shutdown complete.")
        sys.exit(0)
        
        
    def join_threads(self):
        """Keeps main thread alive by joining all worker threads."""
        try:
            self.websocket_server.join()
            self.event_processor.worker_thread.join()

        except KeyboardInterrupt:
            self.shutdown_handler(None, None)
    
    def log(self, msg):
        log_msg = f'{datetime.now()} [{self.__class__.__name__}] {msg}'
        print(log_msg)

if __name__ == "__main__":
    app = Main()
    app.start()
    
    try:
        app.join_threads()
    except KeyboardInterrupt:
        app.shutdown_handler(None, None)