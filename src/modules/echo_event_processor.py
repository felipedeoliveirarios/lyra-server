import asyncio
import threading
from datetime import datetime

class EchoEventProcessor:
    def __init__(self, incoming_event_queue: asyncio.Queue, outgoing_event_queue: asyncio.Queue, shutdown_event: asyncio.Event):
        self.incoming_event_queue = incoming_event_queue
        self.outgoing_event_queue = outgoing_event_queue
        self.shutdown_event = shutdown_event
        self.event_processor_thread = None 

    async def process_events(self):
        """Waits for and processes events asynchronously."""
        self.log(f"[WORKER] Starting worker loop...")
        while not self.shutdown_event.is_set():
            try:
                event = await self.incoming_event_queue.get()

                if event is None:
                    self.log("[WORKER] Received exit signal. Gracefully exiting...")
                    break
                else:
                    self.log(f"[WORKER] Detected message in the input queue: {event}")

                await self.outgoing_event_queue.put(event)
                self.log("[WORKER] Event echoed (added to the output queue).")
                
                self.incoming_event_queue.task_done()

            except Exception as e:
                self.log(f"[WORKER] Error processing event: {e}")

    def run(self):
        """Runs the event processor in an event loop"""
        
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        worker_task = loop.create_task(self.process_events())
        
        while not self.shutdown_event.is_set():
            loop.run_until_complete(asyncio.sleep(0.1))
        
        worker_task.cancel()
    
    def start(self):
        """Starts the event processor in a separate thread."""
        self.log("Starting event processor...")
        
        self.event_processor_thread = threading.Thread(target=self.run, daemon=True)
        self.event_processor_thread.start()
        
        self.log("Event processor started.")

    def stop(self):
        """Signals the processor to exit and waits for it to finish."""
        self.log("Sending stop event to worker...")
        self.incoming_event_queue.put_nowait(None)

        if self.event_processor_thread:
            self.event_processor_thread.join()

    def log(self, msg):
        log_msg = f'{datetime.now()} [{self.__class__.__name__}] {msg}'
        print(log_msg)
