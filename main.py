from bot.bot import Bot
from bot.config import (
    BACKEND,
    URI,
    BOT_USERNAME,
    DEV_ID,
    TOKEN,
    USERS,
    STREAMING,
    instruction_templates,
)


# Run the program
if __name__ == "__main__":
    chatbot = Bot(
        token=TOKEN,
        backend=BACKEND,
        uri=URI,
        bot_username=BOT_USERNAME,
        dev_id=DEV_ID,
        users=USERS,
        instruction_templates=instruction_templates,
        max_new_tokens=256,
        debug=True,
        database_debug=False,
        codeblock_debug=False,
        streaming=STREAMING,
    )

    chatbot.run()
