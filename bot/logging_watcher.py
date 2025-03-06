import time
import logging
import logging.config
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml
from pathlib import Path

logger = logging.getLogger(__name__)

class LoggingConfigHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = time.time()
        self.config_path = Path("config/logging.yml")

    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith("logging.yml"):
            current = time.time()
            if current - self.last_modified < 1:  # Throttle to 1 second
                return
            self.last_modified = current

            try:
                self.reload_config()
                logger.info("Logging configuration reloaded successfully")
            except Exception as e:
                logger.error(f"Logging config reload failed: {str(e)}")

    def reload_config(self):
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
            logging.config.dictConfig(config)

class LoggingWatcher:
    def __init__(self):
        self.observer = Observer()
        # Ensure logs directory exists
        Path("logs").mkdir(parents=True, exist_ok=True)
        self.event_handler = LoggingConfigHandler()
        self.event_handler.reload_config()  # Load initial config

    def start(self):
        self.observer.schedule(self.event_handler, path="config/", recursive=False)
        self.observer.start()
        logger.info("Logging watcher started")

    def stop(self):
        self.observer.stop()
        self.observer.join()