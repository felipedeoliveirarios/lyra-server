import queue
import threading
from datetime import datetime

class EventProcessor:
    def __init__(self, event_queue, shutdown_event):
        self.event_queue = event_queue
        self.shutdown_event = shutdown_event
        self.worker_thread = threading.Thread(target=self._process_events, daemon=True)

    def _process_events(self):
        """Waits for and processes events as they arrive."""
        while True:
            try:
                event = self.event_queue.get()

                if event is None:
                    self.log('[WORKER] Received exit signal. Gracefully exiting...')
                    break

                self.log(f"[WORKER] Processing event: {event}")
                self.event_queue.task_done()

            except Exception as e:
                self.log(f"[WORKER] Error processing event: {e}")


    def start(self):
        """Starts the worker thread."""
        self.log("Starting event processor...")
        self.worker_thread.start()


    def stop(self):
        """Signals the worker to exit and waits for it to finish."""
        self.log("Sending stop event to worker thread...")
        self.event_queue.put(None)  # Send a sentinel value to exit cleanly
        self.worker_thread.join()

    
    def log(self, msg):
        log_msg = f'{datetime.now()} [{self.__class__.__name__}] {msg}'
        print(log_msg)