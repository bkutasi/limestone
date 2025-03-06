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

# Set up logging
logging.basicConfig(
    level=logging.INFO,  # Set default logging level to WARNING
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Get the logger for httpx and set its level to WARNING
httpx_logger = logging.getLogger("httpx")
httpx_logger.setLevel(logging.WARNING)
openai_logger = logging.getLogger("openai")
openai_logger.setLevel(logging.DEBUG)

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
        max_new_tokens=2048,
        streaming=STREAMING,
    )

    config_watcher = ConfigWatcher(chatbot)
    config_watcher.start()

    chatbot.run()
