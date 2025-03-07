from bot.bot import Bot
from bot.config import (
    BACKEND,
    TEMPLATE,
    URI,
    BOT_USERNAME,
    DEV_ID,
    TOKEN,
    USERS,
    STREAMING,
    MODEL,
    instruction_templates,
)
from bot.config_watcher import ConfigWatcher
import logging

from bot.logging_watcher import LoggingWatcher

# Initialize logging system
logging_watcher = LoggingWatcher()
logging_watcher.start()
logger = logging.getLogger(__name__)


# Run the program
if __name__ == "__main__":
    chatbot = Bot(
        token=TOKEN,
        backend=BACKEND,
        template=TEMPLATE,
        uri=URI,
        model=MODEL,
        bot_username=BOT_USERNAME,
        dev_id=DEV_ID,
        users=USERS,
        instruction_templates=instruction_templates,
        max_new_tokens=1024,
        streaming=STREAMING,
    )

    config_watcher = ConfigWatcher(chatbot)
    config_watcher.start()

    chatbot.run()
