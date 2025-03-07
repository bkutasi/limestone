import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from bot.bot import Bot
from bot.config import reload_config
import logging

logger = logging.getLogger(__name__)


class ConfigFileHandler(FileSystemEventHandler):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.last_modified: float = time.time()

    def on_modified(self, event: FileSystemEvent) -> None:
        if not event.is_directory and event.src_path.endswith("config.yml"):
            current = time.time()
            if current - self.last_modified < 1:  # Throttle to 1 second
                return
            self.last_modified = current

            try:
                new_config: dict = reload_config()
                self.bot.message_handling.update_client_settings(
                    new_config["uri"], new_config["model"]
                )
                logger.info("Config reloaded successfully")
            except Exception as e:
                logger.error(f"Config reload failed: {str(e)}")


class ConfigWatcher:
    def __init__(self, bot: Bot) -> None:
        self.observer = Observer()
        self.event_handler: ConfigFileHandler = ConfigFileHandler(bot)

    def start(self) -> None:
        self.observer.schedule(self.event_handler, path="config/", recursive=False)
        self.observer.start()
        logger.info("Config watcher started")

    def stop(self) -> None:
        self.observer.stop()
        self.observer.join()
