import threading
import queue
import signal
import sys

from datetime import datetime
from modules.websocket_handler import WebSocketHandler
from modules.event_processor import EventProcessor

class Main:
    def __init__(self):
        """Initialize the event queue, shutdown event, and necessary components."""
        self.event_queue = queue.Queue()
        self.shutdown_event = threading.Event()

        # Initialize components
        self.websocket_server = WebSocketHandler(self.event_queue, self.shutdown_event)
        self.event_processor = EventProcessor(self.event_queue, self.shutdown_event)

    def start(self):
        """Starts all components."""
        self.log("Starting services...")

        # Start WebSocket Server and Event Processor
        self.websocket_server.start()
        self.event_processor.start()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)

        self.log("Services running.")

    def shutdown_handler(self, signal_received, frame):
        """Handles graceful shutdown when termination signals are received."""
        self.log("Shutting down gracefully...")

        self.shutdown_event.set()  # Signal shutdown

        # Stop WebSocket server and event processor
        self.websocket_server.stop()
        self.event_processor.stop()

        sys.exit(0)

    def join_threads(self):
        """Keeps main thread alive by joining worker threads."""
        try:
            self.websocket_server.join()
            
        except KeyboardInterrupt:
            self.shutdown_handler(None, None)
    
    def log(self, msg):
        log_msg = f'{datetime.now()} [{self.__class__.__name__}] {msg}'
        print(log_msg)

if __name__ == "__main__":
    app = Main()
    app.start()
    app.join_threads()