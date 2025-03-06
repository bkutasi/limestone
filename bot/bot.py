from functools import partial

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
)

import logging

logger = logging.getLogger(__name__)

from .message_handler import MyMessageHandler, StreamGenerator
from .command_handler import Commands
from .helpers.error_helper import ErrorHelper


class Bot:
    def __init__(
        self,
        token: str,
        backend: str,
        template: dict,
        uri: str,
        model: str,
        users: list,
        bot_username: str,
        dev_id: str,
        instruction_templates: dict,
        max_new_tokens: int,
        streaming: bool,
    ):
        self.token = token
        self.backend = backend
        self.template = template
        self.uri = uri
        self.users = users
        self.bot_username = bot_username
        self.dev_id = dev_id
        self.instruction_templates = instruction_templates
        self.max_new_tokens = max_new_tokens
        self.streaming = streaming
        self.model = model

    def run(self) -> None:
        logger.info("Starting up bot...")
        app = ApplicationBuilder().token(self.token).concurrent_updates(True).build()

        self.message_handling = MyMessageHandler(
            template=self.template,
            instruction_templates=self.instruction_templates,
            BOT_USERNAME=self.bot_username,
            DEV_ID=self.dev_id,
            backend=self.backend,
            streaming=self.streaming,
            URI=self.uri,
            MODEL=self.model,
        )

        # add handlers
        user_filter = filters.ALL
        if len(self.users) > 0:
            usernames = [x for x in self.users if isinstance(x, str)]
            user_ids = [x for x in self.users if isinstance(x, int)]
            user_filter = filters.User(username=usernames) | filters.User(
                user_id=user_ids
            )

        # Commands
        app.add_handler(CommandHandler("start", Commands.start_command))
        app.add_handler(CommandHandler("help", Commands.help_command))
        app.add_handler(CommandHandler("custom", Commands.custom_command))
        app.add_handler(
            CommandHandler(
                "wipe",
                partial(
                    Commands.wipe_history_command,
                    message_handling=self.message_handling,
                ),
            )
        )

        # Messages
        app.add_handler(
            MessageHandler(
                filters.TEXT
                & ~filters.COMMAND
                & user_filter
                & filters.UpdateType.MESSAGE,
                self.message_handling.handle_message,
            )
        )

        # Edited messages
        app.add_handler(
            MessageHandler(
                filters.TEXT
                & ~filters.COMMAND
                & user_filter
                & filters.UpdateType.EDITED_MESSAGE,
                self.message_handling.handle_edited_message,
            )
        )

        # Error handling
        app.add_error_handler(
            partial(ErrorHelper.error_handler, message_handler=self.message_handling)
        )

        # start the bot
        logger.info("Pooling...")
        app.run_polling()
