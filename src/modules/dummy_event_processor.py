import asyncio
import threading
from datetime import datetime

class EventProcessor:
    def __init__(self, incoming_events_queue: asyncio.Queue, outgoing_events_queue: asyncio.Queue, shutdown_event):
        self.incoming_events_queue = incoming_events_queue
        self.outgoing_events_queue = outgoing_events_queue
        self.shutdown_event = shutdown_event

    async def process_events(self):
        """Processes events asynchronously."""
        self.log('[WORKER] Starting worker...')
        
        while not self.shutdown_event.is_set():
            try:
                event = await self.incoming_events_queue.get()
                self.log('[WORKER] Detected event in the queue.')

                if event is None:
                    self.log('[WORKER] Received exit signal. Gracefully exiting...')
                    break

                self.log(f"[WORKER] Processing event: {event}")
                await self.outgoing_events_queue.put(event)

            except Exception as e:
                self.log(f"[WORKER] Error processing event: {e}")
    
    def run(self):
        """Runs the eventProcessor in an event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        server_task = loop.create_task(self.process_events())

        while not self.shutdown_event.is_set():
            loop.run_until_complete(asyncio.sleep(0.1))  # Allow loop to check shutdown

        server_task.cancel()  # Cancel the server task before exiting
        loop.stop()
        loop.close()

    def start(self):
        """Starts the event processor as a coroutine."""
        self.log("Starting event processor...")
        self.server_thread = threading.Thread(target=self.run, daemon=True)
        self.server_thread.start()

    def stop(self):
        """Signals the worker to exit by setting the shutdown event."""
        self.log("Sending stop event to worker...")
        self.shutdown_event.set()  # Signal the worker to exit

    def log(self, msg):
        log_msg = f'{datetime.now()} [{self.__class__.__name__}] {msg}'
        print(log_msg)